import torch
import torch.nn as nn
from transformers import pipeline
from narrative_lens.config import NUM_NARRATIVES


# שכבת הלמידה של הישויות
class NarrativeEntityLayer(nn.Module):
    def __init__(self, all_entities_vocab):
        super(NarrativeEntityLayer, self).__init__()

        self.entity_vocab = all_entities_vocab
        self.vocab_size = len(all_entities_vocab)
        self.num_narratives = NUM_NARRATIVES

        # יצירת טבלת המשקולות: כל ישות מקבלת וקטור ציונים לנרטיבים
        self.entity_embeddings = nn.Embedding(self.vocab_size + 1, self.num_narratives)

        # אתחול אקראי ראשוני
        nn.init.uniform_(self.entity_embeddings.weight, 0.0, 1.0)

    def forward(self, entity_indices):
        if entity_indices.numel() == 0:
            return torch.zeros(self.num_narratives)

        # שליפת הוקטורים וחישוב ממוצע הנרטיבים של הישויות בטקסט
        vectors = self.entity_embeddings(entity_indices)
        return torch.mean(vectors, dim=0)


# ניהול חילוץ הישויות מהטקסט
class EntityAnalysisPipeline:
    def __init__(self):
        print("Loading BERT-NER Model...")
        # שימוש באסטרטגיית simple כדי לחבר חלקי שמות לישות אחת
        self.ner_pipe = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )

    def extract_entities(self, text, vocab):
        """ מחלצת רשימת שמות של ישויות מהטקסט ומנקה שברים """
        results = self.ner_pipe(text)

        entities = []
        for res in results:
            word = res['word']
            # אם המילה מתחילה ב-##, אנחנו מדביקים אותה למילה הקודמת
            if word.startswith("##") and entities:
                entities[-1] = entities[-1] + word[2:]
            else:
                entities.append(word)

        # ניקוי רווחים מיותרים ש-BERT לפעמים מוסיף בחיבורים
        entities = [e.replace(" ", "") for e in entities]

        # המרה של המילים שנמצאו לאינדקסים מספריים בעזרת המילון
        indices = [vocab[ent.lower()] for ent in entities if ent.lower() in vocab]

        # הגנה חיונית: אם המשפט לא כלל ישויות מוכרות, נשים אינדקס 0 כדי שהטנזור לא יקרוס
        if len(indices) == 0:
            indices = [0]

        return torch.tensor(indices, dtype=torch.long)

    def extract_raw_entities(self, text):
        """
        Additive method (does not change extract_entities()'s existing behavior/output):
        returns the raw NER hits WITHOUT collapsing them into vocab indices, keeping the
        character offsets so callers (entity_role_tagger.py / relation_extractor.py) can
        align each entity mention to spaCy tokens for dependency-based role/relation
        extraction. Used by the Narrative Fingerprint profiler (build_profile_prototype.py),
        not by the classification models (fusion.py) which keep using extract_entities().

        Returns a list of dicts: {"text": str, "entity_group": str, "start": int, "end": int, "score": float}
        """
        results = self.ner_pipe(text)

        merged = []
        for res in results:
            word = res["word"]
            start = int(res["start"])
            end = int(res["end"])
            # merge continuation word-pieces ("##...") into the previous entity, same
            # defensive logic as extract_entities(), but keeping character offsets.
            if word.startswith("##") and merged:
                merged[-1]["end"] = end
                # Re-slice from the ORIGINAL text rather than string-concatenating
                # res['word'] fragments - see note in the else branch below for why.
                merged[-1]["text"] = text[merged[-1]["start"]:merged[-1]["end"]]
                merged[-1]["score"] = min(merged[-1]["score"], float(res["score"]))
            else:
                merged.append({
                    # Read the entity text directly from the ORIGINAL text's
                    # character offsets (ground truth) instead of trusting the
                    # pipeline's re-joined `word` string. The previous code did
                    # `word.replace(" ", "")`, which was meant to clean up stray
                    # spaces the pipeline sometimes inserts when re-joining
                    # wordpieces of a single fragmented name (e.g. "Go yili" ->
                    # "Goyili") - but it ALSO blindly destroyed the real,
                    # legitimate word-separating spaces inside correctly
                    # recognized multi-word entities (e.g. "Transportation
                    # Security Administration" -> "TransportationSecurityAdmini
                    # stration"), which then got mangled further downstream by
                    # normalize_entity()'s whitespace-based title-casing.
                    # Slicing straight from `text` is name-agnostic and always
                    # matches the true source characters (real spaces preserved,
                    # no spurious ones introduced).
                    "text": text[start:end],
                    "entity_group": res.get("entity_group", "MISC"),
                    "start": start,
                    "end": end,
                    "score": float(res["score"]),
                })

        return merged


