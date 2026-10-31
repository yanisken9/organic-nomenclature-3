"""Targeted missing baseline390 + pixel confirmation of bbox overlap flags."""
from pathlib import Path
import os,json,gzip,traceback
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-general-audit-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8026/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi','exec'))
cat=json.loads(gzip.decompress((root/'catalog.json.gz').read_bytes()))
targets={width:[(x['key'],x['mode'])for x in cat['cases']if x['version']=='candidate'and x['width']==width and x['overlaps']]for width in [1500,390]};out={'cases':[],'completed':False}
try:
 for version in ['baseline','candidate']:
  navigate('app-'+version+'/mulermoc-nom-52.html?audit=overlap-followup');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((here/'final-svg-probe.js').read_text());ev((here/'overlap-pixels.js').read_text())
  for width in [1500,390]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
   for key,mode in targets[width]:
    ev('selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    row=json.loads(ev('auditFinalSvg().then(r=>JSON.stringify(r))'));row.update(version=version,width=width)
    row['pairInk']=json.loads(ev('auditOverlapPixels('+json.dumps(row['overlaps'])+').then(r=>JSON.stringify(r))'));out['cases'].append(row)
    print(version,width,key,'boxes',len(row['overlaps']),'realInkOverlaps',sum(x['overlappingInkPixels']>0 for x in row['pairInk']),flush=True)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(root/'overlap-followup.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('overlap followup',out['completed'],'cases',len(out['cases']),flush=True)
