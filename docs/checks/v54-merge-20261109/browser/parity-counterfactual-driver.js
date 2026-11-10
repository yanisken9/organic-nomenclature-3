var window={},console={log(){},warn(){},error(){}};var selectedMol,mode2D,mainChainMode,jsmeNomeclatureApplet;
load("/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate/js/mulermoc-nom-core-55.js");
function fMolDraftGraphMap(a, b) {
  if (typeof fBuildHeavyMap2D3D !== 'function' || !fMolCanTransform2D(a, true) || !fMolCanTransform2D(b, true)) return null;
  // Added ordinary H must belong to the same implicit-H molecule. Reject
  // detached H/H-H fragments, multiply bonded H and valence overfilling.
  function hydrogenSafe(m) {
    var adjacency = m.atoms.map(function () { return []; });
    m.bonds.forEach(function (bond) {
      adjacency[bond[0] - 1].push([bond[1] - 1, bond[2]]);
      adjacency[bond[1] - 1].push([bond[0] - 1, bond[2]]);
    });
    var valences = { C:4, N:3, O:2, F:1, Cl:1, Br:1, I:1, S:2, P:3 };
    return m.atoms.every(function (atom, index) {
      var neighbors = adjacency[index];
      if (atom.el === "H") return neighbors.length === 1 && neighbors[0][1] === 1 &&
        fIsHeavyEl2D(m.atoms[neighbors[0][0]].el);
      var hydrogenCount = 0, heavyValence = 0;
      neighbors.forEach(function (neighbor) {
        if (m.atoms[neighbor[0]].el === "H") hydrogenCount++;
        else heavyValence += neighbor[1];
      });
      var valence = valences[atom.el], charge = atom.charge || 0;
      if (charge) {
        // Same bounded charge-aware valences as the expanded-form generator.
        // Halide anions have zero H capacity; unsupported charges fail closed.
        var chargedValences = { C: { '-1': 3, 1: 3 }, N: { '-1': 2, 1: 4 }, O: { '-1': 1, 1: 3 },
          F: { '-1': 0 }, Cl: { '-1': 0 }, Br: { '-1': 0 }, I: { '-1': 0 } };
        if (!chargedValences[atom.el] || chargedValences[atom.el][charge] == null) return false;
        valence = chargedValences[atom.el][charge];
        if (heavyValence > valence) return false;
      }
      if (!hydrogenCount) return true;
      return Number.isFinite(valence) && hydrogenCount <= Math.max(0, valence - heavyValence);
    });
  }
  if (!hydrogenSafe(a) || !hydrogenSafe(b)) return null;
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

const a=fParseMolV2000("\nJME 2023-07-31 Tue Nov 10 00:32:04 GMT+200 2026\n\n  8  7  0  0  0  0  0  0  0  0999 V2000\n    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    1.4000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    2.8000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    4.2000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    5.6000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    7.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    8.4000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    9.8000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0  0  0  0\n  2  3  1  0  0  0  0\n  3  4  1  0  0  0  0\n  4  5  1  0  0  0  0\n  5  6  1  0  0  0  0\n  6  7  1  0  0  0  0\n  7  8  1  0  0  0  0\nM  END\n"), b=fParseMolV2000("string\n__Jmol-16.11102600323D 1   1.00000     0.00000     0\nJmol version 16.4.23  2026-08-24 10:15 EXTRACT: ({0:25})\n 26 25  0  0  0  0            999 V2000\n   -0.6084   -0.4286    0.0387 C   0  0  2  0  0  0\n    0.6320    0.4677    0.0288 C   0  0  2  0  0  0\n   -1.9251    0.3534    0.0307 C   0  0  2  0  0  0\n    1.9162   -0.3646    0.0134 C   0  0  2  0  0  0\n   -3.1635   -0.5416   -0.0336 C   0  0  2  0  0  0\n    3.1566    0.5275   -0.0351 C   0  0  2  0  0  0\n   -4.4429    0.2810   -0.0264 C   0  0  0  0  0  0\n    4.4352   -0.2948   -0.0166 C   0  0  0  0  0  0\n   -0.5822   -1.0768    0.9233 H   0  0  0  0  0  0\n   -0.5814   -1.0883   -0.8377 H   0  0  0  0  0  0\n    0.6221    1.1178    0.9119 H   0  0  0  0  0  0\n    0.6044    1.1188   -0.8533 H   0  0  0  0  0  0\n   -1.9307    1.0354   -0.8287 H   0  0  0  0  0  0\n   -1.9737    0.9790    0.9306 H   0  0  0  0  0  0\n    1.9126   -1.0331   -0.8562 H   0  0  0  0  0  0\n    1.9522   -0.9984    0.9079 H   0  0  0  0  0  0\n   -3.1698   -1.2275    0.8214 H   0  0  0  0  0  0\n   -3.1320   -1.1542   -0.9419 H   0  0  0  0  0  0\n    3.1575    1.2109    0.8221 H   0  0  0  0  0  0\n    3.1369    1.1437   -0.9415 H   0  0  0  0  0  0\n   -4.5183    0.8815    0.8858 H   0  0  0  0  0  0\n   -4.4800    0.9564   -0.8871 H   0  0  0  0  0  0\n   -5.3163   -0.3770   -0.0729 H   0  0  0  0  0  0\n    5.3093    0.3628   -0.0530 H   0  0  0  0  0  0\n    4.4807   -0.9684   -0.8784 H   0  0  0  0  0  0\n    4.5011   -0.8974    0.8948 H   0  0  0  0  0  0\n  1  2  1\n  1  3  1\n  1  9  1\n  1 10  1\n  2  4  1\n  2 11  1\n  2 12  1\n  3  5  1\n  3 13  1\n  3 14  1\n  4  6  1\n  4 15  1\n  4 16  1\n  5  7  1\n  5 17  1\n  5 18  1\n  6  8  1\n  6 19  1\n  6 20  1\n  7 21  1\n  7 22  1\n  7 23  1\n  8 24  1\n  8 25  1\n  8 26  1\nM  END\n\n");const result={inputAllowed:fMolCanTransform2D(a,true),readbackAllowed:fMolCanTransform2D(b,true),parity:b.atoms.map((v,i)=>({atom:i+1,el:v.el,parity:v.parity,hydrogenCount:v.hydrogenCount,valence:v.valence})).filter(v=>v.parity||v.hydrogenCount||v.valence),graphBefore:!!fMolDraftGraphMap(a,b)};b.atoms.forEach(v=>v.parity=0);result.readbackAllowedAfterParityOnlyCounterfactual=fMolCanTransform2D(b,true);result.graphAfterParityOnlyCounterfactual=!!fMolDraftGraphMap(a,b);print(JSON.stringify(result));
