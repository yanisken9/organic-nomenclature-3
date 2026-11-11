from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'completed':False,'checks':[],'layouts':[],'role':'Developer actual isolated Firefox logo integration checks'}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def snapshot():return read('(()=>{let im=document.querySelector(".builder-logo"),h=document.querySelector("#game-title"),wrap=document.querySelector(".builder-title"),rect=n=>{let r=n.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};return{width:innerWidth,pageWidth:document.documentElement.scrollWidth,loaded:im.complete&&im.naturalWidth===1254&&im.naturalHeight===1254,logo:rect(im),heading:rect(h),wrapper:rect(wrap),title:h.textContent,h1Count:document.querySelectorAll("h1").length,decorative:im.alt===""&&im.getAttribute("aria-hidden")==="true",imageFit:getComputedStyle(im).objectFit,sectionLabel:document.querySelector(".intro").getAttribute("aria-labelledby"),viewportReserved:im.hasAttribute("width")&&im.hasAttribute("height")}})()')
try:
 open_page('games/name-builder.html?v=logo-20261111-r1&molecule=dimethyl_4_5_hexen_5_yn_1_one_3')
 wait('document.querySelectorAll("#bank-tiles button").length>0 && document.querySelector(".builder-logo").complete',60)
 for width,height in [(1500,1000),(1024,900),(550,900),(390,844),(320,740)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.1)
  g=snapshot();out['layouts'].append(g)
  check(g['loaded'] and g['imageFit']=='contain' and g['logo']['width']==g['logo']['height'],'Complete square logo rendered '+str(width),g)
  check(g['pageWidth']<=width and g['logo']['x']>=0 and g['heading']['right']<=width and g['logo']['right']<=g['heading']['x'],'Heading and logo fit without horizontal page overflow '+str(width))
  check(g['title']=='Χτίσε το όνομα' and g['h1Count']==1 and g['decorative'] and g['sectionLabel']=='game-title' and g['viewportReserved'],'Heading semantics and decorative stable-size image '+str(width))
  ev('scrollTo(0,0);true');shot('header-'+str(width)+'.png')
 # The taller header must not change what a real bank click adds.
 for width,height in [(1024,900),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  if width==390:
   open_page('games/name-builder.html?v=logo-20261111-r1&molecule=dimethyl_4_5_hexen_5_yn_1_one_3');wait('document.querySelectorAll("#bank-tiles button").length>0',60)
  pieces=read('__builderEvents.findLast(e=>e.type==="round").pieces')
  for i,piece in enumerate(pieces):
   tile=read('(()=>{let b=[...document.querySelectorAll("#bank-tiles button")].find(b=>b.textContent==='+json.dumps(piece['text'])+');return{id:b.dataset.tileId,text:b.textContent}})()')
   click('#bank-tiles button[data-tile-id="'+tile['id']+'"]')
   added=read('[...document.querySelectorAll("#answer-tiles button")].at(-1).textContent')
   check(added==tile['text'],'Trusted click preserves chosen component '+str(width)+' '+str(i))
  target=read('__builderEvents.findLast(e=>e.type==="round").correctName')
  check(read('document.querySelector("#candidate-name").textContent')==target,'Full composed candidate remains exact '+str(width))
  click('#check-answer');check(ev('document.querySelector("#feedback").classList.contains("success")'),'Correct full-name answer succeeds '+str(width))
  shot('success-'+str(width)+'.png')
 # Decoration remains separate from game readiness even if image fails.
 ev('document.querySelector(".builder-logo").src="data:image/png;base64,invalid";true');time.sleep(.1)
 check(ev('document.querySelector("#game-title").textContent==="Χτίσε το όνομα" && !document.querySelector("#next-molecule").disabled'),'Readable title and next action survive missing logo')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'capturedJSExceptions':len(js_errors)},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
