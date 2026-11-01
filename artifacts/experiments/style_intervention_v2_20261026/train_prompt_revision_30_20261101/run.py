"""TRAIN-only development: regenerate 30 normalized texts using the user's prompt.

Inputs: frozen 30-example pack; ORIGINAL text alone is sent to the generator.
Outputs here: new rewrites, old/new comparisons, identical automatic screens,
style metrics, readable report and immutable-input audit. No training or LLM judge.
Run --stage all (prepare -> generate -> validate -> report in separate processes).
"""
from pathlib import Path
import argparse, collections, concurrent.futures, csv, datetime, hashlib
import importlib.util, json, os, re, subprocess, sys, time, urllib.request

OUT=Path(__file__).resolve().parent
PARENT=OUT.parent
ROOT=OUT.parents[3]
PREVIOUS=ROOT/'artifacts/experiments/verified_human_style_followup_20261026'
PROMPT='''Rewrite the text to substantially alter the author's writing style while preserving the exact meaning, political/narrative stance, factual claims, attribution, certainty, negation, entities, temporal information, and causal relationships.

The goal is NOT to summarize or soften the text. The goal is to reduce author-specific stylistic signals.

Requirements:

- Preserve all factual claims.
- Preserve the same political/narrative stance.
- Preserve attribution exactly: who said, claimed, alleged, believed, or did what.
- Preserve certainty markers such as "allegedly", "likely", "may", "could", "claims", "supposedly", and similar expressions.
- Preserve negations.
- Preserve all named entities and numerical information.
- Do not introduce new claims, interpretations, opinions, or framing.
- Do not remove politically relevant claims or rhetorical content that contributes to the narrative.
- Do not rewrite text inside quotation marks.
- Do not add meta-text or explanations.

At the same time, substantially change the writing style by changing several of the following:

- sentence structure
- clause order
- sentence length distribution
- active/passive construction
- first-person phrasing where possible without changing meaning
- conversational expressions
- idioms
- rhetorical questions
- discourse markers
- punctuation patterns

Avoid merely replacing individual words with synonyms.

The rewritten text should sound like it was written by a different author while expressing the same content and stance.

Return only the rewritten text.'''


