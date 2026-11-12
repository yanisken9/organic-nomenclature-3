(function (root) {
  'use strict';

  // A candidate is a carbon tree. Coordinates belong to the presentation layer;
  // fixed CHn labels and carbon-to-carbon adjacency alone determine its identity.
  var MAX_NODES = 32;
  var MAX_SOURCE_ATOMS = MAX_NODES * 5;

  function result(valid, code, message) {
    return { valid: valid, code: code, message: message };
  }

  function fail(code, message) {
    return result(false, code, message);
  }

  function inspect(graph) {
    if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.bonds)) {
      return { error: fail('malformed', 'Η κατασκευή δεν μπορεί να ελεγχθεί. Δοκίμασε ξανά.') };
    }
    if (!graph.nodes.length) {
      return { error: fail('empty', 'Πρόσθεσε πρώτα τα κομμάτια του μορίου.') };
    }
    if (graph.nodes.length > MAX_NODES || graph.bonds.length > MAX_NODES * 2) {
      return { error: fail('limit', 'Η κατασκευή έχει υπερβολικά πολλά κομμάτια. Αφαίρεσε όσα δεν χρειάζονται.') };
    }

    var byId = new Map();
    var neighbours = new Map();
    for (var i = 0; i < graph.nodes.length; i += 1) {
      var node = graph.nodes[i];
      if (!node || typeof node.id !== 'string' || !node.id.length || node.id.length > 128 ||
          !Number.isInteger(node.hydrogens) || node.hydrogens < 0 || node.hydrogens > 4) {
        return { error: fail('node', 'Κάποιο κομμάτι δεν είναι έγκυρη ομάδα CH₄, CH₃, CH₂, CH ή C.') };
      }
      if (byId.has(node.id)) {
        return { error: fail('duplicate-node', 'Δύο κομμάτια έχουν το ίδιο αναγνωριστικό. Δοκίμασε ξανά.') };
      }
      byId.set(node.id, node);
      neighbours.set(node.id, []);
    }

    var seen = new Set();
    for (var j = 0; j < graph.bonds.length; j += 1) {
      var bond = graph.bonds[j];
      if (!bond || typeof bond.a !== 'string' || typeof bond.b !== 'string' ||
          !byId.has(bond.a) || !byId.has(bond.b)) {
        return { error: fail('bond-endpoint', 'Κάποιος δεσμός δεν συνδέει δύο υπάρχοντα κομμάτια.') };
      }
      if (bond.a === bond.b) {
        return { error: fail('self-bond', 'Ένας δεσμός χρειάζεται δύο διαφορετικά άτομα C.') };
      }
      if (bond.order !== 1) {
        return { error: fail('bond-order', 'Στα αλκάνια χρησιμοποιούμε μόνο απλούς δεσμούς μεταξύ ατόμων C.') };
      }
      var key = JSON.stringify(bond.a < bond.b ? [bond.a, bond.b] : [bond.b, bond.a]);
      if (seen.has(key)) {
        return { error: fail('duplicate-bond', 'Ανάμεσα στα ίδια δύο άτομα C υπάρχει ήδη δεσμός.') };
      }
      seen.add(key);
      neighbours.get(bond.a).push(bond.b);
      neighbours.get(bond.b).push(bond.a);
    }

    // Diagnose impossible valence immediately, including an attached CH4 group.
    for (var k = 0; k < graph.nodes.length; k += 1) {
      var current = graph.nodes[k];
      if (current.hydrogens + neighbours.get(current.id).length > 4) {
        return { error: fail('overvalence', 'Κάποιο άτομο C έχει περισσότερους από τέσσερις δεσμούς. Έλεγξε τις ομάδες και τις συνδέσεις τους.') };
      }
    }

    var visited = new Set();
    var pending = [graph.nodes[0].id];
    while (pending.length) {
      var id = pending.pop();
      if (visited.has(id)) continue;
      visited.add(id);
      neighbours.get(id).forEach(function (other) {
        if (!visited.has(other)) pending.push(other);
      });
    }
    if (visited.size !== graph.nodes.length) {
      return { error: fail('disconnected', 'Υπάρχουν κομμάτια που δεν συνδέονται με την υπόλοιπη δομή.') };
    }
    if (graph.bonds.length !== graph.nodes.length - 1) {
      return { error: fail('cycle', 'Η κατασκευή σχηματίζει δακτύλιο. Εδώ χτίζουμε αλκάνια με ανοικτή αλυσίδα.') };
    }
    for (var n = 0; n < graph.nodes.length; n += 1) {
      var atom = graph.nodes[n];
      if (atom.hydrogens + neighbours.get(atom.id).length !== 4) {
        return { error: fail('hydrogens', 'Οι ομάδες CH₄, CH₃, CH₂, CH και C πρέπει να συμφωνούν με τους δεσμούς τους. Κάθε άτομο C σχηματίζει συνολικά τέσσερις δεσμούς.') };
      }
    }
    return { byId: byId, neighbours: neighbours };
  }

  function validate(graph) {
    var checked = inspect(graph);
    return checked.error || result(true, 'valid', 'Η κατασκευή είναι έγκυρο αλκάνιο ανοικτής αλυσίδας.');
  }

  function canonical(graph) {
    var checked = inspect(graph);
    if (checked.error) {
      var error = new Error(checked.error.message);
      error.code = checked.error.code;
      throw error;
    }
    // Exact rooted-tree encodings are compared for every possible root. At the
    // bounded size of 32 nodes this is small, and avoids relying on a count or
    // degree signature that would conflate distinct constitutional isomers.
    function encode(id, parent) {
      var children = checked.neighbours.get(id).filter(function (child) {
        return child !== parent;
      }).map(function (child) {
        return encode(child, id);
      }).sort();
      return '(' + checked.byId.get(id).hydrogens + ':' + children.join('') + ')';
    }
    return graph.nodes.map(function (node) { return encode(node.id, null); }).sort()[0];
  }

  function grade(candidate, target) {
    var expected = validate(target);
    if (!expected.valid) {
      return { correct: false, code: 'target-invalid', message: 'Το μόριο της άσκησης δεν μπορεί να ελεγχθεί. Διάλεξε άλλο μόριο.' };
    }
    var checked = validate(candidate);
    if (!checked.valid) {
      return { correct: false, code: checked.code, message: checked.message };
    }
    if (canonical(candidate) === canonical(target)) {
      return { correct: true, code: 'correct', message: 'Σωστά! Η δομή που κατασκεύασες αντιστοιχεί στο όνομα.' };
    }
    return {
      correct: false,
      code: 'mismatch',
      message: 'Η δομή σου δεν αντιστοιχεί ακόμη στο όνομα. Έλεγξε την κύρια αλυσίδα και τις θέσεις των διακλαδώσεων και δοκίμασε ξανά.'
    };
  }

  function sourceError(message) {
    var error = new Error(message);
    error.code = 'source-mol';
    return error;
  }

  function integerField(line, start, length, required) {
    var raw = line.slice(start, start + length).trim();
    if (!raw && !required) return 0;
    if (!/^\d+$/.test(raw)) throw sourceError('Μη έγκυρο αριθμητικό πεδίο στο MOL.');
    return Number(raw);
  }

  function parseMol(mol) {
    if (typeof mol !== 'string' || mol.length > 100000) {
      throw sourceError('Δεν δόθηκε έγκυρο αρχείο MOL.');
    }
    var lines = mol.replace(/\r\n?/g, '\n').split('\n');
    if (lines.length < 5 || !/V2000\s*$/.test(lines[3])) {
      throw sourceError('Απαιτείται αρχείο MOL V2000.');
    }
    var atomCount = integerField(lines[3], 0, 3, true);
    var bondCount = integerField(lines[3], 3, 3, true);
    if (!atomCount || atomCount > MAX_SOURCE_ATOMS || bondCount > MAX_SOURCE_ATOMS * 2 ||
        lines.length < 4 + atomCount + bondCount + 1) {
      throw sourceError('Το μέγεθος ή οι εγγραφές του MOL δεν είναι έγκυρα.');
    }
    var atoms = [];
    for (var i = 0; i < atomCount; i += 1) {
      var line = lines[4 + i];
      var symbol = line.slice(31, 34).trim();
      var coordinates = [line.slice(0, 10), line.slice(10, 20), line.slice(20, 30)];
      if ((symbol !== 'C' && symbol !== 'H') || coordinates.some(function (value) {
        return !value.trim() || !Number.isFinite(Number(value));
      })) {
        throw sourceError('Το MOL πρέπει να περιέχει μόνο άτομα C και H με έγκυρες συντεταγμένες.');
      }
      // This catalog uses explicit hydrogens and neutral, non-isotopic atoms.
      // Reject charge/radical, isotope and implicit-H query fields rather than
      // silently turning a chemically different source into a saturated tree.
      if (line.slice(34, 36).trim() && Number(line.slice(34, 36)) !== 0) {
        throw sourceError('Δεν υποστηρίζονται ισοτοπικές εγγραφές στο MOL.');
      }
      if (integerField(line, 36, 3, false) !== 0 || integerField(line, 42, 3, false) !== 0) {
        throw sourceError('Απαιτούνται ουδέτερα άτομα με ρητά άτομα H στο MOL.');
      }
      atoms.push({ symbol: symbol, neighbours: [] });
    }
    var sourceBonds = new Set();
    for (var j = 0; j < bondCount; j += 1) {
      var bondLine = lines[4 + atomCount + j];
      var a = integerField(bondLine, 0, 3, true) - 1;
      var b = integerField(bondLine, 3, 3, true) - 1;
      var order = integerField(bondLine, 6, 3, true);
      if (a < 0 || b < 0 || a >= atomCount || b >= atomCount || a === b || order !== 1) {
        throw sourceError('Το MOL περιέχει μη έγκυρο ή μη απλό δεσμό.');
      }
      var key = a < b ? a + ':' + b : b + ':' + a;
      if (sourceBonds.has(key)) throw sourceError('Το MOL περιέχει διπλή εγγραφή δεσμού.');
      sourceBonds.add(key);
      atoms[a].neighbours.push(b);
      atoms[b].neighbours.push(a);
    }
    var endIndex = 4 + atomCount + bondCount;
    if (lines[endIndex].trim() !== 'M  END') {
      throw sourceError('Το MOL περιέχει πρόσθετες χημικές ιδιότητες που δεν υποστηρίζονται.');
    }
    // One structure only: do not quietly grade the first record of an SDF.
    if (lines.slice(endIndex + 1).some(function (line) {
      return line.trim() && line.trim() !== '$$$$';
    })) {
      throw sourceError('Απαιτείται μία μόνο δομή MOL χωρίς πρόσθετες εγγραφές.');
    }

    var graph = { nodes: [], bonds: [] };
    atoms.forEach(function (atom, index) {
      if (atom.symbol === 'H') {
        if (atom.neighbours.length !== 1 || atoms[atom.neighbours[0]].symbol !== 'C') {
          throw sourceError('Κάθε άτομο H πρέπει να συνδέεται με ένα άτομο C.');
        }
        return;
      }
      if (atom.neighbours.length !== 4) {
        throw sourceError('Κάθε άτομο C στο MOL πρέπει να έχει τέσσερις ρητούς απλούς δεσμούς.');
      }
      var hydrogens = atom.neighbours.filter(function (other) { return atoms[other].symbol === 'H'; }).length;
      graph.nodes.push({ id: 'c' + (index + 1), hydrogens: hydrogens });
      atom.neighbours.forEach(function (other) {
        if (other > index && atoms[other].symbol === 'C') {
          graph.bonds.push({ a: 'c' + (index + 1), b: 'c' + (other + 1), order: 1 });
        }
      });
    });
    var checked = validate(graph);
    if (!checked.valid) throw sourceError(checked.message);
    return graph;
  }

  root.NameleculeMolecularPuzzleEngine = Object.freeze({
    MAX_NODES: MAX_NODES,
    parseMol: parseMol,
    validate: validate,
    grade: grade,
    canonical: canonical
  });
}(typeof globalThis !== 'undefined' ? globalThis : this));
