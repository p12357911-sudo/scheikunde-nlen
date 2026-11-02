"""NL-pariteit voor ALLE pagina's: de NL-weergave van de nieuwe site (tekst uit JSON) moet gelijk zijn aan de huidige handgeschreven
NL-pagina's (basislijn). Uitvoeren: /workspace/pwenv/bin/python tests/test_nl_parity.py [paginanaam ...]
De uitzonderingen op de index (contactsectie: e-mailadres en 'Contactformulier volgt' vervallen, knop Google Form erbij)
staan met naam in TOEGESTAAN_INDEX."""
import sys, re, json, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

JS_KB = """() => { const c = document.querySelector('h2').closest('.w3-container') || document.body;
 const o = {title: document.title, h2: document.querySelector('h2').innerHTML.trim(),
  intro: [...document.querySelectorAll('p')].filter(p=>!p.closest('.antwoord-box') && !p.closest('footer') && !p.closest('#voet') && !p.closest('.niet-vertaald') && !p.closest('#ai-melding') && !p.closest('.in-ontwikkeling')).map(p=>p.innerHTML.replace(/\\s+/g,' ').trim()),
  q: [...document.querySelectorAll('button.vraag-knop')].map(b => { const w=b.parentNode; const i=w.querySelector('input'); const box=w.querySelector('.antwoord-box');
   return {q:b.innerHTML.trim(), onclick: (b.getAttribute('onclick')||'').replace(/Demo\\d+/,'DemoN'), ph:i.getAttribute('placeholder'), box: box.innerHTML.replace(/ alt="[^"]*"/g,'').replace(/class="\\s*([^"]*?)\\s*"/g,'class="$1"').replace(/\\s+/g,' ').replace(/\\s+</g,'<').replace(/>\\s+/g,'>').trim(), goed: box.getAttribute('data-goed'), cls: box.className, eind: !!box.querySelector('.eindantwoord')}; }),
  zweef: (document.getElementById('zweefknop')||{}).textContent, opn: [...document.querySelectorAll('a.knop-blauw')].map(a=>a.textContent.trim()+'|'+a.getAttribute('href')),
  nav:[...document.querySelectorAll('.oefen-wissel a')].map(a=>a.textContent+'|'+a.getAttribute('href')+'|'+a.getAttribute('aria-current')),
  menu:[...document.querySelectorAll('#navbar .w3-bar a, .w3-top .w3-bar a')].map(a=>a.textContent.trim()+'|'+a.getAttribute('href')).filter((x,i,arr)=>true),
  voet: (document.querySelector('footer')||{textContent:''}).textContent.replace(/\\s+/g,'')};
  o.intro = o.intro.filter(x => x).join(' '); o.q.sort((x,y)=>x.q<y.q?-1:1); return o; }"""
JS_MP = """() => { const quiz=document.getElementById('quiz'); const cont=quiz.parentNode; const kop=cont.querySelector('em, h2');
 const q=[...document.querySelectorAll('.vraag-blok')].map(b=>b.querySelector('.question').innerHTML.trim()+' || '+[...b.querySelectorAll('label')].map(l=>l.textContent.trim().replace(/^[a-d]: /,'')).sort().join(' / '));
 return {title: document.title, kop: kop && kop.tagName+':'+kop.innerHTML.trim(), intro:[...cont.children].filter(e=>e.tagName==='P').map(p=>p.innerHTML.trim()), btn: (document.getElementById('submit')||{}).textContent, zweef: (document.getElementById('zweefknop')||{}).textContent,
  cid: cont.id, ccls: cont.className, n:q.length, q:q.sort(), opn: [...cont.querySelectorAll('a.knop-blauw')].map(a=>a.textContent.trim()),
  nav:[...document.querySelectorAll('.oefen-wissel a')].map(a=>a.textContent+'|'+a.getAttribute('href')+'|'+a.getAttribute('aria-current')),
  menu:[...document.querySelectorAll('.w3-top .w3-bar a')].map(a=>a.textContent.trim()+'|'+a.getAttribute('href')), voet: (document.querySelector('footer')||{textContent:''}).textContent.replace(/\\s+/g,'')}; }"""
JS_MPDATA = "() => JSON.stringify(window.myQuestions.map(q=>({question:q.question, answers:q.answers, correctAnswer:q.correctAnswer, fixed:q.fixed})))"
JS_INDEX = """() => { const sec = {}; for (const e of document.querySelectorAll('body > div[id], body > div > div[id]')) { if (!/^(scheikunde|rekenen|NaSk|natuurkunde|biologie|NED|themas|games|bouw|contact|proefversie|myCarousel)$/.test(e.id)) continue;
   sec[e.id] = e.textContent.replace(/\\s+/g,' ').trim(); }
  const links = [...document.querySelectorAll('a[href]')].filter(a=>!a.closest('footer')&&!a.closest('#voet')&&!a.closest('.w3-top')).map(a=>a.textContent.replace(/\\s+/g,' ').trim()+'|'+a.getAttribute('href'));
  const menu = [...document.querySelectorAll('.w3-top .w3-bar a')].map(a=>a.textContent.trim()+'|'+a.getAttribute('href'));
  const kop = [...document.querySelectorAll('h1,h2,h3,h4')].map(h=>h.tagName+':'+h.textContent.replace(/\\s+/g,' ').trim());
  const voet = (document.querySelector('footer')||{textContent:''}).textContent.replace(/\\s+/g,'');
  return {title: document.title, sec, links, menu, kop, voet}; }"""

