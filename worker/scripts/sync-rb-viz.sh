#!/usr/bin/env bash
# Copy the built rb-viz files (shared map components and stylesheet) into
# public/vendor/, where the map page loads them from.
#
#   scripts/sync-rb-viz.sh                 # from ../../rb-viz at origin/master
#   scripts/sync-rb-viz.sh PATH [REV]      # another checkout, or another commit
#
# With no checkout at PATH, rb-viz is cloned from GitHub into a temporary
# directory. The commit copied from is written to public/vendor/RB_VIZ_VERSION.
set -euo pipefail

here="$(cd "$(dirname "$0")/.." && pwd)"
src="${1:-$here/../../rb-viz}"
rev="${2:-origin/master}"
dest="$here/public/vendor"

if [ ! -d "$src/.git" ]; then
  src="$(mktemp -d)"
  trap 'rm -rf "$src"' EXIT
  git clone --quiet https://github.com/rockybranches/rb-viz "$src"
fi

commit="$(git -C "$src" rev-parse "$rev")"
mkdir -p "$dest"
for file in rb-viz.js rb-viz.css; do
  git -C "$src" show "$commit:dist/$file" > "$dest/$file"
done
printf 'rb-viz %s\nhttps://github.com/rockybranches/rb-viz/tree/%s/dist\n' "$commit" "$commit" \
  > "$dest/RB_VIZ_VERSION"
echo "public/vendor/ is rb-viz $commit"
