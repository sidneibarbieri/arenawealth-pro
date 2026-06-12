#!/usr/bin/env bash
# Build an anonymized, self-contained reviewer artifact from tracked files.
#
# Exports the git-tracked snapshot (no history, respects .gitignore), drops the
# submission-specific and build-tooling material, anonymizes the author identity read
# from pyproject (no hardcoded name), and zips the result under dist/.
set -euo pipefail

cd "$(dirname "$0")/.."
stamp=$(date +%Y%m%d)
name="arenawealth-artifact-${stamp}"
work="dist/${name}"

# Author name to strip, read from the manifest so nothing is hardcoded here.
author=$(python3 - <<'PY'
import re
from pathlib import Path

text = Path("pyproject.toml").read_text(encoding="utf-8")
match = re.search(r'authors\s*=\s*\[\s*\{\s*name\s*=\s*"([^"]+)"', text)
print(match.group(1) if match else "")
PY
)

rm -rf "${work}" "${work}.zip"
mkdir -p "${work}"

# Tracked files only: no .git, no ignored private data.
git archive --format=tar HEAD | tar -x -C "${work}"

# Remove material that is not part of the research artifact, including this
# packager (build tooling reviewers do not need).
rm -rf "${work}/submissions" "${work}/notes" "${work}/codex-skills"
rm -f "${work}/scripts/package_artifact.sh"

# Anonymize the author identity wherever it appears.
if [ -n "${author}" ]; then
    python3 - "${work}" "${author}" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
author = sys.argv[2]
for path in root.rglob("*"):
    if not path.is_file():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    if author in text:
        path.write_text(text.replace(author, "Anonymous"), encoding="utf-8")
PY
    tokens=$(printf '%s' "${author}" | tr ' ' '|')
    if grep -riE "${tokens}" "${work}" >/dev/null 2>&1; then
        echo "ERROR: author identity still present in the snapshot" >&2
        grep -riE "${tokens}" "${work}" >&2
        exit 1
    fi
fi

(cd dist && zip -qr "${name}.zip" "${name}")
echo "Wrote dist/${name}.zip ($(du -h "dist/${name}.zip" | cut -f1))"
echo "Snapshot tree at ${work} (drop it into an anonymous repository)."
