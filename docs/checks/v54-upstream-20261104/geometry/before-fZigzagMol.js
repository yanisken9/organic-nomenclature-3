function fZigzagMol(text, chain) {
  try {
    var m = fParseMolV2000(text);
    if (!fMolCanTransform2D(m, true)) return null;
    if (!Array.isArray(chain) || !chain.length) return null;
    var n = m.atoms.length;
    var map = {}, order = [];
    for (var i = 0; i < n; i++) {
      if (!fIsHeavyEl2D(m.atoms[i].el)) continue;
      map[i + 1] = order.length;
      order.push(i);
    }
    if (!order.length) return null;
    var ch = [];
    for (var c = 0; c < chain.length; c++) {
      var a0 = (chain[c] | 0) - 1;
      if (a0 >= 0 && a0 < n && map[a0 + 1] != null) ch.push(a0);
    }
    if (!ch.length) return null;
    var adj = [], ord = {};
    for (var h0 = 0; h0 < n; h0++) adj[h0] = [];
    for (var b = 0; b < m.bonds.length; b++) {
      var bb = m.bonds[b];
      var x = bb[0] - 1, y = bb[1] - 1;
      if (x < 0 || y < 0 || x >= n || y >= n) continue;
      if (map[x + 1] == null || map[y + 1] == null) continue;
      adj[x].push(y); adj[y].push(x);
      var k = (x < y) ? x + "-" + y : y + "-" + x;
      if (!ord[k] || ord[k] < bb[2]) ord[k] = bb[2];
    }
    var bo = function (a, c) {
      var kk = (a < c) ? a + "-" + c : c + "-" + a;
      return ord[kk] || 1;
    };
    var L = 1.17, CX = L * 0.8660254, CY = L * 0.5;
    var norm2 = function (vx, vy) {
      var l = Math.sqrt(vx * vx + vy * vy);
      if (!(l > 1e-9)) return null;
      return { x: vx / l, y: vy / l };
    };
    var pos = {}, visited = {}, segDir = {};
    pos[ch[0]] = { x: 0, y: 0 }; visited[ch[0]] = true;
    var sgn = -1, pdx = CX, pdy = CY, prevTriple = false;
    for (var k = 1; k < ch.length; k++) {
      var oPrev = bo(ch[k - 1], ch[k]);
      if (oPrev === 3 || prevTriple) { /* keep direction (sp collinear) */ }
      else { sgn = -sgn; pdx = CX; pdy = sgn * CY; }
      prevTriple = (oPrev === 3);
      pos[ch[k]] = { x: pos[ch[k - 1]].x + pdx, y: pos[ch[k - 1]].y + pdy };
      visited[ch[k]] = true;
      segDir[k] = { x: pdx, y: pdy };
    }
    // Branch directions from chain atoms (external-angle bisector).
    var queue = [];
    for (var ci = 0; ci < ch.length; ci++) {
      var c0 = ch[ci], usedC = 0;
      var dIn = (ci > 0) ? segDir[ci] : null;
      var dOut = (ci < ch.length - 1) ? segDir[ci + 1] : null;
      for (var nb = 0; nb < adj[c0].length; nb++) {
        var br = adj[c0][nb];
        if (visited[br]) continue;
        var bd;
        if (!dIn && !dOut) { bd = { x: 1, y: 0 }; }
        else if (!dIn) { bd = norm2(-dOut.x, -dOut.y) || { x: -1, y: 0 }; }
        else if (!dOut) { bd = { x: dIn.x, y: dIn.y }; }
        else {
          var fx = dIn.x - dOut.x, fy = dIn.y - dOut.y;
          bd = norm2(fx, fy);
          if (!bd) { bd = norm2(-dOut.y, dOut.x) || { x: 0, y: 1 }; }
        }
        if (usedC > 0) {
          var r2 = (usedC % 2 === 1) ? 1 : -1;
          bd = norm2(-bd.y * r2, bd.x * r2) || bd;
        }
        usedC++;
        queue.push({ node: br, fx: c0, dx: bd.x, dy: bd.y, rot: 0 });
      }
    }
    while (queue.length) {
      var it = queue.shift();
      if (visited[it.node]) continue;
      visited[it.node] = true;
      var Pp = pos[it.fx] || m.atoms[it.fx];
      pos[it.node] = { x: Pp.x + it.dx * L, y: Pp.y + it.dy * L };
      var kids = 0;
      for (var w = 0; w < adj[it.node].length; w++) {
        var cand = adj[it.node][w];
        if (visited[cand]) continue;
        var nd;
        if (kids === 0) { nd = { x: it.dx, y: it.dy }; }
        else {
          var rr = (kids % 2 === 1) ? 1 : -1;
          nd = norm2(-it.dy * rr, it.dx * rr) || { x: -it.dx, y: -it.dy };
        }
        kids++;
        queue.push({ node: cand, fx: it.node, dx: nd.x, dy: nd.y });
      }
    }
    var atoms = [], newIdx = {};
    for (var o = 0; o < order.length; o++) {
      var oi = order[o];
      var pp = pos[oi] || { x: m.atoms[oi].x, y: m.atoms[oi].y };
      newIdx[oi + 1] = atoms.length + 1;
      atoms.push(fCopyMolAtom2D(m.atoms[oi], pp.x, pp.y));
    }
    var bonds = [];
    for (var j = 0; j < m.bonds.length; j++) {
      var bj = m.bonds[j];
      if (newIdx[bj[0]] && newIdx[bj[1]]) bonds.push(fCopyMolBond2D(bj, newIdx[bj[0]], newIdx[bj[1]]));
    }
    return fWriteMolV2000(m.head, atoms, bonds, m);
  } catch (e) { return null; }
}
