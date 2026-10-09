---
description: 스마트머니 통합 추적 — 13F 구루·대형 기관, 미국 의원 주식 거래, 옵션 특이 거래, 나스닥 기관 매매 동향
argument-hint: [TARGET_QUARTER="2026 Q2"] [MODULES=A,B,C,D]
---

`.agent/workflows/institutional-tracker.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- 인자가 비어 있으면 `{{TARGET_QUARTER}}`는 현재 시점 기준 가장 최신 공시 분기로 자동 판단하세요.
- 인자에 `TARGET_QUARTER=...` 형식이 있으면 그 값을 사용하세요.
- 인자에 `TARGET_INVESTORS=...`가 있으면 워크플로우 문서의 기본 대상 목록 대신 그 목록을 사용하세요.
- 인자에 `MODULES=...`가 있으면 해당 모듈만 실행하세요(A=13F, B=의원 거래, C=옵션 특이 거래, D=나스닥 기관 동향). 없으면 전체(A,B,C,D)를 실행하세요.
- 인자에 `TARGET_POLITICIANS=...` 또는 `OPTIONS_WATCHLIST=...`가 있으면 기본 목록 대신 그 값을 사용하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
