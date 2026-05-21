#!/usr/bin/env bash
# Local verification for the Python package and browser app.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -x "$ROOT/.venv/bin/pytest" ]]; then
  PY="$ROOT/.venv/bin/pytest"
  PYTHON="$ROOT/.venv/bin/python"
elif command -v pytest >/dev/null 2>&1; then
  PY="pytest"
  PYTHON="python"
else
  echo "Install dependencies: python -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
  exit 1
fi

"$PYTHON" -m ruff check .
"$PY" tests/ -q

cd "$ROOT/frontend"
npm run build
npm run lint

echo "OK: pytest + frontend build + eslint"
