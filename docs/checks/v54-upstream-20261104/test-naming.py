"""Actual naming modules in JavaScriptCore; no browser or oracle substitution."""
from pathlib import Path
import ast, json, subprocess, hashlib

D = Path('docs/checks/v54-upstream-20261104')
tree = ast.parse(Path('docs/checks/v54-sync-20261104/core/test-core54.py').read_text())
c = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
     if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
     and n.targets[0].id in ['PREFIX', 'TAIL']}
tail = c['TAIL'].replace('extra.types.map((el,i)=>({el,x:i,y:0}))', 'extra.atoms||extra.types.map((el,i)=>({el,x:i,y:0}))').replace('const answer=state();',
    'const answer=state();answer.en=fPopulateEngineENFromGreek();answer.boxes=fNameENBoxes();')
data = Path('js/jsme-nick-nomeclature-moc2-data_54.js').read_text()
sources = {}
for key, folder in [('before', D/'before'), ('after', Path('.'))]:
    sources[key] = c['PREFIX'] + data + '\n' + '\n'.join(
        (folder/'js'/p).read_text() for p in [
            'mulermoc-nom-core-54.js', 'mulermoc-nom-name-en-54.js', 'mulermoc-nom-iupac-54.js']) + tail.replace('selectedMol=key; mode2D=mode;mainChainMode=cm;', '''if(task==='longGroup') {
 const types=extra.types, conn=types.map(()=>[]);
 extra.edges.forEach(([a,b])=>{conn[a-1].push(b-1);conn[b-1].push(a-1)});
 fInitNamingProps();return fAlkylGroupName(types.length,extra.attach,'substituent',types.map((_,i)=>i),conn,types,extra.edges);
}
selectedMol=key; mode2D=mode;mainChainMode=cm;''')
script = ''.join('var '+k+'=new Function("task","key","mode","cm","extra",'+json.dumps(v)+');'
                 for k,v in sources.items())
