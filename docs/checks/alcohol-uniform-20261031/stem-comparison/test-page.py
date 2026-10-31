# -*- coding: utf-8 -*-
"""Check the static comparison controls in isolated Firefox; writes own evidence."""
from pathlib import Path
import os,json,traceback
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'cases':[],'completed':False}
try:
 navigate('docs/checks/alcohol-uniform-20261031/stem-comparison/index.html')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  boxes=[]
  for name in ['current','equal-invalid','proposed']:
   ev('document.querySelector(\'[data-case="'+name+'"]\').click();true')
   until('document.getElementById("drawing").complete&&document.getElementById("drawing").naturalWidth>0')
   row=json.loads(ev('JSON.stringify((()=>{const b=document.getElementById("drawing").getBoundingClientRect();return {pressed:[...document.querySelectorAll("[aria-pressed=true]")].map(b=>b.dataset.case),image:document.getElementById("drawing").getAttribute("src"),size:[b.width,b.height],detailHidden:document.getElementById("detail").hidden,overflow:document.documentElement.scrollWidth>innerWidth+1};})())'));row.update(width=width,case=name)
   assert row['pressed']==[name]and row['image']==name+'.svg?v=stem-098-applied'and row['detailHidden']==(name!='equal-invalid')and not row['overflow']
   boxes.append(row['size']);out['cases'].append(row)
   if width==1500 or name=='proposed':screenshot(HERE/(name+'-'+str(width)+'.png'))
  assert boxes[0]==boxes[1]==boxes[2],boxes
  ev('document.querySelector("details").open=true;true');until('[...document.querySelectorAll("details img")].every(i=>i.complete&&i.naturalWidth>0)');assert not ev('document.documentElement.scrollWidth>innerWidth+1');ev('document.querySelector("details").open=false;true')
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(HERE/'page-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'cases':len(out['cases']),'errors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
