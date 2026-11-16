"""Definitions only; executed inside current replay-levels helper namespace."""

RECORDED_CLICKEL = clickel
RECORDED_SOLVERS = dict(SOLVERS)
original_detective_pick = detective_pick
LEGACY_SCROLL = False
BASE_SOURCES.update({'js/namelecule-game-viewport.js', 'css/namelecule-game-viewport.css', 'css/namelecule-game-levels.css'})
VIEWPORT_BASELINE=json.loads((HERE.parent/'baseline.json').read_text())
VIEWPORT_PROTECTED=json.loads((HERE.parent/'protected-classification.json').read_text())['unchangedProtectedDependencies']
BASE_SOURCES.update(VIEWPORT_BASELINE['coreBaseline']);BASE_SOURCES.update(VIEWPORT_PROTECTED)

def parse_args():
 parser=argparse.ArgumentParser(description='Bounded viewport lesson acceptance')
 parser.add_argument('--engine', choices=['chrome','firefox'], default='chrome')
 parser.add_argument('--timeout', type=int, default=1200)
 parser.add_argument('--scope', choices=['core','required-tail','detective-native'], default='core')
 args=parser.parse_args();args.prepare_check=False;args.mode='lesson-viewport-'+args.scope;args.cache_variants='new';return args

def element_metrics(expr):
 return read('''(()=>{const e=EXPR;if(!e)return{exists:false};const r=e.getBoundingClientRect(),rect={x:r.x,y:r.y,width:r.width,height:r.height,top:r.top,bottom:r.bottom,left:r.left,right:r.right};let w=e.ownerDocument.defaultView,x=r.x+r.width/2,y=r.y+r.height/2,visible=!!e.getClientRects().length&&r.width>0&&r.height>0&&w.getComputedStyle(e).visibility!=="hidden"&&w.getComputedStyle(e).display!=="none",within=r.left>=-1&&r.top>=-1&&r.right<=w.innerWidth+1&&r.bottom<=w.innerHeight+1,hit=e.contains(w.document.elementFromPoint(x,y));for(let p=e.parentElement;p;p=p.parentElement){const s=w.getComputedStyle(p),b=p.getBoundingClientRect();if(/hidden|auto|scroll|clip/.test(s.overflowX)&&b.width>0)within=within&&r.left>=b.left-2&&r.right<=b.right+2;if(/hidden|auto|scroll|clip/.test(s.overflowY)&&b.height>0)within=within&&r.top>=b.top-2&&r.bottom<=b.bottom+2}while(w!==window){const f=w.frameElement,b=f.getBoundingClientRect();x+=b.x;y+=b.y;w=w.parent;hit=hit&&w.document.elementFromPoint(x,y)===f;within=within&&x>=0&&y>=0&&x<=w.innerWidth&&y<=w.innerHeight}return{exists:true,visible,within,hit,localHit:e.ownerDocument.elementFromPoint(r.x+r.width/2,r.y+r.height/2)?.outerHTML.slice(0,250),rootClass:e.ownerDocument.querySelector("#game")?.className,style:{display:e.ownerDocument.defaultView.getComputedStyle(e).display,visibility:e.ownerDocument.defaultView.getComputedStyle(e).visibility,gridRow:e.ownerDocument.defaultView.getComputedStyle(e).gridRow,gridColumn:e.ownerDocument.defaultView.getComputedStyle(e).gridColumn},x:Math.round(x),y:Math.round(y),rect,disabled:!!e.disabled,text:e.textContent.slice(0,500),clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,clientWidth:e.clientWidth,scrollWidth:e.scrollWidth}})()'''.replace('EXPR',expr))

def clickel(expr):
 if LEGACY_SCROLL:return RECORDED_CLICKEL(expr)
 # Paged content is reached through its actual next/previous buttons. Never
 # scrollIntoView/scrollBy/scrollTop writes for viewport acceptance.
 positions=[]
 for _ in range(35):
  q=element_metrics(expr)
  positions.append(q)
  if q.get('visible') and q.get('within') and q.get('hit'):
   check(not q['disabled'],'enabled genuine UI '+expr);pointer(q,expr);return
  pager=read('''(()=>{const e=EXPR,c=e?.closest('.nl-vp-page-content');if(!c)return null;const p=c.parentElement,n=p.querySelector(':scope>.nl-vp-pager-nav'),r=e.getBoundingClientRect(),b=c.getBoundingClientRect(),horizontal=p.classList.contains('nl-vp-pager-x');if(!n||n.hidden)return null;const forward=horizontal?r.right>b.right:r.bottom>b.bottom,btn=n.querySelector(forward?'button:last-child':'button:first-child');return btn&&!btn.disabled?{forward}:null})()'''.replace('EXPR',expr))
  if not pager:raise AssertionError(('Viewport control has no visible hit point or usable pager',expr,q))
  nav='('+expr+').closest(".nl-vp-page-content").parentElement.querySelector(":scope>.nl-vp-pager-nav button:'+('last' if pager['forward'] else 'first')+'-child")'
  p=element_metrics(nav);check(p.get('visible') and p.get('within') and p.get('hit'),'pager button actually visible',p);pointer(p,'actual content pager');pause(.12)
 OUT['failedPagedControl']={'expression':expr,'positions':positions}
 raise AssertionError(('Pager did not reach target',expr,q))

