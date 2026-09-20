import os
import requests
import pandas as pd
from typing import Optional, Dict
import logging
from dotenv import load_dotenv
from datetime import date, timedelta

# 환경 변수 로드
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://api.stlouisfed.org/fred"

# 매크로 리포트에서 자주 쓰는 FRED 시리즈 (series_id → 설명). get_series()에 series_id를 그대로 넘기면 된다.
SERIES = {
    # 유동성
    "m2": {"id": "M2SL", "desc": "M2 통화량 (월간, 계절조정, 십억달러)"},
    "fed_assets": {"id": "WALCL", "desc": "연준 총자산 (주간 수요일, 백만달러)"},
    "rrp": {"id": "RRPONTSYD", "desc": "역레포(RRP) 일별 잔액 (십억달러)"},
    "tga": {"id": "WTREGEN", "desc": "재무부 일반계정(TGA) 주간 평균 (십억달러)"},
    # 금리
    "fed_funds_upper": {"id": "DFEDTARU", "desc": "연방기금금리 목표 상단 (일간)"},
    "us2y": {"id": "DGS2", "desc": "국채 2년물 (일간, %)"},
    "us10y": {"id": "DGS10", "desc": "국채 10년물 (일간, %)"},
    "us30y": {"id": "DGS30", "desc": "국채 30년물 (일간, %)"},
    "t10y2y": {"id": "T10Y2Y", "desc": "10년-2년 스프레드 (일간, %p)"},
    # 물가
    "cpi": {"id": "CPIAUCSL", "desc": "CPI 전체 (월간, 지수)"},
    "core_cpi": {"id": "CPILFESL", "desc": "근원 CPI (월간, 지수)"},
    "pce": {"id": "PCEPI", "desc": "PCE 물가지수 (월간)"},
    "core_pce": {"id": "PCEPILFE", "desc": "근원 PCE 물가지수 (월간)"},
    "ppi": {"id": "PPIACO", "desc": "PPI 전 품목 (월간)"},
    # 고용·성장
    "payrolls": {"id": "PAYEMS", "desc": "비농업고용 (월간, 천명)"},
    "unemployment": {"id": "UNRATE", "desc": "실업률 (월간, %)"},
    "claims": {"id": "ICSA", "desc": "주간 신규 실업수당 청구 (건)"},
    "gdp_real": {"id": "GDPC1", "desc": "실질 GDP (분기, 십억달러)"},
    "umich": {"id": "UMCSENT", "desc": "미시간대 소비자심리 (월간)"},
    # 시장·환율·원자재
    "vix": {"id": "VIXCLS", "desc": "VIX (일간)"},
    "dxy_broad": {"id": "DTWEXBGS", "desc": "달러 명목 광의 지수 (일간; ICE DXY와 다름)"},
    # ⚠️ DEXKOUS: FRED 원/달러는 갱신이 1~2주 지연되는 경우가 잦음 → 정확한 최신 환율은 ECOS usd_krw 병용 권장
    "usd_krw": {"id": "DEXKOUS", "desc": "원/달러 환율 (일간, FRED — 갱신 지연 주의)"},
    "wti": {"id": "DCOILWTICO", "desc": "WTI 현물 (일간, 달러)"},
    "sp500": {"id": "SP500", "desc": "S&P 500 (일간)"},
    # 해외 유동성 (한국 M2는 FRED 시리즈가 2017년에서 갱신 중단 → ECOS 사용)
    "ecb_assets": {"id": "ECBASSETSW", "desc": "ECB 총자산 (주간, 백만유로)"},
}


def _get_key() -> Optional[str]:
    key = os.getenv("FRED_API_KEY")
    if not key or key.startswith("your_"):
        logger.error("FRED_API_KEY가 설정되지 않았습니다. (.env 파일 확인 필요)")
        return None
    return key


