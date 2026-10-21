import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple

# 주간 가이드·섹터 리포트·퀀트 백테스트에서 반복 계산하던 기술적 지표 모음.
# 입력은 종가 시계열(날짜 오름차순)이라 한국(네이버 fchart)·미국(Yahoo) 어느 소스든 쓸 수 있다.


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Wilder의 평활화 방식을 적용한 14일 상대강도지수(RSI)를 계산합니다.
    30 이하는 과매도(반등 잠재력), 70 이상은 과매수(과열 경계) 구간으로 해석합니다.
    """
    close = close.dropna().astype(float)
    if len(close) < period + 1:
        return pd.Series(np.nan, index=close.index)

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's Exponential Smoothing (alpha = 1 / period)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    # loss가 0인 경우 100으로 수렴
    rsi = rsi.fillna(100.0).where(avg_loss != 0, 100.0)
    rsi = rsi.where(avg_gain != 0, 0.0)
    return rsi


def calculate_macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """
    이동평균 수렴확산(MACD) 지표를 계산합니다.

    Returns:
        DataFrame[macd, signal, hist]
        hist > 0: 매수세 우위 (상승 모멘텀)
        hist < 0: 매도세 우위 (하락 모멘텀)
    """
    close = close.dropna().astype(float)
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line

    return pd.DataFrame({
        "macd": macd_line,
        "signal": signal_line,
        "hist": hist,
    }, index=close.index)


def calculate_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """
    평균 실질 변동폭(ATR: Average True Range)을 계산합니다.
    변동성 측정 및 변동성 기반 트레일링 스탑(Trailing Stop Loss)의 핵심 척도입니다.
    """
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    return atr


def calculate_stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3,
) -> pd.DataFrame:
    """
    스토캐스틱 슬로우(Stochastic Slow %K, %D) 지표를 계산합니다.
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    denom = (highest_high - lowest_low).replace(0, np.nan)
    fast_k = ((close - lowest_low) / denom) * 100.0
    slow_k = fast_k.rolling(window=d_period).mean()
    slow_d = slow_k.rolling(window=d_period).mean()

    return pd.DataFrame({"slow_k": slow_k, "slow_d": slow_d}, index=close.index)


def check_ma_alignment(close: pd.Series) -> str:
    """
    이동평균선 배열 상태(정배열/역배열/혼조)를 판정합니다.
    - 정배열(bullish): MA5 > MA20 > MA60 > MA120 (강력한 추세 상승)
    - 역배열(bearish): MA5 < MA20 < MA60 < MA120 (추세 하락)
    - 혼조(mixed): 그 외 수렴 및 전환 구간
    """
    close = close.dropna().astype(float)
    if len(close) < 120:
        return "insufficient_data"

    ma5 = close.tail(5).mean()
    ma20 = close.tail(20).mean()
    ma60 = close.tail(60).mean()
    ma120 = close.tail(120).mean()

    if ma5 > ma20 > ma60 > ma120:
        return "bullish_alignment"
    elif ma5 < ma20 < ma60 < ma120:
        return "bearish_alignment"
    else:
        return "mixed"


