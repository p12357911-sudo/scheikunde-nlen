"""Vertaal- en taalcontrole op de JSON-bestanden.
  python3 tests/taalcheck.py            -> controleert alles wat er is; pagina's zonder EN-vertaling worden geteld en getoond (niet als fout)
  python3 tests/taalcheck.py --compleet -> ontbrekende EN-pagina's tellen ook als fout (voor de eindcontrole)
Controles: zelfde sleutels in ui.json (NL/EN); per vertaalde pagina zelfde structuur als NL (aantal vragen, 'goed'-lijsten,
'e'-velden); zelfde getallen (NL-komma -> punt) en dezelfde HTML-tags; in EN geen decimale komma, geen niveau-/methodenamen,
geen Nederlandse woorden; in NL geen decimaalpunt. NL-only pagina's (NL1) en '(in Dutch)' vallen buiten de Nederlands-check."""
import json, re, glob, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPLEET = '--compleet' in sys.argv
NL_ONLY = {'NL1'}
UITZ = json.load(open(f'{ROOT}/tests/uitzonderingen.json')) if os.path.exists(f'{ROOT}/tests/uitzonderingen.json') else {}

def teksten(obj, pad=''):
    if isinstance(obj, str): yield pad, obj
    elif isinstance(obj, dict):
        for k, v in obj.items(): yield from teksten(v, pad + '/' + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj): yield from teksten(v, pad + '/' + str(i))

def kaal(t): return re.sub(r'<[^>]+>', ' ', t).replace('&nbsp;', ' ').replace('&deg;', '°').replace('&deg', '°')
def tags(t): return collections.Counter(re.findall(r'<\s*/?\s*([a-zA-Z0-9]+)', t))
def getallen(t, nl):
    t = kaal(t).replace('−', '-').replace('–', '-')
    if nl:
        t = re.sub(r'(?<=\d)\.(?=\d{3}(?!\d))', '', t)   # duizendtalpunt in NL: 1.000 -> 1000
        t = re.sub(r'(?<=\d),(?=\d)', '.', t)
    else: t = re.sub(r'(?<=\d),(?=\d{3}(?!\d))', '', t)   # duizendtalscheiding in EN: 1,000 -> 1000
    return collections.Counter(re.findall(r'\d+(?:\.\d+)?', t))
NL_WOORDEN = r'\b(het|een|niet|zijn|wordt|worden|ook|maar|deze|geen|welke|hoeveel|bereken|noem|geef|leg|stof|stoffen|mengsel|antwoord|vraag|voor|naar|bij|van de|van het|is een|zijn er)\b'
fouten = []
def fout(*a): fouten.append(a)

# 1. ui.json
ui = {t: json.load(open(f'{ROOT}/lang/{t}/ui.json')) for t in ('nl', 'en')}
for k in set(ui['nl']) ^ set(ui['en']): fout('ui.json', 'sleutel niet in beide talen', k)
for k, v in ui['en'].items():
    if k in ui['nl'] and v == ui['nl'][k] and len(v) > 12 and k not in UITZ.get('ui_gelijk', []): fout('ui.json', 'EN gelijk aan NL', k)
    if re.search(NL_WOORDEN, kaal(v)) and not k.startswith('ni.') and '(in Dutch)' not in v: fout('ui.json', 'Nederlands in EN', k + ': ' + v[:80])
    if re.search(r'\d,\d{1,2}(?!\d)', kaal(v)): fout('ui.json', 'decimale komma in EN', k)
    if re.search(r'\b(vmbo|havo|vwo|mavo|nova|polaris|kader)\b|\bbinas\b(?! tables? \d)', v, re.I): fout('ui.json', 'niveau- of methodenaam', k + ': ' + v[:80])

# 2. pagina's
nlp = sorted(os.path.basename(f)[:-5] for f in glob.glob(f'{ROOT}/lang/nl/*.json') if not f.endswith('ui.json'))
ontbreekt = []; klaar = 0
for pg in nlp:
    nl = json.load(open(f'{ROOT}/lang/nl/{pg}.json'))
    for pad, t in teksten(nl):
        for m in re.finditer(r'(?<![\d.])\d+\.\d+(?![\d.])', kaal(t)):
            if not re.fullmatch(r'\d{1,3}\.\d{3}', m.group()) and f'{pg}{pad}' not in UITZ.get('nl_punt', []): fout(pg, 'decimaalpunt in NL', f'{pad}: {kaal(t)[:80]}')
    ep = f'{ROOT}/lang/en/{pg}.json'
    if not os.path.exists(ep):
        if pg not in NL_ONLY: ontbreekt.append(pg)
        continue
    klaar += 1
    en = json.load(open(ep))
    if pg in NL_ONLY: continue
    nlt = dict(teksten(nl)); ent = dict(teksten(en))
    if set(nlt) != set(ent):
        fout(pg, 'structuur wijkt af van NL', str(sorted(set(nlt) ^ set(ent)))[:200]); continue
    for pad, t in ent.items():
        n = nlt[pad]; key = f'{pg}{pad}'
        if t == n and len(kaal(n)) > 25 and re.search(r'[a-z]{4,}', kaal(n)) and key not in UITZ.get('en_gelijk', []): fout(pg, 'EN gelijk aan NL (niet vertaald?)', pad)
        if tags(t) != tags(n) and key not in UITZ.get('tags', []): fout(pg, 'HTML-tags wijken af', f'{pad}: {dict(tags(n))} vs {dict(tags(t))}')
        if getallen(t, False) != getallen(n, True) and key not in UITZ.get('getallen', []): fout(pg, 'getallen wijken af', f'{pad}: NL {sorted(getallen(n, True).elements())} EN {sorted(getallen(t, False).elements())}')
        k = kaal(t).replace("Only use BINAS when the question names a BINAS table.", "")
        if re.search(r'\d,\d{1,2}(?!\d)', k) and key not in UITZ.get('komma', []): fout(pg, 'decimale komma in EN', f'{pad}: {k[:80]}')
        if re.search(r'\b(vmbo|havo|vwo|mavo|nova|polaris|kader|tl)\b|\bbinas\b(?! tables? \d)', k, re.I) and key not in UITZ.get('niveau', []): fout(pg, 'niveau- of methodenaam', f'{pad}: {k[:80]}')
        if re.search(NL_WOORDEN, k, re.I) and key not in UITZ.get('nederlands', []) and pad != '/heading_nl': fout(pg, 'Nederlands woord in EN', f'{pad}: {k[:100]}')
        if re.search(r'\bBINAS\b', k) and not re.search(r'BINAS tables? \d', k) and key not in UITZ.get('binas', []): fout(pg, 'BINAS zonder tabel', f'{pad}: {k[:100]}')
print(f"pagina's: {len(nlp)} NL, {klaar} met EN-vertaling, {len(ontbreekt)} zonder (EN valt terug op NL met melding)")
if COMPLEET:
    for pg in ontbreekt: fout(pg, 'EN-vertaling ontbreekt', '')
print('taalcheck:', 'OK' if not fouten else f'{len(fouten)} problemen')
for x in fouten[:60]: print(' ', x)
sys.exit(1 if fouten else 0)
