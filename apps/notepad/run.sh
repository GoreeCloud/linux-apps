#!/bin/sh
# Run the native GTK4 application without installing Python packages.
set -eu
APP_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHONPATH="$APP_DIR${PYTHONPATH:+:$PYTHONPATH}" exec python3 -m goreecloud_notepad "$@"
