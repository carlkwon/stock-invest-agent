import time
import requests
import pandas as pd
from datetime import date, timedelta
from typing import Iterable, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Nasdaq.com 실적 발표 캘린더(비공식 공개 API, 키 불필요)로 미국 기업 실적일과 장전/장후 여부를 조회합니다.
# Yahoo earningsTimestamp는 추정치가 섞이고 출처마다 날짜가 갈리는 경우가 있어(예: 2026-10 Tesla 10/21 vs 10/22),
# 주간 가이드 캘린더의 실적일을 이 소스로 교차 확인한다.
URL = "https://api.nasdaq.com/api/calendar/earnings"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

# Nasdaq 응답의 발표 시각 코드 → 리포트 표기
TIME_LABELS = {
    "time-pre-market": "장전",
    "time-after-hours": "장후",
    "time-not-supplied": "미정",
}


def _to_float(value) -> Optional[float]:
    """'$1.23' / '($0.45)' / 'N/A' 형태 문자열을 float로 변환. 변환 불가면 None."""
    if value in (None, "", "N/A"):
        return None
    s = str(value).replace("$", "").replace(",", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def get_earnings_on(day: str) -> pd.DataFrame:
    """
    특정 날짜(YYYY-MM-DD, 미국 현지)의 실적 발표 기업 목록.

    Returns:
        DataFrame[date, symbol, name, time, time_label, eps_forecast, num_estimates, last_year_eps, market_cap, fiscal_quarter]
        time_label은 '장전'/'장후'/'미정'. 실패하거나 발표 기업이 없으면 빈 DataFrame.
    """
    try:
        resp = requests.get(URL, params={"date": day}, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        rows = ((resp.json().get("data") or {}).get("rows")) or []
    except Exception as e:
        logger.error("Nasdaq 실적 캘린더 조회 실패 (%s): %s", day, e)
        return pd.DataFrame()

    out = [{
        "date": day,
        "symbol": r.get("symbol"),
        "name": r.get("name"),
        "time": r.get("time"),
        "time_label": TIME_LABELS.get(r.get("time"), r.get("time")),
        "eps_forecast": _to_float(r.get("epsForecast")),
        "num_estimates": r.get("noOfEsts"),
        "last_year_eps": _to_float(r.get("lastYearEPS")),
        "market_cap": r.get("marketCap"),
        "fiscal_quarter": r.get("fiscalQuarterEnding"),
    } for r in rows]
    return pd.DataFrame(out)


def get_earnings_range(start: str, end: str, symbols: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """
    기간(양 끝 포함, 평일만) 실적 발표 일정을 모읍니다. symbols를 주면 그 종목만 남긴다.

    예: 주간 가이드 OUTLOOK 캘린더 ⑤번 범주
        get_earnings_range('2026-10-19', '2026-10-23', ['MSFT', 'META', 'NFLX', 'TSLA'])
    """
    d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
    frames: List[pd.DataFrame] = []
    d = d0
    while d <= d1:
        if d.weekday() < 5:
            df = get_earnings_on(d.isoformat())
            if not df.empty:
                frames.append(df)
            time.sleep(0.3)
        d += timedelta(days=1)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    if symbols is not None:
        wanted = {s.upper() for s in symbols}
        df = df[df["symbol"].str.upper().isin(wanted)]
    return df.reset_index(drop=True)


def find_earnings_date(symbol: str, start: str, days: int = 45) -> Optional[dict]:
    """
    start부터 days일 안에서 해당 종목의 첫 실적 발표일을 찾습니다(하루씩 조회하므로 느리다).
    찾으면 get_earnings_on 행(dict), 없으면 None.
    """
    d = date.fromisoformat(start)
    for _ in range(days):
        if d.weekday() < 5:
            df = get_earnings_on(d.isoformat())
            if not df.empty:
                hit = df[df["symbol"].str.upper() == symbol.upper()]
                if not hit.empty:
                    return hit.iloc[0].to_dict()
            time.sleep(0.3)
        d += timedelta(days=1)
    return None
