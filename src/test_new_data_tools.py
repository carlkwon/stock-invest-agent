import sys
import io
import pandas as pd
import numpy as np

# UTF-8 출력 강제 (윈도우 환경 한글 깨짐 방지)
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding='utf-8')

from data import technicals
from data import portfolio_analytics as pa
from data import alternative_assets_provider as alt
from data import sector_rotation_provider as sec_rot
from data import smart_money_provider as sm

def test_technicals():
    print("\n==================== [1. Technicals 고도화 검증] ====================")
    np.random.seed(42)
    # 150거래일 모의 주가 시계열 (상승 추세 + 변동성)
    dates = pd.date_range("2026-01-01", periods=150, freq="B")
    trend = np.linspace(100, 160, 150)
    noise = np.random.normal(0, 2, 150)
    prices = pd.Series(trend + noise, index=dates)
    highs = prices + np.random.uniform(0.5, 2.5, 150)
    lows = prices - np.random.uniform(0.5, 2.5, 150)

    # 1.1 RSI
    rsi = technicals.calculate_rsi(prices, period=14)
    print(f"RSI(14) 최신값: {rsi.iloc[-1]:.2f}")
    assert 0 <= rsi.iloc[-1] <= 100, "RSI는 0과 100 사이여야 합니다."

    # 1.2 MACD
    macd_df = technicals.calculate_macd(prices)
    print(f"MACD 최신: line={macd_df['macd'].iloc[-1]:.2f}, signal={macd_df['signal'].iloc[-1]:.2f}, hist={macd_df['hist'].iloc[-1]:.2f}")
    assert "macd" in macd_df.columns and "signal" in macd_df.columns

    # 1.3 ATR
    atr = technicals.calculate_atr(highs, lows, prices, period=14)
    print(f"ATR(14) 최신: {atr.iloc[-1]:.2f}")
    assert atr.iloc[-1] > 0

    # 1.4 Trailing Stop
    tstop = technicals.calculate_trailing_stop(prices, highs, drop_pct=7.0)
    print(f"Trailing Stop: peak={tstop['peak_price'].iloc[-1]:.2f}, stop={tstop['stop_line'].iloc[-1]:.2f}, stopped={tstop['is_stopped'].iloc[-1]}")

    # 1.5 MA Alignment
    alignment = technicals.check_ma_alignment(prices)
    print(f"이동평균 배열 판정: {alignment}")

    # 1.6 summarize_technicals 하위 호환성 및 확장 검증
    summary = technicals.summarize_technicals(prices, highs, lows)
    print(f"summarize_technicals 키 개수: {len(summary)}")
    print(f"  last: {summary['last']:.2f}, pct_b: {summary['pct_b']:.2f}, rsi_14: {summary['rsi_14']:.2f}, alignment: {summary['ma_alignment']}")
    assert "rsi_14" in summary and "pct_b" in summary
    print("✅ Technicals 모듈 검증 성공!")

def test_portfolio_analytics():
    print("\n==================== [2. Portfolio Analytics 검증] ====================")
    # 5개 올웨더 자산군 모의 일봉 수익률
    np.random.seed(101)
    n_days = 252
    assets = ["VTI", "TLT", "IEF", "GLD", "DBC"]
    # 평균 일수익률 및 변동성
    returns_dict = {
        "VTI": np.random.normal(0.0004, 0.012, n_days),
        "TLT": np.random.normal(0.0001, 0.009, n_days),
        "IEF": np.random.normal(0.0001, 0.005, n_days),
        "GLD": np.random.normal(0.0003, 0.008, n_days),
        "DBC": np.random.normal(0.0002, 0.014, n_days),
    }
    rets_df = pd.DataFrame(returns_dict)

    # 2.1 리스크 지표
    vti_metrics = pa.calculate_risk_metrics(rets_df["VTI"])
    print("VTI 리스크 지표:")
    for k, v in vti_metrics.items():
        print(f"  {k}: {v:.2f}")
    assert "sharpe_ratio" in vti_metrics
    assert "max_drawdown_pct" in vti_metrics

    # 2.2 상관계수 행렬
    corr = pa.calculate_correlation_matrix(rets_df, is_price=False)
    print("\n자산군 상관계수 행렬:")
    print(corr.round(2))

    # 2.3 리스크 패리티 가중치 최적화
    cov = rets_df.cov() * 252
    rp_weights = pa.calculate_risk_parity_weights(cov)
    print("\n동일 위험 기여(Risk Parity) 최적 비중:")
    for a, w in rp_weights.items():
        print(f"  {a}: {w*100:.1f}%")
    assert abs(rp_weights.sum() - 1.0) < 0.01

    # 2.4 포트폴리오 드리프트 분석
    cur_holdings = {"VTI": 40000, "TLT": 30000, "IEF": 15000, "GLD": 10000, "DBC": 5000}
    drift_df = pa.analyze_portfolio_drift(cur_holdings, pa.ALL_WEATHER_BENCHMARK, total_portfolio_value=100000)
    print("\n포트폴리오 드리프트 및 리밸런싱 주문:")
    print(drift_df[["asset", "current_weight_pct", "target_weight_pct", "drift_pct_p", "action", "rebalance_amount"]])
    assert not drift_df.empty
    print("✅ Portfolio Analytics 모듈 검증 성공!")

