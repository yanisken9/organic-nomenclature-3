"""Real Main before/after expanded forms plus unchanged-form representatives."""
from pathlib import Path
import os
exec(compile(Path('docs/checks/carbonyl-acid-uniform-20261101/browser_support.py').read_text(),'support','exec'))
phase=os.environ.get('NAMELECULE_PHASE','before')
prior=json.load(gzip.open(HERE/'forms-before.json.gz','rt'))['cases']if phase=='after'else[]
REP=['methanal','ethyl_4_isopropyl_3_methyl_2_hexanal',
     'isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5',
     'ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid',
     'ethyl_3_isopropyl_2_dimethyl_4_5_hexadien_2_4_dioic_acid',
     'aminobutanoic_acid_3','dihydroxybutanedioic_acid_2_3','methanoicacid']
out={'phase':phase,'cases':[],'completed':False}
try:
    start('mulermoc-nom-52.html?audit=carbonyl-acid-forms-'+phase)
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        ev('document.getElementById("rotatePromptDismiss")?.click();true')
        for key in KEYS:
            for mode in (['expanded','condensed','skeletal']if key in REP else['expanded']):
                select_ui(key,mode);row=audit(width,phase)
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
