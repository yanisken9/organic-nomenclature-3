"""Headless adapter regression checks; real unchanged core54 in fresh JSC scopes.

The client lifecycle checks use controlled browser doubles and are not browser
Worker evidence. Run from any directory; no dependency installation is required.
Only adapter-report.json in this owned evidence directory is written.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import random
import subprocess
import sys

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
JSC = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc"
CORE = ROOT / "js/mulermoc-nom-core-54.js"
WORKER = ROOT / "js/namelecule-chemistry-worker.js"
CLIENT = ROOT / "js/namelecule-chemistry-client.js"
DATA = ROOT / "js/jsme-nick-nomeclature-moc2-data_54.js"
CATALOG = json.loads((ROOT / "games/data/alkane-structures.json").read_text())


def jsrun(source):
    result = subprocess.run([JSC, "-e", "eval(JSON.parse(readline()))"],
                            input=json.dumps(source) + "\n", text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(result.stdout[-5000:] + result.stderr[-2000:])
    return json.loads(result.stdout)


def analyze(mol, molecule_id="independent-probe", engine_url="blob:https://example.test/verified-source"):
    request = {"type": "analyze", "requestId": "owned-check",
               "engineSHA256": CATALOG["engineSHA256"],
               "engineURL": engine_url,
               "molecule": {"id": molecule_id, "mol": mol}}
    # load() evaluates as a global script, as importScripts does in a Worker.
    # Data54 is deliberately absent from this isolated naming scope.
    return jsrun("""
var outputs=[],diagnostics=[],closed=0,imports=[];
var console={log(){diagnostics.push('log')},warn(){diagnostics.push('warn')},error(){diagnostics.push('error')}};
var self={location:{href:'https://example.test/project/js/namelecule-chemistry-worker.js',origin:'https://example.test'},
 postMessage(value){outputs.push(value)},close(){closed++}};
var URL=function(path){this.href=path;this.protocol=path.split(':')[0]+':';
 this.origin=path.replace(/^blob:/,'').split('/').slice(0,3).join('/')};
function importScripts(url){imports.push(url);load(CORE)}
load(WORKER);
self.onmessage({data:REQUEST});
self.onmessage({data:REQUEST});
print(JSON.stringify({outputs,closed,imports,diagnostics,
 noDOM:typeof document==='undefined'&&typeof window==='undefined'&&typeof Jmol==='undefined'}));
