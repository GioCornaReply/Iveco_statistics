#Per tutte le funzioni che puliscono i nomi delle colonne e gestiscono i duplicati.

# engine_cleaning.py
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
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

# --- NORMALIZZAZIONE MODELLI MOTORE ---

def engine_model_standard(df: DataFrame) -> DataFrame:
    """Mappatura standard per i modelli motore basata sui codici prodotto."""
    return df.withColumn("engine_model", 
        F.when(F.col("product_model").startswith("F1A"), "F1A")
         .when(F.col("product_model").startswith("F1C"), "F1C")
         .when(F.col("product_model").startswith("F4AF"), "Tector 5")
         .when(F.col("product_model").startswith("F4BE"), "Tector 7")
         .when(F.col("product_model").startswith("F2BE"), "Cursor 9")
         .when(F.col("product_model").startswith("F3GE"), "Cursor 11")
         .when(F.col("product_model").startswith("F3HE"), "Cursor 13")
         .otherwise("Unknown")
    )

# --- RIDENOMINAZIONE UFFICIALE ---

def rename_official(df: DataFrame, variables_names_df: DataFrame, config_list: set) -> DataFrame:
    """
    Mappa i nomi tecnici delle colonne sui nomi leggibili definiti nel mapping.
    """
    # Trasforma il mapping in un dizionario per una sostituzione veloce
    mapping = {row['item_name']: row['my_variable_name'] 
               for row in variables_names_df.collect() 
               if row['id_config'] in config_list}
    
    for old_name, new_name in mapping.items():
        if old_name in df.columns:
            df = df.withColumnRenamed(old_name, new_name)
    return df

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