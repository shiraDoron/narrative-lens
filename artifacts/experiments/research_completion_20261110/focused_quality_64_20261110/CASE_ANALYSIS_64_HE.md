# ביקורת איכות ממוקדת — 64 זוגות train

ביקורת AI של ChatGPT/Codex (גרסת מודל מדויקת לא ידועה), 10.11.2026. הביקורת אינה עיוורת ואינה אימות אנושי. הקריאה החוזרת בוצעה בידי אותו עוזר; אין כאן agreement בין סוקרים עצמאיים. 57+7 הם קבוצות הבחירה הקודמות, לא תוצאות חדשות.

הטקסטים, דירוגי AI קודמים וציוני QC נשמרו. האבחון הלקסיקלי שוחזר מהקוד הקפוא והושווה לכל הדגלים השמורים; NLI/NER לא הורצו מחדש. כמתים, scope, ייחוס ועוצמה נבדקו בקריאה של המשפטים המלאים, לא מתוך רשימת מילים בלבד.

## creators:222877

| Original | Style Rewrite |
|---|---|
| The Trump administration and the Republicans in Congress have passed one of the best pro-growth tax bills ever. The Tax Cuts and Jobs Act ranks in the all-time hall of fame along with former President Reagan's 1981 and 1986 tax acts, and former President Kennedy's posthumous tax cuts in 1964. The announcements by Apple, FedEx, AT&T, Fiat Chrysler and over 300 companies with multibillion dollar investments in the United States are early lead indicators of good things to come from the tax-rate cuts. | One of the best pro-growth tax bills ever has been passed by the Trump administration and the Republicans in Congress. Alongside former President Reagan's 1981 and 1986 tax acts and former President Kennedy's posthumous tax cuts in 1964, the Tax Cuts and Jobs Act belongs in the all-time hall of fame. Early lead indicators of the good things to come from the tax-rate cuts are the announcements by Apple, FedEx, AT&T, Fiat Chrysler and over 300 companies of multibillion dollar investments in the United States. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** אותן הערכות מס, השוואות היסטוריות, שנים וחברות. מעבר לפסיב וסידור שלושת המשפטים מחדש ניכר גם אם ה־style proxy לא substantial.

**QC שמור:** passed=True; failed=none; similarity=0.9570993185043335; NLI forward/reverse=0.9946079254150391/0.9909042716026306; style substantial=False.

**הבדל ממוקד:** סידור מחדש של משפטי המס וההכרזות, בלי שינוי הטענות

**ממצא וקשר לדגלים:** שינוי מבני ניכר בקריאה; proxy המבוסס גם על אורכי משפט ופיסוק אינו מודד תחביר. אין כאן באג מוכח או שינוי משמעות מזוהה.

**קריאה חוזרת:** נבדקו שוב השנים, החברות וההשוואות ההיסטוריות; לא נמצא שינוי תוכן.

**סיווג אנליטי:** פער בין proxy לסגנון בקריאה

**המשך מומלץ:** לשפוט את מידת שינוי הסגנון; לא לכוונן סף כדי להעביר מקרה זה.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [
      "states"
    ],
    [
      "states"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "1964",
      "1981",
      "1986",
      "300"
    ],
    [
      "1964",
      "1981",
      "1986",
      "300"
    ]
  ]
}
```

</details>

## creators:421269

| Original | Style Rewrite |
|---|---|
| They're so disgusted that a top legislative priority of Republican leaders in the White House, Congress and state legislatures is to rig election rules, literally to rule out issues and voters they don't like. For example, Republicans in Missouri (the "Show Me" State) showed us what they're made of by attempting to kill the people's right to amend their state's constitution. Missouri and 25 other states have long provided a citizen-led initiative process so the people can propose and pass their own laws, rather than always depending on politicians to "do what's right." Yes — it's direct democracy! | So disgusted are they that Republican leaders in the White House, Congress and state legislatures have made rigging election rules a top legislative priority, literally ruling out issues and voters they don't like. Consider Missouri (the "Show Me" State): Republicans there showed us what they're made of when they attempted to kill the people's right to amend their state's constitution. In Missouri and 25 other states, a citizen-led initiative process has long allowed people to propose and pass laws of their own instead of always relying on politicians to "do what's right." Yes — it's direct democracy! |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** to rule out מנסח תכלית, ואילו literally ruling out עשוי להישמע כתוצאה שכבר מתרחשת. שאר מנגנון היוזמה, המדינות והציטוטים נשמרים; הביקורת על הרפובליקנים זהה.

**QC שמור:** passed=True; failed=none; similarity=0.9008392095565796; NLI forward/reverse=0.9948818683624268/0.9941311478614807; style substantial=True.

**הבדל ממוקד:** to rig ... literally to rule out → literally ruling out

**ממצא וקשר לדגלים:** ניסוח תכלית עשוי להפוך לתיאור תוצאה; אפשר גם לקרוא את שניהם כהסבר לאותה מניפולציה. מעבר QC אינו מכריע בהיבט זה.

**קריאה חוזרת:** גם בקריאה בתוך המשפט המלא היבט הפעולה אינו חד־משמעי; נשמר Borderline אנליטי.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** הכרעה אנושית על תכלית לעומת תוצאה, בלי השלמת הקשר.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't"
    ],
    [
      "n't"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "do what's right.",
      "show me"
    ],
    [
      "do what's right.",
      "show me"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [
      "states"
    ],
    [
      "states"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "25"
    ],
    [
      "25"
    ]
  ]
}
```

</details>

## creators:218236

| Original | Style Rewrite |
|---|---|
| Republicans are supposed to be the party that cuts the job-killing capital gains tax, not raises it. But because of a quirk in the Senate-passed tax bill, the tax on capital gains may go up — and for some types of long-held assets, fairly substantially. | Republicans are supposed to be the party that cuts the job-killing capital gains tax, not the party that raises it. Yet a quirk in the tax bill passed by the Senate could push capital gains taxes higher—and for some long-held assets, the increase may be fairly substantial. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** may/could נשארים אפשרות, והגידול במס לחלק מהנכסים נשאר מסויג. השכתוב מרחיב את הניגוד ומשנה את המבנה בלי שינוי בטענה או בעמדה.

**QC שמור:** passed=False; failed=certainty; similarity=0.9628844261169434; NLI forward/reverse=0.9952398538589478/0.9897952675819397; style substantial=True.

**הבדל ממוקד:** may go up → could push ... higher; increase may ...

**ממצא וקשר לדגלים:** האפשרות נשארת מסויגת. הוספת could לרשימת מילות certainty אינה כשלעצמה שינוי ברמת הוודאות.

