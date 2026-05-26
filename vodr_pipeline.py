# vodr_pipeline.py
#
# Pipeline modulare per i report VODR. Il notebook Main_pipeline_Vodr.ipynb
# deve limitarsi a leggere i widget e orchestrare queste funzioni.

from pathlib import Path

import pyspark.sql.functions as F
from pyspark.sql.utils import AnalysisException

from engine_cleaning import (
    add_legacy_preparation_features,
    clean_spark_column_names,
    keep_latest_record_per_vin,
)
from engine_loader import extract_metadata, import_fat_tables_3
from engine_stats import pyspark_variabili_x, report_pivot_pyspark_fixed
from engine_utils import log_step, report_dim, report_vin
from run_local_sample import export_excel_outputs, read_sample
from vodr_config import (
    VODR_EXCLUDED_VINS,
    config_mt_from_vodr,
    generated_percentage_column,
    get_vodr_export_file_name,
    get_vodr_percentage_groups,
    get_vodr_report_sheets,
)


DEFAULT_VODR_CONFIG = {52}
DEFAULT_VODR_INPUT_MODE = "fat_table"
DEFAULT_VODR_OUTPUT_DIR = "/tmp/iveco_vodr_output"
DEFAULT_VODR_SAMPLE_PATH = "data/sample/vodr"
DEFAULT_VODR_SAMPLE_FORMAT = "parquet"


def parse_config_text(value):
    """Accetta '52', '50,51', liste o set e restituisce un set di int."""
    if isinstance(value, (set, list, tuple)):
        return {int(item) for item in value}

    parts = str(value).replace(";", ",").replace(" ", ",").split(",")
    config = {int(part.strip()) for part in parts if part.strip()}
    if not config:
        raise ValueError("Config vuota: inserisci almeno un id_config, es. 52")
    return config


def _find_column(df, candidates):
    """Trova una colonna anche se cambia solo il case."""
    by_lower = {col_name.lower(): col_name for col_name in df.columns}
    for candidate in candidates:
        found = by_lower.get(candidate.lower())
        if found:
            return found
    return None


def import_mission_test_statistics(spark, config):
    """Importa le fat table Mission Test statistics su Unity Catalog."""
    c = list(sorted(config)) if isinstance(config, (set, list, tuple)) else [config]
    df = None
    loaded_tables = []
    missing_tables = []

    for val in c:
        table_path = f"u_truck_analyzer_p.mission_test_statistics.fat_table_{int(val)}"
        try:
            temp_df = spark.sql(f"SELECT * FROM {table_path}")
            df = temp_df if df is None else df.unionByName(temp_df, allowMissingColumns=True)
            loaded_tables.append(table_path)
            log_step(f"Caricata Mission Test table: {table_path}")
        except AnalysisException as exc:
            missing_tables.append(f"{table_path}: {exc}")
            log_step(f"Mission Test table non accessibile: {table_path}")

    if df is None:
        details = "\n".join(missing_tables) or "nessuna tabella risolta"
        raise FileNotFoundError(f"Nessuna Mission Test table caricata per config={c}.\n{details}")

    log_step(f"Mission Test table caricate: {loaded_tables}")
    return df


def prepare_mission_test_join_frame(df_mt):
    """Riduce Mission Test alle colonne necessarie per arricchire VODR."""
    df_mt = clean_spark_column_names(df_mt)
    df_mt = keep_latest_record_per_vin(df_mt)

    vin_col = _find_column(df_mt, ["vin"])
    timestamp_col = _find_column(df_mt, ["udt_timestamp", "easy_timestamp", "utc_datetime"])
    id_config_col = _find_column(df_mt, ["id_config"])
    avg_speed_col = _find_column(df_mt, ["Average_vehicle_speed", "average_vehicle_speed"])
    mileage_col = _find_column(df_mt, ["cov_div_len", "mileage"])

    if vin_col is None:
        raise ValueError("Mission Test: colonna vin non trovata")

    select_exprs = [F.col(vin_col).alias("vin")]
    if id_config_col:
        select_exprs.append(F.col(id_config_col).alias("id_config_mt"))
    if timestamp_col:
        select_exprs.append(F.col(timestamp_col).alias("udt_timestamp_mt"))
    if avg_speed_col:
        select_exprs.append(F.col(avg_speed_col).alias("Average_vehicle_speed_mt"))
    if mileage_col:
        select_exprs.append(F.col(mileage_col).alias("mileage_mt"))

    return df_mt.select(*select_exprs)


