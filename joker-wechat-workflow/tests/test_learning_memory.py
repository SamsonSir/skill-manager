"""Behavioral checks use two disposable accounts, never live account records."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'learning_memory.py'
spec = importlib.util.spec_from_file_location('learning_memory', SCRIPT)
lm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lm)


class LearningMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        # macOS /var is a symlink; choose the canonical fixture root.
        self.root = Path(self.temp.name).resolve()
        (self.root / '00-矩阵管理').mkdir()
        accounts = []
        for aid in ['a', 'b']:
            path = self.root / 'accounts' / aid
            path.mkdir(parents=True)
            (path / 'feedback.md').write_text('用户原话：不要重复观点。\n用户确认：这篇可作样文。\n撤销这条。', encoding='utf-8')
            (path / 'article.md').write_text(f'{aid} 的私人经历，仅在本账号使用。', encoding='utf-8')
            accounts.append({'account_id': aid, 'root': f'accounts/{aid}'})
        (self.root / '00-矩阵管理/账号目录.json').write_text(json.dumps({'default_account': 'a', 'accounts': accounts}))
        self.a = lm.LearningMemory(str(self.root), 'a')
        self.b = lm.LearningMemory(str(self.root), 'b')

    def tearDown(self):
        self.temp.cleanup()

    def feedback(self, **changes):
        return dict({'id': 'no-repeat', 'rule': '每段推进观点', 'scope': 'account',
                     'origin': 'user_feedback', 'evidence': {'path': 'feedback.md', 'quote': '不要重复观点。'}}, **changes)

    def exemplar(self, **changes):
        return dict({'id': 'sample', 'path': 'article.md', 'kind': 'candidate', 'ownership': 'user',
                     'allowed_uses': ['style'], 'evidence': {'path': 'feedback.md', 'quote': '这篇可作样文。'}}, **changes)

    def test_empty_read_has_no_side_effect(self):
        self.assertEqual(self.a.context('article')['confirmed_rules'], [])
        self.assertFalse(self.a.path.parent.exists())

    def test_single_or_repeated_feedback_is_candidate(self):
        for _ in range(3):
            self.a.put('feedback', self.feedback())
        context = self.a.context('article')
        self.assertEqual(context['confirmed_rules'], [])
        self.assertEqual(len(context['candidate_rules']), 1)
        self.assertEqual(context['candidate_rules'][0]['version'], 3)

    def test_accounts_are_isolated(self):
        self.a.put('feedback', self.feedback(status='confirmed'))
        self.assertEqual(len(self.a.context('article')['confirmed_rules']), 1)
        self.assertEqual(self.b.context('article')['confirmed_rules'], [])
        self.assertFalse(self.b.path.exists())

    def test_confirmed_requires_user_origin_and_verbatim_evidence(self):
        with self.assertRaises(lm.MemoryError):
            self.a.put('feedback', self.feedback(status='confirmed', origin='agent_inference'))
        with self.assertRaises(lm.MemoryError):
            self.a.put('feedback', self.feedback(status='confirmed', evidence={'path': 'feedback.md', 'quote': '虚构反馈'}))

    def test_update_never_inherits_confirmation(self):
        self.a.put('feedback', self.feedback(status='confirmed'))
        self.a.put('feedback', self.feedback(rule='新写法待验证'))
        context = self.a.context('article')
        self.assertEqual(context['confirmed_rules'], [])
        self.assertEqual(context['candidate_rules'][0]['rule'], '新写法待验证')
        history = self.a.load()['records']['feedback']
        self.assertEqual([r['status'] for r in history], ['confirmed', 'candidate'])

    def test_changed_rule_cannot_reuse_old_confirmation(self):
        self.a.put('feedback', self.feedback(status='confirmed'))
        changed = self.feedback(status='confirmed', rule='不同规则必须重新认可')
        with self.assertRaisesRegex(lm.MemoryError, 'new confirmation evidence'):
            self.a.put('feedback', changed)
        self.assertEqual(len(self.a.load()['records']['feedback']), 1)
        # Re-recording the same meaning/evidence is harmless.
        self.a.put('feedback', self.feedback(status='confirmed'))

    def test_candidate_and_revocation_cannot_transfer_confirmation(self):
        self.a.put('feedback', self.feedback(status='confirmed'))
        self.a.put('feedback', self.feedback(rule='尚未认可的新规则'))
        with self.assertRaises(lm.MemoryError):
            self.a.put('feedback', self.feedback(rule='尚未认可的新规则', status='confirmed'))
        self.a.revoke('feedback', 'no-repeat', '撤销', {'path': 'feedback.md', 'quote': '撤销这条。'})
        with self.assertRaises(lm.MemoryError):
            self.a.put('feedback', self.feedback(rule='撤销后换个意思', status='confirmed'))
        self.assertEqual(self.a.context('article')['confirmed_rules'], [])

    def test_changed_rule_with_new_explicit_evidence_is_allowed(self):
        self.a.put('feedback', self.feedback(status='confirmed'))
        (self.a.root / 'new-confirmation.md').write_text('用户确认：这条新规则采用。', encoding='utf-8')
        self.a.put('feedback', self.feedback(rule='经过重新认可的新规则', status='confirmed',
                    evidence={'path': 'new-confirmation.md', 'quote': '这条新规则采用。'}))
        self.assertEqual(self.a.context('article')['confirmed_rules'][0]['rule'], '经过重新认可的新规则')

    def test_changed_approved_exemplar_needs_new_confirmation(self):
        self.a.put('exemplar', self.exemplar(kind='approved', status='confirmed'))
        (self.a.root / 'other.md').write_text('另一篇稿件', encoding='utf-8')
        changed = self.exemplar(path='other.md', kind='approved', status='confirmed')
        with self.assertRaises(lm.MemoryError):
            self.a.put('exemplar', changed)
        self.a.put('exemplar', self.exemplar(path='other.md'))
        with self.assertRaises(lm.MemoryError):
            self.a.put('exemplar', changed)
        # Even the original path needs renewed evidence after its content changes.
        (self.a.root / 'article.md').write_text('原路径上的新稿件', encoding='utf-8')
        with self.assertRaises(lm.MemoryError):
            self.a.put('exemplar', self.exemplar(kind='approved', status='confirmed'))
        (self.a.root / 'new-confirmation.md').write_text('用户确认：另一篇可作为样文。', encoding='utf-8')
        changed['evidence'] = {'path': 'new-confirmation.md', 'quote': '另一篇可作为样文。'}
        self.a.put('exemplar', changed)
        self.assertEqual(self.a.context('article')['exemplars'][0]['path'], 'other.md')

    def test_content_type_scope(self):
        self.a.put('feedback', self.feedback(scope='content_type', content_type='article'))
        self.assertEqual(len(self.a.context('article')['candidate_rules']), 1)
        self.assertEqual(self.a.context('card')['candidate_rules'], [])

    def test_revoke_and_explicit_new_revision(self):
        self.a.put('feedback', self.feedback(status='confirmed'))
        evidence = {'path': 'feedback.md', 'quote': '撤销这条。'}
        self.a.revoke('feedback', 'no-repeat', '用户撤回', evidence)
        self.assertEqual(self.a.context('article')['confirmed_rules'], [])
        self.assertEqual(self.a.context('article')['candidate_rules'], [])
        with self.assertRaises(lm.MemoryError):
            self.a.revoke('feedback', 'unknown', '撤销', evidence)
        with self.assertRaises(lm.MemoryError):
            self.a.revoke('feedback', 'no-repeat', '重复撤销', evidence)
        self.a.put('feedback', self.feedback())
        self.assertEqual(self.a.context('article')['candidate_rules'][0]['version'], 3)

    def test_changed_evidence_excludes_record_with_warning(self):
        self.a.put('feedback', self.feedback(status='confirmed'))
        with (self.a.root / 'feedback.md').open('a') as out:
            out.write('\n来源发生变化')
        context = self.a.context('article')
        self.assertEqual(context['confirmed_rules'], [])
        self.assertEqual(context['warnings'][0]['id'], 'no-repeat')

    def test_changed_exemplar_excludes_record(self):
        self.a.put('exemplar', self.exemplar(kind='approved', status='confirmed'))
        (self.a.root / 'article.md').write_text('改稿尚未重新认可')
        context = self.a.context('article')
        self.assertEqual(context['exemplars'], [])
        self.assertTrue(context['warnings'])

    def test_approved_and_benchmark_are_distinct_and_no_fulltext(self):
        with self.assertRaises(lm.MemoryError):
            self.a.put('exemplar', self.exemplar(kind='approved'))
        self.a.put('exemplar', self.exemplar(kind='approved', status='confirmed'))
        self.a.put('exemplar', self.exemplar(id='benchmark', kind='benchmark', ownership='third_party', allowed_uses=['structure']))
        output = self.a.context('article')
        self.assertEqual([e['kind'] for e in output['exemplars']], ['approved', 'benchmark'])
        self.assertNotIn('私人经历', json.dumps(output, ensure_ascii=False))
        self.assertTrue(all(e['personal_materials_reusable'] is False for e in output['exemplars']))
        with self.assertRaises(lm.MemoryError):
            self.a.put('exemplar', self.exemplar(allowed_uses=['copy_personal_history']))

    def test_cross_account_and_traversal_rejected(self):
        for path in [str(self.b.root / 'article.md'), '../b/article.md']:
            with self.subTest(path=path), self.assertRaises(lm.MemoryError):
                self.a.put('exemplar', self.exemplar(path=path))

    def test_source_and_store_symlinks_rejected(self):
        (self.a.root / 'linked.md').symlink_to(self.b.root / 'article.md')
        with self.assertRaises(lm.MemoryError):
            self.a.put('exemplar', self.exemplar(path='linked.md'))
        self.a.path.parent.symlink_to(self.b.root, target_is_directory=True)
        with self.assertRaises(lm.MemoryError):
            self.a.context('article')

    def test_wrong_store_account_fails_closed(self):
        self.a.put('feedback', self.feedback())
        self.b.path.parent.mkdir()
        self.b.path.write_bytes(self.a.path.read_bytes())
        with self.assertRaises(lm.MemoryError):
            self.b.context('article')
        with self.assertRaises(lm.MemoryError):
            self.b.put('feedback', self.feedback())

    def test_missing_account_and_overlapping_root_rejected(self):
        with self.assertRaises(lm.MemoryError):
            lm.LearningMemory(str(self.root), '')
        with self.assertRaises(lm.MemoryError):
            lm.LearningMemory(str(self.root), 'unknown')
        index = self.root / '00-矩阵管理/账号目录.json'
        value = json.loads(index.read_text())
        value['accounts'][1]['root'] = 'accounts'
        index.write_text(json.dumps(value))
        with self.assertRaises(lm.MemoryError):
            lm.LearningMemory(str(self.root), 'a')

    def test_credentials_are_not_sources(self):
        (self.a.root / 'credentials.json').write_text('{"secret": "fixture-only"}')
        with self.assertRaises(lm.MemoryError):
            self.a.put('exemplar', self.exemplar(path='credentials.json'))

    def test_limit_is_explicit_about_omitted_records(self):
        for i in range(7):
            self.a.put('feedback', self.feedback(id=f'rule-{i}', status='confirmed'))
        result = self.a.context('article')
        self.assertEqual(len(result['confirmed_rules']), 5)
        self.assertEqual(result['total_counts']['confirmed_rules'], 7)
        self.assertTrue(result['truncated']['confirmed_rules'])
        self.assertFalse(self.a.context('article', limit=10)['truncated']['confirmed_rules'])

    def test_corrupt_metadata_fails_closed(self):
        self.a.put('feedback', self.feedback())
        original = self.a.path.read_text()
        for field, value in [('status', 'published'), ('origin', 'unknown'), ('scope', 'shared')]:
            with self.subTest(field=field):
                data = json.loads(original)
                data['records']['feedback'][0][field] = value
                self.a.path.write_text(json.dumps(data))
                with self.assertRaises(lm.MemoryError):
                    self.a.context('article')
        self.a.path.write_text(original)
        self.a.put('exemplar', self.exemplar(kind='approved', status='confirmed'))
        original = self.a.path.read_text()
        for field, value in [('status', 'candidate'), ('personal_materials_reusable', True), ('allowed_uses', ['personal_history'])]:
            with self.subTest(field=field):
                data = json.loads(original)
                data['records']['exemplar'][0][field] = value
                self.a.path.write_text(json.dumps(data))
                with self.assertRaises(lm.MemoryError):
                    self.a.context('article')

    def test_cli_end_to_end_and_negative_inputs(self):
        base = [sys.executable, str(SCRIPT), '--matrix-root', str(self.root), '--account-id', 'a']
        source = self.root / 'input.json'
        source.write_text(json.dumps(self.feedback(status='confirmed')))
        put = subprocess.run(base + ['put-feedback', '--input', str(source)], text=True, capture_output=True)
        self.assertEqual(put.returncode, 0, put.stderr)
        read = subprocess.run(base + ['context', '--content-type', 'article'], text=True, capture_output=True)
        self.assertEqual(len(json.loads(read.stdout)['confirmed_rules']), 1)
        invalid = subprocess.run(base + ['context', '--content-type', 'article', '--limit', '0'], text=True, capture_output=True)
        self.assertEqual(invalid.returncode, 2)
        missing = subprocess.run([sys.executable, str(SCRIPT), '--matrix-root', str(self.root), 'describe'], text=True, capture_output=True)
        self.assertEqual(missing.returncode, 2)
        source.write_text('not JSON')
        bad_json = subprocess.run(base + ['put-feedback', '--input', str(source)], text=True, capture_output=True)
        self.assertEqual(bad_json.returncode, 2)


if __name__ == '__main__':
    unittest.main()
