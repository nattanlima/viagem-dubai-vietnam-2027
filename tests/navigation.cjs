const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { parseHTML } = require('linkedom');

const folder = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(folder, 'index.html'), 'utf8');

assert(!/__D3__|__DATA__|__MAPS__|__MEDIA__|__APP__|__PHOTOS__|__ROUTES__|__MAPLIBRE__/.test(html));

function boot(source, initialHash = '') {
  const { document, window } = parseHTML(source);
  const pending = new Map();
  let frame = 0, now = 0, downloaded = null;
  const storage = new Map();
  const context = vm.createContext({
    document, window, console, Blob,
    location: { hash: initialHash },
    performance: { now: () => now },
    localStorage: { getItem: k => storage.get(k) || null, setItem: (k,v) => storage.set(k,v) },
    URL: { createObjectURL: blob => { downloaded = blob; return 'blob:qa'; }, revokeObjectURL() {} },
    setTimeout: () => 1, clearTimeout() {},
    requestAnimationFrame: fn => { pending.set(++frame, fn); return frame; },
    cancelAnimationFrame: id => pending.delete(id)
  });
  Object.defineProperty(window.HTMLElement.prototype, 'clientWidth', { configurable: true, get: () => 620 });
  Object.defineProperty(window.HTMLElement.prototype, 'clientHeight', { configurable: true, get: () => 410 });
  const dialog=document.querySelector('#photo-dialog');
  dialog.showModal=()=>dialog.setAttribute('open','');
  dialog.close=()=>dialog.removeAttribute('open');
  const city = document.querySelector('#city');
  let cityValue = 'all';
  Object.defineProperty(city, 'value', { get: () => cityValue, set: v => { cityValue = v; } });
  for (const script of document.querySelectorAll('script')) {
    assert(!script.src, 'All scripts must be bundled for offline use');
    if(script.id==='maplibre-lib') continue; // Real WebGL rendering is checked in the browser.
    vm.runInContext(script.textContent, context, { timeout: 10000 });
  }
  const $ = selector => { const element = document.querySelector(selector); assert(element, selector); return element; };
  function advance(ms = 16) {
    now += ms;
    const callbacks = [...pending.values()]; pending.clear();
    callbacks.forEach(fn => fn(now));
  }
  function click(selector) { $(selector).click(); advance(); }
  return { document, context, $, click, advance, getDownload: () => downloaded };
}

(async () => {
  const app = boot(html);
  const { $, click, advance, document } = app;
  for (const panel of ['overview','itinerary','ramadan','hotels','review']) {
    click(`[data-panel="${panel}"]`);
    assert.equal(document.querySelectorAll('main>section:not([hidden])').length, 1);
    assert(!$(`#${panel}`).hidden, `Panel ${panel} must be visible`);
    assert.equal($(`[data-panel="${panel}"]`).getAttribute('aria-pressed'), 'true');
  }
  click('#start');
  assert(!$('#itinerary').hidden);
  for (let day = 11; day <= 25; day++) {
    click(`[data-day="${day}"]`);
    assert.equal($('#days [aria-pressed="true"]').dataset.day, String(day));
    assert($('#day .eyebrow').textContent.includes(`${day} fevereiro`));
    assert(!/undefined|NaN/.test($('#day').textContent));
    assert($('#day img').src.startsWith('data:image/jpeg;base64,'));
    for(const row of document.querySelectorAll('#events .event')) {
      assert(row.querySelector('img')?.src.startsWith('data:image/jpeg;base64,'));
      if(row.querySelector('.attention-label')) assert(row.classList.contains('needs-attention'));
    }
    if (day === 11) { assert($('#play').disabled); continue; }
    assert($('#map svg'));
    assert(!/NaN|undefined/.test($('#map svg').outerHTML));
    click('#expand');
    assert([...document.querySelectorAll('#events details')].every(d => d.open));
    click('#expand');
    assert([...document.querySelectorAll('#events details')].every(d => !d.open));
    const pos = $('#traveler').getAttribute('cx') + ',' + $('#traveler').getAttribute('cy');
    click('#play'); advance(100);
    assert.notEqual($('#traveler').getAttribute('cx') + ',' + $('#traveler').getAttribute('cy'), pos);
    click('#play');
    if (!$('#next').disabled) { click('#next'); assert($('#leg').textContent.includes('Trecho 2')); click('#prev'); }
    click('#reset'); assert($('#leg').textContent.includes('Trecho 1'));
  }
  for (const city of ['Dubai','Hanói','Em trânsito','all']) {
    $('#city').value = city;
    $('#city').dispatchEvent(new document.defaultView.Event('change', { bubbles: true }));
    advance();
    assert($('#days button'));
    if (city !== 'all') for (const b of document.querySelectorAll('#days button')) assert(b.getAttribute('aria-label').includes(city));
  }
  for (const photo of ['heroDubai','heroHanoi']) assert($(`#${photo}`).src.startsWith('data:image/jpeg;base64,'));
  click('[data-panel="review"]');
  const check = $('[data-check="0"]'); check.checked = true;
  check.dispatchEvent(new document.defaultView.Event('change', { bubbles: true }));
  assert.equal(vm.runInContext("JSON.parse(localStorage.getItem('trip2027checks-v2'))[0]", app.context), true);
  click('[data-photo="train"]');
  assert($('#photo-dialog').hasAttribute('open'));
  assert($('#full-photo').src.startsWith('data:image/jpeg;base64,'));
  click('#close-photo');assert(!$('#photo-dialog').hasAttribute('open'));
  click('#share');
  const exported = await app.getDownload().text();
  assert(exported.includes('data:image/jpeg;base64,'));
  assert(!$('#toast').textContent.includes('Cópia salva'));
  const restored = boot(exported);
  assert(!restored.$('#overview').hidden, 'Downloaded copy must start with an active, consistent panel');
  restored.click('#start'); restored.click('[data-day="20"]');
  assert(restored.$('#day').textContent.includes('20h15'));
  for (const hash of ['#itinerary','#hotels','#review','#invalid']) {
    const opened = boot(html, hash); opened.advance();
    assert(!opened.$(hash === '#invalid' ? '#overview' : hash).hidden);
  }
  console.log('PASS: public file complete; 5 sections; 15 days; 14 animated route fallbacks; photos on every stop; red alert classes; filters; details; enlarged photo dialog; checklist; share payload and reopened copy.');
  console.log('DOM integration only: no browser rendering or actual download asserted.');
})().catch(error => { console.error(error); process.exitCode = 1; });
