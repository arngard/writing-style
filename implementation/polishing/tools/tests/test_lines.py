"""--lines(범위 윤문) 시험. 범위 파싱, 기계 수정과 검출의 범위 한정, 검토 자료, 범위 밖 보존 검사."""

import json
import unittest

from _helpers import MARKER_FORM, Fixture, core, run_tool


class ParseTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(core.parse_line_range("2-5"), core.LineRange(2, 5))
        self.assertEqual(core.parse_line_range("3"), core.LineRange(3, 3))
        self.assertEqual(core.parse_line_range(" 1 - 1 "), core.LineRange(1, 1))

    def test_invalid(self):
        for spec in ("", "0-2", "3-2", "a-b", "1-", "-2", "1-2-3", "1,2"):
            with self.assertRaises(core.ToolError, msg=spec):
                core.parse_line_range(spec)

    def test_line_count(self):
        self.assertEqual([core.line_count(t) for t in ("", "a", "a\n", "a\nb", "a\r\nb\r\n", "\n")],
                         [0, 1, 1, 2, 2, 1])

    def test_span_out_of_text(self):
        self.assertEqual(core.range_span("a\nb\nc", core.LineRange(2, 3)), (2, 5))
        self.assertEqual(core.range_span("a\nb\n", core.LineRange(1, 1)), (0, 2))
        with self.assertRaises(core.ToolError):
            core.range_span("a\nb\n", core.LineRange(2, 3))


class ApplyMechanicalTest(unittest.TestCase):
    def fix(self, text, spec):
        rules = [core.load_mechanical(MARKER_FORM)]
        return core.apply_mechanical(text, rules, core.parse_line_range(spec))[0]

    def test_only_inside_range(self):
        text = "see:[a](b)\nsee:[a](b)\nsee:[a](b)\n"
        self.assertEqual(self.fix(text, "2-3"), "see:[a](b)\nsee: [a](b)\nsee: [a](b)\n")
        self.assertEqual(self.fix(text, "1"), "see: [a](b)\nsee:[a](b)\nsee:[a](b)\n")

    def test_match_crossing_boundary_untouched(self):
        fx = Fixture()
        self.addCleanup(fx.cleanup)
        p = fx.write("r.json", json.dumps({"rule": "t", "replacements": [
            {"find": "x\\ny", "replace": "z", "note": "n"}], "apply_in": ["prose"]}))
        rules = [core.load_mechanical(p)]
        text = "x\ny\n"
        self.assertEqual(core.apply_mechanical(text, rules, core.LineRange(1, 1))[0], text)
        self.assertEqual(core.apply_mechanical(text, rules, core.LineRange(1, 2))[0], "z\n")

    def load(self, *reps):
        fx = Fixture()
        self.addCleanup(fx.cleanup)
        p = fx.write("r.json", json.dumps({"rule": "t", "replacements": [
            {"find": f, "replace": r, "note": "n"} for f, r in reps], "apply_in": ["prose"]}))
        return [core.load_mechanical(p)]

    def test_range_follows_line_count_change(self):
        # 앞 치환이 범위의 줄 수를 줄여도 뒤 치환이 범위 밖 줄을 건드리지 않는다.
        rules = self.load(("x\\ny", "z"), ("OUT", "bad"))
        self.assertEqual(core.apply_mechanical("x\ny\nOUT\n", rules, core.LineRange(1, 2))[0],
                         "z\nOUT\n")

    def test_no_join_with_following_line(self):
        rules = self.load(("x\\n", "x"))
        self.assertEqual(core.apply_mechanical("x\nOUT\n", rules, core.LineRange(1, 1))[0], "x\nOUT\n")
        # 같은 치환 항목에서 앞 일치가 이미 줄바꿈을 없앴으면 뒤 일치도 막는다.
        rules2 = self.load(("(x)\\n|y\\n", "\\1"))
        self.assertEqual(core.apply_mechanical("x\ny\nOUT\n", rules2, core.LineRange(1, 2))[0],
                         "xy\nOUT\n")
        # 범위가 글 끝까지면 줄바꿈을 없애도 이어 붙을 줄이 없다.
        self.assertEqual(core.apply_mechanical("a\nx\n", rules, core.LineRange(2, 2))[0], "a\nx")

    def test_regions_judged_on_whole_text(self):
        # 범위가 코드 펜스 안의 줄만 잡아도 그 줄은 산문이 아니다.
        text = "```\nsee:[a](b)\n```\n"
        self.assertEqual(self.fix(text, "2"), text)


