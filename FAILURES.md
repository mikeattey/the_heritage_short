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

## F3: the mother was inconsistent and her face appeared in the hands-only shot
- **What broke:** in the first keyframe set the mother wore a different outfit in s05 (striped headscarf, dark green skirt) than in s04 and s08 (white dress), and s04, meant to show only her hands, showed her face and a paper border no other shot had.
- **What I tried:** compared all 8 shots side by side in a contact sheet instead of one by one. Then made her outfit explicit and fixed ("always the same white outfit"), and rewrote s04 as "cropped at the wrist and forearm... no face, no head, no border".
- **Fix:** only s04, s05 and s08 regenerated (cache). Outfit now matches; s04 shows hands only (a sliver of chin remains at the top edge).
- **Lesson:** a vague description ("white shawl, headscarf") gives the model room to vary it; negative instructions in a prompt work only partly, so concrete visual detail helps more.
- **Still imperfect:** the girl looks slightly younger in s05 and s08 than in s02/s03, and s01 has an oversized injera lying on the floor.

## F4: Homebrew FFmpeg 9.1 has no drawtext or subtitles filter
- **What broke:** the first assemble run died on the end card with `No such filter: 'drawtext'`. `ffmpeg -filters` shows neither `drawtext` nor `subtitles` (no libfreetype/libass), so burned-in subtitles and end-card text were impossible as written.
- **What I tried:** considered building a custom FFmpeg (slow, and a stranger cloning the repo would hit the same wall).
- **Fix:** render text to transparent PNGs with Pillow (`pipeline/textimg.py`) and use FFmpeg's `overlay` filter with `enable='between(t,a,b)'` for each subtitle cue; the end card is a full-frame PNG turned into a 4 s clip. Needs only `pip install pillow`. Kefa font handles the Amharic line.
- **Lesson:** I assumed standard filters exist in a standard build. Check `ffmpeg -filters` for what you rely on before designing around it.

## F5: the score vanished after the last narration line and the film shrank to 59 s
- **What broke:** the first successful assemble produced 59.2 s files, not 68 s. The video track was 68 s, but the audio stopped at 59.26 s, the end of the last narration clip.
- **Diagnosis:** `sidechaincompress` ends when its sidechain input (the voice track) ends, so the score was cut there, and `-shortest` in the final mux trimmed the video to match.
- **Fix:** `apad=whole_dur=<total>` on the voice track before the sidechain. Both exports are now 68.00 s with matching video and audio.
- **Lesson:** check durations of every intermediate with ffprobe, not just that the command succeeds.

## F6: ACE-Step import crash on Kaggle (matplotlib backend)
- **Symptom:** `uv run python gen.py` died at `import acestep.handler` with `ValueError: Key backend: 'module://matplotlib_inline.backend_inline' is not a valid value`.
- **Cause:** Kaggle sets `MPLBACKEND` to the notebook's inline backend. The isolated uv environment has no `matplotlib_inline`, so matplotlib rejects it when torchmetrics imports it.
- **Fix:** run with `MPLBACKEND=Agg` (headless backend). One-line change in the run cell.
- **Lesson:** an environment variable inherited from the host notebook leaks into an isolated venv; override it when isolating.

## F7: Cloudflare returned HTTP 400 once, then succeeded on retry
- **What happened:** generating the s09 keyframe, the first request got `400 Bad Request` from Workers AI. The retry 1 s later with the identical prompt succeeded (18 s total).
- **Handling:** `common.retry` caught it, and the failed attempt is in `runs.jsonl` as the first real `success: false` line (error `HTTPError 400`). I did not change the prompt.
- **Open question:** a 400 normally means a bad request, so a retry should not help. Possible causes are a transient fault at the provider or an intermittent input filter; I cannot tell which from the response I log. Lesson: retrying all errors is crude, but it saved this run.
