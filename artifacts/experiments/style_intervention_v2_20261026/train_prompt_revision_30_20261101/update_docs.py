"""Append the frozen train-only prompt experiment to central documentation."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
MARKER = "## Train-only prompt revision — 2026-11-01"


def main():
    summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    expected = {"Old": {"automatic_pass": 23, "substantial_style_proxy": 10, "both": 7, "exact_copies": 7},
                "New": {"automatic_pass": 6, "substantial_style_proxy": 24, "both": 6, "exact_copies": 0}}
    assert summary["n"] == 30 and summary["totals"] == expected
    section = """## Train-only prompt revision — 2026-11-01

ה־prompt החדש נוסה על 30 דוגמאות מ־train בלבד, מתוך המדגם האבחוני שנבחר קודם. כל שכתוב חדש נוצר רק מן ה־Original; ה־Paraphrase וה־Normalized הקודמים לא שימשו קלט לשכתוב. המודל המקומי והגדרות הפענוח נשמרו, וכך גם בדיקות השימור, הספים וכלל שינוי הסגנון הקיימים. זהו מדגם פיתוח מכוון, לא הערכת הצלחה מייצגת או ראיה להכללה לכותבים שלא נראו.

| מדד על אותן 30 דוגמאות | Old Normalized | New Normalized |
|---|---:|---:|
| מעבר כל בדיקות השימור האוטומטיות | 23/30 | 6/30 |
| שינוי סגנוני משמעותי לפי ה־proxy הקיים | 10/30 | 24/30 |
| הצלחה בשניהם יחד | 7/30 | 6/30 |
| exact copies של המקור | 7 | 0 |

**ה־prompt החדש אגרסיבי יותר בשינוי style, אבל מייצר הרבה יותר פסילות בבדיקות השימור.** פסילה אוטומטית היא signal לסיכון בלבד, ולא הוכחה ל־semantic drift; מעבר אוטומטי גם אינו אימות של שימור משמעות. שינוי משמעותי לפי proxy אינו אימות חיצוני של שינוי style אמיתי או של הסרת סימני כותב. אין להסיק מהסבב שיפור ב־Macro-F1, ב־Author Identification או בהסרת shortcut.

דוגמאות מרכזיות:

- `creators:120669` — דגל ה־NLI הקודם נפתר: השכתוב החדש עובר בסינון. זו תוצאה אוטומטית, לא הכרעה חיצונית שהמשמעות נשמרה במלואה.
- `creators:419062`, `creators:423315`, `creators:224770` — שינוי ה־style הפך למשמעותי לפי הכלל הקיים תוך מעבר בכל בדיקות השימור.
- `creators:212505` — פסילה בגלל numbers בעקבות `10` → `ten` ב־“next 10 weeks”; כנראה false positive טכני של ייצוג המספר. הדבר אינו מאמת אוטומטית את יתר השכתוב.
- `creators:298495` — דגלי negation ו־attribution; בין היתר “strangers” הוחלף ב־“anonymous sources”. נדרשת בדיקה חיצונית.
- `creators:114783` — דגלי numbers, negation, attribution ו־quotations; הציטוט המקורי לא נשמר כלשונו. נדרשת בדיקה חיצונית של משמעות, ייחוס וציטוטים.

ה־Old Normalized וה־New Normalized נשמרו זה לצד זה בקבצים נפרדים מן התוצרים הקודמים: [טבלת כל 30 ההשוואות](train_prompt_revision_30_20261101/COMPARISON_30_HE.md), [CSV עם הטקסטים והבדיקות](train_prompt_revision_30_20261101/comparison_30.csv). [הדוח המפורט](train_prompt_revision_30_20261101/REPORT_HE.md), [ה־prompt המדויק](train_prompt_revision_30_20261101/prompt.txt), [ספירות ניתנות לשחזור](train_prompt_revision_30_20261101/summary.json) ו[הוראות השחזור](train_prompt_revision_30_20261101/README.md) מתעדים את הסבב. תוצרי הבדיקה החיצונית הקודמת מתייחסים לגרסאות הישנות בלבד.

לא שונו test, validation, החלוקה, התוויות, הספים או שדות human review. לא בוצע אימון מחדש. **עוצרים כאן:** השלב הבא הוא External LLM Review חדש של כל 30 ה־New Normalized, שיבחין בין semantic drift אמיתי, false positives של ה־guards ושינוי style אמיתי. אין לכוונן שוב את ה־prompt או הסינון לפני הבדיקה הזו. בדיקת LLM אינה אימות אנושי ואינה ממלאת את שדות human review.
"""
    for name in ("EXPERIMENT_GUIDE_HE.md", "FINAL_REPORT_HE.md"):
        path = HERE.parent / name
        old = path.read_text(encoding="utf-8")
        prefix = old.split(MARKER, 1)[0].rstrip()
        path.write_text(prefix + "\n\n" + section, encoding="utf-8")


if __name__ == "__main__":
    main()
