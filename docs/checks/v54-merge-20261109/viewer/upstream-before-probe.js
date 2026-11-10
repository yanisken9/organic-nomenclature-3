var window = this;
var console = { log:function(){}, warn:function(){}, error:function(){} };
var navigator = { onLine:true };
var selectedMol = 'fixture', mode2D = 'condensed';
var allAtomsTypeList=[], bondList=[], allAtomsTypeList3D=[], bondList3D=[];
var mainChainAtomsList=[1,2,3], nameComponentsList=['fixture'], mainChainMode='algorithmic';
var nameExamples={}, nameExamplesCustom={}, molInfoOpenFlag=true;
var jsmeNomeclatureApplet=null, jsmeEditDraftApplet=null;
var jmolAppletNomeclature={id:'applet'}, JSmolReadyFlag=true;
var fMolDraft3DRevision=0, fMolDraft3DJob=null, fMolDraft3DWriter=null;
var MOLMIN_STEPS=500,MOLMIN_FURTHER_STEPS=200,MOLMIN_WAIT_S=10;
var fMolDraftMinWaitEl=null,fMolDraftMinWaitKey=null,fMolDraftMinWaitPrevFocus=null,fMolDraftMinWaitTimer=null,fMolDraftMinWaitJob=null;
var _intervals=[];
function setInterval(fn,ms){var t={fn:fn,ms:ms,cancel:false};_intervals.push(t);return t;}
function clearInterval(t){if(t)t.cancel=true;}
var _timers=[], _writes=[], _reads=[], _model=null, _confirm=null, _toasts=[], _downloads=[];
var _docElements={};
function element() { return {children:[],classList:{add:function(){},remove:function(){},toggle:function(){},contains:function(){return false;}},setAttribute:function(k,v){this[k]=v;},appendChild:function(n){this.children.push(n); n.parentNode=this;},removeChild:function(n){this.children=this.children.filter(function(x){return x!==n;});},querySelector:function(k){this.queries=this.queries||{};return this.queries[k]||(this.queries[k]=element());},focus:function(){},style:{setProperty:function(){}}}; }
var document={getElementById:function(id){return _docElements[id] || null;},querySelectorAll:function(){return [];},createElement:element,addEventListener:function(){},removeEventListener:function(){},contains:function(){return false;},body:element(),documentElement:element()};
function setTimeout(fn,ms){var t={fn:fn,ms:ms,cancel:false};_timers.push(t);return t;}
function clearTimeout(t){if(t)t.cancel=true;}
function nextTimer(){var t;while((t=_timers.shift())){if(!t.cancel){t.fn();drainMicrotasks();return t.ms;}}return null;}
function settle(p){var done=false,val,err;p.then(function(v){done=true;val=v;},function(e){done=true;err=e;});drainMicrotasks();for(var i=0;!done&&i<30;i++){if(nextTimer()===null)break;}if(err)throw err;if(!done)throw Error('unsettled promise');return val;}
function fMolDraftPresenting(){return false;}
function fJSmolLive(){return true;}
function fMulerNotePending3D(){}
function fMolDraftT(k,f){return f || k;}
function fMulerT(k){return k==='draft3DProvisional'?'Provisional 3D — geometry and convergence unverified.':k;}
function fMolDraftToast(t){_toasts.push(t);}
function fMolDraftSyncBar(){}
function fMolDraftRenderPreview(){}
function fMolDraftShow3D(s){_model=s;}
function fMolDraftIsSameMolecule(){return !!window.MulerDraft.same;}
function fMolDraftRefreshAcceptKey(){}
function fMolDraftReadDrawing(){return {hasAny:true,molText:window.MulerDraft.molText,smiles:window.MulerDraft.smiles};}
function fMolDraftMakeKey(){return 'custom_new';}
function fMolDraftExpandedFormula(){return 'C3H8';}
function fGetMoleculeClassification(){return {chemicalClass:'alkanes'};}
function fMolDraftTeardownDisplay(){fMolDraft3DInvalidate();window.MulerDraft=null;}
function fInitNomeclatureMenu(){}
function fSelectMol(){}
function fMolDraftSyncButtons(){}
function fScenarioConfirm(msg,cb,label){_confirm={msg:msg,cb:cb,label:label};}
function fMolDraftFileSlug(rec){return rec.key+'.js';}
function Blob(parts,opts){this.parts=parts;this.type=opts.type;}
function fScenarioSaveBlobDownload(file,blob){_downloads.push({file:file,text:blob.parts.join('')});return true;}
var Jmol={script:function(a,cmd){_writes.push(cmd);if(cmd.indexOf('load data "model.sdf"')>=0){_model=cmd.split('load data "model.sdf"\n')[1].split('end "model.sdf"')[0];}return '';},scriptWait:function(a,cmd){return this.script(a,cmd);},scriptEcho:function(a,cmd){_reads.push(cmd);return _model;}};
function assert(ok,msg){if(!ok)throw Error(msg);}
var results=[];
function test(name,fn){try{fn();results.push({name:name,pass:true});}catch(e){results.push({name:name,pass:false,error:String(e)});}}
function atom(el,x,y,z,extra){return Object.assign({el:el,x:x,y:y,z:z||0},extra||{});}
function mol(atoms,bonds){return fWriteMolV2000(['fixture','  fixture 3D',''],atoms,bonds,{});}
function fixture(){return mol([atom('C',0,0,0),atom('C',1,0,0),atom('C',2,0,0)],[[1,2,1],[2,3,1]]);}
function reset(){fMolDraft3DInvalidate();_timers=[];_intervals=[];_writes=[];_reads=[];_confirm=null;_toasts=[];_downloads=[];selectedMol='fixture';mode2D='condensed';jsmeNomeclatureApplet=null;jsmeEditDraftApplet=null;nameExamples={};nameExamplesCustom={};window.MulerDraftAcquisition=null;window._mulerNewCustomKeys={};window.MULER_SKIP_REMOTE3D=false;navigator.onLine=true;_model=fixture();window.MulerDraft={_epoch:1,_submitId:1,smiles:'CCC',molText:fixture(),submitted:true,sdfDone:true,engineName:'προπάνιο',pubchem:null,expectHeavy:3,mode:'new',variant:'condensed',stale:false};}

