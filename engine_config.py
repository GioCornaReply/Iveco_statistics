# engine_config.py

SERIES_CONFIG = {
    # Usiamo MAIUSCOLO e underscore per un matching perfetto
    "S_WAY_AT_AD_MY_2024": {
        "5a": ["Diffpressure_DPF_020", "Sox_oxicat_08", "Nh3_concentration_550", "Adblue_concentration_29", "Adblue_concentration_63"]
    },
    "S_WAY_AS_MY_2024": {
        "5a": ["Diffpressure_DPF_020", "Sox_oxicat_08", "Nh3_concentration_550", "Adblue_concentration_29", "Adblue_concentration_63"]
    },
    "S_WAY_AS_ANZ": {
        "5a": ["DPFup1", "DPFup2", "DPFup3"]
    }
}

GROUP_CONFIG = {
    "IVECO_S_WAY": {
        "5a": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"],
        "2b": ["Oilpressure_020", "Oilpressure_25"]
    },
    "EUROCARGO": {
        "5a": ["dpf_upstr_t_1", "dpf_upstr_t_2", "dpf_upstr_t_3"]
    }
}

def get_columns_for_sheet(p_series, p_group, sheet_id):
    """
    Cerca le colonne. Se non trova la serie specifica, 
    prova a rimuovere eventuali underscore extra per flessibilità.
    """
    # 1. Prova Serie esatta
    cols = SERIES_CONFIG.get(p_series, {}).get(sheet_id)
    
    # 2. Se non trova, prova Gruppo
    if not cols:
        cols = GROUP_CONFIG.get(p_group, {}).get(sheet_id)
        
    return cols if cols else []