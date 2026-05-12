# IVECO Statistics

Framework Python/PySpark per rifattorizzare la pipeline legacy notebook-based delle statistiche truck IVECO.

L'obiettivo e' tenere Databricks per l'accesso ai dati completi e usare lo sviluppo locale su un sample Parquet esportato dalla fat table. Il codice modulare puo' poi essere pushato su GitHub e rilanciato da Databricks Repos.

## Struttura

- `engine_loader.py`: lettura fat table/sample e metadata reali dalle righe.
- `engine_config.py`: registry centrale di sheet, colonne e priorita' Series > Group > fallback.
- `engine_cleaning.py`: pulizia colonne, dedup ultimo record per VIN, feature legacy del Prep.
- `engine_stats.py`: percentuali, soglie, pivot e conversione Pandas.
- `engine_utils.py`: log, dimensioni, timestamp e naming.
- `run_local_sample.py`: runner locale da terminale o VS Code debug.
- `Main_pipeline_modular.ipynb`: notebook orchestratore con preview degli sheet prima dell'export.
- `export_config_csv.py`: export Databricks del sample grezzo.
- `Old_statistics/`: riferimento legacy dei notebook/script originali.

## Setup Locale

Prerequisiti Windows gia' attesi:

- Python 3.12
- Java JDK 17
- `HADOOP_HOME=C:\hadoop`
- `winutils.exe` in `C:\hadoop\bin`

Installa le dipendenze:

```powershell
python -m pip install -r requirements.txt
```

In VS Code installa le estensioni consigliate quando compaiono:

- Python
- Jupyter

Poi apri `Main_pipeline_modular.ipynb` e seleziona il kernel Python dell'ambiente in cui hai installato i pacchetti.

## Sample Dati

Il sample locale atteso e':

```text
data/sample/Subset_Config_399_Date_20260511_123241
```

Queste cartelle restano fuori da Git:

```text
data/sample/
data/output/
```

## Run Locale

Validazione senza Excel:

```powershell
python -m run_local_sample --no-excel
```

Run con export Excel:

```powershell
python -m run_local_sample
```

Output:

```text
Excel_statistics/local_sample_statistics.xlsx
```

## Run Su Databricks

Nel cluster cliente non serve il sample locale. `Main_pipeline_modular.ipynb`
rileva Databricks tramite `dbutils` e crea widget modificabili:

```python
input_mode  # default: "fat_table"
config      # default: "399"; accetta anche "399,400"
output_dir  # default: "Excel_statistics"
```

Gli Excel generati vengono salvati nella cartella `Excel_statistics/`.
I file `.xlsx` sono ignorati da Git, quindi puoi scaricarli quando vuoi senza
committare dati/output pesanti nella repo.

Per testare da notebook/driver Databricks con pochi sheet:

```python
sheet_ids = ["complete_dataset", "fuel_consumption", "1a", "1a_2"]
```

Da terminale/job Python:

```bash
python -m run_local_sample --input-mode fat_table --config 399
```

Per non deduplicare il sample per VIN:

```powershell
python -m run_local_sample --keep-all-updates
```

Per lanciare solo alcuni sheet:

```powershell
python -m run_local_sample --sheets fuel_consumption 2a 5a_dpf
```

Se `python` non e' nel PATH, usa l'interprete configurato in VS Code:

```powershell
C:\Users\g.cornacchia\AppData\Local\Python\bin\python.exe -m run_local_sample --no-excel
```

## Notebook Modulare

`Main_pipeline_modular.ipynb` e' il punto di controllo visuale:

1. legge il sample,
2. pulisce i nomi colonna,
3. tiene l'ultimo record per VIN,
4. ricrea feature del vecchio Prep (`engine_model`, range velocita, range mileage, mission),
5. valida le colonne configurate,
6. mostra le pivot sheet per sheet,
7. esporta l'Excel.

Gli sheet sono configurati in `engine_config.py`; il notebook non deve contenere liste hardcoded.
La lista default contiene 58 sheet configurati, incluso `Complete Dataset`, piu' i fogli duplicati legacy come `1a_2`, `1c_2`, `3e_2`, `4c_2` e `5a_dpf_2`.

## Note Di Migrazione

- `Old_statistics/Threshold_old.py` e' tenuto come riferimento legacy/inventory.
- Gli export legacy pesanti in `Old_statistics/` sono esclusi dall'analisi Python di VS Code: contengono magic Databricks (`%run`, `%matplotlib`, `pip install`) e quindi non sono validi script locali.
- Le regole nuove vanno spostate nel modulo giusto, non incollate nel notebook.
- Se uno sheet legacy non appare, prima controlla `engine_config.py` e poi la presenza colonne nel sample.
- Le statistiche trattano esplicitamente gli zeri/null quando lo sheet lo richiede (`zero_as_null`).

## Git

Prima del commit verifica:

```powershell
git status
python -m run_local_sample --no-excel
```

Commit solo codice/config/notebook/documentazione. Non aggiungere sample o output Excel.
