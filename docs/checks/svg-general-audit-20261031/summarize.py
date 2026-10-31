"""Recompute audit conclusions from final corrected evidence, never initial flags."""
from pathlib import Path
import json,gzip,collections,hashlib,statistics
here=Path(__file__).resolve().parent
read=lambda n:json.loads(gzip.decompress((here/(n+'.json.gz')).read_bytes()))
cat,ctrl,future,over,less,replay=[read(n)for n in ['catalog','controls','future','overlap-followup','lessons','corrected-replay']]
assert all(d['completed']for d in [cat,ctrl,future,over,less,replay])
assert all(x['key']==x['expectedKey']and x['mode']==x['expectedMode']for x in cat['cases'])
assert len(cat['cases'])==1266 and len(ctrl['cases'])==120 and len(future['cases'])==36 and len(over['cases'])==16 and len(less['lessons'])==28
assert len(replay['datasets']['catalog'])==1266 and len(replay['datasets']['controls'])==120 and len(replay['datasets']['overlap-followup'])==16
assert not any(d['javascriptErrors']for d in [cat,ctrl,future,over,replay])
rows=replay['datasets']['catalog'];index={(x['version'],x['width'],x['key'],x['mode']):x for x in rows};assert len(index)==1266
contacts=lambda x:x['raster']['inkWithinHalfCssPixelOfBond']>0
phase={}
for version,width in [('baseline',1500),('candidate',1500),('candidate',390)]:
 a=[x for x in rows if(x['version'],x['width'])==(version,width)];assert len(a)==422
 phase[version+'-'+str(width)]={'forms':422,'contactOrWithinHalfCssPixel':sum(contacts(x)for x in a),'formsWithFullyHiddenLine':sum(x['raster']['fullyHiddenLineCount']>0 for x in a),'clippedLabelForms':sum(bool(x['clipped'])for x in a),'bboxOverlapFlags':sum(bool(x['overlaps'])for x in a)}
base={(x['key'],x['mode']):x for x in rows if x['version']=='baseline'};candidate={(x['key'],x['mode']):x for x in rows if x['version']=='candidate'and x['width']==1500}
assert base.keys()==candidate.keys()and len(base)==422
nameDiff=[];graphDiff=[];textDiff=[];newContact=[];resolved=[];remaining=[];newHidden=[]
for k,a in base.items():
 b=candidate[k]
 if a['name']!=b['name']:nameDiff.append(k)
 if a['atomSymbols']!=b['atomSymbols']or a['bondGraph']!=b['bondGraph']:graphDiff.append(k)
 if [x['text']for x in a['atoms']]!=[x['text']for x in b['atoms']]:textDiff.append(k)
 if contacts(b)and not contacts(a):newContact.append(k)
 if contacts(a)and not contacts(b):resolved.append(k)
 if contacts(b):remaining.append(k)
 assert len(a['raster']['lineVisibility'])==len(b['raster']['lineVisibility']), (k,'line count')
 if any(y['visibleLength']==0 and x['visibleLength']>0 for x,y in zip(a['raster']['lineVisibility'],b['raster']['lineVisibility'])):newHidden.append(k)
assert not nameDiff and not graphDiff and not textDiff
controls={}
for v in ['baseline','candidate']:
 a=[x for x in replay['datasets']['controls']if x['version']==v];assert len(a)==60
 controls[v]={'cases':60,'contactOrNearCases':sum(contacts(x)for x in a),'numberCountMismatches':sum(x['expectedNumbers']!=len(x['numbers'])for x in a),'clippedCases':sum(bool(x['clipped'])for x in a)}
