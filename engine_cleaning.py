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
    # Per la 403 NP i record catastroficamente corrotti vanno rimossi prima
    # del ranking, cosi' un update storico valido dello stesso VIN resta usabile.
    df = exclude_corrupt_statistics_rows(df)

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


def apply_statistics_quality_filters(df: DataFrame, max_data_age_days: int = 366) -> DataFrame:
    """Applica le regole di qualita' legacy prima delle statistiche.

    Le metriche fuori soglia diventano NULL, cosi' non pesano su media/deviazione
    standard. I record senza mileage, engine-hours o timestamp validi vengono
    esclusi quando la rispettiva sorgente e' disponibile nel dataset.
    """
    # La stessa protezione si applica anche quando la deduplica VIN e' disattivata.
    df = exclude_corrupt_statistics_rows(df)
    df = _coalesce_legacy_statistics_columns(df)

    metric_ranges = {
        "average_fuel_consumption_kml": (0.1, 6.0),
        "Average_vehicle_speed": (0.1, 80.0),
        "AdBlue_consumption_percentage": (0.1, 100.0),
        "AdBlue_consumption_l100km": (0.1, 9.0),
        "Average_start": (0.1, 1000.0),
    }
    for column, (lower_bound, upper_bound) in metric_ranges.items():
        if column in df.columns:
            value = F.col(column).cast("double")
            df = df.withColumn(
                column,
                F.when(value.between(lower_bound, upper_bound), value),
            )

    if "enginehours" in df.columns:
        value = F.col("enginehours").cast("double")
        df = df.withColumn("enginehours", F.when(value > 1, value)).filter(
            F.col("enginehours").isNotNull()
        )

    if "enginehours" in df.columns:
        engine_hours = F.col("enginehours").cast("double")
        for source_column, target_column in (
            ("engineoverspeed", "engineoverspeed_pct"),
            ("crank_100km", "crank_100km_pct"),
        ):
            if source_column not in df.columns:
                continue
            percentage = F.col(source_column).cast("double") * F.lit(100.0) / engine_hours
            df = df.withColumn(
                target_column,
                F.when((percentage > 0) & (percentage < 101), F.round(percentage, 2)),
            )

    if "mileage" in df.columns:
        mileage = F.col("mileage").cast("double")
        df = df.withColumn("mileage", F.when(mileage > 1000, mileage)).filter(
            F.col("mileage").isNotNull()
        )

    if "udt_timestamp" in df.columns:
        timestamp = F.col("udt_timestamp").cast("timestamp")
        df = df.withColumn("udt_timestamp", timestamp).filter(
            timestamp.isNotNull()
            & (F.datediff(F.current_date(), timestamp) < max_data_age_days)
        )

    return df


def _np_403_scope(df: DataFrame):
    """Identifica le righe Statistics 403 NP senza coinvolgere le altre serie."""
    scope = F.lit(False)
    id_config = _find_column_case_insensitive(df, "id_config")
    if id_config is not None:
        scope = scope | F.coalesce(
            F.col(f"`{id_config}`").cast("int") == F.lit(403), F.lit(False)
        )

    product_series = _find_column_case_insensitive(df, "product_series")
    if product_series is not None:
        normalized = F.upper(F.col(f"`{product_series}`").cast("string"))
        scope = scope | F.coalesce(
            normalized.contains("NP")
            & (
                normalized.contains("MY 2024")
                | normalized.contains("MY_2024")
                | normalized.contains("MY24")
            ),
            F.lit(False),
        )

    return scope


def _domain_violation(df: DataFrame, column_name: str, invalid_condition_builder):
    """Restituisce 1 soltanto quando una metrica presente viola il suo dominio."""
    actual_name = _find_column_case_insensitive(df, column_name)
    if actual_name is None:
        return F.lit(0)
    value = F.col(f"`{actual_name}`").cast("double")
    return F.when(value.isNotNull() & invalid_condition_builder(value), F.lit(1)).otherwise(F.lit(0))


