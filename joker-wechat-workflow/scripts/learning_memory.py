#!/usr/bin/env python3
"""Account-scoped, evidence-backed editorial feedback. Standard library only."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

STORE = Path('00-创作反馈/反馈与样文.json')
MAX_SOURCE_BYTES = 2 * 1024 * 1024


class MemoryError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise MemoryError(message)


def nonempty(value, name):
    require(isinstance(value, str) and bool(value.strip()), f'{name} must be a nonempty string')
    return value.strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scoped_path(root, value, must_exist=True):
    value = nonempty(value, 'path')
    raw = Path(value)
    require('..' not in raw.parts, 'parent traversal is forbidden')
    path = raw if raw.is_absolute() else root / raw
    try:
        relative = path.relative_to(root)
    except ValueError:
        raise MemoryError('path must belong to the selected account')
    current = root
    for part in relative.parts:
        current = current / part
        require(not current.is_symlink(), 'symbolic links are forbidden')
    require(path.resolve().is_relative_to(root), 'path escapes its root')
    if must_exist:
        require(path.is_file(), 'source must be an existing regular file')
    return path


class LearningMemory:
    def __init__(self, matrix_root, account_id):
        self.account_id = nonempty(account_id, 'account_id')
        self.matrix = Path(matrix_root).absolute()
        require(self.matrix.is_dir() and self.matrix.resolve() == self.matrix,
                'matrix root must be a real directory, not a symbolic link')
        index_path = scoped_path(self.matrix, '00-矩阵管理/账号目录.json')
        index = json.loads(index_path.read_text(encoding='utf-8'))
        accounts = index.get('accounts', [])
        matches = [a for a in accounts if a.get('account_id') == self.account_id]
        require(len(matches) == 1, 'account_id must match exactly one registered account')
        self.root = scoped_path(self.matrix, matches[0].get('root'), must_exist=False)
        require(self.root != self.matrix and self.root.is_dir(), 'account root must be an existing subdirectory')
        for other in accounts:
            if other is matches[0]:
                continue
            other_root = scoped_path(self.matrix, other.get('root'), must_exist=False)
            require(not (self.root.is_relative_to(other_root) or other_root.is_relative_to(self.root)),
                    'account roots must not overlap')
        self.path = scoped_path(self.root, str(STORE), must_exist=False)

    def source(self, value):
        path = scoped_path(self.root, value)
        lowered = '/'.join(p.lower() for p in path.relative_to(self.root).parts)
        sensitive = ('.env', 'credential', 'secret', 'token', 'private_key', '密钥', '凭据', '密码')
        require(not any(word in lowered for word in sensitive), 'credential files are not editorial sources')
        require(path.suffix.lower() in {'.md', '.txt', '.json', '.csv', '.html'}, 'source must be a text document')
        require(path.stat().st_size <= MAX_SOURCE_BYTES, 'source document is too large')
        data = path.read_bytes()
        return {'path': path.relative_to(self.root).as_posix(), 'sha256': sha(data)}, data.decode('utf-8')

    def evidence(self, value):
        require(isinstance(value, dict) and set(value) == {'path', 'quote'}, 'evidence requires exactly path and quote')
        quote = nonempty(value['quote'], 'evidence.quote')
        source, text = self.source(value['path'])
        require(quote in text, 'evidence quote was not found verbatim in its source')
        return {**source, 'quote': quote}

    def load(self):
        scoped_path(self.root, str(STORE), must_exist=False)
        if not self.path.exists():
            return {'schema_version': 1, 'account_id': self.account_id, 'records': {'feedback': [], 'exemplar': []}}
        data = json.loads(self.path.read_text(encoding='utf-8'))
        require(isinstance(data, dict) and data.get('schema_version') == 1, 'unsupported store format')
        require(data.get('account_id') == self.account_id, 'store account_id does not match selected account')
        records = data.get('records')
        require(isinstance(records, dict) and set(records) == {'feedback', 'exemplar'}, 'invalid record collections')
        for kind, entries in records.items():
            require(isinstance(entries, list), 'invalid record history')
            seen = {}
            for record in entries:
                require(isinstance(record, dict), 'invalid record')
                rid = nonempty(record.get('id'), 'record id')
                require(record.get('version') == seen.get(rid, 0) + 1, 'invalid version sequence')
                require(record.get('operation') in {'put', 'revoke'}, 'invalid operation')
                require(record.get('account_id') == self.account_id, 'record belongs to another account')
                self.validate_stored(kind, record)
                seen[rid] = record['version']
        return data

    def validate_stored(self, kind, record):
        """Reject corrupt metadata without reopening old, superseded sources."""
        nonempty(record.get('recorded_at'), 'recorded_at')
        refs = [record.get('evidence')]
        require(isinstance(refs[0], dict), 'invalid stored evidence')
        nonempty(refs[0].get('quote'), 'stored evidence.quote')
        if record['operation'] == 'revoke':
            nonempty(record.get('reason'), 'revocation reason')
        else:
            require(record.get('status') in {'candidate', 'confirmed'}, 'invalid stored status')
            if kind == 'feedback':
                nonempty(record.get('rule'), 'stored rule')
                require(record.get('origin') in {'user_feedback', 'agent_inference'}, 'invalid stored origin')
                require(record['status'] != 'confirmed' or record['origin'] == 'user_feedback',
                        'stored agent inference cannot be confirmed')
                require(record.get('scope') in {'account', 'content_type'}, 'invalid stored scope')
                if record['scope'] == 'content_type':
                    nonempty(record.get('content_type'), 'stored content_type')
                else:
                    require('content_type' not in record, 'invalid account scope')
                refs += [record[f] for f in ('draft_path', 'final_path') if f in record]
            else:
                require(record.get('kind') in {'approved', 'benchmark', 'candidate'}, 'invalid stored exemplar kind')
                require(record['kind'] != 'approved' or record['status'] == 'confirmed',
                        'stored approved exemplar lacks confirmation')
                require(record.get('ownership') in {'user', 'third_party', 'unknown'}, 'invalid stored ownership')
                uses = record.get('allowed_uses')
                require(isinstance(uses, list) and uses and all(u in {'style', 'structure'} for u in uses),
                        'invalid stored allowed_uses')
                require(record.get('personal_materials_reusable') is False, 'invalid stored material reuse permission')
                refs.append(record)
        for ref in refs:
            require(isinstance(ref, dict), 'invalid stored source reference')
            scoped_path(self.root, ref.get('path'), must_exist=False)
            require(isinstance(ref.get('sha256'), str) and re.fullmatch('[a-f0-9]{64}', ref['sha256']),
                    'invalid stored source hash')

    @contextmanager
    def lock(self):
        scoped_path(self.root, str(STORE), must_exist=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = scoped_path(self.root, str(STORE) + '.lock', must_exist=False)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'a') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def append(self, kind, record):
        with self.lock():
            data = self.load()
            history = data['records'][kind]
            versions = [r['version'] for r in history if r['id'] == record['id']]
            if record['operation'] == 'put' and record.get('status') == 'confirmed':
                # Confirmation applies to a specific rule/sample, not merely its ID.
                # Scan all versions so an intervening candidate/revocation cannot
                # transfer old confirmation to changed content.
                fields = ('rule', 'scope', 'content_type') if kind == 'feedback' else ('path', 'sha256')
                for previous in history:
                    if (previous['id'] != record['id'] or previous['operation'] != 'put'
                            or previous.get('status') != 'confirmed'):
                        continue
                    if kind == 'exemplar' and not (record.get('kind') == previous.get('kind') == 'approved'):
                        continue
                    same_evidence = all(previous['evidence'].get(key) == record['evidence'].get(key)
                                        for key in ('path', 'quote', 'sha256'))
                    changed_content = any(previous.get(field) != record.get(field) for field in fields)
                    require(not (same_evidence and changed_content),
                            'changed content requires new confirmation evidence; save as candidate or provide new evidence')
            if record['operation'] == 'revoke':
                require(versions, 'cannot revoke an unknown id')
                latest = next(r for r in reversed(history) if r['id'] == record['id'])
                require(latest['operation'] != 'revoke', 'record is already revoked')
            record = {**record, 'account_id': self.account_id,
                      'version': max(versions, default=0) + 1,
                      'recorded_at': datetime.now(timezone.utc).isoformat()}
            history.append(record)
            fd, temporary = tempfile.mkstemp(prefix='.feedback-', dir=self.path.parent)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                    json.dump(data, handle, ensure_ascii=False, indent=2)
                    handle.write('\n')
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, self.path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        return record

    def put(self, kind, value):
        require(isinstance(value, dict), 'input must be an object')
        common = {'id', 'status', 'evidence'}
        allowed = common | ({'rule', 'scope', 'content_type', 'origin', 'draft_path', 'final_path'} if kind == 'feedback'
                            else {'path', 'kind', 'ownership', 'allowed_uses', 'personal_materials_reusable'})
        require(not set(value) - allowed, 'unknown input fields: ' + ', '.join(sorted(set(value) - allowed)))
        rid = nonempty(value.get('id'), 'id')
        require(re.fullmatch(r'[A-Za-z0-9_\-\u4e00-\u9fff]{1,100}', rid) is not None, 'invalid id')
        status = value.get('status', 'candidate')
        require(status in {'candidate', 'confirmed'}, 'invalid status')
        record = {'id': rid, 'operation': 'put', 'status': status, 'evidence': self.evidence(value.get('evidence'))}
        if kind == 'feedback':
            origin = value.get('origin')
            require(origin in {'user_feedback', 'agent_inference'}, 'invalid origin')
            require(status != 'confirmed' or origin == 'user_feedback', 'agent inference cannot be confirmed')
            scope = value.get('scope')
            require(scope in {'account', 'content_type'}, 'invalid scope')
            record.update(rule=nonempty(value.get('rule'), 'rule'), scope=scope, origin=origin)
            if scope == 'content_type':
                record['content_type'] = nonempty(value.get('content_type'), 'content_type')
            else:
                require('content_type' not in value, 'account scope must not set content_type')
            for field in ('draft_path', 'final_path'):
                if field in value:
                    record[field], _ = self.source(value[field])
        else:
            exemplar_kind = value.get('kind')
            require(exemplar_kind in {'approved', 'benchmark', 'candidate'}, 'invalid exemplar kind')
            require(exemplar_kind != 'approved' or status == 'confirmed', 'approved exemplar requires explicit confirmation evidence')
            ownership = value.get('ownership')
            require(ownership in {'user', 'third_party', 'unknown'}, 'invalid ownership')
            uses = value.get('allowed_uses')
            require(isinstance(uses, list) and len(uses) > 0 and all(u in {'style', 'structure'} for u in uses), 'allowed_uses only permits style and structure')
            require(value.get('personal_materials_reusable', False) is False, 'personal materials are never reusable')
            source, _ = self.source(value.get('path'))
            record.update(**source, kind=exemplar_kind, ownership=ownership,
                          allowed_uses=sorted(set(uses)), personal_materials_reusable=False)
        return self.append(kind, record)

    def revoke(self, kind, rid, reason, evidence):
        return self.append(kind, {'id': nonempty(rid, 'id'), 'operation': 'revoke',
                                 'reason': nonempty(reason, 'reason'), 'evidence': self.evidence(evidence)})

    def context(self, content_type, limit=5):
        nonempty(content_type, 'content_type')
        require(isinstance(limit, int) and 1 <= limit <= 100, 'limit must be between 1 and 100')
        result = {'account_id': self.account_id, 'content_type': content_type,
                  'confirmed_rules': [], 'candidate_rules': [], 'exemplars': [], 'warnings': []}
        for kind, history in self.load()['records'].items():
            latest = {}
            for record in history:
                latest[record['id']] = record
            for record in sorted(latest.values(), key=lambda r: r['recorded_at'], reverse=True):
                if record['operation'] == 'revoke':
                    continue
                if kind == 'feedback' and record.get('scope') == 'content_type' and record.get('content_type') != content_type:
                    continue
                refs = [record.get('evidence')]
                refs += [record[f] for f in ('draft_path', 'final_path') if f in record]
                if kind == 'exemplar':
                    refs.append(record)
                try:
                    for ref in refs:
                        require(isinstance(ref, dict), 'missing source reference')
                        current, text = self.source(ref.get('path'))
                        require(current['sha256'] == ref.get('sha256'), 'source changed')
                        if 'quote' in ref:
                            require(ref['quote'] in text, 'evidence quote no longer exists')
                except (MemoryError, OSError, UnicodeError) as exc:
                    result['warnings'].append({'kind': kind, 'id': record['id'], 'reason': f'stale or unavailable: {exc}'})
                    continue
                key = 'exemplars' if kind == 'exemplar' else ('confirmed_rules' if record.get('status') == 'confirmed' else 'candidate_rules')
                result[key].append(record)
        result['exemplars'].sort(key=lambda r: r.get('kind') != 'approved')
        result['total_counts'] = {key: len(result[key]) for key in ('confirmed_rules', 'candidate_rules', 'exemplars')}
        result['truncated'] = {key: count > limit for key, count in result['total_counts'].items()}
        for key in ('confirmed_rules', 'candidate_rules', 'exemplars'):
            result[key] = result[key][:limit]
        return result


def read_input(value, inline=False):
    if inline and value.lstrip().startswith('{'):
        return json.loads(value)
    return json.loads(Path(value).read_text(encoding='utf-8'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix-root', required=True)
    parser.add_argument('--account-id', required=True)
    subs = parser.add_subparsers(dest='command', required=True)
    for command in ('put-feedback', 'put-exemplar'):
        subs.add_parser(command).add_argument('--input', required=True, help='UTF-8 JSON input file')
    revoke = subs.add_parser('revoke')
    revoke.add_argument('--kind', choices=['feedback', 'exemplar'], required=True)
    revoke.add_argument('--id', required=True)
    revoke.add_argument('--reason', required=True)
    revoke.add_argument('--evidence', required=True, help='JSON object or UTF-8 JSON file')
    context = subs.add_parser('context')
    context.add_argument('--content-type', required=True)
    context.add_argument('--limit', type=int, default=5)
    subs.add_parser('describe')
    args = parser.parse_args(argv)
    try:
        memory = LearningMemory(args.matrix_root, args.account_id)
        if args.command.startswith('put-'):
            output = memory.put(args.command[4:], read_input(args.input))
        elif args.command == 'revoke':
            output = memory.revoke(args.kind, args.id, args.reason, read_input(args.evidence, inline=True))
        elif args.command == 'context':
            output = memory.context(args.content_type, args.limit)
        else:
            memory.load()
            output = {'schema_version': 1, 'account_id': memory.account_id, 'account_root': str(memory.root),
                      'store': str(memory.path), 'exists': memory.path.exists(),
                      'confirmation': 'explicit user evidence only; never inferred from repetition',
                      'personal_materials_reusable': False, 'changes_draft_permissions': False}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (MemoryError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
