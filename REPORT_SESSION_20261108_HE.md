# דוח שלמות — ChatGPT Style Rewrite Followup
**תאריך:** 2026-11-08  
**סטטוס:** כל שלוש המשימות המתוכננות **הושלמו** כבר

---

## סיכום ביצוע

| משימה | סטטוס | פרטים |
|-------|--------|--------|
| **1. ייבוא External LLM Review** | ✅ הושלמה | ספירות צבורות יובאו; דירוגים לפי ID לא סופקו ממשמר חיצוני |
| **2. הכנת Human Validation Package** | ✅ הושלמה | חבילה עיוורת מוכנה (30 זוגות); כל השדות ריקים לציון מקום |
| **3. Author-ID Diagnostic** | ✅ הושלמה | הרץ על 30 TRAIN pairs; תוצאות אינן מציגות ירידה יציבה בסגנון כותב |

---

## מה היה קיים ומה השלמתם

### משימה 1: ייבוא External LLM Review ✅
**היסטוריה:** 2026-11-02 (הושלמה בהצליחה)

סיכומי חוות דעת חיצונית שהתקבלו:
- **Meaning preserved:** 24 Yes, 6 Borderline, 0 No
- **Style change valid:** 24 Yes, 6 Borderline, 0 No  
- **Semantic drift:** 3 Yes, 11 Borderline, 16 No
- **"Clean" (drift=No):** 16/30

**חיבור קריטי:** דירוגים לפי ID **לא סופקו**. מכאן:
- לא ניתן לדעת מי מהם 16 ה־"clean" 
- לא ניתן לחשב חפיפה בין criteria (עלול להיות overlap אבל אי אפשר לדעת)
- כל המספרים צבורים בלבד

### משימה 2: Human Validation Package ✅
**היסטוריה:** 2026-11-02 (הושלמה)

**קובץ ראשי:** [`review_author_analysis_20261102/HUMAN_VALIDATION_30.md`](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md)

**עיצוב עיוור:**
- מופיעים: ID, Original text, ChatGPT Style Rewrite בלבד
- חסרים: שם כותב, narrative label, גרסאות קודמות, automatic scores, guards
- מעריך לא יודע איזה דגלים עברו או לא

**שדות להערכה (כולם ריקים כעת):**
- `human_meaning_preserved`
- `human_narrative_stance_preserved`  
- `human_style_change_valid`
- `human_semantic_drift`
- `human_notes`

**כיסוי:** כל 30 דוגמאות; ללא בחירה על בסיס external review או automatic scores.

### משימה 3: Author-ID Diagnostic ✅
**היסטוריה:** 2026-11-02 (הושלמה)

**טווח:**
- Closed-set author identification (זיהוי סגור, לא unseen-author)
- כל 30 TRAIN pairs; 9 כותבים (2-4 דוגמאות לכותב)
- לא אומן Narrative Classifier; Author-ID אומן רק בתוך fold splits (ולא נשמרו weights)
- 5 seeds: 7, 42, 123, 2026, 31415

**תוצאות:**

```
                      Accuracy     Macro-F1
Original              23.33% ± 4.71pp   0.1964 ± 0.0487
Rewrite               22.00% ± 5.58pp   0.1867 ± 0.0339
Delta (Rewrite−Orig)  -1.33pp            -0.0097
```

**בכל seed:**
```
seed    accuracy_delta    
7       +6.67pp           
42      -10.00pp          (ירידה)
123     +3.33pp           
2026    +3.33pp           
31415   -10.00pp          (ירידה)
```

---

## התוצאות — מה הן אומרות ולא אומרות

### ✅ מה הראו Author-ID תוצאות
- **שינוי לשוני:** Original ו־Rewrite הם בהתפלגויות שונות
- **Linguistic features persist:** מסווג שאומן מחדש על rewrites עדיין משיג ~23% accuracy
- **Distribution shift detected:** מסווג Original קבוע → Rewrite-dev = 28% (גבוה יותר מ־in-distribution)

### ❌ מה הן **לא** אומרות
1. **לא ירידה יציבה בסגנון כותב:** mean delta = -1.33pp, אבל SD = 4.71pp (larger than delta). בשתיים מ־5 seeds יש עלייה, בשלוש יש ירידה. אי אפשר להסיק כיוון יציב.

2. **לא הוכחה לסרת author style:** שימור של features שמזהות כותב עם rewrites שמשמרים meaning הוא עקבי עם הנתונים. זה לא מראה שהסגנון הוזר.

3. **לא לדיווח על unseen-author generalization:** זה diagnostic על TRAIN pairs בלבד. המשימה האמיתית היא: האם rewrites משפרים generalization ל־14 כותבים **חדשים** מה־frozen test?

