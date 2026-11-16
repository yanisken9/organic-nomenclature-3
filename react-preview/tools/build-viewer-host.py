"""Reproduce the retained React molecule host without replacing existing files."""
from pathlib import Path
import argparse
import hashlib
import re
import json

root = Path(__file__).resolve().parents[2]
preview = root / 'react-preview'

def frozen_template():
    """Validate the retained inputs before computing or creating any output."""
    manifest = json.loads((preview / 'preserved-main-20261030/PROVENANCE.json').read_text())
    frozen = manifest['frozenReact']
    if (frozen['moleculeCount'], frozen['lessonCount'], frozen['stepCount']) != (126, 12, 283):
        raise ValueError('Frozen React inventory must remain 126 molecules, 12 lessons / 283 steps')
    for name, expected in frozen['inputs'].items():
        path = root / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen React input differs or is missing: ' + name)
    return (root / frozen['template']).read_text(), frozen


def publish_host(destination, source, frozen, check):
    """Check existing bytes; create missing outputs exclusively, never replace."""
    raw = source.encode('utf-8')
    name = destination.relative_to(root).as_posix()
    if hashlib.sha256(raw).hexdigest() != frozen['outputs'][name]:
        raise ValueError('Generated host differs from the retained React baseline: ' + name)
    if destination.exists():
        if destination.read_bytes() != raw:
            raise ValueError('Existing host differs; refusing to overwrite: ' + name)
        return 'Verified existing'
    if check:
        raise ValueError('Host is missing; --check never creates files: ' + name)
    # Exclusive creation also prevents overwriting a file created concurrently.
    with destination.open('xb') as stream:
        stream.write(raw)
    return 'Created missing'

source, frozen = frozen_template()
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
if len(ids) != frozen['moleculeCount'] or len(ids) != len(set(ids)):
    raise ValueError('Frozen React molecule IDs must remain 126 unique entries')
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
result = publish_host(dest, source, frozen, args.check)
print(result + ' frozen React viewer host (126 molecules)')
