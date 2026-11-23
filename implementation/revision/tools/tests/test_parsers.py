"""규칙 문서, 설명 문서 파서와 레포 바깥 실행, 문법 버전 시험."""

import ast
import unittest
from pathlib import Path

from _helpers import (EXPLANATION_VOCAB, RULE_DOC_REFERENCE, RULE_DOC_VOCAB, REPO_ROOT,
                      TOOLS, Fixture, core)


class RuleDocTest(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)

    def test_sections_names_patterns_links(self):
        p = self.fx.rules("vocabulary", RULE_DOC_VOCAB)
        doc = core.parse_rule_doc(p)
        self.assertTrue(doc.named)
        self.assertEqual([s.name for s in doc.sections], ["sample-word", "indented-pattern"])
        first, second = doc.sections
        self.assertEqual(first.title, "예시 낱말을 쓰지 않는다")
        self.assertEqual([x.source for x in first.patterns], ["가나다"])
        self.assertEqual(first.explanation_links[0].section_title, "예시 낱말")
        self.assertTrue(first.explanation_links[0].target.endswith("explanations/vocabulary.md"))
        # 들여쓴 코드도 패턴이고, 같은 절 안 펜스 속 제목은 절이 아니다.
        self.assertIn("라마바", [x.source for x in second.patterns])
        self.assertEqual(len(doc.sections), 2)

    def test_mechanical_link(self):
        doc = core.parse_rule_doc(self.fx.rules("reference", RULE_DOC_REFERENCE))
        self.assertEqual(doc.sections[0].name, "marker-form")
        self.assertTrue(doc.sections[0].mechanical_links[0].target.endswith("marker-form.json"))

    def test_old_form_doc_has_no_names(self):
        doc = core.parse_rule_doc(self.fx.rules("sentence", "# 문장\n\n## 옛 절\n\n본문.\n"))
        self.assertFalse(doc.named)
        self.assertIsNone(doc.sections[0].name)

    def test_bad_pattern_is_reported(self):
        text = "## 규칙 `bad`\n\n### 후보 검출 패턴\n\n```\n(열림\n```\n"
        doc = core.parse_rule_doc(self.fx.rules("format", text))
        self.assertIsNotNone(doc.sections[0].patterns[0].error)
        with self.assertRaises(core.ToolError):
            core.compiled_patterns([doc])

    def test_pattern_fence_with_any_info_string(self):
        text = "## 규칙 `a-b`\n\n### 후보 검출 패턴\n\n~~~text\nx\\u00B7y\n~~~\n"
        doc = core.parse_rule_doc(self.fx.rules("format", text))
        pat = doc.sections[0].patterns[0]
        self.assertEqual(pat.source, "x\\u00B7y")
        self.assertTrue(pat.compiled.search("x" + chr(0xB7) + "y"))

    def test_rule_doc_paths_skip_descriptors(self):
        self.fx.rules("vocabulary", RULE_DOC_VOCAB)
        self.fx.write(core.RULES_DIR_REL + "/AGENTS.md", "# 디스크립터\n")
        self.fx.write(core.RULES_DIR_REL + "/INDEX.md", "# 색인\n")
        names = [p.name for p in core.rule_doc_paths(self.fx.root)]
        self.assertEqual(names, ["vocabulary.md"])


class ExplanationDocTest(unittest.TestCase):
    def test_rule_line(self):
        fx = Fixture()
        self.addCleanup(fx.cleanup)
        p = fx.write("e.md", EXPLANATION_VOCAB + "\n### 깊은 절\n\n규칙: `deep-one`\n\n## 규칙 없는 절\n\n본문\n"
                             "\n## 둘 걸친 절\n\n규칙: `one-a`, `one-b`\n")
        secs = {s.title: s.rules for s in core.parse_explanation_doc(p)}
        self.assertEqual(secs["예시 낱말"], ["sample-word"])
        self.assertEqual(secs["깊은 절"], ["deep-one"])
        self.assertEqual(secs["규칙 없는 절"], [])
        self.assertEqual(secs["둘 걸친 절"], ["one-a", "one-b"])

    def test_section_title_with_inner_quotes(self):
        fx = Fixture()
        self.addCleanup(fx.cleanup)
        text = ('## "짚다"는 쓰지 않는다 `jipda`\n\n본문\n\n### 설명\n\n'
                '- [v.md](../v.md) ""짚다"는 사람을 여격으로 받지 않는다"\n'
                '- [w.md](w.md)\n')
        doc = core.parse_rule_doc(fx.rules("vocabulary", text))
        links = doc.sections[0].explanation_links
        self.assertEqual(links[0].section_title, '"짚다"는 사람을 여격으로 받지 않는다')
        self.assertIsNone(links[1].section_title)
        self.assertEqual(doc.sections[0].title, '"짚다"는 쓰지 않는다')

    def test_rule_without_body_and_extra_subsections(self):
        fx = Fixture()
        self.addCleanup(fx.cleanup)
        text = ("# 문서\n\n머리말 요지.\n\n## 본문 없는 규칙 `no-body`\n\n### 설명\n\n"
                "- [v.md](v.md) \"절\"\n\n## 하위 절 규칙 `with-sub`\n\n본문\n\n### 판정\n\n"
                "`(x)` 와 [자리](x)\n\n### 설명\n\n- [v.md](v.md) \"다른 절\"\n")
        doc = core.parse_rule_doc(fx.rules("format", text))
        self.assertEqual([s.name for s in doc.sections], ["no-body", "with-sub"])
        self.assertEqual(doc.sections[1].explanation_links[0].section_title, "다른 절")
        self.assertIn("머리말 요지", doc.body())


class ReferenceMaterialTest(unittest.TestCase):
    def test_hint(self):
        self.assertTrue(core.is_reference_material("reference/자료/a.md", None))
        self.assertFalse(core.is_reference_material("reference/AGENTS/a.md", None))
        self.assertFalse(core.is_reference_material("reference/AGENTS.md", None))
        self.assertFalse(core.is_reference_material("docs/reference/a.md", None))
        self.assertFalse(core.is_reference_material(None, None))

    def test_real_path_uses_git_root(self):
        fx = Fixture()
        self.addCleanup(fx.cleanup)
        (fx.root / ".git").mkdir()
        p = fx.write("reference/자료/a.md", "x")
        q = fx.write("docs/reference/b.md", "x")
        self.assertTrue(core.is_reference_material(None, p))
        self.assertFalse(core.is_reference_material(None, q))


class RootTest(unittest.TestCase):
    def test_default_root_is_repo_root(self):
        self.assertEqual(core.DEFAULT_ROOT, REPO_ROOT)
        self.assertTrue((REPO_ROOT / core.MECHANICAL_DIR_REL / "marker-form.json").is_file())


class Python39SyntaxTest(unittest.TestCase):
    """이 머신에 3.9가 없어도 3.9 문법 범위를 넘지 않는지 본다."""

    def test_feature_version(self):
        files = sorted(TOOLS.rglob("*.py")) + [REPO_ROOT / "AGENTS/audit-checks/revision_rules.py"]
        for f in files:
            if "__pycache__" in f.parts:
                continue
            src = Path(f).read_text(encoding="utf-8")
            try:
                ast.parse(src, filename=str(f), feature_version=(3, 9))
            except SyntaxError as e:
                self.fail(f"{f}: {e}")


if __name__ == "__main__":
    unittest.main()
