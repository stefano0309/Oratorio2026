
```bash
@echo off
:: Controlla i permessi di amministratore
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Permessi di amministratore rilevati.
) else (
    echo [ERRORE] Per favore, fai click destro sul file e seleziona "Esegui come amministratore".
    pause
    exit /b
)

echo ===================================================
echo   FASE 1: Installazione di Obsidian e Git
echo ===================================================
echo Installazione di Obsidian in corso...
winget install -e --id Obsidian.Obsidian --silent
echo [OK] Obsidian installato.

echo Installazione di Git in corso...
winget install -e --id Git.Git --silent
echo [OK] Git installato.
echo ---------------------------------------------------
echo.

echo ===================================================
echo   FASE 2: Creazione Profilo GitHub
echo ===================================================
echo Ora si aprira il browser per creare un account GitHub (se non lo hai gia).
echo Dopo esserti registrato, torna qui e premi un tasto.
timeout /t 3 >nul
start https://github.com/join
pause

echo.
set /p git_email="Inserisci l'indirizzo EMAIL che hai usato per GitHub: "
set /p git_name="Inserisci il tuo NOME UTENTE di GitHub: "

:: Configura Git localmente
"C:\Program Files\Git\bin\git.exe" config --global user.email "%git_email%"
"C:\Program Files\Git\bin\git.exe" config --global user.name "%git_name%"

echo [OK] Git configurato con i tuoi dati.
echo.

echo ===================================================
echo   FASE 3: Invio Email al Proprietario della Repo
echo ===================================================
echo Ora si aprira il tuo programma di posta per inviare la mail
echo a stefanodutto525@gmail.com. In questo modo potra aggiungerti alla repository.
echo.
timeout /t 2 >nul

:: Preparazione mailto con i dati dell'Oratorio2026
set "subject=Abilitazione Repository GitHub Oratorio2026"
set "body=Ciao, ho configurato l'ambiente. La mia mail di GitHub e: %git_email% (Nome utente: %git_name%). Puoi aggiungermi come collaboratore alla repository Oratorio2026?"

:: Sostituisce gli spazi con %%20 per il protocollo mailto
set "body=%body: =%%20%"
set "subject=%subject: =%%20%"

start mailto:stefanodutto525@gmail.com?subject=%subject%^&body=%body%

echo [INFO] Controlla la finestra della mail, inviala e attendi che il proprietario ti aggiunga.
echo Una volta che hai accettato l'invito su GitHub, torna qui e premi un tasto per clonare sul Desktop.
pause

echo.
echo ===================================================
echo   FASE 4: Clonazione della Repository sul Desktop
echo ===================================================
echo Spostamento sul Desktop...
cd /d "%USERPROFILE%\Desktop"

echo Clonazione della repository in corso...
"C:\Program Files\Git\bin\git.exe" clone https://github.com/stefano0309/Oratorio2026.git

echo.
echo ===================================================
echo   PROCESSO COMPLETATO!
echo ===================================================
echo Obsidian e Git sono installati.
echo La repository e stata clonata direttamente sul tuo Desktop.
echo.
pause
```