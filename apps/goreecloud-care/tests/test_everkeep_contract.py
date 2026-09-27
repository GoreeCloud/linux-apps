from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"


class EverkeepContractTests(unittest.TestCase):
    def test_adoption_manifest_is_read_only_and_fail_closed(self) -> None:
        adoption = json.loads((CONTRACTS / "everkeep.adoption.json").read_text(encoding="utf-8"))
        self.assertEqual(adoption["schema_version"], 1)
        self.assertEqual(adoption["project"], "GoreeCloud Care")
        self.assertEqual(adoption["role"], "producer")
        self.assertTrue(adoption["read_only"])
        self.assertTrue(adoption["fail_closed"])
        self.assertEqual(adoption["status_schema"], "contracts/continuity.status.schema.json")
        self.assertIn("restore_capability", adoption["dimensions"])
        self.assertIn("provenance", adoption["dimensions"])

    def test_continuity_status_schema_exists_and_blocks_unpromoted_ready(self) -> None:
        schema_path = CONTRACTS / "continuity.status.schema.json"
        self.assertTrue(schema_path.is_file())
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["producer"]["const"], "GoreeCloud Care")
        self.assertEqual(schema["properties"]["dimension"]["const"], "restore_capability")
        self.assertEqual(set(schema["properties"]["state"]["enum"]), {"attention", "ready"})
        self.assertIn("everkeep-promoted", schema["properties"]["stage"]["enum"])
        ready_rule = schema["allOf"][0]["then"]
        self.assertEqual(ready_rule["properties"]["stage"]["const"], "everkeep-promoted")
        self.assertEqual(ready_rule["properties"]["freshness"]["const"], "exact-build-bound")
        self.assertEqual(ready_rule["properties"]["limitations"]["maxItems"], 0)

    def test_acceptance_policy_cannot_claim_ready_before_target_acceptance(self) -> None:
        policy = json.loads((CONTRACTS / "everkeep.acceptance.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["schema_version"], 1)
        self.assertEqual(policy["application"], "GoreeCloud Care")
        self.assertEqual(policy["status_schema"], "contracts/continuity.status.schema.json")
        self.assertTrue(policy["freshness"]["required_for_ready"])
        self.assertIn("exact immutable Care candidate", policy["freshness"]["rule"])
        self.assertFalse(policy["acceptance"]["everkeep_integrated"])
        self.assertFalse(policy["acceptance"]["everkeep_ready"])
        self.assertTrue(policy["acceptance"]["target_runtime_acceptance_required"])
        self.assertTrue(policy["acceptance"]["exact_revision_acceptance_required"])
        self.assertTrue(policy["acceptance"]["separate_everkeep_governance_required"])
        self.assertFalse(policy["authority"]["care_may_promote_everkeep"])
        self.assertTrue(policy["authority"]["ready_requires_exact_match_between_records"])
        self.assertEqual(
            policy["authority"]["care_owned_target_record"],
            "/var/lib/goreecloud-care/acceptance/representative-target.json",
        )
        self.assertEqual(
            policy["authority"]["everkeep_governance_record"],
            "/var/lib/goreecloud/everkeep/acceptance/goreecloud-care.target-runtime.json",
        )
        self.assertFalse(
            policy["acceptance"]["everkeep_ready"]
            and not policy["acceptance"]["everkeep_integrated"]
        )

    def test_restore_ready_requires_full_package_lifecycle_and_provenance(self) -> None:
        policy = json.loads((CONTRACTS / "everkeep.acceptance.json").read_text(encoding="utf-8"))
        restore = "\n".join(policy["required_ready_evidence"]["restore_capability"]).lower()
        provenance = "\n".join(policy["required_ready_evidence"]["provenance"]).lower()
        for required in ("installs", "removal", "reinstalls", "downgrade", "restored", "sha-256"):
            self.assertIn(required, restore)
        for required in (
            "source revision",
            "source tree",
            "sha-256",
            "ci workflow",
            "goreecloud/goreecloud-zorin-os",
            "untracked package inputs",
        ):
            self.assertIn(required, provenance)
        self.assertIn("separate everkeep-owned governance record", restore)

    def test_sensitive_recovery_material_is_forbidden(self) -> None:
        policy = json.loads((CONTRACTS / "everkeep.acceptance.json").read_text(encoding="utf-8"))
        forbidden = {item.lower() for item in policy["sensitive_evidence"]["forbidden"]}
        self.assertIn("passwords", forbidden)
        self.assertIn("tokens", forbidden)
        self.assertIn("authentication tokens", forbidden)
        self.assertIn("private keys", forbidden)
        self.assertIn("recovery codes", forbidden)
        self.assertIn("secret values", forbidden)
        self.assertIn("reusable credentials", forbidden)

    def test_package_lifecycle_probe_runs_as_representative_user(self) -> None:
        source = (ROOT / "scripts" / "validate-package-lifecycle.sh").read_text(encoding="utf-8")
        self.assertIn('"$(id -u)" -ne 0', source)
        self.assertIn("representative desktop user, not as root", source)
        self.assertIn('sudo apt install -y --reinstall --allow-downgrades', source)
        self.assertIn('sudo apt remove -y goreecloud-care', source)
        self.assertNotIn('sudo goreecloud-care', source)
        self.assertNotIn('sudo sh "$ROOT/scripts/validate-installed.sh"', source)

    def test_package_lifecycle_probe_reinstalls_same_version_candidate_bytes(self) -> None:
        source = (ROOT / "scripts" / "validate-package-lifecycle.sh").read_text(encoding="utf-8")
        self.assertIn("Exact-candidate acceptance is package-byte scoped", source)
        self.assertIn("--reinstall", source)
        self.assertIn("same Debian version", source)
        self.assertNotIn('sudo apt install -y --allow-downgrades "$package_path"', source)

    def test_package_lifecycle_probe_requires_true_older_rollback_package(self) -> None:
        source = (ROOT / "scripts" / "validate-package-lifecycle.sh").read_text(encoding="utf-8")
        self.assertIn('dpkg --compare-versions "$previous_version" lt "$candidate_version"', source)
        self.assertIn("Previous package must sort older than the candidate", source)
        self.assertIn("expects golden artifact candidate 0.1.0", source)

    def test_package_lifecycle_probe_guards_runtime_isolation_bytecode_and_provenance_cleanup(self) -> None:
        source = (ROOT / "scripts" / "validate-package-lifecycle.sh").read_text(encoding="utf-8")
        self.assertIn("0.1.0 candidate checks deliberately exercise source/working-directory shadow resistance", source)
        self.assertIn("working-directory/PYTHONPATH shadowing", source)
        self.assertIn("Private Python bytecode remained after package removal", source)
        self.assertIn("PREVIOUS_PROBE_DIR=$(mktemp -d)", source)
        self.assertIn("dev17 predates that isolation contract", source)
        self.assertIn("/usr/share/goreecloud-care/build-provenance.json", source)
        self.assertIn("/usr/share/goreecloud-care", source)


if __name__ == "__main__":
    unittest.main()
