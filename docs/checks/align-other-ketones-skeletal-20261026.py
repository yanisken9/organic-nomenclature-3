"""Approved visual axes: vertical carbonyls and regular skeletal zigzag.

Rigidly rotate all atoms together, preserving orientation (no reflection),
about the numbered-parent centroid. No coordinate rewrite below0.02degrees.
--source permits exact reproduction from a saved baseline; refuses overwrite.
"""
from pathlib import Path
import argparse,json,math,runpy
extract=runpy.run_path('docs/checks/orient-other-ketones-skeletal-20261026.py')['extract']
TARGETS=['pentyn_4_one_2','penten_1_yn_4_one_3','dimethyl_4_5_hexen_5_yn_1_one_3','ethyl_3_methyl_4_octen_3_yn_5_dione_2_7','isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5']
def corrections(lines):
 n=int(lines[3][:3]);nb=int(lines[3][3:6]);xy=[(float(l[:10]),float(l[10:20]))for l in lines[4:4+n]];elements=[l[31:34].strip()for l in lines[4:4+n]];out=[]
 for l in lines[4+n:4+n+nb]:
  a,b,o=int(l[:3])-1,int(l[3:6])-1,int(l[6:9])
  if o!=2 or {elements[a],elements[b]}!={'C','O'}:continue
  if elements[a]=='O':a,b=b,a
  dx,dy=xy[b][0]-xy[a][0],xy[b][1]-xy[a][1]
  theta=math.degrees(math.atan2(dy,dx))
  out.append((180-theta)%180-90) # nearest vertical axis, retaining up/down.
 assert out and max(out)-min(out)<.05,('carbonyls not parallel',out)
 return out

def rotate(item):
 lines=item['mol'].splitlines();n=int(lines[3][:3]);xy=[(float(l[:10]),float(l[10:20]))for l in lines[4:4+n]]
 offsets=corrections(lines);degrees=sum(offsets)/len(offsets)
 row=dict(key=item['key'],carbonylCorrectionsBefore=offsets,degrees=degrees)
 if max(abs(t)for t in offsets)<.02:
  row['degrees']=0;row['carbonylCorrectionsAfter']=offsets;return None,row
 assert item['key']in TARGETS,item['key']
 a=math.radians(degrees);co,si=math.cos(a),math.sin(a);parent=[xy[i-1]for i in item['chain']]
 cx=sum(x for x,y in parent)/len(parent);cy=sum(y for x,y in parent)/len(parent)
 for i,(x,y)in enumerate(xy):
  u,v=x-cx,y-cy;lines[4+i]=f'{cx+u*co-v*si:10.4f}{cy+u*si+v*co:10.4f}'+lines[4+i][20:]
 row['carbonylCorrectionsAfter']=corrections(lines)
 assert max(abs(t)for t in row['carbonylCorrectionsAfter'])<.02
 return '\n'.join(lines)+'\n',row
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=Path('js/jsme-nick-nomeclature-moc2-data_51.js'));p.add_argument('--output',type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 rows=[];count=0
 for item in extract(args.source):
  mol,row=rotate(item);rows.append(row)
  if mol:
   dest=args.output/(item['key']+'_2D_Skeletal.mol');assert not dest.exists();dest.write_text(mol);count+=1
 dest=args.output/'alignment.json';assert not dest.exists();dest.write_text(json.dumps(rows,indent=2)+'\n')
 print('Generated',count,'rigid rotations;',len(rows)-count,'already aligned')
