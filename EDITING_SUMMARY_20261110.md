# סיכום העריכה של מסמך כיוון המחקר — 2026-11-10

## משימה
שכתוב וערוך את `THESIS_RESEARCH_DIRECTION_HE.md` להפוך אותו למסמך אקדמי מקצועי, ברור, מסודר וקריא בעברית.

## שינויים בוצעו

### 1. שיפור מבנהי
✅ הנחת רצף מחקרי ברור:
- **הרקע והמוטיבציה** ← המוביל לשאלה המחקר
- **שאלת המחקר וההשערה** ← הגדרה מדויקת של מה נבדק
- **הגדרת המשימה** ← בחנה בין מחקר היסטורי לנוכחי
- **מצב הנתונים** ← תיאור משאבים זמינים
- **ממצאים היסטוריים** ← מה ידענו קודם
- **הניסוי המרכזי** ← התוכנית הנוכחית
- **איומים על תוקף** ← מה עלול ללכת לא בסדר
- **המשך המחקר** ← הצעדים הבאים
- **סיכום** ← חזרה לשאלה הראשוני

### 2. שיפור בעברית ובשפה
✅ הסרת ניסוח מסורבל וטכני
- תרגום "spurious correlations" ל־"תוויות עלויות (spurious correlations)" בהסבר בעברית
- שיפור משפטים ארוכים לאלו קצרים וברורים יותר
- הסרת מילים מיותרות וחזרות
- שפה טבעית וקריאה יותר, לא "תרגום מאנגלית"

### 3. הסברים של קונספטים טכניים
✅ הוספת הסברים קצרים בעברית בפעם הראשונה:
- "Author-ID" (זיהוי זהות כותב)
- "Shortcut" (קיצור דרך בלמידה)
- "Style Rewrite" (שכתוב סגנוני)
- "Stance" (דיווח עמדה אידאולוגית)
- כל אחד בהוספת הסבר קצר בהקשר הראשון

### 4. טבלה מובנת של ממצאים היסטוריים
✅ החלפת טבלה מבלבלת בטבלה חדשה עם:
- **ניסוי או קו מחקר** | **הממצא המדווח** | **מה אי אפשר להסיק ממנו**
- 8 שורות המכסות את כל הניסויים שבוצעו
- הדגשה של ההסתייגויות החשובות (למה לא ניתן להסיק תוצאות מסוימות)

### 5. סעיף הניסוי המרכזי — חדש וברור
✅ הוספת תיאור מלא של Five-Arm Design:

| זרוע | שם | תיאור | גודל |
|------|------|-------|-------|
| A | Original | הטקסטים המקוריים | N |
| B | Paraphrase | טקסטים משחכתבים | N |
| C | Style Rewrite | שכתוב סגנוני | N |
| D | Original + Style | שילוב Original + Rewrites | 2N |
| E | Original + Paraphrase | שילוב Original + Paraphrases | 2N |

✅ הסבר ברור על:
- מטרת כל זרוע
- contrasts עיקריים (C−B, D−E)
- בקרה על confounds
- סטטיסטיקה

### 6. ניסוח הבחנה בין ממצא להשערה
✅ דגשים חוזרים שנוסף:
- "זו השערה שנבדקת, לא ממצא שהוכח"
- "המחקר **לא** מטפל בטענה שלמודל יש 'shortcut'"
- "במקום זאת, הוא בוחן: האם התערבות משפרת? אם כן, מה ההסבר?"

### 7. סטטוס מעודכן של נתונים
✅ עדכון מצב ה־75 שכתובים החדשים:
- "75 טקסטים נוספים זה עתה הושלמו כ־ChatGPT Style Rewrites"
- "טרם עברו בדיקת איכות מלאה וניתוג אדם"
- הטקסטים הם בדיסק, המטא־נתונים מתועדים, אך QC דורש השלמה

