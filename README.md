# The Heritage Short
AI-generated 60–90 s illustrated short film and the pipeline that makes it.

## Run
```
brew install ffmpeg
cp .env.example .env   # add GEMINI_API_KEY, CF_ACCOUNT_ID, CF_API_TOKEN (never commit)
make setup
make film              # validate -> keyframes -> shots -> music -> narration -> assemble
```
Outputs: `outputs/final/heritage_short_9x16.mp4`, `heritage_short_16x9.mp4`.
Change one prompt/narration line in `storyboard.json` and re-run `make film`: only that shot regenerates (see runs.jsonl).

Music needs a chosen ACE-Step candidate in `outputs/music/` (see ARCHITECTURE.md). TODO: costs, links, film.
