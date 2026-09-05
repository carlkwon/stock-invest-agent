---
description: KOSPI & KOSDAQ 시가총액·수급 흐름 분석 워크플로우
argument-hint: [TARGET_TIME=YYYY_MM]
---

`.agent/workflows/KOSPI & KOSDAQ Market Cap & Flow Trends Report.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- 인자가 비어 있으면 `{{TARGET_TIME}}`은 오늘이 속한 월로 자동 설정하세요.
- 인자에 `TARGET_TIME=YYYY_MM` 형식이 있으면 그 값을 사용하세요.
- 나머지는 워크플로우 문서의 Global Context와 Data Retrieval 우선순위를 그대로 따르세요.
