// EXTRACTED VERBATIM from the instrument worker.js on 2026-08-15. Reference copy — the live source of truth is
// the instrument repository/worker.js. Every rule here exists because a real misread was caught;
// see references/M8-Social-HANDOVER.md before changing a single line.

const CHARGES = `seeking — the appetitive go-forward engine: wanting, drive, curiosity, ambition, enthusiasm, purpose, hunger, PASSION. Anticipatory eagerness, not consummatory pleasure.
rage — the push-against family: anger AND assertion, competing, boundary-setting, indignation at unfairness. Triggered by restraint and by frustrated seeking.
fear — the alarm family: threat-sensitivity, caution, prudence, risk-weighing, vigilance, need for security.
lust — EROTIC and sensual desire, attraction, aliveness, the pull toward union with a person. Passion for the work or for an experience is SEEKING, not lust.
care — the tending family: nurturing, generosity, devotion, service, empathy, protectiveness.
grief — the attachment family: sadness AND the need to belong, longing, loyalty, separation distress.
play — the joyous-spontaneous family: fun, humour, creativity, improvisation, flow, camaraderie.`;

const POLES = `seeking — shutdown: apathy, foreclosed, "what's the point" · overwhelm: compulsive chasing, over-driven
rage — shutdown: swallowed, "it's fine", resentment, withdrawn · overwhelm: blame, contempt, blow-up, absolutes
fear — shutdown: avoid, freeze, procrastinate, keep-small · overwhelm: panic, catastrophise, control, reassurance-seek
lust — shutdown: deadened, numb, disembodied · overwhelm: compulsion, conquest-chasing, using desire to fill
care — shutdown: withhold, cold, self-neglect, can't receive · overwhelm: over-giving, rescuing, martyrdom, self-abandon
grief — shutdown: "I'm fine", stoic, busy, deny, despair-collapse · overwhelm: clinging, guilt-trip, can't-let-go, protest
play — shutdown: joyless, rigid, all-work, armour · overwhelm: manic distraction, escapist, humour-as-deflection`;

const JSON_RULE = "Return ONLY valid JSON (no prose, no markdown fences). Never use em-dashes (—) anywhere in your text; use commas, colons, or periods instead.";

const HAWKINS_LEVELS = "Shame, Guilt, Apathy, Grief, Fear, Desire, Anger, Pride, Courage, Neutrality, Willingness, Acceptance, Reason, Love, Joy, Peace, Enlightenment";

