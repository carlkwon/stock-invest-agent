---
description: 워런 버핏, 스탠리 드라켄밀러, 조지 소로스 등 글로벌 투자 대가(Guru) 및 연기금, 재단, 벤처캐피털(VC) 등 주요 대형 기관의 최신 13F Filing 데이터를 파싱 및 데이터베이스화하여 포트폴리오 내 종목별 비중 변화(신규 매수, 전량 매도, 증감) 및 섹터별 쏠림 현상을 다각도로 분석하는 워크플로우입니다.
---

# Title: 13F 공시 기반 구루(Guru) 포트폴리오 및 매매 동향 분석 워크플로우

Description: 워런 버핏, 스탠리 드라켄밀러, 조지 소로스 등 글로벌 투자 대가(Guru) 및 연기금, 재단, 벤처캐피털(VC) 등 주요 대형 기관의 최신 13F Filing 데이터를 파싱 및 데이터베이스화하여 포트폴리오 내 종목별 비중 변화(신규 매수, 전량 매도, 증감) 및 섹터별 쏠림 현상을 다각도로 분석하는 워크플로우입니다.

---

## Global Context
| Variable | Description | Example / Logic |
|----------|-------------|-----------------|
| `{{TARGET_QUARTER}}` | 분석 대상 공시 분기 | 현재 시점 기준 가장 최신 공시 분기 (예: `2026 Q1` 또는 `2026 Q2`) |
| `{{TARGET_INVESTORS}}` | 분석 대상 기관/대가 목록 | `Berkshire Hathaway`, `Fisher Asset Management`, `Duquesne Family Office`, `Bill & Melinda Gates Foundation`, `NPS`, `Soros Fund`, `Founders Fund` 등 |
| `{{OUTPUT_PATH}}` | 리포트 및 결과 저장 경로 | `reports/13f/13f_analysis_{{TARGET_QUARTER_CODE}}.md` |

---

## Target Guru Portfolio Recommendations (추천 분석 대상 기관)

1. **가치투자 & 롱런형 대가 / 자산운용사**
   - **Berkshire Hathaway (CIK: 0001067983)** - 워런 버핏 (Warren Buffett)
   - **Fisher Asset Management (CIK: 0000850529)** - 켄 피셔 (Ken Fisher)
   - **Daily Journal Corp / Himalaya Capital (CIK: 0001483017)** - 리 루 (Li Lu)
   - **Pershing Square Capital Management (CIK: 0001336528)** - 빌 애크먼 (Bill Ackman)

2. **헤지펀드 & 글로벌 매크로 대가**
   - **Duquesne Family Office (CIK: 0001536411)** - 스탠리 드라켄밀러 (Stanley Druckenmiller)
   - **Soros Fund Management (CIK: 0001029160)** - 조지 소로스 / 소로스 펀드 (George Soros)
   - **Scion Asset Management (CIK: 0001649339)** - 마이클 버리 (Michael Burry)
   - **Appaloosa Management (CIK: 0001009258)** - 데이비드 테퍼 (David Tepper)

3. **연기금, 비영리 재단 & 벤처캐피털(VC)**
   - **National Pension Service of Korea / NPS (CIK: 0001600813)** - 대한민국 국민연금공단
   - **Bill & Melinda Gates Foundation Trust (CIK: 0001166559 / 0001262039)** - 빌 & 멜린다 게이츠 재단
   - **Founders Fund (CIK: 0001416950)** - 피터 틸 / 파운더스 펀드 (Peter Thiel)

4. **테크 & 테마/성장주 대가**
   - **ARK Investment Management (CIK: 0001697748)** - 캐시 우드 (Cathie Wood)
   - **Coatue Management (CIK: 0001166559)** - 필립 라퐁트 (Philippe Laffont)

---

## Workflow Phases

