# Statistics 403 NP: qualita', mileage e calculated

## Obiettivo

Correggere l'estrazione Statistics 403 MY24 NP affinche' i record con piu'
metriche fisicamente impossibili non alterino le statistiche, mantenendo il
VIN quando esiste un record storico valido. Completare inoltre le fasce di
velocita', i raggruppamenti per mileage e i fogli calculated secondo il
template NP aggiornato.

## Controllo di integrita' e selezione VIN

La pipeline applichera' un controllo di integrita' prima della selezione
dell'ultimo record per VIN. Ogni record ricevera' un conteggio di violazioni
indipendenti sulle metriche core disponibili:

- `Average_vehicle_speed` deve essere maggiore di zero e non superiore a
  80 km/h;
- `Average_enginespeed` deve essere compreso fra 200 e 4.000 rpm;
- `avgcrank_100km` deve essere compreso fra zero e 100;
- `engineoverspeed` deve essere non negativo e non superiore al tempo motore
  totale, espresso come `enginehours * 3600` secondi;
- `Average_start` deve essere maggiore di zero e non superiore a 1.000 minuti.

Un valore nullo non costituisce una violazione. Un record viene classificato
come corrotto e rimosso soltanto quando presenta almeno due violazioni. Questa
regola intercetta il record anomalo del VIN `ZCFEG2RP70C542992`, che contiene
anche il valore sentinella `538976288` (`0x20202020`), evitando di eliminare
un'intera riga per una singola metrica difettosa.

Dopo la rimozione dei record corrotti, la deduplica mantiene l'ultimo record
valido per VIN. Se il record piu' recente e' corrotto ma ne esiste uno storico
valido, viene quindi usato automaticamente lo storico valido. I filtri per
singola metrica restano attivi: una sola anomalia rende nulla la metrica ma
non elimina il veicolo.

## Average Vehicle Speed

Il foglio NP contiene sempre entrambe le fasce concordate:

- `<20 km/h`;
- `20-40 km/h`.

La fascia `>40 km/h` resta esclusa. Se una fascia non ha osservazioni valide,
viene comunque esportata con media, deviazione, advice e alert vuoti e count
uguale a zero.

## Raggruppamenti mileage

I seguenti fogli usano `engine_model` e `mileage_range` come chiavi di
raggruppamento, in quest'ordine:

- `3c) Gas rail pressure`;
- `3f) Mixture self-adapt poor`;
- `3g) Mixture self-adapt rich`;
- `4d) Catalyst Efficiency`;
- `Engine Life Cycle [%]`;
- `Low Catalyst Efficiency`.

Anche se la popolazione attuale contiene soltanto Cursor 9, `engine_model`
rimane nella configurazione per supportare motorizzazioni future.

## Calculated NP

Le colonne calculated sono derivate dai campi sorgente del template:

- Engine Life Cycle [%]: `100 - mileage / 10000`; il valore e' valido solo
  nell'intervallo chiuso `[0, 100]`;
- Time with Low Catalyst Efficiency [min]: `Cat_Eff_Timer / 60`;
- Low Catalyst Efficiency events [count]: `Cat_Eff_Counter`;
- Catalyst temperature > 860 C [min]:
  `Post_Catalyst_temperature_860_timer / 60`;
- Engine overspeed > 2660 rpm [seconds]:
  `Engine_overspeed_2600_rpm_Timer`;
- High engine coolant temperature > 104 C [seconds]:
  `Coolant_temperature_high_104_timer`;
- High oil temperature > 120 C [seconds]:
  `High_oil_temperature_120_timer`;
- High boost pressure > 2.5 bar [min]: `High_boost_pressure_timer / 60`;
- Low ambient pressure < 850 mbar [seconds]: `Low_ambient_pressure_timer`.

Time with Low Catalyst Efficiency e relativo count sono esportati nello
stesso foglio. I counter di coolant, oil, boost e ambient restano disponibili
nel Complete Dataset ma non sono inclusi nei rispettivi fogli calculated.
I timer sorgente possono essere numerici oppure stringhe `hh:mm:ss`; vengono
prima normalizzati in secondi e poi convertiti nell'unita' finale richiesta.
Gli zero sono validi per timer e counter e rimangono nelle statistiche.

## Compatibilita' e test

Le modifiche restano circoscritte al profilo `S_WAY_NP_MY_2024` quando il
comportamento e' specifico della 403. Le configurazioni diesel continuano a
usare le definizioni correnti.

I test automatici copriranno:

- esclusione di un record con almeno due violazioni;
- conservazione di un record con una sola metrica anomala;
- fallback all'ultimo record storico valido dello stesso VIN;
- presenza della fascia `<20 km/h` anche senza osservazioni;
- assenza della fascia `>40 km/h`;
- raggruppamenti `engine_model` e `mileage_range`;
- formula e limiti dell'Engine Life Cycle;
- nomi, unita' e composizione dei fogli calculated;
- regressione completa delle configurazioni esistenti.
