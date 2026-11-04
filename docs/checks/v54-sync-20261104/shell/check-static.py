"""Bounded developer checks for the isolated v54 shell and welcome integration."""
from pathlib import Path
from html.parser import HTMLParser
import base64, hashlib, json, re, subprocess
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'docs/checks/v54-sync-20261104/shell'
UP = Path('/tmp/namelecule-sync-preflight-20261104/head')
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
OWNED = ['mulermoc-nom-54.html', 'js/mulermoc-nom-teaching-54.js', 'js/mulermoc-nom-scenario-54.js', 'js/mulermoc-nom-note-54.js', 'js/ui-icons-54.js', 'css/jsme-nick-54.css', 'css/mulermoc-nom-scenario-54.css', 'css/namelecule-54.css', 'spt/init-54.spt', 'design/welcome-proposal.html']
checks = []
def check(ok, label, detail=None):
    checks.append({'ok': bool(ok), 'label': label, 'detail': detail})
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids=[]; self.refs=[]; self.inline=[]; self._script=None; self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='script':
            self._script=[] if not a.get('src') else None
            if a.get('src'): self.refs.append(a['src'])
        elif tag=='link' and a.get('rel')=='stylesheet': self.refs.append(a['href'])
    def handle_endtag(self, tag):
        if tag=='script' and self._script is not None:
            self.inline.append(''.join(self._script)); self._script=None
    def handle_data(self, data):
        if self._script is not None: self._script.append(data)
html=(ROOT/'mulermoc-nom-54.html').read_text(); page=Page(html); upstream=Page((UP/'mulermoc-nom-54.html').read_text())
check(not [x for x in page.ids if page.ids.count(x)>1], 'No duplicate shell IDs')
check(set(upstream.ids).issubset(page.ids), 'All upstream active shell IDs retained', sorted(set(upstream.ids)-set(page.ids)))
check(all((ROOT/ref.split('?')[0]).exists() for ref in page.refs if not ref.startswith('http')), 'Every static local54 script and stylesheet resolves')
check(not re.search(r'(?:src|href)="(?:js|css)/[^"\n]*(?:-52\.|_52\.)',html), 'No54 runtime references to version52 files')
check('js/ui-icons-54.js?' in html and 'js/ui-icons.js?' not in html, 'Icons isolated54')
check('namelecule-label-metrics.js?v=20261031-r1' in html and 'data-namelecule-2d-font-size="22"' in html, 'Pinned label metrics and22px preserved')
check('namelecule-20261031-r1/jsme.nocache.js' in html and 'namelecule-20261031-r1/96E40B969193BD74B8A621486920E79C.cache.js' in html, 'Custom pinned JSME preserved')
sri='sha384-'+base64.b64encode(hashlib.sha384((ROOT/'js/vendor/jsmol/namelecule-20261031-r1/JSmol.min.js').read_bytes()).digest()).decode()
check(sri in html, 'Pinned JSmol integrity matches actual bytes')
check('lesson-loading' in html and 'lessonLoading' in page.ids and 'fLessonLoadingDone' in html, 'Presentation loading cover retained')
check('nameleculeHeader' in html and 'langSwitch' in page.ids and 'jsmeEditDraft' in page.ids and 'viewerSettingsBtnDiv' in page.ids, 'Custom brand plus upstream language/settings/dedicated edit draft')
for rel in ['css/jsme-nick-54.css','css/mulermoc-nom-scenario-54.css','js/ui-icons-54.js']:
    upstreamrel='js/ui-icons.js' if rel=='js/ui-icons-54.js' else rel
    check((ROOT/rel).read_bytes()==(UP/upstreamrel).read_bytes(), 'Exact upstream import '+rel)
