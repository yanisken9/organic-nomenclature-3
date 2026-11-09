"""Actual JS display transforms: H accounting, proper rotation, immutable indexed graphs."""
from pathlib import Path
import argparse,json,math,importlib.util
parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
spec=importlib.util.spec_from_file_location('naming',Path('docs/checks/test-esters-naming-20261029.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
source=module.PREFIX+'\n'.join(Path(p).read_text() for p in module.FILES)
old=module.PREFIX+'\n'.join((args.baseline/p).read_text() for p in module.FILES)
tail=r'''
 selectedMol=key;mode2D=mode;mainChainMode='algorithmic';
 const text=window.MOL2D[key][mode],ls=text.split('\n'),n=+ls[3].slice(0,3),nb=+ls[3].slice(3,6);
 const aa=ls.slice(4,4+n).map(l=>({label:l.slice(31,34).trim()}));
 const bb=ls.slice(4+n,4+n+nb).map(l=>({atoms:[+l.slice(0,3),+l.slice(3,6)],order:+l.slice(6,9)}));
 jsmeNomeclatureApplet={totalNumberOfAtoms:()=>aa.length,totalNumberOfBonds:()=>bb.length,getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1]};
 fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();
 const ester=fIsSingleEster();
 return {text,types:allAtomsTypeList,bonds:bondList,name:currentMolName,chain:mainChainAtomsList,ester:esterInfo,
  remaining:allAtomsTypeList.map((t,i)=>t==='C'?fRemainingImplicitCarbonHydrogens(i):null),
  layout:mode==='skeletal'?fSkeletalLayoutMol(text,mainChainAtomsList,ester?esterInfo:null):null,
  formyl:mode==='expanded'?fFormylHydrogenLeftMol(text):null};
'''
js='const run=new Function("key","mode",'+json.dumps(source+tail)+');'
js+='const oldLayout=new Function("mol","chain",'+json.dumps(old+';return fSkeletalLayoutMol(mol,chain);')+');'
js+='const inventory=(new Function('+json.dumps(source+';return Object.keys(window.MOL2D).flatMap(k=>Object.keys(window.MOL2D[k]).filter(m=>window.MOL2D[k][m]).map(m=>[k,m]));')+'))();'
js+='const rows=[];for(const [key,mode]of inventory){const row=run(key,mode);row.key=key;row.mode=mode;if(mode==="skeletal"&&!row.ester&&JSON.stringify(row.layout)!==JSON.stringify(oldLayout(row.text,row.chain)))throw Error("Other skeletal layout changed:"+key);rows.push(row);}print(JSON.stringify(rows));'
rows=module.jsc(js);esters=[];controls=[]
for r in rows:
 ls=r['text'].splitlines();n=int(ls[3][:3]);types=r['types'];bonds=r['bonds']
 for i,t in enumerate(types):
  if t!='C':continue
  valence=sum(o for a,b,o in bonds if i+1 in [a,b])
  assert r['remaining'][i]==4-valence,(r['key'],r['mode'],i,r['remaining'][i],valence)
 if r['mode']=='skeletal':
  out=r['layout']['mol'].splitlines();assert ls[:4]==out[:4] and ls[4+n:]==out[4+n:]
  assert all(a[20:]==b[20:] for a,b in zip(ls[4:4+n],out[4:4+n]))
  xy=lambda lines:[(float(s[:10]),float(s[10:20]))for s in lines[4:4+n]]
  p,q=xy(ls),xy(out)
  if r['ester']:
   assert all(abs(math.dist(p[i],p[j])-math.dist(q[i],q[j]))<.0004 for i in range(n)for j in range(i))
   means=[sum(q[i][0] for i in r['ester'][k])/len(r['ester'][k])for k in ['acidFrag','alcoholFrag']]
   assert means[0]<means[1],r['key']
 if r['formyl']:
  out=r['formyl'].splitlines()
  if r['key']=='tert_butyl_methanoate':
   assert ls[:4]==out[:4] and ls[4+n:]==out[4+n:]
   p=[(float(s[:10]),float(s[10:20]))for s in ls[4:4+n]];q=[(float(s[:10]),float(s[10:20]))for s in out[4:4+n]]
   for a,b,o in bonds:
    if {types[a-1],types[b-1]}!={'C','H'}:continue
    c,h=(a-1,b-1)if types[a-1]=='C'else(b-1,a-1)
    if c!=r['ester']['carbonylC']:continue
    assert q[h][0]<q[c][0] and abs(q[h][1]-q[c][1])<1e-7
    assert abs(math.dist(p[h],p[c])-math.dist(q[h],q[c]))<.0001
    assert all(p[i]==q[i]for i in range(n)if i!=h)
  else:assert r['formyl']==r['text']
 if r['ester']:esters.append({k:r[k]for k in ['key','mode','name','remaining']})
 if r['key'] in ['methanoicacid','methanal','ethanal']:controls.append({k:r[k]for k in ['key','mode','remaining']})
result={'passed':True,'allForms':len(rows),'esterForms':len(esters),'otherSkeletalFormsUnchanged':sum(r['mode']=='skeletal'and not r['ester']for r in rows),'esters':esters,'controls':controls}
args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS',len(rows),'forms H accounting;',len(esters),'ester forms; other skeletal geometry invariant')
