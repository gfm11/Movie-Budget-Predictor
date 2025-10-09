import pandas as pd
from sqlalchemy import create_engine

username = 'root'
password = '2dkw38hfksa_i7y5s'
host = 'localhost'
port = 3360
database = 'moviebudgetpredictor'

engine = create_engine(f"mysql+pymysql://root:2dkw38hfksa_i7y5s@localhost:3360/moviebudgetpredictor")

excel_file = 'MovieStatistics.xlsx'
sheet_name = 'Movie_Stats' 

df = pd.read_excel('MovieStatistics.xlsx', sheet_name='Movie_Stats')

table_name = 'MovieStatistics'

df.to_sql(table_name, con=engine, if_exists='append', index=False)

print(f"Data successfully imported into table '{table_name}' in database '{database}'.")