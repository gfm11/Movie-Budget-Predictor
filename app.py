#importing the Flask class from the flask module we have installed 
#and render the html templates we have created.
from flask import Flask, render_template, request, redirect, make_response, flash
import mysql.connector, hashlib, advancedFunctions

app = Flask(__name__) #create an object of the Flask class called app to use flask functionality.
app.secret_key = 'secret key'

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
            cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
            user_id_result = cursor.fetchone()
            user_id = user_id_result[0] if user_id_result else None
            
            response = make_response(redirect("/"))
            response.set_cookie("username", username)
            response.set_cookie("user_id", str(user_id))
            return response
        except mysql.connector.IntegrityError:
            return render_template("login.html", message="Username already exists. Please choose another.")

    else:
        return "Invalid action."


@app.route("/search")
def search():
    return render_template('Search.html')

@app.route("/search-results", methods=['POST'])
def searchResults():
    title = request.form.get("title") or ""
    genre = request.form.get("genre") or ""
    actor = request.form.get("actor") or ""
    director = request.form.get("director") or ""

    searchQuery = """
       SELECT
            MS.title,
            MS.genres,
            AD.Actors,
            AD.Directors,
            MS.vote_average,
            MS.vote_count,
            MS.movie_status,
            MS.release_date,
            MS.revenue,
            MS.adult,
            B.movie_rank,
            B.worldwide_revenue,
            B.domestic_revenue,
            B.domestic_percentage
        FROM (
            SELECT id, title, genres, vote_average, vote_count, movie_status,
                release_date, revenue, adult
            FROM MovieStatistics
            WHERE title LIKE %s AND genres LIKE %s
            ORDER BY release_date DESC
            LIMIT 20
        ) AS MS
        LEFT JOIN BoxOffice B ON MS.id = B.movie_id
        LEFT JOIN (
            SELECT MA.movie_id,
                GROUP_CONCAT(DISTINCT CASE WHEN D.roll_type = 'ACTOR' THEN D.member_name END SEPARATOR ', ') AS Actors,
                GROUP_CONCAT(DISTINCT CASE WHEN D.roll_type = 'DIRECTOR' THEN D.member_name END SEPARATOR ', ') AS Directors
            FROM MembersAndAwards MA
            JOIN DirectorsAndActors D ON MA.member_id = D.member_id
            GROUP BY MA.movie_id
        ) AS AD ON MS.id = AD.movie_id
        WHERE
            (%s = '' OR AD.Actors LIKE %s)
            AND (%s = '' OR AD.Directors LIKE %s)
        ORDER BY MS.release_date DESC;
    """
    values = (f"%{title}%", f"%{genre}%", actor, f"%{actor}%", director, f"%{director}%")
    cursor.execute(searchQuery, values)
    results = cursor.fetchall()
    return render_template('Search.html', results = results)
    
@app.route("/update", methods=["GET"])
def update():
    user_id = request.cookies.get("user_id")
    cursor.execute("""
        SELECT 
            M.id,
            M.title,
            M.genres,
            GROUP_CONCAT(DISTINCT CASE WHEN D.roll_type = 'ACTOR' THEN D.member_name END SEPARATOR ', ') AS actors,
            GROUP_CONCAT(DISTINCT CASE WHEN D.roll_type = 'DIRECTOR' THEN D.member_name END SEPARATOR ', ') AS directors
        FROM MovieStatistics M
        JOIN UserMovies U ON M.id = U.movie_id
        LEFT JOIN MembersAndAwards MA ON MA.movie_id = M.id
        LEFT JOIN DirectorsAndActors D ON D.member_id = MA.member_id
        WHERE U.user_id = %s
        GROUP BY M.id, M.title, M.genres
    """, (user_id,))
    movies = cursor.fetchall()
    return render_template('Update.html', movies=movies)

@app.route("/insert-movie", methods=['POST']) #route that will submit the form to insert a movie
def insertMovie():
    user_id = request.cookies.get("user_id")
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

    movieInserted = cursor.rowcount > 0

    if actor:
        cursor.execute("INSERT INTO DirectorsAndActors (member_name, roll_type) VALUES (%s, 'ACTOR')", (actor,))
        actor_id = cursor.lastrowid  # get ID of inserted actor
        cursor.execute("INSERT INTO MembersAndAwards (movie_id, member_id, movie_awards) VALUES (%s, %s, 0)", (movieID, actor_id))

    if director:
        cursor.execute("INSERT INTO DirectorsAndActors (member_name, roll_type) VALUES (%s, 'DIRECTOR')", (director,))
        director_id = cursor.lastrowid  # get ID of inserted director
        cursor.execute("INSERT INTO MembersAndAwards (movie_id, member_id, movie_awards) VALUES (%s, %s, 0)", (movieID, director_id))
    
    cursor.execute("INSERT INTO UserMovies (user_id, movie_id) VALUES (%s, %s)", (user_id,movieID))

    db.commit()

    if movieInserted > 0:
        flash("Movie Entered Successfully!", "success")
    else:
        flash("Insert unsuccessful. Check that you're logged in and spelling is correct.", "error")
        
    return redirect("/update") # goes back to update page when done

