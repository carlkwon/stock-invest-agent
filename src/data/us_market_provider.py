import time
import requests
import pandas as pd
from typing import Dict, Iterable, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Yahoo Finance 비공식 API로 미국 종목 일봉·밸류에이션·실적일을 조회합니다.
# 주간 가이드·섹터 리포트에서 매번 즉석으로 짜던 조회 코드를 한곳에 모았다.
# ⚠️ 비공식 API라 응답 형식이 바뀔 수 있다. 종가는 정규장 종가(close)이고, 시간외 가격은 쓰지 않는다.
CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
CRUMB_URL = "https://query1.finance.yahoo.com/v1/test/getcrumb"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# get_quotes()가 돌려주는 필드 (Yahoo quote 응답 키 → 반환 열 이름)
QUOTE_FIELDS = {
    "shortName": "name",
    "regularMarketPrice": "price",
    "marketCap": "market_cap",
    "trailingPE": "trailing_pe",
    "forwardPE": "forward_pe",
    "priceToBook": "pbr",
    "epsTrailingTwelveMonths": "eps_ttm",
    "epsForward": "eps_forward",
    "dividendYield": "dividend_yield_pct",
    "fiftyTwoWeekHigh": "high_52w",
    "fiftyTwoWeekLow": "low_52w",
    "averageAnalystRating": "analyst_rating",
    "earningsTimestamp": "earnings_ts",
}


def get_daily(ticker: str, range_: str = "1y", end: Optional[str] = None) -> pd.DataFrame:
    """
    일봉 OHLCV를 가져옵니다(정규장 기준). 지수(^GSPC)·환율(KRW=X)·선물(CL=F)도 같은 방식으로 조회된다.

    Args:
        ticker: 'MSFT', '^GSPC', 'KRW=X' 등
        range_: Yahoo range 값 ('1mo', '6mo', '1y', '2y', '5y', 'max')
        end: 'YYYY-MM-DD'. 지정하면 그 날짜 이후 행을 잘라 낸다(REVIEW 기준일 고정용).

    Returns:
        DataFrame[date(YYYY-MM-DD), open, high, low, close, volume] 날짜 오름차순.
        종가가 비어 있는 행(장중·미확정)은 뺀다. 실패 시 빈 DataFrame.
    """
    try:
        resp = requests.get(CHART_URL.format(ticker=ticker), params={"range": range_, "interval": "1d"},
                            headers=HEADERS, timeout=15)
        resp.raise_for_status()
        result = resp.json()["chart"]["result"][0]
    except Exception as e:
        logger.error("Yahoo 일봉 조회 실패 (%s): %s", ticker, e)
        return pd.DataFrame()

    quote = result["indicators"]["quote"][0]
    df = pd.DataFrame({
        # Yahoo timestamp는 장 시작 시각(UTC)이라 미국 거래일과 날짜가 같다.
        "date": pd.to_datetime(result["timestamp"], unit="s").strftime("%Y-%m-%d"),
        "open": quote["open"],
        "high": quote["high"],
        "low": quote["low"],
        "close": quote["close"],
        "volume": quote["volume"],
    }).dropna(subset=["close"])
    if end:
        df = df[df["date"] <= end]
    return df.reset_index(drop=True)


def get_close_on(ticker: str, date: str, range_: str = "3mo") -> Optional[float]:
    """해당 날짜(또는 그 이전 마지막 거래일)의 정규장 종가. 없으면 None."""
    df = get_daily(ticker, range_=range_, end=date)
    return float(df["close"].iloc[-1]) if not df.empty else None


def get_returns(tickers: Iterable[str], start: str, end: str, range_: str = "6mo") -> pd.DataFrame:
    """
    여러 종목의 구간 수익률(start 직전 종가 → end 종가)을 계산합니다.
    start·end가 휴장일이면 각각 그 이전 마지막 거래일 종가를 쓴다.

    Returns:
        DataFrame[ticker, start_date, start_close, end_date, end_close, return_pct]
    """
    rows: List[dict] = []
    for t in tickers:
        df = get_daily(t, range_=range_, end=end)
        base = df[df["date"] <= start]
        if df.empty or base.empty:
            logger.warning("구간 수익률 계산 불가 (%s): 데이터 부족", t)
            continue
        s, e = base.iloc[-1], df.iloc[-1]
        rows.append({
            "ticker": t,
            "start_date": s["date"], "start_close": float(s["close"]),
            "end_date": e["date"], "end_close": float(e["close"]),
            "return_pct": (float(e["close"]) / float(s["close"]) - 1) * 100,
        })
        time.sleep(0.1)
    return pd.DataFrame(rows)


def _session_with_crumb():
    """quote API는 쿠키+crumb가 필요하다. 세션을 만들어 crumb와 함께 돌려준다."""
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get("https://fc.yahoo.com", timeout=10)  # 쿠키 발급용(응답 코드는 404여도 무관)
    crumb = s.get(CRUMB_URL, timeout=10).text
    return s, crumb


def get_quotes(tickers: Iterable[str], batch_size: int = 50) -> pd.DataFrame:
    """
    여러 종목의 현재가·시가총액·PER(Trailing/Forward)·PBR·배당수익률·52주 고저·애널리스트 평균 의견·다음(직전) 실적일을 한 번에 조회합니다.

    Returns:
        DataFrame[symbol, name, price, market_cap, trailing_pe, forward_pe, pbr, eps_ttm, eps_forward,
                  dividend_yield_pct, high_52w, low_52w, analyst_rating, earnings_ts, earnings_date]
        earnings_date는 earnings_ts를 UTC 날짜(YYYY-MM-DD)로 바꾼 값이다. 이미 지난 실적이면 직전 실적일이 나온다.
        정확한 발표일·장전/장후는 earnings_calendar_provider로 교차 확인한다.
    """
    tickers = list(tickers)
    try:
        session, crumb = _session_with_crumb()
    except Exception as e:
        logger.error("Yahoo crumb 발급 실패: %s", e)
        return pd.DataFrame()

    rows: List[dict] = []
    for i in range(0, len(tickers), batch_size):
        chunk = tickers[i:i + batch_size]
        try:
            resp = session.get(QUOTE_URL, params={"symbols": ",".join(chunk), "crumb": crumb}, timeout=20)
            resp.raise_for_status()
            result = resp.json()["quoteResponse"]["result"]
        except Exception as e:
            logger.error("Yahoo quote 조회 실패 (%s...): %s", chunk[0], e)
            continue
        for x in result:
            row: Dict = {"symbol": x.get("symbol")}
            row.update({col: x.get(key) for key, col in QUOTE_FIELDS.items()})
            rows.append(row)
    df = pd.DataFrame(rows)
    if not df.empty:
        df["earnings_date"] = pd.to_datetime(df["earnings_ts"], unit="s", errors="coerce").dt.strftime("%Y-%m-%d")
    return df
