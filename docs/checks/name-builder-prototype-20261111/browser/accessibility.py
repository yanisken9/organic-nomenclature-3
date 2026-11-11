from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'checks':[],'completed':False,'scope':'2D pointer/emulated touch/keyboard/resize; no3D, physical-device or reduced-motion runtime claim'}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def state():return read('({answer:[...document.querySelectorAll("#answer-tiles button")].map(b=>b.textContent),candidate:document.querySelector("#candidate-name").textContent,feedback:document.querySelector("#feedback").hidden,bodyWidth:document.documentElement.scrollWidth,viewport:innerWidth})')
def point(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});true');time.sleep(.1)
 return read('(()=>{let r=document.querySelector('+json.dumps(selector)+').getBoundingClientRect();return{x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}})()')
try:
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 open_page('games/name-builder.html?molecule=methane');wait('document.querySelectorAll("#bank-tiles button").length>0')
 check(ev('document.querySelector("[data-representation=skeletal]").disabled'),'Methane unavailable skeletal option disabled')
 check(state()['bodyWidth']<=390,'390px no overflow')
 p=point('#bank-tiles li:first-child button')
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'touch-tap','parameters':{'pointerType':'touch'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y']},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
 wait('document.querySelectorAll("#answer-tiles button").length===1',5)
 check(len(state()['answer'])==1,'Trusted touch tap adds a tile')
 click('#remove-tile');check(state()['answer']==[],'Selected tile removal returns it to bank')
 # Same Pointer Events pathway with a real touch pointer drag.
 ev('document.querySelector("#answer-zone").scrollIntoView({block:"start",behavior:"instant"});scrollBy(0,-40);true');time.sleep(.1)
 points=read('(()=>{let b=document.querySelector("#bank-tiles li:first-child button").getBoundingClientRect(),z=document.querySelector("#answer-zone").getBoundingClientRect();return{sx:Math.round(b.x+b.width/2),sy:Math.round(b.y+b.height/2),tx:Math.round(z.x+z.width/2),ty:Math.round(z.y+z.height/2),height:innerHeight}})()')
 assert 0<points['sy']<points['height'],points
 actions=[{'type':'pointerMove','x':points['sx'],'y':points['sy']},{'type':'pointerDown','button':0}]
 actions += [{'type':'pointerMove','x':round(points['sx']+(points['tx']-points['sx'])*i/8),'y':round(points['sy']+(points['ty']-points['sy'])*i/8),'duration':70}for i in range(1,9)]
 actions += [{'type':'pointerUp','button':0}]
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'touch-drag','parameters':{'pointerType':'touch'},'actions':actions}]})
 wait('document.querySelectorAll("#answer-tiles button").length===1',5)
 check(len(state()['answer'])==1,'Trusted touch drag adds a tile',points)
 before=state();time.sleep(.7)
 # Keyboard removal and addition use actual key input, not simulated click.
 ev('document.querySelector("#answer-tiles button").focus();true')
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'accessible-keyboard','actions':[{'type':'keyDown','value':'\ue017'},{'type':'keyUp','value':'\ue017'}]}]})
 check(state()['answer']==[],'Native Delete removes answer tile')
 ev('document.querySelector("#bank-tiles button").focus();true')
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'accessible-keyboard','actions':[{'type':'keyDown','value':'\ue007'},{'type':'keyUp','value':'\ue007'}]}]})
 check(len(state()['answer'])==1,'Native Enter adds bank tile')
 before=state()['answer']
 for width,height in [(320,700),(1280,900),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.2)
  current=state();check(current['answer']==before and current['bodyWidth']<=width,'Resize preserves answer and no overflow '+str(width))
 ev('scrollTo({top:document.querySelector("#answer-title").getBoundingClientRect().top+scrollY-20,behavior:"instant"});true');shot('accessibility-mobile-answer.png')
 check(not ev('!!document.querySelector(".touch-ghost")'),'Drag ghost cleaned after interaction')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('accessibility-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'accessibility.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
if not out['completed']:raise SystemExit(1)
