/* One molecule per Worker: the unchanged core54 owns a fresh global scope.
 * No data54, lesson state, DOM, viewer or JSmol is loaded here. */
var selectedMol, mode2D, mainChainMode, jsmeNomeclatureApplet;

(function () {
  'use strict';
  var nlChemistryStarted = false;

  function nlChemistryError(code, message) {
    var error = new Error(message);
    error.code = code;
    return error;
  }

  function nlChemistryValidate(text) {
    if (typeof text !== 'string' || text.length > 100000) {
      throw nlChemistryError('INVALID_MOLECULE', 'Απαιτείται έγκυρος μοριακός τύπος V2000.');
    }
    var graph = fParseMolV2000(text);
    if (!graph || !graph.atoms.length || graph.atoms.length > 128) {
      throw nlChemistryError('INVALID_MOLECULE', 'Ο μοριακός τύπος δεν μπορεί να αναλυθεί.');
    }
    var lines = text.split(/\r?\n/);
    var counts = lines[3].slice(6).replace(/V2000\s*$/, '').trim().split(/\s+/);
    if (!/V2000\s*$/.test(lines[3]) || counts.some(function (n, i) {
      return !/^\d+$/.test(n) || (Number(n) !== 0 && !(i === counts.length - 1 && Number(n) === 999));
    })) throw nlChemistryError('UNSUPPORTED_MOLECULE', 'Δεν υποστηρίζονται πρόσθετα πεδία ή ερωτήματα MOL.');
    var carbonCount = 0;
    graph.atoms.forEach(function (atom, i) {
      if (atom.el === 'C') carbonCount++;
      var metadata = lines[4 + i].slice(34).trim();
      if (!['C', 'H'].includes(atom.el) || (metadata && !metadata.split(/\s+/).every(function (n) { return /^0+$/.test(n); }))) {
        throw nlChemistryError('UNSUPPORTED_MOLECULE', 'Ο πιλότος δέχεται μόνο ουδέτερα αλκάνια χωρίς πρόσθετα χαρακτηριστικά.');
      }
    });
    if (!carbonCount || carbonCount > 20) {
      throw nlChemistryError('UNSUPPORTED_MOLECULE', 'Το μόριο είναι εκτός των ορίων του πιλοτικού ελέγχου.');
    }
    var afterBonds = lines.slice(4 + graph.atoms.length + graph.bonds.length);
    var end = afterBonds.findIndex(function (line) { return /^M  END\s*$/.test(line); });
    if (end < 0 || afterBonds.slice(0, end).some(function (line) { return !!line.trim(); }) ||
        !/^\s*(?:\$\$\$\$\s*)?$/.test(afterBonds.slice(end + 1).join('\n'))) {
      throw nlChemistryError('UNSUPPORTED_MOLECULE', 'Δεν υποστηρίζονται ιδιότητες, ισότοπα ή πολλαπλές εγγραφές MOL.');
    }
    var adjacency = graph.atoms.map(function () { return []; });
    var edges = new Set();
    graph.bonds.forEach(function (bond, i) {
      var key = [Math.min(bond[0], bond[1]), Math.max(bond[0], bond[1])].join('-');
      var tail = lines[4 + graph.atoms.length + i].slice(9).trim();
      if (bond[2] !== 1 || edges.has(key) || (tail && !tail.split(/\s+/).every(function (n) { return /^0+$/.test(n); }))) {
        throw nlChemistryError('UNSUPPORTED_MOLECULE', 'Απαιτούνται απλοί δεσμοί χωρίς στερεοχημικά ή άλλα χαρακτηριστικά.');
      }
      edges.add(key);
      adjacency[bond[0] - 1].push(bond[1] - 1);
      adjacency[bond[1] - 1].push(bond[0] - 1);
    });
    graph.atoms.forEach(function (atom, i) {
      if ((atom.el === 'C' && adjacency[i].length > 4) ||
          (atom.el === 'H' && (adjacency[i].length !== 1 || graph.atoms[adjacency[i][0]].el !== 'C'))) {
        throw nlChemistryError('INVALID_MOLECULE', 'Το σθένος δεν αντιστοιχεί σε ουδέτερο αλκάνιο.');
      }
    });
    var visited = new Set([0]), stack = [0];
    while (stack.length) adjacency[stack.pop()].forEach(function (next) {
      if (!visited.has(next)) { visited.add(next); stack.push(next); }
    });
    if (visited.size !== graph.atoms.length || graph.bonds.length !== graph.atoms.length - 1) {
      throw nlChemistryError('UNSUPPORTED_MOLECULE', 'Απαιτείται ένα συνδεδεμένο άκυκλο αλκάνιο.');
    }
    return { graph: graph, carbonCount: carbonCount };
  }

  self.onmessage = function (event) {
    if (nlChemistryStarted) return;
    nlChemistryStarted = true;
    var request = event.data || {};
    try {
      if (request.type !== 'analyze' || typeof request.requestId !== 'string' ||
          !request.molecule || typeof request.molecule.id !== 'string' ||
          !/^[a-f0-9]{64}$/.test(request.engineSHA256 || '') ||
          typeof request.engineURL !== 'string') {
        throw nlChemistryError('INVALID_REQUEST', 'Η αίτηση ανάλυσης δεν είναι έγκυρη.');
      }
      var verifiedSourceURL = new URL(request.engineURL);
      if (verifiedSourceURL.protocol !== 'blob:' || verifiedSourceURL.origin !== self.location.origin) {
        throw nlChemistryError('INVALID_REQUEST', 'Η πηγή της χημικής μηχανής δεν είναι έγκυρη.');
      }
      // The client created this Blob from the exact bytes it hashed, never a
      // second network read. importScripts executes the unchanged core source.
      importScripts(verifiedSourceURL.href);
      var validated = nlChemistryValidate(request.molecule.mol);
      var graph = validated.graph;
      selectedMol = request.molecule.id;
      mode2D = 'expanded';
      mainChainMode = 'algorithmic';
      jsmeNomeclatureApplet = {
        totalNumberOfAtoms: function () { return graph.atoms.length; },
        totalNumberOfBonds: function () { return graph.bonds.length; },
        getAtom: function (_m, i) { return { label: graph.atoms[i - 1].el }; },
        getBond: function (_m, i) { return { atoms: graph.bonds[i - 1].slice(0, 2), order: graph.bonds[i - 1][2] }; },
        molFile: function () { return request.molecule.mol; }
      };
      fAnalyseStructure();
      fDetectMolType();
      fGuessName();
      var classification = fGetMoleculeClassification();
      if (classification.seriesKey !== 'alkanes' || typeof currentMolName !== 'string' ||
          !currentMolName || !Array.isArray(nameComponentsList) || nameComponentsList.length !== 12 ||
          !Array.isArray(mainChainAtomsList) || !mainChainAtomsList.length) {
        throw nlChemistryError('ANALYSIS_FAILED', 'Η χημική μηχανή δεν επέστρεψε πλήρη ανάλυση αλκανίου.');
      }
      self.postMessage({ type: 'result', requestId: request.requestId, result: {
        moleculeId: selectedMol,
        name: currentMolName,
        parts: nameComponentsList.slice(),
        rootVocabulary: nameMainCompList1.slice(),
        chain: mainChainAtomsList.slice(),
        branches: fGetHydrocarbonSubstituentInfo(),
        classification: classification,
        carbonCount: validated.carbonCount,
        engineSHA256: request.engineSHA256
      }});
    } catch (error) {
      self.postMessage({ type: 'error', requestId: request.requestId, error: {
        code: error.code || 'ENGINE_FAILED',
        message: error.message || 'Η χημική ανάλυση απέτυχε.'
      }});
    } finally {
      self.close();
    }
  };
}());
