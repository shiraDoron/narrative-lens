# Dataset V2 - Phase 1 Pilot (candidates, NOT merged into the main dataset)

Status as of 2026-09-22.

## Contents

- `matched_event_pilot.csv` - REAL data, already generated (see repo memory /
  session report). Mined offline from the existing `data/raw/*.csv` corpus (no new
  scraping). Schema: `event_id, event_description, date_window, narrative, author,
  source, text`.
- `pilot_authors_raw.csv` - NOT YET GENERATED. Will be produced by
  `src/narrative_lens/data/build_v2_pilot_dataset.py`, which is BLOCKED: it requires
  `TWITTER_AUTH_TOKEN` to be set by the user in their own terminal (the assistant will
  never collect this token). Schema: `text, narrative, author, source, platform,
  timestamp, event_id, is_synthetic, collection_date`.

## Final shortlist (verified via read-only browser checks, ready to scrape once unblocked)

- **Left-wing (5)**: `AOC`, `RBReich`, `mehdirhasan`, `TheYoungTurks`, `MeidasTouch`
- **Western (5)**: `vonderleyen`, `AtlanticCouncil`, `ianbremmer`, `CFR_org`, `ChathamHouse`
  (backup only, not scraped by default: `10DowningStreet` - see
  `PILOT_BACKUP_CANDIDATES` in `build_v2_pilot_dataset.py`)

See `docs/narrative_definitions.md` for why each Western candidate was chosen (diversifying away
from official-government-only accounts toward think-tank/independent-analyst voices).

## Do NOT merge into data/raw/*.csv

This directory is intentionally separate from the main dataset until the Phase 1
quality gate (see `qc_pilot_candidates.py`) is reviewed and approved.
