function fMulerSelectHeteroAnchors(groups) {
  var out = [];
  try {
    var ownedLabels = null;
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
    if (typeof molSvg === "undefined" || !molSvg) return out;
    if (typeof bondList === "undefined" || !bondList || !bondList.length) return out;
    if (typeof allAtomsTypeList === "undefined" || !allAtomsTypeList) return out;
    if (!groups || !groups.length) return out;
    var med = 0;
    try { med = (typeof fMulerSelectMedianBond === "function") ? fMulerSelectMedianBond(groups) : 0; } catch (eM) { med = 0; }
    if (!(med > 0)) return out;
    var texts = [];
    try {
      var textEls = molSvg.selectAll("text");
      for (var ti = 0; ti < textEls.length; ti++) {
        var tel = textEls[ti], tnd = tel && tel.node ? tel.node : null;
        if (!tnd || !tnd.getAttribute) continue;
        try {
          var tid = String(tnd.getAttribute("id") || "");
          if (tid.indexOf("number") === 0 || tid.indexOf("mulerSelNum") === 0) continue;
          if (tnd.getAttribute("data-muler-hidden")) continue;
          if (tnd.style && tnd.style.display === "none") continue;
        } catch (eA) { continue; }
        var tc = "";
        try { tc = String(tnd.textContent || "").replace(/\s+/g, ""); } catch (eT) { tc = ""; }
        if (!tc) continue;
        var bb = null;
        try { bb = tnd.getBBox ? tnd.getBBox() : null; } catch (eB) { bb = null; }
        if (!bb || !(bb.width > 0 && bb.height > 0)) continue;
        var m = tc.match(/[A-Za-z]/);
        texts.push({ x: bb.x + bb.width / 2, y: bb.y + bb.height / 2, w: bb.width, h: bb.height, sym: m ? m[0].toUpperCase() : "" });
      }
    } catch (eT2) {}
    if (!texts.length) return out;
    var heteros = [];
    try {
      for (var ai = 0; ai < allAtomsTypeList.length; ai++) {
        var es = allAtomsTypeList[ai];
        if (es !== "C" && es !== "H") heteros.push(ai);
      }
    } catch (eH2) {}
    if (!heteros.length) return out;
    var byBond = {};
    try { for (var gi = 0; gi < groups.length; gi++) byBond[groups[gi].bond] = groups[gi]; } catch (eG) {}
    var pairs = [];
    for (var hi = 0; hi < heteros.length; hi++) {
      var hat = heteros[hi], hElem = "";
      try { hElem = String(allAtomsTypeList[hat] || "").toUpperCase().charAt(0); } catch (eE) { hElem = ""; }
      for (var b = 0; b < bondList.length; b++) {
        if (!bondList[b]) continue;
        if (bondList[b][0] !== hat + 1 && bondList[b][1] !== hat + 1) continue;
        var G = byBond[b];
        if (!G || !G.lines) continue;
        for (var li = 0; li < G.lines.length; li++) {
          var L = G.lines[li];
          var ends = [[L.x1, L.y1], [L.x2, L.y2]];
          for (var ei = 0; ei < 2; ei++) {
            for (var tj = 0; tj < texts.length; tj++) {
              var dx = texts[tj].x - ends[ei][0], dy = texts[tj].y - ends[ei][1];
              if (dx * dx + dy * dy > med * med) continue;
              var sc = Math.sqrt(dx * dx + dy * dy);
              if (texts[tj].sym && hElem && texts[tj].sym !== hElem) sc += med;
              pairs.push({ atom: hat, text: tj, dist: sc });
            }
          }
        }
      }
    }
    pairs.sort(function (p, q) { return p.dist - q.dist; });
    var usedText = {}, usedAtom = {};
    for (var pi = 0; pi < pairs.length; pi++) {
      var P = pairs[pi];
      if (usedText[P.text] || usedAtom[P.atom]) continue;
      usedText[P.text] = true; usedAtom[P.atom] = true;
      try { out.push({ atom: P.atom, x: texts[P.text].x, y: texts[P.text].y, w: texts[P.text].w, h: texts[P.text].h }); } catch (eP) {}
    }
  } catch (e) {}
  return out;
}


