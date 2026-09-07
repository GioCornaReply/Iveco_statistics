# Correzione Statistics 403: qualità dati e segmentazione

## Obiettivo

Rendere coerente l'estrazione Statistics 403 con le regole operative condivise: statistiche calcolate su record validi con percorrenza superiore a 1.000 km, nessuna segmentazione chilometrica per Average Vehicle Speed, e ultimo record per VIN selezionato di default.

## Popolazione e qualità dati

Una funzione riusabile di preparazione applicherà, prima di qualsiasi pivot:

- normalizzazione delle varianti legacy per mileage, engine-hours e timestamp quando presenti;
- esclusione dei record con `mileage <= 1000`;
- validazione di `average_fuel_consumption_kml` nell'intervallo `(0, 6]`;
- ripristino dei limiti legacy per le metriche disponibili: engine-hours `> 1`, velocità media `(0, 80]`, AdBlue percentage `(0, 100]`, AdBlue l/100km `(0, 9]`, Average Start `(0, 1000]`, crank/100km `> 0.1`;
- esclusione dei record senza engine-hours, mileage o timestamp valido e più vecchi di 366 giorni, quando le rispettive colonne sono disponibili.

I valori fuori range vengono resi nulli per la metrica; i record non validi per popolazione (mileage, engine-hours, timestamp) vengono esclusi. L'applicazione è tollerante alle colonne non presenti, così resta utilizzabile per le config con schema parziale.

## Statistiche e configurazione dei fogli

- `keep_latest_per_vin` sarà `Yes` nel widget e `True` in esecuzione non-Databricks; l'utente potrà scegliere `No` per analisi degli update storici.
- Il foglio Average Vehicle Speed userà `Average_vehicle_speed_split` come raggruppamento, coerentemente con il riferimento legacy; non userà `mileage_range`.
- Le fasce `mileage_range` restano disponibili per i soli fogli che le richiedono davvero, ma non esporranno più label `1000k` come se rappresentassero 1.000 km. Le fasce esistenti sopra 900.000 km restano semanticamente espresse in milioni (`1M`) per evitare ambiguità.
- Il Complete Dataset continuerà a mostrare i dati preparati (non i raw), quindi non mostrerà fuel a zero o fuori intervallo.

## Punti di integrazione

- `engine_cleaning.py`: funzione di qualità dati riusabile e label mileage corrette.
- `run_local_sample.py`: applicazione del filtro e default VIN, sia nel runner sia nelle funzioni usate dal notebook.
- `Main_pipeline_modular.ipynb`: default del widget `keep_latest_per_vin` e chiamata al filtro prima della derivazione delle feature.
- `engine_config.py`: group-by del foglio Average Vehicle Speed.

## Verifica

I test copriranno i confini di mileage/fuel, l'esclusione dei record invalidi, le label delle fasce di percorrenza, il default VIN e il group-by del foglio. Sarà eseguita l'intera suite `pytest`.
