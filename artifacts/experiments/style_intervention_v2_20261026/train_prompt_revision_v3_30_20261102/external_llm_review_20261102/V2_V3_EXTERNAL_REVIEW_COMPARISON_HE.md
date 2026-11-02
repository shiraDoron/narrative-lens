# השוואה רשמית לפי ID — External LLM Review v2 מול v3

2026-11-02; אותם 30 מקורות train. יובא קובץ סקירת v3 שסופק ללא שינוי בתים, ונשמר בנפרד מסקירת v2 ומ־Human Validation. זהו ניתוח דירוגים שסופקו, לא שופט חדש. גרסאות מודלי ההערכה, prompt ההערכה והקשר השיחה לא סופקו; העיוורון של v3 מבוסס על דיווח/חבילת המקור, ואינו מאומת עצמאית. הקבצים אינם מכילים hashes של הטקסט שנסקר; שיוך הגרסאות נשען על ID והקשר המסירה.

## כלל ההכרעה

השוואת Pareto בחמשת שדות השימור/style המשותפים: No < Borderline < Yes. improved = שיפור בשדה אחד לפחות וללא הרעה; worsened = הרעה ללא שיפור; mixed = שיפור והרעה בשדות שונים; unchanged = ללא שינוי בציונים המשותפים. אין ממוצע מספרי ואין ביטול של פגיעה במשמעות באמצעות שיפור style. כל ערכי Borderline המקוריים נשמרים.

semantic_drift נשמר בשתי גרסאותיו, אך לצורך כלל ההכרעה בלבד Yes ו־Borderline נחשבים נוכחות סיכון: v2 סימן Yes גם ל־15 מקרי meaning=Borderline, בעוד v3 משתמש ב־drift=Borderline. אין לספור שינוי מוסכמת דירוג כשיפור סמנטי. ההשוואה אינה משנה thresholds או filtering של הניסוי.

unchanged פירושו ציונים זהים, לא טקסט או שגיאה זהים. error_change_summary ושדות reported_error_types מתארים בנפרד את מוקד השגיאה בהערות. היעלמות אזכור אינה הוכחה לתיקון; קטגוריות ההערות הן קידוד איכותני של הסוכן, לא תיוג אנושי. כך למשל 295188/416436 משנים מוקד שגיאה מתואר, אף שציוני המשמעות נשארו Borderline.

## תוצאות ההשוואה

| Outcome | Count |
| --- | --- |
| improved | 1 |
| worsened | 15 |
| unchanged | 13 |
| mixed | 1 |

| Field | v2 Yes / Borderline / No | v3 Yes / Borderline / No |
| --- | --- | --- |
| meaning_preserved | 10 / 15 / 5 | 5 / 17 / 8 |
| stance_preserved | 29 / 1 / 0 | 26 / 1 / 3 |
| attribution_preserved | 29 / 0 / 1 | 27 / 2 / 1 |
| certainty_preserved | 28 / 2 / 0 | 22 / 3 / 5 |
| style_change_valid | 30 / 0 / 0 | 27 / 3 / 0 |
| semantic_drift | 20 / 0 / 10 | 9 / 16 / 5 |

## סוגי שגיאות שדווחו בהערות — לא ספירה מלאה של שגיאות

v2 לא אסף quote_fidelity/rhetorical_intensity כשדות נפרדים. לכן הטבלה הבאה מקודדת רק את ההערות בשני הסבבים, באותה טקסונומיה; היא אינה משווה היעדר שדה ב־v2 ל־Yes. קטגוריות חופפות וכיסוי ההערות שונה. גם certainty/attribution כאן הם אזכורי שגיאות בהערות, בנפרד מספירת שדות הדירוג לעיל.

| Error type | v2 count | v3 count | delta |
| --- | --- | --- | --- |
| quote_fidelity | 3 | 3 | 0 |
| certainty | 4 | 5 | 1 |
| attribution | 2 | 3 | 1 |
| factual_claims | 3 | 6 | 3 |
| event_characterization | 1 | 1 | 0 |
| participant_roles | 1 | 3 | 2 |
| rhetorical_intensity | 10 | 9 | -1 |
| omissions_additions | 2 | 6 | 4 |
| temporal_information | 1 | 3 | 2 |
| lexical_or_discourse_nuance | 3 | 3 | 0 |

## דוגמאות המיקוד

