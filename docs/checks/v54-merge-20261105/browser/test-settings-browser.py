from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/v54-upstream-20261104/browser/support.py').read_text(),'support','exec'))
def read(s):return json.loads(ev('JSON.stringify('+s+')'))
try:
 navigate('mulermoc-nom-54.html?lang=gr');app_ready();until('typeof fMulerLang==="function"&&document.readyState==="complete"');call('browsingContext.activate',{'context':ctx})
 keys={'radioChainMode':'chainCalc','originalJSME':'showOrig2D','autoLinearize':'autoLinearize','highlightNumberingSetting':'hlAtoms','highlightNumberingBondsSetting':'hlBonds','bondAtomsSetting':'hlBondAtoms','atomColorModeRow':'atomColor2D','atomSymbolsSetting':'atomSymbols3D','viewerMaxHeightSetting':'maxHeight1','viewerBothHeightSetting':'bothHeight','customMolSetting':'customMols'}
 for lang in ['gr','en','gr']:
  if ev('fMulerLang()')!=lang:
   click('#langSwitch [data-lang="'+lang+'"]');until('typeof fMulerLang==="function"&&fMulerLang()==='+json.dumps(lang)+'&&document.readyState==="complete"');app_ready()
  until('document.readyState==="complete"&&document.documentElement.lang==='+json.dumps('el' if lang=='gr' else 'en')+'&&'+json.dumps(list(['radioChainMode','originalJSME','autoLinearize','highlightNumberingSetting','highlightNumberingBondsSetting','bondAtomsSetting','atomColorModeRow','atomSymbolsSetting','viewerMaxHeightSetting','viewerBothHeightSetting','customMolSetting']))+'.every(id=>!!document.querySelector("#"+id+" .settingLabel"))')
  labels=read('Object.entries('+json.dumps(keys)+').map(([row,key])=>({row,actual:document.querySelector("#"+row+" .settingLabel").firstChild.textContent.trim(),expected:MULER_STRINGS[key]['+json.dumps(lang)+']}))')
  check(all(r['actual']==r['expected'] for r in labels),'All eleven real settings correctly labelled '+lang,labels)
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors
 Path('docs/checks/v54-merge-20261105/browser/settings-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
