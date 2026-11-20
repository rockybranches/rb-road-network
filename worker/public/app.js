"use strict";

// The map layers, legend, pin, PNG export, colours and stat tiles come from
// rb-viz (vendor/rb-viz.js, loaded before this script as the global RBViz).
// To update it: worker/scripts/sync-rb-viz.sh.
const { addBasemaps, bandedArea, buttonControl, labeledPin, downloadMapPng, statTiles } = RBViz;
const { BAND_COLORS, TOKENS, esc, fixed: fmt, slug } = RBViz;

const $ = (selector) => document.querySelector(selector);
const when = (iso) =>
  new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });

// Build an element. Text always goes in as text nodes, never as HTML, so
// names typed by users or read from a CSV cannot inject markup.
function el(tag, props = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

async function api(path, { method = "GET", body } = {}) {
  const init = { method };
  if (body !== undefined) {
    init.body = JSON.stringify(body);
    init.headers = { "content-type": "application/json" };
  }
  const res = await fetch(path, init);
  let data = null;
  try {
    data = await res.json();
  } catch {
    // Not JSON; fall through to the status check.
  }
  if (!res.ok) throw new Error((data && data.error) || `Request failed (${res.status})`);
  return data;
}

function numberField(form, name, label) {
  const value = Number(form.elements[name].value.trim());
  if (form.elements[name].value.trim() === "" || !Number.isFinite(value)) {
    throw new Error(`${label} must be a number`);
  }
  return value;
}

function showError(node, message) {
  node.textContent = message || "";
  node.hidden = !message;
}

const siteName = (request) =>
  request.label || `${request.lat.toFixed(4)}, ${request.lon.toFixed(4)}`;

// ---------------------------------------------------------------- map

const map = L.map("map", { preferCanvas: true }).setView([33.75, -84.39], 8);
// exportable: lets the tiles be copied into the downloadable PNG of the map.
addBasemaps(map, ["osm"], { exportable: true, scale: false });

// What an analysis or a batch draws; cleared when another one is shown.
const overlay = L.layerGroup().addTo(map);
const pin = labeledPin(map);
let legend = null;
let areaBounds = null; // what "Zoom to area" shows; null when no area is drawn

const zoomToArea = buttonControl(
  "Zoom to area",
  () => {
    if (areaBounds) map.fitBounds(areaBounds, { padding: [20, 20] });
  },
  { map, title: "Fit the map to the market area" },
);
zoomToArea.getContainer().hidden = true;

function setAreaBounds(bounds) {
  areaBounds = bounds && bounds.isValid() ? bounds : null;
  zoomToArea.getContainer().hidden = !areaBounds;
}

function clearOverlay() {
  overlay.clearLayers();
  pin.setLabel("");
  setAreaBounds(null);
  if (legend) {
    legend.remove();
    legend = null;
  }
}

map.on("click", (event) => {
  const form = $("#analysis-form");
  form.elements.lat.value = event.latlng.lat.toFixed(5);
  form.elements.lon.value = event.latlng.lng.toFixed(5);
  pin.setLatLng(event.latlng.lat, event.latlng.lng);
  // The marker now shows a new start point, not the analysis on screen.
  pin.setLabel("");
  selectTab("analyze");
});

function drawArea(geojson, start) {
  const area = bandedArea(map, geojson);
  overlay.addLayer(area.layer); // so that clearOverlay() removes it
  legend = area.legend;
  // Fit to what was actually reached, which is usually well inside the
  // reference circle. An empty area keeps the circle's bounds.
  if (area.bounds.isValid()) setAreaBounds(area.bounds.extend(start));
}

$("#dl-map-png").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  showError($("#map-png-error"), "");
  button.disabled = true;
  button.textContent = "Rendering…";
  try {
    await downloadMapPng(map, current ? siteName(current.request) : "map");
  } catch (error) {
    console.error(error);
    showError(
      $("#map-png-error"),
      "The map image could not be made. Wait for the map to finish loading, then try again.",
    );
  } finally {
    button.disabled = false;
    button.textContent = "Rendered Map (png)";
  }
});

// --------------------------------------------------------------- tabs

