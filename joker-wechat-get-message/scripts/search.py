#!/usr/bin/env python3
"""Read-only keyword search over authorized local WeChat snapshot messages."""
import argparse
import datetime as dt
import html
import json
import re
import sqlite3
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from watchlist import ACCOUNT_ROOT, connect, db_path, load_watchlist, watchlist_path
from attachments import atomic_jsonl, TZ
from account_cards import extract_cards, cards_text, strip_sender


def term_pattern(term):
    if not term.strip():
        raise ValueError('关键词不能为空')
    escaped = re.escape(term.strip())
    # Latin keywords/domains must not match within other words (fcbox.com != x.com).
    if term[0].isascii() and term[0].isalnum():
        escaped = r'(?<![A-Za-z0-9_])' + escaped
    if term[-1].isascii() and term[-1].isalnum():
        escaped += r'(?![A-Za-z0-9_])'
    return re.compile(escaped, re.I)


def readable(raw):
    raw = strip_sender(raw)
    card_text = cards_text(extract_cards(raw))
    start = raw.find('<appmsg')
    if start >= 0:
        end = raw.find('</appmsg>', start)
        try:
            root = ET.fromstring(raw[start:end + len('</appmsg>')])
            bits = [root.findtext(k) or '' for k in ['title', 'des', 'url']]
            for item in root.findall('./mmreader/category/item'):
                bits.extend(item.findtext(k) or '' for k in ['title', 'digest', 'url'])
            bits.extend(root.findtext('finderFeed/' + k) or '' for k in ['nickname', 'desc'])
            # Preserve quoted context with an explicit label.
            quote = root.findtext('refermsg/content')
            if quote:
                qtext = strip_sender(quote)
                if qtext.startswith('<'):
                    qtext = cards_text(extract_cards(qtext))
                if qtext:
                    bits.append('【引用内容】' + qtext)
            if card_text:
                bits.append(card_text)
            return '\n'.join(dict.fromkeys(x.strip() for x in bits if x.strip()))
        except ET.ParseError:
            # Only allowlisted user-visible tags, never raw XML or attachment credentials.
            outer = raw[start:]
            boundaries = [outer.find('<' + tag) for tag in ['appattach', 'refermsg', 'finderFeed', 'mmreader']]
            outer = outer[:min([i for i in boundaries if i >= 0], default=len(outer))]
            bits = [html.unescape(x.replace('<![CDATA[', '').replace(']]>', ''))
                    for x in re.findall(r'<(?:title|des|url)>(.*?)</(?:title|des|url)>', outer, re.S)]
            if card_text:
                bits.append(card_text)
            return '\n'.join(dict.fromkeys(bits))
    if raw.lstrip().startswith('<') or raw.lstrip().startswith('<?xml'):
        return card_text
    return re.sub(r'^[^\n ]{1,100}:\n', '', raw)


def urls(text):
    return list(dict.fromkeys(re.findall(r'https?://[^\s<>"\u3000\u3001\u3002\uff0c\uff1b\uff09]+', text)))


