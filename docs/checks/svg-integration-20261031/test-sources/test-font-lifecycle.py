from pathlib import Path
import os,json,time,gzip,traceback
r=Path('/tmp/namelecule-svg-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8031/'
exec(compile((r/'bidi.py').read_text(),'bidi','exec'))
out={'completed':False}
try:
 navigate('main/mulermoc-nom-52.html?audit=font-lifecycle');app_ready();until('window.JSmolReadyFlag===true')
 ev('document.getElementById("ethyl_3_dimethyl_2_5_hexane").click();true');until("(()=>{try{return Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href}catch(e){return false}})()");time.sleep(.3)
 ev('fClearHighlights();fShowNameAnalysis();document.getElementById("comp5").click();true');until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===1',seconds=3)
 out['before']=json.loads(ev('JSON.stringify({count:document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length,index:currNumberEl,timer:myNumberingTimeout})'))
 ev('window.__jmolScripts=[];window.__jmolScript=Jmol.script;Jmol.script=function(a,s,...rest){__jmolScripts.push(s);return __jmolScript.call(this,a,s,...rest)};document.fonts.dispatchEvent(new Event("loadingdone"));new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
 out['afterFont']=json.loads(ev('JSON.stringify({count:document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length,index:currNumberEl,timer:myNumberingTimeout,scripts:__jmolScripts.slice()})'))
 assert out['afterFont']['count']==out['before']['count'] and out['afterFont']['index']==out['before']['index'] and out['afterFont']['timer']==out['before']['timer'] and not out['afterFont']['scripts'],out
 until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===6',seconds=5)
 # Native applet teardown with a still-live 2D page reproduces the risky ordering.
 ev('Jmol._destroy(jmolAppletNomeclature);__jmolScripts.length=0;document.fonts.dispatchEvent(new Event("loadingdone"));new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
 out['after3DDestroy']=json.loads(ev('JSON.stringify({svg:!!document.querySelector("#jsmeNomeclatureSVG svg"),numbers:[...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].map(n=>n.textContent),scripts:__jmolScripts.slice()})'));assert out['after3DDestroy']['svg']and len(out['after3DDestroy']['numbers'])==6 and not out['after3DDestroy']['scripts']
 # Own pending RAF cancelled on pagehide, resumes on pageshow; not a fullBFCache test.
 ev('window.__refreshCount=0;window.__refresh2D=fRefreshFontDrawing2D;fRefreshFontDrawing2D=function(){__refreshCount++;return __refresh2D()};document.fonts.dispatchEvent(new Event("loadingdone"));dispatchEvent(new PageTransitionEvent("pagehide",{persisted:true}));new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)');assert ev('__refreshCount')==0
 ev('dispatchEvent(new PageTransitionEvent("pageshow",{persisted:true}));document.fonts.dispatchEvent(new Event("loadingdone"));new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)');assert ev('__refreshCount')==1
 out['pageEvents']='synthetic controller events only; pending callback cancelled/resumed; no full BFCache claim';out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(r/'font-lifecycle.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('font lifecycle',out['completed'],'errors',len(js_errors),flush=True)
