#!/usr/bin/env python3
"""Hulpmiddel bij het vertalen (NL -> EN).
  python3 tools/vertaal.py dump <pagina> [<pagina> ...]   toont de te vertalen teksten als 'id<TAB>tekst' (platte tekst, HTML-tags blijven staan)
  python3 tools/vertaal.py merge <bestand.txt>            leest een vertaalbestand met blokken '### <pagina>' en regels 'id<TAB>tekst'
                                                          en schrijft lang/en/<pagina>.json (zelfde structuur als lang/nl/<pagina>.json)
  python3 tools/vertaal.py kopieer <van> <naar>           (KBAI) kopieert een EN-pagina naar een andere pagina met de NL-intro van die pagina
id's: heading, intro.0, knop, <i>.q <i>.a <i>.e <i>.g<n> (goed-lijst) <i>.t (tabel) voor KB;
      <i>.Q (vraag) <i>.A/.B/.C/.D (antwoorden a-d) voor MP. De titel wordt afgeleid ('<heading> - 123 school') tenzij die in NL afwijkt ('title')."""
import json, sys, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STD = {
 "Test je kennis door je antwoord in te typen en te vergelijken met het juiste antwoord. Klik daarna op 'Controleer antwoorden'.": "Test your knowledge by typing your answer and comparing it with the correct answer. Then click 'Check answers'.",
 "Deze begrippen en berekeningen leer je door te oefenen. Alleen bij een vraag waar een Binas-tabel bij staat, gebruik je Binas.": "You learn these terms and calculations by practising. Only use BINAS when the question names a BINAS table.",
 "Alle gegevens die je nodig hebt staan in de vraag. Rond af op het juiste aantal cijfers.": "All the data you need is in the question. Round to the correct number of digits.",
 "Deze begrippen leer je uit je hoofd. Alleen bij een vraag waar een Binas-tabel bij staat, gebruik je Binas.": "You learn these terms by heart. Only use BINAS when the question names a BINAS table.",
 "Alle gegevens die je nodig hebt staan in de vraag.": "All the data you need is in the question.",
 "Alle gegevens die je nodig hebt staan in de vraag. In elke vraag staat hoe je moet afronden. Bij een stapelopdracht staat in de tip hoeveel stappen je nodig hebt.": "All the data you need is in the question. Every question tells you how to round. For a multi-step problem, the tip tells you how many steps you need.",
 "Alle gegevens die je nodig hebt staan in de vraag. In elke vraag staat hoe je moet afronden.": "All the data you need is in the question. Every question tells you how to round.",
 "Alleen bij een vraag waar een Binas-tabel bij staat, gebruik je Binas.": "Only use BINAS when the question names a BINAS table.",
}
def laad(l, p): return json.load(open(f'{ROOT}/lang/{l}/{p}.json', encoding='utf-8'))
def vlak(d):
    r = []
    if d['title'] != d['heading'] + ' - 123 school': r.append(('title', d['title']))
    r.append(('heading', d['heading']))
    for i, t in enumerate(d.get('intro', [])):
        if t not in STD: r.append((f'intro.{i}', t))
    if 'knop' in d: r.append(('knop', d['knop']))
    for i, q in enumerate(d['questions']):
        if 'question' in q:
            r.append((f'{i}.Q', q['question']))
            for k in 'abcd': r.append((f'{i}.{k.upper()}', q['answers'][k]))
        else:
            r.append((f'{i}.q', q['q']))
            if 'tabel' in q: r.append((f'{i}.t', q['tabel']))
            r.append((f'{i}.a', q['a']))
            if 'e' in q: r.append((f'{i}.e', q['e']))
            for j, g in enumerate(q.get('goed', [])): r.append((f'{i}.g{j}', g))
    return r
def bouw(nl, ids):
    d = json.loads(json.dumps(nl))
    d['heading'] = ids['heading']; d['title'] = ids.get('title', ids['heading'] + ' - 123 school')
    d['intro'] = [STD.get(t) or ids[f'intro.{i}'] for i, t in enumerate(nl.get('intro', []))]
    if 'knop' in nl: d['knop'] = ids['knop']
    for i, q in enumerate(d['questions']):
        if 'question' in q:
            q['question'] = ids[f'{i}.Q']
            for k in 'abcd': q['answers'][k] = ids[f'{i}.{k.upper()}']
        else:
            q['q'] = ids[f'{i}.q']; q['a'] = ids[f'{i}.a']
            if 'tabel' in q: q['tabel'] = ids[f'{i}.t']
            if 'e' in q: q['e'] = ids[f'{i}.e']
            if 'goed' in q: q['goed'] = [ids[f'{i}.g{j}'] for j in range(len(q['goed']))]
    return d
def schrijf(p, d):
    with open(f'{ROOT}/lang/en/{p}.json', 'w', encoding='utf-8') as f: json.dump(d, f, ensure_ascii=False, indent=1); f.write('\n')
if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'dump':
        for p in sys.argv[2:]:
            print('### ' + p)
            for k, t in vlak(laad('nl', p)): print(k + '\t' + t.replace('\n', ' '))
    elif c == 'merge':
        blok = None; ids = {}; blokken = {}
        for r in open(sys.argv[2], encoding='utf-8').read().split('\n'):
            if r.startswith('### '): blok = r[4:].strip(); blokken[blok] = {}; continue
            if not r.strip() or r.startswith('#'): continue
            m = re.match(r'(\S+)\s+(.*)$', r)
            if not m: sys.exit(f'regel zonder id in {blok}: {r[:80]}')
            k, t = m.group(1), m.group(2)
            if k in blokken[blok]: sys.exit(f'dubbele id {blok} {k}')
            blokken[blok][k] = t.strip()
        for p, ids in blokken.items():
            nl = laad('nl', p); verwacht = [k for k, _ in vlak(nl)]
            ontbreekt = [k for k in verwacht if k not in ids]; extra = [k for k in ids if k not in verwacht]
            if ontbreekt or extra: sys.exit(f'{p}: ontbreekt {ontbreekt[:10]} ({len(ontbreekt)}), extra {extra[:10]}')
            schrijf(p, bouw(nl, ids)); print('geschreven', p, len(verwacht), 'teksten')
    elif c == 'kopieer':
        en = laad('en', sys.argv[2]); nl = laad('nl', sys.argv[3]); en['intro'] = [] if not nl.get('intro') else en['intro']
        en['title'] = en['title'] if nl['title'] == laad('nl', sys.argv[2])['title'] else en['title']
        schrijf(sys.argv[3], en)