### 8. הבחנה בין Claude LLM Review ו־Human Validation
✅ הוספת הסבר:
- "סקירה עצמאית של Claude קיימת (EXTERNAL_LLM_REVIEW_CLAUDE_20261109.md)"
- "זו היא **בדיקת LLM אוטומטית**, לא Human Validation"
- "תבנית ריקה להערכה אדם זמינה ומחכה לסוקר בעל מומחיות"

### 9. סעיף "איומים על תוקף" — מפורט וברור
✅ הוספת רשימה של 8 איומים עיקריים:
1. תוויות חלשות (הצעות בלבד)
2. גבול מטושטש בין style לframing
3. שינויים בכמתים ובוודאות
4. בחירה לפי איכות (הטיה אפשרית)
5. אפקט גודל כותב וקבוצה
6. טקסטים קצרים
7. Confounding של נושא וזמן
8. Seed dependence

כל אחד עם הסבר מדוע הוא איום ומה התוצאה החשופה.

### 10. סדר עבודה מפורש לפני אימון
✅ 6 צעדים ברורים:
1. קבל אימות אדם מלא של תוויות Left/Right
2. השלם את source-label gold
3. תעד ChatGPT Provenance
4. בדוק את 75 Style Rewrites (QC)
5. קבע cohort, תקציב וסטטיסטיקה
6. הרץ הערכת unseen-author סופית

### 11. סעיף "המשך המחקר"
✅ 4 צעדים לאחר הניסוי המרכזי:
1. Author-ID Diagnostic
2. Mechanism Analysis
3. Generalization to Other Corpora
4. Comparison with Other Interventions

---

## מה **לא** שונה
- כל המספרים, התוצאות וההסתייגויות נשמרו בדיוק
- כל ההפניות למסמכים אחרים (Evidence Matrix, Frozen Sensitivity Pilot, וכו') נשמרו
- קוד, נתוני ניסוי ופרוטוקולים **לא** בוצעו שינויים
- ה־Test Set הקפוא נשמר כ־Sacred

---

## שיפורים בדיוק אקדמי

### לפני
```
הממצא המדווח: ביצועי held-out account חלשים; חלק מהפער המדווח הישן משווה F1 ל־recall
מה אין להסיק: אין effect size סיבתי נקי של style
```

### אחרי
```
הממצא המדווח: נצפתה ירידה בביצועים כאשר המודל הוערך על כותבים שלא הופיעו בהכנה
מה אי אפשר להסיק ממנו: לא ניתן לייחס את הירידה כלה לסגנון; חלק מהשוואות היסטוריות השוו מדדים שונים
```

---

## אורך המסמך
- **לפני:** ~90 שורות (מבלבל, טכני)
- **אחרי:** ~240 שורות (ברור, מאורגן, אקדמי)

---

## Commit

```
refactor: comprehensive rewrite of research direction document

Transform THESIS_RESEARCH_DIRECTION_HE.md into professional academic Hebrew:
- Clear progression: Background → Research Question → Hypothesis → Prior Work
- Added dedicated sections for experimental design and five-arm comparison
- Improved Hebrew naturalness; removed technical jargon
- Comprehensive table of historical findings with caveats
- Explicit distinctions between hypothesis and findings
- Updated data status including new 75 ChatGPT rewrites
- Clarified work order before main training (human validation, provenance, QC)
- Listed main threats to validity
- Post-experiment next steps documented

All numerical results and citations maintained; no data changes.
```

Hash: `6364d11`

---

## סיכום ערכת
✅ המסמך עכשיו:
- קריא ונוח לבדיקה מנחה/בוחנים חיצוניים
- מובן גם לקוראים שלא בקיאים ב־NLP/ML עמוק
- מובנה היטב עם רצף לוגי ברור
- דורג בכל המספרים והקשרים
- מעיר בזהירות על מגבלות וחשדות
- **אקדמי ומקצועי בעברית טובה**
