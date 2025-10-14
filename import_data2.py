import pandas as pd
from sqlalchemy import create_engine, inspect

username = 'root'
password = '2dkw38hfksa_i7y5s'
host = 'localhost'
port = 3306
database = 'moviebudgetpredictor'

engine = create_engine(f"mysql+pymysql://root:2dkw38hfksa_i7y5s@localhost:3306/moviebudgetpredictor")

csv_file = 'data/MovieStatistics.csv'
table_name = 'MovieStatistics'
chunk_size = 10000

inspector = inspect(engine)
db_columns = [col['name'] for col in inspector.get_columns(table_name)]
print(f"Database columns: {db_columns}")

print(f"Starting import of '{csv_file}' into table '{table_name}' in chunks of {chunk_size} rows...")

csv_iter = pd.read_csv(csv_file, chunksize=chunk_size)

for chunk in pd.read_csv(csv_file, chunksize=chunk_size):

    filtered_chunk = chunk[db_columns].copy()
    filtered_chunk = filtered_chunk[filtered_chunk['release_date'] >= '2000-01-01']
    filtered_chunk.reset_index(drop=True, inplace=True)

    try:
        filtered_chunk.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Inserted chunk of {len(filtered_chunk)} rows.")
    except Exception as e:
        print("Error inserting chunk:", e)

print("Import complete!")