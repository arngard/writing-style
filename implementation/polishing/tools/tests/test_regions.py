"""영역 판별(core.segment) 시험."""

import unittest

from _helpers import core, kind_of, kinds


class CoverageTest(unittest.TestCase):
    def test_regions_cover_text_in_order(self):
        text = "---\na: 1\n---\n# 제목\n\n본문 `x` [a](b) <i>t</i>\n\n```\nc\n```\n> q\n"
        regions = core.segment(text)
        self.assertEqual(regions[0].start, 0)
        self.assertEqual(regions[-1].end, len(text))
        for a, b in zip(regions, regions[1:]):
            self.assertEqual(a.end, b.start)

    def test_empty_text(self):
        self.assertEqual(core.segment(""), [])


class FrontMatterTest(unittest.TestCase):
    def test_front_matter(self):
        text = "---\ntitle: see:[a](b)\n---\n본문\n"
        self.assertEqual(kind_of(text, "title"), core.FRONT_MATTER)
        self.assertEqual(kind_of(text, "본문"), core.PROSE)

    def test_without_front_matter(self):
        text = "본문 see:[a](b)\n\n다음 문단\n"
        self.assertEqual(kind_of(text, "본문"), core.PROSE)
        self.assertEqual(kind_of(text, "다음"), core.PROSE)

    def test_unclosed_front_matter_is_not_prose(self):
        text = "---\ntitle: x\n본문\n"
        self.assertEqual(kind_of(text, "본문"), core.FRONT_MATTER)

    def test_dash_line_later_is_not_front_matter(self):
        text = "본문\n\n---\n\n뒤\n"
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)


