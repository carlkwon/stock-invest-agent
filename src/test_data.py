import sys
import io
from data.krx_provider import get_krx_listings, get_stock_price

# UTF-8 출력 강제 (윈도우 환경 한글 깨짐 방지)
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding='utf-8')

def run_test():
    print("=== [테스트 1] KRX 종목 목록 가져오기 ===")
    df_listings = get_krx_listings()
    if not df_listings.empty:
        print(f"성공: 총 {len(df_listings)}개 종목 조회됨")
        print("\n[상위 5개 종목 샘플]")
        # 한글 정렬 및 출력을 깔끔하게 확인하기 위해 pandas 출력 옵션 조정
        import pandas as pd
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.unicode.east_asian_width', True) # 한글 정렬 폭 맞춤
        print(df_listings.head())
    else:
        print("실패: 종목 목록을 가져오지 못했습니다.")

    print("\n=== [테스트 2] 삼성전자(005930) 최근 5영업일 주가 가져오기 ===")
    # 오늘 기준 최근 10일간의 주가를 가져와서 주말 제외 5영업일 출력
    import datetime
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    start_date = (datetime.date.today() - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    
    df_price = get_stock_price('005930', start_date, end_date)
    if not df_price.empty:
        print(f"성공: {len(df_price)}일간의 데이터 조회됨")
        print("\n[최근 주가 데이터 샘플]")
        print(df_price.tail())
    else:
        print("실패: 삼성전자 주가 데이터를 가져오지 못했습니다.")

if __name__ == "__main__":
    run_test()