function selectTab(name) {
  for (const tab of document.querySelectorAll(".tabs button")) {
    const selected = tab.dataset.tab === name;
    tab.setAttribute("aria-selected", String(selected));
    $(`#tab-${tab.dataset.tab}`).hidden = !selected;
  }
  if (name === "saved") refreshSaved();
  if (name === "batches") refreshBatches();
}

for (const tab of document.querySelectorAll(".tabs button")) {
  tab.addEventListener("click", () => selectTab(tab.dataset.tab));
}

// ----------------------------------------------------------- analysis

let current = null; // the analysis record on screen

function renderReport(report) {
  const table = $("#result-table");
  table.replaceChildren();
  const head = el("tr", {}, el("th", {}, "County"));
  for (const year of report.years) head.append(el("th", {}, String(year)));
  head.append(el("th", {}, "km²"));
  table.append(el("thead", {}, head));

  const body = el("tbody");
  for (const county of report.counties) {
    const row = el("tr", {}, el("td", {}, `${county.name}, ${county.state}`));
    for (const people of county.population) row.append(el("td", {}, fmt(people)));
    row.append(el("td", {}, fmt(county.reached_km2, 1)));
    body.append(row);
  }
  table.append(body);

  const totals = el("tr", {}, el("td", {}, "Total"));
  for (const total of report.totals) totals.append(el("td", {}, fmt(total)));
  totals.append(el("td"));
  table.append(el("tfoot", {}, totals));

  const missing = report.missing_population.map((c) => `${c.name} (${c.state})`);
  $("#result-missing").textContent = missing.length
    ? `Reached but not counted, because no population figures are loaded: ${missing.join(", ")}.`
    : "";
}

// The detailed result (every reached 250 m road cell, in the layout of the
// earlier C++ program) is built by the Worker in the background, so the page
// asks for it and then checks back until it is ready.
const DETAIL_POLL_MS = 5000;
let detailTimer = null;

function renderDetail(record, detail) {
  clearTimeout(detailTimer);
  const build = $("#detail-build");
  const link = $("#dl-detail");
  const status = $("#detail-status");
  const state = detail ? detail.status : null;
  link.hidden = state !== "done";
  build.hidden = state === "done";
  build.disabled = state === "queued" || state === "running";
  build.textContent = build.disabled ? "Building detailed GeoJSON…" : "Build detailed GeoJSON";
  status.hidden = !state;
  if (state === "done") {
    const name = slug(siteName(record.request));
    Object.assign(link, {
      href: `/api/analyses/${record.id}/detail.geojson`,
      download: `${name}-detail.geojson`,
    });
    status.textContent = `${fmt(detail.points)} points, ${fmt(detail.bytes / 1e6, 1)} MB`;
  } else if (state === "failed") {
    status.textContent = `The detailed result failed: ${detail.error}`;
  } else if (state) {
    status.textContent = "Being built in the background; this can take a few minutes.";
    detailTimer = setTimeout(() => pollDetail(record), DETAIL_POLL_MS);
  }
}

async function pollDetail(record) {
  if (current !== record) return;
  try {
    const { detail } = await api(`/api/analyses/${record.id}/detail`);
    if (current === record) renderDetail(record, detail);
  } catch (err) {
    if (current === record) {
      // Keep checking: one failed request is not the end of the job.
      $("#detail-status").textContent = `Could not check progress (${err.message}); retrying.`;
      detailTimer = setTimeout(() => pollDetail(record), DETAIL_POLL_MS);
    }
  }
}

$("#detail-build").addEventListener("click", async () => {
  const record = current;
  if (!record) return;
  $("#detail-build").disabled = true;
  try {
    const { analyses } = await api(`/api/analyses/${record.id}/detail`, { method: "POST" });
    if (current === record) renderDetail(record, analyses[0].detail);
  } catch (err) {
    $("#detail-build").disabled = false;
    showError($("#form-error"), err.message);
  }
});

