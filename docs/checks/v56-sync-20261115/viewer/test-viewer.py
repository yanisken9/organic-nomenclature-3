from pathlib import Path
import re,subprocess,json,hashlib,datetime
E=Path(__file__).parent;old=Path('docs/checks/v54-merge-20261109/viewer');C=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate')
V=C/'js/mulermoc-nom-molview-56.js';CORE=C/'js/mulermoc-nom-core-56.js'
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def fn(src,name):
 matches=list(re.finditer(r'^(?:async )?function (\w+)\(',src,re.M));idx=next(i for i,m in enumerate(matches) if m.group(1)==name)
 return src[matches[idx].start():matches[idx+1].start() if idx+1<len(matches) else len(src)]
v=V.read_text();core=CORE.read_text()
core_names=['fMolCountsLine','fParseMolV2000','fWriteMolV2000','fRemapMolProperties2D','fMolCanTransform2D','fIsHeavyEl2D','fHeavyAdj2D3D','fOrderOf2D3D','fBuildHeavyMap2D3D','fCopyMolAtom2D','fCopyMolBond2D','fStripHydrogensMol','fGenExpandedMol','fLinearizeMol','fZigzagMol']
viewer_names=['fMolDraftNorm','fMolDraftCancel','fMolDraftAccept','fMolDraft3DCurrent','fMolDraft3DInvalidate','fMolDraft3DBegin','fMolDraft3DWillScript','fMolDraft3DWrite','fMolDraft3DLoad','fMolDraft3DWait','fMolDraftGraphMap','fMolDraftValidSDF3D','fMolDraftNormalizeJSmolReadback','fMolDraftReadBackSDF','fMolDraftMeanDisplacement','fMolDraftLocal3DRelaxFF','fMolDraftLocal3DRelaxBoth','fMolDraftLocal3DPrepare','fMolDraftLocal3DFromMol','fMolDraft3DProvenance','fMolDraftSet3D','fMolDraftManualMinimize','fMolDraftJSmolLoadAndReadBack','fMolDraftPubChem3DFromJSmol','fMolDraftRemote3DFromJSmol','fMolDraftFetchSDF3DTiered','fMolDraftJiggleZ','fMolDraftUntangle2D','fJSmolScript','fJSmolScriptWait','fJSmolScriptEcho','fJSmolLoadInlineSDF','fMolDraftMinWaitClose','fMolDraftMinWaitShow','fMolDraftMinWaitSecs','fMolDraftMinStopEngine','fMolDraftMinWaitAbort','fMolDraftLocal3DReloadMinimized','fSetSettingChecked','fSyncAtomColorModeRadios','fSyncViewerSettingsUI','fMolDraftDownloadSingle','fMolDraftDownloadBundle','fMolDraftMarkNewCustom','fMolDraftNewCustomKeys','fRenderMolInfo','fMolDraftSDF3DStatusHTML','fMolDraftEsc']
prelude=(old/'test-prelude.js').read_text();tests=(old/'test-cases.js').read_text()
tests=tests.replace('/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate/js/mulermoc-nom-molview-55.js',str(V))
# Existing page-fetch regression isolates its provider, now tier1b.
tests=tests.replace("var originalRemote=fMolDraftRemote3DFromJSmol,originalLocal=fMolDraftLocal3DFromMol;", "var originalPub=fMolDraftPubChem3DFromJSmol,originalRemote=fMolDraftRemote3DFromJSmol,originalLocal=fMolDraftLocal3DFromMol;fMolDraftPubChem3DFromJSmol=function(){return null;};")
tests=tests.replace(".source==='pubchem','correct pubchem missed');", ".source==='pubchem-fetch','correct pubchem missed');fMolDraftPubChem3DFromJSmol=originalPub;")
# Extra provider tests are inserted before suite serialization.
extra=(E/'test-new-provider.js').read_text()
tests=tests.replace('print(JSON.stringify({cases:',extra+'\nprint(JSON.stringify({cases:')
source=prelude+'\n'+'\n'.join(fn(core,n) for n in core_names)+'\n'+'\n'.join(fn(v,n) for n in viewer_names)+'\n'+tests
(E/'actual-functions-under-test.js').write_text(source)
r=subprocess.run([JSC,'actual-functions-under-test.js'],cwd=E,capture_output=True,text=True)
(E/'actual-functions-output.txt').write_text(r.stdout+r.stderr)
print(r.stdout);print(r.stderr)
report={'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime':str(V),'runtimeSHA256':hashlib.sha256(V.read_bytes()).hexdigest(),'coreDependencySHA256':hashlib.sha256(CORE.read_bytes()).hexdigest(),'engine':'JavaScriptCore','command':'python3 docs/checks/v56-sync-20261115/viewer/test-viewer.py','exitCode':r.returncode,'scope':'Actual extracted functions with deterministic applet/network/timer/DOM doubles; not browser or physical optimization evidence','output':r.stdout,'untested':['Real JSME/JSmol/browser/UI rendering','Live PubChem/OpenClatura/Cactus availability','Physical minimizer convergence/geometry validity','Full lesson/presentation replay; primary verification']}
(E/'deterministic-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
if r.returncode:raise SystemExit(r.returncode)
summary=json.loads(r.stdout.splitlines()[0]);assert summary['passed']==summary['cases']