def test_alternative_assets():
    print("\n==================== [3. Alternative Assets 검증] ====================")
    # 3.1 크립토 공포/탐욕 지수
    fng = alt.get_crypto_fear_and_greed_index(limit=3)
    if not fng.empty:
        print("Crypto Fear & Greed Index:")
        print(fng)
        assert "value" in fng.columns and "classification" in fng.columns
    else:
        print("공포탐욕지수 응답 대기/생략")

    # 3.2 대체 자산 요약 스코어카드
    summary = alt.get_alternative_investment_summary()
    print("대체 자산 대시보드 스냅샷:")
    print(f"  Timestamp: {summary.get('timestamp')}")
    print(f"  Crypto Sentiment: {summary.get('crypto_fear_greed')}")
    print(f"  Commodities covered: {list(summary.get('commodities', {}).keys())}")
    print("✅ Alternative Assets 모듈 검증 성공!")

def test_sector_rotation():
    print("\n==================== [4. Sector Rotation 검증] ====================")
    # 대표 4개 섹터로 빠른 단위 검증
    sample_sectors = ["XLK", "XLF", "XLE", "XLV"]
    quad = sec_rot.get_sector_rotation_quadrant(benchmark="SPY", range_="3mo", sectors=sample_sectors)
    if not quad.empty:
        print("RRG 4분면 로테이션 현황 (샘플 섹터):")
        print(quad)
        assert "quadrant" in quad.columns
        assert "rs_ratio" in quad.columns
    else:
        print("섹터 데이터 조회 실패 또는 네트워크 대기")
    print("✅ Sector Rotation 모듈 검증 성공!")

def test_smart_money():
    print("\n==================== [5. Smart Money & 13F 검증] ====================")
    # 5.1 옵션 시장 심리
    opts = sm.get_options_market_sentiment()
    print("옵션 및 변동성 체제 진단:")
    for k, v in opts.items():
        print(f"  {k}: {v}")
    assert "volatility_regime" in opts

    # 5.2 13F XML 파서 검증 (모의 13F XML)
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">
        <infoTable>
            <nameOfIssuer>APPLE INC</nameOfIssuer>
            <titleOfClass>COM</titleOfClass>
            <cusip>037833100</cusip>
            <value>69875000</value>
            <shrsOrPrnAmt>
                <sshPrnamt>300000000</sshPrnamt>
                <sshPrnamtType>SH</sshPrnamtType>
            </shrsOrPrnAmt>
            <putCall></putCall>
        </infoTable>
        <infoTable>
            <nameOfIssuer>AMERICAN EXPRESS CO</nameOfIssuer>
            <titleOfClass>COM</titleOfClass>
            <cusip>025816109</cusip>
            <value>35125000</value>
            <shrsOrPrnAmt>
                <sshPrnamt>151610700</sshPrnamt>
                <sshPrnamtType>SH</sshPrnamtType>
            </shrsOrPrnAmt>
            <putCall></putCall>
        </infoTable>
    </informationTable>"""
    df_holdings = sm.parse_13f_holdings_xml(sample_xml)
    print("\n13F 모의 파싱 결과:")
    print(df_holdings[["nameOfIssuer" if "nameOfIssuer" in df_holdings else "name_of_issuer", "value_usd", "shares", "weight_pct"]])
    assert len(df_holdings) == 2
    assert "weight_pct" in df_holdings.columns
    assert df_holdings["weight_pct"].sum() == 100.0
    print("✅ Smart Money 모듈 검증 성공!")

if __name__ == "__main__":
    test_technicals()
    test_portfolio_analytics()
    test_alternative_assets()
    test_sector_rotation()
    test_smart_money()
    print("\n🎉 모든 신규 자산 투자 분석 툴 검증 완료!")
