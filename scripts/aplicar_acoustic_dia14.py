"""Aplica as decisões de 06/10/2026 ao projeto.

1. Hanói: troca a base pelo Acoustic Hotel & Spa (39 Thợ Nhuộm).
2. Dubai: 14/02 vira um dia sem compromisso, a pé perto do hotel, antes do voo.
   Nenhum passeio sai do roteiro: Burj Khalifa vai para 24/02 e
   Madinat + Pai Thai vão para a noite de 21/02.
3. Recalcula todos os trechos novos ou que tocam o hotel no mesmo servidor
   OSRM já usado (routing.openstreetmap.de) e reaproveita os demais.
4. Gera a imagem do hotel no estilo do site.

Uso: python scripts/aplicar_acoustic_dia14.py  (precisa de internet para as rotas)
     python scripts/aplicar_acoustic_dia14.py --offline  (só dados e textos; teste local)
"""
import base64, glob, io, json, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = '2026-10-06'
OFFLINE = '--offline' in sys.argv
OSRM = 'https://routing.openstreetmap.de/routed-{p}/route/v1/{p}/{a};{b}?overview=full&geometries=geojson&steps=true&generate_hints=false'


def load(name):
    return json.loads((ROOT / name).read_text('utf-8'))


def dump(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), 'utf-8')


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f'[{label}] esperava 1 ocorrência, achei {n}: {old[:80]!r}')
    return text.replace(old, new)


# ---------------------------------------------------------------- itinerário
data = load('data/itinerary.json')
items = data['items']
if items['base']['name'].startswith('Acoustic'):
    print('Dados já aplicados; seguindo para rotas, imagem e build.')
    APPLIED = True
else:
    APPLIED = False

