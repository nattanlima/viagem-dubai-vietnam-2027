const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link = (url,label) => `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`;
const mapsUrl = p => 'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(p.query);
let selected=16,legIndex=0,playing=false,raf=null,progress=0,last=0;
let currentPoints=[],currentLegs=[],liveMap=null,traveler=null,project=null,mapTimer=null,viewToken=0;
const photo = k => PHOTOS[k];
const dayData = () => DATA.days.find(x=>x.n===selected);
const hasAlert = k => Boolean(DATA.items[k].alerts?.length);
const warnings = p => (p.alerts||[]).map(a=>`<div class="attention"><b>⚠ ${esc(a.title)}</b><span>${esc(a.text)}</span></div>`).join('');
if(DATA.sheet){$('#sheet').href=DATA.sheet;}else{$('#sheet').hidden=true;}$('#heroDubai').src=MEDIA.dubai.src;$('#heroHanoi').src=MEDIA.hanoi.src;
const alternatives=document.querySelector('#review .card>details');
if(alternatives&&!alternatives.querySelector('.optional-photo')){const preview=document.createElement('div');preview.className='optional-photo';preview.innerHTML=`<img class="place-thumb" src="${PHOTOS.train.src}" alt="${esc(PHOTOS.train.caption)}"><span><b class="attention-label">⚠ Train Street: acesso restrito</b><button class="photo-open" data-photo="train">Ampliar foto</button></span>`;alternatives.appendChild(preview);}
$('#credits').innerHTML='<details><summary>Créditos das fotos e dos mapas</summary>'+Object.values(PHOTOS).map(m=>`<p>${esc(m.caption)} · ${esc(m.credit)} · ${esc(m.license)} · ${link(m.source,'Fonte da foto')}${m.licenseUrl?' · '+link(m.licenseUrl,'Licença'):''}</p>`).join('')+'<p>Mapas © OpenStreetMap contributors / OpenMapTiles / OpenFreeMap. Rotas OSRM, serviço FOSSGIS. MapLibre GL JS (BSD-3-Clause), D3 (ISC). Rotas calculadas em 02 e 05/10/2026, sem trânsito ao vivo.</p></details>';
$('#flights').innerHTML=[['11 fev · 03:45','GIG T2','12 fev · 00:35','DXB T3','EK248'],['15 fev · 03:40','DXB T3','15 fev · 12:55','HAN T2','EK394'],['21 fev · 00:35','HAN T2','21 fev · 05:00','DXB T3','EK395'],['25 fev · 08:05','DXB T3','25 fev · 15:55','GIG T2','EK247']].map(f=>`<div class="flight"><div>${f[0]}<strong>${f[1]}</strong></div><div class="small">${f[4]}<br>→</div><div class="arr">${f[2]}<strong>${f[3]}</strong></div></div>`).join('');
$('#credits details').insertAdjacentHTML('beforeend',Object.values(MEDIA).map(m=>`<p>Foto de abertura: ${esc(m.title)} · ${esc(m.credit)} · ${esc(m.license)} · ${link(m.url,'Fonte')}</p>`).join(''));
function panel(id){
  pause(); document.querySelectorAll('main>section').forEach(s=>s.hidden=s.id!==id);
  document.querySelectorAll('[data-panel]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.panel===id));
  if(id==='itinerary')renderDay();location.hash=id;
}
document.querySelectorAll('[data-panel]').forEach(b=>b.onclick=()=>panel(b.dataset.panel));
window.addEventListener('hashchange',()=>{const id=location.hash.slice(1);if(['overview','itinerary','ramadan','hotels','review'].includes(id)&&$('#'+id).hidden)panel(id);});
$('#start').onclick=()=>panel('itinerary');
function renderDays(){
  const list=DATA.days.filter(d=>$('#city').value==='all'||d.city===$('#city').value);
  if(!list.some(d=>d.n===selected))selected=list[0].n;
  $('#days').innerHTML=list.map(d=>`<button data-day="${d.n}" aria-pressed="${d.n===selected}" aria-label="${d.n} fevereiro, ${d.city}, ${esc(d.title)}"><span>${d.weekday}</span><b>${d.n}</b><span>${d.city==='Em trânsito'?'Voo':d.city}</span></button>`).join('');
  $('#days').querySelectorAll('button').forEach(b=>b.onclick=()=>{selected=+b.dataset.day;renderDays();renderDay();});
}
function eventHTML(e){
  const p=DATA.items[e.id],im=photo(e.id),alert=p.alerts?.length;
  return `<article class="event ${alert?'needs-attention':''}"><div class="time">${esc(e.time)}</div><details><summary><span class="event-top">${im?`<img class="place-thumb" loading="lazy" src="${im.src}" alt="${esc(im.caption)}">`:''}<span><span class="badge">${esc(p.kind)}</span><strong class="place-name">${esc(p.name)}</strong><span class="meta">${esc(e.duration)} · ${esc(p.status)}</span></span></span>${alert?`<span class="attention-label">⚠ ${esc(p.alerts.map(a=>a.title).join(' · '))}</span>`:''}${e.note?`<span class="meta">${esc(e.note)}</span>`:''}</summary><div class="detail-body">${warnings(p)}<p>${esc(p.why)}</p><p><strong>Funcionamento e calendário</strong>${esc(p.hours)} Reconfirmar para fevereiro de 2027.</p><p><strong>Valores de referência</strong>${esc(p.price)}</p><p><strong>Reserva / antecedência</strong>${esc(p.book)}</p><p><strong>Dica prática</strong>${esc(p.tip)}</p>${p.geoNote?`<p class="small">Ponto no mapa: ${esc(p.geoNote)}</p>`:''}<div class="links"><button class="photo-open" data-photo="${e.id}">Ampliar foto</button>${link(mapsUrl(p),'Google Maps')}${link(p.source,'Fonte / reservas')}${p.extraSource?link(p.extraSource,'Conferência adicional'):''}</div></div></details></article>`;
}
function renderDay(){
  pause();disposeMap();legIndex=0;progress=0;const d=dayData();
  const hero=d.events.find(e=>DATA.items[e.id].kind==='Passeio'&&photo(e.id))||d.events.find(e=>photo(e.id));
  const heroPhoto=hero?photo(hero.id):MEDIA.dubai;
  const alerts=[...new Set(d.events.map(e=>e.id))].filter(hasAlert);
  $('#day').innerHTML=`<div class="day-head"><div><div class="eyebrow">${d.weekday} · ${d.n} fevereiro de 2027 · ${d.city}</div><h2>${esc(d.title)}</h2><p class="section-lead" style="margin:12px 0">${esc(d.intro)}</p></div><img src="${heroPhoto.src}" alt="${esc(heroPhoto.caption||'Dubai')}"></div>${d.warning?`<div class="warning">${esc(d.warning)}</div>`:''}${alerts.length?`<details class="day-attention"><summary>⚠ ${alerts.length} locais com horário, reserva ou acesso que exigem atenção</summary>${alerts.map(k=>`<p><b>${esc(DATA.items[k].name)}:</b> ${esc(DATA.items[k].alerts.map(a=>a.title).join(' · '))}</p>`).join('')}</details>`:''}<div class="day-layout"><div><div id="events">${d.events.map(eventHTML).join('')||'<div class="card"><h3>Dia de voo</h3><p>EK248 · GIG 03h45 → DXB 00h35 do dia seguinte. A programação terrestre começa em 12/02.</p></div>'}</div><div class="tips"><h3>Para o dia funcionar bem</h3><ul>${d.tips.map(t=>'<li>'+esc(t)+'</li>').join('')}</ul></div></div><aside class="map-box"><div class="map-header"><div class="eyebrow">Mapa real · ruas e percursos</div><h3 style="margin-top:6px">O dia em movimento</h3><p class="small">Arraste e amplie o mapa. Clique nos pontos para identificar os locais.</p></div><div id="map" class="map"></div><div id="map-status" class="map-status" role="status">Carregando mapa…</div><div class="map-controls"><button id="play" class="primary">▶ Animar roteiro</button><button id="prev" aria-label="Trecho anterior">←</button><button id="next" aria-label="Próximo trecho">→</button><button id="reset">Recomeçar</button><button id="fit-leg">Ver trecho</button><button id="fit-day">Ver dia inteiro</button></div><div class="map-legend"><span>● Azul: carro</span><span>● Verde: a pé / travessia</span><span class="attention-label">⚠ Vermelho: atenção</span></div><div id="leg" class="leg" aria-live="polite"></div><p class="map-note">Percursos calculados pelas vias do OpenStreetMap em 02 e 05/10/2026. Sem trânsito ao vivo ou garantia de abertura futura. A rota chega ao acesso mapeado mais próximo; confirme a entrada no Google Maps. Trechos internos e o circuito de barco de Tràng An não são simulados.<br>${link('https://www.openstreetmap.org/copyright','© OpenStreetMap')}, ${link('https://openfreemap.org/','OpenFreeMap')} · ${link('https://routing.openstreetmap.de/about.html','Rotas FOSSGIS / OSRM')} · ${link('https://www.openstreetmap.org/fixthemap','Reportar erro no mapa')}</p></aside></div>`;
  $('#expand').textContent='Abrir todos os detalhes do dia';
  $('#play').onclick=()=>playing?pause():play();$('#prev').onclick=()=>step(-1);$('#next').onclick=()=>step(1);
  $('#reset').onclick=()=>{pause();legIndex=0;progress=0;updateLeg();};
  $('#fit-leg').onclick=()=>fitMap(false);$('#fit-day').onclick=()=>fitMap(true);
  currentLegs=ROUTES[String(selected)]||[];
  currentPoints=d.route.map((r,i)=>({...DATA.items[r.id],...r,xy:i===0?currentLegs[0]?.coordinates[0]:currentLegs[i-1]?.coordinates.at(-1)}));
  const token=viewToken;requestAnimationFrame(()=>{if(token===viewToken)drawMap();});
}
$('#city').onchange=()=>{renderDays();renderDay();};
$('#expand').onclick=()=>{const ds=[...document.querySelectorAll('#events details')],open=ds.some(d=>!d.open);ds.forEach(d=>d.open=open);$('#expand').textContent=open?'Recolher os detalhes do dia':'Abrir todos os detalhes do dia';};
function disposeMap(){viewToken++;clearTimeout(mapTimer);if(liveMap){liveMap.remove();liveMap=null;}traveler=null;project=null;}
function featureCollection(){return {type:'FeatureCollection',features:currentLegs.map((leg,i)=>({type:'Feature',properties:{index:i,profile:leg.profile,active:i===legIndex?1:0},geometry:{type:'LineString',coordinates:leg.coordinates}}))};}
function fitMap(all){
  if(!liveMap){if(currentLegs.length)drawFallback(!all);return;}
  const coords=all?currentLegs.flatMap(l=>l.coordinates):currentLegs[legIndex]?.coordinates;
  if(!coords?.length)return;
  const b=new maplibregl.LngLatBounds(coords[0],coords[0]);coords.forEach(p=>b.extend(p));
  liveMap.fitBounds(b,{padding:45,maxZoom:16,duration:300});
}
function drawMap(){
  if(!$('#map'))return;
  if(!currentLegs.length){$('#map').innerHTML='<div class="empty"><h3>Hoje o trajeto é aéreo</h3><p>GIG → DXB</p><p>Sem percurso terrestre programado.</p></div>';$('#map-status').textContent='Chegada a Dubai após meia-noite de 12/02.';['play','prev','next','reset','fit-leg','fit-day'].forEach(id=>$('#'+id).disabled=true);return;}
  const token=viewToken;
  try{
    if(typeof maplibregl==='undefined')throw new Error('Map library unavailable');
    liveMap=new maplibregl.Map({container:$('#map'),style:'https://tiles.openfreemap.org/styles/liberty',center:currentLegs[0].coordinates[0],zoom:12,attributionControl:true,cooperativeGestures:true});
    const map=liveMap;
    map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');
    map.addControl(new maplibregl.ScaleControl({unit:'metric'}),'bottom-left');
    map.on('load',()=>{
      if(token!==viewToken)return;clearTimeout(mapTimer);
      map.addSource('trip-route',{type:'geojson',data:featureCollection()});
      map.addLayer({id:'route-outline',type:'line',source:'trip-route',paint:{'line-color':'#ffffff','line-width':8,'line-opacity':0.9}});
      map.addLayer({id:'route-lines',type:'line',source:'trip-route',layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':['match',['get','profile'],'foot','#187657','#2169a8'],'line-width':['case',['==',['get','active'],1],6,4],'line-opacity':['case',['==',['get','active'],1],1,0.65]}});
      const seen=new Set();currentPoints.forEach((p,i)=>{
        if(!p.xy)return;const key=p.id+'|'+p.xy.map(n=>n.toFixed(4)).join(',');if(seen.has(key))return;seen.add(key);
        const numbers=currentPoints.map((q,j)=>q.id===p.id?j+1:null).filter(Boolean).join('/');
        const el=document.createElement('button');el.type='button';el.className='map-pin'+(hasAlert(p.id)?' alert-pin':'');el.textContent=numbers;el.setAttribute('aria-label',numbers+' · '+p.name);
        const popup=new maplibregl.Popup({offset:22}).setHTML(`<b>${esc(p.name)}</b>${hasAlert(p.id)?`<p class="attention-label">⚠ ${esc(p.alerts[0].title)}</p>`:''}<p>${link(mapsUrl(p),'Abrir local no Google Maps')}</p>`);
        new maplibregl.Marker({element:el}).setLngLat(p.xy).setPopup(popup).addTo(map);
      });
      const dot=document.createElement('div');dot.className='traveler-dot';dot.setAttribute('aria-hidden','true');
      traveler=new maplibregl.Marker({element:dot}).setLngLat(currentLegs[0].coordinates[0]).addTo(map);
      fitMap(true);$('#map-status').textContent='Mapa real carregado · '+currentLegs.length+' trechos · '+(currentLegs.reduce((a,l)=>a+l.distance,0)/1000).toLocaleString('pt-BR',{maximumFractionDigits:1})+' km no dia';updateLeg();
    });
    map.on('error',()=>{if(token===viewToken&&$('#map-status'))$('#map-status').textContent='Uma camada não carregou. Os percursos e os links do Google Maps continuam disponíveis.';});
    mapTimer=setTimeout(()=>{if(token===viewToken&&!map.isStyleLoaded()){map.remove();liveMap=null;drawFallback();}},18000);
    updateLeg();
  }catch(e){if(liveMap){liveMap.remove();liveMap=null;}drawFallback();}
}
function drawFallback(legOnly=false){
  const box=$('#map');if(!box)return;
  $('#map-status').innerHTML='Mapa online indisponível. Exibindo vias locais e percursos calculados. '+link(legUrl(currentLegs[legIndex]),'Abrir mapa completo');
  const w=box.clientWidth||600,h=box.clientHeight||410;
  const coords=legOnly?currentLegs[legIndex].coordinates:currentLegs.flatMap(l=>l.coordinates);
  project=d3.geoMercator().fitExtent([[25,25],[w-25,h-25]],{type:'MultiPoint',coordinates:coords});
  const path=d3.geoPath(project),region=dayData().city==='Dubai'?'dubai':'hanoi';
  const features=[...(MAPS[region]?.features||[]),...(selected===17?MAPS.ninhbinh.features:[])];
  let s=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Percursos pelas ruas, modo de reserva sem mapa online"><defs><clipPath id="mapClip"><rect width="${w}" height="${h}"/></clipPath></defs><g clip-path="url(#mapClip)"><path d="${features.map(f=>path(f)).join('')}" fill="none" stroke="#c7d2cf" stroke-width="1"/>`;
  currentLegs.forEach((l,i)=>{s+=`<path id="seg${i}" d="${path({type:'LineString',coordinates:l.coordinates})}" fill="none" stroke="${l.profile==='foot'?'#187657':'#2169a8'}" stroke-width="3"/>`;});
  currentPoints.forEach((p,i)=>{if(!p.xy)return;const xy=project(p.xy);s+=`<circle cx="${xy[0]}" cy="${xy[1]}" r="13" fill="white" stroke="${hasAlert(p.id)?'#ae2727':'#235c4f'}" stroke-width="2"/><text x="${xy[0]}" y="${xy[1]+4}" text-anchor="middle" font-size="12" fill="#172f35">${i+1}</text>`;});
  s+='<circle id="traveler" r="6" fill="#dd9237" stroke="white" stroke-width="2"/></g></svg>';box.innerHTML=s;updateLeg();
}
function legUrl(l){if(!l)return '';return 'https://www.google.com/maps/dir/?api=1&origin='+encodeURIComponent(DATA.items[l.a].query)+'&destination='+encodeURIComponent(DATA.items[l.b].query)+'&travelmode='+(l.profile==='foot'?'walking':'driving');}
function updateLeg(){
  const l=currentLegs[legIndex];if(!l||!$('#leg'))return;
  const a=DATA.items[l.a],b=DATA.items[l.b],boat=l.ferries?.length;
  const min=Math.max(1,Math.round(l.duration/60)),km=(l.distance/1000).toLocaleString('pt-BR',{maximumFractionDigits:1});
  $('#leg').innerHTML=`<div class="small">Trecho ${legIndex+1} de ${currentLegs.length}</div><h3>${esc(a.name.replace(' — hotel sugerido',''))} → ${esc(b.name.replace(' — hotel sugerido',''))}</h3><p><b>${boat?'A pé + travessia':l.profile==='foot'?'A pé':'Carro / táxi'}</b> · ${km} km · ${min} min calculados</p><p class="small">${boat?'Inclui travessia mapeada; confirmar linha, espera e funcionamento do abra no cais.':l.profile==='car'?'Tempo sem trânsito, espera do carro, estacionamento ou bagagens. Mantenha as margens do roteiro.':'Tempo caminhando, sem paradas; confirmar acesso e sinalização no local.'}</p>${b.geoNote?`<p class="small">${esc(b.geoNote)}</p>`:''}${maxSnap(l)>150?'<p class="small attention-label">⚠ Conferir portão/entrada: o ponto cadastrado fica afastado da via de acesso.</p>':''}<div class="links">${link(legUrl(l),'Navegar no Google Maps')}</div>`;
  $('#prev').disabled=legIndex===0;$('#next').disabled=legIndex===currentLegs.length-1;
  if(liveMap?.getSource('trip-route'))liveMap.getSource('trip-route').setData(featureCollection());
  document.querySelectorAll('[id^="seg"]').forEach((p,i)=>p.setAttribute('stroke-width',i===legIndex?'5':'2'));
  moveDot();
}
const maxSnap = l => Math.max(...(l.snaps||[0]));
function positionOnLeg(l,t){
  const points=l.coordinates;
  if(!l.cumulative){l.cumulative=[0];for(let i=1;i<points.length;i++)l.cumulative.push(l.cumulative[i-1]+d3.geoDistance(points[i-1],points[i]));}
  const target=t*l.cumulative.at(-1);let i=1;while(i<points.length-1&&l.cumulative[i]<target)i++;
  const portion=(target-l.cumulative[i-1])/(l.cumulative[i]-l.cumulative[i-1]||1);
  return [points[i-1][0]+(points[i][0]-points[i-1][0])*portion,points[i-1][1]+(points[i][1]-points[i-1][1])*portion];
}
function moveDot(){const l=currentLegs[legIndex];if(!l)return;const xy=positionOnLeg(l,progress);if(traveler)traveler.setLngLat(xy);const dot=$('#traveler');if(dot&&project){const p=project(xy);dot.setAttribute('cx',p[0]);dot.setAttribute('cy',p[1]);}}
function pause(){playing=false;if(raf)cancelAnimationFrame(raf);raf=null;const b=$('#play');if(b)b.textContent='▶ Animar roteiro';}
function play(){if(!currentLegs.length)return;if(progress>=1&&legIndex===currentLegs.length-1){legIndex=0;progress=0;updateLeg();}playing=true;$('#play').textContent='Ⅱ Pausar';last=performance.now();raf=requestAnimationFrame(tick);}
function tick(t){if(!playing)return;progress+=Math.min(t-last,100)/5000;last=t;if(progress>=1){progress=1;moveDot();if(legIndex<currentLegs.length-1){legIndex++;progress=0;updateLeg();}else{pause();return;}}moveDot();raf=requestAnimationFrame(tick);}
function step(v){pause();legIndex=Math.max(0,Math.min(currentLegs.length-1,legIndex+v));progress=0;updateLeg();}
window.addEventListener('resize',()=>{if(liveMap)liveMap.resize();});
const dialog=$('#photo-dialog');
document.addEventListener('click',e=>{const btn=e.target.closest('[data-photo]');if(!btn)return;const p=photo(btn.dataset.photo);if(!p)return;$('#full-photo').src=p.src;$('#full-photo').alt=p.caption;$('#photo-caption').innerHTML=`<b>${esc(p.caption)}</b><p>${esc(p.credit)} · ${esc(p.license)} · ${link(p.source,'Fonte')}</p>`;dialog.showModal();});
$('#close-photo').onclick=()=>dialog.close();dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
const tasks=['Definir teto de orçamento de hotel e jantar por casal','Comparar Peridot com JM Junior e La Siesta nas mesmas datas','Garantir chegada de madrugada e guarda das malas após checkout em Dubai','Escolher 6ª diária ou saída tardia garantida em Hanói','Decidir se Gia entra no orçamento; janela de 60 dias e política de garantia','Confirmar jantares no Tam Vi e La Badiane diretamente','Reconfirmar B-52, D67 e unidade do Museu Nacional','Reconfirmar Ramadã, Global Village e Museu do Futuro','Comprar sessão de marionetes compatível com jantar','Reservar motorista de Ninh Bình e transfers dos voos'];
let checks={};try{checks=JSON.parse(localStorage.getItem('trip2027checks-v2')||'{}')}catch{}
$('#todos').innerHTML=tasks.map((t,i)=>`<label><input type="checkbox" data-check="${i}" ${checks[i]?'checked':''}><span>${esc(t)}</span></label>`).join('');
$('#todos').onchange=e=>{checks[e.target.dataset.check]=e.target.checked;try{localStorage.setItem('trip2027checks-v2',JSON.stringify(checks))}catch{}};
$('#sources').innerHTML=Object.values(DATA.items).map(p=>`<p>${link(p.source,p.name)}${p.geo?' · '+link(p.geo,'Ponto de referência'):''}${p.extraSource?' · '+link(p.extraSource,'Conferência adicional'):''}</p>`).join('')+'<p>Pesquisa inicial em 02/10/2026; Hương Liên e seus trechos incluídos em 05/10/2026. Confirmar funcionamento para 2027. Fotos identificadas e creditadas nos detalhes.</p>';
$('#share').onclick=()=>{pause();const clone=document.documentElement.cloneNode(true);clone.querySelector('#photo-dialog')?.removeAttribute('open');const blob=new Blob(['<!doctype html>\n'+clone.outerHTML],{type:'text/html;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='viagem-dubai-hanoi-2027.html';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);$('#toast').hidden=false;$('#toast').textContent='Download solicitado. Fotos e roteiro incluídos; o mapa completo precisa de internet.';setTimeout(()=>$('#toast').hidden=true,6500);};
renderDays();const initial=location.hash.slice(1);panel(['overview','itinerary','ramadan','hotels','review'].includes(initial)?initial:'overview');
