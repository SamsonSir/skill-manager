import json
from pathlib import Path
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from content_state import update

class StateTests(unittest.TestCase):
    def test_resume_and_unknown_does_not_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); article=root/'body'; article.write_text('approved')
            state=root/'state.json'
            update(state,'init','a','p','POST-1',article)
            def begin():
                try: return update(state,'begin','a','p','POST-1')
                except ValueError: return None
            with ThreadPoolExecutor(2) as pool: results=list(pool.map(lambda _:begin(),range(2)))
            self.assertEqual(sum(x is not None for x in results),1)
            self.assertIsNone(begin()) # response lost; next session must reconcile
            s=json.loads(state.read_text()); self.assertEqual(len(s['attempts']),1)
            proof=root/'proof'; proof.write_text(json.dumps(dict(account_id='a',character_id='p',content_id='POST-1',attempt_id=s['attempt_id'],draft_id='remote-1',article_sha256=s['article_sha256'])))
            update(state,'saved','a','p','POST-1',draft_id='remote-1',attempt_id=s['attempt_id'],evidence=proof)
            with self.assertRaises(ValueError): update(state,'verified','a','p','POST-1',attempt_id=s['attempt_id'],evidence=proof)
            proof.write_text(json.dumps(dict(account_id='a',character_id='p',content_id='POST-1',draft_id='remote-1',article_sha256=s['article_sha256'],text_matches=True,images_match=True,layout_reviewed=True)))
            self.assertEqual(update(state,'verified','a','p','POST-1',attempt_id=s['attempt_id'],evidence=proof)['save_status'],'verified')
            other=root/'second'; update(other,'init','a','p','POST-2',article)
            self.assertEqual(json.loads(other.read_text())['save_status'],'not_requested')
            with self.assertRaises(ValueError): update(other,'begin','wrong','p','POST-2')
            article.write_text('changed')
            with self.assertRaises(ValueError): update(other,'begin','a','p','POST-2')
    def test_no_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'body').write_text('text')
            update(p/'state','init','a','p','1',p/'body',allow_save=False)
            with self.assertRaises(ValueError): update(p/'state','begin','a','p','1')

if __name__=='__main__': unittest.main()
