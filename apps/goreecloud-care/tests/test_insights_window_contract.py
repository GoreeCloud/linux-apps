from pathlib import Path
import unittest


class InsightsWindowContractTests(unittest.TestCase):
    def _source(self) -> str:
        return (
            Path(__file__).resolve().parents[1]
            / "goreecloud_care"
            / "insights_window.py"
        ).read_text(encoding="utf-8")

    def test_window_is_explicitly_read_only(self):
        source = self._source()
        self.assertIn('self.results = Gtk.Label(xalign=0, yalign=0)', source)
        self.assertIn('self.results.set_selectable(True)', source)
        self.assertIn('Nothing is selected or deleted automatically', source)
        self.assertNotIn('Gtk.TextView()', source)
        self.assertNotIn('.unlink(', source)
        self.assertNotIn('shutil.rmtree', source)
        self.assertNotIn('pkexec', source)
        self.assertNotIn('subprocess', source)

    def test_window_exposes_accessible_status_and_results(self):
        source = self._source()
        self.assertIn('Atk.Role.STATUSBAR', source)
        self.assertIn('Maintenance Insights results', source)
        self.assertIn('visible-data-changed', source)

    def test_large_text_page_and_results_remain_vertically_reachable(self):
        source = self._source()
        self.assertIn('self.page_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)', source)
        self.assertIn('self.results_scroll.set_min_content_height(RESULTS_MIN_HEIGHT)', source)
        self.assertIn('RESULTS_MIN_HEIGHT = 320', source)
        self.assertIn('self.results.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)', source)

    def test_results_wrap_without_synthetic_hyphens_or_copy_mutation(self):
        source = self._source()
        self.assertIn('gi.require_version("Pango", "1.0")', source)
        self.assertIn("<span insert_hyphens='false'>{escaped}</span>", source)
        self.assertIn('escaped = GLib.markup_escape_text(text)', source)
        self.assertNotIn('\\u200b', source.lower())
        self.assertNotIn('Gtk.WrapMode.CHAR', source)

    def test_compact_insights_layout_reduces_header_and_fixed_copy(self):
        source = self._source()
        self.assertIn('compact = is_compact_width(width)', source)
        self.assertIn('self.root.set_spacing(COMPACT_SPACING if compact else REGULAR_SPACING)', source)
        self.assertIn('self.header.set_title("Insights" if compact else "Maintenance Insights")', source)
        self.assertIn('self.header.set_subtitle(None if compact else self.header_subtitle)', source)
        self.assertIn("<span weight='bold'>Review storage safely</span>", source)
        self.assertIn('self.privacy_compact_text', source)
        self.assertIn('Refreshing read-only insights…', source)
        self.assertIn('No files changed.', source)

    def test_refresh_control_is_icon_only_and_explicitly_accessible(self):
        source = self._source()
        self.assertIn('self.refresh = Gtk.Button()', source)
        self.assertIn('"view-refresh-symbolic", Gtk.IconSize.BUTTON', source)
        self.assertIn('self.refresh.get_accessible().set_name("Refresh")', source)
        self.assertIn('Refresh read-only maintenance insights', source)
        self.assertNotIn('self.refresh = Gtk.Button(label="Refresh")', source)

    def test_entrypoint_has_dedicated_insights_ui_mode(self):
        entrypoint = (
            Path(__file__).resolve().parents[1]
            / "goreecloud_care"
            / "__main__.py"
        ).read_text(encoding="utf-8")
        self.assertIn('"--insights-ui"', entrypoint)
        self.assertIn('from .insights_window import main as insights_main', entrypoint)


if __name__ == "__main__":
    unittest.main()
