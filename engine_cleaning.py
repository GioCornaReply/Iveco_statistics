#Per tutte le funzioni che puliscono i nomi delle colonne e gestiscono i duplicati.

# engine_cleaning.py
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from pyspark.sql.window import Window
import re

def clean_spark_column_names(df: DataFrame) -> DataFrame:
    """
    Rinomina le colonne sostituendo caratteri speciali (punti, spazi, parentesi)
    con underscore per garantire la compatibilità con il formato Delta.
    """
    new_cols = []
    for col_name in df.columns:
        # Sostituisce caratteri non alfanumerici con underscore
        clean_name = re.sub(r'[.\s\[\](),;]+', '_', col_name).strip('_')
        # Gestisce eventuali nomi duplicati dopo la pulizia
        if clean_name in new_cols:
            suffix = 1
            while f"{clean_name}_{suffix}" in new_cols:
                suffix += 1
            clean_name = f"{clean_name}_{suffix}"
        new_cols.append(clean_name)
    
    return df.toDF(*new_cols)

def to_null(col_name, val_to_replace=0):
    """Sostituisce un valore specifico (es. 0) con NULL in una colonna Spark."""
    return F.when(F.col(col_name) == val_to_replace, None).otherwise(F.col(col_name))

def coalesce_columns(df: DataFrame, col_target: str, col_sources: list) -> DataFrame:
    """Unisce più colonne in una sola usando coalesce (prende il primo valore non null)."""
    return df.withColumn(col_target, F.coalesce(*[F.col(c) for c in col_sources]))

def keep_latest_record_per_vin(
    df: DataFrame,
    vin_col: str = "vin",
    timestamp_candidates=("udt_timestamp", "easy_timestamp", "utc_datetime"),
) -> DataFrame:
    """Mantiene solo il record piu' aggiornato per ogni VIN."""
    if vin_col not in df.columns:
        raise ValueError(f"Colonna VIN non trovata: {vin_col}")

    timestamp_col = next((c for c in timestamp_candidates if c in df.columns), None)
    if timestamp_col is None:
        raise ValueError(
            "Nessuna colonna timestamp trovata per dedup VIN. "
            f"Cercate: {list(timestamp_candidates)}"
        )

    window_spec = Window.partitionBy(vin_col).orderBy(
        F.col(timestamp_col).cast("timestamp").desc_nulls_last()
    )
    return (
        df.withColumn("_vin_latest_rank", F.row_number().over(window_spec))
        .filter(F.col("_vin_latest_rank") == 1)
        .drop("_vin_latest_rank")
    )


