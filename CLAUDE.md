# Contesto del Progetto

- **Scopo**: rifattorizzare e mantenere pipeline statistiche IVECO nate da notebook legacy, con sviluppo locale su sample Parquet e rilancio su Databricks/Repos.
- **Stack**: Python 3.12, PySpark, Pandas, openpyxl/XlsxWriter, notebook Jupyter, Databricks/Unity Catalog.
- **Output principali**: file Excel in `Excel_statistics/`; sample e output dati restano fuori da Git.
- **Struttura cartelle**:
  - `engine_loader.py`: lettura sample/fat table, mapping config -> tabelle, metadata, nomi export.
  - `engine_config.py`: registry centrale degli sheet Mission Test, colonne, alias, trigger, layout Series > Group > fallback.
  - `engine_cleaning.py`: pulizia nomi colonna, dedup ultimo record per VIN, feature legacy Prep, rinomina ufficiale.
  - `engine_stats.py`: percentuali, soglie, pivot PySpark e conversione Pandas.
  - `engine_utils.py`: log, dimensioni, timestamp e helper.
  - `run_local_sample.py`: runner locale Mission Test e funzioni export Excel riusabili.
  - `vodr_config.py` / `vodr_pipeline.py`: configurazione e pipeline VODR, incluse soglie e join opzionale Mission Test.
  - `Main_pipeline_modular.ipynb`: orchestratore Mission Test.
  - `Main_pipeline_Vodr.ipynb`: orchestratore VODR.
  - `tests/`: test unitari su mapping config, layout colonne, nomi export e parsing widget.
  - `Old_statistics/`: riferimento legacy, non fonte da eseguire localmente.

## Decisioni Architetturali

- I notebook devono orchestrare; la logica va nei moduli Python.
- Le liste hardcoded di sheet/colonne devono stare in `engine_config.py` o `vodr_config.py`, non nei notebook.
- `get_table_path()` centralizza il routing delle config verso Unity Catalog o tabelle legacy.
- Per Mission Test nuove config `399,400,401,402,405,406,408,409` si usa `u_truck_analyzer_p.mission_test_statistics.fat_table_<config>`.
- Per VODR config `33,49,50,51,52,53,54,56` si usa `u_truck_analyzer_p.vodr_statistics.fat_table_<config>`.
- Il fallback legacy resta presente per config vecchie, ma va trattato con cautela.
- La priorita' per le colonne Mission Test e' Series > Group > fallback generico.
- VODR puo' arricchire con Mission Test tramite join su `vin`; in locale normalmente si lavora su sample.
- Gli Excel sono output generati e non vanno committati.

## Pattern Comuni

- Normalizzare nomi colonna Spark con `clean_spark_column_names()` prima di usare variabili tecniche.
- Se serve un record per VIN, usare `keep_latest_record_per_vin()` e indicare chiaramente quando invece mantenere tutti gli update.
- Ricreare feature legacy con `add_legacy_preparation_features()` invece di duplicare logica nei notebook.
- Per statistiche/pivot usare `report_pivot_pyspark_fixed()`; il nome storico `report_pivot_pyspark()` delega alla versione robusta.
- Per percentuali di gruppi di colonne usare `pyspark_variabili_x()`.
- Per sheet Mission Test usare `get_columns_for_sheet()`, `get_sheet_name_for_context()`, `get_sheet_settings()` e `get_default_sheet_ids()`.
- Per VODR usare `get_vodr_report_sheets()`, `get_vodr_percentage_groups()` e `parse_config_text()`.
- Prima di toccare la pipeline VODR su una nuova config, verificare: presenza di `Average_vehicle_speed`/`mileage` o `cov_div_len` nella fat table, e che `VODR_TO_MT_CONFIGS` abbia un mapping dedicato che agganci i VIN della config; in caso contrario `mission`/`mileage_range` resteranno NULL e tutti gli sheet con quei `group_by` saranno vuoti.
- Per debug sheet vuoti VODR, usare la cella `diagnose_vodr_empty_sheets(df_time_percentage, config)` in fondo a `Main_pipeline_Vodr.ipynb`: stampa stato colonne sorgente, stato join MT e motivi del vuoto sheet per sheet.
- Per export Excel riusare `export_excel_outputs()` e `prepare_excel_dataframe()` da `run_local_sample.py`.
- Aggiungere test mirati in `tests/` quando si toccano mapping config, nomi export, sheet, parser o ordinamenti Excel.

## Pitfalls Da Evitare

