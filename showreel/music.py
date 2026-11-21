"""Original 12 s score for the AnNam Serif showreel — Huế royal court music colours (Nhã nhạc cung đình).

Instruments (all synthesised, no samples): trống đại (great drum), trống bản (small drum),
phách (wood clapper), sênh tiền (coin clapper), chuông (bell), khánh (stone chime),
kèn bầu (double-reed oboe, the lead), sáo (bamboo flute), đàn nhị (two-string fiddle),
đàn nguyệt (moon lute). Pentatonic "điệu Bắc" on D (Hò Xự Xang Xê Cống ≈ D E G A B).
Cues follow the Figma storyboard (Story-01 … 09, 12 s cut).
Usage: python3 music.py out.wav
"""
import sys
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 12.0
N = int(SR * DUR)
rng = np.random.default_rng(23)
mix = np.zeros((2, N))
B = 0.5


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def bp(x, a, b, o=2):
    return sosfilt(butter(o, [a, b], 'bp', fs=SR, output='sos'), x)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, 'lp', fs=SR, output='sos'), x)


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0:
        return
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[0, i:i + len(sig)] += sig * gain * l * 1.414
    mix[1, i:i + len(sig)] += sig * gain * r * 1.414


def smooth(x):
    x = np.clip(x, 0, 1)
    return np.where(x < .5, 8 * x ** 4, 1 - (-2 * x + 2) ** 4 / 2)


def release(s, r=0.08):
    n = min(len(s), int(r * SR)); s[-n:] *= np.linspace(1, 0, n); return s


# ---------------- percussion ----------------
def trong_dai(gain=1.0, dur=1.6):
    t = tt(dur); f = 46 + 30 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6)
    skin = lp(rng.standard_normal(len(t)), 300) * np.exp(-t * 20) * 0.6
    return np.tanh(1.4 * (body + skin)) * 0.8 * gain


def trong_ban(gain=0.5):
    t = tt(0.25); f = 190 + 60 * np.exp(-t * 40)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)
    s += 0.4 * bp(rng.standard_normal(len(t)), 300, 1500) * np.exp(-t * 45)
    return s * gain


def phach(gain=0.5):
    t = tt(0.06)
    s = bp(rng.standard_normal(len(t)), 1800, 4200) * np.exp(-t * 140) + 0.6 * np.sin(2 * np.pi * 2300 * t) * np.exp(-t * 110)
    return s * gain


def senh_tien(gain=0.25, clicks=3, gap=0.016):
    t = tt(0.16); out = np.zeros_like(t)
    for c in range(clicks):
        k = t - c * gap
        on = k >= 0
        out[on] += bp(rng.standard_normal(on.sum()), 4500, 11000) * np.exp(-k[on] * 120) * (1 - 0.2 * c)
    return out * gain


def chuong(m=81, gain=0.3, dur=2.5):
    t = tt(dur); f = hz(m); out = np.zeros_like(t)
    for r, a, d in [(1, 1, 1.1), (2.0, .45, 1.6), (2.76, .35, 2.2), (5.4, .2, 3.4), (8.9, .1, 5.0)]:
        out += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d)
    return out * np.minimum(1, t / 0.002) * gain


def khanh(m=69, gain=0.35, dur=1.8):
    """Stone chime: dull attack, few inharmonic partials, quick upper decay."""
    t = tt(dur); f = hz(m); out = np.zeros_like(t)
    for r, a, d in [(1, 1, 2.0), (2.32, .5, 4.5), (4.1, .3, 9.0), (6.8, .15, 14.0)]:
        out += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d)
    out += 0.3 * bp(rng.standard_normal(len(t)), 800, 3000) * np.exp(-t * 80)
    return out * gain


# ---------------- melodic ----------------
def ken_bau(notes, gain=0.32):
    """Kèn bầu: nasal double reed. notes = [(t_rel, midi, dur, bend_curve or None)] stitched legato."""
    end = max(a + d for a, m, d, c in notes) + 0.15
    t = tt(end); pitch = np.full_like(t, np.nan); amp = np.zeros_like(t)
    for a, m, d, c in notes:
        i0, i1 = int(a * SR), int((a + d) * SR)
        k = t[i0:i1] - a
        p = m + (c(k) if c else 0)
        pitch[i0:i1] = p
        env = np.minimum(1, k / 0.03) * np.minimum(1, (d - k) / 0.04 + 0.35)
        amp[i0:i1] = np.maximum(amp[i0:i1], env)
    # hold pitch across tiny gaps, vibrato deepening on long notes
    pitch = np.where(np.isnan(pitch), notes[0][1], pitch)
    vib = 0.35 * np.sin(2 * np.pi * 6.2 * t) * np.clip((t % 1.0) / 0.4, 0, 1)
    f = hz(pitch + vib)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.zeros_like(t)
    for h, a in enumerate([.55, .7, 1.0, .9, .75, .55, .4, .3, .2, .14, .1], start=1):
        out += a * np.sin(h * ph)
    out = bp(out, 500, 5200) + 0.25 * bp(out, 1100, 1500)          # reed formant
    out += 0.05 * bp(rng.standard_normal(len(t)), 2000, 6000)      # breath / buzz
    return release(out * lp(amp, 40, 1), 0.1) * gain * 0.5


