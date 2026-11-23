"""detect.py 명령줄 시험."""

import json
import tempfile
import unittest

from _helpers import TOOLS, Fixture, run_tool


class DetectTest(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)
        self.fx.standard()

    def test_violation_and_candidate(self):
        text = "가나다 see:[a](b)\n\n`가나다`\n"
        code, out, _ = run_tool("detect.py", ["--root", str(self.fx.root), "--format", "json"],
                                stdin=text.encode("utf-8"))
        self.assertEqual(code, 1)
        data = json.loads(out.decode("utf-8"))[0]
        self.assertEqual([v["rule"] for v in data["violations"]], ["marker-form"])
        regions = [(c["rule"], c["line"], c["region"]) for c in data["candidates"]]
        self.assertEqual(regions, [("sample-word", 1, "prose"), ("sample-word", 3, "inline_code")])

    def test_candidates_only_exit_zero(self):
        code, out, _ = run_tool("detect.py", ["--root", str(self.fx.root)], stdin="가나다\n".encode("utf-8"))
        self.assertEqual(code, 0)
        self.assertIn("candidate [sample-word]", out.decode("utf-8"))

    def test_clean(self):
        code, out, _ = run_tool("detect.py", ["--root", str(self.fx.root)], stdin=b"see: [a](b)\n")
        self.assertEqual((code, out), (0, b""))

    def test_old_form_rule_docs_give_no_candidates(self):
        fx = Fixture()
        self.addCleanup(fx.cleanup)
        fx.rules("vocabulary", "# 어휘\n\n## 옛 절\n\n### 후보 검출 패턴\n\n```\n가나다\n```\n")
        fx.copy_marker_form()
        code, out, _ = run_tool("detect.py", ["--root", str(fx.root)], stdin="가나다\n".encode("utf-8"))
        self.assertEqual((code, out), (0, b""))

    def test_bad_pattern_is_tool_error(self):
        self.fx.rules("format", "## 규칙 `bad-one`\n\n### 후보 검출 패턴\n\n```\n(열림\n```\n")
        code, _out, err = run_tool("detect.py", ["--root", str(self.fx.root)], stdin=b"x\n")
        self.assertEqual(code, 2)
        self.assertIn("bad-one", err)

    def test_multiple_files(self):
        a = self.fx.write("a.md", "see:[a](b)\n")
        b = self.fx.write("b.md", "ok\n")
        code, out, _ = run_tool("detect.py", ["--root", str(self.fx.root), str(a), str(b)])
        self.assertEqual(code, 1)
        self.assertIn("a.md:1:1: violation [marker-form]", out.decode("utf-8"))

    def test_reference_material_by_git_root(self):
        (self.fx.root / ".git").mkdir()
        p = self.fx.write("reference/자료/a.md", "see:[a](b) 가나다\n")
        code, out, _ = run_tool("detect.py", ["--root", str(self.fx.root), str(p)])
        self.assertEqual((code, out), (0, b""))

    def test_repo_rules_from_other_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            code, _out, err = run_tool(str(TOOLS / "detect.py"), [], stdin=b"see:[a](b)\n", cwd=d)
        self.assertEqual(code, 1, err)


if __name__ == "__main__":
    unittest.main()
