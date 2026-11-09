# QC אוטומטי — 75 שכתובים ופרפרזות תואמות

תאריך בדיקה: 10.11.2026. רק 75 מקורות train שכבר הוגדרו; אין בחירת subset לפי תוצאות.

## מקור ופרוטוקול

לפי הצהרת המשתמשת: כל75 נוצרו ב־GPT-6 בתאריך 9.11.2026. גרסת מודל מדויקת, פרמטרי decoding ו־finish_reason אינם ידועים. הפרטים נשמרו כתוספת metadata, בלי דריסת receipts המקוריים. הפרפרזות הן התוצרים ההיסטוריים של אותם IDs, לא שכתובים חדשים.

אותו validator קפוא: MPNet similarity≥0.85; DeBERTa entailment בכל כיוון≥0.6; אותם guards, token limits ו־style scaling. substantial: word edit≥0.15 ועוד sentence-length relative change≥0.15 או punctuation distance≥1/100 או contraction delta מוחלט≥1/100. ספים לא שונו ולא בוצע fit מחדש.

## תוצאות

| שיטה | N | מעבר כל preservation guards | פסילה | substantial style proxy | שניהם | exact copy |
|---|---:|---:|---:|---:|---:|---:|
| Style | 75 | 42 | 33 | 71 | 39 | 0 |
| Paraphrase | 75 | 43 | 32 | 23 | 6 | 12 |

## כשלי guards

| guard | Style | Paraphrase |
|---|---:|---:|
| attribution | 1 | 4 |
| bidirectional_nli | 1 | 16 |
| certainty | 6 | 4 |
| entities | 0 | 6 |
| framing_anchors | 1 | 1 |
| future_tense | 6 | 4 |
| negation | 16 | 6 |
| numbers | 0 | 2 |
| quotations | 6 | 9 |
| similarity | 4 | 3 |

אפשר כמה דגלים לזוג אחד; אין לחבר את הספירות למספר הפסילות.

Style עבר ו־Paraphrase נפסל: 15 — creators:222877, creators:421241, creators:117018, creators:416964, creators:2644c7547b3b, creators:416490, creators:415758, creators:423931, creators:123470, creators:416624, creators:417479, creators:416232, creators:418728, creators:213908, creators:302588.

Paraphrase עבר ו־Style נפסל: 16 — creators:417886, creators:3fd01161cd76, creators:422791, creators:417610, creators:115785, creators:254aa595a403, creators:421367, creators:418022, creators:420447, creators:418916, creators:420909, creators:423635, creators:421539, creators:217678, creators:424229, creators:415881.

זו השוואת signals בלבד. אין להסיק שאחת השיטות שומרת משמעות טוב יותר ללא סקירה עצמאית; הפרפרזה אינה בקרה מושלמת על כמות או סוג השינוי.

## תוצאות לפי ID

| ID | Style pass | Style substantial | Paraphrase pass | Paraphrase substantial | Style rejection reasons |
|---|---|---|---|---|---|
| creators:222877 | True | False | False | False | — |
| creators:421269 | True | True | True | False | — |
| creators:3c2ffd23abeb | True | True | True | False | — |
| creators:122279 | False | True | False | True | future_tense, similarity |
| creators:421241 | True | True | False | True | — |
| creators:423633 | True | True | True | False | — |
| creators:117018 | True | True | False | True | — |
| creators:416964 | True | True | False | True | — |
| creators:2644c7547b3b | True | True | False | False | — |
| creators:416490 | True | True | False | True | — |
| creators:417886 | False | True | True | False | negation, quotations |
| creators:3fd01161cd76 | False | True | True | False | quotations |
| creators:415758 | True | False | False | True | — |
| creators:422791 | False | True | True | False | negation |
| creators:418434 | True | True | True | True | — |
| creators:121687 | True | True | True | False | — |
| creators:417610 | False | True | True | False | negation |
| creators:118089 | False | True | False | True | negation |
| creators:419097 | True | True | True | False | — |
| creators:416848 | False | True | False | True | certainty |
| creators:221614 | True | True | True | False | — |
| creators:219157 | True | True | True | False | — |
| creators:419420 | True | True | True | False | — |
| creators:423931 | True | True | False | False | — |
| creators:296848 | False | True | False | False | negation |
| creators:417456 | True | True | True | True | — |
| creators:209914 | True | True | True | False | — |
| creators:417661 | False | True | False | False | bidirectional_nli |
| creators:123470 | True | True | False | True | — |
| creators:208496 | False | True | False | False | negation |
| creators:119142 | True | True | True | True | — |
| creators:420299 | False | True | False | False | negation, attribution, future_tense |
| creators:115785 | False | True | True | False | quotations |
| creators:254aa595a403 | False | True | True | False | future_tense, similarity |
| creators:421367 | False | True | True | False | negation, similarity |
| creators:422298 | True | True | True | False | — |
| creators:418022 | False | True | True | False | negation |
| creators:423915 | True | True | True | False | — |
| creators:416624 | True | True | False | False | — |
| creators:420447 | False | True | True | False | future_tense |
| creators:92de8fae2e8e | True | True | True | True | — |
| creators:417479 | True | True | False | True | — |
| creators:418916 | False | True | True | True | certainty |
| creators:423650 | False | True | False | True | certainty |
| creators:223861 | True | True | True | True | — |
| creators:421736 | True | True | True | False | — |
| creators:423461 | True | True | True | False | — |
| creators:420909 | False | True | True | False | negation, quotations |
| creators:296082 | False | True | False | True | negation, similarity |
| creators:117645 | True | True | True | False | — |
| creators:118606 | True | True | True | False | — |
| creators:423635 | False | True | True | False | negation |
| creators:3e254c45e952 | True | True | True | False | — |
| creators:416232 | True | False | False | True | — |
| creators:421539 | False | True | True | False | negation |
| creators:419406 | True | True | True | False | — |
| creators:418728 | True | True | False | True | — |
| creators:ee623a4f5924 | True | True | True | False | — |
| creators:422259 | False | True | False | False | certainty |
| creators:213908 | True | True | False | False | — |
| creators:424146 | False | True | False | True | framing_anchors |
| creators:302588 | True | True | False | False | — |
| creators:418322 | True | True | True | False | — |
| creators:421811 | False | True | False | True | negation |
| creators:0b4c49505392 | False | True | False | False | quotations |
| creators:74180e505e0b | True | True | True | False | — |
| creators:217678 | False | True | True | False | future_tense |
| creators:424229 | False | True | True | False | future_tense |
| creators:423153 | False | True | False | False | quotations |
| creators:213461 | True | True | True | False | — |
| creators:423371 | False | True | False | True | certainty |
| creators:415881 | False | True | True | False | negation |
| creators:11db638844f4 | False | False | False | False | negation |
| creators:424636 | True | True | True | False | — |
| creators:419965 | False | True | False | False | certainty |

