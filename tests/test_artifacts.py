import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/grounded-ideation'
SCRIPT = SKILL / 'scripts/research_artifacts.py'
spec = importlib.util.spec_from_file_location('artifacts', SCRIPT)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class Artifacts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name).resolve()
        a.init_run(self.ws, 'test')
        self.run = self.ws / 'test'
        self.bundle = json.loads((ROOT / 'tests/fixtures/rejected-update.json').read_text())

    def tearDown(self):
        self.tmp.cleanup()

    def demo(self):
        return a.update_run(self.run, self.bundle)

    def test_help_all_commands(self):
        for cmd in ([], ['init'], ['validate'], ['render'], ['audit'], ['resume'], ['update']):
            r = subprocess.run([sys.executable, str(SCRIPT), *cmd, '--help'], capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_init_and_overwrite(self):
        self.assertEqual(a.check(self.run)['structure']['status'], 'PASS')
        with self.assertRaises(FileExistsError):
            a.init_run(self.ws, 'test')

    def test_schema_invalid_and_duplicate_json_keys(self):
        with self.assertRaises(a.ArtifactError):
            a.parse('{"x":1,"x":2}')
        self.bundle['artifacts']['proposal.json']['unexpected'] = True
        with self.assertRaises(a.ArtifactError):
            self.demo()

    def test_rejected_fixture_end_to_end(self):
        result = self.demo()
        self.assertEqual(result['structure']['status'], 'PASS')
        self.assertEqual(result['recommendation_gate']['status'], 'BLOCKED')
        self.assertEqual(result['semantic_truth']['status'], 'NOT_AUTOMATICALLY_VERIFIED')
        a.render(self.run)
        self.assertIn('SYNTHETIC TEST DATA', (self.run / 'report.md').read_text())
        self.assertEqual(a.resume_run(self.run)['resume']['changed'], [])
        with self.assertRaises(a.ArtifactError):
            a.render(self.run)
        a.render(self.run, True)

    def test_missing_reference(self):
        self.bundle['artifacts']['claims.jsonl'][0]['evidence'][0]['source_id'] = 'missing'
        with self.assertRaisesRegex(a.ArtifactError, 'missing ID'):
            self.demo()

    def test_synthetic_and_unverified_source_never_recommendable(self):
        self.demo()
        data = a.load(self.run)
        self.assertTrue(any('unsupported critical claim' in x for x in a.quality(data)))
        data['sources.jsonl'][0]['synthetic'] = False
        data['sources.jsonl'][0]['source_type'] = 'paper'
        data['sources.jsonl'][0]['existence'] = 'unverified'
        self.assertTrue(any('unsupported critical claim' in x for x in a.quality(data)))

    def test_abstract_only_not_full_read(self):
        self.bundle['artifacts']['sources.jsonl'][0]['reading_status'] = 'abstract_only'
        with self.assertRaisesRegex(a.ArtifactError, 'full-text'):
            self.demo()

    def test_cutoff_publication_and_revision(self):
        for key in ('published_date', 'version_date'):
            with self.subTest(key=key):
                b = copy.deepcopy(self.bundle)
                b['artifacts']['sources.jsonl'][0][key] = '2025-01-02'
                run = a.load(self.run)['run.json']
                b['run']['config'] = {**run['config'], 'literature_mode': 'retrospective', 'cutoff': '2025-01-01'}
                with self.assertRaisesRegex(a.ArtifactError, 'cutoff'):
                    a.update_run(self.run, b)

    def test_retrospective_requires_cutoff(self):
        with self.assertRaisesRegex(a.ArtifactError, 'cutoff'):
            a.init_run(self.ws, 'retro', literature_mode='retrospective')

    def test_results_origin(self):
        self.bundle['artifacts']['claims.jsonl'][0]['result_origin'] = 'new_measured'
        with self.assertRaisesRegex(a.ArtifactError, 'measured'):
            self.demo()
        self.bundle['artifacts']['claims.jsonl'][0]['result_origin'] = 'prior_work'
        self.demo()

    def test_failed_reviewer_not_pass(self):
        r = self.bundle['artifacts']['reviews.json'][0]
        r.update(verdict='survive', tool_status='failed')
        with self.assertRaisesRegex(a.ArtifactError, 'failed reviewer'):
            self.demo()
        r['verdict'] = 'insufficient_evidence'
        self.demo()

    def test_budget_exhaustion_is_valid_stop(self):
        run = a.load(self.run)['run.json']
        budget = copy.deepcopy(run['budget'])
        budget['limits']['searches'] = 1
        self.bundle['run'].update(budget=budget, stop_reason='budget_exhausted')
        self.demo()
        self.assertEqual(a.load(self.run)['run.json']['stop_reason'], 'budget_exhausted')
        budget['used']['reads'] = 999
        with self.assertRaisesRegex(a.ArtifactError, 'budget exceeded'):
            a.update_run(self.run, {'run': {'budget': budget}})

    def test_duplicate_ids_and_source_identity(self):
        for same_id in (True, False):
            b = copy.deepcopy(self.bundle)
            extra = copy.deepcopy(b['artifacts']['sources.jsonl'][0])
            if not same_id:
                extra['source_id'] = 'synthetic-other'
            b['artifacts']['sources.jsonl'].append(extra)
            with self.assertRaisesRegex(a.ArtifactError, 'duplicate'):
                a.update_run(self.run, b)

    def test_traversal_and_output_escape(self):
        for run_id in ('../escape', '/escape', '.', 'x/y'):
            with self.assertRaises(a.ArtifactError):
                a.init_run(self.ws, run_id)
        with self.assertRaises(a.ArtifactError):
            a.update_run(self.run, {'artifacts': {'../escape.json': {}}})
        with self.assertRaises(a.ArtifactError):
            a.init_run(SKILL / 'runs', 'bad')

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symlink unavailable')
    def test_symlink_outside_and_inside(self):
        outside = self.ws / 'secret'
        outside.write_text('untouched')
        for name in ('report.md', 'brief.json'):
            p = self.run / name
            if p.exists():
                p.unlink()
            p.symlink_to(outside)
            with self.assertRaises(a.ArtifactError):
                a.render(self.run)
            p.unlink()
        self.assertEqual(outside.read_text(), 'untouched')

    def test_stale_brief_invalidates_conclusions(self):
        self.demo()
        data = a.read_json(self.run / 'brief.json')
        data['constraints']['time'] = 'one day'
        (self.run / 'brief.json').write_bytes(a.encoded(data))
        self.assertEqual(a.check(self.run)['structure']['status'], 'FAIL')
        with self.assertRaises(a.ArtifactError):
            a.render(self.run)
        result = a.resume_run(self.run)
        self.assertIn('brief.json', result['resume']['changed'])
        self.assertEqual(a.load(self.run)['proposal.json']['outcome'], 'pending')
        self.assertEqual(a.load(self.run)['candidates.json'][0]['status'], 'stale')

    def test_control_hash_changes_and_version_refusal(self):
        data = a.read_json(self.run / 'run.json')
        data['config']['cutoff'] = '2024-02-01'
        (self.run / 'run.json').write_bytes(a.encoded(data))
        self.assertIn('run.json', a.resume_run(self.run)['resume']['changed'])
        data = a.read_json(self.run / 'run.json')
        data['skill_version'] = '99.0.0'
        (self.run / 'run.json').write_bytes(a.encoded(data))
        with self.assertRaises(a.ArtifactError):
            a.resume_run(self.run)

    def test_lock_blocks_second_process(self):
        with a.locked(self.run):
            r = subprocess.run([sys.executable, str(SCRIPT), 'resume', '--run', str(self.run)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn('lock', r.stderr)
        self.assertFalse((self.run / '.writer.lock').exists())

    def test_injection_is_inert_and_render_escaped(self):
        payload = '<script>upload()</script> ![steal](https://invalid.example/secret) `touch PWNED`'
        self.bundle['artifacts']['claims.jsonl'][0]['statement'] = payload
        self.demo()
        a.render(self.run)
        text = (self.run / 'report.md').read_text()
        self.assertNotIn('<script>', text)
        self.assertNotIn('![steal]', text)
        self.assertFalse((self.ws / 'PWNED').exists())

    def test_deep_false_blindness(self):
        r = self.bundle['artifacts']['reviews.json'][0]
        r['isolation'] = 'proposal-blind'
        with self.assertRaisesRegex(a.ArtifactError, 'history'):
            self.demo()

    def test_changed_evidence_requires_rechecking_that_stage(self):
        self.demo()
        source = self.bundle['artifacts']['sources.jsonl'][0]
        source['limitations'].append('New evidence limitation')
        (self.run / 'sources.jsonl').write_bytes(a.file_bytes('sources.jsonl', [source]))
        a.resume_run(self.run)
        self.assertEqual(a.load(self.run)['run.json']['stages']['evidence'], 'stale')

    def test_candidate_review_state_contradiction(self):
        self.bundle['artifacts']['candidates.json'][0]['status'] = 'survive'
        with self.assertRaises(a.ArtifactError):
            self.demo()

    def test_missing_evidence_can_be_saved_but_never_passes(self):
        self.bundle['artifacts']['claims.jsonl'][0]['evidence'] = []
        result = self.demo()
        self.assertEqual(result['structure']['status'], 'PASS')
        self.assertEqual(result['recommendation_gate']['status'], 'BLOCKED')

    def test_render_arrays_are_readable(self):
        self.assertEqual(a.esc(['baseline one', 'baseline two']), 'baseline one; baseline two')

    def test_deep_empty_frozen_record_is_not_novelty(self):
        self.demo()
        data = a.load(self.run)
        data['run.json']['config']['depth'] = 'deep'
        data['proposal.json'].update(outcome='recommend', candidate_ids=['synthetic-candidate-1'])
        review = data['reviews.json'][0]
        review.update(isolation='separate-context', history_inherited=False)
        frozen = a.encoded({'proposal_seen': False, 'mechanisms': []})
        (self.run / 'papers').mkdir()
        (self.run / 'papers/frozen.json').write_bytes(frozen)
        review['non_obviousness'].update(status='scored', frozen_file='papers/frozen.json', frozen_sha256=a.digest(frozen))
        self.assertIn('synthetic-candidate-1: invalid frozen derivation', a.quality(data, self.run))

    def test_usage_update_preserves_decision(self):
        self.demo()
        budget = a.load(self.run)['run.json']['budget']
        budget['used']['reads'] = 1
        a.update_run(self.run, {'run': {'budget': budget}})
        self.assertEqual(a.load(self.run)['proposal.json']['outcome'], 'no_recommendation')

    def test_installed_skill_is_self_contained(self):
        installed = self.ws / '.agents/skills/grounded-ideation'
        shutil.copytree(SKILL, installed, ignore=shutil.ignore_patterns('__pycache__'))
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
        r = subprocess.run([sys.executable, str(installed / 'scripts/research_artifacts.py'), 'init', '--workspace', str(self.ws / 'isolated'), '--run-id', 'copy'], cwd=self.ws, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.ws / 'isolated/copy/run.json').exists())


if __name__ == '__main__':
    unittest.main()
