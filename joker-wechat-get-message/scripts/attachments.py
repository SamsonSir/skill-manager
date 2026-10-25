#!/usr/bin/env python3
"""Export downloaded group file attachments from the existing read-only snapshot.
No network, keys, live database writes, deletions or publishing.
"""
from __future__ import annotations
import argparse
import collections
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET

from watchlist import ACCOUNT_ROOT, db_path, connect, load_watchlist, watchlist_path

FILE_ROOT = Path('/Users/joker/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/qq179369161_39db/msg/file')
OUT_ROOT = ACCOUNT_ROOT / '学习整理/Joker/群文件'
TZ = dt.timezone(dt.timedelta(hours=8))
DEFAULT_TYPES = 'pdf,doc,docx,xls,xlsx,ppt,pptx'


def digest(path: Path, algorithm='sha256') -> str:
    h = hashlib.new(algorithm)
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_name(name: str) -> str:
    name = re.sub(r'[\\/\x00-\x1f]', '_', name).strip(' .')
    return name[:160] or 'attachment'


def parse_file(text: str) -> dict | None:
    # Only the outer appmsg; referenced file messages are not new attachments.
    start = text.find('<appmsg')
    if start < 0:
        return None
    outer_type = re.search(r'<type>\s*(\d+)\s*</type>', text[start:])
    if outer_type and outer_type.group(1) != '6':
        return None
    end = text.find('</appmsg>', start)
    if end < 0:
        raise ValueError('malformed_xml')
    try:
        app = ET.fromstring(text[start:end + len('</appmsg>')])
    except ET.ParseError:
        raise ValueError('malformed_xml') from None
    if app.findtext('type') != '6':
        return None
    title = app.findtext('title') or ''
    ext = (app.findtext('appattach/fileext') or Path(title).suffix.lstrip('.')).lower().lstrip('.')
    size = app.findtext('appattach/totallen') or ''
    md5 = (app.findtext('md5') or app.findtext('appattach/md5') or '').lower()
    return {'file_name': title, 'extension': ext,
            'expected_size': int(size) if size.isdigit() and int(size) > 0 else None,
            'expected_md5': md5 if re.fullmatch(r'[0-9a-f]{32}', md5) else None}


def normalized_name(name: str) -> str:
    p = Path(name)
    stem = re.sub(r'\s*[（(]\d+[）)]$', '', p.stem)
    return unicodedata.normalize('NFC', stem + p.suffix).casefold()


def index_files(root: Path):
    by_size = collections.defaultdict(list)
    by_name = collections.defaultdict(list)
    errors = []
    if not root.is_dir() or root.is_symlink():
        return by_size, by_name, ['attachment_root_unavailable']
    def onerror(e):
        errors.append(str(e.filename))
    for folder, dirs, names in os.walk(root, followlinks=False, onerror=onerror):
        dirs[:] = [d for d in dirs if not (Path(folder) / d).is_symlink()]
        for name in names:
            path = Path(folder) / name
            if name.startswith('.') or path.is_symlink():
                continue
            try:
                if path.is_file():
                    by_size[path.stat().st_size].append(path)
                    by_name[normalized_name(name)].append(path)
            except OSError:
                errors.append(str(path))
    return by_size, by_name, errors


def find_file(info, by_size, by_name, cache):
    size, md5 = info['expected_size'], info['expected_md5']
    if md5:
        pool = by_size.get(size, []) if size else [p for paths in by_size.values() for p in paths]
        for path in sorted(pool):
            try:
                key = str(path), path.stat().st_size, path.stat().st_mtime_ns
                if key not in cache:
                    cache[key] = digest(path, 'md5')
                if cache[key] == md5:
                    return path, 'md5_verified'
            except OSError:
                continue
        return None, 'not_found_locally'
    pool = [p for p in by_name.get(normalized_name(info['file_name']), [])
            if size is not None and p.stat().st_size == size]
    if not pool:
        return None, 'insufficient_metadata' if size is None else 'not_found_locally'
    hashes = {digest(p) for p in pool}
    if len(hashes) > 1:
        return None, 'ambiguous'
    return sorted(pool)[0], 'name_size_match'


