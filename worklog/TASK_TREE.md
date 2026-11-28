---
date created: 2026-04-18
date modified: 2026-11-24
tags: [worklog]
description: 작업의 계층 구조와 다음 작업 포인터
---

# 작업 트리

> 작업의 계층 구조와 다음 작업 포인터. 노드 유형, 표기, 갱신 규칙, 삭제 규칙은 [task-tree.md](AGENTS/epistemic-rules/task-tree.md)에 있다.

- [ ] 스캐폴드 시간성 규범의 동결 조항을 소급 적용에 맞춰 개정하도록 상류에 올린다
  - 설명: `@arngard` 2026-11-21 결정. 종결된 문서도 규약에 어긋난 부분은 소급해 규약에 맞추고, 규약이 그 문서에 두지 않기로 한 내용도 걷는다. 상속 `document-temporality.md` "날짜 프리픽스의 의미와 종결 신호"는 종결 문서에 의미 내용을 바꾸지 않는 편집만 허용해 이 범위와 어긋난다. 개정이 들어오면 약식 규칙 자리 표에 시간성 규범을 올린다.

- [/] 워크스페이스 초기 세팅
  - 설명: 이 단계의 모든 "선정/작성" 작업은 사용자 입력 없이 채울 수 없다. AI는 각 작업 전에 필요한 정보를 사용자에게 인터뷰하여 확보한다. 추측으로 채우지 않는다. ref: [epistemic-rules.md](../AGENTS/epistemic-rules.md) "비협상 게이트".
  - [ ] 상류 연결과 채택 방식 기록
    - 설명: 원본은 이미 `upstream` 원격으로 연결돼 있다. 고른 방식과 이유를 [epistemic-structure/strategy/](../epistemic-structure/strategy/AGENTS.md)에 남긴다.
    - 설명: 상류와 연결한 워크스페이스라 `.md` 파일의 날짜를 일괄로 바꾸지 않는다(바꾸면 상류 머지마다 충돌한다). 채택 방식별 처리는 [document-temporality.md](../AGENTS/epistemic-rules/document-temporality.md) "출고 문서의 날짜".
  - [ ] 감사 주기 값 검토
    - 설명: [status-registry.md](AGENTS/epistemic-rules/status-registry.md) "주기 조건"의 값이 작업 빈도에 맞는지 검토한다. 바꿀 값이 있으면 [AGENTS.md](AGENTS.md)에 그 절의 형식으로 바꿀 행만 적은 표를 둔다. 표에 없는 행은 상류 표를 따른다.
  - [ ] 핵심 제약 목록 작성
    - 설명: [epistemic-structure/architecture/core-constraints.md](../epistemic-structure/architecture/core-constraints.md)의 "제약 목록" 절을 작성한다. 각 제약은 상세 문서와 링크로 연결한다. 작성 완료 후 문서 상단의 `[주의]` 주의문을 삭제한다.
  - [ ] 코딩 규약 확장
    - 설명: [epistemic-structure/architecture/conventions.md](../epistemic-structure/architecture/conventions.md)에 언어/빌드, 패키지 구조, 네이밍, 가시성, 의존성, 테스트 등 프로젝트 고유 규약을 추가한다. 작성 완료 후 문서 상단의 `[주의]` 주의문을 삭제한다.

- [/] 2026-10-24 의미 감사 발견 사항 처리
  - [ ] 감사가 확실하지 않음으로 남긴 판단을 사용자와 정한다
    - 설명: [audience-aware-document-placement.md](../epistemic-structure/architecture/audience-aware-document-placement.md)의 주 위치(상류 격상, 또는 인스턴스 유지 시 워크스페이스 운영 규범이라 `AGENTS/` 옆 낱개 문서).

