"""시험 공용 도우미. 시험 자료는 모두 이 파일과 시험 파일에서 만든 예문이다."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOLS.parents[2]
sys.path.insert(0, str(TOOLS))

import _polishing_core as core  # noqa: E402

MARKER_FORM = REPO_ROOT / core.MECHANICAL_DIR_REL / "marker-form.json"


def kinds(text):
    """(영역 이름, 내용) 목록."""
    return [(r.kind, text[r.start:r.end]) for r in core.segment(text)]


def kind_of(text, needle, occurrence=0):
    """needle의 occurrence번째 출현 위치의 영역 이름."""
    pos = -1
    for _ in range(occurrence + 1):
        pos = text.index(needle, pos + 1)
    return core.region_at(core.segment(text), pos)


def run_tool(name, args, stdin=b"", cwd=None):
    """도구를 서브프로세스로 실행하고 (종료 코드, 표준 출력 바이트, 표준 오류 문자열)."""
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    proc = subprocess.run(
        [sys.executable, "-B", str(TOOLS / name)] + list(args),
        input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=cwd or str(TOOLS), env=env, timeout=120,
    )
    return proc.returncode, proc.stdout, proc.stderr.decode("utf-8", "replace")


RULE_DOC_VOCAB = """---
date created: 2026-11-23
date modified: 2026-11-23
tags: [시험]
description: 시험용 규칙 문서
---

# 어휘

## 예시 낱말을 쓰지 않는다 `sample-word`

예시 낱말 "가나다"를 쓰지 않는다.

### 후보 검출 패턴

```regex
가나다
```

### 설명

- [vocabulary.md](../../../implementation/polishing/explanations/vocabulary.md) "예시 낱말"

## 들여쓴 패턴 규칙 `indented-pattern`

본문.

### 후보 검출 패턴

    라마바

```
## 펜스 안 제목은 절이 아니다
```
"""

RULE_DOC_REFERENCE = """---
date created: 2026-11-23
date modified: 2026-11-23
tags: [시험]
description: 시험용 규칙 문서
---

# 참조

## 표지 형태 `marker-form`

형태는 소문자 표지, 콜론, 공백 한 칸, 링크다.

### 기계 규칙

- [marker-form.json](../../../implementation/polishing/mechanical/marker-form.json)
"""

RULE_DOC_PRINCIPLES = """---
date created: 2026-11-23
date modified: 2026-11-23
tags: [시험]
description: 시험용 윤문 원칙
---

# 윤문 원칙

## 원문의 근거를 지킨다 `keep-grounds`

고친 뒤에는 원문과 대조한다.
"""

EXPLANATION_VOCAB = """---
date created: 2026-11-23
date modified: 2026-11-23
tags: [시험]
description: 시험용 설명 문서
---

# 어휘 설명

## 예시 낱말

규칙: `sample-word`

| 고치기 전 | 고친 뒤 |
|---|---|
| 가나다 | 라마바 |
"""


class Fixture:
    """임시 레포 루트. 규칙 문서, 설명 문서, 기계 규칙을 만든다."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()

    def cleanup(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))
        return p

    def rules(self, name, text):
        return self.write(f"{core.RULES_DIR_REL}/{name}.md", text)

    def copy_marker_form(self):
        dst = self.root / core.MECHANICAL_DIR_REL / "marker-form.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(MARKER_FORM), str(dst))
        return dst

    def standard(self):
        """원칙, 어휘, 참조 규칙 문서와 설명 문서, 기계 규칙을 둔다."""
        self.rules("polishing-principles", RULE_DOC_PRINCIPLES)
        self.rules("vocabulary", RULE_DOC_VOCAB)
        self.rules("reference", RULE_DOC_REFERENCE)
        self.write(f"{core.EXPLANATIONS_DIR_REL}/vocabulary.md", EXPLANATION_VOCAB)
        self.copy_marker_form()