if not APPLIED:
    items['base'] = {
        'id': 'base',
        'name': 'Acoustic Hotel & Spa · hotel escolhido',
        'source': 'https://www.booking.com/hotel/vn/acoustic-amp-spa.pt-pt.html',
        'extraSource': 'https://www.tripadvisor.com/Hotel_Review-g293924-d15829479-Reviews-Acoustic_Hotel_Spa-Hanoi.html',
        'why': 'Escolhido pelo casal em 06/10/2026. Avaliação alta e consistente (4,7 no Google, 1.573 avaliações, consulta 06/10/2026) e equipe muito elogiada. Fica a cerca de 600 m da base anterior, mais perto de Hỏa Lò, La Badiane, Tầm Vị e Gia.',
        'hours': 'Check-in 14h, checkout 12h. Saída tardia e entrada cedo custam 50% da diária, sujeitas a disponibilidade, segundo a Hotels.com.',
        'price': 'Sem cotação registrada para 15 a 21/02/2027. Conferir total com taxas; a Hotels.com informa 3% de taxa para pagamento com cartão no hotel.',
        'book': 'Reservar Premier Suite (cerca de 40 m², janela) ou quarto no prédio Acoustic Premium. Evitar o Deluxe, a categoria mais compacta (18 m² segundo o próprio hotel). Pedir quarto de fundos. Comparar 6 diárias com 5 diárias + saída tardia garantida até 17h30.',
        'tip': '39 Thợ Nhuộm, Cửa Nam. A rua da frente tem trânsito desde cedo; alguns quartos internos são escuros. A Hotels.com informa que o prédio não tem elevador: confirmar antes de reservar, por causa das malas.',
        'query': 'Acoustic Hotel & Spa 39 Tho Nhuom Hanoi',
        'kind': 'Hotel',
        'status': 'Escolhido · reservar',
        'cost': None,
        'currency': None,
        'xy': [105.84458029999999, 21.0276833],
        'geo': 'https://www.google.com/maps/search/?api=1&query=Acoustic+Hotel+%26+Spa+Hanoi&query_place_id=ChIJPX0v8JarNTERizl6YUwG558',
        'checked': TODAY,
        'alerts': [
            {'title': 'Categoria e elevador', 'text': 'Reservar Premier Suite ou Acoustic Premium, com janela e de fundos. Confirmar por escrito se há elevador para o andar do quarto.'},
            {'title': '20/02: quarto até 17h30', 'text': 'Checkout padrão às 12h. Garantir por escrito a 6ª diária ou a saída tardia até 17h30; malas guardadas até a saída às 20h15.'},
        ],
    }

    items['burj']['alerts'] = [{'title': 'Sessão com hora marcada', 'text': 'Proposta para 24/02 às 14h, saindo do dia do voo para o Vietnã. Comprar a sessão com data certa e estar no acesso às 13h30 (margem nossa).'}]
    items['pai']['hours'] = 'Referência oficial atual: jantar diário 17h–22h30. Confirmar funcionamento durante o Ramadã.'
    items['pai']['tip'] = 'Proposta para 21/02 às 19h30, terminando até 21h30, depois do passeio por Madinat. Volta de carro ao hotel.'
    items['pai']['alerts'] = [
        {'title': 'Reserva pendente', 'text': 'Reservar mesa para 2 e confirmar horário, cancelamento e valor total antes de assumir o compromisso.'},
        {'title': '21/02: noite após o voo', 'text': 'Confirmar mesa às 19h30 e funcionamento no Ramadã. Se o cansaço pesar depois do voo noturno, encurtar Madinat e manter o jantar.'},
    ]

    days = {d['n']: d for d in data['days']}

    d15 = days[15]
    for e in d15['events']:
        if e['id'] == 'base':
            e['note'] = 'Check-in no Acoustic (a partir das 14h) e descanso.'

    days[14].update({
        'title': 'Checkout, Downtown a pé e voo para o Vietnã',
        'intro': 'Dia sem hora marcada. Depois do checkout tudo fica a poucos minutos a pé do hotel, para voltar às malas sem pressa e seguir para DXB.',
        'events': [
            {'time': '09:00–11:30', 'id': 'rove', 'duration': 'café e organização', 'note': 'Tomar banho, trocar de roupa e fechar as malas antes de entregar o quarto.'},
            {'time': '11:30–12:00', 'id': 'rove', 'duration': 'checkout e guarda das malas', 'note': 'Sair do quarto às 12h. Deixar malas no hotel, obter comprovante e combinar retirada às 22h15. Levar documentos, medicamentos e itens de mão.'},
            {'time': '12:30–17:30', 'id': 'mall', 'duration': 'almoço e passeio sem pressa', 'note': 'Dubai Mall a pé desde o hotel. Almoço tranquilo, Burj Khalifa por fora e pausas em cafés. Sem ingresso nem reserva; dá para voltar ao lobby do hotel a qualquer momento.'},
            {'time': '18:00–21:30', 'id': 'mall', 'duration': 'fontes e jantar sem reserva', 'note': 'Show das fontes (programação do Ramadã a confirmar) e jantar casual na região do Dubai Mall, sem mesa marcada. É Dia dos Namorados e Ramadã: depois do iftar os restaurantes enchem, então escolher lugar com fila curta. Encerrar até 21h30.'},
            {'time': '22:15–23:15', 'id': 'rove', 'duration': 'retirada das malas e saída', 'note': 'Voltar a pé. Retirar e conferir as malas até 22h45; combinar pequena espera no saguão. Sem quarto ou banho. Motorista no hotel às 23h15.'},
            {'time': '23:15 → 00:00', 'id': 'dxb', 'duration': 'transfer de 30–45min', 'note': 'Origem: hotel, já com as malas. Alvo DXB T3 por volta de 00h de 15/02; voo EK394 às 03h40. Margem para trânsito e embarque.'},
        ],
        'route': [
            {'id': 'rove', 'profile': 'start', 'mode': 'Início'},
            {'id': 'mall', 'profile': 'foot', 'mode': 'A pé'},
            {'id': 'rove', 'profile': 'foot', 'mode': 'A pé'},
            {'id': 'dxb', 'profile': 'car', 'mode': 'Carro / táxi'},
        ],
        'tips': [
            'Nenhum ingresso, mesa ou hora marcada neste dia: o único compromisso é o voo.',
            'Tomar banho e separar roupas antes do checkout; depois das 12h o plano não conta com quarto.',
            'Guardar o comprovante das malas e alinhar a retirada às 22h15 com a recepção. Documentos e medicamentos ficam com vocês.',
            'Confirmar o motorista hotel → DXB T3 às 23h15.',
            'Burj Khalifa foi para 24/02 e Madinat + Pai Thai para a noite de 21/02.',
        ],
        'warning': '14/02: checkout às 12h; malas no hotel. Dia sem compromissos, tudo a pé perto do hotel. Retorno às 22h15 para retirada, sem quarto/banho. Saída ao aeroporto às 23h15; voo 03h40 de 15/02.',
    })

    days[21].update({
        'title': 'Volta a Dubai, descanso e noite em Madinat',
        'intro': 'EK395 pousa às 05h. Dormir até a tarde; à noite, canais de Madinat e jantar no Pai Thai.',
        'events': [
            {'time': '05:00', 'id': 'dxb', 'duration': '1h–2h', 'note': ''},
            {'time': '07:00 aprox.', 'id': 'rove', 'duration': 'descanso', 'note': 'Acesso ao quarto somente com entrada cedo garantida ou diária 20→21. Sair por volta de 15h30.'},
            {'time': '16:15–18:45', 'id': 'madinat', 'duration': 'passeio com pausas', 'note': 'Prever 30–45min de carro desde Downtown. Caminhar pelos canais com pausas e ficar na região do jantar. Veio do dia 14.'},
            {'time': '19:30–21:30', 'id': 'pai', 'duration': 'jantar de 2h', 'note': 'Mesa a confirmar. Verificar funcionamento no Ramadã. Veio do dia 14.'},
            {'time': '22:15', 'id': 'rove', 'duration': 'descanso', 'note': 'Volta de carro ao hotel.'},
        ],
        'route': [
            {'id': 'dxb', 'profile': 'start', 'mode': 'Início'},
            {'id': 'rove', 'profile': 'car', 'mode': 'Carro / táxi'},
            {'id': 'madinat', 'profile': 'car', 'mode': 'Carro / táxi'},
            {'id': 'pai', 'profile': 'foot', 'mode': 'A pé'},
            {'id': 'rove', 'profile': 'car', 'mode': 'Carro / táxi'},
        ],
        'tips': [
            'Não programar nada antes do meio da tarde depois do voo noturno.',
            'Confirmar entrada cedo antes de pagar tarifa; recepção 24h não significa quarto disponível.',
            'Se o cansaço pesar, encurtar Madinat e manter o jantar; Madinat → Pai Thai é a pé.',
            'Dubai Mall e Thiptara continuam nos dias 12 e 24.',
        ],
        'warning': 'Rove só garante check-in padrão às 16h. Madinat e Pai Thai vieram do dia 14 para liberar o dia do voo.',
    })

    days[24].update({
        'title': 'Burj Khalifa, Dubai Mall e malas prontas',
        'intro': 'Museu do Futuro opcional de manhã, mirante do Burj à tarde e jantar perto da base. Amanhã o voo é cedo.',
        'events': [
            {'time': '10:30 opcional', 'id': 'future', 'duration': '2h', 'note': 'Somente se reaberto; pode ser substituído por passeio curto na Palm.'},
            {'time': '12:30', 'id': 'mall', 'duration': 'almoço e compras finais', 'note': 'Almoço perto do acesso At the Top.'},
            {'time': '14:00–16:00', 'id': 'burj', 'duration': 'até 2h', 'note': 'Sessão a reservar; estar no acesso às 13h30. Veio do dia 14. Depois, tempo livre a pé até o jantar.'},
            {'time': '18:00', 'id': 'thiptara', 'duration': '1h30', 'note': 'Sugestão perto da base; pode trocar por outro restaurante central.'},
            {'time': '20:00', 'id': 'rove', 'duration': 'malas e sono', 'note': ''},
        ],
        'route': [
            {'id': 'rove', 'profile': 'start', 'mode': 'Início'},
            {'id': 'future', 'profile': 'car', 'mode': 'Carro / táxi'},
            {'id': 'mall', 'profile': 'car', 'mode': 'Carro / táxi'},
            {'id': 'burj', 'profile': 'foot', 'mode': 'A pé'},
            {'id': 'thiptara', 'profile': 'foot', 'mode': 'A pé'},
            {'id': 'rove', 'profile': 'car', 'mode': 'Carro / táxi'},
        ],
        'tips': [
            'Conferir terminal, bagagem e transfer da madrugada.',
            'Comprar a sessão do Burj das 14h com a data certa. Se o Museu do Futuro não reabrir, a manhã fica livre para arrumar as malas.',
            'Evitar safari, Abu Dhabi e Global Village até tarde.',
        ],
        'warning': 'Burj com sessão marcada às 14h. O traçado inclui o Museu do Futuro como parada condicional; se não reabrir, pular essa parada.',
    })

    data['revision'] = 'Acoustic Hotel & Spa como base em Hanói; 14/02 sem compromissos, Burj em 24/02 e Madinat + Pai Thai em 21/02 · 06/10/2026'
    data['updatedAt'] = TODAY
    dump('data/itinerary.json', data)

    # ---------------------------------------------------------- textos do site
    p = ROOT / 'src/presentation.template'
    t = p.read_text('utf-8')
    t = replace_once(t, '<p>Downtown, Frame, Al Fahidi e Creek. Jumeirah antes do voo para o Vietnã.</p>',
                     '<p>Downtown, Frame, Al Fahidi e Creek. Dia 14 leve, a pé perto do hotel, antes do voo para o Vietnã.</p>', 'overview 12-14')
    t = replace_once(t, '<p>Marina/JBR e parques no mesmo eixo. Dia 24 leve; voo de volta na manhã de 25/02.</p>',
                     '<p>Madinat na noite de chegada, Marina/JBR e parques. Burj Khalifa no dia 24; voo de volta na manhã de 25/02.</p>', 'overview 21-24')
    t = replace_once(t, 'Roteiro atualizado em 05/10/2026', 'Roteiro atualizado em 06/10/2026', 'data')
    t = replace_once(t, '<li><b>12 e 21:</b> descanso e jantar flexível após os voos.</li>',
                     '<li><b>12:</b> descanso e jantar flexível após o voo.</li><li><b>21:</b> descanso até a tarde; Madinat e Pai Thai à noite, com mesa reservada.</li>', 'ramadã 12/21')
    t = replace_once(t, '<li><b>14:</b> checkout às 12h, malas guardadas no hotel, jantar e retorno para retirar a bagagem às 22h15; transfer às 23h15.</li>',
                     '<li><b>14:</b> checkout às 12h e malas guardadas no hotel. Dia sem reservas, a pé perto do hotel; retirada da bagagem às 22h15 e transfer às 23h15.</li>', 'ramadã 14')
    t = replace_once(t, '<li><b>24:</b> jantar próximo da base e dormir cedo para sair às 04h15–04h30.</li>',
                     '<li><b>24:</b> Burj às 14h, jantar próximo da base e dormir cedo para sair às 04h15–04h30.</li>', 'ramadã 24')
    t = replace_once(t, '<li>Dia 14: Burj após o checkout, com sessão proposta às 13h30; Museu do Futuro condicional.</li>',
                     '<li>Dia 14 sem compromissos: Burj passou para 24/02 (sessão 14h) e Madinat + Pai Thai para a noite de 21/02. Museu do Futuro condicional.</li>', 'revisão 14')
    old_card = t[t.index('<article class="card"><span class="badge">Hanói · conforto para o casal</span>'):]
    old_card = old_card[:old_card.index('</article>') + len('</article>')]
    new_card = ('<article class="card"><span class="badge">Hanói · escolhido pelo casal</span><h3>Acoustic Hotel &amp; Spa</h3>'
                '<p>Boutique de 66 quartos em 39 Thợ Nhuộm, a cerca de 600 m da base anterior. Equipe muito elogiada; as categorias de entrada são pequenas.</p>'
                '<ul><li><b>Categoria:</b> Premier Suite (cerca de 40 m², janela) ou prédio Acoustic Premium. Evitar o Deluxe, de 18 m².</li>'
                '<li><b>Barulho:</b> pedir quarto de fundos; a rua da frente tem trânsito desde cedo.</li>'
                '<li><b>15–21/02:</b> check-in 14h. Para 20/02, 6ª diária ou saída tardia até 17h30 garantida por escrito (a Hotels.com informa 50% da diária).</li>'
                '<li><b>Confirmar:</b> elevador até o andar do quarto; a Hotels.com informa que o prédio não tem.</li></ul>'
                '<p class="small">Sem cotação registrada. 4,7 no Google com 1.573 avaliações, consulta de 06/10/2026.</p>'
                '<div class="links"><a href="https://www.booking.com/hotel/vn/acoustic-amp-spa.pt-pt.html" target="_blank" rel="noopener">Booking ↗</a>'
                '<a href="https://www.tripadvisor.com/Hotel_Review-g293924-d15829479-Reviews-Acoustic_Hotel_Spa-Hanoi.html" target="_blank" rel="noopener">Avaliações ↗</a></div></article>')
    t = replace_once(t, old_card, new_card, 'card Hanói')
    t = replace_once(t, '<h3>As alternativas que já estão na planilha</h3>', '<h3>Alternativas avaliadas antes da escolha</h3>', 'tabela título')
    t = replace_once(t, '<tbody><tr><td><a href="https://jmmarvelhotel.com',
                     '<tbody><tr><td><a href="https://peridotgrandhotel.com/room/premier-deluxe/" target="_blank" rel="noopener">Peridot Grand Premier Deluxe</a></td><td>28–32 m², janela externa; base anterior dos mapas</td><td>Sem preço verificável</td><td>Sem cotação</td></tr><tr><td><a href="https://jmmarvelhotel.com', 'tabela Peridot')
    p.write_text(t, 'utf-8')

    p = ROOT / 'src/app.js'
    a = p.read_text('utf-8')
    if a.count(".replace(' — hotel sugerido','')") != 2:
        raise SystemExit('app.js: padrão do nome do hotel mudou')
    a = a.replace(".replace(' — hotel sugerido','')", ".replace(/ (—|·) hotel (sugerido|escolhido)$/,'')")
    a = replace_once(a, "'Comparar Peridot com JM Junior e La Siesta nas mesmas datas'",
                     "'Reservar o Acoustic: Premier Suite ou Premium, de fundos, e confirmar elevador'", 'tarefa hotel')
    a = replace_once(a, "'Reservar motorista de Ninh Bình e transfers dos voos'];",
                     "'Reservar motorista de Ninh Bình e transfers dos voos','Reservar Pai Thai em 21/02 e sessão do Burj em 24/02 às 14h'];", 'tarefa burj')
    a = replace_once(a, 'Hương Liên e seus trechos incluídos em 05/10/2026.',
                     'Hương Liên e seus trechos incluídos em 05/10/2026; Acoustic Hotel &amp; Spa e novo dia 14 em 06/10/2026.', 'fontes')
    p.write_text(a, 'utf-8')

    p = ROOT / 'README.md'
    r = p.read_text('utf-8')
    r = replace_once(r, 'Setenta e um trechos calculados', 'Sessenta e nove trechos calculados', 'readme trechos')
    i = r.index('## Dia 14/02: checkout antes do voo para Hanói')
    j = r.index('## Dia 20/02')
    r = r[:i] + '''## Dia 14/02: dia leve antes do voo para Hanói

| Horário local | Programa |
| --- | --- |
| Até 11h30 | Café, banho e organização das malas no hotel |
| 11h30–12h | Checkout; deixar as malas na guarda do hotel |
| 12h30–17h30 | Dubai Mall a pé: almoço sem pressa, Burj por fora e cafés |
| 18h–21h30 | Fontes e jantar casual sem reserva na região |
| 22h15 | Voltar a pé ao hotel, retirar e conferir as malas |
| 23h15 | Transfer do hotel para DXB Terminal 3 |
| Por volta de 00h de 15/02 | Chegada planejada ao aeroporto; voo às 03h40 |

Nenhum passeio saiu do roteiro: o Burj Khalifa passou para 24/02 (sessão das 14h) e Madinat Jumeirah + Pai Thai para a noite de 21/02. Após o checkout, o roteiro não conta com acesso ao quarto ou banho. A primeira estadia em Dubai considera 11–14/02, três diárias, com chegada após meia-noite de 12/02. O hotel indicado no mapa permanece uma sugestão.

## Hotel em Hanói

**Acoustic Hotel & Spa**, 39 Thợ Nhuộm, escolhido em 06/10/2026 para 15–21/02. Reservar Premier Suite ou prédio Acoustic Premium, quarto de fundos, e garantir quarto até 17h30 em 20/02. Confirmar se há elevador. Ainda sem reserva.

''' + r[j:]
    p.write_text(r, 'utf-8')

