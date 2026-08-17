---
description: 
---

# KOSPI & KOSDAQ Market Capitalization & Liquidity Flow Analysis

> **분석 기준일:** {{ANALYSIS_DATE}} (비교 주기: {{ANALYSIS_PERIOD}})  
> **리포트 생성 일시:** {{GENERATED_AT}}  
> **분석 대상 시장:** {{MARKET_SCOPE}} (KOSPI / KOSDAQ)

---

## 1. Executive Summary

- **Total Market Capitalization Changes (시장 전체 시가총액 변동):**
  - **KOSPI:** {{KOSPI_TOTAL_MCAP}} (`{{KOSPI_MCAP_CHANGE_PCT}}%` vs. 직전 주기)
  - **KOSDAQ:** {{KOSDAQ_TOTAL_MCAP}} (`{{KOSDAQ_MCAP_CHANGE_PCT}}%` vs. 직전 주기)
- **Net Buying by Investor Class (수급 주체별 합산 순매수 동향):**
  - **Foreign Investors (외국인):** `{{FOREIGN_NET_BUY_TOTAL}}`
  - **Institutional Investors (기관):** `{{INSTITUTION_NET_BUY_TOTAL}}` (Pension Funds / 연기금: `{{PENSION_NET_BUY_TOTAL}}`)
  - **Retail Investors (개인):** `{{RETAIL_NET_BUY_TOTAL}}`
- **Key Capital Flow Takeaways (주요 자금 이동 핵심 요약):**
  > {{EXECUTIVE_SUMMARY_TEXT}}
  > *(예시: 반도체 및 이차전지 대형주로 외국인 수급이 집중되며 KOSPI 시총 상승을 견인한 반면, KOSDAQ 바이오 섹터에서는 차익 실현 물량이 출회됨)*

---

## 2. Sector & Market Cap Overview

### 2.1 Top 3 Outperforming & Underperforming Sectors (상승/하락 섹터 Top 3)

| Category (구분) | Sector Name (섹터명) | Total Market Cap (시가총액) | Market Share (점유율 %) | Share Change (점유율 변동 %p) | Key Buyer / Seller (주요 수급 주체) |
|:---|:---|:---:|:---:|:---:|:---:|
| **Top Outperformer 1** | {{TOP_SECTOR_1_NAME}} | {{TOP_SECTOR_1_MCAP}} | {{TOP_SECTOR_1_SHARE}}% | `+{{TOP_SECTOR_1_DIFF}}%p` | {{TOP_SECTOR_1_BUYER}} |
| **Top Outperformer 2** | {{TOP_SECTOR_2_NAME}} | {{TOP_SECTOR_2_MCAP}} | {{TOP_SECTOR_2_SHARE}}% | `+{{TOP_SECTOR_2_DIFF}}%p` | {{TOP_SECTOR_2_BUYER}} |
| **Top Outperformer 3** | {{TOP_SECTOR_3_NAME}} | {{TOP_SECTOR_3_MCAP}} | {{TOP_SECTOR_3_SHARE}}% | `+{{TOP_SECTOR_3_DIFF}}%p` | {{TOP_SECTOR_3_BUYER}} |
| **Top Underperformer 1** | {{BOT_SECTOR_1_NAME}} | {{BOT_SECTOR_1_MCAP}} | {{BOT_SECTOR_1_SHARE}}% | `-{{BOT_SECTOR_1_DIFF}}%p` | {{BOT_SECTOR_1_SELLER}} |
| **Top Underperformer 2** | {{BOT_SECTOR_2_NAME}} | {{BOT_SECTOR_2_MCAP}} | {{BOT_SECTOR_2_SHARE}}% | `-{{BOT_SECTOR_2_DIFF}}%p` | {{BOT_SECTOR_2_SELLER}} |

---

## 3. Top 20 Market Cap Dynamics & Megacap Shift (시총 Top 20 대형주 동향)

### 3.1 Notable Market Cap Gainers & Losers in Top 20 (Top 20 주요 시총 변동 종목)

