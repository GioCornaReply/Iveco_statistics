"""Legacy Threshold notebook snapshot.

Il file trovato nel workspace era vuoto. Questa snapshot salva le parti utili
fornite nel prompt del 2026-05-12, cosi' nei prossimi passaggi possiamo
confrontare il framework modulare con gli sheet storici senza ripartire dal
testo incollato in chat.

Nota: non e' pensato come runner Databricks. Il codice operativo deve vivere
nei moduli `engine_*` e in `Main_pipeline_modular.ipynb`.
"""


def report_pivot_pyspark_fixed(
    df3,
    lista,
    variabili,
    valutazione_triggers,
    config_vn=0,
    target_columns=None,
):
    """Versione ottimizzata legacy con filtro colonne e join robusto."""
    if config_vn == 0:
        config_ids = [row[0] for row in df3.select("id_config").distinct().collect()]
        config_vn = set(config_ids)
    else:
        config_vn = {config_vn}

    if target_columns:
        target_columns_clean = {c.strip().lower() for c in target_columns}
        filtered = [
            (col, valutazione_triggers[idx])
            for idx, col in enumerate(lista)
            if col.strip().lower() in target_columns_clean
        ]
        if not filtered:
            print(f"Errore: nessuna target_columns trovata in lista: {target_columns}")
            return None
        lista = [col for col, _ in filtered]
        valutazione_triggers = [trigger for _, trigger in filtered]

    if len(lista) != len(valutazione_triggers):
        print(f"Mismatch: lista ({len(lista)}) vs triggers ({len(valutazione_triggers)})")
        return None

    df_uno = None
    for col_name, trigger in zip(lista, valutazione_triggers):
        try:
            df_col = new_soglie_pyspark(df3, col_name, variabili, trigger)

            if df_col is None or df_col.isEmpty():
                print(f"{col_name}: risultato vuoto, salto.")
                continue

            print(f"Elaborata: {col_name}")

            if df_uno is None:
                df_uno = df_col
            else:
                if "Count" in df_col.columns:
                    df_col = df_col.drop("Count")
                df_uno = df_uno.join(df_col, on=variabili, how="outer")

        except Exception as exc:
            print(f"Errore su {col_name}: {exc}")
            continue

    if df_uno is None:
        print("Operazione fallita: nessun dato prodotto.")
        return None

    try:
        df_final = prep_toPandas(df_uno)
        df_final = ordered(df_final, variabili)
        df_final = rename_official(df_final, variables_names, config_vn)

        if hasattr(df_final, "display"):
            df_final.display()
        elif hasattr(df_final, "head"):
            print(df_final.head())

        import pandas as pd

        if isinstance(df_final, pd.DataFrame):
            return df_final
        return df_final.toPandas()

    except Exception as exc:
        print(f"Errore nel post-processing finale: {exc}")
        return None


