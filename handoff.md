# Handoff

Registro operativo del repository. Ogni agente/contributore dovrebbe leggerlo a inizio sessione e aggiornarlo a fine lavoro.

## Come Aggiornare

- Aggiungi una nuova voce in cima o subito sotto questa sezione.
- Indica data, autore/tool, branch, obiettivo, azioni fatte, decisioni, test eseguiti e prossimi passi.
- Se scopri una regola stabile o un pitfall, aggiorna anche `CLAUDE.md`.

## Sessioni

### 2026-06-19 - Codex - branch `main`

- **Obiettivo**: capire perche' molti sheet Excel VODR risultavano vuoti con `Main_pipeline_Vodr.ipynb` e config `56`, usando la tabella cliente `Selected Table order / Table name / Variable name`.
- **Contesto letto**: `CLAUDE.md`, `handoff.md`, stato Git, `Main_pipeline_Vodr.ipynb`, `vodr_config.py`, `vodr_pipeline.py`, `tests/test_vodr_config.py`, `README.md` e allegato cliente.
- **Causa individuata**:
  - La config `56` era instradata correttamente su `u_truck_analyzer_p.vodr_statistics.fat_table_56`, ma ricadeva sul catalogo VODR legacy (`1b`, `2a`, `average_kick_down`, ecc.).
  - Nel catalogo legacy mancavano variabili richieste dalla 56 come `LowIdle`, `EngCool106`, `OilTemp114`, `Soh90ON`, `Aebs95`; altri sheet invece erano extra rispetto all'allegato.
  - Il notebook chiamava preview hardcoded per ID legacy e poteva fermarsi su `KeyError` quando il registry restituisce sheet diversi.
  - Nel file reale `cestino/VODR_56_new_thresholds_19_06.xlsx`, molti placeholder derivavano anche da `mission` e `mileage_range` presenti nel `Complete Dataset` ma vuoti su tutte le 461 righe; la prep legacy non li riempiva perche' controllava solo l'esistenza della colonna.
- **Azioni fatte**:
  - Aggiunti `VODR_56_PERCENTAGE_GROUPS` e `VODR_56_REPORT_SHEETS` in `vodr_config.py` con i 17 sheet/110 variabili dell'allegato, piu' `Complete Dataset`.
  - `get_vodr_percentage_groups({56})` e `get_vodr_report_sheets({56})` ora restituiscono il catalogo dedicato; le altre config restano sul catalogo legacy.
  - Trattato `7a/Aebs95` come metrica raw (`use_percentage_columns=False`), non come percentuale di un gruppo monocolonna.
  - Aggiornato `Main_pipeline_Vodr.ipynb` per saltare preview di sheet non configurati e aggiungere una preview dinamica degli sheet effettivamente presenti nel registry.
  - Aggiornato `add_legacy_preparation_features()` per riempire colonne derivate gia' presenti ma null/vuote (`mission`, `mileage_range`, range velocita', split mileage).
  - Aggiunto `cestino/` a `.gitignore`, cosi' gli Excel di contesto non entrano nei commit.
  - Aggiornati `tests/test_vodr_config.py`, `README.md`, `CLAUDE.md` e `.gitignore`.
- **Test/verifiche**:
  - `python -m py_compile vodr_config.py vodr_pipeline.py run_local_sample.py`: ok.
  - `python -m py_compile engine_cleaning.py vodr_config.py vodr_pipeline.py run_local_sample.py`: ok.
  - Validazione JSON `Main_pipeline_Vodr.ipynb`: ok.
  - `python -m pytest tests/test_vodr_config.py`: 7 passed.
  - `python -m pytest tests/`: 21 passed.
  - Analisi workbook `cestino/VODR_56_new_thresholds_19_06.xlsx`: 35 sheet totali, 22 placeholder; `Complete Dataset` contiene 109/110 variabili allegato, manca `Soh90ON`; `mission` e `mileage_range` erano vuoti su 461/461 righe.
  - Tentativo di test Spark locale su `engine_cleaning.py` rimosso per timeout ambiente Windows; non lasciarlo nella suite.
- **Prossimi passi**:
  - Su Databricks rilanciare `Main_pipeline_Vodr.ipynb` con widget `config=56`.
  - Controllare dai log eventuali righe `VODR <sheet> mancante: <colonna>` per capire se la fat table 56 ha nomi colonna diversi dal catalogo cliente.
  - Se qualche sheet resta placeholder, verificare soprattutto presenza di `product_series/product_model/power/mission/mileage_range` e delle variabili elencate nell'allegato.

### 2026-06-17 - Codex - branch `main`

