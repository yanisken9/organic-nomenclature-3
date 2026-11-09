"""Bounded Developer evidence for optional equivalent parent numbering.

Execute the actual core parser/signature and viewer equivalence guard in macOS
JavaScriptCore against actual library MOL expressions. Fixed-width adversarial
MOL variants exercise metadata/graph exclusions without changing project data.
This does not execute a browser, drawing geometry, or the complete naming engine.
The script writes only memory-results.json and an automatically removed /tmp JSC
script; invoke with python3 -B to avoid a Python cache.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
CORE = 'js/mulermoc-nom-core-54.js'
VIEWER = 'js/mulermoc-nom-molview-54.js'
PLAYER = 'js/mulermoc-nom-scenario-54.js'
LIBRARY = 'js/jsme-nick-nomeclature-moc2-data_54.js'
SCENARIO = 'scenarios/alkanes-user-3.scenario.json'
baseline = json.loads((HERE / 'baseline.json').read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function(source, name):
    # The selected production declarations have top-level, unindented closing
    # braces; retain the actual text rather than duplicate their implementation.
    match = re.search(r'^function ' + re.escape(name) + r'\([^\n]*\).*?^}',
                      source, re.M | re.S)
    if not match:
        raise AssertionError('Missing production function: ' + name)
    return match.group(0)


def expression(source, name):
    match = re.search(r'\blet\s+' + re.escape(name) + r'\s*=\s*(.*?);', source, re.S)
    if not match:
        raise AssertionError('Missing actual library fixture: ' + name)
    return match.group(1)


core = (ROOT / CORE).read_text()
viewer = (ROOT / VIEWER).read_text()
player = (ROOT / PLAYER).read_text()
library = (ROOT / LIBRARY).read_text()
protected = {path: sha(ROOT / path) for path in baseline['protected']}
assert protected == baseline['protected'], 'A baseline-protected file changed'
assert 'function fEquivalentParentNumberingDirections(' not in (
    HERE / 'before' / VIEWER).read_text(), 'Unexpected baseline capability'
sources = {
    path: sha(ROOT / path) for path in (CORE, VIEWER, PLAYER, LIBRARY, SCENARIO)
}
declarations = [function(core, name) for name in (
    'fMolCountsLine', 'fParseMolV2000', 'fNumberedChainSignature',
    'fMolCanTransform2D', 'fRemapMolProperties2D')]
declarations += [function(viewer, name) for name in (
    'fEquivalentParentNumberingDirections', 'fLocantEmphasisIndices', 'fShowNumbering')]
declarations += [function(player, name) for name in (
    'fScenarioNumberingDirectionContext', 'fScenarioNumberingDirectionAtoms',
    'fScenarioChooseNumberingDirection', 'fScenarioNameCompDisabled',
    'fScenarioApply', 'fScenarioExitPresent')]
fixtures = []
for prefix in ('dimethyl_2_3_butane', 'methyl_2_pentane'):
    for mode in ('Condensed', 'Expanded', 'Skeletal'):
        name = prefix + '_2D_' + mode
        fixtures.append('const ' + name + '= (' + expression(library, name) + ');')

js = '\n'.join(declarations + fixtures + [
    'const actualScenario=' + (ROOT / SCENARIO).read_text() + ';'])
js += r'''
let checks = 0;
const labels = [];
const cases = [];
function check(value, label) {
    if (!value) throw Error(label);
    checks += 1;
    labels.push(label);
}
function equal(actual, expected, label) {
    check(JSON.stringify(actual) === JSON.stringify(expected), label);
}
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function plainGraph(text) {
    const parsed = fParseMolV2000(text);
    if (!parsed) throw Error('Test variant is not parseable');
    return {types: parsed.atoms.map(atom => atom.el),
        bonds: parsed.bonds.map(bond => bond.slice()), parsed};
}
function immutableCall(text, path, types, bonds, label) {
    const before = JSON.stringify({text, path, types, bonds});
    const result = fEquivalentParentNumberingDirections(text, path, types, bonds);
    equal(JSON.stringify({text, path, types, bonds}), before, label + ': inputs unchanged');
    if (result) {
        check(result.left !== path && result.right !== path && result.left !== result.right,
            label + ': returns independent arrays');
    }
    return result;
}
function replaceField(line, from, to, value) {
    const padded = line.padEnd(to, ' ');
    return padded.slice(0, from) + String(value).padStart(to - from, ' ') + padded.slice(to);
}
function atomField(text, id, from, to, value) {
    const lines = text.split(/\r?\n/), ci = fMolCountsLine(lines);
    lines[ci + id] = replaceField(lines[ci + id], from, to, value);
    return lines.join('\n');
}
function bondField(text, id, from, to, value) {
    const lines = text.split(/\r?\n/), ci = fMolCountsLine(lines);
    const na = Number(lines[ci].slice(0, 3));
    lines[ci + na + id] = replaceField(lines[ci + na + id], from, to, value);
    return lines.join('\n');
}
function property(text, value) { return text.replace(/M  END/, value + '\nM  END'); }
function addAtom(text, el) {
    const lines = text.split(/\r?\n/), ci = fMolCountsLine(lines);
    const na = Number(lines[ci].slice(0, 3));
    lines.splice(ci + na + 1, 0, '    2.5000    2.5000    0.0000 ' + el.padEnd(3) + ' 0  0  0  0  0  0  0  0  0  0  0  0');
    lines[ci] = replaceField(lines[ci], 0, 3, na + 1);
    return lines.join('\n');
}
function addBond(text, a, b, order) {
    const lines = text.split(/\r?\n/), ci = fMolCountsLine(lines);
    const na = Number(lines[ci].slice(0, 3)), nb = Number(lines[ci].slice(3, 6));
    lines.splice(ci + 1 + na + nb, 0, [a, b, order, 0].map(n => String(n).padStart(3)).join(''));
    lines[ci] = replaceField(lines[ci], 3, 6, nb + 1);
    return lines.join('\n');
}
function replaceBonds(text, replacement) {
    const lines = text.split(/\r?\n/), ci = fMolCountsLine(lines);
    const na = Number(lines[ci].slice(0, 3)), nb = Number(lines[ci].slice(3, 6));
    lines.splice(ci + 1 + na, nb, ...replacement.map(bond =>
        bond.concat([0]).map(n => String(n).padStart(3)).join('')));
    lines[ci] = replaceField(lines[ci], 3, 6, replacement.length);
    return lines.join('\n');
}
function reject(label, text, path = [1,2,3,4], supplied = null) {
    const graph = supplied || plainGraph(text);
    equal(immutableCall(text, path, graph.types, graph.bonds, label), null, label + ': rejected');
    cases.push({label, expected: 'rejected'});
}

// DOM, presentation selection and drawing primitives are narrow doubles.
// Context, selection action and fShowNumbering below remain production code.
let scenario = null;
let MuLERMoCScenario = {present: true, numberingDirection: null, ready: true,
    applyToken: 9, pending3D: {token: 9, done: false}};
let selectedMol = 'dimethyl_2_3_butane', mainChainAtomsList = [1,2,3,4];
let allAtomsTypeList = [], bondList = [], liveMol = '';
const jsmeNomeclatureApplet = {molFile: () => liveMol};
function fScenarioPresent() { return scenario; }
let nameAnalysisMode = 'compCarbonsCount', currNumberEl = 0;
let numberingFlag = true, myNumberingTimeout = null, numbersSVGElements = [];
let numberingAtomOverride = null, numberingAtomOverride3D = null, numberingEmphasis = null;
let mode2D = 'condensed', molSvg = null, highAtoms = [];
const compactNumberingLabelMap = {};
const document = {querySelector: () => null};
const renderEvents = [];
function MuSVG() { return {node: {dataset: {}}}; }
function fGetRenderedAtomTextMap() {
    return allAtomsTypeList.map((_, i) => ({attr: name => String(name === 'x' ? (i + 1) * 100 : 100)}));
}
function fShowNumber() { renderEvents.push(numbersSVGElements[currNumberEl++]); }
function clearInterval() {}
function setInterval() { throw Error('Unexpected animated timer in synchronous test'); }
let removedSelectedCalls = 0, directionUiRefreshes = 0;
function $(selector) { return {removeClass: () => { removedSelectedCalls++; }}; }
const clickedStepModes = [];
function fScenarioClickNameBox(step) {
    clickedStepModes.push(step.nameAnalysisMode);
    nameAnalysisMode = step.nameAnalysisMode;
}
function fScenarioApplyNumberingDirection() { directionUiRefreshes++; }
const resetBoundary = new Error('test stopped after actual reset boundary');
function fScenarioClearCheckpointNotice() { throw resetBoundary; }
function fScenarioIsAuthorPreview() { return false; }
function resetContext() {
    scenario = {id: 'actual-alkane-lesson', index: 6, steps: clone(actualScenario.steps)};
    MuLERMoCScenario.present = true;
    MuLERMoCScenario.numberingDirection = null;
    MuLERMoCScenario.pending3D = {token: 9, done: false};
    selectedMol = scenario.steps[6].selectedMol;
    mainChainAtomsList = [1,2,3,4];
    liveMol = dimethyl_2_3_butane_2D_Condensed;
    const graph = plainGraph(liveMol);
    allAtomsTypeList = graph.types;
    bondList = graph.bonds;
    nameAnalysisMode = 'compCarbonsCount';
}
function rejectContext(label, mutate) {
    resetContext();
    fScenarioNumberingDirectionContext().state.direction = 'right';
    mutate(scenario.steps[6]);
    equal(fScenarioNumberingDirectionAtoms(), null, label + ': no override');
    equal(MuLERMoCScenario.numberingDirection, null, label + ': transient choice cleared');
}

try {
    const modes = {
        condensed: dimethyl_2_3_butane_2D_Condensed,
        expanded: dimethyl_2_3_butane_2D_Expanded,
        skeletal: dimethyl_2_3_butane_2D_Skeletal
    };
    for (const [mode, text] of Object.entries(modes)) {
        const graph = plainGraph(text), path = [1,2,3,4];
        check(graph.parsed.atoms.filter(a => a.el === 'C').length === 6,
            mode + ': actual library has six atoms C');
        check(fNumberedChainSignature(path, graph.types, graph.bonds) !== null,
            mode + ': actual core signature is defined');
        equal(fNumberedChainSignature(path, graph.types, graph.bonds),
            fNumberedChainSignature(path.slice().reverse(), graph.types, graph.bonds),
            mode + ': actual core confirms equivalent numbered chemistry');
        equal(immutableCall(text, path, graph.types, graph.bonds, mode),
            {left: [1,2,3,4], right: [4,3,2,1]}, mode + ': physical directions retain same atom IDs');
        equal(immutableCall(text, path.slice().reverse(), graph.types, graph.bonds,
            mode + ' reversed canonical copy'), {left: [1,2,3,4], right: [4,3,2,1]},
            mode + ': result independent of incoming canonical orientation');
        const result = fEquivalentParentNumberingDirections(text, path, graph.types, graph.bonds);
        result.left[0] = 999;
        result.right[0] = 999;
        equal(path, [1,2,3,4], mode + ': mutating display output cannot change canonical parent');
        equal(fEquivalentParentNumberingDirections(text, path, graph.types, graph.bonds),
            {left: [1,2,3,4], right: [4,3,2,1]}, mode + ': no retained output mutation');
        // A proper 180-degree whole-molecule rotation changes endpoint positions
        // while preserving every bond, angle and numbered chemical signature.
        const lines = text.split(/\r?\n/), ci = fMolCountsLine(lines);
        graph.parsed.atoms.forEach((atom, i) => {
            let line = replaceField(lines[ci + 1 + i], 0, 10, (-atom.x).toFixed(4));
            lines[ci + 1 + i] = replaceField(line, 10, 20, (-atom.y).toFixed(4));
        });
        equal(immutableCall(lines.join('\n'), path, graph.types, graph.bonds, mode + ' rotated'),
            {left: [4,3,2,1], right: [1,2,3,4]}, mode + ': directions follow actual coordinates');
        cases.push({label: mode, expected: 'accepted with both orientations'});
    }

    const methylFixtures = [
        ['condensed', methyl_2_pentane_2D_Condensed, [1,2,3,4,6]],
        ['expanded', methyl_2_pentane_2D_Expanded, [1,2,3,4,6]],
        ['skeletal', methyl_2_pentane_2D_Skeletal, [1,2,4,5,6]]
    ];
    for (const [mode, text, path] of methylFixtures) {
        const graph = plainGraph(text);
        check(fNumberedChainSignature(path, graph.types, graph.bonds) !==
            fNumberedChainSignature(path.slice().reverse(), graph.types, graph.bonds),
            'methylpentane ' + mode + ': core observes unequal branch locants');
        reject('methylpentane ' + mode + ' unequal numbering', text, path);
    }

    const base = dimethyl_2_3_butane_2D_Condensed;
    reject('atom charge code', atomField(base, 1, 36, 39, 3));
    reject('M CHG property', property(base, 'M  CHG  1   1   1'));
    reject('mass difference', atomField(base, 1, 34, 36, 1));
    reject('M ISO isotope', property(base, 'M  ISO  1   1  13'));
    reject('radical charge code', atomField(base, 1, 36, 39, 4));
    reject('M RAD radical', property(base, 'M  RAD  1   1   2'));
    reject('atom stereo parity', atomField(base, 2, 39, 42, 1));
    reject('bond stereo wedge', bondField(base, 1, 9, 12, 1));
    reject('explicit hydrogen metadata', atomField(base, 1, 42, 45, 2));
    reject('explicit valence metadata', atomField(base, 1, 48, 51, 4));
    reject('unknown atom mapping metadata', atomField(base, 1, 60, 63, 1));
    reject('unknown atom stereocare metadata', atomField(base, 1, 45, 48, 1));
    reject('unknown nonnumeric atom metadata', atomField(base, 1, 45, 48, 'abc'));
    reject('unknown bond topology metadata', bondField(base, 1, 15, 18, 1));
    reject('unknown nonnumeric bond metadata', bondField(base, 1, 15, 18, 'abc'));
    const chiralLines = base.split(/\r?\n/), chiralCounts = fMolCountsLine(chiralLines);
    chiralLines[chiralCounts] = replaceField(chiralLines[chiralCounts], 12, 15, 1);
    reject('counts chiral flag', chiralLines.join('\n'));
    reject('unknown property', property(base, 'M  STY  1   1 SUP'));
    reject('disconnected extra carbon', addAtom(base, 'C'));
    reject('disconnected graph despite tree edge count', addBond(addAtom(base, 'C'), 1, 4, 1));
    reject('cyclic graph', addBond(base, 1, 4, 1));
    reject('multiple bond with symmetric locants', bondField(base, 2, 6, 9, 2));
    reject('unsupported symmetric heteroatoms',
        atomField(atomField(base, 5, 31, 34, 'O'), 6, 31, 34, 'O'));
    const overflow = replaceBonds(base, [[1,2,1],[1,3,1],[1,4,1],[1,5,1],[1,6,1]]);
    const overflowGraph = plainGraph(overflow);
    equal(fNumberedChainSignature([2,1,3], overflowGraph.types, overflowGraph.bonds),
        fNumberedChainSignature([3,1,2], overflowGraph.types, overflowGraph.bonds),
        'invalid valence tree would pass signature equivalence alone');
    reject('carbon degree five in otherwise connected acyclic graph', overflow, [2,1,3]);
    const hydrogenBridge = atomField(replaceBonds(base,
        [[1,2,1],[2,3,1],[3,4,1],[2,5,1],[5,6,1]]), 5, 31, 34, 'H');
    reject('hydrogen degree two in otherwise connected acyclic graph', hydrogenBridge);
    reject('duplicate atom in path', base, [1,2,2,4]);
    reject('disconnected path jump', base, [1,2,4,3]);
    reject('out of range path atom', base, [1,2,3,999]);
    reject('fractional path atom', base, [1,2,3,3.5]);
    reject('empty path', base, []);
    const stale = plainGraph(base);
    reject('stale live atom types', base, [1,2,3,4],
        {types: ['O'].concat(stale.types.slice(1)), bonds: stale.bonds});
    reject('stale missing live bond', base, [1,2,3,4],
        {types: stale.types, bonds: stale.bonds.slice(0, -1)});
    const changedBonds = clone(stale.bonds); changedBonds[0][2] = 2;
    reject('stale live bond order', base, [1,2,3,4],
        {types: stale.types, bonds: changedBonds});
    const invalidBonds = clone(stale.bonds); invalidBonds[0][0] = 0;
    reject('invalid live bond endpoint', base, [1,2,3,4],
        {types: stale.types, bonds: invalidBonds});
    const reversedBonds = stale.bonds.slice().reverse().map(b => [b[1], b[0], b[2]]);
    equal(immutableCall(base, [1,2,3,4], stale.types, reversedBonds, 'reordered undirected live bonds'),
        {left: [1,2,3,4], right: [4,3,2,1]},
        'equivalent graph accepted independent of live bond ordering');
    const tied = atomField(base, 4, 0, 10, '-1.2375');
    reject('ambiguous equal endpoint x', tied);
    const malformed = atomField(base, 1, 0, 10, 'NaN');
    equal(fParseMolV2000(malformed), null, 'actual core parser rejects malformed coordinate');
    reject('malformed source coordinate', malformed, [1,2,3,4], stale);
    equal(fEquivalentParentNumberingDirections('', [1,2,3,4], stale.types, stale.bonds),
        null, 'missing MOL fails closed');
    equal(fEquivalentParentNumberingDirections(base, null, stale.types, stale.bonds),
        null, 'missing parent fails closed');

    resetContext();
    const authoredSnapshot = JSON.stringify(actualScenario);
    equal(actualScenario.steps.filter(step => step.show && step.show.numberingDirection === true)
        .map(step => step.n), [7], 'actual authored opt-in enabled only at step 7');
    equal(scenario.steps[6].nameAnalysisMode, 'compCarbonsCount',
        'actual step 7 starts with parent atoms C highlighted and numbered');
    equal(fScenarioNumberingDirectionAtoms(), [1,2,3,4], 'context starts from physical left');
    const leftCopy = fScenarioNumberingDirectionAtoms(); leftCopy[0] = 999;
    equal(fScenarioNumberingDirectionAtoms(), [1,2,3,4], 'context never returns retained choice array');
    const contextState = MuLERMoCScenario.numberingDirection;
    fScenarioChooseNumberingDirection('right');
    equal(fScenarioNumberingDirectionAtoms(), [4,3,2,1], 'actual choose action reverses same parent');
    equal(clickedStepModes.slice(-1), ['compCarbonsCount'], 'actual choose action requests stem view');
    equal(nameAnalysisMode, 'compCarbonsCount', 'selection action restores visible numbering mode');
    equal(MuLERMoCScenario.pending3D.done, true, 'selection supersedes delayed initial callback');
    equal(directionUiRefreshes, 1, 'selection refreshes the direction control');
    equal(removedSelectedCalls, 1, 'selection clears earlier name-box selection');
    equal(mainChainAtomsList, [1,2,3,4], 'selection does not change canonical parent');
    equal(JSON.stringify(actualScenario), authoredSnapshot, 'selection does not alter authored JSON');
    fScenarioChooseNumberingDirection('invalid');
    equal(MuLERMoCScenario.numberingDirection, contextState, 'invalid direction cannot replace state');
    equal(fScenarioNumberingDirectionAtoms(), [4,3,2,1], 'invalid direction preserves current valid selection');
    // Repainting is the shared numbering path used by zoom, resize and clicks;
    // this verifies the resolver and generated strings, not those browser events.
    for (const reason of ['first render', 'repeat render', 'name component rerender']) {
        nameAnalysisMode = reason === 'name component rerender' ? 'compNumber1' : 'compCarbonsCount';
        currNumberEl = 0;
        renderEvents.length = 0;
        fShowNumbering(0);
        equal(highAtoms, [4,3,2,1], reason + ': actual viewer resolves selected order');
        equal(numberingAtomOverride3D, [], reason + ': optional display choice emits no 3D labels');
        check(renderEvents[0].includes("x='420'") && renderEvents[0].includes('>1</text>'),
            reason + ': displayed C1 follows physical right endpoint');
        check(renderEvents[3].includes("x='120'") && renderEvents[3].includes('>4</text>'),
            reason + ': displayed C4 follows physical left endpoint');
        equal(MuLERMoCScenario.numberingDirection, contextState, reason + ': preserves transient selection');
    }
    currNumberEl = 0;
    fShowNumbering(0, [2,5], [7,8]);
    equal(highAtoms, [2,5], 'explicit component 2D override retains priority');
    equal(numberingAtomOverride3D, [7,8], 'explicit component 3D override retains priority');
    currNumberEl = 0;
    fShowNumbering(0, [], []);
    equal(highAtoms, [], 'explicit empty component overrides retain priority');
    equal(fScenarioNumberingDirectionAtoms(), [4,3,2,1], 'explicit component paint preserves selected parent direction');
    nameAnalysisMode = 'compSecondSub1';
    fScenarioChooseNumberingDirection('left');
    equal(nameAnalysisMode, 'compCarbonsCount', 'choosing after another name component restores stem');
    equal(fScenarioNumberingDirectionAtoms(), [1,2,3,4], 'left choice restores original physical order');
    MuLERMoCScenario.pending3D = {token: 8, done: false};
    fScenarioChooseNumberingDirection('right');
    equal(MuLERMoCScenario.pending3D.done, false, 'different apply token callback is not marked complete');

    rejectContext('presentation inactive', () => { MuLERMoCScenario.present = false; });
    rejectContext('optional feature absent', step => { delete step.show.numberingDirection; });
    rejectContext('optional feature false', step => { step.show.numberingDirection = false; });
    rejectContext('naming panel unavailable', step => { step.show.naming = false; });
    rejectContext('name interaction disabled', step => { step.show.nameClick = false; });
    rejectContext('2D viewer hidden', step => { step.show.viewers['2D'] = false; });
    rejectContext('3D viewer visible', step => { step.show.viewers['3D'] = true; });
    rejectContext('3D visibility not explicit', step => { delete step.show.viewers['3D']; });
    rejectContext('molecule changed during pending load', () => { selectedMol = 'methyl_2_pentane'; });
    rejectContext('stem disabled', step => { step.styleName.disabled = ['comp5']; });
    rejectContext('stem hidden', step => { step.styleName.hidden = ['comp5']; });
    rejectContext('source gains unsupported metadata', () => { liveMol = property(liveMol, 'M  ISO  1   1  13'); });
    rejectContext('live graph becomes stale', () => { bondList = bondList.slice(1); });

    resetContext();
    fScenarioNumberingDirectionContext().state.direction = 'right';
    scenario.index = 7;
    equal(fScenarioNumberingDirectionAtoms(), null, 'moving to ordinary step clears override');
    scenario.index = 6;
    equal(fScenarioNumberingDirectionAtoms(), [1,2,3,4], 'reentry starts from left');
    fScenarioNumberingDirectionContext().state.direction = 'right';
    scenario = {id: 'replacement-scenario', index: 6, steps: clone(actualScenario.steps)};
    equal(fScenarioNumberingDirectionAtoms(), [1,2,3,4], 'scenario identity change resets selection');
    fScenarioNumberingDirectionContext().state.direction = 'right';
    scenario.steps[6] = clone(scenario.steps[6]);
    equal(fScenarioNumberingDirectionAtoms(), [1,2,3,4], 'step identity change resets selection');
    fScenarioNumberingDirectionContext().state.direction = 'right';
    mainChainAtomsList = [5,2,3,4];
    equal(fScenarioNumberingDirectionAtoms(), [5,2,3,4], 'equivalent parent path change resets selection');
    for (const [label, action] of [
        ['actual apply entry', () => fScenarioApply(scenario.steps[6])],
        ['actual exit entry', () => fScenarioExitPresent()]
    ]) {
        resetContext();
        fScenarioNumberingDirectionContext().state.direction = 'right';
        let caught = null;
        try { action(); } catch (error) { caught = error; }
        equal(caught, resetBoundary, label + ': intentional stop after production reset');
        equal(MuLERMoCScenario.numberingDirection, null, label + ': clears choice before downstream effects');
    }
    equal(JSON.stringify(actualScenario), authoredSnapshot, 'all context/render checks leave actual authored JSON unchanged');

    print(JSON.stringify({passed: true, assertions: checks, cases, labels}));
} catch (error) {
    print(JSON.stringify({passed: false, assertions: checks, cases, labels,
        failure: String(error), stack: String(error.stack || '')}));
}
'''

with tempfile.TemporaryDirectory(prefix='namelecule-step7-jsc-', dir='/tmp') as temp:
    script = Path(temp) / 'checks.js'
    script.write_text(js)
    completed = subprocess.run([JSC, str(script)], capture_output=True, text=True)
    lines = completed.stdout.strip().splitlines()
    try:
        evidence = json.loads(lines[-1])
    except (ValueError, IndexError):
        evidence = {'passed': False, 'failure': 'JSC did not produce a result',
                    'stdout': completed.stdout, 'stderr': completed.stderr}

evidence.update({
    'date': '2026-11-08',
    'kind': 'Developer evidence; not independent review',
    'command': 'python3 -B docs/checks/alkane-step7-numbering-20261108/check-memory.py',
    'runtime': JSC,
    'jscExitCode': completed.returncode,
    'sourceSha256': sources,
    'protectedBaselineFilesVerified': len(protected),
    'coreUnchangedFromSessionBaseline': protected[CORE] == baseline['protected'][CORE],
    'baselineNewPureHelperAbsent': True,
    'limitations': [
        'Actual selected production functions are extracted and executed; the full application is not loaded.',
        'Library MOL fixtures are actual expressions from data_54.js; adversarial variants are synthetic in-memory copies.',
        'Presentation lookup, DOM/name-click drawing primitives and timers are doubles; actual context, direction action and viewer numbering function execute.',
        'Actual Apply/Exit functions execute only through their reset boundary; full navigation is left to browser verification.',
        'Repeated render checks represent repaint invariance; actual zoom/resize browser events are not executed.',
        'No browser/layout, complete name-generation, 3D, accessibility, or conference sequence is tested here.',
    ],
})
result_path = HERE / 'memory-results.json'
if result_path.exists():
    previous = json.loads(result_path.read_text())
    attempts = previous.get('earlierFailedAttempts', [])
    if not previous.get('passed'):
        attempts.append({key: previous.get(key) for key in (
            'failure', 'assertions', 'sourceSha256', 'jscExitCode')})
    if attempts:
        evidence['earlierFailedAttempts'] = attempts
result_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: evidence.get(key) for key in (
    'passed', 'assertions', 'failure', 'protectedBaselineFilesVerified')}, ensure_ascii=False))
if not evidence['passed'] or completed.returncode:
    raise SystemExit(1)
