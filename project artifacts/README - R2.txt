1. Installation of HealthNet
	1. Target Environment
		a. Python 3.4.3
		b. SQLite Version 3.8.0.2
		c. Django 1.9.1
	2. Download the zip file and extract it to the desired location.
	3. Open a command prompt or terminal window.
	4. Change directory until you are in .../healthnet_site/
	5. From here, enter the following command to run the server:
		python manage.py runserver
	6. This will execute the server.
	7. Open a web browser and navigate to http://127.0.0.1:8000/healthnet/
	8. Welcome to HealthNet!
2. Known bugs and disclaimers
	1. To run unit tests on our code, use ‘python manage.py test healthnet.’ Testing 	the entire site will result in errors due to faulty unit tests in the django 		postman package.

3. Known missing Release-2 features
	
4. Basic execution and usage instructions
	1. When registering, pick a username and password.
	2. When you login, use the same username and password. The form will authenticate the information. If you login as a Patient, Doctor or
		Nurse, you will be taken to the Appointments page. If you log in as an Admin, you will be taken to the Admin Index page.
	3. To Login as an admin, use the following credentials:
		Username: Test_Admin
		Password: unchained
	4. To Login as a doctor, use the following credentials:
		Username: Test_Doctor
		Password: unchained
	5. To Login as a nurse, use the following credentials:
		Username: Test_Nurse
		Password: unchained
	6. To Login as a patient, use the following credentials:
		Username: Test_Patient
		Password: unchained