LEGACY_THRESHOLD_SHEETS = [
    {
        "sheet_id": "complete_dataset",
        "excel_name": "Complete Dataset",
        "notes": "Export del dataset completo dopo rename_official.",
    },
    {
        "sheet_id": "urea_consumption_pct",
        "excel_name": "Urea Consumption %",
        "columns": ["AdBlue_consumption_percentage"],
        "group_by": ["engine_model"],
        "triggers": [1],
        "conditions": "Non S-WAY_AS_E3; valori >= 6 forzati a null.",
    },
    {
        "sheet_id": "fuel_consumption",
        "excel_name": "Fuel Consumption",
        "columns": ["average_fuel_consumption_kml"],
        "group_by": ["product_model", "power", "axle_description", "mission"],
        "triggers": [0],
    },
    {
        "sheet_id": "fuel_consumption_2",
        "excel_name": "Fuel Consumption 2",
        "columns": ["average_fuel_consumption_kml"],
        "group_by": ["product_model", "power", "axle_description", "Average_vehicle_speed_range"],
        "triggers": [0],
    },
    {
        "sheet_id": "urea_consumption_l100km",
        "excel_name": "Urea Consumption l_100km",
        "columns": ["AdBlue_consumption_l100km"],
        "group_by": ["product_group"],
        "triggers": [1],
    },
    {
        "sheet_id": "urea_consumption_l100km_2",
        "excel_name": "Urea Consumption l_100km 2",
        "columns": ["AdBlue_consumption_l100km"],
        "group_by": ["power", "mileage_range"],
        "triggers": [1],
    },
    {
        "sheet_id": "average_vehicle_speed",
        "excel_name": "Average Vehicle Speed",
        "columns": ["Average_vehicle_speed"],
        "group_by": ["Average_vehicle_speed_split"],
        "triggers": [0],
    },
    {
        "sheet_id": "average_vehicle_speed_2",
        "excel_name": "Average Vehicle Speed 2",
        "columns": ["Average_vehicle_speed"],
        "group_by": ["product_model", "power", "axle_description"],
        "triggers": [0],
    },
    {
        "sheet_id": "average_start",
        "excel_name": "Average Start",
        "columns": ["Average_start"],
        "group_by": ["product_model"],
        "triggers": [0],
    },
    {
        "sheet_id": "average_crank_per_hour",
        "excel_name": "Average Crank Per Hour",
        "columns": ["crank_hour"],
        "group_by": ["product_model"],
        "triggers": [1],
    },
    {
        "sheet_id": "average_crank_per_hour_2",
        "excel_name": "Average Crank Per Hour 2",
        "columns": ["crank_hour"],
        "group_by": ["product_group"],
        "triggers": [1],
    },
    {
        "sheet_id": "average_crank_per_100km",
        "excel_name": "Average crank per 100km",
        "columns": ["crank_100km"],
        "group_by": ["product_model"],
        "triggers": [1],
    },
    {
        "sheet_id": "average_crank_per_100km_2",
        "excel_name": "Average crank per 100km 2",
        "columns": ["crank_100km"],
        "group_by": ["product_group"],
        "triggers": [1],
    },
    {
        "sheet_id": "engine_over_speed",
        "excel_name": "Engine over speed",
        "columns": ["engineoverspeed"],
        "group_by": ["product_group"],
        "triggers": [1],
    },
    {
        "sheet_id": "engine_over_speed_2",
        "excel_name": "Engine over speed 2",
        "columns": ["engineoverspeed"],
        "group_by": ["product_model"],
        "triggers": [1],
    },
    {
        "sheet_id": "up_downstream_temperatures",
        "excel_name": "Up&Downstream Temperatures 2",
        "columns": [
            "Temperatureupstr_DOC_600",
            "Temperatureupstr_DPF_650",
            "Tempemperatureupstr_SCR_550",
            "Tempemperaturedwnstr_SCR_550",
            "SCR_DownstreamTemp_oltre_550",
            "SCR_UpstreamTemp_oltre_550",
            "DOC_UpstreamTemp_oltre_600",
            "DPF_UpstreamTemp_oltre_650",
        ],
        "group_by": ["product_group"],
        "triggers": [1, 1, 1, 1],
    },
    {
        "sheet_id": "catalyst_info",
        "excel_name": "5) CATALYST INFO",
        "columns": [
            "Diffpressure_DPF_020",
            "Sox_oxicat_08",
            "Nh3_concentration_550",
            "Adblue_concentration_29",
            "Adblue_concentration_63",
            "DPFup1",
            "DPFup2",
            "DPFup3",
        ],
        "group_by": ["product_group"],
        "triggers": [1],
    },
    {
        "sheet_id": "catalyst_info_v2",
        "excel_name": "5) CATALYST INFO_V2",
        "notes": "Media, Advice e Alert per product_group usando avg/stddev.",
    },
    {"sheet_id": "max_values", "excel_name": "7) MAXIMUM VALUES"},
    {"sheet_id": "1a", "excel_name": "1a EngineTorque | EngineSpeed"},
    {"sheet_id": "1b", "excel_name": "1b EngineTorque | VehicleSpeed"},
    {"sheet_id": "1c", "excel_name": "1c Engine Revolutions"},
    {"sheet_id": "1c_2", "excel_name": "1c Engine Revolutions 2"},
    {"sheet_id": "1d", "excel_name": "1d Turbine Overspeed"},
    {"sheet_id": "2a", "excel_name": "2a Oil Pressure"},
    {"sheet_id": "2a_5", "excel_name": "2a Oil Pressure 5"},
    {"sheet_id": "2b", "excel_name": "2b Oil Pressure in Sump"},
    {"sheet_id": "2c", "excel_name": "2c Oil Temperature"},
    {"sheet_id": "3a", "excel_name": "3a Engine Coolant Temperature"},
    {"sheet_id": "3a_1", "excel_name": "3a_1 Engine Coolant Temperature"},
    {"sheet_id": "3a_2", "excel_name": "3a_2  Coolant pressure"},
    {"sheet_id": "3b", "excel_name": "3b Fuel Temperature"},
    {"sheet_id": "3c", "excel_name": "3d Intake air temperature"},
    {"sheet_id": "3c_1", "excel_name": "3c_1 pressure sensor of fuel"},
    {"sheet_id": "3d", "excel_name": "3e Intake air pressure"},
    {"sheet_id": "3d_egr", "excel_name": "3d EGR actuator position %"},
    {"sheet_id": "3f", "excel_name": "3f Flap actuator position"},
    {"sheet_id": "3e", "excel_name": "3e Flap Actuator Position"},
    {"sheet_id": "3e_2", "excel_name": "3e Flap Actuator Position 2"},
    {"sheet_id": "4a", "excel_name": "4a Catalyst Efficiency g|kWh"},
    {"sheet_id": "4b", "excel_name": "4b Catalyst Eff vs Eng Speed"},
    {"sheet_id": "4c", "excel_name": "4c HC SCR Catalys"},
    {"sheet_id": "4c_2", "excel_name": "4c HC accum in SCR Catalyst 2"},
    {"sheet_id": "4d", "excel_name": "4d NH3 Concentration"},
    {"sheet_id": "4e_nh3", "excel_name": "4e NH3 Concentration"},
    {"sheet_id": "4d_urea", "excel_name": "4d Urea deposit"},
    {"sheet_id": "4f_adblue", "excel_name": "4f ADBlue Pressure Pump"},
    {"sheet_id": "4e_urea", "excel_name": "4e Urea deposit"},
    {"sheet_id": "4e_adblue", "excel_name": "4e AdBlue PressurePump"},
    {"sheet_id": "4g_doc_upstream_temperature", "excel_name": "4g DOC Upstream Temperature"},
    {"sheet_id": "4h_scr_upstream_temperature", "excel_name": "4h SCR upstream temperature"},
    {"sheet_id": "4i_scr_downstream_temperature", "excel_name": "4i SCR Downstream Temperature"},
    {"sheet_id": "5a_dpf", "excel_name": "5a DPF Upstream Temperature"},
    {"sheet_id": "5a_dpf_2", "excel_name": "5a DPF Upstream Temperature 2"},
    {"sheet_id": "5b", "excel_name": "5b Regeneration Strategies"},
    {"sheet_id": "5c", "excel_name": "5c) Diff pressure of DPF"},
    {"sheet_id": "5d", "excel_name": "5d Soot mass estimated / 5d Flow Resist"},
    {
        "sheet_id": "6a_engine_brake_status",
        "excel_name": "6a) Engine brake status",
        "columns": ["eng_brake_status_1", "eng_brake_status_2", "eng_brake_status_3"],
        "status": "pending: colonne non presenti nel sample 399 esportato",
    },
    {
        "sheet_id": "6b_braking_torque",
        "excel_name": "6b) Braking torque",
        "columns": [
            "brak_torque_req_1",
            "brak_torque_req_2",
            "brak_torque_req_3",
            "brak_torque_req_4",
            "brak_torque_req_5",
            "brak_torque_req_6",
            "brak_torque_req_7",
            "brak_torque_req_8",
        ],
        "status": "pending: colonne non presenti nel sample 399 esportato",
    },
    {
        "sheet_id": "turbocharger_revolutions",
        "excel_name": "Turbocharger revolutions",
        "columns": [
            "Turbochargerrevolutions_109000",
            "Turbochargerrevolutions_127000",
            "Turbochargerrevolutions_130000",
            "Turbochargerrevolutions_max",
        ],
        "group_by": ["engine_model"],
        "triggers": [1, 1],
    },
]


LEGACY_CONFIG_399_NOTES = {
    "config": {399},
    "product_type": "HEAVY",
    "product_group": "IVECO_S_WAY",
    "product_series": "S_WAY_AT_AD_MY_2024",
    "required_prep": [
        "dedup ultimo record per VIN",
        "engine_model da product_model",
        "Average_vehicle_speed_range",
        "Average_vehicle_speed_split",
        "mileage_range",
        "mileage_split",
        "mission",
        "zeri convertiti a null sulle statistiche legacy dove richiesto",
    ],
}
