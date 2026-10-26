// Read-only behavior checks against the real normalized library catalog.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { filterCategories, normalizeGreek } from '../../react-preview/src/library-search.js';

const content = JSON.parse(fs.readFileSync(new URL('../../react-preview/src/content.json', import.meta.url), 'utf8'));
const categories = content.library.categories;
const original = JSON.stringify(categories);
const all = ['alkanes', 'alkenes', 'alkynes', 'alkadienes', 'enynes',
  'monoalcohols', 'other-alcohols', 'monoethers', 'monoaldehydes',
  'other-aldehydes', 'monoketones', 'other-ketones'];
let cases = 0;
assert.equal(normalizeGreek('ΆΛΛΕΣ ΑΛΔΕΫΔΕΣ'), 'αλλεσ αλδευδεσ'); cases++;
for (const [query, categoryId, expected] of [
  ['', '', all],
  ['', 'ketones', ['monoketones', 'other-ketones']],
  ['ΑΛΚΟΟΛΕΣ', '', ['monoalcohols', 'other-alcohols']],
  ['αλδευδεσ', '', ['monoaldehydes', 'other-aldehydes']],
  ['άλΛες', '', ['other-alcohols', 'other-aldehydes', 'other-ketones']],
  ['κορεσμενες', '', ['monoalcohols', 'monoaldehydes', 'monoketones']],
  ['αλκυλια', '', ['alkanes', 'alkenes', 'alkynes', 'alkadienes', 'enynes', 'monoethers']],
  ['αλφαβητικη σειρα', '', ['alkanes', 'alkenes', 'alkynes', 'alkadienes', 'enynes', 'monoethers']],
  ['κετονεσ κορεσμενεσ', '', ['monoketones']],
  ['ΑΛΛΕΣ', 'ketones', ['other-ketones']],
  ['αλκοολες', 'ketones', []],
  ['αλλες', 'alcohols', ['other-alcohols']],
  ['τελείως άγνωστο', '', []],
  ['  \t ', '', all],
  ['', 'missing-category', []],
  ['<script>alert(1)</script>', '', []],
  ['δΙΠΛΟΣ ΤΡΙΠΛΟΣ', '', ['enynes']],
]) {
  const actual = filterCategories(categories, query, categoryId).flatMap(item => item.lessons.map(lesson => lesson.id));
  assert.deepEqual(actual, expected, JSON.stringify({ query, categoryId }));
  cases++;
}
assert.equal(JSON.stringify(categories), original, 'Filtering must not mutate the source catalog'); cases++;
assert.equal(categories.length, 9);
assert.equal(categories.flatMap(item => item.lessons).reduce((sum, lesson) => sum + lesson.steps, 0), 283); cases++;
console.log(JSON.stringify({ passed: true, cases, sourceCatalogUnchanged: true,
  scope: 'Greek accent/case/final-sigma normalization; all-term search; category combinations; empty states; ordering; immutable catalog' }));
