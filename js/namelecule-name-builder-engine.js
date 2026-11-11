/* Pure name-builder rules. The current naming engine supplies the answer and
 * its displayed pieces; this module never derives a chemical name itself. */
(function (global) {
  "use strict";

  const MAX_PIECES = 64;
  const MAX_ANSWER_TILES = 128;
  const REPRESENTATIONS = ["condensed", "expanded", "skeletal", "3d"];
  const SUCCESS = "Σωστά! Επέλεξες τα κατάλληλα συνθετικά και σχημάτισες το όνομα στη σωστή σειρά.";
  const RETRY = "Το όνομα δεν είναι ακόμη σωστό. Έλεγξε τα συνθετικά και τη σειρά τους και δοκίμασε ξανά.";

  function assert(condition, message) {
    if (!condition) throw new Error(message);
  }

  function record(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function normalizedText(value, limit, label) {
    assert(typeof value === "string" && value.length > 0 && value.length <= limit,
      "Invalid " + label);
    const text = value.normalize("NFC");
    assert(text.trim() === text && text.length > 0 &&
      !/[\u0000-\u001f\u007f\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]/.test(text),
      "Invalid " + label);
    return text;
  }

  function normalizeTile(tile) {
    assert(record(tile), "Invalid name tile");
    const text = normalizedText(tile.text, 256, "tile text");
    assert(tile.separatorBefore === "" || tile.separatorBefore === " ",
      "Invalid tile separator");
    const result = { text: text, separatorBefore: tile.separatorBefore };
    if (tile.role !== undefined) result.role = normalizedText(tile.role, 64, "tile role");
    return result;
  }

  function readTiles(tiles) {
    assert(Array.isArray(tiles) && tiles.length <= MAX_ANSWER_TILES, "Invalid answer tiles");
    return Array.from(tiles, normalizeTile);
  }

  function joinTiles(tiles, round) {
    return tiles.map(function (tile, index) {
      // Spacing belongs to the displayed name's boundaries, not a physical
      // copy of a tile. Identical visible values remain interchangeable.
      const expected = round && round.pieces[index];
      const separator = expected && expected.text === tile.text
        ? expected.separatorBefore : tile.separatorBefore;
      return (index === 0 ? "" : separator) + tile.text;
    }).join("");
  }

  function validateRound(raw) {
    assert(record(raw), "Invalid name-builder round");
    const round = {
      roundId: normalizedText(raw.roundId, 160, "round id"),
      moleculeId: normalizedText(raw.moleculeId, 160, "molecule id"),
      correctName: normalizedText(raw.correctName, 2048, "correct name"),
      series: normalizedText(raw.series, 80, "series"),
      parentLength: raw.parentLength
    };
    assert(Number.isSafeInteger(round.parentLength) && round.parentLength >= 1 && round.parentLength <= 128,
      "Invalid parent length");
    assert(Array.isArray(raw.pieces) && raw.pieces.length > 0 && raw.pieces.length <= MAX_PIECES,
      "Invalid correct name pieces");
    round.pieces = Array.from(raw.pieces, function (piece) { return Object.freeze(normalizeTile(piece)); });
    assert(round.pieces[0].separatorBefore === "" && joinTiles(round.pieces) === round.correctName,
      "Displayed name pieces do not reproduce the correct name");
    assert(Array.isArray(raw.representations) && raw.representations.length > 0 &&
      raw.representations.length <= REPRESENTATIONS.length, "Invalid representations");
    round.representations = Array.from(raw.representations);
    assert(new Set(round.representations).size === round.representations.length &&
      round.representations.every(function (mode) { return REPRESENTATIONS.includes(mode); }),
      "Invalid representations");
    assert(record(raw.vocabulary) && Array.isArray(raw.vocabulary.roots) &&
      raw.vocabulary.roots.length > 0 && raw.vocabulary.roots.length <= 128,
      "Invalid engine root vocabulary");
    const roots = Array.from(raw.vocabulary.roots, function (root) {
      return normalizedText(root, 64, "engine root");
    });
    round.vocabulary = Object.freeze({ roots: Object.freeze(roots) });
    Object.freeze(round.pieces);
    Object.freeze(round.representations);
    return Object.freeze(round);
  }

  function seedHash(value) {
    let result = 2166136261;
    for (let index = 0; index < value.length; index += 1) {
      result = Math.imul(result ^ value.charCodeAt(index), 16777619);
    }
    return result >>> 0;
  }

  function randomFromSeed(seed) {
    let state = seed;
    return function () {
      state = (state + 0x6d2b79f5) | 0;
      let value = Math.imul(state ^ (state >>> 15), state | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }

  function createBank(raw, options) {
    const round = validateRound(raw);
    assert(options === undefined || record(options), "Invalid bank options");
    const suppliedSeed = options && options.seed;
    assert(suppliedSeed === undefined ||
      (typeof suppliedSeed === "string" && suppliedSeed.length <= 256) ||
      (typeof suppliedSeed === "number" && Number.isFinite(suppliedSeed)), "Invalid shuffle seed");
    const seed = seedHash(suppliedSeed === undefined
      ? round.roundId + ":" + round.moleculeId : typeof suppliedSeed + ":" + suppliedSeed);
    const bank = round.pieces.map(function (piece) { return Object.assign({}, piece); });
    const usedTexts = new Set(round.pieces.map(function (piece) { return piece.text; }));
    usedTexts.add(round.correctName);
    // C1 is at roots[0]. Nearby engine roots offer plausible count choices
    // without fabricating suffixes, locants or alternative complete names.
    const nearbyRoots = round.vocabulary.roots.map(function (text, index) {
      return { text: text, carbonCount: index + 1 };
    }).sort(function (left, right) {
      return Math.abs(left.carbonCount - round.parentLength) - Math.abs(right.carbonCount - round.parentLength) ||
        left.carbonCount - right.carbonCount;
    });
    let distractors = 0;
    nearbyRoots.some(function (root) {
      // A distractor must not be a substring of the complete answer: longer
      // roots can otherwise fuse existing root/euphony/multiplier pieces into
      // the same written name with a different segmentation.
      if (!usedTexts.has(root.text) && !round.correctName.includes(root.text)) {
        bank.push({ text: root.text, separatorBefore: "", role: "root" });
        usedTexts.add(root.text);
        distractors += 1;
      }
      return distractors === 8;
    });
    bank.forEach(function (tile, index) { tile.id = "tile-" + seed.toString(36) + "-" + index.toString(36); });
    const random = randomFromSeed(seed);
    for (let index = bank.length - 1; index > 0; index -= 1) {
      const destination = Math.floor(random() * (index + 1));
      const previous = bank[index];
      bank[index] = bank[destination];
      bank[destination] = previous;
    }
    return bank;
  }

  function compose(answerTiles, rawRound) {
    const round = rawRound === undefined ? undefined : validateRound(rawRound);
    return joinTiles(readTiles(answerTiles), round);
  }

  function evaluate(rawRound, answerTiles) {
    const round = validateRound(rawRound);
    let answer;
    try {
      answer = readTiles(answerTiles);
    } catch (_) {
      return { correct: false, message: RETRY, candidate: "" };
    }
    const candidate = joinTiles(answer, round);
    const correct = answer.length === round.pieces.length && answer.every(function (tile, index) {
      return tile.text === round.pieces[index].text;
    });
    return { correct: correct, message: correct ? SUCCESS : RETRY, candidate: candidate };
  }

  const api = Object.freeze({ validateRound: validateRound, createBank: createBank,
    evaluate: evaluate, compose: compose });
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  global.NameleculeNameBuilderEngine = api;
}(typeof globalThis !== "undefined" ? globalThis : this));
