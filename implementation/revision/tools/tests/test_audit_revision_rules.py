"""감사 확장 AGENTS/audit-checks/revision_rules.py 시험. 임시 폴더 픽스처를 루트로 준다."""

import json
import subprocess
import sys
import unittest

from _helpers import (RULE_DOC_PRINCIPLES, RULE_DOC_REFERENCE, RULE_DOC_VOCAB, REPO_ROOT,
                      Fixture, core)

EXTENSION = REPO_ROOT / "AGENTS" / "audit-checks" / "revision_rules.py"


def run_ext(root):
    proc = subprocess.run([sys.executable, "-B", str(EXTENSION), str(root)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(root), timeout=120)
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
    out = []
    for line in proc.stdout.decode("ascii").splitlines():
        if line.strip():
            d = json.loads(line)
            assert set(d) == {"severity", "path", "message"}
            out.append((d["severity"], d["path"], d["message"]))
    return out


def complete(fx):
    """규칙 문서 여덟 건을 모두 이름 붙은 형태로 둔다."""
    fx.standard()
    for i, name in enumerate(core.RULE_DOC_NAMES):
        if name in ("vocabulary", "reference", "revision-principles"):
            continue
        fx.rules(name, f"# {name}\n\n## 조항 `rule-{i}`\n\n본문.\n")


class AuditExtensionTest(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)

    def test_empty_root(self):
        self.assertEqual(run_ext(self.fx.root), [])

    def test_old_form_docs_are_tolerated(self):
        self.fx.rules("vocabulary", "# 어휘\n\n## 옛 절\n\n본문\n")
        self.fx.copy_marker_form()
        self.fx.write("implementation/revision/README.md",
                      "[규칙](../../epistemic-structure/architecture/plain-prose-rules/reference.md)\n")
        found = run_ext(self.fx.root)
        self.assertTrue(found)
        self.assertTrue(all(sev == "warning" for sev, _p, _m in found), found)

    def test_complete_and_consistent(self):
        complete(self.fx)
        self.assertEqual(run_ext(self.fx.root), [])

    def test_pending_becomes_violation_when_complete(self):
        complete(self.fx)
        self.fx.rules("reference", "# 참조\n\n## 표지 형태 `marker-form`\n\n본문.\n")
        found = run_ext(self.fx.root)
        self.assertIn("violation", [s for s, _p, _m in found])
        self.assertTrue(any("marker-form.json" in p for _s, p, _m in found))

    def test_missing_and_duplicate_names(self):
        complete(self.fx)
        self.fx.rules("sentence", "# 문장\n\n## 조항 `rule-2`\n\n## 이름 없음\n\n## 대문자 `Bad`\n")
        msgs = [m for s, _p, m in run_ext(self.fx.root) if s == "violation"]
        self.assertTrue(any("규칙 이름이 없다" in m for m in msgs), msgs)
        self.assertTrue(any("중복" in m for m in msgs), msgs)
        self.assertTrue(any("케밥" in m for m in msgs), msgs)

    def test_bad_regex_and_empty_patterns(self):
        complete(self.fx)
        self.fx.rules("format", "# 서식\n\n## 가 `fmt-a`\n\n### 후보 검출 패턴\n\n```\n(열림\n```\n\n"
                                "## 나 `fmt-b`\n\n### 후보 검출 패턴\n\n없음\n")
        msgs = [m for s, _p, m in run_ext(self.fx.root) if s == "violation"]
        self.assertTrue(any("컴파일" in m for m in msgs), msgs)
        self.assertTrue(any("정규식이 없다" in m for m in msgs), msgs)

    def test_mechanical_rule_value_mismatch(self):
        complete(self.fx)
        self.fx.write(core.MECHANICAL_DIR_REL + "/marker-form.json",
                      '{"rule": "other-name", "replacements": [{"find": "a", "replace": "b"}],'
                      ' "apply_in": ["prose"]}')
        msgs = [m for s, _p, m in run_ext(self.fx.root) if s == "violation"]
        self.assertTrue(any("rule 값이 `other-name`" in m for m in msgs), msgs)

    def test_invalid_mechanical_json(self):
        complete(self.fx)
        self.fx.write(core.MECHANICAL_DIR_REL + "/broken.json", "{")
        found = run_ext(self.fx.root)
        self.assertIn(("violation", core.MECHANICAL_DIR_REL + "/broken.json"),
                      [(s, p) for s, p, _m in found])

    def test_explanation_both_directions(self):
        complete(self.fx)
        # 규칙 줄이 다른 규칙을 가리킨다.
        self.fx.write(core.EXPLANATIONS_DIR_REL + "/vocabulary.md",
                      "# 설명\n\n## 예시 낱말\n\n규칙: `indented-pattern`\n\n## 외톨이\n\n규칙: `rule-1`\n")
        msgs = [m for s, _p, m in run_ext(self.fx.root) if s == "violation"]
        self.assertTrue(any("규칙 줄이 `sample-word`이 아니다" in m for m in msgs), msgs)
        self.assertTrue(any("\"외톨이\"을 규칙 `rule-1`" in m for m in msgs), msgs)

    def test_explanation_section_missing(self):
        complete(self.fx)
        self.fx.write(core.EXPLANATIONS_DIR_REL + "/vocabulary.md", "# 설명\n\n## 다른 절\n\n본문\n")
        msgs = [m for s, _p, m in run_ext(self.fx.root) if s == "violation"]
        self.assertTrue(any("\"예시 낱말\"이" in m and "없다" in m for m in msgs), msgs)

    def test_revision_doc_links(self):
        complete(self.fx)
        self.fx.write("implementation/revision/workflows/a.md",
                      "[있음](../README.md) [없음](nothing.md) [밖](https://e.x) [앵커](#x)\n\n"
                      "`[코드](skip.md)`\n\n```\n[펜스](skip2.md)\n```\n")
        self.fx.write("implementation/revision/README.md", "# 안내\n\n- [id]: list-missing.md\n")
        found = run_ext(self.fx.root)
        self.assertEqual(sorted((s, p) for s, p, _m in found),
                         [("violation", "implementation/revision/README.md"),
                          ("violation", "implementation/revision/workflows/a.md")])
        messages = " ".join(m for _s, _p, m in found)
        self.assertIn("nothing.md", messages)
        self.assertIn("list-missing.md", messages)

    def test_output_is_ascii_json(self):
        self.fx.rules("vocabulary", RULE_DOC_VOCAB)
        self.fx.rules("reference", RULE_DOC_REFERENCE)
        self.fx.rules("revision-principles", RULE_DOC_PRINCIPLES)
        proc = subprocess.run([sys.executable, "-B", str(EXTENSION), str(self.fx.root)],
                              stdout=subprocess.PIPE, timeout=120)
        proc.stdout.decode("ascii")


if __name__ == "__main__":
    unittest.main()
