import sys
"""Real core/viewer naming, graph-order probes and whole-library regression."""
from pathlib import Path
import json,subprocess,random,gzip,base64
ns={};exec(Path('docs/checks/test-alcohols-naming-20261024.py').read_text().split("js='var run")[0],ns)
t=ns['body'];tail=t[t.index('var MOL2D=window.MOL2D;'):t.index('return {name:currentMolName')]
tail=tail.replace('probe.edges.map(atoms=>({atoms,order:1}))','probe.edges.map(e=>({atoms:e.slice(0,2),order:e[2]}))')
ret='return {name:currentMolName,series:fGetMoleculeClassification().seriesKey,parts:nameComponentsList,chain:mainChainAtomsList,signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList),signature3:probe?null:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)};'
prefix='var window={},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};'
files=['js/jsme-nick-nomeclature-moc2-data_52.js','js/mulermoc-nom-core-52.js','js/mulermoc-nom-molview-52.js']
body=prefix+'\n'.join(Path(p).read_text() for p in files)+tail+ret
old_sources={p:base64.b64decode(v).decode() for p,v in json.loads(gzip.decompress(Path('docs/checks/acids-before-source-20261028.json.gz').read_bytes())).items()}

# Old library comparison does not need 3D parsing.
tail0=tail[:tail.index('if(!probe){fParseSDF3D')]+ret.replace('signature3:probe?null:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)','signature3:null')
before=prefix+'\n'.join(old_sources[p] for p in files)+tail+ret
after=prefix+'\n'.join(Path(p).read_text() for p in files)+tail+ret
js='var run=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(body)+');var rows=[];'
specs=json.load(open('docs/checks/acids-specs-20261028.json'))
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
data=old_sources[files[0]]
sdfs={p.stem[:-3]:p.read_text() for p in Path('mols/nomeclature-moc2').glob('*_3D.sdf')}
js+='var sdfs='+json.dumps(sdfs)+';'
js+='var inv=(new Function("var window={};"+'+json.dumps(data)+'+";return Object.keys(window.MOL2D).flatMap(k=>Object.keys(window.MOL2D[k]).filter(m=>window.MOL2D[k][m]).map(m=>[k,m]));"))();var n=0;for(var pair of inv){for(var chain of ["algorithmic","data"]){var args=[pair[0],pair[1],chain,sdfs[pair[0]],null];var a=before.apply(null,args),b=after.apply(null,args);if(JSON.stringify(a)!==JSON.stringify(b))throw Error(JSON.stringify([args,a,b]));n++;}}print(JSON.stringify({rows:rows,regressionCases:n}));'
# Boundary tests for the approved saturated acyclic monoketone scope.
js=js.replace('print(JSON.stringify({rows:rows,regressionCases:n}));','')
guard_source=prefix+'\n'.join(Path(p).read_text() for p in files)+"return fIsAcyclicSaturatedMonoacidGraph(conn,types,bonds);"
js+='var guard=new Function("conn","types","bonds",'+json.dumps(guard_source)+');var guards=[];'
for label,types,edges,expected in [
 ('acid',['C','C','O','O'],[[1,2,1],[1,3,2],[1,4,1]],True),
 ('explicit OH',['C','C','O','O','H'],[[1,2,1],[1,3,2],[1,4,1],[4,5,1]],True),
 ('methanoic',['C','O','O'],[[1,2,2],[1,3,1]],True),
 ('ester',['C','C','O','O','C'],[[1,2,1],[1,3,2],[1,4,1],[4,5,1]],False),
 ('unsaturated acid',['C','C','C','O','O'],[[1,2,1],[2,3,2],[1,4,2],[1,5,1]],False),
 ('cyclic acid',['C','C','C','C','O','O'],[[1,2,1],[2,3,1],[3,4,1],[4,2,1],[1,5,2],[1,6,1]],False),
 ('diacid',['C','C','O','O','O','O'],[[1,2,1],[1,3,2],[1,4,1],[2,5,2],[2,6,1]],False),
 ('hydroxyacid',['C','C','O','O','O'],[[1,2,1],[1,3,2],[1,4,1],[2,5,1]],False),
 ('nitrogen acid',['C','C','O','O','N'],[[1,2,1],[1,3,2],[1,4,1],[2,5,1]],False),
 ('separate oxygens',['C','C','C','O','O'],[[1,2,1],[2,3,1],[1,4,2],[3,5,1]],False),
 ('two single O',['C','C','O','O'],[[1,2,1],[1,3,1],[1,4,1]],False),
 ('ketone',['C','C','C','O'],[[1,2,1],[2,3,1],[2,4,2]],False)
]:
 conn=[[] for _ in types]
 for a,b,o in edges:conn[a-1].append(b-1);conn[b-1].append(a-1)
 js+='var g=guard('+','.join(json.dumps(x)for x in [conn,types,edges])+');if(g!=='+json.dumps(expected)+')throw Error('+json.dumps(label)+');guards.push('+json.dumps(label)+');'
framefn=';uniform2DLibraryFrame=null;return fGetUniform2DLibraryFrame();'
oldframe=prefix+'\n'.join(old_sources[p] for p in files)+framefn
newframe=prefix+'\n'.join(Path(p).read_text() for p in files)+framefn
js+='var oldFrame=(new Function('+json.dumps(oldframe)+'))(),newFrame=(new Function('+json.dumps(newframe)+'))();if(JSON.stringify(oldFrame)!==JSON.stringify(newFrame))throw Error("Legacy React frame changed");'
js+='print(JSON.stringify({rows:rows,regressionCases:n,guardBoundaries:guards,legacyFrameBefore:oldFrame,legacyFrameAfter:newFrame}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr)
result=json.loads(r.stdout);bykey={s['key']:s for s in specs}
for key,mode,chain,row in result['rows']:
 assert row['name']==bykey[key]['name'] and row['series']=='carboxylicAcid',(key,mode,chain,row)
 assert len(row['chain'])==bykey[key]['parent'],(key,row)
 if mode!='permutation':assert row['signature']==row['signature3'],(key,mode,chain,row)
if '--read-only' not in sys.argv:Path('docs/checks/acids-naming-20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(result['rows']),'new naming/ordering cases;',result['regressionCases'],'old library cases unchanged')