| Rank Change (순위 변동) | Ticker / Company (종목명 / 티커) | Market (시장) | Current Market Cap (현재 시총) | Period Cap Change (시총 변동률 %) | Foreign Net Buy (외인 순매수) | Inst. Net Buy (기관 순매수) | Key Catalyst / Remarks (주요 변동 사유 및 비고) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **1 (`0`)** | **{{TOP20_STOCK_1_NAME}}** (`{{TOP20_STOCK_1_TICKER}}`) | {{MKT_1}} | {{MCAP_1}} | `+{{CHANGE_1}}%` | {{FOR_1}} | {{INST_1}} | {{NOTE_1}} |
| **2 (`+1`)** | **{{TOP20_STOCK_2_NAME}}** (`{{TOP20_STOCK_2_TICKER}}`) | {{MKT_2}} | {{MCAP_2}} | `+{{CHANGE_2}}%` | {{FOR_2}} | {{INST_2}} | {{NOTE_2}} |
| **3 (`-1`)** | **{{TOP20_STOCK_3_NAME}}** (`{{TOP20_STOCK_3_TICKER}}`) | {{MKT_3}} | {{MCAP_3}} | `-{{CHANGE_3}}%` | {{FOR_3}} | {{INST_3}} | {{NOTE_3}} |
| ... | ... | ... | ... | ... | ... | ... | ... |
| **20 (`+3`)** | **{{TOP20_STOCK_20_NAME}}** (`{{TOP20_STOCK_20_TICKER}}`) | {{MKT_20}} | {{MCAP_20}} | `+{{CHANGE_20}}%` | {{FOR_20}} | {{INST_20}} | {{NOTE_20}} |

### 3.2 Megacap Rank Flipping & Top 10 Entry/Exit Signals (대형주 순위 역전 및 Top 10 진출입 시그널)

- **[시그널 1] Top 10 신규 진입 종목:**
  - **종목명:** {{ENTRY_STOCK_NAME}} (`{{ENTRY_STOCK_TICKER}}`)
  - **순위 변동:** {{OLD_RANK}}위 → **{{NEW_RANK}}위** (시가총액 증가율: `+{{ENTRY_MCAP_PCT}}%`)
  - **원인 및 분석:** {{ENTRY_ANALYSIS}}
- **[시그널 2] 섹터 내 대장주 순위 역전:**
  - **세부 내용:** {{FLIP_STOCK_A}} (시총: {{FLIP_MCAP_A}})이/가 {{FLIP_STOCK_B}} (시총: {{FLIP_MCAP_B}})을/를 제치고 섹터 내 **{{NEW_RANK_A}}위**로 상승.
  - **주요 상승 동인:** {{FLIP_DRIVER_TEXT}}

---

## 4. Smart Money Flow & Market Cap Ranking Shifts (스마트머니 유입 및 시총 확대 종목)

### 4.1 Top Net Buy Holdings & Market Cap Weight Gainers (순매수 상위 및 시총 비중 확대 종목)

| Ticker / Company (종목명 / 티커) | Market (시장) | Current Market Cap (현재 시총) | Rank Change (순위 변동) | Cap Change (시총 변동률 %) | Foreign Net Buy (외인 순매수) | Inst. Net Buy (기관 순매수) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **{{INFLOW_STOCK_1_NAME}}** (`{{INFLOW_STOCK_1_TICKER}}`) | {{MARKET_1}} | {{MCAP_1}} | {{RANK_1}} (`+{{RANK_DIFF_1}}`) | `+{{MCAP_CHANGE_1}}%` | {{FOREIGN_1}} | {{INST_1}} |
| **{{INFLOW_STOCK_2_NAME}}** (`{{INFLOW_STOCK_2_TICKER}}`) | {{MARKET_2}} | {{MCAP_2}} | {{RANK_2}} (`+{{RANK_DIFF_2}}`) | `+{{MCAP_CHANGE_2}}%` | {{FOREIGN_2}} | {{INST_2}} |
| **{{INFLOW_STOCK_3_NAME}}** (`{{INFLOW_STOCK_3_TICKER}}`) | {{MARKET_3}} | {{MCAP_3}} | {{RANK_3}} (`+{{RANK_DIFF_3}}`) | `+{{MCAP_CHANGE_3}}%` | {{FOREIGN_3}} | {{INST_3}} |

---

## 5. Key Investment Ideas & Actionable Strategies (전략별 투자 아이디어)

### Strategy 1: Market Leaders Long Strategy (주도주 롱 전략: 섹터 비중 확대 + 수급 집중)

> **투자 아이디어 논리 (Investment Thesis):**  
> 시장 전체 대비 시가총액 비중이 지속적으로 확대되고 외국인 및 기관의 동반 순매수가 집중되는 섹터 대표 주도주 모멘텀 추종.

