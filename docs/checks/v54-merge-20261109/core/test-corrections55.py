"""Actual before/after probes for chemistry findings CV55-07..10.
Uses the frozen pre-correction source plus current54 for introduction triage.
"""
from pathlib import Path
import argparse,ast,hashlib,json,subprocess,datetime
P=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;D=H/'corrections-20261110';C=Path(argparse.ArgumentParser().parse_known_args()[1][0]);J='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
check='--check' in __import__('sys').argv
z=ast.parse((P/'docs/checks/v54-sync-20261104/core/test-core54.py').read_text());v={n.targets[0].id:ast.literal_eval(n.value)for n in z.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['PREFIX','TAIL']}
rules=r'''
if(task==='rules'){
 const keys=['tert-butyl','sec-butyl','ditert-butyl','dimethyl','isopropyl','2-chloroethyl'].map(x=>[x,fENSubstSortKey(x)]);
 const mults=['diisobutyl','triisobutyl','tetraisobutyl','ditert-butyl','diisopropyl','disec-butyl','dichloromethyl','di(2-chloroethyl)'].map(x=>[x,fSystematicSubstSlot(1,x)]);
 const parens=[['2-chloroethyl','2-chloroethyl','6-'],['propan-2-yl','isopropyl','4-'],['ethyl','ethyl','4-'],['(2-chloroethyl)','2-chloroethyl','6-'],['2-chloroethyl','2-chloroethyl','']].map(x=>({args:x,result:fENSysNeedsParens(...x)}));
 const gs=[{name:'tert-butyl',loc:'1'},{name:'sec-butyl',loc:'8'},{name:'butyl',loc:'9'}];const idx=fENSortSubstGroups(gs)||[0,1,2];
 return {keys,mults,parens,italicTie:idx.map(i=>gs[i].name)};
}
'''
tail=rules+v['TAIL'].replace('const answer=state();',r'''const answer=state();
answer.school=fPopulateEngineENFromGreek(key);answer.sys=fPopulateEngineENFromGreek(key,'sys');
answer.schoolBoxes=fNameENBoxes();answer.sysBoxes=fNameENBoxes('sys');return answer;
''')
files={'current54':[P/'js/mulermoc-nom-core-54.js',P/'js/mulermoc-nom-name-en-54.js'],'before55':[D/'before-core55.js',D/'before-name-en55.js'],'after55':[C/'js/mulermoc-nom-core-55.js',C/'js/mulermoc-nom-name-en-55.js']}
tail=tail.replace('extra.types.map((el,i)=>({el,x:i,y:0}))','extra.atoms||extra.types.map((el,i)=>({el,x:i,y:0}))')
src=''
for k,ps in files.items():src+='var '+k+'=new Function("task","key","mode","cm","extra",'+json.dumps(v['PREFIX']+(P/'js/jsme-nick-nomeclature-moc2-data_54.js').read_text()+'\n'+'\n'.join(p.read_text()for p in ps)+'\n'+tail)+');'
src+=r'''
function chain(n){return {types:Array(n).fill('C'),edges:Array.from({length:n-1},(_,i)=>[i+1,i+2,1])}}
function add(x,at,shape){const first=x.types.length+1;for(const [el,parent,order]of shape){x.types.push(el);x.edges.push([parent===null?at:first+parent,x.types.length,order||1])}return first}
const decorated=chain(11);add(decorated,6,[['C',null],['C',0],['Cl',1]]);
const order=chain(11);add(order,4,[['C',null],['C',0],['C',0],['C',0]]);add(order,6,[['C',null],['C',0],['C',1]]);add(order,7,[['C',null],['C',0]]);
const multiplied=chain(13);for(const at of [5,8])add(multiplied,at,[['C',null],['C',0],['C',1],['C',1]]);
const lost=chain(11);add(lost,6,[['C',null],['C',0,2],['Cl',1]]);
const lostNitro=chain(11);add(lostNitro,6,[['C',null],['C',0,2],['N',1],['O',2,2],['O',2]]);
lostNitro.atoms=lostNitro.types.map((el,i)=>({el,x:i,y:0,charge:el==='N'?1:(i===16?-1:0)}));
const saturatedHalo=chain(11);add(saturatedHalo,6,[['C',null]]);add(saturatedHalo,1,[['Cl',null]]);
const plainHalo=chain(11);add(plainHalo,1,[['Cl',null]]);
const boundaries=[];
for(const [label,shape]of [['isopropyl',[['C',null],['C',0],['C',0]]],['sec-butyl',[['C',null],['C',0],['C',0],['C',2]]],['tert-butyl',[['C',null],['C',0],['C',0],['C',0]]]]){
 const x=chain(13);for(const at of [5,8])add(x,at,shape);boundaries.push([label,x]);}
const out={};for(const [k,fn]of [['current54',current54],['before55',before55],['after55',after55]]){
 out[k]={};for(const [label,x]of [['CV55-07',decorated],['CV55-08',order],['CV55-09',multiplied],['CV55-10',lost],['CV55-10-nitro',lostNitro],['CV55-10-saturated',saturatedHalo],['unbranched-halo',plainHalo],...boundaries]){
 try{out[k][label]={status:'named',...fn('probe','ethane','condensed','algorithmic',x)}}catch(e){out[k][label]={status:'declined',error:String(e)}}
 }
}
print(JSON.stringify({versions:out,rules:after55('rules')}));
'''
r=subprocess.run([J,'-e','eval(JSON.parse(readline()))'],input=json.dumps(src)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout[-4000:],r.stderr[-1500:]);raw=json.loads(r.stdout);o=raw['versions']
o={'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':o,'rules':raw['rules'],'sourceSHA256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for ps in files.values()for p in ps}}
if check:
 a=o['results']['after55'];b=o['results']['before55'];c=o['results']['current54']
 assert b['CV55-07']['sys']=='6-2-chloroethylundecane'
 assert a['CV55-07']['sys']=='6-(2-chloroethyl)undecane'
 assert a['CV55-08']['school']=='4-tert-butyl-7-ethyl-6-propylundecane'
 assert a['CV55-08']['sys']=='7-ethyl-4-(2-methylpropan-2-yl)-6-propylundecane'
 assert a['CV55-09']['sys']=='5,8-bis(2-methylpropyl)tridecane'
 assert a['isopropyl']['sys']=='5,8-di(propan-2-yl)tridecane'
 assert a['sec-butyl']['sys']=='5,8-di(butan-2-yl)tridecane'
 assert a['tert-butyl']['sys']=='5,8-bis(2-methylpropan-2-yl)tridecane'
 assert all(a[k]['status']=='declined' for k in ['CV55-10','CV55-10-nitro','CV55-10-saturated'])
 assert a['unbranched-halo']['status']=='named' and a['unbranched-halo']['school']=='1-chloroundecane'
 assert c['CV55-10']['status']=='named' and b['CV55-10']['status']=='named'
 for k,x in a.items():
  if x['status']!='named':continue
  assert x['name']==b[k]['name'],'Greek format changed:'+k
  for field,box in [('school','schoolBoxes'),('sys','sysBoxes')]:
   bx=x[box];joined=''.join(t+(' 'if bx['spaceAfter']==i else'')for i,t in bx['boxes']);assert joined==x[field],(k,field,joined,x[field])
   ids=[i for i,t in bx['boxes']];assert len(ids)==len(set(ids)),(k,field,ids)
 r=o['rules']
 assert r['keys']==[['tert-butyl','butyl'],['sec-butyl','butyl'],['ditert-butyl','butyl'],['dimethyl','methyl'],['isopropyl','isopropyl'],['2-chloroethyl','chloroethyl']]
 assert dict(r['mults'])=={'diisobutyl':'bis(2-methylpropyl)','triisobutyl':'tris(2-methylpropyl)','tetraisobutyl':'tetrakis(2-methylpropyl)','ditert-butyl':'bis(2-methylpropan-2-yl)','diisopropyl':'di(propan-2-yl)','disec-butyl':'di(butan-2-yl)','dichloromethyl':'bis(chloromethyl)','di(2-chloroethyl)':'bis(2-chloroethyl)'}
 assert [x['result']for x in r['parens']]==[True,True,False,False,False]
 assert r['italicTie']==['butyl','sec-butyl','tert-butyl']
 bx=a['CV55-08']['sysBoxes']['boxes'];by=dict(bx)
 assert by['comp1']=='(2-methylpropan-2-yl)' and by['comp3']=='ethyl' and by['comp3b']=='propyl'
 assert [i for i,t in bx][:6]==['comp2','comp3','comp0','comp1','comp3loc','comp3b']
 o['passed']=True
out=D/('after-results.json'if check else'before-results.json');out.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:{j:{z:x.get(z)for z in ['status','name','school','sys','error']}for j,x in d.items()}for k,d in o['results'].items()},ensure_ascii=False))
