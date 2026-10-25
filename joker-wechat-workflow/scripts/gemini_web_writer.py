#!/usr/bin/env python3
"""Account-scoped Gemini web generation. No credentials or raw errors in output."""
import argparse, asyncio, hashlib, importlib, importlib.metadata, json, os, stat, tempfile, time
from pathlib import Path

MODEL_ID = '56fdd199312815e2'
MODEL_DISPLAY = '3.8 Flash'
MEDIUM_VALUE = 4  # Observed in Gemini web UI on 2026-10-10, not library extended_thinking.
HEADER = 'x-goog-ext-525001261-jspb'
TOTAL_TIMEOUT = 420  # 40s init + 180s stall + up to 180s recovery + 10s close + margin.

def scoped_paths(matrix, account_id, material, output):
    matrix = Path(matrix).resolve()
    registry = json.loads((matrix/'00-矩阵管理/账号目录.json').read_text())
    matches = [a for a in registry['accounts'] if a['account_id'] == account_id]
    if len(matches) != 1:
        raise ValueError('account_not_unique')
    root = (matrix/matches[0]['root']).resolve()
    paths = [Path(material).resolve(), Path(output).resolve()]
    if not all(p.is_relative_to(root) for p in paths) or paths[0] == paths[1]:
        raise ValueError('account_path_mismatch')
    data = json.loads(paths[0].read_text())
    if data.get('account_id') != account_id or data.get('stage') not in ('body', 'title', 'revision'):
        raise ValueError('material_account_or_stage_mismatch')
    if not isinstance(data.get('prompt'), str) or not data['prompt'].strip():
        raise ValueError('empty_prompt')
    return root, paths[1], data

def medium_request(kwargs):
    """Guard and rewrite only StreamGenerate model/reasoning fields."""
    data = dict(kwargs['data']); outer = json.loads(data['f.req']); inner = json.loads(outer[1])
    headers = dict(kwargs['headers']); model = json.loads(headers[HEADER])
    if len(inner) < 81 or len(model) != 17 or model[4] != MODEL_ID or inner[79] != 1 or model[14] != 1:
        raise ValueError('web_request_contract_changed')
    inner[80] = MEDIUM_VALUE; model[15] = MEDIUM_VALUE
    outer[1] = json.dumps(inner, ensure_ascii=False)
    data['f.req'] = json.dumps(outer, ensure_ascii=False); headers[HEADER] = json.dumps(model)
    return {**kwargs, 'data': data, 'headers': headers}

def read_auth(path, account_root):
    p = Path(path).resolve()
    if p.is_relative_to(account_root) or not p.is_file() or stat.S_IMODE(p.stat().st_mode) & 0o077:
        raise ValueError('unsafe_auth_file')
    values = {}
    for item in json.loads(p.read_text()):
        if item.get('name') in ('__Secure-1PSID', '__Secure-1PSIDTS') and item.get('domain', '').lstrip('.') == 'google.com':
            values[item['name']] = item['value']
    if not values.get('__Secure-1PSID'):
        raise ValueError('missing_login')
    return values

