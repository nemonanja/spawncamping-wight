***MODULES***

//db_api/:
- database.py contains api for accessing the SQLite database project.db
- resources.py implements the RESTful API and contains the resources neccessary for the application
- rest_api_test.py contains the tests for the resources.py

//db_test/:
- database_api_tests_common.py is a set up file
- database_api_tests_task.py is a test module for testing task cases in database.py
- database_api_tests_user.py is a test module for testin user cases in database.py

//project_admin/:
-application.py is an set up file

//project_admin/static/:
-contains files required for Bootstrap
-project_client.js contains the code for the web client
-UI.html contais the UI that is used by project_client.js

***DELIVERABLE 2 (DB API)***

To init the database, go to the root directory (project) in console and type:

python
db_path = 'db/project.db'
import db_api.database
db = db_api.database.ProjectDatabase(db_path)

To run the tests:

- Go to the root directory in console (project) and type:

python -m db_test.database_api_tests_user
python -m db_test.database_api_tests_task


***DELIVERABLE 3 (REST API)***

To run application go to the root directory (project) in console and type:

python -m db_api.resources

***DELIVERABLE 4***

To run the test for the RESTful API go to the //project_work/db_api/ and in console run the rest_api_test.py. 


***FINAL DELIVERABLE***

To run the application go to the root directory (project_work) in console and type: python project.py
This will start both the Flask app and the client. Then go to the http://localhost:5000/project_admin/UI.html and you can start using the application. 

