# Repository Notes

## GoreeCloud Care migration

- Migration target: `GoreeCloud/linux-apps/apps/goreecloud-care/`.
- Predecessor source: `GoreeCloud/zorin-os`, branch `feat/goreecloud-care`, migration baseline `43c6cdfc696f80d86505e15c732f115a7615d470`.
- Stable `0.1.0` release artifact provenance remains tied to historical exact source `bbc4779454c2887b810aa0ddc9e8a686a4c68ebd` and its recorded acceptance evidence.
- Predecessor repository history is retained as migration and rollback evidence; it is not deleted or rewritten.
- Accepted dev17 rollback source is hash-for-hash preserved on `archive/care-dev17` at `1a57ccd9b3311000c99e273877eff1af06b06b38`, with original predecessor source identity `0fda6f90a545eaf3d1bed525aae98c6529ebbf7b`.
- Owner-directed placement in `linux-apps` is an explicit repository-boundary decision for this migration. The repository-local structure keeps each application under `apps/<application>/` with its own implementation and product records.
- Active Care development lines from the predecessor repository must be carried forward before the migration is treated as fully reconciled.
