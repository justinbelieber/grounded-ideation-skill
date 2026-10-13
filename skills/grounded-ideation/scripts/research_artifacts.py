#!/usr/bin/env python3
"""Offline artifact bookkeeping. No network, model calls, or shell execution."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import html
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from datetime import datetime, timezone

VERSION = '0.1.0'
SKILL = Path(__file__).resolve().parents[1]
FILES = ('brief.json', 'search-log.jsonl', 'sources.jsonl', 'claims.jsonl',
         'gaps.json', 'candidates.json', 'reviews.json', 'proposal.json')
STAGES = ('define', 'evidence', 'gaps', 'candidates', 'review', 'proposal')
STAGE = {'brief.json': 0, 'search-log.jsonl': 1, 'sources.jsonl': 1,
         'claims.jsonl': 1, 'gaps.json': 2, 'candidates.json': 3,
         'reviews.json': 4, 'proposal.json': 5}
MAX_BYTES = 4 * 1024 * 1024


class ArtifactError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def clean_path(value):
    p = Path(value).expanduser()
    if '..' in p.parts:
        raise ArtifactError('path traversal is forbidden')
    p = p.absolute()
    for item in (p, *p.parents):
        if item.is_symlink():
            raise ArtifactError('symlinks are forbidden: ' + item.name)
    return p


def child(root, relative):
    root = clean_path(root)
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise ArtifactError('expected a confined relative path')
    target = clean_path(root / rel)
    if not target.is_relative_to(root):
        raise ArtifactError('path escapes workspace')
    return target


def read_bytes(path):
    path = clean_path(path)
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    with os.fdopen(fd, 'rb') as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise ArtifactError('expected a regular file')
        data = f.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ArtifactError('artifact exceeds 4 MiB')
    return data


def unique_keys(items):
    out = {}
    for k, v in items:
        if k in out:
            raise ArtifactError('duplicate JSON key: ' + k)
        out[k] = v
    return out


def parse(text):
    def invalid(value):
        raise ArtifactError('non-finite JSON number: ' + value)
    return json.loads(text, object_pairs_hook=unique_keys, parse_constant=invalid)


def read_json(path):
    return parse(read_bytes(path).decode('utf-8'))


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def file_bytes(name, value):
    if name.endswith('.jsonl'):
        return ''.join(json.dumps(x, ensure_ascii=False, allow_nan=False) + '\n' for x in value).encode()
    return encoded(value)


def atomic(path, data, replace=False):
    path = clean_path(path)
    if path.exists() and not replace:
        raise ArtifactError('refusing overwrite: ' + path.name)
    if len(data) > MAX_BYTES:
        raise ArtifactError('artifact exceeds 4 MiB')
    fd, tmp = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        clean_path(path)
        if replace:
            os.replace(tmp, path)
        else:
            os.link(tmp, path)  # atomic create-if-absent
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextlib.contextmanager
def locked(root):
    path = child(root, '.writer.lock')
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    except FileExistsError as e:
        raise ArtifactError('writer lock exists; inspect owner before manual recovery') from e
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        path.unlink()


def schema_errors(name, data):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as e:
        raise ArtifactError('install the skill requirements.txt with Python 3.10+') from e
    stem = name.rsplit('.', 1)[0]
    schema = read_json(SKILL / 'assets' / 'schemas' / (stem + '.schema.json'))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    values = list(enumerate(data)) if name.endswith('.jsonl') and isinstance(data, list) else [(None, data)]
    if name.endswith('.jsonl') and not isinstance(data, list):
        return [name + ': JSONL update must be an array']
    return [f'{name}:{i if i is not None else ""}:{"/".join(map(str, e.path))}: {e.message}'
            for i, value in values for e in validator.iter_errors(value)]


def load(root):
    data = {'run.json': read_json(child(root, 'run.json'))}
    for name in FILES:
        raw = read_bytes(child(root, name)).decode('utf-8')
        data[name] = [parse(line) for line in raw.splitlines() if line.strip()] if name.endswith('.jsonl') else parse(raw)
    return data


def digest(data):
    return hashlib.sha256(data).hexdigest()


def control(run):
    return digest(encoded({k: v for k, v in run.items() if k not in ('hashes', 'control_hash', 'updated_at', 'decisions')}))


def hashes(root):
    names = list(FILES)
    papers = child(root, 'papers')
    if papers.exists():
        for p in sorted(papers.rglob('*')):
            clean_path(p)
            if p.is_file():
                names.append(p.relative_to(root).as_posix())
    return {name: digest(read_bytes(child(root, name))) for name in names}


def changed(root, run):
    current = hashes(root)
    diff = sorted(k for k in current.keys() | run['hashes'].keys() if current.get(k) != run['hashes'].get(k))
    if control(run) != run['control_hash']:
        diff.append('run.json')
    return diff


def structure(data):
    errors = []
    for name, value in data.items():
        errors.extend(schema_errors(name, value))
    if errors:
        return errors
    run = data['run.json']
    indices = {}
    for name, key in [('sources.jsonl', 'source_id'), ('claims.jsonl', 'claim_id'),
                      ('search-log.jsonl', 'search_id'), ('gaps.json', 'gap_id'),
                      ('candidates.json', 'candidate_id'), ('reviews.json', 'review_id')]:
        index = {}
        for x in data[name]:
            if x[key] in index:
                errors.append('duplicate ID: ' + x[key])
            index[x[key]] = x
        indices[name] = index
    sources, claims = indices['sources.jsonl'], indices['claims.jsonl']
    seen = {}
    cutoff = run['config']['cutoff']
    for sid, source in sources.items():
        # Treat alternate versions as one ledger source; record versions in its reading scope.
        ident = (source['identifier'] or source['url'] or source['title']).strip().lower().rstrip('/')
        if ident in seen:
            errors.append('duplicate source identity: ' + sid + '/' + seen[ident])
        seen[ident] = sid
        if source['synthetic'] != (source['source_type'] == 'synthetic') or (source['synthetic'] and not sid.startswith('synthetic-')):
            errors.append('synthetic sources require synthetic- IDs and source_type')
        if source['synthetic'] and source['identifier'] and not source['identifier'].startswith('synthetic:'):
            errors.append('synthetic identifier must use synthetic: namespace')
        if cutoff:
            for key in ('published_date', 'version_date'):
                if source[key] and source[key] > cutoff:
                    errors.append(f'{sid}: {key} exceeds cutoff')
    def refs(values, index, label):
        for value in values:
            if value not in index:
                errors.append(label + ': missing ID ' + value)
    for c in claims.values():
        for e in c['evidence']:
            refs([e['source_id']], sources, c['claim_id'])
            src = sources.get(e['source_id'])
            if src and e['requires_full_text'] and src['reading_status'] in ('unread', 'abstract_only'):
                errors.append(c['claim_id'] + ': full-text evidence claimed without full-text reading')
        if c['result_origin'] == 'new_measured':
            errors.append(c['claim_id'] + ': unexecuted proposals cannot claim new measured results')
    for x in data['search-log.jsonl']:
        refs(x['found_source_ids'], sources, x['search_id'])
        if x['status'] == 'failed' and not x['error']:
            errors.append(x['search_id'] + ': failed search needs an error')
    axes = {}
    for x in data['gaps.json']:
        refs(x['claim_ids'], claims, x['gap_id'])
        refs(x['near_miss_source_ids'], sources, x['gap_id'])
        axes[x['axis']] = axes.get(x['axis'], 0) + (x['status'] != 'rejected')
    if any(n > 2 for n in axes.values()):
        errors.append('at most two active gaps per axis')
    for x in data['candidates.json']:
        refs([x['gap_id']], indices['gaps.json'], x['candidate_id'])
        refs(x['claim_ids'], claims, x['candidate_id'])
        refs(x['source_ids'], sources, x['candidate_id'])
        if x['revision'] > run['budget']['limits']['revisions']:
            errors.append(x['candidate_id'] + ': revision limit exceeded')
    for x in data['reviews.json']:
        refs([x['candidate_id']], indices['candidates.json'], x['review_id'])
        refs(x['claim_ids'], claims, x['review_id'])
        refs(x['search_ids'], indices['search-log.jsonl'], x['review_id'])
        if x['verdict'] == 'survive' and x['tool_status'] == 'failed':
            errors.append(x['review_id'] + ': failed reviewer cannot survive')
        if x['isolation'] == 'proposal-blind' and x['history_inherited']:
            errors.append(x['review_id'] + ': inherited history cannot be proposal-blind')
    for candidate in data['candidates.json']:
        matching = [r for r in data['reviews.json'] if r['candidate_id'] == candidate['candidate_id'] and r['revision'] == candidate['revision']]
        if candidate['status'] == 'survive' and (not matching or matching[-1]['verdict'] != 'survive'):
            errors.append(candidate['candidate_id'] + ': survival contradicts latest review')
    p = data['proposal.json']
    if run['stop_reason'] == 'all_rejected' and p['outcome'] == 'recommend':
        errors.append('all_rejected cannot recommend a candidate')
    refs(p['candidate_ids'], indices['candidates.json'], 'proposal')
    refs(p['claim_ids'], claims, 'proposal')
    if p['outcome'] != 'recommend' and p['candidate_ids']:
        errors.append('non-recommendation must not select candidates')
    if run['status'] == 'stopped' and not run['stop_reason']:
        errors.append('stopped run requires a stop reason')
    if run['status'] == 'active' and run['stop_reason']:
        errors.append('active run cannot have a stop reason')
    if run['config']['literature_mode'] == 'retrospective' and not cutoff:
        errors.append('retrospective requires a cutoff')
    if run['execution'] == 'native-subagents' and run['capabilities']['subagents']['status'] != 'available':
        errors.append('native-subagents requires recorded subagent availability')
    used, limits = run['budget']['used'], run['budget']['limits']
    for k in used:
        if used[k] > limits[k]:
            errors.append('budget exceeded: ' + k)
    if len(data['candidates.json']) > limits['candidates']:
        errors.append('candidate limit exceeded')
    if used['searches'] < len(data['search-log.jsonl']) or used['candidates'] < len(data['candidates.json']):
        errors.append('budget usage undercounts recorded searches/candidates')
    return errors


def quality(data, root=None):
    """Check recorded prerequisites, never scientific truth."""
    blockers = []
    sources = {x['source_id']: x for x in data['sources.jsonl']}
    claims = {x['claim_id']: x for x in data['claims.jsonl']}
    run, proposal = data['run.json'], data['proposal.json']
    selected = proposal['candidate_ids']
    if proposal['outcome'] != 'recommend' or not selected:
        blockers.append('no candidate recommended')
    if any(run['stages'][k] != 'complete' for k in STAGES):
        blockers.append('required stages are incomplete or stale')
    def source_ok(sid):
        src = sources.get(sid)
        return bool(src and not src['synthetic'] and src['existence'] == 'verified'
                    and src['existence_method'] and (src['identifier'] or src['url'])
                    and src['reading_status'] in ('targeted_full_text', 'full_text')
                    and src['read_scope']
                    and (not run['config']['cutoff'] or (src['published_date'] and src['version_date'])))
    def claim_ok(cid):
        c = claims.get(cid)
        if not c or c['kind'] not in ('fact', 'inference'):
            return False
        positive = [e for e in c['evidence'] if e['relation'] == 'supports']
        return bool(positive and all(source_ok(e['source_id']) and e['relevance'] == 'verified'
                                     and e['support'] == 'verified' for e in positive)
                    and not any(e['relation'] == 'contradicts' and e['support'] == 'verified' for e in c['evidence']))
    for c in claims.values():
        if c['critical'] and c['kind'] in ('fact', 'inference', 'unsupported') and not claim_ok(c['claim_id']):
            blockers.append('unsupported critical claim (synthetic, unverified or inadequate evidence): ' + c['claim_id'])
    gaps = {x['gap_id']: x for x in data['gaps.json']}
    candidates = {x['candidate_id']: x for x in data['candidates.json']}
    linked = set(proposal['claim_ids']) if selected else set()
    for candidate in data['candidates.json']:
        if candidate['candidate_id'] in selected:
            linked.update(candidate['claim_ids'])
    for cid in linked:
        c = claims.get(cid)
        if not c or c['kind'] in ('fact', 'inference', 'unsupported') and not claim_ok(cid):
            blockers.append('selected proposal depends on unsupported claim: ' + cid)
    for cid in selected:
        c = candidates.get(cid)
        if not c:
            continue
        g = gaps.get(c['gap_id'])
        if not g or g['status'] != 'grounded' or not g['claim_ids'] or not all(claim_ok(x) for x in g['claim_ids']):
            blockers.append(cid + ': gap is not grounded')
        if not g or not g['near_miss_source_ids'] or not all(source_ok(x) for x in g['near_miss_source_ids']):
            blockers.append(cid + ': near-miss evidence missing')
        if c['status'] != 'survive' or not c['claim_ids'] or not c['source_ids'] or not all(source_ok(x) for x in c['source_ids']):
            blockers.append(cid + ': candidate support/status incomplete')
        matching = [r for r in data['reviews.json'] if r['candidate_id'] == cid and r['revision'] == c['revision']]
        r = matching[-1] if matching else None
        if not r or r['verdict'] != 'survive' or r['tool_status'] != 'ok' or not r['claim_ids'] or not all(claim_ok(x) for x in r['claim_ids']):
            blockers.append(cid + ': no successful evidence-backed review for this revision')
        if r:
            searches = {s['search_id']: s for s in data['search-log.jsonl']}
            if not any(sid in searches and searches[sid]['status'] == 'ok' and searches[sid]['regime'] == 'counterexample' for sid in r['search_ids']):
                blockers.append(cid + ': no logged counterexample search')
            if run['config']['depth'] == 'deep':
                n = r['non_obviousness']
                if n['status'] != 'scored' or r['history_inherited'] or r['isolation'] == 'same-context':
                    blockers.append(cid + ': deep non-obviousness unscored')
                elif root is not None:
                    try:
                        frozen = read_bytes(child(root, n['frozen_file'] or ''))
                        obj = parse(frozen)
                        if digest(frozen) != n['frozen_sha256'] or not obj.get('mechanisms') or obj.get('proposal_seen') is not False:
                            blockers.append(cid + ': invalid frozen derivation')
                    except (OSError, ValueError, TypeError):
                        blockers.append(cid + ': frozen derivation unavailable')
    if selected:
        for key in ('title', 'problem', 'failure_case', 'hypothesis', 'contribution', 'mechanism', 'implementation'):
            if not proposal[key].strip():
                blockers.append('proposal missing ' + key)
        if not proposal['experiments'] or not proposal['claim_ids'] or not proposal['limitations']:
            blockers.append('proposal needs experiments, claim links and limitations')
    return sorted(set(blockers))


def check(root):
    data = load(root)
    errors = structure(data)
    if not errors:
        diff = changed(root, data['run.json'])
        errors.extend('stale hash: ' + x for x in diff)
    blockers = quality(data, root) if not errors else ['structural validation failed']
    return {'structure': {'status': 'PASS' if not errors else 'FAIL', 'errors': errors},
            'recommendation_gate': {'status': 'PASS' if not blockers else 'BLOCKED', 'blockers': blockers},
            'semantic_truth': {'status': 'NOT_AUTOMATICALLY_VERIFIED',
                               'note': 'Existence, relevance and support are recorded attestations; schema and hashes cannot prove them.'}}


def persist(root, data, names):
    for name in names:
        atomic(child(root, name), file_bytes(name, data[name]), replace=True)
    run = data['run.json']
    run['updated_at'] = now()
    run['hashes'] = hashes(root)
    run['control_hash'] = control(run)
    atomic(child(root, 'run.json'), encoded(run), replace=True)


def empty_proposal():
    return {'outcome': 'pending', 'candidate_ids': [], **{k: '' for k in
            ('title', 'problem', 'failure_case', 'hypothesis', 'contribution', 'mechanism', 'implementation')},
            'claim_ids': [], 'experiments': [], 'limitations': [], 'next_diagnostics': [], 'results_status': 'not_executed'}


def init_run(workspace, run_id, brief_path=None, task='ideate', depth='standard', literature_mode='local-only', profile='generic', cutoff=None):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', run_id):
        raise ArtifactError('invalid run ID')
    workspace = clean_path(workspace)
    if workspace == SKILL or workspace.is_relative_to(SKILL):
        raise ArtifactError('run outputs must be outside the installed skill')
    workspace.mkdir(parents=True, exist_ok=True)
    root = child(workspace, run_id)
    brief = read_json(brief_path or SKILL / 'assets/templates/brief.json')
    limits = read_json(SKILL / 'assets/profiles/generic.json')['defaults'][depth]
    caps = {k: {'status': 'untested', 'tool': None, 'note': 'Host must probe actual availability.'} for k in
            ('network_search', 'paper_reading', 'local_files', 'python', 'repository_reading', 'subagents', 'context_isolation')}
    for k in ('local_files', 'python'):
        caps[k] = {'status': 'available', 'tool': 'research_artifacts.py', 'note': 'CLI executed in this runtime.'}
    run = {'schema_version': 1, 'skill_version': VERSION, 'run_id': run_id, 'created_at': now(), 'updated_at': now(),
           'config': dict(task=task, depth=depth, literature_mode=literature_mode, profile=profile, cutoff=cutoff),
           'capabilities': caps, 'execution': 'serial', 'budget': {'limits': limits, 'used': {k: 0 for k in ('searches', 'reads', 'candidates', 'concurrency')}},
           'stages': {k: 'complete' if k == 'define' else 'pending' for k in STAGES}, 'status': 'active',
           'stop_reason': None, 'hashes': {}, 'control_hash': '', 'decisions': []}
    data = {'run.json': run, 'brief.json': brief, **{n: [] for n in FILES if n not in ('brief.json', 'proposal.json')}, 'proposal.json': empty_proposal()}
    errors = structure(data)
    if errors:
        raise ArtifactError('; '.join(errors))
    root.mkdir()  # exclusive; never reinitialize an existing run
    with locked(root):
        for name in FILES:
            atomic(child(root, name), file_bytes(name, data[name]))
        run['hashes'] = hashes(root)
        run['control_hash'] = control(run)
        atomic(child(root, 'run.json'), encoded(run))
    return {'run_id': run_id, 'status': 'initialized'}


def invalidate(data, earliest):
    for stage in STAGES[earliest:]:
        data['run.json']['stages'][stage] = 'stale'
    if earliest <= 3:
        for candidate in data['candidates.json']:
            candidate['status'] = 'stale'
    data['proposal.json']['outcome'] = 'pending'
    data['proposal.json']['candidate_ids'] = []


def update_run(root, bundle):
    with locked(root):
        data = load(root)
        if changed(root, data['run.json']):
            raise ArtifactError('changed artifacts detected; run resume first')
        if not isinstance(bundle, dict) or set(bundle) - {'artifacts', 'run'}:
            raise ArtifactError('update accepts artifacts and run only')
        artifacts = bundle.get('artifacts', {})
        if not isinstance(artifacts, dict) or set(artifacts) - set(FILES):
            raise ArtifactError('unrecognized artifact path')
        updates = bundle.get('run', {})
        allowed = {'config', 'capabilities', 'execution', 'budget', 'status', 'stop_reason'}
        if not isinstance(updates, dict) or set(updates) - allowed:
            raise ArtifactError('unrecognized run update')
        changed_names = [n for n, v in artifacts.items() if v != data[n]]
        dependencies = [STAGE[n] + 1 for n in changed_names]
        old_run = data['run.json']
        if 'config' in updates and updates['config'] != old_run['config']:
            dependencies.append(0)
        if 'budget' in updates and updates['budget'].get('limits') != old_run['budget']['limits']:
            dependencies.append(0)
        if any(k in updates and updates[k] != old_run[k] for k in ('capabilities', 'execution')):
            dependencies.append(4)
        if dependencies and min(dependencies) <= 5:
            invalidate(data, min(dependencies))
        for name, value in artifacts.items():
            data[name] = value
            data['run.json']['stages'][STAGES[STAGE[name]]] = 'complete'
        data['run.json'].update(updates)
        used = data['run.json']['budget']['used']
        used['searches'] = max(used['searches'], len(data['search-log.jsonl']))
        used['candidates'] = max(used['candidates'], len(data['candidates.json']))
        data['run.json']['decisions'].append({'at': now(), 'summary': 'Single-writer update: ' + ', '.join(sorted(artifacts))})
        errors = structure(data)
        if errors:
            raise ArtifactError('; '.join(errors))
        if data['proposal.json']['outcome'] == 'recommend':
            blockers = quality(data, root)
            if blockers:
                raise ArtifactError('recommendation blocked: ' + '; '.join(blockers))
        persist(root, data, FILES)
    return check(root)


def resume_run(root):
    with locked(root):
        data = load(root)
        # Version/schema mismatches are not silently migrated.
        errs = [e for name, value in data.items() for e in schema_errors(name, value)]
        if errs:
            raise ArtifactError('; '.join(errs))
        diff = changed(root, data['run.json'])
        if diff:
            earliest = min([STAGE.get(x, 1) for x in diff if x != 'run.json'] + ([0] if 'run.json' in diff else [6]))
            invalidate(data, earliest)
            data['run.json']['status'] = 'active'
            data['run.json']['stop_reason'] = None
            data['run.json']['decisions'].append({'at': now(), 'summary': 'Resume invalidated dependent stages after changes: ' + ', '.join(diff)})
            persist(root, data, ('candidates.json', 'proposal.json'))
    result = check(root)
    result['resume'] = {'changed': diff, 'next_stages': [k for k, v in data['run.json']['stages'].items() if v != 'complete']}
    return result


def esc(value):
    # Render external text as inert text, including Markdown images/links and HTML.
    if isinstance(value, list):
        value = '; '.join(str(x) for x in value)
    value = html.escape(str(value), quote=False)
    return re.sub(r'([\\`*_{}\[\]()#+.!|>~-])', r'\\\1', value).replace('\n', ' ')


def render(root, replace=False):
    with locked(root):
        result = check(root)
        if result['structure']['status'] != 'PASS':
            raise ArtifactError('render refused: ' + '; '.join(result['structure']['errors']))
        data = load(root)
        run, p = data['run.json'], data['proposal.json']
        if p['outcome'] == 'recommend' and result['recommendation_gate']['status'] != 'PASS':
            raise ArtifactError('render refused: recommendation gate blocked')
        zh = data['brief.json']['language'].lower().startswith('zh')
        title = '科研构思记录' if zh else 'Research ideation record'
        lines = ['# ' + title, '', '**' + esc(p['outcome']) + '**', '',
                 'Structure: PASS. Semantic truth: NOT_AUTOMATICALLY_VERIFIED.', '',
                 ('串行自审；不属于独立评审。' if zh else 'Serial self-review; not independent review.') if run['execution'] == 'serial' else 'Native subagents; inspect each review isolation record.', '',
                 'Mode: ' + esc(run['config']['literature_mode']) + '; cutoff: ' + esc(run['config']['cutoff']), '',
                 'Stop reason: ' + esc(run['stop_reason']), '', '## ' + esc(p['title'] or title), '']
        for k in ('problem', 'failure_case', 'hypothesis', 'contribution', 'mechanism', 'implementation'):
            if p[k]:
                lines.extend(['**' + k + '**: ' + esc(p[k]), ''])
        for k in ('limitations', 'next_diagnostics'):
            lines.extend(['## ' + k, ''] + ['- ' + esc(x) for x in p[k]] + [''])
        lines.extend(['## Experiments — not executed', ''])
        for experiment in p['experiments']:
            for k, v in experiment.items():
                lines.append('- **' + k + '**: ' + esc(v))
            lines.append('')
        lines.extend(['## Candidate and review trail', ''])
        for c in data['candidates.json']:
            lines.append('- ' + esc(c['candidate_id']) + ': ' + esc(c['status']) + ' — ' + esc(c['intuition']))
        for r in data['reviews.json']:
            lines.append('- ' + esc(r['review_id']) + ' → ' + esc(r['candidate_id']) + ': ' + esc(r['verdict']) + '; ' + esc(r['strongest_objection']) + '; evidence: ' + esc(', '.join(r['claim_ids'])))
        lines.extend(['', '## Claim ledger', ''])
        for c in data['claims.jsonl']:
            lines.append('- **' + esc(c['claim_id']) + '** [' + esc(c['kind']) + ']: ' + esc(c['statement']))
            for e in c['evidence']:
                lines.append('  - ' + esc(e['source_id']) + ' / ' + esc(e['locator']) + ': ' + esc(e['paraphrase']) + ' (' + esc(e['relation']) + '; support=' + esc(e['support']) + ')')
        lines.extend(['', '## Sources', ''])
        for s in data['sources.jsonl']:
            lines.append('- **' + esc(s['source_id']) + '**: ' + esc(s['title']) + ' — ' + esc(s['url'] or s['identifier']) + '; ' + esc(s['version']) + '; ' + esc(s['reading_status']) + '; existence=' + esc(s['existence']) + ('; SYNTHETIC TEST DATA' if s['synthetic'] else ''))
        lines.extend(['', '## Coverage and checks', '', '- Searches: ' + str(len(data['search-log.jsonl'])), '- ' + esc(result['semantic_truth']['note'])])
        lines.extend('- ' + esc(x) for x in result['recommendation_gate']['blockers'])
        atomic(child(root, 'report.md'), ('\n'.join(lines) + '\n').encode(), replace=replace)
    return {'status': 'rendered', 'file': 'report.md'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init', help='Create a new run without overwriting anything')
    p.add_argument('--workspace', required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--brief')
    p.add_argument('--task', choices=['ideate', 'audit', 'resume'], default='ideate')
    p.add_argument('--depth', choices=['quick', 'standard', 'deep'], default='standard')
    p.add_argument('--literature-mode', choices=['live', 'local-only', 'retrospective'], default='local-only')
    p.add_argument('--profile', choices=['generic', 'vla-world-model'], default='generic')
    p.add_argument('--cutoff')
    for name in ('validate', 'audit', 'render', 'resume', 'update'):
        p = sub.add_parser(name, help={'validate': 'Check structure, IDs, hashes and recorded quality prerequisites', 'audit': 'Separate deterministic checks from semantic verification', 'render': 'Render inert Markdown from structured artifacts', 'resume': 'Detect changed inputs and invalidate dependent conclusions', 'update': 'Merge an explicit single-writer JSON bundle'}[name])
        p.add_argument('--run', required=True)
        if name in ('validate', 'audit'):
            p.add_argument('--require-recommendable', action='store_true')
        if name == 'render':
            p.add_argument('--replace', action='store_true', help='Explicitly regenerate an existing report')
        if name == 'update':
            p.add_argument('--input', required=True)
    args = parser.parse_args(argv)
    try:
        if sys.version_info < (3, 10):
            raise ArtifactError('Python 3.10+ is required')
        if args.command == 'init':
            result = init_run(args.workspace, args.run_id, args.brief, args.task, args.depth, args.literature_mode, args.profile, args.cutoff)
        else:
            root = clean_path(args.run)
            if args.command in ('validate', 'audit'):
                with locked(root):
                    result = check(root)
            elif args.command == 'resume':
                result = resume_run(root)
            elif args.command == 'render':
                result = render(root, args.replace)
            else:
                result = update_run(root, read_json(args.input))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result.get('structure', {}).get('status') == 'FAIL':
            return 1
        if getattr(args, 'require_recommendable', False) and result['recommendation_gate']['status'] != 'PASS':
            return 2
        return 0
    except (ArtifactError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
