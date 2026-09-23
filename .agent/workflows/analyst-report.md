---
description: 한미 애널리스트 리포트 정리·요약 워크플로우 (/analyst-report)
---

# 한미 애널리스트 리포트 정리·요약 워크플로우

---

## Meta Data & Description
* **Name:** Korea-US Analyst Report Summary Workflow
* **Version:** 1.1
* **Author:** AI Agent Collaborator
* **Description:** 특정 종목(또는 섹터)에 대해 한국 증권사 리포트와 미국 애널리스트 코멘트/IB 뷰를 수집하여, 투자의견·목표주가·실적 추정치 변경(Revision)·핵심 논리·리스크를 한눈에 비교 분석하는 심층 보고서를 생성합니다.
* **Trigger Command:** `/analyst-report`

---

## Global Context
| Variable | Description | Example / Default |
|----------|-------------|-------------------|
| `{{TICKER}}` | 분석 대상 종목 티커 (한국 종목은 종목코드) | `NVDA`, `005930` |
| `{{COMPANY_NAME}}` | 파일명에 쓰는 기업명. 한글 통용명을 공백 없이 쓴다 (한국 종목은 거래소 공식 종목명) | `삼성전자`, `SK하이닉스`, `엔비디아` |
| `{{PEER_TICKER}}` | (선택) 비교할 동일 섹터 대응 종목 | `AMD` |
| `{{PERIOD}}` | 리포트 수집 기간 | `최근 4주` |
| `{{BASE_DATE}}` | 현재가·상승여력 계산 기준일 (YYYY-MM-DD) | 실행일 직전 거래일 |
| `{{WRITE_DATE}}` | 실제 작성일 (YYYYMMDD) | `20260923` |
| `{{OUTPUT_DIR}}` | 리포트 저장 디렉토리 경로 (없으면 생성) | `reports/analyst/` |
| `{{REPORT_PATH}}` | 생성 파일 경로 (모델별 접두사 `[G]` 또는 `[C]` 적용) | `{{OUTPUT_DIR}}[G]{{COMPANY_NAME}}({{TICKER}})_analyst_summary_{{WRITE_DATE}}.md` |

---

## Data Sources

| 구분 | 소스 | URL / 모듈 | 확보 항목 | 접근성 | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **공통 (시세)** | **[우선순위 1] KRX Open API & FDR** | `src/data/krx_openapi_provider.py` / `FinanceDataReader` | 기준일 종가, 시가총액, PER, PBR, 52주 고저 | 무료 | 국내/미국 종가 및 상승여력 계산의 1차 실측 소스 |
| **한국** | 네이버 증권 - 종목분석 리포트 | https://finance.naver.com/research/company_list.naver | 발표일·증권사·제목·목표주가·투자의견, PDF 원문 | 무료 | 국내 증권사(미래에셋, NH, 삼성 등) 1차 소스 |
| **한국** | 한경컨센서스 | https://consensus.hankyung.com/ | 위 항목 + 애널리스트명, 이전 목표가 | 무료 | 검색·필터가 세밀함. 네이버에 없는 리포트 보완용 |
| **미국** | Zacks Investment Research | `https://www.zacks.com/stock/research/{TICKER}/price-target-stock-forecast` | Zacks Rank(1~5), 컨센서스 목표주가(평균·최고·최저), 커버 애널리스트 수 | 무료 | 미국 컨센서스 수치 1차 소스 |
| **미국** | Seeking Alpha / Finviz / TipRanks | `https://seekingalpha.com/symbol/{TICKER}/ratings` / Yahoo Finance | Wall St. 평균 등급, 등급 분포(Buy/Hold/Sell), EPS 추정치 수정 | 일부 무료 | 세부 코멘트 및 주가 목표 갭 보완용 |
| **미국** | 로이터·블룸버그·CNBC 등 보도 | 검색: `"{TICKER}" upgrade OR downgrade price target` | 개별 IB(골드만, 모건스탠리, JP모건 등)의 의견·목표가 변경 및 배경 | 무료(일부 페이월) | 정식 유료 리포트 대신 주요 IB의 핵심 결론 파악 |

> ⚠️ 미국 정식 리포트(골드만삭스, 모건스탠리 등) 원문은 유료/구독 전용인 경우가 많으므로 공개 언론 보도 및 파이낸스 포털을 활용해 핵심 결론(의견·목표주가·EPS 변경 여부)을 확보합니다.

---

## Workflow Phases

### Phase 1: 대상 확정 (Target Definition)
* **Instructions:**
  1. `{{TICKER}}`, `{{PERIOD}}`(예: 최근 4주)를 확정하세요.
  2. 필요 시 동일 섹터의 미국/국내 대응 종목(`{{PEER_TICKER}}`)을 함께 지정하세요.

