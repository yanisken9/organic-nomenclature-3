"""Freeze consolidated Developer evidence; never modifies application files."""
from pathlib import Path
import collections,datetime,hashlib,json,os,socket,urllib.parse
HERE=Path(__file__).resolve().parent
all_results={p.parent.name:json.loads(p.read_text()) for p in sorted(HERE.glob('*/results.json'))}
data={}
for game in ['puzzle','builder','repair','author','migration','detective']:
 prefix='author-exit-run' if game=='author' else game+'-run'
 choices=[(name,d) for name,d in all_results.items() if name.startswith(prefix) and d.get('completed') and all(c['passed'] for c in d['checks'])]
 assert choices, 'Missing completed '+game
 name,d=choices[-1];data[name]=d
freeze_path=Path(os.environ['NAMELECULE_V57_FROZEN_MANIFEST'])
freeze=json.loads(freeze_path.read_text());candidate=Path(next(iter(data.values()))['candidate'])
frozen={p:(v if isinstance(v,str) else v['sha256']) for p,v in freeze['files'].items()}
assert all(hashlib.sha256((candidate/p).read_bytes()).hexdigest()==sha for p,sha in frozen.items())
for d in data.values():
 assert d['sourceBefore']==d['sourceAfter']==d['httpSourceSHA256']
 assert d['frozenFiles']==frozen
 assert all(d['sourceBefore'][p]==sha for p,sha in frozen.items())
 assert all(d.get(k) for k in ['sourceUnchangedDuringRun','ownedBrowserExited','ownedServerClosed','ownProfileRemoved'])
 assert not d['javascriptErrors']
migration=next(d for name,d in data.items() if name.startswith('migration-'))
assert migration['compatibilityPassed'] and migration['signaturesEqual'] and not migration['normalizedStepDifferences']
author=data['author-exit-run1']
assert author['exitMethod']=='Escape' and not author['afterEscape']['present'] and not author['afterEscape']['preview']
assert any(e['type']=='keydown' and e['trusted'] and e['key']=='Escape' for e in author['afterEscape']['events'])
author_control=all_results['author-run3']
assert not author_control.get('completed',False) and not author_control['authorExitAfter']['windowEvents']
assert author_control['authorExitBefore']['inner']==[1280,720] and author_control['authorExitBefore']['outer']==[1366,768]
def cleanup(p):
 def closed(port):
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.2):return False
  except OSError:return True
 try:os.kill(p['ownedPID'],0);absent=False
 except ProcessLookupError:absent=True
 except PermissionError:absent=None
 return {'pid':p['ownedPID'],'pidAbsent':absent,'profileAbsent':not Path(p['profile']).exists(),'bidiPort':p['bidiPort'],'bidiClosed':closed(p['bidiPort']),'serverPort':p['serverPort'],'serverClosed':closed(p['serverPort'])}
clean={name:cleanup(d['process']) for name,d in all_results.items() if 'process' in d}
assert all(c['pidAbsent'] and c['profileAbsent'] and c['bidiClosed'] and c['serverClosed'] for c in clean.values())
requests={}
for name,d in data.items():
 counts=collections.Counter()
 for event in d['providerDiagnostics']:
  p=event['params'];u=p.get('request',{}).get('url','')
  if not u.startswith(d['process']['baseURL']):counts[(event['method'],urllib.parse.urlsplit(u).netloc,p.get('response',{}).get('status'))]+=1
 requests[name]=[{'event':k[0],'host':k[1],'status':k[2],'count':v} for k,v in sorted(counts.items(),key=str)]
