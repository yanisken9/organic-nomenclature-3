from pathlib import Path
import re,subprocess,json,hashlib,datetime
P=Path.cwd();E=P/'docs/checks/v54-merge-20261109/viewer';C=Path('/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate')
V=C/'js/mulermoc-nom-molview-55.js';CORE=C/'js/mulermoc-nom-core-55.js';U=P/'docs/checks/v54-merge-20261109/upstream/target/js/mulermoc-nom-molview-55.js'
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def fn(src,name):
 matches=list(re.finditer(r'^(?:async )?function (\w+)\(',src,re.M));idx=next(i for i,m in enumerate(matches) if m.group(1)==name)
 return src[matches[idx].start():matches[idx+1].start() if idx+1<len(matches) else len(src)]
v=V.read_text();core=CORE.read_text();up=U.read_text()
core_names=['fMolCountsLine','fParseMolV2000','fWriteMolV2000','fRemapMolProperties2D','fMolCanTransform2D','fIsHeavyEl2D','fHeavyAdj2D3D','fOrderOf2D3D','fBuildHeavyMap2D3D','fCopyMolAtom2D','fCopyMolBond2D','fStripHydrogensMol','fGenExpandedMol','fLinearizeMol','fZigzagMol']
viewer_names=['fMolDraftNorm','fMolDraftCancel','fMolDraftAccept','fMolDraft3DCurrent','fMolDraft3DInvalidate','fMolDraft3DBegin','fMolDraft3DWillScript','fMolDraft3DWrite','fMolDraft3DLoad','fMolDraft3DWait','fMolDraftGraphMap','fMolDraftValidSDF3D','fMolDraftReadBackSDF','fMolDraftMeanDisplacement','fMolDraftLocal3DRelaxFF','fMolDraftLocal3DRelaxBoth','fMolDraftLocal3DPrepare','fMolDraftLocal3DFromMol','fMolDraft3DProvenance','fMolDraftSet3D','fMolDraftManualMinimize','fMolDraftRemote3DFromJSmol','fMolDraftFetchSDF3DTiered','fMolDraftJiggleZ','fMolDraftUntangle2D','fJSmolScript','fJSmolScriptWait','fJSmolScriptEcho','fJSmolLoadInlineSDF','fMolDraftMinWaitClose','fMolDraftMinWaitShow','fMolDraftMinWaitSecs','fMolDraftMinStopEngine','fMolDraftMinWaitAbort','fMolDraftLocal3DReloadMinimized','fSetSettingChecked','fSyncAtomColorModeRadios','fSyncViewerSettingsUI','fMolDraftDownloadSingle','fMolDraftDownloadBundle','fMolDraftMarkNewCustom','fMolDraftNewCustomKeys','fRenderMolInfo']
prelude=(E/'test-prelude.js').read_text();tests=(E/'test-cases.js').read_text()
source=prelude+'\n'+'\n'.join(fn(core,n) for n in core_names)+'\n'+'\n'.join(fn(v,n) for n in viewer_names)+'\n'+tests
(E/'actual-functions-under-test.js').write_text(source)
r=subprocess.run([JSC,'actual-functions-under-test.js'],cwd=E,capture_output=True,text=True)
(E/'actual-functions-output.txt').write_text(r.stdout+r.stderr)
print(r.stdout);print(r.stderr)
if r.returncode:raise SystemExit(r.returncode)
summary=json.loads(r.stdout.splitlines()[0])
if summary["cases"] != summary["passed"]:raise SystemExit("deterministic cases failed")
# Historical reproductions execute the exact upstream validator and nested
# relax functions with deterministic clocks/model-read mocks.
before=prelude+'\n'+'\n'.join(fn(core,n) for n in core_names[:7])+'\n'+ '\n'.join(fn(up,n) for n in ['fMolDraftValidSDF3D','fMolDraftLocal3DRelaxFF','fMolDraftLocal3DRelaxBoth','fMolDraftManualMinimize'])+'\n'+(E/'test-before.js').read_text()
(E/'upstream-before-probe.js').write_text(before)
b=subprocess.run([JSC,'upstream-before-probe.js'],cwd=E,capture_output=True,text=True)
(E/'upstream-before-output.txt').write_text(b.stdout+b.stderr);print(b.stdout);print(b.stderr)
if b.returncode:raise SystemExit(b.returncode)
report={'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime':str(V),'runtimeSHA256':hashlib.sha256(V.read_bytes()).hexdigest(),'coreDependencySHA256':hashlib.sha256(CORE.read_bytes()).hexdigest(),'comparison':'current local54 + pinned upstream f49b810/e76d3c0 plus later 5ab24955 delta; candidate HEAD29991c90','engine':'JavaScriptCore','command':'python3 docs/checks/v54-merge-20261109/viewer/test-viewer.py','exitCode':r.returncode,'beforeExitCode':b.returncode,'scope':'Actual function execution with deterministic applet/network/timer/DOM doubles; not browser or real force-field convergence evidence','output':r.stdout,'beforeOutput':b.stdout,'untested':['Real JSME/JSmol/browser/UI rendering','Live PubChem/OpenClatura/remote3D availability','Physical minimizer convergence/geometry validity','Full lesson/presentation replay; owned by primary verification']}
(E/'deterministic-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
