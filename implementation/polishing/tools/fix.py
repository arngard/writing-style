#!/usr/bin/env python3
"""기계 규칙을 글에 적용한다.

사용: python fix.py [INPUT] [--write | --dry-run] [--format text|json]
                    [--lines A-B] [--path-hint PATH] [--root DIR]

- INPUT은 파일 경로나 '-'(표준 입력, 기본값)다. UTF-8만 받는다.
- 기본: 고친 글을 표준 출력으로 낸다. 입력의 BOM 여부와 줄바꿈(LF, CRLF)을 그대로 둔다.
- --dry-run: 바뀔 곳만 보이고 글을 내지 않는다.
- --write: 원본 파일을 고친다. 같은 폴더의 임시 파일에 쓴 뒤 교체한다. 읽은 뒤
  원본이 바뀌었으면 쓰지 않는다. 심볼릭 링크는 고치지 않고 오류로 끝낸다.
  바뀔 곳 목록을 표준 출력으로 낸다.
- --lines A-B: 입력 글의 줄 범위. 영역은 글 전체로 판별하고, 그 범위 안에 완전히
  든 일치만 고친다. 범위가 글의 줄 수를 넘으면 도구 오류다.
- 기계 규칙은 <루트>/implementation/polishing/mechanical/*.json이고 산문 영역에만
  적용한다. 규칙 문서는 읽지 않는다.
- 대상이 레포 루트 바로 아래 reference/<자료> 안의 원본이면(--path-hint나 파일
  경로로 판정) 고치지 않는다.

종료 코드: 0 성공, 2 도구 오류(규칙 읽기 실패, 입력이나 출력 실패, 잘못된 인자).
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _polishing_core as core  # noqa: E402


def _change_dicts(changes):
    return [
        {"rule": c.rule, "line": c.line, "column": c.column,
         "before": c.before, "after": c.after, "note": c.note, "context": c.context}
        for c in changes
    ]


def _report(label, changes, fmt):
    if fmt == "json":
        core.write_stdout(core.to_json({"path": label, "changes": _change_dicts(changes)}))
        return
    lines = [f"{label}:{c.line}:{c.column}: [{c.rule}] {c.before!r} -> {c.after!r}"
             for c in changes]
    core.write_stdout("".join(line + "\n" for line in lines))


def _check_unchanged(path: Path, original: bytes) -> None:
    if path.is_symlink():
        raise core.ToolError(f"Refusing to write a symbolic link. 심볼릭 링크는 고치지 않는다: {path}")
    try:
        current = path.read_bytes()
    except OSError as e:
        raise core.ToolError(f"Cannot re-read file. 쓰기 전에 원본을 다시 읽지 못했다: {path} ({e})")
    if current != original:
        raise core.ToolError(
            f"File changed after reading. 읽은 뒤 원본이 바뀌어 쓰지 않았다: {path}")


def _atomic_write(path: Path, original: bytes, data: bytes) -> None:
    """같은 폴더의 임시 파일에 쓴 뒤, 원본이 읽은 때와 같은지 확인하고 교체한다.

    확인은 임시 파일을 다 쓴 뒤 교체 직전에 한 번 더 한다. 확인과 교체 사이의 짧은
    구간에 다른 프로세스가 쓰는 경우는 막지 못한다. 파일 잠금은 운영체제마다 달라
    표준 라이브러리만으로 일관되게 걸 수 없기 때문이다.
    """
    _check_unchanged(path, original)
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".", suffix=".tmp")
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.chmod(tmp, os.stat(path).st_mode & 0o7777)
        except OSError:
            pass
        _check_unchanged(path, original)
        os.replace(tmp, str(path))
        tmp = None
    except OSError as e:
        raise core.ToolError(f"Cannot write file. 원본을 교체하지 못했다: {path} ({e})")
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def run(args) -> int:
    root = core.root_from_args(args)
    if args.write and args.input == "-":
        raise core.ToolError("--write needs a file path. --write는 표준 입력에 쓸 수 없다")
    if args.write:
        p = Path(args.input)
        if p.is_symlink():
            raise core.ToolError(f"Refusing to write a symbolic link. 심볼릭 링크는 고치지 않는다: {p}")
    rules = core.load_all_mechanical(root)
    doc = core.read_input(args.input)
    if args.lines:
        core.range_span(doc.text, args.lines)
    if core.is_reference_material(args.path_hint, doc.path):
        core.warn(f"fix: reference 원본은 고치지 않는다: {args.path_hint or doc.label}")
        new_text, changes = doc.text, []
    else:
        new_text, changes = core.apply_mechanical(doc.text, rules, args.lines)
    label = args.path_hint or doc.label
    if args.dry_run:
        _report(label, changes, args.format)
        return 0
    if args.write:
        if changes:
            _atomic_write(doc.path, doc.raw, core.encode_text(new_text, doc.bom))
        _report(label, changes, args.format)
        return 0
    core.write_stdout_bytes(core.encode_text(new_text, doc.bom))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="기계 규칙을 산문 영역에 적용한다")
    parser.add_argument("input", nargs="?", default="-", help="입력 파일(기본 '-': 표준 입력)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="원본 파일을 고친다")
    mode.add_argument("--dry-run", action="store_true", help="바뀔 곳만 보인다")
    core.add_lines_arg(parser, "입력 글")
    core.add_common_args(parser)
    args = parser.parse_args(argv)
    try:
        return run(args)
    except core.ToolError as e:
        core.warn(f"fix: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
