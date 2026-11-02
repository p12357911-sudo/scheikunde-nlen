#!/usr/bin/env python3
"""Zet de bestaande NL-pagina's (basislijn) om in een skelet-HTML + lang/nl/<pagina>.json.
Gebruik: extract.py <basislijnmap> <doelmap>
Schrijft ook tools/manifest.json (kenmerken per pagina: wissel, opnieuw, ai, vrij ...)."""
import sys, os, re, glob, json, subprocess
from bs4 import BeautifulSoup

SRC, DST = sys.argv[1], sys.argv[2]
V = '20261102d'

def inner(el): return ''.join(str(c) for c in el.contents).strip()

def js_array(text, naam='myQuestions'):
    i = text.index('var ' + naam + ' =') + len('var ' + naam + ' =')
    i = text.index('[', i); d = 0; q = None; j = i; esc = False
    while True:
        ch = text[j]
        if q:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == q: q = None
        else:
            if ch in '\'"`': q = ch
            elif ch == '[': d += 1
            elif ch == ']':
                d -= 1
                if d == 0: break
        j += 1
    r = subprocess.run(['node', '-e', 'var q=' + text[i:j+1] + ';console.log(JSON.stringify(q))'], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)

KOP = lambda title, body_attrs, body: f'''<!DOCTYPE html>
<html lang="nl">
<head>
<title>{title}</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/x-icon" href="123S.ico">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<link rel="stylesheet" href="https://www.w3schools.com/lib/w3-theme-black.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<link rel="stylesheet" href="123school.css?v={V}">
<script src="i18n.js?v={V}"></script>
</head>
<body id="myPage" {body_attrs}>
{body}
</body>
</html>
'''