def format_ok(path: Path, ext: str) -> bool:
    with path.open('rb') as f:
        header = f.read(1024)
    if ext == 'pdf':
        return b'%PDF-' in header
    if ext in {'docx', 'xlsx', 'pptx'}:
        import zipfile
        member = {'docx': 'word/document.xml', 'xlsx': 'xl/workbook.xml', 'pptx': 'ppt/presentation.xml'}[ext]
        try:
            with zipfile.ZipFile(path) as z:
                return member in z.namelist()
        except zipfile.BadZipFile:
            return False
    if ext in {'doc', 'xls', 'ppt'}:
        return header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1')
    return True


def copy_verified(source: Path, destination: Path, sha: str, expected_md5=None) -> bool:
    if destination.is_symlink():
        raise ValueError('output_symlink_rejected')
    if destination.is_file() and digest(destination) == sha:
        return False
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = tempfile.mkstemp(dir=destination.parent, prefix='.copy-')
    try:
        with os.fdopen(fd, 'wb') as out, source.open('rb') as inp:
            for chunk in iter(lambda: inp.read(1024 * 1024), b''):
                out.write(chunk)
            out.flush()
            os.fsync(out.fileno())
        if digest(Path(tmp)) != sha or (expected_md5 and digest(Path(tmp), 'md5') != expected_md5):
            raise ValueError('source_changed_during_copy')
        os.replace(tmp, destination)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return True


def atomic_jsonl(path: Path, records):
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.manifest-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def resolve_group(con, name, group_id):
    if group_id:
        if not group_id.endswith('@chatroom'):
            raise ValueError('只接受群聊 ID，不能提取私聊附件')
        return group_id
    targets = [t['chat_username'] for t in load_watchlist(watchlist_path()).get('targets', [])
               if t.get('label') == name and t['chat_username'].endswith('@chatroom')]
    if not targets:
        targets = [r[0] for r in con.execute(
            'SELECT DISTINCT chat_username FROM messages WHERE chat_name=? AND chat_username LIKE ?',
            (name, '%@chatroom'))]
    targets = sorted(set(targets))
    if len(targets) != 1:
        raise ValueError('群名未匹配或存在歧义，请提供精确群 ID')
    return targets[0]