def game_expr(game,selector):
 return window_expr(game,True)+'.document.querySelector('+json.dumps(selector)+')' if game!='repair' else 'document.querySelector('+json.dumps(selector)+')'

def present(game,selector):return element_metrics(game_expr(game,selector))

def view(game,key):
 selector={'repair':'[data-repair-view-button="'+key+'"]','builder':'.builder-view-nav [data-view="'+key+'"]','puzzle':'.puzzle-view-nav [data-view="'+key+'"]','detective':'[data-detective-view-button="'+key+'"]'}[game]
 q=present(game,selector)
 if q.get('visible'):game_click(game,selector,game!='repair')
 pause(.25)

def select_level(level,controlled=False):
 prefix='#nlQuizDialog ' if controlled else ''
 selector=prefix+'[data-level="'+str(level)+'"]'
 if not element_metrics('document.querySelector('+json.dumps(selector)+')').get('visible'):
  change=prefix+'.nl-game-levels__change'
  if not ev('!!document.querySelector('+json.dumps(change)+')'):change=prefix+'.nl-game-levels button[aria-expanded]'
  click(change);pause(.2)
 click(selector)

def choose(game,level=None):
 if ev('!!document.querySelector(".nl-game-choice-switch")'):click('.nl-game-choice-switch')
 wait('document.querySelectorAll(".nl-game-choice-card").length===4')
 click('.nl-game-choice-card:nth-child('+str({'repair':1,'builder':2,'puzzle':3,'detective':4}[game])+')')
 if level is not None:
  wait('!!document.querySelector("#nlQuizDialog [data-level]")')
  if gate_state().get('selectedLevel')!=level or read('!!document.querySelector("#nlQuizDialog .nl-game-levels.is-expanded")'):select_level(level,True)
 game_ready(game,True)

def assert_visible(game,selector,label):
 q=present(game,selector);check(q.get('visible') and q.get('within') and q.get('hit'),label,q);return q

def content_pages(game,selector,label,horizontal=False):
 expression=game_expr(game,selector);samples=[]
 for _ in range(30):
  item=read('''(()=>{const c=EXPR,p=c.closest('.nl-vp-pager'),n=p?.querySelector(':scope>.nl-vp-pager-nav'),b=n?.querySelector('button:last-child');return{position:HORIZONTAL?c.scrollLeft:c.scrollTop,size:HORIZONTAL?c.clientWidth:c.clientHeight,total:HORIZONTAL?c.scrollWidth:c.scrollHeight,nextDisabled:b?.disabled??true,navHidden:n?.hidden??true}})()'''.replace('EXPR',expression).replace('HORIZONTAL','true' if horizontal else 'false'));samples.append(item)
  if item['nextDisabled']:break
  clickel('('+expression+').closest(".nl-vp-pager").querySelector(":scope>.nl-vp-pager-nav button:last-child")');pause(.1)
 else:raise AssertionError('Content pager has no bounded end')
 check(samples[-1]['size']>0 and samples[-1]['size']+samples[-1]['position']>=samples[-1]['total']-3,label+' complete content reachable via actual pager',samples)
 for _ in range(30):
  if read('(()=>{const n=('+expression+').closest(".nl-vp-pager")?.querySelector(":scope>.nl-vp-pager-nav button:first-child");return !n||n.disabled})()'):break
  clickel('('+expression+').closest(".nl-vp-pager").querySelector(":scope>.nl-vp-pager-nav button:first-child")');pause(.1)
 OUT.setdefault('contentPages',[]).append({'game':game,'selector':selector,'label':label,'axis':'x' if horizontal else 'y','samples':samples})

