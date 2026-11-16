"""Prepare/run root Workshop+Detective proof with the same owned UI runner.

No seed, selection, answer, bridge message or receipt is written by this harness.
Workshop observes naturally generated rounds and may start bounded new attempts
through the public URL; every preceding round is solved with production inputs.
"""
from pathlib import Path
import textwrap
from urllib.parse import urlsplit, unquote
DRIVER = Path(__file__).with_name('replay-new-six.py').read_text()
prefix, startup_and_rest = DRIVER.split('\ntry:\n server=',1)
exec(compile(prefix,'alkane-games-shared-owned-helpers','exec'))
SOURCES.update({'games/name-repair.html','games/molecular-detective.html','games/molecular-detective-viewer.html',
 'js/namelecule-game-repair.js','js/namelecule-generated-repair-checkpoint.js','js/namelecule-repair-generator.js',
 'js/namelecule-molecular-detective.js','js/namelecule-molecular-detective-engine.js','js/namelecule-molecular-detective-host.js',
 'js/mulermoc-nom-core-56.js','js/mulermoc-nom-molview-56.js'})
PRIOR_ROOT=ROOT/'docs/checks/alkane-pool-implementation-20261116/before'
for prior_path in ['games/name-repair.html','js/namelecule-game-repair.js']:
 assert (PRIOR_ROOT/prior_path).is_file(), 'Archived prior Workshop source required'
 SOURCES.add(str((PRIOR_ROOT/prior_path).relative_to(ROOT)))
