"""Persistent draft-attempt guard. No network or publishing capability."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@contextmanager
def locked(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path) + '.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield path


def update(path, action, account, character, content, article=None, draft_id=None,
           attempt_id=None, allow_save=True, evidence=None, artifacts=None):
    with locked(path) as path:
        if action == 'init':
            if path.exists():
                raise ValueError('content already exists; resume rather than overwrite')
            if not all(isinstance(v, str) and v.strip() for v in (account, character, content)):
                raise ValueError('explicit account, character and content required')
            state = dict(account_id=account, character_id=character, content_id=content,
                         article=str(Path(article).resolve()), article_sha256=digest(article),
                         allow_save=allow_save, save_status='not_requested', attempts=[],
                         artifacts={str(Path(f).resolve()): digest(f) for f in (artifacts or [])})
        else:
            state = json.loads(path.read_text())
            if (account, character, content) != tuple(state[k] for k in ('account_id','character_id','content_id')):
                raise ValueError('context mismatch')
            if digest(state['article']) != state['article_sha256']:
                raise ValueError('approved content changed; re-review required')
            for asset, expected_hash in state.get('artifacts', {}).items():
                if digest(asset) != expected_hash:
                    raise ValueError('approved layout/image changed; re-review required')
            if action == 'begin':
                if not state['allow_save']:
                    raise ValueError('saving disabled by user')
                if state['save_status'] not in ('not_requested', 'failed'):
                    raise ValueError('reconcile existing attempt; do not create another draft')
                state['attempt_id'] = uuid.uuid4().hex
                state['save_status'] = 'unknown'
                state['attempts'].append(state['attempt_id'])
            elif action in ('saved', 'failed', 'verified'):
                if attempt_id != state.get('attempt_id') or not attempt_id:
                    raise ValueError('attempt mismatch')
                if not evidence or not Path(evidence).is_file():
                    raise ValueError('local response/readback evidence required')
                if action == 'saved':
                    if state['save_status'] != 'unknown' or not isinstance(draft_id, str) or not draft_id.strip():
                        raise ValueError('saved requires uncertain attempt and nonempty draft id')
                    proof = json.loads(Path(evidence).read_text())
                    expected = dict(account_id=account, character_id=character, content_id=content,
                                    attempt_id=attempt_id, draft_id=draft_id, article_sha256=state['article_sha256'])
                    if any(proof.get(k) != v for k,v in expected.items()):
                        raise ValueError('save receipt context mismatch')
                    state['draft_id'] = draft_id
                    state['save_status'] = 'saved_pending_readback'
                elif action == 'failed':
                    if state['save_status'] != 'unknown':
                        raise ValueError('cannot erase an acknowledged draft')
                    # Only a definitive rejection permits retry, never a timeout.
                    proof = json.loads(Path(evidence).read_text())
                    if proof.get('definitive_not_created') is not True or proof.get('attempt_id') != attempt_id:
                        raise ValueError('failure must prove this attempt did not create a draft')
                    state['save_status'] = 'failed'
                else:
                    proof = json.loads(Path(evidence).read_text())
                    expected = dict(account_id=account, character_id=character, content_id=content,
                                    draft_id=state.get('draft_id'), article_sha256=state['article_sha256'])
                    if state['save_status'] != 'saved_pending_readback' or any(proof.get(k)!=v for k,v in expected.items()):
                        raise ValueError('readback context mismatch')
                    if any(proof.get(k) is not True for k in ('text_matches','images_match','layout_reviewed')):
                        raise ValueError('readback checks incomplete')
                    state['save_status'] = 'verified'
                state['evidence'] = dict(path=str(Path(evidence).resolve()), sha256=digest(evidence))
            else:
                raise ValueError('unknown action')
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.state-')
        try:
            with os.fdopen(fd, 'w') as out:
                json.dump(state, out, ensure_ascii=False, indent=2)
                out.flush(); os.fsync(out.fileno())
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        return state


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('action', choices=['init','begin','saved','failed','verified'])
    for key in ('state','account-id','character-id','content-id'): p.add_argument('--'+key,required=True)
    for key in ('article','draft-id','attempt-id','evidence'): p.add_argument('--'+key)
    p.add_argument('--artifact', action='append', default=[])
    p.add_argument('--no-save',action='store_true')
    a=p.parse_args()
    try:
        print(json.dumps(update(a.state,a.action,a.account_id,a.character_id,a.content_id,
              a.article,a.draft_id,a.attempt_id,not a.no_save,a.evidence,a.artifact),ensure_ascii=False,indent=2))
    except (ValueError,TypeError,OSError,KeyError) as exc:
        p.exit(1, f'STOP: {exc}\n')