async function showAnalysis(record) {
  current = record;
  const { request, result } = record;
  const report = result.report;
  const form = $("#analysis-form");
  form.elements.label.value = request.label;
  form.elements.lat.value = request.lat;
  form.elements.lon.value = request.lon;
  form.elements.radius_km.value = request.radius_m / 1000;
  form.elements.tons_per_person.value = request.tons_per_person;
  form.elements.min_km2.value = request.min_km2;

  $("#result-title").textContent = siteName(request);
  $("#result-meta").textContent =
    `${fmt(request.radius_m / 1000, 1)} km by road · saved ${when(record.created_at)}` +
    (result.start.moved_to_nearest_road ? " · start moved to the nearest road" : "");
  $("#result-warnings").replaceChildren(...result.warnings.map((w) => el("li", { className: "notice" }, w)));

  const pct = report.percent_increase;
  const tile = (label, value) => ({ label, value });
  statTiles($("#result-stats"), [
    tile("Counties", fmt(report.counties.length)),
    tile(`Population ${report.base_year}`, fmt(report.totals[report.years.indexOf(report.base_year)])),
    tile(`Population ${report.target_year}`, fmt(report.totals[report.years.indexOf(report.target_year)])),
    tile("Growth", pct === null ? "n/a" : `${pct >= 0 ? "+" : ""}${pct.toFixed(1)}%`),
    tile(`Tons needed ${report.target_year}`, fmt(report.tons_target)),
    tile("Reachable area", `${fmt(result.reachable.km2)} km²`),
  ]);
  renderReport(report);

  const name = slug(siteName(request));
  Object.assign($("#dl-tex"), { href: `/api/analyses/${record.id}/report.tex`, download: `${name}.tex` });
  Object.assign($("#dl-geojson"), {
    href: `/api/analyses/${record.id}/area.geojson`,
    download: `${name}.geojson`,
  });
  renderDetail(record, record.detail);
  $("#result").hidden = false;
  showError($("#form-error"), "");
  selectTab("analyze");
  if (location.hash !== `#a/${record.id}`) history.replaceState(null, "", `#a/${record.id}`);

  clearOverlay();
  pin.setLatLng(result.start.lat, result.start.lon).setLabel(siteName(request));
  const reference = L.circle([result.start.lat, result.start.lon], {
    radius: request.radius_m,
    color: "#444", // fixed: map tiles are light in both colour schemes
    weight: 1,
    dashArray: "4 4",
    fill: false,
    interactive: false,
  }).addTo(overlay);
  map.fitBounds(reference.getBounds(), { padding: [10, 10] });
  setAreaBounds(reference.getBounds());

  const geojson = await fetch(`/api/analyses/${record.id}/area.geojson`).then((r) => r.json());
  if (current === record) {
    drawArea(geojson, [result.start.lat, result.start.lon]);
    pin.marker.bringToFront();
  }
}

async function loadAnalysis(id) {
  try {
    const record = await api(`/api/analyses/${id}`);
    if (record.status !== "done") throw new Error("This analysis has not finished.");
    await showAnalysis(record);
  } catch (error) {
    selectTab("analyze");
    showError($("#form-error"), error.message);
  }
}

$("#analysis-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type=submit]");
  showError($("#form-error"), "");
  button.disabled = true;
  button.textContent = "Running…";
  try {
    const record = await api("/api/analyses", {
      method: "POST",
      body: {
        label: form.elements.label.value.trim(),
        lat: numberField(form, "lat", "Latitude"),
        lon: numberField(form, "lon", "Longitude"),
        radius_m: numberField(form, "radius_km", "Road distance") * 1000,
        tons_per_person: numberField(form, "tons_per_person", "Tons per person"),
        min_km2: numberField(form, "min_km2", "Minimum county area"),
      },
    });
    await showAnalysis(record);
  } catch (error) {
    showError($("#form-error"), error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Run analysis";
  }
});

$("#copy-link").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  try {
    await navigator.clipboard.writeText(location.href);
    button.textContent = "Copied";
  } catch {
    button.textContent = "Copy the address bar";
  }
  setTimeout(() => (button.textContent = "Copy link"), 1500);
});

$("#delete-analysis").addEventListener("click", async () => {
  if (!current || !confirm(`Delete the saved analysis "${siteName(current.request)}"?`)) return;
  try {
    await api(`/api/analyses/${current.id}`, { method: "DELETE" });
  } catch (error) {
    showError($("#form-error"), error.message);
    return;
  }
  current = null;
  $("#result").hidden = true;
  clearOverlay();
  history.replaceState(null, "", location.pathname);
});

