# engine_utils.py
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from datetime import datetime
import time

# --- COSTANTI DI FORMATTAZIONE ---
bold_start = "\033[1m"
bold_end = "\033[0m"

# --- FUNZIONI DI DIAGNOSTICA E REPORT ---

def report_dim(df: DataFrame, name: str = "DataFrame"):
    """Stampa le dimensioni (righe e colonne) del DataFrame."""
    if df is not None:
        try:
            rows = df.count()
            cols = len(df.columns)
            print(f"{bold_start}Dimensioni {name}:{bold_end} {rows} righe, {cols} colonne")
        except Exception as e:
            print(f"Errore nel calcolo dimensioni per {name}: {e}")
    else:
        print(f"{bold_start}{name} è nullo (None).{bold_end}")

def report(df: DataFrame, name: str = "DataFrame"):
    """Esegue un report completo: dimensioni, schema e prime righe."""
    print("-" * 50)
    report_dim(df, name)
    if df is not None:
        df.printSchema()
        # display(df.limit(5)) # Solo se usato in ambiente Databricks
    print("-" * 50)

def report_vin(df: DataFrame):
    """Stampa il numero di VIN (veicoli) unici presenti."""
    if "vin" in df.columns:
        n_vin = df.select("vin").distinct().count()
        print(f"{bold_start}Veicoli (VIN) totali:{bold_end} {n_vin}")
    else:
        print("Colonna 'vin' non trovata.")

# --- FUNZIONI DI GESTIONE TEMPO ---

def last_running():
    """Stampa l'orario dell'ultima esecuzione."""
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%y alle %H:%M:%S")
    print(f"{bold_start}L'ultima esecuzione di questo codice è stata: {dt_string}{bold_end}")

def get_current_timestamp():
    """Ritorna una stringa con il timestamp attuale per i nomi dei file."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# --- HELPER PER EXCEL (Utility di sistema) ---

def check_pandas_compatibility(df_pd):
    """Verifica se il dataframe pandas è pronto per l'export Excel."""
    if df_pd is None or df_pd.empty:
        print(f"{bold_start}ATTENZIONE:{bold_end} Il DataFrame è vuoto.")
        return False
    return True

# --- LOGGING ---

def log_step(message: str):
    """Stampa un messaggio di log formattato con l'ora."""
    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{curr_time}] {message}")