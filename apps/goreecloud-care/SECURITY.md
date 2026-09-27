# Security

- The GUI does not run as root.
- The privileged helper is invoked through PolicyKit and accepts exactly one allowlisted action.
- No shell execution is used for privileged maintenance.
- User-file cleanup never follows symbolic links.
- No user-provided arbitrary deletion path is exposed in the UI.
- Trash and cache cleanup re-check current ownership before deletion where applicable.
- Installed Python application and helper entrypoints run with `/usr/bin/python3 -I -B -m ...` so the invoking working directory, `PYTHONPATH`, and user site cannot shadow the installed `goreecloud_care` package. This is mandatory for the PolicyKit helper because that entrypoint may execute with root authority.
- Debian install/remove maintainer scripts clean only the fixed private `/usr/lib/goreecloud-care/goreecloud_care/__pycache__` path. The launchers also use `-B` to prevent new runtime bytecode writes there.
- Dev18 representative lifecycle testing exposed the pre-dev19 ambient-import-path defect after downgrade; dev19 is the remediation line and must receive exact-head source plus representative lifecycle validation before the defect is considered closed.
- Package dependencies and target PolicyKit integration require acceptance before RC.

Report suspected security issues through the authoritative `GoreeCloud/goreecloud-zorin-os` repository/security reporting path.
