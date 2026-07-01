import os
import re
from pypdf import PdfReader

# --- 🎯 DIZIONARIO ESTESO E AUTOMATIZZATO DEI TAG ---
# Lo script cercherà queste parole (o le loro radici) nel testo e applicherà i rispettivi tag su Obsidian.
DIZIONARIO_TAGS = {
    # --- TIPOLOGIA DI GIOCO ---
    "tipo/squadre": ["squadra", "squadre", "fazioni", "gruppi", "fazione", "divisi in due"],
    "tipo/tutti_contro_tutti": ["tutti contro tutti", "singolo", "individuale"],
    "tipo/coppie": ["coppie", "coppia", "a due a due"],
    "tipo/cerchio": ["cerchio", "in cerchio", "seduti in cerchio", "girare in cerchio"],
    "tipo/staffetta": ["staffetta", "a turno", "in fila", "trenino", "colonna"],
    "tipo/acqua": ["acqua", "piscina", "gavettoni", "gavettone", "bagnato", "spugna", "spugne", "secchio", "secchi"],
    "tipo/notturno": ["notturno", "notte", "buio", "pila", "torcia", "torce", "lanterna"],
    
    # --- MECCANICHE DI GIOCO ---
    "meccanica/eliminazione": ["eliminato", "eliminati", "fuori gioco", "squalificato"],
    "meccanica/prigione": ["prigione", "prigioniero", "prigionieri", "liberato", "liberare", "tana"],
    "meccanica/punti": ["punteggio", "punti", "guadagna un punto", "classifica", "vince chi ha più"],
    "meccanica/indovinello": ["indovinare", "indovina", "mimo", "mimare", "quiz", "domanda", "domande", "enigma"],
    "meccanica/scambio_ruoli": ["lupo", "strega", "cacciatore", "toccato diventa", "infetto", "pesta"],

    # --- DINAMICHE E VALORI ---
    "tipo/corsa": ["correre", "corsa", "scatto", "velocità", "inseguire", "fuggire", "scappare", "rapido"],
    "tipo/forza": ["spingere", "tirare", "forza", "fune", "lotta", "sollevare"],
    "tipo/percezione": ["ascoltare", "silenzio", "rumore", "toccare", "percepire", "osservare", "guarda", "vista"],
    "tipo/logica": ["strategia", "astuzia", "pensare", "ragionare", "mente", "tattica", "logica", "memoria"],
    "tipo/cooperazione": ["collaborazione", "aiutarsi", "insieme", "fiducia", "mano nella mano", "cooperativo"],

    # --- MATERIALI COMUNI ---
    "materiale/palla": ["palla", "pallone", "pallina", "palle", "super santos", "palla medica"],
    "materiale/bende": ["bendato", "bendata", "bendati", "bende", "fazzoletto", "fazzoletti", "stoffa"],
    "materiale/cancelleria": ["carta", "fogli", "foglio", "penna", "penne", "pennarello", "pennarelli", "matita", "cartellone", "cartelloni"],
    "materiale/gessetti": ["gesso", "gessetti", "disegnare per terra"],
    "materiale/sedie": ["sedia", "sedie", "panchina", "panchine"],
    "materiale/cerchi": ["cerchio di plastica", "hula hoop", "cerchi"],
    "materiale/carte": ["carte da gioco", "mazzo", "carte"],
    "materiale/oggetti_casuali": ["scatola", "bottiglia", "bottiglie", "sasso", "sassi", "caramelle", "tesoro", "sacchetto", "sacchetti"],

    # --- RUOLI ---
    "ruolo/capogioco": ["capogioco", "animatore", "arbitro", "narratore", "responsabile"],
    "ruolo/capitano": ["capitano", "capisquadra", "caposquadra"],

    # --- SPAZIO DI GIOCO ---
    "spazio/aperto": ["all'aperto", "campo", "prato", "cortile", "bosco", "esterno"],
    "spazio/chiuso": ["al chiuso", "salone", "stanza", "corridoio", "interno", "palestra"]
}

def pulisci_testo_pdf(testo):
    testo = re.sub(r"C\.D\.V\s+NOVARA.*?\n", "", testo, flags=re.IGNORECASE | re.MULTILINE)
    testo = re.sub(r"ORATORIO DI GALLIATE.*?\n", "", testo, flags=re.IGNORECASE | re.MULTILINE)
    testo = re.sub(r"Il libro dei giochi.*?\n", "", testo, flags=re.IGNORECASE | re.MULTILINE)
    return testo

def estrai_testo_da_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    testo_completo = ""
    for page in reader.pages:
        testo_completo += page.extract_text() + "\n"
    return pulisci_testo_pdf(testo_completo)

