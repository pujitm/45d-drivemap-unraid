#!/usr/bin/env bash
set -euo pipefail

# Refresh the vendored 45drives-disks frontend snapshot from an upstream
# 45Drives Cockpit module build, then re-apply the Unraid-specific index.html
# shim (routes Cockpit API calls to php/api.php).
#
# The 45drives-disks UI is built and maintained by 45Drives; we only vendor
# their prebuilt output. This script does NOT build from source -- it takes an
# already-built upstream module (e.g. the contents of
# /usr/share/cockpit/45drives-disks from an installed cockpit-45drives-hardware
# package, or a tarball of it) and copies it into the repo.

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DEST_DIR="${ROOT_DIR}/assets/45d/45drives-disks"
TEMPLATE="${ROOT_DIR}/dev/45drives-disks-index.template.html"
ASSETS_README="${ROOT_DIR}/assets/45d/README.md"

usage() {
  cat <<'EOF'
Update the vendored 45drives-disks frontend snapshot.

Usage:
  dev/update-45drives-disks.sh <source> [--version <ver>] [--dry-run]
  dev/update-45drives-disks.sh --source <source> [--version <ver>] [--dry-run]

<source> is an upstream 45drives-disks module build, either:
  - a directory containing index.html + assets/index.*.js
    (e.g. /usr/share/cockpit/45drives-disks on an installed host), or
  - a tarball (.txz, .tar.xz, .tgz, .tar.gz, .tar) of the same.

Options:
  --version <ver>   Record this release in assets/45d/README.md (e.g. 2.5.5-1).
  --dry-run         Show what would change without modifying the repo.
  -h, --help        Show this help.

After updating, the committed bundle hashes change and the output may differ
from the previous hand-maintained snapshot (Tailwind/formatting). Real-device
visual QA on Unraid Main is required before shipping.
EOF
}

SOURCE=""
VERSION=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --source) SOURCE="${2:-}"; shift 2 ;;
    --version) VERSION="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)
      if [[ -z "$SOURCE" ]]; then SOURCE="$1"; shift
      else echo "error: unexpected argument: $1" >&2; usage >&2; exit 2; fi ;;
  esac
done

[[ -n "$SOURCE" ]] || { echo "error: a source directory or tarball is required" >&2; usage >&2; exit 2; }
[[ -f "$TEMPLATE" ]] || { echo "error: index template missing: $TEMPLATE" >&2; exit 1; }
[[ -d "$DEST_DIR" ]] || { echo "error: destination missing: $DEST_DIR" >&2; exit 1; }
command -v rsync >/dev/null 2>&1 || { echo "error: rsync is required" >&2; exit 1; }

WORK_DIR=$(mktemp -d)
cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT

# Resolve $SOURCE into a directory holding the upstream module
# (index.html + assets/index.*.js).
resolve_module_dir() {
  local src="$1"
  local root
  if [[ -d "$src" ]]; then
    root="$src"
  elif [[ -f "$src" ]]; then
    root="${WORK_DIR}/extracted"
    mkdir -p "$root"
    case "$src" in
      *.txz|*.tar.xz) tar -xJf "$src" -C "$root" ;;
      *.tgz|*.tar.gz) tar -xzf "$src" -C "$root" ;;
      *.tar)          tar -xf  "$src" -C "$root" ;;
      *) echo "error: unsupported source file type: $src" >&2; return 1 ;;
    esac
  else
    echo "error: source not found: $src" >&2; return 1
  fi

  is_module() { [[ -f "$1/index.html" ]] && compgen -G "$1/assets/index.*.js" >/dev/null; }

  if is_module "$root"; then printf '%s\n' "$root"; return 0; fi

  local named
  named=$(find "$root" -type d -name 45drives-disks 2>/dev/null | head -n 1 || true)
  if [[ -n "$named" ]] && is_module "$named"; then printf '%s\n' "$named"; return 0; fi

  local d
  while IFS= read -r d; do
    if is_module "$d"; then printf '%s\n' "$d"; return 0; fi
  done < <(find "$root" -type f -name index.html -exec dirname {} \; 2>/dev/null)

  echo "error: could not locate a 45drives-disks module (need index.html + assets/index.*.js) under $src" >&2
  return 1
}

MODULE_DIR=$(resolve_module_dir "$SOURCE")
echo "Source module: ${MODULE_DIR}"

# Determine the entry bundles from the upstream index.html (most accurate),
# falling back to globbing the assets directory.
detect_bundle() {
  local ext="$1" name
  name=$(grep -oE "assets/index\.[A-Za-z0-9]+\.${ext}" "${MODULE_DIR}/index.html" 2>/dev/null \
           | head -n 1 | sed 's#assets/##' || true)
  if [[ -z "$name" ]]; then
    name=$(cd "${MODULE_DIR}/assets" && ls index.*."${ext}" 2>/dev/null | head -n 1 || true)
  fi
  printf '%s\n' "$name"
}

NEW_JS=$(detect_bundle js)
NEW_CSS=$(detect_bundle css)
[[ -n "$NEW_JS" ]] || { echo "error: could not find a JS bundle in the source" >&2; exit 1; }
[[ -n "$NEW_CSS" ]] || { echo "error: could not find a CSS bundle in the source" >&2; exit 1; }

OLD_JS=$( (cd "${DEST_DIR}/assets" && ls index.*.js  2>/dev/null | head -n 1) || true)
OLD_CSS=$( (cd "${DEST_DIR}/assets" && ls index.*.css 2>/dev/null | head -n 1) || true)

echo "  JS  bundle: ${OLD_JS:-<none>} -> ${NEW_JS}"
echo "  CSS bundle: ${OLD_CSS:-<none>} -> ${NEW_CSS}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo
  echo "Dry run -- would sync these changes into ${DEST_DIR#${ROOT_DIR}/}/ :"
  rsync -ain --delete "${MODULE_DIR}/" "${DEST_DIR}/" | sed 's/^/  /'
  echo
  echo "Would regenerate index.html from template (css=${NEW_CSS}, js=${NEW_JS})."
  [[ -n "$VERSION" ]] && echo "Would record version ${VERSION#v} in ${ASSETS_README#${ROOT_DIR}/}."
  exit 0
fi

# Sync upstream module into place, dropping stale hashed assets.
rsync -a --delete "${MODULE_DIR}/" "${DEST_DIR}/"

# Re-apply the Unraid index.html shim with the new bundle hashes. This
# overwrites the vanilla upstream index.html that rsync just copied in.
sed -e "s#__CSS_BUNDLE__#${NEW_CSS}#g" \
    -e "s#__JS_BUNDLE__#${NEW_JS}#g" \
    "$TEMPLATE" > "${DEST_DIR}/index.html"

# Optionally record the release version in the assets README provenance note.
if [[ -n "$VERSION" ]]; then
  ver="${VERSION#v}"
  if grep -qE 'release snapshot \(v[^)]*\)' "$ASSETS_README"; then
    tmp=$(mktemp)
    sed -E "s/release snapshot \(v[^)]*\)/release snapshot (v${ver})/" "$ASSETS_README" > "$tmp"
    mv "$tmp" "$ASSETS_README"
    echo "Recorded version v${ver} in ${ASSETS_README#${ROOT_DIR}/}"
  else
    echo "warning: could not find the version line in ${ASSETS_README#${ROOT_DIR}/} to update" >&2
  fi
fi

echo
echo "Done. Review the diff, then QA on a real Unraid host:"
echo "  git status --short assets/45d/45drives-disks"
echo "  dev/live-deploy.sh --host root@<unraid-ip> --include-assets"
