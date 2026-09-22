"""Offline integration: real state CLI + fake remote server, never a WeChat request."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_account_readiness import check
from visual_history import append
SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'

class Handoff(unittest.TestCase):
    def test_cli_lost_response_two_posts_and_immutable_assets(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);body=r/'body';body.write_text('已批准正文');layout=r/'article.html';layout.write_text('<p>已批准正文</p>')
            remote=[]
            def cli(action,content='POST-1',extra=(),ok=True):
                result=subprocess.run([sys.executable,str(SCRIPTS/'content_state.py'),action,'--state',str(r/content),'--account-id','a','--character-id','p','--content-id',content,*extra],capture_output=True,text=True)
                self.assertEqual(result.returncode==0,ok,result.stderr)
                return json.loads(result.stdout) if ok else None
            cli('init',extra=['--article',str(body),'--artifact',str(layout)])
            attempt=cli('begin')
            remote.append({'id':'remote-1','body':body.read_text()}) # server accepted, response lost
            cli('begin',ok=False) # fresh process cannot blindly retry
            self.assertEqual(len(remote),1)
            receipt=r/'receipt.json';receipt.write_text(json.dumps(dict(account_id='a',character_id='p',content_id='POST-1',draft_id='remote-1',attempt_id=attempt['attempt_id'],article_sha256=attempt['article_sha256'])))
            cli('saved',extra=['--attempt-id',attempt['attempt_id'],'--draft-id','remote-1','--evidence',str(receipt)])
            cli('init',content='POST-2',extra=['--article',str(body),'--artifact',str(layout),'--no-save'])
            cli('begin',content='POST-2',ok=False)
            self.assertEqual(body.read_text(),'已批准正文')
            layout.write_text('<p>未批准的排版变更</p>')
            cli('begin',ok=False)
            self.assertEqual(len(remote),1)

    def test_new_role_staged_readiness(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);(r/'contract.yaml').write_text('account_id: wang\ncharacter_id: wangjie\nstatus: confirmed\nfact_policy: source_bound\n');(r/'voice').write_text('新角色已认可声音');(r/'layout').write_text('已定排版')
            cfg=dict(account_id='wang',character_id='wangjie',project_root='.',contract='contract.yaml',voice_anchor='voice',layout_template='layout',role_root='role',identity='role/identity.json')
            p=r/'config.json';p.write_text(json.dumps(cfg))
            result=check(p,'wang','wangjie')['stages']
            self.assertTrue(result['writing']['ready']);self.assertTrue(result['layout']['ready']);self.assertFalse(result['images']['ready']);self.assertFalse(result['saving']['ready'])
            with self.assertRaises(ValueError):check(p,'suqin','suqin')

    def test_visual_history_concurrency_and_role_isolation(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);asset=r/'image';asset.write_bytes(b'image fixture')
            entry=dict(account_id='a',character_id='p',content_id='POST-1',asset_path=str(asset),asset_sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),status='candidate',content_date=None,activity_id='unknown',scene_id='living',scene_version=1,outfit='yellow',accessories=[],camera='selfie',reason='history evaluated')
            def add(i):
                try:return append(r/'history',dict(entry,content_id=str(i)),0)
                except ValueError:return None
            with ThreadPoolExecutor(2) as pool:results=list(pool.map(add,[1,2]))
            self.assertEqual(sum(x is not None for x in results),1)
            history=json.loads((r/'history').read_text());self.assertEqual(len(history['entries']),1)
            with self.assertRaises(ValueError):append(r/'history',dict(entry,character_id='other'),1)
            with self.assertRaises(ValueError):append(r/'history',dict(entry,status='published'),1)
            append(r/'history',dict(entry,content_id='retry-replanned'),1)
            self.assertEqual(len(json.loads((r/'history').read_text())['entries']),2)
