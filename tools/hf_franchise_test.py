#!/usr/bin/env python3
"""End-to-end franchise/IP test on Higgsfield via MCP (app path, not dev API).

upload sheet -> confirm -> generate seedance_2_5 draft -> poll -> reveal if ip_detected.
"""
import json, re, sys, time, urllib.request
sys.path.insert(0, '/home/ubuntu/ops-tools/seedance-bypass/tools')
from hf_mcp import call

FILE = '/home/ubuntu/ops-tools/seedance-bypass/out/q3_sheet.png'
PROMPT = ("Reference image 1 defines the character: a young ice queen with a platinum side braid, "
          "ice-blue layered gown and cape. She turns her head toward camera and smiles faintly, braid and cape "
          "sway gently. Slow subtle push-in. Soft volumetric light, 3D animated film aesthetic. No text, no overlay.")


def p(label, obj):
    print('##', label)
    print(json.dumps(obj, ensure_ascii=False)[:700])
    return obj


def text_of(res):
    return ((res.get('result') or {}).get('content') or [{}])[0].get('text', '')


def sc_of(res):
    return (res.get('result') or {}).get('structuredContent') or res.get('structuredContent') or {}


# 1) upload
res = call('media_upload', {'filename': 'q3_sheet.png', 'content_type': 'image/png',
                            'context': 'franchise character sheet test'})
txt = text_of(res)
m_id = re.search(r'([0-9a-f-]{36}):', txt)
m_url = re.search(r"'(https://upload[^']+)'", txt)
print('## upload text:'); print(txt[:300])
if not (m_id and m_url):
    sys.exit('parse fail')
mid, up = m_id.group(1), m_url.group(1)
print('media_id=', mid)

# 2) PUT + 3) confirm
data = open(FILE, 'rb').read()
import subprocess
r = subprocess.run(['curl', '-sS', '-o', '/tmp/put.out', '-w', '%{http_code}', '-X', 'PUT',
                    '-H', 'Content-Type: image/png', '--data-binary', '@' + FILE, up],
                   capture_output=True, text=True)
print('PUT ->', r.stdout)
p('media_confirm', sc_of(call('media_confirm', {'type': 'image', 'media_id': mid})))

# 4) submit
params = {'model': 'seedance_2_5', 'prompt': PROMPT,
          'medias': [{'role': 'image', 'value': mid}],
          'aspect_ratio': '9:16', 'duration': 5, 'resolution': '480p', 'draft': True}
res = call('generate_video', {'params': params, 'context': 'franchise ip test'})
sc = sc_of(res)
p('submit', sc or text_of(res)[:400])
if sc.get('unlim_choice'):
    print('>> unlim choice:', sc['unlim_choice'])
    res = call('generate_video', {'params': dict(params, use_unlim=True), 'context': 'franchise ip test'})
    sc = sc_of(res)
    p('submit(unlim)', sc or text_of(res)[:400])
jid = None
for j in (sc.get('jobs') or []):
    jid = j.get('jobId') or j.get('job_id') or j.get('id')
if not jid:
    jid = sc.get('job_id') or sc.get('jobId')
print('job:', jid)
if not jid:
    sys.exit('no job id')

# 5) poll
s = None
for i in range(40):
    time.sleep(15)
    st = sc_of(call('job_status', {'jobId': jid})).get('generation', {})
    s = st.get('status')
    print(f'[{i}] {s}')
    if s in ('completed', 'failed', 'nsfw', 'ip_detected'):
        break

if s == 'ip_detected':
    p('reveal', sc_of(call('reveal_generation', {'jobId': jid})) or text_of(call('reveal_generation', {'jobId': jid})))
    time.sleep(10)
    st = sc_of(call('job_status', {'jobId': jid})).get('generation', {})
    print('after reveal:', st.get('status'), st.get('result_url'))

out = sc_of(call('job_status', {'jobId': jid})).get('generation', {})
print('FINAL', json.dumps({k: out.get(k) for k in ('id', 'status', 'result_url', 'results')}, default=str)[:900])
