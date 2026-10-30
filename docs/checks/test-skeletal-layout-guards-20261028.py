"""Read-only synthetic bounds: unsafe cycles/collisions decline local sp repair."""
from pathlib import Path
import json,subprocess,math
source=Path('js/mulermoc-nom-molview-52.js').read_text().split('// BEGIN SKELETAL GEOMETRY')[1].split('// END SKELETAL GEOMETRY')[0]
def mol(atoms,bonds):
 lines=['geometry probe','Namelecule','',f'{len(atoms):3}{len(bonds):3}  0  0  0  0            999 V2000']
 for symbol,x,y in atoms:lines.append(f'{x:10.4f}{y:10.4f}{0:10.4f} {symbol:<3} 0  0  0  0  0  0  0  0  0  0  0  0')
 for a,b,order in bonds:lines.append(f'{a:3}{b:3}{order:3}  0  0  0  0')
 return '\n'.join(lines+['M  END',''])
linear=mol([('C',0,0),('N',0,-1),('C',0,1),('C',1,1)],[(1,2,3),(1,3,1),(3,4,1)])
bent=mol([('C',0,0),('N',1,0),('C',0,1),('C',1,1)],[(1,2,3),(1,3,1),(3,4,1)])
ring=mol([('C',0,0),('C',1,0),('C',.5,1)],[(1,2,3),(2,3,1),(3,1,1)])
collision=mol([('C',0,0),('N',1,0),('C',0,1),('C',2,1),('C',2,-.5),('C',-1,-.5)],[(1,2,3),(1,3,1),(3,4,1),(4,5,1),(5,6,1)])
endpoint_contact=mol([('C',0,0),('N',1,0),('C',0,1),('C',2,1),('C',2,-1),('C',-2,-1)],[(1,2,3),(1,3,1),(3,4,1),(4,5,1),(5,6,1)])
# An oblique original sp bond rotates onto a long collinear remote segment.
collinear=mol([('C',0,0),('N',1,1),('C',-1,0),('C',-1,2),('C',.4,2),('C',.4,0),('C',1.1,0)],[(1,2,3),(1,3,1),(3,4,1),(4,5,1),(5,6,1),(6,7,1)])
cases=[('endpointContact',endpoint_contact,[1,3,4,5,6]),('collinearOverlap',collinear,[1,3,4,5,6,7]),('linear',linear,[1,3,4]),('bent',bent,[1,3,4]),('ring',ring,[1,2,3]),('collision',collision,[1,3,4,5,6]),('invalidParent',bent,[1,2]),('duplicateParent',bent,[1,1]),('malformed','invalid',[1])]
js=source+';var cases='+json.dumps(cases)+';print(JSON.stringify(cases.map(([id,mol,chain])=>({id,original:mol,result:fSkeletalLayoutMol(mol,chain)}))));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
rows={x['id']:x for x in json.loads(r.stdout)}
assert not rows['linear']['result']['repairs']
assert len(rows['bent']['result']['repairs'])==1 and not rows['bent']['result']['skipped']
assert set(rows['ring']['result']['skipped'])=={1,2} and not rows['ring']['result']['repairs']
assert rows['collision']['result']['skipped']==[1] and not rows['collision']['result']['repairs']
for key in ['invalidParent','duplicateParent','malformed']:assert rows[key]['result']['mol']==rows[key]['original']
for key in ['endpointContact','collinearOverlap']:
 assert rows[key]['result']['skipped']==[1] and not rows[key]['result']['repairs'],(key,rows[key])
for key in ['ring','collision','endpointContact','collinearOverlap']:
 before=rows[key]['original'].splitlines();after=rows[key]['result']['mol'].splitlines();n=int(before[3][:3]);a=[(float(s[:10]),float(s[10:20])) for s in before[4:4+n]];b=[(float(s[:10]),float(s[10:20])) for s in after[4:4+n]]
 assert max(abs(math.dist(a[i],a[j])-math.dist(b[i],b[j]))for i in range(n)for j in range(i))<.0003
print('PASS 9 geometry guards: valid/bent sp, unsafe ring, new crossing, endpoint-on-bond, collinear overlap, invalid/duplicate parent, malformed input')
