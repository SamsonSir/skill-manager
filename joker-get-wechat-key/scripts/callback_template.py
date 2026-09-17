import hashlib
import hmac
import json
import lldb
import os
RESULT_PATH = ''
EXPECTED_SALTS = []
EXPECTED_HMAC_SALTS = {}
PROBE_PAGE1 = b''
KEY_RETURN_POINTS = {'1B1A6433-A445-3247-B7E1-753C09CDB137': 50096256}
ENABLE_KEY_RETURN_FALLBACK = False
MODULE_NAME = __name__
DIAGNOSTICS = {'pbkdf_calls': 0, 'pbkdf_shape_hits': 0, 'pbkdf_rounds_2_hits': 0, 'pbkdf_rounds_256000_hits': 0, 'pbkdf_salt_hits': 0, 'key_return_hits': 0, 'candidate_rejections': 0}

def _write_result(payload):
    flags = os.O_WRONLY | os.O_TRUNC
    flags |= getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_CLOEXEC', 0)
    descriptor = os.open(RESULT_PATH, flags)
    try:
        data = json.dumps(payload).encode()
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                return False
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return True

def _record_diagnostic(name):
    DIAGNOSTICS[name] = int(DIAGNOSTICS.get(name, 0)) + 1
    _write_result({'diagnostics': dict(DIAGNOSTICS)})

def _register(frame, name):
    return frame.FindRegister(name).GetValueAsUnsigned()

def _candidate_matches_page1(candidate):
    if len(candidate) != 32 or len(PROBE_PAGE1) < 4096:
        return False
    salt = PROBE_PAGE1[:16]
    stored_hmac = PROBE_PAGE1[4032:4096]
    for enc_key in (candidate, hashlib.pbkdf2_hmac('sha512', candidate, salt, 256000, 32)):
        mac_salt = bytes((value ^ 58 for value in salt))
        mac_key = hashlib.pbkdf2_hmac('sha512', enc_key, mac_salt, 2, 32)
        digest = hmac.new(mac_key, digestmod=hashlib.sha512)
        digest.update(PROBE_PAGE1[16:4032])
        digest.update(1 .to_bytes(4, 'little'))
        if hmac.compare_digest(stored_hmac, digest.digest()):
            return True
    return False

def _normalize_candidate(raw):
    if len(raw) == 32:
        return raw
    if len(raw) == 64:
        try:
            decoded = bytes.fromhex(raw.decode('ascii'))
        except (UnicodeDecodeError, ValueError):
            return b''
        return decoded if len(decoded) == 32 else b''
    return b''

def _save_valid_candidate(candidate, salt, source, process):
    normalized = _normalize_candidate(candidate)
    if not _candidate_matches_page1(normalized):
        _record_diagnostic('candidate_rejections')
        return False
    _write_result({'passphrase': normalized.hex(), 'salt': salt, 'source': source, 'diagnostics': dict(DIAGNOSTICS)})
    print('WEDATA_MATCHED_VALIDATED_DATABASE_KEY', source, flush=True)
    process.Kill()
    os._exit(0)

def _pbkdf_callback(frame, bp_loc, _internal_dict):
    process = frame.GetThread().GetProcess()
    _record_diagnostic('pbkdf_calls')
    algorithm = _register(frame, 'x0')
    password_ptr = _register(frame, 'x1')
    password_len = _register(frame, 'x2')
    salt_ptr = _register(frame, 'x3')
    salt_len = _register(frame, 'x4')
    prf = _register(frame, 'x5')
    rounds = _register(frame, 'x6')
    if algorithm != 2 or password_len != 32 or salt_len != 16 or (prf != 5) or (rounds not in (2, 256000)):
        return False
    _record_diagnostic('pbkdf_shape_hits')
    _record_diagnostic('pbkdf_rounds_2_hits' if rounds == 2 else 'pbkdf_rounds_256000_hits')
    error = lldb.SBError()
    salt = process.ReadMemory(salt_ptr, salt_len, error)
    if not error.Success() or len(salt) != 16:
        return False
    salt_hex = salt.hex()
    if rounds == 2:
        database_salt = EXPECTED_HMAC_SALTS.get(salt_hex, '')
        source = 'pbkdf2_hmac_password'
    else:
        database_salt = salt_hex if salt_hex in EXPECTED_SALTS else ''
        source = 'pbkdf2_passphrase'
    if not database_salt:
        return False
    _record_diagnostic('pbkdf_salt_hits')
    password = process.ReadMemory(password_ptr, password_len, error)
    if not error.Success() or len(password) != 32:
        return False
    _save_valid_candidate(password, database_salt, source, process)
    return False

def _report_process_exit(debugger, _command, _result, _internal_dict):
    process = debugger.GetSelectedTarget().GetProcess()
    state = process.GetState()
    try:
        state_name = lldb.SBDebugger.StateAsCString(state) or str(int(state))
    except Exception:
        state_name = str(int(state))
    try:
        exit_status = int(process.GetExitStatus())
    except Exception:
        exit_status = -1
    try:
        exit_description = ' '.join(str(process.GetExitDescription() or '').split())[:240]
    except Exception:
        exit_description = ''
    payload = {'pid': int(process.GetProcessID() or 0), 'state': state_name, 'exit_status': exit_status, 'exit_description': exit_description}
    _write_result({'diagnostics': dict(DIAGNOSTICS), 'process_exit': payload})
    print('WEDATA_DEBUG_PROCESS_EXIT ' + json.dumps(payload, sort_keys=True), flush=True)

