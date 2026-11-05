// Tests load the complete source in the same lexical context. Applet/DOM mocks
// isolate the asynchronous transaction, while parser/mapper/generators are real.
var window = {addEventListener:function(){}};
var messages=[], timers=[], delays=[], fixtures=[], registryWrites=0, selectedCalls=0;
var console={log:function(){},warn:function(){}};
function setTimeout(fn,ms){timers.push({fn:fn,ms:ms});delays.push(ms);return timers.length;}
function clearTimeout(){}
function classes(initial){var data=new Set(initial||[]);return {add:function(v){data.add(v);},remove:function(v){data.delete(v);},contains:function(v){return data.has(v);},toggle:function(v,on){if(on)data.add(v);else data.delete(v);}};}
function el(tag){return {tagName:tag,children:[],classList:classes(),style:{setProperty:function(){}},attributes:{},appendChild:function(n){this.children.push(n);n.parentNode=this;},setAttribute:function(k,v){this.attributes[k]=v;},getAttribute:function(k){return this.attributes[k];},set innerHTML(v){this.children=[];},get innerHTML(){return '';},get textContent(){return this._text || this.children.map(function(c){return c.textContent;}).join('');},set textContent(v){this._text=String(v);this.children=[];}};}
var nodes={};
var document={documentElement:el('html'),body:el('body'),addEventListener:function(){},getElementById:function(id){return nodes[id]||null;},querySelectorAll:function(){return [];},createElement:el};
var $=function(){return {addClass:function(){},removeClass:function(){},html:function(){}};};
var nameExamples={};
var fFetchIUPAC_EN, fFetchSDF3D_PubChem;
var copied=null,navigator={clipboard:{writeText:function(text){copied=text;return Promise.resolve();}}};
// INSERT ACTUAL SOURCE
var results=[];
function check(condition,message){if(!condition)throw new Error(message);}
function test(name,fn){try{fn();results.push({name:name,pass:true});}catch(e){results.push({name:name,pass:false,error:String(e)+'\n'+String(e.stack||'')});}}
function settle(p){var done=false,error=null;p.then(function(){done=true;},function(e){error=e;done=true;});for(var i=0;!done&&i<100;i++){drainMicrotasks();if(!done){check(timers.length,'promise stranded without timer');timers.shift().fn();}}drainMicrotasks();check(done,'promise did not settle');if(error)throw error;}
function atom(x,y,el,charge,isotope){return {x:x,y:y,z:0,el:el||'C',charge:charge||0,isotope:isotope||0};}
function mol(atoms,bonds){return fWriteMolV2000(['test','generated',''],atoms,bonds);}
var drawn=mol([atom(0,0),atom(1,0),atom(2,0),atom(3,0)],[[1,2,1],[2,3,1],[3,4,1]]);
var zigzag=mol([atom(0,0),atom(1,0),atom(1.5,0.866),atom(2.5,0.866)],[[1,2,1],[2,3,1],[3,4,1]]);
function shortHeader(m){var lines=m.split('\n');lines.splice(2,1);return lines.join('\n');}
var emptyMol=mol([],[]);
function applet(prior,outputs,options){
 var a={content:prior,scale:2.75,imports:[],reads:0,restores:[],scales:[],clears:0,active:false};options=options||{};
 a.molFile=function(){if(a.active){a.reads++;if(options.readThrow)throw new Error('read failure');var out=outputs[Math.min(a.reads-1,outputs.length-1)];if(out!==undefined)a.content=out;}return a.content;};
 a.getMolecularAreaScale=function(){return a.scale;};a.setMolecularAreaScale=function(v){a.scales.push(v);a.scale=v;};
 a.clear=function(){a.clears++;a.content=emptyMol;a.active=false;if(options.clearThrow)throw new Error('clear failure');};
 a.readGenericMolecularInput=function(s){a.imports.push(s);a.active=true;a.scale=99;if(options.importHook)options.importHook();if(options.importThrow)throw new Error('import failure');};
 a.readMolFile=function(text){a.restores.push(text);a.content=text;a.active=false;};a.repaint=function(){};a.deferredRepaint=function(){};
 a.hasMolecule=function(){return true;};a.getSmiles=function(){return 'CCCC';};return a;
}
// These record navigation/UI effects; the acceptance code, model generators,
// parser and exact heavy mapper continue to execute from the actual source.
var showEditorCalls=0,tidyCalls=0;
fSelectMol=function(){selectedCalls++;};fInitNomeclatureMenu=function(){};fMolDraftSyncButtons=function(){};
fMolDraftToast=function(msg){messages.push(msg);};fMolDraftShowEditor=function(){showEditorCalls++;};
fMolDraftExpandedFormula=function(){return 'CH3CH2CH2CH3';};fMolDraftRefreshAcceptKey=function(){};
var actualZigzag=fZigzagMol;
function setup(displayOut,editOut,opts){
 nodes={};['molDraftSubmitBtn','molDraftAcceptBtn','molDraftDrawBtn','molDraftBeautifyBtn','molDraftStatus','jsmeEditDraft'].forEach(function(id){nodes[id]=el('div');});
 nodes.jsmeEditDraft.classList.add('hide');nodes.autoLinearizeCheck=el('div');nodes.autoLinearizeCheck.classList.add('selectedCheck');
 timers=[];delays=[];messages=[];selectedCalls=0;showEditorCalls=0;nameExamples={};window.nameExamplesCustom={};window.MulerDraftAcquisition=null;
 selectedMol='source';mode2D='condensed';mainChainAtomsList=[1,2,3,4];allAtomsTypeList=['saved'];bondList=[];allAtomsTypeList3D=['saved3D'];bondList3D=[];
 window.MulerDraft={mode:'new',variant:'condensed',submitted:true,engineName:'βουτάνιο',engineEN:'butane',smiles:'CCCC',molText:drawn,pubchem:{cid:9999,canonicalSmiles:'canonical-CCCC'},sdfDone:true,sdf3D:'fixture SDF'};
 jsmeNomeclatureApplet=applet('actual display transient',displayOut||[zigzag],opts&&opts.display);
 jsmeEditDraftApplet=applet(drawn,editOut||[zigzag],opts&&opts.edit);
 fZigzagMol=actualZigzag;
 return window.MulerDraft;
}
function accepted(){var keys=Object.keys(window.nameExamplesCustom);check(keys.length===1,'expected exactly one accepted record, got '+keys.length);return window.nameExamplesCustom[keys[0]];}
test('JSME canonical display wins with reordered exact graph and restores actual MOL/scale',function(){
 var reordered=mol([atom(2.5,0.866),atom(1.5,0.866),atom(1,0),atom(0,0)],[[1,2,1],[2,3,1],[3,4,1]]);
 setup([shortHeader(reordered)]);var display=jsmeNomeclatureApplet,edit=jsmeEditDraftApplet;var builtins=0;fZigzagMol=function(){builtins++;return zigzag;};settle(fMolDraftAccept());var rec=accepted();
 check(rec.structure2D_Skeletal===shortHeader(reordered),'reordered display result must win');check(display.imports.join()==='canonical-CCCC','must import canonical input');check(!edit.imports.length&&!builtins,'later rungs must not run');
 check(display.content==='actual display transient'&&display.scale===2.75,'restore actual prior display and scale');check(edit.content===drawn,'edit untouched');check(rec.canonicalSmiles==='canonical-CCCC','persist canonical');check(window.MulerDraft===null&&!window.MulerDraftAcquisition,'transaction released');
});
test('Truncated and wrong-heavy reads wait, input once, settle on sixth read',function(){
 setup(['stub V2000',emptyMol,'stub V2000',emptyMol,'stub V2000',shortHeader(zigzag)]);var a=jsmeNomeclatureApplet;settle(fMolDraftAccept());check(accepted().structure2D_Skeletal===shortHeader(zigzag),'settled output selected');check(a.reads===6&&a.imports.length===1,'six reads one input');check(delays.filter(function(x){return x===120;}).length===5,'five exact120ms gaps');
});
test('Exhausted six-read display falls through edit, never unbounded',function(){
 setup(['stub V2000'],[zigzag]);var a=jsmeNomeclatureApplet,b=jsmeEditDraftApplet;settle(fMolDraftAccept());check(accepted().structure2D_Skeletal===zigzag,'edit wins');check(a.reads===6&&b.reads===1,'bounded display then edit');check(a.content==='actual display transient'&&b.content===drawn&&a.scale===2.75&&b.scale===2.75,'both applets restored');
});
test('Echo (rotation/translation/scale) and same-count wrong graph fall through validated builtin',function(){
 var echo=mol([atom(4,5),atom(4,7),atom(4,9),atom(4,11)],[[1,2,1],[2,3,1],[3,4,1]]);
 var wrong=mol([atom(0,0),atom(1,0),atom(1,1),atom(2,0)],[[1,2,1],[2,3,1],[2,4,1]]);
 setup([echo],[wrong]);var count=0;fZigzagMol=function(){count++;return zigzag;};settle(fMolDraftAccept());check(accepted().structure2D_Skeletal===zigzag&&count===1,'must reject both bad JSME rungs');
});
test('Collapsed bond rejected despite exact graph',function(){
 var collapsed=mol([atom(0,0),atom(0,0),atom(1,1),atom(2,1)],[[1,2,1],[2,3,1],[3,4,1]]);
 setup([collapsed],[zigzag]);settle(fMolDraftAccept());check(accepted().structure2D_Skeletal===zigzag&&jsmeEditDraftApplet.imports.length===1,'collapsed display falls through');
});
test('Charge and isotope mismatches rejected; valid metadata preserved',function(){
 var charged=mol([atom(0,0,'C',1,13),atom(1,0),atom(2,0),atom(3,0)],[[1,2,1],[2,3,1],[3,4,1]]);
 var good=mol([atom(0,0,'C',1,13),atom(1,0),atom(1.5,0.866),atom(2.5,0.866)],[[1,2,1],[2,3,1],[3,4,1]]);
 setup([zigzag],[good]);window.MulerDraft.molText=charged;jsmeEditDraftApplet.content=charged;settle(fMolDraftAccept());var rec=accepted(),parsed=fParseMolV2000(rec.structure2D_Skeletal);check(rec.structure2D_Skeletal===good,'metadata-aware edit wins');check(parsed.atoms[0].charge===1&&parsed.atoms[0].isotope===13,'metadata retained');
});
test('Double Accept and Draw/Submit/Beautify stay blocked during acquisition',function(){
 var d=setup(['stub V2000',zigzag]);var pending=fMolDraftAccept();check(d.accepting&&window.MulerDraftAcquisition===d,'lock acquired synchronously');
 check(nodes.molDraftAcceptBtn.disabled&&nodes.molDraftDrawBtn.disabled&&nodes.molDraftSubmitBtn.disabled&&nodes.molDraftBeautifyBtn.disabled,'native controls disabled');
 settle(fMolDraftAccept());fMolDraftBackToEdit();settle(fMolDraftSubmit());fMolDraftBeautify();check(showEditorCalls===0,'draw/beautify must not open editor');check(jsmeNomeclatureApplet.imports.length===1,'duplicate must not acquire');settle(pending);accepted();
});
test('Cancel during wait defers teardown until restore and creates no record',function(){
 var d=setup(['stub V2000',zigzag]);var a=jsmeNomeclatureApplet;var pending=fMolDraftAccept();fMolDraftCancel();check(window.MulerDraft===d&&d.cancelRequested,'cancel is deferred');check(!a.restores.length&&selectedCalls===0,'no early restore/reselect');settle(pending);
 check(window.MulerDraft===null&&!window.MulerDraftAcquisition&&!Object.keys(nameExamples).length,'no stale registration');check(a.content==='actual display transient'&&a.scale===2.75,'restored before teardown');check(selectedCalls===1,'cancel reselect once');
});
test('Replacement draft during wait receives neither stale applet restoration nor registration',function(){
 var d=setup(['stub V2000',zigzag]);var a=jsmeNomeclatureApplet;var pending=fMolDraftAccept();var next={marker:'new draft'};window.MulerDraft=next;a.content='replacement molecule';a.active=false;settle(pending);
 check(window.MulerDraft===next&&a.content==='replacement molecule'&&!a.restores.length&&!a.scales.length,'old content must not overwrite replacement');check(!Object.keys(nameExamples).length&&!d.accepting&&!window.MulerDraftAcquisition,'no registration or lock leak');
});
test('Selection/mode change during wait prevents stale restoration and record creation',function(){
 setup(['stub V2000',zigzag]);var a=jsmeNomeclatureApplet;var pending=fMolDraftAccept();selectedMol='another';mode2D='skeletal';a.content='new selected view';a.active=false;settle(pending);
 check(a.content==='new selected view'&&!a.restores.length&&!Object.keys(nameExamples).length,'do not overwrite navigation or register');check(!window.MulerDraftAcquisition,'lock released');
});
test('Import, clear and read failures restore actual content and scale then fall through',function(){
 ['importThrow','clearThrow','readThrow'].forEach(function(failure){var opt={};opt[failure]=true;setup(['bad'],[zigzag],{display:opt});var a=jsmeNomeclatureApplet;settle(fMolDraftAccept());accepted();check(a.content==='actual display transient'&&a.scale===2.75,'restoration after '+failure);});
});
test('Explicit H stripped in accepted generated condensed and expanded not doubled',function(){
 setup([zigzag]);var expanded=fGenExpandedMol(drawn);check(fParseMolV2000(expanded).atoms.length===14,'fixture explicitH');window.MulerDraft.molText=expanded;jsmeEditDraftApplet.content=expanded;settle(fMolDraftAccept());var rec=accepted();check(fParseMolV2000(rec.structure2D_Condensed).atoms.length===4,'heavy-only condensed');check(fParseMolV2000(rec.structure2D_Expanded).atoms.length===14,'ten hydrogen expansion once');
});
test('Two/three header annotation and skeletal transform are equivalent, metadata/headers retained',function(){
 var three=zigzag,two=shortHeader(three),chain=[1,2,3,4];
 check((fMakeAnnotatedSkeletal(three).match(/\[C\]/g)||[]).length===4,'three header annotation');check((fMakeAnnotatedSkeletal(two).match(/\[C\]/g)||[]).length===4,'two header annotation');
 var a=fSkeletalLayoutMol(three,chain),b=fSkeletalLayoutMol(two,chain);check(Math.abs(a.rotation-b.rotation)<1e-9,'same rotation');var ap=fParseMolV2000(a.mol),bp=fParseMolV2000(b.mol);check(JSON.stringify(ap.atoms)===JSON.stringify(bp.atoms),'same transformed atoms');check(fMolCountsLine(b.mol.split('\n'))===2,'short header preserved');check(a.mol.split('\n').slice(8).join('\n')===three.split('\n').slice(8).join('\n'),'noncoordinate data retained');
});
test('Canonical info SMILES/link/name/copy agree; invalid CID stays plain text',function(){
 setup();nodes.moleculeInfo=el('div');molInfoOpenFlag=true;nameExamples.source={smiles:'drawn',canonicalSmiles:'canonical',pubchemCID:123,iupacPubchem:'butane'};
 fRenderMolInfo();var box=nodes.moleculeInfo;check(box.children[0].children[1].children[0].textContent==='canonical','canonical shown');check(box.children[0].children[1].children[0].href==='https://pubchem.ncbi.nlm.nih.gov/compound/123','CID link');check(box.children[1].children[1].children[0].textContent==='butane','name linked');fCopyMolSmiles();check(copied==='canonical','copy shown value');
 nameExamples.source.pubchemCID='invalid';fRenderMolInfo();check(nodes.moleculeInfo.children[0].children[1].children.length===0&&nodes.moleculeInfo.children[0].children[1].textContent==='canonical','invalid CID plain');
});
test('Default automatic setting and manual Linearize visibility follow current draft/view',function(){
 setup();delete nodes.autoLinearizeCheck;check(fMolDraftAutoLinearizeOn(),'missing checkbox defaults ON');nodes.autoLinearizeCheck=el('div');check(!fMolDraftAutoLinearizeOn(),'unchecked means manual');nodes.jsmeEditDraft.classList.remove('hide');fMolDraftSyncBar();check(!nodes.molDraftBeautifyBtn.classList.contains('hide'),'manual school editor shows Linearize');nodes.autoLinearizeCheck.classList.add('selectedCheck');fMolDraftSyncBar();check(nodes.molDraftBeautifyBtn.classList.contains('hide'),'auto mode hides manual');nodes.autoLinearizeCheck.classList.remove('selectedCheck');window.MulerDraft.mode='edit';window.MulerDraft.variant='skeletal';fMolDraftSyncBar();check(nodes.molDraftBeautifyBtn.classList.contains('hide'),'skeletal mode hides school Linearize');
});
test('Shared auto-tidy uses fresh sandbox chain, regenerates expanded H, skeletal passes through',function(){
 setup();var original=fMolDraftSandboxAnalyse;var sandboxCalls=0;fMolDraftSandboxAnalyse=function(){sandboxCalls++;mainChainAtomsList=[1,2,3,4];mainChainMode='algorithmic';return {ok:true,ring:false};};
 try{mainChainMode='data';jsmeEditDraftApplet.content=zigzag;var tidy=fMolDraftAutoTidy();check(tidy&&fParseMolV2000(tidy.molText).atoms.length===4,'school auto tidy output');check(mainChainMode==='data'&&sandboxCalls===1,'restores mode after fresh sandbox');
 window.MulerDraft.mode='edit';window.MulerDraft.variant='expanded';jsmeEditDraftApplet.content=fGenExpandedMol(zigzag);tidy=fMolDraftAutoTidy();check(tidy&&fParseMolV2000(tidy.molText).atoms.length===14,'expanded H regenerated once');
 window.MulerDraft.variant='skeletal';var originalMol=jsmeEditDraftApplet.content;var before=sandboxCalls;tidy=fMolDraftAutoTidy();check(tidy.molText===originalMol&&sandboxCalls===before,'skeletal geometry untouched');
 }finally{fMolDraftSandboxAnalyse=original;}
});
test('Submit identity guard rejects old oracle against replacement with same SMILES',function(){
 setup();window.MulerDraft.submitted=false;nodes.autoLinearizeCheck.classList.remove('selectedCheck');
 var original=fMolDraftSandboxAnalyse,svg=fUpdateSVG,render=fMolDraftRenderPreview,view=fMolDraftShowPreviewView;
 var resolveFetch;fMolDraftSandboxAnalyse=function(){currentMolName='butane';return {ok:true,ring:false};};fUpdateSVG=function(){};fMolDraftRenderPreview=function(){};fMolDraftShowPreviewView=function(){};
 fFetchIUPAC_EN=function(){return new Promise(function(resolve){resolveFetch=resolve;});};
 // Make the fetch visible in the actual Submit lexical environment.
 window._identityFetch=fFetchIUPAC_EN;
 try{var old=window.MulerDraft;var pending=fMolDraftSubmit();check(old.submitting,'submit running');var replacement={smiles:'CCCC',marker:'replacement'};window.MulerDraft=replacement;resolveFetch({cid:1});settle(pending);check(window.MulerDraft===replacement&&!replacement.pubchem&&!replacement.sdfDone,'old same-SMILES result does not mutate replacement');}
 finally{fMolDraftSandboxAnalyse=original;fUpdateSVG=svg;fMolDraftRenderPreview=render;fMolDraftShowPreviewView=view;}
});
test('Charge-only and isotope-only mismatches independently fall through to matching edit',function(){
 var charged=mol([atom(0,0,'C',1,13),atom(1,0),atom(2,0),atom(3,0)],[[1,2,1],[2,3,1],[3,4,1]]);
 var good=mol([atom(0,0,'C',1,13),atom(1,0),atom(1.5,0.866),atom(2.5,0.866)],[[1,2,1],[2,3,1],[3,4,1]]);
 [[0,13],[1,0]].forEach(function(meta){var bad=mol([atom(0,0,'C',meta[0],meta[1]),atom(1,0),atom(1.5,0.866),atom(2.5,0.866)],[[1,2,1],[2,3,1],[3,4,1]]);setup([bad],[good]);window.MulerDraft.molText=charged;jsmeEditDraftApplet.content=charged;settle(fMolDraftAccept());check(accepted().structure2D_Skeletal===good,'single-field metadata mismatch must reject');});
});
test('Submit identity guard rejects old SDF against replacement with same SMILES',function(){
 setup();window.MulerDraft.submitted=false;nodes.autoLinearizeCheck.classList.remove('selectedCheck');
 var original=fMolDraftSandboxAnalyse,svg=fUpdateSVG,render=fMolDraftRenderPreview,view=fMolDraftShowPreviewView,show3D=fMolDraftShow3D;
 var resolveSDF,showCalls=0;fMolDraftSandboxAnalyse=function(){currentMolName='butane';return {ok:true,ring:false};};fUpdateSVG=function(){};fMolDraftRenderPreview=function(){};fMolDraftShowPreviewView=function(){};fMolDraftShow3D=function(){showCalls++;};
 fFetchIUPAC_EN=function(){return Promise.resolve({cid:9999});};fFetchSDF3D_PubChem=function(){return new Promise(function(resolve){resolveSDF=resolve;});};
 try{var pending=fMolDraftSubmit();drainMicrotasks();check(typeof resolveSDF==='function','at SDF await');var replacement={smiles:'CCCC',marker:'replacement'};window.MulerDraft=replacement;resolveSDF('old SDF');settle(pending);check(window.MulerDraft===replacement&&!replacement.sdf3D&&!replacement.sdfDone&&!showCalls,'old same-SMILES SDF must not mutate/show replacement');}
 finally{fMolDraftSandboxAnalyse=original;fUpdateSVG=svg;fMolDraftRenderPreview=render;fMolDraftShowPreviewView=view;fMolDraftShow3D=show3D;}
});
var failed=results.filter(function(r){return !r.pass;});print(JSON.stringify({passed:results.length-failed.length,total:results.length,results:results},null,2));if(failed.length)quit(1);