- Non committare `data/sample/`, `data/output/`, `.xlsx`, cache o file pesanti esportati.
- Non mettere nuove regole nel notebook se possono stare in un modulo Python.
- Non assumere che config < 100 siano tutte VODR legacy: alcune VODR ora passano da Unity Catalog.
- Non perdere la distinzione fra Mission Test e VODR: hanno config, nomi file e sheet diversi.
- Non deduplicare per VIN quando il confronto legacy richiede righe raw; per config 399 il README segnala differenze attese tra raw e latest VIN.
- Non rinominare colonne ufficiali con stringhe ad hoc: usare dizionari/mapping esistenti.
- Non ignorare i vincoli Excel: nomi sheet, limite righe e ordinamento categorie sono gestiti nel runner.
- Per i nomi sheet e item Mission Test, la fonte e' il catalogo `Table Name / Item Name / Variable Name`; abbreviare i `Table Name` oltre 31 caratteri ma mantenere numero e significato.
- Ordinare sempre `mileage_range`, `mileage_split`, `mission` e range velocita' con gli ordini business, non lessicografici.
- Per Mission Test: `4e` e' Urea Deposit accumulation, `4f` e' AdBlue pressure pump, `4g/4h/4i` sono percentuali, `5c` usa advice/alert sottrattivi.
- Non usare i vecchi Excel locali come fonte nomi per `4e/4f/4h`: contengono nomi storici ormai superati.
- Su cluster Databricks possono mancare `XlsxWriter`/`openpyxl`: il notebook modulare abilita `auto_install_excel_engine=True` nell'export.
- Per copiare su DBFS usare sempre il `excel_path` restituito dall'export; non hardcodare `local_sample_statistics.xlsx` in modalita' `fat_table`.
- Evitare import obbligatori di helper appena aggiunti nella prima cella notebook: usare lazy import/fallback se Databricks puo' avere moduli cacheati.
- Non lavorare direttamente su branch principale se la modifica e' ampia; creare un branch dedicato.
- Prima di cambiare mapping legacy, verificare i test e, se possibile, confrontare con `Old_statistics/`.
- VODR config `56` ha fat table su Unity Catalog ma usa il catalogo sheet **legacy** (`get_vodr_report_sheets()`): un tentativo di catalogo dedicato (`VODR_56_REPORT_SHEETS`) e' stato revertato il 2026-06-19; non reintrodurlo senza riallineare prima con il cliente.
- Per VODR config `56` (Eurocargo MY24), la fat table `u_truck_analyzer_p.vodr_statistics.fat_table_56` non porta `Average_vehicle_speed`/`mileage`/`cov_div_len`: senza queste sorgenti, `add_legacy_preparation_features()` non puo' derivare `mission`/`mileage_range` e ~18 sheet con quei `group_by` restano vuoti. Inoltre il join Mission Test ricade su `DEFAULT_VODR_MT_CONFIGS` perche' manca un mapping dedicato `frozenset({56})` in `VODR_TO_MT_CONFIGS`: nessun VIN viene agganciato. Verificare entrambe le cose prima di toccare il codice (vedi handoff 2026-06-22 pomeriggio).
- Per Mission Test `409` (S-WAY AS NP LATAM) la 1a e' divisa per tag Fly Recorder: `np_1a_1` (`region3`/`region4_torque_enginespeed`) e `np_409_1a_2` (`region1`, `region2`, `region3bis`, `region4bis`); entrambi raggruppati per `engine_model`/`power`/`mission`, non per `mileage_range`; non riattivare i fogli diesel `1a`/`1a_2` ne' l'overspeed in % (`engine_over_speed*`) per la 409. Vehicle Speed 409 = solo fasce `<20` e `20-40`.
- Se una stessa variabile tecnica ha descrizioni diverse per config, usare in `VARIABLE_DISPLAY_NAMES` la chiave `<variabile>_<sheet_id>` invece di sovrascrivere quella generica.
- La cartella locale `cestino/` (non tracciata) puo' contenere Excel di riferimento condivisi dal cliente; non committarla.

## Comandi Utili

- `git status` - controlla modifiche locali.
- `git log --oneline -5` - vede gli ultimi commit.
- `python -m pip install -r requirements.txt` - installa dipendenze.
- `python -m pytest tests/` - esegue i test.
- `python -m run_local_sample --no-excel` - valida il sample locale senza export.
- `python -m run_local_sample` - genera Excel Mission Test locale.
- `python -m run_local_sample --sheets fuel_consumption 2a 5a_dpf` - esegue solo alcuni sheet.
- `python -m run_local_sample --keep-all-updates` - evita dedup per VIN.

## Workflow Agenti

- All'inizio leggere `CLAUDE.md`, poi `handoff.md`, poi `git status` e `git log --oneline -5`.
- Aggiornare `handoff.md` a inizio/fine sessione con data, autore, obiettivo, decisioni e prossimi passi.
- Aggiornare `CLAUDE.md` quando emergono nuove convenzioni, decisioni architetturali o pitfalls.
- Regola d'oro: se un agente fa un'assunzione sbagliata, aggiungere una nota qui per non ripeterla.
