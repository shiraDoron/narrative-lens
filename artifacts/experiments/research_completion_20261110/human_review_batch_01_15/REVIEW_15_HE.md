# חבילת סקירה אנושית ראשונה — 15 זוגות

תאריך הכנה: 10.11.2026. נבחרו15 מתוך75 השכתובים החדשים, כולם train. זו חבילה **בסיוע QC, לא עיוורת**; אין בה הכרעות אדם או תוויות נרטיב מוצעות.

העדיפות היא NLI, אחריו ייחוס/מסגור, ודאות ואז רמזי משטח בכמתים. שוברי שוויון: רמז כמתים, מספר דגלים, ID. זה מדגם מכוון לתחילת העבודה, לא מדגם להערכת שיעורי הצלחה. רמזי כמתים אינם guards חדשים.

## איך למלא

- קראו את שני הטקסטים במלואם. העריכו שימור ביחס למקור; אין צורך להסכים עם העמדה או לבדוק את אמת העובדות.
- **Meaning Preserved:** Yes אם הטענות, העובדות, התפקידים, היחסים, הכמתים, הוודאות והייחוס נשמרו; No אם זוהה שינוי מהותי; Borderline אם קיים ספק שיש לפרט.
- **Narrative Preserved:** Yes אם העמדה, המסגור, מי מואשם/משובח ועוצמתם נשמרו; No אם השתנו מהותית; Borderline אם לא ניתן להכריע. אין צורך לדעת Left/Right כדי לזהות שימור עמדה.
- **Style Change Valid:** Yes אם יש שינוי ניכר באופן ההבעה; No אם הטקסט זהה או השינוי זניח; Borderline אם השינוי מוגבל או קשה להפרידו משינוי תוכן. שפטו בנפרד: שינוי סגנוני יכול להתקיים גם כשמשמעות נפגעה.
- דגל אוטומטי ושאלת בדיקה אינם הוכחה לכשל. גם טקסט שעבר את ה־guards דורש שיפוט. אין לערוך את המקור או השכתוב.
- ב־No או Borderline ציינו בהערות ביטוי מדויק והסבר. השאירו שדה ריק אם עדיין לא נבדק; אל תסמנו Yes כברירת מחדל.
- טבלאות העריכה הן הבדלי רצף מילים אוטומטיים, לא מיפוי סמנטי או רשימת טענות. שינוי סדר עשוי להופיע כמחיקה והוספה. סימן ∅ מציין צד ריק.

| פרטי סקירה | למילוי |
|---|---|
| מזהה סוקר/ת אדם | |
| תאריך הסקירה בפועל | |
| סיוע מכלי AI, אם היה | |

הכרעות של LLM אינן אימות אנושי עצמאי. חבילה זו היא שלב עבודה ראשון; היא אינה קובעת קבלה לאימון או מחליפה את כלל ה־QC המלא וה־adjudication.

## אינדקס

| # | ID | סיבה לתעדוף — אות אוטומטי בלבד |
|---|---|---|
| 1 | creators:417661 | bidirectional_nli |
| 2 | creators:420299 | negation, attribution, future_tense; רמז הבדל משטח בכמתים |
| 3 | creators:424146 | framing_anchors |
| 4 | creators:422259 | certainty; רמז הבדל משטח בכמתים |
| 5 | creators:423650 | certainty; רמז הבדל משטח בכמתים |
| 6 | creators:416848 | certainty |
| 7 | creators:418916 | certainty |
| 8 | creators:419965 | certainty |
| 9 | creators:423371 | certainty |
| 10 | creators:296082 | negation, similarity; רמז הבדל משטח בכמתים |
| 11 | creators:421367 | negation, similarity; רמז הבדל משטח בכמתים |
| 12 | creators:208496 | negation; רמז הבדל משטח בכמתים |
| 13 | creators:3fd01161cd76 | quotations; רמז הבדל משטח בכמתים |
| 14 | creators:421811 | negation; רמז הבדל משטח בכמתים |
| 15 | creators:213461 | אין דגלי פסילה קיימים; רמז הבדל משטח בכמתים |

