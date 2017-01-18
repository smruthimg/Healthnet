from django.db.models import Q
from healthnet.models import *

def determine_action(action_name):
    """
    Helper function for logging
    Takes in an action_name and determines the corresponding
    action string

    Author: Nick Deyette
    """
    action_name = action_name.lower()

    if action_name == "logging in":
        return "has logged in"
    if action_name == "logging out":
        return "has logged out"
    if action_name == "create appointment":
        return "has created an appointment"
    if action_name == "update appointment":
        return "has updated an appointment"
    if action_name == "delete appointment":
        return "has deleted an appointment"
    if action_name == "create user":
        return "has created a new user"
    if action_name == "update profile info":
        return "has updated their profile information"
    if action_name == "register":
        return "has registered"
    if action_name == "change password":
        return "has changed their password"
    if action_name == "exporting information":
        return "has exported their profile information"
    if action_name == "creating prescription":
        return "has created a prescription for"
    if action_name == "removing prescription":
        return "has removed a prescription for"
    if action_name == "admitting patient":
        return "has admitted the following patient to"
    if action_name == "discharging patient":
        return "has discharged the following patient from"
    if action_name == "updating medical info":
        return "has updated the following patient's medical info"
    if action_name == "transferring patient":
        return "has transferred the following patient to"

def determine_total_number_of_activities(start_date, end_date, hospital):
    """
    Determines the total number of activities from start_date to end_date
    at hospital

    Author: Nick Deyette
    """
    total_number_of_activities = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(hospital1=hospital) | Q(hospital2=hospital)).count()

    return total_number_of_activities

def determine_most_common_activity(start_date, end_date, hospital):
    """
    Determines the most common activity from start_date to end_date
    at hospital

    Author: Nick Deyette
    """
    common_activity_dict = {}
    common_activity_list = []

    number_of_appointment_creations = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has created an appointment") & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_appointment_creations] = "appointment creations"
    common_activity_list.append(number_of_appointment_creations)
    number_of_appointment_updates = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has updated an appointment") & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_appointment_updates] = "appointment updates"
    common_activity_list.append(number_of_appointment_updates)
    number_of_appointment_deletes = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has deleted an appointment") & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_appointment_deletes] = "appointment deletions"
    common_activity_list.append(number_of_appointment_deletes)
    number_of_user_creations = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has created a new user") & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_user_creations] = "user creations"
    common_activity_list.append(number_of_user_creations)
    number_of_admits = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has admitted the following patient to") & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_admits] = "admits"
    common_activity_list.append(number_of_admits)
    number_of_discharges = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has discharged the following patient from") & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_discharges] = "discharges"
    common_activity_list.append(number_of_discharges)

    common_activity_list.sort(reverse=True)

    most_common_activity = common_activity_dict[common_activity_list[0]]

    number_of_most_common_activity = common_activity_list[0]

    total_number_of_activities = determine_total_number_of_activities(start_date, end_date, hospital)

    if total_number_of_activities == 0:
        return [most_common_activity, number_of_most_common_activity, 0]

    percent_of_most_common_activity = round((number_of_most_common_activity / total_number_of_activities) * 100)

    return [most_common_activity, number_of_most_common_activity, percent_of_most_common_activity]

def determine_most_common_user_activity(start_date, end_date, user_type, hospital):
    """
    Determines the most common activity from start_date to end_date for
    user_type at hospital

    Author: Nick Deyette
    """
    common_activity_dict = {}
    common_activity_list = []

    number_of_appointment_creations = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has created an appointment") & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_appointment_creations] = "appointment creations"
    common_activity_list.append(number_of_appointment_creations)
    number_of_appointment_updates = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has updated an appointment") & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_appointment_updates] = "appointment updates"
    common_activity_list.append(number_of_appointment_updates)
    number_of_appointment_deletes = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has deleted an appointment") & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_appointment_deletes] = "appointment deletions"
    common_activity_list.append(number_of_appointment_deletes)
    number_of_user_creations = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has created a new user") & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_user_creations] = "user creations"
    common_activity_list.append(number_of_user_creations)
    number_of_admits = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has admitted the following patient to") & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_admits] = "admits"
    common_activity_list.append(number_of_admits)
    number_of_discharges = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has discharged the following patient from") & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(hospital1=hospital) | Q(hospital2=hospital)).count()
    common_activity_dict[number_of_discharges] = "discharges"
    common_activity_list.append(number_of_discharges)

    common_activity_list.sort(reverse=True)

    most_common_activity = common_activity_dict[common_activity_list[0]]

    number_of_most_common_activity = common_activity_list[0]

    total_number_of_activities = determine_total_number_of_activities(start_date, end_date, hospital)

    if total_number_of_activities == 0:
        return [most_common_activity, number_of_most_common_activity, 0]

    percent_of_most_common_activity = round((number_of_most_common_activity / total_number_of_activities) * 100)

    return [most_common_activity, number_of_most_common_activity,  percent_of_most_common_activity]

