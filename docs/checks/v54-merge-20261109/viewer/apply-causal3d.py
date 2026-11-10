from pathlib import Path
P=Path.cwd();F=Path('/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate/js/mulermoc-nom-molview-55.js');s=F.read_text();local=(P/'js/mulermoc-nom-molview-54.js').read_text()
def section(t,a,b):return t[t.index(a):t.index(b,t.index(a))]
def replace(a,b,v):
 global s
 s=s[:s.index(a)]+v+s[s.index(b,s.index(a)):]
# Adopt upstream helpers that perturb geometry, but replace validation and
# the asynchronous lifecycle. Old movement helper remains diagnostic only.
helpers=section(s,'function fMolDraftMeanDisplacement(','// One fire-and-forget minimize round')
helpers=helpers.replace('// Tier-3 movement proof (v55.6+): a real minimization must displace heavy','// Diagnostic movement only: coordinate motion does not establish physical\n// convergence. The upstream diagnostic measures displacement of heavy')
dialog=section(s,'// OK-only save dialog','// Manual 3D minimize fallback')
replace('// ── v55 tiered 3D','function fMolDraftShow3D(',helpers+dialog+(P/'docs/checks/v54-merge-20261109/viewer/causal3d.js').read_text()+'\n')
# Instrument shared applet model writes to revoke a suspended minimizer.
for fn in ('fJSmolScript','fJSmolScriptWait'):
 s=s.replace('function '+fn+'(applet, cmd) {','function '+fn+'(applet, cmd) {\n  fMolDraft3DWillScript(applet, cmd);',1)
