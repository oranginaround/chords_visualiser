#!/usr/bin/env python3
"""
Roland J-6 MIDI Chord Reader — Pygame GUI
==========================================
Reads MIDI from a Roland J-6 over USB, detects chords,
and shows them on a GUI with a piano keyboard schematic.
"""

import pygame
import pygame.freetype  # works where pygame.font doesn't (Python 3.14+)
import sys
import time
import mido
from collections import OrderedDict

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COLORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BG = (30, 30, 30)
TEXT_WHITE = (240, 240, 240)
TEXT_DIM = (120, 120, 120)
KEY_OUTLINE = (100, 100, 100)
KEY_WHITE_UP = (45, 45, 45)
KEY_BLACK_UP = (25, 25, 25)
KEY_WHITE_DN = (255, 255, 255)
KEY_BLACK_DN = (200, 200, 220)
ACCENT = (90, 180, 255)
DIVIDER = (60, 60, 60)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MUSIC THEORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

CHORD_PATTERNS = OrderedDict(
    [
        ((0, 4, 7, 10, 14, 17, 21), "13"),
        ((0, 4, 7, 10, 14, 17), "11"),
        ((0, 4, 7, 11, 14), "maj9"),
        ((0, 3, 7, 10, 14), "min9"),
        ((0, 4, 7, 10, 14), "9"),
        ((0, 4, 7, 11), "maj7"),
        ((0, 3, 7, 10), "min7"),
        ((0, 4, 7, 10), "7"),
        ((0, 3, 6, 10), "min7♭5"),
        ((0, 3, 6, 9), "dim7"),
        ((0, 4, 8, 10), "aug7"),
        ((0, 3, 7, 11), "minMaj7"),
        ((0, 4, 7, 9), "6"),
        ((0, 3, 7, 9), "min6"),
        ((0, 4, 7, 14), "add9"),
        ((0, 3, 7, 14), "min(add9)"),
        ((0, 4, 7), "maj"),
        ((0, 3, 7), "min"),
        ((0, 3, 6), "dim"),
        ((0, 4, 8), "aug"),
        ((0, 5, 7), "sus4"),
        ((0, 2, 7), "sus2"),
        ((0, 7), "5"),
    ]
)


def detect_chord(pitch_classes):
    if not pitch_classes:
        return ""
    pcs = sorted(pitch_classes)
    if len(pcs) == 1:
        return NOTE_NAMES[pcs[0]]

    best_match = None
    best_len = 0

    for root in pcs:
        intervals = tuple(sorted((pc - root) % 12 for pc in pcs))
        for pattern, quality in CHORD_PATTERNS.items():
            if intervals == pattern and len(pattern) > best_len:
                best_match = f"{NOTE_NAMES[root]} {quality}"
                best_len = len(pattern)

    if best_match:
        return best_match

    for bass in pcs:
        remaining = set(pcs) - {bass}
        if len(remaining) >= 3:
            sub = detect_chord(remaining)
            if sub and "," not in sub:
                return f"{sub}/{NOTE_NAMES[bass]}"

    return ", ".join(NOTE_NAMES[pc] for pc in pcs)


def midi_note_to_name(n):
    return f"{NOTE_NAMES[n % 12]}{n // 12 - 1}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  KEYBOARD LAYOUT  (C3 → C5)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LOWEST = 48
HIGHEST = 72


def is_black(midi_note):
    return (midi_note % 12) in {1, 3, 6, 8, 10}


WHITE_NOTES = [n for n in range(LOWEST, HIGHEST + 1) if not is_black(n)]
BLACK_NOTES = [n for n in range(LOWEST, HIGHEST + 1) if is_black(n)]
NUM_WHITE = len(WHITE_NOTES)


def black_key_x_offset(midi_note):
    pc = midi_note % 12
    black_after = {1: 0, 3: 1, 6: 3, 8: 4, 10: 5}
    octave_offset = midi_note // 12 - LOWEST // 12
    return black_after[pc] + octave_offset * 7


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MIDI PORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def find_j6_port():
    ports = mido.get_input_names()
    if not ports:
        return None
    for p in ports:
        if "j-6" in p.lower() or "j6" in p.lower():
            return p
    return ports[0]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPER: centred text blit via freetype
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def draw_text_centred(screen, font, text, colour, cx, cy):
    """Render *text* centred at (cx, cy)."""
    rect = font.get_rect(text)
    rect.center = (cx, cy)
    font.render_to(screen, rect.topleft, text, colour)


