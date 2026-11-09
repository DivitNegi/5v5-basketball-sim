// 5v5 Sim — browser UI (no build step, no external libraries)

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

// Screens redraw their whole contents on every update (a new play, a sort click, an expanded row). A redrawn element starts at scroll
// 0, so every scrolled table and the page itself jumped back to the top. Replacing the contents of any element that has an id now
// remembers the scroll of the container, of everything scrolled inside it (found again by its position), and of the page.
const KEEP_SCROLL_SKIP = new Set(["rawlog", "feed"]);
function scrollSnapshot(root) {
  const out = [];
  const visit = (el, path) => {
    if (el.scrollTop > 0 || el.scrollLeft > 0) out.push([path.slice(), el.scrollTop, el.scrollLeft]);
    let i = 0;
    for (const child of el.children) { path.push(i++); visit(child, path); path.pop(); }
  };
  visit(root, []);
  return out;
}
function scrollRestore(root, snap) {
  for (const [path, top, left] of snap) {
    let el = root;
    for (const i of path) { el = el?.children?.[i]; if (!el) break; }
    if (el) { el.scrollTop = top; el.scrollLeft = left; }
  }
}
const nativeReplaceChildren = Element.prototype.replaceChildren;
Element.prototype.replaceChildren = function (...nodes) {
  if (!this.id || KEEP_SCROLL_SKIP.has(this.id)) return nativeReplaceChildren.apply(this, nodes);
  const snap = scrollSnapshot(this), x = window.scrollX, y = window.scrollY;
  const rootTop = this.scrollTop, rootLeft = this.scrollLeft;
  nativeReplaceChildren.apply(this, nodes);
  this.scrollTop = rootTop; this.scrollLeft = rootLeft;
  scrollRestore(this, snap.filter((s) => s[0].length));
  if (window.scrollY !== y || window.scrollX !== x) window.scrollTo(x, y);
};
const nativeReplaceWith = Element.prototype.replaceWith;
Element.prototype.replaceWith = function (...nodes) {
  const next = nodes.length === 1 && nodes[0] instanceof Element ? nodes[0] : null;
  if (!this.id || !next) return nativeReplaceWith.apply(this, nodes);
  const snap = scrollSnapshot(this), x = window.scrollX, y = window.scrollY;
  nativeReplaceWith.apply(this, nodes);
  for (const [path, top, left] of snap) {
    let el = next;
    for (const i of path) { el = el?.children?.[i]; if (!el) break; }
    if (el) { el.scrollTop = top; el.scrollLeft = left; }
  }
  if (window.scrollY !== y || window.scrollX !== x) window.scrollTo(x, y);
};

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
  feedFilter: "raw", boxTeam: 0, boxSort: null,
  gameNo: 1, gameSnapshots: new Map(), goodPlays: [], lastScoreClock: null,
};

function cleanBadges(values) {
  const seen = new Set();
  return (values || []).map((value) => String(value).replace(/_/g, " ").trim().toLowerCase()
    .replace(/\s+(bronze|silver|gold|hall of fame|hof)$/i, "").trim())
    .filter((value) => value && !seen.has(value) && seen.add(value))
    .map((value) => value.charAt(0).toUpperCase() + value.slice(1));
}

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
      h("div", { class: "court-scroll" }, h("table", { class: "stats" }, h("thead", {}, h("tr", {}, h("th", { class: "l" }, "Player"), ...STAT_COLS.map(([, l]) => h("th", {}, l)))), h("tbody", {}, rows))));
  });
  const keep = $$("#court .court-scroll").map((el) => el.scrollLeft);   // a re-render must not snap the scroll back
  root.replaceChildren(...blocks);
  $$("#court .court-scroll").forEach((el, i) => { el.scrollLeft = keep[i] || 0; });
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
  feed.miss = false;
}

