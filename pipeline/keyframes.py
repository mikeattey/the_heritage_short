"""Stage 1: one keyframe per shot via FLUX.2 klein on Cloudflare Workers AI. Cached by input hash.
Prompt = style block + setting + the shot's cast descriptions + the shot prompt. Optional reference mode:
KEYFRAME_REF=outputs/experiments/ref_girl.png passes a reference image (input_image_0) for the girl's shots."""
import base64, os, time, requests
from .common import load_storyboard, need, input_hash, cached_path, retry, log_call, ROOT

DEFAULT_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
SIZE = 1024  # square; shots.py crops to 16:9 or 9:16, so keep the subject centred


def build_prompt(sb, shot):
    cast = " ".join(sb["characters"][c] + "." for c in shot.get("cast", []))
    return f'{sb["style_block"]}. {sb["setting"]}. {cast} {shot["keyframe_prompt"]}'.strip()


def generate(acct, tok, model, prompt, ref_path=None):
    fields = {"prompt": (None, prompt), "width": (None, str(SIZE)), "height": (None, str(SIZE))}
    if ref_path:
        fields["input_image_0"] = ("ref.png", open(ref_path, "rb"), "image/png")
    r = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}",
                      headers={"Authorization": f"Bearer {tok}"}, files=fields, timeout=180)
    r.raise_for_status()
    j = r.json()
    return base64.b64decode(j.get("result", j)["image"])


def main():
    sb = load_storyboard()
    acct, tok = need("CF_ACCOUNT_ID"), need("CF_API_TOKEN")
    model = os.environ.get("CF_IMAGE_MODEL") or DEFAULT_MODEL
    ref = os.environ.get("KEYFRAME_REF")
    for s in sb["shots"]:
        prompt = build_prompt(sb, s)
        use_ref = ref if ref and "girl" in s.get("cast", []) else None
        ref_id = os.path.basename(use_ref) + str(os.path.getsize(use_ref)) if use_ref else None
        params = {"prompt": prompt, "size": SIZE, "ref": ref_id}
        h = input_hash(model, params)
        out = cached_path("keyframes", s["id"], h, "png")
        if out.exists():
            print(f'{s["id"]}: cached'); continue
        t = time.time()
        out.write_bytes(retry(lambda: generate(acct, tok, model, prompt, use_ref), tries=5, base=3.0,
                              log={"stage": "keyframes", "model": model, "params": params, "shot": s["id"], "hash": h}))
        log_call("keyframes", model, params, None, time.time() - t, shot=s["id"], hash=h)
        print(f'{s["id"]}: generated ({time.time() - t:.0f}s)')


if __name__ == "__main__":
    main()