## זוג 01 — creators:417661

| Original | Style Rewrite |
|---|---|
| Set aside, for a moment, that Maine Senate candidate Graham Platner spent years with a Nazi SS Totenkopf tattoo. Set aside that he blamed sexual assault victims for their predicament, that he called rural white Americans stupid racists, that he advocated political violence, that he mocked a wounded Purple Heart recipient, that he joked about the Virgin Mary being a "skank" and that he joined a hookup site while married. | For a moment, put aside the years Maine Senate candidate Graham Platner spent with a Nazi SS Totenkopf tattoo. Put aside, too, his blaming of sexual assault victims for their predicament, his description of rural white Americans as stupid racists and his advocacy of political violence. Then set aside his mockery of a wounded Purple Heart recipient, his joke that the Virgin Mary was a "skank" and his joining a hookup site while married. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| Set aside, for | For |
| that | put aside the years |
| years | ∅ |
| Set aside that he blamed | Put aside, too, his blaming of |
| that he called | his description of |
| ∅ | as |
| racists, that he advocated | racists and his advocacy of |
| violence, that he mocked | violence. Then set aside his mockery of |
| ∅ | his joke |
| he joked about | ∅ |
| being | was |
| that he joined | his joining |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- בדקו שכל ההאשמות, המשתתפים והפעלים נשמרו אחרי מעבר מרצף “that he…” לצירופים שמניים.
- האם הפיצול לשלושה משפטים שומר על אותה אחריות לטענות ואותה עוצמה רטורית?

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 02 — creators:420299

| Original | Style Rewrite |
|---|---|
| A significant majority of Americans support voter identification laws. According to polls, not only Republicans but Democrats believe a voter should show ID before participating in an election. If you believe the country needs more secure elections, I hear you. But the popular contention that Republicans are going to lose their congressional majority in the next midterm elections because of a failure to pass the SAVE America Act is a partisan fantasy fueled by social media. | Voter identification laws have the support of a significant majority of Americans. Polls show that Democrats, not just Republicans, believe voters should present ID before taking part in an election. I hear you if you believe our elections need greater security. What I don't buy is the popular contention that failing to pass the SAVE America Act will cost Republicans their congressional majority in the next midterm elections. That's a partisan fantasy fueled by social media. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| A | Voter identification laws have the support of a |
| Americans support voter identification laws. According to polls, | Americans. Polls show that Democrats, |
| only Republicans but Democrats | just Republicans, |
| a voter | voters |
| show | present |
| participating | taking part |
| If | I hear you if |
| the country needs more secure elections, | our elections need greater security. What |
| hear you. But | don't buy is |
| ∅ | failing to pass the SAVE America Act will cost |
| are going to lose | ∅ |
| elections because of a failure to pass the SAVE America Act is | elections. That's |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- השוו “According to polls” ל־“Polls show”: האם ייחוס הטענה ומידת הביטחון בה נשמרים?
- בדקו את “not only… but…” מול “not just”, ואת “are going to lose… because” מול “will cost”.
- האם “What I don't buy” שומר על עוצמת דחיית הטענה ועל היקף השלילה?

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 03 — creators:424146

