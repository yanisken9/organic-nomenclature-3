# Automatic name font fitting - 2026-10-20

User reported long name overflow and explicitly chose font adaptation over
wrapping. Approved implementation keeps complete name on one line.

Changed css/namelecule-48.css and js/mulermoc-nom-molview-48.js only (plus
documentation/evidence). A CSS variable scales component and plus fonts;
labels keep their IDs, eye controls, borders, fixed padding and click handlers.
The fit resets to original size, measures rendered row against host content
width and binary-searches largest fitting font. Short names never enlarge
or shrink unnecessarily. ResizeObserver watches panel width only (no height
feedback loop); rebuilds, selection and font load also schedule fitting.
Color/border transitions remain; font transitions disabled to measure reliably.

Actual Firefox checks:
- Complete long name/boxes remain inside panel in one row for boxed/unboxed,
  plus on/off, eye edit on/off (eight combinations), and after prefix clicks.
- Real eye-button hide/show rebuilds fit correctly.
- Width300 fits at 12.5px without plus separators; width700 restores 17.6px.
- Ethene at normal panel width retains original 17.6px.
- Long name at normal 350px panel without plus uses about16.08px.
- Plus separators plus all boxes can require a small 9px font at width350;
  this follows the requested single-line behavior. No typography floor was
  imposed because it would allow overflow again.
- Screenshot inspected and saved: design/assets/namelecule-name-font-fit.png.
Viewer syntax and git diff checks passed. No chemistry/data/name changes.
All local, no commit/push. Mobile/presentation-wide regression not repeated.
