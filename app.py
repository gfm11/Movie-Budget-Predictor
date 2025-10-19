#importing the Flask class from the flask module we have installed 
#and render the html templates we have created.
from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__) #create an object of the Flask class called app to use flask functionality.

db = mysql.connector.connect(
    host="localhost",
    user="flaskuser",       
    password="password123", 
    database= "moviebudgetpredictor"       
)

cursor = db.cursor()

@app.route("/") #creating route for the home page of our website
def homepage():
    return render_template('homepage.html')

@app.route("/search")
def search():
    return render_template('Search.html')

@app.route("/update")
def update():
    return render_template('Update.html')

if __name__ == "__main__": #if we are running app.py as a script, then start the app
    app.run(host = '0.0.0.0', debug = True) 
    #0.0.0.0 is a development server that allows website to run locally