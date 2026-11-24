#!/usr/bin/env python3
"""고치기 전과 뒤의 글을 대조해 변경을 보고한다.

사용: python check_preservation.py BEFORE AFTER [--mechanical] [--lines A-B] [--format text|json]

- BEFORE, AFTER는 파일 경로이고 둘 가운데 하나는 '-'(표준 입력)일 수 있다. UTF-8만 받는다.
- 비교 항목: 숫자(산문 영역), URL, 링크 대상(참조형 링크 정의 포함), 인라인 코드,
  코드 블록(펜스와 들여쓴 코드), 인용 블록, front matter 값. 항목마다 값과 출현
  횟수를 전후로 비교하고, 달라진 값마다 위치(줄:열)와 같은 줄의 앞뒤 문맥을 보고한다.
  줄어든 값은 BEFORE의 위치, 늘어난 값은 AFTER의 위치다.
- --mechanical: 기계 수정 단계의 대조다. 산문이 아닌 영역(front matter, 코드,
  인라인 코드, 인용, 링크 대상, 참조형 링크 정의, URL, HTML)의 내용이 바뀌었으면
  채택 금지다. 기계 수정은 산문만 고치므로 그 경우는 도구의 결함이다.
- --lines A-B: 범위 윤문의 대조다. A-B는 BEFORE의 줄 범위다. BEFORE의 1..A-1줄과
  B+1..끝줄이 AFTER의 처음과 끝에 그대로 있는지(BOM 여부 포함) 보고, 아니면 채택
  금지다. 통과하면 AFTER에서의 현재 범위를 보고한다. 범위의 줄을 모두 지웠으면
  현재 범위는 없음이다. 이후 단계의 --lines에는 이 현재 범위를 쓴다.
- 문체(평어체, 존댓말)는 보지 않는다.

종료 코드: 0 변경 없음, 1 확인할 변경 있음, 3 채택 금지(--mechanical에서 산문이
아닌 영역이 바뀜, --lines에서 범위 밖이 바뀜), 2 도구 오류.
"""

import argparse
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _polishing_core as core  # noqa: E402

_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*")
_FM_LINE_RE = re.compile(r"^([A-Za-z_][\w -]*?)\s*:\s?(.*)$")

CATEGORIES = ("number", "url", "link_target", "inline_code", "code_block", "quote",
              "front_matter")