### Phase 2: 한국 리포트 및 정량 시세 데이터 수집 (Korea Report & Price Retrieval)
* **Instructions:**
  1. **[우선순위 1] 정확한 시세 확보:** `src/data/krx_openapi_provider.py` 또는 `FinanceDataReader`로 `{{TICKER}}`의 **기준일 종가, 시가총액, Fwd PER, PBR** 수치를 실측값으로 확보하세요. (뉴스 인용 수치 사용 금지)
  2. 네이버 증권 및 한경컨센서스에서 해당 종목 리포트 목록(발표일, 증권사, 애널리스트, 목표주가, 투자의견)을 수집하세요.
  3. 각 리포트에서 다음 항목을 추출하세요:
     - 발표일 / 증권사 / 애널리스트
     - 투자의견 (매수/중립/매도) 및 변경 여부
     - 목표주가 및 변경 여부 (상향/하향/유지)
     - **12M Fwd 이익 추정치(영업이익/EPS) 변경 방향 (상향/하향/유지)**
     - 핵심 투자 논리 1~2줄 요약
     - 리스크 요인 1줄 요약

### Phase 3: 미국 애널리스트 코멘트 및 실적 추정치 수집 (US Analyst & Earnings Revisions Retrieval)
* **Instructions:**
  1. Zacks, Seeking Alpha, Yahoo Finance, Finviz에서 미국/글로벌 애널리스트 컨센서스(Zacks Rank, 컨센서스 목표가, Buy/Hold/Sell 비율)를 수집하세요.
  2. 주요 언론 보도(CNBC, Reuters 등)에서 개별 투자은행(골드만삭스, 모건스탠리, JP모건, BofA 등)의 투자의견 및 목표가 변경 내역을 수집하세요.
  3. **12M Fwd EPS 추정치 수정(Earnings Estimate Revision)** 동향(최근 30일간 상향/하향 조정 비율)을 파악하세요.

### Phase 4: 요약표 작성 (Summary Table & Earnings Revisions)
* **Instructions:**
  1. 아래 스키마로 개별 리포트 요약표를 작성하세요.

#### 4.1 개별 리포트 요약표

| 국가 | 증권사/기관 | 애널리스트 | 발표일 | 투자의견 (변경) | 목표주가 (이전 → 현재) | 상승여력 (%) | 12M Fwd 이익 추정 | 핵심 논리 | 리스크 요인 | 출처 |
| :--- | :--- | :--- | :--- | :--- | :--- | ---: | :---: | :--- | :--- | :--- |
| 한국 | 예: 미래에셋증권 | 홍길동 | YYYY-MM-DD | 매수 (유지) | XX,XXX원 → XX,XXX원 (상향) | +XX.X% | 상향 | ... | ... | [링크] |
| 미국 | 예: Morgan Stanley | Jane Doe | YYYY-MM-DD | Overweight (↑ 상향) | $XXX → $XXX (상향) | +XX.X% | 상향 | ... | ... | [링크] |
| 미국 | 예: Zacks (컨센서스) | — | YYYY-MM-DD | Rank #2 (Buy) | 평균 $XXX (최고 $XXX / 최저 $XXX) | +XX.X% | 유지 | ... | ... | [링크] |

**작성 규칙:**
- 투자의견 변경은 `신규` / `↑ 상향` / `↓ 하향` / `유지`로 표기한다.
- 목표주가 변경은 이전 값을 확인할 수 없으면 `→ XX,XXX원 (변경 여부 미확인)`으로 적는다.
- 상승여력은 `(목표주가 / {{BASE_DATE}} 실측 현재가 − 1) × 100`으로 계산한다.
- 12M Fwd 이익 추정 변경은 `상향` / `하향` / `유지` 중 선택하여 기재한다.
- 확인하지 못한 칸은 비워 두지 말고 `미확인`으로 적는다.

#### 4.2 투자의견 표준화 기준 (한미 비교용)

| 표준 등급 | 한국 증권사 표기 | 미국 IB 표기 | Zacks Rank |
| :--- | :--- | :--- | :--- |
| **긍정 (Buy)** | 매수, Buy, Trading Buy, 적극매수 | Buy, Overweight, Outperform, Strong Buy | #1 Strong Buy, #2 Buy |
| **중립 (Hold)** | 중립, Hold, Marketperform, Not Rated | Hold, Neutral, Equal-weight, Market Perform | #3 Hold |
| **부정 (Sell)** | 매도, Sell, Underperform, Reduce | Sell, Underweight, Underperform | #4 Sell, #5 Strong Sell |

