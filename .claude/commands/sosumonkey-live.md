---
description: 매주 일요일 밤 8시 유튜버 '소수몽키' 라이브 영상 분석 및 주간 증시 전망 리포트 생성 워크플로우
argument-hint: [TARGET_DATE=YYYY_MM_DD]
---

`.agent/workflows/sosumonkey-live-report.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- 인자가 비어 있으면 `{{TARGET_DATE}}`는 가장 최근 일요일 날짜(YYYY_MM_DD)로 자동 설정하세요.
- 인자에 `TARGET_DATE=YYYY_MM_DD` 형식이 있으면 그 값을 사용하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
