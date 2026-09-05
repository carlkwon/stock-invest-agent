---
description: 13F 공시 기반 구루(Guru)·대형 기관 포트폴리오 매매 동향 분석 워크플로우
argument-hint: [TARGET_QUARTER="2026 Q2"]
---

`.agent/workflows/institutional-tracker.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- 인자가 비어 있으면 `{{TARGET_QUARTER}}`는 현재 시점 기준 가장 최신 공시 분기로 자동 판단하세요.
- 인자에 `TARGET_QUARTER=...` 형식이 있으면 그 값을 사용하세요.
- 인자에 `TARGET_INVESTORS=...`가 있으면 워크플로우 문서의 기본 대상 목록 대신 그 목록을 사용하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