**קריאה חוזרת:** נבדק גם הסייג לנכסים מסוימים ולעוצמת העלייה; לא זוהה שינוי טענה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** לאמת שימור מודאליות; אין הצדקה לתקן טקסט רק בגלל הדגל.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not"
    ],
    [
      "not"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [
      "may"
    ],
    [
      "could",
      "may"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:122279

| Original | Style Rewrite |
|---|---|
| Democrats are the masters of deceptive persuasion, meaning they will take our attention off something they have really screwed up and put it on something that's not quite so bad. And chief among those masters is he who resides at 1600 Pennsylvania Ave. in Washington, D.C. | Taking our attention away from something they've really screwed up and directing it toward something that's not quite so bad — that's the deceptive persuasion Democrats have mastered. Among the chief masters of this technique is the man residing at 1600 Pennsylvania Ave. in Washington, D.C. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** chief among those masters לעומת Among the chief masters עשוי להחליש דירוג יחיד בראש הקבוצה לקבוצת מובילים. התיאור של הסחת דעת והיעד הפוליטי נשמרים.

**QC שמור:** passed=False; failed=future_tense|similarity; similarity=0.7737259864807129; NLI forward/reverse=0.9969661831855774/0.9900598526000977; style substantial=True.

**הבדל ממוקד:** they will take attention → Taking ...; chief among → Among the chief

**ממצא וקשר לדגלים:** המרת עתיד לניסוח גנרי יכולה לשמר הרגל; שינוי chief עלול להחליש דירוג. similarity ועתיד הם אותות כלליים, לא אבחון של דירוג.

**קריאה חוזרת:** קריאה חוזרת אינה מבססת אובדן עתיד לבדה, אך דירוג הבכירות עדיין דורש הכרעה.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** לבדוק דירוג ועוצמה; להבחין בין זמן גנרי לניבוי.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not"
    ],
    [
      "not"
    ]
  ],
  "future": [
    true,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "1600"
    ],
    [
      "1600"
    ]
  ]
}
```

</details>

## creators:417181

| Original | Style Rewrite |
|---|---|
| It turns out that the most generous funder of white supremacist groups in the United States was likely the Southern Poverty Law Center. At least that's what the Department of Justice's superseding indictment against the SPLC alleges. The organization secretly paid informants to engage in the active promotion and funding of racist groups while denouncing and "fighting" the very same groups in public. The SPLC purportedly created fictitious entities to hide funding from their donors. | The Southern Poverty Law Center was likely the largest financial backer of white supremacist groups in the United States—or at least that is what the Department of Justice alleges in its superseding indictment against the SPLC. According to the indictment, the organization secretly paid informants to actively promote and fund racist groups while publicly denouncing and "fighting" those same groups. The SPLC also purportedly created fictitious entities to conceal funding from its donors. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** most generous funder הומר ל־largest financial backer, פרשנות כמותית מפורשת יותר. לפי ההקשר ייחוס לכתב האישום סביר גם במשפטי ההמשך, אך השכתוב מרחיב אותו במפורש. likely/purportedly והביקורת נשמרים.

**QC שמור:** passed=True; failed=none; similarity=0.8973104953765869; NLI forward/reverse=0.9897533655166626/0.9793847799301147; style substantial=True.

**הבדל ממוקד:** most generous funder → largest financial backer; According to the indictment

**ממצא וקשר לדגלים:** בהקשר המימון, largest הוא פירוש סביר ל-most generous. likely, alleges ו-purportedly נשמרים; הייחוס למשרד המשפטים חל כבר במקור על ההאשמות.

**קריאה חוזרת:** אין בסיס חזק להכרעת drift רק מהפיכת הייחוס למפורש. הסתייגות ה-AI הקודמת נשמרת בארכיון אך אינה מאומצת כאן.

**סיווג אנליטי:** הסתייגות AI קודמת לא נתמכת בקריאת ההקשר

**המשך מומלץ:** לבקש מהאדם לבדוק גודל תמיכה לעומת נדיבות והיקף ייחוס; אין קבלה אוטומטית.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "fighting"
    ],
    [
      "fighting"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [
      "alleges",
      "states"
    ],
    [
      "according",
      "alleges",
      "states"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:418827

| Original | Style Rewrite |
|---|---|
| WASHINGTON — No, friends, Romans, countrymen, it wasn't enough to murder the White House Rose Garden. It wasn't enough to tear down its stately East Wing, where guests gathered and mingled. It wasn't enough to brandish "Donald J. Trump" over "John F. Kennedy" on the marble wall of the national performing arts center. | WASHINGTON — No, friends, Romans, countrymen, murdering the White House Rose Garden was not enough. Tearing down its stately East Wing, where guests once gathered and mingled, was not enough either. Nor was it enough to brandish "Donald J. Trump" over "John F. Kennedy" on the marble wall of the national performing arts center. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** כל שלוש הטענות, שמות הציטוטים ומטאפורת murder נשמרים. החזרה it wasn't enough הומרה למבנה שמני ול־Nor בלי לאבד את ההאשמה המצטברת.

**QC שמור:** passed=False; failed=framing_anchors; similarity=0.9633510112762451; NLI forward/reverse=0.9434950351715088/0.9903761744499207; style substantial=True.

**הבדל ממוקד:** murder → murdering

**ממצא וקשר לדגלים:** אותו גינוי מטאפורי לאותם מעשים; framing guard מזהה צורת מילה מדויקת ולא נטייה דקדוקית.

**קריאה חוזרת:** נבדקו שלוש ההאשמות ושני השמות המצוטטים; לא זוהה ריכוך פוליטי.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** בדיקה אנושית רגילה, לא תיקון סמנטי בשל נטיית המילה.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "no",
      "n't",
      "n't",
      "n't"
    ],
    [
      "no",
      "not",
      "not",
      "nor"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "donald j. trump",
      "john f. kennedy"
    ],
    [
      "donald j. trump",
      "john f. kennedy"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [
      "murder"
    ],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:417886

| Original | Style Rewrite |
|---|---|
| Step right up, folks! Please don't crowd! No need to shove, plenty here for everyone! Welcome to the Bonanza Extravaganza of the Artificial Intelligence (AI) "BOOM." Silicon Valley billionaires are now proposing a scheme to deliver an unbelievable windfall to "every citizen." Tech titans like Sam Altman of OpenAI are pushing the federal government to create a "public wealth fund" to let us commoners be investment partners in building the AI wonderworld. | Folks, step right up! There's no need to shove or crowd — we've got plenty for everyone! The Bonanza Extravaganza of the Artificial Intelligence (AI) "BOOM" welcomes you! What Silicon Valley billionaires are proposing now is a scheme that promises an unbelievable windfall to "every citizen." Tech titans such as Sam Altman of OpenAI want the federal government to establish a "public wealth fund," making us commoners investment partners in the construction of the AI wonderworld. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** scheme to deliver→scheme that promises מוסיף מסגור של הבטחה מפורשת; מטרת הקרן נשארת. BOOM.→BOOM משנה פיסוק בתוך ציטוט. הסאטירה וההכללה לכל אזרח נשמרות.

**QC שמור:** passed=False; failed=negation|quotations; similarity=0.9758507013320923; NLI forward/reverse=0.9923290610313416/0.984553337097168; style substantial=True.

**הבדל ממוקד:** Please don't crowd → no need ... crowd; to deliver → promises; BOOM. → BOOM

**ממצא וקשר לדגלים:** איסור עשוי להיחלש להיעדר צורך; promises מוסיף ייחוס הבטחה. שינוי הפיסוק בתוך ציטוט הוא חריגת fidelity אמיתית, גם בלי שינוי תוכן.

**קריאה חוזרת:** בקריאה חוזרת חלק מדגל השלילה טכני, אך כוח ההנחיה וההבטחה אינם נפתרים בכך.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** לשפוט כוח הנחיה, ייחוס הבטחה ונאמנות ציטוט בנפרד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't",
      "no"
    ],
    [
      "no"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "boom.",
      "every citizen.",
      "public wealth fund"
    ],
    [
      "boom",
      "every citizen.",
      "public wealth fund,"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:3fd01161cd76

| Original | Style Rewrite |
|---|---|
| It's the fall harvest season, when many farm stands and homes decorate with pumpkins, cornstalks and maybe even a straw man. How to make a straw man? Easy — stuff a couple of burlap bags with hay and dress your "man" in an old flannel shirt, overalls and a straw hat. But today's billionaires, corporate elites and other political megadonors have come up with their own version of this creature — stuff a couple of silk pillows with thousand-dollar bills, dress him in a finely tailored suit and — viola! — they turn a common straw man into a congressman. | With fall harvest season comes the familiar sight of pumpkins, cornstalks and perhaps a straw man decorating farm stands and homes. Making a straw man is easy: take a couple of burlap bags, stuff them with hay, then put an old flannel shirt, overalls and a straw hat on your "man." Today's billionaires, corporate elites and other political megadonors, however, have devised a version of their own. Their recipe calls for a couple of silk pillows stuffed with thousand-dollar bills and a finely tailored suit for the fellow. And — viola! — a common straw man becomes a congressman. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** המעבר ל־becomes אינו מוחק את הסוכנות: billionaires...have devised ו־Their recipe ממשיכים לייחס להם את יצירת איש הקש. לכן No עקב היעלמות המבצע חזק מדי. many הוחלף ב־familiar sight ללא כמות מפורשת, והפיסוק ב־man השתנה; אלה מצדיקים Borderline במשמעות. הסאטירה כלפי התורמים נשמרה.

**QC שמור:** passed=False; failed=quotations; similarity=0.9811747074127197; NLI forward/reverse=0.9952515363693237/0.9800136089324951; style substantial=True.

**הבדל ממוקד:** many farm stands → familiar sight; man → man. בתוך ציטוט

**ממצא וקשר לדגלים:** familiar אינו משמר במפורש many. סוכנות המיליארדרים נשמרת בהקשר Their recipe; אין בסיס לקבוע היפוך תפקידים. הפיסוק בציטוט שונה.

**קריאה חוזרת:** בדיקה חוזרת מפרידה אובדן כמת אפשרי מטענת אובדן סוכנות שאינה נתמכת בהקשר.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** להכריע בכמת ובעוצמה; לרשום חריגת ציטוט בנפרד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "man"
    ],
    [
      "man."
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:415758

| Original | Style Rewrite |
|---|---|
| Washington's Democratic Party establishment keeps demanding that progressive members tone down their criticism of billionaire oligarchs and corporate autocrats. Why? Because the insiders want to rebrand the party as ideologically moderate. "Time to get serious," they bark. | Why does Washington's Democratic Party establishment keep demanding that its progressive members tone down their criticism of billionaire oligarchs and corporate autocrats? The insiders want to rebrand the party as ideologically moderate, that's why. "Time to get serious," they bark. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** הדרישה לרסן פרוגרסיבים והמניע למתג כמפלגה מתונה נשמרים. השאלה הועברה לחזית והציטוט נשמר; זה שינוי מבני אף אם proxy קטן.

**QC שמור:** passed=True; failed=none; similarity=0.9911389946937561; NLI forward/reverse=0.9966226816177368/0.9953259229660034; style substantial=False.

**הבדל ממוקד:** Why/Because → שאלת Why מקדימה ותשובה

**ממצא וקשר לדגלים:** אותן טענות וציטוט; עריכת מילים מתחת לסף אינה שוללת שינוי במבנה השיח. אין טענה שהסף חושב לא נכון.

**קריאה חוזרת:** נבדקו סדר ההסבר והקשר הסיבתי; אין שינוי תוכן מזוהה.

**סיווג אנליטי:** פער בין proxy לסגנון בקריאה

**המשך מומלץ:** הכרעה אנושית על שינוי סגנון משמעותי מול ארגון מקומי.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "time to get serious,"
    ],
    [
      "time to get serious,"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:422791

| Original | Style Rewrite |
|---|---|
| WASHINGTON — Sure, build a ballroom dwarfing the clean and classic design of the White House. Go ahead, murder the history of Lafayette Square with prison bars keeping tourists away from our traditional place of dissent. Close the John F. Kennedy Center for the Performing Arts since it will never be the same again, with your name spoiling the grandeur and memory of the slain president. | WASHINGTON — Go ahead and build a ballroom that dwarfs the White House's clean and classic design. Sure, murder the history of Lafayette Square by putting up prison bars that keep tourists away from our traditional place of dissent. And why not close the John F. Kennedy Center for the Performing Arts? With your name spoiling the grandeur and the memory of the slain president, it will never be the same again. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** since במקור קושר במפורש את הקריאה לסגירה לנזק הבלתי הפיך; השכתוב מציג שאלה רטורית ואחריה הטענה בלי הקשר הסיבתי המפורש. אותה סאטירה ונכסים נשמרים.

**QC שמור:** passed=False; failed=negation; similarity=0.9603050947189331; NLI forward/reverse=0.9478840827941895/0.8858208060264587; style substantial=True.

**הבדל ממוקד:** Close ... → why not close?; ההסבר על השם נשאר במשפט הבא

**ממצא וקשר לדגלים:** not נוסף בשאלה רטורית, לא הכחשה חדשה. ההנמקה לא נעלמה: היא מופיעה בצמידות למשפט הראשון.

**קריאה חוזרת:** החשש הקודם לאובדן סיבתיות נחלש בקריאת שני המשפטים יחד; נשמר אותו מהלך סרקסטי.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** לאמת כוח רטורי; לא להסיק drift מספירת not.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "never"
    ],
    [
      "not",
      "never"
    ]
  ],
  "future": [
    true,
    true
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [
      "murder"
    ],
    [
      "murder"
    ]
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:421279

| Original | Style Rewrite |
|---|---|
| You may wonder why President Donald Trump is doing everything he can, day by day, to destroy faith in democracy in little and large ways, on the job day and night. I have an answer that will presently be revealed. | You may be asking why President Donald Trump works day after day, in both small and large ways, to destroy faith in democracy. I have an answer, and I will reveal it shortly. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Borderline; Style=Yes.

**נימוק AI קודם:** נשמטו doing everything he can ו־day and night; day after day משמר התמדה אך לא בהכרח את עוצמת המאמץ הכוללת. הטענה על פגיעה באמון בדמוקרטיה והבטחת תשובה נשמרות.

**QC שמור:** passed=False; failed=bidirectional_nli; similarity=0.8639135360717773; NLI forward/reverse=0.9932460188865662/0.025474661961197853; style substantial=True.

**הבדל ממוקד:** doing everything he can ... on the job day and night → works day after day

**ממצא וקשר לדגלים:** נשמטו מאמץ מרבי ועבודה ביום ובלילה; כיוון ההאשמה נשמר אבל היקף ועוצמה נחלשים. NLI עשוי להיות רלוונטי להשמטה, אינו מסביר אותה בעצמו.

**קריאה חוזרת:** ההשמטה נותרת גם בהקשר המלא; זו הסתייגות חזקה יותר מן ה-Borderline הקודם, בלי לטעון היפוך נרטיב.

**סיווג אנליטי:** הבדל סמנטי מזוהה בקריאת AI

**המשך מומלץ:** הכרעה אנושית ממוקדת בהיקף ובעוצמה לפני כל קבלה.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    true,
    true
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [
      "may"
    ],
    [
      "may"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:416436

| Original | Style Rewrite |
|---|---|
| Socialism will always find an audience because it appeals to base envy and resentment. Ginning up a mob to be mad at "oligarchs," "Wall Street barons," "kulaks" or "billionaires" is cheap and easy. So, it was refreshing to hear Amazon founder Jeff Bezos, the fourth richest man on the planet, offer unadulterated praise of the moral and economic superiority of capitalism in his recent interview with CNBC's Andrew Ross Sorkin. | Socialism will always attract an audience because it appeals to base envy and resentment. It is cheap and easy to stir up a mob against "oligarchs," "Wall Street barons," "kulaks," or "billionaires." That is why it was refreshing to hear Amazon founder Jeff Bezos, the fourth richest man on the planet, offer unadulterated praise for the moral and economic superiority of capitalism in his recent interview with CNBC's Andrew Ross Sorkin. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** הנימוק נגד סוציאליזם, זילות גיוס ההמון, דירוג בזוס והשבח לקפיטליזם נשמרים. מבנה הגרונד הוחלף במשפט. פיסוק ציטוטי הכינויים השתנה בחלקו, ללא שינוי במילותיהם או בטענה.

**QC שמור:** passed=False; failed=quotations; similarity=0.9584630131721497; NLI forward/reverse=0.9939970970153809/0.985142171382904; style substantial=False.

**הבדל ממוקד:** kulaks → kulaks,; billionaires → billionaires. בתוך מרכאות

**ממצא וקשר לדגלים:** לא זוהה שינוי טענה; זה שינוי פיסוק פנימי בציטוט. תחת דרישת verbatim ה-guard רלוונטי, ולכן אין לכנותו false positive חוזי.

**קריאה חוזרת:** נבדקו גם סיבת המשיכה לסוציאליזם והשבח לקפיטליזם; התוכן נשמר בקריאת AI.

**סיווג אנליטי:** נאמנות ציטוט בלבד, ללא drift מזוהה

**המשך מומלץ:** לתעד fidelity ולבקש הכרעה אנושית נפרדת ממשמעות.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    true,
    true
  ],
  "quotations": [
    [
      "billionaires",
      "kulaks",
      "oligarchs,",
      "wall street barons,"
    ],
    [
      "billionaires.",
      "kulaks,",
      "oligarchs,",
      "wall street barons,"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:417610

| Original | Style Rewrite |
|---|---|
| Writer and philosopher Ayn Rand was often accused of inventing cartoonish villains. Rogues like Ellsworth Toohey in "The Fountainhead" would scheme to seize the global economy's commanding heights in pursuit of a distorted sense of justice. But the people who hold such ideas don't just appear in cartoons or in Rand's novels. | Cartoonish villains were something writer and philosopher Ayn Rand was often accused of inventing. Consider rogues such as Ellsworth Toohey in "The Fountainhead": driven by a distorted sense of justice, they would scheme to seize the commanding heights of the global economy. Yet people who hold ideas like these exist beyond cartoons and Rand's novels. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** האשמת ראנד, תיאור הנבלים והקביעה שיש אנשים כאלה מחוץ לספרות נשמרים. שלילה הומרה לחיוב שקול; מבנה המשפטים השתנה.

**QC שמור:** passed=False; failed=negation; similarity=0.8737914562225342; NLI forward/reverse=0.9958282113075256/0.9947795867919922; style substantial=True.

**הבדל ממוקד:** don't just appear in cartoons/novels → exist beyond ...

**ממצא וקשר לדגלים:** שני הניסוחים אומרים שהתופעה קיימת גם במציאות; מספר סמני שלילה אינו שווה לשלילת טענה.

**קריאה חוזרת:** נבדק תחום השלילה, לא רק היעלמות don't; אין הבדל תוכן מזוהה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** אין תיקון מוצדק על בסיס ספירה בלבד; אימות אנושי נותר נדרש.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't"
    ],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "the fountainhead"
    ],
    [
      "the fountainhead"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:118089

| Original | Style Rewrite |
|---|---|
| At first, Parker and Feldman tried to fly under the radar by issuing the subpoenas to the five pastors because they have association with Christian conservative activists who are rightly suing the city over its claim that they did not have a sufficient number of signatures to put a referendum on the ballot to repeal the equal rights ordinance. (They actually collected 50,000 signatures, though they needed only 17,259.) | By issuing subpoenas to five pastors, Parker and Feldman initially tried to fly under the radar. The pastors have associations with Christian conservative activists who are rightly suing the city over its claim that they lacked sufficient signatures to place a referendum on the ballot to repeal the equal rights ordinance. In fact, they collected 50,000 signatures when only 17,259 were required. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** because שקושר את הזימונים לקשרי הכמרים עם הפעילים נעשה שני משפטים סמוכים ללא סיבתיות מפורשת. מספרי החתימות, התביעה וההערכה rightly נשמרים.

**QC שמור:** passed=False; failed=negation; similarity=0.9296271204948425; NLI forward/reverse=0.9959568381309509/0.9954668283462524; style substantial=True.

**הבדל ממוקד:** subpoena ... because of association → אזכור השיוך במשפט נפרד; did not have enough → lacked sufficient

**ממצא וקשר לדגלים:** השלילה המילונית טכנית; לעומתה סיבת הזימון כבר אינה מפורשת באותה מידה. המספרים נשמרים.

**קריאה חוזרת:** הצמדת המשפטים אינה מבטיחה שכל קורא ייחס את אותה סיבת זימון; נשמר חשש סיבתי.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** לבדוק את הקשר הסיבתי; לא להסתפק בהסבר הטכני לדגל השלילה.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not"
    ],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "17,259",
      "50,000"
    ],
    [
      "17,259",
      "50,000"
    ]
  ]
}
```

</details>

## creators:419097

| Original | Style Rewrite |
|---|---|
| WASHINGTON — The Trump whirling dervish has come and gone to Turkey — to demand NATO hand over Greenland! — leaving a city exhausted by his wild Fourth of July displays. But first, it was so great to see legions of World Cup soccer fans all over the world, at all hours, cheering on their countries, especially the England and Mexico teams playing their hearts out. Cape Verde too. Yes, the pursuit of happiness was not just for us but for all across seams, seas and borders. Donald Trump hated to see so many people truly excited. | WASHINGTON — After his trip to Turkey, where he went to demand that NATO hand over Greenland!, the Trump whirling dervish has come and gone. Behind him is a city exhausted by his wild Fourth of July displays. But before all that, how great it was to see legions of World Cup soccer fans around the world cheering for their countries at every hour! The England and Mexico teams especially were playing their hearts out. Cape Verde too. Across seams, seas and borders, the pursuit of happiness belonged to everyone, not just us. And Donald Trump hated seeing so many people truly excited. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** But first עשוי להיות סדר הצגה; before all that מקבע סדר אירועים. הביקור, דרישת גרינלנד, האוהדים והביקורת נשמרים, אך אין להשלים כרונולוגיה מעבר למקור.

**QC שמור:** passed=True; failed=none; similarity=0.9548693299293518; NLI forward/reverse=0.9269350171089172/0.8569080829620361; style substantial=True.

**הבדל ממוקד:** But first → before all that

**ממצא וקשר לדגלים:** סדר שיח עשוי להפוך לסדר אירועים מפורש. QC עבר, אך אינו בודק את משמעות קישור הזמן.

