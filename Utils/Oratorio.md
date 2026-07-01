---
obsidianUIMode: preview
---
```dataviewjs
// ============================================================
// 🏠 ORATORIO — Gestione Settimanale
// ============================================================
const TAG = "#week";
const DAYS_ORDER = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica'];

// ── Font Awesome ──────────────────────────────────────────
const injectFA = () => {
    const id = 'fa-cdn-or';
    if (document.getElementById(id)) return;
    const link = document.createElement('link');
    link.id = id; link.rel = 'stylesheet';
    link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css';
    document.head.appendChild(link);
};
injectFA();

const fa = (name, cls = '') => {
    const i = document.createElement('i');
    i.className = `fa-solid fa-${name}${cls ? ' ' + cls : ''}`;
    return i;
};

// ── Parser ────────────────────────────────────────────────
const parseWeekFile = async (page) => {
    const file  = app.vault.getAbstractFileByPath(page.file.path);
    const raw   = await app.vault.read(file);
    const lines = raw.split('\n');

    const result = {
        date:     page.file.frontmatter?.date ?? null,
        fileName: page.file.name,
        filePath: page.file.path,
        giorni:   {},
        turni:    {},
    };

    let section    = null;
    let currentDay = null;

    lines.forEach((line, idx) => {
        const t    = line.trim();
        const bare = t.replace(/^#+\s*/, '');

        if (bare === 'Turni')  { section = 'turni';  currentDay = null; return; }
        if (bare === 'Giorni') { section = 'giorni'; currentDay = null; return; }

        if (section === 'turni') {
            const found = DAYS_ORDER.find(d => bare === d);
            if (found) {
                currentDay = found;
                if (!result.turni[found]) result.turni[found] = { persone: [], tasks: [] };
                return;
            }
        }

        const bullet = t.match(/^[*-]\s+(\[[ xX]\]\s+)?(.+)$/);
        if (!bullet) return;

        const hasCheckbox = !!bullet[1];
        const isChecked   = /[xX]/.test(bullet[1] ?? '');
        const text        = bullet[2].trim();

        if (section === 'turni' && currentDay) {
            const isOrgTask = hasCheckbox ||
                text.includes('#task') ||
                text.includes('📅') ||
                /[🔺⏫🔽]/u.test(text);

            if (isOrgTask) {
                const dlMatch   = text.match(/📅\s*(\d{4}-\d{2}-\d{2})/);
                const cleanText = text
                    .replace(/#\w+/g, '')
                    .replace(/📅\s*\d{4}-\d{2}-\d{2}/, '')
                    .replace(/[🔺⏫🔽]\s*\w*/gu, '')
                    .trim();

                // ✅ Push nell'array invece di sovrascrivere
                result.turni[currentDay].tasks.push({
                    text:      cleanText,
                    lineNum:   idx,
                    completed: isChecked,
                    deadline:  dlMatch ? dlMatch[1] : null,
                    filePath:  page.file.path,
                });
            } else {
                result.turni[currentDay].persone.push(text);
            }
        }

        if (section === 'giorni') {
            const dm = text.match(/^(Lunedì|Martedì|Mercoledì|Giovedì|Venerdì|Sabato|Domenica)\s+(.+)$/);
            if (dm) result.giorni[dm[1]] = dm[2];
        }
    });

    return result;
};

// ── Toggle ────────────────────────────────────────────────
const toggleTask = async (task, newState) => {
    const file = app.vault.getAbstractFileByPath(task.filePath);
    if (!file) return;
    const raw   = await app.vault.read(file);
    const lines = raw.split('\n');
    const line  = lines[task.lineNum];
    if (!line) return;

    if (line.match(/[-*]\s+\[[xX ]\]/)) {
        lines[task.lineNum] = line.replace(/\[[xX ]\]/, newState ? '[x]' : '[ ]');
    } else {
        lines[task.lineNum] = line.replace(/^(\s*[-*])\s+/, `$1 ${newState ? '[x]' : '[ ]'} `);
    }

    await app.vault.modify(file, lines.join('\n'));
    task.completed = newState;
};

// ── Stile ─────────────────────────────────────────────────
const injectStyle = (c) => {
    if (c.querySelector('style[data-or]')) return;
    const s = c.createEl('style');
    s.setAttribute('data-or', '1');
    s.textContent = `
    .or-wrap { font-family: var(--font-interface); }

    .or-tabs { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:1rem; }
    .or-tab {
        padding:4px 14px; border-radius:99px;
        border:1px solid var(--background-modifier-border);
        background:var(--background-secondary);
        color:var(--text-muted); font-size:0.82em;
        cursor:pointer; transition:all 0.15s;
    }
    .or-tab:hover { color:var(--text-normal); background:var(--background-modifier-hover); }
    .or-tab.active { background:var(--color-accent); color:#fff; border-color:var(--color-accent); }

    .or-header { display:flex; align-items:center; gap:10px; margin-bottom:0.9rem; }
    .or-header-icon {
        width:36px; height:36px; border-radius:9px;
        background:color-mix(in srgb, var(--color-accent) 12%, transparent);
        display:flex; align-items:center; justify-content:center;
        color:var(--color-accent); font-size:1em;
    }
    .or-header-title { font-weight:600; font-size:1em; color:var(--text-normal); }
    .or-header-sub   { font-size:0.78em; color:var(--text-faint); }

    .or-prog { display:flex; align-items:center; gap:8px; margin-bottom:1.1rem; }
    .or-prog-bg {
        flex:1; height:5px; border-radius:99px;
        background:var(--background-modifier-border); overflow:hidden;
    }
    .or-prog-fill { height:100%; border-radius:99px; background:var(--color-accent); transition:width 0.4s; }
    .or-prog-lbl  { font-size:0.75em; color:var(--text-faint); white-space:nowrap; }

    .or-grid {
        display:grid;
        grid-template-columns:repeat(auto-fill, minmax(190px, 1fr));
        gap:10px; margin-bottom:1rem;
    }

    .or-card {
        border-radius:10px;
        border:1px solid var(--background-modifier-border);
        background:var(--background-primary);
        overflow:hidden;
        animation: or-in 0.18s ease;
    }
    .or-card-head {
        padding:9px 12px 7px;
        background:var(--background-secondary);
        border-bottom:1px solid var(--background-modifier-border);
        display:flex; align-items:flex-start; gap:7px;
    }
    .or-day-icon { color:var(--color-accent); font-size:0.82em; margin-top:2px; }
    .or-day-name { font-weight:600; font-size:0.9em; color:var(--text-normal); flex:1; }
    .or-day-date { font-size:0.72em; color:var(--text-faint); margin-top:2px; }

    /* Dot stato aggregato */
    .or-dot { width:7px; height:7px; border-radius:50%; margin-top:5px; flex-shrink:0; }
    .or-dot.all-done  { background:#2f9e44; }
    .or-dot.partial   { background:#f08c00; }
    .or-dot.pending   { background:#e03131; }
    .or-dot.none      { background:var(--text-faint); opacity:0.3; }

    .or-card-body { padding:10px 12px; }

    .or-lbl {
        font-size:0.68em; text-transform:uppercase; letter-spacing:0.05em;
        color:var(--text-faint); font-weight:600; margin-bottom:5px;
        display:flex; align-items:center; gap:4px;
    }
    .or-person {
        display:flex; align-items:center; gap:6px;
        font-size:0.83em; color:var(--text-normal); padding:1px 0;
    }
    .or-person .fa-solid { color:var(--text-faint); font-size:0.75em; }

    .or-sep { border:none; border-top:1px solid var(--background-modifier-border); margin:8px 0; }

    /* Lista task */
    .or-task-item {
        display:flex; gap:7px; align-items:flex-start;
        padding:4px 0;
        border-bottom:1px dashed var(--background-modifier-border);
    }
    .or-task-item:last-child { border-bottom:none; }
    .or-task-item input[type="checkbox"] {
        width:14px; height:14px; margin-top:2px;
        cursor:pointer; accent-color:var(--color-accent); flex-shrink:0;
    }
    .or-task-txt { font-size:0.8em; color:var(--text-normal); line-height:1.4; flex:1; }
    .or-task-txt.done { color:var(--text-faint); text-decoration:line-through; }

    .or-dl {
        font-size:0.7em; color:var(--text-faint);
        display:flex; align-items:center; gap:3px; margin-top:2px;
    }
    .or-dl.overdue { color:#e03131; font-weight:600; }
    .or-dl.soon    { color:#f08c00; }

    /* Contatore task completati */
    .or-task-count {
        display:inline-flex; align-items:center; gap:4px;
        margin-left:auto;
        font-size:0.68em; padding:1px 7px; border-radius:99px;
        background:var(--background-secondary-alt); color:var(--text-muted);
    }
    .or-task-count.all { background:color-mix(in srgb,#2f9e44 15%,transparent); color:#2f9e44; }

    .or-no-task { font-size:0.78em; color:var(--text-faint); font-style:italic; }

    /* Confirm uncheck */
    .or-confirm { display:flex; gap:5px; margin-top:4px; }
    .or-cyes, .or-cno {
        font-size:0.7em; padding:2px 7px; border-radius:5px;
        border:1px solid var(--background-modifier-border);
        cursor:pointer; background:var(--background-secondary);
        display:flex; align-items:center; gap:3px; color:var(--text-muted);
    }
    .or-cyes { color:#2f9e44; border-color:#2f9e44; }
    .or-cyes:hover { background:#2f9e44; color:#fff; }
    .or-cno:hover  { background:var(--background-modifier-hover); }

    .or-stats {
        display:flex; gap:14px; flex-wrap:wrap;
        font-size:0.75em; color:var(--text-faint);
        padding-top:0.6rem;
        border-top:1px solid var(--background-modifier-border);
    }
    .or-stat { display:flex; align-items:center; gap:5px; }

    @keyframes or-in { from { opacity:0; transform:translateY(5px); } to { opacity:1; } }
    `;
};

// ── MAIN ──────────────────────────────────────────────────
const wrap = dv.container;
wrap.addClass('or-wrap');
injectStyle(wrap);

const main = async () => {
    const pagine = dv.pages(TAG).sort(p => p.file.frontmatter?.date, 'desc');

    if (!pagine.length) {
        const e = wrap.createEl('p');
        e.style.cssText = 'color:var(--text-faint);font-style:italic;';
        e.appendChild(fa('inbox')); e.append('  Nessuna settimana trovata con il tag ' + TAG);
        return;
    }

    const settimane = await Promise.all(pagine.map(p => parseWeekFile(p)));
    const state = { idx: 0 };

    const render = () => {
        wrap.querySelectorAll('.or-dyn').forEach(el => el.remove());
        const wk   = settimane[state.idx];
        const days = DAYS_ORDER.filter(d => wk.turni[d]);

        // ── TABS ────────────────────────────────────────
        if (settimane.length > 1) {
            const tabs = wrap.createEl('div', { cls: 'or-tabs or-dyn' });
            settimane.forEach((w, i) => {
                const btn = tabs.createEl('button', {
                    text: w.date ? 'Settimana ' + String(w.date) : w.fileName,
                    cls:  'or-tab' + (i === state.idx ? ' active' : ''),
                });
                btn.addEventListener('click', () => { state.idx = i; render(); });
            });
        }

        // ── HEADER ──────────────────────────────────────
        const hdr = wrap.createEl('div', { cls: 'or-header or-dyn' });
        const ico = hdr.createEl('div', { cls: 'or-header-icon' });
        ico.appendChild(fa('church'));
        const ht = hdr.createEl('div');
        ht.createEl('div', { text: 'Oratorio — Turni Settimanali', cls: 'or-header-title' });
        if (wk.date) ht.createEl('div', {
            text: 'Settimana del ' + String(wk.date), cls: 'or-header-sub'
        });

        // ── PROGRESS (tutti i task di tutti i giorni) ──
        const allTasks    = days.flatMap(d => wk.turni[d].tasks);
        const totalTasks  = allTasks.length;
        const doneTasks   = allTasks.filter(t => t.completed).length;
        const pct         = totalTasks ? Math.round(doneTasks / totalTasks * 100) : 0;

        const prog = wrap.createEl('div', { cls: 'or-prog or-dyn' });
        const pi   = fa('clipboard-check'); pi.style.color = 'var(--text-faint)';
        prog.appendChild(pi);
        const fill = prog.createEl('div', { cls: 'or-prog-bg' })
                         .createEl('div', { cls: 'or-prog-fill' });
        fill.style.width = pct + '%';
        prog.createEl('span', {
            text: `${doneTasks} / ${totalTasks} task completati (${pct}%)`,
            cls:  'or-prog-lbl',
        });

        // ── GRIGLIA ─────────────────────────────────────
        const grid = wrap.createEl('div', { cls: 'or-grid or-dyn' });

        days.forEach(dayName => {
            const d     = wk.turni[dayName];
            const date  = wk.giorni[dayName] ?? null;
            const tasks = d.tasks;

            const card = grid.createEl('div', { cls: 'or-card' });

            // Header card
            const ch   = card.createEl('div', { cls: 'or-card-head' });
            const chL  = ch.createEl('div', { style: 'flex:1' });
            const dRow = chL.createEl('div', { style: 'display:flex;align-items:center;gap:6px;' });
            dRow.appendChild(fa('calendar-day', 'or-day-icon'));
            dRow.createEl('span', { text: dayName, cls: 'or-day-name' });
            if (date) chL.createEl('div', { text: date, cls: 'or-day-date' });

            // Dot stato aggregato
            const dot = ch.createEl('span', { cls: 'or-dot' });
            if (!tasks.length)                          dot.addClass('none');
            else if (tasks.every(t => t.completed))     dot.addClass('all-done');
            else if (tasks.some(t => t.completed))      dot.addClass('partial');
            else                                        dot.addClass('pending');

            // Corpo card
            const body = card.createEl('div', { cls: 'or-card-body' });

            // Animatori
            if (d.persone.length) {
                const lbl = body.createEl('div', { cls: 'or-lbl' });
                lbl.appendChild(fa('users')); lbl.append(' Animatori');
                d.persone.forEach(p => {
                    const row = body.createEl('div', { cls: 'or-person' });
                    row.appendChild(fa('user')); row.append(' ' + p);
                });
            }

            // Separatore + header task
            body.createEl('hr', { cls: 'or-sep' });

            const tHeader = body.createEl('div', {
                cls: 'or-lbl', style: 'margin-bottom:6px;'
            });
            tHeader.appendChild(fa('clipboard-list')); tHeader.append(' Task');

            // Contatore task
            if (tasks.length) {
                const doneCount = tasks.filter(t => t.completed).length;
                const counter   = tHeader.createEl('span', {
                    text: `${doneCount}/${tasks.length}`,
                    cls:  'or-task-count' + (doneCount === tasks.length ? ' all' : ''),
                });
                counter.style.marginLeft = 'auto';
            }

            if (!tasks.length) {
                body.createEl('div', { text: 'Nessun task', cls: 'or-no-task' });
                return;
            }

            // ── Lista task ───────────────────────────────
            tasks.forEach(task => {
                const item = body.createEl('div', { cls: 'or-task-item' });
                const cb   = item.createEl('input');
                cb.type = 'checkbox'; cb.checked = task.completed;

                const right = item.createEl('div', { style: 'flex:1' });
                right.createEl('div', {
                    text: task.text || 'Task',
                    cls:  'or-task-txt' + (task.completed ? ' done' : ''),
                });

                // Scadenza
                if (task.deadline && !task.completed) {
                    const today = new Date(); today.setHours(0, 0, 0, 0);
                    const diff  = Math.ceil((new Date(task.deadline) - today) / 86400000);
                    let cls     = 'or-dl';
                    if (diff < 0)       cls += ' overdue';
                    else if (diff <= 3) cls += ' soon';
                    const dl = right.createEl('div', { cls });
                    if (diff < 0)       { dl.appendChild(fa('triangle-exclamation')); dl.append(' Scaduto'); }
                    else if (diff <= 3) { dl.appendChild(fa('clock')); dl.append(' ' + task.deadline); }
                    else                { dl.appendChild(fa('calendar-day')); dl.append(' ' + task.deadline); }
                }

                // Toggle
                if (task.completed) {
                    cb.addEventListener('change', () => {
                        cb.checked = true; cb.disabled = true;
                        const conf = item.createEl('div', { cls: 'or-confirm' });
                        const yes  = conf.createEl('span', { cls: 'or-cyes' });
                        yes.appendChild(fa('check')); yes.append(' Sì');
                        const no   = conf.createEl('span', { cls: 'or-cno' });
                        no.appendChild(fa('xmark'));
                        yes.addEventListener('click', async () => {
                            await toggleTask(task, false); render();
                        });
                        no.addEventListener('click', () => {
                            cb.disabled = false; conf.remove();
                        });
                    });
                } else {
                    cb.addEventListener('change', async () => {
                        await toggleTask(task, true); render();
                    });
                }
            });
        });

        // ── STATS ───────────────────────────────────────
        const stats      = wrap.createEl('div', { cls: 'or-stats or-dyn' });
        const totPersone = days.reduce((a, d) => a + wk.turni[d].persone.length, 0);

        const s1 = stats.createEl('span', { cls: 'or-stat' });
        s1.appendChild(fa('calendar-week')); s1.append(` ${days.length} giorni`);

        const s2 = stats.createEl('span', { cls: 'or-stat' });
        s2.appendChild(fa('users')); s2.append(` ${totPersone} animatori`);

        const s3 = stats.createEl('span', { cls: 'or-stat' });
        s3.style.color = '#2f9e44';
        s3.appendChild(fa('circle-check')); s3.append(` ${doneTasks} completati`);

        const s4 = stats.createEl('span', { cls: 'or-stat' });
        s4.style.color = '#e03131';
        s4.appendChild(fa('circle-xmark')); s4.append(` ${totalTasks - doneTasks} in sospeso`);
    };

    render();
};

main();
```