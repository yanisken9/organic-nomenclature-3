"""One consolidated sequential verification unit. Never concurrent browsers."""
from pathlib import Path
import datetime,json,os,subprocess,sys
HERE=Path(__file__).resolve().parent
assert os.environ.get('NAMELECULE_V57_BROWSER_READY')=='frozen', 'Root frozen-target/browser permission required'
assert Path(os.environ['NAMELECULE_V57_FROZEN_MANIFEST']).is_file()
runs=[('puzzle','replay.py'),('builder','replay.py'),('repair','replay.py'),('author','replay.py'),('migration','migration.py'),('detective','detective.py')]
out={'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sequential':True,'runs':[]}
for name,script in runs:
 run=name+'-run1'
 env=dict(os.environ,NAMELECULE_V57_GAME='puzzle' if name=='migration' else name,NAMELECULE_V57_RUN=run,PYTHONUNBUFFERED='1')
 print('START '+run,flush=True)
 with (HERE/(run+'-driver.log')).open('x') as log:
  proc=subprocess.run([sys.executable,'-B',str(HERE/script)],env=env,stdout=log,stderr=subprocess.STDOUT)
 item={'run':run,'script':script,'exitCode':proc.returncode}
 result=HERE/run/'results.json'
 if result.exists():
  d=json.loads(result.read_text());item.update(completed=d.get('completed',False),checks=len(d.get('checks',[])),correctUIAttempts=len(d.get('rounds',[])),cleanup=all(d.get(k,False) for k in ['ownedBrowserExited','ownedServerClosed','ownProfileRemoved']))
 out['runs'].append(item);(HERE/'unit-run.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(item),flush=True)
 if proc.returncode or not item.get('completed') or not item.get('cleanup'):sys.exit(1)
out['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();out['completed']=True
(HERE/'unit-run.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