def calculate_trailing_stop(
    close: pd.Series,
    high: Optional[pd.Series] = None,
    drop_pct: float = 7.0,
    atr_mult: Optional[float] = None,
    atr_period: int = 14,
) -> pd.DataFrame:
    """
    최고가 대비 트레일링 스탑(Trailing Stop Loss) 라인을 계산합니다.

    Args:
        close: 종가 Series
        high: 고가 Series (생략 시 종가 사용)
        drop_pct: 고점 대비 고정 하락 허용률 (예: 7.0 -> 전고점 대비 -7% 이탈 시 익절/손절)
        atr_mult: ATR 배수 지정 시 고정 % 대신 ATR x 배수를 사용 (예: 2.5x ATR)

    Returns:
        DataFrame[peak_price, stop_line, is_stopped]
    """
    ref = high if high is not None else close
    ref = ref.dropna().astype(float)
    close = close.loc[ref.index].astype(float)

    cum_max = ref.cummax()

    if atr_mult is not None and high is not None:
        low = close.copy()  # fallback low
        atr = calculate_atr(high, low, close, period=atr_period)
        stop_line = cum_max - (atr * atr_mult)
    else:
        stop_line = cum_max * (1.0 - drop_pct / 100.0)

    # 스탑 라인은 이전 값보다 내려가지 않는 단방향 상향 조정
    stop_line = stop_line.cummax()
    is_stopped = close < stop_line

    return pd.DataFrame({
        "close": close,
        "peak_price": cum_max,
        "stop_line": stop_line,
        "is_stopped": is_stopped,
    }, index=close.index)


def summarize_technicals(
    close: pd.Series,
    high: Optional[pd.Series] = None,
    low: Optional[pd.Series] = None,
    bb_window: int = 20,
    bb_k: float = 2.0,
) -> Dict[str, float]:
    """
    종가 시계열로 이동평균 배열·볼린저 %B·RSI·MACD·52주 고점 대비·최근 5일 최대 일간 상승률을 계산합니다.
    기존 반환 키와의 100% 하위 호환성을 유지하면서 정량 분석 지표를 확장 제공합니다.

    Args:
        close: 종가 Series (날짜 오름차순, 최소 120개 권장)
        high: 고가 Series. 주어지면 52주 고점을 고가 기준으로, 없으면 종가 기준으로 잡는다.
        low: 저가 Series. 주어지면 ATR 등에 활용.
        bb_window / bb_k: 볼린저밴드 기간·표준편차 배수 (기본 20일·2σ)

    Returns:
        {'last', 'ma5', 'ma20', 'ma60', 'ma120', 'bb_lower', 'bb_upper', 'pct_b',
         'high_52w', 'from_high_52w_pct', 'max_daily_gain_5d_pct',
         'rsi_14', 'macd', 'macd_signal', 'macd_hist', 'ma_alignment'}
    """
    close = close.dropna().reset_index(drop=True).astype(float)
    last = float(close.iloc[-1])
    ma = {f"ma{k}": float(close.tail(k).mean()) for k in (5, 20, 60, 120)}

    window = close.tail(bb_window)
    mid, sd = float(window.mean()), float(window.std(ddof=0))
    lower, upper = mid - bb_k * sd, mid + bb_k * sd
    pct_b = (last - lower) / (upper - lower) if upper > lower else float("nan")

    ref = (high.dropna().astype(float) if high is not None else close).tail(252)
    high_52w = float(ref.max())

    daily = close.pct_change().tail(5) * 100.0
    max_daily_gain = float(daily.max()) if not daily.empty else 0.0

    # 보조지표 계산
    rsi_s = calculate_rsi(close, period=14)
    rsi_14 = float(rsi_s.iloc[-1]) if not rsi_s.empty and not np.isnan(rsi_s.iloc[-1]) else 50.0

    macd_df = calculate_macd(close)
    macd_val = float(macd_df["macd"].iloc[-1]) if not macd_df.empty else 0.0
    macd_sig = float(macd_df["signal"].iloc[-1]) if not macd_df.empty else 0.0
    macd_h = float(macd_df["hist"].iloc[-1]) if not macd_df.empty else 0.0

    alignment = check_ma_alignment(close)

    return {
        "last": last,
        **ma,
        "bb_lower": lower,
        "bb_upper": upper,
        "pct_b": pct_b,
        "high_52w": high_52w,
        "from_high_52w_pct": (last / high_52w - 1) * 100.0,
        "max_daily_gain_5d_pct": max_daily_gain,
        "rsi_14": rsi_14,
        "macd": macd_val,
        "macd_signal": macd_sig,
        "macd_hist": macd_h,
        "ma_alignment": alignment,
    }
