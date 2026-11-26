"""E11: does moving the crop window up keep the girl's head in the 16:9 frame of s02?
Run: .venv/bin/python -m experiments.cropfocus s02 0.5 0.25 0.1 0.0
Renders the 16:9 Ken Burns clip for each focus value (focus 0 = top of the square keyframe), grabs the first and last
frame, and counts hair-dark pixels in the top row of the frame (a cut-off head means hair touches the top edge)."""
import sys, subprocess
from PIL import Image
from pipeline.common import OUT, ffmpeg, load_storyboard
from pipeline.shots import kenburns, keyframe_for

D = OUT / "experiments" / "cropfocus"


def top_row_dark(png, thresh=60):
    im = Image.open(png).convert("L"); w, h = im.size
    row = [im.getpixel((x, 1)) for x in range(w)]
    return sum(v < thresh for v in row)


def main(shot, focuses):
    D.mkdir(parents=True, exist_ok=True)
    s = next(x for x in load_storyboard()["shots"] if x["id"] == shot)
    kind = s.get("motion", {}).get("kind", "zoom_in")
    print("focus | dark pixels in top row at start | at end")
    for f in focuses:
        clip = D / f"{shot}_focus{f}.mp4"
        kenburns(keyframe_for(shot), clip, 1920, 1080, s["duration"], kind, f)
        res = []
        for tag, t in (("start", 0.1), ("end", s["duration"] - 0.2)):
            png = D / f"{shot}_focus{f}_{tag}.png"
            ffmpeg("-ss", t, "-i", clip, "-frames:v", 1, png)
            res.append(top_row_dark(png))
        print(f"{f} | {res[0]} | {res[1]}")


if __name__ == "__main__":
    main(sys.argv[1], [float(x) for x in sys.argv[2:]])