// -------------------------------------------------------------- saved

async function refreshSaved() {
  const list = $("#saved-list");
  try {
    const { analyses } = await api("/api/analyses");
    list.replaceChildren(
      ...analyses.map((a) => {
        const button = el(
          "button",
          { type: "button" },
          el("strong", {}, siteName(a.request)),
          el(
            "small",
            {},
            `${when(a.created_at)} · ${fmt(a.request.radius_m / 1000, 1)} km · ` +
              `${fmt(a.summary.counties)} counties · ${fmt(a.summary.population_target)} people`,
          ),
        );
        button.addEventListener("click", () => loadAnalysis(a.id));
        return el("li", {}, button);
      }),
    );
    if (!analyses.length) list.append(el("li", { className: "muted" }, "Nothing saved yet."));
  } catch (error) {
    list.replaceChildren(el("li", { className: "error" }, error.message));
  }
}

// ------------------------------------------------------------ batches

let batch = null; // the batch on screen
let running = false;
let stopRequested = false;

async function refreshBatches() {
  const list = $("#batch-list");
  try {
    const { batches } = await api("/api/batches");
    list.replaceChildren(
      ...batches.map((b) => {
        const failed = b.failed ? `, ${b.failed} failed` : "";
        const button = el(
          "button",
          { type: "button" },
          el("strong", {}, b.label),
          el("small", {}, `${when(b.created_at)} · ${b.done} of ${b.sites} done${failed}`),
        );
        button.addEventListener("click", () => openBatch(b.id));
        return el("li", {}, button);
      }),
    );
    if (!batches.length) list.append(el("li", { className: "muted" }, "No batches yet."));
  } catch (error) {
    list.replaceChildren(el("li", { className: "error" }, error.message));
  }
}

function renderBatch(message = "") {
  const rows = batch.analyses;
  const count = (status) => rows.filter((a) => a.status === status).length;
  const pending = count("pending") + count("running");
  const failed = count("failed");
  $("#batch-title").textContent = batch.label;
  $("#batch-progress").textContent =
    message ||
    `${count("done")} of ${rows.length} done` +
      (failed ? `, ${failed} failed` : "") +
      (pending ? `, ${pending} to run` : "");

  const runButton = $("#batch-run");
  runButton.hidden = !running && !pending && !failed;
  runButton.textContent = running
    ? "Stop"
    : pending
      ? `Run remaining (${pending})`
      : `Retry failed (${failed})`;
  Object.assign($("#batch-csv"), {
    href: `/api/batches/${batch.id}/summary.csv`,
    download: `${slug(batch.label)}.csv`,
  });

  const table = $("#batch-table");
  table.replaceChildren(
    el(
      "thead",
      {},
      el(
        "tr",
        {},
        el("th", {}, "Site"),
        el("th", { className: "text" }, "Status"),
        el("th", {}, "Counties"),
        el("th", {}, "People, 2030"),
      ),
    ),
  );
  const body = el("tbody");
  for (const a of rows) {
    const status = a.status === "failed" ? `failed: ${a.error}` : a.status;
    const row = el(
      "tr",
      {},
      el("td", {}, siteName(a.request)),
      el("td", { className: `text status-${a.status}` }, status),
      el("td", {}, a.summary ? fmt(a.summary.counties) : ""),
      el("td", {}, a.summary ? fmt(a.summary.population_target) : ""),
    );
    if (a.status === "done") {
      row.className = "clickable";
      row.title = "Show on the map";
      row.addEventListener("click", () => loadAnalysis(a.id));
    }
    body.append(row);
  }
  table.append(body);
}