def run(args):
    with connect(Path(args.db).resolve()) as con:
        gid = resolve_group(con, args.name, args.chat_id)
        stats = con.execute('SELECT COUNT(*),MIN(create_time),MAX(create_time) FROM messages WHERE chat_username=?', (gid,)).fetchone()
        if not stats[0]:
            raise ValueError('快照中未找到该群')
        sql = 'SELECT * FROM messages WHERE chat_username=?'
        params = [gid]
        if args.from_date:
            sql += ' AND create_time>=?'
            params.append(int(dt.datetime.combine(dt.date.fromisoformat(args.from_date), dt.time(), TZ).timestamp()))
        if args.to_date:
            sql += ' AND create_time<?'
            params.append(int(dt.datetime.combine(dt.date.fromisoformat(args.to_date) + dt.timedelta(days=1), dt.time(), TZ).timestamp()))
        sql += ' ORDER BY create_time,sort_seq,source_db,source_table,local_id'
        rows = con.execute(sql, params).fetchall()
    if args.from_date and args.to_date and args.from_date > args.to_date:
        raise ValueError('开始日期不能晚于结束日期')
    types = {x.strip() for x in args.types.lower().split(',')}
    by_size, by_name, scan_errors = index_files(Path(args.file_root).resolve())
    out = Path(args.output).resolve() if args.output else OUT_ROOT / gid
    # Prevent exports overwriting source files or entering the skill/source tree.
    for protected in [Path(args.file_root).resolve(), Path(__file__).resolve().parent.parent]:
        if out == protected or out.is_relative_to(protected) or protected.is_relative_to(out):
            raise ValueError('输出目录不能覆盖微信附件源或技能目录')
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (out / '.lock').open('a') as lock:
        os.chmod(out / '.lock', 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = out / 'files.jsonl'
        old = {r['message_id']: r for r in (json.loads(s) for s in manifest.read_text().splitlines())} if manifest.exists() else {}
        cache, selected, copied, errors = {}, [], 0, 0
        seen = set()
        now = dt.datetime.now(TZ).isoformat()
        for row in rows:
            try:
                info = parse_file(row['decoded_content'] or '')
            except ValueError:
                errors += 1
                continue
            if not info or not re.fullmatch(r'[a-z0-9]{1,16}', info['extension']) or ('all' not in types and info['extension'] not in types):
                continue
            identity = f'{gid}:{row["server_id"]}' if row['server_id'] else f'{gid}:{row["source_db"]}:{row["source_table"]}:{row["local_id"]}:{row["create_time"]}'
            if identity in seen:
                continue
            seen.add(identity)
            r = {**info, 'message_id': identity, 'chat_username': gid, 'chat_name': row['chat_name'],
                 'sender_name': row['sender_name'], 'sent_at': dt.datetime.fromtimestamp(row['create_time'], TZ).isoformat(),
                 'source': {k: row[k] for k in ['source_db', 'source_table', 'local_id', 'server_id']},
                 'discovered_at': old.get(identity, {}).get('discovered_at', now),
                 'status': None, 'match_method': None, 'exported_path': None, 'sha256': None}
            try:
                source, method = find_file(info, by_size, by_name, cache)
                r['match_method'] = method
                if source is None:
                    r['status'] = method
                elif not format_ok(source, info['extension']):
                    r['status'] = 'invalid_format'
                else:
                    sha = digest(source)
                    filename = safe_name(info['file_name'])
                    if not filename.lower().endswith('.' + info['extension']):
                        filename += '.' + info['extension']
                    # One path for identical content even when shared under a different name.
                    folder = out / 'files' / sha
                    if folder.is_symlink() or (out / 'files').is_symlink():
                        raise ValueError('output_symlink_rejected')
                    existing = sorted(p for p in folder.glob('*') if p.is_file()) if folder.exists() else []
                    dest = existing[0] if existing else folder / filename
                    copied += copy_verified(source, dest, sha, info['expected_md5'])
                    r.update(status='exported', exported_path=str(dest), sha256=sha)
            except (OSError, ValueError) as e:
                r['status'] = 'read_or_copy_failed'
                r['error_type'] = type(e).__name__
            selected.append(r)
            old[identity] = r
        atomic_jsonl(manifest, sorted(old.values(), key=lambda r: (r['sent_at'], r['message_id'])))
        summary = {'group_id': gid, 'output': str(out), 'manifest': str(manifest),
                   'range': {'from_date': args.from_date, 'to_date': args.to_date},
                   'snapshot_latest_at': dt.datetime.fromtimestamp(stats[2], TZ).isoformat(),
                   'file_messages': len(selected), 'statuses': dict(collections.Counter(r['status'] for r in selected)),
                   'unique_exported_files': len({r['sha256'] for r in selected if r['sha256']}),
                   'new_copies': copied, 'xml_parse_errors': errors, 'scan_errors': scan_errors}
        atomic_jsonl(out / 'last-run.jsonl', [summary])
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--name', help='监控标签或精确群名称')
    g.add_argument('--chat-id', help='精确 @chatroom ID')
    p.add_argument('--db', default=str(db_path()))
    p.add_argument('--file-root', default=str(FILE_ROOT))
    p.add_argument('--output')
    p.add_argument('--from-date')
    p.add_argument('--to-date')
    p.add_argument('--types', default=DEFAULT_TYPES, help='逗号分隔；all 为所有群文件附件')
    args = p.parse_args()
    try:
        print(json.dumps(run(args), ensure_ascii=False, indent=2))
    except (ValueError, OSError, sqlite3.Error) as e:
        print(json.dumps({'status': 'failed', 'error': str(e)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)

if __name__ == '__main__':
    main()
