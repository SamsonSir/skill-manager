#!/usr/bin/env python3
"""Discover public-account card candidates in one explicitly selected chat."""
import argparse
import datetime as dt
import json
from pathlib import Path
from account_cards import extract_cards
from attachments import atomic_jsonl, TZ
from watchlist import ACCOUNT_ROOT, connect, db_path


def run(args):
    if args.from_date and args.to_date and args.from_date > args.to_date:
        raise ValueError('开始日期不能晚于结束日期')
    clauses, params = ['chat_username=?'], [args.chat_id]
    if args.from_date:
        clauses.append('create_time>=?')
        params.append(int(dt.datetime.combine(dt.date.fromisoformat(args.from_date), dt.time(), TZ).timestamp()))
    if args.to_date:
        clauses.append('create_time<?')
        params.append(int(dt.datetime.combine(dt.date.fromisoformat(args.to_date) + dt.timedelta(days=1), dt.time(), TZ).timestamp()))
    where = ' WHERE ' + ' AND '.join(clauses)
    rows, seen, scanned = [], set(), 0
    with connect(Path(args.db).resolve()) as con:
        latest = con.execute('SELECT MAX(create_time) FROM messages' + where, params).fetchone()[0]
        for msg in con.execute('SELECT source_db,source_table,local_id,server_id,chat_username,chat_name,create_time,decoded_content FROM messages' + where, params):
            scanned += 1
            for card in extract_cards(msg['decoded_content'] or ''):
                identity = str(msg['server_id'] or (str(msg['source_db']) + ':' + str(msg['source_table']) + ':' + str(msg['local_id'])))
                key = (identity, json.dumps(card, ensure_ascii=False, sort_keys=True))
                if key in seen:
                    continue
                seen.add(key)
                rows.append(card | {'chat_username': msg['chat_username'], 'chat_name': msg['chat_name'],
                                    'sent_at': dt.datetime.fromtimestamp(msg['create_time'], TZ).isoformat(),
                                    'source': {k: msg[k] for k in ('source_db','source_table','local_id','server_id')}})
    rows.sort(key=lambda r: (r['sent_at'], r['source']['local_id'], r['kind']))
    out = Path(args.output).resolve() if args.output else ACCOUNT_ROOT / '学习整理/Joker/对标发现' / dt.datetime.now(TZ).strftime('%Y%m%d-%H%M%S-%f')
    if out.is_relative_to(Path(__file__).resolve().parent.parent):
        raise ValueError('结果不能写入技能目录')
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    atomic_jsonl(out / 'cards.jsonl', rows)
    summary = {'chat_id': args.chat_id, 'scanned_messages': scanned, 'extracted_records': len(rows),
               'unique_account_names': sorted(set(r['account_name'] for r in rows if r['account_name'])),
               'snapshot_latest_at': dt.datetime.fromtimestamp(latest, TZ).isoformat() if latest else None,
               'output': str(out / 'cards.jsonl'),
               'meaning': '分享线索；尚未按上下文判定为对标，不等于已读取文章或图片',
               'unsupported': ['纯图片截图中的名称/OCR', '已缺失的媒体', '加密转发合集']}
    atomic_jsonl(out / 'summary.jsonl', [summary])
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chat-id', required=True)
    p.add_argument('--db', default=str(db_path()))
    p.add_argument('--from-date'); p.add_argument('--to-date'); p.add_argument('--output')
    print(json.dumps(run(p.parse_args()), ensure_ascii=False, indent=2))