## תשומת לב באימות אנושי

כל75 מחייבים סקירה; דגל אינו הוכחת drift ו־pass אינו gold. תחילה יש לבדוק דגלי NLI ושינויים בייחוס/ודאות/ציטוטים/ישויות/מספרים. הקובץ HUMAN_REVIEW_ATTENTION_75.csv הוא כלי ניתוח נפרד, ואינו חלק מהחבילה העיוורת לסוקר.

| ID | סימני סיכון אוטומטיים |
|---|---|
| creators:417661 | NLI semantic risk; inspect claims, omissions, additions |
| creators:122279 | future_tense |
| creators:421367 | negation |
| creators:296082 | negation |
| creators:254aa595a403 | future_tense |
| creators:217678 | future_tense |
| creators:417610 | negation |
| creators:422791 | negation |
| creators:421811 | negation |
| creators:11db638844f4 | negation; style below existing proxy rule |
| creators:420299 | attribution; negation; future_tense |
| creators:423153 | quotations |
| creators:118089 | negation |
| creators:0b4c49505392 | quotations |
| creators:296848 | negation |

## מגבלות והחלטה

אין במנגנון בדיקה ישירה מתוקפת של narrative/stance או rhetorical intensity. framing anchors הם קבוצת מילים שמורה, NLI הוא proxy, ו־style proxy אינו מדד לזיהוי כותב. ספירת negation אינה בדיקת scope; מספרים/ישויות/ציטוטים עלולים לייצר false positives או לפספס שינוי תפקידים. יש לבדוק גם כמתים, מטאפורות, עוצמת טענה וסיבתיות בכל75.

בשכתובים finish_reason לא סופק: complete guard משתמש ב־truncated=False כברירת מחדל טכנית, ולא כראיה לתשובה מלאה. בפרפרזות נשמר metadata ההיסטורי. אין להציג את מספר ה־passes כמספר זוגות שמשמעותם אומתה.

לא נערכו פלטים, לא השתנו guards או ספים, לא מולאו human fields, לא אומן Narrative Classifier ולא בוצעה הערכת test. כלל הקבלה האנושי הקיים נותר בתוקף.

## שחזור וקבצים

מה־repo root:

```powershell
python artifacts/experiments/data_completion_20261109/automatic_qc.py --run extension_v1_run01
python artifacts/experiments/data_completion_20261109/compare_qc_75.py --run extension_v1_run01
python artifacts/experiments/data_completion_20261109/verify_qc_results.py --run extension_v1_run01
```

קובצי פירוט: QC_COMPARISON_BY_ID_75.csv; QC_METHOD_SUMMARY.csv; HUMAN_REVIEW_ATTENTION_75.csv; STYLE_FAILURES_NOT_IN_MATCHED_PARAPHRASE.csv. תוצאות validator ומדדי style נפרדים בתיקיות automatic_qc ו־paraphrase_qc. QC_RUN_MANIFEST.json מכיל fingerprints; מודלים מקומיים באותן revisions. אין weights/caches/progress logs ב־Git. HUMAN_REVIEW_FOCUS_NOTES_HE.md מפרט שאלות לבדיקה בכמה IDs, ללא דירוגי review.
