#!/usr/bin/env python3
"""Voegt basis-UI (pilot) + index-sleutels samen tot lang/nl/ui.json en lang/en/ui.json."""
import json, sys, importlib.util
sys.path.insert(0, 'tools')
from ui_en_index import EN as ENI
P = '../en-pilot/lang/'
nl = json.load(open(P + 'nl/ui.json')); en = json.load(open(P + 'en/ui.json'))
for d in (nl, en):
    for k in [k for k in d if k.startswith('index.')]: del d[k]
extra_nl = {
 'nav.nask': 'NaSk', 'nav.natuurkunde': 'Natuurkunde', 'nav.biologie': 'Biologie', 'nav.nederlands': 'Nederlands',
 'nav.themas': "Thema's", 'nav.spelletjes': 'Spelletjes', 'nav.bouw': 'Bouw mee',
}
extra_en = {
 'nav.nask': 'Science basics', 'nav.natuurkunde': 'Physics', 'nav.biologie': 'Biology', 'nav.nederlands': 'Dutch',
 'nav.themas': 'Themes', 'nav.spelletjes': 'Games', 'nav.bouw': 'Contribute',
}
nl.update(extra_nl); en.update(extra_en)
nl['pagina.niet_vertaald'] = 'Deze pagina is nog niet vertaald.'
en['pagina.niet_vertaald'] = 'This page has not been translated yet. The Dutch original is shown.'
nl['voet.powered'] = 'Powered by'
inl = json.load(open('tools/index-sleutels-nl.json'))
assert set(inl) == set(ENI), (set(inl) ^ set(ENI))
nl.update(inl); en.update(ENI)
nl['index.klimaatcrisis_href'] = 'https://docs.google.com/forms/d/e/1FAIpQLSd4PXOavgX6V543qbkOmy8MxyS5pHjNA50CFyZFEqMx6oQZjw/viewform'; en['index.klimaatcrisis_href'] = 'https://docs.google.com/forms/d/e/1FAIpQLSema22eYE12utIBLOnGAvGdRWq0KnJ_9eayoWXE9sNvSfuJ2w/viewform'
nl['index.proef'] = 'Proefversie – nog niet live'
# leeftijdsregels: NL toont geen leeftijd, dus geen extra sleutels nodig
json.dump(nl, open('lang/nl/ui.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(en, open('lang/en/ui.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(nl), len(en))