# ---------------------------------------------------------------- imagem
def _font(name, size):
    from PIL import ImageFont
    for path in glob.glob(f'/usr/share/fonts/**/{name}', recursive=True):
        return ImageFont.truetype(path, size)
    raise SystemExit(f'Fonte {name} não encontrada (instale fonts-dejavu-core)')


def hotel_card():
    from PIL import Image, ImageDraw
    W, H, S = 900, 650, 2
    im = Image.new('RGB', (W * S, H * S), '#f7f5ef'); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W * S, 210 * S], fill='#235c4f')
    for i in range(7):
        x = 70 + i * 115
        d.rounded_rectangle([x * S, 62 * S, (x + 58) * S, 168 * S], radius=29 * S, fill='#2d6b5d')
        d.line([(x + 29) * S, 62 * S, (x + 29) * S, 168 * S], fill='#235c4f', width=3 * S)
    d.rectangle([0, 196 * S, W * S, 210 * S], fill='#e9d6b8')
    d.text((60 * S, 258 * S), 'HANÓI · HOTEL ESCOLHIDO', font=_font('DejaVuSans-Bold.ttf', 15 * S), fill='#235c4f')
    d.text((58 * S, 290 * S), 'Acoustic Hotel & Spa', font=_font('DejaVuSerif.ttf', 54 * S), fill='#172f35')
    d.text((60 * S, 372 * S), '39 Thợ Nhuộm · Cửa Nam', font=_font('DejaVuSans.ttf', 22 * S), fill='#53686a')
    d.line([60 * S, 425 * S, (W - 60) * S, 425 * S], fill='#dce2dc', width=2 * S)
    for i, (a, b) in enumerate([('15 → 21/02', 'estadia'), ('Premier Suite', 'categoria indicada'), ('300 m', 'da Prisão Hỏa Lò')]):
        x = 60 + i * 270
        d.text((x * S, 452 * S), a, font=_font('DejaVuSerif.ttf', 28 * S), fill='#172f35')
        d.text((x * S, 496 * S), b, font=_font('DejaVuSans.ttf', 16 * S), fill='#53686a')
    d.text((60 * S, 586 * S), 'Imagem ilustrativa do projeto. Fotos do hotel no link da reserva.', font=_font('DejaVuSans.ttf', 14 * S), fill='#53686a')
    im = im.resize((W, H), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=88, optimize=True)
    return buf.getvalue()