check((ROOT/'spt/init-54.spt').read_bytes()==(UP/'spt/init-3.spt').read_bytes(), 'Exact upstream init3 imported as init54')
check((ROOT/'js/mulermoc-nom-note-54.js').read_bytes()==(UP/'js/mulermoc-nom-note-54.js').read_bytes(), 'Exact upstream note54 import')
check((ROOT/'css/namelecule-54.css').read_bytes()==(ROOT/'css/namelecule-52.css').read_bytes(), 'Local theme preserved as copy54')
for rel in ['js/mulermoc-nom-teaching-54.js','js/mulermoc-nom-scenario-54.js']:
    funcs=lambda p:set(re.findall(r'^function\s+(\w+)\(',p.read_text(),re.M))
    missing=funcs(UP/rel)-funcs(ROOT/rel)
    check(not missing,'Every upstream function retained '+rel,sorted(missing))
check((ROOT/'js/mulermoc-nom-teaching-54.js').read_text().count('$(document).on("click", "#alkoxyRuleTitle"')==1,'Alkoxy rule title has one delegated toggle')
baseline=json.loads((ROOT/'docs/checks/v54-sync-20261104/baseline.json').read_text())['hashes']
preserve=[p for p in baseline if re.search(r'(?:-52\.|_52\.)',p) or p in ['js/ui-icons.js','spt/init-3.spt','js/namelecule-label-metrics.js'] or p.startswith(('react-preview/','scenarios/','games/'))]
changed=[p for p in preserve if sha(ROOT/p)!=baseline[p]]
check(not changed,'All baseline52/shared/React/scenario/game assets preserved',{'checked':len(preserve),'changed':changed})
welcome=(ROOT/'design/welcome-proposal.html').read_text(); old=(OUT/'before/design/welcome-proposal.html').read_text()
check('<h2>Παίζω και εξασκούμαι</h2>' in welcome and 'href="../games/name-repair.html?v=logo-3d-20261104-r1">Συνεργείο ονομάτων ' in welcome, 'Welcome semantic direct game link with accepted card/game names')
check('data-panel="games"' not in welcome and 'games:[' not in welcome and 'σκορ' not in welcome,'Removed stale game panel and score promises')
for key in ['teacher','login']:
    value=lambda t:re.search(key+r':(\[[^\]]*\])',t).group(1)
    check(value(old)==value(welcome),'Unchanged '+key+' dialog contract')
check('mulermoc-nom-54.html' not in welcome and (ROOT/'design/theory-library.html').read_text()==(OUT/'before/design/theory-library.html').read_text(),'Main54 activation deferred; library byte-identical')
patch=subprocess.run(['git','apply','--check',str(OUT/'activate-v54-navigation.patch')],cwd=ROOT,capture_output=True,text=True)
check(patch.returncode==0,'Prepared navigation activation patch applies cleanly',patch.stderr)
syntax='var failures=[];\n'
for rel in [p for p in OWNED if p.endswith('.js')]:
    syntax+='try { new Function(readFile('+json.dumps(rel)+')); } catch(e) { failures.push({file:'+json.dumps(rel)+',error:String(e)}); }\n'
for rel in ['mulermoc-nom-54.html','design/welcome-proposal.html']:
    for i,script in enumerate(Page((ROOT/rel).read_text()).inline):
        syntax+='try { new Function('+json.dumps(script)+'); } catch(e) { failures.push({file:'+json.dumps(rel+' inline#'+str(i))+',error:String(e)}); }\n'
syntax+='print(JSON.stringify({failures:failures}));if(failures.length)quit(1);\n'
(OUT/'syntax-check.js').write_text(syntax)
run=subprocess.run([JSC,str((OUT/'syntax-check.js').relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True)
check(run.returncode==0,'JavaScriptCore syntax checks for owned JS and actual inline HTML scripts',run.stdout.strip()+run.stderr.strip())
result={'checks':len(checks),'passed':sum(c['ok'] for c in checks),'results':checks,'scope':'Developer static/schema evidence; browser behavior remains primary-agent work.','hashes':{p:sha(ROOT/p) for p in OWNED}}
(OUT/'static-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':result['checks'],'passed':result['passed'],'failures':[c for c in checks if not c['ok']]},ensure_ascii=False,indent=2))
raise SystemExit(0 if all(c['ok'] for c in checks) else 1)
