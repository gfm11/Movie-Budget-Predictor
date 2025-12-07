# Movie-Budget-Predictor
This project is for our Database Managment course.

Our project will be a website that can search movies and predict box office revenue and chance at rewards.

# Package Installations
Flask must be installed to use this application. To install, run pip install flask in your terminal.

You also need pandas to run the program. To install, run pip install flask pandas

# MySQL Connector
To properly run the database in the app, you need a local version of our database, and mySQL connector.  
To install mySQL connector and start your mySQL server, run these commands in your terminal:

pip install mysql-connector-python
sudo apt update  
sudo apt install mysql-server -y  
sudo service mysql start && sudo mysql --local-infile=1 -u root

Then, to create a working copy of the actual data in our database, run the command:  

python setup_flask_database_codespaces.py

if you get the error:
Error importing CSV: 3948 (42000): Loading local data is disabled; this must be enabled on both the client and server sides

run these commands in your mysql prompt inside the terminal:
sudo mysql
SET GLOBAL local_infile = 1;
SHOW VARIABLES LIKE 'local_infile'; 

make sure the output of these commands looks like this:  
+---------------+-------+  
| Variable_name | Value |  
+---------------+-------+  
| local_infile  | ON    |  
+---------------+-------+  

if local_infile's value is ON, you are good to go, and can run

python setup_flask_database_codespaces.py

again to import the data.

To run the website, run this command in your terminal:

python app.py

and follow the forwarded port!

If, while using the website, you encounter an error that says a stored procedure cannot be found, you will have to manually
input it into mySQL using your terminal. To do so, enter these commands in your terminal:  

sudo mysql  
use moviebudgetpredictor;  

then, copy the stored procedures from database_schema.sql and paste them on the next line. Make sure to paste them as they are,
not as a single line. Once you have done that, hit enter, and the stored procedures should be there!  

# Analytics  
To view where we got the percentages for our calculations, you can visit these links.  
Domestic ticket prices: https://www.the-numbers.com/market/  
UK and Ireland ticket prices: https://filmdistributorsassociation.com/the-industry/databank/uk-and-ireland-market-trends/average-ticket-price/  
