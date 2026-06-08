# Convenzioni Di Progetto

Questo file riassume le regole operative per strumenti che non caricano automaticamente `CLAUDE.md`.

## Principi

- I notebook orchestrano; la logica di business sta nei moduli Python.
- Le configurazioni di sheet, colonne, trigger e mapping stanno in `engine_config.py` o `vodr_config.py`.
- La pipeline Mission Test e la pipeline VODR sono correlate ma distinte.
- Gli output Excel, sample locali, cache e dati pesanti non vanno committati.
- Le modifiche vanno verificate almeno con test mirati quando toccano mapping, sheet, export o parsing config.

## Moduli

- `engine_loader.py`: sorgenti dati, mapping config, metadata, nomi file.
- `engine_config.py`: configurazione sheet Mission Test.
- `engine_cleaning.py`: normalizzazione colonne, dedup VIN, feature legacy, rinomina ufficiale.
- `engine_stats.py`: percentuali, soglie, pivot e conversione Pandas.
- `run_local_sample.py`: runner locale e export Excel.
- `vodr_config.py`: configurazione report VODR.
- `vodr_pipeline.py`: pipeline VODR e join con Mission Test.
- `tests/`: test unitari di configurazione e regressione.

## Stile

- Preferire funzioni piccole, nominate sul dominio, rispetto a logica dentro notebook.
- Evitare stringhe magiche duplicate: centralizzare in costanti o registry.
- Usare PySpark per trasformazioni dati fino al punto in cui serve Pandas per export/preview.
- Gestire colonne mancanti con validazioni/log, non con assunzioni silenziose.
- Conservare compatibilita' con naming legacy quando serve confrontare vecchi output.

## Dati E Output

- Sample locale atteso: `data/sample/Subset_Config_399_Date_20260511_123241`.
- Output locale Mission Test: `Excel_statistics/local_sample_statistics.xlsx`.
- Output Databricks: `Excel_statistics/` e copia DBFS/FileStore quando gestita dal notebook.
- Non aggiungere a Git sample, output Excel o cartelle cache.

## Comandi

```powershell
python -m pip install -r requirements.txt
python -m pytest tests/
python -m run_local_sample --no-excel
python -m run_local_sample
```

## Prompt Base Nuova Sessione

```text
Sei un assistente di sviluppo per questo repository.
Prima di tutto:
1. Leggi CLAUDE.md per il contesto del progetto
2. Leggi handoff.md per vedere cosa e' stato fatto prima
3. Esegui git status e git log --oneline -5
4. Fammi un riassunto di:
   - Scopo del progetto
   - Stack tecnologico
   - Prossimi passi da handoff
   - Pitfalls da evitare

Poi chiedimi cosa voglio fare oggi.
```

## Prompt Utili

- `/prompt-check`: controlla modifiche, rischi, test mancanti e comandi da eseguire.
- `/prompt-refactor`: proponi refactor piccoli, compatibili con i test e senza cambiare output.
- `/prompt-docs`: aggiorna README, CLAUDE, handoff e commenti solo dove servono.

