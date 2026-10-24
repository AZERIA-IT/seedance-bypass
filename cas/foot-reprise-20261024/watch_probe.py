#!/usr/bin/env python3
"""Surveille le job c8aaf9dc jusqu'au statut terminal (<= 60 min), journalise, puis lit le ledger."""
import datetime, json, os, subprocess, time
from pathlib import Path

D = Path('/home/ubuntu/ops-tools/seedance-bypass/cas/foot-reprise-20261024')
env = dict(os.environ)
env['PATH'] = os.path.expanduser('~/.local/bin') + ':' + os.path.expanduser('~/.npm-global/bin') + ':' + env['PATH']
JOB = (D / 'JOB-ID.txt').read_text().strip()
TERMINAL = {'completed', 'ip_detected', 'nsfw', 'failed', 'error', 'canceled'}

def hf(a, t=120):
    return subprocess.run(['higgsfield', '--json'] + a, capture_output=True, text=True, timeout=t, env=env)

log = open(D / 'STATUS-LOG.txt', 'a')

def emit(s):
    line = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%SZ ') + s
    print(line)
    log.write(line + '\n')
    log.flush()

for _ in range(60):
    r = hf(['generate', 'get', JOB])
    try:
        d = json.loads(r.stdout)
        st = d.get('status')
    except Exception:
        st = 'parse-err'
    emit(f'{JOB} status={st}')
    if st in TERMINAL:
        (D / 'JOB-TERMINAL.json').write_text(r.stdout)
        tx = hf(['account', 'transactions', '--size', '20'])
        (D / 'TX-AFTER.json').write_text(tx.stdout)
        try:
            t = json.loads(tx.stdout)
            for it in (t.get('items') or [])[:12]:
                emit('TX ' + str(it.get('created_at'))[:19] + ' ' + str(it.get('action')) + ' ' + str(it.get('credits')) + ' ' + str(it.get('display_name')))
        except Exception as e:
            emit('tx parse err ' + str(e))
        (D / 'RESULT.txt').write_text('status=' + str(st) + ' at ' + datetime.datetime.now(datetime.timezone.utc).isoformat() + '\n')
        emit('DONE')
        break
    time.sleep(60)
else:
    emit('TIMEOUT-60min')
