"""Smoke test: tools, keys (never printed), live API reachability, model IDs, then storyboard validity."""
import os, shutil, requests
from .common import load_env

load_env()
ok = True


def report(name, good, detail=""):
    global ok
    ok &= bool(good)
    print(f"{'PASS' if good else 'FAIL'}  {name} {detail}")


report("ffmpeg", shutil.which("ffmpeg"), "" if shutil.which("ffmpeg") else "(brew install ffmpeg)")
report("ffprobe", shutil.which("ffprobe"))
for k in ["GEMINI_API_KEY", "GEMINI_TEXT_MODEL", "GEMINI_TTS_MODEL", "GEMINI_TTS_VOICE", "CF_ACCOUNT_ID", "CF_API_TOKEN", "CF_IMAGE_MODEL"]:
    report(f"env {k}", os.environ.get(k))

key = os.environ.get("GEMINI_API_KEY")
if key:
    try:
        r = requests.get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200",
                         headers={"x-goog-api-key": key}, timeout=30)
        report("Gemini key", r.ok, f"(HTTP {r.status_code})")
        if r.ok:
            names = {m["name"].split("/")[-1] for m in r.json().get("models", [])}
            for k in ["GEMINI_TEXT_MODEL", "GEMINI_TTS_MODEL"]:
                m = os.environ.get(k)
                report(f"model {m}", m in names, "" if m in names else "(not in model list; candidates: " +
                       ", ".join(sorted(n for n in names if ("flash" in n) and (("tts" in n) == (k == "GEMINI_TTS_MODEL"))))[:300] + ")")
    except requests.RequestException as e:
        report("Gemini key", False, str(e))

acct, tok = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
if acct and tok:
    try:
        r = requests.get(f"https://api.cloudflare.com/client/v4/accounts/{acct}/tokens/verify",
                         headers={"Authorization": f"Bearer {tok}"}, timeout=30)
        report("Cloudflare token", r.ok and r.json().get("success"), f"(HTTP {r.status_code})")
    except requests.RequestException as e:
        report("Cloudflare token", False, str(e))

try:
    from .validate import validate
    validate(); report("storyboard.json", True)
except SystemExit:
    print("WARN  storyboard.json does not validate yet (expected until the story is written)")

raise SystemExit(0 if ok else 1)
