"""Targeted full-label page verification after overlap correction; isolated Chrome."""
from pathlib import Path
PREFIX=Path(__file__).with_name('check-browser.py').read_text().split('\ntry:\n server=',1)[0]
exec(compile(PREFIX,'viewport-browser-prepared-definitions','exec'))
try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 profile=Path(tempfile.mkdtemp(prefix='namelecule-vp-board-labels-',dir='/private/tmp'));log=(DEST/'chrome.log').open('w')
 browser=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--no-first-run','--no-default-browser-check','--user-data-dir='+str(profile),'--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--window-size=1500,1000','about:blank'],stdout=log,stderr=subprocess.STDOUT)
 end=time.monotonic()+35
 while not (profile/'DevToolsActivePort').is_file():
  if browser.poll() is not None or time.monotonic()>end:raise RuntimeError('Owned Chrome failed startup')
  time.sleep(.1)
 port=int((profile/'DevToolsActivePort').read_text().splitlines()[0]);ctx,connection=connect_target()
 OUT['process']={'pid':browser.pid,'profile':str(profile),'serverPort':server.server_port,'debugPort':port};print(json.dumps(OUT['process']),flush=True)
 view(390,700);page('games/molecular-puzzle.html');wait('document.querySelectorAll("[data-level]").length===3',120);check('Initial chooser replaces board',ev('getComputedStyle(document.querySelector(".puzzle-assembly-panel")).display==="none"'));click('[data-level="3"]');ready('puzzle')
 for stage in ['help','name']:
  click('.puzzle-view-nav button[data-view="'+stage+'"]');check('Puzzle '+stage+' replaces assembly panel',ev('getComputedStyle(document.querySelector(".puzzle-assembly-panel")).display==="none"'))
 click('.puzzle-view-nav button[data-view="editing"]')
 check('Ordinary empty board has no artificial pages',not ev('document.querySelector(".puzzle-assembly-content>.nl-vp-pager").classList.contains("is-overflow")'))
 click('.puzzle-view-nav button[data-view="pieces"]')
 for _ in range(32):click('[data-hydrogens="4"]')
 click('.puzzle-view-nav button[data-view="editing"]')
 for width,height in [(390,700),(390,650)]:
  view(width,height);seen=set();rects=[]
  pager='.puzzle-assembly-content>.nl-vp-pager';previous=pager+' .nl-vp-pager-nav button:first-child';next_button=pager+' .nl-vp-pager-nav button:last-child'
  while visible(previous) and not ev('document.querySelector('+json.dumps(previous)+').disabled'):click(previous)
  for _ in range(50):
   state=ev('''(()=>{const port=document.querySelector('.puzzle-board-port'),p=port.getBoundingClientRect();return{port:p.toJSON(),top:port.scrollTop,nodes:[...document.querySelectorAll('#board-nodes button')].map(e=>{const r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;return{id:e.dataset.nodeId,rect:r.toJSON(),full:r.left>=p.left-.5&&r.right<=p.right+.5&&r.top>=p.top-.5&&r.bottom<=p.bottom+.5&&e.contains(document.elementFromPoint(x,y))}})}})()''')
   rects.append(state);seen.update(n['id'] for n in state['nodes'] if n['full'])
   if not visible(next_button) or ev('document.querySelector('+json.dumps(next_button)+').disabled'):break
   click(next_button)
  OUT.setdefault('fullRectangleRuns',[]).append({'width':width,'height':height,'fullyVisibleCount':len(seen),'pages':rects})
  check('All32 complete labels accessible at '+str((width,height)),len(seen)==32,{'fullCount':len(seen),'pages':len(rects),'portHeight':rects[0]['port']['height']})
  screenshot('puzzle32-full-labels-'+str(height))
  check('Node coordinates agree with bond surface after paging/resize',ev('''(()=>{const b=document.getElementById('board-svg').getBoundingClientRect();return [...document.querySelectorAll('#board-nodes button')].every(e=>{const r=e.getBoundingClientRect(),x=parseFloat(e.style.left)/100*b.width+b.x,y=parseFloat(e.style.top)/100*b.height+b.y;return Math.abs(r.x+r.width/2-x)<.6&&Math.abs(r.y+r.height/2-y)<.6})})()'''))
 view(390,700);click('.nl-game-levels__change');click('[data-level="1"]');ready('puzzle')
 for _ in range(5):
  if ev('document.getElementById("target-name").textContent')=='μεθάνιο':break
  click('#next-molecule');ready('puzzle')
 click('.puzzle-view-nav button[data-view="pieces"]');click('[data-hydrogens="4"]');click('.puzzle-view-nav button[data-view="editing"]')
 check('Methane complete label visible without paging',ev('''(()=>{const p=document.querySelector('.puzzle-board-port').getBoundingClientRect(),r=document.querySelector('#board-nodes button').getBoundingClientRect();return r.left>=p.left&&r.right<=p.right&&r.top>=p.top&&r.bottom<=p.bottom&&!document.querySelector('.puzzle-assembly-content>.nl-vp-pager').classList.contains('is-overflow')})()'''))
 click('#check-answer');wait('document.getElementById("feedback").classList.contains("success")');check('Feedback replaces assembly panel',ev('getComputedStyle(document.querySelector(".puzzle-assembly-panel")).display==="none"'));measure('puzzle','targeted-correct-methane');screenshot('targeted-correct-methane')
 page('games/name-builder.html');wait('document.querySelectorAll("[data-level]").length===3',120);click('[data-level="3"]');ready('builder');click('.builder-view-nav button[data-view="molecule"]');check('Builder molecule inspection replaces answer and spans width',ev('getComputedStyle(document.querySelector(".answer-panel")).display==="none"&&document.querySelector(".molecule-panel").getBoundingClientRect().width>innerWidth-30'));measure('builder','targeted-molecule-only');screenshot('targeted-builder-molecule')
 check('No runtime JavaScript exceptions',not js_errors,js_errors);OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 if browser and browser.poll() is None:
  try:measure('puzzle','failure');screenshot('failure')
  except Exception as capture:OUT['captureFailure']=repr(capture)
finally:
 for c in connections:
  try:c.sock.close()
  except Exception:pass
 if browser:
  browser.terminate()
  try:browser.wait(timeout=12)
  except subprocess.TimeoutExpired:browser.kill();browser.wait(timeout=8)
 if server:server.shutdown();server.server_close()
 if log:log.close()
 if profile and profile.exists():shutil.rmtree(profile)
 OUT['cleanup']={'browserExited':browser is None or browser.poll() is not None,'profileRemoved':profile is None or not profile.exists(),'serverClosed':True}
 OUT['sourceAfterSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths};OUT['sourceUnchangedDuringBrowser']=OUT['sourceAfterSHA256']==OUT['sourceSHA256'];OUT['jsErrors']=js_errors
 (DEST/'results.json').write_text(json.dumps(OUT,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'result':str(DEST/'results.json'),'cleanup':OUT['cleanup']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
