# engine_loader.py
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

def get_table_path(val):
    """Gestisce i percorsi delle tabelle in base alla config."""
    if val in {36, 76, 77}:
        return f"missiontest.fat_table_easy_{val}"
    elif val == 49:
        return f"u_truck_analyzer_p.vodr_statistics.fat_table_{val}"
    elif val in {399, 400, 401, 402}:
        return f"u_truck_analyzer_p.mission_test_statistics.fat_table_{val}"
    elif val < 100:
        return f"vodr.fat_table_{val}"
    elif val > 250:
        return f"missiontest.fat_table_{val}"
    return None

def import_fat_tables_3(spark, config):
    """Importa e unisce le tabelle."""
    c = list(sorted(config)) if isinstance(config, (set, list)) else [config]
    df = None
    for val in c:
        table_path = get_table_path(val)
        if not table_path: continue
        try:
            temp_df = spark.sql(f"SELECT * FROM {table_path}")
            df = temp_df if df is None else df.unionByName(temp_df, allowMissingColumns=True)
            print(f"✅ Caricata: {table_path}")
        except:
            print(f"❌ Tabella {table_path} non trovata.")
    return df

def get_export_file_name(product_group, config):
    """Genera il nome del file Excel."""
    config_str = "_".join(map(str, sorted(config)))
    mapping = {
        "EUROCARGO": "EUROCARGO",
        "IVECO_S_WAY": "HEAVY_SWAY",
        "IVECO_X_WAY": "HEAVY_XWAY",
        "IVECO_T_WAY": "HEAVY_TWAY"
    }
    prefix = mapping.get(product_group, "GENERIC")
    return f"Statistics_{prefix}_{config_str}_dataset.xlsx"

def extract_metadata(df):
    """
    Estrae i VALORI REALI dalle celle del DataFrame.
    Risolve l'errore 'series/group' leggendo il contenuto della riga.
    """
    try:
        # Peschiamo la prima riga
        row = df.select("product_type", "product_group", "product_series").first()
        if not row:
            return "UNKNOWN", "UNKNOWN", "UNKNOWN"

        # Trasformiamo in dizionario per evitare confusione tra nomi colonne e valori
        data = row.asDict()
        
        def clean(v):
            if v is None: return "UNKNOWN"
            # Pulizia: tutto maiuscolo, spazi/trattini/slash diventano underscore
            return str(v).strip().upper().replace(" ", "_").replace("-", "_").replace("/", "_")

        p_type = clean(data.get("product_type"))
        p_group = clean(data.get("product_group"))
        p_series = clean(data.get("product_series"))

        return p_type, p_group, p_series
    except Exception as e:
        print(f"❌ Errore estrazione metadati: {e}")
        return "ERROR", "ERROR", "ERROR"

# Le funzioni Delta rimangono qui perché riguardano il caricamento/salvataggio
def save_to_delta(df, table_name):
    path = f"dbfs:/mnt/truck_analyzer/checkpoints/{table_name}"
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(path)

def load_from_delta(spark, table_name):
    path = f"dbfs:/mnt/truck_analyzer/checkpoints/{table_name}"
    return spark.read.format("delta").load(path)