photos = load('data/photos.json')
if not photos['base'].get('title', '').startswith('Acoustic'):
    raw = hotel_card()
    photos['base'] = {
        'url': items['base']['source'],
        'source': items['base']['source'],
        'credit': 'Cartão ilustrativo do projeto',
        'license': 'Ilustração própria; sem foto de terceiros',
        'caption': 'Acoustic Hotel & Spa · 39 Thợ Nhuộm. Fotos do hotel no link da reserva.',
        'title': 'Acoustic Hotel & Spa · hotel escolhido',
        'src': 'data:image/jpeg;base64,' + base64.b64encode(raw).decode(),
    }
    dump('data/photos.json', photos)

# ---------------------------------------------------------------- rotas
old = load('data/routes.json')
reuse = {}
for legs in old.values():
    for leg in legs:
        if 'base' not in (leg['a'], leg['b']):
            reuse.setdefault((leg['a'], leg['b'], leg['profile']), leg)


def fetch(a, b, profile):
    pa, pb = items[a]['xy'], items[b]['xy']
    url = OSRM.format(p=profile, a=f'{pa[0]:.7f},{pa[1]:.7f}', b=f'{pb[0]:.7f},{pb[1]:.7f}')
    req = urllib.request.Request(url, headers={'User-Agent': 'viagem-dubai-vietnam-2027 (github.com/nattanlima)'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                js = json.load(res)
            break
        except Exception as exc:
            if attempt == 3:
                raise SystemExit(f'Falha ao calcular {a} → {b} ({profile}): {exc}')
            time.sleep(3 * (attempt + 1))
    route = js['routes'][0]
    steps = [s for leg in route['legs'] for s in leg['steps']]
    streets = []
    for s in steps:
        name = s.get('name') or ''
        if name and name not in streets:
            streets.append(name)
    ferries = []
    for s in steps:
        if s.get('mode') == 'ferry' and s.get('name') and s['name'] not in ferries:
            ferries.append(s['name'])
    time.sleep(1.2)  # respeitar o servidor público
    return {
        'a': a, 'b': b, 'profile': profile,
        'coordinates': [[round(x, 6), round(y, 6)] for x, y in route['geometry']['coordinates']],
        'distance': round(route['distance'], 1), 'duration': round(route['duration'], 1),
        'snaps': [w['distance'] for w in js['waypoints']], 'ferries': ferries,
        'source': url, 'streets': streets[:10], 'checked': TODAY,
    }


new_routes, fetched = {}, 0
for day in data['days']:
    legs = []
    for i in range(len(day['route']) - 1):
        a, b = day['route'][i]['id'], day['route'][i + 1]['id']
        profile = day['route'][i + 1]['profile']
        key = (a, b, profile)
        if key in reuse:
            legs.append(reuse[key])
        elif OFFLINE:
            pa, pb = items[a]['xy'], items[b]['xy']
            legs.append({'a': a, 'b': b, 'profile': profile, 'coordinates': [pa, [(pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2], pb],
                         'distance': 1, 'duration': 1, 'snaps': [0, 0], 'ferries': [], 'source': 'https://offline.invalid', 'streets': [], 'checked': 'OFFLINE'})
        else:
            legs.append(fetch(a, b, profile)); fetched += 1
    new_routes[str(day['n'])] = legs
dump('data/routes.json', new_routes)
total = sum(map(len, new_routes.values()))
print(f'Rotas: {total} trechos, {fetched} recalculados agora' + (' (OFFLINE: trechos falsos, não publicar)' if OFFLINE else ''))
