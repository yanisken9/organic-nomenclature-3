"""Before/after forms and atom ownership using actual molecule/mode clicks."""
from pathlib import Path
import os
exec(compile(Path('docs/checks/ether-uniform-20261031/browser_support.py').read_text(),'support','exec'))
phase=os.environ.get('NAMELECULE_PHASE','before');prior=json.load(gzip.open(HERE/'forms-before.json.gz','rt'))['cases'] if phase=='after' else [];out={'cases':[],'completed':False,'phase':phase}
try:
    start('mulermoc-nom-52.html?audit=ether-forms-'+phase)
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        for key in KEYS:
            for mode in ['condensed','expanded','skeletal']:
                select_ui(key,mode);row=audit(width,phase)
                row['calibrated']=ev('!!molSvg.node.dataset.alkaneFixedCCScale')
                if phase=='after':
                    assert row['calibrated']==(mode=='expanded')
                    old=next(c for c in prior if (c['key'],c['mode'],c['width'])==(key,mode,width))
                    assert all(row[k]==old[k]for k in ['name','atomSymbols','bondGraph'])
                    if mode!='expanded':
                        if row['rawFinalSVG']!=old['rawFinalSVG']:
                            (HERE/'unchanged-form-comparison.json.gz').write_bytes(gzip.compress(json.dumps({'before':old,'after':row},ensure_ascii=False).encode(),mtime=0))
                        assert len(row['atoms'])==len(old['atoms'])
                        delta=max(abs(x-y)for a,b in zip(row['atoms'],old['atoms'])for x,y in zip(a['box'],b['box']))
                        assert all(a['text']==b['text']and a['font']==b['font']for a,b in zip(row['atoms'],old['atoms']))
                        row['unchangedFormMaxAtomBoxDeltaCSS']=delta
                        row['unchangedFormViewBoxEqual']=row['viewBox']==old['viewBox']
                        assert delta<.15,(key,mode,'Visible atom position changed',delta)
                out['cases'].append(row)
                if width==1500 and mode=='expanded'and key in ['dimethylether','isopropyl_methyl_ether','tert_butyl_isopropyl_ether']:
                    screenshot(HERE/(key+'-'+phase+'.png'))
            print(phase,width,key,'passed',flush=True)
    out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:save_result(out,'forms-'+phase+'.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
