import re
import requests
import pandas as pd
from typing import Dict, Iterable, List, Optional, Tuple
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 네이버 증권 비공식 API로 투자자별 순매수(외국인·기관·개인)와 일봉을 조회합니다.
# KRX Open API 승인 목록에 투자자별 매매 데이터가 없어 수급 리포트·주간 가이드에서 보완용으로 쓴다.
# ⚠️ 네이버 시세(closePrice)는 NXT(대체거래소) 체결이 섞인 통합가라 KRX 확정 종가와 다를 수 있다
#    (예: 2026-09-23 현대건설 네이버 122,300원 vs KRX 121,100원). 금액 환산에는 KRX 종가를 우선 쓴다.
MOBILE_BASE = "https://m.stock.naver.com/api"
FCHART_URL = "https://fchart.stock.naver.com/sise.nhn"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def _to_int(value) -> int:
    """'+1,234' / '-5,678' / '' 형태의 네이버 문자열 숫자를 int로 변환."""
    if value in (None, "", "-"):
        return 0
    return int(str(value).replace(",", "").replace("+", ""))


def _get_json(url: str, params: Optional[dict] = None):
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("네이버 API 호출 실패 (%s): %s", url, e)
        return None


def get_stock_investor_trend(code: str, page_size: int = 20) -> pd.DataFrame:
    """
    종목별 일별 투자자 순매수 '수량'을 가져옵니다 (최신 거래일부터 page_size개).

    Args:
        code: 6자리 종목코드 (예: '005930')
        page_size: 조회 거래일 수 (네이버 기본 최대 약 20~30)

    Returns:
        DataFrame[date(YYYYMMDD), close_naver, foreign_qty, inst_qty, indiv_qty, foreign_hold_ratio]
        날짜 오름차순. 장중 조회 시 당일 행은 잠정치다. 실패 시 빈 DataFrame.
    """
    data = _get_json(f"{MOBILE_BASE}/stock/{code}/trend", params={"pageSize": page_size})
    if not data:
        return pd.DataFrame()
    rows = [
        {
            "date": x["bizdate"],
            "close_naver": _to_int(x.get("closePrice")),
            "foreign_qty": _to_int(x.get("foreignerPureBuyQuant")),
            "inst_qty": _to_int(x.get("organPureBuyQuant")),
            "indiv_qty": _to_int(x.get("individualPureBuyQuant")),
            "foreign_hold_ratio": float(str(x.get("foreignerHoldRatio", "0")).rstrip("%") or 0),
        }
        for x in data
    ]
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def get_market_investor_trend(market: str, bizdate: str) -> Optional[Dict[str, int]]:
    """
    시장 전체(KOSPI/KOSDAQ)의 특정일 투자자별 순매수 '금액'(억원)을 가져옵니다.
    연기금·기타법인은 제공되지 않습니다(외국인·기관계·개인 3개 주체만).

    Args:
        market: 'KOSPI' 또는 'KOSDAQ'
        bizdate: 'YYYYMMDD'

    Returns:
        {'date', 'foreign', 'institution', 'individual'} (억원). 실패 시 None.
    """
    data = _get_json(f"{MOBILE_BASE}/index/{market}/trend", params={"bizdate": bizdate})
    if not data or "foreignValue" not in data:
        return None
    return {
        "date": data.get("bizdate", bizdate),
        "foreign": _to_int(data.get("foreignValue")),
        "institution": _to_int(data.get("institutionalValue")),
        "individual": _to_int(data.get("personalValue")),
    }


def get_market_investor_trend_range(market: str, dates: Iterable[str]) -> pd.DataFrame:
    """여러 거래일의 시장 전체 투자자별 순매수(억원)를 모아 DataFrame으로 반환합니다."""
    rows = [r for d in dates if (r := get_market_investor_trend(market, d))]
    return pd.DataFrame(rows)


