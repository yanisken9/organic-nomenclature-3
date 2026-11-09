"""Reproducible isolated patch; refuses to write inside the source repository."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
repo=Path(__file__).resolve().parents[3]
root=Path(sys.argv[1]).resolve()
assert root.is_relative_to(Path('/private/tmp')) or root.is_relative_to(Path('/tmp')),root
root.mkdir(parents=True,exist_ok=True)
vendor=repo/'jsme/FEB169D74546A3B279D22AE09AFB86BD.cache.js'
expected='93c3116d5e0775b9fe6953c79102813dac966f7589414ad52509f0c1e254b789'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(vendor)==expected, "Vendor differs from reviewed input"
baseline={str(p.relative_to(repo)):sha(p) for p in [vendor,repo/'js/mulermoc-nom-core-52.js',repo/'js/mulermoc-nom-molview-52.js',repo/'js/jsme-nick-nomeclature-moc2-data_52.js',repo/'mulermoc-nom-52.html']}
# Decode actual vendor payload without executing the module.
jsc='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
decoder=root/'decode.js';decoder.write_text('var jsme={onScriptDownloaded:function(a){print(JSON.stringify(a.join("")))}};eval(JSON.parse(readline()));')
original=json.loads(subprocess.check_output([jsc,str(decoder)],input=json.dumps(vendor.read_text()).encode()).decode())
# Only EQ's cap metric and pre-render label geometry change. Global CQ stays intact.
start=original.index('function EQ(a)');end=original.index('function vQ(',start)
part=original[start:end]
a='c=9;a.n&&(c=CQ(a.n.F));';b='c=9;a.n&&(c=nProtoCap(a.n.F.a));'
assert part.count(a)==1
part=part.replace(a,b)
a='if((!a.p.e||a.p.i)&&-99199!=b.j)';b='nProtoLabel(b.b,a.n.F.a);'+a
assert part.count(a)==1
part=part.replace(a,b)
helper=(Path(__file__).parent/'producer-metrics.js').read_text()
patched=original[:start]+helper+'\n'+part+original[end:]
for name in ['baseline','candidate']:
 target=root/name/'jsme'
 if not target.exists():shutil.copytree(repo/'jsme',target)
(root/'candidate/jsme'/vendor.name).write_text('jsme.onScriptDownloaded(['+json.dumps(patched)+']);\n')
(root/'baseline-decoded.js').write_text(original);(root/'candidate-decoded.js').write_text(patched)
for name in ['baseline','candidate']:
 (root/name/'index.html').write_text('''<!doctype html><meta charset="utf-8"><body><div id="host"></div><div id="export"></div><script>
window.loaded=false;window.jsmeOnLoad=function(){window.a=new JSApplet.JSME('host','600px','400px',{options:'depict,marker',depictbg:'#fff',atombgsize:'0.6'});window.loaded=true;};
</script><script src="jsme/jsme.nocache.js"></script>''')
(root/'baseline.json').write_text(json.dumps({'production':baseline,'candidateVendor':sha(root/'candidate/jsme'/vendor.name),'sourceVendor':sha(vendor),'baseCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo).decode().strip()},indent=2)+'\n')
print(root)