- **Obiettivo**: allineare nomi sheet Excel e nomi variabili Mission Test alla tabella cliente `Table Name / Item Name / Variable Name`.
- **Contesto letto**: `CLAUDE.md`, `handoff.md`, stato Git, `engine_config.py`, `run_local_sample.py`, test esistenti e tabella allegata dal cliente.
- **Azioni fatte**:
  - Verificato che tutte le `Variable Name` della tabella siano presenti in `VARIABLE_DISPLAY_NAMES`.
  - Aggiornati i nomi sheet Mission Test con abbreviazioni entro il limite Excel di 31 caratteri.
  - Corretto l'ordine default `3c -> 3d -> 3e -> 3f -> 3g` usando gli sheet interni esistenti.
  - Rimosso dal default il vecchio sheet interno `4h`, duplicato rispetto al catalogo nuovo `4i`.
  - Aggiunto nome sheet dinamico per `2a`: per `S_WAY_AT_AD_MY_2024` diventa `2a_1) Oil pressure`.
  - Aggiunti test per nomi sheet, ordine catalogo e nome dinamico per serie.
- **Test/verifiche**:
  - `python -m pytest tests/`: 17 passed.
  - Nota: resta warning non bloccante `langsmith`/Pydantic V1 con Python 3.14.
- **Prossimi passi**:
  - Rigenerare Excel su Databricks e confrontare i tab con la tabella cliente.
  - Pubblicare i commit quando la credenziale GitHub locale sara' sistemata.

### 2026-06-15 - Codex - branch `main`

- **Obiettivo**: applicare appunti cliente 405 a tutta la pipeline `Main_pipeline_modular`.
- **Contesto letto**: `CLAUDE.md`, `handoff.md`, stato Git, `engine_config.py`, `run_local_sample.py`, test esistenti e riferimenti legacy.
- **Input cliente**:
  - Ordinamento errato di `mileage_range` e `mission` negli Excel.
  - Verifica grouping per `product_model`, `power`, `axle_description`, `mission`.
  - `4e` deve essere Urea Deposit, non AdBlue Pressure Pump.
  - Rimuovere Upstream Temperature come `4f`; `4f` diventa AdBlue Pressure Pump.
  - `4g/4h/4i` devono essere percentuali, non secondi.
  - `5c` Diff pressure of DPF deve calcolare advice/alert sottraendo dalla media.
- **Azioni fatte**:
  - Corretto ordinamento export per categorie business anche con piu' colonne di raggruppamento.
  - Corretto mapping `4e` -> `urea_dep_*`.
  - Corretto mapping `4f` -> `urea_p_*`.
  - Impostati `4g_doc_upstream_temperature`, `4h_scr_upstream_temperature`, `4i_scr_downstream_temperature` come percentuali.
  - Impostato trigger sottrattivo per `5c`.
  - Aggiunti test mirati su ordinamento e configurazioni fogli.
- **Test/verifiche**:
  - `python -m pytest tests/`: 14 passed.
  - Nota: resta warning non bloccante `langsmith`/Pydantic V1 con Python 3.14.
- **Prossimi passi**:
  - Rigenerare Excel su Databricks per 405 e verificare visivamente fogli citati dal cliente.

### 2026-06-12 - Codex - branch `main`

- **Obiettivo**: creare notebook one-shot per richiesta cliente su VIN con secondi > 600 C.
- **Contesto letto**: `CLAUDE.md`, `handoff.md`, stato Git, `Task_temp_600/MT_DAILY_PREP.ipynb`.
- **Input cliente**:
  - VIN `ZCFCE35B505652215`.
  - Segnalazione: 381 sec > 600 C non emersi dalla ricerca.
- **Azioni fatte**:
  - Identificate nel notebook originale le celle 11-14 come tentativo di analisi su `Temperatureupstr_doc_600`.
  - Creato `Task_temp_600/DOC600_VIN_Extraction.py` come Databricks source notebook.
  - Il nuovo notebook legge la fat table raw per config `382`, risolve case-insensitive `Temperatureupstr_DOC_600`, controlla il VIN cliente, estrae tutti i VIN con secondi > 600 C e confronta raw/all updates vs latest per VIN.
  - Previsto export CSV opzionale su `dbfs:/FileStore/iveco_statistics_output/task_temp_600`.
- **Decisioni**:
  - Task tenuto separato in `Task_temp_600/` perche' one-shot e non parte della pipeline principale.
  - Analisi basata sui raw/all updates prima del latest per evitare di perdere VIN con eventi presenti solo in aggiornamenti precedenti.
- **Test/verifiche**:
  - Validato source Databricks `.py` con separatori `# COMMAND ----------`.
