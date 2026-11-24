"""윤문 도구 공용 모듈.

네 도구(detect.py, fix.py, collect_review.py, check_preservation.py)와 감사 확장
(AGENTS/audit-checks/polishing_rules.py)이 함께 쓰는 부분을 담는다.

- 영역 판별(segment): 글을 구문 영역으로 나누고 위치를 돌려준다. 영역 이름은
  REGION_KINDS다. 판별하지 못한 구문(닫히지 않은 펜스, 닫히지 않은 front matter,
  짝 없는 백틱, 닫히지 않은 HTML 주석)은 그 뒤를 산문이 아닌 영역으로 본다.
  고치지 말아야 할 곳을 고치는 것보다 고칠 곳을 놓치는 편이 안전하기 때문이다.
- 규칙 문서 파서(parse_rule_doc): `## <제목> `<규칙 이름>`` 절, 그 아래
  `### 후보 검출 패턴`의 코드 블록(한 줄에 정규식 하나), `### 기계 규칙`과
  `### 설명`의 링크를 읽는다.
- 설명 문서 파서(parse_explanation_doc): 절 제목 바로 아래 `규칙: `<이름>`` 줄을 읽는다.
- 기계 규칙 파서(load_mechanical): JSON 파일 하나가 규칙 하나다.
- 기계 규칙 적용(apply_mechanical): 산문 영역 안에 완전히 든 일치만 바꾼다.

표준 라이브러리만 쓰고 Python 3.9에서 도는 문법만 쓴다.
"""

import bisect
import json
import re
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# 영역 이름.
FRONT_MATTER = "front_matter"
CODE_FENCE = "code_fence"
INDENTED_CODE = "indented_code"
INLINE_CODE = "inline_code"
QUOTE = "quote"
LINK_TARGET = "link_target"
REF_DEFINITION = "ref_definition"
URL = "url"
HTML = "html"
PROSE = "prose"
REGION_KINDS = (
    FRONT_MATTER, CODE_FENCE, INDENTED_CODE, INLINE_CODE, QUOTE,
    LINK_TARGET, REF_DEFINITION, URL, HTML, PROSE,
)

# 이 파일은 <루트>/implementation/polishing/tools/ 에 있다.
TOOLS_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = TOOLS_DIR.parents[2]
RULES_DIR_REL = "epistemic-structure/architecture/plain-prose-rules"
EXPLANATIONS_DIR_REL = "implementation/polishing/explanations"
MECHANICAL_DIR_REL = "implementation/polishing/mechanical"
POLISHING_DIR_REL = "implementation/polishing"
# 규칙 문서의 이름.
RULE_DOC_NAMES = (
    "vocabulary", "sentence", "format", "bullets-and-prose",
    "reference", "composition", "document-temporality", "polishing-principles",
)
# 모든 검토자가 함께 읽는 윤문 원칙 문서.
PRINCIPLES_DOC = "polishing-principles"
# 의미 수정의 검토 묶음(이름, 규칙 문서)과 수정안을 적용하는 순서. 윤문 원칙을 뺀
# 규칙 문서가 정확히 한 묶음에 든다. 문장 경계와 구성을 바꾸는 묶음을 먼저 적용해
# 뒤 묶음의 수정안이 바뀐 문장 위에 얹히게 한다.
REVIEW_BUNDLES = (
    ("structure", ("composition", "bullets-and-prose", "document-temporality")),
    ("wording", ("vocabulary", "sentence", "format")),
    ("reference", ("reference",)),
)
# 규칙 문서 폴더에서 규칙 문서가 아닌 파일.
NON_RULE_FILES = {"AGENTS.md", "CLAUDE.md"}
INDEX_PAGE_RE = re.compile(r"^INDEX(?:[2-9]|[1-9]\d+)?\.md$")

RULE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PATTERNS_HEADING = "후보 검출 패턴"
MECHANICAL_HEADING = "기계 규칙"
EXPLANATION_HEADING = "설명"


class ToolError(Exception):
    """도구 오류. 도구는 이 오류를 표준 오류에 내고 종료 코드 2로 끝난다."""


# ---------------------------------------------------------------- 입출력


@dataclass
class InputText:
    """읽은 글. text는 BOM을 뗀 문자열이고 줄바꿈은 원문 그대로다."""

    text: str
    bom: bool
    raw: bytes
    path: Optional[Path]  # 표준 입력이면 None
    label: str  # 보고에 쓰는 이름


def decode_utf8(raw: bytes, label: str) -> Tuple[str, bool]:
    """UTF-8 바이트를 문자열과 BOM 여부로 바꾼다. 실패하면 ToolError."""
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw[3:] if bom else raw
    try:
        return body.decode("utf-8"), bom
    except UnicodeDecodeError as e:
        raise ToolError(
            f"Input is not valid UTF-8. {label}: UTF-8로 읽지 못했다"
            f" (바이트 {e.start})"
        )


def read_input(arg: str) -> InputText:
    """파일 경로나 '-'(표준 입력)에서 글을 읽는다."""
    if arg == "-":
        try:
            raw = sys.stdin.buffer.read()
        except OSError as e:
            raise ToolError(f"Cannot read standard input. 표준 입력을 읽지 못했다: {e}")
        text, bom = decode_utf8(raw, "<stdin>")
        return InputText(text, bom, raw, None, "<stdin>")
    path = Path(arg)
    try:
        raw = path.read_bytes()
    except OSError as e:
        raise ToolError(f"Cannot read input file. 입력 파일을 읽지 못했다: {arg} ({e})")
    text, bom = decode_utf8(raw, arg)
    return InputText(text, bom, raw, path, arg)


def encode_text(text: str, bom: bool) -> bytes:
    """문자열을 UTF-8 바이트로 바꾸고 BOM 여부를 되살린다."""
    data = text.encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def write_stdout(text: str) -> None:
    """결과를 표준 출력에 UTF-8 바이트로 쓴다. 콘솔 인코딩과 줄바꿈 변환을 피한다."""
    write_stdout_bytes(text.encode("utf-8"))


def write_stdout_bytes(data: bytes) -> None:
    """바이트를 표준 출력에 쓴다. 실패하면 ToolError."""
    try:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    except OSError as e:  # BrokenPipeError 포함
        raise ToolError(f"Cannot write standard output. 표준 출력에 쓰지 못했다: {e}")


