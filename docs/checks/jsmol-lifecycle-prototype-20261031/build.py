from pathlib import Path
import hashlib,json,difflib,gzip,os
root=Path(os.environ.get('NAMELECULE_JSMOL_PROTOTYPE_ROOT','/tmp/namelecule-jsmol-lifecycle-prototype-20261031'));repo=Path.cwd();here=Path(__file__).resolve().parent
root.mkdir(exist_ok=True)
for version in ['baseline','candidate']:
 target=root/('app-'+version);target.mkdir(exist_ok=True)
 for item in repo.iterdir():
  if item.name.startswith('.') or item.name=='mulermoc-nom-52.html':continue
  link=target/item.name
  if not link.exists():link.symlink_to(item)
 (root/('vendor-'+version)).mkdir(exist_ok=True)
source=gzip.decompress((here/'base-source.js.gz').read_bytes()).decode();helper=(here/'lifecycle-helper.js').read_text()
meta=json.loads(Path('docs/checks/jsmol-lifecycle-20261031/external-source-provenance.json').read_text())['JSmol.min.js'];sha=lambda s:hashlib.sha256(s.encode()).hexdigest();assert sha(source)==meta['SHA256']
marker='a._setDestroy=function';assert source.count(marker)==1
candidate=source.replace(marker,helper+'\n'+marker,1)
old='a._destroy=function(c){try{';new='a._destroy=function(c){a._nameleculeLifecycle.dispose(c);try{';assert candidate.count(old)==1;candidate=candidate.replace(old,new,1)
start=candidate.index('c._resize=function(){');end=candidate.index(';return c};a.repaint=',start)
oldResize=candidate[start:end];newResize='c._resize=function(){a._nameleculeLifecycle.resize(this)}';candidate=candidate[:start]+newResize+candidate[end:]
start=candidate.index('a.repaint=function(b,c){');end=candidate.index(';a.loadImage=',start);oldPaint=candidate[start:end]
newPaint='''a.repaint=function(b,c){
+if(!b||!b._appletPanel||!a._nameleculeLifecycle.live(b))return;
+var panel=b._appletPanel,d=a.$(b,"appletdiv"),f=Math.round(d.width()),h=Math.round(d.height());
+if(!a._nameleculeLifecycle.live(b,panel))return;
+if(b._is2D&&(b._canvas.width!=f||b._canvas.height!=h)){
+  b._newCanvas(!0);
+  if(!a._nameleculeLifecycle.live(b,panel))return;
+  panel.setDisplay(b._canvas);
+}
+if(!a._nameleculeLifecycle.live(b,panel))return;
+panel.setScreenDimension(f,h);
+a._nameleculeLifecycle.paint(b,panel,c,function(){panel.paint?panel.paint(null):panel.update(null)});
+}'''.replace('\n+','\n')
candidate=candidate[:start]+newPaint+candidate[end:]
for version,text in [('baseline',source),('candidate',candidate)]:
 (root/('vendor-'+version)/'JSmol.min.js').write_text(text)
 html=(repo/'mulermoc-nom-52.html').read_text();needle='"https://chemapps.stolaf.edu/jmol/jsmol/JSmol.min.js"';assert html.count(needle)==1;html=html.replace(needle,'"/vendor-'+version+'/JSmol.min.js"');(root/('app-'+version)/'mulermoc-nom-52.html').write_text(html)
(root/'vendor.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True),candidate.splitlines(True),fromfile='pinned-JSmol.min.js',tofile='candidate-JSmol.min.js')))
(root/'base-source.js.gz').write_bytes(gzip.compress(source.encode(),mtime=0))
(root/'build-manifest.json').write_text(json.dumps({'sourceSHA256':sha(source),'candidateSHA256':sha(candidate),'helperSHA256':sha(helper),'sourceURL':meta['url'],'changedSites':['lifecycle helper before _setDestroy','_destroy prefix','_resize body','repaint body'],'oldResize':oldResize,'oldPaint':oldPaint},indent=2)+'\n')
print('Built isolated candidate',sha(candidate))
