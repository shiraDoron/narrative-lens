"""Recompute descriptive paired summaries, cases and source inventory; no inference."""
import collections
import json
import re
from run_pilot import HERE, ROOT, C, F, R, H, LABELS, read, digest, dump, save, verify


def main():
    verify()
    p = {(x['ID'], x['condition']): x for x in read(HERE/'predictions.csv')}
    t = {(x['ID'], x['condition']): x for x in read(HERE/'transitions.csv')}
    inputs = {(x['ID'], x['condition']): x for x in read(HERE/'pilot_inputs.csv')}
    metrics = {(x['ID'],x['version']): x for x in read(C/'style_metrics_v2_v3_chatgpt.csv')}
    reviews = {x['ID']:x for x in read(R)}
    ids = [x['ID'] for x in read(C/'frozen_comparison_inputs.csv')]
    cases = []
    for rid in ids:
        original = p[rid,'Original']
        q, r = p[rid,'ChatGPT'], p[rid,'Paraphrase']
        s = metrics[rid,'ChatGPT']
        para_style = json.loads(reviews[rid]['Paraphrase_style_metrics_json'])
        cases.append(dict(ID=rid, author=original['author'],
          Original=inputs[rid,'Original']['text'], ChatGPT=inputs[rid,'ChatGPT']['text'],
          Paraphrase=inputs[rid,'Paraphrase']['text'],
          original_prediction=original['prediction'], chatgpt_prediction=q['prediction'], paraphrase_prediction=r['prediction'],
          original_confidence=original['confidence'], chatgpt_confidence=q['confidence'], paraphrase_confidence=r['confidence'],
          chatgpt_flip=t[rid,'ChatGPT']['flip'], paraphrase_flip=t[rid,'Paraphrase']['flip'],
          chatgpt_tv=t[rid,'ChatGPT']['total_variation'], paraphrase_tv=t[rid,'Paraphrase']['total_variation'],
          chatgpt_word_edit_fraction=s['word_edit_fraction'], paraphrase_word_edit_fraction=para_style['word_edit_fraction'],
          chatgpt_substantial_style=s['substantial_style_change'],
          chatgpt_auto_rejections=next(x for x in read(C/'automatic_diagnostics_30.csv') if x['ID']==rid)['ChatGPT_rejection_reasons'],
          scope='descriptive training-source sensitivity; no human-gold correctness judgment'))
    save('per_id_comparison.csv',cases)
    means = {arm:sum(float(x[f'{arm}_word_edit_fraction']) for x in cases)/30 for arm in ['chatgpt','paraphrase']}
    cf={arm:{x['ID'] for x in cases if x[f'{arm}_flip']=='1'} for arm in ['chatgpt','paraphrase']}
    dump('paired_control_comparison.json',dict(n=30,
      both_flip=sorted(cf['chatgpt']&cf['paraphrase']),chatgpt_only_flip=sorted(cf['chatgpt']-cf['paraphrase']),
      paraphrase_only_flip=sorted(cf['paraphrase']-cf['chatgpt']),
      neither_flip=30-len(cf['chatgpt']|cf['paraphrase']),mean_word_edit_fraction=means,
      accuracy=None,macro_f1=None,reason='No human-gold source narrative labels; in-fit sources'))
    source_paths = [ROOT/'EXPERIMENTS.md',ROOT/'artifacts/tables/comparison_random_test.md',
      ROOT/'artifacts/experiments/group_dro/confirmatory.json',
      ROOT/'artifacts/experiments/entity_attribution/attribution_results.json',
      ROOT/'artifacts/experiments/narrative_style_normalization_generalization/final_decision.json',
      ROOT/'artifacts/experiments/narrative_few_shot_learning_curve/aggregated_table.csv',
      F/'RESULTS_HE.md',C/'summary.json',
      C/'review_author_analysis_20261102/EXTERNAL_LLM_REVIEW_CLAUDE_20261109.md',
      C/'review_author_analysis_20261102/HUMAN_VALIDATION_30.md']
    # EXPERIMENTS is a changing status index; all original result files stay read-only.
    dump('evidence_source_inventory.json',{str(x.relative_to(ROOT)):digest(x) for x in source_paths})
    lit=(ROOT/'RESEARCH_GAP_AND_NOVELTY_HE.md').read_text(encoding='utf-8')
    papers=[]
    for block in re.split(r'\n## ',lit):
        if re.match(r'\d+\.',block):
            papers.append(dict(title=block.splitlines()[0],accessed='2026-11-09',
                               urls=re.findall(r'\]\((https?://[^)]+)\)',block),
                               source_policy='Primary papers/author or institutional resources; no systematic-review completeness claim'))
    dump('literature_sources.json',papers)
    render(cases,means)


