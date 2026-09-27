#!/bin/sh
set -eu
EXPECTED_PACKAGE_VERSION=${1:-0.1.0}
EXPECTED_RUNTIME_VERSION=${2:-0.1.0}

for command_name in goreecloud-care dpkg-query mktemp mkdir rm python3; do
  command -v "$command_name" >/dev/null
 done

installed=$(dpkg-query -W -f='${Status} ${Version}' goreecloud-care)
[ "$installed" = "install ok installed $EXPECTED_PACKAGE_VERSION" ]
[ "$(goreecloud-care --version)" = "$EXPECTED_RUNTIME_VERSION" ]
[ "$(goreecloud-care --api-version)" = "1" ]

test -f /usr/share/goreecloud-care/build-provenance.json

report_json=$(goreecloud-care --report-json)
health_json=$(goreecloud-care --health-json)
privacy_json=$(goreecloud-care --privacy-status-json)
security_json=$(goreecloud-care --security-status-json)
continuity_json=$(goreecloud-care --continuity-status-json)

REPORT_JSON=$report_json \
HEALTH_JSON=$health_json \
PRIVACY_JSON=$privacy_json \
SECURITY_JSON=$security_json \
CONTINUITY_JSON=$continuity_json \
EXPECTED_PACKAGE_VERSION=$EXPECTED_PACKAGE_VERSION \
EXPECTED_RUNTIME_VERSION=$EXPECTED_RUNTIME_VERSION \
python3 - <<'PY'
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

report = json.loads(os.environ['REPORT_JSON'])
health = json.loads(os.environ['HEALTH_JSON'])
privacy = json.loads(os.environ['PRIVACY_JSON'])
security = json.loads(os.environ['SECURITY_JSON'])
continuity = json.loads(os.environ['CONTINUITY_JSON'])
provenance = json.loads(Path('/usr/share/goreecloud-care/build-provenance.json').read_text(encoding='utf-8'))

assert report['product'] == 'GoreeCloud Care'
assert report['privacy']['contains_file_paths'] is False
assert report['privacy']['contains_raw_scan_errors'] is False
assert report['privacy']['network_used'] is False

assert health['product'] == 'GoreeCloud Care'
assert health['version'] == os.environ['EXPECTED_RUNTIME_VERSION']
assert health['state'] == 'ready'
assert health['local_only'] is True
assert health['network_used'] is False
assert health['telemetry_used'] is False
assert health['privileged_action_performed'] is False

# Care's local privacy endpoint remains fail-closed until exact Stable-adapter
# governance is supplied; the source does not self-promote external approval.
assert privacy['producer']['adapter_id'] == 'goreecloud-care'
assert privacy['privacy']['raw_private_activity_included'] is False
assert privacy['privacy']['contains_credentials'] is False
assert privacy['privacy']['contains_identifiers'] is False
assert privacy['acceptance']['runtime_acceptance_required'] is True
assert privacy['acceptance']['production_approved'] is False
assert privacy['state'] == 'development'

assert provenance['schema_version'] == 1
assert provenance['application'] == 'GoreeCloud Care'
assert provenance['producer'] == 'GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care'
assert provenance['runtime_version'] == os.environ['EXPECTED_RUNTIME_VERSION']
assert provenance['package_version'] == os.environ['EXPECTED_PACKAGE_VERSION']
assert re.fullmatch(r'[0-9a-f]{40}', provenance['source_revision'])
assert re.fullmatch(r'[0-9a-f]{40}', provenance['source_tree'])
assert isinstance(provenance['source_date_epoch'], int)
assert provenance['source_date_epoch'] >= 0
assert provenance['package_sha256_embedded'] is False

assert security['contract_version'] == '0.1.0'
assert security['scope'] == {
    'kind': 'application',
    'id': 'goreecloud-care',
    'display_name': 'GoreeCloud Care',
}
assert security['authority']['system'] == 'GoreeCloud Care'
assert security['authority']['control'] == 'local-maintenance-privilege-boundary'
assert security['authority']['authoritative'] is True
assert security['claim']['protected_by_wardveil'] is False
assert security['source_state'] in {'passing', 'non-passing'}
assert security['state'] in {'protected', 'attention'}
if security['state'] != 'protected':
    raise SystemExit('installed privileged-boundary security evidence is non-passing')
assert security['source_state'] == 'passing'
assert security['evidence']['status'] == 'current'
assert security['evidence']['reference'] == 'local-cli://goreecloud-care/security-status'
assert security['evidence']['summary']
observed = datetime.fromisoformat(security['evidence']['observed_at'].replace('Z', '+00:00'))
valid_until = datetime.fromisoformat(security['evidence']['valid_until'].replace('Z', '+00:00'))
assert observed.tzinfo is not None
assert valid_until.tzinfo is not None
assert valid_until > observed
assert (valid_until - observed).total_seconds() == 15 * 60
assert valid_until > datetime.now(timezone.utc)
assert security['privacy']['details_withheld'] is True
assert security['privacy']['redactions']

