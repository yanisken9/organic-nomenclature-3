# Κορεσμένα μονοκαρβοξυλικά οξέα — θεωρία,28/10/2026

Approved28step progressive-disclosure lesson in the existing Main v52 library.
Implementation and Developer evidence snapshot; independent review outcome and
Desktop-copy status are recorded in SESSION-NOTES.md/YANNIS-CONTRIBUTIONS.md.
Local only, no commit/push/publication. Main now130molecules/13active lessons/
311steps; the previous12active lessonJSONs (all23prior scenariofiles) unchanged.

## Content and sequence

All8existing eligible acyclic saturated monoacids, ascending totalcarbon count:

| Molecule key | Name | Formula | Parent C |
|---|---|---|---|
| methanoicacid | μεθανικό οξύ | CH2O2 | 1 |
| propionicacid | προπανικό οξύ | C3H6O2 | 3 |
| butanoic_acid | βουτανικό οξύ | C4H8O2 | 4 |
| methyl_2_propanoic_acid | 2-μεθυλοπροπανικό οξύ | C4H8O2 | 3 |
| pentanoic_acid | πεντανικό οξύ | C5H10O2 | 5 |
| dimethyl_2_2_propanoic_acid | 2,2-διμεθυλοπροπανικό οξύ | C5H10O2 | 3 |
| ethyl_2_methyl_3_pentanoic_acid | 2-αιθυλο-3-μεθυλοπεντανικό οξύ | C8H16O2 | 5 |
| ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid | 3-αιθυλο-2-ισοπροπυλο-4,5-διμεθυλοεξανικό οξύ | C13H26O2 | 6 |

Steps1–4 build the three name components from methanoicacid;5–8 introduce the
general formula CνH2νO2(ν≥1),COOH carbon asC1/numbering and2Drepresentations;
9–11introduce one methyl;12retrieves the unbranched pattern;13–15distinguish
allC/parentC and repeated2,2locants/di;16–20separate ethyl/methyl then alphabetize;
21–26separate allthree prefixgroups of the complexacid, including4,5locants;
27summarizes in2D;28is optional3D. No quiz, scoring, isomerism or new molecules.

The sequence preserves existing lesson language,JSONv1/style/show controls,
progressive name hiding and optional initially closed rule tables. As in the
monoaldehyde template, plus separators appear while building hidden components
and disappear once the relevant name is assembled, preserving readability. It emphasizes
that C=O withinCOOH does not make the carbon skeleton unsaturated,COOH is one
characteristic group,C1 belongs to the parent and is not written as acidlocant,
totalC differs from parentC,and multiplicative di is ignored in alphabetizing.
The isopropyl and Greek word-joining conventions match the existing application;
no naming-algorithm change. The initially authored elision«διμεθυλεξανικό» was
aligned to the actual runtime«διμεθυλοεξανικό» before final checks.

Scientific reference: IUPAC Blue Book P-65.1.2.1,
https://iupac.qmul.ac.uk/BlueBook/P6.html#P-65.1.2.1
for systematic acid suffix and omitted carboxyl locants. School Greek systematic
names are retained; no claim that methanoic/formic naming conventions are identical
to modern English preferred-name choices. No universal IUPAC certification.

## Integration

New `scenarios/saturated-monocarboxylic-acids-nomenclature.scenario.json` linked
from the existing saturatedmonoacid section; otheracid section stays pending.
Player52 adds only the new lesson to its rule-title whitelist and recognizes
compAcidNumber3/compAcidSub3 as acidPrefixNumber3/acidPrefixSub3. This completes
replay/capture/apply of the already existing Main prefix boxes, previously known
as a limitation for futureacid scenarios. No schema change. MainHTML cache refreshed;
README count updated. No core/viewer/teaching/MOL/SDF/provenance/React change.

## Developer checks

- Static script validates28steps,all8eligibleinventory targets,staged visible
  modes,closedrules/optional3D;48actual-core form/chain cases with matching2D/3D
  numbered signatures. RDKit sanitized graph/formula equality across available
  2Dforms/SDFs. For chemical comparison only, atom-map metadata is ignored:
  oldmethanoicCondensed carries explicitmap0 unlikeExpanded; source stays unchanged.
- 1555protected files unchanged, including all23prior scenarioJSONs and allcore/
  viewer/teaching/molecular/React assets. All283old linked-step rule-availability
  results match before/after. JSsyntax/gitdiffcheck pass.
- RealFirefox naturalNext through28steps: actualnames,hiddenstates,ruleheaders
  with manualopen/close,numbering/fit. Bothnewmodes capture/apply correctly and
  select exact third-group atoms+H in loadedJSmol. Export/validate preserves all
  authored snapshots. Prev/jump/narrow/Exit/library checked;all13linked lessons
  validate. Existingketone root/suffix/branch replay checked. Final browser run
  completed with0JavaScript errors.
- Additional18actualthree-form controls/captureapply at1500/390 and dedicated
  visiblecard checks passed against the finalJSON,0JavaScript errors.
  Screenshots only under /tmp/namelecule-monoacids-lesson-20261028.

One initial browser assertion queried JSmol before its asynchronous selection
completed; the final harness explicitly waits for the expected selected set.
This was not presented as successful initial execution. No application fix beyond
the approved player mapping was needed. Browser execution is Developer evidence;
Reviewer inspection/reruns are recorded separately in session/contribution notes.
No Safari, React rebuild, all311steps runtime replay or student learning-outcome
study claimed. The new lesson's28steps and representative prior flows were tested.

Core52 unchanged by this lesson, SHA256
97ae0466558eb954b810352d5f135fd4958e94a71c4a0cfef09fcf104085f78a.
Earlier28Octacid-naming core extension is a separate contribution.
