---
date created: 2026-04-18
date modified: 2026-10-28
tags: [worklog]
description: 작업의 계층 구조와 다음 작업 포인터
---

# 작업 트리

> 작업의 계층 구조와 다음 작업 포인터. 노드 유형, 표기, 갱신 규칙, 삭제 규칙은 [task-tree.md](AGENTS/epistemic-rules/task-tree.md).

- [/] 워크스페이스 초기 세팅
  - 설명: 이 단계의 모든 "선정/작성" 작업은 인간 입력 없이 채울 수 없다. AI는 각 작업 전에 필요한 정보를 인간에게 인터뷰하여 확보한다. 추측으로 채우지 않는다. ref: [epistemic-rules.md](../AGENTS/epistemic-rules.md) "비협상 게이트".
  - 상태 상세: 정체성을 모든 글쓰기의 정식 규약으로 세우고 이름을 writing-style로 바꿨다. 남은 항목은 상류 연결과 채택 방식 기록, 감사 주기 값 검토, 핵심 제약 목록, 규약 확장이다.
  - [x] 커밋 전 훅 연결
    - 설명: 클론마다 연결 명령을 한 번 실행해 커밋할 때 폴더 색인이 다시 만들어지게 한다. 연결하지 않으면 CI(continuous integration) 감사가 낡은 색인을 위반으로 잡는다. 명령은 [tools.md](../AGENTS/epistemic-rules/tools.md) "색인 생성 스크립트". 이 클론 다음에 만드는 클론도 각자 연결한다.
  - [ ] 상류 연결과 채택 방식 기록
    - 설명: 원본은 이미 `upstream` 원격으로 연결돼 있다. 고른 방식과 이유를 [epistemic-structure/strategy/](../epistemic-structure/strategy/AGENTS.md)에 남긴다.
  - [x] 워크스페이스 폴더 이름을 프로젝트에 맞게 변경
    - 설명: AI는 워크스페이스 부모 디렉토리를 직접 리네임할 수 없다 (현재 작업 디렉토리가 바뀌어 세션 상태가 깨짐). 인간에게 이름을 받은 뒤, 인간이 터미널에서 직접 리네임하고 에디터/세션을 재시작하도록 안내한다. 이미 원하는 이름으로 되어 있으면 이 작업을 `[x]`로 전환하고 다음으로 진행한다.
  - [-] 모든 `.md` 파일의 `date created` / `date modified`를 오늘 날짜로 일괄 업데이트
    - 설명: 상류와 연결한 워크스페이스라 날짜를 바꾸지 않는다(바꾸면 상류 머지마다 충돌한다). 채택 방식별 처리는 [document-temporality.md](../AGENTS/epistemic-rules/document-temporality.md) "출고 문서의 날짜".
  - [x] 워크스페이스 정체 특수화
    - 설명: [AGENTS.md](../AGENTS.md) "이 워크스페이스의 정체" 절을 도메인 정체성으로 특수화한다. 그 밖의 계승 자산은 [AGENTS/epistemic-rules/instance-specialization.md](../AGENTS/epistemic-rules/instance-specialization.md)를 따른다.
  - [x] README와 LICENSE 정리
    - 설명: 스캐폴드 소개문인 README.md, README.en.md를 이 워크스페이스의 소개로 교체하고(상류를 받으면 충돌 유의), LICENSE를 정한다.
    - 상태 상세: README 두 편은 이 레포의 소개로 교체했다. LICENSE는 상류의 MIT 라이선스를 그대로 둔다(사용자 결정).
  - [ ] 감사 주기 값 검토
    - 설명: [status-registry.md](AGENTS/epistemic-rules/status-registry.md) "주기 조건"의 값이 작업 빈도에 맞는지 검토한다. 바꿀 값이 있으면 [AGENTS.md](AGENTS.md)에 그 절의 형식으로 바꿀 행만 적은 표를 둔다. 표에 없는 행은 상류 표를 따른다.
  - [x] 프로젝트 수준 상위 결정 기록
    - 설명: 프로젝트 목표, 첫 출시 핵심 목표와 스펙, 향후 확장, 대상 고객과 사용자 등 큰 결정을 [epistemic-structure/strategy/](../epistemic-structure/strategy/AGENTS.md) 아래 `why-*.md` 문서들로 분리 작성한다. `project-overview.md`는 실제 내용으로 교체 완료.
  - [x] 도메인 온톨로지 정의
    - 설명: 의미가 갈릴 수 있는 핵심 용어를 식별하고 [epistemic-structure/ontology/](../epistemic-structure/ontology/AGENTS.md)에 정의한다. 튜토리얼용 `sample-term.md`는 upstream 동기화 시 제거됨.
  - [ ] 핵심 제약 목록 작성
    - 설명: [epistemic-structure/architecture/core-constraints.md](../epistemic-structure/architecture/core-constraints.md)의 "제약 목록" 섹션을 작성한다. 각 제약은 상세 문서와 링크로 연결한다. 작성 완료 후 문서 상단의 `[주의]` 주의문을 삭제한다.
  - [ ] 코딩 규약 확장
    - 설명: [epistemic-structure/architecture/conventions.md](../epistemic-structure/architecture/conventions.md)에 언어/빌드, 패키지 구조, 네이밍, 가시성, 의존성, 테스트 등 프로젝트 고유 규약을 추가한다. 작성 완료 후 문서 상단의 `[주의]` 주의문을 삭제한다.
  - [x] 남은 튜토리얼 샘플을 실제 문서로 교체
    - 설명: `sample-fact.md`, `sample-spec.md`, `sample-decision.md`는 upstream 동기화 시 제거됨. 각 범주(`knowledge`, `architecture`, `strategy`)에 실제 문서를 작성한다.
  - [x] 구현 프로젝트 등록
    - 설명: 실제 소스 코드 프로젝트를 [implementation/](../implementation/AGENTS.md)에 프로젝트별 폴더로 추가한다.

