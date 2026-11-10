from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
def action(sel,label,first,last=None):
 p=prepare(sel);pause(300);ev('(()=>{window.__reducedTrace=[];let start=performance.now();function tick(){__reducedTrace.push({ms:performance.now()-start,y:scrollY});if(performance.now()-start<800)requestAnimationFrame(tick)}requestAnimationFrame(tick);return true})()');pointer(p);pause(950);g=read('(()=>{let a=document.querySelector('+json.dumps(first)+').getBoundingClientRect(),b=document.querySelector('+json.dumps(last or first)+').getBoundingClientRect();return{top:Math.min(a.top,b.top),bottom:Math.max(a.bottom,b.bottom),height:innerHeight}})()');trace=read('__reducedTrace');ys=[p['y']for p in trace];OUT['actions'].append({'label':label,'trace':trace,'range':g});check(g['top']>=10 and g['bottom']<=g['height']-9,label+' reduced-motion semantic response framed',g);check(len(set(round(y,1)for y in ys))<=2,label+' reduced motion has no smooth intermediate positions',trace)
try:
 source_guard();check(ev('matchMedia("(prefers-reduced-motion: reduce)").matches'),'Actual owned Firefox reduced-motion preference');viewport(390,760);direct();action('#part-saturation','Wrong-part','.part-selection-status');action('#part-root','Target','.choice-fieldset');action('#choice-1','Choice','.candidate','.check-helper');action('#check-button','Check','.feedback','.round-next button');check(ev('!!document.querySelector(".feedback.is-success")'),'Reduced-motion actual authored repair earned');shot('earned');click('.round-next button');check(ev('document.querySelector(".round-progress-counter").textContent')=='Κουίζ 2/3'and abs(ev('scrollY'))<1,'Reduced-motion Next advances to question2 at top');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
