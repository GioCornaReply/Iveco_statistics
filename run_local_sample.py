# run_local_sample.py
#
# Esecuzione locale su un subset esportato da Databricks.
# Lo scopo e' validare metadata, configurazioni e trasformazioni base
# senza leggere direttamente le fat table cliente.

import argparse
from decimal import Decimal
import os
from pathlib import Path
import re
import subprocess
import sys

import pandas as pd
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from engine_cleaning import (
    add_legacy_preparation_features,
    clean_spark_column_names,
    keep_latest_record_per_vin,
)
from engine_config import (
    VARIABLE_DISPLAY_NAMES,
    get_columns_for_sheet,
    get_default_sheet_ids,
    get_sheet_name_for_context,
    get_sheet_settings,
)
from engine_loader import (
    extract_metadata,
    get_export_file_name,
    get_metadata_for_config,
    import_fat_tables_3,
)
from engine_stats import pyspark_variabili_x, report_pivot_pyspark_fixed
from engine_utils import get_current_timestamp, log_step, report_dim, report_vin


DEFAULT_SAMPLE_PATH = "data/sample/Subset_Config_399_Date_20260511_123241"
DEFAULT_FORMAT = "parquet"
DEFAULT_SHEETS = get_default_sheet_ids()
DEFAULT_OUTPUT_DIR = "Excel_statistics"
DEFAULT_INPUT_MODE = "sample"
DEFAULT_CONFIG = {399}
INVALID_EXCEL_SHEET_CHARS = str.maketrans({char: "-" for char in "[]:*?/\\"})
DEFAULT_JAVA_HOME = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot"
DEFAULT_HADOOP_HOME = r"C:\hadoop"
MISSION_ORDER = [
    "<20 km/h HEAVY URBAN",
    "20 - 40 km/h URBAN",
    "40 - 50 km/h MIX URBAN/ MEDIUM HIGHWAY",
    ">50 km/h HIGHWAY",
]
AVERAGE_VEHICLE_SPEED_RANGE_ORDER = [
    "<10 km/h",
    "10-20 km/h",
    "20-30 km/h",
    "30-40 km/h",
    "40-50 km/h",
    "50-60 km/h",
    "60-70 km/h",
    "70-80 km/h",
    ">80 km/h",
]
AVERAGE_VEHICLE_SPEED_SPLIT_ORDER = ["<20 km/h", "20-40 km/h", ">40 km/h"]
MILEAGE_RANGE_ORDER = [
    "<10k km",
    "10k-100k km",
    "100k-200k km",
    "200k-300k km",
    "300k-400k km",
    "400k-500k km",
    "500k-600k km",
    "600k-700k km",
    "700k-800k km",
    "800k-900k km",
    "900k-1000k km",
    ">1000k km",
]
MILEAGE_SPLIT_ORDER = ["<10k km", "over 10k km"]
REPORT_SORT_ORDERS = {
    "mission": MISSION_ORDER,
    "Average_vehicle_speed_range": AVERAGE_VEHICLE_SPEED_RANGE_ORDER,
    "Average_vehicle_speed_split": AVERAGE_VEHICLE_SPEED_SPLIT_ORDER,
    "mileage_range": MILEAGE_RANGE_ORDER,
    "mileage_split": MILEAGE_SPLIT_ORDER,
}


def configure_local_spark_environment():
    """Imposta le variabili minime per PySpark locale su Windows/VS Code."""
    if os.name != "nt":
        return

    java_home = os.environ.get("JAVA_HOME") or DEFAULT_JAVA_HOME
    hadoop_home = os.environ.get("HADOOP_HOME") or DEFAULT_HADOOP_HOME

    if Path(java_home).exists():
        os.environ["JAVA_HOME"] = java_home
    if Path(hadoop_home, "bin", "winutils.exe").exists():
        os.environ["HADOOP_HOME"] = hadoop_home

    path_entries = [
        str(Path(hadoop_home, "bin")),
        str(Path(java_home, "bin")),
    ]
    current_path = os.environ.get("PATH", "")
    existing = {p.lower() for p in current_path.split(os.pathsep) if p}
    missing_entries = [p for p in path_entries if Path(p).exists() and p.lower() not in existing]
    if missing_entries:
        os.environ["PATH"] = os.pathsep.join(missing_entries + [current_path])

    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)


def build_spark(app_name="iveco-local-sample"):
    """Crea una SparkSession locale per sviluppo/debug."""
    configure_local_spark_environment()
    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.session.timeZone", "Europe/Rome")
        .getOrCreate()
    )


