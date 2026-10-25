import argparse
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import search as s

class SearchTests(unittest.TestCase):
 def test_boundaries(self):
  self.assertIsNotNone(s.term_pattern('Twitter').search('TWITTER 热点'))
  self.assertIsNone(s.term_pattern('x.com').search('https://fcbox.com'))
  self.assertIsNotNone(s.term_pattern('x.com').search('https://x.com/user'))
  self.assertIsNone(s.term_pattern('X').search('xlsx'))
 def test_card_and_credentials(self):
  raw='<appmsg><title><![CDATA[Twitter热点]]></title><des>工具</des><url><![CDATA[https://example.com/?a=1&b=2]]></url><appattach><aeskey>SECRET</aeskey></appattach><type>5</type></appmsg>'
  text=s.readable(raw)
  self.assertNotIn('SECRET',text)
  self.assertEqual(s.urls(text),['https://example.com/?a=1&b=2'])
 def test_malformed_card_does_not_export_media_token(self):
  text=s.readable('<appmsg><title>Twitter</title><url>https://example.com</url><appattach/><finderFeed><url>https://media.invalid/?token=SECRET</url></finderFeed><broken></appmsg>')
  self.assertNotIn('SECRET',text)
  self.assertIn('https://example.com',text)
 def test_scope_dates_dedup_and_repeat(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);db=root/'db.sqlite'
   with sqlite3.connect(db) as c:
    c.execute('CREATE TABLE messages(source_db TEXT,source_table TEXT,local_id INT,server_id INT,chat_username TEXT,chat_name TEXT,sender_name TEXT,create_time INT,decoded_content TEXT)')
    for i,gid,ts,text in [(1,'group@chatroom',1788537100,'Twitter 热点 https://example.com'),(2,'group@chatroom',1788537100,'Twitter 热点 https://example.com'),(3,'person',1788537200,'推特 网站 https://example.org')]:
     c.execute('INSERT INTO messages VALUES(?,?,?,?,?,?,?,?,?)',('db','table',i,1 if i<3 else 2,gid,'Chat','Member',ts,text))
   a=argparse.Namespace(keyword=['Twitter','推特'],require=['热点','网站'],scope='all',chat_id=None,db=str(db),from_date=None,to_date=None,limit=0,max_chars=200,output=str(root/'out'))
   result=s.run(a);self.assertEqual(result['total_matches'],2)
   p=Path(result['output']);before=p.read_bytes();s.run(a);self.assertEqual(before,p.read_bytes())
   a.chat_id='group@chatroom';a.scope='watched';self.assertEqual(s.run(a)['total_matches'],1)
   a.from_date='2026-10-01';self.assertEqual(s.run(a)['total_matches'],0)
   a.from_date=None;a.chat_id=None;a.scope='all';a.limit=1
   r=s.run(a);self.assertTrue(r['limited']);self.assertEqual(r['returned'],1)
if __name__=='__main__':unittest.main()
