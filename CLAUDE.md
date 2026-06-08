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
- Per Mission Test nuove config `399,400,401,402,405,406,408` si usa `u_truck_analyzer_p.mission_test_statistics.fat_table_<config>`.
- Per VODR config `33,49,50,51,52,53,54` si usa `u_truck_analyzer_p.vodr_statistics.fat_table_<config>`.
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
- Per sheet Mission Test usare `get_columns_for_sheet()`, `get_sheet_settings()` e `get_default_sheet_ids()`.
- Per VODR usare `get_vodr_report_sheets()`, `get_vodr_percentage_groups()` e `parse_config_text()`.
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
- Non lavorare direttamente su branch principale se la modifica e' ampia; creare un branch dedicato.
- Prima di cambiare mapping legacy, verificare i test e, se possibile, confrontare con `Old_statistics/`.

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
