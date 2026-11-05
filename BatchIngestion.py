import os
import pandas as pd
import sqlalchemy as sa
from datetime import datetime

# 1. INITIALIZATION & CONFIGURATION
# Database connection string (e.g., PostgreSQL, MySQL, SQL Server)
DATABASE_URL = os.getenv("ERP_DB_URL", "sqlite:///erp_source.db")
TARGET_STORAGE = "./data_warehouse/sales_fact/"

def get_db_engine():
    return sa.create_engine(DATABASE_URL)

# 2. EXTRACT PROCESS (Incremental Load)
def extract_new_data(last_run_date: str) -> pd.DataFrame:
    """Extracts data modified after the last successful run pipeline date."""
    engine = get_db_engine()
    query = """
        SELECT id, order_date, customer_id, gross_amount, country 
        FROM erp_sales 
        WHERE updated_at > :last_date
    """
    print(f"Executing extraction since: {last_run_date}")
    df = pd.read_sql_query(sa.text(query), con=engine, params={"last_date": last_run_date})
    return df

# 3. CLEANSE & TRANSFORM PROCESS
def cleanse_data(df: pd.DataFrame) -> pd.DataFrame:
    """Handles missing values, standardizes dates, and filters anomalies."""
    if df.empty:
        print("No new data to cleanse.")
        return df
    
    # Drop rows missing critical identifiers
    df = df.dropna(subset=['customer_id'])
    
    # Standardize and fix messy date formats
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df = df.dropna(subset=['order_date']) # Drop completely unparseable dates
    
    # Cleanse financial anomalies (e.g., negative prices due to entry errors)
    df['gross_amount'] = pd.to_numeric(df['gross_amount'], errors='coerce')
    df['gross_amount'] = df['gross_amount'].apply(lambda x: 0.0 if x < 0 or pd.isna(x) else x)
    
    # Standardize text strings
    df['country'] = df['country'].str.upper().str.strip().fillna('UNKNOWN')
    
    return df

# 4. LOAD PROCESS
def load_to_warehouse(df: pd.DataFrame):
    """Loads cleansed data into a partitioned columnar format (Parquet)."""
    if df.empty:
        return
    
    os.makedirs(TARGET_STORAGE, exist_ok=True)
    
    # Generate a timestamp for the batch file to prevent overwrites
    batch_ts = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = f"{TARGET_STORAGE}batch_{batch_ts}.parquet"
    
    # Save to Parquet format (highly efficient for data warehouses)
    df.to_parquet(file_path, index=False, compression='snappy')
    print(f"Successfully loaded {len(df)} records into warehouse at {file_path}")

# Pipeline Execution Orchestrator
def run_batch_pipeline():
    # In a real environment, retrieve 'last_run_date' from a metadata DB or Airflow context
    LAST_RUN_DATE = "2026-11-01 00:00:00" 
    
    raw_data = extract_new_data(LAST_RUN_DATE)
    cleaned_data = cleanse_data(raw_data)
    load_to_warehouse(cleaned_data)

if __name__ == "__main__":
    run_batch_pipeline()
