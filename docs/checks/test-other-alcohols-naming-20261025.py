"""Actual core/viewer naming and independent atom-order probes, no repo writes."""
from pathlib import Path
import argparse,json,subprocess,random,tempfile
from rdkit import Chem
parser=argparse.ArgumentParser();parser.add_argument('--folder',type=Path,default=Path('mols/new_molecules'));args=parser.parse_args()
specs=json.loads(Path('docs/checks/other-alcohols-specs-20261025.json').read_text())
ns={};exec(Path('docs/checks/test-alcohols-naming-20261024.py').read_text().split("js='var run")[0],ns)
body=ns['body'].replace('var MOL2D=window.MOL2D;selectedMol=key;','window.MOL2D[key]={[mode]:mol};nameExamples[key]=meta;var MOL2D=window.MOL2D;selectedMol=key;')
body=body.replace('groups:[fGetHydrocarbonBranchGroup(1),fGetHydrocarbonBranchGroup(2)]','groups:[fGetHydrocarbonBranchGroup(1),fGetHydrocarbonBranchGroup(2)],ohComponent:fAlcoholOHNameComponent()')
code='var run=new Function("key","mode","chainMode","sdf","probe","mol","meta",'+json.dumps(body)+');var rows=[];'
for spec in specs:
 key=spec['key'];provenance=json.loads((args.folder/(key+'_3D.provenance.json')).read_text());sdf=(args.folder/(key+'_3D.sdf')).read_text()
 meta={'mainChain_'+f:list(range(1,spec['parent']+1)) for f in ['Condensed','Expanded','Skeletal']};meta['mainChain3D']=provenance['mainChain3D']
 for mode in ['condensed','expanded','skeletal']:
  mol=(args.folder/(key+'_2D_'+mode.title()+'.mol')).read_text()
  for chain in ['algorithmic','data']:
   call=[key,mode,chain,sdf,None,mol,meta]
   code+='rows.push('+json.dumps([key,spec['name'],mode,chain])+'.concat([run('+','.join(json.dumps(v) for v in call)+')]));'
 rng=random.Random(20261025)
 for trial in range(16):
  m=Chem.MolFromMolFile(str(args.folder/(key+'_2D_Condensed.mol')),removeHs=False);order=list(range(m.GetNumAtoms()));rng.shuffle(order);m=Chem.RenumberAtoms(m,order)
  call=[key,'condensed','algorithmic',sdf,None,Chem.MolToMolBlock(m),meta]
  code+='rows.push('+json.dumps([key,spec['name'],'permutation','algorithmic'])+'.concat([run('+','.join(json.dumps(v) for v in call)+')]));'
code+='print(JSON.stringify(rows));'
with tempfile.TemporaryDirectory(prefix='namelecule-other-alcohols-') as folder:
 js=Path(folder)/'naming.js';js.write_text(code)
 r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',str(js)],capture_output=True,text=True)
assert r.returncode==0,(r.stdout,r.stderr)
rows=json.loads(r.stdout)
for key,name,mode,chain,result in rows:
 assert result['name']==name,(key,mode,chain,result)
 assert result['signature']==result['signature3'],(key,mode,chain,result)
 assert result['groups'][0] is not None,(key,result)
print(json.dumps({'cases':len(rows),'results':rows,'failures':[]},ensure_ascii=False,indent=2))
