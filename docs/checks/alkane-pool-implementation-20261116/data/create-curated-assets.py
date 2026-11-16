"""One-time curation evidence. Writes only the approved six new asset records."""
from pathlib import Path
import collections, datetime, hashlib, itertools, json, math, runpy, subprocess
ROOT=Path.cwd(); HERE=Path(__file__).resolve().parent
PLAN=json.loads((ROOT/'docs/checks/four-games-roadmap-preflight-20261116/pool-first-plan.json').read_text())
DOWNLOADS={m['id']:m for m in json.loads((HERE/'pubchem-downloads.json').read_text())['rows']}
H=runpy.run_path(str(ROOT/'tools/build-namelecule-alkane-data.py'))
parse=H['parse_mol']; sha=H['sha256']; CORE='js/mulermoc-nom-core-57.js'; DATA='js/jsme-nick-nomeclature-moc2-data_57.js'
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def js(code):
 p=subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True,check=True)
 return json.loads(p.stdout)
base=js('var window={};'+(ROOT/DATA).read_text()+';print(JSON.stringify(window.MOL2D));')
ids=['methane','ethane','propane','butane','pentane','methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']
def metric(mol):
 a,b,ns=parse(mol);d=collections.defaultdict(list)
 for u,v,_ in b:d['CC' if a[u-1]['element']==a[v-1]['element']=='C' else 'CH'].append(round(math.dist(a[u-1]['xyz'],a[v-1]['xyz']),6))
 return {k:{'count':len(v),'min':min(v),'max':max(v),'values':sorted(set(v))}for k,v in d.items()}
# Historical originals may contain harmless SUP Sgroups, parsed separately below.
def oldmetric(mol):
 ls=mol.splitlines();n=int(ls[3][:3]);nb=int(ls[3][3:6]);a=[([float(l[i:i+10])for i in (0,10,20)],l[31:34].strip())for l in ls[4:4+n]];d=collections.defaultdict(list)
 for l in ls[4+n:4+n+nb]:
  u,v=[int(l[i:i+3])-1 for i in (0,3)];d['CC'if a[u][1]==a[v][1]=='C'else'CH'].append(round(math.dist(a[u][0],a[v][0]),6))
 return {k:{'count':len(v),'min':min(v),'max':max(v),'values':sorted(set(v))}for k,v in d.items()}
old={k:{f:oldmetric(mol)for f,mol in base[k].items()if mol}for k in ids}
(HERE/'old-eight-geometry.json').write_text(json.dumps({'baseData':DATA,'sha256':sha((ROOT/DATA).read_bytes()),'molecules':old},indent=2)+'\n')
# The three branched skeletal records use .825; old unbranched skeletal forms use ~1.4.
# Native generation is dimensionless CC=1/CH=.5, normalized per representation.
scales={'condensed':.825,'expanded':.6188,'skeletal':.825}
manifest={'schemaVersion':1,'id':'namelecule-alkanes-v1','molecules':[]}
report=[]
def heavy_mol(m):
 n=max(max(e)for e in m['preflightCarbonEdges']);lines=[m['id'],'  Namelecule 2D','',f'{n:3d}{n-1:3d}  0  0  0  0  0  0  0  0999 V2000']
 lines += [f'{float(i):10.4f}{0.:10.4f}{0.:10.4f} C   0  0  0  0  0  0  0  0  0  0  0  0'for i in range(n)]
 lines += [f'{u:3d}{v:3d}  1  0  0  0  0'for u,v in m['preflightCarbonEdges']];return'\n'.join(lines+['M  END',''])
def write_xy(text,coords):
 ls=text.splitlines();n=int(ls[3][:3]);assert len(coords)==n
 for i,(x,y)in enumerate(coords):
  x=0 if abs(x)<.00005 else x;y=0 if abs(y)<.00005 else y
  ls[i+4]=f'{x:10.4f}{y:10.4f}{0.:10.4f}'+ls[i+4][30:]
 return'\n'.join(ls)+'\n'
def spread_quaternary_branches(text,parent_count):
 # Curate native fourth-ray crowding by rotating whole separable off-parent
 # sides about the saturated quaternary center. Retain the 120-degree parent
 # zigzag, all bond lengths and every other local angle. Two off-parent arms
 # share the exterior bisector at +/-30 degrees (minimum local angle60).
 a,b,ns=parse(text);xy=[p['xyz'][:2]for p in a]
 for center,neighbors in enumerate(ns):
  parent_neighbors=[j-1 for j in neighbors if j<=parent_count]
  branches=[j-1 for j in neighbors if j>parent_count]
  if center>=parent_count or len(neighbors)!=4 or len(parent_neighbors)!=2 or len(branches)!=2:continue
  vectors=[(xy[j][0]-xy[center][0],xy[j][1]-xy[center][1])for j in parent_neighbors]
  bx=-sum(x/math.hypot(x,y)for x,y in vectors);by=-sum(y/math.hypot(x,y)for x,y in vectors);base=math.atan2(by,bx)
  for branch,target in zip(branches,[base-math.pi/6,base+math.pi/6]):
   angle=target-math.atan2(xy[branch][1]-xy[center][1],xy[branch][0]-xy[center][0]);co,si=math.cos(angle),math.sin(angle);visited={center};todo=[branch]
   while todo:
    node=todo.pop()
    if node in visited:continue
    visited.add(node);x,y=xy[node][0]-xy[center][0],xy[node][1]-xy[center][1];xy[node]=[xy[center][0]+co*x-si*y,xy[center][1]+si*x+co*y];todo.extend(j-1 for j in ns[node]if j-1 not in visited)
 return write_xy(text,xy)