function fMolCountsLine(lines) {
  try {
    if (!lines || !lines.length) return -1;
    for (var i = 0, lim = Math.min(lines.length, 8); i < lim; i++) {
      var L = lines[i];
      if (typeof L !== 'string' || !/\bV2000\b/.test(L)) continue;
      if (/^\d{1,3}$/.test(L.substring(0, 3).trim()) &&
          /^\d{1,3}$/.test(L.substring(3, 6).trim())) return i;
    }
    // Older library SDFs omit the version tag. Preserve their existing strict
    // standard-header read without treating arbitrary short-header lines as counts.
    var legacy = lines[3];
    if (typeof legacy === 'string' && !/V\d+/.test(legacy) &&
        /^\d{1,3}$/.test(legacy.substring(0, 3).trim()) &&
        /^\d{1,3}$/.test(legacy.substring(3, 6).trim())) return 3;
  } catch (e) {}
  return -1;
}


function fParseMolV2000(text) {
  try {
    if (!text) return null;
    var lines = String(text).split(/\r?\n/);
    var ci = fMolCountsLine(lines);
    if (ci < 0) return null;
    var nA = Number(lines[ci].substring(0, 3)), nB = Number(lines[ci].substring(3, 6));
    if (!Number.isInteger(nA) || !Number.isInteger(nB) || nA < 0 || nB < 0 || lines.length < ci + 1 + nA + nB) return null;
    var atoms = [], bonds = [], chargeCodes = { 0: 0, 1: 3, 2: 2, 3: 1, 4: 0, 5: -1, 6: -2, 7: -3 };
    for (var i = 0; i < nA; i++) {
      var L = lines[ci + 1 + i], code = Number(L.substring(36, 39));
      var x = Number(L.substring(0, 10)), y = Number(L.substring(10, 20)), z = Number(L.substring(20, 30));
      var el = L.substring(31, 34).trim();
      if (L.length < 34 || !el || !Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(z) || !(code in chargeCodes)) return null;
      atoms.push({ sourceIndex: i + 1, x: x, y: y, z: z, el: el, tail: L.substring(34), charge: chargeCodes[code],
        massDifference: Number(L.substring(34, 36)), isotope: null, radical: code === 4 ? 2 : 0,
        parity: Number(L.substring(39, 42)), hydrogenCount: Number(L.substring(42, 45)),
        valence: Number(L.substring(48, 51)) });
    }
    for (var j = 0; j < nB; j++) {
      var B = lines[ci + 1 + nA + j], a = Number(B.substring(0, 3)), b = Number(B.substring(3, 6)), o = Number(B.substring(6, 9));
      if (!Number.isInteger(a) || !Number.isInteger(b) || a < 1 || a > nA || b < 1 || b > nA || a === b || !Number.isInteger(o) || o < 1) return null;
      var bond = [a, b, o]; bond.tail = B.substring(9); bond.sourceIndex = j + 1; bonds.push(bond);
    }
    var properties = [], ended = false;
    for (var k = ci + 1 + nA + nB; k < lines.length; k++) {
      var P = lines[k];
      if (/^M  END\s*$/.test(P)) { ended = true; break; }
      if (!P.trim()) continue;
      var match = /^M  (CHG|ISO|RAD)\s+/.exec(P);
      if (!match) { properties.push(P); continue; }
      var fields = P.trim().split(/\s+/), count = Number(fields[2]);
      if (!Number.isInteger(count) || count < 1 || fields.length !== 3 + 2 * count) return null;
      for (var q = 0; q < count; q++) {
        var index = Number(fields[3 + q * 2]), value = Number(fields[4 + q * 2]);
        if (!Number.isInteger(index) || index < 1 || index > nA || !Number.isInteger(value)) return null;
        atoms[index - 1][{ CHG: 'charge', ISO: 'isotope', RAD: 'radical' }[match[1]]] = value;
      }
    }
    if (!ended) return null;
    var head = lines.slice(Math.max(0, ci - 3), ci);
    while (head.length < 3) head.unshift('');
    return { head: head, countsTail: lines[ci].substring(6), atoms: atoms, bonds: bonds, properties: properties };
  } catch (e) { return null; }
}

