"""Stage 5: concat shots, place narration, duck the score with sidechaincompress, loudnorm to -16 LUFS,
burn English subtitles (Pillow PNG overlays), append the AI end card. Exports 16:9 and 9:16 to outputs/final/."""
import time
from .common import load_storyboard, OUT, ffmpeg, duration_of, log_call
from .textimg import subtitle_png, end_card_png

SIZES = {"16x9": (1920, 1080), "9x16": (1080, 1920)}
FPS = 25


def latest(stage, pattern):
    c = sorted((OUT / stage).glob(pattern), key=lambda p: p.stat().st_mtime)
    if not c:
        raise SystemExit(f"Missing {stage}/{pattern}")
    return c[-1]


def srt_time(t):
    return f"{int(t//3600):02}:{int(t%3600//60):02}:{int(t%60):02},{int(t%1*1000):03}"


def main():
    sb = load_storyboard()
    final = OUT / "final"; final.mkdir(parents=True, exist_ok=True)
    work = OUT / "work"; work.mkdir(parents=True, exist_ok=True)
    # narration timeline + subtitle cues
    t0, cues, nar = 0.0, [], []
    for s in sb["shots"]:
        if s["narration"].strip():
            wav = latest("narration", f'{s["id"]}_*.wav')
            d = duration_of(wav)
            if d > s["duration"]:
                print(f'WARN {s["id"]}: narration {d:.1f}s > shot {s["duration"]}s')
            nar.append((wav, t0 + 0.3))
            cues.append((s["subtitle"], t0 + 0.3, t0 + 0.3 + d + 0.3))
        t0 += s["duration"]
    end = sb["end_card"]; end_d = end.get("duration", 4)
    total = t0 + end_d
    (final / "subtitles_en.srt").write_text("\n".join(
        f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n" for i, (txt, a, b) in enumerate(cues, 1)))
    score = latest("music", "score_*.wav")

    for name, (w, h) in SIZES.items():
        t = time.time()
        clips = [latest("shots", f'{s["id"]}_{name}_*.mp4') for s in sb["shots"]]
        lst = work / f"concat_{name}.txt"
        lst.write_text("".join(f"file '{c}'\n" for c in clips))
        ffmpeg("-f", "concat", "-safe", 0, "-i", lst, "-c", "copy", work / f"body_{name}.mp4")
        # subtitles: one PNG per cue, overlaid only while it is spoken
        pngs = []
        for i, (txt, a, b) in enumerate(cues):
            p = work / f"sub_{name}_{i}.png"; subtitle_png(txt, p, w, h); pngs.append(p)
        margin = int(h * 0.07) if w > h else int(h * 0.20)  # 9:16: clear of the platform UI
        chain, prev = [], "0:v"
        for i, (txt, a, b) in enumerate(cues):
            chain.append(f"[{prev}][{i+1}:v]overlay=x=(W-w)/2:y=H-h-{margin}:enable='between(t,{a:.2f},{b:.2f})'[v{i}]")
            prev = f"v{i}"
        ins = ["-i", work / f"body_{name}.mp4"]
        for p in pngs:
            ins += ["-i", p]
        ffmpeg(*ins, "-filter_complex", ";".join(chain), "-map", f"[{prev}]", "-c:v", "libx264",
               "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", FPS, work / f"subbed_{name}.mp4")
        # end card
        card = work / f"end_{name}.png"; end_card_png(end["text"], end.get("subline", ""), card, w, h)
        ffmpeg("-loop", 1, "-framerate", FPS, "-i", card, "-t", end_d, "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-r", FPS, work / f"end_{name}.mp4")
        ffmpeg("-i", work / f"subbed_{name}.mp4", "-i", work / f"end_{name}.mp4",
               "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]", "-c:v", "libx264",
               "-preset", "veryfast", "-pix_fmt", "yuv420p", work / f"video_{name}.mp4")
        # audio: delay each narration clip, mix, duck the score, loudnorm
        ains, parts = [], []
        for k, (wav, at) in enumerate(nar):
            ains += ["-i", wav]; ms = int(at * 1000)
            parts.append(f"[{k}:a]adelay={ms}|{ms},aresample=44100,aformat=channel_layouts=stereo[n{k}]")
        ains += ["-i", score]
        mix = "".join(f"[n{k}]" for k in range(len(nar)))
        # pad the voice track to the full length: sidechaincompress ends with its sidechain, which cut the score at the last line
        fc = (";".join(parts) + f";{mix}amix=inputs={len(nar)}:normalize=0,apad=whole_dur={total},asplit=2[voice][vsc];"
              f"[{len(nar)}:a][vsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
              f"[voice][duck]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
        ffmpeg(*ains, "-filter_complex", fc, "-map", "[a]", "-t", total, work / f"audio_{name}.wav")
        out = final / f"heritage_short_{name}.mp4"
        ffmpeg("-i", work / f"video_{name}.mp4", "-i", work / f"audio_{name}.wav", "-map", "0:v", "-map", "1:a",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out)
        log_call("assemble", "ffmpeg", {"aspect": name, "total_s": total, "score": score.name}, None,
                 time.time() - t, local=True)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