**קריאה חוזרת:** גם בקריאה חוזרת אי אפשר לקבוע מהקטע לבדו אם זה סדר סיפור או כרונולוגיה.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** הכרעה אנושית על ציר הזמן, ללא חיפוש עובדות חיצוני.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not"
    ],
    [
      "not"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:416848

| Original | Style Rewrite |
|---|---|
| Democrats are again acting like they occupy the high moral ground of American politics. But if 2026 has proven anything, it's that there's virtually nothing a left-wing candidate could say or do that would elicit condemnation from Democrats if doing so threatened their power. | Once again, Democrats are behaving as though the high moral ground in American politics belongs to them. Yet if 2026 has demonstrated anything, it is this: virtually nothing a left-wing candidate might say or do would draw condemnation from Democrats when that condemnation would threaten their power. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** could→might עשוי להיות שקול, אך if...threatened→when...would threaten יכול להזיז תנאי היפותטי לכלל המנוסח בביטחון רב יותר. התוכן הביקורתי והטענה על הגנת כוח פוליטי נשמרים; אין בסיס ל־No ודאי.

**QC שמור:** passed=False; failed=certainty; similarity=0.9551817178726196; NLI forward/reverse=0.9926964044570923/0.9936128258705139; style substantial=True.

**הבדל ממוקד:** could say → might say; if ... threatened → when ... would threaten

**ממצא וקשר לדגלים:** could/might לבדם קרובים; if לעומת when עשוי להניח התרחשות במקום תנאי. דגל certainty אינו מנתח את תחום התנאי.

**קריאה חוזרת:** אי אפשר לייחס את כל הדגל להבדל מילוני ולסגור את המקרה; חשש ההנחה המוקדמת נשאר.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** לבדוק תנאי לעומת הנחת אירוע, לא רק פעלים מודאליים.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [
      "could"
    ],
    [
      "might"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "2026"
    ],
    [
      "2026"
    ]
  ]
}
```

</details>

## creators:296848

| Original | Style Rewrite |
|---|---|
| Perhaps I should start with a story. I first met Michael J. Fox in 2006, not long after Rush Limbaugh had mocked his involuntary movements caused by Parkinson's disease. Michael was in Ohio for a rally in support of stem cell research that could save countless lives. | Perhaps a story is where I should begin. My first meeting with Michael J. Fox was in 2006, shortly after Rush Limbaugh mocked the involuntary movements caused by Fox's Parkinson's disease. He had come to Ohio for a rally supporting stem cell research, research that could save countless lives. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** הפגישה הראשונה, השנה, המחלה, הלעג והרלי נשמרים; could לגבי הצלת חיים נותר. החזית, הכינוי והחזרה על research משנים ארגון.

**QC שמור:** passed=False; failed=negation; similarity=0.9364164471626282; NLI forward/reverse=0.9917661547660828/0.9966602325439453; style substantial=True.

**הבדל ממוקד:** not long after → shortly after

**ממצא וקשר לדגלים:** אותו מרווח זמן קצר. תבנית not אינה שלילת האירוע בהקשר זה.

**קריאה חוזרת:** נבדקו פרטי Michael Fox, השנה, המחלה והעצרת; אין שינוי מזוהה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** תיעוד דגל שלילה מילוני; אימות אנושי רגיל.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not"
    ],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [
      "could"
    ],
    [
      "could"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "2006"
    ],
    [
      "2006"
    ]
  ]
}
```

</details>

## creators:209914

| Original | Style Rewrite |
|---|---|
| President Donald Trump's pledge to "Make America Great Again" requires nothing less than reigniting economic growth and prosperity. Wealth creation is essential. As Congress pivots to tax reform — which is crucial to the wealth creation — the president could take matters into his own hands by issuing an executive order to index capital gains for inflation. | Reigniting economic growth and prosperity is nothing less than what President Donald Trump's pledge to "Make America Great Again" requires. That makes wealth creation essential. Congress is now pivoting to tax reform, a crucial part of creating that wealth. But the president could act on his own by issuing an executive order indexing capital gains for inflation. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** המקור מחבר באמצעות As בין פעולת הקונגרס לאפשרות הנשיא; השכתוב מוסיף But וממסגר ניגוד מפורש יותר. הפעולה המוצעת, מטרתה ו־could נשמרים; הטון הפרו־צמיחה זהה.

**QC שמור:** passed=True; failed=none; similarity=0.9160309433937073; NLI forward/reverse=0.9954491257667542/0.9948132038116455; style substantial=True.

**הבדל ממוקד:** take matters into his own hands → act on his own; הוספת But

**ממצא וקשר לדגלים:** עצמאות הפעולה כבר קיימת במקור. But מוסיף קישור שיח, לא תנאי או קשר סיבתי חדש מבוסס.

**קריאה חוזרת:** קריאה חוזרת אינה תומכת בקביעה שהניגוד כשלעצמו משנה את הצעת המדיניות.

**סיווג אנליטי:** הסתייגות AI קודמת לא נתמכת בקריאת ההקשר

**המשך מומלץ:** אפשר לסגור את הסתייגות ה-AI האנליטית, אך לא לסמן אימות אנושי.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "make america great again"
    ],
    [
      "make america great again"
    ]
  ],
  "CERT": [
    [
      "could"
    ],
    [
      "could"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:417661

| Original | Style Rewrite |
|---|---|
| Set aside, for a moment, that Maine Senate candidate Graham Platner spent years with a Nazi SS Totenkopf tattoo. Set aside that he blamed sexual assault victims for their predicament, that he called rural white Americans stupid racists, that he advocated political violence, that he mocked a wounded Purple Heart recipient, that he joked about the Virgin Mary being a "skank" and that he joined a hookup site while married. | For a moment, put aside the years Maine Senate candidate Graham Platner spent with a Nazi SS Totenkopf tattoo. Put aside, too, his blaming of sexual assault victims for their predicament, his description of rural white Americans as stupid racists and his advocacy of political violence. Then set aside his mockery of a wounded Purple Heart recipient, his joke that the Virgin Mary was a "skank" and his joining a hookup site while married. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** כל ההאשמות, המבצעים והציטוט נשמרים. שמות פעולה כגון his advocacy אינם הופכים כאן מעשה לתכנון; הפיצול והסדר הם שינוי סגנוני.

**QC שמור:** passed=False; failed=bidirectional_nli; similarity=0.9532029628753662; NLI forward/reverse=0.15832196176052094/0.9968484044075012; style substantial=True.

**הבדל ממוקד:** that he blamed/called/advocated ... → his blaming/description/advocacy ...

**ממצא וקשר לדגלים:** נומינליזציה של רשימת מעשים תוך שימור המבצע והפעולות. פער NLI חריף בין הכיוונים אינו הוכחה להשמטה.

**קריאה חוזרת:** נבדקו בנפרד כל האיברים ברשימה ותפקיד המבצע; לא זוהתה טענה חדשה או חסרה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** להראות לאדם את הרשימה המלאה; NLI כאן נראה אות מודלי לא ממוקד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "skank"
    ],
    [
      "skank"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [
      "victims"
    ],
    [
      "victims"
    ]
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:295188

| Original | Style Rewrite |
|---|---|
| Many of us are feeling a lot of excitement, buttressed by wave after wave of relief. We are a nation of survivors. On Inauguration Day, I felt hopeful watching Joe Biden and Kamala Harris take their oaths of office. They appeared to understand what we were asking of them and accepted without reservation. | Many of us feel a great deal of excitement, reinforced by repeated waves of relief. We are a nation of survivors. On Inauguration Day, I watched Joe Biden and Kamala Harris take their oaths of office and felt hopeful. They seemed to understand what we were asking of them, and they accepted it without reservation. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Borderline.

**נימוק AI קודם:** רבות מהיחידות נשארו כמעט זהות, עם synonyms ופיצול קל של watching...felt לצירוף פעלים. משמעות, הסתייגות appeared/seemed ועמדה נשמרות; עוצמת שינוי הסגנון מוגבלת.

**QC שמור:** passed=True; failed=none; similarity=0.964631199836731; NLI forward/reverse=0.9958578944206238/0.9925957322120667; style substantial=True.

**הבדל ממוקד:** watching ... I felt hopeful → I watched ... and felt hopeful

**ממצא וקשר לדגלים:** הרגש, הדוברים וההסתייגות seemed נשמרים; רוב הטקסט קרוב למקור.

**קריאה חוזרת:** אין בעיית משמעות מזוהה; עדיין לא ברור אם שינוי מקומי מספיק למטרת ההתערבות.

**סיווג אנליטי:** משמעות ללא שינוי מזוהה; סגנון מוגבל

**המשך מומלץ:** הכרעה אנושית על style; לא לשכתב שוב כדי לעבור QC.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "without"
    ],
    [
      "without"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:97c9d6b9ac1b

| Original | Style Rewrite |
|---|---|
| WASHINGTON — Something told me to get me over to East Potomac Park before Donald Trump destroyed it. Sure enough, I did, on a rainy Sunday morning, for a rally to protect the waterfront parkland from his axe. On the next weekend, he cut down 430 trees — for a fancy golf course, of course. He sneakily started on a Saturday morning on the three-day holiday weekend. | WASHINGTON — Something told me to get to East Potomac Park before Donald Trump destroyed it. So, on a rainy Sunday morning, I went to a rally aimed at protecting the waterfront parkland from his axe. The next weekend, he cut down 430 trees—for a fancy golf course, of course. He began sneakily, on a Saturday morning during the three-day holiday weekend. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Borderline.

**נימוק AI קודם:** רוב הפרטים והניסוחים נשארים, כולל430 עצים, בוקר ראשון והתחלה חשאית בשבת. המשפט על ההגעה להפגנה אורגן מחדש, אבל רוב הפסקה near-copy; Style Borderline אינו פסילה של משמעות.

**QC שמור:** passed=True; failed=none; similarity=0.9901853203773499; NLI forward/reverse=0.9927070736885071/0.9657853841781616; style substantial=False.

**הבדל ממוקד:** get me over → get to; משפט העצרת נוסח מחדש

**ממצא וקשר לדגלים:** 430 העצים, יום ראשון הגשום, הסודיות וסוף השבוע נשמרים; רוב הקטע כמעט זהה.

**קריאה חוזרת:** נבדקו גם fancy ו-sneakily; אין השמטה מזוהה. שאלת הסגנון נותרת.

**סיווג אנליטי:** משמעות ללא שינוי מזוהה; סגנון מוגבל

**המשך מומלץ:** בדיקת עוצמת התערבות, בלי לערבב עם preservation.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "430"
    ],
    [
      "430"
    ]
  ]
}
```

</details>

## creators:120177

| Original | Style Rewrite |
|---|---|
| Folks, our country is heading down a slippery slope. We have to stop it before it is too late. We haven't even hit Thanksgiving, and already the war on Christmas is underway. This time, one of the largest public school systems in the U.S. is eliminating every mention of religious holidays on its official calendar. | Folks, the country is moving down a slippery slope, and we have to stop it before it is too late. Thanksgiving has not even arrived, yet the war on Christmas is already underway. This time, one of the largest public school systems in the United States is removing every reference to religious holidays from its official calendar. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** החובה לעצור, לפני חג ההודיה, war on Christmas והמחיקה הכוללת נשמרים. איחוד שני משפטי הפתיחה וסידור פסוקית הזמן מייצרים שינוי מבני.

**QC שמור:** passed=False; failed=entities|attribution; similarity=0.9584868550300598; NLI forward/reverse=0.9894096851348877/0.9872943758964539; style substantial=True.

**הבדל ממוקד:** U.S. → United States

**ממצא וקשר לדגלים:** אותה מדינה; שינוי צורת ישות עשוי להפר את דרישת פני השטח בלי לשנות ישות. States מפעיל גם מילת attribution states אף שאינו פועל דיווח.

**קריאה חוזרת:** לא נוספה אמירה של גורם אחר. מדובר בכינוי ישות ובהומונים, לא בייחוס סמנטי חדש.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** להפריד אי-ציות לצורה המקורית משינוי משמעות; אימות אנושי נדרש.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't"
    ],
    [
      "not"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    [
      "states"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:208496

| Original | Style Rewrite |
|---|---|
| I participated in perhaps a bit of radio history last week when Steve Forbes and Art Laffer joined me on my syndicated radio show. It may have been the first time these supply-side economics giants were ever together over the airwaves. | Last week, when Steve Forbes and Art Laffer joined me on my syndicated radio show, I may have taken part in a little piece of radio history. Perhaps never before had these giants of supply-side economics appeared together over the airwaves. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** may have been the first time ו־Perhaps never before שומרים על השערה בדבר ההופעה המשותפת הראשונה. המשתתפים, המדיום והשבוע נשמרו; החזית והפיסוק שונו.

**QC שמור:** passed=False; failed=negation; similarity=0.9493361711502075; NLI forward/reverse=0.9963639378547668/0.994142472743988; style substantial=True.

**הבדל ממוקד:** may have been the first time ... ever → Perhaps never before ...

**ממצא וקשר לדגלים:** אותה השערת ראשוניות מסויגת של הופעה משותפת. never משנה ספירת שלילה אך אינו הופך את הטענה.

**קריאה חוזרת:** נבדקו יחד הסתייגות Perhaps והאירוע המשותף; אין ודאות חדשה מזוהה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** לתעד שינוי תחבירי עם שימור היקף ההשערה.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    [
      "never"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [
      "may"
    ],
    [
      "may"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:418904

| Original | Style Rewrite |
|---|---|
| "We didn't celebrate the Fourth of July," he told me. "For us, it was the day Vicksburg fell." Vicksburg, Mississippi, fell to Union troops on July 4, 1863. The Confederates surrendered, as was their habit. Long memories still mourn the Lost Cause of Black backs whipped bloody. | "We didn't celebrate the Fourth of July," he told me. "For us, it was the day Vicksburg fell." Vicksburg, Mississippi, fell to Union troops on July 4, 1863. The Confederates surrendered, as was their habit. Long memories continue to mourn the Lost Cause of Black backs whipped bloody. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=No.

**נימוק AI קודם:** הציטוטים וכל הטענות נשמרים, אך רק still mourn הומר ל־continue to mourn. אין שינוי משמעותי באופן ההבעה בפסקה כמכלול.

**QC שמור:** passed=True; failed=none; similarity=0.9990113973617554; NLI forward/reverse=0.9896774291992188/0.990048885345459; style substantial=False.

**הבדל ממוקד:** still mourn → continue to mourn

**ממצא וקשר לדגלים:** כמעט העתקה מלאה; כל הציטוטים והטענות נשמרים. חשש ברור לחוסר שינוי סגנוני, לא drift.

**קריאה חוזרת:** בדיקה חוזרת מאשרת שההחלפה המקומית היא עיקר השינוי.

**סיווג אנליטי:** משמעות ללא שינוי מזוהה; סגנון מוגבל

**המשך מומלץ:** אימות אנושי על style; אין בסיס להציג הצלחת intervention.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't"
    ],
    [
      "n't"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "for us, it was the day vicksburg fell.",
      "we didn't celebrate the fourth of july,"
    ],
    [
      "for us, it was the day vicksburg fell.",
      "we didn't celebrate the fourth of july,"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "1863",
      "4"
    ],
    [
      "1863",
      "4"
    ]
  ]
}
```

</details>

## creators:420299

| Original | Style Rewrite |
|---|---|
| A significant majority of Americans support voter identification laws. According to polls, not only Republicans but Democrats believe a voter should show ID before participating in an election. If you believe the country needs more secure elections, I hear you. But the popular contention that Republicans are going to lose their congressional majority in the next midterm elections because of a failure to pass the SAVE America Act is a partisan fantasy fueled by social media. | Voter identification laws have the support of a significant majority of Americans. Polls show that Democrats, not just Republicans, believe voters should present ID before taking part in an election. I hear you if you believe our elections need greater security. What I don't buy is the popular contention that failing to pass the SAVE America Act will cost Republicans their congressional majority in the next midterm elections. That's a partisan fantasy fueled by social media. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** going to lose because ו־will cost מופיעים שניהם בתוך אותה טענה עממית שהמספר דוחה במפורש. not just משמר not only...but. What I don't buy מלווה באותה קביעת partisan fantasy, ולכן לא זוהתה החמרה מהותית בוודאות או בסיבתיות.