function fGetRenderedAtomTextMap(
  includeCompactedAtoms = false,
  includeHydrogens = false,
) {
  const atomTextMap = {};
  // The native producer supplies actual atom IDs, even when skeletal C is omitted.
  const owned = molSvg.selectAll('text[data-namelecule-atom][data-namelecule-role="label"]');
  if (owned.length) {
    owned.forEach(el => {
      const index = Number(el.node.getAttribute('data-namelecule-atom')) - 1;
      if (Number.isInteger(index) && index >= 0 &&
          (includeHydrogens || allAtomsTypeList[index] !== 'H')) atomTextMap[index] = el;
    });
    return atomTextMap;
  }
  const textEls = molSvg.selectAll("text");
  const skipIndices = fGetCompactedAtomSkipSet(includeCompactedAtoms);

  let textIdx = 0;
  for (let atomIdx = 0; atomIdx < allAtomsTypeList.length; atomIdx++) {
    if (allAtomsTypeList[atomIdx] === "H" && !includeHydrogens) {
      continue;
    }
    if (skipIndices.has(atomIdx)) {
      continue;
    }
    if (textIdx >= textEls.length) {
      break;
    }
    atomTextMap[atomIdx] = textEls[textIdx];
    textIdx += 1;
  }
  return atomTextMap;
}


function fBuildMoleculeSVG() {
  if (!jsmeNomeclatureApplet) return;
  // Stage 1 precedes native label layout. Stage 2 is fFit2DSVG below, after
  // functional labels are finalized. Numbering/highlights reuse stable atom IDs.
  fApplySkeletalLayout();
  // Selection state into the applet BEFORE the SVG string is read, so the
  // render below already carries the merged component+selection colors.
  try { if (typeof fMulerSelectPushState === "function") fMulerSelectPushState(); } catch (eSelPush) {}
  // Fresh line layout per render: the compaction below records its removed
  // bonds for the selection line groups (stale indices would shift picks).
  try { if (typeof window !== "undefined") window.__mulerRemovedBondIdx = []; } catch (eRB2) {}
  // Render epoch for the selection geometry cache (hover reads it at 60 Hz;
  // zoom/repaint bumps it so cached hit-testing never goes stale).
  try { if (typeof window !== "undefined") window.__mulerSelRenderSeq = ((typeof window.__mulerSelRenderSeq === "number") ? window.__mulerSelRenderSeq : 0) + 1; } catch (eSq) {}
  compactNumberingLabelMap = {};
  let mySVG = jsmeNomeclatureApplet.getMolecularAreaGraphicsString();
  // Fix JSME highlight malformation BEFORE HTML parsing
  // Bug 1: fill/stroke attributes corrupted for all highlighted atoms
  mySVG = mySVG.replace(
    /fill="([^"]*?) stroke=" ([^"]*)"="" stroke-width="([^"]*)"/g,
    'fill="$1" stroke="$2" stroke-width="$3"',
  );
  // Bug 2 (N-type: stroke-width absorbs atom label via literal >) is NOT sanitised
  // here — the absorbed content may contain double-quoted tspan attributes (e.g.
  // font-size="80%") which break any [^"]* regex on the raw string.  The DOM
  // representation leaves the stray '>' inside the attribute value, which
  // patchtheNitrogen detects via getAttribute('stroke-width').indexOf('>').
  $("#jsmeNomeclatureSVG").html(mySVG);
  if (mode2D == "condensed" || mode2D == "condensedZigZag") {
    fAddHydrogens2SVG();
  }
  molSvg = MuSVG("#jsmeNomeclatureSVG svg");
  if (!molSvg) {
    return; // empty SVG (molecule with missing representation): nothing to post-process
  }
  const jsmeLogo = molSvg.select("polygon:last-of-type");
  if (jsmeLogo) {
    jsmeLogo.remove();
  }
  if (mode2D === "expanded") {
    fMarkExpandedHydrogens();
  }
  if (mode2D === "condensed") {
    fCompactFunctionalGroups2D();
  }
  fHideSkeletalSpCarbons();
  patchtheNitrogen();
  fWrapStandaloneHydrogenTextsAsTspan();
  fApplyAtomColors2DToSVGLabels();
  fApplyCHBondColors2D();
  // Hydrogen wrapping may replace the text node, so hide only after labels
  // and colors are finalized, before fitting the visible drawing.
  fHideEsterSkeletalCarbonHydrogens();
  fPrepareFixedCCAlkanePrototype();
  $("#jsmeNomeclatureSVG").toggleClass(
    "svgAtomsColorized",
    svgAtomColors2DFlag,
  );
  fRefreshLabelBackplates();
  fFit2DSVG();
  fValidate2DBondVisibility();
  try { if (typeof fMulerSelectRepaint === "function") fMulerSelectRepaint(); } catch (eSel) { /* selection overlay is best-effort */ }
  try { if (typeof fMulerSelectSeqBadges === "function") fMulerSelectSeqBadges(); } catch (eSeq) { /* sequence badges are best-effort */ }
  try { if (typeof fMulerNumberAid === "function") fMulerNumberAid(); } catch (eAid) { /* numbering aid is best-effort */ }
}

