"""Fixed-update A-E MLP trainer with a frozen production encoder. No test interface."""

import hashlib
import importlib.metadata
import json
import time
import statistics

from contract import (HERE, ROOT, PROTOCOL, PRODUCTION_WEIGHTS, LABELS, SEEDS, ARMS,
                      BATCH_SIZE, LEARNING_RATE, module_from_file, schedule, sha, dump, save, assert_frozen)


def load_backend():
    import os
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
    module = module_from_file('ae_frozen_production', ROOT / 'experiments/author_generalization/author_style_controlled.py')
    encoder = module.encoder()
    encoder.eval()
    for parameter in encoder.parameters():
        parameter.requires_grad_(False)
    return module, encoder


def state_digest(state):
    digest = hashlib.sha256()
    for name, value in sorted(state.items()):
        digest.update(name.encode())
        digest.update(value.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def encode_texts(backend, encoder, texts):
    texts = list(dict.fromkeys(texts))
    lengths = encoder.tokenizer(texts, truncation=False, add_special_tokens=True)['input_ids']
    tokens = encoder.tokenize(texts)  # Same tokenizer/limit used by SentenceTransformer.encode.
    assert tokens['input_ids'].shape[0] == len(texts)
    with backend.torch.no_grad():
        vectors = backend.embed(texts, encoder)
    if vectors.shape != (len(texts), 384):
        raise ValueError('Production embedding shape changed')
    audit = [dict(text_sha256=hashlib.sha256(text.encode()).hexdigest(), tokens_before_truncation=len(ids),
                  encoder_max_seq_length=encoder.max_seq_length, truncated=len(ids) > encoder.max_seq_length)
             for text, ids in zip(texts, lengths)]
    return dict(zip(texts, vectors)), audit


def train_head(backend, view, lookup, seed, updates, out, mode, encoder_identity):
    """Same seeded initialization and final-step checkpoint in smoke/scientific modes."""
    torch = backend.torch
    backend.seed(seed)
    head = backend.head()
    initial_hash = state_digest(head.state_dict())
    optimizer = torch.optim.Adam(head.parameters(), lr=LEARNING_RATE)
    plan = schedule(view, seed, updates)
    audit = []
    started = time.perf_counter()
    for step in range(updates):
        slots = plan[step * BATCH_SIZE:(step + 1) * BATCH_SIZE]
        selected = [view[row['view_index']] for row in slots]
        x = torch.as_tensor(backend.np.array([lookup[row['text']] for row in selected]), dtype=torch.float32)
        y = torch.tensor([LABELS.index(row['label']) for row in selected], dtype=torch.long)
        head.train()
        optimizer.zero_grad()
        loss = torch.nn.functional.cross_entropy(head(x), y)
        if not torch.isfinite(loss):
            raise ValueError('Non-finite training loss')
        loss.backward()
        if not all(parameter.grad is not None and torch.isfinite(parameter.grad).all() for parameter in head.parameters()):
            raise ValueError('Head backward gradients missing/nonfinite')
        optimizer.step()
        audit.append(dict(update=step + 1, loss=float(loss.detach()), batch_size=len(slots)))
    head.eval()
    final_hash = state_digest(head.state_dict())
    payload = dict(
        head_state=head.state_dict(), optimizer_state=optimizer.state_dict(), seed=seed, updates=updates,
        batch_size=BATCH_SIZE, lr=LEARNING_RATE, labels=list(LABELS),
        initial_head_sha256=initial_hash, final_head_sha256=final_hash,
        mode=mode, scientific_result=mode == 'scientific', encoder_identity=encoder_identity,
        checkpoint_rule='final fixed update; no best-validation selection',
    )
    checkpoint = out / f'head_seed{seed}.pt'
    torch.save(payload, checkpoint)
    restored = torch.load(checkpoint, map_location='cpu', weights_only=True)
    reloaded = backend.head()
    reloaded.load_state_dict(restored['head_state'], strict=True)
    reloaded.eval()
    reload_optimizer = torch.optim.Adam(reloaded.parameters(), lr=LEARNING_RATE)
    reload_optimizer.load_state_dict(restored['optimizer_state'])
    probe = torch.as_tensor(backend.np.array([lookup[view[0]['text']]]), dtype=torch.float32)
    with torch.no_grad():
        reload_equal = torch.equal(head(probe), reloaded(probe))
    if not reload_equal or initial_hash == final_hash:
        raise ValueError('Checkpoint reload or backward/update verification failed')
    dump(out / 'training_trace.json', audit)
    save(out / 'batch_schedule.csv', plan)
    result = dict(seed=seed, updates=updates, processed_examples=len(plan),
                  initial_head_sha256=initial_hash, final_head_sha256=final_hash,
                  checkpoint_sha256=sha(checkpoint), reload_logits_identical=reload_equal,
                  optimizer_state_reloaded=bool(reload_optimizer.state), backward_pass_verified=True,
                  elapsed_seconds=time.perf_counter() - started, mode=mode,
                  scientific_result=mode == 'scientific')
    dump(out / 'runtime_audit.json', result)
    return reloaded, result, plan


def encoder_identity(encoder):
    return dict(production_checkpoint_sha256=sha(PRODUCTION_WEIGHTS),
                protocol_sha256=sha(PROTOCOL), encoder='production MiniLM with original sbert weights',
                tokenizer_vocabulary_sha256=hashlib.sha256(json.dumps(encoder.tokenizer.get_vocab(), sort_keys=True).encode()).hexdigest(),
                max_seq_length=encoder.max_seq_length,
                torch=importlib.metadata.version('torch'),
                sentence_transformers=importlib.metadata.version('sentence-transformers'))


def run_scientific(snapshot, destination, cohort):
    from data import load_approved
    # Gate before loading a model or starting any training. No test split is accepted.
    assert_frozen()
    views, validation, manifest = load_approved(snapshot, cohort)
    if destination.exists():
        raise ValueError('Scientific run outputs are immutable; select a new run directory')
    backend, encoder = load_backend()
    identity = encoder_identity(encoder)
    n_sources = len(views['A'])
    updates = 20 * ((n_sources + BATCH_SIZE - 1) // BATCH_SIZE)
    if not n_sources or any(len(views[arm]) != n_sources * len(ARMS[arm]) for arm in ARMS):
        raise ValueError('Unmatched A-E dataset sizes')
    embedding_started = time.perf_counter()
    lookup, token_audit = encode_texts(backend, encoder,
                                     [row['text'] for view in views.values() for row in view] + [row['text'] for row in validation])
    embedding_seconds = time.perf_counter() - embedding_started
    token_counts = {row['text_sha256']: min(row['tokens_before_truncation'], row['encoder_max_seq_length']) for row in token_audit}
    destination.mkdir(parents=True)
    save(destination / 'tokenization_audit.csv', token_audit)
    from evaluation_contract import classification_metrics, aligned_arm_metrics
    predictions, metrics, init_hashes = [], [], {}
    validation_hash = hashlib.sha256(json.dumps(validation, sort_keys=True).encode()).hexdigest()
    for seed in SEEDS:
        for arm in ARMS:
            out = destination / f'{arm}_seed{seed}'
            out.mkdir()
            head, runtime, plan = train_head(backend, views[arm], lookup, seed, updates, out, 'scientific', identity)
            runtime['processed_tokens'] = sum(token_counts[hashlib.sha256(views[arm][slot['view_index']]['text'].encode()).hexdigest()] for slot in plan)
            dump(out / 'runtime_audit.json', runtime)
            if seed in init_hashes and init_hashes[seed] != runtime['initial_head_sha256']:
                raise ValueError('Arms do not share identical seeded head initialization')
            init_hashes[seed] = runtime['initial_head_sha256']
            p = backend.probs(head, backend.np.array([lookup[row['text']] for row in validation]))
            score = classification_metrics([row['label'] for row in validation], p.tolist())
            metrics.append(dict(arm=arm, seed=seed, validation_binding_sha256=validation_hash, **score))
            predictions.extend(dict(ID=row['ID'], author=row['author'], gold=row['label'], probabilities=probs.tolist(),
                                    arm=arm, seed=seed, split='validation') for row, probs in zip(validation, p))
    aligned_arm_metrics(predictions)
    dump(destination / 'validation_predictions.json', predictions)
    dump(destination / 'validation_metrics.json', metrics)
    dump(destination / 'validation_summary.json', summarize_validation(predictions))
    dump(destination / 'RUN_MANIFEST.json', dict(
        cohort=cohort, approved_snapshot_sha256=sha(snapshot / 'MANIFEST.json'),
        source_count=n_sources, updates_per_arm=updates, processed_examples_per_arm=updates * BATCH_SIZE,
        same_validation_binding_sha256=validation_hash, final_checkpoint_only=True,
        validation_used_for_checkpoint_selection=False, test_evaluated=False, encoder_identity=identity,
        scientific_run=True, shared_embedding_seconds=embedding_seconds,
        runtime_code_sha256={path.name: sha(path) for path in HERE.glob('*.py')},
    ))
    assert_frozen()


def summarize_validation(predictions):
    """Point summaries only; final test/author-cluster inference is deliberately separate."""
    from evaluation_contract import aligned_arm_metrics, classification_metrics
    aligned = aligned_arm_metrics(predictions)
    seeds = sorted({seed for seed, arm in aligned})
    arms = {}
    for arm in ARMS:
        arms[arm] = {}
        for metric in ('accuracy', 'macro_f1', 'inactive_output_rate'):
            values = [aligned[seed, arm][metric] for seed in seeds]
            arms[arm][metric] = dict(mean=statistics.mean(values),
                                   seed_sd=statistics.stdev(values) if len(values) > 1 else 0)
    contrasts = {}
    for first, second in [('C', 'B'), ('D', 'E')]:
        differences = [aligned[seed, first]['macro_f1'] - aligned[seed, second]['macro_f1'] for seed in seeds]
        contrasts[first + '-' + second] = dict(mean=statistics.mean(differences),
                                                seed_sd=statistics.stdev(differences) if len(differences) > 1 else 0)
    confusion, authors = [], []
    for seed in seeds:
        for arm in ARMS:
            selected = [row for row in predictions if row['seed'] == seed and row['arm'] == arm]
            matrix = [[0] * 7 for _ in range(2)]
            for row in selected:
                predicted = max(range(7), key=row['probabilities'].__getitem__)
                matrix[LABELS[5:].index(row['gold'])][predicted] += 1
            confusion.append(dict(seed=seed, arm=arm, gold_order=list(LABELS[5:]), prediction_order=list(LABELS), counts=matrix))
            for author in sorted({row['author'] for row in selected}):
                group = [row for row in selected if row['author'] == author]
                authors.append(dict(seed=seed, arm=arm, author=author,
                                    single_gold_class=len({row['gold'] for row in group}) == 1,
                                    **classification_metrics([row['gold'] for row in group], [row['probabilities'] for row in group])))
    return dict(arms=arms, primary_contrasts=contrasts, confusion=confusion, per_author=authors,
                split='validation_only', checkpoint_selection=False,
                caution='Seeds are not independent datasets; no significance, confidence interval or test claim from this summary')
