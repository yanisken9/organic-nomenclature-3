from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'completed':False,'checks':[],'moves':[],'role':'Developer actual trusted-pointer evidence'}
LONG='ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid'
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def answer():return read('[...document.querySelectorAll("#answer-tiles button")].map(b=>b.dataset.tileId)')
def fill():ev('(()=>{for(let p of __builderEvents.findLast(e=>e.type==="round").pieces)[...document.querySelectorAll("#bank-tiles button")].find(b=>b.textContent===p.text).click();return true})()')
def prepare(index):
 return read('''(()=>{let z=document.querySelector('#answer-zone'),b=document.querySelector('#bank-tiles button');z.scrollIntoView({block:'start',behavior:'instant'});scrollBy(0,-90);let buttons=[...z.querySelectorAll('button')];if(INDEX===0)z.scrollLeft=0;else if(INDEX===buttons.length)z.scrollLeft=z.scrollWidth;else {let r=buttons[INDEX].getBoundingClientRect(),a=z.getBoundingClientRect();z.scrollLeft+=(r.left+r.width/2)-(a.left+a.width/2)}let a=z.getBoundingClientRect(),s=b.getBoundingClientRect(),r=buttons[INDEX]?.getBoundingClientRect();return{sx:Math.round(s.left+s.width/2),sy:Math.round(s.top+s.height/2),tx:Math.round(INDEX===0?a.left+8:INDEX===buttons.length?a.right-8:r.left+r.width/4),ty:Math.round(a.top+8),tile:b.dataset.tileId,scroll:z.scrollLeft,viewport:innerHeight,zone:a.toJSON()}})()'''.replace('INDEX',str(index)))
def actions_to(p,kind='mouse',release=True):
 assert 0<p['sx']<ev('innerWidth') and 0<p['sy']<ev('innerHeight') and 0<p['ty']<ev('innerHeight'),p
 steps=[{'type':'pointerMove','x':p['sx'],'y':p['sy']},{'type':'pointerDown','button':0}]
 steps +=[{'type':'pointerMove','x':round(p['sx']+(p['tx']-p['sx'])*i/8),'y':round(p['sy']+(p['ty']-p['sy'])*i/8),'duration':60}for i in range(1,9)]
 if release:steps.append({'type':'pointerUp','button':0})
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'single-line-drag-'+kind,'parameters':{'pointerType':kind},'actions':steps}]})
try:
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':900},'devicePixelRatio':1});open_page('games/name-builder.html?molecule='+LONG);wait('document.querySelectorAll("#bank-tiles button").length>0');fill();original=answer();out['original']=original
 for index in [0,6,len(original)]:
  p=prepare(index);actions_to(p);wait('document.querySelectorAll("#answer-tiles button").length===13',5)
  expected=original[:index]+[p['tile']]+original[index:];out['moves'].append({'index':index,'points':p,'actual':answer()})
  check(answer()==expected,'Mouse drop into upper padding inserts at intended '+str(index),p)
  click('#remove-tile');check(answer()==original,'Removal restores exact answer '+str(index))
 # A stationary held pointer at the right edge must continue scrolling.
 p=prepare(0);p['tx']=round(p['zone']['right']-12);p['ty']=round(p['zone']['top']+p['zone']['height']/2)
 ev('document.addEventListener("pointerdown",e=>{window.__lastPointerId=e.pointerId},{once:true});window.__lostTrusted=false;document.addEventListener("lostpointercapture",e=>{window.__lostTrusted=e.isTrusted},{once:true,capture:true});true')
 actions_to(p,release=False);start=ev('document.querySelector("#answer-zone").scrollLeft');time.sleep(.45);end=ev('document.querySelector("#answer-zone").scrollLeft')
 check(end>start+50,'Stationary edge drag continues horizontal scrolling',{'start':start,'end':end})
 check(answer()==original and ev('!!document.querySelector(".touch-ghost")'),'Held drag does not prematurely add a tile')
 ev('document.querySelector(".tile-button.dragging").releasePointerCapture(window.__lastPointerId);true')
 outside={'type':'pointerMove','x':round(p['zone']['left']+50),'y':round(p['zone']['top']-25),'duration':40}
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'single-line-drag-mouse','parameters':{'pointerType':'mouse'},'actions':[outside,{'type':'pointerUp','button':0}]}]})
 wait('!document.querySelector(".touch-ghost")',5);stopped=ev('document.querySelector("#answer-zone").scrollLeft');time.sleep(.25)
 check(ev('window.__lostTrusted') and ev('document.querySelector("#answer-zone").scrollLeft')==stopped and answer()==original,'Lost capture cancels scrolling/ghost without changing answer')
 # Native touch-pointer insertion on a narrow screen uses the same scroll-aware row.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});time.sleep(.2)
 p=prepare(6);actions_to(p,'touch');wait('document.querySelectorAll("#answer-tiles button").length===13',5)
 check(answer()==original[:6]+[p['tile']]+original[6:],'Trusted touch inserts in scrolled narrow row',p)
 click('#remove-tile');check(answer()==original and not ev('!!document.querySelector(".touch-ghost")'),'Touch removal and drag cleanup preserve answer')
 shot('drag-narrow-complete.png');out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('drag-failure.png')
 except Exception:pass
finally:
 try:call('input.releaseActions',{'context':ctx})
 except Exception:pass
 out['javascriptErrors']=js_errors;(HERE/'drag.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
if not out['completed']:raise SystemExit(1)
