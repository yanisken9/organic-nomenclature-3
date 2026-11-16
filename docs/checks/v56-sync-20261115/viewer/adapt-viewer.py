from pathlib import Path
import re
p=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate/js/mulermoc-nom-molview-56.js')
s=p.read_text()
# Shared upstream status layout retains explicit local provisional geometry
# wording/consent semantics and the actual +200 round budget.
s=s.replace('var out = "<div class=\'draftOracleRow\'>" + fMolDraftEsc(fMolDraftT(_k, _f))', 'var out = "<div class=\'draftOracleRow\'>" + fMolDraftEsc(fMolDraftT(d.sdf3DStatus === "provisional" ? "draft3DProvisional" : _k, d.sdf3DStatus === "provisional" ? "3D: provisional local conformation (geometry and convergence unverified)" : _f))')
s=s.replace('fMolDraftT("draftMinMore", "Minimize +100 (local)")', 'fMolDraftT("draftMinMore", "Minimize +200 (local)").replace(/\\+\\d+/, "+" + MOLMIN_FURTHER_STEPS)')
s=s.replace("d.sdf3DStatus = source === 'pubchem' || source === 'remote' ? 'source-provided' : 'provisional';", "d.sdf3DStatus = source === 'pubchem' || source === 'pubchem-jsmol' || source === 'pubchem-fetch' || source === 'remote' ? 'source-provided' : 'provisional';")
a=s.index('function fMolDraftRemote3DFromJSmol(')
b=s.index('\nfunction fMolDraftShow3D(',a)
s=s[:a]+'''// Every applet provider uses the same serialized draft-owned model writer
// and exact graph read-back as local minimization. A stale provider cannot
// read, replace or store a later drawing's model.
function fMolDraftJSmolLoadAndReadBack(loadCmd, expectHeavy, job) {
  if (!loadCmd || !fMolDraft3DCurrent(job) ||
      (typeof navigator !== 'undefined' && navigator.onLine === false)) return null;
  if (fMolDraft3DWrite(job, 'zap;', true) === null) return null;
  if (fMolDraft3DWrite(job, loadCmd, true) === null) return null;
  return fMolDraftReadBackSDF(expectHeavy, job);
}
function fMolDraftPubChem3DFromJSmol(query, expectHeavy, job, by) {
  if (!query || !fMolDraft3DCurrent(job)) return null;
  var q = String(query).trim(), cmd = null;
  if (by === 'cid') {
    if (!/^\\d+$/.test(q)) return null;
    cmd = 'load ":cid:' + q + '"';
  } else {
    // Chemical input cannot terminate a Jmol script string.
    if (/[\\r\\n";]/.test(q)) return null;
    cmd = 'load ":smiles:' + q.replace(/\\\\/g, '\\\\\\\\') + '"';
  }
  return fMolDraftJSmolLoadAndReadBack(cmd, expectHeavy, job);
}
function fMolDraftRemote3DFromJSmol(smiles, expectHeavy, job) {
  if (!smiles || !fMolDraft3DCurrent(job) || /[\\r\\n";]/.test(smiles)) return null;
  var quoted = String(smiles).replace(/\\\\/g, '\\\\\\\\');
  return fMolDraftJSmolLoadAndReadBack('load "$' + quoted + '"', expectHeavy, job);
}
async function fMolDraftFetchSDF3DTiered(smiles, molText, expectHeavy, isCurrent, opts) {
  var job = fMolDraft3DBegin(isCurrent);
  var empty = { sdf:null, source:null };
  if (!job) return empty;
  var offline = typeof navigator !== 'undefined' && navigator.onLine === false;
  var o = opts || {}, cid = o.cid == null ? null : String(o.cid).trim();
  if (cid && !/^\\d+$/.test(cid)) cid = null;
  var canonical = o.canonicalSmiles ? String(o.canonicalSmiles).trim() : null;
  // Native test hook skips all network tiers, leaving bounded local work.
  if (!offline && !window.MULER_SKIP_REMOTE3D) {
    var pubchem = null;
    if (cid) pubchem = fMolDraftPubChem3DFromJSmol(cid, expectHeavy, job, 'cid');
    if (!fMolDraft3DCurrent(job)) return empty;
    if (!pubchem && (canonical || smiles)) {
      pubchem = fMolDraftPubChem3DFromJSmol(canonical || smiles, expectHeavy, job, 'smiles');
    }
    if (!fMolDraft3DCurrent(job)) return empty;
    if (fMolDraftValidSDF3D(pubchem, expectHeavy, molText)) {
      fMolDraft3DJob = null;
      return { sdf:pubchem, source:'pubchem-jsmol' };
    }
    var sdf = null;
    try { if (typeof fFetchSDF3D_PubChem === 'function') sdf = await fFetchSDF3D_PubChem(smiles); } catch (e) {}
    if (!fMolDraft3DCurrent(job)) return empty;
    if (fMolDraftValidSDF3D(sdf, expectHeavy, molText)) {
      fMolDraft3DJob = null;
      return { sdf:sdf, source:'pubchem-fetch' };
    }
    var remote = null;
    try { remote = fMolDraftRemote3DFromJSmol(smiles, expectHeavy, job); } catch (eR) {}
    if (!fMolDraft3DCurrent(job)) return empty;
    if (fMolDraftValidSDF3D(remote, expectHeavy, molText)) {
      fMolDraft3DJob = null;
      return { sdf:remote, source:'remote' };
    }
  }
  var local = null;
  try { local = await fMolDraftLocal3DFromMol(molText, expectHeavy, false, job); } catch (eL) {}
  if (!fMolDraft3DCurrent(job)) return empty;
  fMolDraftMinWaitClose(job);
  fMolDraft3DJob = null;
  return local && fMolDraftValidSDF3D(local.sdf, expectHeavy, molText) ? { sdf:local.sdf, source:'jsmol-min' } : empty;
}
''' +s[b:]
# Native skeletal picking assumes positional maps have no ownership. This
# producer does preserve real atom IDs, so use them for visible hetero labels;
# unlabeled implicit carbons keep upstream vertex/topology picking.
needle='''function fMulerSelectHeteroAnchors(groups) {
  var out = [];
  try {
'''
replacement=needle+'''    var ownedLabels = null;
    try { ownedLabels = molSvg && molSvg.selectAll('text[data-namelecule-atom][data-namelecule-role="label"]'); } catch (eOwned) {}
    if (ownedLabels && ownedLabels.length) {
      var ownedMap = fGetRenderedAtomTextMap(false, false);
      for (var atomId in ownedMap) {
        if (!Object.prototype.hasOwnProperty.call(ownedMap, atomId)) continue;
        var atomIndex = Number(atomId), node = ownedMap[atomId].node;
        if (allAtomsTypeList[atomIndex] === 'C' || allAtomsTypeList[atomIndex] === 'H' ||
            node.getAttribute('data-muler-hidden') || node.hasAttribute('data-hidden-carbon-h') ||
            node.style.display === 'none') continue;
        var ownedBox = node.getBBox();
        if (ownedBox.width > 0 && ownedBox.height > 0) out.push({atom:atomIndex,
          x:ownedBox.x + ownedBox.width / 2, y:ownedBox.y + ownedBox.height / 2,
          w:ownedBox.width, h:ownedBox.height});
      }
      return out;
    }
'''
assert needle in s;s=s.replace(needle,replacement,1)
# The local55 added this same helper earlier; retain one definition.
pat=r'function fGetNameComponentLocants\(component\) \{\n.*?\n\}\n\n'
matches=list(re.finditer(pat,s,re.S));assert len(matches)==2
assert matches[0][0]==matches[1][0]
s=s[:matches[1].start()]+s[matches[1].end():]
# Native sequence badges are overlays, and hidden skeletal sp labels have
# no visible ink. Neither participates in molecular ownership/metrics/fit.
s=s.replace('for (const text of svg.querySelectorAll(\'text:not([id^="number"])\'))', 'for (const text of svg.querySelectorAll(\'text:not([id^="number"]):not([id^="mulerSelNum"])\'))')
s=s.replace("    if (text.hasAttribute('data-hidden-carbon-h')) continue;", "    if (text.hasAttribute('data-hidden-carbon-h') || text.hasAttribute('data-muler-hidden')) continue;")
s=s.replace('if (el.closest("defs") || (el.id || "").indexOf("number") === 0) return;', 'if (el.closest("defs") || (el.id || "").indexOf("number") === 0 || (el.id || "").indexOf("mulerSelNum") === 0) return;')
s=s.replace("      if (el.hasAttribute('data-hidden-carbon-h')) return;", "      if (el.hasAttribute('data-hidden-carbon-h') || el.hasAttribute('data-muler-hidden')) return;")
s=s.replace('// mulermoc-nom-molview-55.js','// mulermoc-nom-molview-56.js',1).replace('// Reads analysis results from mulermoc-nom-core-55.js globals.','// Reads analysis results from mulermoc-nom-core-56.js globals.',1)
s=s.replace("      if (el.hasAttribute('data-hidden-carbon-h') || el.hasAttribute('data-muler-hidden')) return;", "      if (el.hasAttribute('data-hidden-carbon-h') || el.hasAttribute('data-muler-hidden') ||\n          el.hasAttribute('data-muler-sel') || el.hasAttribute('data-muler-compact-sel')) return;")
p.write_text(s)
print('adapted guarded PubChem tier, status +200 and atom ownership')