async def generate(auth, prompt, cache, diagnostics):
    started = time.monotonic()
    def event(stage, **fields):
        diagnostics.append({"stage": stage, "elapsed_s": round(time.monotonic()-started, 2), **fields})
    event("start")
    if importlib.metadata.version('gemini-webapi') != '2.1.1':
        raise ValueError('unverified_library_version')
    from loguru import logger
    logger.remove()
    def safe_log(message):
        msg = message.record["message"]
        if 'waiting state (queueing)' in msg:
            event('server_queueing')
        if 'active (thinking/analyzing)' in msg:
            event('server_thinking')
        if '[Watchdog]' in msg:
            event('watchdog_detail', socket_idle='Socket idle' in msg,
                  thinking='thinking' in msg, queueing='queueing=True' in msg)
        if '[Recovery]' in msg:
            event('recovery_detail', recovered='Successfully recovered' in msg,
                  timed_out='timed out' in msg)
        for marker, stage in (("[Watchdog]", "library_watchdog"), ("[Recovery]", "library_recovery"), ("Stream incomplete", "stream_incomplete")):
            if marker in msg:
                event(stage)
                break
    sink_id = logger.add(safe_log, level="DEBUG")
    os.environ['GEMINI_COOKIE_PATH'] = cache
    from gemini_webapi import GeminiClient
    from curl_cffi.requests import AsyncSession
    # Avoid scanning unrelated browsers. This process uses only explicit ego session cookies.
    importlib.import_module('gemini_webapi.utils.get_access_token').HAS_BC3 = False
    client = GeminiClient(auth['__Secure-1PSID'], auth.get('__Secure-1PSIDTS'), proxy=os.environ.get('GEMINI_WEB_PROXY'))
    observed = []
    original = AsyncSession.stream
    original_generate = GeminiClient._generate
    def single_attempt(client, *args, **kwargs):
        kwargs['current_retry'] = 0
        return original_generate(client, *args, **kwargs)
    def guarded_stream(session, method, url, **kwargs):
        if 'BardFrontendService/StreamGenerate' in str(url):
            kwargs = medium_request(kwargs)
            observed.append({'model_id': MODEL_ID, 'thinking_value': MEDIUM_VALUE})
            event('stream_request', request_count=len(observed))
        return original(session, method, url, **kwargs)
    try:
        event('init_start')
        await asyncio.wait_for(client.init(timeout=180, watchdog_timeout=120, auto_refresh=False, verbose=False), timeout=40)
        event('init_ready', generation_timeout_s=client.timeout, watchdog_timeout_s=client.watchdog_timeout)
        models = [m for m in client.list_models() or [] if m.model_id == MODEL_ID and m.display_name == MODEL_DISPLAY]
        if len(models) != 1:
            raise ValueError('requested_model_unavailable')
        AsyncSession.stream = guarded_stream
        GeminiClient._generate = single_attempt
        event('generation_start')
        result = None
        async for chunk in client.generate_content_stream(prompt, model=models[0], extended_thinking=False):
            result = chunk
            event('output_chunk', chars=len(chunk.text or ''))
        text = result.text if result is not None else None
        event('generation_returned')
        if not isinstance(text, str) or not text.strip() or not observed:
            raise ValueError('empty_or_unverified_response')
        # Stage-specific editorial quality is reviewed by the executing Agent after this transport check.
        if len(text.strip()) < 8:
            raise ValueError('abnormally_short_response')
        return text, observed
    finally:
        AsyncSession.stream = original
        GeminiClient._generate = original_generate
        event('closing')
        try:
            await asyncio.wait_for(client.close(), timeout=10)
        finally:
            logger.remove(sink_id)
            event('closed')

def classify(error):
    message = str(error).lower()
    if any(k in message for k in ('quota', '429', 'resource_exhausted', 'usage limit')):
        return 'quota_exhausted'
    if isinstance(error, (TimeoutError, asyncio.TimeoutError)):
        return 'timeout'
    if isinstance(error, ValueError) and str(error) in ('requested_model_unavailable','web_request_contract_changed','unverified_library_version','missing_login','unsafe_auth_file','empty_or_unverified_response','abnormally_short_response'):
        return str(error)
    return type(error).__name__

def main():
    p=argparse.ArgumentParser();p.add_argument('--matrix-root',required=True);p.add_argument('--account-id',required=True);p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--auth-file',required=True);p.add_argument('--timeout',type=int,default=TOTAL_TIMEOUT)
    args=p.parse_args(); os.umask(0o077)
    diagnostics=[]
    diag_path=None
    try:
        root, output, material = scoped_paths(args.matrix_root,args.account_id,args.input,args.output)
        diag_path=output.with_suffix(output.suffix+'.diagnostics.json')
        auth=read_auth(args.auth_file,Path(args.matrix_root).resolve())
        with tempfile.TemporaryDirectory(prefix='joker-gemini-cache-') as cache:
            text, evidence=asyncio.run(asyncio.wait_for(generate(auth,material['prompt'],cache,diagnostics),timeout=min(args.timeout,TOTAL_TIMEOUT)))
        output.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix='.gemini-',dir=output.parent)
        try:
            with os.fdopen(fd,'w') as f:f.write(text)
            os.replace(tmp,output)
        finally:
            if Path(tmp).exists():Path(tmp).unlink()
        print(json.dumps({'status':'ok','account_id':args.account_id,'stage':material['stage'],'model_display':MODEL_DISPLAY,'model_id':MODEL_ID,'thinking':'medium','thinking_value':MEDIUM_VALUE,'request_count':len(evidence),'chars':len(text),'output':str(output),'sha256':hashlib.sha256(text.encode()).hexdigest()},ensure_ascii=False))
        return 0
    except Exception as e:
        diagnostics.append({'stage':'failed','reason':classify(e),'error_type':type(e).__name__})
        print(json.dumps({'status':'fallback_required','reason':classify(e),'account_id':args.account_id},ensure_ascii=False))
        return 2
    finally:
        if diag_path is not None:
            diag_path.write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2))
if __name__=='__main__':raise SystemExit(main())