// Preserve atom/bond fields and known atom-indexed properties. Layout/stripping
// reject unsupported annotations below; a plain parse/write can retain them.

function fWriteMolV2000(head, atoms, bonds, metadata) {
  try {
    if (atoms.length > 999 || bonds.length > 999) return null;
    var out = [], chargePairs = [], isotopePairs = [], radicalPairs = [];
    out.push(head && head[0] != null ? head[0] : '');
    out.push(head && head[1] != null ? head[1] : '  MuLERMoC 2D');
    out.push(head && head[2] != null ? head[2] : '');
    out.push(String(atoms.length).padStart(3, ' ') + String(bonds.length).padStart(3, ' ') +
      (metadata && metadata.countsTail || '  0  0  0  0  0  0  0  0  0  0999 V2000'));
    for (var i = 0; i < atoms.length; i++) {
      var a = atoms[i], tail = a.tail != null ? a.tail : ' 0  0  0  0  0  0  0  0  0  0  0  0';
      var charge = a.charge || 0, code = ({ 3: 1, 2: 2, 1: 3, '-1': 5, '-2': 6, '-3': 7 })[charge] || 0;
      tail = tail.padEnd(5, ' '); tail = tail.substring(0, 2) + String(code).padStart(3, ' ') + tail.substring(5);
      out.push(a.x.toFixed(4).padStart(10, ' ') + a.y.toFixed(4).padStart(10, ' ') +
        Number(a.z || 0).toFixed(4).padStart(10, ' ') + ' ' + String(a.el || 'C').padEnd(3, ' ') + tail);
      if (charge) chargePairs.push([i + 1, charge]);
      if (a.isotope != null && a.isotope !== 0) isotopePairs.push([i + 1, a.isotope]);
      if (a.radical) radicalPairs.push([i + 1, a.radical]);
    }
    for (var j = 0; j < bonds.length; j++) {
      var b = bonds[j];
      out.push(String(b[0]).padStart(3, ' ') + String(b[1]).padStart(3, ' ') + String(b[2]).padStart(3, ' ') +
        (b.tail != null ? b.tail : '  0  0  0'));
    }
    if (metadata && metadata.properties) {
      var properties = fRemapMolProperties2D(metadata, atoms, bonds);
      if (!properties) return null;
      out.push.apply(out, properties);
    }
    function property(kind, pairs) {
      for (var at = 0; at < pairs.length; at += 8) {
        var group = pairs.slice(at, at + 8);
        out.push('M  ' + kind + String(group.length).padStart(3, ' ') + group.map(function (p) {
          return String(p[0]).padStart(4, ' ') + String(p[1]).padStart(4, ' ');
        }).join(''));
      }
    }
    property('CHG', chargePairs); property('ISO', isotopePairs); property('RAD', radicalPairs);
    out.push('M  END');
    return out.join('\n') + '\n';
  } catch (e) { return null; }
}

