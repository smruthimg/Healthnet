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
	1. Appointment Calendar display is not functioning. Appointments will display correctly, meaning for Patients and Doctors, all of their
		Appointments will be displayed and for Nurses only the Appointments in the current week will be displayed.
	2. Currently, when creating an Appointment, time conflicts for Patient and Doctor schedules are not checked. i.e. two Appointments can
		be made for the same Doctor and/or same Patient at the same time.
	3. When creating a new hospital staff from the hospital admin index, field checking is not implemented. The only required field is
		username when actually all of the fields should be verified.
	4. After changing the password of a Patient, you will be logged out of the system. This is for security's sake, NOT A BUG.
	5. When registering a Patient, if you enter some fields of the registration and select the Back option, you will not be brought back to
		the index page. You will only be brought back if all of the fields are empty.
	6. When creating an appointment if any of the fields are left blank, Django will throw an error. We intend to change it so that we
		throw the error instead of Django.
	7. When creating/updating an appointment, the user can enter any Date/Time they wish, even one in the past.
3. Known missing Release-1 features
	1. Proof of Insurance is not asked for or kept track of when registering Patients.
	2. Medical Information and Hospitals are R2, so they are not kept track of when registering a Patient.
	3. Doctor's do not have locations, as they are Hospitals, which are an R2 feature.
	4. There is no checking for time conflicts on Appointments.
	5. Admins are not able to filter log activities using a timeframe. Most common system or user activities are not shown.
4. Basic execution and usage instructions
	1. When registering, pick a username and password.
	2. When you login, use the same username and password. The form will authenticate the information. If you login as a Patient, Doctor or
		Nurse, you will be taken to the Appointments page. If you log in as an Admin, you will be taken to the Admin Index page.