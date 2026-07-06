import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURAZIONE ---
VAULT_PATH = os.path.expanduser("/Users/stefanodutto/Documents/EstateRagazzi/Note_Obsidian")
SIMILARITY_THRESHOLD = 0.75
print("1/4 Caricamento del modello di Embedding locale (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def pulisci_vecchi_suggerimenti(contenuto):
    """Rimuove la vecchia sezione dei suggerimenti generata nei blocchi precedenti"""
    # Rimuove tutto ciò che parte da '---' seguito dalla sezione dei collegamenti IA fino alla fine del file
    pattern = r'\n\n---\n## 🧠 Collegamenti Suggeriti dall\'IA.*$'
    return re.sub(pattern, '', contenuto, flags=re.DOTALL)

def carica_e_pulisci_note(vault_path):
    """Legge le note, rimuove i vecchi tag IA e restituisce il contenuto pulito"""
    note_files = {}
    for root, dirs, files in os.walk(vault_path):
        if '.obsidian' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Sgancia i vecchi suggerimenti se presenti prima di calcolare i nuovi
                content_pulito = pulisci_vecchi_suggerimenti(content)
                
                # Se il file conteneva vecchi suggerimenti, lo sovrascriviamo pulito temporaneamente
                if content_pulito != content:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content_pulito)
                
                # Rimuove il frontmatter solo per l'analisi del modello IA
                content_per_embedding = re.sub(r'^---.*?---', '', content_pulito, flags=re.DOTALL)
                
                note_files[file] = {
                    "path": full_path,
                    "content": content_per_embedding.strip(),
                    "raw_content": content_pulito
                }
    return note_files

def trova_note_orfane(note_files):
    """Trova le note orfane basandosi sul contenuto appena ripulito"""
    link_pattern = re.compile(r'\[\[(.*?)\]\]')
    tutti_i_link = set()
    note_con_link_uscita = set()

    for nome_nota, dati in note_files.items():
        links = link_pattern.findall(dati['content'])
        if links:
            note_con_link_uscita.add(nome_nota)
            for link in links:
                nome_pulito = link.split('|')[0].strip()
                if not nome_pulito.endswith('.md'):
                    nome_pulito += '.md'
                tutti_i_link.add(nome_pulito)

    orfane = []
    for nome_nota in note_files.keys():
        if nome_nota not in note_con_link_uscita and nome_nota not in tutti_i_link:
            orfane.append(nome_nota)
            
    return orfane

def main():
    # Carica le note e resetta i vecchi collegamenti IA
    note = carica_e_pulisci_note(VAULT_PATH)
    if not note:
        print(f"[ERRORE] Nessuna nota trovata nel percorso: {VAULT_PATH}")
        return

    print(f"2/4 Trovate {len(note)} note totali. Vecchi blocchi IA resettati.")
    
    # Ricalcola le orfane reali adesso che i vecchi link IA sono spariti
    note_orfane = trova_note_orfane(note)
    print(f"3/4 Rilevate {len(note_orfane)} note orfane reali.")

    if not note_orfane:
        print("\n[OK] Nessuna nota orfana rilevata dopo il reset iniziale!")
        return

    nomi_note = list(note.keys())
    testi_note = [dati['content'] if dati['content'] else dati['path'] for dati in note.values()]
    
    print("4/4 Elaborazione IA delle nuove affinità di contenuto...")
    embeddings = model.encode(testi_note, show_progress_bar=False)
    sim_matrix = cosine_similarity(embeddings)

    print("\n=======================================================")
    print("    AGGIORNAMENTO SEZIONE COLLEGAMENTI (REINTEGRAZIONE)")
    print("=======================================================\n")

    modificate = 0
    for orfana in note_orfane:
        idx_orfana = nomi_note.index(orfana)
        percorso_orfana = note[orfana]['path']
        
        suggerimenti = []
        prossimita_idx = np.argsort(sim_matrix[idx_orfana])[::-1]
        
        for idx in prossimita_idx:
            if idx == idx_orfana:
                continue
                
            punteggio = sim_matrix[idx_orfana][idx]
            if punteggio < SIMILARITY_THRESHOLD:
                break
                
            nome_suggerito = nomi_note[idx].replace('.md', '')
            suggerimenti.append(f"- [[{nome_suggerito}]] (Affinità: {int(punteggio * 100)}%)")
            
        if suggerimenti:
            print(f"🔄 Sezione rigenerata per: [{orfana}] -> {len(suggerimenti)} nuovi link.")
            
            with open(percorso_orfana, 'a', encoding='utf-8') as f:
                f.write("\n\n---")
                f.write("\n## 🧠 Collegamenti Suggeriti dall'IA\n")
                for sug in suggerimenti:
                    f.write(f"{sug}\n")
            modificate += 1

    print("\n=======================================================")
    print(f" AGGIORNAMENTO COMPLETATO: {modificate} sezioni aggiornate.")
    print("=======================================================")

if __name__ == "__main__":
    main()