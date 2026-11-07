// 5v5 Sim — browser UI (no build step, no external libraries)

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "style" && typeof v === "object") Object.assign(el.style, v);
    else if (k.startsWith("on") && typeof v === "function") el.addEventListener(k.slice(2), v);
    else if (k === "html") el.innerHTML = v;
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat()) {
    if (kid === null || kid === undefined || kid === false) continue;
    el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

const api = {
  async get(path) { const r = await fetch(path); return r.json(); },
  async post(path, body) {
    const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
    const data = await r.json().catch(() => ({}));
    if (!r.ok || data.ok === false) throw new Error(data.error || `Request failed (${r.status})`);
    return data;
  },
};

function toast(text, kind = "") {
  const el = h("div", { class: `toast ${kind}` }, text);
  $("#toasts").append(el);
  setTimeout(() => el.remove(), 4200);
}

// ───────────────────────── state ─────────────────────────
const S = {
  meta: null,
  teamA: null, teamB: null, rules: "NBA", mode: "Game",
  identities: [null, null],      // team identity of the two teams in the current game
  live: null, prevOnCourt: [new Set(), new Set()],
  score: [0, 0], flow: [], series: null,
  active: false, paused: false, speed: 1,
  feedFilter: "all", boxTeam: 0, boxSort: null,
};

// ───────────────────────── logos & faces ─────────────────────────
// Each image is probed once; afterwards a known-missing one is never requested again (the live view redraws several times a second).
const imageState = new Map();   // url -> "ok" | "missing" | Promise
function withImage(el, url, cls = "") {
  const state = imageState.get(url);
  const attach = () => { el.textContent = ""; el.append(h("img", { src: url, alt: "", class: cls })); };
  if (state === "ok") { attach(); return; }
  if (state === "missing") return;
  if (!state) {
    // 200 = image, 202 = the server is downloading it (ask again shortly), anything else = none
    imageState.set(url, (async () => {
      for (let attempt = 0; attempt < 6; attempt++) {
        try {
          const r = await fetch(url, { cache: "force-cache" });
          if (r.status === 200) { imageState.set(url, "ok"); return true; }
          if (r.status !== 202) break;
        } catch { break; }
        await new Promise((res) => setTimeout(res, 2500));
      }
      imageState.set(url, "missing");
      return false;
    })());
  }
  imageState.get(url).then?.((ok) => ok && el.isConnected && attach());
}
function logoEl(team, cls = "") {
  const el = h("div", { class: `logo ${cls}`, style: { "--c": team?.color || "#334155" } }, team?.initials || "?");
  if (team?.logo) withImage(el, `/media/logo?code=${team.logo}`);
  return el;
}
function faceEl(name) {
  const parts = (name || "").split(" ").filter(Boolean);
  const init = ((parts[0] || "")[0] || "") + ((parts[parts.length - 1] || "")[0] || "");
  const el = h("div", { class: "face" }, init.toUpperCase());
  withImage(el, `/media/headshot?name=${encodeURIComponent(name)}`);
  return el;
}

// ───────────────────────── team picker ─────────────────────────
function makePicker(root, onPick) {
  let open = false, hl = 0, filtered = [];
  const btn = h("button", { class: "picker-btn", type: "button" });
  const pop = h("div", { class: "picker-pop hidden" });
  const input = h("input", { placeholder: "Search teams or years…" });
  const list = h("div", { class: "picker-list" });
  pop.append(input, list);
  root.append(btn, pop);

  const show = (team) => {
    btn.replaceChildren(logoEl(team), h("span", { class: "t-name" }, team ? team.short : "Choose a team"), h("span", { class: "t-year" }, team?.year || ""));
  };
  const render = () => {
    const q = input.value.trim().toLowerCase();
    const teams = S.meta.teams;
    filtered = q ? teams.filter((t) => t.name.toLowerCase().includes(q)) : teams;
    list.replaceChildren();
    let lastYear = null;
    filtered.slice(0, 400).forEach((t, i) => {
      if (!q && t.year !== lastYear) { list.append(h("div", { class: "picker-group" }, t.year || "Other")); lastYear = t.year; }
      list.append(h("div", { class: `picker-opt ${i === hl ? "hl" : ""}`, onclick: () => choose(t) }, logoEl(t), h("span", {}, t.short), h("span", { class: "t-year" }, t.year || "")));
    });
    if (!filtered.length) list.append(h("div", { class: "empty" }, "No team matches."));
  };
  const toggle = (state) => {
    open = state ?? !open;
    pop.classList.toggle("hidden", !open);
    if (open) { hl = 0; input.value = ""; render(); input.focus(); }
  };
  const choose = (t) => { toggle(false); show(t); onPick(t); };
  btn.addEventListener("click", () => toggle());
  input.addEventListener("input", () => { hl = 0; render(); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") { hl = Math.min(hl + 1, filtered.length - 1); render(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { hl = Math.max(hl - 1, 0); render(); e.preventDefault(); }
    else if (e.key === "Enter" && filtered[hl]) choose(filtered[hl]);
    else if (e.key === "Escape") toggle(false);
  });
  document.addEventListener("click", (e) => { if (open && !root.contains(e.target)) toggle(false); });
  return { set: show };
}

// ───────────────────────── scoreboard ─────────────────────────
function renderScoreboard() {
  const [a, b] = S.identities;
  const side = (team, score, cls) => {
    const el = $(cls === "left" ? "#sbA" : "#sbB");
    if (!team) { el.replaceChildren(); return; }
    const poss = h("div", { class: `poss ${S.live?.possession === team.name ? "on" : ""}` });
    const scoreEl = h("div", { class: "sb-score", id: cls === "left" ? "scA" : "scB" }, score);
    const sub = S.live ? `${(S.live.teams[cls === "left" ? 0 : 1].totals.timeouts ?? "-")} timeouts` : "";
    el.replaceChildren(logoEl(team, "xl"), h("div", { class: "sb-name" }, h("div", { class: "yr" }, team.year || ""), h("div", { class: "nm" }, team.short), h("div", { class: "sub" }, sub)), poss, scoreEl);
  };
  side(a, S.score[0], "left");
  side(b, S.score[1], "right");
  document.documentElement.style.setProperty("--team-a", a?.color || "#4f8cff");
  document.documentElement.style.setProperty("--team-b", b?.color || "#f43f5e");
  const margin = S.score[0] - S.score[1];
  const fill = $("#sbMargin");
  const w = Math.min(50, Math.abs(margin) * 2.2);
  fill.style.width = `${w}%`;
  fill.style.left = margin >= 0 ? `${50 - w}%` : "50%";
  fill.style.background = margin >= 0 ? (a?.color || "#4f8cff") : (b?.color || "#f43f5e");
}

function bumpScore(idx) {
  const el = $(idx === 0 ? "#scA" : "#scB");
  if (!el) return;
  el.classList.remove("bump"); void el.offsetWidth; el.classList.add("bump");
}

function setStatus(text, live) {
  $("#sbStatus").replaceChildren(h("span", { class: `pill ${live ? "live" : ""}` }, text));
}

// ───────────────────────── on the floor ─────────────────────────
const STAT_COLS = [
  ["min", "MIN"], ["pts", "PTS"], ["reb", "REB"], ["ast", "AST"], ["stl", "STL"], ["blk", "BLK"], ["tov", "TO"], ["pf", "PF"],
  ["fg", "FG"], ["tp", "3PT"], ["ft", "FT"], ["pm", "+/-"],
];
const cell = (p, key) => {
  if (key === "fg") return `${p.fgm}-${p.fga}`;
  if (key === "tp") return `${p.tpm}-${p.tpa}`;
  if (key === "ft") return `${p.ftm}-${p.fta}`;
  if (key === "pm") return h("span", { class: p.pm > 0 ? "pm-pos" : p.pm < 0 ? "pm-neg" : "" }, p.pm > 0 ? `+${p.pm}` : p.pm);
  if (key === "min") return (p.min ?? 0).toFixed(1);
  return p[key];
};

function playerCell(p, slot) {
  return h("td", { class: "l" }, h("div", { class: "pcell" },
    slot ? h("span", { class: "slot" }, slot) : null,
    faceEl(p.name),
    h("span", { class: "pname" }, p.name, p.rookie ? h("span", { class: "tag rk" }, "R") : null, p.pf >= 5 ? h("span", { class: "tag foul" }, `${p.pf} PF`) : null)));
}

function renderCourt() {
  const root = $("#court");
  if (!S.live) { root.replaceChildren(h("div", { class: "empty" }, "The ten players on the floor show here during a game.")); return; }
  const blocks = S.live.teams.map((t, i) => {
    const prev = S.prevOnCourt[i];
    const now = new Set(t.court.map((p) => p.name));
    const rows = t.court.map((p) => {
      const tr = h("tr", { class: prev.size && !prev.has(p.name) ? "entered" : "" }, playerCell(p, p.pos), ...STAT_COLS.map(([k]) => h("td", { class: k === "pts" ? "pts" : "" }, cell(p, k))));
      return tr;
    });
    S.prevOnCourt[i] = now;
    const tot = t.totals;
    return h("div", { class: "court-team", style: { "--c": t.color } },
      h("div", { class: "court-team-head" }, logoEl(t), t.short, h("span", { class: "tot" }, `FG ${tot.fgm}-${tot.fga} · 3PT ${tot.tpm}-${tot.tpa} · FT ${tot.ftm}-${tot.fta}`)),
      h("table", { class: "stats" }, h("thead", {}, h("tr", {}, h("th", { class: "l" }, "Player"), ...STAT_COLS.map(([, l]) => h("th", {}, l)))), h("tbody", {}, rows)));
  });
  root.replaceChildren(...blocks);
}

// ───────────────────────── team compare ─────────────────────────
function renderCompare() {
  const root = $("#compare");
  if (!S.live) { root.replaceChildren(h("div", { class: "empty" }, "Team stats appear once the game starts.")); return; }
  const [A, B] = S.live.teams;
  const rows = [
    ["FG%", A.totals.fgp, B.totals.fgp, true], ["3PT%", A.totals.tpp, B.totals.tpp, true], ["FT%", A.totals.ftp, B.totals.ftp, true],
    ["Rebounds", A.totals.reb, B.totals.reb], ["Assists", A.totals.ast, B.totals.ast], ["Steals", A.totals.stl, B.totals.stl],
    ["Blocks", A.totals.blk, B.totals.blk], ["Turnovers", A.totals.tov, B.totals.tov], ["Points in paint", A.totals.paint, B.totals.paint],
    ["Fast break", A.totals.fastbreak, B.totals.fastbreak], ["2nd chance", A.totals.second, B.totals.second],
  ];
  root.replaceChildren(
    h("div", { class: "cmp-head" }, h("span", {}, A.short), h("span", {}, ""), h("span", {}, B.short)),
    ...rows.map(([label, a, b, pct]) => {
      const va = a ?? 0, vb = b ?? 0, max = pct ? 100 : Math.max(1, va, vb);
      return h("div", { class: "cmp-row" },
        h("span", { class: "v" }, pct ? (a == null ? "–" : a.toFixed(1)) : va),
        h("div", { class: "bar left" }, h("i", { style: { width: `${(va / max) * 100}%`, background: A.color } })),
        h("span", { class: "lbl" }, label),
        h("div", { class: "bar" }, h("i", { style: { width: `${(vb / max) * 100}%`, background: B.color } })),
        h("span", { class: "v r" }, pct ? (b == null ? "–" : b.toFixed(1)) : vb));
    }));
}

// ───────────────────────── box score ─────────────────────────
const BOX_COLS = [
  ["min", "MIN"], ["pts", "PTS"], ["reb", "REB"], ["oreb", "OREB"], ["ast", "AST"], ["stl", "STL"], ["blk", "BLK"], ["tov", "TO"], ["pf", "PF"],
  ["fg", "FG"], ["fgp", "FG%"], ["tp", "3PT"], ["tpp", "3P%"], ["ft", "FT"], ["ftp", "FT%"], ["pm", "+/-"],
];
function renderBox() {
  const root = $("#boxTable");
  if (!S.live) { root.replaceChildren(h("div", { class: "empty" }, "No game yet.")); return; }
  const t = S.live.teams[S.boxTeam];
  $$("#boxTeam button").forEach((b, i) => { b.textContent = S.live.teams[i].short; });
  let players = [...t.box];
  const sortKey = S.boxSort;
  if (sortKey) players.sort((x, y) => (y[sortKey] ?? -1) - (x[sortKey] ?? -1));
  const starters = sortKey ? players : players.filter((p) => p.starter);
  const bench = sortKey ? [] : players.filter((p) => !p.starter);
  const fmtCell = (p, k) => (k === "fgp" || k === "tpp" || k === "ftp") ? (p[k] == null ? "–" : p[k].toFixed(1)) : cell(p, k);
  const row = (p) => h("tr", { class: `${p.on ? "" : "bench"} ${p.out ? "out" : ""}` }, playerCell(p, p.on ? "●" : ""), ...BOX_COLS.map(([k]) => h("td", { class: k === "pts" ? "pts" : "" }, fmtCell(p, k))));
  const tot = t.totals;
  const totals = h("tr", { class: "total" }, h("td", { class: "l" }, "Team"), ...BOX_COLS.map(([k]) => h("td", {}, k === "min" ? "" : k === "pm" ? "" : k === "oreb" ? "" : fmtCell(tot, k))));
  const head = h("tr", {}, h("th", { class: "l" }, "Player"), ...BOX_COLS.map(([k, l]) => h("th", {
    class: `sortable ${S.boxSort === k ? "sorted" : ""}`,
    onclick: () => { S.boxSort = S.boxSort === k ? null : (["fg", "tp", "ft"].includes(k) ? { fg: "fgm", tp: "tpm", ft: "ftm" }[k] : k); renderBox(); },
  }, l)));
  const body = [];
  if (!sortKey) body.push(h("tr", { class: "sep" }, h("td", { class: "l", colspan: BOX_COLS.length + 1 }, "Starters")));
  body.push(...starters.map(row));
  if (bench.length) { body.push(h("tr", { class: "sep" }, h("td", { class: "l", colspan: BOX_COLS.length + 1 }, "Bench"))); body.push(...bench.map(row)); }
  body.push(totals);
  root.replaceChildren(h("table", { class: "stats" }, h("thead", {}, head), h("tbody", {}, body)));
}

// ───────────────────────── play-by-play ─────────────────────────
const SCORE_RE = /^(.+?) \| ([0-9]+:[0-9]{2}) \| (.+?): (\d+)\s+(.+?): (\d+)$/;
const feed = { block: null, lines: [], last: [0, 0] };

function classifyLines(lines) {
  const text = lines.join(" ").toLowerCase();
  if (/turnover|steal|stolen|picks? (him|it) off|offensive foul|travel|shot clock violation|out of bounds off|loses (it|the handle)/.test(text)) return "tov";
  if (/foul/.test(text)) return "foul";
  if (/miss|no good|off the rim|won.t drop|spins off|rims out|comes? off long|blocked|swat/.test(text)) return "miss";
  return "";
}

function newBlock() {
  feed.block = h("div", { class: "ev pending" }, h("div", { class: "rail" }), h("div", { class: "body" }));
  feed.lines = [];
}

function addFeedLine(line) {
  const root = $("#feed");
  const empty = $(".empty", root);
  if (empty) empty.remove();
  if (!line.trim()) return;
  const m = line.match(SCORE_RE);
  if (m) { closeBlock(m); return; }
  if (/^-{2,}\s*(start|end) of/i.test(line) || /^(halftime|end of regulation|final)/i.test(line.trim())) {
    root.prepend(h("div", { class: "ev period" }, line.replace(/-/g, "").trim().toUpperCase()));
    return;
  }
  if (line.startsWith("[GUI]") || line.startsWith("[Simulation")) {
    root.prepend(h("div", { class: "ev sys" }, h("div", { class: "rail" }), h("div", {}, line.replace("[GUI] ", ""))));
    return;
  }
  if (!feed.block) newBlock();
  feed.lines.push(line);
}

function closeBlock(m) {
  const root = $("#feed");
  const [, period, clock, , sa, , sb] = m;
  const now = [Number(sa), Number(sb)];
  const delta = [now[0] - feed.last[0], now[1] - feed.last[1]];
  feed.last = now;
  if (!feed.block || !feed.lines.length) { newBlock(); return; }
  const block = feed.block;
  const scored = delta[0] > 0 ? 0 : delta[1] > 0 ? 1 : -1;
  const pts = scored >= 0 ? delta[scored] : 0;
  const kind = scored >= 0 ? (pts >= 3 ? "three" : "score") : classifyLines(feed.lines);
  const isDunk = scored >= 0 && /dunk|slam|jam|throws it down|hammers/i.test(feed.lines.join(" "));
  block.className = `ev ${kind} ${isDunk ? "dunk" : ""}`;
  block.dataset.kind = scored >= 0 ? "score" : (kind || "other");
  const team = scored >= 0 ? S.identities[scored] : null;
  if (team) block.querySelector(".rail").style.background = team.color;
  const body = block.querySelector(".body");
  const result = feed.lines[feed.lines.length - 1];
  const detail = feed.lines.slice(0, -1);
  body.append(...[
    h("span", { class: "sc" }, `${period} ${clock} · ${now[0]}-${now[1]}`),
    h("div", { class: scored >= 0 ? "result made" : "result" }, result),
    detail.length ? h("div", { class: "detail" }, detail.slice(-2).join(" ")) : null,
  ].filter(Boolean));
  root.prepend(block);
  applyFeedFilter(block);
  while (root.children.length > 450) root.lastChild.remove();
  newBlock();
}

function applyFeedFilter(el) {
  const k = el.dataset.kind;
  let show = true;
  if (S.feedFilter === "scores") show = k === "score";
  else if (S.feedFilter === "key") show = k === "score" || k === "tov" || k === "foul";
  el.style.display = show ? "" : "none";
}

// ───────────────────────── game flow chart ─────────────────────────
function periodIndex(label) {
  const l = (label || "").toLowerCase();
  const q = { "1st": 0, "2nd": 1, "3rd": 2, "4th": 3 }[l];
  if (q !== undefined) return q;
  const ot = l.match(/ot\s*(\d*)/);
  if (ot) return 3 + (Number(ot[1]) || 1);
  return 0;
}
function flowPoints() {
  const qLen = S.rules === "FIBA" ? 600 : 720;
  return S.flow.map(([period, clock, margin]) => {
    const idx = periodIndex(period);
    const [mm, ss] = (clock || "0:00").split(":").map(Number);
    const left = mm * 60 + ss;
    const elapsed = idx < 4 ? idx * qLen + (qLen - left) : 4 * qLen + (idx - 4) * 300 + (300 - left);
    return [elapsed, margin];
  });
}
function renderFlow(rootSel, height) {
  const root = $(rootSel);
  const pts = flowPoints();
  if (!pts.length) { root.replaceChildren(h("div", { class: "empty" }, "The scoring margin is drawn here as the game goes.")); return; }
  const qLen = S.rules === "FIBA" ? 600 : 720;
  const W = 1000, H = height, pad = 26;
  const maxT = Math.max(4 * qLen, pts[pts.length - 1][0]);
  const maxM = Math.max(8, ...pts.map((p) => Math.abs(p[1]))) * 1.15;
  const x = (t) => pad + (t / maxT) * (W - pad * 2);
  const y = (m) => H / 2 - (m / maxM) * (H / 2 - 14);
  const [A, B] = S.identities;
  let d = `M ${x(0)} ${y(0)}`;
  for (const [t, m] of pts) d += ` L ${x(t)} ${y(m)}`;
  const area = `${d} L ${x(pts[pts.length - 1][0])} ${y(0)} Z`;
  const svg = `
    <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" style="height:${H}px">
      <defs>
        <clipPath id="up${height}"><rect x="0" y="0" width="${W}" height="${H / 2}"/></clipPath>
        <clipPath id="dn${height}"><rect x="0" y="${H / 2}" width="${W}" height="${H / 2}"/></clipPath>
        <linearGradient id="ga${height}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${A?.color || "#4f8cff"}" stop-opacity=".55"/><stop offset="1" stop-color="${A?.color || "#4f8cff"}" stop-opacity=".05"/></linearGradient>
        <linearGradient id="gb${height}" x1="0" x2="0" y1="1" y2="0"><stop offset="0" stop-color="${B?.color || "#f43f5e"}" stop-opacity=".55"/><stop offset="1" stop-color="${B?.color || "#f43f5e"}" stop-opacity=".05"/></linearGradient>
      </defs>
      ${[1, 2, 3].map((q) => `<line class="grid" x1="${x(q * qLen)}" x2="${x(q * qLen)}" y1="8" y2="${H - 8}"/>`).join("")}
      <line class="axis" x1="${pad}" x2="${W - pad}" y1="${y(0)}" y2="${y(0)}"/>
      <path d="${area}" fill="url(#ga${height})" clip-path="url(#up${height})"/>
      <path d="${area}" fill="url(#gb${height})" clip-path="url(#dn${height})"/>
      <path d="${d}" fill="none" stroke="rgba(232,237,246,.85)" stroke-width="1.6" vector-effect="non-scaling-stroke"/>
      <text x="${pad}" y="16">${A?.short || ""} +${Math.round(maxM / 1.15)}</text>
      <text x="${pad}" y="${H - 6}">${B?.short || ""} +${Math.round(maxM / 1.15)}</text>
      ${["Q1", "Q2", "Q3", "Q4"].map((q, i) => `<text x="${x(i * qLen + qLen / 2) - 8}" y="${H - 6}">${q}</text>`).join("")}
    </svg>`;
  root.innerHTML = svg;
  const last = pts[pts.length - 1][1];
  const big = Math.max(...pts.map((p) => p[1])), small = Math.min(...pts.map((p) => p[1]));
  $("#flowNote").textContent = `Largest leads: ${A?.short || "A"} ${Math.max(0, big)}, ${B?.short || "B"} ${Math.max(0, -small)} · now ${last > 0 ? `${A?.short} by ${last}` : last < 0 ? `${B?.short} by ${-last}` : "tied"}`;
}

// ───────────────────────── live data ─────────────────────────
function applyLive(snap) {
  S.live = snap;
  if (snap?.teams) {
    S.identities = snap.teams.map((t) => ({ name: t.name, short: t.short, year: t.year, initials: t.initials, logo: t.logo, color: t.color, color2: t.color2 }));
    const scores = snap.teams.map((t) => t.score);
    const changed = [scores[0] !== S.score[0], scores[1] !== S.score[1]];
    S.score = scores;
    renderScoreboard();
    changed.forEach((c, i) => c && bumpScore(i));
  }
  renderCourt();
  renderCompare();
  if ($("#view-box").classList.contains("active")) renderBox();
}

function applyScore(msg) {
  $("#sbPeriod").textContent = (msg.period || "").toUpperCase();
  $("#sbClock").textContent = msg.clock || "";
  S.flow.push([msg.period, msg.clock, Number(msg.score_a) - Number(msg.score_b)]);
  const newScore = [Number(msg.score_a), Number(msg.score_b)];
  const changed = [newScore[0] !== S.score[0], newScore[1] !== S.score[1]];
  S.score = newScore;
  renderScoreboard();
  changed.forEach((c, i) => c && bumpScore(i));
  renderFlow("#flowMini", 170);
  if ($("#view-flow").classList.contains("active")) renderFlow("#flowBig", 420);
}

function applyStatus(s) {
  S.active = !!s.active; S.paused = !!s.paused; S.speed = s.speed ?? S.speed;
  $("#speedVal").textContent = `${Number(S.speed).toFixed(S.speed < 10 ? 1 : 0)}×`;
  $("#pauseText").textContent = S.paused ? "Resume" : "Pause";
  $("#pauseIcon").textContent = S.paused ? "▶" : "❚❚";
  $("#start").disabled = S.active;
  const live = S.active && !S.paused;
  setStatus(s.text || (S.active ? "Running" : "Ready"), live);
}

function resetGame(msg) {
  S.live = null; S.flow = []; S.score = [0, 0]; S.prevOnCourt = [new Set(), new Set()];
  S.identities = msg.teams || [null, null];
  (msg.teams || []).forEach((t, i) => {     // keep the setup bar on the teams actually playing
    const full = S.meta?.teams.find((x) => x.name === t.name) || t;
    S.pickers?.[i]?.set(full);
    if (i === 0) S.teamA = t.name; else S.teamB = t.name;
  });
  feed.block = null; feed.lines = []; feed.last = [0, 0];
  $("#feed").replaceChildren(h("div", { class: "empty" }, "Tipping off…"));
  $("#sbSeries").textContent = "";
  $("#sbPeriod").textContent = "1ST"; $("#sbClock").textContent = S.rules === "FIBA" ? "10:00" : "12:00";
  $("#simSeries").classList.toggle("hidden", msg.mode !== "Playoff series");
  renderScoreboard(); renderCourt(); renderCompare(); renderFlow("#flowMini", 170);
}

function connect() {
  const conn = $("#conn");
  const es = new EventSource("/api/events");
  es.onopen = async () => {
    conn.className = "conn ok"; conn.lastElementChild.textContent = "Connected";
    const st = await api.get("/api/state");
    applyStatus({ text: st.status, active: st.active, paused: st.paused, speed: st.speed });
    if (st.live) applyLive(st.live);
    if (st.flow?.length) { S.flow = st.flow; renderFlow("#flowMini", 170); }
  };
  es.onerror = () => { conn.className = "conn bad"; conn.lastElementChild.textContent = "Reconnecting…"; };
  es.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    switch (msg.type) {
      case "reset": resetGame(msg); break;
      case "pbp": addFeedLine(msg.text); break;
      case "score": applyScore(msg); break;
      case "live": applyLive(msg.data); break;
      case "status": applyStatus(msg); break;
      case "series":
        if (msg.series_status?.startsWith("SERIES FINAL")) $("#sbSeries").textContent = `${S.seriesText || "Series"} · Final`;
        else if (msg.series_status) { S.seriesText = msg.series_status; $("#sbSeries").textContent = msg.series_status; }
        else if (msg.game_result) toast(msg.game_result);
        break;
      case "finished": toast("Final. The box score has the full line."); break;
    }
  };
}

