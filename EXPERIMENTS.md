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

