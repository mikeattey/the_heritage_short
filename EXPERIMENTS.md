# EXPERIMENTS
Format: **E#: hypothesis** -> change -> result (numbers from runs.jsonl where possible). Target ~10.

## E1: Gemini Flash TTS can narrate Amharic well enough for a native-speaker audience
- **Hypothesis:** The free Gemini TTS model handles Amharic script input, so I can narrate in my audience's language instead of English.
- **Change:** One call with the proverb in Amharic script ("ቀስ በቀስ እንቁላል በእግሩ ይሄዳል።"), voice Kore, model gemini-3.8-flash-tts, saved as outputs/experiments/tts_amharic_test.wav.
- **Result:** HTTP 200 in 3.6 s, 2.95 s of 24 kHz audio. I (a native listener) judged the pronunciation "perfect". Decision: narrate in Amharic, burn in English subtitles. See the E1 line in runs.jsonl.
- **Caveat:** one short sentence only; longer lines and the second (mother) voice are untested until the narration stage runs on the full storyboard.

## E2: a reference image keeps the girl consistent better than text alone (FLUX.2 klein 4B)
- **Hypothesis:** passing the approved character sheet as `input_image_0` gives a more consistent girl than repeating the text description.
- **Change:** same shot (girl on a stool, burnt injera) generated twice on `@cf/black-forest-labs/flux-2-klein-4b`: once with the sheet as reference (9.2 s), once text-only (16.9 s). Images in outputs/experiments/.
- **Result:** the reference matched the sheet's face but drifted in style (lost paper texture, shawl turned into a white top, Western kitchen with sink and cabinets). Text-only kept the style, shawl and mood. One pair is weak evidence, so I used text-only as the default and left reference mode behind the `KEYFRAME_REF` env var. Not yet tested across all shots.

## E3: separating characters from setting and a per-shot cast list improves keyframes
- **Hypothesis:** one combined `character` string put the mother into girl-only shots and gave a Western-looking kitchen; separate `characters`, `setting` and per-shot `cast` fixes that, and a precise setting fixes "injera looks like a tortilla".
- **Change:** schema now has `characters`, `setting` and shot `cast`; setting says mud walls, clay griddle, no cabinets or sink, and describes injera (large, spongy, grey-beige, bubble eyes).
- **Result:** all 8 keyframes in about 95 s (10-16 s each). Setting consistent across all 8, injera reads as injera, girl recognisable in 6 of 6 shots she appears in. Mother was inconsistent (see F3), fixed in E4.

## E4: caching regenerates only the shots whose prompt changed
- **Hypothesis:** editing the mother's description should regenerate only the 3 shots with her in the cast.
- **Change:** tightened the `mother` text and the s04 prompt, re-ran `make keyframes`.
- **Result:** s01, s02, s03, s06, s07 cached; s04, s05, s08 regenerated (12-13 s each, 3 new lines in runs.jsonl). Mother now wears the same white embroidered dress and headscarf in all three, and s04 no longer shows a face.

## E5: Ken Burns on stills is fast enough to be the default moving shot
- **Hypothesis:** FFmpeg `zoompan` on the 1024 px keyframes renders all shots in both aspect ratios in well under a minute on a Mac, with no GPU.
- **Change:** `pipeline/shots.py` renders each shot at 1920x1080 and 1080x1920 (8 s, 25 fps, zoom to 1.25x or a pan). First run crashed (crop wider than the scaled square); fixed by scaling to cover the target box first.
- **Result:** 16 clips in 19 s wall time (about 79 s CPU). First full assemble (subtitle overlays, end card, ducking, loudnorm) took 53 s for both exports. Measured loudness -17.4 LUFS integrated, LRA 6.2 LU, against a -16 target. Caveat: the square keyframe loses about 44% of its height in 16:9, which cuts the top of the girl's head in s02.

## E6: Three ACE-Step 1.5 score candidates, one chosen
- **Hypothesis:** the same brief ("warm, hopeful, slow, no vocals") with three different instrument palettes gives clearly different scores, and one of them will sit under quiet Amharic narration without competing with it.
- **Change:** `notebooks/acestep_kaggle.ipynb` on a Kaggle T4: turbo DiT + 0.6B LM, 8 steps, shift 3.0, 72 s each. A = plucked guitar and hand percussion; B = gentle piano with a string pad; C = kalimba and marimba with a drone. Seeds 101 / 202 / 303.
- **Result:** all three generated first time after the F6 fix. 37-42 s per candidate (about 0.65 GPU-minutes each), 61 s model load, $0. I chose **B (piano + strings)**. Reason (mine): B goes with the theme, a patient, quiet piece for a story about going slowly. Reason (measured, added later): B has the lowest spectral centroid of the three (mean 1.17 kHz against 1.59 kHz for A and 1.57 kHz for C), so it puts less energy in the 1.5-4 kHz band where speech intelligibility sits and masks the voice least; its loudness range is also the widest (10.6 LU against 5.3 and 6.6), so it has quiet passages. All three measure about -15 LUFS before mixing. I did not run a listening test on the candidates themselves. Final mix with B under narration measures -15.9 LUFS integrated, 68 s, both exports.
- **Caveat:** one seed per palette, so the comparison is between palettes and not between seeds.


