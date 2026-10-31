/* =========================================================
   図形推理テスト 問題データ・描画
   各問題は 3×3 のマトリクスで、右下（答え）を8つの選択肢から選ぶ。
   選択肢は「答えに3種類の誤りを0〜3個組み合わせた8通り」で作るため、
   どの属性も正しい値が選択肢の半数にしか現れず、消去法だけでは解けない。
   ========================================================= */
(function (root) {
  "use strict";

  const INK = "#1d2330", GRAY = "#9aa0a8", PAPER = "#ffffff";

  /* ---------- 要素と配置 ---------- */
  const E = (t, o = {}) => Object.assign({ t, x: 50, y: 50, s: 30, f: "none", r: 0 }, o);

  // 3×3 のスロット（0〜8, 左上から行優先）
  const SLOT = [25, 50, 75];
  const slotXY = (k) => [SLOT[k % 3], SLOT[Math.floor(k / 3)]];
  const LAYOUT = {
    1: [4], 2: [3, 5], 3: [3, 4, 5], 4: [0, 2, 6, 8], 5: [0, 2, 4, 6, 8],
    6: [0, 1, 2, 6, 7, 8], 7: [0, 1, 2, 4, 6, 7, 8], 8: [0, 1, 2, 3, 5, 6, 7, 8], 9: [0, 1, 2, 3, 4, 5, 6, 7, 8]
  };
  // 同じ図形を n 個並べる
  function many(n, tpl) {
    const s = tpl.s || (n === 1 ? 40 : n === 2 ? 26 : n === 3 ? 19 : 18);
    return LAYOUT[n].map((k) => { const [x, y] = slotXY(k); return E(tpl.t, Object.assign({}, tpl, { x, y, s })); });
  }
  // ドット集合（3×3スロット）
  const dots = (set) => [...set].map((k) => { const [x, y] = slotXY(k); return E("circle", { x, y, s: 18, f: "black" }); });

  // 線分ライブラリ
  const SEG = {
    H: [20, 50, 80, 50], V: [50, 20, 50, 80], D1: [22, 22, 78, 78], D2: [78, 22, 22, 78],
    T: [20, 20, 80, 20], B: [20, 80, 80, 80], L: [20, 20, 20, 80], R: [80, 20, 80, 80]
  };
  const segs = (set) => [...set].map((id) => { const [x1, y1, x2, y2] = SEG[id]; return { t: "seg", x1, y1, x2, y2 }; });
  // 中心から放射状に伸びる8本のスポーク（0=真上、時計回り45°ずつ）
  const spokes = (set) => [...set].map((k) => {
    const a = (-90 + k * 45) * Math.PI / 180;
    return { t: "seg", x1: 50, y1: 50, x2: +(50 + 38 * Math.cos(a)).toFixed(2), y2: +(50 + 38 * Math.sin(a)).toFixed(2) };
  });
  // 円周上の8点
  const ring = (k, R = 36) => { const a = (-90 + k * 45) * Math.PI / 180; return [+(50 + R * Math.cos(a)).toFixed(2), +(50 + R * Math.sin(a)).toFixed(2)]; };
  // 四隅（0=左上, 1=右上, 2=右下, 3=左下）
  const CORNER = [[27, 27], [73, 27], [73, 73], [27, 73]];
  const CORNER_OUT = [[16, 16], [84, 16], [84, 84], [16, 84]];

  const toggle = (set, v) => { const s = new Set(set); s.has(v) ? s.delete(v) : s.add(v); return s; };
  const set = (o, k, v) => Object.assign({}, o, { [k]: v });
  const P = (k, v) => (p) => set(p, k, v);          // 属性を誤った値に変える
  const T = (k, v) => (p) => set(p, k, toggle(p[k], v)); // 集合の要素を出し入れする

  /* ---------- 問題 ----------
     spec(r, c) : 各マスのパラメータ（r=行, c=列, 0始まり）
     draw(p)    : パラメータ → 要素の配列
     wrong      : 答えに加える3種類の誤り
  */
  const SH = ["circle", "square", "tri"];
  const ITEMS = [
    // ---- 基礎（1〜8）----
    { id: "M01", spec: (r, c) => ({ t: SH[r], n: c + 1 }), draw: (p) => many(p.n, { t: p.t, f: p.hollow ? "none" : "black" }),
      wrong: [P("n", 2), P("t", "square"), P("hollow", true)] },
    { id: "M02", spec: (r, c) => ({ t: ["circle", "square", "hex"][r], s: [54, 36, 20][c], f: "none" }), draw: (p) => [E(p.t, p)],
      wrong: [P("s", 54), P("t", "square"), P("f", "gray")] },
    { id: "M03", spec: (r, c) => ({ t: ["square", "circle", "diamond"][r], f: ["none", "gray", "black"][c], s: 48 }), draw: (p) => [E(p.t, p)],
      wrong: [P("f", "gray"), P("t", "circle"), P("s", 28)] },
    { id: "M04", spec: (r, c) => ({ r: [0, 90, 180][r] + 45 * c, f: "black", s: 50 }), draw: (p) => [E("arrow", p)],
      wrong: [P("r", 90), P("f", "none"), P("s", 30)] },
    { id: "M05", spec: (r, c) => ({ t: [["circle", "square", "tri"], ["square", "tri", "circle"], ["tri", "circle", "square"]][r][c], f: ["none", "gray", "black"][r], s: 46 }),
      draw: (p) => [E(p.t, p)], wrong: [P("t", "tri"), P("f", "gray"), P("s", 28)] },
    { id: "M06", spec: (r, c) => ({ p: (r + c) % 4, t: "circle", f: "black" }),
      draw: (p) => [E(p.t, { x: CORNER[p.p][0], y: CORNER[p.p][1], s: 26, f: p.f })],
      wrong: [P("p", 2), P("t", "square"), P("f", "none")] },
    { id: "M07", spec: (r, c) => ({ t: [["tri", "circle", "square"], ["circle", "square", "tri"], ["square", "tri", "circle"]][r][c], n: c + 1, f: ["none", "gray", "black"][r] }),
      draw: (p) => many(p.n, { t: p.t, f: p.f }), wrong: [P("n", 2), P("f", "gray"), P("t", "square")] },
    { id: "M08", spec: (r, c) => ({ L: [[["H"], ["V"], ["H", "V"]], [["T", "B"], ["L", "R"], ["T", "B", "L", "R"]], [["D1", "D2"], ["H"], ["D1", "D2", "H"]]][r][c] }),
      draw: (p) => segs(p.L), prep: (p) => set(p, "L", new Set(p.L)), wrong: [T("L", "H"), T("L", "V"), T("L", "T")] },

    // ---- 標準（9〜18）----
    { id: "M09", spec: (r, c) => ({ L: [[["H", "T", "L"], ["H", "B"], ["T", "L", "B"]], [["V", "D1", "R"], ["V", "D2"], ["D1", "R", "D2"]], [["T", "B", "D1", "H"], ["T", "D1", "L"], ["B", "H", "L"]]][r][c] }),
      draw: (p) => segs(p.L), prep: (p) => set(p, "L", new Set(p.L)), wrong: [T("L", "T"), T("L", "D1"), T("L", "R")] },
    { id: "M10", spec: (r, c) => ({ D: [[[0, 1, 2, 4], [1, 4], [0, 2]], [[0, 3, 6, 7, 8], [3, 7], [0, 6, 8]], [[2, 4, 5, 6, 8], [4, 8], [2, 5, 6]]][r][c] }),
      draw: (p) => dots(p.D), prep: (p) => set(p, "D", new Set(p.D)), wrong: [T("D", 2), T("D", 4), T("D", 8)] },
    { id: "M11", spec: (r, c) => ({ t: ["circle", "square", "star"][r], n: [[1, 3, 4], [2, 1, 3], [2, 3, 5]][r][c] }),
      draw: (p) => many(p.n, { t: p.t, f: p.f || "none" }), wrong: [P("n", 6), P("t", "square"), P("f", "black")] },
    { id: "M12", spec: (r, c) => ({ r: [0, 45, 90][r] + 90 * c, f: [["none", "gray", "black"], ["gray", "black", "none"], ["black", "none", "gray"]][r][c], s: 50 }),
      draw: (p) => [E("arrow", p)], wrong: [P("r", 90), P("f", "black"), P("s", 30)] },
    { id: "M13", spec: (r, c) => ({ o: ["circle", "square", "hex"][r], i: [["tri", "star", "square"], ["star", "square", "tri"], ["square", "tri", "star"]][r][c], f: "black" }),
      draw: (p) => [E(p.o, { s: 76 }), E(p.i, { s: 30, f: p.f })], wrong: [P("o", "circle"), P("i", "tri"), P("f", "none")] },
    { id: "M14", spec: (r, c) => ({ t: ["circle", "diamond", "pent"][r], n: [3, 2, 1][c], s: [16, 26, 40][c], f: ["black", "none", "gray"][r] }),
      draw: (p) => many(p.n, { t: p.t, s: p.s, f: p.f }), wrong: [P("n", 2), P("s", 16), P("t", "diamond")] },
    { id: "M15", spec: (r, c) => ({ a: ([0, 1, 2][r] + c) % 4, b: (([1, 0, 1][r] - c) % 4 + 4) % 4, fa: "black" }),
      draw: (p) => [E("circle", { x: CORNER[p.a][0], y: CORNER[p.a][1], s: 26, f: p.fa }), E("square", { x: CORNER[p.b][0], y: CORNER[p.b][1], s: 24, f: "gray" })],
      wrong: [P("a", 2), P("b", 1), P("fa", "none")] },
    { id: "M16", spec: (r, c) => ({
        t: [["circle", "square", "tri"], ["tri", "circle", "square"], ["square", "tri", "circle"]][r][c],
        f: [["none", "gray", "black"], ["gray", "black", "none"], ["black", "none", "gray"]][r][c],
        n: [[2, 3, 1], [3, 1, 2], [1, 2, 3]][r][c] }),
      draw: (p) => many(p.n, { t: p.t, f: p.f }), wrong: [P("t", "tri"), P("f", "black"), P("n", 1)] },
    { id: "M17", spec: (r, c) => ({ r: [0, 90, 45][r] + [45, 90, 135][r] * c, f: ["none", "gray", "black"][c], s: 50 }),
      draw: (p) => [E("arrow", p)], wrong: [P("r", 270), P("f", "gray"), P("s", 30)] },
    { id: "M18", spec: (r, c) => ({ D: [[[0, 2, 4, 6], [0, 4, 5, 8], [0, 4]], [[1, 3, 4, 7], [1, 2, 7, 8], [1, 7]], [[0, 2, 5, 6, 8], [2, 3, 6, 7, 8], [2, 6, 8]]][r][c] }),
      draw: (p) => dots(p.D), prep: (p) => set(p, "D", new Set(p.D)), wrong: [T("D", 5), T("D", 0), T("D", 6)] },

    // ---- 発展（19〜30）----
    { id: "M19", spec: (r, c) => ({ t: ["circle", "star", "diamond"][c], n: r + 1, f: [["black", "none", "gray"], ["none", "gray", "black"], ["gray", "black", "none"]][r][c] }),
      draw: (p) => many(p.n, { t: p.t, f: p.f }), wrong: [P("n", 2), P("t", "star"), P("f", "black")] },
    { id: "M20", spec: (r, c) => ({ o: [["circle", "square", "hex"], ["square", "hex", "circle"], ["hex", "circle", "square"]][r][c], r: ([0, 90, 180][r] + 90 * c) % 360, f: ["black", "gray", "none"][r] }),
      draw: (p) => [E(p.o, { s: 78 }), E("arrow", { s: 36, r: p.r, f: p.f })], wrong: [P("o", "hex"), P("r", 180), P("f", "black")] },
    { id: "M21", spec: (r, c) => ({ S: [[[0, 2, 4], [2, 6], [0, 4, 6]], [[1, 3, 5, 7], [3, 7, 0], [1, 5, 0]], [[0, 1, 2, 6], [1, 4, 6], [0, 2, 4]]][r][c] }),
      draw: (p) => spokes(p.S), prep: (p) => set(p, "S", new Set(p.S)), wrong: [T("S", 1), T("S", 6), T("S", 3)] },
    { id: "M22", spec: (r, c) => ({ t: ["tri", "circle", "square"][r], n: [[5, 2, 3], [1, 4, 3], [6, 2, 4]][r][c], f: ["none", "black", "gray"][c] }),
      draw: (p) => many(p.n, { t: p.t, f: p.f }), wrong: [P("n", 8), P("f", "black"), P("t", "circle")] },
    { id: "M23", spec: (r, c) => ({ a: ([0, 3, 6][r] + c) % 8, b: ([4, 0, 2][r] + 2 * c) % 8, fb: "gray" }),
      draw: (p) => { const [ax, ay] = ring(p.a), [bx, by] = ring(p.b); return [E("circle", { x: ax, y: ay, s: 18, f: "black" }), E("square", { x: bx, y: by, s: 17, f: p.fb })]; },
      wrong: [P("a", 7), P("b", 4), P("fb", "black")] },
    { id: "M24", spec: (r, c) => ({ t: ["circle", "tri", "star"][(r + c) % 3], f: ["black", "none", "gray"][((c - r) % 3 + 3) % 3], r: 0 }),
      draw: (p) => [E(p.t, { s: 50, f: p.f, r: p.r })], wrong: [P("t", "star"), P("f", "gray"), P("r", 180)] },
    { id: "M25", spec: (r, c) => ({ n: 3 + r + c, f: ["none", "stripe", "gray"][c], s: 60 }),
      draw: (p) => [E("poly", { n: p.n, s: p.s, f: p.f })], wrong: [P("n", 6), P("f", "none"), P("s", 38)] },
    { id: "M26", spec: (r, c) => ({ r: (([0, 90, 180][r] - 90 * c) % 360 + 360) % 360, d: ([0, 3, 6][r] + c) % 8, fd: "black" }),
      draw: (p) => { const [x, y] = ring(p.d, 41); return [E("arrow", { s: 40, r: p.r, f: "none" }), E("circle", { x, y, s: 12, f: p.fd })]; },
      wrong: [P("r", 180), P("d", 4), P("fd", "none")] },
    { id: "M27", spec: (r, c) => {
        const row = [[["circle", 2], ["square", 1]], [["tri", 3], ["circle", 2]], [["square", 1], ["tri", 3]]][r];
        if (c < 2) return { t: row[c][0], n: row[c][1], f: ["black", "none"][c] };
        return { t: row[1][0], n: row[0][1] + row[1][1], f: "gray" };
      },
      draw: (p) => many(p.n, { t: p.t, f: p.f }), wrong: [P("n", 3), P("t", "square"), P("f", "none")] },
    { id: "M28", spec: (r, c) => {
        const base = [[0, 4], [1, 3, 8], [0, 6, 7]][r];
        return { D: base.map((k) => Math.floor(k / 3) * 3 + (k % 3 + c) % 3) };
      },
      draw: (p) => dots(p.D), prep: (p) => set(p, "D", new Set(p.D)), wrong: [T("D", 7), T("D", 6), T("D", 0)] },
    { id: "M29", spec: (r, c) => ({ lt: SH[r], lf: ["none", "gray", "black"][c], rt: ["star", "diamond", "hex"][c], rf: ["none", "gray", "black"][r] }),
      draw: (p) => [E(p.lt, { x: 30, s: 32, f: p.lf }), E(p.rt, { x: 72, s: 32, f: p.rf })], wrong: [P("lf", "gray"), P("rt", "diamond"), P("rf", "gray")] },
    { id: "M30", spec: (r, c) => ({
        r: [[45, 90, 135], [90, 180, 270], [180, 135, 315]][r][c],
        C: [[[0, 1], [1, 2], [0, 2]], [[0, 3, 2], [0, 1], [1, 3, 2]], [[1, 2], [1, 3, 0], [2, 3, 0]]][r][c] }),
      draw: (p) => [E("arrow", { s: 46, r: p.r, f: "black" }), ...[...p.C].map((k) => E("circle", { x: CORNER_OUT[k][0], y: CORNER_OUT[k][1], s: 14, f: "black" }))],
      prep: (p) => set(p, "C", new Set(p.C)), wrong: [P("r", 45), T("C", 1), T("C", 2)] }
  ];

  // 練習問題（採点対象外）
  const PRACTICE = {
    id: "P00", spec: (r, c) => ({ t: ["circle", "square", "diamond"][r], f: ["none", "gray", "black"][c], s: 46 }),
    draw: (p) => [E(p.t, p)], wrong: [P("f", "none"), P("t", "square"), P("s", 26)]
  };

  /* ---------- 問題の展開 ---------- */
  function build(item) {
    const prep = item.prep || ((p) => p);
    const cells = [];
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) cells.push(item.draw(prep(item.spec(r, c))));
    const ans = prep(item.spec(2, 2));
    const options = [];
    for (let m = 0; m < 8; m++) {
      let p = ans;
      item.wrong.forEach((w, i) => { if (m & (1 << i)) p = w(p); });
      options.push(item.draw(p));
    }
    return { id: item.id, cells, options, answer: 0 }; // options[0] が正解（表示時にシャッフル）
  }

  /* ---------- 描画 ---------- */
  const fillOf = (f) => f === "black" ? INK : f === "gray" ? GRAY : f === "stripe" ? "url(#hatch)" : PAPER;
  function polyPts(n, x, y, rad, start = -90) {
    const pts = [];
    for (let k = 0; k < n; k++) { const a = (start + k * 360 / n) * Math.PI / 180; pts.push(`${(x + rad * Math.cos(a)).toFixed(2)},${(y + rad * Math.sin(a)).toFixed(2)}`); }
    return pts.join(" ");
  }
  const POLY_N = { tri: 3, diamond: 4, pent: 5, hex: 6 };
  function shapeSVG(e) {
    if (e.t === "seg") return `<line x1="${e.x1}" y1="${e.y1}" x2="${e.x2}" y2="${e.y2}" stroke="${INK}" stroke-width="3.2" stroke-linecap="round"/>`;
    const { x, y, s, r } = e, h = s / 2;
    const st = `fill="${fillOf(e.f)}" stroke="${INK}" stroke-width="2.4" stroke-linejoin="round"`;
    const rot = r ? ` transform="rotate(${r} ${x} ${y})"` : "";
    switch (e.t) {
      case "circle": return `<circle cx="${x}" cy="${y}" r="${h}" ${st}/>`;
      case "square": return `<rect x="${x - h}" y="${y - h}" width="${s}" height="${s}" ${st}${rot}/>`;
      case "star": {
        const pts = [];
        for (let k = 0; k < 10; k++) { const a = (-90 + k * 36) * Math.PI / 180, rr = k % 2 ? h * 0.42 : h; pts.push(`${(x + rr * Math.cos(a)).toFixed(2)},${(y + rr * Math.sin(a)).toFixed(2)}`); }
        return `<polygon points="${pts.join(" ")}" ${st}${rot}/>`;
      }
      case "arrow": {
        const P = [[0, -1], [0.72, -0.15], [0.26, -0.15], [0.26, 1], [-0.26, 1], [-0.26, -0.15], [-0.72, -0.15]];
        return `<polygon points="${P.map(([a, b]) => `${(x + a * h).toFixed(2)},${(y + b * h).toFixed(2)}`).join(" ")}" ${st}${rot}/>`;
      }
      case "poly": return `<polygon points="${polyPts(e.n, x, y, h)}" ${st}${rot}/>`;
      default: return `<polygon points="${polyPts(POLY_N[e.t], x, y, h)}" ${st}${rot}/>`;
    }
  }
  function cellSVG(els, extra = "") {
    return `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" ${extra}>
      <defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="${PAPER}"/><line x1="0" y1="0" x2="0" y2="6" stroke="${INK}" stroke-width="2"/></pattern></defs>
      ${els.map(shapeSVG).join("")}</svg>`;
  }

  /* ---------- 同一判定用キー（見た目が同じなら同じキー） ---------- */
  function elKey(e) {
    if (e.t === "seg") {
      const a = `${Math.round(e.x1)},${Math.round(e.y1)}`, b = `${Math.round(e.x2)},${Math.round(e.y2)}`;
      return "seg:" + [a, b].sort().join("-");
    }
    const sym = { circle: 1, square: 90, star: 72, arrow: 360, poly: 360 / e.n, tri: 120, diamond: 90, pent: 72, hex: 60 }[e.t];
    const r = sym === 1 ? 0 : ((Math.round(e.r) % sym) + sym) % sym;
    const t = e.t === "poly" ? `poly${e.n}` : e.t === "diamond" ? "poly4" : e.t === "tri" ? "poly3" : e.t === "pent" ? "poly5" : e.t === "hex" ? "poly6" : e.t;
    return `${t}:${Math.round(e.x)},${Math.round(e.y)},${Math.round(e.s)},${e.f},${Math.round(r * 10) / 10}`;
  }
  const cellKey = (els) => els.map(elKey).sort().join("|");

  const API = { ITEMS, PRACTICE, build, cellSVG, cellKey };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.MatrixItems = API;
})(typeof window !== "undefined" ? window : globalThis);
