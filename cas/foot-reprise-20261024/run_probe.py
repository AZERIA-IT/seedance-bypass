#!/usr/bin/env python3
"""Reprise du job refusé foot (47c6a6c8 / 8b1269d7) — variante A.
Meme prompt, memes 7 fiches (UUID reutilises), seule la copie video change:
reencodee H.264 crf18, sans piste audio. Upload -> devis -> create (1 seul).
"""
import json, os, subprocess, sys
from pathlib import Path

D = Path('/home/ubuntu/ops-tools/seedance-bypass/cas/foot-reprise-20261024')
env = dict(os.environ)
env['PATH'] = os.path.expanduser('~/.local/bin') + ':' + os.path.expanduser('~/.npm-global/bin') + ':' + env['PATH']

def hf(args, timeout=300):
    return subprocess.run(['higgsfield', '--json'] + args, capture_output=True, text=True, timeout=timeout, env=env)

def find_id(x):
    if isinstance(x, dict):
        for k in ('id', 'upload_id', 'media_id', 'file_id'):
            if k in x and isinstance(x[k], str):
                return x[k]
        for v in x.values():
            r = find_id(v)
            if r:
                return r
    if isinstance(x, list):
        for v in x:
            r = find_id(v)
            if r:
                return r
    return None

# 0. help (trace)
h = hf(['upload', 'create', '--help'])
(D / 'UPLOAD-HELP.txt').write_text(h.stdout + h.stderr)

# 1. upload de la variante
r = hf(['upload', 'create', str(D / 'VIDEO-V1-mute.mp4')])
(D / 'UPLOAD-STDOUT.json').write_text(r.stdout)
(D / 'UPLOAD-STDERR.txt').write_text(r.stderr)
print('upload exit', r.returncode, '| out:', r.stdout[:220].replace('\n', ' '), '| err:', r.stderr[:160])
d = json.loads(r.stdout) if (r.returncode == 0 and r.stdout.strip()) else {}
uid = find_id(d)
print('UPLOAD_ID:', uid)
(D / 'UPLOAD-ID.txt').write_text(str(uid) + '\n')
if not uid:
    sys.exit(0)

# 2. devis (paquet complet)
imgs = ['8e2cb109-e021-4d74-a1b9-2f5aa16ef987', '068842f3-43ad-4029-b45a-e6ac42a0aef5',
        '723cb6ee-39e5-453f-85da-f3d4dfcac4e2', '39fcba50-93d3-4ca6-be6f-9171520fa547',
        'c6f4c491-6bac-4f0d-9eac-cbccee804337', 'ce6fe8b1-c9ae-4024-93ae-a9b276f53cd2',
        'b72abb35-d74c-4550-be55-40742d8ad40c']
base = ['hf_mult_replace_object', '--prompt', '@/tmp/football_prompt_cli.json', '--resolution', '720p',
        '--video-references', uid]
for i in imgs:
    base += ['--image-references', i]

rc = hf(['generate', 'cost'] + base)
(D / 'COST.json').write_text(rc.stdout)
(D / 'COST-ERR.txt').write_text(rc.stderr)
print('cost exit', rc.returncode, '| out:', rc.stdout[:250].replace('\n', ' '), '| err:', rc.stderr[:160])

# 3. create (un seul)
if rc.returncode == 0:
    cr = hf(['generate', 'create'] + base, timeout=600)
    (D / 'CREATE-STDOUT.json').write_text(cr.stdout)
    (D / 'CREATE-STDERR.txt').write_text(cr.stderr)
    print('create exit', cr.returncode, '| out:', cr.stdout[:220].replace('\n', ' '), '| err:', cr.stderr[:200])
    try:
        resp = json.loads(cr.stdout)
        vals = resp if isinstance(resp, list) else [resp]
        ids = [v if isinstance(v, str) else v.get('id') for v in vals]
        print('JOB_ID:', ids)
        (D / 'JOB-ID.txt').write_text('\n'.join(str(x) for x in ids) + '\n')
    except Exception as e:
        print('create parse err', e)
