import requests
import pandas as pd
import numpy as np
from typing import Dict, Iterable, List, Optional, Union
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 대체 자산(Alternative Assets: 금, 은, 원자재, 비트코인/가상자산) 데이터 제공자.
# `/Alternative_Assets_Investment` 워크플로우의 정량 시그널 산출을 지원합니다.

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
FNG_URL = "https://api.alternative.me/fng/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# 주요 대체 자산 벤치마크 티커
COMMODITY_TICKERS = {
    "gold": "GLD",        # 금 ETF (SPDR Gold Shares)
    "gold_futures": "GC=F",# 금 선물
    "silver": "SLV",      # 은 ETF (iShares Silver Trust)
    "oil": "USO",         # 원유 ETF (United States Oil Fund)
    "oil_wti": "CL=F",    # WTI 원유 선물
    "copper": "CPER",     # 구리 ETF (United States Copper Index)
    "commodity_broad": "DBC", # 원자재 종합 지수 ETF (Invesco DB Commodity)
    "sp500": "SPY",       # 벤치마크 (비교용)
}

CRYPTO_TICKERS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
}


def get_asset_history(ticker: str, range_: str = "1y", end: Optional[str] = None) -> pd.DataFrame:
    """
    Yahoo Finance v8 Chart API를 통해 대체 자산/원자재/가상자산의 일봉 시계열을 수집합니다.
    """
    try:
        resp = requests.get(
            CHART_URL.format(ticker=ticker),
            params={"range": range_, "interval": "1d"},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json()["chart"]["result"][0]
        timestamps = result.get("timestamp", [])
        quote = result["indicators"]["quote"][0]
    except Exception as e:
        logger.error("대체 자산 시세 조회 실패 (%s): %s", ticker, e)
        return pd.DataFrame()

    df = pd.DataFrame({
        "date": [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in timestamps],
        "open": quote.get("open"),
        "high": quote.get("high"),
        "low": quote.get("low"),
        "close": quote.get("close"),
        "volume": quote.get("volume"),
    }).dropna(subset=["close"])

    if end:
        df = df[df["date"] <= end]

    return df.reset_index(drop=True)


def get_crypto_fear_and_greed_index(limit: int = 30) -> pd.DataFrame:
    """
    Alternative.me 공시 크립토 공포/탐욕 지수(Crypto Fear & Greed Index) 시계열을 조회합니다.

    Returns:
        DataFrame[date, value, classification] (날짜 오름차순)
        classification: 'Extreme Fear'(극단적 공포), 'Fear'(공포), 'Neutral'(중립), 'Greed'(탐욕), 'Extreme Greed'(극단적 탐욕)
    """
    try:
        resp = requests.get(FNG_URL, params={"limit": limit}, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            return pd.DataFrame()
    except Exception as e:
        logger.error("Crypto Fear & Greed 지수 조회 실패: %s", e)
        return pd.DataFrame()

    rows = []
    for d in data:
        dt = datetime.fromtimestamp(int(d["timestamp"])).strftime("%Y-%m-%d")
        rows.append({
            "date": dt,
            "value": int(d["value"]),
            "classification": d.get("value_classification", ""),
        })

    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def get_crypto_summary(range_: str = "6mo") -> pd.DataFrame:
    """
    주요 가상자산(BTC, ETH, SOL)의 현재가, 24h 변동률, 1주/1개월/3개월 수익률을 정리합니다.
    """
    rows = []
    for name, sym in CRYPTO_TICKERS.items():
        df = get_asset_history(sym, range_=range_)
        if df.empty or len(df) < 2:
            continue
        cur_price = float(df["close"].iloc[-1])
        prev_close = float(df["close"].iloc[-2])
        change_1d = (cur_price / prev_close - 1.0) * 100.0

        ret_1w = (cur_price / float(df["close"].iloc[-6]) - 1.0) * 100.0 if len(df) >= 6 else np.nan
        ret_1m = (cur_price / float(df["close"].iloc[-22]) - 1.0) * 100.0 if len(df) >= 22 else np.nan
        ret_3m = (cur_price / float(df["close"].iloc[-65]) - 1.0) * 100.0 if len(df) >= 65 else np.nan

        rows.append({
            "asset": name,
            "ticker": sym,
            "price": round(cur_price, 2),
            "change_1d_pct": round(change_1d, 2),
            "return_1w_pct": round(ret_1w, 2),
            "return_1m_pct": round(ret_1m, 2),
            "return_3m_pct": round(ret_3m, 2),
        })

    return pd.DataFrame(rows)


def calculate_cross_asset_ratios(range_: str = "1y") -> pd.DataFrame:
    """
    대체 자산 간 크로스 매크로 비율(Cross-Asset Ratios)을 계산합니다.

    지표 의미:
    1. gold_to_sp500: 금(GLD) / S&P500(SPY) -> 상승 시 안전자산 선호(Risk-off), 하락 시 위험선호(Risk-on)
    2. btc_to_gold: 비트코인(BTC-USD) / 금(GLD) -> 디지털 금 vs 실물 금 상대 모멘텀
    3. copper_to_gold: 구리(CPER) / 금(GLD) -> '닥터 코퍼' 경기 회복 탄력도 (상승 시 경기 확장, 하락 시 경기 둔화)
    4. oil_to_gold: 원유(USO) / 금(GLD) -> 공급망/에너지 인플레이션 충격 및 스태그플레이션 압력
    """
    tickers = {
        "GLD": COMMODITY_TICKERS["gold"],
        "SPY": COMMODITY_TICKERS["sp500"],
        "BTC": CRYPTO_TICKERS["BTC"],
        "CPER": COMMODITY_TICKERS["copper"],
        "USO": COMMODITY_TICKERS["oil"],
    }

    dfs = {}
    for k, t in tickers.items():
        d = get_asset_history(t, range_=range_)
        if not d.empty:
            dfs[k] = d.set_index("date")["close"].astype(float)

    if "GLD" not in dfs:
        logger.error("금(GLD) 시세 부재로 크로스 자산 비율을 계산할 수 없습니다.")
        return pd.DataFrame()

    m = pd.DataFrame(dfs).dropna()
    if m.empty:
        return pd.DataFrame()

    out = pd.DataFrame(index=m.index)
    if "SPY" in m:
        out["gold_to_sp500"] = m["GLD"] / m["SPY"]
    if "BTC" in m:
        out["btc_to_gold"] = m["BTC"] / m["GLD"]
    if "CPER" in m:
        out["copper_to_gold"] = m["CPER"] / m["GLD"]
    if "USO" in m:
        out["oil_to_gold"] = m["USO"] / m["GLD"]

    return out.reset_index()


def get_alternative_investment_summary() -> Dict[str, Union[float, str, dict]]:
    """
    대체 자산 투자 의사결정에 필요한 주요 지표를 단일 대시보드 딕셔너리로 취합합니다.
    """
    # 1. 크립토 공포탐욕지수
    fng_df = get_crypto_fear_and_greed_index(limit=5)
    fng_latest = fng_df.iloc[-1].to_dict() if not fng_df.empty else {"value": 50, "classification": "Neutral"}

    # 2. 금 및 주요 원자재 1일/1개월 수익률
    comm_summary = {}
    for name in ["gold", "silver", "oil", "copper", "commodity_broad"]:
        t = COMMODITY_TICKERS.get(name)
        df = get_asset_history(t, range_="3mo")
        if not df.empty and len(df) >= 2:
            p = float(df["close"].iloc[-1])
            chg_1d = (p / float(df["close"].iloc[-2]) - 1.0) * 100.0
            ret_1m = (p / float(df["close"].iloc[-22]) - 1.0) * 100.0 if len(df) >= 22 else 0.0
            comm_summary[name] = {
                "ticker": t,
                "price": round(p, 2),
                "change_1d_pct": round(chg_1d, 2),
                "return_1m_pct": round(ret_1m, 2),
            }

    # 3. 크로스 자산 비율 최신값
    ratios_df = calculate_cross_asset_ratios(range_="1mo")
    ratios_latest = ratios_df.iloc[-1].to_dict() if not ratios_df.empty else {}

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crypto_fear_greed": fng_latest,
        "commodities": comm_summary,
        "cross_asset_ratios": ratios_latest,
    }
