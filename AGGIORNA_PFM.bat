@echo off
cd /d "C:\PFM_Uelleci"

echo [1/3] Esecuzione Script Python...
python governance_finanziaria.py

echo [2/3] Preparazione file per GitHub...
:: Aggiungiamo tutto (anche il .bat stesso) per essere sicuri
git add .
:: Il comando commit fallirebbe se non ci sono modifiche, quindi usiamo un trucco
git commit -m "Update automatico %date% %time%" || echo Nessuna modifica rilevata.

echo [3/3] Caricamento su GitHub...
git push origin main

echo ✅ Procedura terminata!
pause