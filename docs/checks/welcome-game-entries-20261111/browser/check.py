from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'completed':False,'checks':[],'layouts':[],'role':'Developer actual isolated Firefox welcome game-entry checks'}
WELCOME='design/welcome-proposal.html?v=games-entries-20261111-r1'
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def home():open_page(WELCOME);wait('document.querySelectorAll(".card.two .game-action").length===2 && [...document.querySelectorAll(".card.two .game-action img")].every(i=>i.complete&&i.naturalWidth>0)',30)
def key(value):call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'welcome-keyboard','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]})
try:
 home()
 for width,height in [(1500,1100),(1024,1000),(390,900),(320,800)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.1)
  g=read('(()=>{let card=document.querySelector(".card.two").getBoundingClientRect();return{width:innerWidth,pageWidth:document.documentElement.scrollWidth,card:{left:card.left,right:card.right},games:[...document.querySelectorAll(".game-action")].map(a=>{let r=a.getBoundingClientRect(),im=a.querySelector("img"),ir=im.getBoundingClientRect(),label=a.querySelector(".game-action-label"),lr=label.getBoundingClientRect(),arrow=a.querySelector(".game-action-arrow").getBoundingClientRect();return{text:label.textContent,href:a.getAttribute("href"),left:r.left,right:r.right,height:r.height,imageLoaded:im.complete&&im.naturalWidth>0,square:ir.width===ir.height,decorative:im.alt===""&&im.getAttribute("aria-hidden")==="true",labelFits:lr.left>=ir.right&&lr.right<=arrow.left,insideCard:r.left>=card.left&&r.right<=card.right,focusStyle:getComputedStyle(a).outlineStyle}})}})()')
  out['layouts'].append(g)
  check(all(x['imageLoaded'] and x['square'] and x['decorative'] for x in g['games']),'Both existing logos loaded, square and decorative '+str(width),g)
  check(all(x['insideCard'] and x['labelFits'] and x['height']>=44 for x in g['games']),'Game labels and hit areas fit the second card '+str(width))
  check(g['pageWidth']<=width,'No horizontal page overflow '+str(width),g['pageWidth'])
  ev('document.querySelector(".card.two").scrollIntoView({block:"center",behavior:"instant"});true');shot('welcome-'+str(width)+'.png')
 # Native keyboard navigation preserves distinct names and opens the Builder.
 ev('document.querySelector(".card.two .game-action").focus();true');key('\ue004')
 check(ev('document.activeElement===document.querySelectorAll(".card.two .game-action")[1]'),'Tab reaches Builder after Workshop')
 check(ev('getComputedStyle(document.activeElement).outlineStyle!=="none"'),'Keyboard focus visibly indicated')
 key('\ue007');wait('location.pathname.endsWith("/games/name-builder.html") && document.querySelectorAll("#bank-tiles button").length>0',60)
 check(ev('document.querySelector("#game-title").textContent==="Χτίσε το όνομα"'),'Builder opens from welcome with Enter')
 check(ev('__builderEvents.findLast(e=>e.type==="round").moleculeId==="ethane"'),'Welcome starts normal default ethane round')
 tile=read('(()=>{let b=document.querySelector("#bank-tiles button");return{id:b.dataset.tileId,text:b.textContent}})()');click('#bank-tiles button[data-tile-id="'+tile['id']+'"]')
 check(read('document.querySelector("#answer-tiles button").textContent')==tile['text'],'Builder bank selection works after welcome entry')
 click('.back-link');wait('location.pathname.endsWith("/design/welcome-proposal.html") && document.querySelectorAll(".game-action").length===2',30)
 check(True,'Builder return link restores two-game welcome')
 # Both links also operate through normal pointer clicks at desktop and narrow widths.
 for width,height in [(1500,1100),(390,900)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});home()
  click('.card.two a[href*="name-repair.html"]');wait('location.pathname.endsWith("/games/name-repair.html") && !!document.querySelector("#set-alkanes-start")',45)
  check(ev('document.querySelector(".workshop-title h1").textContent==="Συνεργείοονομάτων"'),'Workshop opens from actual welcome click '+str(width))
  click('.exit-link');wait('location.pathname.endsWith("/design/welcome-proposal.html") && document.querySelectorAll(".game-action").length===2',30);check(True,'Workshop return restores both entries '+str(width))
  click('.card.two a[href*="name-builder.html"]');wait('location.pathname.endsWith("/games/name-builder.html") && document.querySelectorAll("#bank-tiles button").length>0',60);check(True,'Builder opens from actual welcome click '+str(width))
  click('.back-link');wait('location.pathname.endsWith("/design/welcome-proposal.html") && document.querySelectorAll(".game-action").length===2',30);check(True,'Builder return restores both entries '+str(width))
 # Neighboring entry interactions are unchanged by card-only styles.
 check(ev('document.querySelector(".card.one a.action").getAttribute("href")==="theory-library.html?v=other-ketones-theory-20261026"'),'Theory entry URL preserved')
 click('.card.three button');wait('document.querySelector("#details").open',5);check(ev('document.querySelector("#dialog-title").textContent==="Χώρος εκπαιδευτικού"'),'Teacher dialog remains functional');key('\ue00c');wait('!document.querySelector("#details").open',5)
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'capturedJSExceptions':len(js_errors)},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
