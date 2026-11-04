"""All available Main54 source forms: actual naming chain + skeletal generator.
Python stdlib/macOS JavaScriptCore, no browser/dependency claims.
"""
from pathlib import Path
import json,subprocess,argparse,hashlib
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
TAIL=r'''
function load(text){var p=fParseMolV2000(text);
 jsmeNomeclatureApplet={totalNumberOfAtoms:()=>p.atoms.length,totalNumberOfBonds:()=>p.bonds.length,
 getAtom:(m,i)=>({label:p.atoms[i-1].el}),getBond:(m,i)=>({atoms:p.bonds[i-1].slice(0,2),order:p.bonds[i-1][2]}),molFile:()=>text};
 fAnalyseStructure();fDetectMolType();fInitNamingProps();fGuessName()}
function angles(m){var adj=m.atoms.map(()=>[]);m.bonds.forEach(b=>{if(m.atoms[b[0]-1].el==='H'||m.atoms[b[1]-1].el==='H')return;
 adj[b[0]-1].push([b[1]-1,b[2]]);adj[b[1]-1].push([b[0]-1,b[2]])});
 return m.atoms.flatMap((a,i)=>{if(adj[i].length!==2||!['C','O'].includes(a.el))return [];
 var ns=adj[i],p=m.atoms[ns[0][0]],q=m.atoms[ns[1][0]],u=[p.x-a.x,p.y-a.y],v=[q.x-a.x,q.y-a.y];
 var cosine=(u[0]*v[0]+u[1]*v[1])/(Math.hypot(...u)*Math.hypot(...v));
 var angle=Math.acos(Math.max(-1,Math.min(1,cosine)))*180/Math.PI;
 var sp=a.el==='C'&&(ns.some(b=>b[1]===3)||ns.every(b=>b[1]===2));
 if(a.el==='O'&&!ns.every(b=>b[1]===1))return [];
 return [{atom:i+1,element:a.el,orders:ns.map(b=>b[1]),angle,target:sp?180:120,error:Math.abs(angle-(sp?180:120))}];})}
function localAngles(m){var out=[],adj=m.atoms.map(()=>[]);m.bonds.forEach(b=>{if(m.atoms[b[0]-1].el!=='H'&&m.atoms[b[1]-1].el!=='H'){adj[b[0]-1].push(b[1]-1);adj[b[1]-1].push(b[0]-1)}});
 adj.forEach((ns,i)=>{for(var a=0;a<ns.length;a++)for(var b=0;b<a;b++){
 var p=m.atoms[ns[a]],q=m.atoms[ns[b]],c=m.atoms[i],u=[p.x-c.x,p.y-c.y],v=[q.x-c.x,q.y-c.y];
 var angle=Math.acos(Math.max(-1,Math.min(1,(u[0]*v[0]+u[1]*v[1])/(Math.hypot(...u)*Math.hypot(...v)))))*180/Math.PI;
 out.push({atom:i+1,neighbors:[ns[b]+1,ns[a]+1],degree:ns.length,angle,cross:u[0]*v[1]-u[1]*v[0]})}});return out}
function groupVectors(m){var groups={};m.properties.forEach(p=>{var f=p.trim().split(/\s+/);if(f[1]==='SAL')groups[f[2]]=(groups[f[2]]||[]).concat(f.slice(4).map(Number))});
 return m.properties.every(p=>{var f=p.trim().split(/\s+/);if(f[1]!=='SBV')return true;var ids=groups[f[2]],b=m.bonds[+f[3]-1];
 if(!ids||!b)return false;var a=m.atoms[b[0]-1],c=m.atoms[b[1]-1];var sign=ids.includes(b[0])?1:-1;
 return Math.abs(sign*(c.x-a.x)-Number(f[4]))<0.00015&&Math.abs(sign*(c.y-a.y)-Number(f[5]))<0.00015})}
function graph(m){return JSON.stringify([m.atoms.map(a=>{var o=Object.assign({},a);delete o.x;delete o.y;delete o.z;o.tail=(o.tail||'').slice(5);return o}),
 m.bonds.map(b=>[...b,b.tail,b.sourceIndex]),m.properties.map(p=>/^M  SBV/.test(p)?p.trim().split(/\s+/).slice(0,4).join(' '):p)])}
var rows=[],missing=[],failures=[];
for(var key of Object.keys(window.MOL2D))for(var mode of ['condensed','expanded','skeletal']){
 var source=window.MOL2D[key][mode];if(!source){missing.push({key,mode});continue}
 selectedMol=key;mode2D=mode;mainChainMode='algorithmic';load(source);
 var chain=mainChainAtomsList.slice(),name=currentMolName,heavyText=fStripHydrogensMol(source),heavy=heavyText&&fParseMolV2000(heavyText);
 var out=fZigzagMol(source,chain),p=out&&fParseMolV2000(out);
 var row={key,mode,chain,name,sourceAtoms:fParseMolV2000(source).atoms.length,sourceSupported:!!heavy,
 generated:!!out,before:[],after:[],lengthError:null,graphMetadataPreserved:null,deterministic:null,namePreserved:null};
 if(!p){row.reason=heavy?'generator rejected unsafe/unsupported graph':'unsupported source transformation metadata';rows.push(row);continue}
 row.graphMetadataPreserved=graph(p)===graph(heavy);
 row.deterministic=out===fZigzagMol(source,chain);
 row.after=angles(p);row.before=angles(heavy);row.localAngles=localAngles(p);row.points=p.atoms.map(a=>[a.x,a.y]);row.edges=p.bonds.map(b=>b.slice(0,2));row.groupVectorsValid=groupVectors(p);
 row.lengthError=Math.max(0,...p.bonds.map(b=>Math.abs(Math.hypot(p.atoms[b[0]-1].x-p.atoms[b[1]-1].x,p.atoms[b[0]-1].y-p.atoms[b[1]-1].y)-1.17)));
 load(out);row.generatedName=currentMolName;row.namePreserved=name===currentMolName;
 if(!row.groupVectorsValid||!row.graphMetadataPreserved||!row.deterministic||!row.namePreserved||row.lengthError>0.00015)failures.push({key,mode,kind:'invariant',row});
 row.badAngles=row.after.filter(a=>!Number.isFinite(a.angle)||a.error>0.02);
 if(row.badAngles.length)failures.push({key,mode,kind:'angle',angles:row.badAngles});
 rows.push(row);
}
return {rows,missing,failures};
'''
def run(core):
    code='var window={},console={log(){},warn(){},error(){}};var selectedMol,mode2D,mainChainMode,jsmeNomeclatureApplet;\n'
    code+=(ROOT/'js/jsme-nick-nomeclature-moc2-data_54.js').read_text()+'\n'+core+'\n'+TAIL
    outer='print(JSON.stringify((new Function('+json.dumps(code)+'))()));'
    p=subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps(outer)+'\n',text=True,capture_output=True)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return json.loads(p.stdout)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',action='store_true');parser.add_argument('--normalized',action='store_true');a=parser.parse_args()
    core=(HERE/'before-core54.js' if a.baseline else ROOT/'js/mulermoc-nom-core-54.js').read_text()
    if a.normalized:
        original=(HERE/'before-fZigzagMol.js').read_text()
        original=original.replace('        usedC++;\n        queue.push({ node: br, fx: c0, dx: bd.x, dy: bd.y, rot: 0 });','        bd = norm2(bd.x, bd.y);\n        usedC++;\n        queue.push({ node: br, fx: c0, dx: bd.x, dy: bd.y, rot: 0 });',1)
        start=core.index('function fZigzagMol(');end=core.index('\n// ── fGuessName',start)
        core=core[:start]+original+core[end:]
    result=run(core);result['runtime']='JavaScriptCore actual naming/parser/generator';result['coreSHA256']=hashlib.sha256(core.encode()).hexdigest()
    result['summary']={'forms':len(result['rows']),'molecules':len(set(r['key']for r in result['rows'])),'missing':result['missing'],
     'generated':sum(r['generated']for r in result['rows']),'skipped':[{'key':r['key'],'mode':r['mode'],'reason':r['reason']}for r in result['rows']if not r['generated']],
     'angleFailures':sum(f['kind']=='angle'for f in result['failures']),'invariantFailures':sum(f['kind']=='invariant'for f in result['failures'])}
    output=HERE/('normalized-baseline-results.json'if a.normalized else'baseline-results.json'if a.baseline else'geometry-results.json');output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['summary'],ensure_ascii=False))
    if not a.baseline and not a.normalized and result['failures']:raise SystemExit(1)
if __name__=='__main__':main()
