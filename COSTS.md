# COSTS

Everything was built on free tiers, so the money paid is **$0.00**. The "list-price equivalent" column estimates what the same calls would cost at published paid rates. All counts and latencies come from [runs.jsonl](runs.jsonl) (totals as of 2026-11-26, including experiments and re-runs).

## Measured per stage

| Stage | Model | Calls logged | Total latency | Per call | GPU min | List-price equivalent |
|---|---|---|---|---|---|---|
| keyframes | FLUX.2 klein 4B (Cloudflare Workers AI) | 14 | 170 s | 12 s | none (remote) | about $0.016 |
| narration | Gemini 3.8 Flash TTS | 9 | 55 s | 6 s | none (remote) | about $0.01 |
| music | ACE-Step 1.5 turbo + 0.6B LM (Kaggle T4) | 3 | 117 s | 39 s (plus 61 s model load once) | 1.95 | $0 (free Kaggle quota) |
| shots | FFmpeg Ken Burns (local) | 16 | 19 s | 1.2 s | none | $0 |
| assemble | FFmpeg (local) | 6 | 124 s | 21 s per export | none | $0 |
| music trim, radio cut | FFmpeg (local) | 3 | 16 s | n/a | none | $0 |

One full from-scratch run of the pipeline for the final storyboard is 8 keyframes, 8 narration clips, 16 Ken Burns clips and 2 assemblies. That is about 145 s of API latency (8 x 12 s keyframes + 8 x 6 s narration), 19 s of shots and about 45 s of assembly. The 14 keyframe calls and 9 narration calls above are higher than 8 each because they include regenerations during experiments E2, E3 and E4 and the mother-consistency fix (F3).

Not captured in `runs.jsonl`:
- **Kaggle session time:** install (`uv sync`) and about 10 GB of weight downloads took most of the roughly 20-40 minutes the notebook was open. Only generation and model-load time are logged.
- **Failed and retried calls:** retries (for example the Gemini 429s in F1) are printed to the terminal but not written to `runs.jsonl`. The counts above are successful calls.
- **My time:** roughly the full working day, spread across setup, prompt iteration, listening and testing.

## How the list-price equivalents were worked out

- **Keyframes.** Cloudflare lists $0.000287 per output 512x512 tile for `flux-2-klein-4b` ([model page](https://developers.cloudflare.com/workers-ai/models/flux-2-klein-4b/), [pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)). A 1024x1024 image is 4 tiles, so $0.00115 per image. 14 images is $0.016. Reference-image experiments add input tiles ($0.000059 each), which I did not count.
- **Narration.** The only price I found for Gemini 3.8 Flash TTS was a third-party-looking listing of $9.00 per 1M audio output tokens, at 25 audio tokens per second. That gives $0.000225 per second of speech. The 8 final clips total 36 s, and about 40 s were generated including one re-run, so about $0.009. **This rate is unverified against an official Google page** and the preview price may change after 2026-12-31, so treat it as an order of magnitude.
- **Music.** Kaggle's free GPU quota was used. A rented T4 at typical cloud rates would be well under a dollar for 2 GPU-minutes. I haven't pinned a figure for this and won't claim one.

## Free-tier limits that shaped the design

| Service | Limit met | What I did |
|---|---|---|
| Gemini TTS (free) | HTTP 429 after about 5 requests in a minute (F1) | exponential backoff, 6 tries from 3 s; clips cached so a re-run only asks for missing lines |
| Cloudflare Workers AI | 10,000 free Neurons per day, per Cloudflare's pricing page | 8 keyframes per full run is well within it; I did not hit the cap |
| Kaggle GPU | weekly GPU quota, Internet must be switched on | three candidates in one session, loaded the model once |

## What the caching saves

Changing one shot's narration regenerates 1 narration clip and its subtitle, not 8 (E4). For a single-shot prompt change that is 1 keyframe call (about 12 s, $0.001) instead of 8 (about 100 s, $0.009), roughly 8x less.

## Frontier-model comparison

TODO: one Amharic proofread (the same narration lines through Claude and through Gemini) with a note on cost and quality. Planned as experiment E10 if time allows.
