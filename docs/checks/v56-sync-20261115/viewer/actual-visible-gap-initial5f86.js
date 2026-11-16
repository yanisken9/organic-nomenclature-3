function fMulerSelectCompactCarbonOnly(comp) {
  try {
    if (!comp || typeof comp.anchor !== "number" || comp.anchor < 0) return false;
    if (fMulerSelectPurpose() !== "mainChain") return false;
    if (typeof allAtomsTypeList === "undefined" || !Array.isArray(allAtomsTypeList)) return false;
    return String(allAtomsTypeList[comp.anchor] || "").toUpperCase() === "C";
  } catch (e) { return false; }
}


function fMulerQuizHydrogenParent(atom1) {
  try {
    if (typeof window === "undefined" || !window.MulerQuizTarget) return -1;
    if (typeof allAtomsTypeList === "undefined" || !allAtomsTypeList) return -1;
    if (String(allAtomsTypeList[atom1 - 1] || "").toUpperCase() !== "H") return -1;
    var tgt = [];
    try { tgt = (typeof fMulerQuizTargetSet === "function") ? fMulerQuizTargetSet() : []; } catch (eT) { tgt = []; }
    if (tgt.indexOf(atom1) >= 0) return -1;
    if (typeof bondList === "undefined" || !bondList) return -1;
    for (var b = 0; b < bondList.length; b++) {
      if (!bondList[b]) continue;
      if (bondList[b][0] === atom1) return bondList[b][1];
      if (bondList[b][1] === atom1) return bondList[b][0];
    }
  } catch (e) {}
  return -1;
}


