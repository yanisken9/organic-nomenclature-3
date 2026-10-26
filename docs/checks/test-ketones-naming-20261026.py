"""Real core/viewer naming, graph-order probes and whole-library regression."""
from pathlib import Path
import json,subprocess,random
ns={};exec(Path('docs/checks/test-alcohols-naming-20261024.py').read_text().split("js='var run")[0],ns)
t=ns['body'];tail=t[t.index('var MOL2D=window.MOL2D;'):t.index('return {name:currentMolName')]
tail=tail.replace('probe.edges.map(atoms=>({atoms,order:1}))','probe.edges.map(e=>({atoms:e.slice(0,2),order:e[2]}))')
ret='return {name:currentMolName,series:fGetMoleculeClassification().seriesKey,parts:nameComponentsList,chain:mainChainAtomsList,signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList),signature3:probe?null:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)};'
prefix='var window={},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};'
files=['js/jsme-nick-nomeclature-moc2-data_51.js','js/mulermoc-nom-core-51.js','js/mulermoc-nom-molview-51.js']
body=prefix+'\n'.join(Path(p).read_text() for p in files)+tail+ret
base=Path('/tmp/namelecule-before-ketones-20261026')
# Old library comparison does not need 3D parsing.
tail0=tail[:tail.index('if(!probe){fParseSDF3D')]+ret.replace('signature3:probe?null:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)','signature3:null')
before=prefix+'\n'.join(((base/p) if (base/p).exists() else Path(p)).read_text() for p in files)+tail0
after=prefix+'\n'.join(Path(p).read_text() for p in files)+tail0
js='var run=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(body)+');var rows=[];'
specs=json.load(open('docs/checks/ketones-specs-20261026.json'))
for s in specs:
 for mode in ['condensed','expanded','skeletal']:
  for chain in ['algorithmic','data']:
   args=[s['key'],mode,chain,Path('mols/nomeclature-moc2',s['key']+'_3D.sdf').read_text(),None]
   js+='rows.push('+json.dumps([s['key'],mode,chain])+'.concat([run('+','.join(json.dumps(x) for x in args)+')]));'
 rng=random.Random(20261026)
 for i in range(12):
  order=list(range(len(s['xy'])));rng.shuffle(order);mapping={old+1:new+1 for new,old in enumerate(order)}
  probe={'types':['C' if old<s['carbons'] else 'O' for old in order],'edges':[[mapping[a],mapping[b],o] for a,b,o in s['edges']]};rng.shuffle(probe['edges'])
  args=[s['key'],'condensed','algorithmic','',probe]
  js+='rows.push('+json.dumps([s['key'],'permutation',i])+'.concat([run('+','.join(json.dumps(x) for x in args)+')]));'
js+='var before=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(before)+'),after=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(after)+');'
data=(base/files[0]).read_text()
js+='var inv=(new Function("var window={};"+'+json.dumps(data)+'+";return Object.keys(window.MOL2D).flatMap(k=>Object.keys(window.MOL2D[k]).filter(m=>window.MOL2D[k][m]).map(m=>[k,m]));"))();var n=0;for(var pair of inv){for(var chain of ["algorithmic","data"]){var args=[pair[0],pair[1],chain,"",null];var a=before.apply(null,args),b=after.apply(null,args);if(JSON.stringify(a)!==JSON.stringify(b))throw Error(JSON.stringify([args,a,b]));n++;}}print(JSON.stringify({rows:rows,regressionCases:n}));'
# Boundary tests for the approved saturated acyclic monoketone scope.
js=js.replace('print(JSON.stringify({rows:rows,regressionCases:n}));','')
guard_source=prefix+'\n'.join(Path(p).read_text() for p in files)+"return fIsAcyclicSaturatedMonoketoneGraph(conn,types,bonds);"
js+='var guard=new Function("conn","types","bonds",'+json.dumps(guard_source)+');var guards=[];'
for label,types,edges,expected in [
 ('ketone',['C','C','C','O'],[[1,2,1],[2,3,1],[2,4,2]],True),
 ('branched ketone',['C','C','C','C','C','O'],[[1,2,1],[2,3,1],[3,4,1],[3,5,1],[2,6,2]],True),
 ('aldehyde',['C','C','O'],[[1,2,1],[1,3,2]],False),
 ('acid',['C','O','O'],[[1,2,2],[1,3,1]],False),
 ('alcohol',['C','C','O'],[[1,2,1],[2,3,1]],False),
 ('unsaturated ketone',['C','C','C','C','O'],[[1,2,1],[2,3,1],[3,4,2],[2,5,2]],False),
 ('cyclic ketone',['C','C','C','O'],[[1,2,1],[2,3,1],[3,1,1],[1,4,2]],False),
 ('diketone',['C','C','C','C','O','O'],[[1,2,1],[2,3,1],[3,4,1],[2,5,2],[3,6,2]],False)]:
 conn=[[] for _ in types]
 for a,b,o in edges:conn[a-1].append(b-1);conn[b-1].append(a-1)
 js+='var g=guard('+','.join(json.dumps(x)for x in [conn,types,edges])+');if(g!=='+json.dumps(expected)+')throw Error('+json.dumps(label)+');guards.push('+json.dumps(label)+');'
js+='print(JSON.stringify({rows:rows,regressionCases:n,guardBoundaries:guards}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr)
result=json.loads(r.stdout);bykey={s['key']:s for s in specs}
for key,mode,chain,row in result['rows']:
 assert row['name']==bykey[key]['name'] and row['series']=='ketone',(key,mode,chain,row)
 assert len(row['chain'])==bykey[key]['parent'],(key,row)
 if mode!='permutation':assert row['signature']==row['signature3'],(key,mode,chain,row)
Path('docs/checks/ketones-naming-20261026.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(result['rows']),'new naming/ordering cases;',result['regressionCases'],'old library cases unchanged')
