---
description: 장중 실시간 수급 동향 및 주도 섹터 분석 워크플로우
argument-hint: [CHECK_TIME=HH_MM]
---

`.agent/workflows/intraday-supply-demand.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- `{{TARGET_DATE}}`는 항상 오늘 날짜(YYYY_MM_DD)로 자동 설정하세요.
- 인자에 `CHECK_TIME=HH_MM` 형식이 있으면 그 값을 `{{CHECK_TIME}}`으로 사용하고, 없으면 현재 시각을 기준으로 자동 설정하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
