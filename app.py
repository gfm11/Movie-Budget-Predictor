#importing the Flask class from the flask module we have installed 
#and render the html templates we have created.
from flask import Flask , render_template

app = Flask(__name__) #create an object of the Flask class called app to use flask functionality.

@app.route("/") #creating route for the home page of our website
def homepage():
    return render_template('home.html')

@app.route("/basicFunctions")
def basicFunctions():
    return render_template('BasicFuntions.html')
    
if __name__ == "__main__": #if we are running app.py as a script, then start the app
    app.run(host = '0.0.0.0', debug = True) 
    #0.0.0.0 is a development server that allows website to run locally