def get_series(
    series_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    units: str = "lin",
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """
    FRED series/observations 조회.

    Args:
        series_id: FRED 시리즈 ID (예: 'M2SL'). SERIES 딕셔너리 참고.
        start/end: 'YYYY-MM-DD'. 생략 시 전체 구간.
        units: 'lin'(원값), 'chg'(전기比 변화), 'pch'(전기比 %), 'pc1'(전년比 %) 등 FRED 변환 옵션.
        limit: 최신 N개만 원하면 지정 (내부적으로 내림차순 조회 후 오름차순으로 정렬해 반환).

    Returns:
        DataFrame[date, value]. 결측('.')은 제외. 실패 시 빈 DataFrame.
    """
    key = _get_key()
    if not key:
        return pd.DataFrame()

    params = {
        "series_id": series_id,
        "api_key": key,
        "file_type": "json",
        "units": units,
    }
    if start:
        params["observation_start"] = start
    if end:
        params["observation_end"] = end
    if limit:
        params["sort_order"] = "desc"
        params["limit"] = limit

    try:
        resp = requests.get(f"{BASE_URL}/series/observations", params=params, timeout=15)
        if resp.status_code == 429:
            logger.warning("FRED API rate limit 초과 (429). 잠시 후 재시도하세요.")
            return pd.DataFrame()
        if resp.status_code == 400:
            msg = resp.json().get("error_message", "Bad Request")
            logger.error("FRED 잘못된 요청 (400, %s): %s", series_id, msg)
            return pd.DataFrame()
        resp.raise_for_status()
        obs = resp.json().get("observations", [])
    except requests.exceptions.Timeout:
        logger.error("FRED 타임아웃 (%s): 15초 초과", series_id)
        return pd.DataFrame()
    except Exception as e:
        # 예외 메시지에 요청 URL(=API 키)이 포함될 수 있으므로 키를 마스킹해 로깅
        logger.error("FRED 조회 실패 (%s): %s", series_id, str(e).replace(key, "***"))
        return pd.DataFrame()

    df = pd.DataFrame(obs)
    if df.empty:
        return df
    df = df[df["value"] != "."][["date", "value"]].copy()
    df["value"] = pd.to_numeric(df["value"])
    return df.sort_values("date").reset_index(drop=True)


def get_latest(series_id: str, n: int = 2, units: str = "lin") -> pd.DataFrame:
    """최신 n개 관측치(직전 값과의 WoW/MoM 비교용)를 오름차순으로 반환."""
    return get_series(series_id, units=units, limit=n)


def get_yoy(series_id: str, n_months: int = 14) -> pd.DataFrame:
    """
    월간 시리즈의 전년비(YoY, %) 변화율을 반환합니다.
    FRED units='pc1' 파라미터를 사용하므로 서버에서 계산 — 별도 pandas 계산 불필요.

    주요 사용처: CPI(CPIAUCSL), 근원CPI(CPILFESL), PCE(PCEPI), 근원PCE(PCEPILFE), PPI(PPIACO)

    Args:
        series_id: FRED 시리즈 ID.
        n_months: 최신 N개월치 YoY를 반환 (기본 14개월 = 1년 + 2개월 여유).

    Returns:
        DataFrame[date, value] — value는 전년비 % 변화율.
    """
    return get_series(series_id, units="pc1", limit=n_months)


def get_macro_snapshot(
    lookback_days: int = 14,
    as_of: Optional[str] = None,
) -> Dict[str, pd.DataFrame]:
    """
    매크로 리포트용 주요 지표 스냅샷을 한 번에 수집합니다.
    각 지표별로 최근 ``lookback_days`` 일치 시계열을 반환합니다(일간/주간/월간 혼재).

    Args:
        lookback_days: 조회 시작일을 오늘 기준 N일 전으로 설정 (기본 14일 — 주간 WoW에 충분).
        as_of: 조회 종료일('YYYY-MM-DD'). None이면 오늘.

    Returns:
        {key: DataFrame[date, value]} 딕셔너리.
        key 목록 (SERIES 딕셔너리의 short-name과 동일):
            금리: 'fed_funds_upper', 'us2y', 'us10y', 'us30y', 't10y2y'
            물가: 'cpi_yoy', 'core_cpi_yoy', 'pce_yoy', 'core_pce_yoy'
            고용: 'unemployment', 'claims'
            유동성: 'm2', 'rrp', 'tga', 'fed_assets'
            시장: 'vix', 'sp500', 'wti', 'usd_krw', 'dxy_broad'

    Example::

        snap = get_macro_snapshot(lookback_days=10)
        us10y = snap['us10y']          # DataFrame[date, value]
        print(us10y.tail(3))
    """
    end = as_of or date.today().strftime("%Y-%m-%d")
    start = (date.today() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    # 월간 시리즈는 조금 더 넉넉히
    start_monthly = (date.today() - timedelta(days=max(lookback_days, 60))).strftime("%Y-%m-%d")

    # 일간·주간 시리즈
    daily_series = {
        "fed_funds_upper": "DFEDTARU",
        "us2y":            "DGS2",
        "us10y":           "DGS10",
        "us30y":           "DGS30",
        "t10y2y":          "T10Y2Y",
        "vix":             "VIXCLS",
        "sp500":           "SP500",
        "wti":             "DCOILWTICO",
        "usd_krw":         "DEXKOUS",   # 갱신 지연 주의
        "dxy_broad":       "DTWEXBGS",
        "rrp":             "RRPONTSYD",
        "claims":          "ICSA",      # 주간
        "fed_assets":      "WALCL",     # 주간
        "tga":             "WTREGEN",   # 주간
    }
    # 월간 시리즈 (units='pc1' → 전년비 %)
    monthly_yoy = {
        "cpi_yoy":      "CPIAUCSL",
        "core_cpi_yoy": "CPILFESL",
        "pce_yoy":      "PCEPI",
        "core_pce_yoy": "PCEPILFE",
    }
    # 월간 시리즈 (원값)
    monthly_lin = {
        "unemployment": "UNRATE",
        "m2":           "M2SL",
    }

    result: Dict[str, pd.DataFrame] = {}

    for key, sid in daily_series.items():
        result[key] = get_series(sid, start=start, end=end)

    for key, sid in monthly_yoy.items():
        result[key] = get_series(sid, start=start_monthly, end=end, units="pc1")

    for key, sid in monthly_lin.items():
        result[key] = get_series(sid, start=start_monthly, end=end)

    return result
