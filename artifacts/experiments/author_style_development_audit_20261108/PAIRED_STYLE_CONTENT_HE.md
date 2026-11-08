# מה השתנה בסגנון ומה לא הוכח

30 זוגות זהים, ללא סינון. שימור הטקסטים המקוריים והשכתובים נבדק ב־hashes. לא נוצרו שכתובים ולא בוצעה ביקורת LLM נוספת.

| measurement | observed |
| --- | --- |
| substantial style operational flag | 22/30 |
| automatic preservation pass | 22/30 |
| mean word-sequence edit fraction | 0.278 |
| sentence count changed | 9/30 |
| mean sentence-length proxy changed per pair | 30/30 |
| mean words Original → Rewrite | 59.47 → 57.87 |
| mean sentence words Original → Rewrite | 18.24 → 18.13 |
| mean content TF-IDF cosine | 0.858 |

Word edit fraction הוא 1−SequenceMatcher של רצף מילים, לא שיעור מילים שהוחלפו מילולית. Aggregate sentence mean כמעט זהה אף שכל זוג משתנה מעט; אין להפוך שינוי קטן כלשהו ל“syntax intervention משמעותי”. מספר משפטים השתנה רק ב־9/30.

| feature family | mean absolute standardized paired change |
| --- | --- |
| length | 0.169 |
| lexical_variety | 0.412 |
| sentence_structure_proxies | 0.288 |
| punctuation | 0.191 |
| orthography_contractions | 0.338 |
| function_words | 0.256 |

הסטנדרטיזציה התיאורית מבוססת על סטיית תקן של 202 Originals מ־train, לא על test ולא על labels של review. מאפייני lexical variety, contractions, פונקציות מילים ופיסוק משתנים, ולכן השכתוב אינו רק exact copy. עם זאת, המרחקים אינם metric מתוקף של כתיבה “של מחבר אחר”, והם אינם מודדים semantic preservation. [הפרשים לכל feature/ID](paired_style_feature_deltas.csv) ו[לפי כותב ומשפחה](paired_style_changes_by_author_family.csv).

לא היה English parser model מקומי; spaCy עצמו מותקן אך ללא en_core_web_sm. לא הורדו מודלים ולא הומצאו POS/dependency labels. Sentence lengths, conjunction/function-word rates ופיסוק הם proxies למבנה בלבד, לא ניתוח תחבירי או ראיית active/passive transformation.

Certainty anchor sets השתנו ב־2 זוגות; attribution sets ב־2; framing sets ב־1. זהו איתור מילים לפי אותם לקסיקונים קיימים, **לא שינוי guards** ולא שיפוט מי אמר מה, scope של uncertainty או עוצמה רטורית. Attribution guard המקורי בודק presence boolean ולכן count כשליו אינו חייב להיות זהה ל־set-change count. שימור ציטוטים, framing ו־roles דורש בדיקת הקשר.

לפי הספירות המצרפיות שסופקו קודם, rhetorical intensity קיבל 19 Yes / 10 Borderline / 1 No, ו־event characterization קיבל 22 Yes / 8 Borderline. אין ratings לפי ID כדי לחבר את החששות האלה לשינויי features. Meaning 24 Yes אינו שקול לשימור intensity בכל הדוגמאות. [רשימת anchors לפני/אחרי](paired_certainty_attribution_framing_anchors.csv) היא חומר אבחוני לחוקר, ואינה מוצגת בחבילת Human Validation.

ה־word/char classifiers מזהים כותב באותה accuracy על Original/Rewrite במדגם הקבוע. לכן שילוב של שינויים מדידים ב־surface ושל יציבות cues לקסיקליים תואם **שינוי חלקי של style**, ולא הוכחת obfuscation. גם ציון cosine גבוה אינו שולל drift קטן אך מחקרית חשוב. ה־30 נבחרו בעבר כמדגם אבחוני; אין להכליל מהם שיעורי הצלחה לכל 429.
