"""Verify deployed public bytes against reviewed candidate, no source/runtime edits."""
from pathlib import Path
import json,hashlib,urllib.request,urllib.parse,time,concurrent.futures,datetime
ROOT=Path.cwd();D=ROOT/'docs/checks/publication-20261105';s=json.loads((ROOT/'communication/checkpoints/save-publish-20261105-state.json').read_text());P=Path(s['publicClone']);M=json.loads((D/'curated-source-manifest.json').read_text());BASE='https://yanisken9.github.io/organic-nomenclature-3/'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def get(name):
 req=urllib.request.Request(BASE+urllib.parse.quote(name,safe='/'),headers={'Cache-Control':'no-cache','User-Agent':'Namelecule-release-verification'})
 with urllib.request.urlopen(req,timeout=30) as response:raw=response.read();return {'path':name,'status':response.status,'SHA256':hashlib.sha256(raw).hexdigest()}
critical=['docs/professor-20261105/update.html','js/mulermoc-nom-core-54.js']
for attempt in range(48):
 try:
  if all(get(name)['SHA256']==sha(P/name)for name in critical):break
 except Exception:pass
 if attempt%4==0:print('Waiting for reviewed Pages bytes',attempt,flush=True)
 time.sleep(5)
else:raise SystemExit('Bounded deployment wait exhausted; no deployment claim')
paths=set(M['dependencyHashes'])|set(critical)|{'design/welcome-proposal.html','design/theory-library.html','games/data/name-repair-alkanes.json','scenarios/alkanes-name-repair-pilot.scenario.json','mulermoc-nom-52.html','js/mulermoc-nom-core-52.js','react-preview/dist/index.html','react-preview/dist/viewer-host.html','react-preview/dist/lesson-host.html','react-preview/preserved-main-20261030/js/jsme-nick-nomeclature-moc2-data_52.js','react-preview/preserved-main-20261030/js/mulermoc-nom-molview-52.js'}
paths.update('docs/professor-20261105/'+name for name in ['links.json','links.txt','verified-facts.json','message-to-professor.txt'])
# Explicit React build assets/bridge dependencies remain byte-preserved too.
paths.update(name for name in M['protectedFiles']if name.startswith('react-preview/dist/'))
def verify(name):
 row=get(name);row['expectedSHA256']=sha(P/name);row['matched']=row['SHA256']==row['expectedSHA256'];assert row['matched'],name;return row
rows=[]
try:
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
  for row in pool.map(verify,sorted(paths)):rows.append(row)
 out={'passed':True,'checkedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':rows,'plainURLs':True,'expectedPublicCommit':s.get('publicReleaseCommit'),'limits':'HTTP/exact bytes do not establish browser behavior, external service availability or offline reliability.'}
except Exception as error:
 out={'passed':False,'failure':str(error),'checks':rows};raise
finally:(D/'public-http.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'HTTP200ExactSHA256':len(rows)}),flush=True)
