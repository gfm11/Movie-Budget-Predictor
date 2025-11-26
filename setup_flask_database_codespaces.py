import mysql.connector
import subprocess
import os
import time
import pandas as pd

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
print("flaskuser verified and ready.")

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

try:
    # Disable foreign key checks temporarily
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    db.commit()
    print("Foreign key checks disabled")
    
    # Drop and recreate the table without the PRIMARY KEY constraint
    cursor.execute("DROP TABLE IF EXISTS BoxOffice")
    cursor.execute("""
    CREATE TABLE BoxOffice (
        movie_id INT NULL,
        title VARCHAR(120) NOT NULL,
        movie_rank INT,
        worldwide_revenue FLOAT,
        domestic_revenue FLOAT,
        domestic_percentage FLOAT,
        INDEX idx_title (title)
    )
    """)
    db.commit()
    print("BoxOffice table recreated without primary key")
    
    # Read CSV with latin1 encoding
    df = pd.read_csv(csv_path2, encoding='latin1')
    print(f"Read {len(df)} rows from CSV")
    
    # Create a dictionary of MovieStatistics titles -> IDs for faster lookup
    print("Loading MovieStatistics titles...")
    cursor.execute("SELECT id, LOWER(TRIM(title)) FROM MovieStatistics")
    title_to_id = {title: movie_id for movie_id, title in cursor.fetchall()}
    print(f"Loaded {len(title_to_id)} movie titles")
    
    # Clean up the data and match titles in Python
    df['movie_id'] = df['movie_id'].replace('', None)
    df['movie_id'] = pd.to_numeric(df['movie_id'], errors='coerce')
    
    # Match titles in Python (much faster!)
    matched = 0
    for index, row in df.iterrows():
        if pd.isna(row['movie_id']):
            clean_title = str(row['title']).lower().strip()
            if clean_title in title_to_id:
                df.at[index, 'movie_id'] = title_to_id[clean_title]
                matched += 1
    
    print(f"Matched {matched} titles to movie IDs")
    
    # Insert into database
    inserted = 0
    for index, row in df.iterrows():
        insert_sql = """
        INSERT INTO BoxOffice (movie_id, movie_rank, title, worldwide_revenue, domestic_revenue, domestic_percentage)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            None if pd.isna(row['movie_id']) else int(row['movie_id']),
            int(row['movie_rank']) if not pd.isna(row['movie_rank']) else None,
            str(row['title']),
            float(row['worldwide_revenue']) if not pd.isna(row['worldwide_revenue']) else None,
            float(row['domestic_revenue']) if not pd.isna(row['domestic_revenue']) else None,
            float(row['domestic_percentage']) if not pd.isna(row['domestic_percentage']) else None
        )
        cursor.execute(insert_sql, values)
        inserted += 1
        
        if inserted % 500 == 0:
            print(f"Inserted {inserted} rows...")
    
    db.commit()
    print(f"Inserted {inserted} rows successfully!")

    # Delete rows that couldn't be matched (NULL movie_id)
    cursor.execute("DELETE FROM BoxOffice WHERE movie_id IS NULL")
    unmatched = cursor.rowcount
    db.commit()
    print(f"Deleted {unmatched} unmatched rows")

    # Remove duplicates - keep the one with highest domestic_revenue
    cursor.execute("""
        DELETE b1 FROM BoxOffice b1
        INNER JOIN BoxOffice b2 
        WHERE b1.movie_id = b2.movie_id 
        AND (b1.domestic_revenue < b2.domestic_revenue 
             OR (b1.domestic_revenue = b2.domestic_revenue AND b1.movie_rank > b2.movie_rank))
    """)
    duplicates = cursor.rowcount
    db.commit()
    print(f"Deleted {duplicates} duplicate rows")

    # Add primary key and foreign key back
    cursor.execute("ALTER TABLE BoxOffice ADD PRIMARY KEY (movie_id)")
    cursor.execute("""
    ALTER TABLE BoxOffice 
    ADD FOREIGN KEY (movie_id) 
    REFERENCES MovieStatistics(id) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
    """)
    db.commit()
    print("Primary key and foreign key restored")
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    db.commit()
    print("Foreign key checks re-enabled")
    
    # Check results
    cursor.execute("SELECT COUNT(*) FROM BoxOffice WHERE movie_id IS NOT NULL")
    count = cursor.fetchone()[0]
    print(f"Total rows with valid movie_id: {count}")
    
    # Show sample of 2019 matched data
    cursor.execute("""
    SELECT B.title, B.domestic_revenue, M.release_date
    FROM BoxOffice B
    JOIN MovieStatistics M ON B.movie_id = M.id
    WHERE YEAR(M.release_date) = 2019
    AND MONTH(M.release_date) BETWEEN 4 AND 6
    LIMIT 10
    """)
    results = cursor.fetchall()
    print(f"\nSample April-June 2019 movies matched:")
    for row in results:
        print(f"  {row[0]} - ${row[1]:,.0f} - {row[2]}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        db.commit()
    except:
        pass

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