### Phase 1: 분석 대상 선정 및 13F 데이터 수집 (Data Retrieval)
* **Instructions:**
  1. 분석 대상 기관(`{{TARGET_INVESTORS}}`)의 CIK(Central Index Key) 코드 및 대상 분기(`{{TARGET_QUARTER}}`)를 확정하세요.
  2. SEC EDGAR API (`https://data.sec.gov/submissions/CIK...`) 또는 13F 데이터 파이프라인 스크립트를 구동하여 해당 기관의 최신 **13F-HR / 13F-HR/A** XML/텍스트 데이터를 수집하세요.
  3. 직전 분기(`T-1`) 데이터와 현재 분기(`T`) 데이터를 모두 확보하여 매매 내역 비교의 기반을 마련하세요.
  4. 데이터의 완결성을 검증하세요. (총 포트폴리오 금액, 종목 수, 풋/콜 옵션 포지션 포함 여부 체크)

### Phase 2: 포트폴리오 변화 추출 및 통계 분석 (Data Processing & Analysis)
* **Instructions:**
  1. 수집된 CUSIP 코드 및 발행사명을 티커(Ticker)로 매핑하고 보유 주식 수 및 평가액($)을 가공하세요.
  2. 직전 분기 대비 매매 동향을 다음 4가지 유형으로 분류하세요:
     - **신규 편입 종목 (New Positions):** 직전 분기 미보유 -> 당기 신규 진입
     - **전량 매도 종목 (Sold Out):** 직전 분기 보유 -> 당기 미보유 (0주)
     - **지분 추가 (Increased / Addition):** 직전 분기 대비 보유 주식 수 증가 (특히 비중 5% 이상 증감 종목 표기)
     - **지분 축소 (Decreased / Reduction):** 직전 분기 대비 보유 주식 수 감소
  3. **집중도 및 섹터 분석:**
     - 상위 10개 보유 종목(Top 10 Holdings)의 포트폴리오 내 비중(%) 및 집중도(CR10) 계산
     - GICS 섹터별 비중 변화(예: 기술주, 금융주, 에너지 등) 계산
  4. **풋/콜 옵션 및 특수 포지션 분리:** 풋/콜 옵션 포지션은 일반 주식 포지션과 분리하여 헤징 의도를 파악하세요.

### Phase 3: 리포트 시각화 및 초안 작성 (Report Generation)
* **Instructions:**
  1. 분석 결과를 바탕으로 가독성이 높고 구조화된 마크다운 리포트를 작성하세요.
  2. 리포트는 다음 필수 구조를 포함해야 합니다:
     - **Executive Summary:** 당기 13F 공시 핵심 요약 (포트폴리오 총액 변화, 주요 신규/매도 종목 3선, 대표 섹터 쏠림 현상)
     - **Top 10 Holdings:** 상위 10개 종목 순위, 평가액, 포트폴리오 비중, 직전 분기 대비 주식 수 변동률
     - **주요 매매 동향 상세:** 신규 매수, 전량 매도, 주요 증감 종목 표(Table) 제공
     - **섹터별 자산 배분 현황:** 직전 분기 vs 현재 분기 섹터 비중 비교
     - **주요 투자 시사점:** 기관의 매크로/산업별 시각 추정 및 공시 시차(최대 45일)에 따른 주의점
  3. 상위 10개 보유 종목 및 섹터 비중은 시각화(SVG, Mermaid 차트, 또는 마크다운 표/프로그레스바 형태)로 렌더링하세요.

### Phase 4: 최종 검증 및 저장 (Review & Artifact Output)
* **Instructions:**
  1. 추출된 수치(평가액, 주식 수, 비중 합계 100% 여부)가 원본 SEC 13F 파일과 일치하는지 최종 검증하세요.
  2. 마크다운 포맷팅 및 가독성(표 alignment, 하이라이트 등)을 정돈하세요.
  3. 완료된 분석 리포트를 `{{OUTPUT_PATH}}` 위치에 파일로 저장하고 사용자에게 완료 메시지 및 파일 경로를 제시하세요.