# Handoff

Registro operativo del repository. Ogni agente/contributore dovrebbe leggerlo a inizio sessione e aggiornarlo a fine lavoro.

## Come Aggiornare

- Aggiungi una nuova voce in cima o subito sotto questa sezione.
- Indica data, autore/tool, branch, obiettivo, azioni fatte, decisioni, test eseguiti e prossimi passi.
- Se scopri una regola stabile o un pitfall, aggiorna anche `CLAUDE.md`.

## Sessioni

### 2026-10-28 - Claude (Sonnet 5.5) - branch `feat/mission-test-410`

- **Obiettivo**: far girare `Main_pipeline_modular.ipynb` sulle config Daily MY24 diesel `382`/`384` (errore `Nessun Excel generato`).
- **Diagnosi**: nessuno sheet prodotto perche' `df_clean` risultava vuoto. Indizi: `extract_metadata` restituisce `UNKNOWN` x3 su DataFrame vuoto e anche `complete_dataset` non veniva esportato. Causa piu' probabile: `apply_statistics_quality_filters` scarta i dati con `udt_timestamp` piu' vecchio di 366 giorni (dati Daily MY24 del 2024); possibili anche `mileage <= 1000` / `enginehours <= 1`. Da confermare su Databricks con i conteggi stampati dalla cella export.
- **Azioni fatte**:
  - Cella export: se nessuno sheet e' prodotto, stampa `DIAGNOSI` (metadata, righe raw vs dopo filtri, colonne) e solleva errore chiaro.
  - Widget `max_data_age_days` (default 366, `0` = nessun limite); `apply_statistics_quality_filters` accetta `None`/`<=0` per disattivare il filtro eta'.
  - Layout Daily MY24: serie `DAILY_MY24`, gruppo `IVECO_DAILY`, metadata 382/384 in `CONFIG_METADATA`, export `Statistics_DAILY_<config>_dataset.xlsx`. 23 sheet `daily_*` (1a..6b, 89 variabili) generati da `DAILY_MY24_CATALOG` in `engine_config.py`, fonte il foglio "TABLES AND PROGRESS BAR" dei template in `382_384_daily_disel/` (non tracciata, non committare).
  - Report di riferimento passato `Statistics_LIGHT_382_384_Daily_MY_2024_new_thresholds (7).xlsx` (in `382_384_daily_disel/`): 6 sheet, ora i soli default Daily: `Engine Speed vs Torque F1A/F1C` (rev_tor_*), `Engine Torque F1A/F1C` (torque_*), `Battery Voltage`, `Battery SOC`. 1a/1c: righe per `engine_model`+`power`, filtro motore via `allowed_group_values`; batteria: riga per `mileage_split`, header = item name del template (doppio spazio dopo "region" mantenuto). I 23 sheet del catalogo restano registrati (`daily_*`) ma fuori dal default.
  - Fix `clean_excel_column_name`: senza item name il fallback toglie il suffisso sheet dal nome colonna.
  - Stile header: il runner usa Title Case (`Engine Model`, `Rev Tor Idle`), l'esempio passato era in MAIUSCOLO (`ENGINE`).
  - Run Databricks 382: uscivano solo Battery Voltage/SOC e Complete Dataset perche' `engine_model` era `Unknown` su tutte le 214 righe (`product_model` non inizia per F1A/F1C). Il legacy (`MT_DAILY_PREP`) ricavava il motore con regex su `engine_type`: `engine_model_standard` ora usa anche `engine_type`/`engine_code`. DA VERIFICARE su Databricks che `engine_type` esista nella fat table 382/384 (altrimenti guardare `product_model`, `engine_code`, `power`, `id_config`).
  - Nuovo sheet Daily `Fuel Consumption km_l 2` (`daily_fuel_kml_2`, primo dei default Daily): righe per engine_model/product_model/power/axle_description/missione, colonna `average_fuel_consumption_kml`. Missione Daily in colonna dedicata `mission_daily` (fasce <15 / 15-25 / 25-45 / >45, da `MT_DAILY_PREP`; header 'Mission'), ordinata con `DAILY_MISSION_LABELS`. Header consumo rinominato via nuova setting sheet `rename_columns` (la descrizione generica della variabile e' 'LNG').
  - Filtri qualita': per 382/384 `average_fuel_consumption_kml` ammesso fino a 25 km/l (`get_quality_filter_overrides`; il range Heavy 0.1-6 azzererebbe i valori Daily, fino a ~13 nell'esempio). Il limite 25 e' un'ipotesi: verificare con il cliente.
  - Test: `tests/test_config_daily_my24.py` (incluso export Excel end-to-end su dati sintetici).
