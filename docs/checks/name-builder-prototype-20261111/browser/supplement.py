from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'completed':False,'checks':[],'role':'Developer actual-browser evidence'}
def check(ok,label,detail=None):
 out['checks'].append({'passed':bool(ok),'label':label,'detail':detail});print(('PASS 'if ok else 'FAIL ')+label,flush=True)
 if not ok:raise AssertionError((label,detail))
def answer():return read('[...document.querySelectorAll("#answer-tiles button")].map(b=>({text:b.textContent,id:b.dataset.tileId}))')
try:
 open_page('games/name-builder.html?molecule=ethane');wait('document.querySelectorAll("#bank-tiles button").length>0')
 click('#bank-tiles li:first-child button');partial=answer()
 z=ev('document.querySelector("iframe").contentWindow.eval("molZoom2D")')
 click('#zoom-in');wait('document.querySelector("iframe").contentWindow.eval("molZoom2D")>'+str(z));click('#zoom-out');wait('document.querySelector("iframe").contentWindow.eval("molZoom2D")==='+str(z))
 check(answer()==partial,'Native 2D zoom pair preserves answer')
 # Fault injection is confined to this disposable tab and restored before retry.
 ev('(()=>{let w=document.querySelector("iframe").contentWindow;w.__savedLoad=w.fLoadMol2D;w.fLoadMol2D=()=>{throw Error("owned-test-injected-load-failure")};return true})()')
 click('[data-representation="expanded"]');wait('!document.querySelector("#retry-load").hidden')
 check(answer()==partial and ev('document.querySelector("#check-answer").disabled'),'Load failure preserves partial answer and blocks checking')
 ev('(()=>{let w=document.querySelector("iframe").contentWindow;w.fLoadMol2D=w.__savedLoad;delete w.__savedLoad;return true})()')
 click('#retry-load');wait('document.querySelector("#viewer-mask").hidden&&!document.querySelector("#check-answer").disabled')
 check(answer()==partial and ev('document.querySelector("[data-representation=expanded]").getAttribute("aria-pressed")==="true"'),'Retry recovers same representation without resetting answer')
 before=read('({a:document.querySelector("#candidate-name").textContent,e:__builderEvents.length})')
 ev('dispatchEvent(new MessageEvent("message",{origin:location.origin,source:window,data:{channel:"namelecule-name-builder-v1",session:__builderEvents[0].session,type:"error",requestId:99999}}));true')
 check(answer()==partial and ev('document.querySelector("#viewer-mask").hidden'),'Forged wrong-source reply ignored')
 click('[data-representation="3d"]');wait('document.querySelector("[data-representation=\\"3d\\"]").getAttribute("aria-pressed")==="true"&&!document.querySelector("#check-answer").disabled',35)
 diag=read('(()=>{let w=document.querySelector("iframe").contentWindow;return{orientation:w.Jmol.getPropertyAsArray(w.jmolAppletNomeclature,"orientationInfo"),error:w.Jmol.evaluateVar(w.jmolAppletNomeclature,"_errormessage"),resources:w.performance.getEntriesByType("resource").filter(r=>r.name.includes("init-55.spt")).map(r=>r.name),ready:w.NameleculeNameBuilderHost.modelReady()}})()');out['threeD']=diag
 click('#zoom-in');time.sleep(.3);click('#zoom-out');time.sleep(.3)
 check(answer()==partial and ev('document.querySelector("iframe").contentWindow.NameleculeNameBuilderHost.modelReady()'),'Native 3D zoom pair preserves answer and requested model')
 check(not diag['error'] and any('?v=096f339' in u for u in diag['resources']),'Corrected fingerprinted init executes with no JSmol parse error',diag)
 # Actual ester tiles/space boundary through the learner UI.
 open_page('games/name-builder.html?molecule=isopropyl_ethanoate');wait('document.querySelectorAll("#bank-tiles button").length>0')
 raw=read('__builderEvents.findLast(x=>x.type==="round")');out['esterRound']=raw
 for piece in raw['pieces']:
  sel=read('(()=>{let b=[...document.querySelectorAll("#bank-tiles button")].find(b=>b.textContent==='+json.dumps(piece['text'])+');return "#bank-tiles button[data-tile-id=\\\""+b.dataset.tileId+"\\\"]"})()');click(sel)
 check(ev('document.querySelector("#candidate-name").textContent')==raw['correctName'],'Ester actual UI composes engine target including word boundary')
 click('#check-answer');check(ev('document.querySelector("#feedback").classList.contains("success")'),'Ester UI full name accepted')
 shot('supplement-ester-success.png')
 # Browser history restoration is a real navigation, not a simulated lifecycle event.
 ev('window.__pageshow=[];addEventListener("pageshow",e=>__pageshow.push(e.persisted));true')
 click('.back-link');wait('location.pathname.endsWith("welcome-proposal.html")')
 call('browsingContext.traverseHistory',{'context':ctx,'delta':-1});wait('location.pathname.endsWith("name-builder.html")')
 wait('document.querySelectorAll("#bank-tiles button").length>0 && document.querySelector("#viewer-mask").hidden',45)
 history=read('({persisted:window.__pageshow,frame:document.querySelector("iframe").getAttribute("src"),status:document.querySelector("#game-status").textContent,bank:document.querySelectorAll("#bank-tiles button").length})');out['history']=history
 check(history['frame']!='about:blank' and history['bank']>0,'History Back returns to a working viewer',history)
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('supplement-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'supplement.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
if not out['completed']:raise SystemExit(1)
