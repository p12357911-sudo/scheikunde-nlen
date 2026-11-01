"""Alle interne verwijzingen moeten bestaan: href/src in de HTML, data-kb/data-mp, doorverwijzingen (meta refresh / location),
en de menu-ankers in i18n.js moeten op de index bestaan. Uitvoeren: python3 tests/test_linkcheck.py"""
import os, re, sys, glob, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fouten = []; n = 0
index = open(f'{ROOT}/index.html', encoding='utf8').read()
ids = set(re.findall(r'id="([^"]+)"', index))
def bestaat(doel, bron):
    doel = doel.split('?')[0]
    if doel == 'TODO-FORMULIER': return True   # bewuste plaatshouder, wordt vervangen door de Google Form-url
    if not doel or doel.startswith(('http', '//', 'mailto', 'javascript', 'data:')): return True
    if doel.startswith('#'): return doel[1:] in ids if bron == 'index.html' else True
    pad, _, anker = doel.partition('#')
    p = os.path.join(ROOT, os.path.dirname(bron), pad)
    if os.path.isdir(p): p = os.path.join(p, 'index.html')
    if not os.path.exists(p): return False
    if anker and pad.endswith('index.html') or (anker and pad == 'index.html'): return anker in ids
    return True
for f in sorted(glob.glob(f'{ROOT}/**/*.html', recursive=True)):
    rel = os.path.relpath(f, ROOT)
    if rel.startswith(('tools/', 'tests/', 'screens/')): continue
    t = open(f, encoding='utf8').read()
    cands = re.findall(r'(?:href|src)="([^"]+)"', t) + re.findall(r'data-(?:kb|mp)="([^"]+)"', t) + re.findall(r"location(?:\.href|\.replace\()?\s*=?\s*\(?['\"]([^'\"]+)['\"]", t) + re.findall(r'url=([^"\'>]+)', t)
    for c in cands:
        if re.fullmatch(r'[A-Za-z0-9_\-]+', c) and 'data-' not in c and not os.path.exists(os.path.join(ROOT, c)) and os.path.exists(os.path.join(ROOT, c + '.html')): c += '.html'
        n += 1
        if not bestaat(c, rel): fouten.append((rel, c))
js = open(f'{ROOT}/i18n.js', encoding='utf8').read()
for a in set(re.findall(r"index\.html#(\w+)|'#(\w+)'", js)):
    a = a[0] or a[1]
    if a not in ids and a not in ('myPage',): fouten.append(('i18n.js', '#' + a))
print(f'linkcheck: {n} verwijzingen gecontroleerd,', 'OK' if not fouten else f'{len(fouten)} kapot')
for x in fouten[:30]: print(' ', x)
sys.exit(1 if fouten else 0)
