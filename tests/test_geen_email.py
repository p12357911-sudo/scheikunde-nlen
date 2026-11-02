"""Nergens op de site mag een e-mailadres, mailto: of email.php staan (ook niet in JSON, JS, PDF's of docx).
De contactsectie heeft een knop (opent in een nieuw tabblad, geen ingesloten iframe) naar het Google Form (NL: 'Stuur een bericht', EN: 'Send a message').
Uitvoeren: python3 tests/test_geen_email.py   (zonder browser)"""
import os, re, sys, glob, subprocess, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}')
fouten = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in ('.git', 'screens', '__pycache__', 'tools')]
    for f in fn:
        p = os.path.join(dp, f); rel = os.path.relpath(p, ROOT)
        if rel.startswith('tests/'): continue
        if f.endswith('.pdf'):
            t = subprocess.run(['pdftotext', p, '-'], capture_output=True, text=True).stdout
        elif f.endswith('.docx'):
            t = ''.join(zipfile.ZipFile(p).read(n).decode('utf8', 'ignore') for n in zipfile.ZipFile(p).namelist() if n.endswith('.xml'))
        elif f.endswith(('.html', '.js', '.json', '.css', '.md', '.txt', '.php')):
            t = open(p, encoding='utf8', errors='ignore').read()
        else: continue
        if f == 'email.php' or 'email.php' in t or 'mailto:' in t.lower(): fouten.append((rel, 'mailto/email.php'))
        for m in EMAIL.findall(t):
            fouten.append((rel, m))
# plaatshouder aanwezig in index.html en in beide talen vertaald
idx = open(f'{ROOT}/index.html', encoding='utf8').read()
FORM = 'https://docs.google.com/forms/d/e/1FAIpQLScy7x5-wDjjU_n95WEmYg2VHq_fNlyu9uda95-GUQ4pCbNwgw/viewform'
if f'href="{FORM}"' not in idx or '<iframe' in idx or 'embedded=true' in idx: fouten.append(('index.html', 'Google Form-knop ontbreekt of er staat nog een iframe op de contactpagina'))
if 'TODO-FORMULIER' in idx: fouten.append(('index.html', 'plaatshouder TODO-FORMULIER staat er nog'))
import json
for t, tekst in (('nl', 'Stuur een bericht'), ('en', 'Send a message')):
    ui = json.load(open(f'{ROOT}/lang/{t}/ui.json'))
    if tekst not in ui.values(): fouten.append((t, f'knoptekst "{tekst}" ontbreekt in ui.json'))
print('geen-email:', 'OK' if not fouten else f'{len(fouten)} problemen')
for x in fouten[:20]: print(' ', x)
sys.exit(1 if fouten else 0)
