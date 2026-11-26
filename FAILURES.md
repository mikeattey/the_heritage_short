# FAILURES
Format: what broke -> what I tried -> what fixed it (or didn't).

## F1: Gemini TTS rate limit (HTTP 429) killed the narration run
- **What broke:** the first full narration run generated shots 1-5, then crashed on shot 6 with `429 Too Many Requests` on the free tier. `retry()` only waited 1, 2, 4 s, too short for a per-minute quota.
- **What I tried:** re-running. Cached shots were skipped, which already showed input-hash caching working.
- **Fix:** narration now retries up to 6 times with 1, 3, 9, 27, 81 s backoff. The re-run generated only the 3 missing clips (see runs.jsonl).
- **Lesson:** free-tier limits are part of the design; backoff must match the quota window, not a generic default.

## F2: every narration clip had a click at the start and a burst of noise at the end
- **What broke:** while listening to the radio cut I (the user) heard a cutting, blurry sound in the last instant of every clip. In code the first sample of every file was identical (18770, 17990) and the last 100 ms had RMS ~17,000-24,000 against a body of ~5,000.
- **Diagnosis:** the first two samples decode as ASCII "RIFF". Gemini TTS returned a full WAV file, but my stage wrapped those bytes as raw 24 kHz PCM. So the 44-byte header played as a click and a ~7.7 KB trailing metadata chunk (ASCII text) played as noise, about 0.16 s.
- **Fix:** `narration.decode_audio` parses the RIFF chunks and keeps only the `data` payload (falls back to raw PCM if there is no RIFF header). The cached files hold the original response bytes, so I repaired them without new API calls. After the fix the tail RMS is below 15.
- **Lesson:** I assumed the API returned bare PCM without checking. The same flaw was in the E1 test clip, which I judged "perfect" by ear, so a short flaw can slip past a quick listen. Verify the format of what a model returns, and check the audio numerically.
