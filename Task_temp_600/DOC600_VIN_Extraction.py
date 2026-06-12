# Databricks notebook source
# MAGIC %md
# MAGIC # Estrazione one-shot VIN con secondi > 600 C
# MAGIC 
# MAGIC Notebook temporaneo per verificare la richiesta cliente sul VIN `ZCFCE35B505652215` e per estrarre tutti i VIN che hanno secondi valorizzati nella variabile `Temperatureupstr_DOC_600`.
# MAGIC 
# MAGIC Nota operativa: questo notebook lavora prima sui dati raw/all updates. Solo dopo confronta il record latest per VIN, per evidenziare eventuali casi che spariscono se si deduplica.

# COMMAND ----------
from pathlib import Path

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.utils import AnalysisException

try:
    spark
except NameError:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.appName("task-temp-600-vin-check").getOrCreate()

def log_step(message):
    print(f"[TASK_TEMP_600] {message}")

def report_dim(df, name):
    print(f"{name}: {df.count()} rows, {len(df.columns)} columns")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Parametri
# MAGIC 
# MAGIC Default coerenti con `MT_DAILY_PREP.ipynb`: config `382`, Daily MY 2024, colonna `Temperatureupstr_DOC_600`.

# COMMAND ----------
DEFAULT_CONFIG = "382"
DEFAULT_TARGET_VIN = "ZCFCE35B505652215"
DEFAULT_SECONDS_COLUMN = "Temperatureupstr_DOC_600"
DEFAULT_SECONDS_THRESHOLD = "0"

try:
    dbutils.widgets.text("config", DEFAULT_CONFIG, "Config fat table")
    dbutils.widgets.text("target_vin", DEFAULT_TARGET_VIN, "VIN da verificare")
    dbutils.widgets.text("seconds_column", DEFAULT_SECONDS_COLUMN, "Colonna secondi >600 C")
    dbutils.widgets.text("seconds_threshold", DEFAULT_SECONDS_THRESHOLD, "Soglia secondi")

    config_text = dbutils.widgets.get("config")
    target_vin = dbutils.widgets.get("target_vin")
    seconds_column_hint = dbutils.widgets.get("seconds_column")
    seconds_threshold = float(dbutils.widgets.get("seconds_threshold"))
except NameError:
    config_text = DEFAULT_CONFIG
    target_vin = DEFAULT_TARGET_VIN
    seconds_column_hint = DEFAULT_SECONDS_COLUMN
    seconds_threshold = float(DEFAULT_SECONDS_THRESHOLD)

config = {int(part.strip()) for part in str(config_text).replace(";", ",").replace(" ", ",").split(",") if part.strip()}
target_vin_norm = target_vin.strip().upper()

