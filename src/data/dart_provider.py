import io
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
import requests
import pandas as pd
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 금융감독원 OpenDART API로 국내 상장사 공시 목록과 재무제표(단일회사 전체 재무제표)를 조회합니다.
# 인증키: https://opendart.fss.or.kr → 인증키 신청 → .env의 DART_API_KEY. 하루 약 2만 건 한도.
# KRX Open API·네이버로는 얻을 수 없는 확정 실적(분기·반기·사업보고서)과 공시 원문 링크를 보완한다.
BASE_URL = "https://opendart.fss.or.kr/api"
CORP_CODE_CACHE = Path(__file__).resolve().parents[2] / ".cache" / "dart_corp_codes.csv"

# 보고서 코드: 1분기·반기·3분기·사업보고서
REPORT_CODES = {"1Q": "11013", "H1": "11012", "3Q": "11014", "FY": "11011"}

# 공시 유형(pblntf_ty): 정기공시 A, 주요사항보고 B, 발행공시 C, 지분공시 D, 기타공시 E, 외부감사관련 F, 펀드공시 G,
# 자산유동화 H, 거래소공시 I, 공정위공시 J
STATUS_MESSAGES = {
    "010": "등록되지 않은 인증키",
    "011": "사용할 수 없는 인증키",
    "013": "조회된 데이터 없음",
    "020": "요청 제한 초과",
    "100": "필드 값 오류",
    "800": "시스템 점검 중",
}

# summarize_financials() 기본 계정. 회사마다 계정명이 조금씩 달라 후보를 순서대로 찾는다.
KEY_ACCOUNTS = {
    "매출액": ["매출액", "수익(매출액)", "영업수익", "매출"],
    "영업이익": ["영업이익", "영업이익(손실)"],
    "당기순이익": ["당기순이익", "당기순이익(손실)", "분기순이익", "반기순이익"],
    "지배주주순이익": ["지배기업의 소유주에게 귀속되는 당기순이익", "지배기업 소유주지분"],
}


def _get_key() -> Optional[str]:
    key = os.getenv("DART_API_KEY")
    if not key or key.startswith("your_"):
        logger.error("DART_API_KEY가 설정되지 않았습니다. https://opendart.fss.or.kr 에서 인증키를 발급받아 .env에 넣으세요.")
        return None
    return key


def _call(endpoint: str, params: dict) -> Optional[dict]:
    key = _get_key()
    if not key:
        return None
    try:
        resp = requests.get(f"{BASE_URL}/{endpoint}", params={"crtfc_key": key, **params}, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error("OpenDART 호출 실패 (%s): %s", endpoint, e)
        return None
    status = data.get("status")
    if status != "000":
        msg = STATUS_MESSAGES.get(status, data.get("message"))
        # 013(데이터 없음)은 정상적인 빈 결과라 경고로만 남긴다.
        (logger.warning if status == "013" else logger.error)("OpenDART %s 응답 %s: %s", endpoint, status, msg)
        return None
    return data


def get_corp_codes(refresh: bool = False) -> pd.DataFrame:
    """
    DART 고유번호(corp_code) 목록. 처음 한 번 zip을 받아 `.cache/dart_corp_codes.csv`에 저장하고 이후 재사용한다.

    Returns:
        DataFrame[corp_code, corp_name, stock_code, modify_date] — 상장사만(stock_code 있는 행).
    """
    if CORP_CODE_CACHE.exists() and not refresh:
        return pd.read_csv(CORP_CODE_CACHE, dtype=str)
    key = _get_key()
    if not key:
        return pd.DataFrame()
    try:
        resp = requests.get(f"{BASE_URL}/corpCode.xml", params={"crtfc_key": key}, timeout=60)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            root = ET.fromstring(zf.read(zf.namelist()[0]))
    except Exception as e:
        logger.error("OpenDART 고유번호 파일 수신 실패 (키 오류면 zip 대신 오류 XML이 온다): %s", e)
        return pd.DataFrame()
    rows = [{c.tag: (c.text or "").strip() for c in item} for item in root.findall("list")]
    df = pd.DataFrame(rows)
    df = df[df["stock_code"] != ""].reset_index(drop=True)
    CORP_CODE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CORP_CODE_CACHE, index=False)
    return df


