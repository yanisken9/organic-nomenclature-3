"""Generate a React molecule host around the current v52 application."""
from pathlib import Path
import argparse
import re
import json

root = Path(__file__).resolve().parents[2]
preview = root / 'react-preview'
source = (root / 'mulermoc-nom-52.html').read_text()
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
html[data-view="3d"] #nomeclature3D { left:0!important; width:100%!important; height:100%!important; }
html[data-view="3d"] #jsmeNomeclatureDIV { left:-10000px!important; right:auto!important; visibility:hidden!important; }
'''
source = source.replace('</head>', '<style>\n' + css + '\n</style>\n<script>JSmol_Applet.script = \"set defaultDirectory \" + JSON.stringify(new URL(\"../../\", location.href).href) + \";\";</script>\n</head>', 1)
bridge = (preview / 'public/viewer-host-bridge.js').read_text()
catalog = json.loads((preview / 'src/molecules.json').read_text())
ids = [m['id'] for m in catalog]
assert ids and len(ids) == len(set(ids))
assert all(re.fullmatch(r'[A-Za-z0-9_]+', key) for key in ids)
assert 'ethanol' in ids
assert all(isinstance(m['title'], str) and isinstance(m['formula'], str) for m in catalog)
assert bridge.count('__NAMELECULE_MOLECULE_IDS__') == 1
bridge = bridge.replace('__NAMELECULE_MOLECULE_IDS__', json.dumps(ids))
assert bridge.count('__NAMELECULE_RULE_SCHEMA__') == 1
schema = json.loads((preview / 'src/rule-schema.json').read_text())
bridge = bridge.replace('__NAMELECULE_RULE_SCHEMA__', json.dumps(schema))
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
print('Viewer host matches current v52 source' if args.check else 'Generated viewer host')