class FenceTest(unittest.TestCase):
    def test_backtick_fence(self):
        text = "앞\n\n```\n안\n```\n뒤\n"
        self.assertEqual(kind_of(text, "안"), core.CODE_FENCE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_longer_fence_contains_shorter(self):
        text = "````md\n```\n안1\n```\n안2\n````\n뒤\n"
        self.assertEqual(kind_of(text, "안1"), core.CODE_FENCE)
        self.assertEqual(kind_of(text, "안2"), core.CODE_FENCE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_tilde_fence(self):
        text = "~~~\n```\n안\n~~~\n뒤\n"
        self.assertEqual(kind_of(text, "안"), core.CODE_FENCE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_tilde_not_closed_by_backticks(self):
        text = "~~~\n안\n```\n여전히\n~~~\n뒤\n"
        self.assertEqual(kind_of(text, "여전히"), core.CODE_FENCE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_unclosed_fence_runs_to_end(self):
        text = "앞\n\n```\n안\n\n# 제목\n끝\n"
        self.assertEqual(kind_of(text, "앞"), core.PROSE)
        self.assertEqual(kind_of(text, "제목"), core.CODE_FENCE)
        self.assertEqual(kind_of(text, "끝"), core.CODE_FENCE)

    def test_fence_in_list_item(self):
        text = "- 항목\n\n  ```\n  안\n  ```\n- 다음\n"
        self.assertEqual(kind_of(text, "안"), core.CODE_FENCE)
        self.assertEqual(kind_of(text, "다음"), core.PROSE)


class IndentedCodeTest(unittest.TestCase):
    def test_indented_code_after_blank(self):
        text = "문단\n\n    코드\n\n뒤\n"
        self.assertEqual(kind_of(text, "코드"), core.INDENTED_CODE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_indented_line_continuing_paragraph_is_prose(self):
        text = "문단 첫 줄\n    이어진 줄\n"
        self.assertEqual(kind_of(text, "이어진"), core.PROSE)

    def test_nested_list_is_not_code(self):
        text = "- 항목\n    - 중첩 항목\n"
        self.assertEqual(kind_of(text, "중첩"), core.PROSE)

    def test_list_paragraph_is_not_code(self):
        text = "- 항목\n\n  이어진 문단\n"
        self.assertEqual(kind_of(text, "이어진"), core.PROSE)

    def test_code_inside_list_item(self):
        text = "- 항목\n\n      코드\n"
        self.assertEqual(kind_of(text, "코드"), core.INDENTED_CODE)

    def test_blocks_on_list_item_first_line(self):
        text = "- ~~~\n  안\n  ~~~\n- > 인용\n- 산문\n"
        self.assertEqual(kind_of(text, "안"), core.CODE_FENCE)
        self.assertEqual(kind_of(text, "인용"), core.QUOTE)
        self.assertEqual(kind_of(text, "산문"), core.PROSE)

    def test_nested_list_markers_on_one_line(self):
        text = "- - > 인용\n- * ~~~\n    안\n    ~~~\n"
        self.assertEqual(kind_of(text, "인용"), core.QUOTE)
        self.assertEqual(kind_of(text, "안"), core.CODE_FENCE)

    def test_lazy_quote_line_starting_with_link(self):
        text = "> 인용 문단\n[링크](x) 이어짐\n\n뒤\n"
        self.assertEqual(kind_of(text, "이어짐"), core.QUOTE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_comment_reopened_on_closing_line(self):
        text = "본문 <!-- 첫\n\n--> <!-- 둘째\n안쪽\n-->\n\n뒤\n"
        self.assertEqual(kind_of(text, "안쪽"), core.HTML)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)
        block = "<!-- 첫 -->  <!-- 둘째\n안쪽\n-->\n\n뒤\n"
        self.assertEqual(kind_of(block, "안쪽"), core.HTML)
        self.assertEqual(kind_of(block, "뒤"), core.PROSE)

    def test_thematic_break_is_not_list(self):
        text = "- - -\n\n    코드\n"
        self.assertEqual(kind_of(text, "코드"), core.INDENTED_CODE)

    def test_tab_indented_code(self):
        text = "\n\t코드\n"
        self.assertEqual(kind_of(text, "코드"), core.INDENTED_CODE)


class QuoteTest(unittest.TestCase):
    def test_quote(self):
        text = "앞\n\n> 인용\n\n뒤\n"
        self.assertEqual(kind_of(text, "인용"), core.QUOTE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_nested_quote(self):
        text = "> 바깥\n> > 안쪽\n>> 붙은 중첩\n\n뒤\n"
        self.assertEqual(kind_of(text, "안쪽"), core.QUOTE)
        self.assertEqual(kind_of(text, "붙은"), core.QUOTE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_lazy_continuation_is_quote(self):
        text = "> 인용\n이어짐\n\n뒤\n"
        self.assertEqual(kind_of(text, "이어짐"), core.QUOTE)

    def test_code_fence_inside_quote_is_quote(self):
        text = "> ```\n> 코드\n> ```\n뒤\n"
        self.assertEqual(kind_of(text, "코드"), core.QUOTE)


class InlineTest(unittest.TestCase):
    def test_inline_code(self):
        text = "앞 `코드` 뒤\n"
        self.assertEqual(kind_of(text, "코드"), core.INLINE_CODE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_double_backtick_inline_code(self):
        text = "앞 `` a ` b `` 뒤\n"
        self.assertEqual(kind_of(text, "a"), core.INLINE_CODE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_inline_code_across_lines(self):
        text = "앞 `코드\n이어짐` 뒤\n"
        self.assertEqual(kind_of(text, "이어짐"), core.INLINE_CODE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_unmatched_backtick_makes_rest_of_paragraph_non_prose(self):
        text = "앞 `열림 그리고\n다음 줄\n\n새 문단\n"
        self.assertEqual(kind_of(text, "앞"), core.PROSE)
        self.assertEqual(kind_of(text, "다음"), core.INLINE_CODE)
        self.assertEqual(kind_of(text, "새"), core.PROSE)

    def test_link_target_and_text(self):
        text = "[글자](대상.md \"제목\") 뒤\n"
        self.assertEqual(kind_of(text, "글자"), core.PROSE)
        self.assertEqual(kind_of(text, "대상"), core.LINK_TARGET)
        self.assertEqual(kind_of(text, "제목"), core.LINK_TARGET)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_link_target_with_parentheses(self):
        text = "[a](x_(y).md) 뒤\n"
        self.assertEqual(kind_of(text, "y"), core.LINK_TARGET)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_angle_link_target_with_space(self):
        text = "[a](<경로 공백.md>) 뒤\n"
        self.assertEqual(kind_of(text, "공백"), core.LINK_TARGET)

    def test_image(self):
        text = "![대체](그림.png) 뒤\n"
        self.assertEqual(kind_of(text, "그림"), core.LINK_TARGET)

    def test_reference_style_link(self):
        text = "[글자][라벨] 뒤\n\n[라벨]: https://example.com/a \"제목\"\n"
        self.assertEqual(kind_of(text, "글자"), core.PROSE)
        self.assertEqual(kind_of(text, "라벨"), core.LINK_TARGET)
        self.assertEqual(kind_of(text, "라벨", 1), core.REF_DEFINITION)

    def test_multiline_reference_definition(self):
        text = "[id]: /target\n  \"제목 see\"\n\n[id2]:\n  /x\n  '둘째'\n뒤\n"
        self.assertEqual(kind_of(text, "제목"), core.REF_DEFINITION)
        self.assertEqual(kind_of(text, "둘째"), core.REF_DEFINITION)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_reference_definition_title_continues_from_same_line(self):
        text = '[id]: /target "제목 시작\n안쪽 see\n끝"\n뒤\n'
        self.assertEqual(kind_of(text, "안쪽"), core.REF_DEFINITION)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_reference_title_after_next_line_target(self):
        for text in ('[id]:\n  /target "제목 시작\n  안쪽 see:[a](b)"\n뒤\n',
                     '[id]: <a b.md>\n  "제목 시작\n  안쪽 see:[a](b)"\n뒤\n'):
            self.assertEqual(kind_of(text, "안쪽"), core.REF_DEFINITION, text)
            self.assertEqual(kind_of(text, "뒤"), core.PROSE, text)

    def test_title_content_is_not_a_definition(self):
        text = '[id]: real.md "제목 시작\n[example]: missing.md\n제목 끝"\n[b]: <x y.md>\n'
        links = core.extract_links(text, core.segment(text))
        self.assertEqual([x.target for x in links], ["real.md", "x y.md"])

    def test_reference_definition_in_list_is_extracted(self):
        text = "- [id]: old.md\n  - [id2]: <a b.md>\n"
        self.assertEqual(kind_of(text, "old"), core.REF_DEFINITION)
        links = core.extract_links(text, core.segment(text))
        self.assertEqual([x.target for x in links], ["old.md", "a b.md"])

    def test_multiline_reference_target_is_extracted(self):
        text = "[id]:\n  /old.md\n"
        links = core.extract_links(text, core.segment(text))
        self.assertEqual([x.target for x in links], ["/old.md"])

    def test_footnote_definition_is_prose(self):
        text = "본문[^a]\n\n[^a]: ref: [제목](https://example.com)\n"
        self.assertEqual(kind_of(text, "ref:"), core.PROSE)

    def test_link_inside_inline_code_is_code(self):
        text = "`[a](b)` 뒤\n"
        self.assertEqual(kind_of(text, "b"), core.INLINE_CODE)

    def test_autolink_and_bare_url(self):
        text = "<https://example.com/x> 와 https://example.com/y. 끝\n"
        self.assertEqual(kind_of(text, "example.com/x"), core.URL)
        self.assertEqual(kind_of(text, "example.com/y"), core.URL)
        self.assertEqual(kind_of(text, ". 끝"), core.PROSE)

    def test_inline_html_and_comment(self):
        text = "앞 <span class=\"a\">글</span> <!-- 주석 --> 뒤\n"
        self.assertEqual(kind_of(text, "span"), core.HTML)
        self.assertEqual(kind_of(text, "글"), core.PROSE)
        self.assertEqual(kind_of(text, "주석"), core.HTML)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_html_block(self):
        text = "<div>\n안\n</div>\n\n뒤\n"
        self.assertEqual(kind_of(text, "안"), core.HTML)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_unclosed_html_comment_block(self):
        text = "<!-- 열림\n끝\n"
        self.assertEqual(kind_of(text, "끝"), core.HTML)

    def test_code_inside_link_target_is_absorbed(self):
        text = "[a](foo`x`see:[b](c)) 뒤\n"
        self.assertEqual(kind_of(text, "see"), core.LINK_TARGET)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)
        regions = core.segment(text)
        for a, b in zip(regions, regions[1:]):
            self.assertEqual(a.end, b.start)

    def test_unparsed_link_destination_is_not_prose(self):
        text = "[a](b c see:[d](e)) 뒤\n"
        self.assertEqual(kind_of(text, "see"), core.LINK_TARGET)

    def test_escaped_quote_in_title(self):
        text = '[a](dest "t \\" see:[b](c)") 뒤\n'
        self.assertEqual(kind_of(text, "see"), core.LINK_TARGET)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_html_comment_across_paragraphs(self):
        text = "본문 <!-- 시작\n\n안쪽\n-->\n\n뒤\n"
        self.assertEqual(kind_of(text, "안쪽"), core.HTML)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_unclosed_inline_html_comment_runs_to_end(self):
        text = "본문 <!-- 시작\n\n끝\n"
        self.assertEqual(kind_of(text, "끝"), core.HTML)

    def test_escaped_backtick(self):
        text = "앞 \\` 뒤\n"
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)


class ProseKindsTest(unittest.TestCase):
    def test_heading_list_table_are_prose(self):
        text = "# 제목 말\n\n- 목록 말\n1. 번호 말\n\n| 칸 말 | b |\n|---|---|\n"
        for needle in ("제목", "목록", "번호", "칸"):
            self.assertEqual(kind_of(text, needle), core.PROSE, needle)


class LineEndingTest(unittest.TestCase):
    def test_crlf(self):
        text = "---\r\na: 1\r\n---\r\n본문\r\n\r\n```\r\n코드\r\n```\r\n뒤\r\n"
        self.assertEqual(kind_of(text, "a:"), core.FRONT_MATTER)
        self.assertEqual(kind_of(text, "본문"), core.PROSE)
        self.assertEqual(kind_of(text, "코드"), core.CODE_FENCE)
        self.assertEqual(kind_of(text, "뒤"), core.PROSE)

    def test_bom_is_removed_before_segmenting(self):
        raw = b"\xef\xbb\xbf---\na: 1\n---\n\xeb\xb3\xb8\n"
        text, bom = core.decode_utf8(raw, "x")
        self.assertTrue(bom)
        self.assertEqual(kind_of(text, "a:"), core.FRONT_MATTER)

    def test_invalid_utf8(self):
        with self.assertRaises(core.ToolError):
            core.decode_utf8(b"\xff\xfe", "x")

    def test_line_col(self):
        idx = core.LineIndex("가\r\n나다\n")
        self.assertEqual(idx.line_col(4), (2, 2))


if __name__ == "__main__":
    unittest.main()