- **Decisioni**:
  - Un solo profilo per F1A e F1C: le variabili tecniche sono identiche, cambiano solo soglie rpm nelle descrizioni (usate quelle F1C 6.4.2). La separazione F1A/F1C e' data da `engine_model` (derivato da `product_model`).
  - 382/384 restano su tabelle legacy `missiontest.fat_table_<config>` (non spostate in `MISSION_TEST_STATISTICS_CONFIGS`).
  - Colonne `group_by` non presenti vengono ignorate da `build_sheet_pivot`: gli sheet Daily non saltano se manca `mission`/`mileage_range`.
- **Prossimi passi**:
  - Su Databricks lanciare 382 con `max_data_age_days=0` e verificare i conteggi e le colonne reali (`product_model`, `power`, `mission`).
  - Confermare con il cliente quale config e' F1A e quale F1C (etichette rpm degli item `1a`, `1d`).
  - Verificare il formato sheet con il cliente: i `Table Name` del template sono abbreviati a 31 caratteri.

### 2026-10-12 - Claude (Haiku 5.5) - branch `feat/mission-test-410`

- **Obiettivo**: far uscire la config Mission Test `410` (S-WAY NP MY24 C13) con gli sheet e le colonne del template `1_template_colonne/template S-WAY_NP_MY24_C13.xlsx`.
- **Decisioni**:
  - La 410 riceve sia i profili NP MY24 (403) sia quelli 409 (1a split per tag, 4a, 4b, 4d): il template ha la struttura 409 e le KPI MY24.
  - Serie assunta `S_WAY_NP_MY24_C13` (nome template normalizzato). Dato non disponibile in locale: non verificabile prima del run su Databricks.
  - Fuel: `fuel_lng` (kg) e `fuel_cng` escono entrambi per la 410 (tre voci ciascuno, come CALCULATED_ITEMS del template).
  - La 410 eredita le colonne della 403 (profilo NP MY24) dove non ha una regola propria, rispettando gli skip della 403 (`2a`, `2b` restano esclusi). Override dal template: `1b` (`region1..5_torque_vehiclespeed`), `1c` (`engine_revolutions_OK/medium/high`), `3a` (+`fueltemp_magg_0`). `np_4d` non esce per la 410 perche' duplicherebbe `np_409_4d` (stesse colonne `reg*_Cat_Eff`). Richiesta utente: sheet in piu' rispetto al template vanno esportati comunque e tolti a mano se non servono.
  - Filtro record corrotti: la 410 entra nel scope 403 gia' tramite serie (`NP` + `MY24`) e in modo esplicito per `id_config`.
  - Unita' `coverage_driven_length`: resta il `/1000` (come per la 403). La colonna "Operation new" del template omette il `/1000`, ma il suo esempio numerico e' incoerente: da verificare su Databricks.
