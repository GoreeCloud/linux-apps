#!/bin/sh
set -eu

usage() {
  echo "Usage: $0 <candidate.deb> <previous.deb>" >&2
  exit 2
}

[ "$#" -eq 2 ] || usage
[ "$(id -u)" -ne 0 ] || {
  echo "Run this acceptance probe as the representative desktop user, not as root. The script requests sudo only for apt package operations." >&2
  exit 2
}

for command_name in sudo apt dpkg dpkg-deb dpkg-query grep sed mktemp rm; do
  command -v "$command_name" >/dev/null || {
    echo "Required command not found: $command_name" >&2
    exit 2
  }
done

CANDIDATE=$1
PREVIOUS=$2
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

[ -f "$CANDIDATE" ] || { echo "Candidate package not found: $CANDIDATE" >&2; exit 2; }
[ -f "$PREVIOUS" ] || { echo "Previous package not found: $PREVIOUS" >&2; exit 2; }

candidate_name=$(dpkg-deb -f "$CANDIDATE" Package)
previous_name=$(dpkg-deb -f "$PREVIOUS" Package)
[ "$candidate_name" = "goreecloud-care" ]
[ "$previous_name" = "goreecloud-care" ]

candidate_version=$(dpkg-deb -f "$CANDIDATE" Version)
previous_version=$(dpkg-deb -f "$PREVIOUS" Version)
[ "$candidate_version" != "$previous_version" ]
dpkg --compare-versions "$previous_version" lt "$candidate_version" || {
  echo "Previous package must sort older than the candidate: previous=$previous_version candidate=$candidate_version" >&2
  exit 2
}

candidate_runtime=$(printf '%s' "$candidate_version" | sed 's/~/-/')
previous_runtime=$(printf '%s' "$previous_version" | sed 's/~/-/')

case "$candidate_version" in
  0.1.0) ;;
  *) echo "This lifecycle qualification probe expects golden artifact candidate 0.1.0; got $candidate_version" >&2; exit 2 ;;
esac

# The accepted historical dev17 package predates dev19's isolated launcher.
# Validate that historical rollback from a clean neutral directory, while the
# 0.1.0 candidate retains the dev19+ source/working-directory isolation gate.
PREVIOUS_PROBE_DIR=$(mktemp -d)
cleanup() {
  rm -rf "$PREVIOUS_PROBE_DIR"
}
trap cleanup EXIT INT TERM

printf '%s\n' "Package lifecycle qualification will temporarily remove and downgrade GoreeCloud Care."
printf '%s\n' "0.1.0 golden artifact candidate: $candidate_version"
printf '%s\n' "Rollback package: $previous_version"
printf '%s\n' "Representative user: $(id -un) (uid $(id -u))"
printf '%s\n' "0.1.0 candidate checks deliberately exercise source/working-directory shadow resistance inherited from dev19 hardening."
printf '%s\n' "The immutable historical rollback package is validated from a clean neutral directory because dev17 predates that isolation contract."
printf '%s\n' "No Care-owned user data is expected to be removed; this script does not invoke Care cleanup actions."
printf '%s\n' "Administrator authentication may be requested by apt."

install_package() {
  package_path=$1
  # Exact-candidate acceptance is package-byte scoped. --reinstall prevents APT
  # from treating different local bytes with the same Debian version as already
  # satisfied and leaving stale package provenance installed.
  sudo apt install -y --reinstall --allow-downgrades "$package_path"
}

assert_version_from() {
  expected_package=$1
  expected_runtime=$2
  runtime_dir=$3
  installed=$(dpkg-query -W -f='${Status} ${Version}' goreecloud-care)
  [ "$installed" = "install ok installed $expected_package" ] || {
    echo "Installed package state mismatch: expected='install ok installed $expected_package' actual='$installed'" >&2
    exit 1
  }
  actual_runtime=$(cd "$runtime_dir" && goreecloud-care --version)
  [ "$actual_runtime" = "$expected_runtime" ] || {
    echo "Installed runtime mismatch: package=$expected_package expected_runtime=$expected_runtime actual_runtime=$actual_runtime" >&2
    echo "Runtime probe directory: $runtime_dir" >&2
    echo "For the 0.1.0 candidate this may indicate working-directory/PYTHONPATH shadowing or stale installed bytecode." >&2
    exit 1
  }
}

printf '%s\n' "[1/6] Install/upgrade 0.1.0 candidate"
install_package "$CANDIDATE"
sh "$ROOT/scripts/validate-installed.sh" "$candidate_version" "$candidate_runtime"

printf '%s\n' "[2/6] Remove 0.1.0 candidate"
sudo apt remove -y goreecloud-care
if dpkg-query -W -f='${Status}' goreecloud-care 2>/dev/null | grep -qx 'install ok installed'; then
  echo "Package still installed after removal" >&2
  exit 1
fi
for path in \
  /usr/bin/goreecloud-care \
  /usr/lib/goreecloud-care/goreecloud-care-helper \
  /usr/lib/goreecloud-care/goreecloud_care \
  /usr/lib/goreecloud-care \
  /usr/lib/python3/dist-packages/goreecloud_care.pth \
  /usr/share/polkit-1/actions/com.goreecloud.care.policy \
  /usr/share/applications/com.goreecloud.care.desktop \
  /usr/share/icons/hicolor/scalable/apps/com.goreecloud.care.svg \
  /usr/share/metainfo/com.goreecloud.care.metainfo.xml \
  /usr/share/goreecloud-care/build-provenance.json \
  /usr/share/goreecloud-care; do
  [ ! -e "$path" ] || { echo "Package-owned path remained after removal: $path" >&2; exit 1; }
done
[ ! -e /usr/lib/goreecloud-care/goreecloud_care/__pycache__ ] || {
  echo "Private Python bytecode remained after package removal" >&2
  exit 1
}

printf '%s\n' "[3/6] Reinstall 0.1.0 candidate as a fresh package state"
install_package "$CANDIDATE"
sh "$ROOT/scripts/validate-installed.sh" "$candidate_version" "$candidate_runtime"

printf '%s\n' "[4/6] Downgrade to immutable accepted Development rollback package"
install_package "$PREVIOUS"
assert_version_from "$previous_version" "$previous_runtime" "$PREVIOUS_PROBE_DIR"
(cd "$PREVIOUS_PROBE_DIR" && goreecloud-care --report-json >/dev/null)

printf '%s\n' "[5/6] Restore 0.1.0 candidate after downgrade"
install_package "$CANDIDATE"
sh "$ROOT/scripts/validate-installed.sh" "$candidate_version" "$candidate_runtime"

printf '%s\n' "[6/6] Final 0.1.0 candidate package state"
assert_version_from "$candidate_version" "$candidate_runtime" "$ROOT"
printf '%s\n' "Representative package install/remove/reinstall/downgrade/rollback acceptance: passed"
printf '%s\n' "The 0.1.0 golden artifact candidate is installed at the end of the probe; no Care cleanup action was invoked."
