"""31 upstream acceptance graphs plus local merge regression and suffix fixtures.
SMILES here is a narrow test-input notation, parsed only to an explicit tree;
all analysis/naming/3D functions are the actual project JavaScript. No JSME.
"""
from pathlib import Path
import ast,datetime,hashlib,json,re,subprocess
P=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;C=Path('/private/tmp/namelecule-v57-sync-20261115-l4r9e5_s/candidate');J='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
page=(P/'docs/checks/v56-sync-20261115/upstream/target/zz-test-core56.html').read_text();part=page[page.index('var probes = [')+13:page.index('      function parse(s)')].strip().rstrip(';')
probes=json.loads(part)
def parse(s):
 atoms=[];edges=[];stack=[];prev=None;order=1;i=0
 while i<len(s):
  ch=s[i]
  if ch=='(':stack.append(prev);i+=1;continue
  if ch==')':prev=stack.pop();i+=1;continue
  if ch in '=#':order={'=':2,'#':3}[ch];i+=1;continue
  m=re.match(r'\[([A-Z][a-z]?)([+-]\d*)?\]|(Cl|Br|[A-Z])',s[i:]);assert m,s[i:]
  el=m[1]or m[3];q=m[2];charge=(1 if q[0]=='+'else -1)*(int(q[1:])if q[1:]else 1)if q else 0
  atoms.append({'el':el,'x':len(atoms)*1.25,'y':0,'charge':charge})
  if prev is not None:edges.append([prev,len(atoms),order])
  prev=len(atoms);order=1;i+=len(m[0])
 return {'types':[a['el']for a in atoms],'atoms':atoms,'edges':edges}
fixtures=[{'label':a,'smiles':b,'expected':c,'graph':parse(b)}for a,b,c in probes]
fixtures.append({'label':'local-C7-C4-methyl-C2-chloro','smiles':'CC(Cl)CC(C)CCC','expected':'DECLINE','graph':parse('CC(Cl)CC(C)CCC')})
z=ast.parse((P/'docs/checks/v54-sync-20261104/core/test-core54.py').read_text());const={n.targets[0].id:ast.literal_eval(n.value)for n in z.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['PREFIX','TAIL']}
tail=const['TAIL'].replace("if(task==='probe'){","if(task==='probe'||task==='priority'){").replace('extra.types.map((el,i)=>({el,x:i,y:0}))','extra.atoms||extra.types.map((el,i)=>({el,x:i,y:0}))')
tail=tail.replace('const answer=state();',r'''const answer=state();
answer.school=fPopulateEngineENFromGreek(key);answer.sys=fPopulateEngineENFromGreek(key,'sys');
answer.schoolBoxes=fNameENBoxes();answer.sysBoxes=fNameENBoxes('sys');
if(task==='probe'){
 fParseSDF3D(source);fDetectMolType3D();fCalcMainChain3D();
 answer.groups2=Object.keys(functionalGroupObj);answer.groups3=Object.keys(functionalGroupObj3D);
 answer.chain3=mainChainAtoms3D;answer.signature3=fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D);
 return answer;
}
''')
tail=tail.replace('fGuessName();', "if(task==='priority'){fCalcMainChain();fParseSDF3D(source);fDetectMolType3D();fCalcMainChain3D();return {chain2:mainChainAtomsList,chain3:mainChainAtoms3D,terminal2:terminalFgCarbons,terminal3:terminalFgCarbons3D}}fGuessName();")
tail=r'''
if(task==='fusion')return extra.map(([infix,suffix])=>fFuseEnInfixSuffix(infix,suffix));
'''+tail
src=''
for name,folder,ver in [('candidate',C,57),('local55',P,55),('raw56',P/'docs/checks/v56-sync-20261115/upstream/target',56)]:
 files=[C/'js/jsme-nick-nomeclature-moc2-data_57.js']+[folder/f'js/mulermoc-nom-{k}-{ver}.js'for k in ['core','name-en']]
 src+='var '+name+'=new Function("task","key","mode","cm","extra",'+json.dumps(const['PREFIX']+'\n'.join(p.read_text()for p in files)+'\n'+tail)+');'