**QC שמור:** passed=False; failed=negation|attribution|future_tense; similarity=0.9223640561103821; NLI forward/reverse=0.9954610466957092/0.9970539808273315; style substantial=True.

**הבדל ממוקד:** according to polls → Polls show; not only → not just; going to lose → will cost

**ממצא וקשר לדגלים:** הסקרים ממשיכים להיות המקור, והתחזית נשארת חלק מטענה מפלגתית שהמספר דוחה. ספירת שלילה ו-will אינן ניתוח scope.

**קריאה חוזרת:** נבדקה גם ההכחשה What I don't buy; היא משמרת את דחיית הפנטזיה, לא מוסיפה אמונה הפוכה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** בדיקת ייחוס ותחום ההכחשה בהקשר; הדגלים אינם ראיה להיפוך.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not"
    ],
    [
      "not",
      "n't"
    ]
  ],
  "future": [
    false,
    true
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [
      "according"
    ],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:115785

| Original | Style Rewrite |
|---|---|
| Last week, Hillary Clinton returned to Iowa for the first time since her 2008 presidential campaign loss, saying, "I'm back." She continued: "It's true. I've been thinking about it," referring to another run in 2016. But the truth is that even many of her esteemed liberal cronies think it's a bad idea. | For the first time since losing her 2008 presidential campaign, Hillary Clinton returned to Iowa last week. "I'm back," she announced, then went on to say, "It's true. I've been thinking about it," referring to another presidential run in 2016. The truth, however, is that even many among her esteemed liberal cronies consider it a bad idea. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** ההגעה, השנים, ההרהור בריצה נוספת וההערכה השלילית נשמרים. I'm back.→I'm back, מפר את שימור הפיסוק הפנימי, אך לא משנה כאן תוכן דיבור. יש לתעד fidelity בנפרד ממשמעות.

**QC שמור:** passed=False; failed=quotations; similarity=0.9880785942077637; NLI forward/reverse=0.9911404252052307/0.9883010983467102; style substantial=True.

**הבדל ממוקד:** I'm back. → I'm back, בתוך ציטוט

**ממצא וקשר לדגלים:** אותן מילים וכוונת חזרה; הפיסוק הפנימי שונה ולכן דרישת ציטוט מילולי לא מתקיימת.

**קריאה חוזרת:** לא זוהה שינוי תוכן נוסף בקריאה חוזרת.

**סיווג אנליטי:** נאמנות ציטוט בלבד, ללא drift מזוהה

**המשך מומלץ:** לתעד fidelity אמיתי בלי לתייגו כשינוי משמעות מוכח.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "i'm back.",
      "it's true. i've been thinking about it,"
    ],
    [
      "i'm back,",
      "it's true. i've been thinking about it,"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "2008",
      "2016"
    ],
    [
      "2008",
      "2016"
    ]
  ]
}
```

</details>

## creators:254aa595a403

| Original | Style Rewrite |
|---|---|
| I've got to hand it to Washington's Republican policymakers. They've come up with a truly remarkable way that, they promise, will vastly expand the number of small businesses in America. Great! This is personal for me, for I grew up in a family that had a Main Street business in small-town Texas, so I know how hard it is for little guys to battle the raw monopoly power of corporate chains. Thus, I cheered the GOP ... until I learned that their small business proposal is just another big business scam. | A truly remarkable promise has come from Washington's Republican policymakers: they've devised a way, they say, to vastly increase America's number of small businesses. Great! Having grown up in a family with a Main Street business in small-town Texas, I take this personally. I know just how hard the little guys have to fight against the raw monopoly power of corporate chains. So I was cheering the GOP ... right up until I discovered that its small business proposal was simply another big business scam. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** ההרחבה נשארת הבטחה המיוחסת לרפובליקנים, ולא עובדה מאומתת של המספר. המשפחה, הזדהות עם עסקים קטנים ותפנית scam נשמרות; סדר ההנמקה והזמנים הדיווחיים השתנה.

**QC שמור:** passed=False; failed=future_tense|similarity; similarity=0.8257997632026672; NLI forward/reverse=0.9954786896705627/0.9855132699012756; style substantial=True.

**הבדל ממוקד:** promise will vastly expand → promise ... they say to ... increase

**ממצא וקשר לדגלים:** ההרחבה נותרת תוכן הבטחה עתידית, לא עובדה. היעדר will ושינוי סדר מורידים אותות מילוניים ודמיון.

**קריאה חוזרת:** נבדקו מסגרת ההבטחה והסאטירה הפוליטית; לא זוהה מעבר מהבטחה לאירוע שהושלם.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** להפריד ציון similarity נמוך מאבחון drift; סקירה אנושית רגילה.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    true,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:422329

| Original | Style Rewrite |
|---|---|
| The U.S. national debt just crossed the $40 trillion threshold, doubling in less than a decade. Washington politicians have responded with their favorite fiscal game: blaming the other party. Democrats say Republican tax cuts are the culprit. Republicans say Democratic spending is the root cause. But both parties are responsible, with both hiding behind a lie of omission. And if we let them, they'll keep driving us into the same wall together. | The U.S. national debt has just moved past $40 trillion, having doubled in less than a decade. Washington's response has been its familiar fiscal game of blaming the other party. Democrats point to Republican tax cuts; Republicans point to Democratic spending. The reality is that both parties share responsibility, and both rely on the same lie of omission. If we allow it, they will keep steering us into the same wall together. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** both hiding behind a lie נעשה both rely on the same lie, שמזהה מפורשות את השקר של שניהם כאותו שקר. blame/root cause נהפך ל־point to; הקשר האשמה תומך בקריאה שקולה, אך הבהרת sameness אינה מפורשת במקור.

**QC שמור:** passed=True; failed=none; similarity=0.9613600969314575; NLI forward/reverse=0.9787391424179077/0.9487308263778687; style substantial=True.

**הבדל ממוקד:** both hiding behind a lie of omission → both rely on the same lie

**ממצא וקשר לדגלים:** same מבהיר זהות בין השקרים שלא בהכרח נטענה; culprit/root cause → point to יכול להחליש הסבר סיבתי.

**קריאה חוזרת:** המספרים והאחריות המשותפת נשמרים, אך ההיקף הקולקטיבי וההאשמה דורשים הכרעה.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** לשפוט same ועוצמת ייחוס הסיבה, בלי להתמקד רק בנתון החוב.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    true,
    true
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "40"
    ],
    [
      "40"
    ]
  ]
}
```

</details>

## creators:114783

| Original | Style Rewrite |
|---|---|
| We said on 9/11 that we'd "never forget." But when our president has a no-strategy strategy for stopping Islamic extremists, isn't Washington sidestepping our commitment of remembrance, in addition to its duty to protect our land and liberties? | On 9/11, we said that we'd "never forget." Yet when our president pursues a no-strategy strategy for stopping Islamic extremists, isn't Washington avoiding both our commitment to remembrance and its responsibility to protect our land and liberties? |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** has a no-strategy strategy הומר ל־pursues...strategy, ניסוח שמדגיש פעולה/בחירה של הנשיא במקום מצב. הציטוט, השלילה והביקורת נשמרים; השאלה אם ייחוס האקטיביות הוגבר.

**QC שמור:** passed=True; failed=none; similarity=0.9844287633895874; NLI forward/reverse=0.9934681057929993/0.9854896068572998; style substantial=False.

**הבדל ממוקד:** has a no-strategy strategy → pursues a no-strategy strategy

**ממצא וקשר לדגלים:** אסטרטגיה לעצירת קיצונים כבר מתארת מהלך מכוון; pursues אינו מוסיף בהכרח כוונה חדשה. never forget נשמר מילולית.

**קריאה חוזרת:** לא נמצא בסיס מספיק לייחס drift לסוכנות בלבד; הביקורת על וושינגטון נשמרת.

**סיווג אנליטי:** הסתייגות AI קודמת לא נתמכת בקריאת ההקשר

**המשך מומלץ:** אימות אנושי רגיל; הסתייגות AI קודמת נשמרת בנפרד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "never",
      "no",
      "n't"
    ],
    [
      "never",
      "no",
      "n't"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "never forget."
    ],
    [
      "never forget."
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [
      "said"
    ],
    [
      "said"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "11",
      "9"
    ],
    [
      "11",
      "9"
    ]
  ]
}
```

</details>

## creators:421951

| Original | Style Rewrite |
|---|---|
| Way back there in the 1700s and the 1800s, the British conquered a big chunk of the world thanks to their navy, which was crewed by whip-scarred, toothless, unwilling sailors with untreated syphilis. That's who you want to fight your wars. No one fights like mistreated men living on a diet of garbage, the lash and below-decks rape. | Back in the 1700s and 1800s, Britain conquered a large part of the world with a navy crewed by unwilling, toothless sailors scarred by the whip and suffering from untreated syphilis. Those are the men you want fighting your wars. Few people fight like men who are mistreated, fed garbage, lashed, and subjected to rape below decks. |

**קודם:** ai_substantial_semantic_concern; Meaning=No; Narrative=Borderline; Style=Yes.

**נימוק AI קודם:** No one fights like הוחלף ב־Few people fight like: טענת ייחוד מוחלטת נחלשה לחריגות יחסית. תפקידי המלחים נשמרים, אך ההפרזה הסאטירית נחלשת. אין לתקן No/ Few בטקסט הקפוא.

**QC שמור:** passed=False; failed=entities|negation; similarity=0.904212474822998; NLI forward/reverse=0.9953415393829346/0.9939901828765869; style substantial=True.

**הבדל ממוקד:** No one fights like ... → Few people fight like ...

**ממצא וקשר לדגלים:** אין אף אחד הוחלף במעטים: הכללה מוחלטת נחלשת ונפגעת העוצמה. British/Britain יכול להסביר דגל ישויות אך אינו השינוי העיקרי.

**קריאה חוזרת:** תפקיד הלוחמים נשמר: fighting your wars, ללא היפוך משתתפים. הבדל הכמת נשאר מפורש.

**סיווג אנליטי:** הבדל סמנטי מזוהה בקריאת AI

**המשך מומלץ:** הכרעה אנושית על כמת ועוצמה; לא להסביר את כל הפסילה בכינוי מדינה.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "no"
    ],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:421367

| Original | Style Rewrite |
|---|---|
| You couldn't find a wackier candidate than Francesca Hong, the Democratic Socialist vying to become the governor of Wisconsin. She wanted to defund police and abolish ICE, topping it all off with a call to end Thanksgiving. "Saturday Night Live" couldn't have made her up. | Francesca Hong, the Democratic Socialist running for governor of Wisconsin, would be hard to beat for sheer wackiness as a candidate. Defunding the police and abolishing ICE were among her aims, and she topped them off by calling for an end to Thanksgiving. Even "Saturday Night Live" couldn't have invented her. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Borderline; Style=Yes.

**נימוק AI קודם:** couldn't find a wackier הוא ניסוח מוחלט יותר מ־hard to beat, גם בתוספת sheer. הלעג והעמדות נשמרים, אך עוצמתו עשויה להיחלש. all ב־topping it all off הוא חלק מביטוי, לא ראיה בפני עצמה לאובדן כמת.

**QC שמור:** passed=False; failed=negation|similarity; similarity=0.813119113445282; NLI forward/reverse=0.9919984936714172/0.9863828420639038; style substantial=True.

**הבדל ממוקד:** couldn't find wackier → hard to beat for wackiness

**ממצא וקשר לדגלים:** שלילה מוחלטת של חלופה עשויה להפוך לקושי השוואתי בלבד; הניב topping it all off אינו ספירת אוכלוסייה.

**קריאה חוזרת:** רוב הלעג נשמר אבל הדרגה ההשוואתית אינה שקולה בהכרח; נשאר חשש עוצמה.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** לבדוק מוחלטות והשוואה; similarity אינו אבחון מדויק לכך.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't",
      "n't"
    ],
    [
      "n't"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "saturday night live"
    ],
    [
      "saturday night live"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:418022

| Original | Style Rewrite |
|---|---|
| Why didn't President Donald Trump initially want to share the full text of the framework agreement between the United States and the Islamic Republic of Iran? The first reason is obvious: The memorandum of understanding is a capitulation to the clerics of the regime. | Why was President Donald Trump initially unwilling to share the full text of the framework agreement between the United States and the Islamic Republic of Iran? There's an obvious first reason: the memorandum of understanding amounts to a capitulation to the regime's clerics. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Borderline.

**נימוק AI קודם:** unwilling ו־didn't want משמרים כאן את רתיעת השיתוף; capitulation והסיבה הברורה נשמרות. השינויים מצומצמים לשני מבנים דומים, ולכן Style Borderline.

**QC שמור:** passed=False; failed=negation; similarity=0.9906279444694519; NLI forward/reverse=0.9965336322784424/0.9879139065742493; style substantial=True.

**הבדל ממוקד:** didn't want → unwilling

**ממצא וקשר לדגלים:** שלילה מובלעת בתואר משמרת סירוב, אך שינוי הסגנון מוגבל. דגל השלילה נראה מילוני.

**קריאה חוזרת:** נבדקו הדרישה להסכמה ותיאור הכניעה; אין שינוי תוכן מזוהה.

**סיווג אנליטי:** משמעות ללא שינוי מזוהה; סגנון מוגבל

**המשך מומלץ:** הכרעה אנושית על style לצד תיעוד false alarm סמנטי אפשרי.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't"
    ],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [
      "states"
    ],
    [
      "states"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:423545

| Original | Style Rewrite |
|---|---|
| Greg Abbott, the right-wing hack who is governor of Texas, probably doesn't know what a "petard" is, but he's now been hoisted by a big one. "Hoist on a petard" is a Shakespearean phrase for a bomb maker being blown sky-high by his own creation. | Texas Gov. Greg Abbott, the right-wing hack, probably does not know what a "petard" is, but he has now been hoisted by a big one. "Hoist on a petard" is a Shakespearean phrase describing a bomb maker being blown sky-high by his own creation. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Borderline.

**נימוק AI קודם:** הכינוי החריף, probably, המטאפורה והגדרתה נשמרים. שינוי שם התפקיד לחזית והרחבת contractions מוגבלים יחסית, ורוב הניסוח מועתק.

**QC שמור:** passed=True; failed=none; similarity=0.9864144325256348; NLI forward/reverse=0.9937022924423218/0.9969112277030945; style substantial=True.

**הבדל ממוקד:** Greg Abbott ... governor → Texas Gov. Greg Abbott

**ממצא וקשר לדגלים:** right-wing hack, probably ומטאפורת הפצצה נשמרים. שינוי פתיחה וכיווצים בלבד עשוי להיות קטן.

**קריאה חוזרת:** החשש הקודם להחלשת stance בגרסאות אחרות אינו מועתק לגרסה זו; כאן הגינוי נשמר.

**סיווג אנליטי:** משמעות ללא שינוי מזוהה; סגנון מוגבל

**המשך מומלץ:** בדיקת סגנון בלבד לפי הזוג הנוכחי.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't"
    ],
    [
      "not"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "hoist on a petard",
      "petard"
    ],
    [
      "hoist on a petard",
      "petard"
    ]
  ],
  "CERT": [
    [
      "probably"
    ],
    [
      "probably"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:416624

| Original | Style Rewrite |
|---|---|
| Here in Washington, D.C., we endure slights of the president's barking, his constant use of capital letters and his ever-present red ties. These are forms of shouting, weapons of psychological warfare that he wields as the master of repetition. Then there's the 250-foot Arch he plans to build, which would block the view across Arlington Cemetery to the Lincoln Memorial shrine to freedom. | Here in Washington, D.C., we endure the president's barking, his ever-present red ties and his constant use of capital letters. Each is a form of shouting, part of the psychological warfare he wages as a master of repetition. And now he plans a 250-foot Arch that would obstruct the view from across Arlington Cemetery to the Lincoln Memorial shrine to freedom. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** view across Arlington Cemetery הומר ל־view from across Arlington Cemetery, שעשוי להזיז את נקודת התצפית. שאר תיאור הלוחמה הפסיכולוגית, הגובה והיעד נשמרים.

**QC שמור:** passed=True; failed=none; similarity=0.9780654907226562; NLI forward/reverse=0.9834461808204651/0.9282577633857727; style substantial=True.

**הבדל ממוקד:** view across Arlington Cemetery to ... → view from across ...

**ממצא וקשר לדגלים:** from עלול לשנות נקודת תצפית לעומת נתיב מבט. יתר נתוני הגובה וההאשמה נשמרים.

**קריאה חוזרת:** הקטע לבדו אינו פותר את העמימות המרחבית; אין להסיק ממעבר ישויות שהיחס נשמר.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** הכרעה אנושית על יחסים מרחביים, בלי ידע חיצוני.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [
      "freedom"
    ],
    [
      "freedom"
    ]
  ],
  "numbers": [
    [
      "250"
    ],
    [
      "250"
    ]
  ]
}
```

