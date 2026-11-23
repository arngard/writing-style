"""감사 확장: 윤문 규칙 구성 검사.

계약은 AGENTS/epistemic-rules/audit-extensions.md다. `python -B polishing_rules.py <루트>`로
실행하고, 발견 하나를 한 줄의 JSON 객체(severity, path, message)로 표준 출력에 낸다.
읽기만 한다.

검사:
1. 규칙 이름: 규칙 문서(epistemic-structure/architecture/plain-prose-rules/*.md) 가운데
   이름 붙은 절이 하나라도 있는 문서에서, 이름 없는 `##` 절(누락)과 케밥 케이스가 아닌
   이름을 위반으로 낸다. 같은 이름이 둘 이상이면(중복) 위반이다.
2. 후보 검출 패턴: 컴파일되지 않는 정규식과 정규식 없는 `### 후보 검출 패턴`은 위반이다.
3. 기계 규칙: 규칙의 `### 기계 규칙` 링크 대상이 없거나, 읽지 못하거나, `rule` 값이
   규칙 이름과 다르면 위반이다. 기계 규칙 폴더의 JSON은 읽지 못하면 위반이고, 그
   `rule` 값의 규칙이 없거나 그 규칙이 이 파일로 링크하지 않으면 미결 발견이다.
4. 설명: 규칙의 `### 설명` 링크 대상 문서가 없거나, 지정한 절이 없거나, 그 절의
   `규칙:` 줄이 규칙 이름과 다르면 위반이다. 설명 문서 절의 `규칙:` 값의 규칙이 없으면
   미결 발견이고, 규칙은 있는데 그 규칙의 설명 링크가 이 절을 가리키지 않으면 위반이다.
5. 링크: implementation/polishing/ 안 Markdown 문서의 산문 영역 링크(코드와 인용 안은
   제외) 대상이 없으면 위반이다. 다만 대상이 규칙 문서 폴더나 설명 문서 폴더 안이면
   미결 발견이다.

미결 발견은 규칙 문서 이전이 끝나기 전에는 경고, 끝난 뒤에는 위반이다. 이전이 끝난
상태는 core.RULE_DOC_NAMES의 규칙 문서가 모두 있고 규칙 문서 폴더의 모든 문서에 이름
붙은 절이 있는 상태다. 규칙 문서를 옮기는 동안(옛 형태 문서와 아직 없는 문서가 섞인
동안) 감사가 위반으로 막지 않게 하려는 것이다.

공용 파서는 이 파일이 든 레포의 implementation/polishing/tools/_polishing_core.py에서
가져온다. 그 모듈이 없으면 아무것도 내지 않는다.
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_TOOLS = _HERE.parents[2] / "implementation" / "polishing" / "tools"


def _emit(severity, path, message):
    print(json.dumps({"severity": severity, "path": path, "message": message}))


def _rel(root, path):
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _is_under(path, folder):
    try:
        path.resolve().relative_to(folder.resolve())
        return True
    except ValueError:
        return False


def check(root, core):
    findings = []

    def add(sev, path, msg):
        findings.append((sev, path, msg))

    rules_dir = root / core.RULES_DIR_REL
    expl_dir = root / core.EXPLANATIONS_DIR_REL
    mech_dir = root / core.MECHANICAL_DIR_REL
    polishing_dir = root / core.POLISHING_DIR_REL

    docs = []
    for p in core.rule_doc_paths(root):
        try:
            docs.append(core.parse_rule_doc(p))
        except core.ToolError as e:
            add("violation", _rel(root, p), f"규칙 문서를 읽지 못했다: {e}")
    present = {d.stem for d in docs}
    complete = all(n in present for n in core.RULE_DOC_NAMES) and docs and all(d.named for d in docs)
    pending = "violation" if complete else "warning"
    pending_note = "" if complete else " (규칙 문서 이전 중이라 경고)"

    # 1. 규칙 이름
    rules = {}  # 이름 -> (doc, section)
    for d in docs:
        if not d.named:
            continue
        drel = _rel(root, d.path)
        for s in d.sections:
            if s.name_raw is None:
                add("violation", drel, f"{s.line}행 절 \"{s.title}\"에 규칙 이름이 없다")
                continue
            if s.name is None:
                add("violation", drel, f"{s.line}행 규칙 이름 `{s.name_raw}`가 영문 소문자 케밥 케이스가 아니다")
                continue
            if s.name in rules:
                other = rules[s.name]
                add("violation", drel, f"{s.line}행 규칙 이름 `{s.name}`이 중복된다"
                    f" (먼저 나온 곳: {_rel(root, other[0].path)}:{other[1].line})")
                continue
            rules[s.name] = (d, s)

    # 2. 후보 검출 패턴
    for name, (d, s) in rules.items():
        drel = _rel(root, d.path)
        if s.has_patterns_heading and not s.patterns:
            add("violation", drel, f"`{name}`의 후보 검출 패턴 절에 정규식이 없다")
        for pat in s.patterns:
            if pat.error:
                add("violation", drel, f"{pat.line}행 `{name}`의 정규식이 컴파일되지 않는다: {pat.error}")

    # 3. 기계 규칙
    mech_linked = {}  # 해석한 경로 -> 규칙 이름들
    loaded = {}
    for name, (d, s) in rules.items():
        drel = _rel(root, d.path)
        for link in s.mechanical_links:
            target = core.resolve_link(d.path, link.target)
            if target is None or not target.is_file():
                add("violation", drel, f"{link.line}행 `{name}`의 기계 규칙 링크 대상이 없다: {link.target}")
                continue
            mech_linked.setdefault(target, set()).add(name)
            try:
                rule = loaded.get(target) or core.load_mechanical(target)
                loaded[target] = rule
            except core.ToolError as e:
                add("violation", _rel(root, target), str(e))
                continue
            if rule.rule != name:
                add("violation", drel, f"{link.line}행 `{name}`의 기계 규칙 파일 rule 값이 `{rule.rule}`이다")
    if mech_dir.is_dir():
        for p in sorted(mech_dir.glob("*.json")):
            prel = _rel(root, p)
            try:
                rule = loaded.get(p.resolve()) or core.load_mechanical(p)
            except core.ToolError as e:
                add("violation", prel, str(e))
                continue
            if rule.rule not in rules:
                add(pending, prel, f"rule 값 `{rule.rule}`의 규칙 절이 규칙 문서에 없다{pending_note}")
            elif rule.rule not in mech_linked.get(p.resolve(), set()):
                add(pending, prel, f"규칙 `{rule.rule}`의 기계 규칙 절이 이 파일로 링크하지 않는다{pending_note}")

    # 4. 설명
    expl_cache = {}

    def expl_sections(path):
        if path not in expl_cache:
            try:
                expl_cache[path] = core.parse_explanation_doc(path)
            except core.ToolError as e:
                add("violation", _rel(root, path), f"설명 문서를 읽지 못했다: {e}")
                expl_cache[path] = []
        return expl_cache[path]

    expl_linked = set()  # (경로, 절 제목, 규칙 이름)
    for name, (d, s) in rules.items():
        drel = _rel(root, d.path)
        for link in s.explanation_links:
            target = core.resolve_link(d.path, link.target)
            if target is None or not target.is_file():
                add("violation", drel, f"{link.line}행 `{name}`의 설명 링크 대상이 없다: {link.target}")
                continue
            if not link.section_title:
                add("violation", drel, f"{link.line}행 `{name}`의 설명 링크 뒤에 큰따옴표 절 제목이 없다")
                continue
            expl_linked.add((target, link.section_title, name))
            matches = [e for e in expl_sections(target) if e.title == link.section_title]
            if not matches:
                add("violation", drel, f"{link.line}행 `{name}`의 설명 절 \"{link.section_title}\"이"
                    f" {_rel(root, target)}에 없다")
            elif not any(name in e.rules for e in matches):
                add("violation", drel, f"{link.line}행 `{name}`의 설명 절 \"{link.section_title}\"의"
                    f" 규칙 줄이 `{name}`이 아니다")
    if expl_dir.is_dir():
        for p in sorted(expl_dir.glob("*.md")):
            if p.name in core.NON_RULE_FILES or core.INDEX_PAGE_RE.match(p.name):
                continue
            prel = _rel(root, p)
            for e in expl_sections(p.resolve()):
                for rule_name in e.rules:
                    if rule_name not in rules:
                        add(pending, prel, f"{e.line}행 절 \"{e.title}\"의 규칙 `{rule_name}`이"
                            f" 규칙 문서에 없다{pending_note}")
                    elif (p.resolve(), e.title, rule_name) not in expl_linked:
                        add("violation", prel, f"{e.line}행 절 \"{e.title}\"을 규칙 `{rule_name}`의"
                            " 설명 링크가 가리키지 않는다")

    # 5. implementation/polishing/ 안 문서의 링크
    if polishing_dir.is_dir():
        for p in sorted(polishing_dir.rglob("*.md")):
            if not p.is_file() or any(part.startswith(".") or part == "__pycache__"
                                      for part in p.relative_to(polishing_dir).parts):
                continue
            prel = _rel(root, p)
            try:
                text = core.read_text_file(p)
            except core.ToolError as e:
                add("violation", prel, str(e))
                continue
            regions = core.segment(text)
            index = core.LineIndex(text)
            for link in core.extract_links(text, regions):
                target = core.resolve_link(p, link.target)
                if target is None or target.exists():
                    continue
                line = index.line_col(link.start)[0]
                if _is_under(target, rules_dir) or _is_under(target, expl_dir):
                    add(pending, prel, f"{line}행 링크 대상이 아직 없다: {link.target}{pending_note}")
                else:
                    add("violation", prel, f"{line}행 링크 대상이 없다: {link.target}")
    return findings


def main(argv):
    if len(argv) != 2:
        print("usage: polishing_rules.py <root>. 루트 경로 하나를 받는다", file=sys.stderr)
        return 2
    root = Path(argv[1]).resolve()
    if not (_TOOLS / "_polishing_core.py").is_file():
        return 0
    sys.path.insert(0, str(_TOOLS))
    import _polishing_core as core
    for sev, path, msg in check(root, core):
        _emit(sev, path, msg)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