def warn(message: str) -> None:
    """진단을 표준 오류에 UTF-8로 쓴다. 표준 오류마저 쓸 수 없으면 조용히 넘긴다."""
    try:
        sys.stderr.buffer.write((message + "\n").encode("utf-8"))
        sys.stderr.buffer.flush()
    except OSError:
        pass


def to_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


# ---------------------------------------------------------------- 경로 예외


def _git_root(path: Path) -> Optional[Path]:
    for parent in [path] + list(path.parents):
        if (parent / ".git").exists():
            return parent
    return None


def is_reference_material(path_hint: Optional[str], input_path: Optional[Path]) -> bool:
    """대상 글이 레포 루트 바로 아래 reference/<자료> 안의 원본인지 판정한다.

    reference/ 아래 원본은 원형 부호를 그대로 쓰는 영역이고 고치지 않는 원본이다.
    대상 레포의 루트는 --path-hint가 상대 경로면 그 기준, 절대 경로나 실제 파일
    경로면 가장 가까운 .git이 있는 조상이다. 루트를 정하지 못하면 예외로 보지 않는다.
    reference/AGENTS/는 규범 폴더이고, reference/ 바로 아래의 디스크립터(AGENTS.md,
    CLAUDE.md)와 색인은 레포 자신의 문서라 예외가 아니다.
    """
    rel_parts: Optional[Tuple[str, ...]] = None
    if path_hint:
        hint = Path(path_hint)
        if not hint.is_absolute():
            rel_parts = tuple(p for p in hint.as_posix().split("/") if p not in ("", "."))
        else:
            input_path = hint
    if rel_parts is None and input_path is not None:
        absolute = input_path.resolve()
        root = _git_root(absolute.parent)
        if root is None:
            return False
        rel_parts = absolute.relative_to(root).parts
    if not rel_parts or len(rel_parts) < 2 or rel_parts[0] != "reference":
        return False
    if rel_parts[1] == "AGENTS":
        return False
    if len(rel_parts) == 2 and (rel_parts[1] in NON_RULE_FILES or INDEX_PAGE_RE.match(rel_parts[1])
                                or rel_parts[1] == "INDEX.yaml"):
        return False
    return True


# ---------------------------------------------------------------- 영역 판별


@dataclass(frozen=True)
class Region:
    kind: str
    start: int  # 글 안의 문자 위치(포함)
    end: int  # 문자 위치(제외)


class LineIndex:
    """문자 위치를 1부터 세는 줄과 열로 바꾼다."""

    def __init__(self, text: str):
        self.text = text
        self.starts = [0]
        for m in re.finditer("\n", text):
            self.starts.append(m.end())

    def line_col(self, offset: int) -> Tuple[int, int]:
        i = bisect.bisect_right(self.starts, offset) - 1
        return i + 1, offset - self.starts[i] + 1

    def line_text(self, line: int) -> str:
        start = self.starts[line - 1]
        end = self.starts[line] if line < len(self.starts) else len(self.text)
        return self.text[start:end].rstrip("\r\n")

    def context(self, start: int, end: int, width: int = 30) -> str:
        """일치 앞뒤의 같은 줄 문맥."""
        line, _ = self.line_col(start)
        ls = self.starts[line - 1]
        le = self.starts[line] if line < len(self.starts) else len(self.text)
        before = self.text[max(ls, start - width):start]
        after = self.text[end:min(le, end + width)].rstrip("\r\n")
        return before + "[[" + self.text[start:end] + "]]" + after


_FENCE_OPEN_RE = re.compile(r"^(`{3,}|~{3,})(.*)$")
_LIST_ITEM_RE = re.compile(r"^([-*+]|\d{1,9}[.)])([ \t]+|$)")
_HEADING_RE = re.compile(r"^#{1,6}(?:[ \t]|$)")
_HR_RE = re.compile(r"^(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$")
_REF_DEF_RE = re.compile(r"^\[(?!\^)(?:[^\]\\]|\\.)+\]:")
_HTML_BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "body", "caption", "center",
    "col", "colgroup", "dd", "details", "dialog", "div", "dl", "dt", "fieldset",
    "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6",
    "head", "header", "hr", "html", "iframe", "legend", "li", "main", "menu",
    "nav", "ol", "p", "pre", "script", "section", "style", "summary", "table",
    "tbody", "td", "textarea", "tfoot", "th", "thead", "tr", "ul",
}
_HTML_RAW_TAGS = {"pre", "script", "style", "textarea"}
_HTML_BLOCK_START_RE = re.compile(r"^</?([A-Za-z][A-Za-z0-9-]*)(?=[\s/>]|$)")
_HTML_SINGLE_TAG_LINE_RE = re.compile(
    r"^</?[A-Za-z][A-Za-z0-9-]*(?:\s+[^<>]*)?/?>\s*$")


def _indent_width(line: str) -> Tuple[int, int]:
    """줄 머리 들여쓰기의 폭(탭은 4칸 정렬)과 문자 수."""
    width = 0
    count = 0
    for ch in line:
        if ch == " ":
            width += 1
        elif ch == "\t":
            width += 4 - (width % 4)
        else:
            break
        count += 1
    return width, count


def _split_lines(text: str) -> List[Tuple[int, str, str]]:
    """(시작 위치, 줄바꿈을 뗀 내용, 줄바꿈 문자열) 목록."""
    out = []
    pos = 0
    for raw in text.splitlines(keepends=True):
        body = raw.rstrip("\r\n")
        # splitlines는 \x0b 등에서도 나누므로 실제 줄바꿈만 떼고 나머지는 본문으로 둔다.
        out.append((pos, body, raw[len(body):]))
        pos += len(raw)
    return out


_TITLE_CLOSERS = {'"': '"', "'": "'", "(": ")"}


_REF_LABEL_RE = re.compile(r"[ \t]{0,3}\[(?!\^)(?:[^\]\\\n]|\\.)+\]:")


@dataclass
class RefDefinition:
    target: str
    target_start: int
    target_end: int
    end: int  # 정의가 끝나는 줄의 끝(줄바꿈 포함) 위치


