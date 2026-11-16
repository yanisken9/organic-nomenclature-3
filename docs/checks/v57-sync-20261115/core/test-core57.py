"""Bounded actual-JavaScript regression with preserved historical oracle bodies.
Writes only this evidence directory. Raw literal [H] is explicitly excluded from
naming and maps, never coerced to a source H label; actual JSME belongs to UI QA.
"""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
C=Path('/private/tmp/namelecule-v57-sync-20261115-l4r9e5_s/candidate')
base=P/'docs/checks/v54-sync-20261104/core'
s=(base/'test-core54.py').read_text()
s=s.replace('ROOT = Path(__file__).resolve().parents[4]', 'ROOT = Path('+repr(str(P))+')')
s=s.replace("data52 = ROOT/'js/jsme-nick-nomeclature-moc2-data_52.js'", "data52 = ROOT/'js/jsme-nick-nomeclature-moc2-data_56.js'")
s=s.replace("core52 = ROOT/'js/mulermoc-nom-core-52.js'", "core52 = ROOT/'js/mulermoc-nom-core-56.js'")
s=s.replace("core54 = ROOT/'js/mulermoc-nom-core-54.js'", "core54 = Path("+repr(str(C/'js/mulermoc-nom-core-57.js'))+")")
s=s.replace('str(p.relative_to(ROOT))','str(p)')
s=s.replace("for(const mode of row.modes){for(const cm", "for(const mode of row.modes){if(row.key==='penten_3_yne_1'&&mode==='expanded')continue;for(const cm")
s=s.replace("assert len(result['differences']) == 12", "assert len(result['differences']) == 0")
s=s.replace("assert len(summary['untranslatedMaps']) == 2", "assert len(summary['untranslatedMaps']) == 0")
s=s.replace("assert summary['exactMaps'] == summary['mapCases']-2", "assert summary['exactMaps'] == summary['mapCases']")
a=s.index("    assert summary['reorderedGraphMapFailures'] == [");b=s.index("    assert not summary['signatureMismatches']",a)
s=s[:a]+"    assert summary['reorderedGraphMapFailures'] == []\n"+s[b:]
ns={'__name__':'reused','__file__':str(base/'test-core54.py')};exec(compile(s,str(base/'test-core54.py'),'exec'),ns)
ns['run'](C/'js/jsme-nick-nomeclature-moc2-data_57.js',D/'core57-results.json')
for name in ['mol-properties54','map-transitions54']:
 s=(base/f'test-{name}.py').read_text();start=s.index('SHARED = runpy.run_path(');end=s.index('\n',start);s=s[:start]+'SHARED = shared'+s[end:]
 s=s.replace("ROOT/'js/mulermoc-nom-core-54.js'", "Path("+repr(str(C/'js/mulermoc-nom-core-57.js'))+")")
 s=s.replace("ROOT/'js/jsme-nick-nomeclature-moc2-data_54.js'", "Path("+repr(str(C/'js/jsme-nick-nomeclature-moc2-data_57.js'))+")")
 s=s.replace('str(p.relative_to(ROOT))','str(p)')
 if name=='mol-properties54':
  s=s.replace(' const chain=chainFor(key,mode,text);', ''' if(key==='penten_3_yne_1'&&mode==='expanded'){
   check(!fMolCanTransform2D(m,true),'raw literal [H] must remain unsupported');
   check(Object.values(variants(text,[])).every(v=>v===null),'raw literal [H] generator rejection');
   skips.push({key,mode,reason:'unsupported literal element/query label'});continue;
 }
 const chain=chainFor(key,mode,text);''')
 else:
  s=s.replace("mode2D=mode;load(window.MOL2D[key][mode]);", "mode2D=mode;if(key==='penten_3_yne_1'&&mode==='expanded'){unsupported.push({key,mode,cm,reason:'raw literal [H] naming outside whitelist'});continue;}load(window.MOL2D[key][mode]);")
 ctx={'__name__':'reused','__file__':str(base/f'test-{name}.py'),'shared':ns};exec(compile(s,str(base/f'test-{name}.py'),'exec'),ctx)
 ctx['run'](D/f'{name.replace("54","57")}-results.json')
p=P/'docs/checks/v54-upstream-20261104/geometry/test-geometry.py'
s=p.read_text().replace('ROOT=Path(__file__).resolve().parents[4]','ROOT=Path('+repr(str(P))+')').replace('-1.17)', '-MOLGEN_CC_LEN)')
s=s.replace(" selectedMol=key;mode2D=mode;mainChainMode='algorithmic';load(source);", " if(key==='penten_3_yne_1'&&mode==='expanded'){rows.push({key,mode,generated:false,reason:'unsupported raw literal [H] label; no naming coercion'});continue;}\n selectedMol=key;mode2D=mode;mainChainMode='algorithmic';load(source);")
g={'__name__':'reused','__file__':str(p)};exec(compile(s,str(p),'exec'),g)
core=(C/'js/mulermoc-nom-core-57.js').read_text();r=g['run'](core)
r['coreSHA256']=hashlib.sha256(core.encode()).hexdigest();r['summary']={'forms':len(r['rows']),'molecules':len({x['key']for x in r['rows']}),'missing':r['missing'],'generated':sum(x['generated']for x in r['rows']),'skipped':[{'key':x['key'],'mode':x['mode'],'reason':x['reason']}for x in r['rows']if not x['generated']],'failures':len(r['failures']),'expectedHeavyBondLength':1.0}
(D/'geometry-results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r['summary'],ensure_ascii=False));assert not r['failures'],r['failures'][:2]
