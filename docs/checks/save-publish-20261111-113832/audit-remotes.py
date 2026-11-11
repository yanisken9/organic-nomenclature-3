from pathlib import Path
import json,urllib.request,hashlib,difflib,datetime
here=Path(__file__).resolve().parent
headers={'User-Agent':'Namelecule-save-review','Accept':'application/vnd.github+json'}
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30)as r:return r.read()
def api(path):return json.loads(get('https://api.github.com/'+path))
repo='nick-charistos/organic-nomenclature-3';head=api('repos/'+repo+'/commits/HEAD')['sha'];last='2c3f74f6c110400154efb6001657a3e514b97a70';synced='5ab2495575bbbffeb0ac67f91d4d81857cb65970'
comp=api('repos/'+repo+'/compare/'+synced+'...'+head);since=api('repos/'+repo+'/compare/'+last+'...'+head)
current=get('https://raw.githubusercontent.com/'+repo+'/'+head+'/docs/CHANGELOG.md');prior=get('https://raw.githubusercontent.com/'+repo+'/'+synced+'/docs/CHANGELOG.md')
(here/'professor-changelog.diff').write_text(''.join(difflib.unified_diff(prior.decode().splitlines(True),current.decode().splitlines(True),fromfile=synced,tofile=head)))
(here/'professor-head-changelog.txt').write_bytes(current)
origin='yanisken9/organic-nomenclature-3';public=api('repos/'+origin+'/commits/thesis-work')['sha'];runs=api('repos/'+origin+'/actions/runs?per_page=6')
r={'checkedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'lastActuallySynchronized':synced,'lastCheckedBefore':last,'upstreamHEAD':head,'commitsSinceSync':comp['total_commits'],'newSinceLastCheck':since['total_commits'],'newCommits':[{'sha':c['sha'],'message':c['commit']['message'].splitlines()[0]}for c in since['commits']],'changedSinceSync':[f['filename']for f in comp['files']],'changelogSHA256':hashlib.sha256(current).hexdigest(),'remoteReadSucceeded':True,'integratedThisSave':False,'publicHEAD':public,'recentPagesRuns':[{k:r.get(k)for k in ['id','name','head_sha','status','conclusion','created_at','html_url']}for r in runs['workflow_runs']]}
(here/'upstream-and-public-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:r[k]for k in ['upstreamHEAD','commitsSinceSync','newSinceLastCheck','newCommits','publicHEAD','recentPagesRuns']},ensure_ascii=False))
