# בדיקות Trainer ופרויקט — 10.11.2026

## תוצאה כוללת

הורצו195 מקרי בדיקה ייחודיים בחבילת הפרויקט ובכל חבילות הבדיקה הניסיוניות שנמצאו: **193 עברו,2 נכשלו בארכיון היסטורי**. אין כשל ידוע ב־25 בדיקות ה־Trainer החדש; ה־smoke האמיתי עבר בכל A–E. אין להציג את כלל הבדיקות ברפו כירוק ללא ההסתייגות על הארכיון.

| חבילה | עברו | נכשלו |
|---|---:|---:|
| pytest לפי testpaths של הפרויקט |59 |0 |
| main_training_runtime |25 |0 |
| main_training_preparation |16 |0 |
| data_completion |18 |0 |
| research_completion |16 |0 |
| ai_review_audit105 |10 |0 |
| research_refocus pilot |10 |0 |
| author_style_development_audit היסטורי |17 |2 |
| v2 repair contract |4 |0 |
| structured patch contract |18 |0 |

Ruff על כל קוד התשתית החדש עבר. לא שונו בדיקות או expected hashes בארכיונים כדי להעלים כשל.

## ה־smoke שבוצע

נתוני train בלבד:4 IDs קבועים,12 טקסטים ייחודיים, synthetic targets5/6, seed42. שני עדכונים בכל אחת מחמש הזרועות. אומתו tokenization,384-dimensional frozen embeddings, logits7, gradients בראש, optimizer Adam, שמירת state וטעינתו, זהות logits אחרי reload, אותו initial head hash לכל זרוע ו־encoder unchanged/no gradients. אין Accuracy/F1 או gold labels בבדיקה הזאת.

קובץ SMOKE_RESULT.json מסמן scientific_result=false; traces וסדרי האצוות נשמרו. Checkpoints המקומיים נוצרו ונטענו בפועל, אך קובצי המשקולות אינם ב־Git. לאחר clone בלי checkpoints הבדיקה התלויה בהם תדלג עד להרצת smoke מחדש; בהרצה הנוכחית עברה ולא דילגה.

## מה מכסות25 הבדיקות החדשות

התאמת105 ו־43 המקורות,9/4/6 כותבים, binding ל־SHA ופרוטוקול קפוא, חסימת AI כ־human, חסימת missing/gold disagreement/tampered data/notes None, freeze בלתי מלא, paired human fallback סימטרי, snapshot roundtrip, חסימת טעינת מודל ללא snapshot, checkpoint dimensions/reload,25 schedules בתקציב140/2240, validation metrics על2 labels מתוך7 בלי renormalization, grouping AI שאינו acceptance, tokenization audit ללא test, ואורקסטרציית25 ריצות עם trainer/predictions מדומים לחלוטין ב־TemporaryDirectory. בדיקת initialization אמיתית נוספת יצרה ראשים לא מאומנים לכל חמשת ה־seeds וכל A–E ואימתה hash זהה בתוך seed ושונה בין seeds.

האורקסטרציה עם mocks אינה הרצה מדעית. התחביר, הגייטים והחיבור נבדקו בנפרד מן ה־smoke האמיתי; לא הורצו140 עדכונים על105 המקורות ולא נוצרו תחזיות validation אמיתיות של הניסוי.

## שני כשלי הארכיון

ב־author_style_development_audit_20261108 נכשלו:

1. `test_01_frozen_sources_unchanged`: ה־hash ההיסטורי של HUMAN_VALIDATION_30.csv הוא `c6b0fab01a4fdb01943b57f5b04bdccbcc64b68faf99ef2cdcc18b7df57551e7`; הקובץ הקיים הוא `c05c7b4b3732f93f0cd34bff2e4657cd5ac2c46796ed5a6d458910060d1fdf57`. זה הקובץ הקיים כבר ב־HEAD בתחילת המשימה, המוגן ב־source hashes של ההכנות החדשות. לא השתנה כאן.
2. `test_09_original_human_package_blank_and_exact`: הערות30 השורות נקראות כ־None עקב עמודה אחרונה חסרה בנתונים, ולא כמחרוזת ריקה שהבדיקה הישנה דורשת. אין בכך אימות אנושי או החלטות חדשות.

לא שונה הקובץ, ה־hash הקפוא או הבדיקה ההיסטורית. במסלול החדש נוספו שגיאות schema/provenance ברורות במקום AttributeError או מילוי שקט. קלט אדם חדש חייב להיות מלא ובעל provenance; אין להשתמש בקובץ הארכיון כחומר gold תקין. טיפול היסטורי נוסף דורש גרסת audit חדשה, לא דריסת מקור קפוא.

## מגבלות

בדיקות תשתית אינן מאמתות נכונות תוויות או סמנטיקה. Human Validation וחתימת freeze חסרים. אין test evaluation, אימון מדעי, שינוי בספי QC או אימוץ החלטות AI כ־gold.