def dan_nhi(m, dur, curve=None, gain=0.2):
    t = tt(dur)
    vib = 0.25 * np.sin(2 * np.pi * 5.4 * t) * np.clip((t - 0.15) / 0.3, 0, 1)
    f = hz(m + (curve(t) if curve else 0) + vib)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = sum((1 / k) * np.sin(k * ph) for k in range(1, 12))
    out = bp(out, 300, 4500)
    out += 0.04 * bp(rng.standard_normal(len(t)), 2500, 7000)      # bow hair
    env = np.minimum(1, t / 0.07) * np.minimum(1, (dur - t) / 0.12)
    return out * env * gain


def sao(m, dur, gain=0.16):
    t = tt(dur)
    f = hz(m) * 2 ** (0.12 * np.sin(2 * np.pi * 5 * t) * np.clip((t - .2) / .3, 0, 1) / 12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.2 * bp(rng.standard_normal(len(t)), 1200, 4000) * 0.3
    env = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.1)
    return s * env * gain


def dan_nguyet(m, dur=0.9, gain=0.3, bend=0.0):
    t = tt(dur)
    b = bend * smooth((t - 0.08) / 0.15)
    f = hz(m) * 2 ** (b / 12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.zeros_like(t)
    for k in range(1, 9):
        out += (1 / k ** 1.2) * np.sin(k * ph + k) * np.exp(-t * (3 + 2.2 * k))
    out += 0.25 * bp(rng.standard_normal(len(t)), 2000, 7000) * np.exp(-t * 250)
    return out * np.minimum(1, t / 0.002) * gain


# điệu Bắc on D: D E G A B
D4, E4, G4, A4, B4, D5, E5, G5, A5, B5 = 62, 64, 67, 69, 71, 74, 76, 79, 81, 83
D3, A3 = 50, 57

# ================= cue sheet (hard cuts on the 120 BPM grid) =================
def groove(t0, t1, drum=(0, 3)):
    k = 0; t = t0
    while t < t1 - 1e-6:
        add(senh_tien(0.15 if k % 2 else 0.2), t, pan=0.45)
        add(phach(0.3 if k % 2 == 0 else 0.16), t + 0.125, pan=-0.45)
        if k % 4 in drum:
            add(trong_ban(0.42), t, pan=-0.1)
        t += 0.25; k += 1

# 01  paper — a stone chime opens the court
add(khanh(A4, 0.4), 0.0, pan=-0.2)
# 02  HUD types on (tiny coin taps); symbol cuts in (bell); AN NAM letters drop one per 16th (moon lute), snap at 1.25
for i in range(9):
    add(senh_tien(0.05, 1), 0.25 + i * 0.04, pan=-0.6 + 0.15 * i)
add(chuong(D5 + 12, 0.16, 1.5), 0.5, pan=0.3)
for i, m in enumerate([D4, E4, G4, A4, B4, D5]):
    add(dan_nguyet(m, 0.9, 0.3), 0.5 + i * 0.125, pan=-0.5 + 0.2 * i)
add(trong_dai(1.0), 1.25); add(phach(0.5), 1.25)
# 03  rosette turns in four snaps (stone chime steps); weight wave through AN NAM (kèn bầu swell)
for i, m in enumerate([A4, B4, D5, E5, A5]):
    add(khanh(m, 0.18, 0.9), 1.5 + i * 0.125, pan=-0.4 + 0.2 * i)
add(ken_bau([(0, D5, 0.2, None), (0.2, E5, 0.45, lambda k: -1.0 * np.exp(-k * 16))]), 1.75, 0.9, 0.0)
# 04  hard cut: ink becomes the photo (great drum + bell), one-frame flicker
add(trong_dai(0.9), 2.25); add(chuong(A5, 0.26, 2.2), 2.25, pan=0.35)
add(dan_nhi(A4, 0.7, lambda k: 2 * smooth((k - 0.4) / 0.2), 0.14), 2.3, pan=-0.3)
# 05–06  cut to Huế; letters out of the depth — ensemble enters
add(trong_dai(1.0), 3.0); add(chuong(D5, 0.2, 1.8), 3.0, pan=-0.4)
groove(3.0, 4.5)
for k, m in enumerate([D4, A4, G4, A4, D5, A4]):
    add(dan_nguyet(m, 0.45, 0.2), 3.0 + k * 0.25, pan=-0.25)
add(ken_bau([(0, D5, 0.3, None), (0.3, E5, 0.2, None), (0.5, G5, 0.3, lambda k: 0.8 * np.sin(np.pi * np.clip(k / 0.12, 0, 1))),
             (0.8, E5, 0.2, None)]), 3.05, 0.95, 0.1)
add(sao(A5, 0.4), 3.85, pan=0.3); add(sao(B5, 0.45), 4.0, pan=0.3)
# 07  cut to the guide lines; A breathes through weight (fiddle swell); ^ (bell), hook (kèn hỏi tone); glyph cuts
add(phach(0.5), 4.5); add(trong_ban(0.5), 4.5)
add(dan_nhi(D4, 0.4, lambda k: 3 * np.sin(np.pi * np.clip(k / 0.35, 0, 1)), 0.16), 4.5, pan=-0.2)
add(chuong(D5, 0.16, 1.0), 4.875, pan=0.3)
add(ken_bau([(0, A4, 0.3, lambda k: -1.6 * np.sin(np.pi * np.clip(k / 0.15, 0, 1)) + 2 * smooth((k - 0.11) / 0.14))]), 5.0, 0.85, 0.1)
for k, m in enumerate([D4, E4, G4, A4, B4, D5, E5, G5]):        # Ở Ữ Đ Ặ · ặ ơ đ ỹ
    add(dan_nguyet(m, 0.4, 0.26), 5.25 + k * 0.125, pan=-0.35 + 0.1 * k)
    add(phach(0.14), 5.25 + k * 0.125, pan=0.45)
# 08  names: characters switch on in random order (coin-clapper roll), then the tutti
add(trong_dai(0.9), 6.25)
for i in range(10):
    add(senh_tien(0.08, 1), 6.25 + rng.uniform(0, 0.34), pan=rng.uniform(-0.6, 0.6))
groove(6.5, 7.5, drum=(0, 2))
add(ken_bau([(0, A4, .25, None), (.25, D5, .25, None), (.5, E5, .2, None), (.7, D5, .2, None), (.9, B4, .3, None)]), 6.3, 0.9, 0.05)
# 08b  the proverb lands word by word (wood clap on 8ths); the boat cuts in (fiddle + flute)
for k in range(8):
    add(phach(0.22 if k % 2 == 0 else 0.12), 7.5 + k * 0.125, pan=-0.3 + 0.08 * k)
add(trong_ban(0.45), 7.875)
add(dan_nhi(D4, 0.85, lambda k: np.interp(k, [0, .25, .45, .7, .85], [0, 2, 5, 3, 0]), 0.17), 7.875, pan=-0.3)
add(sao(D5, 0.35), 8.0, pan=0.35); add(sao(E5, 0.3), 8.375, pan=0.35)
# 08c  the French lines type out (a rattle of taps), great drum under, a solemn kèn line
add(trong_dai(0.8), 8.75)
for i in range(22):
    add(senh_tien(0.045, 1), 8.78 + i * 0.04, pan=-0.5 + 0.045 * i)
add(ken_bau([(0, D5, 0.4, None), (0.4, B4, 0.25, None), (0.65, A4, 0.3, lambda k: -0.8 * np.exp(-k * 6))]), 8.8, 0.75, 0.0)
# 09  hard cut to the market; AN NAM gathers (lute), snaps at 10.5 (drum + bells); the styles type on
add(trong_dai(1.0), 9.75); add(chuong(D5, 0.25, 2.0), 9.75, pan=-0.3)
for i, m in enumerate([D4, E4, G4, A4, B4, D5]):
    add(dan_nguyet(m, 0.8, 0.26), 9.875 + i * 0.09, pan=-0.5 + 0.2 * i)
add(trong_dai(1.1), 10.5); add(khanh(D4, 0.4, 2.5), 10.5, pan=0.3); add(senh_tien(0.25, 4, 0.018), 10.5, pan=0.5)
add(ken_bau([(0, D5, 0.2, None), (0.2, E5, 0.2, None), (0.4, G5, 0.2, None), (0.6, A5, 0.9, lambda k: -1 * np.exp(-k * 12))]), 10.5, 0.95, 0.0)
add(dan_nhi(D5, 1.3, gain=0.12), 10.5, pan=-0.35)
for i in range(12):
    add(senh_tien(0.04, 1), 10.62 + i * 0.06, pan=0.3)
add(chuong(A5, 0.22, 1.6), 11.1, pan=0.4)

# ================= master =================
ir_t = tt(2.2)
ir = rng.standard_normal((2, len(ir_t))) * np.exp(-ir_t * 2.4)
ir = np.array([lp(c, 5000, 1) for c in ir]); ir[:, : int(0.02 * SR)] = 0
wet = np.array([fftconvolve(mix[c], ir[c])[:N] for c in range(2)])
wet /= np.max(np.abs(wet)) + 1e-9
out = mix / (np.max(np.abs(mix)) + 1e-9) + 0.3 * wet
out = sosfilt(butter(2, 30, 'hp', fs=SR, output='sos'), out)
out = np.tanh(out * 1.3) / np.tanh(1.3)
fade = np.ones(N); fl = int(0.6 * SR); fade[-fl:] = np.linspace(1, 0, fl) ** 2
out *= fade
out *= 0.89 / np.max(np.abs(out))
pcm = (out.T * 32767).astype('<i2')
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
