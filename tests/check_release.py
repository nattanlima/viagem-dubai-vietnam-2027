"""Check the public artifact and the checkout/baggage itinerary constraints."""
import base64
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
read=lambda name:json.loads((ROOT/name).read_text('utf-8'))
data=read('data/itinerary.json')
routes=read('data/routes.json')
photos=read('data/photos.json')
html=(ROOT/'index.html').read_text('utf-8')
assert not data.get('sheet'), 'Private spreadsheet link must not be published'
for text in [html,(ROOT/'src/presentation.template').read_text('utf-8')]:
    assert 'docs.google.com/spreadsheets/' not in text
    assert 'C:/Users/' not in text and 'C:\\Users\\' not in text
    assert 'quarto mantido' not in text
    assert '11–15/02' not in text

day=next(d for d in data['days'] if d['n']==14)
assert [r['id'] for r in day['route']][-3:]==['pai','rove','dxb']
assert any(e['id']=='rove' and e['time']=='11:30–12:00' for e in day['events'])
assert any(e['id']=='rove' and e['time']=='22:15–23:15' and 'retirar' in e['duration'].replace('retirada','retirar') for e in day['events'])
assert day['events'][-1]['id']=='dxb' and day['events'][-1]['time'].startswith('23:15')
assert 'sem quarto/banho' in day['warning']
assert len(photos)==44 and set(photos)==set(data['items'])
for key,photo in photos.items():
    raw=base64.b64decode(photo['src'].split(',',1)[1],validate=True)
    assert raw.startswith(b'\xff\xd8') and raw.endswith(b'\xff\xd9'),key
    assert photo['src'] in html and photo['source'].startswith('https://')
for day in data['days']:
    if day['n']==11:continue
    legs=routes[str(day['n'])]
    assert len(legs)==len(day['route'])-1
    assert set(e['id'] for e in day['events']) <= set(r['id'] for r in day['route'])
    for i,leg in enumerate(legs):
        assert (leg['a'],leg['b'])==(day['route'][i]['id'],day['route'][i+1]['id'])
        assert len(leg['coordinates'])>2 and leg['distance']>0
assert sum(map(len,routes.values()))==70
print('PASS: public artifact; no private sheet/local paths; checkout 12h; baggage return before DXB; 44 photos; 70 routed legs.')
