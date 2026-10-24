import sys, json, time
sys.path.insert(0, '/home/ubuntu/ops-tools/seedance-bypass/tools')
from hf_mcp import call

def sc(r):
    return ((r.get('result') or {}).get('structuredContent') or {})

BASE = ("3D animated film style: a queen with silver hair in a loose braid, wearing a lavender and teal gown "
        "with a long cape, standing in a snowy forest; she turns to camera; slow push-in. No text.")

C = {
    'C0a-identique-meme-seed': (BASE, 905261752),
    'C0b-identique-seed-neuf': (BASE, None),
    'C1-sans-tresse': ("3D animated film style: a queen with silver hair flowing loosely over one shoulder, wearing a lavender and teal gown with a long cape, standing in a snowy forest; she turns to camera; slow push-in. No text.", None),
    'C2-sans-cape': ("3D animated film style: a queen with silver hair in a loose braid, wearing a lavender and teal gown, standing in a snowy forest; she turns to camera; slow push-in. No text.", None),
    'C3-sans-neige': ("3D animated film style: a queen with silver hair in a loose braid, wearing a lavender and teal gown with a long cape, standing in a quiet forest; she turns to camera; slow push-in. No text.", None),
    'C4-sans-queen': ("3D animated film style: a young woman with silver hair in a loose braid, wearing a lavender and teal gown with a long cape, standing in a snowy forest; she turns to camera; slow push-in. No text.", None),
    'C5-cheveux-blancs': ("3D animated film style: a queen with white hair in a loose braid, wearing a lavender and teal gown with a long cape, standing in a snowy forest; she turns to camera; slow push-in. No text.", None),
}

ids = {}
for k, (p, seed) in C.items():
    params = {'model': 'seedance_2_5', 'prompt': p, 'aspect_ratio': '9:16', 'duration': 5, 'resolution': '480p', 'draft': True}
    if seed is not None:
        params['seed'] = seed
    try:
        r = call('generate_video', {'params': params, 'context': 'accept refus V1'})
        jid = (sc(r).get('results') or [{}])[0].get('id')
        ids[k] = jid
        print('CREATE', k, jid, flush=True)
    except Exception as e:
        print('ERR', k, repr(e)[:300], flush=True)

json.dump(ids, open('/tmp/accept_ids.json', 'w'))
print('---', len(ids), 'jobs lances, polling ---', flush=True)

pend = set(ids)
final = {}
for i in range(60):
    time.sleep(15)
    for k in list(pend):
        try:
            st = sc(call('job_status', {'jobId': ids[k]})).get('generation', {})
            s = st.get('status')
            if s and s not in ('in_progress', 'queued', 'pending'):
                final[k] = [s, st.get('result_url')]
                pend.discard(k)
                print('FIN', k, s, st.get('result_url'), flush=True)
        except Exception as e:
            print('ERRPOLL', k, repr(e)[:200], flush=True)
    print('tick', i, 'restant', len(pend), flush=True)
    if not pend:
        break

print('RESULT', json.dumps(final), flush=True)
json.dump(final, open('/tmp/accept_final.json', 'w'))