def get_corp_code(stock_code: str) -> Optional[str]:
    """6자리 종목코드 → 8자리 DART 고유번호. 없으면 None."""
    df = get_corp_codes()
    if df.empty:
        return None
    hit = df[df["stock_code"] == stock_code]
    if hit.empty:
        logger.warning("DART 고유번호를 찾지 못했습니다: %s", stock_code)
        return None
    return hit.iloc[0]["corp_code"]


def get_disclosures(
    stock_code: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    kind: Optional[str] = None,
    page_count: int = 100,
) -> pd.DataFrame:
    """
    공시 목록(최신순). stock_code를 생략하면 기간 내 전체 공시(최대 3개월)를 조회한다.

    Args:
        start/end: 'YYYYMMDD'. 생략하면 DART 기본값(오늘).
        kind: 공시 유형 코드(A 정기공시, B 주요사항보고, D 지분공시, I 거래소공시 등).

    Returns:
        DataFrame[rcept_dt, corp_name, stock_code, report_nm, rcept_no, flr_nm, url]
    """
    params = {"page_count": page_count}
    if stock_code:
        corp = get_corp_code(stock_code)
        if not corp:
            return pd.DataFrame()
        params["corp_code"] = corp
    if start:
        params["bgn_de"] = start
    if end:
        params["end_de"] = end
    if kind:
        params["pblntf_ty"] = kind
    data = _call("list.json", params)
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data.get("list", []))
    if df.empty:
        return df
    df["url"] = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=" + df["rcept_no"]
    cols = ["rcept_dt", "corp_name", "stock_code", "report_nm", "rcept_no", "flr_nm", "url"]
    return df[[c for c in cols if c in df.columns]]


def get_financial_statements(stock_code: str, year: int, report: str = "FY", consolidated: bool = True) -> pd.DataFrame:
    """
    단일회사 전체 재무제표(fnlttSinglAcntAll).

    Args:
        year: 사업연도(예: 2026)
        report: '1Q' / 'H1' / '3Q' / 'FY'
        consolidated: True면 연결(CFS), False면 별도(OFS)

    Returns:
        DataFrame[sj_div, sj_nm, account_nm, thstrm_nm, thstrm_amount, thstrm_add_amount, frmtrm_amount, ...]
        금액 열은 원 단위 숫자로 바꿔 둔다. sj_div: BS 재무상태표, IS 손익계산서, CIS 포괄손익, CF 현금흐름, SCE 자본변동.
        ⚠️ 분기·반기 보고서의 손익 항목은 thstrm_amount가 해당 분기(3개월), thstrm_add_amount가 누적 값이다.
    """
    corp = get_corp_code(stock_code)
    if not corp:
        return pd.DataFrame()
    data = _call("fnlttSinglAcntAll.json", {
        "corp_code": corp,
        "bsns_year": str(year),
        "reprt_code": REPORT_CODES[report],
        "fs_div": "CFS" if consolidated else "OFS",
    })
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data.get("list", []))
    for col in [c for c in df.columns if c.endswith("_amount")]:
        df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors="coerce")
    return df


def summarize_financials(fs: pd.DataFrame) -> pd.DataFrame:
    """
    get_financial_statements() 결과에서 매출액·영업이익·당기순이익·지배주주순이익만 뽑아 당기·전기 비교표로 만듭니다.

    Returns:
        DataFrame[항목, 계정명, 당기, 전기, 증감률(%)] (원 단위). 전기는 분기 보고서면 전년 같은 분기, 사업보고서면 전년이다.
        찾지 못한 항목은 빠진다.
    """
    if fs.empty:
        return pd.DataFrame()
    pl = fs[fs["sj_div"].isin(["IS", "CIS"])]
    rows = []
    for label, names in KEY_ACCOUNTS.items():
        hit = pl[pl["account_nm"].str.replace(" ", "").isin([n.replace(" ", "") for n in names])]
        if hit.empty:
            continue
        r = hit.iloc[0]
        cur = r.get("thstrm_amount")
        # 분기·반기 보고서는 전년 같은 분기 값이 frmtrm_q_amount에 있다. 없으면(사업보고서) frmtrm_amount를 쓴다.
        prev = r.get("frmtrm_q_amount") if pd.notna(r.get("frmtrm_q_amount", None)) else r.get("frmtrm_amount")
        rows.append({
            "항목": label,
            "계정명": r["account_nm"],
            "당기": cur,
            "전기": prev,
            "증감률(%)": (cur / prev - 1) * 100 if prev else None,
        })
    return pd.DataFrame(rows)
