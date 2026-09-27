from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os
import re
import stat
from typing import Any

from . import __version__

API_VERSION = "1"
PACKAGE_VERSION = "0.1.0"
BUILD_PROVENANCE_PATH = Path("/usr/share/goreecloud-care/build-provenance.json")
REPRESENTATIVE_ACCEPTANCE_PATH = Path(
    "/var/lib/goreecloud-care/acceptance/representative-target.json"
)
EVERKEEP_ACCEPTANCE_PATH = Path(
    "/var/lib/goreecloud/everkeep/acceptance/goreecloud-care.target-runtime.json"
)
REPRESENTATIVE_TARGET_TOKEN = "Zorin OS 17.3"
MAX_EVIDENCE_BYTES = 64 * 1024
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PRIVACY_CAPABILITIES = (
    "telemetry-minimization",
    "data-minimization",
    "privacy-status",
)


def _utc_now(now: datetime | None = None) -> datetime:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def build_health_status(now: datetime | None = None) -> dict[str, Any]:
    observed = _utc_now(now)
    return {
        "schema_version": API_VERSION,
        "product": "GoreeCloud Care",
        "version": __version__,
        "state": "ready",
        "observed_at": _iso(observed),
        "local_only": True,
        "network_used": False,
        "telemetry_used": False,
        "privileged_action_performed": False,
    }


def build_privacy_status(
    now: datetime | None = None,
    *,
    production_approved: bool = False,
) -> dict[str, Any]:
    observed = _utc_now(now)
    state = "protected" if production_approved else "development"
    capability_state = "active" if production_approved else "pending-acceptance"
    payload: dict[str, Any] = {
        "schema_version": 1,
        "producer": {
            "adapter_id": "goreecloud-care",
            "product": "GoreeCloud Care",
            "runtime_authority": "GoreeCloud/goreecloud-zorin-os",
            "adapter_contract_version": 1,
        },
        "generated_at": _iso(observed),
        "state": state,
        "capabilities": [
            {"id": capability, "state": capability_state}
            for capability in PRIVACY_CAPABILITIES
        ],
        "privacy": {
            "raw_private_activity_included": False,
            "contains_credentials": False,
            "contains_identifiers": False,
        },
        "acceptance": {
            "runtime_acceptance_required": True,
            "production_approved": production_approved,
        },
    }
    if production_approved:
        payload["valid_until"] = _iso(observed + timedelta(minutes=15))
    return payload


def _secure_root_owned_file(path: Path, *, expected_uid: int = 0, executable: bool = False) -> bool:
    try:
        st = path.lstat()
    except OSError:
        return False
    if not stat.S_ISREG(st.st_mode) or st.st_uid != expected_uid:
        return False
    if st.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        return False
    if executable and not (st.st_mode & stat.S_IXUSR):
        return False
    return True


def _secure_evidence_file(path: Path, *, expected_uid: int = 0) -> bool:
    if not _secure_root_owned_file(path, expected_uid=expected_uid):
        return False
    try:
        parent = path.parent.lstat()
    except OSError:
        return False
    if not stat.S_ISDIR(parent.st_mode) or parent.st_uid != expected_uid:
        return False
    if parent.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        return False
    return True


def _load_secure_json(
    path: str | Path,
    *,
    expected_uid: int = 0,
) -> tuple[dict[str, Any] | None, str]:
    candidate = Path(path)
    if not _secure_evidence_file(candidate, expected_uid=expected_uid):
        return None, "missing-or-untrusted"
    try:
        if candidate.stat().st_size > MAX_EVIDENCE_BYTES:
            return None, "oversized"
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None, "malformed"
    if not isinstance(payload, dict):
        return None, "malformed"
    return payload, "loaded"


def evaluate_privileged_boundary(
    helper_path: str | Path = "/usr/lib/goreecloud-care/goreecloud-care-helper",
    policy_path: str | Path = "/usr/share/polkit-1/actions/com.goreecloud.care.policy",
    pkexec_path: str | Path = "/usr/bin/pkexec",
    *,
    expected_uid: int = 0,
) -> dict[str, bool]:
    helper = Path(helper_path)
    policy = Path(policy_path)
    pkexec = Path(pkexec_path)
    return {
        "helper_root_owned_nonwritable": _secure_root_owned_file(
            helper, expected_uid=expected_uid, executable=True
        ),
        "policy_root_owned_nonwritable": _secure_root_owned_file(
            policy, expected_uid=expected_uid, executable=False
        ),
        "pkexec_available": pkexec.is_file() and os.access(pkexec, os.X_OK),
    }