※ 한국 증권사 리포트는 '매도' 의견이 매우 드물다. 따라서 기존 '매수'에서 '중립'으로 등급을 낮추는 경우 실질적인 매도/부정 신호로 해석한다.

---

### Phase 5: 한미 비교 종합 (Cross-Market Comparison & Valuation Gap)
* **Instructions:**
  1. 국내외 투자의견 방향이 일치하는지 엇갈리는지 교차 검증하세요.
  2. 목표주가 컨센서스 대비 현재가 괴리율 및 상승여력을 한미 시장별로 비교하세요.
  3. **12M Fwd 실적 추정치 변경(Revision)의 한미 시각 차이**를 분석하세요.
  4. 공통 리스크 요인과 한국/미국 시장별 독자 리스크 요인을 구분하세요.

#### 5.1 한미 컨센서스 및 실적 추정 비교표

| 항목 | 한국 증권사 뷰 | 미국 IB / 해외 뷰 | 시각 일치 여부 |
| :--- | :--- | :--- | :--- |
| 커버 기관 수 | N개 | N개 | — |
| 의견 분포 (긍정/중립/부정) | N / N / N | N / N / N | 일치 / 엇갈림 |
| 평균 목표주가 | XX,XXX원 | $XXX | — |
| 평균 목표주가 상승여력 | +XX.X% | +XX.X% | 차이 XX.X%p |
| 이익 추정치 변경 (상향/하향/유지) | N / N / N | N / N / N | 일치 / 엇갈림 |
| 최고 / 최저 목표주가 | XX,XXX / XX,XXX원 | $XXX / $XXX | — |

※ 통화가 다를 경우 원화/달러로 각각 명시하고, **상승여력(%) 및 PER/PBR 밸류에이션**으로 격차를 비교한다.

#### 5.2 리스크 요인 구분표

| 리스크 요인 | 한국 리포트 언급 | 미국 리포트 언급 | 구분 |
| :--- | :---: | :---: | :--- |
| 예: 밸류에이션 부담 (PER/PBR) | ○ | ○ | 공통 |
| 예: 환율 및 원가율 상승 | ○ | — | 한국만 |
| 예: 반도체/AI 규제 및 관세 | — | ○ | 미국만 |

---

### Phase 6: 리포트 출력 (Report Generation)
* **Instructions:**
  1. 최종 결과를 마크다운 형식으로 작성하여 파일로 저장하세요.
  2. `.agent/rules/report_naming.md` 규칙에 따라 파일명 앞에 분석 주체 접두사를 붙이세요 (Gemini → `[G]`, Claude → `[C]`).
     - **저장 위치:** `{{OUTPUT_DIR}}[G]{{COMPANY_NAME}}({{TICKER}})_analyst_summary_{{WRITE_DATE}}.md`
  3. 문서 구조:
     - **상단 메타데이터**: 작성일자, 분석 주체(`[G]`), 대상 종목/티커, 현재가/시총 기준일
     - **1. Executive Summary (한미 애널리스트 뷰 종합 요약)**
     - **2. 개별 리포트 요약표 (Phase 4)**
     - **3. 한미 비교 종합 및 밸류에이션 분석 (Phase 5)**
     - **4. 핵심 투자 포인트 & 리스크 구분표**
     - **5. 출처 목록 (참고한 링크 전체 나열)**

---

### Phase 7: 데이터 무결성 및 정량 데이터 검증 (Review & Output)
* **Instructions:**
  1. 작성된 파일(`{{OUTPUT_DIR}}[G]{{COMPANY_NAME}}({{TICKER}})_analyst_summary_{{WRITE_DATE}}.md`)을 다시 로드하여 데이터 누락이 없는지 검증하세요.
  2. 본문 및 표에 기재된 목표주가, 현재가, 상승여력(%), PER/PBR 수치가 Phase 2에서 수집한 실측 시세 데이터와 100% 일치하는지 확인하세요.
  3. 검증 완료 후 요약 메시지와 함께 **'한미 애널리스트 뷰의 가장 큰 시각 차이 1가지'**와 **'핵심 리스크 1가지'**를 채팅창에 반환하세요.

---

## Compliance Rules
* 리포트 원문을 통째로 복사하지 않는다. 사실관계(의견/목표가/날짜)와 15단어 미만의 짧은 인용만 사용한다.
* 출처 링크는 항상 표기해 원문 확인이 가능하게 한다.
* 유료 리포트 원문에 접근할 수 없는 경우, "미확인" 또는 대체 공개 소스 사용 사실을 명시한다.
