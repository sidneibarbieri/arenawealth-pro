# Public release / history scrub (MAINTAINER ONLY)

> Not shipped in the reviewer artifact (excluded by `scripts/package_artifact.sh`).
> Contains **no** real data values and **no** author identity — fill private values
> from your own records at run time. Do this only **post-acceptance**, on a **copy**,
> never on your only repository.

## Why this exists

The private repo's **git history** still contains the pre-sanitization fixture
(`tests/fixtures/seed_portfolio_broker.csv`) with real holdings across early commits.
4open serves a single pinned commit's tree, so the anonymous mirror is safe — but the
**repository** must never be pushed public as-is, because old commits stay reachable by
direct SHA.

## ✅ Option A — recommended: fresh history-less public repo (zero risk)

Guarantees that no published commit ever contained the real data.

```bash
# 1. Build the clean snapshot (already history-less, no real data, no manuscript)
bash scripts/package_artifact.sh             # -> dist/<snapshot>/
#    For camera-ready: restore the real author block in the manuscript ONLY
#    (the artifact excludes the manuscript, so the scrub is unaffected).

# 2. Create a brand-new public repo with ONE commit (no history)
cd dist/<snapshot>
git init -b main && git add -A && git commit -m "Public reproducibility artifact"
gh repo create <neutral-public-name> --public --source=. --push
```

## ⚠️ Option B — only if you must publish THIS repo (fragile, error-prone)

Rewrites all history to purge the real values from every blob.

```bash
pip install git-filter-repo
git clone --no-local <this-repo> scrub && cd scrub

# Build a replacements file: one line per real value -> a neutral value.
# Pull the real values from the pre-sanitization fixture in your private records.
#   format:   <REAL_VALUE>==><NEUTRAL_VALUE>
# Include EVERY real holding figure (the value appears in several files at old commits),
# not just one file.
$EDITOR /tmp/repl.txt
git filter-repo --replace-text /tmp/repl.txt

git push --force --all && git push --force --tags
```

Caveats (why Option A is better):
- GitHub keeps old commits reachable by SHA until garbage-collection — you may have to
  open a GitHub Support ticket to purge cached views.
- Forks and existing clones keep the old data.
- Easy to miss a blob.

## 🔎 Mandatory verification before publishing (either option)

Both must come back empty / `0`:

```bash
git log --all -S'<REAL_CASH_VALUE>' --oneline
git log --all -p -- tests/fixtures/seed_portfolio_broker.csv | grep -c '<REAL_HOLDING_QTY>'
```

Also re-run the artifact privacy gate on the snapshot you publish:

```bash
python scripts/check_artifact_privacy.py <snapshot-dir>
```
