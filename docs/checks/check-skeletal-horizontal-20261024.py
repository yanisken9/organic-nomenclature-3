"""Read-only orientation and optional rigid-transform preservation check."""
from pathlib import Path
import sys,math
keys=[('dimethyl_2_3_pentadiene_1_3',5),('ethyl_3_dimethyl_4_5_hexadiene_1_4',6)]
for key,parent in keys:
 p=Path('mols/new_molecules',key+'_2D_Skeletal.mol');lines=p.read_text().splitlines();n=int(lines[3][:3]);xyz=[tuple(map(float,l[:30].split())) for l in lines[4:4+n]]
 if parent==5:assert xyz[parent-1][0]>xyz[0][0] and abs(xyz[parent-1][1]-xyz[0][1])<.0002,key
 else:
  assert abs(xyz[0][1]-xyz[1][1])<.0002,key
  assert abs(xyz[3][1]-xyz[4][1])<.0002,key
 assert abs(min(x[0] for x in xyz)+max(x[0] for x in xyz))<.0002,key
 assert abs(min(x[1] for x in xyz)+max(x[1] for x in xyz))<.0002,key
 if len(sys.argv)>1:
  old=(Path(sys.argv[1])/p).read_text().splitlines();assert len(old)==len(lines)
  assert all((a==b if not 4<=i<4+n else a[30:]==b[30:]) for i,(a,b) in enumerate(zip(old,lines))),key
  before=[tuple(map(float,l[:30].split())) for l in old[4:4+n]]
  for i in range(n):
   for j in range(i):assert abs(math.dist(before[i],before[j])-math.dist(xyz[i],xyz[j]))<.0002,key
 print('PASS',key,'horizontal orientation,centered bounds;rigid distances/fields if baseline supplied')
