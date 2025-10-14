import pandas as pd
from sqlalchemy import create_engine, inspect

username = 'root'
password = '2dkw38hfksa_i7y5s'
host = 'localhost'
port = 3306
database = 'moviebudgetpredictor'

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

csv_file = 'data/BoxOffice.csv'
table_name = 'BoxOffice'

inspector = inspect(engine)
db_columns = [col['name'] for col in inspector.get_columns(table_name)]
print(f"Database columns: {db_columns}")

df = pd.read_csv(csv_file, encoding='latin1')

df = df[[col for col in df.columns if col in db_columns]]

if 'movie_id' in df.columns:
    df = df.dropna(subset=['movie_id'])

print(f"Prepared {len(df)} valid rows for insertion.")

try:
    df.to_sql(table_name, con=engine, if_exists='append', index=False)
    print(f"Data successfully imported into table '{table_name}' in database '{database}'.")
except Exception as e:
    print("Error inserting data:", e)