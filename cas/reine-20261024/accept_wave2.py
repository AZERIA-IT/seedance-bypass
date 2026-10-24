import sys, json, time
sys.path.insert(0, '/home/ubuntu/ops-tools/seedance-bypass/tools')
from hf_mcp import call

def sc(r):
    return ((r.get('result') or {}).get('structuredContent') or {})

# Meme scene que C3, mais on essaie de garder la neige
D = {
    'D1-hiver': "3D animated film style: a queen with silver hair in a loose braid, wearing a lavender and teal gown with a long cape, standing in a winter forest; she turns to camera; slow push-in. No text.",
    'D2-legere-neige': "3D animated film style: a queen with silver hair in a loose braid, wearing a lavender and teal gown with a long cape, standing in a forest with light snow; she turns to camera; slow push-in. No text.",
    'D3-pins-enneiges': "3D animated film style: a queen with silver hair in a loose braid, wearing a lavender and teal gown with a long cape, standing in a snowy pine forest; she turns to camera; slow push-in. No text.",
}

ids = {}
for k, p in D.items():
    params = {'model': 'seedance_2_5', 'prompt': p, 'aspect_ratio': '9:16', 'duration': 5, 'resolution': '480p', 'draft': True}
    try:
        r = call('generate_video', {'params': params, 'context': 'accept refus V1 - garder la neige'})
        jid = (sc(r).get('results') or [{}])[0].get('id')
        ids[k] = jid
        print('CREATE', k, jid, flush=True)
    except Exception as e:
        print('ERR', k, repr(e)[:300], flush=True)

json.dump(ids, open('/tmp/accept_ids_D.json', 'w'))
pend = set(ids)
final = {}
for i in range(40):
    time.sleep(15)
    for k in list(pend):
        try:
            st = sc(call('job_status', {'jobId': ids[k]})).get('generation', {})
            s = st.get('status')
            if s and s not in ('in_progress', 'queued', 'pending'):
                final[k] = s
                pend.discard(k)
                print('FIN', k, s, flush=True)
        except Exception as e:
            print('ERRPOLL', k, repr(e)[:200], flush=True)
    if not pend:
        break
print('RESULT', json.dumps(final), flush=True)
json.dump(final, open('/tmp/accept_final_D.json', 'w'))
