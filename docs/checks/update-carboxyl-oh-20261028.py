"""Approved MOL-only Expanded carboxyl OH update. --apply writes only affected embeds/sources.
Preserves existing atom IDs/coordinates except O-bound H; appends previously implicit H.
"""
from pathlib import Path
import json,subprocess,math,statistics,re,argparse
NODE='/tmp/namelecule-react-tools/node-v24.22.1-darwin-x64/bin/node'
DATA=Path('js/jsme-nick-nomeclature-moc2-data_52.js')
def inventory():
 js="const fs=require('fs');const o=new Function('var window={};'+fs.readFileSync('js/jsme-nick-nomeclature-moc2-data_52.js','utf8')+';return window.MOL2D;')();process.stdout.write(JSON.stringify(o));"
 return json.loads(subprocess.check_output([NODE,'-e',js],text=True))
def parse(text):
 ls=text.splitlines();n=int(ls[3][:3]);nb=int(ls[3][3:6]);atoms=ls[4:4+n];bonds=ls[4+n:4+n+nb]
 types=[a[31:34].strip() for a in atoms];xyz=[tuple(float(a[i:i+10])for i in [0,10,20])for a in atoms]
 edges=[(int(b[:3])-1,int(b[3:6])-1,int(b[6:9]))for b in bonds];conn=[[] for _ in atoms]
 for a,b,o in edges:conn[a].append((b,o));conn[b].append((a,o))
 groups=[]
 for c,t in enumerate(types):
  os=[(a,o)for a,o in conn[c] if types[a]=='O']
  if t!='C' or len(os)!=2 or sorted(o for a,o in os)!=[1,2]:continue
  oh=next(a for a,o in os if o==1)
  if any(types[a]not in ['H','[H]']and a!=c for a,o in conn[oh]):continue
  hs=[a for a,o in conn[oh]if types[a]in ['H','[H]']];assert len(hs)<=1
  groups.append((c,oh,hs))
 return ls,n,nb,atoms,bonds,types,xyz,edges,groups

def update(text):
 ls,n,nb,atoms,bonds,types,xyz,edges,groups=parse(text)
 if not groups:return text,[]
 lengths=[math.dist(xyz[a],xyz[b])for a,b,o in edges if types[a]in ['H','[H]']or types[b]in ['H','[H]']]
 unit=statistics.median(lengths);newatoms=list(atoms);newbonds=list(bonds);rows=[]
 for c,o,hs in groups:
  ox,oy,oz=xyz[o]
  dx=ox-xyz[c][0]
  if abs(dx)<.0001:
   # At vertical C–O, point away from the carbon framework. Each end of a
   # diacid therefore has its own outward direction; never default both right.
   cs=[b if a==c else a for a,b,q in edges if (a==c and types[b]=='C')or(b==c and types[a]=='C')]
   dx=-sum(xyz[i][0]-xyz[c][0]for i in cs)
  sign=-1 if dx<0 else 1;pos=(ox+sign*unit,oy,oz)
  if hs:
   h=hs[0];newatoms[h]=''.join(f'{v:10.4f}'for v in pos)+atoms[h][30:]
  else:
   h=len(newatoms);newatoms.append(''.join(f'{v:10.4f}'for v in pos)+' H   0  0  0  0  0  0  0  0  0  0  0  0');newbonds.append(f'{o+1:3d}{h+1:3d}  1  0')
  rows.append(dict(carbon=c+1,oxygen=o+1,hydrogen=h+1,added=not hs,length=unit,direction=sign))
 counts=f'{len(newatoms):3d}{len(newbonds):3d}'+ls[3][6:]
 out='\n'.join(ls[:3]+[counts]+newatoms+newbonds+ls[4+n+nb:])+('\n' if text.endswith('\n')else '')
 return out,rows

def run(apply=False):
 source=DATA.read_text();rows=[]
 for key,forms in inventory().items():
  old=forms.get('expanded')
  if not old:continue
  new,groups=update(old)
  if not groups:continue
  rows.append(dict(key=key,groups=groups))
  if new==old:continue
  var=key+'_2D_Expanded'
  pattern=r'(let\s+'+re.escape(var)+r'\s*=\s*)(?:"(?:\\.|[^"\\])*"(?:\s*\+\s*"(?:\\.|[^"\\])*")*)\s*;'
  source,count=re.subn(pattern,lambda m:m[1]+json.dumps(new,ensure_ascii=False)+';',source);assert count==1,(key,count)
  path=Path('mols/new_molecules',var+'.mol')
  if path.exists():
   assert path.read_text()==old,(key,'source/embed mismatch')
   if apply:path.write_text(new)
 if apply:DATA.write_text(source)
 return rows
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
 print(json.dumps(run(args.apply),ensure_ascii=False,indent=2))