| ID | Outcome | v2 meaning | v3 meaning | error_change_summary |
| --- | --- | --- | --- | --- |
| creators:421951 | worsened | Yes | No | V3 reviewer identifies fight-for-you versus face-in-battle role reversal; v2 reviewer approved its rewrite. Not proof the defect originated only in v3. |
| creators:120669 | worsened | Yes | No | Obama/Washington subject error returns according to v3 review; v2 review explicitly reported it fixed. |
| creators:423315 | worsened | Borderline | No | Riots to protests and going-to-lose to destined-to-lose remain; meaning and certainty/stance ratings deteriorate. |
| creators:8b0d99b23d03 | unchanged | No | No | Quote alteration and two-countries issue remain; v3 additionally reports omission of Saturday/Sunday. Shared scores remain unchanged. |
| creators:298495 | unchanged | No | No | Strangers to anonymous sources remains; v3 also notes different version of God to different God. |
| creators:418904 | worsened | No | No | Quote error persists; v3 reports a new surrender-on-this-day claim and branded. Meaning stays No; stance/certainty worsen. |
| creators:459e183c1d0d | unchanged | Yes | Yes | Both reviews approve meaning, uncertainty, attribution and style; ratings alone show no gain. |
| creators:418827 | worsened | Borderline | No | Murder to slash remains; v3 also reports brandish to rewrite changing the action. Meaning worsens Borderline to No. |

ב־421951 הסקירה החדשה מזהה היפוך תפקיד, אבל תבנית דומה כבר נצפתה בטקסט v2 ב־Error Analysis; זהו גם פער גילוי בין הבודקים, לא הוכחה שהשגיאה נוצרה לראשונה ב־v3. ב־8b0d99b23d03 נשאר meaning=No ונוספה בהערות השמטת ימים; unchanged אינו אומר שלא נוספה בעיה. ב־417181 יש mixed: attribution משתפר No→Borderline בעוד certainty מידרדר Borderline→No. ב־423545 meaning משתפר No→Borderline, אך המטאפורה עדיין בעייתית. ב־459e183c1d0d שני הבודקים מאשרים; אין מכאן הוכחה שכל סיכון שזוהה בניתוח העצמי נשלל.

סקירת v3 מסמנת quote_fidelity=Yes גם ב־417181, אף שבדיקת הטקסט הקודמת הראתה מחיקת fighting; ב־423545/416436 דגל הציטוטים האוטומטי מתייחס לפסיק בתוך ציטוט. אלה אי־הסכמות/פערי קריטריון שיש לשמר, לא לתקן בקובץ המקור. אין להסיק מספירת quote=Yes שהוראת verbatim נאכפה בכל הטקסט.

## האם v3 טוב יותר?

**לפי הדירוגים שסופקו, לא הודגם שיפור כולל של v3.** meaning=Yes ירד 10→5, ‏No עלה 5→8 ו־Borderline עלה 15→17; style=Yes ירד 30→27 עם 3 Borderline. המעברים האוטומטיים עלו 6→9 וה־style proxy עלה 24→26, אך זה אינו גידול באישורי משמעות חיצוניים. 423545 מציג שיפור חלקי; 120669, ‏423315 ו־418904 מספקים דוגמאות להרעה בדירוגים. שימור סמנטי עדיין צוואר הבקבוק.

זו השוואה תיאורית בין סקירות עם הקשר ושדות לא זהים, לא ניסוי מבוקר בין מעריכים ולא הוכחה סיבתית שה־prompt לבדו גרם להחמרה. אי אפשר לחשב ממנה שיעור semantic-safe מאומת או להסיק על unseen authors/test. שלוש שאלות הסיכום הנוספות מהבקשה המקורית לא התקבלו; הדוח אינו ממציא אותן.

## כל 30 ההשוואות

