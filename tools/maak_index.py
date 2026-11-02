#!/usr/bin/env python3
"""Maakt index.html (skelet met data-i18n-html) en lang/nl/index-sleutels.json uit de basislijn-index.
De contactsectie wordt met de hand gebouwd (geen e-mailadres, Google Form)."""
import sys, re, json, copy
from bs4 import BeautifulSoup, NavigableString, Tag
SRC = sys.argv[1]; V = '20261102d'
html = open(SRC + '/index.html', encoding='utf-8').read()
s = BeautifulSoup(html, 'html.parser')
keys = {}; tekst2sleutel = {}
def slug(t):
    t = re.sub(r'<[^>]+>', '', t).lower()
    t = re.sub(r'[^a-z0-9]+', '_', t).strip('_')
    return t[:28].strip('_') or 'x'
def sleutel(inner):
    if inner in tekst2sleutel: return tekst2sleutel[inner]
    k = 'index.' + slug(inner); n = 2; basis = k
    while k in keys: k = f'{basis}_{n}'; n += 1
    keys[k] = inner; tekst2sleutel[inner] = k
    return k
def inner(el): return ''.join(str(c) for c in el.contents).strip()

# --- hand: banner, contact ---
body = s.body
for el in list(body.find_all(True)):
    pass
banner = s.find(id='proefversie'); banner.string = ''
banner['style'] = 'background:#ffc107;color:#000;text-align:center;font:600 14px/1.4 Arial,sans-serif;padding:4px 10px;position:fixed;bottom:0;left:0;right:0;z-index:900'  # onderaan, zodat de taalknop bovenin bereikbaar blijft
banner['data-i18n'] = 'index.proef'; keys['index.proef'] = 'Proefversie – nog niet live'
# contact: bouw nieuw
contact = s.find(id='contact')
rij = contact.find('div', class_='w3-row')
links = rij.find('div', class_='w3-col')
rechts = links.find_next_sibling('div')
rechts.decompose()
for p in list(links.find_all('p')):
    if p.find('a', href=re.compile('^mailto:')): mail_p = p
mail_p.replace_with(BeautifulSoup('''<!-- Contactformulier: Google Form (tweetalig, dezelfde url voor NL en EN). Geen e-mailadres op de site. -->
            <p><a class="w3-button knop-blauw contact-formulier" href="https://docs.google.com/forms/d/e/1FAIpQLScy7x5-wDjjU_n95WEmYg2VHq_fNlyu9uda95-GUQ4pCbNwgw/viewform" target="_blank" rel="noopener" data-i18n="index.stuur_een_bericht"></a></p>''', 'html.parser'))
keys['index.stuur_een_bericht'] = 'Stuur een bericht'; tekst2sleutel['Stuur een bericht'] = 'index.stuur_een_bericht'
# 'Contact' label in w3-xlarge span -> unit; handled generiek

# --- navbar include weg ---
inc = s.find(attrs={'w3-include-html': True}); inc.replace_with(BeautifulSoup('<div id="navbar"></div>', 'html.parser'))
# --- scripts: w3data weg, i18n erbij ---
for sc in s.find_all('script'):
    if sc.get('src') and ('w3data' in sc['src'] or 'w3.js' in sc['src']): sc.decompose()
head = s.head
head.append(BeautifulSoup('<script src="i18n.js?v=%s"></script>' % V, 'html.parser'))
for l in s.find_all('link', href=re.compile('123school.css')): l['href'] = '123school.css?v=' + V
s.find('script', src=re.compile('school.js')).extract() if False else None
# footer vervangen door #voet
foot = s.find('footer'); foot.replace_with(BeautifulSoup('<div id="voet"></div>', 'html.parser'))
# school.js versie
for sc in s.find_all('script', src=re.compile('school.js')): sc['src'] = 'school.js?v=' + V

