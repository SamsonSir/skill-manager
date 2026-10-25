import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'check_account_readiness.py'
spec = importlib.util.spec_from_file_location('readiness', SCRIPT)
readiness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readiness)


class AccountReadiness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.config = self.root / 'config.json'
        self.contract = self.root / 'contract.yaml'
        self.contract.write_text('account_id: a\ncharacter_id: observer\nstatus: confirmed\nfact_policy: source_bound\nsample_voice_approval: pending\n')
        for name in ('voice.md', 'layout.html', 'visual.md'):
            (self.root / name).write_text('fixture')
        self.cfg = dict(account_id='a', character_id='observer', project_root='.', contract='contract.yaml', voice_anchor='voice.md', layout_template='layout.html', visual_rules='visual.md', visual_mode='non_person_graphic', writing_mode='positioning_sample', image_backend=dict(mode='non_person_graphic', generation=True, provider='image_gen'))

    def tearDown(self):
        self.tmp.cleanup()

    def check(self):
        self.config.write_text(json.dumps(self.cfg))
        return readiness.check(self.config, 'a', 'observer')['stages']

    def test_graphic_sample_without_human_identity_or_backend_binding(self):
        stages = self.check()
        self.assertTrue(stages['images']['ready'])
        self.assertTrue(stages['writing']['ready'])
        self.assertTrue(stages['writing']['warnings'])
        self.assertFalse(stages['saving']['ready'])

    def test_graphic_requires_explicit_backend_and_rules(self):
        self.cfg['image_backend']['mode'] = 'photo'
        self.assertFalse(self.check()['images']['ready'])
        self.cfg['image_backend']['mode'] = 'non_person_graphic'
        self.cfg['visual_rules'] = '../outside.md'
        self.assertFalse(self.check()['images']['ready'])

    def test_contract_confirmation_and_account_isolation(self):
        self.contract.write_text(self.contract.read_text().replace('status: confirmed', 'status: pending'))
        self.assertFalse(self.check()['writing']['ready'])
        self.cfg['account_id'] = 'other'
        with self.assertRaises(ValueError):
            self.check()

    def test_legacy_fixed_person_retains_reference_requirements(self):
        self.cfg.pop('visual_mode')
        self.cfg['role_root'] = 'role'
        role = self.root / 'role'
        role.mkdir()
        face = role / 'face.png'
        face.write_bytes(b'fixture')
        manifest = role / 'identity.json'
        manifest.write_text(json.dumps(dict(account_id='a', character_id='observer', version=1, status='confirmed', references=[dict(role='primary_identity', path='face.png', sha256=hashlib.sha256(face.read_bytes()).hexdigest())])))
        self.cfg['identity'] = 'role/identity.json'
        self.cfg['image_backend'] = dict(reference_images=True, photorealistic=True)
        self.assertTrue(self.check()['images']['ready'])
        self.cfg['image_backend']['reference_images'] = False
        self.assertFalse(self.check()['images']['ready'])

    def test_unknown_visual_mode_fails_closed(self):
        self.cfg['visual_mode'] = 'anything'
        self.assertFalse(self.check()['images']['ready'])


if __name__ == '__main__':
    unittest.main()
