# export_config_csv.py
#
# Script Databricks per esportare un subset grezzo delle fat table.
# Uso previsto:
# 1. Modificare CONFIG_IDS / ROW_LIMIT / OUTPUT_BASE_PATH qui sotto.
# 2. Pushare il file su GitHub e pullarlo in Databricks Repos.
# 3. Eseguirlo su cluster cliente.
# 4. Recuperare la cartella generata da DBFS e usarla in locale come sample.

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from engine_loader import extract_metadata, import_fat_tables_3
from engine_utils import get_current_timestamp, log_step, report_dim


# ---------------------------------------------------------------------------
# CONFIGURAZIONE MANUALE
# ---------------------------------------------------------------------------

# Esempio: 49 per VODR, 399/400/401/402 per Mission Test statistics.
CONFIG_IDS = [49]

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
    timestamp = get_current_timestamp()
    config_label = "_".join(map(str, sorted(CONFIG_IDS)))
    output_folder = OUTPUT_FOLDER_TEMPLATE.format(
        config=config_label,
        timestamp=timestamp,
        format=OUTPUT_FORMAT,
    )
    output_path = f"{OUTPUT_BASE_PATH}/{output_folder}"

    log_step(f"Avvio export sample fat table per config: {CONFIG_IDS}")
    df = import_fat_tables_3(spark_session, CONFIG_IDS)

    if df is None:
        raise ValueError(f"Nessuna tabella caricata per config {CONFIG_IDS}")

    report_dim(df, "RAW config dataframe")

    p_type, p_group, p_series = extract_metadata(df)
    log_step(f"Metadata rilevati: type={p_type}, group={p_group}, series={p_series}")

    export_df = _select_export_columns(df)
    log_step(f"Colonne esportate: {len(export_df.columns)}")

    if ROW_LIMIT is not None:
        log_step(f"Applico ROW_LIMIT={ROW_LIMIT}")
        export_df = export_df.limit(ROW_LIMIT)

    report_dim(export_df, "Sample export dataframe")

    log_step(f"Scrittura {OUTPUT_FORMAT} in: {output_path}")
    writer = export_df.coalesce(1).write.mode("overwrite")

    if OUTPUT_FORMAT == "csv":
        writer.option("header", "true").option("delimiter", ";").csv(output_path)
    elif OUTPUT_FORMAT == "parquet":
        writer.parquet(output_path)
    else:
        raise ValueError(f"OUTPUT_FORMAT non supportato: {OUTPUT_FORMAT}")

    log_step("Export sample completato")
    log_step(f"Output path: {output_path}")
    return output_path


if __name__ == "__main__":
    export_fat_table_sample()
