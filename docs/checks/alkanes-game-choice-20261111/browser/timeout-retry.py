from pathlib import Path
exec((Path(__file__).with_name('integration.py')).read_text().split('try:\n lesson();',1)[0])
call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':'''() => {
 const original=window.fetch;window.__holdCatalog=true;
 window.fetch=function(input,options){if(window.__holdCatalog&&String(input).includes('/games/data/alkane-structures.json')){window.__heldCatalogFetches=(window.__heldCatalogFetches||0)+1;return new Promise(()=>{});}return original.apply(this,arguments);};
}'''})
try:
 lesson();open_gate();click('.nl-game-choice-card:nth-child(2)');begin=time.monotonic();wait('!!document.querySelector(".nl-builder-error")',52);elapsed=time.monotonic()-begin
 check(40<=elapsed<=52,'R2 stalled noncooperative catalog reaches bounded retry',elapsed);check(ev('!!document.querySelector(".nl-builder-error")&&!document.querySelector(".nl-builder-frame")'),'R2 no unverified native frame or answers');check(not rec()['states']['3']['solved'],'R2 timeout never grants access');shot('timeout-retry.png')
 ev('window.__holdCatalog=false;true');click('.nl-builder-error + button');builder_ready();check(ev('!document.querySelector(".nl-builder-error")'),'R2 retry succeeds using real verified Worker/native path');check(not rec()['states']['3']['solved'],'R2 retry alone never unlocks');OUT['passed']=True;OUT['elapsed']=elapsed;OUT['jsExceptions']=js_errors
except Exception as e:
 OUT['passed']=False;OUT['failure']=repr(e);OUT['traceback']=traceback.format_exc();shot('timeout-failure.png');raise
finally:
 (HERE/'timeout-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n');finish()
