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
from urllib.parse import parse_qs, urlsplit

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


def has_class(node, name):
    return isinstance(node, dict) and name in node['attrs'].get('class', '').split()


def clean_text(node):
    return ' '.join(text(node).split())


def formula_data(node):
    if node is None:
        return None
    parts, restriction = [], None
    for child in node['children']:
        if isinstance(child, str):
            if child.strip():
                parts.append({'kind': 'text', 'value': child.strip()})
        elif child['tag'] == 'sub':
            parts.append({'kind': 'subscript', 'value': clean_text(child)})
        elif has_class(child, 'restriction'):
            restriction = clean_text(child)
        else:
            raise ValueError('Unsupported formula markup; update the catalog extractor.')
    return {'parts': parts, 'restriction': restriction}


def lesson_data(block):
    direct = [child for child in block['children'] if isinstance(child, dict)]
    heading = next(child for child in direct if child['tag'] in {'h2', 'h3'})
    descriptions = [child for child in direct if child['tag'] == 'p'
                    and not has_class(child, 'series-formula')
                    and not any(has_class(item, 'count') for item in walk(child))]
    if len(descriptions) != 1:
        raise ValueError('Expected exactly one lesson description.')
    link = next(child for child in direct if child['tag'] == 'a'
                and has_class(child, 'action'))
    href = link['attrs']['href']
    url = urlsplit(href)
    if url.path != '../mulermoc-nom-51.html' or url.scheme or url.netloc:
        raise ValueError('Unexpected lesson player URL.')
    scenario = parse_qs(url.query)['scenario'][0]
    scenario_path = (ROOT / scenario).resolve()
    scenario_path.relative_to(ROOT / 'scenarios')
    scenario_json = json.loads(scenario_path.read_text())
    step_count = len(scenario_json['steps'])
    count = next((item for item in walk(block) if has_class(item, 'count')), None)
    if count is not None and clean_text(count) != f'{step_count} βήματα':
        raise ValueError('Lesson badge does not match its scenario step count.')
    action_label = ''.join(text(child) for child in link['children']
                           if not isinstance(child, dict)
                           or child['attrs'].get('aria-hidden') != 'true').strip()
    formula = next((child for child in direct if has_class(child, 'series-formula')), None)
    topics = next((child for child in direct if has_class(child, 'topics')), None)
    return {
        'id': heading['attrs']['id'].removesuffix('-title'),
        'title': clean_text(heading),
        'description': clean_text(descriptions[0]),
        'formula': formula_data(formula),
        'steps': step_count,
        'topics': [clean_text(child) for child in topics['children']
                   if isinstance(child, dict) and child['tag'] == 'li'] if topics else [],
        'href': href,
        'scenario': scenario,
        'actionLabel': action_label,
    }


def normalize_library(library):
    main = library.pop('main')
    categories = []
    for card in walk(main):
        if card['tag'] != 'article' or not has_class(card, 'lesson'):
            continue
        header = next(child for child in card['children'] if has_class(child, 'illustration'))
        body = next(child for child in card['children'] if has_class(child, 'content'))
        parts = [child for child in body['children'] if has_class(child, 'lesson-part')]
        formula = next((node for node in walk(header) if has_class(node, 'series-formula')), None)
        categories.append({
            'id': card['attrs']['aria-labelledby'].removesuffix('-title'),
            'title': clean_text(next(node for node in walk(header) if has_class(node, 'formula'))),
            'formula': formula_data(formula),
            'summaryLabel': clean_text(next(node for node in walk(header) if has_class(node, 'count'))),
            'lessons': [lesson_data(part) for part in parts] if parts else [lesson_data(body)],
        })
    category_ids = [item['id'] for item in categories]
    lessons = [lesson for item in categories for lesson in item['lessons']]
    if not categories or len(category_ids) != len(set(category_ids)):
        raise ValueError('Missing or duplicate catalog categories.')
    if len({lesson['id'] for lesson in lessons}) != len(lessons):
        raise ValueError('Duplicate lesson IDs.')
    for category in categories:
        if len(category['lessons']) == 1:
            if category['summaryLabel'] != f"{category['lessons'][0]['steps']} βήματα":
                raise ValueError('Category badge does not match its lesson step count.')
    library.update({
        'catalogVersion': 1,
        'eyebrow': clean_text(next(node for node in walk(main) if has_class(node, 'eyebrow'))),
        'heading': clean_text(select(main, 'h1')),
        'intro': clean_text(next(node for node in walk(main) if has_class(node, 'intro'))),
        'categories': categories,
    })
    return [lesson['href'] for lesson in lessons]


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
    links = normalize_library(library)
    card_count = len(library['categories'])
    content = {'welcome': welcome, 'library': library, 'panels': panels,
               'inventory': {'cards': card_count, 'lessonLinks': links}}
    dest = ROOT / 'react-preview' / 'src' / 'content.json'
    serialized = json.dumps(content, ensure_ascii=False, indent=2) + '\n'
    if '--check' in sys.argv:
        if dest.read_text() != serialized:
            raise ValueError('Content snapshot is stale; run npm run sync-content.')
        print(f'Content matches source: {card_count} cards, {len(links)} existing lessons (read-only).')
    else:
        if not dest.exists() or dest.read_text() != serialized:
            dest.write_text(serialized)
        print(f'Content synchronized: {card_count} cards, {len(links)} existing lessons; source hashes recorded.')


if __name__ == '__main__':
    main()
