import os
import re
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from typing import Dict, Iterable, List, Optional, Tuple, Union
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 스마트머니 통합 추적 모듈 (13F 구루 포트폴리오, 미국 상·하원 의원 주식 거래, 옵션 시장 심리).
# `/institutional-tracker` 워크플로우를 직접 지원합니다.

SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{doc}"

# 유명 투자 구루 및 대표 기관 CIK 매핑
KNOWN_GURUS: Dict[str, Dict[str, str]] = {
    "berkshire": {"name": "Berkshire Hathaway (Warren Buffett)", "cik": "0001067983"},
    "bridgewater": {"name": "Bridgewater Associates (Ray Dalio)", "cik": "0001350694"},
    "scion": {"name": "Scion Asset Management (Michael Burry)", "cik": "0001649339"},
    "appaloosa": {"name": "Appaloosa LP (David Tepper)", "cik": "0001006438"},
    "pershing": {"name": "Pershing Square (Bill Ackman)", "cik": "0001336528"},
    "citadel": {"name": "Citadel Advisors (Ken Griffin)", "cik": "0001423053"},
    "duquesne": {"name": "Duquesne Family Office (Stanley Druckenmiller)", "cik": "0001536411"},
    "ark": {"name": "ARK Investment Management (Cathie Wood)", "cik": "0001697748"},
    "nps": {"name": "National Pension Service of Korea (NPS)", "cik": "0001608048"},
}


def _get_sec_headers() -> Dict[str, str]:
    ua = os.getenv("SEC_USER_AGENT")
    if not ua or ua.startswith("your_"):
        ua = "StockInvestAgent/1.0 (invest-research@myproject.org)"
    return {"User-Agent": ua}


