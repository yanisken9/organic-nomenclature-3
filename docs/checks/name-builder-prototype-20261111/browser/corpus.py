"""Actual native55 host: every catalog molecule/form, including real3D graphs."""
from pathlib import Path
import hashlib
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'completed':False,'rounds':[],'forms':[],'failures':[],'role':'Developer actual-browser evidence'}
def save():
 out['javascriptErrors']=js_errors
 (HERE/('corpus-2d.json' if os.environ.get('NAME_BUILDER_SKIP_3D') else 'corpus.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
def command(command,molecule,round_id,representation):
 payload={'command':command,'moleculeId':molecule,'roundId':round_id,'representation':representation}
 expr='''(async()=>{
 const frame=document.querySelector('iframe'), spec=PAYLOAD;
 const session=__builderEvents.find(x=>x.type==='ready').session;
 const requestId=++window.__corpusRequestId;
 return await new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>{removeEventListener('message',receive);reject(Error('Corpus bridge timeout'));},25000);
  function receive(e){let d=e.data;if(e.source!==frame.contentWindow||e.origin!==location.origin||d?.channel!=='namelecule-name-builder-v1'||d.session!==session||d.requestId!==requestId||d.type==='busy')return;
   clearTimeout(timer);removeEventListener('message',receive);resolve(JSON.stringify(d));}
  addEventListener('message',receive);
  frame.contentWindow.postMessage({channel:'namelecule-name-builder-v1',session,requestId,...spec},location.origin);
 });
})()'''.replace('PAYLOAD',json.dumps(payload))
 result=json.loads(ev(expr))
 assert result.get('type')==('round' if command=='load' else 'representation'),result
 assert result['moleculeId']==molecule and result['representation']==representation,result
 return result
try:
 out['sourceHashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['js/namelecule-name-builder-host.js','games/name-builder-viewer.html','js/namelecule-name-builder-engine.js','js/mulermoc-nom-core-55.js','js/jsme-nick-nomeclature-moc2-data_55.js']}
 open_page('games/name-builder.html');wait('document.querySelectorAll("#bank-tiles button").length>0')
 inventory=read('__builderEvents.find(x=>x.type==="ready").inventory')
 assert len(inventory)==141,len(inventory)
 ev('window.__corpusRequestId=10000;true')
 for index,entry in enumerate(inventory):
  round_id='corpus-'+entry['id']
  try:
   raw=command('load',entry['id'],round_id,'condensed')
   out['rounds'].append(raw)
   for representation in entry['representations']:
    if representation=='3d' and os.environ.get('NAME_BUILDER_SKIP_3D'):continue
    actual=raw if representation=='condensed' else command('representation',entry['id'],round_id,representation)
    assert actual['correctName']==raw['correctName'],(entry['id'],representation)
    diagnostic=read('(()=>{let f=document.querySelector("iframe"),w=f.contentWindow,d=f.contentDocument,svg=d.querySelector("#jsmeNomeclatureSVG svg");let r=svg?.getBoundingClientRect();return{host:w.NameleculeNameBuilderHost.snapshot(),modelReady:w.NameleculeNameBuilderHost.modelReady(),viewport:{width:w.innerWidth,height:w.innerHeight},svg:r?{width:r.width,height:r.height}:null,visibleText:d.body.innerText,canvas:[...d.querySelectorAll("canvas")].map(c=>({width:c.width,height:c.height,rect:c.getBoundingClientRect().toJSON()}))}})()')
    if representation=='3d': assert diagnostic['modelReady'],(entry['id'],'3D graph notready')
    else:
     assert diagnostic['svg'] and abs(diagnostic['svg']['height']-diagnostic['viewport']['height'])<=2,(entry['id'],diagnostic)
    assert raw['correctName'] not in diagnostic['visibleText'],(entry['id'],'answer visible')
    out['forms'].append({'moleculeId':entry['id'],'representation':representation,'nameMatches':True,'modelReady':diagnostic['modelReady'] if representation=='3d' else None,'svg':diagnostic['svg'],'viewport':diagnostic['viewport']})
  except Exception:
   out['failures'].append({'moleculeId':entry['id'],'trace':traceback.format_exc(),'lastEvents':read('__builderEvents.slice(-3)')})
   save();raise
  if index%10==0:
   save();print(json.dumps({'molecules':index+1,'forms':len(out['forms']),'last':entry['id']},ensure_ascii=False),flush=True)
 out['summary']={'molecules':len(out['rounds']),'forms2D':sum(f['representation']!='3d' for f in out['forms']),'models3D':sum(f['representation']=='3d' for f in out['forms']),'series':sorted({r['series'] for r in out['rounds']})}
 assert out['summary']['forms2D']==422 and out['summary']['models3D']==(0 if os.environ.get('NAME_BUILDER_SKIP_3D') else 141),out['summary']
 out['completed']=True;print(json.dumps(out['summary'],ensure_ascii=False),flush=True)
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('corpus-failure.png')
 except Exception:pass
finally:
 save();finish()
if not out['completed']:raise SystemExit(1)
