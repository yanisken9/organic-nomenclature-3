"""Actual core/viewer: new ether names, components, parent and full group mappings.
Also compare every old 2D form in both chain modes to the pre-task snapshot.
No dependencies beyond Python/JavaScriptCore; writes evidence under /tmp only.
"""
from pathlib import Path
import json,subprocess,random
specs=json.loads(Path('docs/checks/ethers-specs-20261026.json').read_text())
ns={};exec(Path('docs/checks/test-alcohols-naming-20261024.py').read_text().split("js='var run")[0],ns)
tail=ns['body'][ns['body'].index('var MOL2D=window.MOL2D;'):ns['body'].index('return {name:currentMolName')]
prefix='var window={},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};'
files=['js/jsme-nick-nomeclature-moc2-data_51.js','js/mulermoc-nom-core-51.js','js/mulermoc-nom-molview-51.js']
ret='''nameExamples[selectedMol]=nameExamples[selectedMol]||{};nameExamples[selectedMol].classification=fGetMoleculeClassification();
return {name:currentMolName,common:currentMolCommonName,parts:nameComponentsList,
chain:mainChainAtomsList,chain3:mainChainAtoms3D,ether:etherInfo,
commonParts:probe?null:fGetEtherCommonParts(),prefixes:fEtherPrefixGroups(),
signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList),
signature3:probe?null:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D),
branches:[fGetHydrocarbonBranchGroup(1),fGetHydrocarbonBranchGroup(2)],
branchAtoms:[fGetHydrocarbonBranchHighlight(1),fGetHydrocarbonBranchHighlight(2)],
branchAtoms3:[fGetHydrocarbonBranchHighlight3D(1),fGetHydrocarbonBranchHighlight3D(2)]};'''
body=prefix+'\n'.join(Path(p).read_text() for p in files)+tail+ret
js='var run=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(body)+');var rows=[];'
for s in specs:
 for mode in ['condensed','expanded','skeletal']:
  for chain in ['algorithmic','data']:
   args=[s['key'],mode,chain,Path('mols/nomeclature-moc2',s['key']+'_3D.sdf').read_text(),None]
   js+='rows.push('+json.dumps([s['key'],mode,chain])+'.concat([run('+','.join(json.dumps(a) for a in args)+')]));'
 rng=random.Random(20261026)
 for i in range(32):
  order=list(range(s['carbons']+1));rng.shuffle(order);mapping={old:new+1 for new,old in enumerate(order)}
  probe=dict(types=['C' if old<s['carbons'] else 'O' for old in order],edges=[[mapping[a-1],mapping[b-1]] for a,b in s['edges']]);rng.shuffle(probe['edges'])
  args=[s['key'],'condensed','algorithmic','',probe]
  js+='rows.push('+json.dumps([s['key'],'permutation',i])+'.concat([run('+','.join(json.dumps(a) for a in args)+')]));'
js+='print(JSON.stringify(rows));'
def jsc(code):
 r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr);return json.loads(r.stdout)
rows=jsc(js);bykey={s['key']:s for s in specs}
for key,mode,chain,result in rows:
 s=bykey[key];assert result['name']==s['name'],(key,mode,chain,result)
 assert result['common']==s['common'],(key,mode,result['common'])
 assert len(result['chain'])==s['parent'],(key,mode,result)
 if mode!='permutation':
  assert result['signature']==result['signature3'],(key,mode,chain,'2D3D parent',result)
  parts=result['commonParts']['parts'];assert sum(len(p['chain']) for p in parts if p['kind']=='alkyl')==s['carbons']
  assert sum(len(p['chain3D']) for p in parts if p['kind']=='alkyl')==s['carbons']
  assert len(set(a for p in parts if p['kind']=='alkyl' for a in p['chain']))==s['carbons']
  assert len(set(a for p in parts if p['kind']=='alkyl' for a in p['chain3D']))==s['carbons']
  if 'isobutyl' in key or 'tert_butyl' in key:
   assert result['branches'][0] is None and len(result['branches'][1]['members'])==1
   assert len(result['branchAtoms'][1]['atoms'])==(4 if mode=='expanded' else 1)
   assert len(result['branchAtoms3'][1]['atoms'])==1,(key,mode,chain,result['branchAtoms3'])
# Old common labels, metadata, MOL, name components and chains must remain exact.
base=Path('/tmp/namelecule-before-ethers-20261026')
shorttail=tail[:tail.index('if(!probe){fParseSDF3D')]+'return {name:currentMolName,common:currentMolCommonName,parts:nameComponentsList,chain:mainChainAtomsList};'
funcs=[prefix+'\n'.join((root/p).read_text() for p in files)+shorttail for root in [base,Path('.')]]
code='var before=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(funcs[0])+'),after=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(funcs[1])+');'
code+='var inv=(new Function("var window={};"+'+json.dumps((base/files[0]).read_text())+'+";return Object.keys(window.MOL2D).flatMap(k=>Object.keys(window.MOL2D[k]).filter(m=>window.MOL2D[k][m]).map(m=>[k,m]));"))();var n=0;for(var p of inv)for(var chain of ["algorithmic","data"]){var args=[p[0],p[1],chain,"",null],a=before.apply(null,args),b=after.apply(null,args);if(JSON.stringify(a)!==JSON.stringify(b))throw Error(JSON.stringify([args,a,b]));n++;}print(JSON.stringify(n));'
old=jsc(code)
# Compare the complete original registry metadata and every embedded MOL byte.
fetch=';return {metadata:nameExamples,mols:window.MOL2D};'
olddata=jsc('print(JSON.stringify((new Function("var window={};"+'+json.dumps((base/files[0]).read_text())+'+'+json.dumps(fetch)+'))()));')
newdata=jsc('print(JSON.stringify((new Function("var window={};"+'+json.dumps(Path(files[0]).read_text())+'+'+json.dumps(fetch)+'))()));')
assert len(olddata['metadata'])==98 and len(newdata['metadata'])==105
for key in olddata['metadata']:
 assert olddata['metadata'][key]==newdata['metadata'][key],('old metadata',key)
 assert olddata['mols'].get(key)==newdata['mols'].get(key),('old MOL',key)

Path('/tmp/ethers-naming-20261026.json').write_text(json.dumps(dict(newCases=len(rows),formChainCases=42,permutations=224,oldCases=old,rows=rows),ensure_ascii=False,indent=2))
print('PASS',len(rows),'new name/common/parent/group cases;',old,'old cases unchanged')
