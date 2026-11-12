"""Definitions-only trusted gesture helpers; load after interaction-helpers.py.

These helpers never scroll/focus construction targets or mutate Builder state.
The sole page instrumentation is a temporary capture-phase event recorder.
"""


def _gesture_probe(selector=None, local_point=None, global_point=None, embedded=True):
    """Read frame-scaled geometry/hit tests without making a point reachable."""
    document_expression = B if embedded else 'document'
    return read('''(() => {
      const doc = ''' + document_expression + ''', game = doc.defaultView;
      const selector = ''' + json.dumps(selector) + ''';
      const element = selector ? doc.querySelector(selector) : null;
      if (selector && !element) return {ok:false,reason:'selector missing',selector};
      const plain = r => ({left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height});
      const description = e => e ? {tag:e.tagName,id:e.id || null,
        tileId:e.closest?.('[data-tile-id]')?.dataset.tileId || null,
        inAnswer:!!e.closest?.('#answer-zone'),inBank:!!e.closest?.('#bank-zone')} : null;
      const rect = element ? plain(element.getBoundingClientRect()) : null, chain = [];
      let win = game;
      while (win !== window) {
        const frame = win.frameElement, r = frame.getBoundingClientRect();
        const sx = r.width/frame.offsetWidth, sy = r.height/frame.offsetHeight;
        chain.push({frame,parent:win.parent,left:r.left+frame.clientLeft*sx,
          top:r.top+frame.clientTop*sy,sx,sy});
        win = win.parent;
      }
      const givenLocal = ''' + json.dumps(local_point) + ''', givenGlobal = ''' + json.dumps(global_point) + ''';
      let x, y;
      if (givenGlobal) {
        x=givenGlobal.x; y=givenGlobal.y;
        for (const f of [...chain].reverse()) {x=(x-f.left)/f.sx;y=(y-f.top)/f.sy;}
      } else if (givenLocal) {x=givenLocal.x;y=givenLocal.y;}
      else if (rect) {x=(rect.left+rect.right)/2;y=(rect.top+rect.bottom)/2;}
      else return {ok:false,reason:'point or selector required'};
      const local={x,y}, insideGame=x>=0 && y>=0 && x<game.innerWidth && y<game.innerHeight;
      const hit=insideGame ? doc.elementFromPoint(x,y) : null;
      let visibleGame=!!hit, reason=hit ? null : 'outside game viewport or no hit';
      const frames=[];
      let bounds=rect ? {...rect} : null;
      for (const f of chain) {
        x=f.left+x*f.sx;y=f.top+y*f.sy;
        if (bounds) bounds={left:f.left+bounds.left*f.sx,right:f.left+bounds.right*f.sx,
          top:f.top+bounds.top*f.sy,bottom:f.top+bounds.bottom*f.sy,
          width:bounds.width*f.sx,height:bounds.height*f.sy};
        const inside=x>=0 && y>=0 && x<f.parent.innerWidth && y<f.parent.innerHeight;
        const parentHit=inside ? f.parent.document.elementFromPoint(x,y) : null;
        frames.push({x,y,left:f.left,top:f.top,scaleX:f.sx,scaleY:f.sy,
          width:f.parent.innerWidth,height:f.parent.innerHeight,hit:description(parentHit),
          expectedFrameId:f.frame.id || null,visible:inside && parentHit===f.frame});
        if (!inside || parentHit!==f.frame) {visibleGame=false;reason='parent viewport/clipping/overlay';}
      }
      const globalInside=x>=0 && y>=0 && x<innerWidth && y<innerHeight;
      const topHit=globalInside ? document.elementFromPoint(x,y) : null;
      return {ok:true,selector,local,global:{x:Math.round(x),y:Math.round(y)},rect,
        globalRect:bounds,insideGame,visibleGame,globalInside,reason,hit:description(hit),
        topHit:description(topHit),selectorHit:!element || !!hit && (hit===element || element.contains(hit)),
        gameViewport:{width:game.innerWidth,height:game.innerHeight,scrollX:game.scrollX,scrollY:game.scrollY},
        topViewport:{width:innerWidth,height:innerHeight},frames};
    })()''')