- **Prossimi passi**:
  - Eseguire `Task_temp_600/DOC600_VIN_Extraction.py` su Databricks.
  - Se il VIN compare nei raw ma non nel latest, spiegare al cliente che il filtro latest per VIN nasconde quell'evento.

### 2026-06-12 - Codex - branch `main`

- **Obiettivo**: sistemare apertura/esecuzione del notebook DOC 600 su Databricks.
- **Azioni fatte**:
  - Rimosso dal repo `Task_temp_600/Extract_DOC_600_VIN_check.ipynb`, perche' Databricks Repos non lo caricava correttamente.
  - Promosso il Databricks source notebook a `Task_temp_600/DOC600_VIN_Extraction.py`.
  - Rinominato il source notebook con basename diverso da `Extract_DOC_600_VIN_check`, per evitare conflitti con IPYNB rimasti nel workspace Databricks da pull precedenti.
  - Aggiunto `Task_temp_600/MT_DAILY_PREP.ipynb` a `.gitignore` per evitare commit accidentali del notebook sorgente pesante.
- **Test/verifiche**:
  - Verificata anteprima del `.py` con header `# Databricks notebook source` e separatori `# COMMAND ----------`.
- **Prossimi passi**:
  - Su Databricks usare solo `DOC600_VIN_Extraction.py`, che Repos mostra come notebook nativo.

### 2026-06-12 - Codex - branch `main`

- **Obiettivo**: correggere export download del task DOC 600.
- **Azioni fatte**:
  - Modificato `Task_temp_600/DOC600_VIN_Extraction.py` per esportare CSV singoli nominati in FileStore.
  - I file prodotti sono `vin_summary_over_600.csv`, `detail_rows_over_600.csv`, `raw_vs_latest_check.csv`, `target_vin_all_updates.csv`.
  - Il notebook ora stampa link diretti ai file, non piu' solo alla cartella Spark CSV.
  - Corretta stringa `FileNotFoundError` nella lettura tabelle.
- **Test/verifiche**:
  - `python -m py_compile Task_temp_600/DOC600_VIN_Extraction.py`: ok.
- **Prossimi passi**:
  - Pull su Databricks e rilanciare l'ultima cella export.
  - Usare i link diretti stampati per scaricare i CSV.

### 2026-06-09 - Codex - branch `main`

- **Obiettivo**: evitare ImportError alla prima cella del notebook se Databricks ha `run_local_sample.py` vecchio/cacheato.
- **Contesto letto**: stato Git e `Main_pipeline_modular.ipynb`.
- **Azioni fatte**:
  - Rimosso `copy_excel_to_dbfs` dagli import obbligatori della prima cella.
  - Spostata la risoluzione del copy DBFS nella cella di export con lazy import.
  - Aggiunto fallback locale nella cella di export se `run_local_sample.copy_excel_to_dbfs` non e' ancora disponibile.
  - Aggiornato `CLAUDE.md` con pitfall sugli helper nuovi nei notebook Databricks.
- **Decisioni**:
  - La prima cella deve importare solo funzioni stabili gia' presenti nel modulo Databricks.
  - Gli helper nuovi usati solo a fine notebook vanno importati dove servono, con fallback se possibile.
- **Test/verifiche**:
  - `python -m pytest tests/`: 12 passed.
  - Verificato che `copy_excel_to_dbfs` non sia piu' importato nella prima cella del notebook.
  - Nota: resta il warning non bloccante di `langsmith`/Pydantic V1 con Python 3.14.
- **Prossimi passi**:
  - Sincronizzare Databricks con il commit della fix.
  - Dopo sync, la prima cella non deve piu' fallire anche se il modulo Python e' ancora cacheato.

### 2026-06-09 - Codex - branch `main`

- **Obiettivo**: rendere robusta la copia Excel su DBFS usando il nome file reale generato.
- **Contesto letto**: stato Git, `run_local_sample.py`, `Main_pipeline_modular.ipynb`, `CLAUDE.md`, `handoff.md`.
- **Azioni fatte**:
  - Aggiunta `copy_excel_to_dbfs()` in `run_local_sample.py`.
  - Aggiornato `Main_pipeline_modular.ipynb` per usare `copy_excel_to_dbfs(excel_path, dbutils, spark=spark)`.
  - Aggiunti test unitari per copia DBFS e file mancante.
  - Aggiornato `CLAUDE.md` con pitfall: non hardcodare `local_sample_statistics.xlsx` in `fat_table`.
- **Decisioni**:
  - La sorgente della copia DBFS e' sempre il `Path` restituito da `export_excel_outputs()`.
  - Il notebook non ricostruisce piu' manualmente nome file e download URL.
- **Test/verifiche**:
  - `python -m pytest tests/`: 12 passed.
  - Nota: resta il warning non bloccante di `langsmith`/Pydantic V1 con Python 3.14.
