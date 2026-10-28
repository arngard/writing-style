---
date created: 2026-04-18
date modified: 2026-10-28
tags: [규칙, 문서관리]
---

@AGENTS/epistemic-rules.md

> `@`로 시작하는 줄은 그 경로의 파일을 지금 읽으라는 뜻이다. 경로는 저장소 루트가 아니라 그 줄이 든 파일의 위치 기준이다. 가져오기를 펼치지 않는 도구는 그 파일을 직접 열어 읽는다.

# AI Agent 지침

> 이 파일은 모든 AI 도구가 이 프로젝트를 다룰 때의 기본 지침이다. 출고된 진입점 파일(`CLAUDE.md`, `.github/copilot-instructions.md`)은 이 파일을 가리킨다. 도구별 진입점은 [tool-environment.md](AGENTS/epistemic-rules/tool-environment.md).

## 이 워크스페이스의 정체

이 레포(writing-style)는 사용자(아릉)의 모든 글쓰기에 대한 정식 규약을 연구, 회고, 규정하는 전문화 워크스페이스다. 대상은 평서문 기록(문서, 보고), 회고, 소설 같은 창작, 코드 주석과 커밋 메시지까지 사용자가 쓰는 모든 글이다. 다른 자리의 글쓰기 규칙(사용자 공통 지침, 스캐폴드 문서 작성 규약. 각 자리는 [formal-and-short-rules.md](epistemic-structure/ontology/formal-and-short-rules.md) "약식 규칙의 자리")은 약식 규칙이고, 이 레포가 그 근거와 전체 규정을 담는 정식 규약이다. 다른 레포에서 윤문할 때 윤문 에이전트가 이 레포를 기준으로 읽으며, 외부 독자의 진입점은 [README.md](README.md)다. 목적과 범위의 근거는 [epistemic-structure/strategy/project-overview.md](epistemic-structure/strategy/project-overview.md)다. 새 글쓰기 지식, 근거, 규정을 어느 범주와 `implementation`에 둘지는 [epistemic-structure/architecture/category-placement.md](epistemic-structure/architecture/category-placement.md)를 따르고, 평서문 기록을 쓰거나 윤문할 때는 [epistemic-structure/architecture/plain-prose-rules.md](epistemic-structure/architecture/plain-prose-rules.md)를 읽는다.

스캐폴드 template을 upstream으로 상속한다. 위에서 가져온 상류 규범(요지 [AGENTS/epistemic-rules.md](AGENTS/epistemic-rules.md)와 그 묶음)을 따르고, 상속 자산의 변경과 특수화는 [AGENTS/epistemic-rules/instance-specialization.md](AGENTS/epistemic-rules/instance-specialization.md)를 따른다 - 계승된 자산을 제자리에서 고치기 전에 상류 반영과 도메인 특수화를 분기해 사용자에게 짚는다.

## 이 워크스페이스의 규범

이 워크스페이스 고유의 규범과 상류 규범의 덮어쓰기 목록을 여기에 둔다. 형식은 [AGENTS/epistemic-rules/instance-specialization.md](AGENTS/epistemic-rules/instance-specialization.md)를 따른다.
