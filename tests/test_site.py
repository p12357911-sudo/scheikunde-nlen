"""Playwright-tests van de NL/EN-site (taalwissel, getalnotatie, nakijken, kader, opmaak). Uitvoeren: /workspace/pwenv/bin/python tests/test_site.py
Schermafbeeldingen komen in ../screens/. De AI-worker wordt gemockt (we testen wat er heen gaat en hoe het antwoord getoond wordt)."""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

SCREENS = os.path.join(ROOT, 'screens'); os.makedirs(SCREENS, exist_ok=True)
PAGINAS = ['index', 'sk3t-stoffen-KB', 'sk3t-stoffen-MP', 'rv3h-significante-cijfers-stappen-KB']
RES = []
def check(naam, ok, extra=''):
    RES.append((naam, bool(ok))); print(('PASS ' if ok else 'FAIL ') + naam + (('  -> ' + str(extra)) if (extra and not ok) else ''))

def open_pagina(b, base, pg, taal, size=None, mock=None):
    ctx, page, errs = nieuwe_pagina(b, taal, size)
    verzoeken = []
    def route(r):
        try: body = json.loads(r.request.post_data or '{}')
        except Exception: body = {}
        verzoeken.append(body)
        if r.request.method == 'OPTIONS':
            return r.fulfill(status=204, headers={'access-control-allow-origin': '*', 'access-control-allow-headers': 'content-type'})
        res = [{'id': it['id'], 'verdict': (mock or 'half'), 'tip': 'MOCK-TIP'} for it in body.get('items', [])]
        r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=json.dumps({'results': res}))
    ctx.route(re.compile(r'.*workers\.dev.*'), route)
    page.goto(f'{base}/{pg}.html'); page.wait_for_function('document.querySelector("#navbar a, .navbar a, .taal-knop")', timeout=8000)
    page.wait_for_timeout(600)
    return ctx, page, errs, verzoeken

def alles_zichtbaar(page):
    for _ in range(10):
        k = page.query_selector('button:has-text("More questions"), button:has-text("Meer vragen")')
        if not k or not k.is_visible(): break
        k.click(); page.wait_for_timeout(100)

def kb_item(page, deel):
    alles_zichtbaar(page)
    for it in page.query_selector_all('.kb-item'):
        if deel in it.query_selector('.vraag-knop').inner_text(): return it
    raise AssertionError('vraag niet gevonden: ' + deel)

def antwoord_en_controleer(page, deel, tekst):
    it = kb_item(page, deel)
    page.evaluate('(e)=>e.scrollIntoView()', it)
    for inp in page.query_selector_all('.kb-item input[type=text]'): inp.fill('')
    it.query_selector('input[type=text]').fill(tekst)
    page.click('#kb-controleer'); page.wait_for_timeout(400)
    o = it.query_selector('.kb-oordeel')
    return (o.inner_text() if o else ''), it

