---
date created: 2026-05-19
date modified: 2026-10-28
tags: [strategy, 프로젝트]
description: 이 레포의 목적과 포함, 미포함 범위를 정한 프로젝트 수준 결정
importance: 상
urgency: 중
---

# 프로젝트 수준 결정 - 모든 글쓰기의 정식 규약

## 상황

사용자(아릉)는 평서문 기록, 회고, 소설 같은 창작, 코드 주석까지 여러 갈래의 글을 쓴다. 지금까지 글쓰기 규칙은 여러 자리에 짧게 흩어져 있었다. 모든 AI 작업 환경에 설치되는 사용자 공통 지침, 스캐폴드의 문서 작성 규약, 작업 교훈 단편이다. 이 규칙들은 매 작업에 바로 적용하도록 요지만 담고 있어서, 윤문처럼 글 전체를 본격적으로 다듬을 때 기준으로 삼기에는 근거와 세부가 모자란다.

이 레포는 처음에 란다 작품의 문체를 추출하는 공간으로 출발했다. 그 범위로는 위의 공백을 채울 수 없어서, 대상을 모든 글쓰기로 넓힌다.

importance 상: 이 레포의 규약은 사용자의 다른 모든 글쓰기와 다른 레포의 윤문에 기준으로 쓰인다. urgency 중: 즉시 시급한 마감은 없으나 규약과 회고는 누적에 시간이 들어 일찍 시작할수록 좋다.

## 난점

- 정식 규약과 약식 규칙의 동기화: 정식 규약이 다듬어졌을 때 약식 규칙(공통 지침의 설치 원본, 스캐폴드 문서 작성 규약)으로 언제 어떻게 반영할지 정하지 않았다. 레포 간 반영은 사용자가 트리거할 때만 한다는 기존 교훈(devcode-management `epistemic-structure/strategy/lessons/cross-repo-sync-user-triggered.md`)이 적용된다.
- 윤문 때의 우선순위: 다른 레포를 윤문할 때 이 레포의 정식 규약과 그 레포가 따르는 약식 규칙이 어긋나면 어느 쪽을 따를지 정하지 않았다. 정해지기 전에는 윤문 에이전트가 어긋남을 고치기 전에 사용자에게 짚는다.

## 대응

이 레포의 목적은 사용자의 모든 글쓰기에 대해 정식 규약을 연구, 회고, 규정하는 것이다. 사람과 AI가 사용자의 글을 사용자답게 쓰고 다듬게 한다.

### 포함 범위

- 갈래별 정식 규약과 그 근거. 갈래는 [ontology/writing-genres.md](../ontology/writing-genres.md)가 정의한다.
- 어법, 표기, 문장 단위 규칙을 예시 기반으로 상세히 규정한 세부 규정.
- 써 본 글의 회고와 거기서 얻은 교훈.
- 외부 글쓰기 지침과 문체론의 검토.

### 미포함 범위

- 작품의 세계관, 플롯, 인물 같은 콘텐츠. 란다 작품 콘텐츠의 SSOT(single source of truth)는 landa 레포다.
- 다른 레포의 글 자체. 윤문의 대상은 그 레포의 작업이고, 이 레포는 기준으로 읽히기만 한다.

### 정식 규약과 약식 규칙의 관계

용어는 [ontology/formal-and-short-rules.md](../ontology/formal-and-short-rules.md). 약식 규칙은 매 작업에 적용하는 요지이고, 이 레포는 그 근거와 전체 규정을 담는다. 두 쪽은 의도적으로 내용이 겹친다. 약식 규칙의 본문 SSOT는 각자의 자리(공통 지침은 devcode-management, 스캐폴드 문서 작성 규약은 스캐폴드)에 그대로 둔다.

### 외부 독자

다른 레포의 윤문 에이전트가 이 레포를 기준으로 읽는다. 그래서 규약은 이 레포의 다른 문서를 모두 읽지 않아도 그 자체로 이해되게 쓰고, 진입점 [README.md](../../README.md)에서 닿게 둔다. 배치 명세는 [architecture/category-placement.md](../architecture/category-placement.md)다.

### 란다 갈래

란다 작품의 문체는 창작 갈래의 한 대상이다. 입력은 landa 레포의 작품 정리본이며, 원본 자료는 이 레포의 영역 밖이다. 용어는 [ontology/landa.md](../ontology/landa.md).

## 참고

- ref: [ontology/landa.md](../ontology/landa.md) - "란다" 용어 정의
- ref: [knowledge/about-landa-record.md](../knowledge/about-landa-record.md) - 란다 작품에 대한 외부 사실
- ref: [why-preserve-over-compress.md](why-preserve-over-compress.md) - 압축보다 보존을 우선하는 근거
