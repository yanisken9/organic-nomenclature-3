from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={}
try:
 open_page('games/name-builder.html')
 wait('document.querySelectorAll("#bank-tiles button").length>0 || document.querySelector("#game-status.error")',50)
 out=read('({status:document.querySelector("#game-status").textContent,error:!!document.querySelector("#game-status.error"),bank:[...document.querySelectorAll("#bank-tiles button")].map(x=>x.textContent),events:__builderEvents,host:document.querySelector("iframe").contentWindow.NameleculeNameBuilderHost?.snapshot(),hostText:document.querySelector("iframe").contentDocument.body.innerText.slice(0,2000)})')
 shot('first-open.png')
 out['javascriptErrors']=js_errors
 print(json.dumps({k:v for k,v in out.items() if k!='events'},ensure_ascii=False),flush=True)
 assert not out['error'],out['status']
except Exception:
 out['failure']=traceback.format_exc()
 try:shot('first-open-failure.png')
 except Exception:pass
 print(out['failure'],flush=True)
finally:
 (HERE/'first-open.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 finish()
if out.get('failure'):raise SystemExit(1)
