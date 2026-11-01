"""Reporting-only summary of saved results; no fitting, filtering or selection.

Added after numerical evaluation to make cohort sizes, secondary analyses and
counterfactual copies explicit. Never changes predictions or metric estimates.
"""
from pathlib import Path
import json
import pandas as pd
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def df(n):return pd.read_csv(P/n)
def md(frame):
    def v(x):return f'{x:.4f}' if isinstance(x,float) else str(x)
    return '\n'.join(['| '+' | '.join(frame.columns)+' |','| '+' | '.join(['---']*len(frame.columns))+' |']+['| '+' | '.join(v(x) for x in r)+' |' for r in frame.itertuples(index=False,name=None)])
m=df('metrics_summary.csv');d=m[(m.cohort=='matched_all_four')&(m.train_condition==m.test_condition)].set_index('train_condition');seed=df('paired_seed_comparisons.csv');cf=df('counterfactual_summary.csv');status=read('counterfactual_cohort_status.json');quality=read('matched_design_quality.json')
style=cf[cf.condition!='Paraphrase'];para=cf[cf.condition=='Paraphrase'];style_flips=int(round((style.n_predictions*style.label_flip_rate).sum()));para_flips=int(round((para.n_predictions*para.label_flip_rate).sum()))
v=read('verdict.json');v.update({'counterfactual_style_only_flip_count':style_flips,'counterfactual_paraphrase_only_flip_count':para_flips,'style_only_sensitivity_demonstrated':False,'style_only_sensitivity_interpretation':'No label flips across accepted formal/conversational/concise/elaborate variants; only three source texts changed in all four styles, so power is insufficient to claim invariance. Generic paraphrase/normalization sensitivity is a separate observation.','normalized_vs_paraphrase_seed_outcomes':{'wins':int((seed.normalized_minus_paraphrase>0).sum()),'ties':int((seed.normalized_minus_paraphrase==0).sum()),'losses':int((seed.normalized_minus_paraphrase<0).sum())},'sample_expansion_assessment':'113 versus 94: only 20.2% growth; substantially larger retained sample goal not established. Two active labels rather than seven; no cross-study F1 comparison.'})
(P/'verdict.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
main=d.loc[['Original','Formatting','Paraphrase','Normalized'],['macro_f1_mean','macro_f1_std','accuracy_mean']].reset_index()
secondary=m[(m.train_condition==m.test_condition)&m.cohort.isin(['matched_confidence3','matched_nontrivial_rewrites'])][['cohort','train_condition','macro_f1_mean','macro_f1_std','n']]
fail=df('validation_rejection_reasons.csv');fail=fail[fail.condition.isin(['Paraphrase','Normalized'])].sort_values(['condition','n'],ascending=[True,False])
full=df('fixed_full_original_summary.csv').groupby('condition')[['macro_f1','accuracy','label_flip_rate','correct_to_incorrect','incorrect_to_correct']].mean().reset_index()
baseline=m[(m.cohort=='full_original_baseline')&(m.train_condition=='Original')].iloc[0]
original_target=m[(m.cohort=='matched_all_four')&(m.test_condition=='Original')].set_index('train_condition')
text='''# תמצית תוצאות ניסוי ההמשך

**לא התקבלה כרגע תמיכה מספקת בהשערה ש־Style Normalization מסיר קיצור דרך מזיק של Author Style ומשפר הכללה מעבר לפרפרזה.** לא הוכח שההשערה שגויה; תנאי ההצלחה לא התקיימו יחד.

זהו ניסוי ממוחשב בשני נרטיבים בלבד, Right-wing ו־Left-wing, על מאמרים בעלי חתימה אישית מאותו מפרסם. הייחוס הפומבי של 19 הכותבים מתועד; אין בכך הוכחה לכתיבה ללא עזרה. הצעות התיוג הן ברמת הטקסט ואינן תוויות אמת שאומתו בידי אדם.

נאספו 456 רשומות, מהן 429 קטעים ייחודיים. 218 קטעים קיבלו הצעת תיוג מתאימה לשתי הקטגוריות; נוצרו 436 שכתובים עיקריים ו־128 גרסאות counterfactual. לאחר הסינון המשותף נותרו 113 קטעים: 54 באימון, 21 ב־validation ו־38 ב־test. יש 6 כותבי test שאינם ב־train או validation, ולכל נרטיב נשארו כמה כותבים בכל חלוקה. ההתרחבות מול 94 בפיילוט היא כ־20% בלבד; היעד למדגם מסונן גדול משמעותית עדיין לא הושג.

## ההשוואה המרכזית: אותן רשומות, חמישה seeds

הטבלה היא Train condition → Test same condition. Macro-F1 מחושב על שתי הקטגוריות הפעילות, עם אותה ארכיטקטורת שבע יחידות פלט של הפרויקט. כל המדדים נמדדו מול הצעות התיוג האוטומטיות.

'''+md(main)+f'''

Normalized נמוך מ־Paraphrase ב־{d.loc['Paraphrase','macro_f1_mean']-d.loc['Normalized','macro_f1_mean']:.4f} בממוצע: ארבע ריצות נמוכות ואחת שווה. רווח הסמך התיאורי לפי ששת כותבי ה־test להפרש N−P הוא [{v['narrative_author_cluster_bootstrap']['normalized_minus_paraphrase_ci95'][0]:.4f}, {v['narrative_author_cluster_bootstrap']['normalized_minus_paraphrase_ci95'][1]:.4f}]; הוא כולל אפס, ולכן אין כאן טענה לעליונות מובהקת של אחד התנאים באוכלוסייה. יש יתרון מספרי קטן של N מול O, אך הוא קטן מהיתרון של פרפרזה רגילה.

כאשר בודקים את כל המודלים על טקסטי Original ללא נרמול ב־test, אימון על N נותן Macro-F1={original_target.loc['Normalized','macro_f1_mean']:.4f}, לעומת {original_target.loc['Original','macro_f1_mean']:.4f} באימון על O ו־{original_target.loc['Paraphrase','macro_f1_mean']:.4f} באימון על P. לכן לא הודגם שיפור של המסווג על טקסטים מקוריים מכותבים חדשים בעקבות אימון על N בלבד.

## אין לבלבל בין גדלי מדגם שונים

ב־baseline המקורי המלא אומן הראש על 105 קטעי Original, נבחר על 43 קטעי validation ונבדק על 70 קטעים: Macro-F1={baseline.macro_f1_mean:.4f} ± {baseline.macro_f1_std:.4f}, Accuracy={baseline.accuracy_mean:.4f}. ההשוואה המרכזית לעיל מאמנת על 54 קטעים ובודקת על 38; אין לייחס את פער הציונים בין המדגמים לסגנון.

כדי למדוד רגישות במשקולות קבועות נשמר גם ראש ה־baseline המלא ונבדק על אותן 38 רשומות בכל ארבע הזרועות. הטבלה הבאה מציגה ממוצעים בין seeds; עמודות המעברים הן מספר מעברים ממוצע בכל ריצה:

'''+md(full)+'''

## זיהוי כותב וביקורות סגנון

ב־probe הגלובלי, עם 11 כותבים שנשארו להם מספיק קטעים, דיוק זיהוי הכותב מתוך embeddings נשאר 38.46% גם ב־Original וגם ב־Normalized. במאפייני הסגנון המפורשים ירד הדיוק מ־23.08% ל־21.54%; ב־Paraphrase הוא 20.77%. זו אינה ירידה עקבית וספציפית לנרמול מול שתי הביקורות ובשני הייצוגים. כל מסווג כותב אומן ונבדק מחדש באותו תנאי, והחלוקה שלו נפרדת ממשימת הכללת הנרטיב לכותבים חדשים.

ב־counterfactuals נבחרו 32 קטעים. 15 עברו את הסינון המשותף לכל הסגנונות ולזרועות העיקריות. בארבעת סגנונות היעד התקבלו 0 החלפות תווית מתוך 300 תחזיות (15 קטעים × 4 סגנונות × 5 seeds). בפרפרזה הרגילה הייתה החלפה אחת מתוך 75 תחזיות, מ־incorrect ל־correct. **רק שלושה קטעים השתנו בפועל בכל ארבעת הסגנונות**; גם בהם לא היו החלפות. זהו מדגם קטן מדי להוכחת חסינות לסגנון. שינויים קטנים בתחזיות לאחר שכתוב כללי אינם לבדם ראיה ל־Author Style shortcut.

## האם השכתוב באמת התערב בסגנון?

בכלל השכתובים, 99/218 גרסאות Normalized ו־30/218 גרסאות Paraphrase הועתקו ללא שינוי. במדגם המסונן, שיעור ההעתקה ב־Normalized עלה ל־50.4% לעומת 26.5% בפרפרזה. שיעור עריכת הטוקנים הממוצע במדגם זה הוא כ־2.55% ב־N וכ־8.09% ב־P. לכן איננו מניחים שעצם השם Normalized מעיד על הסרת סגנון; עוצמת ההתערבות מוגבלת והסינון מעשיר טקסטים שהשתנו מעט.

נפסלו 98/218 פרפרזות (45.0%) ו־30/218 נרמולים (13.8%). אלה **פסילות של מסנן אוטומטי**, לא הוכחה שכל שכתוב שנפסל אכן שגוי. מספרי הסיבות חופפים כאשר יש יותר מסיבה אחת לאותה רשומה:

'''+md(fail)+'''

## ניתוחי רגישות שנקבעו לפני תוצאות המסווג

להלן גם התוצאות שאינן תואמות לחלוטין את הדפוס המרכזי. אין להשוות תנאי ממדגם אחד לתנאי ממדגם אחר כאפקט סגנון; בתוך כל מדגם התנאים משתמשים באותן רשומות.

'''+md(secondary)+'''

ב־confidence=3 בלבד, N עדיף מספרית על P, אך אינו משפר את O. כלומר, הדפוס משתנה עם בחירת התוויות והמדגם, ואינו יתרון יציב של נרמול. במדגם שבו שני השכתובים שינו את רצף המילים נשארו רק 8 דוגמאות test וסטיות התקן גדולות מאוד; N אינו עדיף על P או O.

## Verdict

- **רגישות ל־Author Style:** לא נמצאה ראיה משכנעת לרגישות מזיקה לסגנון בלבד. יש רגישות קטנה לשכתוב כללי, בעוד שבביקורות הסגנון התקבלו אפס flips ומעט מאוד התערבויות לא מועתקות.
- **הסרת מידע על הכותב:** לא הודגמה ירידה עקבית מול Original וגם מול Paraphrase בשני סוגי הייצוג.
- **הכללה לכותבים חדשים:** יש שיפור מספרי קטן ב־N לעומת O במדגם המרכזי; הוא אינו מבסס יתרון של הסרת סגנון.
- **Normalized מול Paraphrase:** אין יתרון בניתוח המרכזי; P טוב יותר בארבע ריצות ושווה באחת. ניתוח confidence=3 משנה את הדפוס, אך גם בו N אינו עולה על O.
- **גודל דאטה, איכות שכתוב או ההשערה?** לא ניתן לייחס את התוצאה לאחד מהם בוודאות. תועדו התרחבות מדגם צנועה, התערבות סגנונית חלשה בחלק גדול מהטקסטים, ורמת הסכמה לא גבוהה בין מעריכי התוויות (58.3%, κ≈0.36). אין בסיס לדחיית ההשערה באופן כללי.
- **LoRA/DoRA:** אין הצדקה להתקדם כרגע. גם לא הוכח ש־prompting מספיק. נדרשים קודם אימות אנושי עיוור ושכתוב שמייצר שינוי סגנוני אמיתי ושומר משמעות, עמדה ומסגור.

כל הקוד, המקורות, החלוקות, הצעות התיוג, השכתובים, הפסילות, התחזיות, המדדים, רווחי הסמך וששת הגרפים נשמרו בתיקייה זו. תוצרי הפיילוט הקודם, קובצי המקור והמודל המקורי נבדקו ב־SHA-256 ולא שונו. אין טענה להוכחת סיבתיות.
'''
(P/'RESULTS_HE.md').write_text(text,encoding='utf8')
report=P/'final_research_report_he.md';body=report.read_text(encoding='utf8');marker='\n\n<!-- RESULTS_DIGEST -->\n'
body=body.split(marker)[0];report.write_text(body+marker+text.replace('# תמצית תוצאות ניסוי ההמשך','# תמצית מספרית ודיון ממוקד')+'\n',encoding='utf8')
print('Reporting-only results digest saved; estimates unchanged',flush=True)
