"""Bredere AI-steekproef op de echte GitHub Pages-site: per taal 5 pagina's x 2 vragen (1 goed, 1 bewust fout) = 10 echte AI-aanroepen per taal.
Uitvoeren: /workspace/pwenv/bin/python tests/live_ai.py   (deelt Gemini-quotum met leerlingen: spaarzaam gebruiken)"""
import sys, os, re, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import browser, sync_playwright
BASE = 'https://p12357911-sudo.github.io/scheikunde-nlen'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINAS = ['sk3h-atomen-moleculen-KB', 'sk4h-atoombouw-KB', 'nk3h-elektriciteit-KB', 'nk3h-krachten-KB', 'sk3t-stoffen-KB']  # alle met AI-nakijken
def plat(s): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()
random.seed(7)
tot = {}
with sync_playwright() as p:
    b = browser(p)
    for taal in ('nl', 'en'):
        goed_ok = fout_ok = n = 0
        for pg in PAGINAS:
            d = json.load(open(f'{ROOT}/lang/{taal}/{pg}.json'))
            ans = {plat(q['q']): q for q in d['questions']}
            ctx = b.new_context(locale='nl-NL' if taal == 'nl' else 'en-GB'); page = ctx.new_page(); errs = []
            page.on('pageerror', lambda e: errs.append(str(e)))
            page.goto(f'{BASE}/{pg}.html?lang={taal}'); page.wait_for_timeout(2500)
            knoppen = page.locator('button.vraag-knop')
            kand = []
            for i in range(knoppen.count()):
                if not knoppen.nth(i).is_visible(): continue
                q = ans.get(plat(knoppen.nth(i).inner_text()))
                if q and not q.get('goed') and len(plat(q['a']).split()) >= 3 and 30 < len(plat(q['a'])) < 200: kand.append((i, q))
            random.shuffle(kand)
            if len(kand) < 2: print(taal, pg, 'te weinig kandidaten', len(kand)); continue
            (i1, q1), (i2, q2) = kand[:2]
            def inv(i, tekst):
                knoppen.nth(i).evaluate("(e,t)=>{const inp=e.parentElement.querySelector('input[type=text]');inp.value=t;inp.dispatchEvent(new Event('input',{bubbles:true}))}", tekst)
            inv(i1, plat(q1['a'])); inv(i2, 'I do not know' if taal == 'en' else 'Dat weet ik niet')
            page.click('#kb-controleer'); page.wait_for_timeout(20000)
            res = []
            for i in (i1, i2):
                o = knoppen.nth(i).evaluate("e=>{const o=e.parentElement.querySelector('.kb-oordeel');return o?o.className+' | '+o.innerText:'GEEN'}")
                res.append(o)
            n += 2
            k1 = 'uitslag-goed' in res[0]; k2 = 'uitslag-fout' in res[1]
            goed_ok += k1; fout_ok += k2
            print(taal, pg, '| Q1:', plat(q1['q'])[:50], '| Q2:', plat(q2['q'])[:50], '| goed->', 'OK' if k1 else 'AFWIJKING', res[0][:140].replace('\n', ' '), '| fout->', 'OK' if k2 else 'AFWIJKING', res[1][:140].replace('\n', ' '), '| JS-fouten', errs)
            ctx.close()
        tot[taal] = (n, goed_ok, fout_ok); print('SAMENVATTING', taal, 'aanroepen', n, 'goed herkend', goed_ok, 'fout herkend', fout_ok)
    b.close()
