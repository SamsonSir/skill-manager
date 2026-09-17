import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'

class Gates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def run_gate(self, script, expected, **kwargs):
        command = [sys.executable, str(SCRIPTS / script)]
        for key, value in kwargs.items():
            command += ['--' + key.replace('_', '-'), str(value)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, expected, result.stdout + result.stderr)
        self.assertNotIn('Traceback', result.stderr)
    def test_cover_decode(self):
        image = self.root / 'cover.png'
        Image.new('RGB', (30, 20)).save(image)
        self.run_gate('check_cover_dimensions.py', True, image=image, width=30, height=20)
        self.run_gate('check_cover_dimensions.py', False, image=image, width=31, height=20)
        image.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\0'*8 + struct.pack('>II', 30, 20))
        self.run_gate('check_cover_dimensions.py', False, image=image, width=30, height=20)
    def test_layout(self):
        article = self.root / 'article.md'; preview = self.root / 'preview.html'
        article.write_text('# 标题\n\n你好**世界**。\n')
        valid = '<section id="article"><h1>标题</h1><p>你好<strong>世界</strong>。</p><img src="a.png"></section><button>复制</button>'
        preview.write_text(valid)
        self.run_gate('validate_layout.py', True, article=article, preview=preview)
        for changed in [valid.replace('</p>', '广告</p>'), valid.replace('<h1>标题</h1>', ''), valid.replace('</p>', '</p><button>复制</button>'), valid.replace('</section>', '')]:
            preview.write_text(changed)
            self.run_gate('validate_layout.py', False, article=article, preview=preview)
    def test_identity(self):
        root = self.root / 'account'; root.mkdir()
        image = root / 'face.png'; image.write_bytes(b'fixture')
        manifest = root / 'identity.json'
        data = dict(account_id='a', character_id='person', version=1, status='confirmed', references=[dict(role='primary_identity', path='face.png', sha256=hashlib.sha256(image.read_bytes()).hexdigest())])
        manifest.write_text(json.dumps(data))
        kw = dict(manifest=manifest, account_id='a', character_id='person', account_root=root)
        self.run_gate('check_identity.py', True, **kw)
        self.run_gate('check_identity.py', False, **dict(kw, character_id='other'))
        outside = self.root / 'other.png'; outside.write_bytes(image.read_bytes())
        image.unlink(); image.symlink_to(outside)
        self.run_gate('check_identity.py', False, **kw)
    def test_packet(self):
        article = self.root / 'article.txt'; claims = self.root / 'claims.json'; style = self.root / 'style.json'
        article.write_text('平静也是一种选择。\n你曾经遇到这种情况吗？\n')
        packet = dict(schema_version=1, account_id='a', character_id='p', article=article.name, article_sha256=hashlib.sha256(article.read_bytes()).hexdigest(), fact_policy='source_bound', claims=[], interaction_lines=[2], semantic_review=dict(reviewed_from_final_article=True, result='pass'))
        review = dict(schema_version=1, account_id='a', character_id='p', article=article.name, article_sha256=packet['article_sha256'], contract_ref='contract', anchors_read=['anchor'], reviewed_from_final_article=True, overall='pass', dimensions={name:dict(result='pass', article_evidence='平静', anchor_basis='anchor') for name in ('stance','speaking_position','concreteness','rhythm','ending','recent_structure')})
        (self.root / 'contract').write_text('角色合同')
        (self.root / 'anchor').write_text('认可样文')
        def check(p, r, expected):
            claims.write_text(json.dumps(p)); style.write_text(json.dumps(r))
            self.run_gate('validate_article_packet.py', expected, article=article, claims=claims, style=style)
        check(packet, review, True)
        check(None, review, False); check(packet, None, False)
        check(dict(packet, fact_policy='anything'), review, False)
        check(dict(packet, account_id=None), dict(review, account_id=None), False)
        check(dict(packet, claims=[None]), review, False)
        check(dict(packet, article_sha256='old'), review, False)
        risk = dict(line_start=1, line_end=1, claim='经历', type='experience', source_type='project_fact', source_ref='missing.txt')
        check(dict(packet, claims=[risk]), review, False)
        (self.root/'source.txt').write_text('经历来源')
        risk['source_ref']='source.txt'
        check(dict(packet, claims=[risk]), review, True)
        article.write_text('# 只有标题\n')
        digest=hashlib.sha256(article.read_bytes()).hexdigest()
        check(dict(packet, article_sha256=digest, interaction_lines=[]), dict(review, article_sha256=digest), False)

if __name__ == '__main__':
    unittest.main()
