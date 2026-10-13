import json
from pathlib import Path
import re
import unittest
import yaml
from jsonschema import Draft202012Validator
ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/grounded-ideation'

class Skill(unittest.TestCase):
    def test_manifest_metadata_links(self):
        body = (SKILL / 'SKILL.md').read_text()
        front = yaml.safe_load(body.split('---', 2)[1])
        self.assertEqual(front['name'], SKILL.name)
        self.assertRegex(front['name'], r'^[a-z0-9-]{1,63}$')
        self.assertLessEqual(len(body.splitlines()), 250)
        self.assertIn('do not', front['description'])
        meta = yaml.safe_load((SKILL / 'agents/openai.yaml').read_text())
        self.assertIn('$grounded-ideation', meta['interface']['default_prompt'])
        self.assertTrue(meta.get('policy', {}).get('allow_implicit_invocation', True))
        for file in SKILL.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)', file.read_text()):
                if '://' not in link and not link.startswith('#'):
                    resolved = (file.parent / link.split('#')[0]).resolve()
                    self.assertTrue(resolved.is_relative_to(SKILL.resolve()), (file, link))
                    self.assertTrue(resolved.exists(), (file, link))

    def test_json_schemas_valid(self):
        for file in (SKILL / 'assets/schemas').glob('*.json'):
            Draft202012Validator.check_schema(json.loads(file.read_text()))

if __name__ == '__main__':
    unittest.main()
