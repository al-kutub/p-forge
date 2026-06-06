#!/usr/bin/env bash
# Set up the Quote API on a fresh checkout.
# Creates a virtualenv and installs pinned dependencies.
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
VENV_PY=".venv/bin/python"

echo "==> Creating virtual environment (.venv)"
# Some minimal Python builds ship without ensurepip; fall back to a pip-less
# venv and install into it using the system pip's --python flag.
if "$PYTHON" -m venv .venv 2>/dev/null && [ -x ".venv/bin/pip" ]; then
    echo "==> Installing dependencies (venv pip)"
    "$VENV_PY" -m pip install --quiet --upgrade pip
    "$VENV_PY" -m pip install --quiet -r requirements.txt
else
    echo "==> ensurepip unavailable; using system pip --> .venv"
    rm -rf .venv
    "$PYTHON" -m venv --without-pip .venv
    "$PYTHON" -m pip --python "$VENV_PY" install --quiet -r requirements.txt
fi

echo ""
echo "Setup complete. To run:"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --reload    # serve on http://127.0.0.1:8000"
echo "  pytest                            # run the test suite"