// Bounded SUP Sgroup support covers the library's expanded abbreviations.
// Atom/bond lists follow reindexing; new H join their parent's group, and
// crossing-bond vectors follow the new coordinates. Other group types/records
// cannot be safely interpreted here and reject the transformation.

function fRemapMolProperties2D(m, atoms, bonds) {
  try {
    var atomMap = {}, bondMap = {}, groups = {}, declared = {}, emitted = {}, out = [];
    atoms.forEach(function (a, i) { if (a.sourceIndex) atomMap[a.sourceIndex] = i + 1; });
    bonds.forEach(function (b, i) { if (b.sourceIndex) bondMap[b.sourceIndex] = i + 1; });
    for (var i = 0; i < m.properties.length; i++) {
      var line = m.properties[i], fields = line.trim().split(/\s+/), kind = fields[1];
      if (kind === 'STY') {
        var count = Number(fields[2]);
        if (!Number.isInteger(count) || count < 1 || fields.length !== 3 + 2 * count) return null;
        for (var j = 0; j < count; j++) {
          if (fields[4 + 2 * j] !== 'SUP') return null;
          declared[fields[3 + 2 * j]] = true;
        }
      } else if (kind === 'SAL') {
        var g = fields[2], n = Number(fields[3]), members = fields.slice(4).map(Number);
        if (members.length !== n || members.some(function (x) { return !Number.isInteger(x) || x < 1 || x > m.atoms.length; })) return null;
        groups[g] = (groups[g] || []).concat(members);
      } else if (!['SLB','SBL','SMT','SBV'].includes(kind)) return null;
    }
    if (Object.keys(groups).some(function (g) { return !declared[g]; })) return null;
    function list(kind, group, values) {
      if (!values.length) return false;
      for (var k = 0; k < values.length; k += 15) {
        var part = values.slice(k, k + 15);
        out.push('M  ' + kind + String(group).padStart(4, ' ') + String(part.length).padStart(3, ' ') +
          part.map(function (x) { return String(x).padStart(4, ' '); }).join(''));
      }
      return true;
    }
    for (var at = 0; at < m.properties.length; at++) {
      var P = m.properties[at], f = P.trim().split(/\s+/), type = f[1];
      if (type === 'SAL') {
        if (emitted[f[2]]) continue;
        emitted[f[2]] = true;
        var members = groups[f[2]], mapped = members.filter(function (x) { return atomMap[x] != null; })
          .map(function (x) { return atomMap[x]; });
        atoms.forEach(function (a, index) {
          if (a.parentSourceIndex && members.includes(a.parentSourceIndex)) mapped.push(index + 1);
        });
        if (!list(type, f[2], mapped)) return null;
      } else if (type === 'SBL') {
        var count = Number(f[3]), ids = f.slice(4).map(Number);
        if (ids.length !== count || ids.some(function (x) { return !Number.isInteger(x) || x < 1 || x > m.bonds.length; })) return null;
        var mappedBonds = ids.filter(function (x) { return bondMap[x] != null; }).map(function (x) { return bondMap[x]; });
        if (!list(type, f[2], mappedBonds)) return null;
      } else if (type === 'SBV') {
        var newBond = bondMap[Number(f[3])], group = groups[f[2]];
        if (!newBond || !group) return null;
        var b = bonds[newBond - 1], sourceBond = m.bonds[Number(f[3]) - 1];
        var firstInside = group.includes(sourceBond[0]), secondInside = group.includes(sourceBond[1]);
        if (firstInside === secondInside) return null;
        var inside = atoms[(firstInside ? b[0] : b[1]) - 1], outside = atoms[(firstInside ? b[1] : b[0]) - 1];
        out.push('M  SBV' + String(f[2]).padStart(4, ' ') + String(newBond).padStart(4, ' ') +
          (outside.x - inside.x).toFixed(4).padStart(10, ' ') + (outside.y - inside.y).toFixed(4).padStart(10, ' '));
      } else out.push(P);
    }
    return out;
  } catch (e) { return null; }
}


