"""fix.py 명령줄 시험."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import TOOLS, Fixture, core, run_tool

import fix as fix_module

BOM = b"\xef\xbb\xbf"


class FixTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_stdin_crlf_bom_preserved(self):
        src = BOM + "앞 see:[a](b)\r\n`see:[c](d)`\r\n".encode("utf-8")
        code, out, _err = run_tool("fix.py", [], stdin=src)
        self.assertEqual(code, 0)
        self.assertEqual(out, BOM + "앞 see: [a](b)\r\n`see:[c](d)`\r\n".encode("utf-8"))

    def test_no_front_matter_lf(self):
        code, out, _ = run_tool("fix.py", ["-"], stdin="ref:[a](b)".encode("utf-8"))
        self.assertEqual((code, out), (0, b"ref: [a](b)"))

    def test_write_replaces_file_and_keeps_format(self):
        p = self.dir / "a.md"
        p.write_bytes(BOM + b"see:[a](b)\r\nx\r\n")
        code, out, _ = run_tool("fix.py", [str(p), "--write"])
        self.assertEqual(code, 0)
        self.assertEqual(p.read_bytes(), BOM + b"see: [a](b)\r\nx\r\n")
        self.assertIn(b"marker-form", out)
        self.assertEqual(sorted(x.name for x in self.dir.iterdir()), ["a.md"])

    def test_write_without_change_keeps_file(self):
        p = self.dir / "a.md"
        p.write_bytes(b"see: [a](b)\n")
        before = os.stat(p).st_mtime_ns
        code, _out, _ = run_tool("fix.py", [str(p), "--write"])
        self.assertEqual(code, 0)
        self.assertEqual(os.stat(p).st_mtime_ns, before)

    def test_dry_run_does_not_write(self):
        p = self.dir / "a.md"
        p.write_bytes(b"see:[a](b)\n")
        code, out, _ = run_tool("fix.py", [str(p), "--dry-run", "--format", "json"])
        self.assertEqual(code, 0)
        data = json.loads(out.decode("utf-8"))
        self.assertEqual(data["changes"][0]["after"], "see: ")
        self.assertEqual(p.read_bytes(), b"see:[a](b)\n")

    def test_write_and_dry_run_exclusive(self):
        p = self.dir / "a.md"
        p.write_bytes(b"x\n")
        code, _out, _ = run_tool("fix.py", [str(p), "--write", "--dry-run"])
        self.assertEqual(code, 2)

    def test_write_rejects_stdin(self):
        code, _out, err = run_tool("fix.py", ["--write"], stdin=b"x")
        self.assertEqual(code, 2)
        self.assertIn("--write", err)

    def test_write_rejects_symlink(self):
        target = self.dir / "t.md"
        target.write_bytes(b"see:[a](b)\n")
        link = self.dir / "l.md"
        try:
            os.symlink(str(target), str(link))
        except (OSError, NotImplementedError):
            self.skipTest("이 환경에서는 심볼릭 링크를 만들 수 없다")
        code, _out, err = run_tool("fix.py", [str(link), "--write"])
        self.assertEqual(code, 2)
        self.assertIn("symbolic link", err)
        self.assertEqual(target.read_bytes(), b"see:[a](b)\n")

    def test_symlink_check_in_atomic_write(self):
        p = self.dir / "a.md"
        p.write_bytes(b"x\n")
        with mock.patch.object(Path, "is_symlink", return_value=True):
            with self.assertRaises(core.ToolError):
                fix_module._atomic_write(p, b"x\n", b"y\n")
        self.assertEqual(p.read_bytes(), b"x\n")

    def test_changed_after_read_is_not_written(self):
        p = self.dir / "a.md"
        p.write_bytes(b"see:[a](b)\n")
        original = p.read_bytes()
        p.write_bytes(b"other\n")
        with self.assertRaises(core.ToolError):
            fix_module._atomic_write(p, original, b"see: [a](b)\n")
        self.assertEqual(p.read_bytes(), b"other\n")
        self.assertEqual(sorted(x.name for x in self.dir.iterdir()), ["a.md"])

    def test_change_while_writing_temp_is_not_overwritten(self):
        p = self.dir / "a.md"
        p.write_bytes(b"see:[a](b)\n")
        real_fsync = os.fsync

        def fsync_and_edit(fd):
            real_fsync(fd)
            p.write_bytes(b"other\n")

        with mock.patch("os.fsync", side_effect=fsync_and_edit):
            with self.assertRaises(core.ToolError):
                fix_module._atomic_write(p, b"see:[a](b)\n", b"see: [a](b)\n")
        self.assertEqual(p.read_bytes(), b"other\n")
        self.assertEqual(sorted(x.name for x in self.dir.iterdir()), ["a.md"])

    def test_failed_temp_creation_is_tool_error(self):
        p = self.dir / "a.md"
        p.write_bytes(b"x\n")
        with mock.patch("tempfile.mkstemp", side_effect=PermissionError("막힘")):
            with self.assertRaises(core.ToolError):
                fix_module._atomic_write(p, b"x\n", b"y\n")

    def test_failed_replace_leaves_no_temp(self):
        p = self.dir / "a.md"
        p.write_bytes(b"x\n")
        with mock.patch("os.replace", side_effect=OSError("막힘")):
            with self.assertRaises(core.ToolError):
                fix_module._atomic_write(p, b"x\n", b"y\n")
        self.assertEqual(sorted(x.name for x in self.dir.iterdir()), ["a.md"])
        self.assertEqual(p.read_bytes(), b"x\n")

    def test_invalid_rule_fails_before_output(self):
        fx = Fixture()
        self.addCleanup(fx.cleanup)
        fx.write(core.MECHANICAL_DIR_REL + "/bad.json",
                 '{"rule": "a", "replacements": [], "apply_in": ["prose"]}')
        code, out, err = run_tool("fix.py", ["--root", str(fx.root)], stdin=b"see:[a](b)\n")
        self.assertEqual((code, out), (2, b""))
        self.assertIn("Invalid mechanical rule", err)

    def test_invalid_rule_does_not_touch_file(self):
        fx = Fixture()
        self.addCleanup(fx.cleanup)
        fx.write(core.MECHANICAL_DIR_REL + "/bad.json", "{")
        p = self.dir / "a.md"
        p.write_bytes(b"see:[a](b)\n")
        code, _out, _err = run_tool("fix.py", ["--root", str(fx.root), str(p), "--write"])
        self.assertEqual(code, 2)
        self.assertEqual(p.read_bytes(), b"see:[a](b)\n")

    def test_invalid_utf8_input(self):
        code, _out, err = run_tool("fix.py", [], stdin=b"\xff\xfe")
        self.assertEqual(code, 2)
        self.assertIn("UTF-8", err)

    def test_missing_file(self):
        code, _out, _err = run_tool("fix.py", [str(self.dir / "없음.md")])
        self.assertEqual(code, 2)

    def test_reference_hint_skips(self):
        code, out, err = run_tool("fix.py", ["--path-hint", "reference/자료/a.md"], stdin=b"see:[a](b)\n")
        self.assertEqual((code, out), (0, b"see:[a](b)\n"))
        self.assertIn("reference", err)

    def test_absolute_path_from_other_cwd(self):
        p = self.dir / "a.md"
        p.write_bytes(b"see:[a](b)\n")
        code, out, _ = run_tool(str(TOOLS / "fix.py"), [str(p)], cwd=str(self.dir))
        self.assertEqual((code, out), (0, b"see: [a](b)\n"))


if __name__ == "__main__":
    unittest.main()
