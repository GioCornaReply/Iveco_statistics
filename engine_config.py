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
    "X_WAY_AT_AD_MY_2024",
    "T_WAY_MY_2024",
}

NP_403_SERIES = "S_WAY_NP_MY_2024"
NP_409_SERIES = "S_WAY_AS_NP_MY22_LATAM"
NP_409_SOURCE_SERIES = "S_WAY_AS_NP_LATAM"
# S-WAY NP MY24 C13 (template 1_template_colonne/template S-WAY_NP_MY24_C13.xlsx).
# Serie normalizzata dal nome template: da confermare sulla fat table 410.
NP_410_SERIES = "S_WAY_NP_MY24_C13"
# La 410 ha la struttura 1a/4a/4d della 409 e le KPI MY24 della 403: riceve entrambi i profili.
NP_409_REPORT_SERIES = (NP_409_SERIES, NP_409_SOURCE_SERIES, NP_410_SERIES)
NP_REPORT_SERIES = (NP_403_SERIES, NP_409_SERIES, NP_409_SOURCE_SERIES, NP_410_SERIES)
# Serie che non devono ricevere i fogli diesel 1a/1a_2 (nome 409 storico).
NP_409_SERIES_ALIASES = set(NP_409_REPORT_SERIES)


def _np_series_columns(columns):
    """Applica la stessa metrica NP alle serie MY24 e S-WAY NP LATAM."""
    return {series: columns for series in NP_REPORT_SERIES}


def _np_409_series_columns(columns):
    """Mappa le colonne della serie LATAM, includendo il nome grezzo del dato."""
    return {series: columns for series in NP_409_REPORT_SERIES}

SHEET_ALIASES = {
    # Nome storico usato nel primo runner locale.
    "5a": "catalyst_info",
}

DEFAULT_REPORT_SHEETS = [
    "complete_dataset",
    "urea_consumption_pct",
    "fuel_lng",
    "fuel_cng",
    "fuel_consumption",
    "fuel_consumption_2",
    "urea_consumption_l100km",
    "urea_consumption_l100km_2",
    "average_vehicle_speed",
    "np_average_vehicle_speed",
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
    "3c_1",
    "3c",
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
    "4g_doc_upstream_temperature",
    "4h_scr_upstream_temperature",
    "4i_scr_downstream_temperature",
    "5a_dpf",
    "5a_dpf_2",
    "5b",
    "5c",
    "5d",
    "6a_engine_brake_status",
    "6b_braking_torque",
    "turbocharger_revolutions",
    "np_engine_lifecycle",
    "np_engine_overspeed",
    "np_catalyst_temperature",
    "np_low_catalyst_efficiency",
    "np_coolant_temperature_high",
    "np_oil_temperature_high",
    "np_boost_pressure_high",
    "np_ambient_pressure_low",
    "np_oil_pressure_low",
    "np_misfire_cylinders",
    "np_1a_1",
    "np_409_1a_2",
    "np_2a",
    "np_2b",
    "np_2c",
    "np_3a",
    "np_3c",
    "np_3e",
    "np_3f",
    "np_3g",
    "np_3h_o_cylinders",
    "np_409_4a_1",
    "np_409_4a_2",
    "np_409_4b",
    "np_4d",
    "np_409_4d",
    "np_5c",
]

