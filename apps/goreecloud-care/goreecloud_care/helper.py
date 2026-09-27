from __future__ import annotations

import os
import subprocess
import sys

ACTIONS = {"reclaim-memory", "apt-clean"}


def _require_root() -> None:
    if os.geteuid() != 0:
        raise PermissionError("This helper must be launched through PolicyKit/pkexec")


def reclaim_memory() -> None:
    # Linux manages page cache automatically. This is an explicit, user-requested
    # maintenance action, not a promise of a lasting performance improvement.
    os.sync()
    with open("/proc/sys/vm/drop_caches", "w", encoding="ascii") as handle:
        handle.write("3\n")


def apt_clean() -> None:
    env = {
        "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": "C.UTF-8",
    }
    subprocess.run(
        ["/usr/bin/apt-get", "clean"],
        check=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        timeout=120,
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1 or args[0] not in ACTIONS:
        print("Usage: goreecloud-care-helper {reclaim-memory|apt-clean}", file=sys.stderr)
        return 64
    try:
        _require_root()
        if args[0] == "reclaim-memory":
            reclaim_memory()
        else:
            apt_clean()
        return 0
    except (OSError, PermissionError, subprocess.SubprocessError) as exc:
        print(f"GoreeCloud Care privileged action failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