def exclude_corrupt_statistics_rows(df: DataFrame, minimum_violations: int = 2) -> DataFrame:
    """Scarta record 403 NP corrotti su piu' metriche indipendenti.

    Una singola metrica fuori dominio viene gestita dai filtri metrici senza
    eliminare il veicolo. Due o piu' violazioni indicano invece un payload
    corrotto (per esempio i valori sentinella ripetuti del VIN noto).
    """
    scope = _np_403_scope(df)
    violations = [
        _domain_violation(df, "Average_vehicle_speed", lambda value: (value <= 0) | (value > 80)),
        _domain_violation(df, "Average_enginespeed", lambda value: (value < 200) | (value > 4000)),
        _domain_violation(df, "avgcrank_100km", lambda value: (value < 0) | (value > 100)),
        _domain_violation(df, "Average_start", lambda value: (value <= 0) | (value > 1000)),
    ]

    overspeed_name = _find_column_case_insensitive(df, "engineoverspeed")
    enginehours_name = _find_column_case_insensitive(df, "enginehours")
    if enginehours_name is None:
        enginehours_name = _find_column_case_insensitive(df, "TotEngineHours")
    if enginehours_name is None:
        enginehours_name = _find_column_case_insensitive(df, "tot_eng_hours")

    if overspeed_name is not None:
        overspeed = F.col(f"`{overspeed_name}`").cast("double")
        invalid_overspeed = (overspeed < 0) | (overspeed >= 50000000)
        if enginehours_name is not None:
            enginehours = F.col(f"`{enginehours_name}`").cast("double")
            invalid_overspeed = invalid_overspeed | (
                enginehours.isNotNull()
                & (enginehours > 0)
                & (overspeed > enginehours * F.lit(3600.0))
            )
        violations.append(
            F.when(overspeed.isNotNull() & invalid_overspeed, F.lit(1)).otherwise(F.lit(0))
        )

    violation_count = sum(violations, F.lit(0))
    return (
        df.withColumn("_quality_violation_count", violation_count)
        .filter((~scope) | (F.col("_quality_violation_count") < F.lit(minimum_violations)))
        .drop("_quality_violation_count")
    )


def _coalesce_legacy_statistics_columns(df: DataFrame) -> DataFrame:
    """Espone le colonne canoniche senza perdere le varianti originali."""
    variants = {
        "enginehours": ("enginehours", "TotEngineHours", "tot_eng_hours"),
        "mileage": ("mileage", "cov_div_len"),
        "udt_timestamp": ("udt_timestamp", "easy_timestamp", "utc_datetime"),
        "crank_100km": ("crank_100km", "avgcrank_100km"),
    }
    for canonical, candidates in variants.items():
        present = [column for column in candidates if column in df.columns]
        if not present:
            continue
        df = df.withColumn(canonical, F.coalesce(*[F.col(column) for column in present]))
    return df


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
            .when((mileage >= 900000) & (mileage < 1000000), "900k-1M km")
            .when(mileage >= 1000000, ">1M km")
        )
        df = _fill_derived_column(
            df,
            "mileage_range",
            mileage_range_expr,
            replace_values=("900k-1000k km", ">1000k km"),
        )

        mileage_split_expr = F.when(mileage < 10000, "<10k km").when(
            mileage >= 10000, "over 10k km"
        )
        df = _fill_derived_column(df, "mileage_split", mileage_split_expr)

    return add_np_403_calculated_features(df)


def _find_column_case_insensitive(df: DataFrame, column_name: str):
    """Risolve una colonna del dizionario NP senza dipendere dal casing Spark."""
    return {name.lower(): name for name in df.columns}.get(column_name.lower())