</details>

## creators:420447

| Original | Style Rewrite |
|---|---|
| Does becoming a billionaire turn one into an insufferable jerk, or is that an innate quality they bring to the position? Big-name billionaires — Musk, Bezos and Zuckerberg — literally flaunt their irrepressible jerkism, but the disease seems to inflict their entire class of uber-rich corporate royals. Its telltale symptoms are not their grandiose mansions and yachts, but their sudden impulse to instruct us regular people on how to think. In particular, they're now demanding that we get out of their way so they can remake society in their image. | Is being an insufferable jerk something billionaires become, or is it an innate quality they arrive with? Musk, Bezos and Zuckerberg are big-name billionaires who literally flaunt an irrepressible jerkism. But this disease appears to afflict the whole class of uber-rich corporate royals. You won't recognize its telltale symptoms in their grandiose yachts or mansions. Rather, look for the sudden urge to tell us regular people how we ought to think. Now, in particular, they're demanding that we step aside while they remake society in their own image. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** step aside while they remake עשוי למסגר חפיפה לפעולה המתרחשת, לעומת get out...so they can remake המציג תכלית/יכולת. מאחר ששניהם תחת demanding אין ודאות לפער עובדתי מלא; הביקורת והמיליארדרים נשמרים.

**QC שמור:** passed=False; failed=future_tense; similarity=0.9545873999595642; NLI forward/reverse=0.9928575754165649/0.9861570596694946; style substantial=True.

**הבדל ממוקד:** get out ... so they can remake → step aside while they remake; You won't recognize

**ממצא וקשר לדגלים:** שני התיאורים בתוך דרישה לתרחיש, לא קביעה שההשתלטות כבר קרתה. will מופיע בפנייה לקורא ולא באותה טענה.

**קריאה חוזרת:** חשש ה-AI הקודם להתרחשות בפועל אינו נתמך בהקשר demanding; דגל העתיד אינו מאבחן זאת.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** להראות לאדם את מסגרת הדרישה; לא לפרש while כאירוע שהושלם.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not"
    ],
    [
      "n't"
    ]
  ],
  "future": [
    false,
    true
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:459e183c1d0d

| Original | Style Rewrite |
|---|---|
| French economist Gabriel Zucman has come to California bearing a familiar French solution to a fiscal problem: another tax. Once based at the University of California, Berkeley, Zucman is back and campaigning for Proposition 40, which would impose an allegedly one-time 5% tax on the net worth of Californians worth more than $1 billion. Zucman, who coauthored the proposition, estimates that the tax could raise about $100 billion and claims that 90% of the proceeds would go to health care. | French economist Gabriel Zucman has returned to California with a familiar French answer to a fiscal problem: another tax. Formerly based at the University of California, Berkeley, Zucman is now campaigning for Proposition 40, which would impose an allegedly one-time 5% tax on the net worth of Californians worth more than $1 billion. Zucman, who coauthored the proposition, estimates that the tax could raise about $100 billion and claims that 90% of the proceeds would go to health care. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=No.

**נימוק AI קודם:** המספרים, net worth, allegedly one-time, estimates/claims וכל תנאי המס נשמרים. רק כמה מילים וחזיתות קלות בשני משפטים משתנות; יתר הפסקה כמעט זהה ולכן אין style change ניכר.

**QC שמור:** passed=True; failed=none; similarity=0.9962499141693115; NLI forward/reverse=0.9914552569389343/0.9920510649681091; style substantial=False.

**הבדל ממוקד:** bearing ... solution → returned ... with ... answer

**ממצא וקשר לדגלים:** פרטי המס, net worth, allegedly, estimates ו-claims נשמרים; רוב הקטע מועתק.

**קריאה חוזרת:** אין שיפור סגנוני רחב מזוהה למרות מעבר preservation.

**סיווג אנליטי:** משמעות ללא שינוי מזוהה; סגנון מוגבל

**המשך מומלץ:** אימות אנושי על style; לא להכריז הצלחה משולבת.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [
      "allegedly",
      "could"
    ],
    [
      "allegedly",
      "could"
    ]
  ],
  "ATTR": [
    [
      "claims"
    ],
    [
      "claims"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "1",
      "100",
      "40",
      "5",
      "90"
    ],
    [
      "1",
      "100",
      "40",
      "5",
      "90"
    ]
  ]
}
```

</details>

## creators:120669

| Original | Style Rewrite |
|---|---|
| Last week, when "Fox & Friends" highlighted my most recent column, titled "Neutering Religious Holidays," liberals came out of the woodwork to try to defend President Barack Obama's record. So I decided to do a little research and see just how spiritual his past Thanksgiving addresses have been and compare them with the thoughts of our founding president, George Washington. | Last week, "Fox & Friends" featured my latest column, "Neutering Religious Holidays," and liberals quickly came out to defend President Barack Obama's record. That prompted me to do some research: I wanted to see how spiritual Obama's past Thanksgiving addresses had been and compare them with the thoughts of our founding president, George Washington. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** הייחוס של Thanksgiving addresses מפורש נכון לאובמה, ולא לוושינגטון. came out of the woodwork נעשה quickly came out: רמז להופעה בלתי צפויה/מרובה הוחלף במהירות. הספק מוגבל לניואנס הרטורי; כל ההשוואה והציטוטים נשמרים.

**QC שמור:** passed=True; failed=none; similarity=0.9714114665985107; NLI forward/reverse=0.9910570383071899/0.987583577632904; style substantial=True.

**הבדל ממוקד:** came out of the woodwork → quickly came out

**ממצא וקשר לדגלים:** הפניה ל-Obama תקינה והשוואת Washington נשמרת. הניב על הופעה לא צפויה/מרובה מוחלף במהירות.

**קריאה חוזרת:** כשל Obama/Washington היסטורי אינו קיים כאן; נותר רק סיכון רטורי מקומי.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** לבדוק עוצמת הניב לעומת quickly, לא לייחס כשל מגרסה אחרת.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "fox & friends",
      "neutering religious holidays,"
    ],
    [
      "fox & friends",
      "neutering religious holidays,"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:418916

| Original | Style Rewrite |
|---|---|
| One of the most popular complaints of the younger Americans is that the United States has been bogged down in endless war and interventionism virtually their entire lifetimes. Welcome to history. As much as we may not like it, the United States has engaged in conflict and meddling more or less since its inception. The U.S. was born in war. It expanded through war. It freed its slaves through war. It grew into a superpower through war. And until utopia exists, it's exceedingly likely we will need to clash with those who threaten our prestige and power. | Younger Americans often complain that the United States has spent virtually their whole lives bogged down in endless war and interventionism. It's one of their most popular complaints. Well, welcome to history. Whether we like it or not, conflict and meddling have been part of the United States more or less from its inception. War was how the U.S. was born, how it expanded and how it freed its slaves. Through war, it also became a superpower. And until utopia exists, the likelihood that we will need to clash with those threatening our prestige and power remains exceedingly high. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** שתי גרסאות ההסתייגות מן המלחמה הן ויתור רטורי, לא קביעה עובדתית שונה על דעת הקורא. כל הדוגמאות נשמרות ו־exceedingly likely נשמר כ־likelihood...exceedingly high. איחוד חזרת through war משנה קצב אך לא בהכרח מחליש את העמדה.

**QC שמור:** passed=False; failed=certainty; similarity=0.9792590141296387; NLI forward/reverse=0.9958875775337219/0.9974143505096436; style substantial=True.

**הבדל ממוקד:** as much as we may not like it → whether we like it or not

**ממצא וקשר לדגלים:** may נעלם בהבעת הסתייגות רטורית, אך exceedingly likely נשמר כ-likelihood ... exceedingly high בטענה עצמה.

**קריאה חוזרת:** נבדקו בנפרד רגש הקורא ותחזית האירוע; לא נמצא חיזוק ודאות בטענה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** לתעד תחום מודאליות; אין להסיק certainty drift מהיעלמות may בלבד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not"
    ],
    [
      "not"
    ]
  ],
  "future": [
    true,
    true
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [
      "may"
    ],
    []
  ],
  "ATTR": [
    [
      "states"
    ],
    [
      "states"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:423650

| Original | Style Rewrite |
|---|---|
| Inflation hasn't gone away — it's going up. With the midterm elections seven weeks off, that's a problem for the president and Congress. Voters hate inflation. They don't much like the cure either, and the cure has two parts. The Federal Reserve raising interest rates, like it just did, is one. The second part is overlooked and in the hands of Congress. Indeed, the Fed can't bring inflation down for good unless lawmakers show they will back the debt with future fiscal surpluses. That means becoming serious about overspending. | Inflation is going up, not going away. For the president and Congress, that's a problem with the midterm elections only seven weeks off. Voters hate inflation, but they're not particularly fond of its cure either. That cure has two parts. One is the Federal Reserve's raising of interest rates, as it just did. The other, often overlooked, rests with Congress: unless lawmakers demonstrate that future fiscal surpluses will back the debt, the Fed cannot bring inflation down for good. In other words, Congress must get serious about overspending. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Borderline; Style=Yes.

**נימוק AI קודם:** only seven weeks מוסיף הדגשת דחיפות. Congress must מפורש וחזק יותר מן הסיכום That means becoming serious, אף שההקשר כבר דורש שינוי פיסקלי. תנאי unless וטענות הפד נשמרים; הספק הוא בעוצמת החובה והטון, לא שינוי מספרי.

**QC שמור:** passed=False; failed=certainty; similarity=0.9618841409683228; NLI forward/reverse=0.9870894551277161/0.9916099905967712; style substantial=True.

**הבדל ממוקד:** seven weeks → only seven weeks; getting serious → Congress must ...

**ממצא וקשר לדגלים:** only מוסיף דחיפות ו-must הופך קריאה להצהרת חובה מפורשת יותר. certainty guard רלוונטי אך אינו מדרג עוצמה.

**קריאה חוזרת:** אין טענה שהמספר השתנה; החשש הוא דגש וחובה, לא תוכן כמותי שונה.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** הכרעה אנושית על חובה ועוצמה, בנפרד משימור עובדות.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't",
      "n't",
      "n't"
    ],
    [
      "not",
      "not",
      "cannot"
    ]
  ],
  "future": [
    true,
    true
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    [
      "must"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:420909

| Original | Style Rewrite |
|---|---|
| Not that it matters, but sometimes I wonder if the billionaire potentates of artificial intelligence ever wonder why they've become so despised. I doubt it, since introspection doesn't seem to be in the DNA of hubristic AI demigods like Bezos, Musk and Zuckerberg. Nor are they programming such qualities into their "superintelligent bots." | Sometimes I wonder why the billionaire potentates of artificial intelligence have become so despised, and whether they ever wonder about it themselves. Not that it matters. I doubt they do: introspection hardly seems written into the DNA of hubristic AI demigods such as Bezos, Musk and Zuckerberg. And such qualities aren't being programmed into their "superintelligent bots," either. |

**קודם:** ai_substantial_semantic_concern; Meaning=No; Narrative=Borderline; Style=Yes.

**נימוק AI קודם:** המקור תוהה אם המיליארדרים שואלים מדוע שונאים אותם. השכתוב מוסיף שהמספר עצמו תוהה מדוע, ורק אז האם גם הם תוהים. זה שינוי במושא הספק ובייחוס השאלה, אף שהמשך הביקורת על חוסר introspection נשמר.

**QC שמור:** passed=False; failed=negation|quotations; similarity=0.9442423582077026; NLI forward/reverse=0.9864950180053711/0.9975368976593018; style substantial=True.

**הבדל ממוקד:** I wonder if billionaires wonder why ... → I wonder why ... and whether they wonder

**ממצא וקשר לדגלים:** נוספה תהייה של המספר עצמו על סיבת השנאה, במקום רק תהייה אם המיליארדרים תוהים. זה שינוי בעל עמדה/scope.

**קריאה חוזרת:** הבדל נושא התהייה נשאר גם בקריאה חוזרת; דגלי שלילה וציטוט אינם אבחון ישיר של בעל המחשבה.

**סיווג אנליטי:** הבדל סמנטי מזוהה בקריאת AI

**המשך מומלץ:** הכרעה אנושית ממוקדת בייחוס מחשבה; לתעד גם פיסוק ציטוט בנפרד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not",
      "n't",
      "nor"
    ],
    [
      "not",
      "n't"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "superintelligent bots."
    ],
    [
      "superintelligent bots,"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:419062

| Original | Style Rewrite |
|---|---|
| From Q-Anon nuttiness to JD Vance's "Deep State" quackery, wacko right-wing conspiracies have oozed into the center of Republican politics. But don't let their goofiness obscure the fact that there is indeed a very real plot to rig America's economic and political system, causing wealth and power to flow uphill — from the workaday majority to moneyed elites. | Q-Anon nuttiness and JD Vance's "Deep State" quackery are examples of wacko right-wing conspiracies that have moved into the center of Republican politics. Their silliness should not hide a different reality: there is, in fact, a very real plot to rig America's political and economic system so that wealth and power move uphill, away from the workaday majority and toward moneyed elites. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** oozed into הוא דימוי שלילי מוחשי שנעשה moved into ניטרלי יותר. שאר כינויי nuttiness/quackery/wacko והעלילה הכלכלית נשמרים; הספק נוגע לדימוי ולעוצמה המקומית, לא לכיוון העמדה.

**QC שמור:** passed=True; failed=none; similarity=0.9114111661911011; NLI forward/reverse=0.9974294304847717/0.9940900206565857; style substantial=True.

**הבדל ממוקד:** oozed into → moved into

**ממצא וקשר לדגלים:** מטאפורה דוחה מוחלפת בתנועה ניטרלית; יתר nuttiness/quackery/wacko והאשמת המזימה נשמרים.

**קריאה חוזרת:** אין היפוך עמדה, אבל רמת הגועל המקומית עשויה להיחלש; נשאר Borderline.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** לשפוט עוצמה מטאפורית, לא להניח שכל synonym בטוח.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't"
    ],
    [
      "not"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "deep state"
    ],
    [
      "deep state"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:296082

| Original | Style Rewrite |
|---|---|
| I beg your pardon. Wrong decade. When Marjorie Taylor Greene was in her mid-40s, she clicked "like" on a Facebook post calling for House Speaker Nancy Pelosi to be shot in the head. She liked comments about executing FBI agents as "deep state" operators trying to undermine former President Donald Trump. She promoted the conspiracy theory that a passenger plane never flew into the Pentagon during the 9/11 attacks. | Wrong decade — I beg your pardon. In her mid-40s, Marjorie Taylor Greene clicked "like" on a Facebook post that called for House Speaker Nancy Pelosi to be shot in the head. Comments urging the execution of FBI agents as "deep state" operators seeking to undermine former President Donald Trump also received her likes. And she promoted the conspiracy theory denying that a passenger plane had flown into the Pentagon during the 9/11 attacks. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** comments about executing הפך ל־comments urging the execution: urging מייחס תוכן של קריאה למעשה במפורש, ולא רק דיון בנושא. תיאור הקונספירציה ממשיך להיות מיוחס לגרין ואינו מוצג כאמת של המספר. כיוון הביקורת נשמר.

**QC שמור:** passed=False; failed=negation|similarity; similarity=0.8204799294471741; NLI forward/reverse=0.9705525636672974/0.9302313923835754; style substantial=True.

**הבדל ממוקד:** never ... plane flew → theory denying ...; comments about executing → comments urging execution

**ממצא וקשר לדגלים:** denying משמר שלילה תחת ייחוס תיאוריית קונספירציה. urging מייחס תמיכה בביצוע, מעבר לאזכור about.

**קריאה חוזרת:** הסבר טכני לשלילה אינו פותר את שינוי אפיון האמירה; נותר חשש ייחוס/עמדה.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** הכרעה אנושית על about לעומת urging; לא לפסול רק בגלל never.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "never"
    ],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "deep state",
      "like"
    ],
    [
      "deep state",
      "like"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "11",
      "9"
    ],
    [
      "11",
      "9"
    ]
  ]
}
```