OUT['sourceBefore']=hashes()
OUT['scope']='Actual six-new Workshop repairs via naturally generated attempts, valid legacy8 partial/solved record continuity, and all mission families for each new Detective molecule via trusted native atom/bond picks.'
OUT['harnessSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
OUT['sharedHarnessSHA256']=hashlib.sha256(Path(__file__).with_name('replay-new-six.py').read_bytes()).hexdigest()
OUT['workshopAttemptPolicy']='At most 24 naturally randomized new branched attempts using public startSet; skip attempts containing no remaining new molecule. No seed override or receipt injection.'
NEW_IDS={record['id'] for record in NEW}
LEGACY_KEY='namelecule-repair-engine-pilot-v1'
ENRICHED_KEY='namelecule-repair-engine-pool-v2'
W='document.getElementById("molecule-viewer").contentWindow'
S='NameleculeMolecularDetective.snapshot()'

# Same-origin alias serves real archived before-code where supplied, with only
# unchanged dependencies falling back to the project. The real old UI creates
# its own storage record before current-code navigation; no record is injected.
BaseHandler=Handler
class Handler(BaseHandler):
 def translate_path(self, path):
  requested=unquote(urlsplit(path).path)
  if requested.startswith('/__prior__/'):
   relative=Path(requested.removeprefix('/__prior__/'))
   if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe prior alias path')
   archived=PRIOR_ROOT/relative
   return str(archived if archived.is_file() else ROOT/relative)
  return super().translate_path(path)

def stored(key):return read('JSON.parse(sessionStorage.getItem('+json.dumps(key)+'))')
def workshop_ready():wait('document.getElementById("game-root").getAttribute("aria-busy")==="false"&&!!document.querySelector(".diagram-image.is-ready")',90)
def workshop_round(key, reference):
 record=stored(key)
 if reference=='prior':
  return json.loads(ev('(async()=>{const c=await(await fetch(new URL("data/alkane-structures.json",document.baseURI))).json(),a=await Promise.all(c.molecules.map(m=>NameleculeChemistryClient.analyze(m,{engineSHA256:c.engineSHA256}))),g=NameleculeRepairGenerator.createGame(c,a,{seed:'+json.dumps(record['seed'])+',difficulty:'+json.dumps(record['difficulty'])+'});return JSON.stringify(g.sets.find(s=>s.id==='+json.dumps(record['setId'])+').rounds['+str(record['roundIndex'])+'])})()'))
 expression='''(async()=>{const p=NameleculeGeneratedRepairCheckpoint,d=p.catalogDescriptor(REFERENCE),c=await p.loadCanonicalInput(undefined,d),g=NameleculeRepairGenerator.createGame(c.catalog,c.analyses,{seed:SEED,difficulty:DIFFICULTY});return JSON.stringify(g.sets.find(s=>s.id===SET).rounds[INDEX])})()'''
 expression=expression.replace('REFERENCE',json.dumps(reference)).replace('SEED',json.dumps(record['seed'])).replace('DIFFICULTY',json.dumps(record['difficulty'])).replace('SET',json.dumps(record['setId'])).replace('INDEX',str(record['roundIndex']))
 return json.loads(ev(expression))
def workshop_set(key,reference):
 record=stored(key)
 return json.loads(ev('(async()=>{const c=await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput(undefined,NameleculeGeneratedRepairCheckpoint.catalogDescriptor('+json.dumps(reference)+'));return JSON.stringify(NameleculeRepairGenerator.createGame(c.catalog,c.analyses,{seed:'+json.dumps(record['seed'])+',difficulty:'+json.dumps(record['difficulty'])+'}).sets.find(s=>s.id==='+json.dumps(record['setId'])+'))})()'))
def workshop_solve(key,reference,wrong=True):
 rnd=workshop_round(key,reference);mid=rnd['moleculeId']
 image=read('({src:document.querySelector(".diagram-image").src,loaded:document.querySelector(".diagram-image").complete&&document.querySelector(".diagram-image").naturalWidth>0})')
 check(image['loaded'],'Workshop actual image loaded '+mid,image)
 if mid in NEW_IDS:check('/expanded-v2/' in image['src'] or '/condensed-v2/' in image['src'],'Workshop new versioned asset '+mid,image)
 if rnd['kind']=='replace':
  check(ev('document.querySelector("[id$=check-button]").disabled'),'Workshop empty replacement disabled '+mid)
  badpart=next(p['id'] for p in rnd['parts'] if p['id']!=rnd['targetPartId'])
  click('[id$="part-'+badpart+'"]')
  check(ev('document.querySelector("[id$=check-button]").disabled'),'Workshop wrong part does not form answer '+mid)
  click('[id$="part-'+rnd['targetPartId']+'"]')
  check(ev('document.querySelector("[id$=check-button]").disabled'),'Workshop partial target without replacement disabled '+mid)
  if wrong:
   bad=next(i for i,c in enumerate(rnd['choices']) if c['value']!=rnd['correctValue'])
   click('[id$="choice-'+str(bad)+'"]');click('[id$="check-button"]')
   check(not ev('!!document.querySelector(".feedback.is-success")'),'Workshop wrong replacement rejected '+mid)
  good=next(i for i,c in enumerate(rnd['choices']) if c['value']==rnd['correctValue']);click('[id$="choice-'+str(good)+'"]')
 else:
  if wrong:
   click('[id$="check-button"]');check(not ev('!!document.querySelector(".feedback.is-success")'),'Workshop initial wrong order rejected '+mid)
  for destination,pid in enumerate(rnd['correctOrder']):
   order=read('[...document.querySelectorAll(".part-button")].map(e=>e.id.split("part-")[1])');position=order.index(pid)
   if position>destination:
    click('[id$="part-'+pid+'"]')
    for _ in range(position-destination):click('[id$="move-left"]')
 click('[id$="check-button"]');wait('!!document.querySelector(".feedback.is-success")&&!!document.querySelector(".round-next button")')
 record=stored(key);check(record['states'][record['roundIndex']]['solved'],'Workshop trusted production repair accepted '+mid)
 OUT['correctUIAttempts'].append({'game':'repair','moleculeId':mid,'catalogRevision':record['catalogRevision'],'seed':record['seed'],'roundIndex':record['roundIndex'],'roundId':rnd['id'],'kind':rnd['kind']})
 if mid in NEW_IDS:shot('workshop-'+mid)
 return mid

def workshop_legacy_continuity():
 page('__prior__/games/name-repair.html?source=engine');wait('!!document.getElementById("set-alkanes-start")',90)
 click('#set-alkanes-start');click('#set-alkanes-unbranched-start');workshop_ready()
 prior_scripts=read('[...document.scripts].map(s=>s.src).filter(Boolean)')
 check(any('/__prior__/js/namelecule-game-repair.js' in source for source in prior_scripts),'legacy record created by actual archived before-code UI',prior_scripts)
 check(hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+'__prior__/js/namelecule-game-repair.js').read()).hexdigest()==hashlib.sha256((PRIOR_ROOT/'js/namelecule-game-repair.js').read_bytes()).hexdigest(),'prior alias serves exact archived Workshop JS')
 rnd=workshop_round(LEGACY_KEY,'prior');before=stored(LEGACY_KEY)
 check(before['catalogRevision']=='275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690','archived prior Workshop starts old8 descriptor')
 check(rnd['kind']=='replace','legacy unbranched round has bounded replacement fixture')
 click('[id$="part-'+rnd['targetPartId']+'"]');partial=stored(LEGACY_KEY)
 page('games/name-repair.html?source=engine&catalog=legacy');workshop_ready();restored=stored(LEGACY_KEY);restored_round=workshop_round(LEGACY_KEY,'legacy')
 check(restored['catalogRevision']==before['catalogRevision'] and restored['seed']==partial['seed'] and restored['roundIndex']==partial['roundIndex'] and restored['states']==partial['states'] and restored_round['id']==rnd['id'],'current explicit legacy resume keeps prior UI partial seed/round/state')
 partial_bytes=ev('sessionStorage.getItem('+json.dumps(LEGACY_KEY)+')')
 # Cancel retains the old round; confirm migrates only the new attempt action.
 click('.session-row button.quiet');wait('!!document.querySelector(".confirm-dialog[open]")');click('.confirm-dialog .secondary')
 check(ev('sessionStorage.getItem('+json.dumps(LEGACY_KEY)+')')==partial_bytes and ev('new URL(location.href).searchParams.get("catalog")')=='legacy','cancel legacy Back to sets preserves partial record and version')
 click('.session-row button.quiet');wait('!!document.querySelector(".confirm-dialog[open]")');click('.confirm-dialog .primary')
 wait('new URL(location.href).searchParams.get("catalog")==="enriched"&&!!document.querySelector(".workshop-set-picker")',90)
 check(not ev('new URL(location.href).searchParams.has("pickSet")'),'partial migration consumes picker command once')
 check(ev('sessionStorage.getItem('+json.dumps(LEGACY_KEY)+')')==partial_bytes,'confirm legacy Back to sets preserves old partial bytes immediately')
 click('#set-alkanes-unbranched-start');workshop_ready()
 check(stored(ENRICHED_KEY)['catalogRevision']==CATALOG['revision'] and ev('sessionStorage.getItem('+json.dumps(LEGACY_KEY)+')')==partial_bytes,'next set after partial migration is v2 while old partial remains')
 # Resume the genuine prior partial again and complete all three old repairs.
 page('games/name-repair.html?source=engine&catalog=legacy');workshop_ready()
 restored_round=workshop_round(LEGACY_KEY,'legacy');good=next(i for i,c in enumerate(restored_round['choices']) if c['value']==restored_round['correctValue'])
 click('[id$="choice-'+str(good)+'"]');click('[id$="check-button"]');wait('!!document.querySelector(".feedback.is-success")')
 OUT['correctUIAttempts'].append({'game':'repair-legacy','moleculeId':restored_round['moleculeId'],'catalogRevision':before['catalogRevision'],'seed':partial['seed'],'roundIndex':0})
 for index in [1,2]:
  click('.round-next button:first-child');workshop_ready();workshop_solve(LEGACY_KEY,'legacy',wrong=False)
 click('.round-next button:first-child');wait('!!document.querySelector(".results")')
 earned=stored(LEGACY_KEY)
 check(earned['phase']=='results' and all(state['solved'] for state in earned['states']),'all three genuine legacy repairs reach completed results')
 page('games/name-repair.html?source=engine&catalog=legacy');wait('!!document.querySelector(".results")',90);after=stored(LEGACY_KEY)
 check(after['catalogRevision']==earned['catalogRevision'] and after['seed']==earned['seed'] and after['states']==earned['states'],'explicit legacy reload revalidates complete prior attempt')
 completed_bytes=ev('sessionStorage.getItem('+json.dumps(LEGACY_KEY)+')')
 click('.results-actions button');wait('new URL(location.href).searchParams.get("catalog")==="enriched"&&!!document.querySelector(".workshop-set-picker")',90)
 check(not ev('new URL(location.href).searchParams.has("pickSet")'),'results Back to sets consumes picker command once')
 check(ev('sessionStorage.getItem('+json.dumps(LEGACY_KEY)+')')==completed_bytes,'results migration immediately preserves exact completed old bytes')
 click('#set-alkanes-branched-start');workshop_ready()
 check(stored(ENRICHED_KEY)['catalogRevision']==CATALOG['revision'] and ev('sessionStorage.getItem('+json.dumps(LEGACY_KEY)+')')==completed_bytes,'new set after completed old results uses v2 and preserves old bytes')
 page('games/name-repair.html?source=engine&catalog=legacy&startSet=alkanes-unbranched');workshop_ready()
 direct=stored(ENRICHED_KEY)
 check(ev('new URL(location.href).searchParams.get("catalog")')=='enriched' and not ev('new URL(location.href).searchParams.has("startSet")') and direct['catalogRevision']==CATALOG['revision'],'direct explicit legacy startSet redirects to consumed v2 new attempt')
 check(ev('sessionStorage.getItem('+json.dumps(LEGACY_KEY)+')')==completed_bytes,'direct legacy new-attempt command leaves completed old record byte-exact')
 call('browsingContext.reload',{'context':ctx,'wait':'none'});workshop_ready()
 check(stored(ENRICHED_KEY)['seed']==direct['seed'] and ev('sessionStorage.getItem('+json.dumps(LEGACY_KEY)+')')==completed_bytes,'reloading consumed v2 start command retains same new seed and old record')
 OUT['legacyWorkshop']={'recordCreatedBy':'Archived prior Workshop JS/HTML through same-origin server alias; genuine UI inputs, no receipt injection','partialBefore':partial,'partialAfter':restored,'completedBefore':earned,'completedAfter':after,'v2DirectSeed':direct['seed'],'oldRecordSHA256':hashlib.sha256(completed_bytes.encode()).hexdigest()}
 shot('workshop-v2-after-legacy-completion')

