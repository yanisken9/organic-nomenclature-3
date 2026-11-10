from pathlib import Path
import ast,json,hashlib,re,subprocess,datetime
P=Path.cwd();E=P/'docs/checks/v54-merge-20261109/viewer';D=E/'rv55-03';C=Path('/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate');V=C/'js/mulermoc-nom-molview-55.js';CORE=C/'js/mulermoc-nom-core-55.js'
def fn(src,name):
 matches=list(re.finditer(r'^(?:async )?function (\w+)\(',src,re.M));idx=next(i for i,m in enumerate(matches)if m.group(1)==name)
 return src[matches[idx].start():matches[idx+1].start()if idx+1<len(matches)else len(src)]
assign={n.targets[0].id:ast.literal_eval(n.value)for n in ast.parse((E/'test-viewer.py').read_text()).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('core_names','viewer_names')}
v=V.read_text();core=CORE.read_text();diag=json.loads((E.parent/'browser/reload-readback-diagnostic.json').read_text());reference=diag['submittedMol'];readback=diag['readbacks'][0]['text']
source=(E/'test-prelude.js').read_text()+'\n'+'\n'.join(fn(core,n)for n in assign['core_names'])+'\n'+'\n'.join(fn(v,n)for n in assign['viewer_names']+['fMolDraftNormalizeJSmolReadback'])+'\n'+(E/'test-cases.js').read_text().split('print(JSON.stringify({cases:results.length')[0]
tests=r'''
var c8ref=REFERENCE,c8raw=READBACK;
function normValid(raw,ref){var n=fMolDraftNormalizeJSmolReadback(raw,ref);return n && fMolDraftValidSDF3D(n,8,ref);}
function changeAtom(s,i,field,val){var ls=s.split('\n'),slots={parity:[39,42],mass:[34,36],charge:[36,39]};var q=slots[field];ls[4+i]=ls[4+i].substring(0,q[0])+String(val).padStart(q[1]-q[0],' ')+ls[4+i].substring(q[1]);return ls.join('\n');}
test('RV55-03 captured C8 writer parity rejected at raw import but readback normalized',function(){assert(fMolDraftValidSDF3D(c8ref,8,c8ref),'reference invalid');assert(!fMolDraftValidSDF3D(c8raw,8,c8ref),'raw import unexpectedly allowed');var n=fMolDraftNormalizeJSmolReadback(c8raw,c8ref);assert(fMolDraftValidSDF3D(n,8,c8ref),'normalized rejected');var a=c8raw.split('\n'),b=n.split('\n'),changed=0;for(var i=0;i<a.length;i++){if(a[i]!==b[i]){changed++;assert(a[i].substring(0,39)===b[i].substring(0,39)&&a[i].substring(42)===b[i].substring(42),'changed otherfields');}}assert(changed===6,'not exactly6parities');});
test('RV55-03 parity1 and CRLF preserve all otherbytes',function(){var s=c8raw.replace(/\n/g,'\r\n');s=changeAtom(s,0,'parity',1);var n=fMolDraftNormalizeJSmolReadback(s,c8ref);assert(n.indexOf('\r\n')>=0&&fMolDraftValidSDF3D(n,8,c8ref),'CRLF failed');});
test('RV55-03 stereo reference rejected without normalization',function(){assert(!fMolDraftNormalizeJSmolReadback(c8raw,changeAtom(c8ref,0,'parity',1)),'stereo reference accepted');});
test('RV55-03 unknown parity3 stays unsupported',function(){assert(!normValid(changeAtom(c8raw,0,'parity',3),c8ref),'unknown parity accepted');});
test('RV55-03 isotope mismatch survives normalization and rejected',function(){assert(!normValid(changeAtom(c8raw,0,'mass',1),c8ref),'isotope mismatch accepted');});
test('RV55-03 carbon charge mismatch survives normalization and rejected',function(){assert(!normValid(changeAtom(c8raw,0,'charge',3),c8ref),'charge mismatch accepted');});
test('RV55-03 H/D cannot establish equivalent-H center',function(){assert(!normValid(changeAtom(c8raw,8,'mass',1),c8ref),'H/D accepted');});
test('RV55-03 charged H cannot establish equivalent-H center',function(){assert(!normValid(changeAtom(c8raw,8,'charge',3),c8ref),'charged H accepted');});
test('RV55-03 one-H potentialC* parity remains failclosed',function(){var s=mol([atom('C',0,0),atom('H',1,0),atom('F',0,1),atom('Cl',-1,0),atom('Br',0,-1)],[[1,2,1],[1,3,1],[1,4,1],[1,5,1]]);var raw=changeAtom(s,0,'parity',2);assert(fMolDraftNormalizeJSmolReadback(raw,s)===raw,'potentialC* changed');assert(!fMolDraftValidSDF3D(raw,4,s),'potentialC* accepted');});
test('RV55-03 query and wedge fields remain failclosed',function(){var ls=c8raw.split('\n');var b=30;ls[b]=ls[b].padEnd(12,' ');ls[b]=ls[b].substring(0,9)+'  1'+ls[b].substring(12);assert(!normValid(ls.join('\n'),c8ref),'wedge accepted');ls=c8raw.split('\n');ls[4]=ls[4].substring(0,31)+'*  '+ls[4].substring(34);assert(!normValid(ls.join('\n'),c8ref),'query accepted');});
test('RV55-03 topology mismatch remains rejected after parity normalization',function(){var ls=c8raw.split('\n');ls[30]='  1  4  1';assert(!normValid(ls.join('\n'),c8ref),'wrong topology accepted');});
test('RV55-03 clean input bytes remain unchanged',function(){assert(fMolDraftNormalizeJSmolReadback(c8ref,c8ref)===c8ref,'clean bytes changed');});
print(JSON.stringify({cases:results.length,passed:results.filter(function(r){return r.pass;}).length,results:results}));
if(results.some(function(r){return !r.pass;}))quit(1);
'''.replace('REFERENCE',json.dumps(reference)).replace('READBACK',json.dumps(readback))
source+='\n'+tests;(D/'actual-functions-under-test.js').write_text(source)
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','actual-functions-under-test.js'],cwd=D,capture_output=True,text=True);(D/'output.txt').write_text(r.stdout+r.stderr)
assert r.returncode==0,(r.stdout[-6000:],r.stderr)
report=json.loads(r.stdout.splitlines()[0]);report.update({'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'Developer actualfunctionJSC controlled applet/DOM/network plus exact captured realJSmol rawC8 fixture; not independentreview or physicalminimization','runtimeSHA256':hashlib.sha256(V.read_bytes()).hexdigest(),'coreSHA256':hashlib.sha256(CORE.read_bytes()).hexdigest(),'original55Included':True})
(D/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in ('cases','passed','runtimeSHA256')}))
