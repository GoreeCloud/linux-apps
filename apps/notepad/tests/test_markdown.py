"""Pure parser tests: no display server or GTK required."""
import unittest

from goreecloud_notepad.markdown import inline_runs, parse_markdown


class MarkdownTests(unittest.TestCase):
    def test_headings_and_emphasis(self):
        lines = parse_markdown("# Product **Ideas**\n## Tasks\n### Notes")
        self.assertEqual([line.block for line in lines], ["h1", "h2", "h3"])
        self.assertEqual(lines[0].runs[-1].style, "bold")
        self.assertEqual("".join(run.text for run in lines[0].runs), "Product Ideas")

    def test_checklists_and_lists(self):
        lines = parse_markdown("- [x] Finished\n- [ ] Pending\n- **Point**\n1. First")
        self.assertEqual(lines[0].runs[0].text, "☑ ")
        self.assertEqual(lines[1].runs[0].text, "☐ ")
        self.assertEqual(lines[2].runs[0].text, "• ")
        self.assertEqual(lines[3].runs[0].text, "1. ")
        self.assertTrue(all(line.block == "list" for line in lines))

    def test_code_fence_is_literal(self):
        fence = chr(96) * 3
        lines = parse_markdown("~~~not a fence\n" + fence + "python\n# not a heading\n**not bold**\n" + fence + "\n")
        self.assertEqual(lines[1].block, "code")
        self.assertEqual(lines[1].runs[0].text, "# not a heading")
        self.assertEqual(lines[2].runs[0].text, "**not bold**")

    def test_html_and_unknown_markup_are_plain_text(self):
        raw = '<script>alert("x")</script>'
        runs = inline_runs(raw)
        self.assertEqual(runs[0].text, raw)
        self.assertEqual(runs[0].style, "")
        self.assertEqual(parse_markdown("@tag")[0].runs[0].text, "@tag")

    def test_links_are_text_only(self):
        line = parse_markdown("Read [the guide](https://example.invalid/path).")[0]
        self.assertEqual("".join(run.text for run in line.runs), "Read the guide.")
        self.assertEqual(line.runs[1].style, "link")

    def test_empty_and_quotes(self):
        self.assertEqual(parse_markdown("")[0].block, "blank")
        self.assertEqual(parse_markdown("> Important")[0].block, "quote")

    def test_inline_code_and_strike(self):
        marker = chr(96)
        runs = inline_runs("Use " + marker + "code" + marker + " and ~~old~~ text.")
        self.assertIn("code", [r.style for r in runs])
        self.assertIn("strike", [r.style for r in runs])


if __name__ == "__main__":
    unittest.main()
