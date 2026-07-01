---
obsidianUIMode: preview
---


```dataviewjs
// ============================================================
// 🔍 CONFIG
// ============================================================
const TAG = "#task";

// ============================================================
// 🎨 FONT AWESOME — inject una sola volta
// ============================================================
const injectFA = () => {
    const id = 'fa-cdn-rv';
    if (document.getElementById(id)) return;
    const link = document.createElement('link');
    link.id   = id;
    link.rel  = 'stylesheet';
    link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css';
    document.head.appendChild(link);
};
injectFA();

// Helper: crea icona FA
const fa = (name, cls = '') => {
    const i = document.createElement('i');
    i.className = `fa-solid fa-${name}${cls ? ' ' + cls : ''}`;
    return i;
};

// ============================================================
// 🧩 PARSE METADATA
// ============================================================
const parseTaskMeta = (rawText) => {
    let text = rawText;

    const dlMatch = text.match(/📅\s*(\d{4}-\d{2}-\d{2})/);
    const deadline = dlMatch ? dlMatch[1] : null;
    if (dlMatch) text = text.replace(dlMatch[0], '').trim();

    const PRIORITIES = [
        { icon: '🔺', faIcon: 'angles-up',   label: 'Urgente', val: 3, color: '#e03131' },
        { icon: '⏫', faIcon: 'angle-up',     label: 'Alta',    val: 2, color: '#f08c00' },
        { icon: '🔽', faIcon: 'angle-down',   label: 'Bassa',   val: 1, color: '#5c7cfa' },
    ];
    let priority = { icon: '', faIcon: '', label: '', val: 0, color: '' };
    for (const p of PRIORITIES) {
        if (text.includes(p.icon)) {
            priority = p;
            text = text.replace(p.icon, '').trim();
            break;
        }
    }

    const tags = text.match(/#[\w-]+/g) ?? [];
    text = text.replace(/#[\w-]+/g, '').trim().replace(/\s+/g, ' ');

    return { text, deadline, priority, tags };
};

// ============================================================
// 📄 RACCOLTA TASK
// ============================================================
const pagine = dv.pages(TAG);

const tuttiTask = pagine.flatMap(p =>
    (p.file.tasks ?? [])
        .filter(t => t.text?.trim())
        .map(t => {
            const meta = parseTaskMeta(t.text.trim());
            return {
                testo:      meta.text,
                deadline:   meta.deadline,
                priority:   meta.priority,
                tags:       meta.tags,
                completato: t.completed ?? false,
                sezione:    t.section?.subpath ?? t.section?.path ?? "—",
                data:       p.file.frontmatter?.date ?? "—",
                filePath:   p.file.path,
                lineNum:    t.line,
                ordineData: p.file.frontmatter?.date
                              ? new Date(p.file.frontmatter.date)
                              : new Date(0),
            };
        })
);

const sezioniUniche = ['Tutte', ...new Set(tuttiTask.map(t => t.sezione))];

// ============================================================
// 🔄 TOGGLE
// ============================================================
const toggleTask = async (task, newState) => {
    const file = app.vault.getAbstractFileByPath(task.filePath);
    if (!file) return;
    const content = await app.vault.read(file);
    const lines = content.split('\n');
    if (!lines[task.lineNum]) return;
    lines[task.lineNum] = lines[task.lineNum].replace(
        /- \[[xX ]\]/,
        newState ? '- [x]' : '- [ ]'
    );
    await app.vault.modify(file, lines.join('\n'));
    task.completato = newState;
};

// ============================================================
// ➕ AGGIUNGI TASK
// ============================================================
const addTask = async (filePath, taskText) => {
    const file = app.vault.getAbstractFileByPath(filePath);
    if (!file) return false;
    const content = await app.vault.read(file);
    await app.vault.modify(file, content.trimEnd() + '\n- [ ] ' + taskText.trim() + '\n');
    return true;
};

// ============================================================
// 📤 EXPORT CSV
// ============================================================
const exportCSV = (tasks) => {
    const escape = s => `"${String(s ?? '').replace(/"/g, '""')}"`;
    const header = ['Obiettivo','Priorità','Scadenza','Tag','Ambito','Data','File','Stato'].join(',');
    const rows = tasks.map(t => [
        escape(t.testo),
        escape(t.priority.label || '—'),
        escape(t.deadline || '—'),
        escape(t.tags.join(' ') || '—'),
        escape(t.sezione),
        escape(t.data),
        escape(t.filePath.split('/').pop().replace('.md', '')),
        escape(t.completato ? 'Completato' : 'Da Fare'),
    ].join(','));
    const csv = [header, ...rows].join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'reviewLavoro_export.csv';
    document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
};

