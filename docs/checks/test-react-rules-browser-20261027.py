"""Focused rule checks in actual Firefox; main source is not modified."""
from pathlib import Path
# Reuse the existing connection and ACK-aware helpers, not the ether suite.
helper=Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\ntry:\n',1)[0]
exec(compile(helper,'existing-viewer-harness','exec'))

# Compare the actual legacy rule DOM against React output, independently of
# the adapter serializer. No source engine/scenario changes are made.
normalize=r"""(root)=>{
 const walk=n=>n.nodeType===3?n.textContent:n.nodeType===1?{tag:n.tagName.toLowerCase(),classes:[...n.classList],row:n.getAttribute('data-row'),children:[...n.childNodes].filter(n=>[1,3].includes(n.nodeType)).map(walk)}:null;
 return [...root.childNodes].filter(n=>[1,3].includes(n.nodeType)).map(walk);
}"""
def parity(key,ident):
 source=json.loads(cev("JSON.stringify([...document.querySelectorAll('#ruleTheoryContainer > .ruleTheory')].filter(p=>p.querySelector('.ruleTile')?.textContent.trim()).map(p=>({title:p.querySelector('.ruleTile').textContent.trim(),text:("+normalize+")(p.querySelector('.ruleText')),table:("+normalize+")(p.querySelector('.ruleTable')),textClasses:[...p.querySelector('.ruleText').classList].filter(c=>c!=='ruleText')})))"))
 actual=json.loads(ev("JSON.stringify([...document.querySelectorAll('.react-rule-panel')].map(p=>({title:p.querySelector('button').textContent.slice(2),text:("+normalize+")(p.querySelector('.ruleText')),table:("+normalize+")(p.querySelector('.ruleTable')),textClasses:[...p.querySelector('.ruleText').classList].filter(c=>c!=='ruleText')})))"))
 assert source==actual,(key,ident,source,actual)
 assert ev("[...document.querySelectorAll('.react-rule-toggle')].every(b=>b.getAttribute('aria-expanded')==='false' && document.getElementById(b.getAttribute('aria-controls')).hidden)")
 result['cases'].append({'molecule':key,'component':ident,'titles':[p['title'] for p in source],'exactDOM':True})
 return source

def open_rule():
 ev("document.querySelector('.react-rule-toggle').click()")
 assert ev("document.querySelector('.react-rule-toggle').getAttribute('aria-expanded')==='true' && !document.querySelector('.react-rule-body').hidden")

def selected_id():return ev("document.querySelector('[data-component][aria-pressed=true]')?.dataset.component")

