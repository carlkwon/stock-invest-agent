import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 레이 달리오 올웨더(Risk Parity) 포트폴리오, 자산 배분·리밸런싱 및 위험-수익 프로파일 분석 모듈.
# scipy 등 외부 무거운 패키지 없이 numpy/pandas만으로 경량화 구현되어 안정적으로 구동된다.

# 전통적 올웨더 기본 비중 (Ray Dalio All Weather Benchmark)
ALL_WEATHER_BENCHMARK = {
    "VTI": 0.30,  # 미국 전체 주식
    "TLT": 0.40,  # 미국 장기 국채 (20Y+)
    "IEF": 0.15,  # 미국 중기 국채 (7-10Y)
    "GLD": 0.075, # 금 (Gold)
    "DBC": 0.075, # 원자재 (Commodity Index)
}

# 4계절 매크로 국면별 권장 비중 (성장/인플레 4분면 동적 배분)
REGIME_WEIGHT_TEMPLATES = {
    "standard": ALL_WEATHER_BENCHMARK,
    "high_inflation": {
        "VTI": 0.15,
        "TLT": 0.15,
        "IEF": 0.15,
        "GLD": 0.25,
        "DBC": 0.30,
    },
    "deflation_recession": {
        "VTI": 0.10,
        "TLT": 0.50,
        "IEF": 0.30,
        "GLD": 0.10,
        "DBC": 0.00,
    },
    "goldilocks_growth": {
        "VTI": 0.50,
        "TLT": 0.20,
        "IEF": 0.10,
        "GLD": 0.10,
        "DBC": 0.10,
    },
    "stagflation": {
        "VTI": 0.10,
        "TLT": 0.15,
        "IEF": 0.15,
        "GLD": 0.35,
        "DBC": 0.25,
    },
}


def calculate_returns(prices: pd.DataFrame, method: str = "simple") -> pd.DataFrame:
    """
    다중 자산의 일별 가격 시계열로부터 일별 수익률을 산출합니다.

    Args:
        prices: DataFrame[date_index, asset1, asset2, ...] (오름차순)
        method: 'simple' (단순 수익률) 또는 'log' (로그 수익률)
    """
    prices = prices.dropna().astype(float)
    if method == "log":
        return np.log(prices / prices.shift(1)).dropna()
    return prices.pct_change().dropna()


def calculate_risk_metrics(
    returns: pd.Series,
    rf_rate: float = 0.035,
    periods_per_year: int = 252,
) -> Dict[str, float]:
    """
    단일 자산 또는 포트폴리오의 일별 수익률 시계열로부터 핵심 리스크·성과 지표를 계산합니다.

    Args:
        returns: 일별 수익률 Series
        rf_rate: 무위험이자율 (기본 연 3.5%)
        periods_per_year: 연간 거래일수 (주식 252, 크립토 365)

    Returns:
        {
            'cagr_pct': 연평균 복리 수익률 (%),
            'annualized_vol_pct': 연환산 변동성 (%),
            'sharpe_ratio': 샤프 지수,
            'sortino_ratio': 소르티노 지수 (하방 변동성 기준),
            'max_drawdown_pct': 최대 낙폭 (MDD, %),
            'calmar_ratio': 칼마 비율 (CAGR / |MDD|),
            'var_95_pct': 일간 95% 신뢰수준 VaR (%),
            'cvar_95_pct': 일간 95% 조건부 VaR (Expected Shortfall, %),
            'win_rate_pct': 일간 플러스 수익률 비율 (%)
        }
    """
    r = returns.dropna().astype(float)
    if r.empty or len(r) < 5:
        return {}

    # 누적 수익률 곡선 및 복리 연수익률 (CAGR)
    cum_returns = (1.0 + r).cumprod()
    n_days = len(r)
    n_years = n_days / periods_per_year
    total_return = cum_returns.iloc[-1] - 1.0

    if total_return > -1.0 and n_years > 0:
        cagr = (cum_returns.iloc[-1] ** (1.0 / n_years)) - 1.0
    else:
        cagr = 0.0

    # 연환산 변동성
    vol = r.std(ddof=1) * np.sqrt(periods_per_year)

    # 샤프 지수
    sharpe = (cagr - rf_rate) / vol if vol > 1e-6 else 0.0

    # 소르티노 지수 (하방 편차 기준)
    downside_returns = r[r < 0]
    downside_vol = (downside_returns.std(ddof=1) * np.sqrt(periods_per_year)) if len(downside_returns) > 1 else vol
    sortino = (cagr - rf_rate) / downside_vol if downside_vol > 1e-6 else 0.0

    # 최대 낙폭 (MDD)
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    mdd = abs(float(drawdown.min()))

    # 칼마 비율
    calmar = cagr / mdd if mdd > 1e-6 else 0.0

    # 일간 VaR (95%) & CVaR (95%)
    var_95 = float(np.percentile(r, 5))
    tail_returns = r[r <= var_95]
    cvar_95 = float(tail_returns.mean()) if not tail_returns.empty else var_95

    # 승률 (Win Rate)
    win_rate = (r > 0).sum() / float(len(r)) * 100.0

    return {
        "cagr_pct": cagr * 100.0,
        "annualized_vol_pct": vol * 100.0,
        "sharpe_ratio": float(sharpe),
        "sortino_ratio": float(sortino),
        "max_drawdown_pct": mdd * 100.0,
        "calmar_ratio": float(calmar),
        "var_95_pct": abs(var_95) * 100.0,
        "cvar_95_pct": abs(cvar_95) * 100.0,
        "win_rate_pct": float(win_rate),
    }


