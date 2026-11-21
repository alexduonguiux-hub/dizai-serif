"""Original 10 s score for the AnNam Serif showreel — Indochine jazz lounge (120 BPM, 5 bars of 4/4).

Saigon-1930s feel: felt piano with maj9 / m9 voicings, upright bass, brushes and ride; the
three slider drags are played by a đàn bầu (monochord) voice whose pitch glides with each knob.
Every cut in the picture lands on a piano stab, a rim click or a cymbal. Pure numpy, no samples.
Usage: python3 music.py out.wav
"""
import sys
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 10.0
N = int(SR * DUR)
rng = np.random.default_rng(11)
mix = np.zeros((2, N))
B = 0.5            # one beat
SW = 0.04          # swing delay for off-beat 8ths


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[0, i:i + len(sig)] += sig * gain * l * 1.414
    mix[1, i:i + len(sig)] += sig * gain * r * 1.414


def tt(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f, o=2):
    return sosfilt(butter(o, f, 'lp', fs=SR, output='sos'), x)


def bp(x, a, b, o=2):
    return sosfilt(butter(o, [a, b], 'bp', fs=SR, output='sos'), x)


# ---------------- instruments ----------------
def piano(m, dur=2.0, vel=1.0):
    """Felt piano: slightly inharmonic partials, two-stage decay, soft hammer."""
    t = tt(dur); f = hz(m); out = np.zeros_like(t)
    Bc = 0.0004
    for k in range(1, 11):
        fk = f * k * np.sqrt(1 + Bc * k * k)
        if fk > SR / 2.2:
            break
        a = (1 / k ** 1.6) * (0.6 + 0.4 * vel) ** (k / 3)
        d1, d2 = 2.5 + 0.9 * k, 0.6 + 0.25 * k
        env = 0.65 * np.exp(-t * d1) + 0.35 * np.exp(-t * d2)
        out += a * np.sin(2 * np.pi * fk * t + k) * env
    out += 0.08 * lp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 120)   # hammer felt
    out *= np.minimum(1, t / 0.004)
    rel = np.ones_like(t); r = int(0.12 * SR); rel[-r:] = np.linspace(1, 0, r)
    return out * rel * 0.22 * vel


def chord(notes, t0, dur=2.0, vel=0.8, roll=0.012, pan=0.0):
    for i, m in enumerate(notes):
        add(piano(m, dur, vel), t0 + i * roll, 1.0, pan + (i - len(notes) / 2) * 0.08)


def bass(m, dur=0.5, vel=1.0):
    t = tt(dur); f = hz(m) * (1 + 0.01 * np.exp(-t * 40))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.006) * np.exp(-t * 3.0)
    thump = 0.3 * lp(rng.standard_normal(len(t)), 400) * np.exp(-t * 60)
    rel = np.ones_like(t); r = int(0.05 * SR); rel[-r:] = np.linspace(1, 0, r)
    return (s * env + thump) * rel * 0.42 * vel


def brush_tap(gain=0.12):
    t = tt(0.09)
    return bp(rng.standard_normal(len(t)), 2500, 9000) * np.exp(-t * 55) * gain


def brush_swish(dur=0.45, gain=0.10):
    t = tt(dur); x = t / dur
    return bp(rng.standard_normal(len(t)), 1800, 7000) * np.sin(np.pi * x) ** 1.5 * gain


def ride(gain=0.10, dur=1.2):
    t = tt(dur); out = np.zeros_like(t)
    for r, a in [(1, 1), (1.47, .7), (2.09, .6), (2.56, .5), (3.42, .4), (4.11, .3)]:
        out += a * np.sin(2 * np.pi * 410 * r * 2.3 * t + r)
    noise = bp(rng.standard_normal(len(t)), 6000, 14000)
    return (0.25 * out + 0.6 * noise) * np.exp(-t * 4.5) * np.minimum(1, t / 0.001) * gain


def cymbal_swell(dur, gain=0.18):
    t = tt(dur); x = t / dur
    n = bp(rng.standard_normal(len(t)), 3000, 13000)
    return n * x ** 2.5 * gain


def crash(gain=0.22, dur=2.0):
    t = tt(dur)
    return bp(rng.standard_normal(len(t)), 2500, 14000) * np.exp(-t * 2.2) * gain


