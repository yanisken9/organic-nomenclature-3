"""Rerasterize exact captured final SVGs with corrected independent mask discovery.
No molecule regeneration. Validate fonts/label boxes/viewport against original.
Initial mask counters are superseded; original input SVGs remain preserved.
"""
from pathlib import Path
import os,json,gzip,traceback,hashlib
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-general-audit-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8026/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi','exec'))
result={'datasets':{},'completed':False,'method':'exact stored SVG replay; corrected mask discovery; no app regeneration','probeSHA256':hashlib.sha256((here/'final-svg-probe.js').read_bytes()).hexdigest()}
try:
 navigate('replay.html');ev('document.fonts.ready.then(()=>true)');ev((here/'final-svg-probe.js').read_text());call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 for dataset in ['catalog','controls','overlap-followup']:
  raw=json.loads(gzip.decompress((root/(dataset+'.json.gz')).read_bytes()));rows=raw['cases'];checked=[]
  for i,row in enumerate(rows):
   ev('window.__auditReplaySource='+json.dumps(row)+';document.getElementById("snapshot").style.cssText="width:'+str(row['viewport'][0])+'px;height:'+str(row['viewport'][1])+'px";document.getElementById("snapshot").innerHTML=__auditReplaySource.rawFinalSVG;true')
   new=json.loads(ev('auditFinalSvg().then(r=>JSON.stringify(r))'))
   assert [a['text']for a in new['atoms']]==[a['text']for a in row['atoms']],(dataset,i,'text')
   delta=max([abs(x-y)for a,b in zip(row['atoms'],new['atoms'])for x,y in zip(a['box'],b['box'])]or[0])
   assert delta<.05,(dataset,i,'layout changed',delta)
   assert [a['font']for a in new['atoms']]==[a['font']for a in row['atoms']],(dataset,i,'font')
   assert all(abs(x-y)<.05 for x,y in zip(new['viewport'],row['viewport'])),(dataset,i,'viewport')
   entry={k:v for k,v in row.items()if k not in ['raster','rawFinalSVG']};entry.update(raster=new['raster'],replayLabelBoxMaxDelta=delta,sourceSVG_SHA256=hashlib.sha256(row['rawFinalSVG'].encode()).hexdigest());checked.append(entry)
   if (i+1)%100==0:print(dataset,i+1,'/',len(rows),flush=True)
  result['datasets'][dataset]=checked
 # A negative and positive control, with and without original canvas rect.
 raw=json.loads(gzip.decompress((root/'catalog.json.gz').read_bytes()))['cases'];sample=next(x for x in raw if x['version']=='candidate'and x['width']==1500 and x['key']=='ethanenitrile'and x['mode']=='condensed')
 result['oracleControls']=[]
 for mode in ['original','remove-first-backplate','remove-backplate-add-canvas-background']:
  ev('window.__auditReplaySource='+json.dumps(sample)+';document.getElementById("snapshot").style.cssText="width:'+str(sample['viewport'][0])+'px;height:'+str(sample['viewport'][1])+'px";document.getElementById("snapshot").innerHTML=__auditReplaySource.rawFinalSVG;true')
  if mode!='original':ev('document.querySelector("#snapshot svg rect").remove();true')
  if mode.endswith('add-canvas-background'):
   ev('(()=>{let g=document.querySelector("#snapshot svg g"),r=document.createElementNS("http://www.w3.org/2000/svg","rect");for(let [k,v]of Object.entries({x:0,y:0,width:10000,height:10000,fill:"white"}))r.setAttribute(k,v);g.insertBefore(r,g.firstChild)})();true')
  v=json.loads(ev('auditFinalSvg().then(r=>JSON.stringify(r))'));result['oracleControls'].append({'mode':mode,'raster':v['raster']});print('oracle',mode,v['raster']['inkWithinHalfCssPixelOfBond'],flush=True)
 assert result['oracleControls'][0]['raster']['inkWithinHalfCssPixelOfBond']==0
 assert all(v['raster']['inkWithinHalfCssPixelOfBond']>0 for v in result['oracleControls'][1:])
 result['completed']=True
except Exception as e:result['failure']=str(e);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors;(root/'corrected-replay.json.gz').write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('recheck completed',result['completed'],'counts',{k:len(v)for k,v in result['datasets'].items()},flush=True)
