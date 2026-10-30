
const KEY = "nexus.habits.v1";
const PALETTE = ["#22d3ee","#38bdf8","#a78bfa","#f472b6","#facc15","#4ade80","#fb923c"];
const DAY_LETTERS = ["M","T","W","T","F","S","S"];

let state = load();
let selectedId = state.habits.length ? state.habits[0].id : null;

/* ---------------------------------------------------------------- storage */
function load(){
  try{
    const raw = localStorage.getItem(KEY);
    if(!raw) return {habits:[]};
    const data = JSON.parse(raw);
    if(!Array.isArray(data.habits)) return {habits:[]};
    return data;
  }catch(e){ return {habits:[]}; }
}
function save(){
  try{ localStorage.setItem(KEY, JSON.stringify(state)); }catch(e){}
}

/* ------------------------------------------------------------------ dates */
function iso(d){
  const p = n => String(n).padStart(2,"0");
  return d.getFullYear() + "-" + p(d.getMonth()+1) + "-" + p(d.getDate());
}
function todayStr(){ return iso(new Date()); }
function addDays(d, n){ const c = new Date(d); c.setDate(c.getDate()+n); return c; }
function parse(s){ const [y,m,d] = s.split("-").map(Number); return new Date(y, m-1, d); }

/* --------------------------------------------------------------- behaviour */
function isDone(h, day){ return h.done.includes(day || todayStr()); }
function toggle(h, day){
  day = day || todayStr();
  const i = h.done.indexOf(day);
  if(i >= 0) h.done.splice(i,1);
  else { h.done.push(day); h.done.sort(); }
  save();
}
function streak(h){
  let count = 0;
  let cursor = new Date();
  if(!isDone(h, iso(cursor))) cursor = addDays(cursor, -1);
  while(isDone(h, iso(cursor))){ count++; cursor = addDays(cursor, -1); }
  return count;
}
function bestStreak(h){
  if(!h.done.length) return 0;
  const days = [...new Set(h.done)].sort();
  let best = 1, run = 1;
  for(let i=1;i<days.length;i++){
    const diff = Math.round((parse(days[i]) - parse(days[i-1])) / 86400000);
    run = diff === 1 ? run + 1 : 1;
    if(run > best) best = run;
  }
  return best;
}
function weekDone(h){
  let n = 0;
  const now = new Date();
  for(let i=0;i<7;i++) if(isDone(h, iso(addDays(now, -i)))) n++;
  return n;
}
function completionRate(h, windowDays=30){
  const end = new Date();
  const created = parse(h.created);
  let start = addDays(end, -(windowDays-1));
  if(created > start) start = created;
  const span = Math.round((end - start)/86400000) + 1;
  if(span <= 0) return 0;
  let hits = 0;
  for(let i=0;i<span;i++) if(isDone(h, iso(addDays(end, -i)))) hits++;
  return hits/span;
}

/* ----------------------------------------------------------------- render */
function render(){
  const t = new Date();
  document.getElementById("today").textContent =
    t.toLocaleDateString(undefined,{weekday:"long", day:"numeric", month:"long", year:"numeric"});

  renderRing();
  renderList();
  renderDetail();
}

function renderRing(){
  const total = state.habits.length;
  const done = state.habits.filter(h => isDone(h)).length;
  const share = total ? done/total : 0;
  const circumference = 2 * Math.PI * 24;
  const arc = document.getElementById("ringArc");
  arc.setAttribute("stroke-dasharray", circumference.toFixed(1));
  arc.setAttribute("stroke-dashoffset", (circumference * (1 - share)).toFixed(1));
  document.getElementById("ringText").textContent = Math.round(share*100) + "%";
}

