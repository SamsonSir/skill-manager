#!/usr/bin/env python3
"""Account-isolated local WeChat key capture; never prints keys or chat content."""
import argparse
import ast
import ctypes
import hashlib
import json
import os
import platform
import plistlib
import re
import signal
import subprocess
import tempfile
import time
from pathlib import Path

APP = Path('/Applications/WeChat.app')
DATA = Path.home() / 'Library/Containers/com.tencent.xinWeChat/Data'
ROOT = Path.home() / 'Library/Application Support/JokerWeChatKey'
TEMPLATE = Path(__file__).with_name('callback_template.py')


def output(data):
    print(json.dumps(data, ensure_ascii=False))


def command(args, timeout=30):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def write_json(path, data):
    path = Path(path)
    if path.is_symlink():
        raise RuntimeError('refusing symlink output')
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.state-')
    with os.fdopen(fd, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    path.chmod(0o600)


def clone(src, dst):
    if not src.exists():
        return
    if src.is_symlink() or dst.exists() or dst.is_symlink():
        raise RuntimeError('unsafe clone endpoint')
    dst.parent.mkdir(parents=True, exist_ok=True)
    lib = ctypes.CDLL(None, use_errno=True)
    lib.clonefile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    lib.clonefile.restype = ctypes.c_int
    if lib.clonefile(os.fsencode(src), os.fsencode(dst), 0):
        raise RuntimeError('APFS clone failed; source preserved')


def process_info():
    result = []
    for pid in command(['pgrep', '-x', 'WeChat']).stdout.split():
        path = command(['ps', '-p', pid, '-o', 'comm=']).stdout.strip()
        result.append((int(pid), path))
    return result


def identify():
    folder_root = DATA / 'Documents/xwechat_files'
    opened = set()
    for pid, path in process_info():
        if path != str(APP / 'Contents/MacOS/WeChat'):
            continue
        for line in command(['lsof', '-nP', '-p', str(pid), '-Fn']).stdout.splitlines():
            match = re.search(r'/xwechat_files/([^/]+)/db_storage/.*\.db(?:-wal|-shm)?$', line)
            if match:
                opened.add(match.group(1))
    return {'accounts': [{'folder': p.parent.name,
                          'open_business_database': p.parent.name in opened}
                         for p in sorted(folder_root.glob('*/db_storage'))],
            'active_candidates': sorted(opened),
            'selection_rule': 'Use exactly one confirmed account folder; reject ambiguity.'}


def run_state(run):
    run = Path(run).expanduser().resolve()
    if not run.is_relative_to(ROOT.resolve()) or not run.name.startswith('run-'):
        raise RuntimeError('run outside account isolation root')
    state = json.loads((run / 'state.json').read_text())
    for name in ('profile', 'debug_app', 'dbroot'):
        if not Path(state[name]).resolve().is_relative_to(run):
            raise RuntimeError('state points outside selected run')
    return run, state


def prepare(args):
    if not args.authorized:
        raise RuntimeError('capture requires current user authorization')
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise RuntimeError('this implementation requires macOS Apple Silicon')
    folder = args.account_folder
    if not re.fullmatch(r'[A-Za-z0-9_-]+_[a-fA-F0-9]{4}', folder):
        raise RuntimeError('expected exact local account folder, not a nickname')
    account = folder.rsplit('_', 1)[0]
    source = DATA / 'Documents/xwechat_files' / folder
    if source.is_symlink() or not (source / 'db_storage').is_dir():
        raise RuntimeError('account storage unavailable')
    candidates = identify()['active_candidates']
    if candidates and candidates != [folder]:
        raise RuntimeError('selected account is not the unique active database account')
    existing = process_info()
    if any(path != str(APP / 'Contents/MacOS/WeChat') for _, path in existing):
        raise RuntimeError('another WeChat copy is running; do not interfere')
    if existing and not args.allow_quit:
        raise RuntimeError('installed WeChat running; explain temporary quit before --allow-quit')
    for pid, _ in existing:
        os.kill(pid, signal.SIGTERM)
    for _ in range(30):
        if not process_info():
            break
        time.sleep(.2)
    else:
        raise RuntimeError('WeChat did not exit; no force kill')
    ROOT.mkdir(parents=True, exist_ok=True)
    ROOT.chmod(0o700)
    parent = ROOT / account
    if parent.is_symlink():
        raise RuntimeError('unsafe account output directory')
    parent.mkdir(mode=0o700, exist_ok=True)
    parent.chmod(0o700)
    run = Path(tempfile.mkdtemp(prefix='run-', dir=parent))
    info = plistlib.loads((APP / 'Contents/Info.plist').read_bytes())
    build = str(info['CFBundleVersion'])
    app = run / f'WeChat-{build}-JokerKey.app'
    clone(APP, app)
    p = app / 'Contents/Info.plist'
    d = plistlib.loads(p.read_bytes())
    d.update(CFBundleDisplayName='WeChat Joker Key', SUEnableAutomaticChecks=False,
             SUAutomaticallyUpdate=False, SUAllowsAutomaticUpdates=False,
             SUFeedURL='http://127.0.0.1:9/updates-disabled')
    p.write_bytes(plistlib.dumps(d))
    for argv in [['--force', '--deep', '--sign', '-'], ['--verify', '--deep', '--strict']]:
        if command(['/usr/bin/codesign', *argv, str(app)], 180).returncode:
            raise RuntimeError('isolated copy signature operation failed; installed app unchanged')
    profile = run / 'profile'
    profile.mkdir(mode=0o700)
    rels = [f'Documents/xwechat_files/{folder}',
            'Documents/xwechat_files/all_users/config',
            'Documents/xwechat_files/all_users/sqlite',
            f'Documents/xwechat_files/all_users/login/{account}',
            f'Documents/app_data/login/{account}', 'Documents/app_data/config',
            'Library/Preferences/com.tencent.xinWeChat.plist',
            'Library/Preferences/tx.tableName.DeviceInfo.plist']
    for layout in [profile, profile / 'Library/Containers/com.tencent.xinWeChat/Data']:
        for rel in rels:
            clone(DATA / rel, layout / rel)
        p = layout / 'Library/Preferences/com.tencent.xinWeChat.plist'
        d = plistlib.loads(p.read_bytes()) if p.exists() else {}
        d.update(SUEnableAutomaticChecks=False, SUAutomaticallyUpdate=False, SUHasLaunchedBefore=True)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(plistlib.dumps(d))
    (profile / 'tmp').mkdir(mode=0o700)
    # This macOS build redirects the supplied Application Support home below
    # Library/Containers. Seed that observed layout as well, never a shared home.
    redirected = Path.home() / 'Library/Containers/JokerWeChatKey' / account / run.name / 'profile'
    clone(profile, redirected)
    redirected.chmod(0o700)
    dbroot = profile / 'Documents/xwechat_files' / folder / 'db_storage'
    pages, dbs = {}, []
    for p in sorted(dbroot.rglob('*.db')):
        with p.open('rb') as f:
            page = f.read(4096)
        if len(page) == 4096 and not page.startswith(b'SQLite format 3'):
            pages[page[:16].hex()] = page.hex()
            dbs.append(str(p.relative_to(dbroot)))
    if not pages:
        raise RuntimeError('no supported encrypted pages')
    result = run / 'capture-result.json'
    write_json(result, {})
    tree = ast.parse(TEMPLATE.read_text())
    values = {'RESULT_PATH': str(result), 'EXPECTED_SALTS': list(pages),
              'EXPECTED_HMAC_SALTS': {bytes(v ^ 0x3a for v in bytes.fromhex(s)).hex(): s for s in pages},
              'PROBE_PAGE1': bytes.fromhex(next(iter(pages.values()))), 'PROBE_PAGES': pages}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in values:
                node.value = ast.parse(repr(values[name]), mode='eval').body
    cb = run / 'callback.py'
    cb.write_text(ast.unparse(ast.fix_missing_locations(tree)))
    cb.chmod(0o600)
    cmd = run / 'launch.lldb'
    cmd.write_text(f'settings set target.preload-symbols false\ntarget create "{app}/Contents/MacOS/WeChat"\n'
                   f'settings set target.env-vars "HOME={profile}" "CFFIXED_USER_HOME={profile}" "TMPDIR={profile}/tmp/"\n'
                   f'command script import "{cb}"\nwedata_capture\n'
                   f'process launch --stop-at-entry --working-dir "{profile}"\nprocess continue\nquit\n')
    cmd.chmod(0o600)
    write_json(run / 'state.json', {'account': account, 'source_folder': folder, 'build': build,
               'debug_app': str(app), 'profile': str(profile), 'dbroot': str(dbroot),
               'redirected_profile': str(redirected),
               'expected_databases': len(dbs), 'expected_unique_salts': len(pages),
               'databases': dbs, 'stage': 'prepared', 'authorized': True})
    return {'run': str(run), 'stage': 'prepared', 'build': build, 'databases': len(dbs)}


def status(run):
    run, state = run_state(run)
    try:
        d = json.loads((run / 'capture-result.json').read_text() or '{}')
    except json.JSONDecodeError:
        return {'stage': 'result_write_in_progress', 'run': str(run)}
    return {'run': str(run), 'account': state['account'], 'build': state['build'],
            **{k: d.get(k) for k in ('monitor_ready', 'expected_count', 'verified_count', 'complete', 'diagnostics')}}


def verify(run):
    from sqlcipher3 import dbapi2 as cipher
    run, state = run_state(run)
    result = json.loads((run / 'capture-result.json').read_text())
    keys = result.get('keys_by_salt', {})
    checks = []
    dbroot = Path(state['dbroot'])
    for rel in state['databases']:
        p = (dbroot / rel).resolve()
        if not p.is_relative_to(dbroot):
            raise RuntimeError('database path outside selected account')
        with p.open('rb') as f:
            salt = f.read(16).hex()
        entry = keys.get(salt)
        passed, tables, cipher_passed = False, 0, False
        quick_check_status = 'not_run'
        if entry and re.fullmatch(r'[0-9a-fA-F]{64}', entry.get('key', '')):
            c = None
            try:
                c = cipher.connect(p.as_uri() + '?mode=ro', uri=True)
                c.execute('PRAGMA key = "x\'' + entry['key'] + '\'"')
                c.execute('PRAGMA query_only=ON')
                tables = c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
                cipher_passed = not c.execute('PRAGMA cipher_integrity_check').fetchall()
                if cipher_passed:
                    try:
                        passed = c.execute('PRAGMA quick_check').fetchall() == [('ok',)]
                        quick_check_status = 'passed' if passed else 'failed'
                    except Exception:
                        quick_check_status = 'error'
                        custom = c.execute("SELECT COUNT(*) FROM sqlite_master WHERE sql LIKE '%MMFtsTokenizer%'").fetchone()[0]
                        if custom:
                            quick_check_status = 'error_with_wechat_custom_tokenizer'
            except Exception:
                passed = False
            finally:
                if c is not None:
                    c.close()
        checks.append({'database': rel, 'passed': passed, 'tables': tables,
                       'cipher_integrity_passed': cipher_passed, 'quick_check': quick_check_status})
    complete = bool(checks) and all(c['passed'] for c in checks)
    keys_verified = bool(checks) and all(c['cipher_integrity_passed'] for c in checks)
    report = {'complete': complete, 'verified_databases': sum(c['passed'] for c in checks),
              'keys_verified': keys_verified,
              'cipher_verified_databases': sum(c['cipher_integrity_passed'] for c in checks),
              'expected_databases': len(checks), 'checks': checks}
    write_json(run / 'verification.json', report)
    if keys_verified:
        write_json(run / 'keys.json', keys)
        report['keys_file'] = str(run / 'keys.json')
    return report


def main():
    os.umask(0o077)
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='operation', required=True)
    sub.add_parser('identify')
    prep = sub.add_parser('prepare')
    prep.add_argument('--account-folder', required=True)
    prep.add_argument('--authorized', action='store_true')
    prep.add_argument('--allow-quit', action='store_true')
    for op in ['status', 'verify']:
        sub.add_parser(op).add_argument('--run', required=True)
    a = p.parse_args()
    try:
        if a.operation == 'identify':
            result = identify()
        elif a.operation == 'prepare':
            result = prepare(a)
        elif a.operation == 'status':
            result = status(a.run)
        else:
            result = verify(a.run)
        output(result)
        return 0 if result.get('complete') is not False or a.operation != 'verify' else 2
    except Exception as e:
        # Never serialize exception contents from crypto libraries or private capture data.
        output({'ok': False, 'error_type': type(e).__name__, 'stage': a.operation})
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
