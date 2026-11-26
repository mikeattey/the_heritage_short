# DESIGN

## Story and audience (decided before generating anything)
- **Proverb:** "ቀስ በቀስ እንቁላል በእግሩ ይሄዳል" (*Qes beqes enqulal be'egru yihedal*): "Slowly, slowly, an egg walks on its own legs." My mother says it. Wording to be confirmed with her.
- **The scene is imagined.** I do not remember a specific moment when she said it to me. The kitchen scene below is invented to carry the proverb. The proverb is real and from my family; the story around it is not a true memory. This is stated in the report and the public post.
- **Audience:** young Ethiopians (about 18-30), students and early-career people, at home or abroad, who are impatient with their own progress. They are my peers, so I can reach 3+ of them for both tests, and they will tell me honestly if it rings false.
- **Language:** English narration and subtitles (English is allowed by the brief).
- **Logline:** A girl learning to bake injera wants to quit after her first torn attempts, until her mother puts an egg in her palm and reminds her how slowly good things grow.
- **What the audience should feel at the end:** relief and permission to go slowly; small steady steps count as progress.
- **Characters:** the girl (about 12, main, one fixed design) and her mother (secondary). The mother is shown mostly partially (hands, shoulder, silhouette) and fully in at most two shots, to limit character-consistency risk. One place: the family kitchen.
- **Motif:** the egg, in the first and last shot.
- **Arc:** setup (first torn injera, discouragement) -> turn (mother places the egg in her hand, says the proverb) -> practice montage (weeks pass in one kitchen) -> landing (one perfect injera, egg back in the basket).
- **Why each shot exists:** see the `reason` field per shot in storyboard.json.

## User test 1: radio cut (narration over placeholder music on black)
- **Date / format:** 2026-11-26, `radio_cut.m4a` (64 s, Amharic narration, placeholder chord bed, black screen), sent as an audio file with the same 5 questions to everyone. **Testers so far: 1 of the 3 required; more answers to be added here.**
- **What they said (Abdulhafiz, 28, Amharic speaker, from the audience):**
  1. Story recalled correctly: a girl keeps ruining injera, nearly gives up, her mother tells her the egg proverb, shows a real egg, and she practises for weeks until she gets it right. He understood the metaphor.
  2. Lesson: don't give up, be consistent, continued practice makes perfect.
  3. Felt "caught at the moment" and eager to hear the ending.
  4. Delivery felt "a little bit unnatural": many long pauses between sentences, and some sentences seem to end without a verb, which was confusing, for example when the mother delivered the proverb.
  5. The two voices sound different. When the conversation starts it gets a bit confusing. The story is short, concise and to the point, but the long pauses between every speech make it feel longer.
- **What worked:** the story and the proverb's meaning landed without any picture, and the tester wanted to hear the ending.
- **What I changed because of it:**
  1. **Pauses.** Measured the gaps: narration filled only 2.4-6.4 s of each 8 s shot, so the radio cut had up to 5.6 s of silence, worst on the mother's proverb (2.4 s of speech in an 8 s shot). Shot durations are now 7, 7, 7, 7, 7, 8, 6, 7 s (was 8 each), and the end card is 5 s, so the film stays at 60 s or more. Only the shots whose duration changed re-rendered.
  2. **Who is speaking.** Nothing told the listener the mother had just spoken. Added a new 3 s shot after the proverb where the narrator says one word, "አለቻት" ("she said to her"), over a close-up of an egg in a child's open palm (no face). It closes the quote and gives the proverb a beat. It has id `s09` but sits fifth-to-last in the array: ids are labels and the array is the timeline, so the other shots kept their ids and cached files (only 1 keyframe and 1 voice call were made). The film is now 64 s.
  3. **Still open:** the proverb's delivery (tester: the verb seemed missing). The clip is not cut off (silence in its last 100 ms), so I will test a delivery instruction in E8 after the author listens to it.
- **What I did not change:** the story, the order of shots and the proverb itself. One tester is not enough to rewrite them.

## User test 2: near-final cut
- **Date / format:** 2026-11-26, the vertical MP4 (a few revisions before the final: it had the earlier 7-8 s shot timing and the original voice takes), same 8-9 questions as Test 1 plus picture, subtitle, music and cultural-fit questions. **Testers so far: 1 of the 3 required (Abdu, the same person who did Test 1); more answers to be added here.**
- **What they said (Abdu, 28):**
  1. About a mother teaching her daughter consistency through an Ethiopian proverb.
  2. The moment that stayed: the daughter's delighted look when her persistence pays off; it matched the feeling of success after repeated failures.
  3. Subtitles: "correct and perfectly displayed, it really helped".
  4. Music: "just right and consistent throughout".
  5. Believable and respectful? Yes, but "the injera doesn't resemble an actual injera".
  6. Pace: "a little slow, which is tolerable because the sound is soothing".
  7. Compared with the audio-only version: "this version is cleaner than the previous one".
  8. Would share it: yes, "concise video with good story telling, trying to teach an important lesson in life".
  9. OK to use his first name: yes.
- **What worked:** the story landed from the pictures as well as the audio, the subtitles, the music level and the ending all passed, and the tester said this cut was cleaner than the audio-only one, which is some evidence that the Test 1 changes (shorter pauses, the "she said" tag) helped. Caveat: one tester, who had also done Test 1.
- **What I changed because of it:**
  1. **The injera.** The generated injera had a few large round holes, like a cheese or a pancake, not the dense fine pinholes of real injera. I rewrote the keyframe prompt of the five shots where it appears (s02, s03, s06, s07, s08) to ask for "hundreds of tiny pinhole eyes in a fine honeycomb texture, not a few large holes". Only those five keyframes were regenerated (the other four stayed cached); the new injera has many more, smaller holes but is still not perfect. The new images also redrew the girl a little in those shots, and the crop focus of s02 was retuned (0.3 to 0.2) to keep her head in frame.
  2. **Pace.** Not changed further: the tester found it tolerable and soothing, and the film is already shortened to 61 s.
- **Not done:** the version he watched was older than the current one, so his answers do not cover the final s09 "she said" voice take or the crop changes.