</details>

## creators:118606

| Original | Style Rewrite |
|---|---|
| First, the mayor of Houston flagrantly violated clergy's First Amendment rights, when she subpoenaed sermons, and she still refuses to rescind her mandate. And now California government officials are forcing churches and other faith-based organizations to fund abortions. What's next? | The mayor of Houston first flagrantly violated clergy's First Amendment rights by subpoenaing sermons, and she continues to refuse to rescind her mandate. Now California government officials are forcing churches and other faith-based organizations to fund abortions. What's next? |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Borderline.

**נימוק AI קודם:** הפרת הזכויות, הזימון, סירוב הביטול וכפיית המימון נשמרים. first...now שומר על הרצף; השינויים קטנים ורוב שתי הטענות כמעט מועתק.

**QC שמור:** passed=True; failed=none; similarity=0.9690207242965698; NLI forward/reverse=0.9969883561134338/0.9980672001838684; style substantial=True.

**הבדל ממוקד:** שינוי מיקום מילת זמן וקישור בין שתי טענות church/state

**ממצא וקשר לדגלים:** רוב הטקסט זהה והמסגור נשמר; שינוי סגנוני מוגבל.

**קריאה חוזרת:** לא נמצאה תוספת טענה בקריאה חוזרת; שאלת חוזק ההתערבות נשארת.

**סיווג אנליטי:** משמעות ללא שינוי מזוהה; סגנון מוגבל

**המשך מומלץ:** אימות אנושי על style, בלי ניסיון הגברה אוטומטי.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:298495

| Original | Style Rewrite |
|---|---|
| After I first started writing a column, in the fall of 2002, it wasn't long before I heard regularly from those who brandished God as a weapon in opposing LGBTQ rights. This was not surprising. Back then, I was on staff at The Plain Dealer in Cleveland, and I was long familiar with the bigotry in my home state. Most of the hate mail came from strangers, but I got my share of lectures from blood relatives, too. Few things anger right-wing Christians more than a family member insisting she's acquainted with a different version of God. | Not long after I began writing a column in the fall of 2002, I started hearing regularly from people who used God as a weapon against LGBTQ rights. That did not surprise me. At the time, I worked at The Plain Dealer in Cleveland and was already very familiar with the bigotry in my home state. Most of the hate mail came from strangers, though blood relatives also gave me their share of lectures. Few things anger right-wing Christians more than a family member insisting that she knows a different version of God. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** strangers ו־blood relatives נשמרים, בלי המצאת anonymous sources. long familiar הומר ל־already very familiar: היכרות ממושכת הופכת לדגש על עוצמת ההיכרות. שאר הרצף והמסגור נשמרים; זה ספק ממוקד, לא כשל עובדתי ברור.

**QC שמור:** passed=True; failed=none; similarity=0.9747574925422668; NLI forward/reverse=0.9965535402297974/0.9917067289352417; style substantial=True.

**הבדל ממוקד:** long familiar → already very familiar

**ממצא וקשר לדגלים:** משך היכרות מומר בדרגה; already משמר קודמות אך לא משך. strangers ובני משפחה נשמרים, אין anonymous sources כאן.

**קריאה חוזרת:** אין להעתיק כשל עובדתי מ-v2/v3. ההסתייגות הנוכחית מצומצמת למשך לעומת עוצמה.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** להכריע בהיקף השינוי בתואר, לפי גרסה זו בלבד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't",
      "not"
    ],
    [
      "not",
      "not"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "2002"
    ],
    [
      "2002"
    ]
  ]
}
```

</details>

## creators:423635

| Original | Style Rewrite |
|---|---|
| Go ahead, President Donald Trump, keep the Kennedy Center closed. Don't give it money for necessary repairs. This is low-hanging fruit for Americans done with your extortion schemes. They don't have to submit to small-bore intimidation like this. They can just shrug at the demand that your name, with words of gratitude, be placed on the building's facade. To use a different metaphor, they have bigger fish to fry. | President Donald Trump, go ahead and keep the Kennedy Center closed, withholding money for the repairs it needs. For Americans fed up with your extortion schemes, this is low-hanging fruit: there's no need for them to submit to such small-bore intimidation. They can simply shrug off the demand to put your name on the building's facade along with words of gratitude. Or, to switch metaphors, they have bigger fish to fry. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** withholding money ממשיך את הקריאה הסרקסטית ולא מציג כשלעצמו אירוע חדש. הזכות לא להיכנע, דרישת השם ומטאפורות הפירות/דגים נשמרות; המשפטים חוברו ואורגנו מחדש.

**QC שמור:** passed=False; failed=negation; similarity=0.9534748792648315; NLI forward/reverse=0.9936158657073975/0.9962618947029114; style substantial=True.

**הבדל ממוקד:** don't give it money → withholding money; don't have to submit → no need to submit

**ממצא וקשר לדגלים:** שלילה והיעדר חובה נשמרים בהקשר הסרקסטי; הספירה משתנה בגלל נומינליזציה וניסוח מודאלי.

**קריאה חוזרת:** נבדקו דרישת הכסף ומטאפורת הסחיטה; לא נמצאה עמדה הפוכה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** בדיקת scope אנושית רגילה; לא לתקן בגלל ספירה בלבד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't",
      "n't"
    ],
    [
      "no"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:416232

| Original | Style Rewrite |
|---|---|
| Are we almost at the point of no return? Let America be America again, please, in a post-Donald Trump world. Rebuilding our institutions, arts and trust in government is not a sure thing. Given a global economic, environmental or medical crisis, the endeavor could cross country boundaries, as natural historian David Attenborough said, in "an international ambition for survival." | Are we nearing the point of no return? Please, in a post-Donald Trump world, let America be America again. There is no guarantee that we can rebuild our institutions, arts and trust in government. And if a global economic, environmental or medical crisis arises, that rebuilding endeavor could reach across country boundaries, becoming, as natural historian David Attenborough said, "an international ambition for survival." |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** almost at→nearing אינו מבטא בדיוק אותה קרבה. becoming an international ambition מחבר את המאמץ למטאפורה באופן מפורש יותר מאשר in an international ambition. הספק מקומי; חוסר הוודאות בשיקום והתנאי למשבר נשמרים.

**QC שמור:** passed=True; failed=none; similarity=0.966387927532196; NLI forward/reverse=0.9795352816581726/0.9928467869758606; style substantial=False.

**הבדל ממוקד:** almost at the point → nearing; in international ambition → becoming ... ambition

**ממצא וקשר לדגלים:** דרגת הקרבה והיחס המטאפורי עשויים להשתנות מעט; בנוסף ה-style proxy לא substantial.

**קריאה חוזרת:** בהיעדר הקשר נוסף אין בסיס לסגור גם את שאלת המשמעות וגם את שאלת הסגנון.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** הכרעה אנושית בשני הצירים; לא לסמן מעבר משולב.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "no",
      "not"
    ],
    [
      "no",
      "no"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "an international ambition for survival."
    ],
    [
      "an international ambition for survival."
    ]
  ],
  "CERT": [
    [
      "could"
    ],
    [
      "could"
    ]
  ],
  "ATTR": [
    [
      "said"
    ],
    [
      "said"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:421539

| Original | Style Rewrite |
|---|---|
| Hey, remember that unhinged cultural revolution we launched a few years back? That was insane — amirite? That's essentially what Rep. Alexandria Ocasio-Cortez (D-N.Y.) told ABC News host Jonathan Karl recently, quoting a New York City Council member who describes socialist Wisconsin gubernatorial candidate Francesca Hong's past tweets about defunding the police and shuttering prisons. | Remember the unhinged cultural revolution we launched a few years ago? Insane, wasn't it — amirite? That, essentially, was what Rep. Alexandria Ocasio-Cortez (D-N.Y.) recently told ABC News host Jonathan Karl. She was quoting a New York City Council member whose description concerned past tweets by Francesca Hong, the socialist Wisconsin gubernatorial candidate, about defunding the police and shuttering prisons. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** essentially משמר את העובדה שהפתיחה היא פרפרזה אירונית, לא ציטוט מילולי של AOC. שכבות AOC→חבר מועצה→ציוצי הונג נשמרות, והפיצול מקל על התחביר בלי לשנות ייחוס.

**QC שמור:** passed=False; failed=negation; similarity=0.9770082831382751; NLI forward/reverse=0.9970518350601196/0.9963782429695129; style substantial=True.

**הבדל ממוקד:** Insane — amirite? → Insane, wasn't it — amirite?

**ממצא וקשר לדגלים:** תג שאלה שלילי רטורי אינו שלילת insane. שרשרת AOC המצטטת מועצה ו-essentially נשמרת.

**קריאה חוזרת:** נבדק מי מצטט את מי; לא זוהה החלפת בעל הטענה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** תיעוד דגל שלילה מילוני; לשמור הפרדה בין דובר מצוטט למספר.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    [
      "n't"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:422259

| Original | Style Rewrite |
|---|---|
| Public leadership doesn't mean that the "leader" has to have all the solutions, but instead must be open to others with problem-solving ideas. That was one of Franklin Roosevelt's great strengths when he came into the White House. Facing the full-blown crisis of a national depression, he brought his top advisers together with an open mandate for creativity: "Do something," he told them. "If it works, do more of it. If it doesn't work, do something else." | A public "leader" need not possess every solution. What public leadership requires instead is openness to other people's ideas for solving problems. Franklin Roosevelt demonstrated that strength when he entered the White House amid the full-blown crisis of a national depression. He gathered his top advisers and gave them an open mandate to be creative: "Do something," he told them. "If it works, do more of it. If it doesn't work, do something else." |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** all the solutions ו־every solution שקולים בהקשר השלילה. חובת פתיחות לרעיונות אחרים, הדוגמה ההיסטורית וכל הציטוטים נשמרו; חלוקת המשפטים והחזית השתנו.

**QC שמור:** passed=False; failed=certainty; similarity=0.9662822484970093; NLI forward/reverse=0.9986364245414734/0.9975556135177612; style substantial=True.

**הבדל ממוקד:** must be open → requires openness

**ממצא וקשר לדגלים:** החובה נשמרת למרות היעלמות מילת must מהרשימה. every/all שומרים היקף בהקשר זה.

**קריאה חוזרת:** נבדקו הכמת והציטוטים, לא רק מילת החובה; אין שינוי מזוהה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** אימות אנושי רגיל; אין צורך בשינוי טקסט בגלל לקסיקון certainty.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't",
      "n't"
    ],
    [
      "not",
      "n't"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "do something,",
      "if it works, do more of it. if it doesn't work, do something else.",
      "leader"
    ],
    [
      "do something,",
      "if it works, do more of it. if it doesn't work, do something else.",
      "leader"
    ]
  ],
  "CERT": [
    [
      "must"
    ],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:421853

| Original | Style Rewrite |
|---|---|
| There's an old saying: Those who can, do; those who can't, teach. A similar idea underscores the debate over wealth taxes in California and elsewhere: Those who can, build companies. Those who can't, devise ways for the government to take shares in what others have built. | There is an old saying: Those who can, do; those who can't, teach. The debate over wealth taxes in California and elsewhere reflects a similar idea. Those who can, build companies. Those who can't, devise ways for the government to take shares in what other people have built. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Borderline.

**נימוק AI קודם:** המשל והביקורת על מיסוי נשמרים כמעט מילה במילה. המשפט על debate הוצב בחזית ופוצל, אך עיקר הפסקה זהה ולכן שינוי הסגנון מוגבל.

**QC שמור:** passed=True; failed=none; similarity=0.9775254726409912; NLI forward/reverse=0.9940756559371948/0.9931354522705078; style substantial=False.

**הבדל ממוקד:** There's → There is; פיצול וסידור משפט על wealth taxes

**ממצא וקשר לדגלים:** האמרה והלעג נשמרים; מעט ארגון מחדש ורוב הטקסט קרוב למקור.

**קריאה חוזרת:** הבדיקה החוזרת לא מצאה אובדן משמעות אך אינה הופכת שינוי קטן למשמעותי.

**סיווג אנליטי:** משמעות ללא שינוי מזוהה; סגנון מוגבל

**המשך מומלץ:** לשפוט style באופן עצמאי מהמשמעות.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't",
      "n't"
    ],
    [
      "n't",
      "n't"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:424146

| Original | Style Rewrite |
|---|---|
| During a recent town hall, a Michigan University student named Iman Dashti confronted Democratic Party's Senate candidate Abdul El-Sayed regarding his habitual whitewashing and rationalization of Islamic terrorism. Dashti, who says his family is a victim of the Iranian regime's theocratic persecution, pressed the candidate numerous times to denounce one of the world's most odious tyrannies. | At a recent town hall, Democratic Party's Senate candidate Abdul El-Sayed faced repeated demands from Iman Dashti, a Michigan University student, to denounce one of the world's most odious tyrannies. Dashti, who says his family has suffered the Iranian regime's theocratic persecution, confronted El-Sayed over what Dashti described as the candidate's habitual whitewashing and rationalization of Islamic terrorism. |

**קודם:** ai_substantial_semantic_concern; Meaning=No; Narrative=Borderline; Style=Yes.

**נימוק AI קודם:** המקור מציג habitual whitewashing בתיאור המספר; what Dashti described as מוסיף ייחוס מפורש של התיאור לסטודנט. זו החלפת מקור אחריות להאשמה, גם כשכיוון הביקורת נשמר. Narrative Borderline עקב ההתרחקות של קול המספר.

**QC שמור:** passed=False; failed=framing_anchors; similarity=0.9546544551849365; NLI forward/reverse=0.9961530566215515/0.9818313717842102; style substantial=True.

**הבדל ממוקד:** האשמה ישירה → what Dashti described as ...

**ממצא וקשר לדגלים:** המספר מעביר את אחריות אפיון ה-whitewashing לדאשטי. דגל framing קשור גם ל-victim לעומת suffered, ואינו תופס במדויק את בעל הטענה.

**קריאה חוזרת:** הייחוס החדש נשאר שינוי מפורש. נוכחות says בשני הצדדים יכולה להסתיר אותו ב-guard הבוליאני.

**סיווג אנליטי:** הבדל סמנטי מזוהה בקריאת AI

**המשך מומלץ:** הכרעה אנושית על בעל הטענה; לא להציג רק כ-false positive מילוני.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [
      "says"
    ],
    [
      "says"
    ]
  ],
  "FRAME": [
    [
      "victim"
    ],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:421811

| Original | Style Rewrite |
|---|---|
| You know who. The conqueror whose voice, face and deeds are inescapable. Donald Trump had never heard of William the Conqueror when he visited England, but he loved the word and the idea for his presidency. He also has Napoleon Bonaparte and Julius Caesar "great man" delusions. | You know who: Donald Trump, the conqueror whose voice, face and deeds cannot be escaped. On his visit to England, Trump had never heard of William the Conqueror, yet he loved both the word and the idea as applied to his presidency. Delusions of being a Napoleon Bonaparte or Julius Caesar "great man" are his as well. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** and→or בין נפוליאון לקיסר אינו שימור מילולי של יחס הצירוף. עם זאת מדובר בדימויי great man, לא בהכרח בטענה לוגית פורמלית לשני מצבי־זהות נפרדים; No ודאי מחמיר מדי. הנרטיב הביקורתי נשמר. both מבהיר את word and idea, ו־cannot be escaped שקול ל־inescapable.

**QC שמור:** passed=False; failed=negation; similarity=0.898421585559845; NLI forward/reverse=0.8862411379814148/0.9791974425315857; style substantial=True.

**הבדל ממוקד:** inescapable → cannot be escaped; Napoleon and Julius → Napoleon or Julius

**ממצא וקשר לדגלים:** שלילה מפורשת משמרת inescapable. and/or בדימוי יכול לשנות שילוב לשתי חלופות, אך זו מטאפורה ולא conjunction לוגי פשוט.

**קריאה חוזרת:** נבדקו שני הרכיבים בנפרד; אין הצדקה ל-No ודאי, אך העמימות הרטורית נשמרת.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** אדם יכריע במטאפורה; דגל השלילה אינו בודק and/or.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "never"
    ],
    [
      "cannot",
      "never"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "great man"
    ],
    [
      "great man"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:422146

| Original | Style Rewrite |
|---|---|
| Oh good, another war. This time a trade war with Canada and for no other reason than ... what? To give Donald Trump a new stage for big-league bullying? To divert attention from the Jeffrey Epstein files? Who knows. Whatever. Trying to humiliate our closest ally does not serve American interests, ya think? | Oh good, another war—this time a trade war with Canada, for no obvious reason. Is it meant to give Donald Trump a new stage for big-league bullying? Is it supposed to divert attention from the Jeffrey Epstein files? Who knows. Whatever. Humiliating our closest ally does not serve American interests, ya think? |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** Trying to humiliate נעשה Humiliating: רכיב הניסיון אינו מפורש עוד, אף שהמשפט הוא הכללה ולא בהכרח דיווח הצלחה. for no obvious reason מתון מהשאלה המקורית על מניע; הספק אינו משנה את כיוון הביקורת.

**QC שמור:** passed=True; failed=none; similarity=0.9642197489738464; NLI forward/reverse=0.9855517148971558/0.9643881916999817; style substantial=False.

**הבדל ממוקד:** Trying to humiliate → Humiliating; rhetorical why → no obvious reason

**ממצא וקשר לדגלים:** ייתכן מעבר מניסיון למעשה, או gerund כללי שאינו קובע הצלחה. הכיוון האנטי-מלחמתי נשמר.

**קריאה חוזרת:** קריאה חוזרת אינה מספיקה להכריע scope של gerund בהקשר הרטורי.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** הכרעה אנושית על ניסיון לעומת הישג ועוצמת השאלה.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "no",
      "not"
    ],
    [
      "no",
      "not"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:0b4c49505392

| Original | Style Rewrite |
|---|---|
| "'I'm dreadin' what I've got to watch,' the Colour-Sergeant said." Rudyard Kipling, the racist poet of the British Empire and the writer of the made-into-cartoons "Jungle Book," wrote those words in a poem called "Danny Deever," a poem about a British soldier being hung for murdering a fellow soldier in 1890, in India. | "'I'm dreadin' what I've got to watch,' the Colour-Sergeant said." Those words come from "Danny Deever," a poem Rudyard Kipling wrote in 1890, in India, about a British soldier being hung for murdering a fellow soldier. Kipling was the racist poet of the British Empire who also wrote the made-into-cartoons "Jungle Book." |

**קודם:** ai_substantial_semantic_concern; Meaning=No; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** במקור1890 ו־India מוצמדים לתיאור חייל שנתלה; בשכתוב נאמר במפורש Kipling wrote in1890, in India. זה מעביר זמן ומקום לפעולת הכתיבה שאינה מוצמדת אליהם במקור. הביקורת על קיפלינג והציטוט נשמרים; אין כאן בדיקת היסטוריה חיצונית.

**QC שמור:** passed=False; failed=quotations; similarity=0.9344209432601929; NLI forward/reverse=0.9954730868339539/0.9914747476577759; style substantial=True.

**הבדל ממוקד:** in 1890, in India מתאר אירוע → מתאר את כתיבת Kipling

**ממצא וקשר לדגלים:** אותם זמן ומקום מוצמדים לפעולה אחרת; guard מספרים/ישויות לא בודק attachment. גם פיסוק בציטוט שונה.

**קריאה חוזרת:** השוואת שני המשפטים מאשרת שינוי היקף של תיאור הזמן והמקום בלי צורך בבדיקת אמת היסטורית.

**סיווג אנליטי:** הבדל סמנטי מזוהה בקריאת AI

**המשך מומלץ:** בדיקה אנושית של הצמדת תיאורים; לא להסתפק בזהות ערכי השנה והמקום.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "'i'm dreadin' what i've got to watch,' the colour-sergeant said.",
      "danny deever,",
      "jungle book,"
    ],
    [
      "'i'm dreadin' what i've got to watch,' the colour-sergeant said.",
      "danny deever,",
      "jungle book."
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [
      "said"
    ],
    [
      "said"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "1890"
    ],
    [
      "1890"
    ]
  ]
}
```