def gesture_geometry(selector='#answer-zone', embedded=True):
    """Return current local/global rect, scales and center visibility; never scroll."""
    result = _gesture_probe(selector=selector, embedded=embedded)
    check(result['ok'], 'gesture geometry target exists: ' + selector, result)
    return result


def gesture_global_point(x, y, embedded=True):
    """Read whether an explicit top-viewport point is a visible game release."""
    return _gesture_probe(global_point={'x': round(x), 'y': round(y)}, embedded=embedded)


def _gesture_visible_local(point, embedded=True, selector=None):
    probe = _gesture_probe(selector=selector, local_point=point, embedded=embedded)
    if not (probe.get('ok') and probe['globalInside'] and probe['visibleGame'] and probe['selectorHit']):
        return None
    # Recheck the actual rounded coordinates sent to BiDi, including frame scales.
    actual = _gesture_probe(selector=selector, global_point=probe['global'], embedded=embedded)
    return actual if actual['globalInside'] and actual['visibleGame'] and actual['selectorHit'] else None


def _gesture_target(kind, embedded=True, answer_index=None, gap=12, global_point=None):
    """Choose a currently hit-testable endpoint, including four answer sides."""
    if global_point is not None:
        p = global_point if isinstance(global_point, dict) else dict(zip(('x','y'), global_point))
        result = gesture_global_point(p['x'], p['y'], embedded)
        check(result['ok'] and result['globalInside'], 'explicit gesture point is inside top viewport', result)
        return result
    aliases = {'answerinside':'inside','answer':'inside','moleculeiframe':'molecule',
               'outside-left':'left','outside-right':'right','outside-top':'top','outside-bottom':'bottom'}
    kind = aliases.get(kind, kind)
    answer = gesture_geometry('#answer-zone', embedded)
    r = answer['rect']
    candidates, selector = [], None
    if kind in ('left','right','top','bottom'):
        for fraction in (.5,.25,.75):
            x = r['left'] + r['width']*fraction
            y = r['top'] + r['height']*fraction
            if kind == 'left': x = r['left']-gap
            if kind == 'right': x = r['right']+gap
            if kind == 'top': y = r['top']-gap
            if kind == 'bottom': y = r['bottom']+gap
            candidates.append({'x':x,'y':y})
    elif kind == 'inside':
        selector = '#answer-zone'
        items = _builder_read('''[...document.querySelector('#answer-tiles').children].map(e=>{
          const r=e.getBoundingClientRect();return {left:r.left,right:r.right,center:r.left+r.width/2};})''', embedded)
        if answer_index is None:
            candidates = [{'x':r['left']+r['width']*f,'y':r['top']+r['height']/2} for f in (.5,.25,.75)]
        else:
            check(isinstance(answer_index,int) and 0 <= answer_index <= len(items),
                  'requested drop index exists before removal', {'index':answer_index,'items':items})
            left = r['left']+3 if not answer_index else items[answer_index-1]['center']+.75
            right = r['right']-3 if answer_index == len(items) else items[answer_index]['center']-.75
            x = max(r['left']+3,left) + (min(r['right']-3,right)-max(r['left']+3,left))/2
            check(max(r['left']+3,left) < min(r['right']-3,right),
                  'requested answer index currently visible without scrolling', {'left':left,'right':right,'rect':r})
            candidates = [{'x':x,'y':r['top']+r['height']/2}]
    elif kind in ('bank','molecule'):
        selector = '#bank-zone' if kind == 'bank' else '#molecule-viewer'
        bounds = gesture_geometry(selector, embedded)['rect']
        candidates = [{'x':bounds['left']+bounds['width']*fx,'y':bounds['top']+bounds['height']*fy}
                      for fy in (.5,.25,.75) for fx in (.5,.25,.75)]
    else:
        raise ValueError('Unknown gesture endpoint: ' + str(kind))
    for candidate in candidates:
        result = _gesture_visible_local(candidate, embedded, selector)
        if result:
            result['kind'] = kind
            return result
    check(False, 'gesture endpoint visible through viewport/dialog hit tests: '+kind,
          {'answer':answer,'candidates':candidates,'selector':selector})


