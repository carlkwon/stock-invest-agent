import sys
import io
from data.gsheet_provider import get_portfolio_from_gsheet

# UTF-8 출력 강제 (윈도우 환경 한글 깨짐 방지)
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding='utf-8')

def test_gsheet():
    print("=== [구글 스프레드시트 연동 테스트] ===")
    
    # 포트폴리오 데이터 읽기 (시트 이름이 '시트1'이 아닐 경우 첫 번째 시트가 자동 로드됨)
    df_portfolio = get_portfolio_from_gsheet()
    
    if not df_portfolio.empty:
        print(f"\n성공: 포트폴리오 데이터를 성공적으로 불러왔습니다. (총 {len(df_portfolio)}개 종목)")
        print("\n[수집된 포트폴리오 데이터]")
        
        # 출력 옵션 설정
        import pandas as pd
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.unicode.east_asian_width', True)
        
        print(df_portfolio)
    else:
        print("\n실패: 구글 스프레드시트 데이터를 가져오지 못했습니다. 로그 에러 메시지를 확인하세요.")

if __name__ == "__main__":
    test_gsheet()
