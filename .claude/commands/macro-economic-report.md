---
description: 거시경제지표 종합 분석 및 주식 투자 전략 리포트 워크플로우 (매주 실행)
argument-hint: []
---

`.agent/workflows/macro-economic-report.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS (보통 필요 없음)

- `{{RUN_DATE}}`는 오늘 날짜, `{{TARGET_WEEK_LABEL}}`은 워크플로우 문서의 계산식(`N = ceil(일/7)`)대로 자동 산출하세요.
- `{{PREV_REPORT_PATH}}`는 `reports/macro/` 디렉토리에서 가장 최근 `macro_economic_report_*.md`를 탐색해 확인하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