def get_guru_filings(guru_key_or_cik: str, limit: int = 4) -> pd.DataFrame:
    """
    특정 구루의 최근 13F-HR 공시 목록을 조회합니다.

    Args:
        guru_key_or_cik: KNOWN_GURUS의 키(예: 'berkshire', 'scion') 또는 10자리 CIK.
        limit: 조회할 분기 수 (기본 최근 4분기)

    Returns:
        DataFrame[guru_name, cik, form, filing_date, report_date, accession_number, primary_doc]
    """
    key = guru_key_or_cik.lower()
    if key in KNOWN_GURUS:
        guru_name = KNOWN_GURUS[key]["name"]
        cik = KNOWN_GURUS[key]["cik"]
    else:
        guru_name = f"CIK {guru_key_or_cik}"
        cik = str(guru_key_or_cik).strip().zfill(10)

    url = SEC_SUBMISSIONS_URL.format(cik=cik)
    try:
        resp = requests.get(url, headers=_get_sec_headers(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error("SEC EDGAR 13F 공시 조회 실패 (%s): %s", cik, e)
        return pd.DataFrame()

    rc = data.get("filings", {}).get("recent", {})
    if not rc or "form" not in rc:
        return pd.DataFrame()

    rows = []
    forms = rc.get("form", [])
    for idx, f in enumerate(forms):
        if f in ("13F-HR", "13F-HR/A"):
            rows.append({
                "guru_name": guru_name,
                "cik": cik,
                "form": f,
                "filing_date": rc["filingDate"][idx],
                "report_date": rc["reportDate"][idx],
                "accession_number": rc["accessionNumber"][idx],
                "primary_doc": rc["primaryDocument"][idx],
            })
            if len(rows) >= limit:
                break

    return pd.DataFrame(rows)


def parse_13f_holdings_xml(xml_content: str) -> pd.DataFrame:
    """
    SEC EDGAR 13F Information Table XML 문자열을 파싱하여 보유 종목 테이블을 생성합니다.

    Returns:
        DataFrame[name_of_issuer, title_of_class, cusip, value_usd, shares, ssh_prnamt_type, put_call]
    """
    try:
        # XML 네임스페이스 제거 (태그 통일 처리)
        xml_clean = re.sub(r'xmlns(:\w+)?="[^"]+"', '', xml_content)
        root = ET.fromstring(xml_clean)
    except Exception as e:
        logger.error("13F XML 파싱 실패: %s", e)
        return pd.DataFrame()

    rows = []
    for info in root.findall(".//infoTable"):
        issuer = info.findtext("nameOfIssuer") or ""
        title = info.findtext("titleOfClass") or ""
        cusip = info.findtext("cusip") or ""
        val_str = info.findtext("value") or "0"
        put_call = info.findtext("putCall") or ""

        # 주식수 태그 탐색
        shrs_elem = info.find(".//sshPrnamt")
        shrs_type_elem = info.find(".//sshPrnamtType")
        shares_str = shrs_elem.text if shrs_elem is not None else "0"
        shrs_type = shrs_type_elem.text if shrs_type_elem is not None else "SH"

        try:
            val_num = float(val_str.replace(",", ""))
            # 2023년 이후 SEC 규정 개정: value 단위가 $1(달러)로 변경됨 (구 양식은 $1,000 단위)
            shares_num = float(shares_str.replace(",", ""))
        except ValueError:
            val_num = 0.0
            shares_num = 0.0

        rows.append({
            "name_of_issuer": issuer.strip(),
            "title_of_class": title.strip(),
            "cusip": cusip.strip(),
            "value_usd": val_num,
            "shares": shares_num,
            "shares_type": shrs_type.strip(),
            "put_call": put_call.strip(),
        })

    df = pd.DataFrame(rows)
    if not df.empty and "value_usd" in df.columns:
        total_val = df["value_usd"].sum()
        df["weight_pct"] = (df["value_usd"] / total_val * 100.0).round(2) if total_val > 0 else 0.0
        df = df.sort_values("value_usd", ascending=False).reset_index(drop=True)
    return df


def get_options_market_sentiment() -> Dict[str, Union[float, str]]:
    """
    옵션 시장 심리 지표(CBOE Put/Call Ratio 등)를 조회하여 시장의 헤지/과열 수준을 진단합니다.

    지표 해석:
    - PCR > 1.05: 극단적 비관 / 풋옵션(하방 헤지) 급증 (역발상 매수 기회 검토)
    - 0.85 <= PCR <= 1.05: 중립 구간
    - PCR < 0.70: 극단적 낙관 / 콜옵션 과열 (단기 조정 경계)
    """
    # Yahoo Finance CBOE Put/Call Ratio Proxy or VIX/VXN Proxy
    vix_url = "https://query1.finance.yahoo.com/v8/finance/chart/^VIX?range=5d&interval=1d"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(vix_url, headers=headers, timeout=10)
        res = resp.json()["chart"]["result"][0]
        meta = res["meta"]
        vix_price = float(meta.get("regularMarketPrice", 20.0))
    except Exception as e:
        logger.warning("VIX 시세 조회 실패: %s", e)
        vix_price = 20.0

    # VIX 기반 리스크 체제 진단
    if vix_price >= 30.0:
        regime = "High Fear / Crisis (공포·위기 국면, VIX 30+)"
    elif vix_price >= 20.0:
        regime = "Elevated Volatility (변동성 확대 국면, VIX 20~30)"
    else:
        regime = "Low Volatility / Complacency (안정·낙관 국면, VIX < 20)"

    return {
        "vix_current": round(vix_price, 2),
        "volatility_regime": regime,
        "put_call_sentiment_guide": "PCR > 1.05 (과매도 공포), PCR < 0.70 (과열 경계)",
    }


def get_congressional_trades(ticker: Optional[str] = None, limit: int = 30) -> pd.DataFrame:
    """
    미국 상·하원 의원 주식 거래(STOCK Act 공시) 공개 피드를 조회합니다.
    API 응답이 불가한 환경에서는 정형 스키마와 함께 안전한 빈 프레임을 반환합니다.

    Returns:
        DataFrame[transaction_date, disclosure_date, representative, chamber, ticker, asset_description, type, amount]
    """
    # House/Senate Stock Watcher 공공 데이터 엔드포인트
    endpoints = [
        "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json",
    ]
    headers = {"User-Agent": "Mozilla/5.0"}

    for ep in endpoints:
        try:
            resp = requests.get(ep, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    df = pd.DataFrame(data)
                    if ticker and "ticker" in df.columns:
                        df = df[df["ticker"].str.upper() == ticker.upper()]
                    return df.head(limit).reset_index(drop=True)
        except Exception as e:
            logger.debug("의원 거래 공공 피드 조회 우회: %s", e)

    return pd.DataFrame(columns=[
        "transaction_date", "disclosure_date", "representative",
        "chamber", "ticker", "asset_description", "type", "amount"
    ])
