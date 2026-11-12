/* Developer checks run against actual browser-loaded pure engine and source MOLs. */
(async function () {
  const E = NameleculeMolecularPuzzleEngine;
  const c = await (await fetch('data/alkane-structures.json')).json();
  const source = c.molecules.map(m => E.parseMol(m.mol));
  const report = [];
  function check(ok, label) { report.push({ label, passed: !!ok }); if (!ok) throw Error(label); }
  // Build independently from the names: parent paths, then named branches.
  function named(parent, branches) {
    const edges = [];
    for (let i = 1; i < parent; i++) edges.push([i, i + 1]);
    let count = parent;
    for (const [position, length] of branches) {
      let from = position;
      for (let j = 0; j < length; j++) { edges.push([from, ++count]); from = count; }
    }
    const degree = Array(count + 1).fill(0);
    edges.forEach(([a, b]) => { degree[a]++; degree[b]++; });
    return { nodes: Array.from({ length: count }, (_, i) => ({ id: String(i + 1), hydrogens: 4 - degree[i + 1] })),
      bonds: edges.map(([a, b]) => ({ a: String(a), b: String(b), order: 1 })) };
  }
  const expected = [named(1, []), named(2, []), named(3, []), named(4, []), named(5, []),
    named(5, [[2, 1]]), named(4, [[2, 1], [3, 1]]), named(6, [[3, 2], [2, 1], [5, 1]])];
  source.forEach((g, i) => {
    check(E.grade(g, expected[i]).correct, 'source agrees with independently name-built graph ' + c.molecules[i].id);
    const ids = new Map(g.nodes.map((n, j) => [n.id, 'reversed-' + (99 - j)]));
    const reverse = { nodes: g.nodes.slice().reverse().map(n => ({ id: ids.get(n.id), hydrogens: n.hydrogens, x: -500, y: 999 })),
      bonds: g.bonds.slice().reverse().map(b => ({ a: ids.get(b.b), b: ids.get(b.a), order: b.order })) };
    check(E.grade(reverse, g).correct, 'ID/order/bond orientation/position invariance ' + i);
    source.forEach((other, j) => check(E.grade(g, other).correct === (i === j), 'pair ' + i + '/' + j));
  });
  const isomer = named(5, [[3, 1]]);
  const labels = g => g.nodes.map(n => n.hydrogens).sort().join(',');
  check(labels(isomer) === labels(expected[5]), 'wrong isomer has identical CHn counts');
  check(!E.grade(isomer, source[5]).correct, 'same formula/counts wrong branch position rejected');
  const copy = g => JSON.parse(JSON.stringify(g));
  const bad = [];
  let g = copy(source[1]); g.bonds = []; bad.push(['disconnected', g]);
  g = copy(source[2]); g.bonds.push({ a: g.nodes[0].id, b: g.nodes[2].id, order: 1 }); g.nodes.forEach(n => { n.hydrogens = 2; }); bad.push(['cycle', g]);
  g = copy(source[1]); g.nodes[0].hydrogens = 4; bad.push(['CH4 connected', g]);
  g = copy(source[1]); g.nodes[0].hydrogens = 2; bad.push(['wrong fixed H', g]);
  g = copy(source[1]); g.bonds[0].order = 2; bad.push(['double bond', g]);
  g = copy(source[1]); g.bonds.push({ ...g.bonds[0] }); bad.push(['duplicate bond', g]);
  g = copy(source[1]); g.bonds[0].b = g.bonds[0].a; bad.push(['self edge', g]);
  g = copy(source[1]); g.nodes[1].id = g.nodes[0].id; bad.push(['duplicate node IDs', g]);
  g = { nodes: [], bonds: [] }; bad.push(['empty', g]);
  g = named(33, []); bad.push(['bounded graph', g]);
  bad.forEach(([why, invalid]) => check(!E.validate(invalid).valid && !E.grade(invalid, source[0]).correct, why + ' rejected'));
  return JSON.stringify(report);
}());