class ToolTest(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)
        self.fx.standard()

    def test_fix_lines_keeps_bom_and_crlf(self):
        data = "﻿see:[a](b)\r\nsee:[a](b)\r\n".encode("utf-8")
        code, out, _ = run_tool("fix.py", ["--root", str(self.fx.root), "--lines", "2"], stdin=data)
        self.assertEqual(code, 0)
        self.assertEqual(out, "﻿see:[a](b)\r\nsee: [a](b)\r\n".encode("utf-8"))

    def test_fix_lines_errors(self):
        for spec in ("0", "2-1", "3"):
            code, out, _ = run_tool("fix.py", ["--root", str(self.fx.root), "--lines", spec],
                                    stdin=b"a\nb\n")
            self.assertEqual((code, out), (2, b""), spec)

    def test_range_checked_before_reference_skip(self):
        for tool in ("fix.py", "detect.py"):
            code, out, _ = run_tool(tool, ["--root", str(self.fx.root), "--lines", "2",
                                           "--path-hint", "reference/example/sample.md"], stdin=b"a\n")
            self.assertEqual((code, out), (2, b""), tool)

    def test_detect_lines(self):
        text = "가나다\nsee:[a](b)\n가나다\n".encode("utf-8")
        code, out, _ = run_tool("detect.py", ["--root", str(self.fx.root), "--format", "json",
                                              "--lines", "3"], stdin=text)
        self.assertEqual(code, 0)
        data = json.loads(out.decode("utf-8"))[0]
        self.assertEqual(data["violations"], [])
        self.assertEqual([c["line"] for c in data["candidates"]], [3])
        a = self.fx.write("a.md", "x\n")
        b = self.fx.write("b.md", "y\n")
        code, _out, err = run_tool("detect.py", ["--root", str(self.fx.root), "--lines", "1",
                                                 str(a), str(b)])
        self.assertEqual(code, 2)
        self.assertIn("exactly one input", err)

    def test_collect_review_lines(self):
        text = "가나다\n둘\n가나다\n".encode("utf-8")
        code, out, _ = run_tool("collect_review.py", ["--root", str(self.fx.root), "--format", "json",
                                                      "--docs", "vocabulary", "--lines", "2-3"],
                                stdin=text)
        self.assertEqual(code, 0)
        data = json.loads(out.decode("utf-8"))
        self.assertIn("2-3줄만 고친다", data["guide"])
        self.assertEqual([c["line"] for c in data["candidates"]], [3])
        self.assertEqual(data["target"]["lines"], {"first": 2, "last": 3})
        self.assertEqual(data["target"]["text"], "가나다\n둘\n가나다\n")
        code, out, _ = run_tool("collect_review.py", ["--root", str(self.fx.root),
                                                      "--docs", "vocabulary", "--lines", "4"],
                                stdin=text)
        self.assertEqual((code, out), (2, b""))


class CheckRangeTest(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)

    def check(self, before, after, spec):
        b = self.fx.write("before.md", "")
        b.write_bytes(before.encode("utf-8"))
        a = self.fx.write("after.md", "")
        a.write_bytes(after.encode("utf-8"))
        code, out, err = run_tool("check_preservation.py",
                                  [str(b), str(a), "--lines", spec, "--format", "json"])
        return code, (json.loads(out.decode("utf-8")) if out else None), err

    def test_current_range(self):
        code, data, _ = self.check("a\nb\nc\n", "a\nBx\nBy\nc\n", "2")
        self.assertEqual(code, 0)
        self.assertEqual((data["outside_kept"], data["range"]), (True, {"first": 2, "last": 3}))
        code, data, _ = self.check("a\nb\nc\nd\n", "a\nBC\nd\n", "2-3")
        self.assertEqual(data["range"], {"first": 2, "last": 2})

    def test_range_deleted(self):
        code, data, _ = self.check("a\nb\nc\n", "a\nc\n", "2")
        self.assertEqual(code, 0)
        self.assertEqual((data["range"], data["insert_at"]), (None, 2))

    def test_outside_changed_is_blocked(self):
        for before, after, spec in (
            ("a\nb\nc\n", "A\nb\nc\n", "2"),  # 앞부분이 바뀜
            ("a\nb\nc\n", "a\nb\nC\n", "2"),  # 뒷부분이 바뀜
            ("x\nx\nx\n", "x\n", "2"),  # 같은 줄이 반복될 때 앞뒤가 겹치게 맞추지 않는다
            ("a\nb\nc\n", "a\nBc\n", "2"),  # 범위의 끝 줄바꿈이 빠져 뒷줄과 이어 붙음
            ("a\nb\nc\n", "a\nb\nc\nd\n", "2"),  # 끝에 줄을 더함
        ):
            code, data, _ = self.check(before, after, spec)
            self.assertEqual(code, 3, (before, after))
            self.assertFalse(data["outside_kept"])
            self.assertTrue(data["blocked"])

    def test_bom_and_crlf(self):
        code, data, _ = self.check("a\r\nb\r\nc\r\n", "a\r\nB\r\nc\r\n", "2")
        self.assertEqual((code, data["range"]), (0, {"first": 2, "last": 2}))
        code, data, _ = self.check("a\nb\n", "﻿a\nB\n", "2")
        self.assertEqual(code, 3)

    def test_no_final_newline(self):
        code, data, _ = self.check("a\nb", "a\nB", "2")
        self.assertEqual((code, data["range"]), (0, {"first": 2, "last": 2}))

    def test_changes_still_reported(self):
        code, data, _ = self.check("a\n값 1\nc\n", "a\n값 2\nc\n", "2")
        self.assertEqual(code, 1)
        self.assertTrue(data["outside_kept"])

    def test_invalid_range(self):
        code, data, _ = self.check("a\n", "a\n", "2")
        self.assertEqual((code, data), (2, None))

    def test_text_output(self):
        b = self.fx.write("b.md", "a\nb\nc\n")
        a = self.fx.write("a.md", "a\nc\n")
        code, out, _ = run_tool("check_preservation.py", [str(b), str(a), "--lines", "2"])
        self.assertEqual(code, 0)
        self.assertIn("현재 범위: 없음(2줄 자리)", out.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