def genera_note_con_tag_automatici(testo, output_dir="Note_Obsidian"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pattern_divisione = re.compile(r"(?=^Gioco\s+\d+\s*:)", re.MULTILINE | re.IGNORECASE)
    blocchi_grezzi = pattern_divisione.split(testo)
    blocchi_giochi = [b for b in blocchi_grezzi if re.match(r"^Gioco\s+\d+", b.strip(), re.IGNORECASE)]

    print(f"Giochi totali rilevati nel PDF: {len(blocchi_giochi)}")

    tag_da_cercare = [
        ("giocatori", r"N\.\s*giocatori\s*:\s*"),
        ("eta", r"Età\s*:\s*"),
        ("durata", r"Durata\s+media\s*:\s*"),
        ("tipo", r"Tipo\s+gioco\s*:\s*"),
        ("categoria", r"Categoria\s+scout\s*:\s*"),
        ("ambientazione", r"Ambientazione\s*:\s*"),
        ("materiale", r"Materiale\s+necessario\s*:\s*"),
        ("regole", r"Regole\s*:\s*"),
        ("vince_chi", r"Vince\s+chi\s*\.\.\.\s*"),
        ("valori", r"Valori\s+educativi\s*:\s*"),
    ]

    for blocco in blocchi_giochi:
        lines = blocco.splitlines()
        if not lines:
            continue

        titolo_grezzo = lines[0].strip()
        corpo_gioco = "\n".join(lines[1:])

        posizioni = []
        for chiave, pattern_str in tag_da_cercare:
            match = re.search(pattern_str, corpo_gioco, re.IGNORECASE)
            if match:
                posizioni.append({"chiave": chiave, "start_match": match.start(), "end_match": match.end()})

        posizioni.sort(key=lambda x: x["start_match"])
        dati_gioco = {chiave: "" for chiave, _ in tag_da_cercare}

        for i, pos in enumerate(posizioni):
            inizio_testo = pos["end_match"]
            fine_testo = posizioni[i + 1]["start_match"] if i + 1 < len(posizioni) else len(corpo_gioco)
            dati_gioco[pos["chiave"]] = corpo_gioco[inizio_testo:fine_testo].strip()

        # --- 🤖 AGGREGATORE INTELLIGENTE DEI TAG ---
        set_tags = {"gioco", "scout"}

        # 1. Normalizzazione Categoria Scout
        if dati_gioco["categoria"]:
            cat_tag = dati_gioco["categoria"].lower().replace("di ", "").replace("e ", "").strip()
            cat_tag = re.sub(r'\s+', '_', cat_tag)
            set_tags.add(f"categoria/{cat_tag}")

        # 2. Scansione testuale con barriere di parola (\b) per evitare errori di trigger
        testo_per_scansione = (titolo_grezzo + " " + dati_gioco["regole"] + " " + dati_gioco["materiale"] + " " + dati_gioco["tipo"]).lower()
        
        for tag_proposto, parole_chiave in DIZIONARIO_TAGS.items():
            for parola in parole_chiave:
                # Se la parola contiene spazi, la cerchiamo così com'è, altrimenti usiamo le barriere \b
                pattern_ricerca = rf"\b{re.escape(parola)}\b" if " " not in parola else re.escape(parola)
                if re.search(pattern_ricerca, testo_per_scansione):
                    set_tags.add(tag_proposto)

        # 3. Importazione dei valori educativi nativi del PDF
        if dati_gioco["valori"]:
            valori_puliti = dati_gioco["valori"].replace(" e ", ", ").replace(";", ",").split(",")
            for v in valori_puliti:
                v_clean = v.strip().lower().replace(" ", "_")
                if v_clean:
                    set_tags.add(f"valori/{v_clean}")

        # Nome file e scrittura markdown
        nome_file = re.sub(r'[\\/*?:"<>|]', "-", titolo_grezzo) + ".md"
        filepath = os.path.join(output_dir, nome_file)

        frontmatter = "---\n"
        frontmatter += "tags:\n"
        for t in sorted(list(set_tags)):
            frontmatter += f"  - {t}\n"
        
        if dati_gioco["categoria"]: frontmatter += f'categoria: "{dati_gioco["categoria"]}"\n'
        if dati_gioco["eta"]:       frontmatter += f'eta: "{dati_gioco["eta"]}"\n'
        frontmatter += "---\n"

        markdown_content = f"{frontmatter}# {titolo_grezzo}\n\n"
        markdown_content += "## 📋 Informazioni Generali\n"
        if dati_gioco["giocatori"]: markdown_content += f"- **N. Giocatori:** {dati_gioco['giocatori']}\n"
        if dati_gioco["eta"]:       markdown_content += f"- **Età:** {dati_gioco['eta']}\n"
        if dati_gioco["durata"]:    markdown_content += f"- **Durata Media:** {dati_gioco['durata']}\n"
        if dati_gioco["tipo"]:      markdown_content += f"- **Tipo Gioco:** {dati_gioco['tipo']}\n"
        if dati_gioco["categoria"]: markdown_content += f"- **Categoria Scout:** {dati_gioco['categoria']}\n"

        if dati_gioco["ambientazione"]: markdown_content += f"\n## 🌊 Ambientazione\n{dati_gioco['ambientazione']}\n"
        if dati_gioco["materiale"]:     markdown_content += f"\n## 🎒 Materiale Necessario\n{dati_gioco['materiale']}\n"
        if dati_gioco["regole"]:        markdown_content += f"\n## 📜 Regole e Svolgimento\n{dati_gioco['regole']}\n"
        if dati_gioco["vince_chi"]:     markdown_content += f"\n## 🏆 Condizione di Vittoria\n**Vince chi...** {dati_gioco['vince_chi']}\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)

    print(f"[COMPLETATO] Generati {len(blocchi_giochi)} file .md super-taggati in '{output_dir}'.")

if __name__ == "__main__":
    file_pdf_target = "Libro.pdf"
    if os.path.exists(file_pdf_target):
        testo_pdf = estrai_testo_da_pdf(file_pdf_target)
        genera_note_con_tag_automatici(testo_pdf)
    else:
        print(f"Errore: Il file '{file_pdf_target}' non è stato trovato.")