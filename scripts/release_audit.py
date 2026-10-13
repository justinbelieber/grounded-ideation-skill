#!/usr/bin/env python3
"""Scan actual staged bytes; findings need human review, never automatic legal clearance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, check=True)
    return result.stdout


def scan(root):
    if not (root / '.git').exists():
        raise ValueError('requires this repository to be initialized and intended files staged')
    names = git(root, 'ls-files', '--cached', '-z').decode().split('\0')
    names = [x for x in names if x]
    if not names:
        raise ValueError('no staged files')
    patterns = {
        'machine-path': re.compile(r'/(?:Us' + r'ers|ho' + r'me)/[^\s/]+'),
        'email': re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+'),
        'credential': re.compile(r'(?:gh' + r'p_[A-Za-z0-9]{30,}|sk' + r'-[A-Za-z0-9_-]{25,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)'),
    }
    findings, inventory = [], []
    for name in names:
        mode = git(root, 'ls-files', '--stage', '--', name).decode().split()[0]
        raw = git(root, 'show', ':' + name)
        inventory.append({'path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
        if mode == '120000':
            findings.append({'path': name, 'kind': 'symlink'})
        if any(x in Path(name).parts for x in ('runs', 'private', '.env', '__pycache__')) or Path(name).suffix in ('.pdf', '.db', '.sqlite', '.safetensors', '.pt', '.log'):
            findings.append({'path': name, 'kind': 'private-or-large-resource'})
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            findings.append({'path': name, 'kind': 'binary-needs-review'})
            continue
        for kind, pattern in patterns.items():
            for match in pattern.finditer(text):
                findings.append({'path': name, 'kind': kind, 'line': text.count('\n', 0, match.start()) + 1})
    required = {'LICENSE', 'THIRD_PARTY_NOTICES.md', 'CITATION.cff', 'docs/release-checklist.md'}
    for name in sorted(required - set(names)):
        findings.append({'path': name, 'kind': 'missing-release-file'})
    state = json.loads(git(root, 'show', ':docs/release-state.json'))
    pending = [k for k, v in state['maintainer_confirmations'].items() if v is not True]
    return {'status': 'RELEASE_BLOCKED' if findings or pending else 'READY_FOR_HUMAN_RELEASE_REVIEW',
            'scope': 'actual staged bytes, not just ignore patterns', 'files_scanned': len(names),
            'findings': findings, 'pending_confirmations': pending, 'inventory': inventory,
            'limits': 'Heuristic privacy/credential scan. Human provenance, licensing, claims and identity review remains required.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', default='.')
    args = p.parse_args()
    try:
        result = scan(Path(args.repo).resolve())
        print(json.dumps(result, indent=2))
        return 2 if result['status'] == 'RELEASE_BLOCKED' else 0
    except (OSError, ValueError, subprocess.CalledProcessError) as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
