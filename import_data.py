import pandas as pd
from sqlalchemy import create_engine

username = 'root'
password = '2dkw38hfksa_i7y5s'
host = 'localhost'
port = 3306
database = 'moviebudgetpredictor'

engine = create_engine(f"mysql+pymysql://root:2dkw38hfksa_i7y5s@localhost:3306/moviebudgetpredictor")

excel_file = 'data/MovieStatistics.xlsx'
sheet_name = 'movie_stats' 

df = pd.read_excel(excel_file, sheet_name=sheet_name)

table_name = 'MovieStatistics'

df.to_sql(table_name, con=engine, if_exists='append', index=False)

print(f"Data successfully imported into table '{table_name}' in database '{database}'.")