manifest = {}
stubs = []
for f in sorted(glob.glob(SRC + '/*.html')):
    naam = os.path.basename(f)[:-5]
    t = open(f, encoding='utf-8').read()
    if 'http-equiv="refresh"' in t and len(t) < 1500:
        stubs.append(naam); continue
    if naam in ('index', 'navbar', 'puzzel-moleculaire-stoffen'): continue
    s = BeautifulSoup(t, 'html.parser')
    kb = 'vraag-knop' in t
    mp = (not kb) and 'myQuestions' in t
    if not (kb or mp): print('OVERGESLAGEN', naam); continue
    m = {'soort': 'kb' if kb else 'mp'}
    nav = s.select_one('nav.oefen-wissel')
    if nav:
        h = [a['href'][:-5] for a in nav.find_all('a')]
        m['wissel'] = h
    ai = 'ai-nakijken.js' in t
    m['ai'] = ai
    title = s.title.text.strip()
    d = {'title': title}
    if kb:
        h2 = s.find('h2'); cont = h2.parent
        d['heading'] = inner(h2)
        d['intro'] = [inner(p) for p in cont.find_all('p', recursive=False) if p.get('id') not in ('ai-intro', 'ai-vergelijk')]   # die komen uit ui.json (ai.intro/ai.privacy) via ai-nakijken.js
        qs = []; vrij = []
        for i, knop in enumerate(s.select('button.vraag-knop')):
            blok = knop.parent
            box = blok.select_one('.antwoord-box')
            if box.get('id') != 'Demo%d' % (i + 1): m.setdefault('id_genormaliseerd', 0); m['id_genormaliseerd'] += 1
            ps = box.find_all('p', recursive=False)
            main = [p for p in ps if 'uitleg' not in (p.get('class') or [])]
            uit = [p for p in ps if 'uitleg' in (p.get('class') or [])]
            assert len(main) == 1 and len(uit) <= 1, naam
            q = {'q': inner(knop), 'a': inner(main[0])}
            tb = [c for c in box.children if getattr(c, 'name', None) == 'table']
            assert len(tb) <= 1, naam
            if tb: q['tabel'] = re.sub(r'\s+', ' ', str(tb[0])).strip()
            if main[0].get('class'): q['pc'] = ' '.join(main[0]['class'])
            if uit: q['e'] = re.sub(r'^Uitleg:\s*', '', inner(uit[0]))
            if box.get('data-goed'): q['goed'] = box['data-goed'].split('|')
            oc = knop.get('onclick', '')
            if 'this' not in oc: vrij.append(i)
            qs.append(q)
        d['questions'] = qs
        if vrij: m['vrij'] = 'alle' if len(vrij) == len(qs) else vrij
        opn = [a for a in s.select('a.knop-blauw') if 'oefenen' in a.text.lower()]
        m['opnieuw'] = bool(opn)
        m['opnieuw_wrap'] = (' '.join(opn[0].parent.get('class') or [])) if opn else ''
        if opn: assert opn[0]['href'] == naam + '.html', (naam, opn[0]['href'])
    else:
        cont = s.select_one('#quiz').parent
        em = cont.find('em') or cont.find('h2')
        d['heading'] = inner(em)
        d['intro'] = [inner(p) for p in cont.find_all('p', recursive=False)]
        d['questions'] = js_array(t)
        kn = s.select_one('#submit')
        if kn and kn.text.strip() != 'Controleer nu': d['knop'] = kn.text.strip()
        m['kop'] = em.name
        m['cont_id'] = cont.get('id'); m['cont_class'] = ' '.join(cont.get('class') or [])
        m['br'] = len(cont.find_all('br', recursive=False))
        m['opnieuw'] = bool([a for a in cont.find_all('a', recursive=False) if 'knop-blauw' in (a.get('class') or [])])
        m['fixed'] = any('fixed' in q for q in d['questions'])
    manifest[naam] = m
    os.makedirs(DST + '/lang/nl', exist_ok=True)
    json.dump(d, open(f'{DST}/lang/nl/{naam}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---- skelet ----
    wis = ''
    if 'wissel' in m:
        wis = f'<nav class="oefen-wissel" data-kb="{m["wissel"][0]}" data-mp="{m["wissel"][1]}"></nav>\n'
    vrij_attr = ''
    if m.get('vrij'): vrij_attr = ' data-vrij="%s"' % (m['vrij'] if m['vrij'] == 'alle' else ','.join(map(str, m['vrij'])))
    if kb:
        body = '<div id="navbar"></div>\n' + wis + '<br>\n<div id="inhoud"></div>\n'
        if m['opnieuw']:
            body += '<div class="%s">\n<a class="w3-button knop-blauw" href="%s.html" data-i18n="kb.opnieuw"></a>\n</div>\n' % (m['opnieuw_wrap'] or 'w3-container w3-padding-64 w3-center', naam)
        body += '<div id="voet"></div>\n\n<script src="school.js?v=%s"></script>\n' % V
        if ai: body += '<script src="ai-nakijken.js?v=%s" defer></script>\n' % V
        attrs = f'data-pagina="kb" data-inhoud="{naam}"{vrij_attr}'
    else:
        brs = '<br>' * 0
        kop = '<em id="mp-kop"></em>' if m['kop'] == 'em' else '<h2 id="mp-kop"></h2>'
        intro = ''.join('<p data-mp-intro="%d"></p>\n    ' % i for i in range(len(d['intro'])))
        brtxt = '<br><br>\n    ' if m['br'] else ''
        opn = ('<a class="w3-button knop-blauw" href="%s.html" data-i18n="kb.opnieuw"></a>\n    ' % naam) if m['opnieuw'] else ''
        cid = f' id="{m["cont_id"]}"' if m['cont_id'] else ''
        body = f'''<div id="navbar"></div>
{wis}
<div class="{m['cont_class']}"{cid}>
    {kop}
    {intro}{brtxt}<div id="quiz"></div>
    <button id="submit" class="w3-button knop-blauw"></button>
    {opn}<div id="results" role="status" aria-live="polite"></div>
</div>
<div id="voet"></div>

<script src="school.js?v={V}"></script>'''
        attrs = f'data-pagina="mp" data-inhoud="{naam}"'
    open(f'{DST}/{naam}.html', 'w', encoding='utf-8').write(KOP('123 school', attrs, '<!-- Alle tekst komt uit lang/<taal>/ui.json en lang/<taal>/%s.json (i18n.js) -->\n' % naam + body))
json.dump({'pagina': manifest, 'stubs': stubs}, open(os.path.dirname(os.path.abspath(__file__)) + '/manifest.json', 'w'), indent=1)
print(len(manifest), 'pagina\'s;', len(stubs), 'doorverwijzingen')
