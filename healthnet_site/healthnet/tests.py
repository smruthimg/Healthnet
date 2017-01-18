from django.test import TestCase
from django.contrib.auth.models import User
from .models import *

class UserTestCase(TestCase):
    """
    Class containing all of the User model test cases.
    """
    def test_user_creation(self):
        """
        Tests that Users are created correctly.
        :return: None
        """
        test_user = User.objects.create_user(username="test_user", first_name="test", last_name="user",
                                             email="test@123.com", password="1234")
        test_user.save()

        self.assertEqual(test_user.username, "test_user")
        self.assertEqual(test_user.first_name, "test")
        self.assertEqual(test_user.last_name, "user")
        self.assertEqual(test_user.email, "test@123.com")
        self.assertTrue(test_user.check_password("1234"))

class NurseTestCase(TestCase):
    """
    Class containing all of the Nurse model test cases.
    """
    def test_nurse_creation(self):
        """
        Tests that Nurses are created correctly and
        linked to a User correctly.
        :return: None
        """
        test_hospital = Hospital(name="test", location="test")
        test_hospital.save()

        test_user = User.objects.create_user(username="test_nurse", first_name="test", last_name="nurse",
                                             email="test@123.com", password="1234")
        test_user.save()

        test_nurse_user_id = 1

        test_nurse = Nurse(user_id=test_nurse_user_id, hospital=test_hospital)
        test_nurse.save()

        self.assertEqual(test_user.username, "test_nurse")
        self.assertEqual(test_user.first_name, "test")
        self.assertEqual(test_user.last_name, "nurse")
        self.assertEqual(test_user.email, "test@123.com")
        self.assertTrue(test_user.check_password("1234"))

class DoctorTestCase(TestCase):
    """
    Class containing all of the Doctor model test cases.
    """
    def test_doctor_creation(self):
        """
        Tests that Doctors are created correctly and
        linked to a User correctly.
        :return: None
        """
        test_user = User.objects.create_user(username="test_doctor", first_name="test", last_name="doctor",
                                             email="test@123.com", password="1234")
        test_user.save()

        test_doctor_user_id = 1

        test_hospital = Hospital(name="test", location="test")
        test_hospital.save()

        test_doctor = Doctor(user_id=test_doctor_user_id, hospital=test_hospital)
        test_doctor.save()

        self.assertEqual(test_user.username, "test_doctor")
        self.assertEqual(test_user.first_name, "test")
        self.assertEqual(test_user.last_name, "doctor")
        self.assertEqual(test_user.email, "test@123.com")
        self.assertTrue(test_user.check_password("1234"))

class PatientTestCase(TestCase):
    """
    Class containing all of the Patient model test cases.
    """
    def test_patient_creation(self):
        """
        Tests that Patients are created correctly and
        linked to a User correctly.
        :return: None
        """
        test_user = User.objects.create_user(username="test_patient", first_name="test", last_name="patient",
                                             email="test@123.com", password="1234")
        test_user.save()

        test_patient_user_id = 1

        test_hospital = Hospital(name="test", location="test")
        test_hospital.save()

        test_patient = Patient(user_id=test_patient_user_id, first_name="test", last_name="patient",
                               contact_number=1231231234, emergency_contact_number=1231231234,
                               preferred_hospital=test_hospital, insurance_id=1234, insurance_company="test",
                               address="test", city="test", state="NY", zipcode=12345, country="US", age=1,
                               weight=20, height=20)
        test_patient.save()

        self.assertEqual(test_user.username, "test_patient")
        self.assertEqual(test_user.first_name, "test")
        self.assertEqual(test_user.last_name, "patient")
        self.assertEqual(test_user.email, "test@123.com")
        self.assertTrue(test_user.check_password("1234"))

    def test_update_patient_info(self):
        """
        Tests that Patients can update their information correctly.
        :return: None
        """
        test_user = User.objects.create_user(username="test_patient", first_name="test", last_name="patient",
                                             email="test@123.com", password="1234")
        test_user.save()

        test_patient_user_id = 1

        test_hospital = Hospital(name="test", location="test")
        test_hospital.save()

        test_patient = Patient(user_id=test_patient_user_id, first_name="test", last_name="patient",
                               contact_number=1231231234, emergency_contact_number=1231231234,
                               preferred_hospital=test_hospital, insurance_id=1234, insurance_company="test",
                               address="test", city="test", state="NY", zipcode=12345, age=1,
                               weight=20, height=20)
        test_patient.save()

        test_patient.update_profile_info(new_contact_number=5184223456, new_emergency_contact_number=6781234567, new_address="123 Test Rd", new_city="Test", new_state="NY", new_zipcode=14623, new_email="test@test.com")

        self.assertEqual(test_patient.user_id, test_patient_user_id)
        self.assertEqual(test_patient.first_name, "test")
        self.assertEqual(test_patient.last_name, "patient")
        self.assertEqual(test_patient.contact_number, 5184223456)
        self.assertEqual(test_patient.emergency_contact_number, 6781234567)

