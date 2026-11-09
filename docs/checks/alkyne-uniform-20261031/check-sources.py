"""Read-only source checks; output only to explicitly supplied JSON path."""
from pathlib import Path
import argparse, ast, hashlib, json, math, runpy, subprocess, difflib

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def check(backup):
    helper=runpy.run_path(str(HERE/'transform.py'));keys=helper['KEYS'];data=helper['DATA']
    baseline=json.loads((backup/'baseline.json').read_text());original=backup/'original'
    def registry(code):
        script='var window={};'+code+';print(JSON.stringify({mols:window.MOL2D,examples:nameExamples}));'
        return json.loads(subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps(script)+'\n',text=True,capture_output=True,check=True).stdout)
    before=registry((original/data).read_text());after=registry((ROOT/data).read_text())
    assert before['examples']==after['examples']
    assert set(before['mols'])==set(after['mols']) and len(after['mols'])==141
    for k,forms in before['mols'].items():
        for form,mol in forms.items():
            if k not in keys or form!='expanded': assert after['mols'][k][form]==mol,(k,form)
    rows=[]
    def molecule(old,new,label):
        ol,oa,ob=helper['parse'](old);nl,na,nb=helper['parse'](new);n=len(oa)
        assert len(na)==n and ob==nb and ol[:4]==nl[:4] and ol[4+n:]==nl[4+n:]
        assert all(ol[4+i][20:]==nl[4+i][20:] for i in range(n))
        counts={s:sum(a[2]==s for a in na) for s in ['C','H']}
        assert counts['H']==2*counts['C']-2 and sum(o==3 for a,b,o in nb)==1
        val=[0]*n;lengths={'CH':[],'CC':[],'C#C':[]}
        assert len(set((a[0],a[1])for a in na))==n
        for a,b,o in nb:
            val[a]+=o;val[b]+=o
            length=math.dist(na[a][:2],na[b][:2]);kind='CH' if na[a][2]!=na[b][2] else ('C#C' if o==3 else 'CC')
            assert abs(length-(.3094 if kind=='CH' else .6188))<1e-8,(label,a,b,length)
            dx,dy=na[b][0]-na[a][0],na[b][1]-na[a][1]
            assert abs(dx)<1e-9 or abs(dy)<1e-9
            odx,ody=oa[b][0]-oa[a][0],oa[b][1]-oa[a][1]
            assert dx*odx+dy*ody>0 and abs(dx*ody-dy*odx)<.0001
            lengths[kind].append(length)
        assert all(v==(4 if na[i][2]=='C'else 1) for i,v in enumerate(val))
        for a,b,order in nb:
            if order!=3:continue
            for center in [a,b]:
                near=[v if u==center else u for u,v,o in nb if center in [u,v]]
                assert len(near)==2
                p,q=near;vx,vy=na[p][0]-na[center][0],na[p][1]-na[center][1]
                wx,wy=na[q][0]-na[center][0],na[q][1]-na[center][1]
                assert abs(vx*wy-vy*wx)<1e-9 and vx*wx+vy*wy<0
        return {'source':label,'formula':'C%dH%d'%(counts['C'],counts['H']),'CCCount':len(lengths['CC']),'tripleCount':len(lengths['C#C']),'CHCount':len(lengths['CH']),'graphFieldsDirectionsPreserved':True,'spLinear':True}
    for k in keys: rows.append(molecule(before['mols'][k]['expanded'],after['mols'][k]['expanded'],k))
    physical=[]
    for s in baseline['paths']:
        if s.endswith('.mol'):
            row=molecule((original/s).read_text(),(ROOT/s).read_text(),s)
            key=Path(s).name.removesuffix('_2D_Expanded.mol') if hasattr(str,'removesuffix') else Path(s).name[:-16]
            assert (ROOT/s).read_text().rstrip()==after['mols'][key]['expanded'].rstrip()
            physical.append(row)
    def masked(code):
        for k in keys:
            m,_=helper['literal'](code,k);code=code[:m.start(1)]+'MOL'+code[m.end(1):]
        return code
    assert masked((original/data).read_text())==masked((ROOT/data).read_text())
    allowed=set(baseline['paths']);protected={s:h for s,h in baseline['files'].items() if s not in allowed}
    assert all(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h for s,h in protected.items())
    for s in [data,'js/mulermoc-nom-molview-52.js']:
        subprocess.run([JSC,'-e','new Function(JSON.parse(readline()));'],input=json.dumps((ROOT/s).read_text())+'\n',text=True,capture_output=True,check=True)
    for s in HERE.glob('*.py'):ast.parse(s.read_text())
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==baseline['HEAD']
    assert hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()==baseline['indexSHA256']
    return {'passed':True,'molecules':rows,'physicalSources':physical,'protectedUnchanged':len(protected),'other133RecordsAndTargetOtherFormsUnchanged':True,'outside8MOLLiteralsUnchanged':True,'coreChangedToday':False,'HEADIndexUnchanged':True}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--backup',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=check(args.backup);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
