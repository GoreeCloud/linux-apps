# GoreeCloud Linux Apps

Native Linux applications developed as part of GoreeCloud. This repository currently contains **GoreeCloud Notepad**; it is not a published suite of stable installers.

## Application

| App | Technology | Release state |
| --- | --- | --- |
| [GoreeCloud Notepad](apps/notepad/README.md) | Python, PyGObject and GTK4 | v0.1.0 early preview; no signed public release |

Notepad edits local plain-text and Markdown files. It includes tabs, native file dialogs, search, Markdown source styling, a read-only preview, and optional checklist interaction. See the [app README](apps/notepad/README.md) for exact feature boundaries, keyboard shortcuts, package-building instructions, and known limitations.

## Run Notepad locally

On Ubuntu 24.04 or a compatible Debian-derived desktop, install the system GTK4 bindings and start the app from a clone of this repository:

```sh
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-4.0
cd apps/notepad
./run.sh
```

The launcher uses the system Python and GTK4 packages. It does not install Python dependencies or contact a hosted GoreeCloud service.

## Verify the source

From `apps/notepad`:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q goreecloud_notepad
```

The app also provides GTK4 smoke tests using `xvfb-run`, plus a local Debian-package build script. Follow the [Notepad test and installation guide](apps/notepad/README.md#tests) rather than treating a successful source check as a production-release approval. The repository's [native CI workflow](.github/workflows/notepad.yml) runs unit, compilation, packaging, and virtual-display checks on relevant changes.

## Local data and release boundaries

- Notes are saved only to paths the user chooses. **Unsaved editor changes are not automatically written to disk.**
- Preferences are stored locally under the user's XDG configuration directory; the Notepad app has no login, analytics, required network service, or cloud sync.
- The available `.deb` is a **locally buildable preview**, not a signed or certified distribution. Review package contents before installing.
- Each application owns its tests, packaging, and release maturity. GoreeCloud UI styling guidance does not imply a stable native SDK or production certification.

For development details and supported shortcuts, start with [apps/notepad/README.md](apps/notepad/README.md).
