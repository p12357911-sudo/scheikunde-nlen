"""Controle op de echte GitHub Pages-adressen: pagina's laden in NL en EN zonder JS-fouten, contactformulier-knop,
en één echte AI-aanroep per taal (kost 2 Gemini-verzoeken). Uitvoeren: /workspace/pwenv/bin/python tests/live_check.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import browser, sync_playwright
BASE = 'https://p12357911-sudo.github.io/scheikunde-nlen'
PAGINAS = ['index', 'sk3t-stoffen-KB', 'sk3t-stoffen-MP', 'rv3h-significante-cijfers-stappen-KB', 'puzzel-moleculaire-stoffen']
os.makedirs('screens', exist_ok=True)
with sync_playwright() as p:
    b = browser(p)
    for taal in ('nl', 'en'):
        for pg in PAGINAS:
            ctx = b.new_context(locale='nl-NL' if taal == 'nl' else 'en-GB'); page = ctx.new_page(); errs = []
            page.on('pageerror', lambda e: errs.append(str(e)))
            page.goto(f'{BASE}/{pg}.html?lang={taal}'); page.wait_for_timeout(3000)
            print(taal, pg, 'lang=' + page.evaluate('document.documentElement.lang'), '| titel:', page.title()[:50], '| fouten:', errs)
            if pg == 'index':
                print('  formulierknop:', page.locator('a.contact-formulier').get_attribute('href')[:60], '|', page.locator('a.contact-formulier').inner_text())
                page.screenshot(path=f'screens/live_index_{taal}.png', full_page=False)
            ctx.close()
    for taal, antw in (('nl', 'ja, koper drijft want metaal is licht'), ('en', 'yes, copper floats because metal is light')):
        ctx = b.new_context(locale='nl-NL' if taal == 'nl' else 'en-GB'); page = ctx.new_page()
        page.goto(f'{BASE}/sk3t-stoffen-KB.html?lang={taal}'); page.wait_for_timeout(2500)
        for k in range(6):
            kn = page.locator('button:has-text("More questions"), button:has-text("Meer vragen")')
            if kn.count() and kn.first.is_visible(): kn.first.click(); page.wait_for_timeout(150)
        it = page.locator('.kb-item', has=page.locator('.vraag-knop', has_text='copper' if taal == 'en' else 'koper')).first
        it.locator('input[type=text]').fill(antw)
        page.click('#kb-controleer'); page.wait_for_timeout(15000)
        o = it.locator('.kb-oordeel')
        print('AI', taal, '->', o.inner_text()[:300] if o.count() else 'geen oordeel')
        ctx.close()
    b.close()
