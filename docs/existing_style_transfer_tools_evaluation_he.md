# כלי Style Transfer קיימים — feasibility ותוכנית benchmark קטנה

תאריך: 2026-11-02. **הושלמה בדיקת feasibility; לא הורץ benchmark של StyleRemix.** אין פלטים חדשים, ואין ראיה להשוואת איכות שלו מול v2. נשמרו מטא־דאטה, גרסאות, בדיקת חומרה ו־subset מתוכנן של תשע דוגמאות train, עם תוצאות v2 קיימות בלבד: [תיק ראיות ושחזור](../artifacts/research_existing_style_tools_20261102/REPRODUCTION.md).

בדיקה זו החליפה את עבודת Patch Correctness Evaluation שהופסקה לפני יצירת תוצרים. לא הושלמה הערכת correctness חדשה לתשעת ה־patches, ולא נמשכה עבודת פיתוח ה־repair. אין להציג התרשמות ביניים קודמת כהערכה גמורה.

## החלטה נוכחית

**StyleRemix הוא מועמד רלוונטי לבדיקה, אך טרם הוכח שהוא intervention מספיק טוב עבורנו.** נתיב inference מצומצם דורש wrapper קטן, GPU מתאים וגישה מורשית למודל הבסיס; אלה אינם זמינים יחד בסביבה שנבדקה. גם ה־demo הרשמי נבדק ונמצא ב־RUNTIME_ERROR, ולכן לא סיפק חלופת inference זמינה. CPU/כימות/המרה ל־backend אחר יהיו adaptation נוספת, לא הרצה ישירה של הכלי כפי שפורסם. לא הורדו משקולות inference, לא הותקנו dependencies ולא שונתה סביבת הפרויקט.

אין להסיק שהכלי נכשל בשמירת משמעות: הוא **לא נבדק אמפירית כאן**. במקביל אין בסיס להניח שהוא טוב יותר מ־v2 או להחליפו אוטומטית במנגנון המחקר. עוצרים לפני inference ולפני המשך פיתוח repair.

## גרסאות ומקורות ראשוניים

