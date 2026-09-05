---
description: 최근 1주 누적 외국인/기관 순매수·순매도 상위 종목 및 양방향 추세 분석 워크플로우
argument-hint: [TARGET_DATE=YYYY_MM_DD]
---

`.agent/workflows/weekly-institutional-flow.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- 인자가 비어 있으면 `{{TARGET_DATE}}`는 오늘 날짜(YYYY_MM_DD)를 기준으로 자동 산정하세요.
- 인자에 `TARGET_DATE=YYYY_MM_DD` 형식이 있으면 그 값을 `{{TARGET_DATE}}`로 사용하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
