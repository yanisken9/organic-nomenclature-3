"""Actual v54 authoring UI, with explicitly labelled recorded-response fixtures.

Writes evidence only. Drawing input is loaded into the real JSME editor; model
rendering, engine, generators, acceptance, menus and Blob saving remain real.
"""
from pathlib import Path
import os,json,time,traceback,hashlib
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104/drafts'
os.environ['NAMELECULE_BIDI_PORT']='9246';os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[],'failures':[],'stages':[],'fixturePolicy':'One real browser API attempt; then controlled async recorded PubChem fixtures. JSME drawing input simulation, real engine/render/generator/acceptance/save paths.'}
call('session.subscribe',{'events':['network.responseCompleted'],'contexts':[ctx]})

def read(expr):return json.loads(ev('(async()=>JSON.stringify(await ('+expr+')))()'))
def check(value,label,**details):
    row={'label':label,'passed':bool(value),**details};out['checks'].append(row)
    if not value:out['failures'].append(row)
    return bool(value)
def click(selector):
    for attempt in range(10):
        ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});new Promise(r=>setTimeout(r,100))')
        p=read('(()=>{const n=document.querySelector('+json.dumps(selector)+'),b=n.getBoundingClientRect(),hit=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return{x:b.x+b.width/2,y:b.y+b.height/2,hit:n.contains(hit)}})()')
        if p['hit']:break
    assert p['hit'],('Click intercepted',selector,p)
    call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':round(p['x']),'y':round(p['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
    time.sleep(.3)
