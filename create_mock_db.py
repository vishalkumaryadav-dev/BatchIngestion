import sqlite3
import pandas as pd

# Connect to the local SQLite file
conn = sqlite3.connect('erp_source.db')

# Create mock data matching the script's query schema
mock_data  = pd.DataFrame({
    'id': [1, 2, 3],
    'order_date': ['2026-11-02', '2026-11-03', '2026-11-04'],
    'customer_id': [101, 102, None], # Row 3 will get dropped due to missing customer_id
    'gross_amount': [500.50, -20.00, 150.00], # Row 2 amount will be forced to 0.0
    'country': [' usa ', 'DE', 'ca'],
    'updated_at': ['2026-11-02 10:00:00', '2026-11-03 14:00:00', '2026-11-04 09:00:00']
})

# Write it to the erp_sales table
mock_data.to_sql('erp_sales', conn, if_exists='replace', index=False)
conn.close()
print("Mock database 'erp_source.db' created successfully!")
