---
description: 주간 투자 가이드 통합 워크플로우 — 일요일 전망/수요일 중간점검/금요일 복기를 한 파일에 이어서 작성
argument-hint: [MODE=OUTLOOK|MIDCHECK|REVIEW]
---

`.agent/workflows/weekly-stock-guide.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- 인자가 비어 있으면 워크플로우의 규칙대로 오늘 요일로 `{{MODE}}`를 자동 판별하세요(일→OUTLOOK, 수→MIDCHECK, 금→REVIEW). 그 외 요일이면 사용자에게 MODE를 확인하세요.
- 인자에 `MODE=OUTLOOK` / `MODE=MIDCHECK` / `MODE=REVIEW`가 있으면 그 값을 그대로 `{{MODE}}`로 사용하세요.
- 나머지는 워크플로우 문서의 Global Context와 각 Phase Group 지침을 그대로 따르세요.
