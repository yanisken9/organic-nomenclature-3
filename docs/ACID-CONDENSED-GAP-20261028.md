# Condensed acid branch-label clearance — 2026-10-28

Approved follow-up: upper CH3/CH2 in acid condensed diagrams must not appear
detached from a vertical C–C bond. Developer implementation/evidence snapshot;
the independent review outcome is recorded in [session notes](SESSION-NOTES.md).

The whole CHn text bbox includes a lowered subscript. The existing white label
rectangle consequently masked too much of the bond below C. In the inspected
four new acids, affected upper-label gaps were approximately5.92–5.93px while
plain C/CH had approximately1.43–1.45px, at the22px target font setting.

Only existing `fAddHydrogens2SVG` in viewer52 changes: for Condensed carboxylic
acids with a vertical C neighbor below a carbon label, use the C glyph's lower
bound for mask height. Preserve the whole label's horizontal extent and existing
padding. CHn position/markup, H subscripts and native bond geometry are unchanged.
MainHTML refreshes the viewer cache URL. No new drawing function, MOL change or
coordinate translation. Four affected upper labels in three recent acids now
have approximately1.43–1.45px clearance at desktop default zoom.

Developer verification:

- `check-acid-condensed-gap-20261028.py`: exact two-source diff scope,1547protected
  files unchanged, JS syntax/PythonAST/git diff --check. All data, MOL/SDF,
  provenance, core, scenarios and React files retain exact baseline bytes.
- `test-acid-condensed-gap-browser-20261028.py`: real localFirefox, all15acids and
  four non-acid guards at1500/390px;112before/after form comparisons. Native lines,
  text markup and viewBox unchanged. Otherforms/nonacids have identical fullSVG.
  No new atom-label overlap/clipping. Mask changes confined to the four affected
  acid labels; vertical gaps measured at both widths.
- 18selected/zoom cases on the complexacid: root/methyl/ethyl boxes, two widths,
  default/in/restored zoom. Actual JSmol selection nonempty; CHn clearance and
  no atom-label overlap/clipping checked in the final run. Colour off/on and
  PNGblob/parseableSVG export also exercised. Final run passed,0JavaScript errors.
- Screenshots under /tmp/namelecule-acid-condensed-gap-20261028 inspected by
  Developer; browser execution remains Developer evidence for review.

Scope: presentation only, not new chemistry or teaching. No Safari, Reactbuild,
alllesson replay or new naming certification is claimed. Prior prefix-scenario
replay limitation unchanged. Current core52 SHA256 remains
97ae0466558eb954b810352d5f135fd4958e94a71c4a0cfef09fcf104085f78a.
Earlier28Octcore acid-naming extension remains a separate contribution; this
follow-up adds no core change. All changes local; no commit/push/publication.
