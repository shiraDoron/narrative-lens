"""Descriptive paired style/content changes; never a semantic or human judge."""
from run import *
def main():
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    import importlib.util
    protected();rows=records(OUT/'development_originals.csv');pairs=records(CHAT/'frozen_comparison_inputs.csv');eng,names,original_dev,indices=engine_and_features(rows)
    helper=module(ROOT/'artifacts/experiments/style_intervention_v2_20261026/study.py','existing_pair_proxies')
    o=np.array([eng.style_features(r['Original']) for r in pairs]);w=np.array([eng.style_features(r['ChatGPT_Style_Rewrite']) for r in pairs]);scale=original_dev.std(axis=0);scale=np.where(scale>0,scale,1.)
    vectors=[];summaries=[]
    for j,name in enumerate(names):
        delta=w[:,j]-o[:,j]
        summaries.append(dict(feature=name,original_mean=float(o[:,j].mean()),rewrite_mean=float(w[:,j].mean()),mean_paired_delta=float(delta.mean()),median_paired_delta=float(np.median(delta)),mean_abs_standardized_delta=float(np.mean(np.abs(delta)/scale[j])),pairs_changed=int(np.sum(np.abs(delta)>1e-10)),original_development_sd=float(original_dev[:,j].std())))
        for i,r in enumerate(pairs):vectors.append(dict(ID=r['ID'],feature=name,original=float(o[i,j]),rewrite=float(w[i,j]),delta=float(delta[i]),delta_over_development_sd=float(delta[i]/scale[j])))
    write('paired_style_feature_deltas.csv',vectors);write('paired_style_feature_summary.csv',summaries)
    groups={'length':[0,1],'lexical_variety':[10,12],'sentence_structure_proxies':[2,11],'punctuation':[4,5,6,7,8,9,14,15],'orthography_contractions':[3,13],'function_words':list(range(16,66))}
    cohort=records(CHAT/'analysis_cohort.csv');authors={r['row_id']:r['author'] for r in cohort};family_rows=[]
    for family,ix in groups.items():
        by_author=[]
        for a in sorted(set(authors.values())):
            mask=[i for i,r in enumerate(pairs) if authors[r['ID']]==a]
            by_author.append(dict(author=a,n=len(mask),mean_abs_standardized_delta=float(np.mean(np.abs(w[mask][:,ix]-o[mask][:,ix])/scale[ix]))))
        family_rows.extend(dict(family=family,**r) for r in by_author)
    write('paired_style_changes_by_author_family.csv',family_rows)
    lexical=TfidfVectorizer(ngram_range=(1,2),stop_words='english',min_df=2,max_features=10000,sublinear_tf=True).fit([r['Original'] for r in rows]);zo=lexical.transform([r['Original'] for r in pairs]);zw=lexical.transform([r['ChatGPT_Style_Rewrite'] for r in pairs]);cos=np.array(zo.multiply(zw).sum(axis=1)).ravel()
    old_validation={r['row_id']:r for r in records(CHAT/'rewrite_validation.csv')}
    measurements=[];anchors=[]
    for i,r in enumerate(pairs):
        a=r['Original'];b=r['ChatGPT_Style_Rewrite'];aa=set(words(a));bb=set(words(b));m=helper.style_metrics(a,b)
        measurements.append(dict(ID=r['ID'],author=authors[r['ID']],**m,content_tfidf_cosine=float(cos[i]),word_set_jaccard=len(aa&bb)/max(1,len(aa|bb)),existing_automatic_pass=old_validation[r['ID']]['passed'],existing_rejection_reasons=old_validation[r['ID']]['rejection_reasons']))
        wa=eng.base.words(a);wb=eng.base.words(b)
        for name,vocabulary in [('certainty',eng.base.CERT),('attribution',eng.base.ATTR),('framing',eng.base.FRAME)]:
            before=wa&vocabulary;after=wb&vocabulary
            anchors.append(dict(ID=r['ID'],anchor_family=name,original='|'.join(sorted(before)),rewrite='|'.join(sorted(after)),removed='|'.join(sorted(before-after)),added='|'.join(sorted(after-before)),sets_equal=before==after,interpretation='lexical diagnostic only; no scope/rhetorical-intensity adjudication'))
    write('paired_lexical_structure_metrics.csv',measurements);write('paired_certainty_attribution_framing_anchors.csv',anchors)
    names_lookup={r['feature']:r for r in summaries};summary=dict(n=30,all_pairs_kept=True,style_proxy_substantial=sum(r['substantial_style_change'] for r in measurements),auto_preservation_pass=sum(r['existing_automatic_pass']=='True' for r in measurements),word_edit_fraction_mean=float(np.mean([r['word_edit_fraction'] for r in measurements])),word_edit_fraction_median=float(np.median([r['word_edit_fraction'] for r in measurements])),changed_sentence_count_pairs=sum(r['sentence_count_original']!=r['sentence_count_rewrite'] for r in measurements),changed_mean_sentence_length_pairs=sum(r['sentence_mean_relative_change']>0 for r in measurements),content_tfidf_cosine_mean=float(cos.mean()),word_set_jaccard_mean=float(np.mean([r['word_set_jaccard'] for r in measurements])),family_mean_abs_standardized_change={f:float(np.mean(np.abs(w[:,ix]-o[:,ix])/scale[ix])) for f,ix in groups.items()},mean_word_count_original=float(o[:,1].mean()),mean_word_count_rewrite=float(w[:,1].mean()),mean_sentence_words_original=float(o[:,2].mean()),mean_sentence_words_rewrite=float(w[:,2].mean()),certainty_anchor_set_changes=sum(r['anchor_family']=='certainty' and not r['sets_equal'] for r in anchors),attribution_anchor_set_changes=sum(r['anchor_family']=='attribution' and not r['sets_equal'] for r in anchors),framing_anchor_set_changes=sum(r['anchor_family']=='framing' and not r['sets_equal'] for r in anchors),english_parser_model_available=bool(importlib.util.find_spec('en_core_web_sm')),syntax_measured=False,syntax_note='Sentence/clause-length and punctuation proxies only. No English syntactic parser checkpoint available; no parser downloaded or inferred syntax labels invented.',semantic_or_rhetorical_judgment_performed=False,external_rhetorical_review_counts=read_external_rhetoric(),scope_caution='Style metric changes and lexical overlap do not prove author identity removal, syntactic transformation, or semantic equivalence.')
    dump('paired_style_summary.json',summary);protected();print(json.dumps(summary,ensure_ascii=True),flush=True)
def read_external_rhetoric():return json.loads((PREVIOUS/'external_llm_review_aggregate.json').read_text(encoding='utf8'))['counts']['rhetorical_intensity_preserved']
if __name__=='__main__':main()
