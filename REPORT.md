# Report: The Heritage Short

**Qes Beqes (Slowly, Slowly)**: a 61-second illustrated AI short film in Amharic, with English subtitles, and the pipeline that regenerates it from one file.

Links: film 9:16 (main) https://drive.google.com/file/d/1CASDdT_FSDUUt68cJ-5-_LMv-yN9P15m/view?usp=sharing · film 16:9 https://drive.google.com/file/d/1WaKvpfehkFj9Wpj2h1SKCZ-nH4c31O_P/view?usp=sharing · repo https://github.com/mikeattey/the_heritage_short · the walkthrough video and the public post are linked in the Assignment 2 submission

## 1. What I made, and for whom

A girl in an Ethiopian kitchen keeps tearing her injera and wants to quit. Her mother puts an egg in her hand and says a proverb my own mother says: *ቀስ በቀስ እንቁላል በእግሩ ይሄዳል*, "slowly, slowly, an egg walks on its own legs." Weeks pass, and the injera comes out round and soft. The scene is imagined; the proverb is real and from my family, and my mother agreed to its use (ETHICS.md).

It is for **young Ethiopians, about 18 to 30**, at home or abroad, who are impatient with their own progress. They are my peers, so I could reach them for both tests. The feeling I aimed for was permission to go slowly: small steady steps count.

Everything is illustrated, and the voice is synthetic, so no real person's face or voice appears. The end card says "Made with AI".

The deliverable is also a **pipeline**: `storyboard.json` is the single input, validated by a JSON Schema before every stage, and `make film` produces both aspect ratios. Every output file is named by a hash of its inputs, so editing one shot regenerates only that shot (shown in the walkthrough, and checked on a fresh clone: no model call was made for unchanged shots).

## 2. What the audience taught me

Two testers heard an audio-only cut first and one watched a near-final film (DESIGN.md has every answer). Both testers of the audio cut remembered the lesson, so the story and the proverb work. What they challenged was delivery:

- **Pauses.** Both said the pauses were too long. I measured it: the narration filled 2.4 to 6.4 s of each 8 s shot, up to 5.6 s of silence around the proverb. I shortened the shots (the film went from 68 s to 61 s).
- **Who is speaking.** Both were unsure when the mother starts. I added a one-word narrator tag, "አለቻት" ("she said"), after the proverb.
- **The injera.** The viewer of the near-final cut said the injera did not look like injera. I had not noticed: the model drew a few large holes, like cheese. I rewrote five prompts for finer pinholes, which helped but is not perfect.
- **Wording.** One tester said "ተቀደደ" is not what one says for a torn injera ("ተበጣጠሰ" is better). Both AI proofreaders had passed that line. I left it as a known issue.

The strongest lesson: **native listeners caught things neither AI proofreader did**, and the audience gave me measurable complaints, not taste.

Limit: I reached 2 of the 3 required testers in Test 1 and only 1 in Test 2 (the same person as in Test 1) before the deadline. The counts above are the real ones, and DESIGN.md records every answer.

## 3. The hardest problem: the Amharic voice

Almost every technical failure was about the voice (FAILURES.md):

- the free tier rate limit (F1) and then a **10 requests per day** limit I only saw after hitting it (F9);
- Gemini returning a full WAV that I treated as raw audio, which put a click and noise on every clip's end (F2);
- a delivery instruction that the model **read aloud** (E8);
- seeds that do not repeat (E10), and a one-word clip that sounded like a different voice (re-rolled by hand).

I solved it by measuring (silence detection, spectral checks), a `narration_take` field to re-roll a clip, and **committing the chosen clips** so that reproducing the film never depends on a quota or a random seed. Not solved: pronunciation and naturalness I cannot judge from numbers, so some of it still rests on one native listener.

## 4. A practice that beat my instinct, and one that did not

**Beat my instinct: test the audio on its own first (the radio cut).** I wanted to perfect the pictures. The radio cut, narration on a black screen, exposed the long pauses and the unclear speaker before any picture work was spent on them, and I could measure them.

**Did not work: a delivery prompt for the TTS (E8), and a seed for repeatability (E10).** Both are "obvious" tricks from English TTS. For Amharic the model spoke the instruction aloud, and the same seed gave different audio. The fix was committing outputs, not controlling the model. A related miss: AI proofreading (E9) found a real typo (ቅርጣ for ቆርጣ) but passed a line a native speaker flagged.

## 5. Engineering, measurement and cost

- 173 logged calls in `runs.jsonl`, including 17 failed attempts (retries are logged with the error type, never the message).
- **Cost paid: $0.** List-price equivalent about $0.04 (keyframes at Cloudflare's per-tile rate, narration at an unverified Gemini preview price). Kaggle: 1.95 GPU-minutes for three ACE-Step candidates.
- 11 experiments with hypotheses (some refuted: E8, half of E10, half of E7), 10 failures written up (F1 to F10), including a cache bug I only found by looking at frames (F10).
- Licences checked from model cards and terms (ETHICS.md): FLUX.2 klein 4B and Wan 2.2 Apache-2.0, ACE-Step MIT; on the free Gemini tier Google may use prompts, which here contained only a fictional story.

## 6. Ceiling work

The extra language: **Amharic narration** with English subtitles. Smaller extras: a per-shot crop focus to keep heads in frame in both aspect ratios (E11), and a re-roll field for a voice. Not done: the Wan 2.2 hero shots, because a free Kaggle GPU run could fail with no time to recover.

## 7. What I would do next

1. Have a **native Amharic reviewer** read every line before regenerating the voice (the ተቀደደ wording, the proverb delivery).
2. Run both tests with 3 or more people each, with different people in each round.
3. Draw the injera better (reference images or a LoRA) and keep the girl consistent across shots with a reference image.
4. Try a Wan 2.2 hero shot for the moment the injera works.
5. Move narration to a paid quota so a re-roll does not depend on a daily limit.

## 8. AI use

Claude Code helped write the pipeline, notebooks and documents in this repo; Gemini TTS, FLUX.2 klein 4B (Cloudflare) and ACE-Step 1.5 made the voice, images and score. I made the story choices, the proverb, the Amharic lines and corrections, and every decision about what to change after testing.
