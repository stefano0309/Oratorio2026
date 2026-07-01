---
obsidianUIMode: preview
---
 ```dataviewjs
// ============================================================
// 🎯 ARCHIVIO GIOCHI IBRIDO — DataviewJS Dashboard Avanzata
// ============================================================
const TAG_BASE = "#gioco";

// ── Font Awesome ──────────────────────────────────────────
const injectFA = () => {
    const id = 'fa-cdn-games-v3';
    if (document.getElementById(id)) return;
    const link = document.createElement('link');
    link.id = id; link.rel = 'stylesheet';
    link.href = '[https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css](https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css)';
    document.head.appendChild(link);
};
injectFA();

const fa = (name, cls = '') => {
    const i = document.createElement('i');
    i.className = `fa-solid fa-${name}${cls ? ' ' + cls : ''}`;
    return i;
};

// ── Stile CSS Personalizzato ──────────────────────────────
const injectStyle = (c) => {
    if (c.querySelector('style[data-games-v3]')) return;
    const s = c.createEl('style');
    s.setAttribute('data-games-v3', '1');
    s.textContent = `
    .gm-wrap { font-family: var(--font-interface); }

    .gm-header { display:flex; align-items:center; gap:12px; margin-bottom:1.2rem; }
    .gm-header-icon {
        width:42px; height:42px; border-radius:10px;
        background:color-mix(in srgb, var(--color-accent) 15%, transparent);
        display:flex; align-items:center; justify-content:center;
        color:var(--color-accent); font-size:1.2em;
    }
    .gm-header-title { font-weight:700; font-size:1.2em; color:var(--text-normal); }
    .gm-header-sub   { font-size:0.8em; color:var(--text-faint); }

    /* Contenitore Filtri Avanzati */
    .gm-filter-section { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--background-modifier-border); }
    .gm-filter-group { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 0.6rem; align-items: center; }
    .gm-filter-label { font-size: 0.72em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-faint); min-width: 100px; }
    
    .gm-filter {
        padding:3px 10px; border-radius:99px;
        border:1px solid var(--background-modifier-border);
        background:var(--background-secondary);
        color:var(--text-muted); font-size:0.75em; font-weight:500;
        cursor:pointer; transition:all 0.15s;
    }
    .gm-filter:hover { color:var(--text-normal); background:var(--background-modifier-hover); }
    .gm-filter.active { background:var(--color-accent); color:#fff; border-color:var(--color-accent); }

    /* Griglia delle schede gioco */
    .gm-grid {
        display:grid;
        grid-template-columns:repeat(auto-fill, minmax(260px, 1fr));
        gap:12px; margin-bottom:1.2rem;
    }

    .gm-card {
        border-radius:10px;
        border:1px solid var(--background-modifier-border);
        background:var(--background-primary);
        display:flex; flex-direction:column;
        overflow:hidden;
        transition: transform 0.15s ease, border-color 0.15s ease;
        animation: gm-in 0.2s ease;
    }
    .gm-card:hover {
        border-color: var(--color-accent);
        transform: translateY(-2px);
    }
    
    .gm-card-head {
        padding:12px 14px 8px;
        background:var(--background-secondary);
        border-bottom:1px solid var(--background-modifier-border);
    }
    .gm-card-title { font-weight:600; font-size:0.95em; line-height:1.3; }
    .gm-card-title a { color:var(--text-normal) !important; text-decoration:none !important; }
    .gm-card-title a:hover { color:var(--color-accent) !important; }

    .gm-card-body { padding:12px 14px; flex:1; display:flex; flex-direction:column; gap:8px; }

    .gm-meta-row { display:flex; align-items:center; gap:6px; font-size:0.8em; color:var(--text-muted); }
    .gm-meta-row i { color:var(--text-faint); width:14px; text-align:center; font-size:0.9em; }
    .gm-meta-val { color:var(--text-normal); font-weight:500; }
    .gm-meta-hybrid { font-style: italic; color: var(--text-faint); font-size: 0.78em; }

    /* Mini contenitore tag interni alla card */
    .gm-card-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: auto; padding-top: 6px; }
    .gm-mini-tag {
        font-size: 0.65em; padding: 1px 6px; border-radius: 4px;
        background: var(--background-secondary-alt); color: var(--text-muted);
        border: 1px solid var(--background-modifier-border);
    }

    /* Statistiche */
    .gm-stats {
        display:flex; gap:16px; flex-wrap:wrap;
        font-size:0.78em; color:var(--text-faint);
        padding-top:0.8rem;
        border-top:1px solid var(--background-modifier-border);
    }
    .gm-stat { display:flex; align-items:center; gap:6px; }

    @keyframes gm-in { from { opacity:0; transform:translateY(6px); } to { opacity:1; } }
    `;
};

// ── MAIN ──────────────────────────────────────────────────
const wrap = dv.container;
wrap.addClass('gm-wrap');
injectStyle(wrap);

const main = async () => {
    // Carichiamo tutte le note contenenti il tag base #gioco
    const pagine = dv.pages(TAG_BASE).sort(p => p.file.name, 'asc');

    if (!pagine.length) {
        const e = wrap.createEl('p');
        e.style.cssText = 'color:var(--text-faint);font-style:italic;';
        e.appendChild(fa('inbox')); e.append(' Nessun gioco trovato nell\'archivio.');
        return;
    }

    // Struttura ad albero dei tag estratti per generare i bottoni filtri
    const tagSelezionati = { categoria: new Set(), tipo: new Set(), materiale: new Set(), meccanica: new Set(), valori: new Set() };
    
    const listaGiochi = pagine.map(p => {
        const tagsDellaNota = p.file.tags || [];
        const tagsSpecifici = [];

        tagsDellaNota.forEach(t => {
            const tagPulito = t.replace('#', '');
            // Evitiamo tag ridondanti o macro-tag globali
            if (tagPulito === 'gioco' || tagPulito === 'scout') return;

            tagsSpecifici.push(tagPulito);

            // Catalogazione automatica nei gruppi filtri
            if (tagPulito.startsWith('categoria/')) tagSelezionati.categoria.add(tagPulito);
            else if (tagPulito.startsWith('tipo/'))       tagSelezionati.tipo.add(tagPulito);
            else if (tagPulito.startsWith('materiale/'))  tagSelezionati.materiale.add(tagPulito);
            else if (tagPulito.startsWith('meccanica/'))  tagSelezionati.meccanica.add(tagPulito);
            else if (tagPulito.startsWith('valori/'))     tagSelezionati.valori.add(tagPulito);
        });

        // Controlliamo se la nota appartiene alla seconda parte (senza "eta" esplicito nell'intestazione frontmatter)
        const eIbrido = !p.eta;

        return {
            page: p,
            displayName: p.file.name.replace(/^Gioco\s+\d+\s*:\s*/i, ''),
            path: p.file.path,
            eta: p.eta || null,
            categoria: p.categoria || null,
            tags: tagsSpecifici,
            isHybrid: eIbrido
        };
    });

    // Inizializzazione dello stato dei filtri globale
    if (!window.gm_filtro_attivo) window.gm_filtro_attivo = 'Tutti';

    const render = () => {
        // Pulizia degli elementi dinamici delle precedenti istanze di rendering
        wrap.querySelectorAll('.gm-dyn').forEach(el => el.remove());

        // ── FILTRI DINAMICI SULL'ALBERO DEI TAG ─────────
        const filterSection = wrap.createEl('div', { cls: 'gm-filter-section gm-dyn' });
        
        // Riga di comando generale (Reset)
        const mainGroup = filterSection.createEl('div', { cls: 'gm-filter-group' });
        mainGroup.createEl('span', { text: 'Generale:', cls: 'gm-filter-label' });
        const btnTutti = mainGroup.createEl('button', {
            text: 'Mostra Tutto',
            cls: 'gm-filter' + (window.gm_filtro_attivo === 'Tutti' ? ' active' : '')
        });
        btnTutti.addEventListener('click', () => { window.gm_filtro_attivo = 'Tutti'; render(); });

        // Funzione helper per iniettare le righe di bottoni-filtro
        const creaRigaFiltro = (labelText, setTags) => {
            if (setTags.size === 0) return;
            const riga = filterSection.createEl('div', { cls: 'gm-filter-group' });
            riga.createEl('span', { text: labelText, cls: 'gm-filter-label' });
            
            Array.from(setTags).sort().forEach(t => {
                const labelBottone = t.split('/')[1].replace(/_/g, ' ');
                const btn = riga.createEl('button', {
                    text: labelBottone,
                    cls: 'gm-filter' + (window.gm_filtro_attivo === t ? ' active' : '')
                });
                btn.addEventListener('click', () => { window.gm_filtro_attivo = t; render(); });
            });
        };

        creaRigaFiltro('Categorie:', tagSelezionati.categoria);
        creaRigaFiltro('Tipologie:', tagSelezionati.tipo);
        creaRigaFiltro('Materiali:', tagSelezionati.materiale);
        creaRigaFiltro('Meccaniche:', tagSelezionati.meccanica);
        creaRigaFiltro('Valori:', tagSelezionati.valori);

        // ── INTESTAZIONE DELLA DASHBOARD ──────────────────
        const hdr = wrap.createEl('div', { cls: 'gm-header gm-dyn' });
        const ico = hdr.createEl('div', { cls: 'gm-header-icon' });
        ico.appendChild(fa('cubes'));
        const ht = hdr.createEl('div');
        ht.createEl('div', { text: 'Archivio Giochi Integrato', cls: 'gm-header-title' });
        ht.createEl('div', { 
            text: `Filtro attivo: ${window.gm_filtro_attivo === 'Tutti' ? 'Nessuno' : window.gm_filtro_attivo.replace(/_/g, ' ')}`, 
            cls: 'gm-header-sub' 
        });

        // ── RENDERING DELLE SCHEDE (GRIGLIA) ─────────────
        const grid = wrap.createEl('div', { cls: 'gm-grid gm-dyn' });
        
        // Esecuzione del filtro attivo
        const giochiFiltrati = listaGiochi.filter(g => 
            window.gm_filtro_attivo === 'Tutti' || g.tags.includes(window.gm_filtro_attivo)
        );

        giochiFiltrati.forEach(g => {
            const card = grid.createEl('div', { cls: 'gm-card' });

            // Titolo della Card con Link di Obsidian integrato
            const ch = card.createEl('div', { cls: 'gm-card-head' });
            const titleSpan = ch.createEl('div', { cls: 'gm-card-title' });
            const linkEl = titleSpan.createEl('a', { text: g.displayName, cls: 'internal-link' });
            linkEl.setAttribute('data-href', g.path);
            linkEl.setAttribute('href', g.path);

            // Corpo della Card
            const body = card.createEl('div', { cls: 'gm-card-body' });
            
            if (!g.isHybrid) {
                // Layout per i Giochi 1-98 (Strutturati con metadati espliciti)
                const r1 = body.createEl('div', { cls: 'gm-meta-row' });
                r1.appendChild(fa('child'));
                r1.createEl('span', { text: 'Età: ' });
                r1.createEl('span', { text: g.eta, cls: 'gm-meta-val' });
            } else {
                // Layout adattivo per i Giochi 99+ (Testo continuo)
                const rHybrid = body.createEl('div', { cls: 'gm-meta-row gm-meta-hybrid' });
                rHybrid.appendChild(fa('file-lines'));
                rHybrid.createEl('span', { text: 'Nota a testo continuo' });
            }

            // Iniezione automatica dei tag della card (estratti dal testo via Python)
            if (g.tags.length > 0) {
                const tagsContainer = body.createEl('div', { cls: 'gm-card-tags' });
                g.tags.forEach(t => {
                    const parti = t.split('/');
                    const nomeTagBreve = parti[1] ? parti[1].replace(/_/g, ' ') : parti[0];
                    tagsContainer.createEl('span', { text: nomeTagBreve, cls: 'gm-mini-tag' });
                });
            }
        });

        // ── FOOTER DELLE STATISTICHE ─────────────────────
        const stats = wrap.createEl('div', { cls: 'gm-stats gm-dyn' });
        
        const s1 = stats.createEl('span', { cls: 'gm-stat' });
        s1.appendChild(fa('database')); 
        s1.append(` ${listaGiochi.length} giochi caricati`);

        const s2 = stats.createEl('span', { cls: 'gm-stat' });
        s2.appendChild(fa('filter')); 
        s2.append(` ${giochiFiltrati.length} mostrati dal filtro`);
    };

    render();
};

main();
```