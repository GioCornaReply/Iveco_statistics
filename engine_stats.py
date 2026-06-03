# engine_stats.py
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
import pandas as pd

# --- 1. LOGICA PERCENTUALI ---
def pyspark_variabili_x(df: DataFrame, col_list: list, suffix: str) -> DataFrame:
    if not col_list:
        return df
    safe_cols = [F.coalesce(F.col(c).cast("double"), F.lit(0.0)) for c in col_list]
    df = df.withColumn("total_sum_temp", sum(safe_cols))
    for c in col_list:
        new_name = f"{c.upper()}_{suffix.upper()}"
        safe_value = F.coalesce(F.col(c).cast("double"), F.lit(0.0))
        df = df.withColumn(new_name,
            F.when(F.col("total_sum_temp") > 0, 
                   F.round((safe_value / F.col("total_sum_temp")) * 100, 2))
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
    df_std = grouped.agg(
        F.coalesce(F.round(F.stddev(var_soglia), 2), F.lit(0.0)).alias(stddev_name)
    )
    
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


def report_pivot_pyspark_fixed(
    df3: DataFrame,
    lista: list,
    variabili: list,
    valutazione_triggers: list,
    config_vn=0,
    target_columns=None,
):
    """Versione robusta della pivot legacy: filtra colonne e join senza duplicati."""
    if target_columns:
        target_clean = {col_name.strip().lower() for col_name in target_columns}
        filtered = [
            (col_name, valutazione_triggers[idx])
            for idx, col_name in enumerate(lista)
            if col_name.strip().lower() in target_clean
        ]
        if not filtered:
            print(f"Nessuna target_columns trovata in lista: {target_columns}")
            return None
        lista = [col_name for col_name, _ in filtered]
        valutazione_triggers = [trigger for _, trigger in filtered]

    if len(lista) != len(valutazione_triggers):
        print(f"Mismatch lista/triggers: {len(lista)} vs {len(valutazione_triggers)}")
        return None

    valid_pairs = []
    for col_name, trigger in zip(lista, valutazione_triggers):
        if col_name not in df3.columns:
            print(f"Colonna non presente, salto: {col_name}")
            continue

        valid_pairs.append((col_name, trigger))

    if not valid_pairs:
        return None

    group_filter = None
    for group_col in variabili:
        condition = F.col(f"`{group_col}`").isNotNull()
        group_filter = condition if group_filter is None else group_filter & condition

    df_base = df3
    if group_filter is not None:
        df_base = df_base.filter(group_filter)

    agg_exprs = []
    for col_name, _ in valid_pairs:
        safe_col = F.col(f"`{col_name}`")
        agg_exprs.extend(
            [
                F.round(F.avg(safe_col), 2).alias(col_name),
                F.coalesce(F.round(F.stddev(safe_col), 2), F.lit(0.0)).alias(f"StdDev_{col_name}"),
                F.count(safe_col).alias(f"Count_{col_name}"),
            ]
        )

    df_uno = df_base.groupBy(*variabili).agg(*agg_exprs)

    for col_name, trigger in valid_pairs:
        avg_col = F.col(f"`{col_name}`")
        std_col = F.col(f"`StdDev_{col_name}`")
        advice_name = f"Advice_{col_name}"
        alert_name = f"Alert_{col_name}"

        if trigger == 1:
            df_uno = df_uno.withColumn(advice_name, F.round(avg_col + std_col / 2, 2))
            df_uno = df_uno.withColumn(alert_name, F.round(avg_col + std_col, 2))
        else:
            df_uno = df_uno.withColumn(
                advice_name,
                F.when(avg_col > std_col / 2, F.round(avg_col - std_col / 2, 2)).otherwise(0),
            )
            df_uno = df_uno.withColumn(
                alert_name,
                F.when(avg_col > std_col, F.round(avg_col - std_col, 2)).otherwise(0),
            )

    ordered_columns = list(variabili)
    for col_name, _ in valid_pairs:
        ordered_columns.extend(
            [
                col_name,
                f"StdDev_{col_name}",
                f"Advice_{col_name}",
                f"Alert_{col_name}",
                f"Count_{col_name}",
            ]
        )

    return prep_toPandas(df_uno.select(*ordered_columns))


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


def report_pivot_pyspark(df3: DataFrame, lista: list, variabili: list, valutazione_triggers: list):
    """Compatibilita' con il nome storico: usa la versione robusta."""
    return report_pivot_pyspark_fixed(df3, lista, variabili, valutazione_triggers)
