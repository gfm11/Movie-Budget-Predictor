# Movie-Budget-Predictor
This project is for our Database Managment course.

Our project will be a website that can search movies and predict box office revenue and chance at rewards.

# Flask Installation
Flask must be installed to use this application. To install, run pip install flask in your terminal.

If you want to see the website as you are creating it, run python app.py in your terminal, then press ctrl + shift + p and type Simple Browser: Show

# MySQL Connector
To properly run the database in the app, you need a local version of our database, and mySQL connector.  
To install mySQL connector, run these commands in your terminal:

sudo apt update  
sudo apt install mysql-server -y  
sudo service mysql start  

After those three commands have been run, you need to create a local copy of the database.
Run sudo mysql < database_schema.sql to create a copy of our database.  
Then, run these commands in order, and make sure to copy and paste or type them word for word, because the program will not run if the hostname or password is different.  
Here are the commands:  
CREATE USER 'flaskuser'@'localhost' IDENTIFIED BY 'password123';  
GRANT ALL PRIVILEGES ON moviebudgetpredictor.* TO 'flaskuser'@'localhost';  
FLUSH PRIVILEGES;  
EXIT;  