def build_wardveil_status(
    now: datetime | None = None,
    *,
    helper_path: str | Path = "/usr/lib/goreecloud-care/goreecloud-care-helper",
    policy_path: str | Path = "/usr/share/polkit-1/actions/com.goreecloud.care.policy",
    pkexec_path: str | Path = "/usr/bin/pkexec",
    expected_uid: int = 0,
) -> dict[str, Any]:
    observed = _utc_now(now)
    checks = evaluate_privileged_boundary(
        helper_path,
        policy_path,
        pkexec_path,
        expected_uid=expected_uid,
    )
    passing = all(checks.values())
    summary = (
        "Installed Care privileged boundary passed root-ownership, write-permission, and pkexec checks."
        if passing
        else "Care privileged-boundary evidence is incomplete or non-passing."
    )
    payload: dict[str, Any] = {
        "contract_version": "0.1.0",
        "scope": {
            "kind": "application",
            "id": "goreecloud-care",
            "display_name": "GoreeCloud Care",
        },
        "authority": {
            "system": "GoreeCloud Care",
            "control": "local-maintenance-privilege-boundary",
            "authoritative": True,
        },
        "state": "protected" if passing else "attention",
        "source_state": "passing" if passing else "non-passing",
        "evidence": {
            "status": "current",
            "observed_at": _iso(observed),
            "summary": summary,
            "reference": "local-cli://goreecloud-care/security-status",
        },
        "claim": {"protected_by_wardveil": False},
        "privacy": {
            "details_withheld": True,
            "redactions": [
                "local filesystem paths beyond fixed installation locations",
                "user identity",
                "raw privileged command output",
            ],
        },
    }
    if passing:
        payload["evidence"]["valid_until"] = _iso(observed + timedelta(minutes=15))
    return payload


def _valid_build_provenance(payload: dict[str, Any]) -> bool:
    return (
        payload.get("schema_version") == 1
        and payload.get("application") == "GoreeCloud Care"
        and payload.get("producer") == "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care"
        and payload.get("runtime_version") == __version__
        and payload.get("package_version") == PACKAGE_VERSION
        and isinstance(payload.get("source_revision"), str)
        and bool(_SHA1_RE.fullmatch(payload["source_revision"]))
        and isinstance(payload.get("source_tree"), str)
        and bool(_SHA1_RE.fullmatch(payload["source_tree"]))
        and isinstance(payload.get("source_date_epoch"), int)
        and payload["source_date_epoch"] >= 0
        and payload.get("package_sha256_embedded") is False
    )


def _acceptance_matches_build(
    acceptance: dict[str, Any],
    provenance: dict[str, Any],
    *,
    require_promoted: bool,
) -> bool:
    candidate = acceptance.get("candidate")
    target = acceptance.get("target")
    evidence = acceptance.get("evidence")
    decision = acceptance.get("acceptance")
    dimensions = acceptance.get("dimensions")
    if not all(
        isinstance(item, dict)
        for item in (candidate, target, evidence, decision)
    ) or not isinstance(dimensions, list):
        return False
    package_sha = candidate.get("package_sha256")
    target_name = target.get("name")
    if not isinstance(package_sha, str) or not _SHA256_RE.fullmatch(package_sha):
        return False
    if not isinstance(target_name, str) or REPRESENTATIVE_TARGET_TOKEN not in target_name:
        return False
    exact_identity = (
        candidate.get("source_revision") == provenance["source_revision"]
        and candidate.get("source_tree") == provenance["source_tree"]
        and candidate.get("runtime_version") == provenance["runtime_version"]
        and candidate.get("package_version") == provenance["package_version"]
    )
    accepted_target = (
        acceptance.get("schema_version") == 1
        and acceptance.get("application") == "GoreeCloud Care"
        and acceptance.get("producer") == "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care"
        and target.get("representative") is True
        and target.get("status") == "passed"
        and "restore_capability" in dimensions
        and "provenance" in dimensions
        and evidence.get("source_validation") == "passed"
        and evidence.get("package_lifecycle") == "passed"
        and isinstance(evidence.get("local_tests"), int)
        and evidence["local_tests"] >= 1
        and isinstance(evidence.get("references"), list)
        and bool(evidence["references"])
        and decision.get("target_runtime_status") == "passed"
        and decision.get("exact_revision_accepted") is True
        and isinstance(decision.get("freshness_rule"), str)
        and bool(decision["freshness_rule"].strip())
    )
    if not (exact_identity and accepted_target):
        return False
    if require_promoted:
        return (
            decision.get("everkeep_integration_promoted") is True
            and decision.get("everkeep_ready_promoted") is True
        )
    return True