function fMolCanTransform2D(m, removeHydrogens) {
  if (!m || !m.atoms.length || Number(m.countsTail.substring(6, 9)) ||
      !fRemapMolProperties2D(m, m.atoms, m.bonds)) return false;
  if (m.atoms.some(function (a) {
    return a.parity || a.hydrogenCount || a.valence || a.radical ||
      !['C','N','O','S','P','F','Cl','Br','I','H'].includes(a.el) ||
      (a.el === 'H' && (a.charge || (removeHydrogens && (a.massDifference || a.isotope))));
  })) return false;
  return m.bonds.every(function (b) { return b[2] <= 3 && !Number((b.tail || '').substring(0, 3)); });
}


function fIsHeavyEl2D(el) {
  var s = String(el == null ? "" : el);
  return !(s === "H" || s === "h" || s === "");
}

// Heavy subgraph, atom order and coordinates kept, bonds renumbered.

function fHeavyAdj2D3D(types, bonds) {
    var n = 0
    try { n = types.length } catch (eN) { n = 0 }
    var heavy = {}, adj = [], ord = {}
    for (var i = 0; i < n; i++) {
        var t = null
        try { t = types[i] } catch (eT) {}
        if (t == null) continue
        var s = String(t)
        if (s === "H" || s === "h" || s === "") continue
        heavy[i] = true
        adj[i] = []
    }
    try {
        for (var b = 0; b < bonds.length; b++) {
            var bb = bonds[b]
            if (!bb) continue
            var x = (bb[0] | 0) - 1, y = (bb[1] | 0) - 1, o = bb[2] || 1
            if (!heavy[x] || !heavy[y]) continue
            adj[x].push(y); adj[y].push(x)
            var k = (x < y) ? x + "-" + y : y + "-" + x
            if (!ord[k] || ord[k] < o) ord[k] = o
        }
    } catch (eB) {}
    return { adj: adj, ord: ord, heavy: heavy }
}


function fMolDraftValidSDF3D(sdf, expectHeavy) {
  try {
    if (!sdf || sdf.indexOf("V2000") < 0) return false;
    if (typeof fParseMolV2000 !== "function") return true;
    var p = fParseMolV2000(sdf);
    if (!p || !p.atoms || !p.atoms.length) return false;
    // z-spread over HEAVY atoms only (v55.7): light-H numerical noise can fake
    // spread on an otherwise flat scaffold; a "3D" model with a flat heavy
    // skeleton is not 3D.
    var h = 0, zMin = Infinity, zMax = -Infinity, i;
    for (i = 0; i < p.atoms.length; i++) {
      var e = String(p.atoms[i].el || "");
      if (!e || e === "H" || e === "h") continue;
      h++;
      var z = p.atoms[i].z;
      if (typeof z === "number" && isFinite(z)) { if (z < zMin) zMin = z; if (z > zMax) zMax = z; }
    }
    if (expectHeavy && h !== expectHeavy) return false;
    if (!h) return false;
    if (zMin === Infinity) return true; // 2D-only parse: accept shape, caller decides flatness
    if ((zMax - zMin) < 1e-3) return false; // flat = un-minimized 2D
    return true;
  } catch (eV) { return false; }
}