def _gesture_observe_start(embedded=True):
    """Observe real events; no event dispatch, focus, scroll or Builder mutation."""
    return _builder_read('''(() => {
      window.__nameleculeGestureEvidence?.stop();
      const records=[], types=['pointerdown','pointermove','pointerup','pointercancel',
        'gotpointercapture','lostpointercapture','click'];
      const listener=event=>{
        const x=event.clientX,y=event.clientY,hit=document.elementFromPoint(x,y);
        const r=document.getElementById('answer-zone').getBoundingClientRect();
        let gx=x,gy=y,view=window,visible=x>=0 && y>=0 && x<innerWidth && y<innerHeight && !!hit;
        const frames=[];
        try {while(view!==view.parent){const frame=view.frameElement,b=frame.getBoundingClientRect();
          gx=b.left+(frame.clientLeft+gx)*b.width/frame.offsetWidth;
          gy=b.top+(frame.clientTop+gy)*b.height/frame.offsetHeight;view=view.parent;
          const parentHit=view.document.elementFromPoint(gx,gy);
          const ok=gx>=0 && gy>=0 && gx<view.innerWidth && gy<view.innerHeight && parentHit===frame;
          frames.push({x:gx,y:gy,visible:ok,hit:parentHit?.id || parentHit?.tagName || null});visible=visible&&ok;
        }}catch(_){visible=false;}
        const items=[...document.getElementById('answer-tiles').children];
        let index=items.findIndex(e=>{const q=e.getBoundingClientRect();return x<q.left+q.width/2;});
        records.push({type:event.type,trusted:event.isTrusted,pointerId:event.pointerId ?? null,
          pointerType:event.pointerType || null,primary:event.isPrimary ?? null,button:event.button,
          x,y,globalX:gx,globalY:gy,targetId:event.target?.closest?.('[data-tile-id]')?.dataset.tileId || null,
          hit:hit?.id || hit?.tagName || null,hitInAnswer:!!hit?.closest('#answer-zone'),
          hitInBank:!!hit?.closest('#bank-zone'),hitMoleculeFrame:hit===document.getElementById('molecule-viewer'),
          visibleGame:visible,insideAnswer:x>=r.left && x<=r.right && y>=r.top && y<=r.bottom,
          answerRect:{left:r.left,right:r.right,top:r.top,bottom:r.bottom},
          dropIndex:index<0?items.length:index,scrollY,frames,time:event.timeStamp});
      };
      types.forEach(t=>document.addEventListener(t,listener,true));
      window.__nameleculeGestureEvidence={records,stop:()=>types.forEach(t=>document.removeEventListener(t,listener,true))};
      return true;
    })()''', embedded)


def _gesture_observe_stop(embedded=True):
    return _builder_read('''(() => {const e=window.__nameleculeGestureEvidence;
      e?.stop();const result=e?.records || [];delete window.__nameleculeGestureEvidence;return result;})()''', embedded)


def _gesture_actions(actions, pointer_type='mouse'):
    check(pointer_type in ('mouse','touch'), 'supported trusted gesture pointer type', pointer_type)
    if pointer_type == 'mouse':
        return _pointer_actions(actions)
    return call('input.performActions', {'context':ctx,'actions':[
        {'type':'pointer','id':'workspace-touch','parameters':{'pointerType':'touch'},'actions':actions}]})