def calculate_correlation_matrix(prices_or_returns: pd.DataFrame, is_price: bool = True) -> pd.DataFrame:
    """
    자산 간의 피어슨 상관계수 행렬을 계산합니다.
    """
    if is_price:
        rets = calculate_returns(prices_or_returns)
    else:
        rets = prices_or_returns.dropna().astype(float)
    return rets.corr()


def calculate_risk_parity_weights(
    cov_matrix: pd.DataFrame,
    max_iter: int = 150,
    tol: float = 1e-6,
) -> pd.Series:
    """
    동일 위험 기여(Equal Risk Contribution - ERC) 원칙에 따른 리스크 패리티 최적 비중을 계산합니다.
    각 자산의 변동성과 자산 간 상관관계를 반영하여, 전체 포트폴리오 위험에 미치는 기여도가
    모든 자산에서 동일하도록 가중치를 반복 수렴(Cyclical coordinate scaling) 방식으로 최적화합니다.

    Args:
        cov_matrix: 자산 간 공분산 행렬 (DataFrame)
        max_iter: 최대 반복 수
        tol: 수렴 허용 오차

    Returns:
        pd.Series: 자산별 최적 가중치 (합계 1.0)
    """
    assets = cov_matrix.columns.tolist()
    n = len(assets)
    if n == 0:
        return pd.Series(dtype=float)
    if n == 1:
        return pd.Series([1.0], index=assets)

    V = cov_matrix.values.astype(float)

    # 1. 초기 추정치: 역변동성 가중치 (Inverse Volatility)
    vols = np.sqrt(np.diag(V))
    inv_vols = 1.0 / np.where(vols > 1e-8, vols, 1e-8)
    w = inv_vols / inv_vols.sum()

    # 2. 반복 개선 알고리즘 (Newton-like iterative scaling for ERC)
    for _ in range(max_iter):
        port_var = float(w @ V @ w)
        if port_var <= 1e-12:
            break
        port_vol = np.sqrt(port_var)
        
        # 각 자산의 한계 위험 기여도 (Marginal Risk Contribution)
        mrc = (V @ w) / port_vol
        # 각 자산의 총 위험 기여도 (Total Risk Contribution: TRC_i = w_i * mrc_i)
        trc = w * mrc
        target_trc = port_vol / n

        diff = np.abs(trc - target_trc).max()
        if diff < tol:
            break

        # 위험 기여도가 목표보다 높으면 비중 축소, 낮으면 비중 확대
        scaling = target_trc / np.where(trc > 1e-12, trc, 1e-12)
        w = w * np.sqrt(scaling)
        w = np.clip(w, 0.001, 0.99)
        w = w / w.sum()

    return pd.Series(w, index=assets).round(4)


def analyze_portfolio_drift(
    current_holdings: Dict[str, float],
    target_weights: Dict[str, float],
    total_portfolio_value: float,
    drift_threshold: float = 0.03,
) -> pd.DataFrame:
    """
    현재 자산별 평가금액과 목표 비중을 비교하여 괴리율(Drift)을 분석하고,
    리밸런싱에 필요한 매수/매도 주문 금액을 산출합니다.

    Args:
        current_holdings: {'VTI': 32000.0, 'TLT': 35000.0, ...} (현재 자산별 평가액)
        target_weights: {'VTI': 0.30, 'TLT': 0.40, ...} (목표 비중 합계 1.0)
        total_portfolio_value: 총 포트폴리오 가치 (달러 또는 원화)
        drift_threshold: 리밸런싱 경보 기준 괴리율 (기본 ±3%p)

    Returns:
        DataFrame[asset, current_val, current_weight, target_weight, drift_pct, action, rebalance_amount]
    """
    all_assets = sorted(list(set(current_holdings.keys()) | set(target_weights.keys())))
    rows = []

    for a in all_assets:
        cur_val = current_holdings.get(a, 0.0)
        cur_w = cur_val / total_portfolio_value if total_portfolio_value > 0 else 0.0
        tgt_w = target_weights.get(a, 0.0)
        drift = cur_w - tgt_w
        tgt_val = total_portfolio_value * tgt_w
        rebalance_amt = tgt_val - cur_val  # 양수: 추가 매수 필요, 음수: 매도 필요

        action = "유지 (HOLD)"
        if abs(drift) >= drift_threshold:
            action = f"매수 리밸런싱 (+{abs(drift)*100:.1f}%p)" if drift < 0 else f"매도 차익실현 (-{abs(drift)*100:.1f}%p)"

        rows.append({
            "asset": a,
            "current_value": round(cur_val, 2),
            "current_weight_pct": round(cur_w * 100.0, 2),
            "target_weight_pct": round(tgt_w * 100.0, 2),
            "drift_pct_p": round(drift * 100.0, 2),
            "action": action,
            "rebalance_amount": round(rebalance_amt, 2),
        })

    return pd.DataFrame(rows).sort_values("drift_pct_p", ascending=False).reset_index(drop=True)
