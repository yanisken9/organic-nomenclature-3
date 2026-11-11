from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'completed':False,'measurements':[],'scope':'Developer CSS fit investigation in disposable tab; source files unchanged'}
def measure(label):
 d=read('(()=>{let z=document.querySelector("#answer-zone"),row=document.querySelector("#answer-tiles"),b=[...row.querySelectorAll("button")],a=z.getBoundingClientRect();return{label:'+json.dumps(label)+',viewport:innerWidth,clientWidth:z.clientWidth,scrollWidth:z.scrollWidth,rowWidth:row.getBoundingClientRect().width,first:b[0].getBoundingClientRect().left,last:b.at(-1).getBoundingClientRect().right,left:a.left+z.clientLeft,right:a.left+z.clientLeft+z.clientWidth,font:getComputedStyle(b[0]).fontSize,minHeight:Math.min(...b.map(x=>x.getBoundingClientRect().height)),rows:[...new Set(b.map(x=>Math.round(x.getBoundingClientRect().top)))].length}})()');out['measurements'].append(d);print(json.dumps(d),flush=True)
try:
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1024,'height':900},'devicePixelRatio':1});open_page('games/name-builder.html?molecule=dimethyl_4_5_hexen_5_yn_1_one_3');wait('document.querySelectorAll("#bank-tiles button").length>0',60)
 ev('(()=>{for(let p of __builderEvents.findLast(e=>e.type==="round").pieces){if(p.text==="-3-")continue;[...document.querySelectorAll("#bank-tiles button")].find(b=>b.textContent===p.text).click()}document.querySelector("#answer-zone").scrollLeft=0;return true})()');measure('before8')
 ev('document.querySelector(".answer-panel").scrollIntoView({block:"center",behavior:"instant"});true');shot('before-1024.png')
 for name,gap,padding in [('moderate',4,6),('compact',3,5)]:
  ev('(()=>{document.getElementById("probe-style")?.remove();let s=document.createElement("style");s.id="probe-style";s.textContent='+json.dumps('.tiles.answer-tiles{gap:'+str(gap)+'px}.answer-tiles .tile-button{min-width:32px;padding:10px '+str(padding)+'px}')+';document.head.append(s);document.querySelector("#answer-zone").scrollLeft=0;return true})()');measure(name+'8')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(HERE/'probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
if not out['completed']:raise SystemExit(1)