def stage(label,fn):
    print('Draft stage:',label,flush=True)
    try:fn();out['stages'].append({'stage':label,'completed':True})
    except Exception as error:
        out['stages'].append({'stage':label,'completed':False,'error':str(error),'traceback':traceback.format_exc()})
        out['failures'].append({'stage':label,'error':str(error)})
        print(traceback.format_exc(),flush=True)
        try:screenshot(HERE/('failure-'+label+'.png'))
        except Exception:pass
    (HERE/'drafts-progress.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
def record_state():
    return read('({url:location.href,lang:fMulerLang(),selected:selectedMol,records:Object.keys(nameExamples).length,custom:window.nameExamplesCustom?Object.keys(window.nameExamplesCustom):[],draft:window.MulerDraft,mode:mode2D,chain:mainChainAtomsList,name:currentMolName})')
def model_count(count):
    until('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))==='+str(count),seconds=30)
def setmode(mode):
    index={'condensed':1,'expanded':2,'skeletal':3}[mode]
    if ev('mode2D')!=mode:click('.mode2DOption:nth-child('+str(index)+')')
    until('mode2D==='+json.dumps(mode)+'&&!!document.querySelector("#jsmeNomeclatureSVG svg")',seconds=20)
def load_drawing(kind):
    ev('jsmeEditDraftApplet.readMolFile(window.__draftFixtureMols['+json.dumps(kind)+']);true')
    until('fMolDraftReadDrawing().smiles.length>0',seconds=10)
def submit(count):
    click('#molDraftSubmitBtn')
    until('!!window.MulerDraft&&window.MulerDraft.submitted&&!window.MulerDraft.submitting&&window.MulerDraft.sdfDone',seconds=30)
    if count:model_count(count)
def new():
    if ev('!!window.MulerDraft'):click('#molDraftCancelBtn')
    click('#newMolBtn');until('!!window.MulerDraft')
def install_fixtures():
    records={}
    for name,parent in [('nonane',HERE.parent),('octane',HERE)]:
        props=json.loads((parent/(name+'-pubchem.json')).read_text())['PropertyTable']['Properties'][0]
        records[props['ConnectivitySMILES']]={'hit':{'source':'recorded-pubchem-fixture','cid':props['CID'],'iupac':props['IUPACName'],'iupacPubchem':props['IUPACName'],'title':props['Title'],'systematic':props['IUPACName'],'canonicalSmiles':props['ConnectivitySMILES'],'synonyms':[]},'sdf':(parent/(name+'-3d.sdf')).read_text()}
    records['C']={'hit':{'source':'local-template-fixture','cid':297,'iupac':'methane','iupacPubchem':'methane','title':'Methane','systematic':'methane','canonicalSmiles':'C','synonyms':[]},'sdf':(ROOT/'mols/nomeclature-moc2/methane_3D.sdf').read_text()}
    ev('window.__recordedDraftFixtures='+json.dumps(records)+';window.__fixtureCalls=[];window.__no3D=false;window.__downloads=[];'+r'''
 fFetchIUPAC_EN=async function(smiles){window.__fixtureCalls.push({kind:'name',smiles,mock:true});await new Promise(r=>setTimeout(r,60));const x=window.__recordedDraftFixtures[smiles];return x?JSON.parse(JSON.stringify(x.hit)):{source:'none',cid:null,iupac:null,iupacPubchem:null,title:null,systematic:null,synonyms:[]}};
 fFetchSDF3D_PubChem=async function(smiles){window.__fixtureCalls.push({kind:'3d',smiles,mock:true});await new Promise(r=>setTimeout(r,60));const x=window.__recordedDraftFixtures[smiles];return !window.__no3D&&x?x.sdf:null};
 fScenarioSaveBlobDownload=function(filename,blob){window.__downloadPending=blob.text().then(text=>window.__downloads.push({filename,text,type:blob.type}));return true};
 window.__draftFixtureMols={};for(const[n,kind]of[[9,'nonane'],[8,'octane']])window.__draftFixtureMols[kind]=fWriteMolV2000(['Authoring verification '+kind,'  Namelecule test input',''],Array.from({length:n},(_,i)=>({el:'C',x:i*1.17,y:0})),Array.from({length:n-1},(_,i)=>[i+1,i+2,1]));
 window.__draftFixtureMols.ring=fWriteMolV2000(['Ring negative control','',''],[{el:'C',x:0,y:0},{el:'C',x:1.17,y:0},{el:'C',x:.585,y:1.013}],[[1,2,1],[2,3,1],[3,1,1]]);true''')

def boot():
    navigate('mulermoc-nom-54.html?lang=gr&v=drafts-'+str(time.time_ns()));app_ready()
    until('!!jsmeEditDraftApplet&&window.JSmolReadyFlag===true',seconds=60)
    check(ev('Object.keys(nameExamples).length')==141,'Boot preserves 141 stored records')
    out['actualBrowserPubChemAttempt']=json.loads((HERE/'actual-browser-pubchem.json').read_text())
    out['actualBrowserPubChemEvidenceReused']=True
    time.sleep(1)
    install_fixtures()
    check(ev('document.getElementById("newMolBtn").classList.contains("hide")&&document.getElementById("editMolBtn").classList.contains("hide")'),'Master off hides New/Edit')
    ev('fNewMolDraft();true');check(not ev('!!window.MulerDraft'),'Master off handler guard rejects new draft')
    ev('window.__setupClicks=[];document.addEventListener("click",e=>window.__setupClicks.push({id:e.target.id,at:Date.now()}),true);true')
    click('#viewerSettingsBtn');click('#originalJSMECheck')
    out['masterAfterToggle']=read('({master:document.getElementById("originalJSMECheck").className,button:document.getElementById("newMolBtn").className,clicks:window.__setupClicks})')
    click('#viewerSettingsBtn')
    check(ev('!document.getElementById("newMolBtn").classList.contains("hide")&&!document.getElementById("editMolBtn").classList.contains("hide")'),'Master on exposes New/Edit')

def invalid_inputs():
    new();click('#molDraftSubmitBtn')
    check(ev('!!window.MulerDraft&&!window.MulerDraft.submitted'),'Empty drawing rejected')
    load_drawing('ring');click('#molDraftSubmitBtn')
    check(ev('!!window.MulerDraft&&!window.MulerDraft.submitted&&!window.MulerDraft.submitting'),'Ring rejected before accepting a preview')
    check(ev('!document.getElementById("molDraftSubmitBtn").disabled'),'Ring rejection leaves Submit usable')
    screenshot(HERE/'ring-rejection.png');click('#molDraftCancelBtn')

def create_custom():
    ev('document.getElementById("ethyl_3_dimethyl_2_5_hexane").click();true')
    until('selectedMol==="ethyl_3_dimethyl_2_5_hexane"')
    setmode('skeletal')
    check(ev('allAtomsTypeList.filter(t=>t==="C").length')==10,'Selected source template has ten carbon atoms')
    ev('window.__templateKeys=Object.keys(nameExamples);window.__templateSnapshot=JSON.stringify(Object.fromEntries(window.__templateKeys.map(k=>[k,nameExamples[k]])));window.__sourceMolSnapshot=JSON.stringify(window.MOL2D);true')
    new();load_drawing('nonane');submit(29)
    preview=read('({nameGR:MulerDraft.engineName,nameEN:MulerDraft.engineEN,atoms:allAtomsTypeList,chain:mainChainAtomsList,source:skeletalLayoutSource&&fParseMolV2000(skeletalLayoutSource.mol).atoms.map(a=>a.el),acceptDisabled:document.getElementById("molDraftAcceptBtn").disabled})')
    out['nonanePreview']=preview
    check(preview['nameEN']=='nonane' and preview['nameGR']=='εννεάνιο','Submit predicts GR and EN nonane',names=preview)
    check(preview['atoms'].count('C')==9 and len(preview['chain'])==9 and preview['source'].count('C')==9,'Skeletal draft preview uses live nine-carbon drawing')
    check(not preview['acceptDisabled'],'PubChem-backed inline 29-atom preview enables Accept')
    screenshot(HERE/'nonane-preview-1500.png')
    click('#molDraftDrawBtn');load_drawing('octane')
    ev('fMolDraftAccept();true')
    check(ev('window.MulerDraft.stale&&Object.keys(nameExamples).length===141'),'Changed drawing blocks stale Accept')
    submit(26)
    check(ev('MulerDraft.engineEN==="octane"&&mainChainAtomsList.length===8'),'Resubmit recomputes changed drawing')
    click('#molDraftDrawBtn');load_drawing('nonane');submit(29)
    click('#molDraftAcceptBtn');until('!window.MulerDraft&&selectedMol.startsWith("custom_")')
    out['nonaneKey']=ev('selectedMol');model_count(29)
    check(ev('Object.keys(nameExamples).length===142&&Object.keys(window.nameExamplesCustom).length===1'),'Accept creates one session custom record')
    check(ev('!!document.getElementById(selectedMol)&&document.getElementById(selectedMol).classList.contains("selectedLi")'),'Accepted custom menu entry selected')
    check(ev('JSON.stringify(Object.fromEntries(window.__templateKeys.map(k=>[k,nameExamples[k]])))===window.__templateSnapshot&&JSON.stringify(window.MOL2D)===window.__sourceMolSnapshot'),'All 141 original records and stored 2D forms remain unchanged')
    check(ev('window.__downloads.length===0'),'Accept does not silently download files')
    out['acceptedNonane']=read('window.nameExamplesCustom[selectedMol]')

def variants_and_layout():
    key=out['nonaneKey'];ev((ROOT/'tools/2d-label-probe.js').read_text());out['variantAudits']=[]
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        for mode in ['condensed','expanded','skeletal']:
            setmode(mode)
            check(ev('currentMolName')==out['acceptedNonane']['grName'],'Accepted '+mode+' naming preserved '+str(width))
            atoms=read('allAtomsTypeList')
            check(atoms.count('C')==9 and atoms.count('H')==(20 if mode=='expanded' else 0),'Generated sibling graph atoms '+mode+' '+str(width),atoms=len(atoms))
            check(ev('mainChainAtomsList.length')==9,'Parent length nine '+mode+' '+str(width))
            if ev('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length')!=9:ev('document.querySelector("#nameAnalysis #comp5").click();true')
            until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===9',seconds=10)
            audit=read('auditFinalSvg().then(x=>x)');audit['width']=width;out['variantAudits'].append(audit)
            clean=not audit['clipped']and not audit['raster']['inkWithinHalfCssPixelOfBond']and not audit['raster']['fullyHiddenLineCount']
            check(clean,'Shared label/font/gap/frame probe '+mode+' '+str(width),clipped=audit['clipped'],raster=audit['raster'])
            check(len(audit['numbers'])==9,'Numbering follows generated parent '+mode+' '+str(width))
            if width==390:screenshot(HERE/('nonane-'+mode+'-390.png'))
        data_disabled=ev('document.querySelector("#radioChainMode .radioCheckContainer").classList.contains("disabledRadio")')
        check(data_disabled,'No authored chain uses algorithmic parent fallback '+str(width))
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
    click('#view3DBtn');check(not ev('document.querySelector("#view3DBtn").classList.contains("active")'),'Custom 3D can hide')
    click('#view3DBtn');model_count(29);check(True,'Custom inline 3D survives view switch')
    click('#view2DBtn');click('#view2DBtn');until('!!document.querySelector("#jsmeNomeclatureSVG svg")')
    check(True,'Custom 2D survives view switch')

def update_and_fork():
    key=out['nonaneKey'];setmode('skeletal')
    ev('window.__sameRecordRef=nameExamples[selectedMol];window.__beforeEdit=JSON.stringify(nameExamples[selectedMol]);true')
    click('#editMolBtn');until('!!window.MulerDraft&&MulerDraft.sourceIsCustom')
    ev('(()=>{const m=fParseMolV2000(fMolDraftReadDrawing().molText);m.atoms.forEach(a=>{a.x+=.35;a.y+=.2});jsmeEditDraftApplet.readMolFile(fWriteMolV2000(m.head,m.atoms,m.bonds,m))})();true')
    submit(29)
    check(ev('fMolDraftIsSameMolecule()&&MulerDraft.acceptKey==="draftUpdate"'),'Same custom identity chooses Update')
    click('#molDraftAcceptBtn');until('!window.MulerDraft')
    check(ev('selectedMol')==key and ev('nameExamples[selectedMol]===window.__sameRecordRef'),'Same molecule updates stable key and object')
    updated=read('nameExamples[selectedMol]');out['updatedNonane']=updated
    check(len(updated['history'])==2 and updated['history'][-1]['action']=='updated','Update appends history')
    check(all(updated.get('structure2D_'+suffix)for suffix in ['Condensed','Expanded','Skeletal']),'Update keeps all three representation slots')
    ev('window.__beforeFork=JSON.stringify(nameExamples[selectedMol]);true')
    click('#editMolBtn');load_drawing('octane');submit(26)
    check(ev('!fMolDraftIsSameMolecule()&&MulerDraft.acceptKey==="draftAccept"'),'Changed custom molecule chooses fork Accept')
    click('#molDraftAcceptBtn');until('!window.MulerDraft&&selectedMol!=='+json.dumps(key))
    out['octaneKey']=ev('selectedMol');out['acceptedOctane']=read('nameExamples[selectedMol]')
    check(ev('Object.keys(window.nameExamplesCustom).length')==2,'Changed-molecule Edit forks a second record')
    check(ev('JSON.stringify(nameExamples['+json.dumps(key)+'])===window.__beforeFork'),'Fork preserves original custom record')

def negative_acceptance():
    ev('document.getElementById("methane").click();true');until('selectedMol==="methane"')
    setmode('condensed');click('#editMolBtn');submit(5)
    click('#molDraftAcceptBtn')
    check(ev('!!window.MulerDraft&&Object.keys(nameExamples).length===143'),'Stored-template duplicate blocked')
    screenshot(HERE/'duplicate-template.png');click('#molDraftCancelBtn')
    new();load_drawing('nonane');ev('window.__no3D=true;true');submit(None)
    check(ev('!MulerDraft.sdf3D&&document.getElementById("molDraftAcceptBtn").classList.contains("btnInactive")'),'No PubChem 3D leaves Accept unavailable')
    ev('fMolDraftAccept();true');check(ev('!!window.MulerDraft&&Object.keys(nameExamples).length===143'),'No-3D authoritative guard preserves records')
    screenshot(HERE/'missing-pubchem-3d.png');click('#molDraftCancelBtn');ev('window.__no3D=false;true')

def save_and_reload_losses():
    if ev('!!window.MulerDraft'):click('#molDraftCancelBtn')
    key=out['nonaneKey'];ev('document.getElementById('+json.dumps(key)+').click();true');until('selectedMol==='+json.dumps(key))
    click('#viewerSettingsBtn');click('#customMolSaveBtn')
    until('window.__downloads.length===1')
    saved=read('window.__downloads[0]');out['manualSave']={'filename':saved['filename'],'type':saved['type']}
    (HERE/saved['filename']).write_text(saved['text'])
    prefix='window.nameExamplesCustom = Object.assign(window.nameExamplesCustom || {}, '
    data=saved['text'].split(prefix,1)[1].rsplit(');',1)[0]
    payload=json.loads(data);out['manualSave']['validJSONRecord']=list(payload)
    (HERE/'saved-payload.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    check(list(payload)==[key]and payload[key]['sdf3D']and all(payload[key]['structure2D_'+suffix]for suffix in ['Condensed','Expanded','Skeletal']),'Manual Blob save contains one complete reimportable custom record')
    click('#viewerSettingsBtn')
    out['beforeAcceptedLanguageReload']=record_state()
    click('[data-lang="en"]');until('location.search.includes("lang=en")',seconds=20);app_ready()
    out['afterAcceptedLanguageReload']=record_state()
    preserved=ev('!!nameExamples['+json.dumps(key)+']')
    check(preserved,'Accepted session custom survives language reload',before=out['beforeAcceptedLanguageReload']['custom'],after=out['afterAcceptedLanguageReload']['custom'])
    screenshot(HERE/'accepted-custom-language-reload.png')
    # An independent fresh unsaved scenario uses a stored molecule, separating
    # scenario loss from the custom-registration question.
    ev('document.getElementById("propene").click();fScenarioSetAuthoring(true);window.__unsavedScenario=fScenarioNew("draft-check-unsaved-language",true);fScenarioBuildPanels();true')
    ev('(()=>{const s=fScenarioCapture();if(!s)throw Error("capture failed");fScenarioActive().steps.push(s);fScenarioSyncLegacy();fScenarioRenderList(fScenarioActive().id)})();true')
    out['beforeUnsavedScenarioReload']=read('({url:location.href,scenarios:MuLERMoCScenario.scenarios.map(s=>({id:s.id,title:s.title,steps:s.steps.length})),active:MuLERMoCScenario.activeId})')
    click('[data-lang="gr"]');until('location.search.includes("lang=gr")',seconds=20);app_ready()
    out['afterUnsavedScenarioReload']=read('({url:location.href,scenarios:MuLERMoCScenario.scenarios.map(s=>({id:s.id,title:s.title,steps:s.steps.length})),active:MuLERMoCScenario.activeId})')
    exists=ev('MuLERMoCScenario.scenarios.some(s=>s.title==="draft-check-unsaved-language"&&s.steps.length===1)')
    check(exists,'Unsaved authoring scenario survives language reload',before=out['beforeUnsavedScenarioReload'],after=out['afterUnsavedScenarioReload'])
    screenshot(HERE/'unsaved-scenario-language-reload.png')
    out['savedPayload']=payload

def reimport():
    global ctx
    payload=out['savedPayload'];oldctx=ctx
    ctx=call('browsingContext.create',{'type':'tab'})['context']
    call('session.subscribe',{'events':['log.entryAdded','network.responseCompleted'],'contexts':[ctx]})
    preload=call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':'()=>{window.nameExamplesCustom='+json.dumps(payload)+';}'})['script']
    try:
        navigate('mulermoc-nom-54.html?lang=gr&v=draft-reimport-'+str(time.time_ns()));app_ready()
        key=out['nonaneKey'];check(ev('Object.keys(nameExamples).length===142&&!!nameExamples['+json.dumps(key)+']'),'Fresh registration imports saved custom alongside 141 templates')
        ev('document.getElementById('+json.dumps(key)+').click();true');until('selectedMol==='+json.dumps(key))
        model_count(29)
        for mode in ['condensed','expanded','skeletal']:
            setmode(mode)
            check(ev('allAtomsTypeList.filter(t=>t==="C").length===9&&mainChainAtomsList.length===9'),'Fresh import selects '+mode+' graph and parent')
        out['reimportState']=record_state();screenshot(HERE/'reimported-nonane.png')
        check(True,'Fresh import inline 29-atom model rendered')
    finally:
        call('script.removePreloadScript',{'script':preload});call('browsingContext.close',{'context':ctx});ctx=oldctx

try:
 payload=json.loads((HERE/'saved-payload.json').read_text());key=next(iter(payload));out['nonaneKey']=key;out['acceptedNonane']=payload[key]
 call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':'()=>{window.nameExamplesCustom='+json.dumps(payload)+';}'})
 navigate('mulermoc-nom-54.html?lang=gr&v=draft-probes-'+str(time.time_ns()));app_ready();until('!!jsmeEditDraftApplet&&window.JSmolReadyFlag===true');time.sleep(1)
 ev('document.getElementById('+json.dumps(key)+').click();true');until('selectedMol==='+json.dumps(key));model_count(29);install_fixtures()
 stage('variants-layout-numbering',variants_and_layout)
 click('#viewerSettingsBtn');click('#originalJSMECheck');click('#viewerSettingsBtn')
 new();load_drawing('nonane');ev('window.__no3D=true;true');submit(None)
 out['no3D']=read('({sdf:MulerDraft.sdf3D,sdfDone:MulerDraft.sdfDone,pubchem:MulerDraft.pubchem,acceptClass:document.getElementById("molDraftAcceptBtn").className,records:Object.keys(nameExamples).length})')
 check(out['no3D']['sdf']is None and 'btnInactive'in out['no3D']['acceptClass'],'No PubChem 3D shows inactive Accept')
 ev('fMolDraftAccept();true');check(ev('!!window.MulerDraft&&Object.keys(nameExamples).length===142'),'No-3D direct Accept remains blocked without changing records')
 screenshot(HERE/'missing-pubchem-3d-final.png');click('#molDraftCancelBtn')
 out['completed']=True
finally:
 out['javascriptErrors']=js_errors;out['diagnostics']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in['error','warn']]
 out['sourceHashesAtEnd']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((ROOT/'js').glob('*54.js'))}
 (HERE/'targeted-layout-no3d-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'failures':out['failures'],'javascriptErrors':len(js_errors)},ensure_ascii=False),flush=True)