4. **לא בחירה של seed:** תוצאה תלויה בseed: seed 42 = -10pp, seed 7 = +6.67pp. אי אפשר לבחור seed "שנתן את התוצאה הרצויה."

---

## מגבלות Author-ID Diagnostic

1. **קטן מאוד:** 30 pairs, 9 כותבים, 2-4 דוגמאות לכותב (בהשוואה: LOAO שימש 14 כותבים עם ~40 דוגמאות)

2. **Confounded features:** 66 features כולל:
   - Function word frequencies ✓ (לגיטימי)
   - אבל גם: average word length, sentence length, punctuation — אלה קשורים גם לתוכן complexity ו־emotional intensity, לא רק ל־author identity

3. **Closed-set, לא unseen-author:** אין בדיקה של fresh authors; לא יכול להעיד על unseen-author generalization

4. **Seed instability:** ה־mean masked בשינויים גדולים בין seeds. תשובה אמינה דורשת לפחות 10-20 seeds או bootstrap CI

---

## ממצאים סופיים

### מה קיים ומוכן כעת
✅ **Automatic screening:** 22/30 pass preservation, 22/30 substantial style, 15/30 both  
✅ **External LLM Review:** 24/30 meaning Yes, 24/30 style Yes, 16/30 drift=No (counts צבורים בלבד)  
✅ **Human Validation package:** עיוור, כל 30 pairs, מוכן לתחתון/ת  
✅ **Author-ID diagnostic:** הושלם; תוצאה = no stable evidence of signal reduction  

### מה **לא** בוצע וקיים
❌ **Human validation:** עדיין Pending; כל שדות הערכה ריקים  
❌ **Fresh-author generalization test:** לא הרץ על test_14_fresh_authors  
❌ **Narrative Classifier retraining:** לא אומן; weights לא נשמרו  

---

## צעדים הבאים

### דחוף (נדרש)
**1. איסוף Human Validation על כל 30:**
   - שתפו את [HUMAN_VALIDATION_30.md](artifacts/experiments/chatgpt_style_rewrite_30_20261102/review_author_analysis_20261102/HUMAN_VALIDATION_30.md)
   - ללא ידע של: automatic scores, external LLM ratings, author names
   - תעדו: משמר, תאריך, הערות על דוגמאות אי־בטוחות
   
**2. לאחר human validation (החלטה):**
   - אם human meaning+style both Yes ≥20/30 → **אישור** להמשך ל־unseen-author test
   - אם <15/30 → quality לא מספיקה; שקול alternative rewrite sources
   - **דווח בשקיפות** לפני כל שימוש downstream

### בינוני (תלוי בvalidation)
**3. Fresh-author generalization test** (אם human validation חיובית):
   - קבל rewrites של test_14_fresh_authors **בתהליך זהה**
   - אמן Narrative Classifier בנפרד על: (Original train) vs. (Rewrite train)
   - השווה recall: Original test_14_fresh vs. Rewrite test_14_fresh
   - אם rewrite עלה ב־10+ pp → evidence לטענת author-style shortcut

**4. Re-run Author-ID על test pairs** (אם fresh-author test חיובית):
   - בדוק האם ירידה בauthor-ID correlates עם עלייה בnarrative generalization
   - אבל זה secondary; primary hypothesis = narrative performance

---

## קבצי מטא

**תיקייה ראשית:** `artifacts/experiments/chatgpt_style_rewrite_30_20261102/`

| קובץ | מטרה | סטטוס |
|------|--------|--------|
| `REVIEW_PACKAGE_BLIND_30.md` | זוגות טקסט | ✅ מוכן |
| `review_author_analysis_20261102/HUMAN_VALIDATION_30.md` | טופס ערכה עיוור (30) | ✅ מוכן |
| `review_author_analysis_20261102/HUMAN_VALIDATION_30.csv` | CSV template | ✅ מוכן |
| `review_author_analysis_20261102/author_id_summary.json` | תוצאות Author-ID | ✅ הושלם |
| `REPORT_HE.md` | דוח טכני כללי | ✅ עדכני |

---

## מגבלות שנשמרו ✅

כל ההנחיות שלך נשמרו:
- ❌ **לא** שונה rewrite prompt
- ❌ **לא** שונו guards או thresholds  
- ❌ **לא** אומן Narrative Classifier
- ❌ **לא** בוצע test evaluation
- ❌ **לא** הוצגה External LLM כ־Human Validation
- ❌ **לא** נבחרו 16 דוגמאות כאילו הן sample בלתי מוטה

---

## Git Commit

הוספתי [`COMPLETION_STATUS_20261108.md`](COMPLETION_STATUS_20261108.md) עם דוח מלא (באנגלית) של סטטוס יצוא, קבצים, מגבלות, וצעדים הבאים.

```
commit a79251a
docs: add session completion status for ChatGPT style rewrite followup (2026-11-08)
```