* **관찰 대상 종목 (Watchlist):**
  1. **{{LONG_STOCK_1_NAME}} (`{{LONG_STOCK_1_TICKER}}`)**
     - **투자 논리:** {{LONG_STOCK_1_THESIS}}
     - **수급 및 시총 시그널:** 외인/기관 연속 순매수 `{{LONG_STOCK_1_DAYS}}일` 지속, 시가총액 변동률 `+{{LONG_STOCK_1_MCAP_PCT}}%`
     - **핵심 체크리스트:** {{LONG_STOCK_1_CHECK}}
  2. **{{LONG_STOCK_2_NAME}} (`{{LONG_STOCK_2_TICKER}}`)**
     - **투자 논리:** {{LONG_STOCK_2_THESIS}}

---

### Strategy 2: Value Chain Catch-up Strategy (밸류체인 갭 메우기 / 대장주 추종 전략)

> **투자 아이디어 논리 (Investment Thesis):**  
> 섹터 내 1위 대장주의 시총이 선제적으로 급증한 후, 아직 시총에 반영되지 않은 2~3위 부품/장비/소재 밸류체인 기업의 갭 메우기(Catch-up) 반등 공략.

* **관찰 대상 종목 (Watchlist):**
  1. **{{CATCHUP_STOCK_1_NAME}} (`{{CATCHUP_STOCK_1_TICKER}}`)**
     - **섹터 대장주:** {{CATCHUP_LEADER_1}} (최근 시총 변동률: `+{{LEADER_MCAP_PCT_1}}%`)
     - **투자 논리:** {{CATCHUP_STOCK_1_THESIS}}
     - **상승 여력 분석:** 대장주 대비 시총 변동 갭 `{{GAP_PCT_1}}%` 존재

---

### Strategy 3: Oversold Rebound / Short-Covering Strategy (과매도 반등 / 숏커버링 전략)

> **투자 아이디어 논리 (Investment Thesis):**  
> 고점 대비 시총이 과도하게 하락했으나 외국인·기관의 매도세가 둔화되고 바닥권 거래 회전율이 돌아서는 주가/수급 바닥권 종목 포착.

* **관찰 대상 종목 (Watchlist):**
  1. **{{REBOUND_STOCK_1_NAME}} (`{{REBOUND_STOCK_1_TICKER}}`)**
     - **투자 논리:** {{REBOUND_STOCK_1_THESIS}}
     - **바닥 시그널:** 고점 대비 시총 하락률 `-{{REBOUND_DROP_PCT_1}}%` 기록 후 최근 3거래일 연속 외국인 순매수 전환.

---

## 6. Risk Factors & Monitoring Checklist (리스크 요인 및 감시 항목)

1. **Overcrowding & Overheating Risk (수급 쏠림 및 과열 리스크):**
   - `{{OVERHEAT_STOCK_1}}`: 시총 대비 거래대금 회전율이 `{{TURNOVER_RATE_1}}%`로 단기 과열 구간 진입. 단기 변동성 확대 주의.
2. **Upcoming Catalysts & Events Checklist (주요 일정 및 이벤트 체크리스트):**
   - `{{CHECK_DATE_1}}`: {{CHECK_EVENT_1}} (예: 보호예수 해제, 전환사채 물량 상장 등)
   - `{{CHECK_DATE_2}}`: {{CHECK_EVENT_2}} (예: 분기 실적 발표일)
3. **Disclosure Lag & Statistical Distortions (공시 시차 및 착시 주의):**
   - 자사주 소각, 유상증자, 주식분할 등 기업 이벤트로 인한 단순 시총 변화 건과 순수 주가 변동에 의한 시총 변화를 구별하여 모니터링할 것.

---

## 7. Appendix: Data Source & Methodology (데이터 출처 및 산출 공식)

- **Data Sources (데이터 출처):** KRX 정보데이터시스템 Open API, Open DART
- **Key Formulas (핵심 산출식):**
  - `Sector Market Share (%) = (섹터 총 시가총액 / 시장 전체 시가총액) * 100`
  - `Smart Money Ratio (%) = (외국인+기관 순매수 대금 / 해당 종목 시가총액) * 100`
- **Output Directory (결과 저장 경로):** `{{OUTPUT_PATH}}`