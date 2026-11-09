"""Reproduce versioned JSME display-only patch from pinned installed inputs.
Original vendor files are read only. --check is the default; --write is explicit.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'jsme';TARGET=ROOT/'js/vendor/jsme/namelecule-20261031-r1'
MODULE='FEB169D74546A3B279D22AE09AFB86BD.cache.js'
SOURCE_SHA='93c3116d5e0775b9fe6953c79102813dac966f7589414ad52509f0c1e254b789'
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def sha(b):return hashlib.sha256(b).hexdigest()
def replace_once(s,a,b):
 if s.count(a)!=1:raise ValueError('Pinned patch site missing/ambiguous: '+a[:70])
 return s.replace(a,b,1)
def build():
 pins=json.loads((ROOT/'tools/jsme-label-inputs.json').read_text())['files']
 actual={str(p.relative_to(SOURCE)):sha(p.read_bytes()) for p in SOURCE.rglob('*') if p.is_file()}
 if actual!=pins:raise ValueError('JSME source inventory differs from pinned inputs')
 raw=(SOURCE/MODULE).read_bytes()
 if sha(raw)!=SOURCE_SHA:raise ValueError('Original module differs from pinned source')
 decoder='var jsme={onScriptDownloaded:function(a){print(JSON.stringify(a.join("")))}};eval(JSON.parse(readline()));'
 decoded=json.loads(subprocess.check_output([JSC,'-e',decoder],input=json.dumps(raw.decode()).encode()+b'\n'))
 s=replace_once(decoded,'c=9;a.n&&(c=CQ(a.n.F));','c=9;a.n&&(c=$wnd.NameleculeLabelMetrics?$wnd.NameleculeLabelMetrics.nativeCap(a.n.F.a,CQ(a.n.F)):CQ(a.n.F));')
 s=replace_once(s,'if((!a.p.e||a.p.i)&&-99199!=b.j)','var nBounds=$wnd.NameleculeLabelMetrics&&$wnd.NameleculeLabelMetrics.nativeLabel(b.b,a.n.F.a);if(nBounds)b.b.a=new hR(nBounds.x,nBounds.y,nBounds.right-nBounds.x,nBounds.bottom-nBounds.y);if((!a.p.e||a.p.i)&&-99199!=b.j)')
 # The native painter knows the real atom number, including sparse skeletal labels.
 s=replace_once(s,'VP(Hc,Zb);OP(t,(nO(),qO)[v.b[ka].c]);','VP(Hc,Zb.replace("<rect ","<rect data-namelecule-atom=\\\""+ka+"\\\" data-namelecule-role=\\\"backplate\\\" "));OP(t,(nO(),qO)[v.b[ka].c]);')
 s=replace_once(s,'VP(xe,Qc)}if(!Q)','VP(xe,Qc.replace("<text ","<text data-namelecule-atom=\\\""+ka+"\\\" data-namelecule-role=\\\"label\\\" "))}if(!Q)')
 return ('jsme.onScriptDownloaded(['+json.dumps(s)+']);\n').encode()
def main():
 p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group();mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true');args=p.parse_args();data=build()
 if args.write:
  TARGET.mkdir(parents=True,exist_ok=True)
  for src in SOURCE.rglob('*'):
   if src.is_file():
    dst=TARGET/src.relative_to(SOURCE);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data if src.name==MODULE and src.parent==SOURCE else src.read_bytes())
 else:
  for src in SOURCE.rglob('*'):
   if src.is_file():
    dst=TARGET/src.relative_to(SOURCE);expected=data if src.name==MODULE and src.parent==SOURCE else src.read_bytes()
    if not dst.is_file()or dst.read_bytes()!=expected:raise SystemExit('Versioned JSME differs: '+str(dst))
 print('Versioned JSME bundle verified: '+sha(data))
if __name__=='__main__':main()
