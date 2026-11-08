# סיכום העבודה — נתונים, Author-ID והשלב המרכזי

מחזור פיתוח 8–9 בנובמבר 2026. אין retraining של Narrative Classifier, test evaluation, שכתובים חדשים, שינוי prompts/guards/thresholds או cloud בתשלום.

1. **האם המאגר מספיק?** מספיק ל־development diagnostics, לא לביסוס ניסוי causal/confirmatory לפני אימות אנושי ואיזון גורמי תוכן/זמן. 0/429 תוויות מקור אומתו אנושית בריפו.
2. **כמה באמת זמין?** 202 מקורות מתשעה כותבי train ל־Author-ID; 105 מהם eligible לתת־משימת הנרטיבים. 96 val מארבעה כותבים נשארו מחוץ לניתוח הטקסט; 131 test משישה כותבים לא שימשו לפיתוח. 30 זוגות ChatGPT קיימים בלבד.
3. **ניסויים שבוצעו:** ארבע שיטות, ארבע קוהורטים train-only, חמישה seeds, group-aware folds; ובנפרד אותו fitted classifier על Original/Rewrite של 30 מקורות שלא השתתפו באימון.

| method | n | authors | accuracy mean | seed SD | Macro-F1 mean |
| --- | --- | --- | --- | --- | --- |
| surface_66 | 202 | 9 | 29.11% | 2.51pp | 0.2899 |
| function_punctuation | 202 | 9 | 26.44% | 2.17pp | 0.2637 |
| char_tfidf | 202 | 9 | 48.42% | 2.79pp | 0.4318 |
| word_content_control | 202 | 9 | 42.28% | 2.61pp | 0.4036 |

| method | Original accuracy | Rewrite accuracy | Original F1 | Rewrite F1 | delta accuracy | p exact | p Holm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| surface_66 | 46.67% | 33.33% | 0.4413 | 0.2783 | -13.33pp | 0.21875 | 0.65625 |
| function_punctuation | 50.00% | 26.67% | 0.4717 | 0.2083 | -23.33pp | 0.03906 | 0.15625 |
| char_tfidf | 53.33% | 53.33% | 0.4450 | 0.4979 | +0.00pp | 1.00000 | 1.00000 |
| word_content_control | 53.33% | 53.33% | 0.4878 | 0.4960 | +0.00pp | 1.00000 | 1.00000 |

4. **האם ChatGPT משנה style?** כן במאפיינים מדידים: word-sequence edit fraction ממוצע 0.278, דגל substantial ב־22/30, ושינויים בפונקציות מילים/פיסוק/קצב. אין הוכחה שהוסר author identity: ה־lexical probes נשארו 53.3%, והירידות הסגנוניות אינן יציבות בכל הבקרות או מובהקות לאחר Holm.
5. **המגבלות:** קטעים קצרים; ערבוב כותב־זמן חזק; תוכן/נרטיב/תאריך עשויים להקל על author-ID; מדגם זוגות זעיר ומכוון; אין reviews מלאים לפי ID ל־ChatGPT ואין Human Validation ממולא.
6. **מה צריך לפני הניסוי המרכזי?** לאסוף Human Validation אמיתי לכל 30, להשיג review לפי ID ופרטי generator מקוריים, ולהרחיב ללא בחירת successful-only. מוכנה רשימת 75 מקורות eligible נוספים. פרוטוקול הניסוי המרכזי מופרד ב־[MAIN_EXPERIMENT_PLAN_HE.md](MAIN_EXPERIMENT_PLAN_HE.md); לא הורץ.
7. **תוצרים:** audit וספירות לפי מחבר, קבוצות כפילויות, topic/date diagnostics, כל fold ותחזית, metrics/uncertainty/confusions, ניתוח style זוגי, רשימת rewrites חסרים, protocol, בדיקות ושחזור. חבילת האדם הקיימת נשמרה כפי שהיא, ללא מילוי.

[Corpus audit](CORPUS_AUDIT_HE.md) · [Author-ID results](AUTHOR_ID_RESULTS_HE.md) · [Style/content analysis](PAIRED_STYLE_CONTENT_HE.md) · [Reproduce](REPRODUCTION.md) · [Tests](TEST_RESULTS.md)