| כלי | גרסה שנקראה | מקור |
|---|---|---|
| StyleRemix | `c999002c4a5e858ac452794b20b896d06137a13c` | [README](https://github.com/jfisher52/StyleRemix/blob/c999002c4a5e858ac452794b20b896d06137a13c/README.md), [quickstart.py](https://github.com/jfisher52/StyleRemix/blob/c999002c4a5e858ac452794b20b896d06137a13c/quickstart.py), [obfuscate.py](https://github.com/jfisher52/StyleRemix/blob/c999002c4a5e858ac452794b20b896d06137a13c/obfuscate.py) |
| Thank you BART! | `6c6560caaa7828185ae914b207e3070da789a171` | [README](https://github.com/laihuiyuan/pre-trained-formality-transfer/blob/6c6560caaa7828185ae914b207e3070da789a171/README.md), [infer.py](https://github.com/laihuiyuan/pre-trained-formality-transfer/blob/6c6560caaa7828185ae914b207e3070da789a171/infer.py), [checkpoint tree](https://github.com/laihuiyuan/pre-trained-formality-transfer/tree/6c6560caaa7828185ae914b207e3070da789a171/checkpoints) |
| Decoupled Multi-Agent | אין repo רשמי מזוהה לקיבוע commit | [ACL paper](https://aclanthology.org/2025.findings-emnlp.1166/), [עמוד המחבר](https://lingxi-zhang.github.io/) |

ה־repos נקראו ב־checkout חיצוני לתיקיית הפרויקט. [external_repos.json](../artifacts/research_existing_style_tools_20261102/external_repos.json) מכיל commits ו־SHA-256 של קובצי הקוד שנבדקו. לא שוכפל קוד צד שלישי לתוך הרפו שלנו.

## StyleRemix — מה נדרש עבור טקסטים שלנו

המטרה המקורית היא authorship obfuscation, ולכן ההתאמה העקרונית לשאלת author style גבוהה יותר מהעברת formality בלבד. [Fisher et al., EMNLP 2024](https://aclanthology.org/2024.emnlp-main.241/). הצלחה ב־authorship obfuscation בדומיינים המקוריים אינה תוצאת narrative generalization אצלנו.

### שני נתיבי שימוש שונים

**Quickstart:** `remix(model, tokenizer, input_text, ...)` מקבל string ישירות, בלי AuthorMix, labels או dataset בפורמט מיוחד. הוא בונה prompt של Original/Rewrite, משלב adapters לפי משקלים ומחזיר `input`, `output`, `full_output`, sliders. כל 30 המקורות יכולים עקרונית להיכנס בלולאה, אבל בבדיקה עתידית מתחילים רק בתשע הדוגמאות המתוכננות. משקלים קבועים הם התערבות ידנית בצירי style, לא שחזור מלא של בחירת משקלים מותאמת לכותב. אם כל המשקלים אפס, הקוד מחזיר את המקור ללא generation.

**Pipeline ב־obfuscate.py:** מצפה ל־torch-serialized mapping מקונן לפי domain/author, לנתוני ממוצעי style ולבחירת adapters/weights. קיימים נתיבי weighted combination, sequential ו־LoRAHub. עבור הכותבים שלנו צריך לחשב פרופילים מנתוני train בלבד; אין להשתמש בנתוני AuthorMix או ב־test שלנו כדי לבחור מדיניות. אין צורך בצורת dataset זו ל־quickstart.

### Adapters וצירי style

כל המודלים הבאים נמצאים תחת `hallisky/` ב־Hugging Face. נבדקו metadata ו־adapter_config של **16/16**, ללא הורדת משקולות. revisions מלאים לכל אחד נשמרו ב[adapter_inventory.json](../artifacts/research_existing_style_tools_20261102/adapter_inventory.json).

| Axis | שמות ה־checkpoints לאחר `hallisky/` |
|---|---|
| Length | `lora-length-long-llama-3-8b`, `lora-length-short-llama-3-8b` |
| Function words | `lora-function-more-llama-3-8b`, `lora-function-less-llama-3-8b` |
| Grade level | `lora-grade-highschool-llama-3-8b`, `lora-grade-elementary-llama-3-8b` |
| Formality | `lora-formality-formal-llama-3-8b`, `lora-formality-informal-llama-3-8b` |
| Sarcasm | `lora-sarcasm-more-llama-3-8b`, `lora-sarcasm-less-llama-3-8b` |
| Voice | `lora-voice-active-llama-3-8b`, `lora-voice-passive-llama-3-8b` |
| Writing type | `lora-type-persuasive-llama-3-8b`, `lora-type-expository-llama-3-8b`, `lora-type-narrative-llama-3-8b`, `lora-type-descriptive-llama-3-8b` |

אלו שבעה axes ו־16 כיוונים; API ה־quickstart כולל עשרה sliders משום ש־writing type מחולק לארבעה. ה־configs שנבדקו מציינים `meta-llama/Meta-Llama-3-8B` כבסיס ו־LoRA rank 16. `narrative` ב־writing type הוא סגנון סיפורי, **לא** תווית הנרטיב הפוליטי שלנו.

לצורך benchmark עתידי כדאי לקבוע מראש subset של צירים שאינם מכוונים לשינוי עמדה, בלי random sliders ובלי LoRAHub search בסבב הראשון. sarcasm/persuasiveness, קיצור אגרסיבי ושינוי voice עלולים לגעת ב־stance, omissions או תפקידי משתתפים. זו הערכת סיכון משימתית שלנו, לא תוצאת benchmark של הכלי.

### Hardware, checkpoints ותלויות

| רכיב | ממצא |
|---|---|
| בסיס inference | `meta-llama/Meta-Llama-3-8B`, לא Instruct ולא Llama-3.1; החלפה לבסיס אחר אינה שימוש ישיר ב־adapters המקוריים. |
| revision שנבדק | `8cde5ca8380496c9a6cc7ef3a8b46a0372a1d920`; [base probe](../artifacts/research_existing_style_tools_20261102/base_checkpoint_probe.json). |
| גישה | metadata ציבורי, `gated=manual`; anonymous config GET החזיר 401. לא נבדקה הרשאה קיימת בחשבון המשתמש, ולא הוגשו טופס/הסכמה או פרטי חשבון. |
| טעינת quickstart | `AutoModelForCausalLM.from_pretrained(...).to(device)` ללא dtype/כימות מפורשים; טוען את כל 16 ה־adapters ומשלב באמצעות `cat`. |
| GPU | README דורש GPU; קוד ה־quickstart כולל CPU fallback, אבל generator ב־pipeline משתמש במפורש ב־CUDA. אין במסלול שנבדק תמיכת CPU מכומתת מוכנה. |
| זיכרון — אומדן שלנו | כ־8.03B פרמטרים: משקולות בלבד כ־29.9GiB ב־FP32 או כ־15GiB ב־BF16, לפני adapters/KV/runtime. מסלול FP32 דורש סדר גודל 40–48GB VRAM; לאחר התאמת dtype מפורשת, GPU של כ־24GB הוא יעד סביר לבדיקה, לא מדידה או הבטחה. כימות 4-bit עשוי להפחית דרישה, אך לא נבדקה תאימות לשילוב adapters. |
| חומרה כאן | Intel Core Ultra 5 125U, כ־15.5GiB RAM, Intel Graphics; `torch.cuda.is_available()=False`, אפס CUDA devices. הזיכרון הגרפי המדווח אינו NVIDIA VRAM זמין ל־CUDA. |
| סביבה כאן | Python 3.11.9, torch 2.13.0+cpu, transformers 5.15.0; ללא peft/accelerate/vllm/bitsandbytes. |
| סביבה upstream | README מציע Python 3.10; requirements אינם lockfile ומכילים vllm, TensorFlow/Keras, sentence-transformers ועוד. `quickstart.py` גם מייבא PEFT שאינו מפורט ב־requirements שנקראו. |

מקורות: קוד מקובע לעיל ו[מודל הבסיס הרשמי](https://huggingface.co/meta-llama/Meta-Llama-3-8B). מספרי VRAM הם חישובי capacity לצורך feasibility בלבד. לא בוצע ניסיון טעינת 8B על RAM מוגבל, ולא הורדו משקולות גדולות כדי להגיע ל־OOM צפוי.

נבדקה גם חלופת [ה־demo הרשמי](https://huggingface.co/spaces/hallisky/StyleRemix), המקושר מאוסף המשאבים של המחברים. revision: `27cf7bd1271efbef322464252381293884f8998b`. ה־API דיווח `RUNTIME_ERROR`, עם ImportError של `EncoderDecoderCache` בין PEFT ל־transformers, ו־hardware requested מסוג cpu-basic. זו בדיקת מצב שירות, לא בקשת generation; לא נשלחו אליו הקטעים שלנו. [Snapshot](../artifacts/research_existing_style_tools_20261102/hosted_demo_probe.json). מצב ה־demo עשוי להשתנות בעתיד.

### רישיון

קוד StyleRemix: [Apache-2.0](https://github.com/jfisher52/StyleRemix/blob/c999002c4a5e858ac452794b20b896d06137a13c/LICENSE). מודל הבסיס: רישיון `llama3` וגישה מוגבלת לפי דף המודל. שדה license ב־model-card metadata שנבדק היה חסר לכל 16 ה־adapters; אין להסיק שרישיון הקוד מכסה אוטומטית את כל המשקולות. לפני שימוש/הפצה יש לברר את תנאי checkpoint המתאימים. לא הועתקו משקולות לרפו.

### מדדים שאפשר למחזר — ומגבלות הקוד

[src/eval_data.py](https://github.com/jfisher52/StyleRemix/blob/c999002c4a5e858ac452794b20b896d06137a13c/src/eval_data.py) כולל sentence-embedding cosine באמצעות MiniLM, grammaticality ב־CoLA, length/function-words/readability, וסיווג formality/sarcasm/voice/writing type. ה־cosine אינו bidirectional NLI ואינו בודק quote fidelity או attribution; הוא יכול להישמר כמדד משלים, בלי להחליף את ה־guards הקפואים שלנו.

מסווגי authorship מוכנים מיועדים לכותבי novels/speeches/AMT/blog של הכלי. אין בהם את כותבי Creators שלנו. החלתם על Marc Dion/Harrop וכדומה אינה מודדת author-removal אצלנו; לא נאמן מסווג חדש במסגרת בדיקה זו.

נמצאו בבדיקה סטטית חסמי integration ב־pipeline, ללא הרצת קוד upstream: `args.ensemble_metho` במקום `ensemble_method` בשלב evaluation; שימוש ב־`eval.keys()` במקום mapping התוצאות בענף חישוב ממוצעים; קריאת evaluation על `original_data[author]` ולא על פלטי rewrite; ו־MiniLM עם `device='cuda'` קשיח. אלה ממצאים בקוד ב־commit שנבדק, לא תיאור תוצאות המאמר. ב־generator של ה־pipeline יש גם `max_length=256` עם truncation ו־`unidecode`; ב־quickstart הקלט מוגבל ל־2048 tokens. wrapper צריך לשמור מקור ו־output גולמיים ולתעד truncation, בלי לנרמל ציטוטים/מקור לצורך “תיקון” תוצאות.

**התאמה מינימלית עתידית:** wrapper ל־quickstart inference בלבד, עם revisions קבועים, dtype מפורש, seed/decoding מתועדים, משקלים שנקבעו מראש וקובץ JSONL. אחריו אותם guards ו־style metrics שלנו. אין צורך לשלב את כל obfuscate.py כדי להתחיל. לא נכתב wrapper לא־בדוק כאשר תנאי ההרצה לא מתקיימים.

## Thank you BART! — feasibility בלבד

ב־repo המקובע קיימים שישה קובצי `textcnn_*.chkpt` של style classifiers ופלטי מערכות מוכנים. לא נמצא בו checkpoint של מודל BART לאחר formality-transfer training. `infer.py` טוען `facebook/bart-base` ואז מחייב `checkpoints/bart_<dataset>_<order>_<style>.chkpt`; בסיס BART רגיל אינו תחליף למודל המתואר במאמר. [קוד inference](https://github.com/laihuiyuan/pre-trained-formality-transfer/blob/6c6560caaa7828185ae914b207e3070da789a171/infer.py).

אפשר עקרונית ליצור סביבה מבודדת של Python 3.7 / torch 1.4 / transformers 2.5.1. הקוד מייבא API פנימי ישן, ו־`infer.py` גם מקבע `max_length=30`, בעייתי לקטעים שלנו בני 39–97 מילים ב־subset. Port לסביבה מודרנית אינו הרצה זהה ללא בדיקה. לא הוקמה הסביבה ולא הותקנו החבילות; לא הורץ `pg.sh`, משום שהוא כולל training. Repo code הוא MIT, עם הודעות Apache בקוד BART המועתק. [LICENSE](https://github.com/laihuiyuan/pre-trained-formality-transfer/blob/6c6560caaa7828185ae914b207e3070da789a171/LICENSE).

**החלטה:** לא להריץ. חסר checkpoint transfer מאומת, והתאמת formality בלבד לשאלת author-style מוגבלת. ה־clone החיצוני כלל באופן אוטומטי את קובצי TextCNN שנמצאים ב־Git upstream; הם לא נטענו ולא נכנסו ל־Git שלנו. החיפוש אינו הוכחה שלא פורסם checkpoint במקום אחר, אלא שלא זוהה מסלול רשמי ברור בקוד/מקורות שנבדקו.

## Decoupled Multi-Agent — האם יש implementation רשמי?

לא זוהה repo רשמי ברור בתאריך הבדיקה: דף ACL, PDF המאמר ועמוד המחבר אינם מספקים קישור code שנמצא בבדיקה; שני חיפושי GitHub repositories בשם המאמר וב־style transfer/Lingxi החזירו אפס תוצאות. [ראיות חיפוש](../artifacts/research_existing_style_tools_20261102/official_implementation_search.json). קישור ה־checklist לא היה נגיש דרך כלי הגלישה, ולכן אינו ראיה לכאן או לכאן.

זו מסקנה מוגבלת של **not identified**, לא טענה שאין implementation בעולם. לא הומצא repo או שחזור כאילו הוא implementation רשמי. separate roles, self-check ו־refinement עד חמש איטרציות נשארים השראה מהמאמר בלבד; ראו [Related Work](style_transfer_related_work_he.md).

## Subset מתוכנן בלבד והשוואת v2 זמינה

בחירת תשע הדוגמאות מבוססת על סוגי בעיות ידועים, לא על הצלחת StyleRemix. כל הרשומות נלקחו מחבילת ה־train הקפואה; לא נקראו test examples ולא שונו labels/splits.

| ID ללא prefix creators: | כיסוי |
|---|---|
| 417181 | certainty, attribution, omission/quotation |
| 120177 | rhetorical intensity, temporal detail |
| 212505 | numbers, quantifiers, certainty |
| 421951 | participant roles |
| 423315 | event characterization, certainty |
| 8b0d99b23d03 | quote fidelity, metaphor, factual detail |
| 298495 | factual detail, attribution |
| 418904 | direct quote, historical detail, rhetoric |
| 459e183c1d0d | attribution, certainty, numeric detail |

[Original, v2 output, guards ו־style proxies לכל ID](../artifacts/research_existing_style_tools_20261102/planned_train_subset.json). מדדי style חושבו מחדש באמצעות הפונקציה הקיימת; ציוני ה־guards של v2 הועתקו מהריצה השמורה, ולא הורצו מודלים מחדש.

| Method | Preservation pass | Style change | Both | Exact copy |
|---|---:|---:|---:|---:|
| v2 — existing outputs, planned subset n=9 | 2/9 | 8/9 | 2/9 | 0/9 |
| StyleRemix — not run | N/A | N/A | N/A | N/A |

**זו אינה השוואת benchmark שהושלמה.** אין StyleRemix outputs ולכן אין guards, author/style scores או שיפוטי תוכן עבורו. N/A אינו 0/9. לא בוצעו Human Validation או External LLM Review.

## תשובות לשש שאלות ההחלטה

| שאלה | תשובה נתמכת כעת |
|---|---|
| יכול לשמש intervention כמעט כפי שהוא? | ממשק טקסט קיים; התאמה למשימה ואיכות טרם אומתו. ה־pipeline המלא אינו plug-and-play אצלנו. |
| adaptation קטן? | ב־GPU עם גישה לבסיס, wrapper מצומצם נראה אפשרי. CPU/כימות הוא adaptation רחבה יותר שטרם נבדקה. |
| משנה author style מספיק חזק? | צירים מפורשים קיימים; אין כאן מדידה על הכותבים שלנו, ואין לייחס להם תוצאות authorship של דומיין אחר. |
| שומר semantics טוב יותר מ־v2? | לא ידוע; ללא outputs אין השוואה תקפה. |
| מתאים לטקסטים קצרים? | string input נתמך; יציבות הצירים, readability ופרופיל הכותב על קטעים קצרים עדיין דורשת benchmark. |
| מצדיק החלפת repair engine? | עוד אין יתרון אמפירי המצדיק החלפה. כן מצדיק בדיקת benchmark חיצונית בסביבה מתאימה לפני השקעת פיתוח נוספת ב־repair. |

**התנאי להמשך:** GPU מתאים וגישה מורשית לבסיס, סביבה מבודדת ו־wrapper מאומת; אחריהם בדיוק ה־subset המתוכנן ושיטת הערכה הקפואה. תנאים אלה לא מומשו בבדיקה הנוכחית. לא בוצעו training, LoRA חדש, test evaluation, threshold tuning או שינוי guards/patch contract.