| Original | Style Rewrite |
|---|---|
| During a recent town hall, a Michigan University student named Iman Dashti confronted Democratic Party's Senate candidate Abdul El-Sayed regarding his habitual whitewashing and rationalization of Islamic terrorism. Dashti, who says his family is a victim of the Iranian regime's theocratic persecution, pressed the candidate numerous times to denounce one of the world's most odious tyrannies. | At a recent town hall, Democratic Party's Senate candidate Abdul El-Sayed faced repeated demands from Iman Dashti, a Michigan University student, to denounce one of the world's most odious tyrannies. Dashti, who says his family has suffered the Iranian regime's theocratic persecution, confronted El-Sayed over what Dashti described as the candidate's habitual whitewashing and rationalization of Islamic terrorism. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| During | At |
| a Michigan University student named Iman Dashti confronted | ∅ |
| regarding his habitual whitewashing and rationalization of Islamic terrorism. | faced repeated demands from Iman |
| who says his family is | ∅ |
| victim of the Iranian regime's theocratic persecution, pressed the candidate numerous times | Michigan University student, |
| ∅ | Dashti, who says his family has suffered the Iranian regime's theocratic persecution, confronted El-Sayed over what Dashti described as the candidate's habitual whitewashing and rationalization of Islamic terrorism. |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- מי מציג את ההאשמה על whitewashing במקור, ומי בשכתוב שבו נוסף “what Dashti described as”?
- האם “is a victim” מול “has suffered” וסידור האירועים החדש משמרים מצב, זמן ותפקידים?

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 04 — creators:422259

| Original | Style Rewrite |
|---|---|
| Public leadership doesn't mean that the "leader" has to have all the solutions, but instead must be open to others with problem-solving ideas. That was one of Franklin Roosevelt's great strengths when he came into the White House. Facing the full-blown crisis of a national depression, he brought his top advisers together with an open mandate for creativity: "Do something," he told them. "If it works, do more of it. If it doesn't work, do something else." | A public "leader" need not possess every solution. What public leadership requires instead is openness to other people's ideas for solving problems. Franklin Roosevelt demonstrated that strength when he entered the White House amid the full-blown crisis of a national depression. He gathered his top advisers and gave them an open mandate to be creative: "Do something," he told them. "If it works, do more of it. If it doesn't work, do something else." |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| Public | A public "leader" need not possess every solution. What public |
| doesn't mean | requires instead is openness to other people's ideas for solving problems. Franklin Roosevelt demonstrated |
| the "leader" has to have all the solutions, but instead must be open to others with problem-solving ideas. That was one of Franklin Roosevelt's great strengths | strength |
| came into | entered |
| House. Facing | House amid |
| depression, he brought | depression. He gathered |
| together with | and gave them |
| for creativity: | to be creative: |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- האם “all the solutions” ו־“every solution” מבטאים אותו היקף בהקשר הזה?
- בדקו שדרישת הפתיחות לאחרים נשמרה אחרי ארגון מחדש של must/require, ושהציטוטים נשארו מילוליים.

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 05 — creators:423650

| Original | Style Rewrite |
|---|---|
| Inflation hasn't gone away — it's going up. With the midterm elections seven weeks off, that's a problem for the president and Congress. Voters hate inflation. They don't much like the cure either, and the cure has two parts. The Federal Reserve raising interest rates, like it just did, is one. The second part is overlooked and in the hands of Congress. Indeed, the Fed can't bring inflation down for good unless lawmakers show they will back the debt with future fiscal surpluses. That means becoming serious about overspending. | Inflation is going up, not going away. For the president and Congress, that's a problem with the midterm elections only seven weeks off. Voters hate inflation, but they're not particularly fond of its cure either. That cure has two parts. One is the Federal Reserve's raising of interest rates, as it just did. The other, often overlooked, rests with Congress: unless lawmakers demonstrate that future fiscal surpluses will back the debt, the Fed cannot bring inflation down for good. In other words, Congress must get serious about overspending. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| hasn't gone away — it's | is |
| up. With | up, not going away. For the president and Congress, that's a problem with |
| ∅ | only |
| off, that's a problem for the president and Congress. | off. |
| inflation. They don't much like the | inflation, but they're not particularly fond of its |
| either, and the | either. That |
| The | One is the |
| Reserve | Reserve's |
| ∅ | of |
| like | as |
| did, is one. | did. |
| second part is overlooked and in | other, often overlooked, rests with Congress: unless lawmakers demonstrate that future fiscal surpluses will back |
| hands of Congress. Indeed, | debt, |
| can't | cannot |
| good unless lawmakers show they will back the debt with future fiscal surpluses. That means becoming | good. In other words, Congress must get |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- האם התוספת “only” לפני seven weeks משפיעה על הדגשה או על דחיפות?
- השוו “That means becoming serious” ל־“Congress must get serious”: האם נשמרו עוצמת החיוב והגורם שאליו הוא מופנה?
- בדקו שיחס התנאי “unless” בין גיבוי החוב, עודפים עתידיים ויכולת הפד נשאר זהה.

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 06 — creators:416848

