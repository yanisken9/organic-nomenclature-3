/* Read-only pixel oracle. Firefox DOM text boxes can overestimate tiny glyphs. */
window.auditGlyphOverlap = function (svg = document.querySelector('#jsmeNomeclatureSVG svg')) {
  const outer = svg.getBoundingClientRect(), scale = 4;
  const width = Math.ceil(outer.width * scale), height = Math.ceil(outer.height * scale);
  const owners = new Int32Array(width * height), pairs = new Map();
  const labels = [...svg.querySelectorAll('text')].filter(text => {
    const style = getComputedStyle(text);
    return style.display !== 'none' && style.visibility !== 'hidden' &&
      (text.dataset.nameleculeRole === 'label' || text.id.startsWith('number'));
  });
  let inkPixels = 0;
  for (const [index, text] of labels.entries()) {
    const rect = text.getBoundingClientRect(), matrix = text.getScreenCTM();
    if (!matrix || !rect.width || !rect.height) continue;
    const left = Math.floor((rect.left - outer.left) * scale) - 8;
    const top = Math.floor((rect.top - outer.top) * scale) - 8;
    const w = Math.ceil(rect.width * scale) + 16, h = Math.ceil(rect.height * scale) + 16;
    const canvas = document.createElement('canvas'); canvas.width = w; canvas.height = h;
    const context = canvas.getContext('2d', {willReadFrequently: true});
    const walker = document.createTreeWalker(text, NodeFilter.SHOW_TEXT);
    let node, character = 0;
    while ((node = walker.nextNode())) {
      const style = getComputedStyle(node.parentElement);
      for (const char of node.textContent) {
        const point = text.getStartPositionOfChar(character++);
        if (style.display === 'none' || style.visibility === 'hidden') continue;
        context.setTransform(scale * matrix.a, scale * matrix.b, scale * matrix.c,
          scale * matrix.d, scale * (matrix.e - outer.left) - left,
          scale * (matrix.f - outer.top) - top);
        context.font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
        context.textBaseline = 'alphabetic'; context.fillStyle = 'black';
        context.fillText(char, point.x, point.y);
        if (style.stroke !== 'none' && !text.id.startsWith('number')) {
          context.strokeStyle = 'black'; context.lineWidth = parseFloat(style.strokeWidth) || 0;
          context.strokeText(char, point.x, point.y);
        }
      }
    }
    const pixels = context.getImageData(0, 0, w, h).data;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      if (pixels[(y * w + x) * 4 + 3] < 128) continue;
      const u = left + x, v = top + y;
      if (u < 0 || v < 0 || u >= width || v >= height) continue;
      inkPixels++;
      const offset = v * width + u, owner = owners[offset];
      if (owner && owner !== index + 1) {
        const key = owner + ':' + (index + 1);
        pairs.set(key, (pairs.get(key) || 0) + 1);
      }
      owners[offset] = index + 1;
    }
  }
  return {method: 'Actual document fonts, SVG character positions, per-label Canvas pixels',
    scale, labels: labels.length, inkPixels,
    overlaps: [...pairs].map(([pair, pixels]) => ({labels: pair.split(':').map(Number), pixels}))};
};
