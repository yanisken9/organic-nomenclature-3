from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'checks':[],'completed':False}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def save():
 out['javascriptErrors']=js_errors
 (HERE/'interactions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
def choose_text(text,container='bank-tiles'):
 selector=read('(()=>{let b=[...document.querySelectorAll('+json.dumps('#'+container+' button')+')].find(x=>x.textContent==='+json.dumps(text)+');return b?"#'+container+' button[data-tile-id=\\\""+b.dataset.tileId+"\\\"]":null})()')
 assert selector,text
 click(selector)
def answer():return read('[...document.querySelectorAll("#answer-tiles button")].map(b=>b.textContent)')
try:
 open_page('games/name-builder.html?molecule=ethane')
 wait('document.querySelectorAll("#bank-tiles button").length>0')
 raw=read('__builderEvents.findLast(x=>x.type==="round")');out['round']=raw
 check(raw['correctName']=='αιθάνιο','Initial real engine target ethane')
 geometry=read('(()=>{let f=document.querySelector("iframe"),w=f.contentWindow,d=f.contentDocument;return{frame:f.getBoundingClientRect().toJSON(),child:["#viewerCol","#jsmeNomeclatureDIV","#jsmeNomeclatureSVG","#jsmeNomeclatureSVG svg"].map(s=>({selector:s,rect:d.querySelector(s)?.getBoundingClientRect().toJSON()})),host:w.NameleculeNameBuilderHost.snapshot(),bodyText:d.body.innerText}})()')
 out['initialGeometry']=geometry;check('αιθάνιο' not in geometry['bodyText'],'Target name hidden in learner viewer',geometry)
 # Native mouse drag from bank to central frame, with both endpoints visible.
 ev('scrollTo({top:350,behavior:"instant"});true');time.sleep(.2)
 points=read('(()=>{let b=[...document.querySelectorAll("#bank-tiles button")].find(x=>x.textContent==="αιθ").getBoundingClientRect(),z=document.querySelector("#answer-zone").getBoundingClientRect();return{sx:Math.round(b.x+b.width/2),sy:Math.round(b.y+b.height/2),tx:Math.round(z.x+z.width/2),ty:Math.round(z.y+z.height/2)}})()')
 out['dragPoints']=points
 ev('window.__dragEvents=[];["pointerdown","mousedown","dragstart","dragover","drop","dragend","click"].forEach(t=>document.addEventListener(t,e=>__dragEvents.push({type:t,target:e.target.id||e.target.className,text:e.target.textContent?.slice(0,40),x:e.clientX,y:e.clientY,types:e.dataTransfer?[...e.dataTransfer.types]:null}),true));true')
 steps=[{'type':'pointerMove','x':points['sx'],'y':points['sy'],'duration':0},{'type':'pointerDown','button':0}]
 steps += [{'type':'pointerMove','x':round(points['sx']+(points['tx']-points['sx'])*i/10),'y':round(points['sy']+(points['ty']-points['sy'])*i/10),'duration':80} for i in range(1,11)]
 steps += [{'type':'pointerUp','button':0}]
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'builder-drag','parameters':{'pointerType':'mouse'},'actions':steps}]})
 out['dragEvents']=read('__dragEvents')
 wait('document.querySelectorAll("#answer-tiles button").length===1',5)
 check(answer()==['αιθ'],'Trusted mouse drag adds correct tile',points)
 bank_before=read('[...document.querySelectorAll("#bank-tiles button")].map(b=>b.dataset.tileId)')
 click('[data-representation="expanded"]');wait('document.querySelector("[data-representation=expanded]").getAttribute("aria-pressed")==="true" && !document.querySelector("#check-answer").disabled')
 check(answer()==['αιθ'] and bank_before==read('[...document.querySelectorAll("#bank-tiles button")].map(b=>b.dataset.tileId)'),'Expanded switch preserves exact answer and bank')
 if not os.environ.get('NAME_BUILDER_SKIP_3D'):
  click('[data-representation="3d"]');wait('document.querySelector("[data-representation=\\"3d\\"]").getAttribute("aria-pressed")==="true" && !document.querySelector("#check-answer").disabled',35)
  check(ev('document.querySelector("iframe").contentWindow.NameleculeNameBuilderHost.modelReady()'),'Actual requested3D graph ready')
  check(answer()==['αιθ'],'3D switch preserves partial answer')
  ev('scrollTo({top:200,behavior:"instant"});true');shot('interaction-3d.png')
 else:out['3DSkipped']=True
 click('[data-representation="skeletal"]');wait('document.querySelector("[data-representation=skeletal]").getAttribute("aria-pressed")==="true" && !document.querySelector("#check-answer").disabled')
 check(answer()==['αιθ'],'Skeletal switch preserves partial answer')
 click('#check-answer');check(not ev('document.querySelector("#feedback").classList.contains("success")'),'Missing tile attempt rejected')
 choose_text('ιο');choose_text('άν');check(answer()==['αιθ','ιο','άν'],'Wrong order assembled by native clicks')
 click('#check-answer');check(not ev('document.querySelector("#feedback").classList.contains("success")'),'Wrong order rejected')
 ev('document.querySelector("#answer-tiles li:last-child button").focus();true')
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'builder-keys','actions':[{'type':'keyDown','value':'\ue012'},{'type':'keyUp','value':'\ue012'}]}]})
 check(answer()==['αιθ','άν','ιο'],'Native ArrowLeft reorders selected tile')
 click('#check-answer');check(ev('document.querySelector("#feedback").classList.contains("success")'),'Correct order receives success')
 check(ev('document.querySelector("#candidate-name").textContent')=='αιθάνιο','Candidate exactly matches engine full target')
 click('[data-representation="condensed"]');wait('document.querySelector("[data-representation=condensed]").getAttribute("aria-pressed")==="true" && !document.querySelector("#next-molecule").disabled')
 check(ev('document.querySelector("#feedback").classList.contains("success") && document.querySelector("#check-answer").disabled') and answer()==['αιθ','άν','ιο'],'Solved answer and feedback survive representation switch')
 ev('scrollTo({top:200,behavior:"instant"});true');shot('interaction-success.png')
 click('#next-molecule');wait('document.querySelectorAll("#bank-tiles button").length>0 && !document.querySelector("#next-molecule").disabled')
 check(answer()==[] and ev('document.querySelector("#feedback").hidden'),'Next molecule starts a fresh attempt')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});time.sleep(.4)
 check(ev('document.documentElement.scrollWidth<=innerWidth'),'390px has no horizontal overflow')
 ev('scrollTo({top:0,behavior:"instant"});true');shot('interaction-mobile.png')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['failureState']=read('({status:document.querySelector("#game-status")?.textContent,events:__builderEvents.slice(-5),host:document.querySelector("iframe")?.contentWindow.NameleculeNameBuilderHost?.snapshot()})');shot('interaction-failure.png')
 except Exception:pass
finally:
 save();finish()
if not out['completed']:raise SystemExit(1)
