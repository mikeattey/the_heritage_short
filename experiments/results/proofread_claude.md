# E9, Claude side: proofread of the Amharic narration

from the same prompt as the Gemini side (`proofread_prompt.txt`), without seeing Gemini's answer. No API call was made, so there is no logged latency or cost for this side. **Caveat: my Amharic is weaker than my English; read these as hypotheses for a native speaker to rate, not corrections.**

| Shot | Verdict | Issue | Suggestion | Confidence |
|---|---|---|---|---|
| s01 | ok | none | none | medium |
| s02 | ok | none | none | medium |
| s03 | **flag** | "ተስፋ ቅርጣ" is not a form I recognise. The idiom for giving up hope is "ተስፋ መቁረጥ", so the converb should be "ቆርጣ". "ሁሉንም" ("all of it") in front of it also reads oddly. | ልጅቷ ተስፋ ቆርጣ ለመተው ፈለገች። | medium-high on "ቅርጣ" being a slip; low on the rest |
| s04 | ok | none | none | medium |
| s05 | ok | none. Matches the commonly cited form of the proverb. | none | medium-high |
| s06 | ok | none | none | low-medium |
| s07 | minor | "ክብ እና ለስላሳ" with a separate "እና" reads written and stiff; spoken Amharic usually joins it as "ክብና". | አንድ ማለዳ፣ እንጀራው ክብና ለስላሳ ሆኖ ወጣ። | low |
| s08 | note, not an error | The proverb uses "ይሄዳል" (walks), the closing line uses "ተራመደ" (stepped, strode). It reads as a deliberate echo, but a listener may expect the proverb's own verb. | none required; optional "ቀስ በቀስ፣ እንቁላሉ በእግሩ ሄደ።" | low |
| s09 | ok | "አለቻት" works as a closing tag after a quoted line. | none | medium |

Flags raised: 1 firm (s03), 1 minor (s07), 1 note (s08).
