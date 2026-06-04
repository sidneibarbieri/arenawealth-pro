#!/usr/bin/env bash
# Build an anonymized, self-contained reviewer artifact from tracked files.
#
# Exports the git-tracked snapshot (no history, respects .gitignore), drops the
# venue-specific and tooling directories, anonymizes the author identity, and
# zips the result under dist/.
set -euo pipefail

cd "$(dirname "$0")/.."
stamp=$(date +%Y%m%d)
name="arenawealth-artifact-${stamp}"
work="dist/${name}"

rm -rf "${work}" "${work}.zip"
mkdir -p "${work}"

# Tracked files only: no .git, no ignored private data.
git archive --format=tar HEAD | tar -x -C "${work}"

# Remove material that is not part of the research artifact.
rm -rf "${work}/submissions" "${work}/notes" "${work}/codex-skills"

# Strip the author name from the package manifest (paper is already anonymous).
python3 - "${work}/pyproject.toml" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.write_text(path.read_text(encoding="utf-8").replace("Sidnei Barbieri", "Anonymous"))
PY

# Fail loudly if any author identity remains.
if grep -riE "sidnei|barbieri" "${work}" >/dev/null 2>&1; then
    echo "ERROR: author identity still present in the snapshot" >&2
    grep -riE "sidnei|barbieri" "${work}" >&2
    exit 1
fi

(cd dist && zip -qr "${name}.zip" "${name}")
echo "Wrote dist/${name}.zip ($(du -h "dist/${name}.zip" | cut -f1))"
echo "Snapshot tree at ${work} (drop it into an anonymous repository)."
