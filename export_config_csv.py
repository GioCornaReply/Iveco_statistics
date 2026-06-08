# export_config_csv.py
#
# Script Databricks per esportare un subset grezzo delle fat table.
# Uso previsto:
# 1. Impostare i widget Databricks oppure modificare i default qui sotto.
# 2. Eseguire lo script su cluster cliente.
# 3. Recuperare la cartella generata da DBFS e usarla in locale come sample.

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from engine_loader import extract_metadata, import_fat_tables_3
from engine_utils import get_current_timestamp, log_step, report_dim


# ---------------------------------------------------------------------------
# CONFIGURAZIONE DEFAULT
# ---------------------------------------------------------------------------

# Esempio: 49 per VODR, 399/400/401/402/405/406/408 per Mission Test statistics.
DEFAULT_CONFIG_IDS = [49]

# None = tutte le colonne della fat table.
# Impostare una lista solo se il CSV diventa troppo grande da scaricare.
COLUMNS_TO_KEEP = None

# None = esporta tutte le righe. Impostare un numero piccolo, es. 10000, per un sample.
ROW_LIMIT = 10000

# Formato consigliato per locale: "parquet" mantiene tipi e null meglio del CSV.
# Usare "csv" se serve un file ispezionabile/apribile subito.
OUTPUT_FORMAT = "parquet"

# Cartella DBFS di output. Databricks scrivera' una directory con part file.
OUTPUT_BASE_PATH = "dbfs:/FileStore/iveco_statistics/fat_table_samples"

# Nome cartella generata sotto OUTPUT_BASE_PATH.
# Esempio: Subset_Config_399_Date_20260511_105916
OUTPUT_FOLDER_TEMPLATE = "Subset_Config_{config}_Date_{timestamp}"


def _parse_config_ids(value):
    parts = str(value).replace(";", ",").replace(" ", ",").split(",")
    config_ids = [int(part.strip()) for part in parts if part.strip()]
    if not config_ids:
        raise ValueError("Config vuota: inserisci almeno un id_config")
    return config_ids


def _get_widget_value(name, default, choices=None):
    """Legge un widget Databricks, creandolo se serve; fuori Databricks usa il default."""
    try:
        dbutils  # noqa: F821 - disponibile in Databricks
    except NameError:
        return default

    try:
        return dbutils.widgets.get(name)  # noqa: F821
    except Exception:
        if choices:
            dbutils.widgets.dropdown(name, str(default), choices, name)  # noqa: F821
        else:
            dbutils.widgets.text(name, str(default), name)  # noqa: F821
        return dbutils.widgets.get(name)  # noqa: F821


def get_runtime_config():
    """Ritorna i parametri runtime, preferendo i widget Databricks."""
    config_text = _get_widget_value(
        "config_ids",
        ",".join(map(str, DEFAULT_CONFIG_IDS)),
    )
    row_limit_text = _get_widget_value("row_limit", str(ROW_LIMIT or ""))
    output_format = _get_widget_value("output_format", OUTPUT_FORMAT, ["parquet", "csv"])
    output_base_path = _get_widget_value("output_base_path", OUTPUT_BASE_PATH)

    row_limit = int(row_limit_text) if str(row_limit_text).strip() else None
    return {
        "config_ids": _parse_config_ids(config_text),
        "row_limit": row_limit,
        "output_format": output_format,
        "output_base_path": output_base_path,
    }


def _get_spark():
    """Ritorna la SparkSession Databricks o ne crea una locale per test minimi."""
    try:
        return spark  # noqa: F821 - variabile globale disponibile in Databricks
    except NameError:
        return SparkSession.builder.appName("iveco-export-config-csv").getOrCreate()


def _unique_keep_order(values):
    """Deduplica mantenendo l'ordine originale."""
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _select_export_columns(df):
    """Seleziona le colonne richieste, oppure tutte le colonne disponibili."""
    if COLUMNS_TO_KEEP is None:
        return df

    available = [col_name for col_name in COLUMNS_TO_KEEP if col_name in df.columns]
    missing = [col_name for col_name in COLUMNS_TO_KEEP if col_name not in df.columns]

    if missing:
        log_step(f"ATTENZIONE: {len(missing)} colonne richieste non presenti nel DataFrame")
        for col_name in missing:
            log_step(f" - mancante: {col_name}")

    if not available:
        raise ValueError("Nessuna colonna valida trovata in COLUMNS_TO_KEEP")

    return df.select([F.col(col_name) for col_name in _unique_keep_order(available)])


def export_fat_table_sample():
    """Carica le fat table richieste e scrive un subset grezzo per sviluppo locale."""
    spark_session = _get_spark()
    runtime_config = get_runtime_config()
    config_ids = runtime_config["config_ids"]
    row_limit = runtime_config["row_limit"]
    output_format = runtime_config["output_format"]
    output_base_path = runtime_config["output_base_path"]

    timestamp = get_current_timestamp()
    config_label = "_".join(map(str, sorted(config_ids)))
    output_folder = OUTPUT_FOLDER_TEMPLATE.format(
        config=config_label,
        timestamp=timestamp,
        format=output_format,
    )
    output_path = f"{output_base_path.rstrip('/')}/{output_folder}"

    log_step(f"Avvio export sample fat table per config: {config_ids}")
    df = import_fat_tables_3(spark_session, config_ids)

    if df is None:
        raise ValueError(f"Nessuna tabella caricata per config {config_ids}")

    report_dim(df, "RAW config dataframe")

    p_type, p_group, p_series = extract_metadata(df)
    log_step(f"Metadata rilevati: type={p_type}, group={p_group}, series={p_series}")

    export_df = _select_export_columns(df)
    log_step(f"Colonne esportate: {len(export_df.columns)}")

    if row_limit is not None:
        log_step(f"Applico ROW_LIMIT={row_limit}")
        export_df = export_df.limit(row_limit)

    report_dim(export_df, "Sample export dataframe")

    log_step(f"Scrittura {output_format} in: {output_path}")
    writer = export_df.coalesce(1).write.mode("overwrite")

    if output_format == "csv":
        writer.option("header", "true").option("delimiter", ";").csv(output_path)
    elif output_format == "parquet":
        writer.parquet(output_path)
    else:
        raise ValueError(f"OUTPUT_FORMAT non supportato: {output_format}")

    log_step("Export sample completato")
    log_step(f"Output path: {output_path}")
    return output_path


if __name__ == "__main__":
    export_fat_table_sample()
