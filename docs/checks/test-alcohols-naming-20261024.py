"""Actual core/viewer JS, four names x3forms x2chain modes and atom-order probes."""
from pathlib import Path
import json,subprocess,random
specs=json.loads(Path('docs/checks/alcohols-specs-20261024.json').read_text())
sources='\n'.join(Path(p).read_text() for p in ['js/jsme-nick-nomeclature-moc2-data_50.js','js/mulermoc-nom-core-50.js','js/mulermoc-nom-molview-50.js'])
body="var window={},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};"+sources+r'''
var MOL2D=window.MOL2D;selectedMol=key;mode2D=mode;mainChainMode=chainMode;
var text=MOL2D[key][mode],ls=text.split('\n'),na=Number(ls[3].slice(0,3)),nb=Number(ls[3].slice(3,6));
var aa=ls.slice(4,4+na).map(l=>({label:l.slice(31,34).trim()})),bb=ls.slice(4+na,4+na+nb).map(l=>({atoms:[Number(l.slice(0,3)),Number(l.slice(3,6))],order:Number(l.slice(6,9))}));
if(probe){aa=probe.types.map(label=>({label}));bb=probe.edges.map(atoms=>({atoms,order:1}));na=aa.length;nb=bb.length;selectedMol='__permuted_probe';mainChainMode='algorithmic';}
jsmeNomeclatureApplet={totalNumberOfAtoms:()=>na,totalNumberOfBonds:()=>nb,getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1],molFile:()=>probe?'':text};
fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();
if(!probe){fParseSDF3D(sdf);fDetectMolType3D();fCalcMainChain3D();}
return {name:currentMolName,parts:nameComponentsList,series:fGetMoleculeClassification().seriesKey,chain:mainChainAtomsList,chain3:mainChainAtoms3D,signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList),signature3:probe?null:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D),groups:[fGetHydrocarbonBranchGroup(1),fGetHydrocarbonBranchGroup(2)]};
'''
js='var run=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(body)+');var rows=[];'
for s in specs:
 for mode in ['condensed','expanded','skeletal']:
  for chain in ['algorithmic','data']:
   args=[s['key'],mode,chain,Path('mols/nomeclature-moc2',s['key']+'_3D.sdf').read_text(),None]
   js+='rows.push('+json.dumps([s['key'],s['name'],s['parent'],mode,chain])+'.concat([run('+','.join(json.dumps(x) for x in args)+')]));'
 rng=random.Random(20261024)
 for i in range(32):
  n=s['carbons']+1;order=list(range(n));rng.shuffle(order);mapping={old:new+1 for new,old in enumerate(order)}
  probe={'types':[('C' if old<s['carbons'] else 'O') for old in order],'edges':[[mapping[a-1],mapping[b-1]] for a,b in s['edges']]};rng.shuffle(probe['edges'])
  args=[s['key'],'condensed','algorithmic','',probe]
  js+='rows.push('+json.dumps([s['key'],s['name'],s['parent'],'permutation',i])+'.concat([run('+','.join(json.dumps(x) for x in args)+')]));'
js+='print(JSON.stringify(rows));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e',js],capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
rows=json.loads(r.stdout)
for key,name,n,mode,chain,result in rows:
 assert result['name']==name,(key,mode,chain,result)
 assert len(result['chain'])==n and result['series']=='alcohol',(key,result)
 if mode!='permutation':assert result['signature']==result['signature3'],(key,mode,chain,result)
print(json.dumps({'cases':len(rows),'formChainCases':24,'atomOrderCases':128,'results':rows,'failures':[]},ensure_ascii=False,indent=2))
