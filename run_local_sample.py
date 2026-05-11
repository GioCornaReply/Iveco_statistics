# run_local_sample.py
#
# Esecuzione locale su un subset esportato da Databricks.
# Lo scopo e' validare metadata, configurazioni e trasformazioni base
# senza leggere direttamente le fat table cliente.

import argparse
from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession

from engine_cleaning import clean_spark_column_names
from engine_config import get_columns_for_sheet
from engine_loader import extract_metadata
from engine_stats import pyspark_variabili_x, report_pivot_pyspark
from engine_utils import log_step, report_dim, report_vin


DEFAULT_SAMPLE_PATH = "data/sample/Subset_Config_399_Date_20260511_123241"
DEFAULT_FORMAT = "parquet"
DEFAULT_SHEETS = ["5a"]
DEFAULT_OUTPUT_DIR = "data/output"

LOCAL_SHEET_SETTINGS = {
    "5a": {
        "name": "5) CATALYST INFO",
        "group_by": ["product_group"],
        "trigger": 1,
        "use_percentage_columns": True,
    }
}


def build_spark(app_name="iveco-local-sample"):
    """Crea una SparkSession locale per sviluppo/debug."""
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
        configured = get_columns_for_sheet(p_series, p_group, sheet_id)
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
    settings = LOCAL_SHEET_SETTINGS.get(
        sheet_id,
        {
            "name": sheet_id,
            "group_by": ["product_group"],
            "trigger": 1,
            "use_percentage_columns": True,
        },
    )
    present_cols = validation_entry["present"]
    group_by = [col_name for col_name in settings["group_by"] if col_name in df.columns]

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

    triggers = [settings["trigger"]] * len(pivot_cols)
    df_pivot = report_pivot_pyspark(df_stats, pivot_cols, group_by, triggers)
    return df_pivot, settings["name"]


def export_excel_report(df, validation, output_dir):
    """Esporta le pivot generate localmente in un file Excel sotto data/output."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    excel_path = output_path / "local_sample_statistics.xlsx"

    exported = []
    with pd.ExcelWriter(excel_path) as writer:
        for sheet_id, validation_entry in validation.items():
            df_pivot, sheet_name = build_sheet_pivot(df, sheet_id, validation_entry)
            if df_pivot is None or df_pivot.empty:
                continue

            df_pivot.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            exported.append(sheet_name)
            log_step(f"Sheet esportato: {sheet_name} ({len(df_pivot)} righe)")

    if not exported:
        log_step("Nessuna pivot esportata: rimuovo il file Excel vuoto")
        excel_path.unlink(missing_ok=True)
        return None

    log_step(f"Excel locale creato: {excel_path}")
    return excel_path


def run_local_sample(sample_path, input_format, sheet_ids, output_dir, export_excel):
    spark = build_spark()

    try:
        log_step(f"Lettura sample locale: {sample_path}")
        df_raw = read_sample(spark, sample_path, input_format)
        report_dim(df_raw, "LOCAL RAW sample")
        report_vin(df_raw)

        log_step("Pulizia nomi colonne")
        df_clean = clean_spark_column_names(df_raw)
        report_dim(df_clean, "LOCAL CLEAN sample")

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
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_local_sample(
        args.sample_path,
        args.format,
        args.sheets,
        args.output_dir,
        not args.no_excel,
    )
