"""Synthetic tests: no real chats, keys or network required."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import attachments as a


def card(name, data, md5=True):
    return (f'<msg><appmsg><title>{name}</title><type>6</type><appattach>'
            f'<fileext>{Path(name).suffix[1:]}</fileext><totallen>{len(data)}</totallen>'
            '<aeskey>DO_NOT_EXPORT</aeskey></appattach>'
            f'<md5>{hashlib.md5(data).hexdigest() if md5 else ""}</md5></appmsg></msg>')


class AttachmentTests(unittest.TestCase):
    def test_reference_not_attachment_and_malformed(self):
        xml = '<appmsg><title>reply</title><type>57</type><refermsg>' + card('x.pdf', b'x') + '</refermsg></appmsg>'
        self.assertIsNone(a.parse_file(xml))
        with self.assertRaises(ValueError):
            a.parse_file('<appmsg><type>6</type>')
        self.assertNotIn('aeskey', a.parse_file(card('x.pdf', b'x')))

    def test_md5_wins_over_name_and_missing(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / 'lesson.pdf').write_bytes(b'wrong')
            (root / 'different(1).pdf').write_bytes(b'right')
            sizes, names, _ = a.index_files(root)
            info = a.parse_file(card('lesson.pdf', b'right'))
            result, method = a.find_file(info, sizes, names, {})
            self.assertEqual(result.name, 'different(1).pdf')
            self.assertEqual(method, 'md5_verified')
            info['expected_md5'] = '0' * 32
            self.assertEqual(a.find_file(info, sizes, names, {})[1], 'not_found_locally')

    def test_ambiguous_names_and_symlinks(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / 'a.pdf').write_bytes(b'aaa')
            (root / 'a(1).pdf').write_bytes(b'bbb')
            (root / 'link.pdf').symlink_to(root / 'a.pdf')
            sizes, names, _ = a.index_files(root)
            self.assertEqual(sum(map(len, sizes.values())), 2)
            self.assertEqual(a.find_file(a.parse_file(card('a.pdf', b'aaa', False)), sizes, names, {})[1], 'ambiguous')
            with self.assertRaises(ValueError):
                a.copy_verified(root / 'a.pdf', root / 'link.pdf', a.digest(root / 'a.pdf'))

    def test_office_format_and_safe_filename(self):
        with tempfile.TemporaryDirectory() as t:
            for ext, member in [('docx', 'word/document.xml'), ('xlsx', 'xl/workbook.xml')]:
                p = Path(t) / ('test.' + ext)
                with zipfile.ZipFile(p, 'w') as z:
                    z.writestr(member, '<test/>')
                self.assertTrue(a.format_ok(p, ext))
            p.write_bytes(b'<html>not an office file</html>')
            self.assertFalse(a.format_ok(p, 'xlsx'))
            self.assertNotIn('/', a.safe_name('../../bad.pdf'))

    def test_repeat_dedup_retry_and_private_rejection(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); files = root / 'source'; files.mkdir()
            data = b'%PDF-1.7\nfixture'
            db = root / 'db.sqlite'
            with sqlite3.connect(db) as c:
                c.execute('CREATE TABLE messages (source_db TEXT,source_table TEXT,local_id INT,server_id INT,chat_username TEXT,chat_name TEXT,sender_name TEXT,create_time INT,sort_seq INT,decoded_content TEXT)')
                for i in range(2):
                    c.execute('INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?)', ('msg.db', 'Msg_1', i, i+1, 'test@chatroom', 'Test', 'Member', 1788537100+i, i, card('lesson.pdf', data)))
            args = argparse.Namespace(db=str(db), name=None, chat_id='test@chatroom', from_date=None, to_date=None, types='pdf', file_root=str(files), output=str(root / 'out'))
            self.assertEqual(a.run(args)['statuses'], {'not_found_locally': 2})
            (files / 'lesson(1).pdf').write_bytes(data)
            result = a.run(args)
            self.assertEqual(result['new_copies'], 1)
            self.assertEqual(result['unique_exported_files'], 1)
            manifest = Path(result['manifest']); before = manifest.read_bytes()
            self.assertEqual(a.run(args)['new_copies'], 0)
            self.assertEqual(manifest.read_bytes(), before)
            self.assertNotIn(b'DO_NOT_EXPORT', before)
            args.chat_id = 'private-person'
            with self.assertRaises(ValueError):
                a.run(args)

if __name__ == '__main__':
    unittest.main()