def _norm(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")


def collect_items(text: str):
    """항목 이름 -> [(값, 시작, 끝)] 목록."""
    regions = core.segment(text)
    items = OrderedDict((c, []) for c in CATEGORIES)
    for r in regions:
        chunk = text[r.start:r.end]
        if r.kind == core.PROSE:
            for m in _NUMBER_RE.finditer(text, r.start, r.end):
                items["number"].append((m.group(0), m.start(), m.end()))
        elif r.kind == core.URL:
            value = chunk[1:-1] if chunk.startswith("<") and chunk.endswith(">") else chunk
            items["url"].append((value, r.start, r.end))
        elif r.kind == core.INLINE_CODE:
            items["inline_code"].append((_norm(chunk), r.start, r.end))
        elif r.kind in (core.CODE_FENCE, core.INDENTED_CODE):
            items["code_block"].append((_norm(chunk).rstrip("\n"), r.start, r.end))
        elif r.kind == core.QUOTE:
            items["quote"].append((_norm(chunk).rstrip("\n"), r.start, r.end))
        elif r.kind == core.FRONT_MATTER:
            pos = r.start
            for line in chunk.splitlines(keepends=True):
                body = line.rstrip("\r\n")
                if body.strip() not in ("---", "...", ""):
                    m = _FM_LINE_RE.match(body)
                    value = f"{m.group(1)}: {m.group(2).strip()}" if m else body.rstrip()
                    items["front_matter"].append((value, pos, pos + len(body)))
                pos += len(line)
    for link in core.extract_links(text, regions):
        items["link_target"].append((link.target, link.start, link.end))
    return items, regions


def compare(before: str, after: str):
    b_items, b_regions = collect_items(before)
    a_items, a_regions = collect_items(after)
    b_index, a_index = core.LineIndex(before), core.LineIndex(after)
    diffs = []
    for cat in CATEGORIES:
        bc = Counter(v for v, _s, _e in b_items[cat])
        ac = Counter(v for v, _s, _e in a_items[cat])
        for value in list(OrderedDict.fromkeys([v for v, _s, _e in b_items[cat]]
                                               + [v for v, _s, _e in a_items[cat]])):
            if bc[value] == ac[value]:
                continue
            side, occ, index = ("before", b_items[cat], b_index) if bc[value] > ac[value] \
                else ("after", a_items[cat], a_index)
            locations = []
            for v, s, e in occ:
                if v != value:
                    continue
                line, col = index.line_col(s)
                locations.append({"line": line, "column": col, "context": index.context(s, e)})
            diffs.append({"item": cat, "value": value, "before_count": bc[value],
                          "after_count": ac[value], "side": side, "locations": locations})
    b_non = [(r.kind, _norm(before[r.start:r.end])) for r in b_regions if r.kind != core.PROSE]
    a_non = [(r.kind, _norm(after[r.start:r.end])) for r in a_regions if r.kind != core.PROSE]
    return diffs, b_non != a_non


def check_range(before, after, lines):
    """범위 밖 보존을 확인하고 고친 글에서의 현재 범위를 돌려준다.

    BEFORE를 앞부분(1..A-1줄), 편집 구간, 뒷부분(B+1..끝줄)으로 나누고, 앞뒤 부분이
    겹치지 않게 AFTER의 처음과 끝에 그대로 있는지 본다. 반환은 (보존 여부, 현재 범위
    또는 None(편집 구간이 비었음)).
    """
    start, end = core.range_span(before.text, lines)
    prefix, suffix = before.text[:start], before.text[end:]
    text = after.text
    kept = (before.bom == after.bom and len(text) >= len(prefix) + len(suffix)
            and text.startswith(prefix) and text.endswith(suffix))
    if not kept:
        return False, None
    middle = text[len(prefix):len(text) - len(suffix)]
    # 뒷부분이 있는데 편집 구간이 줄바꿈으로 끝나지 않으면 뒷부분의 첫 줄과 이어 붙는다.
    if suffix and middle and not middle.endswith("\n"):
        return False, None
    count = core.line_count(middle)
    if count == 0:
        return True, None
    return True, core.LineRange(lines.first, lines.first + count - 1)


def run(args) -> int:
    if args.before == "-" and args.after == "-":
        raise core.ToolError("Only one input can be stdin. 표준 입력은 한쪽에만 쓸 수 있다")
    before = core.read_input(args.before)
    after = core.read_input(args.after)
    diffs, non_prose_changed = compare(before.text, after.text)
    blocked = args.mechanical and non_prose_changed
    outside_kept, current = True, None
    if args.lines:
        outside_kept, current = check_range(before, after, args.lines)
        blocked = blocked or not outside_kept
    if args.format == "json":
        data = {
            "before": before.label, "after": after.label, "mechanical": args.mechanical,
            "blocked": blocked, "non_prose_changed": non_prose_changed, "changes": diffs,
        }
        if args.lines:
            data["outside_kept"] = outside_kept
            data["range"] = ({"first": current.first, "last": current.last}
                             if current else None)
            data["insert_at"] = args.lines.first
        core.write_stdout(core.to_json(data))
    else:
        out = []
        if args.mechanical and non_prose_changed:
            out.append("채택 금지: 기계 수정 전후에 산문이 아닌 영역이 바뀌었다")
        if not outside_kept:
            out.append(f"채택 금지: 범위 {args.lines.first}-{args.lines.last}줄 밖이 바뀌었다")
        elif args.lines:
            out.append(f"현재 범위: {current.first}-{current.last}" if current
                       else f"현재 범위: 없음({args.lines.first}줄 자리)")
        for d in diffs:
            label = before.label if d["side"] == "before" else after.label
            out.append(f"[{d['item']}] {d['value']!r}: {d['before_count']} -> {d['after_count']}")
            for loc in d["locations"]:
                out.append(f"  {label}:{loc['line']}:{loc['column']}: {loc['context']}")
        core.write_stdout("".join(line + "\n" for line in out))
    if blocked:
        return 3
    return 1 if diffs else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="고치기 전과 뒤를 대조해 변경을 보고한다")
    parser.add_argument("before", help="고치기 전 글(파일이나 '-')")
    parser.add_argument("after", help="고친 뒤 글(파일이나 '-')")
    parser.add_argument("--mechanical", action="store_true",
                        help="기계 수정 단계 대조. 산문이 아닌 영역이 바뀌면 종료 코드 3")
    core.add_lines_arg(parser, "BEFORE")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="결과 형식(기본 text)")
    args = parser.parse_args(argv)
    try:
        return run(args)
    except core.ToolError as e:
        core.warn(f"check_preservation: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
