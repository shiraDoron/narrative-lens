# Stance Annotation Guide — Experiment 22 validation sample

Applies to `validation_sample.csv` in this folder. For each row, decide the **author's
attitude specifically toward `target_entity`** — not the sentiment of the sentence as a
whole. Use `context` first; consult `original_text` if `context` is too short to judge.

## Labels (`gold_stance`)

- **positive** — the author expresses support, praise, defense, or a positive attitude
  toward the target entity.
- **negative** — the author expresses criticism, blame, mockery, opposition, or a negative
  attitude toward the target entity.
- **neutral** — the entity is only mentioned/described factually, or there isn't enough
  evidence to determine attitude.

## Critical distinction: entity-targeted attitude, not sentence sentiment

Example: *"Trump condemned the horrific attack"* — "horrific" is negative, but it targets
**the attack**, not Trump. Trump is the one condemning, so this is not evidence of a negative
attitude toward Trump. Do not label NEG just because negative-sentiment words appear near the
entity — check **who/what** the sentiment word is actually about.

## Edge-case rules

- **Quotation**: if the author is quoting someone else's words about the entity, label the
  *author's own* framing (surrounding text/tone/hashtags), not necessarily the quoted
  speaker's stance. An uncritically/approvingly presented quote reflects the author's stance.
- **Negation**: watch for negation flipping polarity ("not a threat", "never trusted him") —
  label the actual (negated) meaning, not the surface polarity of the individual words.
- **Sarcasm**: if the literal words are positive/neutral but intent (tone, hashtags, known
  account bias) is clearly mocking, label the intended meaning. Mark
  `error_category=sarcasm` if the model's prediction followed the literal words instead.
- **Reported speech about someone else's position** ("X said Y is corrupt"): label the
  *author's* stance if discernible (do they endorse, distance themselves, or stay neutral
  while relaying it?). If there's no signal of the author's own view, label neutral and mark
  `error_category=reported_speech`.
- **Criticism of an action vs. criticism of the entity**: if the entity did something and the
  author condemns it, that is usually still negative toward the entity. But if the entity is
  only a tangential bystander/location with no attitude expressed about them specifically,
  label neutral. Mark `error_category=action_vs_entity` when this distinction was genuinely
  borderline.
- **Multiple entities in the same sentence**: label each mention independently, based only on
  what's said about *that* entity. Mark `error_category=multiple_entities` if the model
  appears to have picked up sentiment meant for a different entity in the sentence.
- **Headline / context too short**: if `context` (one clause/sentence) doesn't carry enough
  information, check `original_text` for more. If still unclear, label neutral and mark
  `error_category=insufficient_context`.
- **Entity boundary wrong**: if `target_entity` is clearly mis-extracted (merged with a
  hashtag, wrong span, truncated mid-word, etc.), judge stance toward the real intended
  entity anyway, and mark `error_category=wrong_entity_boundary`.
- **Entity type wrong**: if `entity_type` is clearly the wrong category (e.g. a person tagged
  LOC), judge stance toward the real entity regardless, and mark
  `error_category=wrong_entity_type`.

## `error_category` (exactly one value per row)

Fill in whenever `gold_stance != predicted_stance`, or when a genuine edge case applies even
if the prediction happened to be right:

- `none` — prediction matches your judgment, no notable edge case.
- `negation`
- `quotation`
- `sarcasm`
- `wrong_entity_boundary`
- `wrong_entity_type`
- `insufficient_context`
- `multiple_entities`
- `reported_speech`
- `action_vs_entity`
- `other`

## `annotator_notes`

Free text for anything not captured cleanly by `error_category` (e.g. "borderline
neutral/negative", "target entity ambiguous between two candidates").
