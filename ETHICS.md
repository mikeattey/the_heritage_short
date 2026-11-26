# ETHICS
## Consent record
- **No real person's face or voice appears in the film.** Visuals are illustrated with FLUX; prompts never name or describe a real person's likeness. Narration is a synthetic Gemini TTS voice; no real person's voice is recorded or cloned.
- **The characters are fictional.** The girl and the mother are invented illustrated characters, not portraits of my family members.
- **The proverb is real**, from my family (my mother says it). It is a traditional Amharic proverb in common use. I mention my mother only as its source and have no recording of her. TODO: tell her the proverb is used in this film and record the date and how she agreed.
- **The scene is imagined**, not a true family memory, and is labelled that way in the report and the public post.
- **User-test participants** are viewers only; only first names or initials appear in DESIGN.md, with their agreement.

## Licences
Checked 2026-11-26 against the primary pages linked below (model cards and terms, not blogs). I am not a lawyer; this is my reading for a non-commercial student film.

| Model / asset | Licence | Commercial use | What it means for this film |
|---|---|---|---|
| FLUX.2 [klein] 4B (keyframes, via Cloudflare Workers AI) | Apache-2.0 per the [model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B). The 9B variant is non-commercial, so the 4B ID matters. | yes (weights) | Neither the model card nor the [Cloudflare page](https://developers.cloudflare.com/workers-ai/models/flux-2-klein-4b/) says who owns outputs. The card's out-of-scope list bans unlawful, deceptive or harmful content, non-consensual imagery and personal-information misuse; none applies to an illustrated family story. The Cloudflare page defers to BFL's terms of service, which I did not read. |
| Gemini 3.8 Flash TTS (narration) | [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms) (effective 2026-03-23) | per terms | "Google won't claim ownership" of generated content, and I am responsible for how I use it. On the **free (unpaid) tier Google may use prompts and outputs to improve its products, and human reviewers may read them**. Only the narration text was sent: a fictional story and a traditional proverb, no personal data, no real voice. Not for competing-model training. The terms page has no statement on watermarking or labelling, so the "Made with AI" card is my own choice. |
| Wan 2.2 TI2V-5B (optional hero shots) | Apache-2.0 per the [model card](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B) and [LICENSE.txt](https://github.com/Wan-Video/Wan2.2/blob/main/LICENSE.txt) | yes | The README says "We claim no rights over the your generated contents" and adds conduct rules (no unlawful, harmful or misleading content). **Not used in the final film so far**; recorded in case a hero shot is added. |
| ACE-Step 1.5 turbo + 0.6B LM (score) | MIT (model card and README; the weights repo has no separate licence file) | yes | The score was generated on Kaggle, and candidate B is committed as `assets/score_source.flac`. |
| FFmpeg (Homebrew build) | LGPL/GPL, depending on build | n/a | Used as a command-line tool; no FFmpeg code is shipped in this repo. |
| Pillow, jsonschema, requests | HPND, MIT, Apache-2.0 | yes | Python dependencies, installed by `make setup`. |
| System fonts (Helvetica, Kefa) | Apple system licence | n/a | Used only to render subtitles and the end card on my own Mac. Fonts are not redistributed in the repo. |

Open point: no output ownership is stated for FLUX, and Google states it will not claim ownership of Gemini output. I make no claim to copyright over the AI-generated images, voice or score, and the repo's own code is the part I release. A licence file for the repo's code is still to add.

## Labelling plan
End card "Made with AI" in both exports; platform AI label switched on in the public post; this repo documents every model used.
