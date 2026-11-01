import functools, http.server, socketserver, threading, os
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = '/workspace/website/wt-puzzel'   # alleen lezen: de huidige NL-pagina's (basislijn), voor de vergelijking

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def serve(root):
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return 'http://127.0.0.1:%d' % srv.server_address[1]

def browser(p):
    return p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])

def nieuwe_pagina(b, taal=None, size=None, ai_mock=None):
    """Nieuwe browsercontext. taal: kiest de taal vooraf via localStorage (zoals de knop doet)."""
    ctx = b.new_context(viewport=size or {'width': 1280, 'height': 900}, locale='nl-NL' if taal != 'en' else 'en-GB')
    if taal:
        ctx.add_init_script("try{ if(!localStorage.getItem('taal')) localStorage.setItem('taal','%s'); }catch(e){}" % taal)
    # externe CDN's (w3.css, Font Awesome) mogen ontbreken; de test hangt er niet van af
    page = ctx.new_page()
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    return ctx, page, errs