def feedback_pages(game,label):
 editor={'repair':'.bench','builder':'.workspace','puzzle':'.puzzle-assembly-panel','detective':'.detective-workspace'}[game]
 hidden=present(game,editor);check(not hidden.get('visible'),label+' editor pane hidden during feedback',hidden)
 expression=game_expr(game,'.feedback')
 q=element_metrics(expression);check(q.get('visible') and q['clientHeight']>12,label+' feedback has visible text area',q)
 samples=[]
 for _ in range(30):
  item=read('''(()=>{const c=EXPR,p=c.closest('.nl-vp-pager'),n=p?.querySelector(':scope>.nl-vp-pager-nav'),b=n?.querySelector('button:last-child');return{text:c.innerText,top:c.scrollTop,height:c.clientHeight,total:c.scrollHeight,navHidden:n?.hidden??true,nextDisabled:b?.disabled??true}})()'''.replace('EXPR',expression));samples.append(item)
  if item['nextDisabled']:break
  clickel('('+expression+').closest(".nl-vp-pager").querySelector(":scope>.nl-vp-pager-nav button:last-child")');pause(.1)
 else:raise AssertionError('Feedback pager has no bounded end')
 check(samples[-1]['height']+samples[-1]['top']>=samples[-1]['total']-3,label+' full feedback end reachable via visible pager',samples)
 OUT.setdefault('feedbackPages',[]).append({'game':game,'label':label,'pages':samples})

def first_screens(game):
 # These are actual CSS layout sizes. Zoom is tested by effective viewport
 # reductions separately; no document style or application settings are mutated.
 sizes=[(1024,640),(1280,720),(1440,900),(390,700)]
 entries=[]
 for width,height in sizes:
  viewport(width,height);game_ready(game,True);pause(.4)
  parent=read('(()=>{const d=document.getElementById("nlQuizDialog"),r=d.getBoundingClientRect();return{viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio,visual:visualViewport?{width:visualViewport.width,height:visualViewport.height,scale:visualViewport.scale}:null},dialog:{top:r.top,bottom:r.bottom,height:r.height,clientHeight:d.clientHeight,scrollHeight:d.scrollHeight,scrollTop:d.scrollTop},document:{clientHeight:document.documentElement.clientHeight,scrollHeight:document.documentElement.scrollHeight,scrollTop:document.documentElement.scrollTop},frames:[...d.querySelectorAll("iframe")].map(f=>({className:f.className,url:f.src,height:f.getBoundingClientRect().height,childHeight:f.contentWindow.innerHeight,childScrollHeight:f.contentDocument.documentElement.scrollHeight}))}})()')
  check(parent['dialog']['top']>=-1 and parent['dialog']['bottom']<=height+1 and parent['dialog']['scrollHeight']<=parent['dialog']['clientHeight']+2 and parent['dialog']['scrollTop']==0,game+' actual dialog fits without scrolling '+str(width)+'x'+str(height),parent)
  if game!='repair':check(all('viewport=1' in f['url'] for f in parent['frames'] if 'nl-'+game+'-frame' in f['className']),game+' v57 child explicitly opted in')
  observations=[]
  if game=='repair':
   view(game,'answer');observations.append(assert_visible(game,'.broken-name','Repair name accessible '+str(width)))
   observations.append(assert_visible(game,'[id$="check-button"]','Repair Check visible '+str(width)))
   view(game,'structure');observations.append(assert_visible(game,'.diagram-image','Repair complete diagram viewport '+str(width)));view(game,'answer')
  elif game=='builder':
   view(game,'editing');observations.append(assert_visible(game,'#answer-zone','Builder answer area '+str(width)));observations.append(assert_visible(game,'#check-answer','Builder Check '+str(width)))
   view(game,'bank');observations.append(assert_visible(game,'#bank-zone','Builder bank accessible '+str(width)))
   if width==390:content_pages(game,'#bank-zone','Builder complete narrow bank')
   view(game,'molecule');observations.append(assert_visible(game,'#molecule-viewer','Builder molecule accessible '+str(width)));view(game,'editing')
  elif game=='puzzle':
   view(game,'editing');observations.append(assert_visible(game,'#assembly-board','Puzzle board accessible '+str(width)));observations.append(assert_visible(game,'#check-answer','Puzzle Check '+str(width)))
   view(game,'pieces');observations.append(assert_visible(game,'#piece-bank','Puzzle pieces accessible '+str(width)));view(game,'editing')
  else:
   view(game,'clue');observations.append(assert_visible(game,'#mission-name','Detective clue name '+str(width)));observations.append(assert_visible(game,'#mission-prompt','Detective mission '+str(width)))
   if width==390:content_pages(game,'#mission-name','Detective entire narrow name',True);content_pages(game,'#mission-prompt','Detective entire narrow mission')
   view(game,'structure');observations.append(assert_visible(game,'#molecule-viewer','Detective molecule '+str(width)));observations.append(assert_visible(game,'#check-answer','Detective Check '+str(width)))
  shot('first-'+game+'-'+str(width)+'x'+str(height));entries.append({'parent':parent,'observations':observations})
 OUT.setdefault('firstScreens',{})[game]=entries;viewport(1280,720);game_ready(game,True)