def get_krx_closes(codes: Iterable[str], dates: Iterable[str]) -> Dict[Tuple[str, str], int]:
    """
    KRX Open API에서 여러 종목·여러 날짜의 확정 종가를 한 번에 모읍니다.
    날짜당 코스피·코스닥 전 종목을 1회씩 조회하므로 종목 수와 무관하게 호출 수는 (날짜 수 × 2)다.

    Returns:
        {(code, date): close}. 휴장일·미게시일은 빠진다.
    """
    from .krx_openapi_provider import get_kospi_daily_trade, get_kosdaq_daily_trade

    codes = set(codes)
    closes: Dict[Tuple[str, str], int] = {}
    for d in dates:
        for fetch in (get_kospi_daily_trade, get_kosdaq_daily_trade):
            df = fetch(d)
            if df.empty:
                continue
            for _, r in df[df["ISU_CD"].isin(codes)].iterrows():
                closes[(r["ISU_CD"], d)] = _to_int(r["TDD_CLSPRC"])
    return closes


def estimate_net_buy_amount(
    code: str,
    dates: Iterable[str],
    krx_closes: Optional[Dict[Tuple[str, str], int]] = None,
    page_size: int = 30,
) -> pd.DataFrame:
    """
    종목의 일별 순매수 수량 × 해당일 KRX 확정 종가로 투자자별 순매수 '금액'(억원)을 추정합니다.
    (수급 리포트·주간 가이드에서 쓰던 산출식: Σ(순매수 수량 × KRX 종가) / 1e8)

    Args:
        code: 6자리 종목코드
        dates: 집계할 거래일 목록 ('YYYYMMDD')
        krx_closes: get_krx_closes() 결과. 여러 종목을 집계할 때 미리 만들어 넘기면 KRX 재조회를 피한다.
                    None이면 이 종목만 KRX에서 조회한다.
        page_size: 네이버 trend 조회 거래일 수 (dates가 이 범위 안에 있어야 함)

    Returns:
        DataFrame[date, close, price_source, foreign_amt, inst_amt, indiv_amt] (금액 단위 억원).
        KRX 종가가 없는 날은 네이버 종가로 대체하고 price_source='naver'로 표시한다.
    """
    dates = list(dates)
    trend = get_stock_investor_trend(code, page_size=page_size)
    if trend.empty:
        return pd.DataFrame()
    if krx_closes is None:
        krx_closes = get_krx_closes([code], dates)

    rows: List[dict] = []
    for _, r in trend[trend["date"].isin(dates)].iterrows():
        krx = krx_closes.get((code, r["date"]))
        price, source = (krx, "krx") if krx else (r["close_naver"], "naver")
        rows.append({
            "date": r["date"],
            "close": price,
            "price_source": source,
            "foreign_amt": r["foreign_qty"] * price / 1e8,
            "inst_amt": r["inst_qty"] * price / 1e8,
            "indiv_amt": r["indiv_qty"] * price / 1e8,
        })
    missing = set(dates) - {row["date"] for row in rows}
    if missing:
        logger.warning("네이버 trend에 없는 거래일 (%s): %s — page_size를 늘리거나 휴장일 여부 확인", code, sorted(missing))
    return pd.DataFrame(rows)


def get_daily_ohlcv(code: str, count: int = 260) -> pd.DataFrame:
    """
    네이버 차트(fchart)에서 일봉 OHLCV를 가져옵니다. 이동평균·볼린저밴드 계산용.

    Returns:
        DataFrame[date, open, high, low, close, volume] 날짜 오름차순. 실패 시 빈 DataFrame.
        장중 조회 시 마지막 행은 당일 진행 중 시세다.
    """
    try:
        resp = requests.get(
            FCHART_URL,
            headers=HEADERS,
            params={"symbol": code, "timeframe": "day", "count": count, "requestType": 0},
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as e:
        logger.error("네이버 fchart 조회 실패 (%s): %s", code, e)
        return pd.DataFrame()
    rows = [line.split("|") for line in re.findall(r'data="([^"]+)"', resp.text)]
    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col])
    return df