// Shared SDF read-back (v55.8): `write MOL` only. Translate-test proved it
// the sole live-model serializer in this build (`molFile` returns an
// unparseable column layout; `show MOL` is not a command; `fileContents` is
// a stale dump that never reflects the live model). First V2000-valid
// (heavy count + heavy-only z-spread) wins; method + length + heavy count +
// heavy z-spread + verdict are logged.

function fMolDraftLocal3DRelaxFF(expectHeavy, ffName) {
  return (async function () {
  try {
    var _pre = null;
    try { if (typeof fJSmolScriptEcho === "function") _pre = fJSmolScriptEcho(jmolAppletNomeclature, "write MOL") || null; } catch (eP0) { _pre = null; }
    try {
      if (typeof fJSmolScript === "function") {
        try { fJSmolScript(jmolAppletNomeclature, "set forceField " + ffName + ";"); } catch (eF) {}
        fJSmolScript(jmolAppletNomeclature, "select all; minimize steps 500;");
      }
      else if (typeof fJSmolScriptWait === "function") fJSmolScriptWait(jmolAppletNomeclature, "select all; minimize steps 500;");
      else return null;
    } catch (eM) { return null; }
    try { console.log("[SDF-3D] tier local-min: " + ffName + " minimize fired — single read-back in 25 s, no scripts meanwhile"); } catch (eLgF) {}
    try { await new Promise(function (res) { try { setTimeout(res, 25000); } catch (eT) { try { res(); } catch (eR) {} } }); } catch (eW) {}
    var cand = null;
    try { if (typeof fMolDraftReadBackSDF === "function") cand = fMolDraftReadBackSDF(expectHeavy) || null; } catch (eRb) { cand = null; }
    var moved = false;
    try { if (typeof fMolDraftMeanDisplacement === "function") moved = (fMolDraftMeanDisplacement(_pre, cand) >= 0.05); } catch (eMv) { moved = false; }
    try { console.log("[SDF-3D] tier local-min: " + ffName + " candidate " + (moved ? "moved — accepted" : "unmoved — rejected")); } catch (eLgC) {}
    if (cand && moved) {
      try { if (typeof fJSmolScript === "function") fJSmolScript(jmolAppletNomeclature, "select all; center selected;"); } catch (eC) {}
      return cand;
    }
    return null;
  } catch (e) { return null; }
  })();
}

// MMFF round first (console-proven on this chemistry), UFF fallback.

function fMolDraftLocal3DRelaxBoth(expectHeavy) {
  return (async function () {
  try {
    var _m = null;
    try { if (typeof fMolDraftLocal3DRelaxFF === "function") _m = await fMolDraftLocal3DRelaxFF(expectHeavy, "MMFF") || null; } catch (eM) { _m = null; }
    if (_m) return _m;
    try { console.log("[SDF-3D] tier local-min: MMFF round yielded nothing — retrying UFF"); } catch (eLgR) {}
    var _u = null;
    try { if (typeof fMolDraftLocal3DRelaxFF === "function") _u = await fMolDraftLocal3DRelaxFF(expectHeavy, "UFF") || null; } catch (eU) { _u = null; }
    return _u;
  } catch (e) { return null; }
  })();
}

// One-time start-of-draft preparation (v55.13): zap → untangle → jiggle →
// load → drain-verify → calc-H. Returns {ok}. Repeat presses skip it (the
// live model is already prepared) and continue from the live geometry, so
// every press walks further down.

