#!/usr/bin/env python3
"""Probe C1 — meme paquet que les refus, mais AUTRE MOTEUR: hf_mult_replace_object_flash.
Video = source originale 7a92aa1b (reutilisee, aucun upload)."""
import json, os, subprocess, sys
from pathlib import Path

D = Path('/home/ubuntu/ops-tools/seedance-bypass/cas/foot-reprise-20261024')
env = dict(os.environ)
env['PATH'] = os.path.expanduser('~/.local/bin') + ':' + os.path.expanduser('~/.npm-global/bin') + ':' + env['PATH']
MODEL = 'hf_mult_replace_object_flash'
VIDEO = '7a92aa1b-f4b2-4500-881c-c3d8a262f595'

def hf(args, timeout=300):
    return subprocess.run(['higgsfield', '--json'] + args, capture_output=True, text=True, timeout=timeout, env=env)

if (D / 'JOB-ID-C1.txt').exists():
    print('deja consomme:', (D / 'JOB-ID-C1.txt').read_text().strip())
    sys.exit(0)

imgs = ['8e2cb109-e021-4d74-a1b9-2f5aa16ef987', '068842f3-43ad-4029-b45a-e6ac42a0aef5',
        '723cb6ee-39e5-453f-85da-f3d4dfcac4e2', '39fcba50-93d3-4ca6-be6f-9171520fa547',
        'c6f4c491-6bac-4f0d-9eac-cbccee804337', 'ce6fe8b1-c9ae-4024-93ae-a9b276f53cd2',
        'b72abb35-d74c-4550-be55-40742d8ad40c']
base = [MODEL, '--prompt', '@/tmp/football_prompt_cli.json', '--resolution', '720p',
        '--video-references', VIDEO]
for i in imgs:
    base += ['--image-references', i]

rc = hf(['generate', 'cost'] + base)
(D / 'COST-C1.json').write_text(rc.stdout)
(D / 'COST-C1-ERR.txt').write_text(rc.stderr)
print('cost exit', rc.returncode, '| out:', rc.stdout[:200].replace('\n', ' '), '| err:', rc.stderr[:160])

if rc.returncode == 0:
    cr = hf(['generate', 'create'] + base, timeout=600)
    (D / 'CREATE-C1-STDOUT.json').write_text(cr.stdout)
    (D / 'CREATE-C1-STDERR.txt').write_text(cr.stderr)
    print('create exit', cr.returncode, '| out:', cr.stdout[:200].replace('\n', ' '), '| err:', cr.stderr[:200])
    try:
        resp = json.loads(cr.stdout)
        vals = resp if isinstance(resp, list) else [resp]
        ids = [v if isinstance(v, str) else v.get('id') for v in vals]
        print('JOB_C1_ID:', ids)
        (D / 'JOB-ID-C1.txt').write_text('\n'.join(str(x) for x in ids) + '\n')
    except Exception as e:
        print('create parse err', e)