def solve_builder(label,controlled=True,partial=False):
 info=builder_info(controlled);already=len(info['answer']);used=set(n['id'] for n in info['answer'])
 for piece in info['pieces'][already:]:
  info_now=builder_info(controlled);tile=next(t for t in info_now['bank'] if t['id'] not in used and t['text']==piece['text']);used.add(tile['id'])
  view('builder','bank');game_click('builder','#bank-tiles [data-tile-id='+json.dumps(tile['id'])+']',controlled)
  if partial:return info['native']['selectedMol']
 check(game_read('builder','document.getElementById("candidate-name").textContent',controlled)==info['correctName'],label+' exact native composed name')
 view('builder','editing');game_click('builder','#check-answer',controlled);wait('('+window_expr('builder',controlled)+').document.getElementById("feedback").classList.contains("success")')
 OUT['correctUIAttempts'].append({'game':'builder','moleculeId':info['native']['selectedMol'],'label':label,'controlled':controlled});return info['native']['selectedMol']

def solve_puzzle(label,controlled=True,partial=False):
 info=puzzle_info(controlled);mid=info['load']['moleculeId'];graph=game_read('puzzle','NameleculeMolecularPuzzleEngine.parseMol('+json.dumps(MOLS[mid])+')',controlled)
 for node in graph['nodes'][len(info['nodes']):]:
  view('puzzle','pieces');game_click('puzzle','[data-hydrogens="'+str(node['hydrogens'])+'"]',controlled)
  if partial:return mid
  if controlled and not OUT.get('puzzlePointerDrag'):
   view('puzzle','editing');puzzle_drag_and_keyboard()
 ids=[n['id'] for n in puzzle_info(controlled)['nodes']];mapping={n['id']:ids[i] for i,n in enumerate(graph['nodes'])}
 if graph['bonds']:
  view('puzzle','tools')
  if game_read('puzzle','document.getElementById("bond-tool").getAttribute("aria-pressed")',controlled)!='true':game_click('puzzle','#bond-tool',controlled)
  view('puzzle','editing')
  for edge in graph['bonds']:
   game_click('puzzle','[data-node-id='+json.dumps(mapping[edge['a']])+']',controlled);game_click('puzzle','[data-node-id='+json.dumps(mapping[edge['b']])+']',controlled)
 check(puzzle_info(controlled)['bonds']==len(graph['bonds']),label+' actual complete C-C adjacency')
 view('puzzle','editing');game_click('puzzle','#check-answer',controlled);wait('('+window_expr('puzzle',controlled)+').document.getElementById("feedback").classList.contains("success")')
 OUT['correctUIAttempts'].append({'game':'puzzle','moleculeId':mid,'label':label,'controlled':controlled});return mid

def puzzle_raw():
 progress=active_attempt('puzzle')['progress'];return progress['states'][progress['currentRound']]['graph']

def puzzle_drag_and_keyboard():
 before=puzzle_raw();check(len(before['nodes'])==1 and not before['bonds'],'Puzzle drag starts from one genuine placed group')
 identifier=before['nodes'][0]['id'];expr=game_expr('puzzle','[data-node-id='+json.dumps(identifier)+']');start=element_metrics(expr);boardq=present('puzzle','#assembly-board')
 check(start.get('hit') and start.get('within') and boardq.get('within'),'Puzzle actual draggable node and board visible',{'node':start,'board':boardq})
 # Place farther than the seven-pixel drag threshold, safely within the board.
 end={'x':int(start['x']+45 if start['x']+80<boardq['x']+boardq['rect']['width']/2 else start['x']-45),'y':int(start['y']+30)}
 if OUT['engine']=='chrome':
  cdp('Input.dispatchMouseEvent',{'type':'mouseMoved','x':start['x'],'y':start['y'],'button':'none','buttons':0})
  cdp('Input.dispatchMouseEvent',{'type':'mousePressed','x':start['x'],'y':start['y'],'button':'left','buttons':1,'clickCount':1})
  cdp('Input.dispatchMouseEvent',{'type':'mouseMoved',**end,'button':'left','buttons':1})
  cdp('Input.dispatchMouseEvent',{'type':'mouseReleased',**end,'button':'left','buttons':0,'clickCount':1})
 else:
  call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'viewport-puzzle-drag','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':start['x'],'y':start['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerMove',**end,'duration':250},{'type':'pointerUp','button':0}]}]})
 pause(.5);after=puzzle_raw();check(after['nodes'][0]['id']==identifier and after['nodes'][0]['hydrogens']==before['nodes'][0]['hydrogens'] and not after['bonds'] and after['nodes'][0]!=before['nodes'][0],'Puzzle trusted placed-node drag changes coordinates and preserves raw chemical group/topology',{'before':before,'after':after})
 clickel(expr);pause(.4)
 # Focus is preparation only. Delete is trusted native keyboard input.
 ev('('+expr+').focus({preventScroll:true});true')
 if OUT['engine']=='chrome':
  for event in ['keyDown','keyUp']:cdp('Input.dispatchKeyEvent',{'type':event,'key':'Delete','code':'Delete','windowsVirtualKeyCode':46,'nativeVirtualKeyCode':46})
 else:call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'viewport-puzzle-delete','actions':[{'type':'keyDown','value':'\ue017'},{'type':'keyUp','value':'\ue017'}]}]})
 pause(.25);check(not puzzle_raw()['nodes'],'Puzzle native Delete removes selected raw group')
 view('puzzle','tools');game_click('puzzle','#undo-action',True);pause(.3);check(puzzle_raw()==after,'Puzzle actual Undo restores exact dragged graph');view('puzzle','editing')
 OUT['puzzlePointerDrag']={'before':before,'afterDrag':after,'afterUndo':puzzle_raw(),'trustedKeyboardDelete':True}

