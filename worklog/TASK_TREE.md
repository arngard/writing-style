---
date created: 2026-04-18
date modified: 2026-11-03
tags: [worklog]
description: 작업의 계층 구조와 다음 작업 포인터
---

# 작업 트리

> 작업의 계층 구조와 다음 작업 포인터. 노드 유형, 표기, 갱신 규칙, 삭제 규칙은 [task-tree.md](AGENTS/epistemic-rules/task-tree.md).

- [/] 워크스페이스 초기 세팅
  - 설명: 이 단계의 모든 "선정/작성" 작업은 인간 입력 없이 채울 수 없다. AI는 각 작업 전에 필요한 정보를 인간에게 인터뷰하여 확보한다. 추측으로 채우지 않는다. ref: [epistemic-rules.md](../AGENTS/epistemic-rules.md) "비협상 게이트".
  - [x] 커밋 전 훅 연결
  - [ ] 상류 연결과 채택 방식 기록
    - 설명: 원본은 이미 `upstream` 원격으로 연결돼 있다. 고른 방식과 이유를 [epistemic-structure/strategy/](../epistemic-structure/strategy/AGENTS.md)에 남긴다.
  - [x] 워크스페이스 폴더 이름을 프로젝트에 맞게 변경
  - [-] 모든 `.md` 파일의 `date created` / `date modified`를 오늘 날짜로 일괄 업데이트
    - 설명: 상류와 연결한 워크스페이스라 날짜를 바꾸지 않는다(바꾸면 상류 머지마다 충돌한다). 채택 방식별 처리는 [document-temporality.md](../AGENTS/epistemic-rules/document-temporality.md) "출고 문서의 날짜".
  - [x] 워크스페이스 정체 특수화
  - [x] README와 LICENSE 정리
  - [ ] 감사 주기 값 검토
    - 설명: [status-registry.md](AGENTS/epistemic-rules/status-registry.md) "주기 조건"의 값이 작업 빈도에 맞는지 검토한다. 바꿀 값이 있으면 [AGENTS.md](AGENTS.md)에 그 절의 형식으로 바꿀 행만 적은 표를 둔다. 표에 없는 행은 상류 표를 따른다.
  - [x] 프로젝트 수준 상위 결정 기록
  - [x] 도메인 온톨로지 정의
  - [ ] 핵심 제약 목록 작성
    - 설명: [epistemic-structure/architecture/core-constraints.md](../epistemic-structure/architecture/core-constraints.md)의 "제약 목록" 섹션을 작성한다. 각 제약은 상세 문서와 링크로 연결한다. 작성 완료 후 문서 상단의 `[주의]` 주의문을 삭제한다.
  - [ ] 코딩 규약 확장
    - 설명: [epistemic-structure/architecture/conventions.md](../epistemic-structure/architecture/conventions.md)에 언어/빌드, 패키지 구조, 네이밍, 가시성, 의존성, 테스트 등 프로젝트 고유 규약을 추가한다. 작성 완료 후 문서 상단의 `[주의]` 주의문을 삭제한다.
  - [x] 남은 튜토리얼 샘플을 실제 문서로 교체
  - [x] 구현 프로젝트 등록
    - 설명: 이 레포의 구현 영역은 코드가 아니라 세부 규정 묶음을 하위 폴더로 담는다([implementation.md](../implementation.md)).

- [/] 2026-10-24 의미 감사 발견 사항 처리
  - [x] 회고 파일명 형식을 상위 시간성 규약에 맞춘다
  - [x] README.en.md를 이 레포 정체성으로 다시 쓸지 삭제할지 정한다
  - [x] conventions.md의 스캐폴드 상태 마커를 복원할지 코딩 규약 확장 노드를 닫을지 정한다
  - [x] 상류 흡수 단위의 착수 등재 누락과 의미 정합 지연을 스캐폴드 격상 후보로 평가한다
  - [/] 작업 트리의 경위 서술과 어긋난 설명을 정리한다
    - 설명: 초기 세팅 루트의 완료 자식 설명과 상태 상세에 남은 경위 서술, 구현 프로젝트 등록 노드 설명과 실제 구현 영역의 불일치.
    - 브랜치: `docs/261103-split-large-docs` (워크트리: `../writing-style.worktrees/docs-261103-split-large-docs`)
  - [x] main 직접 커밋 2건의 당시 허용 여부를 사용자와 대조한다
  - [ ] 감사가 확실하지 않음으로 남긴 판단을 사용자와 정한다
    - 설명: [audience-aware-document-placement.md](../epistemic-structure/architecture/audience-aware-document-placement.md)의 주 위치(상류 격상, 또는 인스턴스 유지 시 워크스페이스 운영 규범이라 `AGENTS/` 옆 낱개 문서).

- [/] 2026-10-28 흡수 의미 정합 검토 발견 사항 처리
  - [x] 흡수 뒤 의미 감사를 받고 상태 레지스트리를 갱신한다
  - [x] 이 레포 문서의 태그 어휘 정리안을 정한다
  - [x] 정식 규약 문서와 상류 규범의 관계를 "이 워크스페이스의 규범"에 등재할지 정한다
  - [x] 스캐폴드 약식 규칙의 범위 서술을 상류 재배치에 맞춘다
  - [ ] 정식 규약에 없는 상류 약식 규칙 조항을 들일지 정한다
    - 설명: 흡수 전부터의 차이다. 줄임말 회피(레포가 걸리는지 포함), 말줄임표와 둥근 따옴표의 ASCII 치환, 코드 블록 절제, 절 참조 형식, 결격 대응, 비속어 금지, 에러 메시지 첫 문장 영문. 9778a7a 흡수로 상류 [reference-markers.md](../AGENTS/epistemic-rules/writing-style/reference-markers.md)가 표지 생략 대상인 색인 성격의 목록에 규범 요지가 상황별로 읽을 문서를 안내하는 목록(`상황 -> [문서](경로)`)을 더하고, 그 목록의 상황과 대상을 잇는 화살표는 표지로 바꾸지 않는다고 더했다. 정식 규약 [placement-and-omission.md](../implementation/reference-notation/placement-and-omission.md)에는 두 조항이 없고, 색인 성격의 목록 예시 문언도 갈린다(정식은 화자 노드가 의견을 늘어놓은 목록, 약식은 인물이나 주제 문서가 관련 문서를 늘어놓은 목록). 동기화 방향의 난점이 풀리기 전에는 등재만 한다.
    - 상태 상세: 등재만 유지한다(사용자 결정, 2026-10-28). 정식 규약에 들이지 않은 상류 조항은 이 레포 자신의 문서에서 상류대로 따른다(루트 AGENTS.md "이 워크스페이스의 규범").

- [/] 분량 한도에 닿은 문서를 나누고 재배치한다
  - 설명: 공백 제외 2,850자 이상인 문서 가운데 상속 사본이 아닌 것을 관심사별 하위 문서로 나눈다. 작업 트리는 위 경위 서술 정리 노드에서 다룬다.
  - 브랜치: `docs/261103-split-large-docs` (워크트리: `../writing-style.worktrees/docs-261103-split-large-docs`)
  - [x] 평서문 기록 규약의 어휘 절과 구성 절을 하위 문서로 내린다
  - [x] 참조 표지 세부 규정에서 자리와 표지 생략을 다른 문서로 나눈다
