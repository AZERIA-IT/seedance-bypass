#!/usr/bin/env python3
"""Surveille le job C1 (flash). Si completed: telecharge la video + frames. Sinon: statut + ledger. Notification a la sortie."""
import datetime, json, os, subprocess, time
from pathlib import Path

D = Path('/home/ubuntu/ops-tools/seedance-bypass/cas/foot-reprise-20261024')
OUT = D / 'out'; OUT.mkdir(exist_ok=True)
env = dict(os.environ)
env['PATH'] = os.path.expanduser('~/.local/bin') + ':' + os.path.expanduser('~/.npm-global/bin') + ':' + env['PATH']
JOB = (D / 'JOB-ID-C1.txt').read_text().strip()
TERMINAL = {'completed', 'ip_detected', 'nsfw', 'failed', 'error', 'canceled'}

def hf(a, t=120):
    return subprocess.run(['higgsfield', '--json'] + a, capture_output=True, text=True, timeout=t, env=env)

log = open(D / 'STATUS-LOG-C1.txt', 'a')

def emit(s):
    line = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%SZ ') + s
    print(line)
    log.write(line + '\n')
    log.flush()

for _ in range(80):
    r = hf(['generate', 'get', JOB])
    try:
        d = json.loads(r.stdout)
        st = d.get('status')
    except Exception:
        st = 'parse-err'; d = {}
    emit(f'{JOB} status={st}')
    if st in TERMINAL:
        (D / 'JOB-C1-TERMINAL.json').write_text(r.stdout)
        if st == 'completed':
            url = d.get('result_url') or d.get('min_result_url')
            emit('result_url: ' + str(url))
            if url:
                subprocess.run(['curl', '-sL', '-o', str(OUT / 'C1_result.mp4'), url], timeout=300)
                emit('telecharge: ' + str((OUT / 'C1_result.mp4').stat().st_size) + ' octets')
                try:
                    subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(OUT / 'C1_result.mp4')], capture_output=True, text=True, timeout=60)
                    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(OUT / 'C1_result.mp4'), '-vf', 'fps=1/6,scale=640:-1', str(OUT / 'C1_sheet.jpg')], timeout=180)
                    emit('frames ok: ' + str((OUT / 'C1_sheet.jpg').exists()))
                except Exception as e:
                    emit('frames err ' + str(e))
        tx = hf(['account', 'transactions', '--size', '12'])
        (D / 'TX-AFTER-C1.json').write_text(tx.stdout)
        try:
            t = json.loads(tx.stdout)
            for it in (t.get('items') or [])[:10]:
                emit('TX ' + str(it.get('created_at'))[:19] + ' ' + str(it.get('action')) + ' ' + str(it.get('credits')) + ' ' + str(it.get('display_name')))
        except Exception as e:
            emit('tx err ' + str(e))
        (D / 'RESULT-C1.txt').write_text('status=' + str(st) + ' at ' + datetime.datetime.now(datetime.timezone.utc).isoformat() + '\n')
        emit('DONE')
        break
    time.sleep(45)
else:
    emit('TIMEOUT-60min')
