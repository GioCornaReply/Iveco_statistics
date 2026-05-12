# run_local_sample.py
#
# Esecuzione locale su un subset esportato da Databricks.
# Lo scopo e' validare metadata, configurazioni e trasformazioni base
# senza leggere direttamente le fat table cliente.

import argparse
import os
from pathlib import Path
import sys

import pandas as pd
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from engine_cleaning import (
    add_legacy_preparation_features,
    clean_spark_column_names,
    keep_latest_record_per_vin,
)
from engine_config import get_columns_for_sheet, get_default_sheet_ids, get_sheet_settings
from engine_loader import extract_metadata
from engine_stats import pyspark_variabili_x, report_pivot_pyspark_fixed
from engine_utils import get_current_timestamp, log_step, report_dim, report_vin


DEFAULT_SAMPLE_PATH = "data/sample/Subset_Config_399_Date_20260511_123241"
DEFAULT_FORMAT = "parquet"
DEFAULT_SHEETS = get_default_sheet_ids()
DEFAULT_OUTPUT_DIR = "data/output"
INVALID_EXCEL_SHEET_CHARS = str.maketrans({char: "-" for char in "[]:*?/\\"})
DEFAULT_JAVA_HOME = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot"
DEFAULT_HADOOP_HOME = r"C:\hadoop"


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
        return df.toPandas(), settings["name"]

    if not present_cols:
        log_step(f"Sheet {sheet_id}: nessuna colonna presente, export saltato")
        return None, settings["name"]
    if not group_by:
        log_step(f"Sheet {sheet_id}: colonne group_by non presenti, export saltato")
        return None, settings["name"]

    if settings["use_percentage_columns"]:
        df_stats = pyspark_variabili_x(df, present_cols, sheet_id)
        pivot_cols = [f"{col_name.upper()}_{sheet_id.upper()}" for col_name in present_cols]
    else:
        df_stats = df
        pivot_cols = present_cols

    if settings["zero_as_null"]:
        for col_name in pivot_cols:
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
    return df_pivot, settings["name"]


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


def export_excel_outputs(sheet_outputs, output_dir):
    """Esporta pivot gia' generate in un file Excel sotto data/output."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    excel_path = output_path / "local_sample_statistics.xlsx"

    exported = []
    used_sheet_names = set()
    try:
        writer = pd.ExcelWriter(excel_path)
    except PermissionError:
        excel_path = output_path / f"local_sample_statistics_{get_current_timestamp()}.xlsx"
        log_step(f"File Excel standard occupato, uso: {excel_path}")
        writer = pd.ExcelWriter(excel_path)

    with writer:
        for sheet_output in sheet_outputs:
            df_pivot = sheet_output["dataframe"]
            sheet_name = sheet_output["sheet_name"]
            excel_sheet_name = make_excel_sheet_name(sheet_name, used_sheet_names)
            df_pivot.to_excel(writer, sheet_name=excel_sheet_name, index=False)
            exported.append(sheet_name)
            log_step(f"Sheet esportato: {sheet_name} ({len(df_pivot)} righe)")

    if not exported:
        log_step("Nessuna pivot esportata: rimuovo il file Excel vuoto")
        excel_path.unlink(missing_ok=True)
        return None

    log_step(f"Excel locale creato: {excel_path}")
    return excel_path


def export_excel_report(df, validation, output_dir):
    """Genera ed esporta le pivot in un file Excel sotto data/output."""
    sheet_outputs = build_sheet_outputs(df, validation)
    return export_excel_outputs(sheet_outputs, output_dir)


def run_local_sample(
    sample_path,
    input_format,
    sheet_ids,
    output_dir,
    export_excel,
    keep_latest_per_vin,
):
    spark = build_spark()

    try:
        log_step(f"Lettura sample locale: {sample_path}")
        df_raw = read_sample(spark, sample_path, input_format)
        report_dim(df_raw, "LOCAL RAW sample")
        report_vin(df_raw)

        log_step("Pulizia nomi colonne")
        df_clean = clean_spark_column_names(df_raw)
        report_dim(df_clean, "LOCAL CLEAN sample")

        if keep_latest_per_vin:
            log_step("Filtro ultimo record disponibile per VIN")
            df_clean = keep_latest_record_per_vin(df_clean)
            report_dim(df_clean, "LOCAL LATEST VIN sample")
            report_vin(df_clean)

        log_step("Arricchimento colonne legacy Prep")
        df_clean = add_legacy_preparation_features(df_clean)

        p_type, p_group, p_series = extract_metadata(df_clean)
        log_step(f"Metadata rilevati: type={p_type}, group={p_group}, series={p_series}")

        validation = validate_config_columns(df_clean, p_series, p_group, sheet_ids)

        excel_path = None
        if export_excel:
            excel_path = export_excel_report(df_clean, validation, output_dir)

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
    )
