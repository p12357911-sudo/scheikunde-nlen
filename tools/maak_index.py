#!/usr/bin/env python3
"""Maakt index.html (skelet met data-i18n-html) en lang/nl/index-sleutels.json uit de basislijn-index.
De contactsectie wordt met de hand gebouwd (geen e-mailadres, Google Form)."""
import sys, re, json, copy
from bs4 import BeautifulSoup, NavigableString, Tag
SRC = sys.argv[1]; V = '20261101e'
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
            <p><a class="w3-button knop-blauw contact-formulier" href="https://docs.google.com/forms/d/e/1FAIpQLScy7x5-wDjjU_n95WEmYg2VHq_fNlyu9uda95-GUQ4pCbNwgw/viewform" target="_blank" rel="noopener" data-i18n="index.stuur_een_bericht"></a></p>
            <iframe class="contact-formulier-frame" src="https://docs.google.com/forms/d/e/1FAIpQLScy7x5-wDjjU_n95WEmYg2VHq_fNlyu9uda95-GUQ4pCbNwgw/viewform?embedded=true" width="100%" height="900" frameborder="0" loading="lazy" data-i18n-attr="title:index.formulier_titel"></iframe>''', 'html.parser'))
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
tit = s.title; tit.string = 'betermetpeter'
for b in s.find_all(['body']):
    b['data-pagina'] = 'index'
out = str(s)
out = out.replace(' aria-label=""', '')
open('index.html', 'w', encoding='utf-8').write(out)
json.dump(keys, open('tools/index-sleutels-nl.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(keys), 'sleutels')
