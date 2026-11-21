"""Lock the showreel to the beats of a recording, with a hold after every screen.

Usage: python3 beatmap.py audio.wav START_SECONDS out_times.json
- beat-tracks the recording from START_SECONDS,
- plays each screen's animation one video beat (0.5 s) per music beat,
- holds at least 2 beats after the animation, then cuts on the next odd (strong) beat,
- writes one video time per output frame (30 fps) for `TIMES=out_times.json node render.js`.
Prints the cut table and the total length.
"""
import sys, json, math
import numpy as np
import librosa

audio, start, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
y, sr = librosa.load(audio, sr=22050, offset=start, duration=45)
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=256)
_, B = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=256, units='time', start_bpm=100, tightness=300)
B = np.asarray(B); idx = np.arange(len(B))

def bt(x):
    if x <= 0: return B[0] + x * (B[1] - B[0])
    if x >= len(B) - 1: return B[-1] + (x - len(B) + 1) * (B[-1] - B[-2])
    return float(np.interp(x, idx, B))

def xb(tau):
    if tau <= B[0]: return (tau - B[0]) / (B[1] - B[0])
    if tau >= B[-1]: return len(B) - 1 + (tau - B[-1]) / (B[-1] - B[-2])
    return float(np.interp(tau, B, idx))

# (video start, animation end, drift rate while holding, name) — video times of showreel.html
S = [(0.0, 1.25, 0, '01-02 AN NAM'), (1.5, 2.2, 0, '03 rosette'), (2.25, 2.4, 0, '04 ink→photo'), (3.0, 3.75, 0, '05 A–Z'),
     (3.8, 4.45, 0, '06 a–z'), (4.5, 5.02, 0, '07 Ẩ'), (5.25, 6.24, 0, '07 glyphs'), (6.25, 6.62, .35, '08 names'),
     (7.5, 8.45, .3, '08b proverb'), (8.75, 9.5, 0, '08c French'), (9.75, 11.2, .3, '09 market')]
segs = []; c = 0.5                      # AN NAM snaps (video 1.25) on beat 3
for i, (vs, ve, rate, name) in enumerate(S):
    xe = c + (ve - vs) / 0.5
    if i == len(S) - 1:
        xn = xe + 6
    else:
        xn = math.ceil(xe + 2); xn += (xn % 2 == 0)
    vnext = S[i + 1][0] if i + 1 < len(S) else 12.0
    segs.append((c, xe, xn, vs, ve, rate, vnext))
    print(f"{name:14s} cut {bt(c):6.2f}s  anim→{bt(xe):6.2f}s  hold {bt(xn) - bt(xe):4.2f}s")
    c = xn
T = bt(segs[-1][2]); print('total', round(T, 2), 's')
ts = []
for tau in np.arange(0, T, 1 / 30):
    x = xb(tau)
    if x < segs[0][0]: ts.append(0.0); continue
    for (c, xe, xn, vs, ve, rate, vnext) in segs:
        if c <= x < xn:
            t = vs + (x - c) * 0.5 if x < xe else ve + (x - xe) * 0.5 * rate
            ts.append(float(min(t, vnext - 0.011))); break
    else:
        ts.append(11.99)
json.dump(ts, open(out, 'w'))
