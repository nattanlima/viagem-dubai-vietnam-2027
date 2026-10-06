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
assert [r['id'] for r in day['route']]==['rove','mall','rove','dxb'], 'Dia 14 precisa ficar a pé perto do hotel'
assert not {'burj','madinat','pai'} & {e['id'] for e in day['events']}, 'Dia 14 sem compromissos marcados'
assert any(e['id']=='rove' and e['time']=='11:30–12:00' for e in day['events'])
assert any(e['id']=='rove' and e['time']=='22:15–23:15' and 'retirar' in e['duration'].replace('retirada','retirar') for e in day['events'])
assert day['events'][-1]['id']=='dxb' and day['events'][-1]['time'].startswith('23:15')
assert 'sem quarto/banho' in day['warning']
for n,ids in ((21,{'madinat','pai'}),(24,{'burj'})):
    assert ids <= {e['id'] for e in next(d for d in data['days'] if d['n']==n)['events']}, f'Passeio movido ausente em {n}/02'
assert {e['id'] for d in data['days'] for e in d['events']}==set(data['items'])-{'train'}, 'Nenhum passeio pode sair do roteiro'
assert data['items']['base']['name'].startswith('Acoustic') and 'Peridot' not in data['items']['base']['name']
assert all(leg['checked']!='OFFLINE' for legs in routes.values() for leg in legs), 'Rotas falsas do modo offline'
assert len(photos)==45 and set(photos)==set(data['items'])
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
assert sum(map(len,routes.values()))==69
lunch_day=next(day for day in data['days'] if day['n']==20)
assert any(e['id']=='huonglien' and e['time']=='12:30–13:45' for e in lunch_day['events'])
assert [leg['b'] for leg in routes['20']][1:4]==['hoalo','huonglien','national']
assert lunch_day['events'][-1]['id']=='han' and lunch_day['events'][-1]['time']=='20:15'
assert next(e for e in lunch_day['events'] if e['id']=='spice')['time']=='18:00'
assert '24 Le Van Huu' in data['items']['huonglien']['query']
print('PASS: public artifact; light 14/02 with baggage pickup; Burj 24/02 and Madinat + Pai Thai 21/02; Acoustic base; no tour removed; 45 photos; 69 routed legs.')
