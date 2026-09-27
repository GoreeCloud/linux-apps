# GoreeCloud Linux Apps

`GoreeCloud/linux-apps` is the owner-directed source repository for GoreeCloud applications whose maintained implementation is Linux-only.

## Applications

- **GoreeCloud Care** — local-first GTK3 desktop maintenance application. Source: [`apps/goreecloud-care/`](apps/goreecloud-care/README.md).

## Repository layout

- `apps/` — application source, tests, packaging, and product-owned documentation.
- `.github/workflows/` — repository automation, including GoreeCloud Care qualification and Platform Contract checks.
- `MIGRATION.md` — controlled migration/provenance record for applications moved into this repository.
- `NOTES.md` — current repository administration and migration notes.

## GoreeCloud Care authority

Care development is being migrated from `GoreeCloud/zorin-os` into this repository. The predecessor Git history and pull-request records remain preserved in `GoreeCloud/zorin-os`; this repository becomes the source location for continuing Care development after migration verification. Stable `0.1.0` artifact provenance remains bound to its historical exact source and is not rewritten by the repository move.

See [`apps/goreecloud-care/README.md`](apps/goreecloud-care/README.md) for Care build, runtime, security, recovery, and release details.
