"""Original 10 s score for the AnNam Serif showreel (120 BPM, every cut on the grid).

Đàn-tranh-like plucks (additive, with the 'nhấn' pitch bend) in a pentatonic
scale, a mõ (wood block) on the fast-cut section, minimal kick / hat, whooshes on
the cube turns and a gong-ish hit on the end card. Pure numpy, no samples.
Usage: python3 music.py out.wav
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 10.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
mix = np.zeros((2, N))


def note(n):  # midi -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[0, i:i + len(sig)] += sig * gain * l * 1.414
    mix[1, i:i + len(sig)] += sig * gain * r * 1.414


def pluck(midi, dur=1.6, bend=0.0, bend_at=0.12, bright=1.0):
    """Zither pluck: decaying harmonics, optional bend (semitones) after attack."""
    t = np.arange(int(dur * SR)) / SR
    b = bend * np.clip((t - bend_at) / 0.12, 0, 1) ** 1.5
    vib = 0.12 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.3) / 0.3, 0, 1)
    f = note(midi) * 2 ** ((b + vib) / 12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.zeros_like(t)
    for h in range(1, 9):
        amp = (1 / h ** 1.3) * (bright if h > 2 else 1)
        dec = np.exp(-t * (2.2 + 1.6 * h))
        out += amp * np.sin(h * ph + h * 0.3) * dec
    att = np.clip(t / 0.003, 0, 1)
    # metallic pick transient
    out += 0.25 * rng.standard_normal(len(t)) * np.exp(-t * 300)
    return out * att * 0.35


def kick(gain=1.0):
    t = np.arange(int(0.45 * SR)) / SR
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(1.6 * np.sin(ph) * np.exp(-t * 7.5)) * gain


def hat(dec=55, gain=0.18):
    t = np.arange(int(0.12 * SR)) / SR
    n = rng.standard_normal(len(t))
    n = sosfilt(butter(4, 7000, 'hp', fs=SR, output='sos'), n)
    return n * np.exp(-t * dec) * gain


def woodblock(freq=820):
    t = np.arange(int(0.12 * SR)) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2.73 * t) * np.exp(-t * 60)
    return s * np.exp(-t * 38) * 0.4


def clap():
    t = np.arange(int(0.3 * SR)) / SR
    n = sosfilt(butter(2, [900, 3500], 'bp', fs=SR, output='sos'), rng.standard_normal(len(t)))
    env = np.zeros_like(t)
    for d in (0, 0.009, 0.019):
        env += np.where(t >= d, np.exp(-(t - d) * 90), 0)
    env += 0.4 * np.exp(-t * 14)
    return n * env * 0.35


def sub(midi, dur=0.5, gain=0.5):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * note(midi) * t) + 0.2 * np.sin(4 * np.pi * note(midi) * t)
    return s * np.minimum(1, t / 0.01) * np.exp(-t * 3.2) * gain


def noise_sweep(dur, f0, f1, gain=0.3, shape='updown'):
    """Band-passed noise whose centre glides f0 -> f1 (whoosh / riser)."""
    n = int(dur * SR)
    src = rng.standard_normal(n)
    out = np.zeros(n)
    blocks = 64
    edges = np.linspace(0, n, blocks + 1).astype(int)
    for k in range(blocks):
        a, b = edges[k], edges[k + 1]
        fc = f0 * (f1 / f0) ** (k / (blocks - 1))
        sos = butter(2, [fc * 0.6, min(fc * 1.6, SR / 2 - 100)], 'bp', fs=SR, output='sos')
        seg_ = sosfilt(sos, src[max(0, a - 2048):b])[-(b - a):]
        out[a:b] = seg_
    x = np.linspace(0, 1, n)
    env = np.sin(np.pi * x) ** 2 if shape == 'updown' else x ** 2.2
    return out * env * gain


def gong(midi=33, dur=2.2):
    t = np.arange(int(dur * SR)) / SR
    f = note(midi)
    out = np.zeros_like(t)
    for r, a, d in [(1, 1, 1.2), (2.02, .5, 1.8), (2.76, .35, 2.4), (3.9, .25, 3.0), (5.4, .15, 4.0)]:
        out += a * np.sin(2 * np.pi * f * r * t * (1 + 0.004 * np.exp(-t * 3))) * np.exp(-t * d)
    return out * np.minimum(1, t / 0.004) * 0.45


# pentatonic (A minor pentatonic ~ ngũ cung): A C D E G
A3, C4, D4, E4, G4, A4, C5, D5, E5, G5, A5 = 57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81
B = 0.5  # beat

# --- 0–1  intro: rising arpeggio as AN NAM assembles, swell into the cut
for i, m in enumerate([A3, C4, D4, E4, G4, A4, C5, D5]):
    add(pluck(m, 1.4, bright=0.7), i * 0.125, 0.55 + 0.05 * i, pan=-0.5 + i * 0.14)
add(noise_sweep(0.55, 400, 6000, 0.12, 'up'), 0.45)

# --- 1–2  giant glyphs
add(kick(1.0), 1.0); add(sub(33, 0.6), 1.0)
add(pluck(E5, 2.0, bend=2, bend_at=0.15), 1.0, 0.8, 0.2)
add(kick(0.9), 1.5); add(sub(31, 0.5), 1.5)
add(pluck(D5, 1.6, bend=-1, bend_at=0.2), 1.5, 0.7, -0.2)
add(hat(), 1.25, pan=0.4); add(hat(), 1.75, pan=0.4)

# --- 2–3  rolling rows
for k in range(2):
    add(kick(0.9), 2 + k * B); add(hat(), 2.25 + k * B, pan=0.4)
add(sub(33, 0.5), 2.0); add(sub(36, 0.5), 2.5)
for tt, m in [(2.0, A4), (2.25, C5), (2.5, E5), (2.75, D5)]:
    add(pluck(m, 1.0), tt, 0.6, pan=0.3 if m > 70 else -0.3)
add(clap(), 2.5, 0.9)

# --- 3–4  diacritic flash cards: mõ on every 16th
for k in range(8):
    add(woodblock(980 if k % 2 == 0 else 740), 3 + k * 0.125, 0.9, pan=-0.35 if k % 2 else 0.35)
add(kick(1.0), 3.0); add(kick(0.8), 3.5); add(sub(36, 0.5), 3.0); add(sub(38, 0.5), 3.5)
add(pluck(A5, 1.0, bright=1.2), 3.0, 0.4, 0.5)

# --- 4–5.5  Sài Gòn weight stack: folk-ish phrase with bends
for k in range(3):
    add(kick(0.9), 4 + k * B); add(hat(), 4.25 + k * B, pan=0.4)
add(clap(), 4.5); add(clap(), 5.0, 0.7)
add(sub(33, 0.5), 4.0); add(sub(31, 0.5), 4.5); add(sub(28, 0.5), 5.0)
for tt, m, bd in [(4.0, E5, 0), (4.25, D5, 0), (4.5, C5, 2), (5.0, A4, 0), (5.25, G4, 2)]:
    add(pluck(m, 1.4, bend=bd, bend_at=0.1), tt, 0.65, pan=-0.2)

# --- 5.5–7  poster cube: whooshes on the turns, plucks on the landings
for tt in (5.5, 6.0, 6.5):
    add(kick(0.85), tt); add(hat(), tt + 0.25, pan=0.4)
add(sub(33, 0.5), 5.5)
add(noise_sweep(0.42, 300, 5000, 0.35), 5.74, pan=-0.4)
add(noise_sweep(0.42, 300, 5000, 0.35), 6.38, pan=0.4)
add(pluck(A4, 1.2), 6.12, 0.7, -0.2); add(sub(33, 0.4), 6.12)
add(pluck(E5, 1.2, bend=1), 6.76, 0.7, 0.2); add(sub(40, 0.4), 6.76)

# --- 7–8  ampersand tiles: 16th hats, riser into the end card
add(kick(0.9), 7.0); add(kick(0.9), 7.5); add(sub(36, 0.5), 7.0); add(sub(38, 0.5), 7.5)
for k in range(8):
    add(hat(70, 0.12 + 0.012 * k), 7 + k * 0.125, pan=0.4 if k % 2 else -0.4)
for k, m in enumerate([A4, C5, D5, E5, G5, A5, C5 + 12, D5 + 12]):
    add(pluck(m, 0.6, bright=0.8), 7.5 + k * 0.0625, 0.25 + 0.03 * k, pan=-0.6 + 0.17 * k)
add(noise_sweep(0.95, 300, 9000, 0.22, 'up'), 7.05)

# --- 8–10  end card: impact, digit-roll ticks, ring out
add(kick(1.2), 8.0); add(sub(33, 1.6, 0.7), 8.0); add(gong(45, 2.0), 8.0, 0.5)
for k, m in enumerate([A3, E4, A4, C5, E5]):
    add(pluck(m, 2.0, bend=(1 if m == C5 else 0), bend_at=0.3), 8.0 + k * 0.012, 0.5, pan=-0.4 + 0.2 * k)
for k in range(14):
    tt = 8.25 + k * 0.055 * (1 + k * 0.06)
    add(woodblock(1500 + 60 * (k % 3)), tt, 0.22 * (1 - k / 16), pan=0.3)
add(pluck(A5, 1.0, bend=0), 9.0, 0.45, 0.3)
add(pluck(E5, 1.0, bend=2, bend_at=0.15), 9.25, 0.35, -0.3)

# --- master: reverb, glue, fade
ir_t = np.arange(int(1.6 * SR)) / SR
ir = rng.standard_normal((2, len(ir_t))) * np.exp(-ir_t * 3.2)
ir = np.array([sosfilt(butter(1, 5000, 'lp', fs=SR, output='sos'), c) for c in ir])
ir[:, : int(0.012 * SR)] = 0
wet = np.array([fftconvolve(mix[c], ir[c])[:N] for c in range(2)])
wet /= np.max(np.abs(wet)) + 1e-9
out = mix / (np.max(np.abs(mix)) + 1e-9) + 0.22 * wet
out = sosfilt(butter(2, 30, 'hp', fs=SR, output='sos'), out)
out = np.tanh(out * 1.3) / np.tanh(1.3)
fade = np.ones(N); fl = int(0.35 * SR); fade[-fl:] = np.linspace(1, 0, fl) ** 2
out *= fade
out *= 0.89 / np.max(np.abs(out))

import wave
pcm = (out.T * 32767).astype('<i2')
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