def read_sample(spark, sample_path, input_format):
    """Legge il sample locale esportato da Databricks."""
    path = Path(sample_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Sample non trovato: {path.resolve()}. "
            "Scarica prima la cartella DBFS dentro data/sample/."
        )

    if input_format == "parquet":
        return spark.read.parquet(str(path))
    if input_format == "csv":
        return (
            spark.read.option("header", "true")
            .option("delimiter", ";")
            .option("inferSchema", "true")
            .csv(str(path))
        )

    raise ValueError(f"Formato non supportato: {input_format}")


def read_input_data(spark, input_mode, sample_path, input_format, config):
    """Legge il dataset da sample locale oppure da fat table Databricks."""
    if input_mode == "sample":
        return read_sample(spark, sample_path, input_format)
    if input_mode == "fat_table":
        return import_fat_tables_3(spark, config)

    raise ValueError("input_mode deve essere 'sample' oppure 'fat_table'")


def validate_config_columns(df, p_series, p_group, sheet_ids):
    """Mostra quali colonne configurate sono presenti nel sample."""
    validation = {}
    for sheet_id in sheet_ids:
        configured = get_columns_for_sheet(p_series, p_group, sheet_id, df.columns)
        present = [col_name for col_name in configured if col_name in df.columns]
        missing = [col_name for col_name in configured if col_name not in df.columns]

        validation[sheet_id] = {
            "configured": configured,
            "present": present,
            "missing": missing,
            "sheet_name": get_sheet_name_for_context(p_series, p_group, sheet_id),
        }

        log_step(
            f"Sheet {sheet_id}: configurate={len(configured)}, "
            f"presenti={len(present)}, mancanti={len(missing)}"
        )
        for col_name in missing:
            log_step(f" - mancante: {col_name}")

    return validation


def build_sheet_pivot(df, sheet_id, validation_entry):
    """Costruisce la pivot Pandas per un singolo sheet locale."""
    settings = get_sheet_settings(sheet_id)
    present_cols = validation_entry["present"]
    group_by = [col_name for col_name in settings["group_by"] if col_name in df.columns]

    if settings["kind"] == "dataset":
        log_step(f"Sheet {sheet_id}: export diretto del dataset completo")
        return df.toPandas(), validation_entry.get("sheet_name", settings["name"])

    if not present_cols:
        log_step(f"Sheet {sheet_id}: nessuna colonna presente, export saltato")
        return None, validation_entry.get("sheet_name", settings["name"])
    if not group_by:
        log_step(f"Sheet {sheet_id}: colonne group_by non presenti, export saltato")
        return None, validation_entry.get("sheet_name", settings["name"])

    if settings["use_percentage_columns"]:
        df_stats = pyspark_variabili_x(df, present_cols, sheet_id)
        pivot_cols = [f"{col_name.upper()}_{sheet_id.upper()}" for col_name in present_cols]
    else:
        df_stats = df
        pivot_cols = present_cols

    if settings["zero_as_null"]:
        zero_as_null_exclude = set(settings["zero_as_null_exclude"])
        for col_name in pivot_cols:
            if col_name in zero_as_null_exclude:
                continue
            df_stats = df_stats.withColumn(
                col_name,
                F.when(F.col(col_name).cast("double") == 0, None).otherwise(F.col(col_name)),
            )

    if settings["max_value"] is not None:
        for col_name in pivot_cols:
            df_stats = df_stats.withColumn(
                col_name,
                F.when(F.col(col_name).cast("double") < settings["max_value"], F.col(col_name)),
            )

    if settings["scale"] != 1:
        for col_name in pivot_cols:
            df_stats = df_stats.withColumn(col_name, F.col(col_name).cast("double") * settings["scale"])

    configured_triggers = settings["triggers"]
    if configured_triggers:
        triggers = list(configured_triggers[: len(pivot_cols)])
        if len(triggers) < len(pivot_cols):
            triggers.extend([settings["trigger"]] * (len(pivot_cols) - len(triggers)))
    else:
        triggers = [settings["trigger"]] * len(pivot_cols)

    df_pivot = report_pivot_pyspark_fixed(
        df_stats,
        pivot_cols,
        group_by,
        triggers,
        target_columns=settings["target_columns"],
    )
    return df_pivot, validation_entry.get("sheet_name", settings["name"])