def _line_end(text: str, pos: int) -> int:
    """pos가 든 줄의 끝(줄바꿈 포함) 위치."""
    nl = text.find("\n", pos)
    return len(text) if nl < 0 else nl + 1


def _skip_blank_chars(text: str, p: int) -> int:
    while p < len(text) and text[p] in " \t":
        p += 1
    return p


# 글 중간 위치에서 쓰는 목록 표지(앵커 없음). '^'는 match(text, pos)의 pos에서 맞지 않는다.
_LIST_MARKER_AT_RE = re.compile(r"([-*+]|\d{1,9}[.)])([ \t]+|$)", re.MULTILINE)


def _content_start(text: str, pos: int) -> int:
    """줄 머리 pos에서 공백과 (여러 단계의) 목록 표지를 벗긴 내용의 시작 위치."""
    p = _skip_blank_chars(text, pos)
    while True:
        m = _LIST_MARKER_AT_RE.match(text, p)
        if not m or not m.group(2):
            return p
        p = _skip_blank_chars(text, m.end())


def parse_ref_definition(text: str, pos: int) -> Optional[RefDefinition]:
    """pos(줄 머리)에서 참조형 링크 정의 하나를 읽는다. 정의가 아니면 None.

    대상은 같은 줄이나 다음 줄에 있고, `<...>`이거나 공백 없는 문자열이다. 제목은
    대상과 같은 줄이나 다음 줄에서 '"', "'", '(' 로 시작해 이스케이프를 뺀 닫는
    문자까지이며 여러 줄에 걸칠 수 있다. 빈 줄을 만나면 제목이 닫히지 않은 것으로
    보고 그 앞까지를 정의로 본다(산문으로 내보내지 않기 위해서다).
    """
    m = _REF_LABEL_RE.match(text, pos)
    if not m:
        return None
    p = _skip_blank_chars(text, m.end())
    if p < len(text) and text[p] in "\r\n":
        p = _skip_blank_chars(text, _line_end(text, p))
    if p >= len(text) or text[p] in "\r\n":
        return None
    if text[p] == "<":
        close = text.find(">", p + 1, _line_end(text, p))
        if close < 0:
            return None
        t_start, t_end, p = p + 1, close, close + 1
    else:
        t_start = p
        while p < len(text) and not text[p].isspace():
            p += 1
        t_end = p
    end = _line_end(text, t_end)
    q = _skip_blank_chars(text, p)
    if q < len(text) and text[q] in "\r\n":
        nxt = _line_end(text, q)
        r = _skip_blank_chars(text, nxt)
        if r < len(text) and text[r] in _TITLE_CLOSERS:
            q = r
        else:
            q = -1
    if q >= 0 and q < len(text) and text[q] in _TITLE_CLOSERS:
        closer = _TITLE_CLOSERS[text[q]]
        k = q + 1
        while k < len(text):
            c = text[k]
            if c == "\\":
                k += 2
                continue
            if c == closer:
                end = _line_end(text, k)
                break
            if c == "\n":
                nxt = _skip_blank_chars(text, k + 1)
                if nxt >= len(text) or text[nxt] in "\r\n":
                    end = k + 1  # 빈 줄 앞에서 닫히지 않았다
                    break
            k += 1
        else:
            end = len(text)
    return RefDefinition(text[t_start:t_end], t_start, t_end, end)


def _starts_html_block(rest: str) -> bool:
    """블록 수준 HTML 태그로 시작하는 줄인지."""
    hm = _HTML_BLOCK_START_RE.match(rest)
    return bool(hm) and hm.group(1).lower() in _HTML_BLOCK_TAGS


