"""Stage-specific account readiness, no credentials are read or printed."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import yaml


def check(config_file, account, character):
    path = Path(config_file).resolve()
    cfg = json.loads(path.read_text())
    if cfg.get('account_id') != account or cfg.get('character_id') != character:
        raise ValueError('task/account configuration mismatch')
    root = (path.parent / cfg['project_root']).resolve()
    if not root.is_dir(): raise ValueError('project root missing')
    def asset(key):
        value = cfg.get(key)
        if not isinstance(value, str) or not value.strip(): raise ValueError(f'{key} missing')
        file = (root / value).resolve()
        if not file.is_relative_to(root) or not file.is_file(): raise ValueError(f'{key} outside project or missing')
        return file
    errors = {k: [] for k in ('writing','layout','images','saving')}
    try:
        contract = yaml.safe_load(asset('contract').read_text())
        if not isinstance(contract, dict) or any(contract.get(k)!=v for k,v in [('account_id',account),('character_id',character),('status','confirmed')]):
            raise ValueError('contract identity/status mismatch')
        if contract.get('fact_policy') not in ('source_bound','explicit_fiction'): raise ValueError('unknown fact policy')
        asset('voice_anchor')
    except (ValueError, OSError, yaml.YAMLError) as e: errors['writing'].append(str(e))
    try: asset('layout_template')
    except (ValueError, OSError) as e: errors['layout'].append(str(e))
    try:
        role = (root / cfg['role_root']).resolve()
        if not role.is_relative_to(root) or role == root: raise ValueError('role root must be a distinct project subdirectory')
        manifest = asset('identity')
        result = subprocess.run([sys.executable,str(Path(__file__).with_name('check_identity.py')),'--manifest',str(manifest),'--account-id',account,'--character-id',character,'--account-root',str(role)],capture_output=True,text=True)
        if result.returncode: raise ValueError('identity validation failed: '+result.stderr.strip())
        backend = cfg.get('image_backend', {})
        if backend.get('reference_images') is not True or backend.get('photorealistic') is not True:
            raise ValueError('reference-capable photo backend not configured')
    except (KeyError, ValueError, OSError) as e: errors['images'].append(str(e))
    mapping = cfg.get('backend', {})
    if mapping.get('method') not in ('browser','api'): errors['saving'].append('backend method missing')
    field = 'original_id' if mapping.get('method') == 'browser' else 'app_id'
    if not isinstance(mapping.get(field),str) or not mapping[field].strip(): errors['saving'].append('expected backend identity missing')
    if not mapping.get('binding_evidence'): errors['saving'].append('backend binding evidence missing')
    # Configuration readiness is not authentication or a production packet approval.
    return {'account_id':account,'character_id':character,'stages':{k:{'ready':not v,'missing':v} for k,v in errors.items()},'scope':'configuration only; live identity, packet and visual acceptance still required'}

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--account-id',required=True);p.add_argument('--character-id',required=True)
    a=p.parse_args()
    try: print(json.dumps(check(a.config,a.account_id,a.character_id),ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError,TypeError) as e: p.exit(1,f'STOP: {e}\n')
