import mysql.connector
import subprocess
import os
import time

# --- Step 1: Start MySQL server ---
print("Starting MySQL server...")
subprocess.run(["sudo", "service", "mysql", "start"])
time.sleep(2)

# --- Step 2: Ensure flaskuser exists (run as root safely) ---
print("Ensuring flaskuser exists...")
create_user_sql = """
CREATE USER IF NOT EXISTS 'flaskuser'@'localhost' IDENTIFIED BY 'flaskpass';
GRANT ALL PRIVILEGES ON *.* TO 'flaskuser'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
"""
subprocess.run(["sudo", "mysql", "-e", create_user_sql])
print("✅ flaskuser verified and ready.")

# --- Step 3: Connect as flaskuser ---
try:
    db = mysql.connector.connect(
        host="localhost",
        user="flaskuser",
        password="flaskpass",
        allow_local_infile=True
    )
    cursor = db.cursor()
    print("Connected as flaskuser!")
except mysql.connector.Error as err:
    print(f"Error connecting as flaskuser: {err}")
    exit(1)

# --- Step 4: Create and select database ---
cursor.execute("CREATE DATABASE IF NOT EXISTS moviebudgetpredictor;")
cursor.execute("USE moviebudgetpredictor;")

# --- Step 5: Create table if not exists ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS MovieStatistics (
    id INT PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    vote_average FLOAT,
    vote_count INT,
    movie_status VARCHAR(40) NOT NULL,
    release_date DATE,
    revenue BIGINT,
    adult CHAR(1),
    genres VARCHAR(300)
);
""")

# --- Step 6: Import CSV ---
print("\nConnecting as flaskuser and importing CSV...\n")

# Path to CSV
csv_path = "/workspaces/Movie-Budget-Predictor/data/MovieStatistics.csv"

load_sql = f"""
LOAD DATA LOCAL INFILE '{csv_path}'
INTO TABLE MovieStatistics
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(id, title, vote_average, vote_count, movie_status, release_date, revenue, @runtime, adult,
@backdrop_path, @budget, @homepage, @imdb_id, @original_language, @original_title, @overview,
@popularity, @poster_path, @tagline, genres, @production_companies, @production_countries,
@spoken_languages, @keywords);
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
CHARACTER SET latin1
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


csv_path3 = "/workspaces/Movie-Budget-Predictor/data/MembersAndAwards.csv"

load_sql3 = f"""
LOAD DATA LOCAL INFILE '{csv_path3}'
INTO TABLE MembersAndAwards
CHARACTER SET latin1
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(movie_id, member_id, movie_awards);
"""

try:
    cursor.execute(load_sql3)
    db.commit()
    print("CSV imported successfully!\n")
except mysql.connector.Error as err:
    print(f"Error importing CSV: {err}")

csv_path4 = "/workspaces/Movie-Budget-Predictor/data/DirectorsAndActors.csv"

load_sql4 = f"""
LOAD DATA LOCAL INFILE '{csv_path4}'
INTO TABLE DirectorsAndActors
CHARACTER SET latin1
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(member_id, member_name, roll_type, member_awards);
"""

try:
    cursor.execute(load_sql4)
    db.commit()
    print("CSV imported successfully!\n")
except mysql.connector.Error as err:
    print(f"Error importing CSV: {err}")

#Create Users and UserMovies tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS UserMovies (
    user_id INT,
    movie_id INT,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES MovieStatistics(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""")

db.commit()


print("Setup complete! Your Flask app can now connect using flaskuser.\n")