---
description: 한미 애널리스트 리포트 정리·요약 워크플로우 (/analyst-report)
---

# 한미 애널리스트 리포트 정리·요약 워크플로우

---

## Meta Data & Description
* **Name:** Korea-US Analyst Report Summary Workflow (Cumulative)
* **Version:** 2.0
* **Author:** AI Agent Collaborator
* **Description:** 특정 종목(또는 섹터)에 대해 한국 증권사 리포트와 미국 애널리스트 코멘트/IB 뷰를 수집하여, 투자의견·목표주가·실적 추정치 변경(Revision)·핵심 논리·리스크를 한눈에 비교 분석하는 심층 보고서를 생성합니다. **기업별·연도별 단일 누적 파일(`[G]{{COMPANY_NAME}}({{TICKER}})_analyst_summary_{{YYYY}}.md`)에 신규 분석 회차를 최신 순(상단 누적)으로 이어서 기록하여, 시계열적 목표주가/투자의견 추이 및 한미 IB 시각 변화를 영구 추적합니다.**
* **Trigger Command:** `/analyst-report`

---

## Global Context
| Variable | Description | Example / Default |
|----------|-------------|-------------------|
| `{{TICKER}}` | 분석 대상 종목 티커 (한국 종목은 종목코드) | `NVDA`, `005930` |
| `{{COMPANY_NAME}}` | 파일명에 쓰는 기업명. 한글 통용명을 공백 없이 쓴다 (한국 종목은 거래소 공식 종목명) | `삼성전자`, `SK하이닉스`, `엔비디아`, `스페이스X` |
| `{{PEER_TICKER}}` | (선택) 비교할 동일 섹터 대응 종목 | `AMD` |
| `{{PERIOD}}` | 리포트 수집 기간 | `최근 4주` |
| `{{BASE_DATE}}` | 현재가·상승여력 계산 기준일 (YYYY-MM-DD) | 실행일 직전 거래일 |
| `{{WRITE_DATE}}` | 실제 작성일 (YYYYMMDD) | `20261011` |
| `{{OUTPUT_DIR}}` | 리포트 저장 디렉토리 경로 (없으면 생성) | `reports/analyst/` |
| `{{REPORT_PATH}}` | **기업별 단일 누적 파일 경로** (모델별 접두사 `[G]` 또는 `[C]` 적용). 날짜별 개별 파일이 아닌 기업별 연간 파일에 최신 순으로 누적 갱신(`{{YYYY}}` = 작성 연도, 해가 바뀌면 새 파일) | `{{OUTPUT_DIR}}[G]{{COMPANY_NAME}}({{TICKER}})_analyst_summary_{{YYYY}}.md` |

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

### Phase 1: 대상 확정 및 기존 파일 확인 (Target Definition & History Check)
* **Instructions:**
  1. `{{TICKER}}`, `{{COMPANY_NAME}}`, `{{PERIOD}}`(예: 최근 4주)를 확정하세요.
  2. 필요 시 동일 섹터의 미국/국내 대응 종목(`{{PEER_TICKER}}`)을 함께 지정하세요.
  3. **[누적 관리 점검]:** `{{REPORT_PATH}}`(`reports/analyst/[접두사]{{COMPANY_NAME}}({{TICKER}})_analyst_summary_{{YYYY}}.md`) 파일이 이미 존재하는지 확인하세요. 해당 연도 파일이 없으면 전년도 파일(`..._{{YYYY-1}}.md`)의 최신 회차를 Revision 비교 기준으로 쓰세요.
     - 파일이 존재하면 기존 회차의 직전 분석일자, 당시 목표가, 투자의견을 확인하여 이번 회차의 **시계열적 변동(Revision Tracking)**에 반영할 준비를 하세요.

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