- [ ] 란다 갈래의 문체 추출 운영 절차를 설계할 때 단계 권한 배분 규범을 적용한다
  - 설명: [project-overview.md](../epistemic-structure/strategy/project-overview.md)가 목표로 든 "추출 작업의 운영 절차"는 아직 미작성이다. 절차를 쓸 때 상류 [AGENTS/epistemic-rules/unit-task/stage-authority.md](../AGENTS/epistemic-rules/unit-task/stage-authority.md)(2026-08-08 흡수)이 직접 걸린다 - 문체 특징이 스타일 가이드 규칙으로 승격되는 조건은 여러 문서에서 반복 관측되는가일 텐데, 문서 1건씩 읽는 추출 단계는 그 반복을 볼 수 없다. 승격 판정 권한은 누적 전체를 조망하는 자리(추출 후 정리 라운드)에 두고, 그 라운드는 추출 단계가 후보라고 표시한 것만 받지 않고 추출 산출 전체를 훑도록 설계한다 (AI 제안, 다른 자식 워크스페이스에서 같은 구조 결함이 실측된 데서 온 예방 등재).

- [/] 2026-10-24 의미 감사 발견 사항 처리
  - 상태 상세: 사용자가 정한 4건은 처리했다. 남은 것은 회고 파일명 형식, 작업 트리의 경위 서술 정리, 감사가 확실하지 않음으로 남긴 판단이다.
  - [ ] 회고 파일명 형식을 상위 시간성 규약에 맞춘다
    - 설명: [category-placement.md](../epistemic-structure/architecture/category-placement.md) 회고 절의 `yyyy-MM-dd-<슬러그>.md`를 `yyyy-MM-dd <제목>.md`로 고치고, 같은 원인의 `knowledge/2026-10-12-attention-span-review.md`를 리네임하며 링크를 연쇄 갱신한다. 그 문서는 종결 상태라 본문은 바꾸지 않는다. 회고 폴더를 처음 만들 때는 부모 문서 `strategy/retrospectives.md`와 `AGENTS.md`, `CLAUDE.md`를 같은 커밋에 두고, 날짜 순 폴더라 순차 분류로 선언할지 정한다.
  - [x] README.en.md를 이 레포 정체성으로 다시 쓸지 삭제할지 정한다
    - 설명: 내용이 상류 스캐폴드 소개 원문과 같았다. 사용자 결정에 따라 README.md를 영어로 옮겨 다시 썼다.
  - [x] conventions.md의 스캐폴드 상태 마커를 복원할지 코딩 규약 확장 노드를 닫을지 정한다
    - 설명: 상류 초기 세팅이 이 레포에 제대로 들어오지 않아 주의문이 빠져 있었다. 상류와 같은 주의문을 복원하고, 코딩 규약 확장 노드는 대기로 둔다.
  - [x] 상류 흡수 단위의 착수 등재 누락과 의미 정합 지연을 스캐폴드 격상 후보로 평가한다
    - 설명: 상류 흡수 머지 10건에 시작점 커밋이 없고, 27b030e 흡수의 의미 정합이 다음 단위로 밀렸다. 착수 등재와 시작점 커밋, 상류 흡수의 축약 금지, 같은 단위 안의 의미 정합은 기존 규약에 이미 있어 스캐폴드에 격상하지 않는다. 규약을 지키지 않은 데서 온 일이라 과거 이력은 고치지 않고, 이후 흡수부터 규약대로 한다(사용자 판단).
  - [ ] 작업 트리의 경위 서술과 어긋난 설명을 정리한다
    - 설명: 초기 세팅 루트의 완료 자식 설명과 상태 상세에 남은 경위 서술, 구현 프로젝트 등록 노드 설명과 실제 구현 영역의 불일치, 란다 문체 추출 노드의 다른 인스턴스 이력 서술.
  - [x] main 직접 커밋 2건의 당시 허용 여부를 사용자와 대조한다
    - 설명: ddd9f8f(2026-07-18), 2f56a2b(2026-07-21). 둘 다 TASK_TREE 완결 노드 삭제 커밋이다. 허용된 것이 아니라 규약을 지키지 않은 커밋이었고, 결과에 문제가 없어 이력은 고치지 않는다. 이후 트리 정리도 작업 브랜치 안에서 한다(사용자 판단).
  - [ ] 감사가 확실하지 않음으로 남긴 판단을 사용자와 정한다
    - 설명: [audience-aware-document-placement.md](../epistemic-structure/architecture/audience-aware-document-placement.md)의 주 위치(상류 격상, 또는 인스턴스 유지 시 워크스페이스 운영 규범이라 `AGENTS/` 옆 낱개 문서), [about-landa-record.md](../epistemic-structure/knowledge/about-landa-record.md) 방침 문장의 위치, devcode-management 호명과 경로 인용.
    - 상태 상세: 상류 설계 원칙(강타입 등)을 이 레포에서 덮어쓸지의 질문은 상류가 9778a7a에서 강타입을 코드와 데이터 모델 결정으로 한정하고 문서와 글쓰기 규약에는 적용하지 않는다고 밝혀 걷어 냈다([design-principles.md](../AGENTS/epistemic-rules/design-principles.md)). README 태그 중복은 태그 원칙이 바뀐 뒤 README 두 편의 태그가 `소개` 하나라 해소돼 걷어 냈다.

