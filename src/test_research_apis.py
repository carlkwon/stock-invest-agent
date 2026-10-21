import sys
import io
import datetime
import pandas as pd
from data import us_market_provider as us
from data import earnings_calendar_provider as ec
from data import sec_edgar_provider as sec
from data import dart_provider as dart

# UTF-8 출력 강제 (윈도우 환경 한글 깨짐 방지)
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding='utf-8')

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)


def run_test():
    today = datetime.date.today()

    print("=== [테스트 1] Yahoo 일봉 (MSFT, 최근 3거래일) ===")
    df = us.get_daily("MSFT", "1mo")
    print(df.tail(3) if not df.empty else "실패: Yahoo 일봉 응답 없음")

    print("\n=== [테스트 2] Yahoo 밸류에이션·실적일 (MSFT, NVDA, JPM) ===")
    q = us.get_quotes(["MSFT", "NVDA", "JPM"])
    print(q[["symbol", "price", "forward_pe", "pbr", "dividend_yield_pct", "earnings_date"]] if not q.empty else "실패: quote 응답 없음")

    print("\n=== [테스트 3] Nasdaq 실적 캘린더 (오늘부터 5일) ===")
    e = ec.get_earnings_range(today.isoformat(), (today + datetime.timedelta(days=4)).isoformat())
    if not e.empty:
        print(f"성공: {len(e)}건. 앞쪽 10건:")
        print(e[["date", "symbol", "time_label", "eps_forecast"]].head(10))
    else:
        print("결과 없음(주말·휴장이거나 API 응답 없음)")

    print("\n=== [테스트 4] SEC EDGAR 공시·재무 (Microsoft, CIK 789019) ===")
    f = sec.get_recent_filings("789019", ["10-Q", "10-K", "8-K"], limit=3)
    print(f[["form", "filing_date", "report_date"]] if not f.empty else "실패: 공시 목록 없음")
    fin = sec.get_financials("789019", last_n=12)
    if not fin.empty:
        fin["revenue_yoy_pct"] = sec.yoy_growth(fin, "revenue")
        print(fin[["period_end", "fy", "fp", "revenue", "net_income", "eps_diluted", "revenue_yoy_pct"]].tail(4))
    print("티커 조회(SEC_USER_AGENT 필요):", sec.get_cik("MSFT"))

    print("\n=== [테스트 5] OpenDART 공시·재무 (삼성전자, DART_API_KEY 필요) ===")
    d = dart.get_disclosures("005930", start=(today - datetime.timedelta(days=30)).strftime("%Y%m%d"))
    print(d.head(5) if not d.empty else "결과 없음: DART_API_KEY 설정을 확인하세요.")
    fs = dart.get_financial_statements("005930", today.year, report="H1")
    print(dart.summarize_financials(fs) if not fs.empty else "재무제표 없음(키 미설정 또는 보고서 미제출)")


if __name__ == "__main__":
    run_test()