// ============================================================
// 💅 STILE
// ============================================================
const injectStyle = (container) => {
    if (container.querySelector('style[data-rv]')) return;
    const style = container.createEl('style');
    style.setAttribute('data-rv', '1');
    style.textContent = `
        .rv-wrap { font-family: var(--font-interface); }

        /* Icons */
        .rv-wrap .fa-solid { font-size: 0.85em; }

        /* Toolbar */
        .rv-toolbar {
            display: flex; flex-wrap: wrap;
            gap: 8px; align-items: center; margin-bottom: 1rem;
        }
        .rv-search, .rv-add-input {
            padding: 5px 10px; border-radius: 6px;
            border: 1px solid var(--background-modifier-border);
            background: var(--background-primary);
            color: var(--text-normal); font-size: 0.85em;
        }
        .rv-search { flex: 1; min-width: 160px; }
        .rv-select, .rv-add-select {
            padding: 5px 8px; border-radius: 6px;
            border: 1px solid var(--background-modifier-border);
            background: var(--background-primary);
            color: var(--text-normal); font-size: 0.82em; cursor: pointer;
        }
        .rv-btn {
            display: inline-flex; align-items: center; gap: 5px;
            padding: 5px 12px; border-radius: 6px;
            border: 1px solid var(--background-modifier-border);
            background: var(--background-secondary);
            color: var(--text-muted); font-size: 0.82em;
            cursor: pointer; white-space: nowrap; transition: background 0.15s;
        }
        .rv-btn:hover { background: var(--background-modifier-hover); color: var(--text-normal); }
        .rv-btn.active {
            background: var(--color-accent);
            color: #fff; border-color: var(--color-accent);
        }

        /* Progress */
        .rv-progress-wrap {
            display: flex; align-items: center;
            gap: 10px; margin-bottom: 1rem;
        }
        .rv-progress-bar-bg {
            flex: 1; height: 6px; border-radius: 99px;
            background: var(--background-modifier-border); overflow: hidden;
        }
        .rv-progress-bar-fill {
            height: 100%; border-radius: 99px;
            background: var(--color-accent); transition: width 0.4s ease;
        }
        .rv-progress-label { font-size: 0.78em; color: var(--text-faint); white-space: nowrap; }

        /* Section heading */
        .rv-heading {
            display: flex; align-items: center; gap: 8px;
            margin: 1.2rem 0 0.4rem; font-size: 1em;
            font-weight: 600; color: var(--text-normal);
            cursor: pointer; user-select: none;
        }
        .rv-heading:hover { color: var(--color-accent); }
        .rv-chevron {
            font-size: 0.75em; transition: transform 0.2s;
            display: inline-flex; align-items: center;
        }
        .rv-chevron.collapsed { transform: rotate(-90deg); }
        .rv-count {
            font-size: 0.75em; padding: 1px 7px; border-radius: 99px;
            background: var(--background-secondary-alt);
            color: var(--text-muted); font-weight: 500;
        }
        .rv-status-icon { display: inline-flex; align-items: center; }
        .rv-status-icon.da-fare  { color: #e03131; }
        .rv-status-icon.completati { color: #2f9e44; }

        /* Collapsible */
        .rv-table-wrap {
            overflow: hidden; transition: max-height 0.3s ease, opacity 0.3s ease;
            max-height: 4000px; opacity: 1;
        }
        .rv-table-wrap.collapsed { max-height: 0; opacity: 0; }

        /* Table */
        .rv-table {
            width: 100%; border-collapse: collapse;
            font-size: 0.87em; margin-bottom: 0.5rem;
        }
        .rv-table thead th {
            background: var(--background-secondary);
            color: var(--text-muted); font-weight: 600;
            font-size: 0.75em; text-transform: uppercase;
            letter-spacing: 0.05em; padding: 8px 10px;
            text-align: left;
            border-bottom: 2px solid var(--background-modifier-border);
            white-space: nowrap; user-select: none;
        }
        .rv-table thead th.sortable { cursor: pointer; }
        .rv-table thead th.sortable:hover { color: var(--color-accent); }
        .rv-sort-icon { margin-left: 5px; opacity: 0.35; font-size: 0.8em; }
        .rv-sort-icon.active { opacity: 1; color: var(--color-accent); }
        .rv-table tbody tr {
            border-bottom: 1px solid var(--background-modifier-border);
            transition: background 0.12s;
        }
        .rv-table tbody tr:hover { background: var(--background-modifier-hover); }
        .rv-table td { padding: 7px 10px; vertical-align: middle; color: var(--text-normal); }
        .rv-table input[type="checkbox"] {
            width: 15px; height: 15px;
            cursor: pointer; accent-color: var(--color-accent);
        }

        /* Text */
        .rv-text { line-height: 1.4; }
        .rv-done { color: var(--text-faint); text-decoration: line-through; }

        /* Priority badge */
        .rv-priority {
            display: inline-flex; align-items: center; gap: 4px;
            font-size: 0.75em; padding: 2px 7px;
            border-radius: 99px; font-weight: 600; white-space: nowrap;
        }

        /* Ambito badge */
        .rv-badge {
            display: inline-block; padding: 2px 8px; border-radius: 99px;
            font-size: 0.75em; font-weight: 500;
            background: var(--background-secondary-alt); color: var(--text-muted);
        }

        /* Tag */
        .rv-tag {
            display: inline-flex; align-items: center; gap: 3px;
            padding: 1px 6px; border-radius: 99px;
            font-size: 0.72em; margin-right: 3px;
            background: var(--tag-background, var(--background-secondary-alt));
            color: var(--tag-color, var(--text-muted));
        }

        /* Deadline */
        .rv-deadline { font-size: 0.8em; white-space: nowrap; color: var(--text-faint); display: inline-flex; align-items: center; gap: 4px; }
        .rv-deadline.overdue { color: #e03131; font-weight: 600; }
        .rv-deadline.soon    { color: #f08c00; font-weight: 600; }

        /* Date */
        .rv-date { color: var(--text-faint); font-size: 0.8em; white-space: nowrap; }
        .rv-empty { color: var(--text-faint); font-style: italic; padding: 8px 0; font-size: 0.9em; }

        /* Link */
        .rv-link {
            display: inline-flex; align-items: center; gap: 5px;
            color: var(--color-accent); text-decoration: none; font-size: 0.83em;
        }
        .rv-link:hover { text-decoration: underline; }

        /* Group header */
        .rv-group-header {
            display: flex; align-items: center; gap: 6px;
            font-size: 0.83em; font-weight: 600; color: var(--text-muted);
            padding: 10px 0 4px;
            border-bottom: 1px solid var(--background-modifier-border);
        }

        /* Add task */
        .rv-add-wrap {
            display: flex; gap: 6px; margin-top: 0.5rem;
            margin-bottom: 0.2rem; flex-wrap: wrap; align-items: center;
        }
        .rv-add-input { flex: 1; min-width: 180px; }
        .rv-add-btn {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 5px 14px; border-radius: 6px;
            background: var(--color-accent); color: #fff;
            border: none; font-size: 0.85em;
            cursor: pointer; font-weight: 600;
        }
        .rv-add-btn:hover { opacity: 0.85; }

        /* Confirm uncheck */
        .rv-confirm-wrap { display: inline-flex; align-items: center; gap: 4px; }
        .rv-confirm-yes, .rv-confirm-no {
            display: inline-flex; align-items: center;
            font-size: 0.7em; padding: 2px 6px; border-radius: 4px;
            border: 1px solid var(--background-modifier-border);
            cursor: pointer; background: var(--background-secondary);
            color: var(--text-muted);
        }
        .rv-confirm-yes { color: #2f9e44; border-color: #2f9e44; }
        .rv-confirm-yes:hover { background: #2f9e44; color: #fff; }
        .rv-confirm-no:hover { background: var(--background-modifier-hover); }

        /* Footer */
        .rv-footer {
            display: flex; gap: 14px; align-items: center; flex-wrap: wrap;
            font-size: 0.76em; color: var(--text-faint);
            margin-top: 0.6rem; padding-top: 0.5rem;
            border-top: 1px solid var(--background-modifier-border);
        }
        .rv-footer-item { display: inline-flex; align-items: center; gap: 5px; }

        /* Exit animation */
        @keyframes rv-slideout { to { opacity: 0; transform: translateX(18px); } }
        .rv-row-exit { animation: rv-slideout 0.22s ease forwards; }
    `;
};