src+='const fixtures='+json.dumps(fixtures)+';const acidEsterGraph='+json.dumps(parse('COC(=O)CCC(=O)O'))+';'
src+=r'''
function invoke(fn,g){try{return {status:'named',...fn('probe','ethane','condensed','algorithmic',g)}}catch(e){return{status:'declined',error:String(e)}}}
const versions={};for(const [label,fn]of [['local55',local55],['raw56',raw56],['candidate',candidate]]){
 versions[label]=fixtures.map(f=>({...f,result:invoke(fn,f.graph)}));
}
const fusionArgs=[['yn','-2,7-dione'],['en','2,5-diol'],['yn','-1-ol'],['en','-2-one'],['yn','dioic acid'],['yn','dial'],['en','-5-']];
const suffixFusion={args:fusionArgs,result:candidate('fusion',null,null,null,fusionArgs)};
const dialKey='ethyl_2_methyl_3_hexen_2_yn_4_dial';
const dial={};for(const [label,fn]of [['local55',local55],['raw56',raw56],['candidate',candidate]]){
 const a=fn('name',dialKey,'condensed','algorithmic');dial[label]=a;
}
const priority={};for(const [label,fn]of [['local55',local55],['raw56',raw56],['candidate',candidate]]){try{priority[label]=fn('priority','ethane','condensed','algorithmic',acidEsterGraph)}catch(e){priority[label]={error:String(e)}}}print(JSON.stringify({versions,suffixFusion,dial,priority}));
'''
r=subprocess.run([J,'-e','eval(JSON.parse(readline()))'],input=json.dumps(src)+'\n',capture_output=True,text=True);assert r.returncode==0,(r.stdout[-3000:],r.stderr[-1000:]);out=json.loads(r.stdout)
failures=[];accepted=declined=mirror=boxes=0
for f in out['versions']['candidate']:
 a=f['result'];expected=f['expected']
 if expected=='DECLINE':
  declined+=1
  if a['status']!='declined':failures.append({'label':f['label'],'expected':expected,'actual':a})
 else:
  accepted+=1
  if a['status']!='named'or a['school']!=expected:failures.append({'label':f['label'],'expected':expected,'actual':a});continue
  if a['signature']!=a['signature3']or set(a['groups2'])!=set(a['groups3']):failures.append({'label':f['label'],'kind':'3D principal/group mirror','actual':a})
  else:mirror+=1
  for value,bkey in [('school','schoolBoxes'),('sys','sysBoxes')]:
   b=a[bkey];joined=''.join(t+(' 'if b['spaceAfter']==i else'')for i,t in b['boxes'])
   if joined!=a[value]:failures.append({'label':f['label'],'kind':value+' box/name mismatch','actual':a[value],'joined':joined})
   else:boxes+=1
assert out['priority']['candidate']['chain2'][0]==7 and out['priority']['candidate']['chain3'][0]==7,out['priority']
assert out['priority']['local55']['chain2'][0]==3 and out['priority']['local55']['chain3'][0]==3,out['priority']
assert out['suffixFusion']['result']==['yne','ene','yn','en','yne','yne','en']
a=out['dial']['candidate'];assert a['school']=='2-ethyl-3-methylhex-2-en-4-ynedial'
assert out['dial']['raw56']['school']=='2-ethyl-3-methylhex-2-en-4-yne-dial'
out['summary']={'fixtures':len(fixtures),'expectedNamed':accepted,'expectedDeclined':declined,'mirrored3D':mirror,'matchingBoxAssemblies':boxes,'suffixFusionChecks':len(out['suffixFusion']['result']),'failures':failures,'actualRuntime':'macOS JavaScriptCore actual project functions; raw hand-built tree fixtures, no JSME'}
out['timestampUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();out['candidateSHA256']={str(C/f'js/mulermoc-nom-{k}-57.js'):hashlib.sha256((C/f'js/mulermoc-nom-{k}-57.js').read_bytes()).hexdigest()for k in ['core','name-en']}
(D/'upstream-chemistry-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out['summary'],ensure_ascii=False));assert not failures,failures
