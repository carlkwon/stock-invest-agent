---
description: 매주 유튜버 '슈페TV' 미국 증시 분석 영상 및 월가 리포트 요약 워크플로우
argument-hint: [TARGET_DATE=YYYY_MM_DD]
---

`.agent/workflows/supe-tv-weekly-report.md` 워크플로우를 읽고 그 지침을 그대로 따르세요.

전달된 인자: $ARGUMENTS

- 인자가 비어 있으면 `{{TARGET_DATE}}`는 슈페TV 최신 공개 영상 업로드일(YYYY_MM_DD)로 자동 설정하세요.
- 인자에 `TARGET_DATE=YYYY_MM_DD` 형식이 있으면 그 값을 사용하세요.
- 나머지는 워크플로우 문서의 Global Context와 Workflow Phases를 그대로 따르세요.
