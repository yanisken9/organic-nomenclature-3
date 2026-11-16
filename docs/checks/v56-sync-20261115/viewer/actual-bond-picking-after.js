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
    // A visible label's actual glyph bounds own direct label clicks, even
    // when a wide formula extends beyond the loose center radius. Keep that
    // radius only as a fallback: it must not steal a visible bond interior.
    var best = null, bd = Infinity, loose = null, ld = rAtom * rAtom;
    var visibleAnchorAtoms = {};
    for (var i = 0; i < anchors.length; i++) {
      var anchor = anchors[i];
      if (!anchor || anchor.atom == null || isNaN(anchor.atom)) continue;
      if (anchor.w > 0 && anchor.h > 0) visibleAnchorAtoms[anchor.atom] = true;
      var dx = anchor.x - px, dy = anchor.y - py, d2 = dx * dx + dy * dy;
      if (anchor.w > 0 && anchor.h > 0 &&
          px >= anchor.x - anchor.w / 2 && px <= anchor.x + anchor.w / 2 &&
          py >= anchor.y - anchor.h / 2 && py <= anchor.y + anchor.h / 2 && d2 <= bd) {
        bd = d2; best = anchor.atom;
      }
      if (d2 <= ld) { ld = d2; loose = anchor.atom; }
    }
    function anchorPick(atom0) {
      if (atom0 === null || atom0 === undefined) return null;
      // Keep native armed-quiz H-to-parent behavior for both direct glyph
      // hits and the loose fallback. Free and explicitly targeted H stay H.
      var parent = -1;
      try { if (typeof fMulerQuizHydrogenParent === "function") parent = fMulerQuizHydrogenParent(atom0 + 1); } catch (eH) { parent = -1; }
      return { kind: "atom", atom: (parent > 0 ? parent : atom0 + 1) };
    }
    if (best !== null && best !== undefined) return anchorPick(best);
    if (!groups || !groups.length) return anchorPick(loose);
    if (!(med > 0)) {
      try { med = (typeof fMulerSelectMedianBond === "function") ? fMulerSelectMedianBond(groups) : 0; } catch (eM2) { med = 0; }
      if (!(med > 0)) return anchorPick(loose);
      rAtom = med * MULER_SELECT_ATOM_R;
      rBond = med * MULER_SELECT_BOND_HW;
    }
    // vertices (implicit skeletal carbons): resolve topologically
    // (verts/vassign come from the per-render geometry cache above).
    var bv = null, bvd = rAtom * rAtom;
    for (var v = 0; v < verts.length; v++) {
      // A labeled atom is already represented by its visible glyph above.
      // Its raw bond endpoint must not add an implicit-atom halo over the
      // adjacent visible bond. Unlabeled skeletal atoms keep vertex picking.
      if (visibleAnchorAtoms[vAssign[v]]) continue;
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
    // No direct glyph, implicit vertex or bond corridor claimed the point.
    // Preserve the forgiving native atom-center halo on empty surroundings.
    return anchorPick(loose);
  } catch (e) { return { ignore: true }; }
}