# Avoid a second overlay font compensation: local atom anchoring and the
# complete SVG fit consume the already calibrated applet font/scale once.
replace('function fShowNumbering(time,','// ── fShowNumber ─',section(local,'function fShowNumbering(time,','// ── fShowNumber ─'))
# Draw and Cancel invalidate pending oracle/job continuations before new work.
s=s.replace('  if (!window.MulerDraft || window.MulerDraftAcquisition || window.MulerDraft.submitting || fMolDraftPresenting()) return;','  if (!window.MulerDraft || window.MulerDraftAcquisition || fMolDraftPresenting()) return;\n  fMolDraft3DInvalidate();\n  window.MulerDraft._submitId = (window.MulerDraft._submitId || 0) + 1;\n  window.MulerDraft.submitting = false;',1)
s=s.replace('function fMolDraftTeardownDisplay() {','function fMolDraftTeardownDisplay() {\n  fMolDraft3DInvalidate();',1)
s=s.replace('async function fMolDraftSubmit() {','async function fMolDraftSubmit() {',1)
# Freshness includes draft object identity, not only the integer IDs.
s=s.replace('if (!window.MulerDraft || window.MulerDraft._submitId !== _mySid', 'if (window.MulerDraft !== submittingDraft || window.MulerDraft._submitId !== _mySid')
s=s.replace('return !(!window.MulerDraft || window.MulerDraft._submitId !== _mySid', 'return !(window.MulerDraft !== submittingDraft || window.MulerDraft._submitId !== _mySid')
s=s.replace('  window.MulerDraft.sdf3DSource = null;\n  window.MulerDraft.sdfDone = false;','  window.MulerDraft.sdf3DSource = null;\n  window.MulerDraft.sdf3DStatus = null;\n  window.MulerDraft.sdf3DProvenance = null;\n  window.MulerDraft._provisionalConfirmedSDF = null;\n  window.MulerDraft.sdfDone = false;',1)
s=s.replace('    window.MulerDraft.sdf3D = _tier.sdf;\n    window.MulerDraft.sdf3DSource = _tier.source || null;\n    fMolDraftShow3D(_tier.sdf);','    if (fMolDraftSet3D(window.MulerDraft, _tier.sdf, _tier.source || null, null)) fMolDraftShow3D(_tier.sdf);',1)
# No unvalidated fallback if a tier implementation is unavailable.
s=s.replace('if (_s0) _tier = { sdf: _s0, source: "pubchem" };','if (fMolDraftValidSDF3D(_s0, _expH, _molT)) _tier = { sdf: _s0, source: "pubchem" };',1)
# Prevent Accept racing a minimizer; explicit provisional save must name the
# exact conformation (changing it invalidates the prior confirmation).
s=s.replace('if (!d || d.submitting || d.accepting || window.MulerDraftAcquisition || fMolDraftPresenting()) return;','if (!d || d.submitting || d.accepting || d._minimizing || window.MulerDraftAcquisition || fMolDraftPresenting()) return;',1)
needle='  // Edit rule: Update in place only when the drawing is the SAME molecule'
pos=s.index(needle,s.index('async function fMolDraftAccept()'))
s=s[:pos]+'''  if (!fMolDraftValidSDF3D(d.sdf3D, d.expectHeavy || 0, d.molText)) {
    fMolDraftToast(fMolDraftT("accept3DGraphMismatch", "3D does not match the submitted molecular graph."));
    return;
  }
  if (d.sdf3DStatus !== "source-provided" && d._provisionalConfirmedSDF !== d.sdf3D) {
    if (typeof fScenarioConfirm !== "function") return;
    var confirmedSDF = d.sdf3D;
    fScenarioConfirm(fMolDraftT("draftProvisionalConfirm", "Keep this unverified 3D as provisional?"), function () {
      if (window.MulerDraft !== d || d._epoch !== _myEpochA || d._submitId !== _mySidA ||
          d.sdf3D !== confirmedSDF || d._minimizing || d.stale) return;
      d._provisionalConfirmedSDF = confirmedSDF;
      d.sdf3DStatus = "provisional";
      d.sdf3DProvenance = fMolDraft3DProvenance(d.sdf3DSource, "accept");
      fMolDraftAccept();
    }, fMolDraftT("draftProvisionalKeep", "Keep provisional 3D"));
    return;
  }
'''+s[pos:]
s=s.replace('    sdf3DSource: d.sdf3DSource || null,','    sdf3DSource: d.sdf3DSource || null,\n    sdf3DStatus: d.sdf3DStatus || "provisional",\n    sdf3DProvenance: d.sdf3DProvenance || fMolDraft3DProvenance(d.sdf3DSource, "accept"),',1)
s=s.replace('    try { prev.sdf3DSource = rec.sdf3DSource || null; } catch (eS3s) {}','    prev.sdf3DSource = rec.sdf3DSource;\n    prev.sdf3DStatus = rec.sdf3DStatus;\n    prev.sdf3DProvenance = rec.sdf3DProvenance;',1)
# Never fork silently if the confirmation UI is unavailable.
s=s.replace('  // Fail-open without the dialog helper; one-shot flag, cleared on Cancel.','  // Missing confirmation UI fails closed; the source record stays untouched.')
s=s.replace('    if (typeof fScenarioConfirm === "function") {\n      try { fScenarioConfirm(_fm,','    if (typeof fScenarioConfirm !== "function") return;\n    if (typeof fScenarioConfirm === "function") {\n      try { fScenarioConfirm(_fm,',1)
# Local geometry is visibly provisional and may be retried after manual OK.
s=s.replace('if (d.sdf3DSource === "jsmol-unminimized") html +=','if (d.sdf3DStatus === "provisional") html +=')
s=s.replace('fMolDraftT(_s3k, _s3f)','fMolDraftT(d.sdf3DStatus === "provisional" ? "draft3DProvisional" : _s3k, _s3f)')
s=s.replace('fMolDraftT(_s3k2, _s3f2)','fMolDraftT(d.sdf3DStatus === "provisional" ? "draft3DProvisional" : _s3k2, _s3f2)')
# Snapshot consent is durable in both file formats (JSON serialization below
# already preserves arbitrary record fields). Make provenance human-readable.
s=s.replace('"   3D: " + (rec.sdf3DSource || "none") + "\\n" +','"   3D: " + (rec.sdf3DSource || "none") + " (" + (rec.sdf3DStatus || "unspecified") + ")\\n" +')
# Include minimizing in bar state; Draw can revoke a suspended Submit.
s=s.replace('if (!d.submitting && !acquiring) {','if (!d.submitting && !d._minimizing && !acquiring) {')
s=s.replace('if (!d.submitting && !acquiring && !editorVisible)', 'if (!acquiring && !editorVisible)')
F.write_text(s)
print('causal guards applied',len(s))
