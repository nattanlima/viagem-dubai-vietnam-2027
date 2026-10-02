# Dubai e Vietnã · fevereiro de 2027

Apresentação interativa de uma viagem a dois, com roteiro por dia, fotografias dos locais, trajetos pelas ruas e avisos de horário, acesso e reserva.

**[Abrir a apresentação](https://nattanlima.github.io/viagem-dubai-vietnam-2027/)**

## O que há no projeto

- Quinze dias de viagem, entre 11 e 25 de fevereiro de 2027.
- Fotos identificadas de 44 locais, com ampliação e créditos.
- Setenta trechos calculados para carro e caminhada, incluindo restaurantes, hotéis e aeroportos.
- Mapa interativo com OpenFreeMap / OpenStreetMap, via MapLibre GL JS.
- Avisos em vermelho para horários, reservas e restrições que exigem atenção.
- Download de uma cópia da apresentação; roteiro e fotos disponíveis offline.

O mapa completo e os links externos precisam de internet. Tempos de deslocamento não incluem trânsito ao vivo, filas ou esperas. Hotéis, mesas e ingressos apresentados como propostas continuam sujeitos a confirmação.

## Dia 14/02: checkout antes do voo para Hanói

| Horário local | Programa |
| --- | --- |
| Até 11h30 | Café, banho e organização das malas no hotel |
| 11h30–12h | Checkout; deixar as malas na guarda do hotel |
| 12h15–13h | Almoço leve no Dubai Mall e acesso ao Burj |
| 13h30–15h30 | Burj Khalifa, sessão proposta a reservar |
| 16h15–18h45 | Madinat Jumeirah, com pausas |
| 19h30–21h30 | Pai Thai, sujeito a reserva e calendário de 14/02/Ramadã |
| 22h15 | Voltar ao hotel, retirar e conferir as malas |
| 23h15 | Transfer do hotel para DXB Terminal 3 |
| Por volta de 00h de 15/02 | Chegada planejada ao aeroporto; voo às 03h40 |

Após o checkout, o roteiro não conta com acesso ao quarto ou banho. A primeira estadia em Dubai considera 11–14/02, três diárias, com chegada após meia-noite de 12/02. O hotel indicado no mapa permanece uma sugestão.

## Executar e editar

O arquivo `index.html` é uma distribuição completa, com bibliotecas, fotos e dados incorporados. Pode ser aberto diretamente no navegador ou servido localmente:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Abra `http://127.0.0.1:8000/`. Para editar, altere os arquivos em `src/` e `data/`, depois gere novamente:

```sh
python scripts/build.py
python tests/check_release.py
npm ci
npm test
```

`data/itinerary.json` define o roteiro; `data/routes.json` contém os percursos já calculados. Uma alteração de pontos ou ordem de visita requer atualizar também as rotas. O build não consulta serviços de roteamento nem faz reservas.

## Fontes e conteúdo público

Fontes de pesquisa e créditos fotográficos estão na apresentação. Referências privadas da planilha, comprovantes de voo, códigos de reserva, capturas pessoais e material intermediário não fazem parte deste repositório. A versão pública contém as datas e o roteiro proposto.

Consulte [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) para atribuições e condições dos materiais de terceiros. A publicação do repositório não transfere os direitos das fotografias.
