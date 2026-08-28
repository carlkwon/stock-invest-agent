import sys
import io
import pandas as pd
from data.ecos_provider import get_key_statistics, get_base_rate
from data.krx_openapi_provider import get_kospi_index_daily, get_kospi_daily_trade

# UTF-8 출력 강제 (윈도우 환경 한글 깨짐 방지)
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding='utf-8')


def run_test():
    print("=== [테스트 1] ECOS 100대 주요 통계지표 ===")
    df_stats = get_key_statistics(count=10)
    if not df_stats.empty:
        print(f"성공: 총 {len(df_stats)}건 조회됨")
        print(df_stats[["CLASS_NAME", "KEYSTAT_NAME", "DATA_VALUE", "UNIT_NAME", "CYCLE"]])
    else:
        print("실패: ECOS_OPENAPI_KEY 설정을 확인하세요.")

    print("\n=== [테스트 2] ECOS 한국은행 기준금리 (최근 6개월) ===")
    import datetime
    end = datetime.date.today().strftime("%Y%m")
    start = (datetime.date.today().replace(day=1) - datetime.timedelta(days=180)).strftime("%Y%m")
    df_rate = get_base_rate(start=start, end=end)
    if not df_rate.empty:
        print(f"성공: 총 {len(df_rate)}건 조회됨")
        print(df_rate[["TIME", "DATA_VALUE", "UNIT_NAME"]])
    else:
        print("실패: 기준금리 데이터를 가져오지 못했습니다.")

    print("\n=== [테스트 3] KRX Open API 코스피 지수 일별시세 ===")
    # 당일(장중/장마감 전)은 데이터가 비어있을 수 있어, 가장 최근 확정된 과거 거래일부터
    # 최대 5일 역순으로 값이 나올 때까지 탐색한다.
    df_krx = pd.DataFrame()
    base_date = None
    for days_back in range(1, 6):
        base_date = (datetime.date.today() - datetime.timedelta(days=days_back)).strftime("%Y%m%d")
        df_krx = get_kospi_index_daily(base_date)
        if not df_krx.empty:
            break

    if not df_krx.empty:
        print(f"성공 (기준일 {base_date}): 총 {len(df_krx)}건 조회됨")
        kospi_row = df_krx[df_krx["IDX_NM"].str.strip() == "코스피"]
        if not kospi_row.empty:
            r = kospi_row.iloc[0]
            print(f"  코스피 종가: {r['CLSPRC_IDX']} ({r['CMPPREVDD_IDX']}, {r['FLUC_RT']}%), 시가총액: {int(r['MKTCAP']):,}원")
    else:
        print(
            "실패: 최근 5거래일 모두 데이터가 비어있습니다.\n"
            "  → KRX_OPENAPI_SECRET_KEY 설정 및 'KOSPI 시리즈 일별시세정보' 서비스 승인 상태를 확인하세요."
        )

    print("\n=== [테스트 4] KRX Open API 유가증권 종목별 시가총액 (동일 기준일) ===")
    if base_date:
        df_stk = get_kospi_daily_trade(base_date)
        if not df_stk.empty:
            print(f"성공: 총 {len(df_stk)}개 종목 조회됨")
            top5 = df_stk.assign(MKTCAP=pd.to_numeric(df_stk["MKTCAP"])).nlargest(5, "MKTCAP")
            print(top5[["ISU_NM", "TDD_CLSPRC", "FLUC_RT", "MKTCAP"]].to_string(index=False))
        else:
            print("실패: 종목별 시가총액 데이터를 가져오지 못했습니다.")


if __name__ == "__main__":
    run_test()