assert all(x['validSVG']and x['bytes']>1000 for x in ctrl['exports'])
summary={'date':'2026-10-31','scope':'main v52, isolated candidate vendor; no production change','molecules':141,'forms':422,'captureCases':1266,'finalOracle':'actual SVG character positions + Canvas glyph pixels in actual page fonts; real rounded masks and visible bond lines; 4x CSS resolution; proximity radius 0.5 CSS px','phases':phase,'desktopComparison':{'namesChanged':nameDiff,'graphsChanged':graphDiff,'labelStringsChanged':textDiff,'newContactForms':newContact,'resolvedContactForms':resolved,'remainingContactForms':remaining,'newHiddenLineForms':newHidden},'controls':controls,'exports':ctrl['exports'],'overlapFollowup':{'cases':16,'realInkOverlapPairs':sum(v['overlappingInkPixels']>0 for x in over['cases']for v in x['pairInk']),'note':'bbox flags are not glyph overlap; target baseline390 and individual glyph raster checked'},'futureInputs':{'cases':36,'unsafeShortCH':{v:sum(x['raster']['hiddenLines']>0 for x in future['cases']if x['version']==v)for v in ['baseline','candidate']},'metricsFailureInjection':future['faultInjection']},'lessons':{},'oracleValidation':{'replayedCases':sum(map(len,replay['datasets'].values())),'maxLabelBoxDelta':max(x['replayLabelBoxMaxDelta']for a in replay['datasets'].values()for x in a),'controls':replay['oracleControls'],'initialCountersSuperseded':True,'calibrationFailure':'First replay stopped on NH2 inherited-font mismatch; final page uses actual CSS/fonts and per-character pixel painting'},'limitations':['Firefox/macOS only; standard HTML soft permutation0, DPR1','No Safari/quirks renderer validation, late-font-swap validation, full337step replay or conference rehearsal','JSmol and webfonts were loaded from configured external services; offline operation not established','Fault test is injected missing metrics, not a naturally observed failure','Performance observations, if present, are fresh-page starts with warm local HTTP cache, not cold-machine benchmark']}
for v in ['baseline','candidate']:
 a=[x for x in less['lessons']if x['version']==v];assert len(a)==14
 summary['lessons'][v]={'lessons':14,'navigationStates':sum(len(x['steps'])for x in a),'exitToLibrary':sum(x.get('exitToLibrary',False)for x in a),'terminal3DPass':sum(bool(x['terminal3D'].get('file'))for x in a),'javascriptErrors':sum(len(x['javascriptErrors'])for x in a),'failures':[{'lesson':x['lesson'],'terminal3D':x['terminal3D'],'errors':len(x['javascriptErrors'])}for x in a if x['terminal3D'].get('failure')or x['javascriptErrors']]}
if (here/'startup.json').exists():
 st=json.loads((here/'startup.json').read_text());summary['startup']=st
res=read('residual-causes');assert res['completed']and not res['javascriptErrors']
summary['causalDiagnostics']={'collector':[{'version':x['version'],'collectorIncludesUnrelatedC9Mask':x['trace'][0]['collectorIncludesC9'],'contactBefore':x['before']['raster']['inkWithinHalfCssPixelOfBond'],'contactWithC9MaskPreserved':x['diagnosticPreserveC9Mask']['raster']['inkWithinHalfCssPixelOfBond']}for x in res['collector']],'acid':[{'version':x['version'],'hiddenBefore':x['before']['raster']['fullyHiddenLineCount'],'hiddenWithMeasuredInkBounds':x['diagnosticInkBounds']['raster']['fullyHiddenLineCount'],'contactAfter':x['diagnosticInkBounds']['raster']['inkWithinHalfCssPixelOfBond'],'recoveredLineCssPixels':x['diagnosticInkBounds']['raster']['lineVisibility'][-1]['visibleLength']}for x in res['acidBounds']],'dpr2':[{k:x[k]for k in ['key','mode','dpr','raster']}for x in res['dpr2']],'scope':'diagnostic DOM counterfactuals only, not proposed per-molecule fixes or production edits'}
assert all(x['collectorIncludesUnrelatedC9Mask']and x['contactWithC9MaskPreserved']==0 for x in summary['causalDiagnostics']['collector'])
assert all(x['hiddenBefore']==1 and x['hiddenWithMeasuredInkBounds']==0 and x['contactAfter']==0 for x in summary['causalDiagnostics']['acid'])
summary['productionBaselineSHA256']=hashlib.sha256((here/'production-baseline.json').read_bytes()).hexdigest()
(here/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'phases':phase,'newContact':len(newContact),'remainingContact':len(remaining),'newHidden':newHidden,'realOverlaps':summary['overlapFollowup'],'lessons':summary['lessons']},ensure_ascii=False,indent=2))
