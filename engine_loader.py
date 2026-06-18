# engine_loader.py
from pyspark.sql.utils import AnalysisException


MISSION_TEST_STATISTICS_CONFIGS = {
    399,
    400,
    401,
    402,
    405,  # X-WAY MY24 AT/AD V1.6.4 C9
    406,  # T-WAY MY24 V1.6.4 C9
    408,
}

CONFIG_METADATA = {
    399: ("MISSION_TEST", "IVECO_S_WAY", "S_WAY_AT_AD_MY_2024"),
    405: ("MISSION_TEST", "IVECO_X_WAY", "X_WAY_AT_AD_MY_2024"),
    406: ("MISSION_TEST", "IVECO_T_WAY", "T_WAY_MY_2024"),
    408: ("MISSION_TEST", "IVECO_X_WAY", "X_WAY_AT_AD_MY_2024"),
}

VODR_STATISTICS_CONFIGS = {
    33,
    49,
    50,
    51,
    52,
    53,
    54,
    56,
}


def normalize_product_group(product_group):
    """Normalizza il gruppo prodotto per mapping stabili anche con '-' o spazi."""
    if product_group is None:
        return "UNKNOWN"
    return str(product_group).strip().upper().replace(" ", "_").replace("-", "_")


def get_table_path(val):
    """Restituisce il nome tabella Databricks in base alla config."""
    if val in {36, 76, 77}:
        return f"missiontest.fat_table_easy_{val}"
    if val in VODR_STATISTICS_CONFIGS:
        return f"u_truck_analyzer_p.vodr_statistics.fat_table_{val}"
    if val in MISSION_TEST_STATISTICS_CONFIGS:
        return f"u_truck_analyzer_p.mission_test_statistics.fat_table_{val}"
    if val < 100:
        return f"vodr.fat_table_{val}"
    if val > 250:
        return f"missiontest.fat_table_{val}"
    return None


def import_fat_tables_3(spark, config):
    """Importa e unisce le fat table Databricks per una o piu' config."""
    c = list(sorted(config)) if isinstance(config, (set, list, tuple)) else [config]
    df = None
    loaded_tables = []
    missing_tables = []

    for val in c:
        table_path = get_table_path(int(val))
        if not table_path:
            missing_tables.append(f"config {val}: sorgente non configurata")
            continue

        try:
            temp_df = spark.sql(f"SELECT * FROM {table_path}")
            df = temp_df if df is None else df.unionByName(temp_df, allowMissingColumns=True)
            loaded_tables.append(table_path)
            print(f"Caricata fat table: {table_path}")
        except AnalysisException as exc:
            missing_tables.append(f"{table_path}: {exc}")
            print(f"Tabella non trovata o non accessibile: {table_path}")

    if df is None:
        details = "\n".join(missing_tables) or "nessuna tabella risolta"
        raise FileNotFoundError(f"Nessuna fat table caricata per config={c}.\n{details}")

    print(f"Fat table caricate: {loaded_tables}")
    return df


def get_export_file_name(product_group, config):
    """Genera il nome del file Excel."""
    config_str = "_".join(map(str, sorted(config)))
    normalized_group = normalize_product_group(product_group)
    mapping = {
        "EUROCARGO": "EUROCARGO",
        "IVECO_S_WAY": "HEAVY_SWAY",
        "IVECO_X_WAY": "HEAVY_XWAY",
        "IVECO_T_WAY": "HEAVY_TWAY",
    }
    prefix = mapping.get(normalized_group, "GENERIC")
    return f"Statistics_{prefix}_{config_str}_dataset.xlsx"


def get_metadata_for_config(config):
    """Restituisce metadata noti senza leggere righe Spark, quando la config lo consente."""
    config_values = {int(v) for v in config} if isinstance(config, (set, list, tuple)) else {int(config)}
    metadata_values = [CONFIG_METADATA.get(value) for value in sorted(config_values)]
    known_values = [value for value in metadata_values if value is not None]

    if len(known_values) != len(config_values):
        return None

    if len(set(known_values)) == 1:
        return known_values[0]

    product_types = {value[0] for value in known_values}
    product_groups = {value[1] for value in known_values}
    product_series = {value[2] for value in known_values}

    return (
        product_types.pop() if len(product_types) == 1 else "MIXED",
        product_groups.pop() if len(product_groups) == 1 else "MIXED",
        product_series.pop() if len(product_series) == 1 else "MIXED",
    )


def extract_metadata(df):
    """Estrae i valori reali product_type/group/series dalle righe."""
    try:
        row = df.select("product_type", "product_group", "product_series").first()
        if not row:
            return "UNKNOWN", "UNKNOWN", "UNKNOWN"

        data = row.asDict()

        def clean(v):
            if v is None:
                return "UNKNOWN"
            return (
                str(v)
                .strip()
                .upper()
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
            )

        p_type = clean(data.get("product_type"))
        p_group = clean(data.get("product_group"))
        p_series = clean(data.get("product_series"))

        return p_type, p_group, p_series
    except Exception as exc:
        print(f"Errore estrazione metadati: {exc}")
        return "ERROR", "ERROR", "ERROR"


def save_to_delta(df, table_name):
    """Salva un DataFrame in Delta su DBFS."""
    path = f"dbfs:/mnt/truck_analyzer/checkpoints/{table_name}"
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(path)


def load_from_delta(spark, table_name):
    """Legge un DataFrame Delta da DBFS."""
    path = f"dbfs:/mnt/truck_analyzer/checkpoints/{table_name}"
    return spark.read.format("delta").load(path)