FORM = 'https://docs.google.com/forms/d/e/1FAIpQLScy7x5-wDjjU_n95WEmYg2VHq_fNlyu9uda95-GUQ4pCbNwgw/viewform'
JS_PUZ = """() => ({title: document.title, fil: document.querySelector('.fil').textContent.replace(/\\s+/g,' ').trim(), n: document.querySelectorAll('.fil-vakje').length,
  menu:[...document.querySelectorAll('.w3-top .w3-bar a')].map(a=>a.textContent.trim()+'|'+a.getAttribute('href')), voet: (document.querySelector('footer')||{textContent:''}).textContent.replace(/\\s+/g,'')})"""
TOEGESTAAN_INDEX_SEC = {'contact'}   # contactsectie wijkt bewust af (zie hieronder)
CONTACT_VERWACHT = 'Contact Momenteel alleen verkrijgbaar in Nederland Stuur ons een berichtje met je vragen en tips en tops! En waar gehakt wordt vallen spaanders dus zie je een foutje laat dat dan ook even weten. Stuur een bericht Betermetpeter wil nog beter worden om op een vrije manier alle scholieren te helpen. Dat komt niet vanzelf en daar zijn donaties voor nodig. Doneer daarom en zorg dat deze website vrij te bezoeken blijft.'

def laad(b, base, pg, taal):
    ctx, page, errs = nieuwe_pagina(b, taal)
    page.goto(f'{base}/{pg}.html', wait_until='domcontentloaded')
    if taal:
        page.wait_for_function('window.i18nKlaar !== undefined', timeout=10000)
        page.evaluate('window.i18nKlaar')
    page.wait_for_timeout(1300)
    return ctx, page, errs

def vergelijk(a, c):
    delen = []
    for k in a:
        if a[k] != c.get(k):
            if isinstance(a[k], list) and isinstance(c.get(k), list) and len(a[k]) == len(c[k]):
                for i, (x, y) in enumerate(zip(a[k], c[k])):
                    if x != y: delen.append(f'  {k}[{i}]\n    orig: {str(x)[:3000]}\n    nieuw: {str(y)[:3000]}'); break
            else: delen.append(f'  {k}\n    orig: {str(a[k])[:3000]}\n    nieuw: {str(c.get(k))[:3000]}')
    return delen

def main():
    man = json.load(open(os.path.join(ROOT, 'tools/manifest.json')))['pagina']
    paginas = sys.argv[1:] or (['index', 'puzzel-moleculaire-stoffen'] + sorted(man))
    bad = 0
    with sync_playwright() as p:
        b = browser(p); new = serve(ROOT); old = serve(ORIG)
        for pg in paginas:
            soort = 'index' if pg == 'index' else ('puzzel' if pg.startswith('puzzel') else man[pg]['soort'])
            js = {'kb': JS_KB, 'mp': JS_MP, 'index': JS_INDEX, 'puzzel': JS_PUZ}[soort]
            res = []; foutjs = []
            for base, taal in ((old, None), (new, 'nl')):
                ctx, page, errs = laad(b, base, pg, taal)
                r = page.evaluate(js)
                if soort == 'mp': r['_data'] = page.evaluate(JS_MPDATA)
                res.append(r); foutjs += errs; ctx.close()
            a, c = res
            if pg == 'sk3h-stoffen-KBAI': a['intro'] = c['intro'] = ''   # bewust: AI-uitleg komt nu uit ui.json (zelfde tekst als de andere AI-pagina's)
            if soort == 'index':
                a['sec'].pop('contact'); cc = c['sec'].pop('contact')
                a['links'] = [l for l in a['links'] if 'mailto:' not in l and l != 'Stuur ons een bericht|#contact']
                c_links = [l for l in c['links'] if l != 'Stuur een bericht|'+FORM]
                a['kop'] = [h for h in a['kop'] if 'Contactformulier' not in h]; c['kop'] = list(c['kop'])
                dd = vergelijk(a, dict(c, links=c_links))
                if cc != CONTACT_VERWACHT: dd.append('  contact wijkt af van het verwachte:\n    ' + cc)
                if '@' in json.dumps(c): dd.append('  e-mailadres aanwezig!')
                if 'Stuur een bericht|'+FORM not in c['links']: dd.append('  plaatshouder Google Form ontbreekt')
            else:
                if soort == 'puzzel': a['voet'] = a['voet'] + 'NaarTop'   # de nieuwe pagina heeft ook de 'Naar boven'-knop
                dd = vergelijk(a, c)
            if foutjs: dd.append('  JS-fouten: ' + str(foutjs)[:300])
            if dd: bad += 1; print('VERSCHIL', pg); print('\n'.join(dd))
            else: print('GELIJK ', pg)
        b.close()
    print('\nNL-pariteit:', 'ALLES GELIJK' if not bad else f'{bad} pagina(\'s) met verschil', f'({len(paginas)} getest)')
    sys.exit(1 if bad else 0)

if __name__ == '__main__': main()
