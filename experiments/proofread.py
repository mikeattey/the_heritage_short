"""E9: ask Gemini to proofread the Amharic narration. Run: .venv/bin/python -m experiments.proofread
Writes experiments/results/proofread_gemini.json (committed as evidence). The Claude side of E9 is written by hand
in experiments/results/proofread_claude.md from the same prompt, so both models get identical input."""
import json, time, requests
from pipeline.common import load_storyboard, need, retry, log_call, ROOT

OUT = ROOT / "experiments" / "results"


def prompt(sb):
    lines = "\n".join(f'{s["id"]} ({s.get("speaker", "narrator")}): {s["narration"]}  [intended meaning: {s["subtitle"]}]'
                      for s in sb["shots"] if s["narration"].strip())
    return ("You are a careful native-level proofreader of Amharic. These are the narration lines of a one-minute "
            "illustrated short film for young Ethiopians, read aloud by a text-to-speech voice. The story: a girl learns "
            "to bake injera, keeps failing, her mother gives her the proverb about the egg, she practises for weeks and "
            "succeeds. For each line decide if it is natural, correct spoken Amharic. Be conservative: mark 'ok' unless "
            "there is a real problem (wrong or unnatural word, grammar, incomplete sentence, wrong register, "
            "meaning different from the intended meaning). Return a JSON array, one object per line, with keys "
            "id, verdict ('ok' or 'flag'), issue (empty if ok), suggestion (empty if ok), reason (one short English sentence).\n\n"
            + lines)


def main():
    sb = load_storyboard()
    key, model = need("GEMINI_API_KEY"), need("GEMINI_TEXT_MODEL")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    p = prompt(sb)
    body = {"contents": [{"parts": [{"text": p}]}], "generationConfig": {"responseMimeType": "application/json"}}
    t = time.time()

    def call():
        r = requests.post(url, headers={"x-goog-api-key": key}, json=body, timeout=180)
        r.raise_for_status()
        return r.json()
    data = retry(call, tries=5, base=3.0, log={"stage": "experiment-proofread", "model": model, "params": {"side": "gemini"}})
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    usage = data.get("usageMetadata", {})
    dt = time.time() - t
    log_call("experiment-proofread", model, {"side": "gemini", "lines": len(sb["shots"])}, None, dt,
             prompt_tokens=usage.get("promptTokenCount"), output_tokens=usage.get("candidatesTokenCount"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "proofread_prompt.txt").write_text(p)
    (OUT / "proofread_gemini.json").write_text(json.dumps(json.loads(text), ensure_ascii=False, indent=2))
    print(f"{dt:.1f}s", usage)
    for r in json.loads(text):
        print(r["id"], r["verdict"], "|", r.get("issue", ""), "|", r.get("suggestion", ""), "|", r.get("reason", ""))


if __name__ == "__main__":
    main()
