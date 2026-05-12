# engine_config.py
#
# Configurazione centralizzata di colonne e sheet report.
# Le regole mantengono la priorita': Series > Group > layout generico.

NEW_LAYOUT_SERIES = {
    "S_WAY_AS_E3",
    "S_WAY_AS_E5",
    "S_WAY_AS_MY_2024",
    "S_WAY_AT_AD_MY_2024",
    "X_WAY_AS_MY_2024",
}

SHEET_ALIASES = {
    # Nome storico usato nel primo runner locale.
    "5a": "catalyst_info",
}

DEFAULT_REPORT_SHEETS = [
    "complete_dataset",
    "urea_consumption_pct",
    "fuel_consumption",
    "fuel_consumption_2",
    "urea_consumption_l100km",
    "urea_consumption_l100km_2",
    "average_vehicle_speed",
    "average_vehicle_speed_2",
    "average_start",
    "average_crank_per_hour",
    "average_crank_per_hour_2",
    "average_crank_per_100km",
    "average_crank_per_100km_2",
    "engine_over_speed",
    "engine_over_speed_2",
    "up_downstream_temperatures",
    "catalyst_info",
    "catalyst_info_v2",
    "max_values",
    "1a",
    "1a_2",
    "1b",
    "1c",
    "1c_2",
    "1d",
    "2a",
    "2b",
    "2c",
    "3a",
    "3a_1",
    "3a_2",
    "3b",
    "3c",
    "3c_1",
    "3d",
    "3e",
    "3e_2",
    "3f",
    "4a_1",
    "4a",
    "4b",
    "4c",
    "4c_2",
    "4d",
    "4e",
    "4f",
    "4h",
    "5a_dpf",
    "5a_dpf_2",
    "5b",
    "5c",
    "5d",
    "4g_doc_upstream_temperature",
    "4h_scr_upstream_temperature",
    "4i_scr_downstream_temperature",
    "6a_engine_brake_status",
    "6b_braking_torque",
    "turbocharger_revolutions",
]

