This application runs using the Peloton API in conjunction with a user-specific Peloton Session ID cookie. You will need to add the Peloton Session ID Cookie to the code directly or to a user-set environment variable (peloton_session_id). 

A local MYSQL server is required and the root password will also need to be loaded via a user-set environment variable (MYSQL_Password) or to the code directly. 

Run the "PelotonCyclingScraper.py" to build the database. A 1 second timer was added between each Class API call to prevent a very high request rate, but that can be removed if desired. You can modify the limit in the 'url' variable to request a larger number of classes to build the database. 

Once the MYSQL database is built and running, you can run the Peloton_Flask_App.py to serve the search page at localhost:5000. 

![](PelotonSearchScreenCap.gif)