def now():
    """Return an unambiguous UTC audit timestamp."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    """Hash immutable research inputs and outputs."""
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def records(path):
    """Load CSV strings without modifying labels or texts."""
    with path.open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))


def write_csv(name,rows):
    """Write a derived CSV only under this development-run directory."""
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def dump(name,value):
    """Save versioned JSON metadata and audit counts."""
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def read(name):
    """Load run-local JSON."""
    return json.loads((OUT/name).read_text(encoding='utf8'))


def imported_style_module():
    """Import existing style measurement functions without invoking any stages."""
    spec=importlib.util.spec_from_file_location('v2_style_helpers',PARENT/'study.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def event(stage,**extra):
    """Record execution provenance; never consult narrative predictions."""
    with (OUT/'audit_trail.jsonl').open('a',encoding='utf8') as stream:
        stream.write(json.dumps(dict(stage=stage,timestamp_utc=now(),code_sha256=sha(Path(__file__)),**extra),ensure_ascii=False)+'\n')


def prepare():
    """Freeze the exact selected IDs, labels, old versions, prompt and no-test scope."""
    if (OUT/'protocol.json').exists():return
    corpus=records(PARENT/'analysis_cohort.csv');by_id={r['row_id']:r for r in corpus}
    selected=records(PARENT/'external_review_30_20261101/review_30_train_only.csv')
    assert len(selected)==30 and len({r['ID'] for r in selected})==30
    cohort=[by_id[r['ID']] for r in selected]
    assert all(r['split']=='train' for r in cohort)
    held_out={r['author'] for r in corpus if r['split']!='train'}
    assert not held_out&{r['author'] for r in cohort}
    assert all(r['Original']==by_id[r['ID']]['text'] for r in selected)
    write_csv('analysis_cohort.csv',cohort)
    write_csv('frozen_comparison_inputs.csv',[dict(ID=r['ID'],Author=r['Author'],split='train',
        proposed_narrative=r['proposed_narrative'],Original=r['Original'],Old_Normalized=r['Normalized'],
        selection_group=r['selection_group']) for r in selected])
    (OUT/'prompt.txt').write_text(PROMPT,encoding='utf8')
    manifest=json.loads((PARENT/'generator_manifest.json').read_text(encoding='utf8'))
    dump('generator_manifest.json',manifest)
    dump('protocol.json',dict(created_at_utc=now(),n=30,scope='Selected TRAIN sources only; development, not held-out evaluation',
        source_pack_sha256=sha(PARENT/'external_review_30_20261101/review_30_train_only.csv'),
        prompt_sha256=sha(OUT/'prompt.txt'),generator=manifest,seed=20261026,temperature=0,max_tokens=320,
        attempts_per_text=1,generation_input='User prompt in system message + Original alone in user message',
        old_rewrites_labels_authors_scores_sent_to_generator=False,uses_external_review_for_selection=False,
        semantic_similarity_threshold=.85,bidirectional_nli_threshold=.6,
        style_thresholds='Identical V2 style_metrics: edit>=.15 and sentence change>=.15 or punctuation>=1 or contraction change>=1',
        training=False,human_validation=False,automatic_results_are_not_proof_of_preservation=True,
        comparison='Same 30 IDs; New vs Old Normalized; no candidate ranking or automatic retries'))
    protected={str(p.relative_to(ROOT)):sha(p) for p in PARENT.rglob('*') if p.is_file() and OUT not in p.parents and
               '__pycache__' not in p.parts and 'runtime' not in p.parts}
    for relative,digest in json.loads((PREVIOUS/'protected_inputs_sha256.json').read_text(encoding='utf8')).items():
        path=ROOT/relative;assert sha(path)==digest;protected[relative]=digest
    dump('protected_inputs_sha256.json',protected)
    event('prepare',n=30,train_authors=sorted({r['author'] for r in cohort}),protocol_sha256=sha(OUT/'protocol.json'))


def generate():
    """Generate one candidate from each Original using only the specified prompt."""
    manifest=read('generator_manifest.json');model=PREVIOUS/'runtime'/manifest['file']
    executable=PREVIOUS/'runtime_llama/llama-server.exe'
    assert sha(model)==manifest['sha256']
    prompt=(OUT/'prompt.txt').read_text(encoding='utf8');assert sha(OUT/'prompt.txt')==read('protocol.json')['prompt_sha256']
    path=OUT/'generated_rewrites.jsonl'
    existing=[json.loads(s) for s in path.read_text(encoding='utf8').splitlines()] if path.exists() else []
    done={r['row_id'] for r in existing}
    tasks=[r for r in records(OUT/'analysis_cohort.csv') if r['row_id'] not in done]
    if not tasks:return
    runtime=OUT/'runtime';runtime.mkdir(exist_ok=True)
    endpoint='http://127.0.0.1:18094'
    server=subprocess.Popen([str(executable),'-m',str(model),'--host','127.0.0.1','--port','18094','-t','8','-tb','8','-np','4','-c','8192','--no-webui'],
        cwd=runtime,stdout=(runtime/'stdout.log').open('a'),stderr=(runtime/'stderr.log').open('a'),
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    try:
        for _ in range(120):
            try:
                with urllib.request.urlopen(endpoint+'/health',timeout=2) as response:
                    if response.status==200:break
            except Exception:time.sleep(1)
        else:raise RuntimeError('Local generator did not start')
        def request(record):
            """Send only original text; save request hash and raw model response."""
            payload=dict(messages=[dict(role='system',content=prompt),dict(role='user',content=record['text'])],
                temperature=0,seed=20261026,max_tokens=320,repeat_penalty=1.,top_k=1,top_p=1.,min_p=0.,cache_prompt=True)
            req=urllib.request.Request(endpoint+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=900) as response:result=json.load(response)
            choice=result['choices'][0]
            return dict(row_id=record['row_id'],condition='Normalized',original=record['text'],rewrite=choice['message']['content'].strip(),
                truncated=choice['finish_reason']=='length',timestamp_utc=now(),usage=result.get('usage'),seed=20261026,
                request_sha256=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest(),
                prompt_sha256=read('protocol.json')['prompt_sha256'],prompt_content_sha256=hashlib.sha256(prompt.encode()).hexdigest(),generator=manifest['repo'],generator_revision=manifest['revision'])
        with concurrent.futures.ThreadPoolExecutor(4) as pool,path.open('a',encoding='utf8') as stream:
            for i,result in enumerate(pool.map(request,tasks),1):
                stream.write(json.dumps(result,ensure_ascii=False)+'\n');stream.flush()
                dump('generation_status.json',dict(completed=len(done)+i,total=30,timestamp_utc=now()))
                print(f'New Normalized {len(done)+i}/30',flush=True)
    finally:
        server.terminate();server.wait(timeout=30)
    event('generate',n=30,model_sha256=manifest['sha256'],runtime_sha256=sha(executable),output_sha256=sha(path))


def validate():
    """Call precisely the existing automatic validation code, redirecting outputs."""
    generated=[json.loads(s) for s in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]
    assert len(generated)==30 and len({r['row_id'] for r in generated})==30
    helper=imported_style_module();engine=helper.load_engine();engine.OUT=OUT;engine.base.OUT=OUT
    engine.validate()
    method=read('validation_method.json')
    if 'inherited_reference_protocol' not in method:
        method['inherited_reference_protocol']=method.pop('protocol')
    method['protocol']=read('protocol.json')
    method['scope']='Automatic preservation screening of 30 new Normalized TRAIN candidates only'
    dump('validation_method.json',method)
    event('validate',n=30,method_sha256=sha(OUT/'validation_method.json'),validation_sha256=sha(OUT/'rewrite_validation.csv'))


def md_table(headers,rows):
    """Produce readable comparison tables without modifying source text."""
    def cell(v):return str(v).replace('|','\\|').replace('\n','<br>')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(cell(v) for v in row)+' |' for row in rows])


def report():
    """Compare saved automatic outcomes; report risks, not semantic adjudication."""
    helper=imported_style_module();engine=helper.load_engine();np=engine.np
    cohort=records(OUT/'analysis_cohort.csv');old={r['ID']:r for r in records(OUT/'frozen_comparison_inputs.csv')}
    generated={r['row_id']:r for r in [json.loads(s) for s in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]}
    prompt=(OUT/'prompt.txt').read_text(encoding='utf8');request_checks=[]
    for r in cohort:
        payload=dict(messages=[dict(role='system',content=prompt),dict(role='user',content=r['text'])],
            temperature=0,seed=20261026,max_tokens=320,repeat_penalty=1.,top_k=1,top_p=1.,min_p=0.,cache_prompt=True)
        matches=generated[r['row_id']]['request_sha256']==hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        assert matches and generated[r['row_id']]['original']==r['text']
        request_checks.append(dict(ID=r['row_id'],original_only_request_hash_matches=matches))
    dump('request_integrity_audit.json',dict(n=30,all_passed=True,checks=request_checks))
    new_validation={r['row_id']:r for r in records(OUT/'rewrite_validation.csv')}
    old_validation={r['row_id']:r for r in records(PARENT/'rewrite_validation.csv') if r['condition']=='Normalized'}
    comparison=[];metrics=[];explicit=[];changes=[]
    feature_names=json.loads((PREVIOUS/'style_feature_definitions.json').read_text(encoding='utf8'))['names']
    scaling=json.loads((PARENT/'style_feature_scaling.json').read_text(encoding='utf8'))
    assert feature_names==scaling['names']
    scale=np.array(scaling['scale'])
    for record in cohort:
        rid=record['row_id'];original=record['text'];previous=old[rid]['Old_Normalized'];new=generated[rid]['rewrite']
        row=dict(ID=rid,Author=record['author_name'],split='train',proposed_narrative=record['narrative_name'],Original=original,Old_Normalized=previous,New_Normalized=new)
        values={c:helper.style_metrics(original,text) for c,text in [('Old',previous),('New',new)]}
        for c,screen in [('Old',old_validation[rid]),('New',new_validation[rid])]:
            row[c+'_automatic_pass']=screen['passed'];row[c+'_rejection_reasons']=screen['rejection_reasons']
            row[c+'_style_proxy_substantial']=values[c]['substantial_style_change']
            metrics.append(dict(ID=rid,version=c,**values[c]))
        row['new_both_automatic']=row['New_automatic_pass']=='True' and values['New']['substantial_style_change']
        row['automatic_screen_resolved']=row['Old_automatic_pass']=='False' and row['New_automatic_pass']=='True'
        row['new_automatic_failure']=row['Old_automatic_pass']=='True' and row['New_automatic_pass']=='False'
        row['weak_style_intervention_resolved']=not values['Old']['substantial_style_change'] and values['New']['substantial_style_change'] and row['New_automatic_pass']=='True'
        row['new_validation_json']=json.dumps(new_validation[rid],ensure_ascii=False)
        # Additional quotation diagnostic is recorded separately, never replaces old guards.
        quotes=lambda text:re.findall(r'"([^"\n]+)"|“([^”\n]+)”',text)
        row['new_quotes_verbatim_same_order']=quotes(original)==quotes(new)
        row['new_quotes_verbatim_preserved']=sorted(a or b for a,b in quotes(original))==sorted(a or b for a,b in quotes(new))
        comparison.append(row)
        original_features=np.array(engine.style_features(original))
        for version,text in [('Old',previous),('New',new)]:
            changed_features=np.array(engine.style_features(text))
            for measurement in metrics:
                if measurement['ID']==rid and measurement['version']==version:
                    measurement['explicit_style_mean_abs_standardized_change']=float(np.mean(np.abs(changed_features-original_features)/scale))
            for name,a,b in zip(feature_names,original_features,changed_features):
                explicit.append(dict(ID=rid,version=version,feature=name,original=float(a),rewrite=float(b),delta=float(b-a)))
        old_reasons=set(old_validation[rid]['rejection_reasons'].split('|'))-{''};new_reasons=set(new_validation[rid]['rejection_reasons'].split('|'))-{''}
        changes.append(dict(ID=rid,removed_automatic_flags='|'.join(sorted(old_reasons-new_reasons)),added_automatic_flags='|'.join(sorted(new_reasons-old_reasons)),
            old_pass=row['Old_automatic_pass'],new_pass=row['New_automatic_pass'],
            semantic_drift_status='Automatic risk flags only; no new LLM/human adjudication'))
    write_csv('comparison_30.csv',comparison);write_csv('style_metrics_old_new.csv',metrics)
    write_csv('explicit_style_changes_old_new.csv',explicit);write_csv('automatic_flag_changes.csv',changes)
    totals={}
    for version in ['Old','New']:
        totals[version]=dict(automatic_pass=sum(r[version+'_automatic_pass']=='True' for r in comparison),
            substantial_style_proxy=sum(r[version+'_style_proxy_substantial'] for r in comparison),
            both=sum(r[version+'_automatic_pass']=='True' and r[version+'_style_proxy_substantial'] for r in comparison),
            exact_copies=sum(m['exact_copy'] for m in metrics if m['version']==version))
    resolved=[r['ID'] for r in comparison if r['automatic_screen_resolved']]
    introduced=[r['ID'] for r in comparison if r['new_automatic_failure']]
    style_resolved=[r['ID'] for r in comparison if r['weak_style_intervention_resolved']]
    risks=[r['row_id'] for r in new_validation.values() if r['passed']=='False']
    dump('summary.json',dict(n=30,scope='TRAIN-only development; not held-out evidence',totals=totals,
        automatic_failures_resolved=resolved,new_automatic_failures=introduced,new_flagged_sources=risks,
        weak_style_intervention_resolved=style_resolved,
        new_both_ids=[r['ID'] for r in comparison if r['new_both_automatic']],
        new_truncated=sum(r['truncated'] for r in generated.values()),
        new_verbatim_quotes_failed=[r['ID'] for r in comparison if not r['new_quotes_verbatim_preserved']],
        semantic_preservation_human_verified=False,style_change_human_verified=False,no_training=True))
    (OUT/'COMPARISON_30_HE.md').write_text('# Original | Old Normalized | New Normalized — 30 דוגמאות אימון\n\n'
        'כל הטקסטים כאן הם אותם 30 מקורות train. הישן נשמר כקלט להשוואה בלבד ולא הועבר למודל. אין כאן אימות אנושי.\n\n'+
        md_table(['ID','Author','Original','Old Normalized','New Normalized'],[[r[k] for k in ['ID','Author','Original','Old_Normalized','New_Normalized']] for r in comparison])+'\n',encoding='utf8')
    counts=collections.Counter(reason for r in new_validation.values() for reason in r['rejection_reasons'].split('|') if reason)
    lines=['# שכתוב מחדש של 30 טקסטי אימון — prompt חדש','',
        '## מה בוצע','',
        'ה־prompt שסיפקה המשתמשת הועבר ללא תווית/שם כותב/ציונים, עם Original בלבד כקלט. נוצר מועמד יחיד לכל מקור. אותו Qwen2.5-3B-Instruct Q4_K_M קפוא, seed 20261026, temperature=0 ותקציב פלט 320 כמו ב־V2. לא הועברו למודל שכתובים קודמים או דירוגי External LLM Review. לא נבחר המועמד לפי תחזית מסווג, לא שונו ספים ולא בוצע אימון.','',
        '## תוצאות אוטומטיות בלבד','',md_table(['גרסה','עברו כל מסנני השימור','שינוי style משמעותי לפי proxy','שניהם יחד','העתקים מדויקים'],[[v,*[totals[v][k] for k in ['automatic_pass','substantial_style_proxy','both','exact_copies']]] for v in ['Old','New']]),'',
        'מעבר במסננים אינו הוכחה לשימור meaning/stance/framing. דגל substantial הוא כלל המדידה הקיים, לא הכרעה ששינוי הסגנון אמיתי. אימות אנושי ובדיקת LLM חיצונית של הגרסה החדשה לא בוצעו.','',
        '## היכן הוסרו/נוספו דגלי כשל','',
        'כשל סינון קודם נפתר אוטומטית ב־'+str(len(resolved))+' דוגמאות: '+', '.join(resolved)+'.',
        'שינוי סגנוני חלש הפך לשינוי משמעותי לפי proxy שעבר סינון ב־'+str(len(style_resolved))+' דוגמאות: '+', '.join(style_resolved)+'.',
        'נוצר כשל אוטומטי לאחר מעבר קודם ב־'+str(len(introduced))+' דוגמאות: '+', '.join(introduced)+'.',
        'זיהוי הסיכון נעשה מהבדיקות בלבד. אין לייחס שינוי certainty/attribution או semantic drift מאומת רק לפי דגל אוטומטי. ניתן לעיין במקור ובשכתובים בטבלת ההשוואה.','',
        md_table(['ID','דגלים שנעלמו','דגלים שנוספו','עבר קודם','עבר חדש'],[[r[k] for k in ['ID','removed_automatic_flags','added_automatic_flags','old_pass','new_pass']] for r in changes]),'',
        '## סיבות פסילה בגרסה החדשה','',md_table(['דגל','מספר'],list(counts.items())),
        'סיבות חופפות. המודלים והספים לא שונו: MPNet cosine≥0.85, DeBERTa entailment≥0.6 בשני הכיוונים, NER ושמירת מספרים/שלילה/ודאות/ייחוס/מסגור/ציטוטים, זמן עתיד, אורך ואי־קטיעה.',
        'נוסף דיאגנוסטיקת ציטוטים verbatim ובאותו סדר, בלי לשנות את החלטת המסנן הקיים. פירוט ב־comparison_30.csv.','',
        '## מה ניתן להסיק','',
        'זהו סבב פיתוח על 30 דוגמאות אימון שנבחרו במכוון ושכבר נבדקו בעבר. אפשר להשוות עוצמת שינוי ודגלי סיכון אוטומטיים באותם מקורות. אין כאן אומדן הכללה, Author Identification, Macro-F1 או בדיקה על test. התוצאות אינן מאפשרות להכריז על הסרת shortcut או causality. אין להעביר אישורי LLM ישנים לשכתובים החדשים.','',
        '## תוצרים ושחזור','',
        '- COMPARISON_30_HE.md ו־comparison_30.csv: כל שלוש הגרסאות לכל ID.',
        '- rewrite_validation.csv: כל תוצאות הבדיקות בגרסה החדשה.',
        '- style_metrics_old_new.csv ו־explicit_style_changes_old_new.csv: אותם מדדי V2 ו־66 מאפיינים מפורשים.',
        '- prompt.txt, protocol.json, generator_manifest.json ו־audit_trail.jsonl: מקור ההוראות, גרסאות, seed, ספים וזמנים.',
        '- integrity_audit.json: אימות שמקור, תוויות, splits, תוצרי עבר וקוד האימון לא השתנו.',
        '- להפעלה: python artifacts/experiments/style_intervention_v2_20261026/train_prompt_revision_30_20261101/run.py --stage all',
        '- נדרשת סביבת Python הקיימת, מודלים ב־cache וה־runtime של הניסוי הקודם. הריצה מסתיימת בדוח, ללא אימון.','']
    (OUT/'REPORT_HE.md').write_text('\n'.join(lines),encoding='utf8')
    example_ids=['creators:120669','creators:419062','creators:212505','creators:421279','creators:97c9d6b9ac1b','creators:298495','creators:114783']
    examples=[r for rid in example_ids for r in comparison if r['ID']==rid]
    with (OUT/'REPORT_HE.md').open('a',encoding='utf8') as stream:
        stream.write('\n## דוגמאות ממוקדות להשוואה ולבדיקה חיצונית\n\n')
        stream.write('הדוגמאות להלן מציגות טקסט ודגלים בלבד, ללא הכרעת שימור חדשה. '
            'ב־creators:212505 מופיע 10 במקור ו־ten בחדש, ולכן כלל המספרים הלקסיקלי פוסל; '
            'אין להסיק מפסילה כזו לבדה שינוי בכמות. ב־creators:421279 הוחלף may ב־might. '
            'ב־creators:97c9d6b9ac1b מופיע bulldozers בפלט החדש; ב־creators:298495 '
            'הביטוי strangers מוחלף ב־anonymous sources; וב־creators:114783 הציטוט המקורי אינו נשמר כלשונו. '
            'יש לבחון את ההשלכות הסמנטיות בבדיקה חיצונית נפרדת, ולא לאשר/לפסול משמעות כאן על סמך קריאת עוזר נוספת.\n\n')
        stream.write(md_table(['ID','Original','Old Normalized','New Normalized','דגלים חדשים'],
            [[r[k] for k in ['ID','Original','Old_Normalized','New_Normalized','New_rejection_reasons']] for r in examples])+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4));positions=np.arange(3);width=.35
    for offset,version in [(-width/2,'Old'),(width/2,'New')]:
        bars=ax.bar(positions+offset,[totals[version][k] for k in ['automatic_pass','substantial_style_proxy','both']],width,label=version+' Normalized')
        ax.bar_label(bars,padding=3)
    ax.set_xticks(positions,['Automatic meaning screen','Substantial style proxy','Both']);ax.set_ylim(0,33)
    ax.set(title='Prompt revision: same 30 TRAIN texts',ylabel='Source texts (not human-verified)');ax.legend();fig.tight_layout()
    fig.savefig(OUT/'comparison_metrics.png',dpi=160);plt.close(fig)
    with (OUT/'REPORT_HE.md').open('a',encoding='utf8') as stream:
        stream.write('\n![השוואה אוטומטית בין הנרמול הישן לחדש באותם 30 טקסטים](comparison_metrics.png)\n')
    protected=read('protected_inputs_sha256.json');changed=[name for name,digest in protected.items() if sha(ROOT/name)!=digest]
    assert not changed,changed
    assert all(r['split']=='train' and r['narrative_name']==old[r['row_id']]['proposed_narrative'] for r in cohort)
    dump('integrity_audit.json',dict(passed=True,n=30,protected_files=len(protected),changed_files=changed,
        train_only=True,no_labels_changed=True,no_split_changed=True,no_training=True,all_new_records_screened=len(new_validation)==30,
        all_old_versions_preserved=True,original_only_generator_inputs=True,human_fields_not_filled=True))
    event('report',n=30,summary_sha256=sha(OUT/'summary.json'),protected_files_unchanged=len(protected))
    print(json.dumps(totals),flush=True)


def main():
    """Run sequential stages in separate processes to avoid model-memory overlap."""
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',required=True,choices=['prepare','generate','validate','report','all'])
    stage=parser.parse_args().stage
    if stage=='all':
        for step in ['prepare','generate','validate','report']:
            subprocess.run([sys.executable,'-u',str(Path(__file__)), '--stage',step],check=True)
    else:globals()[stage]()


if __name__=='__main__':main()
