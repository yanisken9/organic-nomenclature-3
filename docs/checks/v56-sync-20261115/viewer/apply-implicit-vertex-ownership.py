from pathlib import Path
import hashlib
P=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate/js/mulermoc-nom-molview-56.js');s=P.read_text()
assert hashlib.sha256(P.read_bytes()).hexdigest()=='9a0d9561a93401744ac3189a05edf3b67222c3b29bf7e50cd2152c06dbd6e53d'
Path('docs/checks/v56-sync-20261115/viewer/bond-pick-before-vertex-ownership.js.txt').write_bytes(P.read_bytes())
s=s.replace('    var best = null, bd = Infinity, loose = null, ld = rAtom * rAtom;','    var best = null, bd = Infinity, loose = null, ld = rAtom * rAtom;\n    var visibleAnchorAtoms = {};',1)
s=s.replace('      var dx = anchor.x - px, dy = anchor.y - py, d2 = dx * dx + dy * dy;','      if (anchor.w > 0 && anchor.h > 0) visibleAnchorAtoms[anchor.atom] = true;\n      var dx = anchor.x - px, dy = anchor.y - py, d2 = dx * dx + dy * dy;',1)
needle='''    for (var v = 0; v < verts.length; v++) {
      var dx2 = verts[v].x - px, dy2 = verts[v].y - py, d22 = dx2 * dx2 + dy2 * dy2;
'''
replacement='''    for (var v = 0; v < verts.length; v++) {
      // A labeled atom is already represented by its visible glyph above.
      // Its raw bond endpoint must not add an implicit-atom halo over the
      // adjacent visible bond. Unlabeled skeletal atoms keep vertex picking.
      if (visibleAnchorAtoms[vAssign[v]]) continue;
      var dx2 = verts[v].x - px, dy2 = verts[v].y - py, d22 = dx2 * dx2 + dy2 * dy2;
'''
assert needle in s;s=s.replace(needle,replacement,1);P.write_text(s)
