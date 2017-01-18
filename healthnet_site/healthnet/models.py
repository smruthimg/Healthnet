from django.db import models
from django.contrib.auth.models import User
import datetime
#from django_countries.fields import CountryField


class LogItem(models.Model):
    """
    Represents a single activity log item
    """
    # Username of the first user involved in the activity
    username1 = models.CharField(default='', max_length=20)

    #Type of user of username1
    user_type1 = models.CharField(default='', max_length=20)

    # Username of the second user involved in the activity
    username2 = models.CharField(default='', max_length=20)

    #Type of user of username2
    user_type2 = models.CharField(default='', max_length=20)

    # Date and time performed
    timestamp = models.DateTimeField()

    # The type of activity
    activity = models.CharField(max_length=30)

    # The hospital the first user that triggered the event is at
    hospital1 = models.CharField(max_length=30)

    # The hospital that second user that triggered the event is at
    hospital2 = models.CharField(max_length=30)


class Hospital(models.Model):
    """
    Represents a single hospital.
    Patients can be admitted and discharged to and from a hospital.
    Doctors, Nurses and Administrators are assigned to a hospital.

    name: The name of the hospital
    location: Physical location (city)
    """
    name = models.CharField(max_length=30, default='')
    location = models.CharField(max_length=30, default='')

    def __str__(self):
        return self.name


class Nurse(models.Model):
    """
    Represents a Nurse. Inherits from the User class.
    Nurses have a user_id associated with them. This is the id
    of the User instance that is connected to the Nurse instance.
    Nurses are assigned to a hospital.
    
    user_id: ID of connected user in the database
    hospital: the hospital for which the nurse works
    """
    user_id = models.IntegerField()
    hospital = models.ForeignKey(Hospital)

class Doctor(models.Model):
    """
    Represents a Doctor. Inherits from the User class.
    In R2, Doctors will have a hospital_id attribute of type
    IntegerField.
    Also in R2, Doctors will have a location attribute of type
    CharField.

    user_id: id of the user connected to the doctor object
    hospital: the hospital for which the doctor works
    """
    user_id = models.IntegerField()
    hospital = models.ForeignKey(Hospital)

    def __str__(self):
        user = User.objects.get(id=self.user_id)
        return user.username


class Patient(models.Model):
    """
    Represents a Patient. Inherits from the User class.
    Patients have a user_id associated with them. This is the id
    of the User instance that is connected to the Patient instance.
    Patients have a first name and last name of type CharField.
    They have a contact number and an emergency contact number
    both of type IntegerField.
    """

    state_choices = (
         ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'),
         ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'),
         ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'),
         ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
         ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'),
         ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
         ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
         ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
         ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'),
         ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')
    )

    user_id = models.IntegerField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    contact_number = models.IntegerField()
    emergency_contact_number = models.IntegerField()
    preferred_hospital = models.ForeignKey(Hospital, related_name='preferred_hospital', default=None)
    current_hospital = models.ForeignKey(Hospital, related_name='current_hospital', blank=True, null=True)
    insurance_id = models.IntegerField()
    insurance_company = models.CharField(max_length=30)
    address = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30, choices=state_choices)
    zipcode = models.IntegerField()
    country = models.CharField(default='United States', max_length=20)
    age = models.IntegerField()
    weight = models.IntegerField()
    height = models.IntegerField()

    def update_patient_medical_info(self, insurance_company, insurance_id, age, weight, height, preferred_hospital):
        """
        Allows Nurses and Doctors to change Patient's medical information.
        Medical info includes:

        :param: insurance_company - patient's insurance provider
        :param: insurance_id - patient's insurance ID number
        :param: age - patient's age (in years)
        :param: weight - patient's weight (in pounds)
        :param: height - patient's height (in inches)
        :param: preferred_hospital - patient's choice of preferred hospital
        """
        self.insurance_company = insurance_company
        self.insurance_id = insurance_id
        self.age = age
        self.weight = weight
        self.height = height
        self.preferred_hospital = preferred_hospital
        self.save()

    def admit_patient(self, hospital):
        """
        Admits this patient to hospital
        :param hospital - the hospital to admit to
        :return: None
        """
        self.current_hospital = hospital
        self.save()

    def discharge_patient(self):
        """
        Discharges this patient from their
        current hospital
        :return: None
        """
        self.current_hospital = None
        self.save()

    def update_profile_info(self, new_email, new_contact_number, new_emergency_contact_number, new_address, new_city, new_zipcode, new_state):
        """
        Updates the profile information for this patient.
        :param: new_contact_number - the new contact number of the patient
        :param: new_emergency_contact_number - the new emergency contact number
                of the patient
        :return: None
        """
        user = User.objects.get(pk=self.user_id)
        user.email = new_email
        user.save()
        self.contact_number = new_contact_number
        self.emergency_contact_number = new_emergency_contact_number
        self.address = new_address
        self.city = new_city
        self.zipcode = new_zipcode
        self.state = new_state
        self.save()

    def transfer_patient(self, new_hospital):
        """
        Tranfers the patient by changing their current hospital
        to new_hospital.
        :param: new_hospital - the new hospital the patient will be in
        :return: None
        """
        self.current_hospital = new_hospital
        self.save()

    def __str__(self):
        user = User.objects.get(id=self.user_id)
        return user.username


