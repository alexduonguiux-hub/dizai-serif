"""12 s score for the AnNam Serif showreel — melody of the traditional Huế court suite
"Lưu thủy – Kim tiền – Xuân phong – Long hổ" (public-domain tradition), transcribed from a reference
recording and re-played with synthesised instruments (no audio from the recording is used).

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


# ---------------- melody transcribed from the Huế court ensemble recording ----------------
# (Lưu thủy – Kim tiền – Xuân phong – Long hổ, traditional; transcribed by ear/pitch-tracking, played here by synths)
# Scale: điệu Bắc on Hò = C → Hò C · Xự D · Xang F (tuned high, ≈ F♯) · Xê G · Cống A
C3, D3, G3, A3, C4, D4, F4, G4, A4, C5, D5 = 48, 50, 55, 57, 60, 62, 65, 67, 69, 72, 74
XANG = 54.4            # Xang below Xê, tuned high as in the recording
B3, Bb3, Gs3 = 59, 58, 56
R = None
STEP = 0.125           # one 16th at 120 BPM

LUU_THUY = [(C4,4),(A3,5),(C4,3),(D4,5),(XANG,4),(R,3),(G3,3),(R,1),(G3,3),
            (R,1),(C4,4),(B3,1),(A3,4),(C4,4),(D4,4),(XANG,4),(G3,2)]
LONG_HO = [(A3,1),(G3,3),(C4,1),(A3,1),(C4,2),(R,1),(G3,4),(R,1),(D4,1),(C4,3),(R,2),
           (A3,2),(G3,2),(C4,1),(A3,1),(G3,2),(XANG,2),(R,1),(A3,1),(C4,3),(G3,2),(XANG,1),(G3,2),
           (A3,1),(R,1),(A3,2),(G3,1),(A3,1),(R,1),(A3,2),(G3,1),(A3,1),(G3,2),(XANG,1),(G3,1),(XANG,3),(C4,4)]


def notes_at(seq, t0, step=STEP):
    out, t = [], t0
    for m, n in seq:
        if m is not None:
            out.append((t, m, n * step))
        t += n * step
    return out, t


def line(notes, kind, gain):
    """Legato line (đàn nhị / sáo): one continuous voice with glides between notes."""
    t_end = max(a + d for a, m, d in notes) + 0.2
    t0 = notes[0][0]
    t = tt(t_end - t0); pitch = np.full_like(t, notes[0][1], dtype=float); amp = np.zeros_like(t)
    for i, (a, m, d) in enumerate(notes):
        i0, i1 = int((a - t0) * SR), int((a - t0 + d) * SR)
        prev = notes[i - 1][1] if i else m
        k = t[i0:i1] - (a - t0)
        pitch[i0:i1] = m + (prev - m) * np.exp(-k * 45)          # quick slide into each note (luyến)
        amp[i0:i1] = np.minimum(1, k / 0.02) * (0.85 + 0.15 * np.exp(-k * 8))
    vib = (0.22 if kind == 'nhi' else 0.12) * np.sin(2 * np.pi * (5.3 if kind == 'nhi' else 5.0) * t)
    f = hz(pitch + vib); ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == 'nhi':
        s = sum((1 / k) * np.sin(k * ph) for k in range(1, 12)); s = bp(s, 300, 4500)
        s += 0.04 * bp(rng.standard_normal(len(t)), 2500, 7000)
    else:
        s = np.sin(ph) + 0.15 * np.sin(2 * ph) + 0.06 * bp(rng.standard_normal(len(t)), 1500, 5000)
    return release(s * lp(amp, 30, 1), 0.12) * gain, t0


def play_melody(seq, t0, octave=0):
    notes, t_end = notes_at(seq, t0)
    notes = [(a, m + octave, d) for a, m, d in notes]
    s, s0 = line(notes, 'nhi', 0.22); add(s, s0, 1.0, -0.3)
    s, s0 = line([(a, m + 12, d) for a, m, d in notes], 'sao', 0.12); add(s, s0, 1.0, 0.35)
    for a, m, d in notes:                                         # đàn nguyệt plucks each note
        add(dan_nguyet(m, max(0.35, d + 0.2), 0.24), a, pan=0.05)
    return t_end


# ================= cue sheet =================
# Lưu thủy (0.25 – 6.4 s), then Long hổ (6.25 – 11.5 s), ending on Hò (C)
add(khanh(C4, 0.4), 0.0, pan=-0.2)
play_melody(LUU_THUY, 0.25)
lh_end = play_melody(LONG_HO, 6.25)
for k in range(5):                                               # đàn tranh glissando into Long hổ
    add(dan_nguyet([C4, D4, F4, G4, A4][k] + 12, 0.6, 0.12), 6.0 + k * 0.045, pan=0.5)

# beat keepers: phách on the beat from 0.5; sênh tiền on the off-beats from 3.0; trống bản every bar
t = 0.5
while t < 11.6:
    add(phach(0.26), t, pan=-0.45)
    if t >= 3.0:
        add(senh_tien(0.14), t + 0.25, pan=0.45)
    if abs((t - 0.5) % 2.0) < 1e-6:
        add(trong_ban(0.38), t, pan=-0.1)
    t += 0.5 if t < 6.25 else 0.25 if t >= 9.75 else 0.5

# accents on the picture cuts
for tc in (1.25, 2.25, 3.0, 4.5, 6.25, 7.5, 8.75, 9.75, 10.5):
    add(trong_dai(0.75 if tc not in (6.25, 9.75) else 1.0), tc)
add(chuong(C5, 0.16, 1.5), 0.5, pan=0.3)                         # symbol cuts in
add(chuong(G4 + 12, 0.18, 1.8), 2.25, pan=0.35)                  # ink → photo
for i in range(9):                                               # HUD types on
    add(senh_tien(0.04, 1), 0.25 + i * 0.04, pan=-0.6 + 0.15 * i)
for i in range(22):                                              # French lines type out
    add(senh_tien(0.035, 1), 8.78 + i * 0.04, pan=-0.5 + 0.045 * i)

# ending: Hò (C) held by fiddle + flute, great drum, bell and stone chime
add(trong_dai(1.1), 11.0); add(khanh(C3 + 12, 0.4, 2.0), 11.0, pan=0.3); add(chuong(C5, 0.25, 1.8), 11.0, pan=-0.3)
s, s0 = line([(11.0, C4, 0.95)], 'nhi', 0.2); add(s, s0, 1.0, -0.3)
s, s0 = line([(11.0, C4 + 12, 0.95)], 'sao', 0.1); add(s, s0, 1.0, 0.35)
add(dan_nguyet(C4, 1.0, 0.3), 11.0)

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
