"""Generate a catalog-bounded lesson host; never edit the main player."""
import argparse
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[2]
preview = root / 'react-preview'
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
assert specs
source = (root / 'mulermoc-nom-52.html').read_text()
source, count = re.subn(r'  <!-- Google tag \(gtag.js\) -->.*?(?=  <title>)', '', source, count=1, flags=re.S)
assert count == 1
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
if args.check:
    assert dest.read_text() == source, 'Rebuild lesson host'
else:
    dest.write_text(source)
print(('Lesson host matches current v52 source: ' if args.check else 'Generated lesson host: ') + str(len(specs)) + ' existing lessons')