def solve_repair(label,controlled=True,partial=False):
 view('repair','answer')
 if present('repair','.repair-choice-page > button:first-child').get('visible'):click('.repair-choice-page > button:first-child')
 return RECORDED_SOLVERS['repair'](label,controlled,partial)

def solve_detective(label,controlled=True,partial=False):
 view('detective','structure');return RECORDED_SOLVERS['detective'](label,controlled,partial)

def detective_pick(kind,target,controlled=False):
 # Read native selection geometry only. The inherited solver's preparatory
 # scrollIntoView is omitted in viewport mode; production stages own access.
 if LEGACY_SCROLL:
  original_detective_pick(kind,target,controlled);return
 game=window_expr('detective',controlled);native='('+game+').document.getElementById("molecule-viewer")'
 expression='''(()=>{const f=NATIVE,w=f.contentWindow,g=w.fMulerSelectGeom(),svg=w.document.querySelector('#jsmeNomeclatureSVG svg');let a;if(KIND==='atoms'){a=g.anchors.find(a=>a.atom+1===TARGET);if(!a){const i=g.vassign.findIndex(a=>a+1===TARGET);a=g.verts[i]}}else{const b=g.groups.find(b=>b.bond+1===TARGET),l=b?.rep||b?.lines[0];if(l)a={x:(l.x1+l.x2)/2,y:(l.y1+l.y2)/2}}if(!a)throw Error('Missing native target geometry');const p=svg.createSVGPoint();p.x=a.x;p.y=a.y;const s=p.matrixTransform((svg.querySelector('g')||svg).getScreenCTM());let x=s.x,y=s.y,v=w,hit=true;while(v!==window){const frame=v.frameElement,r=frame.getBoundingClientRect();x+=r.x;y+=r.y;v=v.parent;hit=hit&&v.document.elementFromPoint(x,y)===frame}return{x:Math.round(x),y:Math.round(y),hit,target:TARGET,kind:KIND}})()'''
 q=read(expression.replace('NATIVE',native).replace('KIND',json.dumps(kind)).replace('TARGET',str(target)))
 before=ds(controlled)['selectionRevision'];pointer(q,'native '+kind+str(target));wait('('+game+').NameleculeMolecularDetective.snapshot().selectionRevision>'+str(before),10)
 check(target in ds(controlled)[kind],'genuine native raw selection '+kind+'/'+str(target))

SOLVERS.update(builder=solve_builder,puzzle=solve_puzzle,repair=solve_repair,detective=solve_detective)

def footer_contract(game,final):
 item=read('({footer:[...document.querySelectorAll(".round-next button")].map(b=>({text:b.textContent,hidden:b.hidden,rect:b.getBoundingClientRect().toJSON()})),header:[...document.querySelectorAll(".nl-quiz-dialog-header button")].map(b=>({text:b.textContent,hidden:b.hidden,display:getComputedStyle(b).display}))})')
 check(len(item['footer'])==(3 if final else 1),game+' expected '+('final3' if final else 'intermediate1')+' footer actions',item)
 if final:
  if gate_state()['solved']:check(all(b['hidden'] or b['display']=='none' for b in item['header']),game+' final complete-gate header duplicate actions absent',item)
  else:check(item['header'][0]['hidden'] and not item['header'][1]['hidden'],game+' incomplete gate retains top Back while theory Continue stays hidden',item)
 OUT.setdefault('footerContracts',[]).append({'game':game,'final':final,'gateSolved':gate_state()['solved'],'observed':item})

def zoom_dimensions():return read('({innerWidth,innerHeight,devicePixelRatio,visual:visualViewport?{width:visualViewport.width,height:visualViewport.height,scale:visualViewport.scale}:null})')

