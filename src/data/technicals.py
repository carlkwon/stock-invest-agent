import pandas as pd
from typing import Dict, Optional

# 주간 가이드·섹터 리포트에서 반복 계산하던 기술적 지표 모음.
# 입력은 종가 시계열(날짜 오름차순)이라 한국(네이버 fchart)·미국(Yahoo) 어느 소스든 쓸 수 있다.


def summarize_technicals(
    close: pd.Series,
    high: Optional[pd.Series] = None,
    bb_window: int = 20,
    bb_k: float = 2.0,
) -> Dict[str, float]:
    """
    종가 시계열로 이동평균 배열·볼린저 %B·52주 고점 대비·최근 5일 최대 일간 상승률을 계산합니다.

    Args:
        close: 종가 Series (날짜 오름차순, 최소 120개 권장)
        high: 고가 Series. 주어지면 52주 고점을 고가 기준으로, 없으면 종가 기준으로 잡는다.
        bb_window / bb_k: 볼린저밴드 기간·표준편차 배수 (기본 20일·2σ)

    Returns:
        {'last', 'ma5', 'ma20', 'ma60', 'ma120', 'bb_lower', 'bb_upper', 'pct_b',
         'high_52w', 'from_high_52w_pct', 'max_daily_gain_5d_pct'}
        %B는 1 초과면 상단 밴드 돌파(과열), 0 미만이면 하단 이탈.
        max_daily_gain_5d_pct는 원칙 4 과열 컷(단일일 +10%) 점검용이다.
    """
    close = close.dropna().reset_index(drop=True)
    last = float(close.iloc[-1])
    ma = {f"ma{k}": float(close.tail(k).mean()) for k in (5, 20, 60, 120)}

    window = close.tail(bb_window)
    # 기존 리포트 계산과 같게 모집단 표준편차(ddof=0)를 쓴다.
    mid, sd = float(window.mean()), float(window.std(ddof=0))
    lower, upper = mid - bb_k * sd, mid + bb_k * sd
    pct_b = (last - lower) / (upper - lower) if upper > lower else float("nan")

    ref = (high.dropna() if high is not None else close).tail(252)
    high_52w = float(ref.max())

    daily = close.pct_change().tail(5) * 100

    return {
        "last": last,
        **ma,
        "bb_lower": lower,
        "bb_upper": upper,
        "pct_b": pct_b,
        "high_52w": high_52w,
        "from_high_52w_pct": (last / high_52w - 1) * 100,
        "max_daily_gain_5d_pct": float(daily.max()),
    }
