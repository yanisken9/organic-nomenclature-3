from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'completed':False,'checks':[],'geometry':[],'role':'Developer actual isolated Firefox compaction checks'}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def fill(skip=None):ev('(()=>{for(let p of __builderEvents.findLast(e=>e.type==="round").pieces){if(p.text==='+json.dumps(skip)+')continue;[...document.querySelectorAll("#bank-tiles button")].find(b=>b.textContent===p.text).click()}return true})()')
def geometry():return read('(()=>{let z=document.querySelector("#answer-zone"),a=z.getBoundingClientRect(),b=[...z.querySelectorAll("button")],c=document.querySelector("#candidate-name"),r=document.createRange();r.selectNodeContents(c);return{viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,clientWidth:z.clientWidth,scrollWidth:z.scrollWidth,first:b[0].getBoundingClientRect().left,last:b.at(-1).getBoundingClientRect().right,left:a.left+z.clientLeft,right:a.left+z.clientLeft+z.clientWidth,font:getComputedStyle(b[0]).fontSize,minHeight:Math.min(...b.map(x=>x.getBoundingClientRect().height)),rows:[...new Set(b.map(x=>Math.round(x.getBoundingClientRect().top)))].length,candidate:c.textContent,nameLines:[...new Set([...r.getClientRects()].map(x=>Math.round(x.top)))].length}})()')
def full_visible(g):return g['first']>=g['left']+3 and g['last']<=g['right']-3
try:
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1024,'height':900},'devicePixelRatio':1});open_page('games/name-builder.html?v=compact-r1&molecule=dimethyl_4_5_hexen_5_yn_1_one_3');wait('document.querySelectorAll("#bank-tiles button").length>0',60);fill('-3-')
 g=geometry();out['geometry'].append({'kind':'screenshot8','data':g});check(full_visible(g) and g['rows']==1,'All8 screenshot pieces simultaneously visible at1024',g)
 check(g['pageWidth']<=1024 and abs(float(g['font'][:-2])-16.4833)<.01 and g['minHeight']==46,'Font and height retained; no page overflow')
 ev('document.querySelector(".answer-panel").scrollIntoView({block:"center",behavior:"instant"});true');shot('after-screenshot-1024.png')
 # Add the remaining correct piece and move it before the suffix using native keys.
 selector=read('(()=>{let b=[...document.querySelectorAll("#bank-tiles button")].find(b=>b.textContent==="-3-");return "#bank-tiles button[data-tile-id=\\\""+b.dataset.tileId+"\\\"]"})()');click(selector)
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'compact-keyboard','actions':[{'type':'keyDown','value':'\ue012'},{'type':'keyUp','value':'\ue012'}]}]})
 g=geometry();out['geometry'].append({'kind':'full9','data':g});check(full_visible(g) and g['rows']==1,'All9 full-name pieces simultaneously visible at1024',g)
 check(g['candidate']==read('__builderEvents.findLast(e=>e.type==="round").correctName'),'Keyboard reorder composes exact engine target')
 shot('after-full-1024.png');click('#check-answer');check(ev('document.querySelector("#feedback").classList.contains("success")'),'Correct full name succeeds')
 # Larger names still have an explicitly accepted local scroll fallback.
 open_page('games/name-builder.html?v=compact-r1&molecule=ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid');wait('document.querySelectorAll("#bank-tiles button").length>0',60);fill()
 for width,height in [(1280,900),(390,844),(320,700)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.15);g=geometry();out['geometry'].append({'kind':'long12','data':g})
  check(g['rows']==1 and g['nameLines']==1 and g['pageWidth']<=width,'Long name remains one row/line without page overflow '+str(width),g)
  ends=read('(()=>{let z=document.querySelector("#answer-zone"),a=z.getBoundingClientRect();z.scrollLeft=0;let first=z.querySelector("button").getBoundingClientRect().left;z.scrollLeft=z.scrollWidth;let last=[...z.querySelectorAll("button")].at(-1).getBoundingClientRect().right;return{first:first>=a.left,last:last<=a.right}})()');check(ends['first'] and ends['last'],'Long name both ends reachable '+str(width))
 ev('document.querySelector("#answer-tiles li:last-child button").focus({preventScroll:true});true')
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'compact-keyboard','actions':[{'type':'keyDown','value':'\ue012'},{'type':'keyUp','value':'\ue012'},{'type':'keyDown','value':'\ue014'},{'type':'keyUp','value':'\ue014'}]}]})
 check(ev('(()=>{let z=document.querySelector("#answer-zone").getBoundingClientRect(),b=document.querySelector("#answer-tiles .selected").getBoundingClientRect();return b.left>=z.left&&b.right<=z.right})()'),'Selected compact tile revealed after native key moves')
 click('#check-answer');check(ev('document.querySelector("#feedback").classList.contains("success")'),'Long-name answer and scoring unchanged')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('compact-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'compact.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
if not out['completed']:raise SystemExit(1)
