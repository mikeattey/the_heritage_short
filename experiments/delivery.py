"""E8: does a delivery instruction in front of the narration text change pace, pauses and clip length?
Run: .venv/bin/python -m experiments.delivery [s05]   (optional shot ids: only those are generated)
Writes outputs/experiments/delivery/<shot>_instr.wav (the pipeline's own cache is untouched) and prints, for each
line, plain vs instructed clip length and the longest silence inside the clip (ffmpeg silencedetect)."""
import base64, os, re, subprocess, sys, time, requests
from pipeline.common import load_storyboard, need, retry, log_call, OUT
from pipeline.narration import write_wav
from pipeline.assemble import latest

INSTRUCTION = "Say warmly and naturally: "  # attempt 1 (a long English paragraph ending 'Text: ') was read aloud, see EXPERIMENTS E8
DIR = OUT / "experiments" / "delivery"


def synth(model, key, voice, text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}

    def call():
        r = requests.post(url, headers={"x-goog-api-key": key}, json=body, timeout=120)
        r.raise_for_status()
        return base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    return retry(call, tries=6, base=3.0, log={"stage": "experiment-delivery", "model": model,
                                               "params": {"voice": voice, "instruction": True, "text": text}})


def silences(path):
    """(clip length, longest silence strictly inside the clip) using a -40 dB / 0.2 s silencedetect."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "silencedetect=n=-40dB:d=0.2",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    h, m, sec = re.findall(r"Duration: (\d+):(\d+):([\d.]+)", err)[0]
    total = int(h) * 3600 + int(m) * 60 + float(sec)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    inner = [e - s for s, e in zip(starts, ends) if s > 0.05 and e < total - 0.05]
    return total, max(inner, default=0.0)


def main():
    sb = load_storyboard()
    key, model, narrator = need("GEMINI_API_KEY"), need("GEMINI_TTS_MODEL"), need("GEMINI_TTS_VOICE")
    mother = os.environ.get("GEMINI_TTS_VOICE_MOTHER", "Aoede")
    only = set(sys.argv[1:])
    DIR.mkdir(parents=True, exist_ok=True)
    print("shot | plain len | instr len | change | longest inner pause plain -> instr")
    tot_p = tot_i = 0.0
    for s in sb["shots"]:
        if not s["narration"].strip() or (only and s["id"] not in only):
            continue
        out = DIR / f'{s["id"]}_instr.wav'
        if not out.exists():
            voice = mother if s.get("speaker") == "mother" else narrator
            t = time.time()
            write_wav(out, synth(model, key, voice, INSTRUCTION + s["narration"]))
            log_call("experiment-delivery", model, {"shot": s["id"], "voice": voice, "instruction": True}, None,
                     time.time() - t)
        lp, pp = silences(latest("narration", f'{s["id"]}_*.wav'))
        li, pi = silences(out)
        tot_p += lp; tot_i += li
        print(f'{s["id"]} | {lp:.2f}s | {li:.2f}s | {100 * (li - lp) / lp:+.0f}% | {pp:.2f}s -> {pi:.2f}s')
    if not only:
        print(f"total | {tot_p:.1f}s | {tot_i:.1f}s | {100 * (tot_i - tot_p) / tot_p:+.0f}%")


if __name__ == "__main__":
    main()