| Original | Style Rewrite |
|---|---|
| Democrats are again acting like they occupy the high moral ground of American politics. But if 2026 has proven anything, it's that there's virtually nothing a left-wing candidate could say or do that would elicit condemnation from Democrats if doing so threatened their power. | Once again, Democrats are behaving as though the high moral ground in American politics belongs to them. Yet if 2026 has demonstrated anything, it is this: virtually nothing a left-wing candidate might say or do would draw condemnation from Democrats when that condemnation would threaten their power. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| ∅ | Once again, |
| again acting like they occupy | behaving as though |
| of | in |
| politics. But | politics belongs to them. Yet |
| proven | demonstrated |
| it's that there's | it is this: |
| could | might |
| that | ∅ |
| elicit | draw |
| if doing so threatened | when that condemnation would threaten |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- האם could→might שומר על אותו סוג אפשרות במשפט ההיפותטי?
- השוו “if doing so threatened their power” ל־“when that condemnation would threaten their power”: האם התנאי נשמר?

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 07 — creators:418916

| Original | Style Rewrite |
|---|---|
| One of the most popular complaints of the younger Americans is that the United States has been bogged down in endless war and interventionism virtually their entire lifetimes. Welcome to history. As much as we may not like it, the United States has engaged in conflict and meddling more or less since its inception. The U.S. was born in war. It expanded through war. It freed its slaves through war. It grew into a superpower through war. And until utopia exists, it's exceedingly likely we will need to clash with those who threaten our prestige and power. | Younger Americans often complain that the United States has spent virtually their whole lives bogged down in endless war and interventionism. It's one of their most popular complaints. Well, welcome to history. Whether we like it or not, conflict and meddling have been part of the United States more or less from its inception. War was how the U.S. was born, how it expanded and how it freed its slaves. Through war, it also became a superpower. And until utopia exists, the likelihood that we will need to clash with those threatening our prestige and power remains exceedingly high. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| One of the most popular complaints of the younger | Younger |
| is | often complain |
| been | spent virtually their whole lives |
| interventionism virtually | interventionism. It's one of |
| entire lifetimes. Welcome | most popular complaints. Well, welcome |
| As much as | Whether |
| may not | ∅ |
| it, | it or not, conflict and meddling have been part of |
| has engaged in conflict and meddling | ∅ |
| since | from |
| The | War was how the |
| born in war. It | born, how it |
| through war. It | and how it |
| slaves through war. It grew into | slaves. Through war, it also became |
| superpower through war. | superpower. |
| it's exceedingly likely | the likelihood that |
| who threaten | threatening |
| power. | power remains exceedingly high. |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- בדקו אם “exceedingly likely” ו־“likelihood… remains exceedingly high” שומרים על אותה ודאות.
- השוו “As much as we may not like it” ל־“Whether we like it or not” מבחינת תנאי ועוצמה.
- האם איחוד רצף המשפטים על מלחמה משמר את כל הדוגמאות וההדגשה הרטורית?

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 08 — creators:419965

