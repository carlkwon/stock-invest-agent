---
description: 레이 달리오 올웨더(Risk Parity) 포트폴리오 매크로 국면 진단 및 리밸런싱 리포트 생성 워크플로우
argument-hint: [TARGET_DATE="2026_08"]
---

`.agent/workflows/All_Weather_Portfolio.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- 인자가 비어 있으면 `{{TARGET_DATE}}`는 오늘이 속한 월(YYYY_MM)로 자동 설정하세요.
- 인자에 `TARGET_DATE="YYYY_MM"` 형식이 있으면 그 값을 사용하세요.
- 나머지는 워크플로우 문서의 Global Context와 Step 1~6을 그대로 따르세요.
