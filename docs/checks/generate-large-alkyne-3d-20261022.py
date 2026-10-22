from pathlib import Path
import json,math,sys,hashlib
from rdkit import Chem,rdBase
from rdkit.Chem import AllChem,rdMolDescriptors,rdMolTransforms
key='ethyl_4_dimethyl_3_5_heptyne_1';folder=Path(sys.argv[1]) if len(sys.argv)>1 else Path('mols/new_molecules')
m=Chem.MolFromMolFile(str(folder/(key+'_2D_Condensed.mol')),sanitize=True,removeHs=False)
assert m is not None and m.GetNumAtoms()==11 and rdMolDescriptors.CalcMolFormula(m)=='C11H20'
expected=Chem.MolFromSmiles('C#CC(C)C(CC)C(C)CC')
assert Chem.MolToSmiles(m)==Chem.MolToSmiles(expected)
m=Chem.AddHs(m);assert m.GetNumAtoms()==31 and AllChem.MMFFHasAllMoleculeParams(m)
p=AllChem.ETKDGv3();p.randomSeed=20261022;p.numThreads=1;p.pruneRmsThresh=.25
ids=list(AllChem.EmbedMultipleConfs(m,numConfs=24,params=p));assert ids
results=AllChem.MMFFOptimizeMoleculeConfs(m,numThreads=1,maxIters=1000,mmffVariant='MMFF94s')
ok=[(energy,cid) for cid,(status,energy) in zip(ids,results) if status==0 and math.isfinite(energy)];assert ok
energy,cid=min(ok);conf=m.GetConformer(cid)
angle=rdMolTransforms.GetAngleDeg(conf,0,1,2);assert angle>175
assert all(math.isfinite(v) for pt in conf.GetPositions() for v in pt)
for b in m.GetBonds():
 d=rdMolTransforms.GetBondLength(conf,b.GetBeginAtomIdx(),b.GetEndAtomIdx());assert .8<d<1.8
Chem.RemoveStereochemistry(m)
block=Chem.MolToMolBlock(m,includeStereo=False,confId=cid)
block=key+'\n'+block.split('\n',1)[1]
props={'NAMELECULE_SOURCE':'Locally generated with RDKit; not a PubChem download','NAMELECULE_RDKIT_VERSION':rdBase.rdkitVersion,'NAMELECULE_METHOD':'ETKDGv3 with explicit H; MMFF94s optimization; lowest energy among converged sampled conformers','NAMELECULE_RANDOM_SEED':'20261022','NAMELECULE_INPUT_SMILES':Chem.MolToSmiles(Chem.RemoveHs(m)),'NAMELECULE_STEREOCHEMISTRY':'Not specified by the lesson; one illustrative 3D configuration, no R/S assignment','NAMELECULE_MMFF_ENERGY':str(energy),'NAMELECULE_TESTED_CONFORMERS':str(len(ids))}
sdf=block+'\n'+''.join('> <'+k+'>\n'+v+'\n\n' for k,v in props.items())+'$$$$\n'
(folder/(key+'_3D.sdf')).write_text(sdf)
report={'rdkitVersion':rdBase.rdkitVersion,'seed':20261022,'conformersGenerated':len(ids),'converged':len(ok),'selectedConformerId':cid,'mmff94sEnergy':energy,'spAngleDegrees':angle,'formula':rdMolDescriptors.CalcMolFormula(m),'smiles':props['NAMELECULE_INPUT_SMILES'],'source':'locally generated, no PubChem CID','mainChain3D':[1,2,3,4,5,6,7]}
report.update(inputMolSha256=hashlib.sha256((folder/(key+'_2D_Condensed.mol')).read_bytes()).hexdigest(),sdfSha256=hashlib.sha256((folder/(key+'_3D.sdf')).read_bytes()).hexdigest(),pubchemLookup={'nameQuery':'not found','smilesQueryCID':0,'threeDimensionalQuery':'Cannot generate3Dcoordinates without existingCID'})
(folder/(key+'_3D.provenance.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