class Administrator(models.Model):
    """
    An administrator user.
    Has permission to view system logs and status.
    Administrators have a user_id associated with them. This is the id
    of the User instance that is connected to the Administrator instance.
    """
    hospital = models.ForeignKey(Hospital)
    user_id = models.IntegerField()

    def __str__(self):
        return User.objects.get(id=self.user_id).username


class UserProfile(models.Model):
    '''Model for User Profile
    Author:Smruthi
    date: 30 Sep 2016'''

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.user.username


class Appointment(models.Model):
    """
    Representation of a single appointment.

    location: hospital where appointment takes place
    doctor_id: the ID of the doctor involved in appointment
    patient_id: the ID of the doctor involved in appointment
    start: start date and time of appointment
    end: end date and time of appointment
    """
    location = models.ForeignKey(Hospital)
    doctor_id = models.IntegerField()
    patient_id = models.IntegerField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    def update_appointment(self, new_doctor_id, new_patient_id, new_start, new_end):
        """
        Updates an existing appointment.
        :params: new_doctor_id: the id of the new Doctor that the Appointment is with
                 new_patient_id: the id of the new Patient that the Appointment is for
                 new_appointment_date: the new date and time the Appointment is at
        """
        self.doctor_id = new_doctor_id
        self.patient_id = new_patient_id
        self.start = new_start
        self.end = new_end
        self.save()

    def delete_appointment(self):
        """
        Deletes an existing appointment.
        :return: None
        """
        self.delete()


class Prescription(models.Model):
    """
    Represents a single prescription given to a patient by a doctor.

    patient: reference to patient the prescription is given to
    doctor: reference to doctor that made the prescription
    medication: type of medication prescribed
    dosage: amount of medication prescribed
    """
    patient = models.ForeignKey(Patient, related_name='patient')
    doctor = models.ForeignKey(Doctor, related_name='doctor')
    medication = models.TextField()
    dosage = models.CharField(max_length=100)
    date_prescribed = models.DateTimeField()
    hospital = models.ForeignKey(Hospital, related_name='hospital')

    def __str__(self):
        return self.medication + ' - ' + self.dosage


class TestResult(models.Model):
    """
    Represents the results of a single test carried out by a hospital.

    patient: reference to patient on which test was done
    comments: doctor's comments about the test results. visible to patient once
              the test is released.
    released: determines whether the results have been released to the patient
    name: a name for the test result
    results: doctor's description of the results of the test
    """

    patient = models.ForeignKey(Patient)
    comments = models.TextField()
    released = models.BooleanField()
    name = models.CharField(max_length=30)
    results = models.TextField()
    testfile=models.FileField(upload_to='documents/')

    def update_test_results(self,patient,comments,released,name,results,testfile):
        self.comments=comments
        self.name=name
        self.patient=patient
        self.released=released
        self.results=results
        self.testfile=testfile

    def release(self):
        """
        Releases the test result to be viewed by the patient
        """
        self.released = True
        self.save()


class Logger(models.Model):
    """
    Defines functions needed for system/database operations
    """
    @staticmethod
    def log_system_activity(activity, username1='', username2='', user_type1='', user_type2='', hospital1='', hospital2=''):
        """
        Logs a system activity.
        This occurs whenever a user triggers an action in the system.
        """
        new_item = LogItem(username1=username1, timestamp=datetime.datetime.now(), activity=activity, username2=username2, user_type1=user_type1, user_type2=user_type2, hospital1=hospital1, hospital2=hospital2)
        new_item.save()