def rim(gain=0.25):
    t = tt(0.06)
    s = np.sin(2 * np.pi * 1750 * t) * np.exp(-t * 90) + 0.6 * bp(rng.standard_normal(len(t)), 2000, 6000) * np.exp(-t * 120)
    return s * gain


def kick(gain=0.6):
    t = tt(0.35); f = 48 + 60 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * gain


def bell(m, gain=0.12, dur=0.9):
    """Celesta-like tick for the style list."""
    t = tt(dur); f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 4.01 * t) * np.exp(-t * 12)
    return s * np.exp(-t * 5) * np.minimum(1, t / 0.002) * gain


def danbau(m, dur, curve):
    """Đàn bầu: one string played on harmonics — flute-like tone, pitch bent by the rod.
    curve(t) gives the bend in semitones; vibrato grows on held notes."""
    t = tt(dur)
    vib = 0.18 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.25) / 0.25, 0, 1)
    f = hz(m) * 2 ** ((curve(t) + vib) / 12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    env = (1 - np.exp(-t * 60)) * np.exp(-t * 0.9)
    rel = np.ones_like(t); r = int(0.15 * SR); rel[-r:] = np.linspace(1, 0, r) ** 2
    pick = 0.15 * bp(rng.standard_normal(len(t)), 1500, 5000) * np.exp(-t * 200)
    return (s * env * rel + pick) * 0.26


def smooth(x):
    x = np.clip(x, 0, 1)
    return np.where(x < .5, 8 * x ** 4, 1 - (-2 * x + 2) ** 4 / 2)


# ---------------- harmony (key of D) ----------------
D2, E2, Fs2, G2, A2, B2 = 38, 40, 42, 43, 45, 47
Dmaj9 = [50, 54, 57, 61, 64]          # D F# A C# E
Bm9 = [47, 50, 54, 57, 61]            # B D F# A C#
Gmaj9 = [43, 47, 50, 54, 57]          # G B D F# A
Em9 = [52, 55, 59, 62, 66]            # E G B D F#
A13 = [45, 49, 55, 59, 66]            # A C# G B F#

# ---------------- 0–1  intro: piano arpeggio as AN NAM assembles ----------------
for i, m in enumerate([50, 54, 57, 61, 64, 66, 69, 73]):
    add(piano(m, 1.6, 0.55 + 0.04 * i), 0.04 + i * 0.105, 0.9, -0.4 + i * 0.11)
add(cymbal_swell(0.55, 0.12), 0.45)

# ---------------- groove 1–8: walking bass, brushes, ride ----------------
walk = {1.0: D2, 1.5: Fs2, 2.0: B2 - 12, 2.5: D2, 3.0: Fs2, 3.5: A2, 4.0: G2, 4.5: B2 - 12,
        5.0: D2, 5.5: E2, 6.0: G2, 6.5: E2, 7.0: G2, 7.5: A2}
for t0, m in walk.items():
    add(bass(m, 0.48, 1.0 if (t0 * 2) % 2 == 0 else 0.85), t0, 1.0, -0.1)
for k in range(14):                       # beats 1.0 … 7.5
    t0 = 1.0 + k * B
    add(ride(0.08), t0, pan=0.45)
    add(brush_tap(0.06), t0 + B / 2 + SW, pan=-0.3)
    if k % 2 == 1:
        add(brush_swish(0.4, 0.09), t0 - 0.05, pan=-0.2)
for t0 in (1.0, 2.0, 4.0, 6.5):
    add(kick(0.5), t0)

# ---------------- stabs on the cuts ----------------
chord(Dmaj9, 1.0, 1.0, 0.9)                           # letters fill with the photo
add(cymbal_swell(0.42, 0.10), 1.05)                    # photo grows out of the word
chord([54, 57, 61, 66], 1.5, 0.6, 0.7, roll=0.008)    # photo settles into the panel
chord(Bm9, 2.0, 1.0, 0.8)                             # Phố cổ → Áo dài
add(piano(73, 0.5, 0.6), 2.5 + SW, 0.7, 0.4); add(piano(71, 0.5, 0.6), 2.75 + SW, 0.6, 0.4)
# 3–4  diacritic cards: a rim click + short piano note on every 16th card
mel = [73, 71, 69, 66, 69, 71, 73, 76]
for k in range(8):
    add(rim(0.18), 3 + k * 0.125, pan=0.3 if k % 2 else -0.3)
    add(piano(mel[k], 0.35, 0.55), 3 + k * 0.125, 0.55, 0.25)
chord(Bm9, 3.0, 0.9, 0.6, roll=0.0)

# ---------------- 4–6.5  three sliders: đàn bầu follows each knob ----------------
chord(Gmaj9, 4.0, 2.0, 0.7)
# one sustained bầu line: weight up a major third, slant down a tone, x-height up a fourth,
# then all three back together
def bau_curve(t):
    T = t + 4.40
    c = 4 * smooth((T - 4.46) / 0.44)
    c -= 2 * smooth((T - 5.02) / 0.40)
    c += 5 * smooth((T - 5.56) / 0.44)
    c -= 4.5 * smooth((T - 6.08) / 0.34)
    return c
add(danbau(69, 2.1, bau_curve), 4.40, 1.0, 0.1)        # A4 → C#5 → B4 → E5 → ~C#5
for t0 in (4.42, 4.98, 5.52, 6.04):                     # the cursor grabbing a knob
    add(rim(0.09), t0, pan=0.5)
chord([55, 59, 62, 66], 6.0, 0.6, 0.55, roll=0.006)     # lands on x-height (Em9 colour)

# ---------------- 6.5–7.5  interior + style list: a celesta tick per line ----------------
chord(Em9, 6.42, 1.1, 0.75)
add(brush_swish(0.26, 0.14), 6.38, pan=-0.5)                 # wipe in from the left
for k, m in enumerate([78, 81, 83, 85, 86, 85, 83, 81]):
    add(bell(m, 0.08), 6.56 + k * 0.0625, pan=0.5 - 0.12 * k)
chord(A13, 7.0, 0.8, 0.7)

# ---------------- 7.5–8  the t: tension, snap on 7.75 ----------------
chord([57, 61, 67, 70], 7.5, 0.4, 0.6, roll=0.0)        # A7(b9) colour
add(cymbal_swell(0.5, 0.16), 7.5)
add(bass(A2, 0.25), 7.5); add(bass(A2 - 12, 0.25), 7.75, 0.9)
add(piano(81, 0.4, 0.8), 7.75, 0.8, 0.3); add(rim(0.25), 7.75)
add(piano(78, 0.3, 0.7), 7.875, 0.7, 0.2)

# ---------------- 8–10  end card: resolve to Dmaj9, ring out ----------------
add(kick(0.7), 8.0); add(crash(0.18, 2.0), 8.0, pan=0.3); add(brush_swish(0.28, 0.12), 7.96)
add(bass(D2 - 12 + 12, 1.6, 1.0), 8.0)
chord([38, 50, 54, 57, 61, 64, 69], 8.0, 2.0, 0.95, roll=0.018)
add(danbau(76, 1.3, lambda t: -2 + 2 * smooth((t - 0.05) / 0.7)), 8.62, 0.6, 0.2)   # x-height sweep 495 → 535
for k, m in enumerate([81, 85, 88]):
    add(piano(m, 1.2, 0.5), 9.4 + k * 0.09, 0.5, 0.35)

# ---------------- master: room, glue, fade ----------------
ir_t = tt(1.8)
ir = rng.standard_normal((2, len(ir_t))) * np.exp(-ir_t * 2.8)
ir = np.array([lp(c, 4500, 1) for c in ir]); ir[:, : int(0.015 * SR)] = 0
wet = np.array([fftconvolve(mix[c], ir[c])[:N] for c in range(2)])
wet /= np.max(np.abs(wet)) + 1e-9
out = mix / (np.max(np.abs(mix)) + 1e-9) + 0.28 * wet
out = sosfilt(butter(2, 32, 'hp', fs=SR, output='sos'), out)
# a touch of tape: gentle saturation + faint crackle
out = np.tanh(out * 1.25) / np.tanh(1.25)
crk = np.zeros(N); idx = rng.integers(0, N, 160); crk[idx] = rng.uniform(-1, 1, 160)
crk = bp(crk, 1500, 6000) * 0.25
out += crk
fade = np.ones(N); fl = int(0.4 * SR); fade[-fl:] = np.linspace(1, 0, fl) ** 2
out *= fade
out *= 0.89 / np.max(np.abs(out))

pcm = (out.T * 32767).astype('<i2')
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
