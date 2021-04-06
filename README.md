This application runs using the Peloton API in conjunction with a user-specific Peloton Session ID cookie. You will need to add the Peloton Session ID Cookie to the code directly or to a user-set environment variable (peloton_session_id). 

A local MYSQL server is required and the root password will also need to be loaded via a user-set environment variable (MYSQL_Password) or to the code directly. 

Run the "PelotonCyclingScraper" to build the database. A 1 second timer was added between each Class API call to prevent a very high request rate, but that can be removed if desired. You can modify the 'url' (https://api.onepeloton.com/api/v2/ride/archived?browse_category=cycling&limit=<mark>400</mark>&content_format=audio%2Cvideo&page=0&sort_by=original_air_time&desc=true) to request a larger number of classes to build the database. 

Once the MYSQL database is built and running, you can run the Flask_App to serve the search page at localhost:5000. 

![](PelotonSearchScreenCap.gif)
