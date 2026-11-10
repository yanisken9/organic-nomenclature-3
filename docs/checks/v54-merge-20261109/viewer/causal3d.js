// Draft-owned 3D work. A model replacement through the shared JSmol wrappers
// revokes the job before writing; asynchronous continuations never reacquire it.
var fMolDraft3DRevision = 0;
var fMolDraft3DJob = null;
var fMolDraft3DWriter = null;
function fMolDraft3DCurrent(job) {
  try {
    return !!(job && !job.cancelled && fMolDraft3DJob === job &&
      window.MulerDraft === job.draft && job.draft._epoch === job.epoch &&
      job.draft._submitId === job.submitId && job.draft.smiles === job.smiles &&
      job.draft.molText === job.molText && !job.draft.cancelRequested &&
      jmolAppletNomeclature === job.applet && fMolDraft3DRevision === job.revision &&
      (typeof selectedMol === 'undefined' ? null : selectedMol) === job.selection &&
      (typeof mode2D === 'undefined' ? null : mode2D) === job.mode &&
      (!job.isCurrent || job.isCurrent()) && !fMolDraftPresenting());
  } catch (e) { return false; }
}
function fMolDraft3DInvalidate() {
  var job = fMolDraft3DJob;
  if (job) {
    // Stop only the still-owned model, before any replacement is loaded.
    if (fMolDraft3DCurrent(job) && job.minimizing) {
      try { fJSmolScript(job.applet, 'minimize stop;'); } catch (eStop) {}
    }
    job.cancelled = true;
    if (job.wake) { try { job.wake(); } catch (eWake) {} job.wake = null; }
  }
  fMolDraft3DJob = null;
  try { fMolDraftMinOKClose(false); } catch (eDialog) {}
}
function fMolDraft3DBegin(isCurrent) {
  fMolDraft3DInvalidate();
  var d = window.MulerDraft;
  if (!d || !d.molText || typeof jmolAppletNomeclature === 'undefined' || !jmolAppletNomeclature) return null;
  var job = { draft: d, epoch: d._epoch, submitId: d._submitId, smiles: d.smiles,
    molText: d.molText, applet: jmolAppletNomeclature, revision: fMolDraft3DRevision,
    selection: typeof selectedMol === 'undefined' ? null : selectedMol,
    mode: typeof mode2D === 'undefined' ? null : mode2D, isCurrent: isCurrent || null };
  fMolDraft3DJob = job;
  return fMolDraft3DCurrent(job) ? job : null;
}
function fMolDraft3DWillScript(applet, cmd) {
  if (applet !== jmolAppletNomeclature || !/(^|;)\s*(?:load|zap)\b/i.test(String(cmd))) return;
  if (fMolDraft3DWriter && fMolDraft3DWriter === fMolDraft3DJob) {
    fMolDraft3DWriter.revision = ++fMolDraft3DRevision;
  } else {
    fMolDraft3DInvalidate();
    fMolDraft3DRevision++;
  }
}
function fMolDraft3DWrite(job, cmd, wait) {
  if (!fMolDraft3DCurrent(job)) return null;
  var prior = fMolDraft3DWriter;
  fMolDraft3DWriter = job;
  try { return wait ? fJSmolScriptWait(job.applet, cmd) : fJSmolScript(job.applet, cmd); }
  finally { fMolDraft3DWriter = prior; }
}
function fMolDraft3DLoad(job, mol) {
  if (!fMolDraft3DCurrent(job)) return false;
  var prior = fMolDraft3DWriter;
  fMolDraft3DWriter = job;
  try { return !!fJSmolLoadInlineSDF(job.applet, mol, ''); }
  finally { fMolDraft3DWriter = prior; }
}
function fMolDraft3DWait(job, ms) {
  return new Promise(function (resolve) {
    if (!fMolDraft3DCurrent(job)) { resolve(); return; }
    var timer = setTimeout(function () { job.wake = null; resolve(); }, ms);
    job.wake = function () { clearTimeout(timer); resolve(); };
  });
}
// Exact order-independent heavy graph with charge/isotope labels. Ordinary
// explicit H may be added by the 3D provider. Query/stereo/charged or isotopic
// H transformations remain unsupported and fail closed, as in the 2D ladder.
function fMolDraftGraphMap(a, b) {
  if (typeof fBuildHeavyMap2D3D !== 'function' || !fMolCanTransform2D(a, true) || !fMolCanTransform2D(b, true)) return null;
  var saved = [allAtomsTypeList, bondList, allAtomsTypeList3D, bondList3D];
  var masses = { C:12, N:14, O:16, S:32, P:31, F:19, Cl:35, Br:79, I:127, H:1 };
  function labels(m) {
    return m.atoms.map(function (v) {
      var isotope = v.isotope || (v.massDifference ? masses[v.el] + v.massDifference : 0);
      return fIsHeavyEl2D(v.el) ? JSON.stringify([v.el, v.charge || 0, isotope, v.radical || 0]) : 'H';
    });
  }
  try {
    allAtomsTypeList = labels(a); bondList = a.bonds;
    allAtomsTypeList3D = labels(b); bondList3D = b.bonds;
    return fBuildHeavyMap2D3D(false);
  } finally {
    allAtomsTypeList = saved[0]; bondList = saved[1];
    allAtomsTypeList3D = saved[2]; bondList3D = saved[3];
  }
}
function fMolDraftValidSDF3D(sdf, expectHeavy, referenceMol) {
  try {
    if (!sdf || !referenceMol || typeof fParseMolV2000 !== 'function') return false;
    var a = fParseMolV2000(referenceMol), b = fParseMolV2000(sdf);
    if (!fMolDraftGraphMap(a, b)) return false;
    var heavy = b.atoms.filter(function (v) { return fIsHeavyEl2D(v.el); });
    if (!heavy.length || (expectHeavy && heavy.length !== expectHeavy)) return false;
    // Orientation-independent sanity, not a proof of optimized geometry.
    // A single heavy atom, a linear molecule or a planar group is valid.
    return b.bonds.every(function (bond) {
      var p = b.atoms[bond[0] - 1], q = b.atoms[bond[1] - 1];
      var d = Math.hypot(p.x - q.x, p.y - q.y, p.z - q.z);
      return Number.isFinite(d) && d > 0.05 && d < 5;
    });
  } catch (e) { return false; }
}
function fMolDraftReadBackSDF(expectHeavy, job) {
  if (!fMolDraft3DCurrent(job)) return null;
  var text = null;
  try { text = fJSmolScriptEcho(job.applet, 'write MOL') || null; } catch (e) {}
  return fMolDraft3DCurrent(job) && fMolDraftValidSDF3D(text, expectHeavy, job.molText) ? text : null;
}
// The upstream 25-second MMFF/UFF rounds remain bounded. Motion only decides
// whether to try the fallback force field; it cannot certify convergence.
async function fMolDraftLocal3DRelaxFF(expectHeavy, ffName, job) {
  if (!fMolDraft3DCurrent(job)) return null;
  var before = fMolDraftReadBackSDF(expectHeavy, job);
  if (!before) return null;
  if (fMolDraft3DWrite(job, 'set forceField ' + ffName + ';', false) === null) return null;
  if (!fMolDraft3DCurrent(job)) return null;
  job.minimizing = true;
  try {
    if (fMolDraft3DWrite(job, 'select all; minimize steps 500;', false) === null) return null;
    await fMolDraft3DWait(job, 25000);
    if (!fMolDraft3DCurrent(job)) return null;
    // Finish the bounded round before the next model/force field is used.
    fMolDraft3DWrite(job, 'minimize stop;', false);
    if (!fMolDraft3DCurrent(job)) return null;
    var candidate = fMolDraftReadBackSDF(expectHeavy, job);
    job.lastMotion = candidate ? fMolDraftMeanDisplacement(before, candidate) : -1;
    return candidate;
  } finally { job.minimizing = false; }
}
async function fMolDraftLocal3DRelaxBoth(expectHeavy, job) {
  if (!fMolDraft3DCurrent(job)) return null;
  var mmff = await fMolDraftLocal3DRelaxFF(expectHeavy, 'MMFF', job);
  if (!fMolDraft3DCurrent(job)) return null;
  if (mmff && job.lastMotion >= 0.05) return mmff;
  var uff = await fMolDraftLocal3DRelaxFF(expectHeavy, 'UFF', job);
  return fMolDraft3DCurrent(job) ? (uff || mmff) : null;
}
function fMolDraftLocal3DPrepare(molText, expectHeavy, job) {
  try {
    if (!fMolDraft3DCurrent(job) || !fMolDraftGraphMap(fParseMolV2000(molText), fParseMolV2000(job.molText))) return { ok:false };
    if (fMolDraft3DWrite(job, 'zap;', true) === null) return { ok:false };
    if (!fMolDraft3DCurrent(job)) return { ok:false };
    var prepared = fMolDraftJiggleZ(fMolDraftUntangle2D(molText, 0.9), 0.3);
    if (!fMolDraftValidSDF3D(prepared, expectHeavy, job.molText) || !fMolDraft3DLoad(job, prepared)) return { ok:false };
    if (fMolDraft3DWrite(job, 'select all;', true) === null) return { ok:false };
    if (!fMolDraftReadBackSDF(expectHeavy, job)) return { ok:false };
    if (fMolDraft3DWrite(job, 'select all; calculate hydrogens;', true) === null) return { ok:false };
    return { ok: !!fMolDraftReadBackSDF(expectHeavy, job) };
  } catch (e) { return { ok:false }; }
}
async function fMolDraftLocal3DFromMol(molText, expectHeavy, skipPrepare, job) {
  if (!fMolDraft3DCurrent(job)) return { sdf:null, prepared:false };
  var prepared = skipPrepare ? !!fMolDraftReadBackSDF(expectHeavy, job) : !!fMolDraftLocal3DPrepare(molText, expectHeavy, job).ok;
  if (!prepared || !fMolDraft3DCurrent(job)) return { sdf:null, prepared:false };
  var sdf = await fMolDraftLocal3DRelaxBoth(expectHeavy, job);
  return fMolDraft3DCurrent(job) ? { sdf:sdf || null, prepared:true } : { sdf:null, prepared:false };
}
function fMolDraft3DProvenance(source, confirmation) {
  return { source:source, graphMatched:true, geometryVerified:false, convergenceVerified:false,
    confirmation:confirmation || null, confirmedAt:confirmation ? Date.now() : null };
}
function fMolDraftSet3D(d, sdf, source, confirmation) {
  if (!d || !fMolDraftValidSDF3D(sdf, d.expectHeavy || 0, d.molText)) return false;
  d.sdf3D = sdf;
  d.sdf3DSource = source;
  d.sdf3DStatus = source === 'pubchem' || source === 'remote' ? 'source-provided' : 'provisional';
  d.sdf3DProvenance = fMolDraft3DProvenance(source, confirmation);
  d._provisionalConfirmedSDF = confirmation ? sdf : null;
  return true;
}
async function fMolDraftManualMinimize() {
  var d = window.MulerDraft;
  if (!d || !d.submitted || !d.sdfDone || d.submitting || d.accepting || window.MulerDraftAcquisition ||
      d._minimizing || fMolDraftPresenting() || (d.sdf3D && d.sdf3DStatus !== 'provisional')) return;
  var job = fMolDraft3DBegin();
  if (!job) return;
  d._minimizing = true;
  fMolDraftSyncBar();
  var result = null;
  try { result = await fMolDraftLocal3DFromMol(d.molText, d.expectHeavy || 0, false, job); }
  catch (e) {}
  finally { d._minimizing = false; }
  if (!fMolDraft3DCurrent(job)) return;
  var best = (result && result.sdf) || fMolDraftReadBackSDF(d.expectHeavy || 0, job);
  fMolDraftSyncBar();
  if (!best) { fMolDraftToast(fMolDraftT('submitNo3DAll', 'No graph-matched 3D model.')); return; }
  var source = result && result.sdf ? 'jsmol-min' : 'jsmol-unminimized';
  // ESC/backdrop only dismisses. A missing dialog never implies consent.
  fMolDraftMinimizeDialog(fMolDraftT('draftMinSaveProvisional', 'Keep this unverified conformation as provisional 3D?'), function () {
    if (!fMolDraft3DCurrent(job) || !fMolDraftSet3D(d, best, source, 'manual')) return;
    fMolDraft3DJob = null;
    fMolDraftShow3D(best);
    fMolDraftToast(fMolDraftT('draftMinProvisionalDone', 'Provisional 3D saved; geometry and convergence are unverified.'));
    fMolDraftRenderPreview();
    fMolDraftSyncBar();
  });
}
function fMolDraftRemote3DFromJSmol(smiles, expectHeavy, job) {
  if (!smiles || !fMolDraft3DCurrent(job) || (typeof navigator !== 'undefined' && navigator.onLine === false)) return null;
  // Reject script delimiters; the MOL/SMILES input is chemical data.
  if (/[\r\n";]/.test(smiles)) return null;
  var quoted = String(smiles).replace(/\\/g, '\\\\');
  if (fMolDraft3DWrite(job, 'zap;', true) === null) return null;
  if (fMolDraft3DWrite(job, 'load "$' + quoted + '"', true) === null) return null;
  return fMolDraftReadBackSDF(expectHeavy, job);
}
async function fMolDraftFetchSDF3DTiered(smiles, molText, expectHeavy, isCurrent) {
  var job = fMolDraft3DBegin(isCurrent);
  var empty = { sdf:null, source:null };
  if (!job) return empty;
  var offline = typeof navigator !== 'undefined' && navigator.onLine === false;
  if (!offline) {
    var sdf = null;
    try { if (typeof fFetchSDF3D_PubChem === 'function') sdf = await fFetchSDF3D_PubChem(smiles); } catch (e) {}
    if (!fMolDraft3DCurrent(job)) return empty;
    if (fMolDraftValidSDF3D(sdf, expectHeavy, molText)) { fMolDraft3DJob = null; return { sdf:sdf, source:'pubchem' }; }
    var remote = null;
    if (!window.MULER_SKIP_REMOTE3D) {
      try { remote = fMolDraftRemote3DFromJSmol(smiles, expectHeavy, job); } catch (eR) {}
    }
    if (!fMolDraft3DCurrent(job)) return empty;
    if (fMolDraftValidSDF3D(remote, expectHeavy, molText)) { fMolDraft3DJob = null; return { sdf:remote, source:'remote' }; }
  }
  var local = null;
  try { local = await fMolDraftLocal3DFromMol(molText, expectHeavy, false, job); } catch (eL) {}
  if (!fMolDraft3DCurrent(job)) return empty;
  fMolDraft3DJob = null;
  return local && fMolDraftValidSDF3D(local.sdf, expectHeavy, molText) ? { sdf:local.sdf, source:'jsmol-min' } : empty;
}
