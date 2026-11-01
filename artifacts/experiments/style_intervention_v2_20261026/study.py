"""Style-intervention V2: generation, human-review packaging, and gated evaluation.

Inputs: frozen 218-text predecessor corpus, author split, paraphrases and models.
Outputs: new rewrites, automatic screens, editable human-review CSV/Markdown,
audit events, style measurements and (only after real review) five-seed results.
Run `python study.py --help`. No predecessor file is modified.
"""
from pathlib import Path
import argparse, collections, concurrent.futures, datetime, difflib, hashlib
import importlib.util, itertools, json, os, re, shutil, subprocess, sys, time, urllib.request
import csv

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PREVIOUS = ROOT / 'artifacts/experiments/verified_human_style_followup_20261026'
SEEDS = [7, 42, 123, 2026, 31415]
FIELDS = ['narrative_preserved', 'stance_preserved', 'framing_preserved', 'facts_preserved',
          'entities_preserved', 'negation_preserved', 'certainty_preserved',
          'attribution_preserved', 'claim_added', 'claim_omitted']
COMMON = '''Rewrite the entire input faithfully. Output only the rewritten English text.
Preserve EVERY assertion, allegation, evaluation, political stance and framing.
Preserve actors, actions, causal roles, entities, dates, numbers, negation and its
scope, certainty, tense, attribution, first-person referents and implied judgments.
Keep names, quoted spans, numbers, modal/uncertainty words and politically evaluative
words verbatim. Never resolve an ambiguous pronoun or invent a motive. Never add,
omit, weaken or strengthen a claim. A rhetorical question must remain a question
if making it declarative changes its presupposition. Preserve the language.
Do not add a title, explanation or commentary.'''
NORMALIZATION = COMMON + '''
TASK: actively recast the prose into a single house style: plain, moderately
formal editorial English, complete sentences, standard punctuation, mostly short
subject-verb-object clauses. This is a syntactic rewrite, NOT a light copy edit.
Change clause order within sentences and the placement of attribution when safe.
Split a long sentence or combine very short sentences when all logical relations
remain explicit. Replace non-evaluative idioms with literal equivalents and remove
decorative fillers. Prefer direct grammatical constructions to ornate ones.
Do not copy the original sentence structure throughout. If already plain, recast
the opening construction and clause arrangement rather than returning the input.
Retain evaluative expressions, insults, uncertainty and rhetorical implication even
when they sound informal. Changing these would change framing. Aim for similar
length (80-120%); preserving all meaning takes priority over word count or edits.
Before answering silently compare every claim and attribution to the input.'''


