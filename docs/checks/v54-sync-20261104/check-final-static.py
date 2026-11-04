from pathlib import Path
import re,json,hashlib,subprocess,urllib.request
H=Path('docs/checks/v54-sync-20261104');R=Path.cwd();b=json.loads((H/'baseline.json').read_text());out={'completed':False,'checks':[]}
mods=['js/jsme-nick-nomeclature-moc2-data_54.js']+[f'js/mulermoc-nom-{x}-54.js'for x in ['core','molview','teaching','scenario','note','iupac','lang','name-en']]+['js/ui-icons-54.js']
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail})
for n in mods:
 p=Path(n);r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','checkSyntax('+json.dumps(str(p))+')'],capture_output=True,text=True)
 check(r.returncode==0,'JSC syntax '+n,r.stderr[-300:] or None)
 # Function preservation is a completeness guard, not proof of semantics.
 old=H/'upstream-snapshot'/n
 if old.exists():
  names=lambda t:set(re.findall(r'\bfunction\s+(\w+)\s*\(',t))
  missing=sorted(names(old.read_text())-names(p.read_text()))
  check(not missing,'Upstream named functions retained '+n,missing)
allowed={'README.md','docs/CHANGELOG.md','design/welcome-proposal.html','design/theory-library.html'}
changes=[]
for n,h in b['hashes'].items():
 p=Path(n);new=hashlib.sha256(p.read_bytes()).hexdigest()if p.is_file()else None
 if new!=h:changes.append(n)
check(set(changes)<=allowed,'Protected task-baseline sources unchanged',{'count':len(b['hashes']),'allowedChangesActuallyFound':changes})
check(subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==b['sourceHEAD'],'HEAD unchanged')
check(hashlib.sha256(Path('.git/index').read_bytes()).hexdigest()==b['indexSHA256'],'Git index unchanged')
trace=json.loads((H/'upstream-traceability.json').read_text());check(len(trace['paths'])==69,'69 upstream paths accounted')
for row in trace['paths']:
 check(Path(row['sourceSnapshot']).is_file(),'Source snapshot '+row['upstreamPath'])
html=re.sub(r'<!--.*?-->','',Path('mulermoc-nom-54.html').read_text(),flags=re.S);refs=re.findall(r'(?:src|href)=["\']([^"\']+)["\']',html)
local=sorted(set(x.split('?')[0].split('#')[0]for x in refs if x and not x.startswith(('http:','https:','#','data:','mailto:'))))
missing=[n for n in local if not Path(n).is_file()]
check(not missing,'HTML local dependencies exist',missing)
runtime=['mulermoc-nom-54.html',*mods,'css/jsme-nick-54.css','css/mulermoc-nom-scenario-54.css','css/namelecule-54.css','spt/init-54.spt','design/welcome-proposal.html','design/theory-library.html']
out['http']=[]
for n in runtime:
 url='http://127.0.0.1:8013/'+n+'?v=v54-final-static'
 with urllib.request.urlopen(url,timeout=20)as r:body=r.read();status=r.status
 check(status==200 and body==Path(n).read_bytes(),'HTTP200 exact bytes '+n)
 out['http'].append({'path':n,'sha256':hashlib.sha256(body).hexdigest()})
out['completed']=True;out['protectedChanges']=changes
(H/'final-static.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed':True,'checks':len(out['checks']),'protected':len(b['hashes']),'runtimeHTTP':len(runtime)}))