class UserProfileTestCase(TestCase):
    """
    Class containing all of the UserProfile model test cases.
    """
    def test_user_profile_creation(self):
        """
        Tests that UserProfiles are created correctly.
        :return: None
        """
        test_user = User.objects.create_user(username="test_patient", first_name="test", last_name="patient",
                                             email="test@123.com", password="1234")
        test_user.save()

        test_user_profile = UserProfile(user=test_user, user_type="admin")

        self.assertEqual(test_user_profile.user, test_user)
        self.assertEqual(test_user_profile.user_type, "admin")

class AppointmentTestCase(TestCase):
    """
    Class containing all of the Appointment model test cases.
    """
    def test_appointment_creation(self):
        """
        Tests that Appointments are created correctly.
        :return: None
        """
        test_user1 = User.objects.create_user(username="test_patient", first_name="test", last_name="patient",
                                              email="test@123.com", password="1234")
        test_user1.save()

        test_user2 = User.objects.create_user(username="test_doctor", first_name="test", last_name="doctor",
                                              email="test@123.com", password="1234")
        test_user2.save()

        test_patient_user_id = 1

        test_hospital = Hospital(name="test", location="test")
        test_hospital.save()

        test_patient = Patient(user_id=test_patient_user_id, first_name="test", last_name="patient",
                               contact_number=1231231234, emergency_contact_number=1231231234,
                               preferred_hospital=test_hospital, insurance_id=1234, insurance_company="test",
                               address="test", city="test", state="NY", zipcode=12345, country="US", age=1,
                               weight=20, height=20)
        test_patient.save()

        test_doctor_user_id = 2

        test_doctor = Doctor(user_id=test_doctor_user_id, hospital=test_hospital)
        test_doctor.save()

        test_appointment = Appointment(doctor_id=1, patient_id=1, start=datetime.datetime.day,
                                       end=datetime.datetime.day, location=test_hospital)

        self.assertEqual(test_appointment.doctor_id, 1)
        self.assertEqual(test_appointment.patient_id, 1)
        self.assertEqual(test_appointment.start, datetime.datetime.day)

    def test_appointment_update(self):
        """
        Tests that Appointments update correctly.
        :return: None
        """
        test_user1 = User.objects.create_user(username="test_patient", first_name="test", last_name="patient",
                                              email="test@123.com", password="1234")
        test_user1.save()

        test_user2 = User.objects.create_user(username="test_doctor", first_name="test", last_name="doctor",
                                              email="test@123.com", password="1234")
        test_user2.save()

        test_patient_user_id = 1

        test_hospital = Hospital(name="test", location="test")
        test_hospital.save()

        test_patient = Patient(user_id=test_patient_user_id, first_name="test", last_name="patient",
                               contact_number=1231231234, emergency_contact_number=1231231234,
                               preferred_hospital=test_hospital, insurance_id=1234, insurance_company="test",
                               address="test", city="test", state="NY", zipcode=12345, country="US", age=1,
                               weight=20, height=20)
        test_patient.save()

        test_doctor_user_id = 2

        test_doctor = Doctor(user_id=test_doctor_user_id, hospital=test_hospital)
        test_doctor.save()

        test_appointment = Appointment(doctor_id=1, patient_id=1, start=datetime.datetime.day,
                                       end=datetime.datetime.day, location=test_hospital)

        new_date = datetime.datetime.now()

        test_appointment.update_appointment(new_doctor_id=2, new_patient_id=2, new_start=new_date, new_end=new_date + datetime.timedelta(hours=1))

        self.assertEqual(test_appointment.doctor_id, 2)
        self.assertEqual(test_appointment.patient_id, 2)

class LogItemTestCase(TestCase):
    """
    Class containing all of the tests for the LogItem class.
    """
    def test_log_item_creation(self):
        """
        Tests that LogItems are created correctly.
        :return: None
        """
        test_log_item = LogItem(username1="user1", username2="user2", timestamp=datetime.datetime.now(), activity="test")

        self.assertEqual(test_log_item.username1, "user1")
        self.assertEqual(test_log_item.username2, "user2")
        self.assertEqual(test_log_item.activity, "test")
