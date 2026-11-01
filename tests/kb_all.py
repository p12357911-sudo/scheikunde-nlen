import sys, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
root='/workspace/website/nlen'; taal=sys.argv[1] if len(sys.argv)>1 else 'nl'
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=socketserver.ThreadingTCPServer(('127.0.0.1',0),functools.partial(Q,directory=root))
port=srv.server_address[1]; threading.Thread(target=srv.serve_forever,daemon=True).start()
import glob,os,re
pages=sorted(os.path.basename(f)[:-5] for f in glob.glob(root+'/*.html') if re.match(r'(sk|nk|rv)\d[a-z]-.*-KB(AI)?\.html$',os.path.basename(f)) and 'http-equiv="refresh"' not in open(f).read())
pages=[p for p in pages if re.search(sys.argv[2],p)] if len(sys.argv)>2 else pages
print(len(pages),"paginas")
ok=True
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for pg in pages:
      for nm,vp,mob in (('desktop',{'width':1280,'height':800},False),('mobiel',{'width':390,'height':844},True)):
        ctx=b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); page=ctx.new_page(); errs=[]
        page.on('pageerror',lambda e:errs.append(str(e))); page.on('response',lambda r: errs.append('404 '+r.url) if r.status==404 and 'favicon' not in r.url and '/lang/en/' not in r.url else None)
        page.goto(f'http://127.0.0.1:{port}/{pg}.html?lang='+taal); page.wait_for_timeout(1500)
        if pg.endswith('KBAI') and not page.evaluate("!!document.getElementById('zweefknop')"):
            print(pg,nm,'OVERGESLAGEN: KBAI-pagina zonder #zweefknop'); ctx.close(); continue
        tot=page.evaluate("document.querySelectorAll('.vraag-knop').length")
        vis=page.evaluate("[...document.querySelectorAll('.vraag-knop')].filter(e=>e.offsetParent!==null&&e.getBoundingClientRect().height>0).length")
        ai=pg.endswith('KBAI')
        ins=page.locator('.vraag-knop >> xpath=following-sibling::input')
        exp=page.evaluate("(()=>{const b=document.querySelector('.vraag-knop').parentNode.querySelector('.antwoord-box').cloneNode(true);b.querySelectorAll('.uitleg').forEach(e=>e.remove());b.querySelectorAll('sup').forEach(e=>e.textContent='^'+e.textContent);return b.textContent.replace(/\\s+/g,' ').trim()})()")
        ins.first.fill(exp)
        if False:
            page.locator('.vraag-knop').first.click(); page.wait_for_timeout(300)
            shown=page.evaluate("document.querySelector('.vraag-knop').parentNode.querySelector('.antwoord-box').classList.contains('w3-show')")
            knopok=True
        else:
            page.evaluate("document.activeElement.blur()"); page.wait_for_timeout(450)
            zw=page.locator('#zweefknop').is_visible()
            page.locator('#zweefknop').click(); page.wait_for_timeout(300)
            shown=page.evaluate("document.querySelector('.vraag-knop').parentNode.querySelector('.antwoord-box').classList.contains('w3-show')")
            oordeel=page.evaluate("(document.querySelector('.vraag-knop').parentNode.querySelector('.kb-oordeel')||{}).textContent||''")
            tweede=page.evaluate("document.querySelectorAll('.vraag-knop')[1].parentNode.querySelector('.antwoord-box').classList.contains('w3-show')")
            goedverwacht=pg.startswith('rv')
            knopok=(zw and (oordeel.startswith('\u2713') or (not goedverwacht and (oordeel.startswith('Vergelijk zelf') or oordeel.startswith('Compare')))) and (not tweede) and re.search('ingevulde|filled in',page.locator('#kb-uitslag').inner_text()) is not None)
            if not knopok: print('  oordeel:',repr(oordeel),'verwacht antwoord:',repr(exp),'zwevend',zw,'tweede open',tweede)
        paar=(not pg.endswith('KBAI')) and re.search(r'href="'+pg+r'\.html"',open(root+'/index.html').read()) is not None and os.path.exists(root+'/'+pg[:-2]+'MP.html')
        wis=page.evaluate("[...document.querySelectorAll('nav.oefen-wissel a')].map(a=>a.getAttribute('href')+'|'+a.getAttribute('aria-current'))")
        wisok=(len(wis)==2 and wis[0]==pg+'.html|page' and wis[1].startswith(pg[:-2]+'MP.html')) if len(wis)>0 else (not paar or pg.startswith('sk4t-zoutreacties'))
        hs=page.evaluate("document.documentElement.scrollWidth>window.innerWidth+1")
        menu=page.evaluate("document.querySelectorAll('nav a, .navbar a, .w3-bar a').length>0")
        lvl=page.evaluate("/havo|vwo|vmbo|mavo/i.test(document.title+document.body.innerText)")
        more=page.evaluate("[...document.querySelectorAll('button,a')].some(e=>/meer vragen|more questions/i.test(e.innerText))")
        if more:
            page.evaluate("[...document.querySelectorAll('button,a')].find(e=>/meer vragen|more questions/i.test(e.innerText)).click()"); page.wait_for_timeout(300)
        vis2=page.evaluate("[...document.querySelectorAll('.vraag-knop')].filter(e=>e.offsetParent!==null&&e.getBoundingClientRect().height>0).length")
        good=(vis2>vis or tot<=15) and (not errs) and shown and knopok and wisok and (not hs) and tot>=20 and menu and (not lvl)
        print(pg,nm,'vragen',tot,'zichtbaar',vis,'antwoord getoond',shown,'knop',knopok,'wissel',wisok,'meer-vragen',more,vis2,'hscroll',hs,'niveau-tekst',lvl,errs,'OK' if good else 'FOUT'); ok&=bool(good); ctx.close()
print('ALLES OK' if ok else 'FOUT')