- **Azioni fatte**:
  - `engine_config.py`: `NP_410_SERIES`, aggiunta a `NP_REPORT_SERIES` e `NP_409_REPORT_SERIES`, `series_names` 410 sulle sheet NP 409, `fuel_lng` anche per 410.
  - `engine_cleaning.py`: `_np_409_scope` riconosce config 410 (oltre a 409) e la serie `S_WAY_NP_MY24_C13`.
  - `engine_loader.py`: 410 in `MISSION_TEST_STATISTICS_CONFIGS` e `CONFIG_METADATA` (`IVECO_S_X_WAY_NP`, export `HEAVY_SWAY_NP`).
  - `tests/test_config_410.py`: 10 test (routing, metadata/export, 1a split, diesel skip, fuel LNG/CNG a tre voci, 1b/1c dal template, ereditarieta' dalla 403, KPI e catalyst split, nomi sheet, non-contaminazione 403).
- **Test/verifiche**:
  - `pytest tests`: 42 passed, 3 failed, 13 errors. Stesso set di fallimenti di HEAD (3 failed + 13 errori); i nuovi test passano. I fallimenti sono preesistenti (`test_403_np_calculated_sheet_units_and_vehicle_speed_bands`, due test Excel su `mileage range`, errori Spark `WinError 6` in questo terminale).
  - Non verificato: calcoli Spark delle feature 410 (servono i test Spark, non eseguibili qui) e colonne reali della fat table 410.
- **Prossimi passi (su Databricks)**:
  1. Pull del branch e run `Main_pipeline_modular.ipynb` con `input_mode=fat_table`, `config=410`.
  2. Controllare il `product_series` stampato e che gli sheet `np_1a_1`, `np_409_1a_2`, `np_409_4a_*`, `np_409_4d`, `fuel_lng`, `fuel_cng` non siano vuoti.
  3. Se una colonna del template non esiste nella fat table 410, segnalarla: va aggiunta alla feature calcolata o alla lista colonne.
  4. Gap noti rispetto al template (non coperti dal codice): sheet `2d` (ambient pressure per regione), `3d` (gas rail reg4/5), `5a`/`5d`/`5e` (engine mode, intake low, boost per regione), `4c` (catalyst upstream 600-860), `6) Maximum Values` nella forma del template, misfire 3h-3o per regione di modo motore (per la 410 esce il calcolato `misfire_knocking_cylinders_min`). Decidere se servono nuovi sheet.
  5. Config `402` (stesso SW G35.1/G40.2 del template, da Index) e' instradata ma non ha `CONFIG_METADATA`: confermare se serve lo stesso profilo 410.
  6. Su Databricks: lo sheet 4e/4f deve usare i nomi `urea_dep_*`/`urea_p_*` come la 403; i sheet AdBlue (`urea_consumption_*`) non sono nel template della 410 e sono esclusi.

### 2026-10-08 - Claude (Opus 5.5) - branch `fix/mission-test-409-kpis`

- **Obiettivo**: correzione richiesta dall'utente sulla 1a della 409.
- **Fix**: `np_1a_1` e `np_409_1a_2` ora hanno `group_by = ["engine_model", "power", "mission"]` (prima `mileage_range`, con `power` solo su `_2`). Test `test_409_np_splits_1a_by_fly_recorder_tag` aggiornato.
- **Test**: `pytest tests/test_config_405_406.py -k 409` -> 6 passed.

### 2026-10-07 - Claude (Opus 5.5) - branch `fix/mission-test-409-kpis`

- **Obiettivo**: correggere gli errori 409 (S-WAY AS NP MY22 LATAM) emersi nella call di review dello Statistics.
- **Fix applicate** (solo registry/feature 409, 403 invariata salvo dove indicato):
  - Vehicle Speed: la 409 usa `np_average_vehicle_speed` (solo `<20 km/h` e `20-40 km/h`); `average_vehicle_speed` generico skippato.
  - Engine Overspeed duplicato: skippati `engine_over_speed`/`engine_over_speed_2` (overspeed in % non esiste nelle query SQL); resta `np_engine_overspeed` in secondi.
  - 1A split per tag Fly Recorder: `np_1a_1` = `region3`/`region4_torque_enginespeed` (tag `bsRpm__esPercCMUIstABSReal_1`); nuovo `np_409_1a_2` = `region1`, `region2`, `region3bis`, `region4bis` (tag `_2`) con split `power`. Percentuali calcolate per tag. Fogli diesel `1a`/`1a_2` skippati per la 409. Rimossa la calculated `optimal_specific_fuel_consumption_region_50_100_400_1800_rpm`.
  - Header 1a: display name con chiave `<variabile>_<sheet_id>` (lookup aggiunto in `get_display_name_for_metric`) per non rinominare le regioni diesel legacy.
  - Misfire: `np_misfire_cylinders` spostato fra le calculated; match colonne cilindro reso robusto al naming catalogo (`Misfire/Knocking_Detection_Cylinder_N_MIN`).
  - `np_409_4d`: rimosso `target_columns`, ora esporta anche `reg1_Cat_Eff` (<50 %) come check della somma percentuali.
- **Test**: 5 nuovi test config + 1 Spark per misfire. In locale `pytest` -> 31 passed, 3 failed preesistenti (test 403 su group_by cambiati in `42fbe49` e header `Mileage Range`), 13 error Spark per `WinError 6` (gateway Java non avviabile da questo terminale).
- **Da verificare su Databricks**: log `Sheet np_misfire_cylinders: presenti=...` (se ancora 0, i nomi colonna cilindri della fat table 409 sono diversi); presenza di `region3bis`/`region4bis_torque_enginespeed`.
- **Aperti (non codice)**: deviazione standard ~105 % su un foglio con 21 casi (check Giovanni); gas temperature 43 % sotto -30 C (chiedere a Luigi; verificare anche se la 409 ha regioni gas temperature oltre `fueltemp1..3`, perche' il denominatore percentuale usa solo quelle tre).

### 2026-06-22 (pomeriggio) - Claude (Opus 4.7) - branch `main`

- **Obiettivo**: capire perche' molti sheet VODR config `53` e `56` risultano vuoti su Databricks, partendo dalla lista degli sheet vuoti fornita dal cliente e dal template `cestino/VODR_template EurocargoMY24 6-10 ton.xlsx`.
- **Contesto letto**: `Main_pipeline_Vodr.ipynb`, `vodr_pipeline.py`, `vodr_config.py`, `engine_cleaning.py`, template Eurocargo (5 sheet: `FOGLIO_GIO`, `SIMPLE ITEMS`, `CALCULATED ITEMS`, `TABLES`, `Progress bar`, `GAUGE ITEM`).
- **Strumento di indagine**: aggiunta cella diagnostica `diagnose_vodr_empty_sheets()` in fondo a `Main_pipeline_Vodr.ipynb` (commit `0a99a90`, poi esteso in `04f02b9` per stampare anche stato colonne sorgente, join MT e candidati per speed/mileage).
- **Fix applicate** (commit `424fce1`):
  - `engine_cleaning.add_legacy_preparation_features`: ora usa `F.coalesce` per `mission`, `mileage_range`, `Average_vehicle_speed_range/_split`, `mileage_split`. Helper isolato `_fill_derived_column`. La guardia `if "X" not in df.columns` non bastava: nella fat table VODR 56 quelle colonne esistono come schema ma sono tutte NULL.
  - `vodr_config.VODR_REPORT_SHEETS["time_in_semi"].columns`: rimosso il prefisso `Tot`, ora `TimeInSemiWithEngineRunning` / `TimeInAutoSuspendWithEngineRunning` / `TimeInAutoWithEngineRunning` (allineato al template `SIMPLE ITEMS`).
  - `vodr_config.VODR_PERCENTAGE_GROUPS["5c"]`: aggiunto `Soh90ON` (era nel template ma mancava nel registry); trigger esteso a `[1,1,1,0,0,1,1,1,0,0]`.
- **Test/verifiche**:
  - `tests/test_vodr_config.py`: 2 nuovi test (`test_vodr_time_in_semi_uses_official_column_names`, `test_vodr_5c_battery_soh_includes_soh90on`).
  - `python -m pytest tests/`: 21 passed (Python 3.14 di sistema; il `.venv` locale non ha pyspark/pandas — usare l'interprete `C:\Users\g.cornacchia\AppData\Local\Python\bin\python.exe`).
- **Esito dopo il run Databricks delle 15:35**:
  - **Risolto**: 3b/3c/3d (retarder presente in fat table 56), 4a Gear10-16 e R2-R4, 4c, 2a Weight45/50, lights (29 colonne), time_in_semi, Soh90ON. Tutte queste colonne ora compaiono in `present_cols` nella diagnostica.
  - **Ancora vuoti**: tutti gli sheet con `mission` o `mileage_range` nel `group_by` (1b_2, 2a, 4a, 4c, 4c_2, 5a, 5b, 5c, 5c_2, 6a, 6b, 6b_2, 6c, 6c_2, 6d, average_kick_down_2, selection_mode_2, aebs_intervention, safety, level, lights).
- **Causa rimasta da risolvere**: in `df_time_percentage` per config 56,
  - `Average_vehicle_speed`: TUTTA NULL (0% non-null);
  - `mileage`: TUTTA NULL;
  - `cov_div_len`: ASSENTE;
  - `Average_vehicle_speed_mt` / `mileage_mt`: TUTTA NULL;
  - `id_config_mt`: TUTTA NULL → **il join Mission Test non aggancia nessun VIN VODR 56**.
  Senza sorgenti, `add_legacy_preparation_features` non puo' derivare `mission` / `mileage_range` neanche con la nuova fix `coalesce`.
- **Ipotesi (da verificare)**: in `vodr_config.VODR_TO_MT_CONFIGS` non c'e' un mapping dedicato `frozenset({56})` ne' `frozenset({53})`, quindi il join ricade su `DEFAULT_VODR_MT_CONFIGS` (31 config MT) che probabilmente non coprono Eurocargo MY24 6-10 ton. Da confermare con un'esplorazione di `Old_statistics/*VODR*HEAVY_PREP*` (esplorazione interrotta dall'utente prima dell'esecuzione).
- **Prossimi passi** (sessione 2026-06-23):
  1. Lanciare l'esplorazione interrotta: come calcolavano `mission` / `mileage_range` / `Average_vehicle_speed` i notebook legacy VODR su Eurocargo? Esiste una colonna alternativa nella fat table VODR 56 (`total_distance`, `total_driving_time`, `engineminutes`, somma tempi per mission) utilizzabile come proxy?
  2. Verificare in `vodr_config.VODR_TO_MT_CONFIGS` se serve aggiungere un mapping dedicato per `{56}` (e `{53}`) verso config Mission Test che agganciano i VIN Eurocargo MY24.
  3. Se ne' la fat table VODR 56 ne' MT portano speed/mileage per quei VIN, riaprire la discussione col cliente: o si aggiungono le colonne sorgente nella fat table 56, o si accetta che gli sheet con `mission`/`mileage_range` restino vuoti per quella config.
- **Note operative**:
  - L'output diagnostico completo dei due run (15:06 prima delle fix, 15:35 dopo) e' nella chat ma non incollato qui per non gonfiare il file.
  - La cartella `cestino/` resta non tracciata: contiene `VODR_56_new_thresholds_19_06.xlsx` e `VODR_template EurocargoMY24 6-10 ton.xlsx` (template colonne).
  - Commit pushati su `origin/main`: `0a99a90`, `424fce1`, `04f02b9`.

### 2026-06-22 - Claude (Opus 4.7) - branch `main`

- **Obiettivo**: rilettura del repository per riallineare i file MD allo stato del codice dopo il revert del 2026-06-19.
- **Contesto letto**: `CLAUDE.md`, `handoff.md`, `git status`, `git log --oneline -20`, `engine_loader.py`, `vodr_config.py`, `vodr_pipeline.py`, `run_local_sample.py`, `engine_config.py`, `README.md`, `tests/`, diff dei commit `7c46539`/`bb86fea`/`5cb1e64`.
- **Stato osservato**:
  - VODR config `56` resta **routata su Unity Catalog** (`engine_loader.VODR_STATISTICS_CONFIGS` e `vodr_config.VODR_STATISTICS_CONFIGS` la includono; test `test_vodr_statistics_configs_use_unity_catalog_tables` la asserisce).
  - Il commit "Fix VODR config 56 report sheets" (catalogo sheet dedicato + riempimento colonne null in `add_legacy_preparation_features` + preview dinamica notebook + voce handoff del 2026-06-19) e' stato revertato in `5cb1e64`; quindi VODR 56 usa di nuovo gli sheet legacy `get_vodr_report_sheets()`.
  - `cestino/VODR_56_new_thresholds_19_06.xlsx` resta presente non tracciato (la regola `cestino/` in `.gitignore` e' stata rimossa dal revert: usare con cautela, non aggiungere a Git).
  - `CLAUDE.md` elencava ancora solo `33,49,50,51,52,53,54` come VODR Unity Catalog: disallineato con il codice. Corretto a includere `56`.
- **Azioni fatte**:
  - Aggiornato `CLAUDE.md`: lista VODR Unity Catalog include `56`; aggiunto pitfall su VODR 56 (catalogo sheet legacy, niente reintroduzione del catalogo dedicato senza accordo cliente) e nota su `cestino/` non tracciato.
  - Aggiunta questa voce in `handoff.md` per ricostruire le sessioni mancanti dal 2026-06-17 in poi.
- **Test/verifiche**:
  - Nessun test eseguito in questa sessione: solo letture e aggiornamento documentazione.
- **Prossimi passi**:
  - Se la pipeline VODR 56 produce ancora sheet vuoti su Databricks, riaprire la discussione con il cliente prima di reintrodurre `VODR_56_REPORT_SHEETS`: il revert del 2026-06-19 indica che la fix precedente non era quella attesa.
  - Quando si riprende il lavoro su 56, ripartire dai diff `bb86fea`/`5cb1e64` per capire cosa era stato proposto e perche' e' stato annullato.

### 2026-06-19 - Codex - branch `main` - REVERTATO

- **Nota**: la sessione del 2026-06-19 ("Fix VODR config 56 report sheets") e' stata revertata interamente in `5cb1e64`. Il diff originale resta consultabile come `git show bb86fea`. Il revert ha tolto: `VODR_56_PERCENTAGE_GROUPS` / `VODR_56_REPORT_SHEETS`, il riempimento di colonne null in `add_legacy_preparation_features()`, le modifiche a `Main_pipeline_Vodr.ipynb` per preview dinamiche, la regola `.gitignore` per `cestino/`, i test dedicati e le note README/CLAUDE/handoff.
- **Lezione**: la fix proposta per VODR 56 non era allineata con quanto richiesto dal cliente; non riproporre senza nuovo input.

### 2026-06-18 - Codex - branch `main`

- **Obiettivo**: estendere routing VODR a config `56` e usare metadati di config invece di leggere righe per nome file.
- **Commit principali**: `4a0cf55` (skip heavy fat table diagnostics), `8808023` (use config metadata for fat tables), `7c46539` (route VODR 56 to Unity Catalog).
- **Azioni fatte**:
  - Aggiunta `56` a `VODR_STATISTICS_CONFIGS` in `engine_loader.py` e `vodr_config.py`.
  - Aggiornato test `test_vodr_statistics_configs_use_unity_catalog_tables` per coprire 56.
  - Introdotto `CONFIG_METADATA` e `get_metadata_for_config()` in `engine_loader.py`: il nome export Mission Test ora si risolve senza eseguire `df.select().first()` quando i metadata sono noti (399, 405, 406, 408).
  - Aggiornati `Main_pipeline_modular.ipynb` e `run_local_sample.py` per saltare diagnostiche pesanti sulla fat table quando non servono.
  - Aggiornato `tests/test_config_405_406.py` con asserzioni su `get_metadata_for_config`.
- **Test/verifiche**:
  - Test inclusi nei commit; suite `tests/` mantenuta verde a livello di commit.
- **Prossimi passi**:
  - Verificare su Databricks che VODR 56 legga correttamente da `u_truck_analyzer_p.vodr_statistics.fat_table_56`.
  - Confermare che i nomi file Mission Test su Databricks rispettino la mappa `CONFIG_METADATA` anche per future config.

### 2026-06-18 - Codex - branch `main`

- **Obiettivo**: piccoli fix UX nel notebook modulare Mission Test.
- **Commit principali**: `361e671` (fix turbocharger zero reporting), `8555021` (fix modular notebook 4g/4h/4i previews).
- **Azioni fatte**:
  - Lo sheet `turbocharger_revolutions` ora preserva gli zeri per `Turbochargerrevolutions_130000` (`zero_as_null_exclude`), perche' il valore zero ha significato di business per quella colonna.
  - Le preview di `4g/4h/4i` nel notebook sono allineate al fatto che ora le tre tabelle sono percentuali, non secondi.
- **Test/verifiche**:
  - Test `test_turbocharger_130000_keeps_zero_values` aggiunto in `tests/test_config_405_406.py`.

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