| Original | Style Rewrite |
|---|---|
| Executives climbing the corporate ladder to the top seem to lose IQ the higher up they get. That might explain why John Deere's top corporate bosses have imposed an astonishingly stupid policy on America's farmers. For years, they've decreed that while a farmer "technically owns" a tractor or other John Deere product, the owner is prohibited from making any repairs when the machinery breaks down, stalls out, etc. Instead, owners must call an authorized Deere dealer to fix what most farmers could handle by themselves. | The higher executives climb toward the top of the corporate ladder, the more IQ they seem to lose. Perhaps that explains the astonishingly stupid policy John Deere's top corporate bosses have imposed on America's farmers. For years, the bosses have decreed that a farmer may "technically owns" a tractor or other John Deere product but, when it breaks down, stalls out, etc., is prohibited from repairing it. Instead, the owner has to call an authorized Deere dealer, even for repairs most farmers could handle themselves. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| Executives climbing | The higher executives climb toward the top of |
| ladder to | ladder, |
| top | more IQ they |
| lose IQ | lose. Perhaps that explains |
| higher up they get. That might explain why | astonishingly stupid policy |
| an astonishingly stupid policy | ∅ |
| they've | the bosses have |
| while | ∅ |
| ∅ | may |
| product, the owner is prohibited from making any repairs | product but, |
| the machinery | it |
| etc. | etc., is prohibited from repairing it. |
| owners must | the owner has to |
| dealer to fix what | dealer, even for repairs |
| by | ∅ |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- בדקו “That might explain why” מול “Perhaps that explains” מבחינת מידת הוודאות והסיבתיות.
- בשכתוב מופיע “a farmer may "technically owns"”: האם נוסף רכיב אפשרות/הרשאה או נוצר קושי שמפריע להבנת טענת הבעלות?
- האם איסור התיקונים, החובה לפנות לסוחר וההכללה “most farmers” נשמרים? אל תתקנו את הניסוח בטופס.

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 09 — creators:423371

| Original | Style Rewrite |
|---|---|
| It was probably inevitable that the Right's economic populism would degenerate into promises of more government checks. Early in the week, the administration floated the idea of redirecting federal childcare aid so low-income married stay-at-home parents could get a $9,000 subsidy per child for daycare. | Promises of more government checks were probably the inevitable destination of the Right's economic populism as it degenerated. Early in the week, the administration floated a proposal to redirect federal childcare aid, allowing low-income married stay-at-home parents to receive a $9,000 subsidy per child for daycare. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| It was | Promises of more government checks were |
| ∅ | the |
| that | destination of |
| would degenerate into promises of more government checks. | as it degenerated. |
| the idea of redirecting | a proposal to redirect |
| aid so | aid, allowing |
| could get | to receive |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- השוו את מיקום probably ואת הקשר בין פופוליזם להבטחות: האם נשמרת אותה הערכה ולא קביעה חזקה יותר?
- בדקו “could get” מול “allowing… to receive”: האם עדיין מדובר בהצעה אפשרית ולא בזכאות שכבר נקבעה?
- ודאו שהסכום, התנאים לקבוצת הזכאים והמטרה per child for daycare נשמרים.

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 10 — creators:296082

| Original | Style Rewrite |
|---|---|
| I beg your pardon. Wrong decade. When Marjorie Taylor Greene was in her mid-40s, she clicked "like" on a Facebook post calling for House Speaker Nancy Pelosi to be shot in the head. She liked comments about executing FBI agents as "deep state" operators trying to undermine former President Donald Trump. She promoted the conspiracy theory that a passenger plane never flew into the Pentagon during the 9/11 attacks. | Wrong decade — I beg your pardon. In her mid-40s, Marjorie Taylor Greene clicked "like" on a Facebook post that called for House Speaker Nancy Pelosi to be shot in the head. Comments urging the execution of FBI agents as "deep state" operators seeking to undermine former President Donald Trump also received her likes. And she promoted the conspiracy theory denying that a passenger plane had flown into the Pentagon during the 9/11 attacks. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| ∅ | Wrong decade — |
| Wrong decade. When | In her mid-40s, |
| was in her mid-40s, she | ∅ |
| calling | that called |
| She liked comments about executing | Comments urging the execution of |
| trying | seeking |
| Trump. She | Trump also received her likes. And she |
| ∅ | denying |
| never flew | had flown |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- האם “never flew” ו־“the conspiracy theory denying… had flown” משמרים את השלילה ואת ייחוסה לתאוריה, ולא למספר?
- בדקו שכל שלוש הפעולות המיוחסות למשתתפת ויעדי האיום נשמרו בלי שינוי תפקידים.

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 11 — creators:421367

