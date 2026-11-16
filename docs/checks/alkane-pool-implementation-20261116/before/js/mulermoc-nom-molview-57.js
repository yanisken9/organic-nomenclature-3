// mulermoc-nom-molview-57.js
// Molecule viewer layer — JSME (2D), JSmol (3D), native SVG DOM, jQuery.
// Reads analysis results from mulermoc-nom-core-57.js globals.
// Provides all display, highlighting, naming-panel, and save functions.

// ── Viewer / display globals ──────────────────────────────────────────────
let selectedMol;
let jsmeNomeclatureApplet;
let jsmeNomeclatureAppletORGNL;
// Dedicated draft editor (v54 Stage 2): pure edit mode by construction —
// runtime options() cannot flip depict/edit, so the display applet stays
// depict-only and drafts get their own full-edit instance.
let jsmeEditDraftApplet;
let atomSymbols3DFlag = true;
let hydrogens3DFlag = true;
let rotateFlag = false;
let svgAtomColors2DFlag = false;
let atomColorMode2D = "atom";
let mode2D = "condensed";
let modeSuffix = "_2D_Condensed";
// 2D zoom state: JSME molecular-area scale. Default 2.0 = the long-standing
// hardcoded load value, so behavior is identical until the user zooms.
// fInitProps resets it on every molecule load (mode switches keep zoom);
// fLoadMol2D re-applies it on every load. Scenario steps capture it in
// style2D.zoom (legacy default 2.0) and re-assert it after the step load.
const MOL_ZOOM_DEFAULT = 2.0;
const MOL_ZOOM_MIN = 0.5;
const MOL_ZOOM_MAX = 6.0;
let molZoom2D = MOL_ZOOM_DEFAULT;
// Single-viewer max-height (v48): default "full" (live viewport share); null
// = Auto (cap at the both-visible height, so toggling one viewer off never
// resizes the survivor); a number is an absolute px cap. Applied only when
// exactly one viewer is visible, in fViewerHeights2D3D. Set by the Ρυθμίσεις
// control and per scenario step (show.viewerMaxHeight); scenario owns
// persistence, this is the live value.
let viewerMaxH = "full";
// Double-viewer height (v48): default "full" (live viewport fill for both);
// null = Auto (the equal split both viewers get today); a number is the
// COMBINED 2D+3D height when two viewers are visible — each viewer takes half.
// Applied only when exactly two viewers are visible, in fViewerHeights2D3D.
// Set by the Ρυθμίσεις control and per scenario step (show.viewerBothHeight);
// scenario owns persistence, this is the live value.
let viewerBothH = "full";
// Manual double-viewer slider bounds (v48): the combined 2D+3D height is a
// fixed 300–1000px range regardless of the live single-viewer ceiling.
const VIEWER_BOTH_MIN = 300;
const VIEWER_BOTH_MAX = 1000;
// Manual single-viewer slider bounds (v52): a fixed 150–1000px range. The old
// screen-derived ceiling (live full height, taller on tall displays) is gone
// — predictable authoring on any screen; taller needs the "full" sentinel,
// which resolves live per playback screen instead of storing px.
const VIEWER_SINGLE_MAX = 1000;
// Sanity ceiling for stored single-viewer heights (show.viewerMaxHeight): the
// live slider ceiling is screen-derived and can exceed 1000 on tall displays,
// so scenario validation must not silently rewrite those values. Values applied
// live are still clamped to the real single-viewer share (fViewerHeights2D3D).
const VIEWER_MAX_H = 2000;
// Shared viewer min-height floor (v48): a single 150px minimum for BOTH
// viewers, so a long present note card can never squash them to an unusable
// size (the page scrolls instead). Mirrored by the CSS min-heights
// (.JmolContainer / #jsmeNomeclatureSVG) via the `--viewerMinH` custom
// property, which is set from this constant just below so the two can never
// drift; the CSS value is only a no-JS fallback.
const VIEWER_MIN_H = 150;
try {
  document.documentElement.style.setProperty("--viewerMinH", VIEWER_MIN_H + "px");
} catch (eMinH) { /* CSS custom property unavailable */ }
// B2 owned-shared viewer state: current MOL strings (fDeselectMol/fLoadMol2D).
let myMol2D = null;
let myMol3D = null;
let molSvg;
// Display-only geometry: never replace a library record or a 3D source.
let skeletalLayoutSource = null;
let skeletalLayoutApplied = null;

// ── MuSVG: minimal native SVG DOM helper (replaces the former SVG library) ──
const MuSVG = (function () {
  const SVG_NS = "http://www.w3.org/2000/svg";

  class SvgElement {
    constructor(node) {
      this.node = node;
    }

    select(selector) {
      return wrap(this.node.querySelector(selector));
    }

    selectAll(selector) {
      return Array.prototype.map.call(
        this.node.querySelectorAll(selector),
        function (node) { return wrap(node); },
      );
    }

    attr(name, value) {
      if (name && typeof name === "object") {
        for (const key in name) {
          this.attr(key, name[key]);
        }
        return this;
      }
      if (arguments.length > 1) {
        if (name === "text") {
          this.node.textContent = value;
        } else {
          this.node.setAttribute(name, value);
        }
        return this;
      }
      if (name === "text") {
        return this.node.textContent;
      }
      return this.node.getAttribute(name);
    }

    remove() {
      if (this.node && this.node.parentNode) {
        this.node.parentNode.removeChild(this.node);
      }
      return this;
    }

    append(child) {
      const node = child && child.node ? child.node : child;
      if (node) {
        this.node.appendChild(node);
      }
      return this;
    }

    toString() {
      if (this.node.nodeType === 1) {
        return this.node.outerHTML;
      }
      if (this.node.childNodes) {
        return Array.prototype.map.call(
          this.node.childNodes,
          function (node) {
            return node.nodeType === 1 ? node.outerHTML : (node.textContent || "");
          },
        ).join("");
      }
      return String(this.node);
    }
  }

  function wrap(node) {
    return node ? new SvgElement(node) : null;
  }

  function MuSVG(target) {
    if (typeof target === "string") {
      return wrap(document.querySelector(target));
    }
    return wrap(target);
  }

  MuSVG.parse = function (markup) {
    if (!markup) {
      return null;
    }
    try {
      const doc = new DOMParser().parseFromString(
        '<svg xmlns="' + SVG_NS + '">' + markup + "</svg>",
        "text/html",
      );
      const svg = doc.querySelector("svg");
      if (!svg) {
        return null;
      }
      const fragment = document.createDocumentFragment();
      while (svg.firstChild) {
        fragment.appendChild(document.adoptNode(svg.firstChild));
      }
      return wrap(fragment);
    } catch (e) {
      return null;
    }
  };

  return MuSVG;
})();

let highAtoms;
let nameAnalysisMode;
let myNumberingTimeout;
let numberingFlag = false;
let numbersSVGElements = [];
let currNumberEl = 0;
let namingRules; // owned-shared: assigned once by teaching fInitTheory, read by fShowRule
let ruleFlag = false;
let ruleTableHighlight = null;
let ruleTableFlag = false;
let vis3D = "ballnstick";
let JmolSelection = "select none";
let selectedRule;
let nameSettingsFlag = true;
let narrateAnalysisFlag = false;
// Molecule info panel (SMILES + PubChem IUPAC): live-only toggle, never
// stored in steps. Content refreshes on every naming rebuild and in place
// when a pending PubChem fetch resolves (fMulerMolInfoRefresh).
let molInfoOpenFlag = false;
if (typeof window.nameBoxFlag === "undefined") window.nameBoxFlag = true;
if (typeof window.nameCrossFlag === "undefined") window.nameCrossFlag = false;
// Single source: all code reads/writes window.* directly (no local aliases,
// which desynced after toggles since primitives copy by value)
// Per-component name visibility (eye toggles): window.nameHiddenComps holds
// the hidden comp ids (e.g. ["comp5"]); window.nameEyeEdit is the live-only
// authoring edit mode (never stored in steps).
if (typeof window.nameHiddenComps === "undefined") window.nameHiddenComps = [];
if (typeof window.nameEyeEdit === "undefined") window.nameEyeEdit = false;
let mainChainMode = "algorithmic"; // 'data' | 'algorithmic'
let etherNamingMode = "iupac"; // 'iupac' | 'common' — ether naming variant toggle
let substNamingMode = "school"; // 'school' | 'sys' — traditional (school retained) vs systematic substituent names (EN). Mode ids stay 'school'/'sys' for saved-scenario compatibility; only the labels changed to Traditional/Systematic.
let compactNumberingLabelMap = {};
const compactReverseOffsetScale = {
  HOOC: 0.8,
  OHC: 0.8,
};
const compactForwardOffsetScale = {
  HCOOH: 0.55,
  HCHO: 0.55,
};
const compactLabelWidths = {
  COOH: 900,
  HOOC: 900,
  HCOOH: 1000,
  HCHO: 850,
  CHO: 650,
  OHC: 650,
  CN: 520,
  NC: 520,
  NO2: 760,
  O2N: 760,
};

const compactRectRightEdgeAdjust = {
  OHC: 34,
};

const atomColors2D = {
  Cl: "#10e510",
  Br: "#a62929",
  S: "#FFC832",
  O: "#FF0D0D",
  N: "#3050F8",
  H: "#909090",
  C: "#222222",
};

// ── SVG icon aliases (single source: js/ui-icons.js) ────────────────────────
// ui-icons.js loads first (see mulermoc-nom-46.html); these lexical aliases
// keep every use site below unchanged. Guarded so a missing icon file degrades
// to empty buttons instead of breaking the module. Note: `playSm` is the
// 22-viewBox narration triangle, distinct from the 512-viewBox scenario `play`.
const svgSettings = (window.MuLERIcons && window.MuLERIcons.settings) || "";
const svgSpeaker = (window.MuLERIcons && window.MuLERIcons.speaker) || "";
const svgMute = (window.MuLERIcons && window.MuLERIcons.mute) || "";
const svgStop = (window.MuLERIcons && window.MuLERIcons.stop) || "";
const svgPlay = (window.MuLERIcons && window.MuLERIcons.playSm) || "";
const svgAudioDesc = (window.MuLERIcons && window.MuLERIcons.audioDescription) || "";
const svgNameBox = (window.MuLERIcons && window.MuLERIcons.nameBox) || "";
const svgNameBoxOff = (window.MuLERIcons && window.MuLERIcons.nameBoxOff) || "";
const svgNameCross = (window.MuLERIcons && window.MuLERIcons.nameCross) || "";
const svgNameCrossOff = (window.MuLERIcons && window.MuLERIcons.nameCrossOff) || "";
const svgEye = (window.MuLERIcons && window.MuLERIcons.eye) || "";
const svgEyeOff = (window.MuLERIcons && window.MuLERIcons.eyeOff) || "";
const svgEyeState = (window.MuLERIcons && window.MuLERIcons.eyeState) || "";
const svgNameExplainAll = (window.MuLERIcons && window.MuLERIcons.list) || "";
const svgNameExpand = (window.MuLERIcons && window.MuLERIcons.nameExpand) || "";
const svgMolInfo = (window.MuLERIcons && window.MuLERIcons.info) || "";
const svgEditMol = (window.MuLERIcons && window.MuLERIcons.editMolecule) || "";
const svgNewMol = (window.MuLERIcons && window.MuLERIcons.newMolecule) || "";
const svgSaveMol = (window.MuLERIcons && window.MuLERIcons.saveMolecule) || "";
const svgSelectAtoms = (window.MuLERIcons && window.MuLERIcons.selectAtoms) || "";

// Per-component name visibility helpers (eye toggles). Masking is applied at
// box-construction time in fShowNameAnalysis so every rebuild (mode switch,
// free-browse, scenario apply) honors the live hidden set automatically.
function fNameCompHidden(id) {
  try {
    var h = window.nameHiddenComps;
    return Array.isArray(h) && h.indexOf(id) >= 0;
  } catch (e) {
    return false;
  }
}

// Eye buttons show while the authoring master switch is on. In presentation
// the master switch stays functional whenever the step exposes the naming
// settings gear (show.nameSettings): it is seeded from show.nameEye on step
// entry and toggles the eyes live. Without the gear, eyes follow
// show.nameEye directly.
function fNameEyeVisible() {
  var _inPresent = false;
  try {
    _inPresent = (typeof MuLERMoCScenario !== "undefined" && MuLERMoCScenario.present === true);
  } catch (e) {
    /* scenario absent */
  }
  if (_inPresent) {
    try {
      if (typeof fScenarioPresent === "function") {
        var p = fScenarioPresent();
        var st = p && p.steps ? p.steps[p.index] : null;
        if (st && st.show && st.show.nameSettings === true) return window.nameEyeEdit === true;
        return !!(st && st.show && st.show.nameEye === true);
      }
    } catch (e) {
      /* scenario unavailable */
    }
    return false;
  }
  return window.nameEyeEdit === true;
}

// Wrapped name-component box: eye row above, box below. The eye row keeps
// a fixed-height slot whether eyes are shown or not, so every wrap has the
// same height and the outside "+" separators align uniformly (see CSS).
// Hidden boxes render
// a dash on a lightBlue fill (CSS .comp-hidden); the full text lives only in
// memory (never persisted). Euphony connectors stay as computed for the full
// name — neighbors of a dash box keep their connector letter.
function fNameCompBox(boxId, boxClass, displayComp, tipHtml) {
  var hidden = fNameCompHidden(boxId);
  var cls = boxClass + (hidden ? " comp-hidden" : "");
  var tip = (typeof tipHtml === "string" && tipHtml) ? tipHtml : null;
  if (tip) cls += " sysDiff";
  // Display-only italic prefixes (IUPAC detached sec-/tert-): raw slot text,
  // ids, tooltips and matching stay untouched (see fMulerItalicSecTert).
  var body = hidden ? "–" : displayComp;
  try { if (!hidden && typeof fMulerItalicSecTert === "function") body = fMulerItalicSecTert(displayComp); } catch (eI) {}
  var eye = "";
  if (fNameEyeVisible()) {
    eye = "<button class='compEye" + (hidden ? " off-state" : "") + "' data-comp='" + boxId + "' data-tooltip='" + (hidden ? ((typeof fMulerT === "function") ? fMulerT("showComp") : "Εμφάνιση συνθετικού") : ((typeof fMulerT === "function") ? fMulerT("hideComp") : "Απόκρυψη συνθετικού")) + "'>" + (hidden ? svgEyeOff : svgEye) + "</button>";
  }
  return "<div class='nameCompWrap'><div class='nameCompEyeRow'>" + eye + "</div><div class='" + cls + "' id='" + boxId + "'" + (tip ? " title='" + tip + "'" : "") + ">" + body + "</div></div>";
}

fInitViewerSettingsBtn();
fInitViewerMaxHeight();
fInitViewerBothHeight();

// ── jsmeOnLoad ────────────────────────────────────────────────────────────
// Main applet stays in depict mode: 2D highlights are read back from
// getMolecularAreaGraphicsString(), which needs the depiction pipeline.
// Drafts use the dedicated full-edit jsmeEditDraft applet below (runtime
// options() cannot flip depict/edit — only construction options can).

function jsmeOnLoad() {
  jsmeNomeclatureApplet = new JSApplet.JSME(
    "jsmeNomeclature",
    "590px",
    "240px",
    {
      options: "depict, marker, toggle, noreaction,nomultipart,noquery","guicolor": "#c8d9ec",  "guiAtomColor": "#1b275d",
      depictbg: "#fff",
      atombgsize: "0.6",
    },
  );
  jsmeNomeclatureApplet.setAtomMolecularAreaFontSize(9);
  jsmeNomeclatureApplet.setMolecularAreaLineWidth(0.6);

  let bgAtom = [
    "#7ddfff",
    "#7ddfff", // palette slot 2: v56 user-selection cyan (JSME slots are 1-based — slot N is bgAtom[N-1]; slot 9 green stays)
    "#00ffff",
    "#ffcc66",
    "#ffff00",
    "#f74f4f", // palette slot 6 (reserved: quiz-wrong red, unused for now)
    "#33ccff",
    "#ff99ff",
    "#D8EEDC",
    "#ff8566",
    "#66ff66",
    "#93bfff",
  ];
  jsmeNomeclatureApplet.setBackGroundColorPalette(bgAtom);
  try { if (typeof fMulerSelectWrapBgChannel === "function") fMulerSelectWrapBgChannel(); } catch (eSelWrap) {}

  carbonHydrogens = Array(jsmeNomeclatureApplet.totalNumberOfAtoms()).fill(0);

  // Dedicated draft editor (v54 Stage 2): constructed in pure edit mode (no
  // depict, no toggle — runtime options() cannot flip modes, proven). Visible
  // only during molecule drafts; the display applet above stays depict-only.
  // Guarded so a draft-only failure can never abort boot.
  try {
    jsmeEditDraftApplet = new JSApplet.JSME(
      "jsmeEditDraft",
      "590px",
      "240px",
      {
        options: "marker, norbutton, noxbutton, atommovebutton, noreaction,nomultipart,noquery","guicolor": "#c8d9ec",  "guiAtomColor": "#1b275d",
        depictbg: "#fff",
        atombgsize: "0.6",
      },
    );
    try { jsmeEditDraftApplet.setAtomMolecularAreaFontSize(9); } catch (eF2) {}
    try { jsmeEditDraftApplet.setMolecularAreaLineWidth(0.6); } catch (eL2) {}
    try { jsmeEditDraftApplet.setBackGroundColorPalette(bgAtom); } catch (eP2) {}
  } catch (eDraft) {
    try { /* console.warn("[draft] edit applet unavailable", eDraft); */ } catch (eL3) {}
    try { jsmeEditDraftApplet = null; } catch (eN) {}
  }

  // ORGNL retired 2026-11-02 (v54 Stage 1): single-applet depict+toggle.
  // Restore if a dedicated full-edit applet is ever needed again.
  // jsmeNomeclatureAppletORGNL = new JSApplet.JSME(
  //   "jsmeNomeclatureORGNL",
  //   "590px",
  //   "240px",
  //   {
  //     options: "marker, norbutton, noxbutton, atommovebutton, autonumber,   ",  "guicolor": "#c8d9ec",  "guiAtomColor": "#1b275d", 
  //     depictbg: "#fff",
  //     atombgsize: "0.6",
  //     
  //   },
  // );
  // jsmeNomeclatureAppletORGNL.setAtomMolecularAreaFontSize(9);
  // jsmeNomeclatureAppletORGNL.setMolecularAreaLineWidth(0.6);

  // // let bgAtom = ["#7ddfff", "#ffc37d", "#00ffff", "#ffcc66", "#ffff00", "#ff9999", "#33ccff", "#ff99ff", "#79dc6d", "#ff8566", "#66ff66", "#93bfff"];
  // jsmeNomeclatureAppletORGNL.setBackGroundColorPalette(bgAtom);

  fInitData();
  // Naming tables must exist before any fGuessName call below: teaching's
  // $(document).ready also runs fInitNamingProps, but jsmeOnLoad can win the
  // race on a cold boot (then fGuessName throws on the empty tables and the
  // whole select aborts after the 2D paint). Idempotent pure assignments.
  try { if (typeof fInitNamingProps === "function") fInitNamingProps(); } catch (eNp) { /* best-effort */ }
  fClassifyAllMolecules();
  fInitNomeclatureMenu();

  // carbonHydrogens = Array(jsmeNomeclatureAppletORGNL.totalNumberOfAtoms())

  // Methane on startup (JSmol viewport workaround): a cold boot with no
  // molecule ever loaded leaves the applet without a valid viewport, so a
  // 2D-only scenario step 1 (load-then-zap+hide as its first lifecycle)
  // corrupts all later 3D. One visible startup load primes it. Direct
  // fSelectMol (not synthesized clicks: teaching-layer handlers may not be
  // bound yet when JSME fires jsmeOnLoad). No menu marking and no group
  // auto-open: the landing menu stays clean (no selection, groups closed);
  // the header trigger-click used here before also deselected the molecule
  // and zapped the just-primed 3D.
  try {
    if (typeof nameExamples !== "undefined" && nameExamples.methane) {
      selectedMol = "methane";
      fSelectMol();
    }
  } catch (e) {
    /* startup selection best-effort */
  }

  // Fluid 2D: one initial fit to the real column width (constructor 590px is
  // the known-good first paint), then the debounced observer owns resizes.
  try { fResizeViewers(); } catch (eFit) { /* fit best-effort */ }
  try { fInitZoomObserver2D(); } catch (eObs) { /* observer best-effort */ }
}

function fClassifyAllMolecules() {
  // v54 Stage 2: merge accepted custom drafts (custom .js payload, loaded by
  // mulermoc-nom-54.html when the file exists next to the data file).
  // Missing file -> the script tag 404s and this block no-ops.
  try {
    if (typeof nameExamplesCustom !== "undefined" && nameExamplesCustom) {
      for (var _ck in nameExamplesCustom) {
        if (Object.prototype.hasOwnProperty.call(nameExamplesCustom, _ck) && !nameExamples[_ck]) {
          nameExamples[_ck] = nameExamplesCustom[_ck];
        }
      }
    }
  } catch (eCust) {}
  const previousMol = selectedMol;
  // Snapshot live analysis globals: the loop recomputes them per molecule,
  // so restore afterwards instead of leaving the last molecule's state behind
  const _coreSnapshot = {
    atomsCount, bondsCount, allAtomsTypeList, atomTypes, atomTypeObj,
    atomConnectivityList, atomValenceList, bondList, multiBondListCC,
    multiBondsObj, svgBondList, functionalGroupObj, molType, molTaxonomy,
    carbons, carbonHydrogens: carbonHydrogens.slice(),
  };

  try {
    for (const prop of Object.keys(nameExamples)) {
      const structure = nameExamples[prop].structure2D_Condensed;
      if (!structure) continue;

      jsmeNomeclatureApplet.readMolFile(structure);
      fAnalyseStructure();
      fDetectMolType();
      nameExamples[prop].classification = fGetMoleculeClassification();
      // Canonical SMILES per molecule (storage-only for now; future use as a
      // molecule id in logging/search/display). Condensed source matches the
      // historical title-line convention; in-memory conversion on the already
      // loaded structure, so no extra loop or perf cost. Miss → null, never
      // a boot failure.
      try {
        var _smiles = null;
        if (typeof jsmeNomeclatureApplet.getSmiles === "function") {
          _smiles = jsmeNomeclatureApplet.getSmiles();
        } else if (typeof jsmeNomeclatureApplet.smiles === "function") {
          _smiles = jsmeNomeclatureApplet.smiles();
        }
        nameExamples[prop].smiles = _smiles || null;
      } catch (eSmiles) {
        nameExamples[prop].smiles = null;
      }
    }
  } finally {
    // Direct rebinding: these are `let` globals (not globalThis props),
    // so restore each binding instead of Object.assign on globalThis
    atomsCount = _coreSnapshot.atomsCount;
    bondsCount = _coreSnapshot.bondsCount;
    allAtomsTypeList = _coreSnapshot.allAtomsTypeList;
    atomTypes = _coreSnapshot.atomTypes;
    atomTypeObj = _coreSnapshot.atomTypeObj;
    atomConnectivityList = _coreSnapshot.atomConnectivityList;
    atomValenceList = _coreSnapshot.atomValenceList;
    bondList = _coreSnapshot.bondList;
    multiBondListCC = _coreSnapshot.multiBondListCC;
    multiBondsObj = _coreSnapshot.multiBondsObj;
    svgBondList = _coreSnapshot.svgBondList;
    functionalGroupObj = _coreSnapshot.functionalGroupObj;
    molType = _coreSnapshot.molType;
    molTaxonomy = _coreSnapshot.molTaxonomy;
    carbons = _coreSnapshot.carbons;
    carbonHydrogens = _coreSnapshot.carbonHydrogens;
  }

  selectedMol = previousMol;
  if (previousMol && nameExamples[previousMol]?.structure2D_Condensed) {
    jsmeNomeclatureApplet.readMolFile(nameExamples[previousMol].structure2D_Condensed);
  } else {
    jsmeNomeclatureApplet.reset();
  }
}

//

// ── fToggleViewerSettings ────────────────────────────────────────────────

// Title-bar buttons: 2D / 3D visibility toggles into #viewerVisBtns (far left,
// bold text, same .active contract as the gear) + draft entries + save-all +
// gear into #viewerSettingsBtnDiv.
// Uses existing `svgSettings` constant and the fToggleViewerSettings() handler.
function fInitViewerSettingsBtn() {
  const markup = `<button id='selectAtomsBtn' class='settingsBtn hide' onclick='fToggleAtomSelect()' data-tooltip='` + ((typeof fMulerT === "function") ? fMulerT("selectAtoms") : "Επιλογή ατόμων/δεσμών") + `'>${svgSelectAtoms}</button><button id='editMolBtn' class='settingsBtn hide' onclick='fEditMolDraft()' data-tooltip='` + ((typeof fMulerT === "function") ? fMulerT("editMol") : "Επεξεργασία μορίου") + `'>${svgEditMol}</button><button id='newMolBtn' class='settingsBtn hide' onclick='fNewMolDraft()' data-tooltip='` + ((typeof fMulerT === "function") ? fMulerT("newMol") : "Νέο μόριο") + `'>${svgNewMol}</button><button id='saveMolBtn' class='settingsBtn hide btnInactive' onclick='fMolDraftSaveAllCustom()' data-tooltip='` + ((typeof fMulerT === "function") ? fMulerT("saveNewMols") : "Save new molecules") + `'>${svgSaveMol}</button><button id='viewerSettingsBtn' class='settingsBtn' onclick='fToggleViewerSettings()' data-tooltip='` + ((typeof fMulerT === "function") ? fMulerT("settings") : "Ρυθμίσεις") + `'>${svgSettings}</button>`;
  const visMarkup = `<button id='view2DBtn' class='settingsBtn visBtn active' onclick='fToggleViewer2D()' data-tooltip='` + ((typeof fMulerT === "function") ? fMulerT("show2D") : "Εμφάνιση 2D") + `'>2D</button><button id='view3DBtn' class='settingsBtn visBtn active' onclick='fToggleViewer3D()' data-tooltip='` + ((typeof fMulerT === "function") ? fMulerT("show3D") : "Εμφάνιση 3D") + `'>3D</button>`;
  function insert() {
    try {
      const div = document.getElementById("viewerSettingsBtnDiv");
      if (div && !document.getElementById("viewerSettingsBtn")) {
        div.innerHTML = markup;
      }
      const bar = document.getElementById("viewerVisBtns");
      if (bar && !document.getElementById("view2DBtn")) {
        bar.insertAdjacentHTML("afterbegin", visMarkup);
      }
      // Static HTML icon placeholders (e.g. save-image buttons) hydrate here
      // from the js/ui-icons.js registry — single source, no <img> files.
      document.querySelectorAll("[data-icon]").forEach(function (el) {
        const key = el.getAttribute("data-icon");
        const icon = window.MuLERIcons && window.MuLERIcons[key];
        if (icon && !el.innerHTML) el.innerHTML = icon;
      });
      try { if (typeof fMolDraftSyncButtons === "function") fMolDraftSyncButtons(); } catch (eDs) { /* boot state best-effort */ }
    } catch (e) {
      // defensive - don't throw in init
      // console.warn("viewerSettings init failed", e);
    }
  }
  insert();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", insert);
  } else {
    // ensure insertion if scripts run after DOM ready
    setTimeout(insert, 0);
  }
}

// Title-bar 2D visibility toggle. Same .active contract as fToggleViewerSettings.
// Scope mirrors the (commented-out) viewFinalJSME checkbox: SVG + 2D mode radios.
function fToggleViewer2D() {
  var btn = document.getElementById("view2DBtn");
  var show = btn && btn.classList.contains("active");
  if (show) {
    if (btn) btn.classList.remove("active");
    $("#jsmeNomeclatureSVG").slideUp(200);
    $("#radio2DMode").addClass("hide");
  } else {
    if (btn) btn.classList.add("active");
    $("#jsmeNomeclatureSVG").slideDown(200);
    $("#radio2DMode").removeClass("hide");
  }
  // Auto readouts depend on which viewers are visible; resync once the
  // 200 ms show/hide animation has settled (the panel may be open).
  setTimeout(fViewerHeightControlsSync, 220);
}

// Title-bar 3D visibility toggle. Scope mirrors the (commented-out) viewJSmol
// checkbox: 3D applet + 3D controls, with JSmol refresh on re-show.
function fToggleViewer3D() {
  var btn = document.getElementById("view3DBtn");
  var show = btn && btn.classList.contains("active");
  if (show) {
    if (btn) btn.classList.remove("active");
    $("#nomeclature3D").slideUp(200);
    $("#controls3D").addClass("hide");
  } else {
    if (btn) btn.classList.add("active");
    $("#nomeclature3D").slideDown(200, function () {
      // Re-sync the applet viewport first: after display:none the cached
      // size stays tiny and refresh/center/zoom/load all render into it
      // (tiny molecule, upper-left; only write IMAGE looks right).
      try {
        var _ap = document.getElementById("nomeclature3D");
        var _w = (_ap && _ap.clientWidth) || 480;
        var _h = (_ap && _ap.clientHeight) || 240;
        if (typeof Jmol !== "undefined" && Jmol.resizeApplet &&
            typeof jmolAppletNomeclature !== "undefined") {
          fJSmolResizeApplet(jmolAppletNomeclature, { width: _w, height: _h });
        }
      } catch (eSize) {
        /* measure best-effort */
      }
      // One-shot reload after a no-3D presentation exit (flag set by
      // fScenarioExitPresent; the exit zapped the applet). Ordinary toggles
      // keep no model change and stay refresh-only/instant.
      var once = false;
      try {
        once = (typeof MuLERMoCScenario !== "undefined" &&
          MuLERMoCScenario.reload3DOnce === true);
        if (typeof MuLERMoCScenario !== "undefined") MuLERMoCScenario.reload3DOnce = false;
      } catch (eFlag) {
        once = false;
      }
      if (once) {
        try {
          if (typeof selectedMol !== "undefined" && selectedMol &&
              typeof nameExamples !== "undefined" && nameExamples[selectedMol]) {
            fLoadMol3D();
            if (typeof showAtomSymbols3D === "function") showAtomSymbols3D();
            if (typeof showHydrogens3D === "function") showHydrogens3D();
            if (typeof rotate3D === "function") rotate3D();
          }
        } catch (eLoad) {
          /* fall through to refresh */
        }
        // Delayed refresh: the SDF load above is async, so an immediate
        // refresh fires before the model lands. Re-render once settled.
        setTimeout(function () {
          try {
            fJSmolScript(jmolAppletNomeclature, "refresh");
          } catch (eLate) {
            /* 3D unavailable */
          }
        }, 600);
        return;
      }
      fJSmolScript(jmolAppletNomeclature, "refresh");
    });
    $("#controls3D").removeClass("hide");
  }
  setTimeout(fViewerHeightControlsSync, 220);
}

// Shared resync for the two viewer-height rows (panel may be open while a
// title-bar eye toggle hides/shows a viewer).
function fViewerHeightControlsSync() {
  try { fViewerMaxHeightSync(); } catch (eS) { /* slider sync best-effort */ }
  try { fViewerBothHeightSync(); } catch (eS2) { /* slider sync best-effort */ }
}

// Viewer-settings registry (v55.x): one entry per panel row that mirrors a
// JS global (checkboxes whose truth lives only in DOM classes — originalJSME,
// autoLinearize, bondAtoms, numberingAtoms/Bonds — are captured/applied
// directly at their call sites and are intentionally NOT here; scenario
// stash/restore + capture read them from the DOM). Translation is data-lang
// on each label. Add a row: HTML label with data-lang + one entry here;
// order is display-independent.
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

function fToggleViewerSettings() {
  var panel = document.getElementById("viewerSettingsPanel");
  var btn = document.getElementById("viewerSettingsBtn");
  var isOpen = panel.classList.contains("open");
  if (isOpen) {
    panel.classList.remove("open");
    btn.classList.remove("active");
  } else {
    panel.classList.add("open");
    btn.classList.add("active");
    try { fSyncViewerSettingsUI(); } catch (eS) { /* settings sync best-effort */ }
  }
}

// ── molecule draft session (v54 Stage 2, Step 2) ───────────────────────────
// Single draft session shared by Edit (template) and New (blank).
// selectedMol is never touched: Cancel restores by re-render (fSelectMol),
// the same known-good path as the cold-boot resend. Submit (engine + PubChem)
// arrives in Step 3; the Submit button below is a stub until then.
window.MulerDraft = window.MulerDraft || null;
// Depiction owns the applets until restoration. Cancel waits for that finally
// block; a replacement draft never receives the previous applet content.
window.MulerDraftAcquisition = window.MulerDraftAcquisition || null;

function fMolDraftT(key, fallback) {
  try {
    if (typeof fMulerT === "function") {
      var s = fMulerT(key);
      if (s && s !== key) return s;
    }
  } catch (eT) {}
  return fallback;
}

function fMolDraftToast(msg) {
  try {
    if (typeof fScenarioToast === "function") { fScenarioToast(msg); return; }
  } catch (eT) {}
  try { alert(msg); } catch (eA) {}
}

function fMolDraftPresenting() {
  try {
    return !!(typeof MuLERMoCScenario !== "undefined" && MuLERMoCScenario.present);
  } catch (eP) { return false; }
}

// Stored MOL for the currently displayed 2D variant (edit-selected
// representation: condensed/expanded/skeletal; zigzag shares Skeletal).
function fMolDraftVariantMol() {
  try {
    if (typeof selectedMol === "undefined" || !selectedMol) return null;
    if (typeof nameExamples === "undefined" || !nameExamples[selectedMol]) return null;
    var ex = nameExamples[selectedMol];
    var m = (typeof mode2D !== "undefined") ? mode2D : "condensed";
    if (m === "expanded" && ex.structure2D_Expanded) return ex.structure2D_Expanded;
    if ((m === "skeletal" || m === "condensedZigZag") && ex.structure2D_Skeletal) return ex.structure2D_Skeletal;
    if (ex.structure2D_Condensed) return ex.structure2D_Condensed;
    if (ex.structure2D_Expanded) return ex.structure2D_Expanded;
    if (ex.structure2D_Skeletal) return ex.structure2D_Skeletal;
  } catch (eM) {}
  return null;
}

function fMolDraftBarEl() {
  var bar = null;
  try { bar = document.getElementById("molDraftBar"); } catch (eG) { bar = null; }
  if (bar) return bar;
  var host = null;
  try { host = document.getElementById("radio2DMode"); } catch (eH) { host = null; }
  if (!host || !host.parentNode) return null;
  bar = document.createElement("div");
  bar.id = "molDraftBar";
  bar.className = "hide";
  host.parentNode.insertBefore(bar, host.nextSibling);
  return bar;
}

function fMolDraftShowBar(statusText) {
  var bar = fMolDraftBarEl();
  if (!bar) return;
  var tS = fMolDraftT("draftSubmit", "Submit");
  var tAKey = "draftAccept";
  try { if (window.MulerDraft && window.MulerDraft.acceptKey) tAKey = window.MulerDraft.acceptKey; } catch (eAk) {}
  var tA = fMolDraftT(tAKey, tAKey === "draftUpdate" ? "Update" : "Accept");
  var tD = fMolDraftT("draftDraw", "Draw");
  var tB = fMolDraftT("draftBeautify", "Beautify");
  var tC = fMolDraftT("draftCancel", "Cancel");
  bar.innerHTML = "<span id='molDraftStatus'></span>" +
    "<button id='molDraftSubmitBtn' type='button' class='settingsBtn draftBtn' onclick='fMolDraftSubmit()'>" + fMolDraftEsc(tS) + "</button>" +
    "<button id='molDraftAcceptBtn' type='button' class='settingsBtn draftBtn' onclick='fMolDraftAccept()'>" + fMolDraftEsc(tA) + "</button>" +
    "<button id='molDraftDrawBtn' type='button' class='settingsBtn draftBtn hide' onclick='fMolDraftBackToEdit()'>" + fMolDraftEsc(tD) + "</button>" +
    "<button id='molDraftBeautifyBtn' type='button' class='settingsBtn draftBtn hide' onclick='fMolDraftBeautify()'>" + fMolDraftEsc(tB) + "</button>" +
    "<button id='molDraftCancelBtn' type='button' class='settingsBtn draftBtn' onclick='fMolDraftCancel()'>" + fMolDraftEsc(tC) + "</button>";
  try {
    var st = document.getElementById("molDraftStatus");
    if (st) st.textContent = statusText || "";
    var bs = document.getElementById("molDraftSubmitBtn");
    if (bs) bs.setAttribute("data-tooltip", tS);
    var ba = document.getElementById("molDraftAcceptBtn");
    if (ba) ba.setAttribute("data-tooltip", tA);
    var bd = document.getElementById("molDraftDrawBtn");
    if (bd) bd.setAttribute("data-tooltip", tD);
    var bb = document.getElementById("molDraftBeautifyBtn");
    if (bb) bb.setAttribute("data-tooltip", tB);
    var bc = document.getElementById("molDraftCancelBtn");
    if (bc) bc.setAttribute("data-tooltip", tC);
  } catch (eT) {}
  bar.classList.remove("hide");
  try { fMolDraftSyncBar(); } catch (eSy) {}
}

function fMolDraftHideBar() {
  try {
    var bar = document.getElementById("molDraftBar");
    if (bar) bar.classList.add("hide");
  } catch (eH) {}
}

// Draft bar state machine (v54 Stage 2, v55 tiers): Submit dims once a fresh,
// 3D-backed preview is up (it returns via Draw), and both dim while
// submitting. The editor-visible clause is the strand guard: the preview
// view hides the canvas, so every drawable state goes through Draw, which
// re-lights Submit — no reliance on the live JSME stale callback (name
// unverified against the bundled build). Accept lights only on a fresh
// preview with 3D from ANY tier (PubChem/Cactus/local) — no PubChem-record
// requirement (v55: novel molecules carry sdf3D with null pubchem); stale
// never lights it, and edit mode never lights it (Accept acts
// on the preview). Draw is visible from the first Submit and lit only in
// preview view — a no-op while the canvas is already up. Beautify (school
// linear layout) is offered only for school-geometry drafts (condensed,
// expanded, new): the skeletal slot already has its JSME zigzag beautifier.
function fMolDraftSyncBar() {
  try {
    var d = window.MulerDraft;
    var bs = document.getElementById("molDraftSubmitBtn");
    var ba = document.getElementById("molDraftAcceptBtn");
    if (!bs || !ba || !d) return;
    var editorVisible = false;
    try { editorVisible = !document.getElementById("jsmeEditDraft").classList.contains("hide"); } catch (eV) {}
    var submitActive = false, acceptActive = false;
    var acquiring = !!window.MulerDraftAcquisition;
    if (!d.submitting && !d._minimizing && !acquiring) {
      if (!d.submitted || d.stale || editorVisible) submitActive = true;
      if (d.submitted && !d.stale && d.sdf3D && !editorVisible) acceptActive = true;
    }
    if (submitActive) { bs.classList.add("active"); bs.classList.remove("btnInactive"); }
    else { bs.classList.remove("active"); bs.classList.add("btnInactive"); }
    if (acceptActive) { ba.classList.add("active"); ba.classList.remove("btnInactive"); }
    else { ba.classList.remove("active"); ba.classList.add("btnInactive"); }
    var bw = document.getElementById("molDraftDrawBtn");
    if (bw) {
      if (d.submitted) {
        bw.classList.remove("hide");
        if (!acquiring && !editorVisible) { bw.classList.add("active"); bw.classList.remove("btnInactive"); }
        else { bw.classList.remove("active"); bw.classList.add("btnInactive"); }
      }
      else bw.classList.add("hide");
    }
    // Auto mode owns school linearization; manual mode offers the same
    // shared operation only while the school editor is visible.
    var bb2 = document.getElementById("molDraftBeautifyBtn");
    if (bb2) {
      var schoolDraft = true;
      try { schoolDraft = !(d.mode === "edit" && (d.variant === "skeletal" || d.variant === "condensedZigZag")); } catch (eSd) {}
      var autoOn = true;
      try { autoOn = fMolDraftAutoLinearizeOn(); } catch (eAu) {}
      if (!schoolDraft || autoOn || !editorVisible) { bb2.classList.add("hide"); }
      else {
        bb2.classList.remove("hide");
        if (!d.submitting && !d._minimizing && !acquiring) { bb2.classList.add("active"); bb2.classList.remove("btnInactive"); }
        else { bb2.classList.remove("active"); bb2.classList.add("btnInactive"); }
      }
    }
    [bs, ba, bw, bb2].forEach(function (button) {
      if (button) button.disabled = acquiring;
    });
  } catch (eS) {}
}

// Draft view flips (v54 Stage 2): the editor and the depict (SVG) view take
// turns — Enter/Cancel/Submit/Draw all route through these two helpers.
function fMolDraftShowEditor() {
  try { $("#jsmeEditDraft").removeClass("hide"); } catch (eA) {}
  try { $("#jsmeNomeclatureSVG").addClass("hide"); } catch (eS) {}
  try { $("#radio2DMode").addClass("hide"); } catch (eR) {}
  try {
    if (typeof jsmeEditDraftApplet !== "undefined" && jsmeEditDraftApplet &&
        typeof jsmeEditDraftApplet.deferredRepaint === "function") jsmeEditDraftApplet.deferredRepaint();
  } catch (eRp) {}
  try { if (typeof fResizeViewers === "function") fResizeViewers(); } catch (eR2) {}
}

function fMolDraftShowPreviewView() {
  try { $("#jsmeEditDraft").addClass("hide"); } catch (eA) {}
  try { $("#jsmeNomeclature").addClass("hide"); } catch (eM) {}
  try { $("#jsmeNomeclatureSVG").removeClass("hide"); } catch (eS) {}
  try { if (typeof fResizeViewers === "function") fResizeViewers(); } catch (eR2) {}
}

function fMolDraftBackToEdit() {
  if (!window.MulerDraft || window.MulerDraftAcquisition || fMolDraftPresenting()) return;
  fMolDraft3DInvalidate();
  window.MulerDraft._submitId = (window.MulerDraft._submitId || 0) + 1;
  window.MulerDraft.submitting = false;
  // Like Edit entry: 3D away (hide, not zap — viewport fragility), then the
  // editor view, so the refit below measures the settled layout.
  try {
    var _b3 = document.getElementById("view3DBtn");
    if (_b3 && _b3.classList.contains("active") && typeof fToggleViewer3D === "function") fToggleViewer3D();
  } catch (e3) {}
  fMolDraftShowEditor();
  // Authoritative stale check on returning to the canvas: if the drawing
  // differs from the submitted preview (live callbacks are best-effort and
  // may never fire), mark stale now so Submit re-lights with the right
  // status. The Accept-time SMILES re-check remains the final authority.
  try {
    var d = window.MulerDraft;
    if (d && d.submitted && !d.submitting) {
      var cur = fMolDraftReadDrawing();
      var curSmi = fMolDraftNorm((cur && cur.smiles) || "");
      if (curSmi && curSmi !== fMolDraftNorm(d.smiles || "")) {
        d.stale = true;
        try {
          var st = document.getElementById("molDraftStatus");
          if (st) st.textContent = fMolDraftT("acceptStale", "Drawing changed — press Submit again.");
        } catch (eSt) {}
        try { fMolDraftSyncBar(); } catch (eSy) {}
      }
    }
  } catch (eC) {}
  // View-driven Submit state: the editor is visible again, so Submit
  // re-lights via the sync even when the drawing is unchanged.
  try { fMolDraftSyncBar(); } catch (eSy2) {}
}

// Explicit school-geometry beautifier (pre-Accept): linearizes the canvas
// drawing (collinear main chain + orthogonal branches) and writes it back.
// Sandbox engine pass first so the chain is fresh; geometry is data for the
// stored MOLs, so a submitted preview is always marked stale (resubmit
// recaptures; d.molText is refreshed too, so even the Accept-time self-heal
// path keeps the tidied geometry). School slots only — skeletal drafts keep
// their JSME zigzag (button hidden there).
// Auto-tidy core (Submit auto-linearize + manual Linearize button share it):
// reads the canvas, runs the sandbox engine pass for a fresh chain,
// linearizes school geometry (expanded: heavy skeleton + regenerated H),
// writes back to the edit applet and re-reads. Skeletal drafts pass through
// untouched (zigzag path owns that slot). Returns {molText, smiles} or null
// (toast already shown). Never touches view state or the draft bar — callers
// own those (Submit continues its flow; Beautify flips view + marks stale).
function fMolDraftAutoTidy() {
  var d = window.MulerDraft;
  if (!d || fMolDraftPresenting()) return null;
  if (d.submitting || window.MulerDraftAcquisition) return null;
  if (typeof jsmeEditDraftApplet === "undefined" || !jsmeEditDraftApplet) return null;
  var drawing = null;
  try { drawing = fMolDraftReadDrawing(); } catch (eR) { drawing = null; }
  if (!drawing || !drawing.hasAny) {
    fMolDraftToast(fMolDraftT("submitEmpty", "Empty drawing — draw something first."));
    return null;
  }
  if (d.mode === "edit" && (d.variant === "skeletal" || d.variant === "condensedZigZag")) {
    return { molText: drawing.molText, smiles: drawing.smiles };
  }
  var savedMode = null;
  try { savedMode = (typeof mainChainMode !== "undefined") ? mainChainMode : null; } catch (eM0) {}
  var _sb = { ok: false, ring: false };
  try { _sb = fMolDraftSandboxAnalyse(drawing.molText) || _sb; } catch (eSb) {}
  try { if (savedMode != null) mainChainMode = savedMode; } catch (eRm0) {}
  try { if (typeof fUpdateChainModeButton === "function") fUpdateChainModeButton(); } catch (eBc0) {}
  if (!_sb.ok) {
    fMolDraftToast(fMolDraftT(_sb.ring ? "submitRing" : "submitEngineFail", _sb.ring ? "Rings are out of scope — acyclic structures only." : "Engine failed — check the drawing."));
    return null;
  }
  var chainNow = null;
  try { chainNow = (typeof mainChainAtomsList !== "undefined") ? mainChainAtomsList : null; } catch (eCh) {}
  var lin = null;
  try { if (typeof fLinearizeMol === "function") lin = fLinearizeMol(drawing.molText, chainNow); } catch (eL) { lin = null; }
  if (!lin) {
    fMolDraftToast(fMolDraftT("submitEngineFail", "Engine failed — check the drawing."));
    return null;
  }
  var outMol = lin;
  try {
    var _dv = (d.mode === "edit") ? d.variant : "condensed";
    if (_dv === "expanded" && typeof fGenExpandedMol === "function") {
      var _ex = fGenExpandedMol(lin) || null;
      if (_ex) outMol = _ex;
    }
  } catch (eE) {}
  try { jsmeEditDraftApplet.readMolFile(outMol); } catch (eW) {
    fMolDraftToast(fMolDraftT("submitEngineFail", "Engine failed — check the drawing."));
    return null;
  }
  var fresh = null;
  try { fresh = fMolDraftReadDrawing(); } catch (eR2) { fresh = null; }
  if (!fresh || !fresh.molText) {
    fMolDraftToast(fMolDraftT("submitEngineFail", "Engine failed — check the drawing."));
    return null;
  }
  return { molText: fresh.molText, smiles: fresh.smiles };
}

function fMolDraftBeautify() {
  var d = window.MulerDraft;
  if (!d || fMolDraftPresenting()) return;
  if (d.submitting || window.MulerDraftAcquisition) return;
  if (d.mode === "edit" && (d.variant === "skeletal" || d.variant === "condensedZigZag")) return;
  if (typeof jsmeEditDraftApplet === "undefined" || !jsmeEditDraftApplet) return;
  var _td = null;
  try { _td = fMolDraftAutoTidy(); } catch (eT) { _td = null; }
  if (!_td) return;
  try {
    var _b3 = document.getElementById("view3DBtn");
    if (_b3 && _b3.classList.contains("active") && typeof fToggleViewer3D === "function") fToggleViewer3D();
  } catch (e3) {}
  fMolDraftShowEditor();
  try { d.molText = _td.molText; d.smiles = _td.smiles; } catch (eD) {}
  if (d.submitted && !d.submitting) {
    d.stale = true;
    try {
      var st = document.getElementById("molDraftStatus");
      if (st) st.textContent = fMolDraftT("acceptStale", "Drawing changed — press Submit again.");
    } catch (eSt) {}
  }
  try { fMolDraftSyncBar(); } catch (eSy) {}
}

function fMolDraftMarkStale() {
  try {
    if (!window.MulerDraft || window.MulerDraft.submitting || window.MulerDraftAcquisition) return;
    if (!window.MulerDraft.submitted) return; // nothing to stale yet
    window.MulerDraft.stale = true;
    try {
      var st = document.getElementById("molDraftStatus");
      if (st) st.textContent = fMolDraftT("acceptStale", "Drawing changed — press Submit again.");
    } catch (eSt) {}
    fMolDraftSyncBar();
  } catch (eM) {}
}

// Best-effort live edit detection: structural edits mark the preview stale
// immediately. Guarded — the exact callback name is unverified against the
// bundled JSME; the Accept-time SMILES re-check is authoritative and cannot
// miss. Registered on the dedicated edit applet (the display applet is never
// touched mid-draft, so it needs no watcher).
function fMolDraftWatchEdits() {
  try {
    if (typeof jsmeEditDraftApplet === "undefined" || !jsmeEditDraftApplet) return;
    try {
      if (typeof jsmeEditDraftApplet.setCallBack === "function") {
        jsmeEditDraftApplet.setCallBack("AfterStructureModified", function () { fMolDraftMarkStale(); });
      }
    } catch (eC) {}
  } catch (eW) {}
}

function fMolDraftClearNaming(statusText) {
  try { if (typeof fClearHighlights === "function") fClearHighlights(); } catch (eH) {}
  try {
    var na = document.getElementById("nameAnalysis");
    if (na) na.innerHTML = "<div class='draftHint'>" + fMolDraftEsc(String(statusText || "")) + "</div>";
  } catch (eN) {}
  try {
    var rt = document.getElementById("ruleTheory");
    if (rt) rt.innerHTML = "";
  } catch (eR) {}
  try {
    var ex = document.getElementById("nameAnalysisExplain");
    if (ex) ex.innerHTML = "";
  } catch (eE) {}
}

// Drawing master switch (repurposed Ρυθμίσεις checkbox, default ON):
// the Edit/New/Save title-bar entries exist only while drawing is enabled.
// Called at button build, on toggle, and from fMolDraftSyncButtons.
function fMolDraftSyncEntryButtons() {
  try {
    var on = false;
    try { on = !!document.getElementById("originalJSMECheck").classList.contains("selectedCheck"); } catch (eC) {}
    var eb = document.getElementById("editMolBtn");
    var nb = document.getElementById("newMolBtn");
    var sb = document.getElementById("saveMolBtn");
    if (eb) { if (on) eb.classList.remove("hide"); else eb.classList.add("hide"); }
    if (nb) { if (on) nb.classList.remove("hide"); else nb.classList.add("hide"); }
    if (sb) { if (on) sb.classList.remove("hide"); else sb.classList.add("hide"); }
  } catch (eS) {}
  try { if (typeof fMulerSelectSyncEntry === "function") fMulerSelectSyncEntry(); } catch (eSel) {}
}

// Selection master switch (Ρυθμίσεις "Allow selections", default ON):
// the select-atoms title-bar entry exists only while selection is enabled.
// Missing checkbox fails open (same standardized path as auto-linearize).
function fMulerSelectOn() {
  try {
    var el = document.getElementById("allowSelectCheck");
    if (!el) return true;
    return el.classList.contains("selectedCheck");
  } catch (e) { return true; }
}
function fMulerSelectSyncEntry() {
  try {
    var on = true;
    try { on = fMulerSelectOn(); } catch (eC) { on = true; }
    var b = document.getElementById("selectAtomsBtn");
    if (b) { if (on) b.classList.remove("hide"); else b.classList.add("hide"); }
  } catch (eS) {}
}

// 2D atom/bond selection mode (v56, phase 1A UI): on/off toggle owning the
// future window.MulerUserSelection.active flag. Click capture + selection
// contents land in phase 1B; this is entry/exit + affordances only. Draft
// sessions block entry (same draftLocked contract as name-box clicks); the
// checkbox toggle stays always allowed (it only shows/hides this button).
function fToggleAtomSelect() {
  try {
    if (typeof window !== "undefined" && window.MulerDraft) {
      try { if (typeof fScenarioToast === "function") fScenarioToast(fMolDraftT("draftLocked", "Finish the draft first (Submit/Cancel).")); } catch (eT) {}
      return;
    }
    // Present owns the viewer: arming here would create invisible-active state
    // (paint forced component-only, state kept). Block entry like drafts.
    try { if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return; } catch (eP) {}
    var sel = null;
    try {
      if (typeof window !== "undefined") {
        if (!window.MulerUserSelection) window.MulerUserSelection = { active: false, atoms2D: [], bonds2D: [], atoms3D: [], bonds3D: [] };
        sel = window.MulerUserSelection;
      }
    } catch (eS) { sel = null; }
    var makeActive = !(sel && sel.active === true);
    if (sel) { try { sel.active = makeActive; if (!makeActive) { sel.atoms2D = []; sel.bonds2D = []; sel.atoms3D = []; sel.bonds3D = []; sel.groups = []; } } catch (eA) {} }
    try {
      var b = document.getElementById("selectAtomsBtn");
      if (b) { if (makeActive) b.classList.add("active"); else b.classList.remove("active"); }
    } catch (eB) {}
    try {
      var svg = document.getElementById("jsmeNomeclatureSVG");
      if (svg) { if (makeActive) svg.classList.add("selecting"); else svg.classList.remove("selecting"); }
    } catch (eV) {}
    // Entering select mode starts from a clean slate: drop every previous
    // highlight (2D + 3D + numbering + rule panel + explanation) and any
    // selected component, so picks are never judged against stale visuals.
    // (Selection arrays are empty here — toggle-off cleared them.)
    try { if (makeActive && typeof fMulerQuizDisarm === "function") fMulerQuizDisarm(); } catch (eQD2) {}
    try { if (makeActive && typeof fClearHighlights === "function") fClearHighlights(); } catch (eCH) {}
    try {
      if (makeActive) {
        try { nameAnalysisMode = "none"; } catch (eM) {}
        if (typeof jQuery !== "undefined") { try { jQuery(".nameCompBox").removeClass("selected"); } catch (eB2) {} }
        else { var _sbl = document.querySelectorAll(".nameCompBox"); for (var _si = 0; _si < _sbl.length; _si++) _sbl[_si].classList.remove("selected"); }
      }
    } catch (eD) {}
    try { if (!makeActive && typeof fMulerSelectClear === "function") fMulerSelectClear(); } catch (eC) {}
    try { if (!makeActive && typeof fMulerQuizDisarm === "function") fMulerQuizDisarm(); } catch (eQD) {}
    // v57 3D: disarm erases 3D paint directly (mode flag is already off, so
    // the guarded clear would skip); both paths re-assert picking state.
    try { if (!makeActive && typeof fMulerSelectClear3DPaint === "function") fMulerSelectClear3DPaint(); } catch (eC3) {}
    try { if (typeof fMulerSelectSync3DPicking === "function") fMulerSelectSync3DPicking(); } catch (eS3) {}
    try { if (typeof fMulerSelectRepaint === "function") fMulerSelectRepaint(); } catch (eR) {}
    try { if (typeof fUpdateSVG === "function") fUpdateSVG(); } catch (eU) {}
  } catch (e) {}
}

// ── 2D atom/bond picking (v56 phase 1B: selection contents + paint) ─────
// Displayed-SVG hit-testing + native JSME background-color paint. The JSME
// background channel carries BOTH layers: component green (palette slot 9,
// every existing paint site) and user-selection cyan (palette slot 2).
// A guarded boot-time wrapper merges the two per channel on every paint, so
// selection looks exactly like the default highlight, in cyan, with zero
// DOM cloning and zero per-mode geometry. Precedence is component-wins
// (single merge-order switch — flip it if selection should win instead).
// Stored indices are 1-based JSME numbers (= displayed
// MOL order + 1, same convention as mainChainAtomsList); bond indices are
// 1-based bondList positions (same as setBondBackgroundColors).
var MULER_SELECT_CYAN = "#7ddfff";
var MULER_SELECT_BG_SLOT = 2;   // 1-based JSME palette slot for the selection (component green = 9)
var MULER_SELECT_VERT_EPS = 40;   // vertex clustering, SVG units
var MULER_SELECT_JOINT_EPS = 150; // joint-adoption radius, SVG units (see fMulerSelectVertexAtoms)
var MULER_SELECT_ATOM_R = 0.35;   // atom hit radius, × median bond length
var MULER_SELECT_BOND_HW = 0.2;   // bond corridor half-width, × median bond length
var MULER_SELECT_3D_CLICK_PX = 6;    // max press→release travel for a 3D background "click" (else it was a rotate)
var MULER_SELECT_3D_CLICK_MS = 250;  // grace for the pickCallback to arrive before a release is classified silent
var MULER_SELECT_3D_DOWN_MS = 2000;  // stale-press cap (alt-tab safety)
var MULER_SELECT_3D_DBL_MS = 450;    // double-tap window for 3D deselect
var MULER_SELECT_3D_DBL_PX = 8;      // double-tap radius for 3D deselect

// Selection purpose by quiz target. Only a main-chain purpose lets a compacted
// carbon label resolve to its anchor atom; every other purpose keeps the
// existing whole-fragment semantics (nitro/sulfonyl groups included).
// FG purposes ("fg") are set-only, numberless quiz targets (suffix/ether/ester).
var MULER_SELECT_PURPOSE_BY_TARGET = { compCarbonsCount: "mainChain", compSuffix: "fg", commonEther: "fg", esterEster: "fg", compEndNumber: "loc", compSuffixLocants: "loc", compBondPos: "loc", compNumber1: "loc", compBondType: "bond", compBondType2: "bond" };

function fMulerSelectPurpose() {
  try {
    if (typeof window !== "undefined" && window.MulerSelectPurpose) {
      return String(window.MulerSelectPurpose);
    }
    var t = (typeof window !== "undefined" && window.MulerQuizTarget) ? String(window.MulerQuizTarget) : "";
    if (t && typeof fMulerQuizPurposeFor === "function") {
      return fMulerQuizPurposeFor(t);
    }
  } catch (e) {}
  return "free";
}

// Effective purpose for a mode (no live target needed): bond wins on
// dual-use boxes holding a bond position, else the static map, else free.
// Single FG-first rule shared by arming, redirects and sticky re-arm.
function fMulerQuizPurposeFor(mode) {
  try {
    if (!mode || mode === "none") return "free";
    // Branch first (classic paints branch groups before bond/FG fallthroughs),
    // then secondary hetero prefixes (same paint as fHighlightFG(1)/(2)),
    // then bond dual-use, then the static map. One FG-first rule for the
    // whole dispatch: arm gates, prompts, verdicts and guards.
    if (typeof fMulerBranchAtomsForMode === "function") {
      var _br = fMulerBranchAtomsForMode(mode) || [];
      if (_br.length) return "branch";
    }
    if ((mode === "compNumber1" || mode === "compSecondSub1" || mode === "compNumber2" || mode === "compSecondSub2") &&
        typeof fMulerHeteroPrefixAtomsForMode === "function") {
      var _hg = fMulerHeteroPrefixAtomsForMode(mode) || [];
      if (_hg.length) return "branch";
    }
    if ((mode === "compBondPos" || mode === "compEndNumber" || mode === "compNumber1") &&
        typeof fMulerBondAtomsForMode === "function") {
      var _ba = fMulerBondAtomsForMode(mode) || [];
      if (_ba.length) return "bond";
    }
    if (typeof MULER_SELECT_PURPOSE_BY_TARGET !== "undefined" && MULER_SELECT_PURPOSE_BY_TARGET &&
        Object.prototype.hasOwnProperty.call(MULER_SELECT_PURPOSE_BY_TARGET, mode)) {
      return MULER_SELECT_PURPOSE_BY_TARGET[mode];
    }
  } catch (e) {}
  return "free";
}

// Main-chain + carbon-anchored compact label: the whole label acts as the
// anchor atom. NOx/SOx and every non-main-chain purpose fail this test.
function fMulerSelectCompactCarbonOnly(comp) {
  try {
    if (!comp || typeof comp.anchor !== "number" || comp.anchor < 0) return false;
    if (fMulerSelectPurpose() !== "mainChain") return false;
    if (typeof allAtomsTypeList === "undefined" || !Array.isArray(allAtomsTypeList)) return false;
    return String(allAtomsTypeList[comp.anchor] || "").toUpperCase() === "C";
  } catch (e) { return false; }
}

function fMulerSelectState() {
  try {
    if (typeof window === "undefined") return null;
    if (!window.MulerUserSelection) window.MulerUserSelection = { active: false, molKey: "", atoms2D: [], bonds2D: [], atoms3D: [], bonds3D: [], groups: [] };
    var s = window.MulerUserSelection;
    if (!Array.isArray(s.atoms2D)) s.atoms2D = [];
    if (!Array.isArray(s.bonds2D)) s.bonds2D = [];
    if (!Array.isArray(s.atoms3D)) s.atoms3D = [];
    if (!Array.isArray(s.bonds3D)) s.bonds3D = [];
    if (!Array.isArray(s.groups)) s.groups = [];
    return s;
  } catch (e) { return null; }
}

function fMulerSelectActive() {
  try {
    var s = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null;
    return !!(s && s.active === true);
  } catch (e) { return false; }
}

function fMulerSelectMolKey() {
  try {
    // Intentionally molecule+mode only: eye toggles, chain-stepper index and
    // compaction-skip changes keep atom indices stable, so the selection
    // itself stays valid and only needs a repaint (fUpdateSVG head calls
    // PushState before every render). Extending the key would drop valid picks.
    var m = (typeof selectedMol !== "undefined" && selectedMol) ? String(selectedMol) : "";
    var md = (typeof mode2D !== "undefined" && mode2D) ? String(mode2D) : "";
    return m + "|" + md;
  } catch (e) { return ""; }
}

function fMulerSelectPresenting() {
  try {
    var pc = document.getElementById("pageContainer");
    if (pc && pc.classList && pc.classList.contains("presenting")) return true;
  } catch (e) {}
  try {
    if (typeof window !== "undefined" && window.MuLERMoCScenario && window.MuLERMoCScenario.present) return true;
  } catch (e2) {}
  return false;
}

// Remove the selection halos (DOM only; state untouched — callers own that).
// Halos are <path data-muler-sel> inside the main JSME SVG; the legacy
// sibling-overlay selector is kept so one repaint clears either generation.
function fMulerSelectClearLayer() {
  try {
    var olds = document.querySelectorAll("#jsmeNomeclatureSVG path[data-muler-sel], #jsmeNomeclatureSVG path[data-muler-compact-sel]");
    for (var i = 0; i < olds.length; i++) {
      if (olds[i] && olds[i].parentNode) olds[i].parentNode.removeChild(olds[i]);
    }
  } catch (e) {}
  try {
    var old = document.querySelector("#jsmeNomeclatureSVG #mulerSelectLayerSvg, #jsmeNomeclatureSVG #mulerSelectLayer");
    if (old && old.parentNode) old.parentNode.removeChild(old);
  } catch (e2) {}
}

// Empty the selection (atoms + bonds + groups), paint cleared by repaint.
function fMulerSelectClear() {
  try {
    var s = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null;
    if (s) { s.atoms2D = []; s.bonds2D = []; s.atoms3D = []; s.bonds3D = []; s.groups = []; s._contributors = null; }
  } catch (e) {}
  // v57 3D: erase 3D paint while armed (reward-green lives only under an
  // armed-but-empty state, which never reaches this clear path).
  try { if ((typeof fMulerSelectActive === "function" && fMulerSelectActive()) && typeof fMulerSelectClear3DPaint === "function") fMulerSelectClear3DPaint(); } catch (e3) {}
  try { fMulerSelectClearLayer(); } catch (e2) {}
}

// Bond line groups via the established svgBondList index table (same source
// the highlight painters use for nth-of-type lookups): svgBondList[b] is the
// 1-based position of bond b's first <line>, bondList[b][2] its line count
// (multi-bond rendering). Total-count equality against the live DOM guards
// stale tables (compacted-view line surgery fails closed for bonds here;
// atoms keep working via the label/vertex paths below).
// Returns [{bond:b0, lines:[{x1,y1,x2,y2}...]}] or null on any gap.
function fMulerSelectLineGroups() {
  try {
    if (typeof molSvg === "undefined" || !molSvg) return null;
    if (typeof bondList === "undefined" || !bondList || !bondList.length) return null;
    var lineEls = molSvg.selectAll("line");
    if (!lineEls || !lineEls.length) return null;
    var raw = [];
    for (var i = 0; i < lineEls.length; i++) {
      var nd = lineEls[i] && lineEls[i].node;
      if (!nd || !nd.getAttribute) continue;
      var x1 = parseFloat(nd.getAttribute("x1")), y1 = parseFloat(nd.getAttribute("y1"));
      var x2 = parseFloat(nd.getAttribute("x2")), y2 = parseFloat(nd.getAttribute("y2"));
      if (isNaN(x1 + y1 + x2 + y2)) continue;
      raw.push({ x1: x1, y1: y1, x2: x2, y2: y2 });
    }
    if (!raw.length) return null;
    if (typeof svgBondList === "undefined" || !svgBondList) return null;
    // Compaction deletes removed-bond lines from the DOM, shifting every
    // later bond's position: adjust each start by removed lines before it and
    // skip removed bonds (unpickable — their lines are gone). The removed set
    // is recorded by fCompactFunctionalGroups2D per render (empty elsewhere,
    // so expanded/skeletal/zigzag take the identical path as before).
    var removedSet = {}, removedLinesBefore = {};
    try {
      var __rb = (typeof window !== "undefined" && Array.isArray(window.__mulerRemovedBondIdx))
        ? window.__mulerRemovedBondIdx : [];
      for (var rb = 0; rb < __rb.length; rb++) {
        if (typeof __rb[rb] === "number" && bondList[__rb[rb]]) removedSet[__rb[rb]] = true;
      }
      var __all = [];
      for (var ab = 0; ab < bondList.length; ab++) {
        if (!bondList[ab]) continue;
        __all.push({ b: ab, pos: (svgBondList[ab] || 0), rem: !!removedSet[ab] });
      }
      __all.sort(function (x, y) { return x.pos - y.pos; });
      var __run = 0;
      for (var ao = 0; ao < __all.length; ao++) {
        removedLinesBefore[__all[ao].b] = __run;
        if (__all[ao].rem) __run += bondList[__all[ao].b][2] || 0;
      }
    } catch (eRS) {}
    var groups = [], want = 0;
    for (var b = 0; b < bondList.length; b++) {
      if (!bondList[b]) return null;
      if (removedSet[b]) continue;
      var start = (svgBondList[b] || 0) - 1 - (removedLinesBefore[b] || 0);
      var cnt = bondList[b][2] || 0;
      if (!(start >= 0) || !(cnt > 0) || start + cnt > raw.length) return null;
      want += cnt;
      var ls = [];
      for (var k = 0; k < cnt; k++) ls.push(raw[start + k]);
      groups.push({ bond: b, lines: ls });
    }
    if (!groups.length || want !== raw.length) return null;
    return groups;
  } catch (e) { return null; }
}

// Vertex clustering over group representative segments (longest line per
// group): [{x, y, bonds:[bondIdx...]}]. Implicit (unlabeled) carbons live
// exactly here.
//
// Offset ends of multi-line bonds (C=O, C≡N, ...) are not joints: the
// parallel-line spacing puts the representative endpoint ~60 SVG units away
// from the true atom center, i.e. outside the 40-unit clustering radius, so
// they surface as extra degree-1 vertices. They are merged into the nearby
// true joint (a vertex carrying a different bond) before returning, so the
// topology-based atom assignment below resolves the joint atom correctly.
// Without this, a skeletal aldehyde carbonyl carbon — which has only ONE drawn
// single bond (the C–C; its H is implicit) — would hand the offset C=O end the
// oxygen atom, so clicking the carbon selected O. Ketones/acids were already
// covered by the joint-adoption pass in fMulerSelectVertexAtoms because their
// carbonyl carbon owns two or more drawn single bonds.
function fMulerSelectVertices(groups) {
  var verts = [];
  try {
    if (!groups || !groups.length) return verts;
    // Zoom-relative clustering: absolute EPS breaks when JSME rescales the
    // SVG user units (user zoom / equalizer). Derive from the live median
    // bond length, clamped so extreme layouts fall back near the v56 tuning
    // (40 vertex / 150 joint at typical scale). Falls back to absolute on med==0.
    var _med = 0;
    try { if (typeof fMulerSelectMedianBond === "function") _med = fMulerSelectMedianBond(groups) || 0; } catch (eM) { _med = 0; }
    var _vertEps = MULER_SELECT_VERT_EPS, _jointEps = MULER_SELECT_JOINT_EPS;
    try {
      if (_med > 0 && isFinite(_med)) {
        _vertEps = _med * 0.12;
        if (!(_vertEps >= 15) || !isFinite(_vertEps)) _vertEps = MULER_SELECT_VERT_EPS;
        if (_vertEps < 15) _vertEps = 15;
        if (_vertEps > 120) _vertEps = 120;
        _jointEps = _med * 0.35;
        if (!(_jointEps >= 60) || !isFinite(_jointEps)) _jointEps = MULER_SELECT_JOINT_EPS;
        if (_jointEps < 60) _jointEps = 60;
        if (_jointEps > 400) _jointEps = 400;
      }
    } catch (eC) { _vertEps = MULER_SELECT_VERT_EPS; _jointEps = MULER_SELECT_JOINT_EPS; }
    var EPS2 = _vertEps * _vertEps;
    var at = function (x, y, bi) {
      for (var v = 0; v < verts.length; v++) {
        var dx = verts[v].x - x, dy = verts[v].y - y;
        if (dx * dx + dy * dy <= EPS2) {
          if (verts[v].bonds.indexOf(bi) < 0) verts[v].bonds.push(bi);
          return v;
        }
      }
      verts.push({ x: x, y: y, bonds: [bi] });
      return verts.length - 1;
    };
    for (var g = 0; g < groups.length; g++) {
      var best = groups[g].lines[0], bl = -1;
      for (var li = 0; li < groups[g].lines.length; li++) {
        var L = groups[g].lines[li];
        var dx = L.x2 - L.x1, dy = L.y2 - L.y1, l2 = dx * dx + dy * dy;
        if (l2 > bl) { bl = l2; best = L; }
      }
      groups[g].rep = best;
      at(best.x1, best.y1, groups[g].bond);
      at(best.x2, best.y2, groups[g].bond);
    }
    // Merge offset multi-line ends into their true joint (keep the joint's
    // coordinates). A candidate must carry a different bond and must not
    // already carry the multi-line bond itself — that excludes the bond's
    // opposite end and prevents collapsing both ends into one vertex on a
    // pathologically short bond. Uses the same zoom-relative joint radius.
    try {
      var jointEps2 = _jointEps * _jointEps;
      var merged = true, guard = 0;
      while (merged && guard++ < 64) {
        merged = false;
        for (var vi = 0; vi < verts.length; vi++) {
          var vv = verts[vi];
          if (!vv || !vv.bonds || vv.bonds.length !== 1) continue;
          var bj = vv.bonds[0];
          if (!bondList[bj] || !(bondList[bj][2] > 1)) continue;
          var target = -1, bestD2 = jointEps2 + 1;
          for (var uj = 0; uj < verts.length; uj++) {
            if (uj === vi) continue;
            var uu = verts[uj];
            if (!uu || !uu.bonds || uu.bonds.indexOf(bj) >= 0) continue;
            var otherBond = false;
            for (var ub = 0; ub < uu.bonds.length; ub++) {
              if (uu.bonds[ub] !== bj) { otherBond = true; break; }
            }
            if (!otherBond) continue;
            var ddx = uu.x - vv.x, ddy = uu.y - vv.y, dd = ddx * ddx + ddy * ddy;
            if (dd < bestD2) { bestD2 = dd; target = uj; }
          }
          if (target < 0 || bestD2 > jointEps2) continue;
          for (var vb = 0; vb < vv.bonds.length; vb++) {
            if (verts[target].bonds.indexOf(vv.bonds[vb]) < 0) {
              verts[target].bonds.push(vv.bonds[vb]);
            }
          }
          verts.splice(vi, 1);
          merged = true;
          break;
        }
      }
    } catch (eJ) {}
  } catch (e) {}
  return verts;
}

// Vertex → atom assignment (0-based) purely from connectivity: the atom is
// the unique common member of all incident bond pairs. Degree-1 vertices
// resolve from a resolved co-vertex on the same bond. Leftovers (fully
// symmetric subgraphs, e.g. ethane) get a deterministic arbitrary mapping —
// verdict-neutral there by symmetry. Returns array parallel to verts.
// Optional groups2nd arg lets the joint safety net use the same zoom-relative
// radius as fMulerSelectVertices; without it falls back to absolute.
function fMulerSelectVertexAtoms(verts, groups2nd) {
  var assign = [];
  try {
    for (var v0 = 0; v0 < verts.length; v0++) assign.push(-1);
    var taken = {};
    var pairOf = function (b) {
      try { var q = bondList[b]; return q ? [q[0] - 1, q[1] - 1] : null; } catch (e) { return null; }
    };
    var changed = true, guard = 0;
    while (changed && guard++ < 200) {
      changed = false;
      for (var v = 0; v < verts.length; v++) {
        if (assign[v] >= 0 || !verts[v].bonds.length) continue;
        var common = null, ok = true;
        for (var k = 0; k < verts[v].bonds.length; k++) {
          var pr = pairOf(verts[v].bonds[k]);
          if (!pr) { ok = false; break; }
          if (k === 0) common = pr.slice();
          else {
            var c2 = [];
            for (var c = 0; c < common.length; c++) if (common[c] === pr[0] || common[c] === pr[1]) c2.push(common[c]);
            common = c2;
          }
          if (!common.length) { ok = false; break; }
        }
        if (ok && common.length === 1 && !taken[common[0]]) { assign[v] = common[0]; taken[common[0]] = true; changed = true; continue; }
        if (verts[v].bonds.length === 1) {
          var pr1 = pairOf(verts[v].bonds[0]);
          if (pr1) {
            var free = [];
            for (var a = 0; a < pr1.length; a++) if (!taken[pr1[a]]) free.push(pr1[a]);
            if (free.length === 1) { assign[v] = free[0]; taken[free[0]] = true; changed = true; }
          }
        }
      }
    }
    // Safety net for offset ends that fMulerSelectVertices could not merge
    // (no different-bond vertex within joint radius, or a layout
    // where the offset exceeds the clustering radius): adopt the nearby
    // resolved joint's atom — but only when it belongs to this bond. Multi-line
    // bonds only: single-line joints coincide exactly, so clustering already
    // merges them, and terminal atoms (a full bond length from any joint) can
    // never trigger this. Runs before the leftover pass so the taken-set it
    // sees is clean. Zoom-relative when groups are passed, absolute fallback.
    try {
      var _jEps = MULER_SELECT_JOINT_EPS;
      try {
        if (groups2nd && groups2nd.length && typeof fMulerSelectMedianBond === "function") {
          var _m2 = fMulerSelectMedianBond(groups2nd) || 0;
          if (_m2 > 0 && isFinite(_m2)) {
            _jEps = _m2 * 0.35;
            if (!(_jEps >= 60) || !isFinite(_jEps)) _jEps = MULER_SELECT_JOINT_EPS;
            if (_jEps < 60) _jEps = 60;
            if (_jEps > 400) _jEps = 400;
          }
        }
      } catch (eJE) { _jEps = MULER_SELECT_JOINT_EPS; }
      var JOINT_EPS2 = _jEps * _jEps;
      for (var vj = 0; vj < verts.length; vj++) {
        if (!verts[vj] || !verts[vj].bonds || verts[vj].bonds.length !== 1) continue;
        var bj = verts[vj].bonds[0];
        if (!bondList[bj] || !(bondList[bj][2] > 1)) continue;
        var prj = pairOf(bj);
        if (!prj) continue;
        var bestU = -1, bestD2 = JOINT_EPS2 + 1;
        for (var u = 0; u < verts.length; u++) {
          if (u === vj || !verts[u] || !verts[u].bonds || verts[u].bonds.length < 2) continue;
          if (assign[u] < 0) continue;
          if (assign[u] !== prj[0] && assign[u] !== prj[1]) continue;
          var dux = verts[u].x - verts[vj].x, duy = verts[u].y - verts[vj].y;
          var dd2 = dux * dux + duy * duy;
          if (dd2 < bestD2) { bestD2 = dd2; bestU = u; }
        }
        if (bestU < 0 || !(bestD2 <= JOINT_EPS2)) continue;
        var newA = assign[bestU], oldA = assign[vj];
        if (newA === oldA) continue;
        if (oldA >= 0) {
          var stillHeld = false;
          for (var w = 0; w < verts.length; w++) {
            if (w !== vj && assign[w] === oldA) { stillHeld = true; break; }
          }
          if (!stillHeld) { try { delete taken[oldA]; } catch (eDel) {} }
        }
        assign[vj] = newA;
        try { taken[newA] = true; } catch (eTk) {}
      }
    } catch (eJ) {}
    for (var v3 = 0; v3 < verts.length; v3++) {
      if (assign[v3] >= 0 || !verts[v3].bonds.length) continue;
      var pr3 = pairOf(verts[v3].bonds[0]);
      if (!pr3) continue;
      for (var a3 = 0; a3 < pr3.length; a3++) {
        if (!taken[pr3[a3]]) { assign[v3] = pr3[a3]; taken[pr3[a3]] = true; break; }
      }
    }
  } catch (e) {}
  return assign;
}

// Labeled-atom centers in SVG units, via the established order maps
// (same functions + args the paint pipeline uses). Returns [{atom:0-based, x, y}].
function fMulerSelectAnchors() {
  var out = [];
  try {
    if (typeof molSvg === "undefined" || !molSvg) return out;
    // Skeletal has no per-carbon texts (hetero labels only), so order maps
    // cannot align there — heteroatoms resolve geometrically below, carbons
    // via the topological vertex path in the pick. Other modes use the maps.
    var skel = false;
    try { skel = (typeof mode2D !== "undefined" && mode2D === "skeletal"); } catch (eM2) {}
    if (skel) {
      try {
        var hg = (typeof fMulerSelectLineGroups === "function") ? fMulerSelectLineGroups() : null;
        var ha = (typeof fMulerSelectHeteroAnchors === "function") ? fMulerSelectHeteroAnchors(hg) : [];
        for (var hi = 0; hi < ha.length; hi++) out.push(ha[hi]);
      } catch (eH) {}
      return out;
    }
    var inclH = false;
    try { inclH = (typeof mode2D !== "undefined" && mode2D === "expanded"); } catch (eM) {}
    var rMap = null, tMap = null;
    // Exclude compaction-hidden atoms (COOH/CHO/NO2/CN members): their nodes
    // are deleted from the DOM, so including them shifts every downstream
    // atom onto its neighbor's label. Established maps use the same flags.
    // Hidden skeletal sp-C labels (display:none, kept for order) are filtered
    // below via the data-muler-hidden marker — the vertex fallback owns them.
    try { if (typeof fGetRenderedAtomRectMap === "function") rMap = fGetRenderedAtomRectMap(false, inclH) || null; } catch (eR) { rMap = null; }
    try { if (typeof fGetRenderedAtomTextMap === "function") tMap = fGetRenderedAtomTextMap(false, inclH) || null; } catch (eT) { tMap = null; }
    var isHiddenNode = function (nd) {
      try {
        if (!nd || !nd.getAttribute) return false;
        if (nd.getAttribute("data-muler-hidden")) return true;
        if (nd.style && nd.style.display === "none") return true;
      } catch (eH) {}
      return false;
    };
    var seen = {};
    var pushP = function (atom, x, y, w, h) {
      if (atom == null || isNaN(x) || isNaN(y) || seen[atom]) return;
      seen[atom] = true;
      out.push({ atom: atom, x: x, y: y, w: (w > 0 ? w : 0), h: (h > 0 ? h : 0) });
    };
    // Text centers first (visual truth, immune to rect-list surgery:
    // bg-removal, highlight nodes, compaction deletions); rect centers only
    // as fallback where getBBox is unavailable (e.g. display:none nodes).
    if (tMap && typeof document !== "undefined" && document.createElementNS) {
      for (var k2 in tMap) {
        if (!Object.prototype.hasOwnProperty.call(tMap, k2)) continue;
        if (seen[k2]) continue;
        try {
          var el2 = tMap[k2];
          var nd2 = el2 && el2.node ? el2.node : null;
          if (!nd2 || !nd2.getBBox) continue;
          if (typeof isHiddenNode === "function" && isHiddenNode(nd2)) continue;
          var bb = nd2.getBBox();
          pushP(parseInt(k2, 10), bb.x + bb.width / 2, bb.y + bb.height / 2, bb.width, bb.height);
        } catch (eB) {}
      }
    }
    if (rMap) {
      for (var k in rMap) {
        if (!Object.prototype.hasOwnProperty.call(rMap, k)) continue;
        if (seen[k]) continue;
        try {
          var el = rMap[k];
          var nd = el && el.node ? el.node : el;
          if (typeof isHiddenNode === "function" && isHiddenNode(nd)) continue;
          var x = parseFloat(nd.getAttribute ? nd.getAttribute("x") : NaN);
          var y = parseFloat(nd.getAttribute ? nd.getAttribute("y") : NaN);
          var w = parseFloat(nd.getAttribute ? nd.getAttribute("width") : NaN);
          var h = parseFloat(nd.getAttribute ? nd.getAttribute("height") : NaN);
          if (isNaN(x + y + w + h)) continue;
          pushP(parseInt(k, 10), x + w / 2, y + h / 2, w, h);
        } catch (eA) {}
      }
    }
  } catch (e) {}
  return out;
}

// Heteroatom anchors for skeletal mode (no order maps there — skeletal
// carbons have no text nodes at all). Each hetero label sits at the end of
// its bond line(s), so labels are matched to atoms by bond-endpoint
// proximity: greedy best-first, one text and one atom each, element-letter
// match preferred (breaks N–O ties). Positions come from the text bboxes
// (pixel-exact); bonds only decide the atom index. Fail closed throughout.
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

function fMulerSelectMedianBond(groups) {
  try {
    var lens = [];
    for (var g = 0; g < groups.length; g++) {
      var ls = groups[g].lines;
      for (var i = 0; i < ls.length; i++) {
        var dx = ls[i].x2 - ls[i].x1, dy = ls[i].y2 - ls[i].y1;
        lens.push(Math.sqrt(dx * dx + dy * dy));
      }
    }
    if (!lens.length) return 0;
    lens.sort(function (a, b) { return a - b; });
    return lens[Math.floor(lens.length / 2)] || 0;
  } catch (e) { return 0; }
}

function fMulerSelectCompactRect(anchor) {
  try {
    if (typeof document === "undefined" || typeof anchor !== "number") return null;
    return document.querySelector(
      '#jsmeNomeclatureSVG rect[data-muler-compact-rect="' + (anchor + 1) + '"]',
    );
  } catch (e) { return null; }
}

function fRectBox(rect) {
  try {
    if (!rect || !rect.getBoundingClientRect) return null;
    var bb = rect.getBBox ? rect.getBBox() : null;
    if (!bb || !(bb.width > 0) || !(bb.height > 0)) return null;
    return { x: bb.x, y: bb.y, w: bb.width, h: bb.height };
  } catch (e) { return null; }
}

function fUnionBox(a, b) {
  if (!a) return b;
  if (!b) return a;
  var x = Math.min(a.x, b.x), y = Math.min(a.y, b.y);
  var r = Math.max(a.x + a.w, b.x + b.w);
  var bot = Math.max(a.y + a.h, b.y + b.h);
  return { x: x, y: y, w: r - x, h: bot - b.y };
}

// Bounding boxes for one compacted label:
// - box: whole label/backplate area (main-chain hit area; fragment hover);
// - textBox: the glyph run only (free-selection hit area, pre-v56 behavior);
// - atomBox: the anchor C/N/S glyph only (hover/badge/paint helper).
function fMulerSelectCompactBoxes(comp) {
  var out = { box: null, textBox: null, atomBox: null, rectEl: null, symbol: "" };
  try {
    if (!comp || !comp.el) return out;
    try { out.symbol = String(allAtomsTypeList[comp.anchor] || "").toUpperCase(); } catch (eS) {}
    var textBox = fRectBox(comp.el);
    out.textBox = textBox ? { x: textBox.x, y: textBox.y, w: textBox.w, h: textBox.h } : null;
    out.box = out.textBox;
    var rectEl = fMulerSelectCompactRect(comp.anchor);
    out.rectEl = rectEl || null;
    var rectBox = rectEl ? fRectBox(rectEl) : null;
    if (rectBox) out.box = fUnionBox(out.box, rectBox);

    var txt = "";
    try { txt = String(comp.el.textContent || ""); } catch (eT) { txt = ""; }
    var idx = (out.symbol && txt) ? txt.indexOf(out.symbol) : -1;
    if (idx >= 0 && comp.el.getExtentOfChar) {
      try {
        var ext = comp.el.getExtentOfChar(idx);
        if (ext && ext.width > 0 && ext.height > 0) {
          out.atomBox = { x: ext.x, y: ext.y, w: ext.width, h: ext.height };
        }
      } catch (eC) {}
    }
    if (!out.atomBox && textBox && txt.length) {
      // Geometric fallback: same character cell as the label's text run.
      var cw = textBox.w / txt.length;
      var ci = idx >= 0 ? idx : 0;
      out.atomBox = { x: textBox.x + ci * cw, y: textBox.y, w: cw, h: textBox.h };
    }
  } catch (e) {}
  return out;
}

// Hit test in SVG user units. Priority: labeled anchor → vertex (implicit C)
// → bond corridor → null (clear). Returns {kind:'atom',atom:1-based} |
// Compacted functional-group labels (condensed): the JSME text/rects of the
// member atoms are replaced by a single label. Pair each label with its
// member atoms via the skipped-atom set: connected components, each anchored
// at a non-skipped neighbor whose mapped text IS the compacted label.
// Fail closed on any gap.
function fMulerSelectCompacted() {
  var out = [];
  try {
    if (typeof mode2D === "undefined" || mode2D !== "condensed") return out;
    if (typeof fGetCompactedAtomSkipSet !== "function") return out;
    var skip = null;
    try { skip = fGetCompactedAtomSkipSet(false); } catch (eS) { skip = null; }
    if (!skip || !skip.size) return out;
    var adj = {};
    try {
      if (typeof bondList !== "undefined" && bondList) {
        for (var b = 0; b < bondList.length; b++) {
          var qb = bondList[b];
          if (!qb) continue;
          var ba = qb[0] - 1, bc = qb[1] - 1;
          if (!skip.has(ba) || !skip.has(bc)) continue;
          if (!adj[ba]) adj[ba] = [];
          if (!adj[bc]) adj[bc] = [];
          adj[ba].push(bc); adj[bc].push(ba);
        }
      }
    } catch (eA) {}
    var seen = {}, comps = [];
    skip.forEach(function (s) {
      if (seen[s]) return;
      var comp = [], stack = [s];
      seen[s] = true;
      while (stack.length) {
        var n = stack.pop();
        comp.push(n);
        var nb = adj[n] || [];
        for (var i = 0; i < nb.length; i++) {
          if (!seen[nb[i]]) { seen[nb[i]] = true; stack.push(nb[i]); }
        }
      }
      comp.sort(function (x, y) { return x - y; });
      comps.push(comp);
    });
    if (!comps.length) return out;
    // anchor text per component: mapped label of a non-skipped neighbor
    var tMap = null;
    // Anchor labels only: hidden FG members are deleted from the DOM, so the
    // map must exclude them (same shift bug as the anchors above).
    try { if (typeof fGetRenderedAtomTextMap === "function") tMap = fGetRenderedAtomTextMap(false, false) || null; } catch (eT) { tMap = null; }
    var byNode = {};
    if (tMap) {
      for (var k in tMap) {
        if (!Object.prototype.hasOwnProperty.call(tMap, k)) continue;
        try { if (tMap[k] && tMap[k].node) byNode[k] = tMap[k].node; } catch (eN) {}
      }
    }
    for (var ci = 0; ci < comps.length; ci++) {
      var anchor = -1;
      try {
        var cand = {};
        for (var mi = 0; mi < comps[ci].length; mi++) {
          var nbrs = (typeof atomConnectivityList !== "undefined" && atomConnectivityList[comps[ci][mi]]) || [];
          for (var ni = 0; ni < nbrs.length; ni++) {
            if (!skip.has(nbrs[ni])) cand[nbrs[ni]] = true;
          }
        }
        var keys = Object.keys(cand).map(function (x) { return parseInt(x, 10); }).sort(function (x, y) { return x - y; });
        if (keys.length) anchor = keys[0];
      } catch (eAN) { anchor = -1; }
      if (anchor < 0) continue;
      var members = comps[ci].slice();
      members.push(anchor);
      members.sort(function (x, y) { return x - y; });
      var labelEl = null;
      try { labelEl = byNode[String(anchor)] || null; } catch (eL2) { labelEl = null; }
      var labNode = (labelEl && labelEl.node) ? labelEl.node : ((labelEl && typeof labelEl.getAttribute === "function") ? labelEl : null);
      out.push({
        anchor: anchor,
        members: members.map(function (a) { return a + 1; }),
        el: labNode
      });
    }
    // merge entries that share an anchor (same visual label, e.g. both acid
    // oxygens): the whole label is one pickable unit
    var merged = {};
    for (var oi = 0; oi < out.length; oi++) {
      var mk = "a" + out[oi].anchor;
      if (!merged[mk]) merged[mk] = { anchor: out[oi].anchor, members: [], el: out[oi].el };
      for (var mj = 0; mj < out[oi].members.length; mj++) {
        if (merged[mk].members.indexOf(out[oi].members[mj]) < 0) merged[mk].members.push(out[oi].members[mj]);
      }
      if (!merged[mk].el && out[oi].el) merged[mk].el = out[oi].el;
    }
    var fin = [];
    for (var fk in merged) {
      if (!Object.prototype.hasOwnProperty.call(merged, fk)) continue;
      merged[fk].members.sort(function (x, y) { return x - y; });
      var boxes = fMulerSelectCompactBoxes(merged[fk]);
      merged[fk].box = boxes.box;
      merged[fk].textBox = boxes.textBox;
      merged[fk].atomBox = boxes.atomBox;
      merged[fk].rectEl = boxes.rectEl;
      merged[fk].symbol = boxes.symbol;
      fin.push(merged[fk]);
    }
    return fin;
  } catch (e) { return []; }
}

// Main-chain purpose only: collapse any already-selected compacted carbon
// fragments to their anchor before comparison continues. Non-carbon groups
// (NOx/SOx etc.) and free selection are untouched.
function fMulerSelectNormalizeMainChainCompacts() {
  try {
    if (fMulerSelectPurpose() !== "mainChain") return;
    var sel = fMulerSelectState();
    if (!sel || !Array.isArray(sel.atoms2D) || !sel.atoms2D.length) return;
    var comps = (typeof fMulerSelectCompacted === "function") ? fMulerSelectCompacted() : [];
    for (var ci = 0; ci < comps.length; ci++) {
      var cm = comps[ci];
      if (!cm || !Array.isArray(cm.members) || !fMulerSelectCompactCarbonOnly(cm)) continue;
      var members = {};
      for (var mi = 0; mi < cm.members.length; mi++) members[cm.members[mi]] = true;
      var anchor = cm.anchor + 1;
      var out = [], placed = false, touched = false;
      for (var ai = 0; ai < sel.atoms2D.length; ai++) {
        var a = sel.atoms2D[ai];
        if (members[a]) {
          touched = true;
          if (!placed) { out.push(anchor); placed = true; }
        } else {
          out.push(a);
        }
      }
      if (touched) {
        sel.atoms2D = out;
        if (Array.isArray(sel.groups)) {
          sel.groups = sel.groups.map(function (g) {
            if (!g || !Array.isArray(g.members)) return g;
            var hit = false;
            for (var gi = 0; gi < g.members.length; gi++) {
              if (members[g.members[gi]]) { hit = true; break; }
            }
            return hit ? { heavy: anchor, members: [anchor], compacted: true, anchorOnly: true } : g;
          });
        }
      }
    }
  } catch (e) {}
}

// Hover-ring skin (v56 selection follow-up): stroke-only cyan, no fill —
// visually distinct from solid selection cyan and component green.
var MULER_HOVER_PAD = 45;   // ring margin around label boxes, SVG units
var MULER_HOVER_SW = 30;    // ring stroke width, SVG units
var MULER_HOVER_DOT_R = 210;  // implicit-carbon ring radius, SVG units
var MULER_HOVER_BOND_W = 110; // bond hover stroke width, SVG units
var MULER_HOVER_OPACITY = 0.55; // ring translucency (bonds keep their own 0.5)

// Per-render geometry cache for hit-testing (hover reads it at mousemove
// rate; rebuilding maps + getBBox per move would blow the frame budget).
// Keyed by molecule+mode+render-epoch; fail-soft miss returns empty shapes.
function fMulerSelectGeom() {
  try {
    var key = "";
    try { key = (typeof fMulerSelectMolKey === "function") ? fMulerSelectMolKey() : ""; } catch (eK) {}
    try {
      var seq = (typeof window !== "undefined" && typeof window.__mulerSelRenderSeq === "number") ? window.__mulerSelRenderSeq : 0;
      key += "#" + seq;
    } catch (eS) {}
    try {
      if (typeof window !== "undefined" && window.__mulerSelGeom && window.__mulerSelGeom.key === key) return window.__mulerSelGeom;
    } catch (eC) {}
    var g = null, a = [], c = [], v = [], va = [], m = 0, bb = {};
    try { if (typeof fMulerSelectLineGroups === "function") g = fMulerSelectLineGroups(); } catch (eG) { g = null; }
    try { if (typeof fMulerSelectAnchors === "function") a = fMulerSelectAnchors() || []; } catch (eA) { a = []; }
    try { if (typeof fMulerSelectCompacted === "function") c = fMulerSelectCompacted() || []; } catch (eC2) { c = []; }
    try { v = (typeof fMulerSelectVertices === "function") ? fMulerSelectVertices(g) : []; } catch (eV) { v = []; }
    try { va = (typeof fMulerSelectVertexAtoms === "function") ? fMulerSelectVertexAtoms(v, g) : []; } catch (eVA) { va = []; }
    try { m = (typeof fMulerSelectMedianBond === "function") ? fMulerSelectMedianBond(g) : 0; } catch (eM) { m = 0; }
    try { if (g) for (var gi = 0; gi < g.length; gi++) bb[g[gi].bond] = g[gi]; } catch (eBB) {}
    var geom = { key: key, groups: g, anchors: a, comp: c, verts: v, vassign: va, med: (m > 0 ? m : 0), byBond: bb };
    try { if (typeof window !== "undefined") window.__mulerSelGeom = geom; } catch (eW) {}
    return geom;
  } catch (e) { return { key: "", groups: null, anchors: [], comp: [], verts: [], vassign: [], med: 0, byBond: {} }; }
}

// Label box for a resolved pick (atom/fragment), from cached anchors /
// compacted entries. Vertex picks and bonds are painted from groups instead.
function fMulerHoverBoxForPick(pick, geom) {
  try {
    if (!pick) return null;
    if (pick.kind === "atom" && pick.compactAnchor && pick.compactAtomBox) {
      return pick.compactAtomBox;
    }
    if (pick.kind === "fragment") {
      if (pick.compactGroupBox) return pick.compactGroupBox;
      var want = ((pick.atoms || []).slice() || []).sort(function (x, y) { return x - y; });
      var list = (geom && geom.comp) || [];
      for (var ci = 0; ci < list.length; ci++) {
        var cm = list[ci];
        if (!cm || !cm.members || !cm.el) continue;
        var got = (cm.members.slice() || []).sort(function (x, y) { return x - y; });
        if (got.length !== want.length) continue;
        var same = true;
        for (var mi = 0; mi < got.length; mi++) { if (got[mi] !== want[mi]) { same = false; break; } }
        if (!same) continue;
        if (cm.box && cm.box.w > 0 && cm.box.h > 0) return cm.box;
        var bb = null;
        try { bb = (cm.el.getBBox && cm.el.getBBox()) || null; } catch (eB) { bb = null; }
        if (bb && bb.width > 0 && bb.height > 0) return { x: bb.x, y: bb.y, w: bb.width, h: bb.height };
      }
      return null;
    }
    if (pick.kind === "atom" && (pick.vertex === undefined || pick.vertex === null)) {
      var al = (geom && geom.anchors) || [];
      for (var ai = 0; ai < al.length; ai++) {
        if (al[ai] && al[ai].atom === pick.atom - 1 && al[ai].w > 0 && al[ai].h > 0) {
          return { x: al[ai].x - al[ai].w / 2, y: al[ai].y - al[ai].h / 2, w: al[ai].w, h: al[ai].h };
        }
      }
    }
    return null;
  } catch (e) { return null; }
}

function fMulerHoverClear() {
  try {
    var old = document.querySelector("#jsmeNomeclatureSVG #mulerHoverRing");
    if (old && old.parentNode) old.parentNode.removeChild(old);
  } catch (e) {}
}

// Hover ring paint (DOM overlay only — never the applet channel, never a
// re-render: safe at mousemove rate). One persistent layer, rebuilt per move;
// the fUpdateSVG innerHTML rebuild wipes it implicitly on re-render.
function fMulerHoverPaint(pick, geom) {
  try {
    try { fMulerHoverClear(); } catch (eC) {}
    if (!pick || pick.ignore) return;
    var host = null;
    try { host = document.getElementById("jsmeNomeclatureSVG"); } catch (eH) {}
    if (!host) return;
    var NS = "http://www.w3.org/2000/svg";
    var layer = null, inner = null;
    try {
      layer = document.createElementNS(NS, "svg");
      layer.setAttribute("id", "mulerHoverRing");
      layer.setAttribute("pointer-events", "none");
      layer.setAttribute("width", "100%"); layer.setAttribute("height", "100%");
      layer.setAttribute("style", "position:absolute;inset:0;pointer-events:none;");
      var gT = "";
      try {
        var _svg = host.querySelector("svg");
        var _gs = _svg ? _svg.getElementsByTagName("g") : null;
        var _g0 = (_gs && _gs.length) ? _gs[0] : null;
        if (_g0 && _g0.getAttribute) gT = _g0.getAttribute("transform") || "";
      } catch (eG) {}
      inner = document.createElementNS(NS, "g");
      if (gT) inner.setAttribute("transform", gT);
      layer.appendChild(inner);
    } catch (eL) { return; }
    if (!inner) return;
    var done = false;
    if ((pick.kind === "atom" || pick.kind === "fragment") && (pick.vertex === undefined || pick.vertex === null)) {
      var box = (typeof fMulerHoverBoxForPick === "function") ? fMulerHoverBoxForPick(pick, geom) : null;
      if (box && box.w > 0 && box.h > 0) {
        try {
          var r = document.createElementNS(NS, "rect");
          r.setAttribute("x", Math.round(box.x - MULER_HOVER_PAD));
          r.setAttribute("y", Math.round(box.y - MULER_HOVER_PAD));
          r.setAttribute("width", Math.round(box.w + 2 * MULER_HOVER_PAD));
          r.setAttribute("height", Math.round(box.h + 2 * MULER_HOVER_PAD));
          r.setAttribute("rx", "90");
          r.setAttribute("fill", "none");
          r.setAttribute("stroke", MULER_SELECT_CYAN);
          r.setAttribute("stroke-width", MULER_HOVER_SW);
          r.setAttribute("stroke-opacity", MULER_HOVER_OPACITY);
          r.setAttribute("pointer-events", "none");
          inner.appendChild(r); done = true;
        } catch (eR) {}
      }
    }
    // unlabeled skeletal vertex: circle outline at the vertex
    if (!done && pick.kind === "atom" && pick.vertex !== undefined && pick.vertex !== null && geom && geom.verts) {
      try {
        var vv = geom.verts[pick.vertex];
        if (vv) {
          var cc = document.createElementNS(NS, "circle");
          cc.setAttribute("cx", Math.round(vv.x)); cc.setAttribute("cy", Math.round(vv.y));
          cc.setAttribute("r", MULER_HOVER_DOT_R);
          cc.setAttribute("fill", "none");
          cc.setAttribute("stroke", MULER_SELECT_CYAN);
          cc.setAttribute("stroke-width", MULER_HOVER_SW);
          cc.setAttribute("stroke-opacity", MULER_HOVER_OPACITY);
          cc.setAttribute("pointer-events", "none");
          inner.appendChild(cc); done = true;
        }
      } catch (eC2) {}
    }
    // bond: wide translucent stroke per segment (mirrors selection look)
    if (!done && pick.kind === "bond" && geom && geom.byBond) {
      try {
        var G = geom.byBond[pick.bond - 1];
        if (G && G.lines) {
          for (var li = 0; li < G.lines.length; li++) {
            var L = G.lines[li];
            var ln = document.createElementNS(NS, "line");
            ln.setAttribute("x1", Math.round(L.x1)); ln.setAttribute("y1", Math.round(L.y1));
            ln.setAttribute("x2", Math.round(L.x2)); ln.setAttribute("y2", Math.round(L.y2));
            ln.setAttribute("stroke", MULER_SELECT_CYAN);
            ln.setAttribute("stroke-width", MULER_HOVER_BOND_W);
            ln.setAttribute("stroke-linecap", "round");
            ln.setAttribute("stroke-opacity", "0.5");
            ln.setAttribute("pointer-events", "none");
            inner.appendChild(ln); done = true;
          }
        }
      } catch (eQ) {}
    }
    if (done) { try { host.appendChild(layer); } catch (eA2) { done = false; } }
  } catch (e) {}
}

// rAF tick for hover: same guards + transform + pick path as clicks, so the
// ring always shows exactly what a click would do. No-op on touch devices
// (no mousemove) and whenever select mode is not armed.
function fMulerHoverTick() {
  try {
    if (typeof window === "undefined" || !window.__mulerHoverInside) return;
    if (!(typeof fMulerSelectActive === "function" && fMulerSelectActive())) return;
    if (typeof window !== "undefined" && window.MulerDraft) return;
    if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return;
    if (typeof selectedMol === "undefined" || !selectedMol) return;
    var svg = null;
    try { svg = document.querySelector("#jsmeNomeclatureSVG svg"); } catch (eS) { svg = null; }
    if (!svg) return;
    var g = null;
    try { var gs = svg.getElementsByTagName("g"); if (gs && gs.length) g = gs[0]; } catch (eG) { g = null; }
    var m = null;
    try { m = (g || svg).getScreenCTM(); } catch (eM) { m = null; }
    if (!m) return;
    var inv = null;
    try { inv = m.inverse(); } catch (eI) { return; }
    var q = null;
    try { q = new DOMPoint(window.__mulerHoverX || 0, window.__mulerHoverY || 0).matrixTransform(inv); } catch (eP) { return; }
    if (!q || !isFinite(q.x) || !isFinite(q.y)) return;
    var pick = null;
    try { pick = (typeof fMulerSelectPick === "function") ? fMulerSelectPick(q.x, q.y) : null; } catch (ePk) { pick = null; }
    if (!pick || pick.ignore) { try { fMulerHoverClear(); } catch (eC) {} return; }
    try {
      var geom = (typeof fMulerSelectGeom === "function") ? fMulerSelectGeom() : null;
      if (typeof fMulerHoverPaint === "function") fMulerHoverPaint(pick, geom);
    } catch (ePt) {}
  } catch (e) {}
}

// Returns an atom, fragment, bond, ignored hit, or null for empty canvas.
// Armed-quiz hydrogen rule (v56 H phase): an H pick that is not itself a
// target atom resolves to its sole neighbor — condensed-style unit picking
// (the H belongs to its heavy atom's unit), so alkyl H can never leak into a
// set-only target or force a hetero/wrong hint. Target H (hydroxyl, aldehyde)
// stays distinct and pickable; free selection is untouched. Returns the
// replacement 1-based atom, or -1 to keep the original pick.
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

// The live applet and the page's SDF arrays finish independently. A queued
// load-tail acknowledgement and a parse of that exact requested source are
// both required before any selection callback, paint or picking script runs.
var fMuler3DLoadEpoch = 0;
var fMuler3DModel = null;
var fMuler3DParsed = null;
var fMuler3DLoadWriter = null;
function fMuler3DSourceKey() {
  try {
    var e = nameExamples[selectedMol];
    return e ? JSON.stringify([selectedMol, e.file3D || null, e.sdf3D || null]) : null;
  } catch (e) { return null; }
}
function fMuler3DBeginLoad() {
  var old = fMuler3DModel;
  if (old) { try { delete window[old.pickCallback]; } catch (e) {} }
  var id = ++fMuler3DLoadEpoch;
  var m = { id: id, source: fMuler3DSourceKey(), mol: selectedMol,
    applet: jmolAppletNomeclature, revision: fMolDraft3DRevision,
    completed: false, parsed: null, liveValidated: false, picking: null, pickCallback: "__mulerPickCb_" + id };
  if (fMuler3DParsed && fMuler3DParsed.source === m.source &&
      fMuler3DParsed.text === molAtomMapSource3D) m.parsed = fMuler3DParsed;
  fMuler3DModel = m;
  window[m.pickCallback] = function () {
    if (fMuler3DModel === m) return window.__mulerPickCb.apply(window, arguments);
  };
  return m;
}
function fMuler3DWillScript(applet, cmd) {
  if (applet !== jmolAppletNomeclature || !/(^|;)\s*(?:load|zap)\b/i.test(String(cmd))) return;
  if (fMuler3DLoadWriter && fMuler3DLoadWriter === fMuler3DModel) {
    fMuler3DLoadWriter.revision = fMolDraft3DRevision;
    fMuler3DLoadWriter.completed = false;
    fMuler3DLoadWriter.liveValidated = false;
    fMuler3DLoadWriter.picking = null;
  } else {
    if (fMuler3DModel) { try { delete window[fMuler3DModel.pickCallback]; } catch (e) {} }
    fMuler3DModel = null;
    ++fMuler3DLoadEpoch;
  }
}
function fMuler3DModelReady() {
  try {
    var m = fMuler3DModel;
    return !!(m && m.completed && m.parsed && m.liveValidated && m.source && m.source === fMuler3DSourceKey() &&
      m.mol === selectedMol && m.applet === jmolAppletNomeclature &&
      m.revision === fMolDraft3DRevision && m.parsed.text === molAtomMapSource3D &&
      !window.MulerDraft && fJSmolLive());
  } catch (e) { return false; }
}
// Read the finished live model, rather than treating a script submission (or
// even a tail after a failed load) as proof that the requested model is visible.
function fMuler3DValidateLiveModel(m) {
  try {
    if (!m || m.applet !== jmolAppletNomeclature || m.revision !== fMolDraft3DRevision ||
        m.source !== fMuler3DSourceKey() || !m.parsed) return false;
    var info = fJSmolGetPropertyAsArray(m.applet, "modelInfo");
    var atoms = fJSmolGetPropertyAsArray(m.applet, "atomInfo");
    var bonds = fJSmolGetPropertyAsArray(m.applet, "bondInfo");
    var record = fParseMolV2000(m.parsed.text);
    if (!info || info.modelCount !== 1 || !info.models || info.models.length !== 1 || !record ||
        !Array.isArray(atoms) || atoms.length !== record.atoms.length || info.models[0].atomCount !== atoms.length ||
        info.models[0].bondCount !== record.bonds.length) return false;
    var source = nameExamples[m.mol];
    if (source.file3D && String(info.models[0].file) !== new URL(source.file3D, window.location.href).href) return false;
    for (var i = 0; i < atoms.length; i++) {
      var a = atoms[i], expected = record.atoms[i];
      if (!a || a.atomIndex !== i || a.atomno !== i + 1 || a.sym !== expected.el ||
          a.formalCharge !== (expected.charge || 0) ||
          Math.abs(a.x - expected.x) > 0.001 || Math.abs(a.y - expected.y) > 0.001 || Math.abs(a.z - expected.z) > 0.001) return false;
    }
    if (!Array.isArray(bonds) || bonds.length !== record.bonds.length) return false;
    for (var j = 0; j < bonds.length; j++) {
      var b = bonds[j], expectedBond = record.bonds[j];
      if (!b || b._bpt !== j || !b.atom1 || !b.atom2 || b.order !== expectedBond[2] ||
          !((b.atom1.atomno === expectedBond[0] && b.atom2.atomno === expectedBond[1]) ||
            (b.atom1.atomno === expectedBond[1] && b.atom2.atomno === expectedBond[0]))) return false;
    }
    return true;
  } catch (e) { return false; }
}
function fMuler3DReplaySelection(m) {
  if (fMuler3DModel !== m) return;
  if (!m.liveValidated && m.completed && m.parsed) m.liveValidated = fMuler3DValidateLiveModel(m);
  if (!fMuler3DModelReady()) return;
  try { fMulerSelectSync3DPicking(); } catch (eP) {}
  try { fMulerSelectRebuildMirrors(); } catch (eM) {}
  try { fMulerSelectRepaint(); } catch (eR) {}
}
window.__muler3DLoadDone = function (id) {
  var m = fMuler3DModel;
  if (!m || id !== m.id || m.mol !== selectedMol || m.applet !== jmolAppletNomeclature ||
      m.source !== fMuler3DSourceKey() || m.revision !== fMolDraft3DRevision || window.MulerDraft) return;
  m.completed = true;
  // Leave the JSmol evaluation stack before queuing further applet work.
  setTimeout(function () { fMuler3DReplaySelection(m); }, 0);
};
function fMuler3DParsedSource(m, text) {
  if (!m || fMuler3DModel !== m || m.source !== fMuler3DSourceKey() || m.mol !== selectedMol) return;
  fMuler3DParsed = { source: m.source, text: text };
  m.parsed = fMuler3DParsed;
  fMuler3DReplaySelection(m);
}

// Reuse the core's strict, ordered-graph AND source-aware cache. A failed
// strict translation must never revive an older map or try ignoreOrder=true.
function fMulerHeavyMapCached() {
  try {
    if (!fMuler3DModelReady()) return null;
    var heavy = -1;
    for (var i = 0; i < allAtomsTypeList.length; i++) {
      if (String(allAtomsTypeList[i]).toUpperCase() !== "H") { heavy = i + 1; break; }
    }
    if (heavy < 1 || typeof fTranslateChain2D3D !== "function" || !fTranslateChain2D3D([heavy])) return null;
    var M = molAtomMap2D3D;
    if (!M || !M.arr || M.n2 !== allAtomsTypeList.length || M.n3 !== allAtomsTypeList3D.length) return null;
    return M;
  } catch (e) { return null; }
}

// The old heavy helper does not validate formal metadata. Extend its result
// only when the parsed current records agree on supported atom metadata.
// Equivalent explicit H on a mapped parent are paired in stable source order,
// each at most once. No first-H-for-all shortcut and no invented implicit H.
function fMulerSelectFullMap() {
  try {
    var M = fMulerHeavyMapCached();
    if (!M || typeof fParseMolV2000 !== "function") return null;
    var source2 = jsmeNomeclatureApplet.molFile();
    var key = JSON.stringify([molAtomMapKey, source2, molAtomMapSource3D]);
    if (M.selectionMap && M.selectionMap.key === key) return M.selectionMap;
    var A = fParseMolV2000(source2), B = fParseMolV2000(molAtomMapSource3D);
    if (!A || !B || A.atoms.length !== allAtomsTypeList.length || B.atoms.length !== allAtomsTypeList3D.length) return null;
    function meta(a) {
      return JSON.stringify([a.el, a.charge || 0, a.massDifference || 0, a.isotope || 0, a.radical || 0]);
    }
    // Atom parity and bond stereo require a stereo-aware correspondence, which
    // this helper cannot establish; refuse to guess for those records.
    if (A.properties.length || B.properties.length || A.atoms.some(function (a) { return !!a.parity; }) ||
        B.atoms.some(function (a) { return !!a.parity; }) ||
        A.bonds.concat(B.bonds).some(function (b) { return Number(String(b.tail || "").slice(0, 3)) !== 0; })) return null;
    var forward = [], reverse = [], used = {};
    for (var a = 0; a < A.atoms.length; a++) {
      if (A.atoms[a].el.toUpperCase() === "H") continue;
      var t = M.arr[a];
      if (!Number.isInteger(t) || !B.atoms[t] || used[t] || meta(A.atoms[a]) !== meta(B.atoms[t])) return null;
      forward[a] = t; reverse[t] = a; used[t] = true;
    }
    function hGroups(mol, parentMap) {
      var groups = {};
      mol.atoms.forEach(function (a, i) {
        if (a.el.toUpperCase() !== "H") return;
        var nb = mol.bonds.filter(function (b) { return b[0] === i + 1 || b[1] === i + 1; });
        if (nb.length !== 1 || nb[0][2] !== 1) return;
        var parent = (nb[0][0] === i + 1 ? nb[0][1] : nb[0][0]) - 1;
        var p = parentMap ? parentMap[parent] : parent;
        if (!Number.isInteger(p) || !mol.atoms[parent] || mol.atoms[parent].el.toUpperCase() === "H") return;
        var k = p + ":" + meta(a);
        (groups[k] || (groups[k] = [])).push(i);
      });
      return groups;
    }
    var h2 = hGroups(A, forward), h3 = hGroups(B, null);
    for (var k in h2) {
      var left = h2[k], right = h3[k] || [];
      // Incomplete/non-equivalent groups have no reliable H identity.
      if (left.length !== right.length) continue;
      for (var h = 0; h < left.length; h++) { forward[left[h]] = right[h]; reverse[right[h]] = left[h]; }
    }
    return (M.selectionMap = { key: key, forward: forward, reverse: reverse });
  } catch (e) { return null; }
}
function fMulerMap2D3D(a2) {
  var M = fMulerSelectFullMap();
  var i = M && Number.isInteger(a2) && a2 > 0 ? M.forward[a2 - 1] : null;
  return Number.isInteger(i) && i >= 0 ? i + 1 : -1;
}
function fMulerMap3D2D(a3) {
  var M = fMulerSelectFullMap();
  var i = M && Number.isInteger(a3) && a3 > 0 ? M.reverse[a3 - 1] : null;
  return Number.isInteger(i) && i >= 0 ? i + 1 : -1;
}
function fMulerSelectPairFor2D(a2) { return fMulerMap2D3D(a2); }
function fMulerSelectNormalized3D(a3) {
  var a2 = fMulerMap3D2D(a3);
  if (a2 < 1) return -1;
  var parent = fMulerQuizHydrogenParent(a2);
  return parent > 0 ? parent : a2;
}
function fMulerSelectBondPairFor2D(b2) {
  var b = Number.isInteger(b2) && bondList[b2 - 1];
  if (!b) return -1;
  var a = fMulerMap2D3D(b[0]), c = fMulerMap2D3D(b[1]);
  if (a < 1 || c < 1) return -1;
  for (var i = 0; i < bondList3D.length; i++) {
    var t = bondList3D[i];
    if (t[2] === b[2] && ((t[0] === a && t[1] === c) || (t[0] === c && t[1] === a))) return i + 1;
  }
  return -1;
}
function fMulerSelectBondPairFor3D(b3) {
  var b = Number.isInteger(b3) && bondList3D[b3 - 1];
  if (!b) return -1;
  var a = fMulerMap3D2D(b[0]), c = fMulerMap3D2D(b[1]);
  if (a < 1 || c < 1) return -1;
  for (var i = 0; i < bondList.length; i++) {
    var t = bondList[i];
    if (t[2] === b[2] && ((t[0] === a && t[1] === c) || (t[0] === c && t[1] === a))) return i + 1;
  }
  return -1;
}

// Public arrays remain the existing contract. Private contributors record
// origin, so removing one 3D H cannot remove a C still contributed by another
// 3D atom. A 2D deselection removes every contributor to that 2D membership.
function fMulerSelectContributors(sel) {
  var snapshot = JSON.stringify([sel.atoms2D, sel.bonds2D, sel.atoms3D, sel.bonds3D]);
  var key = fMulerSelectMolKey() + ":" + (window.MulerQuizTarget || "");
  var c = sel._contributors;
  if (!c || c.key !== key || c.snapshot !== snapshot) {
    c = sel._contributors = { key: key, a2: sel.atoms2D.slice(), b2: sel.bonds2D.slice(), a3: [], b3: [] };
  }
  return c;
}
function fMulerSelectRebuildMirrors() {
  var sel = fMulerSelectState();
  if (!sel) return;
  var c = fMulerSelectContributors(sel);
  var a2 = c.a2.slice(), b2 = c.b2.slice(), a3 = c.a3.slice(), b3 = c.b3.slice();
  function add(out, n) { if (n > 0 && out.indexOf(n) < 0) out.push(n); }
  c.a3.forEach(function (a) { add(a2, fMulerSelectNormalized3D(a)); });
  c.b3.forEach(function (b) { add(b2, fMulerSelectBondPairFor3D(b)); });
  c.a2.forEach(function (a) { add(a3, fMulerSelectPairFor2D(a)); });
  c.b2.forEach(function (b) { add(b3, fMulerSelectBondPairFor2D(b)); });
  sel.atoms2D = a2; sel.bonds2D = b2; sel.atoms3D = a3; sel.bonds3D = b3;
  c.snapshot = JSON.stringify([a2, b2, a3, b3]);
}
function fMulerSelect3DFeedback() {
  var en = typeof fMulerLang === "function" && fMulerLang() === "en";
  var msg = en ? "This 3D pick has no reliable counterpart in this 2D form. Select the visible 2D atoms or bonds."
    : "Η επιλογή 3D δεν έχει ασφαλή αντιστοίχιση σε αυτή τη μορφή 2D. Επίλεξε τα ορατά άτομα ή τους δεσμούς στο 2D.";
  var el = typeof fMulerQuizVerdictEl === "function" ? fMulerQuizVerdictEl() : null;
  if (el) { el.textContent = msg; el.style.display = ""; el.className = "mulerQuiz-wrong"; }
  else if (typeof fScenarioToast === "function") fScenarioToast(msg);
}
function fMulerSelectQuiz3DBlocked(sel) {
  return !!(window.MulerQuizTarget && sel &&
    (sel.atoms3D.some(function (a) { return fMulerSelectNormalized3D(a) < 1; }) ||
     sel.bonds3D.some(function (b) { return fMulerSelectBondPairFor3D(b) < 1; })));
}
function fMulerSelectToggle(px) {
  try {
    var sel = fMulerSelectState();
    if (!sel || !px) return;
    var c = fMulerSelectContributors(sel);
    if (px.kind === "atom" || px.kind === "fragment") {
      var picks = px.kind === "atom" ? [px.atom] : (px.atoms || []).slice();
      if (!picks.length || picks.some(function (a) { return !Number.isInteger(a) || a < 1 || a > allAtomsTypeList.length; })) return;
      var removing = picks.every(function (a) { return sel.atoms2D.indexOf(a) >= 0; });
      c.b2 = []; c.b3 = [];
      if (removing) {
        c.a2 = c.a2.filter(function (a) { return picks.indexOf(a) < 0; });
        c.a3 = c.a3.filter(function (a) { return picks.indexOf(fMulerSelectNormalized3D(a)) < 0; });
      } else picks.forEach(function (a) { if (c.a2.indexOf(a) < 0) c.a2.push(a); });
      sel.groups = [{ heavy: px.kind === "atom" ? px.atom : null, members: picks.slice(), compacted: px.kind === "fragment" }];
    } else if (px.kind === "bond") {
      var b = px.bond;
      if (!Number.isInteger(b) || b < 1 || b > bondList.length) return;
      var remove = sel.bonds2D.indexOf(b) >= 0;
      c.a2 = []; c.a3 = [];
      if (remove) {
        c.b2 = c.b2.filter(function (v) { return v !== b; });
        c.b3 = c.b3.filter(function (v) { return fMulerSelectBondPairFor3D(v) !== b; });
      } else if (c.b2.indexOf(b) < 0) c.b2.push(b);
      sel.groups = [];
    } else return;
    // Keep the ledger authoritative while rebuilding its public mirrors.
    c.snapshot = JSON.stringify([sel.atoms2D, sel.bonds2D, sel.atoms3D, sel.bonds3D]);
    fMulerSelectRebuildMirrors();
  } catch (e) {}
  try { fMulerSelectClear3DIfEmpty(); } catch (eC) {}
  try { fMulerQuizRefresh(); } catch (eQ) {}
}
function fMulerSelectCallbackIndex(map, field) {
  if (map == null) return null;
  var n = null;
  try { if (typeof map.get === "function") n = map.get(field); else if (typeof map === "object") n = map[field]; } catch (e) {}
  if (n != null) return Number(n);
  var m = String(map).match(new RegExp("\\b" + field + "\\s*[=:]\\s*(-?\\d+(?:\\.\\d+)?)"));
  return m ? Number(m[1]) : null;
}
window.__mulerPickCb = function (htmlName, strInfo, atomIndex, map) {
  try {
    if (!fMulerSelectActive() || window.MulerDraft || fMulerSelectPresenting() || !fMuler3DModelReady()) return;
    var appletName = String(jmolAppletNomeclature._id || "jmolAppletNomeclature");
    if (String(htmlName) !== appletName || !Number.isInteger(atomIndex) || atomIndex === -1) return;
    var sel = fMulerSelectState();
    if (!sel) return;
    var c = fMulerSelectContributors(sel), a3 = -1, b3 = -1, a2 = -1, b2 = -1;
    if (atomIndex === -3) {
      var info;
      try { info = JSON.parse(String(strInfo)); } catch (eJ) { return; }
      if (!Array.isArray(info) || info[0] !== "bond" || typeof info[1] !== "string") return;
      var head = info[1].match(/^\s*(\d+)\b/), ends = info[1].match(/#(\d+)\b/g) || [];
      if (!head || ends.length !== 2) return;
      b3 = Number(head[1]);
      var e1 = Number(ends[0].slice(1)), e2 = Number(ends[1].slice(1));
      var bond = bondList3D[b3 - 1], mi = fMulerSelectCallbackIndex(map, "index"), order = fMulerSelectCallbackIndex(map, "order");
      if (!Number.isInteger(b3) || b3 < 1 || !bond || e1 < 1 || e2 < 1 || e1 > allAtomsTypeList3D.length || e2 > allAtomsTypeList3D.length ||
          !((bond[0] === e1 && bond[1] === e2) || (bond[0] === e2 && bond[1] === e1)) ||
          (mi !== null && mi !== b3 - 1) || (order !== null && order !== bond[2])) return;
      if (window.MulerQuizTarget && fMulerSelectPurpose() !== "bond") return;
      b2 = fMulerSelectBondPairFor3D(b3);
      if (window.MulerQuizTarget && b2 < 1) { window.__muler3DPickSeen = true; window.__muler3DSilentT = 0; fMulerSelect3DFeedback(); return; }
      var wasBond = sel.bonds3D.indexOf(b3) >= 0;
      c.a2 = []; c.a3 = [];
      if (wasBond) { c.b3 = c.b3.filter(function (b) { return b !== b3; }); c.b2 = c.b2.filter(function (b) { return fMulerSelectBondPairFor2D(b) !== b3; }); }
      else c.b3.push(b3);
      sel.groups = [];
    } else {
      if (atomIndex < 0 || atomIndex >= allAtomsTypeList3D.length || (typeof strInfo === "string" && /^\s*\["bond"/.test(strInfo))) return;
      var ai = fMulerSelectCallbackIndex(map, "index"), hashes = String(strInfo || "").match(/#(\d+)\b/g) || [];
      if ((ai !== null && ai !== atomIndex) || (hashes.length && (hashes.length !== 1 || Number(hashes[0].slice(1)) !== atomIndex + 1))) return;
      a3 = atomIndex + 1;
      a2 = fMulerSelectNormalized3D(a3);
      if (window.MulerQuizTarget && a2 < 1) { window.__muler3DPickSeen = true; window.__muler3DSilentT = 0; fMulerSelect3DFeedback(); return; }
      var wasAtom = sel.atoms3D.indexOf(a3) >= 0;
      c.b2 = []; c.b3 = [];
      if (wasAtom) {
        c.a3 = c.a3.filter(function (a) { return a !== a3; });
        c.a2 = c.a2.filter(function (a) { return fMulerSelectPairFor2D(a) !== a3; });
      } else c.a3.push(a3);
      sel.groups = a2 > 0 ? [{ heavy: a2, members: [a2] }] : [];
    }
    window.__muler3DPickSeen = true; window.__muler3DSilentT = 0;
    c.snapshot = JSON.stringify([sel.atoms2D, sel.bonds2D, sel.atoms3D, sel.bonds3D]);
    fMulerSelectRebuildMirrors();
  } catch (e) { return; }
  try { fMulerSelectClear3DIfEmpty(); } catch (eC) {}
  try { fMulerQuizRefresh(); } catch (eQ) {}
  try { fMulerSelectRepaint(); } catch (eR) {}
  try { fUpdateSVG(); } catch (eU) {}
};

// 3D selection paint (cyan): full rebuild from state — JSmol `select`
// replaces (never accumulates), so native accumulation cannot skew paint.
// Empty state is a no-op (never auto-reset); the explicit clear path owns
// that, so a reward-green live under an armed-but-empty state is never
// wiped. Skipped when select mode is off (classic paths own the viewer)
// and in Present (component-only discipline, state kept).
function fMulerSelectPush3D() {
  try {
    if (!fMuler3DModelReady() || window.MulerDraft || fMulerSelectPresenting()) return;
    if (!(typeof fMulerSelectActive === "function" && fMulerSelectActive())) return;
    if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return;
    if (typeof fJSmolLive === "function" && !fJSmolLive()) return;
    if (typeof jmolAppletNomeclature === "undefined" || !jmolAppletNomeclature) return;
    var sel = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null;
    if (!sel) return;
    var set = {}, out = [];
    var push = function (a) { try { if (typeof a === "number" && a > 0 && !set[a]) { set[a] = true; out.push(a); } } catch (eP) {} };
    try {
      var sa = Array.isArray(sel.atoms3D) ? sel.atoms3D : [];
      for (var i = 0; i < sa.length; i++) push(sa[i]);
      var sb = Array.isArray(sel.bonds3D) ? sel.bonds3D : [];
      if (sb.length && typeof bondList3D !== "undefined" && bondList3D) {
        for (var j = 0; j < sb.length; j++) {
          var bl = bondList3D[sb[j] - 1];
          if (!bl) continue;
          push(bl[0]); push(bl[1]);
        }
      }
    } catch (eS) {}
    if (!out.length) return;
    var cyan = "X7DDFFF";
    try {
      if (typeof MULER_SELECT_CYAN === "string" && /^#[0-9a-fA-F]{6}$/.test(MULER_SELECT_CYAN)) cyan = "X" + MULER_SELECT_CYAN.slice(1).toUpperCase();
    } catch (eC) {}
    out.sort(function (a, b) { return a - b; });
    var arg = "select ";
    for (var k = 0; k < out.length; k++) arg += (k ? "," : "") + "atomno=" + out[k];
    var script = "select all; selectionHalos off; color bonds none; color atoms none;" + arg + ";";
    script += "color selectionHalos [" + cyan + "]; selectionHalos on; color atoms [" + cyan + "];";
    try {
      if (typeof bondList3D !== "undefined" && bondList3D) {
        for (var m = 0; m < bondList3D.length; m++) {
          var mb = bondList3D[m];
          if (!mb) continue;
          // Bond picks own exact bond identities. Their endpoint union may
          // also contain both ends of an unselected bridge between two picks.
          // Atom picks retain the existing both-endpoints bond paint policy.
          if (sb.length ? sb.indexOf(m + 1) >= 0 : set[mb[0]] && set[mb[1]]) script += "select atomno=" + mb[0] + ", atomno=" + mb[1] + "; color bond [" + cyan + "];";
        }
      }
    } catch (eB) {}
    // Halos follow the current selection (not color): the bond loop above
    // leaves only the last pair selected, so re-select the full picked set
    // or halos would cover just those two atoms.
    script += arg + ";";
    if (typeof fJSmolScript === "function") fJSmolScript(jmolAppletNomeclature, script);
    try { JmolSelection = arg; } catch (eJ) {}
  } catch (e) {}
}

// Explicit 3D selection-erase. Disarm calls it directly (the mode flag is
// already off there, so the guarded clear would skip); armed contexts use
// the guarded clear inside fMulerSelectClear.
function fMulerSelectClear3DPaint() {
  try {
    if (!fMuler3DModelReady() || window.MulerDraft || fMulerSelectPresenting()) return;
    if (typeof fJSmolLive === "function" && !fJSmolLive()) return;
    if (typeof jmolAppletNomeclature === "undefined" || !jmolAppletNomeclature) return;
    if (typeof fJSmolScript === "function") fJSmolScript(jmolAppletNomeclature, "select all; selectionHalos off; color bonds none; color atoms none;");
    try { JmolSelection = "select none"; } catch (eJ) {}
  } catch (e) {}
}

// Toggle-to-empty 3D erase. Push3D no-ops on empty state (reward-green
// protection), so a toggle that empties the pick must erase explicitly.
// Called before quiz refresh (the green is painted after, so always safe).
function fMulerSelectClear3DIfEmpty() {
  try {
    var sel = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null;
    if (!sel) return;
    var empty = true;
    try {
      empty = !(Array.isArray(sel.atoms3D) && sel.atoms3D.length) &&
              !(Array.isArray(sel.bonds3D) && sel.bonds3D.length);
    } catch (eE) { empty = false; }
    if (empty && typeof fMulerSelectClear3DPaint === "function") fMulerSelectClear3DPaint();
  } catch (e) {}
}

// Picking-state script for the current mode: armed (molecule set, no draft,
// no Present) enables atom picking + bond picking (bond clicks report via
// the -3 payload; without the flag they are silent) + the page callback.
// Everything else restores picking OFF and the bond default. The callback
// stays registered (JS guards ignore it when disarmed). fLoadMol3D appends
// this to the load script so the init-spt `picking OFF` cannot override an
// armed session.
function fMulerSelectPickingScript() {
  try {
    var armed = false;
    try { armed = (typeof fMulerSelectActive === "function" && fMulerSelectActive()); } catch (eA) { armed = false; }
    try { if (typeof window !== "undefined" && window.MulerDraft) armed = false; } catch (eD) {}
    try { if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) armed = false; } catch (eP) {}
    try { if (typeof selectedMol === "undefined" || !selectedMol) armed = false; } catch (eM) {}
    if (!fMuler3DModelReady()) armed = false;
    if (armed) return 'set pickCallback "' + fMuler3DModel.pickCallback + '"; set picking atom; set bondPicking true;';
    return "set picking OFF; set bondPicking false;";
  } catch (e) { return ""; }
}
function fMulerSelectSync3DPicking() {
  try {
    if (!fMuler3DModelReady() || window.MulerDraft) return;
    if (typeof fJSmolLive === "function" && !fJSmolLive()) return;
    if (typeof jmolAppletNomeclature === "undefined" || !jmolAppletNomeclature) return;
    var s = "";
    try { s = (typeof fMulerSelectPickingScript === "function") ? fMulerSelectPickingScript() : ""; } catch (eS) { s = ""; }
    if (!s || fMuler3DModel.picking === s) return;
    fMuler3DModel.picking = s;
    if (typeof fJSmolScript === "function") fJSmolScript(jmolAppletNomeclature, s);
  } catch (e) {}
}

// Quiz target registry (v56 1C, main chain first): component mode →
// atom-set resolver. Later phases add FG/branch resolvers (incl. bond-aware
// ones) without touching the dispatch, compare, or paint below.
var MULER_QUIZ_TARGET_RESOLVERS = { compCarbonsCount: fMulerMainChainResolved, compSuffix: fMulerSuffixResolved, commonEther: fMulerEtherResolved, esterEster: fMulerEsterResolved, compEndNumber: fMulerEndNumberResolved, compSuffixLocants: fMulerSuffixResolved, compBondPos: fMulerBondPosResolved, compNumber1: fMulerNumber1Resolved, compBondType: fMulerBondTypeResolved, compBondType2: fMulerBondType2Resolved };

// Main-chain resolution shared with the highlight path (same stored-data vs
// algorithmic rule) so quiz and green can never disagree on the answer.
function fMulerMainChainResolved() {
  try {
    if (typeof selectedMol === "undefined" || !selectedMol || typeof nameExamples === "undefined" || !nameExamples[selectedMol]) return [];
    var suffix = "_Condensed";
    try { if (typeof fMainChainKeySuffix === "function") suffix = fMainChainKeySuffix(); } catch (eS) {}
    var stored = nameExamples[selectedMol]["mainChain" + suffix];
    var chain = ((typeof mainChainMode !== "undefined" && mainChainMode === "algorithmic") || !Array.isArray(stored) || !stored.length)
      ? (((typeof mainChainAtomsList !== "undefined" && Array.isArray(mainChainAtomsList)) ? mainChainAtomsList : []))
      : stored;
    return (chain || []).slice();
  } catch (e) { return []; }
}

// FG quiz resolvers (v56 1C suffix phase): green-faithful atom sets — heavy
// fragment atoms plus H exactly where green paints it (alcohol/amine hetero H,
// acid OH hydrogen, aldehyde C-H; bondList-driven, so condensed/skeletal with
// no explicit H stay heavy-only). Ether/ketone/nitro/cyanide/halogen/ester
// stay H-free like the highlight.
// Source of truth is the green path: compSuffix paints fHighlightFG() with
// FGno undefined (single FG) or 2 (principal group of several), commonEther
// paints the whole C-O-C via fHighlightFG(), esterEster paints
// fGetEsterGroupFragment(). The exact reward replays that green, so quiz and
// reward never disagree.
// Hydrocarbon taxonomy (-ιο suffix, alkyl halides) has no highlight atoms,
// so the resolver returns [] and the arm gate falls through to classic.
function fMulerFGInstances() {
  try {
    if (typeof functionalGroupObj === "undefined" || !functionalGroupObj) return [];
    var fgKeys = Object.keys(functionalGroupObj).filter(function (k) { return k !== "hydrocarbon"; });
    if (!fgKeys.length) return [];
    var instances = [];
    for (var k = 0; k < fgKeys.length; k++) {
      var heteroEls = Object.keys(functionalGroupObj[fgKeys[k]]);
      for (var e = 0; e < heteroEls.length; e++) instances.push([fgKeys[k], heteroEls[e]]);
    }
    var order2D = ["carboxylicAcid", "ester", "cyanide", "aldehyde", "ketone", "alcohol", "amine", "nitro", "ether"];
    var halOrder = [];
    try { halOrder = Object.keys(nameMainCompObj3.halogen.substitute); } catch (eH) { halOrder = []; }
    instances.sort(function (a, b) {
      if (a[0] === "halogen" && b[0] === "halogen") return halOrder.indexOf(a[1]) - halOrder.indexOf(b[1]);
      return order2D.indexOf(b[0]) - order2D.indexOf(a[0]);
    });
    return instances;
  } catch (e) { return []; }
}

function fMulerFGHeavyAtoms(FGno) {
  try {
    var instances = (typeof fMulerFGInstances === "function") ? fMulerFGInstances() : [];
    if (!instances.length) return [];
    var targets = (FGno === undefined) ? instances : (instances[FGno - 1] ? [instances[FGno - 1]] : []);
    if (!targets.length) return [];
    var out = [];
    var push = function (a1) { if (typeof a1 === "number" && a1 > 0 && out.indexOf(a1) < 0) out.push(a1); };
    // H donors mirror the green H rules exactly (alcohol/amine hetero H, acid
    // OH hydrogen, aldehyde C-H). The bondList scan below adds only modeled H,
    // so condensed/skeletal (no explicit H) stay heavy-only with no branches.
    var hDonors = [];
    var donor = function (a0) { if (typeof a0 === "number" && a0 >= 0 && hDonors.indexOf(a0) < 0) hDonors.push(a0); };
    for (var t = 0; t < targets.length; t++) {
      var fgKey = targets[t][0], heteroEl = targets[t][1];
      var heteroList = functionalGroupObj[fgKey][heteroEl];
      for (var i = 0; i < heteroList.length; i++) {
        var entry = heteroList[i];
        if (Array.isArray(entry)) {
          if (fgKey === "ester") {
            var triad = (typeof fGetEsterTriad === "function") ? fGetEsterTriad() : null;
            if (triad) for (var e2 = 0; e2 < triad.length; e2++) push(triad[e2]);
            continue;
          }
          var ohIdx = entry[0], coIdx = entry[1];
          push(ohIdx + 1); push(coIdx + 1);
          donor(ohIdx);
          try {
            if (Array.isArray(atomConnectivityList[ohIdx])) push(atomConnectivityList[ohIdx][0] + 1);
          } catch (eA) {}
        } else {
          var hIdx = entry;
          if (fgKey === "aldehyde") {
            push(hIdx + 1);
            try {
              if (Array.isArray(atomConnectivityList[hIdx]) && atomConnectivityList[hIdx].length) {
                push(atomConnectivityList[hIdx][0] + 1);
                donor(atomConnectivityList[hIdx][0]);
              }
            } catch (eC) {}
          } else if (fgKey === "ketone") {
            push(hIdx + 1);
            try {
              var carbC = Array.isArray(atomConnectivityList[hIdx]) ? atomConnectivityList[hIdx][0] : undefined;
              if (carbC !== undefined) {
                push(carbC + 1);
                var nbrs = atomConnectivityList[carbC] || [];
                for (var n = 0; n < nbrs.length; n++) {
                  try { if (String(allAtomsTypeList[nbrs[n]] || "").toUpperCase() === "C") push(nbrs[n] + 1); } catch (eN) {}
                }
              }
            } catch (eK) {}
          } else if (fgKey === "nitro") {
            push(hIdx + 1);
            try {
              var on = atomConnectivityList[hIdx] || [];
              for (var o = 0; o < on.length; o++) {
                try { if (String(allAtomsTypeList[on[o]] || "").toUpperCase() === "O") push(on[o] + 1); } catch (eO) {}
              }
            } catch (eNO) {}
          } else if (fgKey === "ether") {
            push(hIdx + 1);
            try {
              var ec = (atomConnectivityList[hIdx] || []).filter(function (nn) {
                try { return String(allAtomsTypeList[nn] || "").toUpperCase() === "C"; } catch (eF) { return false; }
              });
              for (var c = 0; c < ec.length; c++) push(ec[c] + 1);
            } catch (eE) {}
          } else if (fgKey === "cyanide") {
            push(hIdx + 1);
            try {
              var cn = atomConnectivityList[hIdx] || [];
              for (var u = 0; u < cn.length; u++) push(cn[u] + 1);
            } catch (eCN) {}
          } else {
            push(hIdx + 1);
            if (fgKey === "alcohol" || fgKey === "amine") donor(hIdx);
            if (fgKey !== "alcohol" && fgKey !== "amine" && fgKey !== "halogen") {
              try {
                var gn = atomConnectivityList[hIdx] || [];
                for (var g = 0; g < gn.length; g++) push(gn[g] + 1);
              } catch (eG) {}
            }
          }
        }
      }
    }
    // Modeled H only (same atoms green paints): each donor contributes its
    // bonded H atoms. No explicit H in the model (condensed/skeletal) → noop.
    try {
      if (hDonors.length && typeof bondList !== "undefined" && bondList && typeof allAtomsTypeList !== "undefined" && allAtomsTypeList) {
        var donorSet = {};
        for (var d = 0; d < hDonors.length; d++) donorSet[hDonors[d] + 1] = true;
        for (var b = 0; b < bondList.length; b++) {
          if (!bondList[b]) continue;
          var ba1 = bondList[b][0], ba2 = bondList[b][1];
          if (donorSet[ba1] && String(allAtomsTypeList[ba2 - 1] || "").toUpperCase() === "H") push(ba2);
          else if (donorSet[ba2] && String(allAtomsTypeList[ba1 - 1] || "").toUpperCase() === "H") push(ba1);
        }
      }
    } catch (eH) {}
    out.sort(function (a, b) { return a - b; });
    return out;
  } catch (e) { return []; }
}

function fMulerSuffixResolved() {
  try {
    if (typeof molTaxonomy !== "undefined" && molTaxonomy == "Υδρογονάνθρακες") return [];
    if (typeof functionalGroupObj === "undefined" || !functionalGroupObj) return [];
    var nKeys = Object.keys(functionalGroupObj).length;
    var FGno = nKeys > 1 ? 2 : undefined;
    return ((typeof fMulerFGHeavyAtoms === "function") ? fMulerFGHeavyAtoms(FGno) : []) || [];
  } catch (e) { return []; }
}

function fMulerEtherResolved() {
  try {
    return ((typeof fMulerFGHeavyAtoms === "function") ? fMulerFGHeavyAtoms(undefined) : []) || [];
  } catch (e) { return []; }
}

function fMulerEsterResolved() {
  try {
    if (typeof fGetEsterGroupFragment !== "function") return [];
    var frag = fGetEsterGroupFragment() || [];
    return frag.slice();
  } catch (e) { return []; }
}

// Bond quiz resolvers (v56 1B bond phase): the bonded heavy atoms. Mirror the
// green path exactly — fHighlightMultiBonds(1) paints the double bonds when
// any exist, else the triple bonds; fHighlightMultiBonds(2) paints triples.
function fMulerMultiBondAtoms(order) {
  try {
    var out = [];
    if (typeof multiBondListCC === "undefined" || !multiBondListCC) return [];
    if (typeof bondList === "undefined" || !bondList) return [];
    for (var i = 0; i < multiBondListCC.length; i++) {
      var b = multiBondListCC[i];
      var bl = bondList[b - 1];
      if (!bl || bl[2] !== order) continue;
      if (out.indexOf(bl[0]) < 0) out.push(bl[0]);
      if (out.indexOf(bl[1]) < 0) out.push(bl[1]);
    }
    out.sort(function (a, b) { return a - b; });
    return out;
  } catch (e) { return []; }
}

function fMulerBondAtomsPos1() {
  try {
    var hasD = false;
    try { hasD = !!(typeof multiBondsObj !== "undefined" && multiBondsObj && multiBondsObj.CCd && multiBondsObj.CCd.length > 0); } catch (eD) { hasD = false; }
    return ((typeof fMulerMultiBondAtoms === "function") ? fMulerMultiBondAtoms(hasD ? 2 : 3) : []) || [];
  } catch (e) { return []; }
}

function fMulerBondAtomsPos2() {
  try {
    return ((typeof fMulerMultiBondAtoms === "function") ? fMulerMultiBondAtoms(3) : []) || [];
  } catch (e) { return []; }
}

// Single C–C bonds (order 1, both ends carbon — never C–H), molecule-wide or
// scoped to the ester acid chain, mirroring fHighlightSingleBondsCC.
function fMulerSingleBondAtoms() {
  try {
    var scope = null;
    try {
      if ((typeof fIsSingleEster === "function") && fIsSingleEster() &&
          typeof fGetEsterAcidChain === "function") scope = fGetEsterAcidChain() || null;
    } catch (eS) { scope = null; }
    var set = null;
    if (Array.isArray(scope) && scope.length) {
      set = {};
      for (var s = 0; s < scope.length; s++) set[scope[s]] = true;
    }
    if (typeof bondList === "undefined" || !bondList || typeof allAtomsTypeList === "undefined" || !allAtomsTypeList) return [];
    var out = [];
    for (var b = 0; b < bondList.length; b++) {
      if (!bondList[b] || bondList[b][2] !== 1) continue;
      var a1 = bondList[b][0], a2 = bondList[b][1];
      if (String(allAtomsTypeList[a1 - 1] || "").toUpperCase() !== "C" ||
          String(allAtomsTypeList[a2 - 1] || "").toUpperCase() !== "C") continue;
      if (set && (!set[a1] || !set[a2])) continue;
      if (out.indexOf(a1) < 0) out.push(a1);
      if (out.indexOf(a2) < 0) out.push(a2);
    }
    out.sort(function (a, b) { return a - b; });
    return out;
  } catch (e) { return []; }
}

// Quiz-effective atom set: picked atoms plus the endpoints of picked bonds.
// Bond clicks in a bond quiz count their two atoms, so a bond line and its
// labels are interchangeable ways to pick the same atoms.
function fMulerQuizEffectiveAtoms(selAtoms, selBonds) {
  try {
    var set = {}, out = [];
    var push = function (a) { if (typeof a === "number" && a > 0 && !set[a]) { set[a] = true; out.push(a); } };
    var sa = Array.isArray(selAtoms) ? selAtoms : [];
    for (var i = 0; i < sa.length; i++) push(sa[i]);
    var sb = Array.isArray(selBonds) ? selBonds : [];
    if (sb.length && typeof bondList !== "undefined" && bondList) {
      for (var j = 0; j < sb.length; j++) {
        var bl = bondList[sb[j] - 1];
        if (!bl) continue;
        push(bl[0]); push(bl[1]);
      }
    }
    out.sort(function (a, b) { return a - b; });
    return out;
  } catch (e) { return Array.isArray(selAtoms) ? selAtoms.slice() : []; }
}

// compBondType: the named multiplicity's atoms. "αν" (only singles) quizzes
// every single C–C bond (reward paints that set); other infixes take the
// multi-bond atoms (doubles preferred, else triples — same as the green).
function fMulerBondTypeResolved() {
  try {
    var s6 = "";
    try { s6 = (typeof nameComponentsList !== "undefined" && nameComponentsList) ? (nameComponentsList[6] || "") : ""; } catch (e6) { s6 = ""; }
    if (s6 === "αν" || s6 === "άν") {
      return ((typeof fMulerSingleBondAtoms === "function") ? fMulerSingleBondAtoms() : []) || [];
    }
    if (s6 === "εν" || s6 === "έν" || s6 === "διέν" || s6 === "διεν" || s6 === "ίν" || s6 === "ιν") {
      return ((typeof fMulerBondAtomsPos1 === "function") ? fMulerBondAtomsPos1() : []) || [];
    }
    return [];
  } catch (e) { return []; }
}

// compBondType2: mirrors the classic unconditional fHighlightMultiBonds(2)
// (triple bonds when two multiplicities exist).
function fMulerBondType2Resolved() {
  try {
    return ((typeof fMulerBondAtomsPos2 === "function") ? fMulerBondAtomsPos2() : []) || [];
  } catch (e) { return []; }
}

// Dual-use locant boxes (compBondPos / compEndNumber / compNumber1): bond
// atoms when the box holds a bond position, i.e. exactly when the FG
// resolver for that mode is empty. Keeps quiz and green in agreement by
// construction — one of the two always matches the classic paint.
function fMulerBondAtomsForMode(mode) {
  try {
    var fg = [];
    try {
      var r = (typeof MULER_QUIZ_TARGET_RESOLVERS !== "undefined" && MULER_QUIZ_TARGET_RESOLVERS) ? MULER_QUIZ_TARGET_RESOLVERS[mode] : null;
      if (typeof r === "function") fg = r() || [];
    } catch (eR) { fg = []; }
    if (fg.length) return [];
    if (mode === "compBondPos" || mode === "compNumber1") {
      return ((typeof fMulerBondAtomsPos1 === "function") ? fMulerBondAtomsPos1() : []) || [];
    }
    if (mode === "compEndNumber") {
      return ((typeof fMulerBondAtomsPos2 === "function") ? fMulerBondAtomsPos2() : []) || [];
    }
  } catch (e) {}
  return [];
}

// Branch quiz resolver: heavy atoms of the substituent / alkyl group behind
// the box, mirroring the green paint (fGetHydrocarbonBranchHighlight, with
// the mode passed explicitly so piece scoping and the compNumber2 first-group
// narrowing match the armed box even before nameAnalysisMode is restored).
// Heavy atoms only (branch H is invisible in condensed; the armed H→parent
// redirect keeps expanded picks forgiving). Single-ether alkoxy boxes defer
// to their commonAlkyl quiz home.
function fMulerBranchAtomsForMode(mode) {
  try {
    if (!mode || typeof mode !== "string") return [];
    var heavyOnly = function (arr) {
      var out = [];
      try {
        for (var i = 0; i < ((arr && arr.length) || 0); i++) {
          var a = arr[i];
          if (typeof a !== "number" || a <= 0) continue;
          try { if (typeof allAtomsTypeList !== "undefined" && allAtomsTypeList && String(allAtomsTypeList[a - 1] || "").toUpperCase() === "H") continue; } catch (eH) {}
          if (out.indexOf(a) < 0) out.push(a);
        }
      } catch (eL) {}
      out.sort(function (x, y) { return x - y; });
      return out;
    };
    if (mode === "commonAlkyl1" || mode === "commonAlkyl2") {
      try {
        var parts = (typeof fGetEtherCommonParts === "function") ? fGetEtherCommonParts() : null;
        var part = (parts && parts.parts) ? parts.parts[mode === "commonAlkyl1" ? 0 : 1] : null;
        return heavyOnly(part && part.chain ? part.chain : []);
      } catch (eP) { return []; }
    }
    if (mode === "esterAlkyl") {
      try {
        var alc = (typeof fGetEsterAlcoholChain === "function") ? fGetEsterAlcoholChain() : null;
        return heavyOnly(alc || []);
      } catch (eA) { return []; }
    }
    var slot = 0;
    if (/^compBranch(Sub|Loc)\d+$/.test(mode)) slot = 2;
    else if (mode === "compSecondSub2" || mode === "compNumber2") slot = 2;
    else if (mode === "compSecondSub1" || mode === "compNumber1") slot = 1;
    else return [];
    // An unmatched split piece must not fall back to the whole slot group:
    // without a resolved piece there is no sufficiently precise quiz target.
    try {
      var _pm = /^compBranch(Sub|Loc)(\d+)$/.exec(mode || "");
      if (_pm) {
        var _pp = (typeof fGetHydrocarbonBranchPiece === "function") ? fGetHydrocarbonBranchPiece(parseInt(_pm[2], 10)) : null;
        if (!_pp || !Array.isArray(_pp.members) || !_pp.members.length) return [];
      }
    } catch (eP) { return []; }
    // The classic highlighter falls back to the whole slot for an unmatched
    // split piece; that fallback is not a sufficiently precise quiz target.
    var piece = /^compBranch(Sub|Loc)(\d+)$/.exec(mode);
    if (piece && !fGetHydrocarbonBranchPiece(parseInt(piece[2], 10))) return [];
    // Ether slot groups include alkoxy prefixes, which the branch highlighter
    // filters out. A single-alkoxy selection quizzes the same atoms classic
    // paints (O + full alkoxy chain, heavy-only like other branch quizzes; H
    // via the armed H->parent redirect). A mixed slot cannot safely be indexed.
    if (functionalGroupsList.length === 1 && functionalGroupsList[0] === "ether") {
      var etherGroups = fEtherPrefixGroups();
      var selectedGroups = slot === 1 ? etherGroups.slice(0, 1) : etherGroups.slice(1);
      if (!selectedGroups.length) return [];
      if (selectedGroups.length === 1 && selectedGroups[0].kind === "alkoxy") {
        try {
          var _o1 = (typeof functionalGroupObj !== "undefined" && functionalGroupObj &&
            functionalGroupObj.ether && functionalGroupObj.ether.O) ? (functionalGroupObj.ether.O[0] + 1) : null;
          var _ach = (typeof fGetEtherAlkoxyChain === "function") ? fGetEtherAlkoxyChain() : null;
          var _arr = [];
          if (typeof _o1 === "number" && _o1 > 0) _arr.push(_o1);
          if (_ach && _ach.length) for (var _ai = 0; _ai < _ach.length; _ai++) _arr.push(_ach[_ai]);
          var _ho = heavyOnly(_arr);
          if (_ho.length) return _ho;
        } catch (eA) {}
        return [];
      }
      if (selectedGroups.some(function (group) { return group.kind !== "alkyl"; })) return [];
    }
    var g = null;
    try { g = (typeof fGetHydrocarbonBranchHighlight === "function") ? fGetHydrocarbonBranchHighlight(slot, mode) : null; } catch (eG) { g = null; }
    return heavyOnly(g && g.atoms ? g.atoms : []);
  } catch (e) { return []; }
}

// Secondary hetero prefix boxes ([bromo]/[2-], [nitro]/[2-], [hydroxy]/[2-],
// [amino]/[3-], [oxo]/...): the prefix group atoms, matching the classic
// fHighlightFG(1)/(2) green. Any hetero type qualifies; the prefix-name slot
// (s1/s3) must be non-empty, which is exactly disjoint from the registry
// loc paths (fMulerNumber1Resolved needs empty s1), so principal-FG boxes
// can never be shadowed. Gated on bearing-C locants (fMulerFGPositionAtoms),
// so a bond locant in the box falls through to the bond family instead.
// Slot 1 → compSecondSub1/compNumber1, slot 2 → compSecondSub2/compNumber2.
function fMulerHeteroPrefixAtomsForMode(mode) {
  try {
    var slot = 0;
    if (mode === "compSecondSub1" || mode === "compNumber1") slot = 1;
    else if (mode === "compSecondSub2" || mode === "compNumber2") slot = 2;
    else return [];
    try {
      var _nm = (typeof nameComponentsList !== "undefined" && nameComponentsList) ?
        (slot === 1 ? nameComponentsList[1] : nameComponentsList[3]) : null;
      if (_nm === null || _nm === undefined || String(_nm).length === 0) return [];
    } catch (eN) { return []; }
    var inst = null;
    try { inst = (typeof fMulerFGInstances === "function") ? fMulerFGInstances() : []; } catch (eI) { inst = []; }
    if (!inst || !inst[slot - 1]) return [];
    var atoms = [];
    try { atoms = ((typeof fMulerFGHeavyAtoms === "function") ? fMulerFGHeavyAtoms(slot) : []) || []; } catch (eA) { atoms = []; }
    if (!atoms.length) return [];
    try {
      var pos = (typeof fMulerFGPositionAtoms === "function") ? fMulerFGPositionAtoms(slot) : [];
      if (pos && pos.length && typeof fMulerBoxMatchesTarget === "function" && !fMulerBoxMatchesTarget(mode, pos)) return [];
    } catch (eG) {}
    atoms.sort(function (a, b) { return a - b; });
    return atoms;
  } catch (e) { return []; }
}

// Prerequisite state (v56 locant phase): per-molecule main-chain solves.
// Locant tasks show the chain numbering aid only for solved molecules.
function fMulerChainSolved() {
  try {
    if (typeof window === "undefined") return false;
    var m = (typeof selectedMol !== "undefined" && selectedMol) ? String(selectedMol) : "";
    if (!m) return false;
    var map = window.__mulerChainSolved;
    return !!(map && map[m] === true);
  } catch (e) { return false; }
}

// Mode → box id (mirrors the _modeToCompId table in fShowNameAnalysis plus
// the branch-piece fallback). Used by the chain→locant return flow.
function fMulerQuizBoxIdForMode(mode) {
  try {
    var map = {
      compNumber1: "comp0", compSecondSub1: "comp1", compNumber2: "comp2",
      compSecondSub2: "comp3", compBondPos: "comp4", compCarbonsCount: "comp5",
      compBondType: "comp6", compEndNumber: "comp7", compBondType2: "comp8",
      compSuffix: "comp9", compSuffixLocants: "comp9loc", compBranchSub1: "comp3",
      compBranchLoc2: "comp3loc", compBranchSub2: "comp3b", commonAlkyl1: "comp10",
      commonAlkyl2: "comp11", commonEther: "comp12", esterAlkyl: "comp10",
      esterEster: "comp11",
    };
    if (Object.prototype.hasOwnProperty.call(map, mode)) return map[mode];
    if (typeof fBranchPieceBoxId === "function") {
      var b = fBranchPieceBoxId(mode);
      if (b) return b;
    }
  } catch (e) {}
  return null;
}

// Principal FG position atoms (1-based) for the box/locant match gate — the
// carbons that carry the FG locant, not the full green paint set. Ketone green
// includes alpha carbons and alcohol green is O-only (no locant), so gating on
// paint atoms both over-matches (bond "3" via alpha C3 next to a 2-keto) and
// under-matches (OH "2-" via O with no chain locant). Bearing/carbonyl carbons
// only: ketone/aldehyde carbonyl C, acid carbonyl C, ester carbonyl C,
// alcohol/amine/halogen/nitro bearing C(s), ether both flanking Cs, cyanide
// nitrile C. Quiz/classic targets stay full (paint-faithful); only the gate
// narrows.
function fMulerFGPositionAtoms(FGno) {
  try {
    var inst = (typeof fMulerFGInstances === "function") ? fMulerFGInstances() : [];
    if (!inst.length) return [];
    var tgts = (FGno === undefined) ? inst : (inst[FGno - 1] ? [inst[FGno - 1]] : []);
    if (!tgts.length) return [];
    var out = [];
    var push = function (a1) { if (typeof a1 === "number" && a1 > 0 && out.indexOf(a1) < 0) out.push(a1); };
    var firstC = function (idx0) {
      try {
        var nbs = (typeof atomConnectivityList !== "undefined" && atomConnectivityList) ? atomConnectivityList[idx0] : null;
        if (!nbs) return [];
        var res = [];
        for (var i = 0; i < nbs.length; i++) {
          try { if (String(allAtomsTypeList[nbs[i]] || "").toUpperCase() === "C") res.push(nbs[i] + 1); } catch (eC) {}
        }
        return res;
      } catch (e) { return []; }
    };
    for (var t = 0; t < tgts.length; t++) {
      var fgKey = tgts[t][0], heteroEl = tgts[t][1];
      var hList = null;
      try { hList = functionalGroupObj[fgKey][heteroEl]; } catch (eH) { hList = null; }
      if (!hList) continue;
      for (var i = 0; i < hList.length; i++) {
        var entry = hList[i];
        if (Array.isArray(entry)) {
          if (fgKey === "ester") {
            try {
              var tri = (typeof fGetEsterTriad === "function") ? fGetEsterTriad() : null;
              if (tri && tri.length >= 2) { push(tri[1]); continue; }
            } catch (eT) {}
          }
          try {
            var coO = entry[1];
            var carb = (typeof atomConnectivityList !== "undefined" && atomConnectivityList) ? atomConnectivityList[coO] : null;
            var c0 = (carb && carb.length) ? carb[0] : null;
            if (typeof c0 === "number") push(c0 + 1);
          } catch (eA) {}
          continue;
        }
        var h0 = entry;
        if (fgKey === "ketone" || fgKey === "aldehyde") {
          try {
            var cc = (typeof atomConnectivityList !== "undefined" && atomConnectivityList) ? atomConnectivityList[h0] : null;
            if (cc && cc.length !== undefined && typeof cc[0] === "number") push(cc[0] + 1);
            else if (Array.isArray(cc) && cc.length) push(cc[0] + 1);
          } catch (eK) {}
        } else if (fgKey === "cyanide") {
          var ncs = firstC(h0);
          if (ncs.length) push(ncs[0]);
        } else if (fgKey === "ether") {
          var ecs = firstC(h0);
          for (var e2 = 0; e2 < ecs.length; e2++) push(ecs[e2]);
        } else {
          var bcs = firstC(h0);
          for (var b = 0; b < bcs.length; b++) push(bcs[b]);
        }
      }
    }
    out.sort(function (a, b) { return a - b; });
    return out;
  } catch (e) { return []; }
}

// Locant-box resolver for compBondPos: the same atoms the classic case paints
// green — the keto/OH group whenever the box holds its position: branched
// saturated ketone, alcohol-as-compBondPos, or a slot-{0,4,7} locant on a single
// alcohol/ketone (e.g. EN 2-πεντανόνη, 2-πεντανόλη). Multiple-bond positions
// belong to the bond family: [] falls through to classic.
function fMulerBondPosResolved() {
  try {
    var out = [];
    var allFG = function () {
      try { return ((typeof fMulerFGHeavyAtoms === "function") ? fMulerFGHeavyAtoms(undefined) : []) || []; }
      catch (eF) { return []; }
    };
    try { if ((typeof fBranchedSaturatedKetonePosition === "function") && fBranchedSaturatedKetonePosition()) out = allFG(); } catch (eB) {}
    if (!out.length) {
      try { if ((typeof fAlcoholOHNameComponent === "function") && fAlcoholOHNameComponent() === 'compBondPos') out = allFG(); } catch (eA) {}
    }
    if (!out.length && typeof functionalGroupsList !== "undefined" && functionalGroupsList && functionalGroupsList.length === 1 &&
        (functionalGroupsList[0] === 'ketone' || functionalGroupsList[0] === 'alcohol')) {
      var s4 = "", s0 = "", s7 = "";
      try {
        if (typeof nameComponentsList !== "undefined" && nameComponentsList) {
          s4 = nameComponentsList[4] || "";
          s0 = nameComponentsList[0] || "";
          s7 = nameComponentsList[7] || "";
        }
      } catch (e4) {}
      var stripLoc = function (t) { return String(t == null ? "" : t).replace(/^[-\s]+/, "").replace(/[-\s]+$/, ""); };
      if (/^\d/.test(stripLoc(s4)) || /^\d/.test(stripLoc(s0)) || /^\d/.test(stripLoc(s7))) out = allFG();
    }
    // Box must name the FG: a bond locant in an FG-position box (e.g. a
    // triple-bond number where the OH position was expected) belongs to the
    // bond family, so an unmatched box falls through instead of quizzing FG.
    // Gate on principal position atoms (carbonyl/bearing C), not the full
    // paint set (ketone alpha Cs over-match, OH O under-matches).
    if (out.length && typeof fMulerBoxMatchesTarget === "function") {
      try {
        var _pos = (typeof fMulerFGPositionAtoms === "function") ? fMulerFGPositionAtoms(undefined) : out;
        if (!fMulerBoxMatchesTarget("compBondPos", (_pos && _pos.length) ? _pos : out)) return [];
      } catch (eG) {}
    }
    return out;
  } catch (e) { return []; }
}

// Locant-box resolver for compNumber1: the same atoms the classic case paints
// green — the principal FG (fHighlightFG(), all instances) in the saturated
// fallthrough (e.g. GR 2-πεντανόνη in box comp0). Branch groups, secondary
// positions and multiple-bond infixes belong to later families: [].
function fMulerNumber1Resolved() {
  try {
    var bg = null;
    try { bg = (typeof fGetHydrocarbonBranchGroup === "function") ? fGetHydrocarbonBranchGroup(1) : null; } catch (eB) { bg = null; }
    if (bg) return [];
    var s1 = null;
    try { s1 = (typeof nameComponentsList !== "undefined" && nameComponentsList) ? nameComponentsList[1] : null; } catch (e1) { s1 = null; }
    if (s1 !== null && s1 !== undefined && s1 !== "" && s1.length > 0) return [];
    var s0 = "";
    try { s0 = (typeof nameComponentsList !== "undefined" && nameComponentsList) ? (nameComponentsList[0] || "") : ""; } catch (e0) { s0 = ""; }
    var stripOwnLoc = function (t) { return String(t == null ? "" : t).replace(/^[-\s]+/, "").replace(/[-\s]+$/, ""); };
    if (!/^\d/.test(stripOwnLoc(s0))) return [];
    var s6 = "";
    try { s6 = (typeof nameComponentsList !== "undefined" && nameComponentsList) ? nameComponentsList[6] : ""; } catch (e6) { s6 = ""; }
    if (s6 !== "άν" && s6 !== "αν") return [];
    if (typeof functionalGroupObj === "undefined" || !functionalGroupObj) return [];
    var keys = Object.keys(functionalGroupObj).filter(function (k) { return k !== "hydrocarbon"; });
    if (!keys.length) return [];
    var out1 = ((typeof fMulerFGHeavyAtoms === "function") ? fMulerFGHeavyAtoms(undefined) : []) || [];
    if (out1.length && typeof fMulerBoxMatchesTarget === "function") {
      try {
        var _pos1 = (typeof fMulerFGPositionAtoms === "function") ? fMulerFGPositionAtoms(undefined) : out1;
        if (!fMulerBoxMatchesTarget("compNumber1", (_pos1 && _pos1.length) ? _pos1 : out1)) return [];
      } catch (eG1) {}
    }
    return out1;
  } catch (e) { return []; }
}

// Locant-box resolver for compEndNumber: the same atoms the classic case
// paints — all FG instances (fHighlightFG(), FGno undefined) in the ketone,
// alcohol and empty-suffix branches. The triple-bond-position branch belongs
// to the bond family: [] makes the arm gate fall through to classic.
function fMulerEndNumberResolved() {
  try {
    var out = [];
    var allFG = function () {
      try { return ((typeof fMulerFGHeavyAtoms === "function") ? fMulerFGHeavyAtoms(undefined) : []) || []; }
      catch (eF) { return []; }
    };
    if (typeof functionalGroupsList !== "undefined" && functionalGroupsList &&
        functionalGroupsList.length === 1 && functionalGroupsList[0] === 'ketone' &&
        (typeof fIsAcyclicKetoneGraph === "function") && fIsAcyclicKetoneGraph(atomConnectivityList, allAtomsTypeList, bondList) &&
        (typeof fIsAcyclicSaturatedMonoketoneGraph === "function") && !fIsAcyclicSaturatedMonoketoneGraph(atomConnectivityList, allAtomsTypeList, bondList) &&
        (typeof nameComponentsList !== "undefined" && nameComponentsList && nameComponentsList[8] && nameComponentsList[8].length === 0)) {
      out = allFG();
    } else {
      var ohIsEnd = false;
      try { ohIsEnd = (typeof fAlcoholOHNameComponent === "function") && fAlcoholOHNameComponent() === 'compEndNumber'; } catch (eO) { ohIsEnd = false; }
      var empty8 = true;
      try { empty8 = (typeof nameComponentsList === "undefined" || !nameComponentsList[8] || nameComponentsList[8].length === 0); } catch (e8) { empty8 = true; }
      if (ohIsEnd || empty8) {
        out = allFG();
      }
    }
    // Box must name the FG: a bond locant here belongs to the bond family.
    // Gate on principal position atoms, not the full paint set.
    if (out.length && typeof fMulerBoxMatchesTarget === "function") {
      try {
        var _posE = (typeof fMulerFGPositionAtoms === "function") ? fMulerFGPositionAtoms(undefined) : out;
        if (!fMulerBoxMatchesTarget("compEndNumber", (_posE && _posE.length) ? _posE : out)) return [];
      } catch (eGE) {}
    }
    return out;
  } catch (e) { return []; }
}

function fMulerQuizTargetSet() {
  try {
    var t = (typeof window !== "undefined") ? window.MulerQuizTarget : null;
    if (!t) return [];
    if (typeof fMulerQuizResolveTarget === "function") {
      var _rt = fMulerQuizResolveTarget(t) || [];
      return _rt.slice();
    }
    var r = (typeof MULER_QUIZ_TARGET_RESOLVERS !== "undefined" && MULER_QUIZ_TARGET_RESOLVERS) ? MULER_QUIZ_TARGET_RESOLVERS[t] : null;
    if (typeof r !== "function") return [];
    var out = r() || [];
    return out.slice();
  } catch (e) { return []; }
}

// Effective quiz target for a mode: branch atoms win on branch boxes, then
// secondary hetero prefixes, then bond atoms on dual-use boxes holding a
// bond position, otherwise the registry resolver (FG-or-[]). Single FG-first
// rule shared by the arm gates and fMulerQuizTargetSet.
function fMulerQuizResolveTarget(mode) {
  try {
    if (!mode || mode === "none") return [];
    // Branch first (classic paints branch groups before bond/FG fallthroughs),
    // then secondary hetero prefixes, then bond dual-use, then the registry.
    // Single FG-first rule shared by the arm gates and fMulerQuizTargetSet.
    if (typeof fMulerBranchAtomsForMode === "function") {
      var _br = fMulerBranchAtomsForMode(mode) || [];
      if (_br.length) return _br.slice();
    }
    if ((mode === "compNumber1" || mode === "compSecondSub1" || mode === "compNumber2" || mode === "compSecondSub2") &&
        typeof fMulerHeteroPrefixAtomsForMode === "function") {
      var _hg = fMulerHeteroPrefixAtomsForMode(mode) || [];
      if (_hg.length) return _hg.slice();
    }
    if ((mode === "compBondPos" || mode === "compEndNumber" || mode === "compNumber1") &&
        typeof fMulerBondAtomsForMode === "function") {
      var _ba = fMulerBondAtomsForMode(mode) || [];
      if (_ba.length) return _ba.slice();
    }
    var r = (typeof MULER_QUIZ_TARGET_RESOLVERS !== "undefined" && MULER_QUIZ_TARGET_RESOLVERS) ? MULER_QUIZ_TARGET_RESOLVERS[mode] : null;
    if (typeof r !== "function") return [];
    var out = r() || [];
    return out.slice();
  } catch (e) { return []; }
}

// Order-insensitive set compare of the picked atoms vs the target chain.
// Bonds are normalized to endpoint atoms upstream (fMulerQuizEffectiveAtoms).
function fMulerQuizCompare(selAtoms, target) {
  try {
    var tset = {}, sset = {};
    var ta = target || [], sa = selAtoms || [];
    for (var i = 0; i < ta.length; i++) tset[ta[i]] = true;
    for (var j = 0; j < sa.length; j++) sset[sa[j]] = true;
    var missing = [], extra = [], nHit = 0, nTarget = 0;
    for (var tk in tset) {
      if (!Object.prototype.hasOwnProperty.call(tset, tk)) continue;
      nTarget++;
      if (sset[tk]) nHit++;
      else missing.push(parseInt(tk, 10));
    }
    for (var sk in sset) {
      if (!Object.prototype.hasOwnProperty.call(sset, sk)) continue;
      if (!tset[sk]) extra.push(parseInt(sk, 10));
    }
    missing.sort(function (a, b) { return a - b; });
    extra.sort(function (a, b) { return a - b; });
    var verdict = "empty";
    var orderPair = null;
    if (nHit + extra.length > 0) {
      if (!missing.length && !extra.length) {
        // FG/locant/bond/branch purposes are set-only (no walk, no direction): an unordered
        // fragment is either complete or it is not. Main chain keeps the
        // walk + direction checks below.
        var setOnly = false;
        try {
          if (typeof fMulerSelectPurpose === "function") {
            var _sp = fMulerSelectPurpose();
            setOnly = (_sp === "fg" || _sp === "loc" || _sp === "bond" || _sp === "branch");
          }
        } catch (eP) { setOnly = false; }
        if (setOnly) { verdict = "exact"; }
        else {
        // Exact set: the walk itself must be bonded end to end (either
        // direction is walkable — direction is checked separately below).
        // Same-fragment consecutive picks share one click action and assert
        // no internal order, so they never break the walk.
        var seq = [];
        for (var sj = 0; sj < sa.length; sj++) {
          var sh = sa[sj];
          if (!seq.length || seq[seq.length - 1].atom !== sh) seq.push({ atom: sh, pick: sj + 1 });
        }
        var brk = null;
        try { if (typeof fMulerQuizWalkBreak === "function") brk = fMulerQuizWalkBreak(seq); } catch (eB) { brk = null; }
        if (brk) { verdict = "order"; orderPair = [brk.a, brk.b]; }
        else {
          // Direction: the resolved chain is C1-first (engine orients via
          // lowest-locant tiers), so the pick sequence must match it — or
          // its exact reverse (right chain, wrong direction).
          var aseq = [];
          try {
            for (var di = 0; di < seq.length; di++) {
              var da = seq[di].atom;
              try { if (typeof fMulerQuizAnchorOf === "function") da = fMulerQuizAnchorOf(da); } catch (eDA) {}
              if (!aseq.length || aseq[aseq.length - 1] !== da) aseq.push(da);
            }
          } catch (eAS) { aseq = seq.map(function (s) { return s.atom; }); }
          var fwd = (aseq.length === ta.length);
          if (fwd) { for (var fi = 0; fi < ta.length; fi++) { if (aseq[fi] !== ta[fi]) { fwd = false; break; } } }
          if (fwd) { verdict = "exact"; }
          else {
            var rev = (aseq.length === ta.length);
            if (rev) { for (var ri = 0; ri < ta.length; ri++) { if (aseq[ri] !== ta[ta.length - 1 - ri]) { rev = false; break; } } }
            verdict = rev ? "direction" : "order";
          }
        }
        }
      }
      else if (!extra.length) verdict = "subset";
      else if (nHit === 0) verdict = "disjoint";
      else verdict = "wrong";
    }
    return { verdict: verdict, nHit: nHit, nTarget: nTarget, missing: missing, extra: extra, orderPair: orderPair };
  } catch (e) { return { verdict: "empty", nHit: 0, nTarget: 0, missing: [], extra: [], orderPair: null }; }
}

// Live-feedback helpers (numberless): the verdict line never leaks the
// chain length or pick positions — helpers use counts/geometry internally
// only to choose *which* sentence to show.
function fMulerQuizHasHetero(atoms) {
  try {
    var list = Array.isArray(atoms) ? atoms : [];
    if (!list.length) return false;
    if (typeof allAtomsTypeList === "undefined" || !Array.isArray(allAtomsTypeList)) return false;
    for (var i = 0; i < list.length; i++) {
      var a1 = list[i], t = "";
      try { t = String(allAtomsTypeList[a1 - 1] || "").toUpperCase(); } catch (eT) { t = ""; }
      if (t && t !== "C") return true;
    }
  } catch (e) {}
  return false;
}

// Partial walk break in pick order (any prefix length >= 2). Same
// anchor-collapsing as the exact-set check, but without requiring a complete
// set — powers the live "adjacent atoms" hint.
function fMulerQuizPartialBreak(atoms) {
  try {
    var sa = Array.isArray(atoms) ? atoms : [];
    if (sa.length < 2) return null;
    var seq = [];
    for (var i = 0; i < sa.length; i++) {
      if (!seq.length || seq[seq.length - 1].atom !== sa[i]) seq.push({ atom: sa[i], pick: i + 1 });
    }
    if (seq.length < 2) return null;
    try { if (typeof fMulerQuizWalkBreak === "function") return fMulerQuizWalkBreak(seq); } catch (eB) {}
  } catch (e) {}
  return null;
}

// Pool-wide candidates for main-chain validation (v56 1C multi-chain):
// the adopted chain first, then every ranked pool entry (all C1-first
// oriented), deduped by atom set. In data mode only the adopted (curated)
// chain counts — pool alternatives are engine also-rans there.
function fMulerQuizMainChainPool() {
  var out = [], seen = {};
  var add = function (ch, pi) {
    try {
      if (!Array.isArray(ch) || !ch.length) return;
      var key = ch.slice().sort(function (a, b) { return a - b; }).join(",");
      if (seen[key]) return;
      seen[key] = true;
      out.push({ chain: ch.slice(), poolIdx: (typeof pi === "number" ? pi : -1) });
    } catch (eA) {}
  };
  try {
    var adopted = (typeof fMulerQuizTargetSet === "function") ? fMulerQuizTargetSet() : [];
    var liveIdx = -1;
    try {
      if (typeof mainChainPool !== "undefined" && mainChainPool && adopted && adopted.length) {
        var akey = adopted.slice().sort(function (a, b) { return a - b; }).join(",");
        for (var pi = 0; pi < mainChainPool.length; pi++) {
          var pc = mainChainPool[pi] && mainChainPool[pi].chain;
          if (Array.isArray(pc) && pc.slice().sort(function (a, b) { return a - b; }).join(",") === akey) { liveIdx = pi; break; }
        }
      }
    } catch (eL) { liveIdx = -1; }
    add(adopted, liveIdx);
    var algo = true;
    try { algo = (typeof mainChainMode === "undefined" || mainChainMode === "algorithmic"); } catch (eM) { algo = true; }
    if (algo) {
      try {
        if (typeof mainChainPool !== "undefined" && Array.isArray(mainChainPool)) {
          for (var i = 0; i < mainChainPool.length; i++) {
            if (mainChainPool[i] && Array.isArray(mainChainPool[i].chain)) add(mainChainPool[i].chain, i);
          }
        }
      } catch (eP) {}
    }
  } catch (e) {}
  return out;
}

function fMulerQuizChainsEqual(a, b) {
  try {
    if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
    return true;
  } catch (e) { return false; }
}

// Direction-indifference oracle (v56 symmetric main chains): a chain is
// direction-free exactly when the orienter is indifferent to its reverse,
// i.e. when every lowest-locant tier ties (linear alkanes, etc.). The
// orienter is pure (0-based, idempotent), so rev === orient(rev) — no engine
// changes, no second definition of symmetry to drift.
function fMulerQuizSymmetricChain(chain1) {
  try {
    if (!Array.isArray(chain1) || !chain1.length) return false;
    var rev = chain1.slice().reverse().map(function (a) { return a - 1; });
    var oriented = null;
    try { if (typeof fOrientChainPath === "function") oriented = fOrientChainPath(rev); } catch (eO) { oriented = null; }
    if (!Array.isArray(oriented)) return false;
    for (var i = 0; i < rev.length; i++) if (oriented[i] !== rev[i]) return false;
    return true;
  } catch (e) { return false; }
}

// Pool-wide compare: exact-directional match on ANY candidate wins
// (adopted first); then direction, then order; live numberless hints
// (hetero/gap/more/fewer/wrong) always come from the adopted chain
// (stable reference for the panel).
function fMulerQuizComparePool(atoms) {
  try {
    // FG/locant/bond/branch purposes are a single set-only candidate (no pool, no direction).
    var setOnly = false;
    try {
      if (typeof fMulerSelectPurpose === "function") {
        var _pp = fMulerSelectPurpose();
        setOnly = (_pp === "fg" || _pp === "loc" || _pp === "bond" || _pp === "branch");
      }
    } catch (eP) { setOnly = false; }
    if (setOnly) {
      var tgt = [];
      try { tgt = (typeof fMulerQuizTargetSet === "function") ? fMulerQuizTargetSet() : []; } catch (eT) { tgt = []; }
      if (!tgt.length) return { verdict: "empty", nHit: 0, nTarget: 0, missing: [], extra: [], orderPair: null, matched: null };
      var one = null;
      try { one = (typeof fMulerQuizCompare === "function") ? fMulerQuizCompare(atoms, tgt) : null; } catch (eC) { one = null; }
      if (!one) return { verdict: "empty", nHit: 0, nTarget: 0, missing: [], extra: [], orderPair: null, matched: null };
      return { verdict: one.verdict, nHit: one.nHit, nTarget: one.nTarget, missing: one.missing, extra: one.extra, orderPair: null, matched: null };
    }
    var cands = (typeof fMulerQuizMainChainPool === "function") ? fMulerQuizMainChainPool() : [];
    if (!cands.length) return { verdict: "empty", nHit: 0, nTarget: 0, missing: [], extra: [], orderPair: null, matched: null };
    var results = [];
    for (var i = 0; i < cands.length; i++) {
      var cmp = null;
      try { if (typeof fMulerQuizCompare === "function") cmp = fMulerQuizCompare(atoms, cands[i].chain); } catch (eC) { cmp = null; }
      if (cmp) results.push({ cand: cands[i], cmp: cmp });
    }
    if (!results.length) return { verdict: "empty", nHit: 0, nTarget: 0, missing: [], extra: [], orderPair: null, matched: null };
    var r, j;
    for (j = 0; j < results.length; j++) {
      if (results[j].cmp.verdict === "exact") {
        r = results[j].cmp;
        return { verdict: "exact", nHit: r.nHit, nTarget: r.nTarget, missing: r.missing, extra: r.extra, orderPair: null, matched: results[j].cand };
      }
    }
    for (j = 0; j < results.length; j++) {
      if (results[j].cmp.verdict === "direction") {
        r = results[j].cmp;
        var sym = false;
        try { if (typeof fMulerQuizSymmetricChain === "function") sym = fMulerQuizSymmetricChain(results[j].cand.chain); } catch (eS) { sym = false; }
        if (sym) return { verdict: "exact", nHit: r.nHit, nTarget: r.nTarget, missing: r.missing, extra: r.extra, orderPair: null, matched: results[j].cand };
        return { verdict: "direction", nHit: r.nHit, nTarget: r.nTarget, missing: r.missing, extra: r.extra, orderPair: null, matched: null };
      }
    }
    for (j = 0; j < results.length; j++) {
      if (results[j].cmp.verdict === "order") {
        r = results[j].cmp;
        return { verdict: "order", nHit: r.nHit, nTarget: r.nTarget, missing: r.missing, extra: r.extra, orderPair: r.orderPair, matched: null };
      }
    }
    r = results[0].cmp;
    return { verdict: r.verdict, nHit: r.nHit, nTarget: r.nTarget, missing: r.missing, extra: r.extra, orderPair: r.orderPair || null, matched: null };
  } catch (e) { return { verdict: "empty", nHit: 0, nTarget: 0, missing: [], extra: [], orderPair: null, matched: null }; }
}

// Anchor-aware walk check (v56 1C order dimension): consecutive picks must be
// bonded. Fragment members map to their compacted label's anchor (all member
// bonds run through it), so same-label pairs can never break the walk.
function fMulerQuizAnchorOf(atom1) {
  try {
    var comp = null;
    try {
      var _g = (typeof fMulerSelectGeom === "function") ? fMulerSelectGeom() : null;
      comp = (_g && _g.comp) || null;
    } catch (eG) { comp = null; }
    if (!comp) {
      try { comp = (typeof fMulerSelectCompacted === "function") ? fMulerSelectCompacted() : null; } catch (eC) { comp = null; }
    }
    if (comp) for (var i = 0; i < comp.length; i++) {
      var cm = comp[i];
      if (cm && cm.members && cm.members.indexOf(atom1) >= 0 && cm.anchor !== undefined && cm.anchor !== null) return cm.anchor + 1;
    }
  } catch (e) {}
  return atom1;
}

function fMulerQuizBonded(a, b) {
  try {
    if (typeof bondList === "undefined" || !bondList) return false;
    for (var i = 0; i < bondList.length; i++) {
      if (!bondList[i]) continue;
      if ((bondList[i][0] === a && bondList[i][1] === b) || (bondList[i][0] === b && bondList[i][1] === a)) return true;
    }
  } catch (e) {}
  return false;
}

// seq: [{atom (1-based), pick (1-based selection position)}].
// Returns {a, b} pick numbers of the first broken link, or null.
function fMulerQuizWalkBreak(seq) {
  try {
    for (var i = 1; i < seq.length; i++) {
      var A = seq[i - 1], B = seq[i];
      var ka = A.atom, kb = B.atom;
      try {
        if (typeof fMulerQuizAnchorOf === "function") { ka = fMulerQuizAnchorOf(A.atom); kb = fMulerQuizAnchorOf(B.atom); }
      } catch (eA) {}
      if (ka === kb) continue;
      var ok = false;
      try { ok = (typeof fMulerQuizBonded === "function") ? fMulerQuizBonded(ka, kb) : false; } catch (eB) {}
      if (!ok) return { a: A.pick, b: B.pick };
    }
  } catch (e) {}
  return null;
}

function fMulerQuizVerdictEl() {
  try {
    var el = document.getElementById("mulerQuizVerdict");
    if (el) return el;
    var host = document.getElementById("nameAnalysisExplain");
    if (!host || !host.parentNode) return null;
    el = document.createElement("div");
    el.setAttribute("id", "mulerQuizVerdict");
    // Layout lives in css/jsme-nick-57.css; keep the inline style as fallback
    // for cached CSS (same values, harmless duplication).
    try { el.setAttribute("style", "margin-top:6px;font-weight:bold;"); } catch (eS) {}
    try { el.className = "mulerQuiz-empty"; } catch (eC) {}
    host.parentNode.insertBefore(el, host.nextSibling);
    return el;
  } catch (e) { return null; }
}

// Branch target split: locant boxes keep the "indicated position" wording,
// name boxes (substituent names, common/ester alkyls) use the short wording.
function fMulerBranchTargetIsLocant(mode) {
  try {
    var m = String(mode == null ? "" : mode);
    if (m === "compNumber1" || m === "compNumber2") return true;
    if (/^compBranchLoc\d+$/.test(m)) return true;
    return false;
  } catch (e) { return false; }
}

// Bond target split for the numbering aid: bond-position (locant) boxes
// need the chain scale; bond-type name boxes (compBondType/compBondType2)
// do not — same rule as branch names vs locants.
function fMulerBondTargetIsLocant(mode) {
  try {
    var m = String(mode == null ? "" : mode);
    if (m === "compBondPos" || m === "compEndNumber" || m === "compNumber1") return true;
    return false;
  } catch (e) { return false; }
}

// Single-bond quiz: compBondType with the "αν" infix quizzes every single
// C–C bond (reward paints that set); all other bond quizzes are multiple.
function fMulerBondIsSingle() {
  try {
    if (typeof window === "undefined" || !window.MulerQuizTarget) return false;
    if (String(window.MulerQuizTarget) !== "compBondType") return false;
    var s6 = "";
    try { s6 = (typeof nameComponentsList !== "undefined" && nameComponentsList) ? (nameComponentsList[6] || "") : ""; } catch (e6) { s6 = ""; }
    return s6 === "αν" || s6 === "άν";
  } catch (e) { return false; }
}

function fMulerQuizVerdict(kind, cmp) {
  try {
    // Renderer for every verdict kind. Live schedule: exact/direction/order
    // (final, full-set) plus hetero/gap/more/fewer/wrong (live, numberless —
    // no counts, no pick positions). FG/locant targets reuse the set-only
    // kinds with their own strings (direction/order/gap/hetero never fire).
    // Color is set inline (immediate) + via CSS class (skinnable, see
    // css/jsme-nick-57.css #mulerQuizVerdict.*).
    var el = (typeof fMulerQuizVerdictEl === "function") ? fMulerQuizVerdictEl() : null;
    if (!el) return;
    var T = function (k) { try { return (typeof fMulerT === "function") ? fMulerT(k) : ""; } catch (eT) { return ""; } };
    if (!kind || kind === "clear") { try { el.textContent = ""; el.style.display = "none"; } catch (eC) {} return; }
    try { el.style.display = ""; } catch (eD) {}
    var txt = "", col = "#555555", glyph = "○", cls = "mulerQuiz-empty";
    // FG/locant/bond/branch targets use their own strings (never main-chain words).
    // The exact verdict renders after Refresh clears the target, so it reads
    // the one-shot __mulerQuizFgVerdict flag ("fg"/"loc"/"bond"/"bondSingle"/"branchLoc"/"branchName") first, then live purpose.
    var fgTxt = false, locTxt = false, bondTxt = false, bondSingleTxt = false, branchTxt = false, branchNameTxt = false;
    try {
      if (typeof window !== "undefined") {
        if (window.__mulerQuizFgVerdict === "loc") locTxt = true;
        else if (window.__mulerQuizFgVerdict === "fg") fgTxt = true;
        else if (window.__mulerQuizFgVerdict === "bondSingle") bondSingleTxt = true;
        else if (window.__mulerQuizFgVerdict === "bond") bondTxt = true;
        else if (window.__mulerQuizFgVerdict === "branch" || window.__mulerQuizFgVerdict === "branchLoc") branchTxt = true;
        else if (window.__mulerQuizFgVerdict === "branchName") branchNameTxt = true;
        window.__mulerQuizFgVerdict = "";
      }
    } catch (eF) {}
    if (!fgTxt && !locTxt && !bondTxt && !bondSingleTxt && !branchTxt && !branchNameTxt) {
      try {
        if (typeof fMulerSelectPurpose === "function") {
          var _vp = fMulerSelectPurpose();
          if (_vp === "fg") fgTxt = true;
          else if (_vp === "loc") locTxt = true;
          else if (_vp === "bond") {
            try {
              if ((typeof fMulerBondIsSingle === "function") && fMulerBondIsSingle()) bondSingleTxt = true;
              else bondTxt = true;
            } catch (eBS) { bondTxt = true; }
          }
          else if (_vp === "branch") {
            var _vm = (typeof window !== "undefined") ? window.MulerQuizTarget : "";
            if (typeof fMulerBranchTargetIsLocant === "function" && fMulerBranchTargetIsLocant(_vm)) branchTxt = true;
            else branchNameTxt = true;
          }
        }
      } catch (eP) {}
    }
    var keyFor = function (base) { return fgTxt ? base + "Fg" : (locTxt ? base + "Loc" : (bondSingleTxt ? base + "BondSingle" : (bondTxt ? base + "Bond" : (branchTxt ? base + "Branch" : (branchNameTxt ? base + "Branch" : base))))); };
    if (kind === "exact") { col = "#1a7a3c"; glyph = "✓"; txt = T(branchNameTxt ? "quizExactBranchName" : keyFor("quizExact")); cls = "mulerQuiz-exact"; }
    else if (kind === "more") { col = "#8a6d00"; glyph = "◐"; txt = T(keyFor("quizMore")); cls = "mulerQuiz-more"; }
    else if (kind === "fewer") { col = "#8a6d00"; glyph = "◐"; txt = T(keyFor("quizFewer")); cls = "mulerQuiz-fewer"; }
    else if (kind === "hetero") { col = "#b3261e"; glyph = "✕"; txt = T("quizHetero"); cls = "mulerQuiz-hetero"; }
    else if (kind === "gap") { col = "#8a6d00"; glyph = "⇄"; txt = T("quizGap"); cls = "mulerQuiz-gap"; }
    else if (kind === "subset") { col = "#8a6d00"; glyph = "◐"; txt = T(keyFor("quizMore")); cls = "mulerQuiz-subset"; }
    else if (kind === "wrong") { col = "#b3261e"; glyph = "✕"; txt = T(keyFor("quizWrong")); cls = "mulerQuiz-wrong"; }
    else if (kind === "disjoint") { col = "#555555"; glyph = "○"; txt = T(keyFor("quizDisjoint")); cls = "mulerQuiz-disjoint"; }
    else if (kind === "order") {
      col = "#8a6d00"; glyph = "⇄"; cls = "mulerQuiz-order";
      var _op = (cmp && cmp.orderPair) || [0, 0];
      try { txt = T("quizOrder").replace("{a}", String(_op[0])).replace("{b}", String(_op[1])); } catch (eO) { txt = T("quizOrder"); }
    }
    else if (kind === "direction") { col = "#8a6d00"; glyph = "↩"; txt = T("quizDirection"); cls = "mulerQuiz-direction"; }
    else { col = "#555555"; glyph = "·"; txt = T("quizEmpty"); cls = "mulerQuiz-empty"; }
    try { el.style.color = col; } catch (eC2) {}
    try { el.className = cls; } catch (eC3) {}
    try { el.textContent = glyph + " " + txt; } catch (eT2) {}
  } catch (e) {}
}

function fMulerQuizPrompt() {
  try {
    var ex = document.getElementById("nameAnalysisExplain");
    var pickKey = "quizPick";
    try {
      if (typeof fMulerSelectPurpose === "function") {
        var _pp = fMulerSelectPurpose();
        if (_pp === "fg") pickKey = "quizPickFg";
        else if (_pp === "loc") pickKey = "quizPickLoc";
        else if (_pp === "bond") pickKey = "quizPickBond";
        else if (_pp === "branch") {
          var _bt = (typeof window !== "undefined") ? window.MulerQuizTarget : "";
          pickKey = ((typeof fMulerBranchTargetIsLocant === "function") && fMulerBranchTargetIsLocant(_bt)) ? "quizPickBranch" : "quizPickBranchName";
        }
        else if (_pp === "mainChain" && typeof window !== "undefined" && window.__mulerQuizReturnTo) pickKey = "quizChainFirst";
      }
    } catch (eP) {}
    if (ex) { try { ex.textContent = (typeof fMulerT === "function") ? fMulerT(pickKey) : ""; } catch (eT) {} }
    // The prompt owns the panel until the first pick; Refresh then owns the
    // verdict line (live numberless hints, final direction/order).
    if (typeof fMulerQuizVerdict === "function") fMulerQuizVerdict("clear", null);
  } catch (e) {}
}

function fMulerQuizDisarm() {
  try { if (typeof window !== "undefined") window.MulerQuizTarget = null; } catch (eT) {}
  try { if (typeof window !== "undefined") window.__mulerQuizReturnTo = null; } catch (eR) {}
  try { if (typeof fMulerQuizVerdict === "function") fMulerQuizVerdict("clear", null); } catch (eV) {}
}

// Sticky-quiz re-arm on molecule switch (v56): sticky selection restores the
// component box (.selected + nameAnalysisMode) but PushState disarms the quiz
// on molecule change, leaving select ON + comp selected + purpose "free" —
// so condensed CHO/COOH clicks then take the whole fragment instead of the
// anchor carbon. Re-arm when the restored box is quiz-capable. Mirrors the
// click-arm body without requiring a click; never overrides an active target,
// Present/draft/replay, hidden boxes, or a deselected panel.
function fMulerQuizRearmSticky() {
  try {
    if (typeof window === "undefined") return false;
    if (window.MulerDraft) return false;
    if (typeof fMulerSelectActive === "function" && !fMulerSelectActive()) return false;
    if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return false;
    if (window.__mulerQuizReplayBypass) return false;
    if (window.MulerQuizTarget) return false;
    var mode = "none";
    try { mode = (typeof nameAnalysisMode !== "undefined") ? nameAnalysisMode : "none"; } catch (eM) { mode = "none"; }
    if (!mode || mode === "none") return false;
    var resolver = null;
    try { resolver = (typeof MULER_QUIZ_TARGET_RESOLVERS !== "undefined" && MULER_QUIZ_TARGET_RESOLVERS) ? MULER_QUIZ_TARGET_RESOLVERS[mode] : null; } catch (eR) { resolver = null; }
    // Atom-less targets (hydrocarbon -ιο suffix, hidden boxes) never arm:
    // fall through to the classic explanation path instead of a stuck quiz.
    // Effective target (branch/bond-aware); branch modes need no registry
    // entry of their own, so its emptiness alone decides.
    try {
      var preTgt = (typeof fMulerQuizResolveTarget === "function") ? fMulerQuizResolveTarget(mode) : ((typeof resolver === "function") ? resolver() : []);
      if (!preTgt.length) return false;
    } catch (ePT) { return false; }
    // Number-locant boxes need a solved chain on this molecule (numbering aid
    // reference): sticky restore on an unsolved molecule disarms instead of
    // redirecting — the next box click starts the chain-first flow. Name boxes
    // may re-arm directly (same component selected = same task).
    try {
      var _rBox = null;
      try { _rBox = (typeof fMulerQuizBoxIdForMode === "function") ? fMulerQuizBoxIdForMode(mode) : null; } catch (eRB) { _rBox = null; }
      var _rLoc = false;
      try { _rLoc = (typeof fMulerQuizBoxShowsLocant === "function") ? fMulerQuizBoxShowsLocant(_rBox, null) : false; } catch (eW) { _rLoc = false; }
      if (_rLoc && (typeof fMulerChainSolved !== "function" || !fMulerChainSolved())) return false;
    } catch (eG) {}
    var boxId = null;
    try {
      var s = document.querySelector("#nameAnalysis .nameCompBox.selected");
      if (s) boxId = s.getAttribute("id") || null;
    } catch (eS) { boxId = null; }
    if (!boxId) return false;
    var boxMode = "none";
    try { boxMode = (typeof fNameAnalysisModeForBoxId === "function") ? fNameAnalysisModeForBoxId(boxId) : "none"; } catch (eM2) { boxMode = "none"; }
    if (boxMode !== mode) return false;
    try {
      var bEl = document.getElementById(boxId);
      if (!bEl) return false;
      if (bEl.classList && bEl.classList.contains("comp-hidden")) return false;
      if (typeof fNameCompHidden === "function" && fNameCompHidden(boxId)) return false;
    } catch (eH) { return false; }
    try { window.MulerQuizTarget = mode; } catch (eT) {}
    try { if (typeof fMulerSelectNormalizeMainChainCompacts === "function") fMulerSelectNormalizeMainChainCompacts(); } catch (eN) {}
    try { if (typeof fClearHighlights === "function") fClearHighlights(); } catch (eCH) {}
    try { numberingFlag = false; } catch (eN2) {}
    try { if (window.nameExplainAll) { window.nameExplainAll = false; try { jQuery("#nameExplainAllBtn").removeClass("active"); } catch (eB) {} } } catch (eT2) {}
    try { var rc = document.getElementById("ruleTheoryContainer"); if (rc) rc.style.display = "none"; } catch (eR2) {}
    try { if (typeof fMulerQuizPrompt === "function") fMulerQuizPrompt(); } catch (eP) {}
    try { if (typeof fMulerQuizRefresh === "function") fMulerQuizRefresh(); } catch (eR3) {}
    try { if (typeof fMulerSelectRepaint === "function") fMulerSelectRepaint(); } catch (eR4) {}
    try { if (typeof fUpdateSVG === "function") fUpdateSVG(); } catch (eU) {}
    try { if (typeof fFitNameComponents === "function") fFitNameComponents(); } catch (eF) {}
    try { if (window.nameExplainAll && typeof fNameExplainTableRender === "function") fNameExplainTableRender(); } catch (eET) {}
    return true;
  } catch (e) { return false; }
}

// Quiz arm on name-box click while select mode is armed (teaching layer
// calls this; returns true when it consumed the click). Mirrors the classic
// selection visuals (selected box + mode) but swaps the highlight for the
// neutral prompt; the live compare below replays the classic path on exact.
// A box showing a position number ("-2-", "2,4-") needs the chain scale to
// be interpretable, so on an unsolved molecule it redirects to the main-chain
// quiz first (auto-return on exact); name boxes arm directly.
function fMulerQuizBoxShowsLocant(boxId, $box) {
  try {
    var txt = "";
    try { if ($box && typeof $box.text === "function") txt = $box.text() || ""; } catch (eT) { txt = ""; }
    if (!txt) {
      try {
        var el = (typeof document !== "undefined" && boxId) ? document.getElementById(boxId) : null;
        if (el) txt = el.textContent || "";
      } catch (eD) {}
    }
    var t = String(txt == null ? "" : txt).replace(/^[-\s]+/, "").replace(/[-\s]+$/, "");
    return /^\d/.test(t);
  } catch (e) { return false; }
}

// True when a locant box actually names the FG target: any digit run in the
// rendered box text equals a main-chain locant of the given (1-based) atoms.
// Guards FG quizzes AND classic FG paint against box/mode skew (e.g. a
// triple-bond locant landing in an FG-position box): in that case the box is
// about the bond, not the group. Boxes without digits, missing DOM, or any
// error fall through to true (no contradiction possible — current behavior).
function fMulerBoxMatchesTarget(mode, atoms) {
  try {
    var boxId = null;
    try { boxId = (typeof fMulerQuizBoxIdForMode === "function") ? fMulerQuizBoxIdForMode(mode) : null; } catch (eB) { boxId = null; }
    var txt = "";
    try {
      if (boxId && typeof document !== "undefined") {
        var el = document.getElementById(boxId);
        if (el && el.textContent) txt = el.textContent;
      }
    } catch (eD) {}
    var m = String(txt == null ? "" : txt).match(/\d+/g) || [];
    if (!m.length) return true;
    var locs = {};
    var arr = Array.isArray(atoms) ? atoms : [];
    for (var i = 0; i < arr.length; i++) {
      var L = null;
      try { L = (typeof fMainChainLocant === "function") ? fMainChainLocant(arr[i]) : null; } catch (eL) { L = null; }
      if (typeof L === "number" && isFinite(L)) locs[L] = true;
    }
    for (var j = 0; j < m.length; j++) {
      if (locs[parseInt(m[j], 10)]) return true;
    }
    return false;
  } catch (e) { return true; }
}

function fMulerQuizArmForBox(boxId, $box) {
  try {
    if (typeof window === "undefined" || window.MulerDraft) return false;
    if (typeof fMulerSelectActive === "function" && !fMulerSelectActive()) return false;
    if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return false;
    var mode = "none";
    try { mode = (typeof fNameAnalysisModeForBoxId === "function") ? fNameAnalysisModeForBoxId(boxId) : "none"; } catch (eM) { mode = "none"; }
    if (!mode || mode === "none") return false;
    // Atom-less targets (hydrocarbon -ιο suffix) never arm: fall through to
    // the classic explanation path instead of a stuck quiz. The effective
    // target resolves branch/bond/registry in one place — modes need no
    // registry entry of their own, so its emptiness alone decides.
    var resolver = null;
    try { resolver = (typeof MULER_QUIZ_TARGET_RESOLVERS !== "undefined" && MULER_QUIZ_TARGET_RESOLVERS) ? MULER_QUIZ_TARGET_RESOLVERS[mode] : null; } catch (eR) { resolver = null; }
    try {
      var preTgt = (typeof fMulerQuizResolveTarget === "function") ? fMulerQuizResolveTarget(mode) : ((typeof resolver === "function") ? resolver() : []);
      if (!preTgt.length) return false;
    } catch (ePT) { return false; }
    // Chain-first prerequisite: a number-locant box on an unsolved molecule
    // redirects to the main-chain quiz (chain box visuals included) and stashes
    // the mode for the auto-return on exact. Name boxes arm directly even
    // unsolved; solved molecules arm everything directly.
    try {
      var _showsLoc = false;
      try { _showsLoc = (typeof fMulerQuizBoxShowsLocant === "function") ? fMulerQuizBoxShowsLocant(boxId, $box) : false; } catch (eW) { _showsLoc = false; }
      if (_showsLoc && (typeof fMulerChainSolved !== "function" || !fMulerChainSolved())) {
        var _cb = (typeof fMulerQuizBoxIdForMode === "function") ? fMulerQuizBoxIdForMode("compCarbonsCount") : null;
        var _$cb = null;
        try { _$cb = (_cb && typeof jQuery !== "undefined") ? jQuery("#" + _cb) : null; } catch (eJ) { _$cb = null; }
        if (_cb && _$cb && _$cb.length) {
          try { if (typeof window !== "undefined") window.__mulerQuizReturnTo = mode; } catch (eR) {}
          try { boxId = _cb; } catch (eB) {}
          try { $box = _$cb; } catch (eB2) {}
          mode = "compCarbonsCount";
          try { resolver = (typeof MULER_QUIZ_TARGET_RESOLVERS !== "undefined" && MULER_QUIZ_TARGET_RESOLVERS) ? MULER_QUIZ_TARGET_RESOLVERS[mode] : null; } catch (eR2) { resolver = null; }
          if (typeof resolver !== "function") {
            try { if (typeof window !== "undefined") window.__mulerQuizReturnTo = null; } catch (eR3) {}
            return false;
          }
          try {
            var _preC = resolver() || [];
            if (!_preC.length) {
              try { if (typeof window !== "undefined") window.__mulerQuizReturnTo = null; } catch (eR4) {}
              return false;
            }
          } catch (ePC) {
            try { if (typeof window !== "undefined") window.__mulerQuizReturnTo = null; } catch (eR5) {}
            return false;
          }
        }
      }
    } catch (eRedir) {}
    // Same-box re-click always deselects through the classic path (disarm
    // first); a fresh click afterwards can re-arm.
    try {
      if ($box && $box.hasClass && $box.hasClass("selected")) {
        if (typeof fMulerQuizDisarm === "function") fMulerQuizDisarm();
        return false;
      }
    } catch (eD) { return false; }
    try { window.MulerQuizTarget = mode; } catch (eT) {}
    // Main-chain purpose: an earlier compacted-carbon fragment pick is now a
    // carbon-only pick. NOx/SOx fragment picks are left untouched.
    try { if (typeof fMulerSelectNormalizeMainChainCompacts === "function") fMulerSelectNormalizeMainChainCompacts(); } catch (eNorm) {}
    // Clean slate like the classic preamble (skipped by the early return
    // below): stale component green + numbering interval must not leak in.
    try { if (typeof fClearHighlights === "function") fClearHighlights(); } catch (eCH) {}
    try {
      if (typeof jQuery !== "undefined") { jQuery(".nameCompBox").removeClass("selected"); if ($box && $box.addClass) $box.addClass("selected"); }
      else {
        var bs = document.querySelectorAll(".nameCompBox");
        for (var i = 0; i < bs.length; i++) bs[i].classList.remove("selected");
        var one = document.getElementById(boxId);
        if (one) one.classList.add("selected");
      }
    } catch (eC) {}
    try { nameAnalysisMode = mode; } catch (eM2) {}
    try { numberingFlag = false; } catch (eN) {}
    try { if (window.nameExplainAll) { window.nameExplainAll = false; try { jQuery("#nameExplainAllBtn").removeClass("active"); } catch (eB) {} } } catch (eT2) {}
    try { var rc = document.getElementById("ruleTheoryContainer"); if (rc) rc.style.display = "none"; } catch (eR2) {}
    try { if (typeof fMulerQuizPrompt === "function") fMulerQuizPrompt(); } catch (eP) {}
    try { if (typeof fMulerQuizRefresh === "function") fMulerQuizRefresh(); } catch (eR3) {}
    try { if (typeof fMulerSelectRepaint === "function") fMulerSelectRepaint(); } catch (eR4) {}
    try { if (typeof fUpdateSVG === "function") fUpdateSVG(); } catch (eU) {}
    try { if (typeof fFitNameComponents === "function") fFitNameComponents(); } catch (eF) {}
    // Explain-all panel stays the overview table when it is open (the prompt
    // above only owns the single-explanation panel).
    try { if (window.nameExplainAll && typeof fNameExplainTableRender === "function") fNameExplainTableRender(); } catch (eET) {}
    // Stale return-to must not survive a direct (non-chain) arm.
    try { if (mode !== "compCarbonsCount" && typeof window !== "undefined") window.__mulerQuizReturnTo = null; } catch (eRT) {}
    return true;
  } catch (e) { return false; }
}

// Live compare after every selection change. On exact: clear the target,
// replay the classic component path (green + numbering + explanation as the
// reward), then the success line. Callers repaint/render as usual afterwards.
// Live feedback (numberless — no chain length, no pick positions):
// hetero > gap > more/fewer > wrong. `direction`/`order` stay final-only —
// they fire once the picked set already equals the target set.
function fMulerQuizRefresh() {
  try {
    var target = (typeof window !== "undefined") ? window.MulerQuizTarget : null;
    if (!target) {
      try { if (typeof fMulerQuizVerdict === "function") fMulerQuizVerdict("clear", null); } catch (eC) {}
      return null;
    }
    var sel = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null;
    var atoms = (sel && Array.isArray(sel.atoms2D)) ? sel.atoms2D.slice() : [];
    // Unsupported 3D-only free picks cannot silently earn a 2D quiz reward.
    if (fMulerSelectQuiz3DBlocked(sel)) { fMulerSelect3DFeedback(); return { verdict: "unmapped3D" }; }
    // Bond quizzes compare bond lines by their endpoint atoms, so a bond
    // click counts its two atoms (bond lines and labels interchangeable).
    var effAtoms = atoms;
    try {
      if (typeof fMulerSelectPurpose === "function" && fMulerSelectPurpose() === "bond" &&
          typeof fMulerQuizEffectiveAtoms === "function") {
        var _sb = (sel && Array.isArray(sel.bonds2D)) ? sel.bonds2D : [];
        effAtoms = fMulerQuizEffectiveAtoms(atoms, _sb);
      }
    } catch (eE) { effAtoms = atoms; }
    var r = null;
    try { if (typeof fMulerQuizComparePool === "function") r = fMulerQuizComparePool(effAtoms); } catch (eRP) { r = null; }
    if (!r) return null;
    if (r.verdict === "exact") {
      // Adopt the matched chain when it is not the live one (stepper path:
      // pool index + recompute, so green + numbering + explanation agree).
      // Data mode never reaches here with a foreign match (adopted-only).
      try {
        var _algo = true;
        try { _algo = (typeof mainChainMode === "undefined" || mainChainMode === "algorithmic"); } catch (eM) {}
        var _live = (typeof fMulerMainChainResolved === "function") ? fMulerMainChainResolved() : [];
        if (_algo && r.matched && r.matched.poolIdx >= 0 && r.matched.chain &&
            !(typeof fMulerQuizChainsEqual === "function" && fMulerQuizChainsEqual(_live, r.matched.chain))) {
          try { mainChainPoolIdx = r.matched.poolIdx; } catch (eP) {}
          try { if (typeof fApplyChainStep === "function") fApplyChainStep(); } catch (eA) {}
        }
      } catch (eAd) {}
      // Solved-state is per molecule: any main-chain exact unlocks the locant
      // numbering aid here. Captured before the target clear below.
      var _wasMain = false;
      try { _wasMain = (typeof window !== "undefined" && window.MulerQuizTarget === "compCarbonsCount"); } catch (eW) { _wasMain = false; }
      // Verdict wording needs the pre-clear purpose (exact renders after the
      // target is gone): one-shot flag ("fg"/"loc"/"bond"/"bondSingle"/"branchLoc"/"branchName") consumed by fMulerQuizVerdict.
      try {
        if (typeof window !== "undefined") {
          var _wp = (typeof fMulerSelectPurpose === "function") ? fMulerSelectPurpose() : "";
          var _wv = _wp;
          if (_wp === "branch") {
            try {
              var _wmt = window.MulerQuizTarget;
              _wv = ((typeof fMulerBranchTargetIsLocant === "function") && fMulerBranchTargetIsLocant(_wmt)) ? "branchLoc" : "branchName";
            } catch (eB) { _wv = "branchLoc"; }
          } else if (_wp === "bond") {
            try {
              if ((typeof fMulerBondIsSingle === "function") && fMulerBondIsSingle()) _wv = "bondSingle";
            } catch (eBS2) {}
          }
          window.__mulerQuizFgVerdict = (_wv === "fg" || _wv === "loc" || _wv === "bond" || _wv === "bondSingle" || _wv === "branch" || _wv === "branchLoc" || _wv === "branchName") ? _wv : "";
        }
      } catch (eF) {}
      try { if (typeof window !== "undefined") window.MulerQuizTarget = null; } catch (eT) {}
      try {
        if (_wasMain && typeof selectedMol !== "undefined" && selectedMol && typeof window !== "undefined") {
          if (!window.__mulerChainSolved) window.__mulerChainSolved = {};
          window.__mulerChainSolved[String(selectedMol)] = true;
        }
      } catch (eS) {}
      // Green wins outright: drop the selection itself (not just its paint)
      // so no later clear can resurrect cyan from stale state.
      try { if (sel) { sel.atoms2D = []; sel.bonds2D = []; sel.atoms3D = []; sel.bonds3D = []; sel.groups = []; } } catch (eS2) {}
      // Exact is the one moment selection mode allows a component highlight:
      // opt the viewer-owning guard in fExplainNameComp through for this call.
      // try/finally: the flag must clear even if the explain path throws.
      try { if (typeof window !== "undefined") window.__mulerQuizReward = true; } catch (eRw) {}
      try {
        try { if (typeof fExplainNameComp === "function") fExplainNameComp(); } catch (eE) {}
      } finally {
        try { if (typeof window !== "undefined") window.__mulerQuizReward = false; } catch (eRw2) {}
      }
      try { if (typeof fMulerQuizVerdict === "function") fMulerQuizVerdict("exact", r.cmp || r); } catch (eV) {}
      // Explain-all panel stays the overview table when it is open.
      try { if (window.nameExplainAll && typeof fNameExplainTableRender === "function") fNameExplainTableRender(); } catch (eET) {}
      // Chain-first return: a locant/bond click armed this chain quiz; solving it
      // arms the stashed task now. Selective arm clears the chain verdict
      // when the new prompt opens: target + box + mode + prompt +
      // repaint; the reward green is cleared like any quiz preamble.
      try {
        var _ret = (typeof window !== "undefined") ? window.__mulerQuizReturnTo : null;
        try { if (typeof window !== "undefined") window.__mulerQuizReturnTo = null; } catch (eRC) {}
        if (_wasMain && _ret && typeof fMulerQuizResolveTarget === "function") {
          var _rt = [];
          try { _rt = fMulerQuizResolveTarget(_ret) || []; } catch (eRT) { _rt = []; }
          var _rb = (typeof fMulerQuizBoxIdForMode === "function") ? fMulerQuizBoxIdForMode(_ret) : null;
          var _rel = null;
          try { _rel = (_rb &&typeof document !== "undefined") ? document.getElementById(_rb) : null; } catch (eRE) { _rel = null; }
          if (_rt.length && _rb && _rel && !_rel.classList.contains("comp-hidden") &&
              (typeof fNameCompHidden !== "function" || !fNameCompHidden(_rb))) {
            try { if (typeof window !== "undefined") window.MulerQuizTarget = _ret; } catch (eT2) {}
            try { if (typeof fClearHighlights === "function") fClearHighlights(); } catch (eCH) {}
            try {
              if (typeof jQuery !== "undefined") { jQuery(".nameCompBox").removeClass("selected"); jQuery("#" + _rb).addClass("selected"); }
              else {
                var _bs = document.querySelectorAll(".nameCompBox");
                for (var _bi = 0; _bi < _bs.length; _bi++) _bs[_bi].classList.remove("selected");
                _rel.classList.add("selected");
              }
            } catch (eC) {}
            try { nameAnalysisMode = _ret; } catch (eM2) {}
            try { numberingFlag = false; } catch (eN) {}
            try { if (typeof fMulerQuizPrompt === "function") fMulerQuizPrompt(); } catch (eP) {}
            try { if (typeof fMulerSelectRepaint === "function") fMulerSelectRepaint(); } catch (eR4) {}
            try { if (typeof fUpdateSVG === "function") fUpdateSVG(); } catch (eU) {}
            try { if (typeof fFitNameComponents === "function") fFitNameComponents(); } catch (eF) {}
          }
        }
      } catch (eRet) {}
      return r.cmp || null;
    }
    if (r.verdict === "direction" || r.verdict === "order") {
      try { if (typeof fMulerQuizVerdict === "function") fMulerQuizVerdict(r.verdict, r); } catch (eV2) {}
    } else if (r.verdict === "empty") {
      // No picks: prompt owns the panel, verdict stays hidden.
      try { if (typeof fMulerQuizVerdict === "function") fMulerQuizVerdict("clear", null); } catch (eV3) {}
    } else {
      // Live, numberless, priority-ordered: hetero > gap > count > wrong.
      // FG/locant/bond/branch targets fall through to count/wrong: hetero/gap
      // hints are main-chain-only (hetero text names the main chain; gap needs a walk).
      var liveKind = null;
      var liveSetOnly = false;
      try {
        if (typeof fMulerSelectPurpose === "function") {
          var _lp = fMulerSelectPurpose();
          liveSetOnly = (_lp === "fg" || _lp === "loc" || _lp === "bond" || _lp === "branch");
        }
      } catch (eP) { liveSetOnly = false; }
      if (!liveKind && !liveSetOnly) {
        try { if (typeof fMulerQuizHasHetero === "function" && fMulerQuizHasHetero(atoms)) liveKind = "hetero"; } catch (eH) {}
      }
      if (!liveKind && !liveSetOnly) {
        try { if (typeof fMulerQuizPartialBreak === "function" && fMulerQuizPartialBreak(atoms)) liveKind = "gap"; } catch (eG) {}
      }
      if (!liveKind) {
        try {
          // Bond quizzes count normalized atoms (bond lines count their ends).
          var countList = (typeof effAtoms !== "undefined" && effAtoms) ? effAtoms : atoms;
          var uniq = {};
          for (var ui = 0; ui < countList.length; ui++) uniq[countList[ui]] = true;
          var nSel = 0;
          for (var uk in uniq) if (Object.prototype.hasOwnProperty.call(uniq, uk)) nSel++;
          var nT = (r && typeof r.nTarget === "number") ? r.nTarget : 0;
          if (nT > 0) {
            if (nSel < nT) liveKind = "more";
            else if (nSel > nT) liveKind = "fewer";
          }
        } catch (eC) {}
      }
      if (!liveKind) {
        // Same count, wrong composition, walk intact (e.g. swapped branch):
        // keep the generic outside-chain line (already numberless).
        liveKind = "wrong";
      }
      try { if (typeof fMulerQuizVerdict === "function") fMulerQuizVerdict(liveKind, r); } catch (eV4) {}
    }
    return r.cmp || null;
  } catch (e) { return null; }
}

// Selection-over-component merge (component-wins): keep every component pair,
// append selection pairs only where the component has no claim. Empty
// selection degrades to the component arg unchanged — component behavior with
// selection off is byte-identical to unwrapped.
function fMulerSelectMergeBgArg(compArg, kind) {
  try {
    var selIdx = [];
    try {
      var s = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null;
      if (s && s.active === true && !fMulerSelectPresenting()) selIdx = ((kind === "bond") ? s.bonds2D : s.atoms2D) || [];
    } catch (eS) { selIdx = []; }
    var compSet = {}, out = [];
    try {
      var parts = String(compArg == null ? "" : compArg).split(",");
      for (var i = 0; i + 1 < parts.length; i += 2) {
        var idx = parseInt(parts[i], 10);
        if (isNaN(idx)) continue;
        compSet[idx] = true;
        out.push(idx + "," + parts[i + 1]);
      }
    } catch (eP) {}
    // Condensed hidden members (compacted FG atoms: COOH/CHO oxygens etc.)
    // never paint: their labels are deleted by the compaction, but their
    // highlight circles would survive as detached blobs. The anchor carries
    // the visible selection (compact label inherits its fill). State keeps
    // the full member list for the future 1C compare — this is paint-only.
    var skipSet = null;
    try {
      if (kind === "atom" && typeof mode2D !== "undefined" && mode2D === "condensed" &&
          typeof fGetCompactedAtomSkipSet === "function") skipSet = fGetCompactedAtomSkipSet(false);
    } catch (eSk) { skipSet = null; }
    // Quiz compare (not paint) tells right from wrong: the verdict line
    // shows a numberless hint, all picks stay cyan. Present pushes component-only.
    for (var j = 0; j < selIdx.length; j++) {
      if (compSet[selIdx[j]]) continue;
      try { if (skipSet && skipSet.has(selIdx[j] - 1)) continue; } catch (eSk2) {}
      out.push(selIdx[j] + "," + MULER_SELECT_BG_SLOT);
    }
    return out.join(",");
  } catch (e) { try { return String(compArg == null ? "" : compArg); } catch (e2) { return ""; } }
}
// Push the merged colors through the ORIGINALS (never the wrapped methods —
// recording merged output as component input would leak cyan into the
// component set, and clearing the selection could never clear it).
function fMulerSelectPush() {
  try {
    // Self-healing: if the boot-time install never took, retry it here.
    try {
      if (typeof window !== "undefined" && !window.__mulerBgWrapped &&
          typeof fMulerSelectWrapBgChannel === "function") fMulerSelectWrapBgChannel();
    } catch (eW) {}
    var oA = (typeof window !== "undefined") ? window.__mulerOrigSetAtomBg : null;
    var oB = (typeof window !== "undefined") ? window.__mulerOrigSetBondBg : null;
    if (typeof oA !== "function" || typeof oB !== "function") return;
    var oRA = (typeof window !== "undefined") ? window.__mulerOrigResetAtom : null;
    var oRB = (typeof window !== "undefined") ? window.__mulerOrigResetBond : null;
    var ca = (typeof window !== "undefined" && typeof window.__mulerCompAtomArg === "string") ? window.__mulerCompAtomArg : "";
    var cb = (typeof window !== "undefined" && typeof window.__mulerCompBondArg === "string") ? window.__mulerCompBondArg : "";
    // JSME background sets accumulate rather than replace, so paint must be
    // rebuilt from scratch every push: reset first, then set the merged set.
    // This keeps highlight == selection exactly (the old set-only push left
    // deselected atoms painted). Empty merged arg needs the reset alone.
    try {
      var ma = fMulerSelectMergeBgArg(ca, "atom");
      try { if (typeof oRA === "function") oRA(0); } catch (eRA0) {}
      if (ma) { try { oA(0, ma); } catch (eA) {} }
    } catch (eM) {}
    try {
      var mb = fMulerSelectMergeBgArg(cb, "bond");
      try { if (typeof oRB === "function") oRB(0); } catch (eRB0) {}
      if (mb) { try { oB(0, mb); } catch (eB) {} }
    } catch (eM2) {}
  } catch (e) {}
}
// Boot-time channel wrapper (v56 selection look rework): intercept the four
// background-color methods on the DISPLAY applet only (draft applet untouched).
// Records the last component arg per channel, delegates the merged arg.
// Resets clear the recorded component set and re-apply selection-only, so a
// component clear never wipes the selection. Guarded + once-only; JSME vendor
// code untouched.
function fMulerSelectWrapBgChannel() {
  try {
    if (typeof window !== "undefined" && window.__mulerBgWrapped) return;
    if (typeof jsmeNomeclatureApplet === "undefined" || !jsmeNomeclatureApplet) return;
    if (typeof jsmeNomeclatureApplet.setAtomBackgroundColors !== "function") return;
    if (typeof jsmeNomeclatureApplet.setBondBackgroundColors !== "function") return;
    var _origSetA = jsmeNomeclatureApplet.setAtomBackgroundColors.bind(jsmeNomeclatureApplet);
    var _origSetB = jsmeNomeclatureApplet.setBondBackgroundColors.bind(jsmeNomeclatureApplet);
    var _origResA = jsmeNomeclatureApplet.resetAtomColors.bind(jsmeNomeclatureApplet);
    var _origResB = jsmeNomeclatureApplet.resetBondColors.bind(jsmeNomeclatureApplet);
    try {
      if (typeof window !== "undefined") {
        window.__mulerOrigSetAtomBg = _origSetA;
        window.__mulerOrigSetBondBg = _origSetB;
        window.__mulerOrigResetAtom = _origResA;
        window.__mulerOrigResetBond = _origResB;
        if (typeof window.__mulerCompAtomArg !== "string") window.__mulerCompAtomArg = "";
        if (typeof window.__mulerCompBondArg !== "string") window.__mulerCompBondArg = "";
      }
    } catch (eS) {}
    jsmeNomeclatureApplet.setAtomBackgroundColors = function (mol, arg) {
      try { if (typeof window !== "undefined") window.__mulerCompAtomArg = (arg == null ? "" : String(arg)); } catch (eR) {}
      return _origSetA(mol, fMulerSelectMergeBgArg(arg, "atom"));
    };
    var _wrappedSetA = jsmeNomeclatureApplet.setAtomBackgroundColors;
    jsmeNomeclatureApplet.setBondBackgroundColors = function (mol, arg) {
      try { if (typeof window !== "undefined") window.__mulerCompBondArg = (arg == null ? "" : String(arg)); } catch (eR2) {}
      return _origSetB(mol, fMulerSelectMergeBgArg(arg, "bond"));
    };
    var _wrappedSetB = jsmeNomeclatureApplet.setBondBackgroundColors;
    jsmeNomeclatureApplet.resetAtomColors = function (mol) {
      try { if (typeof window !== "undefined") window.__mulerCompAtomArg = ""; } catch (eR3) {}
      var r = _origResA(mol);
      try { fMulerSelectPush(); } catch (eP) {}
      return r;
    };
    var _wrappedResA = jsmeNomeclatureApplet.resetAtomColors;
    jsmeNomeclatureApplet.resetBondColors = function (mol) {
      try { if (typeof window !== "undefined") window.__mulerCompBondArg = ""; } catch (eR4) {}
      var r2 = _origResB(mol);
      try { fMulerSelectPush(); } catch (eP2) {}
      return r2;
    };
    var _wrappedResB = jsmeNomeclatureApplet.resetBondColors;
    // Verify the shadowing took (a sealed/frozen applet object would silently
    // refuse it in sloppy mode) — only then claim wrapped. A later Push
    // retries the install if this run failed.
    var _ok = false;
    try {
      _ok = (jsmeNomeclatureApplet.setAtomBackgroundColors === _wrappedSetA) &&
            (jsmeNomeclatureApplet.setBondBackgroundColors === _wrappedSetB) &&
            (jsmeNomeclatureApplet.resetAtomColors === _wrappedResA) &&
            (jsmeNomeclatureApplet.resetBondColors === _wrappedResB);
    } catch (eV) { _ok = false; }
    if (!_ok) return;
    try { if (typeof window !== "undefined") window.__mulerBgWrapped = true; } catch (eF) {}
  } catch (e) {}
}

// Rebuild the selection paint from state: push merged colors (no render —
// the fUpdateSVG head calls fMulerSelectPushState before rendering, and its
// tail calls here mid-render). A molecule/mode change drops the selection
// contents (stale indices) and stays armed; a 2D-style change also keeps an
// armed quiz target (molecule-level atom set) and restores its prompt, while a
// molecule change disarms it. Present pushes component-only (selection stays
// hidden in Present, state kept).
function fMulerSelectPushState() {
  try {
    var sel = null;
    try { sel = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null; } catch (eS) {}
    if (!sel) return;
    var key = "";
    try { key = (typeof fMulerSelectMolKey === "function") ? fMulerSelectMolKey() : ""; } catch (eK) { key = ""; }
    var molName = "";
    try { molName = (typeof selectedMol !== "undefined" && selectedMol) ? String(selectedMol) : ""; } catch (eMN) { molName = ""; }
    if (!sel.molKey) { try { sel.molKey = key; sel.molName = molName; } catch (eK2) {} }
    else if (sel.molKey !== key) {
      // molecule or 2D style changed under a live selection: the geometry
      // indices belong to the old drawing — drop the contents (stay armed).
      var _dropHad3D = false;
      try { _dropHad3D = !!((sel.atoms3D && sel.atoms3D.length) || (sel.bonds3D && sel.bonds3D.length)); } catch (eH3) { _dropHad3D = false; }
      sel.atoms2D = []; sel.bonds2D = []; sel.atoms3D = []; sel.bonds3D = []; sel.groups = [];
      // v57 3D: dropped paint is stale — erase it (empty post-drop state
      // never auto-resets, and a reward-green live here implies empty
      // arrays, so the green is never touched).
      try { if (_dropHad3D && typeof fMulerSelectClear3DPaint === "function") fMulerSelectClear3DPaint(); } catch (eC3D) {}
      // A main-chain quiz target is a molecule-level atom set, so a 2D-style
      // switch keeps it armed (the user can pick in the new style and still
      // get the verdict); only an actual molecule change disarms.
      var sameMol = (typeof sel.molName === "string") && sel.molName === molName;
      try {
        if (sameMol) {
          if (typeof window !== "undefined" && window.MulerQuizTarget &&
              typeof fMulerQuizPrompt === "function") fMulerQuizPrompt();
        } else if (typeof fMulerQuizDisarm === "function") {
          fMulerQuizDisarm();
        }
      } catch (eQD2) {}
      try {
        // Wrapped resets when installed (clear recorded comp set, re-push
        // the now-empty selection); original resets otherwise — either way
        // the applet cannot keep stale cyan across the switch.
        if (typeof jsmeNomeclatureApplet !== "undefined" && jsmeNomeclatureApplet &&
            typeof jsmeNomeclatureApplet.resetAtomColors === "function") {
          try { jsmeNomeclatureApplet.resetAtomColors(0); } catch (eRA) {}
        }
        if (typeof jsmeNomeclatureApplet !== "undefined" && jsmeNomeclatureApplet &&
            typeof jsmeNomeclatureApplet.resetBondColors === "function") {
          try { jsmeNomeclatureApplet.resetBondColors(0); } catch (eRB) {}
        }
      } catch (eCC) {}
      try {
        if (typeof window !== "undefined") { window.__mulerCompAtomArg = ""; window.__mulerCompBondArg = ""; }
      } catch (eCC2) {}
      try { sel.molKey = key; sel.molName = molName; } catch (eK3) {}
    } else if (typeof sel.molName !== "string") {
      try { sel.molName = molName; } catch (eMN2) {}
    }
    var presenting = false;
    try { presenting = (typeof fMulerSelectPresenting === "function") ? !!fMulerSelectPresenting() : false; } catch (ePr) { presenting = false; }
    if (presenting) {
      // Hidden in Present: merge() already degrades to component-only when
      // presenting, so a plain push hides the selection (state kept).
      try { if (typeof fMulerSelectPush === "function") fMulerSelectPush(); } catch (ePP) {}
      return;
    }
    try { if (typeof fMulerSelectPush === "function") fMulerSelectPush(); } catch (eP) {}
  } catch (e) {}
}

function fMulerSelectIsSelectionFill(fill) {
  // JSME writes background fills either as the palette hex or as rgb(r,g,b),
  // so derive both forms from the configured selection color. Legacy cyan
  // #22d3ee is retained for one-generation overlap (older renders / cached
  // DOM after the v56 palette move to #7ddfff). Remove the legacy branch once
  // no cached v56-early DOM can survive (post-v56 live flip + cache-bust).
  return fMulerFillMatches(MULER_SELECT_CYAN, fill) || fMulerFillMatches("#22d3ee", fill);
}

// True when a fill attribute expresses `color` in either notation (hex
// substring or rgb(r,g,b)). Used by fill-restricted cleanups so a palette
// change needs no second hardcoded pair.
function fMulerFillMatches(color, fill) {
  try {
    var f = String(fill || "").replace(/\s+/g, "").toLowerCase();
    if (!f) return false;
    var h = String(color || "").replace(/\s+/g, "").replace("#", "").toLowerCase();
    if (h && f.indexOf(h) !== -1) return true;
    if (h.length === 6) {
      var r = parseInt(h.slice(0, 2), 16);
      var g = parseInt(h.slice(2, 4), 16);
      var b = parseInt(h.slice(4, 6), 16);
      if (f.indexOf(r + "," + g + "," + b) !== -1) return true;
    }
  } catch (e) {}
  return false;
}

// The JSME anchor atom owns both a small ellipse (the atom) and the resized
// compact-label backplate. For a carbon-only compacted pick, restore the
// whole-label backplate to white, hide the oversized native ellipse, and draw
// a compact rounded path behind the C glyph only. Group fragment picks leave
// both native shapes painted. The path contains no rect/line/text nodes, so
// order maps and highlight scraping stay blind to it.
// The backplate is optional: methanal can render without highlight geometry,
// in which case the C-sized path is still the only selection cue available.
function fMulerSelectCompactAnchorEllipse(rectEl, comp) {
  try {
    var doc = (rectEl && rectEl.ownerDocument) ||
      (comp && comp.el && comp.el.ownerDocument) || null;
    if (!doc) return null;
    var rbox = rectEl ? fRectBox(rectEl) : null;
    var abox = comp && comp.atomBox ? comp.atomBox : null;
    var cx = abox ? abox.x + abox.w / 2 : (rbox ? rbox.x + rbox.w / 2 : null);
    var cy = abox ? abox.y + abox.h / 2 : (rbox ? rbox.y + rbox.h / 2 : null);
    if (cx === null || cy === null) return null;
    var limit = abox ? Math.max(abox.w, abox.h) * 1.2 : 300;
    var best = null, bestD = limit * limit;
    var els = doc.querySelectorAll("#jsmeNomeclatureSVG ellipse, #jsmeNomeclatureSVG circle");
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (!fMulerSelectIsSelectionFill(el.getAttribute("fill"))) continue;
      var box = fRectBox(el);
      if (!box) continue;
      // Ownership guard: only shapes whose center sits inside the label's
      // own backing area (plus one glyph of slack) may be hidden — never a
      // neighboring atom's ellipse that merely happens to be close.
      if (rbox) {
        var pad = abox ? Math.max(abox.w, abox.h) * 0.5 : 0;
        var ex = box.x + box.w / 2, ey = box.y + box.h / 2;
        if (ex < rbox.x - pad || ex > rbox.x + rbox.w + pad ||
            ey < rbox.y - pad || ey > rbox.y + rbox.h + pad) continue;
      }
      var dx = (box.x + box.w / 2) - cx, dy = (box.y + box.h / 2) - cy;
      var d = dx * dx + dy * dy;
      if (d <= bestD) { bestD = d; best = el; }
    }
    return best;
  } catch (e) { return null; }
}

function fMulerSelectRoundedRectPath(x, y, w, h, r) {
  var rr = Math.max(0, Math.min(r, w / 2, h / 2));
  return "M" + (x + rr) + "," + y +
    "H" + (x + w - rr) +
    "Q" + (x + w) + "," + y + " " + (x + w) + "," + (y + rr) +
    "V" + (y + h - rr) +
    "Q" + (x + w) + "," + (y + h) + " " + (x + w - rr) + "," + (y + h) +
    "H" + (x + rr) +
    "Q" + x + "," + (y + h) + " " + x + "," + (y + h - rr) +
    "V" + (y + rr) +
    "Q" + x + "," + y + " " + (x + rr) + "," + y + "Z";
}

// Marker on a backplate this pass has already whitened. It makes the pass
// idempotent: a repaint that runs without a fresh JSME render (clear removes
// the previous path, fill is now white) must still redraw the C-sized path,
// while a green component backplate is never overpainted.
var MULER_COMPACT_WHITENED_ATTR = "data-muler-compact-white";

function fMulerSelectCompactPaintPass() {
  try {
    // Present keeps the selection state but never shows it (pushState degrades
    // to component-only); the rectless branch below must not leak a cyan path.
    if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return;
    var sel = fMulerSelectState();
    if (!sel || sel.active !== true || !Array.isArray(sel.atoms2D) || !sel.atoms2D.length) return;
    var comps = (typeof fMulerSelectCompacted === "function") ? fMulerSelectCompacted() : [];
    var selected = {};
    for (var ai = 0; ai < sel.atoms2D.length; ai++) selected[sel.atoms2D[ai]] = true;
    for (var ci = 0; ci < comps.length; ci++) {
      var cm = comps[ci];
      if (!cm || !Array.isArray(cm.members) || !cm.atomBox) continue;
      if (String(cm.symbol || "").toUpperCase() !== "C") continue;
      var anchor = cm.anchor + 1;
      if (!selected[anchor]) continue;
      var groupMemberSelected = false;
      for (var mi = 0; mi < cm.members.length; mi++) {
        if (cm.members[mi] !== anchor && selected[cm.members[mi]]) { groupMemberSelected = true; break; }
      }
      if (groupMemberSelected) continue;
      try {
        if (cm.rectEl) {
          var selfWhitened = cm.rectEl.getAttribute(MULER_COMPACT_WHITENED_ATTR) === "1";
          // Component-wins: a green backplate means the selection is not the
          // visible layer on this label, so it is never overpainted. Only a
          // cyan (selection) backplate or our own earlier white-out proceeds.
          if (!selfWhitened) {
            if (!fMulerSelectIsSelectionFill(cm.rectEl.getAttribute("fill"))) continue;
            cm.rectEl.setAttribute("fill", "white");
            cm.rectEl.setAttribute(MULER_COMPACT_WHITENED_ATTR, "1");
          }
        }
        var ell = fMulerSelectCompactAnchorEllipse(cm.rectEl, cm);
        if (ell) ell.setAttribute("display", "none");
        var labelEl = cm.el;
        if (!labelEl || !labelEl.parentNode) continue;
        var px = cm.atomBox.x - 6;
        var py = cm.atomBox.y - 8;
        var pw = cm.atomBox.w + 12;
        var ph = cm.atomBox.h + 16;
        var NS = "http://www.w3.org/2000/svg";
        var path = document.createElementNS(NS, "path");
        path.setAttribute("data-muler-compact-sel", String(anchor));
        path.setAttribute("d", fMulerSelectRoundedRectPath(px, py, pw, ph, 56));
        path.setAttribute("fill", MULER_SELECT_CYAN);
        path.setAttribute("pointer-events", "none");
        labelEl.parentNode.insertBefore(path, labelEl);
      } catch (eF) {}
    }
  } catch (e) {}
}

// Selection repaint entry (tail of fUpdateSVG + every selection change):
// legacy DOM cleanup, then the state push. Rendering itself is owned by the
// caller (fUpdateSVG renders right after its head push).
function fMulerSelectRepaint() {
  try {
    try { fMulerSelectClearLayer(); } catch (eC) {}
    try { if (typeof fMulerHoverClear === "function") fMulerHoverClear(); } catch (eHC) {}
    try { if (typeof fMulerSelectPushState === "function") fMulerSelectPushState(); } catch (eP2) {}
    try { fMulerSelectSync3DPicking(); } catch (eSync3) {}
    // v57 3D: repaint selection paint from state (no-op when off/empty/hidden).
    try { if (typeof fMulerSelectPush3D === "function") fMulerSelectPush3D(); } catch (eP3) {}
    try { fMulerSelectCompactPaintPass(); } catch (eCP) {}
  } catch (e) {}
}

// Click + Esc + hover wiring (bound once). Guards: select mode armed, no
// draft, no Present, molecule selected. Hover is rAF-throttled and paints a
// DOM-only ring (never the applet channel, never a re-render).
function fMulerSelectBindOnce() {
  try {
    if (typeof window !== "undefined" && window.__mulerSelBound) return;
    if (typeof window !== "undefined") window.__mulerSelBound = true;
    var host = null;
    try { host = document.getElementById("jsmeNomeclatureSVG"); } catch (eH) { host = null; }
    if (host && host.addEventListener) {
      host.addEventListener("click", function (e) {
        try {
          if (!(typeof fMulerSelectActive === "function" && fMulerSelectActive())) return;
          if (typeof window !== "undefined" && window.MulerDraft) return;
          if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return;
          if (typeof selectedMol === "undefined" || !selectedMol) return;
          if (typeof window !== "undefined") { try { window.__mulerSelShift = !!(e && e.shiftKey); } catch (eS) {} }
          var svg = null;
          try { svg = document.querySelector("#jsmeNomeclatureSVG svg"); } catch (eS2) { svg = null; }
          if (!svg) return;
          var g = null;
          try { var gs = svg.getElementsByTagName("g"); if (gs && gs.length) g = gs[0]; } catch (eG) { g = null; }
          var m = null;
          try { m = (g || svg).getScreenCTM(); } catch (eM) { m = null; }
          if (!m) return;
          var inv = null;
          try { inv = m.inverse(); } catch (eI) { return; }
          var q = null;
          try { q = new DOMPoint(e.clientX, e.clientY).matrixTransform(inv); } catch (eP) { return; }
          if (!q || !isFinite(q.x) || !isFinite(q.y)) return;
          var pick = null;
          try { pick = (typeof fMulerSelectPick === "function") ? fMulerSelectPick(q.x, q.y) : null; } catch (ePk) { pick = null; }
          if (pick && pick.ignore) return;
          if (!pick) {
            // empty canvas: clear the selection (nothing to pick)
            try { if (typeof fMulerSelectClear === "function") fMulerSelectClear(); } catch (eC) {}
            try { if (typeof fMulerQuizRefresh === "function") fMulerQuizRefresh(); } catch (eQR) {}
            try { if (typeof fMulerSelectRepaint === "function") fMulerSelectRepaint(); } catch (eR) {}
            try { if (typeof fUpdateSVG === "function") fUpdateSVG(); } catch (eU) {}
            return;
          }
          try { if (typeof fMulerSelectToggle === "function") fMulerSelectToggle(pick); } catch (eT) {}
          try { if (typeof fMulerSelectRepaint === "function") fMulerSelectRepaint(); } catch (eR) {}
          try { if (typeof fUpdateSVG === "function") fUpdateSVG(); } catch (eU2) {}
        } catch (e) {}
      });
      host.addEventListener("mousemove", function (e) {
        try {
          if (!(typeof fMulerSelectActive === "function" && fMulerSelectActive())) return;
          if (typeof window !== "undefined" && window.MulerDraft) return;
          if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return;
          if (typeof selectedMol === "undefined" || !selectedMol) return;
          if (typeof window === "undefined") return;
          try { window.__mulerHoverInside = true; } catch (eI) {}
          try { window.__mulerHoverX = (e && e.clientX) || 0; window.__mulerHoverY = (e && e.clientY) || 0; } catch (eXY) {}
          try { if (window.__mulerHoverRaf) return; } catch (eRF) {}
          var run = function () {
            try { window.__mulerHoverRaf = 0; } catch (eR0) {}
            try { if (typeof fMulerHoverTick === "function") fMulerHoverTick(); } catch (eT) {}
          };
          try {
            if (window.requestAnimationFrame) window.__mulerHoverRaf = window.requestAnimationFrame(run);
            else run();
          } catch (eF) { try { run(); } catch (eF2) {} }
        } catch (e) {}
      });
      host.addEventListener("mouseleave", function () {
        try { if (typeof window !== "undefined") window.__mulerHoverInside = false; } catch (eI2) {}
        try { if (typeof fMulerHoverClear === "function") fMulerHoverClear(); } catch (eC2) {}
      });
    }
    if (typeof document !== "undefined" && document.addEventListener) {
      document.addEventListener("keydown", function (e) {
        try {
          if (!e || e.key !== "Escape") return;
          var t = e.target || null;
          try {
            if (t && ((t.tagName && /^(INPUT|TEXTAREA|SELECT)$/i.test(t.tagName)) || t.isContentEditable)) return;
          } catch (eT) {}
          if (!(typeof fMulerSelectActive === "function" && fMulerSelectActive())) return;
          try {
            var s = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null;
            // v57 3D: 3D picks participate through their 2D mirror.
            if (s && (s.atoms2D.length || s.bonds2D.length || s.atoms3D.length || s.bonds3D.length)) {
              try { fMulerSelectClear(); } catch (eC) {}
              try { if (typeof fMulerQuizRefresh === "function") fMulerQuizRefresh(); } catch (eQR2) {}
              try { fMulerSelectRepaint(); } catch (eR) {}
              try { if (typeof fUpdateSVG === "function") fUpdateSVG(); } catch (eU) {}
            }
          } catch (eS) {}
        } catch (e) {}
      });
    }
  } catch (e) {}
}
try { if (typeof fMulerSelectBindOnce === "function") fMulerSelectBindOnce(); } catch (eB) {}
try { if (typeof fMulerSelectBind3DClear === "function") fMulerSelectBind3DClear(); } catch (eB3) {}

// 3D background double-tap clear (v57): empty 3D clicks are silent in JSmol
// (no pickCallback), and silent bond-line taps are indistinguishable from
// empty background page-side — so a single silent release does nothing. A
// second silent release nearby soon after is an explicit deselect. Any
// genuine pick breaks the chain (fast atom picking can never misfire it),
// and double-tapping an atom just toggles twice. Capture phase: JSmol
// canvas handlers run on bubble, so the pick flag may not be set yet at
// mouseup — the grace timer only classifies the release, it never clears.
// Silent-release classifier (v57 double-tap deselect). A silent release is
// a 3D press/release with minimal travel that produced no pick (empty
// background or beyond-radius bond tap — indistinguishable page-side). The
// first one only records time+position; a second one nearby soon after
// clears. Any genuine pick breaks the chain. Returns "pick"/"silent"/"clear"
// or "skip" (best-effort; callers ignore it).
function fMulerSelect3DSilentSettle(px, py) {
  try {
    if (typeof window !== "undefined" && window.__muler3DPickSeen) {
      try { window.__muler3DPickSeen = false; window.__muler3DSilentT = 0; } catch (eF) {}
      return "pick";
    }
    if (!fMuler3DModelReady()) return "skip";
    if (!(typeof fMulerSelectActive === "function" && fMulerSelectActive())) return "skip";
    if (typeof window !== "undefined" && window.MulerDraft) return "skip";
    if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return "skip";
    if (typeof selectedMol === "undefined" || !selectedMol) return "skip";
    var dblMs = 450, dblPx = 8;
    try { if (typeof MULER_SELECT_3D_DBL_MS === "number" && MULER_SELECT_3D_DBL_MS > 0) dblMs = MULER_SELECT_3D_DBL_MS; } catch (eDM) {}
    try { if (typeof MULER_SELECT_3D_DBL_PX === "number" && MULER_SELECT_3D_DBL_PX > 0) dblPx = MULER_SELECT_3D_DBL_PX; } catch (eDP) {}
    var now = (new Date()).getTime();
    var lastT = 0, lastX = 0, lastY = 0;
    try { lastT = (typeof window !== "undefined" && window.__muler3DSilentT) || 0; } catch (eG3) { lastT = 0; }
    try { lastX = (typeof window !== "undefined" && window.__muler3DSilentX) || 0; } catch (eGX) { lastX = 0; }
    try { lastY = (typeof window !== "undefined" && window.__muler3DSilentY) || 0; } catch (eGY) { lastY = 0; }
    var fire = false;
    try {
      if (lastT > 0 && (now - lastT) >= 0 && (now - lastT) <= dblMs &&
          Math.abs(px - lastX) <= dblPx && Math.abs(py - lastY) <= dblPx) fire = true;
    } catch (eC4) { fire = false; }
    try { if (typeof window !== "undefined") { window.__muler3DSilentT = now; window.__muler3DSilentX = px; window.__muler3DSilentY = py; } } catch (eW) {}
    if (!fire) return "silent";
    var _s = null, _any = false;
    try { _s = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null; } catch (eS2) { _s = null; }
    try {
      _any = !!(_s && ((Array.isArray(_s.atoms2D) && _s.atoms2D.length) || (Array.isArray(_s.bonds2D) && _s.bonds2D.length) ||
        (Array.isArray(_s.atoms3D) && _s.atoms3D.length) || (Array.isArray(_s.bonds3D) && _s.bonds3D.length)));
    } catch (eA2) { _any = false; }
    if (!_any) return "silent";
    try { if (typeof fMulerSelectClear === "function") fMulerSelectClear(); } catch (eC2) {}
    try { if (typeof fMulerQuizRefresh === "function") fMulerQuizRefresh(); } catch (eQR) {}
    try { if (typeof fMulerSelectRepaint === "function") fMulerSelectRepaint(); } catch (eR) {}
    try { if (typeof fUpdateSVG === "function") fUpdateSVG(); } catch (eU) {}
    return "clear";
  } catch (e) { return "skip"; }
}

function fMulerSelectBind3DClear() {
  try {
    if (typeof window !== "undefined" && window.__mulerSel3DBound) return;
    if (typeof window !== "undefined") window.__mulerSel3DBound = true;
    if (typeof document === "undefined" || !document.addEventListener) return;
    var in3D = function (e) {
      try {
        var h = document.getElementById("nomeclature3D");
        if (!h) return false;
        var t = (e && e.target) || null;
        if (!t) return false;
        if (typeof h.contains === "function") return !!h.contains(t);
        return h === t;
      } catch (eI) { return false; }
    };
    var live = function () {
      try {
        if (!(typeof fMulerSelectActive === "function" && fMulerSelectActive())) return false;
        if (typeof window !== "undefined" && window.MulerDraft) return false;
        if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return false;
        if (typeof selectedMol === "undefined" || !selectedMol) return false;
        return fMuler3DModelReady();
      } catch (eL) { return false; }
    };
    document.addEventListener("mousedown", function (e) {
      try {
        // Flush: classify any pending release NOW (its pick flag is final —
        // JSmol processed that mouseup synchronously long ago), so a fast
        // second tap never loses the first tap to the grace timer.
        try {
          if (typeof window !== "undefined" && window.__muler3DClearT) {
            try { clearTimeout(window.__muler3DClearT); } catch (eT) {}
            try { window.__muler3DClearT = 0; } catch (eZ0) {}
            var _fx = 0, _fy = 0;
            try { _fx = window.__muler3DPendX || 0; _fy = window.__muler3DPendY || 0; } catch (eP5) {}
            try { window.__muler3DPendX = 0; window.__muler3DPendY = 0; } catch (eP6) {}
            try { if (typeof fMulerSelect3DSilentSettle === "function") fMulerSelect3DSilentSettle(_fx, _fy); } catch (eF3) {}
          }
        } catch (eT) {}
        if (!e || (typeof e.button === "number" && e.button !== 0)) return;
        if (!in3D(e) || !live()) return;
        try {
          window.__muler3DDownX = e.clientX; window.__muler3DDownY = e.clientY;
          window.__muler3DDownT = (new Date()).getTime();
          window.__muler3DPickSeen = false;
        } catch (eR) {}
      } catch (e) {}
    }, true);
    document.addEventListener("mouseup", function (e) {
      try {
        if (!e || (typeof e.button === "number" && e.button !== 0)) return;
        if (!in3D(e) || !live()) return;
        var px = 6, ms = 250, downMs = 2000;
        try { if (typeof MULER_SELECT_3D_CLICK_PX === "number" && MULER_SELECT_3D_CLICK_PX > 0) px = MULER_SELECT_3D_CLICK_PX; } catch (eP) {}
        try { if (typeof MULER_SELECT_3D_CLICK_MS === "number" && MULER_SELECT_3D_CLICK_MS > 0) ms = MULER_SELECT_3D_CLICK_MS; } catch (eM) {}
        try { if (typeof MULER_SELECT_3D_DOWN_MS === "number" && MULER_SELECT_3D_DOWN_MS > 0) downMs = MULER_SELECT_3D_DOWN_MS; } catch (eD) {}
        var dx = 0, dy = 0, dt = -1, cx = 0, cy = 0;
        try {
          dx = e.clientX - window.__muler3DDownX; dy = e.clientY - window.__muler3DDownY;
          dt = (new Date()).getTime() - window.__muler3DDownT;
          cx = e.clientX; cy = e.clientY;
        } catch (eC) { return; }
        if (!isFinite(dx + dy + dt)) return;
        if (Math.abs(dx) > px || Math.abs(dy) > px) return; // rotate, not a click
        if (dt < 0 || dt > downMs) return; // stale press
        if (typeof window !== "undefined" && window.__muler3DPickSeen) {
          try { window.__muler3DPickSeen = false; } catch (eF) {}
          return;
        }
        // Single silent taps do nothing (bond tap vs background is
        // unknowable here); a second one nearby soon after deselects. The
        // timer only classifies the release once any pick had a chance
        // to arrive; a second press flushes the pending one (see mousedown).
        try { if (typeof window !== "undefined" && window.__muler3DClearT) clearTimeout(window.__muler3DClearT); } catch (eT2) {}
        try { if (typeof window !== "undefined") { window.__muler3DPendX = cx; window.__muler3DPendY = cy; } } catch (eP2) {}
        try {
          window.__muler3DClearT = setTimeout(function () {
            try {
              if (typeof window !== "undefined") {
                try { window.__muler3DClearT = 0; } catch (eZ) {}
                var _sx = 0, _sy = 0;
                try { _sx = window.__muler3DPendX || 0; _sy = window.__muler3DPendY || 0; } catch (eP3) {}
                try { window.__muler3DPendX = 0; window.__muler3DPendY = 0; } catch (eP4) {}
                if (typeof fMulerSelect3DSilentSettle === "function") fMulerSelect3DSilentSettle(_sx, _sy);
              }
            } catch (e) {}
          }, ms);
        } catch (eT3) {}
      } catch (e) {}
    }, true);
  } catch (e) {}
}

// Auto-linearize preference (Ρυθμίσεις, default ON): Submit tidies school
// drawings to the canonical linear layout before the naming run. Missing
// checkbox fails open (standardized path).
function fMolDraftAutoLinearizeOn() {
  try {
    var el = document.getElementById("autoLinearizeCheck");
    if (!el) return true;
    return el.classList.contains("selectedCheck");
  } catch (e) { return true; }
}

function fMolDraftEnter(mode) {
  if (fMolDraftPresenting()) return;
  if (window.MulerDraft || window.MulerDraftAcquisition) return;
  try {
    var _sw = document.getElementById("originalJSMECheck");
    if (!_sw || !(_sw.classList && _sw.classList.contains("selectedCheck"))) {
      fMolDraftToast(fMolDraftT("draftEnableFirst", "Enable drawing from Settings first."));
      return;
    }
  } catch (eSw) {
    fMolDraftToast(fMolDraftT("draftEnableFirst", "Enable drawing from Settings first."));
    return;
  }
  var sourceMol = null;
  try { sourceMol = (typeof selectedMol !== "undefined") ? selectedMol : null; } catch (eS) { sourceMol = null; }
  if (mode === "edit") {
    if (!sourceMol || typeof nameExamples === "undefined" || !nameExamples[sourceMol]) {
      fMolDraftToast(fMolDraftT("editNeedsMol", "Select a molecule to edit."));
      return;
    }
  }
  var variant = "condensed";
  try { variant = (typeof mode2D !== "undefined") ? mode2D : "condensed"; } catch (eV) {}
  var had3D = false;
  try {
    var b3 = document.getElementById("view3DBtn");
    had3D = !!(b3 && b3.classList.contains("active"));
  } catch (eB) { had3D = false; }
  window.MulerDraft = { mode: mode, sourceMol: sourceMol, variant: variant, had3D: had3D };
  try { window.MulerDraft._epoch = (window._MulerDraftEpoch = (window._MulerDraftEpoch || 0) + 1); } catch (eEp) { try { window.MulerDraft._epoch = Date.now(); } catch (eEp2) {} }
  try { window.MulerDraft._submitId = 0; window.MulerDraft.accepting = false; } catch (eSi) {}
  // Fresh canvas on New (blank drawing, naming placeholder): clear any sticky
  // hidden set so the preview starts fully visible. Edit keeps the live set
  // (template is the visible variant the author was just looking at).
  try { if (mode === "new" && typeof window !== "undefined") window.nameHiddenComps = []; } catch (eH) {}
  // Update-in-place only when an Edit redraws the SAME molecule (beautify).
  // Edit producing a different molecule always forks a new custom entry;
  // stored (141) templates are never overwritten (option a). Source identity
  // (SMILES + PubChem CID) is captured here; sameness is decided at
  // Submit/Accept time via fMolDraftIsSameMolecule (CID-first, SMILES fallback).
  try {
    window.MulerDraft.sourceIsCustom = !!(mode === "edit" && sourceMol &&
      typeof window.nameExamplesCustom !== "undefined" && window.nameExamplesCustom &&
      Object.prototype.hasOwnProperty.call(window.nameExamplesCustom, sourceMol));
  } catch (eSc) { try { window.MulerDraft.sourceIsCustom = false; } catch (eS2) {} }
  try {
    var _src = (typeof nameExamples !== "undefined" && sourceMol) ? nameExamples[sourceMol] : null;
    window.MulerDraft.sourceSmiles = (_src && _src.smiles) || "";
    window.MulerDraft.sourceCid = (_src && _src.pubchemCID != null) ? String(_src.pubchemCID) : "";
  } catch (eSrc) { try { window.MulerDraft.sourceSmiles = ""; window.MulerDraft.sourceCid = ""; } catch (eS3) {} }
  try {
    window.MulerDraft.acceptKey = window.MulerDraft.sourceIsCustom ? "draftUpdate" : "draftAccept";
  } catch (eAk) {}
  // Drafting chrome: dim every other control cluster (CSS) + light the entry
  // button. Undone symmetrically in fMolDraftCancel.
  try {
    var _pc = document.getElementById("pageContainer");
    if (_pc) _pc.classList.add("drafting");
  } catch (eP) {}
  try {
    var _eb = document.getElementById(mode === "edit" ? "editMolBtn" : "newMolBtn");
    if (_eb) _eb.classList.add("active");
  } catch (eAb) {}
  // Mutual exclusion: the other entry goes visually inactive while a draft
  // is live (its handler early-returns anyway; this is display only).
  try {
    var _ob = document.getElementById(mode === "edit" ? "newMolBtn" : "editMolBtn");
    if (_ob) _ob.classList.add("btnInactive");
  } catch (eOb) {}
  // Selection mode (v56) cannot survive draft entry: the draft clears naming
  // and highlights, so an armed selection would point at stale state. Exit
  // the mode and dim its button (same display-only contract as above; the
  // toggle handler early-returns while a draft is live). Teardown restores
  // via the normal fSelectMol → fMolDraftSyncButtons path.
  try {
    if (typeof window !== "undefined" && window.MulerUserSelection && window.MulerUserSelection.active === true) {
      window.MulerUserSelection.active = false;
      try { window.MulerUserSelection.atoms2D = []; window.MulerUserSelection.bonds2D = []; window.MulerUserSelection.atoms3D = []; window.MulerUserSelection.bonds3D = []; window.MulerUserSelection.groups = []; } catch (eClr) {}
      try { if (typeof fMulerSelectPush === "function") fMulerSelectPush(); } catch (ePush) {}
      try { if (typeof fMulerHoverClear === "function") fMulerHoverClear(); } catch (eHC2) {}
      try { if (typeof fMulerQuizDisarm === "function") fMulerQuizDisarm(); } catch (eQD3) {}
    }
  } catch (eSel) {}
  try {
    var _selB = document.getElementById("selectAtomsBtn");
    if (_selB) { _selB.classList.remove("active"); _selB.classList.add("btnInactive"); }
  } catch (eSb) {}
  try {
    var _selSvg = document.getElementById("jsmeNomeclatureSVG");
    if (_selSvg) _selSvg.classList.remove("selecting");
  } catch (eSv) {}
  // Edit applet must exist (constructed at boot; guarded so a draft-only
  // failure never strands the UI mid-chrome — nothing visible changed yet).
  try {
    if (typeof jsmeEditDraftApplet === "undefined" || !jsmeEditDraftApplet ||
        typeof jsmeEditDraftApplet.readMolFile !== "function") {
      fMolDraftToast("Editor unavailable — reload the page.");
      return;
    }
  } catch (eEA) { return; }
  // 3D away (hide, not zap — viewport fragility), then the editor view.
  try { if (had3D && typeof fToggleViewer3D === "function") fToggleViewer3D(); } catch (e3) {}
  // The display applet stays hidden throughout the draft (depict pipeline
  // untouched); the drawing lives in the dedicated edit applet below.
  fMolDraftShowEditor();
  if (mode === "edit") {
    var mol = fMolDraftVariantMol();
    if (!mol) {
      window.MulerDraft = null;
      try {
        var _pc2 = document.getElementById("pageContainer");
        if (_pc2) _pc2.classList.remove("drafting");
      } catch (eP2) {}
      try {
        var _eb2 = document.getElementById("editMolBtn");
        if (_eb2) _eb2.classList.remove("active");
        var _ob2 = document.getElementById("newMolBtn");
        if (_ob2) _ob2.classList.remove("btnInactive");
      } catch (eAb2) {}
      try { $("#jsmeEditDraft").addClass("hide"); } catch (eH2) {}
      fMolDraftToast(fMolDraftT("editNeedsMol", "Select a molecule to edit."));
      return;
    }
    try { jsmeEditDraftApplet.readMolFile(mol); } catch (eM) {}
    try { if (typeof molZoom2D !== "undefined") jsmeEditDraftApplet.setMolecularAreaScale(molZoom2D); } catch (eZ) {}
    // Status names the edited representation: the author always knows which
    // slot Accept will write (siblings are generated, never touched by hand).
    var _vLab = "";
    try { _vLab = fMolDraftT(variant === "condensedZigZag" ? "skeletal" : variant, variant); } catch (eVl) { _vLab = ""; }
    var _slotHint = "";
    try { _slotHint = fMolDraftT("draftSlotOnly", "only this view updates"); } catch (eSh) { _slotHint = ""; }
    var _editStatus = fMolDraftT("draftEdit", "Editing") + ": " + sourceMol + (_vLab ? " — " + _vLab : "") + (_slotHint ? " — " + _slotHint : "");
    fMolDraftClearNaming(_editStatus);
    fMolDraftShowBar(_editStatus);
  } else {
    var _newHint = "";
    try { _newHint = fMolDraftT("draftAllViews", "all 3 views will be generated"); } catch (eNh) { _newHint = ""; }
    var _newStatus = fMolDraftT("draftNew", "New molecule (draft)") + (_newHint ? " — " + _newHint : "");
    try { jsmeEditDraftApplet.clear(); } catch (eC) {}
    fMolDraftClearNaming(_newStatus);
    fMolDraftShowBar(_newStatus);
  }
  // The edit applet is edit-mode by construction — no toggle, no enforcement.
  setTimeout(function () { try { if (typeof fResizeViewers === "function") fResizeViewers(); } catch (eR2) {} }, 0);
  try { fMolDraftWatchEdits(); } catch (eW) {}
}

function fEditMolDraft() {
  fMolDraftEnter("edit");
}
function fNewMolDraft() {
  fMolDraftEnter("new");
}
// ── Submit: engine + PubChem preview (v54 Stage 2, Step 3) ─────────────────
// Sandbox mirror of fLoadMol2D's analysis tail (read applet -> globals ->
// engine -> overlay), minus the stored-entry classification write:
// selectedMol stays untouched, so Cancel restores via fSelectMol.
function fMolDraftHasRing() {
  // Union-find cycle check over the parsed 2D bond pairs (1-based [a1,a2]).
  // Engine-independent: core only warns-and-falls-back on cyclic input.
  try {
    if (typeof bondList === "undefined" || !bondList || !bondList.length) return false;
    var parent = {};
    var find = function (x) {
      while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; }
      return x;
    };
    for (var i = 0; i < bondList.length; i++) {
      var b = bondList[i];
      if (!b || b[0] == null || b[1] == null) continue;
      var a = b[0], c = b[1];
      if (!(a in parent)) parent[a] = a;
      if (!(c in parent)) parent[c] = c;
      if (find(a) === find(c)) return true;
      parent[find(a)] = find(c);
    }
  } catch (eR) {}
  return false;
}

function fMolDraftNorm(s) {
  return String(s == null ? "" : s).toLowerCase().replace(/\s+/g, " ").trim();
}
// Shared PubChem 3-way match (systematic/retained/title, stereo-stripped):
// feeds the EN auto-check and the PubChem-row glyph alike, so they agree.
function fMolDraftPCMatch(engineEN, hit) {
  try {
    if (!engineEN || !hit || typeof fNormNoStereo !== "function") return false;
    var a = fNormNoStereo(String(engineEN).toLowerCase().trim());
    if (!a) return false;
    var s = fNormNoStereo(String((hit && (hit.systematic || hit.iupacEN)) || "").toLowerCase().trim());
    var r = fNormNoStereo(String((hit && (hit.iupacPubchem || hit.iupac)) || "").toLowerCase().trim());
    var t = fNormNoStereo(String((hit && (hit.title || hit.titlePubchem)) || "").toLowerCase().trim());
    return !!((s && a === s) || (r && a === r) || (t && a === t));
  } catch (e) { return false; }
}

// Stray-H guard for verbatim slots (H32 class): hand geometry can misplace an
// H a full bond length off (right y, wrong x) and a verbatim Accept would keep
// it forever. Reference is the drawing's own H distribution (min H-bond
// length): flags H longer than 1.75× the shortest sibling — uniform hand,
// legacy and regen H all pass (diagonal ≈1.0×, O–H variance covered); a
// 2.24× stray like H32 flags. Plus unbonded H. Returns list.
function fMolDraftStrayH(molText) {
  var out = [];
  try {
    if (typeof fParseMolV2000 !== "function" || !molText) return out;
    var p = fParseMolV2000(molText);
    if (!p || !p.atoms || !p.atoms.length || !p.bonds) return out;
    var isH = function (el) { return el === "H" || el === "h"; };
    var hLens = [], i;
    for (i = 0; i < p.bonds.length; i++) {
      var b = p.bonds[i];
      if (!b || b[0] == null || b[1] == null) continue;
      var a = p.atoms[b[0] - 1], c = p.atoms[b[1] - 1];
      if (!a || !c) continue;
      if ((isH(a.el) && !isH(c.el)) || (!isH(a.el) && isH(c.el))) {
        var hd = Math.hypot(a.x - c.x, a.y - c.y);
        if (hd > 1e-9 && isFinite(hd)) hLens.push(hd);
      }
    }
    if (!hLens.length) return out;
    hLens.sort(function (x, y) { return x - y; });
    var refH = hLens[0];
    for (var hI = 0; hI < p.atoms.length; hI++) {
      if (!isH(p.atoms[hI].el)) continue;
      var par = -1;
      for (var q = 0; q < p.bonds.length; q++) {
        var bb = p.bonds[q];
        if (!bb || bb[0] == null) continue;
        if (bb[0] - 1 === hI) { par = bb[1] - 1; break; }
        if (bb[1] - 1 === hI) { par = bb[0] - 1; break; }
      }
      if (par < 0) { out.push({ h: hI + 1, parent: 0, dist: -1, ratio: -1 }); continue; }
      var dd = Math.hypot(p.atoms[hI].x - p.atoms[par].x, p.atoms[hI].y - p.atoms[par].y);
      if (dd > 1.75 * refH) out.push({ h: hI + 1, parent: par + 1, dist: +dd.toFixed(3), ratio: +(dd / refH).toFixed(2) });
    }
  } catch (e) {}
  return out;
}

// Same-molecule test for the Edit rule (CID-first, normalized-SMILES
// fallback): redraw/beautify keeps atom order unstable in JSME SMILES, so a
// raw string compare false-negatives on pure layout edits. Every
// Accept-able draft has a PubChem CID today (3D gate), making CID the
// primary identity; SMILES covers the future no-CID RDKit path.
function fMolDraftIsSameMolecule() {
  var d = null;
  try { d = window.MulerDraft; } catch (eD) { return false; }
  if (!d || d.mode !== "edit" || !d.sourceMol) return false;
  try {
    var draftCid = (d.pubchem && d.pubchem.cid != null) ? String(d.pubchem.cid) : "";
    var srcCid = (d.sourceCid != null && d.sourceCid !== "") ? String(d.sourceCid) : "";
    if (draftCid && srcCid) return draftCid === srcCid;
  } catch (eC) {}
  try {
    if (d.smiles && d.sourceSmiles && typeof fMolDraftNorm === "function") {
      return fMolDraftNorm(d.smiles) === fMolDraftNorm(d.sourceSmiles);
    }
  } catch (eS) {}
  return false;
}

// Accept-button label follows the runtime decision: custom-template Edit
// shows Update only while the draft is the same molecule, else Accept.
// Called after Submit resolves identity and at Accept time; updates the
// live button in place without rebuilding the bar (status text preserved).
function fMolDraftRefreshAcceptKey() {
  var d = null;
  try { d = window.MulerDraft; } catch (eD) { return; }
  if (!d) return;
  try {
    var want = "draftAccept";
    if (d.mode === "edit" && d.sourceIsCustom) {
      if (!d.submitted) want = "draftUpdate";
      else want = fMolDraftIsSameMolecule() ? "draftUpdate" : "draftAccept";
    }
    if (d.acceptKey !== want) {
      d.acceptKey = want;
      var ba = null;
      try { ba = document.getElementById("molDraftAcceptBtn"); } catch (eB) { ba = null; }
      if (ba) {
        var tA = fMolDraftT(want, want === "draftUpdate" ? "Update" : "Accept");
        ba.textContent = tA;
        try { ba.setAttribute("data-tooltip", tA); } catch (eT) {}
      }
    }
  } catch (eR) {}
}

// Expanded structural formula for the menu (v54 Stage 2, Step 4 fix).
// Regenerates the stored-data convention (CH3CH(Br)CH3, CH2=C(CH3)2) from the
// live post-submit globals, so accepted molecules label like stored ones:
// main-chain walk, SYM+Hn per atom (H from standard valence minus heavy-bond
// orders — self-consistent with explicit/implicit H alike), single bonds
// implicit, =/_ emitted, branches parenthesized. Reads sandbox state;
// selectedMol untouched. Returns "" on any gap (menu falls back to the key).
var MOLDRAFT_STDVALENCE = { C: 4, N: 3, O: 2, F: 1, Cl: 1, Br: 1, I: 1 };

function fMolDraftBondOrderMap() {
  var map = {};
  try {
    if (typeof bondList === "undefined" || !bondList) return map;
    for (var i = 0; i < bondList.length; i++) {
      var b = bondList[i];
      if (!b || b[0] == null || b[1] == null) continue;
      var a = Math.min(b[0], b[1]), c = Math.max(b[0], b[1]), o = b[2] || 1;
      var k = a + "-" + c;
      if (!map[k] || map[k] < o) map[k] = o;
    }
  } catch (eM) {}
  return map;
}

function fMolDraftAtomEl(n) {
  try {
    var t = allAtomsTypeList[n - 1];
    return (t == null ? "" : String(t));
  } catch (eT) { return ""; }
}

function fMolDraftHeavyNbs(n) {
  var out = [], seen = {};
  try {
    if (typeof bondList === "undefined" || !bondList) return out;
    for (var i = 0; i < bondList.length; i++) {
      var b = bondList[i];
      if (!b || b[0] == null || b[1] == null) continue;
      var other = (b[0] === n) ? b[1] : (b[1] === n) ? b[0] : null;
      if (other == null || seen[other]) continue;
      var t = fMolDraftAtomEl(other);
      if (!t || t === "H" || t === "h") continue;
      seen[other] = true;
      out.push({ atom: other, order: b[2] || 1 });
    }
  } catch (eN) {}
  return out;
}

function fMolDraftHCount(el, nbs) {
  var v = MOLDRAFT_STDVALENCE[el];
  if (v == null) return 0;
  var used = 0;
  for (var i = 0; i < nbs.length; i++) used += nbs[i].order;
  return Math.max(0, v - used);
}

function fMolDraftGroup(el, h) {
  if (!el) return "";
  if (el === "H") return "H";
  return el + (h >= 1 ? ("H" + (h > 1 ? h : "")) : "");
}

function fMolDraftBondSym(o) { return o === 3 ? "_" : (o === 2 ? "=" : ""); }

function fMolDraftExcl(self) { var m = {}; try { m[self] = true; } catch (eX) {} return m; }

// Recursive node renderer. endForm: "first" | "mid" | "last" | "single"
// (chain members, end-aware FG terminals) or "branch" (substituent roots,
// trailing forms). Depth-guarded: submit already ring-rejected, this is belt
// and braces against corrupted globals.
function fMolDraftRenderNode(atom, excluded, endForm, depth) {
  if ((depth || 0) > 25) return "";
  var el = fMolDraftAtomEl(atom);
  if (!el || el === "H") return "";
  var allNbs = [];
  try { allNbs = fMolDraftHeavyNbs(atom); } catch (eN) {}
  var nbs = [];
  for (var i = 0; i < allNbs.length; i++) {
    if (excluded && excluded[allNbs[i].atom]) continue;
    nbs.push(allNbs[i]);
  }
  // H counts ALL heavy bonds (chain members included); only branch
  // rendering excludes chain neighbors.
  var h = fMolDraftHCount(el, allNbs);
  // Single heavy-atom molecules: literal water/ammonia (methane etc. fall
  // through to the generic path below).
  if (endForm === "single" && nbs.length === 0) {
    if (el === "O" && h === 2) return "H2O";
    if (el === "N" && h === 3) return "NH3";
  }
  if (el === "C") {
    var oxDouble = null, triN = null, ohC = null;
    for (var j = 0; j < nbs.length; j++) {
      var ce = fMolDraftAtomEl(nbs[j].atom);
      if (nbs[j].order === 2 && ce === "O" && !oxDouble) oxDouble = nbs[j];
      else if (nbs[j].order === 3 && ce === "N" && !triN) triN = nbs[j];
      else if (nbs[j].order === 1 && ce === "O" && !ohC) {
        var onb = fMolDraftHeavyNbs(nbs[j].atom);
        if (fMolDraftHCount("O", onb) >= 1) ohC = nbs[j];
      }
    }
    var rest = function (skip) {
      var r = [];
      for (var q = 0; q < nbs.length; q++) {
        if (skip && nbs[q].atom === skip.atom) continue;
        r.push(nbs[q]);
      }
      return r;
    };
    // Acid carbon: =O + -OH (always terminal by valence; branch roots trail).
    if (oxDouble && ohC) {
      if (endForm === "single") return "HCOOH";
      if (endForm === "first") return "HOOC";
      return "COOH";
    }
    // Formaldehyde (only heavy neighbor is the =O): literal.
    if (oxDouble && h >= 2 && nbs.length === 1) return "HCHO";
    // Aldehyde carbon: H + =O, at least one C neighbor (true acyl R-CHO;
    // formyl/ester -OR neighbors fall through to the keto drop below).
    // NOTE: scanned over ALL neighbors — the R group is usually the (excluded)
    // chain neighbor.
    var hasC = false;
    for (var k = 0; k < allNbs.length; k++) {
      if (oxDouble && allNbs[k].atom === oxDouble.atom) continue;
      if (fMolDraftAtomEl(allNbs[k].atom) === "C") { hasC = true; break; }
    }
    if (oxDouble && h >= 1 && !ohC && hasC) {
      return endForm === "first" ? "O=CH" : "CH=O";
    }
    // Keto/ester/formyl carbonyl: absorb the =O (H prefix keeps formyl HCO).
    if (oxDouble && !ohC) {
      return (h >= 1 ? "H" : "") + "CO" + fMolDraftRenderChildren(rest(oxDouble), h, atom, (depth || 0) + 1);
    }
    // Nitrile carbon (majority stored style drops the triple marker: CN).
    if (triN && !oxDouble && !ohC) {
      return "C" + "N" + fMolDraftRenderChildren(rest(triN), h, atom, (depth || 0) + 1);
    }
  }
  return fMolDraftGroup(el, h) + fMolDraftRenderChildren(nbs, h, atom, (depth || 0) + 1);
}

function fMolDraftRenderChildren(kids, h, self, depth) {
  if (!kids || !kids.length) return "";
  if ((depth || 0) > 25) return "";
  var ds = [];
  for (var i = 0; i < kids.length; i++) {
    var el = fMolDraftAtomEl(kids[i].atom);
    var nb = fMolDraftHeavyNbs(kids[i].atom);
    var own = [];
    for (var w = 0; w < nb.length; w++) {
      if (nb[w].atom === self) continue;
      own.push(nb[w]);
    }
    ds.push({ atom: kids[i].atom, order: kids[i].order, el: el,
      h: fMolDraftHCount(el, nb), leaf: own.length === 0 });
  }
  if (ds.length === 1) {
    var c = ds[0];
    if (c.order === 1) {
      // Alkoxy branch (-O-R, esters): inline O + tail (COOCH3, not CO(OCH3)).
      // The O is H-free with its own carbon tail; -OH keeps parens below.
      if (c.el === "O" && c.h === 0) {
        var oOwn = [];
        try {
          var oNb = fMolDraftHeavyNbs(c.atom);
          for (var oI = 0; oI < oNb.length; oI++) {
            if (oNb[oI].atom === self) continue;
            oOwn.push(oNb[oI]);
          }
        } catch (eO) {}
        if (oOwn.length >= 1) {
          // Forced inline (h=2): the -R tail linearizes like an ethyl branch.
          return "O" + fMolDraftRenderChildren(oOwn, 2, c.atom, depth);
        }
      }
      var sub = fMolDraftRenderNode(c.atom, fMolDraftExcl(self), "branch", depth);
      if (h === 2) return sub; // inline (trailing CH2OH, ethyl branches)
      return "(" + sub + ")"; // (Br) (OH) (CH3) (NO2) ...
    }
    // Multiple-bonded single child: inline, marker kept (generic fallback;
    // aldehyde/nitrile FG forms are handled in fMolDraftRenderNode).
    if (c.leaf) {
      if (c.order === 3 && c.el === "N") return "N";
      return fMolDraftBondSym(c.order) + fMolDraftGroup(c.el, c.h);
    }
    return fMolDraftBondSym(c.order) + fMolDraftRenderNode(c.atom, fMolDraftExcl(self), "branch", depth);
  }
  var allSingle = true, uniformOrder = true;
  for (var s2 = 0; s2 < ds.length; s2++) {
    if (ds[s2].order !== 1) { allSingle = false; }
    if (ds[s2].order !== ds[0].order) { uniformOrder = false; }
  }
  if (allSingle || uniformOrder) {
    var subs = [];
    for (var s3 = 0; s3 < ds.length; s3++) subs.push(fMolDraftRenderNode(ds[s3].atom, fMolDraftExcl(self), "branch", depth));
    var first = subs[0], same = true;
    for (var s4 = 1; s4 < subs.length; s4++) {
      if (subs[s4] !== first) { same = false; break; }
    }
    if (same) {
      var n = subs.length, cnt = n > 1 ? n : "";
      var bare = /^[A-Z][a-z]?$/.test(first);
      if (bare && first === "O") return "O" + cnt; // NO2 inner (=O twins merge)
      if (allSingle && bare && h >= 1 && /^(F|Cl|Br|I)$/.test(first)) return first + cnt; // CHCl2
      if (allSingle) return "(" + first + ")" + cnt; // (Cl)2 (CH3)2
      // Uniform multiple-bond twins that are not bare O (no stored-Data
      // precedent): fall through to the parenthesized path below.
    }
  }
  var out = "";
  for (var m = 0; m < ds.length; m++) {
    out += "(" + (ds[m].order === 1 ? "" : fMolDraftBondSym(ds[m].order)) +
      fMolDraftRenderNode(ds[m].atom, fMolDraftExcl(self), "branch", depth) + ")";
  }
  return out;
}

function fMolDraftExpandedFormula() {
  try {
    if (typeof mainChainAtomsList === "undefined" || !mainChainAtomsList || !mainChainAtomsList.length) return "";
    if (typeof allAtomsTypeList === "undefined" || !allAtomsTypeList) return "";
    var chain = mainChainAtomsList.slice();
    var orderMap = fMolDraftBondOrderMap();
    var texts = [];
    for (var i = 0; i < chain.length; i++) {
      var ex = {};
      if (i > 0) ex[chain[i - 1]] = true;
      if (i < chain.length - 1) ex[chain[i + 1]] = true;
      var ef = chain.length === 1 ? "single" : (i === 0 ? "first" : (i === chain.length - 1 ? "last" : "mid"));
      texts.push(fMolDraftRenderNode(chain[i], ex, ef, 0));
    }
    var out = "";
    for (var k = 0; k < texts.length; k++) {
      out += texts[k];
      if (k < texts.length - 1) {
        var a = Math.min(chain[k], chain[k + 1]), c = Math.max(chain[k], chain[k + 1]);
        out += fMolDraftBondSym(orderMap[a + "-" + c] || 1);
      }
    }
    return out;
  } catch (eF) { return ""; }
}

function fMolDraftEsc(s) {
  return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

// Italicize detached `sec-`/`tert-` prefixes (IUPAC: italic + hyphen) for
// DISPLAY HTML only — engines, oracles, matching, tooltips (title attrs)
// and storage keep the raw strings. `withN` adds the `(n-)` table prefix.
// Tag-safe (attributes never touched) and idempotent (re-wrapping collapses
// to exactly one <i>). Letter-boundary guarded so `butan-2-yl`/`isopropyl`
// never match (`n` needs a non-letter before it, e.g. `(n-)`).
function fMulerItalicSecTert(html, withN) {
  try {
    var src = String(html == null ? "" : html);
    if (src.indexOf("sec-") < 0 && src.indexOf("tert-") < 0 && src.indexOf("Sec-") < 0 && src.indexOf("Tert-") < 0 && (!withN || !/(^|[^A-Za-z])[nN]-/.test(src))) return src;
    var parts = src.split(/(<[^>]*>)/);
    for (var i = 0; i < parts.length; i++) {
      if (!parts[i] || parts[i].charAt(0) === "<") continue;
      var t = parts[i];
      // Idempotence: a bare prefix flanked by <i>...</i> parts is already
      // wrapped from a previous pass — leave it alone (nested <i> would
      // render the same but pollute the markup and the overview cache).
      var prevTag = (i > 0 && parts[i - 1].charAt(0) === "<") ? parts[i - 1] : "";
      var nextTag = (i + 1 < parts.length && parts[i + 1].charAt(0) === "<") ? parts[i + 1] : "";
      var tTrim = t.replace(/^\s+|\s+$/g, "");
      if (/^(sec-|tert-|Sec-|Tert-|SEC-|TERT-)$/.test(tTrim) && /^<i\b[^>]*>$/.test(prevTag) && /^<\/i\s*>$/.test(nextTag)) continue;
      t = t.replace(/(^|[^A-Za-z])(sec-|tert-|Sec-|Tert-|SEC-|TERT-)/g, "$1<i>$2</i>");
      if (withN) t = t.replace(/(^|[^A-Za-z])(n-|N-)/g, "$1<i>$2</i>");
      parts[i] = t;
    }
    return parts.join("");
  } catch (e) { try { return String(html); } catch (e2) { return ""; } }
}

function fMolDraftReadDrawing() {
  // The drawing lives in the dedicated edit applet (display applet untouched).
  var molText = "", smiles = "", hasAny = false;
  try {
    if (typeof jsmeEditDraftApplet !== "undefined" && jsmeEditDraftApplet) {
      try { if (typeof jsmeEditDraftApplet.hasMolecule === "function") hasAny = !!jsmeEditDraftApplet.hasMolecule(); } catch (eH) {}
      try { if (typeof jsmeEditDraftApplet.molFile === "function") molText = jsmeEditDraftApplet.molFile(); } catch (eM) {}
      try {
        if (typeof jsmeEditDraftApplet.getSmiles === "function") smiles = jsmeEditDraftApplet.getSmiles();
        else if (typeof jsmeEditDraftApplet.smiles === "function") smiles = jsmeEditDraftApplet.smiles();
      } catch (eS) {}
    }
  } catch (eA) {}
  smiles = String(smiles || "").trim();
  if (!hasAny) hasAny = !!(molText && molText.length > 200) || !!smiles;
  return { molText: molText || "", smiles: smiles, hasAny: hasAny };
}

// Tri-state name verdict (correct/wrong/unconfirmed) per predicted language.
// Human verdict always wins: setting marks the row touched, which disables
// the EN PubChem auto-check for this Submit. Re-render only — no engine,
// chain or 3D state touched.
function fMolDraftSetVerdict(lang, state) {
  try {
    if (fMolDraftPresenting()) return;
    var d = window.MulerDraft;
    if (!d || !d.submitted) return;
    if (state !== "correct" && state !== "wrong") state = "unconfirmed";
    if (lang === "en") { d.verdictEN = state; d.touchedEN = true; }
    else { d.verdictGR = state; d.touchedGR = true; }
    fMolDraftRenderPreview();
  } catch (eV) {}
}

// Segmented verdict control ([✓|?|✕]) for one predicted-name row. Radio
// behavior: exactly one segment lit. Tooltips follow the session language;
// the EN correct segment notes PubChem auto-validation when applicable.
function fMolDraftVerdictCtrl(lang, verdict, autoNote) {
  try {
    var states = ["correct", "unconfirmed", "wrong"];
    var glyph = { correct: "✓", unconfirmed: "?", wrong: "✕" };
    var tipKey = { correct: "draftCorrect", unconfirmed: "draftUnconfirmed", wrong: "draftWrong" };
    var tipFb = { correct: "Correct", unconfirmed: "Unconfirmed", wrong: "Wrong" };
    var out = "<span class='draftVerdict' data-dvlang='" + lang + "'>";
    for (var i = 0; i < states.length; i++) {
      var s = states[i];
      var tip = fMolDraftEsc(fMolDraftT(tipKey[s], tipFb[s]));
      if (autoNote && s === "correct") tip += " — " + fMolDraftEsc(fMolDraftT("draftAutoPubchem", "Validated by PubChem"));
      out += "<button type='button' class='draftVBtn" + (verdict === s ? " active" : "") + "' data-v='" + s + "'" +
        " data-tooltip='" + tip + "' aria-pressed='" + (verdict === s ? "true" : "false") + "'" +
        " onclick='fMolDraftSetVerdict(\"" + lang + "\",\"" + s + "\")'>" + glyph[s] + "</button>";
    }
    return out + "</span>";
  } catch (eC) { return ""; }
}

// v55 tiered 3D status rows: source-labeled row on success (local flagged
// provisional), fetching note while pending, all-miss note only at end.
function fMolDraftSDF3DStatusHTML(d) {
  try {
    if (d && d.sdf3D && d.sdf3DSource) {
      var _k = d.sdf3DSource === "pubchem-jsmol" ? "draft3DPubchemJsmol" : (d.sdf3DSource === "pubchem-fetch" ? "draft3DPubchemFetch" : (d.sdf3DSource === "pubchem" ? "draft3DPubchem" : (d.sdf3DSource === "remote" ? "draft3DRemote" : (d.sdf3DSource === "jsmol-unminimized" ? "draft3DUnmin" : "draft3DLocal"))));
      var _f = d.sdf3DSource === "pubchem-jsmol" ? "3D: PubChem via JSmol" : (d.sdf3DSource === "pubchem-fetch" ? "3D: PubChem via fetch" : (d.sdf3DSource === "pubchem" ? "3D: PubChem" : (d.sdf3DSource === "remote" ? "3D: Cactus (JSmol)" : (d.sdf3DSource === "jsmol-unminimized" ? "3D: unminimized (local — needs review)" : "3D: local minimize (provisional — needs review)"))));
      var out = "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT(d.sdf3DStatus === "provisional" ? "draft3DProvisional" : _k, d.sdf3DStatus === "provisional" ? "3D: provisional local conformation (geometry and convergence unverified)" : _f)) + "</div>";
      if (d.sdf3DSource === "jsmol-unminimized") out += "<div class='draftOracleRow'><button type='button' class='viewerFullBtn draftMinBtn' onclick='fMolDraftManualMinimize()'>" + fMolDraftEsc(fMolDraftT("draftMinBtn", "Minimize 3D (local)")) + "</button></div>";
      if (d.sdf3DSource === "jsmol-min") out += "<div class='draftOracleRow'><button type='button' class='viewerFullBtn draftMinBtn' onclick='fMolDraftManualMinimize()'>" + fMolDraftEsc(fMolDraftT("draftMinMore", "Minimize +200 (local)").replace(/\+\d+/, "+" + MOLMIN_FURTHER_STEPS)) + "</button></div>";
      return out;
    }
    if (d && !d.sdfDone) {
      return "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT("draft3DFetching", "Fetching 3D… (PubChem → Cactus → local)")) + "</div>";
    }
    return "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT("submitNo3DAll", "No 3D model (PubChem/Cactus/local minimize) — 2D only.")) + "</div>"
      + "<div class='draftOracleRow'><button type='button' class='viewerFullBtn draftMinBtn' onclick='fMolDraftManualMinimize()'>" + fMolDraftEsc(fMolDraftT("draftMinBtn", "Minimize 3D (local)")) + "</button></div>";
  } catch (eS3) { return ""; }
}

function fMolDraftRenderPreview() {
  var d = window.MulerDraft;
  if (!d || !d.submitted) return;
  try {
    var na = document.getElementById("nameAnalysis");
    if (!na) return;
    var vGR = d.verdictGR || "unconfirmed", vEN = d.verdictEN || "unconfirmed";
    var clsGR = vGR === "correct" ? " draftV-correct" : (vGR === "wrong" ? " draftV-wrong" : "");
    var clsEN = vEN === "correct" ? " draftV-correct" : (vEN === "wrong" ? " draftV-wrong" : "");
    var html = "<div class='draftPreview'><div class='draftPreviewTitle'>" + fMolDraftEsc(fMolDraftT("draftPreviewTitle", "Πρόβλεψη Ονομασίας")) + "</div>" +
      "<div class='draftVRow'>" + fMolDraftVerdictCtrl("gr", vGR, false) + "<div class='draftEngine" + clsGR + "'>" + fMulerItalicSecTert(fMolDraftEsc((d.engineName_sys ? fMolDraftT("commonName", "Κοινή") + ": " : "") + d.engineName)) + "</div></div>";
    // Systematic Greek row (v54.31) when it differs — shares the GR verdict
    // state (manual-only, like EN). Common stays first.
    if (d.engineName_sys) html += "<div class='draftVRow'>" + fMolDraftVerdictCtrl("gr", vGR, false) + "<div class='draftEngine" + clsGR + "'>" + fMulerItalicSecTert(fMolDraftEsc(fMolDraftT("systematicName", "Συστηματική") + ": " + d.engineName_sys)) + "</div></div>";
    // EN prediction rows: school (Traditional) always; Systematic variant row
    // (v54.24) when it differs — e.g. 4,4-bis(chloromethyl)heptane vs school
    // 4,4-dichloromethylheptane. One shared EN verdict state per draft
    // (both copies repaint on set); Traditional stays first.
    if (d.engineEN) {
      var _scW = "Traditional", _syW = "Systematic";
      try {
        _scW = fMolDraftT("substTraditional", "Traditional");
        _syW = fMolDraftT("substSystematic", "Systematic");
      } catch (eSW) {}
      var _enLbl = d.engineEN_sys ? _scW + ": " : "";
      html += "<div class='draftVRow'>" + fMolDraftVerdictCtrl("en", vEN, !!d.enAutoValidated) + "<div class='draftEngineEN" + clsEN + "'>" + fMulerItalicSecTert(fMolDraftEsc(_enLbl + d.engineEN)) + "</div></div>";
      if (d.engineEN_sys) html += "<div class='draftVRow'>" + fMolDraftVerdictCtrl("en", vEN, !!d.enAutoValidated) + "<div class='draftEngineEN" + clsEN + "'>" + fMulerItalicSecTert(fMolDraftEsc(_syW + ": " + d.engineEN_sys)) + "</div></div>";
    }
    if (typeof d.pubchem === "undefined") {
      html += "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT("submitFetching", "Looking up PubChem…")) + "</div>";
    } else if (d.pubchem) {
      var hit = d.pubchem;
      var iupac = hit.iupacPubchem || hit.iupac || null;
      var title = hit.title || hit.titlePubchem || null;
      var sys = hit.systematic || hit.iupacEN || null;
      var norm = fMolDraftNorm;
      if (iupac) {
        // Read-only agreement glyph (same shared match as the auto-check;
        // non-interactive, unlike the Correct/Wrong verdict controls).
        var _pcG = "?", _pcT = "";
        try {
          var _pcM = (typeof fMolDraftPCMatch === "function") ? (fMolDraftPCMatch(d.engineEN, hit) || (d.engineEN_sys && fMolDraftPCMatch(d.engineEN_sys, hit))) : false;
          if (_pcM) { _pcG = "✓"; _pcT = fMolDraftT("draftPCMatchTip", "PubChem agrees with the predicted name"); }
          else { _pcG = "✕"; _pcT = fMolDraftT("draftPCMismatchTip", "Predicted name differs from PubChem — pending human review"); }
        } catch (ePCM) {}
        html += "<div class='draftOracleRow'><span class='draftOCMark' title='" + fMolDraftEsc(_pcT) + "'>" + _pcG + "</span> " + fMolDraftEsc(fMolDraftT("draftIUPACRow", "IUPAC (PubChem)")) + ": " + fMolDraftEsc(iupac) + "</div>";
      }
      if (title && /ether$/i.test(String(title).trim()) && norm(title) !== norm(iupac)) html += "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT("draftCommonRow", "Common (PubChem)")) + ": " + fMolDraftEsc(title) + "</div>";
      if (sys && norm(sys) !== norm(iupac) && norm(sys) !== norm(title)) html += "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT("draftSysRow", "Systematic")) + ": " + fMolDraftEsc(sys) + "</div>";
      // OpenClatura second oracle (rule-built EN): verbatim name + OPSIN
      // round-trip status. Display only — never feeds verdicts (Phase 2).
      // Speaks loudest on no-PubChem-record drafts (amber rows).
      try {
        var _ocD = (typeof d.openclatura !== "undefined") ? d.openclatura : undefined;
        if (_ocD && _ocD.name) {
          // Second-oracle verdict glyph (read-only): shared comparator against
          // the predicted EN. Never touches verdictEN/nameCheck (Phase 2 rule).
          var _ocG = "?", _ocT = "";
          try {
            var _ocV = (typeof fMatchENvsOC === "function") ? fMatchENvsOC(d.engineEN, _ocD.name) : "missing";
            // Systematic variant may match where school does not (v54.24).
            try {
              if (_ocV !== "match" && d.engineEN_sys && typeof fMatchENvsOC === "function" &&
                fMatchENvsOC(d.engineEN_sys, _ocD.name) === "match") _ocV = "match";
            } catch (eOCV2) {}
            if (_ocV === "match") { _ocG = "✓"; _ocT = fMolDraftT("ocMatchTip", "OpenClatura agrees with the engine name"); }
            else if (_ocV === "mismatch") { _ocG = "✕"; _ocT = fMolDraftT("ocMismatchTip", "Engine name differs from OpenClatura — pending human review"); }
            else { _ocG = "?"; _ocT = fMolDraftT("ocMissingTip", "No OpenClatura answer"); }
          } catch (eOCV) {}
          html += "<div class='draftOracleRow'><span class='draftOCMark' title='" + fMolDraftEsc(_ocT) + "'>" + _ocG + "</span> " + fMolDraftEsc(fMolDraftT("draftOpenclatura", "IUPAC (OpenClatura)")) + ": " + fMolDraftEsc(_ocD.name) + ((_ocD.opsin && _ocD.opsin !== "matched") ? fMolDraftEsc(" (OPSIN: " + _ocD.opsin + ")") : "") + "</div>";
        } else if (_ocD === undefined && d.submitted) {
          html += "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT("draftOCFetching", "Looking up OpenClatura…")) + "</div>";
        } else if (d.openclaturaErr) {
          html += "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT("draftOCError", "OpenClatura lookup failed (network) — not validated")) + "</div>";
        }
      } catch (eOCD) {}
      if (!iupac && !title) html += "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT("submitNoRecord", "No PubChem record — engine only.")) + "</div>";
      try { if (typeof fMolDraftSDF3DStatusHTML === "function") html += fMolDraftSDF3DStatusHTML(d) || ""; } catch (eS3) {}
    } else {
      html += "<div class='draftOracleRow'>" + fMolDraftEsc(fMolDraftT("submitNoRecord", "No PubChem record — engine only.")) + "</div>";
      try { if (typeof fMolDraftSDF3DStatusHTML === "function") html += fMolDraftSDF3DStatusHTML(d) || ""; } catch (eS32) {}
    }
    html += "</div>";
    na.innerHTML = html;
  } catch (eR) {}
}

// Inline SDF loader (v54 fix): JSmol's `load <url>` file loader rejects
// `blob:` URLs ("invalid url") when j2sPath/serverURL point at the remote
// CDN — a blob lives only in page memory and is not fetchable by the php
// proxy. Passing the SDF text via `load data ... end` avoids any URL fetch
// and works on file:// and https:// alike. Returns true when issued.
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
function fMolDraftMovedEnough(beforeMol, afterSDF) {
  try {
    if (typeof fMolDraftMeanDisplacement !== "function") return false;
    var mean = fMolDraftMeanDisplacement(beforeMol, afterSDF);
    try { /* console.log("[SDF-3D] tier local-min: mean heavy displacement = " + (mean >= 0 ? mean.toFixed(3) : "?") + " A"); */ } catch (eL) {}
    return mean >= 0.05;
  } catch (e) { return false; }
}

// Pure-JS 2D untangle (v55.9): spreads non-bonded heavy overlaps that send
// MMFF energy to the astronomical (E=46000+ → line-search collapse, zero
// movement). Symmetric push-apart along the pair axis, bonded pairs exempt,
// capped sweeps. Same fixed-column surgery + self-verify discipline as the
// jiggle below; falls back to the input on any gap.
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
        try { /* console.log("[SDF-3D] tier local-min: untangle failed self-verify — using input"); */ } catch (eLgV) {}
        return molText;
      }
    } catch (eV) { return molText; }
    try { /* console.log("[SDF-3D] tier local-min: 2D untangle fixed " + fixed + " overlaps (minSep " + MS + ")"); */ } catch (eL) {}
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
        try { /* console.log("[SDF-3D] tier local-min: jiggle failed self-verify — using un-jiggled input"); */ } catch (eLgV) {}
        return molText;
      }
    } catch (eV) { return molText; }
    try { /* console.log("[SDF-3D] tier local-min: z-jiggle ±" + A + " A on " + nA + " atoms"); */ } catch (eL) {}
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
// JSmol's MOL writer can assign parity to ordinary CH2 carbons. Those
// centers cannot carry tetrahedral stereochemistry. Normalize only this
// demonstrated writer output, never imported/source SDF or potential C*.
function fMolDraftNormalizeJSmolReadback(text, referenceMol) {
  try {
    var reference = fParseMolV2000(referenceMol), m = fParseMolV2000(text);
    if (!fMolCanTransform2D(reference, true) || !m) return null;
    var neighbors = m.atoms.map(function () { return []; });
    m.bonds.forEach(function (b) {
      neighbors[b[0] - 1].push([b[1] - 1, b[2]]);
      neighbors[b[1] - 1].push([b[0] - 1, b[2]]);
    });
    var lines = String(text).split('\n'), changed = false;
    m.atoms.forEach(function (a, i) {
      if ((a.parity !== 1 && a.parity !== 2) || a.el !== 'C' || a.charge || a.radical ||
          neighbors[i].length !== 4 || neighbors[i].some(function (v) { return v[1] !== 1; })) return;
      var ordinaryH = neighbors[i].filter(function (v) {
        var h = m.atoms[v[0]];
        return h.el === 'H' && !h.massDifference && !h.isotope && !h.charge && !h.radical &&
          !h.parity && neighbors[v[0]].length === 1;
      });
      if (ordinaryH.length < 2) return;
      lines[i + 4] = lines[i + 4].substring(0, 39) + '  0' + lines[i + 4].substring(42);
      changed = true;
    });
    // Every other field survives byte-for-byte. The caller still applies
    // the unchanged strict graph/charge/isotope/query/stereo/H checks.
    return changed ? lines.join('\n') : text;
  } catch (e) { return null; }
}
function fMolDraftReadBackSDF(expectHeavy, job) {
  if (!fMolDraft3DCurrent(job)) return null;
  var text = null;
  try { text = fJSmolScriptEcho(job.applet, 'write MOL') || null; } catch (e) {}
  text = fMolDraftNormalizeJSmolReadback(text, job.molText);
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
  d.sdf3DStatus = source === 'pubchem' || source === 'pubchem-jsmol' || source === 'pubchem-fetch' || source === 'remote' ? 'source-provided' : 'provisional';
  d.sdf3DProvenance = fMolDraft3DProvenance(source, confirmation);
  d._provisionalConfirmedSDF = confirmation ? sdf : null;
  return true;
}
// Cancel/STOP is tied to the exact still-owned model and running round.
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
// Every applet provider uses the same serialized draft-owned model writer
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
    if (!/^\d+$/.test(q)) return null;
    cmd = 'load ":cid:' + q + '"';
  } else {
    // Chemical input cannot terminate a Jmol script string.
    if (/[\r\n";]/.test(q)) return null;
    cmd = 'load ":smiles:' + q.replace(/\\/g, '\\\\') + '"';
  }
  return fMolDraftJSmolLoadAndReadBack(cmd, expectHeavy, job);
}
function fMolDraftRemote3DFromJSmol(smiles, expectHeavy, job) {
  if (!smiles || !fMolDraft3DCurrent(job) || /[\r\n";]/.test(smiles)) return null;
  var quoted = String(smiles).replace(/\\/g, '\\\\');
  return fMolDraftJSmolLoadAndReadBack('load "$' + quoted + '"', expectHeavy, job);
}
async function fMolDraftFetchSDF3DTiered(smiles, molText, expectHeavy, isCurrent, opts) {
  var job = fMolDraft3DBegin(isCurrent);
  var empty = { sdf:null, source:null };
  if (!job) return empty;
  var offline = typeof navigator !== 'undefined' && navigator.onLine === false;
  var o = opts || {}, cid = o.cid == null ? null : String(o.cid).trim();
  if (cid && !/^\d+$/.test(cid)) cid = null;
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

function fMolDraftShow3D(sdf) {
  try {
    var b3 = document.getElementById("view3DBtn");
    if (b3 && !b3.classList.contains("active") && typeof fToggleViewer3D === "function") {
      fToggleViewer3D();
      if (window.MulerDraft) window.MulerDraft.preview3D = true;
    }
  } catch (eV) {}
  if (!sdf) return;
  // Inline DATA load — never a blob: URL (see helper note above). When JSmol
  // is not live the wrapper returns false: keep the 2D-only note and surface
  // the standard pending-3D path instead of recording an invisible 3D model.
  var _issued = false;
  try {
    if (typeof fJSmolLoadInlineSDF === "function") {
      _issued = !!fJSmolLoadInlineSDF(jmolAppletNomeclature, sdf, "script spt/init-57.spt;");
    }
  } catch (eJ) { _issued = false; }
  if (!_issued) {
    try { if (typeof fMulerNotePending3D === "function") fMulerNotePending3D(); } catch (eP3b) {}
    try { fMolDraftToast(fMolDraftT("submitNo3DAll", "No 3D model (PubChem/Cactus/local minimize) — 2D only.")); } catch (eT3) {}
    return;
  }
  try { if (typeof fSetMolVis3D === "function") fSetMolVis3D(); } catch (eV) {}
  try { if (typeof fParseSDF3D === "function") fParseSDF3D(sdf); } catch (eP1) {}
  try { if (typeof fDetectMolType3D === "function") fDetectMolType3D(); } catch (eP2) {}
  try { if (typeof fCalcMainChain3D === "function") fCalcMainChain3D(); } catch (eP3) {}
  try { if (typeof showAtomSymbols3D === "function") showAtomSymbols3D(); } catch (eA2) {}
  try { if (typeof showHydrogens3D === "function") showHydrogens3D(); } catch (eH2) {}
  try { if (typeof rotate3D === "function") rotate3D(); } catch (eR2) {}
  try { if (typeof fResizeViewers === "function") fResizeViewers(); } catch (eR3) {}
}

function fMolDraftRestoreChainMode(forcedMode) {
  var m = (typeof forcedMode !== "undefined") ? forcedMode : null;
  try {
    if (m == null && window.MulerDraft) m = window.MulerDraft.savedChainMode;
  } catch (eR) {}
  try {
    if (m != null) mainChainMode = m;
  } catch (eM) {}
  try { if (typeof fUpdateChainModeButton === "function") fUpdateChainModeButton(); } catch (eB) {}
}

// Shared sandbox engine pass (Submit + Beautify): syncs the given MOL text
// onto the display applet, forces algorithmic mode, and runs the FULL naming
// tail including fGuessName — the chain rebuild lives there. A bare
// analyse+detect leaves the previous molecule's chain behind (that was the
// pre-submit beautify damage). Returns { ok, ring }. Restores nothing:
// Submit keeps algorithmic through its preview (teardown restores via
// savedChainMode); Beautify restores immediately via its own saved mode.
function fMolDraftSandboxAnalyse(molText) {
  // Display source belongs to this drawing, never the selected template.
  myMol2D = molText;
  skeletalLayoutApplied = null;
  skeletalLayoutSource = mode2D === 'skeletal' && molText
    ? {key: selectedMol, mol: molText, draft: window.MulerDraft || null} : null;
  try {
    if (molText && typeof jsmeNomeclatureApplet !== "undefined" && jsmeNomeclatureApplet &&
        typeof jsmeNomeclatureApplet.readMolFile === "function") {
      // Annotated sync (same as fLoadMol2D): [C] carbons render visible C
      // labels so the preview SVG carries carbon labels + H counts. JSME
      // normalizes [C] to label "C" internally (the 141 annotated stored
      // molecules analyse correctly), so the engine below is unaffected;
      // atom order/count are untouched, only the symbol field changes.
      var _syncMol = molText;
      try { if (typeof fMakeAnnotatedSkeletal === "function") _syncMol = fMakeAnnotatedSkeletal(molText) || molText; } catch (eAn2) { _syncMol = molText; }
      jsmeNomeclatureApplet.readMolFile(_syncMol);
      try {
        if (typeof fApplyMol2DScale === "function") fApplyMol2DScale();
        else if (typeof molZoom2D !== "undefined") jsmeNomeclatureApplet.setMolecularAreaScale(molZoom2D);
      } catch (eZ) {}
    }
  } catch (eSync) {}
  try { mainChainMode = "algorithmic"; } catch (eM1) {}
  try { if (typeof fUpdateChainModeButton === "function") fUpdateChainModeButton(); } catch (eBc) {}
  try {
    if (typeof fAnalyseStructure === "function") fAnalyseStructure();
    if (typeof fDetectMolType === "function") fDetectMolType();
  } catch (eAn) { return { ok: false, ring: false }; }
  try {
    if (typeof fMolDraftHasRing === "function" && fMolDraftHasRing()) return { ok: false, ring: true };
  } catch (eR) {}
  try {
    if (typeof fGuessName === "function") fGuessName();
  } catch (eGn) { return { ok: false, ring: false }; }
  return { ok: true, ring: false };
}

async function fMolDraftSubmit() {
  if (!window.MulerDraft || fMolDraftPresenting()) return;
  if (window.MulerDraft.submitting || window.MulerDraftAcquisition) return;
  fMolDraft3DInvalidate();
  var submittingDraft = window.MulerDraft;
  // 1. read + validate (empty drawing -> toast, no state change).
  var drawing = fMolDraftReadDrawing();
  if (!drawing.hasAny) {
    fMolDraftToast(fMolDraftT("submitEmpty", "Empty drawing — draw something first."));
    return;
  }
  // Auto-linearize (Ρυθμίσεις, default on): tidy school drawings to the
  // canonical linear layout BEFORE the naming run, so preview + stored MOLs
  // always come from tidied geometry. Skeletal drafts pass through untouched
  // (zigzag path owns that slot). Edit mode skips it entirely: the template
  // is already canonical and the author's deltas must survive Submit→Accept
  // verbatim into their slot (single-slot update contract); manual Linearize
  // stays available as an explicit action. Submit then proceeds unchanged.
  var _auto = true;
  try { _auto = (typeof fMolDraftAutoLinearizeOn === "function") ? fMolDraftAutoLinearizeOn() : true; } catch (eA) { _auto = true; }
  try { if (window.MulerDraft && window.MulerDraft.mode === "edit") _auto = false; } catch (eM) {}
  if (_auto) {
    var _td = null;
    try { _td = fMolDraftAutoTidy(); } catch (eT) { _td = null; }
    if (!_td) return;
    drawing.molText = _td.molText;
    drawing.smiles = _td.smiles;
  }
  window.MulerDraft.submitting = true;
  window.MulerDraft._submitId = (window.MulerDraft._submitId || 0) + 1;
  var _mySid = window.MulerDraft._submitId;
  var _myEpoch = window.MulerDraft._epoch;
  try {
    var st = document.getElementById("molDraftStatus");
    if (st) st.textContent = fMolDraftT("submitRunning", "Submitting…");
  } catch (eSt) {}
  try { fMolDraftSyncBar(); } catch (eSy0) {}
  // 0+2. shared sandbox engine pass (Submit + Beautify): syncs the drawing
  // onto the display applet (the engine/overlay pipeline reads the main
  // depict applet, which the user never touches mid-draft — the main applet
  // never leaves depict mode, so highlights just work) and runs the full
  // naming tail. Algorithmic-or-nothing: stored chains belong to the old
  // atom order and are never valid here.
  var _draftMol = "";
  try {
    if (typeof jsmeEditDraftApplet !== "undefined" && jsmeEditDraftApplet &&
        typeof jsmeEditDraftApplet.molFile === "function") _draftMol = jsmeEditDraftApplet.molFile() || "";
  } catch (eSync) {}
  var savedMode = null;
  try { savedMode = (typeof mainChainMode !== "undefined") ? mainChainMode : null; } catch (eM0) {}
  window.MulerDraft.savedChainMode = savedMode;
  var _sb = { ok: false, ring: false };
  try { _sb = fMolDraftSandboxAnalyse(_draftMol) || _sb; } catch (eSb) {}
  if (!_sb.ok) {
    fMolDraftRestoreChainMode();
    window.MulerDraft.submitting = false;
    fMolDraftToast(fMolDraftT(_sb.ring ? "submitRing" : "submitEngineFail", _sb.ring ? "Rings are out of scope — acyclic structures only." : "Engine failed — check the drawing."));
    return;
  }
  var engineName = "";
  try { engineName = (typeof currentMolName !== "undefined") ? String(currentMolName || "") : ""; } catch (eN) {}
  if (!engineName) {
    fMolDraftRestoreChainMode();
    window.MulerDraft.submitting = false;
    fMolDraftToast(fMolDraftT("submitEngineFail", "Engine failed — check the drawing."));
    return;
  }
  try {
    if (typeof fUpdateSVG === "function") fUpdateSVG();
  } catch (eSvg) {}
  // Engine done: flip to the depict (SVG) view — the molecule stays editable
  // via the Draw button, which flips back without touching draft state.
  try { fMolDraftShowPreviewView(); } catch (eV) {}
  window.MulerDraft.smiles = drawing.smiles;
  window.MulerDraft.molText = drawing.molText;
  window.MulerDraft.engineName = engineName;
  // Predicted English name (v53 engine, draft-safe): transliterate the
  // sandbox Greek slots with a nonexistent key, so the store-back guard
  // inside fPopulateEngineENFromGreek skips writing into any real entry
  // (selectedMol is the untouched template). Oracle fallback for the
  // non-transliterable case lands below, once the PubChem hit resolves.
  var _en = null;
  try { if (typeof fPopulateEngineENFromGreek === "function") _en = fPopulateEngineENFromGreek("__draft__"); } catch (eEN) { _en = null; }
  window.MulerDraft.engineEN = (typeof _en === "string" && _en) ? _en : null;
  window.MulerDraft.engineDelegated = false;
  // Systematic variant (v54.24): same-slot transform with the "sys" maps
  // (bis/tris upgrade for decorated branches). Shown as a second EN row and
  // included in oracle matching when it differs from school. Same "__draft__"
  // store-back guard applies (return value only, nothing persisted).
  var _enSys = null;
  try { if (typeof fPopulateEngineENFromGreek === "function") _enSys = fPopulateEngineENFromGreek("__draft__", "sys"); } catch (eENS) { _enSys = null; }
  window.MulerDraft.engineEN_sys = (typeof _enSys === "string" && _enSys && _enSys !== window.MulerDraft.engineEN) ? _enSys : null;
  // Systematic Greek variant (v54.31): same render-time slot transform as the
  // panel toggle, joined with the euphony mirror. No oracle role (GR is
  // manual-only); shown as a second GR row when it differs from common.
  var _grSys = null;
  try {
    if (typeof fGreekSysSlots === "function" && typeof fJoinGreekSysName === "function") {
      var _gs = fGreekSysSlots();
      if (_gs) {
        var _gj = fJoinGreekSysName(_gs);
        if (typeof _gj === "string" && _gj && _gj !== engineName) _grSys = _gj;
      }
    }
  } catch (eGRS) { _grSys = null; }
  window.MulerDraft.engineName_sys = _grSys;
  // Name verdicts (tri-state per language): every Submit resets — new
  // drawing, new prediction, old verdict void. EN auto-check re-applies
  // below once the oracle lands (untouched only); GR is manual-only.
  window.MulerDraft.verdictGR = "unconfirmed";
  window.MulerDraft.verdictEN = "unconfirmed";
  window.MulerDraft.touchedGR = false;
  window.MulerDraft.touchedEN = false;
  window.MulerDraft.enAutoValidated = false;
  try { window.MulerDraft.enAutoSource = null; } catch (eAS) {}
  window.MulerDraft.submitted = true;
  window.MulerDraft.stale = false;
  try { window.MulerDraft._strayConfirmed = false; } catch (eSC) {}
  window.MulerDraft.pubchem = undefined;
  window.MulerDraft.sdf3D = null;
  window.MulerDraft.sdf3DSource = null;
  window.MulerDraft.sdf3DStatus = null;
  window.MulerDraft.sdf3DProvenance = null;
  window.MulerDraft._provisionalConfirmedSDF = null;
  window.MulerDraft.sdfDone = false;
  try { window.MulerDraft._minPrepared = false; } catch (eMp0) {}
  window.MulerDraft.openclatura = undefined;
  window.MulerDraft.openclaturaErr = false;
  fMolDraftRenderPreview();
  try {
    var st2 = document.getElementById("molDraftStatus");
    if (st2) {
      var _idHint = "";
      try {
        var _dh = window.MulerDraft;
        if (_dh && _dh.mode === "edit" && typeof fMolDraftIsSameMolecule === "function") {
          _idHint = fMolDraftIsSameMolecule()
            ? fMolDraftT("draftSameHint", "same molecule, will update this view")
            : fMolDraftT("draftForkHint", "different molecule, will fork as new");
        }
      } catch (eIh) { _idHint = ""; }
      st2.textContent = fMolDraftT("draftPreview", "Preview") + ": " + engineName + (_idHint ? " — " + _idHint : "");
    }
  } catch (eSt2) {}
  // 3. PubChem oracle (async, molecule-guarded like the info panel refresh).
  var submittingSmiles = drawing.smiles;
  if (!submittingSmiles) {
    window.MulerDraft.submitting = false;
    try { fMolDraftSyncBar(); } catch (eSy1) {}
    return;
  }
  var hit = null;
  try {
    if (typeof fFetchIUPAC_EN === "function") hit = await fFetchIUPAC_EN(submittingSmiles);
  } catch (eP) { hit = null; }
  if (window.MulerDraft !== submittingDraft || window.MulerDraft._submitId !== _mySid || window.MulerDraft._epoch !== _myEpoch || window.MulerDraft.smiles !== submittingSmiles) return; // superseded/cancelled/Draw-mid-fetch
  window.MulerDraft.pubchem = hit || null;
  // Oracle fallback for the non-transliterable case (Greek-common
  // esters/complex ethers): same systematicEN the stored path delegates to.
  try {
    var _dd = window.MulerDraft;
    if (_dd && (!_dd.engineEN || /[Α-ω]/.test(_dd.engineEN))) {
      var _sys = (hit && (hit.systematic || hit.iupacEN)) || null;
      if (_sys) { _dd.engineEN = _sys; _dd.engineDelegated = true; }
    }
    // EN auto-validation (untouched only — a human verdict always wins):
    // PubChem 3-way oracle match (shared helper, also feeds the row glyph).
    // School OR systematic variant may match (v54.24 — e.g. PubChem
    // 4,4-bis(chloromethyl)heptane vs school 4,4-dichloromethylheptane);
    // source recorded for the eval-data header. A match auto-checks the EN
    // box as correct.
    if (_dd && _dd.engineEN && !_dd.touchedEN && typeof fMolDraftPCMatch === "function") {
      if (fMolDraftPCMatch(_dd.engineEN, hit)) {
        _dd.verdictEN = "correct";
        _dd.enAutoValidated = true;
        _dd.enAutoSource = "pubchem";
      } else if (_dd.engineEN_sys && fMolDraftPCMatch(_dd.engineEN_sys, hit)) {
        _dd.verdictEN = "correct";
        _dd.enAutoValidated = true;
        _dd.enAutoSource = "pubchem-sys";
      }
    }
  } catch (eED) {}
  try { if (typeof fMolDraftRefreshAcceptKey === "function") fMolDraftRefreshAcceptKey(); } catch (eK1) {}
  fMolDraftRenderPreview();
  // 3b. OpenClatura second oracle (non-blocking): canonical SMILES first
  // (best input, already in the hit — no extra request), drawing SMILES
  // fallback. Molecule-guarded; repaints the preview on resolve. Fail-soft:
  // a null just hides the OC row (console warned).
  try {
    if (typeof fFetchIUPAC_OC === "function") {
      var _ocSmi = (hit && hit.canonicalSmiles) || submittingSmiles;
      fFetchIUPAC_OC(_ocSmi).then(function (oc) {
        try {
          if (window.MulerDraft !== submittingDraft || window.MulerDraft._submitId !== _mySid || window.MulerDraft._epoch !== _myEpoch || window.MulerDraft.smiles !== submittingSmiles) return;
          window.MulerDraft.openclatura = oc && oc.name ? { name: oc.name, opsin: oc.opsin || null } : null;
          try { window.MulerDraft.openclaturaErr = false; } catch (eOCe) {}
          // Second-oracle auto-check (OR with PubChem; untouched-only; human
          // always wins): an OC match also marks the EN prediction correct,
          // source-recorded for the eval-data header. Never un-marks.
          try {
            var _dd2 = window.MulerDraft;
            var _ocM1 = false, _ocM2 = false;
            try {
              if (typeof fMatchENvsOC === "function" && oc && oc.name) {
                _ocM1 = (fMatchENvsOC(_dd2.engineEN, oc.name) === "match");
                _ocM2 = !!(_dd2.engineEN_sys && fMatchENvsOC(_dd2.engineEN_sys, oc.name) === "match");
              }
            } catch (eOCm) { _ocM1 = false; _ocM2 = false; }
            if (_dd2 && _dd2.engineEN && !_dd2.touchedEN && _dd2.verdictEN !== "correct" && (_ocM1 || _ocM2)) {
              _dd2.verdictEN = "correct";
              _dd2.enAutoValidated = true;
              _dd2.enAutoSource = (!_ocM1 && _ocM2) ? "openclatura-sys" : "openclatura";
            }
          } catch (eOCa) {}
          try {
            var _op = (oc && oc.name) || "", _oe = window.MulerDraft.engineEN || "";
            var _ov = (typeof fMatchENvsOC === "function") ? fMatchENvsOC(_oe, _op) : "missing";
            // console.log("[EN-CHECK-OC] draft: predicted=\"" + _oe + "\" openclatura=\"" + _op + "\" verdict=" + _ov);
          } catch (eOCl) {}
          fMolDraftRenderPreview();
        } catch (eOCr) {}
      }).catch(function (eOC) {
        try {
          if (window.MulerDraft !== submittingDraft || window.MulerDraft._submitId !== _mySid || window.MulerDraft._epoch !== _myEpoch || window.MulerDraft.smiles !== submittingSmiles) return;
          window.MulerDraft.openclatura = null;
          try { window.MulerDraft.openclaturaErr = true; } catch (eOCe2) {}
          try { /* console.warn("[OC] draft fetch failed", eOC); */ } catch (eL) {}
          fMolDraftRenderPreview();
        } catch (eOCr2) {}
      });
    }
  } catch (eOCf) {}
  // 4. 3D tiered (v55): JSmol `:cid:`/`:smiles:` (PubChem) -> page PUG fetch
  // (PubChem fallback) -> JSmol `$SMILES` (NCI Cactus) -> local 2D-MOL + UFF
  // minimize (offline). Any tier success shows 3D and unblocks Accept with
  // provenance in d.sdf3DSource; only all-miss keeps the 2D-only note.
  var _tier = { sdf: null, source: null };
  try {
    var _expH = 0;
    try {
      if (typeof fParseMolV2000 === "function" && drawing.molText) {
        var _pe2 = fParseMolV2000(drawing.molText);
        if (_pe2 && _pe2.atoms) for (var _hi = 0; _hi < _pe2.atoms.length; _hi++) {
          var _he = String(_pe2.atoms[_hi].el || "");
          if (_he && _he !== "H" && _he !== "h") _expH++;
        }
      }
    } catch (eEH) { _expH = 0; }
    var _molT = drawing.molText;
    try { window.MulerDraft.expectHeavy = _expH; } catch (eXH) {}
    var _isCur = function () {
      try {
        return !(window.MulerDraft !== submittingDraft || window.MulerDraft._submitId !== _mySid ||
          window.MulerDraft._epoch !== _myEpoch || window.MulerDraft.smiles !== submittingSmiles);
      } catch (eIC) { return false; }
    };
    if (typeof fMolDraftFetchSDF3DTiered === "function") {
      var _cid = null, _canon = null;
      try { _cid = (hit && hit.cid != null) ? String(hit.cid) : null; } catch (eCc) { _cid = null; }
      try { _canon = (hit && hit.canonicalSmiles) ? String(hit.canonicalSmiles) : null; } catch (eCn) { _canon = null; }
      _tier = await fMolDraftFetchSDF3DTiered(submittingSmiles, _molT, _expH, _isCur, { cid: _cid, canonicalSmiles: _canon }) || _tier;
    } else if (typeof fFetchSDF3D_PubChem === "function") {
      var _s0 = null;
      try { _s0 = await fFetchSDF3D_PubChem(submittingSmiles); } catch (eS) { _s0 = null; }
      if (fMolDraftValidSDF3D(_s0, _expH, _molT)) _tier = { sdf: _s0, source: "pubchem" };
    }
  } catch (eS) { _tier = { sdf: null, source: null }; }
  if (window.MulerDraft !== submittingDraft || window.MulerDraft._submitId !== _mySid || window.MulerDraft._epoch !== _myEpoch || window.MulerDraft.smiles !== submittingSmiles) return;
  try {
    var restoredStatus = document.getElementById("molDraftStatus");
    if (restoredStatus) restoredStatus.textContent = fMolDraftT("draftPreview", "Preview") + ": " + engineName;
  } catch (eStatus) {}
  window.MulerDraft.submitting = false;
  window.MulerDraft.sdfDone = true;
  if (_tier && _tier.sdf) {
    if (fMolDraftSet3D(window.MulerDraft, _tier.sdf, _tier.source || null, null)) fMolDraftShow3D(_tier.sdf);
  } else {
    window.MulerDraft.sdf3D = null;
    window.MulerDraft.sdf3DSource = null;
    // v55.8: load the flat drawing into the 3D viewer anyway (honest starting
    // point) — the manual Minimize button beside the 2D-only note takes it
    // from here, and Accept stays locked until valid 3D exists.
    try { if (typeof fMolDraftShowFlat3D === "function") fMolDraftShowFlat3D(); } catch (eF3) {}
  }
  try { if (typeof fMolDraftRefreshAcceptKey === "function") fMolDraftRefreshAcceptKey(); } catch (eK2) {}
  fMolDraftRenderPreview();
  try { fMolDraftSyncBar(); } catch (eSy2) {}
}
// Show-flat fallback (v55.8): when every 3D tier misses, display the flat
// drawing in the 3D viewer anyway (honest starting point) with the manual
// Minimize button beside the 2D-only note. No 3D analysis runs on flat data
// (it would pollute the 3D naming globals); Accept stays locked (sdf3D null).
// Teardown already re-hides the viewer via the preview3D snapshot.
function fMolDraftShowFlat3D() {
  try {
    var d = null;
    try { d = window.MulerDraft; } catch (eD) { return; }
    if (!d || !d.molText) return;
    if (typeof jmolAppletNomeclature === "undefined" || !jmolAppletNomeclature) return;
    if (typeof fJSmolLive === "function" && !fJSmolLive()) return;
    try {
      if (typeof fJSmolScriptWait === "function") { if (fJSmolScriptWait(jmolAppletNomeclature, "zap;") === null) return; }
    } catch (eZ) {}
    var ok = false;
    try { if (typeof fJSmolLoadInlineSDF === "function") ok = !!fJSmolLoadInlineSDF(jmolAppletNomeclature, d.molText, "script spt/init-57.spt;"); } catch (eL) { ok = false; }
    if (!ok) return;
    try {
      var b3 = document.getElementById("view3DBtn");
      if (b3 && !b3.classList.contains("active") && typeof fToggleViewer3D === "function") {
        fToggleViewer3D();
        try { window.MulerDraft.preview3D = true; } catch (eP) {}
      }
    } catch (eV) {}
    try { if (typeof fSetMolVis3D === "function") fSetMolVis3D(); } catch (eVs) {}
    try { if (typeof rotate3D === "function") rotate3D(); } catch (eR) {}
    try { if (typeof fResizeViewers === "function") fResizeViewers(); } catch (eRz) {}
    try { /* console.log("[SDF-3D] flat drawing shown in 3D viewer — manual minimize available"); */ } catch (eLg) {}
  } catch (eF) {}
}

// Shared visual teardown (Cancel + Accept): hides the draft chrome and
// restores display mode. Returns the snapshot callers need (3D visibility,
// chain mode). Does NOT reselect — callers own that.
function fMolDraftTeardownDisplay() {
  fMolDraft3DInvalidate();
  var snap = { back3D: false, preview3D: false, savedMode: null };
  try {
    if (window.MulerDraft) {
      snap.back3D = !!window.MulerDraft.had3D;
      snap.preview3D = !!window.MulerDraft.preview3D;
      try { snap.savedMode = window.MulerDraft.savedChainMode; } catch (eSm) {}
    }
  } catch (eG) {}
  window.MulerDraft = null;
  fMolDraftHideBar();
  try {
    var _pc = document.getElementById("pageContainer");
    if (_pc) _pc.classList.remove("drafting");
  } catch (eP) {}
  try {
    var _e1 = document.getElementById("editMolBtn");
    if (_e1) { _e1.classList.remove("active"); _e1.classList.remove("btnInactive"); }
    var _e2 = document.getElementById("newMolBtn");
    if (_e2) { _e2.classList.remove("active"); _e2.classList.remove("btnInactive"); }
  } catch (eA2) {}
  // Back to display mode first (applets hidden, SVG + radios shown).
  try { $("#jsmeNomeclature").addClass("hide"); } catch (eA) {}
  try { $("#jsmeEditDraft").addClass("hide"); } catch (eED) {}
  try { $("#jsmeNomeclatureSVG").removeClass("hide"); } catch (eS) {}
  try { $("#radio2DMode").removeClass("hide"); } catch (eR) {}
  try {
    if (snap.back3D && typeof fToggleViewer3D === "function") {
      var b3 = document.getElementById("view3DBtn");
      if (b3 && !b3.classList.contains("active")) fToggleViewer3D();
    } else if (!snap.back3D && snap.preview3D && typeof fToggleViewer3D === "function") {
      // Preview showed 3D for PubChem SDF although it was hidden pre-draft.
      var b3h = document.getElementById("view3DBtn");
      if (b3h && b3h.classList.contains("active")) fToggleViewer3D();
    }
  } catch (e3) {}
  // Chain mode back to the author's setting (submit forced algorithmic);
  // the caller's fSelectMol re-syncs the radio UI from it.
  fMolDraftRestoreChainMode(snap.savedMode);
  setTimeout(function () { try { if (typeof fResizeViewers === "function") fResizeViewers(); } catch (eR2) {} }, 0);
  return snap;
}

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

function fMolDraftSlugBase(src) {
  var raw = "";
  try {
    raw = (src && (src.systematicEN || src.systematic || src.iupacEN || src.titlePubchem || src.title)) || "";
  } catch (eR) { raw = ""; }
  var s = String(raw || "").toLowerCase();
  try {
    s = s.replace(/[α-ω]/g, function (ch) { return MOLDRAFT_GR2EN[ch] || ""; });
  } catch (eG) {}
  s = s.replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").replace(/_+/g, "_");
  if (s.length > 48) s = s.slice(0, 48).replace(/_+$/g, "");
  return s || "";
}

// ASCII-safe key (no transliteration needed beyond the Greek map above);
// collision loop keeps it unique against stored + custom keys.
function fMolDraftMakeKey(normSmi, nameSrc) {
  var stem = "";
  try { stem = fMolDraftSlugBase(nameSrc); } catch (eS) { stem = ""; }
  if (!stem) {
    var h = 5381;
    var s = String(normSmi || "");
    for (var i = 0; i < s.length; i++) h = (((h << 5) + h) + s.charCodeAt(i)) >>> 0;
    return "custom_" + ("00000" + h.toString(16)).slice(-6);
  }
  var key = "custom_" + stem, n = 2;
  try {
    while (typeof nameExamples !== "undefined" && nameExamples[key]) key = "custom_" + stem + "_" + (n++);
  } catch (eC) {}
  return key;
}

function fMolDraftFileSlug(rec) {
  // Filename mirrors the key: MULERMOC_<stem>_data.js. Key always starts
  // with "custom_"; legacy hash keys yield MULERMOC_a3f9c2_data.js the same way.
  var stem = "";
  try {
    if (rec && rec.key && String(rec.key).indexOf("custom_") === 0) stem = String(rec.key).slice(7);
    else stem = fMolDraftSlugBase(rec);
  } catch (eR) { stem = ""; }
  if (!stem) stem = "custom";
  return "MULERMOC_" + stem + "_data.js";
}

// Session-new custom provenance (v54.25, save-all scope): keys Accept wrote
// this session (forks + in-place slot updates). Boot-loaded file customs live
// in the same registry but stay unmarked, so save-all skips files that
// already exist on disk. Marks persist until reload — correct for the whole
// session; customs are never deleted mid-session.
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
    try { /* console.warn("[draft] custom file download failed", eD); */ } catch (eL) {}
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
    try { /* console.warn("[draft] custom bundle download failed", eB); */ } catch (eL) {}
  }
  return false;
}

// Manual save-all (Ρυθμίσεις row, v54.25–26): downloads one bundle file for
// all session-new custom molecules (drawn/updated this session; untouched
// boot-loaded file customs are skipped — their files exist). Stored entries
// excluded. v54.26: single bundle instead of a per-file loop (stacked Save
// dialogs kept only the last file on ask-before-download browsers).
function fMolDraftSaveAllCustom() {
  if (fMolDraftPresenting()) return;
  var keys = [];
  try { keys = fMolDraftNewCustomKeys(); } catch (eK) { keys = []; }
  if (!keys.length) {
    fMolDraftToast(fMolDraftT("customSaveAllNone", "Nothing new to save — draw and Accept a molecule first."));
    return;
  }
  var recs = [];
  for (var i = 0; i < keys.length; i++) {
    var rec = null;
    try { rec = window.nameExamplesCustom[keys[i]] || null; } catch (eR) { rec = null; }
    if (rec) recs.push(rec);
  }
  if (recs.length && fMolDraftDownloadBundle(recs)) {
    fMolDraftToast(recs.length + " " + fMolDraftT("customSaveAllBundleDone", "molecules saved in one bundle file — place it next to the data file."));
  } else {
    try { /* console.warn("[draft] save-all bundle failed for " + keys.length + " molecules"); */ } catch (eW) {}
    fMolDraftToast(fMolDraftT("customSaveAllFail", "Save failed — see console."));
  }
}

function fMolDraftSyncSaveBtn() {
  try {
    // Single entry is the title-bar #saveMolBtn (settings row removed v55.x):
    // same hasNew state, btnInactive only (title-bar buttons have no
    // disabled contract).
    var hasNewT = false;
    try { hasNewT = fMolDraftNewCustomKeys().length > 0; } catch (eCT) { hasNewT = false; }
    var tbtn = document.getElementById("saveMolBtn");
    if (tbtn) {
      if (hasNewT) tbtn.classList.remove("btnInactive");
      else tbtn.classList.add("btnInactive");
    }
  } catch (eS) {}
}

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
      if (!_skel) { try { /* console.warn("[draft] skeletal fallback: drawn geometry"); */ } catch (eW1) {} }
    } else if (drawnVariant === "expanded" && isFork) {
      // Edit-expanded fork: same full generation as New (linearize → top-up),
      // never the hand geometry verbatim.
      var _linE = (typeof fLinearizeMol === "function") ? fLinearizeMol(d.molText, _chainLive) : null;
      if (!_linE) { try { /* console.warn("[draft] linearizer failed, condensed = drawn geometry"); */ } catch (eW1b) {} }
      molC = _linE || d.molText;
      if (typeof fStripHydrogensMol === "function") {
        try { molC = (fStripHydrogensMol(molC) || molC); } catch (eStE) {}
      }
      molE = (typeof fGenExpandedMol === "function") ? (fGenExpandedMol(molC) || null) : null;
      if (!molE) { try { /* console.warn("[draft] expanded generation failed — mode disabled"); */ } catch (eW1c) {} }
      molS = _skel || molC;
      if (!_skel) { try { /* console.warn("[draft] skeletal fallback: drawn geometry"); */ } catch (eW1d) {} }
    } else if (drawnVariant === "skeletal" || drawnVariant === "condensedZigZag") {
      // Skeletal is always the ladder zigzag (see above) — the drawn MOL here
      // is layout-agnostic input, often already linearized by Beautify.
      molS = _skel || d.molText;
      if (!_skel) { try { /* console.warn("[draft] skeletal fallback: drawn geometry"); */ } catch (eW2b) {} }
      var _lin = (typeof fLinearizeMol === "function") ? fLinearizeMol(d.molText, _chainLive) : null;
      if (!_lin) { try { /* console.warn("[draft] linearizer failed, condensed = drawn geometry"); */ } catch (eW2) {} }
      molC = _lin || d.molText;
      molE = (typeof fGenExpandedMol === "function") ? (fGenExpandedMol(molC) || null) : null;
      if (!molE) { try { /* console.warn("[draft] expanded generation failed — mode disabled"); */ } catch (eW3) {} }
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
      if (!molE) { try { /* console.warn("[draft] expanded generation failed — mode disabled"); */ } catch (eW4) {} }
      molS = _skel || molC;
      if (!_skel) { try { /* console.warn("[draft] skeletal fallback: drawn geometry"); */ } catch (eW5) {} }
    }
  } catch (eDv) { molC = d.molText; molE = null; molS = d.molText; }
  if (!molC) molC = d.molText;
  if (!molS) molS = molC;
  // One-line slot geometry receipt (Y-inclusive: straight vs zigzag layouts
  // share x-projections, so x-only sums cannot tell them apart).
  try {
    // console.log("[draft] slots variant=" + drawnVariant + " skelSrc=" + (_skelSrc || "-") +
      // " C:[" + _sigOf(molC) + "] E:[" + _sigOf(molE) + "] S:[" + _sigOf(molS) + "] draw:[" + _sigOf(d.molText) + "]");
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
      try { /* console.warn("[draft] stray H: " + _strays.length + " over 1.5x H scale (" + _strays.slice(0, 4).map(function (s) { return "H" + s.h + "/C" + s.parent + "x" + s.ratio; }).join(", ") + ")"); */ } catch (eLw) {}
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
function fMolDraftSyncButtons() {
  try { if (typeof fMolDraftSyncEntryButtons === "function") fMolDraftSyncEntryButtons(); } catch (eEb) {}
  try {
    var eb = document.getElementById("editMolBtn");
    if (!eb) return;
    var hasMol = false;
    try {
      hasMol = (typeof selectedMol !== "undefined") && !!selectedMol &&
        (typeof nameExamples !== "undefined") && !!nameExamples[selectedMol];
    } catch (eM) { hasMol = false; }
    if (hasMol) eb.classList.remove("btnInactive");
    else eb.classList.add("btnInactive");
  } catch (eS) {}
  try {
    var sab = document.getElementById("selectAtomsBtn");
    if (sab) {
      var hasMolSel = false;
      try {
        hasMolSel = (typeof selectedMol !== "undefined") && !!selectedMol &&
          (typeof nameExamples !== "undefined") && !!nameExamples[selectedMol];
      } catch (eM2) { hasMolSel = false; }
      if (hasMolSel) sab.classList.remove("btnInactive");
      else sab.classList.add("btnInactive");
    }
  } catch (eS2) {}
  try { if (typeof fMolDraftSyncSaveBtn === "function") fMolDraftSyncSaveBtn(); } catch (eSy) {}
}

document.addEventListener("click", function (e) {
  var panel = document.getElementById("viewerSettingsPanel");
  var btn = document.getElementById("viewerSettingsBtn");
  if (!panel || !btn) return;
  if (
    !panel.contains(e.target) &&
    e.target !== btn &&
    !btn.contains(e.target)
  ) {
    panel.classList.remove("open");
    btn.classList.remove("active");
  }
});

// ── single-viewer max-height control (v48) ───────────────────────────────
// Ρυθμίσεις row: a checkbox (unchecked = Auto, checked = Manual) plus a px
// slider. Auto caps a lone viewer at the both-visible height; Manual uses the
// slider value; "full" (the Full toggle) resolves per playback screen.
// Only the live global `viewerMaxH` is set here — scenario steps own
// persistence (show.viewerMaxHeight). fResizeViewers() recomputes.
//
// `fViewerMaxHeightFull` (below) no longer ceilings the slider — it documents
// the live full single-viewer height the "full" sentinel resolves to.
function fViewerMaxHeightFull() {
  try { return Math.max(VIEWER_MIN_H, Math.round(fViewerHeights2D3D(true).full || 0)); }
  catch (eF) { return VIEWER_MIN_H; }
}

function fViewerMaxHeightEnsureFullBtn() {
  var row = null;
  try { row = document.getElementById("viewerMaxHeightSetting"); } catch (eR) { /* no DOM */ }
  if (!row || document.getElementById("viewerMaxHeightFull")) return;
  var b = document.createElement("button");
  b.type = "button";
  b.id = "viewerMaxHeightFull";
  b.className = "viewerFullBtn";
  b.textContent = "Full";
  try { b.title = ((typeof fMulerT === "function") ? fMulerT("fullHeight") : "Πλήρες ύψος οθόνης — προσαρμόζεται σε κάθε οθόνη προβολής"); } catch (eT) { b.title = "Πλήρες ύψος οθόνης — προσαρμόζεται σε κάθε οθόνη προβολής"; }
  b.setAttribute("aria-label", (typeof fMulerT === "function") ? fMulerT("fullHeight") : "Πλήρες ύψος οθόνης — προσαρμόζεται σε κάθε οθόνη προβολής");
  b.setAttribute("aria-pressed", "false");
  b.addEventListener("click", function (ev) {
    if (ev && ev.preventDefault) ev.preventDefault();
    fViewerMaxHeightToggleFull();
  });
  row.appendChild(b);
}

function fViewerMaxHeightToggleFull() {
  if (viewerMaxH === "full") {
    var rng = null;
    try { rng = document.getElementById("viewerMaxHeightRange"); } catch (eR) { /* no DOM */ }
    var v = rng ? parseInt(rng.value, 10) : NaN;
    if (isNaN(v)) v = VIEWER_SINGLE_MAX;
    if (v < VIEWER_MIN_H) v = VIEWER_MIN_H;
    if (v > VIEWER_SINGLE_MAX) v = VIEWER_SINGLE_MAX;
    viewerMaxH = v;
  } else {
    viewerMaxH = "full";
  }
  fViewerMaxHeightSync();
  try { fResizeViewers(); } catch (eR) { /* resize best-effort */ }
}

function fViewerMaxHeightSync() {
  var chk = document.getElementById("viewerMaxHeightCheck");
  var rng = document.getElementById("viewerMaxHeightRange");
  var val = document.getElementById("viewerMaxHeightVal");
  if (!chk || !rng) return;
  fViewerMaxHeightEnsureFullBtn();
  var full = viewerMaxH === "full";
  var manual = viewerMaxH != null;
  try {
    chk.classList.toggle("selectedCheck", manual);
    chk.classList.toggle("unselectedCheck", !manual);
  } catch (eC) { /* class toggle best-effort */ }
  var btn = null;
  try { btn = document.getElementById("viewerMaxHeightFull"); } catch (eB) { /* no DOM */ }
  if (btn) {
    try {
      btn.classList.toggle("active", full);
      btn.setAttribute("aria-pressed", full ? "true" : "false");
    } catch (eA) { /* button state best-effort */ }
  }
  // Fixed ceiling (v52): the slider no longer follows the screen height.
  rng.min = String(VIEWER_MIN_H);
  rng.max = String(VIEWER_SINGLE_MAX);
  rng.disabled = !manual || full;
  if (full) {
    // Park the slider at max while Full owns the value; the readout names it.
    rng.value = String(VIEWER_SINGLE_MAX);
    if (val) val.textContent = "Full";
    return;
  }
  var shown;
  if (manual) {
    shown = Math.round(viewerMaxH);
  } else {
    var vh = fViewerHeights2D3D();
    shown = Math.round(vh.h2 || vh.h3 || Math.round(fViewerMaxHeightFull() / 2));
  }
  if (shown < VIEWER_MIN_H) shown = VIEWER_MIN_H;
  if (shown > VIEWER_SINGLE_MAX) shown = VIEWER_SINGLE_MAX;
  rng.value = String(shown);
  if (val) val.textContent = shown + "px";
}

function fViewerMaxHeightFromUi() {
  var chk = document.getElementById("viewerMaxHeightCheck");
  var rng = document.getElementById("viewerMaxHeightRange");
  if (!chk || !rng) return;
  if (chk.classList.contains("selectedCheck")) {
    // The Full toggle owns the value while active — a checkbox tick from the
    // generic handler must not overwrite it with the parked slider value.
    if (viewerMaxH !== "full") {
      var v = parseInt(rng.value, 10);
      if (isNaN(v)) v = VIEWER_MIN_H;
      if (v < VIEWER_MIN_H) v = VIEWER_MIN_H;
      if (v > VIEWER_SINGLE_MAX) v = VIEWER_SINGLE_MAX;
      viewerMaxH = v;
    }
  } else {
    viewerMaxH = null;
  }
  fViewerMaxHeightSync();
  try { fResizeViewers(); } catch (eR) { /* resize best-effort */ }
}

function fInitViewerMaxHeight() {
  var chk = document.getElementById("viewerMaxHeightCheck");
  var rng = document.getElementById("viewerMaxHeightRange");
  if (!chk || !rng) {
    // Script may run before the static panel is parsed; retry once then bind.
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fInitViewerMaxHeight);
    }
    return;
  }
  // The generic .checkBoxContainer handler toggles the class on the same
  // click; defer a tick so the post-toggle state is what we read.
  if (!chk.dataset.vmhBound) {
    chk.dataset.vmhBound = "1";
    chk.addEventListener("click", function () { setTimeout(fViewerMaxHeightFromUi, 0); });
  }
  if (rng && !rng.dataset.vmhBound) {
    rng.dataset.vmhBound = "1";
    rng.addEventListener("input", fViewerMaxHeightFromUi);
  }
  fViewerMaxHeightSync();
}

// ── double-viewer height control (v48) ───────────────────────────────────
// Ρυθμίσεις row: a checkbox (unchecked = Auto = the equal split both viewers
// get today, checked = Manual) plus a fixed slider (see VIEWER_BOTH_MIN/MAX).
// When two viewers are visible, Manual sets their COMBINED height — each
// viewer takes half. "full" (the Full toggle) fills the live viewport instead.
// Only the live global `viewerBothH` is set here — scenario steps own
// persistence (show.viewerBothHeight). fResizeViewers() recomputes.
function fViewerBothHeightEnsureFullBtn() {
  var row = null;
  try { row = document.getElementById("viewerBothHeightSetting"); } catch (eR) { /* no DOM */ }
  if (!row || document.getElementById("viewerBothHeightFull")) return;
  var b = document.createElement("button");
  b.type = "button";
  b.id = "viewerBothHeightFull";
  b.className = "viewerFullBtn";
  b.textContent = "Full";
  try { b.title = ((typeof fMulerT === "function") ? fMulerT("fullHeight") : "Πλήρες ύψος οθόνης — προσαρμόζεται σε κάθε οθόνη προβολής"); } catch (eT) { b.title = "Πλήρες ύψος οθόνης — προσαρμόζεται σε κάθε οθόνη προβολής"; }
  b.setAttribute("aria-label", (typeof fMulerT === "function") ? fMulerT("fullHeight") : "Πλήρες ύψος οθόνης — προσαρμόζεται σε κάθε οθόνη προβολής");
  b.setAttribute("aria-pressed", "false");
  b.addEventListener("click", function (ev) {
    if (ev && ev.preventDefault) ev.preventDefault();
    fViewerBothHeightToggleFull();
  });
  row.appendChild(b);
}

function fViewerBothHeightToggleFull() {
  if (viewerBothH === "full") {
    var rng = null;
    try { rng = document.getElementById("viewerBothHeightRange"); } catch (eR) { /* no DOM */ }
    var v = rng ? parseInt(rng.value, 10) : NaN;
    if (isNaN(v)) v = VIEWER_BOTH_MAX;
    if (v < VIEWER_BOTH_MIN) v = VIEWER_BOTH_MIN;
    if (v > VIEWER_BOTH_MAX) v = VIEWER_BOTH_MAX;
    viewerBothH = v;
  } else {
    viewerBothH = "full";
  }
  fViewerBothHeightSync();
  try { fResizeViewers(); } catch (eR) { /* resize best-effort */ }
}

function fViewerBothHeightSync() {
  var chk = document.getElementById("viewerBothHeightCheck");
  var rng = document.getElementById("viewerBothHeightRange");
  var val = document.getElementById("viewerBothHeightVal");
  if (!chk || !rng) return;
  fViewerBothHeightEnsureFullBtn();
  var full = viewerBothH === "full";
  var manual = viewerBothH != null;
  try {
    chk.classList.toggle("selectedCheck", manual);
    chk.classList.toggle("unselectedCheck", !manual);
  } catch (eC) { /* class toggle best-effort */ }
  var btn = null;
  try { btn = document.getElementById("viewerBothHeightFull"); } catch (eB) { /* no DOM */ }
  if (btn) {
    try {
      btn.classList.toggle("active", full);
      btn.setAttribute("aria-pressed", full ? "true" : "false");
    } catch (eA) { /* button state best-effort */ }
  }
  rng.min = String(VIEWER_BOTH_MIN);
  rng.max = String(VIEWER_BOTH_MAX);
  rng.disabled = !manual || full;
  if (full) {
    rng.value = String(VIEWER_BOTH_MAX);
    if (val) val.textContent = "Full";
    return;
  }
  var shown;
  if (manual) {
    shown = Math.round(viewerBothH);
  } else {
    // Auto: the combined height the equal split currently yields (2D + 3D).
    var vh = fViewerHeights2D3D();
    shown = Math.round((vh.h2 || 0) + (vh.h3 || 0) || VIEWER_BOTH_MIN);
  }
  if (shown < VIEWER_BOTH_MIN) shown = VIEWER_BOTH_MIN;
  if (shown > VIEWER_BOTH_MAX) shown = VIEWER_BOTH_MAX;
  rng.value = String(shown);
  if (val) val.textContent = shown + "px";
}

function fViewerBothHeightFromUi() {
  var chk = document.getElementById("viewerBothHeightCheck");
  var rng = document.getElementById("viewerBothHeightRange");
  if (!chk || !rng) return;
  if (chk.classList.contains("selectedCheck")) {
    // The Full toggle owns the value while active — see single-viewer note.
    if (viewerBothH !== "full") {
      var v = parseInt(rng.value, 10);
      if (isNaN(v)) v = VIEWER_BOTH_MIN;
      if (v < VIEWER_BOTH_MIN) v = VIEWER_BOTH_MIN;
      if (v > VIEWER_BOTH_MAX) v = VIEWER_BOTH_MAX;
      viewerBothH = v;
    }
  } else {
    viewerBothH = null;
  }
  fViewerBothHeightSync();
  try { fResizeViewers(); } catch (eR) { /* resize best-effort */ }
}

function fInitViewerBothHeight() {
  var chk = document.getElementById("viewerBothHeightCheck");
  var rng = document.getElementById("viewerBothHeightRange");
  if (!chk || !rng) {
    // Script may run before the static panel is parsed; retry once then bind.
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fInitViewerBothHeight);
    }
    return;
  }
  // The generic .checkBoxContainer handler toggles the class on the same
  // click; defer a tick so the post-toggle state is what we read.
  if (!chk.dataset.vbhBound) {
    chk.dataset.vbhBound = "1";
    chk.addEventListener("click", function () { setTimeout(fViewerBothHeightFromUi, 0); });
  }
  if (rng && !rng.dataset.vbhBound) {
    rng.dataset.vbhBound = "1";
    rng.addEventListener("input", fViewerBothHeightFromUi);
  }
  fViewerBothHeightSync();
}

// ── fToggleNameSettings ────────────────────────────────────────────────

// Initialize name settings button markup into #nameSettingsBtnDiv.
// Uses existing `svgSettings` constant and the fToggleNameSettings() handler.

function fToggleNameSettings() {
  nameSettingsFlag = !nameSettingsFlag;
  var panel = document.getElementById("nameSettingsPanel");
  var btn = document.getElementById("nameSettingsBtn");
  // var isOpen = panel.classList.contains('open')
  if (!nameSettingsFlag) {
    panel.classList.remove("open");
    btn.classList.remove("active");
  } else {
    panel.classList.add("open");
    btn.classList.add("active");
  }
  // The panel sits above the name boxes and animates (0.25s): re-pin the
  // floating Explain sheet now and once the transition settles.
  try { fNameExpandRepinDelayed(); } catch (eR) { /* best-effort */ }
}

// ── fToggleMolInfo / fRenderMolInfo ───────────────────────────────────────
// Live-only molecule info panel (SMILES + PubChem IUPAC + common ether name),
// toggled by the info button left of the gear. Never stored in steps.
// Content refreshes on every naming rebuild (fShowNameAnalysis calls
// fRenderMolInfo) and in place when a pending PubChem fetch resolves
// (fMulerMolInfoRefresh, guarded).
// Locally joined transliterated common ether name, for INTERNAL comparison
// only (verdict common-match check). Never displayed: the info panel shows
// verbatim PubChem data or nothing, so no locally joined string can appear
// under a "(PubChem)" label. EN joins alkyl words with spaces
// ("ethyl methyl ether", multiplier fused: "dimethyl ether"); Greek stays
// one word ("διμεθυλαιθέρας"). Returns null on any gap.
function fMulerENCommonName() {
  try {
    if (typeof selectedMol === "undefined" || !selectedMol) return null;
    var parts = null;
    try { parts = (typeof fGetEtherCommonParts === "function") ? fGetEtherCommonParts() : null; } catch (eP) { return null; }
    if (!parts || !Array.isArray(parts.parts) || !parts.parts.length) return null;
    var isEN = true;
    try { isEN = (typeof fMulerLang === "function") && fMulerLang() === "en"; } catch (eL) { isEN = true; }
    var alkyls = [], noun = "";
    for (var i = 0; i < parts.parts.length; i++) {
      var p = parts.parts[i] || {};
      var lab = p.label || "";
      if (!lab) return null;
      var isNoun = p.kind === "ether" || /^(αιθέρ|αιθερ|ether)/i.test(String(lab));
      if (isNoun) {
        if (noun) return null;
        noun = isEN ? "ether" : String(lab);
        continue;
      }
      var w = String(lab);
      if (isEN) {
        if (typeof fMulerENCommonLabel !== "function") return null;
        w = fMulerENCommonLabel(lab);
        if (!w || /[\u0370-\u03ff\u1f00-\u1fff]/.test(w)) return null;
      }
      alkyls.push(w);
    }
    if (!alkyls.length || !noun) return null;
    if (isEN) {
      var words = alkyls.slice();
      if (words.length >= 2 && /^(di|tri|tetra)$/i.test(words[0])) words = [words[0] + words[1]].concat(words.slice(2));
      return words.join(" ") + " " + noun;
    }
    return alkyls.join("") + noun;
  } catch (e) { return null; }
}
function fToggleMolInfo() {
  try {
    molInfoOpenFlag = !molInfoOpenFlag;
  } catch (eF) {
    try { molInfoOpenFlag = true; } catch (eF2) { /* best-effort */ }
  }
  try { fRenderMolInfo(); } catch (eR) { /* best-effort */ }
}

// In-place refresh hook for the PubChem fetch completion in iupac-54.js.
// Skipped unless the fetched molecule is on screen and the panel is open.
function fMulerMolInfoRefresh(key) {
  try {
    if (typeof selectedMol === "undefined" || selectedMol !== key) return;
    if (!molInfoOpenFlag) return;
    fRenderMolInfo();
  } catch (e) { /* best-effort */ }
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

function fCopyMolSmiles(btn) {
  var smi = "";
  try {
    smi = (typeof selectedMol !== "undefined" && selectedMol && typeof nameExamples !== "undefined" && nameExamples[selectedMol])
      ? (nameExamples[selectedMol].canonicalSmiles || nameExamples[selectedMol].smiles || "") : "";
  } catch (eS) { smi = ""; }
  if (!smi) return;
  var done = function () {
    if (!btn) return;
    var t = "Αντιγράφηκε";
    try { t = (typeof fMulerT === "function") ? fMulerT("molInfoCopied") : "Αντιγράφηκε"; } catch (eT) { /* keep default */ }
    try {
      var prev = btn.getAttribute("data-tooltip");
      btn.setAttribute("data-tooltip", t);
      setTimeout(function () { try { btn.setAttribute("data-tooltip", prev || ""); } catch (eR) { /* best-effort */ } }, 1200);
    } catch (eA) { /* best-effort */ }
  };
  try {
    if (typeof navigator !== "undefined" && navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(smi).then(done, done);
      return;
    }
  } catch (eC) { /* fall through to legacy path */ }
  try {
    var ta = document.createElement("textarea");
    ta.value = smi;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    ta.parentNode.removeChild(ta);
    done();
  } catch (eF) { /* clipboard unavailable */ }
}

// document.addEventListener('click', function (e) {
//     var panel = document.getElementById('nameSettingsPanel')
//     var btn = document.getElementById('nameSettingsBtn')
//     if (!panel || !btn) return
//     if (!panel.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
//         panel.classList.remove('open')
//         btn.classList.remove('active')
//     }
// })

// ── fInitData ─────────────────────────────────────────────────────────────

function fInitData() {
  for (let prop in nameExamples) {
    const _m = (window.MOL2D && window.MOL2D[prop]) || {};
    const my2D_Condensed = _m.condensed !== undefined ? _m.condensed : null;
    const my2D_Expanded = _m.expanded !== undefined ? _m.expanded : null;
    const my2D_Skeletal = _m.skeletal !== undefined ? _m.skeletal : null;

    nameExamples[prop].structure2D_Condensed = my2D_Condensed;
    nameExamples[prop].structure2D_Expanded = my2D_Expanded;
    nameExamples[prop].structure2D_Skeletal = my2D_Skeletal;

    const my3D = "mols/nomeclature-moc2/" + prop + "_3D.sdf";
    nameExamples[prop].file3D = my3D;
  }
}

// ── fMakeAnnotatedSkeletal ────────────────────────────────────────────────
// Takes a V2000 skeletal MOL string and makes every carbon atom visible
// by replacing the 3-char atom-symbol field 'C  ' with '[C]'.
// JSME renders [C] atoms with a visible 'C' label, so fAddHydrogens2SVG
// can then annotate each with its hydrogen count.

function fMakeAnnotatedSkeletal(molStr) {
  if (!molStr) {
    return molStr;
  }
  const lines = String(molStr).split(/\r?\n/);
  const ci = (typeof fMolCountsLine === "function") ? fMolCountsLine(lines) : -1;
  if (ci < 0) return molStr;
  const atomCount = parseInt(lines[ci].substring(0, 3), 10);
  if (isNaN(atomCount)) return molStr;
  for (let i = ci + 1; i < ci + 1 + atomCount && i < lines.length; i++) {
    if (lines[i].substring(31, 34) === "C  ") {
      lines[i] = lines[i].substring(0, 31) + "[C]" + lines[i].substring(34);
    }
  }
  return lines.join("\n");
}

// ── fUpdateChainModeButton ────────────────────────────────────────────────

function fUpdateChainModeButton() {
  const $dataBtn = $("#radioChainMode .radioCheckContainer").eq(0);
  // Stored chain keys use _Condensed/_Expanded/_Skeletal (see fMainChainKeySuffix).
  const chainKeySuffix = fMainChainKeySuffix();
  const _storedChain =
    selectedMol && nameExamples[selectedMol]
      ? nameExamples[selectedMol]["mainChain" + chainKeySuffix]
      : null;
  // No molecule selected, key missing, or an empty stored array (the ether/
  // ester and two branched-alkane placeholders) all mean "no stored data".
  const hasChainData = Array.isArray(_storedChain) && _storedChain.length > 0;
  if (hasChainData) {
    $dataBtn.removeClass("disabledRadio");
  } else {
    $dataBtn.addClass("disabledRadio");
    if (mainChainMode === "data") {
      mainChainMode = "algorithmic";
    }
  }
  // Always sync radio visuals to current mainChainMode
  const algoIdx = mainChainMode === "algorithmic" ? 1 : 0;
  $("#radioChainMode .radioCheckContainer")
    .removeClass("selectedRadio")
    .addClass("unselectedRadio");
  $("#radioChainMode .radioCheckContainer")
    .eq(algoIdx)
    .removeClass("unselectedRadio")
    .addClass("selectedRadio");
}

// ── fUpdateDiagr2DButton ──────────────────────────────────────────────────
// Generalised: disables any 2D mode radio whose representation is missing
// (condensed=eq(0), expanded=eq(1), skeletal=eq(2)) and falls
// back to the first available representation (condensed > expanded > skeletal).

function fUpdateDiagr2DButton() {
  const $modeBtns = $("#radio2DMode .radioCheckContainer");
  const $condBtn = $modeBtns.eq(0);
  const $expBtn = $modeBtns.eq(1);
  const $diagrBtn = $modeBtns.eq(2);
  const $zigzagCheck = $("#zigzagCheck");
  const ex = selectedMol ? nameExamples[selectedMol] : null;
  const hasCondensed2D = !selectedMol || !!ex?.structure2D_Condensed;
  const hasExpanded2D = !selectedMol || !!ex?.structure2D_Expanded;
  const hasSkeletal2D = !selectedMol || !!ex?.structure2D_Skeletal;
  $condBtn.toggleClass("disabledRadio", !hasCondensed2D);
  $expBtn.toggleClass("disabledRadio", !hasExpanded2D);
  $diagrBtn.toggleClass("disabledRadio", !hasSkeletal2D);

  const modeAvailable =
    mode2D === "condensed"
      ? hasCondensed2D
      : mode2D === "expanded"
        ? hasExpanded2D
        : hasSkeletal2D; // skeletal + condensedZigZag share structure2D_Skeletal
  if (selectedMol && !modeAvailable) {
    if (hasCondensed2D) {
      mode2D = "condensed";
      modeSuffix = "_2D_Condensed";
    } else if (hasExpanded2D) {
      mode2D = "expanded";
      modeSuffix = "_2D_Expanded";
    } else if (hasSkeletal2D) {
      mode2D = "skeletal";
      modeSuffix = "_2D_Skeletal";
    }
    const fallbackIdx =
      mode2D === "expanded" ? 1 : mode2D === "condensed" ? 0 : 2;
    $modeBtns.removeClass("selectedRadio").addClass("unselectedRadio");
    $modeBtns
      .eq(fallbackIdx)
      .removeClass("unselectedRadio")
      .addClass("selectedRadio");
  }

  if (hasSkeletal2D) {
    if (mode2D === "skeletal" || mode2D === "condensedZigZag") {
      // $zigzagCheck.show();
      $zigzagCheck.removeClass("disabledCheck");
      if (mode2D === "condensedZigZag") {
        $zigzagCheck.removeClass("unselectedCheck").addClass("selectedCheck");
      } else {
        $zigzagCheck.removeClass("selectedCheck").addClass("unselectedCheck");
      }
    } else {
      $zigzagCheck.addClass("disabledCheck");
      $zigzagCheck.removeClass("selectedCheck").addClass("unselectedCheck");
    }
  } else {
    $zigzagCheck.addClass("disabledCheck");
    $zigzagCheck.removeClass("selectedCheck").addClass("unselectedCheck");
  }
}

// ── fSyncAtomColorModeDisabled ────────────────────────────────────────────
// The 2D "Κατά άτομο / Κατά ομάδα" radios are only meaningful while colored
// symbols are on (#svgAtomColorCheck). Dim + inert them when the coloring
// toggle is off (same .disabledRadio convention as the 2D mode radios).

function fSyncAtomColorModeDisabled() {
  var on = typeof svgAtomColors2DFlag !== "undefined" ? svgAtomColors2DFlag : true;
  $("#atomColorMode .atomColorModeRadio").toggleClass("disabledRadio", !on);
}

// ── fSelectMol ────────────────────────────────────────────────────────────

function fSelectMol() {
  fMolDraft3DInvalidate();
  // Draft session (v54 Stage 2): menu/row clicks must not clobber the draft
  // canvas (fLoadMol2D reads into the same applet). Cancel nulls the flag
  // before its own fSelectMol, so restore still works.
  if (typeof window !== "undefined" && window.MulerDraft) {
    try { if (typeof fScenarioToast === "function") fScenarioToast(fMolDraftT("draftLocked", "Finish the draft first (Submit/Cancel).")); } catch (eD) {}
    return;
  }
  if (!selectedMol || !nameExamples[selectedMol]) {
    return;
  }

  fInitProps();
  fClearHighlights();
  fUpdateDiagr2DButton();
  fUpdateChainModeButton();
  fLoadMol2D();
  fLoadMol3D();
  fFetchAndParse3D();

  showAtomSymbols3D();
  showHydrogens3D();
  rotate3D();

  // Systematic EN variant for the Traditional/Systematic toggle: compute BEFORE
  // the name panel builds (the toggle's visibility reads engineEN_sys).
  // Same-slot transliteration, mapped substituents; null when identical to
  // school or untranslatable. School engineEN is computed here too (v54.30):
  // it used to run AFTER the panel build, so on a cold first select the
  // toggle compared the fresh sys string against the previous molecule's
  // (or undefined) school name and showed spuriously on nearly every
  // molecule. Order between the two calls is irrelevant; both must precede
  // fShowNameAnalysis.
  try {
    if (typeof fPopulateEngineENFromGreek === "function")
      fPopulateEngineENFromGreek(selectedMol, "sys");
  } catch (eEnSys) {
    /* systematic best-effort */
  }
  try {
    if (typeof fPopulateEngineENFromGreek === "function")
      fPopulateEngineENFromGreek(selectedMol);
  } catch (eEnPopSel) {
    /* engine best-effort */
  }

  // fShowMolName()
  // Cold-boot hardening: a throw here must never silently kill the naming
  // panel (2D already painted above). Log loudly with a tag and continue;
  // the ready-hook resend retries the full select when naming is missing.
  try {
    fShowNameAnalysis();
  } catch (eNA) {
    try { /* console.error("[COLD-BOOT] fShowNameAnalysis failed for " + selectedMol, eNA); */ } catch (eL) { /* console unavailable */ }
  }

  getMolData();

  // v53 select-log: every molecule selection console-logs key + SMILES +
  // cached IUPAC; fire-and-forget fetch fills missing IUPAC without blocking UI.
  try {
    if (typeof fLogMolSelectWithIUPAC === "function")
      fLogMolSelectWithIUPAC(selectedMol);
  } catch (eIupacLog) {
    /* log best-effort */
  }
  try {
    if (typeof fLogMolSelectWithOC === "function")
      fLogMolSelectWithOC(selectedMol);
  } catch (eOCLog) {
    /* second oracle best-effort */
  }

  // (School + systematic engineEN are both computed before the panel build
  // above since v54.30; no later call needed.)
  // Draft entries: Edit needs a selected molecule (visual state only; the
  // click-time guard in fMolDraftEnter is the backstop).
  try { if (typeof fMolDraftSyncButtons === "function") fMolDraftSyncButtons(); } catch (eDs) {}
}

// ── fDeselectMol ──────────────────────────────────────────────────────────

function fDeselectMol() {
  fMolDraft3DInvalidate();
  fInitProps();
  try { if (typeof fMulerQuizDisarm === "function") fMulerQuizDisarm(); } catch (eQD) {}
  // Deselect clears the selection (fInitProps no longer resets the mode —
  // sticky selection across molecule switches lives there).
  try { nameAnalysisMode = "none"; } catch (eM) {}
  fClearHighlights();

  selectedMol = null;
  $(".menuLi").removeClass("selectedLi");
  try { window.__mulerSelGroupKey = null; } catch (eGk) { /* best-effort */ }
  try { window.__mulerUserPickedMol = false; } catch (eUp) { /* best-effort */ }

  myMol3D = null;
  fJSmolScript(jmolAppletNomeclature, "zap");
  try {
    if (typeof MuLERMoCScenario !== "undefined") MuLERMoCScenario.reload3DOnce = false;
  } catch (eFlag) {
    /* flag best-effort */
  }

  myMol2D = null;
  if (jsmeNomeclatureApplet) jsmeNomeclatureApplet.reset();
  if (jsmeNomeclatureAppletORGNL) jsmeNomeclatureAppletORGNL.reset();
  try { fUpdateSVG(); } catch (eU) { try { /* console.error("[COLD-BOOT] fUpdateSVG failed in fDeselectMol", eU); */ } catch (eL) {} }

  $("#molName").html("");
  nameComponentsList = [];
  try { fShowNameAnalysis(); } catch (eNA2) { try { /* console.error("[COLD-BOOT] fShowNameAnalysis failed in fDeselectMol", eNA2); */ } catch (eL2) {} }
  fUpdateDiagr2DButton();
  fUpdateChainModeButton();
  try { if (typeof fMolDraftSyncButtons === "function") fMolDraftSyncButtons(); } catch (eDs) {}
}

// ── fInitProps ────────────────────────────────────────────────────────────

function fInitProps() {
  currNumberEl = 0;
  clearInterval(myNumberingTimeout);
  // Sticky selection: nameAnalysisMode is NOT reset here — selecting another
  // molecule keeps the component selected when the new molecule has the same
  // component (fShowNameAnalysis restores .selected + highlight from the
  // mode, or falls back to "none" when the box is absent/hidden). Explicit
  // resets live where clearing is intended: fDeselectMol, scenario apply
  // (step's stored mode), draft flows that rebuild naming from scratch.
  // Sticky visibility: the hidden-comp set is NOT reset here (v55 working
  // copy) — hiding follows the author across molecule switches (menu steps
  // and main-app browsing hide the same slots everywhere). Fresh starts reset
  // explicitly: cold boot (see init), draft New entry. Scenario applies
  // overwrite with the stored step set; Present entry/exit stash + restore
  // the author's live set.
  carbons = 0;
  ruleTableHighlight = null;
  // New-molecule reset: 2D zoom returns to default on every molecule load.
  // Mode/chain switches call fLoadMol2D directly (teaching layer) and keep
  // the live zoom for comparison. Scenario steps re-assert their stored zoom
  // after fSelectMol returns.
  molZoom2D = MOL_ZOOM_DEFAULT;
  // Stepper pools go stale with the molecule: fCalcMainChain rebuilds them on
  // the next load (index resets to 0 there). Guarded: core may be absent.
  try {
    if (typeof mainChainPool !== "undefined") { mainChainPool = []; mainChainPoolIdx = 0; }
    if (typeof mainChainPool3D !== "undefined") { mainChainPool3D = []; mainChainPool3DKey = null; }
    if (typeof molAtomMap2D3D !== "undefined") { molAtomMap2D3D = null; molAtomMapKey = null; }
  } catch (ePool) { /* core unavailable */ }
}

// ── fShowMolName ──────────────────────────────────────────────────────────

function fShowMolName() {
  if (!selectedMol || !nameExamples[selectedMol]) {
    $("#molName").html("");
    return;
  }

  let molName = currentMolName;
  $("#molName").html(molName);
}

// ── fLoadMol2D ────────────────────────────────────────────────────────────

// Pure V2000 display transform. Topology, atom order, stereo fields and z stay
// unchanged. A proper rotation preserves the authored layout wherever possible.
// BEGIN SKELETAL GEOMETRY
function fSkeletalLayoutMol(mol, chain, esterFragments = null) {
  const unchanged = {mol, rotation: 0, repairs: [], skipped: []};
  if (typeof mol !== "string" || !Array.isArray(chain)) return unchanged;
  const lines = mol.split(/\r?\n/);
  const ci = (typeof fMolCountsLine === "function") ? fMolCountsLine(lines) : -1;
  if (ci < 0) return unchanged;
  const start = ci + 1, counts = lines[ci];
  const n = Number(counts.slice(0, 3)), nb = Number(counts.slice(3, 6));
  if (!counts.includes("V2000") || !(n > 0) || !(nb >= 0) ||
      lines.length < start + n + nb) return unchanged;
  const points = lines.slice(start, start+n).map(l => [Number(l.slice(0,10)), Number(l.slice(10,20))]);
  const types = lines.slice(start, start+n).map(l => l.slice(31,34).trim());
  if (points.some(p => !p.every(Number.isFinite))) return unchanged;
  const parent = chain.map(i => i-1);
  if (new Set(parent).size !== parent.length || parent.some(i =>
      !Number.isInteger(i) || i < 0 || i >= n || types[i] !== 'C')) return unchanged;
  const bonds = lines.slice(start+n,start+n+nb).map(l =>
    [Number(l.slice(0,3))-1, Number(l.slice(3,6))-1, Number(l.slice(6,9))]);
  if (bonds.some(([a,b,o]) => !Number.isInteger(a) || !Number.isInteger(b) ||
      a < 0 || b < 0 || a >= n || b >= n || a === b || !(o > 0))) return unchanged;
  const adj = points.map(() => []), sp = new Set();
  bonds.forEach(([a,b,o]) => {
    adj[a].push(b); adj[b].push(a);
    if (o === 3) { sp.add(a); sp.add(b); }
  });
  function turn(ids, pivot, angle) {
    const co = Math.cos(angle), si = Math.sin(angle);
    for (const i of ids) {
      const x = points[i][0]-pivot[0], y = points[i][1]-pivot[1];
      points[i] = [pivot[0]+x*co-y*si, pivot[1]+x*si+y*co];
    }
  }
  function wrap(angle) { return Math.atan2(Math.sin(angle), Math.cos(angle)); }
  function cross(p,a,b,c) {
    return (p[b][0]-p[a][0])*(p[c][1]-p[a][1])-(p[b][1]-p[a][1])*(p[c][0]-p[a][0]);
  }
  function crosses(p,a,b,c,d) {
    return cross(p,a,b,c)*cross(p,a,b,d) < -1e-10 &&
      cross(p,c,d,a)*cross(p,c,d,b) < -1e-10;
  }
  function atomBondDistance(p,i,a,b) {
    const dx=p[b][0]-p[a][0], dy=p[b][1]-p[a][1], length=dx*dx+dy*dy;
    const t=length ? Math.max(0,Math.min(1,
      ((p[i][0]-p[a][0])*dx+(p[i][1]-p[a][1])*dy)/length)) : 0;
    return Math.hypot(p[i][0]-p[a][0]-t*dx,p[i][1]-p[a][1]-t*dy);
  }
  function safeRepair(previous) {
    const lengths=bonds.map(([a,b]) => Math.hypot(previous[a][0]-previous[b][0],previous[a][1]-previous[b][1])).sort((a,b)=>a-b);
    const unit=lengths[Math.floor(lengths.length/2)] || 1;
    const clearance=unit*0.45;
    const linked=new Set(bonds.map(([a,b]) => [Math.min(a,b),Math.max(a,b)].join(',')));
    for (let a=0; a<n; a++) for (let b=0; b<a; b++) {
      if (linked.has([b,a].join(','))) continue;
      const old=Math.hypot(previous[a][0]-previous[b][0],previous[a][1]-previous[b][1]);
      const now=Math.hypot(points[a][0]-points[b][0],points[a][1]-points[b][1]);
      if (now < clearance && now < old-1e-6) return false;
    }
    // Strict crossings miss endpoint-on-bond and collinear contacts. Test
    // every nonincident atom against each segment too, with bond-scaled space.
    for (const [a,b] of bonds) for (let i=0; i<n; i++) {
      if (i===a || i===b) continue;
      const old=atomBondDistance(previous,i,a,b), now=atomBondDistance(points,i,a,b);
      if (now < unit*0.12 && now < old-1e-6) return false;
    }
    for (let i=0; i<bonds.length; i++) for (let j=0; j<i; j++) {
      const [a,b]=bonds[i], [c,d]=bonds[j];
      if (a===c || a===d || b===c || b===d) continue;
      if (crosses(points,a,b,c,d) && !crosses(previous,a,b,c,d)) return false;
    }
    return true;
  }
  const all = points.map((_,i) => i), repairs = [], skipped = [];
  // A bent, degree-two sp carbon needs a local angle repair; global rotation
  // cannot fix it. Only move a whole acyclic side, retaining all bond lengths
  // and every other local angle. Never tear apart a ring or reflect a fragment.
  for (const center of sp) {
    if (types[center] !== 'C' || adj[center].length !== 2) continue;
    const sides = adj[center].map(start => {
      const seen = new Set([center]), ids = [], todo = [start];
      while (todo.length) {
        const i = todo.pop(); if (seen.has(i)) continue;
        seen.add(i); ids.push(i);
        adj[i].forEach(j => { if (!seen.has(j)) todo.push(j); });
      }
      return {start, ids};
    });
    // Prefer the side outside the numbered parent; otherwise its downstream
    // side, so corrections propagate from C1 towards the end of the chain.
    sides.sort((a,b) => {
      const ia = parent.indexOf(a.start), ib = parent.indexOf(b.start);
      return (ia < 0 ? -1 : 0)-(ib < 0 ? -1 : 0) || ib-ia || a.ids.length-b.ids.length;
    });
    const moving = sides[0], fixed = adj[center].find(i => i !== moving.start);
    const c = points[center], a = points[moving.start], b = points[fixed];
    if (Math.hypot(a[0]-c[0],a[1]-c[1]) < 1e-8 ||
        Math.hypot(b[0]-c[0],b[1]-c[1]) < 1e-8) continue;
    const angle = wrap(Math.atan2(b[1]-c[1],b[0]-c[0])+Math.PI-
      Math.atan2(a[1]-c[1],a[0]-c[0]));
    if (Math.abs(angle) < Math.PI/3600) continue; // <=0.05 degree input rounding
    if (moving.ids.includes(fixed)) { skipped.push(center+1); continue; }
    const previous=points.map(p=>p.slice());
    turn(moving.ids, c, angle);
    if (!safeRepair(previous)) {
      previous.forEach((p,i)=>{ points[i]=p; });
      skipped.push(center+1); continue;
    }
    repairs.push({atom: center+1, degrees: angle*180/Math.PI});
  }
  function bounds(ids, angle) {
    const co = Math.cos(angle), si = Math.sin(angle);
    const xs = ids.map(i => points[i][0]*co-points[i][1]*si);
    const ys = ids.map(i => points[i][0]*si+points[i][1]*co);
    return {width: Math.max(...xs)-Math.min(...xs), height: Math.max(...ys)-Math.min(...ys)};
  }
  const before = parent.length ? bounds(parent,0) : {height:0};
  let best = null;
  // Minimum-height strip: an optimum is parallel to an edge of the parent's
  // convex hull. Pair directions include those edges, without a hull dependency.
  // Degenerate/single-C parents keep their existing orientation.
  if (parent.length >= 2) {
    const angles = [0];
    for (let i=0; i<parent.length; i++) for (let j=0; j<i; j++) {
      const a=points[parent[j]], b=points[parent[i]];
      if (Math.hypot(b[0]-a[0],b[1]-a[1]) > 1e-8) angles.push(-Math.atan2(b[1]-a[1],b[0]-a[0]));
    }
    for (let angle of angles) {
      const first=points[parent[0]], last=points[parent[parent.length-1]];
      const dx=(last[0]-first[0])*Math.cos(angle)-(last[1]-first[1])*Math.sin(angle);
      if (dx < -1e-8) angle += Math.PI;
      angle=wrap(angle);
      const box=bounds(parent,angle), whole=bounds(all,angle);
      const score=[box.height, whole.height, Math.abs(angle)];
      const better=!best || score.some((v,i) =>
        score.slice(0,i).every((x,j) => Math.abs(x-best.score[j]) < 1e-6) && v < best.score[i]-1e-6);
      if (better) best={angle,score};
    }
  }
  let angle=best ? best.angle : 0;
  // Ester display convention takes precedence over C1-left progression.
  // Choose the half-turn inside this same pipeline, retaining every local
  // angle/length and its repair safeguards. Naming/numbering are unchanged.
  if (esterFragments) {
    const groups = [esterFragments.acidFrag, esterFragments.alcoholFrag];
    if (groups.every(ids => Array.isArray(ids) && ids.length &&
        ids.every(i => Number.isInteger(i) && i >= 0 && i < n && types[i] === 'C'))) {
      const mean = ids => ids.reduce((sum,i) => sum +
        points[i][0]*Math.cos(angle)-points[i][1]*Math.sin(angle),0)/ids.length;
      if (mean(groups[0]) > mean(groups[1]) + 1e-6) angle=wrap(angle+Math.PI);
    }
  }
  turn(all,[0,0],angle);
  // Center coordinates of the complete molecule, not just its parent. The
  // final SVG fit separately includes the actual rendered labels and strokes.
  const cx=(Math.min(...points.map(p=>p[0]))+Math.max(...points.map(p=>p[0])))/2;
  const cy=(Math.min(...points.map(p=>p[1]))+Math.max(...points.map(p=>p[1])))/2;
  for (let i=0; i<n; i++) {
    const x=(points[i][0]-cx).toFixed(4), y=(points[i][1]-cy).toFixed(4);
    if (x.length > 10 || y.length > 10) return unchanged;
    lines[start+i]=x.padStart(10)+y.padStart(10)+lines[start+i].slice(20);
  }
  return {mol:lines.join('\n'), rotation:angle*180/Math.PI, repairs, skipped,
    parentHeightBefore:before.height, parentHeightAfter:parent.length ? bounds(parent,0).height : 0};
}
// END SKELETAL GEOMETRY

function fApplySkeletalLayout() {
  if (mode2D !== 'skeletal' || !skeletalLayoutSource ||
      skeletalLayoutSource.key !== selectedMol ||
      (skeletalLayoutSource.draft || null) !== (window.MulerDraft || null)) return;
  const key=mainChainAtomsList.join(',');
  if (skeletalLayoutApplied === key) return;
  const fragments = fIsSingleEster() &&
    fIsAcyclicSaturatedMonoesterGraph(atomConnectivityList,allAtomsTypeList,bondList)
      ? esterInfo : null;
  const layout=fSkeletalLayoutMol(skeletalLayoutSource.mol,mainChainAtomsList,fragments);
  myMol2D=layout.mol;
  jsmeNomeclatureApplet.readMolFile(myMol2D);
  jsmeNomeclatureApplet.setMolecularAreaScale(molZoom2D);
  if (jsmeNomeclatureAppletORGNL) {
    jsmeNomeclatureAppletORGNL.readMolFile(myMol2D);
    jsmeNomeclatureAppletORGNL.setMolecularAreaScale(molZoom2D);
  }
  skeletalLayoutApplied=key;
}

// School expanded form: terminal formyl H left of C for the requested ester.
// Start from the saved string each load; only this H's transient XY changes.
function fFormylHydrogenLeftMol(mol) {
  if (selectedMol !== 'tert_butyl_methanoate' || typeof mol !== 'string') return mol;
  const lines=mol.split('\n'), n=Number((lines[3] || '').slice(0,3));
  const nb=Number((lines[3] || '').slice(3,6));
  if (!(lines[3] || '').includes('V2000') || !(n > 0) || !(nb > 0)) return mol;
  const atoms=lines.slice(4,4+n).map(l => ({x:Number(l.slice(0,10)),
    y:Number(l.slice(10,20)), type:l.slice(31,34).trim()}));
  const bonds=lines.slice(4+n,4+n+nb).map(l =>
    [Number(l.slice(0,3))-1,Number(l.slice(3,6))-1,Number(l.slice(6,9))]);
  for (const [a,b,order] of bonds) {
    if (order !== 2 || !atoms[a] || !atoms[b]) continue;
    const carbon=atoms[a].type === 'C' && atoms[b].type === 'O' ? a :
      atoms[b].type === 'C' && atoms[a].type === 'O' ? b : -1;
    if (carbon < 0) continue;
    const hs=bonds.filter(e => e[2] === 1 && (e[0] === carbon || e[1] === carbon))
      .map(e => e[0] === carbon ? e[1] : e[0]).filter(i => atoms[i]?.type === 'H');
    if (hs.length !== 1) return mol;
    const h=hs[0], c=atoms[carbon], length=Math.hypot(atoms[h].x-c.x,atoms[h].y-c.y);
    if (!(length > 0) || !Number.isFinite(length)) return mol;
    const x=(c.x-length).toFixed(4), y=c.y.toFixed(4);
    if (x.length > 10 || y.length > 10) return mol;
    lines[4+h]=x.padStart(10)+y.padStart(10)+lines[4+h].slice(20);
    return lines.join('\n');
  }
  return mol;
}

function fLoadMol2D() {
  skeletalLayoutSource = null;
  skeletalLayoutApplied = null;
  const selectedExample = nameExamples[selectedMol];
  if (!selectedExample) {
    myMol2D = null;
    jsmeNomeclatureApplet.clear();
    if (jsmeNomeclatureAppletORGNL) jsmeNomeclatureAppletORGNL.clear();
    return;
  }

  // Fall back to the first available representation if the requested
  // mode has no data (condensed > expanded > skeletal). Keeps globals
  // and radios in sync with what is actually loaded.
  const modeHasData =
    mode2D === "condensed"
      ? !!selectedExample.structure2D_Condensed
      : mode2D === "expanded"
        ? !!selectedExample.structure2D_Expanded
        : !!selectedExample.structure2D_Skeletal;
  if (!modeHasData) {
    if (selectedExample.structure2D_Condensed) {
      mode2D = "condensed";
      modeSuffix = "_2D_Condensed";
    } else if (selectedExample.structure2D_Expanded) {
      mode2D = "expanded";
      modeSuffix = "_2D_Expanded";
    } else if (selectedExample.structure2D_Skeletal) {
      mode2D = "skeletal";
      modeSuffix = "_2D_Skeletal";
    }
    const fallbackIdx =
      mode2D === "expanded" ? 1 : mode2D === "condensed" ? 0 : 2;
    $("#radio2DMode .radioCheckContainer")
      .removeClass("selectedRadio")
      .addClass("unselectedRadio");
    $("#radio2DMode .radioCheckContainer")
      .eq(fallbackIdx)
      .removeClass("unselectedRadio")
      .addClass("selectedRadio");
  }

  let rawMol2D;

  switch (mode2D) {
    case "condensed":
      rawMol2D = selectedExample.structure2D_Condensed;
      myMol2D = fMakeAnnotatedSkeletal(selectedExample.structure2D_Condensed);
      break;
    case "expanded":
      rawMol2D = fFormylHydrogenLeftMol(selectedExample.structure2D_Expanded);
      myMol2D = fMakeAnnotatedSkeletal(rawMol2D);
      break;
    case "skeletal":
      rawMol2D = selectedExample.structure2D_Skeletal;
      myMol2D = selectedExample.structure2D_Skeletal;
      break;
    case "condensedZigZag":
      rawMol2D = selectedExample.structure2D_Skeletal;
      myMol2D = fMakeAnnotatedSkeletal(selectedExample.structure2D_Skeletal);
      break;
    default:
      rawMol2D = selectedExample.structure2D_Condensed;
      myMol2D = selectedExample.structure2D_Condensed;
  }

  if (!myMol2D) {
    jsmeNomeclatureApplet.clear();
    if (jsmeNomeclatureAppletORGNL) jsmeNomeclatureAppletORGNL.clear();
    myMol2D = null;
    fUpdateSVG();
    return;
  }

  if (mode2D === "skeletal" && myMol2D) {
    skeletalLayoutSource = {key: selectedMol, mol: myMol2D};
  }
  jsmeNomeclatureApplet.readMolFile(myMol2D);
  try { fApplyMol2DFont(); } catch (eFo) {}
  try { fApplyMol2DScale(); } catch (eSc) {
    try { jsmeNomeclatureApplet.setMolecularAreaScale(molZoom2D); } catch (eS2) {}
  }
  if (jsmeNomeclatureAppletORGNL && rawMol2D) {
    jsmeNomeclatureAppletORGNL.readMolFile(rawMol2D);
    jsmeNomeclatureAppletORGNL.setMolecularAreaScale(molZoom2D);
  }

  try {
    fAnalyseStructure();
    fDetectMolType();
    nameExamples[selectedMol].classification = fGetMoleculeClassification();
  } catch (eAn) {
    try { /* console.error("[COLD-BOOT] analysis failed for " + selectedMol + " — naming cleared, not guessed", eAn); */ } catch (eL) { /* console unavailable */ }
    try { nameComponentsList = []; currentMolName = ""; } catch (eC) { /* best-effort */ }
  }
  try {
    fGuessName();
  } catch (eGn) {
    try { /* console.error("[COLD-BOOT] fGuessName failed for " + selectedMol + " — naming cleared, not guessed", eGn); */ } catch (eL2) { /* console unavailable */ }
    try { nameComponentsList = []; currentMolName = ""; } catch (eC2) { /* best-effort */ }
  }
  try {
    fUpdateSVG();
  } catch (eSvg) {
    try { /* console.error("[COLD-BOOT] fUpdateSVG failed for " + selectedMol + " — overlay skipped, naming continues", eSvg); */ } catch (eL3) { /* console unavailable */ }
  }
  // Fresh pools were just built by fCalcMainChain — refresh the stepper UI.
  try { if (typeof fRenderChainStepper === "function") fRenderChainStepper(); } catch (eStep) { /* stepper unavailable */ }
}

// ── fReapplyZoomScale2D ─────────────────────────────────────────────────────
// Per-mode C–C pixel equalizer: JSME rescales each loaded MOL by whole-input
// bond statistics, so expanded (heavy + short H) renders bigger C–C than
// condensed from identical stored skeletons. The inverse is exact:
// factor = meanAllBonds/meanHeavyBonds of the loaded MOL (1.0 when
// heavy-only); effective scale = molZoom2D * factor. Derived live from
// myMol2D at every scale application — nothing stored, user zoom stays in
// molZoom2D, mode switches recompute via fLoadMol2D below.
function fMol2DModeScaleFactor() {
  try {
    if (typeof fParseMolV2000 !== "function" || typeof myMol2D === "undefined" || !myMol2D) return 1;
    var p = fParseMolV2000(myMol2D);
    if (!p || !p.atoms || !p.atoms.length || !p.bonds || !p.bonds.length) return 1;
    var sAll = 0, nAll = 0, sHv = 0, nHv = 0;
    for (var i = 0; i < p.bonds.length; i++) {
      var b = p.bonds[i];
      if (!b || b[0] == null || b[1] == null) continue;
      var a = p.atoms[b[0] - 1], c = p.atoms[b[1] - 1];
      if (!a || !c) continue;
      var d = Math.hypot(a.x - c.x, a.y - c.y);
      if (!(d > 1e-9) || !isFinite(d)) continue;
      var ah = a.el === "H" || a.el === "h", ch = c.el === "H" || c.el === "h";
      sAll += d; nAll++;
      if (!ah && !ch) { sHv += d; nHv++; }
    }
    if (!nAll || !nHv) return 1;
    var f = (sAll / nAll) / (sHv / nHv);
    if (!(f > 0) || !isFinite(f)) return 1;
    if (f < 0.3) return 0.3;
    if (f > 6) return 6;
    return f;
  } catch (e) { return 1; }
}
function fMol2DModeScale() {
  var z = 2.0;
  try { z = (typeof molZoom2D !== "undefined") ? molZoom2D : 2.0; } catch (eZ) {}
  try { return z * fMol2DModeScaleFactor(); } catch (eF) { return z; }
}
// Expanded-only label compensation, split out so fLoadMol2D can set the font
// BEFORE readMolFile (first paint already correct) while fApplyMol2DScale
// re-asserts it after every scale write. Idempotent; other modes reset to base.
// Owner-tuned 2D label sizes (MOL px at boot scale): base default, hard clamp.
var MOL2D_FONT_BASE = 9, MOL2D_FONT_MIN = 7, MOL2D_FONT_MAX = 20;
function fApplyMol2DFont() {
  try {
    if (typeof jsmeNomeclatureApplet === "undefined" || !jsmeNomeclatureApplet) return;
    var _f = 1, _m = "condensed";
    try { _f = fMol2DModeScaleFactor(); } catch (eF2) { _f = 1; }
    try { _m = (typeof mode2D !== "undefined") ? mode2D : "condensed"; } catch (eM2) { _m = "condensed"; }
    var _fs = (_m === "expanded" && _f !== 1) ? (MOL2D_FONT_BASE / _f) : MOL2D_FONT_BASE;
    if (!(_fs > 0) || !isFinite(_fs)) _fs = MOL2D_FONT_BASE;
    if (_fs < MOL2D_FONT_MIN) _fs = MOL2D_FONT_MIN;
    if (_fs > MOL2D_FONT_MAX) _fs = MOL2D_FONT_MAX;
    if (typeof jsmeNomeclatureApplet.setAtomMolecularAreaFontSize === "function") {
      jsmeNomeclatureApplet.setAtomMolecularAreaFontSize(_fs);
    }
  } catch (eFs) { /* font compensation best-effort */ }
}
function fApplyMol2DScale() {
  try {
    if (typeof jsmeNomeclatureApplet !== "undefined" && jsmeNomeclatureApplet) {
      jsmeNomeclatureApplet.setMolecularAreaScale(fMol2DModeScale());
      // Expanded-only label compensation: the equalizer scales the view down
      // (factor < 1), which shrinks atom labels with it. Counter-scale the
      // label font so expanded labels render at condensed pixel size
      // (9 = boot value, set once in jsmeOnLoad). Other modes recompute
      // factor 1.0 and reset to 9 here — no per-mode state, no leaks.
      try { fApplyMol2DFont(); } catch (eF3) {}
    }
  } catch (e) { /* applet unavailable */ }
}
// Re-applies the live absolute zoom scale on both applets, then rebuilds the
// SVG overlay + replays numbering. Split out of fZoom2D so resizes can force
// the same re-fit: setSize alone resizes the box but leaves a stale small
// depiction (fixed by any zoom press) — re-applying the scale re-fits it.
// Highlight-safe (JSME background state survives scale changes: the zoom
// buttons prove it daily). No value change, no narration.
function fReapplyZoomScale2D() {
  if (!jsmeNomeclatureApplet) return;
  try {
    fApplyMol2DScale();
    if (jsmeNomeclatureAppletORGNL) jsmeNomeclatureAppletORGNL.setMolecularAreaScale(molZoom2D);
  } catch (e) {
    /* applet unavailable */
  }
  fUpdateSVG();
  if (numberingFlag) {
    currNumberEl = 0;
    fShowNumbering(0);
  }
}

// ── fZoom2D ─────────────────────────────────────────────────────────────────
// Zoom in (dir > 0) / out (dir < 0) the 2D molecule view by one ×1.25 step,
// clamped to 0.5–6.0. Scale is applet state: re-render the SVG afterwards and
// replay numbering overlays (DOM-side, wiped by the rebuild) like the color
// toggle does. Highlights are JSME background state and survive.
function fZoom2D(dir) {
  if (!jsmeNomeclatureApplet) return;
  var next = molZoom2D * (dir > 0 ? 1.25 : 1 / 1.25);
  next = Math.min(MOL_ZOOM_MAX, Math.max(MOL_ZOOM_MIN, next));
  if (next === molZoom2D) return;
  molZoom2D = next;
  fReapplyZoomScale2D();
}

// ── fZoom3D ─────────────────────────────────────────────────────────────────
// Zoom in (dir > 0) / out (dir < 0) the 3D molecule view. Live-only aid:
// zoom is JSmol-side state (numbering echoes and selections survive), JSmol
// `load` resets the framing on every molecule switch, and per-step cameras
// remain moveto's job (capture/apply follow-up pending elsewhere).
function fZoom3D(dir) {
  try {
    if (typeof Jmol !== "undefined" && typeof jmolAppletNomeclature !== "undefined") {
      fJSmolScript(jmolAppletNomeclature, dir > 0 ? "quit;zoomTo IN;" : "quit; zoomTo OUT;");
    }
  } catch (e) {
    /* JSmol unavailable */
  }
}

// ── fAddHydrogens2SVG ─────────────────────────────────────────────────────

function fRemainingImplicitCarbonHydrogens(atomIdx) {
  const explicit=bondList.filter(([a,b,order]) => order === 1 &&
    ((a-1 === atomIdx && allAtomsTypeList[b-1] === 'H') ||
     (b-1 === atomIdx && allAtomsTypeList[a-1] === 'H'))).length;
  const remaining=carbonHydrogens[atomIdx]-explicit;
  if (!Number.isInteger(remaining) || remaining < 0 || remaining > 4) {
    console.warn('Invalid display hydrogen count', selectedMol, atomIdx, remaining);
    return null;
  }
  return remaining;
}

function fAddHydrogens2SVG() {
  let tmpTexts, tmpRects, tmpBonds;
  let currText, currElement, currID, currHydrogensCount;
  let myLabel, myNo, currString, newString, newStringElement;
  molSvg = MuSVG("#jsmeNomeclatureSVG svg");

  tmpTexts = molSvg.selectAll("text");
  tmpRects = molSvg.selectAll("rect");
  tmpBonds = molSvg.selectAll("line");

  for (let i = 0; i < tmpTexts.length; i++) {
    currText = tmpTexts[i].attr("text");
    currElement = molSvg.select("text:nth-of-type(" + (i + 1) + ")");

    if (currText === "C") {
      currID = currText + (i + 1);

      currHydrogensCount = fRemainingImplicitCarbonHydrogens(i);
      if (currHydrogensCount === null) continue;
      switch (currHydrogensCount) {
        case 0:
          myLabel = "C";
          myNo = "";
          break;
        case 1:
          myLabel = "CH";
          myNo = "";
          break;
        case 4:
          myLabel = "CH";
          myNo = 4;
          break;
        default:
          myLabel = "CH";
          myNo = currHydrogensCount;
      }

      currString = tmpTexts[i].toString();
      const hydrogenTspan =
        myLabel === "CH"
          ? `<tspan class="svgHydrogenPart">H${myNo !== "" ? `<tspan dy="70" font-size=".8em">${myNo}</tspan>` : ""}</tspan>`
          : "";
      newString = currString.replace(
        [">C</text>"],
        `class="svgAtomLabel" id="${currID}"><tspan>C</tspan>${hydrogenTspan}</text>`,
      );
      newStringElement = MuSVG.parse(newString);
      if (!newStringElement) continue;
      tmpTexts[i].remove();
      molSvg.select("g").append(newStringElement);
      // Keep C at its original JSME anchor. Only the real label and a small
      // uniform clearance may mask a bond; CHn must not shift the carbon.
      const label = molSvg.select("#" + currID);
      const owner = tmpTexts[i].node.getAttribute("data-namelecule-atom");
      const backplate = owner ? molSvg.select(`rect[data-namelecule-atom="${owner}"][data-namelecule-role="backplate"]`) : tmpRects[i + 1];
      if (label && backplate) {
        if (selectedMol === 'tert_butyl_methanoate' && fIsSingleEster() &&
            i === esterInfo.carbonylC && currHydrogensCount === 1) {
          // H precedes C, while C keeps the native atom anchor.
          const carbon=label.node.firstElementChild, hydrogen=carbon?.nextElementSibling;
          if (carbon && hydrogen) {
            const x=Number(label.attr('x'));
            const pad=parseFloat(label.attr('font-size'))*.06;
            hydrogen.setAttribute('x',x-hydrogen.getComputedTextLength()-pad);
            carbon.setAttribute('x',x);
            label.node.insertBefore(hydrogen,carbon);
          }
        }
        const bounds = label.node.getBBox();
        const fontSize = parseFloat(label.attr("font-size"));
        const padding = Number.isFinite(fontSize) && fontSize > 0 ? fontSize * 0.06 : 20;
        // In acid condensed drawings a vertical bond below C must not stop
        // at the lower edge of the adjacent H subscript's rectangular mask.
        const carbon = label.node.firstElementChild;
        if (mode2D === "condensed" && functionalGroupObj && functionalGroupObj.carboxylicAcid && carbon &&
            (atomConnectivityList[i] || []).some(nb =>
              allAtomsTypeList[nb] === "C" && tmpTexts[nb] &&
              Math.abs(parseFloat(tmpTexts[nb].attr("x")) - parseFloat(label.attr("x"))) < 0.01 &&
              parseFloat(tmpTexts[nb].attr("y")) > parseFloat(label.attr("y")) + 0.01)) {
          const carbonBounds = carbon.getBBox();
          bounds.height = carbonBounds.y + carbonBounds.height - bounds.y;
        }
        if ([bounds.x, bounds.y, bounds.width, bounds.height].every(Number.isFinite) &&
            bounds.width > 0 && bounds.height > 0) {
          backplate.attr({
            x: bounds.x - padding, y: bounds.y - padding,
            width: bounds.width + 2 * padding, height: bounds.height + 2 * padding
          });
        }
      }
    } else {
      currString = tmpTexts[i].toString();
      newStringElement = MuSVG.parse(currString);
      if (!newStringElement) continue;
      tmpTexts[i].remove();
      molSvg.select("g").append(newStringElement);
    }
  }
}

function fGetCompactedAtomSkipSet(includeCompactedAtoms = false) {
  const skipIndices = new Set();
  if (includeCompactedAtoms || mode2D !== "condensed" || !functionalGroupObj) {
    return skipIndices;
  }

  if (functionalGroupObj.hasOwnProperty("carboxylicAcid")) {
    const acidEntries = functionalGroupObj.carboxylicAcid.O || [];
    for (let i = 0; i < acidEntries.length; i++) {
      const entry = acidEntries[i];
      if (!Array.isArray(entry) || entry.length < 2) {
        continue;
      }
      skipIndices.add(entry[0]);
      skipIndices.add(entry[1]);
    }
  }
  if (functionalGroupObj.hasOwnProperty("aldehyde")) {
    const aldehydeEntries = functionalGroupObj.aldehyde.O || [];
    for (let i = 0; i < aldehydeEntries.length; i++) {
      const carbon = (atomConnectivityList[aldehydeEntries[i]] || [])[0];
      const ns = atomConnectivityList[carbon] || [];
      const methanal = ns.length === 1 && atomValenceList[carbon] === 2 && allAtomsTypeList[ns[0]] === "O";
      if (!methanal && !ns.some(n => allAtomsTypeList[n] === "C")) continue;
      skipIndices.add(aldehydeEntries[i]);
    }
  }
  if (functionalGroupObj.hasOwnProperty("cyanide")) {
    const cyanideEntries = functionalGroupObj.cyanide.N || [];
    for (let i = 0; i < cyanideEntries.length; i++) {
      skipIndices.add(cyanideEntries[i]);
    }
  }
  if (functionalGroupObj.hasOwnProperty("nitro")) {
    const nitroEntries = functionalGroupObj.nitro.N || [];
    for (let i = 0; i < nitroEntries.length; i++) {
      const nitrogenIdx = nitroEntries[i];
      if (!Array.isArray(atomConnectivityList[nitrogenIdx])) {
        continue;
      }
      for (let n = 0; n < atomConnectivityList[nitrogenIdx].length; n++) {
        const neighborIdx = atomConnectivityList[nitrogenIdx][n];
        if (allAtomsTypeList[neighborIdx] === "O") {
          skipIndices.add(neighborIdx);
        }
      }
    }
  }

  return skipIndices;
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

function fGetRenderedAtomRectMap(
  includeCompactedAtoms = false,
  includeHydrogens = false,
) {
  const atomRectMap = {};
  // The native producer supplies actual atom IDs, even when skeletal C is omitted.
  const owned = molSvg.selectAll('rect[data-namelecule-atom][data-namelecule-role="backplate"]');
  if (owned.length) {
    owned.forEach(el => {
      const index = Number(el.node.getAttribute('data-namelecule-atom')) - 1;
      if (Number.isInteger(index) && index >= 0 &&
          (includeHydrogens || allAtomsTypeList[index] !== 'H')) atomRectMap[index] = el;
    });
    return atomRectMap;
  }
  const rectEls = molSvg.selectAll("rect");
  const skipIndices = fGetCompactedAtomSkipSet(includeCompactedAtoms);
  let rectIdx = 1;

  for (let atomIdx = 0; atomIdx < allAtomsTypeList.length; atomIdx++) {
    if (allAtomsTypeList[atomIdx] === "H" && !includeHydrogens) {
      continue;
    }
    if (skipIndices.has(atomIdx)) {
      continue;
    }
    if (rectIdx >= rectEls.length) {
      break;
    }
    atomRectMap[atomIdx] = rectEls[rectIdx];
    rectIdx += 1;
  }

  return atomRectMap;
}

function fGetAttachedHydrogenIndices(atomIdx) {
  const hydrogenIndices = [];
  if (!Array.isArray(atomConnectivityList[atomIdx])) {
    return hydrogenIndices;
  }
  for (let i = 0; i < atomConnectivityList[atomIdx].length; i++) {
    const neighborIdx = atomConnectivityList[atomIdx][i];
    if (allAtomsTypeList[neighborIdx] === "H") {
      hydrogenIndices.push(neighborIdx);
    }
  }
  return hydrogenIndices;
}

function fFindBondIndexByAtoms(atomIdxA, atomIdxB) {
  const atomA = atomIdxA + 1;
  const atomB = atomIdxB + 1;
  for (let bondIdx = 0; bondIdx < bondList.length; bondIdx++) {
    if (!bondList[bondIdx]) {
      continue;
    }
    const bondAtom1 = bondList[bondIdx][0];
    const bondAtom2 = bondList[bondIdx][1];
    if (
      (bondAtom1 === atomA && bondAtom2 === atomB) ||
      (bondAtom1 === atomB && bondAtom2 === atomA)
    ) {
      return bondIdx;
    }
  }
  return -1;
}

function fRemoveBondLinesByBondIndex(bondIdx, lineEls) {
  if (bondIdx < 0 || !bondList[bondIdx]) {
    return;
  }
  const lineStart = svgBondList[bondIdx];
  const lineCount = bondList[bondIdx][2];
  for (let offset = 0; offset < lineCount; offset++) {
    const lineEl = lineEls[lineStart + offset - 1];
    if (lineEl) {
      lineEl.remove();
    }
  }
}

function fBuildTextAttrsFromElement(el) {
  let attrs = "";
  const attrNames = [
    "x",
    "y",
    "font-size",
    "font-family",
    "font-weight",
    "font-style",
    "data-namelecule-atom",
    "data-namelecule-role",
    "text-anchor",
    "fill",
    "stroke",
    "stroke-width",
    "class",
    "id",
  ];
  for (let i = 0; i < attrNames.length; i++) {
    const attrName = attrNames[i];
    const attrValue = el.node.getAttribute(attrName);
    if (attrValue) {
      attrs += " " + attrName + '="' + attrValue + '"';
    }
  }
  return attrs;
}

function fReplaceTextElementMarkup(el, markup, attrOverrides) {
  if (!el) {
    return null;
  }
  const x = el.node.getAttribute("x");
  const y = el.node.getAttribute("y");
  if (!x || !y) {
    return null;
  }
  let attrs = fBuildTextAttrsFromElement(el);
  if (attrOverrides) {
    for (const attrName in attrOverrides) {
      attrs = attrs.replace(new RegExp(" " + attrName + '="[^"]*"', "g"), "");
      attrs += " " + attrName + '="' + attrOverrides[attrName] + '"';
    }
  }
  const newString = `<text${attrs}>${markup}</text>`;
  let newEl;
  try {
    newEl = MuSVG.parse(newString);
  } catch (e) {
    return null;
  }
  const parentNode = el.node.parentNode;
  if (!parentNode || !newEl || !newEl.node) {
    return null;
  }

  const nextSibling = el.node.nextSibling;
  const fragmentNode = newEl.node;
  let insertedNode = null;

  while (fragmentNode.firstChild) {
    const childNode = fragmentNode.firstChild;
    parentNode.insertBefore(childNode, nextSibling);
    if (!insertedNode && childNode.nodeType === 1) {
      insertedNode = childNode;
    }
  }

  el.remove();
  return insertedNode ? MuSVG(insertedNode) : null;
}

function fShouldReverseCompactLabel(anchorEl, attachedEls) {
  if (!anchorEl || !attachedEls || attachedEls.length === 0) {
    return false;
  }
  const anchorX = parseFloat(anchorEl.node.getAttribute("x"));
  if (isNaN(anchorX)) {
    return false;
  }

  let attachedXSum = 0;
  let attachedCount = 0;
  for (let i = 0; i < attachedEls.length; i++) {
    if (!attachedEls[i]) {
      continue;
    }
    const attachedX = parseFloat(attachedEls[i].node.getAttribute("x"));
    if (isNaN(attachedX)) {
      continue;
    }
    attachedXSum += attachedX;
    attachedCount += 1;
  }
  if (attachedCount === 0) {
    return false;
  }

  return attachedXSum / attachedCount < anchorX;
}

function fGetReversedCompactLabelAttrs(anchorEl, labelKey) {
  if (!anchorEl) {
    return { "text-anchor": "end" };
  }
  const anchorX = parseFloat(anchorEl.node.getAttribute("x"));
  const fontSize = parseFloat(anchorEl.node.getAttribute("font-size"));
  const hasCustomScale = Object.prototype.hasOwnProperty.call(
    compactReverseOffsetScale,
    labelKey,
  );
  const offsetScale = hasCustomScale
    ? compactReverseOffsetScale[labelKey]
    : 0.8;
  const xShift = isNaN(fontSize) ? 120 : fontSize * offsetScale;
  if (isNaN(anchorX)) {
    return { "text-anchor": "end" };
  }
  return {
    "text-anchor": "end",
    x: String(anchorX + xShift),
  };
}

function fGetForwardCompactLabelAttrs(anchorEl, labelKey) {
  if (!anchorEl) {
    return null;
  }
  const anchorX = parseFloat(anchorEl.node.getAttribute("x"));
  const fontSize = parseFloat(anchorEl.node.getAttribute("font-size"));
  const hasCustomScale = Object.prototype.hasOwnProperty.call(
    compactForwardOffsetScale,
    labelKey,
  );
  if (!hasCustomScale || isNaN(anchorX)) {
    return null;
  }
  const offsetScale = compactForwardOffsetScale[labelKey];
  const xShift = isNaN(fontSize) ? 80 : fontSize * offsetScale;
  return {
    x: String(anchorX - xShift),
  };
}

function fGetReverseCompactRightEdge(anchorEl, labelKey, geometryHint) {
  const anchorX =
    geometryHint && typeof geometryHint.x === "number"
      ? geometryHint.x
      : parseFloat(
          anchorEl && anchorEl.node ? anchorEl.node.getAttribute("x") : NaN,
        );
  const fontSize = parseFloat(
    anchorEl && anchorEl.node ? anchorEl.node.getAttribute("font-size") : NaN,
  );
  if (isNaN(anchorX)) {
    return NaN;
  }

  const hasCustomScale = Object.prototype.hasOwnProperty.call(
    compactReverseOffsetScale,
    labelKey,
  );
  const offsetScale = hasCustomScale
    ? compactReverseOffsetScale[labelKey]
    : 0.8;
  const xShift = isNaN(fontSize) ? 120 : fontSize * offsetScale;
  return anchorX + xShift;
}

function fFindNearestHighlightCircle(anchorEl, geometryHint) {
  const anchorX =
    geometryHint && typeof geometryHint.x === "number"
      ? geometryHint.x
      : parseFloat(
          anchorEl && anchorEl.node ? anchorEl.node.getAttribute("x") : NaN,
        );
  const anchorY =
    geometryHint && typeof geometryHint.y === "number"
      ? geometryHint.y
      : parseFloat(
          anchorEl && anchorEl.node ? anchorEl.node.getAttribute("y") : NaN,
        );
  if (isNaN(anchorX) || isNaN(anchorY)) {
    return null;
  }

  const circleEls = molSvg.selectAll("circle");
  let nearestCircle = null;
  let nearestDistSq = Infinity;
  for (let i = 0; i < circleEls.length; i++) {
    const circleEl = circleEls[i];
    const cx = parseFloat(circleEl.attr("cx"));
    const cy = parseFloat(circleEl.attr("cy"));
    if (isNaN(cx) || isNaN(cy)) {
      continue;
    }
    const dx = cx - anchorX;
    const dy = cy - anchorY;
    const distSq = dx * dx + dy * dy;
    if (distSq < nearestDistSq) {
      nearestDistSq = distSq;
      nearestCircle = circleEl;
    }
  }
  return nearestCircle;
}

function fGetNodeAttr(el, attrName) {
  if (!el || !el.node || !attrName) {
    return "";
  }
  return el.node.getAttribute(attrName) || "";
}

function fBuildCompactGeometryHint(anchorEl, anchorRectEl) {
  const anchorX = parseFloat(
    anchorEl && anchorEl.node ? anchorEl.node.getAttribute("x") : NaN,
  );
  const anchorY = parseFloat(
    anchorEl && anchorEl.node ? anchorEl.node.getAttribute("y") : NaN,
  );
  const hint = {
    x: anchorX,
    y: anchorY,
    fill: fGetNodeAttr(anchorEl, "fill"),
  };

  const rectX = parseFloat(
    anchorRectEl && anchorRectEl.node ? anchorRectEl.attr("x") : NaN,
  );
  const rectWidth = parseFloat(
    anchorRectEl && anchorRectEl.node ? anchorRectEl.attr("width") : NaN,
  );
  if (!isNaN(rectX) && !isNaN(rectWidth)) {
    hint.rightEdge = rectX + rectWidth;
    hint.leftEdge = rectX;
  }

  const nearestCircle = fFindNearestHighlightCircle(anchorEl, hint);
  if (nearestCircle) {
    const circleX = parseFloat(nearestCircle.attr("cx"));
    const circleRadius = parseFloat(nearestCircle.attr("r"));
    if (!isNaN(circleX) && !isNaN(circleRadius)) {
      hint.circleRightEdge = circleX + circleRadius;
      hint.circleLeftEdge = circleX - circleRadius;
    }
  }

  return hint;
}

function fCreateCompactLabelRect(anchorEl, geometryHint) {
  if (!anchorEl || !anchorEl.node || !anchorEl.node.parentNode) {
    return null;
  }

  let rectX = NaN;
  let rectY = NaN;
  let rectWidth = NaN;
  let rectHeight = NaN;
  let fill = "";
  let stroke = "";
  let strokeWidth = "";

  const nearestCircle = fFindNearestHighlightCircle(anchorEl, geometryHint);
  if (nearestCircle) {
    const cx = parseFloat(nearestCircle.attr("cx"));
    const cy = parseFloat(nearestCircle.attr("cy"));
    const r = parseFloat(nearestCircle.attr("r"));
    if (!isNaN(cx) && !isNaN(cy) && !isNaN(r)) {
      rectX = cx - r;
      rectY = cy - r;
      rectWidth = r * 2;
      rectHeight = r * 2;
      fill = fGetNodeAttr(nearestCircle, "fill");
      stroke = fGetNodeAttr(nearestCircle, "stroke");
      strokeWidth = fGetNodeAttr(nearestCircle, "stroke-width");
    }
  }

  if (isNaN(rectX) || isNaN(rectY) || isNaN(rectWidth) || isNaN(rectHeight)) {
    if (!anchorEl.node.getBBox) {
      return null;
    }
    let textBBox;
    try {
      textBBox = anchorEl.node.getBBox();
    } catch (e) {
      return null;
    }
    const hintX =
      geometryHint && typeof geometryHint.x === "number"
        ? geometryHint.x
        : null;
    const hintY =
      geometryHint && typeof geometryHint.y === "number"
        ? geometryHint.y
        : null;
    rectX =
      hintX !== null
        ? hintX - Math.max(textBBox.width + 160, 260) / 2
        : textBBox.x - 80;
    rectY =
      hintY !== null
        ? hintY - Math.max(textBBox.height + 120, 260) / 2
        : textBBox.y - 60;
    rectWidth = Math.max(textBBox.width + 160, 260);
    rectHeight = Math.max(textBBox.height + 120, 260);
    fill =
      (geometryHint && geometryHint.fill) ||
      fGetNodeAttr(anchorEl, "fill") ||
      "rgb(121,220,109)";
  }

  let rectMarkup =
    '<rect x="' +
    rectX +
    '" y="' +
    rectY +
    '" width="' +
    rectWidth +
    '" height="' +
    rectHeight +
    '"';
  if (fill) {
    rectMarkup += ' fill="' + fill + '"';
  }
  if (stroke) {
    rectMarkup += ' stroke="' + stroke + '"';
  }
  if (strokeWidth) {
    rectMarkup += ' stroke-width="' + strokeWidth + '"';
  }
  rectMarkup += "></rect>";

  let newRect;
  try {
    newRect = MuSVG.parse(rectMarkup);
  } catch (e) {
    return null;
  }

  const parentNode = anchorEl.node.parentNode;
  if (!newRect || !newRect.node || !parentNode) {
    return null;
  }
  let insertedNode = null;
  const fragmentNode = newRect.node;
  while (fragmentNode.firstChild) {
    const childNode = fragmentNode.firstChild;
    parentNode.insertBefore(childNode, anchorEl.node);
    if (!insertedNode && childNode.nodeType === 1) {
      insertedNode = childNode;
    }
  }

  return insertedNode ? MuSVG(insertedNode) : null;
}

function fResizeCompactLabelRect(
  rectEl,
  anchorEl,
  labelKey,
  reverseLabel,
  geometryHint,
) {
  if (!anchorEl) {
    return;
  }

  // Methanal may have no highlight geometry at all; never invent a filled
  // rectangle from its normal dark text colour merely to size HCHO.
  if (labelKey === "HCHO" && !rectEl && !fFindNearestHighlightCircle(anchorEl, geometryHint)) return;
  const workingRectEl =
    rectEl || fCreateCompactLabelRect(anchorEl, geometryHint);
  if (!workingRectEl) {
    return;
  }

  const rectX = parseFloat(workingRectEl.attr("x"));
  const rectWidth = parseFloat(workingRectEl.attr("width"));
  const fontSize = parseFloat(anchorEl.node.getAttribute("font-size"));
  if (isNaN(rectX) || isNaN(rectWidth)) {
    return;
  }

  const widthOverride = compactLabelWidths[labelKey];
  const labelLength = String(labelKey || "").length;
  const targetWidth =
    typeof widthOverride === "number"
      ? widthOverride
      : isNaN(fontSize)
        ? Math.max(rectWidth, 450 + labelLength * 120)
        : Math.max(rectWidth, fontSize * (labelLength * 0.9 + 0.35));

  const rectAttrs = { width: targetWidth };
  const widthDelta = targetWidth - rectWidth;
  const hasForwardScale = Object.prototype.hasOwnProperty.call(
    compactForwardOffsetScale,
    labelKey,
  );
  const forwardShift =
    hasForwardScale && !reverseLabel
      ? isNaN(fontSize)
        ? 80
        : fontSize * compactForwardOffsetScale[labelKey]
      : 0;
  const reverseTextRightEdge = reverseLabel
    ? fGetReverseCompactRightEdge(anchorEl, labelKey, geometryHint)
    : NaN;
  const circleRightEdge =
    geometryHint && typeof geometryHint.circleRightEdge === "number"
      ? geometryHint.circleRightEdge
      : NaN;
  const hintedRightEdge =
    geometryHint && typeof geometryHint.rightEdge === "number"
      ? geometryHint.rightEdge
      : NaN;
  const targetRightEdge =
    labelKey === "OHC" && !isNaN(circleRightEdge)
      ? circleRightEdge
      : !isNaN(reverseTextRightEdge)
        ? reverseTextRightEdge
        : !isNaN(circleRightEdge)
          ? circleRightEdge
          : hintedRightEdge;
  const rightEdgeAdjust = Object.prototype.hasOwnProperty.call(
    compactRectRightEdgeAdjust,
    labelKey,
  )
    ? compactRectRightEdgeAdjust[labelKey]
    : 0;
  const adjustedRightEdge = !isNaN(targetRightEdge)
    ? targetRightEdge + rightEdgeAdjust
    : targetRightEdge;
  if (typeof widthOverride === "number") {
    if (reverseLabel) {
      if (!isNaN(adjustedRightEdge)) {
        rectAttrs.x = adjustedRightEdge - targetWidth;
      } else {
        rectAttrs.x = rectX - widthDelta;
      }
    } else if (forwardShift > 0) {
      rectAttrs.x = rectX - forwardShift;
    }
  } else if (reverseLabel) {
    if (!isNaN(adjustedRightEdge)) {
      rectAttrs.x = adjustedRightEdge - targetWidth;
    } else {
      rectAttrs.x = rectX - widthDelta;
    }
  } else if (forwardShift > 0) {
    rectAttrs.x = rectX - forwardShift;
  }
  workingRectEl.attr(rectAttrs);
  return workingRectEl;
}

function fCollectHighlightRectsNearText(textEls) {
  // Ownership, never proximity: a neighboring CH3 must keep its own backplate.
  const owners = new Set(textEls.filter(Boolean).map(el =>
    el.node.getAttribute("data-namelecule-atom")).filter(Boolean));
  return molSvg.selectAll("rect[data-namelecule-atom]").filter(el =>
    owners.has(el.node.getAttribute("data-namelecule-atom")));
}

// Circle twin of the rect collector above: highlight circles (JSME renders
// atom highlights as circles where no label rect owns them) near removed
// texts are dropped by the compaction too. Fill-restricted to highlight
// colors (component green + selection cyan) so structural circles are never
// touched.
function fCollectHighlightCirclesNearText(textEls) {
  const collectedCircles = [];
  const seenCircles = new Set();
  const circleEls = molSvg.selectAll("circle");

  for (let i = 0; i < textEls.length; i++) {
    const textEl = textEls[i];
    if (!textEl || !textEl.node || !textEl.node.getBBox) {
      continue;
    }

    let textBBox;
    try {
      textBBox = textEl.node.getBBox();
    } catch (e) {
      continue;
    }

    const padX = Math.max(textBBox.width * 0.7, 160);
    const padY = Math.max(textBBox.height * 0.6, 120);
    const minX = textBBox.x - padX;
    const maxX = textBBox.x + textBBox.width + padX;
    const minY = textBBox.y - padY;
    const maxY = textBBox.y + textBBox.height + padY;

    for (let c = 0; c < circleEls.length; c++) {
      const circleEl = circleEls[c];
      if (!circleEl || !circleEl.node) {
        continue;
      }
      if (seenCircles.has(circleEl.node)) {
        continue;
      }

      const fillValue = String(circleEl.node.getAttribute("fill") || "").replace(/\s+/g, "").toLowerCase();
      const isHiglightFill =
        fMulerFillMatches("#79dc6d", fillValue) ||
        fMulerFillMatches((typeof MULER_SELECT_CYAN !== "undefined" ? MULER_SELECT_CYAN : "#22d3ee"), fillValue) ||
        fMulerFillMatches("#22d3ee", fillValue);
      if (!isHiglightFill) {
        continue;
      }

      const cx = parseFloat(circleEl.attr("cx"));
      const cy = parseFloat(circleEl.attr("cy"));
      const cr = parseFloat(circleEl.attr("r"));
      if (isNaN(cx) || isNaN(cy) || isNaN(cr)) {
        continue;
      }

      if (cx + cr >= minX && cx - cr <= maxX && cy + cr >= minY && cy - cr <= maxY) {
        seenCircles.add(circleEl.node);
        collectedCircles.push(circleEl);
      }
    }
  }

  return collectedCircles;
}

function fGetCompactLabelNumberX(textEl, labelKey, defaultOffsetX) {
  if (!textEl || !textEl.node || !labelKey || !textEl.node.getBBox) {
    return parseInt(textEl.attr("x")) + defaultOffsetX;
  }

  let textBBox;
  try {
    textBBox = textEl.node.getBBox();
  } catch (e) {
    return parseInt(textEl.attr("x")) + defaultOffsetX;
  }

  const labelText = String(labelKey);
  if (labelText.length === 0) {
    return parseInt(textEl.attr("x")) + defaultOffsetX;
  }

  let anchorCharIdx = labelText.indexOf("C");
  if (anchorCharIdx < 0) {
    anchorCharIdx = labelText.indexOf("N");
  }
  if (anchorCharIdx < 0) {
    return parseInt(textEl.attr("x")) + defaultOffsetX;
  }

  const anchorLeftX =
    textBBox.x + textBBox.width * (anchorCharIdx / labelText.length);
  return Math.round(anchorLeftX + defaultOffsetX);
}

function fBuildCompactAtomTspan(text, fillColor, className) {
  let tspan = `<tspan${fillColor ? ` fill="${fillColor}"` : ""}${className ? ` class="${className}"` : ""}>${text}</tspan>`;
  return tspan;
}

function fGetCompactAtomFill() {
  for (let i = 0; i < arguments.length; i++) {
    const fill = fGetNodeAttr(arguments[i], "fill");
    if (fill) {
      return fill;
    }
  }
  return "";
}

function fGetHydrogenGroupParentSymbol(atomIdx) {
  if (
    !Array.isArray(allAtomsTypeList) ||
    !Array.isArray(atomConnectivityList)
  ) {
    return "";
  }
  if (
    typeof atomIdx !== "number" ||
    atomIdx < 0 ||
    allAtomsTypeList[atomIdx] !== "H"
  ) {
    return "";
  }
  if (!Array.isArray(atomConnectivityList[atomIdx])) {
    return "";
  }

  for (let i = 0; i < atomConnectivityList[atomIdx].length; i++) {
    const neighborIdx = atomConnectivityList[atomIdx][i];
    const neighborSymbol = allAtomsTypeList[neighborIdx];
    if (neighborSymbol === "O" || neighborSymbol === "N") {
      return neighborSymbol;
    }
  }

  return "";
}

function fGetAtomColor2D(symbol, colorContext) {
  if (!symbol || !atomColors2D) {
    return "";
  }
  const baseFill = Object.prototype.hasOwnProperty.call(atomColors2D, symbol)
    ? atomColors2D[symbol]
    : "";
  if (!baseFill) {
    return "";
  }

  if (symbol !== "H" || atomColorMode2D !== "group") {
    return baseFill;
  }

  const parentSymbol =
    colorContext && colorContext.parentSymbol ? colorContext.parentSymbol : "";
  if (parentSymbol === "O" || parentSymbol === "N") {
    return atomColors2D[parentSymbol] || baseFill;
  }

  const atomIdx =
    colorContext && typeof colorContext.atomIdx === "number"
      ? colorContext.atomIdx
      : -1;
  const attachedParentSymbol = fGetHydrogenGroupParentSymbol(atomIdx);
  if (attachedParentSymbol === "O" || attachedParentSymbol === "N") {
    return atomColors2D[attachedParentSymbol] || baseFill;
  }

  return baseFill;
}

function fGetDisplayAtomFill(symbol) {
  let colorContext = null;
  let fallbackStartIdx = 1;
  if (
    arguments.length > 1 &&
    arguments[1] &&
    typeof arguments[1] === "object" &&
    (Object.prototype.hasOwnProperty.call(arguments[1], "parentSymbol") ||
      Object.prototype.hasOwnProperty.call(arguments[1], "atomIdx"))
  ) {
    colorContext = arguments[1];
    fallbackStartIdx = 2;
  }

  if (svgAtomColors2DFlag) {
    const mappedFill = fGetAtomColor2D(symbol, colorContext);
    if (mappedFill) {
      return mappedFill;
    }
  }

  const fallbackEls = [];
  for (let i = fallbackStartIdx; i < arguments.length; i++) {
    fallbackEls.push(arguments[i]);
  }

  return fGetCompactAtomFill.apply(null, fallbackEls);
}

function fGetOwnTextFromSvgNode(node) {
  if (!node || !node.childNodes) {
    return "";
  }
  let ownText = "";
  for (let i = 0; i < node.childNodes.length; i++) {
    const child = node.childNodes[i];
    if (child.nodeType === 3) {
      ownText += child.nodeValue || "";
    }
  }
  return ownText.trim();
}

function fResolveAtomSymbolFromLabelNode(node) {
  if (!node) {
    return "";
  }
  if (node.classList && node.classList.contains("svgHydrogenPart")) {
    return "H";
  }
  const rawText = fGetOwnTextFromSvgNode(node);
  if (!rawText) {
    return "";
  }
  const symbolMatch = rawText.match(/^([A-Z][a-z]?)/);
  if (!symbolMatch) {
    return "";
  }
  const symbol = symbolMatch[1];
  return Object.prototype.hasOwnProperty.call(atomColors2D, symbol)
    ? symbol
    : "";
}

function fResolveParentSymbolForHydrogenTspan(tspanNode, fallbackParentSymbol) {
  if (!tspanNode || !tspanNode.parentElement) {
    return fallbackParentSymbol && fallbackParentSymbol !== "H"
      ? fallbackParentSymbol
      : "";
  }

  const className = String(tspanNode.getAttribute("class") || "");
  if (className.indexOf("svgOxygenAttachedHydrogen") !== -1) {
    return "O";
  }
  if (className.indexOf("svgCarbonAttachedHydrogen") !== -1) {
    return "C";
  }

  const siblingSpans = [];
  for (let i = 0; i < tspanNode.parentElement.childNodes.length; i++) {
    const child = tspanNode.parentElement.childNodes[i];
    if (!child || child.nodeType !== 1) {
      continue;
    }
    if (String(child.nodeName).toLowerCase() !== "tspan") {
      continue;
    }
    siblingSpans.push(child);
  }

  for (let i = 0; i < siblingSpans.length; i++) {
    const sibling = siblingSpans[i];
    if (sibling === tspanNode) {
      continue;
    }
    const siblingSymbol = fResolveAtomSymbolFromLabelNode(sibling);
    if (siblingSymbol && siblingSymbol !== "H") {
      return siblingSymbol;
    }
  }

  return fallbackParentSymbol && fallbackParentSymbol !== "H"
    ? fallbackParentSymbol
    : "";
}

function fBuildTextNodeAtomIndexMap() {
  const textNodeAtomIndexMap = new Map();
  if (!molSvg || !Array.isArray(allAtomsTypeList) || mode2D === "condensed") {
    return textNodeAtomIndexMap;
  }

  const atomTextMap = fGetRenderedAtomTextMap(true, true);
  for (const atomIdxKey in atomTextMap) {
    const atomTextEl = atomTextMap[atomIdxKey];
    if (!atomTextEl || !atomTextEl.node) {
      continue;
    }
    textNodeAtomIndexMap.set(atomTextEl.node, parseInt(atomIdxKey, 10));
  }

  return textNodeAtomIndexMap;
}

function fIsHighlightFillColor(fillValue) {
  if (!fillValue || typeof fillValue !== "string") {
    return false;
  }
  const normalized = fillValue.replace(/\s+/g, "").toLowerCase();
  if (normalized.indexOf("d8eedc") !== -1 || normalized.indexOf("79dc6d") !== -1) {
    return true;
  }
  if (normalized.indexOf("216,238,220") !== -1 || normalized.indexOf("121,220,109") !== -1) {
    return true;
  }
  // Selection cyan gets the same black-label contrast as component green.
  try {
    if (typeof fMulerSelectIsSelectionFill === "function" && fMulerSelectIsSelectionFill(fillValue)) {
      return true;
    }
  } catch (eSel) {}
  try {
    if (typeof fMulerFillMatches === "function") {
      var _cyan = "#7ddfff";
      try { if (typeof MULER_SELECT_CYAN !== "undefined" && MULER_SELECT_CYAN) _cyan = MULER_SELECT_CYAN; } catch (eC) {}
      if (fMulerFillMatches(_cyan, fillValue)) {
        return true;
      }
      if (fMulerFillMatches("#7ddfff", fillValue)) {
        return true;
      }
      if (fMulerFillMatches("#22d3ee", fillValue)) {
        return true;
      }
    }
  } catch (eFill) {}
  if (normalized.indexOf("7ddfff") !== -1) {
    return true;
  }
  if (normalized.indexOf("22d3ee") !== -1) {
    return true;
  }
  if (normalized.indexOf("125,223,255") !== -1) {
    return true;
  }
  if (normalized.indexOf("34,211,238") !== -1) {
    return true;
  }
  return false;
}

function fBuildHighlightedTextNodeSet() {
  if (!molSvg) {
    return new Set();
  }

  const highlightedTextNodes = new Set();
  const highlightRects = [];
  const highlightCircles = [];

  const rectEls = molSvg.selectAll("rect");
  for (let i = 0; i < rectEls.length; i++) {
    const rectEl = rectEls[i];
    if (!rectEl || !rectEl.node) {
      continue;
    }
    const fillValue = String(rectEl.node.getAttribute("fill") || "");
    if (!fIsHighlightFillColor(fillValue)) {
      continue;
    }

    const x = parseFloat(rectEl.node.getAttribute("x"));
    const y = parseFloat(rectEl.node.getAttribute("y"));
    const width = parseFloat(rectEl.node.getAttribute("width"));
    const height = parseFloat(rectEl.node.getAttribute("height"));
    if (isNaN(x) || isNaN(y) || isNaN(width) || isNaN(height)) {
      continue;
    }
    highlightRects.push({ x: x, y: y, width: width, height: height });
  }

  const circleEls = molSvg.selectAll("circle");
  for (let i = 0; i < circleEls.length; i++) {
    const circleEl = circleEls[i];
    if (!circleEl || !circleEl.node) {
      continue;
    }
    const fillValue = String(circleEl.node.getAttribute("fill") || "");
    if (!fIsHighlightFillColor(fillValue)) {
      continue;
    }

    const cx = parseFloat(circleEl.node.getAttribute("cx"));
    const cy = parseFloat(circleEl.node.getAttribute("cy"));
    const r = parseFloat(circleEl.node.getAttribute("r"));
    if (isNaN(cx) || isNaN(cy) || isNaN(r)) {
      continue;
    }
    highlightCircles.push({ cx: cx, cy: cy, r: r });
  }

  if (highlightRects.length === 0 && highlightCircles.length === 0) {
    return highlightedTextNodes;
  }

  const textEls = molSvg.selectAll("text");
  for (let i = 0; i < textEls.length; i++) {
    const textEl = textEls[i];
    if (!textEl || !textEl.node) {
      continue;
    }

    const textId = String(fGetNodeAttr(textEl, "id") || "");
    if (textId.indexOf("number") === 0 || textId.indexOf("mulerSelNum") === 0) {
      continue;
    }

    const textX = parseFloat(textEl.node.getAttribute("x"));
    const textY = parseFloat(textEl.node.getAttribute("y"));
    if (isNaN(textX) || isNaN(textY)) {
      continue;
    }

    let isHighlighted = false;

    for (let r = 0; r < highlightRects.length; r++) {
      const rect = highlightRects[r];
      if (
        textX >= rect.x &&
        textX <= rect.x + rect.width &&
        textY >= rect.y &&
        textY <= rect.y + rect.height
      ) {
        isHighlighted = true;
        break;
      }
    }

    if (!isHighlighted) {
      for (let c = 0; c < highlightCircles.length; c++) {
        const circle = highlightCircles[c];
        const dx = textX - circle.cx;
        const dy = textY - circle.cy;
        if (dx * dx + dy * dy <= circle.r * circle.r) {
          isHighlighted = true;
          break;
        }
      }
    }

    if (isHighlighted) {
      highlightedTextNodes.add(textEl.node);
    }
  }

  return highlightedTextNodes;
}

function fApplyAtomColors2DToSVGLabels() {
  if (!svgAtomColors2DFlag || !molSvg) {
    return;
  }

  const highlightedTextNodes = fBuildHighlightedTextNodeSet();
  const textNodeAtomIndexMap = fBuildTextNodeAtomIndexMap();

  const textEls = molSvg.selectAll("text");
  for (let i = 0; i < textEls.length; i++) {
    const textEl = textEls[i];
    if (!textEl || !textEl.node) {
      continue;
    }

    const textId = String(fGetNodeAttr(textEl, "id") || "");
    if (textId.indexOf("number") === 0 || textId.indexOf("mulerSelNum") === 0) {
      continue;
    }

    const tspanNodes = textEl.node.querySelectorAll("tspan");
    if (highlightedTextNodes.has(textEl.node)) {
      textEl.attr({ fill: "#000" });
      for (let t = 0; t < tspanNodes.length; t++) {
        tspanNodes[t].setAttribute("fill", "#000");
      }
      continue;
    }

    if (tspanNodes.length === 0) {
      const symbol = fResolveAtomSymbolFromLabelNode(textEl.node);
      const mappedFill = symbol
        ? fGetAtomColor2D(symbol, {
            atomIdx: textNodeAtomIndexMap.has(textEl.node)
              ? textNodeAtomIndexMap.get(textEl.node)
              : -1,
            parentSymbol: symbol,
          })
        : "";
      if (mappedFill) {
        textEl.attr({ fill: mappedFill });
      }
      continue;
    }

    const parentSymbol = fResolveAtomSymbolFromLabelNode(textEl.node);
    const parentAtomIdx = textNodeAtomIndexMap.has(textEl.node)
      ? textNodeAtomIndexMap.get(textEl.node)
      : -1;
    for (let t = 0; t < tspanNodes.length; t++) {
      const tspanNode = tspanNodes[t];
      const symbol = fResolveAtomSymbolFromLabelNode(tspanNode);
      if (!symbol) {
        continue;
      }

      const effectiveParentSymbol =
        symbol === "H"
          ? fResolveParentSymbolForHydrogenTspan(tspanNode, parentSymbol)
          : parentSymbol;

      const mappedFill = fGetAtomColor2D(symbol, {
        atomIdx: parentAtomIdx,
        parentSymbol: effectiveParentSymbol,
      });
      if (mappedFill) {
        tspanNode.setAttribute("fill", mappedFill);
      }
    }
  }
}

// Grey C–H bonds in expanded mode when colored symbols are on, matching the
// grey H labels (atomColors2D.H). Display-only base coat inside fUpdateSVG:
// fresh JSME SVG lines are black, so toggle-off needs no reset; green
// highlight backgrounds are separate attributes and win where applied.
function fApplyCHBondColors2D() {
  if (!svgAtomColors2DFlag || !molSvg) {
    return;
  }
  if (mode2D !== "expanded") {
    return;
  }
  if (typeof bondList === "undefined" || typeof allAtomsTypeList === "undefined" ||
      typeof svgBondList === "undefined" || !atomColors2D || !atomColors2D.H) {
    return;
  }
  const lineEls = molSvg.selectAll("line");
  if (!lineEls || lineEls.length === 0) {
    return;
  }
  for (let b = 0; b < bondList.length; b++) {
    if (!bondList[b]) {
      continue;
    }
    const a1 = bondList[b][0]; // 1-based
    const a2 = bondList[b][1]; // 1-based
    const t1 = allAtomsTypeList[a1 - 1];
    const t2 = allAtomsTypeList[a2 - 1];
    if (!((t1 === "C" && t2 === "H") || (t1 === "H" && t2 === "C"))) {
      continue;
    }
    const lineStart = svgBondList[b];
    const lineCount = bondList[b][2] || 1;
    for (let offset = 0; offset < lineCount; offset++) {
      const lineEl = lineEls[lineStart + offset - 1];
      if (lineEl) {
        lineEl.attr({ stroke: atomColors2D.H });
      }
    }
  }
}

function fShouldReverseAldehydeLabel(
  anchorEl,
  oxygenEl,
  anchorIdx,
  oxygenIdx,
  atomTextMap,
) {
  if (!anchorEl || !oxygenEl) {
    return false;
  }

  const anchorX = parseFloat(anchorEl.node.getAttribute("x"));
  const oxygenX = parseFloat(oxygenEl.node.getAttribute("x"));
  if (!isNaN(anchorX) && !isNaN(oxygenX)) {
    const oxygenDx = oxygenX - anchorX;
    if (Math.abs(oxygenDx) > 30) {
      return oxygenDx < 0;
    }
  }

  if (!Array.isArray(atomConnectivityList[anchorIdx])) {
    return false;
  }
  for (let i = 0; i < atomConnectivityList[anchorIdx].length; i++) {
    const neighborIdx = atomConnectivityList[anchorIdx][i];
    if (neighborIdx === oxygenIdx) {
      continue;
    }
    const neighborEl = atomTextMap[neighborIdx];
    if (!neighborEl) {
      continue;
    }
    const neighborX = parseFloat(neighborEl.node.getAttribute("x"));
    if (isNaN(anchorX) || isNaN(neighborX)) {
      continue;
    }
    // The aldehyde H sits opposite the carbon-chain neighbor.
    return neighborX > anchorX;
  }

  return false;
}

function fCompactFunctionalGroups2D() {
  if (!functionalGroupObj) {
    return;
  }

  const atomTextMap = fGetRenderedAtomTextMap(true, true);
  const atomRectMap = fGetRenderedAtomRectMap(true, true);
  const textElsToRemove = [];
  const rectElsToRemove = [];
  const bondsToRemove = [];
  const replacements = [];

  if (functionalGroupObj.hasOwnProperty("carboxylicAcid")) {
    const acidEntries = functionalGroupObj.carboxylicAcid.O || [];
    for (let i = 0; i < acidEntries.length; i++) {
      const entry = acidEntries[i];
      if (!Array.isArray(entry) || entry.length < 2) {
        continue;
      }
      const ohIdx = entry[0];
      const carbonylOIdx = entry[1];
      const anchorIdx = Array.isArray(atomConnectivityList[ohIdx])
        ? atomConnectivityList[ohIdx][0]
        : -1;
      if (anchorIdx < 0) {
        continue;
      }

      const anchorEl = atomTextMap[anchorIdx];
      const ohEl = atomTextMap[ohIdx];
      const carbonylOEl = atomTextMap[carbonylOIdx];
      if (!anchorEl || !ohEl || !carbonylOEl) {
        continue;
      }

      const anchorRectEl = atomRectMap[anchorIdx];
      const ohRectEl = atomRectMap[ohIdx];
      const carbonylORectEl = atomRectMap[carbonylOIdx];

      textElsToRemove.push(ohEl, carbonylOEl);
      rectElsToRemove.push(ohRectEl, carbonylORectEl);
      const ohHydrogens = fGetAttachedHydrogenIndices(ohIdx);
      for (let hIdx = 0; hIdx < ohHydrogens.length; hIdx++) {
        const hydrogenAtomIdx = ohHydrogens[hIdx];
        const hydrogenEl = atomTextMap[hydrogenAtomIdx];
        const hydrogenRectEl = atomRectMap[hydrogenAtomIdx];
        if (hydrogenEl) {
          textElsToRemove.push(hydrogenEl);
        }
        if (hydrogenRectEl) {
          rectElsToRemove.push(hydrogenRectEl);
        }
        const hydrogenBondIdx = fFindBondIndexByAtoms(ohIdx, hydrogenAtomIdx);
        if (hydrogenBondIdx >= 0) {
          bondsToRemove.push(hydrogenBondIdx);
        }
      }
      bondsToRemove.push(
        fFindBondIndexByAtoms(anchorIdx, ohIdx),
        fFindBondIndexByAtoms(anchorIdx, carbonylOIdx),
      );
      const anchorNeighbors = Array.isArray(atomConnectivityList[anchorIdx])
        ? atomConnectivityList[anchorIdx]
        : [];
      let carbonNeighborCount = 0;
      for (let n = 0; n < anchorNeighbors.length; n++) {
        if (allAtomsTypeList[anchorNeighbors[n]] === "C") {
          carbonNeighborCount += 1;
        }
      }
      const isFormicAcid =
        carbonNeighborCount === 0 && carbonHydrogens[anchorIdx] === 1;
      const reverseAcid = isFormicAcid
        ? false
        : fShouldReverseCompactLabel(anchorEl, [ohEl, carbonylOEl]);
      const acidLabelKey = isFormicAcid
        ? "HCOOH"
        : reverseAcid
          ? "HOOC"
          : "COOH";
      const acidOFill = fGetDisplayAtomFill("O", carbonylOEl, ohEl, anchorEl);
      const acidMarkup = isFormicAcid
        ? fBuildCompactAtomTspan(
            "H",
            null,
            "svgHydrogenPart svgCarbonAttachedHydrogen",
          ) +
          fBuildCompactAtomTspan("C") +
          fBuildCompactAtomTspan("O", acidOFill) +
          fBuildCompactAtomTspan("O", acidOFill) +
          fBuildCompactAtomTspan(
            "H",
            null,
            "svgHydrogenPart svgOxygenAttachedHydrogen",
          )
        : reverseAcid
          ? fBuildCompactAtomTspan(
              "H",
              null,
              "svgHydrogenPart svgOxygenAttachedHydrogen",
            ) +
            fBuildCompactAtomTspan("O", acidOFill) +
            fBuildCompactAtomTspan("O", acidOFill) +
            fBuildCompactAtomTspan("C")
          : fBuildCompactAtomTspan("C") +
            fBuildCompactAtomTspan("O", acidOFill) +
            fBuildCompactAtomTspan("O", acidOFill) +
            fBuildCompactAtomTspan(
              "H",
              null,
              "svgHydrogenPart svgOxygenAttachedHydrogen",
            );
      const acidAttrs = reverseAcid
        ? fGetReversedCompactLabelAttrs(anchorEl, "HOOC")
        : fGetForwardCompactLabelAttrs(anchorEl, acidLabelKey);
      replacements.push({
        anchorIdx: anchorIdx,
        el: anchorEl,
        markup: acidMarkup,
        attrs: acidAttrs,
        rectEl: anchorRectEl,
        labelKey: acidLabelKey,
        reverseLabel: reverseAcid,
        geometryHint: fBuildCompactGeometryHint(anchorEl, anchorRectEl),
      });
    }
  }

  if (functionalGroupObj.hasOwnProperty("aldehyde")) {
    const aldehydeEntries = functionalGroupObj.aldehyde.O || [];
    for (let i = 0; i < aldehydeEntries.length; i++) {
      const oxygenIdx = aldehydeEntries[i];
      const anchorIdx = Array.isArray(atomConnectivityList[oxygenIdx])
        ? atomConnectivityList[oxygenIdx][0]
        : -1;
      if (anchorIdx < 0) {
        continue;
      }

      // Methanal has only O as a heavy neighbour: retain BOTH H in HCHO.
      const carbonNeighbours = atomConnectivityList[anchorIdx] || [];
      const isMethanal = carbonNeighbours.length === 1 && atomValenceList[anchorIdx] === 2 && allAtomsTypeList[carbonNeighbours[0]] === "O";
      if (!isMethanal && !carbonNeighbours.some(n => allAtomsTypeList[n] === "C")) continue;
      const anchorEl = atomTextMap[anchorIdx];
      const oxygenEl = atomTextMap[oxygenIdx];
      if (!anchorEl || !oxygenEl) {
        continue;
      }

      const anchorRectEl = atomRectMap[anchorIdx];
      const oxygenRectEl = atomRectMap[oxygenIdx];

      textElsToRemove.push(oxygenEl);
      rectElsToRemove.push(oxygenRectEl);
      const anchorHydrogens = fGetAttachedHydrogenIndices(anchorIdx);
      for (let hIdx = 0; hIdx < anchorHydrogens.length; hIdx++) {
        const hydrogenAtomIdx = anchorHydrogens[hIdx];
        const hydrogenEl = atomTextMap[hydrogenAtomIdx];
        const hydrogenRectEl = atomRectMap[hydrogenAtomIdx];
        if (hydrogenEl) {
          textElsToRemove.push(hydrogenEl);
        }
        if (hydrogenRectEl) {
          rectElsToRemove.push(hydrogenRectEl);
        }
        const hydrogenBondIdx = fFindBondIndexByAtoms(
          anchorIdx,
          hydrogenAtomIdx,
        );
        if (hydrogenBondIdx >= 0) {
          bondsToRemove.push(hydrogenBondIdx);
        }
      }
      bondsToRemove.push(fFindBondIndexByAtoms(anchorIdx, oxygenIdx));
      const reverseAldehyde = !isMethanal && fShouldReverseAldehydeLabel(
        anchorEl,
        oxygenEl,
        anchorIdx,
        oxygenIdx,
        atomTextMap,
      );
      const aldehydeOFill = fGetDisplayAtomFill("O", oxygenEl, anchorEl);
      const aldehydeMarkup = isMethanal
        ? fBuildCompactAtomTspan("H", null, "svgHydrogenPart svgCarbonAttachedHydrogen") +
          fBuildCompactAtomTspan("C") +
          fBuildCompactAtomTspan("H", null, "svgHydrogenPart svgCarbonAttachedHydrogen") +
          fBuildCompactAtomTspan("O", aldehydeOFill)
        : reverseAldehyde
        ? fBuildCompactAtomTspan("O", aldehydeOFill) +
          fBuildCompactAtomTspan(
            "H",
            null,
            "svgHydrogenPart svgCarbonAttachedHydrogen",
          ) +
          fBuildCompactAtomTspan("C")
        : fBuildCompactAtomTspan("C") +
          fBuildCompactAtomTspan(
            "H",
            null,
            "svgHydrogenPart svgCarbonAttachedHydrogen",
          ) +
          fBuildCompactAtomTspan("O", aldehydeOFill);
      replacements.push({
        anchorIdx: anchorIdx,
        el: anchorEl,
        markup: aldehydeMarkup,
        attrs: isMethanal
          ? fGetForwardCompactLabelAttrs(anchorEl, "HCHO")
          : reverseAldehyde
          ? fGetReversedCompactLabelAttrs(anchorEl, "OHC")
          : null,
        rectEl: anchorRectEl,
        labelKey: isMethanal ? "HCHO" : reverseAldehyde ? "OHC" : "CHO",
        reverseLabel: reverseAldehyde,
        geometryHint: fBuildCompactGeometryHint(anchorEl, anchorRectEl),
      });
    }
  }

  if (functionalGroupObj.hasOwnProperty("cyanide")) {
    const cyanideEntries = functionalGroupObj.cyanide.N || [];
    for (let i = 0; i < cyanideEntries.length; i++) {
      const nitrogenIdx = cyanideEntries[i];
      const anchorIdx = Array.isArray(atomConnectivityList[nitrogenIdx])
        ? atomConnectivityList[nitrogenIdx][0]
        : -1;
      if (anchorIdx < 0) {
        continue;
      }

      const anchorEl = atomTextMap[anchorIdx];
      const nitrogenEl = atomTextMap[nitrogenIdx];
      if (!anchorEl || !nitrogenEl) {
        continue;
      }

      const anchorRectEl = atomRectMap[anchorIdx];
      const nitrogenRectEl = atomRectMap[nitrogenIdx];
      textElsToRemove.push(nitrogenEl);
      rectElsToRemove.push(nitrogenRectEl);
      bondsToRemove.push(fFindBondIndexByAtoms(anchorIdx, nitrogenIdx));

      const reverseCyanide = fShouldReverseCompactLabel(anchorEl, [nitrogenEl]);
      const nitrogenFill = fGetDisplayAtomFill("N", nitrogenEl, anchorEl);
      const cyanideMarkup = reverseCyanide
        ? fBuildCompactAtomTspan("N", nitrogenFill) +
          fBuildCompactAtomTspan("C")
        : fBuildCompactAtomTspan("C") +
          fBuildCompactAtomTspan("N", nitrogenFill);

      replacements.push({
        anchorIdx: anchorIdx,
        el: anchorEl,
        markup: cyanideMarkup,
        attrs: reverseCyanide
          ? fGetReversedCompactLabelAttrs(anchorEl, "NC")
          : null,
        rectEl: anchorRectEl,
        labelKey: reverseCyanide ? "NC" : "CN",
        reverseLabel: reverseCyanide,
        geometryHint: fBuildCompactGeometryHint(anchorEl, anchorRectEl),
      });
    }
  }

  if (functionalGroupObj.hasOwnProperty("nitro")) {
    const nitroEntries = functionalGroupObj.nitro.N || [];
    for (let i = 0; i < nitroEntries.length; i++) {
      const nitrogenIdx = nitroEntries[i];
      if (!Array.isArray(atomConnectivityList[nitrogenIdx])) {
        continue;
      }

      const oxygenIndices = [];
      for (let n = 0; n < atomConnectivityList[nitrogenIdx].length; n++) {
        const neighborIdx = atomConnectivityList[nitrogenIdx][n];
        const neighborEl = allAtomsTypeList[neighborIdx];
        if (neighborEl === "O") {
          oxygenIndices.push(neighborIdx);
        }
      }
      if (oxygenIndices.length < 2) {
        continue;
      }

      const anchorIdx = nitrogenIdx;

      const anchorEl = atomTextMap[anchorIdx];
      const oxygenEl1 = atomTextMap[oxygenIndices[0]];
      const oxygenEl2 = atomTextMap[oxygenIndices[1]];
      if (!anchorEl || !oxygenEl1 || !oxygenEl2) {
        continue;
      }

      const anchorRectEl = atomRectMap[anchorIdx];
      const oxygenRectEl1 = atomRectMap[oxygenIndices[0]];
      const oxygenRectEl2 = atomRectMap[oxygenIndices[1]];
      textElsToRemove.push(oxygenEl1, oxygenEl2);
      rectElsToRemove.push(oxygenRectEl1, oxygenRectEl2);

      for (let o = 0; o < oxygenIndices.length; o++) {
        bondsToRemove.push(
          fFindBondIndexByAtoms(nitrogenIdx, oxygenIndices[o]),
        );
      }

      const reverseNitro = fShouldReverseCompactLabel(anchorEl, [
        oxygenEl1,
        oxygenEl2,
      ]);
      const oxygenFill = fGetDisplayAtomFill(
        "O",
        oxygenEl1,
        oxygenEl2,
        anchorEl,
      );
      const nitrogenFill = fGetDisplayAtomFill("N", anchorEl);
      const nitroMarkup = reverseNitro
        ? fBuildCompactAtomTspan("O", oxygenFill) +
          `<tspan dy="70" font-size=".8em"${oxygenFill ? ` fill="${oxygenFill}"` : ""}>2</tspan>` +
          `<tspan dy="-70"${nitrogenFill ? ` fill="${nitrogenFill}"` : ""}>N</tspan>`
        : fBuildCompactAtomTspan("N", nitrogenFill) +
          fBuildCompactAtomTspan("O", oxygenFill) +
          `<tspan dy="70" font-size=".8em"${oxygenFill ? ` fill="${oxygenFill}"` : ""}>2</tspan>`;

      replacements.push({
        anchorIdx: anchorIdx,
        el: anchorEl,
        markup: nitroMarkup,
        attrs: reverseNitro
          ? fGetReversedCompactLabelAttrs(anchorEl, "O2N")
          : null,
        rectEl: anchorRectEl,
        labelKey: reverseNitro ? "O2N" : "NO2",
        reverseLabel: reverseNitro,
        geometryHint: fBuildCompactGeometryHint(anchorEl, anchorRectEl),
      });
    }
  }

  const lineEls = molSvg.selectAll("line");
  for (let i = 0; i < bondsToRemove.length; i++) {
    fRemoveBondLinesByBondIndex(bondsToRemove[i], lineEls);
  }
  // Record the removed bonds for the selection line groups (positions of all
  // later bonds shift by the deleted lines; see fMulerSelectLineGroups).
  try {
    if (typeof window !== "undefined") window.__mulerRemovedBondIdx = bondsToRemove.slice();
  } catch (eRB) {}

  const nearbyRectEls = fCollectHighlightRectsNearText(textElsToRemove);
  for (let i = 0; i < nearbyRectEls.length; i++) {
    rectElsToRemove.push(nearbyRectEls[i]);
  }

  const nearbyCircleEls = fCollectHighlightCirclesNearText(textElsToRemove);
  for (let i = 0; i < nearbyCircleEls.length; i++) {
    if (nearbyCircleEls[i]) {
      nearbyCircleEls[i].remove();
    }
  }

  for (let i = 0; i < textElsToRemove.length; i++) {
    if (textElsToRemove[i]) {
      textElsToRemove[i].remove();
    }
  }

  for (let i = 0; i < rectElsToRemove.length; i++) {
    if (rectElsToRemove[i]) {
      rectElsToRemove[i].remove();
    }
  }

  for (let i = 0; i < replacements.length; i++) {
    const newTextEl = fReplaceTextElementMarkup(
      replacements[i].el,
      replacements[i].markup,
      replacements[i].attrs,
    );
    const rectEl =
      replacements[i].rectEl &&
      replacements[i].rectEl.node &&
      replacements[i].rectEl.node.parentNode
        ? replacements[i].rectEl
        : null;
    var compactRectEl = fResizeCompactLabelRect(
      rectEl,
      newTextEl,
      replacements[i].labelKey,
      replacements[i].reverseLabel,
      replacements[i].geometryHint,
    );
    // Tag the group backplate so selection can distinguish an anchor-only
    // highlight from a whole-fragment highlight. The tag is geometry only;
    // atom/rect order maps ignore it.
    try {
      if (compactRectEl && compactRectEl.node && replacements[i].anchorIdx >= 0) {
        compactRectEl.node.setAttribute("data-muler-compact-rect", String(replacements[i].anchorIdx + 1));
      }
    } catch (eCR) {}
    if (newTextEl && replacements[i].anchorIdx >= 0) {
      const owner = String(replacements[i].anchorIdx + 1);
      newTextEl.node.setAttribute("data-namelecule-atom", owner);
      newTextEl.node.setAttribute("data-namelecule-role", "label");
      const rect = rectEl || MuSVG(newTextEl.node.previousElementSibling);
      if (rect && rect.node.localName === "rect") {
        rect.node.setAttribute("data-namelecule-atom", owner);
        rect.node.setAttribute("data-namelecule-role", "backplate");
      }
      compactNumberingLabelMap[replacements[i].anchorIdx] =
        replacements[i].labelKey;
    }
  }
}

// ── fMarkExpandedHydrogens ───────────────────────────────────────────────

function fWrapStandaloneHydrogenTextsAsTspan() {
  if (!molSvg) {
    return;
  }

  const textEls = molSvg.selectAll("text");
  for (let i = 0; i < textEls.length; i++) {
    const textEl = textEls[i];
    if (!textEl || !textEl.node) {
      continue;
    }
    if (textEl.node.children && textEl.node.children.length > 0) {
      continue;
    }

    const rawText = String(textEl.node.textContent || "").trim();

    if (rawText === "OH") {
      const oxygenFill = fGetDisplayAtomFill("O", textEl);
      const hydrogenFill = fGetDisplayAtomFill(
        "H",
        { parentSymbol: "O" },
        textEl,
      );
      fReplaceTextElementMarkup(
        textEl,
        `<tspan${oxygenFill ? ` fill="${oxygenFill}"` : ""}>O</tspan><tspan class="svgHydrogenPart"${hydrogenFill ? ` fill="${hydrogenFill}"` : ""}>H</tspan>`,
      );
      continue;
    }

    if (rawText === "HO" || rawText === "HO-") {
      const hydrogenFill = fGetDisplayAtomFill(
        "H",
        { parentSymbol: "O" },
        textEl,
      );
      const oxygenFill = fGetDisplayAtomFill("O", textEl);
      let markup =
        `<tspan class="svgHydrogenPart"${hydrogenFill ? ` fill="${hydrogenFill}"` : ""}>H</tspan>` +
        `<tspan${oxygenFill ? ` fill="${oxygenFill}"` : ""}>O</tspan>`;
      if (rawText === "HO-") {
        markup += `<tspan>-</tspan>`;
      }
      fReplaceTextElementMarkup(textEl, markup);
      continue;
    }

    if (rawText !== "H") {
      continue;
    }

    const existingClass = fGetNodeAttr(textEl, "class");
    const classOverride = existingClass
      ? existingClass.indexOf("svgHydrogenPart") === -1
        ? existingClass + " svgHydrogenPart"
        : existingClass
      : "svgHydrogenPart";
    const hydrogenFill = fGetDisplayAtomFill("H", textEl);

    fReplaceTextElementMarkup(
      textEl,
      `<tspan class="svgHydrogenPart"${hydrogenFill ? ` fill="${hydrogenFill}"` : ""}>H</tspan>`,
      { class: classOverride },
    );
  }
}

function fMarkExpandedHydrogens() {
  fWrapStandaloneHydrogenTextsAsTspan();
}

function fRefreshLabelBackplates() {
  const svg = document.querySelector("#jsmeNomeclatureSVG svg");
  if (!svg || !svg.getClientRects().length) return;
  const metrics = window.NameleculeLabelMetrics;
  if (!metrics) throw new Error("Label metrics service unavailable");
  for (const text of svg.querySelectorAll('text:not([id^="number"]):not([id^="mulerSelNum"])')) {
    if (!text.hasAttribute("data-namelecule-atom")) throw new Error("Unowned 2D label");
  }
  const owners=new Set();
  for (const text of svg.querySelectorAll('text[data-namelecule-role="label"]')) {
    if (text.hasAttribute('data-hidden-carbon-h') || text.hasAttribute('data-muler-hidden')) continue;
    const owner = text.getAttribute('data-namelecule-atom');
    const index=Number(owner)-1;
    if (!Number.isInteger(index) || index<0 || index>=allAtomsTypeList.length || owners.has(owner))
      throw new Error("Invalid or duplicate 2D atom owner");
    owners.add(owner);
    const rect = svg.querySelector(`rect[data-namelecule-atom="${owner}"][data-namelecule-role="backplate"]`);
    if (!rect) throw new Error("Missing owned label backplate: " + owner);
    const box = metrics.element(text), matrix = text.getScreenCTM();
    if (!box || !matrix) throw new Error("Label bounds unavailable: " + owner);
    const scale = Math.hypot(matrix.a,matrix.b), font = parseFloat(getComputedStyle(text).fontSize);
    if (!(scale > 0 && font > 0)) continue;
    // Single-element labels retain the approved centered square. Compound
    // OH/NH2 labels need their complete measured ink bounds, including H/tails.
    const singleElement = text.textContent.replace(/\s+/g, "") === allAtomsTypeList[index];
    if (svg.dataset.alkaneFixedCCScale && text.dataset.fixedCCAtomX && singleElement) {
      const half=font*.52, x=Number(text.dataset.fixedCCAtomX), y=Number(text.dataset.fixedCCAtomY);
      for (const [key,value] of Object.entries({x:x-half,y:y-half,width:2*half,height:2*half,rx:0,ry:0})) rect.setAttribute(key,value);
      continue;
    }
    const line=svg.querySelector('line'), bondWidth=line ? parseFloat(line.getAttribute('stroke-width')) || 0 : 0;
    const padding=Math.max(font*.06,Math.min(.6/scale,font*.18)) + bondWidth/2;
    for (const [key,value] of Object.entries({x:box.left-padding,y:box.top-padding,
        width:box.right-box.left+2*padding,height:box.bottom-box.top+2*padding,rx:0,ry:0})) rect.setAttribute(key,value);
  }
}

// Reject a drawing whose visible graph has lost a complete bond primitive.
// Interval clipping is exact for our rectangular backplates, not pixel sampling.
function fValidate2DBondVisibility() {
  const svg=document.querySelector("#jsmeNomeclatureSVG svg");
  if (!svg || !svg.getClientRects().length) return;
  const visible=el=>!el.hasAttribute("data-hidden-carbon-h") &&
    getComputedStyle(el).display!=="none" && getComputedStyle(el).visibility!=="hidden";
  const masks=[...svg.querySelectorAll('rect[data-namelecule-role="backplate"]')].filter(visible).map(r=>({
    inverse:r.getScreenCTM()?.inverse(), x:+r.getAttribute("x"),y:+r.getAttribute("y"),
    width:+r.getAttribute("width"),height:+r.getAttribute("height")
  })).filter(r=>r.inverse);
  for (const line of [...svg.querySelectorAll("line")].filter(visible)) {
    const m=line.getScreenCTM();if (!m) continue;
    const a=new DOMPoint(+line.getAttribute("x1"),+line.getAttribute("y1")).matrixTransform(m);
    const b=new DOMPoint(+line.getAttribute("x2"),+line.getAttribute("y2")).matrixTransform(m);
    if (Math.hypot(b.x-a.x,b.y-a.y)<.01) continue;
    const intervals=[];
    for (const r of masks) {
      const p=a.matrixTransform(r.inverse),q=b.matrixTransform(r.inverse);
      let lo=0,hi=1;
      for (const [v,d,min,max] of [[p.x,q.x-p.x,r.x,r.x+r.width],[p.y,q.y-p.y,r.y,r.y+r.height]]) {
        if (Math.abs(d)<1e-9) {if(v<min || v>max) {hi=-1;break;}}
        else {const t=(min-v)/d,u=(max-v)/d;lo=Math.max(lo,Math.min(t,u));hi=Math.min(hi,Math.max(t,u));}
      }
      if (lo<=hi) intervals.push([lo,hi]);
    }
    intervals.sort((a,b)=>a[0]-b[0]);let covered=0;
    for (const [lo,hi] of intervals) {if(lo>covered+1e-7)break;covered=Math.max(covered,hi);}
    if (covered>=1-1e-7) throw new Error("2D bond fully hidden by label backplates");
  }
}

// ── fMolHasSpCarbon ────────────────────────────────────────────────────────
// True when the parsed 2D structure contains at least one sp-hybridised
// carbon: a carbon in a triple bond (C≡C or C≡N) or in cumulated double bonds
// (C=C=C, allene). Reads the core bond graph (bondList entries are
// [atom1, atom2, order] with 1-based atoms into allAtomsTypeList). No
// molecule selected or no analysed graph → false.

function fMolHasSpCarbon() {
  if (
    !selectedMol ||
    !Array.isArray(bondList) ||
    !Array.isArray(allAtomsTypeList)
  ) {
    return false;
  }
  const ccDoubleCount = {};
  for (let i = 0; i < bondList.length; i++) {
    const bond = bondList[i];
    if (!bond) continue;
    const atom1 = bond[0];
    const atom2 = bond[1];
    const order = bond[2];
    if (order === 3) {
      if (
        allAtomsTypeList[atom1 - 1] === "C" ||
        allAtomsTypeList[atom2 - 1] === "C"
      ) {
        return true;
      }
    } else if (order === 2) {
      if (
        allAtomsTypeList[atom1 - 1] === "C" &&
        allAtomsTypeList[atom2 - 1] === "C"
      ) {
        ccDoubleCount[atom1] = (ccDoubleCount[atom1] || 0) + 1;
        ccDoubleCount[atom2] = (ccDoubleCount[atom2] || 0) + 1;
      }
    }
  }
  for (const atomIdx in ccDoubleCount) {
    if (ccDoubleCount[atomIdx] >= 2) {
      return true;
    }
  }
  return false;
}

// ── fHideSkeletalSpCarbons ─────────────────────────────────────────────────
// In pure skeletal mode sp carbons are drawn as C labels with rounded
// backplates that mask the bond lines. Remove the paired label and backplate
// for any molecule carrying an sp carbon (alkynes, enynes, yne-carbonyls,
// nitriles, allenes); bonds, highlights and numbering stay intact.

function fHideSkeletalSpCarbons() {
  if (mode2D !== "skeletal" || !fMolHasSpCarbon()) {
    return;
  }
  const svg = document.querySelector("#jsmeNomeclatureSVG svg");
  if (!svg) {
    return;
  }
  // Hide (NOT remove): deleting these nodes shifts every order map built on
  // the live DOM (atom text/rect maps assign slots in document order), so
  // later atoms would resolve onto their neighbor's label. display:none keeps
  // document order — and PNG export still omits them. Pick code skips
  // data-muler-hidden nodes; the vertex fallback owns those carbons.
  svg.querySelectorAll("text").forEach(function (label) {
    if (label.textContent.trim() !== "C") {
      return;
    }
    try { label.setAttribute("data-muler-hidden", "spC"); } catch (eM) {}
    try { label.style.display = "none"; } catch (eD) {}
    const backplate = label.previousElementSibling;
    if (
      backplate &&
      backplate.localName === "rect" &&
      backplate.hasAttribute("rx")
    ) {
      try { backplate.setAttribute("data-muler-hidden", "spC"); } catch (eM2) {}
      try { backplate.style.display = "none"; } catch (eD2) {}
    }
  });
}

// Match explicit H by its actual chemical bond's native SVG endpoints and
// paired backplate, never by text ordinal (skeletal carbons have no text).
// Keep hidden nodes in the DOM so existing bond/atom indices stay stable.
function fHideEsterSkeletalCarbonHydrogens() {
  if (mode2D !== 'skeletal' || !fIsSingleEster()) return;
  const svg=document.querySelector('#jsmeNomeclatureSVG svg');
  if (!svg) return;
  const lines=[...svg.querySelectorAll('line')];
  for (let i=0;i<bondList.length;i++) {
    const [a,b,order]=bondList[i], ta=allAtomsTypeList[a-1], tb=allAtomsTypeList[b-1];
    if (order !== 1 || !((ta === 'C' && tb === 'H') || (ta === 'H' && tb === 'C'))) continue;
    const line=lines[svgBondList[i]-1];
    if (!line) continue;
    const ends=[1,2].map(k => [Number(line.getAttribute('x'+k)),Number(line.getAttribute('y'+k))]);
    const matches=[...svg.querySelectorAll('text')].filter(label => {
      if (label.textContent.trim() !== 'H') return false;
      const r=label.previousElementSibling;
      if (!r || r.localName !== 'rect' || !r.hasAttribute('rx')) return false;
      const x=Number(r.getAttribute('x')), y=Number(r.getAttribute('y'));
      const w=Number(r.getAttribute('width')), h=Number(r.getAttribute('height'));
      return ends.some(p => p[0]>=x && p[0]<=x+w && p[1]>=y && p[1]<=y+h);
    });
    if (matches.length !== 1) {
      console.warn('Unmatched skeletal ester H',selectedMol,ta === 'H' ? a : b);
      continue;
    }
    for (const el of [line,matches[0],matches[0].previousElementSibling]) {
      el.setAttribute('visibility','hidden');
      el.setAttribute('data-hidden-carbon-h','true');
    }
  }
}

// ── fUpdateSVG ────────────────────────────────────────────────────────────

// Use the same viewport policy for every 2D representation. Measure molecular
// bonds/labels only: backgrounds and highlight shapes must not affect centering.
// Reserve numbering room up front so its animation never moves the drawing.
// A shared library frame prevents molecule-by-molecule label magnification.
// Cache geometry only; the pixel size is recomputed for each visible viewport.
let uniform2DLibraryFrame = null;
function fPrepareFixedCCAlkanePrototype() {
  const esterScale = ["ethanoic_methyl_ester", "propanoic_methyl_ester", "methyl_methanoate", "isopropyl_ethanoate", "sec_butyl_ethanoate", "butyl_propanoate", "tert_butyl_methanoate", "isobutyl_2_methylpropanoate", "isopropyl_2_3_dimethylbutanoate"].includes(selectedMol);
  const carbonylScale = ["ethanal", "butanal", "propanal", "propynal", "pentanal", "methanal", "methyl_2_propanal", "dimethyl_2_3_butanal", "ethyl_2_methyl_3_pentanal", "ethyl_4_isopropyl_3_methyl_2_hexanal", "propenal", "methyl_2_propenal", "propanedial", "methyl_3_penten_2_dial", "ethyl_4_penten_4_yn_2_al", "isopropyl_2_buten_2_dial", "ethyl_2_methyl_3_hexen_2_yn_4_dial", "penten_1_one_3", "pentanone_2", "pentyn_4_one_2", "butanone", "propanone", "pentanone_3", "dimethyl_2_4_pentanone_3", "trimethyl_3_4_4_pentanone_2", "diethyl_4_5_dimethyl_2_6_heptanone_3", "penten_1_yn_4_one_3", "dimethyl_4_5_hexen_5_yn_1_one_3", "methyl_6_hepten_3_dione_2_5", "ethyl_3_methyl_4_octen_3_yn_5_dione_2_7", "isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5", "methanoicacid", "propionicacid", "butanoic_acid", "propenoic_acid", "propanedioic_acid", "hydroxypropanoic_acid_2", "Oxopropanoic_acid", "aminobutanoic_acid_3", "pentanoic_acid", "oxobutanoic_acid", "dihydroxybutanedioic_acid_2_3", "methyl_2_propanoic_acid", "dimethyl_2_2_propanoic_acid", "ethyl_2_methyl_3_pentanoic_acid", "ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid", "methyl_2_propenoic_acid", "ethyl_2_methyl_3_penten_2_yn_4_oic_acid", "ethyl_3_isopropyl_2_dimethyl_4_5_hexadien_2_4_dioic_acid", "ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid", "penten_2_yn_4_oic_acid", "hexen_2_yn_4_dioic_acid"].includes(selectedMol);
  const etherScale = ["dimethylether", "ethyl_methyl_ether", "diethyl_ether",
    "isopropyl_methyl_ether", "methyl_propyl_ether", "ethyl_propyl_ether",
    "ethyl_isopropyl_ether", "butyl_methyl_ether", "ethyl_sec_butyl_ether",
    "isobutyl_isopropyl_ether", "tert_butyl_isopropyl_ether"].includes(selectedMol);
  if (mode2D !== "expanded" ||
      (!etherScale && !carbonylScale && !esterScale && !["methane", "ethane", "propane", "butane", "pentane",
        "methyl_2_pentane", "dimethyl_2_3_butane", "ethyl_3_dimethyl_2_5_hexane",
        "ethene", "propene", "butene_1", "butene_2", "methyl_2_propene",
        "methyl_3_butene_1", "ethyl_3_dimethyl_2_5_hexene_2",
        "propyne", "ethyne", "butyne_1", "butyne_2", "methyl_3_butyne_1",
        "methyl_3_pentyne_1", "methyl_4_pentyne_2", "ethyl_4_dimethyl_3_5_heptyne_1",
        "propadiene", "pentadiene_1_3", "butadiene_1_3", "butadiene_1_2",
        "pentadiene_1_4", "methyl_3_pentadiene_1_3", "dimethyl_2_3_pentadiene_1_3",
        "ethyl_3_dimethyl_4_5_hexadiene_1_4",
        "penten_3_yne_1", "hexen_1_yne_4", "buten_1_yne_3", "hexen_2_yne_4",
        "methyl_2_buten_1_yne_3", "dimethyl_2_3_penten_1_yne_4",
        "ethyl_4_dimethyl_2_3_hepten_2_yne_5",
        "propanol_1", "penten_4_ol_2", "butanol_1", "butene_3_ol_2", "penten_2_ol_1", "propanediol_1_2", "propanetriol", "ethanol", "butanol_2", "methyl_4_pentanol_2", "dimethyl_2_2_pentanol_3", "methyl_2_propanediol_1_2", "methyl_3_buten_3_ol_2", "methyl_3_pentyn_4_ol_2", "methyl_4_penten_4_yn_2_ol_1", "ethyl_3_methyl_4_hexen_3_yn_5_ol_2", "isopropyl_4_dimethyl_3_5_heptanol_2"].includes(selectedMol))) return;
  const svg = molSvg?.node;
  if (!svg || svg.dataset.alkaneFixedCCScale) return;
  const lines = [...svg.querySelectorAll("line")];
  if (lines.length !== bondList.reduce((sum,bond)=>sum+bond[2],0)) return;
  const anchors = new Map(), lengths = [], hydrogenLengths = [];
  for (let i = 0; i < bondList.length; i++) {
    const [a, b, order] = bondList[i];
    if (![1,2,3].includes(order)) return;
    // Multiple-bond strokes can be offset from their atom centers. Derive centers
    // from single C-C/C-H bonds, using the actual bond-to-SVG primitive map.
    // Prefer single-bond anchors. A cumulene center can have only double
    // bonds; its missing anchor is resolved from validated stroke pairs below.
    if (order > 1) continue;
    const line = lines[svgBondList[i]-1];
    if (!line) return;
    const p = {x: Number(line.getAttribute("x1")), y: Number(line.getAttribute("y1"))};
    const q = {x: Number(line.getAttribute("x2")), y: Number(line.getAttribute("y2"))};
    if (![p.x, p.y, q.x, q.y].every(Number.isFinite)) return;
    for (const [atom, point] of [[a - 1, p], [b - 1, q]]) {
      const previous = anchors.get(atom);
      if (previous && Math.hypot(previous.x - point.x, previous.y - point.y) > 0.01) return;
      anchors.set(atom, point);
    }
    if ((allAtomsTypeList[a - 1] === "C" && allAtomsTypeList[b - 1] === "H") ||
        (allAtomsTypeList[a - 1] === "H" && allAtomsTypeList[b - 1] === "C")) {
      hydrogenLengths.push(Math.hypot(q.x - p.x, q.y - p.y));
    }
  }
  if (anchors.size !== allAtomsTypeList.length) {
    // Symmetric, parallel native double strokes identify their centerline.
    // Validate both endpoints against every existing anchor before accepting
    // missing centers. No atom or bond geometry is moved by this operation.
    for (let i=0;i<bondList.length;i++) {
      const [a,b,order]=bondList[i];
      if (order!==2) continue;
      const pair=lines.slice(svgBondList[i]-1,svgBondList[i]+1);
      if (pair.length!==2) return;
      const points=pair.map(line=>({
        p:{x:Number(line.getAttribute("x1")),y:Number(line.getAttribute("y1"))},
        q:{x:Number(line.getAttribute("x2")),y:Number(line.getAttribute("y2"))}
      }));
      if (points.some(v=>![v.p.x,v.p.y,v.q.x,v.q.y].every(Number.isFinite))) return;
      const vectors=points.map(v=>({x:v.q.x-v.p.x,y:v.q.y-v.p.y}));
      const lengths=vectors.map(v=>Math.hypot(v.x,v.y));
      if (lengths.some(v=>!(v>0)) || Math.abs(lengths[0]-lengths[1])>2 ||
          Math.abs(vectors[0].x*vectors[1].y-vectors[0].y*vectors[1].x)>lengths[0]*lengths[1]*.001 ||
          vectors[0].x*vectors[1].x+vectors[0].y*vectors[1].y<=0) return;
      for (const [atom,end] of [[a-1,"p"],[b-1,"q"]]) {
        const point={x:(points[0][end].x+points[1][end].x)/2,
          y:(points[0][end].y+points[1][end].y)/2};
        const previous=anchors.get(atom);
        // One native unit allows only the producer's integer rounding.
        if (previous && Math.hypot(previous.x-point.x,previous.y-point.y)>1) return;
        if (!previous) anchors.set(atom,point);
      }
    }
  }
  if (anchors.size !== allAtomsTypeList.length) return;
  for (const [a,b] of bondList) {
    const first=allAtomsTypeList[a-1], second=allAtomsTypeList[b-1];
    // Normalized drawings share the same heavy-bond unit. C-O includes
    // C=O, so methanal and methanoic acid also calibrate without any C-C.
    if (!(first === "C" && second === "C") &&
        !((etherScale || carbonylScale || esterScale) &&
          ((first === "C" && second === "O") || (first === "O" && second === "C"))) &&
        !(carbonylScale &&
          ((first === "C" && second === "N") || (first === "N" && second === "C")))) continue;
    const p=anchors.get(a-1),q=anchors.get(b-1);
    lengths.push(Math.hypot(q.x-p.x,q.y-p.y));
  }
  // Methane has no C-C. Its C-H/font uses half the common C-C/font unit.
  // This is a calibration value only; native atom anchors and bonds stay intact.
  if (!lengths.length && selectedMol === "methane") {
    lengths.push(...hydrogenLengths.map(length => length * 2));
  }
  if (!lengths.length || anchors.size !== allAtomsTypeList.length) return;
  lengths.sort((a, b) => a - b);
  // Original reference C-C/font 3.49, shortened by the approved 25%.
  // The existing calibration/backplate/numbering pipeline is shared by the
  // alkenes, alkynes and dienes; the historical dataset name stays for callers.
  // Change label size around native atom anchors, never molecular geometry.
  const font = lengths[Math.floor(lengths.length / 2)] / 2.6175;
  if (!(font > 0)) return;
  const context = document.createElement("canvas").getContext("2d");
  if (!context) return;
  const texts = fGetRenderedAtomTextMap(false, true), changes = [];
  for (const [atom, anchor] of anchors) {
    const label = texts[atom];
    const symbol = allAtomsTypeList[atom];
    const raw = label?.node.textContent.replace(/\s+/g, "");
    if (!label || !(raw === symbol || (carbonylScale &&
        ((symbol === "O" && ["OH", "HO"].includes(raw)) ||
         (symbol === "N" && raw === "NH2"))))) return;
    const originalFont = parseFloat(label.attr("font-size"));
    const x = Number(label.attr("x")), y = Number(label.attr("y"));
    if (!(originalFont > 0) || ![x, y].every(Number.isFinite)) return;
    const style = getComputedStyle(label.node);
    context.font = `${style.fontStyle} ${style.fontWeight} ${font}px ${style.fontFamily}`;
    const ink = context.measureText(allAtomsTypeList[atom]);
    const cx = (ink.actualBoundingBoxRight - ink.actualBoundingBoxLeft) / 2;
    const cy = (ink.actualBoundingBoxAscent - ink.actualBoundingBoxDescent) / 2;
    if (![cx, cy].every(Number.isFinite)) return;
    const prefix = raw === "HO" ? context.measureText("H").width : 0;
    // Keep implicit-H labels intact. Queue all changes, including numeric
    // subscript offsets, so a later validation failure leaves the drawing intact.
    const offsets = [];
    for (const tspan of label.node.querySelectorAll("tspan[dy]")) {
      const dy = tspan.getAttribute("dy");
      if (/^-?\d+(?:\.\d+)?$/.test(dy))
        offsets.push([tspan, String(Number(dy) * font / originalFont)]);
    }
    changes.push([label, {x: anchor.x - cx - prefix, y: anchor.y + cy,
      "font-size": font + "px"}, anchor, offsets]);
  }
  changes.forEach(([label, attributes, anchor, offsets]) => {
    label.attr(attributes);
    offsets.forEach(([node, dy]) => node.setAttribute("dy", dy));
    label.node.dataset.fixedCCAtomX = String(anchor.x);
    label.node.dataset.fixedCCAtomY = String(anchor.y);
  });
  svg.dataset.alkaneFixedCCScale = String(font / 270);
}

function fGetUniform2DLibraryFrame() {
  if (uniform2DLibraryFrame) return uniform2DLibraryFrame;
  let spanX = 1, spanY = 1;
  const inventory = window.MOL2D || {};
  Object.values(inventory).forEach(function (forms) {
    Object.values(forms).forEach(function (mol) {
      if (typeof mol !== 'string' || !mol.trim()) return;
      const lines = mol.split('\n'), counts = lines[3] || '';
      const na = Number(counts.slice(0,3)), nb = Number(counts.slice(3,6));
      if (!(na > 0)) return;
      const atoms = lines.slice(4,4+na).map(l => ({
        x:Number(l.slice(0,10)), y:Number(l.slice(10,20)), symbol:l.slice(31,34).trim()
      }));
      if (atoms.some(a => !Number.isFinite(a.x) || !Number.isFinite(a.y))) return;
      const heavyLengths = [], allLengths = [];
      lines.slice(4+na,4+na+nb).forEach(function (line) {
        const a=atoms[Number(line.slice(0,3))-1], b=atoms[Number(line.slice(3,6))-1];
        if (!a || !b) return;
        const length=Math.hypot(b.x-a.x,b.y-a.y);
        if (!(length > 0)) return;
        allLengths.push(length);
        if (a.symbol !== 'H' && b.symbol !== 'H') heavyLengths.push(length);
      });
      const lengths=(heavyLengths.length ? heavyLengths : allLengths).sort((a,b)=>a-b);
      const unit=lengths.length ? lengths[Math.floor(lengths.length/2)] : 1;
      spanX=Math.max(spanX,(Math.max(...atoms.map(a=>a.x))-Math.min(...atoms.map(a=>a.x)))/unit);
      spanY=Math.max(spanY,(Math.max(...atoms.map(a=>a.y))-Math.min(...atoms.map(a=>a.y)))/unit);
    });
  });
  // Native JSME uses up to ~3.7 em per heavy bond; reserve label/number margins.
  uniform2DLibraryFrame = {width:spanX*4+5, height:spanY*4+5};
  return uniform2DLibraryFrame;
}

function fFit2DSVG() {
  const svg = document.querySelector("#jsmeNomeclatureSVG svg");
  if (!svg || !svg.getClientRects().length) return;
  try {
    const rootMatrix = svg.getCTM();
    if (!rootMatrix) return;
    const inverse = rootMatrix.inverse();
    let left = Infinity, top = Infinity, right = -Infinity, bottom = -Infinity;
    svg.querySelectorAll("line, text, path").forEach(function (el) {
      if (el.closest("defs") || (el.id || "").indexOf("number") === 0 || (el.id || "").indexOf("mulerSelNum") === 0) return;
      if (el.hasAttribute('data-hidden-carbon-h') || el.hasAttribute('data-muler-hidden') ||
          el.hasAttribute('data-muler-sel') || el.hasAttribute('data-muler-compact-sel')) return;
      const matrix = el.getCTM();
      if (!matrix) return;
      const box = el.getBBox();
      const transform = inverse.multiply(matrix);
      [[box.x, box.y], [box.x + box.width, box.y],
       [box.x, box.y + box.height], [box.x + box.width, box.y + box.height]].forEach(function (xy) {
        const p = svg.createSVGPoint();
        p.x = xy[0]; p.y = xy[1];
        const q = p.matrixTransform(transform);
        left = Math.min(left, q.x); right = Math.max(right, q.x);
        top = Math.min(top, q.y); bottom = Math.max(bottom, q.y);
      });
    });
    // Single atoms and horizontal/vertical skeletal bonds are valid drawings.
    if (![left, top, right, bottom].every(Number.isFinite)) return;
    if (!svg.dataset.baseViewport) {
      const box = svg.viewBox.baseVal;
      svg.dataset.baseViewport = JSON.stringify([
        box.width || svg.width.baseVal.value,
        box.height || svg.height.baseVal.value,
      ]);
    }
    const size = JSON.parse(svg.dataset.baseViewport);
    if (!(size[0] > 0 && size[1] > 0)) return;
    const viewport = svg.parentNode.getBoundingClientRect();
    const aspect = viewport.width > 0 && viewport.height > 0
      ? viewport.width / viewport.height : size[0] / size[1];
    // Numbers are inserted in the first drawing group, whose coordinates
    // JSME scales down. Convert their clearance into root SVG units too.
    const numberGroup = svg.querySelector("g");
    const numberMatrix = numberGroup && numberGroup.getCTM();
    const numberTransform = numberMatrix ? inverse.multiply(numberMatrix) : null;
    // Reserve numbering clearance without forcing the largest library drawing
    // back to a smaller label size (all numbered forms are browser-checked).
    const prototypeNumberScale = Number(svg.dataset.alkaneFixedCCScale) || 1;
    const numberPaddingX = numberTransform
      ? 350 * prototypeNumberScale * (Math.abs(numberTransform.a) + Math.abs(numberTransform.c)) : 0;
    const numberPaddingY = numberTransform
      ? 350 * prototypeNumberScale * (Math.abs(numberTransform.b) + Math.abs(numberTransform.d)) : 0;
    const margin = Math.max(right - left, bottom - top) * 0.04;
    const paddingX = Math.max(numberPaddingX, margin);
    const paddingY = Math.max(numberPaddingY, margin);
    let desiredWidth = size[0];
    const label = svg.querySelector('text:not([id^="number"])');
    if (label && viewport.width > 0 && viewport.height > 0) {
      const frame=fGetUniform2DLibraryFrame();
      const fontSize=parseFloat(getComputedStyle(label).fontSize);
      const matrix=label.getCTM();
      const local=matrix && inverse.multiply(matrix);
      const fontInRoot=local && fontSize*Math.hypot(local.a,local.b);
      const zoom=molZoom2D/MOL_ZOOM_DEFAULT;
      // Main can request readable labels, with the bounds below fitting large
      // drawings. Saved embedded hosts retain their existing common scale.
      const pageScale=Number(document.documentElement.getAttribute("data-namelecule-2d-scale"));
      const initialScale=Number.isFinite(pageScale) && pageScale > 0 ? pageScale : 1;
      const pageFont=Number(document.documentElement.getAttribute("data-namelecule-2d-font-size"));
      const pixels=Number.isFinite(pageFont) && pageFont > 0 ? pageFont*zoom
        : Math.min(18,viewport.width/frame.width,viewport.height/frame.height)*zoom*1.15*initialScale;
      if (fontInRoot > 0 && pixels > 0) {
        desiredWidth=viewport.width*fontInRoot/pixels;
        svg.dataset.uniformAtomFontPixels=String(pixels);
      }
    }
    // Free editor input beyond the library frame still fits without clipping.
    const width = Math.max(desiredWidth, right - left + paddingX * 2,
      (bottom - top + paddingY * 2) * aspect);
    const height = width / aspect;
    svg.setAttribute("viewBox", [(left + right - width) / 2,
      (top + bottom - height) / 2, width, height].join(" "));
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    svg.style.width = "100%";
    svg.style.height = "100%";
    // Font bounds depend on the final viewBox (including browser hinting).
    fRefreshLabelBackplates();
  } catch (eFit) {
    /* Hidden/uninitialized drawings are fitted on the next visible render. */
  }
}

// JSME labels collinear sp carbons even in its skeletal depiction. Its bond
// lines already reach the atom centers; the label backplates mask those lines.
// Remove the paired labels/backplates, keeping the separate atom/bond highlights.

var MULER_SELECT_SEQ_DY = 300;  // selection badge baseline below label bottom, SVG units

// Selection-sequence badges (v56 1C order dimension): one per picked atom,
// numbered by selection order, below the label (locants live above). White
// text + cyan halo, tagged mulerSelNum* and skipped by highlight scraping
// like the numbering badges. Painted per render from live state — toggle,
// re-pick, exact-clear and mode switches renumber automatically.
// Main-chain only: FG and free selections paint the highlight with no numbers.
function fMulerSelectSeqBadges() {
  try {
    if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return;
    try { if (typeof fMulerSelectPurpose === "function" && fMulerSelectPurpose() !== "mainChain") return; } catch (eP) { return; }
    var sel = (typeof fMulerSelectState === "function") ? fMulerSelectState() : null;
    var atoms = (sel && sel.active === true && Array.isArray(sel.atoms2D)) ? sel.atoms2D : [];
    if (!atoms.length) return;
    if (typeof molSvg === "undefined" || !molSvg) return;
    var geom = null;
    try { if (typeof fMulerSelectGeom === "function") geom = fMulerSelectGeom(); } catch (eG) { geom = null; }
    var anchors = (geom && geom.anchors) || [];
    var byAtom = {};
    try { for (var ai = 0; ai < anchors.length; ai++) { if (anchors[ai] && !(anchors[ai].atom in byAtom)) byAtom[anchors[ai].atom] = anchors[ai]; } } catch (eA) {}
    var compByAnchor = {}, selectedSet = {};
    try {
      var cList = (geom && geom.comp) || [];
      for (var ci = 0; ci < cList.length; ci++) {
        if (cList[ci] && typeof cList[ci].anchor === "number") compByAnchor[cList[ci].anchor] = cList[ci];
      }
      for (var si = 0; si < atoms.length; si++) selectedSet[atoms[si]] = true;
    } catch (eCA) {}
    var verts = (geom && geom.verts) || [], va = (geom && geom.vassign) || [];
    // Expanded compensation mirrors fShowNumbering (the equalizer shrinks
    // the model while overlay glyphs stay fixed-size).
    var numFS = 380, numSW = 60, numK = 1;
    try {
      var _nf = 1, _nm = "condensed";
      try { _nf = (typeof fMol2DModeScaleFactor === "function") ? fMol2DModeScaleFactor() : 1; } catch (eNF) { _nf = 1; }
      try { _nm = (typeof mode2D !== "undefined") ? mode2D : "condensed"; } catch (eNM) { _nm = "condensed"; }
      if (_nm === "expanded" && _nf !== 1) {
        numFS = 380 / _nf;
        if (!(numFS > 0) || !isFinite(numFS)) numFS = 380;
        if (numFS < 296) numFS = 296;
        if (numFS > 844) numFS = 844;
        numSW = numFS * 60 / 380;
        numK = numFS / 380;
      }
    } catch (eNK) { numFS = 380; numSW = 60; numK = 1; }
    var gWrap = null;
    try { gWrap = molSvg.select("g"); } catch (eGW) { gWrap = null; }
    if (!gWrap || !gWrap.node) return;
    for (var i = 0; i < atoms.length; i++) {
      var a0 = atoms[i] - 1, bx = null, by = null;
      try {
        var cm = compByAnchor[a0];
        var cmHiddenPicked = false;
        if (cm && Array.isArray(cm.members)) {
          for (var cmi = 0; cmi < cm.members.length; cmi++) {
            if (cm.members[cmi] !== atoms[i] && selectedSet[cm.members[cmi]]) { cmHiddenPicked = true; break; }
          }
        }
        if (cm && !cmHiddenPicked && cm.atomBox && cm.atomBox.w > 0 && cm.atomBox.h > 0) {
          bx = cm.atomBox.x + cm.atomBox.w / 2;
          by = cm.atomBox.y + cm.atomBox.h / 2 + MULER_SELECT_SEQ_DY * numK;
        } else {
          var an = byAtom[a0];
          if (an && an.w > 0 && an.h > 0) { bx = an.x; by = an.y + an.h / 2 + MULER_SELECT_SEQ_DY * numK; }
          else {
            for (var vi = 0; vi < verts.length; vi++) {
              if (va[vi] === a0) { bx = verts[vi].x; by = verts[vi].y + MULER_HOVER_DOT_R + MULER_SELECT_SEQ_DY * numK; break; }
            }
            if (bx === null || bx === undefined) continue;
          }
        }
      } catch (eB) { continue; }
      try {
        var _cyan = (typeof MULER_SELECT_CYAN !== "undefined" && MULER_SELECT_CYAN) ? MULER_SELECT_CYAN : "#7ddfff";
        var s = "<text id='mulerSelNum" + i + "' x='" + Math.round(bx) + "' y='" + Math.round(by) + "' font-size='" + Math.round(numFS) + "px' font-weight='bold' font-family='Arial, sans-serif' text-anchor='middle' fill='" + _cyan + "' stroke='#000000' stroke-width='" + Math.round(numSW) + "px' paint-order='stroke' class='mulerSelNum'>" + (i + 1) + "</text>";
        var nel = null;
        try { nel = (typeof MuSVG !== "undefined" && MuSVG.parse) ? MuSVG.parse(s) : null; } catch (eP) { nel = null; }
        if (nel) gWrap.append(nel);
      } catch (eN) {}
    }
  } catch (e) {}
}

function fUpdateSVG() {
  try {
    fBuildMoleculeSVG();
    document.getElementById("jsmeNomeclatureSVG").removeAttribute("data-label-error");
  } catch (error) {
    // Never leave an obsolete molecule on screen after a failed redraw.
    const host = document.getElementById("jsmeNomeclatureSVG");
    host.replaceChildren();host.setAttribute("data-label-error", "true");
    const status=document.createElement("p");status.setAttribute("role","status");
    status.textContent="Η αναπαράσταση 2D δεν είναι διαθέσιμη. Δοκίμασε ξανά ή επίλεξε άλλη μορφή.";
    host.appendChild(status);
    console.warn("Namelecule 2D rendering unavailable", error);
  }
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
function fNumberingAnchor2D(atomNo) {
  if (mode2D !== "skeletal") {
    const label=fGetRenderedAtomTextMap(false,true)[atomNo-1];
    if (!label) return null;
    const compact=compactNumberingLabelMap[atomNo-1];
    return {x:compact ? fGetCompactLabelNumberX(label,compact,0) : parseInt(label.attr("x")),
      y:parseInt(label.attr("y"))};
  }
  const lines=molSvg.selectAll("line");let point=null;
  for (let i=0;i<bondList.length;i++) {
    const bond=bondList[i],line=lines[svgBondList[i]-1];if(!line)continue;
    if (bond[0]===atomNo) return {x:parseInt(line.attr("x1")),y:parseInt(line.attr("y1"))};
    if (bond[1]===atomNo) point={x:parseInt(line.attr("x2")),y:parseInt(line.attr("y2"))};
  }
  return point;
}

function fRefreshFontDrawing2D() {
  const svg=document.querySelector("#jsmeNomeclatureSVG svg");
  if (!svg) {fUpdateSVG();return;}
  const chain=((Array.isArray(numberingAtomOverride) ? numberingAtomOverride : mainChainAtomsList) || [])
    .filter(atomNo=>allAtomsTypeList[atomNo-1]==="C");
  const anchors=chain.map(fNumberingAnchor2D);
  const sources=Array.isArray(numbersSVGElements) ? numbersSVGElements.slice() : [];
  const visible=[...svg.querySelectorAll('text[id^="number"]')].map(n=>n.cloneNode(true));
  fUpdateSVG();
  const fresh=document.querySelector("#jsmeNomeclatureSVG svg");
  if (!fresh || !numberingFlag || !sources.length) return;
  const next=chain.map(fNumberingAnchor2D);
  // Update queued 2D positions while leaving the existing interval, progress,
  // override chains and all 3D echoes untouched.
  numbersSVGElements=sources.map((source,i)=>{
    if (!source || !anchors[i] || !next[i]) return source;
    const dx=next[i].x-anchors[i].x,dy=next[i].y-anchors[i].y;
    return source.replace(/(\bx=['"])([^'"]+)(['"])/,(_m,a,v,b)=>a+(Number(v)+dx)+b)
      .replace(/(\by=['"])([^'"]+)(['"])/,(_m,a,v,b)=>a+(Number(v)+dy)+b);
  });
  const group=molSvg.select("g");
  visible.forEach(node=>{
    const index=Number(node.id.slice(6)),before=anchors[index],after=next[index];
    if (before && after) {
      node.setAttribute("x",Number(node.getAttribute("x"))+after.x-before.x);
      node.setAttribute("y",Number(node.getAttribute("y"))+after.y-before.y);
      group.node.appendChild(node);
    }
  });
}

// ── Numbering aid (v56 locant/bond phases) ───────────────────────────────────
// Chain numbers as a position reference while a locant or bond-position quiz
// is armed — only for molecules whose main chain is already solved. Name
// boxes (branch names, bond types) get no numbers; locant boxes do.
// Numbers only (the aid never paints highlights), same number* ids,
// repaint-driven lifecycle.
function fMulerNumberAid() {
  try {
    if (typeof fMulerSelectPurpose !== "function") return;
    var _ap = fMulerSelectPurpose();
    if (_ap !== "loc" && _ap !== "bond" && _ap !== "branch") return;
    if (_ap === "branch") {
      try {
        var _bt = (typeof window !== "undefined") ? window.MulerQuizTarget : "";
        if ((typeof fMulerBranchTargetIsLocant !== "function") || !fMulerBranchTargetIsLocant(_bt)) return;
      } catch (eB) { return; }
    }
    if (_ap === "bond") {
      try {
        var _bd = (typeof window !== "undefined") ? window.MulerQuizTarget : "";
        if ((typeof fMulerBondTargetIsLocant !== "function") || !fMulerBondTargetIsLocant(_bd)) return;
      } catch (eBo) { return; }
    }
    if (typeof fMulerSelectPresenting === "function" && fMulerSelectPresenting()) return;
    if (typeof fMulerChainSolved !== "function" || !fMulerChainSolved()) return;
    if (typeof molSvg === "undefined" || !molSvg) return;
    var keep = false;
    try { keep = numberingFlag; } catch (eK) { keep = false; }
    try { numberingFlag = true; } catch (eS) { return; }
    try { if (typeof fShowAnalysisNumbering === "function") fShowAnalysisNumbering(0); } catch (eN) {}
    try { numberingFlag = keep; } catch (eR) {}
  } catch (e) {}
}

let labelFontRefreshFrame = null;
let labelFontPageActive = true;
function fCancelFontRefresh2D() {
  if (labelFontRefreshFrame!==null) cancelAnimationFrame(labelFontRefreshFrame);
  labelFontRefreshFrame=null;
}
// beforeunload can be cancelled; only pagehide suspends the controller.
window.addEventListener("beforeunload",fCancelFontRefresh2D);
window.addEventListener("pagehide",function(){labelFontPageActive=false;fCancelFontRefresh2D();});
window.addEventListener("pageshow",function(){labelFontPageActive=true;});
window.addEventListener("namelecule-font-metrics-change",function(){
  if (!labelFontPageActive) return;
  if (labelFontRefreshFrame!==null) cancelAnimationFrame(labelFontRefreshFrame);
  labelFontRefreshFrame=requestAnimationFrame(function(){
    labelFontRefreshFrame=null;
    if (labelFontPageActive && jsmeNomeclatureApplet && selectedMol) fRefreshFontDrawing2D();
  });
});

// ── patchtheNitrogen ──────────────────────────────────────────────────────

function patchtheNitrogen() {
  if (!functionalGroupObj || !molSvg) {
    return;
  }

  ////// NH2 special case PATCH //////
  if (functionalGroupObj.hasOwnProperty("amine")) {
    molSvg.selectAll("text").forEach(function (el) {
      var labelText = String(el.attr("text") || "").trim();
      var rawText = (el.node.textContent || "").replace(/\s+/g, "");
      // JSME Bug 2: stroke-width absorbed the label → DOM value contains '>'
      var swAttr = el.node.getAttribute("stroke-width") || "";
      var hasBug2 = swAttr.indexOf(">") !== -1;
      var isTarget =
        labelText === "2" || rawText === "2" || rawText === "NH2" || hasBug2;
      if (!isTarget) {
        return;
      }
      // Rebuild from scratch — only use clean positional/style attributes.
      // Do NOT use el.toString(): it carries the malformed stroke-width into
      // the string, so the boundary regex matches inside the attribute value.
      var x = el.node.getAttribute("x");
      var y = el.node.getAttribute("y");
      if (!x || !y) {
        return;
      }
      var fontSize = el.node.getAttribute("font-size");
      var textAnchor = el.node.getAttribute("text-anchor");
      var fill = fGetDisplayAtomFill("N", el);
      var stroke = el.node.getAttribute("stroke");
      var strokeW = swAttr.replace(/>[\s\S]*$/, ""); // "11px>NH2" → "11px"
      var attrs = `x="${x}" y="${y}"`;
      if (fontSize) {
        attrs += ` font-size="${fontSize}"`;
      }
      for (const key of ["font-family", "font-weight", "font-style",
          "data-namelecule-atom", "data-namelecule-role"]) {
        const value = el.node.getAttribute(key);
        if (value) attrs += ` ${key}="${value}"`;
      }
      if (textAnchor) {
        attrs += ` text-anchor="${textAnchor}"`;
      }
      if (fill) {
        attrs += ` fill="${fill}"`;
      }
      if (stroke && strokeW) {
        attrs += ` stroke="${stroke}" stroke-width="${strokeW}"`;
      }
      var hydrogenFill = fGetDisplayAtomFill("H", { parentSymbol: "N" }, el);
      var hydrogenFillAttr = hydrogenFill ? ` fill="${hydrogenFill}"` : "";
      var newString =
        `<text ${attrs}>N<tspan class="svgHydrogenPart"${hydrogenFillAttr}>H<tspan dy="70" font-size=".8em">2</tspan></tspan></text>`;
      var newEl;
      try {
        newEl = MuSVG.parse(newString);
      } catch (e) {
        return;
      }
      var parentNode = el.node.parentNode;
      var nextSibling = el.node.nextSibling;
      if (!parentNode || !newEl || !newEl.node) {
        return;
      }
      var fragmentNode = newEl.node;
      while (fragmentNode.firstChild) {
        parentNode.insertBefore(fragmentNode.firstChild, nextSibling);
      }
      el.remove();
    });
  }
  ////// NO2 special case PATCH //////
  if (functionalGroupObj.hasOwnProperty("nitro")) {
    molSvg.selectAll("text").forEach(function (el) {
      var txt = el.attr("text") || "";
      if (String(txt).trim() === "+") {
        el.attr({ text: "N+" });
      }
      if (String(txt).trim() === "-") {
        el.attr({ text: "O-" });
      }
    });
  }
}

// ── fLoadMol3D ────────────────────────────────────────────────────────────

// ── Safe JSmol access ─────────────────────────────────────────────────────
// The JSmol library loads async (no document.write: Chrome may block the
// cross-site parser-blocking script on poor connectivity) and the applet
// initializes after that. Every JSmol call below goes through fJSmol*
// wrappers: fail-closed (null / no-op) with a pending-3D note instead of
// throwing, so a cold/dead applet can never abort molecule loading, naming,
// or menu selection. The pending load is resent from the jmol_isReady hook.
// The JSmol applet object is created by the parse-time inline script in
// mulermoc-nom-54.html (Jmol.getApplet must run during parsing). Only
// declare the binding if nothing assigned it yet — an unconditional
// `var ... = null` here would wipe the live applet (execution order:
// inline getApplet first, this file after).
try { if (typeof jmolAppletNomeclature === "undefined") jmolAppletNomeclature = null; } catch (eG) { /* best-effort */ }

function fJSmolLive() {
  try {
    if (typeof Jmol === "undefined" || !Jmol || !Jmol.__mulerSafe) return false;
    if (typeof jmolAppletNomeclature === "undefined" || !jmolAppletNomeclature) return false;
    if (typeof window !== "undefined" && window.JSmolReadyFlag !== true) return false;
    return true;
  } catch (e) { return false; }
}

function fMulerNotePending3D() {
  try {
    if (typeof selectedMol !== "undefined" && selectedMol) window.__mulerPending3D = selectedMol;
  } catch (e) { /* best-effort */ }
}

function fJSmolScript(applet, cmd) {
  fMolDraft3DWillScript(applet, cmd);
  fMuler3DWillScript(applet, cmd);
  if (!fJSmolLive()) { fMulerNotePending3D(); return null; }
  try { return Jmol.script(applet, cmd); } catch (e) { fMulerNotePending3D(); return null; }
}

function fJSmolScriptWait(applet, cmd) {
  fMolDraft3DWillScript(applet, cmd);
  fMuler3DWillScript(applet, cmd);
  if (!fJSmolLive()) { fMulerNotePending3D(); return null; }
  try { return Jmol.scriptWait(applet, cmd); } catch (e) { fMulerNotePending3D(); return null; }
}

function fJSmolScriptEcho(applet, cmd) {
  if (!fJSmolLive()) { fMulerNotePending3D(); return ""; }
  try { return Jmol.scriptEcho(applet, cmd); } catch (e) { fMulerNotePending3D(); return ""; }
}

function fJSmolGetPropertyAsArray(applet, prop, query) {
  if (!fJSmolLive()) { fMulerNotePending3D(); return null; }
  try { return Jmol.getPropertyAsArray(applet, prop, query); } catch (e) { fMulerNotePending3D(); return null; }
}

function fJSmolGetPropertyAsString(applet, prop) {
  if (!fJSmolLive()) { fMulerNotePending3D(); return null; }
  try { return Jmol.getPropertyAsString(applet, prop); } catch (e) { fMulerNotePending3D(); return null; }
}

function fJSmolResizeApplet(applet, dims) {
  if (!fJSmolLive()) return;
  try { Jmol.resizeApplet(applet, dims); } catch (e) { /* best-effort */ }
}

// Marks the real JSmol API as guarded (idempotent): after this, direct
// Jmol.* calls that slip through still fail closed instead of throwing.
function fMulerSafeJSmol() {
  try {
    if (typeof Jmol === "undefined" || !Jmol) return;
    if (Jmol.__mulerSafe) return;
    try {
      var _sc = Jmol.script, _sw = Jmol.scriptWait, _se = Jmol.scriptEcho,
        _gpa = Jmol.getPropertyAsArray, _gps = Jmol.getPropertyAsString, _rs = Jmol.resizeApplet;
      if (typeof _sc === "function") Jmol.script = function (a, c) {
        try { if (!fJSmolLive()) { fMulerNotePending3D(); return null; } return _sc(a, c); }
        catch (e) { fMulerNotePending3D(); return null; }
      };
      if (typeof _sw === "function") Jmol.scriptWait = function (a, c) {
        try { if (!fJSmolLive()) { fMulerNotePending3D(); return null; } return _sw(a, c); }
        catch (e) { fMulerNotePending3D(); return null; }
      };
      if (typeof _se === "function") Jmol.scriptEcho = function (a, c) {
        try { if (!fJSmolLive()) { fMulerNotePending3D(); return ""; } return _se(a, c); }
        catch (e) { fMulerNotePending3D(); return ""; }
      };
      if (typeof _gpa === "function") Jmol.getPropertyAsArray = function (a, p, q) {
        try { if (!fJSmolLive()) { fMulerNotePending3D(); return null; } return _gpa(a, p, q); }
        catch (e) { fMulerNotePending3D(); return null; }
      };
      if (typeof _gps === "function") Jmol.getPropertyAsString = function (a, p) {
        try { if (!fJSmolLive()) { fMulerNotePending3D(); return null; } return _gps(a, p); }
        catch (e) { fMulerNotePending3D(); return null; }
      };
      if (typeof _rs === "function") Jmol.resizeApplet = function (a, d) {
        try { if (!fJSmolLive()) return; return _rs(a, d); } catch (e) { /* best-effort */ }
      };
      Jmol.__mulerSafe = true;
    } catch (eI) { /* best-effort */ }
  } catch (e) { /* best-effort */ }
}

// The JSmol library loads synchronously at parse time (see the head script),
// so its API is present by the time this file runs. Install the fail-closed
// patches immediately: with a blocked/slow CDN the applet may not exist yet,
// and every JSmol call must degrade to a pending note instead of throwing.
try { if (typeof fMulerSafeJSmol === "function") fMulerSafeJSmol(); } catch (eW0) { /* best-effort */ }

function fLoadMol3D() {
  fMolDraft3DInvalidate();
  const selectedExample = nameExamples[selectedMol];
  if (!selectedExample) {
    return;
  }
  // A live load supersedes any pending cold-boot resend for an older molecule.
  try { if (typeof fJSmolLive === "function" && fJSmolLive()) window.__mulerPending3D = null; } catch (eP) {}
  // Hard failure (library itself missing, e.g. blocked CDN): say so once.
  // Transient unreadiness stays silent — the ready-hook resend covers it.
  try {
    if ((typeof Jmol === "undefined" || !Jmol) && !window.__mulerJSmolToasted) {
      window.__mulerJSmolToasted = true;
      try { if (typeof fScenarioToast === "function") fScenarioToast("3D unavailable (JSmol failed to load) — 2D continues to work."); } catch (eT) {}
      try { /* console.warn("[JSmol] library failed to load; 3D disabled for this session."); */ } catch (eC) {}
    }
  } catch (eW) { /* best-effort */ }

  var model = fMuler3DBeginLoad();
  var loadTail = 'javascript "window.__muler3DLoadDone(' + model.id + ')";';
  let myMol3D = selectedExample.file3D;
  // v54 Stage 2 accepted drafts: no file3D on disk — inline SDF text via
  // `load data` (blob: URLs are rejected by JSmol's file loader online).
  if (!myMol3D && selectedExample.sdf3D) {
    let movetoInline =
      selectedExample.hasOwnProperty("moveto") && selectedExample.moveto
        ? String(selectedExample.moveto).trim().replace(/;?\s*$/, "; ")
        : "";
    const initialZoomInline = selectedExample.initialZoom3D;
    const zoomInline = (!movetoInline && Number.isFinite(initialZoomInline) && initialZoomInline > 0)
      ? "zoom " + initialZoomInline + ";"
      : "";
    try {
      if (typeof fJSmolLoadInlineSDF === "function") {
        fMuler3DLoadWriter = model;
        try { fJSmolLoadInlineSDF(jmolAppletNomeclature, selectedExample.sdf3D,
          "script spt/init-57.spt;" + zoomInline + movetoInline + loadTail); }
        finally { fMuler3DLoadWriter = null; }
      }
    } catch (eInline) {}
    try { if (typeof fSetMolVis3D === "function") fSetMolVis3D(); } catch (eV) {}
    try {
      if (typeof MuLERMoCScenario !== "undefined") MuLERMoCScenario.reload3DOnce = false;
    } catch (eFlag) { /* flag best-effort */ }
    return;
  }
  if (!myMol3D) {
    return;
  }
  let movetoCmd =
    selectedExample.hasOwnProperty("moveto") && selectedExample.moveto
      ? String(selectedExample.moveto).trim().replace(/;?\s*$/, "; ")
      : "";
  // Optional model framing, applied after init-3.spt's shared zoom 50.
  // Later user zoom and scenario camera commands retain control.
  // IMPORTANT: init-3.spt ends with `zoom 50`, so a data-file moveto must run
  // AFTER it (moveto encodes its own zoom/orientation); when moveto is
  // present the generic initialZoom3D is skipped to avoid overwriting it.
  const initialZoom = selectedExample.initialZoom3D;
  const zoomCmd = (!movetoCmd && Number.isFinite(initialZoom) && initialZoom > 0)
    ? "zoom " + initialZoom + ";"
    : "";
  fMuler3DLoadWriter = model;
  try { fJSmolScript(
    jmolAppletNomeclature,
    "frank off;load " +
      myMol3D +
      "; select all; center selected;" +
      "script spt/init-57.spt;" + zoomCmd + movetoCmd + loadTail,
  ); } finally { fMuler3DLoadWriter = null; }
  fSetMolVis3D();
  // A fresh load satisfies any pending one-shot exit reload (e.g. molecule
  // picked while 3D hidden after a no-3D exit: already loaded, reopen is instant).
  try {
    if (typeof MuLERMoCScenario !== "undefined") MuLERMoCScenario.reload3DOnce = false;
  } catch (eFlag) {
    /* flag best-effort */
  }
}

// ── fFetchAndParse3D ──────────────────────────────────────────────────────

function fFetchAndParse3D() {
  if (!selectedMol || !nameExamples[selectedMol]) {
    return;
  }
  const model = fMuler3DModel;
  const mol = selectedMol; // source + generation guard below
  const url = nameExamples[selectedMol].file3D;
  // v54 Stage 2 accepted drafts: inline SDF, nothing to fetch.
  if (!url && nameExamples[selectedMol].sdf3D) {
    try {
      fParseSDF3D(nameExamples[selectedMol].sdf3D);
      fDetectMolType3D();
      fCalcMainChain3D();
      fMuler3DParsedSource(model, nameExamples[selectedMol].sdf3D);
    } catch (eInline) { /* 3D parse best-effort */ }
    try {
      if (typeof window.fScenarioOn3DParsed === "function") window.fScenarioOn3DParsed(mol);
    } catch (e) {
      /* scenario absent */
    }
    return;
  }
  fetch(url)
    .then(function (r) {
      if (!r.ok) throw new Error("3D source HTTP " + r.status);
      return r.text();
    })
    .then(function (text) {
      if (selectedMol !== mol || fMuler3DModel !== model || !model || model.source !== fMuler3DSourceKey()) {
        return;
      } // user navigated away
      fParseSDF3D(text);
      fDetectMolType3D();
      fCalcMainChain3D();
      fMuler3DParsedSource(model, text);
      // S2 scenario gate (additive, guarded): notify the scenario layer so a
      // per-step name highlight applies after 3D analysis exists. No-op when
      // the scenario module is absent or no step is pending.
      try {
        if (typeof window.fScenarioOn3DParsed === "function") window.fScenarioOn3DParsed(mol);
      } catch (e) {
        /* scenario absent */
      }
    })
    .catch(function (e) {
      // console.warn("[3D parse failed]", url, e);
    });
}

// ── showAtomSymbols3D ─────────────────────────────────────────────────────

function showAtomSymbols3D(restoreNumbering) {
  if (atomSymbols3DFlag) {
    fJSmolScript(
      jmolAppletNomeclature,
      "select all; labels %e;" + JmolSelection + ";",
    );
  } else {
    fJSmolScript(
      jmolAppletNomeclature,
      "select all; labels off;" + JmolSelection + ";",
    );
  }

  if (restoreNumbering !== false && nameAnalysisMode == "compCarbonsCount") {
    fShowNumbering3D();
  }
}

// ── showHydrogens3D ─────────────────────────────────────────────────────

function showHydrogens3D() {
  if (hydrogens3DFlag) {
    fJSmolScript(jmolAppletNomeclature, "hide none;");
  } else {
    fJSmolScript(
      jmolAppletNomeclature,
      "select _H and connected(_C); hide selected;" + JmolSelection + ";",
    );
  }

  if (nameAnalysisMode == "compCarbonsCount") {
    fShowNumbering3D();
  }
}

// ── rotate3D ─────────────────────────────────────────────────────────────

function rotate3D() {
  if (rotateFlag) {
    fJSmolScript(jmolAppletNomeclature, "rotate spin 60;");
  } else {
    fJSmolScript(jmolAppletNomeclature, "rotate  off;");
  }
}

// ── fGetNameBoxes ─────────────────────────────────────────────────────────

function fGetNameBoxes() {
  return Array.from(
    document.querySelectorAll(".nameCompContainer .nameCompBox"),
  )
    .map(function (el) {
      return {
        text: el.textContent.trim(),
        selected: el.classList.contains("selected"),
      };
    })
    .filter(function (b) {
      return b.text;
    });
}

// ── fDrawNameBoxes ────────────────────────────────────────────────────────

function fDrawNameBoxes(ctx, nameBoxes, canvasWidth, yTop) {
  if (!nameBoxes.length) return;
  let font = "bold 40px Arial, sans-serif";
  ctx.font = font;
  let pad = 18;
  let boxH = 60;
  let gap = -2; // boxes overlap border like CSS margin-right: -2px
  let totalW =
    nameBoxes.reduce(function (acc, b) {
      return acc + ctx.measureText(b.text).width + pad * 2;
    }, 0) +
    gap * (nameBoxes.length - 1);
  let x = Math.round((canvasWidth - totalW) / 2);
  let y = yTop + 10;
  nameBoxes.forEach(function (b) {
    let tw = ctx.measureText(b.text).width;
    let bw = Math.round(tw + pad * 2);
    ctx.fillStyle = b.selected ? "#5FAD56" : "#ffffff";
    ctx.fillRect(x, y, bw, boxH);
    ctx.strokeStyle = b.selected ? "#5FAD56" : "#dddddd";
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, bw, boxH);
    ctx.fillStyle = b.selected ? "#ffffff" : "#000000";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText(b.text, x + pad, y + boxH / 2);
    x += bw + gap;
  });
}

// ── fSave2DPng ────────────────────────────────────────────────────────────

window.fSave2DPng = function () {
  let svgEl = document.querySelector("#jsmeNomeclatureSVG svg");
  if (!svgEl) return;
  let nameBoxes = fGetNameBoxes();
  let bbox = svgEl.getBoundingClientRect();
  let srcWidth = bbox.width || 450;
  let srcHeight = bbox.height || 200;
  let width = 1200;
  let molHeight = Math.round(srcHeight * (width / srcWidth));
  let labelHeight = nameBoxes.length ? 90 : 0;

  let svgClone = svgEl.cloneNode(true);
  svgClone.setAttribute("width", srcWidth);
  svgClone.setAttribute("height", srcHeight);

  // Export uses a serialized standalone SVG blob, so page CSS selectors are
  // not available there. Inline unchecked atom-color mode directly.
  if (
    !document
      .querySelector("#jsmeNomeclatureSVG")
      ?.classList.contains("svgAtomsColorized")
  ) {
    svgClone
      .querySelectorAll(
        'text:not([id^="number"]), text:not([id^="number"]) tspan',
      )
      .forEach(function (el) {
        el.setAttribute("fill", "#000");
      });
  }

  // Defensive scrub: highlighted malformed labels may leak broken stroke-width
  // values (with absorbed tag text) into export serialization.
  svgClone.querySelectorAll("[stroke-width]").forEach(function (el) {
    let strokeWidthValue = el.getAttribute("stroke-width") || "";
    if (/[<>]|&(lt|gt);|tspan|stroke=/i.test(strokeWidthValue)) {
      let safeStrokeWidth = strokeWidthValue
        .split("&gt;")[0]
        .split(">")[0]
        .split("&lt;")[0]
        .split("<")[0]
        .trim();
      if (/^\d+(\.\d+)?(px)?$/i.test(safeStrokeWidth)) {
        el.setAttribute("stroke-width", safeStrokeWidth);
      } else {
        el.removeAttribute("stroke-width");
      }
      el.removeAttribute("stroke");
    }
  });

  let svgData = new XMLSerializer().serializeToString(svgClone);
  if (!svgData.includes('xmlns="http://www.w3.org/2000/svg"')) {
    svgData = svgData.replace(
      "<svg",
      '<svg xmlns="http://www.w3.org/2000/svg"',
    );
  }

  // Fix JSME bug: highlighted atom labels produce malformed XML.
  svgData = svgData.replace(
    /fill="([^"]*?)\s+stroke="\s*([^"]*?)"\s*=\s*"\s+stroke-width="([^"]*)"/g,
    'fill="$1" stroke="$2" stroke-width="$3"',
  );

  // Fix N-type highlight corruption: stroke-width can absorb escaped/literal
  // fragments (e.g. &gt;&lt;tspan&gt;...) and break SVG image decode.
  svgData = svgData.replace(/stroke-width="([^"]*)"/g, function (_m, value) {
    if (!/(?:&gt;|&lt;|>|<|tspan|stroke=)/i.test(value)) {
      return 'stroke-width="' + value + '"';
    }
    let safeValue = value
      .split("&gt;")[0]
      .split(">")[0]
      .split("&lt;")[0]
      .split("<")[0]
      .trim();
    if (!/^\d+(\.\d+)?(px)?$/i.test(safeValue)) {
      return "";
    }
    return 'stroke-width="' + safeValue + '"';
  });

  // Remove orphaned encoded tspan tags left inside attribute contexts.
  svgData = svgData.replace(/&lt;\/?tspan[^&]*?&gt;/gi, "");

  // Fix another JSME highlight corruption variant seen in <text> tags:
  //   ... fill="#000" black"="" stroke-width="11px" ...
  // Remove orphan attributes ending as: <token>"=""
  svgData = svgData.replace(
    /\s+[A-Za-z_:-][A-Za-z0-9_:\-\.]*"=""(?=\s|>)/g,
    "",
  );

  let svgDebugFlags = {
    hasMalformedFillStroke: /fill="[^"]*?\s+stroke="\s*[^"]*?"\s*=\s*"/i.test(
      svgData,
    ),
    hasCorruptStrokeWidth:
      /stroke-width="[^"]*(?:&gt;|&lt;|>|<|tspan|stroke=)/i.test(svgData),
    hasEncodedTspan: /&lt;\/?tspan/i.test(svgData),
    hasOrphanQuotedAttribute:
      /\s+[A-Za-z_:-][A-Za-z0-9_:\-\.]*"=""(?=\s|>)/.test(svgData),
  };

  let canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = molHeight + labelHeight;
  let ctx = canvas.getContext("2d");
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  let img = new Image();
  img.onload = function () {
    ctx.drawImage(img, 0, 0, width, molHeight);
    fDrawNameBoxes(ctx, nameBoxes, width, molHeight);
    canvas.toBlob(function (blob) {
      if (!blob) {
        // console.error("2D PNG: toBlob returned null");
        return;
      }
      let a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download =
        (currentMolName || selectedMol || "molecule").replace(/\s+/g, "_") +
        "_2D.png";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(a.href);
    });
  };
  img.onerror = function () {
    // console.error("[2D PNG] SVG failed to load. SVG content:");
    // console.error(svgData.slice(0, 4000));
    // console.error("[2D PNG] Debug flags:", svgDebugFlags);
  };

  let svgBlob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
  img.src = URL.createObjectURL(svgBlob);
};

// ── fSaveJmolPng ──────────────────────────────────────────────────────────

window.fSaveJmolPng = function () {
  let baseName = (currentMolName || selectedMol || "molecule").replace(
    /\s+/g,
    "_",
  );
  let safeLabel = (currentMolName || "").replace(/'/g, "");

  fJSmolScript(
    jmolAppletNomeclature,
    "set echo  bottom center; color echo black; font echo 24 ; echo " +
      safeLabel +
      "|| ;" +
      "write IMAGE 1200 1200 PNG '" +
      baseName +
      "_3D.png';",
  );
  setTimeout(function () {
    fJSmolScript(jmolAppletNomeclature, "set echo off;");
  }, 500);
};

// ── fShowNameAnalysis ─────────────────────────────────────────────────────

// Fit the complete name without wrapping or changing its component IDs.
// Main can tighten overflowing box padding before shrinking label/separator fonts.
var nameFitFrame = null;
var nameFitObserver = null;
var nameFitPanel = null;
var nameFitFontsBound = false;
function fFitNameToWidth() {
  if (window.nameExpanded) return;
  const host = document.querySelector("#nameAnalysis .nameContainer");
  const row = host && host.querySelector(".nameCompContainer");
  if (!row || !host.getClientRects().length || host.clientWidth <= 0) return;
  const style = getComputedStyle(host);
  const available = host.clientWidth - parseFloat(style.paddingLeft || 0)
    - parseFloat(style.paddingRight || 0) - 4;
  if (available <= 0) return;
  row.classList.remove("nl-name-tight");
  row.style.setProperty("--nl-name-scale", "1");
  if (row.getBoundingClientRect().width <= available) return;
  if (document.documentElement.dataset.nameleculeCompactNamePadding === "true") {
    row.classList.add("nl-name-tight");
    if (row.getBoundingClientRect().width <= available) return;
  }
  let low = 0, high = 1;
  for (let i = 0; i < 12; i++) {
    const mid = (low + high) / 2;
    row.style.setProperty("--nl-name-scale", String(mid));
    if (row.getBoundingClientRect().width <= available) low = mid;
    else high = mid;
  }
  row.style.setProperty("--nl-name-scale", String(low));
}
function fScheduleNameFit() {
  const panel = document.getElementById("nameAnalysisContainer");
  if (panel && panel !== nameFitPanel && typeof ResizeObserver !== "undefined") {
    if (nameFitObserver) nameFitObserver.disconnect();
    nameFitPanel = panel;
    let lastWidth = -1;
    nameFitObserver = new ResizeObserver(function (entries) {
      const width = entries[0].contentRect.width;
      // Font changes alter height; observing only width avoids resize loops.
      if (width === lastWidth) return;
      lastWidth = width;
      fScheduleNameFit();
    });
    nameFitObserver.observe(panel);
  }
  if (!nameFitFontsBound && document.fonts) {
    nameFitFontsBound = true;
    document.fonts.ready.then(fScheduleNameFit);
    document.fonts.addEventListener("loadingdone", fScheduleNameFit);
  }
  if (nameFitFrame !== null) cancelAnimationFrame(nameFitFrame);
  nameFitFrame = requestAnimationFrame(function () {
    nameFitFrame = null;
    fFitNameToWidth();
  });
}

function fFitNameComponents() {
  fScheduleNameFit();
}

// Keep the upstream public initializer on the same observer/fitter owner.
function fInitNameFitObserver() {
  fScheduleNameFit();
}

// ── Expanded-name floating overlay ────────────────────────────────────────
// Non-modal: the existing boxes are restyled in place (same nodes, so all
// clicks/eyes/narration keep working); the app underneath stays fully live.
// Close contract: toggle button, Esc, or a rebuild for another molecule.

function fNameExpandOpen() {
  var cont = null;
  try { cont = document.querySelector("#nameAnalysis .nameCompContainer"); } catch (eC) { cont = null; }
  if (!cont || !selectedMol) return;
  window.nameExpanded = true;
  window.expandedMol = selectedMol;
  try {
    cont.style.setProperty("--nameCompScale", "1");
    cont.style.setProperty("--nl-name-scale", "1");
    cont.classList.remove("nl-name-tight");
    var parent = cont.parentElement;
    if (parent) parent.classList.remove("nameOverflow");
    var host = document.getElementById("nameAnalysisContainer");
    if (host) { host.classList.add("nameExpanded"); host.style.minHeight = ""; }
    try { fNameExplainPortalIn(); } catch (eP) { /* best-effort */ }
    var explain = document.getElementById("nameAnalysisExplain");
    if (explain) explain.classList.add("nameExplainExpanded");
    cont.setAttribute("role", "dialog");
    cont.setAttribute("aria-label", (typeof fMulerT === "function") ? fMulerT("fullName") : "Πλήρες όνομα");
    var btn = document.getElementById("nameExpandBtn");
    if (btn) { btn.classList.add("active"); btn.setAttribute("aria-expanded", "true"); }
    try { fNameExpandPaintBtn(); } catch (eP) { /* best-effort */ }
    try { fNameExpandReserve(); } catch (eR) { /* best-effort */ }
    try { fNameExplainAnchor(); } catch (eA) { /* best-effort */ }
  } catch (eO) { /* best-effort */ }
}

// Portal: while expanded, #nameAnalysisExplain lives inside
// #nameAnalysisContainer (same containing block as the name sheet) so its
// right anchor matches the sheet and it can extend left outside analysisCol.
var _nameExplainPlaceholder = null;
function fNameExplainPortalIn() {
  var host = null, explain = null;
  try { host = document.getElementById("nameAnalysisContainer"); } catch (eH) { host = null; }
  try { explain = document.getElementById("nameAnalysisExplain"); } catch (eE) { explain = null; }
  if (!host || !explain) return;
  if (explain.parentElement === host) return;
  try {
    _nameExplainPlaceholder = document.createComment("nameExplainAnchor");
    explain.parentNode.insertBefore(_nameExplainPlaceholder, explain);
    host.appendChild(explain);
  } catch (eP) { /* best-effort */ }
}
function fNameExplainPortalOut() {
  var explain = null;
  try { explain = document.getElementById("nameAnalysisExplain"); } catch (eE) { explain = null; }
  if (!explain) { _nameExplainPlaceholder = null; return; }
  try { explain.style.top = ""; explain.style.width = ""; } catch (eS) { /* best-effort */ }
  try {
    if (_nameExplainPlaceholder && _nameExplainPlaceholder.parentNode) {
      _nameExplainPlaceholder.parentNode.insertBefore(explain, _nameExplainPlaceholder);
      _nameExplainPlaceholder.parentNode.removeChild(_nameExplainPlaceholder);
    } else if (explain.parentElement) {
      var host = document.getElementById("nameAnalysisContainer");
      if (host && host.parentNode && explain.parentElement !== host.parentNode) {
        if (host.nextSibling) host.parentNode.insertBefore(explain, host.nextSibling);
        else host.parentNode.appendChild(explain);
      }
    }
  } catch (eP) { /* best-effort */ }
  _nameExplainPlaceholder = null;
}

// Height reserve: both sheets are absolute (out of flow). Pin #nameAnalysis
// min-height to sheet + gap + Explain so Explain floats just below the name
// sheet and #ruleTheoryContainer/footer stay below the stack.
function fNameExpandReserve() {
  if (!window.nameExpanded) return;
  try {
    var cont = document.querySelector("#nameAnalysis .nameCompContainer");
    if (!cont) return;
    var parent = cont.parentElement;
    if (!parent) return;
    var host = document.getElementById("nameAnalysisContainer");
    var explain = document.getElementById("nameAnalysisExplain");
    // Keep Explain in the same containing block as the sheet.
    try {
      if (explain && host && explain.parentElement !== host) fNameExplainPortalIn();
    } catch (eP) { /* best-effort */ }
    var sheetH = 0, sheetW = 0;
    try { sheetH = Math.ceil(cont.offsetHeight); } catch (eH) { sheetH = 0; }
    try { sheetW = Math.ceil(cont.offsetWidth); } catch (eW) { sheetW = 0; }
    // Robust top: rect math (immune to offsetParent/static-position quirks).
    var topPx = null;
    try {
      if (host && cont.getBoundingClientRect && host.getBoundingClientRect) {
        var hostRect = host.getBoundingClientRect();
        var sheetRect = cont.getBoundingClientRect();
        if (hostRect && sheetRect) topPx = Math.round(sheetRect.bottom - hostRect.top - 1);
      }
    } catch (eR) { topPx = null; }
    var explainH = 0;
    if (explain) {
      try {
        if (sheetW > 0) explain.style.width = sheetW + "px";
        // Rect-only: the (sheetH - 1) fallback ignored #ruleTheory height and
        // misplaced Explain by exactly that amount. If rect math is
        // unavailable, keep the previous top instead of guessing.
        if (topPx !== null && topPx >= 0) explain.style.top = topPx + "px";
        void explain.offsetHeight;
        explainH = Math.ceil(explain.offsetHeight);
      } catch (eE) { explainH = 0; }
    }
    var total = sheetH - 1 + explainH + 6;
    if (total > 0) parent.style.minHeight = total + "px";
  } catch (eR) { /* best-effort */ }
}

// Explain anchor (expanded mode): shrink-wrapped Explain box centers under
// the selected name component. Overlay is right-anchored + scrollable, so
// the selected box center is measured live via getBoundingClientRect and the
// Explain offset is clamped to the Explain row. No selection docks left.
function fNameExplainAnchor() {
  var wrap = null;
  try { wrap = document.getElementById("nameAnalysisExplain"); } catch (eW) { wrap = null; }
  if (!wrap) return;
  var tip = null;
  try { tip = wrap.querySelector(".explainText"); } catch (eQ) { tip = null; }
  if (!tip) return;
  if (!window.nameExpanded) {
    try { tip.style.marginLeft = ""; } catch (eC) { /* best-effort */ }
    return;
  }
  var sel = null;
  try { sel = document.querySelector("#nameAnalysis .nameCompBox.selected"); } catch (eS) { sel = null; }
  try { tip.style.marginLeft = "0px"; } catch (eM) { /* best-effort */ }
  if (!sel) return;
  try {
    var wrapRect = wrap.getBoundingClientRect();
    var selRect = sel.getBoundingClientRect();
    var tipW = tip.offsetWidth || tip.getBoundingClientRect().width || 0;
    var wrapW = wrap.clientWidth || wrapRect.width || 0;
    if (!(tipW > 0) || !(wrapW > 0)) return;
    var center = (selRect.left - wrapRect.left) + selRect.width / 2;
    var left = Math.round(center - tipW / 2);
    if (wrapW > tipW) left = Math.max(0, Math.min(left, wrapW - tipW));
    else left = 0;
    tip.style.marginLeft = left + "px";
  } catch (eA) { /* best-effort */ }
}

function fNameExpandClose(refit) {
  if (!window.nameExpanded) return;
  window.nameExpanded = false;
  window.expandedMol = null;
  try {
    var host = document.getElementById("nameAnalysisContainer");
    if (host) { host.classList.remove("nameExpanded"); host.style.minHeight = ""; }
    var explain = document.getElementById("nameAnalysisExplain");
    if (explain) {
      explain.classList.remove("nameExplainExpanded");
      try {
        var _tip = explain.querySelector(".explainText");
        if (_tip) _tip.style.marginLeft = "";
      } catch (eT) { /* best-effort */ }
      try { fNameExplainPortalOut(); } catch (eP) { /* best-effort */ }
    }
    var cont = document.querySelector("#nameAnalysis .nameCompContainer");
    if (cont) { cont.removeAttribute("role"); if (cont.parentElement) cont.parentElement.style.minHeight = ""; }
    var btn = document.getElementById("nameExpandBtn");
    if (btn) { btn.classList.remove("active"); btn.setAttribute("aria-expanded", "false"); }
    try { fNameExpandPaintBtn(); } catch (eP) { /* best-effort */ }
  } catch (eC) { /* best-effort */ }
  if (refit !== false) {
    try { fFitNameComponents(); } catch (eF) { /* best-effort */ }
    try { fNameExpandSync(); } catch (eS) { /* best-effort */ }
  }
}

// Toggle-button visibility: only when the name is actually shrunk or
// scrolled (or already expanded). Runs after every render + open/close.
function fNameExpandSync() {
  var btn = null;
  try { btn = document.getElementById("nameExpandBtn"); } catch (eB) { btn = null; }
  if (!btn) return;
  var show = !!window.nameExpanded;
  if (!show) {
    try {
      var cont = document.querySelector("#nameAnalysis .nameCompContainer");
      var parent = cont && cont.parentElement;
      var scale = cont ? parseFloat(cont.style.getPropertyValue("--nameCompScale") || "1") : 1;
      show = !!selectedMol &&
        !!((parent && parent.classList.contains("nameOverflow")) || scale < 1);
    } catch (eS) { show = false; }
  }
  try {
    if (show) btn.removeAttribute("hidden");
    else btn.setAttribute("hidden", "");
    btn.classList.toggle("active", !!window.nameExpanded);
    btn.setAttribute("aria-expanded", window.nameExpanded ? "true" : "false");
  } catch (eA) { /* best-effort */ }
  try { fNameExpandPaintBtn(); } catch (eP) { /* best-effort */ }
}

// Expand-button icon/tooltip follow state — same fullScreen pair as the
// note editor expand/close buttons (fallback: legacy expand glyph).
function fNameExpandPaintBtn() {
  var btn = null;
  try { btn = document.getElementById("nameExpandBtn"); } catch (eB) { btn = null; }
  if (!btn) return;
  var open = !!window.nameExpanded;
  var icon = "";
  try {
    if (window.MuLERIcons) {
      icon = open ? (window.MuLERIcons.fullScreenExit || "") : (window.MuLERIcons.fullScreen || "");
    }
    if (!icon && typeof svgNameExpand !== "undefined") icon = svgNameExpand;
  } catch (eI) { icon = ""; }
  var tip = open ? ((typeof fMulerT === "function") ? fMulerT("exitFullName") : "Έξοδος από το πλήρες όνομα") : ((typeof fMulerT === "function") ? fMulerT("fullName") : "Πλήρες όνομα");
  try {
    btn.innerHTML = icon;
    btn.setAttribute("data-tooltip", tip);
    btn.setAttribute("aria-label", tip);
  } catch (eA) { /* best-effort */ }
}

// ── fShowNameAnalysis ─────────────────────────────────────────────────────

// Displayed EN name for verdicts: systematic variant when the
// Traditional/Systematic toggle selects it and it differs, else school engineEN.
function fDisplayedEngineEN(key) {
  try {
    if (typeof nameExamples === "undefined" || !key || !nameExamples[key]) return null;
    var _e = nameExamples[key];
    if (typeof substNamingMode !== "undefined" && substNamingMode === "sys" && _e.engineEN_sys) return _e.engineEN_sys;
    return _e.engineEN || null;
  } catch (eD) { return null; }
}

// EN verdict for the name marker ("oracle"|"fallback"|"mismatch"|"nooracle"|"noerror"|null).
// fetched=true skips the pending-fetch grace (used by the fetch-completion hook).
function fMulerVerdictState(key, fetched, engOverride) {
  try {
    if (typeof fMulerLang === "function" && fMulerLang() !== "en") return null;
    if (typeof nameExamples === "undefined" || !key || !nameExamples[key]) return null;
    var ex = nameExamples[key];
    var _eng = (typeof engOverride !== "undefined" && engOverride !== null) ? engOverride : null;
    if (_eng == null && typeof fDisplayedEngineEN === "function") { try { _eng = fDisplayedEngineEN(key); } catch (eD2) {} }
    var boxesEN = false;
    try {
      var r = (typeof fNameENBoxes === "function") ? fNameENBoxes() : null;
      boxesEN = !!(r && r.boxes && r.boxes.length);
    } catch (eB) { boxesEN = false; }
    if (!boxesEN) return "fallback";
    if (ex.engineDelegated) return "oracle";
    if (typeof fMatchEngineEN !== "function") return null;
    var v = fMatchEngineEN(key, _eng);
    // Merged plain rule (owner choice): either oracle agreeing with the
    // predicted name silences red. OC data comes from fMatchEngineEN_OC.
    var ocS = "missing";
    try {
      if (typeof fMatchEngineEN_OC === "function") ocS = fMatchEngineEN_OC(key, _eng).status || "missing";
    } catch (eOCs) { ocS = "missing"; }
    if (ocS === "match") return null;
    if (v.status === "mismatch") return "mismatch";
    if (v.status === "missing") {
      if (ocS === "mismatch") return "mismatch";
      var pend = false, done = false, err = false;
      try { pend = !!(typeof window !== "undefined" && window.__mulerIupacPending && window.__mulerIupacPending[key]); } catch (eP) {}
      try { done = !!ex.iupacFetchDone; err = !!ex.iupacFetchError; } catch (eD) {}
      if (fetched || (done && !pend)) return err ? "noerror" : "nooracle";
    }
    return null;
  } catch (e) { return null; }
}

// In-place verdict repaint (no rebuild: preserves focus, scroll, selection).
function fMulerApplyVerdict(key, fetched, engOverride) {
  try {
    if (typeof selectedMol === "undefined" || selectedMol !== key) return null;
    var cont = document.querySelector("#nameAnalysis .nameCompContainer");
    if (!cont) return null;
    var st = (typeof fMulerVerdictState === "function") ? fMulerVerdictState(key, fetched, engOverride) : null;
    cont.classList.remove("oracle-name", "verdict-oracle", "verdict-fallback", "verdict-mismatch", "verdict-nooracle", "verdict-noerror");
    cont.removeAttribute("title");
    if (!st) return null;
    // Ether common-name fallback (live only): the shared comparator checks the
    // systematic engine name, so a school-retained common name can mismatch
    // while still being valid. If the locally built common name matches the
    // PubChem title, show plain instead of red. Batch validation is untouched.
    if (st === "mismatch") {
      try {
        var _ex = (typeof nameExamples !== "undefined") ? nameExamples[key] : null;
        var _isEth = !!(_ex && _ex.classification && _ex.classification.chemicalClass === "ethers");
        if (_isEth && typeof fMulerENCommonName === "function" && _ex && _ex.titlePubchem) {
          var _cn = fMulerENCommonName();
          var _norm = function (s) { return String(s == null ? "" : s).toLowerCase().trim(); };
          if (_cn && _norm(_cn) === _norm(_ex.titlePubchem)) {
            var _ctip = "Common name matches PubChem — systematic form differs by school convention";
            try { if (typeof fMulerT === "function") _ctip = fMulerT("commonMatchTip"); } catch (eT2) { /* fallback above */ }
            try { cont.setAttribute("title", _ctip); } catch (eA2) { /* best-effort */ }
            try { /* console.log("[EN-CHECK] " + key + ": common name matches PubChem title — plain (systematic mismatch kept for review)"); */ } catch (eL) {}
            return "common";
          }
        }
      } catch (eC) { /* fall through to mismatch */ }
    }
    var tipMap = { oracle: "oracleNameTip", fallback: "greekFallbackTip", mismatch: "enMismatchTip", nooracle: "enNoOracleTip", noerror: "enNoErrorTip" };
    var tipFall = {
      oracle: "Name from the PubChem oracle — pending human review",
      fallback: "No engine English name — showing Greek",
      mismatch: "Engine name differs from PubChem IUPAC — pending human review",
      nooracle: "No PubChem/CIR data to validate against",
      noerror: "Oracle lookup failed (network) — not validated"
    };
    var tip = tipFall[st] || tipFall.oracle;
    try { if (typeof fMulerT === "function") tip = fMulerT(tipMap[st] || "oracleNameTip"); } catch (eT) {}
    cont.classList.add("oracle-name", "verdict-" + st);
    cont.setAttribute("title", tip);
    return st;
  } catch (e) { return null; }
}

// Oracle fetch completion: log predicted vs displayed, repaint the verdict
// in place (no rebuild). Skipped unless the fetched molecule is on screen.
function fMulerENFetchDone(key) {
  try {
    if (typeof selectedMol === "undefined" || selectedMol !== key) return;
    var isEN = false;
    try { isEN = (typeof fMulerLang === "function" && fMulerLang() === "en"); } catch (eL) {}
    if (!isEN) return;
    var _dsp = null;
    try { if (typeof fDisplayedEngineEN === "function") _dsp = fDisplayedEngineEN(key); } catch (eDsp) {}
    var st = (typeof fMulerApplyVerdict === "function") ? fMulerApplyVerdict(key, true, _dsp) : null;
    // Re-assert the OC marker: the PubChem repaint above resets the container
    // title, which would otherwise drop the OC sentence (classes survive).
    try { if (typeof fMulerApplyOCVerdict === "function") fMulerApplyOCVerdict(key, _dsp); } catch (eOC) {}
    var predicted = "", displayed = "";
    try {
      if (typeof nameExamples !== "undefined" && nameExamples[key]) predicted = _dsp || nameExamples[key].engineEN || "";
    } catch (eP) {}
    try {
      var parts = [];
      document.querySelectorAll("#nameAnalysis .nameCompBox").forEach(function (b) { parts.push((b.textContent || "").trim()); });
      displayed = parts.join(" ").replace(/\s+/g, " ").trim();
    } catch (eD) {}
    var via = "";
    try {
      if (typeof nameExamples !== "undefined" && nameExamples[key] && nameExamples[key].engineMatchVia) via = " via " + nameExamples[key].engineMatchVia;
      else if (typeof fMatchEngineEN === "function") { var _r = fMatchEngineEN(key, _dsp); if (_r && _r.via) via = " via " + _r.via; }
    } catch (eV) {}
    // console.log("[EN-CHECK] " + key + ": predicted=\"" + predicted + "\" displayed=\"" + displayed + "\" verdict=" + (st || "plain") + via);
  } catch (e) { /* best-effort */ }
}

// Second-oracle (OpenClatura) verdict data: EN-only; null outside EN or
// without a molecule. States match|mismatch|missing (no OC data yet — pending
// and unnameable share the state, the tip tells them apart via openclaturaDone;
// transport errors are a separate "error" state via openclaturaErr).
function fMulerOCVerdict(key, engOverride) {
  try {
    if (typeof fMulerLang === "function" && fMulerLang() !== "en") return null;
    if (typeof nameExamples === "undefined" || !key || !nameExamples[key]) return null;
    var ex = nameExamples[key];
    var _eng = (typeof engOverride !== "undefined" && engOverride != null) ? engOverride : null;
    if (_eng == null && typeof fDisplayedEngineEN === "function") { try { _eng = fDisplayedEngineEN(key); } catch (eDsp) {} }
    if (_eng == null) _eng = ex.engineEN;
    if (!_eng) return null;
    var r = (typeof fMatchEngineEN_OC === "function") ? fMatchEngineEN_OC(key, _eng) : null;
    if (!r || r.status === "missing") {
      var done = false, failed = false;
      try { done = !!ex.openclaturaDone; } catch (eD) {}
      try { failed = !!ex.openclaturaErr; } catch (eE) {}
      if (done && failed) {
        var tipE = "OpenClatura lookup failed (network) — not validated";
        try { if (typeof fMulerT === "function") tipE = fMulerT("ocErrorTip"); } catch (eT0) {}
        return { state: "error", tip: tipE };
      }
      var tipM = "Looking up OpenClatura…", tkM = "ocPendingTip";
      if (done) { tipM = "No OpenClatura answer"; tkM = "ocMissingTip"; }
      try { if (typeof fMulerT === "function") tipM = fMulerT(tkM); } catch (eT) {}
      return { state: "missing", tip: tipM };
    }
    var tk = (r.status === "match") ? "ocMatchTip" : "ocMismatchTip";
    var tipF = (r.status === "match")
      ? "OpenClatura agrees with the engine name"
      : "Engine name differs from OpenClatura — pending human review";
    try { if (typeof fMulerT === "function") tipF = fMulerT(tk); } catch (eT2) {}
    return { state: r.status, tip: tipF + (r.oracle ? " — " + r.oracle : "") };
  } catch (e) { return null; }
}

// In-place OC repaint (no rebuild): container outline classes + combined
// tooltip. Runs after fMulerApplyVerdict (which owns the PubChem classes and
// resets the title), so the two markers compose instead of clobbering.
function fMulerApplyOCVerdict(key, engOverride) {
  try {
    if (typeof selectedMol === "undefined" || selectedMol !== key) return null;
    var cont = document.querySelector("#nameAnalysis .nameCompContainer");
    if (!cont) return null;
    try { cont.classList.remove("verdict-oc-match", "verdict-oc-mismatch", "verdict-oc-missing", "verdict-oc-error"); } catch (eR) {}
    var v = (typeof fMulerOCVerdict === "function") ? fMulerOCVerdict(key, engOverride) : null;
    if (!v || !v.state) return null;
    // OR rule (owner choice): either oracle agreeing silences the tint. The
    // PubChem pass already goes quiet on OC-match (fMulerVerdictState); mirror
    // it here — a plain PubChem side suppresses the OC mismatch/missing/error
    // outline so e.g. propanedioic acid renders white/correct. fMulerVerdictState
    // is the single source of truth (null = plain for systematic/retained/title
    // agreement); the OC disagreement stays on record (console log,
    // info-panel row, REVIEW tables), just untinted.
    if (v.state === "mismatch" || v.state === "missing" || v.state === "error") {
      try {
        if (typeof fMulerVerdictState === "function" && fMulerVerdictState(key, true, engOverride) == null) return null;
      } catch (ePC) { /* fall through to the OC marker */ }
    }
    try { cont.classList.add("verdict-oc-" + v.state); } catch (eC) {}
    try {
      var t = "";
      try { t = cont.getAttribute("title") || ""; } catch (eG) {}
      t = String(t).split(" | ")[0];
      cont.setAttribute("title", (t ? t + " | " : "") + "OC: " + v.tip);
    } catch (eT) {}
    return v.state;
  } catch (e) { return null; }
}

// OC fetch completion: repaint the second marker in place + log. Skipped
// unless the fetched molecule is on screen (same guard as the PubChem hook).
// Recomputes the PubChem marker FIRST: a build-time red goes stale once OC
// data lands (merge rule), and only a full recompute removes it.
function fMulerOCFetchDone(key) {
  try {
    if (typeof selectedMol === "undefined" || selectedMol !== key) return;
    var isEN = false;
    try { isEN = (typeof fMulerLang === "function" && fMulerLang() === "en"); } catch (eL) {}
    if (!isEN) return;
    var _dsp = null;
    try { if (typeof fDisplayedEngineEN === "function") _dsp = fDisplayedEngineEN(key); } catch (eDsp) {}
    try { if (typeof fMulerApplyVerdict === "function") fMulerApplyVerdict(key, true, _dsp); } catch (eV) {}
    var ost = (typeof fMulerApplyOCVerdict === "function") ? fMulerApplyOCVerdict(key, _dsp) : null;
    var predicted = "", oc = "";
    try {
      if (typeof nameExamples !== "undefined" && nameExamples[key]) predicted = _dsp || nameExamples[key].engineEN || "";
    } catch (eP) {}
    try {
      if (typeof nameExamples !== "undefined" && nameExamples[key]) oc = nameExamples[key].openclaturaEN || "";
    } catch (eO) {}
    // console.log("[EN-CHECK-OC] " + key + ": predicted=\"" + predicted + "\" openclatura=\"" + oc + "\" verdict=" + (ost || "plain"));
  } catch (e) { /* best-effort */ }
}

// ── Greek systematic substituent variant (v54.31) ─────────────────────────
// Common -> systematic Greek (school retained -> substitutive): renders behind
// the Κοινή|Συστηματική toggle (GR only), sharing substNamingMode with the EN
// Traditional/Systematic toggle. Render-time transform of the common slots —
// fGuessName slots stay common, so the v54.30 staleness class cannot recur
// (no stored variant; always computed from the current chain).
// Word forms: 2-προπανυλο- pattern user-confirmed; rule-derived siblings
// flagged for P3 (same gate as v54.23). tert-βουτυλο mapped since v54.38
// (didactic override like EN: fully substitutive construction for teaching,
// even though tert-butyl is the preferred prefix).
var GR_SYST_SUBST = {
  "ισοπροπυλο": "προπαν-2-υλο",
  "ισοβουτυλο": "2-μεθυλοπροπυλο",
  "sec-βουτυλο": "βουταν-2-υλο",
  "tert-βουτυλο": "2-μεθυλοπροπαν-2-υλο",
  "ισοπροποξυ": "προπαν-2-υλοξυ",
  "sec-βουτοξυ": "βουταν-2-υλοξυ",
  "ισοπροπυλ": "προπαν-2-υλ",
  "ισοβουτυλ": "2-μεθυλοπροπυλ",
  "sec-βουτυλ": "βουταν-2-υλ",
  "tert-βουτυλ": "2-μεθυλοπροπαν-2-υλ"
};
// One common stem -> systematic (with P-16.3.4(a)-analogue parens when the
// mapped name carries a locant digit and the group is multiplied). Bare
// groups stay bare; unknown stems pass through unchanged. Idempotent:
// re-transforming systematic text is the identity.
function fGRSystOneStem(w) {
  try {
    if (Object.prototype.hasOwnProperty.call(GR_SYST_SUBST, w)) return GR_SYST_SUBST[w];
    var m = /^(δι|τρι|τετρα|πεντα|εξα|επτα|οκτα)(.+)$/.exec(String(w));
    if (m && Object.prototype.hasOwnProperty.call(GR_SYST_SUBST, m[2])) {
      var s2 = GR_SYST_SUBST[m[2]];
      return /\d/.test(s2) ? (m[1] + "(" + s2 + ")") : (m[1] + s2);
    }
  } catch (eS) {}
  return null;
}
// Parenthesize-when-preceded-by-locants (v54.35): a bare systematic name
// carrying an internal digit (προπαν-2-υλο) is ambiguous right after a parent
// locant run ("2-προπαν-2-υλο"), so the alkyl box nests it in parens when the
// preceding component is a number locant: -2-(προπαν-2-υλο)-. Already
// parenthesized (multiplied), unchanged, or digitless names pass through;
// empty locants (tiny chains, locant-free slots like the ester tail) mean no
// parens. Render/join-layer only — slots keep bare forms, so toggle
// visibility, splitting and idempotence are unaffected.
function fGRSysNeedsParens(sysText, commonText, prevLocText) {
  try {
    if (!sysText || sysText === commonText) return false;
    if (/[()]/.test(sysText)) return false;
    if (!/\d/.test(sysText)) return false;
    var loc = String(prevLocText == null ? "" : prevLocText).replace(/-/g, "");
    return /\d/.test(loc);
  } catch (eP) { return false; }
}

// Slot transform (slots 1/3/10, like the EN fSystematicSubstSlot): whole-string
// first (covers single groups incl. multiplied hyphenated stems), then fused
// multi-group slots with hyphen-carrying stems (sec-/tert-) shielded so the
// segment split cannot tear them apart (cf. EN sec-/tert- protection).
function fSystematicGRSubstSlot(slot, text) {
  try {
    if (slot !== 1 && slot !== 3 && slot !== 10) return text;
    // Preserve empty slots as-is (v54.32): null comp0bText/compAlcoholEster
    // must stay null, otherwise the changed-slot check flags a phantom
    // difference and the toggle shows on molecules with no variant.
    if (text == null || text === "") return text;
    var t = String(text);
    var one = fGRSystOneStem(t);
    if (one !== null) return one;
    var stems = ["sec-βουτυλο", "sec-βουτυλ", "tert-βουτυλο", "tert-βουτυλ"];
    var rx = new RegExp("(?:δι|τρι|τετρα|πεντα|εξα|επτα|οκτα)?(?:" + stems.join("|") + ")", "g");
    var held = [];
    var sh = t.replace(rx, function (m) { held.push(m); return "" + (held.length - 1) + ""; });
    var parts = sh.split("-");
    var out = [];
    for (var k = 0; k < parts.length; k++) {
      var w = parts[k];
      var hm = /^(\d+)$/.exec(w);
      if (hm) {
        var orig = held[parseInt(hm[1], 10)];
        var om = fGRSystOneStem(orig);
        out.push(om !== null ? om : orig);
        continue;
      }
      if (!w || /^\d[\d,]*$/.test(w)) { out.push(w); continue; }
      var pm = fGRSystOneStem(w);
      out.push(pm !== null ? pm : w);
    }
    return out.join("-");
  } catch (eS) { return text; }
}
// Transformed copy of the live common slots (1/3/10), or null when the
// systematic variant is identical (toggle hides; common renders).
function fGreekSysSlots() {
  try {
    if (typeof nameComponentsList === "undefined" || !nameComponentsList) return null;
    var slots = nameComponentsList.slice();
    var changed = false;
    for (var i = 0; i < slots.length; i++) {
      if (i === 1 || i === 3 || i === 10) {
        var nt = fSystematicGRSubstSlot(i, slots[i]);
        if (nt !== slots[i]) { slots[i] = nt; changed = true; }
      }
    }
    return changed ? slots : null;
  } catch (eG) { return null; }
}
// Sys-aware slot-3 pieces (v54.34): split the COMMON fused text for group
// boundaries, transform each name piece, keep locants. Returns {sys, com}
// or null (common itself unfused/unsplittable → whole-box fallback).
// The sys pieces feed the standard piece loop verbatim (same ids, same
// separators), so click modes, positional lookup, highlight, numbering and
// restore all work unchanged — no new modes.
function fSysFusedPieces() {
  try {
    if (typeof nameComponentsList === "undefined" || !nameComponentsList) return null;
    var common = nameComponentsList[3];
    if (typeof common !== "string" || !common) return null;
    var parts = (typeof fSplitBranchPieces === "function") ? fSplitBranchPieces(common) : null;
    if (!parts) return null;
    var sys = parts.map(function (p, k) {
      if (k % 2 === 1) return p;
      var m = (typeof fGRSystOneStem === "function") ? fGRSystOneStem(p) : null;
      return m !== null ? m : p;
    });
    if (sys.join("-") === parts.join("-")) return null;
    return { sys: sys, com: parts };
  } catch (eF) { return null; }
}

// Euphony join mirror of the fGuessName tail (common + ester two-word rule),
// for the joined systematic preview name from transformed slots.
function fJoinGreekSysName(slots) {
  try {
    if (!Array.isArray(slots) || !slots.length) return null;
    var _isEster = false;
    try {
      _isEster = (typeof functionalGroupsList !== "undefined" && functionalGroupsList &&
        functionalGroupsList.length === 1 && functionalGroupsList[0] === "ester");
    } catch (eE) {}
    // Parenthesize-when-preceded-by-locants (v54.35, mirrors the panel):
    // bare sys names after a locant run nest in parens so the joined preview
    // matches the panel boxes. Slots here are a fresh copy (safe to rewrite).
    // v54.41: full alphabetical group order (slot-1 + slot-3 pieces, locants
    // traveling) before wrapping — mirrors the panel pre-section.
    try {
      slots = slots.slice();
      var _jc = (typeof nameComponentsList !== "undefined") ? nameComponentsList : null;
      if (_jc && typeof fGRSysNeedsParens === "function") {
        var _jg = (typeof fGRSubstGroups === "function") ? fGRSubstGroups(slots, _jc) : [];
        var _jo = (typeof fGRSortSubstGroups === "function") ? fGRSortSubstGroups(_jg) : null;
        if (_jo) {
          try {
            var _jgp = -1;
            for (var _jgq = 0; _jgq < _jo.length; _jgq++) { if (_jg[_jo[_jgq]].kind === "g1") { _jgp = _jgq; break; } }
            if (_jgp > 0 && _jgp < _jo.length - 1) _jo = null;
          } catch (eJQJ) { _jo = null; }
        }
        if (_jo) {
          var _jpre = [];
          var _jje = false;
          for (var _jqi = 0; _jqi < _jo.length; _jqi++) {
            var _jgg = _jg[_jo[_jqi]];
            var _jgl = String(_jgg.loc == null ? "" : _jgg.loc).replace(/^[-\s]+/, "").replace(/[-\s]+$/, "");
            var _jlt = _jgl ? ((_jje ? "-" : "") + _jgl + "-") : "";
            var _jnt = _jgg.name;
            try { if (fGRSysNeedsParens(_jnt, _jgg.com, _jgg.loc)) _jnt = "(" + _jnt + ")"; } catch (ePPJ) {}
            if (_jlt) { _jpre.push(_jlt); _jje = true; }
            _jpre.push(_jnt); _jje = true;
          }
          slots[0] = _jpre.length > 0 ? _jpre[0] : "";
          slots[1] = _jpre.length > 1 ? _jpre[1] : "";
          slots[2] = _jpre.length > 2 ? _jpre[2] : "";
          slots[3] = _jpre.length > 3 ? _jpre.slice(3).join("") : "";
          if (fGRSysNeedsParens(slots[10], _jc[10], _jc[9])) slots[10] = "(" + slots[10] + ")";
        } else {
          if (fGRSysNeedsParens(slots[1], _jc[1], _jc[0])) slots[1] = "(" + slots[1] + ")";
          var _jsfp = (typeof fSysFusedPieces === "function") ? fSysFusedPieces() : null;
          if (_jsfp) {
            var _jp = _jsfp.sys.slice();
            for (var _jk = 0; _jk < _jp.length; _jk += 2) {
              var _jprev = (_jk === 0) ? _jc[2] : _jp[_jk - 1];
              if (fGRSysNeedsParens(_jp[_jk], _jsfp.com[_jk], _jprev)) _jp[_jk] = "(" + _jp[_jk] + ")";
            }
            slots[3] = _jp.join("-");
          } else if (fGRSysNeedsParens(slots[3], _jc[3], _jc[2])) {
            slots[3] = "(" + slots[3] + ")";
          }
          if (fGRSysNeedsParens(slots[10], _jc[10], _jc[9])) slots[10] = "(" + slots[10] + ")";
        }
      }
    } catch (eJP2) {}
    var _gkV = ['α', 'ε', 'η', 'ι', 'ο', 'υ', 'ω', 'ά', 'έ', 'ή', 'ί', 'ό', 'ύ', 'ώ'];
    var _isC = function (ch) {
      try { return /[\u0370-\u03ff\u1f00-\u1fff]/u.test(ch) && _gkV.indexOf(ch) < 0; } catch (eC) { return false; }
    };
    var _join = function (list) {
      return list.reduce(function (acc, part) {
        if (acc === '') return part;
        var lastCh = acc[acc.length - 1], firstCh = part[0];
        if (_isC(lastCh) && _isC(firstCh)) {
          var connector = ((lastCh === 'π' || lastCh === 'τ' || lastCh === 'ξ') && firstCh === 'δ') ? 'α' : 'ο';
          return acc + connector + part;
        }
        return acc + part;
      }, '');
    };
    if (_isEster) {
      var _acid = slots.slice(0, 10).filter(function (c) { return c != null && c !== ''; });
      var _tail = slots.slice(10).filter(function (c) { return c != null && c !== ''; });
      return _join(_acid) + (_tail.length ? ' ' + _join(_tail) : '');
    }
    return _join(slots.filter(function (c) { return c != null && c !== ''; }));
  } catch (eJ) { return null; }
}

function fShowNameAnalysis() {
  let compCount, currComp, displayComp, compBox, nameCompContainer;
  compCount = selectedMol ? nameComponentsList.length : 0;

  // Expanded-name overlay follows the same molecule only: a rebuild for a
  // different molecule closes it (fresh boxes + trailing fitter restore the
  // normal state, no refit needed here); same-molecule rebuilds (2D mode,
  // chain mode, stepper, eyes, scenario steps) keep it open.
  if (window.nameExpanded && window.expandedMol !== selectedMol) {
    window.nameExpanded = false;
    window.expandedMol = null;
    try {
      var _nxHost = document.getElementById("nameAnalysisContainer");
      if (_nxHost) { _nxHost.classList.remove("nameExpanded"); _nxHost.style.minHeight = ""; }
      var _nxExplain = document.getElementById("nameAnalysisExplain");
      if (_nxExplain) {
        _nxExplain.classList.remove("nameExplainExpanded");
        try {
          var _nxTip = _nxExplain.querySelector(".explainText");
          if (_nxTip) _nxTip.style.marginLeft = "";
        } catch (eNt) { /* best-effort */ }
      }
      try { fNameExplainPortalOut(); } catch (eNp) { /* best-effort */ }
      try { fNameExpandPaintBtn(); } catch (ePp) { /* best-effort */ }
      var _nxCont = document.querySelector("#nameAnalysis .nameCompContainer");
      if (_nxCont && _nxCont.parentElement) _nxCont.parentElement.style.minHeight = "";
    } catch (eNx) { /* best-effort */ }
  }

  const toggleIcon = narrateAnalysisFlag ? svgSpeaker : svgMute;
  const toggleTitle = narrateAnalysisFlag
    ? ((typeof fMulerT === "function") ? fMulerT("narrateOn") : "Αφήγηση ενεργή")
    : ((typeof fMulerT === "function") ? fMulerT("narrateOff") : "Αφήγηση ανενεργή");
  const narrateActiveClass = narrateAnalysisFlag ? " active" : "";
  const playDisabled = narrateAnalysisFlag ? "" : " disabled";

  const toggleNameStyleBox = window.nameBoxFlag ? svgNameBox : svgNameBoxOff;
  const boxClass = window.nameBoxFlag ? "nameCompBox boxed" : "nameCompBox unboxed";
  const boxTooltip = window.nameBoxFlag
    ? ((typeof fMulerT === "function") ? fMulerT("showBoxes") : "Πλαίσια συνθετικών")
    : ((typeof fMulerT === "function") ? fMulerT("hideBoxes") : "Χωρίς πλαίσια συνθετικών");
  const boxActiveClass = window.nameBoxFlag ? " active" : "";

  const toggleNameStyleCross = window.nameCrossFlag ? svgNameCross : svgNameCrossOff;
  const crossClass = window.nameCrossFlag ? "nameCompPlus " : "nameCompPlus hide";
  const crossTooltip = window.nameCrossFlag
    ? ((typeof fMulerT === "function") ? fMulerT("splitComps") : "Διαχωρισμένα συνθετικά")
    : ((typeof fMulerT === "function") ? fMulerT("joinedComps") : "Ενωμένα συνθετικά");
  const crossActiveClass = window.nameCrossFlag ? " active" : "";
  // Master eye-edit switch: single icon + .active highlight (live-only
  // authoring aid; never stored in steps).
  const toggleNameStyleEye = svgEyeState;
  const eyeActiveClass = window.nameEyeEdit === true ? " active" : "";
  // Explain-all overview toggle (live-only, like eye-edit).
  const explainAllActiveClass = (typeof window !== "undefined" && window.nameExplainAll) ? " active" : "";

  const nameSettingClass = nameSettingsFlag ? "open" : "";
  const namesSettingsBtnActiveClass = nameSettingsFlag ? "active" : "";
  // Ether IUPAC/COMMON toggle (ethers only, name panel).
  const _isEtherNaming =
    !!selectedMol &&
    nameExamples[selectedMol]?.classification?.chemicalClass === "ethers";
  const _iupacCls = etherNamingMode === "iupac" ? "selectedRadio" : "unselectedRadio";
  const _commonCls = etherNamingMode === "common" ? "selectedRadio" : "unselectedRadio";
  const _commonWord = (() => { try { return (typeof fMulerT === "function") ? fMulerT("commonName") : "Κοινή"; } catch (e) { return "Κοινή"; } })();
  const etherNamingToggle = _isEtherNaming
    ? `<div id='radioEtherNaming' class='HFlex' style='align-items:center;gap:0;margin-right:8px'><span class='settingLabel'>${(() => { try { return (typeof fMulerT === "function") ? fMulerT("etherNamingLabel") : "Αιθέρες:"; } catch (eL) { return "Αιθέρες:"; } })()}</span><div class='radioCheckContainer etherNamingRadio ${_iupacCls}' data-naming-mode='iupac'>IUPAC<span class='radioCheck'></span></div><div class='radioCheckContainer etherNamingRadio ${_commonCls}' data-naming-mode='common'>${_commonWord}<span class='radioCheck'></span></div></div>`
    : "";
  // Traditional/Systematic substituent toggle (EN only, when a systematic variant
  // exists that differs from school; hidden for common-ether rendering).
  var _substEntry = null;
  try { _substEntry = (typeof selectedMol !== "undefined" && selectedMol && typeof nameExamples !== "undefined") ? nameExamples[selectedMol] : null; } catch (eSE) { _substEntry = null; }
  var _isENLang = false;
  try { _isENLang = (typeof fMulerLang === "function" && fMulerLang() === "en"); } catch (eL0) { _isENLang = false; }
  var _showSubst = !!(_isENLang && _substEntry && _substEntry.engineEN_sys && _substEntry.engineEN_sys !== _substEntry.engineEN);
  if (_showSubst && _isEtherNaming) { try { if (typeof etherNamingMode !== "undefined" && etherNamingMode === "common") _showSubst = false; } catch (eC0) {} }
  var _substToggle = "";
  if (_showSubst) {
    var _scCls = (typeof substNamingMode !== "undefined" && substNamingMode === "sys") ? "unselectedRadio" : "selectedRadio";
    var _syCls = (typeof substNamingMode !== "undefined" && substNamingMode === "sys") ? "selectedRadio" : "unselectedRadio";
    var _scW = "Traditional", _syW = "Systematic";
    try { if (typeof fMulerT === "function") { _scW = fMulerT("substTraditional"); _syW = fMulerT("substSystematic"); } } catch (eTW) {}
    _substToggle = `<div id='radioSubstNaming' class='HFlex' style='align-items:center;gap:0;margin-right:8px'><span class='settingLabel'>${(() => { try { return (typeof fMulerT === "function") ? fMulerT("substNamingLabel") : "Υποκαταστάτες:"; } catch (eL2) { return "Υποκαταστάτες:"; } })()}</span><div class='radioCheckContainer substNamingRadio ${_scCls}' data-subst-mode='school'>${_scW}<span class='radioCheck'></span></div><div class='radioCheckContainer substNamingRadio ${_syCls}' data-subst-mode='sys'>${_syW}<span class='radioCheck'></span></div></div>`;
  }
  // Κοινή|Συστηματική substituent toggle (GR only, v54.31): same shared
  // substNamingMode as the EN toggle (one preference, language-exclusive
  // rendering). Render-time slots — visibility reads the live transform,
  // so no stored variant and no staleness class.
  var _grSysSlots = null, _showSubstGR = false;
  try {
    if (!_isENLang && selectedMol && typeof fGreekSysSlots === "function") {
      _grSysSlots = fGreekSysSlots();
      _showSubstGR = !!_grSysSlots;
    }
  } catch (eGS) { _grSysSlots = null; _showSubstGR = false; }
  if (_showSubstGR && _isEtherNaming) { try { if (typeof etherNamingMode !== "undefined" && etherNamingMode === "common") _showSubstGR = false; } catch (eC1) {} }
  var _grSubstToggle = "";
  if (_showSubstGR) {
    var _gscCls = (typeof substNamingMode !== "undefined" && substNamingMode === "sys") ? "unselectedRadio" : "selectedRadio";
    var _gsyCls = (typeof substNamingMode !== "undefined" && substNamingMode === "sys") ? "selectedRadio" : "unselectedRadio";
    var _gcW = "Κοινή", _gyW = "Συστηματική";
    try { if (typeof fMulerT === "function") { _gcW = fMulerT("commonName"); _gyW = fMulerT("systematicName"); } } catch (eTW2) {}
    _grSubstToggle = `<div id='radioSubstNaming' class='HFlex' style='align-items:center;gap:0;margin-right:8px'><span class='settingLabel'>${(() => { try { return (typeof fMulerT === "function") ? fMulerT("substNamingLabel") : "Υποκαταστάτες:"; } catch (eL3) { return "Υποκαταστάτες:"; } })()}</span><div class='radioCheckContainer substNamingRadio ${_gscCls}' data-subst-mode='school'>${_gcW}<span class='radioCheck'></span></div><div class='radioCheckContainer substNamingRadio ${_gsyCls}' data-subst-mode='sys'>${_gyW}<span class='radioCheck'></span></div></div>`;
  }
  // Panel layout: one row per control set, buttons first — each set renders
  // only when present, so there are never empty rows or half-rows.
  const _stepperHTML = (typeof fChainStepperHTML === "function") ? fChainStepperHTML() : "";
  const _buttonsHTML = (() => {
    const _tt = (k, gr) => { try { return (typeof fMulerT === "function") ? fMulerT(k) : gr; } catch (e) { return gr; } };
    return `<button id='narrateAnalysisToggle' class='narrateBtn${narrateActiveClass}' data-tooltip='${toggleTitle}'>${toggleIcon}</button><button id='readNameBtn' class='readNameBtn' data-tooltip='${_tt("readName", "Εκφώνηση ονόματος")}' >${svgAudioDesc}</button><button id='nameStyleBoxToggle' class='nameStyleBox ${boxActiveClass}' data-tooltip='${boxTooltip}'>${toggleNameStyleBox}</button><button id='nameStyleCrossToggle' class='nameStyleCross ${crossActiveClass}' data-tooltip='${crossTooltip}'>${toggleNameStyleCross}</button><button id='nameStyleEyeToggle' class='nameStyleEye${eyeActiveClass}' data-tooltip='${_tt("compVisibility", "Ορατότητα συνθετικών")}'>${toggleNameStyleEye}</button><button id='nameExplainAllBtn' class='nameExplainAll${explainAllActiveClass}' data-tooltip='${(typeof window !== "undefined" && window.nameExplainAll) ? _tt("explainSingle", "Μεμονωμένη εξήγηση") : _tt("explainAll", "Επισκόπηση")}' aria-label='${(typeof window !== "undefined" && window.nameExplainAll) ? _tt("explainSingle", "Μεμονωμένη εξήγηση") : _tt("explainAll", "Επισκόπηση")}'>${svgNameExplainAll}</button><button id='nameExpandBtn' class='nameStyleExpand' data-tooltip='${_tt("fullName", "Πλήρες όνομα")}' aria-label='${_tt("fullName", "Πλήρες όνομα")}' hidden>${svgNameExpand}</button>`;
  })();
  var _panelInner = "";
  // One row per control set: buttons first, then naming radios, then stepper.
  // Rows render only when they have content (no empty rows by construction).
  var _rowsAll = [`<div id='nameSettingsRowMain'><div class='nsLeft'>${_buttonsHTML}</div></div>`];
  if (etherNamingToggle) _rowsAll.push(`<div class='nameSettingsRow'>${etherNamingToggle}</div>`);
  if (_substToggle) _rowsAll.push(`<div class='nameSettingsRow'>${_substToggle}</div>`);
  else if (_grSubstToggle) _rowsAll.push(`<div class='nameSettingsRow'>${_grSubstToggle}</div>`);
  if (_stepperHTML) _rowsAll.push(`<div class='nameSettingsRow'>${_stepperHTML}</div>`);
  _panelInner = _rowsAll.join("");

  const _namingWord = (() => { try { return (typeof fMulerT === "function") ? fMulerT("naming") : "Ονομασία"; } catch (e) { return "Ονομασία"; } })();
  const _namingSettingsWord = (() => { try { return (typeof fMulerT === "function") ? fMulerT("namingSettings") : "Ρυθμίσεις Ονομασίας"; } catch (e) { return "Ρυθμίσεις Ονομασίας"; } })();
  const _molInfoWord = (() => { try { return (typeof fMulerT === "function") ? fMulerT("molInfo") : "Πληροφορίες μορίου"; } catch (e) { return "Πληροφορίες μορίου"; } })();
  const _molInfoActive = (typeof molInfoOpenFlag !== "undefined" && molInfoOpenFlag) ? " active" : "";
  const _molInfoAria = (typeof molInfoOpenFlag !== "undefined" && molInfoOpenFlag) ? "true" : "false";
  nameCompContainer =
    `<div class='panelTitle'><span>${_namingWord}</span><div id='nameSettingsBtnDiv'><button id='molInfoBtn' class='settingsBtn${_molInfoActive}' onclick='fToggleMolInfo()' data-tooltip='${_molInfoWord}' aria-label='${_molInfoWord}' aria-expanded='${_molInfoAria}'>${svgMolInfo}</button><button  id='nameSettingsBtn'  class='settingsBtn ${namesSettingsBtnActiveClass}'  onclick='fToggleNameSettings()'  data-tooltip='${_namingSettingsWord}' >${svgSettings} </button></div></div><div id='nameSettingsPanel' class='${nameSettingClass}'>${_panelInner}</div><div id='moleculeInfo' class='${(typeof molInfoOpenFlag !== "undefined" && molInfoOpenFlag) ? "open" : ""}'></div><div class='HFlex nameContainer' style='justify-content:center;'><div class='nameCompContainer'>`;

  if (!selectedMol) {
    nameCompContainer +=
      `<div class='nameEmptyHint'>` + ((typeof fMulerT === "function") ? fMulerT("noMolHint") : "Επιλέξτε μόριο για ανάλυση ονόματος") + `</div>`;
  }

  // COMMON ether naming: render alkyl boxes + αιθέρας instead of IUPAC slots.
  const _commonParts = _isEtherNaming && etherNamingMode === "common" ? fGetEtherCommonParts() : null;
  var _isEN = false;
  try { _isEN = (typeof fMulerLang === "function" && fMulerLang() === "en"); } catch (eL) { _isEN = false; }
  var _enBoxes = null;
  var _renderedENBoxes = false;
  try { _enBoxes = (_isEN && typeof fNameENBoxes === "function") ? fNameENBoxes() : null; } catch (eEN) { _enBoxes = null; }
  if (_commonParts && _commonParts.parts) {
    var _labels = _commonParts.parts.map(function (p) { return p.label; });
    if (_isEN && typeof fMulerENCommonLabel === "function") {
      var _enLabels = [];
      for (var _li = 0; _li < _labels.length; _li++) { _enLabels.push(fMulerENCommonLabel(_labels[_li])); }
      if (_enLabels.indexOf(null) < 0) { _labels = _enLabels; _renderedENBoxes = true; }
    }
    for (let ci = 0; ci < _labels.length; ci++) {
      currComp = _labels[ci];
      if (currComp == "" || currComp == undefined) {
        continue;
      }
      let displayComp = currComp;
      for (let n = ci + 1; n < _labels.length; n++) {
        const nextComp = _labels[n];
        if (!nextComp) continue;
        const lastCh = currComp[currComp.length - 1];
        const firstCh = nextComp[0];
        const _isGkConsonant = (ch) =>
          /[\u0370-\u03ff\u1f00-\u1fff]/u.test(ch) &&
          !new Set([
            "α",
            "ε",
            "η",
            "ι",
            "ο",
            "υ",
            "ω",
            "ά",
            "έ",
            "ή",
            "ί",
            "ό",
            "ύ",
            "ώ",
          ]).has(ch);
        if (_isGkConsonant(lastCh) && _isGkConsonant(firstCh)) {
          const connector =
            (lastCh === "π" || lastCh === "τ" || lastCh === "ξ") && firstCh === "δ" ? "α" : "ο";
          displayComp = `${currComp}<span class='euphonyLetter'>${connector}</span>`;
        }
        break;
      }

      compBox = fNameCompBox("comp" + (10 + ci), boxClass, displayComp);
      if (ci < _labels.length - 1) {
        compBox += `<div class='${crossClass}' > + </div>`;
      }
      nameCompContainer += compBox;
    }
  } else if (_enBoxes && _enBoxes.boxes && _enBoxes.boxes.length) {
  // EN systematic name boxes: pre-transliterated text in EN order, stable Greek box ids.
  _renderedENBoxes = true;
  var _elist = _enBoxes.boxes;
  // Systematic variant: same ids, systematic substituent text, diff-marked
  // boxes whose text is new vs school (locants match by construction).
  if (_showSubst && typeof substNamingMode !== "undefined" && substNamingMode === "sys") {
    try {
      var _sbx = (typeof fNameENBoxes === "function") ? fNameENBoxes("sys") : null;
      if (_sbx && _sbx.boxes && _sbx.boxes.length) {
        var _preIds = /^(comp0|comp1|comp2|comp3|comp3b\d*|comp3loc\d*|comp10)$/;
        var _schoolSeen = {};
        for (var _sbi = 0; _sbi < _elist.length; _sbi++) {
          if (_preIds.test(_elist[_sbi][0])) _schoolSeen[_elist[_sbi][1]] = true;
        }
        var _tipPre = "Traditional form: ";
        try { if (typeof fMulerT === "function") _tipPre = fMulerT("sysDiffTip"); } catch (eTtip) {}
        var _schoolEN = "";
        try {
          if (typeof nameExamples !== "undefined" && selectedMol && nameExamples[selectedMol]) _schoolEN = nameExamples[selectedMol].engineEN || "";
        } catch (eSEN) {}
        try { if (typeof fMolDraftEsc === "function") { _tipPre = fMolDraftEsc(_tipPre); _schoolEN = fMolDraftEsc(_schoolEN); } } catch (eEsc) {}
        var _slist = [];
        for (var _dbi = 0; _dbi < _sbx.boxes.length; _dbi++) {
          var _bid = _sbx.boxes[_dbi][0], _btx = _sbx.boxes[_dbi][1];
          var _tip = null;
          if (_preIds.test(_bid) && !_schoolSeen.hasOwnProperty(_btx)) _tip = _tipPre + _schoolEN;
          _slist.push([_bid, _btx, _tip]);
        }
        _elist = _slist;
      }
    } catch (eSys) { /* school render stands */ }
  }
  for (var _ei = 0; _ei < _elist.length; _ei++) {
    compBox = fNameCompBox(_elist[_ei][0], boxClass, _elist[_ei][1], _elist[_ei].length > 2 ? _elist[_ei][2] : null);
    nameCompContainer += compBox;
    if (_ei < _elist.length - 1) {
      if (_enBoxes.spaceAfter && _elist[_ei][0] === _enBoxes.spaceAfter) nameCompContainer += `<div class='nameCompSpace'>&nbsp;</div>`;
      else nameCompContainer += `<div class='${crossClass}' > + </div>`;
    }
  }
  } else {
  // Build the name component boxes with Greek euphony applied, and + signs in between
  // Systematic GR variant (v54.31): when the Κοινή|Συστηματική toggle selects
  // sys and a variant exists, render from the transformed slots (same box ids,
  // so highlight/explain mapping is untouched). Changed substituent boxes get
  // a "Κοινή μορφή: …" title (mirror of the EN sys diff-mark).
  var _grSysMode = false;
  try {
    _grSysMode = !_isENLang && _showSubstGR && !!_grSysSlots &&
      typeof substNamingMode !== "undefined" && substNamingMode === "sys";
  } catch (eGM) { _grSysMode = false; }
  var _slots = _grSysMode ? _grSysSlots : nameComponentsList;
  var _grTipPre = null, _grSchoolFull = "";
  if (_grSysMode) {
    try {
      _grTipPre = (typeof fMulerT === "function") ? fMulerT("sysDiffTipCommon", "sysDiffTipCommon") : "Κοινή μορφή: ";
      if (!_grTipPre || _grTipPre === "sysDiffTipCommon") _grTipPre = "Κοινή μορφή: ";
      _grSchoolFull = (typeof currentMolName !== "undefined") ? String(currentMolName) : "";
      try { if (typeof fMolDraftEsc === "function") { _grTipPre = fMolDraftEsc(_grTipPre); _grSchoolFull = fMolDraftEsc(_grSchoolFull); } } catch (eEscG) {}
    } catch (eGTp) { _grTipPre = null; }
  }
  // Systematic alphabetical pre-section (v54.41, P-14.5.1/2 analogue): the
  // slot-1 group + every slot-3 piece sort together by DISPLAYED sys name,
  // locants traveling with their group. Rendered here directly (bypassing
  // the slot loop below for i<4); box ids stay attached to content so the
  // highlight/explain mapping is untouched. Null = legacy loop below
  // (single group, original order, middle order, or a non-first group
  // without digit locants — fail-closed, today's exact output).
  var _preHTML = "";
  if (_grSysMode && typeof fGRSubstGroups === "function" && typeof fGRSortSubstGroups === "function") {
    try {
      var _pg = fGRSubstGroups(_slots, (typeof nameComponentsList !== "undefined") ? nameComponentsList : null);
      var _po = fGRSortSubstGroups(_pg);
      if (_po) {
        var _pgp = -1;
        for (var _pgq = 0; _pgq < _po.length; _pgq++) { if (_pg[_po[_pgq]].kind === "g1") { _pgp = _pgq; break; } }
        if (_pgp > 0 && _pgp < _po.length - 1) _po = null;
      }
      if (_po) {
        var _pem = false;
        for (var _pge = 0; _pge < _po.length; _pge++) {
          var _gg = _pg[_po[_pge]];
          var _gl = String(_gg.loc == null ? "" : _gg.loc).replace(/^[-\s]+/, "").replace(/[-\s]+$/, "");
          var _lt = _gl ? ((_pem ? "-" : "") + _gl + "-") : "";
          if (_lt) { _preHTML += fNameCompBox(_gg.locId, boxClass, _lt); _pem = true; }
          var _nt2 = _gg.name, _ntTip = null;
          try { if (_nt2 !== _gg.com && _grTipPre) _ntTip = _grTipPre + _grSchoolFull; } catch (eTGp) { _ntTip = null; }
          try { if (typeof fGRSysNeedsParens === "function" && fGRSysNeedsParens(_nt2, _gg.com, _gg.loc)) _nt2 = "(" + _nt2 + ")"; } catch (ePGp) {}
          _preHTML += fNameCompBox(_gg.nameId, boxClass, _nt2, _ntTip);
          _pem = true;
          if (_pge < _po.length - 1) _preHTML += `<div class='${crossClass}' > + </div>`;
        }
        var _pnx = -1;
        for (var _pnxM = 4; _pnxM < compCount; _pnxM++) { if (_slots[_pnxM]) { _pnx = _pnxM; break; } }
        if (_pnx >= 0) {
          var _preEster = false;
          try {
            _preEster = (typeof nameExamples !== "undefined" && selectedMol &&
              nameExamples[selectedMol] && nameExamples[selectedMol].classification &&
              nameExamples[selectedMol].classification.chemicalClass === "esters");
          } catch (ePEst) { _preEster = false; }
          if (_preEster && _pnx >= 10) _preHTML += `<div class='nameCompSpace'>&nbsp;</div>`;
          else _preHTML += `<div class='${crossClass}' > + </div>`;
        }
      }
    } catch (ePre) { _preHTML = ""; }
  }

  const acidPrefixGroups = fAcidPrefixBoxGroups();
  for (let i = 0; i < compCount; i++) {
    if (_preHTML && i < 4) {
      if (i === 0) nameCompContainer += _preHTML;
      continue;
    }
    currComp = !_grSysMode && i === 3 && acidPrefixGroups.length === 3 ? acidPrefixGroups[1].label : _slots[i];
    if (currComp == "" || currComp == undefined) {
      continue;
    }

    // Apply Greek euphony: append connecting vowel to this component's display
    // if it ends with a consonant and the next non-empty component starts with one.
    // Esters are two words (προπανικός μεθυλεστέρας): no connector from the
    // acid part (slots <10) into the fused tail (slots 10+).
    const _isEsterWordBoundary = (typeof nameExamples !== "undefined" && selectedMol &&
      nameExamples[selectedMol]?.classification?.chemicalClass === "esters");
    // Next non-empty component drives both euphony and the trailing separator,
    // so no "+" (or space) ever renders after the last box.
    let _nextIdx = -1;
    for (let _m = i + 1; _m < compCount; _m++) {
      if (_slots[_m]) { _nextIdx = _m; break; }
    }
    let displayComp = currComp;
    for (let n = i + 1; n < compCount; n++) {
      const nextComp = _slots[n];
      if (!nextComp) continue;
      const lastCh = currComp[currComp.length - 1];
      const firstCh = nextComp[0];
      const _isGkConsonant = (ch) =>
        /[\u0370-\u03ff\u1f00-\u1fff]/u.test(ch) &&
        !new Set([
          "α",
          "ε",
          "η",
          "ι",
          "ο",
          "υ",
          "ω",
          "ά",
          "έ",
          "ή",
          "ί",
          "ό",
          "ύ",
          "ώ",
        ]).has(ch);
      const _crossesEsterBoundary = _isEsterWordBoundary && (n >= 10 && i < 10);
      if (!_crossesEsterBoundary && _isGkConsonant(lastCh) && _isGkConsonant(firstCh)) {
        const connector =
          (lastCh === "π" || lastCh === "τ" || lastCh === "ξ") && firstCh === "δ" ? "α" : "ο";
        displayComp = `${currComp}<span class='euphonyLetter'>${connector}</span>`;
      }
      break;
    }

    var _grBoxText = displayComp;
    var _grBoxTip = (_grSysMode && (i === 1 || i === 3 || i === 10) && _slots[i] !== nameComponentsList[i] && _grTipPre) ? (_grTipPre + _grSchoolFull) : null;
    if (_grSysMode && (i === 1 || i === 3) && _slots[i] !== nameComponentsList[i] && typeof fGRSysNeedsParens === "function") {
      var _grPrevLoc = (i === 1) ? _slots[0] : _slots[2];
      if (fGRSysNeedsParens(displayComp, nameComponentsList[i], _grPrevLoc)) _grBoxText = "(" + displayComp + ")";
    }
    compBox = fNameCompBox("comp" + i, boxClass, _grBoxText, _grBoxTip);
    if (!_grSysMode && i === 3 && acidPrefixGroups.length === 3) {
      compBox += `<div class='${crossClass}'> + </div>` +
        fNameCompBox('acidPrefixNumber3', boxClass, '-'+acidPrefixGroups[2].locants+'-') +
        `<div class='${crossClass}'> + </div>` +
        fNameCompBox('acidPrefixSub3', boxClass, acidPrefixGroups[2].label);
    }
    // Locants are always their own component: the suffix slot (index 9)
    // fuses them only on the db+tb ketone/polyol paths ("-2,7-διόνη"), so
    // split that shape here at render time — locants first, suffix keeping
    // the slot id so every id-driven behavior (click mode, restore, hidden
    // sets, eye toggles) is unchanged. Data list, euphony boundaries and
    // the joined name are identical to the fused string.
    if (i === 9 && !(typeof fScenarioUseLegacyNameBoxes === "function" && fScenarioUseLegacyNameBoxes())) {
      try {
        var _singleFG = (typeof functionalGroupsList !== "undefined" &&
          Array.isArray(functionalGroupsList) && functionalGroupsList.length === 1)
          ? functionalGroupsList[0] : null;
        // Both C=C and C≡C present (same globals the suffix explain path
        // already reads): only those two fusion sites ever merge locants
        // into the suffix slot.
        var _hasDB = false, _hasTB = false;
        try {
          _hasDB = !!(typeof multiBondsObj !== "undefined" && multiBondsObj &&
            multiBondsObj.CCd && multiBondsObj.CCd.length > 0);
          _hasTB = !!(typeof multiBondsObj !== "undefined" && multiBondsObj &&
            multiBondsObj.CCt && multiBondsObj.CCt.length > 0);
        } catch (eBonds) { _hasDB = false; _hasTB = false; }
        if ((_singleFG === "ketone" || _singleFG === "alcohol") && _hasDB && _hasTB) {
          var _sm = String(displayComp).match(/^(-\d[\d,]*-)([\u0370-\u03ff\u1f00-\u1fff]+)$/);
          if (_sm) {
            compBox = fNameCompBox("comp9loc", boxClass, _sm[1]);
            compBox += fNameCompBox("comp" + i, boxClass, _sm[2]);
          }
        }
      } catch (eSplit) { /* fused single box fallback */ }
    }
    // Branch labels are always their own components: slot 3 (comp0bText)
    // fuses the 2nd and later substituent groups ("ισοπροπυλο-4,5-διμεθυλο")
    // once three substituent types exist, so split it here at render time —
    // the first name keeps the comp3 slot id, locants take comp3loc and
    // later names comp3b (then comp3loc2/comp3b2, ...). Core list, euphony
    // and the joined name are unchanged: piece ends ("-", digit, vowel-end
    // name) never take a connector, and a fired euphony aborts the split.
    // Systematic fused slot (v54.34): the naive splitter would shred
    // internal-locant names ("προπαν-2-υλο" → 3 pieces) or mis-pair them, so
    // split the COMMON text for group boundaries and transform name pieces
    // instead — [sysName, locants, sysName...] through the same loop, ids
    // and lookup unchanged. Null (common itself unsplittable) falls back to
    // the whole box, as does an unchanged slot.
    if (i === 3 && displayComp === currComp &&
        !(typeof fScenarioUseLegacyNameBoxes === "function" && fScenarioUseLegacyNameBoxes())) {
      try {
        var _brp = null, _brpCom = null;
        if (_grSysMode && _slots[3] !== nameComponentsList[3]) {
          var _sfp = (typeof fSysFusedPieces === "function") ? fSysFusedPieces() : null;
          if (_sfp) { _brp = _sfp.sys; _brpCom = _sfp.com; }
        } else {
          _brp = fSplitBranchPieces(currComp);
        }
        if (_brp) {
          var _brLast = _brp[_brp.length - 1];
          var _brNext = _nextIdx >= 0 ? String(_slots[_nextIdx]) : "";
          // Local copy of the Greek-consonant test: _isGkConsonant is scoped
          // to the euphony for-loop above and is not visible here.
          var _brIsGk = function (ch) {
            return /[\u0370-\u03ff\u1f00-\u1fff]/u.test(ch) &&
              !new Set([
                "α",
                "ε",
                "η",
                "ι",
                "ο",
                "υ",
                "ω",
                "ά",
                "έ",
                "ή",
                "ί",
                "ό",
                "ύ",
                "ώ",
              ]).has(ch);
          };
          var _brEuph = _brNext !== "" &&
            _brIsGk(_brLast[_brLast.length - 1]) && _brIsGk(_brNext[0]);
          if (!_brEuph) {
            var _brx = "";
            // Locants pieces carry dashes on both sides ("-6,6-"), unless the
            // piece leads the whole panel — then trailing dash only, like the
            // comp0 "3-" convention. (Unreachable while slot 3 is fused, since
            // fusion implies slots 0-2 exist; kept as the general rule.)
            var _brFirst = !(_slots[0] || _slots[1] || _slots[2]);
            for (var _bri = 0; _bri < _brp.length; _bri++) {
              var _brId, _brText;
              if (_bri % 2 === 0) {
                var _brNj = _bri / 2 + 1;
                _brId = _brNj === 1 ? "comp3" : "comp3b" + (_brNj === 2 ? "" : String(_brNj - 1));
                // Names stay bare: dashes live in locants boxes only, so the
                // locants piece supplies the junction dash on both sides.
                _brText = _brp[_bri];
              } else {
                var _brLj = (_bri + 1) / 2 + 1;
                _brId = "comp3loc" + (_brLj === 2 ? "" : String(_brLj - 1));
                _brText = (_brFirst ? "" : "-") + _brp[_bri] + "-";
              }
              if (_bri > 0) _brx += `<div class='${crossClass}' > + </div>`;
              if (_brpCom && _bri % 2 === 0 && typeof fGRSysNeedsParens === "function") {
                var _brPrevLoc = (_bri === 0) ? nameComponentsList[2] : _brp[_bri - 1];
                if (fGRSysNeedsParens(_brText, _brpCom[_bri], _brPrevLoc)) _brText = "(" + _brText + ")";
              }
              var _brTip = null;
              try {
                if (_brpCom && _bri % 2 === 0 && _brp[_bri] !== _brpCom[_bri] && _grTipPre) {
                  _brTip = _grTipPre + _grSchoolFull;
                }
              } catch (eBT) { _brTip = null; }
              _brx += fNameCompBox(_brId, boxClass, _brText, _brTip);
            }
            compBox = _brx;
          }
        }
      } catch (eSplitB) { /* fused single box fallback */ }
    }
    if (_nextIdx >= 0) {
      // Esters: two-word name — blank space after ικός instead of +.
      if (_isEsterWordBoundary && i < 10 && _nextIdx >= 10) {
        compBox += `<div class='nameCompSpace'>&nbsp;</div>`;
      } else {
        compBox += `<div class='${crossClass}' > + </div>`;
      }
    }
    nameCompContainer += compBox;
  }
  } // end IUPAC boxes (else of COMMON render)

  // nameCompContainer += "</div><button id='readNameBtn' class='readNameBtn' data-tooltip='Ανάγνωση ονόματος'" + playDisabled + ">" + svgPlay + "</button></div>"

  // Oracle/fallback marker (EN only): tint when the shown name is not pure
  // engine output — PubChem-oracle EN boxes, or Greek fallback in EN mode.
  // Verdict states (mismatch/no-data) are decided by fMulerVerdictState.
  // Additive container classes: box ids and hooks untouched. GR never marked.
  try {
    var _oracleState = (typeof fMulerVerdictState === "function") ? fMulerVerdictState(selectedMol, false) : null;
    if (_oracleState) {
      var _tipMap = { oracle: "oracleNameTip", fallback: "greekFallbackTip", mismatch: "enMismatchTip", nooracle: "enNoOracleTip", noerror: "enNoErrorTip" };
      var _tipFall = {
        oracle: "Name from the PubChem oracle — pending human review",
        fallback: "No engine English name — showing Greek",
        mismatch: "Engine name differs from PubChem IUPAC — pending human review",
        nooracle: "No PubChem/CIR data to validate against",
        noerror: "Oracle lookup failed (network) — not validated"
      };
      var _tip = _tipFall[_oracleState] || _tipFall.oracle;
      try { if (typeof fMulerT === "function") _tip = fMulerT(_tipMap[_oracleState] || "oracleNameTip"); } catch (eT) {}
      nameCompContainer = nameCompContainer.replace("<div class='nameCompContainer'>",
        "<div class='nameCompContainer oracle-name verdict-" + _oracleState + "' title='" + _tip + "'>");
    }
  } catch (eO) { /* marker best-effort */ }

  $("#nameAnalysis").html(nameCompContainer);
  // Second-oracle (OpenClatura) marker: same post-process as the in-place
  // repaint, so rebuilds and fetch completions paint identically.
  try { if (typeof fMulerApplyOCVerdict === "function") fMulerApplyOCVerdict(selectedMol); } catch (eOC) {}
  try { if (typeof fRenderMolInfo === "function") fRenderMolInfo(); } catch (eMI) {}

  // Fix 3: the explain line follows box visibility — hidden when zero
  // components are visible, restored on reveal (toggle, so both directions
  // work; the presentation lock logic re-asserts afterwards).
  try {
    var _allBoxesFx3 = document.querySelectorAll(".nameCompContainer .nameCompBox");
    var _visBoxes = document.querySelectorAll(".nameCompContainer .nameCompBox:not(.comp-hidden)");
    var _tableOnFx3 = (typeof window !== "undefined" && !!window.nameExplainAll);
    $("#nameAnalysisExplain").toggle((_tableOnFx3 && _allBoxesFx3.length > 0) || _visBoxes.length > 0); // table on: all-hidden still shows (dashed chips)
  } catch (e) {
    /* DOM unavailable */
  }

  // Restore .selected on the previously-selected box after HTML rebuild.
  // A shown position number ("-2-" here is not "-4-" there) never carries
  // across molecules; component selections keep the sticky restore below.
  // Same-molecule rebuilds are unaffected.
  try {
    var _rm = (typeof selectedMol !== "undefined" && selectedMol) ? String(selectedMol) : "";
    var _prevRm = (typeof window !== "undefined") ? window.__mulerRestoreMol : null;
    if (typeof window !== "undefined") window.__mulerRestoreMol = _rm;
    if (_prevRm !== null && _prevRm !== _rm && nameAnalysisMode !== "none") {
      var _showLoc = false;
      try {
        var _rBox = (typeof fMulerQuizBoxIdForMode === "function") ? fMulerQuizBoxIdForMode(nameAnalysisMode) : null;
        _showLoc = (typeof fMulerQuizBoxShowsLocant === "function") ? fMulerQuizBoxShowsLocant(_rBox, null) : false;
      } catch (eRP) { _showLoc = false; }
      if (_showLoc) {
        try { nameAnalysisMode = "none"; } catch (eRN) {}
      }
    }
  } catch (eR) {}
  if (nameAnalysisMode !== "none") {
    const _modeToCompId = {
      compNumber1: "comp0",
      "compSecondSub1": "comp1",
      compNumber2: "comp2",
      compAcidNumber3: "acidPrefixNumber3",
      compAcidSub3: "acidPrefixSub3",
      "compSecondSub2": "comp3",
      compBondPos: "comp4",
      compCarbonsCount: "comp5",
      compBondType: "comp6",
      compEndNumber: "comp7",
      compBondType2: "comp8",
      compSuffix: "comp9",
      compSuffixLocants: "comp9loc",
      compBranchSub1: "comp3",
      compBranchLoc2: "comp3loc",
      compBranchSub2: "comp3b",
      commonAlkyl1: "comp10",
      commonAlkyl2: "comp11",
      commonEther: "comp12",
      esterAlkyl: "comp10",
      esterEster: "comp11",
    };
    const _selId = _modeToCompId[nameAnalysisMode] || fBranchPieceBoxId(nameAnalysisMode);
    // Hidden boxes stay inert: never restore .selected onto a dash box.
    if (_selId && $(`#${_selId}`).length && !fNameCompHidden(_selId) &&
        !(typeof window.fScenarioNameCompDisabled === "function" &&
          window.fScenarioNameCompDisabled(_selId))) {
      $(`#${_selId}`).addClass("selected");
    } else {
      nameAnalysisMode = "none";
    }
  }

  fExplainNameComp();

  // Sticky-quiz re-arm: sticky selection restored .selected above, but the
  // molecule switch disarmed the quiz (PushState) — re-arm so condensed
  // CHO/COOH clicks stay anchor-carbon-only instead of whole-fragment.
  // No-op unless select is armed, target is clear, and the restored box is
  // quiz-capable + visible. Safe on every rebuild (style/eye/stepper paths
  // keep their target and skip here).
  try { if (typeof fMulerQuizRearmSticky === "function") fMulerQuizRearmSticky(); } catch (eQR) {}

  // Scenario rebuild hook (additive, guarded): this rebuild recreates
  // #nameSettingsBtnDiv/#nameSettingsPanel + voice buttons without the
  // presentation hides, so re-assert the current present step's naming
  // chrome (same pattern as the fScenarioOn3DParsed hook below).
  try {
    if (typeof window.fScenarioApplyNamingChrome === "function") window.fScenarioApplyNamingChrome();
  } catch (e) {
    /* scenario absent */
  }
  fFitNameComponents();
  fNameExpandSync();
  // Same-molecule rebuild while open: boxes were recreated, re-pin the
  // host height so Explain stays below the sheet (fFit is a no-op here).
  try { if (window.nameExpanded) fNameExpandReserve(); } catch (eR) { /* best-effort */ }
  try { if (window.nameExpanded) fNameExplainAnchor(); } catch (eA) { /* best-effort */ }
  // Explain-all overview on: every rebuild path (molecule/variant/eye)
  // funnels through here, so re-render the table from a fresh build. The
  // single explain above already restored the live selection's paint.
  try { if (typeof window !== "undefined" && window.nameExplainAll && typeof fNameExplainTableShow === "function") fNameExplainTableShow(); } catch (eEA) {}
}

// While open, viewport/column changes can alter the wrapped height:
// re-pin the reserve + re-anchor Explain (debounced, guarded so it registers only once).
var _nameExpandResizeTimer = null;
var _nameExpandScrollRaf = 0;
var _nameExpandRepinTimer = null;
// Re-pin after a layout shift above the sheet (e.g. the name settings panel
// opening/closing, which animates 0.25s): pin now for the start state and
// once more after the transition settles. No-op unless expanded; pending
// timers collapse into one.
function fNameExpandRepinDelayed() {
  if (!window.nameExpanded) return;
  try { fNameExpandReserve(); } catch (eR) { /* best-effort */ }
  try { fNameExplainAnchor(); } catch (eA) { /* best-effort */ }
  try {
    if (_nameExpandRepinTimer) clearTimeout(_nameExpandRepinTimer);
    _nameExpandRepinTimer = setTimeout(function () {
      _nameExpandRepinTimer = null;
      if (!window.nameExpanded) return;
      try { fNameExpandReserve(); } catch (eR2) { /* best-effort */ }
      try { fNameExplainAnchor(); } catch (eA2) { /* best-effort */ }
    }, 320);
  } catch (eT) { /* best-effort */ }
}
(function () {
  try {
    if (window._nameExpandResizeHook) return;
    window._nameExpandResizeHook = true;
    window.addEventListener("resize", function () {
      if (!window.nameExpanded) return;
      if (_nameExpandResizeTimer) clearTimeout(_nameExpandResizeTimer);
      _nameExpandResizeTimer = setTimeout(function () {
        _nameExpandResizeTimer = null;
        try { fNameExpandReserve(); } catch (eR) { /* best-effort */ }
        try { fNameExplainAnchor(); } catch (eA) { /* best-effort */ }
      }, 150);
    });
    document.addEventListener("scroll", function (e) {
      if (!window.nameExpanded) return;
      try {
        var t = e && e.target;
        if (!t || !t.classList || !t.classList.contains("nameCompContainer")) return;
        if (_nameExpandScrollRaf) return;
        _nameExpandScrollRaf = requestAnimationFrame(function () {
          _nameExpandScrollRaf = 0;
          try { fNameExplainAnchor(); } catch (eA) { /* best-effort */ }
        });
      } catch (eS) { /* best-effort */ }
    }, true);
  } catch (eW) { /* best-effort */ }
})();

// ── fClearHighlights ──────────────────────────────────────────────────────

function fClearHighlights() {
  clearInterval(myNumberingTimeout);
  currNumberEl = 0;
  if (!jsmeNomeclatureApplet) return;
  jsmeNomeclatureApplet.resetAtomColors(0);
  jsmeNomeclatureApplet.resetBondColors(0);
  fJSmolScript(
    jmolAppletNomeclature,
    "select all;  selectionHalos off; color bonds none; color atoms none;",
  );
  showAtomSymbols3D(!fSequentialKetoneNumberingTarget());
  removeEcho3D();
  $("#ruleTheoryContainer").hide();
  $("#nameAnalysisExplain").html("");
  ruleTableHighlight = null;
  numberingAtomOverride = null;
  numberingAtomOverride3D = null;
  JmolSelection = "select none"; // no trailing ";": call sites join as "...;" + JmolSelection + ";"
}

// ── Secondary-group display names ─────────────────────────────────────────
// Greek nouns for secondary characteristic groups, shown in parentheses in
// fExplainNameComp messages. Vocabulary matches the r4 rule table.
const secondaryGroupNouns = {
  alcohol: "Υδροξύλιο",
  aldehyde: "Αλδεϋδομάδα",
  ketone: "Κετονομάδα",
  carboxylicAcid: "Καρβοξύλιο",
  cyanide: "Κυανομάδα",
  amine: "Αμινοομάδα",
  nitro: "Νιτροομάδα",
  ether: "Αλκοξυομάδα",
  ester: "Εστερομάδα",
};

const secondaryHalogenNouns = {
  Cl: "Χλώριο",
  Br: "Βρώμιο",
  F: "Φθόριο",
  I: "Ιώδιο",
};

const secondaryGroupPluralNouns = {
  alcohol: "Υδροξύλια",
  aldehyde: "Αλδεϋδομάδες",
  ketone: "Κετονομάδες",
  carboxylicAcid: "Καρβοξύλια",
  cyanide: "Κυανομάδες",
  amine: "Αμινοομάδες",
  nitro: "Νιτροομάδες",
  ether: "Αλκοξυομάδες",
  ester: "Εστερομάδες",
};

const alkylBranchNouns = {
  μεθυλο: "μεθύλιο",
  αιθυλο: "αιθύλιο",
  προπυλο: "προπύλιο",
  ισοπροπυλο: "ισοπροπύλιο",
  βουτυλο: "βουτύλιο",
  πεντυλο: "πεντύλιο",
  εξυλο: "εξύλιο",
  επτυλο: "επτύλιο",
  οκτυλο: "οκτύλιο",
};

// EN counterparts for the explain line (lang=en only; Greek default untouched).
const secondaryGroupNounsEN = {
  alcohol: "hydroxyl",
  aldehyde: "aldehyde group",
  ketone: "ketone group",
  carboxylicAcid: "carboxyl",
  cyanide: "cyano group",
  amine: "amino group",
  nitro: "nitro group",
  ether: "alkoxy group",
  ester: "ester group",
};

const secondaryHalogenNounsEN = {
  Cl: "chlorine",
  Br: "bromine",
  F: "fluorine",
  I: "iodine",
};

const secondaryGroupPluralNounsEN = {
  alcohol: "hydroxyls",
  aldehyde: "aldehyde groups",
  ketone: "ketone groups",
  carboxylicAcid: "carboxyls",
  cyanide: "cyano groups",
  amine: "amino groups",
  nitro: "nitro groups",
  ether: "alkoxy groups",
  ester: "ester groups",
};

const alkylBranchNounsEN = {
  μεθυλο: "methyl",
  αιθυλο: "ethyl",
  προπυλο: "propyl",
  ισοπροπυλο: "isopropyl",
  βουτυλο: "butyl",
  ισοβουτυλο: "isobutyl",
  "sec-βουτυλο": "sec-butyl",
  "tert-βουτυλο": "tert-butyl",
  πεντυλο: "pentyl",
  εξυλο: "hexyl",
  επτυλο: "heptyl",
  οκτυλο: "octyl",
};

const chemicalClassEN = {
  hydrocarbons: "Hydrocarbons",
  alkylHalides: "Alkyl halides",
  alcohols: "Alcohols",
  ethers: "Ethers",
  carbonylCompounds: "Carbonyl compounds",
  carboxylicAcids: "Carboxylic acids",
  esters: "Esters",
  nitriles: "Nitriles",
  amines: "Amines",
  nitro: "Nitro compounds",
  unclassified: "Unclassified",
};

const homologousSeriesEN = {
  alkanes: "Alkanes",
  alkenes: "Alkenes",
  alkadienes: "Alkadienes",
  alkynes: "Alkynes",
  enynes: "Enynes",
  halogen: "Alkyl halides",
  alcohol: "Alcohols",
  ether: "Ethers",
  aldehyde: "Aldehydes",
  ketone: "Ketones",
  carboxylicAcid: "Carboxylic acids",
  ester: "Esters",
  nitro: "Nitro compounds",
  cyanide: "Nitriles",
  hydroxyNitriles: "Hydroxynitriles",
  amine: "Amines",
  aminoAcids: "Amino acids",
  oxoCarboxylicAcids: "Oxocarboxylic acids",
  hydroxyAcids: "Hydroxy acids",
  ketoAcids: "Keto acids",
};

function fIsENMode() {
  try { return typeof fMulerLang === "function" && fMulerLang() === "en"; } catch (e) { return false; }
}

// Branch noun (Greek key in, localized display noun out).
function fBranchNoun(grName) {
  try {
    var m = fIsENMode() ? alkylBranchNounsEN : alkylBranchNouns;
    return (m && m[grName]) || grName;
  } catch (e) { return grName; }
}

// Greek taxonomy label (molTaxonomy / class / series label) → EN in EN mode.
// Includes legacy core spellings ("Καροξυλικά", "Ιμίνες") as aliases;
// the Greek default is never altered.
function fTaxonomyEN(grLabel) {
  if (!fIsENMode()) return grLabel;
  try {
    var _alias = { "Καροξυλικά οξέα": "Carboxylic acids", "Ιμίνες": "Imines", "Αλδεϋδες": "Aldehydes" };
    if (_alias[grLabel]) return _alias[grLabel];
    if (typeof chemicalClassLabels !== "undefined") {
      for (var k in chemicalClassLabels) {
        if (chemicalClassLabels[k] === grLabel && chemicalClassEN[k]) return chemicalClassEN[k];
      }
    }
    if (typeof homologousSeriesLabels !== "undefined") {
      for (var s in homologousSeriesLabels) {
        if (homologousSeriesLabels[s] === grLabel && homologousSeriesEN[s]) return homologousSeriesEN[s];
      }
    }
  } catch (e) {}
  return grLabel;
}

// FG key -> rule-4 table row key. Returns null when the FG has no rule-4 row
// (nitro, halogens, ethers): no highlight instead of a wrong one.
const r4KeyForFG = {
  carboxylicAcid: "r4-carboxylic",
  ester: "r4-alkoxycarbonyl",
  cyanide: "r4-cyano",
  aldehyde: "r4-aldehyde",
  ketone: "r4-keto",
  alcohol: "r4-hydroxy",
  amine: "r4-amino",
};
function fRule4KeysForFGs(fgA, fgB) {
  return [fgA, fgB]
    .map(function (k) { return r4KeyForFG[k] || null; })
    .filter(function (k) { return !!k; });
}

// Resolve the [fgKey, heteroEl] instance behind FGno, using the same
// fgInstances ordering as fHighlightFG (FGno=1 → first name prefix).
// Returns null when FGno matches no functional group (e.g. alkyl branch).
function fGetFGInstance(FGno) {
  const fgKeys = Object.keys(functionalGroupObj).filter(function (k) {
    return k !== "hydrocarbon";
  });
  const fgInstances = [];
  for (let k = 0; k < fgKeys.length; k++) {
    const heteroEls = Object.keys(functionalGroupObj[fgKeys[k]]);
    for (let e = 0; e < heteroEls.length; e++) {
      fgInstances.push([fgKeys[k], heteroEls[e]]);
    }
  }
  const fgPriorityOrder2D = [
    "carboxylicAcid",
    "ester",
    "cyanide",
    "aldehyde",
    "ketone",
    "alcohol",
    "amine",
    "nitro",
    "ether",
  ];
  const halogenOrder2D = Object.keys(nameMainCompObj3.halogen.substitute);
  fgInstances.sort(function (a, b) {
    if (a[0] === "halogen" && b[0] === "halogen") {
      return halogenOrder2D.indexOf(a[1]) - halogenOrder2D.indexOf(b[1]);
    }
    return fgPriorityOrder2D.indexOf(b[0]) - fgPriorityOrder2D.indexOf(a[0]);
  });
  return fgInstances[FGno - 1] || null;
}

// " (Χλώριο)" suffix for explanation messages, or "" when FGno matches
// no functional group.
function fGetSecondaryGroupNounSuffix(FGno) {
  const inst = fGetFGInstance(FGno);
  if (!inst) {
    return "";
  }
  const noun =
    inst[0] === "halogen"
      ? (fIsENMode() ? secondaryHalogenNounsEN : secondaryHalogenNouns)[inst[1]]
      : (fIsENMode() ? secondaryGroupNounsEN : secondaryGroupNouns)[inst[0]];
  return noun ? ` (${noun})` : "";
}

// " (Υδροξύλιο)" / " (Υδροξύλια)" suffix naming the principal (strongest)
// characteristic group, or "" when there is none. Halogens are always
// secondary, so they are skipped (defensive "Αλογόνο" fallback included).
function fGetPrincipalGroupNounSuffix(usePlural) {
  const fgPriorityOrder2D = [
    "carboxylicAcid",
    "ester",
    "cyanide",
    "aldehyde",
    "ketone",
    "alcohol",
    "amine",
    "nitro",
    "ether",
  ];
  const fgKeys = Object.keys(functionalGroupObj).filter(function (k) {
    return k !== "hydrocarbon" && k !== "halogen";
  });
  let principalKey = null;
  for (let i = 0; i < fgPriorityOrder2D.length; i++) {
    if (fgKeys.includes(fgPriorityOrder2D[i])) {
      principalKey = fgPriorityOrder2D[i];
      break;
    }
  }
  if (!principalKey) {
    if (Object.keys(functionalGroupObj).includes("halogen")) {
      return fTX(" (Αλογόνο)", " (halogen)");
    }
    return "";
  }
  const noun = usePlural
    ? (fIsENMode() ? secondaryGroupPluralNounsEN : secondaryGroupPluralNouns)[principalKey]
    : (fIsENMode() ? secondaryGroupNounsEN : secondaryGroupNouns)[principalKey];
  return noun ? ` (${noun})` : "";
}

// Alkyl branch noun (e.g. "μεθύλιο") for pure-hydrocarbon molecules with a
// side branch, or "" otherwise.
function fGetBranchDisplayName() {
  if (
    Object.keys(functionalGroupObj).length !== 1 ||
    !functionalGroupObj.hydrocarbon ||
    !Array.isArray(nameComponentsList) ||
    !nameComponentsList[1]
  ) {
    return "";
  }
  if (fGetHydrocarbonBranchHighlight().atoms.length === 0) {
    return "";
  }
  const prefix = String(nameComponentsList[1]);
  return fBranchNoun(prefix);
}

// ── fExplainNameComp ──────────────────────────────────────────────────────

function fGetNameComponentLocants(component) {
  if (component === null || component === undefined) return [];
  return String(component)
    .replace(/^-+|-+$/g, "")
    .split(/[,\-]+/)
    .map(function (n) {
      return parseInt(n, 10);
    })
    .filter(function (n) {
      return Number.isFinite(n) && n > 0;
    });
}

function fGetNameComponentMultiplier(comp) {
  const s = String(comp || "");
  const prefixes = [
    ["οκτα", 8],
    ["επτα", 7],
    ["εξα", 6],
    ["πεντα", 5],
    ["τετρα", 4],
    ["τρι", 3],
    ["δι", 2],
  ];
  for (let i = 0; i < prefixes.length; i++) {
    if (s.indexOf(prefixes[i][0]) === 0) return prefixes[i][1];
  }
  return 0;
}

function fIsMultiLocantComponent(comp) {
  return fGetNameComponentLocants(comp).length > 1;
}

// Locate the OH-bearing component without confusing it with either C-C
// multiple-bond locant. Mixed branched alcohols group OH locant with -όλη.
function fAlcoholOHNameComponent() {
  if (typeof functionalGroupObj === 'undefined' || !functionalGroupObj ||
      !functionalGroupObj.alcohol || !fSupportsAlkylBranchPrefixes()) return null;
  const branched = fGetHydrocarbonSubstituentInfo().length > 0;
  const db = multiBondsObj.CCd.length, tb = multiBondsObj.CCt.length;
  if (branched && db && tb) return 'compSuffix';
  if (db || tb) return db && tb ? null : 'compEndNumber';
  return branched ? 'compBondPos' : 'compNumber1';
}
function fAlcoholOHPositionText() {
  if (fIsENMode()) {
    return functionalGroupObj.alcohol.O.length > 1
      ? ' Indicates the positions of the hydroxyl groups (–OH).'
      : ' Indicates the position of the hydroxyl group (–OH).';
  }
  return functionalGroupObj.alcohol.O.length > 1
    ? ' Δηλώνει τις θέσεις των υδροξυλομάδων (–OH).'
    : ' Δηλώνει τη θέση της υδροξυλομάδας (–OH).';
}
// Split suffix locants ("-2,7-" beside "διόνη", db+tb ketones/polyols):
// true once the render has emitted the standalone locants box, which keeps
// the suffix slot id for the name itself. The suffix explanation then stays
// a class statement; positions move to the new compSuffixLocants mode.
function fSplitSuffixLocantsActive() {
  try {
    return !!(typeof document !== "undefined" && document.getElementById("comp9loc"));
  } catch (eD) { return false; }
}
// Split branch-label slot ("ισοπροπυλο-4,5-διμεθυλο" in comp0bText, slot 3):
// true once the render has emitted the standalone pieces. Pieces alternate
// name/locants/name; the first name keeps the comp3 slot id so every
// id-driven behavior for unfused molecules is unchanged.
function fSplitBranchPiecesActive() {
  try {
    return !!(typeof document !== "undefined" && document.getElementById("comp3loc"));
  } catch (eD) { return false; }
}
// Pure splitter for a fused branch-label slot. Returns the alternating
// pieces ([name, locants, name, ...]) or null when the slot is not fused.
// Names must be bare Greek-letter runs, locants bare digit runs — labels
// carrying their own dashes (sec-/tert-) stay a single fused box.
function fSplitBranchPieces(text) {
  var parts = String(text == null ? "" : text).split("-");
  if (parts.length < 3 || parts.length % 2 === 0) return null;
  var gk = "[\u0370-\u03ff\u1f00-\u1fff]";
  for (var k = 0; k < parts.length; k++) {
    if (parts[k] === "") return null;
    if (k % 2 === 0) {
      if (!new RegExp("^" + gk + "+$").test(parts[k])) return null;
    } else {
      if (!/^\d[\d,]*$/.test(parts[k])) return null;
    }
  }
  if (parts.join("-") !== String(text)) return null;
  return parts;
}
// Greek substituent sort key (v54.41, P-14.5.1/2 analogue — no official Greek
// guidelines exist, so this mirrors the EN rule): simple substituents ignore
// δι/τρι/τετρα… (διμεθυλο under μ); compound (substituted) substituents sort
// by the first letter of the complete name (διχλωρομεθυλο under δ), leading
// locants skipped.
function fGRSubstSortKey(nm) {
  try {
    var s = String(nm == null ? "" : nm);
    s = s.replace(/[()]/g, "");
    s = s.replace(/^[^\u0370-\u03ff\u1f00-\u1fff]+/, "");
    var low = s.toLowerCase();
    if (/υλ$/.test(low) && /(χλωρο|βρωμο|φθορο|ιωδο|νιτρο)/.test(low)) return s;
    var m = /^(δι|τρι|τετρα|πεντα|εξα|επτα|οκτα)(.+)$/.exec(s);
    if (m && m[2]) return m[2];
    return s;
  } catch (e) { return ""; }
}
// Numeric locants list for the P-14.5.4 tie-break (identical first letters ->
// lowest locants first). Unparseable -> [] (stable fallback).
function fGRLocKey(locText) {
  try {
    var out = [];
    var parts = String(locText == null ? "" : locText).replace(/^[-\s]+/, "").replace(/[-\s]+$/, "").split(/[, \-]+/);
    for (var i = 0; i < parts.length; i++) {
      var n = parseInt(parts[i], 10);
      if (isFinite(n)) out.push(n);
    }
    return out;
  } catch (eL) { return []; }
}
// Substituent groups from sys slots + common slots (v54.41): slot-1 group +
// every slot-3 piece, locants traveling with their group. Mirrors
// fENSubstGroups (P-14.5.1/2). Returns raw-order groups or [].
function fGRSubstGroups(sysSl, comSl) {
  try {
    if (!Array.isArray(sysSl) || !sysSl) return [];
    var gs = [];
    var s1 = sysSl[1], c1 = (comSl && comSl[1] != null) ? comSl[1] : s1;
    if (s1) gs.push({ loc: sysSl[0], name: s1, com: c1, kind: "g1", locId: "comp0", nameId: "comp1" });
    var s3 = sysSl[3], c3 = (comSl && comSl[3] != null) ? comSl[3] : s3;
    if (s3) {
      var pcs = null, ccs = null;
      if (s3 !== c3 && typeof fSysFusedPieces === "function") {
        var sfp = null;
        try { sfp = fSysFusedPieces(); } catch (eSF) { sfp = null; }
        if (sfp && sfp.sys.join("-") === s3) { pcs = sfp.sys; ccs = sfp.com; }
      }
      if (!pcs) {
        var br = null;
        try { if (typeof fSplitBranchPieces === "function") br = fSplitBranchPieces(s3); } catch (eB) { br = null; }
        if (br) { pcs = br; ccs = br.slice(); }
      }
      if (pcs) {
        for (var k = 0; k < pcs.length; k += 2) {
          var j = k / 2;
          gs.push({
            loc: (k === 0) ? sysSl[2] : pcs[k - 1], name: pcs[k], com: ccs[k], kind: "g3",
            locId: (j === 0) ? "comp2" : ("comp3loc" + (j === 1 ? "" : String(j))),
            nameId: (j === 0) ? "comp3" : ("comp3b" + (j === 1 ? "" : String(j - 1)))
          });
        }
      } else {
        gs.push({ loc: sysSl[2], name: s3, com: c3, kind: "g3", locId: "comp2", nameId: "comp3" });
      }
    }
    return gs;
  } catch (eG) { return []; }
}
// Full alphabetical group order (v54.41). Null = legacy path (single group,
// original order, or a non-first group without digit locants — fail-closed).
function fGRSortSubstGroups(gs) {
  try {
    if (!Array.isArray(gs) || gs.length < 2) return null;
    var idx = [];
    for (var i = 0; i < gs.length; i++) idx.push(i);
    idx.sort(function (a, b) {
      var ka = "", kb = "";
      try { ka = fGRSubstSortKey(gs[a].name); } catch (e1) {}
      try { kb = fGRSubstSortKey(gs[b].name); } catch (e2) {}
      if (ka < kb) return -1;
      if (ka > kb) return 1;
      var la = [], lb = [];
      try { la = fGRLocKey(gs[a].loc); } catch (e3) {}
      try { lb = fGRLocKey(gs[b].loc); } catch (e4) {}
      for (var k = 0; k < Math.max(la.length, lb.length); k++) {
        var va = (k < la.length) ? la[k] : 1e9, vb = (k < lb.length) ? lb[k] : 1e9;
        if (va !== vb) return va - vb;
      }
      return a - b;
    });
    var ident = true;
    for (var j = 0; j < idx.length; j++) { if (idx[j] !== j) { ident = false; break; } }
    if (ident) return null;
    for (var m = 1; m < idx.length; m++) {
      if (!/\d/.test(String(gs[idx[m]].loc))) return null;
    }
    return idx;
  } catch (eS) { return null; }
}
// k-th name group (1-based) inside slot 3, for per-piece explanation and
// highlight. Positional: slot-3 names follow the same alphabetical order in
// the fused string and in fGetHydrocarbonBranchGroup(2). Null (halogen-only
// or unmatched pieces) falls back to the slot-level sentences.
function fGetHydrocarbonBranchPiece(k) {
  var g = null;
  try { g = fGetHydrocarbonBranchGroup(2); } catch (eG) { g = null; }
  if (!g || !Array.isArray(g.names) || !Array.isArray(g.members)) return null;
  if (typeof k !== "number" || k < 1 || k > g.names.length) return null;
  var name = g.names[k - 1];
  var members = g.members.filter(function (b) { return b && b.name === name; });
  if (!members.length) return null;
  return { names: [name], members: members };
}
// Box id for a branch-piece mode ("compBranchSub1" -> "comp3",
// "compBranchLoc2" -> "comp3loc", "compBranchSub2" -> "comp3b",
// then "comp3loc2"/"comp3b2", ...). Null when the mode is not a piece mode.
function fBranchPieceBoxId(mode) {
  var m = /^compBranch(Sub|Loc)(\d+)$/.exec(String(mode == null ? "" : mode));
  if (!m) return null;
  var k = parseInt(m[2], 10);
  if (!(k >= 1)) return null;
  if (m[1] === "Sub") {
    if (k === 1) return "comp3";
    return "comp3b" + (k === 2 ? "" : String(k - 1));
  }
  if (k < 2) return null;
  return "comp3loc" + (k === 2 ? "" : String(k - 1));
}
function fBranchedSaturatedKetonePosition() {
  return typeof functionalGroupObj !== 'undefined' && functionalGroupObj &&
    functionalGroupObj.ketone && fSupportsAlkylBranchPrefixes() &&
    fIsAcyclicSaturatedMonoketoneGraph(atomConnectivityList, allAtomsTypeList, bondList) &&
    fGetHydrocarbonSubstituentInfo().length > 0;
}
// Keep the existing numbering policy elsewhere; animate explicit analysis
// of the new ketones and the ten carboxylic acids, not instant zoom/resize overlay restoration.
function fSequentialKetoneNumberingTarget() {
  return ['penten_2_yn_4_oic_acid', 'hexen_2_yn_4_dioic_acid',
    'methyl_2_propenoic_acid', 'ethyl_2_methyl_3_penten_2_yn_4_oic_acid', 'ethyl_3_isopropyl_2_dimethyl_4_5_hexadien_2_4_dioic_acid', 'ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid',
    'methyl_2_propanoic_acid', 'dimethyl_2_2_propanoic_acid',
    'ethyl_2_methyl_3_pentanoic_acid',
    'ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid', 'pentanone_3', 'dimethyl_2_4_pentanone_3',
    'trimethyl_3_4_4_pentanone_2',
    'diethyl_4_5_dimethyl_2_6_heptanone_3',
    'penten_1_yn_4_one_3', 'dimethyl_4_5_hexen_5_yn_1_one_3',
    'methyl_6_hepten_3_dione_2_5', 'ethyl_3_methyl_4_octen_3_yn_5_dione_2_7',
    'isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5'].includes(selectedMol);
}
function fShowAnalysisNumbering(time, overrideAtoms, overrideAtoms3D) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  if (fSequentialKetoneNumberingTarget() && !Array.isArray(overrideAtoms)) {
    currNumberEl = 0;
    document.querySelectorAll('#jsmeNomeclatureSVG text[id^="number"]').forEach(el => el.remove());
    removeEcho3D();
    // Numbering policy: instant (time 0/missing), animated only for time > 0
    // (main-chain carbon-count component). The old-number cleanup above stays.
    fShowNumbering(time);
    return;
  }
  fShowNumbering(time, overrideAtoms, overrideAtoms3D);
}
function fExplainNameComp() {
  // Selection mode owns the viewer: while it is armed, no name-component
  // highlight or explanation is painted — including the classic repaint a 2D
  // style switch runs (fShowNameAnalysis -> fExplainNameComp). The exact quiz
  // verdict opts in for one call via __mulerQuizReward so the green reward is
  // the only highlight the user ever sees while selecting.
  try {
    var _selOwnsViewer = (typeof fMulerSelectActive === "function") && fMulerSelectActive();
    var _rewardPaint = (typeof window !== "undefined") && window.__mulerQuizReward === true;
    // Explain-all builds scrape this function's explanation HTML with paints
    // suppressed (__mulerExplainQuiet): the text must still be generated there,
    // otherwise the table nests its own previous markup or repeats the quiz
    // prompt in every cell.
    var _quietExplainBuild = (typeof window !== "undefined") && window.__mulerExplainQuiet === true;
    if (_selOwnsViewer && !_rewardPaint && !_quietExplainBuild) return;
  } catch (eSelOwn) {}
  let myText, myClass, nStyle, countSubs, myCountText, myFG0, myFG1, myHTML;
  switch (nameAnalysisMode) {
    case "none":
      myText = fTX(
        "Κάνε κλικ σε ένα συνθετικό του ονόματος για να δεις την εξήγηση",
        "Click a name component to see its explanation");
      nStyle =
        "color:#666; font-style:italic; font-weight:normal; border:0;background-color:transparent;font-size:1rem;box-shadow:0 0 #fff;";
      myClass = "";
      ruleFlag = false;
      numberingFlag = false;
      break;
    case "compAcidNumber3":
    case "compAcidSub3": {
      const group = fSeparateAcidPrefixBoxes() ? fGetHydrocarbonBranchGroup(3) : null;
      nStyle = ""; myClass = "";
      const positions = nameAnalysisMode === 'compAcidNumber3';
      myText = group ? fHydrocarbonBranchExplanation(group, positions) : '';
      numberingFlag = !!group && positions;
      if (group) {
        fHighlightFG(3); fHighlightFG3D(3);
        if (positions) fShowAnalysisNumbering(0);
        $("#ruleTheoryContainer").show();
      }
      break;
    }
    case "compNumber1":
      nStyle = "";
      myClass = "";
      const branchGroup_compNumber1 = fGetHydrocarbonBranchGroup(1);
      if (branchGroup_compNumber1) {
        myText = fHydrocarbonBranchExplanation(branchGroup_compNumber1, true);
        numberingFlag = true;
        if (!fPaintBranchHighlightAtoms(1, "compNumber1")) { fHighlightFG(1); fHighlightFG3D(1); }
        fShowAnalysisNumbering(0);
        $("#ruleTheoryContainer").show();
        break;
      }
      if (nameComponentsList[1] !== null && nameComponentsList[1].length > 0) {
        if (
          nameComponentsList[3] !== null &&
          nameComponentsList[3].length > 0
        ) {
          myText = fIsMultiLocantComponent(nameComponentsList[0])
          ? fTX(` Δηλώνει τις θέσεις της πρώτης αλφαβητικά δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(1)}.`, ` Indicates the positions of the alphabetically first secondary characteristic group${fGetSecondaryGroupNounSuffix(1)}.`)
          : fTX(` Δηλώνει τη θέση της πρώτης αλφαβητικά δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(1)}.`, ` Indicates the position of the alphabetically first secondary characteristic group${fGetSecondaryGroupNounSuffix(1)}.`);
          fHighlightFG(1);
          fHighlightFG3D(1);
        } else {
          if (nameComponentsList[0].includes(",")) {
            countSubs = (nameComponentsList[0].match(/,/g) || []).length;
            switch (countSubs) {
              case 1:
                myCountText = fTX(" δύο ", " two ");
                break;
              case 2:
                myCountText = fTX(" τριών", " three");
                break;
              default:
                myCountText = "";
            }

            myText = fTX(` Δηλώνει τις θέσεις των ${myCountText} δευτερευουσών  Χαρακτηριστικών Ομάδών${fGetSecondaryGroupNounSuffix(1)}.`, ` Indicates the positions of the${myCountText} secondary characteristic groups${fGetSecondaryGroupNounSuffix(1)}.`);
          } else {
            const branchPosName = fGetBranchDisplayName();
            if (branchPosName) {
              myText = fTX(` Δηλώνει τη θέση της ανθρακικής διακλάδωσης (`, ` Indicates the position of the carbon branch (`) + branchPosName + ").";
            } else {
              myText = fTX(` Δηλώνει τη θέση της δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(1)}.`, ` Indicates the position of the secondary characteristic group${fGetSecondaryGroupNounSuffix(1)}.`);
            }
          }

          if (Object.keys(functionalGroupObj).length > 1) {
            fHighlightFG(1);
            fHighlightFG3D(1);
            myFG0 = functionalGroupsList[0];
            myFG1 = functionalGroupsList[1];
            ruleTableHighlight = fRule4KeysForFGs(myFG0, myFG1);
            $("#ruleTheoryContainer").show();
          } else {
            fHighlightFG();
            fHighlightFG3D();
          }
        }
      } else if (
        (nameComponentsList[6] == "άν" ||
        nameComponentsList[6] == "αν") &&
        (function () {
          try {
            var _r1 = (typeof fMulerNumber1Resolved === "function") ? fMulerNumber1Resolved() : null;
            return !!(_r1 && _r1.length);
          } catch (eR1) { return true; }
        })()
      ) {
        if (nameComponentsList[0].includes(",")) {
          countSubs = (nameComponentsList[0].match(/,/g) || []).length;
          switch (countSubs) {
            case 1:
              myCountText = fTX(" δύο ", " two ");
              break;
            case 2:
              myCountText = fTX(" τριών", " three");
              break;
            default:
              myCountText = "";
          }

          myText = fTX(` Δηλώνει τις θέσεις των ${myCountText}  Χαρακτηριστικών Ομάδών${fGetPrincipalGroupNounSuffix(true)}.`, ` Indicates the positions of the${myCountText} characteristic groups${fGetPrincipalGroupNounSuffix(true)}.`);
        } else {
          myText = fTX(` Δηλώνει τη θέση της Χαρακτηριστικής Ομάδας${fGetPrincipalGroupNounSuffix(false)}.`, ` Indicates the position of the characteristic group${fGetPrincipalGroupNounSuffix(false)}.`);
        }

        fHighlightFG();
        fHighlightFG3D();
      } else {
        switch (nameComponentsList[6]) {
          case "έν":
          case "εν":
            myText = fTX(" Δηλώνει τη θέση του διπλού δεσμού.", " Indicates the position of the double bond.");
            ruleTableHighlight = "r2-double";
            break;
          case "διέν":
          case "διεν":
            myText = fTX(" Δηλώνει τις θέσεις των διπλών δεσμών.", " Indicates the positions of the double bonds.");
            ruleTableHighlight = "r2-didouble";
            break;
          case "ίν":
          case "ιν":
            myText = fTX(" Δηλώνει τη θέση του τριπλού δεσμού.", " Indicates the position of the triple bond.");
            ruleTableHighlight = "r2-triple";
            break;
          case "διίν":
          case "διιν":
            myText = fTX(" Δηλώνει τις θέσεις των τριπλών δεσμών.", " Indicates the positions of the triple bonds.");

            ruleTableHighlight = "r2-ditriple";
            break;
          default:
          // myText = " Δηλώνει τη θέση του Πολλαπλού Δεσμού."
        }
        fHighlightMultiBonds(1);
        fHighlightMultiBonds3D(1);
        //
        $("#ruleTheoryContainer").show();
      }
      numberingFlag = true;
      fShowAnalysisNumbering(0);
      break;
    case "compSecondSub1":
      numberingFlag = false;
      nStyle = "";
      myClass = "";
      const branchGroup_compSecondSub1 = fGetHydrocarbonBranchGroup(1);
      if (branchGroup_compSecondSub1) {
        myText = fHydrocarbonBranchExplanation(branchGroup_compSecondSub1, false);
        numberingFlag = false;
        if (!fPaintBranchHighlightAtoms(1, "compSecondSub1")) { fHighlightFG(1); fHighlightFG3D(1); }
        $("#ruleTheoryContainer").show();
        break;
      }
      if (
        functionalGroupsList.length === 1 &&
        functionalGroupsList[0] === "ether"
      ) {
        // IUPAC alkoxy prefix (e.g. μεθοξυ): highlight O + alkoxy fragment.
        // Name box: no numbering (locants only).
        myText = fTX(` Δηλώνει το όνομα της αλκοξυομάδας${fGetSecondaryGroupNounSuffix(1)}.`, ` Indicates the name of the alkoxy group${fGetSecondaryGroupNounSuffix(1)}.`);
        fHighlightFG(1);
        fHighlightFG3D(1);
        numberingFlag = false;
        $("#ruleTheoryContainer").show();
        break;
      }
      if (nameComponentsList[3] !== null && nameComponentsList[3].length > 0) {
        myText = fGetNameComponentMultiplier(nameComponentsList[1]) > 1
          ? fTX(` Δηλώνει το πλήθος των δευτερευουσών Χαρακτηριστικών Ομάδων${fGetSecondaryGroupNounSuffix(1)}.`, ` Indicates the number of the secondary characteristic groups${fGetSecondaryGroupNounSuffix(1)}.`)
          : fTX(` Δηλώνει το όνομα  της πρώτης αλφαβητικά δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(1)}.`, ` Indicates the name of the alphabetically first secondary characteristic group${fGetSecondaryGroupNounSuffix(1)}.`);
        fHighlightFG(1);
        fHighlightFG3D(1);
      } else {
        if (Object.keys(functionalGroupObj).length > 1) {
          fHighlightFG(1);
          fHighlightFG3D(1);

          // Βρισκει τις υπαρχουσες ΧΟ και επιλέγει τη σειρά στον πινακα
          myFG0 = functionalGroupsList[0];
          myFG1 = functionalGroupsList[1];
          ruleTableHighlight = fRule4KeysForFGs(myFG0, myFG1);
          $("#ruleTheoryContainer").show();
        } else {
          fHighlightFG();
          fHighlightFG3D();
        }
        const branchSubName = fGetBranchDisplayName();
        if (branchSubName) {
          myText = fTX(` Δηλώνει το όνομα της ανθρακικής διακλάδωσης (`, ` Indicates the name of the carbon branch (`) + branchSubName + ").";
        } else {
          myText = fGetNameComponentMultiplier(nameComponentsList[1]) > 1
            ? fTX(` Δηλώνει το πλήθος των δευτερευουσών Χαρακτηριστικών Ομάδων${fGetSecondaryGroupNounSuffix(1)}.`, ` Indicates the number of the secondary characteristic groups${fGetSecondaryGroupNounSuffix(1)}.`)
            : fTX(` Δηλώνει το όνομα της δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(1)}.`, ` Indicates the name of the secondary characteristic group${fGetSecondaryGroupNounSuffix(1)}.`);
        }
      }

      break;
    case "compNumber2":
      nStyle = "";
      myClass = "";
      let branchGroup_compNumber2 = fGetHydrocarbonBranchGroup(2);
      // Locants-box scope (v54.35): explain only the first of the remaining
      // groups — the box shows that group's locants. Mirrors the 2D/3D
      // highlight narrowing; the existing single-group sentence then fires,
      // making multi-group behave exactly like the single-group case.
      if (branchGroup_compNumber2 && Array.isArray(branchGroup_compNumber2.names) &&
          branchGroup_compNumber2.names.length > 1) {
        try {
          const _fmN = (branchGroup_compNumber2.members || []).filter(function (b) { return b && b.name === branchGroup_compNumber2.names[0]; });
          if (_fmN.length) branchGroup_compNumber2 = { names: [branchGroup_compNumber2.names[0]], members: _fmN };
        } catch (eN2) {}
      }
      if (branchGroup_compNumber2) {
        myText = fHydrocarbonBranchExplanation(branchGroup_compNumber2, true);
        numberingFlag = true;
        if (!fPaintBranchHighlightAtoms(2, "compNumber2")) { fHighlightFG(2); fHighlightFG3D(2); }
        fShowAnalysisNumbering(0);
        $("#ruleTheoryContainer").show();
        break;
      }
      myText = fIsMultiLocantComponent(nameComponentsList[2])
          ? fTX(` Δηλώνει τις θέσεις της δεύτερης αλφαβητικά δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(2)}.`, ` Indicates the positions of the alphabetically second secondary characteristic group${fGetSecondaryGroupNounSuffix(2)}.`)
          : fTX(` Δηλώνει τη θέση της δεύτερης αλφαβητικά δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(2)}.`, ` Indicates the position of the alphabetically second secondary characteristic group${fGetSecondaryGroupNounSuffix(2)}.`);
      numberingFlag = true;

      fHighlightFG(2);
      fHighlightFG3D(2);
      fShowAnalysisNumbering(0);
      break;
    case "compSecondSub2":
      nStyle = "";
      myClass = "";
      const branchGroup_compSecondSub2 = fGetHydrocarbonBranchGroup(2);
      if (branchGroup_compSecondSub2) {
        myText = fHydrocarbonBranchExplanation(branchGroup_compSecondSub2, false);
        numberingFlag = false;
        if (!fPaintBranchHighlightAtoms(2, "compSecondSub2")) { fHighlightFG(2); fHighlightFG3D(2); }
        $("#ruleTheoryContainer").show();
        break;
      }
      myText = fGetNameComponentMultiplier(nameComponentsList[3]) > 1
          ? fTX(` Δηλώνει το πλήθος των δευτερευουσών Χαρακτηριστικών Ομάδων${fGetSecondaryGroupNounSuffix(2)}.`, ` Indicates the number of the secondary characteristic groups${fGetSecondaryGroupNounSuffix(2)}.`)
          : fTX(` Δηλώνει το όνομα  της δεύτερης αλφαβητικά δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(2)}.`, ` Indicates the name of the alphabetically second secondary characteristic group${fGetSecondaryGroupNounSuffix(2)}.`);
      numberingFlag = false;
      fHighlightFG(2);
      fHighlightFG3D(2);
      break;
    case "compBondPos":
      nStyle = "";
      myClass = "";
      if (fBranchedSaturatedKetonePosition() && (function () {
        try {
          var _r = (typeof fMulerBondPosResolved === "function") ? fMulerBondPosResolved() : null;
          return !!(_r && _r.length);
        } catch (eR) { return true; }
      })()) {
        myText = fTX(' Δηλώνει τη θέση της καρβονυλομάδας (>C=O).', ' Indicates the position of the carbonyl group (>C=O).');
        ruleTableHighlight = 'r3-ketones';
        fHighlightFG(); fHighlightFG3D();
        numberingFlag = true; fShowAnalysisNumbering(0);
        $('#ruleTheoryContainer').show();
        break;
      }
      if (fAlcoholOHNameComponent() === 'compBondPos' && (function () {
        try {
          var _r2 = (typeof fMulerBondPosResolved === "function") ? fMulerBondPosResolved() : null;
          return !!(_r2 && _r2.length);
        } catch (eR2) { return true; }
      })()) {
        myText = fAlcoholOHPositionText();
        ruleTableHighlight = "r3-alcohols";
        fHighlightFG(); fHighlightFG3D();
        numberingFlag = true; fShowAnalysisNumbering(0);
        $("#ruleTheoryContainer").show();
        break;
      }
      // Saturated single-FG locant (e.g. 2-πεντανόνη, 2-πεντανόλη in box comp4):
      // the classic fell through to the multiple-bond text with nothing to
      // paint. The box holds the FG position, so paint the group (reward +
      // classic agree, quiz armed via the matching resolver). The locant may
      // live in slots {0,4,7} (EN renders the slot-0/7 locant in comp4).
      // A digit-led box that names no FG locant belongs to a bond: fall
      // through to the multiple-bond handling below instead.
      if (typeof functionalGroupsList !== "undefined" && functionalGroupsList &&
          functionalGroupsList.length === 1 &&
          (functionalGroupsList[0] === 'ketone' || functionalGroupsList[0] === 'alcohol') &&
          (function () {
            try {
              if (typeof nameComponentsList === "undefined" || !nameComponentsList) return false;
              var stripLoc = function (t) { return String(t == null ? "" : t).replace(/^[-\s]+/, "").replace(/[-\s]+$/, ""); };
              return /^\d/.test(stripLoc(nameComponentsList[4])) || /^\d/.test(stripLoc(nameComponentsList[0])) || /^\d/.test(stripLoc(nameComponentsList[7]));
            } catch (eS) { return false; }
          })() &&
          (function () {
            try {
              var _r = (typeof fMulerBondPosResolved === "function") ? fMulerBondPosResolved() : null;
              return !!(_r && _r.length);
            } catch (eR) { return true; }
          })()) {
        if (functionalGroupsList[0] === 'ketone') {
          myText = fTX(' Δηλώνει τη θέση της καρβονυλομάδας (>C=O).', ' Indicates the position of the carbonyl group (>C=O).');
          ruleTableHighlight = 'r3-ketones';
        } else {
          myText = fAlcoholOHPositionText();
          ruleTableHighlight = "r3-alcohols";
        }
        fHighlightFG(); fHighlightFG3D();
        numberingFlag = true; fShowAnalysisNumbering(0);
        $("#ruleTheoryContainer").show();
        break;
      }
      switch (nameComponentsList[6]) {
        case "έν":
        case "εν":
          myText = fTX(" Δηλώνει τη θέση του διπλού δεσμού.", " Indicates the position of the double bond.");
          ruleTableHighlight = "r2-double";
          break;
        case "ίν":
        case "ιν":
          myText = fTX(" Δηλώνει τη θέση του τριπλού δεσμού.", " Indicates the position of the triple bond.");
          ruleTableHighlight = "r2-triple";
          break;
        case "διέν":
        case "διεν":
          myText = fTX(" Δηλώνει τις θέσεις των διπλών δεσμών.", " Indicates the positions of the double bonds.");
          ruleTableHighlight = "r2-didouble";
          break;
        default:
          myText = fTX(" Δηλώνει τη θέση του Πολλαπλού Δεσμού.", " Indicates the position of the multiple bond.");
      }
      fHighlightMultiBonds(1);
      fHighlightMultiBonds3D(1);
      numberingFlag = true;
      fShowAnalysisNumbering(0);
      $("#ruleTheoryContainer").show();
      break;
    case "compCarbonsCount":
      if (fIsSingleEster()) {
        // Ester acid-stem click (e.g. αιθ-): the name counts the ACID carbons,
        // so text + highlight + numbering follow the named acid parent chain,
        // not the longest chain (which may run through the alcohol part).
        var _acidChain = fGetEsterAcidParentChain();
        var _acidChain3D = fGetEsterAcidParentChain3D();
        var _acidParentLen = _acidChain ? _acidChain.length : esterInfo.acidLen;
        myText = _acidParentLen === esterInfo.acidLen
          ? fTX(`Το οξύ-τμήμα του εστέρα έχει ${esterInfo.acidLen} άτομα άνθρακα C`, `The acid part of the ester has ${esterInfo.acidLen} carbon atoms`)
          : fTX(`Η κύρια αλυσίδα του όξινου τμήματος του εστέρα έχει ${_acidParentLen} άτομα άνθρακα C`, `The main chain of the acid part of the ester has ${_acidParentLen} carbon atoms`);
        nStyle = "";
        myClass = "";
        ruleTableHighlight = `r1-c${_acidParentLen}`;
        numberingFlag = true;
        // Numbering highlight, atoms and bonds gated independently
        // (either checkbox alone still paints its half).
        var _showA = false, _showB = true;
        try { _showA = $("#highlightNumberingCheck").hasClass("selectedCheck"); } catch (eA) { _showA = false; }
        try { _showB = (typeof fShowNumberingBonds === "function") ? fShowNumberingBonds() : true; } catch (eB2) { _showB = true; }
        if (_showA || _showB) {
          if (_acidChain && _acidChain.length > 0) fHighlightAtomChain(_acidChain, true, !_showB, !_showA);
          if (_acidChain3D && _acidChain3D.length > 0) fHighlightAtomChain3D(_acidChain3D, true, !_showB, !_showA);
        }
        // Numbering follows the acid parent numbering (carbonyl C = 1),
        // sequential along the longest saturated chain from it (v54.39).
        var _acidNum = _acidChain, _acidNum3 = _acidChain3D;
        try {
          var _aOrd = (typeof fEsterAcidNumbering === "function") ? fEsterAcidNumbering(_acidChain) : null;
          var _aOrd3 = (typeof fEsterAcidNumbering3D === "function") ? fEsterAcidNumbering3D(_acidChain3D) : null;
          if (_aOrd && _aOrd.length) _acidNum = _aOrd;
          if (_aOrd3 && _aOrd3.length) _acidNum3 = _aOrd3;
        } catch (eANa) {}
        fShowAnalysisNumbering(0, _acidNum, _acidNum3);
        $("#ruleTheoryContainer").show();
        break;
      }
      myText = fTX(`Η κύρια αλυσίδα έχει ${mainChainAtomsList.length} άτομα άνθρακα C`, `The main chain has ${mainChainAtomsList.length} carbon atoms`);
      nStyle = "";
      myClass = "";
      ruleTableHighlight =
        `r1-c${Array.isArray(mainChainAtomsList) && mainChainAtomsList.length
          ? mainChainAtomsList.length
          : carbons}`;
      numberingFlag = true;
      // Numbering highlight, atoms and bonds gated independently
      // (either checkbox alone still paints its half).
      var _showA2 = false, _showB2 = true;
      try { _showA2 = $("#highlightNumberingCheck").hasClass("selectedCheck"); } catch (eA2) { _showA2 = false; }
      try { _showB2 = (typeof fShowNumberingBonds === "function") ? fShowNumberingBonds() : true; } catch (eB3) { _showB2 = true; }
      if (_showA2) fHighLightMainChain();
      if (_showB2) fHighLightMainChainBonds();
      if (_showA2 || _showB2) fHighlightAtomChain3D(mainChainAtoms3D, true, !_showB2, !_showA2);
      // Main-chain carbon-count component: the sole animated numbering reveal.
      fShowAnalysisNumbering(400);
      $("#ruleTheoryContainer").show();
      break;
    case "compBondType":
      switch (nameComponentsList[6]) {
        case "αν":
        case "άν":
          myText = fTX("μόνο απλούς δεσμούς μεταξύ των ατόμων άνθρακα", "only single bonds between the carbon atoms");
          ruleTableHighlight = "r2-single";
          break;
        case "εν":
        case "έν":
          myText = fTX("έναν διπλό δεσμο μεταξύ των ατόμων άνθρακα", "one double bond between the carbon atoms");
          ruleTableHighlight = "r2-double";
          break;
        case "ίν":
        case "ιν":
          myText = fTX("έναν τριπλό δεσμό μεταξύ των ατόμων άνθρακα", "one triple bond between the carbon atoms");
          ruleTableHighlight = "r2-triple";
          break;
        case "διέν":
        case "διεν":
          myText = fTX("δύο διπλούς δεσμούς μεταξύ των ατόμων άνθρακα", "two double bonds between the carbon atoms");
          ruleTableHighlight = "r2-didouble";
          break;
        default:
          myText = fTX("μόνο απλούς δεσμούς μεταξύ των ατόμων άνθρακα", "only single bonds between the carbon atoms");
          ruleTableHighlight = "r2-single";
      }
      myText = fTX(`Έχει `, `It has `) + `${myText}`;
      nStyle = "";
      myClass = "";
      numberingFlag = false;
      if (nameComponentsList[6] === "αν" || nameComponentsList[6] === "άν") {
        if (fIsSingleEster()) {
          // Ester -αν-: only the acid C–C single bond(s), not every C–C single
          // bond in the molecule (the alcohol part has its own boxes).
          fHighlightSingleBondsCC(fGetEsterAcidChain());
          fHighlightSingleBondsCC3D(fGetEsterAcidChain3D());
        } else {
          fHighlightSingleBondsCC();
          fHighlightSingleBondsCC3D();
        }
      } else {
        fHighlightMultiBonds(1);
        fHighlightMultiBonds3D(1);
      }
      $("#ruleTheoryContainer").show();
      break;
    case "compBondType2":
      switch (nameComponentsList[8]) {
        case "άν":
          myText = fTX("μόνο απλούς δεσμούς μεταξύ των ατόμων άνθρακα", "only single bonds between the carbon atoms");
          ruleTableHighlight = "r2-single";
          break;
        case "αν":
          myText = fTX("μόνο απλούς δεσμούς μεταξύ των ατόμων άνθρακα", "only single bonds between the carbon atoms");
          ruleTableHighlight = "r2-single";
          break;
        case "έν":
          myText = fTX("έναν διπλό δεσμο μεταξύ των ατόμων άνθρακα", "one double bond between the carbon atoms");
          ruleTableHighlight = "r2-double";
          break;
        case "εν":
          myText = fTX("έναν διπλό δεσμο μεταξύ των ατόμων άνθρακα", "one double bond between the carbon atoms");
          ruleTableHighlight = "r2-double";
          break;
        case "ίν":
          myText = fTX("έναν τριπλό δεσμό μεταξύ των ατόμων άνθρακα", "one triple bond between the carbon atoms");
          ruleTableHighlight = "r2-triple";
          break;
        case "ιν":
          myText = fTX("έναν τριπλό δεσμό μεταξύ των ατόμων άνθρακα", "one triple bond between the carbon atoms");
          ruleTableHighlight = "r2-triple";
          break;
        case "διέν":
          myText = fTX("δύο διπλούς δεσμούς μεταξύ των ατόμων άνθρακα", "two double bonds between the carbon atoms");
          ruleTableHighlight = "r2-didouble";
          break;
        case "διεν":
          myText = fTX("δύο διπλούς δεσμούς μεταξύ των ατόμων άνθρακα", "two double bonds between the carbon atoms");
          ruleTableHighlight = "r2-didouble";
          break;
        default:
          myText = fTX("μόνο απλούς δεσμούς μεταξύ των ατόμων άνθρακα", "only single bonds between the carbon atoms");
          ruleTableHighlight = "r2-single";
      }
      myText = fTX(`Έχει `, `It has `) + `${myText}`;
      nStyle = "";
      myClass = "";
      numberingFlag = false;
      fHighlightMultiBonds(2);
      fHighlightMultiBonds3D(2);
      $("#ruleTheoryContainer").show();
      break;
    case "compEndNumber":
      nStyle = "";
      myClass = "";
      if (functionalGroupsList.length === 1 && functionalGroupsList[0] === 'ketone' &&
          fIsAcyclicKetoneGraph(atomConnectivityList, allAtomsTypeList, bondList) &&
          !fIsAcyclicSaturatedMonoketoneGraph(atomConnectivityList, allAtomsTypeList, bondList) &&
          nameComponentsList[8].length === 0 &&
          (function () {
            try {
              var _re = (typeof fMulerEndNumberResolved === "function") ? fMulerEndNumberResolved() : null;
              return !!(_re && _re.length);
            } catch (eRe) { return true; }
          })()) {
        myText = fTX(' Δηλώνει ', ' Indicates ') + (functionalGroupObj.ketone.O.length > 1 ? fTX('τις θέσεις των καρβονυλομάδων', 'the positions of the carbonyl groups') : fTX('τη θέση της καρβονυλομάδας', 'the position of the carbonyl group')) + ' (>C=O).';
        ruleTableHighlight = 'r3-ketones';
        fHighlightFG(); fHighlightFG3D();
        numberingFlag = true; fShowAnalysisNumbering(0);
        $('#ruleTheoryContainer').show();
        break;
      }
      if ((fAlcoholOHNameComponent() === 'compEndNumber' || nameComponentsList[8].length === 0) &&
          (function () {
            try {
              var _re2 = (typeof fMulerEndNumberResolved === "function") ? fMulerEndNumberResolved() : null;
              return !!(_re2 && _re2.length);
            } catch (eRe2) { return true; }
          })()) {
        fHighlightFG();
        fHighlightFG3D();
        myText = fAlcoholOHNameComponent() === 'compEndNumber' ? fAlcoholOHPositionText()
          : fTX(` Δηλώνει τη θέση της  Χαρακτηριστικής Ομάδας${fGetPrincipalGroupNounSuffix(false)}.`, ` Indicates the position of the characteristic group${fGetPrincipalGroupNounSuffix(false)}.`);
      } else {
        myText = fTX(" Δηλώνει τη θέση του τριπλού δεσμού.", " Indicates the position of the triple bond.");
        ruleTableHighlight = "r2-triple";
        fHighlightMultiBonds3D(2);
        fHighlightMultiBonds(2);
      }
      numberingFlag = true;
      fShowAnalysisNumbering(0);
      break;
    case "compSuffixLocants": {
      // Split-off suffix locants ("-2,7-" beside "διόνη"): positions only.
      // The class sentence stays on the suffix box (compSuffix mode).
      nStyle = "";
      myClass = "";
      const _locKetone = typeof functionalGroupsList !== "undefined" && functionalGroupsList &&
        functionalGroupsList.length === 1 && functionalGroupsList[0] === 'ketone' &&
        fIsAcyclicKetoneGraph(atomConnectivityList, allAtomsTypeList, bondList) &&
        multiBondsObj.CCd.length > 0 && multiBondsObj.CCt.length > 0;
      if (_locKetone) {
        const _locN = functionalGroupObj.ketone.O.length;
        myText = _locN > 1
          ? fTX('Δηλώνει τις θέσεις των ', 'It indicates the positions of the ') + _locN + fTX(' καρβονυλομάδων (>C=O).', ' carbonyl groups (>C=O).')
          : fTX('Δηλώνει τη θέση της καρβονυλομάδας (>C=O).', 'It indicates the position of the carbonyl group (>C=O).');
        ruleTableHighlight = "r3-ketones";
      } else if (fAlcoholOHNameComponent() === 'compSuffix') {
        myText = fAlcoholOHPositionText().trim();
        ruleTableHighlight = 'r3-alcohols';
      } else {
        // Defensive: locants box without a split parent — class statement.
        myText = fIsENMode() ? ("It belongs to the chemical class " + fTaxonomyEN(molTaxonomy) + ".") : ("Ανήκει στη Χημική Τάξη " + molTaxonomy + ".");
      }
      if (molTaxonomy != "Υδρογονάνθρακες") {
        if (Object.keys(functionalGroupObj).length > 1) {
          fHighlightFG(2);
          fHighlightFG3D(2);
        } else {
          fHighlightFG();
          fHighlightFG3D();
        }
      }
      numberingFlag = true;
      fShowAnalysisNumbering(0);
      $("#ruleTheoryContainer").show();
      break;
    }
    case "compSuffix":
      // myText = "Ανήκει στη χημική τάξη " + molTaxonomy;
      const chemicalClass =
        nameExamples[selectedMol]?.classification?.chemicalClass;

      const myChemClass = chemicalClassLabels[chemicalClass] || molTaxonomy;
      const _seriesKey = nameExamples[selectedMol]?.classification?.seriesKey;
      const _seriesLabel =
        (typeof homologousSeriesLabels !== "undefined" && _seriesKey && homologousSeriesLabels[_seriesKey]) || "";
      if (fIsENMode()) {
        const _ccEN = (typeof chemicalClassEN !== "undefined" && chemicalClass && chemicalClassEN[chemicalClass]) || fTaxonomyEN(myChemClass);
        const _srEN = (typeof homologousSeriesEN !== "undefined" && _seriesKey && homologousSeriesEN[_seriesKey]) || "";
        myText = `It belongs to the chemical class ${_ccEN}`;
        if (_srEN && _srEN.toLowerCase() !== String(_ccEN).toLowerCase()) {
          myText += ` and to the homologous series ${_srEN}.`;
        } else {
          myText += ".";
        }
        // EN: Greek common names are data, not chrome — clause omitted.
      } else {
        myText = `Ανήκει στη Χημική Τάξη ${myChemClass}`;
        if (_seriesLabel && _seriesLabel.toLocaleLowerCase("el") !== myChemClass.toLocaleLowerCase("el")) {
          myText += ` και στην Ομόλογη Σειρά ${_seriesLabel}.`;
        } else {
          myText += ".";
        }
        if (typeof currentMolCommonName !== "undefined" && currentMolCommonName) {
          myText += ` Κοινή ονομασία: ${currentMolCommonName}`;
        }
      }
      nStyle = "";
      myClass = "";

      switch (myChemClass) {
        case "Υδρογονάνθρακες":
          ruleTableHighlight = "r3-hydrocarbons";
          break;
        case "Αλκυλαλογονίδια":
          ruleTableHighlight = "r3-alkyl-halides";
          break;
        case "Νιτροενώσεις":
          ruleTableHighlight = "r3-nitro";
          break;
        case "Αλκοόλες":
          ruleTableHighlight = "r3-alcohols";
          break;
        case "Αλδεΰδες":
          ruleTableHighlight = "r3-aldehydes";
          break;
        case "Κετόνες":
          ruleTableHighlight = "r3-ketones";
          break;
        case "Καρβονυλικές Ενώσεις":
          // Single row via series below (Αλδεϋδες=5 xor Κετόνες=6).
          break;
        case "Καρβοξυλικά Οξέα":
          ruleTableHighlight = "r3-carboxylic-acids";
          break;
        case "Νιτρίλια":
          ruleTableHighlight = "r3-nitriles";
          break;
        case "Αιθέρες":
          ruleTableHighlight = "r3-ethers";
          break;
        case "Εστέρες":
          ruleTableHighlight = "r3-esters";
          break;
      }
      if (chemicalClass === "carbonylCompounds") {
        if (_seriesKey === "aldehyde") ruleTableHighlight = "r3-aldehydes";
        else if (_seriesKey === "ketone") ruleTableHighlight = "r3-ketones";
      }
      const ketoneSuffixLocants = functionalGroupsList.length === 1 && functionalGroupsList[0] === 'ketone' &&
        fIsAcyclicKetoneGraph(atomConnectivityList, allAtomsTypeList, bondList) &&
        multiBondsObj.CCd.length > 0 && multiBondsObj.CCt.length > 0;
      // Class box: no numbering even when it carries positions in text
      // (locants only) — split or not, numbers live on locant boxes.
      numberingFlag = false;
      // Split suffix: the positions sentences live on the standalone
      // locants box (compSuffixLocants mode) — the suffix keeps the class
      // statement, the highlight, and no numbering.
      const _splitLoc = fSplitSuffixLocantsActive();
      if (!_splitLoc && ketoneSuffixLocants) myText += fTX(' Δηλώνει ', ' Indicates ') + (functionalGroupObj.ketone.O.length > 1 ? fTX('τις θέσεις των καρβονυλομάδων', 'the positions of the carbonyl groups') : fTX('τη θέση της καρβονυλομάδας', 'the position of the carbonyl group')) + ' (>C=O).';
      if (!_splitLoc && fAlcoholOHNameComponent() === 'compSuffix') {
        myText += fAlcoholOHPositionText();
      }
      if (molTaxonomy != "Υδρογονάνθρακες") {
        if (Object.keys(functionalGroupObj).length > 1) {
          fHighlightFG(2);
          fHighlightFG3D(2);
        } else {
          fHighlightFG();
          fHighlightFG3D();
        }
      }
      $("#ruleTheoryContainer").show();
      break;
    case "commonAlkyl1":
    case "commonAlkyl2": {
      // COMMON alkyl click: highlight that alkyl chain only (no O).
      // Name box: no numbering (locants only).
      nStyle = "";
      myClass = "";
      const _parts = fGetEtherCommonParts();
      const _idx = nameAnalysisMode === "commonAlkyl1" ? 0 : 1;
      const _part = _parts && _parts.parts ? _parts.parts[_idx] : null;
      if (_parts && _parts.symmetric) {
        myText =
          _idx === 0
            ? fTX('Δηλώνει το πρόθεμα δι- του συμμετρικού αιθέρα.', 'It indicates the prefix di- of the symmetric ether.')
            : fTX('Δηλώνει το αλκύλιο του συμμετρικού αιθέρα.', 'It indicates the alkyl group of the symmetric ether.');
      } else {
        myText =
          _idx === 0
            ? fTX('Δηλώνει το πρώτο αλφαβητικά αλκύλιο του αιθέρα.', 'It indicates the alphabetically first alkyl group of the ether.')
            : fTX('Δηλώνει το δεύτερο αλφαβητικά αλκύλιο του αιθέρα.', 'It indicates the alphabetically second alkyl group of the ether.');
      }
      const _chain = _part && Array.isArray(_part.chain) ? _part.chain : null;
      const _chain3D = _part && Array.isArray(_part.chain3D) ? _part.chain3D : null;
      if (_chain && _chain.length > 0) {
        fHighlightAtomChain(_chain, true);
        fHighlightAtomChain3D(_chain3D);
        // 3D bonds are not covered by the halo path — color the alkyl C–C
        // and C–H bonds explicitly (both ends in the chain), like the ester triad.
        fColorFragmentBonds3D(_chain3D, true);
      }
      numberingFlag = false;
      break;
    }
    case "esterAlkyl": {
      // Ester alcohol-part click (e.g. μεθυλ): highlight O + alcohol chain.
      // Name box: no numbering (locants only).
      nStyle = "";
      myClass = "";
      myText = fTX('Δηλώνει το αλκυλο-τμήμα του εστέρα (από την αλκοόλη).', 'It indicates the alkyl part of the ester (from the alcohol).');
      const _alcChain = fGetEsterAlcoholChain();
      const _alcChain3D = fGetEsterAlcoholChain3D();
      if (_alcChain && _alcChain.length > 0) {
        fHighlightAtomChain(_alcChain, true);
        fHighlightAtomChain3D(_alcChain3D);
        // Alkyl rule: alcohol-part C–C and C–H bonds go green explicitly.
        fColorFragmentBonds3D(_alcChain3D, true);
      }
      numberingFlag = false;
      break;
    }
    case "esterEster":
      // Ester noun click (εστέρας): highlight triad O-C(=O)-O, no numbering.
      nStyle = "";
      myClass = "";
      myText = fTX('Ανήκει στη χημική τάξη Εστέρες.', 'It belongs to the chemical class Esters.');
      ruleTableHighlight = "r3-esters";
      fHighlightAtomChain(fGetEsterGroupFragment());
      fHighlightAtomChain3D(fGetEsterGroupFragment3D(), true);
      // 3D bonds: color each fragment bond explicitly (both ends in fragment),
      // mirroring the 2D both-ends logic. Ester-branch only — the shared
      // fHighlightAtomChain3D paints the same green, so this stays as the
      // explicit alkyl guarantee; main-chain numbering bonds follow the
      // numbering-bonds setting instead.
      var _estFrag3D = fGetEsterGroupFragment3D() || [];
      // Overview-table builds (v55.x) scrape explanations with paints off.
      if ((typeof window === "undefined" || !window.__mulerExplainQuiet) && typeof bondList3D !== "undefined" && _estFrag3D.length > 0) {
        for (var _eb = 0; _eb < bondList3D.length; _eb++) {
          if (!bondList3D[_eb]) continue;
          if (
            _estFrag3D.indexOf(bondList3D[_eb][0]) >= 0 &&
            _estFrag3D.indexOf(bondList3D[_eb][1]) >= 0
          ) {
            fJSmolScript(
              jmolAppletNomeclature,
              "select atomno=" + bondList3D[_eb][0] + ", atomno=" + bondList3D[_eb][1] + "; color bond [XD8EEDC];",
            );
          }
        }
      }
      numberingFlag = false;
      $("#ruleTheoryContainer").show();
      break;
    case "commonEther":
      // COMMON αιθέρας click: highlight C-O-C, no numbering.
      nStyle = "";
      myClass = "";
      myText = fTX('Ανήκει στη χημική τάξη Αιθέρες (κοινή ονομασία).', 'It belongs to the chemical class Ethers (common name).');
      ruleTableHighlight = "r3-ethers";
      fHighlightFG();
      fHighlightFG3D();
      // 3D bonds are not covered by the halo path — color exactly the two
      // C–O bonds explicitly (both ends in the C-O-C fragment; no C–H by
      // design for the αιθέρας group), like the ester triad.
      fColorFragmentBonds3D(fGetEtherGroupFragment3D());
      numberingFlag = false;
      $("#ruleTheoryContainer").show();
      break;
    default: {
      // Split branch-label pieces (slot 3, comp0bText): per-piece scope — a
      // name piece explains/highlights that substituent, a locants piece
      // numbers. Anything else keeps the generic prompt below.
      const _bpx = /^compBranch(Sub|Loc)(\d+)$/.exec(nameAnalysisMode || "");
      if (_bpx) {
        nStyle = "";
        myClass = "";
        const _pk = parseInt(_bpx[2], 10);
        let _pg = null;
        try { _pg = fGetHydrocarbonBranchPiece(_pk); } catch (ePg) { _pg = null; }
        const _isLoc = _bpx[1] === "Loc";
        if (_pg) {
          myText = fHydrocarbonBranchExplanation(_pg, _isLoc);
          numberingFlag = _isLoc;
          if (!fPaintBranchHighlightAtoms(2, (typeof nameAnalysisMode !== "undefined" ? nameAnalysisMode : ""))) { fHighlightFG(2); fHighlightFG3D(2); }
          if (_isLoc) fShowAnalysisNumbering(0);
          $("#ruleTheoryContainer").show();
        } else if (_isLoc) {
          myText = fIsMultiLocantComponent(nameComponentsList[2])
            ? fTX(` Δηλώνει τις θέσεις της δεύτερης αλφαβητικά δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(2)}.`, ` Indicates the positions of the alphabetically second secondary characteristic group${fGetSecondaryGroupNounSuffix(2)}.`)
            : fTX(` Δηλώνει τη θέση της δεύτερης αλφαβητικά δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(2)}.`, ` Indicates the position of the alphabetically second secondary characteristic group${fGetSecondaryGroupNounSuffix(2)}.`);
          numberingFlag = true;
          fHighlightFG(2);
          fHighlightFG3D(2);
          fShowAnalysisNumbering(0);
        } else {
          myText = fGetNameComponentMultiplier(nameComponentsList[3]) > 1
            ? fTX(` Δηλώνει το πλήθος των δευτερευουσών Χαρακτηριστικών Ομάδων${fGetSecondaryGroupNounSuffix(2)}.`, ` Indicates the number of the secondary characteristic groups${fGetSecondaryGroupNounSuffix(2)}.`)
            : fTX(` Δηλώνει το όνομα  της δεύτερης αλφαβητικά δευτερεύουσας Χαρακτηριστικής Ομάδας${fGetSecondaryGroupNounSuffix(2)}.`, ` Indicates the name of the alphabetically second secondary characteristic group${fGetSecondaryGroupNounSuffix(2)}.`);
          numberingFlag = false;
          fHighlightFG(2);
          fHighlightFG3D(2);
        }
        break;
      }
      myText = fTX(
        "Κάνε κλικ σε ένα συστατικό του ονόματος για να δεις την εξήγηση",
        "Click a name constituent to see its explanation");
      nStyle = "color:#666; font-style:italic; font-weight:normal; border:0;";
      myClass = "";
    }
  }
  fShowRule(nameAnalysisMode);
  // Display-only italic prefixes (IUPAC detached sec-/tert-); narration
  // reads .text() (tags stripped) and the overview scrape reuses this HTML.
  try { if (typeof fMulerItalicSecTert === "function") myText = fMulerItalicSecTert(myText); } catch (eI) {}
  myHTML = `<div class='explainText ${myClass} ' style='${nStyle}'  >${myText}</div>`;
  $("#nameAnalysisExplain").html(myHTML);
  fFitNameComponents();
  try { if (window.nameExpanded) fNameExpandReserve(); } catch (eR) { /* best-effort */ }
  try { if (window.nameExpanded) fNameExplainAnchor(); } catch (eA) { /* best-effort */ }
}

// ── Explain-all overview table (v55.x) ────────────────────────────────────
// One row per visible name box (GR + EN + sys variants uniformly — rows are
// scraped from the rendered boxes, so hidden comps are skipped like in
// narration). Each mode runs through fExplainNameComp with paints suppressed
// (quiet guards in the highlight/numbering/rule helpers); the panel HTML is
// scraped per mode while globals + rule-panel visibility are restored, and
// the synchronous loop never yields, so nothing flashes. Row clicks
// delegate to the box click (same highlight/select/narration), then repaint
// from cache — no rebuild per click.
// QUIZ-FUTURE: blank the row bodies here for self-test mode.
function fExplainAllKey() {
  try {
    var parts = [];
    try { parts.push(typeof selectedMol !== "undefined" ? selectedMol : ""); } catch (eS) {}
    try { parts.push((typeof fMulerLang === "function") ? fMulerLang() : "gr"); } catch (eL) {}
    try { parts.push(Array.isArray(window.nameHiddenComps) ? window.nameHiddenComps.join(",") : ""); } catch (eH) {}
    try { parts.push(typeof substNamingMode !== "undefined" ? substNamingMode : ""); } catch (eV) {}
    try { parts.push(typeof etherNamingMode !== "undefined" ? etherNamingMode : ""); } catch (eE) {}
    try {
      var sig = [], _bx = document.querySelectorAll("#nameAnalysis .nameCompBox");
      for (var i = 0; i < _bx.length; i++) sig.push((_bx[i].getAttribute("id") || "") + "=" + ((_bx[i].textContent || "").replace(/\s+/g, " ").trim()));
      parts.push(sig.join("|"));
    } catch (eB) {}
    return parts.join(";");
  } catch (eO) { return ""; }
}
function fNameExplainTableBuild() {
  var rows = [];
  try {
    if (typeof selectedMol === "undefined" || !selectedMol) return rows;
    var boxes = null;
    try { boxes = document.querySelectorAll("#nameAnalysis .nameCompBox"); } catch (eQ) { boxes = null; }
    if (!boxes || !boxes.length) return rows;
    var prevMode = "none", prevNum = false, prevRule = false, prevRTC = null;
    try { prevMode = (typeof nameAnalysisMode !== "undefined") ? nameAnalysisMode : "none"; } catch (eG) {}
    try { prevNum = !!numberingFlag; } catch (eN) {}
    try { prevRule = !!ruleFlag; } catch (eR) {}
    try { prevRTC = (typeof $ !== "undefined") ? $("#ruleTheoryContainer").is(":visible") : null; } catch (eV) {}
    // try/finally: quiet flag + author view state must restore even if the
    // synchronous scrape loop throws (a stuck flag would suppress all paints).
    try { if (typeof window !== "undefined") window.__mulerExplainQuiet = true; } catch (eF) {}
    try {
      try {
        for (var bi = 0; bi < boxes.length; bi++) {
          var box = boxes[bi], bid = "";
          try { bid = box.getAttribute("id") || ""; } catch (eI) { bid = ""; }
          if (!bid) continue;
          // Eye-hidden components keep their row instead of vanishing: the
          // chip mirrors the hidden box (dash), the explanation cell stays.
          var _rowHidden = false;
          try { _rowHidden = !!(box.classList && box.classList.contains("comp-hidden")); } catch (eH) { _rowHidden = false; }
          var mode = null;
          try { mode = (typeof fNameAnalysisModeForBoxId === "function") ? fNameAnalysisModeForBoxId(bid) : null; } catch (eM) { mode = null; }
          if (!mode || mode === "none") continue;
          var chip = _rowHidden ? "–" : "";
          try { if (!_rowHidden) chip = (box.textContent || "").replace(/\s+/g, " ").trim(); } catch (eC) {}
          if (!chip) continue;
          try { nameAnalysisMode = mode; } catch (eS) {}
          try { if (typeof fExplainNameComp === "function") fExplainNameComp(); } catch (eX) { continue; }
          var html = "";
          try { html = document.getElementById("nameAnalysisExplain").innerHTML || ""; } catch (eH2) {}
          // Defensive: never scrape our own overview markup into a cell (a stale
          // nested table must not survive a rebuild).
          try { if (html.indexOf("explainTable") >= 0) html = ""; } catch (eH3) { html = ""; }
          if (!html) continue;
          rows.push({ id: bid, chip: chip, html: html, hidden: _rowHidden });
        }
      } catch (eL) {}
    } finally {
      try { if (typeof window !== "undefined") window.__mulerExplainQuiet = false; } catch (eF2) {}
      try { nameAnalysisMode = prevMode; } catch (eS2) {}
      try { numberingFlag = !!prevNum; } catch (eN2) {}
      try { ruleFlag = !!prevRule; } catch (eR2) {}
      try {
        if (typeof $ !== "undefined") {
          if (prevRTC) $("#ruleTheoryContainer").show(); else $("#ruleTheoryContainer").hide();
        }
      } catch (eV2) {}
    }
  } catch (eO) {}
  return rows;
}
function fNameExplainTableRender() {
  // Cheap repaint from cache (row clicks); rebuilds only on cache miss.
  try {
    var key = "", cache = null;
    try { key = (typeof fExplainAllKey === "function") ? fExplainAllKey() : ""; } catch (eK) {}
    try { cache = window._explainAllCache || null; } catch (eC) {}
    var rows = (cache && cache.key === key && Array.isArray(cache.rows)) ? cache.rows : null;
    if (!rows) {
      rows = (typeof fNameExplainTableBuild === "function") ? fNameExplainTableBuild() : [];
      try { window._explainAllCache = { key: key, rows: rows }; } catch (eC2) {}
    }
    var na = null;
    try { na = document.getElementById("nameAnalysisExplain"); } catch (eN) {}
    if (!na) return;
    if (!rows.length) {
      try { if (typeof fExplainNameComp === "function") fExplainNameComp(); } catch (eF) {}
      return;
    }
    var sel = null;
    try { var _s = document.querySelector("#nameAnalysis .nameCompBox.selected"); if (_s) sel = _s.getAttribute("id"); } catch (eS) {}
    var h = "<div class='explainTable'>";
    for (var i = 0; i < rows.length; i++) {
      var esc = String(rows[i].chip).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      // Display-only italic prefixes (IUPAC detached sec-/tert-), mirroring
      // the box: escape first, then wrap (chip source is textContent, so the
      // only tags reaching the HTML are our own <i>).
      try { if (typeof fMulerItalicSecTert === "function") esc = fMulerItalicSecTert(esc); } catch (eI) {}
      h += "<div class='explainRow" + (rows[i].hidden ? " row-hidden" : "") + (rows[i].id === sel ? " selected" : "") + "' data-box='" + rows[i].id + "'><span class='explainChip'>" + esc + "</span><div class='explainCell'>" + rows[i].html + "</div></div>";
    }
    na.innerHTML = h + "</div>";
  } catch (eO) {}
}
function fNameExplainTableShow() {
  // Full build + render (toggle-on, molecule/variant/eye rebuilds).
  try {
    var key = "", rows = [];
    try { key = (typeof fExplainAllKey === "function") ? fExplainAllKey() : ""; } catch (eK) {}
    try { rows = (typeof fNameExplainTableBuild === "function") ? fNameExplainTableBuild() : []; } catch (eB) {}
    try { window._explainAllCache = { key: key, rows: rows }; } catch (eC) {}
    try { if (typeof fNameExplainTableRender === "function") fNameExplainTableRender(); } catch (eR) {}
  } catch (eO) {}
}

// ── fShowRule ─────────────────────────────────────────────────────────────

function fShowRule(theRule) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  let ruleText, ruleTable, ruleTitle, myStyle, myClass, myHTML;
  let alkylRows = null;
  if (theRule === fAlcoholOHNameComponent()) {
    theRule = 'compSuffix';
    ruleTableHighlight = 'r3-alcohols';
  }
  switch (theRule) {
    case "compNumber1":
    case "compNumber2":
    case "compAcidNumber3": {
      const group = fGetHydrocarbonBranchGroup(theRule === "compAcidNumber3" ? 3 : theRule === "compNumber2" ? 2 : 1);
      if (group) {
        ruleText = namingRules.alkylRule;
        ruleTable = namingRules.alkylTable;
        ruleTitle = "Ονόματα αλκυλίων και προθέματα";
        alkylRows = group.names.map(function (name) { return "alkyl-" + name; });
      } else if (Object.keys(functionalGroupObj).length > 1) {
        ruleText = namingRules.rule4;
        ruleTable = namingRules.table4;
        ruleTitle = "Σειρά ισχύος Χαρακτηριστικών Ομάδων";
      } else {
        ruleText = namingRules.rule2;
        ruleTable = namingRules.table2;
        ruleTitle = "Κανόνας συνθετικού τύπου δεσμών";
      }
      break;
    }
    case "compSecondSub1":
    case "compSecondSub2":
    case "compAcidSub3": {
      const group = fGetHydrocarbonBranchGroup(theRule === "compAcidSub3" ? 3 : theRule === "compSecondSub2" ? 2 : 1);
      if (group) {
        ruleText = namingRules.alkylRule;
        ruleTable = namingRules.alkylTable;
        ruleTitle = "Ονόματα αλκυλίων και προθέματα";
        alkylRows = group.names.map(function (name) { return "alkyl-" + name; });
      } else {
        ruleText = namingRules.rule4;
        ruleTable = namingRules.table4;
        ruleTitle = "Σειρά ισχύος Χαρακτηριστικών Ομάδων";
      }
      break;
    }
    case "compCarbonsCount":
      ruleText = namingRules.rule1;
      ruleTable = namingRules.table1;
      ruleTitle = "Κανόνας συνθετικού ανθρακικής αλυσίδας";
      break;
    case "compBondPos":
      if (fBranchedSaturatedKetonePosition()) {
        ruleText = namingRules.rule3; ruleTable = namingRules.table3;
        ruleTitle = "Κανόνας συνθετικού χημικής τάξης";
        break;
      }
    case "compBondType":
    case "compBondType2":
    case "compEndNumber":
      ruleText = namingRules.rule2;
      ruleTable = namingRules.table2;
      ruleTitle = "Κανόνας συνθετικού τύπου δεσμών";
      break;
    case "compSuffix":
    case "compSuffixLocants":
      ruleText = namingRules.rule3;
      ruleTable = namingRules.table3;
      ruleTitle = "Κανόνας συνθετικού χημικής τάξης";
      break;
    case "commonEther":
      ruleText = namingRules.rule3;
      ruleTable = namingRules.table3;
      ruleTitle = "Κανόνας συνθετικού χημικής τάξης";
      break;
    case "commonAlkyl1":
    case "commonAlkyl2":
    case "esterAlkyl":
      ruleText = "";
      ruleTable = "";
      ruleTitle = "";
      break;
    case "esterEster":
      ruleText = namingRules.rule3;
      ruleTable = namingRules.table3;
      ruleTitle = "Κανόνας συνθετικού χημικής τάξης";
      break;
    case "none":
      ruleText = "";
      ruleTable = "";
      ruleTitle = "";
      break;
    default: {
      // Split branch-label pieces: same alkyl rule/table as the slot-level
      // branch modes, with rows scoped to the clicked substituent.
      const _rbpx = /^compBranch(Sub|Loc)(\d+)$/.exec(theRule || "");
      if (_rbpx) {
        const _rpg = fGetHydrocarbonBranchPiece(parseInt(_rbpx[2], 10));
        if (_rpg) {
          ruleText = namingRules.alkylRule;
          ruleTable = namingRules.alkylTable;
          ruleTitle = "Ονόματα αλκυλίων και προθέματα";
          alkylRows = _rpg.names.map(function (name) { return "alkyl-" + name; });
        } else {
          ruleText = namingRules.rule4;
          ruleTable = namingRules.table4;
          ruleTitle = "Σειρά ισχύος Χαρακτηριστικών Ομάδων";
        }
        break;
      }
      ruleText = "";
      ruleTable = "";
      ruleTitle = "";
    }
  }

  const showAlkoxy = typeof fScenarioShowAlkoxyRule === "function" && fScenarioShowAlkoxyRule();
  const etherGroups = showAlkoxy && Array.isArray(atomConnectivityList) &&
    Array.isArray(allAtomsTypeList) && Array.isArray(bondList) &&
    fIsAcyclicMonoetherGraph(atomConnectivityList, allAtomsTypeList, bondList)
    ? fEtherPrefixGroups() : [];
  const alkoxy = etherGroups.find(g => g.kind === "alkoxy");
  const slot = ["compNumber1", "compSecondSub1"].includes(theRule) ? 1 :
    ["compNumber2", "compSecondSub2"].includes(theRule) || /^compBranch(Sub|Loc)\d+$/.test(theRule || "") ? 2 : 0;
  const selectedGroups = slot === 1 ? etherGroups.slice(0, 1) : slot === 2 ? etherGroups.slice(1) : [];
  const alkoxyAsMain = !!alkoxy && selectedGroups.length === 1 && selectedGroups[0].kind === "alkoxy";
  if (alkoxyAsMain) {
    ruleText = namingRules.alkoxyRule;
    ruleTable = namingRules.alkoxyTable;
    ruleTitle = "Ονόματα αλκοξυομάδων και προθέματα";
  }
  const pilotRule = typeof fScenarioShowComponentRule === "function" &&
    fScenarioShowComponentRule(theRule);
  // EN rule panel: static GR text/table → translated HTML (chemistry tokens stay).
  if (typeof fIsENMode === "function" && fIsENMode() && typeof fTranslateRuleHTML === "function") {
    ruleTitle = fTranslateRuleHTML(ruleTitle);
    ruleText = fTranslateRuleHTML(ruleText);
    ruleTable = fTranslateRuleHTML(ruleTable);
  }
  if (pilotRule) $("#ruleTheoryContainer").show();
  if (ruleFlag && !pilotRule) {
    myStyle = "display: block;";
    myClass = "open";
  } else {
    myStyle = "display:none;";
    myClass = "closed";
  }

  myHTML = `
  <div class='ruleTheory' >
  <div class='ruleTile ${myClass}' id='ruleTitle'> ${ruleTitle} </div>
  <div id='ruleContainer' style='${myStyle}'><div class='ruleText' >${ruleText}</div><div class='ruleTable' >${ruleTable}</div></div>
  </div>`;
  // Display-only italic prefixes (IUPAC detached sec-/tert-, plus (n-) in
  // tables): applied post-translation so RULE_GR2EN keys still match.
  try { if (typeof fMulerItalicSecTert === "function") myHTML = fMulerItalicSecTert(myHTML, true); } catch (eI) {}

  if (alkoxy && !alkoxyAsMain) {
    // Keep the current chain/alkyl rule; add a separate, initially closed table.
    if (!ruleTitle) myHTML = "";
    myHTML += `<div class='ruleTheory'><button type='button' class='ruleTile closed' id='alkoxyRuleTitle' style='width:100%;border:0;text-align:left;' aria-expanded='false' aria-controls='alkoxyRuleContainer'>Ονόματα αλκοξυομάδων και προθέματα</button><div id='alkoxyRuleContainer' style='display:none;'><div class='ruleText'>${namingRules.alkoxyRule}</div><div class='ruleTable'>${namingRules.alkoxyTable}</div></div></div>`;
  }
  $("#ruleTheoryContainer").html(myHTML);
  if (alkoxy) {
    $("#ruleTheoryContainer").show();
    $("#ruleTheoryContainer [data-row='alkoxy-" + alkoxy.name + "']").addClass("selected");
  }

  if (alkylRows) {
    alkylRows.forEach(function (key) {
      $("#ruleContainer [data-row='" + key + "']").addClass("selected");
    });
  }

  // Key-based highlight: rows carry data-row="rN-key" (see fInitTheory tables).
  // Row order no longer matters — moves/additions need no code changes.
  if (typeof ruleTableHighlight === "string" && ruleTableHighlight) {
    $(`#ruleContainer [data-row="${ruleTableHighlight}"]`).addClass("selected");
  }
  if (Array.isArray(ruleTableHighlight)) {
    $("#ruleContainer .ruleText").addClass("hideTopRow");
    if (ruleTableHighlight[0]) {
      $(`#ruleContainer [data-row="${ruleTableHighlight[0]}"]`).addClass(
        "selected selectedB",
      );
    }
    if (ruleTableHighlight[1]) {
      $(`#ruleContainer [data-row="${ruleTableHighlight[1]}"]`).addClass(
        "selected selectedA",
      );
    }
  }
}

// ── fAdjustRuleContainerHeight ────────────────────────────────────────────

function fAdjustRuleContainerHeight() {
  let ruleElement, myTop, myBottom, ruleContainerHeight;
  ruleElement = document.querySelector(".ruleTable");
  if (!ruleFlag) {
    ruleElement.setAttribute("style", " max-height: none ");
  } else {
    myTop = document
      .querySelector("#ruleContainer .ruleTable")
      .getBoundingClientRect().top;
    myBottom = document
      .querySelector("#molRepColumn")
      .getBoundingClientRect().bottom;
    ruleContainerHeight = myBottom - myTop;
    ruleElement.setAttribute(
      "style",
      ` max-height:${ruleContainerHeight}px; overflow:auto; `,
    );
  }
}

// Stored main-chain keys use _Condensed/_Expanded/_Skeletal; modeSuffix
// carries the MOL _2D_* form, so chain lookups use this mapping.
function fMainChainKeySuffix() {
  return mode2D === "expanded"
    ? "_Expanded"
    : mode2D === "skeletal" || mode2D === "condensedZigZag"
      ? "_Skeletal"
      : "_Condensed";
}

// ── fHighLightMainChain ───────────────────────────────────────────────────

function fHighLightMainChain() {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  if (nameAnalysisMode == "none") {
    return;
  }

  highAtoms = mainChainAtomsList;

  let highAtomsArg = "";
  for (let i = 0; i < highAtoms.length; i++) {
    highAtomsArg += highAtoms[i] + ",9";
    if (i < highAtoms.length - 1) {
      highAtomsArg += ",";
    }
  }
  jsmeNomeclatureApplet.setAtomBackgroundColors(0, highAtomsArg);

  fUpdateSVG();
}

// ── fHighLightMainChainBonds ─────────────────────────────────────────────
// 2D companion to fHighLightMainChain: paints every bond with both ends in
// the same resolved chain (any order, green 9, 3D parity). Separate function
// so the numbering-bonds setting gates bonds independently of the atoms
// setting; the caller decides. Sole numbering-path use (via compCarbonsCount).
function fHighLightMainChainBonds() {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  if (nameAnalysisMode == "none") {
    return;
  }

  const _chain = mainChainAtomsList;
  if (!Array.isArray(_chain) || _chain.length === 0 || typeof bondList === "undefined") {
    return;
  }
  const _chainSet = new Set(_chain);
  const _bondArgs = [];
  for (let b = 0; b < bondList.length; b++) {
    if (!bondList[b]) continue;
    if (_chainSet.has(bondList[b][0]) && _chainSet.has(bondList[b][1])) {
      _bondArgs.push((b + 1) + ",9");
    }
  }
  if (_bondArgs.length > 0) jsmeNomeclatureApplet.setBondBackgroundColors(0, _bondArgs.join(","));

  fUpdateSVG();
}

// ── Main-chain stepper (v47, in the name-settings panel) ───────────────────────
// Compact block: fStepMainChain(dir) + fRenderChainStepper() (+ helpers).
// Walks the FG-aware multiple-bond-first pool (core mainChainPool, rank-parallel
// mainChainPool3D). Swaps the live chain globals and recomputes name +
// substituents per candidate WITHOUT disturbing teaching state
// (nameAnalysisMode, boxes, rule theory untouched — stepping only refreshes
// the selected component's highlight via the click sequence). Pool[0] is the
// adopted main chain; loading a molecule restores it. Algorithmic mode only;
// scenario steps capture the pool index (chainIdx, v47 additive) and
// re-assert it after the step load.

function fMainChainPoolLive() {
  return (typeof mainChainPool !== "undefined" && Array.isArray(mainChainPool)) ? mainChainPool : [];
}

function fChainStepper3DFresh() {
  try {
    return (typeof mainChainPool3D !== "undefined" && Array.isArray(mainChainPool3D) &&
      typeof mainChainPool3DKey !== "undefined" && typeof selectedMol !== "undefined" &&
      mainChainPool3DKey !== null && mainChainPool3DKey === selectedMol);
  } catch (e) { return false; }
}

function fApplyChainStep() {
  var pool = fMainChainPoolLive();
  if (pool.length === 0) return;
  var idx = (typeof mainChainPoolIdx === "number") ? mainChainPoolIdx : 0;
  if (idx < 0) idx = 0;
  if (idx > pool.length - 1) idx = pool.length - 1;
  var branchQuiz = typeof window !== "undefined" && window.MulerQuizTarget &&
    (fMulerSelectPurpose() === "branch" ||
      (window.__mulerQuizReturnTo && fMulerBranchAtomsForMode(window.__mulerQuizReturnTo).length > 0));
  if (branchQuiz) fMulerSelectClear();
  mainChainPoolIdx = idx;
  mainChainAtomsList = pool[idx].chain.slice();
  // 3D by atom correspondence, not ordinal: the 2D (JSME) and 3D (SDF) pools
  // rank the same molecule from different atom orderings and can diverge in
  // length or order — and signatures cannot tell symmetry-equivalent chains
  // apart (neopentane: 6 identical C–C–C paths). The per-molecule heavy-atom
  // map translates the adopted 2D chain exactly, so distinct 2D chains always
  // land on distinct 3D chains. Fallbacks: signature match (chemistry, for
  // asymmetric cases), then legacy ordinal only when signatures are
  // unavailable — never a wrong chain as counterpart. Freshness gate as
  // before (3D parse is async; a stale pool must not leak across molecules).
  try {
    if (fChainStepper3DFresh()) {
      var _t3 = null;
      try { if (typeof fTranslateChain2D3D === "function") _t3 = fTranslateChain2D3D(mainChainAtomsList); } catch (eT) { _t3 = null; }
      if (_t3) { mainChainAtoms3D = _t3.slice(); }
      else {
        var _sig = null, _sigOk = false;
        try {
          if (typeof fNumberedChainSignature === "function") {
            _sig = fNumberedChainSignature(mainChainAtomsList, allAtomsTypeList, bondList);
            _sigOk = (_sig !== null);
          }
        } catch (eSg) { _sigOk = false; }
        if (_sigOk) {
          for (var _q = 0; _q < mainChainPool3D.length; _q++) {
            var _qs = null;
            try { _qs = fNumberedChainSignature(mainChainPool3D[_q].chain, allAtomsTypeList3D, bondList3D); } catch (eQ) { _qs = null; }
            if (_qs !== null && _qs === _sig) {
              mainChainAtoms3D = mainChainPool3D[_q].chain.slice();
              break;
            }
          }
        } else if (idx < mainChainPool3D.length) {
          mainChainAtoms3D = mainChainPool3D[idx].chain.slice();
        }
      }
    }
  } catch (e3) { /* 3D unavailable */ }
  // Naming runs ON the swapped chain: the `true` flag skips fGuessName's
  // internal winner recompute (which would rebuild the pool, reset this step
  // and rename the winner — the trap that froze the stepper). Validation is
  // skipped with it, as intended while stepping.
  try { if (typeof fGuessName === "function") fGuessName(true); } catch (eN) { /* naming unavailable */ }
  // Stepper refresh (v54.30): Greek slots just changed chain, so refresh both
  // EN variants too — otherwise the Traditional/Systematic toggle visibility
  // (and verdict-source EN) keeps reflecting the select-time chain while the
  // boxes already show the stepped one. Pure string ops, no oracle traffic.
  try { if (typeof fPopulateEngineENFromGreek === "function") fPopulateEngineENFromGreek(selectedMol); } catch (eEnSt) { /* engine best-effort */ }
  try { if (typeof fPopulateEngineENFromGreek === "function") fPopulateEngineENFromGreek(selectedMol, "sys"); } catch (eEnSySt) { /* systematic best-effort */ }
  // Refresh ONLY the selected component's highlight (or clear to deselect
  // visuals when nothing is selected): same clear + rebuild + explain sequence
  // as a name-box click, minus the selection toggle and narration. The
  // component's own path repaints explanation, highlight and numbering
  // against the new chain; with mode "none" nothing paints.
  try {
    if (typeof fClearHighlights === "function") fClearHighlights();
    if (typeof fUpdateSVG === "function") fUpdateSVG();
    if (typeof fExplainNameComp === "function") fExplainNameComp();
  } catch (eHl) { /* viewer unavailable */ }
  if (branchQuiz) {
    var quizMode = window.MulerQuizTarget;
    var quizBox = fMulerQuizBoxIdForMode(quizMode);
    if (quizMode && quizBox && document.getElementById(quizBox) &&
        fNameAnalysisModeForBoxId(quizBox) === quizMode &&
        fMulerQuizResolveTarget(quizMode).length &&
        (window.__mulerQuizReturnTo
          ? fMulerBranchAtomsForMode(window.__mulerQuizReturnTo).length
          : fMulerQuizPurposeFor(quizMode) === "branch")) {
      fMulerQuizPrompt();
    } else {
      fMulerQuizDisarm();
    }
    fMulerSelectRepaint();
  }
  fRenderChainStepper();
  try {
    if (typeof window.fScenarioOnPresentBrowse === "function") window.fScenarioOnPresentBrowse();
  } catch (eScenario) { /* scenario absent */ }
}

function fStepMainChain(dir) {
  var pool = fMainChainPoolLive();
  if (pool.length === 0) return;
  if (typeof mainChainMode !== "undefined" && mainChainMode !== "algorithmic") return;
  if (typeof selectedMol === "undefined" || !selectedMol) return;
  var idx = (typeof mainChainPoolIdx === "number") ? mainChainPoolIdx : 0;
  var n = idx + dir;
  if (n < 0) n = 0;
  if (n > pool.length - 1) n = pool.length - 1;
  if (n === idx) { fRenderChainStepper(); return; }
  mainChainPoolIdx = n;
  fApplyChainStep();
}

function fRenderChainStepper() {
  var box = null, label = null, prev = null, next = null;
  try {
    box = document.getElementById("chainStepperBox");
    if (!box) return; // stepper markup absent — nothing to sync
    label = document.getElementById("chainStepLabel");
    prev = document.getElementById("chainPrevBtn");
    next = document.getElementById("chainNextBtn");
  } catch (eD) { return; }
  var pool = fMainChainPoolLive();
  var idx = (typeof mainChainPoolIdx === "number") ? mainChainPoolIdx : 0;
  var algo = (typeof mainChainMode === "undefined" || mainChainMode === "algorithmic");
  var okMol = false;
  try {
    okMol = (typeof selectedMol !== "undefined" && !!selectedMol &&
      typeof nameExamples !== "undefined" && !!nameExamples[selectedMol]);
  } catch (eM) { /* no molecule */ }
  // Visible only with 2+ chains; otherwise the whole box hides.
  // The stepper owns its row, so the row follows the box (no empty row
  // reserves space); radio/button rows are unaffected.
  var active = okMol && algo && pool.length > 1;
  try {
    box.style.display = active ? "" : "none";
    var _row = box.parentNode;
    if (_row && _row.className && ((" " + _row.className + " ").indexOf(" nameSettingsRow ") !== -1)) _row.style.display = active ? "" : "none";
  } catch (eS) { /* styling unavailable */ }
  if (!active || !label) return;
  if (idx < 0) idx = 0;
  if (idx > pool.length - 1) idx = pool.length - 1;
  label.textContent = (idx + 1) + "/" + pool.length;
  if (prev) prev.disabled = idx <= 0;
  if (next) next.disabled = idx >= pool.length - 1;
}

// Stepper group markup for the name-settings panel (rebuilt with it on every
// fShowNameAnalysis, so the counter/disabled states are always current).
// One container div (#chainStepperBox) holds everything for easy styling.
// The group renders only when there is something to step through (2+ chains,
// algorithmic mode, molecule loaded) — otherwise nothing lands in the DOM.
function fChainStepperHTML() {
  var pool = fMainChainPoolLive();
  var idx = (typeof mainChainPoolIdx === "number") ? mainChainPoolIdx : 0;
  var algo = (typeof mainChainMode === "undefined" || mainChainMode === "algorithmic");
  var okMol = false;
  try {
    okMol = (typeof selectedMol !== "undefined" && !!selectedMol &&
      typeof nameExamples !== "undefined" && !!nameExamples[selectedMol]);
  } catch (eM) { /* no molecule */ }
  if (!okMol || !algo || pool.length < 2) return "";
  if (idx < 0) idx = 0;
  if (idx > pool.length - 1) idx = pool.length - 1;
  var txt = (idx + 1) + "/" + pool.length;
  var disP = idx <= 0 ? " disabled" : "";
  var disN = idx >= pool.length - 1 ? " disabled" : "";
  var chevL = (window.MuLERIcons && window.MuLERIcons.chevronLeft) || "‹";
  var chevR = (window.MuLERIcons && window.MuLERIcons.chevronRight) || "›";
  const _chainWords = (() => {
    try {
      if (typeof fMulerT === "function") return { label: fMulerT("mainChainShort"), prev: fMulerT("prevChain"), next: fMulerT("nextChain") };
    } catch (e) { /* fall through */ }
    return { label: "Κύρια αλυσίδα:", prev: "Προηγούμενη αλυσίδα", next: "Επόμενη αλυσίδα" };
  })();
  return "<div id='chainStepperBox'><span class='settingLabel'>" + _chainWords.label + "</span>" +
    "<button id='chainPrevBtn' class='stepBtn' onclick='fStepMainChain(-1)' data-tooltip='" + _chainWords.prev + "'" + disP + ">" + chevL + "</button>" +
    "<span id='chainStepLabel'>" + txt + "</span>" +
    "<button id='chainNextBtn' class='stepBtn' onclick='fStepMainChain(1)' data-tooltip='" + _chainWords.next + "'" + disN + ">" + chevR + "</button></div>";
}

// ── fGetHydrocarbonBranchHighlight ─────────────────────────────────────────

// Match the same Greek-alphabetical prefix groups used by fGuessName.
// Slot 2 represents all remaining groups, matching the fused comp2/comp3 boxes.
// Main-only projection for the approved three-alkyl acid. Keep the core's
// fixed component array and the saved React/scenario contracts unchanged.
function fSeparateAcidPrefixBoxes() {
  return ['ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid',
    'ethyl_3_isopropyl_2_dimethyl_4_5_hexadien_2_4_dioic_acid',
    'ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid'].includes(selectedMol) &&
    typeof document !== 'undefined' && !!document.documentElement &&
    document.documentElement.getAttribute('data-namelecule-acid-prefix-boxes') === 'true';
}
function fAcidPrefixBoxGroups() {
  if (!fSeparateAcidPrefixBoxes()) return [];
  const branches = fGetHydrocarbonSubstituentInfo();
  return [...new Set(branches.map(b => b.name))].sort().map(name => {
    const members = branches.filter(b => b.name === name);
    return { label: nameMultiPrefix[members.length-1] + name,
      locants: members.map(b => b.locant).sort((a,b) => a-b).join(',') };
  });
}

function fGetHydrocarbonBranchGroup(slot) {
  if (functionalGroupsList.length === 1 && functionalGroupsList[0] === 'ether') {
    const groups = fEtherPrefixGroups();
    const selected = slot === 2 ? groups.slice(1) : groups.slice(0,1);
    const members = selected.filter(g => g.kind === 'alkyl').flatMap(g => g.members);
    return members.length ? {names:selected.filter(g=>g.kind==='alkyl').map(g=>g.name),members:members} : null;
  }
  if (!functionalGroupObj || !fSupportsAlkylBranchPrefixes()) return null;
  const branches = fGetHydrocarbonSubstituentInfo();
  const names = [...new Set(branches.map(function (b) { return b.name; }))]
    .sort(function (a, b) { return a < b ? -1 : a > b ? 1 : 0; });
  const selected = fSeparateAcidPrefixBoxes() ? names.slice(slot-1, slot) :
    slot === 2 ? names.slice(1) : names.slice(0, 1);
  const members = branches.filter(function (b) { return selected.includes(b.name); });
  return members.length ? { names: selected, members: members } : null;
}

function fHydrocarbonBranchSlot() {
  if (["compAcidNumber3", "compAcidSub3"].includes(nameAnalysisMode)) return 3;
  if (/^compBranch(Sub|Loc)\d+$/.test(nameAnalysisMode || "")) return 2;
  return nameAnalysisMode === "compNumber2" || nameAnalysisMode === "compSecondSub2" ? 2 : 1;
}

function fHydrocarbonBranchExplanation(group, positions) {
  const locants = [...new Set(group.members.map(function (b) { return b.locant; }))]
    .sort(function (a, b) { return a - b; }).join(", ");
  const names = group.names.map(function (name) { return fBranchNoun(name); }).join(", ");
  if (group.names.length > 1) {
    const pairs = group.names.map(name => {
      const nums = group.members.filter(b => b.name === name).map(b => b.locant)
        .sort((a, b) => a - b).join(", ");
      return `${fBranchNoun(name)}${fTX(" στις θέσεις ", " at positions ")}${nums}`;
    }).join(" · ");
    return positions
      ? fTX(`Δηλώνει τη θέση ή τις θέσεις της πρώτης από τις υπόλοιπες ομάδες. Οι επόμενες θέσεις περιλαμβάνονται στο διπλανό συνθετικό (${pairs}).`, `Indicates the position(s) of the first of the remaining groups. The following positions are included in the adjacent component (${pairs}).`)
      : fTX(`Ομαδοποιημένο συνθετικό με τα ονόματα των υπόλοιπων διακλαδώσεων και τις ενδιάμεσες θέσεις τους (${pairs}).`, `Grouped component with the names of the remaining branches and their intermediate positions (${pairs}).`);
  }
  if (positions) {
    return group.members.length === 1
      ? fTX(`Δηλώνει τη θέση ${locants} της ανθρακικής διακλάδωσης (${names}).`, `Indicates position ${locants} of the carbon branch (${names}).`)
      : fTX(`Δηλώνει τις θέσεις ${locants} των ανθρακικών διακλαδώσεων (${names}).`, `Indicates positions ${locants} of the carbon branches (${names}).`);
  }
  return group.members.length === 1
    ? fTX(`Δηλώνει το όνομα της ανθρακικής διακλάδωσης (${names}).`, `Indicates the name of the carbon branch (${names}).`)
    : fTX(`Δηλώνει το όνομα και το πλήθος (${group.members.length}) των ανθρακικών διακλαδώσεων (${names}).`, `Indicates the name and the number (${group.members.length}) of the carbon branches (${names}).`);
}

function fGetHydrocarbonBranchHighlight(slot, modeOverride) {
  if (!Array.isArray(mainChainAtomsList) || mainChainAtomsList.length === 0) {
    return { atoms: [], bonds: [] };
  }

  const mainSet = new Set(mainChainAtomsList.map((n) => n - 1));
  // Optional explicit mode (quiz resolvers): the global nameAnalysisMode is
  // not yet (re)armed when an arm gate resolves the target, so the piece
  // scope and compNumber2 narrowing below must see the candidate mode.
  var _modeHl = (typeof modeOverride === "string" && modeOverride) ? modeOverride : ((typeof nameAnalysisMode !== "undefined") ? nameAnalysisMode : "");
  const _pieceM = /^compBranch(Sub|Loc)(\d+)$/.exec(_modeHl || "");
  var group = slot ? fGetHydrocarbonBranchGroup(slot) : null;
  // Split branch-label pieces highlight only their own substituent; an
  // unmatched piece keeps the whole slot group (never an empty highlight).
  if (_pieceM && slot === 2) {
    let _pp = null;
    try { _pp = fGetHydrocarbonBranchPiece(parseInt(_pieceM[2], 10)); } catch (ePp) { _pp = null; }
    if (_pp && _pp.members.length) group = _pp;
  }
  // The "-2-" style locants box (compNumber2) highlights only the first of
  // the remaining groups — its explanation already scopes positions that
  // way ("της πρώτης από τις υπόλοιπες ομάδες"). Single-name slots are
  // unaffected; an unmatched shape keeps the whole slot group.
  if (!_pieceM && _modeHl === "compNumber2" && slot === 2 &&
      group && Array.isArray(group.names) && group.names.length > 1) {
    const _fm = group.members.filter(function (b) { return b && b.name === group.names[0]; });
    if (_fm.length) group = { names: [group.names[0]], members: _fm };
  }
  if (slot && !group) return { atoms: [], bonds: [] };
  const atoms = new Set();
  const bonds = new Set();

  for (let i = 0; i < atomsCount; i++) {
    if (allAtomsTypeList[i] !== "C" || mainSet.has(i)) continue;

    const neighbors = Array.isArray(atomConnectivityList[i])
      ? atomConnectivityList[i]
      : [];
    const parent = neighbors.find((nb) => mainSet.has(nb));
    if (parent === undefined) continue;

    const sideSet = new Set([i]);
    const stack = [i];
    while (stack.length > 0) {
      const node = stack.pop();
      const ns = Array.isArray(atomConnectivityList[node])
        ? atomConnectivityList[node]
        : [];
      for (let k = 0; k < ns.length; k++) {
        const nb = ns[k];
        if (nb === parent || allAtomsTypeList[nb] !== "C" || sideSet.has(nb))
          continue;
        sideSet.add(nb);
        stack.push(nb);
      }
    }

    // Match the attachment-rooted carbon graph at its live parent locant.
    // Equal-sized straight/branched groups must never cross-highlight.
    const locant = mainChainAtomsList.indexOf(parent + 1) + 1;
    const branch = group ? fDescribeCarbonBranches(mainChainAtomsList.map(n => n - 1),
      atomConnectivityList, allAtomsTypeList).find(d => d.attach === i) : null;
    if (group && !group.members.some(function (b) {
      return branch && b.locant === locant && b.signature === branch.signature;
    })) continue;

    for (const node of sideSet) {
      atoms.add(node + 1);
      const ns = Array.isArray(atomConnectivityList[node])
        ? atomConnectivityList[node]
        : [];
      for (let k = 0; k < ns.length; k++) {
        const nb = ns[k];
        if (!sideSet.has(nb)) continue;
        const a = node + 1;
        const b = nb + 1;
        for (let idx = 0; idx < bondList.length; idx++) {
          const bond = bondList[idx];
          if (!bond) continue;
          const sameBond =
            (bond[0] === a && bond[1] === b) ||
            (bond[0] === b && bond[1] === a);
          if (sameBond) {
            bonds.add(idx + 1);
            break;
          }
        }
      }
      // Expanded mode: H atoms are explicit — highlight H attached to branch
      // carbons together with their C–H bonds. atomConnectivityList skips
      // H bonds (see fAnalyseStructure), so scan bondList for C–H endpoints
      // instead. In condensed modes no H endpoints exist, so this is a
      // no-op there.
      for (let b = 0; b < bondList.length; b++) {
        if (!bondList[b]) continue;
        const ba1 = bondList[b][0];
        const ba2 = bondList[b][1];
        let hIdx = -1;
        if (ba1 === node + 1 && allAtomsTypeList[ba2 - 1] === "H") {
          hIdx = ba2;
        } else if (ba2 === node + 1 && allAtomsTypeList[ba1 - 1] === "H") {
          hIdx = ba1;
        }
        if (hIdx !== -1) {
          atoms.add(hIdx);
          bonds.add(b + 1);
        }
      }
    }
  }

  return { atoms: [...atoms], bonds: [...bonds] };
}

// ── fGetHydrocarbonBranchHighlight3D ──────────────────────────────────────

function fGetHydrocarbonBranchHighlight3D(slot) {
  if (!Array.isArray(mainChainAtoms3D) || mainChainAtoms3D.length === 0) {
    return { atoms: [], bonds: [] };
  }

  const mainSet = new Set(mainChainAtoms3D.map((n) => n - 1));
  const _pieceM3 = /^compBranch(Sub|Loc)(\d+)$/.exec(typeof nameAnalysisMode !== "undefined" ? nameAnalysisMode : "");
  var group = slot ? fGetHydrocarbonBranchGroup(slot) : null;
  // Same per-piece scope as the 2D twin (matched by locant+signature below).
  if (_pieceM3 && slot === 2) {
    let _pp3 = null;
    try { _pp3 = fGetHydrocarbonBranchPiece(parseInt(_pieceM3[2], 10)); } catch (ePp3) { _pp3 = null; }
    if (_pp3 && _pp3.members.length) group = _pp3;
  }
  // Same first-group scope for compNumber2 as the 2D twin.
  if (!_pieceM3 && nameAnalysisMode === "compNumber2" && slot === 2 &&
      group && Array.isArray(group.names) && group.names.length > 1) {
    const _fm3 = group.members.filter(function (b) { return b && b.name === group.names[0]; });
    if (_fm3.length) group = { names: [group.names[0]], members: _fm3 };
  }
  if (slot && !group) return { atoms: [], bonds: [] };
  const atoms = new Set();
  const bonds = new Set();

  for (let i = 0; i < allAtomsTypeList3D.length; i++) {
    if (allAtomsTypeList3D[i] !== "C" || mainSet.has(i)) continue;

    const neighbors = Array.isArray(atomConnectivityList3D[i])
      ? atomConnectivityList3D[i]
      : [];
    const parent = neighbors.find((nb) => mainSet.has(nb));
    if (parent === undefined) continue;

    const sideSet = new Set([i]);
    const stack = [i];
    while (stack.length > 0) {
      const node = stack.pop();
      const ns = Array.isArray(atomConnectivityList3D[node])
        ? atomConnectivityList3D[node]
        : [];
      for (let k = 0; k < ns.length; k++) {
        const nb = ns[k];
        if (nb === parent || allAtomsTypeList3D[nb] !== "C" || sideSet.has(nb))
          continue;
        sideSet.add(nb);
        stack.push(nb);
      }
    }

    // Match the attachment-rooted carbon graph at its live parent locant.
    // Equal-sized straight/branched groups must never cross-highlight.
    const locant = mainChainAtoms3D.indexOf(parent + 1) + 1;
    const branch = group ? fDescribeCarbonBranches(mainChainAtoms3D.map(n => n - 1),
      atomConnectivityList3D, allAtomsTypeList3D).find(d => d.attach === i) : null;
    if (group && !group.members.some(function (b) {
      return branch && b.locant === locant && b.signature === branch.signature;
    })) continue;

    for (const node of sideSet) {
      atoms.add(node + 1);
      const ns = Array.isArray(atomConnectivityList3D[node])
        ? atomConnectivityList3D[node]
        : [];
      for (let k = 0; k < ns.length; k++) {
        const nb = ns[k];
        if (!sideSet.has(nb)) continue;
        const a = node + 1;
        const b = nb + 1;
        for (let idx = 0; idx < bondList3D.length; idx++) {
          const bond = bondList3D[idx];
          if (!bond) continue;
          const sameBond =
            (bond[0] === a && bond[1] === b) ||
            (bond[0] === b && bond[1] === a);
          if (sameBond) {
            bonds.add(idx + 1);
            break;
          }
        }
      }
    }
  }

  return { atoms: [...atoms], bonds: [...bonds] };
}

// Paint a resolved branch group green (2D atom + bond backgrounds, 3D halo
// selection), mirroring fGetHydrocarbonBranchHighlight slot/piece scoping so
// paint and quiz target always agree. Used by classic branch-box sub-cases
// and (via the exact-reward replay) by the branch quiz. Returns true when
// something painted; false keeps the caller's FG paint (empty group).
function fPaintBranchHighlightAtoms(slot, mode) {
  try {
    var useMode = (typeof mode === "string" && mode) ? mode : ((typeof nameAnalysisMode !== "undefined") ? nameAnalysisMode : "");
    var gm = null;
    try { gm = (typeof fGetHydrocarbonBranchHighlight === "function") ? fGetHydrocarbonBranchHighlight(slot, useMode) : null; } catch (eG) { gm = null; }
    var atoms = (gm && gm.atoms) || [];
    var bonds = (gm && gm.bonds) || [];
    if (!atoms.length) return false;
    if (typeof window !== "undefined" && window.__mulerExplainQuiet) return true;
    var aArg = atoms.map(function (a) { return a + ",9"; }).join(",");
    try { if (typeof jsmeNomeclatureApplet !== "undefined" && jsmeNomeclatureApplet) jsmeNomeclatureApplet.setAtomBackgroundColors(0, aArg); } catch (eA) {}
    if (bonds.length) {
      var bArg = bonds.map(function (b) { return b + ",9"; }).join(",");
      try { if (typeof jsmeNomeclatureApplet !== "undefined" && jsmeNomeclatureApplet) jsmeNomeclatureApplet.setBondBackgroundColors(0, bArg); } catch (eB) {}
    }
    try {
      var g3 = (typeof fGetHydrocarbonBranchHighlight3D === "function") ? fGetHydrocarbonBranchHighlight3D(slot) : null;
      var a3 = (g3 && g3.atoms) || [];
      if (a3.length && typeof fJSmolScript === "function") {
        var arg3d = "select";
        for (var i = 0; i < a3.length; i++) arg3d += (i ? "," : "") + " atomno=" + a3[i];
        arg3d += "; select connected(selected) and _H or selected;";
        var _jm = null;
        try { _jm = (typeof jmolAppletNomeclature !== "undefined") ? jmolAppletNomeclature : null; } catch (eJM) { _jm = null; }
        fJSmolScript(_jm,
          "select all; selectionHalos off; color atoms none; color bonds none;" +
          arg3d + ";color selectionHalos[X79dc6d]; selectionHalos on; color atoms [X79dc6d];");
        try { JmolSelection = arg3d; } catch (eJS) {}
      }
    } catch (e3) {}
    try { if (typeof fUpdateSVG === "function") fUpdateSVG(); } catch (eU) {}
    return true;
  } catch (e) { return false; }
}

// ── Ether helpers ─────────────────────────────────────────────────────────
// Alkoxy-side carbon (0-based) = ether-O neighbour NOT on the parent chain.
function fGetEtherAlkoxyC() {
  if (!functionalGroupObj || !functionalGroupObj.ether || !functionalGroupObj.ether.O) return null;
  const oIdx = functionalGroupObj.ether.O[0];
  if (oIdx === undefined || !Array.isArray(atomConnectivityList[oIdx])) return null;
  const nbrs = atomConnectivityList[oIdx].filter(function (n) {
    return allAtomsTypeList[n] === "C";
  });
  if (nbrs.length === 0) return null;
  if (Array.isArray(mainChainAtomsList)) {
    for (let i = 0; i < nbrs.length; i++) {
      if (mainChainAtomsList.indexOf(nbrs[i] + 1) < 0) return nbrs[i];
    }
  }
  if (typeof etherInfo !== "undefined" && etherInfo) return etherInfo.alkoxyAttachC;
  return nbrs.length > 1 ? nbrs[1] : nbrs[0];
}

// Ordered alkoxy chain (1-based JSME numbers), attachment C first.
// Live rule (mirrors fGetEtherAlkoxyChain3D): the alkoxy side is the FIRST
// O-bonded carbon NOT on the current main chain, BFS-expanded over the
// carbon-only graph — so the highlight sweeps when the stepper (or free
// browsing) moves the parent chain elsewhere. At the winner chain this picks
// the stored side in every realistic case (symmetric, ethyl/isopropyl/butyl
// methyl: the non-parent side is found regardless of neighbor order).
// Falls back to load-time etherInfo, then to fGetEtherAlkoxyC.
function fGetEtherAlkoxyChain() {
  if (typeof functionalGroupObj !== "undefined" && functionalGroupObj &&
      functionalGroupObj.ether && functionalGroupObj.ether.O) {
    var oIdx = functionalGroupObj.ether.O[0];
    if (oIdx !== undefined && Array.isArray(atomConnectivityList[oIdx])) {
      var nbrs = atomConnectivityList[oIdx].filter(function (n) {
        return allAtomsTypeList[n] === "C";
      });
      var att = null;
      if (Array.isArray(mainChainAtomsList)) {
        for (var i = 0; i < nbrs.length; i++) {
          if (mainChainAtomsList.indexOf(nbrs[i] + 1) < 0) { att = nbrs[i]; break; }
        }
      }
      if (att === null || att === undefined) att = nbrs.length > 1 ? nbrs[1] : nbrs[0];
      if (att !== null && att !== undefined) {
        var seen = {};
        var q = [att];
        seen[att] = true;
        while (q.length > 0) {
          var n = q.pop();
          var nbs = atomConnectivityList[n] || [];
          for (var k = 0; k < nbs.length; k++) {
            if (allAtomsTypeList[nbs[k]] === "C" && !seen[nbs[k]]) {
              seen[nbs[k]] = true;
              q.push(nbs[k]);
            }
          }
        }
        var rest = Object.keys(seen).map(function (x) { return parseInt(x); }).filter(function (c) { return c !== att; });
        return [att + 1].concat(rest.map(function (c) { return c + 1; }));
      }
    }
  }
  if (typeof etherInfo !== "undefined" && etherInfo && Array.isArray(etherInfo.alkoxyFrag)) {
    var att0 = etherInfo.alkoxyAttachC;
    var rest0 = etherInfo.alkoxyFrag.filter(function (c) { return c !== att0; });
    return [att0 + 1].concat(rest0.map(function (c) { return c + 1; }));
  }
  var alk = fGetEtherAlkoxyC();
  return alk !== null && alk !== undefined ? [alk + 1] : null;
}

// 3D mirror: alkoxy-side carbon (0-based SDF index).
function fGetEtherAlkoxyC3D() {
  if (!functionalGroupObj3D || !functionalGroupObj3D.ether || !functionalGroupObj3D.ether.O) return null;
  const oIdx = functionalGroupObj3D.ether.O[0];
  if (oIdx === undefined || !Array.isArray(atomConnectivityList3D[oIdx])) return null;
  const nbrs = atomConnectivityList3D[oIdx].filter(function (n) {
    return allAtomsTypeList3D[n] === "C";
  });
  if (nbrs.length === 0) return null;
  if (Array.isArray(mainChainAtoms3D)) {
    for (let i = 0; i < nbrs.length; i++) {
      if (mainChainAtoms3D.indexOf(nbrs[i] + 1) < 0) return nbrs[i];
    }
  }
  return nbrs.length > 1 ? nbrs[1] : nbrs[0];
}

// 3D mirror: ordered alkoxy chain (1-based SDF numbers), attachment C first.
function fGetEtherAlkoxyChain3D() {
  if (!functionalGroupObj3D || !functionalGroupObj3D.ether || !functionalGroupObj3D.ether.O) return null;
  const oIdx = functionalGroupObj3D.ether.O[0];
  if (oIdx === undefined || !Array.isArray(atomConnectivityList3D[oIdx])) return null;
  const att = fGetEtherAlkoxyC3D();
  if (att === null || att === undefined) return null;
  // BFS over 3D carbon-only graph from attachment
  const seen = {};
  const q = [att];
  seen[att] = true;
  while (q.length > 0) {
    const n = q.pop();
    const nbs = atomConnectivityList3D[n] || [];
    for (let i = 0; i < nbs.length; i++) {
      if (allAtomsTypeList3D[nbs[i]] === "C" && !seen[nbs[i]]) {
        seen[nbs[i]] = true;
        q.push(nbs[i]);
      }
    }
  }
  const rest = Object.keys(seen).map(function (x) { return parseInt(x); }).filter(function (c) { return c !== att; });
  return [att + 1].concat(rest.map(function (c) { return c + 1; }));
}

// 3D mirror: ether functional group C-O-C (1-based SDF numbers) — the bridging
// O plus its carbon neighbors. Used to color the two C–O bonds explicitly,
// since the halo path highlights atoms only.
function fGetEtherGroupFragment3D() {
  if (!functionalGroupObj3D || !functionalGroupObj3D.ether || !functionalGroupObj3D.ether.O) return null;
  const oIdx = functionalGroupObj3D.ether.O[0];
  if (oIdx === undefined || !Array.isArray(atomConnectivityList3D[oIdx])) return null;
  const frag = [oIdx + 1];
  const nbrs = atomConnectivityList3D[oIdx].filter(function (n) {
    return allAtomsTypeList3D[n] === "C";
  });
  for (let i = 0; i < nbrs.length; i++) {
    if (frag.indexOf(nbrs[i] + 1) < 0) frag.push(nbrs[i] + 1);
  }
  return frag.length > 1 ? frag : null;
}

// COMMON ether name parts: [{label, chain, chain3D, kind}] + suffix "αιθέρας".
// kind: "alkyl" (chain only, no O) or "ether" (C-O-C, no numbering).
// chain/chain3D: 1-based atom lists for highlight + numbering.
function fGetEtherCommonParts() {
  if (!selectedMol || !nameExamples[selectedMol]) return null;
  if (nameExamples[selectedMol].classification?.chemicalClass !== "ethers") return null;
  const parentLen = etherInfo ? etherInfo.parentLen : (Array.isArray(mainChainAtomsList) ? mainChainAtomsList.length : 0);
  const alkLen = (typeof etherInfo !== "undefined" && etherInfo && etherInfo.alkoxyLen) || 1;
  const _eI = (typeof etherInfo !== "undefined" && etherInfo) ? etherInfo : null;
  const stemFor = function (n, attachC, fragment) {
    const iso = (typeof fAlkylGroupName !== "undefined") ? fAlkylGroupName(n, attachC, "substituent", fragment) : null;
    const full = iso || ((typeof alkylSubstituentNames !== "undefined" && alkylSubstituentNames[n]) || (nameMainCompList1[n - 1] || ""));
    return String(full).replace(/ο$/, "");
  };
  const parentChain = _eI ? _eI.parentFrag.map(c=>c+1) : (mainChainAtomsList || []).slice();
  const alkoxyChain = fGetEtherAlkoxyChain() || [];
  const o3 = functionalGroupObj3D && functionalGroupObj3D.ether && functionalGroupObj3D.ether.O[0];
  const alk3 = fGetEtherAlkoxyC3D();
  const parentAttach3 = o3 == null ? null : (atomConnectivityList3D[o3] || []).find(c=>allAtomsTypeList3D[c]==='C' && c!==alk3);
  const parentChain3D = parentAttach3 == null ? [] : fCarbonFragment(parentAttach3,atomConnectivityList3D,allAtomsTypeList3D).map(c=>c+1);
  const alkoxyChain3D = fGetEtherAlkoxyChain3D() || [];
  const symmetric = (typeof etherInfo !== "undefined" && etherInfo) ? !!etherInfo.symmetric : parentLen === alkLen;
  if (symmetric) {
    const alkyl = stemFor(alkLen, _eI && _eI.alkoxyAttachC, _eI && _eI.alkoxyFrag);
    const both = parentChain.concat(alkoxyChain.filter(function (a) { return parentChain.indexOf(a) < 0; }));
    const both3D = parentChain3D.concat(alkoxyChain3D.filter(function (a) { return parentChain3D.indexOf(a) < 0; }));
    return {
      symmetric: true,
      parts: [
        { label: nameMultiPrefix[1] || "δι", chain: both, chain3D: both3D, kind: "alkyl", numberChain: parentChain, numberChain3D: parentChain3D },
        { label: alkyl, chain: both, chain3D: both3D, kind: "alkyl", numberChain: parentChain, numberChain3D: parentChain3D },
        { label: "αιθέρας", chain: "ether", chain3D: "ether", kind: "ether", numberChain: null, numberChain3D: null },
      ],
    };
  }
  const sP = stemFor(parentLen, _eI && _eI.parentAttachC, _eI && _eI.parentFrag), sA = stemFor(alkLen, _eI && _eI.alkoxyAttachC, _eI && _eI.alkoxyFrag);
  const mk = function (label, isParent) {
    // Alkoxy numbering (v54.39): systematic internal order instead of the
    // raw fragment order; the parent chain keeps main-chain numbering.
    var _numA = alkoxyChain, _numA3 = alkoxyChain3D;
    if (!isParent) {
      try {
        var _anm = null;
        if (typeof fAlkylGroupName === "function" && _eI) {
          _anm = fAlkylGroupName(alkLen, _eI.alkoxyAttachC, "alkoxy", _eI.alkoxyFrag) || null;
        }
        if (!_anm && typeof alkoxyNames !== "undefined" && _eI) { try { _anm = alkoxyNames[alkLen] || null; } catch (eAN2) {} }
        var _ord = null, _ord3 = null;
        try { _ord = fEtherAlkoxyNumbering(alkoxyChain, _anm); } catch (eON) { _ord = null; }
        try { _ord3 = fEtherAlkoxyNumbering3D(alkoxyChain3D, _anm); } catch (eON3) { _ord3 = null; }
        if (_ord && _ord.length) _numA = _ord;
        if (_ord3 && _ord3.length) _numA3 = _ord3;
      } catch (eAN3) {}
    }
    return {
      label: label,
      chain: isParent ? parentChain : alkoxyChain,
      chain3D: isParent ? parentChain3D : alkoxyChain3D,
      kind: "alkyl",
      numberChain: isParent ? mainChainAtomsList.slice() : _numA,
      numberChain3D: isParent ? mainChainAtoms3D.slice() : _numA3,
    };
  };
  const pair = [mk(sP, true), mk(sA, false)].sort(function (a, b) {
    return fEtherNameSortKey(a.label) < fEtherNameSortKey(b.label) ? -1 : fEtherNameSortKey(a.label) > fEtherNameSortKey(b.label) ? 1 : 0;
  });
  fEtherCommonLabels(pair.map(p=>p.label)).forEach((label,i)=>{pair[i].label=label;});
  pair.push({ label: "αιθέρας", chain: "ether", chain3D: "ether", kind: "ether", numberChain: null, numberChain3D: null });
  return { symmetric: false, parts: pair };
}

// ── Ester helpers ─────────────────────────────────────────────────────────
// Scope v41: saturated acyclic mono-esters R-C(=O)-O-R'.
// esterInfo (2D, from fCalcMainChain): {oDouble, oSingle, carbonylC,
// alcoholAttachC, acidFrag, alcoholFrag, acidLen, alcoholLen} — 0-based.


// ── Systematic internal numbering for O-linked alkyl fragments ─────────
// v54.39: on-canvas numbers must follow the substituent's own numbering —
// the attachment atom carries the free-valence locant (2 for propan-2-yl),
// the parent chain runs sequentially outward, and a sub-branch (e.g. the
// isobutyl 2-methyl) takes the next free number so every shown atom is
// traceable. Positional numbering can only render i+1, so the fragment is
// reordered instead of relabeled (no numbering-engine changes).
// Table: common Greek alkyl name -> {attachLoc, parentLen}. Straight chains
// (incl. decorated methyl/ethyl, any n-alkyl) need no entry — attachLoc 1,
// parent = longest path. Unknown branched shapes, C-C multi-bonds and rings
// fall back to today's fragment order (never worse). Applies in every
// language and toggle state: numbering follows the rules, not the display.
var ALKYL_SYS_NUMBERING = {
  "ισοπροπυλο": { attach: 2, parent: 3 },
  "sec-βουτυλο": { attach: 2, parent: 4 },
  "tert-βουτυλο": { attach: 2, parent: 3 },
  "ισοβουτυλο": { attach: 1, parent: 3 }
};
// Returns the fragment atoms (0-based) in display order, or null (keep
// today's order). connList/typeList are 0-based; bondList is 1-based
// [a, b, order] or null (skips the saturation check when absent).
// specOverride: { attach } (parent defaults to longest path) or null.
function fAlkylNumberingOrder(frag0, attach0, connList, typeList, bondListOrNull, commonAlkylName, specOverride) {
  try {
    if (!Array.isArray(frag0) || !frag0.length) return null;
    if (attach0 === undefined || attach0 === null) return null;
    var side = [];
    for (var si = 0; si < frag0.length; si++) {
      var _sa = frag0[si];
      if (typeList[_sa] === "C") side.push(_sa);
    }
    if (!side.length || side.indexOf(attach0) < 0) return null;
    // acyclic saturated side only (connected tree, all single bonds)
    var inSide = {};
    for (var sj = 0; sj < side.length; sj++) inSide[side[sj]] = true;
    var seen = {}, stack = [attach0], edgeCount = 0, _ok = true;
    seen[attach0] = true;
    while (stack.length && _ok) {
      var node = stack.pop();
      var nbs = (connList && connList[node]) || [];
      for (var ni = 0; ni < nbs.length; ni++) {
        var nb = nbs[ni];
        if (!inSide[nb]) continue;
        var o = 1;
        try {
          var bl = bondListOrNull;
          if (bl && typeof bl.length === "number") {
            for (var bi = 0; bi < bl.length; bi++) {
              var bb = bl[bi];
              if (bb && ((bb[0] - 1 === node && bb[1] - 1 === nb) || (bb[0] - 1 === nb && bb[1] - 1 === node))) { o = bb[2]; break; }
            }
          }
        } catch (eBO) { o = 1; }
        if (o !== 1) { _ok = false; break; }
        edgeCount++;
        if (!seen[nb]) { seen[nb] = true; stack.push(nb); }
      }
    }
    var seenCount = 0;
    for (var sk in seen) { if (Object.prototype.hasOwnProperty.call(seen, sk)) seenCount++; }
    if (!_ok || seenCount !== side.length || edgeCount / 2 !== side.length - 1) return null;
    // longest simple path from attach (DFS, ascending neighbours: deterministic)
    var best = [];
    (function () {
      var path = [attach0], vis = {};
      vis[attach0] = true;
      function dfs(node) {
        if (path.length > best.length) best = path.slice();
        var nbs2 = ((connList && connList[node]) || []).slice().sort(function (a, b) { return a - b; });
        for (var i = 0; i < nbs2.length; i++) {
          var nb2 = nbs2[i];
          if (!inSide[nb2] || vis[nb2]) continue;
          vis[nb2] = true; path.push(nb2);
          dfs(nb2);
          path.pop(); delete vis[nb2];
        }
      }
      dfs(attach0);
    })();
    if (!best.length) return null;
    // resolve attach locant + parent length: explicit spec (acid), table
    // entry, or straight-chain rule (longest path must cover every atom)
    var attachLoc = 1, parentLen = best.length;
    if (specOverride && typeof specOverride.attach === "number") {
      attachLoc = specOverride.attach;
      if (typeof specOverride.parent === "number" && specOverride.parent > 0) parentLen = specOverride.parent;
    } else {
      var nm = String(commonAlkylName == null ? "" : commonAlkylName);
      if (/οξυ$/.test(nm)) nm = nm.replace(/οξυ$/, "υλο");
      else if (/υλ$/.test(nm)) nm = nm + "ο";
      if (Object.prototype.hasOwnProperty.call(ALKYL_SYS_NUMBERING, nm)) {
        attachLoc = ALKYL_SYS_NUMBERING[nm].attach;
        parentLen = ALKYL_SYS_NUMBERING[nm].parent;
      } else if (best.length !== side.length) {
        return null;
      } else {
        attachLoc = 1; parentLen = side.length;
      }
    }
    if (best.length > parentLen) return null;
    var P = best.slice(0, parentLen);
    var inP = {};
    for (var pi = 0; pi < P.length; pi++) inP[P[pi]] = true;
    var leftovers = [];
    for (var li = 0; li < side.length; li++) {
      if (!inP[side[li]]) leftovers.push(side[li]);
    }
    leftovers.sort(function (a, b) { return a - b; });
    // chain-completing atom(s) before the attachment (at most attachLoc - 1
    // for the v1 set; symmetric ties broken by ascending index — any choice
    // is a valid numbering), then the path, then sub-branches in order
    var need = attachLoc - 1, chainTaken = [], branchRest = [];
    for (var qi = 0; qi < leftovers.length; qi++) {
      var q = leftovers[qi];
      if (((connList && connList[attach0]) || []).indexOf(q) >= 0 && chainTaken.length < need) chainTaken.push(q);
      else branchRest.push(q);
    }
    if (chainTaken.length < need) return null;
    return chainTaken.concat(P).concat(branchRest);
  } catch (eN) { return null; }
}

// Numbering-order wrappers (1-based in/out, attach-first or null on any
// gap — callers fall back to today's fragment order). Highlight arrays are
// never reordered: numbering and highlight stay on the same molecule but
// follow their own contracts.
function fEsterAlcoholNumbering(chain1) {
  try {
    if (!Array.isArray(chain1) || !chain1.length) return null;
    var _e = (typeof esterInfo !== "undefined") ? esterInfo : null;
    var att = (_e && _e.alcoholAttachC != null) ? _e.alcoholAttachC : chain1[0] - 1;
    var nm = (typeof nameComponentsList !== "undefined" && nameComponentsList) ? nameComponentsList[10] : null;
    var ord = fAlkylNumberingOrder(chain1.map(function (n) { return n - 1; }), att,
      (typeof atomConnectivityList !== "undefined" ? atomConnectivityList : null),
      (typeof allAtomsTypeList !== "undefined" ? allAtomsTypeList : null),
      (typeof bondList !== "undefined" ? bondList : null), nm, null);
    if (!ord || !ord.length) return null;
    return ord.map(function (n) { return n + 1; });
  } catch (e) { return null; }
}
function fEsterAlcoholNumbering3D(chain1) {
  try {
    if (!Array.isArray(chain1) || !chain1.length) return null;
    var att = null;
    try { att = (typeof fGetEsterAlcoholC3D === "function") ? fGetEsterAlcoholC3D() : null; } catch (eA) { att = null; }
    if (att === null || att === undefined) att = chain1[0] - 1;
    var nm = (typeof nameComponentsList !== "undefined" && nameComponentsList) ? nameComponentsList[10] : null;
    var ord = fAlkylNumberingOrder(chain1.map(function (n) { return n - 1; }), att,
      (typeof atomConnectivityList3D !== "undefined" ? atomConnectivityList3D : null),
      (typeof allAtomsTypeList3D !== "undefined" ? allAtomsTypeList3D : null),
      (typeof bondList3D !== "undefined" ? bondList3D : null), nm, null);
    if (!ord || !ord.length) return null;
    return ord.map(function (n) { return n + 1; });
  } catch (e) { return null; }
}
function fEsterAcidNumbering3D(chain1) {
  try {
    if (!Array.isArray(chain1) || !chain1.length) return null;
    var att = null;
    try { att = (typeof fGetEsterAcidC3D === "function") ? fGetEsterAcidC3D() : null; } catch (eA) { att = null; }
    if (att === null || att === undefined) att = chain1[0] - 1;
    var ord = fAlkylNumberingOrder(chain1.map(function (n) { return n - 1; }), att,
      (typeof atomConnectivityList3D !== "undefined" ? atomConnectivityList3D : null),
      (typeof allAtomsTypeList3D !== "undefined" ? allAtomsTypeList3D : null),
      (typeof bondList3D !== "undefined" ? bondList3D : null), null, { attach: 1 });
    if (!ord || !ord.length) return null;
    return ord.map(function (n) { return n + 1; });
  } catch (e) { return null; }
}
function fEsterAcidNumbering(chain1) {
  // Acid parent numbering (v54.39): carbonyl C is always C1; longest
  // saturated chain from it numbers sequentially, extra branches last.
  try {
    if (!Array.isArray(chain1) || !chain1.length) return null;
    var _e = (typeof esterInfo !== "undefined") ? esterInfo : null;
    var att = (_e && _e.carbonylC != null) ? _e.carbonylC : chain1[0] - 1;
    var ord = fAlkylNumberingOrder(chain1.map(function (n) { return n - 1; }), att,
      (typeof atomConnectivityList !== "undefined" ? atomConnectivityList : null),
      (typeof allAtomsTypeList !== "undefined" ? allAtomsTypeList : null),
      (typeof bondList !== "undefined" ? bondList : null), null, { attach: 1 });
    if (!ord || !ord.length) return null;
    return ord.map(function (n) { return n + 1; });
  } catch (e) { return null; }
}
function fEtherAlkoxyNumbering(chain1, alkoxyName) {
  try {
    if (!Array.isArray(chain1) || !chain1.length) return null;
    var att = chain1[0] - 1;
    try {
      var _e = (typeof etherInfo !== "undefined") ? etherInfo : null;
      if (_e && _e.alkoxyAttachC != null && chain1.indexOf(_e.alkoxyAttachC + 1) >= 0) att = _e.alkoxyAttachC;
    } catch (eA) {}
    var ord = fAlkylNumberingOrder(chain1.map(function (n) { return n - 1; }), att,
      (typeof atomConnectivityList !== "undefined" ? atomConnectivityList : null),
      (typeof allAtomsTypeList !== "undefined" ? allAtomsTypeList : null),
      (typeof bondList !== "undefined" ? bondList : null), alkoxyName, null);
    if (!ord || !ord.length) return null;
    return ord.map(function (n) { return n + 1; });
  } catch (e) { return null; }
}
function fEtherAlkoxyNumbering3D(chain1, alkoxyName) {
  try {
    if (!Array.isArray(chain1) || !chain1.length) return null;
    var att = null;
    try { att = (typeof fGetEtherAlkoxyC3D === "function") ? fGetEtherAlkoxyC3D() : null; } catch (eA) { att = null; }
    if (att === null || att === undefined) att = chain1[0] - 1;
    var ord = fAlkylNumberingOrder(chain1.map(function (n) { return n - 1; }), att,
      (typeof atomConnectivityList3D !== "undefined" ? atomConnectivityList3D : null),
      (typeof allAtomsTypeList3D !== "undefined" ? allAtomsTypeList3D : null),
      (typeof bondList3D !== "undefined" ? bondList3D : null), alkoxyName, null);
    if (!ord || !ord.length) return null;
    return ord.map(function (n) { return n + 1; });
  } catch (e) { return null; }
}

// Ordered alcohol chain (1-based JSME numbers), attachment C first.
function fGetEsterAlcoholChain() {
  if (typeof esterInfo !== "undefined" && esterInfo && Array.isArray(esterInfo.alcoholFrag)) {
    const att = esterInfo.alcoholAttachC;
    const rest = esterInfo.alcoholFrag.filter(function (c) { return c !== att; });
    return [att + 1].concat(rest.map(function (c) { return c + 1; }));
  }
  return null;
}

// 3D mirror: alcohol-side carbon (0-based SDF index).
function fGetEsterAlcoholC3D() {
  if (!functionalGroupObj3D || !functionalGroupObj3D.ester || !functionalGroupObj3D.ester.O) return null;
  const pair = functionalGroupObj3D.ester.O[0];
  if (!pair) return null;
  const ketoneO = pair[0], etherO = pair[1];
  const carbC = (Array.isArray(atomConnectivityList3D[ketoneO]) ? atomConnectivityList3D[ketoneO] : []).filter(function (n) {
    return allAtomsTypeList3D[n] === "C";
  })[0];
  const oNbrs = (Array.isArray(atomConnectivityList3D[etherO]) ? atomConnectivityList3D[etherO] : []).filter(function (n) {
    return allAtomsTypeList3D[n] === "C";
  });
  for (let i = 0; i < oNbrs.length; i++) {
    if (oNbrs[i] !== carbC) return oNbrs[i];
  }
  return null;
}

// 3D mirror: ordered alcohol chain (1-based SDF numbers), attachment C first.
function fGetEsterAlcoholChain3D() {
  const att = fGetEsterAlcoholC3D();
  if (att === null || att === undefined) return null;
  const seen = {};
  const q = [att];
  seen[att] = true;
  while (q.length > 0) {
    const n = q.pop();
    const nbs = atomConnectivityList3D[n] || [];
    for (let i = 0; i < nbs.length; i++) {
      if (allAtomsTypeList3D[nbs[i]] === "C" && !seen[nbs[i]]) {
        seen[nbs[i]] = true;
        q.push(nbs[i]);
      }
    }
  }
  const rest = Object.keys(seen).map(function (x) { return parseInt(x); }).filter(function (c) { return c !== att; });
  return [att + 1].concat(rest.map(function (c) { return c + 1; }));
}

// Ordered acid chain (1-based JSME numbers), carbonyl C first.
function fGetEsterAcidChain() {
  if (typeof esterInfo !== "undefined" && esterInfo && Array.isArray(esterInfo.acidFrag)) {
    const att = esterInfo.carbonylC;
    const rest = esterInfo.acidFrag.filter(function (c) { return c !== att; });
    return [att + 1].concat(rest.map(function (c) { return c + 1; }));
  }
  return null;
}

// The stem/numbering concerns the selected acid parent; bond-type highlights
// still use the complete acid fragment above. Never number alcohol carbons.
function fGetEsterAcidParentChain() {
  if (!fIsSingleEster()) return null;
  const fragment = fGetEsterAcidChain();
  if (Array.isArray(mainChainAtomsList) && mainChainAtomsList[0] === esterInfo.carbonylC + 1 &&
      mainChainAtomsList.every(n => fragment.includes(n))) return mainChainAtomsList.slice();
  return fragment;
}

function fGetEsterAcidParentChain3D() {
  const carbonyl = fGetEsterAcidC3D(), fragment = fGetEsterAcidChain3D();
  if (carbonyl === null || !fragment) return null;
  if (Array.isArray(mainChainAtoms3D) && mainChainAtoms3D[0] === carbonyl + 1 &&
      mainChainAtoms3D.every(n => fragment.includes(n))) return mainChainAtoms3D.slice();
  return null; // 3D analysis/mapping has not caught up with this molecule.
}

// 3D mirror: acid-side carbon (0-based SDF index) = C neighbor of the ketone O.
function fGetEsterAcidC3D() {
  if (!functionalGroupObj3D || !functionalGroupObj3D.ester || !functionalGroupObj3D.ester.O) return null;
  const pair = functionalGroupObj3D.ester.O[0];
  if (!pair) return null;
  const carbC = (Array.isArray(atomConnectivityList3D[pair[0]]) ? atomConnectivityList3D[pair[0]] : []).filter(function (n) {
    return allAtomsTypeList3D[n] === "C";
  })[0];
  return (carbC === undefined) ? null : carbC;
}

// 3D mirror: ordered acid chain (1-based SDF numbers), carbonyl C first.
function fGetEsterAcidChain3D() {
  const att = fGetEsterAcidC3D();
  if (att === null || att === undefined) return null;
  const seen = {};
  const q = [att];
  seen[att] = true;
  while (q.length > 0) {
    const n = q.pop();
    const nbs = atomConnectivityList3D[n] || [];
    for (let i = 0; i < nbs.length; i++) {
      if (allAtomsTypeList3D[nbs[i]] === "C" && !seen[nbs[i]]) {
        seen[nbs[i]] = true;
        q.push(nbs[i]);
      }
    }
  }
  const rest = Object.keys(seen).map(function (x) { return parseInt(x); }).filter(function (c) { return c !== att; });
  return [att + 1].concat(rest.map(function (c) { return c + 1; }));
}

// Acid PARENT chain for branched esters — the named chain,
// not the whole acid fragment (parent + branches).
function fGetEsterAcidParentChain() {
  if (!fIsSingleEster()) return null;
  const fragment = fGetEsterAcidChain();
  if (Array.isArray(mainChainAtomsList) && mainChainAtomsList[0] === esterInfo.carbonylC + 1 &&
      mainChainAtomsList.every(n => fragment.includes(n))) return mainChainAtomsList.slice();
  return fragment;
}
function fGetEsterAcidParentChain3D() {
  const carbonyl = fGetEsterAcidC3D(), fragment = fGetEsterAcidChain3D();
  if (carbonyl === null || !fragment) return null;
  if (Array.isArray(mainChainAtoms3D) && mainChainAtoms3D[0] === carbonyl + 1 &&
      mainChainAtoms3D.every(n => fragment.includes(n))) return mainChainAtoms3D.slice();
  return null; // 3D analysis/mapping has not caught up with this molecule.
}

// Sole-FG ester predicate: name + highlight overrides apply only when the
// ester is the single functional group (matches the fGuessName ester branch).
function fIsSingleEster() {
  return (typeof functionalGroupsList !== "undefined" && Array.isArray(functionalGroupsList) &&
    functionalGroupsList.length === 1 && functionalGroupsList[0] === "ester" &&
    typeof esterInfo !== "undefined" && esterInfo && Array.isArray(esterInfo.acidFrag));
}

// Ester triad O-C(=O)-O (1-based JSME numbers) for highlight (no numbering).
function fGetEsterTriad() {
  if (typeof esterInfo !== "undefined" && esterInfo && esterInfo.carbonylC !== undefined) {
    return [esterInfo.oDouble + 1, esterInfo.carbonylC + 1, esterInfo.oSingle + 1];
  }
  if (!functionalGroupObj || !functionalGroupObj.ester || !functionalGroupObj.ester.O) return null;
  const pair = functionalGroupObj.ester.O[0];
  if (!pair) return null;
  const carbC = (atomConnectivityList[pair[0]] || []).filter(function (n) {
    return allAtomsTypeList[n] === "C";
  })[0];
  if (carbC === undefined) return [pair[0] + 1, pair[1] + 1];
  return [pair[0] + 1, carbC + 1, pair[1] + 1];
}

// Ester functional group C(=O)-O-C (1-based JSME numbers): triad + alcohol C.
function fGetEsterGroupFragment() {
  const triad = fGetEsterTriad() || [];
  let alc = null;
  if (typeof esterInfo !== "undefined" && esterInfo && esterInfo.alcoholAttachC !== undefined) {
    alc = esterInfo.alcoholAttachC + 1;
  }
  if ((alc === null || alc === undefined) && functionalGroupObj && functionalGroupObj.ester && functionalGroupObj.ester.O) {
    const pair = functionalGroupObj.ester.O[0];
    if (pair) {
      const carbC = (atomConnectivityList[pair[0]] || []).filter(function (n) {
        return allAtomsTypeList[n] === "C";
      })[0];
      const oNbrs = (atomConnectivityList[pair[1]] || []).filter(function (n) {
        return allAtomsTypeList[n] === "C";
      });
      for (let i = 0; i < oNbrs.length; i++) {
        if (oNbrs[i] !== carbC) { alc = oNbrs[i] + 1; break; }
      }
    }
  }
  if (alc !== null && alc !== undefined && triad.indexOf(alc) < 0) triad.push(alc);
  return triad;
}

// 3D mirror: ester functional group (1-based SDF numbers).
function fGetEsterGroupFragment3D() {
  const triad = fGetEsterTriad3D() || [];
  const alc = fGetEsterAlcoholC3D();
  if (alc !== null && alc !== undefined && triad.indexOf(alc + 1) < 0) triad.push(alc + 1);
  return triad;
}

// 3D mirror: ester triad (1-based SDF numbers).
function fGetEsterTriad3D() {
  if (!functionalGroupObj3D || !functionalGroupObj3D.ester || !functionalGroupObj3D.ester.O) return null;
  const pair = functionalGroupObj3D.ester.O[0];
  if (!pair) return null;
  const carbC = (atomConnectivityList3D[pair[0]] || []).filter(function (n) {
    return allAtomsTypeList3D[n] === "C";
  })[0];
  if (carbC === undefined) return [pair[0] + 1, pair[1] + 1];
  return [pair[0] + 1, carbC + 1, pair[1] + 1];
}

// Sync IUPAC/COMMON toggle visuals (radios are rebuilt in fShowNameAnalysis).
function fUpdateEtherNamingButton() {
  const $btns = $("#radioEtherNaming .etherNamingRadio");
  if ($btns.length === 0) return;
  $btns.removeClass("selectedRadio").addClass("unselectedRadio");
  $btns
    .filter(`[data-naming-mode='${etherNamingMode}']`)
    .removeClass("unselectedRadio")
    .addClass("selectedRadio");
}

// Sync SCHOOL/SYSTEMATIC substituent toggle visuals (same rebuild pattern).
function fUpdateSubstNamingButton() {
  const $btns = $("#radioSubstNaming .substNamingRadio");
  if ($btns.length === 0) return;
  $btns.removeClass("selectedRadio").addClass("unselectedRadio");
  $btns
    .filter(`[data-subst-mode='${substNamingMode}']`)
    .removeClass("unselectedRadio")
    .addClass("selectedRadio");
}

// Chain-only highlight (no heteroatom): atoms + bonds with both ends in the
// set. With includeH, attached H atoms join the atom set and C–H bonds join
// the bond set (alkyl rule: CnH2n+1 highlights C + H + C–C + C–H). Expanded
// mode only in practice — condensed/skeletal models carry no H atoms, so the
// H scan is a no-op there (same pattern as fGetHydrocarbonBranchHighlight).
function fHighlightAtomChain(chainAtoms, includeH, skipBonds, skipAtoms) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  if (!Array.isArray(chainAtoms) || chainAtoms.length === 0) return;
  let atomSet = chainAtoms.slice();
  if (includeH && typeof bondList !== "undefined" && typeof allAtomsTypeList !== "undefined") {
    for (let b = 0; b < bondList.length; b++) {
      if (!bondList[b]) continue;
      const ba1 = bondList[b][0];
      const ba2 = bondList[b][1];
      if (chainAtoms.includes(ba1) && allAtomsTypeList[ba2 - 1] === "H") {
        if (!atomSet.includes(ba2)) atomSet.push(ba2);
      } else if (chainAtoms.includes(ba2) && allAtomsTypeList[ba1 - 1] === "H") {
        if (!atomSet.includes(ba1)) atomSet.push(ba1);
      }
    }
  }
  let atomArg = "";
  for (let i = 0; i < atomSet.length; i++) {
    atomArg += atomSet[i] + ",9";
    if (i < atomSet.length - 1) atomArg += ",";
  }
  jsmeNomeclatureApplet.setAtomBackgroundColors(0, atomArg);
  let bondArg = "";
  let first = true;
  for (let b = 0; b < bondList.length; b++) {
    if (!bondList[b]) continue;
    if (atomSet.includes(bondList[b][0]) && atomSet.includes(bondList[b][1])) {
      bondArg += (first ? "" : ",") + (b + 1) + ",9";
      first = false;
    }
  }
  // Numbering path may opt out of atoms and/or bonds independently
  // (settings); alkyl-rule callers always keep both (opts omitted → false).
  if (!skipAtoms) jsmeNomeclatureApplet.setAtomBackgroundColors(0, atomArg);
  if (bondArg && !skipBonds) jsmeNomeclatureApplet.setBondBackgroundColors(0, bondArg);
  fUpdateSVG();
}

function fHighlightAtomChain3D(chainAtoms3D, skipH, skipBonds, skipAtoms) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  if (!Array.isArray(chainAtoms3D) || chainAtoms3D.length === 0) return;
  let arg = "select";
  for (let i = 0; i < chainAtoms3D.length; i++) {
    arg += " atomno=" + chainAtoms3D[i];
    if (i < chainAtoms3D.length - 1) arg += ",";
  }
  // skipH: halo exactly the listed atoms (ester group: alkyl C without its H).
  if (!skipH) arg += "; select connected(selected) and _H or selected;";
  // Numbering path may opt out of atoms and/or bonds independently
  // (settings); alkyl-rule callers always keep both (opts omitted → false).
  // Bonds are always explicit: green when on, neutral grey when off — plain
  // `none` would inherit the atom color and defeat the off state.
  // Halos belong to the atoms half: skipped together with the atoms.
  // NOTE: the bond clause carries its own leading `;` — when atoms are off
  // _atomClause is empty and the separator must still be there, otherwise
  // `select …` fuses with `color …` into one unparsable command.
  var _atomClause = skipAtoms
    ? ""
    : ";color selectionHalos[XD8EEDC]; selectionHalos on; color atoms [XD8EEDC]";
  fJSmolScript(
    jmolAppletNomeclature,
    "select all; selectionHalos off; color atoms none; color bonds none;" + arg +
      _atomClause +
      (skipBonds ? ";color bonds [X909090];" : ";color bonds [XD8EEDC];"),
  );
  JmolSelection = arg;
}

// Explicit 3D fragment-bond coloring (green): colors every bond with both
// ends in fragAtoms (1-based SDF numbers). With includeH, bonds from a
// fragment atom to a connected H are also colored (alkyl rule: CnH2n+1
// highlights C + H + C–C + C–H). The shared halo paths highlight atoms only,
// so COMMON ether/ester clicks and the IUPAC alkoxy prefix call this after
// their atom highlight — same pattern as the v42 ester triad fix, batched
// into one script to avoid Jmol queue races.
function fColorFragmentBonds3D(fragAtoms, includeH) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  if (!Array.isArray(fragAtoms) || fragAtoms.length === 0) return;
  if (typeof bondList3D === "undefined" || typeof Jmol === "undefined") return;
  const wantH = !!includeH && typeof allAtomsTypeList3D !== "undefined";
  let script = "";
  for (let b = 0; b < bondList3D.length; b++) {
    if (!bondList3D[b]) continue;
    const in1 = fragAtoms.indexOf(bondList3D[b][0]) >= 0;
    const in2 = fragAtoms.indexOf(bondList3D[b][1]) >= 0;
    const hBond = wantH && ((in1 && allAtomsTypeList3D[bondList3D[b][1] - 1] === "H") ||
      (in2 && allAtomsTypeList3D[bondList3D[b][0] - 1] === "H"));
    if ((in1 && in2) || hBond) {
      script += "select atomno=" + bondList3D[b][0] + ", atomno=" + bondList3D[b][1] + "; color bond [XD8EEDC];";
    }
  }
  if (script) {
    try {
      fJSmolScript(jmolAppletNomeclature, script);
    } catch (e) {
      /* 3D unavailable */
    }
  }
}

// ── fHighlightFG ──────────────────────────────────────────────────────────

function fHighlightFG(FGno) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  // Algorithmic: reads functionalGroupObj computed by fDetectMolType.
  // No static nameExamples.functionalGroup* data used.
  if (nameAnalysisMode == "none") {
    return;
  }

  const fgKeys = Object.keys(functionalGroupObj).filter(function (k) {
    return k !== "hydrocarbon";
  });
  const branch = fGetHydrocarbonBranchHighlight(fHydrocarbonBranchSlot());
  const allowBranchFallback = [
    "compNumber1",
    "compNumber2",
    "compSecondSub1",
    "compSecondSub2",
    "compAcidNumber3",
    "compAcidSub3",
  ].includes(nameAnalysisMode) || /^compBranch(Sub|Loc)\d+$/.test(nameAnalysisMode || "");

  if (fgKeys.length === 0 || (allowBranchFallback &&
      (fSupportsAlkylBranchPrefixes() || fEtherPrefixGroups().length > 0) && branch.atoms.length > 0)) {
    if (!allowBranchFallback || branch.atoms.length === 0) {
      return;
    }

    let highAtomsFGArg = "";
    for (let i = 0; i < branch.atoms.length; i++) {
      highAtomsFGArg += branch.atoms[i] + ",9";
      if (i < branch.atoms.length - 1) {
        highAtomsFGArg += ",";
      }
    }
    jsmeNomeclatureApplet.setAtomBackgroundColors(0, highAtomsFGArg);

    let highBondsArg = "";
    for (let i = 0; i < branch.bonds.length; i++) {
      highBondsArg += branch.bonds[i] + ",9";
      if (i < branch.bonds.length - 1) {
        highBondsArg += ",";
      }
    }
    if (highBondsArg) {
      jsmeNomeclatureApplet.setBondBackgroundColors(0, highBondsArg);
    }
    fUpdateSVG();
    return;
  }

  // Build flat [fgKey, heteroEl] instances — one per distinct element type per FG key.
  // This lets FGno index correctly across multi-element FG types (e.g. halogen: {Br, Cl}).
  let fgInstances = [];
  for (let k = 0; k < fgKeys.length; k++) {
    const heteroEls = Object.keys(functionalGroupObj[fgKeys[k]]);
    for (let e = 0; e < heteroEls.length; e++) {
      fgInstances.push([fgKeys[k], heteroEls[e]]);
    }
  }
  // Sort: lower-priority FGs first, matching functionalGroupsList order (FGno=1 = first prefix).
  const fgPriorityOrder2D = [
    "carboxylicAcid",
    "ester",
    "cyanide",
    "aldehyde",
    "ketone",
    "alcohol",
    "amine",
    "nitro",
    "ether",
  ];
  const halogenOrder2D = Object.keys(nameMainCompObj3.halogen.substitute);
  fgInstances.sort(function (a, b) {
    if (a[0] === "halogen" && b[0] === "halogen") {
      return halogenOrder2D.indexOf(a[1]) - halogenOrder2D.indexOf(b[1]);
    }
    return fgPriorityOrder2D.indexOf(b[0]) - fgPriorityOrder2D.indexOf(a[0]);
  });

  let targetInstances = [];
  if (FGno === undefined) {
    targetInstances = fgInstances;
  } else {
    if (fgInstances[FGno - 1]) {
      targetInstances = [fgInstances[FGno - 1]];
    }
  }

  // If the selected component is a carbon side branch rather than a real functional group,
  // highlight the branch atoms even when other functional groups are present.
  if (
    allowBranchFallback &&
    branch.atoms.length > 0 &&
    targetInstances.length === 0
  ) {
    let highAtomsFGArg = "";
    for (let i = 0; i < branch.atoms.length; i++) {
      highAtomsFGArg += branch.atoms[i] + ",9";
      if (i < branch.atoms.length - 1) {
        highAtomsFGArg += ",";
      }
    }
    jsmeNomeclatureApplet.setAtomBackgroundColors(0, highAtomsFGArg);

    let highBondsArg = "";
    for (let i = 0; i < branch.bonds.length; i++) {
      highBondsArg += branch.bonds[i] + ",9";
      if (i < branch.bonds.length - 1) {
        highBondsArg += ",";
      }
    }
    if (highBondsArg) {
      jsmeNomeclatureApplet.setBondBackgroundColors(0, highBondsArg);
    }
    fUpdateSVG();
    return;
  }

  let highAtomsFG = [];

  for (let t = 0; t < targetInstances.length; t++) {
    const fgKey = targetInstances[t][0];
    const heteroEl = targetInstances[t][1];
    const heteroList = functionalGroupObj[fgKey][heteroEl]; // 0-based atom indices

    for (let i = 0; i < heteroList.length; i++) {
      const entry = heteroList[i];
      if (Array.isArray(entry)) {
        if (fgKey === "ester") {
          // Ester pair [oDouble, oSingle]: highlight triad O-C(=O)-O in every mode.
          const _esTriad = fGetEsterTriad() || [];
          for (let _ei = 0; _ei < _esTriad.length; _ei++) {
            if (!highAtomsFG.includes(_esTriad[_ei])) {
              highAtomsFG.push(_esTriad[_ei]);
            }
          }
          continue;
        }
        // carboxylicAcid: entry = [oh_idx, co_idx] both 0-based
        const ohIdx = entry[0],
          coIdx = entry[1];
        if (mode2D === "condensed") {
          if (Array.isArray(atomConnectivityList[ohIdx])) {
            const sharedC = atomConnectivityList[ohIdx][0];
            if (!highAtomsFG.includes(sharedC + 1)) {
              highAtomsFG.push(sharedC + 1);
            }
          }
          continue;
        }
        if (!highAtomsFG.includes(ohIdx + 1)) {
          highAtomsFG.push(ohIdx + 1);
        }
        if (!highAtomsFG.includes(coIdx + 1)) {
          highAtomsFG.push(coIdx + 1);
        }
        if (Array.isArray(atomConnectivityList[ohIdx])) {
          const sharedC = atomConnectivityList[ohIdx][0];
          if (!highAtomsFG.includes(sharedC + 1)) {
            highAtomsFG.push(sharedC + 1);
          }
        }
        // H on the -OH oxygen (present in expanded mode)
        for (let b = 0; b < bondList.length; b++) {
          if (!bondList[b]) {
            continue;
          }
          const ba1 = bondList[b][0],
            ba2 = bondList[b][1];
          let hIdx = -1;
          if (ba1 === ohIdx + 1 && allAtomsTypeList[ba2 - 1] === "H") {
            hIdx = ba2;
          } else if (ba2 === ohIdx + 1 && allAtomsTypeList[ba1 - 1] === "H") {
            hIdx = ba1;
          }
          if (hIdx !== -1 && !highAtomsFG.includes(hIdx)) {
            highAtomsFG.push(hIdx);
          }
        }
      } else {
        const heteroIdx = entry; // 0-based
        if (fgKey === "alcohol" || fgKey === "amine") {
          if (!highAtomsFG.includes(heteroIdx + 1)) {
            highAtomsFG.push(heteroIdx + 1);
          }
          // highlight H atoms bonded to the heteroatom (present in expanded mode)
          for (let b = 0; b < bondList.length; b++) {
            if (!bondList[b]) {
              continue;
            }
            const ba1 = bondList[b][0],
              ba2 = bondList[b][1];
            let hIdx = -1;
            if (ba1 === heteroIdx + 1 && allAtomsTypeList[ba2 - 1] === "H") {
              hIdx = ba2;
            } else if (
              ba2 === heteroIdx + 1 &&
              allAtomsTypeList[ba1 - 1] === "H"
            ) {
              hIdx = ba1;
            }
            if (hIdx !== -1 && !highAtomsFG.includes(hIdx)) {
              highAtomsFG.push(hIdx);
            }
          }
        } else if (fgKey === "aldehyde") {
          // O + carbonyl C + aldehyde H on carbonyl C
          if (
            Array.isArray(atomConnectivityList[heteroIdx]) &&
            atomConnectivityList[heteroIdx].length > 0
          ) {
            const carbonylC = atomConnectivityList[heteroIdx][0]; // 0-based
            if (mode2D === "condensed") {
              if (!highAtomsFG.includes(carbonylC + 1)) {
                highAtomsFG.push(carbonylC + 1);
              }
              continue;
            }
            if (!highAtomsFG.includes(heteroIdx + 1)) {
              highAtomsFG.push(heteroIdx + 1);
            }
            if (!highAtomsFG.includes(carbonylC + 1)) {
              highAtomsFG.push(carbonylC + 1);
            }
            for (let b = 0; b < bondList.length; b++) {
              if (!bondList[b]) {
                continue;
              }
              const ba1 = bondList[b][0],
                ba2 = bondList[b][1];
              let hIdx = -1;
              if (ba1 === carbonylC + 1 && allAtomsTypeList[ba2 - 1] === "H") {
                hIdx = ba2;
              } else if (
                ba2 === carbonylC + 1 &&
                allAtomsTypeList[ba1 - 1] === "H"
              ) {
                hIdx = ba1;
              }
              if (hIdx !== -1 && !highAtomsFG.includes(hIdx)) {
                highAtomsFG.push(hIdx);
              }
            }
          }
        } else if (fgKey === "ketone") {
          // O + carbonyl C + C-neighbors of carbonyl C
          if (!highAtomsFG.includes(heteroIdx + 1)) {
            highAtomsFG.push(heteroIdx + 1);
          }
          if (
            Array.isArray(atomConnectivityList[heteroIdx]) &&
            atomConnectivityList[heteroIdx].length > 0
          ) {
            const carbonylC = atomConnectivityList[heteroIdx][0]; // 0-based
            if (!highAtomsFG.includes(carbonylC + 1)) {
              highAtomsFG.push(carbonylC + 1);
            }
            if (Array.isArray(atomConnectivityList[carbonylC])) {
              for (let n = 0; n < atomConnectivityList[carbonylC].length; n++) {
                const neighbor = atomConnectivityList[carbonylC][n]; // 0-based
                if (
                  allAtomsTypeList[neighbor] === "C" &&
                  !highAtomsFG.includes(neighbor + 1)
                ) {
                  highAtomsFG.push(neighbor + 1);
                }
              }
            }
          }
        } else if (fgKey === "halogen") {
          // halogen atom only — no carbon neighbor
          if (!highAtomsFG.includes(heteroIdx + 1)) {
            highAtomsFG.push(heteroIdx + 1);
          }
        } else if (fgKey === "cyanide") {
          if (
            Array.isArray(atomConnectivityList[heteroIdx]) &&
            atomConnectivityList[heteroIdx].length > 0
          ) {
            const cyanideAnchorC = atomConnectivityList[heteroIdx][0];
            if (mode2D === "condensed") {
              if (!highAtomsFG.includes(cyanideAnchorC + 1)) {
                highAtomsFG.push(cyanideAnchorC + 1);
              }
              continue;
            }
          }
          if (!highAtomsFG.includes(heteroIdx + 1)) {
            highAtomsFG.push(heteroIdx + 1);
          }
          if (Array.isArray(atomConnectivityList[heteroIdx])) {
            for (let n = 0; n < atomConnectivityList[heteroIdx].length; n++) {
              const neighbor = atomConnectivityList[heteroIdx][n] + 1; // to 1-based
              if (!highAtomsFG.includes(neighbor)) {
                highAtomsFG.push(neighbor);
              }
            }
          }
        } else if (fgKey === "nitro") {
          // N + bonded O atoms only, no carbon
          if (mode2D === "condensed") {
            if (!highAtomsFG.includes(heteroIdx + 1)) {
              highAtomsFG.push(heteroIdx + 1);
            }
            continue;
          }
          if (!highAtomsFG.includes(heteroIdx + 1)) {
            highAtomsFG.push(heteroIdx + 1);
          }
          if (Array.isArray(atomConnectivityList[heteroIdx])) {
            for (let n = 0; n < atomConnectivityList[heteroIdx].length; n++) {
              const neighbor = atomConnectivityList[heteroIdx][n]; // 0-based
              if (
                allAtomsTypeList[neighbor] === "O" &&
                !highAtomsFG.includes(neighbor + 1)
              ) {
                highAtomsFG.push(neighbor + 1);
              }
            }
          }
        } else if (fgKey === "ether") {
          // Ether R-O-R': whole (FGno undefined, suffix click) -> O + both Cs (C-O-C).
          // Prefix click (FGno defined, e.g. alkoxy) -> O + full alkoxy fragment (C-O for methoxy).
          if (!highAtomsFG.includes(heteroIdx + 1)) {
            highAtomsFG.push(heteroIdx + 1);
          }
          const _ethNbrs = Array.isArray(atomConnectivityList[heteroIdx])
            ? atomConnectivityList[heteroIdx].filter(function (n) {
                return allAtomsTypeList[n] === "C";
              })
            : [];
          let _ethTargets = _ethNbrs;
          if (FGno !== undefined) {
            const _alkChain = fGetEtherAlkoxyChain();
            if (_alkChain && _alkChain.length > 0) {
              _ethTargets = _alkChain.map(function (a) { return a - 1; });
            } else {
              const _alk = fGetEtherAlkoxyC();
              if (_alk !== null && _alk !== undefined) _ethTargets = [_alk];
              else if (_ethNbrs.length > 1) _ethTargets = [_ethNbrs[1]];
            }
          }
          for (let _en = 0; _en < _ethTargets.length; _en++) {
            if (!highAtomsFG.includes(_ethTargets[_en] + 1)) {
              highAtomsFG.push(_ethTargets[_en] + 1);
            }
          }
          // Alkyl rule (prefix clicks only): attached H join the highlight.
          // The whole C-O-C group (suffix/αιθέρας click, FGno undefined)
          // stays H-free by design. Expanded mode has explicit H;
          // condensed/skeletal models carry none, so this is a no-op there.
          // The both-ends bond derivation below then picks up the C–H bonds
          // automatically.
          if (FGno !== undefined) {
            for (let _en = 0; _en < _ethTargets.length; _en++) {
              const _c1 = _ethTargets[_en] + 1;
              for (let _b = 0; _b < bondList.length; _b++) {
                if (!bondList[_b]) continue;
                const _ba1 = bondList[_b][0];
                const _ba2 = bondList[_b][1];
                if (_ba1 === _c1 && allAtomsTypeList[_ba2 - 1] === "H") {
                  if (!highAtomsFG.includes(_ba2)) highAtomsFG.push(_ba2);
                } else if (_ba2 === _c1 && allAtomsTypeList[_ba1 - 1] === "H") {
                  if (!highAtomsFG.includes(_ba1)) highAtomsFG.push(_ba1);
                }
              }
            }
          }
        } else {
          // cyanide, imine, CCamine, etc.
          if (!highAtomsFG.includes(heteroIdx + 1)) {
            highAtomsFG.push(heteroIdx + 1);
          }
          if (Array.isArray(atomConnectivityList[heteroIdx])) {
            for (let n = 0; n < atomConnectivityList[heteroIdx].length; n++) {
              const neighbor = atomConnectivityList[heteroIdx][n] + 1; // to 1-based
              if (!highAtomsFG.includes(neighbor)) {
                highAtomsFG.push(neighbor);
              }
            }
          }
        }
      }
    }
  }

  if (highAtomsFG.length === 0) {
    return;
  }

  let highAtomsFGArg = "";
  for (let i = 0; i < highAtomsFG.length; i++) {
    highAtomsFGArg += highAtomsFG[i] + ",9";
    if (i < highAtomsFG.length - 1) {
      highAtomsFGArg += ",";
    }
  }
  jsmeNomeclatureApplet.setAtomBackgroundColors(0, highAtomsFGArg);

  // Derive highlighted bonds: any bond with both endpoints highlighted
  let highBondsFG = [];
  for (let b = 0; b < bondList.length; b++) {
    if (!bondList[b]) {
      continue;
    }
    if (
      highAtomsFG.includes(bondList[b][0]) &&
      highAtomsFG.includes(bondList[b][1])
    ) {
      highBondsFG.push(b + 1);
    }
  }

  if (highBondsFG.length === 0) {
    fUpdateSVG();
    return;
  }

  let highBondsArg = "";
  for (let i = 0; i < highBondsFG.length; i++) {
    highBondsArg += highBondsFG[i] + ",9";
    if (i < highBondsFG.length - 1) {
      highBondsArg += ",";
    }
  }
  jsmeNomeclatureApplet.setBondBackgroundColors(0, highBondsArg);
  fUpdateSVG();
}

// ── fHighlightFG3D ────────────────────────────────────────────────────────

function fHighlightFG3D(FGno) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  // Build atom list from computed functionalGroupObj3D (SDF 1-based indices).
  // FGno undefined  → all FG atoms (for suffix / single-FG display)
  // FGno 1 or 2     → atoms for the Nth functional group (for prefix position display)

  const fgKeys = Object.keys(functionalGroupObj3D).filter(function (k) {
    return k !== "hydrocarbon";
  });
  const branch = fGetHydrocarbonBranchHighlight3D(fHydrocarbonBranchSlot());
  const allowBranchFallback = [
    "compNumber1",
    "compNumber2",
    "compSecondSub1",
    "compSecondSub2",
    "compAcidNumber3",
    "compAcidSub3",
  ].includes(nameAnalysisMode) || /^compBranch(Sub|Loc)\d+$/.test(nameAnalysisMode || "");

  let highAtoms3D = [];

  if (fgKeys.length === 0 || (allowBranchFallback &&
      (fSupportsAlkylBranchPrefixes() || fEtherPrefixGroups().length > 0) && branch.atoms.length > 0)) {
    if (!allowBranchFallback || branch.atoms.length === 0) {
      // pure hydrocarbon or no branch match — clear any existing highlight
      fJSmolScript(
        jmolAppletNomeclature,
        "select all; selectionHalos off; color atoms none; color bonds none;",
      );
      return;
    }
    highAtoms3D = branch.atoms;
    let highAtoms3DArg = "select";
    for (let i = 0; i < highAtoms3D.length; i++) {
      highAtoms3DArg += " atomno=" + highAtoms3D[i];
      if (i < highAtoms3D.length - 1) {
        highAtoms3DArg += ",";
      }
    }
    highAtoms3DArg += "; select connected(selected) and _H or selected;";
    fJSmolScript(
      jmolAppletNomeclature,
      "select all; selectionHalos off; color atoms none; color bonds none;" +
        highAtoms3DArg +
        ";color selectionHalos[XD8EEDC]; selectionHalos on; color atoms [XD8EEDC];",
    );
    JmolSelection = highAtoms3DArg;
  } else {
    // Build flat [fgKey, heteroEl] instances — one per distinct element type per FG key.
    let fgInstances = [];
    for (let k = 0; k < fgKeys.length; k++) {
      const heteroEls = Object.keys(functionalGroupObj3D[fgKeys[k]]);
      for (let e = 0; e < heteroEls.length; e++) {
        fgInstances.push([fgKeys[k], heteroEls[e]]);
      }
    }

    // Sort: lower-priority FGs first, matching functionalGroupsList order (FGno=1 = first prefix).
    const fgPriorityOrder3D = [
      "carboxylicAcid",
      "ester",
      "cyanide",
      "aldehyde",
      "ketone",
      "alcohol",
      "amine",
      "nitro",
      "ether",
    ];
    // Stash for the IUPAC alkoxy-prefix bond post-pass (O + alkoxy chain,
    // 1-based): the halo script below colors atoms only.
    let _ethAlkoxyFrag3D = null;
    const halogenOrder3D = Object.keys(nameMainCompObj3.halogen.substitute);
    fgInstances.sort(function (a, b) {
      if (a[0] === "halogen" && b[0] === "halogen") {
        return halogenOrder3D.indexOf(a[1]) - halogenOrder3D.indexOf(b[1]);
      }
      return fgPriorityOrder3D.indexOf(b[0]) - fgPriorityOrder3D.indexOf(a[0]);
    });

    let targetInstances = [];
    if (FGno === undefined) {
      targetInstances = fgInstances;
    } else {
      if (fgInstances[FGno - 1]) {
        targetInstances = [fgInstances[FGno - 1]];
      }
    }

    // If the selected component is a carbon side branch rather than a real functional group,
    // highlight the branch atoms even when other functional groups are present.
    if (
      allowBranchFallback &&
      branch.atoms.length > 0 &&
      targetInstances.length === 0
    ) {
      highAtoms3D = branch.atoms;
      let highAtoms3DArg = "select";
      for (let i = 0; i < highAtoms3D.length; i++) {
        highAtoms3DArg += " atomno=" + highAtoms3D[i];
        if (i < highAtoms3D.length - 1) {
          highAtoms3DArg += ",";
        }
      }
      highAtoms3DArg += "; select connected(selected) and _H or selected;";
      fJSmolScript(
        jmolAppletNomeclature,
        "select all; selectionHalos off; color atoms none; color bonds none;" +
          highAtoms3DArg +
          ";color selectionHalos[XD8EEDC]; selectionHalos on; color atoms [XD8EEDC];",
      );
      JmolSelection = highAtoms3DArg;
      return;
    }

    for (let t = 0; t < targetInstances.length; t++) {
      const fgKey = targetInstances[t][0];
      const heteroEl = targetInstances[t][1];
      const heteroList = functionalGroupObj3D[fgKey][heteroEl]; // array of 0-based indices

      for (let i = 0; i < heteroList.length; i++) {
        const entry = heteroList[i];
        if (Array.isArray(entry)) {
          // carboxylicAcid: [oh_idx, co_idx] both 0-based
          const ohIdx = entry[0],
            coIdx = entry[1];
          highAtoms3D.push(ohIdx + 1); // to 1-based
          highAtoms3D.push(coIdx + 1);
          // also include the shared C
          if (Array.isArray(atomConnectivityList3D[ohIdx])) {
            const sharedC = atomConnectivityList3D[ohIdx][0];
            if (!highAtoms3D.includes(sharedC + 1)) {
              highAtoms3D.push(sharedC + 1);
            }
          }
          // H on the -OH oxygen
          for (let b = 0; b < bondList3D.length; b++) {
            if (!bondList3D[b]) {
              continue;
            }
            const ba1 = bondList3D[b][0],
              ba2 = bondList3D[b][1];
            let hIdx = -1;
            if (ba1 === ohIdx + 1 && allAtomsTypeList3D[ba2 - 1] === "H") {
              hIdx = ba2;
            } else if (
              ba2 === ohIdx + 1 &&
              allAtomsTypeList3D[ba1 - 1] === "H"
            ) {
              hIdx = ba1;
            }
            if (hIdx !== -1 && !highAtoms3D.includes(hIdx)) {
              highAtoms3D.push(hIdx);
            }
          }
        } else {
          const heteroIdx = entry; // 0-based
          if (!highAtoms3D.includes(heteroIdx + 1)) {
            highAtoms3D.push(heteroIdx + 1);
          }
          if (fgKey === "alcohol" || fgKey === "amine") {
            // highlight H atoms bonded to the heteroatom
            for (let b = 0; b < bondList3D.length; b++) {
              if (!bondList3D[b]) {
                continue;
              }
              const ba1 = bondList3D[b][0],
                ba2 = bondList3D[b][1];
              let hIdx = -1;
              if (
                ba1 === heteroIdx + 1 &&
                allAtomsTypeList3D[ba2 - 1] === "H"
              ) {
                hIdx = ba2;
              } else if (
                ba2 === heteroIdx + 1 &&
                allAtomsTypeList3D[ba1 - 1] === "H"
              ) {
                hIdx = ba1;
              }
              if (hIdx !== -1 && !highAtoms3D.includes(hIdx)) {
                highAtoms3D.push(hIdx);
              }
            }
          } else if (fgKey === "aldehyde") {
            // O + carbonyl C + aldehyde H on carbonyl C
            if (
              Array.isArray(atomConnectivityList3D[heteroIdx]) &&
              atomConnectivityList3D[heteroIdx].length > 0
            ) {
              const carbonylC = atomConnectivityList3D[heteroIdx][0]; // 0-based
              if (!highAtoms3D.includes(carbonylC + 1)) {
                highAtoms3D.push(carbonylC + 1);
              }
              for (let b = 0; b < bondList3D.length; b++) {
                if (!bondList3D[b]) {
                  continue;
                }
                const ba1 = bondList3D[b][0],
                  ba2 = bondList3D[b][1];
                let hIdx = -1;
                if (
                  ba1 === carbonylC + 1 &&
                  allAtomsTypeList3D[ba2 - 1] === "H"
                ) {
                  hIdx = ba2;
                } else if (
                  ba2 === carbonylC + 1 &&
                  allAtomsTypeList3D[ba1 - 1] === "H"
                ) {
                  hIdx = ba1;
                }
                if (hIdx !== -1 && !highAtoms3D.includes(hIdx)) {
                  highAtoms3D.push(hIdx);
                }
              }
            }
          } else if (fgKey === "ketone") {
            // O + carbonyl C + C-neighbors of carbonyl C
            if (
              Array.isArray(atomConnectivityList3D[heteroIdx]) &&
              atomConnectivityList3D[heteroIdx].length > 0
            ) {
              const carbonylC = atomConnectivityList3D[heteroIdx][0]; // 0-based
              if (!highAtoms3D.includes(carbonylC + 1)) {
                highAtoms3D.push(carbonylC + 1);
              }
              if (Array.isArray(atomConnectivityList3D[carbonylC])) {
                for (
                  let n = 0;
                  n < atomConnectivityList3D[carbonylC].length;
                  n++
                ) {
                  const neighbor = atomConnectivityList3D[carbonylC][n]; // 0-based
                  if (
                    allAtomsTypeList3D[neighbor] === "C" &&
                    !highAtoms3D.includes(neighbor + 1)
                  ) {
                    highAtoms3D.push(neighbor + 1);
                  }
                }
              }
            }
          } else if (fgKey === "halogen") {
            // halogen atom only — no carbon neighbor
          } else if (fgKey === "nitro") {
            // N + bonded O atoms only, no carbon
            if (Array.isArray(atomConnectivityList3D[heteroIdx])) {
              for (
                let n = 0;
                n < atomConnectivityList3D[heteroIdx].length;
                n++
              ) {
                const neighbor = atomConnectivityList3D[heteroIdx][n]; // 0-based
                if (
                  allAtomsTypeList3D[neighbor] === "O" &&
                  !highAtoms3D.includes(neighbor + 1)
                ) {
                  highAtoms3D.push(neighbor + 1);
                }
              }
            }
          } else if (fgKey === "ether") {
            // Ether R-O-R': whole (FGno undefined) -> O + both Cs (C–O–C bonds
            // are colored by the commonEther case); prefix -> O + full alkoxy
            // chain, mirroring the 2D branch (fGetEtherAlkoxyChain).
            if (Array.isArray(atomConnectivityList3D[heteroIdx])) {
              let _eth3Targets = atomConnectivityList3D[heteroIdx].filter(function (n) {
                return allAtomsTypeList3D[n] === "C";
              });
              if (FGno !== undefined) {
                const _alkChain3D = fGetEtherAlkoxyChain3D();
                if (_alkChain3D && _alkChain3D.length > 0) {
                  _eth3Targets = _alkChain3D.map(function (a) { return a - 1; });
                } else {
                  const _alk3 = fGetEtherAlkoxyC3D();
                  if (_alk3 !== null && _alk3 !== undefined) _eth3Targets = [_alk3];
                  else if (_eth3Targets.length > 1) _eth3Targets = [_eth3Targets[1]];
                }
                // stash O + alkoxy chain (1-based) for the bond post-pass below
                _ethAlkoxyFrag3D = [heteroIdx + 1].concat(_eth3Targets.map(function (c) { return c + 1; }));
              }
              for (let n = 0; n < _eth3Targets.length; n++) {
                const neighbor = _eth3Targets[n] + 1;
                if (!highAtoms3D.includes(neighbor)) {
                  highAtoms3D.push(neighbor);
                }
              }
              // Alkyl rule (prefix clicks only: FGno defined): halo H attached
              // to the highlighted carbons. The whole C-O-C group (suffix /
              // αιθέρας click, FGno undefined) stays H-free by design. The FG
              // halo script has no connected-H extension (unlike the chain
              // path), so add them explicitly here.
              if (FGno !== undefined && typeof bondList3D !== "undefined" && typeof allAtomsTypeList3D !== "undefined") {
                for (let _h = 0; _h < _eth3Targets.length; _h++) {
                  const _c1 = _eth3Targets[_h] + 1;
                  for (let _b = 0; _b < bondList3D.length; _b++) {
                    if (!bondList3D[_b]) continue;
                    const _ba1 = bondList3D[_b][0];
                    const _ba2 = bondList3D[_b][1];
                    if (_ba1 === _c1 && allAtomsTypeList3D[_ba2 - 1] === "H") {
                      if (!highAtoms3D.includes(_ba2)) highAtoms3D.push(_ba2);
                    } else if (_ba2 === _c1 && allAtomsTypeList3D[_ba1 - 1] === "H") {
                      if (!highAtoms3D.includes(_ba1)) highAtoms3D.push(_ba1);
                    }
                  }
                }
              }
            }
          } else {
            // cyanide, imine, CCamine, etc.
            if (Array.isArray(atomConnectivityList3D[heteroIdx])) {
              for (
                let n = 0;
                n < atomConnectivityList3D[heteroIdx].length;
                n++
              ) {
                const neighbor = atomConnectivityList3D[heteroIdx][n] + 1;
                if (!highAtoms3D.includes(neighbor)) {
                  highAtoms3D.push(neighbor);
                }
              }
            }
          }
        }
      }
    }

    if (highAtoms3D.length === 0) {
      fJSmolScript(
        jmolAppletNomeclature,
        "select all; selectionHalos off; color atoms none; color bonds none;",
      );
      return;
    }

    let highAtoms3DArg = "select";
    for (let i = 0; i < highAtoms3D.length; i++) {
      highAtoms3DArg += " atomno=" + highAtoms3D[i];
      if (i < highAtoms3D.length - 1) {
        highAtoms3DArg += ",";
      }
    }

    // Merged into one script (vs. relying on the earlier fClearHighlights() call) to avoid a Jmol script-queue race.
    fJSmolScript(
      jmolAppletNomeclature,
      "select all; selectionHalos off; color atoms none; color bonds none;" +
        highAtoms3DArg +
        ";color selectionHalos[XD8EEDC]; selectionHalos on; color atoms [XD8EEDC];",
    );
    JmolSelection = highAtoms3DArg;
    // IUPAC alkoxy prefix: the halo script colors atoms only — color the
    // O–C + C–C + C–H bonds of the stashed O + alkoxy chain explicitly (green).
    if (_ethAlkoxyFrag3D) fColorFragmentBonds3D(_ethAlkoxyFrag3D, true);
  }
}

// Per-component numbering override (ethers): when set, fShowNumbering numbers
// the override atom list instead of the parent main chain. Cleared on next
// plain fShowNumbering(time) call and in fClearHighlights.
let numberingAtomOverride = null;
let numberingAtomOverride3D = null;

// A display-only comparison of equivalent directions of one parent. The core
// signature omits some chemical metadata, so accept only a plain, connected
// saturated C/H tree whose parsed graph is exactly the live numbering graph.
function fEquivalentParentNumberingDirections(molText, chain, types, bonds) {
  try {
    const m = fParseMolV2000(molText);
    if (!m || !Array.isArray(chain) || chain.length < 2 ||
        !Array.isArray(types) || !Array.isArray(bonds) ||
        m.atoms.length !== types.length || m.bonds.length !== types.length - 1 ||
        m.properties.length || !fMolCanTransform2D(m, false)) return null;
    if (m.atoms.some((a, i) => !["C", "H"].includes(a.el) || a.el !== types[i] ||
        a.charge !== 0 || a.massDifference !== 0 || (a.isotope != null && a.isotope !== 0) ||
        a.tail.trim().split(/\s+/).some(v => !/^[+-]?\d+$/.test(v) || Number(v) !== 0))) return null;
    const key = b => {
      if (!Array.isArray(b) || !Number.isInteger(b[0]) || !Number.isInteger(b[1]) ||
          b[0] < 1 || b[1] < 1 || b[0] > types.length || b[1] > types.length ||
          b[0] === b[1] || b[2] !== 1) throw new Error("Unsupported numbering graph");
      return [Math.min(b[0], b[1]), Math.max(b[0], b[1]), b[2]].join(":");
    };
    if (m.bonds.some(b => b.tail.trim().split(/\s+/).some(v => !/^[+-]?\d+$/.test(v) || Number(v) !== 0)) ||
        JSON.stringify(m.bonds.map(key).sort()) !== JSON.stringify(bonds.map(key).sort())) return null;
    const adj = types.map(() => []);
    bonds.forEach(([a, b]) => { adj[a - 1].push(b - 1); adj[b - 1].push(a - 1); });
    if (adj.some((ns, i) => types[i] === "H" ? ns.length !== 1 : ns.length > 4)) return null;
    const seen = new Set([0]), queue = [0];
    for (let i = 0; i < queue.length; i++) adj[queue[i]].forEach(n => {
      if (!seen.has(n)) { seen.add(n); queue.push(n); }
    });
    if (seen.size !== types.length || new Set(chain).size !== chain.length ||
        chain.some(n => !Number.isInteger(n) || types[n - 1] !== "C")) return null;
    const reverse = chain.slice().reverse();
    const signature = fNumberedChainSignature(chain, types, bonds);
    if (signature === null || signature !== fNumberedChainSignature(reverse, types, bonds)) return null;
    const dx = m.atoms[chain[chain.length - 1] - 1].x - m.atoms[chain[0] - 1].x;
    if (Math.abs(dx) < 1e-6) return null; // no unambiguous left/right endpoints
    return { left: (dx > 0 ? chain : reverse).slice(), right: (dx > 0 ? reverse : chain).slice() };
  } catch (e) { return null; }
}

// Locant emphasis (visual): when a locant/position component is clicked, its
// number(s) stay blue while the rest dim to gray — 2D fill + 3D echo.
// Only for main-chain numbering modes whose box digits ARE display indices
// (locant value v = label = index v-1, chains stored in numbering order).
// Override-chain and whole-chain modes return null (all blue, as today).
// Parse failures also return null, so the safe default is today's rendering.
let numberingEmphasis = null;
function fLocantEmphasisIndices() {
  try {
    var mode = (typeof nameAnalysisMode !== "undefined") ? nameAnalysisMode : "none";
    var ok = mode === "compBondPos" || mode === "compEndNumber" ||
      mode === "compSuffixLocants" || mode === "compNumber1" || mode === "compNumber2" ||
      /^compBranchLoc\d+$/.test(mode);
    if (!ok) return null;
    var box = null;
    try { box = document.querySelector("#nameAnalysis .nameCompBox.selected"); } catch (eB) { box = null; }
    if (!box) return null;
    var text = "";
    try { text = box.textContent || ""; } catch (eT) { text = ""; }
    var found = text.match(/\d+/g);
    if (!found || !found.length) return null;
    var idx = [];
    for (var k = 0; k < found.length; k++) {
      var v = parseInt(found[k], 10);
      if (v >= 1 && idx.indexOf(v - 1) < 0) idx.push(v - 1);
    }
    return idx.length ? idx : null;
  } catch (e) { return null; }
}

// ── fShowNumbering ────────────────────────────────────────────────────────

function fShowNumbering(time, overrideAtoms, overrideAtoms3D) {
  let numberOffset, currAtomTextElement, x, y, r, numberString;
  if (!numberingFlag) {
    return;
  }
  // Resolve on every repaint, including zoom/resize. Explicit component
  // overrides retain priority. This lesson feature is restricted to 2D.
  if (!Array.isArray(overrideAtoms) && !Array.isArray(overrideAtoms3D) &&
      typeof fScenarioNumberingDirectionAtoms === "function") {
    const directionAtoms = fScenarioNumberingDirectionAtoms();
    if (directionAtoms) { overrideAtoms = directionAtoms; overrideAtoms3D = []; }
  }
  numberingAtomOverride = Array.isArray(overrideAtoms) ? overrideAtoms : null;
  numberingAtomOverride3D = Array.isArray(overrideAtoms3D) ? overrideAtoms3D : null;
  // Locant emphasis is recomputed on every numbering render (click, rebuild,
  // scenario replay), so it always matches the live selection; null = all blue.
  numberingEmphasis = fLocantEmphasisIndices();
  clearInterval(myNumberingTimeout);
  numbersSVGElements = [];

  molSvg = MuSVG("#jsmeNomeclatureSVG svg");
  switch (mode2D) {
    case "condensed":
      highAtoms =
        Array.isArray(numberingAtomOverride)
          ? numberingAtomOverride
          : mainChainAtomsList;
      highAtoms = (Array.isArray(highAtoms) ? highAtoms : []).filter(
        function (atomNo) {
          return allAtomsTypeList[atomNo - 1] === "C";
        },
      );
      const condensedAtomTextMap = fGetRenderedAtomTextMap();
      numberOffset = [20, -280];
      for (let i = 0; i < highAtoms.length; i++) {
        currAtomTextElement = condensedAtomTextMap[highAtoms[i] - 1];
        if (!currAtomTextElement) {
          continue;
        }
        const compactLabelKey = compactNumberingLabelMap[highAtoms[i] - 1];
        x = compactLabelKey
          ? fGetCompactLabelNumberX(
              currAtomTextElement,
              compactLabelKey,
              numberOffset[0],
            )
          : parseInt(currAtomTextElement.attr("x")) + numberOffset[0];
        y = parseInt(currAtomTextElement.attr("y")) + +numberOffset[1];
        r = 220;
        numberString = `  <text id='number${i}' x='${x}' y='${y}' font-size='270px' font-weight='600' font-family='Arial, sans-serif' fill='${(numberingEmphasis === null || numberingEmphasis.indexOf(i) >= 0) ? "#193F8F" : "#9ac1ed"}' stroke='white' stroke-width='30px' paint-order='stroke'>${i + 1}</text> `;
        numbersSVGElements[i] = numberString;
      }
      break;
    case "condensedZigZag":
      highAtoms =
        Array.isArray(numberingAtomOverride)
          ? numberingAtomOverride
          : mainChainAtomsList;
      highAtoms = (Array.isArray(highAtoms) ? highAtoms : []).filter(
        function (atomNo) {
          return allAtomsTypeList[atomNo - 1] === "C";
        },
      );
      const condensedZigZagAtomTextMap = fGetRenderedAtomTextMap();
      numberOffset = [20, -280];
      for (let i = 0; i < highAtoms.length; i++) {
        currAtomTextElement = condensedZigZagAtomTextMap[highAtoms[i] - 1];
        if (!currAtomTextElement) {
          continue;
        }
        x = parseInt(currAtomTextElement.attr("x")) + numberOffset[0];
        y = parseInt(currAtomTextElement.attr("y")) + +numberOffset[1];
        r = 220;
        numberString = `  <text id='number${i}' x='${x}' y='${y}' font-size='270px' font-weight='600' font-family='Arial, sans-serif' fill='${(numberingEmphasis === null || numberingEmphasis.indexOf(i) >= 0) ? "#193F8F" : "#9ac1ed"}' stroke='white' stroke-width='30px' paint-order='stroke'>${i + 1}</text> `;
        numbersSVGElements[i] = numberString;
      }
      break;
    case "expanded":
      highAtoms =
        Array.isArray(numberingAtomOverride)
          ? numberingAtomOverride
          : mainChainAtomsList;
      highAtoms = (Array.isArray(highAtoms) ? highAtoms : []).filter(
        function (atomNo) {
          return allAtomsTypeList[atomNo - 1] === "C";
        },
      );
      const expandedAtomTextMap = fGetRenderedAtomTextMap(false, true);
      const fixedCCNumberScale = Number(molSvg.node.dataset.alkaneFixedCCScale) || 1;
      numberOffset = [(molSvg.node.dataset.alkaneFixedCCScale ? -230 : -120) * fixedCCNumberScale,
        -280 * fixedCCNumberScale];
      for (let i = 0; i < highAtoms.length; i++) {
        currAtomTextElement = expandedAtomTextMap[highAtoms[i] - 1];
        if (!currAtomTextElement) {
          continue;
        }
        x = parseInt(currAtomTextElement.attr("x")) + numberOffset[0];
        y = parseInt(currAtomTextElement.attr("y")) + +numberOffset[1];
        r = 220;
        numberString = `  <text id='number${i}' x='${x}' y='${y}' font-size='${270 * fixedCCNumberScale}px' font-weight='600' font-family='Arial, sans-serif' fill='${(numberingEmphasis === null || numberingEmphasis.indexOf(i) >= 0) ? "#193F8F" : "#9ac1ed"}' stroke='white' stroke-width='${30 * fixedCCNumberScale}px' paint-order='stroke'>${i + 1}</text> `;
        numbersSVGElements[i] = numberString;
      }
      break;

    case "skeletal":
      highAtoms = Array.isArray(numberingAtomOverride)
        ? numberingAtomOverride : mainChainAtomsList;
      highAtoms = (Array.isArray(highAtoms) ? highAtoms : []).filter(
        function (atomNo) {
          return allAtomsTypeList[atomNo - 1] === "C";
        },
      );
      numberOffset = [-50, -180];
      for (let i = 0; i < highAtoms.length; i++) {
        let _foundBond = false;
        for (let b = 0; b < bondList.length; b++) {
          if (highAtoms[i] == bondList[b][0]) {
            currAtomTextElement = molSvg.select(
              "line:nth-of-type(" + svgBondList[b] + ")",
            );
            x = parseInt(currAtomTextElement.attr("x1")) + numberOffset[0];
            y = parseInt(currAtomTextElement.attr("y1")) + +numberOffset[1];

            _foundBond = true;
            break;
          } else {
            if (highAtoms[i] == bondList[b][1]) {
              currAtomTextElement = molSvg.select(
                "line:nth-of-type(" + svgBondList[b] + ")",
              );
              x = parseInt(currAtomTextElement.attr("x2")) + numberOffset[0];
              y = parseInt(currAtomTextElement.attr("y2")) + +numberOffset[1];
              _foundBond = true;
            }
          }
        }
        if (!_foundBond) {
          continue; // atom has no drawn bond: skip instead of reusing stale x/y
        }

        r = 220;
        numberString = `  <text id='number${i}' x='${x}' y='${y}' font-size='270px' font-weight='600' font-family='Arial, sans-serif' fill='${(numberingEmphasis === null || numberingEmphasis.indexOf(i) >= 0) ? "#193F8F" : "#9ac1ed"}' stroke='white' stroke-width='30px' paint-order='stroke'>${i + 1}</text> `;
        numbersSVGElements[i] = numberString;
      }
      break;
  }

  if (time === undefined || time === null) {
    time = 400;
  }
  if (time == 0) {
    for (let i = 0; i < numbersSVGElements.length; i++) {
      fShowNumber();
    }
  } else {
    myNumberingTimeout = setInterval(fShowNumber, time);
  }
}

// ── fShowNumber ───────────────────────────────────────────────────────────

function fShowNumber() {
  fShowNumber3D(currNumberEl);
  const numberElement = MuSVG.parse(numbersSVGElements[currNumberEl]);
  if (numberElement) {
    molSvg.select("g").append(numberElement);
  }
  currNumberEl += 1;

  if (currNumberEl >= numbersSVGElements.length) {
    currNumberEl = 0;
    clearInterval(myNumberingTimeout);
  }
}

// ── fShowNumbering3D ──────────────────────────────────────────────────────

function fShowNumbering3D() {
  const chain3D = Array.isArray(numberingAtomOverride3D)
    ? numberingAtomOverride3D : mainChainAtoms3D;
  for (let i = 0; i < chain3D.length; i++) {
    fShowNumber3D(i, chain3D);
  }
}

// ── removeEcho3D ──────────────────────────────────────────────────────────

function removeEcho3D() {
  fJSmolScript(jmolAppletNomeclature, " set echo  off;");
}

// ── fShowNumber3D ─────────────────────────────────────────────────────────

function fShowNumber3D(n, chain) {
  const _chain = Array.isArray(chain) ? chain : mainChainAtoms3D;
  let myAtom =
    Array.isArray(numberingAtomOverride3D)
      ? numberingAtomOverride3D[n]
      : _chain[n];

  if (typeof myAtom === "undefined" || myAtom === null) {
    return;
  }

  let id = "theGroupEcho" + (n + 1);
  let atom = "{atomno = " + myAtom + "}";
  let num = n + 1;
  let d = 0.01; // stroke thickness in Å (tune this)

  // Locant emphasis: the selected number(s) stay blue, the rest dim to gray
  // (shadow echoes stay black for legibility). Same index space as the 2D
  // labels (position in the displayed chain); null = all blue.
  let _dim = false;
  try { _dim = Array.isArray(numberingEmphasis) && numberingEmphasis.indexOf(n) < 0; } catch (eD) { _dim = false; }
  let _echoCol = _dim ? "x9ac1ed" : "x193f8f";

  // Shadow echoes in 4 directions (black stroke)
  let s = "";
  s +=
    " set echo " +
    id +
    " " +
    atom +
    "; set echo offset {-1.1 1.1 3}; font echo 30 sansSerif bold; color echo[" + _echoCol + "]; echo " +
    num +
    ";";

  s +=
    " set echo " +
    id +
    "s1 " +
    atom +
    "; set echo offset {" +
    (-1.1 + d) +
    " " +
    (1.1 - d) +
    " 3}; font echo 30 sansSerif bold; color echo white; echo " +
    num +
    ";";

  fJSmolScript(jmolAppletNomeclature, s);
}

// ── fHighlightMultiBonds ──────────────────────────────────────────────────

function fShowBondAtoms() {
  // Settings-panel option (default off): bond-component clicks (αν/εν/ιν)
  // highlight only the bonds; endpoint C atoms join only when enabled.
  try {
    return $("#bondAtomsCheck").hasClass("selectedCheck");
  } catch (e) {
    return false;
  }
}

function fShowNumberingBonds() {
  // Settings-panel option (default on): main-chain/acid-fragment numbering
  // clicks highlight the C–C bonds as well as the atoms.
  try {
    return $("#highlightNumberingBondsCheck").hasClass("selectedCheck");
  } catch (e) {
    return true;
  }
}

function fHighlightMultiBonds(bondCompPos) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  let bondType, bondID;
  if (nameAnalysisMode == "none") {
    return;
  }
  if (multiBondListCC.length == 0) {
    return;
  }

  let highAtomsArg = "";
  let highBondsArg = "";
  if (bondCompPos == 1) {
    // one type of multiple bond
    if (multiBondsObj.CCd.length > 0) {
      bondType = 2; // double bond
    } else {
      bondType = 3; // triple bond
    }

    for (let i = 0; i < multiBondListCC.length; i++) {
      bondID = multiBondListCC[i];
      if (bondList[bondID - 1][2] !== bondType) {
        continue;
      } // skip if not the  bond type
      highBondsArg += multiBondListCC[i] + ",9";
      if (i < multiBondListCC.length - 1) {
        highBondsArg += ",";
      }

      highAtomsArg +=
        bondList[multiBondListCC[i] - 1][0] +
        ",9," +
        bondList[multiBondListCC[i] - 1][1] +
        ",9";
      if (i < multiBondListCC.length - 1) {
        highAtomsArg += ",";
      }
    }
  } else if (bondCompPos == 2) {
    // two types of multiple bonds -- highlight triple bonds
    for (let i = 0; i < multiBondListCC.length; i++) {
      bondID = multiBondListCC[i];
      if (bondList[bondID - 1][2] !== 3) {
        continue;
      } // skip if not triple bond
      highBondsArg += multiBondListCC[i] + ",9";
      if (i < multiBondListCC.length - 1) {
        highBondsArg += ",";
      }

      highAtomsArg +=
        bondList[multiBondListCC[i] - 1][0] +
        ",9," +
        bondList[multiBondListCC[i] - 1][1] +
        ",9";
      if (i < multiBondListCC.length - 1) {
        highAtomsArg += ",";
      }
    }
  }

  jsmeNomeclatureApplet.setBondBackgroundColors(0, highBondsArg);
  // Endpoint atoms only when the bond-atoms setting is on (default: bonds only).
  if (fShowBondAtoms()) jsmeNomeclatureApplet.setAtomBackgroundColors(0, highAtomsArg);

  fUpdateSVG();
}

// ── fHighlightMultiBonds3D ────────────────────────────────────────────────

function fHighlightMultiBonds3D(bondCompPos) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  // Uses SDF-derived *3D globals directly — no 2D-position-3D mapping needed.

  if (multiBondListCC3D.length === 0) {
    return;
  }

  let bondType;
  let bOrder;
  if (bondCompPos === 1) {
    bondType = multiBondsObj3D.CCd.length > 0 ? 2 : 3;
  } else {
    bondType = 3; // bondCompPos 2 always targets triple bonds
  }

  const highBonds3D = [];
  for (let i = 0; i < multiBondListCC3D.length; i++) {
    const bondID = multiBondListCC3D[i];
    if (bondList3D[bondID - 1][2] !== bondType) {
      continue;
    }
    const atom1 = bondList3D[bondID - 1][0]; // already SDF 1-based
    const atom2 = bondList3D[bondID - 1][1];
    highBonds3D.push([atom1, atom2]);
  }

  if (highBonds3D.length === 0) {
    return;
  }

  let highAtoms3DArg = "select";
  for (let i = 0; i < highBonds3D.length; i++) {
    highAtoms3DArg +=
      " atomno=" + highBonds3D[i][0] + ", atomno=" + highBonds3D[i][1];
    if (i < highBonds3D.length - 1) {
      highAtoms3DArg += ",";
    }
    fJSmolScript(
      jmolAppletNomeclature,
      "select atomno=" +
        highBonds3D[i][0] +
        ", atomno=" +
        highBonds3D[i][1] +
        "; color bond [XD8EEDC];",
    );
  }

  fJSmolScript(
    jmolAppletNomeclature,
    highAtoms3DArg +
      "; color selectionHalos[XD8EEDC]; selectionHalos on; color atoms [XD8EEDC];",
  );
  if (!fShowBondAtoms()) {
    // Bonds-only mode: undo the atom halo — keep just the green bonds above.
    fJSmolScript(
      jmolAppletNomeclature,
      "select all; selectionHalos off; color atoms none;",
    );
  } else {
    // Single bonds bridging two highlighted atoms inherit green from atom colors.
    // Reset them to CPK.
    const highAtomSet = new Set();
    for (let i = 0; i < highBonds3D.length; i++) {
      highAtomSet.add(highBonds3D[i][0]);
      highAtomSet.add(highBonds3D[i][1]);
    }
    for (let b = 0; b < bondList3D.length; b++) {
      if (!bondList3D[b]) {
        continue;
      }
      const ba1 = bondList3D[b][0],
        ba2 = bondList3D[b][1],
        bOrder = bondList3D[b][2];
      if (bOrder === 1 && highAtomSet.has(ba1) && highAtomSet.has(ba2)) {
        fJSmolScript(
          jmolAppletNomeclature,
          "select atomno=" + ba1 + ", atomno=" + ba2 + "; color bond cpk;",
        );
      }
    }
  }

  JmolSelection = highAtoms3DArg;
}

// ── fHighlightSingleBondsCC ───────────────────────────────────────────────

function fHighlightSingleBondsCC(atomSetOrNull) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  if (nameAnalysisMode === "none") {
    return;
  }

  // Optional scope: 1-based atom numbers (e.g. the ester acid chain). Both bond
  // ends must lie inside the set; omitted/null keeps the molecule-wide default.
  const _set = Array.isArray(atomSetOrNull) ? atomSetOrNull : null;
  let highAtomsArg = "";
  let highBondsArg = "";
  const bondArgs = [];
  const atomArgs = [];
  for (let i = 0; i < bondList.length; i++) {
    const bOrder = bondList[i][2];
    if (bOrder !== 1) {
      continue;
    }
    const a1 = bondList[i][0]; // 1-based
    const a2 = bondList[i][1]; // 1-based
    if (allAtomsTypeList[a1 - 1] !== "C" || allAtomsTypeList[a2 - 1] !== "C") {
      continue;
    }
    if (_set && (_set.indexOf(a1) < 0 || _set.indexOf(a2) < 0)) {
      continue;
    }
    bondArgs.push(i + 1 + ",9");
    atomArgs.push(a1 + ",9," + a2 + ",9");
  }
  if (bondArgs.length === 0) {
    return;
  }
  highBondsArg = bondArgs.join(",");
  highAtomsArg = atomArgs.join(",");

  jsmeNomeclatureApplet.setBondBackgroundColors(0, highBondsArg);
  // Endpoint atoms only when the bond-atoms setting is on (default: bonds only).
  if (fShowBondAtoms()) jsmeNomeclatureApplet.setAtomBackgroundColors(0, highAtomsArg);
  fUpdateSVG();
}

// ── fHighlightSingleBondsCC3D ─────────────────────────────────────────────

function fHighlightSingleBondsCC3D(atomSetOrNull) {
  // Overview-table builds (v55.x) scrape explanations with paints off.
  if (typeof window !== "undefined" && window.__mulerExplainQuiet) return;
  if (!bondList3D || bondList3D.length === 0) {
    return;
  }

  const _set3D = Array.isArray(atomSetOrNull) ? atomSetOrNull : null;
  const highBonds3D = [];
  for (let i = 0; i < bondList3D.length; i++) {
    if (!bondList3D[i]) {
      continue;
    }
    const bOrder = bondList3D[i][2];
    if (bOrder !== 1) {
      continue;
    }
    const a1 = bondList3D[i][0]; // SDF 1-based
    const a2 = bondList3D[i][1];
    if (
      allAtomsTypeList3D[a1 - 1] !== "C" ||
      allAtomsTypeList3D[a2 - 1] !== "C"
    ) {
      continue;
    }
    if (_set3D && (_set3D.indexOf(a1) < 0 || _set3D.indexOf(a2) < 0)) {
      continue;
    }
    highBonds3D.push([a1, a2]);
  }
  if (highBonds3D.length === 0) {
    return;
  }

  let highAtoms3DArg = "select";
  for (let i = 0; i < highBonds3D.length; i++) {
    highAtoms3DArg +=
      " atomno=" + highBonds3D[i][0] + ", atomno=" + highBonds3D[i][1];
    if (i < highBonds3D.length - 1) {
      highAtoms3DArg += ",";
    }
    fJSmolScript(
      jmolAppletNomeclature,
      "select atomno=" +
        highBonds3D[i][0] +
        ", atomno=" +
        highBonds3D[i][1] +
        "; color bond [XD8EEDC];",
    );
  }
  fJSmolScript(
    jmolAppletNomeclature,
    highAtoms3DArg +
      "; color selectionHalos[XD8EEDC]; selectionHalos on; color atoms [XD8EEDC];",
  );
  if (!fShowBondAtoms()) {
    // Bonds-only mode: undo the atom halo — keep just the green bonds above.
    fJSmolScript(
      jmolAppletNomeclature,
      "select all; selectionHalos off; color atoms none;",
    );
  }

  JmolSelection = highAtoms3DArg;
}

// ── fSetMolVis3D ──────────────────────────────────────────────────────────

function fSetMolVis3D(theVisModel) {
  let mySpt;
  if (theVisModel === undefined) {
    theVisModel = vis3D;
  }

  switch (theVisModel) {
    case "ballnstick":
      mySpt =
        " select all and not _Xx;  spacefill 24%; wireframe 0.13;set labelFront off;" +
        JmolSelection;
      break;
    case "spacefill":
      mySpt =
        " select all and not _Xx;  spacefill 70%; wireframe off;set labelFront off;" +
        JmolSelection;
      break;
    case "sticks":
      mySpt =
        " select all and not _Xx;  spacefill off; wireframe 0.2;  set labelFront on;" +
        JmolSelection;
      break;
  }
  fJSmolScript(jmolAppletNomeclature, mySpt);
}

// ── fViewerHeights2D3D ────────────────────────────────────────────────────
// Container-derived viewer heights (viewport-based, never the viewers' own
// heights — that would be circular). Total = viewport minus page chrome;
// column chrome = every visible viewerCol child except the two viewer
// hosts (generic, so per-step chrome toggles are honored). Visible viewers
// split the remainder equally; both viewers share the VIEWER_MIN_H floor
// (mirrors the CSS minimums), the phone landscape cap stays as ceiling.
// Returns {h2, h3} (0 = hidden).

// Scroll-stable viewport height (v55.x, mobile): window.innerHeight slides
// with the URL bar on scroll (~50px); feeding it live recomputed viewer
// heights mid-scroll and ping-ponged the column ResizeObserver. Cached;
// refreshed only on width change (rotation/resize), large deltas
// (keyboard/split-screen) or first run. Falls back to live on any gap.
var _stableVH = 0, _stableVW = 0;
function fStableViewportH() {
  try {
    var liveW = 0, liveH = 0;
    try { liveW = window.innerWidth || 0; liveH = window.innerHeight || 0; } catch (eM) {}
    if (!(liveH > 0)) return _stableVH > 0 ? _stableVH : 0;
    if (!(_stableVH > 0) || (liveW > 0 && liveW !== _stableVW) || Math.abs(liveH - _stableVH) > 120) {
      _stableVH = liveH; _stableVW = liveW;
    }
    return _stableVH;
  } catch (e) { return 0; }
}
function fViewerHeights2D3D(raw) {
  var out = { h2: 0, h3: 0, full: 0 };
  try {
    // Scroll-stable viewport (v55.x): live innerHeight slides with the
    // mobile URL bar; the cached value keeps heights still mid-scroll.
    var _vph = 0;
    try { if (typeof fStableViewportH === "function") _vph = fStableViewportH() || 0; } catch (eV) { _vph = 0; }
    if (!(_vph > 0)) { try { _vph = window.innerHeight || 0; } catch (eV2) { _vph = 0; } }
    var total = _vph - 30; // header
    var h1 = document.getElementById("pageTitle");
    if (h1 && h1.offsetParent !== null) total -= h1.offsetHeight;
    // WIP notice banner (normal flow above the title while not dismissed).
    var devN = document.getElementById("devNotice");
    if (devN && devN.offsetParent !== null) total -= devN.offsetHeight;
    // Footer excluded from the budget (v54.28): the content-driven credits
    // footer must never shrink the viewers — the page scrolls for the
    // excess instead. (Previously subtracted its live offsetHeight.)
    // Per-step note card (presentation only): when it stays in flow above the
    // app columns (top position), its full vertical footprint (incl. net
    // margins) must leave the viewer budget — otherwise a two-viewer present
    // step with a note overflows the page. Hidden in authoring → offsetParent
    // is null; in a side rail it is beside the app (see probe below).
    var stepTxt = document.getElementById("scStepText");
    var textIsSideRail = false;
    try {
      textIsSideRail = !!(stepTxt && stepTxt.parentElement &&
        stepTxt.parentElement.classList &&
        stepTxt.parentElement.classList.contains("mainApp3Columns"));
    } catch (eRail) { /* layout probe unavailable */ }
    // v50: in a side-rail layout the card is beside the app, not above it,
    // so its height must not be subtracted from the viewer budget.
    if (stepTxt && stepTxt.offsetParent !== null && !textIsSideRail) {
      var sTxtH = stepTxt.offsetHeight, sTxtMT = 0, sTxtMB = 0;
      try {
        var sTxtCs = window.getComputedStyle(stepTxt);
        sTxtMT = parseFloat(sTxtCs.marginTop) || 0;
        sTxtMB = parseFloat(sTxtCs.marginBottom) || 0;
      } catch (eSTxt) { /* computed style unavailable */ }
      total -= (sTxtH + sTxtMT + sTxtMB);
    }
    total -= 30; // page margins / gaps
    // Presentation navigation: the fixed play bar overlays the top of the
    // viewport without taking flow space, so carve it out of the budget
    // while presenting — "full" heights then clear the h1, the play bar,
    // and the credits footer on any playback screen.
    try {
      if (typeof MuLERMoCScenario !== "undefined" && MuLERMoCScenario && MuLERMoCScenario.present) {
        var pb = document.getElementById("scenarioPlayBar");
        if (pb && pb.offsetParent !== null && pb.offsetHeight > 0) total -= (pb.offsetHeight + 8);
      }
    } catch (ePb) { /* play-bar probe unavailable */ }
    var vc = document.getElementById("viewerCol");
    var chrome = 0;
    var show2D = false, show3D = false;
    if (vc) {
      // Visibility is read off the actually-toggled units: for 2D the nested
      // SVG overlay, the live JSME applet, or the dedicated draft editor
      // (exactly one is visible; the DIV itself never hides) and the 3D
      // container. Both hosts are skipped in chrome accounting below (their
      // heights are viewers, not chrome).
      try {
        var _svg2D = document.getElementById("jsmeNomeclatureSVG");
        var _app2D = document.getElementById("jsmeNomeclature");
        var _ed2D = document.getElementById("jsmeEditDraft");
        if ((_svg2D && _svg2D.offsetParent !== null) || (_app2D && _app2D.offsetParent !== null) ||
            (_ed2D && _ed2D.offsetParent !== null)) show2D = true;
      } catch (eV2) { /* overlay lookup unavailable */ }
      var kids = vc.children;
      for (var i = 0; i < kids.length; i++) {
        var k = kids[i];
        if (k.id === "jsmeNomeclatureDIV" || k.id === "nomeclature3D") {
          if (k.id === "nomeclature3D" && k.offsetParent !== null) show3D = true;
          continue;
        }
        if (k.offsetParent !== null && k.offsetHeight > 0) chrome += k.offsetHeight;
      }
    } else {
      show2D = true; show3D = true;
    }
    var n = (show2D ? 1 : 0) + (show3D ? 1 : 0);
    if (n === 0) return out;
    // Dead-space top-up: when a sibling column (menu/analysis content)
    // stretches the row taller than the viewport share, viewers split the
    // row-driven height instead — otherwise dead space sits under them.
    // Sibling heights never depend on viewer size: no circularity.
    var sibH = 0;
    try {
      var menu = document.getElementById("menuCol");
      if (menu && menu.offsetParent !== null) sibH = Math.max(sibH, menu.offsetHeight);
      var anal = document.getElementById("analysisCol");
      if (anal && anal.offsetParent !== null) sibH = Math.max(sibH, anal.offsetHeight);
    } catch (eSib) { /* sibling measuring unavailable */ }
    var shareFor = function (k) {
      var e = Math.floor((total - chrome) / k);
      var rowE = Math.floor((sibH - chrome) / k);
      return rowE > e ? rowE : e;
    };
    var each = shareFor(n);
    // Single-viewer full height (no cap), independent of how many are visible
    // right now — the slider ceiling in Ρυθμίσεις.
    var eachFull = shareFor(1);
    out.full = Math.max(
      show2D ? Math.max(eachFull, VIEWER_MIN_H) : 0,
      show3D ? Math.max(eachFull, VIEWER_MIN_H) : 0
    );
    var maxViewerH =
      _vph < 430 ? Math.floor(_vph * 0.3) : Infinity;
    // Single visible viewer: cap its height. Default is "full" (whole single
    // share); null uses the both-visible share so hiding the other viewer
    // never resizes the survivor; an explicit px cap also overrides. The cap
    // is clamped into
    // [floor, single share], so it can neither squash below the CSS minimum
    // nor exceed the space one viewer can actually take. `raw` skips the cap
    // (used to measure the full height for the slider ceiling).
    var cap2 = Infinity, cap3 = Infinity;
    // Double visible viewers: an explicit COMBINED total overrides the equal
    // split for BOTH — each viewer gets half the combined 2D+3D height (it can
    // grow or shrink; the page scrolls if the total no longer fits). Default
    // is "full"; Auto (viewerBothH == null) keeps the split. The phone cap
    // still trims.
    var each2 = each, each3 = each;
    if (!raw && n === 2 && viewerBothH != null) {
      // "full" fills the live viewport instead of a stored px total.
      var bothTotal = viewerBothH === "full"
        ? Math.round(total - chrome)
        : Math.round(viewerBothH);
      if (viewerBothH !== "full") {
        if (bothTotal < VIEWER_BOTH_MIN) bothTotal = VIEWER_BOTH_MIN;
        if (bothTotal > VIEWER_BOTH_MAX) bothTotal = VIEWER_BOTH_MAX;
      }
      each2 = each3 = Math.round(bothTotal / 2);
    } else if (n === 1 && !raw) {
      var autoCap = shareFor(2);
      if (show2D) {
        // "full" resolves to the whole single share: Infinity collapses to
        // single2 through the clamp below — never below the CSS minimum,
        // never beyond what one viewer can actually take.
        cap2 = viewerMaxH === "full" ? Infinity : (viewerMaxH != null ? viewerMaxH : autoCap);
        var single2 = Math.max(each, VIEWER_MIN_H);
        if (cap2 < VIEWER_MIN_H) cap2 = VIEWER_MIN_H;
        if (cap2 > single2) cap2 = single2;
      }
      if (show3D) {
        cap3 = viewerMaxH === "full" ? Infinity : (viewerMaxH != null ? viewerMaxH : autoCap);
        var single3 = Math.max(each, VIEWER_MIN_H);
        if (cap3 < VIEWER_MIN_H) cap3 = VIEWER_MIN_H;
        if (cap3 > single3) cap3 = single3;
      }
    }
    if (show2D) out.h2 = Math.min(Math.max(each2, VIEWER_MIN_H), cap2, maxViewerH);
    if (show3D) out.h3 = Math.min(Math.max(each3, VIEWER_MIN_H), cap3, maxViewerH);
    // Width bound (v55.x): a viewer is never taller than it is wide
    // (width/height >= 1), phones and desktop alike. Widths don't move on
    // scroll, so this also damps any residual URL-bar jitter. Final word —
    // applies to auto split, stored px caps and "Full".
    try {
      var _w2 = 0, _w3 = 0;
      try { if (vc && vc.clientWidth > 0) _w2 = Math.max(vc.clientWidth - 4, 50); } catch (eW2) {}
      try { var _c3 = document.getElementById("nomeclature3D"); if (_c3 && _c3.clientWidth > 0) _w3 = _c3.clientWidth; } catch (eW3) {}
      if (show2D && _w2 > 0 && out.h2 > _w2) out.h2 = _w2;
      if (show3D && _w3 > 0 && out.h3 > _w3) out.h3 = _w3;
      var _wF = _w2 > 0 ? _w2 : _w3;
      if (_wF > 0 && out.full > _wF) out.full = _wF;
    } catch (eW) { /* width clamp best-effort */ }
  } catch (eH) { /* measuring unavailable */ }
  return out;
}

// ── fResizeViewers ────────────────────────────────────────────────────────
// Fluid viewers: widths follow the viewer column (native re-depict —
// coordinates correct by construction); heights are container-derived via
// fViewerHeights2D3D (viewport minus chrome, split equally, floors hold).
// Then rebuild the SVG overlay + replay numbering from the fresh graphics.
// Triggered by a debounced ResizeObserver on #viewerCol (installed in
// jsmeOnLoad); the old window-resize listener below stays retired. Zoom
// (molZoom2D, absolute, stored per step) composes on top, untouched — fit
// and framing are independent.
function fResizeViewers() {
  // 3D: fit the JSmol viewport to its container (unchanged behavior).
  var container = document.getElementById("nomeclature3D");
  var vh = fViewerHeights2D3D();
  if (container && container.clientWidth > 0) {
    var w3 = container.clientWidth;
    // Container-derived height (falls back to the old width ratio if the
    // helper yields nothing, e.g. hidden viewer).
    var h = vh.h3 > 0 ? vh.h3 : Math.round((w3 * 220) / 480);
    try {
      if (typeof Jmol !== "undefined" && typeof jmolAppletNomeclature !== "undefined") {
        fJSmolResizeApplet(jmolAppletNomeclature, { width: w3, height: h });
      }
    } catch (e3D) { /* 3D applet unavailable */ }
    // The applet info table div sets the visible 3D height: assert it to the
    // same value so API and DOM agree (guarded: JSmol version naming).
    try {
      var infoDiv = document.getElementById("jmolAppletNomeclature_appletinfotablediv");
      if (infoDiv) infoDiv.style.height = h + "px";
    } catch (eInfo) { /* JSmol internals unavailable */ }
  }
  // 2D fluid: fit the applets to the viewer column content width.
  var vc = document.getElementById("viewerCol");
  if (!vc) return;
  var vw = 0;
  try { vw = Math.round(vc.clientWidth); } catch (eV) { vw = 0; }
  if (!(vw > 0)) return;
  // Column chrome gutter (border + panel padding): the applet must never
  // overflow its column. Height is container-derived (falls back to the old
  // width ratio if the helper yields nothing).
  var aw = Math.max(vw - 4, 50);
  var svgH = vh.h2 > 0 ? vh.h2 : Math.round((aw * 200) / 450);
  // Diagnostics (owner console protocol): set window.MuLERmoCDebugResize
  // to true and watch for one [resize] line per run (off by default).
  try {
    if (typeof window !== "undefined" && window.MuLERmoCDebugResize) {
      var _vis2 = false, _vis3 = false;
      try {
        var _s2 = document.getElementById("jsmeNomeclatureSVG");
        var _a2 = document.getElementById("jsmeNomeclature");
        var _e2 = document.getElementById("jsmeEditDraft");
        _vis2 = !!((_s2 && _s2.offsetParent !== null) || (_a2 && _a2.offsetParent !== null) ||
          (_e2 && _e2.offsetParent !== null));
        var _s3 = document.getElementById("nomeclature3D");
        _vis3 = !!(_s3 && _s3.offsetParent !== null);
      } catch (eVis) { /* visibility check unavailable */ }
      // console.info("[resize] vh2=" + vh.h2 + " vh3=" + vh.h3 +
        // " fallback2D=" + (!(vh.h2 > 0)) + " fallback3D=" + (!(vh.h3 > 0)) +
        // " applied2D=" + aw + "x" + svgH + " visible2D=" + _vis2 +
        // " visible3D=" + _vis3);
    }
  } catch (eDbg) { /* diagnostics unavailable */ }
  var svg = document.getElementById("jsmeNomeclatureSVG");
  if (svg) {
    svg.style.width = aw + "px";
    svg.style.height = svgH + "px";
    try {
      if (
        typeof jsmeNomeclatureApplet !== "undefined" &&
        jsmeNomeclatureApplet.setSize
      ) {
        jsmeNomeclatureApplet.setSize(aw, svgH);
      }
    } catch (eS) { /* applet unavailable */ }
  }
  // Draft editor: same box as the SVG view it replaces (sized only while
  // visible — a display:none setSize would collapse it to zero).
  try {
    var _edDiv = document.getElementById("jsmeEditDraft");
    if (_edDiv && _edDiv.offsetParent !== null &&
        typeof jsmeEditDraftApplet !== "undefined" && jsmeEditDraftApplet && jsmeEditDraftApplet.setSize) {
      _edDiv.style.width = aw + "px";
      _edDiv.style.height = svgH + "px";
      jsmeEditDraftApplet.setSize(aw, svgH);
    }
  } catch (eE) { /* edit applet unavailable */ }
  // Overlays derive from the applet graphics: re-apply the zoom scale (this
  // re-fits the depiction — setSize alone leaves it small/stale, as any zoom
  // press demonstrates), rebuild the overlay + replay numbering. Highlight
  // survival across setSize is a browser verdict (see checklist); if the
  // tint drops, re-fire the selected component via the click sequence
  // (fClearHighlights + fUpdateSVG + fExplainNameComp, no narration).
  try { if (typeof fReapplyZoomScale2D === "function") fReapplyZoomScale2D(); } catch (eZ) { /* zoom re-apply unavailable */ }
}

// Debounced ResizeObserver on the viewer column: window drags, pin/unpin,
// viewer toggles, settings open/close. Tracks width AND height; skips
// unchanged geometry; no loop (applet boxes follow the column, never the
// reverse). Replaces the retired window listener below.
var _zoomROTimer = null;
var _zoomROLastW = 0;
var _zoomROLastH = 0;
var _zoomRO = null;
function fInitZoomObserver2D() {
  try {
    if (_zoomRO || typeof ResizeObserver === "undefined") return;
    var vc = document.getElementById("viewerCol");
    if (!vc) return;
    var _geom = function () {
      var r = { w: 0, h: 0 };
      try {
        var b = vc.getBoundingClientRect();
        r.w = Math.round(b.width); r.h = Math.round(b.height);
      } catch (eG) { /* measuring unavailable */ }
      return r;
    };
    _zoomRO = new ResizeObserver(function () {
      try {
        var g = _geom();
        if (g.w === _zoomROLastW && g.h === _zoomROLastH) return;
        if (_zoomROTimer) clearTimeout(_zoomROTimer);
        _zoomROTimer = setTimeout(function () {
          _zoomROTimer = null;
          var g2 = _geom();
          if (!(g2.w > 0) || (g2.w === _zoomROLastW && g2.h === _zoomROLastH)) return;
          _zoomROLastW = g2.w; _zoomROLastH = g2.h;
          fResizeViewers();
        }, 150);
      } catch (eO) { /* observer unavailable */ }
    });
    try {
      var g0 = _geom();
      _zoomROLastW = g0.w; _zoomROLastH = g0.h;
    } catch (eI) { _zoomROLastW = 0; _zoomROLastH = 0; }
    _zoomRO.observe(vc);
  } catch (eZ) { /* observer unavailable */ }
}

// Retired window-resize listener (superseded by the observer above):
// window.addEventListener('resize', function () {
//     clearTimeout(_resizeTimer)
//     _resizeTimer = setTimeout(fResizeViewers, 150)
// })

// JSmol-ready resend: the initial fit (jsmeOnLoad) can land before the 3D
// applet is live, silently dropping its resize (the usual suspect when the
// 3D height sticks at a stale value). Re-run once when JSmol reports ready
// via the page handshake (scenario deep links wait on the same flag).
var _resizeSentOn3DReady = false;
(function () {
  try {
    var _prevReady = (typeof jmol_isReady === "function") ? jmol_isReady : null;
    jmol_isReady = function (applet) {
      try { if (_prevReady) _prevReady(applet); } catch (eP) { /* handshake first */ }
      if (!_resizeSentOn3DReady) {
        _resizeSentOn3DReady = true;
        try { setTimeout(function () { fResizeViewers(); }, 300); } catch (eT) { /* timer unavailable */ }
      }
      // Cold-boot resend: a 3D load skipped while JSmol was dead is replayed
      // once the applet reports ready — molecule-guarded, no rebuild.
      // If the naming panel never rendered (cold-boot abort before the
      // wrappers existed), redo the full select instead: it is the same code
      // path as clicking the molecule, which is known to recover. Skipped
      // while presenting (step chrome owns the state there; the step
      // re-click below covers it).
      try {
        var _pm = null, _sel = null;
        try { _pm = window.__mulerPending3D || null; } catch (ePm) { _pm = null; }
        try { _sel = (typeof selectedMol !== "undefined") ? selectedMol : null; } catch (eSm) { _sel = null; }
        if (_pm && _sel && _pm === _sel && typeof fJSmolLive === "function" && fJSmolLive()) {
          try { window.__mulerPending3D = null; } catch (eC) { /* best-effort */ }
          var _presenting = false;
          try { _presenting = !!(typeof MuLERMoCScenario !== "undefined" && MuLERMoCScenario.present); } catch (ePs) { /* best-effort */ }
          var _named = false;
          try { _named = !!document.querySelector("#nameAnalysis .nameCompContainer .nameCompBox"); } catch (eNb) { /* best-effort */ }
          if (!_named && !_presenting && typeof fSelectMol === "function") {
            try { /* console.warn("[COLD-BOOT] naming missing at 3D-ready; re-running full select for " + _sel); */ } catch (eW2) { /* best-effort */ }
            try { fSelectMol(); } catch (eFs) { try { /* console.error("[COLD-BOOT] resend reselect failed for " + _sel, eFs); */ } catch (eL) {} }
          } else {
            try { if (typeof fLoadMol3D === "function") fLoadMol3D(); } catch (eL) { /* best-effort */ }
            try { if (typeof showAtomSymbols3D === "function") showAtomSymbols3D(); } catch (eA) { /* best-effort */ }
            try { if (typeof showHydrogens3D === "function") showHydrogens3D(); } catch (eH) { /* best-effort */ }
            try { if (typeof rotate3D === "function") rotate3D(); } catch (eR) { /* best-effort */ }
          }
          try {
            if (typeof MuLERMoCScenario !== "undefined" && MuLERMoCScenario.present &&
              typeof fScenarioPresent === "function" && typeof fScenarioNormMode === "function" &&
              typeof fScenarioClickNameBox === "function") {
              var _ps = fScenarioPresent();
              var _st = (_ps && _ps.steps) ? _ps.steps[_ps.index] : null;
              if (_st && _st.selectedMol === _sel && _st.nameAnalysisMode && fScenarioNormMode(_st.nameAnalysisMode) !== "none") {
                fScenarioClickNameBox(_st, ++MuLERMoCScenario.applyToken);
              }
            }
          } catch (eSH) { /* scenario re-highlight best-effort */ }
        }
      } catch (ePR) { /* resend best-effort */ }
    };
  } catch (eW) { /* hook unavailable */ }
})();
