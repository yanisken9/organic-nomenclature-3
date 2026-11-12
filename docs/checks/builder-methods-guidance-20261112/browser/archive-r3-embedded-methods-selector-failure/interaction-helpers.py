"""Trusted UI helpers. Load after helpers.py; definitions never scroll a target."""


def _builder_read(expression, embedded=True):
    return bread(expression) if embedded else read(expression)


def builder_state(embedded=True):
    """Read actual rendered IDs, focus, selection, feedback and observed load."""
    return _builder_read('''(() => {
      const ids = selector => [...document.querySelectorAll(selector)].map(e => e.dataset.tileId);
      const feedback = document.getElementById('feedback');
      return {
        answer: ids('#answer-tiles button'), bank: ids('#bank-tiles button'),
        selected: document.querySelector('#answer-tiles [aria-pressed="true"]')?.dataset.tileId || null,
        focusedId: document.activeElement?.dataset.tileId || null,
        focusedInAnswer: !!document.activeElement?.closest('#answer-tiles'),
        focusedInBank: !!document.activeElement?.closest('#bank-tiles'),
        candidate: document.getElementById('candidate-name').textContent,
        feedback: {hidden: feedback.hidden, success: feedback.classList.contains('success'), text: feedback.textContent},
        load: typeof __lessonLoad === 'undefined' ? null : __lessonLoad,
        scrollY, answerScrollLeft: document.getElementById('answer-zone').scrollLeft
      };
    })()''', embedded)


def correct_tile_ids(embedded=True):
    """Derive exact IDs only from the genuine observed lesson round/bank seed."""
    state = builder_state(embedded)
    load = state['load']
    check(bool(load and load.get('round')), 'genuine lesson load available', load)
    round_data = load['round']
    check(round_data['moleculeId'] == load['moleculeId'], 'lesson load molecule identity')
    bank = _builder_read('NameleculeNameBuilderEngine.createBank(__lessonLoad.round,{seed:__lessonLoad.bankSeed})', embedded)
    check(sorted(state['answer'] + state['bank']) == sorted(tile['id'] for tile in bank),
          'rendered tile IDs match genuine seeded bank')
    used, result = set(), []
    for piece in round_data['pieces']:
        matches = [tile for tile in bank if tile['id'] not in used
                   and tile['text'] == piece['text']
                   and tile.get('separatorBefore') == piece.get('separatorBefore')]
        check(bool(matches), 'genuine piece has unused matching tile', piece)
        tile_id = matches[0]['id']
        used.add(tile_id)
        result.append(tile_id)
    return result


def _visible_point(selector, embedded=True):
    """Read a center point through frame borders/scales; reject clipping/overlays."""
    expression = bel(selector) if embedded else 'document.querySelector(' + json.dumps(selector) + ')'
    point = read('''(() => {
      const element = ''' + expression + ''';
      if (!element) return {ok:false, reason:'target missing'};
      if (element.disabled) return {ok:false, reason:'target disabled'};
      const r = element.getBoundingClientRect();
      if (!r.width || !r.height) return {ok:false, reason:'target has no area'};
      let x = r.left + r.width / 2, y = r.top + r.height / 2;
      const localX = x, localY = y;
      let bounds = {left:r.left, top:r.top, right:r.right, bottom:r.bottom};
      let win = element.ownerDocument.defaultView, expected = element, fullyVisible = true;
      const frames = [];
      while (true) {
        const inside = x >= 0 && y >= 0 && x < win.innerWidth && y < win.innerHeight;
        const hit = inside ? win.document.elementFromPoint(x,y) : null;
        if (!inside || !hit || !(hit === expected || expected.contains(hit))) {
          return {ok:false, reason:inside?'target center occluded':'target center outside viewport',
            x,y,hit:hit?.id || hit?.className || null,frames};
        }
        fullyVisible = fullyVisible && bounds.left >= 0 && bounds.top >= 0 &&
          bounds.right <= win.innerWidth && bounds.bottom <= win.innerHeight;
        frames.push({width:win.innerWidth,height:win.innerHeight,scrollY:win.scrollY});
        if (win === window) break;
        const frame = win.frameElement, f = frame.getBoundingClientRect();
        const sx = f.width / frame.offsetWidth, sy = f.height / frame.offsetHeight;
        const left = f.left + frame.clientLeft*sx, top = f.top + frame.clientTop*sy;
        x = left + x*sx; y = top + y*sy;
        bounds = {left:left+bounds.left*sx,top:top+bounds.top*sy,
          right:left+bounds.right*sx,bottom:top+bounds.bottom*sy};
        expected = frame; win = win.parent;
      }
      const usable = {left:0,top:0,right:innerWidth,bottom:innerHeight};
      const dialog = document.getElementById('nlQuizDialog');
      const ownHeaderControl = element.ownerDocument === document && !!element.closest('.nl-quiz-dialog-header');
      if (dialog?.open && dialog.contains(expected) && !ownHeaderControl) {
        const d = dialog.getBoundingClientRect();
        const header = dialog.querySelector('.nl-quiz-dialog-header')?.getBoundingClientRect();
        usable.left = Math.max(0,d.left+dialog.clientLeft);
        usable.right = Math.min(innerWidth,d.left+dialog.clientLeft+dialog.clientWidth);
        usable.top = Math.max(0,d.top+dialog.clientTop,header?.bottom || 0);
        usable.bottom = Math.min(innerHeight,d.top+dialog.clientTop+dialog.clientHeight);
      }
      fullyVisible = fullyVisible && bounds.left >= usable.left && bounds.right <= usable.right &&
        bounds.top >= usable.top && bounds.bottom <= usable.bottom;
      if (x < usable.left || x >= usable.right || y < usable.top || y >= usable.bottom)
        return {ok:false,reason:'target center outside usable dialog/window',x,y,usable,bounds,frames};
      return {ok:true,x:Math.round(x),y:Math.round(y),localX,localY,fullyVisible,usable,bounds,frames,
        dialogScrollTop:dialog?.open?dialog.scrollTop:null};
    })()''')
    check(point['ok'], 'target reachable without test scrolling: ' + selector, point)
    return point