def run(args):
    patterns = [term_pattern(t) for t in args.keyword]
    required = [term_pattern(t) for t in args.require]
    if args.limit < 0 or args.max_chars < 100:
        raise ValueError('limit>=0，max-chars>=100')
    if args.scope == 'all' and args.chat_id:
        raise ValueError('全微信和指定会话不能同时选择')
    if args.from_date and args.to_date and args.from_date > args.to_date:
        raise ValueError('开始日期不能晚于结束日期')
    with connect(Path(args.db).resolve()) as con:
        params, clauses = [], []
        if args.chat_id:
            clauses.append('chat_username=?'); params.append(args.chat_id)
        elif args.scope == 'watched':
            ids = [t['chat_username'] for t in load_watchlist(watchlist_path()).get('targets', []) if t.get('enabled')]
            if not ids:
                raise ValueError('监控名单为空，请指定会话或明确选择全微信')
            clauses.append('chat_username IN (' + ','.join('?' for _ in ids) + ')');params.extend(ids)
        if args.from_date:
            clauses.append('create_time>=?');params.append(int(dt.datetime.combine(dt.date.fromisoformat(args.from_date),dt.time(),TZ).timestamp()))
        if args.to_date:
            clauses.append('create_time<?');params.append(int(dt.datetime.combine(dt.date.fromisoformat(args.to_date)+dt.timedelta(days=1),dt.time(),TZ).timestamp()))
        where = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
        latest = con.execute('SELECT MAX(create_time) FROM messages' + where,params).fetchone()[0]
        # Stream one scan; no modification or persistent whole-chat index.
        sql = ('SELECT source_db,source_table,local_id,server_id,chat_username,chat_name,sender_name,create_time,decoded_content FROM messages' + where)
        results, seen, hits = [], set(), 0
        for row in con.execute(sql,params):
            raw = row['decoded_content'] or ''
            if not any(p.search(raw) for p in patterns):
                continue
            text = readable(raw)
            matched = [t for t,p in zip(args.keyword,patterns) if p.search(text)]
            if not matched or (required and not any(p.search(text) for p in required)):
                continue
            identity = f'{row["chat_username"]}:{row["server_id"]}' if row['server_id'] else ':'.join(str(row[k]) for k in ['chat_username','source_db','source_table','local_id','create_time'])
            if identity in seen:
                continue
            seen.add(identity);hits+=1
            # Keep the window around the first match, not just the beginning of a long message.
            position = min(p.search(text).start() for p in patterns if p.search(text))
            begin = max(0,position-args.max_chars//3)
            excerpt = text[begin:begin+args.max_chars]
            results.append({'message_id':identity,'chat_username':row['chat_username'],'chat_name':row['chat_name'],
                            'sender_name':row['sender_name'],'sent_at':dt.datetime.fromtimestamp(row['create_time'],TZ).isoformat(),
                            'source':{k:row[k] for k in ['source_db','source_table','local_id','server_id']},
                            'matched_keywords':matched,'excerpt':excerpt,'excerpt_truncated':len(excerpt)<len(text),
                            'urls':urls(text),'cards':extract_cards(raw)})
        results.sort(key=lambda r:(r['sent_at'],r['message_id']),reverse=True)
        if args.limit:
            results=results[:args.limit]
    out=Path(args.output).resolve() if args.output else ACCOUNT_ROOT/'学习整理/Joker/关键词搜索'/dt.datetime.now(TZ).strftime('%Y%m%d-%H%M%S-%f')
    if out.is_relative_to(Path(__file__).resolve().parent.parent):
        raise ValueError('搜索结果不能写入技能目录')
    out.mkdir(parents=True,exist_ok=True,mode=0o700)
    atomic_jsonl(out/'matches.jsonl',results)
    summary={'scope':args.scope if not args.chat_id else args.chat_id,'keywords':args.keyword,'require_any':args.require,
             'from_date':args.from_date,'to_date':args.to_date,'total_matches':hits,'returned':len(results),
             'limited':hits>len(results),'snapshot_latest_at':dt.datetime.fromtimestamp(latest,TZ).isoformat() if latest else None,
             'output':str(out/'matches.jsonl'),'searched_content':'消息文字及链接卡片，不包含附件正文'}
    atomic_jsonl(out/'summary.jsonl',[summary])
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--keyword',action='append',required=True,help='重复参数为 OR，英文忽略大小写并匹配词边界')
    p.add_argument('--require',action='append',default=[],help='可选：还须匹配此组任一词')
    p.add_argument('--scope',choices=['watched','all'],default='watched')
    p.add_argument('--chat-id')
    p.add_argument('--db',default=str(db_path()))
    p.add_argument('--from-date');p.add_argument('--to-date')
    p.add_argument('--limit',type=int,default=100,help='最新100条；0为全部匹配')
    p.add_argument('--max-chars',type=int,default=1600)
    p.add_argument('--output')
    try:
        print(json.dumps(run(p.parse_args()),ensure_ascii=False,indent=2))
    except (ValueError,OSError,sqlite3.Error) as e:
        print(json.dumps({'status':'failed','error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(1)

if __name__=='__main__':
    main()
