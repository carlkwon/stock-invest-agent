---
description: 한국 수출입 통계 및 주요 기업 실적 분석 리포트 생성 워크플로우
argument-hint: [TARGET_MONTH=YYYY년 M월]
---

`.agent/workflows/korea-trade-report.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- 인자가 비어 있으면 `{{TARGET_MONTH}}`는 현재 시점 기준 직전 월(산업통상자원부 수출입동향이 이미 발표된 가장 최근 월)로 자동 판단하세요.
- 인자에 `TARGET_MONTH=...` 형식이 있으면 그 값을 사용하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
