"""Stage 4: one TTS clip per shot via Gemini TTS. Cached by (text, voice, model)."""
import base64, os, time, wave, requests
from .common import load_storyboard, need, input_hash, cached_path, retry, log_call


def decode_audio(data):
    """Return (pcm, channels, sample_width, rate). Gemini TTS has returned a full RIFF/WAV file; treating
    its bytes as raw PCM played the header as a click and the trailing metadata chunk as noise (F2).
    Parse the chunks, keep only the 'data' payload, and fall back to raw 24 kHz mono 16-bit PCM."""
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return data, 1, 2, 24000
    ch, width, rate, pos = 1, 2, 24000, 12
    while pos + 8 <= len(data):
        cid, size = data[pos:pos + 4], int.from_bytes(data[pos + 4:pos + 8], "little")
        body = pos + 8
        if cid == b"fmt ":
            ch = int.from_bytes(data[body + 2:body + 4], "little")
            rate = int.from_bytes(data[body + 4:body + 8], "little")
            width = int.from_bytes(data[body + 14:body + 16], "little") // 8
        elif cid == b"data":
            end = len(data) if size in (0, 0xFFFFFFFF) or body + size > len(data) else body + size
            return data[body:end], ch, width, rate
        pos = body + size + (size & 1)
    raise ValueError("WAV response has no data chunk")


def write_wav(path, data):
    pcm, ch, width, rate = decode_audio(data)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(ch); w.setsampwidth(width); w.setframerate(rate); w.writeframes(pcm)


def clip_params(s, model, voices):
    """The inputs that define a narration clip (also its cache key). `narration_take` is added only when set."""
    params = {"text": s["narration"], "voice": voices[s.get("speaker", "narrator")]}
    if s.get("narration_take", 0):
        params["take"] = s["narration_take"]
    return params


def clip_for(s):
    """Path of the clip the storyboard asks for, not merely the newest file for that shot: assemble uses this so
    a re-rolled or older take on disk can never be picked by accident."""
    from .common import load_env
    load_env()
    model = os.environ["GEMINI_TTS_MODEL"]
    voices = {"narrator": os.environ["GEMINI_TTS_VOICE"], "mother": os.environ.get("GEMINI_TTS_VOICE_MOTHER", "Aoede")}
    return cached_path("narration", s["id"], input_hash(model, clip_params(s, model, voices)), "wav")


def main():
    sb = load_storyboard()
    key, model, narrator = need("GEMINI_API_KEY"), need("GEMINI_TTS_MODEL"), need("GEMINI_TTS_VOICE")
    voices = {"narrator": narrator, "mother": os.environ.get("GEMINI_TTS_VOICE_MOTHER", "Aoede")}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    for s in sb["shots"]:
        if not s["narration"].strip():
            continue
        voice = voices[s.get("speaker", "narrator")]
        take = s.get("narration_take", 0)
        params = clip_params(s, model, voices)
        h = input_hash(model, params)
        out = cached_path("narration", s["id"], h, "wav")
        if out.exists():
            print(f'{s["id"]}: cached'); continue
        body = {"contents": [{"parts": [{"text": s["narration"]}]}],
                "generationConfig": {"responseModalities": ["AUDIO"], **({"seed": take} if take else {}),
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
        t = time.time()

        def call():
            r = requests.post(url, headers={"x-goog-api-key": key}, json=body, timeout=120)
            r.raise_for_status()
            return base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
        data = retry(call, tries=6, base=3.0, log={"stage": "narration", "model": model, "params": params, "shot": s["id"], "hash": h})  # free tier 429s: waits 1, 3, 9, 27, 81 s
        write_wav(out, data)
        log_call("narration", model, params, None, time.time() - t, shot=s["id"], hash=h)
        print(f'{s["id"]}: generated')


if __name__ == "__main__":
    main()
