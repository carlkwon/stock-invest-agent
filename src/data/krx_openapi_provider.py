import os
import requests
import pandas as pd
from typing import Optional
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 참고: 기존 src/data/krx_provider.py는 FinanceDataReader(비공식)를 사용합니다.
# 이 모듈은 .env의 KRX_OPENAPI_SECRET_KEY로 인증하는 KRX 정보데이터시스템 공식 Open API
# (data.krx.co.kr → "OpenAPI" 메뉴에서 서비스별 개별 신청 필요)를 호출합니다.
BASE_URL = "https://data-dbg.krx.co.kr/svc/apis"

# 서비스별 엔드포인트 (KRX Open API 포털에 문서화된 경로 기준)
ENDPOINTS = {
    "kospi_daily": "/sto/stk_bydd_trd",       # 유가증권(코스피) 일별매매정보
    "kosdaq_daily": "/sto/ksq_bydd_trd",      # 코스닥 일별매매정보
    "kospi_index": "/idx/kospi_dd_trd",       # 코스피 지수 일별시세
    "kosdaq_index": "/idx/kosdaq_dd_trd",     # 코스닥 지수 일별시세
}


def _get_key() -> Optional[str]:
    key = os.getenv("KRX_OPENAPI_SECRET_KEY")
    if not key or key.startswith("your_"):
        logger.error("KRX_OPENAPI_SECRET_KEY가 설정되지 않았습니다. (.env 파일 확인 필요)")
        return None
    return key


def _call(endpoint: str, params: dict) -> pd.DataFrame:
    key = _get_key()
    if not key:
        return pd.DataFrame()

    url = BASE_URL + endpoint
    try:
        resp = requests.get(url, headers={"AUTH_KEY": key}, params=params, timeout=10)
        data = resp.json()
    except Exception as e:
        logger.error(f"KRX Open API 호출 중 오류 발생 (endpoint={endpoint}): {e}")
        return pd.DataFrame()

    # KRX는 인증/구독 실패 시에도 HTTP 200 + JSON 바디로 respCode를 내려주는 경우가 있어 별도 체크 필요
    if isinstance(data, dict) and data.get("respCode") == "401":
        logger.error(
            f"KRX Open API 인증 실패(401, endpoint={endpoint}): {data.get('respMsg')}. "
            "data.krx.co.kr 포털 로그인 → 'OpenAPI' 메뉴에서 해당 서비스가 실제로 신청/승인되어 있는지, "
            "AUTH_KEY 값이 최신 발급 키와 일치하는지 확인하세요. (서비스는 API별로 개별 신청이 필요합니다)"
        )
        return pd.DataFrame()

    # 정상 응답의 최상위 키는 엔드포인트 마지막 세그먼트를 딴 이름(OutBlock_1 등)인 경우가 많아 첫 리스트를 탐색
    rows = None
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                rows = v
                break
    if not rows:
        logger.warning(f"KRX Open API 응답에서 데이터 목록을 찾지 못했습니다 (endpoint={endpoint}): {data}")
        return pd.DataFrame()

    return pd.DataFrame(rows)


def get_kospi_daily_trade(base_date: str) -> pd.DataFrame:
    """
    코스피(유가증권) 전 종목의 일별 매매정보(시가/고가/저가/종가/거래량/시가총액 등)를 가져옵니다.

    Args:
        base_date (str): 조회 기준일자, 'YYYYMMDD' 형식 (예: '20260827')

    Returns:
        pd.DataFrame: 종목별 일별 매매정보. 오류/미승인 시 빈 DataFrame.
    """
    logger.info(f"KRX 코스피 일별매매정보 조회 중 (기준일: {base_date})...")
    return _call(ENDPOINTS["kospi_daily"], {"basDd": base_date})


def get_kosdaq_daily_trade(base_date: str) -> pd.DataFrame:
    """코스닥 전 종목의 일별 매매정보를 가져옵니다. (base_date: 'YYYYMMDD')"""
    logger.info(f"KRX 코스닥 일별매매정보 조회 중 (기준일: {base_date})...")
    return _call(ENDPOINTS["kosdaq_daily"], {"basDd": base_date})


def get_kospi_index_daily(base_date: str) -> pd.DataFrame:
    """코스피 지수 일별시세(종가/등락률/거래대금 등)를 가져옵니다. (base_date: 'YYYYMMDD')"""
    logger.info(f"KRX 코스피 지수 일별시세 조회 중 (기준일: {base_date})...")
    return _call(ENDPOINTS["kospi_index"], {"basDd": base_date})


def get_kosdaq_index_daily(base_date: str) -> pd.DataFrame:
    """코스닥 지수 일별시세를 가져옵니다. (base_date: 'YYYYMMDD')"""
    logger.info(f"KRX 코스닥 지수 일별시세 조회 중 (기준일: {base_date})...")
    return _call(ENDPOINTS["kosdaq_index"], {"basDd": base_date})
