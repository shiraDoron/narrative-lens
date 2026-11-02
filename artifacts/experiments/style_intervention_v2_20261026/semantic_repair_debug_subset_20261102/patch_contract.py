"""Fail-closed, local patches. Lookup normalization never changes the document."""
import re
import unicodedata

OPERATIONS = ('replace_exact', 'insert_after_exact', 'insert_before_exact', 'delete_exact')
VIOLATIONS = ('certainty_change','attribution_change','quote_change','stance_or_framing_change','factual_change','entity_change','number_change','negation_change','causal_relation_change','temporal_change','omission','addition','participant_roles','other')

def canonical(text):
    table = str.maketrans({'“':'"','”':'"','‘':"'",'’':"'",'—':'-','–':'-'})
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', text).translate(table)).casefold().strip()

def locate(text, query):
    """Return an exact surface span only when normalized lookup is unambiguous."""
    if not query or not canonical(query):
        raise ValueError('missing target')
    # Offset mapping handles whitespace collapse, quotes, dashes and case only.
    chars=[]; starts=[]; ends=[]
    for i,c in enumerate(text):
        n=canonical(c) if not c.isspace() else ' '
        if n==' ' and chars and chars[-1]==' ':
            ends[-1]=i+1; continue
        for x in n:
            chars.append(x); starts.append(i); ends.append(i+1)
    normalized=''.join(chars); needle=canonical(query)
    matches=[m.start() for m in re.finditer('(?='+re.escape(needle)+')',normalized)]
    if len(matches)!=1: raise ValueError('missing target' if not matches else 'multiple matches')
    i=matches[0]; return text[starts[i]:ends[i+len(needle)-1]]

def apply_patch(text, patch, original):
    required={'operation','target_text','evidence_original','reason','violation_type'}
    if not isinstance(patch,dict) or not required <= patch.keys(): raise ValueError('missing required field')
    if set(patch)-required-{'replacement_text'}: raise ValueError('invalid schema')
    if any(not isinstance(patch[k],str) for k in patch): raise ValueError('invalid schema')
    op=patch['operation']; target=patch['target_text']; evidence=patch['evidence_original']
    if op not in OPERATIONS: raise ValueError('unsupported patch type')
    if patch['violation_type'] not in VIOLATIONS: raise ValueError('unsupported violation type')
    if not evidence or evidence not in original: raise ValueError('evidence span not found')
    if not patch['reason'].strip(): raise ValueError('missing reason')
    # Always exact, including overlapping occurrences. Resolver is explicit and separate.
    matches=list(re.finditer('(?='+re.escape(target)+')',text)) if target else []
    if len(matches)!=1: raise ValueError('multiple matches' if matches else 'missing target')
    replacement=patch.get('replacement_text','')
    if op!='delete_exact' and ('replacement_text' not in patch or not replacement): raise ValueError('invalid replacement')
    if op=='delete_exact' and replacement: raise ValueError('invalid replacement')
    if target==text or len(target.split())>20 or len(replacement.split())>24: raise ValueError('over-broad patch')
    if op=='delete_exact' and len(target.split())>8: raise ValueError('over-broad deletion')
    start=matches[0].start(); end=start+len(target)
    if op=='insert_after_exact': start=end
    if op=='insert_before_exact': end=start
    result=text[:start]+replacement+text[end:]
    if result==text: raise ValueError('no-op patch')
    return result, {'start':start,'end':end,'before':text[start:end],'after':replacement}

def apply_patches(text, patches, original):
    """Sequential current-text validation; invalid proposals cannot block valid siblings."""
    events=[]
    for p in patches:
        before=text
        try:
            text,event=apply_patch(text,p,original)
            events.append(dict(applied=True,patch=p,edit=event))
        except ValueError as e:
            assert text==before
            events.append(dict(applied=False,patch=p,error=str(e)))
    return text,events
