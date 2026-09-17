"""Validate a role manifest; this does not judge generated-image resemblance."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--manifest', required=True)
parser.add_argument('--account-id', required=True)
args = parser.parse_args()
path = Path(args.manifest).resolve()
data = json.loads(path.read_text())
if data.get('account_id') != args.account_id or data.get('status') != 'confirmed':
    raise SystemExit('STOP: account mismatch or unconfirmed identity')
refs = data.get('references', [])
if not refs or refs[0].get('role') != 'primary_identity':
    raise SystemExit('STOP: first reference must be primary_identity')
retired = {(path.parent / x).resolve() for x in data.get('retired_identity_files', [])}
paths = []
for ref in refs:
    image = (path.parent / ref['path']).resolve()
    if image in retired or not image.is_file():
        raise SystemExit('STOP: retired or missing reference')
    if hashlib.sha256(image.read_bytes()).hexdigest() != ref['sha256']:
        raise SystemExit('STOP: reference hash changed')
    paths.append(str(image))
print(json.dumps({'account_id': args.account_id, 'character_id': data['character_id'],
                  'version': data['version'], 'identity_inputs': paths,
                  'visual_review': 'REQUIRED: inspect references and output; hash is not resemblance'},
                 ensure_ascii=False, indent=2))