def timestamp():
    """Return UTC ISO timestamp for audit records."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read_json(path):
    """Read a UTF-8 JSON research input."""
    return json.loads(Path(path).read_text(encoding='utf8'))


def write_json(name, value):
    """Write a JSON output only inside this versioned experiment directory."""
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def rows(path):
    """Load CSV rows as strings, accepting Excel's UTF-8 BOM."""
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def write_csv(name, records, fields=None):
    """Save an editable CSV; explicit fields permit empty result sets."""
    records = list(records)
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def sha(path):
    """Hash a frozen input or produced artifact without loading it all in RAM."""
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def event(stage, inputs, outputs, before, after, **extra):
    """Append artifact hashes, model/config and counts to the audit trail."""
    record = dict(timestamp=timestamp(), stage=stage, before=before, after=after,
                  inputs={str(p): sha(p) for p in inputs if Path(p).is_file()},
                  outputs={str(p): sha(p) for p in outputs if Path(p).is_file()},
                  code_sha256={p.name:sha(p) for p in OUT.glob('*.py')},
                  seed=20261026, thresholds=dict(similarity=.85, bidirectional_nli=.6,
                  word_edit_fraction=.15, sentence_mean_relative_change=.15,
                  punctuation_l1_per100=1.), **extra)
    with (OUT / 'audit_trail.jsonl').open('a', encoding='utf8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + '\n')


def load_engine():
    """Reuse frozen previous validation/training code; redirect ALL output paths."""
    spec = importlib.util.spec_from_file_location('frozen_followup', PREVIOUS / 'experiment.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    module.base.OUT = OUT
    module.base.CONFIG.update(epochs=20, lr=.001, batch_size=16)
    return module


def prepare():
    """Freeze the old cohort/split/control and preregister intervention thresholds."""
    if not (OUT/'environment.json').exists():
        import importlib.metadata, platform
        packages={}
        for package in ['torch','transformers','sentence-transformers','numpy','pandas','scikit-learn','matplotlib']:
            try: packages[package]=importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:packages[package]='unavailable'
        write_json('environment.json',dict(python=sys.version,executable=sys.executable,platform=platform.platform(),packages=packages,
            runtime_sha256=sha(PREVIOUS/'runtime_llama/llama-server.exe'),runtime_release='llama.cpp b11887',
            inherited_analysis_code_sha256=sha(PREVIOUS/'experiment.py'),timestamp=timestamp()))
    if (OUT / 'protocol.json').exists():
        return
    for name in ['analysis_cohort.csv', 'author_splits.csv', 'split_definitions.csv',
                 'author_registry.json', 'generator_manifest.json', 'counterfactual_selection.csv']:
        shutil.copyfile(PREVIOUS / name, OUT / name)
    for name in ['analysis_cohort.csv', 'author_splits.csv', 'split_definitions.csv']:
        assert sha(OUT / name) == sha(PREVIOUS / name)
    old = [json.loads(line) for line in (PREVIOUS / 'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]
    control = [r for r in old if r['condition'] in ['Formatting', 'Paraphrase']]
    (OUT / 'generated_rewrites.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in control), encoding='utf8')
    write_json('rewrite_prompts.json', dict(Normalized=NORMALIZATION,
        Paraphrase=read_json(PREVIOUS / 'rewrite_prompts.json')['prompts']['Paraphrase'],
        control='Frozen previous paraphrases; no retry, outcome selection or new narrative label given to generator.'))
    write_json('protocol.json', dict(created_at=timestamp(), seeds=SEEDS, epochs=20,
        source_texts=218, previous_matched=113, same_author_split=True,
        primary='Human-reviewed, all-condition matched cohort, Normalized minus Paraphrase Macro-F1',
        human_gate='No new narrative fitting before complete identifiable human review. No AI self-review counts as human.',
        human_labels=['Left-wing', 'Right-wing', 'Unclear'],
        significance='Descriptive five-seed estimates; no causal proof or confirmatory p-value.',
        intervention='One new Normalized per source. Previous Paraphrase/Formatting held fixed. No classifier consulted.',
        validation='Unchanged previous similarity .85, bidirectional NLI .6 and ALL lexical/entity/truncation guards.',
        substantial_style='word edit >= .15 AND (sentence-mean relative change >= .15 OR punctuation L1/100 words >=1 OR contraction-rate change >=1/100 words)',
        style_caution='Operational syntax/punctuation proxies, not validated causal or formality ground truth.',
        expansion_ceiling='Frozen Paraphrase passed 120/218 previously; matched cannot exceed 120 without changing control.',
        generation=dict(model=read_json(OUT/'generator_manifest.json'),temperature=0,max_tokens=320,seed=20261026),
        source_provenance='New analysis reuses existing bylined excerpts; no new author identity claims.'))
    protected = {str(p.relative_to(ROOT)): sha(p) for p in PREVIOUS.rglob('*') if p.is_file() and not any(v in p.parts for v in ['runtime','runtime_llama','sources','__pycache__','psutil','psutil-6.1.1.dist-info'])}
    write_json('protected_previous_sha256.json', protected)
    event('prepare', [PREVIOUS/'analysis_cohort.csv', PREVIOUS/'generated_rewrites.jsonl'],
          [OUT/'protocol.json', OUT/'rewrite_prompts.json', OUT/'study.py'], 218, 218,
          model=read_json(OUT/'generator_manifest.json'))


def generate():
    """Generate exactly one new normalized version per source; resume by source ID."""
    endpoint = 'http://127.0.0.1:18093'
    manifest = read_json(OUT / 'generator_manifest.json')
    runtime = OUT / 'runtime'; runtime.mkdir(exist_ok=True)
    executable = PREVIOUS/'runtime_llama/llama-server.exe'
    model = PREVIOUS/'runtime'/manifest['file']
    assert sha(model) == manifest['sha256']
    server = subprocess.Popen([str(executable), '-m', str(model), '--host', '127.0.0.1',
        '--port', '18093', '-t','8','-tb','8','-np','4','-c','8192','--no-webui'],
        cwd=runtime, stdout=(runtime/'stdout.log').open('a'), stderr=(runtime/'stderr.log').open('a'),
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    try:
        for _ in range(120):
            try:
                with urllib.request.urlopen(endpoint+'/health', timeout=2) as response:
                    if response.status==200: break
            except Exception: time.sleep(1)
        else: raise RuntimeError('Local model failed to start')
        current = [json.loads(s) for s in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]
        done = {r['row_id'] for r in current if r['condition']=='Normalized'}
        tasks = [r for r in rows(OUT/'analysis_cohort.csv') if r['row_id'] not in done]
        def request(record):
            """Send only text and house-style instructions; record full decoding provenance."""
            payload = dict(messages=[dict(role='system',content=NORMALIZATION),dict(role='user',content=record['text'])],
                temperature=0, seed=20261026, max_tokens=320, repeat_penalty=1., top_k=1, top_p=1., min_p=0., cache_prompt=True)
            req=urllib.request.Request(endpoint+'/v1/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req, timeout=900) as response: result=json.load(response)
            choice=result['choices'][0]
            return dict(row_id=record['row_id'],condition='Normalized',original=record['text'],
                rewrite=choice['message']['content'].strip(),truncated=choice['finish_reason']=='length',
                timestamp=timestamp(),generator=manifest,prompt_sha256=hashlib.sha256(NORMALIZATION.encode()).hexdigest(),
                seed=20261026,temperature=0,max_tokens=320,usage=result.get('usage'))
        with concurrent.futures.ThreadPoolExecutor(4) as pool, (OUT/'generated_rewrites.jsonl').open('a',encoding='utf8') as stream:
            for index, result in enumerate(pool.map(request,tasks),1):
                stream.write(json.dumps(result,ensure_ascii=False)+'\n');stream.flush()
                write_json('generation_status.json',dict(completed=len(done)+index,total=218,timestamp=timestamp()))
                print(f'Normalized {len(done)+index}/218',flush=True)
    finally:
        server.terminate();server.wait(timeout=30)
    event('generate',[OUT/'rewrite_prompts.json',OUT/'analysis_cohort.csv'],[OUT/'generated_rewrites.jsonl'],218,218,model=manifest)


def style_metrics(original, rewrite):
    """Return transparent lexical/structural proxies; no semantic model selects edits."""
    def features(text):
        words=re.findall(r'\b\w+\b',text.lower()); n=max(1,len(words))
        sentences=[s for s in re.split(r'[.!?]+',text) if s.strip()]
        punctuation=[100*text.count(p)/n for p in ',;:!?—-()']
        contractions=100*len(re.findall(r"\b\w+['’]\w+\b",text))/n
        informal=100*len(re.findall(r'\b(?:yeah|gonna|gotta|hey|okay|ok|stuff|kinda)\b',text.lower()))/n
        return words,n,n/max(1,len(sentences)),punctuation,contractions,informal,len(sentences)
    a,na,sa,pa,ca,ia,nsa=features(original);b,nb,sb,pb,cb,ib,nsb=features(rewrite)
    edit=1-difflib.SequenceMatcher(None,a,b,autojunk=False).ratio()
    operations=difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()
    replaced=sum(i2-i1 for tag,i1,i2,j1,j2 in operations if tag=='replace')
    deleted=sum(i2-i1 for tag,i1,i2,j1,j2 in operations if tag=='delete')
    inserted=sum(j2-j1 for tag,i1,i2,j1,j2 in operations if tag=='insert')
    structure=abs(sb-sa)/max(1,sa); punctuation=sum(abs(x-y) for x,y in zip(pa,pb))
    substantial=edit>=.15 and (structure>=.15 or punctuation>=1 or abs(cb-ca)>=1)
    return dict(word_edit_fraction=edit,original_words_replaced_pct=100*replaced/na,
        original_words_deleted_pct=100*deleted/na,inserted_words_per100_original=100*inserted/na,
        word_length_change_pct=100*(nb-na)/na,
        mean_sentence_words_original=sa,mean_sentence_words_rewrite=sb,
        sentence_count_original=nsa,sentence_count_rewrite=nsb,
        sentence_mean_relative_change=structure,punctuation_l1_per100=punctuation,
        formality_proxy_delta=(ca+ia)-(cb+ib),contraction_rate_delta=cb-ca,
        exact_copy=original==rewrite,substantial_style_change=substantial,
        style_change_group='substantial' if substantial else ('minimal' if edit<.05 else 'intermediate'))


def package():
    """Build side-by-side manual review and quantitative intervention measurements."""
    corpus=rows(OUT/'analysis_cohort.csv')
    generated=[json.loads(s) for s in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]
    lookup={(r['row_id'],r['condition']):r['rewrite'] for r in generated}
    old={r['row_id']:r['rewrite'] for r in [json.loads(s) for s in (PREVIOUS/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()] if r['condition']=='Normalized'}
    validation={(r['row_id'],r['condition']):r for r in rows(OUT/'rewrite_validation.csv')} if (OUT/'rewrite_validation.csv').exists() else {}
    existing={r['row_id']:r for r in rows(OUT/'human_review.csv')} if (OUT/'human_review.csv').exists() else {}
    review=[];measurements=[]; markdown=['# אימות ידני: מקור מול שכתובים','',
        'יש לסמן בקובץ human_review.csv. שדות ריקים פירושם שלא בוצע אימות. confidence הוא ציון AI בסולם 1–3, לא הסתברות.',
        'לכל שכתוב סמנו yes/no/unclear. claim_added ו־claim_omitted: yes פירושו כשל. אין להשאיר אותם ריקים.',
        'התווית המוצעת גלויה ולכן אינה תיוג בלתי תלוי. אפשר לשנות ל־Left-wing / Right-wing / Unclear.',
        'לתיוג בלתי תלוי השתמשו ב־human_labels_blind.csv; אין בו הצעת AI, כותב או split.','']
    for record in corpus:
        rid=record['row_id']; entry=dict(row_id=rid,original=record['text'],proposed_narrative=record['narrative_name'],
            proposed_confidence_1_to_3=record['confidence_a'],label_evidence=record['evidence_a'])
        entry.update(reviewer='',reviewed_at='',human_narrative='',human_label_confidence='',notes='')
        for condition in ['Paraphrase','Normalized']:
            value=lookup.get((rid,condition),'');entry[condition]=value
            screen=validation.get((rid,condition),{})
            entry[condition+'_automatic_pass']=screen.get('passed','pending')
            entry[condition+'_automatic_reasons']=screen.get('rejection_reasons','pending')
            entry[condition+'_validation_score']=screen.get('validation_score','pending')
            for field in FIELDS: entry[condition+'_'+field]=''
            if value: measurements.append(dict(row_id=rid,condition=condition,split=record['split'],**style_metrics(record['text'],value)))
        measurements.append(dict(row_id=rid,condition='Previous_Normalized',split=record['split'],**style_metrics(record['text'],old[rid])))
        if rid in existing:
            for key in ['reviewer','reviewed_at','human_narrative','human_label_confidence','notes']+[c+'_'+f for c in ['Paraphrase','Normalized'] for f in FIELDS]: entry[key]=existing[rid].get(key,'')
        review.append(entry)
        markdown.extend([f'## {rid}',f"הצעת נרטיב: **{record['narrative_name']}**; confidence: {record['confidence_a']}/3",'',
            '**Original**',record['text'],'','**Paraphrase**',entry['Paraphrase'],'','**Normalized V2**',entry['Normalized'] or 'טרם נוצר','',
            'לכל גרסה: נרטיב □ עמדה □ מסגור □ עובדות □ ישויות □ שלילה □ ודאות □ ייחוס □ נוספה טענה? □ הושמטה טענה? □',''])
    write_csv('human_review.csv',review)
    write_csv('style_change_metrics.csv',measurements)
    # Reuse ALL existing explicit style features; scale on ORIGINAL TRAIN ONLY.
    # These measures are descriptive and never decide semantic acceptance.
    if sum(r['condition']=='Normalized' for r in generated)==218:
        engine=load_engine();np=engine.np
        names=read_json(PREVIOUS/'style_feature_definitions.json')['names']
        train=np.array([engine.style_features(r['text']) for r in corpus if r['split']=='train'])
        scale=train.std(axis=0);scale[scale<1e-8]=1.
        explicit=[]
        for r in corpus:
            original=np.array(engine.style_features(r['text']))
            for condition in ['Paraphrase','Normalized']:
                values=np.array(engine.style_features(lookup[r['row_id'],condition]))
                for name,a,b in zip(names,original,values):
                    explicit.append(dict(row_id=r['row_id'],condition=condition,feature=name,original=float(a),rewrite=float(b),delta=float(b-a)))
                for measurement in measurements:
                    if measurement['row_id']==r['row_id'] and measurement['condition']==condition:
                        measurement['explicit_style_mean_abs_standardized_change']=float(np.mean(np.abs(values-original)/scale))
        write_csv('explicit_style_changes.csv',explicit)
        for measurement in measurements:measurement.setdefault('explicit_style_mean_abs_standardized_change','')
        write_csv('style_change_metrics.csv',measurements)
        write_json('style_feature_scaling.json',dict(names=names,scale=scale.tolist(),fit_scope='Original training texts only; no validation/test scaling fit'))
    (OUT/'HUMAN_REVIEW_HE.md').write_text('\n'.join(markdown),encoding='utf8')
    if not (OUT/'human_labels_blind.csv').exists():
        import random
        order=corpus[:];random.Random(20261026).shuffle(order)
        write_csv('human_labels_blind.csv',[dict(review_id=f'B{i:03d}',text=r['text'],reviewer='',human_narrative='',confidence='',evidence='',notes='') for i,r in enumerate(order)])
        write_csv('human_labels_key.csv',[dict(review_id=f'B{i:03d}',row_id=r['row_id']) for i,r in enumerate(order)])
    event('package',[OUT/'generated_rewrites.jsonl'],[OUT/'human_review.csv',OUT/'style_change_metrics.csv'],len(corpus),len(review))
    if sum(r['condition']=='Normalized' for r in generated)==218:
        subprocess.run([sys.executable,str(OUT/'render_review.py')],check=True)


def validate():
    """Apply unchanged previous MPNet/NLI/NER and lexical checks to all versions."""
    generated=[json.loads(s) for s in (OUT/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]
    new=[r for r in generated if r['condition']=='Normalized']
    assert len(new)==218 and len({r['row_id'] for r in new})==218
    if not (OUT/'rewrite_validation.csv').exists():
        # Frozen controls already have the exact same-model, same-threshold screen.
        # Reuse those scores after exact text checks; compute new scores only for N.
        old_generated=[json.loads(s) for s in (PREVIOUS/'generated_rewrites.jsonl').read_text(encoding='utf8').splitlines()]
        old_lookup={(r['row_id'],r['condition']):(r['original'],r['rewrite']) for r in old_generated}
        for r in generated:
            if r['condition'] in ['Formatting','Paraphrase']:
                assert old_lookup[r['row_id'],r['condition']]==(r['original'],r['rewrite'])
        screen=OUT/'normalized_screen';screen.mkdir(exist_ok=True)
        shutil.copyfile(OUT/'analysis_cohort.csv',screen/'analysis_cohort.csv')
        (screen/'generated_rewrites.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in new),encoding='utf8')
        engine=load_engine();engine.OUT=screen;engine.base.OUT=screen;engine.validate()
        controls=[r for r in rows(PREVIOUS/'rewrite_validation.csv') if r['condition'] in ['Formatting','Paraphrase']]
        write_csv('rewrite_validation.csv',controls+rows(screen/'rewrite_validation.csv'))
        write_json('validation_reuse.json',dict(reused_control_rows=len(controls),new_scored_rows=218,
            exact_control_text_match=True,unchanged_thresholds=True,
            previous_validation_sha256=sha(PREVIOUS/'rewrite_validation.csv'),new_validation_sha256=sha(screen/'rewrite_validation.csv')))
    event('validate',[OUT/'generated_rewrites.jsonl'],[OUT/'rewrite_validation.csv'],654,
          sum(r['passed']=='True' for r in rows(OUT/'rewrite_validation.csv')),model=read_json(OUT/'generator_manifest.json'),
          validation_model_versions=read_json(OUT/'normalized_screen/validation_method.json'))
    write_json('validated_inputs.json',{name:sha(OUT/name) for name in ['analysis_cohort.csv','generated_rewrites.jsonl','rewrite_validation.csv']})


def reviewed_cohort():
    """Require a real named human review, valid values and unchanged automatic gates."""
    accepted=[]; incomplete=[]
    for row in rows(OUT/'human_review.csv'):
        if not row['reviewer'].strip() or not row['reviewed_at'].strip() or row['human_narrative'] not in ['Left-wing','Right-wing','Unclear']:
            incomplete.append(row['row_id']);continue
        values=[row[c+'_'+f].strip().lower() for c in ['Paraphrase','Normalized'] for f in FIELDS]
        if any(v not in ['yes','no','unclear'] for v in values): incomplete.append(row['row_id']);continue
        if row['human_narrative']=='Unclear': continue
        passed=all(row[c+'_'+f].strip().lower()==('no' if f in ['claim_added','claim_omitted'] else 'yes')
                   for c in ['Paraphrase','Normalized'] for f in FIELDS)
        if passed: accepted.append(row)
    write_json('human_review_status.json',dict(total=218,incomplete=len(incomplete),human_acceptable=len(accepted),timestamp=timestamp()))
    if incomplete: raise RuntimeError(f'Human review incomplete for {len(incomplete)} sources. No new training was performed.')
    return accepted


def evaluate():
    """After human adjudication only: same-source 3x3 retraining and refitted probes."""
    accepted=reviewed_cohort()
    for name,digest in read_json(OUT/'validated_inputs.json').items():
        assert sha(OUT/name)==digest,f'Changed input since validation: {name}'
    for name in ['analysis_cohort.csv','author_splits.csv','split_definitions.csv']:
        assert sha(OUT/name)==sha(PREVIOUS/name),f'Frozen source/split changed: {name}'
    engine=load_engine();np=engine.np;pd=engine.pd
    corpus=engine.frame('analysis_cohort.csv');v=engine.frame('rewrite_validation.csv')
    valid={(r.row_id,r.condition):bool(r.passed) for r in v.itertuples()}
    review={r['row_id']:r for r in accepted}
    corpus=corpus[corpus.row_id.map(lambda rid:rid in review and all(valid.get((rid,c),False) for c in ['Formatting','Paraphrase','Normalized']))].copy()
    corpus['narrative_name']=corpus.row_id.map(lambda rid:review[rid]['human_narrative'])
    corpus['label']=corpus.narrative_name.map(lambda label:engine.LABELS.index(label))
    changed=set(r['row_id'] for r in rows(OUT/'style_change_metrics.csv') if r['condition']=='Normalized' and r['substantial_style_change']=='True')
    cohorts=[('human_matched',corpus),('substantial_style',corpus[corpus.row_id.isin(changed)].copy())]
    rew={(r['row_id'],r['condition']):r['rewrite'] for r in engine.jsonl('generated_rewrites.jsonl')}
    source_text={r['row_id']:r['text'] for r in rows(OUT/'analysis_cohort.csv')}
    for r in accepted:
        assert r['original']==source_text[r['row_id']],f"Review CSV original was edited: {r['row_id']}"
        for condition in ['Paraphrase','Normalized']:
            assert r[condition]==rew[r['row_id'],condition],f"Review CSV rewrite was edited: {r['row_id']} {condition}"
    texts=list(dict.fromkeys([r.text for r in corpus.itertuples()]+[rew[rid,c] for rid in corpus.row_id for c in ['Paraphrase','Normalized']]))
    encoder=engine.base.encoder();vectors=engine.base.embed(texts,encoder);lookup=dict(zip(texts,vectors));del encoder
    # Exclude any cross-split duplicate/near-duplicate among ANY generated condition.
    bad=set();duplicates=[]
    for a,b in itertools.combinations(list(corpus.itertuples()),2):
        if a.split==b.split: continue
        av=[a.text,rew[a.row_id,'Paraphrase'],rew[a.row_id,'Normalized']]
        bv=[b.text,rew[b.row_id,'Paraphrase'],rew[b.row_id,'Normalized']]
        if any(float(lookup[x]@lookup[y]/(np.linalg.norm(lookup[x])*np.linalg.norm(lookup[y])))>=.97 or
               engine.base.jaccard(engine.base.get_shingles(engine.base.canon(x)),engine.base.get_shingles(engine.base.canon(y)))>=.7 for x,y in itertools.product(av,bv)):
            bad.update([a.row_id,b.row_id]);duplicates.append(dict(row_a=a.row_id,row_b=b.row_id))
    write_json('cross_split_duplicates.json',duplicates)
    results=[];predictions=[];status=[]
    for name,df in cohorts:
        df=df[~df.row_id.isin(bad)].reset_index(drop=True)
        write_csv(name+'_cohort.csv',df.to_dict('records'),list(corpus.columns))
        coverage=[dict(split=s,label=l,n=int(((df.split==s)&(df.label==l)).sum()),authors=int(df[(df.split==s)&(df.label==l)].author.nunique())) for s in ['train','val','test'] for l in [5,6]]
        sufficient=all(r['n']>=3 and r['authors']>=2 for r in coverage)
        status.append(dict(cohort=name,n=len(df),runnable=sufficient,coverage=coverage))
        if not sufficient: continue
        y=df.label.to_numpy(int);spl=df.split.to_numpy();test=spl=='test'
        arms=['Original','Paraphrase','Normalized']
        z={c:np.array([lookup[r.text if c=='Original' else rew[r.row_id,c]] for r in df.itertuples()]) for c in arms}
        for seed in SEEDS:
            for train_condition in arms:
                head=engine.base.train(z[train_condition],y,spl,seed,name+'_'+train_condition)
                for condition in arms:
                    p=engine.base.probs(head,z[condition][test]);results.append(dict(cohort=name,seed=seed,train_condition=train_condition,test_condition=condition,**engine.metrics(y[test],p)))
                    for r,pp in zip(df[test].itertuples(),p):predictions.append(dict(cohort=name,seed=seed,train_condition=train_condition,test_condition=condition,row_id=r.row_id,author=r.author,label=int(r.label),predicted=int(pp.argmax()),probabilities=json.dumps(pp.tolist())))
        if name=='human_matched': engine.probe(df,rew,lookup)
    write_json('evaluation_status.json',status)
    if results:
        write_csv('retraining_results.csv',results);write_csv('narrative_predictions.csv',predictions)
        summary=pd.DataFrame(results).groupby(['cohort','train_condition','test_condition']).agg(macro_f1_mean=('macro_f1','mean'),macro_f1_std=('macro_f1','std'),accuracy_mean=('accuracy','mean'),accuracy_std=('accuracy','std'),n=('n','first')).reset_index()
        summary.to_csv(OUT/'metrics_summary.csv',index=False,encoding='utf-8-sig')
        diagonal=pd.DataFrame(results).query('train_condition==test_condition').pivot(index=['cohort','seed'],columns='train_condition',values='macro_f1').reset_index()
        diagonal['normalized_minus_paraphrase']=diagonal.Normalized-diagonal.Paraphrase
        diagonal['normalized_minus_original']=diagonal.Normalized-diagonal.Original
        diagonal.to_csv(OUT/'paired_seed_comparisons.csv',index=False,encoding='utf-8-sig')
        prediction_frame=pd.DataFrame(predictions);per_author=[];transitions=[]
        for key,group in prediction_frame.groupby(['cohort','seed','train_condition','test_condition','author']):
            probabilities=np.array([json.loads(p) for p in group.probabilities])
            per_author.append(dict(zip(['cohort','seed','train_condition','test_condition','author'],key))|engine.metrics(group.label.to_numpy(int),probabilities))
        write_csv('per_author_metrics.csv',per_author)
        for key,group in prediction_frame[prediction_frame.train_condition=='Original'].groupby(['cohort','seed']):
            original=group[group.test_condition=='Original'].set_index('row_id')
            for condition,subgroup in group.groupby('test_condition'):
                reference=original.loc[subgroup.row_id];y=subgroup.label.to_numpy(int)
                pp=np.array([json.loads(p) for p in subgroup.probabilities]);old=np.array([json.loads(p) for p in reference.probabilities])
                transitions.append(dict(cohort=key[0],seed=int(key[1]),condition=condition,
                    **engine.base.transitions(y,old.argmax(1),pp.argmax(1)),
                    true_probability_delta=float(np.mean(pp[np.arange(len(y)),y]-old[np.arange(len(y)),y]))))
        write_csv('fixed_classifier_transitions.csv',transitions)
    event('evaluate',[OUT/'human_review.csv',OUT/'protocol.json'],[OUT/'retraining_results.csv',OUT/'evaluation_status.json'],218,len(corpus)-len(bad),training_seeds=SEEDS)


def main():
    """Run one explicit stage; all stops after review packaging, never invents reviewers."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',required=True,choices=['prepare','generate','validate','package','evaluate','report','all'])
    stage=parser.parse_args().stage
    if stage=='all':
        for child in ['prepare','generate','validate','package','report']:
            subprocess.run([sys.executable,'-u',str(OUT/'study.py'),'--stage',child],check=True)
        subprocess.run([sys.executable,str(OUT/'audit.py')],check=True)
        return
    if stage=='report':
        subprocess.run([sys.executable,str(OUT/'report.py')],check=True)
    else: globals()[stage]()


if __name__=='__main__': main()