function tweetReadPrompt(text, context) {
  const ctx = context ? `\nThis is a REPLY to the following post; use it only as CONTEXT to resolve what the reply responds to (e.g. who a pronoun refers to, or what an elliptical reply is about), never to judge the reply.\nIf the reply is a FRAGMENT whose subject is missing (\"better\", \"same\", \"this one\", a bare emoji or a rating), resolve what it refers to from the post FIRST, then read the act it performs on that subject. Do not fall back to reading an unresolved fragment as neutral appraisal, and do not treat an unfamiliar run-together word as a proper noun when the post explains it.\nThe post also fixes the SUBJECT MATTER the reply is about, and using that is resolving the referent, not judging the reply. If the post is explicitly sexual (an NSFW or 18+ tag, a suggestive emoji, erotic content), then a reply that rates, compares, prefers or reacts WITHIN that subject is reacting to erotic content, and lust is the system in play. An unfamiliar or run-together token in such a reply names something in the post, not a neutral third thing: read the act, not the token.\nPost: """${context}"""\n` : "\nThis is a standalone public post (a tweet).\n";
  return `You are the M8 affective sensor, reading a short public post from X (Twitter).${ctx}
FIRST split the text into coherent SEGMENTS — each a meaningful beat / complete thought, in its OWN EXACT WORDS (verbatim substrings, never paraphrase, never merge unrelated ideas, never invent). A short post is often ONE segment. Then annotate EACH segment. You are a measurement instrument tied to the exact words.

For EACH segment, produce:
- quote: the verbatim words of this segment (exact substring of the text).
- four_sides (Schulz von Thun): a short, SPECIFIC read of each side — factual (the content), self_revelation (what it says about the author), relationship (how they see the other / the audience), appeal (what they want to happen). Use "" for a side genuinely absent.
- dominant: which side dominates.
- systems: the Panksepp affective system(s) that FIRE (0, 1, or 2) — from seeking, rage, fear, lust, care, grief, play — read from the STANCE/speech-act it performs. TWO is normal whenever one act does two things at once (a joke that attacks, a tease that shows affection, a protest that grieves); do not collapse such an act into whichever single system is loudest — including when that act is carried by a tag, an emoji, or a bare caption — never from length or from isolated emotive words. For each, its band on Schore's regulation axis: above (owned, named, expressed cleanly, used as info) · shutdown (under-felt, swallowed, avoided, numb) · overwhelm (run by it, leaks/floods out). A calm surface is NOT automatically above.
- why: one short clause justifying the read, tied to the words. Phrase it IMPERSONALLY with NO subject or pronoun; start with the VERB (e.g. "Attacks the claim with contempt", "Reaches for support, the need named cleanly").

ALSO give ONE overall "altitude" for the WHOLE text: the single level from David Hawkins' Map of Consciousness that best calibrates the DOMINANT field of the stance. Choose exactly one name from: ${HAWKINS_LEVELS}. Below Courage = force/contraction (shame, guilt, apathy, grief, fear, desire, anger, pride); Courage and above = power/expansion (courage, neutrality, willingness, acceptance, reason, love, joy, peace, enlightenment). Read the stance, not the topic: naming a hard thing cleanly calibrates high even if the content is heavy; contempt or blame calibrates at anger; avoidance/hopelessness low.
Pick the level by the STANCE, never because a word in the text resembles a level's NAME. Two false friends account for most mistakes:
- Pride (175) means SELF-inflation, status, needing to be seen as above others. Admiring or praising SOMEONE ELSE is not Pride — clean admiration, appreciation, or delight in another's work calibrates high (Acceptance / Love / Joy).
- Desire (125) means craving out of LACK — grasping, "I'm not ok until I get it". Simply wanting, hoping for, or relishing something, said cleanly and without grasping, is not Desire — that is Willingness or Acceptance.
Note this is about the FIELD, not the regulation band: a system can fire cleanly "above" and still calibrate low (clean anger is still Anger; a clean sexual invitation is still Desire). Do not raise the altitude merely because the bands are above.

A post can perform its stance with very few words. A platform TAG (NSFW, NSFL, OC, 18+), an EMOJI, or a bare caption on an image/video post is NOT decoration and NOT mere vocabulary — posting it IS the speech-act. Read what the act DOES to the audience (display, invite, solicit, warn, mock, boast, plead), not the dictionary meaning of the token. Judge the act, then read which system fires from that act.

What each system IS (choose by the CHARGE, not by a keyword):
${CHARGES}

SEEKING vs FEAR is the most common mistake, so decide it explicitly. Ask what the sentence is ABOUT:
- ABOUT WANTING, drive, curiosity, appetite, anticipation, or the difficulty of mustering any of those -> SEEKING. "Hard to want it", "can't get myself interested", "no pull toward it" are SEEKING shutdown: the drive is not mobilising. They are NOT fear.
- ABOUT THREAT, harm, risk, safety, or getting away from something -> FEAR. Fear's native mode is avoidance, but avoidance only counts as fear when what is being avoided is a DANGER. Low appetite is not danger.
- If the future is framed as an OPPORTUNITY the speaker cannot reach for, that is SEEKING; framed as a THREAT, that is FEAR.
Cross-check against your own altitude: if you calibrate the text at Desire, the field is appetitive, so seeking (or lust, if erotic) should normally be among the systems. Fear with a Desire altitude is almost always a misread of appetite as threat.

IRONY. The literal content of a reply is not its act. Mock-praise, absurd escalation, a rhetorical question, a flat "yeah sure" or "sure buddy", quoting someone's own words back at them, and deadpan agreement with something ridiculous all SAY one thing and DO another. Read what the act does to its target, not the surface meaning. A reply whose words are admiring or agreeable but whose point is that the poster is ridiculous, out of touch, privileged or lying is an ATTACK, and rage fires. Do not read such a reply as seeking merely because its words are positive. The absence of swearing is not the absence of aggression: sarcasm is how contempt is delivered politely.

MOCKERY fires TWO systems, and the test is what the TARGET would feel. Ask it explicitly: reading this, would the poster feel laughed AT, diminished, called out, exposed, or denied? If yes, rage fires alongside play, however mild, polite or admiring the words are. If instead they would feel included in the joke — riffing, camaraderie, self-deprecation, a joke about a shared third thing — play fires alone. Two common dunks that must not be read as friendly: explaining someone's result by an unfair advantage they hold ("sure, with YOUR budget", "yeah cuz you got the unlimited plan") denies that the achievement is real; and questioning whether their claim exists at all (asking if the people or the results are actually there) denies their credibility. Both are attacks wearing a joke, so both fire play AND rage.
The band follows the DELIVERY, not the politeness: a controlled, well-aimed jab is rage/above, while contempt, ridicule of the person rather than the claim, profanity aimed at them, or piling absolutes ("how out of touch can you be") is rage/overwhelm.

EMOJI. 22% of replies carry them, so read them deliberately.
- When the comment HAS WORDS, the words set which system fires and the emoji only colours the intensity or the tone. An emoji must not flip the system the words establish: "its disgusting 😭" is still rage, "I miss her 😭" is still grief.
- When the emoji is the ONLY content, it IS the whole speech-act. Resolve what it is reacting to from the post, then read the act.
- WHEN THE EMOJI STANDS ALONE, read it as HYPERBOLE, not literally. 😭 💀 🫠 😵 alone under something enjoyable mark being overwhelmed by amusement or delight, not sorrow, death or collapse: that is play, often play/overwhelm, never grief. 🔥 alone marks excellence or admiration, which is seeking or play, and is only lust when the subject itself is erotic. 🤡 💅 😎 alone are self-aware performance, so play.
- Repetition and stacking (😭😭😭, 💕💕💕) raise INTENSITY only. They are a cue for the overwhelm band, never for a different system. Stacked hearts on something tender are still care, felt harder.

Below-the-line pole cues per system:
${POLES}

${JSON_RULE}
Shape: {"altitude":"Acceptance","segments":[{"quote":"","four_sides":{"factual":"","self_revelation":"","relationship":"","appeal":""},"dominant":"factual|self_revelation|relationship|appeal","systems":[{"system":"seeking|rage|fear|lust|care|grief|play","band":"above|shutdown|overwhelm"}],"why":""}]}

Text:
"""${text}"""`;
}
