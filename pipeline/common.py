"""Shared helpers: env, storyboard loading, input-hash cache, retries, runs.jsonl logging."""
import hashlib, json, os, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
RUNS = ROOT / "runs.jsonl"
STORYBOARD = ROOT / "storyboard.json"


def load_env():
    """Load .env (git-ignored) into os.environ without overriding real env vars."""
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def need(name):
    load_env()
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f"Missing {name}. Copy .env.example to .env and fill it in.")
    return v


def load_storyboard():
    from .validate import validate
    return validate()


def input_hash(*parts):
    """Stable short hash of JSON-serialisable inputs (prompt, model, params, seed...)."""
    blob = json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


def cached_path(stage, name, h, ext):
    d = OUT / stage
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{name}_{h}.{ext}"


def _short_error(e):
    """Exception type and HTTP status only. Messages can carry URLs (account ids), so they are not logged."""
    code = getattr(getattr(e, "response", None), "status_code", None)
    return f"{type(e).__name__} {code}" if code else type(e).__name__


def retry(fn, tries=4, base=2.0, log=None):
    """Exponential backoff; re-raises after the last attempt.
    log = {"stage", "model", "params", ...extras}: every failed attempt is appended to runs.jsonl with
    success=false, the attempt number and the error type/status (a final failure has final=true)."""
    for i in range(tries):
        t = time.time()
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = i == tries - 1
            if log:
                extra = {k: v for k, v in log.items() if k not in ("stage", "model", "params")}
                log_call(log["stage"], log["model"], log.get("params", {}), None, time.time() - t,
                         success=False, attempt=i + 1, of=tries, error=_short_error(e), final=last, **extra)
            if last:
                raise
            wait = base ** i
            print(f"  retry {i + 1}/{tries - 1} after error: {e} (sleep {wait:.0f}s)")
            time.sleep(wait)


def log_call(stage, model, params, seed, latency_s, cost_usd=0.0, **extra):
    """Append one line to runs.jsonl. cost_usd is the list-price equivalent (free tier = 0 paid)."""
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "stage": stage, "model": model,
           "params": params, "seed": seed, "latency_s": round(latency_s, 2),
           "cost_usd": cost_usd, **extra}
    with open(RUNS, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def ffmpeg(*args):
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *map(str, args)]
    subprocess.run(cmd, check=True)


def duration_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())
