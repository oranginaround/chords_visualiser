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

Python dependencies are listed in `requirements.txt`:

- `mido`
- `python-rtmidi`
- `pygame-ce` (vanilla `pygame` may work but `pygame-ce` is recommended for better compatibility with Python 3.14+)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 j6_chord_gui.py
```

## Usage

- Connect your Roland J-6 (USB MIDI).
- Launch the app.
- If no device is found, the GUI shows a waiting screen and retries every few seconds.
- Play notes/chords on the J-6 and watch the detected chord and keys update live.
- Press `Esc` or close the window to quit.

## File Overview

- `j6_chord_gui.py`: main application (MIDI input, chord detection, GUI rendering)
- `requirements.txt`: Python package dependencies

## Notes

- If multiple MIDI devices are connected, the app uses the first matching J-6 port; otherwise it falls back to the first available MIDI input.
- Chord naming is pattern-based and focuses on common qualities/extensions.
