---
obsidianUIMode: preview
---

```dataviewjs
// ╔══════════════════════════════════════════════════════════════╗
//  🏛️  VAULT MASTER DASHBOARD — by DataviewJS
//  Richiede: Plugin "Dataview" con JavaScript abilitato
// ╚══════════════════════════════════════════════════════════════╝

const container = dv.container;
container.style.fontFamily = "var(--font-interface)";
container.style.padding = "0";
container.style.maxWidth = "100%";

// ────────────────────────────────────────────────────────────────
//  ⚙️  CONFIGURAZIONE — modifica questi valori
// ────────────────────────────────────────────────────────────────

const EXCLUDED_FOLDERS = ["Templates", "Excalidraw", "Utils"];

// ────────────────────────────────────────────────────────────────
//  RACCOLTA DATI (tutte le pagine filtrate)
// ────────────────────────────────────────────────────────────────

const allPages = dv.pages().filter(p => {
  const top = p.file.folder.split("/")[0] || "(root)";
  return !EXCLUDED_FOLDERS.includes(top);
});

const totalNotes = allPages.length;

// Date (Luxon)
const today    = dv.date("today");
const weekAgo  = today.minus({ days: 7 });
const monthAgo = today.minus({ days: 30 });

// Attività
const modifiedToday = allPages.filter(p => p.file.mtime >= today).length;
const modifiedWeek  = allPages.filter(p => p.file.mtime >= weekAgo).length;
const createdWeek   = allPages.filter(p => p.file.ctime >= weekAgo).length;
const createdMonth  = allPages.filter(p => p.file.ctime >= monthAgo).length;

// Dimensioni
const totalSize = allPages.values.reduce((a, p) => a + (p.file.size || 0), 0);
const avgSize   = totalNotes > 0 ? Math.round(totalSize / totalNotes) : 0;

// Tag
const allTags    = allPages.values.flatMap(p => p.file.tags?.values || []);
const tagMap     = {};
allTags.forEach(t => tagMap[t] = (tagMap[t] || 0) + 1);
const sortedTags  = Object.entries(tagMap).sort((a, b) => b[1] - a[1]);
const topTags     = sortedTags.slice(0, 20);
const uniqueTagsN = sortedTags.length;

// Cartelle — solo primo livello, già filtrate
const folderMap = {};
allPages.values.forEach(p => {
  const topLevel = p.file.folder.split("/")[0] || "(root)";
  folderMap[topLevel] = (folderMap[topLevel] || 0) + 1;
});
const sortedFolders = Object.entries(folderMap).sort((a, b) => b[1] - a[1]);
const totalFolders  = sortedFolders.length;

// Orfane
const orphaned    = allPages.filter(p => p.file.inlinks.length === 0 && p.file.outlinks.length === 0);
const noInlinks   = allPages.filter(p => p.file.inlinks.length === 0 && p.file.outlinks.length > 0);
const orphanedPct = totalNotes > 0 ? Math.round((orphaned.length / totalNotes) * 100) : 0;

// Senza tag
const noTags    = allPages.filter(p => !p.file.tags || p.file.tags.length === 0);
const noTagsPct = totalNotes > 0 ? Math.round((noTags.length / totalNotes) * 100) : 0;

// Task
const allTasks  = allPages.values.flatMap(p => p.file.tasks?.values || []);
const openTasks = allTasks.filter(t => !t.completed);
const doneTasks = allTasks.filter(t => t.completed);
const taskPct   = allTasks.length > 0 ? Math.round((doneTasks.length / allTasks.length) * 100) : 0;

// Liste ordinate
const recentModified = allPages.sort(p => p.file.mtime, "desc").slice(0, 10);
const recentCreated  = allPages.sort(p => p.file.ctime, "desc").slice(0, 10);
const longestNotes   = allPages.sort(p => p.file.size, "desc").slice(0, 10);
const stubNotes      = allPages.filter(p => (p.file.size || 0) < 200).sort(p => p.file.size, "asc").slice(0, 10);
const hubNotes       = allPages.sort(p => p.file.inlinks.length + p.file.outlinks.length, "desc").slice(0, 10);

// Health score
let health = 100;
if (orphanedPct > 30)      health -= 25;
else if (orphanedPct > 15) health -= 15;
else if (orphanedPct > 5)  health -= 7;
if (noTagsPct > 60)        health -= 20;
else if (noTagsPct > 40)   health -= 12;
else if (noTagsPct > 20)   health -= 6;
if (modifiedWeek === 0)    health -= 10;
if (totalNotes > 0 && openTasks.length / totalNotes > 0.5) health -= 5;
health = Math.max(0, Math.min(100, health));

const hColor = health >= 80 ? "#4ade80" : health >= 60 ? "#facc15" : "#f87171";
const hLabel = health >= 80 ? "Eccellente" : health >= 60 ? "Buono" : "Richiede attenzione";

// Grafico mensile (ultimi 12 mesi)
const monthlyData = {};
for (let i = 11; i >= 0; i--) {
  const m   = today.minus({ months: i });
  const key = m.toFormat("yyyy-MM");
  monthlyData[key] = { label: m.toFormat("MMM"), created: 0 };
}
allPages.values.forEach(p => {
  const ck = p.file.ctime?.toFormat("yyyy-MM");
  if (ck && monthlyData[ck]) monthlyData[ck].created++;
});
const months      = Object.values(monthlyData);
const maxMonthVal = Math.max(...months.map(m => m.created), 1);

const PALETTE = ["#60a5fa","#4ade80","#fb923c","#a78bfa","#f87171","#facc15","#34d399","#f472b6","#38bdf8","#e879f9"];

// ────────────────────────────────────────────────────────────────
//  CSS
// ────────────────────────────────────────────────────────────────

if (!document.getElementById("vmd-style")) {
  const st = document.createElement("style");
  st.id = "vmd-style";
  st.textContent = `
    .vmd { display:flex; flex-direction:column; gap:14px; padding:2px 0; }
    .vmd-header {
      display:flex; align-items:center; justify-content:space-between;
      padding:20px 24px; background:var(--background-secondary);
      border-radius:14px; border:1px solid var(--background-modifier-border);
    }
    .vmd-title   { font-size:20px; font-weight:800; color:var(--text-normal); letter-spacing:-0.5px; }
    .vmd-subtitle { font-size:11px; color:var(--text-muted); margin-top:3px; }
    .vmd-excluded { font-size:10px; color:var(--text-faint); margin-top:2px; }
    .vmd-health-wrap { display:flex; flex-direction:column; align-items:center; gap:5px; }
    .vmd-ring {
      width:68px; height:68px; border-radius:50%; border:4px solid;
      display:flex; align-items:center; justify-content:center;
      font-size:19px; font-weight:900;
    }
    .vmd-ring-label { font-size:9px; text-transform:uppercase; letter-spacing:1px; color:var(--text-muted); }
    .vmd-g4 { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }
    .vmd-g3 { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
    .vmd-g2 { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }
    @media(max-width:700px){
      .vmd-g4,.vmd-g3 { grid-template-columns:repeat(2,1fr); }
      .vmd-g2 { grid-template-columns:1fr; }
    }
    .vmd-card {
      background:var(--background-secondary);
      border:1px solid var(--background-modifier-border);
      border-radius:12px; padding:16px; overflow:hidden;
    }
    .vmd-stat { display:flex; flex-direction:column; gap:5px; }
    .vmd-stat-lbl { font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:1.2px; color:var(--text-muted); }
    .vmd-stat-num { font-size:30px; font-weight:900; line-height:1; }
    .vmd-stat-sub { font-size:10px; color:var(--text-faint); }
    .vmd-stitle {
      font-size:9px; font-weight:700; text-transform:uppercase;
      letter-spacing:1.3px; color:var(--text-muted);
      margin-bottom:10px; display:flex; align-items:center; gap:6px;
    }
    .vmd-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:3px; }
    .vmd-li {
      display:flex; align-items:center; justify-content:space-between;
      padding:5px 8px; border-radius:7px; font-size:11.5px; cursor:pointer;
      transition:background .12s;
    }
    .vmd-li:hover { background:var(--background-modifier-hover); }
    .vmd-li-name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--text-normal); }
    .vmd-b { font-size:9px; padding:2px 7px; border-radius:10px; font-weight:700; flex-shrink:0; margin-left:5px; }
    .vmd-blue   { background:rgba(96,165,250,.15);  color:#60a5fa; }
    .vmd-green  { background:rgba(74,222,128,.15);  color:#4ade80; }
    .vmd-orange { background:rgba(251,146,60,.15);  color:#fb923c; }
    .vmd-red    { background:rgba(248,113,113,.15); color:#f87171; }
    .vmd-purple { background:rgba(167,139,250,.15); color:#a78bfa; }
    .vmd-yellow { background:rgba(250,204,21,.15);  color:#facc15; }
    .vmd-bar-row { display:flex; align-items:center; gap:7px; margin-bottom:5px; font-size:10.5px; }
    .vmd-bar-lbl { width:110px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--text-muted); text-align:right; flex-shrink:0; }
    .vmd-bar-track { flex:1; height:7px; background:var(--background-modifier-border); border-radius:4px; overflow:hidden; }
    .vmd-bar-fill  { height:100%; border-radius:4px; }
    .vmd-bar-n    { width:26px; text-align:right; color:var(--text-faint); font-size:10px; flex-shrink:0; }
    .vmd-prog-row { display:flex; align-items:center; gap:8px; font-size:11px; margin-bottom:7px; }
    .vmd-prog-lbl { width:130px; font-size:10.5px; color:var(--text-muted); flex-shrink:0; }
    .vmd-prog-track { flex:1; height:7px; background:var(--background-modifier-border); border-radius:4px; overflow:hidden; }
    .vmd-prog-fill  { height:100%; border-radius:4px; }
    .vmd-prog-pct  { width:34px; text-align:right; font-size:10px; color:var(--text-faint); flex-shrink:0; }
    .vmd-warn { display:flex; align-items:center; gap:9px; padding:9px 13px; border-radius:8px; font-size:11px; margin-bottom:5px; }
    .vmd-warn-red    { background:rgba(248,113,113,.08); border:1px solid rgba(248,113,113,.25); }
    .vmd-warn-yellow { background:rgba(250,204,21,.08);  border:1px solid rgba(250,204,21,.25); }
    .vmd-warn-green  { background:rgba(74,222,128,.08);  border:1px solid rgba(74,222,128,.25); }
    .vmd-warn-blue   { background:rgba(96,165,250,.08);  border:1px solid rgba(96,165,250,.25); }
    .vmd-div { height:1px; background:var(--background-modifier-border); margin:8px 0; }
    details.vmd-det > summary { cursor:pointer; list-style:none; display:flex; align-items:center; justify-content:space-between; }
    details.vmd-det > summary::-webkit-details-marker { display:none; }
    .vmd-chev { transition:transform .18s; font-size:10px; color:var(--text-muted); }
    details.vmd-det[open] .vmd-chev { transform:rotate(180deg); }
    .vmd-chips { display:flex; flex-wrap:wrap; gap:5px; margin-top:8px; }
    .vmd-chip {
      font-size:10.5px; padding:3px 10px; border-radius:12px; cursor:pointer;
      background:rgba(248,113,113,.1); color:#f87171;
      border:1px solid rgba(248,113,113,.25); transition:all .15s;
    }
    .vmd-chip:hover { background:#f87171; color:white; }
    .vmd-footer { text-align:center; font-size:10px; color:var(--text-faint); padding:6px 0 0; }
    .vmd-task { display:flex; align-items:flex-start; gap:6px; padding:5px 8px; border-radius:7px; font-size:11px; cursor:pointer; }
    .vmd-task:hover { background:var(--background-modifier-hover); }
    .vmd-task-dot  { color:#fb923c; flex-shrink:0; margin-top:1px; }
    .vmd-task-text { flex:1; color:var(--text-normal); overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; }
    .vmd-task-src  { font-size:9px; color:var(--text-faint); flex-shrink:0; margin-top:1px; }
    .vmd-empty { text-align:center; padding:18px; color:var(--text-faint); font-size:11px; }
    .vmd-actions { display:flex; flex-wrap:wrap; gap:7px; }
    .vmd-btn {
      font-size:11px; padding:6px 14px; border-radius:8px; cursor:pointer; border:none;
      background:var(--interactive-normal); color:var(--text-normal); transition:all .15s;
      display:flex; align-items:center; gap:5px;
    }
    .vmd-btn:hover { background:var(--interactive-hover); }
    .vmd-btn-accent { background:var(--color-accent); color:white; }
    .vmd-btn-accent:hover { opacity:.9; }
    .vmd-excl-pill {
      display:inline-flex; align-items:center; gap:4px;
      font-size:9px; padding:2px 7px; border-radius:10px; margin-right:4px;
      background:var(--background-modifier-border); color:var(--text-faint);
    }
  `;
  document.head.appendChild(st);
}

// ────────────────────────────────────────────────────────────────
//  HELPERS
// ────────────────────────────────────────────────────────────────

function openFile(path) {
  const file = app.vault.getAbstractFileByPath(path);
  if (file) app.workspace.getLeaf(false).openFile(file);
}

function makeStatCard(parent, label, value, sub, accent) {
  const card = parent.createEl("div", { cls: "vmd-card vmd-stat" });
  card.style.borderTop = `3px solid ${accent}`;
  card.createEl("div", { cls: "vmd-stat-lbl", text: label });
  const n = card.createEl("div", { cls: "vmd-stat-num", text: String(value) });
  n.style.color = accent;
  card.createEl("div", { cls: "vmd-stat-sub", text: sub });
  return card;
}

function makeList(parent, items, { badgeCls = "vmd-blue", getBadge, getName, getPath } = {}) {
  const ul = parent.createEl("ul", { cls: "vmd-list" });
  items.forEach(item => {
    const li = ul.createEl("li", { cls: "vmd-li" });
    li.createEl("span", { cls: "vmd-li-name", text: getName(item) });
    if (getBadge) li.createEl("span", { cls: `vmd-b ${badgeCls}`, text: getBadge(item) });
    if (getPath)  li.addEventListener("click", () => openFile(getPath(item)));
  });
}

function makeBar(parent, label, count, maxCount, color) {
  const row = parent.createEl("div", { cls: "vmd-bar-row" });
  const lbl = row.createEl("div", { cls: "vmd-bar-lbl" });
  lbl.textContent = label;
  lbl.title = label;
  const track = row.createEl("div", { cls: "vmd-bar-track" });
  const fill  = track.createEl("div", { cls: "vmd-bar-fill" });
  fill.style.width      = `${Math.max(3, Math.round((count / maxCount) * 100))}%`;
  fill.style.background = color;
  row.createEl("div", { cls: "vmd-bar-n", text: String(count) });
}

function makeProgress(parent, label, value, total, color) {
  const pct  = total > 0 ? Math.round((value / total) * 100) : 0;
  const row  = parent.createEl("div", { cls: "vmd-prog-row" });
  row.createEl("div", { cls: "vmd-prog-lbl", text: label });
  const track = row.createEl("div", { cls: "vmd-prog-track" });
  const fill  = track.createEl("div", { cls: "vmd-prog-fill" });
  fill.style.width      = `${pct}%`;
  fill.style.background = color;
  row.createEl("div", { cls: "vmd-prog-pct", text: `${pct}%` });
}

function makeCollapsible(parent, title, badgeText, badgeCls = "vmd-blue") {
  const details = parent.createEl("details", { cls: "vmd-det" });
  const summary = details.createEl("summary");
  const titleEl = summary.createEl("div", { cls: "vmd-stitle", text: title });
  titleEl.style.marginBottom = "0";
  if (badgeText) titleEl.createEl("span", { cls: `vmd-b ${badgeCls}`, text: badgeText });
  summary.createEl("span", { cls: "vmd-chev", text: "▾" });
  return details;
}

function warn(parent, icon, text, type = "yellow") {
  const w = parent.createEl("div", { cls: `vmd-warn vmd-warn-${type}` });
  w.createEl("span", { text: icon });
  w.createEl("span", { text });
}

// ────────────────────────────────────────────────────────────────
//  BUILD DOM
// ────────────────────────────────────────────────────────────────

const dash = container.createEl("div", { cls: "vmd" });

// ╔══════════════════════════════════════════════╗
//  HEADER
// ╚══════════════════════════════════════════════╝
const hdr   = dash.createEl("div", { cls: "vmd-header" });
const hLeft = hdr.createEl("div");
hLeft.createEl("div", { cls: "vmd-title", text: "⟁ Vault Master Dashboard" });
hLeft.createEl("div", {
  cls: "vmd-subtitle",
  text: `${today.toFormat("cccc d MMMM yyyy")} · ${app.vault.getName()} · ${totalNotes} note · ${totalFolders} cartelle`
});

// Pill cartelle escluse
const exclRow = hLeft.createEl("div", { cls: "vmd-excluded" });
exclRow.createEl("span", { text: "Escluse: " });
EXCLUDED_FOLDERS.forEach(f => exclRow.createEl("span", { cls: "vmd-excl-pill", text: f }));

const hRight = hdr.createEl("div", { cls: "vmd-health-wrap" });
const ring   = hRight.createEl("div", { cls: "vmd-ring", text: `${health}` });
ring.style.borderColor = hColor;
ring.style.color       = hColor;
hRight.createEl("div", { cls: "vmd-ring-label", text: `Salute: ${hLabel}` });

// ╔══════════════════════════════════════════════╗
//  AZIONI RAPIDE
// ╚══════════════════════════════════════════════╝
const actCard = dash.createEl("div", { cls: "vmd-card" });
actCard.createEl("div", { cls: "vmd-stitle", text: "⚡ Azioni Rapide" });
const actions = actCard.createEl("div", { cls: "vmd-actions" });

const btns = [
  { label: "📝 Nuova Nota",      action: () => app.commands.executeCommandById("app:create-new-note-in-vault") },
  { label: "📋 Grafo",           action: () => app.commands.executeCommandById("graph:open") },
  { label: "🔍 Cerca",           action: () => app.commands.executeCommandById("global-search:open") },
  { label: "⚙️ Impostazioni",    action: () => app.commands.executeCommandById("app:open-settings") },
  { label: "📅 Nota Giornaliera",action: () => app.commands.executeCommandById("daily-notes") },
  { label: "🏷️ Tag Pane",        action: () => app.commands.executeCommandById("tag-pane:open") },
];
btns.forEach((b, i) => {
  const btn = actions.createEl("button", { cls: i === 0 ? "vmd-btn vmd-btn-accent" : "vmd-btn", text: b.label });
  btn.addEventListener("click", () => { try { b.action(); } catch(e) {} });
});

// ╔══════════════════════════════════════════════╗
//  STAT CARDS × 4
// ╚══════════════════════════════════════════════╝
const statsGrid = dash.createEl("div", { cls: "vmd-g4" });
makeStatCard(statsGrid, "Note Totali",     totalNotes,       `+${createdMonth} ultimi 30gg`,                    "#60a5fa");
makeStatCard(statsGrid, "Modificate Oggi", modifiedToday,    `${modifiedWeek} questa settimana`,                 "#4ade80");
makeStatCard(statsGrid, "Task Aperti",     openTasks.length, `${doneTasks.length} completati · ${taskPct}%`,    "#fb923c");
makeStatCard(statsGrid, "Note Orfane",     orphaned.length,  `${orphanedPct}% del vault`,                       orphaned.length > 0 ? "#f87171" : "#4ade80");

// ╔══════════════════════════════════════════════╗
//  RIGA: RECENTI + SALUTE VAULT
// ╚══════════════════════════════════════════════╝
const row1 = dash.createEl("div", { cls: "vmd-g3" });

const rMod = row1.createEl("div", { cls: "vmd-card" });
rMod.createEl("div", { cls: "vmd-stitle", text: "🕐 Modificate di Recente" });
makeList(rMod, recentModified.values, {
  badgeCls: "vmd-blue",
  getName:  p => p.file.name,
  getBadge: p => p.file.mtime.toFormat("dd/MM"),
  getPath:  p => p.file.path
});

const rCre = row1.createEl("div", { cls: "vmd-card" });
rCre.createEl("div", { cls: "vmd-stitle", text: "✨ Ultime Note Create" });
makeList(rCre, recentCreated.values, {
  badgeCls: "vmd-green",
  getName:  p => p.file.name,
  getBadge: p => p.file.ctime.toFormat("dd/MM"),
  getPath:  p => p.file.path
});

const healthCard = row1.createEl("div", { cls: "vmd-card" });
healthCard.createEl("div", { cls: "vmd-stitle", text: "🩺 Salute del Vault" });
makeProgress(healthCard, "Note collegate",    totalNotes - orphaned.length,  totalNotes,                "#4ade80");
makeProgress(healthCard, "Note con tag",      totalNotes - noTags.length,    totalNotes,                "#60a5fa");
makeProgress(healthCard, "Note con backlink", totalNotes - noInlinks.length, totalNotes,                "#a78bfa");
makeProgress(healthCard, "Task completati",   doneTasks.length,              Math.max(1, allTasks.length), "#fb923c");
healthCard.createEl("div", { cls: "vmd-div" });

if (orphaned.length === 0 && noTags.length === 0) {
  warn(healthCard, "✅", "Vault in ottima forma!", "green");
} else {
  if (orphaned.length > 0)  warn(healthCard, "🔴", `${orphaned.length} note orfane senza nessun link`, orphaned.length > 10 ? "red" : "yellow");
  if (noTags.length > 0)    warn(healthCard, "🏷️", `${noTags.length} note (${noTagsPct}%) senza tag`, "yellow");
  if (modifiedWeek === 0)   warn(healthCard, "⏸️", "Nessuna nota modificata questa settimana", "blue");
}

// ╔══════════════════════════════════════════════╗
//  RIGA: CARTELLE + TAG
// ╚══════════════════════════════════════════════╝
const row2 = dash.createEl("div", { cls: "vmd-g2" });

const fCard = row2.createEl("div", { cls: "vmd-card" });
fCard.createEl("div", { cls: "vmd-stitle", text: `📁 Cartelle Primo Livello · ${totalFolders} visibili` });
const maxF = sortedFolders[0]?.[1] || 1;
sortedFolders.forEach(([folder, count], i) => {
  makeBar(fCard, folder, count, maxF, PALETTE[i % PALETTE.length]);
});

const tCard = row2.createEl("div", { cls: "vmd-card" });
tCard.createEl("div", { cls: "vmd-stitle", text: `🏷️ Tag più Usati · ${uniqueTagsN} unici · ${allTags.length} totali` });
if (topTags.length === 0) {
  tCard.createEl("div", { cls: "vmd-empty", text: "Nessun tag trovato nel vault" });
} else {
  const maxT = topTags[0][1];
  topTags.forEach(([tag, count]) => makeBar(tCard, tag, count, maxT, "var(--color-accent)"));
}

// ╔══════════════════════════════════════════════╗
//  ATTIVITÀ MENSILE
// ╚══════════════════════════════════════════════╝
const actCard2 = dash.createEl("div", { cls: "vmd-card" });
actCard2.createEl("div", { cls: "vmd-stitle", text: "📈 Attività Ultimi 12 Mesi" });

const chartWrap = actCard2.createEl("div");
chartWrap.style.cssText = "display:flex; align-items:flex-end; gap:6px; height:80px; padding:4px 0 2px";
months.forEach(m => {
  const col = chartWrap.createEl("div");
  col.style.cssText = "flex:1; display:flex; flex-direction:column; align-items:center; gap:2px; height:100%";
  const barArea = col.createEl("div");
  barArea.style.cssText = "flex:1; display:flex; flex-direction:column-reverse; gap:2px; width:100%; align-items:center";
  const bcH = Math.round((m.created / maxMonthVal) * 60);
  if (bcH > 0) {
    const bc = barArea.createEl("div");
    bc.style.cssText = `width:100%; height:${bcH}px; background:#4ade80; border-radius:3px 3px 0 0; min-height:3px`;
    bc.title = `${m.label}: ${m.created} create`;
  }
  col.createEl("div", { text: m.label.slice(0, 3) }).style.cssText = "font-size:8px; color:var(--text-faint); text-align:center";
});
const legend = actCard2.createEl("div");
legend.style.cssText = "display:flex; gap:14px; margin-top:6px; font-size:10px; color:var(--text-faint)";
const l1 = legend.createEl("div");
l1.style.cssText = "display:flex; align-items:center; gap:5px";
const dot1 = l1.createEl("div");
dot1.style.cssText = "width:10px; height:10px; border-radius:2px; background:#4ade80";
l1.createEl("span", { text: "Note create" });

// ╔══════════════════════════════════════════════╗
//  RIGA: HUB NOTES + TASK APERTI
// ╚══════════════════════════════════════════════╝
const row3 = dash.createEl("div", { cls: "vmd-g2" });

const hubCard = row3.createEl("div", { cls: "vmd-card" });
hubCard.createEl("div", { cls: "vmd-stitle", text: "🔗 Note Hub (più collegate)" });
makeList(hubCard, hubNotes.values, {
  badgeCls: "vmd-purple",
  getName:  p => p.file.name,
  getBadge: p => `↔ ${p.file.inlinks.length + p.file.outlinks.length}`,
  getPath:  p => p.file.path
});

const taskCard = row3.createEl("div", { cls: "vmd-card" });
taskCard.createEl("div", { cls: "vmd-stitle", text: `☑️ Task Aperti · ${openTasks.length} da fare` });
if (openTasks.length === 0) {
  taskCard.createEl("div", { cls: "vmd-empty", text: "✅ Nessun task aperto. Ottimo lavoro!" });
} else {
  openTasks.slice(0, 8).forEach(t => {
    const row = taskCard.createEl("div", { cls: "vmd-task" });
    row.createEl("span", { cls: "vmd-task-dot", text: "○" });
    row.createEl("span", { cls: "vmd-task-text", text: t.text });
    const src = t.path?.split("/").pop()?.replace(".md", "") || "";
    if (src) row.createEl("span", { cls: "vmd-task-src", text: src });
    row.addEventListener("click", () => openFile(t.path || ""));
  });
  if (openTasks.length > 8)
    taskCard.createEl("div", { text: `+${openTasks.length - 8} altri task…`, style: "font-size:10px;color:var(--text-faint);margin-top:6px;text-align:center" });
}

// ╔══════════════════════════════════════════════╗
//  RIGA: NOTE LUNGHE + STUB
// ╚══════════════════════════════════════════════╝
const row4 = dash.createEl("div", { cls: "vmd-g2" });

const longCard = row4.createEl("div", { cls: "vmd-card" });
longCard.createEl("div", { cls: "vmd-stitle", text: "📚 Note più Ricche (per dimensione)" });
makeList(longCard, longestNotes.values, {
  badgeCls: "vmd-blue",
  getName:  p => p.file.name,
  getBadge: p => `${Math.round((p.file.size || 0) / 1024 * 10) / 10} KB`,
  getPath:  p => p.file.path
});

const stubCard = row4.createEl("div", { cls: "vmd-card" });
stubCard.style.borderTop = "3px solid #facc15";
stubCard.createEl("div", { cls: "vmd-stitle", text: "📄 Stub (note troppo corte)" });
if (stubNotes.length === 0) {
  stubCard.createEl("div", { cls: "vmd-empty", text: "✅ Nessuna nota stub" });
} else {
  makeList(stubCard, stubNotes.values, {
    badgeCls: "vmd-yellow",
    getName:  p => p.file.name,
    getBadge: p => `${p.file.size || 0} B`,
    getPath:  p => p.file.path
  });
}

// ╔══════════════════════════════════════════════╗
//  NOTE ORFANE (collassabile)
// ╚══════════════════════════════════════════════╝
if (orphaned.length > 0) {
  const orphCard = dash.createEl("div", { cls: "vmd-card" });
  orphCard.style.borderTop = "3px solid #f87171";
  const det   = makeCollapsible(orphCard, "🔴 Note Orfane — nessun link in entrata né in uscita", `${orphaned.length}`, "vmd-red");
  const chips = det.createEl("div", { cls: "vmd-chips" });
  orphaned.values.forEach(p => {
    const chip = chips.createEl("span", { cls: "vmd-chip", text: p.file.name });
    chip.addEventListener("click", () => openFile(p.file.path));
  });
}

// Note senza tag (collassabile)
if (noTags.length > 0) {
  const noTagCard = dash.createEl("div", { cls: "vmd-card" });
  noTagCard.style.borderTop = "3px solid #facc15";
  const det2 = makeCollapsible(noTagCard, "🏷️ Note senza Tag", `${noTags.length}`, "vmd-yellow");
  const ul2  = det2.createEl("ul", { cls: "vmd-list" });
  ul2.style.marginTop = "8px";
  noTags.values.slice(0, 30).forEach(p => {
    const li = ul2.createEl("li", { cls: "vmd-li" });
    li.createEl("span", { cls: "vmd-li-name", text: p.file.name });
    li.createEl("span", { cls: "vmd-b vmd-yellow", text: p.file.folder.split("/")[0] || "(root)" });
    li.addEventListener("click", () => openFile(p.file.path));
  });
  if (noTags.length > 30)
    det2.createEl("div", { text: `+${noTags.length - 30} altre note…`, style: "font-size:10px;color:var(--text-faint);margin-top:6px;padding:0 8px" });
}

// ╔══════════════════════════════════════════════╗
//  RIEPILOGO NUMERICO
// ╚══════════════════════════════════════════════╝
const sumCard = dash.createEl("div", { cls: "vmd-card" });
sumCard.createEl("div", { cls: "vmd-stitle", text: "📊 Riepilogo Completo Vault" });
const sumGrid = sumCard.createEl("div");
sumGrid.style.cssText = "display:grid; grid-template-columns:repeat(auto-fill,minmax(170px,1fr)); gap:8px";

const summaryStats = [
  ["📝 Note totali",         totalNotes],
  ["📁 Cartelle visibili",   totalFolders],
  ["🚫 Cartelle escluse",    EXCLUDED_FOLDERS.length],
  ["🏷️ Tag unici",           uniqueTagsN],
  ["🔗 Tag totali",          allTags.length],
  ["✨ Create questa sett.", createdWeek],
  ["🕐 Modificate oggi",     modifiedToday],
  ["🔴 Orfane",              orphaned.length],
  ["🏷️ Senza tag",           noTags.length],
  ["☑️ Task aperti",         openTasks.length],
  ["✅ Task completati",      doneTasks.length],
  ["📦 Dim. media nota",     `${avgSize} B`],
];
summaryStats.forEach(([label, val]) => {
  const cell = sumGrid.createEl("div");
  cell.style.cssText = "padding:9px 12px; background:var(--background-primary); border-radius:8px; border:1px solid var(--background-modifier-border)";
  cell.createEl("div", { text: label }).style.cssText = "font-size:9px;color:var(--text-faint);text-transform:uppercase;letter-spacing:.8px;margin-bottom:3px";
  cell.createEl("div", { text: String(val) }).style.cssText = "font-size:15px;font-weight:700;color:var(--text-normal)";
});

// ╔══════════════════════════════════════════════╗
//  FOOTER
// ╚══════════════════════════════════════════════╝
dash.createEl("div", {
  cls:  "vmd-footer",
  text: `Vault: "${app.vault.getName()}" · ${totalNotes} note · escluse: ${EXCLUDED_FOLDERS.join(", ")} · Dashboard generata con DataviewJS`
});
```