def normalize(text,scale,orthogonal=False):
 a,b,ns=parse(text);xy=[p['xyz'][:2]for p in a]
 if orthogonal:
  axes=[(1,0),(0,1),(-1,0),(0,-1)]
  for i,p in enumerate(a):
   if p['element']!='C':continue
   heavy=[j-1 for j in ns[i]if a[j-1]['element']=='C'];hs=[j-1 for j in ns[i]if a[j-1]['element']=='H']
   occupied={(round(xy[j][0]-xy[i][0]),round(xy[j][1]-xy[i][1]))for j in heavy}
   assert occupied.issubset(set(axes)),(i,occupied)
   free=[v for v in axes if v not in occupied];assert len(free)==len(hs)
   for h,(dx,dy)in zip(hs,free):xy[h]=[xy[i][0]+.5*dx,xy[i][1]+.5*dy]
 # Proper uniform scaling+translation only after the native layout/H policy.
 cx=(max(p[0]for p in xy)+min(p[0]for p in xy))/2;cy=(max(p[1]for p in xy)+min(p[1]for p in xy))/2
 return write_xy(text,[((x-cx)*scale,(y-cy)*scale)for x,y in xy])
def map_graph(a2,b2,a3,b3):
 n=sum(x['element']=='C'for x in a2); ns2=[[]for _ in a2];ns3=[[]for _ in a3]
 for u,v,_ in b2:ns2[u-1].append(v-1);ns2[v-1].append(u-1)
 for u,v,_ in b3:ns3[u-1].append(v-1);ns3[v-1].append(u-1)
 c3=[i for i,a in enumerate(a3)if a['element']=='C'];order=sorted(range(n),key=lambda i:-len([j for j in ns2[i]if j<n]));mapping={};used=set()
 def walk(k):
  if k==n:return True
  i=order[k]
  for j in c3:
   if j in used or len(ns2[i])!=len(ns3[j]):continue
   if sum(x<n for x in ns2[i])!=sum(a3[x]['element']=='C'for x in ns3[j]):continue
   if any((p in ns2[i])!=(q in ns3[j])for p,q in mapping.items()):continue
   mapping[i]=j;used.add(j)
   if walk(k+1):return True
   del mapping[i];used.remove(j)
  return False
 assert walk(0),'no heavy-atom graph isomorphism'
 for i in range(n):
  hs2=sorted(j for j in ns2[i]if j>=n);hs3=sorted(j for j in ns3[mapping[i]]if a3[j]['element']=='H');assert len(hs2)==len(hs3)
  mapping.update(zip(hs2,hs3))
 return[mapping[i]+1 for i in range(len(a2))]
def achiral(mol):
 a,b,ns=parse(mol)
 def tree(i,par):return a[i]['element']+'('+''.join(sorted(tree(j-1,i)for j in ns[i]if j-1!=par))+')'
 centers=[]
 for i,at in enumerate(a):
  if at['element']=='C'and len(ns[i])==4 and len(set(tree(j-1,i)for j in ns[i]))==4:centers.append(i+1)
 assert not centers;return True
