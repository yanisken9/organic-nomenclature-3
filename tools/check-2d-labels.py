"""Acceptance check of current/future available Main 2D forms in isolated Firefox.

Start a local server and isolated Firefox with --remote-debugging-port 9237 first.
Example: python3 -B tools/check-2d-labels.py --base-url http://127.0.0.1:8013/
 --output /tmp/namelecule-2d-check.json.gz
Captures actual browser evidence; refuses contact<=0.5CSSpx, fully hidden bonds,
clipping, missing/duplicate atom ownership or a controlled unavailable drawing.
This does not certify chemical naming or graph correctness. It writes only the
explicit output path and changes transient selections in its own browser tab.
"""
from pathlib import Path
import argparse,os,json,gzip,traceback
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--base-url',required=True)
p.add_argument('--bidi-port',type=int,default=9237)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--width',type=int,action='append')
p.add_argument('--molecule',action='append')
p.add_argument('--mode',choices=['condensed','expanded','skeletal'],action='append')
args=p.parse_args()
os.environ['NAMELECULE_TEST_BASE_URL']=args.base_url.rstrip('/')+'/'
os.environ['NAMELECULE_BIDI_PORT']=str(args.bidi_port)
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'namelecule-bidi','exec'))
out={'cases':[],'completed':False,'chemicalCertification':False,'failures':[]}
try:
 navigate('mulermoc-nom-52.html?audit=2d-acceptance');app_ready()
 ev('document.fonts.ready.then(()=>true)')
 fixtures=json.loads(ev('JSON.stringify(Object.entries(window.MOL2D).flatMap(([key,forms])=>["condensed","expanded","skeletal"].filter(mode=>typeof forms[mode]==="string"&&forms[mode].trim()).map(mode=>({key,mode}))))'))
 if args.molecule:fixtures=[f for f in fixtures if f['key']in args.molecule]
 if args.mode:fixtures=[f for f in fixtures if f['mode']in args.mode]
 if not fixtures:raise ValueError('No matching available forms')
 out['environment']=json.loads(ev('JSON.stringify({url:location.href,userAgent:navigator.userAgent,resources:performance.getEntriesByType("resource").filter(r=>r.name.includes(".cache.js")).map(r=>r.name)})'))
 ev((ROOT/'tools/2d-label-probe.js').read_text())
 for width in args.width or [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for i,f in enumerate(fixtures):
   ev('selectedMol='+json.dumps(f['key'])+';mode2D='+json.dumps(f['mode'])+';fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
   if ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'):
    row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'))
    owners=json.loads(ev('JSON.stringify([...document.querySelectorAll("#jsmeNomeclatureSVG text:not([id^=number])")].map(n=>Number(n.dataset.nameleculeAtom)))'))
    owner_error=any(not isinstance(n,(int,float))or not float(n).is_integer()or n<1 or n>len(row['atomSymbols'])for n in owners)or len(set(owners))!=len(owners)
    row['passed']=not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount']and not owner_error
    row['owners']=owners
   else:row={'key':f['key'],'mode':f['mode'],'renderError':ev('document.getElementById("jsmeNomeclatureSVG").textContent'),'passed':False}
   row['width']=width;out['cases'].append(row)
   if not row['passed']:out['failures'].append({'key':f['key'],'mode':f['mode'],'width':width})
   if (i+1)%60==0:print('2D acceptance',width,i+1,'/',len(fixtures),'failures',len(out['failures']),flush=True)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc()
finally:
 out['javascriptErrors']=js_errors
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'cases':len(out['cases']),'failed':len(out['failures']),'javascriptErrors':len(js_errors)}))
if not out['completed']or out['failures']or js_errors:raise SystemExit(1)
