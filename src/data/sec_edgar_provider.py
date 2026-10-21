import os
import requests
import pandas as pd
from functools import lru_cache
from typing import Dict, Iterable, List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 미국 SEC EDGAR 공식 API(키 불필요)로 공시 목록·내부자 거래 공시(Form 4)·XBRL 재무 수치를 조회합니다.
# - data.sec.gov(submissions, companyfacts)는 일반 User-Agent로도 응답한다.
# - www.sec.gov/Archives(공시 원문)는 "이름 + 연락처"가 들어간 User-Agent를 요구한다 → .env의 SEC_USER_AGENT.
# - SEC 공정 접근 정책: 초당 10건 이하.
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc}/{doc}"

# get_financials() 기본 항목. 회사마다 매출 태그가 달라 후보를 순서대로 찾는다.
DEFAULT_CONCEPTS: Dict[str, List[str]] = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
}


def _headers() -> Dict[str, str]:
    ua = os.getenv("SEC_USER_AGENT")
    if not ua or ua.startswith("your_"):
        # data.sec.gov는 이 값으로도 응답한다. 공시 원문(Archives)은 SEC_USER_AGENT가 있어야 한다.
        ua = "stock-invest-agent research-script"
    return {"User-Agent": ua}


def _get_json(url: str):
    try:
        resp = requests.get(url, headers=_headers(), timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("SEC EDGAR 조회 실패 (%s): %s", url, e)
        return None


@lru_cache(maxsize=1)
def _ticker_map() -> Dict[str, dict]:
    # company_tickers.json은 www.sec.gov에 있어 SEC_USER_AGENT(이름 + 연락처)가 없으면 403이 난다.
    data = _get_json(TICKERS_URL)
    if data is None:
        logger.error("SEC 티커 목록을 받지 못했습니다. .env에 SEC_USER_AGENT='이름 이메일'을 설정하거나 CIK 숫자를 직접 넘기세요.")
        return {}
    return {v["ticker"].upper(): v for v in data.values()}


def get_cik(ticker_or_cik: str) -> Optional[str]:
    """
    티커 또는 CIK → 10자리 CIK 문자열(예: 'MSFT' → '0000789019', '789019' → '0000789019').
    숫자를 넘기면 티커 목록 조회 없이 그대로 쓴다. 찾지 못하면 None.
    """
    s = str(ticker_or_cik).strip()
    if s.isdigit():
        return s.zfill(10)
    row = _ticker_map().get(s.upper())
    if not row:
        logger.warning("SEC 티커 목록에서 찾지 못했습니다: %s (ADR·ETF는 없을 수 있음)", s)
        return None
    return str(row["cik_str"]).zfill(10)


def get_recent_filings(ticker: str, forms: Optional[Iterable[str]] = None, limit: int = 20) -> pd.DataFrame:
    """
    최근 공시 목록(최신순).

    Args:
        forms: 걸러 낼 서식(예: ['10-Q', '10-K', '8-K', '4', 'SC 13G']). None이면 전체.
        limit: 반환 행 수.

    Returns:
        DataFrame[form, filing_date, report_date, accession, primary_doc, url]
        url은 공시 원문 주소다(열람은 SEC_USER_AGENT가 필요할 수 있다).
    """
    cik = get_cik(ticker)
    if not cik:
        return pd.DataFrame()
    data = _get_json(SUBMISSIONS_URL.format(cik=cik))
    if not data:
        return pd.DataFrame()
    rc = data["filings"]["recent"]
    df = pd.DataFrame({
        "form": rc["form"],
        "filing_date": rc["filingDate"],
        "report_date": rc["reportDate"],
        "accession": rc["accessionNumber"],
        "primary_doc": rc["primaryDocument"],
    })
    if forms is not None:
        df = df[df["form"].isin(list(forms))]
    df = df.head(limit).copy()
    df["url"] = [
        ARCHIVE_URL.format(cik_int=int(cik), acc=a.replace("-", ""), doc=d)
        for a, d in zip(df["accession"], df["primary_doc"])
    ]
    return df.reset_index(drop=True)


def get_insider_filings(ticker: str, since: Optional[str] = None, limit: int = 50) -> pd.DataFrame:
    """
    내부자 거래 공시(Form 4) 목록. since('YYYY-MM-DD') 이후 접수분만 남긴다.
    거래 세부(매수·매도, 주식 수, 가격)는 공시 원문 XML에 있다 — 원문 파싱은 SEC_USER_AGENT 설정 후 확장한다.

    Returns:
        DataFrame[form, filing_date, report_date, accession, primary_doc, url]
    """
    df = get_recent_filings(ticker, forms=["4", "4/A"], limit=limit)
    if since and not df.empty:
        df = df[df["filing_date"] >= since]
    return df.reset_index(drop=True)


def get_financials(
    ticker: str,
    concepts: Optional[Dict[str, List[str]]] = None,
    quarterly: bool = True,
    last_n: int = 8,
) -> pd.DataFrame:
    """
    XBRL companyfacts에서 재무 수치를 뽑아 기간별로 정리합니다.

    Args:
        concepts: {열 이름: [us-gaap 태그 후보...]}. 기본은 DEFAULT_CONCEPTS(매출·영업이익·순이익·희석 EPS·영업현금흐름).
        quarterly: True면 분기(약 90일 구간) 값, False면 연간(10-K, 약 365일 구간) 값.
        last_n: 최근 몇 기간을 남길지.

    Returns:
        DataFrame[period_end, fy, fp, form, filed, <concept 열들>] 기간 오름차순.
        ⚠️ 10-Q의 4분기 값은 따로 없다(10-K 연간 값만 있음). 분기 표에서 Q4가 빠지는 것은 정상이다.
    """
    concepts = concepts or DEFAULT_CONCEPTS
    cik = get_cik(ticker)
    if not cik:
        return pd.DataFrame()
    data = _get_json(FACTS_URL.format(cik=cik))
    if not data:
        return pd.DataFrame()
    gaap = data.get("facts", {}).get("us-gaap", {})

    series = {}
    meta_parts = []
    for col, tags in concepts.items():
        best = None
        for tag in tags:
            if tag not in gaap:
                continue
            units = gaap[tag]["units"]
            df = pd.DataFrame(units["USD"] if "USD" in units else next(iter(units.values())))
            if "start" not in df.columns:
                continue  # 기간이 없는 시점 값(재무상태표 항목)은 이 함수 대상이 아니다
            days = (pd.to_datetime(df["end"]) - pd.to_datetime(df["start"])).dt.days
            mask = days.between(80, 100) if quarterly else days.between(350, 380)
            df = df[mask & df["form"].isin(["10-Q", "10-K", "10-Q/A", "10-K/A"])]
            # 태그 후보가 여럿이면 가장 최근 기간까지 보고된 태그를 쓴다(회사가 태그를 바꾼 경우 대비).
            if not df.empty and (best is None or df["end"].max() > best["end"].max()):
                best = df
        if best is None:
            logger.warning("%s: XBRL 값을 찾지 못했습니다 (%s)", ticker, col)
            continue
        best = best.sort_values("filed")
        # 값은 가장 늦게 접수된 공시(정정 반영), 기간 표기(fy·fp)는 그 기간을 처음 보고한 공시 기준.
        # 이후 공시가 과거 기간을 비교치로 다시 싣기 때문에, 늦은 공시의 fy·fp는 그 기간과 맞지 않는다.
        series[col] = best.drop_duplicates("end", keep="last").set_index("end")["val"]
        meta_parts.append(best.drop_duplicates("end", keep="first").set_index("end")[["fy", "fp", "form", "filed"]])

    if not series:
        return pd.DataFrame()
    values = pd.DataFrame(series)
    meta = pd.concat(meta_parts).sort_values("filed")
    meta = meta[~meta.index.duplicated(keep="first")]
    out = meta.join(values, how="right").sort_index().tail(last_n)
    out.index.name = "period_end"
    return out.reset_index()


def yoy_growth(fin: pd.DataFrame, col: str) -> pd.Series:
    """
    get_financials() 결과에서 전년 같은 기간 대비 증감률(%)을 계산합니다.
    분기 표에는 Q4가 빠져 행 간격이 일정하지 않으므로, 행 순서가 아니라 period_end가 약 1년(355~375일) 전인 행과 비교한다.
    비교 대상이 표 안에 없으면 NaN이다 — 분기 YoY가 필요하면 last_n을 12 이상으로 넉넉히 받는다.
    """
    ends = pd.to_datetime(fin["period_end"])
    out = []
    for i, e in enumerate(ends):
        gap = (e - ends).dt.days
        prev = fin.loc[gap.between(355, 375), col]
        out.append((fin[col].iloc[i] / prev.iloc[0] - 1) * 100 if len(prev) else float("nan"))
    return pd.Series(out, index=fin.index)
