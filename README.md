
1. Imports and Setup

• import os: Loads tools to interact with your computer's operating system (like reading environment variables or folders).
• import pandas as pd: Loads Pandas, a popular library for working with tables of data (DataFrames).
• import sqlalchemy as sa: Loads SQLAlchemy, a tool to connect to and query relational databases.
• from datetime import datetime: Imports a tool to get current dates and times.
• DATABASE_URL = os.getenv(...): Looks for a database connection string in your system settings; if it finds none, it defaults to a local SQLite file named erp_source.db.
• TARGET_STORAGE = './data_warehouse/sales_fact/': Sets the folder path where the final processed data files will be saved.
• def get_db_engine():: Defines a function that creates the database connection.
• return sa.create_engine(DATABASE_URL): Returns the active database engine object.

2. Extract Process

• def extract_new_data(last_run_date: str) -> pd.DataFrame:: Defines a function that grabs new records added after a specific timestamp.
• engine = get_db_engine(): Calls the function above to get the database connection.
• query = ...: Writes a SQL command to select id, order_date, customer_id, gross_amount, and country from the erp_sales table where updated_at is newer than last_date.
• print(...): Prints a status message showing the start date of the data pull.
• df = pd.read_sql_query(...): Runs the SQL query on the database and loads the results into a Pandas table (DataFrame).
• return df: Sends the raw table back to whoever called the function.

3. Cleanse and Transform Process

• def cleanse_data(df: pd.DataFrame) -> pd.DataFrame:: Defines a function to clean up messy data.
• if df.empty:: Checks if the table has zero rows.
• print(...) & return df: If the table is empty, it prints a message and stops early.
• df = df.dropna(subset=['customer_id']): Deletes any row that is missing a customer_id.
• df['order_date'] = ...: Converts the order_date column into actual date-time objects (turning garbage text into NaT or "Not a Time").
• df = df.dropna(subset=['order_date']): Deletes any row where the date could not be fixed.
• df['gross_amount'] = ...: Converts gross_amount into numbers.
• df['gross_amount'] = df['gross_amount'].apply(...): Replaces negative numbers or missing values with 0.0.
• df['country'] = ...: Turns country names into uppercase, trims extra spaces, and replaces blank values with 'UNKNOWN'.
• return df: Sends the cleaned table back.

4. Load Process

• def load_to_warehouse(df: pd.DataFrame):: Defines a function to save the clean data.
• if df.empty: return: Stops the function if there is no data to save.
• os.makedirs(TARGET_STORAGE, exist_ok=True): Creates the destination folder if it does not already exist.
• batch_ts = datetime.now().strftime('%Y%m%d%H%M%S'): Generates a timestamp string (e.g., 20261105115201) to make a unique file name.
• file_path = ...: Builds the full file path ending in .parquet.
• df.to_parquet(...): Saves the table into a columnar Parquet file using Snappy compression.
• print(...): Prints a confirmation message with the record count and file location.

5. Orchestrator and Execution

• def run_batch_pipeline():: Defines the main function that runs the entire workflow in order.
• LAST_RUN_DATE = '2026-11-01 00:00:00': Hardcodes the starting cutoff date for this batch run.
• raw_data = extract_new_data(...): Runs step 2 to pull the data.
• cleaned_data = cleanse_data(raw_data): Runs step 3 to clean the data.
• load_to_warehouse(cleaned_data): Runs step 4 to save the data.
• if __name__ == '__main__':: Checks if the script is run directly from the terminal.
• run_batch_pipeline(): Triggers the main pipeline function.