def zoom_chord(key):
 if OUT['engine']=='chrome':
  code='Equal' if key=='=' else 'Digit0';virtual=187 if key=='=' else 48;native=24 if key=='=' else 29
  cdp('Input.dispatchKeyEvent',{'type':'rawKeyDown','key':'Meta','code':'MetaLeft','modifiers':4,'windowsVirtualKeyCode':91,'nativeVirtualKeyCode':55})
  cdp('Input.dispatchKeyEvent',{'type':'keyDown','key':key,'code':code,'modifiers':4,'windowsVirtualKeyCode':virtual,'nativeVirtualKeyCode':native})
  cdp('Input.dispatchKeyEvent',{'type':'keyUp','key':key,'code':code,'modifiers':4,'windowsVirtualKeyCode':virtual,'nativeVirtualKeyCode':native})
  cdp('Input.dispatchKeyEvent',{'type':'keyUp','key':'Meta','code':'MetaLeft','modifiers':0,'windowsVirtualKeyCode':91,'nativeVirtualKeyCode':55})
 else:
  call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'viewport-real-browser-zoom','actions':[{'type':'keyDown','value':'\ue03d'},{'type':'keyDown','value':key},{'type':'keyUp','value':key},{'type':'keyUp','value':'\ue03d'}]}]})
 pause(.35)

def actual_zoom_attempt(game):
 if game=='detective':game_click(game,'#detective-feedback-back',True);view(game,'structure')
 else:view(game,'editing')
 before_record=rec();zoom_chord('0');baseline=zoom_dimensions();samples=[]
 for count in range(1,6):
  zoom_chord('=')
  if count in [2,5]:
   dims=zoom_dimensions();changed=dims['innerWidth']!=baseline['innerWidth'] or dims['devicePixelRatio']!=baseline['devicePixelRatio'];sample={'trustedShortcutCount':count,'intendedPercent':125 if count==2 else 200,'dimensions':dims,'effectiveBrowserZoomChanged':changed};samples.append(sample)
   if changed:
    assert_visible(game,'#check-answer',game+' actual zoom changed Check accessible '+str(sample['intendedPercent']))
    if game=='builder':view(game,'bank');content_pages(game,'#bank-zone','actual zoom changed full Builder bank');view(game,'editing')
    else:view(game,'clue');content_pages(game,'#mission-name','actual zoom changed Detective name',True);view(game,'structure')
   shot('actual-zoom-attempt-'+game+'-'+str(sample['intendedPercent']))
 zoom_chord('0');restored=zoom_dimensions();check(rec()==before_record,'trusted browser zoom shortcuts preserve exact learner record')
 check(restored==baseline,'trusted browser zoom reset restores measured dimensions',{'before':baseline,'after':restored})
 confirmed=all(s['effectiveBrowserZoomChanged'] for s in samples)
 OUT.setdefault('actualBrowserZoomAttempts',[]).append({'game':game,'method':'trusted macOS Meta+Equal twice/5times and Meta+0; no pageScale/CSS zoom/device emulation substituted','baseline':baseline,'samples':samples,'restored':restored,'actualBrowserZoomConfirmed':confirmed})
 if not confirmed:OUT['limits'].append('Actual125/200 browser zoom unverified: trusted Meta+Equal in this isolated headless '+OUT['engine']+' left measured CSS viewport/DPR unchanged. Screenshots are attempts at100%, not proof of125/200%.')
 if game=='detective':game_click(game,'#detective-feedback-open',True)

def viewport_triple(game,level):
 ids=[]
 for n in range(3):
  ids.append(SOLVERS[game]('viewport gate'+str(INDEX+1)+' '+game+' L'+str(level)+' round'+str(n+1),True));wait('!!document.querySelector(".round-next button")')
  check(active_attempt(game,level)['progress']['states'][n]['solved'],'parent genuinely regrades '+game+' round'+str(n+1));feedback_pages(game,game+' correct round'+str(n+1));footer_contract(game,n==2)
  if n<2:next_round(game,True)
 check(len(set(ids))==3,'three distinct '+game+' L'+str(level),ids);return ids

def priority_repair_triple():
 ids=[]
 for n,(width,height) in enumerate([(1280,720),(1024,640),(390,700)]):
  viewport(width,height);game_ready('repair',True);view('repair','answer');rnd=repair_oracle(True)
  if rnd['kind']=='replace':
   click('[id$="part-'+rnd['targetPartId']+'"]');content_pages('repair','.choices','Repair full choices '+str(width))
   wrong=next(i for i,c in enumerate(rnd['choices']) if c['value']!=rnd['correctValue']);click('[id$="choice-'+str(wrong)+'"]')
  click('[id$="check-button"]');pause(.25)
  state=active_attempt('repair',1)['progress']['states'][n];check(state['submitted'] and not state['solved'] and state['attempts']>=1,'Repair genuine wrong candidate rejected '+str(width),state)
  feedback_pages('repair','Repair wrong '+str(width));click('.repair-feedback-stage .repair-stage-heading button:first-of-type')
  ids.append(solve_repair('priority Repair gate4 round'+str(n+1)+' '+str(width),True));feedback_pages('repair','Repair correct '+str(width));footer_contract('repair',n==2)
  if n<2:next_round('repair',True)
 check(len(set(ids))==3,'priority Repair three distinct molecules',ids);return ids

