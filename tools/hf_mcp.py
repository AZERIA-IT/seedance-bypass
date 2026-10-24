#!/usr/bin/env python3
"""Higgsfield MCP one-shot client — uses the Hermes MohCreatesAI OAuth tokens.

Usage:
  python3 hf_mcp.py refresh
  python3 hf_mcp.py call <tool_name> '<json_args>'
  python3 hf_mcp.py reveal <jobId>        # flip an ip_detected generation
  python3 hf_mcp.py status <jobId>

Rotating refresh tokens are written back to the token store (mode 600).
Stdlib only.
"""
import json, sys, time, uuid, urllib.request, urllib.parse
from pathlib import Path

TOK_DIR = Path.home() / '.hermes/profiles/mohcreatesai/mcp-tokens'
MCP_URL = 'https://mcp.higgsfield.ai/mcp'
TOKEN_ENDPOINT = 'https://clerk.higgsfield.ai/oauth/token'


def _load(p):
    return json.loads(Path(p).read_text())


def _save(fp, data):
    tmp = Path(str(fp) + '.tmp')
    tmp.write_text(json.dumps(data, indent=1))
    tmp.chmod(0o600)
    tmp.replace(fp)


def _paths():
    return TOK_DIR / 'higgsfield.json', TOK_DIR / 'higgsfield.client.json'


def refresh():
    tp, cp = _paths()
    tok, cli = _load(tp), _load(cp)
    body = urllib.parse.urlencode({
        'grant_type': 'refresh_token',
        'refresh_token': tok['refresh_token'],
        'client_id': cli['client_id'],
    }).encode()
    req = urllib.request.Request(TOKEN_ENDPOINT, data=body,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36',})
    with urllib.request.urlopen(req, timeout=30) as r:
        new = json.loads(r.read())
    if 'access_token' not in new:
        raise SystemExit('refresh failed: ' + json.dumps(new)[:300])
    new.setdefault('refresh_token', tok['refresh_token'])
    new['_obtained_at'] = time.time()
    _save(tp, new)
    return new['access_token']


def ensure_token(max_age=6 * 3600):
    tp, _ = _paths()
    tok = _load(tp)
    if tok.get('_obtained_at') and time.time() - tok['_obtained_at'] < max_age:
        return tok['access_token']
    return refresh()


def _rpc(method, params=None, session=None, token=None, notify=False):
    payload = {'jsonrpc': '2.0', 'method': method}
    if not notify:
        payload['id'] = str(uuid.uuid4())
    if params is not None:
        payload['params'] = params
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': 'application/json',
               'Accept': 'application/json, text/event-stream', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36',}
    if session:
        headers['Mcp-Session-Id'] = session
    req = urllib.request.Request(MCP_URL, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=180) as r:
        sid = r.headers.get('Mcp-Session-Id') or r.headers.get('mcp-session-id')
        raw = r.read().decode('utf-8', 'replace')
    if raw.startswith('event:') or 'data:' in raw[:80]:
        for line in raw.splitlines():
            if line.startswith('data:'):
                raw = line[5:].strip()
                break
    return (json.loads(raw) if raw.strip() else {}), sid


def connect():
    token = ensure_token()
    try:
        res, sid = _rpc('initialize', {
            'protocolVersion': '2025-06-18',
            'capabilities': {},
            'clientInfo': {'name': 'hermes-ops', 'version': '1'},
        }, token=token)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            token = refresh()
            res, sid = _rpc('initialize', {
                'protocolVersion': '2025-06-18', 'capabilities': {},
                'clientInfo': {'name': 'hermes-ops', 'version': '1'}}, token=token)
        else:
            raise
    if not sid:
        sid = (res.get('result') or {}).get('sessionId')
    _rpc('notifications/initialized', {}, session=sid, token=token, notify=True)
    return token, sid


def call(tool, args):
    token, sid = connect()
    res, _ = _rpc('tools/call', {'name': tool, 'arguments': args}, session=sid, token=token)
    return res


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    if cmd == 'refresh':
        print('token refreshed, len', len(refresh()))
        return
    if cmd == 'call':
        tool = sys.argv[2]
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(call(tool, args), ensure_ascii=False, indent=1)[:4000])
        return
    if cmd == 'reveal':
        job = sys.argv[2]
        out = call('reveal_generation', {'jobId': job})
        print(json.dumps(out, ensure_ascii=False, indent=1)[:2000])
        return
    if cmd == 'status':
        print(json.dumps(call('job_status', {'jobId': sys.argv[2]}), ensure_ascii=False, indent=1)[:3000])
        return
    print(__doc__)


if __name__ == '__main__':
    main()
