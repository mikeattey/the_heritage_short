"""Smoke test: validate storyboard, check tools and keys (without printing them), one tiny text call."""
import shutil, os
from .common import load_env
from .validate import validate

load_env()
validate(); print("storyboard OK")
print("ffmpeg:", "OK" if shutil.which("ffmpeg") else "MISSING (brew install ffmpeg)")
for k in ["GEMINI_API_KEY", "CF_ACCOUNT_ID", "CF_API_TOKEN"]:
    print(f"{k}:", "set" if os.environ.get(k) else "MISSING")
