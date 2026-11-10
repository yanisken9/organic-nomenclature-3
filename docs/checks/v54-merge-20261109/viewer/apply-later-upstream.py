from pathlib import Path
P=Path.cwd();F=Path('/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate/js/mulermoc-nom-molview-55.js');s=F.read_text();u=(P/'docs/checks/v54-merge-20261109/later-upstream/target/js/mulermoc-nom-molview-55.js').read_text()
def part(t,a,b):return t[t.index(a):t.index(b,t.index(a))]
def replace(a,b,v):
 global s
 s=s[:s.index(a)]+v+s[s.index(b,s.index(a)):]
# The exact settings registry has no overlap with local viewer calibration.
reg=part(u,'// Viewer-settings registry','function fToggleViewerSettings()')
s=s.replace('function fToggleViewerSettings() {',reg+'function fToggleViewerSettings() {',1)
replace('function fToggleViewerSettings() {','// ── Stage 2',part(u,'function fToggleViewerSettings() {','// ── Stage 2')) if '// ── Stage 2' in s and '// ── Stage 2' in u else None
# Replace the earlier save-OK overlay with the new wait/countdown UI.
wait=part(u,'// Blocking wait window','// Halt a possibly in-flight minimize')
wait=wait.replace('var fMolDraftMinWaitTimer = null;','var fMolDraftMinWaitTimer = null;\nvar fMolDraftMinWaitJob = null;')
wait=wait.replace('function fMolDraftMinWaitClose() {','function fMolDraftMinWaitClose(job) {\n  if (job && fMolDraftMinWaitJob !== job) return;\n  fMolDraftMinWaitJob = null;')
wait=wait.replace('function fMolDraftMinWaitShow(onCancel, totalS) {','function fMolDraftMinWaitShow(onCancel, totalS, job) {\n  if (!fMolDraft3DCurrent(job)) return;')
wait=wait.replace('try { fMolDraftMinWaitEl = ov; }','try { fMolDraftMinWaitJob = job; fMolDraftMinWaitEl = ov; }')
# A queued old Escape handler cannot close or cancel a newer job's overlay.
wait=wait.replace('  var _fireCancel = function () {','  var _fireCancel = function () {\n    if (fMolDraftMinWaitJob !== job || !fMolDraft3DCurrent(job)) return;')
replace('// OK-only save dialog','// Draft-owned 3D work.',wait)
s=s.replace("try { fJSmolScript(job.applet, 'minimize stop;'); }","try { fJSmolScript(job.applet, 'minimize STOP;'); }",1)
s=s.replace('try { fMolDraftMinOKClose(false); } catch (eDialog) {}','try { fMolDraftMinWaitClose(job); } catch (eDialog) {}',1)
# Add the upstream step/wait constants and graph-size budget helper.
budget=part(u,'// Step budget + blind wait','// One fire-and-forget minimize round')
s=s.replace('// The upstream 25-second MMFF/UFF rounds remain bounded.',budget+'// The size-budgeted MMFF/UFF rounds remain bounded.',1)
s=s.replace('async function fMolDraftLocal3DRelaxFF(expectHeavy, ffName, job) {','async function fMolDraftLocal3DRelaxFF(expectHeavy, ffName, job, steps, skipGate) {',1)
s=s.replace("  job.minimizing = true;\n  try {\n    if (fMolDraft3DWrite(job, 'select all; minimize steps 500;', false) === null) return null;\n    await fMolDraft3DWait(job, 25000);","  job.minimizing = true;\n  var stepBudget = Number.isFinite(steps) && steps > 0 ? Math.floor(steps) : MOLMIN_STEPS;\n  try {\n    var waitSecs = fMolDraftMinWaitSecs(expectHeavy);\n    fMolDraftMinWaitShow(function () { fMolDraftMinWaitAbort(job); }, waitSecs, job);\n    if (fMolDraft3DWrite(job, 'select all; minimize steps ' + stepBudget + ';', false) === null) return null;\n    await fMolDraft3DWait(job, waitSecs * 1000);",1)
s=s.replace("    // Finish the bounded round before the next model/force field is used.\n    fMolDraft3DWrite(job, 'minimize stop;', false);\n    if (!fMolDraft3DCurrent(job)) return null;\n",'    // Normal completion never sends STOP; STOP is reserved for cancellation.\n',1)
s=s.replace("async function fMolDraftLocal3DRelaxBoth(expectHeavy, job) {","async function fMolDraftLocal3DRelaxBoth(expectHeavy, job, steps, skipGate) {",1)
s=s.replace("fMolDraftLocal3DRelaxFF(expectHeavy, 'MMFF', job)","fMolDraftLocal3DRelaxFF(expectHeavy, 'MMFF', job, steps, skipGate)",1)
s=s.replace('if (mmff && job.lastMotion >= 0.05) return mmff;','if (mmff && (skipGate || job.lastMotion >= 0.05)) return mmff;',1)
s=s.replace("fMolDraftLocal3DRelaxFF(expectHeavy, 'UFF', job)","fMolDraftLocal3DRelaxFF(expectHeavy, 'UFF', job, steps, skipGate)",1)
s=s.replace('async function fMolDraftLocal3DFromMol(molText, expectHeavy, skipPrepare, job) {','async function fMolDraftLocal3DFromMol(molText, expectHeavy, skipPrepare, job, steps, skipGate) {',1)
s=s.replace('fMolDraftLocal3DRelaxBoth(expectHeavy, job);','fMolDraftLocal3DRelaxBoth(expectHeavy, job, steps, skipGate);',1)
newmanual='''// Cancel/STOP is tied to the exact still-owned model and running round.
function fMolDraftMinStopEngine(job) {
  job = job || fMolDraft3DJob;
  if (!fMolDraft3DCurrent(job) || !job.minimizing) return;
  fMolDraft3DWrite(job, "minimize STOP;", false);
  job.minimizing = false;
}
function fMolDraftMinWaitAbort(job) {
  job = job || fMolDraft3DJob;
  if (!fMolDraft3DCurrent(job)) return;
  var d = job.draft;
  fMolDraftMinStopEngine(job);
  fMolDraft3DInvalidate();
  d._submitId = (d._submitId || 0) + 1;
  d.submitting = false;
  d._minimizing = false;
  d.sdfDone = true;
  // Existing provisional SDF is retained on Cancel; no new model is banked.
  if (d.sdf3D) fMolDraftShow3D(d.sdf3D);
  fMolDraftRenderPreview();
  fMolDraftSyncBar();
}
function fMolDraftLocal3DReloadMinimized(sdf, expectHeavy, job) {
  if (!fMolDraft3DCurrent(job) || !fMolDraftValidSDF3D(sdf, expectHeavy, job.molText)) return false;
  if (!fMolDraft3DLoad(job, sdf)) return false;
  if (fMolDraft3DWrite(job, "select all;", true) === null) return false;
  return !!fMolDraftReadBackSDF(expectHeavy, job);
}
async function fMolDraftManualMinimize() {
  var d = window.MulerDraft;
  if (!d || !d.submitted || !d.sdfDone || d.submitting || d.accepting || window.MulerDraftAcquisition ||
      d._minimizing || fMolDraftPresenting() || (d.sdf3D && d.sdf3DStatus !== 'provisional')) return;
  var job = fMolDraft3DBegin();
  if (!job) return;
  var further = !!(d.sdf3D && d.sdf3DSource === "jsmol-min");
  d._minimizing = true;
  fMolDraftSyncBar();
  var result = null;
  try {
    var ready = !further || fMolDraftLocal3DReloadMinimized(d.sdf3D, d.expectHeavy || 0, job);
    if (ready) result = await fMolDraftLocal3DFromMol(d.molText, d.expectHeavy || 0, further, job,
      further ? MOLMIN_FURTHER_STEPS : MOLMIN_STEPS, further);
  } catch (e) {}
  if (!fMolDraft3DCurrent(job)) return;
  d._minimizing = false;
  fMolDraftMinWaitClose(job);
  var best = (result && result.sdf) || (!further ? fMolDraftReadBackSDF(d.expectHeavy || 0, job) : null);
  if (!best) {
    fMolDraft3DJob = null;
    fMolDraftToast(fMolDraftT(further ? 'draftMinFurtherMiss' : 'submitNo3DAll', further ?
      'Further round produced no valid result — kept the previous 3D structure.' : 'No graph-matched 3D model.'));
    fMolDraftRenderPreview(); fMolDraftSyncBar();
    return;
  }
  var source = result && result.sdf ? 'jsmol-min' : 'jsmol-unminimized';
  // This is a preview, not consent to persist it. Accept asks once for the
  // exact provisional conformation; there is no second save-OK dialog.
  if (!fMolDraftSet3D(d, best, source, null)) return;
  fMolDraft3DJob = null;
  fMolDraftShow3D(best);
  fMolDraftToast(fMolDraftT('draftMinProvisionalDone', 'Provisional 3D preview; geometry and convergence are unverified.'));
  fMolDraftRenderPreview(); fMolDraftSyncBar();
}
'''
replace('async function fMolDraftManualMinimize() {','function fMolDraftRemote3DFromJSmol(',newmanual)
# Every successful local tier closes only its own wait window.
s=s.replace('  fMolDraft3DJob = null;\n  return local &&','  fMolDraftMinWaitClose(job);\n  fMolDraft3DJob = null;\n  return local &&',1)
# Dynamic step count corrects the upstream +100 label/200-step mismatch.
s=s.replace('fMolDraftT("draftMinBtn", "Minimize 3D (local)")) + "</button></div>";', 'fMolDraftT(d.sdf3DSource === "jsmol-min" ? "draftMinMore" : "draftMinBtn", "Minimize 3D (local)").replace(/\\+\\d+/, "+" + MOLMIN_FURTHER_STEPS)) + "</button></div>";')
s=s.replace('spt/init-54.spt','spt/init-55.spt')
replace('function fMolDraftSyncSaveBtn() {','async function fMolDraftAccept()',part(u,'function fMolDraftSyncSaveBtn() {','async function fMolDraftAccept()'))
# Include the latest submit status restoration without changing ownership.
needle='  window.MulerDraft.submitting = false;\n  window.MulerDraft.sdfDone = true;'
s=s.replace(needle,'''  try {
    var restoredStatus = document.getElementById("molDraftStatus");
    if (restoredStatus) restoredStatus.textContent = fMolDraftT("draftPreview", "Preview") + ": " + engineName;
  } catch (eStatus) {}
'''+needle,1)
F.write_text(s);print('later viewer delta composed',len(s))
