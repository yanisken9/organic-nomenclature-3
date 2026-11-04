from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/v54-sync-20261104/test-features.py').read_text().split('\ntry:\n',1)[0],'support','exec'))
out={'completed':False,'checks':[]}
def click(selector):
 for attempt in range(10):
  ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});new Promise(r=>setTimeout(r,100))')
  p=json.loads(ev('JSON.stringify((()=>{let n=document.querySelector('+json.dumps(selector)+'),b=n.getBoundingClientRect(),hit=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return{x:b.x+b.width/2,y:b.y+b.height/2,hit:n.contains(hit),pointer:getComputedStyle(n).pointerEvents,at:hit&&hit.outerHTML.slice(0,200)}})())'))
  if p['hit']:break
 assert p['hit'],(selector,p)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':round(p['x']),'y':round(p['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})

def check(value,label,detail=None):
 assert value,(label,detail)
 out['checks'].append({'label':label,'detail':detail})
try:
 navigate('mulermoc-nom-54.html?lang=gr&v=final-interactions-'+str(time.time_ns()));app_ready();until('window.JSmolReadyFlag===true');until('!!document.querySelector("#ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid.menuLi")')
 key='ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid'
 # Select the longest acid by data key, as an actual row click.
 keys=json.loads(ev('JSON.stringify(Object.keys(nameExamples).filter(k=>k.includes("isopropyl")&&k.includes("hexanoic")))'))
 assert len(keys)==1,keys
 key=keys[0];click('[id="'+key+'"].menuLi');until('selectedMol==='+json.dumps(key))
 before=ev('molZoom2D');click('#zoomInBtn');until('molZoom2D>'+str(before));click('#zoomOutBtn');until('Math.abs(molZoom2D-'+str(before)+')<1e-8')
 check(True,'Actual zoomIn/out returns same zoom')
 click('#comp5');until('numberingFlag===true');until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===6',seconds=15)
 check(True,'Parent numbering six actual SVG labels')
 for width in [1100,1500]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===6',seconds=15)
  check(ev('!!document.querySelector("#comp5.selected")&&numberingFlag'),'Resize keeps name selection and numbering '+str(width))
 ev('window.__pngResult=null;window.__originalAnchorClick=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){if(this.download&&this.download.endsWith("_2D.png")){let filename=this.download;fetch(this.href).then(r=>r.blob()).then(async b=>{let im=await createImageBitmap(b);window.__pngResult={filename,type:b.type,size:b.size,width:im.width,height:im.height};im.close();});return;}return window.__originalAnchorClick.apply(this,arguments);};true')
 click('#save2DBtn');until('!!window.__pngResult')
 png=json.loads(ev('JSON.stringify(window.__pngResult)'))
 check(png['width']==1200 and png['height']>90 and png['type']=='image/png'and png['size']>1000,'Real highlighted SVG→PNG render/decode, delivery intercepted only',png)
 ev('HTMLAnchorElement.prototype.click=window.__originalAnchorClick;true')
 click('[data-lang="en"]');until('location.search.includes("lang=en")');app_ready();until('selectedMol==='+json.dumps(key))
 ev('fNameExpandOpen();true');until('window.nameExpanded===true')
 check(ev('document.querySelector("#nameAnalysis .nameCompContainer").style.getPropertyValue("--nl-name-scale")==="1"'),'Expanded ENname resets normal-fit font scaling')
 screenshot(HERE/'final-expanded-name-en.png')
 ev('fNameExpandClose();true');until('window.nameExpanded===false')
 check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!!currentMolName'),'Expanded close preserves actual molecule/name')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot(HERE/'final-interactions-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'final-interactions-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