</details>

## creators:217678

| Original | Style Rewrite |
|---|---|
| Warts and all, if I were a voting member of Congress, I would certainly cast a yea for the tax-cut plans passed by the Senate and House that are headed for conference (to work out minor differences) in the weeks ahead. | If I had a vote in Congress, it would certainly be a yea for the tax-cut plans the Senate and House have passed, warts and all. Those plans are headed to conference in the coming weeks, where minor differences will be worked out. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** to work out minor differences מציין תכלית הכינוס; where differences will be worked out מציג פתרון צפוי באופן מפורש יותר. ההצבעה ההיפותטית וה־certainly של תמיכת הכותב נשמרים.

**QC שמור:** passed=False; failed=future_tense; similarity=0.8737668395042419; NLI forward/reverse=0.9966732263565063/0.9983450174331665; style substantial=True.

**הבדל ממוקד:** conference to work out differences → where differences will be worked out

**ממצא וקשר לדגלים:** מטרת ועידה מוצגת כתוצאה עתידית צפויה. certainly נוגע להצבעה אחרת ונשמר.

**קריאה חוזרת:** בדיקה חוזרת מפרידה ודאות ההצבעה מוודאות פתרון המחלוקת; החשש נותר.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** לבדוק תכלית לעומת התחייבות לתוצאה, דגל future רלוונטי אך לא מכריע.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    true
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [
      "certainly"
    ],
    [
      "certainly"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:424229

| Original | Style Rewrite |
|---|---|
| It would be hard to find a more insulting offer than to exchange money for your vote. That's exactly what President Donald Trump did in announcing that if voters keep Republicans in power come the midterms, he'll send every adult citizen a $5,000 check. | Exchanging money for someone's vote would be hard to surpass as an insulting offer. Yet that is exactly the offer President Donald Trump made: he announced that every adult citizen would receive a $5,000 check if voters kept Republicans in power come the midterms. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** would receive...if kept הוא backshift בתוך he announced, לא הפיכת ההבטחה לעובדה. הסכום, כל אזרח בוגר והתנאי האלקטורלי נשמרים; ההערכה insulting באותה עוצמה.

**QC שמור:** passed=False; failed=future_tense; similarity=0.9377061128616333; NLI forward/reverse=0.9977278113365173/0.9933997392654419; style substantial=True.

**הבדל ממוקד:** he'll send ... if voters keep → announced ... would receive if voters kept

**ממצא וקשר לדגלים:** backshift בתוך דיווח מותנה, לא הכרזה על תשלום שכבר בוצע; $5000 והאוכלוסייה נשמרים.

**קריאה חוזרת:** נבדקו יחד announced, would ו-if; לא זוהה מעבר מניבוי לעובדה.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** לתעד מגבלת זיהוי will בלבד, ללא שינוי guard כעת.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    true,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "5,000"
    ],
    [
      "5,000"
    ]
  ]
}
```

</details>

## creators:423153

| Original | Style Rewrite |
|---|---|
| Growing up, I received a wealth of working-class values from my parents, including this nugget about egalitarianism: "Nobody is better than you," they said, "and you're no better than anybody else." That's the ethical underpinning for "We're all in this together" — it's what Thomas Jefferson enshrined in the Declaration of Independence and it's what Lincoln consecrated in his Gettysburg address; it's in our own pledge of allegiance to "liberty and justice for all;" it's what the Statue of Liberty welcomes; it's Woody Guthrie's anthem to the Common Good; and ... well, it's AMERICA! | Among the wealth of working-class values my parents gave me as I grew up was this nugget of egalitarianism: "Nobody is better than you," they said, "and you're no better than anybody else." From that ethical foundation comes "We're all in this together." Thomas Jefferson enshrined it in the Declaration of Independence; Lincoln consecrated it in his Gettysburg address; and our own pledge of allegiance promises "liberty and justice for all;" The Statue of Liberty welcomes it, Woody Guthrie made it an anthem to the Common Good, and ... well, it's AMERICA! |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** it's Woody Guthrie's anthem הומר ל־Woody Guthrie made it an anthem, ניסוח של פעולת יצירה מפורשת יותר ממטאפורת הזיהוי. גם פיסוק הציטוט We're all in this together משתנה. המכלול השוויוני והמקורות המנויים נשמרים.

**QC שמור:** passed=False; failed=quotations; similarity=0.9263155460357666; NLI forward/reverse=0.9960675239562988/0.9938716888427734; style substantial=True.

**הבדל ממוקד:** We're all in this together → אותו ציטוט עם נקודה פנימית; anthem → made it an anthem

**ממצא וקשר לדגלים:** פיסוק פנימי מפר verbatim. בהקשר הרשימה המטאפורית, תיאור Guthrie אינו מבסס טענת חיבור חדשה מעבר לאזכור האנתם שלו.

**קריאה חוזרת:** החשש הסמנטי הקודם ל-made אינו חזק דיו בהקשר; חריגת הציטוט נשארת ודאית ברמת פני השטח.

**סיווג אנליטי:** נאמנות ציטוט בלבד, ללא drift מזוהה

**המשך מומלץ:** אדם יבחין ב-fidelity ובמטאפורה; אין קבלה אוטומטית.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "no"
    ],
    [
      "no"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "and you're no better than anybody else.",
      "liberty and justice for all;",
      "nobody is better than you,",
      "we're all in this together"
    ],
    [
      "and you're no better than anybody else.",
      "liberty and justice for all;",
      "nobody is better than you,",
      "we're all in this together."
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [
      "said"
    ],
    [
      "said"
    ]
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:418620

| Original | Style Rewrite |
|---|---|
| The next mayor of Washington, D.C. is likely to be a Marxist. In Los Angeles, the Mensheviks and Bolsheviks are battling it out for control. New York City has already fallen to a champion of Third Worldism. | Washington, D.C.'s next mayor is likely to be a Marxist. In Los Angeles, Mensheviks and Bolsheviks are fighting for control. New York City, meanwhile, has already fallen to a champion of Third Worldism. |

**קודם:** borderline_or_unresolved_quality; Meaning=Yes; Narrative=Yes; Style=Borderline.

**נימוק AI קודם:** likely, שמות הפלגים והטענה על ניו יורק נשמרים. שינוי possessive, כמה מילים ו־meanwhile מצומצם מאוד; אין שינוי מבני רחב בפסקה הקצרה.

**QC שמור:** passed=True; failed=none; similarity=0.9857903718948364; NLI forward/reverse=0.9943168759346008/0.9934711456298828; style substantial=True.

**הבדל ממוקד:** The next mayor ... → Washington's next mayor ...; meanwhile

**ממצא וקשר לדגלים:** אותן הסתייגות likely, קבוצות ואפיון Third Worldism; שינויים מקומיים יחסית.

**קריאה חוזרת:** אין החלפת אידאולוגיה מזוהה; בדיקת סגנון נשארת נפרדת.

**סיווג אנליטי:** משמעות ללא שינוי מזוהה; סגנון מוגבל

**המשך מומלץ:** אימות אנושי על חוזק ההתערבות.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:423371

| Original | Style Rewrite |
|---|---|
| It was probably inevitable that the Right's economic populism would degenerate into promises of more government checks. Early in the week, the administration floated the idea of redirecting federal childcare aid so low-income married stay-at-home parents could get a $9,000 subsidy per child for daycare. | Promises of more government checks were probably the inevitable destination of the Right's economic populism as it degenerated. Early in the week, the administration floated a proposal to redirect federal childcare aid, allowing low-income married stay-at-home parents to receive a $9,000 subsidy per child for daycare. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** was probably inevitable...would degenerate עשוי להיות עתיד־בעבר רטרוספקטיבי, במיוחד לפני הדוגמה על השבוע האחרון; אין הצדקה ל־No רק מהזמנים. as it degenerated מקבע קריאה בדיעבד ולכן נשמר ספק. allowing נמצא תחת floated a proposal ואינו מציג כשלעצמו סובסידיה כעובדה שבוצעה.

**QC שמור:** passed=False; failed=certainty; similarity=0.9785171747207642; NLI forward/reverse=0.9937000274658203/0.9967171549797058; style substantial=True.

**הבדל ממוקד:** probably inevitable ... would degenerate → as it degenerated

**ממצא וקשר לדגלים:** future-in-the-past יכול להיות רטרוספקטיבי כבר במקור, אך החדש מפורש יותר כאירוע. הטבת $9,000 לילד נשארת בתוך הצעה ולא ביצוע.

**קריאה חוזרת:** אין בסיס ל-No חד־משמעי; דגל could אינו לבדו הסיבה לחשש הזמן.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** אדם יכריע בהיקף הסתייגות probably ובמצב האירוע; לא לייחס הטבה שכבר ניתנה.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [
      "could",
      "probably"
    ],
    [
      "probably"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "9,000"
    ],
    [
      "9,000"
    ]
  ]
}
```