// ============================================================
// 🧠 STATO
// ============================================================
const state = {
    search:      '',
    sezFilter:   'Tutte',
    sortCol:     'data',
    sortDir:     'desc',
    collapsedDF: false,
    collapsedCO: false,
    groupByFile: false,
};

// ============================================================
// 🔢 FILTER & SORT
// ============================================================
const filterAndSort = (tasks) => {
    let result = tasks;
    if (state.search.trim()) {
        const q = state.search.toLowerCase();
        result = result.filter(t =>
            t.testo.toLowerCase().includes(q) ||
            t.sezione.toLowerCase().includes(q) ||
            t.tags.some(tag => tag.toLowerCase().includes(q))
        );
    }
    if (state.sezFilter !== 'Tutte') {
        result = result.filter(t => t.sezione === state.sezFilter);
    }
    result = [...result].sort((a, b) => {
        let va, vb;
        switch (state.sortCol) {
            case 'testo':    va = a.testo.toLowerCase(); vb = b.testo.toLowerCase(); break;
            case 'sezione':  va = a.sezione.toLowerCase(); vb = b.sezione.toLowerCase(); break;
            case 'priority': va = a.priority.val; vb = b.priority.val; break;
            case 'deadline': va = a.deadline ?? '9999'; vb = b.deadline ?? '9999'; break;
            default:         va = a.ordineData; vb = b.ordineData; break;
        }
        if (va < vb) return state.sortDir === 'asc' ? -1 : 1;
        if (va > vb) return state.sortDir === 'asc' ?  1 : -1;
        return 0;
    });
    return result;
};

