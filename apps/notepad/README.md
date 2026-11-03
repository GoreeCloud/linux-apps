# GoreeCloud Notepad

A calm, **native GTK4 Linux** notepad for quick notes. Early preview **v0.1.0**; not a packaged stable release. No browser, login, analytics, network requests, or backend.

## Features

**Visual target:** the founder-supplied `GoreeCloud Notepad Interface.png` reference (31 October 2026). The UI follows its hierarchy and controls while preserving native GTK4 accessibility and save-state semantics. This source implementation has passed headless GTK smoke checks; pixel-level screenshot comparison on real desktop hardware is a separate release acceptance step.

- Edit plain-text and Markdown files as ordinary UTF-8 text.
- New, reorderable, independently closable tabs; unsaved-change indicators. The rounded, glyph-only New Tab control follows the last document tab, including after reordering or closing tabs.
- Open, Save, and Save As using native Linux file dialogs.
- **Word wrap enabled by default**, adjustable in Settings. When a note contains an unbroken run of 4,096 or more characters, the editor temporarily switches from word-aware wrapping to faster character wrapping. The status bar shows **Wrap: Fast**; ordinary wrapping resumes after the long run is shortened. This changes display layout only, not source text or the saved note. Turning wrapping off still takes precedence.
- A founder-directed **native mockup toolbar** provides a blue cloud brand mark; labeled **New / Open / Save** controls; Bold, Italic, Markdown preview, list/checklist formatting, Find, Settings, and a pinned More menu. GTK provides real minimize/maximize/close controls. At narrow widths, the action strip scrolls without hiding the More menu.
- Settings: Light (first-run default), Dark, or Follow system; word wrap and **Style Markdown while editing** toggles. Preferences: font size and monospace text.
- Unsaved-change confirmation; local-only atomic file saving; UTF-8 errors and files with embedded NUL characters are rejected before editing to prevent silent truncation or data loss.
- Mockup-led native shell: light blue chrome, a blue-highlighted rounded `Untitled.md` tab, a softly bordered white writing canvas, a compact bottom status strip, and corresponding dark surfaces. The new tab display name does not imply a file has been saved.
- Line counts use the GTK4 text buffer's actual logical lines, including CR, LF, CRLF and Unicode paragraph separators; status and cursor positions agree with editing and checklist targeting. A dedicated native test verifies caret and selection integrity when graphical checkboxes are activated.
- Live word and source-line counts, cursor position, wrap state, and truthful **Saved / Unsaved / Not saved** status with a contextual icon and tooltip. The status changes to Saved only after data is persisted to a chosen local path. A wrapped paragraph may span several screen rows while still being one source line.
- Both light and dark surfaces follow GoreeCloud UI's semantic color hierarchy.
- Native quick Find searches the active note, highlights matches, shows counts, and wraps next/previous navigation without changing file contents.
- **Native inline Markdown visuals (preview):** while editing Markdown, checklist markers render as accessible GTK checkboxes and horizontal rules render as thin separators. Clicking a checkbox changes only the `[ ]` / `[x]` source marker, preserving ordinary UTF-8 Markdown and undo/redo. Checked tasks have strike-through styling. Raw source remains in the text buffer; marker characters are only visually disguised, not deleted, so source positions and saving remain unchanged. Disable **Style Markdown while editing** in Settings for plain source display. This is not full WYSIWYG (other Markdown punctuation remains editable). Inline widgets are capped to 350 per note and disabled above 100,000 characters for responsiveness. Editing plain text below the last visible Markdown control now preserves existing overlays rather than rebuilding them; changes to Markdown markers and task labels still trigger an immediate refresh. Notes above the limit do not retain an additional visual-rendering text snapshot. Inline rules automatically recompute their visual width when the editor is resized; both rule and checkbox overlays follow horizontal and vertical document scrolling and refresh after font or wrap changes, without modifying source text.
- **Live Markdown styling while typing:** headings, emphasis, code, links, lists, and task markers are visually distinguished directly in the native editor. Formatting cues are enabled by default and may be switched off under Settings; source Markdown punctuation stays visible and editable. For responsiveness, notes above 100,000 characters or with more than 2,500 formatting spans remain unstyled but fully editable. The decoration never changes note text, creates a save, or downloads anything.
- Native Undo/Redo, keyboard shortcuts to switch tabs, direct Bold/Italic controls, a preview toggle, and a Markdown tools menu. Bold, italic, inline code, and strikethrough actions wrap or unwrap selected text (or insert paired markers at the cursor). Bullet and checklist actions insert Markdown line prefixes. The development branch additionally offers Heading 1, Heading 2, and Heading 3 actions that toggle or replace the current line's Markdown heading marker while preserving the remaining source text and supporting one-step undo/redo. All are undoable source edits; none saves the note automatically.
- Optional **read-only native Markdown preview** for headings, bullets, numbered lists, checkbox symbols, blockquotes, code fences, emphasis, and inline links (display-only). Source text and local file format remain unchanged.
- Markdown checklist boxes can be clicked in Preview to mark tasks done/undone, updating only the original `[ ]` / `[x]` marker. The change is undoable, marks the note as unsaved, and is never written to disk until Save. Use Ctrl+Enter to toggle the task at the source editor cursor.
- Preview is not a WYSIWYG editor: links are not opened, raw HTML is shown literally, and preview is limited to the first 500,000 characters. Only checkbox glyphs are interactive.
- Full WYSIWYG editing (hidden Markdown source markers), cloud sync, and persisted saved-time history are not yet implemented.

