var window = this;
var console = { log:function(){}, warn:function(){}, error:function(){} };
var navigator = { onLine:true };
var selectedMol = 'fixture', mode2D = 'condensed';
var allAtomsTypeList=[], bondList=[], allAtomsTypeList3D=[], bondList3D=[];
var mainChainAtomsList=[1,2,3], nameComponentsList=['fixture'], mainChainMode='algorithmic';
var nameExamples={}, nameExamplesCustom={}, molInfoOpenFlag=true;
var jsmeNomeclatureApplet=null, jsmeEditDraftApplet=null;
var jmolAppletNomeclature={id:'applet'}, JSmolReadyFlag=true;
var fMolDraft3DRevision=0, fMolDraft3DJob=null, fMolDraft3DWriter=null;
var MOLMIN_STEPS=500,MOLMIN_FURTHER_STEPS=200,MOLMIN_WAIT_S=10;
var fMolDraftMinWaitEl=null,fMolDraftMinWaitKey=null,fMolDraftMinWaitPrevFocus=null,fMolDraftMinWaitTimer=null,fMolDraftMinWaitJob=null;
var _intervals=[];
function setInterval(fn,ms){var t={fn:fn,ms:ms,cancel:false};_intervals.push(t);return t;}
function clearInterval(t){if(t)t.cancel=true;}
var _timers=[], _writes=[], _reads=[], _model=null, _confirm=null, _toasts=[], _downloads=[];
var _docElements={};
function element() { return {children:[],classList:{add:function(){},remove:function(){},toggle:function(){},contains:function(){return false;}},setAttribute:function(k,v){this[k]=v;},appendChild:function(n){this.children.push(n); n.parentNode=this;},removeChild:function(n){this.children=this.children.filter(function(x){return x!==n;});},querySelector:function(k){this.queries=this.queries||{};return this.queries[k]||(this.queries[k]=element());},focus:function(){},style:{setProperty:function(){}}}; }
var document={getElementById:function(id){return _docElements[id] || null;},querySelectorAll:function(){return [];},createElement:element,addEventListener:function(){},removeEventListener:function(){},contains:function(){return false;},body:element(),documentElement:element()};
function setTimeout(fn,ms){var t={fn:fn,ms:ms,cancel:false};_timers.push(t);return t;}
function clearTimeout(t){if(t)t.cancel=true;}
function nextTimer(){var t;while((t=_timers.shift())){if(!t.cancel){t.fn();drainMicrotasks();return t.ms;}}return null;}
function settle(p){var done=false,val,err;p.then(function(v){done=true;val=v;},function(e){done=true;err=e;});drainMicrotasks();for(var i=0;!done&&i<30;i++){if(nextTimer()===null)break;}if(err)throw err;if(!done)throw Error('unsettled promise');return val;}
function fMolDraftPresenting(){return false;}
function fJSmolLive(){return true;}
function fMulerNotePending3D(){}
function fMolDraftT(k,f){return f || k;}
function fMulerT(k){return k==='draft3DProvisional'?'Provisional 3D — geometry and convergence unverified.':k;}
function fMolDraftToast(t){_toasts.push(t);}
function fMolDraftSyncBar(){}
function fMolDraftRenderPreview(){}
function fMolDraftShow3D(s){_model=s;}
function fMolDraftIsSameMolecule(){return !!window.MulerDraft.same;}
function fMolDraftRefreshAcceptKey(){}
function fMolDraftReadDrawing(){return {hasAny:true,molText:window.MulerDraft.molText,smiles:window.MulerDraft.smiles};}
function fMolDraftMakeKey(){return 'custom_new';}
function fMolDraftExpandedFormula(){return 'C3H8';}
function fGetMoleculeClassification(){return {chemicalClass:'alkanes'};}
function fMolDraftTeardownDisplay(){fMolDraft3DInvalidate();window.MulerDraft=null;}
function fInitNomeclatureMenu(){}
function fSelectMol(){}
function fMolDraftSyncButtons(){}
function fScenarioConfirm(msg,cb,label){_confirm={msg:msg,cb:cb,label:label};}
function fMolDraftFileSlug(rec){return rec.key+'.js';}
function Blob(parts,opts){this.parts=parts;this.type=opts.type;}
function fScenarioSaveBlobDownload(file,blob){_downloads.push({file:file,text:blob.parts.join('')});return true;}
var Jmol={script:function(a,cmd){_writes.push(cmd);if(cmd.indexOf('load data "model.sdf"')>=0){_model=cmd.split('load data "model.sdf"\n')[1].split('end "model.sdf"')[0];}return '';},scriptWait:function(a,cmd){return this.script(a,cmd);},scriptEcho:function(a,cmd){_reads.push(cmd);return _model;}};
function assert(ok,msg){if(!ok)throw Error(msg);}
var results=[];
function test(name,fn){try{fn();results.push({name:name,pass:true});}catch(e){results.push({name:name,pass:false,error:String(e)});}}
function atom(el,x,y,z,extra){return Object.assign({el:el,x:x,y:y,z:z||0},extra||{});}
function mol(atoms,bonds){return fWriteMolV2000(['fixture','  fixture 3D',''],atoms,bonds,{});}
function fixture(){return mol([atom('C',0,0,0),atom('C',1,0,0),atom('C',2,0,0)],[[1,2,1],[2,3,1]]);}
function reset(){fMolDraft3DInvalidate();_timers=[];_intervals=[];_writes=[];_reads=[];_confirm=null;_toasts=[];_downloads=[];selectedMol='fixture';mode2D='condensed';jsmeNomeclatureApplet=null;jsmeEditDraftApplet=null;nameExamples={};nameExamplesCustom={};window.MulerDraftAcquisition=null;window._mulerNewCustomKeys={};window.MULER_SKIP_REMOTE3D=false;navigator.onLine=true;_model=fixture();window.MulerDraft={_epoch:1,_submitId:1,smiles:'CCC',molText:fixture(),submitted:true,sdfDone:true,engineName:'προπάνιο',pubchem:null,expectHeavy:3,mode:'new',variant:'condensed',stale:false};}
