"""All 422 available forms: current names/text versus captured unmodified baseline.
This checks invariance, not independent chemical naming certification.
"""
from pathlib import Path
import os,json,gzip,traceback,time,xml.etree.ElementTree as ET
root=Path('/tmp/namelecule-jsmol-integration-20261031');repo=Path.cwd();os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8030/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
old=json.loads(gzip.decompress((repo/'docs/checks/svg-general-audit-20261031/catalog.json.gz').read_bytes()))['cases'];old=[r for r in old if r['version']=='baseline' and r['width']==1500];assert len(old)==422
out={'rows':[],'completed':False}
def labels(svg):
 return [''.join(n.itertext()) for n in ET.fromstring(svg).iter() if n.tag.split('}')[-1]=='text' and not n.get('id','').startswith('number')]
try:
 navigate('main/mulermoc-nom-52.html?audit=2d-name-invariants');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)')
 for i,r in enumerate(old):
  ev('selectedMol='+json.dumps(r['key'])+';mode2D='+json.dumps(r['mode'])+';fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
  n=json.loads(ev('JSON.stringify({key:selectedMol,mode:mode2D,name:currentMolName,labels:[...document.querySelectorAll("#jsmeNomeclatureSVG svg text:not([id^=number])")].map(n=>n.textContent)})'))
  n['expectedName']=r['name'];n['expectedLabels']=labels(r['rawFinalSVG']);n['passed']=n['name']==n['expectedName'] and n['labels']==n['expectedLabels'] and n['key']==r['key'] and n['mode']==r['mode'];out['rows'].append(n)
  if (i+1)%60==0:print('invariants',i+1,'failures',sum(not v['passed'] for v in out['rows']),flush=True)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(root/'invariants.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('invariants complete',out['completed'],'rows',len(out['rows']),'failures',sum(not v['passed'] for v in out['rows']),'errors',len(js_errors),flush=True)
