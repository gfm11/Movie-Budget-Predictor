import os
import subprocess
import time
import mysql.connector

# -----------------------------
# 1️⃣ Start MySQL server with local_infile enabled
# -----------------------------
print("Starting MySQL server...")
# Stop MySQL service first (ignore errors)
subprocess.run(["sudo", "service", "mysql", "stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# Start MySQL in the background
subprocess.Popen(["sudo", "mysqld", "--local-infile=1"])
time.sleep(5)  # wait a few seconds for MySQL to start

# -----------------------------
# 3️⃣ Connect as flaskuser to create tables and import CSV
# -----------------------------
print("Connecting as flaskuser and importing CSV...\n")
try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="flaskuser",
        password="password123",
        database="moviebudgetpredictor",
        allow_local_infile=True
    )
except mysql.connector.Error as err:
    print(f"Error connecting as flaskuser: {err}")
    exit(1)

cursor = db.cursor()

# Path to CSV
csv_path = "/workspaces/Movie-Budget-Predictor/data/MovieStatistics.csv"

load_sql = f"""
LOAD DATA LOCAL INFILE '{csv_path}'
INTO TABLE MovieStatistics
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(id, title, vote_average, vote_count, movie_status, release_date, revenue, adult, genres);
"""

try:
    cursor.execute(load_sql)
    db.commit()
    print("CSV imported successfully!\n")
except mysql.connector.Error as err:
    print(f"Error importing CSV: {err}")


# Path to CSV
csv_path2 = "/workspaces/Movie-Budget-Predictor/data/BoxOffice.csv"

load_sql2 = f"""
LOAD DATA LOCAL INFILE '{csv_path2}'
INTO TABLE BoxOffice
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(movie_id, title, movie_rank, worldwide_revenue, domestic_revenue, domestic_percentage);
"""

try:
    cursor.execute(load_sql2)
    db.commit()
    print("CSV imported successfully!\n")
except mysql.connector.Error as err:
    print(f"Error importing CSV: {err}")


print("Setup complete! Your Flask app can now connect using flaskuser.\n")


cursor.execute("SELECT COUNT(*) FROM MovieStatistics;")
count = cursor.fetchone()[0]
print(f"Number of rows in MovieStatistics: {count}")

# Optional: preview the first 5 rows
cursor.execute("SELECT * FROM MovieStatistics LIMIT 5;")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
db.close()