def _block_labels(text: str, lines: List[Tuple[int, str, str]]) -> List[str]:
    """줄마다 블록 영역 이름을 정한다. 산문 줄은 PROSE다."""
    n = len(lines)
    labels = [PROSE] * n
    i = 0
    # front matter: 첫 줄이 --- 이면 다음 --- 나 ... 줄까지. 닫히지 않으면 끝까지.
    if n and lines[0][1].rstrip() == "---":
        close = None
        for j in range(1, n):
            if lines[j][1].rstrip() in ("---", "..."):
                close = j
                break
        last = close if close is not None else n - 1
        for j in range(0, last + 1):
            labels[j] = FRONT_MATTER
        i = last + 1

    list_cols: List[int] = []  # 열린 목록 항목의 내용 시작 열
    prev_blank = True
    prev_para = False  # 직전 줄이 문단(산문) 줄이었는가
    prev_quote = False
    while i < n:
        body = lines[i][1]
        if body.strip() == "":
            labels[i] = PROSE
            prev_blank, prev_para, prev_quote = True, False, False
            i += 1
            continue
        width, count = _indent_width(body)
        rest = body[count:]
        if prev_blank:
            while list_cols and width < list_cols[-1] and not _LIST_ITEM_RE.match(rest):
                list_cols.pop()
        base = list_cols[-1] if list_cols else 0
        rel = width - base if width >= base else 0

        # 인용의 게으른 이어짐 줄. 문단을 끊는 블록 구문이 아니면 인용에 속한다.
        if prev_quote and not (
            _FENCE_OPEN_RE.match(rest) or _HEADING_RE.match(rest)
            or _LIST_ITEM_RE.match(rest) or _HR_RE.match(rest.rstrip())
            or rest.startswith("<!--") or _starts_html_block(rest)
        ):
            labels[i] = QUOTE
            i += 1
            continue

        # 목록 항목: 표지 뒤 내용에서 블록 구문(인용, 펜스 등)을 다시 판별한다.
        # 한 줄에서 목록이 여러 단계 열리면(- - 항목) 가장 안쪽 내용까지 벗긴다.
        indented_item = False
        first_item = True
        while rel <= 3 and not _HR_RE.match(rest.rstrip()):
            lm = _LIST_ITEM_RE.match(rest)
            if not lm:
                break
            if first_item:
                while list_cols and list_cols[-1] > width:
                    list_cols.pop()
                first_item = False
            spaces = _indent_width(lm.group(2))[0] if lm.group(2) else 1
            if spaces > 4:
                # 표지 뒤 공백이 다섯 칸 이상이면 내용은 들여쓴 코드다.
                list_cols.append(width + len(lm.group(1)) + 1)
                indented_item = True
                break
            width = width + len(lm.group(1)) + spaces
            list_cols.append(width)
            rest = rest[lm.end():]
            base, rel = width, 0
        if indented_item:
            labels[i] = INDENTED_CODE
            prev_blank, prev_para, prev_quote = False, False, False
            i += 1
            continue

        # 인용 블록
        if rel <= 3 and rest.startswith(">"):
            labels[i] = QUOTE
            prev_blank, prev_para, prev_quote = False, False, True
            i += 1
            continue

        # 펜스 코드
        m = _FENCE_OPEN_RE.match(rest) if rel <= 3 else None
        if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
            marker = m.group(1)
            close = None
            for j in range(i + 1, n):
                b = lines[j][1]
                w, c = _indent_width(b)
                r = b[c:].rstrip()
                if (w - base <= 3 and r.startswith(marker[0] * len(marker))
                        and set(r) == {marker[0]}):
                    close = j
                    break
            last = close if close is not None else n - 1
            for j in range(i, last + 1):
                labels[j] = CODE_FENCE
            i = last + 1
            prev_blank, prev_para, prev_quote = False, False, False
            continue

        # 들여쓴 코드: 문단을 끊고 들어올 수 없다.
        if rel >= 4 and not prev_para:
            labels[i] = INDENTED_CODE
            prev_blank, prev_para, prev_quote = False, False, False
            i += 1
            continue

        # HTML 블록
        if rel <= 3 and rest.startswith("<!--"):
            start = lines[i][0] + len(body) - len(rest)
            stop = _comment_spill_end(text, start)
            last = i
            while last + 1 < n and lines[last + 1][0] < stop:
                last += 1
            for k in range(i, last + 1):
                labels[k] = HTML
            i = last + 1
            prev_blank, prev_para, prev_quote = False, False, False
            continue
        hm = _HTML_BLOCK_START_RE.match(rest) if rel <= 3 else None
        if hm and (hm.group(1).lower() in _HTML_BLOCK_TAGS
                   or (not prev_para and _HTML_SINGLE_TAG_LINE_RE.match(rest))):
            tag = hm.group(1).lower()
            j = i
            if tag in _HTML_RAW_TAGS:
                end_re = re.compile(r"</" + tag + r"\s*>", re.IGNORECASE)
                while j < n and not end_re.search(lines[j][1]):
                    j += 1
                last = j if j < n else n - 1
            else:
                while j + 1 < n and lines[j + 1][1].strip() != "":
                    j += 1
                last = j
            for k in range(i, last + 1):
                labels[k] = HTML
            i = last + 1
            prev_blank, prev_para, prev_quote = False, False, False
            continue

        # 참조형 링크 정의. 각주 정의([^x]:)는 산문이다.
        rd = None
        if rel <= 3 and _REF_DEF_RE.match(rest):
            rd = parse_ref_definition(text, lines[i][0] + len(body) - len(rest))
        if rd:
            last = i
            while last + 1 < n and lines[last + 1][0] < rd.end:
                last += 1
            for k in range(i, last + 1):
                labels[k] = REF_DEFINITION
            i = last + 1
            prev_blank, prev_para, prev_quote = False, False, False
            continue

        # 산문
        labels[i] = PROSE
        is_heading = bool(_HEADING_RE.match(rest)) and rel <= 3
        prev_blank, prev_quote = False, False
        prev_para = not is_heading and not _HR_RE.match(rest.rstrip())
        i += 1
    return labels


_AUTOLINK_RE = re.compile(r"<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^\s<>]*|[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+)>")
_INLINE_TAG_RE = re.compile(
    r"</?[A-Za-z][A-Za-z0-9-]*(?:\s+[A-Za-z_:][A-Za-z0-9_.:-]*"
    r"(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+))?)*\s*/?>")
_BARE_URL_RE = re.compile(r"(?:https?|ftp)://[^\s<>\[\]\"'`]+")
_URL_TRAIL = ".,;:!?*_~"
_ASCII_PUNCT = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