out={'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'candidate':str(candidate),'frozenManifest':str(freeze_path),'frozenManifestSHA256':hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
 'role':'Developer actual browser execution; not independent review',
 'completedRuns':{name:{'checks':len(d['checks']),'genuineCorrectUIAttempts':len(d['rounds']),'javascriptExceptions':len(d['javascriptErrors']),'sourcePaths':len(d['sourceBefore']),'sourceUnchanged':d['sourceUnchangedDuringRun'],'resultsSHA256':hashlib.sha256((HERE/name/'results.json').read_bytes()).hexdigest()} for name,d in data.items()},
 'completedChecks':sum(len(d['checks']) for d in data.values()),'genuineCorrectUIAttempts':sum(len(d['rounds']) for d in data.values()),
 'coverage':[
  'Each existing game: actual welcome → library → Main57 alkane entry; all12 lesson steps in order.',
  'Each game: gate4 and11 genuinely earned by3 distinct correct molecules in that same game; locked after first2; all3 approved branched targets solved.',
  'Each game: exact active partial answer/round/seed survive actual reload; exact required earned receipts survive reload/revalidation at both gates.',
  'Each game: one optional correct triple at gate4 preserves exact original required receipt; 3 footer actions, hidden duplicate headers, actual distinct-game switch, optional header Continue and final footer Continue.',
  'Desktop1440×1000 and solved gate11 resize390×844; page/frame width and actual Continue to12.',
  'Supporting original author runs pass6 assertions including actual step5 rehearsal through gate11 to12 and no stored learner receipt, then stop at Exit pointer dispatch. Separate completed bounded diagnostic verifies trusted Escape Exit and normal card Play restores learner gate4 without earning a receipt.',
  'Same tab/origin Main56 genuine Puzzle partial →57, normalized steps/content signatures equal; return56, complete genuine3 distinct molecules →57step5; exact earned receipt preserved.',
  'Preserved Detective: actual native56 isolated child; empty rejected; expected ethane atoms1/2 picked with trusted pointer input; production Check accepted; clear removes answer.',
  'Canonical APIs/bridge data are read-only oracles choosing trusted pointer input; no fabricated callback, storage receipt, solved flag, progress or molecular selection setter.',
  'Every completed run: exact frozen17 paths plus existing source dependencies match filesystem/HTTP before/after.'
 ],
 'originalUnitRunner':'run_all.py stopped at author-run1; original failure retained in unit-run.json. Targeted diagnostics/corrections and remaining cases ran sequentially afterward. Full original author pointer sequence did not complete; bounded keyboard Exit/normal Play is the completed author case.',
 'authorInputEvidence':{'completedKeyboardDiagnostic':'author-exit-run1/results.json','beforeExit':author['beforeExit'],'afterPointer':author['afterExitClick'],'afterEscape':author['afterEscape'],'controlledPointerRun':'author-run3/results.json','controlledBefore':author_control['authorExitBefore'],'controlledAfter':author_control['authorExitAfter'],'supportingPassedTraversalAssertions':6,'supportingAssertionsCountedInCompletedChecks':False,'pointerExitVerified':False,'diagnosis':'At1440×1000 viewport, outer1366×768 and Exitpointx1394/y25 delivered zero events at preload window capture; trusted Escape exited. Controlled1280×720 inside the same outer bounds still delivered zero Exit window/document events atx1234/y25. Therefore the viewport/outer mismatch hypothesis is not sufficient or proven. Exact headless input routing cause remains unresolved; handler works via trusted Escape. No product source change.'},
 'migration':{k:migration[k] for k in ['partialPreserved','signaturesEqual','normalizedStepDifferences','earnedPreserved','earnedGateAllowsStep5','compatibilityPassed','earned56IDs']},
 'failedHarnessAttempts':{name:{'completed':d.get('completed',False),'checks':len(d.get('checks',[])),'failure':d.get('failure'),'evidence':name+'/results.json'} for name,d in all_results.items() if name not in data and not d.get('completed')},
 'cleanup':clean,'diagnostics':{'javascriptExceptionsAcrossCompletedRuns':0,'httpErrors':{name:d.get('httpErrors',[]) for name,d in data.items()},'externalRequests':requests,'stderr':'Per-run firefox.log retained; zero captured page JavaScript exceptions does not imply clean browser stderr.'},
 'harnessCorrections':{'deferredDetectiveAPI':'detective-run1 first poll raised ReferenceError before deferred API existed; typeof guard added, detective-run2 passed.','authorInput':'Three original author pointer attempts timed out; zero Exit events observed, including controlled smaller viewport. Supporting actual Escape Exit/normal Play passes; pointer route cause remains unresolved. No symptom workaround was applied to the product.','checksumAdaptation':'Six accidental SHA257 tokens from initial version substitution corrected before any browser run; actual SHA-256 function checked.'},
 'visualInspection':['puzzle-run1/gate4-earned.png','puzzle-run1/phone-gate11-earned.png','builder-run1/gate11-earned.png','repair-run1/gate11-earned.png','author-run3/author-preview-step5.png','author-exit-run1/learner-gate-after-author-exit.png','detective-run2/detective-native56-correct.png'],
 'limits':['Owned headless Firefox, temporary loopback origin and new profiles; no personal/GUI Firefox, public deployment, physical phone or conference-machine qualification.','Author Exit pointer input remains unverified: no events reached window/document in three attempts, even1280×720 within actual outer1366×768. Exact input routing cause unresolved; trusted Escape Exit and normal Play/gating are verified.','Phone check is solved-state resize/Continue, not fresh full construction or touch/pen.','Live font/PubChem/vendor dependencies retained; no offline/uncached/uninterrupted-operation guarantee.','Native57 2D/3D picking, source/generation ownership, chemistry and broad framing verification belong to separate root evidence.','Detective coverage intentionally bounded to one genuine answer because its prototype source and pinned native56 child are preserved.'],
 'ownedChanges':'Only scripts/evidence in this browser directory and task-owned temporary resources. No application/core/scenario/game source, shared notes, Git stage/commit/push or publication changed by this worker.'}
(HERE/'summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
manifest={p.relative_to(HERE).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='manifest.json'}
(HERE/'manifest.json').write_text(json.dumps({'recordedUTC':out['recordedUTC'],'files':manifest,'cutoff':'All current browser scripts/logs/results/screenshots/summary; excludes manifest itself.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':out['completedChecks'],'genuineCorrectUIAttempts':out['genuineCorrectUIAttempts'],'files':len(manifest),'summarySHA256':hashlib.sha256((HERE/'summary.json').read_bytes()).hexdigest()}))