def _pointer_actions(actions):
    return call('input.performActions', {'context': ctx, 'actions': [
        {'type': 'pointer', 'id': 'workspace-pointer', 'parameters': {'pointerType': 'mouse'},
         'actions': actions}]})


def no_scroll_click(selector, embedded=True):
    """Click the currently reachable center with trusted input; allow app reveal."""
    point = _visible_point(selector, embedded)
    _pointer_actions([{'type': 'pointerMove', 'x': point['x'], 'y': point['y'], 'duration': 0},
                      {'type': 'pointerDown', 'button': 0}, {'type': 'pointerUp', 'button': 0}])
    pause(.7)
    return point


def drag_tile(tile_id, embedded=True):
    """Drag a fully visible genuine bank tile to the fully visible answer center."""
    before = builder_state(embedded)
    check(tile_id in before['bank'] and tile_id not in before['answer'], 'drag source is exact bank ID', tile_id)
    source = _visible_point('#bank-tiles [data-tile-id=' + json.dumps(tile_id) + ']', embedded)
    target = _visible_point('#answer-zone', embedded)
    check(source['fullyVisible'] and target['fullyVisible'], 'drag endpoints fully visible before input',
          {'source': source, 'target': target})
    index = _builder_read('''(() => {
      const items = [...document.querySelector('#answer-tiles').children];
      const index = items.findIndex(e => {const r=e.getBoundingClientRect();return ''' +
      json.dumps(target['localX']) + ''' < r.left+r.width/2});
      return index < 0 ? items.length : index;
    })()''', embedded)
    actions = [{'type': 'pointerMove', 'x': source['x'], 'y': source['y'], 'duration': 0},
               {'type': 'pointerDown', 'button': 0}]
    for step in range(1, 10):
        fraction = step / 9
        actions.append({'type': 'pointerMove', 'duration': 65,
                        'x': round(source['x'] + (target['x'] - source['x']) * fraction),
                        'y': round(source['y'] + (target['y'] - source['y']) * fraction)})
    actions.append({'type': 'pointerUp', 'button': 0})
    _pointer_actions(actions)
    pause(.7)
    after = builder_state(embedded)
    expected = before['answer'][:index] + [tile_id] + before['answer'][index:]
    check(after['answer'] == expected and tile_id not in after['bank'],
          'trusted drag placed exact ID at actual drop position', {'expected': expected, 'actual': after['answer']})
    return {'before': before, 'after': after, 'source': source, 'target': target}


def _trusted_key(key):
    values = {'ArrowLeft': '\ue012', 'ArrowRight': '\ue014', 'Delete': '\ue017',
              'Backspace': '\ue003', 'Enter': '\ue007'}
    check(key in values, 'supported trusted key', key)
    return call('input.performActions', {'context': ctx, 'actions': [
        {'type': 'key', 'id': 'workspace-keyboard', 'actions': [
            {'type': 'keyDown', 'value': values[key]}, {'type': 'keyUp', 'value': values[key]}]}]})


def key_selected(key, embedded=True):
    """Reorder/delete the already focused selected tile and verify exact IDs."""
    check(key in ('ArrowLeft', 'ArrowRight', 'Delete', 'Backspace'), 'supported selected-tile key', key)
    before = builder_state(embedded)
    tile_id = before['selected']
    check(bool(tile_id and before['focusedInAnswer'] and before['focusedId'] == tile_id),
          'selected answer tile already has actual keyboard focus', before)
    expected = before['answer'][:]
    index = expected.index(tile_id)
    if key in ('ArrowLeft', 'ArrowRight'):
        other = index + (-1 if key == 'ArrowLeft' else 1)
        check(0 <= other < len(expected), 'keyboard move has actual neighboring tile', before)
        expected[index], expected[other] = expected[other], expected[index]
    else:
        expected.remove(tile_id)
    _trusted_key(key)
    pause(.7)
    after = builder_state(embedded)
    check(after['answer'] == expected, 'trusted ' + key + ' changed exact answer IDs',
          {'expected': expected, 'actual': after['answer']})
    if key in ('Delete', 'Backspace'):
        check(tile_id in after['bank'] and after['focusedInBank'] and after['focusedId'] == tile_id,
              'deleted exact tile returned to bank with focus', after)
    else:
        check(after['selected'] == tile_id and after['focusedId'] == tile_id and after['focusedInAnswer'],
              'reordered exact tile retains selection and focus', after)
    return {'before': before, 'after': after}


def key_add_focused(embedded=True):
    """Press Enter on an already focused bank tile; never move focus or scroll."""
    before = builder_state(embedded)
    tile_id = before['focusedId']
    check(bool(tile_id and before['focusedInBank'] and tile_id in before['bank']),
          'actual keyboard focus already on bank tile', before)
    _trusted_key('Enter')
    pause(.7)
    after = builder_state(embedded)
    check(after['answer'] == before['answer'] + [tile_id] and tile_id not in after['bank'],
          'trusted Enter added exact focused bank ID', after)
    return {'before': before, 'after': after}