def evaluate_continuity_evidence(
    *,
    provenance_path: str | Path = BUILD_PROVENANCE_PATH,
    representative_acceptance_path: str | Path = REPRESENTATIVE_ACCEPTANCE_PATH,
    everkeep_acceptance_path: str | Path = EVERKEEP_ACCEPTANCE_PATH,
    expected_uid: int = 0,
) -> dict[str, Any]:
    provenance, provenance_state = _load_secure_json(
        provenance_path,
        expected_uid=expected_uid,
    )
    if provenance is None or not _valid_build_provenance(provenance):
        return {
            "state": "attention",
            "stage": "provenance-unavailable",
            "evidence_reference": None,
            "reason": "Installed build provenance is missing, untrusted, or does not match this Care runtime.",
            "limitations": [
                "Exact candidate identity must be available from a protected package-owned provenance record."
            ],
            "provenance_state": provenance_state,
        }

    representative, representative_state = _load_secure_json(
        representative_acceptance_path,
        expected_uid=expected_uid,
    )
    representative_matches = (
        representative is not None
        and _acceptance_matches_build(
            representative,
            provenance,
            require_promoted=False,
        )
    )

    everkeep, everkeep_state = _load_secure_json(
        everkeep_acceptance_path,
        expected_uid=expected_uid,
    )
    everkeep_matches = (
        everkeep is not None
        and _acceptance_matches_build(
            everkeep,
            provenance,
            require_promoted=True,
        )
    )

    package_identity_matches = (
        representative_matches
        and everkeep_matches
        and representative["candidate"]["package_sha256"]
        == everkeep["candidate"]["package_sha256"]
    )
    if package_identity_matches:
        return {
            "state": "ready",
            "stage": "everkeep-promoted",
            "evidence_reference": f"file://{Path(everkeep_acceptance_path)}",
            "reason": "Exact representative-target rollback evidence and package identity are accepted and Everkeep integration/readiness are governed as promoted.",
            "limitations": [],
            "provenance_state": "matched",
        }

    if representative_matches:
        limitation = (
            "Care-produced target acceptance evidence cannot grant Everkeep readiness by itself."
        )
        if everkeep_matches and not package_identity_matches:
            limitation = (
                "Governed Everkeep evidence does not match the representative target package SHA-256 for this exact build."
            )
        return {
            "state": "attention",
            "stage": "target-accepted-governance-pending",
            "evidence_reference": f"file://{Path(representative_acceptance_path)}",
            "reason": "Representative-device package lifecycle is accepted for this exact build; exact package identity and governed Everkeep integration/readiness promotion are still required.",
            "limitations": [limitation],
            "provenance_state": "matched",
            "everkeep_state": everkeep_state,
        }

    return {
        "state": "attention",
        "stage": "target-acceptance-required",
        "evidence_reference": None,
        "reason": "Representative-device uninstall/downgrade/rollback acceptance is still required for this exact build.",
        "limitations": [
            "Source validation and package construction do not prove target-device rollback."
        ],
        "provenance_state": "matched",
        "representative_state": representative_state,
        "everkeep_state": everkeep_state,
    }


def build_continuity_status(
    now: datetime | None = None,
    *,
    provenance_path: str | Path = BUILD_PROVENANCE_PATH,
    representative_acceptance_path: str | Path = REPRESENTATIVE_ACCEPTANCE_PATH,
    everkeep_acceptance_path: str | Path = EVERKEEP_ACCEPTANCE_PATH,
    expected_uid: int = 0,
) -> dict[str, Any]:
    observed = _utc_now(now)
    evaluation = evaluate_continuity_evidence(
        provenance_path=provenance_path,
        representative_acceptance_path=representative_acceptance_path,
        everkeep_acceptance_path=everkeep_acceptance_path,
        expected_uid=expected_uid,
    )
    payload: dict[str, Any] = {
        "record_id": f"goreecloud-care-package-rollback-{observed.strftime('%Y%m%dT%H%M%SZ')}",
        "producer": "GoreeCloud Care",
        "scope": "goreecloud-care Debian package lifecycle",
        "dimension": "restore_capability",
        "state": evaluation["state"],
        "stage": evaluation["stage"],
        "observed_at": _iso(observed),
        "required_evidence": True,
        "verification_method": (
            "Representative-device install, upgrade, uninstall/reinstall, downgrade, rollback validation, and governed Everkeep promotion."
        ),
        "evidence_reference": evaluation["evidence_reference"],
        "reason": evaluation["reason"],
        "limitations": evaluation["limitations"],
    }
    if evaluation["state"] == "ready":
        payload["freshness"] = "exact-build-bound"
    return payload
