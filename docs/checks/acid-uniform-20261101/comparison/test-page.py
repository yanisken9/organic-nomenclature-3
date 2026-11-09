"""Check the six-pair comparison UI and standalone SVG glyph/bond clearance."""
from pathlib import Path
import os,json,gzip,traceback,hashlib
from urllib.parse import urlsplit,parse_qs
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
gallery=json.loads((HERE/'figure-framing.json').read_text())['molecules'];out={'cases':[],'figureAudits':[],'versionedAssetChecks':[],'completed':False}
def image_path(url):
    parts=urlsplit(url);assert not parts.scheme and not parts.netloc and '/'not in parts.path
    path=HERE/parts.path
    assert parse_qs(parts.query)=={'v':[hashlib.sha256(path.read_bytes()).hexdigest()]}
    return path
def loaded():until('[...document.querySelectorAll(".pairs img")].every(i=>i.complete&&i.naturalWidth>0)')
def check(index,width,font):
    loaded();row=json.loads(ev('JSON.stringify({name:document.getElementById("name").textContent,counter:document.getElementById("counter").textContent,previousDisabled:document.getElementById("previous").disabled,nextDisabled:document.getElementById("next").disabled,sizes:[...document.querySelectorAll(".pairs img")].map(i=>{const b=i.getBoundingClientRect();return [b.width,b.height]}),sources:[...document.querySelectorAll(".pairs img")].map(i=>i.getAttribute("src")),overflow:document.documentElement.scrollWidth>innerWidth+1})'));row.update(index=index,width=width,fontCSS=font)
    assert row['name']==gallery[index]['name']and row['counter']==str(index+1)+' / '+str(len(gallery))
    assert row['previousDisabled']==(index==0)and row['nextDisabled']==(index==len(gallery)-1)
    out['lastMeasuredCase']=row
    assert not row['overflow']and all(abs(a-b)<.001 for a,b in zip(row['sizes'][0],row['sizes'][1])),row
    assert all(abs(size[0]-gallery[index]['widthEm']*font)<.05 and abs(size[1]-gallery[index]['heightEm']*font)<.05 for size in row['sizes'])
    assert row['sources']==[gallery[index]['images'][v]for v in ['before','proposed']]
    out['cases'].append(row)
try:
    navigate('docs/checks/acid-uniform-20261101/comparison/index.html')
    # Verify default and forced-cache responses against the URL's content hash.
    urls=[url for item in gallery for url in item['images'].values()]
    for url in urls:image_path(url)
    checks=json.loads(ev('(async()=>{const rows=[];for(const mode of ["default","force-cache"]){for(const src of '+json.dumps(urls)+'){const response=await fetch(src,{cache:mode});if(!response.ok)throw Error("Image fetch failed: "+src);const bytes=await response.arrayBuffer(),hash=[...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))].map(v=>v.toString(16).padStart(2,"0")).join("");rows.push({src,mode,hash,expected:new URL(src,location.href).searchParams.get("v")});}}return JSON.stringify(rows)})()'))
    assert len(checks)==len(gallery)*4 and all(row['hash']==row['expected']for row in checks)
    out['versionedAssetChecks']=checks
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        ev('document.getElementById("molecule").value="0";document.getElementById("molecule").dispatchEvent(new Event("change"));document.getElementById("reset-size").click();true')
        for index in range(len(gallery)):
            if index:ev('document.getElementById("next").click();true')
            check(index,width,26)
            if width==1500:screenshot(HERE/(gallery[index]['key']+'-comparison.png'))
        ev('document.getElementById("previous").click();true');check(0,width,26)
        for font in [18,36]:
            ev('document.getElementById("size").value='+json.dumps(str(font))+';document.getElementById("size").dispatchEvent(new Event("input"));true');check(0,width,font)
        ev('document.getElementById("reset-size").click();true');check(0,width,26)
        ev('document.getElementById("molecule").value="1";document.getElementById("molecule").dispatchEvent(new Event("change"));true');check(1,width,26)
        if width==390:screenshot(HERE/'comparison-390.png')
    # Independent raster oracle on exported figures, at the exact common font sizes.
    capture=json.load(gzip.open(HERE/'browser.json.gz','rt'))['cases'];ev((ROOT/'tools/2d-label-probe.js').read_text())
    for item in gallery:
        for variant in ['before','proposed']:
            source=next(r for r in capture if r['key']==item['key']and r['variant']==variant and r['width']==1500)
            replay={k:source[k]for k in ['key','name','atomSymbols','bondGraph']};replay['mode']='expanded'
            raw=image_path(item['images'][variant]).read_text()
            for font in [18,26]:
                ev('(()=>{document.getElementById("snapshot")?.remove();window.__auditReplaySource='+json.dumps(replay)+';const d=document.createElement("div");d.id="snapshot";d.innerHTML='+json.dumps(raw)+';document.body.append(d);const svg=d.querySelector("svg");svg.style.width='+json.dumps(str(item['widthEm']*font)+'px')+';svg.style.height='+json.dumps(str(item['heightEm']*font)+'px')+';return true})()')
                row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(variant=variant,fontCSS=font)
                assert not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount'],(item['key'],variant,font)
                # Prove the actual glyph transform gives the advertised common font.
                actual=ev('(()=>{const s=document.querySelector("#snapshot svg"),t=s.querySelector("text[data-namelecule-role=label]"),m=t.getScreenCTM();return parseFloat(getComputedStyle(t).fontSize)*Math.hypot(m.a,m.b)})()');assert abs(actual-font)<.01,(actual,font)
                out['figureAudits'].append(row)
    ev('document.getElementById("snapshot").remove();delete window.__auditReplaySource;true');out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
    out['javascriptErrors']=js_errors;(HERE/'page-check.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'UIcases':len(out['cases']),'figureAudits':len(out['figureAudits']),'jsErrors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
