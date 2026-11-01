import sys, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
root='/workspace/website/nlen'; taal=sys.argv[1] if len(sys.argv)>1 else 'nl'
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=socketserver.ThreadingTCPServer(('127.0.0.1',0),functools.partial(Q,directory=root))
port=srv.server_address[1]; threading.Thread(target=srv.serve_forever,daemon=True).start()
import glob,os,re
pages=sorted(os.path.basename(f)[:-5] for f in glob.glob(root+'/*.html') if re.match(r'(sk|nk|rv)\d[a-z]-.*-MP(AI)?\.html$',os.path.basename(f)) and 'http-equiv="refresh"' not in open(f).read())
print(len(pages),"paginas")
ok=True
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for pg in pages:
      for nm,vp,mob in (('desktop',{'width':1280,'height':800},False),('mobiel',{'width':390,'height':844},True)):
        ctx=b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); page=ctx.new_page(); errs=[]
        page.on('pageerror',lambda e:errs.append(str(e)))
        page.goto(f'http://127.0.0.1:{port}/{pg}.html?lang='+taal); page.wait_for_timeout(1500)
        n=page.evaluate("document.querySelectorAll('.answers').length")
        def pick(good):
            page.evaluate("""g=>{const norm=h=>{const d=document.createElement('div');d.innerHTML=h;return d.innerHTML};
              document.querySelectorAll('.answers').forEach(a=>{const idx=+a.querySelector('input').name.replace('question','');const q=myQuestions[idx];
              const goodT=norm(q.answers[q.correctAnswer]);
              const labs=[...a.querySelectorAll('label')];
              const isGood=l=>{const c=l.cloneNode(true);c.querySelector('input').remove();return norm(c.innerHTML.replace(/^[a-h]: /,''))===goodT};
              const pickL=labs.find(l=>g?isGood(l):!isGood(l));pickL.querySelector('input').checked=true;});}""",good)
        pick(True); page.locator('#submit').scroll_into_view_if_needed(); page.locator('#submit').click(); r1=page.inner_text('#results')
        pick(False); page.locator('#submit').click(); r0=page.inner_text('#results')
        # real tap on label of a radio row
        page.reload(); page.wait_for_timeout(600)
        first=page.locator('.answers label').first
        first.scroll_into_view_if_needed()
        bb=first.bounding_box()
        if mob: page.touchscreen.tap(bb['x']+bb['width']-8,bb['y']+bb['height']/2)
        else: page.mouse.click(bb['x']+bb['width']-8,bb['y']+bb['height']/2)
        tapped=page.evaluate("document.querySelectorAll('.answers input:checked').length")
        wis=page.evaluate("[...document.querySelectorAll('nav.oefen-wissel a')].map(a=>a.getAttribute('href')+'|'+a.getAttribute('aria-current'))")
        kbp=pg[:-2]+'KB.html'
        wisok=(len(wis)==2 and wis[0].startswith(kbp) and wis[1]==pg+'.html|page') if re.search('href="'+kbp+'"',open(root+'/index.html').read()) else (len(wis) in (0,2))
        mm=re.match(r'(\d+)\D+?(\d+)',r1); good=bool(mm and mm.group(1)==mm.group(2) and r0.startswith('0 ') and tapped==1 and not errs and wisok)
        print(pg,nm,'vragen',n,'|',r1,'|',r0,'| tik op rechterrand rij ->',tapped,'| fouten',errs,'OK' if good else 'FOUT')
        ok&=good; ctx.close()
print('ALLES OK' if ok else 'FOUT')
