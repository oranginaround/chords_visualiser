#!/usr/bin/env python3
"""Backward-compatible launcher for the packaged app."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from j6_chords.app import main

if __name__ == "__main__":
    main()