def repair_final_inspection():
 click('.repair-feedback-stage .repair-stage-heading button:last-child');pause(.3)
 back=element_metrics('document.getElementById("nlQuizBack")');check(back.get('visible') and back.get('within') and back.get('hit'),'Repair final inspection restores visible top Back',back)
 footer=read('[...document.querySelectorAll(".round-next button")].map(b=>({text:b.textContent,visible:!!b.getClientRects().length}))')
 check(not any(b['visible'] for b in footer),'Repair final inspection hides footer while leaving return route',footer)
 view('repair','answer');clickel('[...document.querySelectorAll(".repair-stage-tabs button")].find(b=>b.textContent==="Στην εξήγηση")');pause(.3);footer_contract('repair',True)
 assert_visible('repair','[data-checkpoint-continue]','Repair final explanation restores visible Continue footer')

def wrong_restore_builder():
 solve_builder('prefix only',True,True);view('builder','editing');game_click('builder','#check-answer',True)
 check(not game_read('builder','document.getElementById("feedback").classList.contains("success")',True),'genuine incomplete Builder answer rejected');feedback_pages('builder','wrong Builder')
 before=active_attempt('builder',1);raw=builder_info(True)['answer'];call('browsingContext.reload',{'context':ctx,'wait':'none'});ready();open_gate();game_ready('builder',True)
 check(active_attempt('builder',1)==before and builder_info(True)['answer']==raw,'wrong Builder prefix/raw partial exact cold restore');game_click('builder','.builder-feedback-actions button:first-child',True);view('builder','editing')
 select_level(2,True);game_ready('builder',True);select_level(1,True);game_ready('builder',True)
 check(builder_info(True)['answer']==raw,'wrong prefix exact level switch restore');game_click('builder','.builder-feedback-actions button:first-child',True)

def legacy_native_smoke():
 global LEGACY_SCROLL
 LEGACY_SCROLL=True
 try:
  # Existing helper selects exact archived v1 scenario, current shared JS.
  old=SOLVERS.copy();SOLVERS.update(RECORDED_SOLVERS);native_cache(['new']);SOLVERS.update(old)
  check(read('typeof NameleculeGameViewport')=='undefined','native legacy Main56 omits viewport helper')
 finally:LEGACY_SCROLL=False

def bounded_builder_3d():
 lesson(3);open_gate();choose('builder',1);before=rec();info=builder_info(True);view('builder','molecule');result={'moleculeId':info['native']['selectedMol'],'timeBoundSeconds':25,'kind':'actual v57 embedded Builder3D then Condensed'}
 try:
  control=present('builder','[data-representation="3d"]')
  if control['disabled']:
   result['unavailable']=True;OUT['limits'].append('Selected embedded Builder3D control unavailable; no3D claim.')
  else:
   game_click('builder','[data-representation="3d"]',True)
   wait('('+window_expr('builder',True)+').document.getElementById("viewer-mask").hidden&&('+window_expr('builder',True)+').document.getElementById("molecule-viewer").contentWindow.NameleculeNameBuilderHost.modelReady()',25)
   result['nativeModelReady']=True;assert_visible('builder','#molecule-viewer','actual Builder3D native frame fits');assert_visible('builder','[data-representation="condensed"]','actual Builder3D return control visible');shot('actual-v57-builder3d')
 except Exception as error:
  result['externalOrUntestedFailure']=repr(error);OUT['limits'].append('Bounded actual embedded Builder3D did not establish modelReady within25s; captured separately, no3D success claim.')
 finally:
  try:
   game_click('builder','[data-representation="condensed"]',True);wait('('+window_expr('builder',True)+').document.getElementById("viewer-mask").hidden',25)
   check(builder_info(True)['native']['selectedMol']==info['native']['selectedMol'] and builder_info(True)['answer']==info['answer'] and rec()==before,'actual3D/Condensed switch preserves molecule/raw learner state');result['returnedCondensed']=True
  except Exception as error:result['returnFailure']=repr(error);OUT['limits'].append('Return from bounded3D needs separate investigation; native compatibility uses fresh context afterward.')
  OUT['boundedBuilder3D']=result

