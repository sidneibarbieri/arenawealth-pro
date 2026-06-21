#!/usr/bin/env bash
# Build an anonymized, self-contained reviewer artifact from tracked files.
#
# Exports the committed git snapshot (no history), anonymizes the author
# identity read from pyproject, and zips the result under dist/.
set -euo pipefail

cd "$(dirname "$0")/.."
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: commit or discard local changes before packaging the artifact." >&2
    exit 1
fi

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

# Remove this packager; reviewers receive the frozen artifact, not release tooling.
rm -f "${work}/scripts/package_artifact.sh"

# Bibliography curation notes are development input, not part of the runtime artifact.
rm -rf "${work}/paper/bibliography"

# The manuscript is the separately-submitted paper. It is referenced by the
# artifact through its anonymous URL but never published with it, so drop the LaTeX
# sources, the vendored template, and the paper README. Keep paper/figures (the
# experiment output figures) and paper/data (frozen inputs) so the experiments still
# reproduce.
rm -f "${work}/paper/main.tex" \
      "${work}/paper/references.bib" \
      "${work}/paper/acmart.cls" \
      "${work}/paper/ACM-Reference-Format.bst" \
      "${work}/paper/README.md"
echo "removed the manuscript from the artifact (experiments only)"

# Anonymize the author identity wherever it appears.
if [ -n "${author}" ] && [ "${author}" != "Anonymous" ] && [ "${author}" != "Anonymous Authors" ]; then
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

python3 "${work}/scripts/check_artifact_privacy.py" "${work}"

(cd dist && zip -qr "${name}.zip" "${name}")
echo "Wrote dist/${name}.zip ($(du -h "dist/${name}.zip" | cut -f1))"
echo "Snapshot tree at ${work} (drop it into an anonymous repository)."