function renderList(){
  const card = document.getElementById("listCard");
  card.innerHTML = "";
  if(!state.habits.length){
    card.innerHTML = '<div class="empty">Nothing here yet.<br>Press “+ New habit” to begin.</div>';
    return;
  }
  state.habits.forEach(h => {
    const done = isDone(h);
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <div class="check" style="background:${done ? h.color : 'transparent'};
           border:2px solid ${done ? h.color : h.color + '66'}">
        ${done ? '<svg viewBox="0 0 24 24" fill="none" stroke="#06131f" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5 5L20 6.5"/></svg>' : ''}
      </div>
      <div style="flex:1">
        <div class="name ${done?'done':''}">${escapeHtml(h.name)}</div>
        <div class="sub">${weekDone(h)}/7 this week</div>
      </div>
      <div class="streak">${streak(h) ? streak(h) + "d" : ""}</div>`;

    row.querySelector(".check").addEventListener("click", ev => {
      ev.stopPropagation();
      toggle(h);
      selectedId = h.id;
      render();
    });
    row.addEventListener("click", () => { selectedId = h.id; render(); });
    card.appendChild(row);
  });
}

function renderDetail(){
  const host = document.getElementById("detail");
  const h = state.habits.find(x => x.id === selectedId);
  host.innerHTML = "";
  if(!h) return;

  const stats = document.createElement("div");
  stats.className = "stats";
  stats.innerHTML = `
    <div class="stat"><b style="color:var(--accent)">${streak(h)}</b><small>STREAK</small></div>
    <div class="stat"><b>${bestStreak(h)}</b><small>BEST</small></div>
    <div class="stat"><b>${weekDone(h)}/7</b><small>WEEK</small></div>
    <div class="stat"><b>${Math.round(completionRate(h)*100)}%</b><small>30 DAYS</small></div>`;
  host.appendChild(stats);

  const head = document.createElement("div");
  head.className = "card";
  head.innerHTML = `<div style="display:flex;align-items:center;justify-content:space-between;gap:10px">
      <div style="font-size:16px;font-weight:700">${escapeHtml(h.name)}</div>
      <div id="editBtn" style="font-size:12px;color:var(--accent);border:1px solid var(--border);
           border-radius:9px;padding:6px 10px">Edit</div></div>
    <div class="sub" style="margin-top:4px">Started ${parse(h.created).toLocaleDateString(undefined,
      {day:"numeric", month:"short", year:"numeric"})} · target ${h.target} days a week</div>`;
  host.appendChild(head);
  document.getElementById("editBtn").addEventListener("click", () => {
    document.getElementById("nameInput").value = h.name;
    draftColour = h.color;
    draftTarget = h.target;
    editing = h;
    buildDialog();
    document.querySelector("#dlg b").textContent = "EDIT HABIT";
    document.getElementById("saveBtn").textContent = "Save";
    document.getElementById("dlg").showModal();
  });

  const heatLabel = document.createElement("div");
  heatLabel.className = "label";
  heatLabel.textContent = "LAST 5 WEEKS";
  host.appendChild(heatLabel);

  const heat = document.createElement("div");
  heat.className = "heat";
  const end = new Date();
  for(let i=34;i>=0;i--){
    const day = addDays(end, -i);
    const key = iso(day);
    const cell = document.createElement("div");
    cell.className = "cell" + (isDone(h,key) ? " on" : "") + (key === todayStr() ? " today" : "");
    if(isDone(h,key)) cell.style.background = h.color;
    cell.title = key;
    cell.addEventListener("click", () => { toggle(h, key); render(); });
    heat.appendChild(cell);
  }
  host.appendChild(heat);

  const barLabel = document.createElement("div");
  barLabel.className = "label";
  barLabel.textContent = "SUCCESS BY WEEKDAY";
  host.appendChild(barLabel);

  const bars = document.createElement("div");
  bars.className = "bars";
  const totals = new Array(7).fill(0), hits = new Array(7).fill(0);
  let cursor = parse(h.created);
  const stop = new Date();
  while(cursor <= stop){
    const idx = (cursor.getDay() + 6) % 7;
    totals[idx]++;
    if(isDone(h, iso(cursor))) hits[idx]++;
    cursor = addDays(cursor, 1);
  }
  for(let i=0;i<7;i++){
    const rate = totals[i] ? hits[i]/totals[i] : 0;
    const wrap = document.createElement("div");
    wrap.className = "barwrap";
    wrap.innerHTML = `<div class="bar ${rate?'':'off'}" style="height:${Math.max(3, rate*86)}px;
      ${rate?'':'background:#1a2740'}"></div><small>${DAY_LETTERS[i]}</small>`;
    bars.appendChild(wrap);
  }
  host.appendChild(bars);

  const actions = document.createElement("div");
  actions.style.display = "flex";
  actions.style.gap = "10px";
  actions.innerHTML = `
    <button class="btn ghost" id="deleteBtn" style="color:var(--danger)">Delete habit</button>`;
  host.appendChild(actions);
  document.getElementById("deleteBtn").addEventListener("click", () => {
    if(!confirm("Delete “" + h.name + "” and all of its history?")) return;
    const index = state.habits.findIndex(x => x.id === h.id);
    const removed = state.habits.splice(index, 1)[0];
    selectedId = state.habits.length ? state.habits[0].id : null;
    save(); render();
    const bar = document.createElement("div");
    bar.style.cssText = "position:fixed;left:12px;right:12px;bottom:18px;background:#101a2e;border:1px solid #1e2d47;border-radius:12px;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;font-size:13px;z-index:9";
    bar.innerHTML = '<span>Deleted “' + escapeHtml(removed.name) + '”</span><b style="color:var(--accent)">UNDO</b>';
    bar.querySelector("b").addEventListener("click", () => {
      state.habits.splice(index, 0, removed);
      selectedId = removed.id;
      save(); render(); bar.remove();
    });
    document.body.appendChild(bar);
    setTimeout(() => bar.remove(), 6000);
  });
}

function escapeHtml(s){
  return s.replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

/* ------------------------------------------------------------------- new ---*/
let draftColour = PALETTE[0];
let draftTarget = 7;
let editing = null;

function buildDialog(){
  const sw = document.getElementById("swatches");
  sw.innerHTML = "";
  PALETTE.forEach(c => {
    const el = document.createElement("div");
    el.className = "sw" + (c === draftColour ? " sel" : "");
    el.style.background = c;
    el.addEventListener("click", () => { draftColour = c; buildDialog(); });
    sw.appendChild(el);
  });
  const days = document.getElementById("days");
  days.innerHTML = "";
  for(let n=1;n<=7;n++){
    const el = document.createElement("div");
    el.className = "day" + (n === draftTarget ? " sel" : "");
    el.textContent = n;
    el.addEventListener("click", () => { draftTarget = n; buildDialog(); });
    days.appendChild(el);
  }
}

document.getElementById("addBtn").addEventListener("click", () => {
  editing = null;
  document.getElementById("nameInput").value = "";
  draftColour = PALETTE[Math.floor(Math.random()*PALETTE.length)];
  draftTarget = 7;
  document.querySelector("#dlg b").textContent = "NEW HABIT";
  document.getElementById("saveBtn").textContent = "Create";
  buildDialog();
  document.getElementById("dlg").showModal();
});
document.getElementById("cancelBtn").addEventListener("click", () => document.getElementById("dlg").close());
document.getElementById("saveBtn").addEventListener("click", () => {
  const name = document.getElementById("nameInput").value.trim();
  if(!name) return;
  if(editing){
    editing.name = name;
    editing.color = draftColour;
    editing.target = draftTarget;
    selectedId = editing.id;
    editing = null;
    save();
    document.getElementById("dlg").close();
    render();
    return;
  }
  const habit = {
    id: Date.now().toString(36),
    name, color: draftColour, target: draftTarget,
    created: todayStr(), done: []
  };
  state.habits.push(habit);
  selectedId = habit.id;
  save();
  document.getElementById("dlg").close();
  render();
});

/* ------------------------------------------------------------------ pages */
function switchPage(name){
  ["today","stats","calendar"].forEach(p => {
    document.getElementById("page-" + p).hidden = (p !== name);
  });
  document.querySelectorAll("#tabs button").forEach(b => {
    b.classList.toggle("on", b.dataset.page === name);
  });
  document.querySelector(".footer").style.visibility = (name === "today") ? "visible" : "hidden";
  if(name === "stats") renderStats();
  if(name === "calendar") renderCalendar();
  window.scrollTo(0,0);
}
document.querySelectorAll("#tabs button").forEach(b => {
  b.addEventListener("click", () => switchPage(b.dataset.page));
});

/* ------------------------------------------------------------- statistics */
function habitsOn(day){
  return state.habits.filter(h => h.created <= day);
}
function dayCompletion(day){
  const list = habitsOn(day);
  if(!list.length) return null;
  return list.filter(h => h.done.includes(day)).length / list.length;
}
function series(days){
  const out = [];
  const now = new Date();
  for(let i=days-1;i>=0;i--){
    const d = iso(addDays(now, -i));
    out.push({day:d, pct: dayCompletion(d)});
  }
  return out;
}
function renderStats(){
  const all = state.habits;
  const totalTicks = all.reduce((n,h) => n + h.done.length, 0);
  const activeStreaks = all.map(streak).filter(Boolean);
  const bestNow = activeStreaks.length ? Math.max(...activeStreaks) : 0;
  const bestEver = all.length ? Math.max(...all.map(bestStreak)) : 0;
  const last30 = series(30).filter(p => p.pct !== null);
  const avg30 = last30.length ? last30.reduce((n,p) => n + p.pct, 0) / last30.length : 0;

  document.getElementById("bigStats").innerHTML = `
    <div class="stat"><b style="color:var(--accent)">${totalTicks}</b><small>TICKS</small></div>
    <div class="stat"><b>${bestNow}</b><small>STREAK</small></div>
    <div class="stat"><b>${bestEver}</b><small>BEST</small></div>
    <div class="stat"><b>${Math.round(avg30*100)}%</b><small>30 DAYS</small></div>`;

  // ---- trend line (SVG) ----
  const svg = document.getElementById("trendChart");
  const w = 320, h = 120, pad = 6;
  const pts = last30.map((p,i) => {
    const x = pad + (i * (w - pad*2) / Math.max(1, last30.length-1));
    const y = h - pad - (p.pct || 0) * (h - pad*2);
    return [x,y];
  });
  let path = "";
  pts.forEach((p,i) => { path += (i ? " L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1); });
  const area = path + ` L ${pts.length ? pts[pts.length-1][0].toFixed(1) : pad} ${h-pad} L ${pad} ${h-pad} Z`;
  svg.innerHTML = `
    <defs><linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity=".35"/>
      <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>
    </linearGradient></defs>
    <path d="${area}" fill="url(#g1)"></path>
    <path d="${path}" fill="none" stroke="#22d3ee" stroke-width="2" stroke-linejoin="round"></path>
    <line x1="${pad}" y1="${h-pad}" x2="${w-pad}" y2="${h-pad}" stroke="#1e2d47"></line>`;

  // ---- per-habit bars ----
  const table = document.getElementById("habitTable");
  table.innerHTML = "";
  if(!state.habits.length){
    table.innerHTML = '<div class="empty">No habits yet.</div>';
    return;
  }
  state.habits.forEach(h => {
    const pct = Math.round(completionRate(h) * 100);
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `<div class="bar-name">${escapeHtml(h.name)}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${h.color}"></div></div>
      <div class="bar-pct">${pct}%</div>`;
    table.appendChild(row);
  });
}

/* --------------------------------------------------------------- calendar */
let calMonth = new Date();
function renderCalendar(){
  const label = document.getElementById("monthLabel");
  const head = document.getElementById("calHead");
  const grid = document.getElementById("calGrid");
  const year = calMonth.getFullYear(), month = calMonth.getMonth();
  label.textContent = calMonth.toLocaleDateString(undefined,{month:"long", year:"numeric"});

  head.innerHTML = DAY_LETTERS.map(d => `<div>${d}</div>`).join("");

  const first = new Date(year, month, 1);
  const offset = (first.getDay() + 6) % 7;          // Monday-first
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  grid.innerHTML = "";
  for(let i=0;i<offset;i++){
    const pad = document.createElement("div");
    pad.className = "pad";
    grid.appendChild(pad);
  }
  for(let d=1; d<=daysInMonth; d++){
    const key = iso(new Date(year, month, d));
    const pct = dayCompletion(key) || 0;
    const cell = document.createElement("div");
    cell.textContent = d;
    cell.title = key + " · " + Math.round(pct*100) + "%";
    if(pct > 0){
      cell.style.background = "rgba(34,211,238," + (0.18 + pct*0.82).toFixed(2) + ")";
      cell.style.color = pct > 0.5 ? "#06131f" : "#cdeefb";
    } else if(key > todayStr()){
      cell.className = "dim";
      cell.style.opacity = ".35";
    }
    grid.appendChild(cell);
  }

  // overall weekday performance
  const totals = new Array(7).fill(0), hits = new Array(7).fill(0);
  state.habits.forEach(h => {
    let cursor = parse(h.created);
    const stop = new Date();
    while(cursor <= stop){
      const idx = (cursor.getDay() + 6) % 7;
      totals[idx]++;
      if(h.done.includes(iso(cursor))) hits[idx]++;
      cursor = addDays(cursor, 1);
    }
  });
  const bars = document.getElementById("globalBars");
  bars.innerHTML = "";
  for(let i=0;i<7;i++){
    const rate = totals[i] ? hits[i]/totals[i] : 0;
    const wrap = document.createElement("div");
    wrap.className = "barwrap";
    wrap.innerHTML = `<div class="bar" style="height:${Math.max(3, rate*80)}px;
       ${rate?'':'background:#1a2740'}"></div><small>${DAY_LETTERS[i]}</small>`;
    bars.appendChild(wrap);
  }
}
document.getElementById("prevMonth").addEventListener("click", () => {
  calMonth = new Date(calMonth.getFullYear(), calMonth.getMonth()-1, 1);
  renderCalendar();
});
document.getElementById("nextMonth").addEventListener("click", () => {
  calMonth = new Date(calMonth.getFullYear(), calMonth.getMonth()+1, 1);
  renderCalendar();
});

render();
