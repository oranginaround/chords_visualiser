#!/usr/bin/env bash
set -euo pipefail

# Build sdist and wheel into dist/
uv build

# Validate metadata before upload
uv run --group dev twine check dist/*