- [/] 2026-10-28 흡수 의미 정합 검토 발견 사항 처리
  - [ ] 정식 규약에 없는 상류 약식 규칙 조항을 들일지 정한다
    - 설명: 흡수 전부터의 차이다. 줄임말 회피(상류는 "레포(레포지토리)"를 허용한다), 말줄임표와 둥근 따옴표의 ASCII 치환, 코드 블록 절제, 절 참조 형식, 결격 대응, 비속어 금지. 9778a7a 흡수로 상류 [reference-markers.md](../AGENTS/epistemic-rules/writing-style/reference-markers.md)가 표지 생략 대상인 색인 성격의 목록에 규범 요지가 상황별로 읽을 문서를 안내하는 목록(`상황 -> [문서](경로)`)을 더하고, 그 목록의 상황과 대상을 잇는 화살표는 표지로 바꾸지 않는다고 더했다. 정식 규약 [reference.md](../epistemic-structure/architecture/plain-prose-rules/reference.md)에는 두 조항이 없고, 색인 성격의 목록 예시 문언도 갈린다(정식은 화자 노드가 의견을 늘어놓은 목록, 약식은 인물이나 주제 문서가 관련 문서를 늘어놓은 목록). 2700319 흡수로 상류가 더한 조항 가운데 정식 규약에 없는 것은 통용되는 개념의 정의를 새로 적지 않는 조항([writing-style.md](../AGENTS/epistemic-rules/writing-style.md) "통용되는 개념의 정의"), 도구 호출 설명과 진행 알림처럼 사용자 화면에 보이는 글도 한국어로 쓰는 조항([communication.md](../AGENTS/epistemic-rules/communication.md) "응답 언어"), 질문에 대상 정보, 배경, 선택지, 판단 기준을 함께 두는 조항([conversation-reporting.md](../AGENTS/epistemic-rules/writing-style/conversation-reporting.md)), [attribution-scope.md](../AGENTS/epistemic-rules/writing-style/attribution-scope.md)의 의견의 시점, 결정 주체의 커밋 기록, 결정의 표기 범위다. 결정의 표기는 정식 규약이 규칙 문서에만 걸고 상류는 현재적 문서의 규칙, 명세, 결정 문장 전반에 건다. 4009e88 흡수로 상류 [conversation-reporting.md](../AGENTS/epistemic-rules/writing-style/conversation-reporting.md)가 질문 안의 판단과 선택지 순서를 [working-principles.md](../AGENTS/epistemic-rules/working-principles.md) "1. 넘겨짚지 않는다"에 맡겼고, 그 항목은 핵심 원인과 권하는 방향을 먼저 밝히고 선택지를 뒤에 붙인다. 정식 규약 [composition.md](../epistemic-structure/architecture/plain-prose-rules/composition.md)에는 이 조항이 없다. 그 문서의 결론 앞 요약과 질문을 끝에 두는 조항은 글 안의 배치를 정해 이 조항과 어긋나지 않는다. 동기화 방향의 난점이 풀리기 전에는 등재만 한다.
    - 상태 상세: 등재만 유지한다(사용자 결정, 2026-10-28). 정식 규약에 들이지 않은 상류 조항은 이 레포 자신의 문서에서 상류대로 따른다(루트 AGENTS.md "이 워크스페이스의 규범").