var window=this, allAtomsTypeList=[],bondList=[],_geom={},_purpose='free',_target=[];
var MULER_SELECT_ATOM_R=.35,MULER_SELECT_BOND_HW=.2;
function fMulerSelectGeom(){return _geom;}
function fMulerSelectPurpose(){return _purpose;}
function fMulerQuizTargetSet(){return _target;}
function assert(v,m){if(!v)throw Error(m);}
function same(actual,expected){assert(JSON.stringify(actual)===JSON.stringify(expected),'expected '+JSON.stringify(expected)+', got '+JSON.stringify(actual));}
var results=[];
function test(name,fn){try{fn();results.push({name:name,pass:true});}catch(e){results.push({name:name,pass:false,error:String(e)});}}
function label(atom,x,y,w,h){return {atom:atom,x:x,y:y,w:w,h:h};}
function setup(){window.MulerQuizTarget=null;_target=[];_purpose='free';allAtomsTypeList=['C','C'];bondList=[[1,2,1]];_geom={med:750,groups:[{bond:0,lines:[{x1:4221,y1:2528,x2:4971,y2:2528}]}],anchors:[label(0,4385.966064453125,2586.3636474609375,330,290),label(1,5135.966064453125,2586.3636474609375,330,290)],comp:[],verts:[{x:4221,y:2528},{x:4971,y:2528}],vassign:[0,1]};}
test('measured condensed ethane midpoint selects actual C-C bond',function(){setup();same(fMulerSelectPick(4596,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('direct visible carbon label retains atom priority over bond corridor',function(){setup();same(fMulerSelectPick(4385.966064453125,2586.3636474609375),{kind:'atom',atom:1});});
test('wide visible formula label remains selectable beyond loose atom radius',function(){setup();_geom.anchors=[label(0,4385,2586,900,290)];same(fMulerSelectPick(4770,2586),{kind:'atom',atom:1});});
test('bond-purpose armed mission retains native bond endpoint result',function(){setup();window.MulerQuizTarget='compBondType';_purpose='bond';same(fMulerSelectPick(4596,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('parallel multiple-bond strokes retain their source bond identity',function(){setup();bondList=[[1,2,2]];_geom.groups[0].lines.push({x1:4221,y1:2590,x2:4971,y2:2590});same(fMulerSelectPick(4596,2590),{kind:'bond',bond:1,pair:[1,2]});});
test('diagonal bond corridor remains selectable between implicit vertices',function(){setup();_geom.anchors=[];_geom.groups[0].lines=[{x1:0,y1:0,x2:600,y2:600}];_geom.verts=[{x:0,y:0},{x:600,y:600}];same(fMulerSelectPick(300,300),{kind:'bond',bond:1,pair:[1,2]});});
test('main-chain armed mission ignores actual bond interior',function(){setup();window.MulerQuizTarget='compCarbonsCount';_purpose='mainChain';same(fMulerSelectPick(4596,2528),{ignore:true});});
test('FG atom-only mission ignores actual bond interior',function(){setup();window.MulerQuizTarget='compSuffix';_purpose='fg';same(fMulerSelectPick(4596,2528),{ignore:true});});
test('loose atom fallback remains available away from any bond or vertex',function(){setup();_geom.verts=[];_geom.vassign=[];same(fMulerSelectPick(4385,2800),{kind:'atom',atom:1});});
test('isolated atom retains loose fallback without bond groups',function(){setup();_geom.groups=null;_geom.anchors=[label(0,100,100,30,30)];_geom.verts=[];same(fMulerSelectPick(250,100),{kind:'atom',atom:1});});
test('empty canvas still returns null',function(){setup();same(fMulerSelectPick(8000,8000),null);});
test('expanded free H label remains literal H selection',function(){setup();allAtomsTypeList=['C','H'];_geom.anchors=[label(0,4221,2528,130,180),label(1,4971,2528,100,180)];same(fMulerSelectPick(4971,2528),{kind:'atom',atom:2});});
test('expanded armed non-target H retains native parent redirect',function(){setup();allAtomsTypeList=['C','H'];_geom.anchors=[label(0,4221,2528,130,180),label(1,4971,2528,100,180)];window.MulerQuizTarget='compCarbonsCount';_purpose='mainChain';_target=[1];same(fMulerSelectPick(4971,2528),{kind:'atom',atom:1});});
test('expanded target H remains distinct in armed mission',function(){setup();allAtomsTypeList=['C','H'];_geom.anchors=[label(0,4221,2528,130,180),label(1,4971,2528,100,180)];window.MulerQuizTarget='compSuffix';_purpose='fg';_target=[2];same(fMulerSelectPick(4971,2528),{kind:'atom',atom:2});});
test('skeletal implicit vertex retains topological atom identity',function(){setup();_geom.anchors=[];same(fMulerSelectPick(4221,2528),{kind:'atom',atom:1,vertex:0});});
test('skeletal hetero glyph takes priority at its vertex',function(){setup();allAtomsTypeList=['O','C'];_geom.anchors=[label(0,4221,2528,180,200)];same(fMulerSelectPick(4221,2528),{kind:'atom',atom:1});});
function compactSetup(){setup();_geom.comp=[{anchor:0,symbol:'C',members:[1,3,4],el:{getBBox:function(){return{x:4300,y:2400,width:300,height:250};}},textBox:{x:4300,y:2400,w:300,h:250},box:{x:4270,y:2370,w:360,h:310},atomBox:{x:4300,y:2400,w:80,h:250}}];}
test('compacted free label retains whole fragment priority',function(){compactSetup();same(fMulerSelectPick(4500,2500),{kind:'fragment',atoms:[1,3,4],compactGroupBox:_geom.comp[0].textBox});});
test('compacted main-chain label retains carbon anchor-only policy',function(){compactSetup();_purpose='mainChain';window.MulerQuizTarget='compCarbonsCount';same(fMulerSelectPick(4500,2500),{kind:'atom',atom:1,compactAnchor:true,compactAtomBox:_geom.comp[0].atomBox});});
test('compacted N/S group retains whole-fragment policy during main-chain purpose',function(){compactSetup();_geom.comp[0].symbol='N';allAtomsTypeList[0]='N';_purpose='mainChain';window.MulerQuizTarget='compCarbonsCount';same(fMulerSelectPick(4500,2500),{kind:'fragment',atoms:[1,3,4],compactGroupBox:_geom.comp[0].box});});
print(JSON.stringify({cases:results.length,passed:results.filter(function(r){return r.pass;}).length,results:results}));
if(results.some(function(r){return !r.pass;}))quit(1);
