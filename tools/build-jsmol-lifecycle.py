"""Rebuild/check the exact reviewed Namelecule JSmol bundle, without downloads.

Default --check is read-only. --write explicitly writes the output bundle.
The original bundle, helper and reviewed input manifest remain archived in docs.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "docs/checks/jsmol-lifecycle-prototype-20261031"
TARGET = ROOT / "js/vendor/jsmol/namelecule-20261031-r1/JSmol.min.js"
SOURCE_SHA = "7ade5bf896b800582acd0067d2f669433a501d2c450c8c4a176604a379f771a6"
HELPER_SHA = "fe038bc9bb7754e9d3e822b123fc1673ccc2c7184e3d6d68311703bfdbc91a48"
OUTPUT_SHA = "d99b1168acbbd55d59073943e6fde174513e8b815ddb88ae8f1bfa927961b323"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Pinned JSmol patch site is missing or ambiguous")
    return text.replace(old, new, 1)


def build():
    source = gzip.decompress((INPUT / "base-source.js.gz").read_bytes())
    helper = (INPUT / "lifecycle-helper.js").read_bytes()
    if sha(source) != SOURCE_SHA or sha(helper) != HELPER_SHA:
        raise ValueError("Archived source/helper differs from reviewed inputs")
    text = replace_once(source.decode(), "a._setDestroy=function", helper.decode() + "\na._setDestroy=function")
    text = replace_once(text, "a._destroy=function(c){try{", "a._destroy=function(c){a._nameleculeLifecycle.dispose(c);try{")
    manifest = json.loads((INPUT / "build-manifest.json").read_text())
    text = replace_once(text, manifest["oldResize"], "c._resize=function(){a._nameleculeLifecycle.resize(this)}")
    paint = '''a.repaint=function(b,c){
if(!b||!b._appletPanel||!a._nameleculeLifecycle.live(b))return;
var panel=b._appletPanel,d=a.$(b,"appletdiv"),f=Math.round(d.width()),h=Math.round(d.height());
if(!a._nameleculeLifecycle.live(b,panel))return;
if(b._is2D&&(b._canvas.width!=f||b._canvas.height!=h)){
  b._newCanvas(!0);
  if(!a._nameleculeLifecycle.live(b,panel))return;
  panel.setDisplay(b._canvas);
}
if(!a._nameleculeLifecycle.live(b,panel))return;
panel.setScreenDimension(f,h);
a._nameleculeLifecycle.paint(b,panel,c,function(){panel.paint?panel.paint(null):panel.update(null)});
}'''
    output = replace_once(text, manifest["oldPaint"], paint).encode()
    if sha(output) != OUTPUT_SHA:
        raise ValueError("Rebuild differs from independently reviewed candidate")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Check without writing (default)")
    mode.add_argument("--write", action="store_true", help="Write the exact reviewed bundle")
    parser.add_argument("--output", type=Path, default=TARGET)
    args = parser.parse_args()
    output = build()
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(output)
    elif not args.output.is_file() or args.output.read_bytes() != output:
        raise SystemExit("Bundle is missing or differs; use --write only for an intentional rebuild")
    print("JSmol lifecycle bundle verified: " + OUTPUT_SHA)


if __name__ == "__main__":
    main()
