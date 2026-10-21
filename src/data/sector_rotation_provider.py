import requests
import pandas as pd
import numpy as np
from typing import Dict, Iterable, List, Optional, Tuple
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# S&P 500 11개 주요 SPDR 섹터 및 테마 ETF의 상대강도(Relative Strength),
# 모멘텀 스코어, RRG(Relative Rotation Graph) 4분면 국면 판정 모듈.
# `/sector-investment-report` 및 주간 가이드 주도 섹터 스크리닝을 지원합니다.

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

SECTOR_ETFS: Dict[str, str] = {
    "XLK": "정보기술 (Tech)",
    "XLC": "통신서비스 (Communication)",
    "XLY": "임의소비재 (Consumer Discretionary)",
    "XLF": "금융 (Financials)",
    "XLI": "산업재 (Industrials)",
    "XLE": "에너지 (Energy)",
    "XLV": "헬스케어 (Health Care)",
    "XLP": "필수소비재 (Consumer Staples)",
    "XLU": "유틸리티 (Utilities)",
    "XLRE": "부동산 (Real Estate)",
    "XLB": "소재 (Materials)",
    "SMH": "반도체 (Semiconductors)",
    "IGV": "소프트웨어 (Software)",
}


def _get_history(ticker: str, range_: str = "6mo") -> pd.DataFrame:
    try:
        resp = requests.get(
            CHART_URL.format(ticker=ticker),
            params={"range": range_, "interval": "1d"},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        res = resp.json()["chart"]["result"][0]
        timestamps = res.get("timestamp", [])
        quote = res["indicators"]["quote"][0]
        df = pd.DataFrame({
            "date": [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in timestamps],
            "close": quote.get("close"),
        }).dropna(subset=["close"])
        return df.reset_index(drop=True)
    except Exception as e:
        logger.error("섹터 ETF 시세 조회 실패 (%s): %s", ticker, e)
        return pd.DataFrame()


def get_sector_performance(range_: str = "6mo", benchmark: str = "SPY") -> pd.DataFrame:
    """
    모든 섹터 ETF와 벤치마크(SPY)의 구간별 수익률(1W, 1M, 3M, 6M) 및 벤치마크 대비 초과수익률(Alpha)을 계산합니다.
    """
    tickers = list(SECTOR_ETFS.keys()) + [benchmark]
    price_dict = {}

    for t in tickers:
        df = _get_history(t, range_=range_)
        if not df.empty:
            price_dict[t] = df.set_index("date")["close"].astype(float)

    if benchmark not in price_dict:
        logger.error("벤치마크(%s) 시세가 없어 섹터 성과 분석을 수행할 수 없습니다.", benchmark)
        return pd.DataFrame()

    prices = pd.DataFrame(price_dict).dropna()
    if prices.empty:
        return pd.DataFrame()

    rows = []
    bench_p = prices[benchmark]
    bench_1w = (bench_p.iloc[-1] / bench_p.iloc[-6] - 1.0) * 100.0 if len(bench_p) >= 6 else 0.0
    bench_1m = (bench_p.iloc[-1] / bench_p.iloc[-22] - 1.0) * 100.0 if len(bench_p) >= 22 else 0.0
    bench_3m = (bench_p.iloc[-1] / bench_p.iloc[-65] - 1.0) * 100.0 if len(bench_p) >= 65 else 0.0

    for t, name in SECTOR_ETFS.items():
        if t not in prices:
            continue
        p = prices[t]
        ret_1w = (p.iloc[-1] / p.iloc[-6] - 1.0) * 100.0 if len(p) >= 6 else np.nan
        ret_1m = (p.iloc[-1] / p.iloc[-22] - 1.0) * 100.0 if len(p) >= 22 else np.nan
        ret_3m = (p.iloc[-1] / p.iloc[-65] - 1.0) * 100.0 if len(p) >= 65 else np.nan
        ret_6m = (p.iloc[-1] / p.iloc[0] - 1.0) * 100.0

        # 모멘텀 종합 가중치: 1M 40% + 3M 30% + 6M 30%
        m_score = (ret_1m * 0.40) + (ret_3m * 0.30) + (ret_6m * 0.30)

        # 벤치마크 대비 1개월 알파
        alpha_1m = ret_1m - bench_1m

        rows.append({
            "ticker": t,
            "sector_name": name,
            "last_price": round(float(p.iloc[-1]), 2),
            "return_1w_pct": round(ret_1w, 2),
            "return_1m_pct": round(ret_1m, 2),
            "return_3m_pct": round(ret_3m, 2),
            "return_6m_pct": round(ret_6m, 2),
            "alpha_1m_pct": round(alpha_1m, 2),
            "momentum_score": round(m_score, 2),
        })

    df_out = pd.DataFrame(rows).sort_values("momentum_score", ascending=False).reset_index(drop=True)
    df_out["rank"] = df_out.index + 1
    return df_out


def calculate_relative_strength(
    sector_ticker: str,
    benchmark: str = "SPY",
    range_: str = "6mo",
    sector_df: Optional[pd.DataFrame] = None,
    benchmark_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    특정 섹터의 벤치마크 대비 상대강도(RS = Sector / Benchmark * 100) 및 RS 20일 이동평균을 계산합니다.
    """
    df_sec = sector_df if sector_df is not None else _get_history(sector_ticker, range_=range_)
    df_bm = benchmark_df if benchmark_df is not None else _get_history(benchmark, range_=range_)

    if df_sec.empty or df_bm.empty:
        return pd.DataFrame()

    m = pd.merge(df_sec, df_bm, on="date", suffixes=("_sec", "_bm")).dropna()
    m["rs_line"] = (m["close_sec"] / m["close_bm"]) * 100.0
    m["rs_ma20"] = m["rs_line"].rolling(window=20).mean()
    m["rs_ratio"] = m["rs_line"] / m["rs_ma20"] * 100.0
    # 모멘텀: RS ratio의 최근 10거래일 변화율
    m["rs_momentum"] = m["rs_ratio"] - m["rs_ratio"].shift(10)

    return m[["date", "close_sec", "close_bm", "rs_line", "rs_ma20", "rs_ratio", "rs_momentum"]].dropna()


def get_sector_rotation_quadrant(
    benchmark: str = "SPY",
    range_: str = "6mo",
    sectors: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    RRG(Relative Rotation Graph) 원리에 기반하여 각 섹터를 4대 로테이션 국면으로 분류합니다.

    1. Leading (주도 국면): RS Ratio >= 100 and RS Momentum >= 0 (시장 대비 초과상승 추세 강화)
    2. Weakening (과열 둔화): RS Ratio >= 100 and RS Momentum < 0 (상대강도 우위이나 모멘텀 둔화)
    3. Lagging (후행/소외): RS Ratio < 100 and RS Momentum < 0 (시장 대비 지속 약세)
    4. Improving (회복/반등): RS Ratio < 100 and RS Momentum >= 0 (바닥에서 턴어라운드 시도)
    """
    target_sectors = list(sectors) if sectors is not None else list(SECTOR_ETFS.keys())
    bm_df = _get_history(benchmark, range_=range_)
    if bm_df.empty:
        return pd.DataFrame()

    rows = []
    for t in target_sectors:
        name = SECTOR_ETFS.get(t, t)
        rs_df = calculate_relative_strength(t, benchmark=benchmark, range_=range_, benchmark_df=bm_df)
        if rs_df.empty:
            continue
        latest = rs_df.iloc[-1]
        rs_ratio = float(latest["rs_ratio"])
        rs_mom = float(latest["rs_momentum"])

        if rs_ratio >= 100.0:
            quadrant = "Leading (주도 국면)" if rs_mom >= 0 else "Weakening (과열 둔화)"
        else:
            quadrant = "Improving (회복 국면)" if rs_mom >= 0 else "Lagging (후행/소외)"

        rows.append({
            "ticker": t,
            "sector_name": name,
            "rs_ratio": round(rs_ratio, 2),
            "rs_momentum": round(rs_mom, 2),
            "quadrant": quadrant,
        })

    return pd.DataFrame(rows).sort_values("rs_ratio", ascending=False).reset_index(drop=True)
