# Statistics 403: profilo MY24 NP

## Obiettivo

Generare l'estrazione Statistics 403 per i veicoli MY24 NP senza riutilizzare
le definizioni diesel associate agli stessi numeri di foglio. Il profilo NP
mantiene i report comuni, esclude le matrici 1a/1b non piu' prodotte dal
software corrente e aggiunge i report gas richiesti.

## Identificazione

La config 403 usa metadata statici:

- product type `MISSION_TEST`;
- product group `IVECO_S_X_WAY_NP`;
- product series `S_WAY_NP_MY_2024`.

Le eccezioni sono risolte per serie e non modificano le configurazioni 399,
405, 406 e 408.

## Fogli NP

I fogli 2a, 2b, 2c, 3a, 3c, 3f, 3g, 4d e 5c sono implementati come voci
interne dedicate al profilo NP. I nomi Excel restano quelli del catalogo NP:

- 2a Engine coolant temperature;
- 2b Oil temperature;
- 2c Intake air temperature;
- 3a Gas temperature;
- 3c Gas rail pressure;
- 3f Mixture self-adapting poor;
- 3g Mixture self-adapting rich;
- 4d Catalyst Efficiency;
- 5c Intake manifold pressure.

Le colonne e le descrizioni derivano dal template NP condiviso. Le percentuali
di permanenza nelle regioni sono calcolate con la logica gia' usata per i
fogli a soglia. Le definizioni diesel con gli stessi numeri sono disabilitate
solo per `S_WAY_NP_MY_2024`.

## Metriche calcolate

Sono aggiunti fogli dedicati per:

- Engine Lifecycle: solo `Engine_on_time`, in ore;
- Engine Overspeed: timer oltre 2660 rpm, in secondi;
- Catalyst Temperature: timer oltre 860 gradi, in minuti;
- Low Catalyst Efficiency: timer in minuti e numero eventi;
- Coolant Temperature oltre 104 gradi: timer `hh:mm:ss` e numero eventi;
- Oil Temperature oltre 120 gradi: timer `hh:mm:ss` e numero eventi;
- Boost Pressure alta: timer `hh:mm:ss` e numero eventi;
- Ambient Pressure bassa: timer `hh:mm:ss` e numero eventi.

I timer sorgente possono essere numerici oppure stringhe `hh:mm:ss`. La
preparazione li normalizza in secondi prima delle statistiche. Solo l'output
dei quattro timer richiesti in formato durata viene riconvertito in
`hh:mm:ss`; overspeed e catalyst restano numerici nelle unita' concordate.
Gli zero dei timer e dei counter sono valori validi e indicano assenza di
eventi, quindi non vengono trasformati in null.

## Vehicle Speed e Fuel Consumption

Il foglio Vehicle Speed della 403 NP include soltanto le fasce `<20 km/h` e
`20-40 km/h`. La fascia `>40 km/h` non viene esportata.

Fuel Consumption resta presente. Poiche' la fat table 403 contiene soltanto
zero o null, gli zero vengono esclusi come valori non validi e media,
deviazione, advice e alert rimangono vuoti. Il conteggio valido resta zero.

## Compatibilita' e verifica

Le API esistenti mantengono il comportamento corrente per tutte le altre
serie. Test automatici coprono metadata 403, risoluzione delle colonne NP,
esclusione delle matrici, conversione dei timer, fasce Vehicle Speed e celle
vuote in assenza di osservazioni fuel valide.
