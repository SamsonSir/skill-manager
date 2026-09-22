"""Optimistic, atomic visual-history append. Plans use content dates, never runtime dates."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from content_state import locked, digest


def append(path, entry, expected_revision):
    required=('account_id','character_id','content_id','asset_path','asset_sha256','status','content_date','activity_id','scene_id','scene_version','outfit','accessories','camera','reason')
    if any(k not in entry for k in required): raise ValueError('incomplete visual entry')
    if entry['status'] not in ('candidate','selected','published'): raise ValueError('invalid asset status')
    if entry['status'] != 'candidate' and entry.get('visual_review') != 'pass': raise ValueError('actual visual review required')
    if entry['status'] == 'published' and not entry.get('publication_evidence'): raise ValueError('publication evidence required')
    if entry['content_date'] is not None:
        from datetime import date
        date.fromisoformat(entry['content_date'])
    if digest(entry['asset_path']) != entry['asset_sha256']: raise ValueError('asset hash mismatch')
    with locked(path) as target:
        history=json.loads(target.read_text()) if target.exists() else dict(account_id=entry['account_id'],character_id=entry['character_id'],revision=0,entries=[])
        if any(history[k]!=entry[k] for k in ('account_id','character_id')): raise ValueError('foreign role history')
        if history['revision'] != expected_revision: raise ValueError('history changed; replan against current history')
        if any(e==entry for e in history['entries']): raise ValueError('duplicate entry')
        history['entries'].append(entry);history['revision']+=1
        fd,tmp=tempfile.mkstemp(dir=target.parent,prefix='.visual-')
        try:
            with os.fdopen(fd,'w') as f:
                json.dump(history,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
            os.replace(tmp,target)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        return history

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--history',required=True);p.add_argument('--entry',required=True);p.add_argument('--expected-revision',required=True,type=int);a=p.parse_args()
    try: print(json.dumps(append(a.history,json.loads(Path(a.entry).read_text()),a.expected_revision),ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError,TypeError) as e: p.exit(1,f'STOP: {e}\n')
