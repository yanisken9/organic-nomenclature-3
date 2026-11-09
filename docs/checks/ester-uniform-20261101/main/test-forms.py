"""Real Main before/after expanded forms plus unchanged-form representatives."""
from pathlib import Path
import os
exec(compile(Path('docs/checks/ester-uniform-20261101/main/browser_support.py').read_text(),'support','exec'))
phase=os.environ.get('NAMELECULE_PHASE','before')
prior=json.load(gzip.open(HERE/'forms-before.json.gz','rt'))['cases']if phase=='after'else[]
REP=KEYS
out={'phase':phase,'cases':[],'completed':False}
try:
    start('mulermoc-nom-52.html?audit=ester-forms-'+phase)
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        ev('document.getElementById("rotatePromptDismiss")?.click();true')
        for key in KEYS:
            for mode in (['expanded','condensed','skeletal']if key in REP else['expanded']):
                select_ui(key,mode)
                if phase=='before':
                    row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(width=width,phase=phase)
                else:row=audit(width,phase)
                row['calibrated']=ev('!!molSvg.node.dataset.alkaneFixedCCScale')
                if phase=='after':
                    assert row['calibrated']==(mode=='expanded'),('Calibration rejected',key,mode)
                    old=next(c for c in prior if(c['key'],c['mode'],c['width'])==(key,mode,width))
                    assert all(row[k]==old[k]for k in ['name','atomSymbols','bondGraph'])
                    if mode!='expanded':
                        assert len(row['atoms'])==len(old['atoms'])
                        delta=max(abs(x-y)for a,b in zip(row['atoms'],old['atoms'])for x,y in zip(a['box'],b['box']))
                        assert all(a['text']==b['text']and a['font']==b['font']for a,b in zip(row['atoms'],old['atoms']))
                        assert delta<.15,('Unchanged form moved',key,mode,delta)
                        row['unchangedFormMaxAtomBoxDeltaCSS']=delta
                out['cases'].append(row)
                if width==1500 and mode=='expanded'and key in REP:
                    screenshot(HERE/(key+'-'+phase+'.png'))
            print(phase,width,key,'passed',flush=True)
    out['completed']=True
except Exception as error:
    out.update(failure=str(error),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:save_result(out,'forms-'+phase+'.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
