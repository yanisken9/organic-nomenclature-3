from pathlib import Path
import ast,json,subprocess,hashlib
H=Path('docs/checks/v54-sync-20261104');tree=ast.parse((H/'core/test-core54.py').read_text());c={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['PREFIX','TAIL']}
data=Path('js/jsme-nick-nomeclature-moc2-data_54.js').read_text();core=Path('js/mulermoc-nom-core-54.js').read_text();old=(H/'nonane-before-mulermoc-nom-core-54.js').read_text()
assert core==old.replace('"οκτ", "εν", "δεκ"','"οκτ", "εννε", "δεκ"')
code='var A=new Function("key","mode","cm","task","extra",'+json.dumps(c['PREFIX']+data+old+c['TAIL'])+');var B=new Function("key","mode","cm","task","extra",'+json.dumps(c['PREFIX']+data+core+c['TAIL'])+');var inv=A(null,null,null,"inventory"),n=0,changes=[];inv.forEach(r=>r.modes.forEach(m=>["algorithmic","data"].forEach(cm=>{var a=A(r.key,m,cm,"name"),b=B(r.key,m,cm,"name");n++;if(JSON.stringify(a)!==JSON.stringify(b))changes.push({key:r.key,mode:m,cm,before:a,after:b});})));print(JSON.stringify({checks:n,changes}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True)
assert r.returncode==0,(r.stdout[-1000:],r.stderr[-300:]);out=json.loads(r.stdout);assert out['checks']==844 and not out['changes'],out
out['finalCoreSHA256']=hashlib.sha256(core.encode()).hexdigest();(H/'final-parent-stem-library-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