function fMolDraftManualMinimize() {
  return (async function () {
  try {
    var d = null;
    try { d = window.MulerDraft; } catch (eD) { return; }
    if (!d || (typeof fMolDraftPresenting === "function" && fMolDraftPresenting())) return;
  if (!d.submitted || !d.sdfDone || d.sdf3D || d.submitting || d._minimizing) return;
  var _e = d._epoch, _s = d._submitId, _sm = d.smiles;
  d._minimizing = true;
  try { if (typeof fMolDraftSyncBar === "function") fMolDraftSyncBar(); } catch (eSy) {}
  try {
    var _stM = document.getElementById("molDraftStatus");
    if (_stM) _stM.textContent = fMolDraftT("draftMinimizing", "Minimizing 3D… please wait.");
  } catch (eStM) {}
  var out = null;
  try {
    var _eh = 0;
    try { _eh = (typeof d.expectHeavy === "number" && d.expectHeavy > 0) ? d.expectHeavy : 0; } catch (eEH) {}
    var _lrM = null;
    try { if (typeof fMolDraftLocal3DFromMol === "function") _lrM = await fMolDraftLocal3DFromMol(d.molText, _eh, !!d._minPrepared) || null; } catch (eM2) { _lrM = null; }
    out = (_lrM && _lrM.sdf) || null;
    try { d._minPrepared = !!(_lrM && _lrM.prepared); } catch (eMp) {}
  } catch (eM) { out = null; }
  try { d._minimizing = false; } catch (eMf) {}
  if (!window.MulerDraft || window.MulerDraft !== d || d._epoch !== _e || d._submitId !== _s || d.smiles !== _sm) return;
  try {
    var _stM2 = document.getElementById("molDraftStatus");
    if (_stM2) _stM2.textContent = fMolDraftT("draftPreview", "Preview") + ": " + (d.engineName || "");
  } catch (eStR) {}
  // v55.11: the author judges the geometry, not the heuristics. Always show
  // the OK-only save dialog after the pipeline; OK stores best-effort
  // (validated minimized preferred, live model as explicitly-unminimized
  // fallback) and unlocks Accept. ESC/backdrop = back out, stay locked.
  var _best = null, _bestSrc = null, _bestLive = false;
  if (out) { _best = out; _bestSrc = "jsmol-min"; }
  else {
    try {
      var _w = null;
      try { if (typeof fJSmolScriptEcho === "function") _w = fJSmolScriptEcho(jmolAppletNomeclature, "write MOL") || null; } catch (eW) { _w = null; }
      if (_w && _w.indexOf("V2000") >= 0 && typeof fParseMolV2000 === "function") {
        var _pp = fParseMolV2000(_w), _lhc = 0;
        if (_pp && _pp.atoms) {
          for (var _li = 0; _li < _pp.atoms.length; _li++) { var _le = String(_pp.atoms[_li].el || ""); if (_le && _le !== "H" && _le !== "h") _lhc++; }
          var _eh2 = 0;
          try { _eh2 = (typeof d.expectHeavy === "number" && d.expectHeavy > 0) ? d.expectHeavy : 0; } catch (eEH2) {}
          if (_eh2 && _lhc === _eh2) { _best = _w; _bestSrc = "jsmol-unminimized"; _bestLive = true; }
        }
      }
    } catch (eL) { _best = null; _bestSrc = null; _bestLive = false; }
  }
  var _storeBest = function () {
    try {
      if (!window.MulerDraft || window.MulerDraft !== d || d._epoch !== _e || d._submitId !== _s || d.smiles !== _sm) return;
      if (!_best) {
        try { fMolDraftToast(fMolDraftT("submitNo3DAll", "No 3D model (PubChem/remote/local minimize) — 2D only.")); } catch (eT) {}
        try { fMolDraftRenderPreview(); } catch (eR0) {}
        try { if (typeof fMolDraftSyncBar === "function") fMolDraftSyncBar(); } catch (eSy0) {}
        return;
      }
      d.sdf3D = _best;
      d.sdf3DSource = _bestSrc || "jsmol-unminimized";
      try { if (typeof fMolDraftShow3D === "function") fMolDraftShow3D(_best); } catch (eS3) {}
      if (!_bestLive) {
        try { fMolDraftToast(fMolDraftT("draftMinDone", "3D minimized locally — review the model, then Accept.")); } catch (eTd) {}
      } else {
        try { fMolDraftToast(fMolDraftT("draftMinUnminDone", "Unoptimized 3D saved — review it, then Accept.")); } catch (eTd2) {}
      }
      try { fMolDraftRenderPreview(); } catch (eR2) {}
      try { if (typeof fMolDraftSyncBar === "function") fMolDraftSyncBar(); } catch (eSy3) {}
    } catch (eCb) {}
  };
  var _msg = "";
  try { _msg = fMolDraftT("draftMinSave3D", "Save the 3D conformation of the molecule once geometry optimization completes."); } catch (eMm) { _msg = "Save the 3D conformation of the molecule once geometry optimization completes."; }
  try {
    if (typeof fMolDraftMinimizeDialog === "function") fMolDraftMinimizeDialog(_msg, _storeBest);
    else _storeBest();
  } catch (eDg) { try { _storeBest(); } catch (eFb) {} }
  } catch (eOuter) {}
  })();
}