## Visual audit status

The 31 October 2026 founder mockup remains the UI target. On an isolated Ubuntu 24.04 GTK 4.14 laptop, the native GTK4 app was rendered under Xvfb at 1080×720 (light and dark) and 560×420 (light), with actual screenshot inspection. The follow-up pass corrected folder/floppy iconography and the dark-theme New/Unsaved contrast. Native GTK4 tests cover keyboard-accessible controls, responsive More menu, and accurate save state. **The editor remains a lossless Markdown source editor:** it renders native graphical checkbox and horizontal-rule overlays on top of the original Markdown source markers. PR #24 preserves editable text, real source offsets, native checkbox focus and unchanged file serialization. Disable **Style Markdown while editing** to see raw markers. Exact pixel parity, screen-reader acceptance, and additional supported-Linux display tests remain open before any Stable release.

## Accessible task controls

Native checkbox accessible names identify the source line and task text **without changing when checked state changes**; the separate GTK checkbox state conveys checked/unchecked. The editor and task controls expose accessible descriptions of keyboard actions (Ctrl+Enter from the editor, Space on the checkbox). Markdown source remains inspectable and is never rewritten for accessibility. Native GTK4 tests verify roles, keyboard focus, undo/redo focus preservation, source integrity, and preview focus restoration. **An external AT-SPI screen-reader audit is still pending**; native widget checks alone do not establish screen-reader acceptance.

## External AT-SPI accessibility audit (manual desktop acceptance)

On a Linux desktop with a running session accessibility bus, GTK4, Xvfb and the `gir1.2-atspi-2.0` introspection package installed, run `/usr/bin/python3 tests/manual_atspi_audit.py` from `apps/notepad/`. The audit starts a temporary GTK4 Notepad fixture on a **separate virtual display** with isolated configuration, then queries its AT-SPI tree from a **different process**. It checks the actual accessible editor text role, checkbox names, focusability, independent checked states and keyboard descriptions; it targets only its fixture process ID, not unrelated desktop applications. It neither saves a note nor modifies the host's installed application. A private D-Bus session on Xvfb is not yet a reliable substitute for the active desktop accessibility bus, so this test is deliberately **manual**, not a GitHub-hosted pass/fail gate.

On the Ubuntu 24.04 / GTK 4.14 laptop, the test exposed two real AT-SPI check boxes with correct labels and state. The native checkboxes reported **zero AT-SPI Action operations** in that environment, even though the in-process keyboard focus and activation tests pass. A screen reader's actual navigation, announcements and activation must therefore still be tested manually. Do **not** equate the programmatic tree inspection with complete screen-reader acceptance.

## Package-payload verification

The native CI now builds a Debian package, extracts it to an isolated temporary filesystem, validates the desktop entry, and launches the packaged GTK4 Python modules in a separate process with a private XDG profile. The test opens and saves a Markdown note and confirms user data remains intact after staged payload removal. **This does not install, upgrade, or uninstall the package on a real operating system**; clean system-level installation and upgrade remain separate release-acceptance gates.

## Isolated Debian package lifecycle check

