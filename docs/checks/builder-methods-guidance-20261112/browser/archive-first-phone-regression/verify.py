"""Bounded actual UI checks in an owned headless Firefox, never a personal browser."""
from pathlib import Path
import argparse, datetime, hashlib, http.server, json, os, socket, subprocess
import tempfile, threading, time, traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--phase', choices=['layout', 'flow'], default='layout')
args = parser.parse_args()
PHASE = args.phase
manifest_path = HERE.parent / 'runtime-source-freeze.json'
manifest = json.loads(manifest_path.read_text())
expected = {**manifest['sourceSHA256'], **manifest['protectedSHA256']}
before = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in expected}
assert before == expected, 'Frozen source/protected file hashes differ before browser startup'
HTTP_ERRORS = []


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, *a):
        pass

    def send_error(self, code, message=None, explain=None):
        HTTP_ERRORS.append({'code': code, 'path': self.path, 'message': message})
        super().send_error(code, message, explain)


def port_closed(port_number):
    with socket.socket() as probe:
        probe.settimeout(.3)
        return probe.connect_ex(('127.0.0.1', port_number)) != 0


def dismiss_orientation():
    if read('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):
        no_scroll_click('#rotatePromptDismiss', False)


def enter(embedded, width, height):
    viewport(width, height)
    if embedded:
        lesson(3, 55)
        dismiss_orientation()
        open_gate()
        if ev('!!document.querySelector(".nl-game-choice-card")'):
            choose('builder')
        else:
            builder_ready()
    else:
        open_page('games/name-builder.html?molecule=ethane')
        wait('!!document.querySelector("#bank-tiles button")', 65)
    pause(1)


def rectangle_visibility(selector, embedded):
    data = gesture_geometry(selector, embedded)
    usable = read('''(() => {const d=document.getElementById('nlQuizDialog');
      if(!d?.open)return{left:0,top:0,right:innerWidth,bottom:innerHeight};
      const r=d.getBoundingClientRect(),h=d.querySelector('.nl-quiz-dialog-header').getBoundingClientRect();
      return{left:Math.max(0,r.left+d.clientLeft),top:Math.max(0,h.bottom),
        right:Math.min(innerWidth,r.left+d.clientLeft+d.clientWidth),
        bottom:Math.min(innerHeight,r.top+d.clientTop+d.clientHeight)};})()''')
    bounds = data['globalRect']
    visible = bounds['left'] >= usable['left'] - 1 and bounds['right'] <= usable['right'] + 1 and bounds['top'] >= usable['top'] - 1 and bounds['bottom'] <= usable['bottom'] + 1
    return {'fullyVisible': visible, 'bounds': bounds, 'usable': usable, 'probe': data}


def measure(label, embedded):
    data = _builder_read('''(() => {
      const plain=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return{
        top:r.top,bottom:r.bottom,left:r.left,right:r.right,height:r.height,width:r.width,
        fontSize:s.fontSize,fontWeight:s.fontWeight,display:s.display,overflow:s.overflow,
        scrollHeight:e.scrollHeight,clientHeight:e.clientHeight}};
      const help=document.getElementById('answer-help');
      return{width:innerWidth,pageWidth:document.documentElement.scrollWidth,
        bodyWidth:document.body.scrollWidth,scrollY,help:plain(help),
        rows:[...document.querySelectorAll('#answer-help .helper-method')].map(e=>({
          ...plain(e),text:e.textContent,labelWeight:getComputedStyle(e.querySelector('strong')).fontWeight})),
        answer:plain(document.getElementById('answer-zone')),bank:plain(document.getElementById('bank-zone')),
        controls:plain(document.getElementById('tile-controls')),check:plain(document.getElementById('check-answer')),
        buttons:[...document.querySelectorAll('#tile-controls button')].map(e=>({...plain(e),name:e.getAttribute('aria-label')||e.textContent})),
        answerRows:new Set([...document.querySelectorAll('#answer-tiles button')].map(e=>Math.round(e.getBoundingClientRect().top))).size};
    })()''', embedded)
    data['label'] = label
    data['embedded'] = embedded
    data['checkVisibility'] = rectangle_visibility('#check-answer', embedded)
    data['answerVisibility'] = rectangle_visibility('#answer-zone', embedded)
    data['bankVisibility'] = rectangle_visibility('#bank-zone', embedded)
    OUT.setdefault('layouts', []).append(data)
    check(len(data['rows']) == 3, label + ' three explicit method rows', data['rows'])
    check(all(r['display'] == 'block' and float(r['fontSize'].replace('px', '')) >= 14 and int(r['labelWeight']) >= 700 for r in data['rows']), label + ' readable rows and bold labels', data['rows'])
    check(data['help']['scrollHeight'] <= data['help']['clientHeight'] + 1, label + ' full guidance has no internal clipping', data['help'])
    check(data['pageWidth'] <= data['width'] + 1 and data['bodyWidth'] <= data['width'] + 1,
          label + ' no horizontal page overflow', {'width': data['width'], 'page': data['pageWidth'], 'body': data['bodyWidth']})
    check(data['answerRows'] <= 1, label + ' answer remains one line')
    return data


def native_ids(embedded):
    if embedded:
        return correct_tile_ids(), bread('__lessonLoad.round')
    round_data = read('__builderEvents.findLast(e=>e.type==="round")')
    bank = read('NameleculeNameBuilderEngine.createBank(__builderEvents.findLast(e=>e.type==="round"),{seed:__builderEvents.findLast(e=>e.type==="round").roundId})')
    used, ids = set(), []
    for piece in round_data['pieces']:
        tile = next(t for t in bank if t['id'] not in used and t['text'] == piece['text'] and t['separatorBefore'] == piece['separatorBefore'])
        used.add(tile['id'])
        ids.append(tile['id'])
    return ids, round_data


def tile_selector(tile_id, container='bank'):
    return '#' + container + '-tiles [data-tile-id=' + json.dumps(tile_id) + ']'


def select(tile_id, embedded):
    current = builder_state(embedded)
    if current['selected'] != tile_id:
        no_scroll_click(tile_selector(tile_id, 'answer'), embedded)
    elif not current['focusedInAnswer'] or current['focusedId'] != tile_id:
        no_scroll_click(tile_selector(tile_id, 'answer'), embedded)
        no_scroll_click(tile_selector(tile_id, 'answer'), embedded)
    check(builder_state(embedded)['selected'] == tile_id, 'actual clicked answer tile selected', tile_id)


def clear_answer(embedded):
    for tile_id in builder_state(embedded)['answer'][:]:
        select(tile_id, embedded)
        no_scroll_click('#remove-tile', embedded)
    check(builder_state(embedded)['answer'] == [], 'actual remove controls emptied answer')


def methods_flow(embedded):
    label = 'embedded' if embedded else 'standalone'
    ids, round_data = native_ids(embedded)
    for tile_id in ids:
        no_scroll_click(tile_selector(tile_id), embedded)
    check(builder_state(embedded)['answer'] == ids, label + ' real click additions')
    check(len(ids) >= 2, label + ' canonical round supports actual reordering')
    moved = ids[-1]
    reordered = [moved] + ids[:-1]
    result = gesture_drag(moved, 'inside', embedded, answer_index=0, expected_order=reordered)
    OUT.setdefault('gestures', []).append(result)
    no_scroll_click('#move-after', embedded)
    expected_order = reordered[:]
    expected_order[0], expected_order[1] = expected_order[1], expected_order[0]
    check(builder_state(embedded)['answer'] == expected_order, label + ' actual right button exact reorder')
    no_scroll_click('#move-before', embedded)
    check(builder_state(embedded)['answer'] == reordered, label + ' actual left button exact reorder')
    key_selected('ArrowRight', embedded)
    key_selected('ArrowLeft', embedded)
    key_selected('Delete', embedded)
    key_add_focused(embedded)
    select(moved, embedded)
    no_scroll_click('#remove-tile', embedded)
    check(moved in builder_state(embedded)['bank'], label + ' actual remove button returned exact ID')
    no_scroll_click(tile_selector(moved), embedded)
    result = gesture_drag(moved, 'bottom', embedded)
    OUT.setdefault('gestures', []).append(result)
    clear_answer(embedded)
    no_scroll_click(tile_selector(ids[0]), embedded)
    if embedded:
        saved = builder_state()['answer']
        record_before = rec()
        call('browsingContext.reload', {'context': ctx, 'wait': 'complete'})
        ready(); dismiss_orientation(); open_gate(); builder_ready(); pause(1)
        check(builder_state()['answer'] == saved, 'actual reload restores exact partial answer')
        check(rec()['states']['3']['games']['builder']['seed'] == record_before['states']['3']['games']['builder']['seed'], 'actual reload preserves canonical round seed')
    no_scroll_click('#check-answer', embedded)
    state = builder_state(embedded)
    check(not state['feedback']['hidden'] and not state['feedback']['success'], label + ' partial answer gets genuine wrong feedback')
    visibility = rectangle_visibility('#feedback', embedded)
    check(visibility['fullyVisible'], label + ' wrong feedback automatically revealed', visibility)
    for tile_id in ids[1:]:
        no_scroll_click(tile_selector(tile_id), embedded)
    check(builder_state(embedded)['candidate'] == round_data['correctName'], label + ' canonical composition preserved')
    no_scroll_click('#check-answer', embedded)
    check(builder_state(embedded)['feedback']['success'], label + ' genuine native correct answer')
    visibility = rectangle_visibility('#feedback', embedded)
    check(visibility['fullyVisible'], label + ' correct feedback automatically revealed', visibility)
    if embedded:
        wait('!!document.querySelector(".round-next button")')
        check(not read('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'), 'one completed round does not prematurely unlock required gate')
        earned = rec()['states']['3']['games']['builder']
        check(bool(earned['states'][0]), 'canonical completed-round evidence retained', earned)
        no_scroll_click('.round-next button', False)
        builder_ready(); pause(1)
        check(read('document.getElementById("nlQuizProgress").textContent') == 'Κουίζ 2/3', 'actual next action preserves progress')
        next_molecule = bread('__lessonLoad.moleculeId')
        no_scroll_click('#nlQuizReturn', False)
        wait('!document.getElementById("nlQuizDialog").open')
        open_gate(); builder_ready(); pause(1)
        check(bread('__lessonLoad.moleculeId') == next_molecule, 'return/reopen resumes actual next round')
    OUT['solved'].append({'context': label, 'moleculeId': round_data['moleculeId'], 'correctName': round_data['correctName']})
    shot(label + '-methods-success.png')


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
with socket.socket() as probe:
    probe.bind(('127.0.0.1', 0))
    bidi_port = probe.getsockname()[1]
profile = Path(tempfile.mkdtemp(prefix='namelecule-builder-methods-' + PHASE + '-20261112-'))
(profile / 'user.js').write_text('user_pref("ui.prefersReducedMotion", 0);\n')
log = (HERE / (PHASE + '-firefox.log')).open('w')
command = ['/Applications/Firefox.app/Contents/MacOS/firefox', '--headless', '--no-remote',
           '--profile', str(profile), '--remote-debugging-port', str(bidi_port)]
firefox = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
process = {'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'serverPID': os.getpid(), 'serverScript': str(Path(__file__).resolve()),
    'firefoxPID': firefox.pid, 'command': command, 'profile': str(profile), 'bidiPort': bidi_port,
    'serverPort': server.server_port, 'baseURL': f'http://127.0.0.1:{server.server_port}/',
    'scope': 'Only a fresh owned headless profile and local server. Personal/GUI Firefox untouched.',
    'phase': PHASE, 'manifestSHA256': hashlib.sha256(manifest_path.read_bytes()).hexdigest()}
(HERE / 'process.json').write_text(json.dumps(process, indent=2) + '\n')
(HERE / (PHASE + '-process.json')).write_text(json.dumps(process, indent=2) + '\n')
print(json.dumps(process), flush=True)
complete = False
try:
    deadline = time.monotonic() + 25
    while port_closed(bidi_port):
        if firefox.poll() is not None or time.monotonic() > deadline:
            raise RuntimeError('Owned Firefox BiDi endpoint did not start')
        time.sleep(.2)
    for name in ['helpers.py', 'interaction-helpers.py', 'gesture-helpers.py']:
        exec(compile((HERE / name).read_text(), str(HERE / name), 'exec'))
    OUT['phase'] = PHASE
    OUT['sourceSHA256'] = before
    OUT['conditions'] = 'Actual native viewer and canonical engine in owned headless Firefox. Navigation helpers may scroll lesson navigation; all Builder construction/check controls use trusted pointer/keyboard input with no test scrolling or DOM focus.'
    if PHASE == 'layout':
        for embedded, width, height in [(True,390,760),(True,320,740),(True,1500,900),
                                         (False,390,760),(False,320,740),(False,1500,900)]:
            label = ('lesson' if embedded else 'standalone') + '-' + str(width)
            enter(embedded, width, height)
            initial = measure(label + '-initial', embedded)
            shot(label + '-initial.png')
            check(initial['answerVisibility']['fullyVisible'] and initial['bankVisibility']['fullyVisible'],
                  label + ' initial answer and bank automatically visible', initial)
            tile_id = builder_state(embedded)['bank'][0]
            no_scroll_click(tile_selector(tile_id), embedded)
            populated = measure(label + '-populated', embedded)
            shot(label + '-populated.png')
            print(json.dumps({'label':label,'helpHeight':populated['help']['height'],
                              'checkVisibility':populated['checkVisibility']}), flush=True)
            check(populated['checkVisibility']['fullyVisible'],
                  label + ' needed check action automatically visible after construction', populated['checkVisibility'])
            check(all(b['height'] >= 44 for b in populated['buttons']), label + ' editing actions retain44px targets', populated['buttons'])
            no_scroll_click('#check-answer', embedded)
            feedback = rectangle_visibility('#feedback', embedded)
            shot(label + '-feedback.png')
            check(feedback['fullyVisible'], label + ' feedback automatically visible', feedback)
    else:
        for embedded in [False, True]:
            enter(embedded, 1500, 1000)
            measure(('lesson' if embedded else 'standalone') + '-desktop', embedded)
            methods_flow(embedded)
    complete = True
    OUT['completed'] = True
except Exception:
    if 'OUT' not in globals():
        OUT = {'checks': [], 'solved': []}
    OUT['failure'] = traceback.format_exc()
    print(OUT['failure'], flush=True)
    try:
        shot(PHASE + '-failure.png')
    except Exception:
        pass
finally:
    if 'OUT' not in globals():
        OUT = {'checks': [], 'solved': []}
    OUT['phase'] = PHASE
    OUT['javascriptErrors'] = globals().get('js_errors', [])
    OUT['consoleWarningsAndErrors'] = [e['params'] for e in globals().get('all_events', [])
        if e.get('method') == 'log.entryAdded' and e.get('params', {}).get('level') in ('warn','error')]
    OUT['httpErrors'] = HTTP_ERRORS
    OUT['sourceUnchangedDuringRun'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == sha for p, sha in expected.items()}
    try:
        if 'finish' in globals():
            finish()
    except Exception as error:
        OUT['sessionCleanupError'] = repr(error)
    server.shutdown(); server.server_close()
    if firefox.poll() is None:
        actual_command = subprocess.check_output(['ps', '-p', str(firefox.pid), '-o', 'command='], text=True)
        assert str(profile) in actual_command and str(bidi_port) in actual_command and '/Firefox.app/Contents/MacOS/firefox' in actual_command, 'Owned PID command guard failed'
        firefox.terminate()
        try:
            firefox.wait(timeout=10)
        except subprocess.TimeoutExpired:
            firefox.kill(); firefox.wait(timeout=5)
    log.close()
    process['ownedFirefoxExited'] = firefox.poll() is not None
    process['bidiPortClosed'] = port_closed(bidi_port)
    process['serverPortClosed'] = port_closed(process['serverPort'])
    (HERE / (PHASE + '-cleanup.json')).write_text(json.dumps(process, indent=2) + '\n')
    (HERE / (PHASE + '-results.json')).write_text(json.dumps(OUT, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'phase':PHASE,'completed':complete,'checks':len(OUT['checks']),
                     'ownedFirefoxExited':process['ownedFirefoxExited'],'bidiPortClosed':process['bidiPortClosed'],
                     'serverPortClosed':process['serverPortClosed']}), flush=True)
if not complete:
    raise SystemExit(1)
