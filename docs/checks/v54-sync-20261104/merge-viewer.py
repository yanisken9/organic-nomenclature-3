"""Reproducible first-pass merge of root-owned v54 viewer/data modules.

Reads the frozen upstream scratch comparison, never changes 52 or React.
Subsequent verified candidate corrections are recorded separately.
"""
from pathlib import Path
import re, json, hashlib

ROOT = Path.cwd()
SOURCE = Path('/tmp/namelecule-sync-preflight-20261104')
HERE = ROOT / 'docs/checks/v54-sync-20261104'
text = (SOURCE / 'merge-analysis/3-analysis.txt').read_text()
pattern = re.compile(r'^<<<<<<< [^\n]*\n(.*?)^\|{7} [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n', re.M | re.S)
blocks = list(pattern.finditer(text))
assert len(blocks) == 23
decisions = []

def resolve(match):
    n = blocks.index(match) + 1
    local, base, incoming = match.groups()
    result = incoming
    reason = 'Keep cumulative upstream functionality.'
    if n == 2:
        result = local
        reason = 'Keep one Namelecule name fitter; expanded overlay is added separately.'
    elif n == 4:
        result = local + incoming
        reason = 'Keep approved acid-specific component IDs and add generic upstream branch/suffix splitting.'
    elif n == 6:
        result = incoming
        reason = 'Use translated OH text and new component helpers; remove later duplicate GR-only function.'
    elif n == 8:
        result = local
        reason = 'Retain the full approved local sequential-numbering molecule list.'
    elif n == 12:
        result = local.replace('["compNumber2", "compSecondSub2"].includes(theRule)', '["compNumber2", "compSecondSub2"].includes(theRule) || /^compBranch(Sub|Loc)\\d+$/.test(theRule || "")')
        reason = 'Keep optional alkoxy rule exposure and support upstream branch-piece modes.'
    elif n == 15:
        result = local + incoming
        reason = 'Retain acid third-group mapping and add general branch modes.'
    elif n == 16:
        result = incoming.replace('X79dc6d', 'XD8EEDC')
        reason = 'Use readiness-safe JSmol wrapper with existing Namelecule palette.'
    elif n in [17, 18]:
        result = local.rstrip().removesuffix(';') + ' || /^compBranch(Sub|Loc)\\d+$/.test(nameAnalysisMode || "");\n'
        reason = 'Support both local acid third-group and generic branch-piece highlights.'
    elif n in [19, 20, 21, 22]:
        result = local.replace("fill='#254C50'", "fill='${(numberingEmphasis === null || numberingEmphasis.indexOf(i) >= 0) ? \"#193F8F\" : \"#9ac1ed\"}'")
        reason = 'Keep calibrated number size/scale; add upstream locant emphasis colors.'
    elif n == 23:
        result = incoming.replace('font echo 42', 'font echo 30')
        reason = 'Keep calibrated 3D numbering size with upstream emphasis color.'
    decisions.append({'conflict': n, 'reason': reason})
    return result

# Match objects from a second iterator are distinct: resolve by source offset.
index_by_start = {m.start(): i for i, m in enumerate(blocks)}
original_resolve = resolve
def resolve_by_offset(match):
    return original_resolve(blocks[index_by_start[match.start()]])
text = pattern.sub(resolve_by_offset, text)
assert not re.search(r'^(<<<<<<<|=======|>>>>>>>|\|{7})', text, re.M)
text = text.replace('-52', '-54').replace('_52', '_54')
text = text.replace('script spt/init-3.spt', 'script spt/init-54.spt')

# Upstream callers and local ResizeObserver share one fitting mechanism.
text = text.replace('function fFitNameToWidth() {', 'function fFitNameToWidth() {\n  if (window.nameExpanded) return;')
anchor = '// ── Expanded-name floating overlay'
wrapper = 'function fFitNameComponents() {\n  fScheduleNameFit();\n}\n\n'
assert text.count(anchor) == 1
text = text.replace(anchor, wrapper + anchor, 1)
text = text.replace('cont.style.setProperty("--nameCompScale", "1");', 'cont.style.setProperty("--nameCompScale", "1");\n    cont.style.setProperty("--nl-name-scale", "1");\n    cont.classList.remove("nl-name-tight");', 1)

# A local moved helper must not override upstream's translated definition.
gr_only = "function fAlcoholOHPositionText() {\n  return functionalGroupObj.alcohol.O.length > 1\n    ? ' Δηλώνει τις θέσεις των υδροξυλομάδων (–OH).'\n    : ' Δηλώνει τη θέση της υδροξυλομάδας (–OH).';\n}\n"
assert text.count(gr_only) == 1
text = text.replace(gr_only, '', 1)

# Drafts analyse the live drawing while selectedMol deliberately stays the
# template. Reset the transient source at that shared analysis boundary.
needle = 'function fMolDraftSandboxAnalyse(molText) {\n'
source_reset = '''  // Display source belongs to this drawing, never the selected template.
  myMol2D = molText;
  skeletalLayoutApplied = null;
  skeletalLayoutSource = mode2D === 'skeletal' && molText
    ? {key: selectedMol, mol: molText, draft: window.MulerDraft || null} : null;
'''
assert text.count(needle) == 1
text = text.replace(needle, needle + source_reset, 1)
text = text.replace('skeletalLayoutSource.key !== selectedMol) return;', 'skeletalLayoutSource.key !== selectedMol ||\n      (skeletalLayoutSource.draft || null) !== (window.MulerDraft || null)) return;', 1)
target = ROOT / 'js/mulermoc-nom-molview-54.js'
target.write_text(text)

# Keep all accepted geometry/IDs/order. Follow upstream54's new initial-camera
# policy at runtime; the old authored camera metadata remains visible in source.
data = (ROOT / 'js/jsme-nick-nomeclature-moc2-data_52.js').read_text()
data += '''
// v54 integration: initial 3D framing follows upstream's shared init script.
// Per-step scenario cameras remain supported. Original52 retains old defaults.
Object.keys(nameExamples).forEach(function (key) {
  delete nameExamples[key].moveto;
  delete nameExamples[key].initialZoom3D;
});
'''
(ROOT / 'js/jsme-nick-nomeclature-moc2-data_54.js').write_text(data)
for stem in ['iupac', 'lang', 'name-en']:
    p = Path('js/mulermoc-nom-' + stem + '-54.js')
    (ROOT / p).write_bytes((SOURCE / 'head' / p).read_bytes())
(HERE / 'viewer-merge-decisions.json').write_text(json.dumps(decisions, ensure_ascii=False, indent=2) + '\n')
print('Created root-owned54 viewer/data/language modules; 23 conflicts explicitly resolved.')