| Original | Style Rewrite |
|---|---|
| You couldn't find a wackier candidate than Francesca Hong, the Democratic Socialist vying to become the governor of Wisconsin. She wanted to defund police and abolish ICE, topping it all off with a call to end Thanksgiving. "Saturday Night Live" couldn't have made her up. | Francesca Hong, the Democratic Socialist running for governor of Wisconsin, would be hard to beat for sheer wackiness as a candidate. Defunding the police and abolishing ICE were among her aims, and she topped them off by calling for an end to Thanksgiving. Even "Saturday Night Live" couldn't have invented her. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| You couldn't find a wackier candidate than | ∅ |
| vying to become the | running for |
| Wisconsin. She wanted | Wisconsin, would be hard |
| defund | beat for sheer wackiness as a candidate. Defunding the |
| abolish ICE, topping it all | abolishing ICE were among her aims, and she topped them |
| with a call | by calling for an end |
| end | ∅ |
| ∅ | Even |
| made her up. | invented her. |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- האם “couldn't find a wackier candidate” ו־“hard to beat for sheer wackiness” מבטאים אותה עוצמת ביקורת?
- המילה all נעלמת מהביטוי “topping it all off”; בדקו אם זה שינוי כמותי או שינוי בביטוי רטורי בלבד.
- האם היחס בין שלוש העמדות המיוחסות למועמדת והאירוניה סביב הציטוט נשמרים?

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 12 — creators:208496

| Original | Style Rewrite |
|---|---|
| I participated in perhaps a bit of radio history last week when Steve Forbes and Art Laffer joined me on my syndicated radio show. It may have been the first time these supply-side economics giants were ever together over the airwaves. | Last week, when Steve Forbes and Art Laffer joined me on my syndicated radio show, I may have taken part in a little piece of radio history. Perhaps never before had these giants of supply-side economics appeared together over the airwaves. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| I participated in perhaps a bit of radio history last week | Last week, |
| show. It | show, I |
| been the first time | taken part in a little piece of radio history. Perhaps never before had |
| ∅ | giants of |
| giants were ever | appeared |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- האם “may have been the first time” ו־“Perhaps never before” משמרים את אותו ספק לגבי ראשוניות האירוע?
- בדקו שנשמרת הופעה משותפת של שני המשתתפים באותו מדיום, ולא טענה אחרת על הופעותיהם.

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 13 — creators:3fd01161cd76

| Original | Style Rewrite |
|---|---|
| It's the fall harvest season, when many farm stands and homes decorate with pumpkins, cornstalks and maybe even a straw man. How to make a straw man? Easy — stuff a couple of burlap bags with hay and dress your "man" in an old flannel shirt, overalls and a straw hat. But today's billionaires, corporate elites and other political megadonors have come up with their own version of this creature — stuff a couple of silk pillows with thousand-dollar bills, dress him in a finely tailored suit and — viola! — they turn a common straw man into a congressman. | With fall harvest season comes the familiar sight of pumpkins, cornstalks and perhaps a straw man decorating farm stands and homes. Making a straw man is easy: take a couple of burlap bags, stuff them with hay, then put an old flannel shirt, overalls and a straw hat on your "man." Today's billionaires, corporate elites and other political megadonors, however, have devised a version of their own. Their recipe calls for a couple of silk pillows stuffed with thousand-dollar bills and a finely tailored suit for the fellow. And — viola! — a common straw man becomes a congressman. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| It's the | With |
| season, when many | season comes the familiar sight of pumpkins, cornstalks and perhaps a straw man decorating |
| homes decorate with pumpkins, cornstalks and maybe even | homes. Making |
| man. How to make a straw man? Easy — stuff | man is easy: take |
| bags | bags, stuff them |
| hay and dress your "man" in | hay, then put |
| hat. But today's | hat on your "man." Today's |
| megadonors | megadonors, however, |
| come up with their own | devised a |
| this creature — stuff | their own. Their recipe calls for |
| ∅ | stuffed |
| bills, dress him in | bills and |
| and | for the fellow. And |
| they turn | ∅ |
| into | becomes |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- המקור אומר “many farm stands and homes”; השכתוב מתאר “the familiar sight”. האם היקף התופעה נשמר?
- בדקו את הציטוט “man” והפיסוק שבתוכו, ואת כל רכיבי המטאפורה של יצירת איש קש/חבר קונגרס.
- האם עוצמת הסאטירה והייחוס לתורמים הפוליטיים נשמרים לאחר שינוי מבנה המתכון?

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 14 — creators:421811

