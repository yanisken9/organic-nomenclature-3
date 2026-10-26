"""Read-only v51 migration checks against the task snapshot and pinned upstream."""
from pathlib import Path
from html.parser import HTMLParser
import json,hashlib,subprocess
base=Path('/tmp/namelecule-before-v51-20261026');up=Path('/tmp/namelecule-upstream-v51')
hashes=json.loads((base/'baseline-hashes.json').read_text());allowed={'design/welcome-proposal.html','design/theory-library.html','js/ui-icons.js','README.md','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=[]
for p,h in hashes.items():
 if p in allowed:continue
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p;protected.append(p)
exact=['js/mulermoc-nom-core-51.js','js/mulermoc-nom-note-51.js','css/jsme-nick-51.css','css/mulermoc-nom-scenario-51.css']
for p in exact:assert Path(p).read_bytes()==(up/p).read_bytes(),p
for p in (up/'js/vendor').rglob('*'):
 if p.is_file():assert p.read_bytes()==Path(p.relative_to(up)).read_bytes(),str(p)
class Assets(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for k,a in attrs:
   if k in ('src','href') and a and not a.startswith(('https:','http:','#')):assert Path(a.split('?')[0]).exists(),a
Assets().feed(Path('mulermoc-nom-51.html').read_text())
html=Path('mulermoc-nom-51.html').read_text();assert 'snap.svg' not in html.lower() and 'mulermoc-nom-note-51.js' in html
code='var before=new Function("var window={};"+'+json.dumps(Path('js/jsme-nick-nomeclature-moc2-data_50.js').read_text())+'+";return {examples:nameExamples,MOL2D:window.MOL2D};"),after=new Function("var window={};"+'+json.dumps(Path('js/jsme-nick-nomeclature-moc2-data_51.js').read_text())+'+";return {examples:nameExamples,MOL2D:window.MOL2D};");var a=before(),b=after();if(JSON.stringify(a)!==JSON.stringify(b))throw Error("data mismatch");print(JSON.stringify({molecules:Object.keys(b.examples).length,identicalMetadataAndMOL:true}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr)
print(json.dumps({'protectedUnchangedFiles':len(protected),'exactUpstream':exact,'core51SHA256':hashlib.sha256(Path(exact[0]).read_bytes()).hexdigest(),'data':json.loads(r.stdout),'HTMLAssetsResolve':True,'noSnapDependency':True},ensure_ascii=False,indent=2))
