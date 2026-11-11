from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
LONG='ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid'
out={'completed':False,'checks':[],'geometry':[],'role':'Developer actual isolated Firefox evidence'}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def raw():return read('__builderEvents.findLast(e=>e.type==="round")')
def fill():
 ev('(()=>{for(let p of __builderEvents.findLast(e=>e.type==="round").pieces){let b=[...document.querySelectorAll("#bank-tiles button")].find(b=>b.textContent===p.text);if(!b)throw Error("missing tile");b.click()}return true})()')
def geometry():return read('''(()=>{let zone=document.querySelector('#answer-zone'),row=document.querySelector('#answer-tiles'),candidate=document.querySelector('#candidate-name'),success=document.querySelector('#feedback strong');function lines(el){if(!el)return null;let r=document.createRange();r.selectNodeContents(el);return [...new Set([...r.getClientRects()].map(x=>Math.round(x.top)))].length}return{viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,tileRows:[...new Set([...row.querySelectorAll('button')].map(b=>Math.round(b.getBoundingClientRect().top)))].length,candidateLines:lines(candidate),successLines:lines(success),candidate:candidate.textContent,success:success?.textContent,zone:{width:zone.clientWidth,scrollWidth:zone.scrollWidth,left:zone.scrollLeft},font:getComputedStyle(row.querySelector('button')).fontSize,minHeight:Math.min(...[...row.querySelectorAll('button')].map(b=>b.getBoundingClientRect().height)),molecule:document.querySelector('.molecule-panel').getBoundingClientRect().toJSON(),answer:document.querySelector('.answer-panel').getBoundingClientRect().toJSON()}})()''')
def key(value,count=1):
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'single-line-keyboard','actions':sum(([{'type':'keyDown','value':value},{'type':'keyUp','value':value}]for _ in range(count)),[])}]})
def ids():return read('[...document.querySelectorAll("#answer-tiles button")].map(b=>b.dataset.tileId)')
def selected_visible():return ev('(()=>{let z=document.querySelector("#answer-zone"),b=document.querySelector("#answer-tiles .selected");if(!b)return false;let a=z.getBoundingClientRect(),r=b.getBoundingClientRect();return r.left>=a.left+z.clientLeft-1&&r.right<=a.left+z.clientLeft+z.clientWidth+1})()')
try:
 open_page('games/name-builder.html?molecule='+LONG);wait('document.querySelectorAll("#bank-tiles button").length>0');r=raw();out['round']=r;fill();original=ids()
 for width,height in [(1280,900),(390,844),(320,700)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.2);g=geometry();out['geometry'].append(g)
  check(g['tileRows']==1 and g['candidateLines']==1,'Longest name remains one row/line '+str(width),g)
  check(g['pageWidth']<=width and float(g['font'][:-2])>=16 and g['minHeight']>=44,'Readable tiles and no page overflow '+str(width))
  check(g['candidate']==r['correctName'],'Exact engine name retained '+str(width))
  if width==1280:check(g['molecule']['top']==g['answer']['top'] and g['molecule']['right']<g['answer']['left'],'Original desktop columns retained')
  edges=read('(()=>{let z=document.querySelector("#answer-zone");z.scrollLeft=0;let a=z.getBoundingClientRect(),first=z.querySelector("button").getBoundingClientRect();z.scrollLeft=z.scrollWidth;let last=[...z.querySelectorAll("button")].at(-1).getBoundingClientRect();return{firstReachable:first.left>=a.left,lastReachable:last.right<=a.right,scroll:z.scrollLeft}})()')
  check(edges['firstReachable'] and edges['lastReachable'],'Both ends reachable by local scrolling '+str(width),edges)
  ev('document.querySelector(".answer-panel").scrollIntoView({block:"center",behavior:"instant"});true');shot('after-'+str(width)+'.png')
 # Native key reorders reveal the selected tile without moving the page vertically.
 ev('document.querySelector("#answer-tiles li:last-child button").focus({preventScroll:true});true');page_y=ev('scrollY')
 for _ in range(len(original)-1):key('\ue012');check(selected_visible(),'Keyboard move reveals selected tile horizontally')
 check(abs(ev('scrollY')-page_y)<1,'Keyboard reveal preserves vertical page position')
 for _ in range(len(original)-1):key('\ue014')
 check(ids()==original and selected_visible(),'Keyboard reordering restores exact original answer')
 # Named regions accept native horizontal keyboard scrolling.
 for selector in ['#answer-zone','#candidate-name']:
  ev('(()=>{let n=document.querySelector('+json.dumps(selector)+');n.scrollLeft=0;n.focus({preventScroll:true});return true})()');key('\ue014',5);time.sleep(.2)
  check(ev('document.querySelector('+json.dumps(selector)+').scrollLeft>0'),selector+' is keyboard-scrollable')
 click('#check-answer');check(ev('document.querySelector("#feedback").classList.contains("success")'),'Longest exact name accepted')
 g=geometry();out['geometry'].append(g);check(g['successLines']==1 and g['success']==r['correctName'],'Success name stays exact and on one line')
 ev('document.querySelector("#feedback strong").focus({preventScroll:true});true');key('\ue014',5);time.sleep(.2);check(ev('document.querySelector("#feedback strong").scrollLeft>0'),'Success name is keyboard-scrollable')
 for form in ['expanded','3d','condensed']:
  click('[data-representation="'+form+'"]');wait('document.querySelector("[data-representation=\\"'+form+'\\"]").getAttribute("aria-pressed")==="true"&&!document.querySelector("#next-molecule").disabled',35)
  check(ids()==original and ev('document.querySelector("#feedback").classList.contains("success")'),'Solved answer preserved on '+form)
  if form=='3d':check(ev('document.querySelector("iframe").contentWindow.NameleculeNameBuilderHost.modelReady()'),'Same requested3D graph ready')
 click('#next-molecule');wait('document.querySelectorAll("#bank-tiles button").length>0&&!document.querySelector("#next-molecule").disabled')
 check(ids()==[] and ev('document.querySelector("#answer-zone").scrollLeft===0&&document.querySelector("#feedback").hidden'),'New round resets local scroll and answer')
 for mid in ['ethane','isopropyl_ethanoate']:
  open_page('games/name-builder.html?molecule='+mid);wait('document.querySelectorAll("#bank-tiles button").length>0');r=raw();fill();g=geometry();check(g['tileRows']==1 and g['candidateLines']==1 and g['candidate']==r['correctName'],'Short/ester name one line and exact '+mid)
  click('#check-answer');check(ev('document.querySelector("#feedback").classList.contains("success")'),'Correct short/ester answer accepted '+mid)
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('layout-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'layout.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
if not out['completed']:raise SystemExit(1)