function fMulerSelectPick(px, py) {
  try {
    var geom = null;
    try { if (typeof fMulerSelectGeom === "function") geom = fMulerSelectGeom(); } catch (eG0) { geom = null; }
    var groups = null, anchors = [], comp = null, verts = [], vAssign = [], med = 0;
    if (geom) {
      groups = geom.groups || null;
      anchors = geom.anchors || [];
      comp = geom.comp || null;
      verts = geom.verts || [];
      vAssign = geom.vassign || [];
      med = geom.med || 0;
    } else {
      try { if (typeof fMulerSelectLineGroups === "function") groups = fMulerSelectLineGroups(); } catch (eG) { groups = null; }
      if (groups && groups.length) {
        try { med = (typeof fMulerSelectMedianBond === "function") ? fMulerSelectMedianBond(groups) : 0; } catch (eM) { med = 0; }
      }
      try { if (typeof fMulerSelectCompacted === "function") comp = fMulerSelectCompacted(); } catch (eC0) { comp = null; }
      try { if (typeof fMulerSelectAnchors === "function") anchors = fMulerSelectAnchors() || []; } catch (eA0) { anchors = []; }
      try { verts = (typeof fMulerSelectVertices === "function") ? fMulerSelectVertices(groups) : []; } catch (eV) { verts = []; }
      try { vAssign = (typeof fMulerSelectVertexAtoms === "function") ? fMulerSelectVertexAtoms(verts, groups) : []; } catch (eVA) { vAssign = []; }
    }
    var rAtom = med > 0 ? med * MULER_SELECT_ATOM_R : 200;
    var rBond = med > 0 ? med * MULER_SELECT_BOND_HW : 150;
    // compacted-label fragments (condensed) first: the label IS the anchor's
    // own text element, so a plain anchor hit below would select only the
    // anchor atom instead of the whole fragment.
    // (comp comes from the per-render geometry cache above.)
    try {
      if (comp && comp.length) {
        var mainChainPurpose = fMulerSelectPurpose() === "mainChain";
        for (var ci = 0; ci < comp.length; ci++) {
          var L0 = comp[ci], m0 = 14;
          if (!L0 || !L0.el) continue;
          // Main-chain purpose: the whole label/backplate is the anchor
          // carbon's hit area. Free selection keeps the pre-v56 glyph-run
          // area only, so the deliberately wider backplate never steals
          // picks from adjacent atoms or bond stubs.
          var lb = (mainChainPurpose && L0.box) ? L0.box : (L0.textBox || null);
          if (!lb) {
            try {
              var _bb = L0.el.getBBox ? L0.el.getBBox() : null;
              if (_bb && _bb.width > 0 && _bb.height > 0) lb = { x: _bb.x, y: _bb.y, w: _bb.width, h: _bb.height };
            } catch (eBb) { lb = null; }
          }
          if (!lb || !(lb.w > 0 && lb.h > 0)) continue;
          if (px >= lb.x - m0 && px <= lb.x + lb.w + m0 && py >= lb.y - m0 && py <= lb.y + lb.h + m0) {
            // Main-chain purpose: a compacted carbon label is the anchor
            // atom, never the heteroatom fragment. Other purposes (and
            // N/S-anchored groups) keep whole-fragment picking.
            if (typeof fMulerSelectCompactCarbonOnly === "function" && fMulerSelectCompactCarbonOnly(L0)) {
              return {
                kind: "atom",
                atom: L0.anchor + 1,
                compactAnchor: true,
                compactAtomBox: L0.atomBox || null
              };
            }
            return {
              kind: "fragment",
              atoms: (L0.members || []).slice(),
              compactGroupBox: lb
            };
          }
        }
      }
    } catch (eC) {}
    // (anchors come from the per-render geometry cache above.)
    var best = null, bd = rAtom * rAtom;
    for (var i = 0; i < anchors.length; i++) {
      if (!anchors[i] || anchors[i].atom == null || isNaN(anchors[i].atom)) continue;
      var dx = anchors[i].x - px, dy = anchors[i].y - py, d2 = dx * dx + dy * dy;
      if (d2 <= bd) { bd = d2; best = anchors[i].atom; }
    }
    if (best !== null && best !== undefined) {
      // Armed quiz: a non-target H resolves to its heavy atom (condensed-style
      // unit picking); target H stays distinct. See fMulerQuizHydrogenParent.
      var _ha = -1;
      try { if (typeof fMulerQuizHydrogenParent === "function") _ha = fMulerQuizHydrogenParent(best + 1); } catch (eH) { _ha = -1; }
      return { kind: "atom", atom: (_ha > 0 ? _ha : best + 1) };
    }
    if (!groups || !groups.length) return null;
    if (!(med > 0)) {
      try { med = (typeof fMulerSelectMedianBond === "function") ? fMulerSelectMedianBond(groups) : 0; } catch (eM2) { med = 0; }
      if (!(med > 0)) return null;
      rAtom = med * MULER_SELECT_ATOM_R;
      rBond = med * MULER_SELECT_BOND_HW;
    }
    // vertices (implicit skeletal carbons): resolve topologically
    // (verts/vassign come from the per-render geometry cache above).
    var bv = null, bvd = rAtom * rAtom;
    for (var v = 0; v < verts.length; v++) {
      var dx2 = verts[v].x - px, dy2 = verts[v].y - py, d22 = dx2 * dx2 + dy2 * dy2;
      if (d22 <= bvd) { bvd = d22; bv = v; }
    }
    if (bv !== null && vAssign[bv] !== undefined && vAssign[bv] >= 0) return { kind: "atom", atom: vAssign[bv] + 1, vertex: bv };
    // bonds: corridor around each line segment
    var bb = null, bbd = rBond * rBond, bpair = null;
    for (var g = 0; g < groups.length; g++) {
      var ls2 = groups[g].lines;
      for (var li = 0; li < ls2.length; li++) {
        var L = ls2[li];
        var vx = L.x2 - L.x1, vy = L.y2 - L.y1;
        var L2 = vx * vx + vy * vy;
        if (!(L2 > 0)) continue;
        var t = ((px - L.x1) * vx + (py - L.y1) * vy) / L2;
        t = t < 0 ? 0 : (t > 1 ? 1 : t);
        var qx = L.x1 + t * vx - px, qy = L.y1 + t * vy - py;
        var qd = qx * qx + qy * qy;
        if (qd <= bbd) {
          bbd = qd; bb = g;
          try {
            var pr = (typeof bondList !== "undefined" && bondList[groups[g].bond]) ? bondList[groups[g].bond] : null;
            bpair = pr ? [pr[0], pr[1]] : null;
          } catch (eP) { bpair = null; }
        }
      }
    }
    if (bb !== null && bpair) {
      // Atoms-only quizzes (all targets): bond clicks never select, never clear.
      // Bond-purpose quizzes accept bond clicks (normalized to endpoint atoms
      // at compare time) — the prompt names the bond.
      var _bPurp = "free";
      try { _bPurp = (typeof fMulerSelectPurpose === "function") ? fMulerSelectPurpose() : "free"; } catch (eP2) { _bPurp = "free"; }
      if (typeof window !== "undefined" && window.MulerQuizTarget && _bPurp !== "bond") return { ignore: true };
      return { kind: "bond", bond: groups[bb].bond + 1, pair: bpair };
    }
    return null;
  } catch (e) { return { ignore: true }; }
}