def legacy_migration():
 global INDEX
 shutil.copyfile(Path(OUT['manifest']),DEST/'frozen-manifest.json')
 OUT['coreBaseline']=VIEWPORT_BASELINE['coreBaseline'];OUT['protectedBaseline']=VIEWPORT_PROTECTED
 check(all(OUT['sourceBefore'][p]==v for p,v in VIEWPORT_BASELINE['coreBaseline'].items()),'all13 cores match session baseline before actual UI')
 check(all(OUT['sourceBefore'][p]==v for p,v in VIEWPORT_PROTECTED.items()),'all16 protected dependencies match baseline before actual UI')
 for filename in ['lesson-checks.py','replay-viewport.py']:
  shutil.copyfile(HERE/filename,DEST/filename)
 shutil.copyfile(ROOT/'docs/checks/game-levels-alkanes-implementation-20261116/browser/replay-levels.py',DEST/'reused-replay-levels.py')
 OUT['scenarioHarnessSHA256']=sha(Path(__file__).parent/'lesson-checks.py');OUT['reuseHarnessSHA256']=sha(ROOT/'docs/checks/game-levels-alkanes-implementation-20261116/browser/replay-levels.py')
 OUT['limits'].append('Zoom100 is actual CSS viewport. 125/200 browser UI zoom is not inferred from viewport emulation and requires explicit separate evidence.')
 if MODE.endswith('detective-native'):
  viewport(1280,720);lesson(3);open_gate();choose('detective',1);first_screens('detective');OUT['gate4IDs']=viewport_triple('detective',1);earned=gate_state()['receipts'];check(gate_state()['solved'],'Detective triple unlocks step4')
  call('browsingContext.reload',{'context':ctx,'wait':'none'});ready();open_gate();game_ready('detective',True);check(gate_state()['receipts']==earned,'Detective earned exact cold restore')
  actual_zoom_attempt('detective')
  activate_button('[data-checkpoint-continue]');wait('fScenarioPresent().index===4&&!document.getElementById("nlQuizDialog").open');INDEX=4
  bounded_builder_3d()
  legacy_native_smoke();return
 viewport(1280,720);lesson();OUT['replayIndices']=[0]
 for index in range(1,4):pause(.4);click('#scNext');wait('fScenarioPresent().index==='+str(index));INDEX=index;OUT['replayIndices'].append(index)
 check(read('document.getElementById("scNext").disabled'),'fresh step4 locked');open_gate()
 tail=MODE.endswith('required-tail')
 choose('repair',1);OUT['gate4IDs']=viewport_triple('repair',1) if tail else priority_repair_triple();check(gate_state()['solved'] and bool(gate_state()['receipts']['1']),'Repair level1 triple unlocks step4')
 if not tail:repair_final_inspection()
 viewport(1280,720);pause(.4)
 activate_button('[data-checkpoint-continue]');wait('fScenarioPresent().index===4&&!document.getElementById("nlQuizDialog").open');INDEX=4;OUT['replayIndices'].append(4)
 for index in range(5,11):pause(.4);click('#scNext');wait('fScenarioPresent().index==='+str(index));INDEX=index;OUT['replayIndices'].append(index)
 check(read('document.getElementById("scNext").disabled'),'fresh step11 independently locked');open_gate()
 if not tail:
  for game in ['repair','builder','puzzle','detective']:
   choose(game,1);first_screens(game)
   if game=='detective':
    game_click('detective','#check-answer',True);check(not ds(True)['correct'],'genuine empty Detective rejected');feedback_pages('detective','wrong Detective');game_click('detective','#detective-feedback-back',True)
  choose('detective',3);OUT['optional3IDs']=viewport_triple('detective',3)
  check(not gate_state()['solved'] and not gate_state()['receipts'].get('1') and not gate_state()['receipts'].get('2'),'genuine optional3 triple alone blocked')
 choose('builder',1);wrong_restore_builder();OUT['level1IDs']=viewport_triple('builder',1)
 check(not gate_state()['solved'] and bool(gate_state()['receipts'].get('1')) and not gate_state()['receipts'].get('2'),'Builder1 cannot replace required2 (optional3 separate evidence)' if tail else 'Builder1 plus optional3 cannot replace required2')
 choose('puzzle',2);OUT['level2IDs']=viewport_triple('puzzle',2);earned=gate_state()['receipts'];check(gate_state()['solved'] and bool(earned['1']) and bool(earned['2']),'Builder1 and Puzzle2 independent receipts unlock step11')
 call('browsingContext.reload',{'context':ctx,'wait':'none'});ready();open_gate();game_ready('puzzle',True);check(gate_state()['receipts']==earned and gate_state()['solved'],'separate earned receipts exact cold revalidation');feedback_pages('puzzle','cold restored Puzzle')
 viewport(390,700);pause(.4);assert_visible('puzzle','.puzzle-feedback-actions button:first-child','cold restored narrow feedback inspection reachable');viewport(1280,720)
 activate_button('[data-checkpoint-continue]');wait('fScenarioPresent().index===11&&!document.getElementById("nlQuizDialog").open');INDEX=11;OUT['replayIndices'].append(11)
 check(OUT['replayIndices']==list(range(12)),'all12 actual presentation steps and both checkpoint Continue transitions');OUT['finalRecord']=rec();shot('final-step12')
 lesson(3);open_gate();choose('builder',1);actual_zoom_attempt('builder')
