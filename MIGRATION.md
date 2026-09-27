# Migration Record

## GoreeCloud Care → `GoreeCloud/linux-apps`

**Migration type:** controlled component consolidation / authority move  
**Predecessor repository:** `GoreeCloud/zorin-os`  
**Destination:** `GoreeCloud/linux-apps/apps/goreecloud-care/`  
**Stable migration baseline:** `feat/goreecloud-care` at `43c6cdfc696f80d86505e15c732f115a7615d470`  
**Stable release artifact source:** `bbc4779454c2887b810aa0ddc9e8a686a4c68ebd`

### Scope

This migration moves GoreeCloud Care source, packaging, tests, product documentation, contracts, and Care-specific CI into the dedicated Linux application repository. Zorin theme source and unrelated `zorin-os` assets are intentionally excluded.

### History and rollback

Care's predecessor commit history, release evidence, issues, pull requests, and exact artifact references remain preserved in `GoreeCloud/zorin-os`. The predecessor branch is retained as a recoverable provenance source rather than being force-rewritten or deleted. Historical URLs and exact revisions that prove the Stable `0.1.0` artifact remain historical evidence even after the canonical continuing-development location changes.

### Active development migration

At migration start, the predecessor repository contains active Care development PRs including the Glaze UI 2.2 line (`zorin-os#15`) and the Glaze UI 1.4.1 optical line (`zorin-os#17`). Their exact heads are migrated as separate destination branches and cross-linked rather than collapsed into Stable `0.1.0`.

### Verification

Migration is complete only after destination source readback, Care CI/Platform Contract validation, active-development branch recreation, predecessor record reconciliation, and downstream reference review. A copied snapshot alone is not sufficient completion evidence.
