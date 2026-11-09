# הפער והתרומה המחקרית המועמדת

החלטה 2026-11-09: לשאול **Can meaning-preserving author-style interventions improve political narrative classification generalization to unseen authors?** ולבחון זאת אמפירית. אין לנו עדיין תוצאה שמוכיחה שיפור או מנגנון style shortcut.

הרעיון הכללי אינו חדש: Style Pooling משנה סגנון לשיפור הוגנות; CATO משתמש במבנה סיבתי וב־augmentation לשיפור OOD; Shortcut Maze יוצר style shortcuts; SCPN משווה פרפרזה מבוקרת תחביר לפרפרזה כללית; Amazon-WILDS מחלק לפי כותב. [מקורות מלאים](RELATED_WORK_DEEP_REVIEW_HE.md), [מטריצה](RELATED_WORK_COMPARISON.md). הכותרת הסופית המאומתת של עבודת CATO היא *Data Augmentations for Improved (Large) Language Model Generalization* (NeurIPS2023), ולא כותרת הטיוטה שהופיעה בתיעוד הקודם.

הפער המועמד הוא **בדיקה טבעית ומבוקרת בתחום הפוליטי**, שבו style ו־framing אינם נפרדים מאליהם: אותם מקורות, label space ברור, אימות humans של התערבות, בקרת paraphrase/augmentation, Original unseen-author evaluation, וניתוח ממצאים שליליים לצד חיוביים. לא אותר בקריאה הממוקדת צירוף זהה לכל אלה; אין בכך הוכחת ראשוניות. לפני כתיבת claim סופי דרוש citation chaining נוסף סביב העבודות הקרובות.

| דירוג | ניסוח contribution | Novelty | Significance | Evidence כיום | Feasibility | Risks |
|---|---|---|---|---|---|---|
| 1 | מחקר אמפירי מבוקר של תועלת ומגבלות meaning-preserving style interventions להכללה פוליטית בין כותבים | בינוני כתרומה תחומית; העקרונות קיימים | גבוהה אם labels ו־QC תקפים | תשתית/שליליים/פיילוט קיימים; A–E עדיין לא בוצע | בינונית | מדגם קטן, gold/provenance חסרים, style/framing entanglement |
| 2 | פרוטוקול evaluation לשימור מסגור המפריד בין author predictability, rewrite sensitivity ו־downstream benefit | בינוני, דורש הערכה ולא רק מסמך | מועילה למחקרי augmentation פוליטיים | audit ודוגמאות מחלוקת קיימים; אדם עדיין חסר | בינונית–גבוהה | להציג רובריקה בלבד כאילו validated benchmark |
| 3 | התערבות סגנונית משפרת unseen-author F1 מעבר לפרפרזה ובקרת גודל | מוגבל כעיקרון; עשוי להיות ממצא תחומי | גבוהה אם משוחזר | עדיין לא נתמך; ניסויים קודמים מעורבים/שליליים | בינונית–נמוכה כטענה חיובית מובטחת | תוצאה לא חיובית, CI רחב, confounding |

**המלצה:** 1, עם 2 כרכיב מתודולוגי. 3 היא hypothesis לתוצאה אפשרית. הניסוי המרכזי יכול להניב contribution שלילי/מוגבל אם ההתערבות וההערכה תקפות; אין צורך להמשיך לבנות repair system כדי לנסות לכפות תשובה חיובית.

ראיות כיום מאפשרות לומר: מאפייני כותב ניתנים לחיזוי, ההכללה בין מקורות מוגבלת, והשפעת rewrite אינה מזהה לבדה style dependence. אין לומר שהסרנו shortcut מזיק או שהכללה השתפרה בעקבות ChatGPT.

[כיוון התזה](THESIS_RESEARCH_DIRECTION_HE.md) · [פרוטוקול A–E](MAIN_TRAINING_EXPERIMENT_PROTOCOL_HE.md) · [מטריצת ראיות](EVIDENCE_MATRIX_HE.md)