def render(cases,means):
    summary=read(HERE/'summary.csv')
    lines=['# פיילוט רגישות סגנונית של Narrative Classifier קפוא',
      '', '2026-11-09. **הבדיקה בוצעה בפועל**: 90 תחזיות על 30 מקורות train בשלושה תנאים. אין אימון חדש ואין תחזיות על validation/test.',
      '', '## התאמת המודל והגבלת ההסקה', '',
      'נבחר מראש seed42 של `full_original_baseline_Original` מהניסוי עם מחברים מזוהים, לא לפי תוצאותיו. הראש הקיים אומן בעבר על 105 מקורות Original עם תוויות טקסט אוטומטיות Left/Right ונבחר בעבר על 43 מקורות validation. לכל 30 ה־IDs יש התאמה מדויקת למקור, לתווית ולחלוקת train. כל 30 המקורות **נראו באימון הראש**. זו בדיקת רגישות במשקולות קבועות על training sources, ואינה הערכה על held-out sources או unseen authors.',
      '', 'המודל כולל MiniLM קפוא מהמשקולות המקוריות ב־`models/best_model_sbert_only.pth`, וראש קפוא 384→128→7. סדר שבע התוויות נבדק מול config ומקור האימון; נשמר softmax מלא על שבע יחידות, בלי הגבלה או renormalization לשתי יחידות. התאמת ה־ontology כאן עדיפה על החלת checkpoint של חשבונות באופן עיוור, אבל משימה עם שתי תוויות פעילות אינה רפליקציה של שבעה נרטיבים עשירים.',
      '', '## פרוטוקול', '',
      '- כל 30 המקורות, ללא סינון לפי guards, reviewer judgments או הצלחת תחזית.',
      '- אותם IDs ואותו encoder/head: Original, ChatGPT Style Rewrite, וה־Paraphrase שכבר נשמר בחבילת המקורות. לא נוצר טקסט חדש.',
      '- מצב eval, CPU, ללא gradients/fit/optimizer; אותו סדר תוויות. SHA-256 של המשקולות, המקורות והקוד נשמר לפני inference ונבדק אחריו.',
      '- פרוטוקול נכתב לפני שמירת תוצאות. ניסיון ראשון לא הצליח לשמור קבצים לאחר שתיקיית העבודה הוסרה בשינוי מקביל ברפו; השחזור השתמש באותה בחירת seed/model/arms, ללא בחירה לפי מדדים. אין תוצאות מספריות שמורות מהניסיון הכושל.',
      '- Accuracy ו־Macro-F1 **לא חושבו**: תוויות המקור הן machine proposals, לא human-gold. גם סיווג נכון על מקור שנראה באימון לא יהיה תוצאת generalization.',
      '- flip = שינוי argmax; TV = חצי סכום הפרשים מוחלטים בווקטור ההסתברות; JS בנאטים. confidence הוא max-softmax לא מכויל; delta אינו שינוי ודאות אנושי.',
      '- CI תיאורי: 2,000 דגימות bootstrap של תשעת הכותבים, seed20261109. מדגם מכוון קטן אינו מייצג אוכלוסייה; אין מבחן superiority או causal effect.',
      '', '## תוצאות', '',
      '| תנאי מול Original | flips | TV ממוצע | JS ממוצע | שינוי בביטחון המרבי | שינוי בהסתברות התווית המקורית |',
      '|---|---:|---:|---:|---:|---:|']
    for s in summary:
        lines.append(f"| {s['condition']} | {s['flips']}/30 ({float(s['mean_flip'])*100:.2f}%) | {float(s['mean_total_variation']):.6f} | {float(s['mean_js_nats']):.6f} | {float(s['mean_delta_confidence'])*100:+.3f}pp | {float(s['mean_delta_original_predicted_probability'])*100:+.3f}pp |")
    lines += ['', 'בשני התנאים flip rate=3.33%; רווח ה־bootstrap התיאורי הוא 0%–10% לכל תנאי. ה־flips התרחשו ב־IDs שונים: 28 זוגות לא שינו תווית בשום זרוע, זוג אחד רק ב־ChatGPT וזוג אחד רק בפרפרזה. אין בסיס להכריז על שקילות או היעדר השפעה רק משום שהספירה זהה.',
      '',f"עוצמת הבקרה אינה מותאמת: word_edit_fraction ממוצע ChatGPT={means['chatgpt']:.4f}, Paraphrase={means['paraphrase']:.4f}. זהו 1−SequenceMatcher, לא שיעור החלפות מילולי. תכונות ו־drift עשויים להשתנות אחרת בכל זרוע. פרפרזה היא בקרה לא מושלמת, ולא placebo סגנוני טהור.",
      '', 'ב־Paraphrase של `0105f26ef9f1` נשמר גם פתיח המכונה `Sure, here\'s the paraphrased version...`, כפי שהיה בתוצר המקורי. אין להסירו בדיעבד; נוכחותו מדגימה שבקרת הפרפרזה כוללת גם artifacts שאינם style נקי. השוואת עוצמת עריכה ממוצעת אינה מאזנת semantic drift או artifacts לפי ID.',
      '', '## מקרים וגבול החלטה', '']
    for rid,arm in [('creators:114783','ChatGPT'),('creators:116358','Paraphrase')]:
        c=next(x for x in cases if x['ID']==rid)
        a=next(x for x in read(HERE/'predictions.csv') if x['ID']==rid and x['condition']=='Original')
        b=next(x for x in read(HERE/'predictions.csv') if x['ID']==rid and x['condition']==arm)
        lines.append(f"- `{rid}`, {arm}: {a['prediction']}→{b['prediction']}; Original P(Right)={float(a['p_Right-wing']):.6f}, P(Left)={float(a['p_Left-wing']):.6f}; לאחר השכתוב P(Right)={float(b['p_Right-wing']):.6f}, P(Left)={float(b['p_Left-wing']):.6f}. אלה תחזיות מודל, לא תיקון/קלקול מול אמת אנושית.")
    lines += ['', 'ההחלפות תואמות תזוזה קטנה ליד גבול החלטה. אין דרך לייחס אותן לסגנון בלבד: paraphrase שונה בעוצמתו, המקורות נראו באימון, והשתמרות ודאות/עוצמה אינה מוכחת אנושית. גם המקור עשוי להיות מסווג לא נכון.',
      '', '## ניתוח כל 30 ה־IDs', '',
      'O/C/P הם Original/ChatGPT/Paraphrase. שורת ID אינה מוצאת מהניתוח בגלל review או guard.', '',
      '| ID | O | C | P | flip C/P | TV C | TV P |', '|---|---|---|---|---|---:|---:|']
    for c in cases:
        lines.append(f"| {c['ID']} | {c['original_prediction']} | {c['chatgpt_prediction']} | {c['paraphrase_prediction']} | {c['chatgpt_flip']}/{c['paraphrase_flip']} | {float(c['chatgpt_tv']):.5f} | {float(c['paraphrase_tv']):.5f} |")
    lines += ['', '## מה מוסיף הפיילוט ומה אינו מוכיח', '',
      'קיימת כבר בדיקת fixed-classifier היסטורית על 38 דוגמאות test בדוח byline. היא לא הורצה מחדש. הפיילוט הנוכחי מוסיף את 30 שכתובי ChatGPT החדשים יותר, על train בלבד; אין להשוות שיעורי flips משני המדגמים כאפקט של generator.',
      '', '**מסקנה:** המסווג הקפוא רגיש מעט לשכתובים האלה; לא נצפה עודף flips ב־ChatGPT לעומת פרפרזה. אין כאן הוכחה לתלות בסגנון מחבר, להסרת shortcut, לשיפור accuracy או לשיפור generalization. היעדר עודף flips אינו הוכחת חסינות.',
      '', '## הניסוי המכריע הבא — מתוכנן בלבד', '',
      'ראשית להגדיר text-level narrative/stance gold ולהשלים Human Validation עצמאי לכל 30, עם הכרעה ב־quantifiers/certainty/intensity. בהמשך: מקורות development שלא נראו במודל, כמה כותבים בכל תווית, בקרת נושא/אירוע/תקופה, ואותם IDs ב־Original/Formatting/Paraphrase/Style. לקבוע מטריקות וכלל קבלה לפני תוצאות ולדווח all-attempted לצד accepted, בלי לבחור רק clean examples.',
      '', 'לאחר מעבר שערי המדידה ורק באישור ניסוי אימון נפרד: Original מול חזרה/תקציב אימון מותאם, augmentation פרפרזה ו־augmentation style, הערכה על **Original של כותבים חדשים** כיעד ראשי. לא להחליף בו־זמנית train וגם test כתנאי ראשי. לקבע encoder/תקציב/seeds/IDs; להוסיף worst-author ו־Macro-F1 לפי gold, רווחי סמך לפי כותב, וניתוח coverage. ה־holdout ההיסטורי כבר נבחן במספר מחקרים מקומיים; אינו confirmation חדש. ייתכן צורך בכותבים חדשים באמת.',
      '', '## שחזור ותוצרים', '',
      '[קוד/פרוטוקול/תוצאות גולמיות](artifacts/experiments/research_refocus_20261109/REPRODUCTION.md): 90 וקטורי הסתברות, 60 מעברים, 30 השוואות מלאות, hashes ובדיקות. לא נשמרו משקולות חדשות, caches או logs.',
      '', '[Evidence Matrix](EVIDENCE_MATRIX_HE.md) · [פער מחקרי](RESEARCH_GAP_AND_NOVELTY_HE.md)']
    (ROOT/'STYLE_SENSITIVITY_PILOT_HE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':main()