def _inline_regions(text: str, start: int, end: int) -> Tuple[List[Region], Optional[int]]:
    """산문 문단 하나(text[start:end]) 안의 인라인 영역과 문단을 넘는 HTML 주석의 시작.

    산문은 돌려주지 않는다. 영역은 겹치지 않는다. 새로 표시하는 영역이 앞서 표시한
    영역과 겹치면 둘을 합쳐 새 영역의 이름으로 둔다(예: 링크 대상 안의 백틱).
    문단 안에서 닫히지 않은 HTML 주석이 있으면 그 시작 위치를 둘째 값으로 돌려준다.
    """
    out: List[Region] = []
    taken = [False] * (end - start)
    spill: Optional[int] = None

    def mark(kind: str, a: int, b: int) -> None:
        if b <= a:
            return
        keep = []
        for r in out:
            if r.end <= a or r.start >= b:
                keep.append(r)
            else:
                a, b = min(a, r.start), max(b, r.end)
        out[:] = keep
        out.append(Region(kind, a, b))
        for k in range(a - start, b - start):
            taken[k] = True

    # 1단계: 인라인 코드, 자동 링크, 인라인 HTML. 왼쪽부터 먼저 시작한 것이 이긴다.
    j = start
    while j < end:
        ch = text[j]
        if ch == "\\" and j + 1 < end and text[j + 1] in _ASCII_PUNCT:
            j += 2
            continue
        if ch == "`":
            k = j
            while k < end and text[k] == "`":
                k += 1
            run = k - j
            close = None
            p = k
            while p < end:
                if text[p] == "`":
                    q = p
                    while q < end and text[q] == "`":
                        q += 1
                    if q - p == run:
                        close = q
                        break
                    p = q
                else:
                    p += 1
            if close is None:
                # 짝 없는 백틱: 판별하지 못한 구문이라 문단 끝까지 산문이 아니다.
                mark(INLINE_CODE, j, end)
                break
            mark(INLINE_CODE, j, close)
            j = close
            continue
        if ch == "<":
            m = _AUTOLINK_RE.match(text, j, end)
            if m:
                mark(URL, j, m.end())
                j = m.end()
                continue
            if text.startswith("<!--", j):
                close = text.find("-->", j + 4, end)
                if close < 0:
                    # 문단 안에서 닫히지 않았다. 호출부가 문단 밖까지 보호한다.
                    mark(HTML, j, end)
                    spill = j
                    break
                mark(HTML, j, close + 3)
                j = close + 3
                continue
            m = _INLINE_TAG_RE.match(text, j, end)
            if m:
                mark(HTML, j, m.end())
                j = m.end()
                continue
        j += 1

    def free(a: int, b: int) -> bool:
        return not any(taken[a - start:b - start])

    # 2단계: 링크와 이미지의 대상. 링크 글자는 산문으로 남긴다.
    j = start
    while j < end:
        if taken[j - start]:
            j += 1
            continue
        ch = text[j]
        if ch == "\\" and j + 1 < end and text[j + 1] in _ASCII_PUNCT:
            j += 2
            continue
        if ch != "[":
            j += 1
            continue
        # 짝이 맞는 ] 를 찾는다.
        depth = 0
        k = j
        close_br = None
        while k < end:
            c = text[k]
            if taken[k - start]:
                k += 1
                continue
            if c == "\\" and k + 1 < end:
                k += 2
                continue
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    close_br = k
                    break
            k += 1
        if close_br is None:
            j += 1
            continue
        after = close_br + 1
        if after < end and text[after] == "(" and free(after, after + 1):
            dest_end = _parse_inline_destination(text, after + 1, end)
            if dest_end is None:
                # 링크 모양이지만 대상을 해석하지 못했다. 같은 줄의 다음 ')'까지(없으면
                # 줄 끝까지) 산문이 아닌 영역으로 보아 고치지 않는다.
                line_end = text.find("\n", after, end)
                line_end = end if line_end < 0 else line_end
                close = text.find(")", after + 1, line_end)
                dest_end = line_end if close < 0 else close
            mark(LINK_TARGET, after + 1, dest_end)
            j += 1  # 링크 글자 안도 계속 본다
            continue
        if after < end and text[after] == "[" and free(after, after + 1):
            lab_close = text.find("]", after + 1, end)
            if lab_close > after + 1 and "[" not in text[after + 1:lab_close] \
                    and free(after + 1, lab_close):
                mark(LINK_TARGET, after + 1, lab_close)
        j += 1

    # 3단계: 맨 URL
    for m in _BARE_URL_RE.finditer(text, start, end):
        a, b = m.start(), m.end()
        while b > a and text[b - 1] in _URL_TRAIL:
            b -= 1
        if b > a and free(a, b):
            mark(URL, a, b)
    out.sort(key=lambda r: r.start)
    return out, spill


def _parse_inline_destination(text: str, j: int, end: int) -> Optional[int]:
    """인라인 링크 '(' 뒤에서 대상과 제목을 읽고, 닫는 ')' 의 위치를 돌려준다.

    링크 대상 영역은 '(' 다음부터 ')' 앞까지(제목 포함)다. 형식이 맞지 않으면 None.
    """
    k = j
    while k < end and text[k] in " \t\r\n":
        k += 1
    if k < end and text[k] == "<":
        close = text.find(">", k + 1, end)
        if close < 0 or "\n" in text[k:close]:
            return None
        k = close + 1
    else:
        depth = 0
        while k < end:
            c = text[k]
            if c == "\\" and k + 1 < end:
                k += 2
                continue
            if c in " \t\r\n":
                break
            if c == "(":
                depth += 1
            elif c == ")":
                if depth == 0:
                    break
                depth -= 1
            k += 1
    while k < end and text[k] in " \t\r\n":
        k += 1
    if k < end and text[k] in "\"'(":
        closer = ")" if text[k] == "(" else text[k]
        p = k + 1
        close = -1
        while p < end:
            if text[p] == "\\" and p + 1 < end:
                p += 2
                continue
            if text[p] == closer:
                close = p
                break
            p += 1
        if close < 0:
            return None
        k = close + 1
        while k < end and text[k] in " \t\r\n":
            k += 1
    if k < end and text[k] == ")":
        return k
    return None


def _comment_spill_end(text: str, start: int) -> int:
    """start의 '<!--'가 닫히는 '-->' 바로 뒤 위치. 그 줄에서 새 주석이 열려 닫히지
    않으면 그 주석이 닫히는 곳까지 잇는다. 닫히지 않으면 글 끝이다."""
    pos = start
    while True:
        close = text.find("-->", pos + 4)
        if close < 0:
            return len(text)
        stop = close + 3
        line_end = text.find("\n", stop)
        line_end = len(text) if line_end < 0 else line_end
        reopen = text.rfind("<!--", stop, line_end)
        if reopen < 0 or text.find("-->", reopen + 4, line_end) >= 0:
            return stop
        pos = reopen


def segment(text: str) -> List[Region]:
    """글을 겹치지 않는 영역들로 나눈다. 영역은 글 전체를 순서대로 덮는다."""
    lines = _split_lines(text)
    labels = _block_labels(text, lines)
    pieces: List[Region] = []
    i = 0
    n = len(lines)
    while i < n:
        kind = labels[i]
        if kind != PROSE:
            j = i
            while j + 1 < n and labels[j + 1] == kind:
                j += 1
            pieces.append(Region(kind, lines[i][0], lines[j][0] + len(lines[j][1]) + len(lines[j][2])))
            i = j + 1
            continue
        # 산문 문단: 빈 줄과 제목 줄이 문단을 나눈다.
        j = i
        if lines[i][1].strip() == "" or _HEADING_RE.match(lines[i][1].lstrip()):
            pass
        else:
            while (j + 1 < n and labels[j + 1] == PROSE
                   and lines[j + 1][1].strip() != ""
                   and not _HEADING_RE.match(lines[j + 1][1].lstrip())):
                j += 1
        a = lines[i][0]
        b = lines[j][0] + len(lines[j][1]) + len(lines[j][2])
        pos = a
        inline, spill = _inline_regions(text, a, b)
        for r in inline:
            if r.start > pos:
                pieces.append(Region(PROSE, pos, r.start))
            pieces.append(r)
            pos = r.end
        if pos < b:
            pieces.append(Region(PROSE, pos, b))
        i = j + 1
        if spill is not None:
            # 문단을 넘는 HTML 주석: '-->'가 든 줄 끝까지(없으면 글 끝까지) HTML로 본다.
            stop = _comment_spill_end(text, spill)
            while i < n and lines[i][0] < stop:
                i += 1
            stop_end = lines[i - 1][0] + len(lines[i - 1][1]) + len(lines[i - 1][2]) if i > 0 else b
            if stop_end > b:
                pieces.append(Region(HTML, b, stop_end))
    # 같은 이름의 이웃 영역을 합친다.
    merged: List[Region] = []
    for r in pieces:
        if r.end <= r.start:
            continue
        if merged and merged[-1].kind == r.kind and merged[-1].end == r.start:
            merged[-1] = Region(r.kind, merged[-1].start, r.end)
        else:
            merged.append(r)
    return merged


