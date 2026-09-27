# Security

- The GUI does not run as root.
- Privileged helper is invoked through PolicyKit and accepts exactly one allowlisted action.
- No shell execution is used for privileged maintenance.
- User-file cleanup never follows symbolic links.
- No user-provided arbitrary deletion path is exposed in the UI.
- Trash and cache cleanup re-check current ownership before deletion where applicable.
- Package dependencies and target PolicyKit integration require acceptance before RC.

Report suspected security issues through the authoritative `GoreeCloud/goreecloud-zorin-os` repository/security reporting path.
