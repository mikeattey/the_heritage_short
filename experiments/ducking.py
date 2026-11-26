"""E7: how does the sidechaincompress threshold change ducking? Run: .venv/bin/python -m experiments.ducking
Builds the same voice+score graph as pipeline/assemble.py for several thresholds, and measures (pure Python,
no numpy) how far the score drops while the narrator speaks, and how quickly it recovers afterwards."""
import array, math, time, wave
from pipeline.common import load_storyboard, OUT, ffmpeg, duration_of, log_call
from pipeline.assemble import latest

THRESHOLDS = [0.015, 0.03, 0.06]
RATIO, ATTACK, RELEASE = 8, 20, 400
SR = 16000
WORK = OUT / "experiments" / "ducking"


def timeline(sb):
    t0, nar, spans = 0.0, [], []
    for s in sb["shots"]:
        if s["narration"].strip():
            wav = latest("narration", f'{s["id"]}_*.wav')
            d = duration_of(wav); a = t0 + 0.3
            nar.append((wav, a)); spans.append((a, a + d))
        t0 += s["duration"]
    return nar, spans, t0 + sb["end_card"].get("duration", 4)


def render(nar, score, total, thr):
    ins, parts = [], []
    for k, (wav, at) in enumerate(nar):
        ins += ["-i", wav]; ms = int(at * 1000)
        parts.append(f"[{k}:a]adelay={ms}|{ms},aresample=44100,aformat=channel_layouts=stereo[n{k}]")
    ins += ["-i", score]
    mix = "".join(f"[n{k}]" for k in range(len(nar)))
    fc = (";".join(parts) + f";{mix}amix=inputs={len(nar)}:normalize=0,apad=whole_dur={total},asplit=2[voice][vsc];"
          f"[{len(nar)}:a][vsc]sidechaincompress=threshold={thr}:ratio={RATIO}:attack={ATTACK}:release={RELEASE}[duck]")
    out = ["-t", total, "-ac", 1, "-ar", SR, "-c:a", "pcm_s16le"]
    ffmpeg(*ins, "-filter_complex", fc, "-map", "[voice]", *out, WORK / "voice.wav",
           "-map", "[duck]", *out, WORK / f"duck_{thr}.wav")  # both pads in one pass: FFmpeg rejects unused labels


def mono(path):
    with wave.open(str(path)) as w:
        a = array.array("h"); a.frombytes(w.readframes(w.getnframes()))
    return a


def rms_db(x, a, b):
    seg = x[int(a * SR):int(b * SR)]
    if not len(seg):
        return float("nan")
    return 10 * math.log10(max(sum(v * v for v in seg) / len(seg), 1.0) / 32768 ** 2)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    sb = load_storyboard()
    nar, spans, total = timeline(sb)
    score = latest("music", "score_*.wav")
    ffmpeg("-i", score, "-t", total, "-ac", 1, "-ar", SR, "-c:a", "pcm_s16le", WORK / "score_raw.wav")
    raw = mono(WORK / "score_raw.wav")
    rows = []
    for thr in THRESHOLDS:
        t = time.time()
        render(nar, score, total, thr)
        log_call("experiment-ducking", "ffmpeg sidechaincompress", {"threshold": thr, "ratio": RATIO,
                 "attack_ms": ATTACK, "release_ms": RELEASE}, None, time.time() - t, local=True)
        duck, voice = mono(WORK / f"duck_{thr}.wav"), mono(WORK / "voice.wav")
        # speech windows (inset 0.2 s from the edges) and gaps (at least 0.6 s clear of speech)
        drops, margins, rec = [], [], []
        for a, b in spans:
            drops.append(rms_db(raw, a + .2, b - .2) - rms_db(duck, a + .2, b - .2))
            margins.append(rms_db(voice, a + .2, b - .2) - rms_db(duck, a + .2, b - .2))
            # recovery: first 50 ms frame after speech ends where the ducked score is within 3 dB of the raw score
            for k in range(0, 40):
                f = b + k * 0.05
                if rms_db(raw, f, f + .05) - rms_db(duck, f, f + .05) < 3:
                    rec.append(k * 0.05); break
            else:
                rec.append(2.0)
        gap_drop, n = 0.0, 0
        edges = [0.0] + [x for ab in spans for x in ab] + [total]
        for i in range(0, len(edges), 2):
            a, b = edges[i] + .6, edges[i + 1] - .6
            if b - a > .3:
                gap_drop += rms_db(raw, a, b) - rms_db(duck, a, b); n += 1
        rows.append((thr, sum(drops) / len(drops), sum(margins) / len(margins), gap_drop / max(n, 1), sum(rec) / len(rec)))
    print("threshold | score drop in speech (dB) | voice over score in speech (dB) | score drop in gaps (dB) | mean recovery (s)")
    for r in rows:
        print(f"{r[0]:>9} | {r[1]:>25.1f} | {r[2]:>31.1f} | {r[3]:>23.1f} | {r[4]:>17.2f}")


if __name__ == "__main__":
    main()