log_step(f"Config: {sorted(config)}")
log_step(f"Target VIN: {target_vin_norm}")
log_step(f"Colonna richiesta: {seconds_column_hint}")
log_step(f"Soglia secondi: > {seconds_threshold}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Lettura fat table raw
# MAGIC 
# MAGIC Il notebook prova piu' naming storici/Databricks per evitare dipendenze dal vecchio `../Utils`.

# COMMAND ----------
def candidate_table_paths(config_id):
    return [
        f"missiontest.fat_table_{config_id}",
        f"missiontest.fat_table_easy_{config_id}",
        f"u_truck_analyzer_p.mission_test_statistics.fat_table_{config_id}",
    ]

def read_one_config(config_id):
    errors = []
    for table_path in candidate_table_paths(config_id):
        try:
            df = spark.sql(f"SELECT * FROM {table_path}")
            log_step(f"Caricata tabella {table_path}")
            return df.withColumn("_source_table", F.lit(table_path))
        except AnalysisException as exc:
            errors.append(f"{table_path}: {exc}")

    raise FileNotFoundError(f"Nessuna fat table caricata per config {config_id}.\
" + "\
".join(errors))

df_raw = None
for cfg in sorted(config):
    df_cfg = read_one_config(cfg)
    df_raw = df_cfg if df_raw is None else df_raw.unionByName(df_cfg, allowMissingColumns=True)

report_dim(df_raw, "df_raw")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Risoluzione colonne
# MAGIC 
# MAGIC Qui evitiamo problemi di maiuscole/minuscole: `Temperatureupstr_DOC_600` e `Temperatureupstr_doc_600` vengono risolte case-insensitive.

# COMMAND ----------
def find_column(df, candidates):
    by_lower = {col_name.lower(): col_name for col_name in df.columns}
    for candidate in candidates:
        found = by_lower.get(candidate.lower())
        if found:
            return found
    return None

seconds_col = find_column(df_raw, [seconds_column_hint, "Temperatureupstr_DOC_600", "Temperatureupstr_doc_600"])
vin_col = find_column(df_raw, ["vin"])
timestamp_col = find_column(df_raw, ["udt_timestamp", "easy_timestamp", "utc_datetime"])
km_col = find_column(df_raw, ["cov_div_len", "cov_driv_len_DPF", "mileage"])

if seconds_col is None:
    columns_600 = [c for c in df_raw.columns if "600" in c.lower()]
    raise ValueError(f"Colonna secondi >600 C non trovata. Colonne candidate con '600': {columns_600}")
if vin_col is None:
    raise ValueError("Colonna VIN non trovata")
if timestamp_col is None:
    raise ValueError("Colonna timestamp non trovata tra udt_timestamp/easy_timestamp/utc_datetime")

log_step(f"VIN column: {vin_col}")
log_step(f"Timestamp column: {timestamp_col}")
log_step(f"Km column: {km_col}")
log_step(f"Seconds column: {seconds_col}")

matching_temperature_columns = [c for c in df_raw.columns if any(token in c.lower() for token in ["600", "900", "temp", "scr", "doc", "dpf"])]
print("Colonne temperatura/600 disponibili:")
for col_name in matching_temperature_columns:
    print(" -", col_name)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Base normalizzata
# MAGIC 
# MAGIC Manteniamo tutte le righe raw e calcoliamo anche il rank latest per VIN.

# COMMAND ----------
metadata_cols = [
    "request_code", "id_config", "product_type", "product_group", "product_series",
    "product_model", "commercial_model", "dealer", "customer", "engine_code", "power", "fdp"
]
metadata_cols = [c for c in metadata_cols if c in df_raw.columns]

select_exprs = [
    F.upper(F.trim(F.col(vin_col).cast("string"))).alias("vin"),
    F.col(timestamp_col).cast("timestamp").alias("event_timestamp"),
    F.col(seconds_col).cast("double").alias("seconds_over_600c"),
]
if km_col:
    select_exprs.append(F.col(km_col).cast("double").alias("km_value"))
else:
    select_exprs.append(F.lit(None).cast("double").alias("km_value"))

select_exprs.extend([F.col(c) for c in metadata_cols])
select_exprs.append(F.col("_source_table"))

df_base = df_raw.select(*select_exprs)
df_base = df_base.withColumn(
    "is_over_threshold",
    F.col("seconds_over_600c").isNotNull() & (F.col("seconds_over_600c") > F.lit(seconds_threshold)),
)

latest_window = Window.partitionBy("vin").orderBy(F.col("event_timestamp").desc_nulls_last())
df_base = df_base.withColumn("latest_rank", F.row_number().over(latest_window))

report_dim(df_base, "df_base raw/all updates")
df_base.select("vin", "event_timestamp", "seconds_over_600c", "km_value", "latest_rank", *metadata_cols).display()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Verifica VIN email Luigi
# MAGIC 
# MAGIC Questa cella mostra tutte le righe raw del VIN `ZCFCE35B505652215`, incluse eventuali righe non latest.

# COMMAND ----------
df_target_all_updates = df_base.filter(F.col("vin") == target_vin_norm).orderBy("event_timestamp")
report_dim(df_target_all_updates, f"target VIN {target_vin_norm} - all updates")
df_target_all_updates.display()

df_target_over_600 = df_target_all_updates.filter(F.col("is_over_threshold"))
report_dim(df_target_over_600, f"target VIN {target_vin_norm} - seconds_over_600c > {seconds_threshold}")
df_target_over_600.display()

df_target_latest = df_target_all_updates.filter(F.col("latest_rank") == 1)
report_dim(df_target_latest, f"target VIN {target_vin_norm} - latest only")
df_target_latest.display()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Estrazione tutti i VIN con secondi > 600 C
# MAGIC 
# MAGIC Questo e' l'output principale da consegnare/controllare: una riga per VIN con conteggi e massimo tempo osservato.

# COMMAND ----------
df_all_over_600_rows = df_base.filter(F.col("is_over_threshold"))

df_vin_summary_over_600 = (
    df_all_over_600_rows
    .groupBy("vin")
    .agg(
        F.count("*").alias("records_over_600c"),
        F.round(F.sum("seconds_over_600c"), 2).alias("total_seconds_over_600c"),
        F.round(F.max("seconds_over_600c"), 2).alias("max_seconds_over_600c"),
        F.min("event_timestamp").alias("first_event_timestamp"),
        F.max("event_timestamp").alias("last_event_timestamp"),
        F.round(F.min("km_value"), 2).alias("min_km_value"),
        F.round(F.max("km_value"), 2).alias("max_km_value"),
    )
    .orderBy(F.col("max_seconds_over_600c").desc(), F.col("total_seconds_over_600c").desc(), "vin")
)

report_dim(df_all_over_600_rows, f"righe raw con seconds_over_600c > {seconds_threshold}")
report_dim(df_vin_summary_over_600, f"VIN distinti con seconds_over_600c > {seconds_threshold}")
df_vin_summary_over_600.display()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Confronto raw vs latest
# MAGIC 
# MAGIC Serve per capire se stiamo perdendo VIN quando si tiene solo l'ultimo aggiornamento.

# COMMAND ----------
df_latest_only = df_base.filter(F.col("latest_rank") == 1)
df_raw_vins = df_all_over_600_rows.select("vin").distinct().withColumn("found_in_raw_all_updates", F.lit(True))
df_latest_vins = df_latest_only.filter(F.col("is_over_threshold")).select("vin").distinct().withColumn("found_in_latest_only", F.lit(True))

df_raw_vs_latest = (
    df_raw_vins
    .join(df_latest_vins, on="vin", how="left")
    .fillna(False, subset=["found_in_latest_only"])
    .withColumn("would_be_lost_by_latest_filter", F.col("found_in_raw_all_updates") & ~F.col("found_in_latest_only"))
    .orderBy(F.col("would_be_lost_by_latest_filter").desc(), "vin")
)

report_dim(df_raw_vs_latest.filter(F.col("would_be_lost_by_latest_filter")), "VIN over 600 C persi usando latest only")
df_raw_vs_latest.display()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Dettaglio righe da esportare
# MAGIC 
# MAGIC Tabella dettagliata di tutte le righe raw che hanno secondi > 600 C.

# COMMAND ----------
detail_order_cols = ["vin", "event_timestamp", "seconds_over_600c", "km_value", "latest_rank"]
df_detail_over_600 = df_all_over_600_rows.select(*detail_order_cols, *metadata_cols, "_source_table").orderBy(
    F.col("seconds_over_600c").desc(), "vin", "event_timestamp"
)

df_detail_over_600.display()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Export opzionale su DBFS/FileStore
# MAGIC 
# MAGIC Esporta summary, dettaglio e controllo raw-vs-latest in CSV. Il path e' pensato per download da browser Databricks.

# COMMAND ----------
EXPORT_RESULTS = True
dbfs_output_base = "dbfs:/FileStore/iveco_statistics_output/task_temp_600"

if EXPORT_RESULTS:
    outputs = {
        "vin_summary_over_600": df_vin_summary_over_600,
        "detail_rows_over_600": df_detail_over_600,
        "raw_vs_latest_check": df_raw_vs_latest,
        "target_vin_all_updates": df_target_all_updates,
    }

    for name, df_out in outputs.items():
        output_path = f"{dbfs_output_base}/{name}"
        df_out.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)
        log_step(f"Esportato {name}: {output_path}")

    try:
        workspace_url = spark.conf.get("spark.databricks.workspaceUrl", None)
        if workspace_url:
            print(f"Download folder: https://{workspace_url}/files/iveco_statistics_output/task_temp_600/")
    except Exception:
        pass
else:
    log_step("Export disabilitato")

# COMMAND ----------