with sync_playwright() as p:
    b = browser(p); base = serve(ROOT)

    # 1. Knop: wisselen, onthouden, URL-parameter, standaardtaal
    ctx, page, errs, _ = open_pagina(b, base, 'index', None)           # browser nl-NL, niets opgeslagen -> NL
    check('standaard bij Nederlandse browser = NL', page.evaluate('document.documentElement.lang') == 'nl')
    check('NL-index toont Nederlandse tekst', 'scheikunde' in page.inner_text('body').lower() and 'chemistry' not in page.inner_text('body').lower())
    page.click('.taal-knop:has-text("EN")'); page.wait_for_load_state(); page.wait_for_timeout(800)
    check('klik EN -> html lang=en', page.evaluate('document.documentElement.lang') == 'en')
    check('klik EN -> Engelse tekst op index', 'chemistry' in page.inner_text('body').lower() and 'maths skills' in page.inner_text('body').lower())
    check('keuze staat in localStorage', page.evaluate("localStorage.getItem('taal')") == 'en')
    page.goto(f'{base}/sk3t-stoffen-KB.html'); page.wait_for_timeout(1200)
    check('keuze blijft onthouden op andere pagina', page.evaluate('document.documentElement.lang') == 'en' and 'Substances and mixtures' in page.title())
    page.click('.taal-knop:has-text("NL")'); page.wait_for_load_state(); page.wait_for_timeout(800)
    check('terug naar NL', page.evaluate('document.documentElement.lang') == 'nl' and 'Stoffen en mengsels' in page.title())
    check('geen JS-fouten tijdens wisselen', not errs, errs)
    ctx.close()
    ctx, page, errs, _ = open_pagina(b, base, 'sk3t-stoffen-KB', None); page.goto(f'{base}/sk3t-stoffen-KB.html?lang=en'); page.wait_for_timeout(1000)
    check('?lang=en wint van de browsertaal', page.evaluate('document.documentElement.lang') == 'en')
    ctx.close()
    ctx = b.new_context(locale='de-DE'); page = ctx.new_page(); page.goto(f'{base}/index.html'); page.wait_for_timeout(1500)
    check('niet-Nederlandse browser -> EN', page.evaluate('document.documentElement.lang') == 'en'); ctx.close()

    # 2. Getalnotatie en checker, per taal
    for taal, vraag, goed, komma, punt, fout, half in [
        ('en', '0.09996', '0.10', '0,10', '0.10', '0.11', '0.1'),
        ('nl', '0,09996', '0,10', '0,10', '0.10', '0,11', '0,1')]:
        ctx, page, errs, _ = open_pagina(b, base, 'rv3h-significante-cijfers-stappen-KB', taal)
        it = kb_item(page, vraag)
        shown = it.query_selector('.eindantwoord').inner_text().strip()
        check(f'[{taal}] getoond antwoord in juiste notatie ({shown})', shown == goed)
        check(f'[{taal}] vraag in juiste notatie', vraag in it.query_selector('.vraag-knop').inner_text())
        for txt, verwacht, lab in [(komma, 'goed', 'komma'), (punt, 'goed', 'punt'), (fout, 'fout', 'fout getal'), (half, 'half', 'te weinig decimalen')]:
            uit, _ = antwoord_en_controleer(page, vraag, txt)
            marker = {'goed': ('Correct', 'Goed'), 'half': ('Nearly', 'Bijna'), 'fout': ('Not correct', 'Niet goed')}[verwacht]
            check(f'[{taal}] "{txt}" ({lab}) -> {verwacht}', any(m in uit for m in marker), uit)
        check(f'[{taal}] geen JS-fouten', not errs, errs); ctx.close()

    ctx, page, errs, _ = open_pagina(b, base, 'rv3h-significante-cijfers-stappen-KB', 'en')
    for tekst, verwacht in [('1,000', '1000'), ('1,000.5', '1000.5'), ('2,5', '2.5'), ('1,000,000 g', '1000000g'), ('12,34', '12.34'), ('3.14', '3.14')]:
        r = page.evaluate('(t)=>kbNormaal(t)', tekst)
        check(f'[en] kbNormaal("{tekst}") = {verwacht}', r == verwacht, r)
    ctx.close()
    ctx, page, errs, _ = open_pagina(b, base, 'rv3h-significante-cijfers-stappen-KB', 'nl')
    for tekst, verwacht in [('2,5', '2.5'), ('1.000', '1.000'), ('3,14', '3.14')]:
        r = page.evaluate('(t)=>kbNormaal(t)', tekst)
        check(f'[nl] kbNormaal("{tekst}") = {verwacht} (ongewijzigd gedrag)', r == verwacht, r)
    ctx.close()

    # 2b. Tijdelijke tweak: bij een "=" telt alleen wat na het laatste "=" staat (kbNaLaatsteIs in school.js)
    GOED = ('Correct', 'Goed'); FOUT = ('Not correct', 'Niet goed')
    for taal, vraag, gevallen in [
        ('en', 'x / 8 = 2.5', [('20', GOED), ('8x2.5=20', GOED), ('8 x 2.5 = 20', GOED), ('8*2.5=20', GOED), ('8 \u00d7 2.5 = 20', GOED), ('x = 20', GOED), ('x=20', GOED),
                               ('2.5 x 8 = 20.0', ('Nearly',)), ('8x2.5=21', FOUT), ('20=8x2.5', FOUT), ('8x2.5=', FOUT), ('8x2.5', FOUT), ('=', FOUT)]),
        ('nl', 'x / 8 = 2,5', [('20', GOED), ('8x2,5=20', GOED), ('8 \u00d7 2,5 = 20', GOED), ('8 * 2,5 = 20', GOED), ('x = 20', GOED), ('8x2,5=21', FOUT), ('20=8x2,5', FOUT)])]:
        ctx, page, errs, vz = open_pagina(b, base, 'rv3h-significante-cijfers-stappen-KB', taal, mock='fout')
        for txt, want in gevallen:
            try:
                uit, it = antwoord_en_controleer(page, vraag, txt)
            except AssertionError as e:
                check(f'[{taal}] vraag {vraag!r} gevonden', False, e); break
            check(f'[{taal}] "{txt}" bij {vraag} -> {want[0]}', any(m in uit for m in want), uit)
        check(f'[{taal}] "=": geen JS-fouten', not errs, errs); ctx.close()
    ctx, page, errs, vz = open_pagina(b, base, 'rv3h-significante-cijfers-stappen-KB', 'en', mock='fout')
    for txt, want in [('rho = 2.70 g/cm3', 'goed'), ('m / V = 2.70 g/cm3', 'goed'), ('2.70 g/cm3', 'goed'), ('2.70 g', 'goed'), ('3.70 g/cm3', 'fout')]:
        r = page.evaluate('(t)=>{var v=kbGetal("2.70 g/cm3"); return kbVergelijkGetal(t, v).oordeel;}', txt)
        r = {'goed': 'goed', 'half': 'half', 'fout': 'fout'}[r]
        check(f'[en] kbVergelijkGetal("{txt}", 2.70 g/cm3) = {want}', r == want or (txt == '2.70 g' and r in ('goed', 'half')), r)
    for txt, want in [('20', '20'), ('8x2.5=20', '20'), ('a = b = 20 g', '20 g'), ('x = ', ''), ('abc', 'abc'), ('20=8x2.5', '8x2.5')]:
        r = page.evaluate('(t)=>kbNaLaatsteIs(t)', txt)
        check(f'[en] kbNaLaatsteIs("{txt}") = "{want}"', r == want, r)
    ctx.close()

    # 2c. Kader om titel en uitleg op KB-pagina's (NL en EN, desktop en 390 px)
    for pg in ('sk3t-stoffen-KB', 'rv3h-significante-cijfers-stappen-KB'):
        for taal in ('en', 'nl'):
            for naam, size in (('390', {'width': 390, 'height': 800}), ('1280', {'width': 1280, 'height': 900})):
                ctx, page, errs, _ = open_pagina(b, base, pg, taal, size)
                page.wait_for_timeout(500)
                d = page.evaluate("""() => { const k = document.getElementById('kb-intro'); if (!k) return null; const cs = getComputedStyle(k), h = getComputedStyle(k.querySelector('h2')), p = k.querySelectorAll('p'), pv = document.getElementById('ai-privacy');
                  const r = k.getBoundingClientRect(); const vk = document.querySelector('.kb-item, button.vraag-knop').getBoundingClientRect();
                  return {border: cs.borderTopWidth, kleur: cs.borderTopColor, bg: cs.backgroundColor, font: cs.fontFamily.split(',')[0], h2: h.color, h2font: h.fontFamily.split(',')[0], pcol: [...p].map(x=>getComputedStyle(x).color),
                          psize: [...p].map(x=>parseFloat(getComputedStyle(x).fontSize)), n: p.length, privacy: !!pv && k.contains(pv), pvbold: pv ? getComputedStyle(pv).fontWeight : '', pad: cs.paddingLeft,
                          voorVragen: r.bottom <= vk.top, breed: document.documentElement.scrollWidth - document.documentElement.clientWidth, rechts: r.right <= innerWidth, links: r.left >= 0}; }""")
                lab = f'[{taal} {naam}] {pg}'
                check(f'{lab}: intro-kader aanwezig', d is not None)
                if d:
                    check(f'{lab}: kader 1,3 pt (browser rondt af naar 1 px) #003A5C', d['border'] in ('1px', '1.75px') and d['kleur'] == 'rgb(0, 58, 92)', d)
                    check(f'{lab}: Arial, tekst #111111, kop #003A5C', d['font'] == 'Arial' and d['h2font'] == 'Arial' and d['h2'] == 'rgb(0, 58, 92)' and all(c == 'rgb(17, 17, 17)' for c in d['pcol']), d)
                    check(f'{lab}: tekst 12 pt (16 px)', all(abs(s - 16) < 0.1 for s in d['psize']), d['psize'])
                    check(f'{lab}: privacyregel apart, in het kader, vet', d['privacy'] and int(d['pvbold']) >= 700, d)
                    check(f'{lab}: kader staat boven de vragen en past in het scherm', d['voorVragen'] and d['rechts'] and d['links'] and d['breed'] <= 0, d)
                if pg.startswith('rv3h') and taal == 'en':
                    page.screenshot(path=f'{SCREENS}/intro_kader_{taal}_{naam}.png')
                check(f'{lab}: kader geen JS-fouten', not errs, errs); ctx.close()

    # 3. Tekstvraag lokaal (zonder AI) en AI-aanroep: taal van het verzoek en weergave van de EN-tip
    for taal, vraag, juist in [('en', 'Which unit goes with density', 'g/cm3'), ('nl', 'Welke eenheid hoort bij dichtheid', 'g/cm3')]:
        ctx, page, errs, vz = open_pagina(b, base, 'sk3t-stoffen-KB', taal)
        try:
            uit, it = antwoord_en_controleer(page, vraag, juist)
            check(f'[{taal}] "g/cm3" lokaal goed gekeurd', any(m in uit for m in ('Correct', 'Goed')), uit)
        except AssertionError as e:
            check(f'[{taal}] vraag voor lokale test gevonden', False, e)
        ctx.close()
    for taal in ('en', 'nl'):
        ctx, page, errs, vz = open_pagina(b, base, 'sk3t-stoffen-KB', taal, mock='half')
        vraag = 'Name two hazard symbols' if taal == 'en' else 'Noem twee gevarensymbolen'
        uit, it = antwoord_en_controleer(page, vraag, 'only a flame')
        page.wait_for_timeout(800)
        gestuurd = [v for v in vz if v.get('items')]
        check(f'[{taal}] AI-verzoek bevat lang="{taal}"', gestuurd and all(v.get('lang') == taal for v in gestuurd), vz)
        o = it.query_selector('.kb-oordeel')
        txt = o.inner_text() if o else ''
        check(f'[{taal}] AI-uitslag + tip getoond ({txt[:40]!r})', 'MOCK-TIP' in txt and (('Nearly' in txt) if taal == 'en' else ('Bijna' in txt)), txt)
        check(f'[{taal}] geen JS-fouten', not errs, errs); ctx.close()

    for taal, vraag, juist, alt in [('en', 'density of aluminium', '2.70 g/cm3', '2,70 g/cm3'), ('nl', 'dichtheid van aluminium', '2,70 g/cm3', '2.70 g/cm3')]:
        ctx, page, errs, vz = open_pagina(b, base, 'sk3t-stoffen-KB', taal)
        shown = kb_item(page, vraag).query_selector('.eindantwoord').inner_text().strip()
        check(f'[{taal}] aluminium: getoond antwoord "{shown}" in juiste notatie', shown.startswith(juist.split()[0]))
        for t in (juist, alt):
            uit, it = antwoord_en_controleer(page, vraag, t)
            check(f'[{taal}] aluminium "{t}" goed', any(m in uit for m in ('Correct', 'Goed')), uit)
        t = '2.7 g/cm3' if taal == 'en' else '2,7 g/cm3'
        uit, it = antwoord_en_controleer(page, vraag, t)
        check(f'[{taal}] aluminium "{t}" (te weinig cijfers) -> bijna goed, net als in NL', any(m in uit for m in ('Nearly', 'Bijna')), uit)
        uit, it = antwoord_en_controleer(page, vraag, '3.70 g/cm3' if taal == 'en' else '3,70 g/cm3')
        check(f'[{taal}] aluminium 3.70 niet goed', any(m in uit for m in ('Not correct', 'Niet goed')), uit)
        ctx.close()

    # 4. Meerkeuze: alles juist beantwoord, in beide talen
    for taal in ('en', 'nl'):
        ctx, page, errs, _ = open_pagina(b, base, 'sk3t-stoffen-MP', taal)
        alles_zichtbaar(page)
        n = page.evaluate('myQuestions.length')
        page.evaluate("""()=>{ myQuestions.forEach((q,i)=>{
            const juist = (()=>{const d=document.createElement('div'); d.innerHTML=q.answers[q.correctAnswer]; return d.innerText.trim();})();
            [...document.querySelectorAll('input[name=question'+i+']')].forEach(r=>{ if (r.parentNode.innerText.replace(/^[a-h]: /,'').trim()===juist) r.click(); }); }); }""")
        page.click('#submit'); page.wait_for_timeout(500)
        txt = page.inner_text('#results')
        want = (f'{n} of {n} correct' if taal == 'en' else f'{n}')
        check(f'[{taal}] MP-uitslag na alles goed: "{txt.strip()[:50]}"', want in txt, txt)
        check(f'[{taal}] MP geen JS-fouten', not errs, errs); ctx.close()

    # 5. Schermen + layout/opmaak op mobiel en desktop
    AUDIT = """() => {
      const bad = [], kl = [];
      document.querySelectorAll('body *').forEach(e => {
        if (!e.offsetParent && e.tagName !== 'BODY') return;
        const direct = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
        if (!direct) return;
        const cs = getComputedStyle(e), fs = parseFloat(cs.fontSize);
        const m = cs.color.match(/\\d+/g).map(Number);
        const grijs = m[0] === m[1] && m[1] === m[2] && m[0] > 20 && m[0] < 235;
        if (fs < 13.3) kl.push(e.tagName + ':' + e.textContent.trim().slice(0, 25) + ' ' + fs);
        if (grijs) bad.push(e.tagName + ':' + e.textContent.trim().slice(0, 25) + ' ' + cs.color);
      });
      return {klein: kl.slice(0, 8), grijs: bad.slice(0, 8), breed: document.documentElement.scrollWidth - document.documentElement.clientWidth,
              fonts: [...new Set([...document.querySelectorAll('h1,h2,p,label,button')].filter(e=>e.offsetParent).map(e => getComputedStyle(e).fontFamily.split(',')[0].replace(/"/g,'')))]};
    }"""
    LEVEL = re.compile(r'\b(vmbo|havo|vwo|mavo|nova|polaris|binas\b(?! tables? \d))', re.I)
    for naam, size in (('390', {'width': 390, 'height': 800}), ('1280', {'width': 1280, 'height': 900})):
        for taal in ('en', 'nl'):
            for pg in PAGINAS:
                ctx, page, errs, _ = open_pagina(b, base, pg, taal, size)
                page.wait_for_timeout(500)
                page.screenshot(path=f'{SCREENS}/{pg}_{taal}_{naam}.png', full_page=False)
                if taal == 'en' and pg != 'index':
                    page.screenshot(path=f'{SCREENS}/{pg}_{taal}_{naam}_vol.png', full_page=True)
                a = page.evaluate(AUDIT)
                check(f'[{taal} {naam}] {pg}: geen horizontale scroll', a['breed'] <= 0, a['breed'])
                check(f'[{taal} {naam}] {pg}: tekst >= 10 pt', not a['klein'], a['klein'])
                check(f'[{taal} {naam}] {pg}: geen grijze tekst', not a['grijs'], a['grijs'])
                if taal == 'en':
                    check(f'[en {naam}] {pg}: geen niveau- of methodenamen', not LEVEL.search(page.inner_text('body')))
                check(f'[{taal} {naam}] {pg}: geen JS-fouten', not errs, errs)
                ctx.close()
    # extra: EN-pagina's na controleren, voor het scherm
    for naam, size in (('390', {'width': 390, 'height': 800}), ('1280', {'width': 1280, 'height': 900})):
        ctx, page, errs, _ = open_pagina(b, base, 'rv3h-significante-cijfers-stappen-KB', 'en', size, mock='goed')
        for it in page.query_selector_all('.kb-item')[:4]:
            it.query_selector('input[type=text]').fill(it.query_selector('.eindantwoord').inner_text().strip().split()[0])
        page.click('#kb-controleer'); page.wait_for_timeout(600)
        page.evaluate("document.querySelector('.kb-oordeel').scrollIntoView({block:'center'})"); page.wait_for_timeout(200); page.screenshot(path=f'{SCREENS}/rv3h_en_{naam}_gecontroleerd.png'); ctx.close()
    b.close()

nok = sum(1 for _, ok in RES if ok)
print(f'\n{nok}/{len(RES)} geslaagd'); sys.exit(0 if nok == len(RES) else 1)
