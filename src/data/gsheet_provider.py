import os
import gspread
import pandas as pd
from typing import Optional
import logging
from dotenv import load_dotenv

# 로드 환경 변수
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_portfolio_from_gsheet(sheet_name: str = "시트1") -> pd.DataFrame:
    """
    구글 서비스 계정(Service Account) 보안 인증 방식을 사용하여 
    구글 스프레드시트에서 보유 주식 포트폴리오 데이터를 읽어옵니다.
    
    Args:
        sheet_name (str): 데이터를 가져올 워크시트 이름 (기본값: '시트1' 또는 '포트폴리오')
        
    Returns:
        pd.DataFrame: 포트폴리오 데이터가 정리된 DataFrame.
                     오류 발생 시 빈 DataFrame 반환.
    """
    # 환경 변수에서 설정 로드
    creds_path = os.getenv("GOOGLE_SHEET_CREDENTIALS_PATH")
    sheet_key = os.getenv("GOOGLE_SHEET_KEY")
    
    # 가끔 실행 위치(CWD)가 서브디렉터리일 때 상위 폴더의 키 파일을 가리킬 수 있도록 보완
    if creds_path and not os.path.exists(creds_path):
        fallback_path = os.path.join("..", creds_path)
        if os.path.exists(fallback_path):
            creds_path = fallback_path
            
    if not creds_path or not os.path.exists(creds_path):
        logger.error(f"구글 서비스 계정 키 파일 경로가 유효하지 않거나 존재하지 않습니다. (현재 검색 경로: {os.path.abspath(creds_path or '')})")
        return pd.DataFrame()
        
    if not sheet_key or sheet_key == "your_spreadsheet_key_here":
        logger.error("구글 스프레드시트 키가 설정되지 않았습니다. (.env 파일 내 GOOGLE_SHEET_KEY 확인 필요)")
        return pd.DataFrame()
        
    try:
        logger.info("구글 서비스 계정 인증 중...")
        # gspread 서비스 계정 인증
        gc = gspread.service_account(filename=creds_path)
        
        logger.info(f"구글 스프레드시트 여는 중 (Key: {sheet_key})...")
        spreadsheet = gc.open_by_key(sheet_key)
        
        # 특정 워크시트 선택
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # 지정된 시트가 없으면 첫 번째 시트를 기본으로 시도
            logger.warning(f"지정된 시트 '{sheet_name}'를 찾을 수 없습니다. 첫 번째 시트로 조회를 시도합니다.")
            worksheet = spreadsheet.get_worksheet(0)
            
        logger.info(f"시트 '{worksheet.title}' 데이터 로드 중...")
        
        # 모든 행 데이터 가져오기 (첫 번째 행은 헤더로 가정)
        records = worksheet.get_all_records()
        
        if not records:
            logger.warning("스프레드시트에 데이터가 비어 있습니다.")
            return pd.DataFrame()
            
        df = pd.DataFrame(records)
        
        # 한글/영어 컬럼명 정제 및 공백 제거
        df.columns = [col.strip() for col in df.columns]
        
        logger.info(f"포트폴리오 데이터 수집 완료 (총 {len(df)}개 행)")
        return df
        
    except Exception as e:
        import traceback
        logger.error("구글 스프레드시트 데이터 수집 중 오류 발생:")
        traceback.print_exc()
        return pd.DataFrame()
