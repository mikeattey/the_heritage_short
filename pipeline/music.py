"""Stage 3: music. ACE-Step 1.5 runs on Kaggle/Colab (notebooks/acestep_kaggle.ipynb) and writes
candidates to outputs/music/. This stage checks the chosen candidate exists and trims/pads it to the film length.
Record the choice + reason in EXPERIMENTS.md and set storyboard.music.chosen."""
import time
from .common import load_storyboard, OUT, ffmpeg, log_call, input_hash, cached_path


def main():
    sb = load_storyboard()
    chosen = sb["music"].get("chosen")
    if not chosen:
        raise SystemExit("Set storyboard.music.chosen to a file in outputs/music/ (generate candidates in the Kaggle notebook).")
    src = OUT / "music" / chosen
    if not src.exists():
        raise SystemExit(f"{src} not found. Download candidates from the Kaggle notebook output.")
    total = sum(s["duration"] for s in sb["shots"]) + sb["end_card"].get("duration", 4)
    h = input_hash(chosen, total, src.stat().st_size)
    out = cached_path("music", "score", h, "wav")
    if out.exists():
        print("score: cached"); return
    t = time.time()
    ffmpeg("-i", src, "-af", f"apad,atrim=0:{total},afade=t=in:d=1,afade=t=out:st={total-3}:d=3", "-ar", 44100, "-ac", 2, out)
    log_call("music", "ffmpeg-trim", {"src": chosen, "total": total}, None, time.time() - t, local=True, hash=h)
    print("score: ready")


if __name__ == "__main__":
    main()
