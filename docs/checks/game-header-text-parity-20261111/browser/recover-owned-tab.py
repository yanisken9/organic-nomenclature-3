"""Try normal Firefox reopen-closed-tab in the owned profile; no state fabrication."""
from pathlib import Path
exec((Path(__file__).with_name('helpers.py')).read_text())
R={}
try:
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'owned-reopen','actions':[{'type':'keyDown','value':'\ue03d'},{'type':'keyDown','value':'\ue008'},{'type':'keyDown','value':'t'},{'type':'keyUp','value':'t'},{'type':'keyUp','value':'\ue008'},{'type':'keyUp','value':'\ue03d'}]}]});pause(.7)
 R['tree']=call('browsingContext.getTree',{})
 targets=[c for c in R['tree']['contexts'] if 'textParity=20261111-r1' in c.get('url','')]
 R['recovered']=bool(targets)
 if targets:
  ctx=targets[0]['context'];call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]});ready();R['record']=rec();R['storage']=read('Object.fromEntries(Object.entries(sessionStorage))');R['url']=ev('location.href')
 print(json.dumps({'recovered':R['recovered'],'urls':[c.get('url') for c in R['tree']['contexts']]},ensure_ascii=False))
finally:
 (HERE/'recovery-results.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n');finish()