def gesture_drag(tile_id, endpoint='bottom', embedded=True, pointer_type='mouse',
                 origin='answer', answer_index=None, global_point=None, via=None,
                 outside_side='bottom', gap=12, expected_order=None, finish='up'):
    """Run a trusted >8px drag and verify exact answer/bank ID transitions.

    endpoint: left/right/top/bottom, inside, reentry, bank, molecule, or global.
    origin: answer or bank. via: optional list of top-viewport {x,y} waypoints.
    finish: up, releaseActions, or nativeCancel (unsupported is reported honestly).
    expected_order optionally asserts a caller-specified exact final answer order.
    """
    check(origin in ('answer','bank'), 'gesture source container supported', origin)
    check(finish in ('up','releaseActions','nativeCancel'), 'gesture completion supported', finish)
    before = builder_state(embedded)
    check(tile_id in before[origin] and tile_id not in before['bank' if origin == 'answer' else 'answer'],
          'gesture source is exact rendered '+origin+' ID', {'id':tile_id,'state':before})
    selector = '#'+('answer-tiles' if origin == 'answer' else 'bank-tiles')+' [data-tile-id='+json.dumps(tile_id)+']'
    source = _visible_point(selector, embedded)
    reentry = endpoint == 'reentry'
    target = _gesture_target('inside' if reentry else endpoint, embedded, answer_index, gap, global_point)
    path = list(via or [])
    if reentry:
        excursion = _gesture_target(outside_side, embedded, gap=gap)
        path.append(excursion['global'])
    # Force a real activation excursion even when an inside drop returns to source.
    if not path and abs(target['global']['x']-source['x'])+abs(target['global']['y']-source['y']) < 12:
        for dx,dy in ((18,0),(-18,0),(0,18),(0,-18)):
            probe=gesture_global_point(source['x']+dx,source['y']+dy,embedded)
            if probe['globalInside'] and probe['visibleGame']:
                path.append(probe['global']);break
        check(bool(path), 'visible activation excursion exists without scrolling', source)
    path.append(target['global'])
    for point in path:
        check(0 <= point['x'] < target['topViewport']['width'] and 0 <= point['y'] < target['topViewport']['height'],
              'trusted path stays inside top viewport (BiDi cannot release outside it)', point)
    actions=[{'type':'pointerMove','x':source['x'],'y':source['y'],'duration':0},
             {'type':'pointerDown','button':0}]
    previous={'x':source['x'],'y':source['y']}
    for point in path:
        for step in range(1,7):
            actions.append({'type':'pointerMove','duration':40,
                            'x':round(previous['x']+(point['x']-previous['x'])*step/6),
                            'y':round(previous['y']+(point['y']-previous['y'])*step/6)})
        previous=point
    _gesture_observe_start(embedded)
    protocol_error = None
    try:
        _gesture_actions(actions,pointer_type)
        if finish == 'up':
            _gesture_actions([{'type':'pointerUp','button':0}],pointer_type)
        elif finish == 'releaseActions':
            call('input.releaseActions',{'context':ctx})
        else:
            try:
                _gesture_actions([{'type':'pointerCancel'}],pointer_type)
            except RuntimeError as error:
                protocol_error=str(error)
                call('input.releaseActions',{'context':ctx})
        pause(.7)
    except Exception:
        try: call('input.releaseActions',{'context':ctx})
        finally: _gesture_observe_stop(embedded)
        raise
    events=_gesture_observe_stop(embedded)
    after=builder_state(embedded)
    downs=[e for e in events if e['type']=='pointerdown' and e['trusted']]
    check(len(downs)==1 and downs[0]['targetId']==tile_id and downs[0]['pointerType']==pointer_type and downs[0]['primary'],
          'trusted primary pointerdown reached exact source ID', events)
    pointer_id=downs[0]['pointerId']
    relevant=[e for e in events if e.get('pointerId')==pointer_id and e['trusted']]
    moved=max([((e['x']-downs[0]['x'])**2+(e['y']-downs[0]['y'])**2)**.5
               for e in relevant if e['type']=='pointermove'] or [0])
    cancelled=any(e['type']=='pointercancel' for e in relevant)
    ups=[e for e in relevant if e['type']=='pointerup']
    check(moved>=8 or cancelled, 'trusted gesture activated beyond 8px or was natively cancelled', {'distance':moved,'events':events})
    check(bool(ups) or cancelled, 'trusted pointer terminal event observed', events)
    release=ups[-1] if ups else None
    expected=before['answer'][:]
    removed=False
    # Approved user contract: a completed release inside the browser viewport
    # places only on the visibly hit answer; any other release removes a placed
    # tile, including parent headers/outside-game-frame browser content.
    in_browser = release and 0 <= release['globalX'] < target['topViewport']['width'] and 0 <= release['globalY'] < target['topViewport']['height']
    if not cancelled and release and moved>=8 and in_browser:
        if release['visibleGame'] and release['insideAnswer'] and release['hitInAnswer']:
            index=release['dropIndex']
            if tile_id in expected:
                old=expected.index(tile_id);expected.remove(tile_id)
                if old<index:index-=1
            expected.insert(max(0,min(index,len(expected))),tile_id)
        elif origin=='answer':
            expected.remove(tile_id);removed=True
    if finish=='up' and not cancelled:
        check(abs(release['globalX']-target['global']['x'])<=2 and abs(release['globalY']-target['global']['y'])<=2,
              'actual trusted release reached requested global endpoint', {'release':release,'target':target})
        if reentry or endpoint in ('inside','answer','answerinside'):
            check(release['visibleGame'] and release['insideAnswer'] and release['hitInAnswer'],
                  'actual trusted release returned inside visible answer', release)
            if answer_index is not None:
                check(release['dropIndex']==answer_index, 'actual release reached requested pre-removal answer index',
                      {'requested':answer_index,'release':release})
            if reentry:
                check(any(e['type']=='pointermove' and e['visibleGame'] and not e['insideAnswer'] for e in relevant),
                      'trusted reentry path actually left current answer before returning', relevant)
        elif global_point is None:
            check(release['visibleGame'] and not release['insideAnswer'],
                  'actual trusted release outside current answer in visible game', release)
            side={'outside-left':'left','outside-right':'right','outside-top':'top','outside-bottom':'bottom'}.get(endpoint,endpoint)
            rect=release['answerRect']
            side_ok={'left':release['x']<rect['left'],'right':release['x']>rect['right'],
                     'top':release['y']<rect['top'],'bottom':release['y']>rect['bottom']}
            if side in side_ok:check(side_ok[side], 'actual release crossed requested answer '+side+' side', release)
            if endpoint=='bank':check(release['hitInBank'], 'actual release hit visible bank content', release)
            if endpoint in ('molecule','moleculeiframe'):
                check(release['hitMoleculeFrame'], 'actual release hit visible molecule iframe', release)
    check(after['answer']==expected, 'trusted gesture exact answer order', {'expected':expected,'actual':after['answer']})
    if expected_order is not None:
        check(after['answer']==expected_order, 'caller-specified exact gesture order', {'expected':expected_order,'actual':after['answer']})
    check(sorted(before['answer']+before['bank'])==sorted(after['answer']+after['bank']) and
          len(set(after['answer']+after['bank']))==len(after['answer']+after['bank']),
          'gesture preserved every genuine tile ID exactly once', {'before':before,'after':after})
    check(sorted(after['bank'])==sorted(t for t in before['answer']+before['bank'] if t not in expected),
          'gesture bank exact ID membership', after['bank'])
    if removed:
        check(after['selected'] is None and after['focusedInBank'] and after['focusedId']==tile_id and after['feedback']['hidden'],
              'outside removal cleared selection/feedback and focused exact returned bank tile', after)
    limits=[]
    if finish!='up' and not cancelled:
        limits.append('No trusted pointercancel observed; releaseActions/nativeCancel fallback is not cancellation evidence.')
    return {'before':before,'after':after,'source':source,'target':target,'path':path,
            'pointerType':pointer_type,'finish':finish,'events':events,'release':release,
            'actualDistance':moved,'expectedAnswer':expected,'removed':removed,
            'nativeCancelSupported':cancelled,'protocolError':protocol_error,'limits':limits}
