"""Extract the checked welcome/library content without maintaining a second syllabus.

Only trusted repository HTML is read. Runtime React renders text/element nodes,
never raw HTML. The small legacy panel literal is parsed as data, not executed.
"""
import ast
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}


class TreeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {'tag': 'document', 'attrs': {}, 'children': []}
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'children': []}
        self.stack[-1]['children'].append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index]['tag'] == tag:
                self.stack = self.stack[:index]
                return

    def handle_data(self, data):
        self.stack[-1]['children'].append(data)


def walk(node):
    if isinstance(node, dict):
        yield node
        for child in node['children']:
            yield from walk(child)


def text(node):
    return node if isinstance(node, str) else ''.join(map(text, node['children']))


def select(tree, tag):
    return next(node for node in walk(tree) if node['tag'] == tag)


def read_page(filename):
    path = ROOT / 'design' / filename
    parser = TreeParser()
    raw = path.read_text()
    parser.feed(raw)
    body = select(parser.root, 'body')
    return {
        'source': 'design/' + filename,
        'sourceSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'title': text(select(parser.root, 'title')),
        'styles': '\n'.join(text(node) for node in walk(parser.root)
                            if node['tag'] == 'style'),
        'header': select(body, 'header'),
        'main': select(body, 'main'),
        'footer': select(body, 'footer'),
    }, raw


def main():
    welcome, raw = read_page('welcome-proposal.html')
    library, _ = read_page('theory-library.html')
    # The source currently uses a data-only object of quoted strings/arrays.
    literal = re.search(r'const panels=(\{.*?\});\s*document\.', raw, re.S)
    if not literal:
        raise ValueError('Welcome panel data changed; update the extractor explicitly.')
    quoted = re.sub(r'([,{])\s*(\w+)\s*:', r'\1"\2":', literal.group(1))
    panels = ast.literal_eval(quoted)
    assert set(panels) == {'games', 'teacher', 'login'}
    cards = [node for node in walk(library['main'])
             if node['tag'] == 'article' and node['attrs'].get('class') == 'lesson']
    links = [node['attrs']['href'] for node in walk(library['main'])
             if node['tag'] == 'a' and 'scenario=' in node['attrs'].get('href', '')]
    assert len(cards) == 9 and len(links) == 12
    content = {'welcome': welcome, 'library': library, 'panels': panels,
               'inventory': {'cards': len(cards), 'lessonLinks': links}}
    dest = ROOT / 'react-preview' / 'src' / 'content.json'
    serialized = json.dumps(content, ensure_ascii=False, indent=2) + '\n'
    if '--check' in sys.argv:
        if dest.read_text() != serialized:
            raise ValueError('Content snapshot is stale; run npm run sync-content.')
        print('Content matches source: 9 cards, 12 existing lessons (read-only).')
    else:
        if not dest.exists() or dest.read_text() != serialized:
            dest.write_text(serialized)
        print('Content synchronized: 9 cards, 12 existing lessons; source hashes recorded.')


if __name__ == '__main__':
    main()
