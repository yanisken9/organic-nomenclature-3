"""Syntax, bounded changed regions and real SyncBar visibility behavior."""
from pathlib import Path
import json, subprocess, hashlib, re
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
VIEW=ROOT/'js/mulermoc-nom-molview-54.js'
BEFORE=ROOT/'docs/checks/v54-upstream-20261104/before/js/mulermoc-nom-molview-54.js'
s=VIEW.read_text();b=BEFORE.read_text()
def parts(text):
    a=text.index('function fMolDraftSyncBar(');z=text.index('\nfunction ',a+1)
    c=text.index('function fMolDraftAccept(');d=text.index('\nfunction ',c+1)
    return [text[:a],text[z:c],text[d:]]
checks=[]
def check(ok,label):
    checks.append({'ok':bool(ok),'label':label})
    assert ok,label
check(parts(s)==parts(b),'All bytes outside fMolDraftSyncBar/fMolDraftAccept unchanged')
check('skeletalLayoutSource = mode2D === \'skeletal\' && molText' in s,'Live-draft skeletal source retained')
start=s.index('function fMolDraftSyncBar(');end=s.index('\nfunction ',start+1)
code='new Function('+json.dumps(s)+');\n'+s[start:end]+r'''
var checks=[];
function check(ok,label){checks.push({ok:!!ok,label});if(!ok)throw Error(label)}
function classes(initial){var x=new Set(initial||[]);return {add:v=>x.add(v),remove:v=>x.delete(v),contains:v=>x.has(v)}}
for(var editor of [true,false])for(var variant of ['condensed','expanded','skeletal','condensedZigZag']){
 var window={MulerDraft:{mode:'edit',variant,submitted:true,submitting:false,stale:false,pubchem:{},sdf3D:'3D'}};
 var nodes={};['molDraftSubmitBtn','molDraftAcceptBtn','molDraftDrawBtn','molDraftBeautifyBtn'].forEach(id=>nodes[id]={classList:classes()});
 nodes.jsmeEditDraft={classList:classes(editor?[]:['hide'])};
 var document={getElementById:id=>nodes[id]};fMolDraftSyncBar();
 check(nodes.molDraftBeautifyBtn.classList.contains('hide')===(!editor||variant==='skeletal'||variant==='condensedZigZag'),
  'Beautify editor='+editor+' variant='+variant);
 check(nodes.molDraftAcceptBtn.classList.contains('active')===!editor,'Accept editor='+editor+' variant='+variant);
 check(nodes.molDraftSubmitBtn.classList.contains('active')===editor,'Submit editor='+editor+' variant='+variant);
}
print(JSON.stringify(checks));
'''
p=subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True)
assert p.returncode==0,p.stdout+p.stderr
checks+=json.loads(p.stdout)
checks.append({'ok':True,'label':'Whole viewer compiles in JavaScriptCore'})
(HERE/'preservation-results.json').write_text(json.dumps({'checks':checks,'viewerSHA256':hashlib.sha256(VIEW.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(checks)}))
