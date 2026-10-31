from pathlib import Path
import os,json,traceback
r=Path('/tmp/namelecule-svg-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8031/'
exec(compile((r/'bidi.py').read_text(),'bidi','exec'))
out={'completed':False}
measure='JSON.stringify({epoch:NameleculeLabelMetrics.state.epoch,box:NameleculeLabelMetrics.synthetic({a:"NameleculeDelayedFixture, Helvetica",b:9,c:0},{n:"COOH",j:null,k:null})})'
try:
 navigate('main/mulermoc-nom-52.html?audit=real-fontface');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)')
 out['before']=json.loads(ev(measure))
 ev(r'''(async()=>{
   window.__face=new FontFace('NameleculeDelayedFixture','local("Times New Roman")');
   window.__span=document.createElement('span');__span.textContent='HCO';
   __span.style.cssText='position:fixed;left:-100000px;top:0;font-family:NameleculeDelayedFixture,Helvetica';
   document.body.appendChild(__span);document.fonts.add(__face);__span.getBoundingClientRect();
   await __face.load();await document.fonts.ready;return true;
 })()''')
 until('NameleculeLabelMetrics.state.epoch>'+str(out['before']['epoch']),seconds=8)
 out['after']=json.loads(ev(measure));out['fontFaceStatus']=ev('__face.status')
 assert out['fontFaceStatus']=='loaded'and out['before']['box']!=out['after']['box']
 ev('__span.remove();document.fonts.delete(__face);true');out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(r/'late-font.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));call('browsingContext.close',{'context':ctx});call('session.end',{});print('actual late FontFace',out['completed'],'errors',len(js_errors),flush=True)
