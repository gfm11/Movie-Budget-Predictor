import pandas as pd
from sqlalchemy import create_engine

username = 'root'
password = '2dkw38hfksa_i7y5s'
host = 'localhost'
port = 3306
database = 'moviebudgetpredictor'

engine = create_engine(f"mysql+pymysql://root:2dkw38hfksa_i7y5s@localhost:3306/moviebudgetpredictor")

excel_file = 'data/MovieStatistics.csv'
table_name = 'MovieStatistics'
chunk_size = 10000

print(f"Starting import of '{excel_file}' into table '{table_name}' in chunks of {chunk_size} rows...")

csv_iter = pd.read_csv(csv_file, chunksize=chunk_size)

for i, chunk in enumerate(excel_iter):
    chunk.to_sql(table_name, con=engine, if_exists='append', index=False)
    print(f"Imported chunk {i+1} ({len(chunk)} rows)")

print(f"Data successfully imported into table '{table_name}' in database '{database}'.")