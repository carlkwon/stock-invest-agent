---
description: 섹터별 심층 투자 분석 및 핵심 기업 실적·수급 스크리닝 워크플로우
argument-hint: TARGET_SECTOR=반도체 [TARGET_TIME=YYYY_MM]
---

`.agent/workflows/sector-investment-report.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- `{{TARGET_SECTOR}}`는 필수입니다. 인자에 섹터명이 없으면 어떤 섹터를 분석할지 사용자에게 먼저 확인하세요(예: 반도체, 이차전지, 헬스케어, AI전력).
- `{{TARGET_TIME}}`이 인자에 없으면 가장 최근 실적·업황이 확인 가능한 월로 자동 설정하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