// A font notification owns only 2D work. It must not replay JSmol scripts or
// restart the user's progressive numbering animation.

var results=[];
function assert(v,m){if(!v)throw Error(m);}
function test(name,fn){try{fn();results.push({name:name,pass:true});}catch(e){results.push({name:name,pass:false,error:String(e)});}}
var window=this, mode2D='expanded', compactNumberingLabelMap={}, svgAtomColors2DFlag=false;
var allAtomsTypeList=['C','O','N','H'];
var node=function(atom,symbol,hidden,x){return {dataset:{},style:{display:hidden?'none':''},textContent:symbol,attrs:{'data-namelecule-atom':String(atom),'data-namelecule-role':'label'},getAttribute:function(k){return k==='data-muler-hidden'&&hidden?'spC':this.attrs[k]||null;},hasAttribute:function(k){return !!this.getAttribute(k);},getBBox:function(){return {x:x||0,y:10,width:20,height:30};}};};
var labels=[{node:node(1,'C',true,0)},{node:node(3,'N',false,90)},{node:node(2,'OH',false,50)},{node:node(4,'H',false,130)}];
var molSvg={selectAll:function(sel){return sel.indexOf('text[data-namelecule')===0?labels:[];}};
var document={querySelector:function(){return null;}};
test('skeletal hetero selection follows actual atom IDs despite DOM order',function(){var anchors=fMulerSelectHeteroAnchors(null);assert(anchors.length===2,'hidden C/H were included');var byId={};anchors.forEach(function(a){byId[a.atom]=a;});assert(byId[1].x===60&&byId[2].x===100,'hetero ownership shifted with DOM order');});
test('rendered ownership map keeps source IDs with skeletal omissions',function(){var map=fGetRenderedAtomTextMap(false,false);assert(map[1].node.textContent==='OH'&&map[2].node.textContent==='N'&&!map[3],'wrong atom text ownership or H included');});
// Exercise the actual composed renderer with stage stubs: preparation and
// selection state must precede native SVG read; overlays must follow final
// chemical geometry/metrics/fit, preserving guarded failure handling.
var calls=[], jsmeNomeclatureApplet={getMolecularAreaGraphicsString:function(){calls.push('readSVG');return '<svg></svg>';}};
var $=function(){return {html:function(){calls.push('mountSVG');},toggleClass:function(){}};};
var MuSVG=function(){return {select:function(){return null;}};};
function fApplySkeletalLayout(){calls.push('chemicalGeometry');}
function fMulerSelectPushState(){calls.push('selectionPush');}
function fAddHydrogens2SVG(){calls.push('hydrogens');}
function fMarkExpandedHydrogens(){calls.push('expandedH');}
function fCompactFunctionalGroups2D(){calls.push('compact');}
function fHideSkeletalSpCarbons(){calls.push('sp');}
function patchtheNitrogen(){calls.push('nitrogen');}
function fWrapStandaloneHydrogenTextsAsTspan(){calls.push('wrapH');}
function fApplyAtomColors2DToSVGLabels(){calls.push('atomColor');}
function fApplyCHBondColors2D(){calls.push('bondColor');}
function fHideEsterSkeletalCarbonHydrogens(){calls.push('hideEsterH');}
function fPrepareFixedCCAlkanePrototype(){calls.push('fixedCC');}
function fRefreshLabelBackplates(){calls.push('metrics');}
function fFit2DSVG(){calls.push('fit');}
function fValidate2DBondVisibility(){calls.push('validateVisibleBonds');}
function fMulerSelectRepaint(){calls.push('selectionRepaint');}
function fMulerSelectSeqBadges(){calls.push('sequenceBadges');}
function fMulerNumberAid(){calls.push('numberAid');}
test('composed SVG lifecycle retains local final geometry before native overlays',function(){fBuildMoleculeSVG();for(var pair of [['chemicalGeometry','selectionPush'],['selectionPush','readSVG'],['readSVG','mountSVG'],['hideEsterH','metrics'],['fixedCC','metrics'],['metrics','fit'],['fit','validateVisibleBonds'],['validateVisibleBonds','selectionRepaint'],['selectionRepaint','sequenceBadges'],['sequenceBadges','numberAid']])assert(calls.indexOf(pair[0])<calls.indexOf(pair[1]),pair.join(' must precede '));assert(window.__mulerSelRenderSeq===1&&Array.isArray(window.__mulerRemovedBondIdx),'render epoch/removal cache not reset');});
print(JSON.stringify({cases:results.length,passed:results.filter(function(r){return r.pass;}).length,results:results}));
if(results.some(function(r){return !r.pass;}))quit(1);