// ============================================================
// 🖥️ RENDER
// ============================================================
const wrap = dv.container;
wrap.addClass('rv-wrap');
injectStyle(wrap);

const render = () => {
    const searchFocused = document.activeElement?.classList?.contains('rv-search');
    const addFocused    = document.activeElement?.classList?.contains('rv-add-input');

    wrap.querySelectorAll('.rv-dynamic').forEach(el => el.remove());

    const daFare     = filterAndSort(tuttiTask.filter(t => !t.completato));
    const completati = filterAndSort(tuttiTask.filter(t =>  t.completato));
    const totale     = tuttiTask.length;
    const nComp      = tuttiTask.filter(t => t.completato).length;
    const pct        = totale > 0 ? Math.round((nComp / totale) * 100) : 0;

    // ── TOOLBAR ──────────────────────────────────────────────
    const toolbar = wrap.createEl('div', { cls: 'rv-toolbar rv-dynamic' });

    // Search
    const searchWrap = toolbar.createEl('div');
    searchWrap.style.cssText = 'position:relative;flex:1;min-width:160px;display:flex;align-items:center;';
    const searchIcon = fa('magnifying-glass');
    searchIcon.style.cssText = 'position:absolute;left:9px;color:var(--text-faint);font-size:0.8em;';
    searchWrap.appendChild(searchIcon);
    const search = searchWrap.createEl('input', { cls: 'rv-search' });
    search.type = 'text'; search.placeholder = 'Cerca task, sezione, tag…';
    search.value = state.search; search.style.paddingLeft = '28px';
    search.addEventListener('input', e => { state.search = e.target.value; render(); });

    // Filtro sezione
    const selSez = toolbar.createEl('select', { cls: 'rv-select' });
    sezioniUniche.forEach(s => {
        const opt = selSez.createEl('option', { text: s });
        opt.value = s; opt.selected = s === state.sezFilter;
    });
    selSez.addEventListener('change', e => { state.sezFilter = e.target.value; render(); });

    // Bottone raggruppamento
    const btnGroup = toolbar.createEl('button', { cls: 'rv-btn' + (state.groupByFile ? ' active' : '') });
    btnGroup.appendChild(fa('folder-open')); btnGroup.append(' Per File');
    btnGroup.addEventListener('click', () => { state.groupByFile = !state.groupByFile; render(); });

    // Bottone export
    const btnExport = toolbar.createEl('button', { cls: 'rv-btn' });
    btnExport.style.marginLeft = 'auto';
    btnExport.appendChild(fa('file-csv')); btnExport.append(' CSV');
    btnExport.addEventListener('click', () => exportCSV(tuttiTask));

    // ── PROGRESS BAR ─────────────────────────────────────────
    const progWrap = wrap.createEl('div', { cls: 'rv-progress-wrap rv-dynamic' });
    const barIcon  = fa('chart-simple'); barIcon.style.color = 'var(--text-faint)';
    progWrap.appendChild(barIcon);
    const barFill = progWrap.createEl('div', { cls: 'rv-progress-bar-bg' })
                            .createEl('div', { cls: 'rv-progress-bar-fill' });
    barFill.style.width = pct + '%';
    progWrap.createEl('span', {
        text: `${nComp} / ${totale} completati (${pct}%)`,
        cls: 'rv-progress-label',
    });

    // ── COLONNE ───────────────────────────────────────────────
    const COLS = [
        { key: null,       label: ''           },
        { key: 'testo',    label: 'Obiettivo'  },
        { key: 'priority', label: 'Priorità'   },
        { key: 'sezione',  label: 'Ambito'     },
        { key: 'deadline', label: 'Scadenza'   },
        { key: 'data',     label: 'Data'       },
        { key: null,       label: 'Tag'        },
        { key: null,       label: 'File'       },
    ];

    const buildPlainTable = (container, tasks, isCompletati) => {
        const table = container.createEl('table', { cls: 'rv-table' });
        const hrow  = table.createEl('thead').createEl('tr');

        COLS.forEach(col => {
            const th = hrow.createEl('th', { text: col.label });
            if (col.key) {
                th.addClass('sortable');
                const sortIcon = fa(
                    col.key === state.sortCol
                        ? (state.sortDir === 'asc' ? 'sort-up' : 'sort-down')
                        : 'sort',
                    'rv-sort-icon' + (col.key === state.sortCol ? ' active' : '')
                );
                th.appendChild(sortIcon);
                th.addEventListener('click', () => {
                    state.sortDir = state.sortCol === col.key
                        ? (state.sortDir === 'asc' ? 'desc' : 'asc')
                        : 'asc';
                    state.sortCol = col.key;
                    render();
                });
            }
        });

        const tbody = table.createEl('tbody');

        tasks.forEach(task => {
            const row = tbody.createEl('tr');

            // ☑ Checkbox
            const tdCb = row.createEl('td');
            if (isCompletati) {
                const cbWrap = tdCb.createEl('div', { cls: 'rv-confirm-wrap' });
                const cb = cbWrap.createEl('input');
                cb.type = 'checkbox'; cb.checked = true;
                cb.addEventListener('change', () => {
                    cb.checked = true; cb.disabled = true;
                    const btnSi = cbWrap.createEl('span', { cls: 'rv-confirm-yes' });
                    btnSi.appendChild(fa('check')); btnSi.append(' Sì');
                    const btnNo = cbWrap.createEl('span', { cls: 'rv-confirm-no' });
                    btnNo.appendChild(fa('xmark'));
                    btnSi.addEventListener('click', () => {
                        row.addClass('rv-row-exit');
                        setTimeout(async () => { await toggleTask(task, false); render(); }, 230);
                    });
                    btnNo.addEventListener('click', () => {
                        cb.disabled = false; btnSi.remove(); btnNo.remove();
                    });
                });
            } else {
                const cb = tdCb.createEl('input');
                cb.type = 'checkbox'; cb.checked = false;
                cb.addEventListener('change', () => {
                    row.addClass('rv-row-exit');
                    setTimeout(async () => { await toggleTask(task, true); render(); }, 230);
                });
            }

            // Obiettivo
            row.createEl('td', {
                text: task.testo,
                cls: 'rv-text' + (isCompletati ? ' rv-done' : ''),
            });

            // Priorità
            const tdPri = row.createEl('td');
            if (task.priority.faIcon) {
                const badge = tdPri.createEl('span', { cls: 'rv-priority' });
                badge.appendChild(fa(task.priority.faIcon));
                badge.append(' ' + task.priority.label);
                badge.style.background = task.priority.color + '22';
                badge.style.color = task.priority.color;
            }

            // Ambito
            row.createEl('td').createEl('span', { text: task.sezione, cls: 'rv-badge' });

            // Scadenza
            const tdDl = row.createEl('td');
            if (task.deadline) {
                const today  = new Date(); today.setHours(0, 0, 0, 0);
                const diff   = Math.ceil((new Date(task.deadline) - today) / 86400000);
                let dlCls    = 'rv-deadline';
                if (!isCompletati) {
                    if (diff < 0)       dlCls += ' overdue';
                    else if (diff <= 3) dlCls += ' soon';
                }
                const dl = tdDl.createEl('span', { cls: dlCls });
                if (!isCompletati && diff < 0)  dl.appendChild(fa('triangle-exclamation'));
                else if (!isCompletati && diff <= 3) dl.appendChild(fa('clock'));
                else dl.appendChild(fa('calendar-day'));
                dl.append(' ' + task.deadline);
            } else {
                tdDl.createEl('span', { text: '—', cls: 'rv-date' });
            }

            // Data
            row.createEl('td', { text: String(task.data), cls: 'rv-date' });

            // Tag
            const tdTag = row.createEl('td');
            if (task.tags.length) {
                task.tags.forEach(tag => {
                    const span = tdTag.createEl('span', { cls: 'rv-tag' });
                    span.appendChild(fa('hashtag'));
                    span.append(tag.replace('#', ''));
                });
            } else {
                tdTag.createEl('span', { text: '—', cls: 'rv-date' });
            }

            // File
            const a = row.createEl('td').createEl('a', {
                cls: 'rv-link internal-link',
            });
            a.appendChild(fa('file-lines'));
            a.append(' ' + task.filePath.split('/').pop().replace('.md', ''));
            a.setAttribute('data-href', task.filePath);
            a.setAttribute('href', task.filePath);
            a.addEventListener('click', e => {
                e.preventDefault();
                app.workspace.openLinkText(task.filePath, '', false);
            });
        });
    };

    const buildTable = (container, tasks, isCompletati) => {
        if (tasks.length === 0) {
            const empty = container.createEl('p', { cls: 'rv-empty' });
            empty.appendChild(fa('inbox'));
            empty.append(' Nessun task.');
            return;
        }
        if (state.groupByFile) {
            const byFile = {};
            tasks.forEach(t => {
                const fname = t.filePath.split('/').pop().replace('.md', '');
                if (!byFile[fname]) byFile[fname] = [];
                byFile[fname].push(t);
            });
            Object.entries(byFile).forEach(([fname, group]) => {
                const gh = container.createEl('div', { cls: 'rv-group-header' });
                gh.appendChild(fa('folder'));
                gh.append(' ' + fname);
                buildPlainTable(container, group, isCompletati);
            });
        } else {
            buildPlainTable(container, tasks, isCompletati);
        }
    };

    // ── DA FARE ───────────────────────────────────────────────
    const h1 = wrap.createEl('div', { cls: 'rv-heading rv-dynamic' });
    const chv1 = h1.createEl('span', { cls: 'rv-chevron' + (state.collapsedDF ? ' collapsed' : '') });
    chv1.appendChild(fa('chevron-down'));
    const ico1 = h1.createEl('span', { cls: 'rv-status-icon da-fare' });
    ico1.appendChild(fa('circle-xmark'));
    h1.createSpan({ text: ' Da Fare' });
    h1.createSpan({ text: String(daFare.length), cls: 'rv-count' });
    h1.addEventListener('click', () => { state.collapsedDF = !state.collapsedDF; render(); });

    const wrapDF = wrap.createEl('div', {
        cls: 'rv-table-wrap rv-dynamic' + (state.collapsedDF ? ' collapsed' : ''),
    });
    buildTable(wrapDF, daFare, false);

    // ── ADD TASK ──────────────────────────────────────────────
    const addWrap  = wrap.createEl('div', { cls: 'rv-add-wrap rv-dynamic' });
    const addSel   = addWrap.createEl('select', { cls: 'rv-add-select' });
    pagine.forEach(p => {
        const opt = addSel.createEl('option', { text: p.file.name });
        opt.value = p.file.path;
    });
    const addInput = addWrap.createEl('input', { cls: 'rv-add-input' });
    addInput.type = 'text'; addInput.placeholder = 'Nuovo task…';
    const addBtn = addWrap.createEl('button', { cls: 'rv-add-btn' });
    addBtn.appendChild(fa('plus')); addBtn.append(' Aggiungi');
    const doAdd = async () => {
        const txt = addInput.value.trim();
        if (!txt) return;
        if (await addTask(addSel.value, txt)) addInput.value = '';
    };
    addBtn.addEventListener('click', doAdd);
    addInput.addEventListener('keydown', e => { if (e.key === 'Enter') doAdd(); });

    // ── COMPLETATI ────────────────────────────────────────────
    const h2 = wrap.createEl('div', { cls: 'rv-heading rv-dynamic' });
    const chv2 = h2.createEl('span', { cls: 'rv-chevron' + (state.collapsedCO ? ' collapsed' : '') });
    chv2.appendChild(fa('chevron-down'));
    const ico2 = h2.createEl('span', { cls: 'rv-status-icon completati' });
    ico2.appendChild(fa('circle-check'));
    h2.createSpan({ text: ' Completati' });
    h2.createSpan({ text: String(completati.length), cls: 'rv-count' });
    h2.addEventListener('click', () => { state.collapsedCO = !state.collapsedCO; render(); });

    const wrapCO = wrap.createEl('div', {
        cls: 'rv-table-wrap rv-dynamic' + (state.collapsedCO ? ' collapsed' : ''),
    });
    buildTable(wrapCO, completati, true);

    // ── FOOTER ────────────────────────────────────────────────
    const footer = wrap.createEl('div', { cls: 'rv-footer rv-dynamic' });

    const fi1 = footer.createEl('span', { cls: 'rv-footer-item' });
    fi1.appendChild(fa('folder-open')); fi1.append(` ${pagine.length} pagine`);

    const fi2 = footer.createEl('span', { cls: 'rv-footer-item' });
    fi2.appendChild(fa('list-check')); fi2.append(` ${totale} task`);

    const fi3 = footer.createEl('span', { cls: 'rv-footer-item' });
    fi3.appendChild(fa('circle-xmark')); fi3.style.color = '#e03131';
    fi3.append(` ${tuttiTask.filter(t => !t.completato).length} da fare`);

    const fi4 = footer.createEl('span', { cls: 'rv-footer-item' });
    fi4.appendChild(fa('circle-check')); fi4.style.color = '#2f9e44';
    fi4.append(` ${nComp} completati`);

    // Ripristina focus
    if (searchFocused) wrap.querySelector('.rv-search')?.focus();
    if (addFocused)    wrap.querySelector('.rv-add-input')?.focus();
};

render();
``````
---
