from pathlib import Path
import json,subprocess,hashlib,datetime
E=Path(__file__).resolve().parent
C=Path('/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate/js/mulermoc-nom-iupac-55.js')
J='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
harness=r'''
var clock=100000, timers=[], starts=[], done=false, result=null, AbortController=undefined;
Date.now=function(){return clock;};
function setTimeout(cb,ms){timers.push({at:clock+ms,cb:cb});return timers.length;}
function clearTimeout(){}
function fetch(url){var index=starts.length;starts.push({at:clock,url:url});
 if (CASE==='failures' && index===1) return Promise.reject(new Error('fixture network'));
 var response={ok:!(CASE==='failures' && index===2),status:429,json:function(){return Promise.resolve(CASE==='failures' && index===3?{ok:false,error:'fixture noanswer'}:{ok:true,name:'methane'});}};
 if(CASE==='slow')return new Promise(function(r){setTimeout(function(){r(response);},500);});
 return Promise.resolve(response);
}
(async function(){
 var empty=false;try{await fFetchIUPAC_OC(' ');}catch(e){empty=true;}
 var first=await Promise.all(Array.from({length:12},function(){return fFetchIUPAC_OC('C').then(function(v){return {ok:true,name:v.name};},function(e){return {ok:false,error:String(e)};});}));
 var retry=await fFetchIUPAC_OC('C');
 result={starts:starts,first:first,retry:retry,emptyRejected:empty,finishedAt:clock};done=true;
})();
(async function(){for(var i=0;i<2000 && !done;i++){
 for(var m=0;m<40;m++)await Promise.resolve();
 if(!done && timers.length){timers.sort(function(a,b){return a.at-b.at;});var t=timers.shift();clock=t.at;t.cb();}
} print(JSON.stringify({done:done,result:result}));})();
'''
def run(src,case):
 code=src[:src.index('\nasync function fFetchIUPAC_EN(smiles, opts)')]+"\nvar CASE="+json.dumps(case)+";\n"+harness
 p=subprocess.run([J,'-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',capture_output=True,text=True)
 assert p.returncode==0,(p.stdout,p.stderr)
 r=json.loads(p.stdout.strip());assert r['done'],r
 r=r['result'];r['minimumStartGap']=min(b['at']-a['at']for a,b in zip(r['starts'],r['starts'][1:]));return r
before=run((E/'before.js').read_text(),'burst');assert before['minimumStartGap']==0,before
cases={k:run(C.read_text(),k)for k in ('burst','failures','slow')}
for case,r in cases.items():
 assert len(r['starts'])==13 and r['emptyRejected'] and r['minimumStartGap']>=150,(case,r)
 assert r['retry']['name']=='methane'
 assert sum(not x['ok']for x in r['first'])==(3 if case=='failures'else 0)
assert cases['slow']['starts'][1]['at']<cases['slow']['starts'][0]['at']+500
out={'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'Developer actual-function JavaScriptCore tests; virtual clock, controlled transport, no live service/browser','beforeSHA256':hashlib.sha256((E/'before.js').read_bytes()).hexdigest(),'afterSHA256':hashlib.sha256(C.read_bytes()).hexdigest(),'beforeBurst':before,'cases':cases,'passed':True,'assertions':15}
(E/'results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':True,'beforeMinimumGap':0,'afterMinimumGaps':{k:v['minimumStartGap']for k,v in cases.items()},'assertions':15}))