| ID | Outcome | improved fields | worsened fields | error_change_summary |
| --- | --- | --- | --- | --- |
| creators:0105f26ef9f1 | unchanged |  |  | Both reviews approve meaning and style; no reported error change. |
| creators:421024 | worsened |  | meaning_preserved\|semantic_drift_risk_presence | New review flags Saturday night to next night; both mention evaluative rephrasing. |
| creators:422329 | unchanged |  |  | V2 notes duration and blame changes; v3 notes the opposing-party versus governing-party blame change. Missing duration mention alone is not proof of repair. |
| creators:417181 | mixed | attribution_preserved | certainty_preserved | Rank and claim structure remain problematic; attribution rating improves No to Borderline while certainty worsens Borderline to No. |
| creators:120177 | worsened |  | meaning_preserved\|semantic_drift_risk_presence | New timing concern: not yet Thanksgiving becomes barely Thanksgiving. |
| creators:212505 | worsened |  | style_change_valid | Meaning remains Yes; style rating declines Yes to Borderline. V2 numeric-format concern was not external semantic drift. |
| creators:421951 | worsened |  | meaning_preserved\|semantic_drift_risk_presence | V3 reviewer identifies fight-for-you versus face-in-battle role reversal; v2 reviewer approved its rewrite. Not proof the defect originated only in v3. |
| creators:422331 | unchanged |  |  | Reported error focus moves from added tradespeople interpretation to tough women versus tough uniforms; meaning remains Borderline. |
| creators:120669 | worsened |  | meaning_preserved\|stance_preserved\|attribution_preserved\|certainty_preserved\|semantic_drift_risk_presence | Obama/Washington subject error returns according to v3 review; v2 review explicitly reported it fixed. |
| creators:216128 | unchanged |  |  | Bet to strategy remains the reported expectation/planning nuance. |
| creators:421279 | unchanged |  |  | Answer revealed versus explanation made public remains Borderline. |
| creators:419062 | unchanged |  |  | Both reviews approve meaning, stance and style. |
| creators:295188 | unchanged |  |  | Both meaning ratings are Borderline; reported focus changes from final-sentence equivalence to strengthened emotional intensity. Earlier defect is not thereby proved fixed. |
| creators:423315 | worsened |  | meaning_preserved\|stance_preserved\|certainty_preserved | Riots to protests and going-to-lose to destined-to-lose remain; meaning and certainty/stance ratings deteriorate. |
| creators:422146 | worsened |  | certainty_preserved\|style_change_valid | Reported focus moves from bullying/Epstein framing to speculative perhaps; certainty and style ratings decline. No proof all earlier issues are gone. |
| creators:421853 | unchanged |  |  | Proverb interpretation persists; v3 also flags intensified schemes/seize wording. |
| creators:418620 | worsened |  | meaning_preserved\|semantic_drift_risk_presence | V3 adds a metaphor-framing concern; v2 had accepted meaning and certainty. |
| creators:114783 | unchanged |  |  | Quoted never forget is still not retained as a quotation; meaning remains Borderline. |
| creators:224770 | worsened |  | style_change_valid | Meaning remains Yes; v3 style is rated Borderline rather than Yes. |
| creators:8b0d99b23d03 | unchanged |  |  | Quote alteration and two-countries issue remain; v3 additionally reports omission of Saturday/Sunday. Shared scores remain unchanged. |
| creators:97c9d6b9ac1b | worsened |  | certainty_preserved | V3 notes omitted/weakened destruction, axe, fancy and sneakily; certainty rating declines despite a different notes focus. |
| creators:423545 | improved | meaning_preserved |  | Meaning improves No to Borderline; weakened hoisting metaphor remains. This is partial improvement, not full preservation. |
| creators:298495 | unchanged |  |  | Strangers to anonymous sources remains; v3 also notes different version of God to different God. |
| creators:418904 | worsened |  | stance_preserved\|certainty_preserved | Quote error persists; v3 reports a new surrender-on-this-day claim and branded. Meaning stays No; stance/certainty worsen. |
| creators:2e34435c6ccf | worsened |  | certainty_preserved | Inevitability/expectation strengthening remains; certainty rating worsens Yes to No. |
| creators:459e183c1d0d | unchanged |  |  | Both reviews approve meaning, uncertainty, attribution and style; ratings alone show no gain. |
| creators:416436 | unchanged |  |  | Reported focus moves from superiority softened to virtues toward cheap/easy replaced by effective. Borderline rating persists; error substitution is not proof of overall improvement. |
| creators:116358 | worsened |  | attribution_preserved | Relationship shift remains; v3 also reports voluntary departure and lowers attribution to Borderline. |
| creators:218236 | worsened |  | certainty_preserved | Normative reframing persists; v3 additionally flags uncertainty emphasis and rates certainty Borderline. |
| creators:418827 | worsened |  | meaning_preserved | Murder to slash remains; v3 also reports brandish to rewrite changing the action. Meaning worsens Borderline to No. |

## תוצרים ושחזור

- [כל השדות, ההערות והתוצאות לפי ID](V2_V3_EXTERNAL_REVIEW_COMPARISON_30.csv).
- [ספירות outcome](OUTCOME_COUNTS.csv), [מעברי שדות](FIELD_TRANSITIONS.csv), [סוגי שגיאות מדווחות](REPORTED_ERROR_TYPE_COUNTS.csv).
- [מקור v3 ללא שינוי](V3_BLIND_EXTERNAL_LLM_REVIEW_30_20261102.csv), [סיכום](summary.json), [בדיקת תקינות](import_comparison_audit.json).

להרצה חוזרת של הייבוא/הסיכום בלבד, מתיקיית הרפו:

```powershell
python artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_v3_30_20261102/external_llm_review_20261102/compare_reviews.py
```

לא שונו prompt, guards, thresholds, filtering, split, labels, human-review fields או קוד אימון. לא הורצו מודל שופט, training או test evaluation. External LLM Review ≠ Human Validation. עוצרים לפני שינוי נוסף.
