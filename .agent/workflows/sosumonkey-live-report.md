---
description: 매주 일요일 밤 8시 유튜버 '소수몽키' 라이브 영상 분석 및 주간 증시 전망 리포트 생성 워크플로우 (/sosumonkey-live)
---

# 소수몽키 일요일 라이브 증시 분석 및 주간 대응 리포트 워크플로우

---

## Meta Data & Description
* **Name:** Sosumonkey Sunday Live Stream & Weekly Market Analysis Workflow
* **Version:** 1.0
* **Author:** AI Agent Collaborator
* **Description:** 매주 일요일 밤 8시에 진행되는 유튜버 '소수몽키'의 라이브 방송 내용(영상 트랜스크립트, 채널 커뮤니티, 관련 브리핑 자료)을 분석하고, 이번 주 예정된 글로벌/미국 매크로 경제 지표 및 빅테크 실적 일정과 결합하여 개인 투자자를 위한 체계적인 주간 투자 전략 리포트를 생성합니다.
* **Trigger Command:** `/sosumonkey-live`

---

## Global Context
| Variable | Description | Example / Default |
|----------|-------------|-------------------|
| `{{TARGET_DATE}}` | 분석 기준일 (일요일 라이브/공개영상 업로드 날짜, YYYY_MM_DD) | `2026_09_06` |
| `{{VIDEO_URL}}` | 소수몽키 공개 영상/재생목록 URL | `https://www.youtube.com/watch?v=qXuK203LR5Y&list=PL-QIFKCEb2mCPUP-7IP22EWODYGySjX52` |
| `{{OUTPUT_DIR}}` | 리포트 저장 디렉토리 경로 | `reports/youtube_sosumonkey/` |

---

## Workflow Phases

### Phase 1: 소수몽키 공개 영상 및 주간 이슈 데이터 수집 (Data Retrieval)
* **Instructions:**
  1. 일요일 라이브는 회원 전용이므로, 공개 버전 업로드 시리즈인 **'소몽의 해외주식투자 이야기' 재생목록 (`https://www.youtube.com/watch?v=qXuK203LR5Y&list=PL-QIFKCEb2mCPUP-7IP22EWODYGySjX52`)**, 영상 설명란, 커뮤니티 게시글 및 공개 핵심 요약 텍스트를 수집하세요.
  2. `{{TARGET_DATE}}` 주간에 발표되는 **글로벌/미국 매크로 경제 지표 일정**을 수집하세요:
     - FOMC 회의, 미 연준 의장 연설, CPI/PPI/PCE 물가지수, 고용보고서 등
     - 엔비디아, 테슬라, 애플, 마이크로소프트 등 주요 빅테크 및 주력 기업 실적 발표(Earnings) 일정
  3. 소수몽키 채널에서 주로 다루는 4대 핵심 자산군(미국 빅테크/AI, 배당성장주/ETF, 고배당/리츠, 지수 ETF)에 대한 최근 시장 분위기를 정리하세요.

### Phase 2: 라이브 핵심 인사이트 및 투자 뷰 추출 (Insight Extraction)
* **Instructions:**
  1. **소수몽키의 주간 시장 뷰(Stance) 파악:** 이번 주 시장을 바라보는 톤앤매너(우호적/중립/경계) 및 핵심 주제(예: "실적발표 주간 대응법", "금리인하 수혜주 점검" 등)를 도출하세요.
  2. **핵심 분석 내용 카테고리화:**
     - **빅테크 & AI 섹터:** 테슬라, 엔비디아, 빅테크 7(M7) 관련 최신 이슈 및 기술적/기본적 분석 포인트
     - **배당성장 및 고배당주:** SCHD, JEPI, 주요 리츠/금융주 등 배당 투자 관련 소수몽키의 언급 및 전략
     - **지수 & ETF 흐름:** S&P500(VOO/IVV), 나스닥100(QQQ), 중소형주(IWM) 흐름 분석
     - **라이브 Q&A 및 시청자 관심 이슈:** 라이브/공개 영상 중 시청자들이 가장 많이 질문하거나 강조된 종목/리스크 요인

### Phase 3: 주간 종합 투자 전망 리포트 작성 (Report Generation)
* **Instructions:**
  1. 수집 및 분석한 내용을 바탕으로 마크다운 형식의 보고서를 작성하세요.
  2. `.agent/rules/report_naming.md` 규칙에 따라 파일명 앞에 분석 주체 접두사(`[C]`)를 붙여 저장하세요.
     - **저장 위치:** `{{OUTPUT_DIR}}[C]sosumonkey_live_report_{{TARGET_DATE}}.md`
  3. 리포트는 다음 구조를 엄격히 준수해야 합니다:
     - **상단 메타데이터**: 작성일자, 분석 주체(`[C]`), **원본 출처 재생목록/영상 URL (`https://www.youtube.com/watch?v=qXuK203LR5Y&list=PL-QIFKCEb2mCPUP-7IP22EWODYGySjX52`)** 포함

     - **1. Executive Summary (소수몽키의 한 줄 뷰 & 주간 핵심 요약 3가지)**
     - **2. 이번 주 마켓 캘린더 & 매크로 빅이벤트 (지표 발표 및 기업 실적 일정표)**
     - **3. 소수몽키 라이브 핵심 브리핑 (섹터/테마별 상세 분석)**
       - 3.1 미국 빅테크 & AI 반도체 동향
       - 3.2 배당성장주 및 지수 ETF(SCHD, QQQ 등) 대응 전략
       - 3.3 라이브 핫 이슈 & Q&A 주요 종목 분석
     - **4. 주간 포커스 종목 & 관전 포인트 (소수몽키 픽 및 밸류체인 체크)**
     - **5. 개인 투자자를 위한 주간 실전 행동 가이드 (매수/매도/관망 가이드라인)**


### Phase 4: 데이터 검증 및 완료 브리핑 (Review & Output)
* **Instructions:**
  1. 생성된 파일(`{{OUTPUT_DIR}}[C]sosumonkey_live_report_{{TARGET_DATE}}.md`)이 정상적으로 작성되었는지 확인하세요.
  2. 리포트 생성이 완료되면, 사용자에게 **"이번 주 소수몽키 라이브의 핵심 메시지 1가지"**와 **"이번 주 반드시 챙겨봐야 할 마크 지표/실적 일정"**을 3~4줄로 요약하여 출력하고 저장된 파일 링크를 제공하세요.