UITGEZONDERD = {'script', 'style'}
def verwerk(el):
    if not isinstance(el, Tag) or el.name in UITGEZONDERD: return
    if el.get('data-i18n') or el.get('data-i18n-html') or el.get('id') in ('navbar', 'voet'): return
    kind = [c for c in el.children if isinstance(c, Tag)]
    direct = any(isinstance(c, NavigableString) and not isinstance(c, type(s.new_string(''))) and str(c).strip() and not str(c).strip().startswith('<!--') for c in el.children)
    # Opmerkingen (Comment) uitsluiten
    from bs4 import Comment
    direct = any(isinstance(c, NavigableString) and not isinstance(c, Comment) and str(c).strip() for c in el.children)
    eigen_blok = any(c.name in ('div', 'p', 'h2', 'h3', 'a', 'button', 'ol', 'ul', 'form', 'li') for c in kind)
    if (direct and not eigen_blok) or (not kind and el.get_text(strip=True)):
        if el.name == 'title': return
        sl = sleutel(inner(el)); el.clear(); el['data-i18n-html'] = sl; return
    for c in kind: verwerk(c)
for c in list(body.children): verwerk(c)
# aria-label van carousel en alt
car = s.find(id='myCarousel'); car['data-i18n-attr'] = 'aria-label:' + sleutel(car['aria-label']); car['aria-label'] = ''
keys['index.tips_aria'] = keys.pop(car['data-i18n-attr'].split(':')[1])
car['data-i18n-attr'] = 'aria-label:index.tips_aria'; tekst2sleutel['Tips voor leerlingen'] = 'index.tips_aria'
tit = s.title; tit.string = 'Scheikunde en natuurkunde oefenen'
for b in s.find_all(['body']):
    b['data-pagina'] = 'index'
# 'Bouw mee': dode shorturl-links vervangen door twee zichtbare knoppen naar Google Forms (hover-menu werkt niet op telefoons)
_kb = s.find('a', attrs={'data-i18n-html': 'index.kennis_basis_vragen_kb'})
if _kb is not None:
    _rij = _kb.find_parent('div', class_='w3-row')
    _rij.replace_with(BeautifulSoup('''<br/>
<p class="bouw-knoppen"><a class="w3-button knop-blauw w3-margin-right w3-margin-bottom" data-i18n="index.kennis_basis_vragen_kb" href="https://docs.google.com/forms/d/e/1FAIpQLScNvaeo7U68JrZL5Ah4McmxnhiRVwfwodPeCoIvTznsYVINww/viewform" rel="noopener" target="_blank"></a> <a class="w3-button knop-blauw w3-margin-bottom" data-i18n="index.multiple_choice_mp" href="https://docs.google.com/forms/d/e/1FAIpQLSeurJFsNKEny9DQ1jdjg5db8JRdYB63OIeMp3Et4gsC5FzlbQ/viewform" rel="noopener" target="_blank"></a></p>''', 'html.parser'))
# Thema 'Klimaatcrisis': dode shorturl-link vervangen door het Google Form 'Klimaatverandering' (NL) / 'Climate change' (EN, via ui.json-sleutel index.klimaatcrisis_href)
for _a in s.find_all('a', href='http://www.shorturl.at/motR0'):
    _a['href'] = 'https://docs.google.com/forms/d/e/1FAIpQLSd4PXOavgX6V543qbkOmy8MxyS5pHjNA50CFyZFEqMx6oQZjw/viewform'; _a['rel'] = 'noopener'; _a['data-i18n-attr'] = 'href:index.klimaatcrisis_href'
# Rustiger voorpagina (Peter): geen kleine iconen boven de leerjaar-kaarten; de grote sectie-iconen blijven
for _i in s.find_all('i', class_='fa-solid'):
    _par = _i.parent
    _kaart = _par.name == 'div' and any(c in (_par.get('class') or []) for c in ('w3-third', 'w3-half', 'w3-quarter'))
    _themakaart = _par.name == 'div' and 'w3-row' in (_par.get('class') or []) and 'fa-folder-open' in (_i.get('class') or [])
    if not _i.get('style') and (_kaart or _themakaart):
        _i.decompose()
out = str(s)
out = out.replace(' aria-label=""', '')
open('index.html', 'w', encoding='utf-8').write(out)
json.dump(keys, open('tools/index-sleutels-nl.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(keys), 'sleutels')
