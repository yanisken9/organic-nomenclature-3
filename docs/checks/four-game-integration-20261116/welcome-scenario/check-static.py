#!/usr/bin/env python3
"""Bounded preservation and asset checks for the approved welcome/two-note change."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import hashlib, json, re, struct, difflib

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BEFORE = HERE.parent / 'before'
sha = lambda data: hashlib.sha256(data).hexdigest()
paths = ['design/welcome-proposal.html', 'scenarios/alkanes-user-3.scenario.json']
base = {path: (BEFORE / path).read_bytes() for path in paths}
current = {path: (ROOT / path).read_bytes() for path in paths}
old = json.loads(base[paths[1]])
new = json.loads(current[paths[1]])
assert len(new['steps']) == len(old['steps']) == 12

def differences(a, b, path=''):
    if type(a) is not type(b): return [path]
    if isinstance(a, dict):
        assert list(a) == list(b), ('key order or membership changed', path)
        return sum((differences(a[k], b[k], path + '.' + k) for k in a), [])
    if isinstance(a, list):
        assert len(a) == len(b), ('array size changed', path)
        return sum((differences(x, y, path + '[' + str(i) + ']') for i, (x, y) in enumerate(zip(a, b))), [])
    return [] if a == b else [path]

fields = differences(old, new)
assert fields == ['.steps[3].note', '.steps[10].note'], fields
# Prove every source byte outside the two JSON string tokens is preserved.
reconstructed = current[paths[1]].decode()
for idx in (3, 10):
    for name in ['Συνεργείο ονομάτων', 'Χτίσε το όνομα', 'Μοριακό παζλ', 'Μοριακός ντεντέκτιβ']:
        assert '<b>' + name + '</b>' in new['steps'][idx]['note']
    assert 'τρία διαφορετικά μόρια' in new['steps'][idx]['note']
    assert 'στο ίδιο παιχνίδι' in new['steps'][idx]['note']
    assert 'μία αποστολή ανά μόριο' in new['steps'][idx]['note']
    reconstructed = reconstructed.replace(json.dumps(new['steps'][idx]['note'], ensure_ascii=False), json.dumps(old['steps'][idx]['note'], ensure_ascii=False))
assert reconstructed.encode() == base[paths[1]]
html_before, html_after = (base[paths[0]].decode(), current[paths[0]].decode())
for cls in ['one', 'three']:
    pattern = r'<article class="card ' + cls + r'">.*?</article>'
    assert re.search(pattern, html_before, re.S).group() == re.search(pattern, html_after, re.S).group(), cls
for pattern in [r'<body><header>.*?</header>', r'<section class="representations">.*?</section>', r'<footer.*?</footer>', r'<dialog.*?</dialog>', r'<script>.*?</script>']:
    assert re.search(pattern, html_before, re.S).group() == re.search(pattern, html_after, re.S).group(), pattern

class WelcomeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.game_links = []
        self.images = []
        self.ids = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and 'game-action' in a.get('class', '').split(): self.game_links.append(a)
        if tag == 'img': self.images.append(a)
        if 'id' in a: self.ids.append(a['id'])
parser = WelcomeParser(); parser.feed(html_after); parser.close()
assert len(parser.ids) == len(set(parser.ids))
expected = ['name-repair.html', 'name-builder.html', 'molecular-puzzle.html', 'molecular-detective.html']
assert [Path(urlsplit(a['href']).path).name for a in parser.game_links] == expected
for a in parser.game_links:
    assert (ROOT / 'design' / urlsplit(a['href']).path).resolve().is_file(), a['href']
assets = []
for a in parser.images:
    file = (ROOT / 'design' / urlsplit(a['src']).path).resolve()
    assert file.is_file(), a['src']
    data = file.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', a['src']
    width, height = struct.unpack('>II', data[16:24])
    assert (int(a['width']), int(a['height'])) == (width, height), (a['src'], width, height)
    assets.append({'path': str(file.relative_to(ROOT)), 'width': width, 'height': height, 'SHA256': sha(data)})
assert 'object-fit:contain' in html_after
assert '.card.two .game-action-logo' in html_after
assert '@media(min-width:901px) and (max-width:1100px)' in html_after
result = {
    'changedPaths': paths,
    'hashes': {p: {'beforeSHA256': sha(base[p]), 'afterSHA256': sha(current[p])} for p in paths},
    'scenarioSteps': len(new['steps']), 'onlyChangedFields': fields,
    'allOtherScenarioBytesPreserved': True,
    'unaffectedWelcomeRegionsByteIdentical': ['card.one', 'card.three', 'header', 'representations', 'footer', 'dialog', 'script'],
    'gameRoutes': [a['href'] for a in parser.game_links], 'images': assets,
    'checks': 'passed',
    'limits': ['Static checks do not establish rendered fit, keyboard behavior or actual game navigation.', 'Browser checks pending the shared browser slot; no browser was launched.', 'No Desktop export performed by this worker; parent owns the mapped backup/export.']
}
(HERE / 'static.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
for p in paths:
    name = 'welcome.diff' if p.endswith('.html') else 'scenario.diff'
    (HERE / name).write_text(''.join(difflib.unified_diff(base[p].decode().splitlines(True), current[p].decode().splitlines(True), fromfile='before/' + p, tofile=p)))
print(json.dumps(result, ensure_ascii=False, indent=2))
