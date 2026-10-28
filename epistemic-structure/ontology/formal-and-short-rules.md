---
date created: 2026-10-21
date modified: 2026-10-28
tags: [ontology, 규약, 정식, 약식]
description: 정식 규약과 약식 규칙의 정의, 약식 규칙의 자리, 둘의 관계
---

# 정식 규약과 약식 규칙

## 정의

- 정식 규약: 이 레포가 담는 글쓰기 규정 전체. 갈래별 규정, 그 근거, 기각한 대안, 예시 기반 세부 규정까지 포함한다. 윤문처럼 글 전체를 본격적으로 다듬을 때의 기준이다.
- 약식 규칙: 다른 자리에 설치되거나 상속되어 매 작업에 바로 적용되는 짧은 글쓰기 규칙. 근거와 세부는 담지 않는다.

## 약식 규칙의 자리

| 약식 규칙 | 자리 | 적용 대상 |
|-----------|------|-----------|
| 사용자 공통 지침의 문서 작성, 표현 정확성, 응답 구성 조항 | devcode-management의 공통 지침 설치 원본. 전역 `~/.claude/CLAUDE.md`와 채팅 UI 사용자 맞춤 설정에 설치된다 | 모든 AI 작업 환경 |
| 스캐폴드 문서 작성 규약 | 에피스테믹 워크스페이스 스캐폴드의 `AGENTS/epistemic-rules/communication.md` "문서 작성 스타일", "응답 언어", "대화 보고"와 `AGENTS/epistemic-rules/writing-style.md`, 그 하위 문서(`AGENTS/epistemic-rules/writing-style/`). 늘 읽히는 핵심은 `communication.md`에, 나머지 본문과 세부는 `writing-style.md`와 하위 문서에 있다. 이 레포를 포함한 스캐폴드 자식이 상속한다 | 워크스페이스 문서 |

스캐폴드에서 상속한 이 규약은 이 레포 자신의 문서 작성 규약이기도 하다. 레포 이름 writing-style과 상속한 파일 `AGENTS/epistemic-rules/writing-style.md`의 이름이 같지만 서로 다른 것을 가리킨다. 이 레포 자신의 평서문 기록에서 이 규약과 정식 규약이 어긋날 때 어느 쪽을 따르는지는 루트 [AGENTS.md](../../AGENTS.md) "이 워크스페이스의 규범"이 정한다.

## 관계

약식 규칙의 본문 SSOT(single source of truth)는 각자의 자리에 있고, 이 레포는 그 규칙들의 근거와 전체 규정을 담는다. 두 쪽은 의도적으로 내용이 겹친다. 동기화의 방향과 시점은 [strategy/project-overview.md](../strategy/project-overview.md)가 다룬다.
