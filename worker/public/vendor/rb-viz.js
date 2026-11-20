/* rb-viz: https://github.com/rockybranches/rb-viz */
var RBViz = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // js/index.js
  var index_exports = {};
  __export(index_exports, {
    BAND_COLORS: () => BAND_COLORS,
    BASEMAPS: () => BASEMAPS,
    CATEGORICAL: () => CATEGORICAL,
    LITHOLOGY_COLORS: () => LITHOLOGY_COLORS,
    PLOT_CONFIG: () => PLOT_CONFIG,
    SEQUENTIAL: () => SEQUENTIAL,
    SERIES: () => SERIES,
    TOKENS: () => TOKENS,
    addBasemaps: () => addBasemaps,
    axis: () => axis,
    bandedArea: () => bandedArea,
    baseLayout: () => baseLayout,
    bindThemeToggle: () => bindThemeToggle,
    buttonControl: () => buttonControl,
    categoricalScale: () => categoricalScale,
    categoryShares: () => categoryShares,
    closeLightbox: () => closeLightbox,
    collarTraces: () => collarTraces,
    colorbar: () => colorbar,
    colorscale: () => colorscale,
    compareCells: () => compareCells,
    compositionBar: () => compositionBar,
    correlationHeatmap: () => correlationHeatmap,
    correlationHeight: () => correlationHeight,
    crossPlot: () => crossPlot,
    currentScheme: () => currentScheme,
    currentTheme: () => currentTheme,
    dataTable: () => dataTable,
    divergingColorscale: () => divergingColorscale,
    downloadMapPng: () => downloadMapPng,
    draw: () => draw,
    esc: () => esc,
    fitText: () => fitText,
    fixed: () => fixed,
    fmt: () => fmt,
    gallery: () => gallery,
    gradedPoints: () => gradedPoints,
    hashFor: () => hashFor,
    hashRouter: () => hashRouter,
    holes3d: () => holes3d,
    imageOverlay: () => imageOverlay,
    initTheme: () => initTheme,
    intervalAt: () => intervalAt,
    labeledPin: () => labeledPin,
    leaflet: () => leaflet,
    legendControl: () => legendControl,
    lineOverlay: () => lineOverlay,
    lithologyColor: () => lithologyColor,
    log10: () => log10,
    logHistogram: () => logHistogram,
    matrixHeatmap: () => matrixHeatmap,
    onDepthPick: () => onDepthPick,
    onPointClick: () => onPointClick,
    openLightbox: () => openLightbox,
    parseHash: () => parseHash,
    planView: () => planView,
    plural: () => plural,
    quantileLogScale: () => quantileLogScale,
    rankedBars: () => rankedBars,
    renderMapPng: () => renderMapPng,
    scoresMatrix: () => scoresMatrix,
    setActiveNav: () => setActiveNav,
    showEmpty: () => showEmpty,
    slug: () => slug,
    statTiles: () => statTiles,
    stepRuns: () => stepRuns,
    stepSeries: () => stepSeries,
    stripLog: () => stripLog,
    stripLogHeight: () => stripLogHeight,
    surfaceTrace: () => surfaceTrace,
    themeFor: () => themeFor,
    toggleTheme: () => toggleTheme,
    traceOffset: () => traceOffset
  });

  // js/tokens.js
  var TOKENS = {
    "light": {
      "page": "#f9f9f7",
      "surface": "#fcfcfb",
      "surface-2": "#f2f1ed",
      "ink": "#0b0b0b",
      "ink-2": "#4c5753",
      "muted": "#626b66",
      "grid": "#e4dfd4",
      "axis": "#c3c2b7",
      "border": "rgba(11, 11, 11, 0.10)",
      "accent": "#1c5cab",
      "series-1": "#2a78d6",
      "series-2": "#eb6834",
      "series-3": "#1baf7a",
      "diverge-mid": "#f0efec",
      "diverge-neg": "#2a78d6",
      "diverge-pos": "#e34948",
      "header": "#13233a",
      "header-ink": "#f0efec",
      "shadow": "0 1px 2px rgba(0,0,0,.04), 0 4px 16px rgba(0,0,0,.05)"
    },
    "dark": {
      "page": "#0d0d0d",
      "surface": "#1a1a19",
      "surface-2": "#232321",
      "ink": "#f0efec",
      "ink-2": "#c3c2b7",
      "muted": "#898781",
      "grid": "#2c2c2a",
      "axis": "#383835",
      "border": "rgba(255,255,255,0.10)",
      "accent": "#6da7ec",
      "series-1": "#3987e5",
      "series-2": "#d95926",
      "series-3": "#199e70",
      "diverge-mid": "#383835",
      "diverge-neg": "#3987e5",
      "diverge-pos": "#e66767",
      "header": "#101826",
      "header-ink": "#f0efec",
      "shadow": "none"
    },
    "sequential": [
      "#cde2fb",
      "#9ec5f4",
      "#6da7ec",
      "#3987e5",
      "#256abf",
      "#1c5cab",
      "#104281"
    ],
    "series": [
      "#2a78d6",
      "#eb6834",
      "#1baf7a",
      "#eda100",
      "#e87ba4",
      "#008300"
    ],
    "categorical": [
      "#2a78d6",
      "#eb6834",
      "#1baf7a",
      "#e3a008",
      "#8f5bd6",
      "#e34948",
      "#6b8e23",
      "#0ea5b7",
      "#b8860b",
      "#c2185b",
      "#5d6d7e",
      "#a0522d"
    ],
    "bands": [
      "#0b3d91",
      "#2166ac",
      "#4393c3",
      "#74add1",
      "#abd9e9"
    ],
    "lithology": {
      "Alluvium": "#eadb9f",
      "Sandstone": "#f1c062",
      "Calcareous Sandstone": "#d8c48d",
      "Quartzite": "#f3e3c0",
      "Siltstone": "#b39a76",
      "Mudstone": "#8e877b",
      "Siliceous Mudstone": "#6f7c8d",
      "Shale": "#5b5b5b",
      "Chert": "#7d9db7",
      "Fault Breccia": "#c4504c",
      "Sedimentary Breccia": "#d48d6e",
      "Intermediate Igneous Rock": "#76a66f",
      "Felsic Igneous Rock": "#e2a0b8",
      "Mafic Igneous Rock": "#3f6b3f",
      "Greenstone": "#4f7f5f",
      "Limestone": "#9fc5e8",
      "Barite": "#c9b8e8",
      "Vein": "#fafafa",
      "No Data": "#d9d9d9"
    },
    "lithology-fallback": "#cccccc",
    "font": 'system-ui, -apple-system, "Segoe UI", sans-serif'
  };

  // js/format.js
  var ENTITIES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  var esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ENTITIES[c]);
  function fmt(v, digits = 3) {
    if (v == null || typeof v === "number" && Number.isNaN(v)) return "\u2013";
    if (typeof v !== "number") return esc(v);
    if (Math.abs(v) >= 1e3) return Math.round(v).toLocaleString("en-US");
    if (v === 0) return "0";
    return Number(v.toPrecision(digits)).toString();
  }
  var fixed = (v, decimals = 0) => v == null ? "\u2013" : Number(v).toLocaleString("en-US", { maximumFractionDigits: decimals });
  var plural = (n, word) => `${n.toLocaleString("en-US")} ${word}${n === 1 ? "" : "s"}`;
  var log10 = (v) => v != null && v > 0 ? Math.log10(v) : null;
  var slug = (s) => String(s).replace(/[^\w.-]+/g, "_");

  // js/theme.js
  function build(get) {
    const series = [get("series-1"), get("series-2"), get("series-3"), ...TOKENS.series.slice(3)];
    return {
      page: get("page"),
      surface: get("surface"),
      surface2: get("surface-2"),
      ink: get("ink"),
      ink2: get("ink-2"),
      muted: get("muted"),
      grid: get("grid"),
      axis: get("axis"),
      border: get("border"),
      accent: get("accent"),
      header: get("header"),
      series,
      divergeNeg: get("diverge-neg"),
      divergeMid: get("diverge-mid"),
      divergePos: get("diverge-pos"),
      sequential: get("seq") ?? TOKENS.sequential,
      font: TOKENS.font
    };
  }
  function themeFor(scheme = "light") {
    const set = TOKENS[scheme === "dark" ? "dark" : "light"];
    return build((name) => name === "seq" ? TOKENS.sequential : set[name]);
  }
  function currentScheme(root = globalThis.document?.documentElement) {
    const set = root?.dataset?.theme;
    if (set === "light" || set === "dark") return set;
    return globalThis.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function currentTheme(root = globalThis.document?.documentElement) {
    const fallback = TOKENS[currentScheme(root)];
    if (!root || !globalThis.getComputedStyle) return themeFor(currentScheme(root));
    const style = globalThis.getComputedStyle(root);
    return build((name) => {
      const value = style.getPropertyValue(`--${name}`).trim();
      if (name === "seq") return value ? value.split(",").map((s) => s.trim()) : TOKENS.sequential;
      return value || fallback[name];
    });
  }
  function initTheme(storageKey = "rb-viz-theme", root = document.documentElement) {
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved === "light" || saved === "dark") root.dataset.theme = saved;
    } catch {
    }
  }
  function toggleTheme(storageKey = "rb-viz-theme", root = document.documentElement) {
    const next = currentScheme(root) === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try {
      localStorage.setItem(storageKey, next);
    } catch {
    }
    return next;
  }
  function bindThemeToggle(button, { storageKey = "rb-viz-theme", onChange } = {}) {
    const sync = () => button.setAttribute("aria-pressed", String(currentScheme() === "dark"));
    sync();
    button.addEventListener("click", () => {
      const scheme = toggleTheme(storageKey);
      sync();
      onChange?.(scheme);
    });
  }

  // js/colors.js
  var SERIES = TOKENS.series;
  var CATEGORICAL = TOKENS.categorical;
  var SEQUENTIAL = TOKENS.sequential;
  var BAND_COLORS = TOKENS.bands;
  var LITHOLOGY_COLORS = TOKENS.lithology;
  var lithologyColor = (name) => LITHOLOGY_COLORS[name] ?? TOKENS["lithology-fallback"];
  function categoricalScale(palette = CATEGORICAL, known = {}) {
    const seen = /* @__PURE__ */ new Map();
    return (value) => {
      const key = String(value);
      if (known[key]) return known[key];
      if (!seen.has(key)) seen.set(key, palette[seen.size % palette.length]);
      return seen.get(key);
    };
  }
  var colorscale = (steps = SEQUENTIAL) => steps.map((c, i) => [steps.length === 1 ? 0 : i / (steps.length - 1), c]);
  var divergingColorscale = (theme) => [[0, theme.divergeNeg], [0.5, theme.divergeMid], [1, theme.divergePos]];
  function quantileLogScale(values, { steps = SEQUENTIAL, low = 0.05, high = 0.95, missing = TOKENS.light.muted } = {}) {
    const logs = values.map(log10).filter((v) => v != null).sort((a, b) => a - b);
    if (!logs.length) return null;
    const q = (p) => logs[Math.min(logs.length - 1, Math.floor(p * (logs.length - 1)))];
    const lo = q(low), hi = Math.max(q(high), lo + 1e-9);
    const t = (v) => {
      const l = log10(v);
      return l == null ? null : Math.min(1, Math.max(0, (l - lo) / (hi - lo)));
    };
    const color = (pos) => pos == null ? missing : steps[Math.round(pos * (steps.length - 1))];
    return { lo, hi, flat: hi - lo <= 1e-6, t, color, colorOf: (v) => color(t(v)), value: (pos) => 10 ** (lo + pos * (hi - lo)) };
  }

  // js/plotting.js
  function axis(extra = {}, theme = currentTheme()) {
    return {
      gridcolor: theme.grid,
      linecolor: theme.axis,
      zerolinecolor: theme.axis,
      tickfont: { color: theme.ink2, size: 11 },
      ...extra,
      title: { font: { color: theme.ink2, size: 12 }, ...titleOf(extra.title) }
    };
  }
  var titleOf = (title) => typeof title === "string" ? { text: title } : title ?? {};
  function baseLayout(extra = {}, theme = currentTheme()) {
    return {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: { family: theme.font, color: theme.ink2, size: 12 },
      margin: { l: 56, r: 16, t: 16, b: 44 },
      xaxis: axis({}, theme),
      yaxis: axis({}, theme),
      hoverlabel: { bgcolor: theme.surface, bordercolor: theme.axis, font: { color: theme.ink, size: 12 } },
      legend: { orientation: "h", y: -0.18, font: { color: theme.ink2 } },
      ...extra
    };
  }
  var colorbar = (theme, extra = {}) => ({ thickness: 12, tickfont: { color: theme.ink2 }, ...extra });
  var PLOT_CONFIG = { displaylogo: false, responsive: true, modeBarButtonsToRemove: ["select2d", "lasso2d", "autoScale2d"] };
  var resolve = (el) => typeof el === "string" ? document.getElementById(el) : el;
  function showEmpty(el, message) {
    const node = resolve(el);
    globalThis.Plotly?.purge?.(node);
    const p = document.createElement("p");
    p.className = "empty";
    p.textContent = message;
    node.replaceChildren(p);
    node.style.minHeight = "0";
  }
  function draw(el, spec, config = {}) {
    const node = resolve(el);
    const { Plotly = globalThis.Plotly, ...rest } = config;
    if (!Plotly) {
      showEmpty(node, "Charts need Plotly, which could not be loaded (offline?).");
      return null;
    }
    if (node.querySelector(":scope > p.empty")) {
      node.replaceChildren();
      node.style.minHeight = "";
    }
    return Plotly.react(node, spec.data, spec.layout, { ...PLOT_CONFIG, ...spec.config, ...rest });
  }
  function onPointClick(el, handler) {
    const node = resolve(el);
    if (!node?.on) return;
    node.removeAllListeners?.("plotly_click");
    node.on("plotly_click", (ev) => {
      const p = ev.points?.[0];
      if (p) handler(p, ev);
    });
  }

  // js/charts/striplog.js
  var base = (iv) => iv.to ?? iv.from;
  var mid = (iv) => (iv.from + base(iv)) / 2;
  function stepSeries(intervals, tolerance = 1e-6) {
    const x = [], y = [];
    let last = null;
    for (const iv of intervals) {
      if (iv.value == null) {
        x.push(null);
        y.push(null);
        last = null;
        continue;
      }
      if (last != null && Math.abs(last - iv.from) > tolerance) {
        x.push(null);
        y.push(null);
      }
      x.push(iv.value, iv.value);
      y.push(iv.from, base(iv));
      last = base(iv);
    }
    return { x, y };
  }
  function stepRuns(intervals, tolerance = 1e-6) {
    const { x, y } = stepSeries(intervals, tolerance);
    const runs = [];
    let run = null;
    for (let i = 0; i < x.length; i++) {
      if (x[i] == null) {
        run = null;
        continue;
      }
      if (!run) runs.push(run = { x: [], y: [] });
      run.x.push(x[i]);
      run.y.push(y[i]);
    }
    return runs;
  }
  function stripLog(tracks, { depthTitle = "Depth", selected = null, maxTracks = Infinity, theme = currentTheme() } = {}) {
    let kept = 0;
    tracks = tracks.filter((t) => t.type === "category" || kept++ < maxTracks);
    const all = tracks.flatMap((t) => t.intervals);
    const bottom = all.length ? Math.max(...all.map(base)) : 1;
    const top = all.length ? Math.min(...all.map((iv) => iv.from)) : 0;
    const pad = Math.max(1, (bottom - top) * 0.01);
    const layout = baseLayout({ margin: { l: 58, r: 8, t: 34, b: 30 }, showlegend: false, hovermode: "y unified", dragmode: "zoom", bargap: 0 }, theme);
    layout.yaxis = axis({
      range: [bottom + pad, Math.min(0, top) - pad],
      zeroline: false,
      title: depthTitle,
      showspikes: true,
      spikemode: "across",
      spikethickness: 1,
      spikecolor: theme.muted,
      spikedash: "solid"
    }, theme);
    const widths = tracks.map((t) => t.width ?? (t.type === "category" ? 0.7 : 1));
    const total = widths.reduce((a, b) => a + b, 0) || 1;
    const gap = 0.012;
    const data = [];
    let x0 = 0;
    tracks.forEach((t, i) => {
      const xa = i === 0 ? "x" : `x${i + 1}`, key = i === 0 ? "xaxis" : `xaxis${i + 1}`;
      const w = widths[i] / total;
      layout[key] = axis({
        domain: [x0, Math.min(1, x0 + w - gap)],
        anchor: "y",
        side: "top",
        fixedrange: true,
        title: { text: esc(t.title), font: { size: 11, color: theme.ink }, standoff: 4 },
        tickfont: { size: 10, color: theme.ink2 }
      }, theme);
      x0 += w;
      if (t.type === "category") {
        Object.assign(layout[key], { showticklabels: false, range: [0, 1], showgrid: false, zeroline: false });
        const rows = t.intervals.filter((iv) => iv.label != null && iv.label !== "");
        data.push({
          type: "bar",
          orientation: "h",
          xaxis: xa,
          yaxis: "y",
          x: rows.map(() => 1),
          y: rows.map(mid),
          width: rows.map((iv) => base(iv) - iv.from || 1),
          marker: { color: rows.map((iv) => t.color(iv.label)), line: { width: 0 } },
          customdata: rows.map((iv) => esc(iv.detail ? `${iv.label}, ${iv.detail}` : iv.label)),
          hovertemplate: "%{customdata}<extra></extra>"
        });
        return;
      }
      const color = t.color ?? theme.series[0];
      if (t.range) layout[key].range = t.range;
      const values = t.intervals.map((iv) => iv.value).filter((v) => v != null);
      if (t.log && values.length && values.every((v) => v > 0)) layout[key].type = "log";
      for (const run of stepRuns(t.intervals)) {
        data.push({
          type: "scatter",
          mode: "lines",
          xaxis: xa,
          yaxis: "y",
          x: run.x,
          y: run.y,
          line: { color, width: 1.5 },
          fill: "tozerox",
          fillcolor: withAlpha(color, 0.2),
          hoverinfo: "skip"
        });
      }
      data.push({
        type: "scatter",
        mode: "markers",
        xaxis: xa,
        yaxis: "y",
        x: t.intervals.map((iv) => iv.value),
        y: t.intervals.map(mid),
        marker: { size: 8, opacity: 0 },
        customdata: t.intervals.map((iv) => iv.note ? ` (${esc(iv.note)})` : ""),
        hovertemplate: `${esc(t.name ?? t.title)} %{x}%{customdata}<extra></extra>`
      });
    });
    if (selected != null) {
      layout.shapes = [{ type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: selected, y1: selected, line: { color: theme.divergePos, width: 2 } }];
    }
    return { data, layout, config: { scrollZoom: false } };
  }
  function withAlpha(color, alpha) {
    if (!/^#[0-9a-f]{6}$/i.test(color)) return color;
    return color + Math.round(alpha * 255).toString(16).padStart(2, "0");
  }
  function onDepthPick(el, handler, { step: step2 = 0.01 } = {}) {
    onPointClick(el, (p) => {
      if (p.y != null) handler(Math.round(p.y / step2) * step2);
    });
  }
  var stripLogHeight = (n) => Math.min(1400, Math.max(560, 14 * n + 120));
  function intervalAt(intervals, depth) {
    return intervals.find((iv) => iv.from <= depth && depth < base(iv)) ?? intervals.reduce((best, iv) => !best || Math.abs(iv.from - depth) < Math.abs(best.from - depth) ? iv : best, null);
  }
  function categoryShares(intervals) {
    const length = /* @__PURE__ */ new Map();
    for (const iv of intervals) {
      if (iv.label == null || iv.label === "") continue;
      const key = String(iv.label);
      length.set(key, (length.get(key) ?? 0) + (base(iv) - iv.from || 1));
    }
    return [...length].map(([name, len]) => ({ name, length: len })).sort((a, b) => b.length - a.length);
  }

  // js/charts/heatmaps.js
  function correlationHeatmap({ labels, matrix }, { theme = currentTheme(), margin } = {}) {
    return {
      data: [{
        type: "heatmap",
        z: matrix,
        x: labels,
        y: labels,
        zmin: -1,
        zmax: 1,
        xgap: 1,
        ygap: 1,
        colorscale: divergingColorscale(theme),
        colorbar: colorbar(theme, { title: { text: "r" } }),
        hovertemplate: "%{y} \u2013 %{x}: r = %{z:.2f}<extra></extra>"
      }],
      layout: baseLayout({
        margin: margin ?? { l: 60, r: 10, t: 10, b: 60 },
        xaxis: axis({ side: "bottom", showgrid: false, type: "category" }, theme),
        yaxis: axis({ autorange: "reversed", showgrid: false, type: "category" }, theme)
      }, theme)
    };
  }
  var correlationHeight = (n) => Math.min(760, Math.max(320, 22 * n + 120));
  function matrixHeatmap({ rows, columns, values }, { theme = currentTheme(), valueTitle, margin } = {}) {
    return {
      data: [{
        type: "heatmap",
        x: columns,
        y: rows,
        z: values,
        colorscale: colorscale(theme.sequential),
        xgap: 1,
        ygap: 1,
        colorbar: colorbar(theme, valueTitle ? { title: { text: valueTitle } } : {}),
        hovertemplate: "%{y} \xB7 %{x}: %{z:.3f}<extra></extra>"
      }],
      layout: baseLayout({
        margin: margin ?? { l: 90, r: 10, t: 10, b: 40 },
        xaxis: axis({ showgrid: false, type: "category" }, theme),
        yaxis: axis({ showgrid: false, type: "category", autorange: "reversed" }, theme)
      }, theme)
    };
  }
  function scoresMatrix(groups) {
    const keys = [...new Set(groups.flatMap((g) => Object.keys(g.scores)))];
    const mean = (k) => groups.reduce((s, g) => s + (g.scores[k] ?? 0), 0) / groups.length;
    const columns = keys.sort((a, b) => mean(b) - mean(a));
    return { rows: groups.map((g) => g.name), columns, values: groups.map((g) => columns.map((k) => g.scores[k] ?? null)) };
  }

  // js/charts/bars.js
  function rankedBars(items, { valueTitle, limit = 14, sort = true, theme = currentTheme(), labelWidth } = {}) {
    let rows = Array.isArray(items) ? items.slice() : Object.entries(items).map(([label, value]) => ({ label, value }));
    rows = rows.filter((r) => r.value != null && !Number.isNaN(r.value));
    if (sort) rows.sort((a, b) => b.value - a.value);
    rows = rows.slice(0, limit).reverse();
    const longest = rows.reduce((n, r) => Math.max(n, String(r.label).length), 0);
    return {
      data: [{
        type: "bar",
        orientation: "h",
        x: rows.map((r) => r.value),
        y: rows.map((r) => String(r.label)),
        marker: { color: theme.series[0] },
        hovertemplate: "%{y}: %{x:.3f}<extra></extra>"
      }],
      layout: baseLayout({
        margin: { l: labelWidth ?? Math.max(44, 12 + 7 * longest), r: 16, t: 8, b: 40 },
        bargap: 0.35,
        xaxis: axis({ title: valueTitle }, theme),
        yaxis: axis({ showgrid: false, type: "category" }, theme)
      }, theme),
      config: { displayModeBar: false }
    };
  }

  // js/charts/scatter.js
  var GL_FROM = 2e3;
  function crossPlot(groups, { xTitle = "x", yTitle = "y", log = true, theme = currentTheme() } = {}) {
    const usable = (p) => p.x != null && p.y != null && (!log || p.x > 0 && p.y > 0);
    const many = groups.length > 1;
    const data = groups.map((g, i) => {
      const pts = g.points.filter(usable);
      const emphasised = !many || i > 0;
      return {
        type: pts.length > GL_FROM ? "scattergl" : "scatter",
        mode: "markers",
        name: g.name,
        x: pts.map((p) => p.x),
        y: pts.map((p) => p.y),
        customdata: pts.map((p) => [esc(p.label ?? ""), p.id ?? null]),
        hovertemplate: `%{customdata[0]}<br>${esc(xTitle)} %{x}<br>${esc(yTitle)} %{y}<extra></extra>`,
        marker: {
          color: g.color ?? (emphasised ? theme.series[many ? i - 1 : 0] : theme.axis),
          size: g.size ?? (emphasised ? many ? 8 : 7 : 6),
          line: { color: theme.surface, width: 1 }
        }
      };
    });
    const scale = log ? { type: "log" } : {};
    const suffix = log ? " (log)" : "";
    return {
      data,
      layout: baseLayout({
        xaxis: axis({ ...scale, title: `${xTitle}${suffix}` }, theme),
        yaxis: axis({ ...scale, title: `${yTitle}${suffix}` }, theme),
        showlegend: many,
        legend: { orientation: "h", y: 1.08, x: 0, font: { color: theme.ink2 } },
        margin: { l: 60, r: 10, t: 30, b: 50 }
      }, theme),
      empty: data.every((t) => !t.x.length)
    };
  }
  function planView(points, { xTitle = "Easting", yTitle = "Northing", valueTitle = "value", theme = currentTheme() } = {}) {
    const pts = points.filter((p) => p.x != null && p.y != null);
    const scale = quantileLogScale(pts.map((p) => p.value), { steps: theme.sequential, missing: theme.muted });
    return {
      data: [{
        type: pts.length > GL_FROM ? "scattergl" : "scatter",
        mode: "markers",
        x: pts.map((p) => p.x),
        y: pts.map((p) => p.y),
        customdata: pts.map((p) => [esc(p.label ?? ""), p.id ?? null, p.value ?? null]),
        hovertemplate: `%{customdata[0]}${scale ? `<br>${esc(valueTitle)} %{customdata[2]}` : ""}<extra></extra>`,
        marker: {
          size: 9,
          line: { color: theme.surface, width: 1 },
          color: scale ? pts.map((p) => log10(p.value)) : theme.series[0],
          colorscale: colorscale(theme.sequential),
          cmin: scale?.lo,
          cmax: scale?.hi,
          colorbar: scale ? colorbar(theme, { title: { text: `log\u2081\u2080 ${valueTitle}` } }) : void 0
        }
      }],
      layout: baseLayout({ xaxis: axis({ title: xTitle }, theme), yaxis: axis({ title: yTitle, scaleanchor: "x" }, theme), margin: { l: 70, r: 10, t: 10, b: 50 } }, theme)
    };
  }
  function lineOverlay(series, { xTitle = "x", yTitle = "y", theme = currentTheme() } = {}) {
    return {
      data: series.map((s, i) => ({
        type: "scatter",
        mode: "lines",
        name: s.name,
        x: s.x,
        y: s.y,
        line: { color: s.color ?? theme.series[i % theme.series.length], width: 1.5 },
        hovertemplate: `${esc(s.name)}: %{x}, %{y}<extra></extra>`
      })),
      layout: baseLayout({
        xaxis: axis({ title: xTitle }, theme),
        yaxis: axis({ title: yTitle }, theme),
        showlegend: series.length > 1,
        legend: { orientation: "h", y: 1.1, x: 0, font: { color: theme.ink2 } },
        margin: { l: 56, r: 12, t: 30, b: 50 }
      }, theme)
    };
  }

  // js/charts/distribution.js
  function logHistogram(groups, { title = "value", binSize, theme = currentTheme() } = {}) {
    const many = groups.length > 1;
    const bins = binSize ? { xbins: { size: binSize } } : { nbinsx: 40 };
    const data = groups.map((g, i) => ({
      type: "histogram",
      histnorm: "percent",
      opacity: 0.75,
      ...bins,
      x: g.values.map(log10).filter((v) => v != null),
      name: g.name,
      marker: { color: g.color ?? (many ? i === 0 ? theme.axis : theme.series[i - 1] : theme.series[0]) }
    }));
    return {
      data,
      layout: baseLayout({
        barmode: "overlay",
        bargap: 0.04,
        showlegend: many,
        legend: { orientation: "h", y: 1.08, x: 0, font: { color: theme.ink2 } },
        margin: { l: 50, r: 10, t: many ? 30 : 10, b: 50 },
        xaxis: axis({ title: `log\u2081\u2080 ${title}` }, theme),
        yaxis: axis({ title: "% of samples" }, theme)
      }, theme),
      empty: data.every((t) => !t.x.length)
    };
  }

  // js/charts/holes3d.js
  function traceOffset({ azimuth = 0, inclination = 90 }, distance) {
    const inc = (inclination ?? 90) * Math.PI / 180, az = (azimuth ?? 0) * Math.PI / 180;
    const horizontal = distance * Math.cos(inc);
    return { dx: horizontal * Math.sin(az), dy: horizontal * Math.cos(az), dz: -distance * Math.sin(inc) };
  }
  function surfaceTrace(collar, metres) {
    const end = traceOffset(collar, metres);
    return [
      [collar.lat, collar.lon],
      [collar.lat + end.dy / 111320, collar.lon + end.dx / (111320 * Math.cos(collar.lat * Math.PI / 180))]
    ];
  }
  function holes3d(holes, {
    depthScale = 1,
    valueTitle = "value",
    depthUnit = "",
    range,
    theme = currentTheme(),
    axisTitles = ["Easting", "Northing", "Elevation"],
    aspect = { x: 1, y: 2.2, z: 0.9 }
  } = {}) {
    const logs = holes.flatMap((h) => h.intervals.filter((iv) => iv.value > 0).map((iv) => Math.log10(iv.value)));
    const [cmin, cmax] = range ?? (logs.length ? [Math.min(...logs), Math.max(...logs)] : [0, 1]);
    const ticks = [];
    for (let t = Math.ceil(cmin); t <= Math.floor(cmax); t++) ticks.push(t);
    const data = [];
    let barDrawn = false;
    for (const h of holes) {
      const end = traceOffset(h, h.length * depthScale);
      data.push({
        type: "scatter3d",
        mode: "lines+text",
        x: [h.x, h.x + end.dx],
        y: [h.y, h.y + end.dy],
        z: [h.z, h.z + end.dz],
        line: { color: theme.muted, width: 3 },
        text: [esc(h.id), ""],
        textposition: "top center",
        textfont: { color: theme.ink, size: 13 },
        hoverinfo: "skip",
        showlegend: false
      });
      const pts = h.intervals.filter((iv) => iv.value != null && iv.value > 0);
      const pos = pts.map((iv) => traceOffset(h, (iv.from + (iv.to ?? iv.from)) / 2 * depthScale));
      data.push({
        type: "scatter3d",
        mode: "markers",
        name: h.id,
        showlegend: false,
        x: pos.map((p) => h.x + p.dx),
        y: pos.map((p) => h.y + p.dy),
        z: pos.map((p) => h.z + p.dz),
        customdata: pts.map((iv) => [esc(h.id), iv.from, iv.to ?? iv.from, iv.value]),
        hovertemplate: `%{customdata[0]} %{customdata[1]}\u2013%{customdata[2]}${depthUnit ? ` ${esc(depthUnit)}` : ""}<br>${esc(valueTitle)} %{customdata[3]}<extra></extra>`,
        marker: {
          size: pts.map((iv) => 2 + 6.6 * Math.min(1, Math.max(0, (Math.log10(iv.value) - cmin) / (cmax - cmin || 1)))),
          color: pts.map((iv) => Math.log10(iv.value)),
          colorscale: colorscale(theme.sequential),
          cmin,
          cmax,
          line: { width: 0 },
          opacity: 0.9,
          // one colour bar for the whole chart, labelled in real values rather than logs
          colorbar: !barDrawn && pts.length ? colorbar(theme, {
            title: { text: valueTitle },
            len: 0.6,
            ...ticks.length ? { tickvals: ticks, ticktext: ticks.map((t) => String(Number((10 ** t).toPrecision(3)))) } : {}
          }) : void 0
        }
      });
      if (pts.length) barDrawn = true;
    }
    const sceneAxis = (title) => ({ title: { text: title }, gridcolor: theme.grid, zerolinecolor: theme.axis, showbackground: false, tickfont: { color: theme.ink2, size: 10 } });
    return {
      data,
      layout: {
        ...baseLayout({}, theme),
        margin: { l: 0, r: 0, t: 0, b: 0 },
        scene: {
          xaxis: sceneAxis(axisTitles[0]),
          yaxis: sceneAxis(axisTitles[1]),
          zaxis: sceneAxis(axisTitles[2]),
          aspectmode: "manual",
          aspectratio: aspect,
          camera: { eye: { x: 1.9, y: -1.3, z: 0.9 } }
        }
      }
    };
  }

  // js/maps/leaflet.js
  var leaflet = (L) => {
    const lib = L ?? globalThis.L;
    if (!lib) throw new Error("Leaflet is not loaded: include leaflet.js before drawing a map");
    return lib;
  };
  var BASEMAPS = {
    osm: {
      name: "OpenStreetMap",
      url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      options: { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }
    },
    topo: {
      name: "USGS topographic",
      url: "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
      options: { maxZoom: 16, attribution: "USGS The National Map" }
    },
    imagery: {
      name: "Imagery",
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      options: { maxZoom: 18, attribution: "Esri World Imagery" }
    }
  };
  function addBasemaps(map, keys = ["osm"], { L, exportable = false, scale = true, imperial = true } = {}) {
    L = leaflet(L);
    const layers = {}, named = {};
    for (const key of keys) {
      const b = BASEMAPS[key];
      if (!b) throw new Error(`Unknown basemap "${key}"; known: ${Object.keys(BASEMAPS).join(", ")}`);
      layers[key] = L.tileLayer(b.url, { ...b.options, ...exportable ? { crossOrigin: "" } : {} });
      named[b.name] = layers[key];
    }
    layers[keys[0]].addTo(map);
    if (keys.length > 1) L.control.layers(named, null, { position: "topright" }).addTo(map);
    if (scale) L.control.scale({ imperial }).addTo(map);
    return layers;
  }
  function legendControl(items, { L, map, title, shape = "circle", position = "bottomright" } = {}) {
    L = leaflet(L);
    const control = L.control({ position });
    control.onAdd = () => {
      const div = L.DomUtil.create("div", "map-legend");
      div.innerHTML = (title ? `<strong>${esc(title)}</strong>` : "") + items.map((it) => `<div><i class="${shape === "square" ? "square" : ""}" style="background:${esc(it.color)}"></i>${esc(it.label)}</div>`).join("");
      return div;
    };
    if (map) control.addTo(map);
    return control;
  }
  function buttonControl(text, onClick, { L, map, title = "", position = "topleft" } = {}) {
    L = leaflet(L);
    const control = L.control({ position });
    control.onAdd = () => {
      const button = L.DomUtil.create("button", "map-button");
      button.type = "button";
      button.textContent = text;
      button.title = title;
      L.DomEvent.disableClickPropagation(button);
      button.addEventListener("click", onClick);
      return button;
    };
    if (map) control.addTo(map);
    return control;
  }
  function labeledPin(map, { L, lat = 0, lon = 0, label = "", radius = 7 } = {}) {
    L = leaflet(L);
    const marker = L.circleMarker([lat, lon], { radius, color: "#111", weight: 2, fillColor: "#fff", fillOpacity: 1 });
    const pin = {
      marker,
      setLatLng(newLat, newLon) {
        marker.setLatLng([newLat, newLon]).addTo(map).bringToFront();
        return pin;
      },
      setLabel(text) {
        marker.unbindTooltip();
        if (text) marker.bindTooltip(esc(text), { permanent: true, direction: "right", offset: [8, -14], className: "site-label", interactive: false });
        return pin;
      },
      remove() {
        marker.remove();
        return pin;
      }
    };
    if (label) pin.setLabel(label);
    return pin;
  }
  function imageOverlay(map, src, bounds, { L, checkbox, slider, opacity = 0.6, exportable = false } = {}) {
    L = leaflet(L);
    const layer = L.imageOverlay(src, bounds, { opacity: slider ? +slider.value : opacity, ...exportable ? { crossOrigin: "" } : {} });
    if (checkbox) {
      const sync = () => {
        if (checkbox.checked) {
          layer.addTo(map);
          map.fitBounds(bounds);
        } else layer.remove();
      };
      checkbox.addEventListener("change", sync);
      if (checkbox.checked) layer.addTo(map);
    } else layer.addTo(map);
    slider?.addEventListener("input", () => layer.setOpacity(+slider.value));
    return layer;
  }

  // js/maps/layers.js
  function gradedPoints(map, points, { L, valueTitle = "", fit = true, theme = currentTheme() } = {}) {
    L = leaflet(L);
    const pts = points.filter((p) => p.lat != null && p.lon != null);
    const scale = quantileLogScale(pts.map((p) => p.value), { steps: theme.sequential, missing: theme.muted });
    const groups = /* @__PURE__ */ new Map();
    for (const p of pts) {
      const key = `${p.lat},${p.lon}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(p);
    }
    const layer = L.layerGroup().addTo(map);
    const bounds = [];
    for (const group of groups.values()) {
      const p = group.reduce((best, x) => (x.value ?? -Infinity) > (best.value ?? -Infinity) ? x : best, group[0]);
      const t = scale ? scale.t(p.value) : null;
      const more = group.length > 1 ? ` and ${group.length - 1} more here` : "";
      const popup = p.popup ?? `<b>${esc(p.label ?? "")}</b>${more}<br>${valueTitle && p.value != null ? `${esc(valueTitle)}: ${fmt(p.value)}<br>` : ""}${p.lat.toFixed(5)}, ${p.lon.toFixed(5)}`;
      L.circleMarker([p.lat, p.lon], { radius: 5 + 6 * (t ?? 0), color: "#fff", weight: 1.5, fillColor: scale ? scale.color(t) : theme.series[0], fillOpacity: 0.9 }).bindPopup(popup).addTo(layer);
      bounds.push([p.lat, p.lon]);
    }
    if (fit && bounds.length === 1) map.setView(bounds[0], 13);
    else if (fit && bounds.length) map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
    const legend = scale && !scale.flat ? legendControl([1, 0.5, 0].map((pos) => ({ color: scale.color(pos), label: fmt(scale.value(pos)) })), { L, map, title: valueTitle }) : null;
    return { layer, legend, scale, bounds };
  }
  function collarTraces(map, collars, { L, fit = true, theme = currentTheme() } = {}) {
    L = leaflet(L);
    const layer = L.layerGroup().addTo(map);
    const bounds = [];
    for (const c of collars) {
      if (c.metres) {
        const line = surfaceTrace(c, c.metres);
        L.polyline(line, { color: theme.series[1], weight: 4, opacity: 0.95 }).addTo(layer);
        bounds.push(line[1]);
      }
      const marker = L.circleMarker([c.lat, c.lon], { radius: 7, color: "#fff", weight: 2, fillColor: theme.header, fillOpacity: 1 }).bindTooltip(esc(c.id), { permanent: true, direction: "right", className: "pt-label", offset: [8, 0] });
      if (c.popup) marker.bindPopup(c.popup);
      marker.addTo(layer);
      bounds.push([c.lat, c.lon]);
    }
    if (fit && bounds.length) map.fitBounds(bounds, { padding: [60, 60] });
    return { layer, bounds };
  }
  function bandedArea(map, geojson, { L, colors = BAND_COLORS, title = "Distance by road", opacity = 0.55, pane = "area" } = {}) {
    var _a;
    L = leaflet(L);
    if (!map.getPane(pane)) {
      Object.assign(map.createPane(pane).style, { opacity: String(opacity), zIndex: "350" });
    }
    const renderer = (_a = map._rbvRenderers ?? (map._rbvRenderers = {}))[pane] ?? (_a[pane] = L.canvas({ pane }));
    const color = (feature) => colors[Math.min(feature.properties.band, colors.length - 1)];
    const layer = L.geoJSON(geojson, {
      pane,
      renderer,
      interactive: false,
      style: (feature) => ({ color: color(feature), weight: 1, fillColor: color(feature), fillOpacity: 1 })
    }).addTo(map);
    const bands = /* @__PURE__ */ new Map();
    for (const f of geojson.features) if (!bands.has(f.properties.band)) bands.set(f.properties.band, f);
    const legend = legendControl([...bands.values()].sort((a, b) => a.properties.band - b.properties.band).map((f) => ({
      color: color(f),
      label: `${fixed(f.properties.from_m / 1e3, 1)}\u2013${fixed(f.properties.to_m / 1e3, 1)} km`
    })), { L, map, title, shape: "square" });
    return { layer, legend, bounds: layer.getBounds() };
  }

  // js/maps/png.js
  var place = (node, box2) => {
    const r = node.getBoundingClientRect();
    return { x: r.left - box2.left, y: r.top - box2.top, w: r.width, h: r.height };
  };
  var fontOf = (node) => {
    const style = getComputedStyle(node);
    return `${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
  };
  function fitText(ctx, text, width) {
    if (ctx.measureText(text).width <= width + 1) return text;
    let cut = text.length;
    while (cut > 1 && ctx.measureText(`${text.slice(0, cut)}\u2026`).width > width) cut -= 1;
    return `${text.slice(0, cut)}\u2026`;
  }
  function tilesLoaded(map, timeout) {
    const loading = [];
    map.eachLayer((layer) => {
      if (layer.isLoading?.()) loading.push(layer);
    });
    if (!loading.length) return Promise.resolve();
    return Promise.race([
      Promise.all(loading.map((layer) => new Promise((resolve2) => layer.once("load", resolve2)))),
      new Promise((resolve2) => setTimeout(resolve2, timeout))
    ]);
  }
  async function renderMapPng(map, { attribution = "\xA9 OpenStreetMap contributors", timeout = 8e3 } = {}) {
    await tilesLoaded(map, timeout);
    const container = map.getContainer();
    const box2 = container.getBoundingClientRect();
    const scale = globalThis.devicePixelRatio || 1;
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(box2.width * scale);
    canvas.height = Math.round(box2.height * scale);
    const ctx = canvas.getContext("2d");
    ctx.scale(scale, scale);
    ctx.fillStyle = "#ddd";
    ctx.fillRect(0, 0, box2.width, box2.height);
    const pieces = [...container.querySelectorAll("img.leaflet-tile-loaded, img.leaflet-image-layer, .leaflet-pane canvas")].filter((node) => node.tagName !== "IMG" || node.complete && node.naturalWidth > 0).map((node, order) => {
      const style = getComputedStyle(node.closest(".leaflet-pane"));
      const own = node.classList.contains("leaflet-image-layer") ? Number(getComputedStyle(node).opacity) : 1;
      return { node, order, z: Number(style.zIndex) || 0, opacity: Number(style.opacity) * own };
    }).sort((a, b) => a.z - b.z || a.order - b.order);
    for (const { node, opacity } of pieces) {
      const { x, y, w, h } = place(node, box2);
      ctx.globalAlpha = opacity;
      ctx.drawImage(node, x, y, w, h);
    }
    ctx.globalAlpha = 1;
    ctx.textBaseline = "middle";
    for (const label of container.querySelectorAll(".leaflet-tooltip.site-label")) {
      const { x, y, w, h } = place(label, box2);
      ctx.font = fontOf(label);
      const text = fitText(ctx, label.textContent, w);
      ctx.lineJoin = "round";
      ctx.lineWidth = 3.5;
      ctx.strokeStyle = "#fff";
      ctx.strokeText(text, x, y + h / 2);
      ctx.fillStyle = getComputedStyle(label).color;
      ctx.fillText(text, x, y + h / 2);
    }
    for (const key of container.querySelectorAll(".map-legend")) {
      const style = getComputedStyle(key);
      const { x, y, w, h } = place(key, box2);
      ctx.fillStyle = style.backgroundColor;
      ctx.strokeStyle = "rgb(0 0 0 / 30%)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(x, y, w, h, 8);
      else ctx.rect(x, y, w, h);
      ctx.fill();
      ctx.stroke();
      for (const row of key.children) {
        const line = place(row, box2);
        let left = line.x;
        const swatch = row.querySelector("i");
        if (swatch) {
          const s = place(swatch, box2);
          ctx.fillStyle = swatch.style.background;
          ctx.beginPath();
          if (swatch.classList.contains("square") || !ctx.roundRect) ctx.rect(s.x, s.y, s.w, s.h);
          else ctx.roundRect(s.x, s.y, s.w, s.h, s.w / 2);
          ctx.fill();
          left = s.x + s.w + 6;
        }
        ctx.font = fontOf(row);
        ctx.fillStyle = style.color;
        ctx.fillText(row.textContent, left, line.y + line.h / 2);
      }
    }
    if (attribution) {
      ctx.font = "11px system-ui, sans-serif";
      const width = ctx.measureText(attribution).width + 10;
      ctx.fillStyle = "rgb(255 255 255 / 80%)";
      ctx.fillRect(box2.width - width, box2.height - 18, width, 18);
      ctx.fillStyle = "#333";
      ctx.fillText(attribution, box2.width - width + 5, box2.height - 9);
    }
    return new Promise((resolve2, reject) => {
      canvas.toBlob((blob) => blob ? resolve2(blob) : reject(new Error("empty image")), "image/png");
    });
  }
  async function downloadMapPng(map, name = "map", options = {}) {
    const url = URL.createObjectURL(await renderMapPng(map, options));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${slug(name)}-map.png`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1e4);
  }

  // js/widgets/lightbox.js
  var box = null;
  var state = { items: [], i: 0, caption: null, opener: null };
  var background = [];
  function ensure() {
    if (box) return box;
    box = document.createElement("div");
    box.className = "lightbox";
    box.hidden = true;
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "Image viewer");
    box.innerHTML = `
    <button class="lb-close icon-btn" type="button" aria-label="Close">\u2715</button>
    <button class="lb-prev icon-btn" type="button" aria-label="Previous image">\u2039</button>
    <figure><img alt=""><figcaption></figcaption></figure>
    <button class="lb-next icon-btn" type="button" aria-label="Next image">\u203A</button>`;
    document.body.append(box);
    box.querySelector(".lb-close").onclick = closeLightbox;
    box.querySelector(".lb-prev").onclick = () => step(-1);
    box.querySelector(".lb-next").onclick = () => step(1);
    box.addEventListener("click", (e) => {
      if (e.target === box || e.target.tagName === "FIGURE" || e.target.closest("figcaption a")) closeLightbox();
    });
    document.addEventListener("keydown", (e) => {
      if (box.hidden) return;
      if (e.key === "Escape") closeLightbox();
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
      if (e.key === "Tab") trapFocus(e);
    });
    return box;
  }
  function trapFocus(e) {
    const stops = [...box.querySelectorAll("button, a[href]")].filter((n) => !n.hidden);
    const first = stops[0], last = stops.at(-1);
    if (!box.contains(document.activeElement)) {
      e.preventDefault();
      first.focus();
    } else if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
  function disableBackground() {
    background = [...document.body.children].filter((element) => element !== box).map((element) => ({ element, inert: element.inert }));
    for (const { element } of background) element.inert = true;
  }
  function restoreBackground() {
    for (const { element, inert } of background) element.inert = inert;
    background = [];
  }
  function step(by) {
    state.i = (state.i + by + state.items.length) % state.items.length;
    show();
  }
  function show() {
    const it = state.items[state.i];
    const img = box.querySelector("img");
    img.src = it.src;
    img.alt = it.caption ?? "";
    const many = state.items.length > 1;
    box.querySelector(".lb-prev").hidden = box.querySelector(".lb-next").hidden = !many;
    box.querySelector("figcaption").innerHTML = (state.caption ? state.caption(it) : esc(it.caption)) + (many ? ` <span class="lb-count">(${state.i + 1} / ${state.items.length})</span>` : "");
  }
  function openLightbox(items, index = 0, { caption = null } = {}) {
    ensure();
    Object.assign(state, { items, i: index, caption, opener: document.activeElement });
    show();
    box.hidden = false;
    disableBackground();
    document.body.style.overflow = "hidden";
    box.querySelector(".lb-close").focus();
  }
  function closeLightbox() {
    if (!box || box.hidden) return;
    box.hidden = true;
    restoreBackground();
    document.body.style.overflow = "";
    state.opener?.focus?.();
  }
  function gallery(root, items, { label = (it) => it.caption ?? "", caption = null, className = "gallery" } = {}) {
    root.innerHTML = `<div class="${esc(className)}">${items.map((it, i) => `<figure><button type="button" data-i="${i}" aria-label="Open image: ${esc(it.caption ?? "")}"><img loading="lazy" src="${esc(it.thumb || it.src)}" alt="${esc(it.caption ?? "")}"></button><figcaption>${esc(label(it))}</figcaption></figure>`).join("")}</div>`;
    root.querySelectorAll("button[data-i]").forEach((b) => {
      b.onclick = () => openLightbox(items, +b.dataset.i, { caption });
    });
  }

  // js/widgets/blocks.js
  function statTiles(root, tiles) {
    root.classList.add("tiles");
    root.innerHTML = tiles.map((t) => `<div class="tile"><div class="v">${esc(t.value)}</div><div class="l">${esc(t.label)}</div></div>`).join("");
  }
  function compositionBar(root, parts, { color, label = "Composition", describe = (p) => `${p.name}: ${fmt(p.length)}` }) {
    const total = parts.reduce((s, p) => s + p.length, 0) || 1;
    root.innerHTML = `
    <div class="lithbar" role="img" aria-label="${esc(label)}: ${esc(parts.map((p) => `${p.name} ${Math.round(100 * p.length / total)}%`).join(", "))}">
      ${parts.map((p) => `<span title="${esc(describe(p))}" style="flex:${p.length};background:${esc(color(p.name))}"></span>`).join("")}</div>
    <div class="legend">${parts.map((p) => `<span><i class="swatch" style="background:${esc(color(p.name))}"></i>${esc(p.name)} ${Math.round(100 * p.length / total)}%</span>`).join("")}</div>`;
  }
  function compareCells(x, y, dir = 1) {
    if (x == null || y == null) return (x == null) - (y == null);
    return dir * (typeof x === "number" && typeof y === "number" ? x - y : String(x).localeCompare(String(y), void 0, { numeric: true }));
  }
  function dataTable(table, columns, rows, options = {}) {
    const state2 = { rows, sort: null, limit: 1e3, filter: "", ...options };
    const draw2 = () => {
      const needle = state2.filter.trim().toLowerCase();
      const keys = state2.filterKeys ?? columns.map((c) => c.key);
      let shown = needle ? state2.rows.filter((r) => keys.some((k) => r[k] != null && String(r[k]).toLowerCase().includes(needle))) : state2.rows.slice();
      if (state2.sort) shown.sort((a, b) => compareCells(a[state2.sort.key], b[state2.sort.key], state2.sort.dir));
      const drawn = shown.slice(0, state2.limit);
      table.innerHTML = `<thead><tr>${columns.map((c) => `<th scope="col" class="sortable ${c.numeric ? "num" : ""}" data-key="${esc(c.key)}"
        ${state2.sort?.key === c.key ? `aria-sort="${state2.sort.dir > 0 ? "ascending" : "descending"}"` : ""}><button type="button">${esc(c.title ?? c.key)}</button></th>`).join("")}</tr></thead>
      <tbody>${drawn.map((r, i) => `<tr ${state2.onRow ? `class="clickable" tabindex="0" data-i="${i}"` : ""}>${columns.map((c) => `<td class="${c.numeric ? "num" : ""} ${c.className ? esc(c.className(r)) : ""}">${c.cell ? c.cell(r) : r[c.key] == null ? "" : fmt(r[c.key])}</td>`).join("")}</tr>`).join("")}</tbody>`;
      table.querySelectorAll("th[data-key]").forEach((th) => {
        th.querySelector("button").onclick = () => {
          state2.sort = { key: th.dataset.key, dir: state2.sort?.key === th.dataset.key ? -state2.sort.dir : 1 };
          draw2();
        };
      });
      if (state2.onRow) {
        table.querySelectorAll("tr[data-i]").forEach((tr) => {
          tr.onclick = () => state2.onRow(drawn[+tr.dataset.i]);
          tr.onkeydown = (e) => {
            if (e.key === "Enter") state2.onRow(drawn[+tr.dataset.i]);
          };
        });
      }
      if (state2.note) {
        const notes = [];
        if (needle) notes.push(`${shown.length.toLocaleString("en-US")} of ${state2.rows.length.toLocaleString("en-US")} match`);
        if (shown.length > state2.limit) notes.push(`showing the first ${state2.limit.toLocaleString("en-US")}`);
        state2.note.textContent = notes.join("; ");
      }
    };
    draw2();
    return { update(changes) {
      Object.assign(state2, changes);
      draw2();
    } };
  }

  // js/widgets/shell.js
  function parseHash(hash = globalThis.location?.hash ?? "") {
    const path = hash.replace(/^#\/?/, "");
    if (!path) return [];
    return path.split("/").map((part) => {
      try {
        return decodeURIComponent(part);
      } catch {
        return part;
      }
    });
  }
  var hashFor = (...parts) => `#/${parts.filter((p) => p != null && p !== "").map((p) => encodeURIComponent(p)).join("/")}`;
  function setActiveNav(route, nav = document.getElementById("nav")) {
    nav?.querySelectorAll("a[data-route]").forEach((a) => {
      const on = a.dataset.route === route;
      a.classList.toggle("active", on);
      if (on) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }
  function hashRouter(routes, { root = document.getElementById("app"), nav = document.getElementById("nav") } = {}) {
    const render = async () => {
      const [name = "", ...rest] = parseHash();
      const key = Object.hasOwn(routes, name) ? name : "";
      setActiveNav(key || "overview", nav);
      try {
        await routes[key]?.(...rest);
      } catch (e) {
        console.error(e);
        if (root) root.innerHTML = `<div class="error" role="alert"><b>Could not show this page.</b> ${esc(e.message)}</div>`;
      }
    };
    globalThis.addEventListener("hashchange", () => {
      render();
      globalThis.scrollTo?.(0, 0);
    });
    render();
    return { render };
  }
  return __toCommonJS(index_exports);
})();
