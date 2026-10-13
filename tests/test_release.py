import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release', ROOT / 'scripts/release_audit.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class Release(unittest.TestCase):
    def test_scans_staged_bytes_even_when_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'docs').mkdir()
            for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md', 'CITATION.cff', 'docs/release-checklist.md'):
                (root / name).write_text('test-only')
            (root / 'docs/release-state.json').write_text(json.dumps({'maintainer_confirmations': {'license': False}}))
            (root / '.gitignore').write_text('private.txt\n')
            (root / 'private.txt').write_text('test' + '@' + 'example.invalid')
            subprocess.run(['git', '-C', d, 'add', '.'], check=True)
            subprocess.run(['git', '-C', d, 'add', '-f', 'private.txt'], check=True)
            (root / 'private.txt').write_text('clean working copy')
            result = a.scan(root)
            self.assertEqual(result['status'], 'RELEASE_BLOCKED')
            self.assertTrue(any(x['kind'] == 'email' and x['path'] == 'private.txt' for x in result['findings']))
            self.assertEqual(result['pending_confirmations'], ['license'])

if __name__ == '__main__':
    unittest.main()