def add_legacy_preparation_features(df: DataFrame) -> DataFrame:
    """Ricrea localmente alcune colonne prodotte dal vecchio notebook Prep."""
    if "product_model" in df.columns:
        df = engine_model_standard(df)

    if "mileage" not in df.columns and "cov_div_len" in df.columns:
        df = df.withColumn("mileage", F.col("cov_div_len"))

    if "Average_vehicle_speed" in df.columns:
        speed = F.col("Average_vehicle_speed").cast("double")

        speed_range_expr = (
            F.when(speed < 10, "<10 km/h")
            .when((speed >= 10) & (speed < 20), "10-20 km/h")
            .when((speed >= 20) & (speed < 30), "20-30 km/h")
            .when((speed >= 30) & (speed < 40), "30-40 km/h")
            .when((speed >= 40) & (speed < 50), "40-50 km/h")
            .when((speed >= 50) & (speed < 60), "50-60 km/h")
            .when((speed >= 60) & (speed < 70), "60-70 km/h")
            .when((speed >= 70) & (speed < 80), "70-80 km/h")
            .when(speed >= 80, ">80 km/h")
        )
        df = _fill_derived_column(df, "Average_vehicle_speed_range", speed_range_expr)

        speed_split_expr = (
            F.when(speed < 20, "<20 km/h")
            .when((speed >= 20) & (speed < 40), "20-40 km/h")
            .when(speed >= 40, ">40 km/h")
        )
        df = _fill_derived_column(df, "Average_vehicle_speed_split", speed_split_expr)

        mission_expr = (
            F.when(speed < 20, "<20 km/h HEAVY URBAN")
            .when((speed >= 20) & (speed < 40), "20 - 40 km/h URBAN")
            .when(
                (speed >= 40) & (speed < 50),
                "40 - 50 km/h MIX URBAN/ MEDIUM HIGHWAY",
            )
            .when(speed >= 50, ">50 km/h HIGHWAY")
        )
        df = _fill_derived_column(df, "mission", mission_expr)

    mileage_col = None
    if "mileage" in df.columns:
        mileage_col = "mileage"
    elif "cov_div_len" in df.columns:
        mileage_col = "cov_div_len"

    if mileage_col:
        mileage = F.col(mileage_col).cast("double")

        mileage_range_expr = (
            F.when(mileage < 10000, "<10k km")
            .when((mileage >= 10000) & (mileage < 100000), "10k-100k km")
            .when((mileage >= 100000) & (mileage < 200000), "100k-200k km")
            .when((mileage >= 200000) & (mileage < 300000), "200k-300k km")
            .when((mileage >= 300000) & (mileage < 400000), "300k-400k km")
            .when((mileage >= 400000) & (mileage < 500000), "400k-500k km")
            .when((mileage >= 500000) & (mileage < 600000), "500k-600k km")
            .when((mileage >= 600000) & (mileage < 700000), "600k-700k km")
            .when((mileage >= 700000) & (mileage < 800000), "700k-800k km")
            .when((mileage >= 800000) & (mileage < 900000), "800k-900k km")
            .when((mileage >= 900000) & (mileage < 1000000), "900k-1000k km")
            .when(mileage >= 1000000, ">1000k km")
        )
        df = _fill_derived_column(df, "mileage_range", mileage_range_expr)

        mileage_split_expr = F.when(mileage < 10000, "<10k km").when(
            mileage >= 10000, "over 10k km"
        )
        df = _fill_derived_column(df, "mileage_split", mileage_split_expr)

    return df


def _fill_derived_column(df: DataFrame, col_name: str, expr) -> DataFrame:
    """Crea la colonna se manca, oppure rimpiazza solo i NULL con il valore derivato.

    Necessario per VODR: nella fat table colonne come `mission` o `mileage_range`
    possono esistere come schema ma essere completamente NULL; senza coalesce
    la versione 'colonna esiste' non veniva ricalcolata e gli sheet pivot per
    `mission`/`mileage_range` risultavano vuoti.
    """
    if col_name not in df.columns:
        return df.withColumn(col_name, expr)
    return df.withColumn(col_name, F.coalesce(F.col(col_name), expr))

# --- NORMALIZZAZIONE MODELLI MOTORE ---

def engine_model_standard(df: DataFrame) -> DataFrame:
    """Mappatura standard per i modelli motore basata sui codici prodotto."""
    product_model = F.upper(F.coalesce(F.col("product_model").cast("string"), F.lit("")))
    power = (
        F.upper(F.coalesce(F.col("power").cast("string"), F.lit("")))
        if "power" in df.columns
        else F.lit("")
    )

    derived_engine = (
        F.when(product_model.startswith("F1A"), "F1A")
        .when(product_model.startswith("F1C"), "F1C")
        .when(product_model.startswith("F4AF"), "Tector 5")
        .when(product_model.startswith("F4BE"), "Tector 7")
        .when(product_model.startswith("F2BE") | product_model.contains("C9") | power.contains("C9"), "Cursor 9")
        .when(product_model.startswith("F3GE") | product_model.contains("C11") | power.contains("C11"), "Cursor 11")
        .when(product_model.startswith("F3HE") | product_model.contains("C13") | power.contains("C13"), "Cursor 13")
        .otherwise("Unknown")
    )

    if "engine_model" not in df.columns:
        return df.withColumn("engine_model", derived_engine)

    current_engine = F.upper(F.coalesce(F.col("engine_model").cast("string"), F.lit("")))
    return df.withColumn(
        "engine_model",
        F.when(
            F.col("engine_model").isNull()
            | current_engine.isin("", "NA", "N/A", "UNKNOWN", "UNKNOW", "NONE", "NULL"),
            derived_engine,
        ).otherwise(F.col("engine_model")),
    )

