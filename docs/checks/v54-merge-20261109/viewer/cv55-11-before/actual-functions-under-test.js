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


function fOrderOf2D3D(ord, a, b) {
    var k = (a < b) ? a + "-" + b : b + "-" + a
    return ord[k] || 1
}


function fBuildHeavyMap2D3D(ignoreOrder) {
    try {
        if (typeof allAtomsTypeList === "undefined" || typeof allAtomsTypeList3D === "undefined") return null
        if (typeof bondList === "undefined" || typeof bondList3D === "undefined") return null
        if (!allAtomsTypeList || !allAtomsTypeList3D || !bondList || !bondList3D) return null
        var A = fHeavyAdj2D3D(allAtomsTypeList, bondList)
        var B = fHeavyAdj2D3D(allAtomsTypeList3D, bondList3D)
        var N2 = [], N3 = [], degA = {}, degB = {}
        for (var i in A.heavy) { i = +i; N2.push(i); degA[i] = A.adj[i].length }
        for (var j in B.heavy) { j = +j; N3.push(j); degB[j] = B.adj[j].length }
        if (!N2.length || N2.length !== N3.length) return null
        var elA = function (x) { try { return String(allAtomsTypeList[x]) } catch (e) { return "" } }
        var elB = function (y) { try { return String(allAtomsTypeList3D[y]) } catch (e) { return "" } }
        // Rare-element / high-degree first: tiny search tree on these graphs.
        N2.sort(function (p, q) {
            if (degA[q] !== degA[p]) return degA[q] - degA[p]
            if (elA(p) < elA(q)) return -1
            if (elA(p) > elA(q)) return 1
            return p - q
        })
        var assign = {}, used = {}
        var consistent = function (x, y) {
            var nbrs = A.adj[x] || []
            for (var k = 0; k < nbrs.length; k++) {
                var nx = nbrs[k]
                if (!(nx in assign)) continue
                var ny = assign[nx]
                if ((B.adj[y] || []).indexOf(ny) < 0) return false
                if (!ignoreOrder && fOrderOf2D3D(B.ord, y, ny) !== fOrderOf2D3D(A.ord, x, nx)) return false
            }
            // Reverse: every already-mapped 3D neighbor of y must be the image
            // of a 2D neighbor of x (forward-only checks admit spurious maps).
            var yNbrs = B.adj[y] || []
            for (var r = 0; r < yNbrs.length; r++) {
                var ny2 = yNbrs[r], wx = null
                for (var q in assign) { if (assign[q] === ny2) { wx = +q; break } }
                if (wx === null) continue
                if (nbrs.indexOf(wx) < 0) return false
                if (!ignoreOrder && fOrderOf2D3D(A.ord, x, wx) !== fOrderOf2D3D(B.ord, y, ny2)) return false
            }
            return true
        }
        var bt = function (pos) {
            if (pos >= N2.length) return true
            var x = N2[pos]
            for (var c = 0; c < N3.length; c++) {
                var y = N3[c]
                if (used[y]) continue
                if (elB(y) !== elA(x)) continue
                if (degB[y] !== degA[x]) continue
                assign[x] = y; used[y] = true
                if (consistent(x, y) && bt(pos + 1)) return true
                delete assign[x]; used[y] = false
            }
            return false
        }
        if (!bt(0)) return null
        var arr = []
        try { arr.length = allAtomsTypeList.length } catch (eL) {}
        for (var m in assign) arr[+m] = assign[m]
        return { arr: arr, adj3: B.adj, n2: allAtomsTypeList.length, n3: allAtomsTypeList3D.length }
    } catch (e) { return null }
}

// Translate a 1-based 2D (JSME) chain to 1-based 3D (SDF/JSmol atomno) positions.
// Null when no exact correspondence exists (caller falls back to signature,
// then ordinal, then leaves 3D untouched).

function fCopyMolAtom2D(a, x, y) {
  return Object.assign({}, a, { x: x == null ? a.x : x, y: y == null ? a.y : y });
}


function fCopyMolBond2D(b, a, c) {
  var copy = [a, c, b[2]]; copy.tail = b.tail; copy.sourceIndex = b.sourceIndex; return copy;
}


function fStripHydrogensMol(text) {
  try {
    var m = fParseMolV2000(text);
    if (!fMolCanTransform2D(m, true)) return null;
    var map = {}, atoms = [];
    for (var i = 0; i < m.atoms.length; i++) {
      if (!fIsHeavyEl2D(m.atoms[i].el)) continue;
      map[i + 1] = atoms.length + 1;
      atoms.push(fCopyMolAtom2D(m.atoms[i]));
    }
    if (!atoms.length) return null;
    var bonds = [];
    for (var j = 0; j < m.bonds.length; j++) {
      var b = m.bonds[j];
      if (map[b[0]] && map[b[1]]) bonds.push(fCopyMolBond2D(b, map[b[0]], map[b[1]]));
    }
    return fWriteMolV2000(m.head, atoms, bonds, m);
  } catch (e) { return null; }
}

var MOLGEN_STDVALENCE = { C: 4, N: 3, O: 2, F: 1, Cl: 1, Br: 1, I: 1, S: 2, P: 3 }; // S/P: single-bond default; hypervalent forms unsupported (no auto-H beyond this)

// Minimum clearance for a newly placed H against placed atoms that are
// neither its parent nor vicinal to it (same rule as the overlap harness:
// geminal/vicinal closeness is natural). Below this, the next-largest
// angular gap is tried; the best candidate always wins, so clean molecules
// keep byte-identical coords and only colliding placements move.
const MOLGEN_H_MINSEP = 0.4;

// 2D layout bond lengths (MOL units, hardcoded — adjust manually here).
// All heavy–heavy bonds share MOLGEN_CC_LEN in every slot (condensed,
// expanded skeleton, zigzag); C–H bonds use MOLGEN_CH_LEN (~half of C–C).
const MOLGEN_CC_LEN = 1.0;
const MOLGEN_CH_LEN = 0.5;

// Expanded form: heavy skeleton + explicit H at MOLGEN_CH_LEN, placed by
// largest-free-sector bisection (connectivity is what matters). Pre-existing
// explicit H are kept; missing ones are topped up. Elements outside
// MOLGEN_STDVALENCE: kept, never added to (no silent H).
// Missing H use supported charge-aware valences; query, radical and stereo inputs fail closed.

function fGenExpandedMol(text) {
  try {
    var m = fParseMolV2000(text);
    if (!fMolCanTransform2D(m, false)) return null;
    var n = m.atoms.length;
    var adj = [], ord = {};
    for (var a = 0; a < n; a++) adj[a] = [];
    for (var b = 0; b < m.bonds.length; b++) {
      var bb = m.bonds[b];
      var x = bb[0] - 1, y = bb[1] - 1;
      if (x < 0 || y < 0 || x >= n || y >= n) continue;
      adj[x].push(y); adj[y].push(x);
      var k = (x < y) ? x + "-" + y : y + "-" + x;
      if (!ord[k] || ord[k] < bb[2]) ord[k] = bb[2];
    }
    var atoms = [];
    for (var c = 0; c < n; c++) atoms.push(fCopyMolAtom2D(m.atoms[c]));
    var bonds = [];
    for (var d = 0; d < m.bonds.length; d++) bonds.push(fCopyMolBond2D(m.bonds[d], m.bonds[d][0], m.bonds[d][1]));
    var HLEN = MOLGEN_CH_LEN;
    for (var h = 0; h < n; h++) {
      var el = String(m.atoms[h].el || "");
      if (!fIsHeavyEl2D(el)) continue;
      var v = MOLGEN_STDVALENCE[el], charge = m.atoms[h].charge || 0;
      if (charge) {
        var chargedValences = { C: { '-1': 3, 1: 3 }, N: { '-1': 2, 1: 4 }, O: { '-1': 1, 1: 3 },
          F: { '-1': 0 }, Cl: { '-1': 0 }, Br: { '-1': 0 }, I: { '-1': 0 } };
        if (!chargedValences[el] || chargedValences[el][charge] == null) return null;
        v = chargedValences[el][charge];
      }
      if (v == null) return null;
      var used = 0;
      for (var q = 0; q < adj[h].length; q++) {
        var nb = adj[h][q];
        var kk = (h < nb) ? h + "-" + nb : nb + "-" + h;
        used += ord[kk] || 1;
      }
      if (used > v) return null;
      var missing = v - used;
      for (var t = 0; t < missing; t++) {
        var angs = [];
        for (var r = 0; r < adj[h].length; r++) {
          var p = atoms[adj[h][r]];
          angs.push(Math.atan2(p.y - atoms[h].y, p.x - atoms[h].x));
        }
        angs.sort(function (p1, p2) { return p1 - p2; });
        // Candidate gaps, largest first. The old code took the largest gap
        // unconditionally; we keep that as the first try (clean molecules are
        // unaffected) and fall through to smaller gaps only on collision.
        var gaps = [];
        if (!angs.length) { gaps.push({ a: 0, g: 2 * Math.PI }); }
        else {
          for (var s = 0; s < angs.length; s++) {
            var a1 = angs[s], a2 = (s + 1 < angs.length) ? angs[s + 1] : angs[0] + 2 * Math.PI;
            gaps.push({ a: a1 + (a2 - a1) / 2, g: a2 - a1 });
          }
          gaps.sort(function (g1, g2) { return g2.g - g1.g; });
        }
        var SEPN = MOLGEN_H_MINSEP;
        // Clearance of a candidate point against placed atoms under the
        // vicinal rule (harness-identical): the parent itself, atoms bonded
        // to it, and H whose own parent is bonded to (or is) it are skipped.
        var minClear = function (qx, qy, par) {
          var md = 1e9;
          for (var cI = 0; cI < atoms.length; cI++) {
            if (cI === par) continue;
            var cEl = String(atoms[cI].el || "");
            var cIsH = (cEl === "H" || cEl === "h");
            if (adj[cI].indexOf(par) >= 0) continue;
            if (cIsH) {
              var cPar = -1;
              for (var cR = 0; cR < adj[cI].length; cR++) {
                var cCand = adj[cI][cR];
                if (!fIsHeavyEl2D(String(atoms[cCand].el || ""))) continue;
                cPar = cCand; break;
              }
              if (cPar === par || (cPar >= 0 && adj[par].indexOf(cPar) >= 0)) continue;
            }
            var dd = Math.hypot(qx - atoms[cI].x, qy - atoms[cI].y);
            if (dd < md) md = dd;
          }
          return md;
        };
        // Heavy parent of a placed H (its bond partner); -1 when unknown.
        var heavyParOf = function (idx) {
          for (var hR = 0; hR < adj[idx].length; hR++) {
            var hCand = adj[idx][hR];
            if (!fIsHeavyEl2D(String(atoms[hCand].el || ""))) continue;
            return hCand;
          }
          return -1;
        };
        var bestX = atoms[h].x + HLEN, bestY = atoms[h].y, bestD = -1;
        var splayed = false;
        for (var gI = 0; gI < gaps.length; gI++) {
          var cx = atoms[h].x + HLEN * Math.cos(gaps[gI].a);
          var cy = atoms[h].y + HLEN * Math.sin(gaps[gI].a);
          var md = minClear(cx, cy, h), mOff = -1;
          if (md < SEPN) {
            // Nearest offender, for the symmetric-splay attempt below.
            var mBest = 1e9;
            for (var oI = 0; oI < atoms.length; oI++) {
              if (oI === h || adj[oI].indexOf(h) >= 0) continue;
              var oEl = String(atoms[oI].el || "");
              if ((oEl === "H" || oEl === "h")) {
                var oPar = heavyParOf(oI);
                if (oPar === h || (oPar >= 0 && adj[h].indexOf(oPar) >= 0)) continue;
              }
              var oD = Math.hypot(cx - atoms[oI].x, cy - atoms[oI].y);
              if (oD < mBest) { mBest = oD; mOff = oI; }
            }
          }
          if (md > bestD) { bestD = md; bestX = cx; bestY = cy; }
          if (md >= SEPN) break;
          // Symmetric splay (first colliding gap only): when the offender is
          // a placed H, rotate it and the candidate apart by equal and
          // opposite steps around their own parents (bond lengths kept), so
          // both stay near their ideal sectors instead of one jumping sides.
          // First clearing pair wins; otherwise the gap loop continues.
          if (!splayed && gI === 0 && mOff >= 0) {
            var oEl2 = String(atoms[mOff].el || "");
            var oPar2 = heavyParOf(mOff);
            if ((oEl2 === "H" || oEl2 === "h") && oPar2 >= 0) {
              var aA0 = Math.atan2(atoms[mOff].y - atoms[oPar2].y, atoms[mOff].x - atoms[oPar2].x);
              var aB0 = gaps[0].a;
              var steps = [5, 10, 15, 20, 30, 45], sDone = false;
              for (var sI = 0; sI < steps.length && !sDone; sI++) {
                var rad = steps[sI] * Math.PI / 180;
                var pairs = [[1, -1], [-1, 1]];
                for (var pI = 0; pI < pairs.length && !sDone; pI++) {
                  var ax = atoms[oPar2].x + HLEN * Math.cos(aA0 + pairs[pI][0] * rad);
                  var ay = atoms[oPar2].y + HLEN * Math.sin(aA0 + pairs[pI][0] * rad);
                  var bx = atoms[h].x + HLEN * Math.cos(aB0 + pairs[pI][1] * rad);
                  var by = atoms[h].y + HLEN * Math.sin(aB0 + pairs[pI][1] * rad);
                  var cA = minClear(ax, ay, oPar2), cB = minClear(bx, by, h);
                  // A moved: exclude the candidate spot itself is unnecessary
                  // (B not placed yet); but A must also clear B's new spot.
                  var cAB = Math.hypot(ax - bx, ay - by);
                  var cMin = Math.min(cA, cB, cAB);
                  if (cMin > bestD) { bestD = cMin; bestX = bx; bestY = by; }
                  if (cMin >= SEPN) {
                    atoms[mOff].x = ax; atoms[mOff].y = ay;
                    bestX = bx; bestY = by; bestD = cMin;
                    sDone = true;
                  }
                }
              }
              splayed = true;
              if (sDone) break;
            }
          }
        }
        atoms.push({ x: bestX, y: bestY, el: "H", parentSourceIndex: h + 1 });
        var ni = atoms.length - 1;
        adj[h].push(ni); adj.push([h]);
        bonds.push([h + 1, ni + 1, 1]);
      }
    }
    return fWriteMolV2000(m.head, atoms, bonds, m);
  } catch (e) { return null; }
}

// School-form condensed layout: main chain collinear (MOLGEN_CC_LEN spacing,
// the stored-condensed convention), branches orthogonal alternating sides, sp
// centers stay on the line like the stored files. H atoms are dropped
// (condensed = heavy only). Chain entries are 1-based numbers into the source
// MOL's atom list (engine mainChainAtomsList of the same drawing).

