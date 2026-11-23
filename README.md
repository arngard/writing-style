---
date created: 2026-04-18
date modified: 2026-11-23
tags: [소개]
description: 사용자의 모든 글쓰기에 대한 정식 규약 워크스페이스의 소개, 윤문의 정의와 윤문 절차, 갈래별 규약 파일, 규칙 문서를 읽는 때, 영역 구성
---

한국어 | [English](README.en.md)

# writing-style

사용자(아릉)의 모든 글쓰기에 대한 정식 규약을 연구, 회고, 규정하는 워크스페이스. 평서문 기록(문서, 보고), 회고, 소설 같은 창작, 코드 주석과 커밋 메시지까지 모든 갈래를 다룬다. 사용자 공통 지침이나 스캐폴드 문서 작성 규약 같은 다른 자리의 글쓰기 규칙은 매 작업에 적용하는 약식 규칙이고, 이 레포는 그 근거와 전체 규정을 담는 정식 규약이다.

## 이 레포를 기준으로 윤문할 때

윤문은 이미 쓴 글의 뜻을 유지하면서 표현, 문장, 구성을 다듬는 일이다. 내용의 사실관계를 새로 조사하거나 주장을 바꾸는 일은 윤문이 아니라 개정이다. 정의는 [epistemic-structure/ontology/polishing.md](epistemic-structure/ontology/polishing.md)에 있다.

다른 레포의 글을 윤문하는 에이전트는 윤문 절차 [implementation/polishing/workflows/polish.md](implementation/polishing/workflows/polish.md)를 따른다. 글을 고치지 않고 규약에 어긋난 자리의 리포트만 받을 때는 검출 절차 [implementation/polishing/workflows/detect.md](implementation/polishing/workflows/detect.md)를 따른다.

고칠 글의 갈래를 먼저 정한다. 갈래 정의는 [epistemic-structure/ontology/writing-genres.md](epistemic-structure/ontology/writing-genres.md)에 있다. 갈래마다 따르는 규약 파일은 다음과 같다.

| 갈래 | 규약 파일 |
|------|-----------|
| 평서문 기록(문서, 보고, 분석, 커밋 메시지, 사실과 판단을 전하는 대화 응답) | [plain-prose-rules.md](epistemic-structure/architecture/plain-prose-rules.md)와 그 규칙 문서 |
| 회고 | 없음 |
| 창작 | 없음 |
| 주석 | 없음 |

규약 파일이 없는 갈래를 다루는 법은 윤문 절차의 첫 단계에 있다.

평서문 기록을 윤문할 때 읽는 규칙 문서와 읽는 때는 다음과 같다. 각 규칙의 예시는 규칙의 `### 설명` 절이 가리키는 설명 문서에 있다.

| 규칙 문서 | 읽는 때 |
|-----------|---------|
| [polishing-principles.md](epistemic-structure/architecture/plain-prose-rules/polishing-principles.md) | 윤문할 때마다. 다른 규칙 문서를 맡은 검토자도 함께 읽는다 |
| [vocabulary.md](epistemic-structure/architecture/plain-prose-rules/vocabulary.md) | 용어, 외래어, 낱말, 약어를 고를 때 |
| [sentence.md](epistemic-structure/architecture/plain-prose-rules/sentence.md) | 문체, 문장 하나의 구성, 날짜와 시간 표기를 볼 때 |
| [format.md](epistemic-structure/architecture/plain-prose-rules/format.md) | 서식 강조, 기호, 문장 부호를 볼 때 |
| [bullets-and-prose.md](epistemic-structure/architecture/plain-prose-rules/bullets-and-prose.md) | 개조식과 줄글 가운데 무엇으로 쓸지 가를 때 |
| [reference.md](epistemic-structure/architecture/plain-prose-rules/reference.md) | 링크, 참조 표지, 문서의 부분을 가리키는 말을 볼 때 |
| [composition.md](epistemic-structure/architecture/plain-prose-rules/composition.md) | 글의 구성, 요약과 전재, 사실과 의견의 구분을 볼 때 |
| [document-temporality.md](epistemic-structure/architecture/plain-prose-rules/document-temporality.md) | 문서 전체가 가리키는 시점과 이유, 서사의 자리를 볼 때 |

규정의 이유가 필요하면 [epistemic-structure/strategy/INDEX.md](epistemic-structure/strategy/INDEX.md)의 문서 목록에서 근거 문서를 찾아본다.

윤문의 대상은 그 레포의 글이며, 이 레포는 읽기만 한다. 이 레포의 규정과 대상 레포가 따르는 약식 규칙이 어긋나면 고치기 전에 사용자의 결정을 받는다. 이 레포의 규정에서 고칠 점을 발견하면 이 레포의 작업으로 넘긴다.

## 구성

에피스테믹 워크스페이스 스캐폴드([arngard/epistemic-workspace-scaffold](https://github.com/arngard/epistemic-workspace-scaffold))를 `upstream`으로 상속한다. 영역별로 담는 것은 [epistemic-structure/architecture/category-placement.md](epistemic-structure/architecture/category-placement.md)가 정한다.

| 영역 | 담는 것 |
|------|---------|
| `epistemic-structure/ontology/` | 글 갈래와 글쓰기 개념의 정의 |
| `epistemic-structure/knowledge/` | 외부 사실, 외부 지침의 검토 |
| `epistemic-structure/strategy/` | 규약의 근거, 기각한 대안, 회고 |
| `epistemic-structure/architecture/` | 갈래별 정식 규약 본체 |
| `implementation/` | 규약을 글에 적용하는 수단(규칙의 설명, 윤문 도구, 윤문 절차, 윤문 스킬 원본) |

운영 지침의 단일 진입점은 [AGENTS.md](AGENTS.md)다.
