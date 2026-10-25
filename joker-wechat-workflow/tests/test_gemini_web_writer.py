import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import sys
spec=importlib.util.spec_from_file_location('gemini_web_writer',Path(__file__).parents[1]/'scripts/gemini_web_writer.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
class WriterTests(unittest.TestCase):
 def request(self):
  inner=[None]*81;inner[79]=1;inner[80]=1
  header=[None]*17;header[4]=w.MODEL_ID;header[14]=1;header[15]=1;header[16]='session-placeholder'
  return {'data':{'at':'private-token','f.req':json.dumps([None,json.dumps(inner)])},'headers':{w.HEADER:json.dumps(header),'other':'preserve'}}
 def test_medium_rewrites_only_two_fields(self):
  req=self.request();before=json.loads(json.loads(req['data']['f.req'])[1]);out=w.medium_request(req);after=json.loads(json.loads(out['data']['f.req'])[1]);self.assertEqual([i for i in range(81) if before[i]!=after[i]],[80]);self.assertEqual(after[80],4);self.assertEqual(json.loads(out['headers'][w.HEADER])[15],4);self.assertEqual(out['data']['at'],'private-token');self.assertEqual(json.loads(json.loads(req['data']['f.req'])[1])[80],1)
 def test_changed_model_fails_closed(self):
  req=self.request();h=json.loads(req['headers'][w.HEADER]);h[4]='another-model';req['headers'][w.HEADER]=json.dumps(h)
  with self.assertRaisesRegex(ValueError,'contract_changed'):w.medium_request(req)
 def test_isolation_and_symlink_escape(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'00-矩阵管理').mkdir();(p/'a').mkdir();(p/'b').mkdir();(p/'00-矩阵管理/账号目录.json').write_text(json.dumps({'accounts':[{'account_id':'A','root':'a'},{'account_id':'B','root':'b'}]}));f=p/'a/input.json';f.write_text(json.dumps({'account_id':'A','stage':'body','prompt':'write'}))
   w.scoped_paths(p,'A',f,p/'a/out.md')
   with self.assertRaises(ValueError):w.scoped_paths(p,'A',f,p/'b/out.md')
   (p/'a/escape').symlink_to(p/'b',target_is_directory=True)
   with self.assertRaises(ValueError):w.scoped_paths(p,'A',f,p/'a/escape/out.md')
 def test_quota_fallback_keeps_existing_output(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);out=p/'approved.md';out.write_text('approved content')
   async def fail(*args):raise RuntimeError('429 quota exhausted')
   with patch.object(w,'scoped_paths',return_value=(p,out,{'prompt':'draft','stage':'body'})),patch.object(w,'read_auth',return_value={}),patch.object(w,'generate',side_effect=fail),patch.object(sys,'argv',['writer','--matrix-root',t,'--account-id','A','--input','x','--output',str(out),'--auth-file','x']):
    self.assertEqual(w.main(),2)
   self.assertEqual(out.read_text(),'approved content')
if __name__=='__main__':unittest.main()
