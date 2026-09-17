"""Validate a role manifest; this does not judge generated-image resemblance."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--manifest', required=True)
parser.add_argument('--account-id', required=True)
parser.add_argument('--character-id', required=True)
parser.add_argument('--account-root', required=True)
args = parser.parse_args()
path = Path(args.manifest).resolve()
data = json.loads(path.read_text())
root = Path(args.account_root).resolve()
if not root.is_dir() or not path.is_relative_to(root):
    raise SystemExit('STOP: manifest outside account root')
if not isinstance(data, dict) or data.get('character_id') != args.character_id:
    raise SystemExit('STOP: character mismatch or invalid manifest')
if data.get('account_id') != args.account_id or data.get('status') != 'confirmed':
    raise SystemExit('STOP: account mismatch or unconfirmed identity')
refs = data.get('references', [])
if not isinstance(refs, list) or not refs or not isinstance(refs[0], dict) or refs[0].get('role') != 'primary_identity':
    raise SystemExit('STOP: first reference must be primary_identity')
retired_files = data.get('retired_identity_files', [])
if not isinstance(retired_files, list) or not all(isinstance(x, str) for x in retired_files):
    raise SystemExit('STOP: invalid retired references')
if not data.get('version'):
    raise SystemExit('STOP: identity version missing')
retired = {(path.parent / x).resolve() for x in retired_files}
paths = []
for ref in refs:
    if not isinstance(ref, dict) or not isinstance(ref.get('path'), str) or not ref['path'].strip():
        raise SystemExit('STOP: invalid reference')
    image = (path.parent / ref['path']).resolve()
    if not image.is_relative_to(root):
        raise SystemExit('STOP: reference outside account root (including symlinks)')
    if image in retired or not image.is_file():
        raise SystemExit('STOP: retired or missing reference')
    if hashlib.sha256(image.read_bytes()).hexdigest() != ref.get('sha256'):
        raise SystemExit('STOP: reference hash changed')
    paths.append(str(image))
print(json.dumps({'account_id': args.account_id, 'character_id': data['character_id'],
                  'version': data['version'], 'identity_inputs': paths,
                  'visual_review': 'REQUIRED: inspect references and output; hash is not resemblance'},
                 ensure_ascii=False, indent=2))