## E7: how hard should the voice push the score down? (sidechaincompress threshold)
- **Hypothesis:** the shipped threshold 0.03 (first guess, never tested) ducks the score by about 10 dB while the narrator speaks, and a lower threshold buys only a marginal extra drop.
- **Change:** `experiments/ducking.py` builds the voice-and-score graph from `assemble.py` with thresholds 0.015, 0.03 and 0.06 (ratio 8, attack 20 ms, release 400 ms fixed), then measures RMS of the score alone, with and without ducking, inside the narration windows and in the gaps. Run on the 61 s film with score B.
- **Result:**

| Threshold | Score drop while speaking | Voice above score while speaking | Score drop in gaps |
|---|---|---|---|
| 0.015 | 14.8 dB | 16.7 dB | 0.0 dB |
| **0.03 (shipped)** | **10.7 dB** | **12.6 dB** | 0.0 dB |
| 0.06 | 6.9 dB | 8.8 dB | 0.0 dB |

  The hypothesis held for 0.03 (10.7 dB) and failed on "marginal": halving the threshold gave 4 dB more ducking, which is not marginal, and doubling it lost nearly 4 dB. The score is untouched in gaps in all three, so ducking only acts under speech. The drop scales about 4 dB per halving of the threshold.
- **Decision:** keep 0.03 for now, pending a listening check of `outputs/experiments/ducking/listen_thr_*.wav` (voice plus ducked score at each setting; not committed, WAVs are git-ignored).
- **Limits:** the numbers describe how much the score drops, not how it sounds, and I did not measure "pumping". I also tried to measure recovery time after each line, but the result (0 to 0.06 s) is not reliable, because the narration clips end with trailing quiet and the compressor has already released by the end of the file. I do not rely on it.

## E8: does a delivery instruction fix the stiff pacing Test 1 reported?
- **Hypothesis:** putting a style instruction in front of the Amharic text ("say it warmly and naturally...") makes Gemini TTS deliver it faster, with shorter pauses and clear sentence endings, so the clip gets at least 10% shorter.
- **Change:** `experiments/delivery.py` sends the s05 proverb line (the line Test 1 singled out) with an English instruction prefix and compares it with the plain clip, using the same voice (Aoede). Two attempts, both on s05 only:
  1. A long instruction ("Read the following Amharic text warmly... finish every sentence clearly. Text: "): the clip was **19.4 s instead of 2.43 s**; the model read the instruction out loud.
  2. A short instruction ("Say warmly and naturally: "): **5.64 s instead of 2.43 s**. Silence detection shows speech from 0 to 2.1 s (the instruction spoken in English), a 0.7 s pause, then about 2.4 s of speech, which is the length of the proverb alone.
- **Result:** hypothesis refuted. With an Amharic line, this model reads the style instruction aloud, so it cannot be used as a hidden control. In attempt 2 the proverb itself took the same time as the plain clip (about 2.4 s), so the instruction did not speed it up either. I did not run the other 8 lines, to save free-tier quota. Caveat: this is from the clip timings and silence structure; I did not listen to attempt 2 to check what was said, and one line is a small sample.
- **What I did instead:** fixed the pauses in the storyboard (shorter shots, E-Test 1 change in DESIGN.md) and added the "she said" tag. Not tried: a separate system instruction field, or splitting a long line into two calls, because neither is documented for this TTS model.
- **Lesson:** a prompt trick that works for English TTS cannot be assumed to work for Amharic. Measure the clip length before generating a batch: a 19 s clip for a 2 s line showed the failure immediately.

## E9: Gemini vs Claude proofreading the Amharic narration (frontier comparison)
- **Hypothesis:** both models flag the same real problem in at least one line, and they disagree on at least one other point.
- **Change:** the same prompt (`experiments/results/proofread_prompt.txt`: the 9 narration lines plus their English meaning, "be conservative, mark ok unless there is a real problem") went to Gemini 3.5 Flash through the API (`experiments/proofread.py`) and to Claude (Sonnet 5.5) in the working session, answered without seeing Gemini's output. Raw results: `experiments/results/proofread_gemini.json` and `proofread_claude.md`.
- **Result:**
  - **Agreement:** both flagged the same line, s03, for the same word: "ተስፋ ቅርጣ" should be "ተስፋ ቆርጣ" (the idiom for giving up hope). That word is a typo in my own edited line.
  - **Disagreement:** Claude also flagged s07 (minor register: "ክብ እና" vs "ክብና") and noted s08 (the closing line uses "ተራመደ", the proverb uses "ይሄዳል"). Gemini marked both ok. Gemini also said s05 is "the exact traditional proverb"; Claude agreed with medium-high confidence.
  - **Counts:** Gemini 1 flag / 8 ok; Claude 1 firm flag, 1 minor, 1 note.
  - **Cost and latency:** Gemini 27.3 s, 555 prompt + 527 output + 1,161 thinking tokens, free tier ($0 paid). Claude: answered in-session, so no separate API call, latency or cost was logged; I do not claim a figure.
  - **Human rating:** the author (native speaker) rates each flag in the table below. _Pending._
- **Caveat:** neither model is a reliable judge of Amharic, and both flagged only what a reader could also see on the page; neither heard the audio. Agreement between two models is not proof. The value of the experiment is that two independent checks converged on a real error that I had missed.
- **Failed attempts:** the planned model (Gemini 3.8 Flash) returned HTTP 503 and read-timeouts for about 10 attempts, and so did 3.7 Flash. A direct probe showed 3.6 Flash also 503 and 3.5 Flash working but slow (16 s for "say OK"). I switched to 3.5 Flash, so the Gemini side used an older model than the pipeline's default. All failed attempts are in `runs.jsonl` (see F8).
