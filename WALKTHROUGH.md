# Walkthrough script (5 minutes maximum)

Record your screen and your voice. Target 4:30 so there is room to spare. The one thing the grading needs to see is **a storyboard line changed and only that shot regenerating**, so that is the centre of the video (section 4).

## Before you record (10 minutes, not on camera)
1. Open a terminal in the repo. Run `make film` once. Every keyframe and narration line must print `cached`. This proves the starting state.
2. Close `.env` and any tab showing keys. Never show it.
3. Open these in tabs, ready: `storyboard.json`, `runs.jsonl`, `outputs/keyframes/` (Finder, sorted by date), the final 9:16 film, `DESIGN.md`, `EXPERIMENTS.md`.
4. Increase the terminal font size so it reads on a phone.
5. Rehearse section 4 once, then undo it with `git checkout storyboard.json && make film` (everything prints `cached` again, because the old keyframe is still on disk).
6. Use an **image prompt** for the demo, not a narration line. The free Gemini TTS key allows only 10 requests per day, and Cloudflare has plenty.

## The script

### 1. What it is (0:00 to 0:35)
**Show:** the film playing for about 10 seconds, then the repo on GitHub.
**Say:** "This is The Heritage Short, a 61-second illustrated film in Amharic with English subtitles. A girl keeps tearing her injera, and her mother gives her a proverb: slowly, slowly, an egg walks on its own legs. It's made for young Ethiopians who are impatient with their own progress. Every image, the voice and the music are AI-made, and the end card says so. The scene is imagined and nobody's real face or voice is used. The rest of this video is the pipeline that makes it."

### 2. One file drives everything (0:35 to 1:20)
**Show:** `storyboard.json` (scroll through one shot), then `schema/storyboard.schema.json`.
**Say:** "Everything starts from storyboard.json: the story, one prompt per shot, the Amharic narration and the English subtitle. Every stage first validates it against a JSON Schema."
**Do:** in the terminal run `make validate` (prints OK). Then change `"duration": 7` in one shot to `"duration": 1`, run `make validate` again and show it failing with a clear message, then undo with `git checkout storyboard.json`.
**Say:** "A mistake stops here, before any paid model call."

### 3. Stages, hashes and caching (1:20 to 2:00)
**Show:** the stage table in the README, then Finder at `outputs/keyframes/`.
**Say:** "Five stages: keyframes with FLUX on Cloudflare, Ken Burns shots in FFmpeg, music from ACE-Step on Kaggle, narration with Gemini TTS, and the FFmpeg assembly with ducking, subtitles and loudness. Each file is named by a hash of its inputs, so s04 underscore a hash. If the inputs don't change, the hash doesn't change, and the stage skips the call."

### 4. The demo: change one line, one shot regenerates (2:00 to 3:35)  <- the graded part
**Do, on camera, in order:**
1. In `storyboard.json`, shot `s04`, add to the end of `keyframe_prompt`: `, warm golden afternoon light`. Save.
2. Run `make film`.
3. While it runs, say: "I changed one prompt in one shot. Watch the output."
4. Point at the terminal: s04 prints **generated**, and the other eight print **cached**. Then the shots stage re-renders only s04, in both aspect ratios.
5. Open `runs.jsonl` at the bottom (or `tail -n 5 runs.jsonl`): there is **one new keyframes line** for s04 with its model, parameters, latency and cost.
6. Open `outputs/keyframes/` in Finder: **a second s04 file with a new hash**, next to the old one, and no new files for the other shots.
7. Open the new image and the old one side by side.
**Say:** "One prompt, one call, one new file. Nothing else was regenerated. That's about 12 seconds and a fraction of a cent, instead of regenerating all nine images."
**Then undo:** `git checkout storyboard.json && make film`. Everything prints cached, and the original film is back, because the old keyframe was never deleted.

If the Cloudflare call is slow or fails and retries, keep recording: the retry shows up in `runs.jsonl` as a line with `"success": false`, which is evidence for the failure handling.

### 5. Result and evidence (3:35 to 4:20)
**Show:** the final 9:16 film for about 15 seconds, then `COSTS.md` and `EXPERIMENTS.md` headings.
**Say:** "Two exports, 9:16 and 16:9, with the score ducked under the voice and normalised to minus 16 LUFS. Every model call is logged in runs.jsonl. I ran 11 experiments with hypotheses, and several failed: for example a delivery instruction that the Amharic voice read out loud. Ten failures are written up. Cost paid was zero dollars, about four cents at list price."

### 6. The audience and what changed (4:20 to 4:50)
**Show:** the Test 1 and Test 2 sections of `DESIGN.md`.
**Say:** "Testers said the pauses were too long, and that it wasn't clear who was speaking. I shortened the shots and added a narrator tag, 'she said'. One tester said the injera didn't look like injera, so I rewrote five prompts. Only two testers answered each round, which I state in the report."

### 7. Close (4:50 to 5:00)
**Say:** "Clone the repo, add your keys, run make film, and you get this film. The repo, the report and the film links are in the description."

## Checklist before you upload
- [ ] The video shows a storyboard line changed and **only that shot regenerating** (section 4).
- [ ] Under 5 minutes.
- [ ] No keys or `.env` visible.
- [ ] Google Drive link set to "Anyone with the link can view" and opened in a private window to confirm it works without login.