def _read_libcxx_string(frame):
    process = frame.GetThread().GetProcess()
    object_address = _register(frame, 'x29') - 184
    error = lldb.SBError()
    header = process.ReadMemory(object_address, 24, error)
    if not error.Success() or len(header) != 24:
        return b''
    flag = header[23]
    if flag & 128:
        data_address = int.from_bytes(header[0:8], 'little')
        length = int.from_bytes(header[8:16], 'little')
    else:
        data_address = object_address
        length = flag
    if length <= 0 or length > 128:
        return b''
    value = process.ReadMemory(data_address, length, error)
    return value if error.Success() and len(value) == length else b''

def _key_return_callback(frame, bp_loc, _internal_dict):
    process = frame.GetThread().GetProcess()
    _record_diagnostic('key_return_hits')
    candidate = _read_libcxx_string(frame)
    _save_valid_candidate(candidate, PROBE_PAGE1[:16].hex(), 'wechat_key_return', process)
    return False

def _setup(debugger, _command, _result, _internal_dict):
    target = debugger.GetSelectedTarget()
    breakpoint = target.BreakpointCreateByName('CCKeyDerivationPBKDF')
    breakpoint.SetScriptCallbackFunction(f'{MODULE_NAME}._pbkdf_callback')
    breakpoint.SetAutoContinue(True)
    pbkdf_locations = breakpoint.GetNumResolvedLocations()
    key_locations = 0
    if ENABLE_KEY_RETURN_FALLBACK:
        for module in target.module_iter():
            uuid = (module.GetUUIDString() or '').upper()
            offset = KEY_RETURN_POINTS.get(uuid)
            if offset is None:
                continue
            address = module.ResolveFileAddress(offset)
            section = address.GetSection() if address.IsValid() else lldb.SBSection()
            if not address.IsValid() or not section.IsValid() or (not section.GetPermissions() & lldb.ePermissionsExecutable) or (address.GetLoadAddress(target) == lldb.LLDB_INVALID_ADDRESS):
                continue
            key_breakpoint = target.BreakpointCreateBySBAddress(address)
            key_breakpoint.SetScriptCallbackFunction(f'{MODULE_NAME}._key_return_callback')
            key_breakpoint.SetAutoContinue(True)
            key_locations += key_breakpoint.GetNumResolvedLocations()
    print('WEDATA_KEY_MONITOR_READY', pbkdf_locations, key_locations, flush=True)
    _persist({'monitor_ready': True, 'pbkdf_locations': pbkdf_locations})
    if False:
        process = target.GetProcess()
        process.Detach()
        os._exit(24)

def __lldb_init_module(debugger, _internal_dict):
    debugger.HandleCommand(f'command script add -f {MODULE_NAME}._setup wedata_capture')
    debugger.HandleCommand(f'command script add -f {MODULE_NAME}._report_process_exit wedata_capture_exit_report')
PROBE_PAGES = {}
KEYS = {}

def _persist(extra=None):
    data = {'keys_by_salt': KEYS, 'expected_count': len(PROBE_PAGES), 'verified_count': len(KEYS), 'diagnostics': dict(DIAGNOSTICS)}
    if extra:
        data.update(extra)
    _write_result(data)

def _record_diagnostic(name):
    DIAGNOSTICS[name] = int(DIAGNOSTICS.get(name, 0)) + 1
    _persist()

def _valid_raw(candidate, page):
    salt = page[:16]
    mac_key = hashlib.pbkdf2_hmac('sha512', candidate, bytes((v ^ 58 for v in salt)), 2, 32)
    digest = hmac.new(mac_key, page[16:4032] + 1 .to_bytes(4, 'little'), hashlib.sha512).digest()
    return hmac.compare_digest(page[4032:4096], digest)

def _save_valid_candidate(candidate, salt, source, process):
    value = _normalize_candidate(candidate)
    if len(value) != 32:
        return False
    matched = False
    targets = PROBE_PAGES.items() if source == 'pbkdf2_passphrase' else [(salt, PROBE_PAGES.get(salt, ''))]
    for db_salt, page_hex in targets:
        if not page_hex:
            continue
        page = bytes.fromhex(page_hex)
        key = hashlib.pbkdf2_hmac('sha512', value, page[:16], 256000, 32) if source == 'pbkdf2_passphrase' else value
        if _valid_raw(key, page):
            KEYS[db_salt] = {'key': key.hex(), 'mode': 'raw_enc_key'}
            matched = True
    if not matched:
        _record_diagnostic('candidate_rejections')
    _persist()
    if len(KEYS) == len(PROBE_PAGES):
        _persist({'complete': True})
        process.Kill()
        os._exit(0)
    return False
