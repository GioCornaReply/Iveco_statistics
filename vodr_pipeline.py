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
    official_column_names,
    rename_official,
)
from engine_loader import extract_metadata, import_fat_tables_3
from engine_stats import pyspark_variabili_x, report_pivot_pyspark_fixed
from engine_utils import log_step, report_dim, report_vin
from run_local_sample import ensure_excel_writer_available, export_excel_outputs, read_sample
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
EXCEL_MAX_ROWS = 1_048_576
MAX_DIRECT_DATASET_EXCEL_CELLS = 5_000_000

VARIABLE_NAME_QUERIES = [
    "SELECT item_name, variable_name, id_config FROM vodr.config_simple_item",
    "SELECT item_name, variable_name, id_config FROM vodr.config_calculated_item",
    (
        "SELECT i.item_name, i.variable_name, o.id_config "
        "FROM vodr.config_directive_order o "
        "JOIN vodr.config_directive_items i ON i.id_directive_order = o.id"
    ),
    "SELECT item_name, variable_name, id_config FROM missiontest.config_simple_item",
    "SELECT item_name, variable_name, id_config FROM missiontest.config_calculated_item",
    "SELECT item_name, variable_name, id_config FROM missiontest.config_directive",
    "SELECT item_name, variable_name, id_config FROM missiontest.config_directive_others",
    "SELECT item_name, variable_name, id_config FROM missiontest.config_simple_item_easy",
    "SELECT item_name, variable_name, id_config FROM missiontest.config_calculated_item_easy",
    "SELECT item_name, variable_name, id_config FROM missiontest.config_directive_easy",
    "SELECT item_name, variable_name, id_config FROM missiontest.config_directive_others_easy",
]


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


def load_variables_names(spark, config=None):
    """Carica il dizionario variable_name -> item_name, se disponibile."""
    try:
        variables_names = spark.table("variables_names")
        log_step("Dizionario colonne caricato da temp view/table variables_names")
    except Exception:
        variables_names = None

    loaded_sources = []
    for query in VARIABLE_NAME_QUERIES:
        source_name = query.split(" FROM ", 1)[1].split(" ", 1)[0]
        try:
            partial = spark.sql(query).select("item_name", "variable_name", "id_config")
            variables_names = partial if variables_names is None else variables_names.unionByName(partial)
            loaded_sources.append(source_name)
        except Exception:
            log_step(f"Dizionario colonne non disponibile: {source_name}")

    if variables_names is None:
        log_step("Dizionario colonne non caricato: export con nomi tecnici/fallback")
        return None

    variables_names = variables_names.dropna(subset=["item_name", "variable_name"]).dropDuplicates()
    if config is not None:
        variables_names_config = variables_names.where(F.col("id_config").isin([int(value) for value in config]))
        log_step(
            "Dizionario colonne caricato: "
            f"{variables_names.count()} righe totali, "
            f"{variables_names_config.count()} per config {sorted(config)}"
        )
        return variables_names_config

    log_step(f"Dizionario colonne caricato: {variables_names.count()} righe da {loaded_sources}")
    return variables_names


def rename_pandas_official(df_pd, variables_names_df, config):
    """Rinomina un DataFrame pandas usando lo stesso dizionario del legacy."""
    if variables_names_df is None:
        return df_pd

    renamed = df_pd.copy()
    metric_prefixes = ("StdDev_", "Advice_", "Alert_", "Count_")
    columns = list(renamed.columns)
    plain_positions = [
        idx
        for idx, col_name in enumerate(columns)
        if not str(col_name).startswith(metric_prefixes)
    ]
    plain_names = [columns[idx] for idx in plain_positions]
    official_names = official_column_names(plain_names, variables_names_df, config)

    for idx, official_name in zip(plain_positions, official_names):
        columns[idx] = official_name

    renamed.columns = columns
    return renamed


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
    join_type="left",
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

        if (
            join_type == "inner"
            and "udt_timestamp" in df_vodr.columns
            and "udt_timestamp_mt" in df_vodr.columns
        ):
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


def build_vodr_sheet_output(df, sheet, variables_names_df=None, config=None):
    """Costruisce un singolo sheet VODR come DataFrame Pandas."""
    if sheet.get("kind") == "dataset":
        log_step("Sheet VODR Complete Dataset: export diretto")
        row_count = df.limit(EXCEL_MAX_ROWS + 1).count()
        if row_count > EXCEL_MAX_ROWS:
            log_step(
                "Sheet VODR Complete Dataset saltato: "
                f"oltre il limite Excel di {EXCEL_MAX_ROWS} righe"
            )
            return None
        cell_count = row_count * len(df.columns)
        if cell_count > MAX_DIRECT_DATASET_EXCEL_CELLS:
            log_step(
                "Sheet VODR Complete Dataset saltato: "
                f"{row_count} righe x {len(df.columns)} colonne = {cell_count} celle, "
                "troppo grande per conversione pandas/Excel sul driver"
            )
            return None

        df_export = rename_official(df, variables_names_df, config) if variables_names_df is not None else df
        return {
            "sheet_id": sheet["sheet_id"],
            "sheet_name": sheet["name"],
            "dataframe": df_export.toPandas(),
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

    log_step(
        f"Sheet VODR {sheet['sheet_id']}: calcolo pivot "
        f"({len(pivot_columns)} colonne, group_by={group_by})"
    )
    df_pivot = report_pivot_pyspark_fixed(df, pivot_columns, group_by, pivot_triggers)
    if df_pivot is None or df_pivot.empty:
        log_step(f"Sheet VODR {sheet['sheet_id']}: pivot vuota, salto")
        return None

    df_pivot = rename_pandas_official(df_pivot, variables_names_df, config)

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


def build_vodr_sheet_outputs(df, config, variables_names_df=None):
    outputs = []
    for sheet in get_vodr_report_sheets(config):
        output = build_vodr_sheet_output(df, sheet, variables_names_df, config)
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
    join_type="left",
):
    log_step(f"Avvio pipeline VODR config={sorted(config)}")
    if export_excel:
        excel_engine = ensure_excel_writer_available(auto_install=True)
        log_step(f"Engine Excel disponibile: {excel_engine}")

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
    variables_names = load_variables_names(spark, config)
    sheet_outputs = build_vodr_sheet_outputs(df_time_percentage, config, variables_names)

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
