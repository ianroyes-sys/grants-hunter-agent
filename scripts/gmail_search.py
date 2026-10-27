"""List Gmail messages matching a query, one line each, for the follow-up step.

usage: python3 scripts/gmail_search.py 'from:(program.org OR other.org) newer_than:2d'
Needs the Google Workspace CLI (`gws`) signed in to the inbox that receives program mail. Read-only.
"""
import json, subprocess, sys

q = sys.argv[1]


def call(*a):
    r = subprocess.run(['gws', 'gmail', 'users', 'messages', *a], capture_output=True, text=True)
    s = r.stdout
    return json.loads(s[s.find('{'):])


L = call('list', '--params', json.dumps({"userId": "me", "q": q, "maxResults": 30}))
for m in L.get('messages', []):
    i = m['id'].strip()
    try:
        d = call('get', '--params', json.dumps({"userId": "me", "id": i, "format": "metadata"}))
        h = {x['name']: x['value'] for x in d['payload']['headers']}
        print(i, '|', h.get('Date', '')[:22], '|', h.get('From', '')[:45], '|', h.get('Subject', '')[:80], '|', d.get('snippet', '')[:100])
    except Exception as e:
        print(i, 'ERR', e)