def determine_number_of_patients(hospital, start_date, end_date):
    """
    Determines the total number of patients that were admitted to the hospital
    between and including start_date to end_date

    Author: Nick Deyette
    """
    number_of_patients = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has admitted the following patient to") & Q(hospital1=hospital)).count()

    return number_of_patients

def determine_average_number_of_visits_per_patient(hospital, start_date, end_date):
    """
    Determines the average number of visits per patient at hospital
    between start_date and end_date

    Author: Nick Deyette
    """
    average_number_of_visits_per_patient = Appointment.objects.filter(Q(start__lt=end_date) & Q(start__gt=start_date) & Q(end__lt=end_date) & Q(end__gt=start_date)).count()

    return average_number_of_visits_per_patient

def determine_average_length_of_stay(hospital, start_date, end_date):
    """
    Determines the average length of stay between the start_date and end_date
    at the hospital

    Author: Nick Deyette
    """
    admit_list = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has admitted the following patient to") & Q(hospital1=hospital)).values_list('username2', flat=True)

    date_count = 0
    days_total = 0

    for admit in admit_list:
        try:
            admit_dates = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has admitted the following patient to") & Q(hospital1=hospital) & Q(username2=admit))
            dismiss_dates = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains="has discharged the following patient from") & Q(hospital1=hospital) & Q(username2=admit))
            for admit_date in admit_dates:
                for dismiss_date in dismiss_dates:
                    date_difference = abs(admit_date.timestamp - dismiss_date.timestamp)
                    days_total += date_difference.days
            date_count += 1
        except LogItem.DoesNotExist:
            dismiss_date = None

    if date_count != 0:
        average_length_of_stay = round(days_total / date_count)
    else:
        average_length_of_stay = 0

    return average_length_of_stay

def determine_most_common_reason_for_being_admitted(hospital, start_date, end_date):
    """
    Determines the most common reason for being admitted at hospital between
    start_date and end_date

    Author: Nick Deyette
    """
    admit_list = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(hospital1=hospital) & Q(activity__icontains="has admitted the following patient to"))

    emergency_count = 0
    observation_count = 0
    surgery_count = 0
    other_count = 0

    for admit in admit_list:
        if "Emergency" in admit.activity:
            emergency_count += 1
        if "Observation" in admit.activity:
            observation_count += 1
        if "Surgery" in admit.activity:
            surgery_count += 1
        if "Other" in admit.activity:
            other_count += 1

    admit_count_list = [emergency_count, observation_count, surgery_count, other_count]

    admit_count_list.sort()

    most_common_reason_for_being_admitted_count = admit_count_list[-1]

    if most_common_reason_for_being_admitted_count == 0:
        return None
    elif most_common_reason_for_being_admitted_count == emergency_count:
        return "Emergency"
    elif most_common_reason_for_being_admitted_count == observation_count:
        return "Observation"
    elif most_common_reason_for_being_admitted_count == surgery_count:
        return "Surgery"
    elif most_common_reason_for_being_admitted_count == other_count:
        return "Other"
    else:
        return None

def determine_medication_list(hospital):
    """
    Determines the list of all medications prescribed at the
    hospital in the given timeframe.

    Author: Nick Deyette
    """
    medication_list = Prescription.objects.filter(Q(doctor=(Doctor.objects.filter(hospital=hospital)))).values_list('medication', flat=True)

    return medication_list

def determine_doctor_list(hospital):
    """
    Determines the list of all doctors
    at the given hospital.

    Author: Nick Deyette
    """
    doctor_list = Doctor.objects.filter(hospital=hospital)

    return doctor_list

def determine_number_of_times_medication_prescribed(medication, hospital, start_date, end_date):
    """
    Determines the number of times medication was prescribed
    at hospital between start_date and end_date

    Author: Nick Deyette
    """
    number_of_times_medication_prescribed = Prescription.objects.filter(Q(date_prescribed__range=[start_date, end_date]) & Q(medication__icontains=medication) & Q(hospital=hospital)).count()

    return number_of_times_medication_prescribed

def determine_medications_prescribed_by_doctor(doctor, start_date, end_date):
    """
    Determines all of the medications prescribed by doctor
    between start_date and end_date

    Author: Nick Deyette
    """
    medications_prescribed_by_doctor = Prescription.objects.filter(Q(date_prescribed__range=[start_date, end_date]) & Q(doctor=doctor))

    return medications_prescribed_by_doctor
