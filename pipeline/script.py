"""Stage 0 (optional, run by hand): draft storyboard.json from a story brief with Gemini.
Usage: python -m pipeline.script brief.txt  -> writes storyboard.draft.json (review, then copy over storyboard.json)."""
import json, sys, time, requests
from .common import ROOT, need, retry, log_call


def main(brief_path):
    key, model = need("GEMINI_API_KEY"), need("GEMINI_TEXT_MODEL")
    schema = (ROOT / "schema" / "storyboard.schema.json").read_text()
    brief = open(brief_path).read()
    prompt = f"Write a storyboard for a 60-90s illustrated short film. Brief:\n{brief}\nReturn JSON only, matching this JSON Schema:\n{schema}"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}
    t = time.time()
    def call():
        r = requests.post(url, headers={"x-goog-api-key": key}, json=body, timeout=120)
        r.raise_for_status()
        return r
    r = retry(call)
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    log_call("script", model, {"brief": brief_path}, None, time.time() - t)
    (ROOT / "storyboard.draft.json").write_text(json.dumps(json.loads(text), indent=2, ensure_ascii=False))
    print("wrote storyboard.draft.json")


if __name__ == "__main__":
    main(sys.argv[1])
