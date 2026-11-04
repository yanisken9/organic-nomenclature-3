from pathlib import Path
import ast,json,subprocess,hashlib
HERE=Path('docs/checks/v54-sync-20261104');tree=ast.parse((HERE/'core/test-core54.py').read_text())
c={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['PREFIX','TAIL']}
paths=['js/jsme-nick-nomeclature-moc2-data_54.js','js/mulermoc-nom-core-54.js','js/mulermoc-nom-name-en-54.js']
s=c['PREFIX']+''.join(Path(p).read_text()for p in paths)+c['TAIL'].split('selectedMol=key;')[0]+'''
let rows=[];for(const n of [8,9,10])for(const order of [1,2,3]){
 selectedMol='custom_probe';nameExamples[selectedMol]={};mode2D='condensed';mainChainMode='algorithmic';
 const types=Array.from({length:n},(_,i)=>({el:'C',x:i,y:0})),edges=Array.from({length:n-1},(_,i)=>[i+1,i+2,i===0?order:1]);
 load(fWriteMolV2000([],types,edges));fInitNamingProps();fGuessName();let en=fPopulateEngineENFromGreek(selectedMol), b=fNameENBoxes();
 rows.push({n,order,gr:currentMolName,en,boxes:b.boxes.map(([id,t])=>t+(id===b.spaceAfter?' ':'')).join('')});
}return rows;
'''
code='print(JSON.stringify(new Function('+json.dumps(s)+')()));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True)
assert r.returncode==0,(r.stdout[-1200:],r.stderr[-500:]);rows=json.loads(r.stdout)
for x in rows:
 assert x['gr'].removeprefix('1-').startswith({8:'οκτ',9:'εννε',10:'δεκ'}[x['n']]),x
 assert x['en']==x['boxes'],x
 assert x['en'].startswith({8:'oct',9:'non',10:'dec'}[x['n']]),x
assert rows[3]['gr']=='εννεάνιο'and rows[3]['en']=='nonane',rows[3]
assert 'έν' in rows[4]['gr']and'en'in rows[4]['en'],rows[4]
out={'checks':len(rows),'rows':rows,'hashes':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in paths}}
(HERE/'nonane-stem-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
