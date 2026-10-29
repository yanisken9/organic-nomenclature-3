"""Approved Expanded COOH orientation and six direct methyl stems; MOL-only update.
--apply writes data52 / existing Expanded source MOLs / four-acid coordinate specs.
"""
from pathlib import Path
import json,subprocess,math,re,runpy,argparse
ns=runpy.run_path('docs/checks/update-carboxyl-oh-20261028.py')
def run(apply=False):
 source=ns['DATA'].read_text();rows=[]
 js="const fs=require('fs');const r=new Function('var window={};'+fs.readFileSync('js/jsme-nick-nomeclature-moc2-data_52.js','utf8')+';return nameExamples;')();process.stdout.write(JSON.stringify(r));"
 examples=json.loads(subprocess.check_output([ns['NODE'],'-e',js],text=True));specfile=Path('docs/checks/acids-specs-20261028.json');specs=json.loads(specfile.read_text());bykey={s['key']:s for s in specs}
 for key,forms in ns['inventory']().items():
  old=forms.get('expanded')
  if not old:continue
  ls,n,nb,atoms,bonds,types,xy,edges,groups=ns['parse'](old)
  if not groups:continue
  xyz=[list(p)for p in xy];main={i-1 for i in examples[key]['mainChain_Expanded']};methyls=[]
  for c,o,hs in groups:
   assert len(hs)==1
   carbonyl=next(b if a==c else a for a,b,q in edges if q==2 and ((a==c and types[b]=='O')or(b==c and types[a]=='O')))
   cs=[b if a==c else a for a,b,q in edges if (a==c and types[b]=='C')or(b==c and types[a]=='C')]
   dx=-sum(xy[i][0]-xy[c][0]for i in cs);sign=-1 if dx<0 else 1
   if not cs:sign=-1 if xy[o][0]<xy[c][0]else 1
   d=math.dist(xy[c],xy[carbonyl]);oh=math.dist(xy[c],xy[o]);hh=math.dist(xy[o],xy[hs[0]])
   direction=-1 if abs(xy[carbonyl][0]-xy[c][0])<.0001 and xy[carbonyl][1]<xy[c][1]else 1
   xyz[carbonyl]=[xy[c][0],xy[c][1]+direction*d,xy[c][2]]
   xyz[o]=[xy[c][0]+sign*oh,xy[c][1],xy[c][2]]
   xyz[hs[0]]=[xyz[o][0]+sign*hh,xyz[o][1],xyz[o][2]]
  for c,t in enumerate(types):
   if t!='C'or c in main:continue
   es=[b if a==c else a for a,b,q in edges if a==c or b==c];cs=[b for b in es if types[b]=='C'];hs=[b for b in es if types[b]=='H']
   if len(cs)!=1 or cs[0]not in main or len(hs)!=3 or abs(xy[c][0]-xy[cs[0]][0])>.0001:continue
   # Only the six approved direct methyl stems of the four new acids.
   if key not in bykey:continue
   parent=cs[0];sign=1 if xy[c][1]>xy[parent][1]else -1;delta=xy[parent][1]+sign*1.755-xy[c][1]
   for i in [c]+hs:xyz[i][1]+=delta
   bykey[key]['xy'][c][1]=sign*1.5
   methyls.append(dict(carbon=c+1,parent=parent+1,length=1.755))
  newatoms=[(''.join(f'{v:10.4f}'for v in xyz[i])+line[30:])if any(abs(xyz[i][j]-xy[i][j])>.00001 for j in range(3))else line for i,line in enumerate(atoms)]
  new='\n'.join(ls[:4]+newatoms+ls[4+n:])+('\n'if old.endswith('\n')else'')
  if new!=old:
   var=key+'_2D_Expanded';pat=r'(let\s+'+re.escape(var)+r'\s*=\s*)(?:"(?:\\.|[^"\\])*"(?:\s*\+\s*"(?:\\.|[^"\\])*")*)\s*;'
   source,count=re.subn(pat,lambda m:m[1]+json.dumps(new,ensure_ascii=False)+';',source);assert count==1
   path=Path('mols/new_molecules',var+'.mol')
   if path.exists():
    assert path.read_text()==old
    if apply:path.write_text(new)
  rows.append(dict(key=key,changed=new!=old,groups=len(groups),methyls=methyls))
 if apply:ns['DATA'].write_text(source);specfile.write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n')
 return rows
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');args=p.parse_args();print(json.dumps(run(args.apply),ensure_ascii=False,indent=2))
