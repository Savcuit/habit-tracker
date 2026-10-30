
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

render();