def region_at(regions: Sequence[Region], offset: int) -> str:
    """offset이 든 영역의 이름."""
    starts = [r.start for r in regions]
    i = bisect.bisect_right(starts, offset) - 1
    if 0 <= i < len(regions) and regions[i].start <= offset < regions[i].end:
        return regions[i].kind
    return PROSE


def within_kind(regions: Sequence[Region], start: int, end: int, kind: str) -> bool:
    """[start, end)가 kind 영역 하나 안에 완전히 드는지."""
    starts = [r.start for r in regions]
    i = bisect.bisect_right(starts, start) - 1
    if i < 0:
        return False
    r = regions[i]
    return r.kind == kind and r.start <= start and end <= r.end


# ---------------------------------------------------------------- 링크 추출


@dataclass
class Link:
    target: str  # 대상 경로나 URL(제목 제외, <> 제외)
    start: int  # 대상 영역의 시작 위치
    end: int  # 대상 영역 끝(링크를 닫는 ')' 위치)


def extract_links(text: str, regions: Sequence[Region]) -> List[Link]:
    """인라인 링크와 참조형 링크 정의의 대상을 뽑는다. 코드와 인용 안의 링크는 뺀다."""
    out: List[Link] = []
    for r in regions:
        if r.kind == LINK_TARGET and r.start > 0 and text[r.start - 1] == "(":
            raw = text[r.start:r.end].strip()
            if raw.startswith("<"):
                target = raw[1:raw.find(">")] if ">" in raw else raw[1:]
            else:
                target = raw.split()[0] if raw.split() else ""
            out.append(Link(target, r.start, r.end))
        elif r.kind == REF_DEFINITION:
            # 영역 판별과 같은 파서로 정의를 차례로 소비한다. 제목 안은 새 정의로 보지 않는다.
            pos = r.start
            while pos < r.end:
                d = parse_ref_definition(text, pos)
                if d is None:
                    # 목록 안의 정의: 영역 판별처럼 줄 머리 공백과 목록 표지를 벗긴다.
                    d = parse_ref_definition(text, _content_start(text, pos))
                if d is None:
                    pos = _line_end(text, pos)
                    continue
                out.append(Link(d.target, d.target_start, d.target_end))
                pos = max(d.end, _line_end(text, pos))
    return out


def is_external_target(target: str) -> bool:
    return bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)) or target.startswith("//")


def resolve_link(doc_path: Path, target: str) -> Optional[Path]:
    """문서 안의 상대 링크를 파일 경로로 푼다. 외부 링크와 절 앵커만 있는 링크는 None."""
    if not target or is_external_target(target) or target.startswith("#"):
        return None
    path_part = target.split("#", 1)[0].split("?", 1)[0]
    if not path_part:
        return None
    return (doc_path.parent / urllib.parse.unquote(path_part)).resolve()


# ---------------------------------------------------------------- 규칙 문서


@dataclass
class Pattern:
    source: str
    line: int
    compiled: Optional["re.Pattern"] = None
    error: Optional[str] = None


@dataclass
class DocLink:
    target: str
    line: int
    section_title: Optional[str] = None  # 설명 링크 뒤 큰따옴표 절 제목


@dataclass
class RuleSection:
    title: str  # 규칙 이름 표기를 뺀 제목
    heading: str  # 제목 줄 원문(## 뒤)
    name: Optional[str]  # 규칙 이름. 없으면 None
    name_raw: Optional[str]  # 백틱 안 원문(형식 검사용)
    line: int
    start: int
    end: int
    patterns: List[Pattern] = field(default_factory=list)
    has_patterns_heading: bool = False
    mechanical_links: List[DocLink] = field(default_factory=list)
    explanation_links: List[DocLink] = field(default_factory=list)


@dataclass
class RuleDoc:
    path: Path
    stem: str
    text: str
    sections: List[RuleSection]
    body_start: int  # front matter 다음 위치

    @property
    def named(self) -> bool:
        return any(s.name_raw is not None for s in self.sections)

    def body(self) -> str:
        return self.text[self.body_start:]


_H2_RE = re.compile(r"^##[ \t]+(.*?)[ \t]*#*[ \t]*$")
_H3_RE = re.compile(r"^###[ \t]+(.*?)[ \t]*#*[ \t]*$")
_ANY_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$")
_NAME_SUFFIX_RE = re.compile(r"^(.*?)[ \t]*`([^`]+)`$")
# 설명 링크 뒤 절 제목. 제목 안에 큰따옴표가 들어갈 수 있어 줄 끝의 따옴표까지 읽는다.
_QUOTED_TITLE_RE = re.compile(r'[ \t]*"(.+)"[ \t]*$')


def _prose_heading_lines(text: str, regions: Sequence[Region], lines) -> List[int]:
    """코드, 인용, HTML 밖에 있는 줄 번호(0부터) 목록."""
    out = []
    for idx, (pos, body, _nl) in enumerate(lines):
        if body.startswith("#") and region_at(regions, pos) == PROSE:
            out.append(idx)
    return out


