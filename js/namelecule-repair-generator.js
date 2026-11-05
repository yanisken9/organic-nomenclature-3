/* Engine-backed alkane repair rounds. Pure generation: no network, DOM or saved answer tables. */
(function (global) {
  "use strict";

  const VERSION = "1.0.0";
  const WRONG_PART = "Αυτό το συνθετικό συμφωνεί με τη δομή.";
  const NEUTRAL_OBJECTIVE = "Ένα μέρος του ονόματος δεν συμφωνεί με τη δομή. Εντόπισέ το και επισκεύασέ το.";
  const MULTIPLIERS = ["", "", "δι", "τρι", "τετρα", "πεντα", "εξα"];
  const SLOT_LABELS = {
    0: "Θέσεις διακλαδώσεων", 1: "Είδος και πλήθος διακλαδώσεων",
    2: "Θέσεις διακλαδώσεων", 3: "Είδος και πλήθος διακλαδώσεων",
    5: "Μήκος κύριας αλυσίδας", 6: "Είδος δεσμών", 9: "Χημική τάξη"
  };

  function assert(condition, message) { if (!condition) throw new Error("Repair generator: " + message); }
  function nonempty(value) { return typeof value === "string" && value.trim().length > 0; }
  function hasValue(value) { return value !== null && value !== undefined && value !== ""; }
  function hash(value) {
    let result = 2166136261;
    for (let index = 0; index < value.length; index += 1) {
      result ^= value.charCodeAt(index);
      result = Math.imul(result, 16777619);
    }
    return result >>> 0;
  }
  function normalizeSeed(value) {
    if (value === undefined) return "0";
    assert((typeof value === "string" && value.length > 0 && value.length <= 128) ||
      (Number.isSafeInteger(value) && value >= 0), "Invalid seed");
    return String(value);
  }
  function randomSource(seed) {
    let state = hash(seed);
    return function () {
      state += 0x6D2B79F5;
      let value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }
  function shuffle(values, random) {
    const result = values.slice();
    for (let index = result.length - 1; index > 0; index -= 1) {
      const destination = Math.floor(random() * (index + 1));
      const value = result[index];
      result[index] = result[destination];
      result[destination] = value;
    }
    return result;
  }
  function joined(parts) { return parts.filter(hasValue).join(""); }
  function localAsset(value) {
    return nonempty(value) && /^assets\/[a-zA-Z0-9_/-]+\.svg$/.test(value) && !value.includes("..");
  }
  function locantsText(values, slot) { return (slot === 2 ? "-" : "") + values.join(",") + "-"; }

  // Check the engine's indexing contract against the supplied structure before
  // using branch locations/counts to construct a misconception. Core still owns
  // selection and numbering of the longest parent chain and the correct name.
  function checkedGraph(molecule, analysis) {
    const lines = molecule.mol.split(/\r?\n/);
    const atomCount = Number((lines[3] || "").slice(0, 3));
    const bondCount = Number((lines[3] || "").slice(3, 6));
    assert(Number.isInteger(atomCount) && atomCount > 0 && Number.isInteger(bondCount) && bondCount >= 0,
      "Invalid MOL counts for " + molecule.id);
    const types = lines.slice(4, 4 + atomCount).map(function (line) { return line.slice(31, 34).trim(); });
    assert(types.length === atomCount && types.every(function (type) { return type === "C" || type === "H"; }),
      "Expected an alkane structure for " + molecule.id);
    const carbons = types.map(function (type, index) { return type === "C" ? index : -1; }).filter(function (index) { return index >= 0; });
    const neighbors = types.map(function () { return []; });
    let carbonBonds = 0;
    assert(lines.length >= 4 + atomCount + bondCount, "Incomplete MOL for " + molecule.id);
    lines.slice(4 + atomCount, 4 + atomCount + bondCount).forEach(function (line) {
      const a = Number(line.slice(0, 3)) - 1;
      const b = Number(line.slice(3, 6)) - 1;
      const order = Number(line.slice(6, 9));
      assert(Number.isInteger(a) && Number.isInteger(b) && a >= 0 && b >= 0 && a < atomCount && b < atomCount &&
        a !== b && order === 1 && !neighbors[a].includes(b), "Expected unique single bonds for " + molecule.id);
      neighbors[a].push(b);
      neighbors[b].push(a);
      if (types[a] === "C" && types[b] === "C") carbonBonds += 1;
    });
    assert(carbons.length === analysis.carbonCount && carbonBonds === carbons.length - 1,
      "Carbon count/acyclic graph mismatch for " + molecule.id);
    assert(types.every(function (type, index) { return neighbors[index].length <= (type === "C" ? 4 : 1); }),
      "Invalid alkane valence for " + molecule.id);
    const reached = new Set();
    function visit(atom) {
      if (reached.has(atom)) return;
      reached.add(atom);
      neighbors[atom].forEach(visit);
    }
    visit(carbons[0]);
    assert(reached.size === atomCount, "Disconnected structure for " + molecule.id);
    const parent = analysis.chain.map(function (atom) { return atom - 1; });
    assert(parent.length > 0 && new Set(parent).size === parent.length && parent.every(function (atom, index) {
      return Number.isInteger(atom) && types[atom] === "C" && (index === 0 || neighbors[parent[index - 1]].includes(atom));
    }), "Invalid engine parent chain for " + molecule.id);
    const covered = new Set(parent);
    analysis.branches.forEach(function (branch) {
      assert(branch && Number.isInteger(branch.locant) && branch.locant > 0 && branch.locant <= parent.length &&
        Number.isInteger(branch.length) && branch.length > 0 && nonempty(branch.name) && nonempty(branch.signature) &&
        Array.isArray(branch.atoms) && branch.atoms.length === branch.length &&
        branch.atoms.includes(branch.attach) && neighbors[parent[branch.locant - 1]].includes(branch.attach),
      "Invalid engine branch attachment for " + molecule.id);
      branch.atoms.forEach(function (atom) {
        assert(Number.isInteger(atom) && types[atom] === "C" && !covered.has(atom), "Invalid engine branch atoms for " + molecule.id);
        covered.add(atom);
      });
      const connected = new Set();
      function visitBranch(atom) {
        if (connected.has(atom) || !branch.atoms.includes(atom)) return;
        connected.add(atom);
        neighbors[atom].forEach(visitBranch);
      }
      visitBranch(branch.attach);
      assert(connected.size === branch.length && branch.atoms.every(function (atom) {
        return neighbors[atom].filter(function (neighbor) { return parent.includes(neighbor); }).every(function (neighbor) {
          return atom === branch.attach && neighbor === parent[branch.locant - 1];
        });
      }), "Invalid engine branch graph for " + molecule.id);
    });
    assert(covered.size === carbons.length, "Incomplete engine carbon coverage for " + molecule.id);
  }

  function checkedAnalysis(molecule, analysis) {
    assert(analysis && analysis.moleculeId === molecule.id && nonempty(analysis.name), "Missing engine result for " + molecule.id);
    assert(Array.isArray(analysis.parts) && analysis.parts.length === 12 && analysis.parts.every(function (part) {
      return part === null || part === undefined || typeof part === "string";
    }) && joined(analysis.parts) === analysis.name, "Engine name/components mismatch for " + molecule.id);
    assert(analysis.classification && analysis.classification.seriesKey === "alkanes" &&
      Number.isInteger(analysis.carbonCount) && analysis.carbonCount > 0 &&
      Array.isArray(analysis.chain) && Array.isArray(analysis.branches), "Expected alkane engine result for " + molecule.id);
    assert(Array.isArray(analysis.rootVocabulary) && analysis.rootVocabulary.length >= 3 &&
      analysis.rootVocabulary.every(nonempty) && new Set(analysis.rootVocabulary).size === analysis.rootVocabulary.length &&
      analysis.rootVocabulary[analysis.chain.length - 1] === analysis.parts[5], "Invalid engine root vocabulary for " + molecule.id);
    const activeSlots = analysis.parts.map(function (value, slot) { return hasValue(value) ? slot : -1; }).filter(function (slot) { return slot >= 0; });
    assert(activeSlots.every(function (slot) { return Object.prototype.hasOwnProperty.call(SLOT_LABELS, slot); }) &&
      [5, 6, 9].every(function (slot) { return nonempty(analysis.parts[slot]); }), "Unsupported alkane components for " + molecule.id);
    checkedGraph(molecule, analysis);
    const groups = [];
    [0, 2].forEach(function (slot) {
      if (!hasValue(analysis.parts[slot]) && !hasValue(analysis.parts[slot + 1])) return;
      assert(nonempty(analysis.parts[slot]) && nonempty(analysis.parts[slot + 1]), "Incomplete branch group for " + molecule.id);
      const match = analysis.parts[slot].match(slot === 0 ? /^(\d+(?:,\d+)*)-$/ : /^-(\d+(?:,\d+)*)-$/);
      assert(match, "Unsupported locant component for " + molecule.id);
      const locants = match[1].split(",").map(Number);
      const possible = analysis.branches.filter(function (branch) {
        return analysis.parts[slot + 1].endsWith(branch.name);
      });
      const names = Array.from(new Set(possible.map(function (branch) { return branch.name; })));
      assert(names.length === 1, "Ambiguous engine branch group for " + molecule.id);
      const members = possible.filter(function (branch) { return branch.name === names[0]; });
      assert(members.length === locants.length && JSON.stringify(members.map(function (branch) { return branch.locant; }).sort(function (a, b) { return a - b; })) ===
        JSON.stringify(locants), "Engine branch locants mismatch for " + molecule.id);
      assert(new Set(members.map(function (branch) { return branch.signature; })).size === 1,
        "Unsupported mixed branch group for " + molecule.id);
      groups.push({ slot: slot, text: analysis.parts[slot + 1], base: names[0], locants: locants, members: members });
    });
    assert(groups.reduce(function (sum, group) { return sum + group.members.length; }, 0) === analysis.branches.length,
      "Incomplete branch components for " + molecule.id);
    return { molecule: molecule, analysis: analysis, groups: groups };
  }

  function nameParts(analysis) {
    return analysis.parts.map(function (value, slot) {
      return hasValue(value) ? { id: "component-" + slot, text: value, label: SLOT_LABELS[slot] } : null;
    }).filter(Boolean);
  }
  function feedback(kind) {
    return {
      wrongPart: WRONG_PART,
      unchanged: kind === "order" ? "Μετακίνησε μια ομάδα πριν ελέγξεις την επισκευή." : "Διάλεξε μια αντικατάσταση πριν ελέγξεις την επισκευή.",
      incorrect: "Η επισκευή δεν συμφωνεί ακόμη με τη δομή. Δοκίμασε ξανά."
    };
  }
  function roundBase(record, family, signature, objective, difficulty, successText) {
    return {
      id: "engine-" + record.molecule.id + "-" + family + "-" + hash(signature).toString(16),
      guided: false, title: "Επισκευή ονόματος",
      objective: difficulty === "basic" ? objective : NEUTRAL_OBJECTIVE,
      moleculeId: record.molecule.id, asset: record.molecule.asset,
      diagramAlt: "Ανεπτυγμένος συντακτικός τύπος αλκανίου. Τα άτομα και οι δεσμοί φαίνονται στο διάγραμμα.",
      correctName: record.analysis.name, successText: successText + " Σωστό όνομα: " + record.analysis.name + ".",
      fault: { kind: family, signature: record.molecule.id + ":" + signature }
    };
  }
  function replacement(record, family, slot, wrongValue, values, objective, successText, difficulty) {
    const correctValue = record.analysis.parts[slot];
    assert(wrongValue !== correctValue && new Set(values).size === values.length && values.includes(correctValue), "Invalid generated replacement");
    const result = roundBase(record, family, family + ":" + slot + ":" + wrongValue, objective, difficulty, successText);
    result.kind = "replace";
    result.parts = nameParts(record.analysis).map(function (part) {
      return part.id === "component-" + slot ? { id: part.id, text: wrongValue, label: part.label } : part;
    });
    result.targetPartId = "component-" + slot;
    result.correctValue = correctValue;
    result.choices = values.map(function (value) { return { value: value, label: value }; });
    result.feedback = feedback("replace");
    return result;
  }
  function candidates(record, rootVocabulary, difficulty) {
    const analysis = record.analysis;
    const parentLength = analysis.chain.length;
    const rounds = [];
    const largestLocant = analysis.branches.reduce(function (largest, branch) { return Math.max(largest, branch.locant); }, 0);
    const otherRoots = rootVocabulary.filter(function (entry) {
      // A wrong length must still leave every branch locant inside its proposed
      // parent: do not create a second fault such as position 5 on methane.
      return entry.value !== analysis.parts[5] && entry.count > largestLocant;
    }).sort(function (a, b) {
      // Total-carbon confusion is useful only when it is actually different from
      // the engine's numbered parent; otherwise use adjacent length vocabulary.
      if (analysis.carbonCount !== parentLength && (a.count === analysis.carbonCount) !== (b.count === analysis.carbonCount)) {
        return a.count === analysis.carbonCount ? -1 : 1;
      }
      return Math.abs(a.count - parentLength) - Math.abs(b.count - parentLength) || a.count - b.count;
    });
    assert(otherRoots.length >= 2, "Need three distinct engine-derived parent roots");
    otherRoots.forEach(function (wrongRoot, index) {
      const second = otherRoots[(index + 1) % otherRoots.length];
      const fact = analysis.branches.length ? "Το μόριο έχει " + analysis.carbonCount + " άνθρακες συνολικά, αλλά η κύρια αλυσίδα έχει " + parentLength + "." :
        "Η συνεχής κύρια αλυσίδα έχει " + parentLength + " άτομα άνθρακα.";
      rounds.push(replacement(record, "parent-length", 5, wrongRoot.value, [analysis.parts[5], wrongRoot.value, second.value],
        "Έλεγξε το μήκος της κύριας αλυσίδας και το συνθετικό που το δηλώνει.",
        fact + " Το συνθετικό «" + analysis.parts[5] + "» περιγράφει το μήκος της κύριας αλυσίδας.", difficulty));
    });
    // C1 has no C–C bond. C4+ unsaturation would also require a locant,
    // so it cannot be introduced as a single independent component error.
    if (analysis.branches.length === 0 && parentLength >= 2 && parentLength <= 3 && analysis.parts[6] === "άν") {
      ["έν", "ίν"].forEach(function (wrongValue) {
        rounds.push(replacement(record, "bond-type", 6, wrongValue, [analysis.parts[6], "έν", "ίν"],
          "Έλεγξε το είδος των δεσμών ανάμεσα στα άτομα άνθρακα.",
          "Οι δεσμοί ανάμεσα στα " + parentLength + " άτομα άνθρακα είναι απλοί. Γι’ αυτό χρησιμοποιούμε το συνθετικό «" + analysis.parts[6] + "».", difficulty));
      });
    }
    record.groups.forEach(function (group) {
      const alternatives = new Map();
      const occupancy = {};
      analysis.branches.forEach(function (branch) { occupancy[branch.locant] = (occupancy[branch.locant] || 0) + 1; });
      group.locants.forEach(function (current, index) {
        for (let next = 2; next < parentLength; next += 1) {
          if (next === current || (occupancy[next] || 0) >= 2) continue;
          const changed = group.locants.slice();
          changed[index] = next;
          changed.sort(function (a, b) { return a - b; });
          const value = locantsText(changed, group.slot);
          if (value !== analysis.parts[group.slot]) alternatives.set(value, changed);
        }
      });
      // Reversing a symmetric locant set is the same answer, never a fault.
      const reverse = group.locants.map(function (locant) { return parentLength + 1 - locant; }).sort(function (a, b) { return a - b; });
      const reverseValue = locantsText(reverse, group.slot);
      if (reverseValue !== analysis.parts[group.slot] && reverse.every(function (locant) { return locant > 1 && locant < parentLength; })) {
        const reversedOccupancy = {};
        analysis.branches.filter(function (branch) { return !group.members.includes(branch); }).forEach(function (branch) {
          reversedOccupancy[branch.locant] = (reversedOccupancy[branch.locant] || 0) + 1;
        });
        reverse.forEach(function (locant) { reversedOccupancy[locant] = (reversedOccupancy[locant] || 0) + 1; });
        if (Object.keys(reversedOccupancy).every(function (locant) { return reversedOccupancy[locant] <= 2; })) alternatives.set(reverseValue, reverse);
      }
      const values = Array.from(alternatives.keys());
      values.forEach(function (wrongValue, index) {
        const choices = [analysis.parts[group.slot], wrongValue];
        if (values.length > 1) choices.push(values[(index + 1) % values.length]);
        rounds.push(replacement(record, "branch-locants", group.slot, wrongValue, choices,
          "Έλεγξε τα σημεία σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.",
          "Οι διακλαδώσεις «" + group.base + "» συνδέονται στις θέσεις " + group.locants.join(", ") + " της κύριας αλυσίδας. " +
          "Οι θέσεις πρέπει να αντιστοιχούν στα σημεία σύνδεσης. Η αρίθμηση συγκρίνεται από τα δύο άκρα, στο πρώτο σημείο διαφοράς.", difficulty));
      });
      if (group.members.length >= 2 && group.members.length < MULTIPLIERS.length &&
        group.text === MULTIPLIERS[group.members.length] + group.base) {
        const counts = [1, group.members.length + 1];
        const choices = [group.text].concat(counts.map(function (count) { return MULTIPLIERS[count] + group.base; }));
        counts.forEach(function (count) {
          rounds.push(replacement(record, "branch-multiplier", group.slot + 1, MULTIPLIERS[count] + group.base, choices,
            "Έλεγξε πόσες ίδιες διακλαδώσεις υπάρχουν και πώς δηλώνεται το πλήθος τους.",
            "Υπάρχουν " + group.members.length + " ίδιες διακλαδώσεις «" + group.base + "», στις θέσεις " + group.locants.join(", ") +
            ". Το συνθετικό «" + group.text + "» δηλώνει μαζί το είδος και το πλήθος τους.", difficulty));
        });
      }
    });
    if (record.groups.length === 2 && record.groups[0].base !== record.groups[1].base) {
      const first = record.groups[0];
      const second = record.groups[1];
      const parentText = joined(analysis.parts.slice(5));
      const firstText = analysis.parts[first.slot].replace(/^-/, "") + first.text;
      const secondText = analysis.parts[second.slot].replace(/^-/, "") + second.text;
      assert(firstText + "-" + secondText + parentText === analysis.name, "Unsupported branch-group composition");
      const round = roundBase(record, "alphabetical-order", "alphabetical-order:reversed", "Έλεγξε την αλφαβητική σειρά των διαφορετικών διακλαδώσεων.", difficulty,
        "Το «" + first.base + "» προηγείται αλφαβητικά του «" + second.base + "». Οι αριθμοί θέσης και τα πολλαπλασιαστικά προθέματα δεν καθορίζουν τη σειρά. Κάθε ομάδα κρατά τις δικές της θέσεις.");
      Object.assign(round, {
        kind: "order", parts: [
          { id: "branch-group-2", text: secondText, label: "Ομάδα διακλαδώσεων με τις θέσεις της" },
          { id: "branch-group-1", text: firstText, label: "Ομάδα διακλαδώσεων με τις θέσεις της" },
          { id: "parent", text: parentText, label: "Κύρια αλυσίδα" }
        ], movablePartIds: ["branch-group-2", "branch-group-1"],
        correctOrder: ["branch-group-1", "branch-group-2"], suffixPartId: "parent", feedback: feedback("order")
      });
      rounds.push(round);
    }
    return rounds;
  }

  function createGame(catalog, analyses, options) {
    options = options || {};
    const seed = normalizeSeed(options.seed);
    const difficulty = options.difficulty === undefined ? "basic" : options.difficulty;
    assert(difficulty === "basic" || difficulty === "challenge", "Invalid difficulty");
    assert(catalog && catalog.schemaVersion === 1 && nonempty(catalog.revision) &&
      /^[a-f0-9]{64}$/.test(catalog.engineSHA256) && Array.isArray(catalog.molecules), "Invalid structure catalog");
    const byId = Object.create(null);
    if (Array.isArray(analyses)) analyses.forEach(function (analysis) {
      assert(analysis && nonempty(analysis.moleculeId) && !byId[analysis.moleculeId], "Duplicate engine result");
      byId[analysis.moleculeId] = analysis;
    });
    else {
      assert(analyses && typeof analyses === "object", "Missing engine analyses");
      Object.keys(analyses).forEach(function (id) { byId[id] = analyses[id]; });
    }
    const ids = new Set();
    const records = catalog.molecules.map(function (molecule) {
      assert(molecule && /^[a-zA-Z0-9_-]+$/.test(molecule.id) && !ids.has(molecule.id) &&
        nonempty(molecule.mol) && localAsset(molecule.asset), "Invalid/duplicate catalog molecule");
      ids.add(molecule.id);
      const analysis = byId[molecule.id];
      assert(!analysis || analysis.engineSHA256 === undefined || analysis.engineSHA256 === catalog.engineSHA256,
        "Engine revision mismatch for " + molecule.id);
      return checkedAnalysis(molecule, analysis);
    }).sort(function (a, b) { return a.molecule.id < b.molecule.id ? -1 : a.molecule.id > b.molecule.id ? 1 : 0; });
    const rootByCount = new Map();
    records.forEach(function (record) {
      const count = record.analysis.chain.length;
      const root = record.analysis.parts[5];
      assert(!rootByCount.has(count) || rootByCount.get(count) === root, "Inconsistent engine roots for the same chain length");
      rootByCount.set(count, root);
      assert(JSON.stringify(record.analysis.rootVocabulary) === JSON.stringify(records[0].analysis.rootVocabulary),
        "Inconsistent engine root vocabulary");
    });
    // Bound wrong lengths to the pilot's existing carbon range: importing the
    // engine's C1–C20 grammar must not introduce unrelated long-stem difficulty.
    const largestCarbonCount = records.reduce(function (largest, record) { return Math.max(largest, record.analysis.carbonCount); }, 0);
    const vocabulary = records[0].analysis.rootVocabulary.slice(0, largestCarbonCount).map(function (value, index) {
      return { count: index + 1, value: value };
    });
    const random = randomSource(JSON.stringify([VERSION, catalog.revision, catalog.engineSHA256, seed]));
    const definitions = [
      { id: "alkanes-unbranched", title: "Χωρίς διακλαδώσεις", description: "Επισκεύασε ένα μέρος του ονόματος από τη μοριακή δομή.",
        topics: ["Μήκος αλυσίδας", "Είδος δεσμών"], branched: false },
      { id: "alkanes-branched", title: "Με διακλαδώσεις", description: "Σύνδεσε την κύρια αλυσίδα και τις διακλαδώσεις με το όνομα.",
        topics: ["Κύρια αλυσίδα", "Θέσεις διακλαδώσεων", "Πλήθος και σειρά"], branched: true }
    ];
    const sets = definitions.map(function (definition) {
      const eligible = records.filter(function (record) { return (record.analysis.branches.length > 0) === definition.branched; });
      assert(eligible.length >= 3, "Need three different structures per set");
      const usedFamilies = new Set();
      const rounds = shuffle(eligible, random).slice(0, 3).map(function (record) {
        const available = shuffle(candidates(record, vocabulary, difficulty), random);
        const chosen = available.find(function (round) { return !usedFamilies.has(round.fault.kind); }) || available[0];
        assert(chosen, "No eligible fault for " + record.molecule.id);
        usedFamilies.add(chosen.fault.kind);
        if (chosen.kind === "replace") chosen.choices = shuffle(chosen.choices, random);
        return chosen;
      });
      return { id: definition.id, title: definition.title, description: definition.description, topics: definition.topics, rounds: shuffle(rounds, random) };
    });
    return {
      schemaVersion: 2, title: "Συνεργείο ονομάτων",
      description: "Κάθε μόριο έχει ένα λάθος στο όνομά του. Οι επισκευές παράγονται από την ανάλυση των διαθέσιμων δομών.",
      generatorVersion: VERSION, catalogRevision: catalog.revision, engineSHA256: catalog.engineSHA256,
      seed: seed, difficulty: difficulty, availableMoleculeCount: records.length, sets: sets
    };
  }

  const api = Object.freeze({ version: VERSION, createGame: createGame, normalizeSeed: normalizeSeed });
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  global.NameleculeRepairGenerator = api;
}(typeof globalThis !== "undefined" ? globalThis : this));