CI performs a real `dpkg` install, a simulated upgrade from a **synthetic** version 0.0.9 package, and removal inside a disposable temporary root using unprivileged `fakeroot`. It verifies that the packaged launcher and modules appear and disappear and that an unrelated saved Markdown note survives byte-for-byte. The test does not touch the host package database, use `sudo`, or run against the user's actual desktop.

The test uses `--force-depends` **only because the disposable root has an empty dependency database**. Never use this flag for a normal user installation. This isolated lifecycle check complements staged payload and GTK runtime tests; it does **not** prove real dependency resolution, desktop integration, clean system installation, or upgrades from genuine historical releases.

## Install & run

Ubuntu 24.04+ / Debian-derived desktops with GTK 4.10 or later:

```sh
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-4.0
cd apps/notepad
./run.sh
```

Alternatively from `apps/notepad`: `PYTHONPATH=. python3 -m goreecloud_notepad`.
Files can also be passed as command-line arguments when launching.

Install a desktop menu launcher (after cloning the repo):

```sh
mkdir -p ~/.local/share/applications
sed "s|@APP_DIR@|$(pwd)|g" packaging/com.goreecloud.Notepad.desktop.in > ~/.local/share/applications/com.goreecloud.Notepad.desktop
```

The icon references GTK's built-in `accessories-text-editor` theme icon.

## Build an installable Debian package

On Ubuntu/Debian, create a local `.deb` without root permissions or downloads:

```sh
sudo apt install dpkg-dev desktop-file-utils
cd apps/notepad
python3 packaging/build_deb.py
```

This produces `dist/goreecloud-notepad_0.1.0_all.deb`. Inspect the archive with `dpkg-deb --contents dist/*.deb`; install deliberately with `sudo apt install ./dist/goreecloud-notepad_0.1.0_all.deb`. The installed command is `goreecloud-notepad`, and the desktop menu entry supports opening local text and Markdown files. System GTK4/PyGObject packages are declared as dependencies. The package requires GTK 4.10+ because native file and alert dialogs use APIs added in that version. Debian 12 Bookworm's default GTK 4.8 does not meet this requirement; do not force-install the package there.

Remove the package with `sudo apt remove goreecloud-notepad` if desired. Installation and removal do **not** delete saved notes or preferences. This is a locally buildable **preview** package, not a signed public release. No network services, build-time package downloads, or post-installation scripts are included.

## Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+T | New tab |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save as |
| Ctrl+W | Close tab |
| Ctrl+F | Find text in current note |
| Ctrl+Shift+M | Toggle Markdown preview / Edit source |
| Ctrl+Enter | Toggle the checklist item on the source cursor line |
| Ctrl+B / Ctrl+I | Bold / italic Markdown |
| Ctrl+Shift+K / Ctrl+Shift+X | Inline code / strikethrough Markdown |
| Ctrl+Alt+1 / Ctrl+Alt+2 / Ctrl+Alt+3 | Toggle or change Markdown heading H1 / H2 / H3 (development branch) |
| F3 / Shift+F3 | Next / previous search match |
| Enter / Shift+Enter | Next / previous match with search focused |
| Escape | Close search and return to editor |
| Ctrl+Z / Ctrl+Shift+Z | Undo / redo |
| Ctrl+Y | Redo |
| Ctrl+PageDown / Ctrl+PageUp | Next / previous tab |
| Ctrl+Q | Quit |

Settings saved at `$XDG_CONFIG_HOME/goreecloud/notepad/settings.json` (or `~/.config/goreecloud/notepad/settings.json`). Notes are stored **only where the user chooses to save them**. Revisions in the editor are not auto-saved. Find highlighting is temporary, does not write data to disk, and does not change the dirty status of a note.

## Tests

```sh
cd apps/notepad
python3 -m unittest discover -s tests -v
python3 -m compileall -q goreecloud_notepad
# With GTK installed:
xvfb-run -a python3 tests/gui_smoke.py
xvfb-run -a python3 tests/gui_format_smoke.py
xvfb-run -a python3 tests/gui_source_style_smoke.py
xvfb-run -a python3 tests/gui_inline_smoke.py
xvfb-run -a python3 tests/gui_inline_performance_smoke.py
```

GTK4 and PyGObject are provided by the Linux system package manager, not downloaded executable packages. This app uses GC UI semantic design guidance, not a claimed stable GC UI native SDK. License decision for the broader monorepo remains pending; no third-party assets are copied here.
