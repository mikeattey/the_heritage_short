"""Stage 1: one keyframe per shot via FLUX on Cloudflare Workers AI. Cached by input hash."""
import base64, time, requests
from .common import load_storyboard, need, input_hash, cached_path, retry, log_call


def main():
    sb = load_storyboard()
    acct, tok = need("CF_ACCOUNT_ID"), need("CF_API_TOKEN")
    model = need("CF_IMAGE_MODEL")
    for i, s in enumerate(sb["shots"]):
        prompt = f'{sb["style_block"]}. {sb["character"]}. {s["keyframe_prompt"]}'
        seed = sb.get("seed", 42) + i
        params = {"prompt": prompt, "steps": 8, "seed": seed, "width": 1024, "height": 1024}
        h = input_hash(model, params)
        out = cached_path("keyframes", s["id"], h, "png")
        if out.exists():
            print(f'{s["id"]}: cached'); continue
        t = time.time()

        def call():
            r = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}",
                              headers={"Authorization": f"Bearer {tok}"}, json=params, timeout=120)
            r.raise_for_status()
            return r.json()["result"]["image"]
        out.write_bytes(base64.b64decode(retry(call)))
        log_call("keyframes", model, params, seed, time.time() - t, shot=s["id"], hash=h)
        print(f'{s["id"]}: generated')


if __name__ == "__main__":
    main()
