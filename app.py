#importing the Flask class from the flask module we have installed 
#and render the html templates we have created.
from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__) #create an object of the Flask class called app to use flask functionality.

db = mysql.connector.connect(
    host="127.0.0.1",
    user="flaskuser",       
    password="password123", 
    database= "moviebudgetpredictor", 
    allow_local_infile = True      
)

cursor = db.cursor()

print("CSV data imported successfully!")
@app.route("/") #creating route for the home page of our website
def homepage():
    return render_template('homepage.html')

@app.route("/search")
def search():
    return render_template('Search.html')

@app.route("/search-results", methods=['POST'])
def searchResults():
    title = request.form["title"]
    genre = request.form["genre"]
    actor = request.form.get("actor") or ""
    director = request.form.get("director") or ""

    searchQuery = """SELECT M.title, M.genres,
                    GROUP_CONCAT(CASE WHEN D.roll_type = 'ACTOR' THEN D.member_name END SEPARATOR ', ') AS actors,
                    GROUP_CONCAT(CASE WHEN D.roll_type = 'DIRECTOR' THEN D.member_name END SEPARATOR ', ') AS directors
                    FROM MovieStatistics M
                    LEFT JOIN MembersAndAwards MA ON M.id = MA.movie_id
                    LEFT JOIN DirectorsAndActors D ON MA.member_id = D.member_id
                    WHERE M.title LIKE %s AND M.genres LIKE %s AND (D.member_name LIKE %s OR %s = '') AND (D.member_name LIKE %s OR %s = '')
                    GROUP BY M.id, M.title, M.genres;"""
    values = (f"%{title}%", f"%{genre}%", f"%{actor}%", actor, f"%{director}%", director )
    cursor.execute(searchQuery, values)
    results = cursor.fetchall()
    return render_template('Search.html', results = results)
    
@app.route("/update")
def update():
    return render_template('Update.html')

@app.route("/insert-movie", methods=['POST']) #route that will submit the form to insert a movie
def insertMovie():
    title = request.form["title"]
    genre = request.form["genre"]
    actor = request.form.get("actor")
    director = request.form.get("director")

    cursor.execute("SELECT MAX(id) FROM MovieStatistics")
    max_id = cursor.fetchone()[0] or 0 
    movieID = max_id + 1

    insertQuery = "INSERT INTO MovieStatistics (id, title, vote_average, vote_count, movie_status, release_date, revenue, adult, genres) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (movieID, title, None, None, "Released", None, None, None, genre)
    cursor.execute(insertQuery, values)

    if actor:
        cursor.execute("INSERT INTO DirectorsAndActors (member_name, roll_type) VALUES (%s, 'ACTOR')", (actor,))
        actor_id = cursor.lastrowid  # get ID of inserted actor
        cursor.execute("INSERT INTO MembersAndAwards (movie_id, member_id, movie_awards) VALUES (%s, %s, 0)", (movieID, actor_id))

    if director:
        cursor.execute("INSERT INTO DirectorsAndActors (member_name, roll_type) VALUES (%s, 'DIRECTOR')", (director,))
        director_id = cursor.lastrowid  # get ID of inserted director
        cursor.execute("INSERT INTO MembersAndAwards (movie_id, member_id, movie_awards) VALUES (%s, %s, 0)", (movieID, director_id))

    db.commit()
    return redirect("/update") #goes back to update page when done

@app.route("/update-movie", methods=['POST']) #route that will submit the form to update a movie
def updateMovie():
    title = request.form["title"]
    genre = request.form["genre"]
    actor = request.form.get("actor")
    director = request.form.get("director")

    updateQuery = "UPDATE MovieStatistics SET genres=%s WHERE title=%s"
    values = (genre, actor, director, title)
    cursor.execute(updateQuery, values)
    db.commit()
    return redirect("/update")

@app.route("/remove-movie", methods=['POST'])
def removeMovie():
    title = request.form["title"]
    genre = request.form["genre"]

    removeQuery = "DELETE FROM MovieStatistics WHERE title=%s AND genres=%s"
                                                    
    values = (title, genre)
    cursor.execute(removeQuery, values)
    db.commit()
    return redirect("/update")

if __name__ == "__main__": #if we are running app.py as a script, then start the app
    app.run(host = '0.0.0.0', debug = True) 
    #0.0.0.0 is a development server that allows website to run locally