function fLinearizeMol(text, chain) {
  try {
    var m = fParseMolV2000(text);
    if (!fMolCanTransform2D(m, true)) return null;
    if (!Array.isArray(chain) || !chain.length) return null;
    var n = m.atoms.length;
    var map = {}, order = [];
    for (var i = 0; i < n; i++) {
      if (!fIsHeavyEl2D(m.atoms[i].el)) continue;
      map[i + 1] = order.length;
      order.push(i);
    }
    if (!order.length) return null;
    var ch = [];
    for (var c = 0; c < chain.length; c++) {
      var a0 = (chain[c] | 0) - 1;
      if (a0 >= 0 && a0 < n && map[a0 + 1] != null) ch.push(a0);
    }
    if (!ch.length) return null;
    var adj = [];
    for (var h0 = 0; h0 < n; h0++) adj[h0] = [];
    for (var b = 0; b < m.bonds.length; b++) {
      var bb = m.bonds[b];
      var x = bb[0] - 1, y = bb[1] - 1;
      if (x < 0 || y < 0 || x >= n || y >= n) continue;
      if (map[x + 1] == null || map[y + 1] == null) continue;
      adj[x].push(y); adj[y].push(x);
    }
    var DX = MOLGEN_CC_LEN, DY = MOLGEN_CC_LEN;
    var pos = {}, inChain = {};
    for (var k = 0; k < ch.length; k++) { inChain[ch[k]] = true; pos[ch[k]] = { x: k * DX, y: 0 }; }
    var visited = {};
    for (var kc = 0; kc < ch.length; kc++) visited[ch[kc]] = true;
    // Queue: {node, x, y, dx, dy} — first continuation keeps direction,
    // extra forks try +90/-90 first, then diagonal relief (depiction-only).
    // Terminal chain atoms lean their branches outward (±x): without this,
    // end-group branches sit exactly above the anchor and geometry-based
    // tests (e.g. HOOC-vs-COOH orientation) tie instead of deciding.
    // Ether links (R-O-R) go fully horizontal from terminal atoms so C-O-C
    // stays linear instead of kinking the R groups orthogonal.
    // Overlap guard: quantized occupancy of placed atoms. Two methyls of
    // the same tert-butyl centre used to receive the identical +90° rotation
    // (perfect overlap); adjacent bulky branches could also land on each
    // other. Candidates closer than LIN_MINSEP to a placed non-parent atom
    // fall through to the next fallback angle (orthogonal first, diagonal
    // relief next), so clean molecules keep byte-identical coords and only
    // colliding placements move.
    var LIN_MINSEP = 0.3 * DX;
    // Claimed = queued but not yet placed (siblings pushed in the same
    // batch are invisible to pos until popped — without this, two methyls of
    // one tert-butyl centre both pass the check and land identically).
    var _claimed = {};
    var _linHit = function (x, y, selfNode, parentNode) {
      try {
        for (var _k in pos) {
          if (!Object.prototype.hasOwnProperty.call(pos, _k)) continue;
          var _ni = parseInt(_k, 10);
          if (_ni === selfNode || _ni === parentNode) continue;
          var _p = pos[_k];
          var _ddx = _p.x - x, _ddy = _p.y - y;
          if ((_ddx * _ddx + _ddy * _ddy) < LIN_MINSEP * LIN_MINSEP) return true;
        }
        for (var _q in _claimed) {
          if (!Object.prototype.hasOwnProperty.call(_claimed, _q)) continue;
          var _qi = parseInt(_q, 10);
          if (_qi === selfNode || _qi === parentNode) continue;
          var _c = _claimed[_q];
          var _edx = _c.x - x, _edy = _c.y - y;
          if ((_edx * _edx + _edy * _edy) < LIN_MINSEP * LIN_MINSEP) return true;
        }
      } catch (eH) {}
      return false;
    };
    // Rotate a unit direction by degrees (length-preserving; diagonal
    // fallbacks use 0.7071 so every bond stays MOLGEN_CC_LEN).
    var _linRot = function (dx, dy, deg) {
      try {
        var r = deg * Math.PI / 180, c = Math.cos(r), s = Math.sin(r);
        return [dx * c - dy * s, dx * s + dy * c];
      } catch (eR) { return [dx, dy]; }
    };
    var queue = [];
    // Stagger: neighbouring chain atoms open opposite sides when both carry
    // non-ether branches, so adjacent tert-butyl centres never start on top
    // of each other. Isolated branches keep the historical -1 start.
    var _nextParity = 0;
    for (var ci = 0; ci < ch.length; ci++) {
      var c0 = ch[ci], sideCount = 0, etherDone = false, placedHere = 0;
      var lean = 0;
      if (ci === 0) lean = -0.5;
      else if (ci === ch.length - 1) lean = 0.5;
      var _startPar = _nextParity;
      for (var nb = 0; nb < adj[c0].length; nb++) {
        var br = adj[c0][nb];
        if (visited[br]) continue;
        // A terminal degree-two sp center continues the parent axis, even
        // when its triple-bonded neighbor (e.g. nitrile N) is off the carbon
        // parent. Orthogonal branch placement would bend C-C≡N by 90°.
        var terminalSp = ch.length > 1 && (ci === 0 || ci === ch.length - 1) &&
          adj[c0].length === 2 && m.bonds.some(function (bond) {
            return bond[2] === 3 && (bond[0] === c0 + 1 || bond[1] === c0 + 1);
          });
        if (terminalSp) {
          var outward = ci === 0 ? -1 : 1;
          queue.push({ node: br, x: (ci + outward) * DX, y: 0, dx: outward, dy: 0 });
          _claimed[br] = { x: (ci + outward) * DX, y: 0 };
          continue;
        }
        var isEtherLink = false;
        try {
          if ((ci === 0 || ci === ch.length - 1) && !etherDone &&
              String(m.atoms[br].el || '').toUpperCase() === 'O' && adj[br].length === 2) {
            var carbonNeighbors = 0;
            for (var oi = 0; oi < adj[br].length; oi++) {
              if (String(m.atoms[adj[br][oi]].el || '').toUpperCase() === 'C') carbonNeighbors++;
            }
            if (carbonNeighbors === 2) isEtherLink = true;
          }
        } catch (eEl) { isEtherLink = false; }
        if (isEtherLink) {
          var _dir = (ci === 0) ? -1 : 1;
          queue.push({ node: br, x: ci * DX + _dir * DX, y: 0, dx: _dir, dy: 0, p: c0 });
          try { _claimed[br] = { x: ci * DX + _dir * DX, y: 0 }; } catch (eCl2) {}
          etherDone = true;
          continue;
        }
        var side = (((sideCount + _startPar) % 2) === 0) ? -1 : 1;
        sideCount++;
        // Orthogonal first; on collision try the opposite side, then the two
        // diagonals (length-preserving). First non-colliding wins.
        var _cands = [
          [ci * DX + lean * DX, side * DY, 0, side],
          [ci * DX + lean * DX, -side * DY, 0, -side],
          [ci * DX + lean * DX + 0.7071 * DX, side * 0.7071 * DY, 0.7071, side * 0.7071],
          [ci * DX + lean * DX - 0.7071 * DX, side * 0.7071 * DY, -0.7071, side * 0.7071]
        ];
        var _pick = _cands[0];
        for (var _qi = 0; _qi < _cands.length; _qi++) {
          if (!_linHit(_cands[_qi][0], _cands[_qi][1], br, c0)) { _pick = _cands[_qi]; break; }
          _pick = _cands[_qi];
        }
        queue.push({ node: br, x: _pick[0], y: _pick[1], dx: _pick[2], dy: _pick[3], p: c0 });
        try { _claimed[br] = { x: _pick[0], y: _pick[1] }; } catch (eCl) {}
        placedHere++;
      }
      _nextParity = (placedHere > 0) ? (_startPar ^ 1) : 0;
    }
    while (queue.length) {
      var it = queue.shift();
      if (visited[it.node]) continue;
      try { delete _claimed[it.node]; } catch (eDc) {}
      // Pop-time recheck: a collider may have been placed after this item
      // was queued (e.g. the neighbour branch centre). Relocate through the
      // same fallback list before committing.
      if (typeof it.p !== "undefined" && _linHit(it.x, it.y, it.node, it.p)) {
        var _re = false;
        for (var _ri = 0; _ri < 8; _ri++) {
          var _rdeg = [0, 90, -90, 45, -45, 135, -135, 180][_ri];
          var _rrv = _linRot(it.dx, it.dy, _rdeg);
          var _rcx = pos[it.p].x + _rrv[0] * DX, _rcy = pos[it.p].y + _rrv[1] * DY;
          if (!_linHit(_rcx, _rcy, it.node, it.p)) {
            it.x = _rcx; it.y = _rcy; it.dx = _rrv[0]; it.dy = _rrv[1];
            _re = true;
            break;
          }
        }
        if (!_re) { /* keep queued coords: overlap beats dropping the atom */ }
      }
      visited[it.node] = true;
      pos[it.node] = { x: it.x, y: it.y };
      // Fan-out: first child continues straight; each extra fork prefers
      // +90°, -90°, then ±45° diagonals, +135/-135, 180°. Every extra scans
      // the same fallback list against occupancy, so the second tert-butyl
      // methyl no longer duplicates the first — it takes -90° (or diagonal
      // relief when both orthogonals are taken). Single/double-child nodes
      // keep their historical coords (straight / +90°) when uncollided.
      var _kids = [];
      for (var w = 0; w < adj[it.node].length; w++) {
        var cand = adj[it.node][w];
        if (visited[cand]) continue;
        _kids.push(cand);
      }
      for (var ki = 0; ki < _kids.length; ki++) {
        var _done = false;
        // First child: straight unless occupied; extras: alternate +90/-90
        // first (historical), diagonals on collision.
        var _order = (ki === 0) ? [0, 90, -90, 45, -45, 135, -135, 180] : [90, -90, 45, -45, 135, -135, 0, 180];
        // Avoid re-offering the exact angle an earlier sibling just took:
        // occupancy catches it anyway (dist 0), this just orders better.
        for (var fi = 0; fi < _order.length; fi++) {
          var _deg = _order[fi];
          var _rv = _linRot(it.dx, it.dy, _deg);
          var _cx = it.x + _rv[0] * DX, _cy = it.y + _rv[1] * DY;
          if (!_linHit(_cx, _cy, _kids[ki], it.node)) {
            queue.push({ node: _kids[ki], x: _cx, y: _cy, dx: _rv[0], dy: _rv[1], p: it.node });
            try { _claimed[_kids[ki]] = { x: _cx, y: _cy }; } catch (eCl3) {}
            _done = true;
            break;
          }
        }
        if (!_done) {
          var _rvf = _linRot(it.dx, it.dy, (ki === 0) ? 0 : 90);
          queue.push({ node: _kids[ki], x: it.x + _rvf[0] * DX, y: it.y + _rvf[1] * DY, dx: _rvf[0], dy: _rvf[1], p: it.node });
          try { _claimed[_kids[ki]] = { x: it.x + _rvf[0] * DX, y: it.y + _rvf[1] * DY }; } catch (eCl4) {}
        }
      }
    }
    var atoms = [], newIdx = {};
    for (var o = 0; o < order.length; o++) {
      var oi = order[o];
      var pp = pos[oi] || { x: m.atoms[oi].x, y: m.atoms[oi].y };
      newIdx[oi + 1] = atoms.length + 1;
      atoms.push(fCopyMolAtom2D(m.atoms[oi], pp.x, pp.y));
    }
    var bonds = [];
    for (var j = 0; j < m.bonds.length; j++) {
      var bj = m.bonds[j];
      if (newIdx[bj[0]] && newIdx[bj[1]]) bonds.push(fCopyMolBond2D(bj, newIdx[bj[0]], newIdx[bj[1]]));
    }
    return fWriteMolV2000(m.head, atoms, bonds, m);
  } catch (e) { return null; }
}

// Scientific zigzag layout (university skeletal form): chain walk with
// alternating ±30° segments at uniform bond lengths, triple bonds kept
// collinear like the stored files, branches bisecting the external angle.
// Heavy atoms only; chain entries are 1-based numbers into the source MOL.
// Deterministic fallback when JSME cannot lay out SMILES in this build.

function fZigzagMol(text, chain) {
  try {
    var m = fParseMolV2000(text);
    if (!fMolCanTransform2D(m, true)) return null;
    if (!Array.isArray(chain) || !chain.length) return null;
    var n = m.atoms.length;
    var map = {}, order = [];
    for (var i = 0; i < n; i++) {
      if (!fIsHeavyEl2D(m.atoms[i].el)) continue;
      map[i + 1] = order.length;
      order.push(i);
    }
    if (!order.length) return null;
    var ch = [];
    for (var c = 0; c < chain.length; c++) {
      var a0 = (chain[c] | 0) - 1;
      if (a0 >= 0 && a0 < n && map[a0 + 1] != null) ch.push(a0);
    }
    if (!ch.length) return null;
    var adj = [], ord = {};
    for (var h0 = 0; h0 < n; h0++) adj[h0] = [];
    for (var b = 0; b < m.bonds.length; b++) {
      var bb = m.bonds[b];
      var x = bb[0] - 1, y = bb[1] - 1;
      if (x < 0 || y < 0 || x >= n || y >= n) continue;
      if (map[x + 1] == null || map[y + 1] == null) continue;
      adj[x].push(y); adj[y].push(x);
      var k = (x < y) ? x + "-" + y : y + "-" + x;
      if (!ord[k] || ord[k] < bb[2]) ord[k] = bb[2];
    }
    var bo = function (a, c) {
      var kk = (a < c) ? a + "-" + c : c + "-" + a;
      return ord[kk] || 1;
    };
    // This tree layout cannot safely reconstruct ring closure or disconnected
    // fragments. Reject those inputs instead of stretching an unvisited edge.
    var reached = {}, todo = [ch[0]], heavyBonds = 0;
    while (todo.length) {
      var node = todo.pop(); if (reached[node]) continue;
      reached[node] = true;
      adj[node].forEach(function (v) { if (!reached[v]) todo.push(v); });
    }
    order.forEach(function (v) { heavyBonds += adj[v].length; });
    if (Object.keys(reached).length !== order.length || heavyBonds !== 2 * (order.length - 1) ||
        ch.length !== chain.length || new Set(ch).size !== ch.length ||
        ch.some(function (v, i) { return i && adj[ch[i - 1]].indexOf(v) < 0; })) return null;
    var L = MOLGEN_CC_LEN, CX = L * 0.8660254, CY = L * 0.5;
    var norm2 = function (vx, vy) {
      var l = Math.sqrt(vx * vx + vy * vy);
      if (!(l > 1e-9)) return null;
      return { x: vx / l, y: vy / l };
    };
    var pos = {}, visited = {}, segDir = {};
    pos[ch[0]] = { x: 0, y: 0 }; visited[ch[0]] = true;
    var sgn = -1, pdx = CX, pdy = CY, prevTriple = false;
    for (var k = 1; k < ch.length; k++) {
      var oPrev = bo(ch[k - 1], ch[k]);
      if (oPrev === 3 || prevTriple) { /* keep direction (sp collinear) */ }
      else { sgn = -sgn; pdx = CX; pdy = sgn * CY; }
      prevTriple = (oPrev === 3);
      pos[ch[k]] = { x: pos[ch[k - 1]].x + pdx, y: pos[ch[k - 1]].y + pdy };
      visited[ch[k]] = true;
      segDir[k] = { x: pdx, y: pdy };
    }
    // Branch directions from chain atoms (external-angle bisector).
    var queue = [];
    for (var ci = 0; ci < ch.length; ci++) {
      var c0 = ch[ci], usedC = 0;
      var dIn = (ci > 0) ? segDir[ci] : null;
      var dOut = (ci < ch.length - 1) ? segDir[ci + 1] : null;
      for (var nb = 0; nb < adj[c0].length; nb++) {
        var br = adj[c0][nb];
        if (visited[br]) continue;
        var bd;
        if (!dIn && !dOut) { bd = { x: 1, y: 0 }; }
        else if (!dIn) { bd = norm2(-dOut.x, -dOut.y) || { x: -1, y: 0 }; }
        else if (!dOut) { bd = { x: dIn.x, y: dIn.y }; }
        else {
          var fx = dIn.x - dOut.x, fy = dIn.y - dOut.y;
          bd = norm2(fx, fy);
          if (!bd) { bd = norm2(-dOut.y, dOut.x) || { x: 0, y: 1 }; }
        }
        if (usedC > 0) {
          var r2 = (usedC % 2 === 1) ? 1 : -1;
          bd = norm2(-bd.y * r2, bd.x * r2) || bd;
        }
        // Endpoint dIn carries a bond vector of length L, not a unit vector.
        // Normalize every branch direction before multiplying by L below.
        bd = norm2(bd.x, bd.y);
        if (!bd) return null;
        usedC++;
        queue.push({ node: br, fx: c0, dx: bd.x, dy: bd.y, rot: 0 });
      }
    }
    while (queue.length) {
      var it = queue.shift();
      if (visited[it.node]) continue;
      visited[it.node] = true;
      var Pp = pos[it.fx] || m.atoms[it.fx];
      pos[it.node] = { x: Pp.x + it.dx * L, y: Pp.y + it.dy * L };
      var kids = 0;
      for (var w = 0; w < adj[it.node].length; w++) {
        var cand = adj[it.node][w];
        if (visited[cand]) continue;
        var nd;
        if (kids === 0) { nd = { x: it.dx, y: it.dy }; }
        else {
          var rr = (kids % 2 === 1) ? 1 : -1;
          nd = norm2(-it.dy * rr, it.dx * rr) || { x: -it.dx, y: -it.dy };
        }
        kids++;
        queue.push({ node: cand, fx: it.node, dx: nd.x, dy: nd.y });
      }
    }
    // The first continuation of an off-parent subtree used to stay straight.
    // Correct only the affected degree-two pivot by rotating an entire side:
    // all generated bond lengths and every other local angle remain invariant.
    function turn(ids, pivot, angle) {
      var co = Math.cos(angle), si = Math.sin(angle);
      ids.forEach(function (v) {
        var x = pos[v].x - pivot.x, y = pos[v].y - pivot.y;
        pos[v] = { x: pivot.x + x * co - y * si, y: pivot.y + x * si + y * co };
      });
    }
    function cross(p, a, b, c) {
      return (p[b].x - p[a].x) * (p[c].y - p[a].y) - (p[b].y - p[a].y) * (p[c].x - p[a].x);
    }
    function crossing(p, a, b, c, d) {
      return cross(p, a, b, c) * cross(p, a, b, d) < -1e-10 &&
        cross(p, c, d, a) * cross(p, c, d, b) < -1e-10;
    }
    function atomBondDistance(p, i, a, b) {
      var dx = p[b].x - p[a].x, dy = p[b].y - p[a].y, length = dx * dx + dy * dy;
      var t = length ? Math.max(0, Math.min(1, ((p[i].x - p[a].x) * dx + (p[i].y - p[a].y) * dy) / length)) : 0;
      return Math.hypot(p[i].x - p[a].x - t * dx, p[i].y - p[a].y - t * dy);
    }
    var edges = m.bonds.filter(function (b) { return map[b[0]] != null && map[b[1]] != null; })
      .map(function (b) { return [b[0] - 1, b[1] - 1]; });
    function safe(previous) {
      for (var i = 0; i < order.length; i++) for (var j = 0; j < i; j++) {
        var a = order[i], b = order[j];
        if (adj[a].indexOf(b) >= 0) continue;
        var old = Math.hypot(previous[a].x - previous[b].x, previous[a].y - previous[b].y);
        var now = Math.hypot(pos[a].x - pos[b].x, pos[a].y - pos[b].y);
        if (now < L * 0.45 && now < old - 1e-6) return false;
      }
      for (var e = 0; e < edges.length; e++) {
        var a = edges[e][0], b = edges[e][1];
        for (var j = 0; j < order.length; j++) {
          var v = order[j]; if (v === a || v === b) continue;
          var old = atomBondDistance(previous, v, a, b), now = atomBondDistance(pos, v, a, b);
          if (now < L * 0.12 && now < old - 1e-6) return false;
        }
        for (var d = 0; d < e; d++) {
          var c = edges[d][0], q = edges[d][1];
          if (a === c || a === q || b === c || b === q) continue;
          if (crossing(pos, a, b, c, q) && !crossing(previous, a, b, c, q)) return false;
        }
      }
      return true;
    }
    for (var at = 0; at < order.length; at++) {
      var center = order[at], el = m.atoms[center].el;
      if (adj[center].length !== 2 || (el !== 'C' && el !== 'O')) continue;
      var ns = adj[center], orders = ns.map(function (v) { return bo(center, v); });
      if (el === 'O' && (m.atoms[center].charge || orders.some(function (v) { return v !== 1; }))) return null;
      if (el === 'C' && orders[0] + orders[1] > 4) return null;
      var sp = el === 'C' && (orders.indexOf(3) >= 0 || (orders[0] === 2 && orders[1] === 2));
      var target = sp ? Math.PI : 2 * Math.PI / 3;
      var sides = ns.map(function (start) {
        var seen = {}, ids = [], todo = [start]; seen[center] = true;
        while (todo.length) {
          var v = todo.pop(); if (seen[v]) continue;
          seen[v] = true; ids.push(v);
          adj[v].forEach(function (q) { if (!seen[q]) todo.push(q); });
        }
        return { start: start, ids: ids };
      });
      // Keep C1 and as much of the resolved parent as possible fixed.
      sides.sort(function (a, b) {
        return Number(a.ids.indexOf(ch[0]) >= 0) - Number(b.ids.indexOf(ch[0]) >= 0) ||
          a.ids.filter(function (v) { return ch.indexOf(v) >= 0; }).length -
          b.ids.filter(function (v) { return ch.indexOf(v) >= 0; }).length || a.ids.length - b.ids.length;
      });
      var moving = sides[0], fixed = ns[0] === moving.start ? ns[1] : ns[0], pivot = pos[center];
      if (moving.ids.indexOf(fixed) >= 0) return null;
      var from = Math.atan2(pos[moving.start].y - pivot.y, pos[moving.start].x - pivot.x);
      var base = Math.atan2(pos[fixed].y - pivot.y, pos[fixed].x - pivot.x);
      var choices = [target, -target].map(function (t) { return Math.atan2(Math.sin(base + t - from), Math.cos(base + t - from)); });
      choices.sort(function (a, b) { return Math.abs(a) - Math.abs(b); });
      if (Math.abs(choices[0]) < 1e-7) continue;
      var previous = {};
      order.forEach(function (v) { previous[v] = { x: pos[v].x, y: pos[v].y }; });
      var repaired = false;
      for (var trial = 0; trial < choices.length; trial++) {
        order.forEach(function (v) { pos[v] = { x: previous[v].x, y: previous[v].y }; });
        turn(moving.ids, pivot, choices[trial]);
        if (safe(previous)) { repaired = true; break; }
      }
      // An unsafe generated layout is not a successful deterministic rung.
      if (!repaired) return null;
    }
    var atoms = [], newIdx = {};
    for (var o = 0; o < order.length; o++) {
      var oi = order[o];
      var pp = pos[oi] || { x: m.atoms[oi].x, y: m.atoms[oi].y };
      newIdx[oi + 1] = atoms.length + 1;
      atoms.push(fCopyMolAtom2D(m.atoms[oi], pp.x, pp.y));
    }
    var bonds = [];
    for (var j = 0; j < m.bonds.length; j++) {
      var bj = m.bonds[j];
      if (newIdx[bj[0]] && newIdx[bj[1]]) bonds.push(fCopyMolBond2D(bj, newIdx[bj[0]], newIdx[bj[1]]));
    }
    return fWriteMolV2000(m.head, atoms, bonds, m);
  } catch (e) { return null; }
}

