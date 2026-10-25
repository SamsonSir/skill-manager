"""Allowlisted public account metadata from cards, quotes and forwarded records.

Never serialize raw XML, media endpoints, stranger IDs or namecard tickets.
"""
import html
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, parse_qs


def strip_sender(raw):
    return re.sub(r'^[^\n ]{1,100}:\n', '', raw or '').strip()


def public_url(value):
    value = (value or '').strip()
    try:
        p = urlsplit(value)
        return value if p.scheme in ('http', 'https') and p.hostname == 'mp.weixin.qq.com' and not p.username else None
    except ValueError:
        return None


def attr(tag, key):
    # Snapshot decoder can unescape '&' in XML attributes, making ET reject
    # otherwise intact cards. Extract only known display attributes in this case.
    m = re.search(r'(?<![\w-])' + re.escape(key) + r'\s*=\s*([\"\'])(.*?)\1', tag, re.S)
    return html.unescape(m.group(2)) if m else ''


def picture_metadata(root):
    share = root.find('mmreadershare')
    if share is None:
        return {}
    def number(key):
        value = share.findtext(key) or ''
        return int(value) if value.isdigit() else None
    # Public article cover only; never appattach/CDN download credentials.
    cover = (share.findtext('coverpicimageurl') or '').strip()
    try:
        parsed = urlsplit(cover)
        if parsed.hostname != 'mmbiz.qpic.cn' or parsed.scheme not in ('http','https') or any(k not in ('wx_fmt','wxfrom','wx_lazy','tp') for k in parse_qs(parsed.query)):
            cover = None
    except ValueError:
        cover = None
    return {'message_format': 'image' if share.findtext('itemshowtype') == '8' else 'article',
            'picture_count': number('piccount'), 'cover_url': cover or None,
            'cover_width': number('coverpicwidth'), 'cover_height': number('coverpicheight')}


def parse_xml(raw):
    if '<!DOCTYPE' in raw.upper() or '<!ENTITY' in raw.upper():
        return None
    try:
        return ET.fromstring(raw)
    except ET.ParseError:
        try:
            return ET.fromstring(re.sub(r'&(?!#\d+;|#x[0-9a-fA-F]+;|amp;|lt;|gt;|quot;|apos;)', '&amp;', raw))
        except ET.ParseError:
            return None


def extract_cards(raw, depth=0, context='direct'):
    if depth > 4 or len(raw or '') > 2_000_000:
        return []
    raw = strip_sender(raw)
    if '<!DOCTYPE' in raw.upper() or '<!ENTITY' in raw.upper():
        return []
    result = []
    # Look only at actual msg opening tags, not attributes buried in appattach.
    for match in re.finditer(r'^\s*(?:<\?xml[^>]*>\s*)?(<msg\b[^>]*>)', raw):
        tag = match.group(1)
        name = attr(tag, 'nickname')
        try:
            is_public = bool(int(attr(tag, 'certflag') or '0') & 8)
        except ValueError:
            is_public = False
        if name and is_public:
            username, alias = attr(tag, 'username'), attr(tag, 'alias')
            stable = username if re.fullmatch(r'gh_[A-Za-z0-9_]+', username) else None
            result.append({'kind': 'official_account_card', 'account_name': name,
                           'account_id': stable, 'account_alias': alias or None,
                           'description': attr(tag, 'certinfo') or None,
                           'original_url': public_url(attr(tag, 'brandHomeUrl')),
                           'article_title': None, 'biz': None, 'context': context})
    start = raw.find('<appmsg')
    if start >= 0:
        end = raw.find('</appmsg>', start)
        root = parse_xml(raw[start:end + 9]) if end >= 0 else None
        if root is not None:
            if root.findtext('type') == '5':
                link = public_url(root.findtext('url'))
                if link:
                    q = parse_qs(urlsplit(link).query)
                    name = root.findtext('sourcedisplayname') or None
                    uid = root.findtext('sourceusername') or ''
                    result.append({'kind': 'official_article_card', 'account_name': name,
                                   'account_id': uid if re.fullmatch(r'gh_[A-Za-z0-9_]+', uid) else None,
                                   'account_alias': None, 'description': root.findtext('des') or None,
                                   'article_title': root.findtext('title') or None,
                                   'original_url': link, 'biz': (q.get('__biz') or [None])[0],
                                   'context': context, **picture_metadata(root)})
            for item in root.findall('./mmreader/category/item'):
                link = public_url(item.findtext('url'))
                if link:
                    result.append({'kind': 'official_article_card',
                                   'account_name': item.findtext('sources/source/name') or root.findtext('sourcedisplayname') or None,
                                   'account_id': None, 'account_alias': None,
                                   'description': item.findtext('digest') or None,
                                   'article_title': item.findtext('title') or None,
                                   'original_url': link,
                                   'biz': (parse_qs(urlsplit(link).query).get('__biz') or [None])[0],
                                   'context': context})
            quote = root.findtext('refermsg/content')
            if quote:
                result.extend(extract_cards(quote, depth + 1, 'quoted'))
            record = root.findtext('recorditem')
            if record:
                # Only user-visible embedded content, never CDN URLs or keys.
                rroot = parse_xml(record)
                if rroot is not None:
                    for item in rroot.findall('.//dataitem'):
                        for field in ('datadesc', 'datatitle', 'datafmt'):
                            value = item.findtext(field)
                            if value:
                                result.extend(extract_cards(value, depth + 1, 'forwarded'))
                        web = item.find('weburlitem')
                        if web is not None:
                            link = public_url(web.findtext('link'))
                            if link:
                                result.append({'kind': 'official_article_card', 'account_name': None,
                                               'account_id': None, 'account_alias': None,
                                               'description': web.findtext('desc') or None,
                                               'article_title': web.findtext('title') or item.findtext('datatitle') or None,
                                               'original_url': link,
                                               'biz': (parse_qs(urlsplit(link).query).get('__biz') or [None])[0],
                                               'context': 'forwarded'})
    # Decode escaped nested cards in record/quote content without exporting
    # surrounding XML. Bounded expansion handles one or two encoding layers.
    if '&lt;msg' in raw or '&lt;appmsg' in raw:
        expanded = html.unescape(raw)
        if expanded != raw:
            result.extend(extract_cards(expanded, depth + 1, 'embedded'))
    unique = {}
    for item in result:
        unique.setdefault(json.dumps(item, ensure_ascii=False, sort_keys=True), item)
    return list(unique.values())


def cards_text(cards):
    return '\n'.join(dict.fromkeys(str(c[k]) for c in cards
                                 for k in ('account_name', 'description', 'article_title', 'original_url') if c.get(k)))