| Original | Style Rewrite |
|---|---|
| You know who. The conqueror whose voice, face and deeds are inescapable. Donald Trump had never heard of William the Conqueror when he visited England, but he loved the word and the idea for his presidency. He also has Napoleon Bonaparte and Julius Caesar "great man" delusions. | You know who: Donald Trump, the conqueror whose voice, face and deeds cannot be escaped. On his visit to England, Trump had never heard of William the Conqueror, yet he loved both the word and the idea as applied to his presidency. Delusions of being a Napoleon Bonaparte or Julius Caesar "great man" are his as well. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| who. The | who: Donald Trump, the |
| are inescapable. Donald | cannot be escaped. On his visit to England, |
| Conqueror when he visited England, but | Conqueror, yet |
| ∅ | both |
| for | as applied to |
| He also has | Delusions of being a |
| and | or |
| delusions. | are his as well. |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- האם “inescapable” מול “cannot be escaped” הוא אותו תוכן למרות שינוי בסמן השלילה?
- בדקו “the word and the idea” מול “both…”; הופעת both אינה בהכרח תוספת משמעות.
- המקור מחבר Napoleon Bonaparte ו־Julius Caesar ב־and, והשכתוב ב־or; האם הקשר והמסגור נשמרים?

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


## זוג 15 — creators:213461

| Original | Style Rewrite |
|---|---|
| Much as he did in his command performance before the United Nations, when he took back control of U.S. foreign policy, President Donald Trump has seized and energized the tax cut issue. Almost daily, he is pounding away on the themes of faster economic growth and more take-home pay, arguing that his plan will make America's economy great again. | President Donald Trump has seized the tax cut issue and given it new energy, much as he took back control of U.S. foreign policy in his command performance before the United Nations. Nearly every day, he pounds away at faster economic growth and greater take-home pay, arguing that his plan will make America's economy great again. |

### מה השתנה בניסוח — הבדלים מילוליים

| קטע במקור | קטע בשכתוב |
|---|---|
| Much | President Donald Trump has seized the tax cut issue and given it new energy, much |
| did | took back control of U.S. foreign policy |
| Nations, when | Nations. Nearly every day, |
| took back control of U.S. foreign policy, President Donald Trump has seized and energized the tax cut issue. Almost daily, he is pounding | pounds |
| on the themes of | at |
| more | greater |

### פרטים לבדיקה אנושית — שאלות, לא הכרעות

- השוו “Almost daily” ל־“Nearly every day”: האם אותה תדירות מסויגת נשמרת?
- בדקו שהקביעה על foreign policy והטענה על תכנית המס עדיין מיוחסות באותו אופן ושעוצמת השבח נשמרת.
- אין כאן דגל פסילה ב־guards הקיימים; הבחירה נובעת מרמז כמתים תיאורי ואינה הכרעה שנוצר כשל.

### הכרעת הסוקר/ת

| שדה | תשובה — Yes / No / Borderline |
|---|---|
| Meaning Preserved | |
| Narrative Preserved | |
| Style Change Valid | |
| הערות וביטויים תומכים | |


---

## הוראות נפרדות לתיוג Left/Right

הוראות מלאות וקישורים לטפסי המקור נמצאים ב־[LEFT_RIGHT_LABELING_GUIDE_HE.md](LEFT_RIGHT_LABELING_GUIDE_HE.md). התיוג נעשה על Original, לא על השכתוב ולא לפי דגלי השימור.
