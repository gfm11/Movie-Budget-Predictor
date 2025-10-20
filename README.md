# Movie-Budget-Predictor
This project is for our Database Managment course.

Our project will be a website that can search movies and predict box office revenue and chance at rewards.

# Package Installations
Flask must be installed to use this application. To install, run pip install flask in your terminal.

You also need pandas to run the program. To install, run pip install flask pandas

If you want to see the website as you are creating it, run python app.py in your terminal, then press ctrl + shift + p and type Simple Browser: Show

# MySQL Connector
To properly run the database in the app, you need a local version of our database, and mySQL connector.  
To install mySQL connector, run these commands in your terminal:

pip install my-sql-connector-python
sudo apt update  
sudo apt install mysql-server -y  
sudo service mysql start  

After those three commands have been run, you need to create a local copy of the database.
Run sudo mysql < database_schema.sql to create a copy of our database.  

Then, to create a working copy of the actual data in our database, run the command:  

python setup_flask_database_codespaces.py