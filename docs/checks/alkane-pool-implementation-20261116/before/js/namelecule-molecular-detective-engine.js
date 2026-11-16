(function (root) {
  'use strict';

  // This first pool is deliberately bounded. Targets are derived from the live
  // expanded graph; these profiles validate its identity, never prescribe IDs.
  var starterIds = Object.freeze([
    'ethane', 'butane', 'methyl_2_pentane', 'dimethyl_2_3_butane',
    'ethene', 'butene_1', 'butene_2', 'butyne_1', 'butyne_2',
    'butadiene_1_2', 'butadiene_1_3', 'ethanol', 'butanol_2',
    'propanal', 'propanone', 'pentanone_3', 'methanoicacid'
  ]);
  var profiles = {
    ethane: profile('CC', [[1, 2, 1]], 2),
    butane: profile('CCCC', [[1, 2, 1], [2, 3, 1], [3, 4, 1]], 4),
    methyl_2_pentane: profile('CCCCCC', [[1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 5, 1], [2, 6, 1]], 5, 1),
    dimethyl_2_3_butane: profile('CCCCCC', [[1, 2, 1], [2, 3, 1], [3, 4, 1], [2, 5, 1], [3, 6, 1]], 4, 2),
    ethene: profile('CC', [[1, 2, 2]], 2, 0, 2),
    butene_1: profile('CCCC', [[1, 2, 2], [2, 3, 1], [3, 4, 1]], 4, 0, 2),
    butene_2: profile('CCCC', [[1, 2, 1], [2, 3, 2], [3, 4, 1]], 4, 0, 2),
    butyne_1: profile('CCCC', [[1, 2, 3], [2, 3, 1], [3, 4, 1]], 4, 0, 3),
    butyne_2: profile('CCCC', [[1, 2, 1], [2, 3, 3], [3, 4, 1]], 4, 0, 3),
    butadiene_1_2: profile('CCCC', [[1, 2, 2], [2, 3, 2], [3, 4, 1]], 4, 0, 2),
    butadiene_1_3: profile('CCCC', [[1, 2, 2], [2, 3, 1], [3, 4, 2]], 4, 0, 2),
    ethanol: profile('CCO', [[1, 2, 1], [2, 3, 1]], 2, 0, 1, 'hydroxyl'),
    butanol_2: profile('CCCCO', [[1, 2, 1], [2, 3, 1], [3, 4, 1], [2, 5, 1]], 4, 0, 1, 'hydroxyl'),
    propanal: profile('CCCO', [[1, 2, 1], [2, 3, 1], [1, 4, 2]], 3, 0, 1, 'aldehyde'),
    propanone: profile('CCCO', [[1, 2, 1], [2, 3, 1], [2, 4, 2]], 3, 0, 1, 'carbonyl'),
    pentanone_3: profile('CCCCCO', [[1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 5, 1], [3, 6, 2]], 5, 0, 1, 'carbonyl'),
    methanoicacid: profile('COO', [[1, 2, 2], [1, 3, 1]], 1, 0, 1, 'carboxyl')
  };

  function profile(elements, edges, parentLength, branches, order, group) {
    var atoms = elements.split('').map(function (element, i) { return { id: i + 1, element: element }; });
    var bonds = edges.map(function (edge, i) { return { id: i + 1, a: edge[0], b: edge[1], order: edge[2] }; });
    return { signature: signature(atoms, bonds), parentLength: parentLength,
      branches: branches || 0, order: order || 1, group: group || null };
  }

  function error(code, message) {
    var problem = new Error(message);
    problem.code = code;
    return problem;
  }

  function idValid(id) { return Number.isSafeInteger(id) && id > 0; }
  function sorted(ids) { return ids.slice().sort(function (a, b) { return a - b; }); }
  function textKey(text) {
    return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[\s\-–—]/g, '');
  }

  function adjacency(atoms, bonds) {
    var adj = new Map();
    atoms.forEach(function (atom) { adj.set(atom.id, []); });
    bonds.forEach(function (bond) {
      adj.get(bond.a).push({ id: bond.b, order: bond.order });
      adj.get(bond.b).push({ id: bond.a, order: bond.order });
    });
    return adj;
  }

  // Exact rooted-tree encoding, independent of atom/bond numbering and layout.
  // Called only with the known tree profiles or after graph validation.
  function signature(atoms, bonds) {
    var heavy = atoms.filter(function (atom) { return atom.element !== 'H'; });
    var byId = new Map(heavy.map(function (atom) { return [atom.id, atom]; }));
    var adj = adjacency(heavy, bonds.filter(function (bond) { return byId.has(bond.a) && byId.has(bond.b); }));
    function encode(id, parent) {
      return byId.get(id).element + '(' + adj.get(id).filter(function (next) {
        return next.id !== parent;
      }).map(function (next) { return next.order + encode(next.id, id); }).sort().join('') + ')';
    }
    return heavy.map(function (atom) { return encode(atom.id, null); }).sort()[0];
  }

  function inspect(snapshot) {
    if (!snapshot || typeof snapshot !== 'object' || !Object.prototype.hasOwnProperty.call(profiles, snapshot.moleculeId)) {
      throw error('unsupported-molecule', 'Το μόριο δεν ανήκει στο αρχικό σύνολο των 17 μορίων.');
    }
    if (typeof snapshot.correctName !== 'string' || !snapshot.correctName.trim() || snapshot.correctName.length > 300 ||
        !Array.isArray(snapshot.pieces) || !snapshot.pieces.length || snapshot.pieces.length > 30 ||
        !Array.isArray(snapshot.atoms) || !snapshot.atoms.length || snapshot.atoms.length > 40 ||
        !Array.isArray(snapshot.bonds) || snapshot.bonds.length !== snapshot.atoms.length - 1) {
      throw error('snapshot-shape', 'Τα δεδομένα της αποστολής είναι ελλιπή.');
    }
    var pieceIds = new Set();
    snapshot.pieces.forEach(function (piece, i) {
      if (!piece || typeof piece.id !== 'string' || !piece.id || piece.id.length > 80 || pieceIds.has(piece.id) ||
          typeof piece.text !== 'string' || !piece.text.trim() || piece.text.length > 100 ||
          typeof piece.mode !== 'string' || typeof piece.separatorBefore !== 'string' ||
          !/^[ ]*$/.test(piece.separatorBefore) || (i === 0 && piece.separatorBefore !== '')) {
        throw error('name-pieces', 'Τα συνθετικά του ονόματος δεν είναι έγκυρα.');
      }
      pieceIds.add(piece.id);
    });
    if (snapshot.pieces.map(function (piece) { return piece.separatorBefore + piece.text; }).join('').normalize('NFC') !== snapshot.correctName.normalize('NFC')) {
      throw error('name-roundtrip', 'Τα συνθετικά δεν ανασυνθέτουν το όνομα του μορίου.');
    }
    var byId = new Map();
    snapshot.atoms.forEach(function (atom) {
      if (!atom || !idValid(atom.id) || byId.has(atom.id) || ['C', 'H', 'O'].indexOf(atom.element) < 0 ||
          (atom.charge != null && atom.charge !== 0) || (atom.isotope != null && atom.isotope !== 0)) {
        throw error('atom', 'Ο γράφος περιέχει μη έγκυρο ή μη υποστηριζόμενο άτομο.');
      }
      byId.set(atom.id, atom);
    });
    var bondIds = new Set(), edges = new Set(), valences = new Map();
    snapshot.atoms.forEach(function (atom) { valences.set(atom.id, 0); });
    snapshot.bonds.forEach(function (bond) {
      if (!bond || !idValid(bond.id) || bondIds.has(bond.id) || !byId.has(bond.a) || !byId.has(bond.b) ||
          bond.a === bond.b || [1, 2, 3].indexOf(bond.order) < 0) {
        throw error('bond', 'Ο γράφος περιέχει μη έγκυρο δεσμό.');
      }
      var edge = sorted([bond.a, bond.b]).join(':');
      if (edges.has(edge)) throw error('duplicate-edge', 'Ο ίδιος δεσμός καταγράφεται δύο φορές.');
      edges.add(edge);
      bondIds.add(bond.id);
      valences.set(bond.a, valences.get(bond.a) + bond.order);
      valences.set(bond.b, valences.get(bond.b) + bond.order);
    });
    snapshot.atoms.forEach(function (atom) {
      if (valences.get(atom.id) !== { C: 4, H: 1, O: 2 }[atom.element]) {
        throw error('expanded-valence', 'Απαιτείται πλήρης ανεπτυγμένος τύπος με ρητά άτομα H και σωστά σθένη.');
      }
    });
    var adj = adjacency(snapshot.atoms, snapshot.bonds), seen = new Set(), pending = [snapshot.atoms[0].id];
    while (pending.length) {
      var id = pending.pop();
      if (seen.has(id)) continue;
      seen.add(id);
      adj.get(id).forEach(function (next) { if (!seen.has(next.id)) pending.push(next.id); });
    }
    if (seen.size !== snapshot.atoms.length) throw error('disconnected', 'Ο μοριακός γράφος δεν είναι ενιαίος.');
    var chosen = profiles[snapshot.moleculeId];
    if (signature(snapshot.atoms, snapshot.bonds) !== chosen.signature) {
      throw error('molecule-identity', 'Ο γράφος δεν αντιστοιχεί στο επιλεγμένο μόριο.');
    }
    var series = { hydroxyl: 'alcohol', aldehyde: 'aldehyde', carbonyl: 'ketone', carboxyl: 'carboxylicAcid' }[chosen.group];
    var chemicalClass = { hydroxyl: 'alcohols', aldehyde: 'carbonylCompounds', carbonyl: 'carbonylCompounds', carboxyl: 'carboxylicAcids' }[chosen.group];
    if (!series) {
      var doubles = snapshot.bonds.filter(function (bond) { return bond.order === 2; }).length;
      series = chosen.order === 3 ? 'alkynes' : doubles > 1 ? 'alkadienes' : doubles ? 'alkenes' : 'alkanes';
      chemicalClass = 'hydrocarbons';
    }
    if (snapshot.series !== series || snapshot.chemicalClass !== chemicalClass) {
      throw error('classification', 'Η κατηγορία και η ομόλογη σειρά δεν συμφωνούν με τον μοριακό γράφο.');
    }
    return { byId: byId, adj: adj, profile: chosen };
  }

  function validateSnapshot(snapshot) {
    try { inspect(snapshot); return { valid: true, code: 'valid' }; }
    catch (problem) { return { valid: false, code: problem.code || 'snapshot-invalid', message: problem.message }; }
  }

  function uniqueSets(sets) {
    var seen = new Set();
    return sets.map(sorted).filter(function (ids) {
      var key = ids.join(',');
      if (!ids.length || seen.has(key)) return false;
      seen.add(key);
      return true;
    }).sort(function (a, b) { return a.join(',').localeCompare(b.join(',')); });
  }

  function parentSets(snapshot, graph) {
    var carbons = snapshot.atoms.filter(function (atom) { return atom.element === 'C'; }).map(function (atom) { return atom.id; });
    var paths = [], max = 0;
    function walk(path) {
      if (path.length > max) { max = path.length; paths = []; }
      if (path.length === max) paths.push(path);
      graph.adj.get(path[path.length - 1]).forEach(function (next) {
        if (graph.byId.get(next.id).element === 'C' && path.indexOf(next.id) < 0) walk(path.concat(next.id));
      });
    }
    carbons.forEach(function (id) { walk([id]); });
    if (max !== graph.profile.parentLength) throw error('parent-length', 'Δεν βρέθηκε η αναμενόμενη κύρια αλυσίδα.');
    // All longest carbon paths are valid in these two small branched alkanes.
    // Other pool members have an unbranched carbon skeleton, including their FG.
    return uniqueSets(paths);
  }

  function literalGroups(snapshot, graph) {
    var groups = { hydroxyl: [], aldehyde: [], carbonyl: [], carboxyl: [] };
    function neighbours(id, element, order) {
      return graph.adj.get(id).filter(function (next) {
        return graph.byId.get(next.id).element === element && next.order === order;
      }).map(function (next) { return next.id; });
    }
    snapshot.atoms.forEach(function (atom) {
      if (atom.element === 'O') {
        var oh = neighbours(atom.id, 'H', 1), oc = neighbours(atom.id, 'C', 1);
        if (oh.length === 1 && oc.length === 1) groups.hydroxyl.push([atom.id, oh[0]]);
      }
      if (atom.element !== 'C') return;
      var oxygen = neighbours(atom.id, 'O', 2), hydroxy = neighbours(atom.id, 'O', 1);
      if (oxygen.length !== 1) return;
      var hydrogens = neighbours(atom.id, 'H', 1), carbon = neighbours(atom.id, 'C', 1);
      if (hydroxy.length === 1) {
        var h = neighbours(hydroxy[0], 'H', 1);
        if (h.length === 1) groups.carboxyl.push([atom.id, oxygen[0], hydroxy[0], h[0]]);
      } else if (hydrogens.length === 1 && carbon.length === 1) {
        groups.aldehyde.push([atom.id, oxygen[0], hydrogens[0]]);
      } else if (carbon.length === 2) {
        groups.carbonyl.push([atom.id, oxygen[0]]);
      }
    });
    return groups;
  }

  function missions(snapshot) {
    var graph = inspect(snapshot), chosen = graph.profile, parents = parentSets(snapshot, graph);
    var carbonIds = snapshot.atoms.filter(function (atom) { return atom.element === 'C'; }).map(function (atom) { return atom.id; });
    var branches = uniqueSets(parents.map(function (parent) {
      return carbonIds.filter(function (id) { return parent.indexOf(id) < 0; });
    }));
    if (chosen.branches && branches.some(function (set) {
      return set.length !== chosen.branches || set.some(function (id) {
        return graph.adj.get(id).filter(function (next) { return graph.byId.get(next.id).element === 'C'; }).length !== 1;
      });
    })) throw error('branch-target', 'Οι διακλαδώσεις δεν είναι οι αναμενόμενες μεθυλομάδες.');
    var groups = literalGroups(snapshot, graph), output = [], families = new Set();
    var roots = { μεθ: 1, αιθ: 2, προπ: 3, βουτ: 4, πεντ: 5 };
    function add(piece, kind, family, accepted, prompt, explanation) {
      accepted = uniqueSets(accepted);
      if (!accepted.length || families.has(family)) throw error('mission-target', 'Δεν βρέθηκε μοναδικός μη κενός στόχος για το συνθετικό.');
      families.add(family);
      output.push({ id: snapshot.moleculeId + ':' + piece.id + ':' + family, pieceId: piece.id,
        kind: kind, family: family, prompt: prompt, explanation: explanation, accepted: accepted });
    }
    snapshot.pieces.forEach(function (piece) {
      var key = textKey(piece.text), rootMatch = /^(μεθ|αιθ|προπ|βουτ|πεντ)[αο]?$/.exec(key);
      if (piece.mode === 'compCarbonsCount' && rootMatch) {
        if (roots[rootMatch[1]] !== chosen.parentLength) throw error('root-text', 'Το συνθετικό δεν συμφωνεί με το πλήθος ατόμων C της κύριας αλυσίδας.');
        add(piece, 'atoms', 'parent-chain', parents,
          'Επίλεξε τα άτομα C της κύριας αλυσίδας που δηλώνει το τονισμένο συνθετικό.',
          'Το συνθετικό δηλώνει τα ' + chosen.parentLength + ' άτομα C της κύριας αλυσίδας. Η σειρά επιλογής τους δεν αλλάζει την απάντηση.');
        return;
      }
      if ((piece.mode === 'compBondType' || piece.mode === 'compBondType2') && /^(αν|εν|διεν|ιν)$/.test(key)) {
        var order = key === 'αν' ? 1 : key === 'ιν' ? 3 : 2;
        if (order !== chosen.order) throw error('bond-text', 'Το συνθετικό δεν συμφωνεί με τους δεσμούς του μορίου.');
        var targets = snapshot.bonds.filter(function (bond) {
          return bond.order === order && graph.byId.get(bond.a).element === 'C' && graph.byId.get(bond.b).element === 'C';
        }).map(function (bond) { return bond.id; });
        // Methanoic acid has no C-C edge: its -αν- is never an empty mission.
        if (!targets.length && order === 1 && chosen.group === 'carboxyl') return;
        if ((key === 'διεν' && targets.length !== 2) || (key === 'εν' && targets.length !== 1)) {
          throw error('bond-multiplier', 'Το συνθετικό δεν συμφωνεί με το πλήθος των πολλαπλών δεσμών.');
        }
        var label = { 1: 'απλούς', 2: 'διπλούς', 3: 'τριπλούς' }[order];
        add(piece, 'bonds', { 1: 'single-bonds', 2: 'double-bonds', 3: 'triple-bonds' }[order], [targets],
          'Επίλεξε όλους τους ' + label + ' δεσμούς μεταξύ ατόμων C που δηλώνει το τονισμένο συνθετικό.',
          'Το συνθετικό δηλώνει τους ' + label + ' δεσμούς μεταξύ ατόμων C. Επιλέγουμε τους ίδιους τους δεσμούς.');
        return;
      }
      if (/^comp(SecondSub[12]|BranchSub\d+)$/.test(piece.mode) && /^(μεθυλο|διμεθυλο)$/.test(key)) {
        if (chosen.branches !== (key === 'διμεθυλο' ? 2 : 1)) throw error('branch-text', 'Το συνθετικό δεν συμφωνεί με τις μεθυλομάδες του μορίου.');
        add(piece, 'atoms', 'branches', branches,
          'Επίλεξε τα άτομα C ' + (chosen.branches === 1 ? 'της μεθυλομάδας' : 'των δύο μεθυλομάδων') + ' που δηλώνει το τονισμένο συνθετικό.',
          'Κάθε μεθυλομάδα έχει ένα άτομο C έξω από την κύρια αλυσίδα. Τα άτομα H και το άτομο C της κύριας αλυσίδας δεν ανήκουν στην επιλογή.');
        return;
      }
      // Native alcohol suffixes may occupy slot 8 / compBondType2. Literal text
      // plus a validated functional graph, rather than a box number, identifies FG.
      var family = { ολη: 'hydroxyl', αλη: 'aldehyde', ονη: 'carbonyl', ικοοξυ: 'carboxyl' }[key];
      if (!family) return; // No locant, isolated multiplier, punctuation or -ιο task.
      if (family !== chosen.group || groups[family].length !== 1) throw error('functional-group', 'Η χαρακτηριστική ομάδα δεν συμφωνεί με το συνθετικό.');
      var words = {
        hydroxyl: ['της υδροξυλομάδας –OH', 'Η υδροξυλομάδα περιλαμβάνει το άτομο O και το άτομο H που συνδέεται μαζί του.'],
        aldehyde: ['της αλδεϋδομάδας –CHO', 'Η αλδεϋδομάδα περιλαμβάνει το άτομο C, το διπλά συνδεδεμένο άτομο O και το αλδεϋδικό άτομο H.'],
        carbonyl: ['της καρβονυλομάδας >C=O', 'Η καρβονυλομάδα περιλαμβάνει το άτομο C και το άτομο O του διπλού δεσμού. Τα γειτονικά άτομα C δεν ανήκουν στην ομάδα.'],
        carboxyl: ['της καρβοξυλομάδας –COOH', 'Η καρβοξυλομάδα περιλαμβάνει το άτομο C, τα δύο άτομα O και το άτομο H του –OH. Το άτομο H που συνδέεται απευθείας με το άτομο C μένει έξω.']
      }[family];
      add(piece, 'atoms', family, groups[family], 'Επίλεξε όλα τα άτομα ' + words[0] + ' που δηλώνει το τονισμένο συνθετικό.', words[1]);
    });
    var expected = 1 + (chosen.branches ? 1 : 0) + (chosen.group ? 1 : 0) + (carbonIds.length > 1 ? 1 : 0);
    if (output.length !== expected || !families.has('parent-chain') || (chosen.branches && !families.has('branches')) ||
        (chosen.group && !families.has(chosen.group))) {
      throw error('missing-mission', 'Δεν αναγνωρίστηκαν όλα τα αναμενόμενα συνθετικά του μορίου.');
    }
    return output;
  }

  function grade(mission, selection) {
    if (!mission || ['atoms', 'bonds'].indexOf(mission.kind) < 0 || !Array.isArray(mission.accepted) ||
        !mission.accepted.length || mission.accepted.some(function (set) { return !Array.isArray(set) || !set.length || set.some(function (id) { return !idValid(id); }); })) {
      throw error('invalid-mission', 'Η αποστολή δεν έχει έγκυρο στόχο.');
    }
    if (!selection || !Array.isArray(selection.atoms) || !Array.isArray(selection.bonds) ||
        selection.atoms.concat(selection.bonds).some(function (id) { return !idValid(id); })) {
      return { correct: false, kind: 'incorrect' };
    }
    if (!selection.atoms.length && !selection.bonds.length) return { correct: false, kind: 'empty' };
    var other = mission.kind === 'atoms' ? selection.bonds : selection.atoms;
    if (other.length) return { correct: false, kind: 'wrong-kind' };
    var actual = sorted(Array.from(new Set(selection[mission.kind])));
    var exact = mission.accepted.some(function (set) {
      var target = sorted(Array.from(new Set(set)));
      return target.length === actual.length && target.every(function (id, i) { return id === actual[i]; });
    });
    return { correct: exact, kind: exact ? 'exact' : 'incorrect' };
  }

  var api = Object.freeze({ starterIds: starterIds, missions: missions, grade: grade, validateSnapshot: validateSnapshot });
  root.NameleculeMolecularDetectiveEngine = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
