import pandas as pd
import re
import os

# --- CONFIGURAZIONE AMBIENTE ---
path = os.path.dirname(os.path.abspath(__file__))

FILE_REV = os.path.join(path, 'Revolut.csv')
FILE_N26 = os.path.join(path, 'N26.csv')
FILE_ALZ = os.path.join(path, 'Allianz.xls') 
FILE_MAP = os.path.join(path, 'Mapping_Categorie.xlsx')
# RITORNO AL CSV
OUTPUT   = os.path.join(path, 'Master_Finanze_Umberto.csv')

# 1. Caricamento Mapping
mapping = pd.read_excel(FILE_MAP).sort_values(by='Priorità')

def apply_mapping(desc, amount):
    desc_clean = " ".join(str(desc).split()).upper()
    for _, row in mapping.iterrows():
        pattern = str(row['Regex Pattern']).upper()
        if re.search(pattern, desc_clean):
            if any(x in pattern for x in ["TABACCHI", "AMOROSI", "GOLE"]):
                return ("Vizi", "Sigarette") if abs(amount) < 8 else ("Mangiare fuori", "Bar")
            return row['Categoria'], row['Sotto-Categoria']
    return "DA CATEGORIZZARE", "Altro"

# 2. Elaborazione Allianz
try:
    df_alz = pd.read_excel(FILE_ALZ, skiprows=3, engine='xlrd')
except Exception:
    df_alz = pd.read_csv(FILE_ALZ, skiprows=3, sep=',', on_bad_lines='skip', encoding='latin1')

df_alz['Importo'] = df_alz['Dare Euro'].fillna(0) + df_alz['Avere Euro'].fillna(0)
df_alz = df_alz[['Data Contabile', 'Descrizione', 'Importo']].copy()
df_alz.columns = ['Data', 'Descrizione', 'Importo']
df_alz['Conto'] = 'Allianz'

# 3. Elaborazione Revolut
df_rev = pd.read_csv(FILE_REV)
df_rev = df_rev[['Data di completamento', 'Descrizione', 'Importo']].copy()
df_rev.columns = ['Data', 'Descrizione', 'Importo']
df_rev['Conto'] = 'Revolut'

# 4. Elaborazione N26
df_n2 = pd.read_csv(FILE_N26)
df_n2['Descrizione'] = df_n2['Partner Name'].fillna('') + " " + df_n2['Payment Reference'].fillna('')
df_n2 = df_n2[['Booking Date', 'Descrizione', 'Amount (EUR)']].copy()
df_n2.columns = ['Data', 'Descrizione', 'Importo']
df_n2['Conto'] = 'N26'

# 5. Unione e Pulizia
df_master = pd.concat([df_rev, df_n2, df_alz], ignore_index=True)
df_master['Descrizione'] = df_master['Descrizione'].apply(lambda x: " ".join(str(x).split()))

# 6. Applicazione Mapping
df_master[['Categoria', 'Sotto_Cat']] = df_master.apply(
    lambda x: apply_mapping(x['Descrizione'], x['Importo']), axis=1, result_type='expand'
)

# 7. Export CSV (Standard IT: sep ; e decimal ,)
df_master.to_csv(OUTPUT, index=False, sep=';', decimal=',', encoding='utf-8-sig')

print(f"✅ Elaborazione completata! File CSV generato: {OUTPUT}")