def read_text_file(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as e:
        raise ToolError(f"Cannot read file. 파일을 읽지 못했다: {path} ({e})")
    text, _bom = decode_utf8(raw, str(path))
    return text


def parse_rule_doc(path: Path, text: Optional[str] = None) -> RuleDoc:
    """규칙 문서를 읽는다. 정규식은 컴파일해 두되 실패는 Pattern.error에 담는다."""
    if text is None:
        text = read_text_file(path)
    regions = segment(text)
    lines = _split_lines(text)
    body_start = 0
    if regions and regions[0].kind == FRONT_MATTER:
        body_start = regions[0].end
    heading_idx = _prose_heading_lines(text, regions, lines)
    h2 = [i for i in heading_idx if _H2_RE.match(lines[i][1]) and not lines[i][1].startswith("###")]
    sections: List[RuleSection] = []
    for n_i, li in enumerate(h2):
        heading = _H2_RE.match(lines[li][1]).group(1)
        nm = _NAME_SUFFIX_RE.match(heading)
        title, name_raw = (nm.group(1), nm.group(2)) if nm else (heading, None)
        name = name_raw if name_raw is not None and RULE_NAME_RE.match(name_raw) else None
        start = lines[li][0]
        end_line = h2[n_i + 1] if n_i + 1 < len(h2) else None
        # 문서 끝 다음 #(h1) 제목에서도 끝난다.
        stop_candidates = [i for i in heading_idx if i > li and lines[i][1].startswith("# ")]
        if stop_candidates and (end_line is None or stop_candidates[0] < end_line):
            end_line = stop_candidates[0]
        end = lines[end_line][0] if end_line is not None else len(text)
        sec = RuleSection(title, heading, name, name_raw, li + 1, start, end)
        _parse_subsections(text, regions, lines, heading_idx, li, end_line, sec, path)
        sections.append(sec)
    return RuleDoc(path, path.stem, text, sections, body_start)


def _parse_subsections(text, regions, lines, heading_idx, h2_line, end_line, sec: RuleSection, path: Path):
    limit = end_line if end_line is not None else len(lines)
    h3 = [i for i in heading_idx if h2_line < i < limit and _H3_RE.match(lines[i][1])
          and not lines[i][1].startswith("####")]
    links_all = extract_links(text, regions)
    li = LineIndex(text)
    for n_i, hi in enumerate(h3):
        name = _H3_RE.match(lines[hi][1]).group(1)
        sub_end_line = h3[n_i + 1] if n_i + 1 < len(h3) else limit
        a = lines[hi][0]
        b = lines[sub_end_line][0] if sub_end_line < len(lines) else len(text)
        if name == PATTERNS_HEADING:
            sec.has_patterns_heading = True
            for r in regions:
                if r.kind not in (CODE_FENCE, INDENTED_CODE) or r.end <= a or r.start >= b:
                    continue
                block_lines = _split_lines(text[r.start:r.end])
                first_line = li.line_col(r.start)[0]
                for k, (_p, body, _nl) in enumerate(block_lines):
                    if r.kind == CODE_FENCE and (k == 0 or (
                            k == len(block_lines) - 1 and _FENCE_OPEN_RE.match(body.strip())
                            and not body.strip()[3:].strip("`~"))):
                        continue
                    src = body.strip() if r.kind == CODE_FENCE else _dedent4(body)
                    if not src:
                        continue
                    pat = Pattern(src, first_line + k)
                    try:
                        pat.compiled = re.compile(src)
                    except re.error as e:
                        pat.error = str(e)
                    sec.patterns.append(pat)
        elif name in (MECHANICAL_HEADING, EXPLANATION_HEADING):
            for link in links_all:
                if not (a <= link.start < b):
                    continue
                line_no = li.line_col(link.start)[0]
                dl = DocLink(link.target, line_no)
                if name == EXPLANATION_HEADING:
                    line_end = text.find("\n", link.end)
                    tail = text[link.end + 1:line_end if line_end >= 0 else len(text)]
                    m = _QUOTED_TITLE_RE.match(tail.rstrip("\r"))
                    if m:
                        dl.section_title = m.group(1)
                    sec.explanation_links.append(dl)
                else:
                    sec.mechanical_links.append(dl)


def _dedent4(body: str) -> str:
    w, c = _indent_width(body)
    return body[c:].strip() if w >= 4 else body.strip()


def rule_doc_paths(root: Path) -> List[Path]:
    """규칙 문서 폴더의 규칙 문서들(디스크립터와 색인 제외)."""
    folder = root / RULES_DIR_REL
    if not folder.is_dir():
        return []
    return sorted(
        p for p in folder.glob("*.md")
        if p.is_file() and p.name not in NON_RULE_FILES and not INDEX_PAGE_RE.match(p.name)
    )


def load_rule_docs(root: Path) -> List[RuleDoc]:
    return [parse_rule_doc(p) for p in rule_doc_paths(root)]


def compiled_patterns(docs: Sequence[RuleDoc]) -> List[Tuple[RuleDoc, RuleSection, Pattern]]:
    """이름 붙은 규칙의 후보 검출 패턴. 컴파일되지 않는 정규식이 있으면 ToolError."""
    out = []
    errors = []
    for d in docs:
        for s in d.sections:
            if s.name is None:
                continue
            for p in s.patterns:
                if p.error:
                    errors.append(f"{d.path.name}:{p.line} `{s.name}`: {p.error}")
                else:
                    out.append((d, s, p))
    if errors:
        raise ToolError("Rule pattern failed to compile. 후보 검출 패턴을 읽지 못했다: "
                        + "; ".join(errors))
    return out


# ---------------------------------------------------------------- 설명 문서


@dataclass
class ExplanationSection:
    title: str
    rules: List[str]  # `규칙:` 줄의 규칙 이름들. 줄이 없으면 빈 목록
    line: int


_RULE_LINE_RE = re.compile(r"^규칙:[ \t]*(`[^`]+`(?:[ \t]*,[ \t]*`[^`]+`)*)[ \t]*$")


def parse_explanation_doc(path: Path, text: Optional[str] = None) -> List[ExplanationSection]:
    """설명 문서의 절 제목과 그 아래 첫 줄의 `규칙:` 값을 읽는다.

    절 제목 수준은 가리지 않는다. `규칙:` 줄은 인라인 코드로 쓴 규칙 이름 하나 이상을
    쉼표로 나열한다(예: 규칙: `a-rule`, `b-rule`).
    """
    if text is None:
        text = read_text_file(path)
    regions = segment(text)
    lines = _split_lines(text)
    out = []
    for idx in _prose_heading_lines(text, regions, lines):
        m = _ANY_HEADING_RE.match(lines[idx][1])
        if not m:
            continue
        rules: List[str] = []
        for j in range(idx + 1, len(lines)):
            body = lines[j][1]
            if body.strip() == "":
                continue
            rm = _RULE_LINE_RE.match(body.strip())
            if rm:
                rules = re.findall(r"`([^`]+)`", rm.group(1))
            break
        out.append(ExplanationSection(m.group(2), rules, idx + 1))
    return out


# ---------------------------------------------------------------- 기계 규칙


@dataclass
class Replacement:
    find: "re.Pattern"
    replace: str
    note: str


@dataclass
class MechanicalRule:
    path: Path
    rule: str
    replacements: List[Replacement]
    apply_in: List[str]


_TOP_KEYS = {"rule", "replacements", "apply_in"}
_REP_KEYS = {"find", "replace", "note"}


def load_mechanical(path: Path) -> MechanicalRule:
    """기계 규칙 JSON 하나를 읽고 검증한다. 어긋나면 ToolError."""
    name = path.name

    def fail(detail: str):
        raise ToolError(f"Invalid mechanical rule. 기계 규칙을 읽지 못했다: {name}: {detail}")

    try:
        data = json.loads(read_text_file(path))
    except ValueError as e:
        fail(f"JSON 형식 오류 ({e})")
    if not isinstance(data, dict):
        fail("최상위가 객체가 아니다")
    unknown = set(data) - _TOP_KEYS
    if unknown:
        fail(f"알 수 없는 키 {sorted(unknown)}")
    missing = _TOP_KEYS - set(data)
    if missing:
        fail(f"빠진 키 {sorted(missing)}")
    rule = data["rule"]
    if not isinstance(rule, str) or not RULE_NAME_RE.match(rule):
        fail("rule은 영문 소문자 케밥 케이스 문자열이어야 한다")
    apply_in = data["apply_in"]
    if not isinstance(apply_in, list) or not apply_in or not all(isinstance(x, str) for x in apply_in):
        fail("apply_in은 영역 이름 문자열의 비지 않은 목록이어야 한다")
    for x in apply_in:
        if x not in REGION_KINDS:
            fail(f"알 수 없는 영역 이름 {x!r}")
        if x != PROSE:
            fail(f"기계 규칙은 산문 영역에만 적용한다 ({x!r})")
    reps = data["replacements"]
    if not isinstance(reps, list) or not reps:
        fail("replacements는 비지 않은 목록이어야 한다")
    out = []
    for k, rep in enumerate(reps, 1):
        if not isinstance(rep, dict):
            fail(f"replacements[{k}]가 객체가 아니다")
        unknown = set(rep) - _REP_KEYS
        if unknown:
            fail(f"replacements[{k}]에 알 수 없는 키 {sorted(unknown)}")
        find = rep.get("find")
        replace = rep.get("replace")
        note = rep.get("note", "")
        if not isinstance(find, str) or not find:
            fail(f"replacements[{k}].find가 비었거나 문자열이 아니다")
        if not isinstance(replace, str):
            fail(f"replacements[{k}].replace가 문자열이 아니다")
        if not isinstance(note, str):
            fail(f"replacements[{k}].note가 문자열이 아니다")
        try:
            compiled = re.compile(find)
        except re.error as e:
            fail(f"replacements[{k}].find 정규식 컴파일 실패 ({e})")
        for m in re.finditer(r"\\(.?)", replace):
            if m.group(1) not in "123456789" or not m.group(1):
                fail(f"replacements[{k}].replace의 역참조는 \\1-\\9 형태만 허용한다")
            if int(m.group(1)) > compiled.groups:
                fail(f"replacements[{k}].replace가 없는 그룹 \\{m.group(1)}을 가리킨다")
        out.append(Replacement(compiled, replace, note))
    return MechanicalRule(path, rule, out, list(apply_in))


def load_all_mechanical(root: Path) -> List[MechanicalRule]:
    """기계 규칙 폴더의 JSON을 이름 순으로 모두 읽는다. 하나라도 어긋나면 ToolError."""
    folder = root / MECHANICAL_DIR_REL
    if not folder.is_dir():
        return []
    return [load_mechanical(p) for p in sorted(folder.glob("*.json")) if p.is_file()]


@dataclass
class Change:
    rule: str
    line: int
    column: int
    before: str
    after: str
    note: str
    context: str


def _expand(m: "re.Match", replace: str) -> str:
    """역참조 \\1-\\9(한 자리)를 그룹 값으로 바꾼다. 검증(load_mechanical)과 같은 해석이다."""
    return re.sub(r"\\([1-9])", lambda g: m.group(int(g.group(1))) or "", replace)


def apply_mechanical(text: str, rules: Sequence[MechanicalRule]) -> Tuple[str, List[Change]]:
    """기계 규칙을 적힌 순서대로 한 번씩 적용한다.

    일치가 산문 영역 하나 안에 완전히 든 경우만 바꾼다. 치환 항목마다 영역을 다시
    판별한다. 보고 위치는 그 치환 항목을 적용하기 직전 글 기준이다.
    """
    changes: List[Change] = []
    for rule in rules:
        for rep in rule.replacements:
            regions = segment(text)
            index = LineIndex(text)
            parts = []
            pos = 0
            for m in rep.find.finditer(text):
                if m.end() == m.start():
                    continue
                if not within_kind(regions, m.start(), m.end(), PROSE):
                    continue
                new = _expand(m, rep.replace)
                if new == m.group(0):
                    continue
                line, col = index.line_col(m.start())
                changes.append(Change(rule.rule, line, col, m.group(0), new, rep.note,
                                      index.context(m.start(), m.end())))
                parts.append(text[pos:m.start()])
                parts.append(new)
                pos = m.end()
            if parts:
                parts.append(text[pos:])
                text = "".join(parts)
    return text, changes


# ---------------------------------------------------------------- 인자


def add_common_args(parser, path_hint: bool = True) -> None:
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="결과 형식(기본 text)")
    if path_hint:
        parser.add_argument("--path-hint", metavar="PATH",
                            help="표준 입력일 때 경로로 정하는 예외를 판정할 경로")
    parser.add_argument("--root", metavar="DIR", default=None,
                        help="규칙을 읽을 레포 루트(기본: 이 도구가 든 레포)")


def root_from_args(args) -> Path:
    return Path(args.root).resolve() if args.root else DEFAULT_ROOT
