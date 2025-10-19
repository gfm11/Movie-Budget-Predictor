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
    actor = request.form.get("actor")
    director = request.form.get("director")

    searchQuery = "SELECT title FROM MovieStatistics WHERE title LIKE '%s%' AND genre LIKE '%s%' AND actor LIKE '%s% AND director LIKE '%s%"
    values = (title, genre, actor, director)
    cursor.execute(searchQuery, values)
    results = cursor.fetchall()
    return render_template('Search.html', results = results)
@app.route("/update")
def update():
    return render_template('Update.html')

@app.route("/insert-movie", methods=["POST"]) #route that will submit the form to insert a movie
def insertMovie():
    title = request.form["title"]
    genre = request.form["genre"]
    actor = request.form.get("actor")
    director = request.form.get("director")

    cursor.execute("SELECT COUNT(*) FROM MovieStatistics")
    movieID = cursor.fetchone()[0] + 1 #the id for the new movie will be the count of movie entries plus one 

    insertQuery = "INSERT INTO MovieStatistics (id, title, vote_average, vote_count, movie_status, release_date, revenue, adult, genres) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (movieID, title, "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", genre)
    cursor.execute(insertQuery, values)
    db.commit()
    return redirect("/update") #goes back to update page when done

@app.route("/update-movie", methods=['POST']) #route that will submit the form to update a movie
def updateMovie():
    title = request.form["title"]
    genre = request.form["genre"]
    actor = request.form.get("actor")
    director = request.form.get("director")

    updateQuery = "UPDATE MovieStatistics SET genre=%s, actor=%s, director=%s WHERE title=%s"
    values = (genre, actor, director, title)
    cursor.execute(updateQuery, values)
    db.commit()
    return redirect("/update")

@app.route("/remove-movie", methods=['POST'])
def removeMovie():
    title = request.form["title"]
    genre = request.form["genre"]
    actor = request.form.get("actor")
    director = request.form.get("director")

    removeQuery = "DELETE FROM MovieStatistics WHERE title=%s AND genre=%s AND actor=%s AND director=%s"
    values = (title, genre, actor, director)
    cursor.execute(removeQuery, values)
    db.commit()
    return redirect("/update")

if __name__ == "__main__": #if we are running app.py as a script, then start the app
    app.run(host = '0.0.0.0', debug = True) 
    #0.0.0.0 is a development server that allows website to run locally