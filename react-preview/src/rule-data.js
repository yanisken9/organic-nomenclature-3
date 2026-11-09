import schema from './rule-schema.json' with { type: 'json' };

const exactKeys = (value, keys) => !!value && typeof value === 'object' &&
  Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key));
const validClasses = classes => Array.isArray(classes) && classes.length <= schema.classes.length &&
  new Set(classes).size === classes.length && classes.every(name => schema.classes.includes(name));

// The renderer consumes only these fields, never DOM attributes, styles or HTML.
export function validRules(rules) {
  if (!Array.isArray(rules) || rules.length > 2) return false;
  const ids = new Set();
  return rules.every(rule => {
    if (!exactKeys(rule, ['id', 'title', 'text', 'textClasses', 'table']) ||
        !['component', 'alkoxy'].includes(rule.id) || ids.has(rule.id) ||
        typeof rule.title !== 'string' || !rule.title.trim() || rule.title.length > 180 ||
        !validClasses(rule.textClasses)) return false;
    ids.add(rule.id);
    let count = 0, textLength = 0;
    function nodes(value, depth) {
      if (!Array.isArray(value) || depth > schema.maxDepth || value.length > schema.maxNodes) return false;
      return value.every(node => {
        if (++count > schema.maxNodes) return false;
        if (typeof node === 'string') {
          textLength += node.length;
          return textLength <= schema.maxText;
        }
        return exactKeys(node, ['tag', 'classes', 'row', 'children']) &&
          schema.tags.includes(node.tag) && validClasses(node.classes) &&
          (node.row === null || (typeof node.row === 'string' && /^[\p{L}\p{N}_-]{1,80}$/u.test(node.row))) &&
          (node.tag !== 'br' || (Array.isArray(node.children) && node.children.length === 0)) &&
          nodes(node.children, depth + 1);
      });
    }
    return nodes(rule.text, 0) && nodes(rule.table, 0);
  });
}
