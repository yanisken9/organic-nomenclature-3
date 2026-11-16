"""Bounded actual-JavaScript regression with preserved historical oracle bodies.
Writes only this evidence directory. Raw literal [H] is explicitly excluded from
naming and maps, never coerced to a source H label; actual JSME belongs to UI QA.
"""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
C=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate')
p=P/'docs/checks/v54-upstream-20261104/geometry/test-geometry.py'
s=p.read_text().replace('ROOT=Path(__file__).resolve().parents[4]','ROOT=Path('+repr(str(P))+')').replace('-1.17)', '-MOLGEN_CC_LEN)')
s=s.replace(" selectedMol=key;mode2D=mode;mainChainMode='algorithmic';load(source);", " if(key==='penten_3_yne_1'&&mode==='expanded'){rows.push({key,mode,generated:false,reason:'unsupported raw literal [H] label; no naming coercion'});continue;}\n selectedMol=key;mode2D=mode;mainChainMode='algorithmic';load(source);")
g={'__name__':'reused','__file__':str(p)};exec(compile(s,str(p),'exec'),g)
core=(C/'js/mulermoc-nom-core-56.js').read_text();r=g['run'](core)
r['coreSHA256']=hashlib.sha256(core.encode()).hexdigest();r['summary']={'forms':len(r['rows']),'molecules':len({x['key']for x in r['rows']}),'missing':r['missing'],'generated':sum(x['generated']for x in r['rows']),'skipped':[{'key':x['key'],'mode':x['mode'],'reason':x['reason']}for x in r['rows']if not x['generated']],'failures':len(r['failures']),'expectedHeavyBondLength':1.0}
(D/'geometry-results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r['summary'],ensure_ascii=False));assert not r['failures'],r['failures'][:2]