REPORT_SHEET_CONFIG = {
    "complete_dataset": {
        "name": "Complete Dataset",
        "kind": "dataset",
        "use_percentage_columns": False,
    },
    "urea_consumption_pct": {
        "name": "Urea Consumption %",
        "use_percentage_columns": False,
        "columns": ["AdBlue_consumption_percentage"],
        "group_by": ["engine_model"],
        "trigger": 1,
        "max_value": 6,
        "zero_as_null": True,
        "skip_series": {"S_WAY_AS_E3"},
    },
    "fuel_consumption": {
        "name": "Fuel Consumption",
        "use_percentage_columns": False,
        "columns": ["average_fuel_consumption_kml"],
        "group_by": ["product_model", "power", "axle_description", "mission"],
        "trigger": 0,
        "zero_as_null": True,
    },
    "fuel_consumption_2": {
        "name": "Fuel Consumption 2",
        "use_percentage_columns": False,
        "columns": ["average_fuel_consumption_kml"],
        "group_by": ["product_model", "power", "axle_description", "Average_vehicle_speed_range"],
        "trigger": 0,
        "zero_as_null": True,
    },
    "urea_consumption_l100km": {
        "name": "Urea Consumption l_100km",
        "use_percentage_columns": False,
        "columns": ["AdBlue_consumption_l100km"],
        "group_by": ["product_group"],
        "trigger": 1,
        "zero_as_null": True,
        "skip_series": {"S_WAY_AS_E3"},
    },
    "urea_consumption_l100km_2": {
        "name": "Urea Consumption l_100km 2",
        "use_percentage_columns": False,
        "columns": ["AdBlue_consumption_l100km"],
        "group_by": ["power", "mileage_range"],
        "trigger": 1,
        "zero_as_null": True,
        "skip_series": {"S_WAY_AS_E3"},
    },
    "average_vehicle_speed": {
        "name": "Average Vehicle Speed",
        "use_percentage_columns": False,
        "columns": ["Average_vehicle_speed"],
        "group_by": ["Average_vehicle_speed_split"],
        "trigger": 0,
        "zero_as_null": True,
    },
    "average_vehicle_speed_2": {
        "name": "Average Vehicle Speed 2",
        "use_percentage_columns": False,
        "columns": ["Average_vehicle_speed"],
        "group_by": ["product_model", "power", "axle_description"],
        "trigger": 0,
        "zero_as_null": True,
    },
    "average_start": {
        "name": "Average Start",
        "use_percentage_columns": False,
        "columns": ["Average_start"],
        "group_by": ["product_model"],
        "trigger": 0,
        "zero_as_null": True,
    },
    "average_crank_per_hour": {
        "name": "Average Crank Per Hour",
        "use_percentage_columns": False,
        "columns": ["crank_hour", "avgcrank_km"],
        "group_by": ["product_model"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "average_crank_per_hour_2": {
        "name": "Average Crank Per Hour 2",
        "use_percentage_columns": False,
        "columns": ["crank_hour", "avgcrank_km"],
        "group_by": ["product_group"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "average_crank_per_100km": {
        "name": "Average crank per 100km",
        "use_percentage_columns": False,
        "columns": ["crank_100km"],
        "group_by": ["product_model"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "average_crank_per_100km_2": {
        "name": "Average crank per 100km 2",
        "use_percentage_columns": False,
        "columns": ["crank_100km"],
        "group_by": ["product_group"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "engine_over_speed": {
        "name": "Engine over speed",
        "use_percentage_columns": False,
        "columns": ["engineoverspeed", "vehicleoverspeed"],
        "group_by": ["product_group"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "engine_over_speed_2": {
        "name": "Engine over speed 2",
        "use_percentage_columns": False,
        "columns": ["engineoverspeed", "vehicleoverspeed"],
        "group_by": ["product_model"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "up_downstream_temperatures": {
        "name": "Up&Downstream Temperatures 2",
        "use_percentage_columns": False,
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
        "trigger": 1,
        "zero_as_null": True,
    },
    "catalyst_info": {
        "name": "5) CATALYST INFO",
        "series": {
            "S_WAY_AT_AD_MY_2024": [
                "Diffpressure_DPF_020",
                "Sox_oxicat_08",
                "Nh3_concentration_550",
                "Adblue_concentration_29",
                "Adblue_concentration_63",
            ],
            "S_WAY_AS_MY_2024": [
                "Diffpressure_DPF_020",
                "Sox_oxicat_08",
                "Nh3_concentration_550",
                "Adblue_concentration_29",
                "Adblue_concentration_63",
            ],
            "S_WAY_AS_ANZ": ["DPFup1", "DPFup2", "DPFup3"],
        },
        "groups": {
            "IVECO_S_WAY": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
            "EUROCARGO": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
        },
    },
    "catalyst_info_v2": {
        "name": "5) CATALYST INFO_V2",
        "use_percentage_columns": False,
        "series": {
            "S_WAY_AT_AD_MY_2024": [
                "Diffpressure_DPF_020",
                "Sox_oxicat_08",
                "Nh3_concentration_550",
                "Adblue_concentration_29",
                "Adblue_concentration_63",
            ],
            "S_WAY_AS_MY_2024": [
                "Diffpressure_DPF_020",
                "Sox_oxicat_08",
                "Nh3_concentration_550",
                "Adblue_concentration_29",
                "Adblue_concentration_63",
            ],
            "S_WAY_AS_ANZ": ["DPFup1", "DPFup2", "DPFup3"],
        },
        "columns": [
            "Diffpressure_DPF_012",
            "Diffpressure_DPF_020",
            "Sox_oxicat_08",
            "Nh3_concentration_550",
            "Adblue_concentration_29",
            "Adblue_concentration_63",
        ],
        "group_by": ["product_group"],
        "trigger": 1,
        "zero_as_null": True,
        "skip_series": {"S_WAY_AS_E3", "S_WAY_AS_E5"},
    },
    "max_values": {
        "name": "7) MAXIMUM VALUES",
        "use_percentage_columns": False,
        "columns": [
            "Oilpressure_020",
            "Oilpressure_25",
            "Enginerevolutions_max",
            "Coolanttemperature_max",
            "Diffpressure_DPF_max",
            "Temperatureupstr_DOC_max",
            "Intakeairtemperature_max",
            "Fueltemperature_max",
            "Intakeairpressure_max",
        ],
    },
    "1a": {
        "name": "1a_1 EngineTorque | EngineSpeed",
        "group_by": ["engine_model", "power", "mission"],
        "triggers": [1, 0, 1, 1, 0, 1, 1, 1],
        "new_layout": [
            "tor_rev_cutoff",
            "tor_rev_low",
            "tor_rev_lowlow",
            "tor_rev_high_1",
            "tor_rev_opt",
            "tor_rev_highlow",
            "tor_rev_high_2",
        ],
        "legacy": [
            "region1_torque_enginespeed",
            "region2_torque_enginespeed",
            "region3_torque_enginespeed",
            "region4_torque_enginespeed",
            "region5_torque_enginespeed",
            "region6_torque_enginespeed",
            "region7_torque_enginespeed",
        ],
    },
    "1a_2": {
        "name": "1a_2 EngineTorque | EngineSpeed",
        "group_by": ["engine_model"],
        "triggers": [1, 0, 1, 1, 0, 1, 1, 1],
        "new_layout": [
            "tor_rev_cutoff",
            "tor_rev_low",
            "tor_rev_lowlow",
            "tor_rev_high_1",
            "tor_rev_opt",
            "tor_rev_highlow",
            "tor_rev_high_2",
        ],
        "legacy": [
            "region1_torque_enginespeed",
            "region2_torque_enginespeed",
            "region3_torque_enginespeed",
            "region4_torque_enginespeed",
            "region5_torque_enginespeed",
            "region6_torque_enginespeed",
            "region7_torque_enginespeed",
        ],
    },
    "1b": {
        "name": "1b EngineTorque | VehicleSpeed",
        "group_by": ["engine_model", "power", "mission"],
        "triggers": [0, 1, 1, 1, 1, 0, 0, 0, 1],
        "groups": {
            "EUROCARGO": [
                "tor_speed_cutoff",
                "tor_speed_idle",
                "tor_speed_pto",
                "tor_speed_hurb",
                "tor_speed_urb",
                "tor_speed_extrurb_1",
                "tor_speed_extrurb_2",
                "tor_speed_highway",
            ],
        },
        "new_layout": [
            "tor_speed_cutoff",
            "tor_speed_idle",
            "tor_speed_pto",
            "tor_speed_hurb",
            "tor_speed_urb",
            "tor_speed_extrurb",
            "tor_speed_highway",
            "tor_speed_downhill",
            "tor_speed_overspeedlimit",
        ],
        "legacy": [
            "region1_torque_vehiclespeed",
            "region2_torque_vehiclespeed",
            "region3_torque_vehiclespeed",
            "region4_torque_vehiclespeed",
            "region5_torque_vehiclespeed",
            "region6_torque_vehiclespeed",
            "region7_torque_vehiclespeed",
            "region8_torque_vehiclespeed",
            "region9_torque_vehiclespeed",
        ],
    },
    "1c": {
        "name": "1c Engine Revolutions",
        "group_by": ["engine_model"],
        "triggers": [1, 0, 1, 1, 1],
        "groups": {"EUROCARGO": ["eng_speed_1", "eng_speed_2", "eng_speed_3"]},
        "new_layout": ["eng_speed_1", "eng_speed_2", "eng_speed_3", "eng_speed_4", "eng_speed_5"],
        "legacy": [
            "engine_revolutions_low",
            "engine_revolutions_OK",
            "engine_revolutions_medium",
            "engine_revolutions_high2",
        ],
    },
    "1c_2": {
        "name": "1c Engine Revolutions 2",
        "group_by": ["engine_model", "power", "mission"],
        "triggers": [1, 0, 1, 1, 1],
        "groups": {"EUROCARGO": ["eng_speed_1", "eng_speed_2", "eng_speed_3"]},
        "new_layout": ["eng_speed_1", "eng_speed_2", "eng_speed_3", "eng_speed_4", "eng_speed_5"],
        "legacy": [
            "engine_revolutions_low",
            "engine_revolutions_OK",
            "engine_revolutions_medium",
            "engine_revolutions_high2",
        ],
    },
    "1d": {
        "name": "1d Turbine Overspeed",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["turb_speed_1", "turb_speed_2", "turb_speed_3", "turb_speed_4"],
        "legacy": ["region1_turborev", "region2_turborev", "region3_turborev"],
    },
    "2a": {
        "name": "2a Oil Pressure",
        "group_by": ["engine_model", "mission"],
        "triggers": [0, 1, 1],
        "groups": {"EUROCARGO": ["p_oil_ok_1", "p_oil_tbc", "p_oil_low", "p_oil_low_1"]},
        "new_layout": ["p_oil_ok_1", "p_oil_tbc_1", "p_oil_low_1"],
        "legacy": ["oilpressure_low1", "oilpressure_tocheck1", "oilpressure_ok1"],
    },
    "2b": {
        "name": "2b Oil Pressure in Sump",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1],
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["p_sump_ok_1", "p_sump_tbc_1", "p_sump_crit_1"],
        "legacy": [
            "oilpressuresump_ok1",
            "oilpressuresump_tobechecked1",
            "oilpressuresump_critical1",
        ],
    },
    "2c": {
        "name": "2c Oil Temperature",
        "group_by": ["engine_model"],
        "triggers": [0, 1],
        "groups": {"EUROCARGO": ["oil_t_ok", "oil_t_high"]},
        "new_layout": ["oil_t_ok", "oil_t_high"],
        "legacy": ["oiltemp1", "oiltemp2"],
    },
    "3a": {
        "name": "3a Engine Coolant Temperature",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1],
        "groups": {"EUROCARGO": ["eng_t_cool_1", "eng_t_cool_2", "eng_t_cool_3"]},
        "new_layout": ["eng_t_cool_1", "eng_t_cool_2", "eng_t_cool_3"],
        "legacy": ["region1_coolantT", "region2_coolantT", "region3_coolantT"],
    },
    "3a_1": {
        "name": "3a_1 Engine Coolant Temperature",
        "columns": ["eng_t_p_cool_1", "eng_t_p_cool_2", "eng_t_p_cool_3", "eng_t_p_cool_4", "eng_t_p_cool_5"],
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1, 1],
    },
    "3a_2": {
        "name": "3a_2) Coolant pressure",
        "columns": ["eng_p_cool_1", "eng_p_cool_2", "eng_p_cool_3", "eng_p_cool_4"],
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
    },
    "3b": {
        "name": "3b Fuel Temperature",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1],
        "groups": {"EUROCARGO": ["fuel_t_1", "fuel_t_2", "fuel_t_3"]},
        "new_layout": ["fuel_t_1", "fuel_t_2", "fuel_t_3"],
        "legacy": ["fueltemp1", "fueltemp2", "fueltemp3"],
    },
    "3c": {
        "name": "3d Intake air temperature",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["int_air_t_1", "int_air_t_2", "int_air_t_3", "int_air_t_4"]},
        "new_layout": ["int_air_t_1", "int_air_t_2", "int_air_t_3", "int_air_t_4"],
    },
    "3c_1": {
        "name": "3c_1 pressure sensor of fuel",
        "columns": ["fuel_prefilter_p_low", "fuel_prefilter_p_ok", "fuel_prefilter_p_high"],
        "group_by": ["engine_model"],
        "triggers": [0, 1, 0],
    },
    "3d": {
        "name": "3e Intake air pressure",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["int_air_p_1", "int_air_p_2", "int_air_p_3", "int_air_p_4"]},
        "new_layout": ["int_air_p_1", "int_air_p_2", "int_air_p_3", "int_air_p_4"],
        "legacy": ["EGR_position1", "EGR_position2", "EGR_position3"],
    },
    "3e": {
        "name": "3e Flap Actuator Position",
        "group_by": ["engine_model", "mission"],
        "triggers": [0, 1, 1, 1],
        "groups": {
            "EUROCARGO": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"]
        },
        "new_layout": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"],
        "legacy": ["Flap1", "Flap2", "Flap3", "Flap4"],
    },
    "3e_2": {
        "name": "3e Flap Actuator Position 2",
        "group_by": ["engine_model", "power", "mission"],
        "triggers": [0, 1, 1, 1],
        "groups": {
            "EUROCARGO": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"]
        },
        "new_layout": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"],
        "legacy": ["Flap1", "Flap2", "Flap3", "Flap4"],
    },
    "3f": {
        "name": "3f Flap actuator position",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["egr_position_1", "egr_position_2", "egr_position_3"],
    },
    "4a_1": {
        "name": "4a.1) Catalyst Efficiency PEMS",
        "groups": {
            "EUROCARGO": ["cat_eff_scr_1_a", "cat_eff_scr_1_b", "cat_eff_scr_1_c", "cat_eff_scr_1_d"]
        },
        "new_layout": ["cat_eff_scr_1_a", "cat_eff_scr_1_b", "cat_eff_scr_1_c", "cat_eff_scr_1_d"],
    },
    "4a": {
        "name": "4a Catalyst Efficiency g|kWh",
        "group_by": ["engine_model", "power", "mileage_range"],
        "triggers": [0, 1, 1],
        "groups": {"EUROCARGO": ["cat_eff_scr_2_a", "cat_eff_scr_2_b", "cat_eff_scr_2_c"]},
        "new_layout": ["cat_eff_scr_2_a", "cat_eff_scr_2_b", "cat_eff_scr_2_c"],
        "legacy": ["regionA_catalyst_BAD", "regionB_catalyst_BAD", "regionCD_catalyst_BAD"],
    },
    "4b": {
        "name": "4b Catalyst Eff vs Eng Speed",
        "group_by": ["engine_model", "power", "mileage_range", "mission"],
        "triggers": [1, 1, 1, 0],
        "groups": {"EUROCARGO": ["cat_eff_0_40", "cat_eff_40_65", "cat_eff_65_90", "cat_eff_90_100"]},
        "new_layout": ["cat_eff_0_40", "cat_eff_40_65", "cat_eff_65_90", "cat_eff_90_100"],
        "legacy": [
            "region1_Cateff_enginespeed",
            "region2_Cateff_enginespeed",
            "region3_Cateff_enginespeed",
            "region4_Cateff_enginespeed",
        ],
    },
    "4c": {
        "name": "4c HC SCR Catalys",
        "group_by": ["product_group"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"]},
        "new_layout": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"],
        "legacy": ["region1_hc", "region2_hc", "region3_hc", "region4_hc"],
    },
    "4c_2": {
        "name": "4c HC accum in SCR Catalyst 2",
        "group_by": ["product_group"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"]},
        "new_layout": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"],
        "legacy": ["region1_hc", "region2_hc", "region3_hc", "region4_hc"],
    },
    "4d": {
        "name": "4d NH3 Concentration",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["urea_dep_1", "urea_dep_2", "urea_dep_3", "urea_dep_4"]},
        "new_layout": ["nh3_conc_1", "nh3_conc_2", "nh3_conc_3"],
        "legacy": ["region1_NH3", "region2_NH3", "regipn3_NH3"],
    },
    "4e": {
        "name": "4e) AdBlue Pressure Pump",
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["urea_p_1", "urea_p_2", "urea_p_3", "urea_p_4"],
        "legacy": ["adbluepressure1", "adbluepressure2", "adbluepressure3", "adbluepressure4"],
    },
    "4f": {
        "name": "4f) Upstream Temperature",
        "groups": {"EUROCARGO": ["doc_upstr_t_1", "doc_upstr_t_2", "doc_upstr_t_3"]},
        "new_layout": ["scr_upstr_t_1", "scr_upstr_t_2", "scr_upstr_t_3"],
        "legacy": ["DOCtemp1", "DOCtemp2", "DOCtemp3"],
    },
    "4h": {
        "name": "4h) SCR Downstream Temperature",
        "groups": {"EUROCARGO": ["scr_dwnstr_t_1", "scr_dwnstr_t_2", "scr_dwnstr_t_3"]},
        "new_layout": ["scr_dwnstr_t_1", "scr_dwnstr_t_2", "scr_dwnstr_t_3"],
        "legacy": ["SCRdwntemp1", "SCRdwntemp2", "SCRdwntemp3"],
    },
    "5a_dpf": {
        "name": "5a DPF Upstream Temperature",
        "group_by": ["product_group"],
        "triggers": [1],
        "groups": {
            "EUROCARGO": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
            "IVECO_X_WAY": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
            "IVECO_T_WAY": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
            "IVECO_S_WAY": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
        },
        "skip_series": {"S_WAY_AS_E3", "S_WAY_AS_E5"},
        "legacy": ["DPFup1", "DPFup2", "DPFup3"],
    },
    "5a_dpf_2": {
        "name": "5a DPF Upstream Temperature 2",
        "group_by": ["product_group"],
        "triggers": [1, 0, 1],
        "groups": {
            "EUROCARGO": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
            "IVECO_X_WAY": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
            "IVECO_T_WAY": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
            "IVECO_S_WAY": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
        },
        "skip_series": {"S_WAY_AS_E3", "S_WAY_AS_E5"},
        "legacy": ["DPFup1", "DPFup2", "DPFup3"],
    },
    "5b": {
        "name": "5b Regeneration Strategies",
        "group_by": ["engine_model", "power", "mileage_range"],
        "trigger": 1,
        "groups": {
            "EUROCARGO": [
                "regen_strategy_1",
                "regen_strategy_2",
                "regen_strategy_3",
                "regen_strategy_4",
                "regen_strategy_5",
                "regen_strategy_6",
            ]
        },
        "new_layout": [
            "regen_strategy_1",
            "regen_strategy_2",
            "regen_strategy_3",
            "regen_strategy_4",
            "regen_strategy_5",
            "regen_strategy_6",
        ],
        "skip_series": {"S_WAY_AS_E3", "S_WAY_AS_E5"},
        "legacy": ["DPFreg1", "DPFreg2", "DPFreg3", "DPFreg4", "DPFreg5"],
    },
    "5c": {
        "name": "5c) Diff pressure of DPF",
        "group_by": ["engine_model", "power", "mileage_range"],
        "trigger": 1,
        "groups": {"EUROCARGO": ["dpf_diff_p_1", "dpf_diff_p_2", "dpf_diff_p_3", "dpf_diff_p_4"]},
        "new_layout": ["dpf_diff_p_1", "dpf_diff_p_2", "dpf_diff_p_3", "dpf_diff_p_4"],
        "skip_series": {"S_WAY_AS_E3", "S_WAY_AS_E5"},
        "legacy": ["deltap_flux_ok1", "deltap_flux_highpr1", "deltap_flux_lowpr1", "deltap_flux_nok1"],
    },
    "5d": {
        "name": "5d Soot mass estimated",
        "group_by": ["engine_model", "mileage_range"],
        "triggers": [0, 0, 1, 1, 1, 1],
        "groups": {
            "EUROCARGO": [
                "soot_mass_0_30",
                "soot_mass_30_60",
                "soot_mass_60_80",
                "soot_mass_80_100",
                "soot_mass_100_150",
                "soot_mass_150_200",
            ]
        },
        "new_layout": [
            "soot_mass_0_30",
            "soot_mass_30_60",
            "soot_mass_60_80",
            "soot_mass_80_100",
            "soot_mass_100_150",
            "soot_mass_150_200",
        ],
        "skip_series": {"S_WAY_AS_E3", "S_WAY_AS_E5"},
        "legacy": ["flowres_soot_1", "flowres_soot_2", "flowres_soot_4"],
    },
    "4g_doc_upstream_temperature": {
        "name": "4g DOC Upstream Temperature",
        "use_percentage_columns": False,
        "columns": ["doc_upstr_t_1", "doc_upstr_t_2", "doc_upstr_t_3", "DOCtemp1", "DOCtemp2", "DOCtemp3"],
        "group_by": ["product_group"],
        "triggers": [1, 0, 1, 1, 0, 1],
        "zero_as_null": True,
        "skip_series": {"S_WAY_AS_E3", "S_WAY_AS_E5"},
    },
    "4h_scr_upstream_temperature": {
        "name": "4h SCR upstream temperature",
        "use_percentage_columns": False,
        "columns": ["scr_upstr_t_1", "scr_upstr_t_2", "scr_upstr_t_3", "SCRuptemp1", "SCRuptemp2", "SCRuptemp3"],
        "group_by": ["product_group"],
        "triggers": [1, 0, 1, 1, 0, 1],
        "zero_as_null": True,
    },
    "4i_scr_downstream_temperature": {
        "name": "4i SCR Downstream Temperature",
        "use_percentage_columns": False,
        "columns": ["scr_dwnstr_t_1", "scr_dwnstr_t_2", "scr_dwnstr_t_3", "SCRdwntemp1", "SCRdwntemp2", "SCRdwntemp3"],
        "group_by": ["product_group"],
        "triggers": [1, 0, 1, 1, 0, 1],
        "zero_as_null": True,
    },
    "6a_engine_brake_status": {
        "name": "6a) Engine brake status",
        "use_percentage_columns": False,
        "columns": [
            "eng_brake_status_1",
            "eng_brake_status_2",
            "eng_brake_status_3",
            "Enginebrakestatus_1",
            "Enginebrakestatus_2",
        ],
        "group_by": ["engine_model", "power", "mileage_range"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "6b_braking_torque": {
        "name": "6b) Braking torque",
        "use_percentage_columns": False,
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
        "group_by": ["engine_model", "power", "mileage_range"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "turbocharger_revolutions": {
        "name": "Turbocharger revolutions",
        "use_percentage_columns": False,
        "columns": [
            "Turbochargerrevolutions_109000",
            "Turbochargerrevolutions_127000",
            "Turbochargerrevolutions_130000",
            "Turbochargerrevolutions_max",
        ],
        "group_by": ["engine_model"],
        "trigger": 1,
        "zero_as_null": True,
    },
}


def normalize_sheet_id(sheet_id):
    return SHEET_ALIASES.get(sheet_id, sheet_id)


def is_new_layout_series(p_series):
    return p_series in NEW_LAYOUT_SERIES or p_series.endswith("_MY_2024")


def get_default_sheet_ids():
    return list(DEFAULT_REPORT_SHEETS)


def get_sheet_settings(sheet_id):
    sheet_id = normalize_sheet_id(sheet_id)
    conf = REPORT_SHEET_CONFIG.get(sheet_id, {})
    return {
        "name": conf.get("name", sheet_id),
        "kind": conf.get("kind", "pivot"),
        "group_by": conf.get("group_by", ["product_group"]),
        "trigger": conf.get("trigger", 1),
        "triggers": conf.get("triggers"),
        "target_columns": conf.get("target_columns"),
        "use_percentage_columns": conf.get("use_percentage_columns", True),
        "zero_as_null": conf.get("zero_as_null", False),
        "max_value": conf.get("max_value"),
    }


def get_columns_for_sheet(p_series, p_group, sheet_id, available_columns=None):
    """Risoluzione colonne con priorita' Series > Group > layout."""
    sheet_id = normalize_sheet_id(sheet_id)
    conf = REPORT_SHEET_CONFIG.get(sheet_id)
    if not conf:
        return []

    if p_series in conf.get("skip_series", set()) or p_group in conf.get("skip_groups", set()):
        return []

    series_cols = conf.get("series", {}).get(p_series)
    if series_cols:
        return series_cols

    group_cols = conf.get("groups", {}).get(p_group)
    if group_cols:
        return group_cols

    if "columns" in conf:
        return conf["columns"]

    if is_new_layout_series(p_series):
        return conf.get("new_layout", [])

    return conf.get("legacy", [])
