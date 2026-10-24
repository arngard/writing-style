---
date created: 2026-04-18
date modified: 2026-10-24
tags: [소개]
---

한국어 | [English](README.en.md)

# writing-style

사용자(아릉)의 모든 글쓰기에 대한 정식 규약을 연구, 회고, 규정하는 워크스페이스. 평서문 기록(문서, 보고), 회고, 소설 같은 창작, 코드 주석과 커밋 메시지까지 모든 갈래를 다룬다. 사용자 공통 지침이나 스캐폴드 문서 작성 규약 같은 다른 자리의 글쓰기 규칙은 매 작업에 적용하는 약식 규칙이고, 이 레포는 그 근거와 전체 규정을 담는 정식 규약이다.

## 이 레포를 기준으로 윤문할 때

다른 레포의 글을 윤문하는 에이전트는 아래 순서로 읽는다.

1. [_docs/_ontology/writing-genres.md](_docs/_ontology/writing-genres.md)에서 고칠 글의 갈래를 정한다.
2. [_docs/_architecture/AGENTS.md](_docs/_architecture/AGENTS.md)의 파일별 안내에서 그 갈래의 규약을 찾아 적용한다. 평서문 기록은 [_docs/_architecture/plain-prose-rules.md](_docs/_architecture/plain-prose-rules.md)다.
3. 어법, 표기 같은 세부는 [_implementation/](_implementation/AGENTS.md)의 예시 기반 세부 규정을 본다.
4. 규정의 이유가 필요하면 [_docs/_strategy/](_docs/_strategy/AGENTS.md)의 근거 문서를 본다.

윤문의 대상은 그 레포의 글이며, 이 레포는 읽기만 한다. 이 레포의 규정과 대상 레포가 따르는 약식 규칙이 어긋나면 고치기 전에 사용자에게 짚는다. 이 레포의 규정에서 고칠 점을 발견하면 이 레포의 작업으로 넘긴다.

## 구성

에피스테믹 워크스페이스 스캐폴드([arngard/epistemic-workspace-scaffold](https://github.com/arngard/epistemic-workspace-scaffold))를 `upstream`으로 상속한다. 영역별로 담는 것은 [_docs/_architecture/category-placement.md](_docs/_architecture/category-placement.md)가 정한다.

| 영역 | 담는 것 |
|------|---------|
| `_docs/_ontology/` | 글 갈래와 글쓰기 개념의 정의 |
| `_docs/_knowledge/` | 외부 사실, 외부 지침의 검토, 사용자의 글쓰기 선호 진술 |
| `_docs/_strategy/` | 규약의 근거, 기각한 대안, 회고 |
| `_docs/_architecture/` | 갈래별 정식 규약 본체 |
| `_implementation/` | 예시 기반 세부 규정 |

운영 지침의 단일 진입점은 [AGENTS.md](AGENTS.md)다.