VARIABLE_DISPLAY_NAMES = {
    "engineoverspeed_pct": "Engine overspeed [%]",
    "crank_100km_pct": "Average crank per 100 km [%]",
    "engine_on_time": "Engine on time [h]",
    "engine_life_cycle": "Engine Life Cycle [%]",
    "engineoverspeed": "Engine overspeed > 2660 rpm [s]",
    "catalyst_temp_860": "Catalyst temperature > 860 C [min]",
    "low_cat_eff_time": "Time with Low Catalyst Efficiency [min]",
    "low_cat_eff_count": "Low Catalyst Efficiency events [count]",
    "coolant_temp_high_104": "High engine coolant temperature > 104 C [s]",
    "oil_temp_high_120": "High oil temperature > 120 C [s]",
    "boost_pressure_high_25": "High boost pressure > 2.5 bar [min]",
    "ambient_pressure_low_850": "Low ambient pressure < 850 mbar [s]",
    "average_fuel_consumption_kml": "Average fuel consumption LNG [km/l]",
    "average_fuel_consumption_l100km": "Average fuel consumption LNG [l/100km]",
    "tot_fuel_lng": "Total fuel consumption LNG [l]",
    "average_fuel_consumption_cng_kml": "Average fuel consumption CNG [km/l]",
    "average_fuel_consumption_cng_l100km": "Average fuel consumption CNG [l/100km]",
    "tot_fuel_cng": "Total fuel consumption CNG [l]",
    "engine_overspeed_2600_rpm_seconds": "Engine overspeed > 2660 rpm [s]",
    "post_catalyst_temperature_860_minutes": "Post-Catalyst temperature > 860 C [min]",
    "cat_eff_minutes": "Low Catalyst Efficiency time [min]",
    "cat_eff_counter": "Low Catalyst Efficiency events [count]",
    "coolant_temperature_high_104_seconds": "High engine coolant temperature > 104 C [s]",
    "coolant_temperature_high_104_counter": "Coolant temperature > 104 C events [count]",
    "high_oil_temperature_120_seconds": "High oil temperature > 120 C [s]",
    "high_oil_temperature_120_counter": "Oil temperature > 120 C events [count]",
    "high_boost_pressure_minutes": "High boost pressure > 2.5 bar [min]",
    "high_boost_pressure_counter": "High boost pressure events [count]",
    "low_ambient_pressure_seconds": "Low ambient pressure < 850 mbar [s]",
    "low_ambient_pressure_counter": "Low ambient pressure events [count]",
    "oil_pressure_low_12": "Low oil pressure <1.2 bar [min]",
    # Regioni 1a 409: chiavi con suffisso sheet per non rinominare le
    # stesse variabili region*_torque_enginespeed delle config diesel legacy.
    "region3_torque_enginespeed_np_1a_1": "Optimal specific fuel consumption region (50-100 % / 400-1800 rpm)",
    "region4_torque_enginespeed_np_1a_1": "High specific fuel consumption (50-100 % / 1800-2500 rpm)",
    "region1_torque_enginespeed_np_409_1a_2": "Low load, low TVA percentage opening, high specific fuel consumption (0-30 % / 400-2500 rpm)",
    "region2_torque_enginespeed_np_409_1a_2": "High specific fuel consumption (30-50 % / 400-1000 rpm)",
    "region3bis_torque_enginespeed_np_409_1a_2": "Optimal specific fuel consumption region (30-50 % / 1000-1800 rpm)",
    "region4bis_torque_enginespeed_np_409_1a_2": "High specific fuel consumption (30-50 % / 1800-2500 rpm)",
    "misfire_knocking_cylinders_min": "Misfire/Knocking Detection Cylinders (MIN)",
    "misfuel_engine_normal_pct": "Misfuel With Engine In Normal Mode (Driving Conditions, Working Conditions (Pto))",
    "catalyst_temperature_low_pct": "Low Catalyst Temperature (<300 deg C)",
    "catalyst_temperature_over_900_pct": "Catalyst Overheating (900-1000 deg C)",
    "catalyst_upstream_over_900_pct": "Temperature Upstream the Catalyst over 900 deg C",
    "region1_coolantt": "Not optimal coolant temperature [102-107 C]",
    "region2_coolantt": "Critical coolant temperature [>107 C]",
    "oiltemp1": "Oil temperature OK [<120 C]",
    "oiltemp2": "Oil temperature HIGH [120-125 C]",
    "oiltemp3": "Oil temperature VERY HIGH [>125 C]",
    "reg1_intake_temp": "Intake air temperature OK [35-50 C]",
    "reg2_intake_temp": "Intake air temperature [50-65 C]",
    "reg3_intake_temp": "Intake air temperature over 65 C",
    "fueltemp1": "Too cold gas temperature [<-30 C]",
    "fueltemp2": "Cold gas temperature [-30..-10 C]",
    "fueltemp3": "Gas temperature OK [-10..0 C]",
    "fueltemp_magg_0": "Gas temperature [>0 C]",
    "reg1_gas_railpressure": "Gas rail pressure too low [<4500 mbar]",
    "reg2_gas_railpressure": "Gas rail pressure low [4500-5500 mbar]",
    "reg3_gas_railpressure": "Gas rail pressure OK [5500-6500 mbar]",
    "region1_etasp_railpressure": "Lng cold refill / fuel filter clogged / low gas level [800-5500 mbar]",
    "region2_etasp_railpressure": "Fuel filter clogged / fuel line malfunction [5500-7500 mbar]",
    "region3_etasp_railpressure": "Fuel line OK [7500-9500 mbar]",
    "reg1_mixture_selfpoor": "Mixture self-adapting poor OK [1-1.10]",
    "reg2_mixture_selfpoor": "Mixture self-adapting poor [1.10-1.15]",
    "reg3_mixture_selfpoor": "Mixture self-adapting very poor [>1.15]",
    "reg1_mixture_selfrich": "Mixture self-adapting very rich [<0.78]",
    "reg2_mixture_selfrich": "Mixture self-adapting rich [0.78-0.8]",
    "reg3_mixture_selfrich": "Mixture self-adapting rich OK [0.8-1]",
    "reg1_cat_eff": "Catalyst Efficiency [0-50 %]",
    "reg2_cat_eff": "Catalyst Efficiency [50-60 %]",
    "reg3_cat_eff": "Catalyst Efficiency [60-100 %]",
    "reg1_intake_manifoldpressure": "Intake manifold pressure [2000-2300 mbar]",
    "reg2_intake_manifoldpressure": "Intake manifold pressure [2300-2500 mbar]",
    "reg3_intake_manifoldpressure": "Intake manifold pressure over 2500 mbar",
    "tor_rev_cutoff": "Cut off with gear engaged (250-2500 rpm / -15 - 0 %)",
    "tor_rev_low": "Low Load (250-2500 rpm / 0-15%)",
    "tor_rev_lowlow": "Low Load, low engine speed, high specific fuel consumption (250-650 rpm / 15-45 %)",
    "tor_rev_high_1": "High specific fuel consumption (250-650 rpm / 45-110%)",
    "tor_rev_opt": "Optimal specific fuel consumption region (650-1450 rpm / 15-110 %)",
    "tor_rev_highlow": "High speed, low load, not ideal gear, highest specific fuel consumption (1450-2500 rpm / 15-45 %)",
    "tor_rev_high_2": "High specific fuel consumption (1450-2500 rpm / 45-110%)",
    "tor_speed_cutoff": "Cut off with gear engaged (-3 -100 km/h / -15 -0%)",
    "tor_speed_idle": "Low idle (-3 -3 km/h / 0-15%)",
    "tor_speed_pto": "PTO Active, Clima ON, Air leakage in the pneumatic system (-3 -3 km/h / 15-110 %)",
    "tor_speed_hurb": "Heavy urban (3-20 km/h / 0-110%)",
    "tor_speed_urb": "Urban (20-50 km/h / 0-110%)",
    "tor_speed_extrurb": "Extra Urban (50-70 km/h / 0-110%)",
    "tor_speed_highway": "Highway (70-90 km/h / 0-110%)",
    "tor_speed_downhill": "Downhill (90-100 km/h / 0-15%)",
    "tor_speed_overspeedlimit": "Vehicle over speed limit (90-100 km/h / 15-110%)",
    "eng_speed_1": "Low Engine Speed 250-650 [rpm]",
    "eng_speed_2": "Engine Speed OK 650-1450 [rpm]",
    "eng_speed_3": "Rated Speed (Down Speed) 1450-1850 [rpm]",
    "eng_speed_4": "Full Speed with Torque cut 1850-2250 [rpm]",
    "eng_speed_5": "Full Speed with Torque cut 2250-2500 [rpm]",
    "turb_speed_1": "Turbine speed OK 10000-90000 [rpm]",
    "turb_speed_2": "Turbine speed under mechanical limit 90000-103000 [rpm]",
    "turb_speed_3": "Turbine speed over mechanical limit (For biggest turbo) 103000-120000 [rpm]",
    "turb_speed_4": "Turbine speed over mechanical limit (For smallest turbo) 120000-130000 [rpm]",
    "p_oil_low_1": "Oil pressure TOO LOW [bar]",
    "p_oil_ok_1": "Oil pressure OK [bar]",
    "p_oil_ok_2": "Oil pressure OK [bar]",
    "p_oil_tbc_1": "Oil pressure TO BE CHECKED [bar]",
    "p_oil_tbc_2": "Oil pressure TO BE CHECKED [bar]",
    "p_oil_1": "Oil pressure OK 0.20-3.50 [bar]",
    "p_oil_2": "Oil pressure 3.50-4.50 [bar]",
    "p_oil_3": "Oil pressure 4.50-25 [bar]",
    "p_sump_ok_1": "Oil pressure in sump vs engine revolutions OK [bar]",
    "p_sump_ok_2": "Oil pressure in sump vs engine revolutions OK [bar]",
    "p_sump_tbc_1": "Oil pressure in sump vs engine revolutions TO BE CHECKED [bar]",
    "p_sump_tbc_2": "Oil pressure in sump vs engine revolutions TO BE CHECKED [bar]",
    "p_sump_crit_1": "Oil pressure in sump vs engine revolutions CRITICAL AREA [bar]",
    "p_sump_crit_2": "Oil pressure in sump vs engine revolutions CRITICAL AREA [bar]",
    "oil_t_ok": "Oil temperature OK [C]",
    "oil_t_high": "Oil temperature HIGH >125 [C] - power reduction active [C]",
    "eng_t_cool_1": "Optimal temperature -20..106 [C] - Full power",
    "eng_t_cool_2": "Not optimal temperature 106 - 110 [C] - WARNING | Fuel injection cut ACTIVE",
    "eng_t_cool_3": "Critical Temperature 110 - 112 [C] - Fuel injection cut by 50%",
    "eng_t_p_cool_1": "Low coolant pressure in cavitation range 0-0.80 [bar]",
    "eng_t_p_cool_2": "Coolant pressure in operating range 0.80-1.20 [bar]",
    "eng_t_p_cool_3": "Coolant overpressure in high operating range 1.20-1.40 [bar]",
    "eng_t_p_cool_4": "Coolant overpressure 1.40-1.60 [bar]",
    "eng_t_p_cool_5": "Coolant overpressure very critical >1.60 [bar]",
    "eng_p_cool_1": "Coolant pressure in operating range (0..1.50) [bar]",
    "eng_p_cool_2": "Coolant pressure in high operating range (1.50..1.60) [bar]",
    "eng_p_cool_3": "Coolant overpressure (1.60..1.70) [bar]",
    "eng_p_cool_4": "Coolant overpressure very critical (>1.70) [bar]",
    "fuel_t_1": "Fuel temperature OK < 70 [C]",
    "fuel_t_2": "Fuel temperature WARNING 70 - 80 [C] - at maximum 200 hours over entire life",
    "fuel_t_3": "Fuel temperature HIGH WARNING 80 - 90 [C] - at maximum 100 hours over entire life",
    "fuel_prefilter_p_low": "Pressure of fuel pre-filter TOO LOW 0-0.41 [bar]",
    "fuel_prefilter_p_ok": "Pressure of fuel pre-filter OK 0.41-0.80 [bar]",
    "fuel_prefilter_p_high": "Pressure of fuel pre-filter TOO HIGH 0.80-33 [bar]",
    "int_air_t_1": "Intake air temperature < 60 [C]",
    "int_air_t_2": "Intake air temperature 60-70 [C]",
    "int_air_t_3": "Intake air temperature 70-80 [C]",
    "int_air_t_4": "Intake air temperature > 80 [C]",
    "int_air_p_1": "Intake air pressure < 2.20 [bar]",
    "int_air_p_2": "Intake air pressure 2.20 - 2.80 [bar]",
    "int_air_p_3": "Intake air pressure 2.80 - 3.40 [bar]",
    "int_air_p_4": "Intake air pressure > 3.40 [bar]",
    "flap_position_1": "Flap OPEN - flap position between 0 - 25 %",
    "flap_position_2": "Flap partially OPEN - flap position between 25 - 50 %",
    "flap_position_3": "Flap partially CLOSED - flap position between 50 - 75 %",
    "flap_position_4": "Flap CLOSED - flap position between 75 - 100 %",
    "egr_position_1": "EGR actuator between 0 - 40%",
    "egr_position_2": "EGR actuator between 40 - 80 %",
    "egr_position_3": "EGR actuator over 80%",
    "cat_eff_scr_1_a": "REGION A Optimal catalyst efficiency under PEMS limit: 0.01- 0.69 [g/kWh]",
    "cat_eff_scr_1_b": "REGION B Middle/good catalyst efficiency under PEMS limit: 0.69- 1.20 [g/kWh]",
    "cat_eff_scr_1_c": "REGION C Low catalyst efficiency above OBD limit: 1.20-2.00 [g/kWh]",
    "cat_eff_scr_1_d": "REGION D Low/critical catalyst efficiency measured above OBD limit: 2.00-5.00 [g/kWh]",
    "cat_eff_scr_2_a": "REGION A Optimal catalyst efficiency under PEMS limit: 0.01- 0.69 [g/kWh]",
    "cat_eff_scr_2_b": "REGION B Middle/good catalyst efficiency under PEMS limit: 0.69- 1.20 [g/kWh]",
    "cat_eff_scr_2_c": "REGION C-D Low/critical catalyst efficiency measured above OBD limit: 1.20-5.00 [g/kWh]",
    "cat_eff_0_40": "Low Catalyst Efficiency 0-40 [%]",
    "cat_eff_40_65": "Medium-Low Catalyst Efficiency 40-65 [%]",
    "cat_eff_65_90": "Medium-Good Catalyst Efficiency 65-90 [%]",
    "cat_eff_90_100": "Excellent Catalyst Efficiency 90-100 [%]",
    "hc_accum_scr_1": "Low quantity of HC accumulated in the SCR catalyst - No Warning [0-4800 mg/l]",
    "hc_accum_scr_2": "Low/medium quantity of HC accumulated in the SCR catalyst - No Warning [4800-5000 mg/l]",
    "hc_accum_scr_3": "High quantity of HC accumulated in the catalyst [5000-5500 mg/l] - Warning level 1",
    "hc_accum_scr_4": "High quantity of HC accumulated in the catalyst [>5500 mg/l] - Warning level 2",
    "nh3_conc_1": "NH3 concentration OK 0-100 [ppm]",
    "nh3_conc_2": "NH3 concentration medium 100-200 [ppm]",
    "nh3_conc_3": "NH3 concentration medium - high >200 [ppm]",
    "urea_dep_1": "Level 1-2-3 Urea deposit < 0.25",
    "urea_dep_2": "Level 4 Urea deposit 0.25 - 0.50",
    "urea_dep_3": "Level 5 Urea deposit 0.50 - 1",
    "urea_dep_4": "Level 6 Urea deposit 1 - 2",
    "urea_p_1": "No AdBlue injection [0 - 8 bar]",
    "urea_p_2": "AdBlue operating pressure [8 - 10 bar]",
    "urea_p_3": "AdBlue light overpressure [10 - 12 bar]",
    "urea_p_4": "AdBlue overpressure [12 - 20 bar]",
    "doc_upstr_t_1": "Temperature before the oxidation catalyst between 0 - 200 [C]",
    "doc_upstr_t_2": "Temperature before the oxidation catalyst between 200 - 576 [C]",
    "doc_upstr_t_3": "Temperature before the oxidation catalyst > 576 [C] - power reduction active",
    "scr_upstr_t_1": "Temperature before the SCR catalyst between 0 - 200 [C]",
    "scr_upstr_t_2": "Temperature before the SCR catalyst between 200 - 535 [C]",
    "scr_upstr_t_3": "Temperature before the SCR catalyst > 535 [C] - power reduction active",
    "scr_dwnstr_t_1": "Temperature after the SCR catalyst between 0 - 200 [C]",
    "scr_dwnstr_t_2": "Temperature after the SCR catalyst between 200 - 535 [C]",
    "scr_dwnstr_t_3": "Temperature after the SCR catalyst > 535 [C] - power reduction active",
    "dpf_upstr_t_1": "DPF upstream temperature 0 - 200 [C]",
    "dpf_upstr_t_2": "DPF upstream temperature 200 - 550 [C]",
    "dpf_upstr_t_3": "DPF upstream temperature >550 [C]",
    "regen_strategy_1": "No thermal treatment demand",
    "regen_strategy_2": "Level low of DPF clogging, thermal treatment holding due to calculated soot mass",
    "regen_strategy_3": "Level medium of DPF clogging, thermal treatment holding due to calculated soot mass",
    "regen_strategy_4": "Level high of DPF clogging, thermal treatment holding due to calculated soot mass",
    "regen_strategy_5": "Thermal treatment demand due to calculated soot mass",
    "regen_strategy_6": "Thermal treatment demand due to Sox (Sulfure oxides)",
    "dpf_diff_p_1": "Differential pressure of DPF 0-0.06 [bar]",
    "dpf_diff_p_2": "Differential pressure of DPF 0.06-0.08 [bar]",
    "dpf_diff_p_3": "Differential pressure of DPF 0.08-0.10 [bar]",
    "dpf_diff_p_4": "Differential pressure of DPF 0.10-0.20 [bar]",
    "soot_mass_0_30": "Soot mass estimated 0-30 [%]",
    "soot_mass_30_60": "Soot mass estimated 30-60 [%]",
    "soot_mass_60_80": "Soot mass estimated 60-80 [%]",
    "soot_mass_80_100": "Soot mass estimated 80-100 [%]",
    "soot_mass_100_150": "Soot mass estimated 100-150 [%]",
    "soot_mass_150_200": "Soot mass estimated 150-200 [%]",
    "eng_brake_status_1": "Region 1 - Engine brake activation 0-4 bank 1",
    "eng_brake_status_2": "Region 2 - Engine brake activation 4-5 bank 2",
    "eng_brake_status_3": "Region 3 - Engine brake activation >5 bank 1 and 2",
    "brak_torque_req_1": "Low braking torque request (-300..-150 [Nm] /700..1000 [rpm])",
    "brak_torque_req_2": "Braking torque request (yellow zone Nm/rpm)",
    "brak_torque_req_3": "Braking torque request (yellow zone Nm/rpm)",
    "brak_torque_req_4": "Braking torque request (green zone Nm/rpm)",
    "brak_torque_req_5": "Braking torque request (green zone Nm/rpm)",
    "brak_torque_req_6": "Braking torque request (green zone Nm/rpm)",
    "brak_torque_req_7": "High braking torque request (-2200..-1500 [Nm] / >1000 [rpm] and (-1500..-900 [Nm] /1000..1300 [rpm]))",
    "brak_torque_req_8": "High braking torque request (-2200..-1500 [Nm] / >1000 [rpm] and (-1500..-900 [Nm] /1000..1300 [rpm]))",
}


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
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "fuel_consumption_2": {
        "name": "Fuel Consumption 2",
        "use_percentage_columns": False,
        "columns": ["average_fuel_consumption_kml"],
        "group_by": ["product_model", "power", "axle_description", "Average_vehicle_speed_range"],
        "trigger": 0,
        "zero_as_null": True,
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "fuel_lng": {
        "name": "Fuel Consumption LNG",
        "use_percentage_columns": False,
        "series": {
            NP_403_SERIES: [
                "average_fuel_consumption_kml",
                "average_fuel_consumption_l100km",
                "Tot_fuel_LNG",
            ],
            NP_410_SERIES: [
                "average_fuel_consumption_kml",
                "average_fuel_consumption_l100km",
                "Tot_fuel_LNG",
            ],
        },
        "group_by": ["product_model", "power", "axle_description", "mission"],
        "triggers": [0, 0, 0],
        "zero_as_null": True,
    },
    "fuel_cng": {
        "name": "Fuel Consumption CNG",
        "use_percentage_columns": False,
        "series": {
            **_np_series_columns(
                [
                    "average_fuel_consumption_CNG_kml",
                    "average_fuel_consumption_CNG_l100km",
                    "Tot_fuel_CNG",
                ]
            ),
            **_np_409_series_columns(["average_fuel_consumption_CNG_kml"]),
            NP_410_SERIES: [
                "average_fuel_consumption_CNG_kml",
                "average_fuel_consumption_CNG_l100km",
                "Tot_fuel_CNG",
            ],
        },
        "group_by": ["product_model", "power", "axle_description", "mission"],
        "triggers": [0, 0, 0],
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
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "np_average_vehicle_speed": {
        "name": "Average Vehicle Speed",
        "use_percentage_columns": False,
        "series": _np_series_columns(["Average_vehicle_speed"]),
        "group_by": ["Average_vehicle_speed_split"],
        "allowed_group_values": {
            "Average_vehicle_speed_split": ["<20 km/h", "20-40 km/h"],
        },
        "required_group_values": {
            "Average_vehicle_speed_split": ["<20 km/h", "20-40 km/h"],
        },
        "trigger": 0,
        "zero_as_null": True,
    },
    "average_vehicle_speed_2": {
        "name": "Average Vehicle Speed 2",
        "series_names": {
            NP_409_SERIES: "Average Vehicle Speed (2)",
            NP_409_SOURCE_SERIES: "Average Vehicle Speed (2)",
            NP_410_SERIES: "Average Vehicle Speed (2)",
        },
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
        "columns": ["crank_100km_pct"],
        "group_by": ["product_model"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "average_crank_per_100km_2": {
        "name": "Average crank per 100km 2",
        "use_percentage_columns": False,
        "columns": ["crank_100km_pct"],
        "group_by": ["product_group"],
        "trigger": 1,
        "zero_as_null": True,
    },
    "engine_over_speed": {
        "name": "Engine over speed",
        "use_percentage_columns": False,
        "columns": ["engineoverspeed_pct", "vehicleoverspeed"],
        "group_by": ["product_group"],
        "trigger": 1,
        "zero_as_null": True,
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "engine_over_speed_2": {
        "name": "Engine over speed 2",
        "use_percentage_columns": False,
        "columns": ["engineoverspeed_pct", "vehicleoverspeed"],
        "group_by": ["product_model"],
        "trigger": 1,
        "zero_as_null": True,
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
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
    "np_engine_lifecycle": {
        "name": "Engine Life Cycle (%)",
        "series_names": {NP_409_SERIES: "Engine Life Cycle", NP_409_SOURCE_SERIES: "Engine Life Cycle", NP_410_SERIES: "Engine Life Cycle"},
        "use_percentage_columns": False,
        "series": _np_series_columns(["engine_life_cycle"]),
        "group_by": ["mileage_range"],
        "trigger": 0,
        "zero_as_null": False,
    },
    "np_engine_overspeed": {
        "name": "Engine overspeed >2660 rpm",
        "series_names": {NP_409_SERIES: "Engine Overspeed", NP_409_SOURCE_SERIES: "Engine Overspeed", NP_410_SERIES: "Engine Overspeed"},
        "use_percentage_columns": False,
        "series": _np_series_columns(["engineoverspeed"]),
        "group_by": ["engine_model"],
        "trigger": 1,
        "zero_as_null": False,
    },
    "np_catalyst_temperature": {
        "name": "Catalyst temperature >860 C",
        "series_names": {NP_409_SERIES: "Catalyst Temperature", NP_409_SOURCE_SERIES: "Catalyst Temperature", NP_410_SERIES: "Catalyst Temperature"},
        "use_percentage_columns": False,
        "series": _np_series_columns(["Catalyst_temp_860"]),
        "group_by": ["engine_model"],
        "trigger": 1,
        "zero_as_null": False,
    },
    "np_low_catalyst_efficiency": {
        "name": "Low Catalyst Efficiency",
        "use_percentage_columns": False,
        "series": _np_series_columns(["Low_Cat_Eff_time", "Low_Cat_Eff_count"]),
        "group_by": ["engine_model", "mileage_range"],
        "triggers": [1, 1],
        "zero_as_null": False,
    },
    "np_coolant_temperature_high": {
        "name": "High coolant temp >104 C",
        "series_names": {NP_409_SERIES: "Engine Coolant Temperature", NP_409_SOURCE_SERIES: "Engine Coolant Temperature", NP_410_SERIES: "Engine Coolant Temperature"},
        "use_percentage_columns": False,
        "series": _np_series_columns(["Coolant_temp_high_104"]),
        "group_by": ["engine_model"],
        "triggers": [1],
        "zero_as_null": False,
    },
    "np_oil_temperature_high": {
        "name": "High oil temp >120 C",
        "series_names": {NP_409_SERIES: "Oil Temperature (Low, High)", NP_409_SOURCE_SERIES: "Oil Temperature (Low, High)", NP_410_SERIES: "Oil Temperature (Low, High)"},
        "use_percentage_columns": False,
        "series": _np_series_columns(["Oil_temp_high_120"]),
        "group_by": ["engine_model"],
        "triggers": [1],
        "zero_as_null": False,
    },
    "np_boost_pressure_high": {
        "name": "High boost pressure >2.5 bar",
        "series_names": {NP_409_SERIES: "Boost Pressure", NP_409_SOURCE_SERIES: "Boost Pressure", NP_410_SERIES: "Boost Pressure"},
        "use_percentage_columns": False,
        "series": _np_series_columns(["Boost_pressure_high_25"]),
        "group_by": ["engine_model"],
        "triggers": [1],
        "zero_as_null": False,
    },
    "np_ambient_pressure_low": {
        "name": "Low ambient pressure <850 mbar",
        "series_names": {NP_409_SERIES: "Ambient Pressure", NP_409_SOURCE_SERIES: "Ambient Pressure", NP_410_SERIES: "Ambient Pressure"},
        "use_percentage_columns": False,
        "series": _np_series_columns(["Ambient_pressure_low_850"]),
        "group_by": ["product_group"],
        "triggers": [1],
        "zero_as_null": False,
    },
    "np_oil_pressure_low": {
        "name": "Oil Pressure",
        "use_percentage_columns": False,
        "series": _np_series_columns(["Oil_pressure_low_12"]),
        "group_by": ["engine_model", "mileage_range", "mission"],
        "triggers": [1],
        "zero_as_null": False,
    },
    "np_2a": {
        "name": "2a) Engine coolant temperature",
        "series": _np_series_columns(["region1_coolantT", "region2_coolantT"]),
        "group_by": ["engine_model"],
        "triggers": [1, 1],
    },
    "np_2b": {
        "name": "2b) Oil temperature",
        "series": _np_series_columns(["oiltemp1", "oiltemp2", "oiltemp3"]),
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1],
    },
    "np_2c": {
        "name": "2c) Intake air temperature",
        "series": _np_series_columns(
            ["reg1_Intake_Temp", "reg2_Intake_Temp", "reg3_Intake_Temp"]
        ),
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1],
    },
    "np_3a": {
        "name": "3a) Gas temperature",
        "series": {
            **_np_series_columns(["fueltemp1", "fueltemp2", "fueltemp3"]),
            # La 409 CNG ha anche la fascia >0 C: senza, il denominatore
            # esclude quasi tutto il tempo e gonfia le fasce fredde.
            **_np_409_series_columns(
                ["fueltemp1", "fueltemp2", "fueltemp3", "fueltemp_magg_0"]
            ),
        },
        "group_by": ["engine_model"],
        "triggers": [1, 1, 0, 0],
    },
    "np_3c": {
        "name": "3c) Gas rail pressure",
        "series": _np_series_columns(
            [
                "reg1_gas_railpressure",
                "reg2_gas_railpressure",
                "reg3_gas_railpressure",
            ]
        ),
        "group_by": ["engine_model", "mileage_range"],
        "triggers": [1, 1, 0],
    },
    "np_3e": {
        "name": "3e) ETAS | Rail pressure",
        "series_names": {
            NP_409_SERIES: "3e ETAS | Rail Pressure",
            NP_409_SOURCE_SERIES: "3e ETAS | Rail Pressure",
            NP_410_SERIES: "3e ETAS | Rail Pressure",
        },
        "series": _np_series_columns(
            [
                "region1_etasp_railpressure",
                "region2_etasp_railpressure",
                "region3_etasp_railpressure",
            ]
        ),
        "group_by": ["engine_model", "mileage_range"],
        "triggers": [1, 1, 0],
        "zero_as_null": False,
    },
    "np_3f": {
        "name": "3f) Mixture self-adapt poor",
        "series": _np_series_columns(
            [
                "reg1_Mixture_selfpoor",
                "reg2_Mixture_selfpoor",
                "reg3_Mixture_selfpoor",
            ]
        ),
        "group_by": ["engine_model", "mileage_range"],
        "triggers": [0, 1, 1],
    },
    "np_3g": {
        "name": "3g) Mixture self-adapt rich",
        "series": _np_series_columns(
            [
                "reg1_Mixture_selfrich",
                "reg2_Mixture_selfrich",
                "reg3_Mixture_selfrich",
            ]
        ),
        "group_by": ["engine_model", "mileage_range"],
        "triggers": [1, 1, 0],
    },
    "np_misfire_cylinders": {
        "name": "Misfire-Knocking Detection Cyl",
        "use_percentage_columns": False,
        "series": _np_series_columns(["misfire_knocking_cylinders_min"]),
        "group_by": ["engine_model", "mileage_range"],
        "triggers": [1],
        "zero_as_null": False,
    },
    # La 1a della 409 arriva da due tag Fly Recorder diversi: le percentuali
    # vanno calcolate separatamente per tag, quindi un foglio per tag.
    "np_1a_1": {
        "name": "1a_1 EngineTorque | EngineSpeed",
        "series": _np_409_series_columns(
            ["region3_torque_enginespeed", "region4_torque_enginespeed"]
        ),
        "group_by": ["engine_model", "power", "mission"],
        "triggers": [0, 1],
        "zero_as_null": False,
    },
    "np_409_1a_2": {
        "name": "1a_2 EngineTorque | EngineSpeed",
        "series": _np_409_series_columns(
            [
                "region1_torque_enginespeed",
                "region2_torque_enginespeed",
                "region3bis_torque_enginespeed",
                "region4bis_torque_enginespeed",
            ]
        ),
        "group_by": ["engine_model", "power", "mission"],
        "triggers": [1, 1, 0, 1],
        "zero_as_null": False,
    },
    "np_3h_o_cylinders": {
        "name": "3h-o Cylinders",
        "use_percentage_columns": False,
        "series": _np_409_series_columns(["misfuel_engine_normal_pct"]),
        "group_by": ["engine_model", "mileage_range", "mission"],
        "triggers": [1],
        "zero_as_null": False,
    },
    "np_409_4a_1": {
        "name": "4a_1 CatalystTemp | EngineSpeed",
        "use_percentage_columns": False,
        "series": _np_409_series_columns(["catalyst_temperature_over_900_pct"]),
        "group_by": ["engine_model"],
        "triggers": [1],
        "zero_as_null": False,
    },
    "np_409_4a_2": {
        "name": "4a_2 CatalystTemp | EngineSpeed",
        "use_percentage_columns": False,
        "series": _np_409_series_columns(["catalyst_temperature_low_pct"]),
        "group_by": ["engine_model"],
        "triggers": [1],
        "zero_as_null": False,
    },
    "np_409_4b": {
        "name": "4b Catalyst Upstream Temp",
        "use_percentage_columns": False,
        "series": _np_409_series_columns(["catalyst_upstream_over_900_pct"]),
        "group_by": ["engine_model"],
        "triggers": [1],
        "zero_as_null": False,
    },
    "np_4d": {
        "name": "4d) Catalyst Efficiency",
        "series": _np_series_columns(["reg1_Cat_Eff", "reg2_Cat_Eff", "reg3_Cat_Eff"]),
        "group_by": ["engine_model", "mileage_range"],
        "triggers": [0, 1, 1],
        "skip_series": NP_409_SERIES_ALIASES,
    },
    "np_409_4d": {
        "name": "4d Catalyst Efficiency C13",
        "use_percentage_columns": True,
        "series": _np_409_series_columns(["reg1_Cat_Eff", "reg2_Cat_Eff", "reg3_Cat_Eff"]),
        "group_by": ["engine_model", "mileage_range"],
        "triggers": [0, 1, 1],
        "zero_as_null": False,
    },
    "np_5c": {
        "name": "5c) Intake manifold pressure",
        "series": _np_series_columns(
            [
                "reg1_Intake_manifoldpressure",
                "reg2_Intake_manifoldpressure",
                "reg3_Intake_manifoldpressure",
            ]
        ),
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1],
    },
    "1a": {
        "name": "1a) Engine Torque-Speed",
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
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "1a_2": {
        "name": "1a_2) Engine Torque-Speed",
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
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "1b": {
        "name": "1b) Engine Torque-Veh Speed",
        "group_by": ["engine_model", "power", "mission"],
        "triggers": [0, 1, 1, 1, 1, 0, 0, 0, 1],
        # 410: le 5 regioni del template (triggers posizionali, primi 5).
        "series": {
            NP_410_SERIES: [
                "region1_torque_vehiclespeed",
                "region2_torque_vehiclespeed",
                "region3_torque_vehiclespeed",
                "region4_torque_vehiclespeed",
                "region5_torque_vehiclespeed",
            ]
        },
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
        "skip_series": {NP_403_SERIES},
    },
    "1c": {
        "name": "1c) Engine revolutions",
        "group_by": ["engine_model"],
        "triggers": [1, 0, 1, 1, 1],
        # 410: OK / medium / high del template (triggers posizionali, primi 3).
        "series": {
            NP_410_SERIES: [
                "engine_revolutions_OK",
                "engine_revolutions_medium",
                "engine_revolutions_high",
            ]
        },
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
        "name": "1c_2) Engine revolutions",
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
        "name": "1d) Turbine Overspeed",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["turb_speed_1", "turb_speed_2", "turb_speed_3", "turb_speed_4"],
        "legacy": ["region1_turborev", "region2_turborev", "region3_turborev"],
    },
    "2a": {
        "name": "2a) Oil Pressure Analysis",
        "series_names": {"S_WAY_AT_AD_MY_2024": "2a_1) Oil pressure"},
        "group_by": ["engine_model", "mission"],
        "triggers": [0, 1, 1],
        "groups": {"EUROCARGO": ["p_oil_ok_1", "p_oil_tbc", "p_oil_low", "p_oil_low_1"]},
        "series": {"S_WAY_AT_AD_MY_2024": ["p_oil_1", "p_oil_2", "p_oil_3"]},
        "new_layout": ["p_oil_ok_1", "p_oil_tbc_1", "p_oil_low_1"],
        "legacy": ["oilpressure_low1", "oilpressure_tocheck1", "oilpressure_ok1"],
        "skip_series": {NP_403_SERIES},
    },
    "2b": {
        "name": "2b) Oil sump pressure analysis",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1],
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["p_sump_ok_1", "p_sump_tbc_1", "p_sump_crit_1"],
        "legacy": [
            "oilpressuresump_ok1",
            "oilpressuresump_tobechecked1",
            "oilpressuresump_critical1",
        ],
        "skip_series": {NP_403_SERIES},
    },
    "2c": {
        "name": "2c) Oil temperature",
        "group_by": ["engine_model"],
        "triggers": [0, 1],
        "groups": {"EUROCARGO": ["oil_t_ok", "oil_t_high"]},
        "new_layout": ["oil_t_ok", "oil_t_high"],
        "legacy": ["oiltemp1", "oiltemp2"],
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "3a": {
        "name": "3a) Coolant Temperature",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1],
        "groups": {"EUROCARGO": ["eng_t_cool_1", "eng_t_cool_2", "eng_t_cool_3"]},
        "new_layout": ["eng_t_cool_1", "eng_t_cool_2", "eng_t_cool_3"],
        "legacy": ["region1_coolantT", "region2_coolantT", "region3_coolantT"],
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "3a_1": {
        "name": "3a_1) Coolant temp-pressure",
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
        "name": "3b) Fuel Temperature",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1],
        "groups": {"EUROCARGO": ["fuel_t_1", "fuel_t_2", "fuel_t_3"]},
        "new_layout": ["fuel_t_1", "fuel_t_2", "fuel_t_3"],
        "legacy": ["fueltemp1", "fueltemp2", "fueltemp3"],
        # La 410 eredita fuel_t_1..3 dalla 403: escluse solo le serie 409.
        "skip_series": {NP_409_SERIES, NP_409_SOURCE_SERIES},
    },
    "3c": {
        "name": "3d) Intake air temperature",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["int_air_t_1", "int_air_t_2", "int_air_t_3", "int_air_t_4"]},
        "new_layout": ["int_air_t_1", "int_air_t_2", "int_air_t_3", "int_air_t_4"],
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "3c_1": {
        "name": "3c) Fuel pre-filter pressure",
        "columns": ["fuel_prefilter_p_low", "fuel_prefilter_p_ok", "fuel_prefilter_p_high"],
        "group_by": ["engine_model"],
        "triggers": [0, 1, 0],
    },
    "3d": {
        "name": "3e) Intake air pressure",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["int_air_p_1", "int_air_p_2", "int_air_p_3", "int_air_p_4"]},
        "new_layout": ["int_air_p_1", "int_air_p_2", "int_air_p_3", "int_air_p_4"],
        "legacy": ["EGR_position1", "EGR_position2", "EGR_position3"],
    },
    "3e": {
        "name": "3f) Flap actuator position",
        "group_by": ["engine_model", "mission"],
        "triggers": [0, 1, 1, 1],
        "groups": {
            "EUROCARGO": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"]
        },
        "new_layout": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"],
        "legacy": ["Flap1", "Flap2", "Flap3", "Flap4"],
    },
    "3e_2": {
        "name": "3f_2) Flap actuator position",
        "group_by": ["engine_model", "power", "mission"],
        "triggers": [0, 1, 1, 1],
        "groups": {
            "EUROCARGO": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"]
        },
        "new_layout": ["flap_position_1", "flap_position_2", "flap_position_3", "flap_position_4"],
        "legacy": ["Flap1", "Flap2", "Flap3", "Flap4"],
    },
    "3f": {
        "name": "3g) EGR actuator position",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["egr_position_1", "egr_position_2", "egr_position_3"],
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "4a_1": {
        "name": "4a_1) Catalyst eff [g-kWh]",
        "groups": {
            "EUROCARGO": ["cat_eff_scr_1_a", "cat_eff_scr_1_b", "cat_eff_scr_1_c", "cat_eff_scr_1_d"]
        },
        "new_layout": ["cat_eff_scr_1_a", "cat_eff_scr_1_b", "cat_eff_scr_1_c", "cat_eff_scr_1_d"],
    },
    "4a": {
        "name": "4a_2) Catalyst eff [g-kWh]",
        "group_by": ["engine_model", "power", "mileage_range"],
        "triggers": [0, 1, 1],
        "groups": {"EUROCARGO": ["cat_eff_scr_2_a", "cat_eff_scr_2_b", "cat_eff_scr_2_c"]},
        "new_layout": ["cat_eff_scr_2_a", "cat_eff_scr_2_b", "cat_eff_scr_2_c"],
        "legacy": ["regionA_catalyst_BAD", "regionB_catalyst_BAD", "regionCD_catalyst_BAD"],
    },
    "4b": {
        "name": "4b) Catalyst eff vs Eng Speed",
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
        "name": "4c) HC in SCR catalyst",
        "group_by": ["product_group"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"]},
        "new_layout": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"],
        "legacy": ["region1_hc", "region2_hc", "region3_hc", "region4_hc"],
    },
    "4c_2": {
        "name": "4c_2) HC in SCR catalyst",
        "group_by": ["product_group"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"]},
        "new_layout": ["hc_accum_scr_1", "hc_accum_scr_2", "hc_accum_scr_3", "hc_accum_scr_4"],
        "legacy": ["region1_hc", "region2_hc", "region3_hc", "region4_hc"],
    },
    "4d": {
        "name": "4d) NH3 concentration",
        "group_by": ["engine_model"],
        "triggers": [0, 1, 1, 1],
        "groups": {"EUROCARGO": ["urea_dep_1", "urea_dep_2", "urea_dep_3", "urea_dep_4"]},
        "new_layout": ["nh3_conc_1", "nh3_conc_2", "nh3_conc_3"],
        "legacy": ["region1_NH3", "region2_NH3", "regipn3_NH3"],
        "skip_series": {NP_403_SERIES, *NP_409_SERIES_ALIASES},
    },
    "4e": {
        "name": "4e) Urea deposit accumulation",
        "group_by": ["engine_model", "mission"],
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["urea_dep_1", "urea_dep_2", "urea_dep_3", "urea_dep_4"],
        "legacy": ["adblue_deposit1", "adblue_deposit2", "adblue_deposit3", "adblue_deposit4"],
    },
    "4f": {
        "name": "4f) AdBlue pressure pump",
        "skip_groups": {"EUROCARGO"},
        "new_layout": ["urea_p_1", "urea_p_2", "urea_p_3", "urea_p_4"],
        "legacy": ["adbluepressure1", "adbluepressure2", "adbluepressure3", "adbluepressure4"],
    },
    "4h": {
        "name": "4h) SCR Downstream Temperature",
        "groups": {"EUROCARGO": ["scr_dwnstr_t_1", "scr_dwnstr_t_2", "scr_dwnstr_t_3"]},
        "new_layout": ["scr_dwnstr_t_1", "scr_dwnstr_t_2", "scr_dwnstr_t_3"],
        "legacy": ["SCRdwntemp1", "SCRdwntemp2", "SCRdwntemp3"],
    },
    "5a_dpf": {
        "name": "5a) DPF upstream temperature",
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
        "name": "5a_2) DPF upstream temp",
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
        "name": "5b) Regeneration strategies",
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
        "name": "5c) DPF differential pressure",
        "group_by": ["engine_model", "power", "mileage_range"],
        "trigger": 0,
        "groups": {"EUROCARGO": ["dpf_diff_p_1", "dpf_diff_p_2", "dpf_diff_p_3", "dpf_diff_p_4"]},
        "new_layout": ["dpf_diff_p_1", "dpf_diff_p_2", "dpf_diff_p_3", "dpf_diff_p_4"],
        "skip_series": {
            "S_WAY_AS_E3",
            "S_WAY_AS_E5",
            NP_403_SERIES,
            *NP_409_SERIES_ALIASES,
        },
        "legacy": ["deltap_flux_ok1", "deltap_flux_highpr1", "deltap_flux_lowpr1", "deltap_flux_nok1"],
    },
    "5d": {
        "name": "5d) Soot mass estimated",
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
        "name": "4g) DOC upstream temperature",
        "use_percentage_columns": True,
        "columns": ["doc_upstr_t_1", "doc_upstr_t_2", "doc_upstr_t_3", "DOCtemp1", "DOCtemp2", "DOCtemp3"],
        "group_by": ["product_group"],
        "triggers": [1, 0, 1, 1, 0, 1],
        "zero_as_null": False,
        "skip_series": {"S_WAY_AS_E3", "S_WAY_AS_E5"},
    },
    "4h_scr_upstream_temperature": {
        "name": "4h) SCR upstream temperature",
        "use_percentage_columns": True,
        "columns": ["scr_upstr_t_1", "scr_upstr_t_2", "scr_upstr_t_3", "SCRuptemp1", "SCRuptemp2", "SCRuptemp3"],
        "group_by": ["product_group"],
        "triggers": [1, 0, 1, 1, 0, 1],
        "zero_as_null": False,
    },
    "4i_scr_downstream_temperature": {
        "name": "4i) SCR downstream temperature",
        "use_percentage_columns": True,
        "columns": ["scr_dwnstr_t_1", "scr_dwnstr_t_2", "scr_dwnstr_t_3", "SCRdwntemp1", "SCRdwntemp2", "SCRdwntemp3"],
        "group_by": ["product_group"],
        "triggers": [1, 0, 1, 1, 0, 1],
        "zero_as_null": False,
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
        "zero_as_null_exclude": ["Turbochargerrevolutions_130000"],
    },
}

# Daily MY24 diesel (config 382/384, F1A 6.4.1 e F1C 6.4.2).
# Fonte: catalogo "TABLES AND PROGRESS BAR" dei template in 382_384_daily_disel/
# (non tracciato). Le variabili tecniche sono identiche fra F1A e F1C; cambiano
# solo le soglie rpm nelle descrizioni (qui usate quelle F1C 6.4.2). La
# separazione F1A/F1C avviene tramite engine_model (derivato da product_model).
DAILY_MY24_SERIES = "DAILY_MY24"
DAILY_SHEET_PREFIX = "daily_"
DAILY_MY24_CATALOG = {
    "1a": (
        "1a) Engine Speed-Torque",
        [
            ("rev_tor_idle", "Low idle -15..15 [%] / 600..900 [rpm]"),
            ("rev_tor_cutoff", "Cut off range -15..0 [%] / 900.. 4200 [rpm]"),
            ("rev_tor_extrlow", "Extreme Low load -15..0 [%] / 900..4200 [rpm]"),
            ("rev_tor_low", "Low load 15..30 [%] / 600.. 4200 [rpm]"),
            ("rev_tor_opt", "Optimal consumption 30..60 [%] / 600..2400 [rpm]"),
            ("rev_tor_tor", "High torque request 90..110 [%] / 600..2850 [rpm]"),
            ("rev_tor_high", "High fuel consumption 30..110 [%] / 2850..4200 [rpm]"),
        ],
    ),
    "1b": (
        "1b) Vehicle speed distribution",
        [
            ("speed_1_20", "Vehicle speed 1..20 [km/h]"),
            ("speed_20_40", "Vehicle speed 20..40 [km/h]"),
            ("speed_40_60", "Vehicle speed 40..60 [km/h]"),
            ("speed_60_80", "Vehicle speed 60..80 [km/h]"),
            ("speed_80_100", "Vehicle speed 80..100 [km/h]"),
            ("speed_100_120", "Vehicle speed 100..120 [km/h]"),
            ("speed_120_140", "Vehicle speed 120..140 [km/h]"),
            ("speed_140_160", "Vehicle speed 140..160 [km/h]"),
        ],
    ),
    "1c": (
        "1c) Engine Torque request",
        [
            ("torque_15_30", "Low Engine torque request -15..30 [%]"),
            ("torque_30_60", "Medium-low Engine torque request 30..60 [%]"),
            ("torque_60_90", "Medium-High Engine torque request 60..90 [%]"),
            ("torque_90_110", "High Engine torque request 90..110 [%]"),
        ],
    ),
    "1d": (
        "1d) Engine over speed",
        [
            ("eng_rev_1", "Region 1 Engine Speed OK (4200-4300 rpm)"),
            ("eng_rev_2", "Region 2 Engine Speed under mechanical limit (4300-4400 rpm)"),
            ("eng_rev_3", "Region 3 Engine Speed (4400-5000 rpm)"),
        ],
    ),
    "2a": (
        "2a) Oil Pressure",
        [
            ("p_oil_opt", "Optimal oil pressure"),
            ("p_oil_not_opt_low", "Not optimal oil pressure - low speed/ low pressure"),
            ("p_oil_not_opt_high", "Not optimal oil pressure - high speed/ high pressure"),
            ("p_oil_critic", "Oil pressure very low - high severity"),
        ],
    ),
    "3a": (
        "3a) Engine coolant Temperature",
        [
            ("eng_t_cool_1", "Region 1 Engine coolant temperature (-30 - 0 deg C)"),
            ("eng_t_cool_2", "Region 2 Engine coolant temperature (0 - 100 deg C)"),
            ("eng_t_cool_3", "Region 3 Engine coolant temperature (100 - 110 deg C)"),
            ("eng_t_cool_4", "Region 4 Engine coolant temperature (110 - 120 deg C)"),
            ("eng_t_cool_5", "Region 5 Engine coolant temperature (120 - 130 deg C)"),
        ],
    ),
    "3b": (
        "3b) Fuel Temperature",
        [
            ("fuel_t_1", "Region 1 Fuel temperature (40-70 deg C)"),
            ("fuel_t_2", "Region 2 Fuel temperature (70-90 deg C)"),
            ("fuel_t_3", "Region 3 Fuel temperature (90-100 deg C)"),
        ],
    ),
    "3c": (
        "3c) Input air T air-flow meter",
        [
            ("in_air_t_meter_1", "Region 1 Input air temperature to air-flow meter (-30 - -10 deg C)"),
            ("in_air_t_meter_2", "Region 2 Input air temperature to air-flow meter (-10 - 0 deg C)"),
            ("in_air_t_meter_3", "Region 3 Input air temperature to air-flow meter (0 - 50 deg C)"),
            ("in_air_t_meter_4", "Region 4 Input air temperature to air-flow meter (50 - 70 deg C)"),
        ],
    ),
    "3d": (
        "3d) Intake air temperature",
        [
            ("int_air_t_1", "Region 1 Intake air temperature (50-70 deg C)"),
            ("int_air_t_2", "Region 2 Intake air temperature (70-80 deg C)"),
            ("int_air_t_3", "Region 3 Intake air temperature (80-100 deg C)"),
            ("int_air_t_4", "Region 4 Intake air temperature (100-130 deg C)"),
        ],
    ),
    "4a": (
        "4a) Catalyst Eff NOx [g-kWh]",
        [
            ("nox_em_a", "REGION A (Optimal catalyst efficiency under PEMS limit: 0 -0.69 g/kWh)"),
            ("nox_em_b", "REGION B (Middle/good catalyst efficiency under PEMS limit: 0.69- 1.20 g/kWh)"),
            ("nox_em_c", "REGION C (Low/critical catalyst efficiency measured above OBD limit: 1.2 - 5 g/kWh)"),
        ],
    ),
    "4b": (
        "4b) Cat Eff vs T upstream DPF",
        [
            ("cat_eff_dpf_90_100", "Excellent Catalyst Efficiency 90-100 %"),
            ("cat_eff_dpf_70_90", "Medium-Good Catalyst Efficiency 70-90 %"),
            ("cat_eff_dpf_50_70", "Medium-Low Catalyst Efficiency 50-70 %"),
            ("cat_eff_dpf_0_50", "Low Catalyst Efficiency 0-50 %"),
        ],
    ),
    "4c": (
        "4c) Cat Eff vs T upstream SCR",
        [
            ("cat_eff_scr_90_100", "Excellent Catalyst Efficiency 90-100 %"),
            ("cat_eff_scr_70_90", "Medium-Good Catalyst Efficiency 70-90 %"),
            ("cat_eff_scr_50_70", "Medium-Low Catalyst Efficiency 50-70 %"),
            ("cat_eff_scr_0_50", "Low Catalyst Efficiency 0-50 %"),
        ],
    ),
    "4d": (
        "4d) SCR upstream temperature",
        [
            ("scr_upstr_t_1", "Region 1 SCR Upstream Temperature 400-700 [deg C]"),
            ("scr_upstr_t_2", "Region 2 SCR Upstream Temperature 700-800 [deg C]"),
            ("scr_upstr_t_3", "Region 3 SCR Upstream Temperature 800-900 [deg C]"),
        ],
    ),
    "4e": (
        "4e) SCR downstream temp",
        [
            ("scr_dwnstr_t_1", "Region 1 SCR Downstream Temperature 400-700 [deg C]"),
            ("scr_dwnstr_t_2", "Region 2 SCR Downstream Temperature 700-800 [deg C]"),
            ("scr_dwnstr_t_3", "Region 3 SCR Downstream Temperature 800-900 [deg C]"),
        ],
    ),
    "5b": (
        "5b) DPF Flow Resistance",
        [
            ("dpf_flow_res_1", "Region 1 Flow resistance 0.50 - 0.60 [hPa/(m^3/h]"),
            ("dpf_flow_res_2", "Region 2 Flow resistance 0.60 - 0.80 [hPa/(m^3/h]"),
            ("dpf_flow_res_3", "Region 3 Flow resistance 0.80 - 1 [hPa/(m^3/h]"),
            ("dpf_flow_res_4", "Region 4 Flow resistance 1 - 1.20 [hPa/(m^3/h]"),
        ],
    ),
    "5c": (
        "5c) DPF Differential pressure",
        [
            ("dpf_diff_p_1", "Region 1 DPF Differential pressure 0-0.20 [bar]"),
            ("dpf_diff_p_2", "Region 2 DPF Differential pressure 0.20-0.40 [bar]"),
            ("dpf_diff_p_3", "Region 3 DPF Differential pressure 0.40-0.50 [bar]"),
            ("dpf_diff_p_4", "Region 4 DPF Differential pressure 0.50-0.60 [bar]"),
        ],
    ),
    "5d": (
        "5d) DPF upstream temperature",
        [
            ("dpf_upstr_t_400_600", "DPF upstream Temperature (400-600 deg C)"),
            ("dpf_upstr_t_600_800", "DPF upstream Temperature (600-800 deg C)"),
            ("dpf_upstr_t_800_900", "DPF upstream Temperature (800-900 deg C)"),
        ],
    ),
    "5e": (
        "5e) DPF downstream temp",
        [
            ("dpf_dwnstr_t_400_600", "DPF Downstream Temperature (400-600 deg C)"),
            ("dpf_dwnstr_t_600_800", "DPF Downstream Temperature (600-800 deg C)"),
            ("dpf_dwnstr_t_800_900", "DPF Downstream Temperature (800-900 deg C)"),
        ],
    ),
    "5f": (
        "5f) DOC upstream temperature",
        [
            ("doc_upstr_t_0_200", "DOC upstream Temperature (0-200 deg C)"),
            ("doc_upstr_t_200_500", "DOC upstream Temperature (200-500 deg C)"),
            ("doc_upstr_t_500_600", "DOC upstream Temperature (500-600 deg C)"),
        ],
    ),
    "5g": (
        "5g) AdBlue Pressure Pump",
        [
            ("adblue_p_1", "Region 1 AdBlue Pump Pressure 5-6.5 [bar]"),
            ("adblue_p_2", "Region 2 AdBlue Pump Pressure 6.5-7.5 [bar]"),
            ("adblue_p_3", "Region 3 AdBlue Pump Pressure 7.5-8.5 [bar]"),
        ],
    ),
    "5h": (
        "5h) AdBlue tank temperature",
        [
            ("adblue_t_1", "Region 1 - AdBlue tank temperature -30.. -11 [deg C]"),
            ("adblue_t_2", "Region 2 - AdBlue tank temperature -11..0 [deg C]"),
            ("adblue_t_3", "Region 3 - AdBlue tank temperature 0-30 [deg C]"),
            ("adblue_t_4", "Region 4 - AdBlue tank temperature 30-50 [deg C]"),
        ],
    ),
    "6a": (
        "6a) Battery voltage",
        [
            ("batt_volt_7_11", "Critical Voltage region 7-11 [Volt]"),
            ("batt_volt_11_12", "Nominal Voltage region 11-12 [Volt]"),
            ("batt_volt_12_15", "Optimal Voltage region 12-15 [Volt]"),
        ],
    ),
    "6b": (
        "6b) Battery SOC",
        [
            ("batt_soc_0_60", "Critical SOC region 0-60 [%]"),
            ("batt_soc_60_75", "Nominal SOC region 60-75 [%]"),
            ("batt_soc_75_100", "Optimal SOC region 75-100 [%]"),
        ],
    ),
}

# Missione Daily (fasce diverse dall'Heavy), da MT_DAILY_PREP: colonna dedicata
# `mission_daily`, mostrata con header "Mission".
DAILY_MISSION_LABELS = [
    "< 15 km/h HEAVY URBAN",
    "15 – 25 km/h URBAN",
    "25 - 45 km/h MIX",
    "> 45 LONG RANGE",
]
DAILY_FUEL_KML_COLUMN = "average_fuel_consumption_kml"
DAILY_FUEL_KML_ALIAS = "average_fuel_consumption_kml_daily"

# Gruppi di raggruppamento per sheet Daily: default engine_model + mission,
# sheet legati a km/usura con mileage_range.
DAILY_MY24_GROUP_BY = {
    "default": ["engine_model", "mission"],
    "4a": ["engine_model", "mileage_range"],
    "4b": ["engine_model", "mileage_range"],
    "4c": ["engine_model", "mileage_range"],
    "5b": ["engine_model", "mileage_range"],
    "5c": ["engine_model", "mileage_range"],
    "5d": ["engine_model", "mileage_range"],
}

# Report "LIGHT" 382/384 (esempio Statistics_LIGHT_382_384_Daily_MY_2024_new_thresholds):
# (sheet_id, nome sheet, suffisso catalogo, group_by, motore, usa item name come header).
# 1a/1c sono divisi per motore con header = nome tecnico variabile; la batteria e'
# raggruppata per mileage_split con gli item name del template.
DAILY_MY24_LIGHT_SHEETS = [
    ("daily_light_1a_f1a", "Engine Speed vs Torque F1A", "1a", ["engine_model", "power"], "F1A", False),
    ("daily_light_1a_f1c", "Engine Speed vs Torque F1C", "1a", ["engine_model", "power"], "F1C", False),
    ("daily_light_1c_f1a", "Engine Torque F1A", "1c", ["engine_model", "power"], "F1A", False),
    ("daily_light_1c_f1c", "Engine Torque F1C", "1c", ["engine_model", "power"], "F1C", False),
    ("daily_light_6a", "Battery Voltage", "6a", ["mileage_split"], None, True),
    ("daily_light_6b", "Battery SOC", "6b", ["mileage_split"], None, True),
]
# Il template 6a/6b usa il doppio spazio dopo "region" (mantenuto nell'header Excel).
DAILY_MY24_RAW_ITEM_NAMES = {
    "Critical Voltage region 7-11 [Volt]": "Critical Voltage region  7-11 [Volt]",
    "Nominal Voltage region 11-12 [Volt]": "Nominal Voltage region  11-12 [Volt]",
    "Optimal Voltage region 12-15 [Volt]": "Optimal Voltage region  12-15 [Volt]",
    "Critical SOC region 0-60 [%]": "Critical SOC region  0-60 [%]",
    "Nominal SOC region 60-75 [%]": "Nominal SOC region  60-75 [%]",
    "Optimal SOC region 75-100 [%]": "Optimal SOC region  75-100 [%]",
}


def _register_daily_my24_sheets():
    # Consumo medio km/l per motore/modello/potenza/asse/missione (primo sheet Daily).
    REPORT_SHEET_CONFIG["daily_fuel_kml_2"] = {
        "name": "Fuel Consumption km_l 2",
        "series": {DAILY_MY24_SERIES: [DAILY_FUEL_KML_COLUMN]},
        "use_percentage_columns": False,
        "group_by": ["engine_model", "product_model", "power", "axle_description", "mission_daily"],
        "trigger": 0,
        "zero_as_null": True,
        # Il nome generico e' la descrizione LNG: qui serve l'header diesel.
        "rename_columns": {DAILY_FUEL_KML_COLUMN: DAILY_FUEL_KML_ALIAS},
    }
    DEFAULT_REPORT_SHEETS.append("daily_fuel_kml_2")
    VARIABLE_DISPLAY_NAMES[DAILY_FUEL_KML_ALIAS] = "Average fuel consumption [km/l]"

    # Catalogo completo (opt-in: non nei sheet di default).
    for suffix, (sheet_name, items) in DAILY_MY24_CATALOG.items():
        sheet_id = f"{DAILY_SHEET_PREFIX}{suffix}"
        REPORT_SHEET_CONFIG[sheet_id] = {
            "name": sheet_name,
            "series": {DAILY_MY24_SERIES: [variable for variable, _ in items]},
            "group_by": DAILY_MY24_GROUP_BY.get(suffix, DAILY_MY24_GROUP_BY["default"]),
            "trigger": 1,
        }
        for variable, item_name in items:
            # Chiave con suffisso sheet: non sovrascrive le descrizioni Heavy.
            VARIABLE_DISPLAY_NAMES[f"{variable}_{sheet_id}".lower()] = item_name

    # Report LIGHT: sheet di default per la serie Daily.
    for sheet_id, sheet_name, suffix, group_by, engine, use_item_names in DAILY_MY24_LIGHT_SHEETS:
        items = DAILY_MY24_CATALOG[suffix][1]
        conf = {
            "name": sheet_name,
            "series": {DAILY_MY24_SERIES: [variable for variable, _ in items]},
            "group_by": group_by,
            "trigger": 1,
        }
        if engine:
            conf["allowed_group_values"] = {"engine_model": [engine]}
        REPORT_SHEET_CONFIG[sheet_id] = conf
        DEFAULT_REPORT_SHEETS.append(sheet_id)
        if use_item_names:
            for variable, item_name in items:
                key = f"{variable}_{sheet_id}".lower()
                VARIABLE_DISPLAY_NAMES[key] = DAILY_MY24_RAW_ITEM_NAMES.get(item_name, item_name)


_register_daily_my24_sheets()


def normalize_sheet_id(sheet_id):
    return SHEET_ALIASES.get(sheet_id, sheet_id)


def normalize_metadata_key(value):
    """Allinea product_group/product_series prima di confrontarli con il registry."""
    if value is None:
        return ""
    normalized = str(value).strip().upper()
    for char in (" ", "-", "/", "."):
        normalized = normalized.replace(char, "_")
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def is_new_layout_series(p_series):
    normalized_series = normalize_metadata_key(p_series)
    return (
        normalized_series in NEW_LAYOUT_SERIES
        or "_MY_2024" in normalized_series
        or "MY24" in normalized_series
    )


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
        "zero_as_null_exclude": conf.get("zero_as_null_exclude", []),
        "max_value": conf.get("max_value"),
        "scale": conf.get("scale", 1),
        "allowed_group_values": conf.get("allowed_group_values", {}),
        "duration_columns": conf.get("duration_columns", []),
        "required_group_values": conf.get("required_group_values", {}),
        "rename_columns": conf.get("rename_columns", {}),
    }


def get_sheet_name_for_context(p_series, p_group, sheet_id):
    """Ritorna il nome sheet tenendo conto di eccezioni per serie o gruppo."""
    sheet_id = normalize_sheet_id(sheet_id)
    conf = REPORT_SHEET_CONFIG.get(sheet_id, {})
    p_series = normalize_metadata_key(p_series)
    p_group = normalize_metadata_key(p_group)

    series_name = conf.get("series_names", {}).get(p_series)
    if series_name:
        return series_name

    group_name = conf.get("group_names", {}).get(p_group)
    if group_name:
        return group_name

    return conf.get("name", sheet_id)


def get_columns_for_sheet(p_series, p_group, sheet_id, available_columns=None):
    """Risoluzione colonne con priorita' Series > Group > layout."""
    sheet_id = normalize_sheet_id(sheet_id)
    conf = REPORT_SHEET_CONFIG.get(sheet_id)
    if not conf:
        return []

    p_series = normalize_metadata_key(p_series)
    p_group = normalize_metadata_key(p_group)

    # La serie Daily usa solo i propri sheet: nessun fallback sui layout Heavy.
    if p_series == DAILY_MY24_SERIES:
        if not sheet_id.startswith(DAILY_SHEET_PREFIX):
            return []
        return conf.get("series", {}).get(p_series, [])

    skip_series = conf.get("skip_series", set())
    if p_series in skip_series or p_group in conf.get("skip_groups", set()):
        return []

    series_map = conf.get("series", {})
    series_cols = series_map.get(p_series)
    if series_cols:
        return series_cols

    # La 410 segue le regole della 403 (stesso profilo NP MY24) dove non ha una
    # regola propria: se la 403 e' esclusa dallo sheet, lo e' anche la 410.
    if p_series == NP_410_SERIES:
        if NP_403_SERIES in skip_series:
            return []
        series_cols = series_map.get(NP_403_SERIES)
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
