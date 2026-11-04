"""Bounded acceptance ladder regression: actual viewer functions + pure core.
Python stdlib/macOS JavaScriptCore. Mocked applet faults, no browser claims.
Run from repo root; outputs only the selected drawing evidence directory.
"""
from pathlib import Path
import json, subprocess, hashlib

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'

def function(text, name):
    start = text.index('function '+name+'(')
    end = text.find('\nfunction ', start + 1)
    return text[start:end if end >= 0 else len(text)]

core = (ROOT/'js/mulermoc-nom-core-54.js').read_text()
viewers = {
    'before': ROOT/'docs/checks/v54-upstream-20261104/before/js/mulermoc-nom-molview-54.js',
    'upstream': ROOT/'docs/checks/v54-upstream-20261104/upstream/35d791ee9d6bdb8566d3adca1a1bdaba97efc5b8/js/mulermoc-nom-molview-54.js',
    'after': ROOT/'js/mulermoc-nom-molview-54.js',
}
HARNESS = r'''
var logs=[],toasts=[],window={},document={getElementById:()=>null,querySelectorAll:()=>[]};
var console={log:(...v)=>logs.push(v.join(' ')),warn:(...v)=>logs.push(v.join(' '))};
var selectedMol='original',nameExamples={},mode2D='skeletal',molZoom2D=1.7;
function fMolDraftPresenting(){return false}
function fMolDraftT(k,f){return f}
function fMolDraftToast(v){toasts.push(v)}
function fMolDraftReadDrawing(){return {smiles:cfg.stale?'CC':'CCCC'}}
function fMolDraftIsSameMolecule(){return !!cfg.update}
function fMolDraftMakeKey(){return 'accepted'}
function fMolDraftTeardownDisplay(){window.MulerDraft=null}
function fMolDraftExpandedFormula(){return 'C4H10'}
function atom(x,y,el){return {x,y,el:el||'C'}}
var line=fWriteMolV2000(['Source','',''],[atom(0,0),atom(1,0),atom(2,0),atom(3,0)],[[1,2,1],[2,3,1],[3,4,1]]);
var equalSum=fWriteMolV2000(['Zigzag','',''],[atom(0,-0.2887),atom(1,0.2887),atom(2,-0.2887),atom(3,0.2887)],[[1,2,1],[2,3,1],[3,4,1]]);
function change(text,mutate){var p=fParseMolV2000(text);mutate(p);return fWriteMolV2000(p.head,p.atoms,p.bonds,p)}
var translated=change(line,p=>p.atoms.forEach(a=>{a.x+=10;a.y+=5}));
var formatted=change(line,p=>p.head[0]='Formatted header');
var rotated=change(line,p=>p.atoms.forEach(a=>{var x=a.x;a.x=10-2*a.y;a.y=5+2*x}));
var builtinZig=fZigzagMol(line,[1,2,3,4]);
var shapes={line,equalSum,translated,formatted,rotated,builtinZig,expanded:fGenExpandedMol(line),
  invalid:'bad MOL',nan:line.replace('    0.0000','       NaN'),
  collapsed:change(line,p=>p.atoms.forEach(a=>{a.x=0;a.y=0})),
  wrongHeavy:change(line,p=>p.atoms[3].el='O'),
  wrongBonds:change(line,p=>p.bonds[1][2]=2),
  wrongTopology:change(line,p=>p.bonds=[[1,2,1],[2,3,1],[2,4,1]]),
  wrongCharge:change(line,p=>p.atoms[0].charge=1),
  wrongIsotope:change(line,p=>p.atoms[0].isotope=13),
  wrongMass:change(line,p=>p.atoms[0].tail=' 1'+p.atoms[0].tail.slice(2)),
  one:fWriteMolV2000(['One','',''],[atom(0,0)],[])};
var source=shapes[cfg.source||'line'];
window.MulerDraft={submitted:true,engineName:'probe',smiles:'CCCC',molText:source,
 mode:cfg.variant?'edit':'new',variant:cfg.variant||'condensed',pubchem:cfg.no3d?null:{cid:999},
 sdfDone:!cfg.pending,sdf3D:cfg.no3d?null:'3D',sourceIsCustom:!!(cfg.update||cfg.template),sourceMol:(cfg.update||cfg.template)?'custom':null};
if(cfg.update||cfg.template){nameExamples.custom={history:[],smiles:cfg.template?'CC':'CCCC',pubchemCID:cfg.template?998:999,structure2D_Skeletal:'template-original'};window.nameExamplesCustom={custom:nameExamples.custom}}
if(cfg.duplicate)nameExamples.existing={smiles:'CCCC'};
mainChainAtomsList=cfg.source==='one'?[1]:[1,2,3,4];
var stateA=['engine2D'],stateB=[[7,8,1]],stateC=['engine3D'],stateD=[[9,10,1]],cache={kept:true};
allAtomsTypeList=stateA;bondList=stateB;allAtomsTypeList3D=stateC;bondList3D=stateD;
molAtomMap2D3D=cache;molAtomMapKey='cached-key';molAtomMapSource3D='cached-source';
if(cfg.mapperThrows)fBuildHeavyMap2D3D=()=>{throw Error('mapper injected')};
var builtinCalls=0,originalBuiltin=fZigzagMol;
fZigzagMol=function(text,chain){builtinCalls++;if(cfg.builtin==='throw')throw Error('builtin injected');
 return cfg.builtin===undefined?originalBuiltin(text,chain):shapes[cfg.builtin]};
function applet(spec,label){
 spec=spec||{};
 var prior=label==='display'?shapes.rotated:shapes.formatted,content=prior,scale=label==='display'?2.3:0.8;
 var oldScale=scale,calls=[],clearCalls=0,readCalls=0;
 return {calls,prior,oldScale,content:()=>content,scale:()=>scale,
  molFile(){calls.push('mol');readCalls++;if(spec.readThrows===readCalls)throw Error('read injected');return content},
  getMolecularAreaScale(){return scale},setMolecularAreaScale(v){calls.push('scale');scale=v},
  clear(){calls.push('clear');clearCalls++;if(spec.clearThrows&&clearCalls===1)throw Error('clear injected');if(!spec.clearNoop)content=''},
  readGenericMolecularInput(){calls.push('import');scale=9;if(spec.importThrows)throw Error('import injected');
   if(!spec.noop)content=shapes[spec.output||'equalSum']},
  deferredRepaint(){calls.push('deferred');if(spec.repaintThrows)throw Error('repaint injected')},
  repaint(){calls.push('repaint')},readMolFile(v){calls.push('restore');content=v},
 };
}
var jsmeNomeclatureApplet=cfg.noDisplay?null:applet(cfg.display,'display');
var jsmeEditDraftApplet=cfg.noEdit?null:applet(cfg.edit,'edit');
fMolDraftAccept();
var rec=nameExamples.accepted||(cfg.update?nameExamples.custom:null);
return {accepted:!!rec&&!!rec.structure2D_Skeletal,slot:rec&&rec.structure2D_Skeletal,
 C:rec&&rec.structure2D_Condensed,E:rec&&rec.structure2D_Expanded,
 source,shapes,selectedMol,logs,toasts,builtinCalls,
 display:jsmeNomeclatureApplet&&{calls:jsmeNomeclatureApplet.calls,
 restored:jsmeNomeclatureApplet.content()===jsmeNomeclatureApplet.prior,scale:jsmeNomeclatureApplet.scale()===jsmeNomeclatureApplet.oldScale},
 edit:jsmeEditDraftApplet&&{calls:jsmeEditDraftApplet.calls,
 restored:jsmeEditDraftApplet.content()===jsmeEditDraftApplet.prior,scale:jsmeEditDraftApplet.scale()===jsmeEditDraftApplet.oldScale},
 stateRestored:allAtomsTypeList===stateA&&bondList===stateB&&allAtomsTypeList3D===stateC&&bondList3D===stateD,
 cachePreserved:molAtomMap2D3D===cache&&molAtomMapKey==='cached-key'&&molAtomMapSource3D==='cached-source',
 customIdentity:!cfg.update||nameExamples.custom===window.nameExamplesCustom.custom,
 templatePreserved:!cfg.template||nameExamples.custom.structure2D_Skeletal==='template-original',
 history:rec&&rec.history,keys:Object.keys(nameExamples)};
'''
# Function declarations are evaluated together; the core source supplies actual
# parser/generators/mapper, while viewer functions retain actual guard logic.
factories = {}
for key,path in viewers.items():
    text=path.read_text()
    factories[key]=core+'\n'+function(text,'fMolDraftNorm')+'\n'+function(text,'fMolDraftAccept')+'\n'+HARNESS

