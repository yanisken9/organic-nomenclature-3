from pathlib import Path
import json,hashlib,difflib
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
b=json.loads((H/'baseline.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((H/'before/scenarios/alkanes-user-3.scenario.json').read_text());new=json.loads((R/'scenarios/alkanes-user-3.scenario.json').read_text())
assert len(new['steps'])==12
assert {k:v for k,v in old.items() if k!='steps'}=={k:v for k,v in new.items() if k!='steps'}
for i,(a,c) in enumerate(zip(old['steps'],new['steps'])):
 if i not in (3,10):assert a==c,(i,'unapproved step change');continue
 fields={'title','note','titleLogo','checkpoint'}
 assert {k:v for k,v in a.items() if k not in fields}=={k:v for k,v in c.items() if k not in fields}
 assert a['checkpoint']['id']==c['checkpoint']['id'] and a['checkpoint']['round']==c['checkpoint']['round']
 assert c['checkpoint']['type']=='alkane-game-choice-set'
core={p:sha(R/p) for p in b['coreHashes']};assert core==b['coreHashes']
changes={p:sha(R/p)for p in b['appScopePaths']};diff=''
for p,after in changes.items():
 prior=H/'before'/p
 diff+=''.join(difflib.unified_diff(prior.read_text().splitlines(True) if prior.exists() else [],(R/p).read_text().splitlines(True),fromfile='before/'+p,tofile=p))
(H/'implementation.diff').write_text(diff)
m=json.loads((R/'communication/checkpoints/alkanes-json-export-20261111-game-choice.json').read_text());assert Path(m['destination']).read_bytes()==(R/'scenarios/alkanes-user-3.scenario.json').read_bytes();assert Path(m['Desktop_recovery']).read_bytes()==(H/'before/scenarios/alkanes-user-3.scenario.json').read_bytes()
report={'passed':True,'sourceHashes':changes,'coreHashes':core,'coreChanges':False,'json':'Only gates4/11 authored fields changed; other10steps and all settings/recipes/IDs invariant','DesktopExport':'Byte-identical, dated backup equals baseline','diff':'implementation.diff'}
(H/'static-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':True,'appPaths':len(changes),'coreUnchanged':len(core),'DesktopBytesEqual':True}))
