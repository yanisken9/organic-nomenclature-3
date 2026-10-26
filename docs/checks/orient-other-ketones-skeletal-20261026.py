"""Rigid MOL rotation: minimize numbered parent height, least rotation on ties.

Read --source JS data and write three rotated MOL files into new --output.
No atom/bond order, stereoflag, graph, angle or bond-length edits. Existing
shape is retained; atoms are rotated together about the parent centroid.
"""
from pathlib import Path
import argparse,json,math,subprocess
TARGETS=['pentyn_4_one_2','penten_1_yn_4_one_3','ethyl_3_methyl_4_octen_3_yn_5_dione_2_7']
def extract(source):
 keys=json.loads(Path('scenarios/other-ketones-nomenclature.scenario.json').read_text())['steps'][0]['menuSubset']
 js='var window={};'+Path(source).read_text()+';print(JSON.stringify('+json.dumps(keys)+'.map(k=>({key:k,chain:nameExamples[k].mainChain_Skeletal,mol:window.MOL2D[k].skeletal}))));'
 r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',capture_output=True,text=True)
 assert r.returncode==0,(r.stdout,r.stderr)
 return json.loads(r.stdout)
def optimal(points):
 candidates=[0.]
 for i,(x,y) in enumerate(points):
  for u,v in points[:i]:
   a=-math.atan2(v-y,u-x)
   while a>math.pi/2:a-=math.pi
   while a<-math.pi/2:a+=math.pi
   if abs(a)<=math.pi/4:candidates.append(a)
 def height(a):
  ys=[x*math.sin(a)+y*math.cos(a)for x,y in points]
  return max(ys)-min(ys)
 angle=min(candidates,key=lambda a:(round(height(a),4),abs(a)))
 return angle,height(0),height(angle)
def rotate(item):
 lines=item['mol'].splitlines();n=int(lines[3][:3]);xy=[(float(l[:10]),float(l[10:20]))for l in lines[4:4+n]]
 parent=[xy[i-1]for i in item['chain']];a,h0,h1=optimal(parent)
 if h0-h1<.0002:
  return None,dict(key=item['key'],degrees=0,parentHeightBefore=h0,parentHeightAfter=h0)
 assert item['key']in TARGETS,item['key']
 assert abs(a)>1e-6 and h1<h0
 cx=sum(x for x,y in parent)/len(parent);cy=sum(y for x,y in parent)/len(parent);co,si=math.cos(a),math.sin(a)
 for i,(x,y) in enumerate(xy):
  u=x-cx;v=y-cy;lines[4+i]=f'{cx+u*co-v*si:10.4f}{cy+u*si+v*co:10.4f}'+lines[4+i][20:]
 return '\n'.join(lines)+'\n',dict(key=item['key'],degrees=math.degrees(a),parentHeightBefore=h0,parentHeightAfter=h1)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=Path('js/jsme-nick-nomeclature-moc2-data_51.js'));p.add_argument('--output',type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 rows=[];changed=0
 for item in extract(args.source):
  mol,row=rotate(item);rows.append(row)
  if mol:
   changed+=1
   dest=args.output/(item['key']+'_2D_Skeletal.mol');assert not dest.exists();dest.write_text(mol)
 dest=args.output/'rotation.json';assert not dest.exists();dest.write_text(json.dumps(rows,indent=2)+'\n')
 print('Generated',changed,'rigid rotations;',len(rows)-changed,'already horizontal')
