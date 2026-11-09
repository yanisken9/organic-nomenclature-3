"""Summarize stored evidence; importing/build() does not write or run a browser."""
from pathlib import Path
import json,gzip,collections
here=Path(__file__).resolve().parent

def build():
 def read(n):return json.loads(gzip.decompress((here/(n+'.json.gz')).read_bytes()))
 datasets={n:read(n) for n in ['reproduction','faithful-exit','slow-load','slow-settle','controlled-teardown','active-flows']}
 assert all(d['completed'] for d in datasets.values())
 result={'scope':'Read-only Main-source investigation; isolated Firefox/macOS; no production fix','navigation':{}}
 for name in ['reproduction','faithful-exit','slow-load','slow-settle']:
  d=datasets[name];errors=d['javascriptErrors'];life=[]
  for e in d['bidiEvents']:
   t=e.get('params',{}).get('text','')
   if t.startswith('LIFE '):life.append(json.loads(t[5:]))
  classified=[]
  for e in errors:
   matches=[x for x in life if x['kind']=='error' and abs(x['date']-e['timestamp'])<=2 and x['departing'] and not x['state']['viewer']]
   assert matches,(name,e['text'])
   x=min(matches,key=lambda x:abs(x['date']-e['timestamp']))
   destroy=[v for v in life if v['epoch']==x['epoch'] and v['kind']=='Jmol._destroy:after' and v['date']<=x['date']]
   assert destroy
   classified.append({'errorTime':e['timestamp'],'epoch':x['epoch'],'millisecondsAfterDestroy':x['date']-destroy[-1]['date']})
  result['navigation'][name]={'runs':len(d['runs']),'states':sum(len(r['steps']) for r in d['runs']),'errors':len(errors),'errorSignatures':dict(collections.Counter(e['text'] for e in errors)),'errorTiming':classified,'firstTerminalAtoms':[r['settled']['atoms'] for r in d['runs']]}
 d=datasets['slow-settle'];assert len(d['runs'])==6
 later=[r['snapshot'] for run in d['runs'] for r in run['later']]
 assert len(later)==24 and all(r['atoms']==37 and r['model']['models'][0]['file']==r['expected'] for r in later)
 zaps=[sum(e['kind']=='loadStructCallback' and e['state']['step']==23 and e['detail']['args'][2]=='zapped' for e in run['events']) for run in d['runs']]
 result['settlement']={'samples':len(later),'allFinalAtoms37AndExpectedFile':True,'cumulativeWaitSeconds':[.1,.5,1.5,3.0],'lateZapCallbacksAtFinalVisibleStepPerRun':zaps,'note':'The one immediate empty read in slow-load was not itself followed to recovery; six separate follow-up runs settled correctly.'}
 cases=datasets['controlled-teardown']['cases'];assert len(cases)==8
 result['controlledTeardown']=[]
 for kind in ['raf','resize']:
  for cancel in [False,True]:
   rows=[r for r in cases if r['kind']==kind and r['cancelPending']==cancel];assert len(rows)==2
   counts=[len(r['javascriptErrors']) for r in rows];assert counts==([0,0] if cancel else [1,1])
   result['controlledTeardown'].append({'kind':kind,'cancelPending':cancel,'repeats':2,'errorCounts':counts})
 d=datasets['active-flows'];assert len(d['flows'])==3
 for r in d['flows']:
  assert r['atoms']==37 and r['model']['models'][0]['file']==r['expected'] and not r['javascriptErrors']
 assert d['toggleResize']['atoms']==37 and not d['toggleResize']['javascriptErrors'] and not d['javascriptErrors']
 result['activeFlows']={'rapidFourMoleculeSequences':3,'selectionClicks':12,'toggleHideShow':True,'resizeWidths':[900,1500],'errors':0,'finalAtoms':37,'environment':d['environment']}
 result['initialDiagnosticFailure']={'file':'reproduction-initial-preload-failure.json.gz','cause':'Incorrect preload functionDeclaration syntax','errors':3,'applicationRegression':False}
 result['limits']=['Instrumentation may change timing; measured frequencies are not estimates','No permanent blank active-page failure reproduced','Cannot retrospectively attribute all older audit errors without lifecycle timestamps','One focused lesson, not all14 lessons/337steps','Safari/other browsers, offline, intended-machine cold rehearsal and BFCache Back/Forward not tested','Cancellation only diagnostic and owned-work-specific; no production implementation','No 2D/core/React/MOL edits or chemical certification']
 return result

if __name__=='__main__':
 result=build();(here/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Stored-evidence assertions pass; summary.json written')
