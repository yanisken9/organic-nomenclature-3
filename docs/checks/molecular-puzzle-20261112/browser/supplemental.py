"""Targeted touch, cancellation, readable learner placement and source-error recovery."""
from pathlib import Path
import textwrap
source=(Path(__file__).parent/'verify.py').read_text()
exec(compile(source.split('\ntry:\n    server=')[0],str(Path(__file__)),'exec'))
OUT={'checks':[], 'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'scope':'Trusted touch/mouse; induced blur is NOT native OS cancellation proof. Forced reduced-motion preference belongs only to disposable test profile. No real GUI or source mutation.'}
bootstrap=source.split('\ntry:\n')[1].split('    viewport(1440,1000)')[0]
bootstrap=bootstrap.replace("(HERE/'firefox.log')", "(HERE/'supplemental-firefox.log')")
bootstrap=bootstrap.replace("    log=(HERE/", "    (profile/'user.js').write_text('user_pref(\"ui.prefersReducedMotion\", 1);\\n')\n    log=(HERE/")
OriginalHandler=Handler
class Handler(OriginalHandler):
    broken_catalog=False
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()
    def do_GET(self):
        if self.broken_catalog and self.path.split('?')[0]=='/games/data/alkane-structures.json':
            catalog=json.loads((ROOT/'games/data/alkane-structures.json').read_text())
            catalog['molecules'][0]['mol']+='corruption injected only in test HTTP response'
            payload=json.dumps(catalog).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
        else:super().do_GET()
try:
    exec(compile(textwrap.dedent(bootstrap),str(Path(__file__)),'exec'))
    viewport(390,844);navigate('games/molecular-puzzle.html?embedded=1')
    until('!document.querySelector("#next-molecule").disabled',40);time.sleep(.4)
    check(ev('matchMedia("(prefers-reduced-motion:reduce)").matches'),'owned test profile reduced-motion preference active')
    b=read('document.querySelector("#assembly-board").getBoundingClientRect().toJSON()')
    drag_to('[data-hydrogens="3"]',round(b['left']+b['width']*.5),round(b['top']+b['height']*.5),'touch')
    check(len(state()['nodes'])==1,'trusted touch palette drag adds group')
    time.sleep(.3)
    node=state()['nodes'][0]['id'];before=state()['nodes'][0]
    p=read('(()=>{const r=document.querySelector("[data-node-id]").getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})()')
    call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[
       {'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},
       {'type':'pointerMove','x':p['x']+25,'y':p['y']+20,'duration':200}]}]})
    check(ev('!!document.querySelector(".puzzle-drag-ghost")'),'trusted drag active before induced cancellation')
    ev('window.dispatchEvent(new Event("blur"));true')
    call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerUp','button':0}]}]})
    check(state()['nodes'][0]==before and not ev('!!document.querySelector(".puzzle-drag-ghost")'),'induced blur cancels movement without removing or mutating group')
    bank=read('document.querySelector("#piece-bank").getBoundingClientRect().toJSON()')
    drag_to('[data-node-id="'+node+'"]',round(bank['left']+bank['width']*.8),round(bank['top']+bank['height']*.5),'touch')
    check(len(state()['nodes'])==0,'trusted touch outside-board release removes group')
    check(ev("!document.querySelector('[data-hydrogens=\"3\"]').disabled"),'touch-removed group remains available')
    # As a learner, place each group by trusted drags in a clear condensed layout.
    viewport(1440,1000);select_round(7)
    target=json.loads(ev('(async()=>{const c=await(await fetch("data/alkane-structures.json")).json();const m=c.molecules[7];return JSON.stringify({graph:NameleculeMolecularPuzzleEngine.parseMol(m.mol),mol:m.mol})})()'))
    lines=target['mol'].splitlines();count=int(lines[3][:3])
    points=[(float(line[:10]),-float(line[10:20])) for line in lines[4:4+count] if line[31:34].strip()=='C']
    minx=min(x for x,y in points);maxx=max(x for x,y in points);miny=min(y for x,y in points);maxy=max(y for x,y in points)
    # Relative source carbon geometry is a TEST oracle only; never exposed by game.
    for item,(x,y) in zip(target['graph']['nodes'],points):
        ev('document.querySelector("#piece-bank").scrollIntoView({block:"nearest",behavior:"instant"})')
        rect=read('document.querySelector("#assembly-board").getBoundingClientRect().toJSON()')
        px=round(rect['left']+44+(x-minx)/(maxx-minx)*(rect['width']-88))
        py=round(rect['top']+36+(y-miny)/(maxy-miny)*(rect['height']-72))
        drag_to('[data-hydrogens="'+str(item['hydrogens'])+'"]',px,py)
    check(len(state()['nodes'])==10,'10 pieces placed by trusted drags for branched molecule')
    ids=[n['id'] for n in state()['nodes']];mapping={n['id']:ids[i] for i,n in enumerate(target['graph']['nodes'])}
    click('#bond-tool')
    for edge in target['graph']['bonds']:
        click('[data-node-id="'+mapping[edge['a']]+'"]');click('[data-node-id="'+mapping[edge['b']]+'"]')
    check(state()['bonds']==9,'nine bonds constructed in readable branched layout')
    OUT['readablePositions']=state()['nodes']
    shot('largest-learner-placed.png')
    click('#fit-board')
    check(state()['bonds']==9 and len(state()['nodes'])==10,'fit preserves topology')
    click('#check-answer');check(state()['solved'],'trusted manually positioned branched construction succeeds')
    time.sleep(.3);shot('largest-learner-success.png')
    # Error injection is isolated in the temporary HTTP response. Disk bytes unchanged.
    Handler.broken_catalog=True
    navigate('games/molecular-puzzle.html')
    until('!document.querySelector("#retry-load").hidden',15)
    check(ev('document.querySelector("#check-answer").disabled && document.querySelector("#round-select").disabled'),'corrupt source cannot start a round')
    check(ev('document.querySelector("#game-status").textContent.includes("πηγής")'),'source digest mismatch explained')
    Handler.broken_catalog=False
    click('#retry-load');until('!document.querySelector("#next-molecule").disabled',40)
    check(ev('document.querySelector("#round-select").options.length===8'),'retry restores eight verified targets')
    check(state()['nodes']==[],'retry restores empty candidate')
    OUT['completed']=True
except Exception:
    OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
    try:shot('supplemental-failure.png')
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
    (HERE/'supplemental-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'javascriptErrors':len(OUT['javascriptErrors']),'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
