import argparse
import html
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from account_cards import extract_cards
import benchmarks
import search


class AccountCardTests(unittest.TestCase):
    def test_public_card_malformed_ampersand_and_no_tickets(self):
        raw = 'sender:\n<msg nickname="写真情报局" certflag="8" username="v3_SECRET@stranger" certinfo="A & B" alias="" antispamticket="TICKET" biznamecardinfo="PAYLOAD" />'
        cards = extract_cards(raw)
        self.assertEqual(cards[0]['account_name'], '写真情报局')
        self.assertEqual(cards[0]['description'], 'A & B')
        self.assertIsNone(cards[0]['account_id'])
        encoded = json.dumps(cards)
        for secret in ('SECRET', 'TICKET', 'PAYLOAD'):
            self.assertNotIn(secret, encoded)
        self.assertIn('写真情报局', search.readable(raw))

    def test_private_and_image_not_exported(self):
        self.assertEqual(extract_cards('<msg nickname="私人好友" username="wxid_person" certflag="0"/>'), [])
        self.assertEqual(search.readable('sender:\n<msg><img aeskey="SECRET" cdnurl="PRIVATE"/></msg>'), '')
        quote = html.escape('<msg><img aeskey="SECRET"/><aeskey>SECOND_SECRET</aeskey></msg>')
        text = search.readable('<appmsg><type>57</type><title>看看</title><refermsg><content>' + quote + '</content></refermsg></appmsg>')
        self.assertNotIn('SECRET', text)

    def test_quote_and_forward_card_and_article(self):
        card = '<msg nickname="对标" certflag="8" username="gh_public" certinfo="简介"/>'
        quote = '<appmsg><type>57</type><title>看看</title><refermsg><content>' + html.escape(card) + '</content></refermsg></appmsg>'
        got = extract_cards(quote)
        self.assertTrue(any(c['account_id'] == 'gh_public' for c in got))
        self.assertTrue(all(c['context'] == 'quoted' for c in got))
        record = '<recordinfo><datalist><dataitem><datadesc>' + html.escape(card) + '</datadesc></dataitem><dataitem><weburlitem><title>文章</title><link>https://mp.weixin.qq.com/s?__biz=ABC&amp;mid=1&amp;idx=2&amp;sn=HASH</link></weburlitem><cdndatakey>SECRET</cdndatakey></dataitem></datalist></recordinfo>'
        forwarded = '<appmsg><type>19</type><recorditem><![CDATA[' + record + ']]></recorditem></appmsg>'
        got = extract_cards(forwarded)
        self.assertTrue(any(c['account_name'] == '对标' for c in got))
        article = next(c for c in got if c['kind'] == 'official_article_card')
        self.assertEqual(article['biz'], 'ABC')
        self.assertIn('idx=2&sn=HASH', article['original_url'])
        self.assertNotIn('SECRET', json.dumps(got))

    def test_article_source_and_media_exclusion(self):
        raw = '<appmsg><type>5</type><title>正文</title><url>https://mp.weixin.qq.com/s/abc</url><sourcedisplayname>公众号</sourcedisplayname><sourceusername>gh_public</sourceusername><appattach><aeskey>SECRET</aeskey><url>https://media.invalid/SECRET</url></appattach></appmsg>'
        got = extract_cards(raw)
        self.assertEqual(got[0]['account_name'], '公众号')
        self.assertEqual(got[0]['account_id'], 'gh_public')
        self.assertNotIn('SECRET', json.dumps(got))

    def test_image_card_metadata_not_visual_claim(self):
        raw = '<appmsg><type>5</type><title>图组</title><url>https://mp.weixin.qq.com/s/abc</url><mmreadershare><itemshowtype>8</itemshowtype><piccount>4</piccount><coverpicimageurl>https://mmbiz.qpic.cn/mmbiz_jpg/abc/0?wx_fmt=jpeg</coverpicimageurl><coverpicwidth>1200</coverpicwidth></mmreadershare></appmsg>'
        got = extract_cards(raw)[0]
        self.assertEqual(got['message_format'], 'image')
        self.assertEqual(got['picture_count'], 4)
        self.assertEqual(got['cover_width'], 1200)
        self.assertTrue(got['cover_url'].startswith('https://mmbiz.qpic.cn'))
        raw = raw.replace('wx_fmt=jpeg', 'token=SECRET')
        self.assertIsNone(extract_cards(raw)[0]['cover_url'])

    def test_scope_repeat_dedup_and_readonly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); db = root / 'db.sqlite'
            with sqlite3.connect(db) as c:
                c.execute('CREATE TABLE messages(source_db TEXT,source_table TEXT,local_id INT,server_id INT,chat_username TEXT,chat_name TEXT,create_time INT,decoded_content TEXT)')
                for i, chat in [(1, 'target@chatroom'), (2, 'target@chatroom'), (3, 'other')]:
                    c.execute('INSERT INTO messages VALUES(?,?,?,?,?,?,?,?)', ('db','table',i,11 if i < 3 else 12,chat,'群',1790900000,'<msg nickname="账号" certflag="8"/>'))
            before = db.read_bytes()
            args = argparse.Namespace(chat_id='target@chatroom',db=str(db),from_date=None,to_date=None,output=str(root/'out'))
            result = benchmarks.run(args)
            self.assertEqual(result['extracted_records'], 1)
            file = Path(result['output']); contents = file.read_bytes()
            benchmarks.run(args)
            self.assertEqual(file.read_bytes(), contents)
            self.assertEqual(db.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
