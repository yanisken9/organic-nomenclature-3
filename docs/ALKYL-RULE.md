# Alkyl name/prefix reference rule - 2026-10-20

User approved new reusable rule table at lesson step9: methyl, ethyl, two
propyls and four butyls, with structures/attachment bonds, Greek traditional
names and prefixes plus IUPAC alternatives. Reference:
https://iupac.qmul.ac.uk/BlueBook/Papp2.html
Traditional iso/sec/tert labels are shown alongside systematic alternatives;
this adds teaching reference data, not new molecule engine coverage.

Changes: teaching_48.js builds eight-row reference as namingRules.alkylRule/
alkylTable; molview_48.js selects it for hydrocarbon compSecondSub1/2 and
highlights selected group's row(s). Non-hydrocarbon prefixes keep FG rule4.
Theme CSS provides compact two-column table, fixed width, wrapping for long
systematic labels. Existing collapsible rule title behavior preserved.

The user's latest Desktop file is now named
1Alkenia-Onomatologia_kai_diakladoseis (actual Greek filename),22 steps.
Read it directly, preserving user edits; enabled step9 show.rule and copied
to project under the same name. Old version1 filename no longer exists in
Desktop output folder. Both copies are byte-identical.

Tests: JSC syntax in teaching/viewer; lesson validation22 steps/no warnings.
Full Firefox: step2/3/4 existing highlighted rule rows retained. Step9 rule
visible, eight rows, methyl selected; opened table height677,width346 fits
350px column. Screenshot inspected, design/assets/alkyl-rule-step9.png.
Free exploration ethyl/methyl groups select appropriate reference rows;
chlorobutane retains FG rule4. No core/data change, commit or publication.
Public app does not yet include this new table; use local v48 port8013.
