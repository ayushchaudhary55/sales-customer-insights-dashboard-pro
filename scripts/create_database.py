import sqlite3, pandas as pd
from pathlib import Path
DATA_PATH=Path('data/sales_customer_data.csv'); DB_PATH=Path('data/sales_dashboard.db')
df=pd.read_csv(DATA_PATH); conn=sqlite3.connect(DB_PATH); df.to_sql('sales_orders',conn,if_exists='replace',index=False); conn.close()
print(f'SQLite database created successfully at {DB_PATH}')