def build_sheet_outputs(df, validation):
    """Genera le pivot per tutti gli sheet e restituisce gli output riusabili."""
    outputs = []
    for sheet_id, validation_entry in validation.items():
        df_pivot, sheet_name = build_sheet_pivot(df, sheet_id, validation_entry)
        if df_pivot is None or df_pivot.empty:
            continue

        outputs.append(
            {
                "sheet_id": sheet_id,
                "sheet_name": sheet_name,
                "dataframe": df_pivot,
                "validation": validation_entry,
            }
        )
    return outputs


def make_excel_sheet_name(sheet_name, used_names):
    """Normalizza un nome sheet per i vincoli Excel/openpyxl."""
    safe_name = sheet_name.translate(INVALID_EXCEL_SHEET_CHARS).strip() or "Sheet"
    safe_name = safe_name[:31]
    candidate = safe_name
    suffix = 1
    while candidate in used_names:
        suffix_text = f"_{suffix}"
        candidate = f"{safe_name[:31 - len(suffix_text)]}{suffix_text}"
        suffix += 1
    used_names.add(candidate)
    return candidate


def clean_excel_column_name(col_name):
    """Rende leggibili gli header finali Excel."""
    name = str(col_name)
    lower_name = name.lower()

    if lower_name.startswith("stddev_"):
        return "STD"
    if lower_name.startswith("advice_"):
        return "advice"
    if lower_name.startswith("alert_"):
        return "alert"
    if lower_name.startswith("count_"):
        return "count"

    display_name = get_display_name_for_metric(name)
    if display_name:
        return display_name

    name = re.sub(r"_+", " ", name).strip()
    return name


def get_display_name_for_metric(col_name):
    """Ritorna l'Item Name del dizionario a partire dal nome tecnico."""
    metric_name = strip_metric_suffix(str(col_name))
    return VARIABLE_DISPLAY_NAMES.get(metric_name.lower())


def strip_metric_suffix(col_name):
    """Rimuove i suffissi sheet aggiunti dalle colonne percentuali."""
    candidate = col_name.strip().lower()
    for sheet_id in sorted(get_default_sheet_ids(), key=len, reverse=True):
        suffix = f"_{sheet_id.lower()}"
        if candidate.endswith(suffix):
            return candidate[: -len(suffix)]
    return candidate


def move_count_columns_to_end(df):
    """Sposta tutte le colonne Count_* alla fine del report."""
    count_cols = [col_name for col_name in df.columns if str(col_name).lower().startswith("count_")]
    if not count_cols:
        return df

    all_count_cols = list(count_cols)
    if len(count_cols) > 1:
        counts_are_identical = df[count_cols].nunique(axis=1, dropna=False).le(1).all()
        if counts_are_identical:
            count_cols = [count_cols[0]]

    other_cols = [col_name for col_name in df.columns if col_name not in all_count_cols]
    return df[other_cols + count_cols]


def sort_report_rows(df):
    """Ordina le categorie note come mission, velocita' e mileage in modo naturale."""
    sort_order_columns = [col_name for col_name in df.columns if col_name in REPORT_SORT_ORDERS]
    if not sort_order_columns:
        return df

    df_sorted = df.copy()
    for col_name in sort_order_columns:
        df_sorted[col_name] = df_sorted[col_name].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        df_sorted[col_name] = pd.Categorical(
            df_sorted[col_name],
            categories=REPORT_SORT_ORDERS[col_name],
            ordered=True,
        )

    first_numeric_idx = next(
        (
            idx
            for idx, col_name in enumerate(df_sorted.columns)
            if pd.api.types.is_numeric_dtype(df_sorted[col_name])
        ),
        len(df_sorted.columns),
    )
    leading_group_cols = list(df_sorted.columns[:first_numeric_idx])
    leading_sort_order_cols = [
        col_name for col_name in leading_group_cols if col_name in REPORT_SORT_ORDERS
    ]
    if not leading_sort_order_cols:
        leading_group_cols = [
            col_name for col_name in df_sorted.columns if col_name in REPORT_SORT_ORDERS
        ]

    sort_cols = leading_group_cols or sort_order_columns

    df_sorted = df_sorted.sort_values(sort_cols, kind="mergesort", na_position="last")

    for col_name in sort_order_columns:
        df_sorted[col_name] = df_sorted[col_name].astype(object)

    return df_sorted.reset_index(drop=True)


