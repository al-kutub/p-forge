#!/usr/bin/env bash
# Set up the Quote API on a fresh checkout.
# Creates a virtualenv and installs pinned dependencies.
set -euo pipefail

cd "$(dirname "$0")"

# The app uses PEP 604 "X | None" type unions, which require Python >= 3.10.
# Pick a suitable interpreter: honor $PYTHON if set, otherwise prefer the
# newest available of python3.12 / 3.11 / 3.10, falling back to python3.
MIN_MAJOR=3
MIN_MINOR=10

py_ok() {
    # Usage: py_ok <interpreter> -> returns 0 if it is >= 3.10
    command -v "$1" >/dev/null 2>&1 || return 1
    "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= ('"$MIN_MAJOR"', '"$MIN_MINOR"') else 1)' 2>/dev/null
}

PYTHON="${PYTHON:-}"
if [ -n "$PYTHON" ]; then
    if ! py_ok "$PYTHON"; then
        ver="$("$PYTHON" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "unknown")"
        echo "ERROR: \$PYTHON ($PYTHON) is Python $ver, but >= ${MIN_MAJOR}.${MIN_MINOR} is required." >&2
        echo "       The Quote API uses 'X | None' type unions (PEP 604) that need Python ${MIN_MAJOR}.${MIN_MINOR}+." >&2
        exit 1
    fi
else
    for cand in python3.13 python3.12 python3.11 python3.10 python3; do
        if py_ok "$cand"; then
            PYTHON="$cand"
            break
        fi
    done
    if [ -z "$PYTHON" ]; then
        found="$(command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "none")"
        echo "ERROR: no Python >= ${MIN_MAJOR}.${MIN_MINOR} found (highest python3 on PATH: $found)." >&2
        echo "       Install Python ${MIN_MAJOR}.${MIN_MINOR} or newer, or set \$PYTHON to a suitable interpreter." >&2
        echo "       The Quote API uses 'X | None' type unions (PEP 604) that need Python ${MIN_MAJOR}.${MIN_MINOR}+." >&2
        exit 1
    fi
fi

echo "==> Using $("$PYTHON" -c 'import sys; print(sys.executable, "(%d.%d.%d)" % sys.version_info[:3])')"

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
