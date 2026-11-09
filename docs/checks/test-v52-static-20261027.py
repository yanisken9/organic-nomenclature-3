"""Read-only v52 merge/preservation contracts; no network or generated files."""
from pathlib import Path
import ast,hashlib,json,re
from html.parser import HTMLParser
from urllib.parse import urlsplit
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
b=json.loads(Path('docs/checks/v52-before-sync-20261027.json').read_text())
allowed={'README.md','design/welcome-proposal.html','design/theory-library.html','docs/CHANGELOG.md','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md','js/ui-icons.js','react-preview/README.md','react-preview/src/content.json','react-preview/tools/build-viewer-host.py','react-preview/tools/sync-content.py'}
protected={p:h for p,h in b['files'].items() if p not in allowed}
assert all(Path(p).is_file() and sha(p)==h for p,h in protected.items())
assert Path('js/jsme-nick-nomeclature-moc2-data_52.js').read_bytes()==Path('js/jsme-nick-nomeclature-moc2-data_51.js').read_bytes()
assert Path('css/namelecule-52.css').read_bytes()==Path('css/namelecule-51.css').read_bytes()
origins={'js/mulermoc-nom-core-52.js': '72ac4b4ae3c9bfaa90fde650bf588ed6430acec9ad3ceef72a94a27ad6750e3a', 'js/mulermoc-nom-note-52.js': '95550db821fcf8d76a4c15f400bd821b9797db79089bb9c2410db44f8e6f998b', 'css/mulermoc-nom-scenario-52.css': '3333831cefab5c063a7e3e429a2c3cae2b3ed223421d7fc48037c5a46d373fbf', 'js/ui-icons.js': '41f475b9d6c95d35db5e6aa6b2ece6df9719c3ec1940b2099235aec635a56307'}
assert all(sha(p)==h for p,h in origins.items())
old=Path('js/mulermoc-nom-core-51.js').read_text()
new=Path('js/mulermoc-nom-core-52.js').read_text().replace('core-52.js','core-51.js').replace('molview-52.js','molview-51.js')
new=new.replace('    if (!Array.isArray(conn) || !Array.isArray(types) || !Array.isArray(bonds)) return false\n','')
assert new==old,'Unexpected additional naming algorithm difference'
class Refs(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in {'script','img','link'}:
   value=a.get('src') or a.get('href')
   if value and not urlsplit(value).scheme and not value.startswith('//'):self.refs.append(urlsplit(value).path)
p=Refs();p.feed(Path('mulermoc-nom-52.html').read_text())
assert all(Path(x).is_file() for x in p.refs),[x for x in p.refs if not Path(x).is_file()]
assert all('-51.' not in x and '_51.' not in x for x in p.refs)
links=re.findall(r'href="([^"]*scenario=[^"]*)"',Path('design/theory-library.html').read_text())
assert len(links)==12 and all('mulermoc-nom-52.html' in h for h in links)
paths=re.findall(r'scenario=([^&"]+)',Path('design/theory-library.html').read_text())
assert sum(len(json.loads(Path(p).read_text())['steps']) for p in paths)==283
content=json.loads(Path('react-preview/src/content.json').read_text())
assert len(content['library']['categories'])==9 and len(content['inventory']['lessonLinks'])==12
assert all('mulermoc-nom-52.html' in h for h in content['inventory']['lessonLinks'])
for p in Path('docs/checks').glob('test-v52-*.py'):ast.parse(p.read_text())
print(json.dumps({'passed':True,'baselineFiles':len(b['files']),'protectedUnchanged':len(protected),'data52EqualsChecked51':True,'theme52EqualsChecked51':True,'core52OnlyAddsUpstreamArrayGuard':True,'unalteredUpstreamFiles':origins,'localHTMLReferencesResolve':True,'lessons':12,'steps':283,'reactCards':9},ensure_ascii=False,indent=2))