def prepare_excel_dataframe(df):
    """Normalizza i valori numerici prima dell'export Excel."""
    df_export = sort_report_rows(df.copy())
    df_export = move_count_columns_to_end(df_export)

    numeric_cols = df_export.select_dtypes(include=["number"]).columns
    if len(numeric_cols) > 0:
        df_export[numeric_cols] = df_export[numeric_cols].round(2)

    object_cols = df_export.select_dtypes(include=["object"]).columns
    for col_name in object_cols:
        has_decimal = df_export[col_name].map(lambda value: isinstance(value, Decimal)).any()
        if has_decimal:
            df_export[col_name] = df_export[col_name].map(
                lambda value: round(float(value), 2) if isinstance(value, Decimal) else value
            )

    df_export.columns = [clean_excel_column_name(col_name) for col_name in df_export.columns]
    return df_export


def export_excel_outputs(
    sheet_outputs,
    output_dir,
    file_name="local_sample_statistics.xlsx",
    auto_install_excel_engine=False,
):
    """Esporta pivot gia' generate in un file Excel."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    excel_path = output_path / file_name

    exported = []
    used_sheet_names = set()
    excel_engine = ensure_excel_writer_available(auto_install=auto_install_excel_engine)

    try:
        writer = pd.ExcelWriter(excel_path, engine=excel_engine)
    except PermissionError:
        suffix = excel_path.suffix or ".xlsx"
        excel_path = output_path / f"{excel_path.stem}_{get_current_timestamp()}{suffix}"
        log_step(f"File Excel standard occupato, uso: {excel_path}")
        writer = pd.ExcelWriter(excel_path, engine=excel_engine)

    with writer:
        for sheet_output in sheet_outputs:
            df_pivot = prepare_excel_dataframe(sheet_output["dataframe"])
            sheet_name = sheet_output["sheet_name"]
            excel_sheet_name = make_excel_sheet_name(sheet_name, used_sheet_names)
            df_pivot.to_excel(writer, sheet_name=excel_sheet_name, index=False, float_format="%.2f")
            if excel_engine == "xlsxwriter":
                worksheet = writer.sheets[excel_sheet_name]
                number_format = writer.book.add_format({"num_format": "0.00"})
                worksheet.set_column(0, len(df_pivot.columns) - 1, None, number_format)
            exported.append(sheet_name)
            log_step(f"Sheet esportato: {sheet_name} ({len(df_pivot)} righe)")

    if not exported:
        log_step("Nessuna pivot esportata: rimuovo il file Excel vuoto")
        excel_path.unlink(missing_ok=True)
        return None

    log_step(f"Excel locale creato: {excel_path}")
    return excel_path


def copy_excel_to_dbfs(
    excel_path,
    dbutils,
    spark=None,
    dbfs_output_dir="dbfs:/FileStore/iveco_statistics_output",
):
    """Copia su DBFS il file Excel effettivamente generato dal notebook."""
    if excel_path is None:
        raise FileNotFoundError(
            "Nessun Excel generato: export_excel_outputs ha restituito None. "
            "Controlla che almeno uno sheet sia stato prodotto."
        )

    local_path = Path(excel_path)
    if not local_path.exists():
        raise FileNotFoundError(
            f"Excel non trovato: {local_path}. "
            "Non usare nomi hardcoded: copia il path restituito da export_excel_outputs."
        )

    local_excel_path = local_path.resolve()
    dbfs_output_dir = dbfs_output_dir.rstrip("/")
    dbfs_excel_path = f"{dbfs_output_dir}/{local_excel_path.name}"

    dbutils.fs.mkdirs(dbfs_output_dir)
    dbutils.fs.cp(f"file:{local_excel_path.as_posix()}", dbfs_excel_path, True)
    log_step(f"Excel copiato su DBFS: {dbfs_excel_path}")

    download_url = None
    if spark is not None:
        try:
            workspace_url = spark.conf.get("spark.databricks.workspaceUrl", None)
        except Exception:
            workspace_url = None
        if workspace_url:
            file_store_prefix = "dbfs:/FileStore/"
            if dbfs_output_dir.startswith(file_store_prefix):
                file_url_dir = dbfs_output_dir[len(file_store_prefix) :]
            else:
                file_url_dir = "iveco_statistics_output"
            download_url = (
                f"https://{workspace_url}/files/{file_url_dir}/"
                f"{local_excel_path.name}"
            )
            print(f"Download: {download_url}")

    return {
        "local_path": str(local_excel_path),
        "dbfs_path": dbfs_excel_path,
        "download_url": download_url,
    }


def ensure_excel_writer_available(auto_install=False):
    """Restituisce un engine Excel disponibile, installandolo se richiesto."""
    try:
        import xlsxwriter  # noqa: F401

        return "xlsxwriter"
    except ImportError:
        pass

    try:
        import openpyxl  # noqa: F401

        return "openpyxl"
    except ImportError:
        pass

    if auto_install:
        log_step("Engine Excel mancante: installo XlsxWriter e openpyxl")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "XlsxWriter>=3.2.0",
                "openpyxl>=3.1.5",
            ]
        )
        return ensure_excel_writer_available(auto_install=False)

    raise ModuleNotFoundError(
        "Nessun engine Excel disponibile. Installa XlsxWriter oppure openpyxl "
        "prima di eseguire l'export Excel."
    )


def export_excel_report(
    df,
    validation,
    output_dir,
    file_name="local_sample_statistics.xlsx",
    auto_install_excel_engine=False,
):
    """Genera ed esporta le pivot in un file Excel sotto data/output."""
    sheet_outputs = build_sheet_outputs(df, validation)
    return export_excel_outputs(
        sheet_outputs,
        output_dir,
        file_name,
        auto_install_excel_engine=auto_install_excel_engine,
    )


def run_local_sample(
    sample_path,
    input_format,
    sheet_ids,
    output_dir,
    export_excel,
    keep_latest_per_vin,
    input_mode=DEFAULT_INPUT_MODE,
    config=DEFAULT_CONFIG,
):
    spark = build_spark()

    try:
        if input_mode == "fat_table":
            log_step(f"Lettura fat table Databricks per config: {sorted(config)}")
        else:
            log_step(f"Lettura sample locale: {sample_path}")

        df_raw = read_input_data(spark, input_mode, sample_path, input_format, config)
        log_step(f"RAW input dataframe creato: columns={len(df_raw.columns)}")
        if input_mode == "sample":
            report_dim(df_raw, "RAW input")
            report_vin(df_raw)
        else:
            log_step("Salto count/VIN automatici su fat_table")

        log_step("Pulizia nomi colonne")
        df_clean = clean_spark_column_names(df_raw)
        log_step(f"LOCAL CLEAN dataframe creato: columns={len(df_clean.columns)}")
        if input_mode == "sample":
            report_dim(df_clean, "LOCAL CLEAN sample")

        if keep_latest_per_vin:
            log_step("Filtro ultimo record disponibile per VIN")
            df_clean = keep_latest_record_per_vin(df_clean)
            if input_mode == "sample":
                report_dim(df_clean, "LOCAL LATEST VIN sample")
                report_vin(df_clean)
            else:
                log_step("Deduplica VIN applicata; count automatico saltato su fat_table")

        log_step("Arricchimento colonne legacy Prep")
        df_clean = add_legacy_preparation_features(df_clean)

        metadata_from_config = get_metadata_for_config(config) if input_mode == "fat_table" else None
        if metadata_from_config:
            p_type, p_group, p_series = metadata_from_config
            log_step("Metadata rilevati da config, senza lettura righe fat_table")
        else:
            p_type, p_group, p_series = extract_metadata(df_clean)
        log_step(f"Metadata rilevati: type={p_type}, group={p_group}, series={p_series}")

        validation = validate_config_columns(df_clean, p_series, p_group, sheet_ids)

        excel_path = None
        if export_excel:
            excel_file_name = (
                get_export_file_name(p_group, config)
                if input_mode == "fat_table"
                else "local_sample_statistics.xlsx"
            )
            excel_path = export_excel_report(df_clean, validation, output_dir, excel_file_name)

        log_step("Run locale completato")
        return {
            "dataframe": df_clean,
            "metadata": {
                "product_type": p_type,
                "product_group": p_group,
                "product_series": p_series,
            },
            "config_validation": validation,
            "excel_path": excel_path,
        }
    finally:
        spark.stop()


def parse_args():
    parser = argparse.ArgumentParser(description="Run locale su sample fat table IVECO.")
    parser.add_argument("--sample-path", default=DEFAULT_SAMPLE_PATH)
    parser.add_argument("--format", choices=["parquet", "csv"], default=DEFAULT_FORMAT)
    parser.add_argument("--sheets", nargs="+", default=DEFAULT_SHEETS)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--input-mode", choices=["sample", "fat_table"], default=DEFAULT_INPUT_MODE)
    parser.add_argument("--config", nargs="+", type=int, default=sorted(DEFAULT_CONFIG))
    parser.add_argument("--no-excel", action="store_true")
    parser.add_argument(
        "--keep-all-updates",
        action="store_true",
        help="Non deduplicare per VIN; mantiene anche record storici/intermedi.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_local_sample(
        args.sample_path,
        args.format,
        args.sheets,
        args.output_dir,
        not args.no_excel,
        not args.keep_all_updates,
        args.input_mode,
        set(args.config),
    )
