# Statistics 403: normalizzazione overspeed e crank

## Evidenza

La query sulla tabella `u_truck_analyzer_p.mission_test_statistics.fat_table_403`, dopo selezione dell'ultimo record per VIN, ha identificato il VIN `ZCFEG2RP70C542992` come outlier per entrambe le metriche:

- `engineoverspeed = 538976288` con `enginehours = 1792.05`;
- `avgcrank_100km = 167471.52` con `enginehours = 1792.05`.

L'aggregazione raw produceva quindi le deviazioni standard anomale. La normalizzazione candidata `metrica * 100 / enginehours` restituisce rispettivamente `30075962.61` e `9345.25`; entrambe devono essere escluse dalla soglia legacy `< 101`.

## Comportamento

Prima delle pivot, quando le colonne sono disponibili, la preparazione calcola:

- `engineoverspeed_pct = engineoverspeed * 100 / enginehours`;
- `crank_100km_pct = crank_100km * 100 / enginehours`.

Il valore normalizzato e' disponibile solo se strettamente maggiore di zero e minore di 101. I valori originali restano nel dataset completo per tracciabilita'.

I quattro fogli `Engine over speed`, `Engine over speed 2`, `Average crank per 100km` e `Average crank per 100km 2` usano le rispettive colonne normalizzate; i loro nomi e i trigger restano invariati. Per la 403 l'assenza di `vehicleoverspeed` non deve bloccare l'export: la colonna viene gia' ignorata quando non presente.

## Verifica

Test unitari verificano la formula, l'esclusione dei confini `0` e `101`, e che i quattro fogli risolvano le colonne normalizzate. Il run 403 atteso ha valori indicativi: overspeed valido con media circa `1.12`, deviazione circa `1.26`, conteggio `3`; crank con media `15.82`, deviazione `22.02`, conteggio `35`.