// Mark every site of the batch on the map; finished ones open on click.
function drawBatchSites() {
  clearOverlay();
  pin.remove();
  // Fixed, not from the page theme: map tiles are light in both colour schemes.
  const unfinished = TOKENS.light.axis;
  const points = [];
  for (const a of batch.analyses) {
    const done = a.status === "done";
    const point = [a.request.lat, a.request.lon];
    points.push(point);
    const marker = L.circleMarker(point, {
      radius: 6,
      color: "#111",
      weight: 1.5,
      fillColor: done ? BAND_COLORS[1] : unfinished,
      fillOpacity: 1,
      bubblingMouseEvents: false,
    }).bindTooltip(esc(siteName(a.request))); // Leaflet treats tooltip text as HTML
    if (done) marker.on("click", () => loadAnalysis(a.id));
    marker.addTo(overlay);
  }
  if (points.length) map.fitBounds(L.latLngBounds(points).pad(0.2), { maxZoom: 10 });
}

function showBatch(data) {
  batch = data;
  $("#batch-index").hidden = true;
  $("#batch-view").hidden = false;
  selectTabQuietly("batches");
  if (location.hash !== `#b/${batch.id}`) history.replaceState(null, "", `#b/${batch.id}`);
  renderBatch();
  drawBatchSites();
}

// Show the batches tab without reloading the batch list behind the view.
function selectTabQuietly(name) {
  for (const tab of document.querySelectorAll(".tabs button")) {
    const selected = tab.dataset.tab === name;
    tab.setAttribute("aria-selected", String(selected));
    $(`#tab-${tab.dataset.tab}`).hidden = !selected;
  }
}

async function openBatch(id) {
  try {
    showBatch(await api(`/api/batches/${id}`));
  } catch (error) {
    selectTab("batches");
    showError($("#batch-error"), error.message);
  }
}

async function runBatch() {
  if (running) {
    stopRequested = true;
    return;
  }
  const mine = batch;
  const pending = mine.analyses.filter((a) => a.status === "pending");
  const targets = pending.length ? pending : mine.analyses.filter((a) => a.status === "failed");
  running = true;
  stopRequested = false;
  let problem = "";
  for (const row of targets) {
    if (stopRequested || batch !== mine) break;
    const before = row.status;
    row.status = "running";
    renderBatch();
    try {
      const updated = await api(`/api/analyses/${row.id}/run`, { method: "POST" });
      delete updated.result;
      Object.assign(row, updated);
    } catch (error) {
      // The request itself failed (network or server), which would hit
      // every remaining site too: stop and let the user resume.
      row.status = before;
      problem = `Stopped: ${error.message}`;
      break;
    }
  }
  running = false;
  if (batch === mine) renderBatch(problem);
}

$("#batch-run").addEventListener("click", runBatch);

$("#batch-back").addEventListener("click", () => {
  stopRequested = true;
  batch = null;
  $("#batch-view").hidden = true;
  $("#batch-index").hidden = false;
  history.replaceState(null, "", location.pathname);
  refreshBatches();
});

$("#batch-delete").addEventListener("click", async () => {
  if (!confirm(`Delete the batch "${batch.label}" and all ${batch.analyses.length} of its sites?`)) return;
  stopRequested = true;
  try {
    await api(`/api/batches/${batch.id}`, { method: "DELETE" });
  } catch (error) {
    renderBatch(error.message);
    return;
  }
  $("#batch-back").click();
});

$("#batch-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type=submit]");
  showError($("#batch-error"), "");
  button.disabled = true;
  try {
    const created = await api("/api/batches", {
      method: "POST",
      body: {
        label: form.elements.label.value.trim(),
        csv: await form.elements.file.files[0].text(),
        radius_m: numberField(form, "radius_km", "Road distance") * 1000,
        tons_per_person: numberField(form, "tons_per_person", "Tons per person"),
      },
    });
    form.reset();
    showBatch(created);
    runBatch();
  } catch (error) {
    showError($("#batch-error"), error.message);
  } finally {
    button.disabled = false;
  }
});

// -------------------------------------------------------------- start

function followHash() {
  const [kind, id] = location.hash.slice(1).split("/");
  if (kind === "a" && id) loadAnalysis(id);
  else if (kind === "b" && id) openBatch(id);
}

window.addEventListener("hashchange", followHash);
followHash();

api("/api/status")
  .then((status) => {
    $("#datasets").textContent =
      `Roads ${status.active.roads} · counties ${status.active.counties}`;
  })
  .catch(() => {
    $("#datasets").textContent = "The data service is not responding.";
  });