### Phase 6: 리포트 출력 및 누적 갱신 (Cumulative Report Generation & Prepending)
* **Instructions:**
  1. 최종 결과를 마크다운 형식으로 작성하여 **기업별 단일 누적 파일**로 저장하세요.
  2. `.agent/rules/report_naming.md` 규칙에 따라 파일명 앞에 분석 주체 접두사를 붙이세요 (Gemini → `[G]`, Claude → `[C]`).
     - **저장 위치:** `{{OUTPUT_DIR}}[G]{{COMPANY_NAME}}({{TICKER}})_analyst_summary_{{YYYY}}.md` (해당 연도 파일이 있으면 그 파일에 누적, 없으면 새로 생성)
  3. **누적 리포트 구조 (최신 순 - Latest First 정렬 원칙):**
     - **상단 고정 영역**:
       - 문서 대제목: `# [G] {{COMPANY_NAME}}({{TICKER}}) 한미 애널리스트 리포트 종합 분석 (누적)`
       - **★ 회차별 히스토리 요약표 (Timeline Index)**:
         ```markdown
         | 분석 일자 | 기준일 종가 | 한국 평균 목표가 | 미국 평균 목표가 | 글로벌 종합 의견 | 핵심 이벤트 및 Revision 포인트 |
         | :--- | :---: | :---: | :---: | :---: | :--- |
         | YYYY-MM-DD | ... | ... | ... | 매수 | ... (신규 분석 시 항상 이 표의 맨 윗줄에 추가) |
         ```
     - **본문 회차별 분석 영역 (최신 회차가 항상 맨 위로 삽입 - Prepending)**:
       - 신규 분석 시 **최상단 히스토리 요약표 바로 아래이자 기존 과거 회차 본문들보다 위**에 새로운 회차를 삽입합니다:
         ```markdown
         ---
         
         # 📅 [{{WRITE_DATE}} 분석] {{COMPANY_NAME}}({{TICKER}}) 한미 애널리스트 리포트
         
         > **작성일자:** YYYY년 MM월 DD일  
         > **시세 기준일:** YYYY-MM-DD 종가 기준 (현재가: $XXX / XX,XXX원)  
         > **시가총액:** $X.XX조 | **밸류에이션:** 12M Fwd P/E ...
         
         ## 1. Executive Summary (한미 애널리스트 뷰 종합 요약)
         ## 2. 개별 리포트 요약표 (Phase 4)
         ## 3. 한미 비교 종합 및 밸류에이션 분석 (Phase 5)
         ## 4. 핵심 투자 포인트 & 리스크 구분표
         ## 5. 출처 목록 (참고한 링크 전체)
         ```
       - 기존에 작성되어 있던 과거 분석 회차들은 그 아래에 그대로 보존되어, **파일을 열었을 때 항상 가장 최신 회차가 상단에 위치하고 아래로 스크롤할수록 과거 히스토리가 이어지도록 구성**합니다.

---

### Phase 7: 데이터 무결성 및 정량 데이터 검증 (Review & Output)
* **Instructions:**
  1. 갱신된 파일(`{{REPORT_PATH}}`)을 다시 로드하여 최신 회차가 정상적으로 최상단에 누적되었는지, 과거 회차가 온전히 보존되었는지 검증하세요.
  2. 본문 및 표에 기재된 목표주가, 현재가, 상승여력(%), PER/PBR 수치가 실측 시세 데이터와 100% 일치하는지 확인하세요.
  3. 검증 완료 후 요약 메시지와 함께 **'한미 애널리스트 뷰의 가장 큰 시각 차이 1가지'**, **'핵심 리스크 1가지'**, 그리고 누적 갱신된 파일 링크를 채팅창에 반환하세요.

---

## Compliance Rules
* 리포트 원문을 통째로 복사하지 않는다. 사실관계(의견/목표가/날짜)와 15단어 미만의 짧은 인용만 사용한다.
* 출처 링크는 항상 표기해 원문 확인이 가능하게 한다.
* 유료 리포트 원문에 접근할 수 없는 경우, "미확인" 또는 대체 공개 소스 사용 사실을 명시한다.
