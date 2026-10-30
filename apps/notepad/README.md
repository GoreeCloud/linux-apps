# GoreeCloud Notepad

A calm, **native GTK4 Linux** notepad for quick notes. Early preview **v0.1.0**; not a packaged stable release. No browser, login, analytics, network requests, or backend.

## Features

- Edit plain-text and Markdown files as ordinary UTF-8 text.
- New, reorderable, independently closable tabs; unsaved-change indicators.
- Open, Save, and Save As using native Linux file dialogs.
- **Word wrap enabled by default**, adjustable in Settings.
- All requested File, New Tab, Preferences, and Settings **glyph-only controls live in the native title bar**, alongside native minimize, maximize, and close controls provided by the window manager.
- Settings: Light (first-run default), Dark, or Follow system; wrap option. Preferences: font size and monospace text.
- Unsaved-change confirmation; local-only atomic file saving; UTF-8 errors displayed rather than silently changing content.
- Mockup-inspired native shell: left-aligned identity, blue document tabs, a rounded writing surface, and compact glyph controls.
- Live word and line counts, cursor position, wrap state, and honest local save status.
- Both light and dark surfaces follow GoreeCloud UI's semantic color hierarchy.
- Native quick Find searches the active note, highlights matches, shows counts, and wraps next/previous navigation without changing file contents.
- Native Undo/Redo, plus keyboard shortcuts to switch between tabs.
- Optional **read-only native Markdown preview** for headings, bullets, numbered lists, checkbox symbols, blockquotes, code fences, emphasis, and inline links (display-only). Source text and local file format remain unchanged.
- Markdown checklist boxes can be clicked in Preview to mark tasks done/undone, updating only the original `[ ]` / `[x]` marker. The change is undoable, marks the note as unsaved, and is never written to disk until Save. Use Ctrl+Enter to toggle the task at the source editor cursor.
- Preview is not a WYSIWYG editor: links are not opened, raw HTML is shown literally, and preview is limited to the first 500,000 characters. Only checkbox glyphs are interactive.
- Cloud sync, interactive rich text, and persisted saved-time history are not yet implemented.

## Install & run

Ubuntu 24.04+ / Debian-derived desktops:

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
```

GTK4 and PyGObject are provided by the Linux system package manager, not downloaded executable packages. This app uses GC UI semantic design guidance, not a claimed stable GC UI native SDK. License decision for the broader monorepo remains pending; no third-party assets are copied here.
