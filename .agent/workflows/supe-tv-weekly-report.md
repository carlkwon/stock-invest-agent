---
description: 매주 유튜버 '슈페TV' 미국 증시 분석 영상 및 월가 리포트 요약 워크플로우 (/supe-tv)
---

# 슈페TV 미국 증시 분석 및 월가 리포트 요약 워크플로우

---

## Meta Data & Description
* **Name:** Supe TV Weekly US Stock Report & Wall Street Analysis Workflow
* **Version:** 1.0
* **Author:** AI Agent Collaborator
* **Description:** 매주 유튜버 '슈페TV'가 업로드하는 미국 증시 분석 및 월가(Wall Street) 주요 IB 보고서 요약 영상을 분석하고, 최신 미국 시장 매크로 데이터 및 빅테크/ETF 동향과 결합하여 개인 투자자를 위한 주간 미국 주식 투자 보고서를 생성합니다.
* **Trigger Command:** `/supe-tv`

---

## Global Context
| Variable | Description | Example / Default |
|----------|-------------|-------------------|
| `{{TARGET_DATE}}` | 분석 기준일 (주간 공개영상 업로드 날짜, YYYY_MM_DD) | `2026_09_06` |
| `{{VIDEO_URL}}` | 슈페TV 공개 동영상 목록/영상 URL | `https://www.youtube.com/@supe-tv/videos` |
| `{{OUTPUT_DIR}}` | 리포트 저장 디렉토리 경로 | `reports/youtube_supe/` |

---

## Workflow Phases

### Phase 1: 슈페TV 공개 영상 및 월가 리포트 데이터 수집 (Data Retrieval)
* **Instructions:**
  1. `/browser` 또는 웹 검색을 활용하여 **슈페TV 공개 동영상 시리즈 (`https://www.youtube.com/@supe-tv/videos`)**의 최신 미국 증시/월가 리포트 분석 영상, 영상 설명란, 주요 자막/타임스탬프 및 커뮤니티 게시글 수집.
  2. 슈페TV 공개 영상에서 다루는 **월가 주요 투자은행(골드만삭스, 모건스탠리, JP모건 등)의 리포트 핵심 뷰 및 목표주가 조정 내역**을 정리하세요.
  3. `{{TARGET_DATE}}` 주간의 미국 S&P500, 나스닥 100 지수 흐름, 주요 ETF(SCHD, QQQ, VOO, JEPI 등) 수급 및 매크로 지표(금리, CPI, 실적)를 수집하세요.

### Phase 2: 월가 리포트 및 슈페TV 핵심 인사이트 추출 (Insight Extraction)
* **Instructions:**
  1. **월가 IB 리포트 핵심 요약:** 슈페TV가 강조한 글로벌 투자은행들의 미 증시 투자의견(Overweight/Neutral/Underweight)과 이익 추정치 변동 사항 도출.
  2. **섹터 & ETF 투자 포인트 분석:**
     - **미국 빅테크 & 성장주:** 엔비디아, 테슬라, 애플, 마이크로소프트 등 주요 테크 기업에 대한 슈페TV의 밸류에이션 및 수급 시그널.
     - **배당주 & ETF:** SCHD, JEPI, O(알파벳/리츠) 등 배당성장 및 고배당 ETF의 분배금/배당수익률 및 투자 타이밍 가이드.
     - **지수 ETF 및 현금 비중:** VOO/QQQ 등 대표 지수 추종 ETF 대응법 및 적정 현금 비중 제언.
  3. **슈페TV 특유의 시각화 데이터 정리:** 영상에서 강조된 주요 차트, 히트맵(Heatmap), 주주 환원(자사주 매입/배당) 데이터 포인트 정리.

### Phase 3: 주간 미국 주식 분석 리포트 작성 (Report Generation)
* **Instructions:**
  1. 수집 및 분석한 내용을 바탕으로 마크다운 형식의 보고서를 작성하세요.
  2. `.agent/rules/report_naming.md` 규칙에 따라 파일명 앞에 분석 주체 접두사(`[C]`)를 붙여 저장하세요.
     - **저장 위치:** `{{OUTPUT_DIR}}[C]supe_tv_report_{{TARGET_DATE}}.md`
  3. 리포트는 다음 구조를 엄격히 준수해야 합니다:
     - **상단 메타데이터**: 작성일자, 분석 주체(`[C]`), **원본 출처 공개 동영상 URL (`https://www.youtube.com/@supe-tv/videos` 또는 특정 영상 URL)** 포함

     - **1. Executive Summary (슈페TV 주간 브리핑 핵심 요약 3가지 & 월가 스탠스)**
     - **2. 월가(Wall Street) 주요 보고서 & 매크로 핵심 정리** (IB별 목표가/투자의견 및 매크로 지표)
     - **3. 슈페TV 섹터 & ETF 심층 분석**
       - 3.1 빅테크 & AI 반도체 동향 및 밸류에이션
       - 3.2 배당성장주 & 지수 ETF(SCHD, QQQ, VOO) 매수/매도 타이밍 점검
       - 3.3 주간 히트맵 및 자금 유출입 핵심 차트 분석
     - **4. 주간 포커스 종목 & 관전 포인트** (월가 리포트 수혜주 및 관심 종목 밸류체인)
     - **5. 개인 투자자를 위한 주간 미국 주식 실전 대응 가이드** (적정 포트폴리오 비중 및 대응 전략)


### Phase 4: 데이터 검증 및 완료 브리핑 (Review & Output)
* **Instructions:**
  1. 생성된 파일(`{{OUTPUT_DIR}}[C]supe_tv_report_{{TARGET_DATE}}.md`)이 정상적으로 작성되었는지 최종 검토하세요.
  2. 리포트 생성이 완료되면, 사용자에게 **"이번 주 슈페TV 리포트의 핵심 메시지 1가지"**와 **"월가가 바라보는 핵심 미국 종목/ETF 관전 포인트"**를 요약하여 출력하고 저장된 파일 링크를 제공하세요.
