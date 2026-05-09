# engine_stats.py
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
import pandas as pd

# --- 1. LOGICA PERCENTUALI ---
def pyspark_variabili_x(df: DataFrame, col_list: list, suffix: str) -> DataFrame:
    if not col_list:
        return df
    df = df.withColumn("total_sum_temp", sum([F.col(c) for c in col_list]))
    for c in col_list:
        new_name = f"{c.upper()}_{suffix.upper()}"
        df = df.withColumn(new_name, 
            F.when(F.col("total_sum_temp") > 0, 
                   F.round((F.col(c) / F.col("total_sum_temp")) * 100, 2))
             .otherwise(0)
        )
    return df.drop("total_sum_temp")

# --- 2. LOGICA SOGLIE (CORRETTA PER EVITARE AMBIGUITÀ) ---
def new_soglie_pyspark(df2: DataFrame, var_soglia: str, var_altre: list, valutazione_trigger: int) -> DataFrame:
    variabili = [var_soglia] + var_altre
    df_new = df2.select(variabili).dropna(how="any", subset=[var_soglia])
    
    grouped = df_new.groupby(var_altre)
    
    # Nomi unici per evitare AMBIGUOUS_REFERENCE
    avg_name = var_soglia
    stddev_name = f"StdDev_{var_soglia}"
    advice_name = f"Advice_{var_soglia}"
    alert_name = f"Alert_{var_soglia}"
    
    df_mean = grouped.agg(F.round(F.avg(var_soglia), 2).alias(avg_name))
    df_std = grouped.agg(F.round(F.stddev(var_soglia), 2).alias(stddev_name))
    
    df_table = df_mean.join(df_std, var_altre).dropna(how="any")
    
    if valutazione_trigger == 1:
        df_table = df_table.withColumn(advice_name, F.round(F.col(avg_name) + F.col(stddev_name) / 2, 2))
        df_table = df_table.withColumn(alert_name, F.round(F.col(avg_name) + F.col(stddev_name), 2))
    else:
        df_table = df_table.withColumn(advice_name, 
            F.when(F.col(avg_name) > F.col(stddev_name) / 2, 
                   F.round(F.col(avg_name) - F.col(stddev_name) / 2, 2)).otherwise(0))
        df_table = df_table.withColumn(alert_name, 
            F.when(F.col(avg_name) > F.col(stddev_name), 
                   F.round(F.col(avg_name) - F.col(stddev_name), 2)).otherwise(0))

    grouped_counts = grouped.count().withColumnRenamed("count", f"Count_{var_soglia}")
    df_table = df_table.join(grouped_counts, var_altre)
    
    return df_table

# --- 3. PIVOT E PREPARAZIONE ---
def prep_toPandas(df: DataFrame) -> pd.DataFrame:
    # Usiamo un trick per gestire le colonne ambigue se fossero rimaste, 
    # ma con i nomi unici sopra non dovrebbe più servire.
    for col_name in df.columns:
        dtype = dict(df.dtypes)[col_name]
        if "decimal" in dtype or "double" in dtype:
            # Usiamo F.col con il nome esatto per sicurezza
            df = df.withColumn(col_name, F.col(f"`{col_name}`").cast("float"))
    
    return df.toPandas()

def report_pivot_pyspark(df3: DataFrame, lista: list, variabili: list, valutazione_triggers: list):
    df_uno = None
    for i in range(len(lista)):
        try:
            df_temp = new_soglie_pyspark(df3, lista[i], variabili, valutazione_triggers[i])
            if df_uno is None:
                df_uno = df_temp
            else:
                # Mantieni solo il conteggio dell'ultima colonna o gestisci i drop
                df_uno = df_uno.join(df_temp, on=variabili, how="outer")
        except Exception as e:
            print(f"⚠️ Errore su {lista[i]}: {e}")
            continue

    if df_uno is not None:
        return prep_toPandas(df_uno)
    return None