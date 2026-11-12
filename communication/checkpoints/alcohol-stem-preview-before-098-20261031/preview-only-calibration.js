function fPrepareFixedCCAlkanePrototype() {
  if (mode2D !== "expanded" ||
      !["methane", "ethane", "propane", "butane", "pentane",
        "methyl_2_pentane", "dimethyl_2_3_butane", "ethyl_3_dimethyl_2_5_hexane",
        "ethene", "propene", "butene_1", "butene_2", "methyl_2_propene",
        "methyl_3_butene_1", "ethyl_3_dimethyl_2_5_hexene_2",
        "propyne", "ethyne", "butyne_1", "butyne_2", "methyl_3_butyne_1",
        "methyl_3_pentyne_1", "methyl_4_pentyne_2", "ethyl_4_dimethyl_3_5_heptyne_1",
        "propadiene", "pentadiene_1_3", "butadiene_1_3", "butadiene_1_2",
        "pentadiene_1_4", "methyl_3_pentadiene_1_3", "dimethyl_2_3_pentadiene_1_3",
        "ethyl_3_dimethyl_4_5_hexadiene_1_4",
        "penten_3_yne_1", "hexen_1_yne_4", "buten_1_yne_3", "hexen_2_yne_4",
        "methyl_2_buten_1_yne_3", "dimethyl_2_3_penten_1_yne_4",
        "ethyl_4_dimethyl_2_3_hepten_2_yne_5",
        "propanol_1", "penten_4_ol_2", "butanol_1", "butene_3_ol_2", "penten_2_ol_1", "propanediol_1_2", "propanetriol", "ethanol", "butanol_2", "methyl_4_pentanol_2", "dimethyl_2_2_pentanol_3", "methyl_2_propanediol_1_2", "methyl_3_buten_3_ol_2", "methyl_3_pentyn_4_ol_2", "methyl_4_penten_4_yn_2_ol_1", "ethyl_3_methyl_4_hexen_3_yn_5_ol_2", "isopropyl_4_dimethyl_3_5_heptanol_2"].includes(selectedMol)) return;
  const svg = molSvg?.node;
  if (!svg || svg.dataset.alkaneFixedCCScale) return;
  const lines = [...svg.querySelectorAll("line")];
  if (lines.length !== bondList.reduce((sum,bond)=>sum+bond[2],0)) return;
  const anchors = new Map(), lengths = [], hydrogenLengths = [];
  for (let i = 0; i < bondList.length; i++) {
    const [a, b, order] = bondList[i];
    if (![1,2,3].includes(order)) return;
    // Multiple-bond strokes can be offset from their atom centers. Derive centers
    // from single C-C/C-H bonds, using the actual bond-to-SVG primitive map.
    // Prefer single-bond anchors. A cumulene center can have only double
    // bonds; its missing anchor is resolved from validated stroke pairs below.
    if (order > 1) continue;
    const line = lines[svgBondList[i]-1];
    if (!line) return;
    const p = {x: Number(line.getAttribute("x1")), y: Number(line.getAttribute("y1"))};
    const q = {x: Number(line.getAttribute("x2")), y: Number(line.getAttribute("y2"))};
    if (![p.x, p.y, q.x, q.y].every(Number.isFinite)) return;
    for (const [atom, point] of [[a - 1, p], [b - 1, q]]) {
      const previous = anchors.get(atom);
      if (previous && Math.hypot(previous.x - point.x, previous.y - point.y) > 0.01) return;
      anchors.set(atom, point);
    }
    if ((allAtomsTypeList[a - 1] === "C" && allAtomsTypeList[b - 1] === "H") ||
        (allAtomsTypeList[a - 1] === "H" && allAtomsTypeList[b - 1] === "C")) {
      hydrogenLengths.push(Math.hypot(q.x - p.x, q.y - p.y));
    }
  }
  if (anchors.size !== allAtomsTypeList.length) {
    // Symmetric, parallel native double strokes identify their centerline.
    // Validate both endpoints against every existing anchor before accepting
    // missing centers. No atom or bond geometry is moved by this operation.
    for (let i=0;i<bondList.length;i++) {
      const [a,b,order]=bondList[i];
      if (order!==2) continue;
      const pair=lines.slice(svgBondList[i]-1,svgBondList[i]+1);
      if (pair.length!==2) return;
      const points=pair.map(line=>({
        p:{x:Number(line.getAttribute("x1")),y:Number(line.getAttribute("y1"))},
        q:{x:Number(line.getAttribute("x2")),y:Number(line.getAttribute("y2"))}
      }));
      if (points.some(v=>![v.p.x,v.p.y,v.q.x,v.q.y].every(Number.isFinite))) return;
      const vectors=points.map(v=>({x:v.q.x-v.p.x,y:v.q.y-v.p.y}));
      const lengths=vectors.map(v=>Math.hypot(v.x,v.y));
      if (lengths.some(v=>!(v>0)) || Math.abs(lengths[0]-lengths[1])>2 ||
          Math.abs(vectors[0].x*vectors[1].y-vectors[0].y*vectors[1].x)>lengths[0]*lengths[1]*.001 ||
          vectors[0].x*vectors[1].x+vectors[0].y*vectors[1].y<=0) return;
      for (const [atom,end] of [[a-1,"p"],[b-1,"q"]]) {
        const point={x:(points[0][end].x+points[1][end].x)/2,
          y:(points[0][end].y+points[1][end].y)/2};
        const previous=anchors.get(atom);
        // One native unit allows only the producer's integer rounding.
        if (previous && Math.hypot(previous.x-point.x,previous.y-point.y)>1) return;
        if (!previous) anchors.set(atom,point);
      }
    }
  }
  if (anchors.size !== allAtomsTypeList.length) return;
  for (const [a,b] of bondList) {
    if (allAtomsTypeList[a-1] !== "C" || allAtomsTypeList[b-1] !== "C") continue;
    const p=anchors.get(a-1),q=anchors.get(b-1);
    lengths.push(Math.hypot(q.x-p.x,q.y-p.y));
  }
  // Methane has no C-C. Its C-H/font uses half the common C-C/font unit.
  // This is a calibration value only; native atom anchors and bonds stay intact.
  if (!lengths.length && selectedMol === "methane") {
    lengths.push(...hydrogenLengths.map(length => length * 2));
  }
  if (!lengths.length || anchors.size !== allAtomsTypeList.length) return;
  lengths.sort((a, b) => a - b);
  // Original reference C-C/font 3.49, shortened by the approved 25%.
  // The existing calibration/backplate/numbering pipeline is shared by the
  // alkenes, alkynes and dienes; the historical dataset name stays for callers.
  // Change label size around native atom anchors, never molecular geometry.
  const font = lengths[Math.floor(lengths.length / 2)] / 2.6175;
  if (!(font > 0)) return;
  const context = document.createElement("canvas").getContext("2d");
  if (!context) return;
  const texts = fGetRenderedAtomTextMap(false, true), changes = [];
  for (const [atom, anchor] of anchors) {
    const label = texts[atom];
    if (!label || label.node.textContent.trim() !== allAtomsTypeList[atom]) return;
    const originalFont = parseFloat(label.attr("font-size"));
    const x = Number(label.attr("x")), y = Number(label.attr("y"));
    if (!(originalFont > 0) || ![x, y].every(Number.isFinite)) return;
    const style = getComputedStyle(label.node);
    context.font = `${style.fontStyle} ${style.fontWeight} ${font}px ${style.fontFamily}`;
    const ink = context.measureText(allAtomsTypeList[atom]);
    const cx = (ink.actualBoundingBoxRight - ink.actualBoundingBoxLeft) / 2;
    const cy = (ink.actualBoundingBoxAscent - ink.actualBoundingBoxDescent) / 2;
    if (![cx, cy].every(Number.isFinite)) return;
    changes.push([label, {x: anchor.x - cx, y: anchor.y + cy,
      "font-size": font + "px"}, anchor]);
  }
  changes.forEach(([label, attributes, anchor]) => {
    label.attr(attributes);
    label.node.dataset.fixedCCAtomX = String(anchor.x);
    label.node.dataset.fixedCCAtomY = String(anchor.y);
  });
  svg.dataset.alkaneFixedCCScale = String(font / 270);
}

