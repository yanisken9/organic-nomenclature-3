from pathlib import Path
exec((Path(__file__).with_name('integration.py')).read_text().split('try:\n lesson();',1)[0])
try:
 previous=json.loads((HERE/'diagnostic-cold-wait-results.json').read_text())['storageAtFailure'];records=[json.loads(v)for k,v in previous.items() if k.startswith('namelecule:lesson-checkpoints:')];record=next(r for r in records if r.get('states',{}).get('3',{}).get('games',{}).get('repair')is not None)
 evidence=record['practices']['3']['games']['repair'];assert evidence['currentRound']==2 and all(s['submitted'] and s['attempts']>0 for s in evidence['states'])
 open_page('mulermoc-nom-55.html?scenario=docs/checks/alkanes-game-choice-20261111/before/scenarios/alkanes-user-3.scenario.json&present=1#step=4');ready()
 check(ev('fScenarioPresent().steps[3].checkpoint.type')=='generated-name-repair-set','Old exact lesson runtime loaded')
 raw=ev('(()=>{let s=fScenarioPresent(),content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps}),h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);let key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16);let value=JSON.stringify({version:1,content,states:{3:'+json.dumps(evidence)+'},practices:{}});sessionStorage.setItem(key,value);window.__legacyMigration={key,value};return JSON.stringify(__legacyMigration)})()');legacy=json.loads(raw)
 lesson(4);wait('fScenarioPresent().index===4',60);new=rec();check(new['states']['3']['solved'] and new['states']['3']['earned']['game']=='repair','Actual old Workshop receipt migrates and revalidates before step5');check(new['states']['3']['games']['repair']['seed']==evidence['seed'],'Migration preserves exact original triple');check(ev('sessionStorage.getItem('+json.dumps(legacy['key'])+')')==legacy['value'],'Old record bytes unchanged')
 ev('NameleculeQuizCheckpoints.reset(fScenarioPresent());true');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();wait('fScenarioPresent().index===3');check(not rec()['states'] and ev('sessionStorage.getItem('+json.dumps(legacy['key'])+')')==legacy['value'],'Explicit current reset survives refresh without old-record resurrection')
 OUT['passed']=True;OUT['jsExceptions']=js_errors
except Exception as e:
 OUT['passed']=False;OUT['failure']=repr(e);OUT['traceback']=traceback.format_exc();shot('migration-failure.png');raise
finally:
 (HERE/'migration-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n');finish()