- [/] 2026-10-28 흡수 의미 정합 검토 발견 사항 처리
  - 상태 상세: 의미 감사, 약식 규칙의 자리, 상류 규범과의 관계 등재는 처리했다. 남은 것은 태그 어휘 정리안(사용자 결정 대기)과 정식 규약에 없는 상류 약식 규칙 조항(등재만 유지)이다.
  - [x] 흡수 뒤 의미 감사를 받고 상태 레지스트리를 갱신한다
    - 설명: 독립 감사 에이전트가 338370d부터 c81f60c까지의 흡수 이후 상태(main c51422d)를 감사했다. 판정은 조건부 clean이며, 승인이 필요 없는 지적은 이 흡수 단위에서 반영하고 태그 정리안은 아래 노드에 받았다. 9778a7a 흡수 뒤에는 전체 재감사 없이 감사가 짚은 머지 뒤 점검만 한다.
  - [ ] 이 레포 문서의 태그 어휘 정리안을 정한다
    - 설명: 의미 감사의 병합안과 삭제안을 사용자가 승인한 것만 바꾼다 (ref: [tags.md](../AGENTS/epistemic-rules/tags.md) "어휘 정리"). 옛 첫 항목 규칙에서 온 범주 이름 태그를 남길지, `규약`과 상류 `규칙`의 표기 갈림 등이 후보다.
    - 상태 상세: 2026-10-28 의미 감사가 아래 네 안을 냈고 모두 사용자 결정 대기다. 명령은 모두 `python3 AGENTS/epistemic-rules/tools/retag.py`로 시작한다. `retag.py`는 `implementation/` 하위 문서를 보지 않으므로 바뀌는 태그가 그 문서에도 있으면 손으로 고친다.
    - [ ] `규약`과 상류 `규칙`을 합칠지 정한다
      - 설명: `규약` 2건(plain-prose-rules.md, formal-and-short-rules.md), `규칙` 19건. 이 레포 온톨로지가 정식 규약과 약식 규칙을 다른 개념으로 정의하므로 합치면 그 구분이 태그에서 사라진다. 감사자는 둘 다 두고 `AGENTS/tag-vocabulary.md`를 새로 두어 합치지 않는 이유를 적는 안을 권한다(감사자 판단). 후속 과제 분류는 상류 고정 태그 `규칙`으로 합치는 안을 권했다(AI 제안). 합친다면 `--map 규약=규칙`.
    - [ ] 범주 이름 태그를 둘지 정한다
      - 설명: 옛 첫 항목 규칙에서 온 `architecture` 8건, `knowledge` 7건, `ontology` 7건, `strategy` 6건, `implementation/` 하위의 `implementation` 5건. 현 태그 규약은 위치만을 이유로 달거나 빼지 않는다. 각 문서가 그 범주라는 의미 단위에 속하면 두고, 위치만으로 붙었으면 범주별로 경로를 한정해 뺀다(예: `--drop knowledge --path epistemic-structure/knowledge`). 같은 이름 폴더를 소개하는 부모 문서에서 뺄지는 따로 정한다. 감사자는 한쪽을 권하지 않았고, 후속 과제 분류는 걸렀을 때 의미 있는 묶음인지로 판정하라고 권했다(AI 제안).
    - [ ] 묶음을 만들지 않는 단일 사용 태그 다섯을 뺄지 정한다
      - 설명: `정식`, `약식`(formal-and-short-rules.md, 같은 문서의 `규약`이 묶음을 맡는다), `검토`(일반어), `출력스타일`(같은 문서의 `외부지침`이 묶음을 맡는다), `프로젝트`(일반어). 감사자는 삭제를 권한다(감사자 판단). 실행 전 `--drop 정식 --drop 약식 --drop 검토 --drop 출력스타일 --drop 프로젝트 --dry-run`으로 확인한다.
    - [ ] `링크`를 `참조`로 합칠지 정한다
      - 설명: `링크` 1건(why-reference-markers-follow-reliance.md, 이미 `참조`도 단다). 이 레포의 참조 규약은 링크(형식)와 참조(기대는 관계)를 구분해 엄밀한 동의어가 아니다. 감사자는 병합안을 내면서 확실하지 않음으로 표시했다. 합치면 `--map 링크=참조`에 더해 implementation/reference-notation/reference-markers.md를 손으로 고친다.
  - [x] 정식 규약 문서와 상류 규범의 관계를 "이 워크스페이스의 규범"에 등재할지 정한다
    - 설명: [category-placement.md](../epistemic-structure/architecture/category-placement.md)는 상류 "판별 규칙"에 보태는 배치이고, 이 레포 자신의 문서를 쓸 때 [plain-prose-rules.md](../epistemic-structure/architecture/plain-prose-rules.md)와 상류 약식 규칙이 어긋나면 어느 쪽을 따를지 정한 곳이 없다. 루트 [AGENTS.md](../AGENTS.md)의 두 읽는 시점 문장을 규범 절로 옮길지도 함께 정한다 (ref: [instance-specialization.md](../AGENTS/epistemic-rules/instance-specialization.md) "특수화 방식").
    - 상태 상세: 후속 과제 분류의 권고안대로 등재했다. category-placement.md는 상류 "판별 규칙"에 대한 보탬으로 [epistemic-structure/AGENTS.md](../epistemic-structure/AGENTS.md)에, plain-prose-rules.md는 이 레포 자신의 평서문 기록에서 상류 약식 규칙의 겹치는 조항을 대체하는 것으로 루트 AGENTS.md에 두었다. 정식 규약에 없는 상류 조항은 상류를 따른다. 두 읽는 시점 문장은 규범 절로 옮겼다.
  - [x] 스캐폴드 약식 규칙의 범위 서술을 상류 재배치에 맞춘다
    - 설명: [formal-and-short-rules.md](../epistemic-structure/ontology/formal-and-short-rules.md)와 루트 AGENTS.md가 스캐폴드 약식 규칙을 `writing-style.md` 하나로 부른다. 상류는 늘 읽히는 핵심을 `communication.md`로 옮겼다. 온톨로지 정의라 관련 문서와의 정합도 함께 본다.
    - 상태 상세: 약식 규칙의 자리를 `communication.md`의 세 절과 `writing-style.md`, 그 하위 문서로 고쳤고, 루트 AGENTS.md는 파일 이름 대신 그 자리를 가리킨다. 이 정의를 인용하는 문서는 이름으로만 불러 고칠 것이 없었다.
  - [ ] 정식 규약에 없는 상류 약식 규칙 조항을 들일지 정한다
    - 설명: 흡수 전부터의 차이다. 줄임말 회피(레포가 걸리는지 포함), 말줄임표와 둥근 따옴표의 ASCII 치환, 코드 블록 절제, 절 참조 형식, 결격 대응, 비속어 금지, 에러 메시지 첫 문장 영문. 9778a7a 흡수로 상류 [reference-markers.md](../AGENTS/epistemic-rules/writing-style/reference-markers.md)가 표지 생략 대상인 색인 성격의 목록에 규범 요지가 상황별로 읽을 문서를 안내하는 목록(`상황 -> [문서](경로)`)을 더하고, 그 목록의 상황과 대상을 잇는 화살표는 표지로 바꾸지 않는다고 더했다. 정식 규약 [reference-markers.md](../implementation/reference-notation/reference-markers.md)에는 두 조항이 없고, 색인 성격의 목록 예시 문언도 갈린다(정식은 화자 노드가 의견을 늘어놓은 목록, 약식은 인물이나 주제 문서가 관련 문서를 늘어놓은 목록). [plain-prose-rules.md](../epistemic-structure/architecture/plain-prose-rules.md)의 색인 목록 열거도 같이 본다. 동기화 방향의 난점이 풀리기 전에는 등재만 한다.
    - 상태 상세: 등재만 유지한다(사용자 결정, 2026-10-28). 정식 규약에 들이지 않은 상류 조항은 이 레포 자신의 문서에서 상류대로 따른다(루트 AGENTS.md "이 워크스페이스의 규범").

- [x] 스캐폴드 9778a7a 흡수 (문언 정정, 감사 도구, 워크플로 판 고정)
  - 설명: 상류 변경이 위 2026-10-28 노드의 항목(설계 원칙의 강타입 범위, 약식 규칙의 상황별 안내 목록 조항, 주기 표의 행 단위 덮어쓰기)과 맞물려 같은 브랜치에서 함께 처리한다. 흡수 전에 의미 감사 결과를 먼저 기록한다.
  - 상태 상세: 범주 부모 문서 셋과 작업 트리의 충돌은 이 레포 문장을 지키고 날짜 처리 노드에 상류 새 절 안내만 들였다. 지운 출고 샘플은 되살아나지 않았다. 이 레포 고유 문서에 옮겨진 감사자 절차나 강타입 덮어쓰기를 가리키는 문장은 없었다.
