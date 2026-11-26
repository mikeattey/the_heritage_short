"""Stage 5: concat shots, place narration, duck score with sidechaincompress, loudnorm to -16 LUFS,
burn English subtitles, append the AI end card. Exports 16:9 and 9:16 to outputs/final/."""
import time
from .common import load_storyboard, OUT, ffmpeg, duration_of, log_call, input_hash

SIZES = {"16x9": (1920, 1080), "9x16": (1080, 1920)}
FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_ETHIOPIC = "/System/Library/Fonts/Supplemental/KefaIII.ttf"  # Helvetica has no Ethiopic glyphs


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
    # narration timeline + subtitles
    t0, srt, nar = 0.0, [], []
    for i, s in enumerate(sb["shots"], 1):
        if s["narration"].strip():
            wav = latest("narration", f'{s["id"]}_*.wav')
            d = duration_of(wav)
            if d > s["duration"]:
                print(f'WARN {s["id"]}: narration {d:.1f}s > shot {s["duration"]}s')
            nar.append((wav, t0 + 0.3))
            srt.append(f"{len(srt)+1}\n{srt_time(t0+0.3)} --> {srt_time(t0+0.3+d)}\n{s['subtitle']}\n")
        t0 += s["duration"]
    body_len = t0
    (work / "subs.srt").write_text("\n".join(srt))
    end = sb["end_card"]; end_d = end.get("duration", 4)
    total = body_len + end_d
    score = latest("music", "score_*.wav")
    for name, (w, h) in SIZES.items():
        t = time.time()
        clips = [latest("shots", f'{s["id"]}_{name}_*.mp4') for s in sb["shots"]]
        lst = work / f"concat_{name}.txt"
        lst.write_text("".join(f"file '{c}'\n" for c in clips))
        ffmpeg("-f", "concat", "-safe", 0, "-i", lst, "-c", "copy", work / f"body_{name}.mp4")
        # end card
        (work / "end_text.txt").write_text(end["text"])
        (work / "end_subline.txt").write_text(end.get("subline", ""))
        vf = (f"drawtext=fontfile={FONT}:textfile={work/'end_text.txt'}:fontcolor=white:fontsize={h//18}:x=(w-tw)/2:y=(h/2)-{h//12},"
              f"drawtext=fontfile={FONT_ETHIOPIC}:textfile={work/'end_subline.txt'}:fontcolor=0xE8C27A:fontsize={h//26}:x=(w-tw)/2:y=(h/2)+{h//30},"
              "format=yuv420p")
        ffmpeg("-f", "lavfi", "-i", f"color=c=black:s={w}x{h}:d={end_d}:r=25", "-vf", vf,
               "-c:v", "libx264", work / f"end_{name}.mp4")
        fs = 26 if name == "16x9" else 18
        sub = f"subtitles={work/'subs.srt'}:force_style='FontSize={fs},Outline=2,MarginV={60 if name=='16x9' else 220}'"
        ffmpeg("-i", work / f"body_{name}.mp4", "-i", work / f"end_{name}.mp4",
               "-filter_complex", f"[0:v][1:v]concat=n=2:v=1:a=0[v0];[v0]{sub}[v]", "-map", "[v]",
               "-c:v", "libx264", "-preset", "veryfast", work / f"video_{name}.mp4")
        # audio: delay each narration clip, mix, duck music, loudnorm
        ins, parts = [], []
        for k, (wav, at) in enumerate(nar):
            ins += ["-i", wav]; ms = int(at * 1000)
            parts.append(f"[{k}:a]adelay={ms}|{ms},aresample=44100,aformat=channel_layouts=stereo[n{k}]")
        ins += ["-i", score]
        mix = "".join(f"[n{k}]" for k in range(len(nar)))
        fc = (";".join(parts) + f";{mix}amix=inputs={len(nar)}:normalize=0,asplit=2[voice][vsc];"
              f"[{len(nar)}:a][vsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
              f"[voice][duck]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
        ffmpeg(*ins, "-filter_complex", fc, "-map", "[a]", "-t", total, work / f"audio_{name}.wav")
        out = final / f"heritage_short_{name}.mp4"
        ffmpeg("-i", work / f"video_{name}.mp4", "-i", work / f"audio_{name}.wav", "-map", "0:v", "-map", "1:a",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out)
        log_call("assemble", "ffmpeg", {"aspect": name, "total_s": total}, None, time.time() - t, local=True)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
