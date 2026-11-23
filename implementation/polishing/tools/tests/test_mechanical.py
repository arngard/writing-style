"""기계 규칙 파일 검증과 marker-form 적용 시험."""

import json
import unittest

from _helpers import MARKER_FORM, Fixture, core


def fix(text):
    rules = [core.load_mechanical(MARKER_FORM)]
    return core.apply_mechanical(text, rules)[0]


class MarkerFormTest(unittest.TestCase):
    def test_adds_space_before_inline_link(self):
        self.assertEqual(fix("근거다 (ref:[a.md](a.md)).\n"), "근거다 (ref: [a.md](a.md)).\n")
        self.assertEqual(fix("sub:[a](b)\nsee:[c](d)\n"), "sub: [a](b)\nsee: [c](d)\n")

    def test_reference_style_link_is_left_for_candidates(self):
        # 참조형 링크는 정의가 있는지 정규식으로 확정할 수 없어 고치지 않는다.
        text = "see:[제목][라벨]\n\n[라벨]: x.md\n"
        self.assertEqual(fix(text), text)

    def test_link_with_title_and_angle_destination(self):
        self.assertEqual(fix('see:[a](b.md "제목")\n'), 'see: [a](b.md "제목")\n')
        self.assertEqual(fix("see:[a](<b c.md>)\n"), "see: [a](<b c.md>)\n")

    def test_unconfirmed_link_forms_untouched(self):
        for text in ("see:[a](not a destination)\n", "see:[a](b(c))\n", "see:[a](b \"열림)\n",
                     "see:[a\\](b)\n", "see:[a](b\\)c)\n"):
            self.assertEqual(fix(text), text, text)

    def test_word_boundary(self):
        for text in ("resee:[a](b)\n", "xref:[a](b)\n", "subsee:[a](b)\n", "참조see:[a](b)\n",
                     "my_ref:[a](b)\n"):
            self.assertEqual(fix(text), text, text)

    def test_requires_real_link(self):
        for text in ("see:[글자만]\n", "see:[열림\n", "see:[a] (b)\n", "see:\n", "see:x\n"):
            self.assertEqual(fix(text), text, text)

    def test_uppercase_and_other_forms_untouched(self):
        for text in ("See:[a](b)\n", "REF:[a](b)\n", "see : [a](b)\n", "see:  [a](b)\n",
                     "cf.[a](b)\n", "ref.[a](b)\n"):
            self.assertEqual(fix(text), text, text)

    def test_already_correct(self):
        text = "see: [a](b)\n"
        self.assertEqual(fix(text), text)

    def test_code_quote_and_other_regions_excluded(self):
        text = (
            "---\nnote: see:[a](b)\n---\n"
            "`see:[a](b)`\n\n"
            "```\nsee:[a](b)\n```\n\n"
            "    see:[a](b)\n\n"
            "> see:[a](b)\n\n"
            "<div>\nsee:[a](b)\n</div>\n\n"
            "<!-- see:[a](b) -->\n"
        )
        self.assertEqual(fix(text), text)

    def test_link_text_containing_marker(self):
        # 링크 글자 안의 표지도 산문이고 뒤에 링크가 붙으면 고친다.
        self.assertEqual(fix("[see:[a](b)](c)\n"), "[see: [a](b)](c)\n")

    def test_prose_kinds(self):
        text = "# 제목 see:[a](b)\n\n- 항목 ref:[a](b)\n\n| sub:[a](b) | x |\n|---|---|\n\n[^n]: ref:[a](https://e.x)\n"
        expected = text.replace(":[", ": [")
        self.assertEqual(fix(text), expected)

    def test_idempotent(self):
        text = "a see:[x](y), ref:[z][w] resee:[q](r) `see:[c](d)`\n> sub:[e](f)\n"
        once = fix(text)
        self.assertNotEqual(once, text)
        self.assertEqual(fix(once), once)

    def test_crlf_preserved(self):
        self.assertEqual(fix("see:[a](b)\r\n둘\r\n"), "see: [a](b)\r\n둘\r\n")

    def test_change_report(self):
        rules = [core.load_mechanical(MARKER_FORM)]
        _new, changes = core.apply_mechanical("앞\nx see:[a](b)\n", rules)
        self.assertEqual(len(changes), 1)
        c = changes[0]
        self.assertEqual((c.rule, c.line, c.column, c.before, c.after), ("marker-form", 2, 3, "see:", "see: "))


class LoadMechanicalTest(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)

    def load(self, data):
        p = self.fx.write("r.json", json.dumps(data) if not isinstance(data, str) else data)
        return core.load_mechanical(p)

    def base(self, **rep):
        r = {"find": "a", "replace": "b", "note": "n"}
        r.update(rep)
        return {"rule": "x-y", "replacements": [r], "apply_in": ["prose"]}

    def test_valid(self):
        rule = self.load(self.base(find="(a)(b)", replace="\\2\\1"))
        self.assertEqual(rule.rule, "x-y")

    def test_invalid_cases(self):
        bad = [
            "{not json",
            [],
            dict(self.base(), extra=1),
            {"rule": "x", "replacements": [{"find": "a", "replace": "b"}]},
            dict(self.base(), rule="Bad_Name"),
            self.base(find=""),
            self.base(find="(unclosed"),
            self.base(replace="\\g<1>"),
            self.base(replace="\\0"),
            self.base(find="(a)", replace="\\2"),
            self.base(replace="a\\"),
            self.base(other="k"),
            dict(self.base(), apply_in=["nowhere"]),
            dict(self.base(), apply_in=["code_fence"]),
            dict(self.base(), apply_in=[]),
            dict(self.base(), replacements=[]),
        ]
        for data in bad:
            with self.assertRaises(core.ToolError, msg=repr(data)):
                self.load(data)

    def test_load_all_fails_before_fixing(self):
        self.fx.copy_marker_form()
        self.fx.write(core.MECHANICAL_DIR_REL + "/z-bad.json", "{}")
        with self.assertRaises(core.ToolError):
            core.load_all_mechanical(self.fx.root)

    def test_backreference_is_single_digit(self):
        rule = self.load({"rule": "b", "replacements": [{"find": "(a)", "replace": "\\10"}],
                          "apply_in": ["prose"]})
        self.assertEqual(core.apply_mechanical("a\n", [rule])[0], "a0\n")

    def test_order_of_replacements(self):
        rule = self.load({"rule": "o", "replacements": [
            {"find": "a", "replace": "b"}, {"find": "b", "replace": "c"}], "apply_in": ["prose"]})
        self.assertEqual(core.apply_mechanical("a\n", [rule])[0], "c\n")


if __name__ == "__main__":
    unittest.main()