@app.route("/update-movie", methods=['POST']) # route that will submit the form to update a movie
def updateMovie():
    movie_id = request.form["movie_id"]
    title = request.form.get("title")
    genre = request.form.get("genre")
    actor = request.form.get("actor")
    director = request.form.get("director")

    if title:
        cursor.execute("UPDATE MovieStatistics SET title=%s WHERE id=%s", (title, movie_id))

    if genre:
        cursor.execute("UPDATE MovieStatistics SET genres=%s WHERE id=%s", (genre, movie_id))


    if actor: # update actor if needed
        cursor.execute("""
            UPDATE DirectorsAndActors D
            JOIN MembersAndAwards MA ON D.member_id = MA.id
            SET D.member_name = %s
            WHERE MA.id = %s AND D.roll_type = 'ACTOR'
        """, (actor, movie_id))

    if director: # update director if needed
        cursor.execute("""
            UPDATE DirectorsAndActors D
            JOIN MembersAndAwards MA ON D.member_id = MA.member_id
            JOIN MovieStatistics M ON M.id = MA.id
            SET D.member_name = %s
            WHERE M.id = %s AND D.roll_type = 'DIRECTOR'
        """, (director, movie_id))

    # print message if update is successful or unsuccessful
    if cursor.rowcount > 0:
        flash("Movie Updated Successfully!", "success")
    else:
        flash("Update unsuccessful. Check that you're logged in and spelling is correct.", "error")

    db.commit()
    return redirect("/update") # goes back to update page when done

@app.route("/remove-movie", methods=['POST'])
def removeMovie():
    movie_id = request.form["movie_id"]

    cursor.execute("DELETE FROM MovieStatistics WHERE id=%s", (movie_id,))

    db.commit()

    if cursor.rowcount > 0:
        flash("Movie Removed Successfully!", "success")
    else:
        flash("Removal unsuccessful. Check that you're logged in and spelling is correct.", "error")
    return redirect("/update")

@app.route("/BoxOfficePredictor")
def BoxOfficePredictor():
    return render_template('BoxOfficePredictor.html')

@app.route("/predict-box-office", methods=['POST'])
def PredictBoxOffice():
    title = request.form["title"]
    genre = request.form.get("genre")
    actor = request.form.get("actor")
    director = request.form.get("director")
    release = request.form.get("release")

    # check if the title is valid
    cursor_title = db.cursor(buffered=True)
    validTitleQuery = "SELECT 1 FROM MovieStatistics WHERE title=%s"
    cursor_title.execute(validTitleQuery, (title,))
    titleResult = cursor_title.fetchone()
    cursor_title.close()

    # check if the actor is valid
    cursor_actor = db.cursor(buffered=True)
    validActorQuery = "SELECT 1 FROM DirectorsAndActors WHERE member_name=%s AND roll_type='ACTOR'"
    cursor_actor.execute(validActorQuery, (actor,))
    actorResult = cursor_actor.fetchone()
    cursor_actor.close()

    # check if the director is valid
    cursor_director = db.cursor(buffered=True)
    validDirectorQuery = "SELECT 1 FROM DirectorsAndActors WHERE member_name=%s AND roll_type='DIRECTOR'"
    cursor_director.execute(validDirectorQuery, (director,))
    directorResult = cursor_director.fetchone()
    cursor_director.close()

    # flash error if title is not in the table
    if(titleResult is None and not(title == "")):
        flash("Predictor error. Invalid title name.", "error")
    
    # flash error if actor is not in the table
    if(actorResult is None and not(actor == "")):
        flash("Predictor error. Invalid actor name.", "error")

    # flash error if director is not in the table
    if(directorResult is None and not (director == "")):
        flash("Predictor error. Invalid director name", "error")
    
    print("DB connection:", db.is_connected())
    domestic_prediction = advancedFunctions.calculate_national_box_office(db, genre, actor, director, release)
    print("DOMESTIC: ", domestic_prediction)
    return render_template('BoxOfficePredictor.html', domestic_value = domestic_prediction)

@app.route("/AwardsPredictor")
def AwardsPredictor():
    return render_template('AwardsPredictor.html')

@app.route("/predict-awards", methods=['POST'])
def Predictawards():
    return redirect("/AwardsPredictor")

@app.context_processor
def inject_user():
    username = request.cookies.get("username")
    user_id = request.cookies.get("user_id")
    return dict(username=username, user_id=user_id)


if __name__ == "__main__": #if we are running app.py as a script, then start the app
    app.run(host = '0.0.0.0', debug = True) 
    #0.0.0.0 is a development server that allows website to run locally\
