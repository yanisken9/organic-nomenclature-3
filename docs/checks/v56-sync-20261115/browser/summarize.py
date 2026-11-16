"""Freeze the bounded candidate56 browser evidence; no application writes."""
from pathlib import Path
import collections, datetime, hashlib, json, os, socket, urllib.parse

HERE=Path(__file__).resolve().parent
NAMES=['puzzle-run3','builder-run1','repair-run2','author-run3']
data={name:json.loads((HERE/name/'results.json').read_text()) for name in NAMES}
assert all(d.get('completed') and all(c['passed'] for c in d['checks']) for d in data.values())
freeze=json.loads((HERE.parent/'verification-target.json').read_text())
candidate=Path(freeze['candidate'])
frozen={p:hashlib.sha256((candidate/p).read_bytes()).hexdigest() for p in freeze['files']}
assert frozen==freeze['files']
for d in data.values():
 assert d['sourceBefore']==d['sourceAfter']==d['httpSourceSHA256']
 assert all(d['sourceBefore'][p]==sha for p,sha in freeze['files'].items())
 assert d['ownedBrowserExited'] and d['ownedServerClosed'] and d['ownProfileRemoved']
 assert not d['javascriptErrors']

def cleanup(p):
 def closed(port):
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.2):return False
  except OSError:return True
 try:os.kill(p['ownedPID'],0);absent=False
 except ProcessLookupError:absent=True
 except PermissionError:absent=None
 return {'pid':p['ownedPID'],'pidAbsent':absent,'profileAbsent':not Path(p['profile']).exists(),
  'bidiPort':p['bidiPort'],'bidiClosed':closed(p['bidiPort']),
  'serverPort':p['serverPort'],'serverClosed':closed(p['serverPort'])}

all_results={p.parent.name:json.loads(p.read_text()) for p in HERE.glob('*/results.json')}
clean={name:cleanup(d['process']) for name,d in all_results.items() if 'process' in d}
assert all(c['pidAbsent'] and c['profileAbsent'] and c['bidiClosed'] and c['serverClosed'] for c in clean.values())
requests={}
for name,d in data.items():
 counts=collections.Counter()
 for e in d['providerDiagnostics']:
  p=e['params'];u=p.get('request',{}).get('url','')
  if not u.startswith(d['process']['baseURL']):
   counts[(e['method'],urllib.parse.urlsplit(u).netloc,p.get('response',{}).get('status'))]+=1
 requests[name]=[{'event':k[0],'host':k[1],'status':k[2],'count':v} for k,v in sorted(counts.items(),key=str)]

