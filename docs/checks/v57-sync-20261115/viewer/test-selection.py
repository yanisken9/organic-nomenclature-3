from pathlib import Path
import re,json,subprocess,hashlib,datetime
H=Path(__file__).parent
V=Path('/private/tmp/namelecule-v57-sync-20261115-l4r9e5_s/candidate/js/mulermoc-nom-molview-57.js')
C=V.with_name('mulermoc-nom-core-57.js')
U=H.parent/'upstream/target/js/mulermoc-nom-molview-57.js'
def fn(src,name):
 matches=list(re.finditer(r'^(?:async )?function (\w+)\(',src,re.M));i=next(i for i,m in enumerate(matches) if m[1]==name)
 return src[matches[i].start():matches[i+1].start() if i+1<len(matches) else len(src)]
core=C.read_text(); viewer=V.read_text(); upstream=U.read_text()
common='\n'.join(fn(core,n) for n in ['fMolCountsLine','fParseMolV2000','fWriteMolV2000','fIsHeavyEl2D','fHeavyAdj2D3D','fOrderOf2D3D','fBuildHeavyMap2D3D','fTranslateChain2D3D'])
common+='\n'+'\n'.join(fn(viewer,n) for n in ['fMulerSelectState','fMulerSelectActive','fMulerSelectMolKey','fMulerSelectPresenting','fMulerQuizHydrogenParent'])
common+='\nfunction fFindBondIndexByAtoms(a,b){return bondList.findIndex(t=>(t[0]===a+1&&t[1]===b+1)||(t[0]===b+1&&t[1]===a+1));}\n'
selection=viewer[viewer.index('// The live applet and'):viewer.index('// Quiz target registry (v56')]
legacy=fn(upstream,'fMulerSelectToggle')+upstream[upstream.index('function fMulerHeavyMapCached()'):upstream.index('// Quiz target registry (v56')]
payload={'reviewBeforePaint':fn((H/'before-REV57-1.js').read_text(),'fMulerSelectPush3D'),'common':common,'after':selection,'before':legacy,'functions':{n:fn(viewer,n) for n in ['fMulerSelectClear','fLoadMol3D','fFetchAndParse3D','fJSmolScript','fJSmolScriptWait','fMulerSelect3DSilentSettle','fMulerSelectBind3DClear','fMulerSelectPushState']},'viewerSHA256':hashlib.sha256(V.read_bytes()).hexdigest(),'coreSHA256':hashlib.sha256(C.read_bytes()).hexdigest(),'upstreamSHA256':hashlib.sha256(U.read_bytes()).hexdigest()}
(H/'actual-functions.json').write_text(json.dumps(payload,indent=2)+'\n')
r=subprocess.run(['node',str(H/'test-selection.js')],text=True,capture_output=True)
(H/'test-output.txt').write_text(r.stdout+r.stderr)
print(r.stdout);print(r.stderr)
report={'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':'python3 docs/checks/v57-sync-20261115/viewer/test-selection.py','exitCode':r.returncode,**{k:v for k,v in payload.items() if k.endswith('SHA256')},'scope':'Actual extracted production functions, deterministic DOM/applet/timer/source doubles. Before is actual raw upstream57. No browser execution or optimizer convergence claimed.','output':r.stdout,'limits':['Actual native UI/browser checks delegated to primary','Live JSmol JavaScript tail confirmed separately by primary; this harness controls the completion callback','Stereo/query correspondences intentionally fail closed; no universal formal correspondence claimed']}
(H/'deterministic-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
if r.returncode:raise SystemExit(r.returncode)