// ── fGuessName ────────────────────────────────────────────────────────────


function fMolDraftNorm(s) {
  return String(s == null ? "" : s).toLowerCase().replace(/\s+/g, " ").trim();
}
// Shared PubChem 3-way match (systematic/retained/title, stereo-stripped):
// feeds the EN auto-check and the PubChem-row glyph alike, so they agree.

function fMolDraftCancel() {
  if (!window.MulerDraft) return;
  if (window.MulerDraftAcquisition === window.MulerDraft) {
    window.MulerDraft.cancelRequested = true;
    return; // The owning Accept restores both applets before teardown.
  }
  fMolDraftTeardownDisplay();
  // Full reselect — the same path recovery flows use — rebuilds naming + 3D.
  try { if (typeof fSelectMol === "function") fSelectMol(); } catch (eF) {}
}

// Human-readable custom keys: custom_<english-name> (systematic preferred).
// Greek letters expand (α-pinene stays distinct from β-pinene); ultimate
// fallback is the stable SMILES hash. Duplicate structures are blocked by the
// Accept guard, so same-name collisions only arise from stereoisomers etc.
var MOLDRAFT_GR2EN = { "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon", "ζ": "zeta", "η": "eta", "θ": "theta", "ι": "iota", "κ": "kappa", "λ": "lambda", "μ": "mu", "ν": "nu", "ξ": "xi", "ο": "omicron", "π": "pi", "ρ": "rho", "σ": "sigma", "ς": "sigma", "τ": "tau", "υ": "upsilon", "φ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega" };


