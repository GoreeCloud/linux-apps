#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
python3 -m compileall -q goreecloud_care tests
python3 -m unittest discover -s tests -v
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
for p in [
    Path('packaging/com.goreecloud.care.policy'),
    Path('packaging/com.goreecloud.care.dev.metainfo.xml'),
]:
    ET.parse(p)
print('XML validation: passed')
PY
# Security/source invariants for the privileged boundary.
grep -F '["/usr/bin/apt-get", "clean"]' goreecloud_care/helper.py >/dev/null
! grep -R --line-number -E 'shell[[:space:]]*=[[:space:]]*True|os\.system\(' goreecloud_care packaging scripts
# Adaptive/accessibility invariants for current Development.
grep -F 'self.set_size_request(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)' goreecloud_care/app.py >/dev/null
grep -F 'def _apply_layout(' goreecloud_care/app.py >/dev/null
grep -F 'compact = is_compact_width(width)' goreecloud_care/app.py >/dev/null
grep -F 'self.header.set_subtitle(None if compact else self.header_subtitle)' goreecloud_care/app.py >/dev/null
grep -F 'COMPACT_WIDTH = 820' goreecloud_care/ui_contract.py >/dev/null
grep -F 'GDK_DPI_SCALE' goreecloud_care/ui_contract.py >/dev/null
grep -F 'def effective_layout_width(' goreecloud_care/ui_contract.py >/dev/null
grep -F 'Atk.Role.STATUSBAR' goreecloud_care/app.py >/dev/null
grep -F 'visible-data-changed' goreecloud_care/app.py >/dev/null
grep -F 'is_high_contrast_theme' goreecloud_care/app.py >/dev/null
grep -F 'GTK_THEME' goreecloud_care/ui_contract.py >/dev/null
grep -F 'gtk_theme_override' goreecloud_care/ui_contract.py >/dev/null
grep -F 'GLib.set_prgname("GoreeCloud Care")' goreecloud_care/__main__.py >/dev/null
grep -F 'GLib.set_application_name("GoreeCloud Care")' goreecloud_care/__main__.py >/dev/null
grep -F 'install_focus_resilience_provider' goreecloud_care/__main__.py >/dev/null
grep -F 'Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION - 1' goreecloud_care/focus_resilience.py >/dev/null
grep -F '@theme_fg_color' goreecloud_care/focus_resilience.py >/dev/null
grep -F 'button:focus, checkbutton:focus' goreecloud_care/focus_resilience.py >/dev/null
grep -F 'gir1.2-atk-1.0' scripts/build-deb.sh >/dev/null
# Privacy-safe read-only report invariants retained from dev13.
grep -F -- '"--report"' goreecloud_care/__main__.py >/dev/null
grep -F -- '"--report-json"' goreecloud_care/__main__.py >/dev/null
grep -F 'contains_file_paths' goreecloud_care/reporting.py >/dev/null
grep -F 'contains_raw_scan_errors' goreecloud_care/reporting.py >/dev/null
grep -F 'read-only-local-maintenance-report' goreecloud_care/reporting.py >/dev/null
grep -F 'classify_disk_headroom' goreecloud_care/reporting.py >/dev/null
# Maintenance Insights must remain bounded, local, review-only, and large-text reachable.
grep -F -- '"--insights-ui"' goreecloud_care/__main__.py >/dev/null
grep -F 'MAX_VISITED_ENTRIES = 50_000' goreecloud_care/insights.py >/dev/null
grep -F 'STANDARD_USER_DIRS' goreecloud_care/insights.py >/dev/null
grep -F 'def build_insights(' goreecloud_care/insights.py >/dev/null
grep -F 'self.results = Gtk.Label(xalign=0, yalign=0)' goreecloud_care/insights_window.py >/dev/null
grep -F 'self.results.set_selectable(True)' goreecloud_care/insights_window.py >/dev/null
grep -F 'Atk.Role.STATUSBAR' goreecloud_care/insights_window.py >/dev/null
grep -F 'self.page_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)' goreecloud_care/insights_window.py >/dev/null
grep -F 'self.results_scroll.set_min_content_height(RESULTS_MIN_HEIGHT)' goreecloud_care/insights_window.py >/dev/null
grep -F 'self.results.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)' goreecloud_care/insights_window.py >/dev/null
grep -F "<span insert_hyphens='false'>{escaped}</span>" goreecloud_care/insights_window.py >/dev/null
! grep -F 'Gtk.WrapMode.CHAR' goreecloud_care/insights_window.py >/dev/null
grep -F 'compact = is_compact_width(width)' goreecloud_care/insights_window.py >/dev/null
grep -F 'self.header.set_subtitle(None if compact else self.header_subtitle)' goreecloud_care/insights_window.py >/dev/null
grep -F 'self.root.set_spacing(COMPACT_SPACING if compact else REGULAR_SPACING)' goreecloud_care/insights_window.py >/dev/null
grep -F 'view-refresh-symbolic' goreecloud_care/insights_window.py >/dev/null
grep -F 'self.refresh.get_accessible().set_name("Refresh")' goreecloud_care/insights_window.py >/dev/null
grep -F "<span weight='bold'>Review storage safely</span>" goreecloud_care/insights_window.py >/dev/null
grep -F 'Refreshing read-only insights…' goreecloud_care/insights_window.py >/dev/null
grep -F 'Maintenance Insights (Read-only)' packaging/com.goreecloud.care.dev.desktop >/dev/null
! grep -R --line-number -E '\.unlink\(|shutil\.rmtree|os\.remove|subprocess|pkexec' goreecloud_care/insights.py goreecloud_care/insights_window.py
# Post-action completion must survive the automatic values refresh.
grep -F 'def _refresh_after_action(' goreecloud_care/app.py >/dev/null
grep -F 'def _refresh_after_action_done(' goreecloud_care/app.py >/dev/null
grep -F 'self._show_notice(completion_title, outcome.message, Gtk.MessageType.INFO)' goreecloud_care/app.py >/dev/null
grep -F 'self._refresh_after_action(outcome.message, "success", completion_title)' goreecloud_care/app.py >/dev/null
# Mandatory GoreeCloud component documentation.
for f in README.md SPECIFICATIONS.md FEATURES.md BENEFITS.md CAPABILITIES.md COMPETITIVE-OBJECTIVES.md BRANDING.md USER-MANUAL.md LICENSE CHANGELOG.md goreecloud.platform.yaml; do
  test -s "$f"
done
echo 'Local source validation: passed'