security_text = json.dumps(security, sort_keys=True).lower()
for forbidden in (
    'password', 'authentication token', 'private key', 'recovery code',
    'raw privileged command output:', '/home/', 'username', 'user_email',
):
    assert forbidden not in security_text, forbidden

assert continuity['producer'] == 'GoreeCloud Care'
assert continuity['dimension'] == 'restore_capability'
assert continuity['state'] in {'attention', 'ready'}
allowed_stages = {
    'target-acceptance-required',
    'target-accepted-governance-pending',
    'everkeep-promoted',
}
if continuity['stage'] not in allowed_stages:
    raise SystemExit(
        'installed continuity evidence failed its trust boundary: '
        f"state={continuity.get('state')} stage={continuity.get('stage')}"
    )
if continuity['state'] == 'ready':
    assert continuity['stage'] == 'everkeep-promoted'
    assert continuity['freshness'] == 'exact-build-bound'
    assert continuity['limitations'] == []
else:
    assert continuity['stage'] != 'everkeep-promoted'
    assert continuity['limitations']
PY

test -f /usr/lib/goreecloud-care/goreecloud-care-helper
test -f /usr/share/polkit-1/actions/com.goreecloud.care.policy
test -f /usr/share/applications/com.goreecloud.care.desktop
test -f /usr/share/icons/hicolor/scalable/apps/com.goreecloud.care.svg
test -f /usr/share/metainfo/com.goreecloud.care.metainfo.xml
test -f /usr/share/doc/goreecloud-care/API.md
test -f /usr/share/doc/goreecloud-care/WARDVEIL-INTEGRATION.md
grep -F 'Icon=com.goreecloud.care' /usr/share/applications/com.goreecloud.care.desktop >/dev/null
grep -F 'Name=GoreeCloud Care' /usr/share/applications/com.goreecloud.care.desktop >/dev/null
! grep -F 'Release Candidate' /usr/share/applications/com.goreecloud.care.desktop >/dev/null

grep -F '<name>GoreeCloud Care</name>' /usr/share/metainfo/com.goreecloud.care.metainfo.xml >/dev/null
grep -F '<release version="0.1.0"' /usr/share/metainfo/com.goreecloud.care.metainfo.xml >/dev/null

SHADOW_ROOT=$(mktemp -d)
cleanup() {
  rm -rf "$SHADOW_ROOT"
}
trap cleanup EXIT INT TERM
mkdir -p "$SHADOW_ROOT/goreecloud_care"
cat > "$SHADOW_ROOT/goreecloud_care/__init__.py" <<'PY'
__version__ = 'SHADOWED'
PY
cat > "$SHADOW_ROOT/goreecloud_care/__main__.py" <<'PY'
print('SHADOWED-APP')
PY
cat > "$SHADOW_ROOT/goreecloud_care/helper.py" <<'PY'
print('SHADOWED-HELPER')
PY

shadow_runtime=$(cd "$SHADOW_ROOT" && goreecloud-care --version)
[ "$shadow_runtime" = "$EXPECTED_RUNTIME_VERSION" ] || {
  echo "Installed application launcher was shadowed by the working directory: $shadow_runtime" >&2
  exit 1
}

HELPER=/usr/lib/goreecloud-care/goreecloud-care-helper
if helper_output=$(cd "$SHADOW_ROOT" && "$HELPER" invalid-action 2>&1); then
  helper_status=0
else
  helper_status=$?
fi
[ "$helper_status" -eq 64 ] || {
  echo "Installed helper launcher did not execute the real fixed helper (status=$helper_status): $helper_output" >&2
  exit 1
}
case "$helper_output" in
  *SHADOWED-HELPER*)
    echo "Installed privileged helper launcher was shadowed by the working directory" >&2
    exit 1
    ;;
esac

test ! -e /usr/lib/goreecloud-care/goreecloud_care/__pycache__ || {
  echo "Private Care bytecode cache exists after installed-runtime validation" >&2
  exit 1
}

printf '%s\n' "Installed GoreeCloud Care $EXPECTED_PACKAGE_VERSION safe qualification probe: passed"
printf '%s\n' "Installed application/helper launchers are isolated from working-directory Python shadowing."
printf '%s\n' "Installed package-owned exact-source provenance is present and structurally valid."
printf '%s\n' "Installed Wardveil-compatible privilege-boundary evidence is passing, current, minimized, scoped, and does not self-claim Wardveil governance."
printf '%s\n' "Canonical GoreeCloud Care desktop/AppStream identity and icon derivative are installed."
printf '%s\n' "Continuity remains evidence-derived and cannot become ready without exact governed Everkeep promotion."
