"""Read-only build() recomputes evidence. Main writes summary.json only."""
from pathlib import Path
import json,gzip,zipfile,hashlib,struct
here=Path(__file__).resolve().parent

def build():
 read=lambda n:json.loads(gzip.decompress((here/(n+'.json.gz')).read_bytes()))
 causal=read('causal');assert causal['completed'] and len(causal['cases'])==20
 groups=[];expected={'raf':'updateJS','resize':'setScreenDimension','entryAfterDestroy':'setScreenDimension','lateDeliveredFrame':'updateJS','resizeAfterDestroy':'setScreenDimension'}
 for kind,signature in expected.items():
  for version in ['baseline','candidate']:
   rows=[r for r in causal['cases'] if r['kind']==kind and r['version']==version];assert len(rows)==2
   for r in rows:
    assert r['pageWork']=={'raf':True,'timer':True}
    messages=[e['text'] for e in r['javascriptErrors']]+([r['caught']]if r['caught']else[])
    if version=='baseline':assert any(signature in m for m in messages)
    else:assert not messages
   groups.append({'kind':kind,'version':version,'repeats':2,'failedCases':sum(bool(r['javascriptErrors']or r['caught'])for r in rows),'uncaughtExceptions':sum(len(r['javascriptErrors'])for r in rows),'caughtExceptions':sum(bool(r['caught'])for r in rows)})
 lessons=read('lessons');assert lessons['completed']and len(lessons['lessons'])==28 and not lessons['javascriptErrors']
 baseline=lessons['lessons'][:14];candidate=lessons['lessons'][14:]
 for a,b in zip(baseline,candidate):
  assert a['lesson']==b['lesson']and a['version']=='baseline'and b['version']=='candidate'
  assert a['exitToLibrary']and b['exitToLibrary']and a['terminal3D']['atoms']==b['terminal3D']['atoms']
  assert a['terminal3D']['file'].split('/mols/')[1]==b['terminal3D']['file'].split('/mols/')[1]
  assert len(a['steps'])==len(b['steps'])==5
  for x,y in zip(a['steps'],b['steps']):
   for k in ['index','key','mode','name','analysisMode','numberCount']:assert x[k]==y[k],(a['lesson'],k)
 active=[]
 for version in ['baseline','candidate']:
  d=read('active-flows-'+version);assert d['completed']and len(d['flows'])==3 and not d['javascriptErrors']
  assert all(r['atoms']==37 and r['model']['models'][0]['file']==r['expected']for r in d['flows'])
  assert d['toggleResize']['atoms']==37 and not d['toggleResize']['javascriptErrors']
  active.append({'version':version,'selectionClicks':12,'rapidSequences':3,'hideShowAndResize':True,'errors':0,'finalAtoms':37})
 ownership=json.loads((here/'ownership.json').read_text());assert ownership['passed']
 video=read('video-evidence');assert video['completed']and len(video['caseResults'])==3
 assert all(r['counts']=={'baseline':1,'candidate':0}for r in video['caseResults'])
 frames=json.loads((here/'video-frame-manifest.json').read_text());assert len(frames)==video['frames']==105
 with zipfile.ZipFile(here/'video-frames.zip')as z:
  assert set(z.namelist())=={r['file']for r in frames}
  for r in frames:
   data=z.read(r['file']);assert hashlib.sha256(data).hexdigest()==r['SHA256'];assert struct.unpack('>II',data[16:24])==(1280,800)
 verification=json.loads((here/'video-verification.json').read_text());assert verification['encodedFrames']==verification['decodedFrames']==105
 assert verification['allSourceTimestampsPresent']and verification['readCompleted']
 assert verification['width']==1280 and verification['height']==800
 assert abs(verification['sourceTimestampOffset']-frames[0]['seconds'])<1e-9
 assert abs(verification['durationSeconds']-(frames[-1]['seconds']-frames[0]['seconds']+.4))<.002
 assert (here/'jsmol-before-after.mp4').stat().st_size==verification['fileBytes']
 watch=json.loads((here/'watch-browser.json').read_text());assert watch['completed']and not watch['javascriptErrors']and watch['seeks']==[4,12,20]
 return {'scope':'Isolated JSmol lifecycle prototype; production source unchanged; not integrated','causal':groups,'unrelatedPageRAFAndTimerPreserved':True,'mockedOwnershipUnit':ownership,'lessonCoverage':{'versions':2,'lessonsPerVersion':14,'states':140,'libraryExits':28,'correctTerminalModels':28,'errors':0,'pairedStateAndFinalAtomCountsEqual':True,'full337Steps':False},'activeFlows':active,'video':{'sourceFrames':105,'seconds':verification['durationSeconds'],'dimensions':[1280,800],'bytes':verification['fileBytes'],'cases':video['caseResults'],'fullDecodeCompleted':True,'allSourceTimestampsPresent':True,'browserPlaybackAndSeeks':True,'method':'Sequential actual Firefox viewport captures at approximately5fps, monotonic times normalized by first capture; no generated intermediate frames. Controlled illustration, not a claimed Main crash.'},'limitations':['Firefox/macOS/currentCDN j2s only; other browsers/offline not certified','No complete lesson replay, all141-model 3D audit, camera/selection/numbering pixel certification or conference rehearsal','Two-owner isolation uses mocked unit, not two live Jmol engines','Initial model-ready/hidden-load-zap behavior not changed','No production integration, core/MOL/React change, commit or publication']}

if __name__=='__main__':
 (here/'summary.json').write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n');print('Evidence checks passed; summary written')
