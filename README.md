# J-6 Chords

A lightweight desktop GUI that reads live MIDI notes from a Roland J-6 (or any available MIDI input), detects chord names, and displays both the chord and pressed keys on a piano-style keyboard.

## Features

- Auto-detects a MIDI input port (prefers names containing `J-6`/`J6`)
- Real-time chord detection from held pitch classes
- Displays:
  - detected chord name (for example: `C maj7`, `D min9`, `G 13`)
  - currently held note names (for example: `C4  E4  G4`)
  - an on-screen keyboard (range `C3` to `C5`) with pressed-key highlighting
- Auto-reconnects when the MIDI device is disconnected/reconnected

## Requirements

- Python 3.10+
- A MIDI input device (Roland J-6 recommended)
- OS MIDI support (CoreMIDI/ALSA/etc.)
- `uv` package manager

## Setup (uv)

```bash
# install dependencies from pyproject.toml
uv sync
```

## Run

```bash
uv run j6-chords-gui
```

Backward-compatible launcher still works:

```bash
uv run python j6_chord_gui.py
```

## Build package

```bash
./scripts/build_package.sh
```

Build artifacts are written to `dist/`.

## Publish

Automatic publish is handled by GitHub Actions on each published GitHub Release:

- Workflow: `.github/workflows/publish-pypi.yml`
- Details and credential checklist: `PUBLISHING_TODO.md`

Manual publish fallback (token-based):

```bash
PYPI_API_TOKEN=... ./scripts/publish_package.sh
```

## File Overview

- `pyproject.toml`: project metadata, dependencies, and build configuration
- `src/j6_chords/app.py`: main application (MIDI input, chord detection, GUI rendering)
- `j6_chord_gui.py`: backward-compatible launcher
- `scripts/build_package.sh`: local build and package validation
- `.github/workflows/publish-pypi.yml`: CI build/publish workflow
- `PUBLISHING_TODO.md`: required credentials and where to configure them

## Notes

- If multiple MIDI devices are connected, the app uses the first matching J-6 port; otherwise it falls back to the first available MIDI input.
- Chord naming is pattern-based and focuses on common qualities/extensions.
