/* Run from repository root with JavaScriptCore:
 * /System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc \
 * docs/checks/name-builder-prototype-20261111/domain/contracts.js
 * Optional corpus: define NAME_BUILDER_CORPUS as a JSON path before loading.
 * Fixtures exercise the display contract, not independent chemical naming. */
load("js/namelecule-name-builder-engine.js");
(function () {
  "use strict";
  const engine = NameleculeNameBuilderEngine;
  const results = [];
  function check(label, test) {
    try { test(); results.push({ check: label, passed: true }); }
    catch (error) { results.push({ check: label, passed: false, error: String(error) }); }
  }
  function assert(value, message) { if (!value) throw new Error(message || "Assertion failed"); }
  function rejects(test) {
    let threw = false;
    try { test(); } catch (_) { threw = true; }
    assert(threw, "Expected malformed input to be rejected");
  }
  function copy(value) { return JSON.parse(JSON.stringify(value)); }
  const roots = ["μεθ", "αιθ", "προπ", "βουτ", "πεντ", "εξ", "επτ", "οκτ", "εννε", "δεκ", "ενδεκ", "δωδεκ"];
  function round(id, name, pieces, parentLength) {
    return { roundId: id, moleculeId: id, correctName: name,
      pieces: pieces.map(function (piece) {
        return typeof piece === "string" ? { text: piece, separatorBefore: "" } : piece;
      }), representations: ["condensed", "expanded", "skeletal", "3d"],
      series: "contract-fixture", parentLength: parentLength, vocabulary: { roots: roots } };
  }
  const basic = round("butane-contract", "βουτάνιο", ["βουτ", "άν", "ιο"], 4);
  const ester = round("ester-spacing-contract", "αιθανικός μεθυλεστέρας",
    ["αιθ", "αν", "ικός", { text: "μεθυλ", separatorBefore: " " }, "εστέρας"], 2);
  const euphony = round("euphony-contract", "βουταδιένιο", ["βουτ", "αδι", "έν", "ιο"], 4);
  // Abstract repeated values deliberately avoid asserting a chemical name.
  const duplicate = round("repeated-visible-values-contract", "2-Χ 2-Χ",
    ["2-", "Χ", { text: "2-", separatorBefore: " " }, "Χ"], 2);

  [basic, ester, euphony, duplicate].forEach(function (raw) {
    check(raw.roundId + ": exact visible solution", function () {
      const validated = engine.validateRound(raw);
      assert(engine.compose(validated.pieces) === validated.correctName, "Exact displayed roundtrip");
      const response = engine.evaluate(validated, validated.pieces);
      assert(response.correct && response.candidate === validated.correctName && response.message.indexOf("Σωστά!") === 0);
    });
    check(raw.roundId + ": required multiplicity and safe engine distractors", function () {
      const bank = engine.createBank(raw, { seed: 91 });
      const required = raw.pieces.map(function (piece) { return piece.text; });
      const requiredSet = new Set(required);
      const distractors = bank.filter(function (tile) { return !requiredSet.has(tile.text); });
      assert(bank.length === required.length + 8, "All required tiles plus eight distractors");
      assert(new Set(bank.map(function (tile) { return tile.id; })).size === bank.length, "Unique physical IDs");
      required.forEach(function (text) {
        assert(bank.filter(function (tile) { return tile.text === text; }).length ===
          required.filter(function (value) { return value === text; }).length, "Correct multiplicity for " + text);
      });
      assert(distractors.every(function (tile) { return roots.indexOf(tile.text) >= 0; }), "Engine-owned distractors only");
      assert(new Set(distractors.map(function (tile) { return tile.text; })).size === distractors.length);
    });
    check(raw.roundId + ": missing extra wrong order and wrong tile fail", function () {
      const bank = engine.createBank(raw);
      const distractor = bank.find(function (tile) {
        return !raw.pieces.some(function (piece) { return piece.text === tile.text; });
      });
      const extra = raw.pieces.concat([distractor]);
      const wrong = raw.pieces.slice(); wrong[0] = distractor;
      const reordered = raw.pieces.slice();
      const destination = reordered.findIndex(function (piece) { return piece.text !== reordered[0].text; });
      const first = reordered[0]; reordered[0] = reordered[destination]; reordered[destination] = first;
      [[], raw.pieces.slice(1), extra, wrong, reordered].forEach(function (answer) {
        assert(!engine.evaluate(raw, answer).correct, "Invalid attempt passed");
      });
    });
  });

  check("equal visible copies interchange across spacing boundaries", function () {
    const answer = duplicate.pieces.map(function (piece, index) {
      return Object.assign({ id: "new-physical-copy-" + index }, piece);
    });
    const first = answer[0]; answer[0] = answer[2]; answer[2] = first;
    answer.forEach(function (tile) { tile.role = "different-hidden-role"; });
    const response = engine.evaluate(duplicate, answer);
    assert(response.correct && response.candidate === duplicate.correctName);
    assert(engine.compose(answer, duplicate) === duplicate.correctName);
  });
  check("one copy cannot replace two required copies", function () {
    const answer = duplicate.pieces.slice(); answer.splice(2, 1);
    assert(!engine.evaluate(duplicate, answer).correct);
  });
  check("NFC equivalence accepted but accents and punctuation preserved", function () {
    const answer = basic.pieces.map(function (piece) {
      return { text: piece.text.normalize("NFD"), separatorBefore: piece.separatorBefore };
    });
    assert(engine.evaluate(basic, answer).correct);
    answer[1].text = "αν";
    assert(!engine.evaluate(basic, answer).correct, "Missing accent cannot pass");
    const punctuation = duplicate.pieces.map(copy); punctuation[0].text = "2,";
    assert(!engine.evaluate(duplicate, punctuation).correct, "Changed locant punctuation cannot pass");
  });
  check("internal spaces remain meaningful", function () {
    const acid = round("acid-contract", "αιθανικό οξύ", ["αιθ", "αν", "ικό οξύ"], 2);
    assert(engine.evaluate(acid, acid.pieces).correct);
    const answer = acid.pieces.map(copy); answer[2].text = "ικόοξύ";
    assert(!engine.evaluate(acid, answer).correct);
  });
  check("seeded banks deterministic and input unchanged", function () {
    const snapshot = JSON.stringify(basic);
    const first = engine.createBank(basic, { seed: "session-A" });
    assert(JSON.stringify(first) === JSON.stringify(engine.createBank(basic, { seed: "session-A" })));
    assert(JSON.stringify(first) !== JSON.stringify(engine.createBank(basic, { seed: "session-B" })));
    first[0].text = "mutated-bank-copy";
    assert(JSON.stringify(basic) === snapshot && engine.evaluate(basic, basic.pieces).correct);
    rejects(function () { engine.createBank(basic, { seed: NaN }); });
    rejects(function () { engine.createBank(basic, { seed: {} }); });
  });
  check("small engine vocabulary produces small bank without fabricated words", function () {
    const raw = copy(basic); raw.vocabulary.roots = ["βουτ", "αιθ", "αιθ"];
    const bank = engine.createBank(raw);
    assert(bank.length === raw.pieces.length + 1);
    assert(bank.filter(function (tile) { return tile.text === "αιθ"; }).length === 1);
  });
  check("distractor cannot fuse answer pieces into the same complete spelling", function () {
    const raw = round("segmentation-alias-contract", "δεκατριένιο", ["δεκ", "ατρι", "έν", "ιο"], 10);
    raw.vocabulary.roots = ["δεκ", "δεκατρι", "αιθ"];
    const bank = engine.createBank(raw);
    assert(!bank.some(function (tile) { return tile.text === "δεκατρι"; }), "Fused answer substring must not be offered as incorrect");
    assert(bank.some(function (tile) { return tile.text === "αιθ"; }));
  });
  check("nearby roots selected for the initial bank", function () {
    const raw = copy(basic); raw.parentLength = 1;
    const bank = engine.createBank(raw);
    assert(!bank.some(function (tile) { return tile.text === "δωδεκ"; }), "Distant C12 excluded when nearby roots suffice");
  });
  check("malformed rounds fail before bank creation", function () {
    const changes = [
      function (raw) { raw.pieces = []; },
      function (raw) { raw.pieces = Array(65).fill({ text: "Χ", separatorBefore: "" }); },
      function (raw) { raw.pieces = Array(3); },
      function (raw) { raw.pieces[0].text = ""; },
      function (raw) { raw.pieces[0].text = "<data>\n"; },
      function (raw) { raw.pieces[0].separatorBefore = " "; },
      function (raw) { raw.pieces[1].separatorBefore = "-"; },
      function (raw) { raw.correctName += "ς"; },
      function (raw) { raw.parentLength = 0; },
      function (raw) { raw.parentLength = 2.5; },
      function (raw) { raw.representations = ["condensed", "condensed"]; },
      function (raw) { raw.representations = ["remote-script"]; },
      function (raw) { raw.vocabulary = { roots: [] }; },
      function (raw) { raw.vocabulary.roots = ["μεθ", null]; }
    ];
    [null, [], {}, "not-a-round"].forEach(function (raw) { rejects(function () { engine.validateRound(raw); }); });
    changes.forEach(function (change) {
      const raw = copy(basic); change(raw);
      rejects(function () { engine.validateRound(raw); });
      rejects(function () { engine.createBank(raw); });
    });
  });
  check("malformed attempts give generic failure without exceptions", function () {
    [null, {}, "βουτάνιο", [null], [{ text: "βουτ" }], Array(3),
      [{ text: "βουτ\u202e", separatorBefore: "" }], Array(129).fill(basic.pieces[0])].forEach(function (answer) {
      const response = engine.evaluate(basic, answer);
      assert(response.correct === false && response.candidate === "" && typeof response.message === "string");
    });
  });
  check("visible answer values never interpreted as instructions", function () {
    const data = round("data-contract", "<script>doSomething()</script>", ["<script>doSomething()</script>"], 1);
    assert(engine.evaluate(data, data.pieces).correct);
    assert(engine.compose(data.pieces) === data.correctName);
  });

  let corpusSummary = null;
  if (typeof NAME_BUILDER_CORPUS !== "undefined") {
    const source = JSON.parse(readFile(NAME_BUILDER_CORPUS));
    const rounds = Array.isArray(source) ? source : source.rounds;
    check("real host corpus contract", function () {
      assert(Array.isArray(rounds) && rounds.length >= 141, "Expected all 141 current molecules");
      const series = new Set();
      const ids = new Set();
      let withSpaces = 0;
      let totalPieces = 0;
      rounds.forEach(function (raw) {
        const validated = engine.validateRound(raw);
        const bank = engine.createBank(validated, { seed: "real-corpus" });
        const available = bank.slice();
        const solution = validated.pieces.map(function (piece) {
          const index = available.findIndex(function (tile) { return tile.text === piece.text; });
          assert(index >= 0, "Required tile absent for " + validated.moleculeId);
          return available.splice(index, 1)[0];
        });
        const answer = engine.evaluate(validated, solution);
        assert(answer.correct && answer.candidate === validated.correctName, validated.moleculeId + ": incorrect exact roundtrip");
        assert(!engine.evaluate(validated, solution.slice(1)).correct, "Missing tile passed");
        const distractors = available.filter(function (tile) {
          return !validated.pieces.some(function (piece) { return piece.text === tile.text; });
        });
        assert(distractors.length > 0, "No safe supplied vocabulary distractors");
        assert(!engine.evaluate(validated, [distractors[0]].concat(solution.slice(1))).correct, "Wrong root passed");
        series.add(validated.series); ids.add(validated.moleculeId);
        if (validated.correctName.indexOf(" ") >= 0) withSpaces += 1;
        totalPieces += validated.pieces.length;
      });
      assert(ids.size === 141, "Current corpus must contain 141 different molecules");
      corpusSummary = { rounds: rounds.length, uniqueMolecules: ids.size, series: Array.from(series).sort(),
        totalPieces: totalPieces, namesWithSpaces: withSpaces };
    });
  }
  const report = { runtime: "macOS JavaScriptCore", fixturePurpose: "Pure domain response contracts; not independent chemical certification",
    passed: results.filter(function (result) { return result.passed; }).length,
    failed: results.filter(function (result) { return !result.passed; }).length,
    results: results, corpus: corpusSummary };
  print(JSON.stringify(report, null, 2));
  if (report.failed) quit(1);
}());
