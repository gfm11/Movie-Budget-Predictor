#importing the Flask class from the flask module we have installed 
#and render the html templates we have created.
from flask import Flask, render_template, request, redirect, make_response
import mysql.connector, hashlib

app = Flask(__name__) #create an object of the Flask class called app to use flask functionality.

db = mysql.connector.connect(
    host="127.0.0.1",
    user="flaskuser",       
    password="flaskpass", 
    database= "moviebudgetpredictor", 
    allow_local_infile = True      
)

cursor = db.cursor()

print("CSV data imported successfully!")
@app.route("/") #creating route for the home page of our website
def homepage():
    username = request.cookies.get("username")
    user_id = request.cookies.get("user_id")

    if username:
        return render_template("homepage.html", username=username, user_id=user_id)
    else:
        return render_template('homepage.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/logout")
def logout():
    response = make_response(redirect("/"))
    response.delete_cookie("username")
    response.delete_cookie("user_id")
    return response

@app.route("/login-status", methods=["POST"])
def loginstatus():
    username = request.form["username"]
    password = request.form["password"]
    action = request.form["action"]

    if action == "Log In":
        login_query = "SELECT hashed_password FROM Users WHERE username = %s"
        cursor.execute(login_query, (username,))
        result = cursor.fetchone()

        if result is None:
            return render_template("login.html", message="Incorrect Username or Password")

        stored_hash = result[0]
        entered_hash = hashlib.sha256(password.encode()).hexdigest()

        if stored_hash == entered_hash:
            cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
            user_id_result = cursor.fetchone()
            user_id = user_id_result[0] if user_id_result else None

            response = make_response(redirect("/"))
            response.set_cookie("username", username)
            response.set_cookie("user_id", str(user_id))
            return response
        else:
            return render_template("login.html", message="Incorrect Username or Password")

    elif action == "Create Account":
        if len(username) < 6:
            return render_template("login.html", message="Your username must be at least 6 characters")
             
        if len(password) < 8:
            return render_template("login.html", message="Your password must be at least 8 characters")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            create_query = "INSERT INTO Users (username, hashed_password) VALUES (%s, %s)"
            cursor.execute(create_query, (username, hashed_password))
            db.commit()
            return redirect("/")
        except mysql.connector.IntegrityError:
            return render_template("login.html", message="Username already exists. Please choose another.")

    else:
        return "Invalid action."


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
    values = (genre, title)
    cursor.execute(updateQuery, values)

    if actor: #update actor if needed
        cursor.execute("""
            UPDATE DirectorsAndActors D
            JOIN MembersAndAwards MA ON D.member_id = MA.member_id
            JOIN MovieStatistics M ON M.id = MA.movie_id
            SET D.member_name = %s
            WHERE M.title = %s AND D.roll_type = 'ACTOR'
        """, (actor, title))

    if director: #update director if needed
        cursor.execute("""
            UPDATE DirectorsAndActors D
            JOIN MembersAndAwards MA ON D.member_id = MA.member_id
            JOIN MovieStatistics M ON M.id = MA.movie_id
            SET D.member_name = %s
            WHERE M.title = %s AND D.roll_type = 'DIRECTOR'
        """, (director, title))

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

@app.route("/BoxOfficePredictor")
def BoxOfficePredictor():
    return render_template('BoxOfficePredictor.html')

@app.route("/AwardsPredictor")
def AwardsPredictor():
    return render_template('AwardsPredictor.html')

@app.context_processor
def inject_user():
    username = request.cookies.get("username")
    user_id = request.cookies.get("user_id")
    return dict(username=username, user_id=user_id)


if __name__ == "__main__": #if we are running app.py as a script, then start the app
    app.run(host = '0.0.0.0', debug = True) 
    #0.0.0.0 is a development server that allows website to run locally