</details>

## creators:0105f26ef9f1

| Original | Style Rewrite |
|---|---|
| Good examples of that are Donald Trump, escargot and gang rape, three things that disgust me, but are keenly desired by some people. Just knowing that will make you look around for a long time before you sit next to a stranger on the bus. The fact that I can type the word "bus" without automatically putting the word "school" in front of it indicates that I might have at least some history with people whose wants and needs are not only disgusting, but poorly concealed. | Donald Trump, escargot, and gang rape are good examples: all three disgust me, yet some people strongly desire them. Knowing that can make you spend a long time looking around before choosing a seat beside a stranger on the bus. The fact that I can type the word "bus" without instinctively putting "school" in front of it suggests that I may have some history with people whose wants and needs are both disgusting and badly concealed. |

**קודם:** ai_substantial_semantic_concern; Meaning=No; Narrative=Borderline; Style=Yes.

**נימוק AI קודם:** will make you הוחלף ב־can make you, תחזית החלטית לעומת אפשרות. הגועל והדוגמאות נשמרים אך תוקף האזהרה לקורא נחלש. שאר סדר המשפטים והארגון משתנים במידה ניכרת.

**QC שמור:** passed=False; failed=negation|certainty|future_tense; similarity=0.9328413009643555; NLI forward/reverse=0.9945619702339172/0.9874430298805237; style substantial=True.

**הבדל ממוקד:** will make → can make

**ממצא וקשר לדגלים:** ניבוי מוחלף באפשרות. not only → both אינו היפוך שלילה; might/may קרובים. דגל future תואם כאן לשינוי מודאלי אמיתי.

**קריאה חוזרת:** ההבדל נותר גם כשקוראים אותו כאזהרה הומוריסטית; תפקידים ודוגמאות הגועל נשמרים.

**סיווג אנליטי:** הבדל סמנטי מזוהה בקריאת AI

**המשך מומלץ:** הכרעה אנושית על כוח הניבוי; לא להסביר את כל הדגלים כטכניים.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "without",
      "not"
    ],
    [
      "without"
    ]
  ],
  "future": [
    true,
    false
  ],
  "quotations": [
    [
      "bus",
      "school"
    ],
    [
      "bus",
      "school"
    ]
  ],
  "CERT": [
    [
      "might"
    ],
    [
      "may"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:421024

| Original | Style Rewrite |
|---|---|
| Brides should know that they already have a man. They don't have to use their wedding to attract a date for Saturday night. They've supposedly secured one for the foreseeable future. Thus, it's hard to figure how the fashion trend of "naked dressing," lamentable even at nightclubs, has invaded the precincts of ancient social custom. Displaying one's privates — or underwear — in public started as a fashion trend pushed by attention-hungry celebrities. Now it's walking down the aisle. | Brides should remember that they already have a man. A wedding is not supposed to be a way to attract a date for Saturday night; supposedly, that part is settled for the foreseeable future. That is why it is hard to understand how "naked dressing"—lamentable even in nightclubs—has entered an ancient social custom. Publicly displaying one's privates, or one's underwear, began as a fashion trend promoted by attention-hungry celebrities. Now it is making its way down the aisle. |

**קודם:** ai_substantial_semantic_concern; Meaning=No; Narrative=Borderline; Style=Yes.

**נימוק AI קודם:** don't have to use אינו not supposed to be a way: היעדר צורך הופך לנורמה על שימוש ראוי בחתונה. הביקורת הכללית על החשיפה נשמרת, אך עוצמת ההוראה השתנתה. suppose/כיווני הזמן נשמרים בשאר הקטע.

**QC שמור:** passed=False; failed=quotations; similarity=0.9467470645904541; NLI forward/reverse=0.9914616346359253/0.9900017976760864; style substantial=True.

**הבדל ממוקד:** don't have to use their wedding → wedding is not supposed to be a way

**ממצא וקשר לדגלים:** היעדר צורך הומר לנורמה מגבילה. דגל quotations נוגע לפיסוק naked dressing ולא מזהה את השינוי הדאונטי.

**קריאה חוזרת:** הבדיקה החוזרת מאשרת הבדל בין unnecessary ל-not supposed to, גם אם הביקורת הכללית דומה.

**סיווג אנליטי:** הבדל סמנטי מזוהה בקריאת AI

**המשך מומלץ:** הכרעה אנושית על חובה/נורמה; fidelity בנפרד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "n't"
    ],
    [
      "not"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "naked dressing,"
    ],
    [
      "naked dressing"
    ]
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:415881

| Original | Style Rewrite |
|---|---|
| WASHINGTON — Camelot, it's not. King Arthur, not even close. Donald Trump is a pretender president who doesn't even pretend to do right by the people. In all candor, this city, graced by garden squares, memorials and museums, feels like a crime scene, with his fingerprints everywhere on it. Places we held dear are demolished (the White House East Wing) or closed (the Kennedy Center for the Performing Arts). But who knows what's in the knave's heart? | WASHINGTON — This is no Camelot, and Donald Trump is nowhere close to King Arthur. A pretender president, he doesn't even pretend to do right by the people. In all candor, with his fingerprints everywhere, this city of garden squares, memorials and museums feels like a crime scene. The White House East Wing, one of the places we held dear, has been demolished; another, the Kennedy Center for the Performing Arts, is closed. Yet who can know what's in the knave's heart? |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** who knows מה בלבו נעשה who can know, שעשוי לנסח אי־יכולת לדעת ולא רק שאלה על ידיעה קיימת. תיאורי ההרס, הסגירה וזירת הפשע נשמרים; המסגור החריף זהה.

**QC שמור:** passed=False; failed=negation; similarity=0.9663621187210083; NLI forward/reverse=0.9898573160171509/0.9882488250732422; style substantial=True.

**הבדל ממוקד:** Camelot not → no Camelot; Who knows → Who can know

**ממצא וקשר לדגלים:** ספירת שלילה משתנה בלי היפוך הדימוי. שאלת חוסר הידיעה רטורית בשני הנוסחים, ולא טענה חדשה על יכולת.

**קריאה חוזרת:** הסתייגות ה-AI הקודמת על can נחלשת בהקשר הרטורי המלא.

**סיווג אנליטי:** דגל QC ללא הבדל משמעות מזוהה בקריאת AI

**המשך מומלץ:** אימות אנושי רגיל; לא להכריז drift רק מפועל יכולת בשאלה רטורית.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not",
      "not",
      "n't"
    ],
    [
      "no",
      "n't"
    ]
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:2e34435c6ccf

| Original | Style Rewrite |
|---|---|
| About three weeks before Republicans expect an electoral beating, Donald Trump had to get rid of Kimberly Guilfoyle, his ambassador to Greece. He simply had to. Trump's money-grabbing corruption was wearing thin even on devoted fans, but the president knew how to wrap his mob-like patter in foggy euphemisms and double meanings. | Roughly three weeks before Republicans expected an electoral beating, Donald Trump had to remove Kimberly Guilfoyle, his ambassador to Greece. He simply had to. Trump's money-grabbing corruption was wearing thin even among devoted supporters, though the president remained skilled at wrapping his mob-like patter in vague euphemisms and double meanings. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Borderline.

**נימוק AI קודם:** expect בזמן הווה הומר ל־expected בעבר, ומזיז את נקודת המבט על ציפיית הרפובליקנים. שאר ההאשמה והשליחוּת נשמרות. הניסוח כמעט באותו סדר עם החלפות מילוליות, ולכן Style Borderline.

**QC שמור:** passed=True; failed=none; similarity=0.9732093811035156; NLI forward/reverse=0.9926124811172485/0.9918253421783447; style substantial=False.

**הבדל ממוקד:** Republicans expect → expected

**ממצא וקשר לדגלים:** backshift עשוי להתאים לנרטיב עבר שכבר היה במקור, או לשנות את זמן הציפייה הנוכחית. הסגנון קרוב למקור.

**קריאה חוזרת:** אין די הקשר להכרעה סופית בזמן; אין להשלים אותו באמצעות עובדות חיצוניות.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** אדם יבדוק זמן ושינוי סגנוני בנפרד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>

## creators:11db638844f4

| Original | Style Rewrite |
|---|---|
| One of the most unheralded policy successes of President Donald Trump's second term has been the purging of many unnecessary federal jobs. The federal government has reduced its workforce by 300,000 jobs since Jan. 20, 2025, bringing it down to a still-bulky 2.7 million employees. Not since President Lyndon Johnson's Great Society vastly expanded the scope of the national government has the federal workforce been at this level. | The purging of many unnecessary federal jobs stands among the most unheralded policy successes of President Donald Trump's second term. Since Jan. 20, 2025, the federal workforce has shrunk by 300,000 jobs to a still-bulky 2.7 million employees. The last time the workforce stood at this level was before President Lyndon Johnson's Great Society vastly expanded the scope of the national government. |

**קודם:** ai_substantial_semantic_concern; Meaning=No; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** Not since...Great Society מציב את נקודת ההשוואה בתקופת ההרחבה; last time...was before...expanded מקבע זמן מוקדם יותר. before אינו נובע מן המקור באופן בטוח ומוסיף טענה היסטורית. המספרים וההערכה בעד קיצוץ נשמרים.

**QC שמור:** passed=False; failed=negation; similarity=0.9727492928504944; NLI forward/reverse=0.9017007946968079/0.9110477566719055; style substantial=False.

**הבדל ממוקד:** not since Great Society → last time ... before Great Society

**ממצא וקשר לדגלים:** not since אינו קובע לבדו את הרגע המדויק האחרון. before מוסיף גבול זמן מפורש, אך אין די ראיות לסתירה היסטורית ודאית.

**קריאה חוזרת:** ה-No הקודם היה נחרץ מדי: הסיווג האנליטי הנוכחי הוא סיכון זמן לא מוכרע, ולא הוכחת drift. דגל שלילה אינו מוכיח תזמון.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** הכרעה אנושית על גבולות זמן; לשמר את אי-הוודאות ואת ההערכה הקודמת בנפרד.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [
      "not"
    ],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [],
    []
  ],
  "CERT": [
    [],
    []
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [
      "2.7",
      "20",
      "2025",
      "300,000"
    ],
    [
      "2.7",
      "20",
      "2025",
      "300,000"
    ]
  ]
}
```

</details>

## creators:419965

| Original | Style Rewrite |
|---|---|
| Executives climbing the corporate ladder to the top seem to lose IQ the higher up they get. That might explain why John Deere's top corporate bosses have imposed an astonishingly stupid policy on America's farmers. For years, they've decreed that while a farmer "technically owns" a tractor or other John Deere product, the owner is prohibited from making any repairs when the machinery breaks down, stalls out, etc. Instead, owners must call an authorized Deere dealer to fix what most farmers could handle by themselves. | The higher executives climb toward the top of the corporate ladder, the more IQ they seem to lose. Perhaps that explains the astonishingly stupid policy John Deere's top corporate bosses have imposed on America's farmers. For years, the bosses have decreed that a farmer may "technically owns" a tractor or other John Deere product but, when it breaks down, stalls out, etc., is prohibited from repairing it. Instead, the owner has to call an authorized Deere dealer, even for repairs most farmers could handle themselves. |

**קודם:** borderline_or_unresolved_quality; Meaning=Borderline; Narrative=Yes; Style=Yes.

**נימוק AI קודם:** may technically owns פגום דקדוקית ומכניס סמן מודאלי לפני טענת הבעלות. ההמשך עדיין אוסר תיקון ומחייב סוחר, אך אין ודאות שהבעלות הובעה באותה עוצמה. שינוי מבני ניכר קיים; Style Yes אינו אישור תקינות דקדוקית.

**QC שמור:** passed=False; failed=certainty; similarity=0.981190025806427; NLI forward/reverse=0.9936355352401733/0.9806760549545288; style substantial=True.

**הבדל ממוקד:** might explain → Perhaps explains; must call → has to call; farmer may ... technically owns

**ממצא וקשר לדגלים:** שני השינויים הראשונים יכולים לשמר הסתייגות וחובה. may עם owns יוצר מבנה פגום ועלול לשנות את היקף הבעלות המסויגת.

**קריאה חוזרת:** אין לסווג את כל המקרה כטכני רק משום שמילות המודאליות האחרות שקולות.

**סיווג אנליטי:** סיכון סמנטי שלא הוכרע גם בקריאה חוזרת

**המשך מומלץ:** אדם יבדוק בעלות, scope ודקדוק; אין לתקן את הטקסט במסגרת הביקורת.

<details><summary>אבחון לקסיקלי מדויק: Original ואז Rewrite</summary>

```json
{
  "neg": [
    [],
    []
  ],
  "future": [
    false,
    false
  ],
  "quotations": [
    [
      "technically owns"
    ],
    [
      "technically owns"
    ]
  ],
  "CERT": [
    [
      "could",
      "might",
      "must"
    ],
    [
      "could",
      "may"
    ]
  ],
  "ATTR": [
    [],
    []
  ],
  "FRAME": [
    [],
    []
  ],
  "numbers": [
    [],
    []
  ]
}
```

</details>
