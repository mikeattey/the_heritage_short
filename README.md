# The Heritage Short

**Qes Beqes (Slowly, Slowly)** is a 68-second illustrated short film made with AI. A girl in an Ethiopian kitchen keeps tearing her injera, and her mother answers with a proverb: *slowly, slowly, the egg learned to walk.* The narration is in Amharic with burned-in English subtitles, over an original AI-generated score. The scene is imagined, and every image, voice and note is synthetic.

It is made for young Ethiopians who are impatient with learning. This repo is the pipeline that makes it, so you can regenerate the whole film from one file, [storyboard.json](storyboard.json).

- Film (9:16 and 16:9), walkthrough and public post: _links to be added at submission_
- Made with AI. Every model, its licence and its cost are documented below.

## Quick start

You need Python 3.10+, FFmpeg, and two free accounts (Google AI Studio and Cloudflare). No GPU is needed locally.

```
git clone https://github.com/mikeattey/the_heritage_short.git
cd the_heritage_short
brew install ffmpeg            # or your package manager
cp .env.example .env           # then fill in the keys, see below
make setup                     # creates .venv and installs requirements
make smoke                     # checks tools and keys, prints names only, never secrets
make film
```

Outputs land in `outputs/final/`:
- `heritage_short_9x16.mp4` (vertical, main)
- `heritage_short_16x9.mp4` (widescreen)
- `subtitles_en.srt`

### Keys (`.env`, git-ignored)

| Variable | What it is | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | narration (Gemini TTS) | Google AI Studio, free tier |
| `CF_ACCOUNT_ID`, `CF_API_TOKEN` | keyframes (FLUX on Workers AI) | Cloudflare dashboard, token with Workers AI permission |
| `GEMINI_TTS_MODEL`, `GEMINI_TTS_VOICE`, `GEMINI_TTS_VOICE_MOTHER`, `CF_IMAGE_MODEL`, `GEMINI_TEXT_MODEL` | model IDs and voices, already filled in `.env.example` | change here if a model is renamed |

`.env` is never committed. Model IDs live in `.env`, not in code.

## How it works

```
storyboard.json  --validate-->  keyframes -> shots -> music -> narration -> assemble  -->  outputs/final/
```

| Stage | Command | What it does | Model |
|---|---|---|---|
| validate | `make validate` | checks `storyboard.json` against `schema/storyboard.schema.json` | none |
| keyframes | `make keyframes` | one still per shot | FLUX.2 klein 4B on Cloudflare Workers AI |
| shots | `make shots` | slow zoom or pan on each still, in both aspect ratios | FFmpeg `zoompan` (local) |
| music | `make music` | trims and fades the chosen score to the film length | ACE-Step 1.5 (generated on Kaggle, committed in `assets/`) |
| narration | `make narration` | one clip per line, narrator and mother voices | Gemini 3.8 Flash TTS |
| assemble | `make assemble` | places narration, ducks the score under it, burns subtitles, adds the end card, normalises loudness to -16 LUFS | FFmpeg (local) |

`make film` runs them all in order. Each stage validates the storyboard first, so a typo fails early.

### Change one shot, regenerate only that shot

Every output file is named by a hash of its inputs (`s03_<hash>.png`). Edit one prompt or one narration line in `storyboard.json` and run `make film` again: only that shot's hash changes, so only that shot's model call runs. Everything else prints `cached`.

Try it:
1. Edit the `narration` of shot `s03`.
2. Run `make film`.
3. `tail runs.jsonl` shows one new narration line for `s03` and nothing for the other shots.

### Logs

Every model call appends one line to `runs.jsonl` (stage, model, parameters, seed, latency, cost). Local FFmpeg steps are logged with `"local": true`. The Kaggle music runs were added by hand from the notebook's own log.

## Repo map

| Path | Purpose |
|---|---|
| `storyboard.json` | the single source of truth: story, prompts, narration, subtitles, music brief |
| `schema/` | JSON Schema for the storyboard |
| `pipeline/` | one module per stage, plus `common.py` (hashing, retries, logging) |
| `notebooks/acestep_kaggle.ipynb` | generates three score candidates on a free Kaggle GPU |
| `assets/score_source.flac` | the chosen score (candidate B), committed so a clean clone can run `make film` |
| `outputs/keyframes/` | the generated stills (committed as evidence; audio and video are git-ignored) |
| `runs.jsonl` | one line per model call |
| [DESIGN.md](DESIGN.md) | audience, story, user tests and what they changed |
| [EXPERIMENTS.md](EXPERIMENTS.md) | hypothesis, change, result for each experiment |
| [FAILURES.md](FAILURES.md) | what broke and how it was fixed |
| [COSTS.md](COSTS.md) | latency, GPU minutes and list-price equivalents |
| [ETHICS.md](ETHICS.md) | consent record, licences and labelling |
| [ARCHITECTURE.md](ARCHITECTURE.md) | contracts, caching and failure handling |

## Optional steps

- **Radio cut** (narration over placeholder music on black, used for user test 1): `.venv/bin/python -m pipeline.radiocut`
- **Draft a storyboard with Gemini:** `.venv/bin/python -m pipeline.script`. This is a drafting aid, and the committed `storyboard.json` was edited by hand.
- **New score:** run `notebooks/acestep_kaggle.ipynb` on Kaggle (GPU, Internet on), put the chosen file in `assets/`, and set `music.chosen` in `storyboard.json`.

## Known limits

- Subtitle and end-card text is drawn with Pillow using macOS system fonts (Helvetica, Kefa for Ethiopic script). On Linux or Windows, change the two font paths at the top of `pipeline/textimg.py`. Homebrew's FFmpeg has no `drawtext` or `subtitles` filter, which is why text is drawn this way (see FAILURES.md F4).
- Keyframes are square and cropped per aspect ratio, so the 16:9 crop can cut the top of a character's head.
- Characters are kept consistent by detailed text descriptions, not by a fixed reference image, so small differences between shots remain.
- Gemini TTS on the free tier allows **3 requests per minute and 10 per day** (per project, `gemini-3.8-flash-tts`, observed 2026-11-26). A full narration run is 9 clips, so it nearly uses a day's allowance. The final clips are committed in `outputs/narration/`, so `make film` on a fresh clone makes no TTS calls; change a line and exactly one call is made. The pipeline retries with backoff on the per-minute limit, but a daily-limit 429 only clears the next day (use a second API key or wait).
- Amharic narration was proofread by a native speaker (the author) and has not been checked by a professional translator.

## AI use and licences

Everything in the film is AI-generated or synthetic: no real person's face or voice appears, and the characters are invented. The end card reads "Made with AI". Licences for each model are listed in [ETHICS.md](ETHICS.md). The pipeline code is MIT-licensed (see [LICENSE](LICENSE)).
