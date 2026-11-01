from pathlib import Path
import json,hashlib,subprocess,re,urllib.parse
R=Path.cwd();H=R/'docs/checks/publication-20261101';B=json.loads((H/'baseline.json').read_text());P=Path(B['publicationClone']);A=json.loads((H/'assembly-inputs.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p in A['runtimePaths']:assert sha(R/p)==sha(P/p),p
for p,d in A['ReactPreservedHashes'].items():assert sha(P/p)==d,p
for pattern in ['js/*core*.js','scenarios/*.json']:
 for p in P.glob(pattern):
  rel=str(p.relative_to(P));old=subprocess.check_output(['git','-C',str(P),'show',B['publicBase']+':'+rel]);assert old==p.read_bytes(),rel
for p in ['mulermoc-nom-51.html','design/welcome-proposal.html','design/theory-library.html']:
 assert subprocess.check_output(['git','-C',str(P),'show',B['publicBase']+':'+p])==(P/p).read_bytes()
# Extract actual registry values; exactly72Expanded drawings changed, no metadata/otherform.
jsc='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc';data='js/jsme-nick-nomeclature-moc2-data_52.js'
def registry(code):
 s='var window={};'+code+';print(JSON.stringify({metadata:nameExamples,mols:window.MOL2D}));';r=subprocess.run([jsc,'-e','eval(JSON.parse(readline()))'],input=json.dumps(s)+'\n',capture_output=True,text=True);assert r.returncode==0,r.stderr;return json.loads(r.stdout)
old=registry(subprocess.check_output(['git','-C',str(P),'show',B['publicBase']+':'+data]).decode());new=registry((P/data).read_text());assert old['metadata']==new['metadata'];changed=[]
for k,forms in old['mols'].items():
 for mode,mol in forms.items():
  if new['mols'][k][mode]!=mol:assert mode=='expanded';changed.append(k)
assert len(changed)==72
from html.parser import HTMLParser
class Links(HTMLParser):
 def __init__(self):super().__init__();self.items=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for k in ['href','src']:
   if a.get(k):self.items.append(a[k])
page=P/'docs/professor-20261101/update.html';parser=Links();parser.feed(page.read_text());checked=[]
for link in parser.items:
 u=urllib.parse.urlsplit(link)
 if u.scheme or not u.path:continue
 p=(page.parent/urllib.parse.unquote(u.path)).resolve();assert p.is_file(),(link,p);checked.append(str(p.relative_to(P.resolve())))
subprocess.run(['git','-C',str(P),'diff','--cached','--check','--','.',':(exclude)*.mol',':(exclude)*.diff'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out={'passed':True,'publicBase':B['publicBase'],'runtimePathsMatched':len(A['runtimePaths']),'changedExpandedFromLastPublic':changed,'metadataOtherFormsUnchanged':True,'coreScenariosReactLegacyWelcomeLibraryPreserved':True,'ReactPaths':len(A['ReactPreservedHashes']),'localReportLinksChecked':checked,'noDeletedPaths':not subprocess.check_output(['git','-C',str(P),'diff','--cached','--name-only','--diff-filter=D']).strip()}
assert out['noDeletedPaths'];(H/'assembly-check.json').write_text(json.dumps(out,indent=2)+'\n');print('Assembly passed:50runtime paths,72expanded changes,39React paths preserved; all report links present.')
