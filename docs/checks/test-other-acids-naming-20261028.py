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
old_sources={p:base64.b64decode(v).decode() for p,v in json.loads(gzip.decompress(Path('docs/checks/other-acids-before-source-20261028.json.gz').read_bytes())).items()}

# Old library comparison does not need 3D parsing.
tail0=tail[:tail.index('if(!probe){fParseSDF3D')]+ret.replace('signature3:probe?null:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)','signature3:null')
before=prefix+'\n'.join(old_sources[p] for p in files)+tail+ret
after=prefix+'\n'.join(Path(p).read_text() for p in files)+tail+ret
js='var run=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(body)+');var rows=[];'
specs=json.load(open('docs/checks/other-acids-specs-20261028.json'))
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
# Original saturated-only guard boundaries remain unchanged.
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
unsat_guard_source=prefix+'\n'.join(Path(p).read_text() for p in files)+"return fIsAcyclicUnsaturatedAcidGraph(conn,types,bonds);"
js+='var ug=new Function("conn","types","bonds",'+json.dumps(unsat_guard_source)+');'
js+='if(ug([[1], [0, 2, 3], [1], [1, 4, 5], [3], [3]],["C", "C", "C", "C", "O", "O"],[[1, 2, 2], [2, 3, 1], [2, 4, 1], [4, 5, 2], [4, 6, 1]])!==true)throw Error("monoacid");guards.push("monoacid");'
js+='if(ug([[1], [0, 2, 3], [1], [1, 4, 5], [3], [3], [], [], [], [], [], []],["C", "C", "C", "C", "O", "O", "H", "H", "H", "H", "H", "H"],[[1, 2, 2], [2, 3, 1], [2, 4, 1], [4, 5, 2], [4, 6, 1], [1, 7, 1], [1, 8, 1], [3, 9, 1], [3, 10, 1], [3, 11, 1], [6, 12, 1]])!==true)throw Error("monoacid explicit H");guards.push("monoacid explicit H");'
js+='if(ug([[1], [0, 2, 3], [1], [1, 4], [3, 5, 6], [4], [4, 7, 8], [6], [6]],["O", "C", "O", "C", "C", "C", "C", "O", "O"],[[1, 2, 2], [2, 3, 1], [2, 4, 1], [4, 5, 2], [5, 6, 1], [5, 7, 1], [7, 8, 2], [7, 9, 1]])!==true)throw Error("diacid");guards.push("diacid");'
js+='if(ug([[1], [0, 2, 3], [1], [1, 4], [3, 5, 6], [4], [4, 7, 8], [6], [6], [], [], [], [], [], []],["O", "C", "O", "C", "C", "C", "C", "O", "O", "H", "H", "H", "H", "H", "H"],[[1, 2, 2], [2, 3, 1], [2, 4, 1], [4, 5, 2], [5, 6, 1], [5, 7, 1], [7, 8, 2], [7, 9, 1], [3, 10, 1], [4, 11, 1], [6, 12, 1], [6, 13, 1], [6, 14, 1], [9, 15, 1]])!==true)throw Error("diacid explicit H");guards.push("diacid explicit H");'
js+='if(ug([[1], [0, 2, 3], [1], [1]],["C", "C", "O", "O"],[[1, 2, 1], [2, 3, 2], [2, 4, 1]])!==false)throw Error("saturated acid");guards.push("saturated acid");'
js+='if(ug([[1], [0, 2, 3], [1], [1], [], [], [], []],["C", "C", "O", "O", "H", "H", "H", "H"],[[1, 2, 1], [2, 3, 2], [2, 4, 1], [1, 5, 1], [1, 6, 1], [1, 7, 1], [4, 8, 1]])!==false)throw Error("saturated acid explicit H");guards.push("saturated acid explicit H");'
js+='if(ug([[1], [0, 2], [1, 3, 4], [2], [2, 5], [4]],["C", "C", "C", "O", "O", "C"],[[1, 2, 2], [2, 3, 1], [3, 4, 2], [3, 5, 1], [5, 6, 1]])!==false)throw Error("ester");guards.push("ester");'
js+='if(ug([[1], [0, 2], [1, 3, 4], [2], [2, 5], [4], [], [], [], [], [], []],["C", "C", "C", "O", "O", "C", "H", "H", "H", "H", "H", "H"],[[1, 2, 2], [2, 3, 1], [3, 4, 2], [3, 5, 1], [5, 6, 1], [1, 7, 1], [1, 8, 1], [2, 9, 1], [6, 10, 1], [6, 11, 1], [6, 12, 1]])!==false)throw Error("ester explicit H");guards.push("ester explicit H");'
js+='if(ug([[1], [0, 2, 4], [1, 3], [2], [1, 5, 6], [4], [4]],["O", "C", "C", "C", "C", "O", "O"],[[1, 2, 1], [2, 3, 1], [3, 4, 2], [2, 5, 1], [5, 6, 2], [5, 7, 1]])!==false)throw Error("hydroxyacid");guards.push("hydroxyacid");'
js+='if(ug([[1], [0, 2, 4], [1, 3], [2], [1, 5, 6], [4], [4], [], [], [], [], [], []],["O", "C", "C", "C", "C", "O", "O", "H", "H", "H", "H", "H", "H"],[[1, 2, 1], [2, 3, 1], [3, 4, 2], [2, 5, 1], [5, 6, 2], [5, 7, 1], [1, 8, 1], [2, 9, 1], [3, 10, 1], [4, 11, 1], [4, 12, 1], [7, 13, 1]])!==false)throw Error("hydroxyacid explicit H");guards.push("hydroxyacid explicit H");'
js+='if(ug([[1], [0, 2, 3], [1], [1, 4], [3, 5], [4, 6, 7], [5], [5]],["C", "C", "O", "C", "C", "C", "O", "O"],[[1, 2, 1], [2, 3, 2], [2, 4, 1], [4, 5, 2], [5, 6, 1], [6, 7, 2], [6, 8, 1]])!==false)throw Error("ketoacid");guards.push("ketoacid");'
js+='if(ug([[1], [0, 2, 3], [1], [1, 4], [3, 5], [4, 6, 7], [5], [5], [], [], [], [], [], []],["C", "C", "O", "C", "C", "C", "O", "O", "H", "H", "H", "H", "H", "H"],[[1, 2, 1], [2, 3, 2], [2, 4, 1], [4, 5, 2], [5, 6, 1], [6, 7, 2], [6, 8, 1], [1, 9, 1], [1, 10, 1], [1, 11, 1], [4, 12, 1], [5, 13, 1], [8, 14, 1]])!==false)throw Error("ketoacid explicit H");guards.push("ketoacid explicit H");'
js+='if(ug([[1], [0, 2, 3], [1], [1, 4, 8], [3, 5], [4, 6], [5, 7], [6, 8], [7, 3]],["O", "C", "O", "C", "C", "C", "C", "C", "C"],[[1, 2, 2], [2, 3, 1], [2, 4, 1], [4, 5, 2], [5, 6, 1], [6, 7, 1], [7, 8, 1], [8, 9, 1], [9, 4, 1]])!==false)throw Error("cyclic acid");guards.push("cyclic acid");'
js+='if(ug([[1], [0, 2, 3], [1], [1, 4, 8], [3, 5], [4, 6], [5, 7], [6, 8], [7, 3], [], [], [], [], [], [], [], [], [], []],["O", "C", "O", "C", "C", "C", "C", "C", "C", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],[[1, 2, 2], [2, 3, 1], [2, 4, 1], [4, 5, 2], [5, 6, 1], [6, 7, 1], [7, 8, 1], [8, 9, 1], [9, 4, 1], [3, 10, 1], [5, 11, 1], [6, 12, 1], [6, 13, 1], [7, 14, 1], [7, 15, 1], [8, 16, 1], [8, 17, 1], [9, 18, 1], [9, 19, 1]])!==false)throw Error("cyclic acid explicit H");guards.push("cyclic acid explicit H");'
js+='if(ug([[1], [0, 2], [1, 3], [2, 4], [3, 5, 6], [4], [4]],["N", "C", "C", "C", "C", "O", "O"],[[1, 2, 1], [2, 3, 1], [3, 4, 2], [4, 5, 1], [5, 6, 2], [5, 7, 1]])!==false)throw Error("nitrogen acid");guards.push("nitrogen acid");'
js+='if(ug([[1], [0, 2], [1, 3], [2, 4], [3, 5, 6], [4], [4], [], [], [], [], [], [], []],["N", "C", "C", "C", "C", "O", "O", "H", "H", "H", "H", "H", "H", "H"],[[1, 2, 1], [2, 3, 1], [3, 4, 2], [4, 5, 1], [5, 6, 2], [5, 7, 1], [1, 8, 1], [1, 9, 1], [2, 10, 1], [2, 11, 1], [3, 12, 1], [4, 13, 1], [7, 14, 1]])!==false)throw Error("nitrogen acid explicit H");guards.push("nitrogen acid explicit H");'
unsupported_body=body.replace("return {name:currentMolName", "return {supported:fSupportsAlkylBranchPrefixes(),name:currentMolName")
js+='var unsupportedRun=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(unsupported_body)+');var unsupported=unsupportedRun('+','.join(json.dumps(x) for x in ['methyl_2_propenoic_acid', 'condensed', 'algorithmic', '', {'types': ['O', 'C', 'O', 'C', 'C', 'C', 'C', 'C'], 'edges': [[1, 2, 2], [2, 3, 1], [2, 4, 1], [4, 5, 1], [5, 6, 2], [4, 7, 1], [7, 8, 2]]}])+');if(unsupported.supported||unsupported.name.includes("αιθυλο"))throw Error("False vinyl-as-ethyl support");guards.push("vinyl sidebranch unsupported");'
framefn=';uniform2DLibraryFrame=null;return fGetUniform2DLibraryFrame();'
oldframe=prefix+'\n'.join(old_sources[p] for p in files)+framefn
# Saved React inventory is unchanged; additions change Main inventory only.
newframe=prefix+'\n'.join(old_sources[p] if p==files[0] else Path(p).read_text() for p in files)+framefn
js+='var oldFrame=(new Function('+json.dumps(oldframe)+'))(),newFrame=(new Function('+json.dumps(newframe)+'))();if(JSON.stringify(oldFrame)!==JSON.stringify(newFrame))throw Error("Legacy React frame changed");'
js+='print(JSON.stringify({rows:rows,regressionCases:n,guardBoundaries:guards,legacyFrameBefore:oldFrame,legacyFrameAfter:newFrame}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr)
result=json.loads(r.stdout);bykey={s['key']:s for s in specs}
for key,mode,chain,row in result['rows']:
 assert row['name']==bykey[key]['name'] and row['series']=='carboxylicAcid',(key,mode,chain,row)
 assert len(row['chain'])==bykey[key]['parent'],(key,row)
 if mode!='permutation':assert row['signature']==row['signature3'],(key,mode,chain,row)
if '--read-only' not in sys.argv:Path('docs/checks/other-acids-naming-20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(result['rows']),'new naming/ordering cases;',result['regressionCases'],'old library cases unchanged')
