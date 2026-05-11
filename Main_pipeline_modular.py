# Databricks notebook source
# MAGIC %md
# MAGIC # IVECO Statistics - Modular Main Pipeline
# MAGIC Notebook finale di orchestrazione: la logica vive nei moduli Python, qui si controllano i passaggi.

# COMMAND ----------

from run_local_sample import (
    DEFAULT_FORMAT,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SAMPLE_PATH,
    build_spark,
    build_sheet_outputs,
    export_excel_outputs,
    read_sample,
    validate_config_columns,
)
from engine_cleaning import clean_spark_column_names, keep_latest_record_per_vin
from engine_config import get_default_sheet_ids
from engine_loader import extract_metadata
from engine_utils import log_step, report_dim, report_vin

# COMMAND ----------

sample_path = DEFAULT_SAMPLE_PATH
input_format = DEFAULT_FORMAT
sheet_ids = get_default_sheet_ids()
output_dir = DEFAULT_OUTPUT_DIR
keep_latest_per_vin = True
export_excel = True

log_step(f"Sample path: {sample_path}")
log_step(f"Sheet configurati: {sheet_ids}")

# COMMAND ----------

try:
    spark
except NameError:
    spark = build_spark("iveco-main-pipeline-modular")

df_raw = read_sample(spark, sample_path, input_format)
report_dim(df_raw, "RAW sample")
report_vin(df_raw)

# COMMAND ----------

df_clean = clean_spark_column_names(df_raw)
report_dim(df_clean, "CLEAN sample")

if keep_latest_per_vin:
    df_clean = keep_latest_record_per_vin(df_clean)
    report_dim(df_clean, "LATEST VIN sample")
    report_vin(df_clean)

# COMMAND ----------

p_type, p_group, p_series = extract_metadata(df_clean)
log_step(f"Metadata rilevati: type={p_type}, group={p_group}, series={p_series}")

validation = validate_config_columns(df_clean, p_series, p_group, sheet_ids)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Preview sheet Excel
# MAGIC Ogni output qui sotto corrisponde a un tab che verra' scritto nell'Excel.

# COMMAND ----------

sheet_outputs = build_sheet_outputs(df_clean, validation)

for sheet_output in sheet_outputs:
    sheet_id = sheet_output["sheet_id"]
    sheet_name = sheet_output["sheet_name"]
    validation_entry = sheet_output["validation"]
    df_sheet = sheet_output["dataframe"]

    log_step(
        f"Preview {sheet_id} - {sheet_name}: "
        f"presenti={len(validation_entry['present'])}, "
        f"mancanti={len(validation_entry['missing'])}, "
        f"righe={len(df_sheet)}"
    )

    if validation_entry["missing"]:
        print(f"Colonne mancanti per {sheet_id}: {validation_entry['missing']}")

    try:
        display(df_sheet)
    except NameError:
        print(df_sheet.to_string(index=False))

# COMMAND ----------

if export_excel:
    excel_path = export_excel_outputs(sheet_outputs, output_dir)
    log_step(f"Excel generato: {excel_path}")
else:
    log_step("Export Excel disabilitato")

# COMMAND ----------

log_step("Main pipeline modulare completata")