// Tier-2 remote 3D via JSmol `load $SMILES` (v55.1): JSmol resolves `$`
// itself through its configured server proxy (CDN jsmol.php, and verified
// working with local JSmol files too) — no page-side fetch, hence no CORS
// wall like the retired direct Cactus fetch. scriptWait blocks until the
// remote model lands; the SDF text is read back via the shared battery.
// Null on any gap (offline, unknown SMILES, JSmol dead).

var _modelName='original';
function fMolDraftReadBackSDF(){_reads.push(_modelName);return 'candidate';}
function fMolDraftMeanDisplacement(){return 0;}
function fJSmolScript(a,c){_writes.push(_modelName+':'+c);return '';}
var wrong=mol([atom('C',0,0),atom('N',1,0,1),atom('O',2,1,0)],[[1,2,1],[2,3,1]]);
var methane=mol([atom('C',0,0)],[]);
assert(fMolDraftValidSDF3D(wrong,3),'before mismatch did not reproduce');
assert(!fMolDraftValidSDF3D(methane,1),'before methane failure did not reproduce');
var p=fMolDraftLocal3DRelaxBoth(3);drainMicrotasks();_modelName='replacement';settle(p);
assert(_reads.indexOf('replacement')>=0&&_writes.some(function(c){return /replacement:.*UFF/.test(c);}), 'before stale UFF failure did not reproduce');
print(JSON.stringify({reproduced:['CV55-04 wrong identity same heavy count accepted','CV55-06 one-heavy methane rejected','VV55-01 replacement read and UFF fired after first wait'],writes:_writes,reads:_reads}));

function fMolDraft3DInvalidate() {}
function fJSmolScriptEcho(){return _model;}
var calls=0;
fMolDraftLocal3DFromMol=async function(){calls++;return {sdf:null,prepared:false};};
fMolDraftMinimizeDialog=function(msg,cb){cb();};
reset();window.MulerDraft.sdf3D=fixture();window.MulerDraft.sdf3DSource='jsmol-unminimized';settle(fMolDraftManualMinimize());assert(calls===0,'before retry failure did not reproduce');
reset();settle(fMolDraftManualMinimize());assert(window.MulerDraft.sdf3DSource==='jsmol-unminimized'&&!window.MulerDraft.sdf3DStatus&&!window.MulerDraft.sdf3DProvenance,'before durable status gap did not reproduce');
print(JSON.stringify({reproduced:['VV55-02 existing provisional SDF prevents visible manual retry','CV55-05 explicit manual OK stores fallback without durable provisional status'],source:window.MulerDraft.sdf3DSource,status:window.MulerDraft.sdf3DStatus||null}));