- **Prossimi passi**:
  - Sincronizzare Databricks con il commit della fix.
  - Rilanciare la cella `Export Excel`; non serve usare la cella manuale con `local_sample_statistics.xlsx`.

### 2026-06-09 - Codex - branch `main`

- **Obiettivo**: sbloccare export Excel su Databricks quando mancano `XlsxWriter`/`openpyxl`.
- **Contesto letto**: `CLAUDE.md`, `handoff.md`, stato Git, `run_local_sample.py`, `Main_pipeline_modular.ipynb`.
- **Azioni fatte**:
  - Estesa `export_excel_outputs()` con parametro `auto_install_excel_engine`.
  - Estesa `export_excel_report()` con lo stesso parametro per compatibilita' futura.
  - Aggiornato `Main_pipeline_modular.ipynb` per chiamare l'export con `auto_install_excel_engine=True`.
  - Aggiornato `CLAUDE.md` con il pitfall Databricks sugli engine Excel.
- **Decisioni**:
  - Lasciare default `False` nelle funzioni Python per non installare pacchetti in modo implicito da runner locali o chiamate programmatiche.
  - Abilitare auto-install solo nel notebook Databricks, dove l'errore e' emerso.
- **Test/verifiche**:
  - `python -m pytest tests/`: 10 passed.
  - Nota: resta il warning non bloccante di `langsmith`/Pydantic V1 con Python 3.14.
- **Prossimi passi**:
  - Sincronizzare Databricks con il commit della fix.
  - Dopo sync/restart, rilanciare la cella di export Excel.

### 2026-06-08 - Codex - branch `main`

- **Obiettivo**: abilitare la config Mission Test `408` per il notebook modulare.
- **Contesto letto**: `CLAUDE.md`, `handoff.md`, stato Git, `engine_loader.py`, `Main_pipeline_modular.ipynb`, `Main_pipeline.ipynb`, README e test config esistenti.
- **Azioni fatte**:
  - Aggiunta `408` a `MISSION_TEST_STATISTICS_CONFIGS` in `engine_loader.py`.
  - Aggiornato `Main_pipeline_modular.ipynb` per includere 408 negli esempi di config.
  - Aggiornati README, `export_config_csv.py`, `CLAUDE.md` e test.
- **Decisioni**:
  - Usare `Main_pipeline_modular.ipynb` con widget `config = 408`.
  - Non duplicare un notebook dedicato alla 408 e non aggiornare il vecchio `Main_pipeline.ipynb` hardcoded, per evitare assunzioni manuali sul `product_group`.
- **Test/verifiche**:
  - `python -c "from engine_loader import get_table_path; print(get_table_path(408))"`: restituisce `u_truck_analyzer_p.mission_test_statistics.fat_table_408`.
  - `python -m pytest tests/`: 10 passed.
  - Nota: resta il warning non bloccante di `langsmith`/Pydantic V1 con Python 3.14.
- **Prossimi passi**:
  - Su Databricks aprire `Main_pipeline_modular.ipynb`, impostare `input_mode=fat_table`, `config=408`, scegliere `keep_latest_per_vin` in base al confronto richiesto e lanciare.
  - Se la 408 produce `GENERIC` nel nome Excel, leggere i metadata reali e aggiornare `get_export_file_name()` solo se serve un prefisso dedicato.

### 2026-06-08 - Codex - branch `main`

- **Obiettivo**: creare memoria operativa di progetto per agenti AI e tool di coding.
- **Contesto letto**: `README.md`, `requirements.txt`, moduli `engine_*`, `vodr_*`, test principali e stato Git.
- **Azioni fatte**:
  - Creati `CLAUDE.md`, `handoff.md`, `conventions.md`.
  - Creata `.github/instructions.md` per GitHub Copilot.
  - Allineate le istruzioni a struttura reale del progetto: Mission Test, VODR, Databricks/Unity Catalog, runner locale, test.
- **Decisioni**:
  - Usare `CLAUDE.md` come memoria primaria per auto-load.
  - Usare `conventions.md` come riferimento compatto per tool senza auto-load.
  - Tenere `handoff.md` come diario di lavoro, non come duplicato del README.
- **Test/verifiche**:
  - `python -m pytest tests/`: 10 passed.
  - Nota: pytest mostra un warning non bloccante di `langsmith`/Pydantic V1 con Python 3.14.
- **Prossimi passi**:
  - Aggiornare questo file dopo ogni sessione.
  - Aggiornare `CLAUDE.md` quando emergono nuove convenzioni o assunzioni sbagliate.
  - Valutare se aggiungere prompt salvati o template specifici per review/refactor/documentazione.
