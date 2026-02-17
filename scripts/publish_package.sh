#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${PYPI_API_TOKEN:-}" ]]; then
  echo "PYPI_API_TOKEN is not set"
  exit 1
fi

uv run --group dev twine upload \
  --non-interactive \
  --username __token__ \
  --password "${PYPI_API_TOKEN}" \
  dist/*