- [/] 스크립트화와 트리거에 따른 일괄 윤문에 맞게 레포 구성을 바꾼다
  - 설명: `@arngard` 2026-11-22 지시: "글쓰기 레포의 개선 작업으로서, 스크립트화 및 트리거에 따른 일괄 윤문에 용이한 형식으로 글쓰기 레포의 구성을 변경하는 작업이 필요해." 지금 정식 규약은 `epistemic-structure/architecture/plain-prose-rules/`와 `implementation/`(문장 부호, 참조 표기, 어휘 선택) 아래 산문 문서로만 있고, 기계로 검사하거나 일괄로 고치는 스크립트는 없다. 이어진 방향(`@arngard` 2026-11-22): "그 전부야. 스크립트로 완전처리 가능한 것 / 스크립트로 검출만 하고 수정은 의미적으로 하는 것 / 읽으면서 의미적으로 생각해서 고쳐야 하는 것. 각각을 분류하고 적절한 폴더 배치와 일관된 형식으로 구성해서, 일괄 처리하기에 능률적으로 만드는 거야." "윤문 트리거는 특별한 용어는 아니고. 윤문 스킬이 트리거 역할을 하겠지." 곧 정식 규약의 규칙을 세 부류(스크립트로 완전 처리, 스크립트로 검출하고 의미적으로 수정, 읽으며 의미적으로 수정)로 나눠 부류에 맞는 폴더 배치와 일관된 형식으로 다시 구성하고, 윤문 스킬이 그 처리를 시작하게 한다. 설계와 구현은 아직 착수하지 않는다(`@arngard` 2026-11-22).
  - 상태 상세: 구성 개편은 끝났다. 남은 것은 아래 범위 표시 규칙과 다른 레포에서 윤문 도구를 호출하게 하는 배치다.
  - [ ] 범위 표시를 물결표 대신 대시로 쓰는 규칙을 이 개편을 거쳐 적용한다
    - 설명: `@arngard` 2026-11-17 지시. 범위 표시를 물결표(`~`)나 "에서 ... 까지" 서술에서 대시(ASCII 하이픈 `-`)로 바꾼다. 물결표는 GitHub 마크다운과 채팅 화면이 물결표 사이를 취소선으로 그려 글이 깨질 수 있다. 스캐폴드 쪽 대상은 `ascii-punctuation.md`의 em dash 항목의 범위 표시 문장과 보존 예외의 `U+2500 ~ U+257F` 표기다. 정할 것: 끝점에 하이픈이 든 날짜 범위(`2026-11-17`부터 `2026-11-20`)의 표기(띄운 하이픈 ` - `은 부연 표지와 겹친다), 감사 검출을 넣을지. 2026-11-22 범위 물결표 실측(코드 영역 밖 숫자-물결표-숫자): 스캐폴드 3곳, epistemic-workspace-scaffold-management 7곳, devcode-management 25곳, writing-style 3곳, mobile-app-scaffold 2곳, investment-cartograph 10,509곳(2,159개 파일). 사용자 공통 지침 원본 devcode-management `implementation/global-claude-md/formal.md` 60행("4~5개")에도 있어 고치면 머신 재설치로 이어진다. `@arngard` 2026-11-22: 범위 표시와 물결표는 이 레포를 개선한 뒤 자연스럽게 처리된다.
    - 상태 상세: 표기 결정(`@arngard` 2026-11-23): "A - B"처럼 띄어쓰기와 대시를 쓴다. 끝점에 하이픈이 든 날짜 범위도 같은 표기로 본다(AI 해석, 확인 필요). 감사 검출 여부는 아직 정하지 않았다. 적용은 착수하지 않았다(기록만 지시).
  - [ ] 다른 레포에서 윤문 도구를 호출하게 devCode 폴더 체계에 배치한다
    - 설명: `@arngard` 2026-11-23 지시. 머신 전역이 아니라 devCode 폴더 체계에 넣는다. 다른 곳에서도 쓸 수 있게 처음부터 경로나 주소 같은 대상을 입력으로 받는다. 직접 고칠 수 없는 대상은 수정안만 받는 방식도 둔다. 스크립트와 스킬 워크플로의 핵심은 이 레포 안에 두고, 밖에서는 호출만 하게 구성한다. 착수하지 않았다(기록만 지시).

- [ ] macOS와 Python 3.9에서 윤문 도구 시험을 돌려 확인한다
  - 설명: 2026-11-24 윤문 속도 개선(검토 묶음, `--lines` 범위 옵션)은 Windows의 Python 3.15에서만 시험을 돌렸고, Python 3.9는 구문 검사만 했다. macOS 머신에서 `python3 -B -m unittest discover -s implementation/polishing/tools/tests -v`를, 가능하면 Python 3.9로 돌린다.

- [ ] 윤문 도구 개편으로 생긴 분량 경고 3건과 절 참조 경고를 판정한다
  - 설명: 개편 머지 시점(2026-11-23) 형식 감사가 새로 낸 경고다. 분량 경고는 `plain-prose-rules/reference.md`(공백 제외 5,435자), `plain-prose-rules/vocabulary.md`(4,245자), `README.en.md`(4,415자)이며, 여러 관심사가 섞였으면 나누고 한 관심사로 응집되면 수용 근거를 적는다. 절 참조 경고는 `vocabulary.md`가 설명 문서의 절 `'따로, 다른'의 뜻으로 "별"을 홀로 쓰지 않는다`를 가리키는 링크다. 대상 제목은 있고, 상류 형식 감사가 절 이름을 첫 큰따옴표에서 끊어 읽는 오탐이다. 상류 도구를 고칠지, 이 레포에서 수용할지 정한다.

- [x] 스캐폴드 005fb0a 흡수
  - 상태 상세: 328bb49 뒤 상류 머지 8건을 흡수했다. 충돌은 이 작업 트리 하나이며 자식 판으로 풀었다(자식은 출고 "환경 설치" 노드를 이미 지웠다). 형식 감사는 위반 0건, 경고 6건으로 머지 전과 같고, `.agents/skills`는 `.claude/skills`와 같다. 의미 정합 검토에서 인용 1건("감사 주기 값 검토" -> status-registry.md "주기 조건")은 정합이며, 자식 고유 문서에 CI 감사를 전제한 서술은 없다. 상류 writing-style.md "도구 전용 설정 파일 예외"의 변경은 front matter 의무와 감사 순회 범위 조항이라 정식 규약과 비교할 글쓰기 조항이 아니다.
