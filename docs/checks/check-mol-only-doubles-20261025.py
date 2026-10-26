"""Read-only verification of the approved MOL-only double-bond migration.
Baseline is the task snapshot in /tmp/mol-files-only-baseline; no RDKit needed.
"""
from pathlib import Path
import json,re,hashlib,ast,subprocess
base=Path('/tmp/mol-files-only-baseline')
inventory=json.loads((base/'inventory.json').read_text());changed=[];formulas=[]
data=Path('js/jsme-nick-nomeclature-moc2-data_50.js').read_text()
def formula(lines):
 n=int(lines[3][:3]);nb=int(lines[3][3:6]);atoms=[l[31:34].strip() for l in lines[4:4+n]];val=[0]*n
 for l in lines[4+n:4+n+nb]:
  a,b,o=int(l[:3])-1,int(l[3:6])-1,int(l[6:9]);val[a]+=o;val[b]+=o
 counts={e:atoms.count(e) for e in ['C','H','O']}
 for e,v in zip(atoms,val):
  assert e in ['C','H','O'] and v<={'C':4,'H':1,'O':2}[e]
  if e!='H':counts['H']+={'C':4,'O':2}[e]-v
 return counts
for row in inventory:
 p=Path(row['file']);old=(base/p).read_text();new=p.read_text();a=old.splitlines();b=new.splitlines();assert len(a)==len(b)
 for i,(x,y) in enumerate(zip(a,b)):
  if x!=y:assert x[:9]==y[:9] and x[12:]==y[12:] and x[6:9]=='  2' and x[9:12]=='  3' and y[9:12]=='  0',(p,i)
 assert formula(a)==formula(b)
 match=re.search(r'(?:const|let|var) '+re.escape(p.stem)+r' = ("(?:[^"\\]|\\.)*");',data);assert match and json.loads(match[1])==new,p
 formulas.append({'file':str(p),'counts':formula(b)})
 if old!=new:changed.append(str(p))
assert len(changed)==12
allowed=set(changed)|{'js/jsme-nick-nomeclature-moc2-data_50.js','js/mulermoc-nom-molview-50.js'}
protected=0
for file,h in json.loads((base/'hashes.json').read_text()).items():
 if file not in allowed:assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h,file;protected+=1
viewer=Path('js/mulermoc-nom-molview-50.js').read_text();assert 'fDrawDieneParallelDoubleBonds' not in viewer
for p in ['docs/checks/generate-dienes-20261024.py','docs/checks/generate-other-alcohols-20261025.py']:ast.parse(Path(p).read_text())
# Generator block routines can be exercised without importing RDKit or producing files.
class FakeChem:
 class StereoType:Bond_Double=1
 class BondStereo:STEREOANY=3
 @staticmethod
 def Mol(m):return m
 @staticmethod
 def FindPotentialStereo(m):return []
 @staticmethod
 def MolToMolBlock(m,**kwargs):return m
for generator,keys in [('generate-dienes-20261024.py',[Path(x['file']).name.split('_2D_')[0] for x in inventory[:18]]),('generate-other-alcohols-20261025.py',['ethyl_3_methyl_4_hexen_3_yn_5_ol_2'])]:
 tree=ast.parse(Path('docs/checks',generator).read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='block');ns={'Chem':FakeChem};exec(compile(ast.Module(body=[fn],type_ignores=[]),generator,'exec'),ns)
 for row in inventory:
  key=Path(row['file']).name.split('_2D_')[0]
  if key not in keys:continue
  original=(base/row['file']).read_text();out=ns['block'](original,Path(row['file']).stem);ls=out.splitlines();n=int(ls[3][:3]);nb=int(ls[3][3:6]);assert all(not(int(l[6:9])==2 and int(l[9:12])==3) for l in ls[4+n:4+n+nb])
 # A 3D serialization title must not trigger the 2D field normalization.
 if generator.startswith('generate-dienes'):
  raw=(base/inventory[9]['file']).read_text();out=ns['block'](raw,'methyl_3_pentadiene_1_3')
  assert out.splitlines()[1:]==raw.splitlines()[1:]
print(json.dumps({'changedMOLs':changed,'protectedUnchangedFiles':protected,'formulas':formulas,'generatorSerializationChecks':'PASS','helperAbsent':True},ensure_ascii=False,indent=2))
