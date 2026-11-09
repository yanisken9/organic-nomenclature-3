from pathlib import Path
import os,json,hashlib,traceback
os.environ['NAMELECULE_BIDI_PORT']='9243';os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
H=Path('docs/checks/game-workshop-logo-20261104');paths=['games/name-repair.html','js/namelecule-game-repair.js','css/namelecule-games.css','games/data/name-repair-alkanes.json','js/mulermoc-nom-core-52.js']
hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in paths};out={'previewOnly':True,'filesBefore':hashes,'captures':[]}
try:
 navigate('games/name-repair.html?v=logo-preview-20261104');until('!!document.querySelector(".intro-copy h1")')
 ev("""(()=>{const title=document.querySelector('.intro-copy h1'),wrap=document.createElement('div'),img=document.createElement('img');wrap.className='workshop-title-preview';img.src='assets/name-repair/workshop-logo-v1.png';img.width=128;img.height=128;img.alt='Γαλλικό κλειδί με μοριακά σφαιρίδια';title.before(wrap);wrap.append(img,title);const style=document.createElement('style');style.textContent='.workshop-title-preview{display:flex;align-items:center;gap:18px;margin:0 0 24px}.workshop-title-preview h1{margin:0;min-width:0}.workshop-title-preview>img{width:128px;height:128px;object-fit:contain;flex:0 0 auto}@media(max-width:550px){.workshop-title-preview{gap:13px}.workshop-title-preview>img{width:88px;height:88px}.workshop-title-preview h1{font-size:2.25rem}}';document.head.append(style);return true})()""")
 until('document.querySelector(".workshop-title-preview img").complete&&document.querySelector(".workshop-title-preview img").naturalWidth>0')
 for width,height in [(1500,980),(390,900)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  assert ev('document.documentElement.scrollWidth<=innerWidth')
  screenshot(H/('intro-'+str(width)+'.png'));out['captures'].append({'width':width,'file':'intro-'+str(width)+'.png','noOverflow':True})
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':980},'devicePixelRatio':1})
 ev('document.querySelector(".intro-start").click();true');until('!!document.querySelector(".diagram-image.is-ready")')
 ev("""(()=>{const label=document.querySelector('.round-topbar .eyebrow'),img=document.createElement('img');img.src='assets/name-repair/workshop-logo-v1.png';img.width=36;img.height=36;img.alt='';img.style.cssText='width:36px;height:36px;object-fit:contain;flex-shrink:0';label.prepend(img);label.style.cssText='display:flex;align-items:center;gap:10px;margin:0';return true})()""")
 until('document.querySelector(".round-topbar .eyebrow img").naturalWidth>0');screenshot(H/'round-1500.png')
 out['captures'].append({'width':1500,'file':'round-1500.png','compactLogo':True})
 out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'])
finally:
 out['applicationFilesUnchanged']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==d for p,d in hashes.items());out['javascriptErrors']=js_errors
 (H/'preview.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({k:v for k,v in out.items()if k!='filesBefore'},ensure_ascii=False))
if not out.get('completed')or not out['applicationFilesUnchanged']:raise SystemExit(1)
