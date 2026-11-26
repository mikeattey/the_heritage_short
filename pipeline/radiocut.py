"""Radio cut for user test 1: narration clips placed on the storyboard timeline over a placeholder
music bed (synthesised chord, NOT the final score), on a black screen. No subtitles, no pictures.
Output: outputs/final/radio_cut.mp4 (and .m4a for sharing as audio)."""
import time
from .common import load_storyboard, OUT, ffmpeg, duration_of, log_call
from .assemble import latest


def main():
    sb = load_storyboard()
    final = OUT / "final"; final.mkdir(parents=True, exist_ok=True)
    t0, nar = 0.0, []
    for s in sb["shots"]:
        if s["narration"].strip():
            wav = latest("narration", f'{s["id"]}_*.wav')
            nar.append((wav, t0 + 0.3))
            if duration_of(wav) > s["duration"]:
                print(f'WARN {s["id"]}: narration longer than the {s["duration"]}s shot')
        t0 += s["duration"]
    total = t0
    t = time.time()
    ins, parts = [], []
    for k, (wav, at) in enumerate(nar):
        ins += ["-i", wav]; ms = int(at * 1000)
        parts.append(f"[{k}:a]adelay={ms}|{ms},aresample=44100,aformat=channel_layouts=stereo[n{k}]")
    n = len(nar)
    # placeholder bed: A-minor chord of sines with slow tremolo, quiet, ducked under the voice
    bed = ("aevalsrc='0.20*sin(2*PI*220*t)+0.16*sin(2*PI*261.63*t)+0.14*sin(2*PI*329.63*t)':s=44100:d=" + str(total))
    mix = "".join(f"[n{k}]" for k in range(n))
    fc = (";".join(parts) + f";{mix}amix=inputs={n}:normalize=0,asplit=2[voice][vsc];"
          f"[{n}:a]tremolo=f=0.25:d=0.3,volume=0.5,aformat=channel_layouts=stereo[bed];"
          f"[bed][vsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
          f"[voice][duck]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
    audio = OUT / "work"; audio.mkdir(parents=True, exist_ok=True)
    wav_out = audio / "radio_cut.wav"
    ffmpeg(*ins, "-f", "lavfi", "-i", bed, "-filter_complex", fc, "-map", "[a]", "-t", total, wav_out)
    ffmpeg("-i", wav_out, "-c:a", "aac", "-b:a", "160k", final / "radio_cut.m4a")
    ffmpeg("-f", "lavfi", "-i", f"color=c=black:s=1280x720:d={total}:r=10", "-i", wav_out,
           "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k", "-shortest",
           "-movflags", "+faststart", final / "radio_cut.mp4")
    log_call("radiocut", "ffmpeg", {"shots": len(nar), "total_s": total}, None, time.time() - t, local=True)
    print(f"wrote {final/'radio_cut.mp4'} and radio_cut.m4a ({total:.0f}s)")


if __name__ == "__main__":
    main()