// "X will guard Y" opening-matchup lines are left out of the play-by-play
const GUARD_RE = /\bwill guard\b|^\s*When .+ are on offense:\s*$/;
const rawState = { last: [0, 0], namesKey: "", re: null };
// glide to the newest line; repeated calls just re-aim the same glide
function pinBottom(root) {
  root._stick = true; root._auto = true;
  clearTimeout(root._autoT);
  root.scrollTo({ top: root.scrollHeight, behavior: "smooth" });
  root._autoT = setTimeout(() => {
    if (root._auto) root.scrollTo({ top: root.scrollHeight, behavior: "instant" });   // the glide did not finish (busy or background tab): land exactly on the newest line
    root._auto = false; root._stick = root.scrollHeight - root.scrollTop - root.clientHeight < 48; if (root._stick) { root._behind = 0; } syncLatestButton();
  }, 450);
}
// the "Jump to latest" button: visible only while you are scrolled up, with how many new plays you are missing
function syncLatestButton() {
  const root = $("#rawlog"), btn = $("#pbpLatest");
  if (!btn) return;
  const behind = !root._stick && root.scrollHeight - root.scrollTop - root.clientHeight > 80;
  btn.classList.toggle("hidden", !behind || S.feedFilter !== "raw");
  btn.textContent = root._behind ? `Jump to latest · ${root._behind} new ⤓` : "Jump to latest ⤓";
}
const escHtml = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
function nameRegex() {
  const names = (S.live?.teams || []).flatMap((t) => (t.box || []).map((p) => p.name)).filter(Boolean);
  const key = names.join("|");
  if (key !== rawState.namesKey) {
    rawState.namesKey = key;
    rawState.re = names.length ? new RegExp(`(${names.sort((x, y) => y.length - x.length).map((n) => escHtml(n).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`, "g") : null;
  }
  return rawState.re;
}
function rawLine(line, shot) {
  const root = $("#rawlog");
  root.querySelector(".empty")?.remove();
  if (!root.dataset.watch) {   // follow the newest line until the user scrolls up; following resumes when they scroll back to the bottom
    root.dataset.watch = "1"; root._stick = true;
    // our own smooth scrolling must not look like the user scrolling away: only user input (wheel, touch, keys, scrollbar drag) can unpin
    const userScrolling = () => { root._auto = false; clearTimeout(root._autoT); };
    ["wheel", "touchstart", "keydown", "pointerdown"].forEach((ev) => root.addEventListener(ev, userScrolling, { passive: true }));
    root.addEventListener("scroll", () => {
      if (root._auto) return;
      root._stick = root.scrollHeight - root.scrollTop - root.clientHeight < 48;
      if (root._stick) root._behind = 0;
      syncLatestButton();
    }, { passive: true });
    $("#pbpLatest").addEventListener("click", () => { root._behind = 0; pinBottom(root); syncLatestButton(); });
  }
  const t = line.trim();
  let el;
  const sm = t.match(SCORE_RE);
  if (sm) {
    const [, period, clock, na, sa, nb, sb] = sm;
    const idA = S.identities?.find((x) => x && x.name === na), idB = S.identities?.find((x) => x && x.name === nb);
    const now = [Number(sa), Number(sb)];
    const scored = now[0] > rawState.last[0] ? 0 : now[1] > rawState.last[1] ? 1 : -1;
    if (scored >= 0 && root.lastElementChild) { root.lastElementChild.classList.remove("miss", "tov", "foul"); root.lastElementChild.classList.add("made"); }   // the play that scored is a make, whatever else its words say
    rawState.last = now;
    const side = (id, name, sc, hot) => h("span", { class: `sb-side ${hot ? "hot" : ""}`, style: { "--c": id?.color || "#64748b" } }, h("span", { class: "sb-name" }, id?.short || name.replace(/^\d{4} /, "")), h("b", {}, sc));
    el = h("div", { class: "pbp-score" }, h("span", { class: "pbp-clock" }, `${period} · ${clock}`), side(idA, na, sa, scored === 0), h("span", { class: "sb-dash" }, "–"), side(idB, nb, sb, scored === 1));
  } else if (/^-{2,}\s*(start|end) of|^(halftime|end of regulation|final)/i.test(t)) {
    el = h("div", { class: "pbp-period" }, h("span", {}, t.replace(/-/g, "").trim().toUpperCase()));
    rawState.last = rawState.last;
  } else if (/^\[(GUI|Simulation)/.test(t)) {
    el = h("div", { class: "pbp-sys" }, t.replace(/^\[GUI\]\s*/, ""));
  } else {
    el = h("div", { class: "pbp-line" });
    let html = escHtml(line.replace(/\s+$/, ""));
    const re = nameRegex();
    if (re) html = html.replace(re, '<b class="nm">$1</b>');
    el.innerHTML = html;
    if (shot === "make") el.classList.add("made");          // the engine says how the shot ended: no guessing from the wording
    else if (shot === "miss") el.classList.add("miss");
    else if (/steal|stolen|turnover|loses the|travel/i.test(t)) el.classList.add("tov");
    else if (/foul/i.test(t)) el.classList.add("foul");
    else if (/\b(misses|missed|no good|rims? out|off the (iron|rim|glass|backboard)|front rim|back rim|bricks?|clanks?|blocked|swats?|won.t drop|spins (off|out)|comes? off long|falls short)\b/i.test(t)) el.classList.add("miss");
  }
  root.append(el);
  while (root.children.length > 5000) root.firstChild.remove();
  if (!root._stick && el.className !== "pbp-sys") { root._behind = (root._behind || 0) + 1; syncLatestButton(); }
  if (root._stick) root._wantPin = true;   // the batch scrolls once, after all its lines are in
}

function addFeedLine(line, shot) {
  const root = $("#feed");
  const empty = $(".empty", root);
  if (empty) empty.remove();
  if (GUARD_RE.test(line)) return;
  if (!line.trim() && !$("#rawlog").lastChild?.textContent) return;
  rawLine(line, shot);
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
  if (shot === "miss") feed.miss = true;
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
  const kind = scored >= 0 ? (pts >= 3 ? "three" : "score") : (feed.miss ? "miss" : classifyLines(feed.lines));
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
  const positive = scored >= 0
    ? feed.lines.filter((line) => /\b(buries|drills|hits|makes|cash|scores|finishes|slams|dunks|lays? it in|knocks? down|connects|assist|finds)\b/i.test(line))
    : feed.lines.filter((line) => /\b(steals?|stolen|picks? .* off|blocks?|swats?|chasedown|forces? the turnover|draws? (?:the )?charge)\b/i.test(line));
  for (const line of positive) {
    S.goodPlays.unshift({ game: S.gameNo, period, clock, score: `${now[0]}-${now[1]}`, text: line });
  }
  S.goodPlays.length = Math.min(S.goodPlays.length, 3000);
  S.plays.unshift({ period, clock, score: `${now[0]}-${now[1]}`, text: feed.lines.join(" ") });
  S.plays.length = Math.min(S.plays.length, 1500);
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
function flowElapsed(period, clock) {
  const qLen = S.rules === "FIBA" ? 600 : 720;
  const idx = periodIndex(period);
  const [mm, ss] = (clock || "0:00").split(":").map(Number);
  const left = mm * 60 + ss;
  return idx < 4 ? idx * qLen + (qLen - left) : 4 * qLen + (idx - 4) * 300 + (300 - left);
}
function flowPoints() {
  // time only moves forward: a point that goes backwards is a replay of one already drawn (e.g. after a reconnect)
  const out = [];
  for (const [period, clock, margin] of S.flow) {
    const t = flowElapsed(period, clock);
    if (out.length && t < out[out.length - 1][0]) continue;
    out.push([t, margin]);
  }
  return out;
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
    </svg>`;
  const lead = Math.round(maxM / 1.15);
  const dot = (c) => `<i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${c};margin-right:6px"></i>`;
  const legend = `<div class="flow-legend"><span>${dot(A?.color || "#4f8cff")}${A?.short || "A"} ahead (up)</span><span>${dot(B?.color || "#f43f5e")}${B?.short || "B"} ahead (down)</span><span class="muted">scale ±${lead}</span></div>`;
  const qlabels = `<div class="flow-q">${["Q1", "Q2", "Q3", "Q4"].map((q, i) => `<span style="left:${100 * x(i * qLen + qLen / 2) / W}%">${q}</span>`).join("")}</div>`;
  root.innerHTML = legend + `<div class="flow-plot">${svg}${qlabels}</div>`;
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

function applyScore(msg, paint = true) {
  const startsFresh = /^1st$/i.test(msg.period || "") && /^(12|10):00$/.test(msg.clock || "") && Number(msg.score_a) === 0 && Number(msg.score_b) === 0;
  if (startsFresh && S.lastScoreClock === "0:00" && S.live) {
    S.gameSnapshots.set(S.gameNo, structuredClone(S.live));
    S.gameNo += 1;
  }
  $("#sbPeriod").textContent = (msg.period || "").toUpperCase();
  $("#sbClock").textContent = msg.clock || "";
  const lastFlow = S.flow[S.flow.length - 1];
  if (!lastFlow || flowElapsed(msg.period, msg.clock) >= flowElapsed(lastFlow[0], lastFlow[1])) S.flow.push([msg.period, msg.clock, Number(msg.score_a) - Number(msg.score_b)]);
  const newScore = [Number(msg.score_a), Number(msg.score_b)];
  const before = S.score.slice();
  S.score = newScore;
  S.lastScoreClock = msg.clock || null;
  if (paint) paintScore(before);
}
function paintScore(before) {
  renderScoreboard();
  [0, 1].forEach((i) => { if (S.score[i] !== before[i]) bumpScore(i); });
  renderFlow("#flowMini", 170);
  if ($("#view-flow").classList.contains("active")) renderFlow("#flowBig", 420);
}

function applyStatus(s) {
  S.active = !!s.active; S.paused = !!s.paused; S.speed = s.speed ?? S.speed;
  $("#speedVal").textContent = `${Number(S.speed).toFixed(S.speed < 10 ? 1 : 0)}×`;
  $("#pauseText").textContent = S.paused ? "Resume" : "Pause";
  $("#pauseIcon").textContent = S.paused ? "▶" : "❚❚";
  $("#start").disabled = S.active;
  renderSeasonBar();
  const live = S.active && !S.paused;
  setStatus(s.text || (S.active ? "Running" : "Ready"), live);
}

function resetGame(msg) {
  const quietSeason = isSeasonMode(msg.mode) && msg.mode !== "2027 play-in & playoffs";
  $("#scoreboard").classList.toggle("hidden", quietSeason);
  $("#simSeries").classList.toggle("hidden", !["Playoff series", "2027 play-in & playoffs"].includes(msg.mode));
  $("#simPlayoffs").classList.toggle("hidden", msg.mode !== "2027 play-in & playoffs");
  if (msg.mode === "2027 play-in & playoffs") { $('#nav .nav-item[data-view="bracket"]').click(); BR.selected = null; return; }
  if (isSeasonMode(msg.mode)) {
    $('#nav .nav-item[data-view="season"]').click();
    SE.data = null; SE.players = null; refreshSeason();
    return;
  }
  S.plays = []; S.goodPlays = []; S.gameNo = 1; S.gameSnapshots = new Map(); S.lastScoreClock = null;
  S.live = null; S.flow = []; S.score = [0, 0]; S.prevOnCourt = [new Set(), new Set()];
  S.identities = msg.teams || [null, null];
  (msg.teams || []).forEach((t, i) => {     // keep the setup bar on the teams actually playing
    if (!t) return;
    const full = S.meta?.teams.find((x) => x.name === t.name) || t;
    S.pickers?.[i]?.set(full);
    if (i === 0) S.teamA = t.name; else S.teamB = t.name;
  });
  feed.block = null; feed.lines = []; feed.last = [0, 0];
  $("#feed").replaceChildren(h("div", { class: "empty" }, "Tipping off…"));
  $("#rawlog").replaceChildren(h("div", { class: "empty" }, "Tipping off…")); $("#rawlog")._stick = true; $("#rawlog")._behind = 0; syncLatestButton();
  rawState.last = [0, 0];
  $("#sbSeries").textContent = "";
  $("#sbPeriod").textContent = "1ST"; $("#sbClock").textContent = S.rules === "FIBA" ? "10:00" : "12:00";
  $("#simSeries").classList.toggle("hidden", !["Playoff series", "2027 play-in & playoffs"].includes(msg.mode));
  $("#simPlayoffs").classList.toggle("hidden", msg.mode !== "2027 play-in & playoffs");
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
    api.get("/api/trade/prompt").then((r) => showTradePrompt(r.prompt)).catch(() => {});
    if (st.flow?.length) { S.flow = st.flow; renderFlow("#flowMini", 170); }
  };
  es.onerror = () => { conn.className = "conn bad"; conn.lastElementChild.textContent = "Reconnecting…"; };
  es.onmessage = (e) => { evQueue.push(JSON.parse(e.data)); scheduleDrain(); };
}

// Events are queued and applied in short batches (about 12 ms each): thousands of plays and score updates arrive in a few seconds
// during a "sim to" jump, and drawing every one separately froze the page. The scoreboard is drawn once per batch with the latest score,
// like Tk's polling, while every play still lands in the log and every score still lands in the game-flow data.
const evQueue = [];
let drainScheduled = false;
function scheduleDrain() {
  if (drainScheduled) return;
  drainScheduled = true;
  let ran = false;
  const run = () => { if (ran) return; ran = true; drainScheduled = false; drainEvents(); };
  requestAnimationFrame(run);
  setTimeout(run, 100);   // a hidden tab does not run animation frames
}
// the engine says the shot just described missed (a rebound is being resolved): colour that line red
function markLastMiss() {
  const last = $("#rawlog").lastElementChild;
  if (last && last.classList.contains("pbp-line") && !last.classList.contains("made")) { last.classList.remove("tov", "foul"); last.classList.add("miss"); }
  feed.miss = true;
}
function drainEvents() {
  const t0 = performance.now();
  const before = S.score.slice();
  let sawScore = false, lastLive = null;
  while (evQueue.length && performance.now() - t0 < 12) {
    const msg = evQueue.shift();
    if (msg.type === "pbp") addFeedLine(msg.text, msg.shot);
    else if (msg.type === "shotmark") markLastMiss();
    else if (msg.type === "score") { applyScore(msg, false); sawScore = true; }
    else if (msg.type === "live") lastLive = msg;
    else handleEvent(msg);
  }
  if (sawScore) paintScore(before);
  if (lastLive) { applyLive(lastLive.data); scheduleGameViews(); scheduleStats(); }
  const log = $("#rawlog");
  if (log._wantPin) { log._wantPin = false; if (log._stick) pinBottom(log); }
  if (evQueue.length) scheduleDrain();
}
function handleEvent(msg) {
    switch (msg.type) {
      case "reset": resetGame(msg); break;
      case "status": applyStatus(msg); break;
      case "series":
        if (msg.series_status?.startsWith("SERIES FINAL")) $("#sbSeries").textContent = `${S.seriesText || "Series"} · Final`;
        else if (msg.series_status) { S.seriesText = msg.series_status; $("#sbSeries").textContent = msg.series_status; }
        break;
      case "season": SE.data = { ...(SE.data || {}), state: msg.season }; renderSeasonBar(msg.season); scheduleSeasonRefresh(); break;
      case "sections": scheduleSeasonRefresh(); scheduleStats(); break;
      case "draft": loadDraft(); break;
      case "trade_prompt": showTradePrompt(msg.data); break;
      case "bracket": scheduleBracket(); break;
      case "finished": scheduleStats(); scheduleSeasonRefresh(); break;
    }
}

// ───────────────────────── season ─────────────────────────
const SEASON_MODE_NAMES = ["2021 season", "2022 season", "2023 season", "2026 season", "2027 season", "2018 season", "2027 play-in"];
const isSeasonMode = (m) => SEASON_MODE_NAMES.some((x) => (m || "").startsWith(x));
const SE = { tab: "standings", data: null, players: null, sort: "pts", filter: "", loading: false };

async function refreshSeason() {
  if (SE.loading) return;
  SE.loading = true;
  try {
    SE.data = await api.get("/api/season");
    renderSeasonBar();
    if ($("#view-season").classList.contains("active")) {
      if (SE.tab === "players") { const q = new URLSearchParams({ team: AV.team, quarter: AV.quarter, rank: AV.rank, source: AV.source }); AV.data = await api.get(`/api/season/avg?${q}`); }
      if (SE.tab === "advanced") SE.advStats = await api.get("/api/stats?kind=advanced&source=Season&team=All+teams&quarter=All");
      if (SE.tab === "teams") SE.teams = (await api.get("/api/season/teams")).teams;
      if (SE.tab === "shots") { SH.source = SH.source || "Season"; await loadShots2(); }
      if (SE.tab === "recap") RC.data = await api.get(`/api/season/recap?team=${encodeURIComponent(RC.team)}`);
      if (SE.tab === "highs" && !HV.box) SE.highs = await api.get(`/api/season/highs?${new URLSearchParams({ view: HV.view, stat: HV.stat, team: HV.team })}`);
      if (SE.tab === "schedule" && SE.team) SE.sched = (await api.get(`/api/season/schedule?team=${encodeURIComponent(SE.team)}`)).games;
      renderSeasonBody();
    }
  } finally { SE.loading = false; }
}
let seasonTimer = null;
function scheduleSeasonRefresh() {
  if (seasonTimer) return;                       // one refresh at a time, at most every ~0.9s while games finish quickly
  seasonTimer = setTimeout(() => { seasonTimer = null; refreshSeason(); }, 900);
}

function renderSeasonBar(state) {
  const st = state || SE.data?.state;
  if (!st) return;
  const p = st.progress;
  const pct = p ? Math.min(100, (100 * p.completed) / Math.max(1, p.total)) : (st.ready ? 100 : 0);
  $("#seasonFill").style.width = `${pct}%`;
  $("#seasonProgText").textContent = st.ready ? "Regular season complete. Browse the tabs, or start the play-in and playoffs."
    : p ? `Game ${p.completed} of ${p.total} (${pct.toFixed(0)}%)` : "Season running…";
  $("#nextPost").classList.toggle("hidden", !st.ready || S.active);
}

function teamCell(r) {
  return h("div", { class: "tcell" }, logoEl({ logo: r.logo, color: r.color, initials: r.initials }), r.year ? h("span", { class: "yr" }, r.year) : null, h("span", { class: "pname" }, r.short));
}

function standingsTable(title, rows) {
  const body = rows.map((r, i) => h("tr", { class: i === 5 || i === 9 ? "cut" : "" },
    h("td", { class: "l" }, h("span", { class: "seed" }, i + 1), teamCell(r)),
    h("td", {}, r.wins), h("td", {}, r.losses), h("td", {}, (r.pct ?? 0).toFixed(3)), h("td", {}, r.diff > 0 ? `+${r.diff.toFixed(1)}` : (r.diff ?? 0).toFixed(1))));
  return h("div", {}, h("h3", {}, title),
    h("table", { class: "stats" }, h("thead", {}, h("tr", {}, h("th", { class: "l" }, "Team"), h("th", {}, "W"), h("th", {}, "L"), h("th", {}, "PCT"), h("th", {}, "DIFF"))), h("tbody", {}, body)));
}

function renderStandings() {
  const rows = SE.data?.standings || [];
  if (!rows.length) return h("div", { class: "empty" }, "Standings appear as the season runs.");
  const byConf = {};
  rows.forEach((r) => { (byConf[r.conference || "League"] ||= []).push(r); });
  return h("div", { class: "conf-grid" }, Object.keys(byConf).map((k) => standingsTable(k === "League" ? "League" : `${k} conference`, byConf[k])));
}

// "31.8 PPG, 6.5 RPG, ..." -> small stat tiles
function statChips(text) {
  const parts = (text || "").split(/,\s*|\s*\|\s*/).filter(Boolean);
  return h("div", { class: "chips" }, parts.map((s) => {
    const m = s.match(/^([+-]?[\d.]+(?:\/[\d.]+)?)\s*(.*)$/);
    return m ? h("div", { class: "chip" }, h("b", {}, m[1]), h("span", {}, m[2])) : h("div", { class: "chip wide" }, h("span", {}, s));
  }));
}
const shortTeam = (t) => t || "";   // award / race lines keep the year: "2021 Brooklyn Nets"
function raceCard(title, list) {
  return h("div", { class: "race-card" }, h("h3", {}, title),
    list.map((r, i) => {
      const id = identOf(r.team);
      return h("div", { class: `race-item ${i === 0 ? "lead" : ""}`, style: { "--c": id.color || "#64748b" } },
        h("div", { class: "rk" }, r.rank),
        h("div", { class: "rb" }, h("div", { class: "rtop" }, faceEl(r.player), h("div", {}, h("div", { class: "who" }, r.player), h("div", { class: "tm" }, logoEl(id), shortTeam(r.team)))), statChips(r.stats)));
    }));
}
function renderRaces() {
  const ready = !!SE.data?.state?.ready;
  if (!ready) {
    const races = SE.data?.races || {};
    const titles = { mvp: "MVP race", dpoy: "DPOY race", roy: "Rookie of the Year race" };
    const cards = Object.keys(titles).filter((k) => (races[k] || []).length).map((k) => raceCard(titles[k], races[k]));
    return cards.length ? h("div", {}, h("div", { class: "muted", style: { marginBottom: "10px" } }, "Live standings for the awards. They update as the season goes and become the official awards when it ends."), h("div", { class: "race-grid" }, cards))
      : h("div", { class: "empty" }, "The award races appear once games are played.");
  }
  const groups = {};
  (SE.data?.awards || []).forEach((a) => { (groups[a.award] ||= []).push(a); });
  // rookie awards sit above the All-Star entries
  const order = (name) => (/all-star/i.test(name) ? 2 : /rookie|roy/i.test(name) ? 1 : 0);
  const cleanName = (n) => String(n || "").replace(/^\d+\.\s*/, "").replace(/\s*\([A-Z]{1,2}\)\s*$/, "").trim();   // "1. LeBron James (G)" -> "LeBron James"
  const cards = Object.entries(groups).sort((x, y) => order(x[0]) - order(y[0])).map(([name, list]) => h("div", { class: "award-card" }, h("div", { class: "a" }, name),
    list.map((a) => {
      const id = identOf(a.team);
      const nm = cleanName(a.player);
      const isPlayer = !/\bwin\b/i.test(nm);
      return h("div", { class: "award-item", style: { "--c": id.color || "#64748b" } }, h("div", { class: "rtop" }, isPlayer ? faceEl(nm) : null, h("div", {}, h("div", { class: "p" }, a.player), h("div", { class: "tm" }, logoEl(id), shortTeam(a.team)))), statChips(a.stats));
    })));
  return cards.length ? h("div", {}, h("div", { class: "muted", style: { marginBottom: "10px" } }, "Final season awards"), h("div", { class: "award-grid" }, cards)) : h("div", { class: "empty" }, "Awards are given out when the regular season ends.");
}

const AV = { team: "All Teams", quarter: "All", rank: "Team order", source: "Season", sort: null, dir: -1, filter: "", data: null };
const AVG_RANKS = ["Team order", "GP", "MIN", "PTS", "REB", "ORB", "AST", "STL", "BLK", "TOV", "FG", "FG%", "3P", "3P%", "FT", "FT%", "TS%", "+/-", "STK", "AST/TOV", "STL/TOV", "PTS/48", "REB/48", "AST/48", "STL/48", "BLK/48"];
// [key, header, sort key, formatter]
const f1 = (v) => (v == null ? "–" : v.toFixed(1));
const PCOLS = [["gp", "GP", "gp", (v) => v], ["min", "MIN", "min", f1], ["pts", "PTS", "pts", f1], ["reb", "REB", "reb", f1], ["orb", "ORB", "orb", f1], ["ast", "AST", "ast", f1],
  ["stl", "STL", "stl", f1], ["blk", "BLK", "blk", f1], ["tov", "TOV", "tov", f1], ["fg", "FG", "fgm", null], ["fgp", "FG%", "fgp", f1], ["tp", "3P", "tpm", null], ["tpp", "3P%", "tpp", f1],
  ["ft", "FT", "ftm", null], ["ftp", "FT%", "ftp", f1], ["ts", "TS%", "ts", f1], ["pm", "+/-", "pm", (v) => (v > 0 ? `+${v.toFixed(1)}` : v.toFixed(1))]];
const madeAtt = (r, m, a) => `${r[m].toFixed(1)}/${r[a].toFixed(1)}`;

async function loadAvg() {
  const q = new URLSearchParams({ team: AV.team, quarter: AV.quarter, rank: AV.rank, source: AV.source });
  AV.data = await api.get(`/api/season/avg?${q}`);
  if (AV.data.source && AV.data.sources.length && !AV.data.sources.includes(AV.source)) AV.source = AV.data.source;
  renderSeasonBody();
}
function avSelect(label, value, options, onchange) {
  return h("label", { class: "fsel" }, h("span", { class: "muted" }, label), h("select", { onchange: (e) => onchange(e.target.value) }, options.map((o) => h("option", { value: o.v ?? o, selected: (o.v ?? o) === value }, o.t ?? o))));
}
function renderPlayers() {
  const d = AV.data;
  if (!d) { loadAvg(); return h("div", { class: "empty" }, "Loading player stats…"); }
  if (!d.teams.length) return h("div", { class: "empty" }, "Player stats appear once games are played.");
  const set = (k) => (v) => { AV[k] = v; if (k === "rank") { AV.sort = null; } loadAvg(); };
  const teamOpts = [{ v: "All Teams", t: "All Teams" }, ...d.teams.map((t) => ({ v: t, t: identOf(t).short }))];
  const q = AV.filter.toLowerCase();
  const input = h("input", { placeholder: "Search player…", value: AV.filter, oninput: (e) => { AV.filter = e.target.value; const pos = e.target.selectionStart; renderSeasonBody(); const i = $("#seasonBody input"); i.focus(); i.setSelectionRange(pos, pos); } });
  const filters = h("div", { class: "filters" }, avSelect("Team", AV.team, teamOpts, set("team")), avSelect("Quarter", AV.quarter, ["All", "Q1", "Q2", "Q3", "Q4", "OT"], set("quarter")),
    avSelect("Rank by", AV.rank, AVG_RANKS, set("rank")), avSelect("Show", d.source, (d.sources.length ? d.sources : [d.source]), set("source")), input);
  let rows = d.rows.filter((r) => !q || (r.kind === "player" && r.name.toLowerCase().includes(q)) || (r.kind === "team" && q.length < 1));
  let sorted = false;
  if (AV.sort && !d.flat) {
    rows = rows.filter((r) => r.kind === "player").sort((a, b) => AV.dir * ((a[AV.sort] ?? -1e9) - (b[AV.sort] ?? -1e9)));
    sorted = true;
  }
  const flat = d.flat || sorted;
  const sortBy = (key) => () => { if (d.flat) { AV.rank = "Team order"; AV.sort = key; AV.dir = -1; loadAvg(); return; } if (AV.sort === key) AV.dir *= -1; else { AV.sort = key; AV.dir = -1; } renderSeasonBody(); };
  const head = h("tr", {}, h("th", { class: "l sortable", onclick: () => { AV.sort = null; AV.dir = -1; if (d.flat) { AV.rank = "Team order"; loadAvg(); } else renderSeasonBody(); } }, flat ? "Team" : "Team / player"),
    ...(flat ? [h("th", { class: "l" }, "Player")] : []),
    ...PCOLS.map(([k, l, sk]) => h("th", { class: `sortable ${AV.sort === sk && !d.flat ? "sorted" : ""}`, onclick: sortBy(sk) }, l, AV.sort === sk && !d.flat ? (AV.dir < 0 ? " ▾" : " ▴") : "")));
  const cells = (r) => PCOLS.map(([k, , sk, fmt]) => {
    let v;
    if (k === "fg") v = madeAtt(r, "fgm", "fga"); else if (k === "tp") v = madeAtt(r, "tpm", "tpa"); else if (k === "ft") v = madeAtt(r, "ftm", "fta");
    else if (k === "min" && r.kind === "team") v = "--"; else v = fmt(r[sk]);
    return h("td", { class: k === "pts" ? "pts" : k === "pm" ? (r.pm > 0 ? "pm-pos" : r.pm < 0 ? "pm-neg" : "") : "" }, v);
  });
  const body = rows.map((r) => {
    if (r.kind === "team") return h("tr", { class: "team-row" }, h("td", { class: "l", colspan: 1 }, h("div", { class: "tcell" }, logoEl(r), h("span", { class: "pname" }, r.short), h("span", { class: "muted" }, `${AV.quarter === "All" ? "team avg" : AV.quarter + " avg"}`))), ...cells(r));
    const who = h("div", { class: "pcell" }, faceEl(r.name), h("span", { class: "pname" }, r.rank ? `${r.rank}. ${r.name}` : r.name));
    return flat ? h("tr", {}, h("td", { class: "l" }, h("div", { class: "tcell" }, logoEl(r), h("span", { class: "pname" }, r.short))), h("td", { class: "l" }, who), ...cells(r))
      : h("tr", {}, h("td", { class: "l" }, who), ...cells(r));
  });
  const note = d.flat ? `Ranked by ${AV.rank}${["FG%", "FT%", "3P%", "AST/TOV", "STL/TOV"].includes(AV.rank) || AV.rank.endsWith("/48") ? " (NBA leaderboard minimums apply)" : ""}` : AV.sort ? "Sorted across all players · click Team to go back to team order" : "Grouped by team · click any column to sort";
  return h("div", {}, filters, h("div", { class: "muted", style: { margin: "2px 2px 10px" } }, `${d.source} · per-game averages · ${note}`),
    h("div", { class: "table-wrap tall" }, h("table", { class: "stats avg" }, h("thead", {}, head), h("tbody", {}, body))));
}


const TCOLS = [["w", "W"], ["l", "L"], ["pts", "PTS"], ["opp", "OPP"], ["diff", "DIFF"], ["ortg", "ORtg"], ["drtg", "DRtg"], ["net", "NET"], ["pace", "PACE"], ["efg", "eFG%"], ["ts", "TS%"], ["tpp", "3P%"], ["reb", "REB"], ["ast", "AST"], ["tov", "TO"], ["oppfg", "OPP FG%"], ["opp3", "OPP 3P%"]];
const ACOLS = [["gp", "GP"], ["mpg", "MPG"], ["ts", "TS%"], ["efg", "eFG%"], ["usg", "USG%"], ["astto", "AST/TO"], ["p36", "PTS/36"], ["r36", "REB/36"], ["a36", "AST/36"], ["s36", "STK/36"], ["tpar", "3PAr"], ["ftr", "FTr"], ["pm", "+/-"]];

function simpleTable(head, rows) {
  return h("div", { class: "table-wrap" }, h("table", { class: "stats" }, h("thead", {}, head), h("tbody", {}, rows)));
}
function renderTeamsTab() {
  const rows = SE.teams || [];
  if (!rows.length) return h("div", { class: "empty" }, "Team stats appear once games are played.");
  const key = SE.tsort || "net";
  const lowIsGood = ["opp", "drtg", "tov", "oppfg", "opp3"].includes(key);
  const sorted = [...rows].sort((a, b) => lowIsGood ? (a[key] ?? 999) - (b[key] ?? 999) : (b[key] ?? -999) - (a[key] ?? -999));
  const head = h("tr", {}, h("th", { class: "l" }, "Team"), ...TCOLS.map(([k, l]) => h("th", { class: `sortable ${key === k ? "sorted" : ""}`, onclick: () => { SE.tsort = k; renderSeasonBody(); } }, l)));
  return simpleTable(head, sorted.map((t) => h("tr", {}, h("td", { class: "l" }, teamCell(t)), ...TCOLS.map(([k]) => h("td", { class: k === "net" ? "pts" : "" }, t[k] == null ? "–" : (k === "diff" || k === "net") && t[k] > 0 ? `+${t[k]}` : t[k])))));
}
function renderAdvancedTab() {
  const box = h("div", { id: "seasonAdv" });
  if (!SE.advStats || !SE.advStats.rows?.length) return h("div", { class: "empty" }, "Advanced stats appear once games are played.");
  renderStatsInto(box, SE.advStats);
  return box;
}
async function openScheduleBox(gid) {
  const d = await api.get(`/api/season/box?gid=${encodeURIComponent(gid)}`);
  if (d.error) { toast(d.error, "err"); return; }
  SE.sbox = d; renderSeasonBody();
}
function renderScheduleTab() {
  if (SE.sbox) {
    const b = SE.sbox;
    return h("div", {}, h("div", { class: "filters" }, h("button", { class: "btn", onclick: () => { SE.sbox = null; renderSeasonBody(); } }, "‹ Back to schedule"),
      h("b", {}, b.teams.map((t) => `${t.short} ${t.score}`).join("  –  ")), h("span", { class: "muted" }, `(team game ${b.game})`),
      b.order != null ? h("button", { class: "btn", onclick: () => startSpecial("Replay season game", { order: b.order }) }, "Replay this game") : null), fullBox(b));
  }
  // the teams come from the season's own standings, so a fantasy draft's teams (which are not in the built-in team list) work too
  const teams = [...new Set((SE.data?.standings || []).map((r) => r.team))].sort((a, b) => shortTeam(a).localeCompare(shortTeam(b)));
  const sel = h("select", { onchange: (e) => { SE.team = e.target.value; loadSchedule(); } }, h("option", { value: "" }, "Pick a team"), teams.map((n) => h("option", { value: n, selected: n === SE.team }, shortTeam(n))));
  const g = SE.sched || [];
  const w = g.filter((x) => x.win).length;
  const list = SE.team ? simpleTable(h("tr", {}, ...["#", "", "Opponent", "Result", "Score"].map((x, i) => h("th", { class: i === 2 ? "l" : "" }, x))),
    g.map((x) => h("tr", { class: x.mine != null && x.gid != null ? "pl-row" : "", onclick: () => { if (x.mine != null && x.gid != null) openScheduleBox(x.gid); } }, h("td", {}, x.n), h("td", {}, x.home ? "vs" : "@"), h("td", { class: "l" }, h("div", { class: "pcell" }, logoEl(identOf(x.opp)), shortTeam(x.opp))), h("td", { class: x.win ? "pm-pos" : "pm-neg" }, x.mine == null ? "–" : x.win ? "W" : "L"), h("td", {}, x.mine == null ? "" : `${x.mine}-${x.theirs}`)))) : h("div", { class: "empty" }, "Choose a team to see its schedule and results.");
  return h("div", {}, h("div", { class: "filters" }, sel, SE.team ? h("span", { class: "muted" }, `${w}-${g.length - w} so far · click a game for its box score`) : null), list);
}
async function loadSchedule() {
  if (!SE.team) { renderSeasonBody(); return; }
  SE.sched = (await api.get(`/api/season/schedule?team=${encodeURIComponent(SE.team)}`)).games;
  renderSeasonBody();
}
const HV = { view: "Season highs (every stat)", stat: "PTS", team: "All Teams", box: null };
async function loadHighs() {
  const q = new URLSearchParams({ view: HV.view, stat: HV.stat, team: HV.team });
  SE.highs = await api.get(`/api/season/highs?${q}`);
  renderSeasonBody();
}
async function openGameBox(gid, focusPlayer, focusTeam) {
  const d = await api.get(`/api/season/box?gid=${encodeURIComponent(gid)}`);
  if (d.error) { toast(d.error, "err"); return; }
  HV.box = { ...d, focusPlayer, focusTeam };
  renderSeasonBody();
}
// the full box score both Highs and Schedule open: every player by points, a totals row per team
function fullBox(d, focus = {}) {
  const pct = (m, a) => (a ? (100 * m / a).toFixed(1) : "0.0");
  const ts = (pts, fga, fta) => { const dn = 2 * (fga + 0.44 * fta); return dn ? (100 * pts / dn).toFixed(1) : "0.0"; };
  const head = ["Player", "POS", "ST", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "ORB", "DRB", "PF", "+/-", "FG", "FG%", "3P", "3P%", "FT", "FT%", "TS%"];
  return h("div", { class: "fullbox" }, d.teams.map((t) => {
    const T = { pts: 0, reb: 0, ast: 0, stl: 0, blk: 0, tov: 0, oreb: 0, dreb: 0, pf: 0, fgm: 0, fga: 0, tpm: 0, tpa: 0, ftm: 0, fta: 0, min: 0 };
    const body = t.players.map((p) => {
      Object.keys(T).forEach((k) => { T[k] += p[k] || 0; });
      const hot = focus.player === p.name && focus.team === t.name;
      return h("tr", { class: hot ? "focus" : "" }, h("td", { class: "l" }, h("div", { class: "pcell" }, faceEl(p.name), h("span", { class: "pname" }, p.name))), h("td", {}, p.pos), h("td", {}, p.st ? "★" : ""), h("td", {}, p.min.toFixed(1)), h("td", { class: "pts" }, p.pts), h("td", {}, p.reb), h("td", {}, p.ast),
        h("td", {}, p.stl), h("td", {}, p.blk), h("td", {}, p.tov), h("td", {}, p.oreb), h("td", {}, p.dreb), h("td", {}, p.pf), h("td", {}, p.pm > 0 ? `+${p.pm}` : p.pm),
        h("td", {}, `${p.fgm}-${p.fga}`), h("td", {}, pct(p.fgm, p.fga)), h("td", {}, `${p.tpm}-${p.tpa}`), h("td", {}, pct(p.tpm, p.tpa)), h("td", {}, `${p.ftm}-${p.fta}`), h("td", {}, pct(p.ftm, p.fta)), h("td", {}, ts(p.pts, p.fga, p.fta)));
    });
    body.push(h("tr", { class: "totals" }, h("td", { class: "l" }, "TEAM TOTALS"), h("td", {}), h("td", {}), h("td", {}, T.min.toFixed(0)), h("td", {}, T.pts), h("td", {}, T.reb), h("td", {}, T.ast), h("td", {}, T.stl), h("td", {}, T.blk), h("td", {}, T.tov), h("td", {}, T.oreb), h("td", {}, T.dreb), h("td", {}, T.pf), h("td", {}),
      h("td", {}, `${T.fgm}-${T.fga}`), h("td", {}, pct(T.fgm, T.fga)), h("td", {}, `${T.tpm}-${T.tpa}`), h("td", {}, pct(T.tpm, T.tpa)), h("td", {}, `${T.ftm}-${T.fta}`), h("td", {}, pct(T.ftm, T.fta)), h("td", {}, ts(T.pts, T.fga, T.fta))));
    const extras = Object.entries(t.extras || {});
    return h("div", { class: "fullbox-team" }, h("div", { class: "court-team-head", style: { "--c": t.color } }, logoEl(t), t.short, h("span", { class: "tot" }, `${t.score}`)),
      h("div", { class: "table-wrap" }, h("table", { class: "stats" }, h("thead", {}, h("tr", {}, head.map((x, i) => h("th", { class: i === 0 ? "l" : "" }, x)))), h("tbody", {}, body))),
      extras.length ? h("div", { class: "muted", style: { padding: "6px 10px" } }, extras.map(([k, v]) => `${k}: ${v}`).join("  ·  ")) : null);
  }));
}
function renderHighsTab() {
  if (HV.box) {
    const b = HV.box;
    return h("div", {}, h("div", { class: "filters" }, h("button", { class: "btn", onclick: () => { HV.box = null; renderSeasonBody(); } }, "‹ Back to highs"),
      h("b", {}, b.teams.map((t) => `${t.short} ${t.score}`).join("  –  ")), h("span", { class: "muted" }, `(team game ${b.game})`),
      b.order != null ? h("button", { class: "btn", onclick: () => startSpecial("Replay season game", { order: b.order }) }, "Replay this game") : null),
      fullBox(b, { player: b.focusPlayer, team: b.focusTeam }));
  }
  const hs = SE.highs;
  if (!hs) { loadHighs(); return h("div", { class: "empty" }, "Loading highs…"); }
  if (!hs.rows.length) return h("div", { class: "empty" }, "Season highs will appear here after Season mode.");
  const set = (k) => (e) => { HV[k] = e.target.value; loadHighs(); };
  const sel = (label, value, opts) => h("label", { class: "fsel" }, h("span", { class: "muted" }, label), h("select", { onchange: set(label === "View" ? "view" : label === "Stat" ? "stat" : "team") }, opts.map((o) => h("option", { value: o.v ?? o, selected: (o.v ?? o) === value }, o.t ?? o))));
  const filters = h("div", { class: "filters" }, sel("View", HV.view, hs.views), HV.view !== hs.views[0] ? sel("Stat", HV.stat, hs.stats) : null,
    sel("Team", HV.team, [{ v: "All Teams", t: "All Teams" }, ...hs.teams.map((t) => ({ v: t, t: identOf(t).short }))]), h("span", { class: "muted" }, "click a row for the box score" + (hs.note ? ` · ${hs.note}` : (HV.view === hs.views[0] ? " · FG% needs 20+ attempts, 3P% needs 10+" : ""))));
  const cols = ["Record", "Player", "Team", "Opponent", "Gm", "Result", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "PF", "FG", "3P", "FT", "+/-"];
  const rows = hs.rows.map((r) => h("tr", { class: "pl-row", onclick: () => openGameBox(r.gid, r.player, r.team) },
    h("td", { class: "l" }, h("b", { style: { color: "var(--accent-2)" } }, r.label)), h("td", { class: "l" }, h("div", { class: "pcell" }, faceEl(r.player), h("span", { class: "pname" }, r.player))),
    h("td", { class: "l" }, h("div", { class: "tcell" }, logoEl(r), h("span", {}, r.short))), h("td", { class: "l" }, r.opp), h("td", {}, r.game), h("td", {}, r.result), h("td", {}, r.min),
    h("td", { class: "pts" }, r.pts), h("td", {}, r.reb), h("td", {}, r.ast), h("td", {}, r.stl), h("td", {}, r.blk), h("td", {}, r.tov), h("td", {}, r.pf), h("td", {}, r.fg), h("td", {}, r.tp), h("td", {}, r.ft), h("td", {}, r.pm > 0 ? `+${r.pm}` : r.pm)));
  return h("div", {}, filters, h("div", { class: "table-wrap tall" }, h("table", { class: "stats avg" }, h("thead", {}, h("tr", {}, cols.map((c, i) => h("th", { class: i < 4 ? "l" : "" }, c)))), h("tbody", {}, rows))));
}
const RC = { team: "", data: null };
async function loadRecap() {
  RC.data = await api.get(`/api/season/recap?team=${encodeURIComponent(RC.team)}`);
  RC.team = RC.data.team || RC.team;
  renderSeasonBody();
}
function renderRecapTab() {
  const d = RC.data;
  if (!d) { loadRecap(); return h("div", { class: "empty" }, "Loading recap…"); }
  if (!d.lines.length) return h("div", { class: "empty" }, "Team season recaps appear after a regular season has been simulated.");
  const sel = h("select", { onchange: (e) => { RC.team = e.target.value; loadRecap(); } }, d.teams.map((t) => h("option", { value: t.name, selected: t.name === d.team }, `${t.year} ${t.short}`)));
  return h("div", {}, h("div", { class: "filters" }, h("label", { class: "fsel" }, h("span", { class: "muted" }, "Team"), sel)),
    h("div", { class: "recap" }, d.lines.map(([tag, text]) => h("div", { class: `rc-line ${tag}` }, text || "\u00a0"))));
}

function renderShotsTab() {
  const box = h("div", { class: "sh-scope" }, h("div", { class: "filters sh-filters" }), h("div", { class: "sh-table" }, h("div", { class: "empty" }, "Loading shots…")));
  if (SH.data) queueMicrotask(renderShots2); else loadShots2().catch((e) => toast(e.message, "err"));
  return box;
}

function renderSeasonBody() {
  const view = { standings: renderStandings, races: renderRaces, players: renderPlayers, advanced: renderAdvancedTab, teams: renderTeamsTab, schedule: renderScheduleTab, highs: renderHighsTab, recap: renderRecapTab, shots: renderShotsTab }[SE.tab]();
  $("#seasonBody").replaceChildren(view);
}

// ───────────────────────── playoffs bracket ─────────────────────────
const BR = { data: null, view: "tree", selected: null, game: null };
const identOf = (name) => (S.meta?.teams.find((t) => t.name === name)) || { name, short: (name || "").replace(/^\d{4} /, ""), initials: "TM", color: "#334155" };

async function refreshBracket() {
  BR.data = await api.get("/api/bracket");
  renderBracket();
}

function brTeam(name, wins, winner) {
  const t = identOf(name);
  const seed = BR.data?.teams?.[name]?.seed;
  const cls = winner ? (winner === name ? "win" : "lose") : "";
  return h("div", { class: `br-team ${cls}`, style: { "--c": t.color } }, h("span", { class: "seed" }, seed ?? ""), logoEl(t), h("span", { class: "nm" }, t.short), wins != null ? h("span", { class: "w" }, wins) : null);
}
function seriesFor(a, b) {
  const sr = BR.data?.series || {};
  return sr[`${a}|${b}`] || sr[`${b}|${a}`] || null;
}
function brCard([a, b, winner], extra = "") {
  const sr = seriesFor(a, b);
  const wa = sr ? (sr.a === a ? sr.wins_a : sr.wins_b) : null, wb = sr ? (sr.a === a ? sr.wins_b : sr.wins_a) : null;
  const key = `${a}|${b}`;
  const note = sr ? (sr.winner ? `${identOf(sr.winner).initials} won ${Math.max(sr.wins_a, sr.wins_b)}-${Math.min(sr.wins_a, sr.wins_b)}` : (sr.wins_a || sr.wins_b ? `Game ${sr.wins_a + sr.wins_b + 1} next` : "")) : "";
  return h("div", { class: `br-card ${extra} ${BR.selected === key ? "sel" : ""}`, onclick: () => { BR.selected = key; BR.game = null; renderBracket(); } },
    brTeam(a, wa, winner), brTeam(b, wb, winner), note ? h("div", { class: "br-note" }, note) : null);
}
function renderTree() {
  const d = BR.data || {};
  const rounds = d.rounds || {};
  if (!rounds.East) return h("div", { class: "empty" }, d.play_in ? "The play-in is running. The bracket fills in after it." : "The bracket appears when the playoffs start.");
  const E = rounds.East || {}, W = rounds.West || {}, F = rounds.Finals || {};
  const finals = Object.values(F)[0] || [];
  const pairs = (list, side) => {
    const out = [];
    for (let i = 0; i < (list || []).length; i += 2) out.push(h("div", { class: "br-pair" }, (list.slice(i, i + 2)).map((s) => brCard(s))));
    return h("div", { class: "br-stack" }, out);
  };
  const solo = (list, side) => h("div", { class: "br-stack" }, h("div", { class: `br-solo ${side}` }, (list || []).map((s) => brCard(s))));
  const col = (title, body, cls = "") => h("div", { class: `br-col ${cls}` }, h("h4", {}, title), body);
  const champ = d.champion ? h("div", { class: "br-champ" }, h("div", { class: "muted" }, "CHAMPIONS"), h("div", { class: "t" }, identOf(d.champion).short),
    d.finals_mvp ? h("div", { class: "muted" }, `Finals MVP: ${typeof d.finals_mvp === "string" ? d.finals_mvp : `${d.finals_mvp.player || d.finals_mvp.name || ""}${d.finals_mvp.line ? " · " + d.finals_mvp.line : ""}`}`) : null) : null;
  const center = h("div", { class: "br-col br-finals-col" }, h("h4", {}, Object.keys(F)[0] || "NBA Finals"), h("div", { class: "br-trophy" }, "🏆"), finals.map((s) => brCard(s, "final")));
  return h("div", {}, champ, h("div", { class: "bracket-wrap" }, h("div", { class: "bracket" },
    col("East · 1st round", pairs(E["First Round"], "east")), col("East · semis", pairs(E["Semifinals"], "east")), col("East · finals", solo(E["Conference Finals"], "east")),
    center,
    col("West · finals", solo(W["Conference Finals"], "west"), "west"), col("West · semis", pairs(W["Semifinals"], "west"), "west"), col("West · 1st round", pairs(W["First Round"], "west"), "west"))));
}
function piCard(g, note, conf, label) {
  const sel = BR.pi && BR.pi[0] === conf && BR.pi[1] === label;
  return h("div", { class: `br-card ${sel ? "sel" : ""}`, onclick: () => { BR.pi = [conf, label]; renderBracket(); } }, brTeam(g.a, g.score_a, g.winner), brTeam(g.b, g.score_b, g.winner), (note || g.boxes) ? h("div", { class: "br-note" }, [note, g.boxes ? "click for box score" : ""].filter(Boolean).join(" · ")) : null);
}
function renderPlayIn() {
  const pi = BR.data?.play_in;
  if (!pi) return h("div", { class: "empty" }, "This season has no play-in.");
  const confs = Object.entries(pi).map(([conf, g]) => {
    const g78 = g["7v8"], g910 = g["9v10"], g8 = g["8seed"];
    const seedLine = (n, who) => h("div", { class: "pi-seed" }, h("span", { class: "n" }, n), who ? [logoEl(identOf(who)), h("b", {}, identOf(who).short)] : h("span", { class: "muted" }, "TBD"));
    return h("div", { class: "pi-conf" }, h("h3", {}, `${conf} play-in`),
      h("div", { class: "pi-grid" },
        h("div", { class: "br-col" }, h("h4", {}, "Round 1"), h("div", { class: "br-stack" }, h("div", { class: "br-pair" },
          g78 ? piCard(g78, g78.winner ? `${identOf(g78.winner).initials} take the 7 seed` : "Winner gets the 7 seed", conf, "7v8") : null,
          g910 ? piCard(g910, g910.winner ? `${identOf(g910.winner === g910.a ? g910.b : g910.a).initials} eliminated` : "Loser eliminated", conf, "9v10") : null))),
        h("div", { class: "br-col" }, h("h4", {}, "8 seed game"), h("div", { class: "br-stack" }, h("div", { class: "br-solo east" }, g8 ? piCard(g8, g8.winner ? `${identOf(g8.winner).initials} take the 8 seed` : "", conf, "8seed") : h("div", { class: "muted", style: { padding: "10px" } }, "Loser of 7v8 vs winner of 9v10")))),
        h("div", { class: "br-col" }, h("h4", {}, "Advance"), h("div", { class: "br-stack", style: { justifyContent: "center", gap: "10px" } },
          seedLine(7, g78?.winner), seedLine(8, g8?.winner)))));
  });
  return h("div", { class: "pi-wrap" }, confs);
}
// box score tables for one game: [{name, score, players:[...]}]
function bracketBoxTables(boxes) {
  return h("div", { class: "conf-grid" }, boxes.map((tm) => h("div", {}, h("h3", {}, `${identOf(tm.name).short} · ${tm.score}`),
    h("div", { class: "table-wrap" }, h("table", { class: "stats" },
      h("thead", {}, h("tr", {}, h("th", { class: "l" }, "Player"), ...["MIN", "PTS", "REB", "AST", "STL", "BLK", "TO", "FG", "3PT", "FT", "+/-"].map((x) => h("th", {}, x)))),
      h("tbody", {}, (tm.players || []).map((p) => h("tr", { class: p.st ? "" : "bench" }, h("td", { class: "l" }, h("div", { class: "pcell" }, faceEl(p.name), h("span", { class: "pname" }, p.name))),
        h("td", {}, (p.min ?? 0).toFixed(1)), h("td", { class: "pts" }, p.pts), h("td", {}, p.reb), h("td", {}, p.ast), h("td", {}, p.stl), h("td", {}, p.blk), h("td", {}, p.tov),
        h("td", {}, `${p.fgm}-${p.fga}`), h("td", {}, `${p.tpm}-${p.tpa}`), h("td", {}, `${p.ftm}-${p.fta}`), h("td", {}, p.pm)))))))));
}
// per-game player averages over the whole series, one table per team (the Tk "series averages")
function seriesAverages(sr) {
  const f1 = (v) => (v || 0).toFixed(1);
  const pct = (m, a) => (a ? (100 * m / a).toFixed(1) : "0.0");
  const cols = ["GP", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "FG", "FG%", "3P", "3P%", "FT", "FT%", "TS%", "+/-"];
  return h("div", { class: "conf-grid" }, Object.entries(sr.totals || {}).map(([team, players]) => {
    const rows = Object.entries(players).filter(([, s]) => s.games).sort((x, y) => (y[1].pts / y[1].games) - (x[1].pts / x[1].games));
    const body = rows.map(([name, s]) => {
      const g = s.games, ts = 2 * (s.fga + 0.44 * s.fta);
      return h("tr", {}, h("td", { class: "l" }, h("div", { class: "pcell" }, faceEl(name), h("span", { class: "pname" }, name))), h("td", {}, g), h("td", {}, f1(s.minutes / 60 / g)), h("td", { class: "pts" }, f1(s.pts / g)), h("td", {}, f1(s.reb / g)), h("td", {}, f1(s.ast / g)),
        h("td", {}, f1(s.stl / g)), h("td", {}, f1(s.blk / g)), h("td", {}, f1(s.tov / g)), h("td", {}, `${f1(s.fgm / g)}/${f1(s.fga / g)}`), h("td", {}, pct(s.fgm, s.fga)),
        h("td", {}, `${f1(s.tpm / g)}/${f1(s.tpa / g)}`), h("td", {}, pct(s.tpm, s.tpa)), h("td", {}, `${f1(s.ftm / g)}/${f1(s.fta / g)}`), h("td", {}, pct(s.ftm, s.fta)),
        h("td", {}, ts ? (100 * s.pts / ts).toFixed(1) : "0.0"), h("td", {}, (s.plus_minus / g >= 0 ? "+" : "") + f1(s.plus_minus / g)));
    });
    return h("div", {}, h("h3", {}, `${identOf(team).short} · series averages`),
      h("div", { class: "table-wrap" }, h("table", { class: "stats" }, h("thead", {}, h("tr", {}, h("th", { class: "l" }, "Player"), ...cols.map((c) => h("th", {}, c)))), h("tbody", {}, body))));
  }));
}
function renderSeriesDetail() {
  const root = $("#seriesDetail");
  if (BR.view === "playin") {
    const pi = BR.data?.play_in, g = pi && BR.pi && pi[BR.pi[0]]?.[BR.pi[1]];
    if (!g || !g.boxes) { root.replaceChildren(); return; }
    root.replaceChildren(h("div", { class: "series-detail" }, h("div", { class: "panel-head" }, h("h2", {}, `${identOf(g.a).short} vs ${identOf(g.b).short}`), h("span", { class: "muted" }, `${BR.pi[0]} play-in · ${BR.pi[1].replace("v", " vs ")}`)), bracketBoxTables(g.boxes)));
    return;
  }
  const key = BR.selected;
  if (!key || BR.view !== "tree") { root.replaceChildren(); return; }
  const [a, b] = key.split("|");
  const sr = seriesFor(a, b);
  if (!sr) { root.replaceChildren(); return; }
  const A = identOf(sr.a), B = identOf(sr.b);
  const games = h("div", { class: "series-games" },
    h("div", { class: `sg avg ${BR.avg ? "on" : ""}`, onclick: () => { BR.avg = !BR.avg; BR.game = null; renderSeriesDetail(); } }, "Series averages"),
    (sr.games || []).map(([n, sa, sb, home]) =>
      h("div", { class: `sg ${!BR.avg && BR.game === n ? "on" : ""}`, onclick: () => { BR.avg = false; BR.game = n; renderSeriesDetail(); } }, `G${n} `, h("b", {}, `${sa}-${sb}`), ` · ${identOf(home).initials}`)));
  const head = h("div", { class: "panel-head" }, h("h2", {}, `${A.short} vs ${B.short}`), h("span", { class: "muted" }, sr.winner ? `${identOf(sr.winner).short} won ${Math.max(sr.wins_a, sr.wins_b)}-${Math.min(sr.wins_a, sr.wins_b)}` : `${sr.wins_a}-${sr.wins_b}`));
  const boxes = sr.boxes?.[BR.game];
  const body = BR.avg ? seriesAverages(sr) : boxes ? bracketBoxTables(boxes) : h("div", { class: "muted" }, "Pick a game for its box score, or Series averages for the whole series.");
  root.replaceChildren(h("div", { class: "series-detail" }, head, games, body));
}
function renderBracket() {
  // rebuilding the DOM on every finished game would snap the bracket back to its left edge: keep the scroll position
  const wrap = $("#bracketBody .bracket-wrap");
  const left = wrap ? wrap.scrollLeft : 0, top = window.scrollY;
  $("#bracketBody").replaceChildren(BR.view === "tree" ? renderTree() : renderPlayIn());
  const nw = $("#bracketBody .bracket-wrap");
  if (nw && left) nw.scrollLeft = left;
  if (window.scrollY !== top) window.scrollTo(0, top);
  renderSeriesDetail();
}
let bracketTimer = null;
function scheduleBracket() { if (bracketTimer) return; bracketTimer = setTimeout(() => { bracketTimer = null; refreshBracket(); }, 700); }

// ───────────────────────── teams & players ─────────────────────────
const CD = { team: null, data: null, sel: 0, picker: null };
const ratingColor = (v) => v >= 90 ? "#22c55e" : v >= 80 ? "#84cc16" : v >= 70 ? "#f5a524" : v >= 55 ? "#fb923c" : "#f43f5e";

async function loadRoster(name) {
  CD.team = name; CD.sel = 0;
  CD.data = await api.get(`/api/roster?team=${encodeURIComponent(name)}`);
  renderRoster(); renderPlayerCard();
}
function renderRoster() {
  const d = CD.data;
  if (!d?.players) return;
  $("#rosterList").replaceChildren(...d.players.map((p, i) => h("div", { class: `roster-row ${i === CD.sel ? "on" : ""}`, onclick: () => { CD.sel = i; renderRoster(); renderPlayerCard(); } },
    h("span", { class: "pos" }, p.pos), faceEl(p.name), h("div", {}, h("div", { class: "pname" }, p.name, p.rookie ? h("span", { class: "tag rk" }, "R") : null), h("div", { class: "muted" }, `${p.archetype || ""}`)),
    h("span", { class: "ovr", style: { color: ratingColor(p.ovr || 0) } }, p.ovr ?? "–"))));
}
function renderPlayerCard() {
  const d = CD.data, p = d?.players?.[CD.sel];
  const root = $("#playerCard");
  if (!p) { root.replaceChildren(h("div", { class: "empty" }, "Pick a team, then a player.")); return; }
  const face = h("div", { class: "pcard-face", style: { "--c": d.team.color } }, (p.name.split(" ")[0]?.[0] || "") + (p.name.split(" ").slice(-1)[0]?.[0] || ""));
  withImage(face, `/media/headshot?name=${encodeURIComponent(p.name)}`);
  const ft = Math.floor(p.height / 12), inch = p.height % 12;
  root.replaceChildren(
    h("div", { class: "pcard-head" }, face,
      h("div", {}, h("div", { class: "pcard-name" }, p.name), h("div", { class: "pcard-sub" }, `${d.team.short} · ${p.pos}${p.height ? ` · ${ft}'${inch}"` : ""}${p.archetype ? ` · ${p.archetype}` : ""}`),
        h("div", { class: "badges" }, cleanBadges(p.badges).map((b) => h("span", { class: "badge" }, b)), p.rookie ? h("span", { class: "badge", style: { background: "rgba(167,139,250,.15)", color: "#c4b5fd", borderColor: "rgba(167,139,250,.35)" } }, "Rookie") : null)),
      h("div", { class: "pcard-ovr" }, h("div", { class: "n" }, p.ovr ?? "–"), h("small", {}, "Overall"))),
    h("div", { class: "rating-groups" }, p.groups.map((g) => h("div", {}, h("h3", {}, g.title), g.items.map((it) => h("div", { class: "rbar" },
      h("span", {}, it.label), h("div", { class: "track" }, h("div", { class: "fill", style: { width: `${it.value}%`, background: ratingColor(it.value) } })), h("span", { class: "val" }, it.value)))))));
}

// ───────────────────────── in-game views: player card, shot chart, quarters, compare ─────────────────────────
const GV = { qtr: "1", pc: { team: null, name: null, quarter: "all", game: "live" }, shot: [ "Team", "Team" ], comp: { a: [null, null], b: [null, null], data: null } };
S.plays = [];
let gvTimer = null;
function scheduleGameViews() {
  if (gvTimer) return;
  gvTimer = setTimeout(() => { gvTimer = null; refreshGameViews(); }, 1200);
}
function refreshGameViews() {
  const active = $(".view.active")?.id;
  if (active === "view-qtr") loadQuarters();
  else if (active === "view-pcard") loadPlayerCard();
  else if (active === "view-shots") loadShots();
}
const pct1 = (m, a) => (a ? (100 * m / a).toFixed(1) : "–");

// ---- quarters
async function loadQuarters() {
  const d = await api.get("/api/game/quarters");
  const tabs = $("#qtrTabs");
  if (!d.teams.length) { $("#qtrBody").replaceChildren(h("div", { class: "empty" }, "Quarter box scores appear once a game is going.")); return; }
  const have = [...new Set(d.teams.flatMap((t) => Object.keys(t.periods)))].map(Number).sort((x, y) => x - y);
  const label = (n) => (n <= 4 ? `Q${n}` : n === 5 ? "OT" : `OT${n - 4}`);
  tabs.replaceChildren(...have.map((n) => h("button", { class: String(n) === GV.qtr ? "on" : "", onclick: () => { GV.qtr = String(n); loadQuarters(); } }, label(n))));
  if (!have.includes(Number(GV.qtr))) GV.qtr = String(have[have.length - 1]);
  const blocks = d.teams.map((t) => {
    const per = t.periods[GV.qtr];
    if (!per) return h("div", {}, h("h3", {}, t.short), h("div", { class: "muted" }, "Not played yet."));
    const tm = per.team;
    const rows = t.roster.map((p) => ({ p, r: per.players[p.name] })).filter((x) => x.r && (x.r.minutes > 0 || x.r.pts || x.r.reb || x.r.ast || x.r.fga || x.r.tov));
    const head = ["MIN", "PTS", "REB", "AST", "STL", "BLK", "TO", "OREB", "DREB", "PF", "+/-", "FG", "3PT", "FT", "FG%", "TS%"];
    const row = ({ p, r }) => {
      const tsd = 2 * (r.fga + 0.44 * r.fta);
      return h("tr", {}, h("td", { class: "l" }, h("div", { class: "pcell" }, h("span", { class: "slot" }, p.pos), h("span", { class: "pname" }, p.name))),
        h("td", {}, (r.minutes / 60).toFixed(1)), h("td", { class: "pts" }, r.pts), h("td", {}, r.reb), h("td", {}, r.ast), h("td", {}, r.stl), h("td", {}, r.blk), h("td", {}, r.tov),
        h("td", {}, r.oreb), h("td", {}, r.dreb), h("td", {}, r.pf), h("td", {}, r.plus_minus > 0 ? `+${r.plus_minus}` : r.plus_minus),
        h("td", {}, `${r.fgm}-${r.fga}`), h("td", {}, `${r.tpm}-${r.tpa}`), h("td", {}, `${r.ftm}-${r.fta}`), h("td", {}, pct1(r.fgm, r.fga)), h("td", {}, tsd ? (100 * r.pts / tsd).toFixed(1) : "–"));
    };
    return h("div", {}, h("div", { class: "court-team-head", style: { "--c": t.color, borderRadius: "10px" } }, logoEl(t), t.short,
      h("span", { class: "tot" }, `${tm.score} pts · ${tm.reb} reb · ${tm.ast} ast · FG ${tm.fgm}-${tm.fga} · 3PT ${tm.tpm}-${tm.tpa} · paint ${tm.points_paint} · fast break ${tm.fastbreak_pts}`)),
      h("div", { class: "table-wrap" }, h("table", { class: "stats" }, h("thead", {}, h("tr", {}, h("th", { class: "l" }, "Player"), ...head.map((x) => h("th", {}, x)))), h("tbody", {}, rows.map(row)))));
  });
  $("#qtrBody").replaceChildren(h("div", { style: { display: "grid", gap: "18px" } }, blocks));
}

// ---- player card
function cardFromSnapshot(snap, teamName, playerName) {
  const team = snap?.teams?.find((t) => t.name === teamName);
  const opp = snap?.teams?.find((t) => t.name !== teamName);
  const p = team?.box?.find((row) => row.name === playerName);
  if (!team || !p) return null;
  const tsd = 2 * (p.fga + .44 * p.fta);
  return { team, opp, score: [team.score, opp?.score || 0], player: { ...p, ts: tsd ? +(100 * p.pts / tsd).toFixed(1) : null },
    archetype: "", badges: [], shots: { rim:[0,0], mid:[0,0], three:[0,0], post:[0,0] }, defended: { rim:[0,0], mid:[0,0], three:[0,0], post:[0,0] } };
}

async function loadPlayerCard() {
  const list = await api.get("/api/game/players");
  const pick = $("#pcardPick");
  if (!list.length) { $("#pcardBody").replaceChildren(h("div", { class: "empty" }, "Start a game, then pick a player.")); return; }
  if (!GV.pc.team || !list.some((t) => t.team === GV.pc.team)) GV.pc.team = list[0].team;
  const roster = list.find((t) => t.team === GV.pc.team).players;
  if (!roster.includes(GV.pc.name)) GV.pc.name = roster[0];
  // earlier games are offered only if this player actually played in one of them (his team was in it and he got on the floor)
  const playedGames = [...S.gameSnapshots.keys()].sort((a, b) => b - a).filter((n) => {
    const row = S.gameSnapshots.get(n)?.teams?.find((t) => t.name === GV.pc.team)?.box?.find((r) => r.name === GV.pc.name);
    return !!row && ((row.min || 0) > 0 || (row.fga || 0) > 0 || (row.pts || 0) > 0);
  });
  if (GV.pc.game !== "live" && !playedGames.includes(Number(GV.pc.game))) GV.pc.game = "live";
  pick.replaceChildren(
    h("select", { onchange: (e) => { GV.pc.team = e.target.value; GV.pc.name = null; loadPlayerCard(); } }, list.map((t) => h("option", { value: t.team, selected: t.team === GV.pc.team }, t.short))),
    h("select", { onchange: (e) => { GV.pc.name = e.target.value; loadPlayerCard(); } }, roster.map((n) => h("option", { value: n, selected: n === GV.pc.name }, n))),
    h("select", { onchange: (e) => { GV.pc.game = e.target.value; loadPlayerCard(); } },
      h("option", { value: "live", selected: GV.pc.game === "live" }, `Live / Game ${S.gameNo}`),
      playedGames.map((n) => h("option", { value: String(n), selected: GV.pc.game === String(n) }, `Game ${n}`))),
    h("div", { class: "seg small" }, ["all", "1", "2", "3", "4", "OT"].map((q) => h("button", { class: GV.pc.quarter === q ? "on" : "", onclick: () => { GV.pc.quarter = q; loadPlayerCard(); } }, q === "all" ? "All plays" : q === "OT" ? "OT" : `Q${q}`))));
  const d = GV.pc.game === "live"
    ? await api.get(`/api/game/card?team=${encodeURIComponent(GV.pc.team)}&name=${encodeURIComponent(GV.pc.name)}&quarter=${GV.pc.quarter}`)
    : cardFromSnapshot(S.gameSnapshots.get(Number(GV.pc.game)), GV.pc.team, GV.pc.name);
  if (!d) { $("#pcardBody").replaceChildren(h("div", { class: "empty" }, "That player was not in this game.")); return; }
  if (d.error) { $("#pcardBody").replaceChildren(h("div", { class: "empty" }, d.error)); return; }
  const p = d.player;
  const face = h("div", { class: "pcard-face", style: { "--c": d.team.color } }, p.name.split(" ").map((w) => w[0]).slice(0, 2).join(""));
  withImage(face, `/media/headshot?name=${encodeURIComponent(p.name)}`);
  const tile = (k, v) => h("div", { class: "tile" }, h("div", { class: "k" }, k), h("div", { class: "v" }, v));
  const zoneBox = (title, z) => h("div", {}, h("h3", { style: { margin: "14px 0 8px", fontSize: "12px", letterSpacing: ".14em", textTransform: "uppercase", color: "var(--accent-2)" } }, title),
    h("div", { class: "zone-row" }, [["Rim", z.rim, "rim"], ["Mid", z.mid, "mid"], ["3PT", z.three, "three"], ["Post", z.post, "post"]].map(([lbl, v, key]) => zoneCard(lbl, v, key))));
  const qmatch = (pb) => GV.pc.quarter === "all" || String(periodIndex(pb.period) + 1) === GV.pc.quarter || (GV.pc.quarter === "OT" && periodIndex(pb.period) >= 4);
  const chosenGame = GV.pc.game === "live" ? S.gameNo : Number(GV.pc.game);
  const qLabel = GV.pc.quarter === "all" ? "game" : GV.pc.quarter === "OT" ? "overtime" : `Q${GV.pc.quarter}`;
  const pastGame = GV.pc.game !== "live";
  const qNote = GV.pc.quarter !== "all" && pastGame ? h("div", { class: "muted", style: { margin: "6px 0" } }, "Quarter splits are only kept for the game being played; this earlier game shows its full-game line.") : null;
  const plays = S.goodPlays.filter((pb) => pb.game === chosenGame && pb.text.includes(p.name) && qmatch(pb)).slice(0, 40);
  $("#pcardBody").replaceChildren(
    h("div", { class: "pcard-head" }, face, h("div", {}, h("div", { class: "pcard-name" }, p.name, p.rookie ? h("span", { class: "tag rk" }, "R") : null),
      h("div", { class: "pcard-sub" }, `${d.team.short} · ${p.listed}${d.archetype ? ` · ${d.archetype}` : ""} · ${p.on ? "on the floor" : "bench"}`),
      h("div", { class: "badges" }, cleanBadges(d.badges).map((b) => h("span", { class: "badge" }, b)))),
      h("div", { class: "pcard-ovr" }, h("div", { class: "n" }, `${p.pts}`), h("small", {}, `${qLabel} · pts · ${p.reb} reb · ${p.ast} ast`))),
    qNote,
    h("div", { class: "stat-tiles" }, tile("MIN", p.min.toFixed(1)), tile("PTS", p.pts), tile("REB", p.reb), tile("AST", p.ast), tile("STL", p.stl), tile("BLK", p.blk), tile("TO", p.tov), tile("PF", p.pf),
      tile("+/-", p.pm > 0 ? `+${p.pm}` : p.pm), tile("FG", `${p.fgm}/${p.fga}`), tile("3PT", `${p.tpm}/${p.tpa}`), tile("FT", `${p.ftm}/${p.fta}`), tile("FG%", pct1(p.fgm, p.fga)), tile("TS%", p.ts ?? "–")),
    h("div", { class: "conf-grid" }, zoneBox(d.scope === "quarter" ? `Shot diet · ${qLabel}` : "Shot diet", d.shots), zoneBox(d.scope === "quarter" ? "Shots defended · full game" : "Shots defended", d.defended)),
    h("h3", { style: { margin: "18px 0 6px", fontSize: "12px", letterSpacing: ".14em", textTransform: "uppercase", color: "var(--accent-2)" } }, `Positive plays · ${p.name}`),
    h("div", { class: "pc-plays" }, plays.length ? plays.map((pb) => h("div", { class: "ev score" }, h("div", { class: "rail", style: { background: "var(--line-strong)" } }, ""), h("div", {}, h("span", { class: "sc" }, `${pb.period} ${pb.clock} · ${pb.score}`), pb.text))) : h("div", { class: "muted" }, "No plays logged yet for this selection.")));
}
function zoneClass(key, made, att) {
  if (!att) return "none";
  const pct = 100 * made / att;
  const [hi, lo] = key === "rim" ? [50, 40] : key === "mid" ? [40, 30] : key === "post" ? [48, 38] : [42, 33];
  return pct > hi ? "good" : pct >= lo ? "ok" : "bad";
}
function zoneCard(label, v, key) {
  const [m, a] = v || [0, 0];
  return h("div", { class: `zone ${zoneClass(key, m, a)}` }, h("div", { class: "z" }, label), h("div", { class: "n" }, `${m}/${a}`), h("div", { class: "p" }, a ? `${(100 * m / a).toFixed(0)}%` : "–"));
}

// ---- shot chart
async function loadShots() {
  const d = await api.get("/api/game/shots");
  if (!d.teams.length) { $("#shotBody").replaceChildren(h("div", { class: "empty" }, "The shot chart fills in as the game goes.")); return; }
  $("#shotPick").replaceChildren(...d.teams.map((t, i) => h("select", { onchange: (e) => { GV.shot[i] = e.target.value; loadShots(); } },
    h("option", { value: "Team" }, `${t.short} · whole team`), Object.keys(t.players).map((n) => h("option", { value: n, selected: n === GV.shot[i] }, n)))));
  // NBA court at 10px per foot: 94 x 50 ft, basket 5.25 ft from the baseline, 3-pt arc 23.75 ft, lane 16 x 19 ft.
  const W = 1000, H = 600, X0 = 30, Y0 = 70, CW = 940, CH = 500, CY = Y0 + CH / 2;
  const line = 'stroke="#c9d3e6" stroke-opacity=".55" stroke-width="2" fill="none"';
  const half = (t, i, flip) => {
    const own = GV.shot[i] !== "Team" && t.players[GV.shot[i]];
    const subj = own ? t.players[GV.shot[i]] : t.team;
    const name = own ? GV.shot[i] : "Whole team";
    const X = (v) => (flip ? W - v : v);
    const hoopX = X0 + 52.5, arcX = X0 + 142;
    const card = (cx, cy, label, v, key) => {
      const [m, a2] = v;
      const cls = zoneClass(key, m, a2);
      const col = { good: "#22c55e", ok: "#f5a524", bad: "#f43f5e", none: "#64748b" }[cls];
      return `<g transform="translate(${X(cx) - 50},${cy - 32})"><rect width="100" height="64" rx="12" fill="#0e1830"/><rect width="100" height="64" rx="12" fill="${col}" fill-opacity=".26" stroke="${col}" stroke-width="2"/>
        <text x="50" y="19" text-anchor="middle" fill="#e8edf6" font-size="12" font-weight="800" letter-spacing="1.4">${label}</text>
        <text x="50" y="40" text-anchor="middle" fill="#fff" font-size="19" font-weight="800">${m}/${a2}</text>
        <text x="50" y="56" text-anchor="middle" fill="#cbd5e1" font-size="12">${a2 ? Math.round(100 * m / a2) + "%" : "–"}</text></g>`;
    };
    const anchor = flip ? "end" : "start";
    return `<g>
      <path d="M ${X(X0)} ${Y0 + 30} L ${X(arcX)} ${Y0 + 30} A 237.5 237.5 0 0 ${flip ? 0 : 1} ${X(arcX)} ${Y0 + CH - 30} L ${X(X0)} ${Y0 + CH - 30}" ${line}/>
      <rect x="${flip ? W - (X0 + 190) : X0}" y="${CY - 80}" width="190" height="160" ${line}/>
      <path d="M ${X(X0 + 190)} ${CY - 60} A 60 60 0 0 ${flip ? 0 : 1} ${X(X0 + 190)} ${CY + 60}" ${line}/>
      <path d="M ${X(X0 + 190)} ${CY - 60} A 60 60 0 0 ${flip ? 1 : 0} ${X(X0 + 190)} ${CY + 60}" ${line} stroke-dasharray="6 6"/>
      <path d="M ${X(hoopX)} ${CY - 40} A 40 40 0 0 ${flip ? 0 : 1} ${X(hoopX)} ${CY + 40}" ${line}/>
      <line x1="${X(X0 + 40)}" y1="${CY - 30}" x2="${X(X0 + 40)}" y2="${CY + 30}" stroke="#e8edf6" stroke-width="3"/>
      <circle cx="${X(hoopX)}" cy="${CY}" r="7.5" stroke="#f5a524" stroke-width="3" fill="none"/>
      ${card(X0 + 150, CY, "RIM", subj.rim, "rim")}
      ${card(X0 + 175, Y0 + 125, "MID", subj.mid, "mid")}
      ${card(X0 + 335, CY, "3PT", subj.three, "three")}
      <text x="${X(X0)}" y="34" text-anchor="${anchor}" fill="${t.color}" font-size="22" font-weight="800">${t.short}</text>
      <text x="${X(X0)}" y="56" text-anchor="${anchor}" fill="#a7b2c5" font-size="13">${name}</text></g>`;
  };
  const svg = `<svg class="court-svg" viewBox="0 0 ${W} ${H}">
    <rect x="${X0}" y="${Y0}" width="${CW}" height="${CH}" rx="6" fill="#13203a" stroke="#c9d3e6" stroke-opacity=".6" stroke-width="2.5"/>
    <line x1="${W / 2}" y1="${Y0}" x2="${W / 2}" y2="${Y0 + CH}" ${line}/><circle cx="${W / 2}" cy="${CY}" r="60" ${line}/>
    ${half(d.teams[0], 0, false)}${half(d.teams[1], 1, true)}</svg>`;
  $("#shotBody").innerHTML = svg;
}

// ---- compare
const COMPARE_ROWS = [
  ["Games", (s) => s.games, null], ["Minutes / game", (s, g) => s.minutes / 60 / g, "hi"], ["Points / game", (s, g) => s.pts / g, "hi"], ["Rebounds / game", (s, g) => s.reb / g, "hi"],
  ["Assists / game", (s, g) => s.ast / g, "hi"], ["Steals / game", (s, g) => s.stl / g, "hi"], ["Blocks / game", (s, g) => s.blk / g, "hi"], ["Turnovers / game", (s, g) => s.tov / g, "lo"],
  ["FG%", (s) => 100 * s.fgm / Math.max(1, s.fga), "hi"], ["3P%", (s) => 100 * s.tpm / Math.max(1, s.tpa), "hi"], ["FT%", (s) => 100 * s.ftm / Math.max(1, s.fta), "hi"],
  ["eFG%", (s) => 100 * (s.fgm + 0.5 * s.tpm) / Math.max(1, s.fga), "hi"], ["TS%", (s) => 100 * s.pts / Math.max(1, 2 * (s.fga + 0.44 * s.fta)), "hi"],
  ["Points / 36", (s) => 36 * s.pts / Math.max(1, s.minutes / 60), "hi"], ["Rebounds / 36", (s) => 36 * s.reb / Math.max(1, s.minutes / 60), "hi"], ["Assists / 36", (s) => 36 * s.ast / Math.max(1, s.minutes / 60), "hi"],
  ["Stocks / 36", (s) => 36 * (s.stl + s.blk) / Math.max(1, s.minutes / 60), "hi"], ["AST / TOV", (s) => s.ast / Math.max(1, s.tov), "hi"], ["Plus-minus / game", (s, g) => s.plus_minus / g, "hi"],
];
async function loadCompare() {
  const d = await api.get("/api/compare");
  GV.comp.data = d;
  const teams = Object.keys(d.teams).sort();
  if (!teams.length) { $("#compBody").replaceChildren(h("div", { class: "empty" }, "Pick two players once games have been played.")); return; }
  $("#compSource").textContent = `Uses the ${d.source} totals`;
  for (const [i, side] of ["a", "b"].entries()) {
    const c = GV.comp[side];
    if (!c[0] || !d.teams[c[0]]) c[0] = teams[Math.min(i, teams.length - 1)];
    const roster = Object.keys(d.teams[c[0]].players).sort((x, y) => d.teams[c[0]].players[y].minutes - d.teams[c[0]].players[x].minutes);
    if (!c[1] || !roster.includes(c[1])) c[1] = roster[0];
  }
  renderCompare2();
}
function renderCompare2() {
  const d = GV.comp.data;
  const teams = Object.keys(d.teams).sort();
  const pick = $("#compPick");
  const selectors = ["a", "b"].map((side) => {
    const c = GV.comp[side];
    const roster = Object.keys(d.teams[c[0]].players).sort((x, y) => d.teams[c[0]].players[y].minutes - d.teams[c[0]].players[x].minutes);
    return [h("select", { onchange: (e) => { c[0] = e.target.value; c[1] = null; loadCompare(); } }, teams.map((t) => h("option", { value: t, selected: t === c[0] }, d.teams[t].short + ` (${t.slice(0, 4)})`))),
      h("select", { onchange: (e) => { c[1] = e.target.value; renderCompare2(); } }, roster.map((n) => h("option", { value: n, selected: n === c[1] }, n)))];
  });
  pick.replaceChildren(...selectors[0], h("span", { class: "muted", style: { alignSelf: "center" } }, "vs"), ...selectors[1]);
  const sa = d.teams[GV.comp.a[0]].players[GV.comp.a[1]], sb = d.teams[GV.comp.b[0]].players[GV.comp.b[1]];
  const ga = Math.max(1, sa.games), gb = Math.max(1, sb.games);
  const body = COMPARE_ROWS.map(([label, fn, dir]) => {
    const va = fn(sa, ga), vb = fn(sb, gb);
    const better = dir === "hi" ? (va > vb ? 0 : vb > va ? 1 : -1) : dir === "lo" ? (va < vb ? 0 : vb < va ? 1 : -1) : -1;
    const f = (v) => (Number.isInteger(v) ? v : v.toFixed(label === "AST / TOV" ? 2 : 1));
    return h("tr", {}, h("td", {}, label), h("td", { class: better === 0 ? "better" : "" }, f(va)), h("td", { class: better === 1 ? "better" : "" }, f(vb)));
  });
  $("#compBody").replaceChildren(h("div", { class: "table-wrap" }, h("table", { class: "stats cmp-table" },
    h("thead", {}, h("tr", {}, h("th", {}, "Stat"), h("th", {}, GV.comp.a[1]), h("th", {}, GV.comp.b[1]))), h("tbody", {}, body))));
}

// ───────────────────────── Tk-equivalent coach and mode tools ─────────────────────────
const CO = { team: 0, out: null };
async function loadCoach() {
  const d = await api.get("/api/coach");
  if (!d.active) {
    $("#coachTeams").replaceChildren(); $("#coachFloor").replaceChildren(); $("#coachBench").replaceChildren();
    $("#coachStatus").textContent = "Start a live game to use substitutions and adjustments."; return;
  }
  if (!d.teams[CO.team]) CO.team = 0;
  $("#coachTeams").replaceChildren(...d.teams.map((t, i) => h("button", { class: i === CO.team ? "on" : "", onclick: () => { CO.team = i; CO.out = null; renderCoach(d); } }, t.team.short)));
  renderCoach(d);
}
async function coachDo(body) {
  try { await api.post("/api/coach", { team: CO.team, ...body }); await loadCoach(); }
  catch (err) { toast(err.message, "err"); }
}
function renderCoach(d) {
  const t = d.teams[CO.team]; if (!t) return;
  const opp = d.teams[1 - CO.team];
  const queued = new Map(t.queued.map((x) => [x.out, x.in]));
  $("#coachStatus").textContent = `${t.timeouts} timeouts${t.timeoutOpen ? " · timeout open" : ""} · ${t.offense.replaceAll("_", " ")} offense · ${t.defense.replaceAll("_", " ")} defense${t.focus ? ` · help toward ${t.focus}` : ""}`;
  // schemes, picked directly (they used to only cycle)
  const sel = (label, options, value, onchange) => h("label", { class: "fsel" }, h("span", { class: "muted" }, label), h("select", { onchange: (e) => onchange(e.target.value) }, options.map((o) => h("option", { value: o.value, selected: o.value === value }, o.label))));
  const focusOpts = [{ value: "", label: "No extra help" }, ...(opp?.floor || []).concat(opp?.bench || []).map((p) => ({ value: p.name, label: p.name }))];
  $("#coachPlan").replaceChildren(
    sel("Offense", d.offenseOptions, t.offenseSet, (v) => coachDo({ action: "setoffense", value: v })),
    sel("Defense", d.defenseOptions, t.defenseSet, (v) => coachDo({ action: "setdefense", value: v })),
    sel("Help toward", focusOpts, t.focus || "", (v) => coachDo({ action: "setfocus", value: v })));
  // players: click-to-sub or drag a bench player onto a floor player (or the other way round)
  const subNow = (out, inn) => coachDo({ action: "sub", out, in: inn });
  const card = (p, floor) => {
    const c = h("button", { class: `coach-card ${floor && CO.out === p.name ? "on" : ""} ${p.out ? "fouled" : ""}`, draggable: "true",
      onclick: async () => {
        if (floor) { CO.out = CO.out === p.name ? null : p.name; renderCoach(d); return; }
        if (!CO.out) { toast("Select the player going out first."); return; }
        const out = CO.out; CO.out = null; subNow(out, p.name);
      },
      ondragstart: (e) => { e.dataTransfer.setData("text/plain", JSON.stringify({ name: p.name, floor })); e.dataTransfer.effectAllowed = "move"; },
      ondragover: (e) => { e.preventDefault(); c.classList.add("drop"); }, ondragleave: () => c.classList.remove("drop"),
      ondrop: (e) => { e.preventDefault(); c.classList.remove("drop"); try { const src = JSON.parse(e.dataTransfer.getData("text/plain")); if (src.floor === floor || src.name === p.name) return; floor ? subNow(p.name, src.name) : subNow(src.name, p.name); } catch (_) {} } },
      faceEl(p.name), h("span", { class: "nm" }, p.name),
      h("span", { class: "line" }, `${p.pos} · ${p.min} min · ${p.pts} pts · ${p.pf} PF${p.stint ? ` · stint ${p.stint}` : ""}${queued.get(p.name) ? ` · OUT → ${queued.get(p.name)}` : ""}`),
      p.energy != null ? h("span", { class: "energy", title: `Energy ${p.energy}%` }, h("i", { style: { width: `${Math.max(4, Math.min(100, (p.energy - 85) / 15 * 100))}%`, background: p.energy >= 98 ? "var(--green)" : p.energy >= 93 ? "var(--accent)" : "var(--red)" } })) : null);
    return c;
  };
  $("#coachFloor").replaceChildren(...t.floor.map((p) => card(p, true)));
  $("#coachBench").replaceChildren(...t.bench.map((p) => card(p, false)));
  // matchups: who guards whom and the coverage
  const defenders = [{ value: "", label: "Coach auto" }, ...t.floor.concat(t.bench).map((p) => ({ value: p.name, label: p.name }))];
  const rows = (t.matchups || []).map((m) => h("tr", { class: m.onFloor ? "" : "bench" },
    h("td", { class: "l" }, h("div", { class: "pcell" }, faceEl(m.target), h("span", { class: "pname" }, m.target), h("span", { class: "muted" }, `${m.pos}${m.onFloor ? "" : " · bench"}`))),
    h("td", {}, h("select", { onchange: (e) => coachDo({ action: "matchup", target: m.target, defender: e.target.value }) }, defenders.map((o) => h("option", { value: o.value, selected: o.value === m.defender }, o.value === "" && m.auto ? `Coach auto (${m.auto})` : o.label)))),
    h("td", {}, h("select", { onchange: (e) => coachDo({ action: "matchup", target: m.target, coverage: e.target.value }) }, d.coverageOptions.map((o) => h("option", { value: o.value, selected: o.value === m.coverage }, o.label))))));
  $("#coachLines").replaceChildren((t.lineups || []).length ? h("table", { class: "stats" }, h("thead", {}, h("tr", {}, h("th", {}, "+/-"), h("th", {}, "MIN"), h("th", {}, "PF"), h("th", {}, "PA"), h("th", { class: "l" }, "Lineup"))),
    h("tbody", {}, t.lineups.map((l) => h("tr", {}, h("td", { class: l.pm > 0 ? "pm-pos" : l.pm < 0 ? "pm-neg" : "" }, l.pm > 0 ? `+${l.pm}` : l.pm), h("td", {}, l.min), h("td", {}, l.pf), h("td", {}, l.pa), h("td", { class: "l" }, l.players.join(" / ")))))) : h("div", { class: "empty" }, "Lineup plus-minus appears once the game gets going."));
  $("#coachMatch").replaceChildren(rows.length ? h("table", { class: "stats" }, h("thead", {}, h("tr", {}, h("th", { class: "l" }, "Opposing player"), h("th", {}, "Primary defender"), h("th", {}, "Coverage"))), h("tbody", {}, rows)) : h("div", { class: "empty" }, "Matchups appear once the game starts."));
}

async function loadLineup() {
  const d = await api.get("/api/fantasy"), root = $("#lineupBody");
  if (!d.active) { root.replaceChildren(h("div", { class: "empty" }, d.message)); return; }
  const rows = d.userRoster.map((p, i) => h("tr", { "data-name": p.name },
    h("td", { class: "l" }, h("div", { class: "pcell" }, faceEl(p.name), h("span", { class: "pname" }, p.name))),
    h("td", {}, p.ovr), h("td", {}, h("input", { type: "checkbox", class: "lu-start", checked: p.starter })),
    h("td", {}, h("select", { class: "lu-pos" }, ["PG","SG","SF","PF","C"].map((x) => h("option", { value:x, selected:x===p.pos }, x)))),
    h("td", {}, h("input", { class: "lineup-input lu-min", type:"number", min:"0", max:"48", value:p.minutes ?? 0 })),
    h("td", {}, h("input", { class: "lineup-input lu-use", type:"number", min:"0.05", max:"0.5", step:"0.01", value:(p.usage ?? .2).toFixed(2) })),
    h("td", {}, i + 1)));
  root.replaceChildren(h("table", { class:"stats lineup-table" }, h("thead", {}, h("tr", {}, ["Player","OVR","Start","Pos","Minutes","Usage","Rotation"].map((x,i) => h("th", { class:i===0?"l":"" }, x)))), h("tbody", {}, rows)));
}
async function saveLineup(reset=false) {
  if (reset) { await api.post("/api/fantasy/lineup", { reset:true }); await loadLineup(); return; }
  const rows = $$("#lineupBody tbody tr"), starters=[], positions={}, minutes={}, usage={}, rotation=[];
  rows.forEach((tr) => { const n=tr.dataset.name; rotation.push(n); if ($(".lu-start",tr).checked) starters.push(n); positions[n]=$(".lu-pos",tr).value; minutes[n]=Number($(".lu-min",tr).value); usage[n]=Number($(".lu-use",tr).value); });
  if (starters.length !== 5) throw new Error("Choose exactly five starters.");
  await api.post("/api/fantasy/lineup", { starters, positions, minutes, usage, rotation }); toast("Lineup saved.", "ok"); await loadLineup();
}

// ratings shown beside every player in the draft and trade screens (the Tk draft board's columns)
const RATE_COLS = [["3PT", "3PT"], ["MID", "MID"], ["RIM", "RIM"], ["PLAY", "PLAY"], ["PERIM D", "PD"], ["INT D", "ID"]];
const RATE_GROUPS = [["Scoring", ["3PT", "MID", "RIM", "DUNK", "FT"]], ["Playmaking", ["PLAY", "HANDLE", "USAGE"]], ["Defense", ["PERIM D", "INT D", "STL", "BLK"]], ["Rebounding", ["OREB", "DREB"]]];
const fmtHt = (n) => (n ? `${Math.floor(n / 12)}'${n % 12}"` : "");
function ratingDetail(p) {
  return h("div", { class: "pl-detail" },
    h("div", { class: "pl-meta" }, [fmtHt(p.ht), p.arch, p.team].filter(Boolean).join(" · "), (p.badges || []).length ? h("div", { class: "badges" }, p.badges.map((b) => h("span", { class: "badge" }, b.replace(/_/g, " ")))) : null),
    h("div", { class: "rating-groups" }, RATE_GROUPS.map(([title, keys]) => h("div", {}, h("h3", {}, title), keys.map((k) => h("div", { class: "rbar" },
      h("span", {}, k), h("div", { class: "track" }, h("div", { class: "fill", style: { width: `${p.r[k]}%`, background: ratingColor(p.r[k]) } })), h("span", { class: "val" }, p.r[k])))))));
}
// one table of players: sortable columns, click a row for the full rating card. `action` adds a button/checkbox column.
function playerTable(players, { id, action, sortKey = "ovr", extra = [] } = {}) {
  const st = (playerTable.state[id] ||= { sort: sortKey, dir: -1, open: null, q: "" });
  const val = (p, k) => (k === "ovr" ? p.ovr : k === "name" ? p.name : k === "pos" ? p.pos : k === "minutes" ? (p.minutes ?? -1) : (p.r?.[k] ?? 0));
  let rows = players.filter((p) => !st.q || p.name.toLowerCase().includes(st.q));
  rows = rows.sort((x, y) => (typeof val(x, st.sort) === "string" ? st.dir * -val(x, st.sort).localeCompare(val(y, st.sort)) : st.dir * (val(x, st.sort) - val(y, st.sort))));
  const redraw = () => { const t = $("#" + id); if (t) t.replaceWith(playerTable(players, { id, action, sortKey, extra })); };
  const th = (label, key, cls = "") => h("th", { class: `sortable ${cls} ${st.sort === key ? "sorted" : ""}`, onclick: () => { st.dir = st.sort === key ? -st.dir : (key === "name" || key === "pos" ? 1 : -1); st.sort = key; redraw(); } }, label, st.sort === key ? (st.dir < 0 ? " ▾" : " ▴") : "");
  const body = [];
  for (const p of rows) {
    const open = st.open === p.name;
    body.push(h("tr", { class: `pl-row ${open ? "open" : ""}`, onclick: (e) => { if (e.target.closest("button,input,label")) return; st.open = open ? null : p.name; redraw(); } },
      h("td", {}, h("span", { class: "pos" }, p.pos)), h("td", { class: "l" }, h("div", { class: "pcell" }, faceEl(p.name), h("div", {}, h("div", { class: "pname" }, p.name), h("div", { class: "muted" }, p.team || "")))),
      h("td", {}, h("b", { style: { color: ratingColor(p.ovr || 0) } }, p.ovr)), ...RATE_COLS.map(([k]) => h("td", { style: { color: ratingColor(p.r[k]) } }, p.r[k])),
      ...extra.map(([, f]) => h("td", {}, f(p))), action ? h("td", {}, action(p)) : null));
    if (open) body.push(h("tr", { class: "pl-expand" }, h("td", { colspan: 9 + extra.length }, ratingDetail(p))));
  }
  return h("div", { id, class: "pl-table-wrap" },
    h("div", { class: "filters" }, h("input", { placeholder: "Search player…", value: st.q, oninput: (e) => { st.q = e.target.value.toLowerCase(); const pos = e.target.selectionStart; redraw(); const i = $(`#${id} input`); i.focus(); i.setSelectionRange(pos, pos); } }),
      h("span", { class: "muted" }, `${rows.length} players · click a column to sort, click a player for the full ratings`)),
    h("div", { class: "table-wrap" }, h("table", { class: "stats pl-table" }, h("thead", {}, h("tr", {}, th("POS", "pos"), th("Player", "name", "l"), th("OVR", "ovr"), ...RATE_COLS.map(([k, l]) => th(l, k)), ...extra.map(([l, , k]) => th(l, k || "ovr")), action ? h("th", {}, "") : null)), h("tbody", {}, body))));
}
playerTable.state = {};

function lineupPanel(roster, title = "Your lineup") {
  const starters = roster.filter((p) => p.starter), bench = roster.filter((p) => !p.starter);
  const row = (p) => h("div", { class: "lu-row" }, h("span", { class: "pos" }, p.pos), faceEl(p.name), h("div", { class: "lu-name" }, h("b", {}, p.name), h("span", { class: "muted" }, p.minutes != null ? `${p.minutes} min` : (p.arch || ""))), h("b", { style: { color: ratingColor(p.ovr || 0) } }, p.ovr));
  return h("div", { class: "lineup-panel" }, h("h3", {}, title), starters.length ? [h("div", { class: "muted lu-h" }, "Starters"), ...starters.map(row)] : null,
    bench.length ? [h("div", { class: "muted lu-h" }, starters.length ? "Bench" : `Roster (${bench.length})`), ...bench.map(row)] : null,
    !roster.length ? h("div", { class: "empty" }, "No players yet.") : null);
}

async function loadDraft() {
  const d = await api.get("/api/draft"), root = $("#draftBoard");
  const mine = d.roster || [];
  const picks = d.state?.log ? d.state.log.slice(-10).reverse() : [];
  const side = h("div", { class: "draft-side" }, lineupPanel(mine, `Your roster (${mine.length})`),
    picks.length ? h("div", { class: "lineup-panel" }, h("h3", {}, "Recent picks"), picks.map((x) => h("div", { class: `lu-row ${x.user ? "mine" : ""}` }, h("span", { class: "pos" }, `#${x.overall}`), h("div", { class: "lu-name" }, h("b", {}, x.player), h("span", { class: "muted" }, `${x.team.replace(/^\d{4} /, "")} · ${x.pos}`)), h("b", {}, x.ovr)))) : null);
  if (!d.active) { root.replaceChildren(h("div", { class: "draft-layout" }, h("div", {}, h("div", { class: "empty" }, d.state?.on_clock ? `${d.state.on_clock} are picking…` : "Start a draft to open the board.")), mine.length ? side : null)); return; }
  const p = d.prompt;
  if (p.kind === "option") { root.replaceChildren(h("div", { class: "draft-layout" }, h("div", {}, h("h3", {}, p.title), p.message ? h("p", { class: "muted" }, p.message) : null, h("div", { class: "action-row" }, p.options.map((x) => h("button", { class: "btn", onclick: () => chooseDraft(x) }, x)))), side)); return; }
  const st = d.state || {};
  root.replaceChildren(h("div", { class: "draft-layout" }, h("div", {},
    h("div", { class: "panel-head" }, h("h3", {}, `${p.title}${st.round ? ` · round ${st.round} of ${st.rounds}, pick ${st.pick_in_round}` : ""}`), h("button", { class: "btn", onclick: () => chooseDraft("__auto__") }, "Auto-draft the rest")),
    playerTable(p.players, { id: "draftPool", action: (pl) => h("button", { class: "btn", onclick: () => chooseDraft(pl.key) }, "Draft") })), side));
}
async function chooseDraft(value) { try { await api.post("/api/draft", { value }); setTimeout(loadDraft, 250); } catch (e) { toast(e.message, "err"); } }

async function loadTrades() {
  const d = await api.get("/api/fantasy"), root = $("#tradeBody");
  if (!d.active) { root.replaceChildren(h("div", { class: "empty" }, d.message)); return; }
  window.__tradeTeams = d.teams.filter((x) => x !== d.userTeam);
  const sel = h("select", { id: "tradeTeam", onchange: loadTradeOpponent }, window.__tradeTeams.map((x) => h("option", { value: x }, x)));
  const give = new Set();
  const tick = (set) => (p) => h("label", { class: "trade-pick" }, h("input", { type: "checkbox", value: p.name, checked: set.has(p.name), onchange: (e) => (e.target.checked ? set.add(p.name) : set.delete(p.name)) }), "Trade");
  window.__tradeGive = give; window.__tradeGet = new Set();
  root.replaceChildren(h("p", {}, h("b", {}, d.userTeam), ` · deadline ${d.deadlinePassed ? "passed" : `game ${d.deadline}`}`),
    h("div", { class: "trade-layout" }, h("div", {}, h("h3", {}, "Your players"), playerTable(d.userRoster, { id: "tradeMineTbl", extra: [["MIN", (p) => (p.minutes ?? ""), "minutes"]], action: tick(give) })),
      h("div", {}, h("div", { class: "filters" }, h("h3", { style: { margin: 0 } }, "Trade with"), sel), h("div", { id: "tradeTheirs" }))),
    h("div", { class: "action-row" }, h("button", { class: "btn primary", onclick: findTrades }, "Find offers")), h("div", { id: "tradeOffers" }),
    h("div", { class: "trade-layout" }, lineupPanel(d.userRoster, "Your current lineup")));
  const pre = window.__tradePreset; window.__tradePreset = null;
  if (pre) {
    sel.value = pre.team; (pre.give || []).forEach((n) => give.add(n)); window.__tradeGet = new Set(pre.get || []);
    root.prepend(h("div", { class: "lineup-panel" }, h("h3", {}, "Negotiating"), h("div", {}, `${pre.team} offered ${(pre.get || []).join(", ")} for ${(pre.give || []).join(", ")}. Change it, press Find offers, then Resume the season (Pause button) when you are done.`)));
    $("#tradeMineTbl")?.replaceWith(playerTable(d.userRoster, { id: "tradeMineTbl", extra: [["MIN", (p) => (p.minutes ?? ""), "minutes"]], action: tick(give) }));
  }
  await loadTradeOpponent();
}
async function loadTradeOpponent() {
  const el = $("#tradeTeam"); if (!el) return;
  const d = await api.get(`/api/fantasy/roster?team=${encodeURIComponent(el.value)}`);
  $("#tradeTheirs").replaceChildren(playerTable(d.players, { id: "tradeTheirsTbl" }));
}
async function findTrades() {
  const userGives = [...(window.__tradeGive || [])];
  if (!userGives.length) { toast("Choose at least one of your players."); return; }
  const d = await api.post("/api/fantasy/trade", { action: "find", userGives });
  $("#tradeOffers").replaceChildren(...(d.offers.length ? d.offers.map((o) => h("div", { class: "replay-row" }, h("b", {}, o.ai_team), h("span", {}, `${o.user_gives.join(", ")} ⇄ ${o.ai_gives.join(", ")}`),
    h("button", { class: "btn", onclick: async () => { await api.post("/api/fantasy/trade", { action: "submit", team: o.ai_team, userGives: o.user_gives, aiGives: o.ai_gives }); loadTrades(); } }, "Accept"))) : [h("div", { class: "empty" }, "No acceptable offers found.")]));
}

const customSelected=new Set();
function renderCustomTeams(){ const root=$("#customTeams"); root.replaceChildren(...S.meta.teams.map((t)=>h("label",{class:"team-check"},h("input",{type:"checkbox",checked:customSelected.has(t.name),onchange:(e)=>{e.target.checked?customSelected.add(t.name):customSelected.delete(t.name);$("#customCount").textContent=`${customSelected.size} teams selected`;}}),logoEl(t),h("span",{},t.name)))); $("#customCount").textContent=`${customSelected.size} teams selected`; }
async function startSpecial(mode,options={}){ try{await api.post("/api/start",{mode,teamA:S.teamA,teamB:S.teamB,rules:S.rules,options});}catch(e){toast(e.message,"err");} }

async function fillOnePlayers(side){ const team=$("#oneTeam"+side).value,d=await api.get(`/api/roster?team=${encodeURIComponent(team)}`),sel=$("#onePlayer"+side); sel.replaceChildren(...d.players.map((p)=>h("option",{value:p.name},`${p.name} · ${p.pos} · ${p.ovr}`))); }
async function loadReplays(){ const d=await api.get("/api/replays"),root=$("#replayBody"); root.replaceChildren(...(d.games.length?d.games.map((g)=>h("div",{class:"replay-row"},h("b",{},`Game ${g.game}`),h("span",{},`${g.teamA} vs ${g.teamB}`),h("button",{class:"btn",disabled:!g.available,onclick:()=>startSpecial("Replay season game",{order:g.order})},"Replay"))):[h("div",{class:"empty"},"Complete a season to create replays.")])); }
function broadcastText(e){ const names=Object.entries(e).filter(([k])=>k!=="kind").map(([k,v])=>`${k.replaceAll("_"," ")}: ${v}`).join(" · "); return names||"Live game event"; }
async function loadBroadcast(){ const d=await api.get("/api/broadcast"),root=$("#broadcastBody"),follow=root.scrollHeight-root.scrollTop-root.clientHeight<60; root.replaceChildren(...(d.events.length?d.events.map((e)=>h("div",{class:"broadcast-event"},h("span",{class:"kind"},e.kind),h("span",{},broadcastText(e)))):[h("div",{class:"empty"},"Broadcast events appear once a game starts.")])); if(follow)root.scrollTop=root.scrollHeight; }

// Tables retain their scroll position and update only when the data changes.
let statsData = null, statsTimer = null, statsSignature = "", statsRequest = 0;
let statsSort = {column: -1, direction: 1};
function scheduleStats() {
  if (!$("#view-stats").classList.contains("active") || statsTimer) return;
  statsTimer = setTimeout(() => {statsTimer = null; loadStats().catch(e => toast(e.message,"err"));}, 700);
}
async function loadStats() {
  const request = ++statsRequest;
  const query = new URLSearchParams({kind:$("#statsKind").value,source:$("#statsSource").value,team:$("#statsTeam").value,quarter:$("#statsQuarter").value});
  const data = await api.get(`/api/stats?${query}`);
  if(request !== statsRequest) return;
  for (const [id, options, selected] of [["statsSource",data.sources.length ? data.sources : ["Live"],data.source],["statsTeam",["All teams",...data.teams],$("#statsTeam").value]]) {
    const select = $("#"+id);
    if(JSON.stringify([...select.options].map(o=>o.value)) !== JSON.stringify(options)) select.replaceChildren(...options.map(v=>h("option",{value:v},v)));
    select.value = options.includes(selected) ? selected : options[0];
  }
  $("#statsQuarterLabel").hidden = $("#statsKind").value !== "shots";
  const signature = JSON.stringify(data);
  statsData=data;
  if(signature !== statsSignature) {statsSignature=signature; renderStats();}
}
// ---- Tk-style stats table: team groups, rank by, "rank all players", minimum games. Used by the Stats tab and Season > Advanced.
const STX = {};   // per-table state, keyed by the root element id
const numOf = (v) => {
  if (typeof v === "number") return v;
  if (v == null || v === "—" || v === "") return -1e9;
  const s = String(v);
  const m = s.includes("·") ? s.match(/\/(\d+)/) : s.match(/-?\d+(\.\d+)?/);
  return m ? parseFloat(m[1] !== undefined && s.includes("·") ? m[1] : m[0]) : -1e9;
};
function renderStatsInto(root, data, opts = {}) {
  const st = (STX[root.id] ||= { rank: "Team order", flat: false, minGp: 0, search: "", sort: { column: -1, direction: -1 } });
  if (data.reports) { root.replaceChildren(...Object.entries(data.reports).map(([title, text]) => h("details", {}, h("summary", {}, title.replaceAll("_", " ")), h("pre", {}, text)))); return; }
  const cols = data.columns || [];
  const colSig = cols.join("|");
  if (st.colSig !== colSig) { st.colSig = colSig; st.rank = "Team order"; st.flat = false; st.sort = { column: -1, direction: -1 }; }   // a different table: start from team order
  const hasPlayer = cols[1] === "Player";
  if (!hasPlayer) {   // awards etc.: plain table
    root.replaceChildren(data.rows.length ? h("table", { class: "stats" }, h("thead", {}, h("tr", {}, cols.map((c) => h("th", {}, c)))), h("tbody", {}, data.rows.map((r) => h("tr", {}, r.map((v) => h("td", {}, v ?? "—")))))) : h("div", { class: "empty" }, "Nothing here yet."));
    return;
  }
  const rerender = () => renderStatsInto(root, data, opts);
  const rankCols = cols.slice(2).filter((c) => !["Opponent"].includes(c));
  const maxGp = Math.max(1, ...(data.gp || [1]));
  const controls = h("div", { class: "filters stx-controls" },
    h("label", {}, "Rank by ", h("select", { onchange: (e) => { st.rank = e.target.value; st.sort = { column: -1, direction: -1 }; rerender(); } }, ["Team order", ...rankCols].map((c) => h("option", { value: c, selected: c === st.rank }, c)))),
    h("label", {}, "Min games ", h("input", { type: "number", min: 0, max: maxGp, value: st.minGp, style: { width: "70px" }, onchange: (e) => { st.minGp = Math.max(0, Number(e.target.value) || 0); rerender(); } })),
    h("label", { class: "chk" }, h("input", { type: "checkbox", checked: st.flat, onchange: (e) => { st.flat = e.target.checked; rerender(); } }), " Rank all players (no team headers)"),
    h("label", {}, "Find player ", h("input", { type: "search", placeholder: "Player name", value: st.search, oninput: (e) => { st.search = e.target.value.toLowerCase(); const pos = e.target.selectionStart; rerender(); const i = $(`#${root.id} .stx-controls input[type=search]`); i.focus(); i.setSelectionRange(pos, pos); } })),
    h("span", { class: "muted" }, `${maxGp > 1 ? `${maxGp} games played · ` : ""}click a column to sort`));
  let items = data.rows.map((r, i) => ({ r, gp: data.gp?.[i] ?? maxGp }))
    .filter((x) => x.gp >= st.minGp && (!st.search || String(x.r[1]).toLowerCase().includes(st.search)));
  const colIdx = st.sort.column >= 0 ? st.sort.column : (st.rank !== "Team order" ? cols.indexOf(st.rank) : -1);
  const dirn = st.sort.column >= 0 ? st.sort.direction : -1;
  const byCol = (a, b) => dirn * (numOf(a.r[colIdx]) - numOf(b.r[colIdx]));
  const defaultCol = Math.max(2, cols.findIndex((c) => ["MPG", "MIN"].includes(c)) >= 0 ? cols.findIndex((c) => ["MPG", "MIN"].includes(c)) : (cols.indexOf("TOTAL") >= 0 ? cols.indexOf("TOTAL") : 2));
  const flat = st.flat || st.rank !== "Team order" || st.sort.column >= 0;
  const head = h("tr", {}, cols.map((label, i) => h("th", { class: `sortable ${st.sort.column === i ? "sorted" : ""} ${i < 2 ? "l" : ""}`, onclick: () => { if (i === 0) { st.sort = { column: -1, direction: -1 }; st.rank = "Team order"; st.flat = false; } else st.sort = { column: i, direction: st.sort.column === i ? -st.sort.direction : (i === 1 ? 1 : -1) }; rerender(); } }, label, st.sort.column === i ? (st.sort.direction < 0 ? " ▾" : " ▴") : "")));
  const rowEl = (x, rank) => h("tr", {}, x.r.map((v, i) => h("td", { class: i < 2 ? "l" : "" }, i === 1 && rank ? `${rank}. ${v}` : (v ?? "—"))));
  const body = [];
  if (flat) {
    let list = [...items];
    if (colIdx >= 0) list.sort(byCol);
    list.forEach((x, i) => body.push(rowEl(x, st.rank !== "Team order" || st.sort.column >= 0 ? i + 1 : null)));
  } else {
    const by = new Map();
    items.forEach((x) => { (by.get(x.r[0]) || by.set(x.r[0], []).get(x.r[0])).push(x); });
    for (const [team, list] of by) {
      const id = identOf(team);
      body.push(h("tr", { class: "team-row" }, h("td", { colspan: cols.length }, h("div", { class: "tcell" }, logoEl(id), h("span", { class: "yr" }, id.year || ""), h("span", { class: "pname" }, id.short || team), h("span", { class: "muted" }, `${list.length} players`)))));
      list.sort((a, b) => numOf(b.r[defaultCol]) - numOf(a.r[defaultCol])).forEach((x) => body.push(rowEl(x, null)));
    }
  }
  const prev = root.querySelector(".stx-wrap");
  const left = prev ? prev.scrollLeft : 0, top = prev ? prev.scrollTop : 0;
  const wrap = h("div", { class: "table-wrap tall stx-wrap" }, body.length ? h("table", { class: "stats avg" }, h("thead", {}, head), h("tbody", {}, body)) : h("div", { class: "empty" }, "No stats for this selection yet. Start a game or choose another source."));
  root.replaceChildren(controls, wrap);
  wrap.scrollLeft = left; wrap.scrollTop = top;
}
function renderStats() {
  if (!statsData) return;
  renderStatsInto($("#statsBody"), statsData);
}

// ---- Shots tab (Tk): shot diet / defense diet / matchup defense
const SH = { mode: "Shot Diet", game: "All Games", quarter: "All Quarters", team: "All Teams", defender: "All Defenders", guarded: "All Guarded", rank: "Team order", rankStat: "Made", minAtt: "", minDef: "", source: "Season", data: null };
async function loadShots2() {
  const q = new URLSearchParams({ mode: SH.mode, game: SH.game, quarter: SH.quarter, team: SH.team, defender: SH.defender, guarded: SH.guarded, rank: SH.rank, rankStat: SH.rankStat, minAtt: SH.minAtt, minDef: SH.minDef, source: SH.source });
  SH.data = await api.get(`/api/shots?${q}`);
  if (SH.data.source) SH.source = SH.data.source;
  renderShots2();
}
function renderShots2() {
  const d = SH.data; if (!d) return;
  for (const scope of $$(".sh-scope")) paintShots(scope, d);
}
function paintShots(scope, d) {
  const filtersEl = scope.querySelector(".sh-filters"), tableEl = scope.querySelector(".sh-table");
  const sel = (label, key, opts, show = true) => !show ? null : h("label", { class: "fsel" }, h("span", { class: "muted" }, label),
    h("select", { onchange: (e) => { SH[key] = e.target.value; loadShots2(); } }, opts.map((o) => h("option", { value: o.v ?? o, selected: (o.v ?? o) === SH[key] }, o.t ?? o))));
  const rankable = SH.mode !== "Matchup Defense";
  filtersEl.replaceChildren(
    sel("Type", "mode", d.modes), sel("Game", "game", d.games), SH.mode === "Shot Diet" ? sel("Quarter", "quarter", ["All Quarters", "Q1", "Q2", "Q3", "Q4", "OT"]) : null,
    sel("Team", "team", [{ v: "All Teams", t: "All Teams" }, ...d.teams.map((t) => ({ v: t, t }))]),
    SH.mode === "Matchup Defense" ? sel("Defender", "defender", [{ v: "All Defenders", t: "All Defenders" }, ...d.defenders.map((t) => ({ v: t, t }))]) : null,
    SH.mode === "Matchup Defense" ? sel("Guarded", "guarded", [{ v: "All Guarded", t: "All Guarded" }, ...d.guarded.map((t) => ({ v: t, t }))]) : null,
    rankable ? sel("Rank by", "rank", ["Team order", ...d.rankKeys]) : null, rankable ? sel("", "rankStat", ["Made", "Attempted", "Percentage"]) : null,
    rankable ? h("label", { class: "fsel" }, h("span", { class: "muted" }, SH.mode === "Defense Diet" ? "Min defended (blank = auto)" : "Min att (blank = NBA min)"),
      h("input", { value: SH[SH.mode === "Defense Diet" ? "minDef" : "minAtt"], style: { width: "70px" }, onchange: (e) => { SH[SH.mode === "Defense Diet" ? "minDef" : "minAtt"] = e.target.value; loadShots2(); } })) : null,
    sel("Show", "source", d.sources));
  if (!d.rows.length) { tableEl.replaceChildren(h("div", { class: "empty" }, d.note || "Shot data appears once games are played.")); return; }
  const prev = tableEl.querySelector(".table-wrap"), left = prev?.scrollLeft || 0, top = prev?.scrollTop || 0;
  const wrap = h("div", { class: "table-wrap tall" }, h("table", { class: "stats avg" }, h("thead", {}, h("tr", {}, d.columns.map((c, i) => h("th", { class: i < (SH.mode === "Matchup Defense" ? 3 : 2) ? "l" : "" }, c)))),
    h("tbody", {}, d.rows.map((r) => h("tr", { class: r.kind === "team" ? "team-row" : "" }, r.cells.map((c, i) => h("td", { class: i < (SH.mode === "Matchup Defense" ? 3 : 2) ? "l" : "" }, i === 0 ? (identOf(c).short ? `${identOf(c).year || ""} ${identOf(c).short}`.trim() : c) : c)))))));
  tableEl.replaceChildren(wrap); wrap.scrollLeft = left; wrap.scrollTop = top;
}

// ───────────────────────── trade offers (the season pauses until you answer) ─────────────────────────
function showTradePrompt(pr) {
  document.getElementById("tradeModal")?.remove();
  if (!pr || !pr.kind) return;
  const respond = async (action) => {
    try {
      const r = await api.post("/api/trade/respond", { action });
      document.getElementById("tradeModal")?.remove();
      if (action === "negotiate" && r.preset) { window.__tradePreset = r.preset; $('#nav [data-view=draft]').click(); }
    } catch (e) { toast(e.message, "err"); }
  };
  const box = pr.kind === "deadline"
    ? h("div", { class: "tm-box" }, h("h2", {}, "Trade deadline"), h("p", { class: "muted" }, `Game ${pr.completed} of ${pr.total}. The season is paused for your last trades: after you resume, nothing can be traded this year.`),
        h("div", { class: "tm-actions" }, h("button", { class: "btn", onclick: () => { document.getElementById("tradeModal")?.remove(); window.__tradeWait = true; $('#nav [data-view=draft]').click(); } }, "Open the trade window"),
          h("button", { class: "btn primary", onclick: () => respond("resume") }, "Finish: resume the season")))
    : h("div", { class: "tm-box" }, h("div", { class: "tm-kicker" }, "Trade offer · the season is paused"), h("h2", {}, `${pr.ai_team} want ${(pr.user_gives || [])[0] || "a player"}`), h("p", { class: "muted" }, pr.pitch || ""),
        h("div", { class: "tm-deal" }, h("div", {}, h("div", { class: "muted" }, "You send"), (pr.send || pr.user_gives || []).map((x) => h("div", { class: "tm-p" }, x))),
          h("div", { class: "tm-arrow" }, "⇄"), h("div", {}, h("div", { class: "muted" }, "You receive"), (pr.receive || pr.ai_gives || []).map((x) => h("div", { class: "tm-p" }, x)))),
        h("p", { class: "muted" }, `Effect on your top-ten rotation value: ${pr.user_change >= 0 ? "+" : ""}${(100 * (pr.user_change || 0)).toFixed(1)}%`),
        h("div", { class: "tm-actions" }, h("button", { class: "btn primary", onclick: () => respond("accept") }, "Accept"), h("button", { class: "btn", onclick: () => respond("negotiate") }, "Negotiate"), h("button", { class: "btn", onclick: () => respond("reject") }, "Reject")),
        h("p", { class: "muted", style: { fontSize: "12px" } }, "Negotiate opens the trade screen with this deal filled in; the season stays paused until you press Resume."));
  document.body.append(h("div", { id: "tradeModal", class: "tm-backdrop" }, box));
}

// ───────────────────────── boot ─────────────────────────
async function boot() {
  S.meta = await api.get("/api/meta");
  const modeSel = $("#mode");
  // the year seasons live on the Modes screen as buttons now, so the dropdown stays short
  const YEAR_SEASON = /^(\d{4}) season/;
  for (const m of S.meta.modes) { if (YEAR_SEASON.test(m.name) || m.name === "Custom 16-team playoffs") continue; modeSel.append(h("option", { value: m.name, disabled: !m.ready }, m.ready ? m.name : `${m.name} (Tk app for now)`)); }
  $("#seasonPresets").replaceChildren(...S.meta.modes.filter((m) => YEAR_SEASON.test(m.name) && m.ready).sort((a, b) => a.name.localeCompare(b.name)).map((m) => {
    const year = m.name.match(YEAR_SEASON)[1];
    return h("button", { class: "btn primary", onclick: () => startSpecial(m.name) }, `${year} season`);
  }));
  const pickTeams = async (kind) => {
    const d = await api.get("/api/teams/strength");
    let chosen;
    if (kind === "franchise") {   // the single best team-year of each franchise
      const seen = new Map();
      d.teams.forEach((t) => { if (!seen.has(t.franchise)) seen.set(t.franchise, t.name); });
      chosen = [...seen.values()].slice(0, 30);
    } else chosen = d.teams.slice(0, 30).map((t) => t.name);
    customSelected.clear(); chosen.forEach((n) => customSelected.add(n)); renderCustomTeams();
    toast(`${chosen.length} teams selected${kind === "franchise" ? " (the best team of each franchise)" : " (the 30 strongest)"}. Press Run 30-team season to play them.`, "ok");
  };
  $("#strong30").addEventListener("click", () => pickTeams("top").catch((e) => toast(e.message, "err")));
  $("#bestPerFranchise").addEventListener("click", () => pickTeams("franchise").catch((e) => toast(e.message, "err")));
  const syncMode = () => {
    S.mode = modeSel.value;
    const seasonal = isSeasonMode(S.mode);
    $$("#setup .field.grow, #setup .vs").forEach((el) => { el.style.display = seasonal ? "none" : ""; });
    $("#start").lastChild.textContent = seasonal ? " Start season" : " Tip off";
  };
  modeSel.addEventListener("change", syncMode);

  const pickA = makePicker($("#pickA"), (t) => { S.teamA = t.name; });
  const pickB = makePicker($("#pickB"), (t) => { S.teamB = t.name; });
  const preferred = S.meta.teams.filter((t) => t.year === "2027");
  const first = preferred[0] || S.meta.teams[0], second = preferred[1] || S.meta.teams[1];
  S.teamA = first.name; S.teamB = second.name;
  pickA.set(first); pickB.set(second);
  S.pickers = [pickA, pickB];
  CD.picker = makePicker($("#pickCards"), (t) => loadRoster(t.name));
  CD.picker.set(first);
  for (const sel of [$("#oneTeamA"), $("#oneTeamB")]) sel.append(...S.meta.teams.map((t)=>h("option",{value:t.name},t.name)));
  $("#oneTeamA").value=first.name; $("#oneTeamB").value=second.name;
  await fillOnePlayers("A"); await fillOnePlayers("B"); renderCustomTeams();

  $$("#rules button").forEach((b) => b.addEventListener("click", () => {
    $$("#rules button").forEach((x) => x.classList.toggle("on", x === b)); S.rules = b.dataset.v;
  }));
  $("#start").addEventListener("click", async () => {
    if(S.mode === "1-on-1") {$('#nav [data-view="one"]').click(); return;}
    if(S.mode.startsWith("Custom ")) {$('#nav [data-view="modes"]').click(); return;}
    if(S.mode.startsWith("Fantasy draft")) {$('#nav [data-view="draft"]').click();}
    try { await api.post("/api/start", { mode: S.mode, teamA: S.teamA, teamB: S.teamB, rules: S.rules }); }
    catch (err) { toast(err.message, "err"); }
  });
  $$("#seasonTabs button").forEach((b) => b.addEventListener("click", () => {
    $$("#seasonTabs button").forEach((x) => x.classList.toggle("on", x === b)); SE.tab = b.dataset.v; refreshSeason();
  }));
  $$("#brView button").forEach((b) => b.addEventListener("click", () => {
    $$("#brView button").forEach((x) => x.classList.toggle("on", x === b)); BR.view = b.dataset.v; renderBracket();
  }));
  $("#nextPost").addEventListener("click", async () => {
    try { await api.post("/api/start", { mode: "Next", teamA: "", teamB: "", rules: S.rules }); } catch (err) { toast(err.message, "err"); }
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
  $("#simPlayoffs").addEventListener("click", () => api.post("/api/control", { action: "simPlayoffs" }).catch((e) => toast(e.message, "err")));
  $("#simSeries").addEventListener("click", () => api.post("/api/control", { action: "simSeries" }).catch((e) => toast(e.message, "err")));
  $$('[data-coach]').forEach((b)=>b.addEventListener('click',async()=>{try{await api.post('/api/coach',{action:b.dataset.coach,team:CO.team});await loadCoach();}catch(e){toast(e.message,'err');}}));
  $("#lineupSave").addEventListener("click",()=>saveLineup(false).catch((e)=>toast(e.message,"err")));
  $("#lineupReset").addEventListener("click",()=>saveLineup(true).catch((e)=>toast(e.message,"err")));
  $$('[data-fantasy]').forEach((b)=>b.addEventListener('click',()=>startSpecial(b.dataset.fantasy==='2027'?'Fantasy draft: 2027 players (season + playoffs)':b.dataset.fantasy==='all'?'Fantasy draft: all-time (season + playoffs)':'Fantasy draft playoffs')));
  $("#tradeRefresh").addEventListener("click",loadTrades);
  $("#select2027").addEventListener("click",()=>{customSelected.clear();S.meta.teams.filter((t)=>t.year==='2027').slice(0,30).forEach((t)=>customSelected.add(t.name));renderCustomTeams();});
  $("#clearCustom").addEventListener("click",()=>{customSelected.clear();renderCustomTeams();});
  $("#customSeason").addEventListener("click",()=>startSpecial("Custom season (82 games)",{teams:[...customSelected]}));
  $("#olympics").addEventListener("click",()=>startSpecial("Olympic tournament"));
  $("#oneTeamA").addEventListener("change",()=>fillOnePlayers("A")); $("#oneTeamB").addEventListener("change",()=>fillOnePlayers("B"));
  $("#oneStart").addEventListener("click",()=>startSpecial("1-on-1",{teamA:$("#oneTeamA").value,playerA:$("#onePlayerA").value,teamB:$("#oneTeamB").value,playerB:$("#onePlayerB").value,target:11,winBy:2}));
  $("#replayRefresh").addEventListener("click",loadReplays);
  $$("#statsTabs button").forEach((b) => b.addEventListener("click", () => {
    $$("#statsTabs button").forEach((x) => x.classList.toggle("on", x === b));
    $("#statsKind").value = b.dataset.k; $("#statsKind").dispatchEvent(new Event("change", { bubbles: true }));
  }));
  $("#statsRefresh").addEventListener("click",()=>loadStats().catch(e=>toast(e.message,"err")));
  for(const id of ["statsKind","statsSource","statsTeam","statsQuarter"]) $("#"+id).addEventListener("change",()=>{statsSignature="";statsSort.column=-1;loadStats().catch(e=>toast(e.message,"err"));});
  $("#statsSearch").addEventListener("input",renderStats);

  $$("#feedFilter button").forEach((b) => b.addEventListener("click", () => {
    $$("#feedFilter button").forEach((x) => x.classList.toggle("on", x === b)); S.feedFilter = b.dataset.v;
    $("#rawlog").classList.toggle("hidden", S.feedFilter !== "raw");
    syncLatestButton();
    $("#feed").classList.toggle("hidden", S.feedFilter === "raw");
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
    if (b.dataset.view === "season") refreshSeason();
    if (b.dataset.view === "shottab") loadShots2().catch((e) => toast(e.message, "err"));
    if (b.dataset.view === "stats") loadStats().catch(e=>toast(e.message,"err"));
    if (b.dataset.view === "bracket") refreshBracket();
    if (b.dataset.view === "cards" && !CD.data) loadRoster(S.teamA);
    if (["qtr", "pcard", "shots"].includes(b.dataset.view)) refreshGameViews();
    if (b.dataset.view === "comp") loadCompare();
    if (b.dataset.view === "coach") loadCoach();
    if (b.dataset.view === "lineup") loadLineup();
    if (b.dataset.view === "draft") { loadDraft(); loadTrades(); }
    if (b.dataset.view === "modes") renderCustomTeams();
    if (b.dataset.view === "replay") loadReplays();
    if (b.dataset.view === "broadcast") loadBroadcast();
  }));
  document.addEventListener("keydown", (e) => {
    if (e.target.matches("input, select, textarea")) return;
    if (e.code === "Space") { e.preventDefault(); $("#pause").click(); }
  });

  renderScoreboard(); renderCourt(); renderCompare(); renderFlow("#flowMini", 170);
  connect();
  setInterval(()=>{ const view=$(".view.active")?.id; if(view==="view-coach")loadCoach(); else if(view==="view-draft")loadDraft(); else if(view==="view-broadcast")loadBroadcast(); },1000);
}

boot().catch((err) => toast(`Could not load: ${err.message}`, "err"));
