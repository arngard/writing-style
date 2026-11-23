#!/usr/bin/env python3
"""기계 규칙 위반과 후보 검출 패턴 위치를 리포트한다. 글을 고치지 않는다.

사용: python detect.py [INPUT ...] [--format text|json] [--path-hint PATH] [--root DIR]

- INPUT은 파일 경로나 '-'(표준 입력)다. 없으면 표준 입력을 읽는다. UTF-8만 받는다.
- 위반(violation): 기계 규칙(<루트>/implementation/revision/mechanical/*.json)이
  산문 영역에서 고칠 곳. fix.py가 바꿀 곳과 같다.
- 후보(candidate): 규칙 문서(<루트>/epistemic-structure/architecture/plain-prose-rules/)
  의 이름 붙은 규칙 절 `### 후보 검출 패턴` 코드 블록의 정규식(한 줄에 하나)이
  일치한 곳. 모든 영역에서 찾고 영역 이름을 함께 보고한다. 고칠지는 의미 검토가 정한다.
- 대상이 레포 루트 바로 아래 reference/<자료> 안의 원본이면 아무것도 보고하지 않는다.

텍스트 결과 한 줄: <경로>:<줄>:<열>: <violation|candidate> [<규칙 이름>] <일치> (<영역>)

종료 코드: 0 위반 없음(후보만 있어도 0), 1 위반 있음, 2 도구 오류.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _revision_core as core  # noqa: E402


def find_candidates(text, patterns, root):
    """후보 검출 패턴의 일치를 영역과 함께 돌려준다."""
    regions = core.segment(text)
    index = core.LineIndex(text)
    out = []
    for doc, sec, pat in patterns:
        for m in pat.compiled.finditer(text):
            if m.end() == m.start():
                continue
            line, col = index.line_col(m.start())
            try:
                doc_rel = doc.path.resolve().relative_to(root).as_posix()
            except ValueError:
                doc_rel = doc.path.as_posix()
            out.append({
                "rule": sec.name, "line": line, "column": col, "match": m.group(0),
                "region": core.region_at(regions, m.start()), "pattern": pat.source,
                "doc": doc_rel, "context": index.context(m.start(), m.end()),
            })
    out.sort(key=lambda d: (d["line"], d["column"], d["rule"]))
    return out


def detect_text(text, rules, patterns, root):
    _new, changes = core.apply_mechanical(text, rules)
    violations = [
        {"rule": c.rule, "line": c.line, "column": c.column, "match": c.before,
         "suggestion": c.after, "region": core.PROSE, "note": c.note, "context": c.context}
        for c in changes
    ]
    return violations, find_candidates(text, patterns, root)


def run(args) -> int:
    root = core.root_from_args(args)
    rules = core.load_all_mechanical(root)
    patterns = core.compiled_patterns(core.load_rule_docs(root))
    inputs = args.inputs or ["-"]
    results = []
    any_violation = False
    for arg in inputs:
        doc = core.read_input(arg)
        label = args.path_hint or doc.label
        if core.is_reference_material(args.path_hint, doc.path):
            core.warn(f"detect: reference 원본은 검사하지 않는다: {label}")
            violations, candidates = [], []
        else:
            violations, candidates = detect_text(doc.text, rules, patterns, root)
        any_violation = any_violation or bool(violations)
        results.append({"path": label, "violations": violations, "candidates": candidates})
    if args.format == "json":
        core.write_stdout(core.to_json(results))
    else:
        lines = []
        for r in results:
            for v in r["violations"]:
                lines.append(f"{r['path']}:{v['line']}:{v['column']}: violation [{v['rule']}] "
                             f"{v['match']!r} -> {v['suggestion']!r} ({v['region']})")
            for c in r["candidates"]:
                lines.append(f"{r['path']}:{c['line']}:{c['column']}: candidate [{c['rule']}] "
                             f"{c['match']!r} ({c['region']})")
        core.write_stdout("".join(line + "\n" for line in lines))
    return 1 if any_violation else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="기계 규칙 위반과 후보 위치를 보고한다")
    parser.add_argument("inputs", nargs="*", help="입력 파일(없거나 '-'면 표준 입력)")
    core.add_common_args(parser)
    args = parser.parse_args(argv)
    try:
        return run(args)
    except core.ToolError as e:
        core.warn(f"detect: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