def read_vodr_input_data(spark, input_mode, sample_path, input_format, config):
    if input_mode == "fat_table":
        return import_fat_tables_3(spark, config)
    if input_mode == "sample":
        return read_sample(spark, sample_path, input_format)
    raise ValueError("input_mode deve essere 'fat_table' oppure 'sample'")


def prepare_vodr_dataframe(
    spark,
    config,
    input_mode=DEFAULT_VODR_INPUT_MODE,
    sample_path=DEFAULT_VODR_SAMPLE_PATH,
    input_format=DEFAULT_VODR_SAMPLE_FORMAT,
    join_mission_test=True,
    join_type="inner",
    mt_config=None,
):
    """Importa VODR, applica cleaning legacy e opzionalmente il join MT."""
    df_vodr_raw = read_vodr_input_data(spark, input_mode, sample_path, input_format, config)
    report_dim(df_vodr_raw, "VODR raw")
    report_vin(df_vodr_raw)

    df_vodr = clean_spark_column_names(df_vodr_raw)
    if "vin" in df_vodr.columns:
        df_vodr = df_vodr.filter(~F.col("vin").isin(VODR_EXCLUDED_VINS))

    df_vodr = keep_latest_record_per_vin(df_vodr)
    report_dim(df_vodr, "VODR latest VIN")
    report_vin(df_vodr)

    if join_mission_test and input_mode == "fat_table":
        mt_config = set(mt_config or config_mt_from_vodr(config))
        log_step(f"Config Mission Test per join VODR: {sorted(mt_config)}")
        df_mt = import_mission_test_statistics(spark, mt_config)
        df_mt_join = prepare_mission_test_join_frame(df_mt)
        report_dim(df_mt_join, "Mission Test latest VIN")

        df_vodr = df_vodr.join(df_mt_join, on="vin", how=join_type)

        if "udt_timestamp" in df_vodr.columns and "udt_timestamp_mt" in df_vodr.columns:
            df_vodr = (
                df_vodr.withColumn(
                    "_vodr_mt_day_diff",
                    F.datediff(
                        F.to_date(F.col("udt_timestamp_mt")),
                        F.to_date(F.col("udt_timestamp")),
                    ),
                )
                .filter(F.col("_vodr_mt_day_diff").between(-1, 1))
                .drop("_vodr_mt_day_diff")
            )

        if "Average_vehicle_speed_mt" in df_vodr.columns:
            if "Average_vehicle_speed" in df_vodr.columns:
                df_vodr = df_vodr.withColumn(
                    "Average_vehicle_speed",
                    F.coalesce(F.col("Average_vehicle_speed"), F.col("Average_vehicle_speed_mt")),
                )
            else:
                df_vodr = df_vodr.withColumn(
                    "Average_vehicle_speed",
                    F.col("Average_vehicle_speed_mt"),
                )

        if "mileage_mt" in df_vodr.columns:
            if "mileage" in df_vodr.columns:
                df_vodr = df_vodr.withColumn("mileage", F.coalesce(F.col("mileage"), F.col("mileage_mt")))
            else:
                df_vodr = df_vodr.withColumn("mileage", F.col("mileage_mt"))

        report_dim(df_vodr, "VODR after Mission Test join")
        if "id_config" in df_vodr.columns:
            df_vodr.groupBy("id_config").count().orderBy("id_config").show()

    df_vodr = add_legacy_preparation_features(df_vodr)
    if "TotEngineHours" in df_vodr.columns and "engineminutes" not in df_vodr.columns:
        df_vodr = df_vodr.withColumn("engineminutes", F.col("TotEngineHours").cast("double") * F.lit(60))

    report_dim(df_vodr, "VODR prepared")
    return df_vodr


def add_vodr_time_percentages(df, config):
    """Aggiunge le colonne percentuali usate dagli sheet VODR."""
    percentage_groups = get_vodr_percentage_groups(config)
    for sheet_id, columns in percentage_groups.items():
        present = [col_name for col_name in columns if col_name in df.columns]
        missing = [col_name for col_name in columns if col_name not in df.columns]

        if sheet_id == "2a" and present:
            df = df.fillna(0, subset=present)

        if present:
            df = pyspark_variabili_x(df, present, sheet_id)
            log_step(f"Percentuali VODR {sheet_id}: {len(present)} colonne")
        else:
            log_step(f"Percentuali VODR {sheet_id}: nessuna colonna presente")

        for col_name in missing:
            log_step(f" - VODR {sheet_id} mancante: {col_name}")

    report_dim(df, "VODR time_percentage")
    return df


