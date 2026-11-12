"""Actual gesture matrix definitions, loaded after trusted helpers."""

def run_gesture_matrix(embedded):
    label='lesson' if embedded else 'standalone'
    OUT.setdefault('gestureMatrix',[])
    def add(tid):
        no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']',embedded)
    def record(result,case):
        result['case']=label+' '+case;OUT['gestureMatrix'].append(result)
    tid=builder_state(embedded)['bank'][0]
    for side in ['left','right','top','bottom','bank','moleculeiframe']:
        add(tid)
        record(gesture_drag(tid,side,embedded),'remove '+side)
        check(builder_state(embedded)['answer']==[],label+' drag-out removal returns to empty answer')
    ids=builder_state(embedded)['bank'][:2]
    add(ids[0]);add(ids[1])
    style=_builder_read('''(() => {const b=document.getElementById('remove-tile'),h=document.getElementById('answer-help'),r=b.getBoundingClientRect();return {height:r.height,fontSize:getComputedStyle(b).fontSize,weight:getComputedStyle(b).fontWeight,helpFont:getComputedStyle(h).fontSize,keycaps:[...h.querySelectorAll('kbd')].map(e=>e.textContent),label:document.querySelector('.selected-tile').textContent}})()''',embedded)
    check(style['height']>=44 and float(style['weight'])>=700 and float(style['fontSize'][:-2])>=14,label+' clearer44px bold controls',style)
    check(len(style['keycaps'])==4 and 'Επιλεγμένο:' in style['label'],label+' explicit selected tile and keyboard methods',style)
    record(gesture_drag(ids[1],'inside',embedded,answer_index=0,expected_order=[ids[1],ids[0]]),'inside reorder')
    record(gesture_drag(ids[1],'reentry',embedded,answer_index=2,expected_order=ids),'exit then reenter')
    key_selected('ArrowLeft',embedded);key_selected('ArrowRight',embedded)
    key_selected('Backspace',embedded)
    key_add_focused(embedded)
    no_scroll_click('#remove-tile',embedded)
    no_scroll_click('#answer-tiles button',embedded)
    no_scroll_click('#remove-tile',embedded)
    check(builder_state(embedded)['answer']==[],label+' accessible buttons and keyboard return exact tiles')
    add(tid)
    before=builder_state(embedded)
    source=_visible_point('#answer-tiles [data-tile-id='+json.dumps(tid)+']',embedded)
    _pointer_actions([{'type':'pointerMove','x':source['x'],'y':source['y'],'duration':0},{'type':'pointerDown','button':0},
      {'type':'pointerMove','x':source['x']+3,'y':source['y'],'duration':50},{'type':'pointerUp','button':0}])
    pause(.7)
    check(builder_state(embedded)['answer']==before['answer'],label+' sub8px movement remains click/selection')
    if embedded:
        header=read('''(() => {const r=document.querySelector('.nl-quiz-dialog-header').getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})()''')
        record(gesture_drag(tid,'global',True,global_point=header,expected_order=before['answer']),'release over parent header cancels')
    # Exercise the actual cancel handler after a real captured drag. This event
    # is explicitly synthetic; it is not evidence of native device cancellation.
    source=_visible_point('#answer-tiles [data-tile-id='+json.dumps(tid)+']',embedded)
    target=_gesture_target('bottom',embedded)
    _gesture_observe_start(embedded)
    _pointer_actions([{'type':'pointerMove','x':source['x'],'y':source['y'],'duration':0},{'type':'pointerDown','button':0},
      {'type':'pointerMove','x':target['global']['x'],'y':target['global']['y'],'duration':250}])
    check(_builder_read('!!document.querySelector(".touch-ghost")',embedded),label+' real active drag before synthetic cancellation')
    _builder_read('''(() => {const e=__nameleculeGestureEvidence.records.find(e=>e.type==='pointerdown'&&e.trusted);const b=document.querySelector('#answer-tiles [data-tile-id='+CSS.escape(e.targetId)+']');return b.dispatchEvent(new PointerEvent('pointercancel',{pointerId:e.pointerId,pointerType:e.pointerType,bubbles:true}))})()''',embedded)
    _pointer_actions([{'type':'pointerUp','button':0}]);pause(.7)
    events=_gesture_observe_stop(embedded)
    check(builder_state(embedded)['answer']==before['answer'] and not _builder_read('!!document.querySelector(".touch-ghost")',embedded),label+' synthetic cancel handler preserves answer and cleans actual drag')
    OUT.setdefault('syntheticCancelEvidence',[]).append({'context':label,'events':events,'nativeDeviceCancellation':False})
    record(gesture_drag(tid,'bottom',embedded,finish='nativeCancel'),'native cancellation capability probe')
    if tid in builder_state(embedded)['answer']:
        record(gesture_drag(tid,'bottom',embedded),'cleanup after native cancel')
    # A bank-origin outside drop keeps the unused tile, even with real touch.
    record(gesture_drag(tid,'bottom',embedded,pointer_type='touch',origin='bank',expected_order=[]),'touch bank outside no-op')
    add(tid)
    record(gesture_drag(tid,'bottom',embedded,pointer_type='touch',expected_order=[]),'touch placed outside removal')
    # A wrong check must not leave stale feedback after drag-out correction.
    add(tid);no_scroll_click('#check-answer',embedded)
    check(not builder_state(embedded)['feedback']['hidden'] and not builder_state(embedded)['feedback']['success'],label+' partial answer rejected before drag correction')
    record(gesture_drag(tid,'bottom',embedded),'wrong-feedback correction')
    check(builder_state(embedded)['answer']==[] and builder_state(embedded)['feedback']['hidden'],label+' matrix ends empty with cleared feedback')
    shot(label+'-guidance.png')