js='\n'.join('var '+k+'=new Function("cfg",'+json.dumps(v)+');' for k,v in factories.items())
js+=r'''
var checks=[],observed=[];
function check(ok,label,detail){checks.push({label,ok:!!ok,detail:detail||null});if(!ok)throw Error(label+':'+JSON.stringify(detail))}
function trial(cfg,label,shape){var r=after(cfg);check(r.accepted,label+' accepts');
 if(shape)check(r.slot===r.shapes[shape],label+' chooses '+shape,r.logs);
 check(r.stateRestored&&r.cachePreserved,label+' preserves engine lists/cache');
 [r.display,r.edit].filter(Boolean).forEach((a,i)=>check(a.restored&&a.scale,label+' restores applet '+i,a.calls));
 return r}
function upstreamObservation(cfg,label,expected){var r=upstream(cfg),b=before(cfg);observed.push({label,
 upstreamSlot: r.slot===r.shapes[expected]?'expected':r.slot===r.source?'drawn fallback':'other',
 upstreamLogs:r.logs,beforeSlot:b.slot===b.shapes[expected]?'expected':b.slot===b.source?'drawn fallback':'other'});return r}
var u=upstreamObservation({builtin:'equalSum',noDisplay:true,noEdit:true},'different zigzag shares coordinate sums','equalSum');
check(u.slot===u.source,'reproduced upstream equal-sum false rejection');
u=upstreamObservation({builtin:'invalid',display:{output:'equalSum'},noEdit:true},'invalid builtin blocks valid display','equalSum');
check(u.slot===u.source,'reproduced upstream invalid builtin blocks next rung');
u=upstreamObservation({builtin:'invalid',display:{output:'translated'},noEdit:true},'translated echo masks unchanged geometry','translated');
// Exercise the echo path without builtin blocking it.
u=upstream({builtin:'throw',display:{output:'translated'},noEdit:true});
check(u.slot===u.shapes.translated,'reproduced upstream translated echo false acceptance');
observed.push({label:'translated echo direct rung',upstreamAcceptedEcho:true,logs:u.logs});
trial({builtin:'equalSum',noDisplay:true,noEdit:true},'equal sums changed geometry','equalSum');
var fixed=trial({source:'builtinZig',builtin:'builtinZig',update:true,variant:'skeletal'},'builtin fixed point update','builtinZig');
check(fixed.logs.some(l=>l.includes('builtin ok'))&&!fixed.display.calls.length&&!fixed.edit.calls.length,'fixed point wins builtin before applet fallbacks');
check(fixed.customIdentity&&fixed.keys.join()==='custom'&&fixed.history[fixed.history.length-1].action==='updated','same custom molecule update keeps registry identity/key/history');
var fork=trial({template:true},'changed custom molecule forks','builtinZig');
check(fork.keys.includes('custom')&&fork.keys.includes('accepted')&&fork.templatePreserved,'fork preserves template and creates fresh key');
trial({source:'one',builtin:'one',variant:'skeletal'},'single heavy atom fixed point','one');
trial({source:'expanded'},'explicit H source maps to heavy-only builtin','builtinZig');
trial({source:'wrongIsotope',builtin:'wrongIsotope'},'isotope fixed point preserves isotope','wrongIsotope');
trial({source:'wrongCharge',builtin:'wrongCharge'},'charge fixed point preserves charge','wrongCharge');
for(var bad of ['invalid','nan','collapsed','wrongHeavy','wrongBonds','wrongTopology','wrongCharge','wrongIsotope','wrongMass']){
 var r=trial({builtin:bad,display:{output:'equalSum'},noEdit:true},'invalid builtin '+bad+' proceeds to display','equalSum');
 check(r.display.calls.includes('import'),'invalid '+bad+' actually imports next rung');
}
for(var echo of ['translated','formatted','rotated']){
 var r=trial({builtin:'throw',display:{output:echo},edit:{output:'equalSum'}},'display '+echo+' echo proceeds to edit','equalSum');
 check(r.logs.some(l=>l.includes('display rejected (unchanged internal geometry)')),'echo diagnosis '+echo,r.logs);
}
for(var field of ['clearThrows','importThrows','repaintThrows','clearNoop','noop']){
 var spec={};spec[field]=true;
 var r=trial({builtin:'invalid',display:spec,edit:{output:'equalSum'}},'display '+field+' restores and continues','equalSum');
 if(field==='clearNoop')check(!r.display.calls.includes('import'),'silent clear failure cannot import over stale applet');
 if(field==='noop')check(r.display.calls.filter(c=>c==='import').length===2,'synchronous immediate retry exercised');
}
for(var n of [1,2,3,4])trial({builtin:'invalid',display:{readThrows:n},edit:{output:'equalSum'}},'display read exception '+n+' safe','equalSum');
var r=trial({builtin:'invalid',display:{output:'wrongCharge'},edit:{output:'equalSum'}},'invalid display graph proceeds to edit','equalSum');
r=trial({variant:'skeletal'},'skeletal edit regenerates via builtin','builtinZig');
check(!r.display.calls.length&&!r.edit.calls.length,'valid builtin leaves applets untouched');
r=trial({variant:'condensedZigZag'},'annotated skeletal edit regenerates','builtinZig');
r=trial({builtin:'invalid',mapperThrows:true,display:{output:'equalSum'},edit:{output:'equalSum'}},'mapper exceptions preserve engine state','line');
for(var guard of ['stale','no3d','pending','duplicate']){
 var cfg={};cfg[guard]=true;var r=after(cfg);
 check(!r.accepted&&r.builtinCalls===0,guard+' guard prevents derivation',r.toasts);
 check(r.stateRestored&&r.cachePreserved,guard+' guard keeps engine state');
}
r=trial({variant:'expanded'},'expanded drawn slot preserved');check(r.E===r.source,'expanded source retained verbatim');
r=trial({variant:'condensed'},'condensed drawn slot preserved');check(r.C===r.source,'condensed source retained verbatim');
print(JSON.stringify({runtime:'JavaScriptCore actual acceptance/core with mocked applets',checks,observed,
 limitations:['Not a browser or live JSME/PubChem check','Immediate synchronous retry does not await asynchronous layout','Echo uses one exact graph mapping; symmetric reordered atoms may select another correspondence','Unsupported stereo/query/ambiguous transformation metadata fails closed to drawn fallback']}));
'''
p=subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True)
if p.returncode:
    raise SystemExit(p.stdout+'\n'+p.stderr)
result=json.loads(p.stdout)
result['sourceSHA256']={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in viewers.items()}
result['coreSHA256']=hashlib.sha256((ROOT/'js/mulermoc-nom-core-54.js').read_bytes()).hexdigest()
(HERE/'acceptance-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(result['checks']),'upstreamReproductions':len(result['observed'])}))