def workshop_new_six():
 covered=set();attempts=[]
 for attempt in range(24):
  page('games/name-repair.html?catalog=enriched&startSet=alkanes-branched');workshop_ready()
  record=stored(ENRICHED_KEY);rounds=workshop_set(ENRICHED_KEY,'enriched')['rounds']
  ids={r['moleculeId'] for r in rounds};attempts.append({'seed':record['seed'],'molecules':sorted(ids)})
  check(record['catalogRevision']==CATALOG['revision'],'new Workshop attempt stays enriched '+str(attempt+1))
  if not ((NEW_IDS-covered)&ids):continue
  for index in range(3):
   workshop_ready();mid=workshop_solve(ENRICHED_KEY,'enriched');covered.add(mid)
   if NEW_IDS.issubset(covered):break
   if index<2:click('.round-next button:first-child')
  if NEW_IDS.issubset(covered):break
 OUT['workshopNaturallyGeneratedAttempts']=attempts
 check(NEW_IDS.issubset(covered),'all six new molecules genuinely repaired in Workshop',{'covered':sorted(NEW_IDS&covered),'attempts':len(attempts)})

def detective_pick(kind, target):
 ev('document.getElementById("molecule-viewer").scrollIntoView({block:"center",behavior:"instant"});true');pause(.15)
 if kind=='atoms':
  expression='''(()=>{const f=document.getElementById('molecule-viewer'),w=f.contentWindow,g=w.fMulerSelectGeom(),svg=w.document.querySelector('#jsmeNomeclatureSVG svg');let a=g.anchors.find(a=>a.atom+1===TARGET);if(!a){const i=g.vassign.findIndex(a=>a+1===TARGET);a=g.verts[i]}if(!a)throw Error('Missing atom anchor');const p=svg.createSVGPoint();p.x=a.x;p.y=a.y;const s=p.matrixTransform((svg.querySelector('g')||svg).getScreenCTM()),r=f.getBoundingClientRect(),x=Math.round(r.x+s.x),y=Math.round(r.y+s.y);return{x,y,hit:document.elementFromPoint(x,y)===f,target:TARGET}})()'''
 else:
  expression='''(()=>{const f=document.getElementById('molecule-viewer'),w=f.contentWindow,g=w.fMulerSelectGeom(),svg=w.document.querySelector('#jsmeNomeclatureSVG svg'),b=g.groups.find(b=>b.bond+1===TARGET),l=b?.rep||b?.lines[0];if(!l)throw Error('Missing bond geometry');const p=svg.createSVGPoint();p.x=(l.x1+l.x2)/2;p.y=(l.y1+l.y2)/2;const s=p.matrixTransform((svg.querySelector('g')||svg).getScreenCTM()),r=f.getBoundingClientRect(),x=Math.round(r.x+s.x),y=Math.round(r.y+s.y);return{x,y,hit:document.elementFromPoint(x,y)===f,target:TARGET}})()'''
 point=read(expression.replace('TARGET',str(target)))
 check(point['hit'] and 0<=point['x']<1500 and 0<=point['y']<1000,'Detective trusted native point within input surface',point)
 before=read(S+'.selectionRevision')
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'alkane-pool-detective-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':point['x'],'y':point['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
 wait(S+'.selectionRevision>'+str(before),8)
 actual=read(S+'.'+kind);check(target in actual,'Detective native trusted pick selected expected '+kind,{'target':target,'actual':actual})

def detective_new_six():
 for record in NEW:
  mid=record['id'];page('games/molecular-detective.html?molecule='+mid+'&v=alkane-pool-browser');wait('typeof NameleculeMolecularDetective!=="undefined"&&'+S+'.phase==="active"',90)
  snapshot=read(W+'.NameleculeMolecularDetectiveHost.getSnapshot()');missions=read('NameleculeMolecularDetectiveEngine.missions('+json.dumps(snapshot)+')')
  check(snapshot['moleculeId']==mid and snapshot['correctName']==record['nameGR'],'Detective actual native56 snapshot '+mid)
  scripts=read('[...'+W+'.document.scripts].map(e=>e.src).filter(Boolean)')
  check(any('/js/mulermoc-nom-core-56.js' in p for p in scripts) and any('/js/MULERMOC_namelecule_alkanes_v1_data.js' in p for p in scripts),'Detective native56 and new shared bundle '+mid)
  check(read('document.querySelectorAll("#molecule-select option").length')==27,'Detective 27 supported starters include enriched14')
  for index,mission in enumerate(missions):
   wait(S+'.phase==="active"&&'+S+'.missionIndex==='+str(index));label=mid+'/'+mission['family']
   click('#check-answer');check(not read(S+'.correct'),'Detective empty rejected '+label)
   if mission['kind']=='atoms':wrong=next(atom['id'] for atom in snapshot['atoms'] if atom['element']=='H')
   else:
    byid={atom['id']:atom for atom in snapshot['atoms']}
    wrong=next(b['id'] for b in snapshot['bonds'] if byid[b['a']]['element']=='H' or byid[b['b']]['element']=='H')
   detective_pick(mission['kind'],wrong);click('#check-answer');check(not read(S+'.correct'),'Detective wrong H or C-H rejected '+label)
   click('#clear-selection');wait(S+'.atoms.length===0&&'+S+'.bonds.length===0')
   target=mission['accepted'][-1] # Alternate equivalent target when more than one exists.
   for i,identifier in enumerate(target):
    detective_pick(mission['kind'],identifier)
    if i==0 and len(target)>1:click('#check-answer');check(not read(S+'.correct'),'Detective partial target rejected '+label)
   click('#check-answer');wait(S+'.correct&&!document.getElementById("next-mission").hidden')
   OUT['correctUIAttempts'].append({'game':'detective','moleculeId':mid,'family':mission['family'],'acceptedTargetCount':len(mission['accepted']),'selectedTarget':target,'nativeState':read(S)})
   check(True,'Detective genuine production mission solved '+label)
   if index+1<len(missions):click('#next-mission')
  shot('detective-'+mid)
 check({a['moleculeId'] for a in OUT['correctUIAttempts'] if a['game']=='detective'}==NEW_IDS,'all six new Detective molecules genuinely solved in all available families')

try:
 startup=' server='+startup_and_rest.split(' # BEGIN_GAME_REPLAY',1)[0]
 exec(compile(textwrap.dedent(startup),'alkane-root-games-owned-startup','exec'))
 workshop_legacy_continuity();workshop_new_six();detective_new_six()
 check(not js_errors,'no captured JavaScript exceptions in Workshop/Detective',js_errors)
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:OUT['failureState']={'url':read('location.href'),'body':read('document.body.innerText.slice(-9000)'),'detective':read('typeof NameleculeMolecularDetective!=="undefined"?'+S+':null')};shot('failure')
 except Exception as capture:OUT['failureCaptureError']=repr(capture)
finally:
 cleanup=DRIVER.rsplit("\nfinally:\n OUT['javascriptErrors']",1)[1].split("\nif not OUT.get('completed')",1)[0]
 exec(compile(textwrap.dedent(" OUT['javascriptErrors']"+cleanup),'alkane-root-games-owned-cleanup','exec'))
if not OUT.get('completed'):raise SystemExit(1)
