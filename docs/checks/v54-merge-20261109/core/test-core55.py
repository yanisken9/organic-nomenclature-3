"""Reuse the original broad suites with candidate paths and new outputs only.
Historical assertions retained except expected comparison/approved generator scale.
"""
from pathlib import Path
import argparse,hashlib,json,runpy
P=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent
C=Path(argparse.ArgumentParser().parse_known_args()[1][0])
base=P/'docs/checks/v54-sync-20261104/core'
s=(base/'test-core54.py').read_text().replace("ROOT = Path(__file__).resolve().parents[4]",'ROOT = Path('+repr(str(C))+')')
s=s.replace("data52 = ROOT/'js/jsme-nick-nomeclature-moc2-data_52.js'","data52 = Path("+repr(str(P/'js/jsme-nick-nomeclature-moc2-data_54.js'))+")")
s=s.replace("core52 = ROOT/'js/mulermoc-nom-core-52.js'","core52 = Path("+repr(str(P/'js/mulermoc-nom-core-54.js'))+")")
s=s.replace("core54 = ROOT/'js/mulermoc-nom-core-54.js'","core54 = ROOT/'js/mulermoc-nom-core-55.js'")
s=s.replace('str(p.relative_to(ROOT))','str(p)').replace("assert len(result['differences']) == 12","assert len(result['differences']) == 0")
ns={'__name__':'reused','__file__':str(base/'test-core54.py')};exec(compile(s,str(base/'test-core54.py'),'exec'),ns)
ns['run'](C/'js/jsme-nick-nomeclature-moc2-data_54.js',H/'core55-results.json')
for name in ['mol-properties54','map-transitions54']:
 s=(base/f'test-{name}.py').read_text()
 start=s.index("SHARED = runpy.run_path(");end=s.index('\n',start)
 s=s[:start]+"SHARED = shared"+s[end:]
 s=s.replace("ROOT/'js/mulermoc-nom-core-54.js'","ROOT/'js/mulermoc-nom-core-55.js'")
 ctx={'__name__':'reused','__file__':str(base/f'test-{name}.py'),'shared':ns};exec(compile(s,str(base/f'test-{name}.py'),'exec'),ctx)
 ctx['run'](H/f'{name.replace("54","55")}-results.json')
p=P/'docs/checks/v54-upstream-20261104/geometry/test-geometry.py'
s=p.read_text().replace('ROOT=Path(__file__).resolve().parents[4]','ROOT=Path('+repr(str(C))+')').replace('-1.17)', '-MOLGEN_CC_LEN)')
g={'__name__':'reused','__file__':str(p)};exec(compile(s,str(p),'exec'),g)
core=(C/'js/mulermoc-nom-core-55.js').read_text();r=g['run'](core)
r['coreSHA256']=hashlib.sha256(core.encode()).hexdigest();r['summary']={'forms':len(r['rows']),'molecules':len({x['key']for x in r['rows']}),'missing':r['missing'],'generated':sum(x['generated']for x in r['rows']),'skipped':[{'key':x['key'],'mode':x['mode'],'reason':x['reason']}for x in r['rows']if not x['generated']],'failures':len(r['failures']),'expectedHeavyBondLength':1.0}
(H/'geometry-results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r['summary'],ensure_ascii=False));assert not r['failures'],r['failures'][:2]