def draw_text(screen, font, text, colour, x, cy):
    """Render *text* left-aligned at x, vertically centred at cy."""
    rect = font.get_rect(text)
    rect.midleft = (x, cy)
    font.render_to(screen, rect.topleft, text, colour)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN APP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    pygame.init()
    W, H = 720, 440
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("J-6 Chord Reader")
    clock = pygame.time.Clock()

    def load_font(size):
        return pygame.freetype.Font(None, size)


    font_big = load_font(48)
    font_med = load_font(22)
    font_small = load_font(15)
    font_tiny = load_font(12)

    font_big.strong = True

    # ── State ──────────────────────────────────
    held_notes = {}
    chord_text = ""
    notes_text = ""
    midi_port = None
    port_name = ""
    connected = False
    last_change = 0.0
    CHORD_WINDOW = 0.04

    pname = find_j6_port()
    if pname:
        try:
            midi_port = mido.open_input(pname)
            port_name = pname
            connected = True
        except Exception:
            pass

    retry_interval = 3.0
    last_retry = time.time()

    # ── Keyboard geometry ──────────────────────
    KB_MARGIN_X = 40
    KB_TOP = 250
    KB_W = W - 2 * KB_MARGIN_X
    WHITE_W = KB_W / NUM_WHITE
    WHITE_H = 150
    BLACK_W = WHITE_W * 0.58
    BLACK_H = WHITE_H * 0.60

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

        # ── MIDI reconnect ─────────────────────
        if not connected and time.time() - last_retry > retry_interval:
            last_retry = time.time()
            pname = find_j6_port()
            if pname:
                try:
                    midi_port = mido.open_input(pname)
                    port_name = pname
                    connected = True
                except Exception:
                    pass

        # ── Read MIDI ──────────────────────────
        if connected and midi_port:
            try:
                for msg in midi_port.iter_pending():
                    if msg.type == "note_on" and msg.velocity > 0:
                        held_notes[msg.note] = msg.velocity
                        last_change = time.time()
                    elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                        held_notes.pop(msg.note, None)
                        last_change = time.time()
            except Exception:
                connected = False
                held_notes.clear()
                if midi_port:
                    try:
                        midi_port.close()
                    except:
                        pass
                    midi_port = None

        # ── Chord detection ────────────────────
        if held_notes and time.time() - last_change >= CHORD_WINDOW:
            pcs = set(n % 12 for n in held_notes)
            chord_text = detect_chord(pcs)
            names = [midi_note_to_name(n) for n in sorted(held_notes)]
            notes_text = "  ".join(names)
        elif not held_notes:
            chord_text = ""
            notes_text = ""

        # ── Draw ───────────────────────────────
        screen.fill(BG)
        pygame.draw.line(screen, DIVIDER, (30, 20), (W - 30, 20), 1)

        if not connected:
            draw_text_centred(screen, font_med, "Waiting for", TEXT_DIM, W // 2, H // 2 - 24)
            draw_text_centred(screen, font_med, "MIDI connect", TEXT_DIM, W // 2, H // 2 + 10)
            dots = "." * (int(time.time() * 2) % 4)
            draw_text_centred(screen, font_med, dots, TEXT_DIM, W // 2, H // 2 + 46)
        else:
            # Port name
            draw_text_centred(screen, font_tiny, port_name, TEXT_DIM, W // 2, 34)

            # Chord name
            if chord_text:
                draw_text_centred(screen, font_big, chord_text, ACCENT, W // 2, 95)
            else:
                draw_text_centred(screen, font_med, "play something …", TEXT_DIM, W // 2, 95)

            # Note names
            if notes_text:
                draw_text_centred(screen, font_small, notes_text, TEXT_WHITE, W // 2, 145)

            # Divider
            pygame.draw.line(screen, DIVIDER, (30, 170), (W - 30, 170), 1)
            draw_text_centred(screen, font_tiny, "C3 – C5", TEXT_DIM, W // 2, 185)

            pressed_set = set(held_notes.keys())

            # ── WHITE KEYS ─────────────────────
            for i, note in enumerate(WHITE_NOTES):
                x = KB_MARGIN_X + i * WHITE_W
                rect = pygame.Rect(x, KB_TOP, WHITE_W - 1, WHITE_H)
                pressed = note in pressed_set

                if pressed:
                    pygame.draw.rect(screen, KEY_WHITE_DN, rect)
                    pygame.draw.rect(screen, ACCENT, rect, 2)
                else:
                    pygame.draw.rect(screen, KEY_WHITE_UP, rect)
                    pygame.draw.rect(screen, KEY_OUTLINE, rect, 1)

                lbl = NOTE_NAMES[note % 12]
                col = BG if pressed else TEXT_DIM
                draw_text_centred(screen, font_tiny, lbl, col, int(x + WHITE_W / 2), int(KB_TOP + WHITE_H - 14))

            # ── BLACK KEYS ─────────────────────
            for note in BLACK_NOTES:
                wi = black_key_x_offset(note)
                cx = KB_MARGIN_X + (wi + 1) * WHITE_W
                bx = cx - BLACK_W / 2
                rect = pygame.Rect(bx, KB_TOP, BLACK_W, BLACK_H)
                pressed = note in pressed_set

                if pressed:
                    pygame.draw.rect(screen, KEY_BLACK_DN, rect)
                    pygame.draw.rect(screen, ACCENT, rect, 2)
                else:
                    pygame.draw.rect(screen, KEY_BLACK_UP, rect)
                    pygame.draw.rect(screen, KEY_OUTLINE, rect, 1)

            # Divider bottom
            pygame.draw.line(screen, DIVIDER, (30, KB_TOP + WHITE_H + 20), (W - 30, KB_TOP + WHITE_H + 20), 1)

        pygame.display.flip()
        clock.tick(60)

    if midi_port:
        midi_port.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
