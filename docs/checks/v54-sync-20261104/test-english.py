from pathlib import Path
import ast,json,subprocess,hashlib
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104'
tree=ast.parse((HERE/'core/test-core54.py').read_text())
constants={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['PREFIX','TAIL']}
data=(ROOT/'js/jsme-nick-nomeclature-moc2-data_54.js').read_text()
core=(ROOT/'js/mulermoc-nom-core-54.js').read_text()
suffix=constants['TAIL'].split('selectedMol=key;')[0]+'''selectedMol=key;mode2D='condensed';mainChainMode='algorithmic';load(window.MOL2D[key].condensed);fInitNamingProps();fGuessName();const en=fPopulateEngineENFromGreek(key),b=fNameENBoxes();return {key,en,box:b?b.boxes.map(([id,t])=>t+(id===b.spaceAfter?' ':'')).join(''):null};'''
results={}
for label,path in [('before',Path('/tmp/namelecule-sync-preflight-20261104/head/js/mulermoc-nom-name-en-54.js')),('after',ROOT/'js/mulermoc-nom-name-en-54.js')]:
    source=constants['PREFIX']+data+core+path.read_text()+suffix
    inventory=constants['PREFIX']+data+';return Object.keys(nameExamples);'
    code='var run=new Function("key",'+json.dumps(source)+');var keys=new Function('+json.dumps(inventory)+')();print(JSON.stringify(keys.map(k=>run(k))));'
    p=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True)
    assert p.returncode==0,(p.stdout[-2000:],p.stderr[-1000:])
    rows=json.loads(p.stdout)
    results[label]={'records':len(rows),'rendered':sum(x['box']is not None for x in rows),'mismatches':[x for x in rows if x['box']is not None and x['en']!=x['box']],'rows':rows,'sourceSHA256':hashlib.sha256(path.read_bytes()).hexdigest()}
assert len(results['before']['mismatches'])==7,results['before']['mismatches']
assert not results['after']['mismatches'],results['after']['mismatches']
(HERE/'english-box-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:{n:v for n,v in row.items()if n!='rows'}for k,row in results.items()},ensure_ascii=False))