# --- RIDENOMINAZIONE UFFICIALE ---

def _build_variables_mapping(variables_names_df: DataFrame, config_list: set) -> dict:
    """Crea mapping case-insensitive variable_name -> item_name."""
    if variables_names_df is None:
        return {}

    columns_by_lower = {col_name.lower(): col_name for col_name in variables_names_df.columns}
    variable_col = columns_by_lower.get("variable_name") or columns_by_lower.get("my_variable_name")
    item_col = columns_by_lower.get("item_name")
    config_col = columns_by_lower.get("id_config")

    if variable_col is None or item_col is None:
        return {}

    df_mapping = variables_names_df
    if config_col is not None and config_list:
        df_mapping = df_mapping.where(F.col(config_col).isin([int(value) for value in config_list]))

    mapping = {}
    for row in df_mapping.select(item_col, variable_col).dropna().dropDuplicates().collect():
        old_name = row[variable_col]
        new_name = row[item_col]
        if old_name and new_name:
            mapping[str(old_name).lower()] = str(new_name)

    return mapping


def _column_candidates(col_name: str) -> list:
    """Possibili chiavi legacy per una colonna tecnica o percentuale."""
    candidates = [col_name]

    if col_name.endswith("_x"):
        candidates.append(col_name[:-2])

    parts = col_name.rsplit("_", 1)
    if len(parts) == 2 and parts[1].lower()[:1].isdigit():
        candidates.append(parts[0])

    return candidates


def _fallback_display_name(col_name: str) -> str:
    return col_name.replace("_x", "").replace("_", " ").title()


def _make_unique_column_names(column_names: list) -> list:
    used = {}
    result = []
    for col_name in column_names:
        if col_name not in used:
            used[col_name] = 0
            result.append(col_name)
            continue

        used[col_name] += 1
        suffix = used[col_name]
        result.append(f"{col_name} ({suffix})")
    return result


def official_column_names(columns: list, variables_names_df: DataFrame, config_list: set) -> list:
    """Restituisce nomi ufficiali mantenendo l'ordine delle colonne."""
    mapping = _build_variables_mapping(variables_names_df, config_list)
    renamed = []

    for col_name in columns:
        official_name = None
        for candidate in _column_candidates(str(col_name)):
            official_name = mapping.get(candidate.lower())
            if official_name:
                break

        renamed.append(official_name or _fallback_display_name(str(col_name)))

    return _make_unique_column_names(renamed)


def rename_official(df: DataFrame, variables_names_df: DataFrame, config_list: set) -> DataFrame:
    """Mappa i nomi tecnici delle colonne sui nomi ufficiali item_name."""
    return df.toDF(*official_column_names(df.columns, variables_names_df, config_list))

# --- LOGICA TRIGGER ---

def searchforADVICEorALERT(df: DataFrame) -> DataFrame:
    """
    Analizza i trigger presenti e assegna una valutazione testuale.
    """
    if "trigger_id" not in df.columns:
        return df
        
    return df.withColumn("trigger_status",
        F.when(F.col("trigger_id").isin([1, 3]), "ADVICE")
         .when(F.col("trigger_id").isin([2, 4]), "ALERT")
         .otherwise("NORMAL")
    )

def outlier_founder(df: DataFrame, column: str, threshold: float = 3.0) -> DataFrame:
    """
    Filtra gli outlier basandosi sullo Z-score (semplificato).
    """
    stats = df.select(F.avg(column).alias("avg"), F.stddev(column).alias("std")).collect()[0]
    if stats['std'] == 0 or stats['std'] is None:
        return df
        
    upper_bound = stats['avg'] + (threshold * stats['std'])
    lower_bound = stats['avg'] - (threshold * stats['std'])
    
    return df.filter((F.col(column) <= upper_bound) & (F.col(column) >= lower_bound))
