"""Reproduce the retained 12-lesson React host without replacing existing files."""
import argparse
import hashlib
import json
import re
from pathlib import Path

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

catalog = json.loads((preview / 'src/content.json').read_text())
specs = {}
for category in catalog['library']['categories']:
    for entry in category['lessons']:
        key, scenario = entry['id'], entry['scenario']
        assert re.fullmatch(r'[a-z][a-z0-9-]*', key) and key not in specs
        assert scenario.startswith('scenarios/') and scenario.endswith('.json') and '..' not in scenario
        lesson = json.loads((root / scenario).read_text())
        assert entry['steps'] == len(lesson['steps']) and entry['steps'] > 0
        titles = [s['title'] for s in lesson['steps']]
        assert all(isinstance(title, str) and 0 < len(title) <= 200 for title in titles)
        specs[key] = {'id': key, 'scenario': scenario, 'total': entry['steps'], 'titles': titles}
if len(specs) != 12 or sum(spec['total'] for spec in specs.values()) != 283:
    raise ValueError('Frozen React lessons must remain 12 courses / 283 steps')
source, frozen = frozen_template()
source = source.replace('<head>', '<head>\n  <base href="../../" />', 1)
# Keep the native content layout, DOM and scoped presentation styles. React
# supplies only the enclosing shell/navigation. No renderer is substituted.
css = '''
.nameleculeHeader, #scenarioPlayBar, #scenarioAuthorBar, #creditsUs,
#rotatePrompt, #lessonLoading { display:none!important; }
html, body { margin:0!important; min-width:0!important; }
'''
source = source.replace('</head>', '<style>\n' + css + '\n</style>\n<script>JSmol_Applet.script = "set defaultDirectory " + JSON.stringify(new URL("../../", location.href).href) + ";";</script>\n</head>', 1)
bridge = (preview / 'public/lesson-host-bridge.js').read_text()
assert bridge.count('__NAMELECULE_LESSONS__') == 1
bridge = bridge.replace('__NAMELECULE_LESSONS__', json.dumps(specs, ensure_ascii=False))
assert '</script' not in bridge.lower()
source = source.replace('</body>', '<script>\n' + bridge + '\n</script>\n</body>', 1)
parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
dest = preview / 'public/lesson-host.html'
result = publish_host(dest, source, frozen, args.check)
print(result + ' frozen React lesson host (12 lessons / 283 steps)')
