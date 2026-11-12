"""Targeted final typography and selected/solved label contrast, no chemistry changes."""
from pathlib import Path
import textwrap
source=(Path(__file__).parent/'verify.py').read_text()
exec(compile(source.split('\ntry:\n    server=')[0],str(Path(__file__)),'exec'))
OUT={'checks':[],'scope':'Final CSS only: real hover/solved labels and parent-vs-frame heading typography.'}
bootstrap=source.split('\ntry:\n')[1].split('    viewport(1440,1000)')[0].replace("(HERE/'firefox.log')","(HERE/'presentation-firefox.log')")
try:
    exec(compile(textwrap.dedent(bootstrap),str(Path(__file__)),'exec'))
    viewport(1440,1000);navigate('games/molecular-puzzle.html?embedded=1')
    until('!document.querySelector("#next-molecule").disabled',40)
    click('[data-hydrogens="4"]')
    node=read('(()=>{const r=document.querySelector("[data-node-id]").getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})()')
    call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':node['x'],'y':node['y'],'duration':0}]}]})
    style=read('(()=>{const s=getComputedStyle(document.querySelector("[data-node-id]"));return{background:s.backgroundColor,color:s.color,opacity:s.opacity}})()')
    OUT['selectedHover']=style
    check(style['background']=='rgb(37, 76, 80)' and style['color']=='rgb(255, 255, 255)','selected hovered chemical label keeps dark background and white text')
    click('#check-answer');check(state()['solved'],'final-CSS genuine methane success')
    check(ev('getComputedStyle(document.querySelector("[data-node-id]")).opacity==="1"'),'solved diagram label remains fully opaque')
    time.sleep(.8);shot('final-solved-label.png')
    navigate('design/molecular-puzzle-preview.html')
    until('document.querySelector("iframe").contentDocument.querySelector("#round-select").options.length===8',40)
    for width,height,title,objective,logo in [(1440,1000,'40px','24px',88),(760,900,'28px','20px',88),(390,844,'28px','20px',64)]:
        viewport(width,height);time.sleep(.25)
        row=read('(()=>{const d=document.querySelector("iframe").contentDocument;const w=d.defaultView;const h=w.getComputedStyle(d.querySelector("#game-title"));const o=w.getComputedStyle(d.querySelector(".objective"));return{title:h.fontSize,family:h.fontFamily,weight:h.fontWeight,lineHeight:h.lineHeight,letterSpacing:h.letterSpacing,objective:o.fontSize,logoHeight:d.querySelector(".puzzle-logo").getBoundingClientRect().height,logoLoaded:d.querySelector(".puzzle-logo").naturalWidth>0,overflow:d.documentElement.scrollWidth>w.innerWidth}})()')
        OUT.setdefault('typography',[]).append({'viewport':[width,height],**row})
        check(row['title']==title and row['objective']==objective and row['logoHeight']==logo,'existing game title/objective/logo-height parity '+str(width))
        check(row['logoLoaded'] and not row['overflow'],'logo and no frame overflow '+str(width))
    viewport(1440,1000);time.sleep(.2);shot('final-lesson-preview.png')
    OUT['completed']=True
except Exception:
    OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
    try:shot('presentation-failure.png')
    except Exception:pass
finally:
    OUT['javascriptErrors']=globals().get('js_errors',[])
    if firefox is not None and firefox.poll() is None:
        firefox.terminate()
        try:firefox.wait(timeout=8)
        except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=5)
    if server:server.shutdown();server.server_close()
    if log:log.close()
    OUT['ownedBrowserExited']=firefox is None or firefox.poll() is not None
    (HERE/'presentation-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'javascriptErrors':len(OUT['javascriptErrors']),'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