def _duration_seconds(column_name: str):
    """Converte un timer numerico o `hh:mm:ss` in secondi."""
    raw_value = F.trim(F.col(f"`{column_name}`").cast("string"))
    numeric_value = F.when(
        raw_value.rlike(r"^[+-]?[0-9]+(?:[.][0-9]+)?$"),
        raw_value.cast("double"),
    )
    hours = F.regexp_extract(raw_value, r"^([0-9]+):[0-9]{1,2}:[0-9]{1,2}(?:[.][0-9]+)?$", 1)
    minutes = F.regexp_extract(raw_value, r"^[0-9]+:([0-9]{1,2}):[0-9]{1,2}(?:[.][0-9]+)?$", 1)
    seconds = F.regexp_extract(raw_value, r"^[0-9]+:[0-9]{1,2}:([0-9]{1,2}(?:[.][0-9]+)?)$", 1)
    clock_value = F.when(
        raw_value.rlike(r"^[0-9]+:[0-9]{1,2}:[0-9]{1,2}(?:[.][0-9]+)?$"),
        hours.cast("double") * F.lit(3600.0)
        + minutes.cast("double") * F.lit(60.0)
        + seconds.cast("double"),
    )
    return F.coalesce(numeric_value, clock_value)


def add_np_403_calculated_features(df: DataFrame) -> DataFrame:
    """Normalizza timer/counter MY24 NP nelle unita' richieste dal report 403."""
    duration_columns = (
        ("Engine_overspeed_2600_rpm_Timer", "Engine_overspeed_2600_rpm_seconds", 1.0),
        ("Post_Catalyst_temperature_860_timer", "Post_Catalyst_temperature_860_minutes", 1.0 / 60.0),
        ("Cat_Eff_Timer", "Cat_Eff_minutes", 1.0 / 60.0),
        ("Coolant_temperature_high_104_timer", "Coolant_temperature_high_104_seconds", 1.0),
        ("High_oil_temperature_120_timer", "High_oil_temperature_120_seconds", 1.0),
        ("High_boost_pressure_timer", "High_boost_pressure_minutes", 1.0 / 60.0),
        ("Low_ambient_pressure_timer", "Low_ambient_pressure_seconds", 1.0),
    )
    for source_name, target_name, scale in duration_columns:
        source_column = _find_column_case_insensitive(df, source_name)
        if source_column is not None:
            df = df.withColumn(target_name, _duration_seconds(source_column) * F.lit(scale))

    numeric_columns = (
        "Engine_on_time",
        "Cat_Eff_Counter",
        "Coolant_temperature_high_104_counter",
        "High_oil_temperature_120_counter",
        "High_boost_pressure_counter",
        "Low_ambient_pressure_counter",
    )
    for target_name in numeric_columns:
        source_column = _find_column_case_insensitive(df, target_name)
        if source_column is not None:
            df = df.withColumn(target_name, F.col(f"`{source_column}`").cast("double"))

    mileage_column = _find_column_case_insensitive(df, "mileage")
    if mileage_column is not None:
        mileage = F.col(f"`{mileage_column}`").cast("double")
        lifecycle = F.lit(100.0) - mileage / F.lit(10000.0)
        df = df.withColumn(
            "engine_life_cycle",
            F.when(lifecycle.between(0.0, 100.0), F.round(lifecycle, 2)),
        )

    return df


def _fill_derived_column(df: DataFrame, col_name: str, expr, replace_values=()) -> DataFrame:
    """Crea la colonna se manca, oppure rimpiazza solo i NULL con il valore derivato.

    Necessario per VODR: nella fat table colonne come `mission` o `mileage_range`
    possono esistere come schema ma essere completamente NULL; senza coalesce
    la versione 'colonna esiste' non veniva ricalcolata e gli sheet pivot per
    `mission`/`mileage_range` risultavano vuoti.
    """
    if col_name not in df.columns:
        return df.withColumn(col_name, expr)

    current = F.col(col_name)
    if replace_values:
        current = F.when(current.isin(*replace_values), expr).otherwise(current)
    return df.withColumn(col_name, F.coalesce(current, expr))

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
