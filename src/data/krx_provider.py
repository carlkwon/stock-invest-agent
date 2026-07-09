import FinanceDataReader as fdr
import pandas as pd
from typing import Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_krx_listings() -> pd.DataFrame:
    """
    KRX(한국거래소) 전체 상장 종목 목록을 가져옵니다.
    
    Returns:
        pd.DataFrame: 종목코드, 종목명, 시장구분 등을 포함하는 DataFrame.
                     오류 발생 시 빈 DataFrame 반환.
    """
    try:
        logger.info("KRX 상장 종목 목록 수집 중...")
        df = fdr.StockListing('KRX')
        
        # 필요한 주요 컬럼 필터링 및 이름 변경
        # 컬럼 존재 여부 확인 후 처리
        columns_map = {
            'Code': 'ticker',
            'Name': 'name',
            'Market': 'market',
            'Sector': 'sector',
            'Industry': 'industry'
        }
        
        # 실제 존재하는 컬럼만 선택
        existing_cols = [col for col in columns_map.keys() if col in df.columns]
        df_filtered = df[existing_cols].rename(columns={col: columns_map[col] for col in existing_cols})
        
        logger.info(f"KRX 상장 종목 수집 완료 (총 {len(df_filtered)}개 종목)")
        return df_filtered
        
    except Exception as e:
        logger.error(f"KRX 상장 종목 목록 수집 중 오류 발생: {e}")
        return pd.DataFrame()

def get_stock_price(ticker: str, start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    특정 종목의 지정 기간 동안의 일별 주가 데이터를 가져옵니다.
    
    Args:
        ticker (str): 종목 코드 (예: '005930' - 삼성전자)
        start_date (str): 시작일 (예: '2026-01-01')
        end_date (str, optional): 종료일 (예: '2026-06-30'). 지정하지 않으면 오늘 날짜까지 조회.
        
    Returns:
        pd.DataFrame: 날짜(Index), 시가(Open), 고가(High), 저가(Low), 종가(Close), 거래량(Volume), 대비(Change) 컬럼을 갖는 DataFrame.
                     오류 발생 시 빈 DataFrame 반환.
    """
    try:
        logger.info(f"종목 코드 {ticker} 주가 데이터 수집 중 (기간: {start_date} ~ {end_date or '오늘'})...")
        df = fdr.DataReader(ticker, start=start_date, end=end_date)
        
        if df.empty:
            logger.warning(f"종목 코드 {ticker}의 데이터가 없습니다.")
            return pd.DataFrame()
            
        logger.info(f"종목 코드 {ticker} 주가 데이터 수집 완료 ({len(df)}개 행)")
        return df
        
    except Exception as e:
        logger.error(f"종목 코드 {ticker} 주가 데이터 수집 중 오류 발생: {e}")
        return pd.DataFrame()
