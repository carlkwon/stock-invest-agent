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

BASE_URL = "https://ecos.bok.or.kr/api"

# 자주 쓰이는 통계표코드/항목코드 (2026-08-28 기준 실제 호출로 검증된 값만 표기, 나머지는 ECOS Open API
# 포털(https://ecos.bok.or.kr/api/#/) "통계코드검색" 화면에서 직접 확인 후 사용 권장)
STAT_CODES = {
    "base_rate": {"stat_code": "722Y001", "item_code1": "0101000", "desc": "한국은행 기준금리 (검증됨)"},
    "usd_krw": {"stat_code": "731Y001", "item_code1": "0000001", "desc": "원/미국달러 매매기준율 (검증됨)"},
    # 아래는 ECOS에 공식 문서화된 코드이나 이번 세션에서 실호출 검증은 하지 않음 — 사용 전 재확인 권장
    "cpi": {"stat_code": "901Y009", "item_code1": "0", "desc": "소비자물가지수(총지수, 미검증)"},
    "m2": {"stat_code": "101Y003", "item_code1": "BBHS00", "desc": "M2(광의통화, 평잔, 미검증)"},
}


def _get_key() -> Optional[str]:
    key = os.getenv("ECOS_OPENAPI_KEY")
    if not key or key.startswith("your_"):
        logger.error("ECOS_OPENAPI_KEY가 설정되지 않았습니다. (.env 파일 확인 필요)")
        return None
    return key


def get_key_statistics(count: int = 100) -> pd.DataFrame:
    """
    한국은행 '100대 주요 통계지표'(기준금리, 환율, GDP, 통화량 등)를 한 번에 가져옵니다.
    가장 빠르게 매크로 스냅샷을 확인할 때 유용합니다.

    Args:
        count (int): 가져올 지표 개수 (최대 약 100개 내외)

    Returns:
        pd.DataFrame: CLASS_NAME(분류), KEYSTAT_NAME(지표명), DATA_VALUE(값),
                     CYCLE(기준시점), UNIT_NAME(단위) 컬럼을 갖는 DataFrame.
                     오류 발생 시 빈 DataFrame 반환.
    """
    key = _get_key()
    if not key:
        return pd.DataFrame()

    url = f"{BASE_URL}/KeyStatisticList/{key}/json/kr/1/{count}"
    try:
        logger.info("ECOS 100대 주요 통계지표 조회 중...")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if "RESULT" in data:
            logger.error(f"ECOS API 오류: {data['RESULT'].get('MESSAGE', data['RESULT'])}")
            return pd.DataFrame()

        rows = data.get("KeyStatisticList", {}).get("row", [])
        df = pd.DataFrame(rows)
        logger.info(f"ECOS 주요 통계지표 수집 완료 (총 {len(df)}건)")
        return df

    except Exception as e:
        logger.error(f"ECOS 주요 통계지표 조회 중 오류 발생: {e}")
        return pd.DataFrame()


def get_statistic_search(
    stat_code: str,
    item_code1: str,
    cycle: str,
    start: str,
    end: str,
    item_code2: str = "",
    item_code3: str = "",
    item_code4: str = "",
    count: int = 1000,
) -> pd.DataFrame:
    """
    ECOS StatisticSearch API — 특정 통계표코드(stat_code)의 시계열 데이터를 조회합니다.
    통계표코드/항목코드는 ECOS Open API 포털(ecos.bok.or.kr/api) "통계코드검색"에서 확인 가능하며,
    STAT_CODES 딕셔너리에 자주 쓰는 코드 일부를 정리해뒀습니다.

    Args:
        stat_code (str): 통계표코드 (예: '722Y001' 기준금리)
        item_code1 (str): 통계항목코드1 (예: '0101000')
        cycle (str): 주기 — 'D'(일) / 'M'(월) / 'Q'(분기) / 'A'(연)
        start (str): 검색 시작일자 (주기에 맞는 형식, 예: 월 주기면 '202501')
        end (str): 검색 종료일자 (예: '202608')
        item_code2~4 (str): 세부 항목코드 (해당 통계표에 존재하는 경우만 사용)
        count (int): 최대 조회 건수

    Returns:
        pd.DataFrame: TIME(시점), DATA_VALUE(값), UNIT_NAME(단위), STAT_NAME(통계명) 등을 포함하는 DataFrame.
                     오류 발생 시 빈 DataFrame 반환.
    """
    key = _get_key()
    if not key:
        return pd.DataFrame()

    # ECOS URL 경로 규격: /StatisticSearch/{인증키}/{요청유형}/{언어}/{시작건수}/{종료건수}/{통계표코드}/{주기}/{시작일}/{종료일}/{항목1}/{항목2}/{항목3}/{항목4}
    path_parts = [
        "StatisticSearch", key, "json", "kr", "1", str(count),
        stat_code, cycle, start, end, item_code1,
    ]
    if item_code2:
        path_parts.append(item_code2)
    if item_code3:
        path_parts.append(item_code3)
    if item_code4:
        path_parts.append(item_code4)

    url = "/".join([BASE_URL] + path_parts)
    try:
        logger.info(f"ECOS StatisticSearch 조회 중 (stat_code={stat_code}, item_code1={item_code1})...")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if "RESULT" in data:
            logger.error(f"ECOS API 오류: {data['RESULT'].get('MESSAGE', data['RESULT'])}")
            return pd.DataFrame()

        rows = data.get("StatisticSearch", {}).get("row", [])
        if not rows:
            logger.warning("조회 결과가 없습니다. stat_code/item_code/기간을 확인하세요.")
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df["DATA_VALUE"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")
        logger.info(f"ECOS 시계열 수집 완료 (총 {len(df)}건)")
        return df

    except Exception as e:
        logger.error(f"ECOS StatisticSearch 조회 중 오류 발생: {e}")
        return pd.DataFrame()


def get_base_rate(start: str = "202401", end: Optional[str] = None) -> pd.DataFrame:
    """한국은행 기준금리 월별 시계열을 가져옵니다. (검증된 통계표코드 사용)"""
    end = end or pd.Timestamp.today().strftime("%Y%m")
    code = STAT_CODES["base_rate"]
    return get_statistic_search(code["stat_code"], code["item_code1"], "M", start, end)


def get_usd_krw_rate(start: str, end: Optional[str] = None) -> pd.DataFrame:
    """원/달러 매매기준율 일별 시계열을 가져옵니다. (검증된 통계표코드 사용, start/end는 YYYYMMDD)"""
    end = end or pd.Timestamp.today().strftime("%Y%m%d")
    code = STAT_CODES["usd_krw"]
    return get_statistic_search(code["stat_code"], code["item_code1"], "D", start, end)
