"""Stage 4: one TTS clip per shot via Gemini TTS. Cached by (text, voice, model)."""
import base64, os, time, wave, requests
from .common import load_storyboard, need, input_hash, cached_path, retry, log_call


def main():
    sb = load_storyboard()
    key, model, narrator = need("GEMINI_API_KEY"), need("GEMINI_TTS_MODEL"), need("GEMINI_TTS_VOICE")
    voices = {"narrator": narrator, "mother": os.environ.get("GEMINI_TTS_VOICE_MOTHER", "Aoede")}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    for s in sb["shots"]:
        if not s["narration"].strip():
            continue
        voice = voices[s.get("speaker", "narrator")]
        params = {"text": s["narration"], "voice": voice}
        h = input_hash(model, params)
        out = cached_path("narration", s["id"], h, "wav")
        if out.exists():
            print(f'{s["id"]}: cached'); continue
        body = {"contents": [{"parts": [{"text": s["narration"]}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
        t = time.time()

        def call():
            r = requests.post(url, headers={"x-goog-api-key": key}, json=body, timeout=120)
            r.raise_for_status()
            return base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
        pcm = retry(call, tries=6, base=3.0)  # free tier 429s: waits 1, 3, 9, 27, 81 s
        with wave.open(str(out), "wb") as w:  # Gemini TTS returns 24 kHz mono 16-bit PCM
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
        log_call("narration", model, params, None, time.time() - t, shot=s["id"], hash=h)
        print(f'{s["id"]}: generated')


if __name__ == "__main__":
    main()