var window=this, allAtomsTypeList=[],bondList=[],_geom={},_purpose='free',_target=[];
var MULER_SELECT_ATOM_R=.35,MULER_SELECT_BOND_HW=.2;
function fMulerSelectGeom(){return _geom;}
function fMulerSelectPurpose(){return _purpose;}
function fMulerQuizTargetSet(){return _target;}
function assert(v,m){if(!v)throw Error(m);}
function same(actual,expected){assert(JSON.stringify(actual)===JSON.stringify(expected),'expected '+JSON.stringify(expected)+', got '+JSON.stringify(actual));}
var results=[];function test(name,fn){try{fn();results.push({name:name,pass:true});}catch(e){results.push({name:name,pass:false,error:String(e)});}}
function setup(){window.MulerQuizTarget=null;_target=[];_purpose='free';allAtomsTypeList=['C','C'];bondList=[[1,2,1]];_geom={med:750,groups:[{bond:0,lines:[{x1:4221,y1:2528,x2:4971,y2:2528}]}],anchors:[{atom:0,x:4385.966064453125,y:2586.3636474609375,w:559.02294921875,h:340.000244140625},{atom:1,x:5135.966064453125,y:2586.3636474609375,w:559.02294921875,h:340.000244140625}],comp:[],verts:[{x:4221,y:2528},{x:4971,y:2528}],vassign:[0,1]};}
test('actual measured raw midpoint is inside C1 glyph and correctly selects C1',function(){setup();same(fMulerSelectPick(4596,2528),{kind:'atom',atom:1});});
test('actual independently measured visible gap selects C-C bond',function(){setup();same(fMulerSelectPick(4761,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('all observed visible samples avoid explicit-atom vertex halos',function(){setup();for(var t=.65;t<=.84;t+=.01)same(fMulerSelectPick(4221+750*t,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('main-chain mission ignores actual visible gap without selecting endpoint',function(){setup();window.MulerQuizTarget='compCarbonsCount';_purpose='mainChain';same(fMulerSelectPick(4761,2528),{ignore:true});});
test('bond mission retains native endpoint payload for visible gap',function(){setup();window.MulerQuizTarget='compBondType';_purpose='bond';same(fMulerSelectPick(4761,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('expanded explicit carbon vertex does not steal visible C-C interior',function(){setup();_geom.anchors=[{atom:0,x:4221,y:2528,w:100,h:100},{atom:1,x:4971,y:2528,w:100,h:100}];same(fMulerSelectPick(4761,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('labeled hetero vertex does not steal visible adjacent bond interior',function(){setup();allAtomsTypeList=['C','O'];_geom.anchors=[{atom:1,x:4971,y:2528,w:100,h:100}];same(fMulerSelectPick(4761,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('unlabeled skeletal endpoint retains native implicit-vertex selection',function(){setup();_geom.anchors=[];same(fMulerSelectPick(4761,2528),{kind:'atom',atom:2,vertex:1});});
test('skeletal vertex ownership excludes only explicitly labeled atom',function(){setup();allAtomsTypeList=['C','O'];_geom.anchors=[{atom:1,x:4971,y:2528,w:100,h:100}];same(fMulerSelectPick(4221,2528),{kind:'atom',atom:1,vertex:0});same(fMulerSelectPick(4971,2528),{kind:'atom',atom:2});});
test('explicit expanded H retains native parent redirection',function(){setup();allAtomsTypeList=['C','H'];_geom.anchors=[{atom:1,x:4971,y:2528,w:100,h:100}];window.MulerQuizTarget='compCarbonsCount';_purpose='mainChain';_target=[1];same(fMulerSelectPick(4971,2528),{kind:'atom',atom:1});});
print(JSON.stringify({cases:results.length,passed:results.filter(function(r){return r.pass;}).length,results:results}));if(results.some(function(r){return !r.pass;}))quit(1);
