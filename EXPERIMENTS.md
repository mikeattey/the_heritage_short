# EXPERIMENTS
Format: **E#: hypothesis** -> change -> result (numbers from runs.jsonl where possible). Target ~10.

## E1: Gemini Flash TTS can narrate Amharic well enough for a native-speaker audience
- **Hypothesis:** The free Gemini TTS model handles Amharic script input, so I can narrate in my audience's language instead of English.
- **Change:** One call with the proverb in Amharic script ("ቀስ በቀስ እንቁላል በእግሩ ይሄዳል።"), voice Kore, model gemini-3.8-flash-tts, saved as outputs/experiments/tts_amharic_test.wav.
- **Result:** HTTP 200 in 3.6 s, 2.95 s of 24 kHz audio. I (a native listener) judged the pronunciation "perfect". Decision: narrate in Amharic, burn in English subtitles. See the E1 line in runs.jsonl.
- **Caveat:** one short sentence only; longer lines and the second (mother) voice are untested until the narration stage runs on the full storyboard.

## E2: TODO