def reconstruct_fragmented_entities(raw_entities, text, max_gap_chars=1):
    """
    Generic, name-agnostic post-processing pass to address NER FRAGMENTATION -
    e.g. a single proper noun (often a rare/foreign/transliterated name, like
    "Ran Goyili") gets split by dslim/bert-base-NER into multiple adjacent
    entity chunks ("Ra", "n", "Go", "yili", ...) because the token-classifier's
    B-/I- tag confidence flips mid-name at the sub-word level. This is NOT the
    same failure mode as the "##"-continuation merging already done in
    extract_raw_entities() (that handles clean word-piece continuations the HF
    pipeline's own aggregation_strategy="simple" already keeps together);
    this instead merges separately-returned entity dicts that are of the SAME
    entity_group and are adjacent in the original text (at most `max_gap_chars`
    characters apart - i.e. touching or separated by a single space), using
    ONLY character offsets. Deliberately contains no name-specific / alias
    lookups (per project convention: general, methodological fixes only, not
    hand-fixes for individual names encountered in a particular sample).

    `text` is the ORIGINAL source string the entities were extracted from -
    required so merged spans are re-sliced directly from it (ground truth)
    instead of synthesizing a separator (" " if gap > 0 else ""). The old
    synthesized-separator approach broke down whenever the tokenizer's
    reported offsets left a zero character gap between two chunks that were
    still genuinely separate, space-separated words in the source text (a
    known quirk of fast tokenizer offset reporting) - it produced run-on,
    no-space strings like "TransportationSecurityAdministration" for what
    should have stayed "Transportation Security Administration". Slicing from
    `text` always reproduces the real characters (real spaces, hyphens, or
    none at all) that actually appear between the merged chunks, with no
    per-name special-casing.

    Input: raw_entities as returned by extract_raw_entities(text) (must be
    sorted or will be sorted here by `start`).
    Returns a NEW list of merged entity dicts (same shape: text/entity_group/
    start/end/score), plus a "was_reconstructed" bool flag and
    "n_fragments_merged" int on each dict, so downstream error-analysis can
    flag/inspect cases where reconstruction fired (a proxy for likely
    fragmentation in the original NER output).
    """
    if not raw_entities:
        return []

    ordered = sorted(raw_entities, key=lambda e: e["start"])
    reconstructed = [dict(ordered[0], was_reconstructed=False, n_fragments_merged=1)]

    for ent in ordered[1:]:
        prev = reconstructed[-1]
        gap = ent["start"] - prev["end"]
        if gap <= max_gap_chars and ent["entity_group"] == prev["entity_group"]:
            prev["end"] = ent["end"]
            prev["text"] = text[prev["start"]:prev["end"]]
            prev["score"] = min(prev["score"], ent["score"])
            prev["was_reconstructed"] = True
            prev["n_fragments_merged"] += 1
        else:
            reconstructed.append(dict(ent, was_reconstructed=False, n_fragments_merged=1))

    return reconstructed


DEFAULT_ENTITY_MASK_TOKENS = {"PER": "[PERSON]", "ORG": "[ORG]", "LOC": "[LOCATION]", "MISC": "[MISC]"}


def mask_entities(text, raw_entities, mask_tokens=None):
    """
    Replaces each entity span (as returned by extract_raw_entities(), ideally passed
    through reconstruct_fragmented_entities() first so a single fragmented name is not
    masked twice) with a generic placeholder token based on its entity_group, e.g.
    "Trump criticized Biden" -> "[PERSON] criticized [PERSON]". Used by the Entity
    Shortcut Test (experiments/author_generalization/narrative_entity_shortcut.py) to
    strip entity IDENTITY out of the text fed to SBERT while preserving sentence
    structure and all non-entity language (stance/sentiment words, syntax, etc.) - the
    model can still see THAT an entity is mentioned and of what type, but not WHICH
    specific entity.

    Entities are masked in descending `start` order so replacing one span never shifts
    the character offsets of spans not yet processed. `mask_tokens` maps entity_group ->
    placeholder string; unmapped groups fall back to a generic "[ENTITY]" token.
    """
    tokens = mask_tokens or DEFAULT_ENTITY_MASK_TOKENS
    if not raw_entities:
        return text
    masked = text
    for ent in sorted(raw_entities, key=lambda e: e["start"], reverse=True):
        token = tokens.get(ent["entity_group"], "[ENTITY]")
        masked = masked[:ent["start"]] + token + masked[ent["end"]:]
    return masked


# --- קוד בדיקה (Test) ---
if __name__ == "__main__":
    analyzer = EntityAnalysisPipeline()

    # בדיקה על משפט לדוגמה מהקונגרס
    test_text = "Zelenskyy met with Biden in Washington regarding the war in Ukraine."

    found = analyzer.extract_entities(test_text)

    print(f"\nמשפט לבדיקה: {test_text}")
    print(f"ישויות שנמצאו: {found}")