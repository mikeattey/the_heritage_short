"""Generate several voice takes of one narration line through the real pipeline (narration_take -> seed -> new cache key).
Run: .venv/bin/python -m experiments.takes s09 1 2 3
Copies each take to outputs/experiments/takes/<shot>_take<N>.wav for listening and prints its length. Leaves the
storyboard unchanged: pick a take afterwards by setting narration_take in storyboard.json. Spaced 22 s apart because the
free tier allows 3 TTS requests per minute (and 10 per day)."""
import json, shutil, sys, time
from pipeline.common import STORYBOARD, OUT, duration_of
from pipeline import narration


def main(shot, takes):
    original = STORYBOARD.read_text()
    dest = OUT / "experiments" / "takes"; dest.mkdir(parents=True, exist_ok=True)
    try:
        for i, take in enumerate(takes):
            sb = json.loads(original)
            for s in sb["shots"]:
                if s["id"] == shot:
                    s["narration_take"] = take
            STORYBOARD.write_text(json.dumps(sb, ensure_ascii=False, indent=2) + "\n")
            before = set((OUT / "narration").glob(f"{shot}_*.wav"))
            narration.main()
            new = set((OUT / "narration").glob(f"{shot}_*.wav")) - before
            if new:
                f = new.pop(); shutil.copy(f, dest / f"{shot}_take{take}.wav")
                print(f"take {take}: {duration_of(f):.2f}s -> {f.name}", flush=True)
            if i < len(takes) - 1:
                time.sleep(22)
    finally:
        STORYBOARD.write_text(original)


if __name__ == "__main__":
    main(sys.argv[1], [int(x) for x in sys.argv[2:]])
