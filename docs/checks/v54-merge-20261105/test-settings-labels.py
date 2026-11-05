"""Actual translation code + labels parsed from HTML; isolated JSC DOM, not browser evidence."""
from pathlib import Path
from html.parser import HTMLParser
import json,subprocess
ROOT=Path(__file__).resolve().parents[3]
CANDIDATE=Path('/tmp/namelecule-v54-merge-20261105-candidate')
HERE=Path(__file__).resolve().parent
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
KEYS={'radioChainMode':'chainCalc','originalJSME':'showOrig2D','autoLinearize':'autoLinearize','highlightNumberingSetting':'hlAtoms','highlightNumberingBondsSetting':'hlBonds','bondAtomsSetting':'hlBondAtoms','atomColorModeRow':'atomColor2D','atomSymbolsSetting':'atomSymbols3D','viewerMaxHeightSetting':'maxHeight1','viewerBothHeightSetting':'bothHeight','customMolSetting':'customMols'}
class Labels(HTMLParser):
 def __init__(self):super().__init__();self.stack=[];self.rows=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'settingLabel' in d.get('class','').split() and any(x.get('id')=='viewerSettingsPanel' for _,x in self.stack):
   owner=next((x.get('id') for _,x in reversed(self.stack) if x.get('id')),None)
   self.rows.append({'row':owner,'id':d.get('id'),'text':''})
  if tag not in ['input','br','img','link','meta','hr']:self.stack.append((tag,d))
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==tag:self.stack=self.stack[:i];break
 def handle_data(self,data):
  if self.rows and any('settingLabel' in x.get('class','').split() for _,x in self.stack):self.rows[-1]['text']+=data
JS=r"""
var rows=INPUT.rows.map(r=>Object.assign({},r,{firstChild:{textContent:r.text}}));
var document={documentElement:{},querySelectorAll:function(s){return s==='#viewerSettingsPanel .settingLabel'?rows:[]},
 querySelector:function(s){var m=/^#([^ ]+) \.settingLabel$/.exec(s);return m?rows.find(r=>r.row===m[1])||null:null},
 getElementById:function(id){return rows.find(r=>r.id===id)||null},addEventListener:function(){}};
var window={location:{search:''}},console={log:function(){}};
SOURCE
var activeLang='gr';fMulerLang=function(){return activeLang};
var failures=[],checks=0;
for(var lang of ['gr','en','gr']){activeLang=lang;fMulerPaintStaticChrome();
 for(var row of rows){var key=INPUT.keys[row.row];if(!key)continue;
  var expected=MULER_STRINGS[key][lang],actual=row.firstChild.textContent.trim();checks++;
  if(actual!==expected)failures.push({row:row.row,lang,expected,actual});}}
print(JSON.stringify({checks,failures,labels:rows.length}));
"""
def run(base,extra=False):
 parser=Labels();parser.feed((base/'mulermoc-nom-54.html').read_text())
 rows=parser.rows
 if extra:rows.insert(2,{'row':'unrelatedFutureSetting','id':None,'text':'Future control'})
 payload={'rows':rows,'keys':KEYS};src=(base/'js/mulermoc-nom-lang-54.js').read_text()
 code='var INPUT='+json.dumps(payload)+';\n'+JS.replace('SOURCE',src)
 p=subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return json.loads(p.stdout)
if __name__=='__main__':
 result={'before':run(HERE/'before'),'incoming':run(HERE/'upstream-target'),'candidate':run(CANDIDATE),'candidateFutureRow':run(CANDIDATE,True)}
 assert not result['before']['failures']
 assert result['incoming']['failures'],'Incoming regression must reproduce'
 assert not result['candidate']['failures'] and not result['candidateFutureRow']['failures']
 (HERE/'settings-labels.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:{'checks':v['checks'],'failures':len(v['failures'])} for k,v in result.items()}))
