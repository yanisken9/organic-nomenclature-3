"""Real before/after font and large-construction resize regression checks."""
from pathlib import Path
import textwrap
source=(Path(__file__).parent/'verify.py').read_text()
exec(compile(source.split('\ntry:\n    server=')[0],str(Path(__file__)),'exec'))
mode=os.environ.get('PUZZLE_CORRECTION_MODE','after')
OUT={'checks':[], 'mode':mode, 'scope':'Real trusted 10-piece graph UI plus unsolved/solved resize. FontFaceSet and rendered glyph metrics, not computed family alone.'}
bootstrap=source.split('\ntry:\n')[1].split('    viewport(1440,1000)')[0].replace("(HERE/'firefox.log')","(HERE/('correction-'+mode+'-firefox.log'))")
def geometry():return read('(()=>{const r=[...document.querySelectorAll("#board-nodes button")].map(e=>e.getBoundingClientRect());const b=document.querySelector("#assembly-board").getBoundingClientRect();let overlap=[];r.forEach((a,i)=>r.forEach((c,j)=>{if(j>i&&Math.min(a.right,c.right)-Math.max(a.left,c.left)>1&&Math.min(a.bottom,c.bottom)-Math.max(a.top,c.top)>1)overlap.push([i,j])}));return{count:r.length,bonds:document.querySelectorAll("#board-svg .puzzle-bond:not(.puzzle-bond-hit)").length,overlap,clipped:r.map((a,i)=>({i,clipped:a.left<b.left||a.right>b.right||a.top<b.top||a.bottom>b.bottom})).filter(a=>a.clipped),board:{width:b.width,height:b.height}}})()')
try:
    exec(compile(textwrap.dedent(bootstrap),str(Path(__file__)),'exec'))
    viewport(1440,1000);navigate('games/molecular-puzzle.html')
    until('!document.querySelector("#next-molecule").disabled',40)
    # Parentless embedded-mode title document must register and actually load faces.
    OUT['fontFaces']=json.loads(ev('(async()=>{const faces=await document.fonts.load(\'700 40px "Roboto Condensed"\',"Μοριακό παζλ");const c=document.createElement("canvas").getContext("2d");c.font=\'700 40px "Roboto Condensed",sans-serif\';const actual=c.measureText("Μοριακό παζλ").width;c.font="700 40px sans-serif";return JSON.stringify({count:faces.length,faces:faces.map(f=>({family:f.family,status:f.status})),actualWidth:actual,fallbackWidth:c.measureText("Μοριακό παζλ").width})})()'))
    for _ in range(7):click('#next-molecule')
    target=json.loads(ev('(async()=>{const c=await(await fetch("data/alkane-structures.json")).json();return JSON.stringify(NameleculeMolecularPuzzleEngine.parseMol(c.molecules[7].mol))})()'))
    build(target)
    desktop=geometry();OUT['desktop']=desktop
    viewport(320,680);time.sleep(.35);small=geometry();OUT['unsolved320']=small
    shot('correction-'+mode+'-unsolved320.png')
    viewport(1440,1000);click('#check-answer');check(state()['solved'],'real largest graph correctly graded before solved resize')
    viewport(320,680);time.sleep(.35);small_solved=geometry();OUT['solved320']=small_solved
    shot('correction-'+mode+'-solved320.png')
    check(small['count']==10 and small['bonds']==9 and small_solved['count']==10 and small_solved['bonds']==9,'resize preserves all10groups and9bonds')
    if mode=='before':
        check(OUT['fontFaces']['count']==0,'reproduced no loaded heading font faces despite declaredfamily')
        check(bool(small['overlap'] or small['clipped']),'reproduced actual unsolved large construction overlap/clipping')
        OUT['reproduced']=True
    else:
        check(OUT['fontFaces']['count']>0 and all(f['status']=='loaded' for f in OUT['fontFaces']['faces']),'actual Roboto Condensed faces loaded')
        check(abs(OUT['fontFaces']['actualWidth']-OUT['fontFaces']['fallbackWidth'])>1,'actual heading glyph metrics differ from fallback')
        check(not small['overlap'] and not small['clipped'],'unsolved320 whole labels separated and framed')
        check(not small_solved['overlap'] and not small_solved['clipped'],'solved320 locked labels separated and framed')
        viewport(390,844);time.sleep(.25);g=geometry();check(not g['overlap'] and not g['clipped'],'solved390 geometry safe')
        viewport(1440,1000);time.sleep(.25);g=geometry();check(not g['overlap'] and not g['clipped'],'return desktop geometry safe')
        # Compare real face registrations/metrics in both preview documents.
        navigate('design/molecular-puzzle-preview.html')
        until('document.querySelector("iframe").contentDocument.querySelector("#round-select").options.length===8',40)
        font=json.loads(ev('(async()=>{const child=document.querySelector("iframe").contentDocument;const f=await document.fonts.load(\'700 40px "Roboto Condensed"\',"Μοριακό παζλ");const g=await child.fonts.load(\'700 40px "Roboto Condensed"\',"Μοριακό παζλ");function width(d){const c=d.createElement("canvas").getContext("2d");c.font=\'700 40px "Roboto Condensed"\';return c.measureText("Μοριακό παζλ").width}return JSON.stringify({parentFaces:f.length,childFaces:g.length,parentWidth:width(document),childWidth:width(child)})})()'))
        OUT['previewFontParity']=font
        check(font['parentFaces']>0 and font['childFaces']>0 and abs(font['parentWidth']-font['childWidth'])<.1,'parent and child actual font render identically')
        rendered=read('(()=>{const d=document.querySelector("iframe").contentDocument;const box=document.createElement("div");box.className="nl-builder-title";box.style.cssText="position:absolute;visibility:hidden;left:0;top:0";const h=document.createElement("h2");h.className="nl-builder-heading";h.textContent="Μοριακό παζλ";box.append(h);document.body.append(box);function width(e){const r=e.ownerDocument.createRange();r.selectNodeContents(e);return r.getBoundingClientRect().width}const a=width(h),b=width(d.querySelector("#game-title"));box.remove();return{existingBuilderHeadingTextWidth:a,puzzleHeadingTextWidth:b}})()')
        OUT['actualRenderedTextParity']=rendered
        check(abs(rendered['existingBuilderHeadingTextWidth']-rendered['puzzleHeadingTextWidth'])<.1,'actual puzzle heading glyph width matches existing Builder heading rule')
        shot('corrected-font-preview.png')
        # Maximum supported piece count also fits after desktop/phone transitions.
        navigate('games/molecular-puzzle.html?embedded=1');until('!document.querySelector("#next-molecule").disabled',40)
        viewport(320,680)
        for _ in range(32):click('[data-hydrogens="0"]')
        g=geometry();check(g['count']==32 and not g['overlap'] and not g['clipped'],'all32 supported learner groups framed on320 with surface expansion')
        check(ev('[...document.querySelectorAll("[data-hydrogens]")].every(e=>e.disabled)'),'palette respects32group bound')
        click('#undo-action');g=geometry();check(g['count']==31 and not g['overlap'] and not g['clipped'],'undo also uses safe whole-candidate framing')
        viewport(1440,1000);time.sleep(.25);g=geometry();check(not g['overlap'] and not g['clipped'],'31groups returndesktop without label overlap')
    OUT['completed']=True
except Exception:
    OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
finally:
    OUT['javascriptErrors']=globals().get('js_errors',[])
    if firefox is not None and firefox.poll() is None:
        firefox.terminate()
        try:firefox.wait(timeout=8)
        except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=5)
    if server:server.shutdown();server.server_close()
    if log:log.close()
    OUT['ownedBrowserExited']=firefox is None or firefox.poll() is not None
    (HERE/('correction-'+mode+'-results.json')).write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'mode':mode,'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'javascriptErrors':len(OUT['javascriptErrors']),'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
