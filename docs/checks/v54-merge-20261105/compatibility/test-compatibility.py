"""Bounded SHA-addressed engine regression checks; no dependency installation.

Browser API doubles run in JSC; SHA fixtures are computed by Python hashlib.
Real browser Worker/quiz/lesson evidence is collected separately by Developer.
Only compatibility-report.json in this directory is written by this check.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
JSC = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc"
OLD_HASH = "3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"
CLIENT = ROOT / "js/namelecule-chemistry-client.js"
CURRENT = ROOT / "js/mulermoc-nom-core-54.js"
SNAPSHOT = ROOT / f"js/chemistry-engines/{OLD_HASH}.js"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsrun(source):
    result = subprocess.run([JSC, "-e", "eval(JSON.parse(readline()))"],
                            input=json.dumps(source) + "\n", text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(result.stdout[-6000:] + result.stderr[-2000:])
    return json.loads(result.stdout)


def compatibility_checks(baseline_only=False):
    # Compact distinguishable source fixtures keep the browser doubles focused on
    # resolution, byte binding and lifecycle. Actual shipped asset hashes are
    # checked separately below; no fixed digest is returned for arbitrary bytes.
    fixtures = {"old": b"/* fixture previous engine */\n", "current": b"/* fixture current engine */\n",
                "corrupt": b"/* fixture previous engine CORRUPTED */\n"}
    values = {key: {"bytes": list(value), "hash": hashlib.sha256(value).hexdigest()}
              for key, value in fixtures.items()}
    source = r'''
var fixtures=FIXTURES;
var OLD=fixtures.old.hash,CURRENT=fixtures.current.hash,ZERO='0'.repeat(64);
var checks=0,scenarios=[];
function ok(value,label){checks++;if(!value)throw Error(label)}
async function rejects(p,code,label){let error;try{await p}catch(e){error=e}ok(error&&error.code===code,label+': '+(error&&error.code));return error}
async function rawRejects(p,label){let error;try{await p}catch(e){error=e}ok(error,label);return error}
function tick(){return Promise.resolve().then(()=>Promise.resolve()).then(()=>Promise.resolve()).then(()=>Promise.resolve()).then(()=>Promise.resolve())}
var Signal=class{constructor(){this.aborted=false;this.listeners=[]}addEventListener(_n,f){this.listeners.push(f)}removeEventListener(_n,f){this.listeners=this.listeners.filter(x=>x!==f)}};
var AbortController=class{constructor(){this.signal=new Signal()}abort(){if(this.signal.aborted)return;this.signal.aborted=true;this.signal.listeners.slice().forEach(f=>f())}};
var URL=class{
 constructor(path,base){base=base&&base.href||base;
  if(/^https?:/.test(path))this.href=path;
  else if(path==='.')this.href=base.replace(/[?#].*$/,'').replace(/[^/]*$/,'');
  else this.href=base.replace(/[^/]*$/,'')+path;
  this.searchParams={set:(k,v)=>{this.href+='?'+k+'='+v},get:k=>{let m=new RegExp('[?&]'+k+'=([^&]*)').exec(this.href);return m?decodeURIComponent(m[1]):null}};
 }
};
var active,window,document={currentScript:{src:'https://example.test/project/js/namelecule-chemistry-client.js?v=compatibility'},baseURI:'https://example.test/project/games/name-repair.html'};
function fresh(options,source){
 options=options||{};
 const s={requests:[],digests:[],blobs:[],workers:[],urls:new Map(),revoked:[],timers:[],options};active=s;
 URL.createObjectURL=blob=>{const u='blob:https://example.test/source-'+(s.blobs.indexOf(blob))+'-'+s.urls.size;s.urls.set(u,blob);return u};
 URL.revokeObjectURL=u=>{ok(s.urls.has(u),'Revokes an active source URL');s.revoked.push(u);s.urls.delete(u)};
 var Blob=class{constructor(parts,opts){this.bytes=Object.freeze(Array.from(new Uint8Array(parts[0])));this.type=opts.type;s.blobs.push(this);Object.freeze(this)}};
 var Worker=class{
  constructor(url){this.url=url;this.terminated=0;s.workers.push(this)}
  postMessage(request){this.request=request;ok(s.urls.has(request.engineURL),'Worker gets active Blob URL');this.bytes=s.urls.get(request.engineURL).bytes.slice()}
  terminate(){this.terminated++}
  answer(change){this.onmessage({data:{type:'result',requestId:this.request.requestId,result:Object.assign({moleculeId:this.request.molecule.id,engineSHA256:this.request.engineSHA256,name:'checked'},change||{})}})}
 };
 window={URL,Blob,Worker,
  setTimeout(f){s.timers.push(f);return s.timers.length-1},clearTimeout(i){s.timers[i]=null},
  crypto:{subtle:{digest(algorithm,bytes){
   ok(algorithm==='SHA-256','Same SHA-256 algorithm required');const actual=Array.from(new Uint8Array(bytes));s.digests.push(actual);
   const key=Object.keys(fixtures).find(k=>JSON.stringify(fixtures[k].bytes)===JSON.stringify(actual));ok(key,'Hash mock rejects unknown bytes');
   if(options.digestError)return Promise.reject(Error('digest blocked'));
   const result=new Uint8Array(fixtures[key].hash.match(/../g).map(h=>parseInt(h,16))).buffer;
   if(options.pendingDigest)return new Promise(resolve=>{s.releaseDigest=()=>resolve(result)});
   return Promise.resolve(result);
  }}},
  fetch(url,request){
   s.requests.push({url,request});ok(request.cache==='reload','Resolution bypasses stale cache');
   const snapshot=url.includes('/chemistry-engines/');
   const route=snapshot?(options.snapshot||{status:200,fixture:'old'}):(options.current||{status:200,fixture:'current'});
   if(route.onFetch)route.onFetch(request);
   if(route.error)return Promise.reject(route.error);
   if(route.pending)return new Promise((_resolve,reject)=>{request.signal.addEventListener('abort',()=>{const e=Error('fetch cancelled');e.name='AbortError';reject(e)})});
   return Promise.resolve({ok:route.status>=200&&route.status<300,status:route.status,arrayBuffer(){
    if(route.bodyError)return Promise.reject(Error('body unreadable'));
    return Promise.resolve(new Uint8Array(fixtures[route.fixture||'old'].bytes).buffer);
   }});
  }
 };
 load(source||CLIENT);s.client=window.NameleculeChemistryClient;return s;
}
const molecule={id:'probe',mol:'unchanged fixture'};
async function run(){
 let s=fresh({},BEFORE);
 await rejects(s.client.verifyEngine(OLD),'ENGINE_VERSION_MISMATCH','Original client rejects previous engine once current source changes');
 ok(s.requests.length===1&&s.requests[0].url.includes('/mulermoc-nom-core-54.js?sha256='+OLD),'Original failure is current-source lookup with legacy pin');
 scenarios.push('original mismatch reproduced before intervention');
 if(BASELINE_ONLY)return {checks,scenarios,originalClientHash:ORIGINAL_HASH};
 s=fresh();ok(await s.client.verifyEngine(OLD)===OLD,'Immutable source returns measured previous hash');
 ok(s.requests.length===1&&s.requests[0].url==='https://example.test/project/js/chemistry-engines/'+OLD+'.js','SHA path resolves from client subdirectory');
 ok(await s.client.verifyEngine(OLD)===OLD&&s.requests.length===1,'Verified engine success cache suppresses later fetches');
 s.options.snapshot={status:200,fixture:'corrupt'};const first=s.client.analyze(molecule,{engineSHA256:OLD});await tick();
 ok(s.workers.length===1&&s.workers[0].url==='https://example.test/project/js/namelecule-chemistry-worker.js?v=compatibility','Worker cache version and relative path preserved');
 ok(JSON.stringify(s.workers[0].bytes)===JSON.stringify(fixtures.old.bytes),'Worker executes exact previously measured bytes after network mutation');
 s.workers[0].answer();await first;ok(s.workers[0].terminated===1&&s.revoked.length===1&&s.urls.size===0,'Success terminates Worker and revokes Blob once');
 scenarios.push('immutable lookup, success cache and immutable Worker bytes');
 s=fresh({snapshot:{status:404}});ok(await s.client.verifyEngine(CURRENT)===CURRENT,'Missing immutable source falls back to current engine');
 ok(s.requests.length===2&&s.requests[0].url.endsWith('/'+CURRENT+'.js')&&s.requests[1].url==='https://example.test/project/js/mulermoc-nom-core-54.js?sha256='+CURRENT,'Fallback URL remains version-addressed');
 ok(JSON.stringify(s.blobs[0].bytes)===JSON.stringify(fixtures.current.bytes),'Fallback snapshots actual measured source bytes');
 const current=s.client.analyze(molecule,{engineSHA256:CURRENT});await tick();s.workers[0].answer();await current;ok(s.requests.length===2,'Fallback success cache reused without fetch');
 scenarios.push('HTTP 404 current-version fallback and cache');
 s=fresh({snapshot:{status:404}});await rejects(s.client.verifyEngine(ZERO),'ENGINE_VERSION_MISMATCH','Unknown hash fails after current fallback');ok(s.blobs.length===0&&s.requests.length===2,'Unknown engine never creates Blob');
 s=fresh({snapshot:{status:200,fixture:'corrupt'},current:{status:200,fixture:'old'}});await rejects(s.client.verifyEngine(OLD),'ENGINE_VERSION_MISMATCH','Corrupted immutable asset fails closed');ok(s.requests.length===1&&s.blobs.length===0,'Corruption does not fall back or create Blob');
 s=fresh({snapshot:{status:404},current:{status:200,fixture:'corrupt'}});await rejects(s.client.verifyEngine(OLD),'ENGINE_VERSION_MISMATCH','Corrupted fallback fails same digest verification');ok(s.requests.length===2&&s.blobs.length===0,'Bad fallback cannot create Blob');
 scenarios.push('wrong hash and corruption of either source fail closed');
 for(const status of [401,403,410,500,503]){s=fresh({snapshot:{status}});await rejects(s.client.verifyEngine(OLD),'ENGINE_LOAD_FAILED','Snapshot HTTP '+status);ok(s.requests.length===1&&s.blobs.length===0,'Only 404 permits fallback')}
 for(const status of [404,403,500]){s=fresh({snapshot:{status:404},current:{status}});await rejects(s.client.verifyEngine(CURRENT),'ENGINE_LOAD_FAILED','Fallback HTTP '+status);ok(s.requests.length===2&&s.blobs.length===0,'Fallback HTTP failure creates no Blob')}
 scenarios.push('HTTP failures: 401/403/410/500/503 fail closed; fallback errors bounded');
 s=fresh({snapshot:{error:Error('offline')}});await rawRejects(s.client.verifyEngine(OLD),'Snapshot network failure rejected');ok(s.requests.length===1&&s.blobs.length===0,'Network failure cannot silently fall back');
 s=fresh({snapshot:{status:200,fixture:'old',bodyError:true}});await rawRejects(s.client.verifyEngine(OLD),'Unreadable snapshot rejected');ok(s.requests.length===1&&s.blobs.length===0,'Body read failure cannot silently fall back');
 s=fresh({digestError:true});await rawRejects(s.client.verifyEngine(OLD),'Unavailable digest rejects');ok(s.requests.length===1&&s.blobs.length===0,'Digest failure cannot fall back or create Blob');
 scenarios.push('network, body and digest errors fail closed');
 for(const hash of [null,'','../escape','A'.repeat(64),'f'.repeat(63),'f'.repeat(65),4]){s=fresh();await rejects(s.client.verifyEngine(hash),'INVALID_ENGINE_VERSION','Invalid hash rejected before URL formation');ok(s.requests.length===0,'Invalid hash never fetches')}
 s=fresh();window.crypto=null;await rejects(s.client.verifyEngine(OLD),'ENGINE_UNAVAILABLE','Missing crypto rejected');ok(s.requests.length===0,'Unavailable integrity check does not fetch');
 scenarios.push('input validation precedes lookup; unavailable integrity checks reject');
 let controller=new AbortController();controller.abort();s=fresh();await rejects(s.client.verifyEngine(OLD,{signal:controller.signal}),'ABORTED','Pre-aborted verification rejected');ok(s.requests.length===0,'Pre-aborted request never fetches');
 controller=new AbortController();s=fresh({snapshot:{status:404,onFetch(){controller.abort()}}});await rejects(s.client.verifyEngine(OLD,{signal:controller.signal}),'ABORTED','Abort before fallback rejected');ok(s.requests.length===1,'Aborted snapshot does not begin fallback');
 controller=new AbortController();s=fresh({pendingDigest:true});const verifying=s.client.verifyEngine(OLD,{signal:controller.signal});await tick();ok(s.releaseDigest,'Digest started');controller.abort();s.releaseDigest();await rejects(verifying,'ABORTED','Abort during digest rejected');ok(s.blobs.length===0,'Aborted digest cannot cache bytes');
 scenarios.push('abort before lookup, before fallback and during digest');
 for(const fallback of [false,true]){
  s=fresh(fallback?{snapshot:{status:404},current:{pending:true}}:{snapshot:{pending:true}});
  const stalled=s.client.analyze(molecule,{engineSHA256:OLD});await tick();ok(s.requests.length===(fallback?2:1),'Stalled source reached');s.timers.filter(Boolean).forEach(f=>f());
  await rejects(stalled,'ENGINE_TIMEOUT','Timeout covers '+(fallback?'fallback':'snapshot')+' fetch');ok(s.requests.every(r=>r.request.signal.aborted)&&s.workers.length===0&&s.blobs.length===0,'Timed out resolution aborts network and creates no Worker');
 }
 controller=new AbortController();s=fresh({snapshot:{status:404},current:{pending:true}});const cancelled=s.client.analyze(molecule,{engineSHA256:OLD,signal:controller.signal});await tick();controller.abort();await rejects(cancelled,'ABORTED','Abort during fallback rejected');ok(controller.signal.listeners.length===0&&s.workers.length===0&&s.requests[1].request.signal.aborted,'Abort releases listener and cancels fallback');
 scenarios.push('analysis timeout covers both sources; cancellation preserves cleanup');
 return {checks,scenarios,limitations:'Controlled browser API doubles; crypto fixture hashes computed with Python hashlib. Browser Worker, legacy receipts and lesson restore verified separately.'};
}
run().then(result=>print(JSON.stringify(result))).catch(e=>{print(String(e.stack||e));quit(1)});
'''
    source = source.replace("FIXTURES", json.dumps(values)).replace("BEFORE", json.dumps(str(HERE / "before-client.js"))).replace("CLIENT", json.dumps(str(CLIENT)))
    source = source.replace("BASELINE_ONLY", json.dumps(baseline_only)).replace("ORIGINAL_HASH", json.dumps(sha(HERE / "before-client.js")))
    return jsrun(source)


if __name__ == "__main__":
    if "--baseline-only" in sys.argv:
        report = compatibility_checks(baseline_only=True)
        (HERE / "baseline-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(0)
    report = {"compatibility": compatibility_checks(),
              "existingClientLifecycle": jsrun((HERE / "client-lifecycle-tests.js").read_text().replace("CLIENT", json.dumps(str(CLIENT))).replace("HASH", json.dumps(OLD_HASH))),
              "sourceSHA256": {str(p.relative_to(ROOT)): sha(p) for p in [CLIENT, CURRENT, SNAPSHOT, HERE / "before-client.js"]},
              "snapshotMatchesRequiredHash": sha(SNAPSHOT) == OLD_HASH}
    assert report["snapshotMatchesRequiredHash"], report
    (HERE / "compatibility-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