def differences(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  return sum((differences(a.get(k),b.get(k),path+'/'+str(k)) for k in sorted(set(a)|set(b))),[])
 if isinstance(a,list) and isinstance(b,list):
  return sum((differences(a[i] if i<len(a) else None,b[i] if i<len(b) else None,path+'/'+str(i)) for i in range(max(len(a),len(b)))),[])
 return [] if a==b else [{'path':path,'before':a,'after':b}]

partial=data['repair-run2']['partialRestore']
out={
 'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'passed':True,'candidate':str(candidate),'reviewedCandidateFreeze':'../verification-target.json',
 'completedRuns':{name:{'checks':len(d['checks']),'correctUIAttempts':len(d['rounds']),
  'javascriptExceptions':len(d['javascriptErrors']),'sourcePaths':len(d['sourceBefore']),
  'sourceUnchanged':d['sourceUnchangedDuringRun'],'resultsSHA256':hashlib.sha256((HERE/name/'results.json').read_bytes()).hexdigest()} for name,d in data.items()},
 'completedChecks':sum(len(d['checks']) for d in data.values()),
 'genuineCorrectUIAttempts':sum(len(d['rounds']) for d in data.values()),
 'supportingCompletedRun':{'run':'author-run2','checks':10,'results':'author-run2/results.json','reason':'Passed actual pointer-observed author rehearsal after explicit complete startup, before requested focused confirmation. Its10 assertions are not added to completedChecks above.'},
 'coverage':[
  'Each game entered through actual welcome → theory library → Main56 alkane link; replayed all twelve steps in order.',
  'Each game earned its own gate4 and gate11 after three distinct correct molecules in that same game; first two results remained locked. All three approved branched targets solved in every game.',
  'Exact active partial answer, round and seed survive real page reload; earned required receipts at both gates survive revalidation.',
  'Each game completed one genuinely answered optional triple at gate4 without replacing the original required receipt.',
  'Three final actions, hidden duplicate header actions, same-game new triple, three-game chooser, actual different-game launch, optional header Continue and final footer Continue → step12.',
  'Solved gate11 resized to390×844; no horizontal page/frame overflow and actual Continue → step12. Desktop was1440×1000.',
  'Actual author-tab → step5 screen action starts transient rehearsal beyond unsolved gate4; continues through gate11 to12; Exit and normal card Play restore learner gating without a stored earned receipt.',
  'Read-only observed canonical engine/bridge loads selected trusted pointer input; no answer callback, bridge response, storage receipt, solved flag or progress injection.',
  'All35 candidate source/HTTP hashes before/after each completed run match, including17 frozen new/navigation paths and18 existing game/scenario/core55 dependencies.'
 ],
 'failedHarnessAttempts':[
  {'run':'puzzle-run1','classification':'Environment/harness startup','evidence':'puzzle-run1-driver.log','reason':'Sandbox denied localhost bind before any browser existed; escalated authorized isolated run succeeded.0 assertions, source hashes unchanged.'},
  {'run':'puzzle-run2','classification':'Harness hit-test rule','evidence':'puzzle-run2/results.json','successfulAssertions':75,'reason':'Generic helper rejected actual hit-testable sticky-header Continue at y85 above header bottom122. Corrected helper accepts actual header actions; complete run3 passed. No application change.'},
  {'run':'repair-run1','classification':'Harness whole-state equality assumption','evidence':'repair-run1/results.json','successfulAssertions':7,'reason':'Entire game equality was too broad: unchanged restore resets unused future rounds with randomized choiceOrder. Original before state was not captured; corrected run2 records full before/after and verifies exact active selection/choice order, seed and index. No application change.'},
  {'run':'author-run1','classification':'Incomplete harness input delivery/readiness; exact cause unisolated','evidence':'author-run1/results.json','successfulAssertions':3,'reason':'Initial unactivated author-tab input dispatch did not toggle authoring; original lacked event observations and explicit completed-startup/focus evidence. Run2 passed with explicit completed startup and observed trusted pointer events; run3 additionally activates the owned context and records document focus. No application change and no asserted causal fix.'}
 ],
 'repairRun2PartialBeforeAfterDifferences':differences(partial['before'],partial['after']),
 'sourceReferencesForFutureChoiceRandomization':['js/namelecule-generated-repair-checkpoint.js:58','js/namelecule-generated-repair-checkpoint.js:64','js/namelecule-game-repair.js:7'],
 'diagnostics':{'javascriptExceptionsAcrossCompletedRuns':0,
  'httpErrors':{name:d.get('httpErrors',[]) for name,d in data.items()},'externalRequests':requests,
  'stderr':'Retained per run: Firefox internal BiDi WeakMap warnings and macOS sandbox-extension startup warnings. Zero captured page JavaScript exceptions does not mean stderr is clean.'},
 'cleanup':clean,
 'visualInspection':['puzzle-run3/gate4-earned.png','puzzle-run3/phone-gate11-earned.png','builder-run1/gate11-earned.png','repair-run2/gate11-earned.png','author-run3/author-preview-step5.png','author-run3/learner-gate-after-author-preview.png'],
 'limits':[
  'Developer browser execution, not independent Reviewer execution.',
  'Owned headless Firefox and ephemeral localhost candidate only; no published deployment, native macOS Firefox UI, personal profile, physical device or conference-machine qualification.',
  'Phone coverage is solved-state resize/Continue, not fresh full phone construction or trusted touch/pen.',
  'Fonts and PubChem network requests succeeded during these runs; network/uncached/offline availability is not guaranteed.',
  'Broader native56 selection/chemistry/framing/author editing/3D acquisition are separate root evidence, not claimed by this game/lesson unit.'
 ],
 'ownedChanges':'Only tests and evidence beneath this browser directory; no app/core/scenario/game source, Git stage/commit/push or publication changes by this worker.'
}
(HERE/'summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
manifest={p.relative_to(HERE).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='manifest.json'}
(HERE/'manifest.json').write_text(json.dumps({'recordedUTC':out['recordedUTC'],'files':manifest,'cutoff':'Includes summary and current drivers/logs/results/screenshots; excludes this manifest itself.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':out['completedChecks'],'genuineCorrectUIAttempts':out['genuineCorrectUIAttempts'],'files':len(manifest),'summarySHA256':hashlib.sha256((HERE/'summary.json').read_bytes()).hexdigest()}))
