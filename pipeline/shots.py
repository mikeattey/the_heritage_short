"""Stage 2: moving shots. Default = FFmpeg Ken Burns on the keyframe (local, free, deterministic).
motion.engine == "wan": uses outputs/shots/<id>_wan.mp4 produced by notebooks/wan_kaggle.ipynb if present,
otherwise falls back to Ken Burns (logged). Rendered per aspect ratio so both exports are native crops."""
import time
from .common import load_storyboard, input_hash, cached_path, ffmpeg, log_call, OUT

SIZES = {"16x9": (1920, 1080), "9x16": (1080, 1920)}
FPS = 25


def keyframe_for(shot_id):
    c = sorted((OUT / "keyframes").glob(f"{shot_id}_*.png"), key=lambda p: p.stat().st_mtime)
    if not c:
        raise SystemExit(f"No keyframe for {shot_id}; run make keyframes")
    return c[-1]


def kenburns(img, out, w, h, dur, kind):
    n = int(dur * FPS)
    z = {"zoom_in": f"min(1+0.0008*on,1.25)", "zoom_out": f"max(1.25-0.0008*on,1.0)"}.get(kind, "1.15")
    x = {"pan_left": f"(iw-iw/zoom)*(1-on/{n})", "pan_right": f"(iw-iw/zoom)*(on/{n})"}.get(kind, "iw/2-(iw/zoom/2)")
    vf = (f"scale=-2:{h*2},crop={w*2}:{h*2},zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d={n}:s={w}x{h}:fps={FPS},format=yuv420p")
    ffmpeg("-i", img, "-vf", vf, "-t", dur, "-c:v", "libx264", "-preset", "veryfast", out)


def main():
    sb = load_storyboard()
    for s in sb["shots"]:
        m = s.get("motion", {})
        kf = keyframe_for(s["id"])
        for name, (w, h) in SIZES.items():
            wan = list((OUT / "shots").glob(f'{s["id"]}_wan.mp4')) if m.get("engine") == "wan" else []
            params = {"engine": "wan" if wan else "kenburns", "kind": m.get("kind", "zoom_in"), "dur": s["duration"],
                      "size": [w, h], "keyframe": kf.name, "wan": [p.name for p in wan]}
            h8 = input_hash(params)
            out = cached_path("shots", f'{s["id"]}_{name}', h8, "mp4")
            if out.exists():
                print(f'{s["id"]} {name}: cached'); continue
            t = time.time()
            if wan:
                ffmpeg("-i", wan[0], "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS},format=yuv420p",
                       "-t", s["duration"], "-c:v", "libx264", out)
            else:
                kenburns(kf, out, w, h, s["duration"], params["kind"])
            log_call("shots", params["engine"], params, None, time.time() - t, shot=s["id"], hash=h8, local=True)
            print(f'{s["id"]} {name}: rendered')


if __name__ == "__main__":
    main()