""".replace("CORE", json.dumps(str(CORE))).replace("WORKER", json.dumps(str(WORKER)))
                 .replace("REQUEST", json.dumps(request)))


def mol(types, edges):
    lines = ["Independent test graph", "  Namelecule test", "",
             f"{len(types):3}{len(edges):3}  0  0  0  0  0  0  0  0  0  0999 V2000"]
    lines += [f"{float(i):10.4f}{0.:10.4f}{0.:10.4f} {el:<3} 0  0  0  0  0  0  0  0  0  0  0  0"
              for i, el in enumerate(types)]
    lines += [f"{a:3}{b:3}{order:3}  0  0  0  0" for a, b, order in edges]
    return "\n".join(lines + ["M  END", ""])


def edit_field(text, line, start, end, replacement):
    lines = text.splitlines()
    lines[line] = lines[line][:start] + replacement + lines[line][end:]
    return "\n".join(lines) + "\n"


def worker_checks():
    expected = {
        "methane": ("μεθάνιο", 1, 1, []),
        "ethane": ("αιθάνιο", 2, 2, []),
        "propane": ("προπάνιο", 3, 3, []),
        "butane": ("βουτάνιο", 4, 4, []),
        "pentane": ("πεντάνιο", 5, 5, []),
        "methyl_2_pentane": ("2-μεθυλοπεντάνιο", 6, 5, [(2, 1)]),
        "dimethyl_2_3_butane": ("2,3-διμεθυλοβουτάνιο", 6, 4, [(2, 1), (3, 1)]),
        "ethyl_3_dimethyl_2_5_hexane": ("3-αιθυλο-2,5-διμεθυλοεξάνιο", 10, 6,
                                        [(2, 1), (3, 2), (5, 1)]),
    }
    rows = []
    for entry in CATALOG["molecules"]:
        output = analyze(entry["mol"], entry["id"])
        assert len(output["outputs"]) == 1 and output["closed"] == 1, output
        assert output["noDOM"] and not output["diagnostics"], output
        assert output["imports"] == ["blob:https://example.test/verified-source"]
        message = output["outputs"][0]
        assert message["type"] == "result", message
        result = message["result"]
        name, carbon_count, parent, branches = expected[entry["id"]]
        assert result["name"] == name and result["carbonCount"] == carbon_count, result
        assert result["classification"]["seriesKey"] == "alkanes", result
        assert len(result["chain"]) == parent and len(set(result["chain"])) == parent, result
        assert [(b["locant"], b["length"]) for b in result["branches"]] == branches, result
        assert all(b["attach"] in b["atoms"] and len(b["atoms"]) == b["length"] for b in result["branches"]), result
        assert len(result["parts"]) == 12 and "".join(p or "" for p in result["parts"]) == name, result
        assert len(result["rootVocabulary"]) == 20 and result["rootVocabulary"][:6] == ["μεθ", "αιθ", "προπ", "βουτ", "πεντ", "εξ"], result
        rows.append(result)

    # Compare every available source representation without loading its authored
    # chain/name data into the naming Worker. Methane has no skeletal source.
    representations = jsrun("var window={};load(" + json.dumps(str(DATA)) + ");print(JSON.stringify(" +
                            json.dumps(list(expected)) + ".flatMap(id=>Object.keys(window.MOL2D[id])" +
                            ".filter(mode=>window.MOL2D[id][mode]).map(mode=>({id,mode,mol:window.MOL2D[id][mode]})))));")
    for form in representations:
        output = analyze(form["mol"], form["id"])
        assert output["outputs"][0]["type"] == "result", (form["id"], form["mode"], output)
        answer = output["outputs"][0]["result"]
        assert answer["name"] == expected[form["id"]][0], answer

    # Independent carbon trees, permuted atom and bond numbering: no nameExamples.
    probes = [(["C"] * 5, [(1, 2, 1), (1, 3, 1), (1, 4, 1), (1, 5, 1)],
               "2,2-διμεθυλοπροπάνιο"),
              (["C"] * 6, [(1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 5, 1), (2, 6, 1)],
               "2-μεθυλοπεντάνιο")]
    randomizer = random.Random(20261105)
    for types, edges, name in probes:
        for _ in range(4):
            order = list(range(len(types)))
            randomizer.shuffle(order)
            mapping = {old + 1: new + 1 for new, old in enumerate(order)}
            mapped = [(mapping[a], mapping[b], o) for a, b, o in edges]
            randomizer.shuffle(mapped)
            output = analyze(mol([types[i] for i in order], mapped))
            assert output["outputs"][0]["type"] == "result", output
            assert output["outputs"][0]["result"]["name"] == name, output

    valid = mol(["C", "C"], [(1, 2, 1)])
    invalid = {
        "malformed": "not MOL",
        "oxygen": mol(["C", "O"], [(1, 2, 1)]),
        "double bond": mol(["C", "C"], [(1, 2, 2)]),
        "cycle": mol(["C"] * 3, [(1, 2, 1), (2, 3, 1), (3, 1, 1)]),
        "disconnected": mol(["C"] * 2, []),
        "duplicate": mol(["C"] * 2, [(1, 2, 1), (1, 2, 1)]),
        "carbon valence five": mol(["C"] * 6, [(1, i, 1) for i in range(2, 7)]),
        "hydrogen valence two": mol(["C", "H", "C"], [(1, 2, 1), (2, 3, 1)]),
        "hydrogen-hydrogen": mol(["C", "H", "H"], [(1, 2, 1), (2, 3, 1)]),
        "isotope": edit_field(valid, 4, 34, 36, " 1"),
        "charge": edit_field(valid, 4, 36, 39, "  3"),
        "stereo parity": edit_field(valid, 4, 39, 42, "  1"),
        "hydrogen count": edit_field(valid, 4, 42, 45, "  1"),
        "valence metadata": edit_field(valid, 4, 48, 51, "  4"),
        "atom mapping": edit_field(valid, 4, 60, 63, "  1"),
        "bond stereo": edit_field(valid, 6, 9, 12, "  1"),
        "query property": valid.replace("M  END", "M  ALS   1  1 F C\nM  END"),
        "radical property": valid.replace("M  END", "M  RAD  1   1   2\nM  END"),
        "isotope property": valid.replace("M  END", "M  ISO  1   1  13\nM  END"),
        "SDF data": valid + "> <NAME>\nunhandled\n\n$$$$\n",
        "second record": valid + "$$$$\n" + valid,
        "V3000": valid.replace("V2000", "V3000"),
    }
    for label, text in invalid.items():
        output = analyze(text)
        assert output["outputs"][0]["type"] == "error", (label, output)
        assert output["closed"] == 1 and len(output["outputs"]) == 1, (label, output)
    rejected_urls = ["https://example.test/js/core54.js", "blob:https://other.test/source", "data:text/javascript,code"]
    for url in rejected_urls:
        output = analyze(valid, engine_url=url)
        assert output["outputs"][0]["type"] == "error" and output["outputs"][0]["error"]["code"] == "INVALID_REQUEST", output
        assert not output["imports"], output
    return {"catalogResults": rows, "allAvailableForms": len(representations),
            "missingForms": ["methane:skeletal"], "independentPermutedGraphs": 8,
            "rejectedInputs": list(invalid), "rejectedSourceURLs": rejected_urls}


def catalog_checks():
    spec = importlib.util.spec_from_file_location("catalog_builder", ROOT / "tools/build-alkane-game-catalog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = (ROOT / "games/data/alkane-structures.json").read_text()
    assert module.build_catalog() == original
    assert module.build_catalog() == original
    assert CATALOG["engineSHA256"] == hashlib.sha256(CORE.read_bytes()).hexdigest()
    assert CATALOG["source"]["sha256"] == hashlib.sha256(DATA.read_bytes()).hexdigest()
    for entry in CATALOG["molecules"]:
        assert set(entry) == {"id", "mol", "asset", "diagramAlt", "sourceSHA256"}
        assert entry["sourceSHA256"] == hashlib.sha256(entry["mol"].encode()).hexdigest()
    return {"reproducible": True, "structureOnly": True, "revision": CATALOG["revision"]}


def client_checks():
    # Browser API doubles expose cancellation, stale replies and termination.
    # Actual network/Worker/subdirectory execution is the separate browser test.
    source = r'''
let checks=0,fetches=0,created=[],timers=[],fetchFailure=null,fetchPending=false;
let networkBytes=[13,37,42],digested=[],blobs=new Map(),revoked=[],nextBlob=0,allBlobURLs=[];
function ok(value,label){checks++;if(!value)throw Error(label)}
function tick(){return Promise.resolve().then(()=>Promise.resolve()).then(()=>Promise.resolve())}
var URL = class URL {
 constructor(path,base){
  base=base&&base.href||base;
  if(/^https?:/.test(path))this.href=path;
  else if(path==='.')this.href=base.replace(/[?#].*$/,'').replace(/[^/]*$/,'');
  else this.href=base.replace(/[^/]*$/,'')+path;
  this.searchParams={set:(k,v)=>{this.href+='?'+k+'='+v},get:k=>{const m=new RegExp('[?&]'+k+'=([^&]*)').exec(this.href);return m?decodeURIComponent(m[1]):null}};
 }
};
URL.createObjectURL=blob=>{const url='blob:https://example.test/source-'+(++nextBlob);blobs.set(url,blob);allBlobURLs.push(url);return url};
URL.revokeObjectURL=url=>{ok(blobs.has(url),'Every revoked source URL is active');revoked.push(url);blobs.delete(url)};
var Blob=class Blob {constructor(parts,options){this.bytes=Object.freeze(Array.from(new Uint8Array(parts[0])));this.type=options.type;Object.freeze(this)}};
var Signal = class Signal {
 constructor(){this.aborted=false;this.listeners=[]}
 addEventListener(_name,fn){this.listeners.push(fn)}
 removeEventListener(_name,fn){this.listeners=this.listeners.filter(f=>f!==fn)}
};
var AbortController = class AbortController {
 constructor(){this.signal=new Signal()}
 abort(){if(this.signal.aborted)return;this.signal.aborted=true;this.signal.listeners.slice().forEach(f=>f())}
};
var FakeWorker = class FakeWorker {
 constructor(url){this.url=url;this.terminations=0;created.push(this)}
 postMessage(request){this.request=request;ok(blobs.has(request.engineURL),'Worker receives an active verified-source Blob URL');this.importedBytes=blobs.get(request.engineURL).bytes.slice()}
 terminate(){this.terminations++}
 answer(change){const result={moleculeId:this.request.molecule.id,engineSHA256:HASH,name:'measured'};
  if(change)Object.assign(result,change);
  this.onmessage({data:{type:'result',requestId:this.request.requestId,result}})}
};
var document={currentScript:{src:'https://example.test/project/js/namelecule-chemistry-client.js?v=engine-pilot-20261105-r2'},baseURI:'https://example.test/project/games/name-repair.html'};
var window={Worker:FakeWorker,URL,Blob,crypto:{subtle:{digest:(_algorithm,bytes)=>{digested.push(Array.from(new Uint8Array(bytes)));return Promise.resolve(new Uint8Array(HASH.match(/../g).map(h=>parseInt(h,16))).buffer)}}},
 setTimeout(fn){timers.push(fn);return timers.length-1},clearTimeout(id){timers[id]=null},
 fetch(url,options){fetches++;ok(url==='https://example.test/project/js/mulermoc-nom-core-54.js?sha256='+HASH,'Measured URL follows script subdirectory');
  ok(options.cache==='reload','Version verification bypasses stale cache');
  if(fetchFailure)return Promise.reject(fetchFailure);
  if(fetchPending)return new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>reject(Error('aborted fetch'))));
  return Promise.resolve({ok:true,arrayBuffer:()=>Promise.resolve(new Uint8Array(networkBytes).buffer)})}};
load(CLIENT);
const client=window.NameleculeChemistryClient, molecule={id:'probe',mol:'test'};
async function rejectCode(p,code,label){let error;try{await p}catch(e){error=e}ok(error&&error.code===code,label+': '+(error&&error.code))}
async function run(){
 ok(await client.verifyEngine(HASH)===HASH,'Returns actually measured hash');
 ok(await client.verifyEngine(HASH)===HASH&&fetches===1,'Successful measured version cached once');
 ok(JSON.stringify(digested[0])===JSON.stringify(networkBytes),'Digest receives exact fetched source bytes');
 networkBytes=[99,88,77];
 const a=client.analyze(molecule,{engineSHA256:HASH});await tick();
 const first=created[0];ok(first.url==='https://example.test/project/js/namelecule-chemistry-worker.js?v=engine-pilot-20261105-r2','Worker follows script subdirectory and adapter cache version');
 ok(JSON.stringify(first.importedBytes)===JSON.stringify(digested[0])&&JSON.stringify(first.importedBytes)!==JSON.stringify(networkBytes),'Changed network source cannot replace the actually verified engine bytes');
 first.onmessage({data:{type:'result',requestId:'stale',result:{}}});ok(first.terminations===0,'Stale request ID cannot settle current promise');
 first.answer();ok((await a).name==='measured'&&first.terminations===1,'Success terminates one-shot Worker');
 ok(first.onmessage===null&&first.onerror===null,'Success releases event handlers');
 const b=client.analyze(molecule,{engineSHA256:HASH});await tick();
 const second=created[1];second.answer({moleculeId:'wrong'});await rejectCode(b,'INVALID_ENGINE_RESULT','Wrong molecule rejected');ok(second.terminations===1,'Invalid result terminates Worker');
 const c=client.analyze(molecule,{engineSHA256:HASH});await tick();
 const third=created[2];third.onmessage({data:{type:'error',requestId:third.request.requestId,error:{code:'UNSUPPORTED_MOLECULE',message:'bounded'}}});
 await rejectCode(c,'UNSUPPORTED_MOLECULE','Worker rejection propagated');ok(third.terminations===1,'Worker error terminates');
 const ctrl=new AbortController(), d=client.analyze(molecule,{engineSHA256:HASH,signal:ctrl.signal});await tick();
 const fourth=created[3],oldHandler=fourth.onmessage;ctrl.abort();
 await rejectCode(d,'ABORTED','Abort rejects');ok(fourth.terminations===1&&ctrl.signal.listeners.length===0,'Abort terminates and releases signal listener');
 oldHandler({data:{type:'result',requestId:fourth.request.requestId,result:{}}});ok(fourth.terminations===1,'Stale reply after cancellation stays inert');
 const already=new AbortController();already.abort();await rejectCode(client.analyze(molecule,{engineSHA256:HASH,signal:already.signal}),'ABORTED','Already aborted request');
 ok(created.length===4,'Already aborted request creates no Worker');
 const e=client.analyze(molecule,{engineSHA256:HASH});await tick();const fifth=created[4];timers.filter(Boolean).forEach(f=>f());
 await rejectCode(e,'ENGINE_TIMEOUT','Timeout bounded');ok(fifth.terminations===1,'Timeout terminates Worker');
 const f=client.analyze(molecule,{engineSHA256:HASH});await tick();const sixth=created[5];sixth.onerror({preventDefault(){}});
 await rejectCode(f,'ENGINE_FAILED','Worker startup/runtime error bounded');ok(sixth.terminations===1,'Runtime error terminates Worker');
 const g=client.analyze(molecule,{engineSHA256:HASH});await tick();const seventh=created[6];seventh.onmessageerror();
 await rejectCode(g,'INVALID_ENGINE_RESULT','Unreadable message bounded');ok(seventh.terminations===1,'Message error terminates Worker');
 await rejectCode(client.analyze(molecule,{engineSHA256:'declared'}),'INVALID_ENGINE_VERSION','No unmeasured declaration accepted');
 await rejectCode(client.analyze(null,{engineSHA256:HASH}),'INVALID_MOLECULE','Missing structure rejected');
 await rejectCode(client.analyze(molecule,{engineSHA256:HASH,timeoutMs:0}),'INVALID_TIMEOUT','Invalid timeout rejected');
 const oldWorker=window.Worker;window.Worker=undefined;await rejectCode(client.analyze(molecule,{engineSHA256:HASH}),'ENGINE_UNAVAILABLE','Unsupported Worker bounded');window.Worker=oldWorker;
 const changing={id:'original',mol:'original MOL'},snap=client.analyze(changing,{engineSHA256:HASH});
 changing.id='mutated';changing.mol='mutated MOL';await tick();
 const snapshot=created[7];ok(snapshot.request.molecule.id==='original'&&snapshot.request.molecule.mol==='original MOL','Caller mutation cannot retarget an asynchronous request');
 snapshot.answer();ok((await snap).moleculeId==='original'&&snapshot.terminations===1,'Snapshot validates the original reply');
 ok(created.every(w=>JSON.stringify(w.importedBytes)===JSON.stringify(digested[0]))&&fetches===1,'Every analysis imports the same measured bytes with no second network request');
 window.Worker=function(){throw Error('Worker constructor blocked')};let constructorFailed=false;
 try{await client.analyze(molecule,{engineSHA256:HASH})}catch(e){constructorFailed=true}ok(constructorFailed,'Worker constructor failure is bounded');window.Worker=oldWorker;
 window.Worker=class extends FakeWorker {postMessage(){throw Error('postMessage failed')}};let postFailed=false;
 try{await client.analyze(molecule,{engineSHA256:HASH})}catch(e){postFailed=true}ok(postFailed&&created[8].terminations===1,'Failed message dispatch terminates its Worker');window.Worker=oldWorker;
 ok(blobs.size===0&&revoked.length===allBlobURLs.length&&new Set(revoked).size===revoked.length,'Success, rejection, abort, timeout, runtime/message/constructor/dispatch failures revoke every Blob URL once');
 // Reload the client to clear its successful version cache.
 load(CLIENT);const fresh=window.NameleculeChemistryClient;
 window.crypto.subtle.digest=()=>Promise.resolve(new Uint8Array(32).buffer);
 await rejectCode(fresh.verifyEngine(HASH),'ENGINE_VERSION_MISMATCH','Actual byte hash mismatch rejected');
 fetchFailure=Error('offline');let failed=false;try{await fresh.verifyEngine(HASH)}catch(e){failed=true}ok(failed,'Offline fetch rejected');fetchFailure=null;
 fetchPending=true;const stalled=fresh.analyze(molecule,{engineSHA256:HASH});await tick();timers.filter(Boolean).forEach(f=>f());
 await rejectCode(stalled,'ENGINE_TIMEOUT','Timeout also covers engine fetch');
 return {checks,workerRequests:created.length,allCreatedWorkersTerminated:created.every(w=>w.terminations===1),exactVerifiedBytesBoundToImports:true,blobURLsCreated:allBlobURLs.length,blobURLsRevoked:revoked.length,adapterVersionPropagated:true,limitations:'Controlled API doubles; real browser/network tests are separate'};
}
run().then(x=>print(JSON.stringify(x))).catch(e=>{print(String(e.stack||e));quit(1)});
'''.replace("CLIENT", json.dumps(str(CLIENT))).replace("HASH", json.dumps(CATALOG["engineSHA256"]))
    return jsrun(source)


if __name__ == "__main__":
    report = {"catalog": catalog_checks(), "worker": worker_checks(), "client": client_checks(),
              "sourceSHA256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [CORE, WORKER, CLIENT, DATA, ROOT / "games/data/alkane-structures.json",
                                         ROOT / "tools/build-alkane-game-catalog.py"]}}
    (HERE / "adapter-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"catalog": report["catalog"], "forms": report["worker"]["allAvailableForms"],
                      "rejected": len(report["worker"]["rejectedInputs"]), "client": report["client"]}, ensure_ascii=False))
