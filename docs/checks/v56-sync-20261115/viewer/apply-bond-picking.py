from pathlib import Path
import hashlib
P=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate/js/mulermoc-nom-molview-56.js');s=P.read_text()
assert hashlib.sha256(P.read_bytes()).hexdigest()=='5f86d5e80baee771fe7aa76767dd41258e354ae082033f3cc44d6572e1386a17'
a=s.index('    // (anchors come from the per-render geometry cache above.)\n',s.index('function fMulerSelectPick('));b=s.index('    if (!(med > 0)) {\n',a)
s=s[:a]+'''    // A visible label's actual glyph bounds own direct label clicks, even
    // when a wide formula extends beyond the loose center radius. Keep that
    // radius only as a fallback: it must not steal a visible bond interior.
    var best = null, bd = Infinity, loose = null, ld = rAtom * rAtom;
    for (var i = 0; i < anchors.length; i++) {
      var anchor = anchors[i];
      if (!anchor || anchor.atom == null || isNaN(anchor.atom)) continue;
      var dx = anchor.x - px, dy = anchor.y - py, d2 = dx * dx + dy * dy;
      if (anchor.w > 0 && anchor.h > 0 &&
          px >= anchor.x - anchor.w / 2 && px <= anchor.x + anchor.w / 2 &&
          py >= anchor.y - anchor.h / 2 && py <= anchor.y + anchor.h / 2 && d2 <= bd) {
        bd = d2; best = anchor.atom;
      }
      if (d2 <= ld) { ld = d2; loose = anchor.atom; }
    }
    function anchorPick(atom0) {
      if (atom0 === null || atom0 === undefined) return null;
      // Keep native armed-quiz H-to-parent behavior for both direct glyph
      // hits and the loose fallback. Free and explicitly targeted H stay H.
      var parent = -1;
      try { if (typeof fMulerQuizHydrogenParent === "function") parent = fMulerQuizHydrogenParent(atom0 + 1); } catch (eH) { parent = -1; }
      return { kind: "atom", atom: (parent > 0 ? parent : atom0 + 1) };
    }
    if (best !== null && best !== undefined) return anchorPick(best);
    if (!groups || !groups.length) return anchorPick(loose);
''' +s[b:]
a=s.index('function fMulerSelectPick(');b=s.index('\nfunction fMulerSelectToggle(',a)
section=s[a:b]
section=section.replace('      if (!(med > 0)) return null;','      if (!(med > 0)) return anchorPick(loose);',1)
assert section.endswith('    return null;\n  } catch (e) { return { ignore: true }; }\n}\n')
section=section[:-len('    return null;\n  } catch (e) { return { ignore: true }; }\n}\n')]+'''    // No direct glyph, implicit vertex or bond corridor claimed the point.
    // Preserve the forgiving native atom-center halo on empty surroundings.
    return anchorPick(loose);
  } catch (e) { return { ignore: true }; }
}
'''
s=s[:a]+section+s[b:];P.write_text(s)