for m in PLAN['proposedBatch']:
 key=m['id'];mol=heavy_mol(m);chain=list(range(1,m['parentC']+1))
 code=(ROOT/CORE).read_text()+'\nvar src='+json.dumps(mol)+';var ch='+json.dumps(chain)+';var c=fLinearizeMol(src,ch);print(JSON.stringify({condensed:c,expanded:fGenExpandedMol(c),skeletal:fZigzagMol(src,ch)}));'
 forms=js(code);assert all(forms.values()),key
 forms['skeletal']=spread_quaternary_branches(forms['skeletal'],m['parentC'])
 forms={f:normalize(s,scales[f],f=='expanded')for f,s in forms.items()}
 files={};hashes={}
 for f,s in forms.items():
  p=f'mols/namelecule-alkanes-v1/{key}_2D_{H["FORMS"][f]}.mol';(ROOT/p).write_text(s);files[f]=p;hashes[f]=sha(s.encode())
 p=f'mols/namelecule-alkanes-v1/{key}_3D.sdf';files['sdf']=p;raw=(ROOT/p).read_bytes();hashes['sdf']=sha(raw);sdf=raw.decode()
 a2,b2,_=parse(forms['expanded']);a3,b3,_=parse(sdf);mapping=map_graph(a2,b2,a3,b3);assert achiral(sdf)
 # Source 3D is not normalized; validate ordinary single-bond length ranges.
 cc3=[math.dist(a3[u-1]['xyz'],a3[v-1]['xyz'])for u,v,_ in b3 if a3[u-1]['element']==a3[v-1]['element']=='C']
 ch3=[math.dist(a3[u-1]['xyz'],a3[v-1]['xyz'])for u,v,_ in b3 if a3[u-1]['element']!=a3[v-1]['element']]
 assert all(1.35<x<1.7 for x in cc3)and all(.9<x<1.25 for x in ch3)
 source={'provider':'PubChem','pubchemCID':m['CID'],'url':DOWNLOADS[key]['url'],'retrievedUTC':json.loads((HERE/'pubchem-downloads.json').read_text())['recordedUTC'],'sha256':hashes['sdf'],'bytes':len(raw),'geometry':'Unmodified PubChem source conformer; no local minimization or optimizer-convergence claim.'}
 prov={'schemaVersion':1,'id':key,'source3D':source,'source2D':{'type':'Locally authored new curated records','graphSource':'Approved pool-first-plan.json carbon edges','nativePipeline':{'file':CORE,'sha256':sha((ROOT/CORE).read_bytes()),'functions':['fLinearizeMol','fGenExpandedMol','fZigzagMol'],'generatorUnits':{'CC':1.0,'CH':.5}},'normalization':{'condensedCC':.825,'expandedCC':.6188,'expandedCH':.3094,'skeletalCC':.825,'expandedHPolicy':'Free orthogonal axes at each saturated carbon, matching the existing eight school-form alkanes; parent horizontal.','reference':'js/jsme-nick-nomeclature-moc2-data_57.js; methyl_2_pentane and old-eight-geometry.json','source3DTransformed':False,'skeletalQuaternaryPolicy':'For a degree-four parent center with two off-parent sides, rotate complete sides to exterior bisector +/-30 degrees; preserve 120-degree parent zigzag, all lengths and other local angles. No molecule-ID exception.'}},'atomCorrespondence':{'indexBase':1,'heavy2DAcrossForms':'Carbon IDs 1..N are identical in all three 2D forms.','carbon2DTo3D':mapping[:len(m['preflightCarbonEdges'])+1],'expandedTo3D':mapping,'parentTo3D':[mapping[i-1]for i in chain],'hydrogenEquivalence':'Explicit H are bijectively matched by bonded carbon; symmetry-equivalent H order is arbitrary. These constitutionally achiral alkanes encode no stereochemistry.'},'validation':{'neutral':True,'isotopeFree':True,'connectedAcyclic':True,'singleBondsOnly':True,'formula':m['formula'],'carbonValence':4,'hydrogenValence':1,'constitutionallyAchiral':True,'achiralityMethod':'Rooted-tree substituent equality at each tetrahedral carbon, including explicit H.','graphIdentity':'Element/bond-preserving full 2D-expanded-to-source3D bijection','CC3DRange':[min(cc3),max(cc3)],'CH3DRange':[min(ch3),max(ch3)]}}
 pp=f'mols/namelecule-alkanes-v1/{key}_provenance.json';pr=(json.dumps(prov,ensure_ascii=False,indent=2)+'\n').encode();(ROOT/pp).write_bytes(pr)
 record={'id':key,'nameGR':m['nameGR'],'formula':m['formula'],'pubchemCID':m['CID'],'parentC':m['parentC'],'carbonCount':len(m['preflightCarbonEdges'])+1,'carbonEdges':m['preflightCarbonEdges'],'files':files,'sha256':hashes,'provenance':pp,'provenanceSHA256':sha(pr)}
 H['validate_record'](record,{**forms,'sdf':sdf},prov);manifest['molecules'].append(record)
 report.append({'id':key,'geometry':{f:metric(s)for f,s in forms.items()},'source3DSHA256':hashes['sdf'],'expandedTo3D':mapping,'constitutionallyAchiral':True})
mp=ROOT/'data/namelecule-alkanes-v1/manifest.json';mp.parent.mkdir(parents=True,exist_ok=True);mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(HERE/'asset-validation.json').write_text(json.dumps({'passed':True,'role':'Developer evidence, pending independent chemistry validation','manifestSHA256':sha(mp.read_bytes()),'rows':report},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sources':len(manifest['molecules']),'manifestSHA256':sha(mp.read_bytes()),'nativeCoreUnchanged':sha((ROOT/CORE).read_bytes())}))
