"""check_preservation.py 명령줄 시험."""

import json
import tempfile
import unittest
from pathlib import Path

from _helpers import run_tool


class CheckPreservationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def put(self, name, text):
        p = self.dir / name
        p.write_bytes(text.encode("utf-8"))
        return str(p)

    BASE = ("---\ndate modified: 2026-11-20\n---\n"
            "보관 기간은 30일이다. [문서](a.md) <https://e.x/1>\n"
            "`code` 와 see:[b](c)\n\n```\n블록\n```\n\n> 인용\n")

    def test_identical(self):
        a = self.put("a.md", self.BASE)
        code, out, _ = run_tool("check_preservation.py", [a, a])
        self.assertEqual((code, out), (0, b""))

    def test_mechanical_fix_passes(self):
        a = self.put("a.md", self.BASE)
        _c, fixed, _e = run_tool("fix.py", [a])
        self.assertNotEqual(fixed, self.BASE.encode("utf-8"))
        code, out, _ = run_tool("check_preservation.py", [a, "-", "--mechanical"], stdin=fixed)
        self.assertEqual((code, out), (0, b""))

    def test_changes_are_reported_with_location(self):
        a = self.put("a.md", self.BASE)
        changed = (self.BASE.replace("30일", "31일").replace("(a.md)", "(b.md)")
                   .replace("`code`", "`코드`").replace("블록", "블럭")
                   .replace("> 인용", "> 인용문").replace("2026-11-20", "2026-11-23")
                   .replace("https://e.x/1", "https://e.x/2"))
        b = self.put("b.md", changed)
        code, out, _ = run_tool("check_preservation.py", [a, b, "--format", "json"])
        self.assertEqual(code, 1)
        data = json.loads(out.decode("utf-8"))
        items = {(d["item"], d["value"], d["side"]) for d in data["changes"]}
        for expected in [("number", "30", "before"), ("number", "31", "after"),
                         ("link_target", "a.md", "before"), ("inline_code", "`code`", "before"),
                         ("code_block", "```\n블록\n```", "before"), ("quote", "> 인용", "before"),
                         ("front_matter", "date modified: 2026-11-20", "before"),
                         ("url", "https://e.x/1", "before")]:
            self.assertIn(expected, items)
        num = [d for d in data["changes"] if d["value"] == "30"][0]
        self.assertEqual(num["locations"][0]["line"], 4)
        self.assertIn("[[30]]", num["locations"][0]["context"])

    def test_count_change(self):
        a = self.put("a.md", "1 그리고 1\n")
        b = self.put("b.md", "1 그리고 하나\n")
        code, out, _ = run_tool("check_preservation.py", [a, b])
        self.assertEqual(code, 1)
        self.assertIn("[number] '1': 2 -> 1", out.decode("utf-8"))

    def test_style_change_is_not_reported(self):
        a = self.put("a.md", "설정을 바꾼다.\n")
        b = self.put("b.md", "설정을 바꿉니다.\n")
        code, _out, _ = run_tool("check_preservation.py", [a, b])
        self.assertEqual(code, 0)

    def test_mechanical_non_prose_change_is_blocked(self):
        a = self.put("a.md", "글 `see:[a](b)`\n")
        b = self.put("b.md", "글 `see: [a](b)`\n")
        code, _out, _ = run_tool("check_preservation.py", [a, b, "--mechanical"])
        self.assertEqual(code, 3)
        code, _out, _ = run_tool("check_preservation.py", [a, b])
        self.assertEqual(code, 1)

    def test_crlf_vs_lf_code_block_equal(self):
        a = self.put("a.md", "```\r\nx\r\n```\r\n")
        b = self.put("b.md", "```\nx\n```\n")
        code, _out, _ = run_tool("check_preservation.py", [a, b])
        self.assertEqual(code, 0)

    def test_reference_definition_target_change_in_list(self):
        a = self.put("a.md", "- [id]: old.md\n")
        b = self.put("b.md", "- [id]: new.md\n")
        code, out, _ = run_tool("check_preservation.py", [a, b])
        self.assertEqual(code, 1)
        self.assertIn("old.md", out.decode("utf-8"))

    def test_two_stdin_rejected(self):
        code, _out, _err = run_tool("check_preservation.py", ["-", "-"], stdin=b"")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
