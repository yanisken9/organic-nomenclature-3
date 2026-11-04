"""Reuse bounded acceptance suite, plus real library geometry Accept/Update.
Actual acceptance/core; mock applets and PubChem preconditions, no browser claim.
"""
from pathlib import Path
import json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
support=(ROOT/'docs/checks/v54-upstream-20261104/drawing/test-drawing.py').read_text()
# Reuse setup and generated test JavaScript without executing its output writes.
namespace={'__file__':str(ROOT/'docs/checks/v54-upstream-20261104/drawing/test-drawing.py')}
exec(compile(support.split('p=subprocess.run([JSC,',1)[0],'<drawing acceptance setup>','exec'),namespace)
base=namespace['factories']['after']
base=base.replace("var source=shapes[cfg.source||'line'];","var source=cfg.molText||shapes[cfg.source||'line'];")
base=base.replace("mainChainAtomsList=cfg.source==='one'?[1]:[1,2,3,4];","mainChainAtomsList=cfg.chain||(cfg.source==='one'?[1]:[1,2,3,4]);")
js=namespace['js']
# Replace final print with extra representative geometry checks and one result.
js=js[:js.rfind('print(JSON.stringify(')]
js+='\nvar libraryAccept=new Function("cfg",'+json.dumps(base)+');\n'
data=(ROOT/'js/jsme-nick-nomeclature-moc2-data_54.js').read_text()
js+='var catalog=(new Function('+json.dumps('var window={};'+data+';return window.MOL2D;')+'))();\n'
rows=json.loads((HERE/'geometry-results.json').read_text())['rows']
probes=[r for r in rows if r['key']in ['diethyl_ether','ethyl_propyl_ether','butyne_1','propadiene','butadiene_1_2']and r['mode']=='condensed']
assert len(probes)==5
js+='var probes='+json.dumps([{'key':r['key'],'chain':r['chain']}for r in probes])+';\n'
js+=r'''
function molAngles(text){var lines=text.split(/\r?\n/),n=+lines[3].slice(0,3),nb=+lines[3].slice(3,6),
 atoms=lines.slice(4,4+n).map(l=>({x:+l.slice(0,10),y:+l.slice(10,20),el:l.slice(31,34).trim()})),adj=atoms.map(()=>[]);
 lines.slice(4+n,4+n+nb).forEach(l=>{var a=+l.slice(0,3)-1,b=+l.slice(3,6)-1,o=+l.slice(6,9);adj[a].push([b,o]);adj[b].push([a,o])});
 return atoms.flatMap((a,i)=>{var ns=adj[i];if(ns.length!==2||!['C','O'].includes(a.el))return [];
 var p=atoms[ns[0][0]],q=atoms[ns[1][0]],u=[p.x-a.x,p.y-a.y],v=[q.x-a.x,q.y-a.y],
 angle=Math.acos(Math.max(-1,Math.min(1,(u[0]*v[0]+u[1]*v[1])/(Math.hypot(...u)*Math.hypot(...v)))))*180/Math.PI,
 target=a.el==='C'&&(ns.some(n=>n[1]===3)||ns.every(n=>n[1]===2))?180:120;
 return [{atom:i+1,angle,target,error:Math.abs(angle-target)}]})}
var representative=[];
for(var probe of probes)for(var update of [false,true]){
 var r=libraryAccept({molText:catalog[probe.key].condensed,chain:probe.chain,variant:'skeletal',update});
 var label=probe.key+' '+(update?'Update':'Accept'),angles=molAngles(r.slot);
 check(r.accepted&&r.logs.some(l=>l.includes('builtin ok')),label+' wins deterministic builtin');
 check(angles.every(a=>a.error<0.02),label+' has correct C/O/sp angles',angles);
 check(r.stateRestored&&r.cachePreserved,label+' preserves live engine mapping state');
 check(!update||r.customIdentity&&r.history[r.history.length-1].action==='updated',label+' preserves update contract');
 representative.push({key:probe.key,update,angles,source:r.logs.find(l=>l.includes('builtin ok'))});
}
print(JSON.stringify({runtime:'JavaScriptCore actual Accept/Update with mocked external/app inputs',checks,representative,observed}));
'''
p=subprocess.run([namespace['JSC'],'-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True)
assert p.returncode==0,p.stdout+p.stderr
result=json.loads(p.stdout);result['coreSHA256']=hashlib.sha256((ROOT/'js/mulermoc-nom-core-54.js').read_bytes()).hexdigest()
(HERE/'acceptance-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(result['checks']),'representativeAcceptUpdate':len(result['representative'])}))
