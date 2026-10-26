"""Generate a layout-only ethanol host from the unchanged v51 application."""
from pathlib import Path
import argparse
import re

root = Path(__file__).resolve().parents[2]
preview = root / 'react-preview'
source = (root / 'mulermoc-nom-51.html').read_text()
# Avoid adding another analytics page view. The source is untouched.
source, count = re.subn(r'  <!-- Google tag \(gtag.js\) -->.*?(?=  <title>)', '', source, count=1, flags=re.S)
assert count == 1
source = source.replace('<head>', '<head>\n  <base href="../../" />', 1)
css = '''
html, body { margin:0!important; padding:0!important; width:100%!important; height:100%!important; overflow:hidden!important; min-width:0!important; background:white!important; }
.nameleculeHeader, #rotatePrompt, #creditsUs, #lessonLoading, #scenarioAuthorBar, #scenarioPlayBar,
#pageContainer > :not(#authorLayout), #authorLayout > :not(#mainAppContainer),
.mainApp3Columns > :not(#viewerCol), #viewerCol > :not(#jsmeNomeclatureDIV):not(#nomeclature3D) { display:none!important; }
#pageContainer, #authorLayout, #mainAppContainer, .mainApp3Columns, #viewerCol { display:block!important; position:relative!important; margin:0!important; padding:0!important; width:100%!important; height:100%!important; max-width:none!important; min-width:0!important; border:0!important; }
#jsmeNomeclatureDIV { position:absolute!important; inset:0!important; margin:0!important; width:100%!important; height:100%!important; border:0!important; }
#jsmeNomeclatureSVG { width:100%!important; height:100%!important; }
/* Preserve the existing startup 3D viewport until initialization is complete. */
#nomeclature3D { position:absolute!important; left:-10000px!important; top:0!important; width:600px!important; height:300px!important; }
'''
source = source.replace('</head>', '<style>\n' + css + '\n</style>\n</head>', 1)
bridge = (preview / 'public/viewer-host-bridge.js').read_text()
assert '</script' not in bridge.lower()
source = source.replace('</body>', '<script>\n' + bridge + '\n</script>\n</body>', 1)
dest = preview / 'public/viewer-host.html'
parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
if args.check:
    assert dest.read_text() == source, 'Rebuild viewer host'
else:
    dest.write_text(source)
print('Viewer host matches unchanged v51 source' if args.check else 'Generated viewer host')