script += r'''
var checks=0, changes=[], cases=[];
function check(ok,label){checks++;if(!ok)throw Error(label)}
var inventory=before('inventory');
inventory.forEach(row=>row.modes.forEach(mode=>['algorithmic','data'].forEach(cm=>{
 const a=before('name',row.key,mode,cm),b=after('name',row.key,mode,cm);
 check(JSON.stringify(a)===JSON.stringify(b),'existing library '+row.key+'/'+mode+'/'+cm);
})));
const stems=['meth','eth','prop','but','pent','hex','hept','oct','non','dec','undec','dodec','tridec','tetradec','pentadec','hexadec','heptadec','octadec','nonadec','eicos'];
function chain(n,orders){return {types:Array(n).fill('C'),edges:Array.from({length:n-1},(_,i)=>[i+1,i+2,orders&&orders[i+1]||1])}}
function probe(extra){return after('probe','ethane','condensed','algorithmic',extra)}
function exact(extra,name,label){const a=probe(extra);check(a.en===name,label+': '+a.en);check(!/[\u0370-\u03ff\u1f00-\u1fff]/.test(a.en),'fully English '+label);cases.push({label,gr:a.name,en:a.en,chain:a.chain.length,boxes:a.boxes});return a}
for(let n=1;n<=20;n++){
 const a=exact(chain(n),stems[n-1]+'ane','C'+n+' alkane');check(a.chain.length===n,'parent C'+n);
 if(n===9)check(a.name==='εννεάνιο','preserved Greek nonane');
 if(n>=2)for(let order of [2,3])exact(chain(n,{1:order}),stems[n-1]+(n<=3?'':'-1-')+(order===2?'ene':'yne'),'C'+n+' terminal '+order);
 if(n>=4){const x=chain(n);x.types.push('C');x.edges.push([2,n+1,1]);exact(x,'2-methyl'+stems[n-1]+'ane','C'+n+' 2-methyl');}
}
for(const [n,orders,expected]of[
 [12,{2:2,10:2},'dodeca-2,10-diene'],[12,{2:3,10:3},'dodeca-2,10-diyne'],[13,{1:2,2:2,10:2},'trideca-1,2,10-triene']
])exact(chain(n,orders),expected,'numeric locants '+expected);
// Real functional-group engine paths: numeric order must also apply to suffix/prefix positions.
for(const kind of ['diol','hydroxyacid','nitro']){
 const x=chain(12);
 if(kind==='hydroxyacid'){
  x.types.push('O','O');x.edges.push([1,13,2],[1,14,1]);
 }
 for(const at of [2,10]){
  const next=x.types.length+1;
  if(kind==='nitro'){x.types.push('N','O','O');x.edges.push([at,next,1],[next,next+1,2],[next,next+2,1]);}
  else{x.types.push('O');x.edges.push([at,next,1]);}
 }
 if(kind==='nitro')x.atoms=x.types.map((el,i)=>({el,x:i,y:0,charge:el==='N'?1:(el==='O'&&i>0&&x.types[i-1]==='O'?-1:0)}));
 if(kind==='nitro'){
  const a=probe(x);check(a.name.startsWith('2,10-'),'numeric nitro Greek locants');check(a.en.startsWith('2,10-'),'numeric nitro English locants');
  cases.push({label:'numeric nitro locants; inherited English multiplier limit',gr:a.name,en:a.en,chain:a.chain.length,boxes:a.boxes});
 }else exact(x,({diol:'dodecane-2,10-diol',hydroxyacid:'2,10-dihydroxydodecanoic acid'})[kind],'numeric functional locants '+kind);
}
const inheritedNitro=chain(8);for(const at of [2,6]){const n=inheritedNitro.types.length+1;inheritedNitro.types.push('N','O','O');inheritedNitro.edges.push([at,n,1],[n,n+1,2],[n,n+2,1]);}
inheritedNitro.atoms=inheritedNitro.types.map((el,i)=>({el,x:i,y:0,charge:el==='N'?1:(el==='O'&&i>0&&inheritedNitro.types[i-1]==='O'?-1:0)}));
const inheritedBefore=before('probe','ethane','condensed','algorithmic',inheritedNitro),inheritedAfter=probe(inheritedNitro);
check(inheritedBefore.en===inheritedAfter.en&&inheritedAfter.en==='2,6-nitrooctane','nitro multiplier omission independently predates sync');
cases.push({label:'inherited nitro English multiplier before/after',before:inheritedBefore.en,after:inheritedAfter.en});
for(let n of [11,13,19,20]){
 let x=chain(n);x.types.push('O');x.edges.push([n,n+1,1]);let start=n+2;
 for(let j=0;j<n;j++){x.types.push('C');x.edges.push([j?start+j-1:n+1,start+j,1]);}
 exact(x,'1-('+stems[n-1]+'yloxy)'+stems[n-1]+'ane','C'+n+' ether groups');
 const e={types:['C','C','O','O'].concat(Array(n).fill('C')),edges:[[1,2,1],[2,3,2],[2,4,1],[4,5,1]].concat(Array.from({length:n-1},(_,i)=>[i+5,i+6,1]))};
 exact(e,stems[n-1]+'yl ethanoate','C'+n+' ester group');
}

const longParent=chain(20);
for(let j=0;j<9;j++){longParent.types.push('C');longParent.edges.push([j?20+j:10,21+j,1]);}
exact(longParent,'10-nonyleicosane','C20 parent with linear C9 group');
const branched=chain(20);
for(let j=0;j<8;j++){branched.types.push('C');branched.edges.push([j?20+j:10,21+j,1]);}
branched.types.push('C');branched.edges.push([22,29,1]);
const unknown=probe(branched);
check(unknown.name.includes('[μη υποστηριζόμενη ομάδα]'),'complex C9 group explicitly unsupported in Greek');
check(unknown.en.includes('[unsupported group]')&&!/octyl|nonyl/.test(unknown.en),'complex C9 group never false octyl/nonyl');
cases.push({label:'unsupported complex C9 group',gr:unknown.name,en:unknown.en,chain:unknown.chain.length,boxes:unknown.boxes});
for(let n=9;n<=20;n++){
 const x=chain(n);x.attach=0;
 check(after('longGroup',null,null,null,x)!=='[μη υποστηριζόμενη ομάδα]','supported endpoint C'+n);
 x.attach=1;check(after('longGroup',null,null,null,x)==='[μη υποστηριζόμενη ομάδα]','internal attachment declined C'+n);
 x.attach=0;x.edges[0][2]=2;check(after('longGroup',null,null,null,x)==='[μη υποστηριζόμενη ομάδα]','unsaturated alkyl declined C'+n);
}
print(JSON.stringify({completed:true,checks,libraryComparisons:844,cases,limitations:['C20 eicos spelling follows upstream CAS convention, not IUPAC preferred icos.','Greek C13/C14/C19 spelling conventions retained; polyunsaturation connector orthography not certified.','Inherited English nitro multiplicity omission persists (2,10-nitro instead of dinitro); this case verifies numeric locants only.','No external oracle or browser in this test.']}));
'''
r = subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',
    '-e','eval(JSON.parse(readline()))'], input=json.dumps(script)+'\n', text=True, capture_output=True)
assert r.returncode == 0, (r.stdout[-4000:], r.stderr[-1000:])
out=json.loads(r.stdout)
out['sourceSHA256']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in [
    'js/mulermoc-nom-core-54.js','js/mulermoc-nom-name-en-54.js','js/mulermoc-nom-iupac-54.js']}
(D/'naming-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'completed':out['completed'],'checks':out['checks'],'libraryComparisons':844,'newCases':len(out['cases'])}))