// ───────────────────────── boot ─────────────────────────
async function boot() {
  S.meta = await api.get("/api/meta");
  const modeSel = $("#mode");
  for (const m of S.meta.modes) modeSel.append(h("option", { value: m.name, disabled: !m.ready }, m.ready ? m.name : `${m.name} (Tk app for now)`));
  modeSel.addEventListener("change", () => { S.mode = modeSel.value; });

  const pickA = makePicker($("#pickA"), (t) => { S.teamA = t.name; });
  const pickB = makePicker($("#pickB"), (t) => { S.teamB = t.name; });
  const preferred = S.meta.teams.filter((t) => t.year === "2027");
  const first = preferred[0] || S.meta.teams[0], second = preferred[1] || S.meta.teams[1];
  S.teamA = first.name; S.teamB = second.name;
  pickA.set(first); pickB.set(second);
  S.pickers = [pickA, pickB];

  $$("#rules button").forEach((b) => b.addEventListener("click", () => {
    $$("#rules button").forEach((x) => x.classList.toggle("on", x === b)); S.rules = b.dataset.v;
  }));
  $("#start").addEventListener("click", async () => {
    try { await api.post("/api/start", { mode: S.mode, teamA: S.teamA, teamB: S.teamB, rules: S.rules }); }
    catch (err) { toast(err.message, "err"); }
  });
  $("#pause").addEventListener("click", () => api.post("/api/control", { action: "pause" }).catch((e) => toast(e.message, "err")));
  const speeds = [0.5, 0.75, 1, 1.5, 2, 3, 5, 10, 20];
  const stepSpeed = (dir) => {
    let i = speeds.findIndex((s) => s >= S.speed - 1e-6); if (i < 0) i = speeds.length - 1;
    const next = speeds[Math.max(0, Math.min(speeds.length - 1, i + dir))];
    api.post("/api/control", { action: "speed", value: next }).catch((e) => toast(e.message, "err"));
  };
  $("#slower").addEventListener("click", () => stepSpeed(-1));
  $("#faster").addEventListener("click", () => stepSpeed(1));
  $$("[data-jump]").forEach((b) => b.addEventListener("click", () => api.post("/api/control", { action: "jump", value: b.dataset.jump }).catch((e) => toast(e.message, "err"))));
  $("#simSeries").addEventListener("click", () => api.post("/api/control", { action: "simSeries" }).catch((e) => toast(e.message, "err")));

  $$("#feedFilter button").forEach((b) => b.addEventListener("click", () => {
    $$("#feedFilter button").forEach((x) => x.classList.toggle("on", x === b)); S.feedFilter = b.dataset.v;
    $$("#feed .ev").forEach((el) => el.dataset.kind && applyFeedFilter(el));
  }));
  $$("#boxTeam button").forEach((b) => b.addEventListener("click", () => {
    $$("#boxTeam button").forEach((x) => x.classList.toggle("on", x === b)); S.boxTeam = Number(b.dataset.v); renderBox();
  }));
  $$("#nav .nav-item[data-view]").forEach((b) => b.addEventListener("click", () => {
    $$("#nav .nav-item").forEach((x) => x.classList.toggle("active", x === b));
    $$(".view").forEach((v) => v.classList.toggle("active", v.id === `view-${b.dataset.view}`));
    if (b.dataset.view === "box") renderBox();
    if (b.dataset.view === "flow") renderFlow("#flowBig", 420);
  }));
  document.addEventListener("keydown", (e) => {
    if (e.target.matches("input, select, textarea")) return;
    if (e.code === "Space") { e.preventDefault(); $("#pause").click(); }
  });

  renderScoreboard(); renderCourt(); renderCompare(); renderFlow("#flowMini", 170);
  connect();
}

boot().catch((err) => toast(`Could not load: ${err.message}`, "err"));
