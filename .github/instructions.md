# GitHub Copilot Instructions

Questo repository contiene pipeline Python/PySpark per statistiche IVECO Mission Test e VODR.

## Contesto

- Sviluppo locale su sample Parquet/CSV, esecuzione completa su Databricks/Unity Catalog.
- I notebook `Main_pipeline_modular.ipynb` e `Main_pipeline_Vodr.ipynb` devono restare orchestratori.
- La logica va nei moduli `engine_*`, `vodr_*` e `run_local_sample.py`.
- `Old_statistics/` e' riferimento legacy, non codice da importare o rieseguire localmente.

## Regole Di Implementazione

- Non introdurre liste hardcoded nei notebook.
- Per Mission Test aggiornare `engine_config.py`; per VODR aggiornare `vodr_config.py`.
- Usare `clean_spark_column_names()` prima di lavorare su colonne tecniche Spark.
- Usare `keep_latest_record_per_vin()` solo quando e' richiesto il latest VIN; preservare raw updates per confronti legacy.
- Usare `report_pivot_pyspark_fixed()` per pivot statistiche.
- Riutilizzare funzioni di export in `run_local_sample.py`.
- Non committare sample, output Excel, cache o file dati pesanti.

## Verifica

- Prima di proporre modifiche, controllare se esistono test in `tests/`.
- Per cambi a mapping/config/export, aggiungere o aggiornare test mirati.
- Comandi preferiti:

```powershell
python -m pytest tests/
python -m run_local_sample --no-excel
```

## Documentazione

- Aggiornare `handoff.md` dopo sessioni operative.
- Aggiornare `CLAUDE.md` se emergono nuove decisioni architetturali, convenzioni o pitfalls.
