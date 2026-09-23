---
description: 한미 애널리스트 리포트 정리·요약 워크플로우 (투자의견·목표주가·리스크 비교표)
argument-hint: TICKER=NVDA [PEER_TICKER=AMD] [PERIOD=최근 4주]
---

`.agent/workflows/analyst-report.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- `{{TICKER}}`는 필수입니다. 인자에 종목(티커 또는 종목명/종목코드)이 없으면 어떤 종목을 분석할지 사용자에게 먼저 확인하세요(예: NVDA, 005930, 삼성전자).
  - `TICKER=` 없이 `NVDA`처럼 종목만 전달된 경우에도 그 값을 `{{TICKER}}`로 사용하세요.
- `{{PEER_TICKER}}`는 선택입니다. 인자에 없으면 비교 종목 없이 진행하세요.
- `{{PERIOD}}`가 인자에 없으면 `최근 4주`로 설정하세요.
- `{{BASE_DATE}}`는 실행일 직전 거래일, `{{WRITE_DATE}}`는 실제 작성일(YYYYMMDD)로 자동 설정하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
