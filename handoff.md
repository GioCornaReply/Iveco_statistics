# Handoff

Registro operativo del repository. Ogni agente/contributore dovrebbe leggerlo a inizio sessione e aggiornarlo a fine lavoro.

## Come Aggiornare

- Aggiungi una nuova voce in cima o subito sotto questa sezione.
- Indica data, autore/tool, branch, obiettivo, azioni fatte, decisioni, test eseguiti e prossimi passi.
- Se scopri una regola stabile o un pitfall, aggiorna anche `CLAUDE.md`.

## Sessioni

### 2026-06-12 - Codex - branch `main`

- **Obiettivo**: creare notebook one-shot per richiesta cliente su VIN con secondi > 600 C.
- **Contesto letto**: `CLAUDE.md`, `handoff.md`, stato Git, `Task_temp_600/MT_DAILY_PREP.ipynb`.
- **Input cliente**:
  - VIN `ZCFCE35B505652215`.
  - Segnalazione: 381 sec > 600 C non emersi dalla ricerca.
- **Azioni fatte**:
  - Identificate nel notebook originale le celle 11-14 come tentativo di analisi su `Temperatureupstr_doc_600`.
  - Creato `Task_temp_600/Extract_DOC_600_VIN_check.ipynb`.
  - Il nuovo notebook legge la fat table raw per config `382`, risolve case-insensitive `Temperatureupstr_DOC_600`, controlla il VIN cliente, estrae tutti i VIN con secondi > 600 C e confronta raw/all updates vs latest per VIN.
  - Previsto export CSV opzionale su `dbfs:/FileStore/iveco_statistics_output/task_temp_600`.
- **Decisioni**:
  - Task tenuto separato in `Task_temp_600/` perche' one-shot e non parte della pipeline principale.
  - Analisi basata sui raw/all updates prima del latest per evitare di perdere VIN con eventi presenti solo in aggiornamenti precedenti.
- **Test/verifiche**:
  - Validato JSON notebook con Node: 20 celle leggibili.
- **Prossimi passi**:
  - Eseguire `Task_temp_600/Extract_DOC_600_VIN_check.ipynb` su Databricks.
  - Se il VIN compare nei raw ma non nel latest, spiegare al cliente che il filtro latest per VIN nasconde quell'evento.

### 2026-06-12 - Codex - branch `main`

- **Obiettivo**: sistemare apertura/esecuzione del notebook DOC 600 su Jupyter/Databricks.
- **Azioni fatte**:
  - Normalizzato `Task_temp_600/Extract_DOC_600_VIN_check.ipynb` con `nbformat`, includendo `id` celle.
  - Aggiunta versione fallback Databricks source `Task_temp_600/Extract_DOC_600_VIN_check.py`.
- **Test/verifiche**:
  - `nbformat.validate`: ok, 20 celle, tutte con `id`.
  - Verificata anteprima del `.py` con separatori `# COMMAND ----------`.
- **Prossimi passi**:
  - Su Databricks usare il `.ipynb`; se il viewer fa ancora problemi, aprire/importare il `.py`.

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