def build_vodr_sheet_output(df, sheet):
    """Costruisce un singolo sheet VODR come DataFrame Pandas."""
    if sheet.get("kind") == "dataset":
        log_step("Sheet VODR Complete Dataset: export diretto")
        return {
            "sheet_id": sheet["sheet_id"],
            "sheet_name": sheet["name"],
            "dataframe": df.toPandas(),
            "validation": {},
        }

    group_by = [col_name for col_name in sheet.get("group_by", []) if col_name in df.columns]
    if not group_by:
        log_step(f"Sheet VODR {sheet['sheet_id']}: group_by non presenti, salto")
        return None

    configured_columns = sheet.get("columns", [])
    triggers = sheet.get("triggers", [])
    source_sheet_id = sheet.get("source_sheet_id", sheet["sheet_id"])

    pivot_columns = []
    pivot_triggers = []
    missing_columns = []

    for idx, col_name in enumerate(configured_columns):
        if sheet.get("use_percentage_columns", False):
            pivot_col = generated_percentage_column(col_name, source_sheet_id)
            raw_is_present = col_name in df.columns
            pivot_is_present = pivot_col in df.columns
            if raw_is_present and pivot_is_present:
                pivot_columns.append(pivot_col)
                pivot_triggers.append(triggers[idx] if idx < len(triggers) else 1)
            else:
                missing_columns.append(pivot_col if raw_is_present else col_name)
        elif col_name in df.columns:
            pivot_columns.append(col_name)
            pivot_triggers.append(triggers[idx] if idx < len(triggers) else 1)
        else:
            missing_columns.append(col_name)

    for col_name in missing_columns:
        log_step(f"Sheet VODR {sheet['sheet_id']} mancante: {col_name}")

    if not pivot_columns:
        log_step(f"Sheet VODR {sheet['sheet_id']}: nessuna colonna presente, salto")
        return None

    df_pivot = report_pivot_pyspark_fixed(df, pivot_columns, group_by, pivot_triggers)
    if df_pivot is None or df_pivot.empty:
        log_step(f"Sheet VODR {sheet['sheet_id']}: pivot vuota, salto")
        return None

    return {
        "sheet_id": sheet["sheet_id"],
        "sheet_name": sheet["name"],
        "dataframe": df_pivot,
        "validation": {
            "present": pivot_columns,
            "missing": missing_columns,
            "group_by": group_by,
        },
    }


def build_vodr_sheet_outputs(df, config):
    outputs = []
    for sheet in get_vodr_report_sheets(config):
        output = build_vodr_sheet_output(df, sheet)
        if output is not None:
            outputs.append(output)
    return outputs


def run_vodr_pipeline(
    spark,
    config=DEFAULT_VODR_CONFIG,
    input_mode=DEFAULT_VODR_INPUT_MODE,
    sample_path=DEFAULT_VODR_SAMPLE_PATH,
    input_format=DEFAULT_VODR_SAMPLE_FORMAT,
    output_dir=DEFAULT_VODR_OUTPUT_DIR,
    export_excel=True,
    join_mission_test=True,
    join_type="inner",
):
    log_step(f"Avvio pipeline VODR config={sorted(config)}")
    df_prepared = prepare_vodr_dataframe(
        spark=spark,
        config=config,
        input_mode=input_mode,
        sample_path=sample_path,
        input_format=input_format,
        join_mission_test=join_mission_test,
        join_type=join_type,
    )
    df_time_percentage = add_vodr_time_percentages(df_prepared, config)
    sheet_outputs = build_vodr_sheet_outputs(df_time_percentage, config)

    excel_path = None
    if export_excel:
        excel_path = export_excel_outputs(
            sheet_outputs,
            Path(output_dir),
            get_vodr_export_file_name(config),
        )

    p_type, p_group, p_series = extract_metadata(df_time_percentage)
    return {
        "dataframe": df_time_percentage,
        "sheet_outputs": sheet_outputs,
        "excel_path": excel_path,
        "metadata": {
            "product_type": p_type,
            "product_group": p_group,
            "product_series": p_series,
        },
    }