try:
 navigate('react-preview/dist/?v=rules-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe()
 assert not ev("!!document.querySelector('.react-rule-panel')")
 # Cover all 19 existing series, including mixed functional groups (A/B),
 # branched alkyls, enynes and both common/systematic naming conventions.
 representatives=[next(m['id'] for m in reversed(catalog) if m['series']==series) for series in dict.fromkeys(m['series'] for m in catalog)]
 for key in representatives:
  pick(key)
  ids=json.loads(ev("JSON.stringify([...document.querySelectorAll('[data-component]')].map(e=>e.dataset.component))"))
  for ident in ids:
   component(ident);rules=parity(key,ident)
   if rules:
    open_rule()
    assert ev("document.querySelector('.react-rule-body').scrollWidth<=document.querySelector('.react-rule-body').clientWidth+1"),(key,ident,'overflow')
    selected=json.loads(ev("JSON.stringify([...document.querySelectorAll('.react-rule-body .ruleRow.selected')].map(e=>({classes:e.className,color:getComputedStyle(e.querySelector('.ruleCase')).color,bg:getComputedStyle(e).backgroundColor})))"))
    for row in selected:
     if 'selectedA' in row['classes']:assert row['color']=='rgb(27, 39, 93)' and row['bg']=='rgb(200, 217, 236)'
     elif 'ruleAlkyl' not in ev("document.querySelector('.react-rule-body .namingRuleTable')?.className||''"):assert row['color']=='rgb(255, 255, 255)'
   component(ident);assert selected_id() is None;parity(key,'none')
  print('Rule parity',key,len(ids),flush=True)
 result['checks'].append('All visible components for 19 representative series: exact source text/tree/sub/sup/row classes; initially closed; no-rule deselection; desktop table fit and selected colors')
 # Source rules stay optional across ordinary viewer operations.
 pick('dimethyl_2_3_butane')
 ids=json.loads(ev("JSON.stringify([...document.querySelectorAll('[data-component]')].map(e=>e.dataset.component))"))
 target=next(i for i in ids if cev("document.getElementById("+json.dumps(i)+").textContent.includes('βουτ')"))
 component(target);parity('dimethyl_2_3_butane',target);open_rule()
 ev("document.querySelector('.react-rule-toggle').focus()")
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':' '},{'type':'keyUp','value':' '}]}]})
 assert ev("document.querySelector('.react-rule-body').hidden")
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':'\ue007'},{'type':'keyUp','value':'\ue007'}]}]})
 assert ev("!document.querySelector('.react-rule-body').hidden")
 action("document.querySelector('button[aria-label=Μεγέθυνση]').click()")
 assert ev("!document.querySelector('.react-rule-body').hidden")
 view('3d');assert ev("!document.querySelector('.react-rule-body').hidden")
 view('2d');form('expanded');assert ev("!document.querySelector('.react-rule-body').hidden")
 form('condensed')
 # While a component ACK is pending, old rule cannot be reopened.
 cev("window.__savedModelProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:__savedModelProperty(a,p,...r)}")
 other=next(i for i in ids if i!=target)
 ev("document.querySelector('[data-component="+other+"]').click()")
 wait(ev,"document.querySelector('.react-rule-toggle').disabled && document.querySelector('.react-rule-body').hidden")
 cev('Jmol.getPropertyAsArray=__savedModelProperty')
 wait(ev,'window.__etherAck===window.__etherSent');parity('dimethyl_2_3_butane',other)
 # Rapid component commands close immediately and end with the last rule.
 ev("document.querySelector('[data-component="+target+"]').click();document.querySelector('[data-component="+other+"]').click();document.querySelector('[data-component="+target+"]').click()")
 wait(ev,'window.__etherAck===window.__etherSent');assert selected_id()==target;parity('dimethyl_2_3_butane',target)
 open_rule();pick('ethanol');assert not ev("!!document.querySelector('.react-rule-panel')")
 result['checks'].append('Manual Space/Enter; open retained on zoom/2D/3D/form; immediate close and disabled old rule during delayed ACK; rapid commands; molecule switch resets')
 pick('ethyl_isopropyl_ether');naming('iupac')
 for ident in json.loads(ev("JSON.stringify([...document.querySelectorAll('[data-component]')].map(e=>e.dataset.component))")):
  component(ident);rules=parity('ethyl_isopropyl_ether',ident)
  if rules:open_rule();break
 naming('common');assert not ev("!!document.querySelector('.react-rule-panel')")
 for ident in json.loads(ev("JSON.stringify([...document.querySelectorAll('[data-component]')].map(e=>e.dataset.component))")):
  component(ident);parity('ethyl_isopropyl_ether-common',ident);component(ident)
 naming('iupac')
 result['checks'].append('Ether IUPAC/common transitions reset panels; original unavailable common-alkyl/alkoxy rules remain absent')
 # Malformed rule message must be rejected before any title/content mutation.
 before=ui_analysis()
 ev("(()=>{let d=structuredClone(window.__etherLast);d.analysis.rules=[{id:'component',title:'FAKE',text:[],textClasses:[],table:[{tag:'script',classes:[],row:null,children:['window.BAD=1']}]}];dispatchEvent(new MessageEvent('message',{origin:location.origin,source:document.querySelector('iframe').contentWindow,data:d}))})()")
 assert ui_analysis()==before and not ev("!!window.BAD")
 assert not ev("document.querySelector('.react-name-analysis').textContent.includes('FAKE')")
 result['checks'].append('Invalid structured rule packet ignored; no arbitrary element/script rendering')
 pick('dimethyl_2_3_butane')
 # Prefer alkyl table for narrow layout; source alone chooses content.
 for ident in json.loads(ev("JSON.stringify([...document.querySelectorAll('[data-component]')].map(e=>e.dataset.component))")):
  component(ident)
  if ev("!!document.querySelector('.react-rule-body .ruleAlkyl')"):break
  component(ident)
 open_rule();screenshot('/tmp/react-rules-desktop-20261027.png')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});time.sleep(.4)
 result['mobile']=json.loads(ev("JSON.stringify({width:innerWidth,scroll:document.documentElement.scrollWidth,panel:document.querySelector('.react-rule-panel').getBoundingClientRect().width,body:document.querySelector('.react-rule-body').clientWidth,bodyScroll:document.querySelector('.react-rule-body').scrollWidth})"))
 assert result['mobile']['scroll']<=390 and result['mobile']['bodyScroll']<=result['mobile']['body']+1,result['mobile']
 screenshot('/tmp/react-rules-mobile-20261027.png')
 result['checks'].append('1500px/390px rule layout, no page/panel horizontal overflow; screenshots captured')
 result['javascriptErrors']=js_errors;assert not js_errors,js_errors
 result['completed']=True
finally:
 Path('/tmp/react-rules-browser-20261027.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'checks':result['checks'],'javascriptErrors':len(js_errors)},ensure_ascii=False,indent=2))
