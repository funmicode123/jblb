import os, requests
ANOMA_REST = os.getenv('ANOMA_REST_ENDPOINT','')
def publish_intent(intent):
    if not ANOMA_REST:
        # mock
        return {'mock': True, 'type': intent.get('type'), 'match_id': 'mock-' + intent.get('type','')}
    url = ANOMA_REST.rstrip('/') + '/intents'
    resp = requests.post(url, json=intent, timeout=10)
    resp.raise_for_status()
    return resp.json()