async function fMolDraftAccept() {
  var d = window.MulerDraft;
  if (!d || d.submitting || d.accepting || d._minimizing || window.MulerDraftAcquisition || fMolDraftPresenting()) return;
  if (!d.submitted || !d.engineName) {
    fMolDraftToast(fMolDraftT("acceptNeedsSubmit", "Press Submit for a preview first."));
    return;
  }
  var _myEpochA = d._epoch, _mySidA = d._submitId;
  // Freshness: drawing changed since the preview? Re-read and compare —
  // authoritative even if the live edit callbacks turn out to be no-ops.
  // Self-healing: identical structure clears a spurious stale flag.
  try {
    var _cur = fMolDraftReadDrawing();
    var _curSmi = fMolDraftNorm((_cur && _cur.smiles) || "");
    if (!_curSmi || _curSmi !== fMolDraftNorm(d.smiles || "")) {
      d.stale = true;
      try {
        var _st = document.getElementById("molDraftStatus");
        if (_st) _st.textContent = fMolDraftT("acceptStale", "Drawing changed — press Submit again.");
      } catch (eStF) {}
      try { fMolDraftSyncBar(); } catch (eSyF) {}
      fMolDraftToast(fMolDraftT("acceptStale", "Drawing changed — press Submit again."));
      return;
    }
    d.stale = false;
  } catch (eFr) {}
  // Every source is graph-checked; provisional geometry requires confirmation.
  if (typeof d.pubchem === "undefined" || !d.sdfDone) {
    fMolDraftToast(fMolDraftT("acceptWaitFetch", "Still looking up PubChem — wait a moment."));
    return;
  }
  if (!d.sdf3D) {
    fMolDraftToast(fMolDraftT("acceptNeeds3D", "Acceptance requires a 3D model."));
    return;
  }
  if (!fMolDraftValidSDF3D(d.sdf3D, d.expectHeavy || 0, d.molText)) {
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
  // Edit rule: Update in place only when the drawing is the SAME molecule
  // (beautify). A different molecule always forks a new custom entry —
  // the template is never overwritten. Stored (141) sources never update
  // (option a): same-molecule redraw hits the dup guard below as its own
  // key and blocks with "Already exists".
  var isSame = false;
  try { if (typeof fMolDraftIsSameMolecule === "function") isSame = !!fMolDraftIsSameMolecule(); } catch (eIs) { isSame = false; }
  try { if (typeof fMolDraftRefreshAcceptKey === "function") fMolDraftRefreshAcceptKey(); } catch (eK3) {}
  var isUpdate = !!(isSame && d.sourceIsCustom && d.sourceMol && typeof nameExamples !== "undefined" && nameExamples[d.sourceMol]);
  // Duplicate guard: exact-SMILES (normalized) + PubChem CID against stored
  // entries. Canonical-SMILES comparison waits on the RDKit decision.
  // Own record excluded only on the true update path; a fork checks
  // against every entry including its template.
  var normSmi = fMolDraftNorm(d.smiles);
  var selfKey = isUpdate ? d.sourceMol : null;
  var dupKey = null;
  try {
    var keys = (typeof nameExamples !== "undefined") ? Object.keys(nameExamples) : [];
    for (var i = 0; i < keys.length; i++) {
      var e = nameExamples[keys[i]];
      if (!e) continue;
      if (selfKey && keys[i] === selfKey) continue;
      try {
        if (e.smiles && fMolDraftNorm(e.smiles) === normSmi) { dupKey = keys[i]; break; }
        if (d.pubchem && d.pubchem.cid && e.pubchemCID && String(e.pubchemCID) === String(d.pubchem.cid)) { dupKey = keys[i]; break; }
      } catch (eC) {}
    }
  } catch (eK) {}
  if (dupKey) {
    fMolDraftToast(fMolDraftT("acceptDup", "Already exists — pick it from the menu.") + " (" + dupKey + ")");
    return;
  }
  // Edit-different confirm: Edit edits one view, New creates. A different
  // drawing in Edit forks — ask first (stored source untouched either way).
  // Missing confirmation UI fails closed; the source record stays untouched.
  if (d.mode === "edit" && !isSame && !d._forkConfirmed) {
    var _fm = "", _fy = "";
    try { _fm = fMolDraftT("draftForkConfirm", "This drawing is a different molecule — fork as new?"); } catch (eFm) { _fm = "Fork as new?"; }
    try { _fy = fMolDraftT("draftForkYes", "Fork as new"); } catch (eFy) { _fy = "Fork as new"; }
    if (typeof fScenarioConfirm !== "function") return;
    if (typeof fScenarioConfirm === "function") {
      try { fScenarioConfirm(_fm, function () { try { if (window.MulerDraft !== d || d._epoch !== _myEpochA || d._submitId !== _mySidA) return; d._forkConfirmed = true; } catch (eFc) {} try { fMolDraftAccept(); } catch (eFa) {} }, _fy); } catch (eSc) {}
      return;
    }
  }
  d.accepting = true;
  d.cancelRequested = false;
  window.MulerDraftAcquisition = d;
  var selectionAtAccept = (typeof selectedMol !== "undefined") ? selectedMol : null;
  var modeAtAccept = (typeof mode2D !== "undefined") ? mode2D : null;
  function ownsDraft() {
    return window.MulerDraft === d && window.MulerDraftAcquisition === d &&
      d._epoch === _myEpochA && d._submitId === _mySidA &&
      ((typeof selectedMol !== "undefined") ? selectedMol : null) === selectionAtAccept &&
      ((typeof mode2D !== "undefined") ? mode2D : null) === modeAtAccept;
  }
  function liveDraft() { return ownsDraft() && !d.cancelRequested; }
  try { fMolDraftSyncBar(); } catch (eSyA) {}
  try {
  var hit = d.pubchem || null;
  var key = fMolDraftMakeKey(normSmi, hit);
  if (isUpdate) key = d.sourceMol;
  var slotsCopy = null;
  try { slotsCopy = JSON.parse(JSON.stringify((typeof nameComponentsList !== "undefined") ? nameComponentsList : [])); } catch (eSl) { slotsCopy = []; }
  var cls = null;
  try { if (typeof fGetMoleculeClassification === "function") cls = fGetMoleculeClassification(); } catch (eCl) { cls = null; }
  var formula = "";
  try { if (typeof fMolDraftExpandedFormula === "function") formula = fMolDraftExpandedFormula() || ""; } catch (eFo) { formula = ""; }
  // Same-identity edits replace only their edited slot; forks generate all forms.
  var drawnVariant = (d.mode === "edit") ? d.variant : "condensed";
  var _chainLive = null;
  try { _chainLive = (typeof mainChainAtomsList !== "undefined") ? mainChainAtomsList : null; } catch (eCh) { _chainLive = null; }
  var _skel = null, _skelSrc = "";
  var depictSmiles = (hit && hit.canonicalSmiles) || d.smiles || "";
  var expectedHeavy = 0;
  try {
    var drawnParsed = fParseMolV2000(d.molText);
    if (drawnParsed) expectedHeavy = drawnParsed.atoms.filter(function (a) { return fIsHeavyEl2D(a.el); }).length;
  } catch (eHeavy) {}
  // Coordinate sums are a diagnostic receipt, never an identity/quality gate.
  var _sigOf = function (text) {
    try {
      if (!text) return "none";
      var p = fParseMolV2000(text);
      if (!p || !p.atoms.length) return "unparseable";
      var hc = 0, xs = 0, ys = 0;
      p.atoms.forEach(function (a) {
        if (fIsHeavyEl2D(a.el)) { hc++; xs += Math.round(a.x * 100); ys += Math.round(a.y * 100); }
      });
      return "heavy=" + hc + " x=" + xs + " y=" + ys;
    } catch (eSg) { return "?"; }
  };
  // Reuse the existing exact heavy-graph mapper in a synchronous transaction.
  // It only reads these four lists (no map-cache mutation). Composite labels
  // retain charge and isotope distinctions; H stays H for explicit-H removal.
  function fMolDraftLayoutMap(a, b) {
    if (typeof fBuildHeavyMap2D3D !== "function") return null;
    var saved = [allAtomsTypeList, bondList, allAtomsTypeList3D, bondList3D];
    function labels(m) {
      return m.atoms.map(function (v) {
        return fIsHeavyEl2D(v.el) ? JSON.stringify([v.el, v.charge || 0,
          v.massDifference || 0, v.isotope || 0]) : "H";
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
  // Compare all mapped internal distances, normalized by extent: headers,
  // translation, rotation and uniform scale cannot turn a depict echo into
  // a new layout. Built-in fixed points deliberately bypass this echo test.
  function fMolDraftLayoutEcho(a, b, map) {
    var pairs = [], extentA = 0, extentB = 0;
    for (var i = 0; i < a.atoms.length; i++) {
      if (map.arr[i] == null) continue;
      for (var j = i + 1; j < a.atoms.length; j++) {
        if (map.arr[j] == null) continue;
        var x = a.atoms[i], y = a.atoms[j], u = b.atoms[map.arr[i]], v = b.atoms[map.arr[j]];
        var da = Math.hypot(x.x - y.x, x.y - y.y), db = Math.hypot(u.x - v.x, u.y - v.y);
        extentA = Math.max(extentA, da); extentB = Math.max(extentB, db);
        pairs.push([da, db]);
      }
    }
    if (!pairs.length) return true;
    if (!(extentA > 1e-6) || !(extentB > 1e-6)) return extentA <= 1e-6 && extentB <= 1e-6;
    return pairs.every(function (p) { return Math.abs(p[0] / extentA - p[1] / extentB) < 0.0002; });
  }
  function fMolDraftUseSkeletal(text, source) {
    try {
      if (!text) return false;
      text = String(text).replace(/\[C\]/g, "C  ");
      var a = fParseMolV2000(d.molText), b = fParseMolV2000(text);
      // Supported transformation rules reject ambiguous query/stereo records;
      // parser enforces finite coordinates and valid bond endpoints.
      if (!fMolCanTransform2D(a, true) || !fMolCanTransform2D(b, true)) throw new Error("unsupported/invalid MOL");
      var map = fMolDraftLayoutMap(a, b);
      if (!map) throw new Error("heavy graph/charge/isotope mismatch");
      var heavy = b.atoms.filter(function (v) { return fIsHeavyEl2D(v.el); });
      if (heavy.length > 1 && b.bonds.some(function (bond) {
        var x = b.atoms[bond[0] - 1], y = b.atoms[bond[1] - 1];
        return fIsHeavyEl2D(x.el) && fIsHeavyEl2D(y.el) && Math.hypot(x.x - y.x, x.y - y.y) < 1e-6;
      })) throw new Error("collapsed bond");
      if (source !== "builtin" && fMolDraftLayoutEcho(a, b, map)) throw new Error("unchanged internal geometry");
      _skel = text; _skelSrc = source;
      try { console.log("[draft] skeletal: " + source + " ok " + _sigOf(text)); } catch (eL) {}
      return true;
    } catch (eV) {
      try { console.warn("[draft] skeletal: " + source + " rejected (" + eV.message + ")"); } catch (eL) {}
      return false;
    }
  }
  // Canonical JSME display, then edit, then deterministic built-in. Every
  // rung must pass the same exact graph/metadata/geometry gates before winning.
  if (typeof jsmeNomeclatureApplet !== "undefined" && jsmeNomeclatureApplet) {
    var displayDepiction = await fMolDraftDepictSmiles(jsmeNomeclatureApplet, depictSmiles, expectedHeavy);
    if (!liveDraft()) return;
    fMolDraftUseSkeletal(displayDepiction, "display");
  }
  if (!_skel && typeof jsmeEditDraftApplet !== "undefined" && jsmeEditDraftApplet) {
    var editDepiction = await fMolDraftDepictSmiles(jsmeEditDraftApplet, depictSmiles, expectedHeavy);
    if (!liveDraft()) return;
    fMolDraftUseSkeletal(editDepiction, "edit");
  }
  if (!_skel && typeof fZigzagMol === "function") {
    try { fMolDraftUseSkeletal(fZigzagMol(d.molText, _chainLive), "builtin"); }
    catch (eZ) { try { console.warn("[draft] skeletal: builtin failed", eZ); } catch (eL0) {} }
  }
  if (!liveDraft()) return;
  var molC = null, molE = null, molS = null;
  // Fork ⇒ full generation (New always + Edit-different): the result is a new
  // molecule, so all three slots derive canonically and drawnVariant is
  // ignored. Update ⇒ slot verbatim (single-slot contract). isUpdate is
  // decided above from molecule identity, before derivation.
  var isFork = true;
  try { isFork = !isUpdate; } catch (eIF) { isFork = true; }
  try {
    if (drawnVariant === "expanded" && !isFork) {
      molE = d.molText;
      molC = (typeof fStripHydrogensMol === "function") ? (fStripHydrogensMol(d.molText) || d.molText) : d.molText;
      molS = _skel || molC;
      if (!_skel) { try { console.warn("[draft] skeletal fallback: drawn geometry"); } catch (eW1) {} }
    } else if (drawnVariant === "expanded" && isFork) {
      // Edit-expanded fork: same full generation as New (linearize → top-up),
      // never the hand geometry verbatim.
      var _linE = (typeof fLinearizeMol === "function") ? fLinearizeMol(d.molText, _chainLive) : null;
      if (!_linE) { try { console.warn("[draft] linearizer failed, condensed = drawn geometry"); } catch (eW1b) {} }
      molC = _linE || d.molText;
      if (typeof fStripHydrogensMol === "function") {
        try { molC = (fStripHydrogensMol(molC) || molC); } catch (eStE) {}
      }
      molE = (typeof fGenExpandedMol === "function") ? (fGenExpandedMol(molC) || null) : null;
      if (!molE) { try { console.warn("[draft] expanded generation failed — mode disabled"); } catch (eW1c) {} }
      molS = _skel || molC;
      if (!_skel) { try { console.warn("[draft] skeletal fallback: drawn geometry"); } catch (eW1d) {} }
    } else if (drawnVariant === "skeletal" || drawnVariant === "condensedZigZag") {
      // Skeletal is always the ladder zigzag (see above) — the drawn MOL here
      // is layout-agnostic input, often already linearized by Beautify.
      molS = _skel || d.molText;
      if (!_skel) { try { console.warn("[draft] skeletal fallback: drawn geometry"); } catch (eW2b) {} }
      var _lin = (typeof fLinearizeMol === "function") ? fLinearizeMol(d.molText, _chainLive) : null;
      if (!_lin) { try { console.warn("[draft] linearizer failed, condensed = drawn geometry"); } catch (eW2) {} }
      molC = _lin || d.molText;
      molE = (typeof fGenExpandedMol === "function") ? (fGenExpandedMol(molC) || null) : null;
      if (!molE) { try { console.warn("[draft] expanded generation failed — mode disabled"); } catch (eW3) {} }
    } else {
      // Condensed slot must stay heavy-only: the overlay adds implicit H
      // itself, so any hand-drawn explicit H would double-render. Strip
      // first. Forks additionally linearize (MOLGEN_CC_LEN) so hand-drawn
      // C–C lengths always land on the shared bond length; updates keep the
      // author's geometry verbatim (single-slot update contract).
      // (drawn geometry otherwise kept verbatim).
      molC = d.molText;
      if (isFork && typeof fLinearizeMol === "function") {
        try { molC = fLinearizeMol(d.molText, _chainLive) || molC; } catch (eLn) {}
      }
      if (typeof fStripHydrogensMol === "function") {
        try { molC = isFork ? (fStripHydrogensMol(molC) || molC) : (fStripHydrogensMol(d.molText) || d.molText); } catch (eSt) {}
      }
      molE = (typeof fGenExpandedMol === "function") ? (fGenExpandedMol(molC) || null) : null;
      if (!molE) { try { console.warn("[draft] expanded generation failed — mode disabled"); } catch (eW4) {} }
      molS = _skel || molC;
      if (!_skel) { try { console.warn("[draft] skeletal fallback: drawn geometry"); } catch (eW5) {} }
    }
  } catch (eDv) { molC = d.molText; molE = null; molS = d.molText; }
  if (!molC) molC = d.molText;
  if (!molS) molS = molC;
  // One-line slot geometry receipt (Y-inclusive: straight vs zigzag layouts
  // share x-projections, so x-only sums cannot tell them apart).
  try {
    console.log("[draft] slots variant=" + drawnVariant + " skelSrc=" + (_skelSrc || "-") +
      " C:[" + _sigOf(molC) + "] E:[" + _sigOf(molE) + "] S:[" + _sigOf(molS) + "] draw:[" + _sigOf(d.molText) + "]");
  } catch (eLg2) {}
  // Stray-H guard (H32 class): verbatim slots keep hand geometry including
  // hand errors — an H a full bond length off its parent would be stored
  // forever. Edit-expanded writes the drawing verbatim, so check molE here;
  // regen'd slots carry our own validated H. Warn-only via confirm (one-shot
  // flag, reset on every Submit); Cancel/Draw keeps the draft for fixing.
  // Reference is the drawing's own H distribution (min H-bond length):
  // uniform hand/legacy/regen H pass (0/141 stored expanded flagged).
  if (isUpdate && d && d.mode === "edit" && drawnVariant === "expanded" && molE && !d._strayConfirmed) {
    var _strays = [];
    try { if (typeof fMolDraftStrayH === "function") _strays = fMolDraftStrayH(molE) || []; } catch (eSy) { _strays = []; }
    if (_strays.length) {
      var _sm = "", _sy = "";
      try { _sm = fMolDraftT("draftStrayH", "Some H sit far from their atoms"); } catch (eSm) { _sm = "Stray H?"; }
      try { _sy = fMolDraftT("draftStrayKeep", "Keep anyway"); } catch (eSy2) { _sy = "Keep anyway"; }
      try { console.warn("[draft] stray H: " + _strays.length + " over 1.5x H scale (" + _strays.slice(0, 4).map(function (s) { return "H" + s.h + "/C" + s.parent + "x" + s.ratio; }).join(", ") + ")"); } catch (eLw) {}
      if (typeof fScenarioConfirm === "function") {
        try { fScenarioConfirm(_sm + " (" + _strays.length + ")", function () { try { if (window.MulerDraft !== d || d._epoch !== _myEpochA || d._submitId !== _mySidA) return; d._strayConfirmed = true; d.accepting = false; } catch (eFc) {} try { fMolDraftAccept(); } catch (eFa) {} }, _sy); } catch (eSc2) { try { d.accepting = false; } catch (eAb3) {} }
        return;
      }
    }
  }
  // Input once; poll at most six reads 120 ms apart. Capture actual applet
  // MOL + scale, restoring in finally even when import/read fails. Deferred
  // Cancel retains ownership; replacement/selection changes relinquish it so
  // old content cannot overwrite a new view.
  async function fMolDraftDepictSmiles(applet, smiles, expectHeavy) {
    if (!liveDraft() || !smiles || !applet || typeof applet.readGenericMolecularInput !== "function" ||
        typeof applet.molFile !== "function" || typeof applet.readMolFile !== "function" ||
        typeof applet.clear !== "function") return null;
    var priorMol, priorScale, captured = false, out = null;
    try {
      priorMol = applet.molFile();
      if (typeof priorMol !== "string") return null;
      if (typeof applet.getMolecularAreaScale !== "function" || typeof applet.setMolecularAreaScale !== "function") return null;
      priorScale = applet.getMolecularAreaScale();
      if (!Number.isFinite(priorScale)) return null;
      captured = true;
      applet.clear();
      var cleared = applet.molFile();
      var empty = cleared ? fParseMolV2000(cleared) : null;
      if (cleared && (!empty || empty.atoms.length)) return null;
      applet.readGenericMolecularInput(smiles);
      if (typeof applet.deferredRepaint === "function") applet.deferredRepaint();
      for (var ri = 0; ri < 6; ri++) {
        if (!liveDraft()) break;
        var result = null, parsed = null;
        try { result = applet.molFile(); parsed = result ? fParseMolV2000(result) : null; } catch (eRead) {}
        if (parsed && parsed.atoms.length && expectHeavy > 0 &&
            parsed.atoms.filter(function (a) { return fIsHeavyEl2D(a.el); }).length === expectHeavy) {
          out = result;
          break;
        }
        if (ri === 0 && typeof applet.repaint === "function") applet.repaint();
        if (ri < 5) await new Promise(function (resolve) { setTimeout(resolve, 120); });
      }
    } catch (eD) { out = null; }
    finally {
      if (captured && ownsDraft()) {
        try { if (priorMol) applet.readMolFile(priorMol); else applet.clear(); }
        catch (eR) { out = null; try { console.warn("[draft] depict content restoration failed", eR); } catch (eL) {} }
        try { applet.setMolecularAreaScale(priorScale); }
        catch (eS) { out = null; try { console.warn("[draft] depict scale restoration failed", eS); } catch (eL2) {} }
      } else out = null;
    }
    return liveDraft() ? out : null;
  }
  // Tri-state verdicts travel with the molecule: the saved file becomes
  // labeled eval data (predicted pair + oracle + human label) for engine work.
  var _vc = { gr: "unconfirmed", en: "unconfirmed", enAutoValidated: false, enAutoSource: null };
  try {
    if (d.verdictGR === "correct" || d.verdictGR === "wrong") _vc.gr = d.verdictGR;
    if (d.verdictEN === "correct" || d.verdictEN === "wrong") _vc.en = d.verdictEN;
    _vc.enAutoValidated = !!d.enAutoValidated;
    try { _vc.enAutoSource = (d.enAutoSource === "openclatura" || d.enAutoSource === "pubchem" || d.enAutoSource === "openclatura-sys" || d.enAutoSource === "pubchem-sys") ? d.enAutoSource : (_vc.enAutoValidated ? "pubchem" : null); } catch (eAS2) {}
  } catch (eVc) {}
  var rec = {
    key: key,
    formula: formula,
    smiles: d.smiles,
    classification: cls,
    grName: d.engineName,
    engineEN: d.engineEN || null,
    engineDelegated: !!d.engineDelegated,
    nameCheck: _vc,
    slots: slotsCopy,
    systematicEN: (hit && (hit.systematic || hit.iupacEN)) || null,
    iupacPubchem: (hit && (hit.iupacPubchem || hit.iupac)) || null,
    titlePubchem: (hit && (hit.title || hit.titlePubchem)) || null,
    openclaturaEN: (d.openclatura && d.openclatura.name) || null,
    openclaturaOpsin: (d.openclatura && d.openclatura.opsin) || null,
    openclaturaDone: !!((d.openclatura && d.openclatura.name) || null),
    pubchemCID: (hit && hit.cid) || null,
    canonicalSmiles: (hit && hit.canonicalSmiles) || null,
    sdf3D: d.sdf3D || null,
    sdf3DSource: d.sdf3DSource || null,
    sdf3DStatus: d.sdf3DStatus || "provisional",
    sdf3DProvenance: d.sdf3DProvenance || fMolDraft3DProvenance(d.sdf3DSource, "accept"),
    file3D: null,
    author: "",
    status: "draft",
    history: [{ t: Date.now(), action: "accepted", mode: d.mode, source: d.sourceMol || null, sdf3DSource: d.sdf3DSource || null, verdict: { gr: _vc.gr, en: _vc.en } }]
  };
  if (!liveDraft()) return;
  rec.structure2D_Condensed = molC;
  rec.structure2D_Expanded = molE;
  rec.structure2D_Skeletal = molS;
  if (isUpdate) {
    // Update in place, single slot: same molecule + layout-only edit rewrites
    // only the edited representation (condensed: stripped verbatim; expanded:
    // verbatim; skeletal: ladder output — never raw canvas). Siblings stay
    // byte-untouched so their hand-tuned geometry cannot go stale. Metadata
    // (formula/names/oracle) refreshes from the new preview; key stable.
    var prev = null;
    try { prev = nameExamples[key] || null; } catch (ePv) { prev = null; }
    if (!prev) { try { d.accepting = false; } catch (eAb4) {} return; }
    var _slot = "condensed";
    try { _slot = (drawnVariant === "expanded") ? "expanded" : (drawnVariant === "skeletal" || drawnVariant === "condensedZigZag") ? "skeletal" : "condensed"; } catch (eSl2) { _slot = "condensed"; }
    try {
      if (_slot === "expanded" && molE) prev.structure2D_Expanded = molE;
      else if (_slot === "skeletal" && molS) prev.structure2D_Skeletal = molS;
      else if (molC) prev.structure2D_Condensed = molC;
    } catch (eWs) {}
    prev.formula = formula;
    prev.smiles = d.smiles;
    prev.classification = cls;
    prev.grName = d.engineName;
    prev.engineEN = d.engineEN || null;
    prev.engineDelegated = !!d.engineDelegated;
    prev.nameCheck = _vc;
    prev.slots = slotsCopy;
    prev.systematicEN = rec.systematicEN;
    prev.iupacPubchem = rec.iupacPubchem;
    prev.titlePubchem = rec.titlePubchem;
    prev.openclaturaEN = rec.openclaturaEN;
    prev.openclaturaOpsin = rec.openclaturaOpsin;
    try { if (rec.openclaturaEN) prev.openclaturaDone = true; } catch (eOCd) {}
    prev.pubchemCID = rec.pubchemCID;
    prev.canonicalSmiles = rec.canonicalSmiles;
    prev.sdf3D = rec.sdf3D;
    prev.sdf3DSource = rec.sdf3DSource;
    prev.sdf3DStatus = rec.sdf3DStatus;
    prev.sdf3DProvenance = rec.sdf3DProvenance;
    try {
      prev.history = prev.history || [];
      prev.history.push({ t: Date.now(), action: "updated-slot:" + _slot, mode: d.mode, source: d.sourceMol || null, verdict: { gr: _vc.gr, en: _vc.en } });
    } catch (eH) {}
    rec = prev;
    try { if (typeof fMolDraftMarkNewCustom === "function") fMolDraftMarkNewCustom(key); } catch (eMk) {}
  } else {
    try {
      window.nameExamplesCustom = window.nameExamplesCustom || {};
    } catch (eRg) {}
    try { window.nameExamplesCustom[key] = rec; if (typeof fMolDraftMarkNewCustom === "function") fMolDraftMarkNewCustom(key); } catch (eR2) {}
    try { nameExamples[key] = rec; } catch (eN) { try { d.accepting = false; } catch (eAb5) {} return; }
  }
  fMolDraftTeardownDisplay();
  // Rebuild the menu so the new row exists, then select it: the rebuild
  // itself marks nothing (all groups closed, no selectedLi — marking only
  // happens on row clicks), and fSelectMol doesn't touch menu classes.
  try { if (typeof fInitNomeclatureMenu === "function") fInitNomeclatureMenu(); } catch (eM) {}
  try { selectedMol = key; } catch (eSel) { return; }
  try { if (typeof fSelectMol === "function") fSelectMol(); } catch (eF) {}
  try { if (typeof fMolDraftSyncButtons === "function") fMolDraftSyncButtons(); } catch (eDs) {}
  // Mark the accepted row + open its group (mirror fRestoreMenuSelection):
  // without this the new entry sits unmarked inside a closed group.
  try {
    var _arow = document.getElementById(key);
    if (_arow) {
      var _marked = document.querySelectorAll("#nomeclature2Menu .menuLi.selectedLi");
      for (var _mi = 0; _mi < _marked.length; _mi++) {
        try { _marked[_mi].classList.remove("selectedLi"); } catch (eMr) {}
      }
      try { _arow.classList.add("selectedLi"); } catch (eMa) {}
      try {
        var _cont = _arow.closest ? _arow.closest(".exmplContainer") : null;
        if (_cont) {
          _cont.classList.remove("closed");
          _cont.classList.add("open");
          try { _cont.style.display = ""; } catch (eDd) {}
        }
        var _hdr = _cont && _cont.previousElementSibling && _cont.previousElementSibling.classList &&
          _cont.previousElementSibling.classList.contains("crossMenuLi") ? _cont.previousElementSibling : null;
        var _hdrs = document.querySelectorAll("#nomeclature2Menu .crossMenuLi.selectedLi");
        for (var _hi = 0; _hi < _hdrs.length; _hi++) {
          try { _hdrs[_hi].classList.remove("selectedLi"); } catch (eHr) {}
        }
        if (_hdr && _hdr.classList) _hdr.classList.add("selectedLi");
      } catch (eHg) {}
      try { _arow.scrollIntoView({ block: "nearest" }); } catch (eSv) {}
    }
  } catch (eMs) {}
  // Outcome toast: unconfirmed names are saved, not blocked — but said aloud.
  try {
    if (_vc.gr === "correct" && _vc.en === "correct") fMolDraftToast(fMolDraftT("acceptKept", "Accepted into this session — save it from Settings."));
    else fMolDraftToast(fMolDraftT("draftSavedUnconfirmed", "Accepted — with unconfirmed names."));
  } catch (eTk) { try { fMolDraftToast(fMolDraftT("acceptKept", "Accepted into this session — save it from Settings.")); } catch (eT2) {} }
  } finally {
    d.accepting = false;
    if (window.MulerDraftAcquisition === d) window.MulerDraftAcquisition = null;
    if (window.MulerDraft === d) {
      if (d.cancelRequested) fMolDraftCancel();
      else { try { fMolDraftSyncBar(); } catch (eSyEnd) {} }
    }
  }
}

// Edit-entry visual state: inactive when no molecule is selected (menu-only
// steps, deselected). Click-time guard in fMolDraftEnter is the backstop;
// this is display only. Called from fSelectMol/fDeselectMol tails.

function fMolDraft3DCurrent(job) {
  try {
    return !!(job && !job.cancelled && fMolDraft3DJob === job &&
      window.MulerDraft === job.draft && job.draft._epoch === job.epoch &&
      job.draft._submitId === job.submitId && job.draft.smiles === job.smiles &&
      job.draft.molText === job.molText && !job.draft.cancelRequested && !job.draft.stale &&
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
    if (!job.cancelled && job.minimizing && job.applet === jmolAppletNomeclature &&
        job.revision === fMolDraft3DRevision) {
      try { fJSmolScript(job.applet, 'minimize STOP;'); } catch (eStop) {}
    }
    job.cancelled = true;
    if (job.wake) { try { job.wake(); } catch (eWake) {} job.wake = null; }
  }
  fMolDraft3DJob = null;
  try { fMolDraftMinWaitClose(job); } catch (eDialog) {}
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
      if (!hydrogenCount) return true;
      var valence = valences[atom.el];
      if (atom.el === "N") valence += atom.charge || 0;
      else if (atom.el === "O") valence += atom.charge || 0;
      else if (atom.el === "C" && atom.charge) valence = 3;
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
// Step budget + blind wait per minimize round (v55.x): the wait is
// wall-clock (any mid-run applet poll would interrupt the in-flight run),
// so the step count bounds the runtime. Repeat presses re-fire from the
// live model, walking further downhill each round (fresh rounds use
// MOLMIN_STEPS with the movement gate; further rounds use
// MOLMIN_FURTHER_STEPS with no gate — any valid result banks).
var MOLMIN_STEPS = 500;
var MOLMIN_FURTHER_STEPS = 200;
var MOLMIN_WAIT_S = 10;
// Blind-wait budget per minimize round (v55.x): the base 10 s covers small
// systems; large systems need longer since the step budget scales worse
// than linear with size. Capped so a pathological run can't pin the UI
// forever; the wait-window countdown shows the budget. Same helper feeds
// the relax sleep and both window call sites, so the countdown and the
// read-back always agree.

function fMolDraftMeanDisplacement(beforeMol, afterSDF) {
  try {
    if (typeof fParseMolV2000 !== "function" || !beforeMol || !afterSDF) return -1;
    var a = fParseMolV2000(beforeMol), b = fParseMolV2000(afterSDF);
    if (!a || !b || !a.atoms || !b.atoms) return -1;
    var ha = [], hb = [], i;
    for (i = 0; i < a.atoms.length; i++) { var ea = String(a.atoms[i].el || ""); if (ea && ea !== "H" && ea !== "h") ha.push(a.atoms[i]); }
    for (i = 0; i < b.atoms.length; i++) { var eb = String(b.atoms[i].el || ""); if (eb && eb !== "H" && eb !== "h") hb.push(b.atoms[i]); }
    if (!ha.length || ha.length !== hb.length) return -1;
    var sum = 0;
    for (i = 0; i < ha.length; i++) {
      var dx = (hb[i].x || 0) - (ha[i].x || 0), dy = (hb[i].y || 0) - (ha[i].y || 0), dz = (hb[i].z || 0) - (ha[i].z || 0);
      sum += Math.sqrt(dx * dx + dy * dy + dz * dz);
    }
    return sum / ha.length;
  } catch (e) { return -1; }
}

// Diagnostic movement only: coordinate motion does not establish physical
// convergence. The upstream diagnostic measures displacement of heavy
// atoms (the v55.7 jiggle already perturbs every atom, so anything at or
// below jiggle noise means the minimizer never acted). Mean displacement
// under 0.05 A rejects, even if the candidate parses.

async function fMolDraftLocal3DRelaxFF(expectHeavy, ffName, job, steps, skipGate) {
  if (!fMolDraft3DCurrent(job)) return null;
  var before = fMolDraftReadBackSDF(expectHeavy, job);
  if (!before) return null;
  if (fMolDraft3DWrite(job, 'set forceField ' + ffName + ';', false) === null) return null;
  if (!fMolDraft3DCurrent(job)) return null;
  job.minimizing = true;
  var stepBudget = Number.isFinite(steps) && steps > 0 ? Math.floor(steps) : MOLMIN_STEPS;
  try {
    var waitSecs = fMolDraftMinWaitSecs(expectHeavy);
    fMolDraftMinWaitShow(function () { fMolDraftMinWaitAbort(job); }, waitSecs, job);
    if (fMolDraft3DWrite(job, 'select all; minimize steps ' + stepBudget + ';', false) === null) return null;
    await fMolDraft3DWait(job, waitSecs * 1000);
    if (!fMolDraft3DCurrent(job)) return null;
    // Normal completion never sends STOP; STOP is reserved for cancellation.
    var candidate = fMolDraftReadBackSDF(expectHeavy, job);
    job.lastMotion = candidate ? fMolDraftMeanDisplacement(before, candidate) : -1;
    return candidate;
  } finally { job.minimizing = false; }
}

async function fMolDraftLocal3DRelaxBoth(expectHeavy, job, steps, skipGate) {
  if (!fMolDraft3DCurrent(job)) return null;
  var mmff = await fMolDraftLocal3DRelaxFF(expectHeavy, 'MMFF', job, steps, skipGate);
  if (!fMolDraft3DCurrent(job)) return null;
  if (mmff && (skipGate || job.lastMotion >= 0.05)) return mmff;
  var uff = await fMolDraftLocal3DRelaxFF(expectHeavy, 'UFF', job, steps, skipGate);
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

async function fMolDraftLocal3DFromMol(molText, expectHeavy, skipPrepare, job, steps, skipGate) {
  if (!fMolDraft3DCurrent(job)) return { sdf:null, prepared:false };
  var prepared = skipPrepare ? !!fMolDraftReadBackSDF(expectHeavy, job) : !!fMolDraftLocal3DPrepare(molText, expectHeavy, job).ok;
  if (!prepared || !fMolDraft3DCurrent(job)) return { sdf:null, prepared:false };
  var sdf = await fMolDraftLocal3DRelaxBoth(expectHeavy, job, steps, skipGate);
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
// Cancel/STOP is tied to the exact still-owned model and running round.

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
  fMolDraftMinWaitClose(job);
  fMolDraft3DJob = null;
  return local && fMolDraftValidSDF3D(local.sdf, expectHeavy, molText) ? { sdf:local.sdf, source:'jsmol-min' } : empty;
}


function fMolDraftJiggleZ(molText, amp) {
  try {
    if (!molText || typeof fParseMolV2000 !== "function") return molText;
    if (typeof fMolCountsLine !== "function") return molText;
    var refH = 0;
    try {
      var ref = fParseMolV2000(molText) || null;
      if (ref && ref.atoms) for (var i0 = 0; i0 < ref.atoms.length; i0++) { var re0 = String(ref.atoms[i0].el || ""); if (re0 && re0 !== "H" && re0 !== "h") refH++; }
    } catch (eR) { refH = 0; }
    var lines = String(molText).split(/\r?\n/);
    var ci = fMolCountsLine(lines);
    if (ci < 0) return molText;
    var nA = parseInt((lines[ci] || "").substring(0, 3), 10);
    if (!(nA > 0)) return molText;
    var A = (typeof amp === "number" && isFinite(amp) && amp > 0) ? amp : 0.3;
    for (var i = 0; i < nA; i++) {
      var idx = ci + 1 + i, L = lines[idx] || "";
      while (L.length < 34) L += " ";
      var jz = (Math.random() - 0.5) * 2 * A;
      var zs = ("          " + jz.toFixed(4)).slice(-10);
      lines[idx] = L.substring(0, 20) + zs + L.substring(30);
    }
    var out = lines.join("\n");
    try {
      var chk = fParseMolV2000(out) || null, chkH = 0;
      if (chk && chk.atoms) for (var k = 0; k < chk.atoms.length; k++) { var ce = String(chk.atoms[k].el || ""); if (ce && ce !== "H" && ce !== "h") chkH++; }
      if (!chk || (refH && chkH !== refH)) {
        try { console.log("[SDF-3D] tier local-min: jiggle failed self-verify — using un-jiggled input"); } catch (eLgV) {}
        return molText;
      }
    } catch (eV) { return molText; }
    try { console.log("[SDF-3D] tier local-min: z-jiggle ±" + A + " A on " + nA + " atoms"); } catch (eL) {}
    return out;
  } catch (e) { return molText; }
}

// Blocking wait window for the local-minimize run (v55.x): same overlay /
// panel skin as the scenario confirm, single Cancel button. Cancel aborts the
// in-flight run via the established _submitId invalidation (Draw's
// mechanism) plus local cleanup — the stale async continuation guard-fails
// and returns without touching anything. ESC/backdrop = Cancel. Close is
// idempotent; safe to call on every exit path (resolve, miss, Draw,
// teardown, Present).
var fMolDraftMinWaitEl = null;
var fMolDraftMinWaitKey = null;
var fMolDraftMinWaitPrevFocus = null;
var fMolDraftMinWaitTimer = null;
var fMolDraftMinWaitJob = null;

function fMolDraftUntangle2D(molText, minSep) {
  try {
    if (!molText || typeof fParseMolV2000 !== "function") return molText;
    if (typeof fMolCountsLine !== "function") return molText;
    var ref = fParseMolV2000(molText) || null;
    if (!ref || !ref.atoms || !ref.atoms.length) return molText;
    var refH = 0, i0;
    for (i0 = 0; i0 < ref.atoms.length; i0++) { var re0 = String(ref.atoms[i0].el || ""); if (re0 && re0 !== "H" && re0 !== "h") refH++; }
    if (!refH) return molText;
    var MS = (typeof minSep === "number" && isFinite(minSep) && minSep > 0) ? minSep : 0.9;
    var n = ref.atoms.length, xs = [], ys = [], heavy = [], i;
    for (i = 0; i < n; i++) {
      xs.push(ref.atoms[i].x || 0); ys.push(ref.atoms[i].y || 0);
      var e0 = String(ref.atoms[i].el || "");
      heavy.push(!!(e0 && e0 !== "H" && e0 !== "h"));
    }
    var bonded = {};
    try {
      if (ref.bonds) for (var b = 0; b < ref.bonds.length; b++) {
        var a1 = ref.bonds[b][0] - 1, a2 = ref.bonds[b][1] - 1;
        if (a1 >= 0 && a2 >= 0 && a1 < n && a2 < n) { bonded[a1 + "_" + a2] = 1; bonded[a2 + "_" + a1] = 1; }
      }
    } catch (eB) {}
    var fixed = 0;
    for (var sw = 0; sw < 50; sw++) {
      var moved = false;
      for (var p = 0; p < n; p++) {
        if (!heavy[p]) continue;
        for (var q = p + 1; q < n; q++) {
          if (!heavy[q] || bonded[p + "_" + q]) continue;
          var dx = xs[q] - xs[p], dy = ys[q] - ys[p];
          var d = Math.sqrt(dx * dx + dy * dy);
          if (!(d < MS)) continue;
          var ux = 0.5, uy = 0;
          if (d > 1e-6) { ux = dx / d; uy = dy / d; }
          else { var ang = Math.random() * 2 * Math.PI; ux = Math.cos(ang); uy = Math.sin(ang); }
          var push = (MS - d) / 2 + 0.01;
          xs[p] -= ux * push; ys[p] -= uy * push;
          xs[q] += ux * push; ys[q] += uy * push;
          moved = true; fixed++;
        }
      }
      if (!moved) break;
    }
    if (!fixed) return molText;
    var lines = String(molText).split(/\r?\n/);
    var ci = fMolCountsLine(lines);
    if (ci < 0) return molText;
    for (var w = 0; w < n; w++) {
      var idx = ci + 1 + w, L = lines[idx] || "";
      while (L.length < 34) L += " ";
      var xstr = ("          " + xs[w].toFixed(4)).slice(-10);
      var ystr = ("          " + ys[w].toFixed(4)).slice(-10);
      lines[idx] = xstr + ystr + L.substring(20);
    }
    var out = lines.join("\n");
    try {
      var chk = fParseMolV2000(out) || null, chkH = 0;
      if (chk && chk.atoms) for (var k = 0; k < chk.atoms.length; k++) { var ce = String(chk.atoms[k].el || ""); if (ce && ce !== "H" && ce !== "h") chkH++; }
      if (!chk || chkH !== refH) {
        try { console.log("[SDF-3D] tier local-min: untangle failed self-verify — using input"); } catch (eLgV) {}
        return molText;
      }
    } catch (eV) { return molText; }
    try { console.log("[SDF-3D] tier local-min: 2D untangle fixed " + fixed + " overlaps (minSep " + MS + ")"); } catch (eL) {}
    return out;
  } catch (e) { return molText; }
}

// Pure-JS z-jiggle (v55.7+): breaks the planar-saddle trap before MMFF runs.
// From exactly-flat z=0 every z-force is zero by symmetry, so steepest
// descent can never leave the plane (observed: heavies frozen at 0.000 A
// while H-noise faked spread). ±0.3 A uniform noise per atom gives real 3D
// gradients; small enough to keep topology. Byte-identical except the z
// field (cols 20-30). Self-verifying (v55.8): short-line MOLs used to come
// out unparseable and poison the loader — the result is parsed and heavy
// count-checked against the input, falling back to the un-jiggled input.

function fJSmolScript(applet, cmd) {
  fMolDraft3DWillScript(applet, cmd);
  if (!fJSmolLive()) { fMulerNotePending3D(); return null; }
  try { return Jmol.script(applet, cmd); } catch (e) { fMulerNotePending3D(); return null; }
}


function fJSmolScriptWait(applet, cmd) {
  fMolDraft3DWillScript(applet, cmd);
  if (!fJSmolLive()) { fMulerNotePending3D(); return null; }
  try { return Jmol.scriptWait(applet, cmd); } catch (e) { fMulerNotePending3D(); return null; }
}


function fJSmolScriptEcho(applet, cmd) {
  if (!fJSmolLive()) { fMulerNotePending3D(); return ""; }
  try { return Jmol.scriptEcho(applet, cmd); } catch (e) { fMulerNotePending3D(); return ""; }
}


function fJSmolLoadInlineSDF(applet, sdfText, tailCmd) {
  try {
    var clean = String(sdfText == null ? "" : sdfText);
    if (!clean) return false;
    if (clean.split(/\r?\n/).some(function (line) { return /^\s*end\s+[\"\']model\.sdf[\"\']\s*;?\s*$/i.test(line); })) return false;
    // SDF V2000 has no double quotes, but a stray one would break the
    // `load data "..."` wrapper — neutralize defensively.
    clean = clean.replace(/"/g, "'");
    // Guard the `end "model.sdf"` terminator: a payload line that is exactly
    // the terminator would truncate the DATA block early. Such content never
    // occurs in PubChem SDF, but fail closed rather than issue a split load.
    try {
      var _lines = clean.split(/\r?\n/);
      for (var _li = 0; _li < _lines.length; _li++) {
        if (_lines[_li].trim() === 'end "model.sdf"') return false;
      }
    } catch (eTl) {}
    if (clean.charAt(clean.length - 1) !== "\n") clean += "\n";
    var tail = String(tailCmd == null ? "" : tailCmd);
    var cmd = "frank off;load data \"model.sdf\"\n" + clean + "end \"model.sdf\"; select all; center selected;" + tail;
    if (typeof fJSmolScript === "function") {
      if (fJSmolScript(applet, cmd) === null && typeof fMulerNotePending3D === "function") { try { fMulerNotePending3D(); } catch (eP3) {} return false; }
    }
    else if (typeof Jmol !== "undefined" && Jmol && typeof Jmol.script === "function") Jmol.script(applet, cmd);
    return true;
  } catch (eIn) { return false; }
}


function fMolDraftMinWaitClose(job) {
  if (job && fMolDraftMinWaitJob !== job) return;
  fMolDraftMinWaitJob = null;
  try { if (fMolDraftMinWaitTimer) { clearInterval(fMolDraftMinWaitTimer); fMolDraftMinWaitTimer = null; } } catch (eT) {}
  var ov = null;
  try { ov = fMolDraftMinWaitEl; } catch (eO) { ov = null; }
  try {
    if (ov) {
      ov.classList.remove("show");
      if (ov.parentNode) { try { ov.parentNode.removeChild(ov); } catch (eR) {} }
    }
  } catch (eRm) {}
  try { fMolDraftMinWaitEl = null; } catch (eN) {}
  if (fMolDraftMinWaitKey) {
    try { document.removeEventListener("keydown", fMolDraftMinWaitKey, true); } catch (eK) {}
    try { fMolDraftMinWaitKey = null; } catch (eK2) {}
  }
  try {
    if (fMolDraftMinWaitPrevFocus && document.contains(fMolDraftMinWaitPrevFocus) && fMolDraftMinWaitPrevFocus.focus) fMolDraftMinWaitPrevFocus.focus();
  } catch (eF2) {}
  try { fMolDraftMinWaitPrevFocus = null; } catch (eP) {}
}

function fMolDraftMinWaitShow(onCancel, totalS, job) {
  if (!fMolDraft3DCurrent(job)) return;
  try { fMolDraftMinWaitClose(); } catch (eC) {}
  var ov = document.createElement("div");
  ov.id = "molDraftMinWait";
  ov.setAttribute("role", "dialog");
  ov.setAttribute("aria-modal", "true");
  var _msg = "";
  try { _msg = fMolDraftT("draftMinimizing", "Minimizing 3D… please wait."); } catch (eMm) { _msg = "Minimizing 3D… please wait."; }
  var _cancelLbl = "Cancel";
  try { var _cl = fMolDraftT("draftCancel", "Cancel"); if (_cl) _cancelLbl = _cl; } catch (eCl) {}
  ov.innerHTML = "<div class='scConfirmPanel'><div class='scConfirmMsg'></div>" +
    "<div class='scConfirmBtns'><button type='button' class='scConfirmCancel'></button></div></div>";
  try {
    var m = ov.querySelector(".scConfirmMsg");
    if (m) m.textContent = _msg;
    var cb = ov.querySelector(".scConfirmCancel");
    if (cb) cb.textContent = _cancelLbl;
  } catch (eM) {}
  try { document.body.appendChild(ov); } catch (eA) { return; }
  try { fMolDraftMinWaitJob = job; fMolDraftMinWaitEl = ov; } catch (eE) {}
  try { fMolDraftMinWaitPrevFocus = document.activeElement; } catch (eAf) { fMolDraftMinWaitPrevFocus = null; }
  var _fireCancel = function () {
    if (fMolDraftMinWaitJob !== job || !fMolDraft3DCurrent(job)) return;
    var fn = null;
    try { fn = (typeof onCancel === "function") ? onCancel : null; } catch (eG) { fn = null; }
    try { fMolDraftMinWaitClose(); } catch (eCc) {}
    if (fn) { try { fn(); } catch (eFn) {} }
  };
  var cancelB = null;
  try { cancelB = ov.querySelector(".scConfirmCancel"); } catch (eQ) {}
  if (cancelB) cancelB.onclick = function (e) { if (e && e.stopPropagation) e.stopPropagation(); _fireCancel(); };
  // No backdrop-cancel: a stray click anywhere must never abort a run.
  // Dismissal is Cancel button or ESC only; the window otherwise stays
  // until the budgeted wait elapses.
  ov.onclick = function (e) { if (e && e.stopPropagation) e.stopPropagation(); };
  fMolDraftMinWaitKey = function (e) {
    if (e.key === "Escape" || e.key === "Esc") {
      if (e.preventDefault) e.preventDefault();
      if (e.stopPropagation) e.stopPropagation();
      _fireCancel();
      return;
    }
    // Single-button trap: Tab never leaves the dialog.
    if (e.key === "Tab") {
      if (e.preventDefault) e.preventDefault();
      try { var b = ov.querySelector(".scConfirmCancel"); if (b && b.focus) b.focus(); } catch (eT) {}
    }
  };
  try { document.addEventListener("keydown", fMolDraftMinWaitKey, true); } catch (eK3) {}
  ov.classList.add("show");
  try { if (cancelB && cancelB.focus) cancelB.focus(); } catch (eFo) {}
  // Live countdown (page-side timer only — zero applet traffic, so the
  // undisturbed-run rule holds). Clamps at 0; the window closes when the
  // read-back lands.
  try {
    var _secs = (typeof totalS === "number" && totalS > 0) ? totalS : 0;
    if (_secs > 0) {
      var _mEl = null;
      try { _mEl = ov.querySelector(".scConfirmMsg"); } catch (eMq) { _mEl = null; }
      var _deadline = new Date().getTime() + _secs * 1000;
      var _tick = function () {
        try {
          var _left = Math.ceil((_deadline - new Date().getTime()) / 1000);
          if (_left <= 0) {
            try { if (_mEl) _mEl.textContent = _msg; } catch (eZ) {}
            try { if (fMolDraftMinWaitTimer) { clearInterval(fMolDraftMinWaitTimer); fMolDraftMinWaitTimer = null; } } catch (eZi) {}
            return;
          }
          try { if (_mEl) _mEl.textContent = _msg + " (" + _left + "s)"; } catch (eTs) {}
        } catch (eTk) {}
      };
      try { if (fMolDraftMinWaitTimer) { clearInterval(fMolDraftMinWaitTimer); fMolDraftMinWaitTimer = null; } } catch (eTc) {}
      try { fMolDraftMinWaitTimer = setInterval(_tick, 250); } catch (eTi) {}
      try { _tick(); } catch (eT0) {}
    }
  } catch (eCt) {}
}
// Draft-owned 3D work. A model replacement through the shared JSmol wrappers
// revokes the job before writing; asynchronous continuations never reacquire it.
var fMolDraft3DRevision = 0;
var fMolDraft3DJob = null;
var fMolDraft3DWriter = null;

function fMolDraftMinWaitSecs(expectHeavy) {
  try {
    var n = (typeof expectHeavy === "number" && expectHeavy > 0) ? expectHeavy : 0;
    var s = MOLMIN_WAIT_S + Math.max(0, n - 30);
    if (s > 120) s = 120;
    return s;
  } catch (eS) { return 10; }
}
// The size-budgeted MMFF/UFF rounds remain bounded. Motion only decides
// whether to try the fallback force field; it cannot certify convergence.

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

function fSetSettingChecked(id, on) {
  try {
    var el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle("selectedCheck", !!on);
    el.classList.toggle("unselectedCheck", !on);
  } catch (e) {}
}

function fSyncAtomColorModeRadios() {
  try {
    if (typeof atomColorMode2D === "undefined") return;
    var _cmBtns = document.querySelectorAll("#atomColorMode .atomColorModeRadio");
    for (var _ci = 0; _ci < _cmBtns.length; _ci++) {
      var _on = _cmBtns[_ci].getAttribute("data-color-mode") === atomColorMode2D;
      _cmBtns[_ci].classList.remove(_on ? "unselectedRadio" : "selectedRadio");
      _cmBtns[_ci].classList.add(_on ? "selectedRadio" : "unselectedRadio");
    }
  } catch (e) {}
}
var MULER_VIEWER_SETTINGS = [
  { row: "radioChainMode", sync: function () { try { if (typeof fUpdateChainModeButton === "function") fUpdateChainModeButton(); } catch (e) {} } },
  { row: "atomColorModeRow", sync: function () {
      try { if (typeof svgAtomColors2DFlag !== "undefined") fSetSettingChecked("svgAtomColorCheck", !!svgAtomColors2DFlag); } catch (eA) {}
      try { if (typeof fSyncAtomColorModeRadios === "function") fSyncAtomColorModeRadios(); } catch (eB) {}
      try { if (typeof fSyncAtomColorModeDisabled === "function") fSyncAtomColorModeDisabled(); } catch (eC) {}
  } },
  { row: "viewerMaxHeightSetting", sync: function () { try { fViewerMaxHeightSync(); } catch (e) {} } },
  { row: "viewerBothHeightSetting", sync: function () { try { fViewerBothHeightSync(); } catch (e) {} } }
];

function fSyncViewerSettingsUI() {
  try {
    for (var i = 0; i < MULER_VIEWER_SETTINGS.length; i++) {
      try { var _se = MULER_VIEWER_SETTINGS[i]; if (_se && typeof _se.sync === "function") _se.sync(); } catch (eI) {}
    }
  } catch (eO) {}
}


function fMolDraftDownloadSingle(rec) {  // One molecule per file (Accept auto-save). Merge-safe assignment so any
  // number of collected files coexist regardless of load order — a plain
  // `var nameExamplesCustom = ...` would let file #2 clobber file #1.
  try {
    if (!rec || !rec.key) return false;
    var one = {};
    one[rec.key] = rec;
    var _nc = rec.nameCheck || { gr: "unconfirmed", en: "unconfirmed" };
    var header = "/* MuLER custom draft molecule (v55 tiered-3D, manual save from Ρυθμίσεις).\n" +
      "   Molecule: " + rec.key + (rec.grName ? " (" + rec.grName + ")" : "") + "\n" +
      "   Status: " + (rec.status || "draft") + " | " + new Date().toISOString().slice(0, 10) + "\n" +
      "   3D: " + (rec.sdf3DSource || "none") + " (" + (rec.sdf3DStatus || "unspecified") + ")\n" +
      "   Names: GR " + _nc.gr + ", EN " + _nc.en + (_nc.enAutoValidated ? " (EN auto: " + (_nc.enAutoSource === "openclatura" ? "OpenClatura" : (_nc.enAutoSource === "openclatura-sys" ? "OpenClatura-sys" : (_nc.enAutoSource === "pubchem-sys" ? "PubChem-sys" : "PubChem"))) + ")" : "") + "\n" +
      "   Place next to the data file (js/) and register it:\n" +
      "   <script src=\"js/" + fMolDraftFileSlug(rec) + "\"><\/script> */\n" +
      "window.nameExamplesCustom = Object.assign(window.nameExamplesCustom || {}, " +
      JSON.stringify(one, null, 2) + ");\n";
    if (typeof fScenarioSaveBlobDownload === "function") {
      return !!fScenarioSaveBlobDownload(fMolDraftFileSlug(rec), new Blob([header], { type: "text/javascript" }));
    }
  } catch (eD) {
    try { console.warn("[draft] custom file download failed", eD); } catch (eL) {}
  }
  return false;
}

// Bundle download (v54.26): one file holding every given custom molecule as
// its own merge-safe Object.assign statement (same JSON bytes as single
// files, each under a section comment). One download = one Save dialog, so
// "ask where to save" browsers reliably keep all molecules — the per-file
// loop lost all but the last to stacked dialogs. Dropping the bundle into
// js/ + registering works like single files (boot merge executes each
// statement in order); statements stay human-splittable.

function fMolDraftDownloadBundle(recs) {
  try {
    var list = Array.isArray(recs) ? recs.filter(function (r) { return r && r.key; }) : [];
    if (!list.length) return false;
    var date = "";
    try { date = new Date().toISOString().slice(0, 10).replace(/-/g, ""); } catch (eD) { date = "nodate"; }
    var filename = "MULERMOC_custom_" + date + "_" + list.length + "mols_data.js";
    var header = "/* MuLER custom draft molecules, session bundle (v55 tiered-3D).\n" +
      "   Molecules (" + list.length + "): " + list.map(function (r) { return r.key + (r.grName ? " (" + r.grName + ")" : ""); }).join("; ") + "\n" +
      "   Status/date: " + new Date().toISOString().slice(0, 10) + "\n" +
      "   Place next to the data file (js/) and register it:\n" +
      "   <script src=\"js/" + filename + "\"><\/script> */\n";
    var body = "";
    for (var i = 0; i < list.length; i++) {
      var one = {};
      one[list[i].key] = list[i];
      var _nc = list[i].nameCheck || { gr: "unconfirmed", en: "unconfirmed" };
      body += "\n/* " + list[i].key + (list[i].grName ? " (" + list[i].grName + ")" : "") +
        " | Names: GR " + _nc.gr + ", EN " + _nc.en + " */\n" +
        "window.nameExamplesCustom = Object.assign(window.nameExamplesCustom || {}, " +
        JSON.stringify(one, null, 2) + ");\n";
    }
    if (typeof fScenarioSaveBlobDownload === "function") {
      return !!fScenarioSaveBlobDownload(filename, new Blob([header + body], { type: "text/javascript" }));
    }
  } catch (eB) {
    try { console.warn("[draft] custom bundle download failed", eB); } catch (eL) {}
  }
  return false;
}

// Manual save-all (Ρυθμίσεις row, v54.25–26): downloads one bundle file for
// all session-new custom molecules (drawn/updated this session; untouched
// boot-loaded file customs are skipped — their files exist). Stored entries
// excluded. v54.26: single bundle instead of a per-file loop (stacked Save
// dialogs kept only the last file on ask-before-download browsers).

function fMolDraftMarkNewCustom(key) {
  try {
    if (!key) return;
    window._molDraftNewKeys = window._molDraftNewKeys || {};
    window._molDraftNewKeys[String(key)] = true;
  } catch (eM) {}
}

function fMolDraftNewCustomKeys() {
  try {
    var reg = (typeof window.nameExamplesCustom !== "undefined" && window.nameExamplesCustom) ? window.nameExamplesCustom : {};
    var marks = (typeof window._molDraftNewKeys !== "undefined" && window._molDraftNewKeys) ? window._molDraftNewKeys : {};
    return Object.keys(marks).filter(function (k) { return Object.prototype.hasOwnProperty.call(reg, k); });
  } catch (eK) { return []; }
}


function fRenderMolInfo() {
  var box = null;
  try { box = document.getElementById("moleculeInfo"); } catch (eB) { box = null; }
  if (!box) return;
  var open = false;
  try { open = !!molInfoOpenFlag; } catch (eF) { open = false; }
  var btn = null;
  try { btn = document.getElementById("molInfoBtn"); } catch (eBtn) { btn = null; }
  try {
    if (btn) {
      btn.classList.toggle("active", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }
    box.classList.toggle("open", open);
  } catch (eC) { /* best-effort */ }
  try { box.innerHTML = ""; } catch (eX) { return; }
  if (!open) return;
  var T = function (k, gr) {
    try { return (typeof fMulerT === "function") ? fMulerT(k) : gr; } catch (e) { return gr; }
  };
  var entry = null;
  try {
    entry = (typeof selectedMol !== "undefined" && selectedMol && typeof nameExamples !== "undefined")
      ? nameExamples[selectedMol] : null;
  } catch (eE) { entry = null; }
  if (!entry) {
    var hint = document.createElement("div");
    hint.className = "molInfoEmpty";
    hint.textContent = T("noMolHint", "Επιλέξτε μόριο για ανάλυση ονόματος");
    try { box.appendChild(hint); } catch (eA) { /* best-effort */ }
    return;
  }
  // Saved/reloaded provisional status travels with the record and remains
  // visible in the molecule information panel after the draft is torn down.
  if (entry.sdf3DStatus === "provisional") {
    var status3D = document.createElement("div");
    status3D.className = "molInfoRow";
    status3D.setAttribute("data-3d-status", "provisional");
    status3D.textContent = T("draft3DProvisional", "Provisional 3D — geometry and convergence unverified.");
    box.appendChild(status3D);
  }
  // SMILES row (cached SMILES, PubChem canonical preferred; always available
  // when a molecule is loaded). Canonical value links to the PubChem compound
  // page when we have a numeric CID.
  var cidNum = null;
  try {
    var _cid = entry.pubchemCID;
    if (_cid != null && /^\d+$/.test(String(_cid).trim())) cidNum = String(_cid).trim();
  } catch (eCid) { cidNum = null; }
  var smiShown = null;
  try { smiShown = entry.canonicalSmiles || entry.smiles || null; } catch (eS) { smiShown = null; }
  var r1 = document.createElement("div");
  r1.className = "molInfoRow";
  var l1 = document.createElement("span");
  l1.className = "molInfoLabel";
  l1.textContent = T("molInfoSmiles", "SMILES");
  var v1 = document.createElement("code");
  v1.className = "molInfoSmiles";
  if (smiShown) {
    if (cidNum) {
      var _as = document.createElement("a");
      _as.href = "https://pubchem.ncbi.nlm.nih.gov/compound/" + cidNum;
      _as.target = "_blank";
      try { _as.rel = "noopener noreferrer"; } catch (eR) {}
      _as.textContent = smiShown;
      try { _as.className = "molInfoLink"; } catch (eC2) {}
      v1.appendChild(_as);
    } else v1.textContent = smiShown;
  } else v1.textContent = "—";
  var cp = document.createElement("button");
  cp.type = "button";
  cp.className = "molInfoCopy";
  cp.setAttribute("data-tooltip", T("molInfoCopy", "Αντιγραφή SMILES"));
  cp.setAttribute("aria-label", T("molInfoCopy", "Αντιγραφή SMILES"));
  try { cp.innerHTML = (window.MuLERIcons && window.MuLERIcons.copy) || "⧉"; } catch (eI) { cp.textContent = "⧉"; }
  cp.onclick = function (ev) {
    try { if (ev && ev.preventDefault) ev.preventDefault(); } catch (eP) { /* best-effort */ }
    fCopyMolSmiles(cp);
  };
  r1.appendChild(l1);
  r1.appendChild(v1);
  r1.appendChild(cp);
  try { box.appendChild(r1); } catch (eB1) { /* best-effort */ }
  // IUPAC row (verbatim PubChem name; async fetch may still be pending).
  var r2 = document.createElement("div");
  r2.className = "molInfoRow";
  var l2 = document.createElement("span");
  l2.className = "molInfoLabel";
  l2.textContent = T("molInfoIupac", "IUPAC (PubChem)");
  var v2 = document.createElement("span");
  v2.className = "molInfoValue";
  var iupac = null;
  try { iupac = entry.iupacPubchem || null; } catch (eN) { iupac = null; }
  if (iupac) {
    if (cidNum) {
      var _ai = document.createElement("a");
      _ai.href = "https://pubchem.ncbi.nlm.nih.gov/compound/" + cidNum;
      _ai.target = "_blank";
      try { _ai.rel = "noopener noreferrer"; } catch (eR2) {}
      _ai.textContent = iupac;
      try { _ai.className = "molInfoLink"; } catch (eC3) {}
      v2.appendChild(_ai);
    } else v2.textContent = iupac;
  } else {
    var failed = false, done = false;
    try { failed = !!entry.iupacFetchError; done = !!entry.iupacFetchDone; } catch (eS) { /* best-effort */ }
    v2.textContent = (failed || done)
      ? T("molInfoMissing", "Χωρίς εγγραφή PubChem")
      : T("molInfoFetching", "Αναζήτηση…");
    try { v2.classList.add("molInfoPending"); } catch (eP2) { /* best-effort */ }
  }
  r2.appendChild(l2);
  r2.appendChild(v2);
  try { box.appendChild(r2); } catch (eB2) { /* best-effort */ }
  // Systematic row: PubChem-derived systematic name, shown only when our
  // computed name differs from the IUPAC name (stereo-insensitive) and the
  // candidate passes the locant-shaped PIN test. PubChem has no authoritative
  // systematic field, so heuristic synonyms never reach the UI — and a bogus
  // pool pick stays hidden whenever engine and oracle agree.
  try {
    var _sys = entry.systematicEN || null;
    var _eng = null;
    try { _eng = entry.engineEN || null; } catch (eE2) { _eng = null; }
    if (_sys && _eng && iupac) {
      var _norm = function (s) {
        try { if (typeof fNormNoStereo === "function") return fNormNoStereo(String(s)); } catch (eN) {}
        return String(s == null ? "" : s).toLowerCase().trim();
      };
      var _okShape = false;
      try { _okShape = (typeof fIsSystematicName === "function") ? !!fIsSystematicName(_sys) : false; } catch (eS2) { _okShape = false; }
      if (_okShape && _norm(_eng) !== _norm(iupac) && _norm(_sys) !== _norm(v2.textContent)) {
        var r3 = document.createElement("div");
        r3.className = "molInfoRow";
        var l3 = document.createElement("span");
        l3.className = "molInfoLabel";
        l3.textContent = T("molInfoSystematic", "Systematic (PubChem)");
        var v3 = document.createElement("span");
        v3.className = "molInfoValue";
        v3.textContent = _sys;
        r3.appendChild(l3);
        r3.appendChild(v3);
        try { box.appendChild(r3); } catch (eB3) { /* best-effort */ }
      }
    }
  } catch (eSys) { /* best-effort */ }
  // OpenClatura row (second oracle, rule-built systematic EN): verbatim name
  // with the OPSIN round-trip status in parens. Display only — never feeds
  // validation or naming (Phase 2 decides that). Pending/failed states mirror
  // the PubChem row above; fetch fires from the select path (fLogMolSelectWithOC).
  try {
    var _oc = null, _ocOpsin = null, _ocDone = false, _ocErr = false, _ocSmi = null;
    try {
      _oc = entry.openclaturaEN || null;
      _ocOpsin = entry.openclaturaOpsin || null;
      _ocDone = !!entry.openclaturaDone;
      _ocErr = !!entry.openclaturaErr;
      _ocSmi = entry.canonicalSmiles || entry.smiles || null;
    } catch (eO) { /* best-effort */ }
    if (_oc || _ocDone || _ocSmi) {
    var rOC = document.createElement("div");
    rOC.className = "molInfoRow";
    var lOC = document.createElement("span");
    lOC.className = "molInfoLabel";
    lOC.textContent = T("molInfoOpenclatura", "IUPAC (OpenClatura)");
    var vOC = document.createElement("span");
    vOC.className = "molInfoValue";
    if (_oc) {
      // OPSIN status shows only when unmatched (matched = quiet confidence;
      // mismatched/unparseable/error/skipped_* each mean something for review).
      vOC.textContent = _oc + ((_ocOpsin && _ocOpsin !== "matched") ? " (OPSIN: " + _ocOpsin + ")" : "");
    } else {
      vOC.textContent = (_ocDone && _ocErr)
        ? T("molInfoOCError", "OpenClatura lookup failed (network)")
        : (_ocDone
          ? T("molInfoOCMissing", "No OpenClatura answer")
          : T("molInfoFetching", "Αναζήτηση…"));
      try { vOC.classList.add("molInfoPending"); } catch (eP3) { /* best-effort */ }
    }
    rOC.appendChild(lOC);
    rOC.appendChild(vOC);
    try { box.appendChild(rOC); } catch (eBOC) { /* best-effort */ }
    }
  } catch (eOC) { /* best-effort */ }
  // Common-name row (ethers only): the verbatim PubChem Title, and only if
  // it actually looks like a common ether name (ends in "ether").
  // Systematic "...oxy..." titles are skipped, never translated or locally
  // reconstructed — this row reports PubChem data as-is.
  try {
    var _isEth = false;
    try { _isEth = !!(entry && entry.classification && entry.classification.chemicalClass === "ethers"); } catch (eC2) { _isEth = false; }
    if (_isEth) {
      var _common = null;
      var _norm2 = function (s) { return String(s == null ? "" : s).toLowerCase().trim(); };
      var _row2 = "";
      try { _row2 = v2.textContent || ""; } catch (eR2) { _row2 = ""; }
      try {
        var _tit = entry.titlePubchem || null;
        if (_tit && /ether$/i.test(String(_tit).trim()) && _norm2(_tit) !== _norm2(_row2)) _common = _tit;
      } catch (eT2) { /* best-effort */ }
      if (_common && _norm2(_common) !== _norm2(v2.textContent)) {
        var r4 = document.createElement("div");
        r4.className = "molInfoRow";
        var l4 = document.createElement("span");
        l4.className = "molInfoLabel";
        l4.textContent = T("molInfoCommon", "Common name");
        var v4 = document.createElement("span");
        v4.className = "molInfoValue";
        v4.textContent = _common;
        r4.appendChild(l4);
        r4.appendChild(v4);
        try { box.appendChild(r4); } catch (eB4) { /* best-effort */ }
      }
    }
  } catch (eCN) { /* best-effort */ }
  // The panel sits above the name boxes: re-pin the floating Explain sheet.
  try { if (typeof fNameExpandRepinDelayed === "function") fNameExpandRepinDelayed(); } catch (eR2) { /* best-effort */ }
}


test('all syntax compiles',function(){new Function(readFile('/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate/js/mulermoc-nom-molview-55.js'));});
test('CV55-04 same heavy count different elements rejected',function(){reset();var wrong=mol([atom('C',0,0),atom('N',1,0,1),atom('O',2,1,0)],[[1,2,1],[2,3,1]]);assert(!fMolDraftValidSDF3D(wrong,3,fixture()),'wrong graph accepted');});
test('CV55-04 order-independent graph accepted; globals restored',function(){reset();var saved=[allAtomsTypeList,bondList,allAtomsTypeList3D,bondList3D];var reordered=mol([atom('O',2,0,1),atom('C',0,0),atom('C',1,0)],[[2,3,1],[3,1,1]]);var ref=mol([atom('C',0,0),atom('C',1,0),atom('O',2,0)],[[1,2,1],[2,3,1]]);assert(fMolDraftValidSDF3D(reordered,3,ref),'reorder rejected');assert(saved[0]===allAtomsTypeList&&saved[1]===bondList&&saved[2]===allAtomsTypeList3D&&saved[3]===bondList3D,'global leak');});
test('CV55-04 bond-order charge isotope topology mismatches rejected',function(){reset();var ref=fixture();for(var kind of ['order','charge','isotope','element']){var p=fParseMolV2000(ref);if(kind==='order')p.bonds[0][2]=2;if(kind==='charge')p.atoms[0].charge=1;if(kind==='isotope')p.atoms[0].isotope=13;if(kind==='element')p.atoms[0].el='N';var m=fWriteMolV2000(p.head,p.atoms,p.bonds,p);assert(!fMolDraftValidSDF3D(m,3,ref),'accepted '+kind);}var branched=mol([atom('C',0,0),atom('C',1,0),atom('C',2,0),atom('C',1,1)],[[1,2,1],[2,3,1],[2,4,1]]);var linear=mol([atom('C',0,0),atom('C',1,0),atom('C',2,0),atom('C',3,0)],[[1,2,1],[2,3,1],[3,4,1]]);assert(!fMolDraftValidSDF3D(branched,4,linear),'topology mismatch accepted');});
test('CV55-06 methane planar and rotated structures accepted',function(){reset();var methane=mol([atom('C',0,0)],[]);assert(fMolDraftValidSDF3D(methane,1,methane),'methane rejected');var planar=fixture();assert(fMolDraftValidSDF3D(planar,3,planar),'planar rejected');var rotated=mol([atom('C',0,0),atom('C',0,0,1),atom('C',0,0,2)],[[1,2,1],[2,3,1]]);assert(fMolDraftValidSDF3D(rotated,3,planar),'orientation rejected');});
test('collapsed bonds and unsupported query/isotopic H fail closed',function(){reset();var bad=mol([atom('C',0,0),atom('C',0,0),atom('C',1,0)],[[1,2,1],[2,3,1]]);assert(!fMolDraftValidSDF3D(bad,3,fixture()),'collapsed accepted');var query=mol([atom('*',0,0)],[]);assert(!fMolDraftValidSDF3D(query,1,query),'query accepted');var isoH=mol([atom('C',0,0),atom('H',1,0,0,{isotope:2})],[[1,2,1]]);assert(!fMolDraftValidSDF3D(isoH,1,isoH),'isotopic H unsupported but accepted');});
test('PubChem tier rejects identity mismatch and accepts exact graph',function(){reset();var originalRemote=fMolDraftRemote3DFromJSmol,originalLocal=fMolDraftLocal3DFromMol;fMolDraftRemote3DFromJSmol=function(){return null;};fMolDraftLocal3DFromMol=async function(){return {sdf:null};};fFetchSDF3D_PubChem=async function(){return mol([atom('N',0,0),atom('C',1,0),atom('O',2,0,1)],[[1,2,1],[2,3,1]]);};assert(!settle(fMolDraftFetchSDF3DTiered('CCC',fixture(),3,function(){return true;})).sdf,'wrong tier1 graph accepted');fFetchSDF3D_PubChem=async function(){return fixture();};assert(settle(fMolDraftFetchSDF3DTiered('CCC',fixture(),3,function(){return true;})).source==='pubchem','correct pubchem missed');fMolDraftRemote3DFromJSmol=originalRemote;fMolDraftLocal3DFromMol=originalLocal;});
test('Remote tier reads exact graph and rejects wrong graph',function(){reset();var j=fMolDraft3DBegin();assert(fMolDraftRemote3DFromJSmol('CCC',3,j),'valid remote missed');_model=mol([atom('C',0,0),atom('N',1,0),atom('O',2,0,1)],[[1,2,1],[2,3,1]]);assert(!fMolDraftRemote3DFromJSmol('CCC',3,j),'wrong remote accepted');});
test('VV55-01 replacement during MMFF wait prevents readback/UFF',function(){reset();var job=fMolDraft3DBegin();var promise=fMolDraftLocal3DRelaxBoth(3,job);drainMicrotasks();assert(_writes.some(function(c){return /MMFF/.test(c);}), 'MMFF never started');fJSmolScript(jmolAppletNomeclature,'load "replacement.sdf";');var writes=_writes.length,reads=_reads.length;settle(promise);assert(_writes.length===writes&&_reads.length===reads,'stale continuation touched replacement');assert(!_writes.some(function(c){return /UFF/.test(c);}), 'UFF started after replacement');assert(_writes.some(function(c){return /minimize stop/i.test(c);}), 'prior minimizer not stopped');});
for(var field of ['draft','epoch','submitId','smiles','molText','selection','mode','applet','cancel'])test('currentness abort inside round: '+field,function(){reset();var job=fMolDraft3DBegin();var p=fMolDraftLocal3DRelaxBoth(3,job);drainMicrotasks();if(field==='draft')window.MulerDraft=Object.assign({},window.MulerDraft);if(field==='epoch')window.MulerDraft._epoch++;if(field==='submitId')window.MulerDraft._submitId++;if(field==='smiles')window.MulerDraft.smiles='CC';if(field==='molText')window.MulerDraft.molText+='\n';if(field==='selection')selectedMol='other';if(field==='mode')mode2D='expanded';if(field==='applet')jmolAppletNomeclature={id:'other'};if(field==='cancel')window.MulerDraft.cancelRequested=true;var writes=_writes.length,reads=_reads.length;settle(p);assert(_writes.length===writes&&_reads.length===reads,'stale '+field+' touched applet');jmolAppletNomeclature={id:'applet'};});
test('local preparation validates generated graph and both bounded rounds',function(){reset();navigator.onLine=false;var job=fMolDraft3DBegin();var result=settle(fMolDraftLocal3DFromMol(fixture(),3,false,job));assert(result.prepared&&result.sdf,'local result missing');assert(fMolDraftValidSDF3D(result.sdf,3,fixture()),'local result identity changed');assert(_writes.filter(function(c){return /minimize steps/.test(c);}).length===2,'expected MMFF+UFF attempts');assert(!result.geometryVerified&&!result.convergenceVerified,'invented convergence');});
test('source metadata distinguishes source-provided and provisional',function(){reset();var d=window.MulerDraft;assert(fMolDraftSet3D(d,fixture(),'pubchem',null),'pubchem rejected');assert(d.sdf3DStatus==='source-provided'&&!d.sdf3DProvenance.convergenceVerified,'wrong source status');fMolDraftSet3D(d,fixture(),'jsmol-min',null);assert(d.sdf3DStatus==='provisional'&&!d.sdf3DProvenance.geometryVerified&&!d.sdf3DProvenance.convergenceVerified,'wrong local status');});
function prepareUpdate(variant,provisional){reset();var d=window.MulerDraft;d.mode='edit';d.variant=variant;d.same=true;d.sourceIsCustom=true;d.sourceMol='fixture';nameExamples.fixture={key:'fixture',structure2D_Condensed:'C-original',structure2D_Expanded:'E-original',structure2D_Skeletal:'S-original'};nameExamplesCustom.fixture=nameExamples.fixture;fMolDraftSet3D(d,fixture(),provisional?'jsmol-min':'pubchem',null);return d;}
for(var variant of ['condensed','expanded','skeletal'])test('same identity '+variant+' updates one slot, siblings byte unchanged',function(){prepareUpdate(variant,false);var r=nameExamples.fixture;settle(fMolDraftAccept());assert(window.MulerDraft===null,'not accepted');var expected=variant==='condensed'?'structure2D_Condensed':variant==='expanded'?'structure2D_Expanded':'structure2D_Skeletal';for(var pair of [['structure2D_Condensed','C-original'],['structure2D_Expanded','E-original'],['structure2D_Skeletal','S-original']])assert(pair[0]===expected?r[pair[0]]!==pair[1]:r[pair[0]]===pair[1],'wrong slot mutation '+pair[0]);assert(r.history[0].action==='updated-slot:'+variant,'slot history absent');});
test('provisional acceptance needs explicit exact-conformation confirmation',function(){var d=prepareUpdate('condensed',true);settle(fMolDraftAccept());assert(_confirm&&window.MulerDraft===d,'accepted without consent');assert(nameExamples.fixture.structure2D_Condensed==='C-original','mutated before consent');_confirm.cb();drainMicrotasks();while(_timers.length)nextTimer();assert(window.MulerDraft===null,'confirmed accept did not finish');var r=nameExamples.fixture;assert(r.sdf3DStatus==='provisional'&&r.sdf3DProvenance.confirmation==='accept'&&r.sdf3DProvenance.confirmedAt,'consent provenance missing');});
test('stale provisional confirmation cannot accept replaced draft',function(){var d=prepareUpdate('condensed',true);settle(fMolDraftAccept());var cb=_confirm.cb;window.MulerDraft=Object.assign({},d);cb();drainMicrotasks();assert(nameExamples.fixture.structure2D_Condensed==='C-original','stale callback mutated source');});
test('Edit-different confirms fork and leaves source unchanged',function(){var d=prepareUpdate('expanded',false);d.same=false;var before=JSON.stringify(nameExamples.fixture);settle(fMolDraftAccept());assert(_confirm,'no fork confirmation');_confirm.cb();drainMicrotasks();while(_timers.length)nextTimer();assert(JSON.stringify(nameExamples.fixture)===before,'fork changed original');var r=nameExamples.custom_new;assert(r&&r.structure2D_Condensed&&r.structure2D_Expanded&&r.structure2D_Skeletal,'fork missing generated slots');});
test('New derives all three forms canonically',function(){reset();var d=window.MulerDraft;fMolDraftSet3D(d,fixture(),'pubchem',null);settle(fMolDraftAccept());var r=nameExamples.custom_new;assert(r&&r.structure2D_Condensed&&r.structure2D_Expanded&&r.structure2D_Skeletal,'new slot gap');var p=fParseMolV2000(r.structure2D_Expanded);assert(p.atoms.length>3,'expanded H missing');});
test('manual provisional retry uses wait window; Escape retains old SDF',function(){reset();var d=window.MulerDraft;fMolDraftSet3D(d,fixture(),'jsmol-unminimized',null);var prior=d.sdf3D;var p=fMolDraftManualMinimize();drainMicrotasks();assert(fMolDraftMinWaitEl&&fMolDraftMinWaitKey,'retry did not reach wait UI');fMolDraftMinWaitKey({key:'Escape',preventDefault:function(){},stopPropagation:function(){}});settle(p);assert(d.sdf3D===prior&&!d._minimizing,'Escape saved a new result');assert(_writes.filter(function(c){return /minimize STOP/i.test(c);}).length===1,'cancel STOP count');});
test('manual preview remains provisional; Accept owns the single confirmation',function(){reset();var d=window.MulerDraft;settle(fMolDraftManualMinimize());assert(d.sdf3DStatus==='provisional'&&!d.sdf3DProvenance.confirmation&&!d.sdf3DProvenance.convergenceVerified,'manual preview falsely confirmed');assert(!_confirm,'manual opened duplicate save confirm');assert(!_writes.some(function(c){return /minimize STOP/i.test(c);}), 'normal completion sent STOP');settle(fMolDraftAccept());assert(_confirm&&window.MulerDraft===d,'Accept omitted explicit confirmation');});
test('stale wait Cancel cannot STOP replacement model',function(){reset();var d=window.MulerDraft;var p=fMolDraftManualMinimize();drainMicrotasks();var oldKey=fMolDraftMinWaitKey;fJSmolScript(jmolAppletNomeclature,'load "replacement";');var writes=_writes.length;oldKey({key:'Escape',preventDefault:function(){},stopPropagation:function(){}});settle(p);assert(_writes.length===writes,'stale Cancel wrote STOP on replacement');assert(!d.sdf3D,'stale manual preview stored');});
test('single and bundle exports retain provisional fields on reload',function(){reset();var d=window.MulerDraft;fMolDraftSet3D(d,fixture(),'jsmol-min','manual');var r=Object.assign({key:'fixture',grName:'προπάνιο',nameCheck:{gr:'correct',en:'unconfirmed'}},d);assert(fMolDraftDownloadSingle(r),'single export failed');assert(fMolDraftDownloadBundle([r]),'bundle export failed');for(var out of _downloads){var scope={};new Function('window',out.text)(scope);var reloaded=scope.nameExamplesCustom.fixture;assert(reloaded.sdf3DStatus==='provisional'&&reloaded.sdf3DProvenance.confirmation==='manual'&&!reloaded.sdf3DProvenance.geometryVerified,'export lost status');}});
test('saved provisional model info remains visible after draft teardown',function(){reset();nameExamples.fixture={key:'fixture',sdf3DStatus:'provisional',smiles:'CCC'};window.MulerDraft=null;var box=element();_docElements.moleculeInfo=box;fRenderMolInfo();assert(box.children.some(function(n){return n['data-3d-status']==='provisional'&&/unverified/.test(n.textContent);}), 'persistent status absent');});
function depictApplet(prior,output,delay) {
  return { value:prior,scale:3.125,reads:0,imports:0,restored:0,depicting:false,
    molFile:function(){if(this.depicting&&this.reads++<(delay||0))return 'stub V2000';return this.value;},
    getMolecularAreaScale:function(){return this.scale;},setMolecularAreaScale:function(v){this.scale=v;},
    clear:function(){this.value='';this.depicting=false;},
    readGenericMolecularInput:function(){this.imports++;this.depicting=true;this.value=output;this.scale=9;},
    readMolFile:function(m){this.value=m;this.depicting=false;this.restored++;},
    deferredRepaint:function(){},repaint:function(){}
  };
}
function zigzag(){return mol([atom('C',0,0),atom('C',1,0.5),atom('C',2,0)],[[1,2,1],[2,3,1]]);}
test('bounded async display acquisition restores actual applet MOL and scale',function(){prepareUpdate('skeletal',false);var app=depictApplet('prior actual display',zigzag(),2);jsmeNomeclatureApplet=app;settle(fMolDraftAccept());assert(app.imports===1&&app.restored===1&&app.value==='prior actual display'&&app.scale===3.125,'applet not restored');assert(nameExamples.fixture.structure2D_Skeletal===zigzag(),'delayed valid rung missed');});
test('wrong graph rung cannot win; later exact edit rung succeeds',function(){prepareUpdate('skeletal',false);var wrong=mol([atom('C',0,0),atom('N',1,0.5),atom('O',2,0)],[[1,2,1],[2,3,1]]);var app1=depictApplet('prior display',wrong,0),app2=depictApplet('prior edit',zigzag(),0);jsmeNomeclatureApplet=app1;jsmeEditDraftApplet=app2;settle(fMolDraftAccept());assert(nameExamples.fixture.structure2D_Skeletal===zigzag(),'unsafe rung won or fallback skipped');assert(app1.restored===1&&app2.restored===1,'not both restored');});
test('layout rotation/translation/scale echo falls through to later rung',function(){prepareUpdate('skeletal',false);var echo=mol([atom('C',8,2),atom('C',8,4),atom('C',8,6)],[[1,2,1],[2,3,1]]);jsmeNomeclatureApplet=depictApplet('prior',echo,0);jsmeEditDraftApplet=depictApplet('prior edit',zigzag(),0);settle(fMolDraftAccept());assert(nameExamples.fixture.structure2D_Skeletal===zigzag(),'echo accepted as new geometry');});
test('exhausted 2D polling is bounded and uses built-in fallback',function(){prepareUpdate('skeletal',false);var app=depictApplet('prior',zigzag(),99);jsmeNomeclatureApplet=app;settle(fMolDraftAccept());assert(app.reads===6&&app.imports===1&&app.restored===1,'poll/import bound violated');assert(fParseMolV2000(nameExamples.fixture.structure2D_Skeletal),'fallback invalid');});
test('Cancel during acquisition defers teardown until applet restoration',function(){var d=prepareUpdate('skeletal',false);var app=depictApplet('actual previous',zigzag(),99);jsmeNomeclatureApplet=app;var p=fMolDraftAccept();drainMicrotasks();assert(window.MulerDraftAcquisition===d,'not acquired');fMolDraftCancel();assert(window.MulerDraft===d&&d.cancelRequested,'Cancel not deferred');settle(p);assert(window.MulerDraft===null&&app.value==='actual previous'&&app.scale===3.125&&app.restored===1,'cancel restoration failed');assert(nameExamples.fixture.structure2D_Skeletal==='S-original','cancel stored new molecule');});
test('selection replacement during acquisition prevents stale restoration/write',function(){prepareUpdate('skeletal',false);var app=depictApplet('actual previous',zigzag(),99);jsmeNomeclatureApplet=app;var p=fMolDraftAccept();drainMicrotasks();selectedMol='other';app.value='new selected drawing';settle(p);assert(app.value==='new selected drawing'&&app.restored===0,'stale restoration overwrote replacement');assert(nameExamples.fixture.structure2D_Skeletal==='S-original','stale acquisition stored');});
test('import exception after clear restores captured content and scale',function(){prepareUpdate('skeletal',false);var app=depictApplet('actual previous',zigzag(),0);app.readGenericMolecularInput=function(){this.scale=99;throw Error('import failed');};jsmeNomeclatureApplet=app;settle(fMolDraftAccept());assert(app.restored===1&&app.value==='actual previous'&&app.scale===3.125,'exception restoration failed');});
test('ordinary added H supported; detached and excess H rejected',function(){reset();var expanded=fGenExpandedMol(fixture());assert(fMolDraftValidSDF3D(expanded,3,fixture()),'ordinary added H rejected');var isolated=mol([atom('C',0,0),atom('H',2,0)],[]);var methane=mol([atom('C',0,0)],[]);assert(!fMolDraftValidSDF3D(isolated,1,methane),'isolated H accepted');var over=mol([atom('C',0,0),atom('H',1,0),atom('H',0,1),atom('H',-1,0),atom('H',0,-1),atom('H',0,0,1)],[[1,2,1],[1,3,1],[1,4,1],[1,5,1],[1,6,1]]);assert(!fMolDraftValidSDF3D(over,1,methane),'CH5 accepted');});
test('inline SDF data cannot terminate the Jmol DATA wrapper',function(){reset();var count=_writes.length;assert(!fJSmolLoadInlineSDF(jmolAppletNomeclature,'end "model.sdf"\n'+fixture(),''),'terminator accepted');assert(_writes.length===count,'malformed data issued script');});
test('size-based wait is 10..120 seconds and countdown sends no applet traffic',function(){reset();assert(fMolDraftMinWaitSecs(3)===10&&fMolDraftMinWaitSecs(40)===20&&fMolDraftMinWaitSecs(300)===120,'wait scaling mismatch');var job=fMolDraft3DBegin();fMolDraftMinWaitShow(function(){},20,job);var writes=_writes.length,reads=_reads.length;assert(/20s/.test(fMolDraftMinWaitEl.querySelector('.scConfirmMsg').textContent),'countdown absent');_intervals[_intervals.length-1].fn();assert(_writes.length===writes&&_reads.length===reads,'countdown touched applet');fMolDraftMinWaitClose(job);});
test('further 200-step round reloads previous SDF and retains stationary valid geometry',function(){reset();var d=window.MulerDraft;var previous=zigzag();fMolDraftSet3D(d,previous,'jsmol-min',null);settle(fMolDraftManualMinimize());assert(d.sdf3D===previous&&d.sdf3DStatus==='provisional','further did not retain conformation');assert(_writes.some(function(c){return /minimize steps 200/.test(c);}), 'further budget not 200');assert(!_writes.some(function(c){return /minimize steps 500|minimize STOP/i.test(c);}), 'further ran fresh/STOP');assert(_writes.filter(function(c){return /minimize steps/.test(c);}).length===1,'stationary further result needlessly fell back');assert(!d.sdf3DProvenance.confirmation,'further preview inherited consent');});
test('idle minimizer STOP helper performs no applet writes',function(){reset();var job=fMolDraft3DBegin();fMolDraftMinStopEngine(job);assert(!_writes.length,'idle STOP poisoned next load');});
test('later settings registry synchronizes independent controls despite one failure',function(){reset();var count=0;var original=MULER_VIEWER_SETTINGS;MULER_VIEWER_SETTINGS=[{sync:function(){count++;throw Error('one row');}},{sync:function(){count++;}}];fSyncViewerSettingsUI();assert(count===2,'registry stopped on failed row');MULER_VIEWER_SETTINGS=original;});
for(var halogen of ['F','Cl','Br','I'])test('CV55-11 '+halogen+' anion rejects added hydrogen',function(){reset();var reference=mol([atom(halogen,0,0,0,{charge:-1})],[]);var addedH=mol([atom(halogen,0,0,0,{charge:-1}),atom('H',1,0)],[[1,2,1]]);assert(!fMolDraftValidSDF3D(addedH,1,reference),'added H accepted on '+halogen+' anion');});
for(var halogen of ['F','Cl','Br','I'])test('CV55-11 unchanged '+halogen+' anion stays accepted',function(){reset();var reference=mol([atom(halogen,0,0,0,{charge:-1})],[]);assert(fMolDraftValidSDF3D(reference,1,reference),'unchanged '+halogen+' anion rejected');});
test('CV55-11 neutral HF remains accepted with implicit-to-explicit H',function(){reset();var reference=mol([atom('F',0,0)],[]);var hf=mol([atom('F',0,0),atom('H',1,0)],[[1,2,1]]);assert(fMolDraftValidSDF3D(hf,1,reference),'neutral HF rejected');});
test('CV55-11 unsupported charged valences fail closed',function(){reset();for(var config of [['N',2],['O',-2],['F',1],['S',-1],['P',1],['C',2]]){var m=mol([atom(config[0],0,0,0,{charge:config[1]})],[]);assert(!fMolDraftValidSDF3D(m,1,m),'unsupported charge accepted '+config);}});
print(JSON.stringify({cases:results.length,passed:results.filter(function(r){return r.pass;}).length,results:results}));
if(results.some(function(r){return !r.pass;}))quit(1);
