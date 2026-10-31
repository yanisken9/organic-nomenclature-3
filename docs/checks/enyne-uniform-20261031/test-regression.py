"""Bounded previous-category guards plus matched-viewport follow-up of old captures."""
from pathlib import Path
import os,json,gzip,traceback
ROOT=Path(__file__).resolve().parents[3];TMP=Path('/tmp/namelecule-enyne-uniform-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8032/main/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
read=lambda p:json.load(gzip.open(p,'rt'))
prior=read('/tmp/namelecule-alkadiene-uniform-20261031/regression.json.gz')['cases']+read('/tmp/namelecule-alkadiene-uniform-20261031/after.json.gz')['cases']
index={(c['key'],c['width']):c for c in prior if c['mode']=='expanded'};keys=list(dict.fromkeys(k for k,w in index))
assert len(keys)==31
out={'cases':[],'completed':False};paired={'cases':[],'completed':False}
def load(base):
 os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8032/'+base+'/'
 navigate('mulermoc-nom-52.html?audit=bounded-regression');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((ROOT/'tools/2d-label-probe.js').read_text())
def capture(key,width,mode="expanded"):
 ev('selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
 row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(width=width)
 assert not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount']
 return row
try:
 load('main')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key in keys:
   row=capture(key,width);old=index[key,width]
   assert all(row[k]==old[k]for k in ['name','atomSymbols','bondGraph'])
   assert [a['text']for a in row['atoms']]==[a['text']for a in old['atoms']]
   out['cases'].append(row)
  print('old31 guards',width,'passed',flush=True)
 out['completed']=True
 # Historical captures used different native viewport sizes during resize.
 # Compare the exact three cases afresh under the same settled viewport.
 for base in ['diene-baseline','main']:
  load(base)
  for width in [1500,390]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
   until('innerWidth==='+str(width));ev('new Promise(r=>setTimeout(()=>r(true),350))')
   targets=[('hexen_1_yne_4','condensed')]
   if width==390:targets += [(k,'expanded')for k in ['ethyne','methyl_3_butene_1','methyl_2_propene']]
   for key,mode in targets:
    row=capture(key,width,mode);row['base']=base;paired['cases'].append(row)
 for a,b in zip(paired['cases'][:5],paired['cases'][5:]):
  assert (a['key'],a['mode'],a['width'])==(b['key'],b['mode'],b['width']) and a['rawFinalSVG']==b['rawFinalSVG'],(a['key'],a['mode'],a['width'])
 paired['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;paired['javascriptErrors']=js_errors
 for name,data in [('regression.json.gz',out),('matched-viewport.json.gz',paired)]:
  (TMP/name).write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False).encode(),mtime=0))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'guards':len(out['cases']),'pairedExact':paired['completed'],'errors':len(js_errors)}),flush=True)
if not out['completed']or not paired['completed']or js_errors:raise SystemExit(1)
