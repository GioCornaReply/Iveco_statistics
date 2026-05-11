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
    "catalyst_info",
    "max_values",
    "1a",
    "1b",
    "1c",
    "1d",
    "2a",
    "2b",
    "2c",
    "3a",
    "3a_1",
    "3b",
    "3c",
    "3c_1",
    "3d",
    "3e",
    "3f",
    "4a_1",
    "4a",
    "4b",
    "4c",
    "4d",
    "4e",
    "4f",
    "4h",
    "5a_dpf",
    "5b",
    "5c",
    "5d",
]

REPORT_SHEET_CONFIG = {
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
        "name": "1a) Engine Torque / Engine Speed",
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
        "name": "1b) Engine Torque / Vehicle Speed",
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
        "name": "1c) Engine Revolutions",
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
        "name": "1d) Turbo Overspeed",
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["turb_speed_1", "turb_speed_2", "turb_speed_3", "turb_speed_4"],
        "legacy": ["region1_turborev", "region2_turborev", "region3_turborev"],
    },
    "2a": {
        "name": "2a) Oil Pressure",
        "groups": {"EUROCARGO": ["p_oil_ok_1", "p_oil_tbc", "p_oil_low", "p_oil_low_1"]},
        "new_layout": ["p_oil_ok_1", "p_oil_tbc_1", "p_oil_low_1"],
        "legacy": ["oilpressure_low1", "oilpressure_tocheck1", "oilpressure_ok1"],
    },
    "2b": {
        "name": "2b) Oil Sump Pressure",
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["p_sump_ok_1", "p_sump_tbc_1", "p_sump_crit_1"],
        "legacy": [
            "oilpressuresump_ok1",
            "oilpressuresump_tobechecked1",
            "oilpressuresump_critical1",
        ],
    },
    "2c": {
        "name": "2c) Oil Temperature",
        "groups": {"EUROCARGO": ["oil_t_ok", "oil_t_high"]},
        "new_layout": ["oil_t_ok", "oil_t_high"],
        "legacy": ["oiltemp1", "oiltemp2"],
    },
    "3a": {
        "name": "3a) Coolant Temperature",
        "groups": {"EUROCARGO": ["eng_t_cool_1", "eng_t_cool_2", "eng_t_cool_3"]},
        "new_layout": ["eng_t_cool_1", "eng_t_cool_2", "eng_t_cool_3"],
        "legacy": ["region1_coolantT", "region2_coolantT", "region3_coolantT"],
    },
    "3a_1": {
        "name": "3a.1) Coolant Pressure",
        "columns": ["eng_t_p_cool_1", "eng_t_p_cool_2", "eng_t_p_cool_3", "eng_t_p_cool_4", "eng_t_p_cool_5"],
    },
    "3b": {
        "name": "3b) Fuel Temperature",
        "groups": {"EUROCARGO": ["fuel_t_1", "fuel_t_2", "fuel_t_3"]},
        "new_layout": ["fuel_t_1", "fuel_t_2", "fuel_t_3"],
        "legacy": ["fueltemp1", "fueltemp2", "fueltemp3"],
    },
    "3c": {
        "name": "3c) Intake Air Temperature",
        "groups": {"EUROCARGO": ["int_air_t_1", "int_air_t_2", "int_air_t_3", "int_air_t_4"]},
        "new_layout": ["int_air_t_1", "int_air_t_2", "int_air_t_3", "int_air_t_4"],
    },
    "3c_1": {
        "name": "3c.1) Fuel Pre-Filter Pressure",
        "columns": ["fuel_prefilter_p_low", "fuel_prefilter_p_ok", "fuel_prefilter_p_high"],
    },
    "3d": {
        "name": "3d) Intake Air Pressure",
        "groups": {"EUROCARGO": ["int_air_p_1", "int_air_p_2", "int_air_p_3", "int_air_p_4"]},
        "new_layout": ["int_air_p_1", "int_air_p_2", "int_air_p_3", "int_air_p_4"],
        "legacy": ["EGR_position1", "EGR_position2", "EGR_position3"],
    },
    "3e": {
        "name": "3e) Flap Actuator Position",
        "groups": {
            "EUROCARGO": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"]
        },
        "new_layout": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"],
        "legacy": ["Flap1", "Flap2", "Flap3", "Flap4"],
    },
    "3f": {
        "name": "3f) EGR Actuator Position",
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
        "name": "4a) Catalyst Efficiency",
        "groups": {"EUROCARGO": ["cat_eff_scr_2_a", "cat_eff_scr_2_b", "cat_eff_scr_2_c"]},
        "new_layout": ["cat_eff_scr_2_a", "cat_eff_scr_2_b", "cat_eff_scr_2_c"],
        "legacy": ["regionA_catalyst_BAD", "regionB_catalyst_BAD", "regionCD_catalyst_BAD"],
    },
    "4b": {
        "name": "4b) Catalyst Efficiency vs Engine Speed",
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
        "name": "4c) HC Accumulated in SCR Catalyst",
        "groups": {"EUROCARGO": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"]},
        "new_layout": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"],
        "legacy": ["region1_hc", "region2_hc", "region3_hc", "region4_hc"],
    },
    "4d": {
        "name": "4d) NH3 Concentration",
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
        "name": "5a) DPF Upstream Temperature",
        "groups": {
            "EUROCARGO": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
            "IVECO_X_WAY": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
        },
        "skip_series": NEW_LAYOUT_SERIES,
        "legacy": ["DPFup1", "DPFup2", "DPFup3"],
    },
    "5b": {
        "name": "5b) Regeneration Strategies",
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
        "skip_series": NEW_LAYOUT_SERIES,
        "legacy": ["DPFreg1", "DPFreg2", "DPFreg3", "DPFreg4", "DPFreg5"],
    },
    "5c": {
        "name": "5c) DPF Differential Pressure",
        "groups": {"EUROCARGO": ["dpf_diff_p_1", "dpf_diff_p_2", "dpf_diff_p_3", "dpf_diff_p_4"]},
        "skip_series": NEW_LAYOUT_SERIES,
        "legacy": ["deltap_flux_ok1", "deltap_flux_highpr1", "deltap_flux_lowpr1", "deltap_flux_nok1"],
    },
    "5d": {
        "name": "5d) Soot Mass Estimated",
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
        "skip_series": NEW_LAYOUT_SERIES,
        "legacy": ["flowres_soot_1", "flowres_soot_2", "flowres_soot_4"],
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
        "group_by": conf.get("group_by", ["product_group"]),
        "trigger": conf.get("trigger", 1),
        "use_percentage_columns": conf.get("use_percentage_columns", True),
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
