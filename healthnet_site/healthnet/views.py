from django.http import HttpResponseRedirect
from healthnet.forms import *
from django.contrib.auth import authenticate, login,logout
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from .models import *
from django.db.models import Q
from .functions import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from healthnet_site.settings import MEDIA_ROOT
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
import collections

def index(request):
    """
    Displays the landing page if the user not active
    Re-routes to the appointments page for the user if they are active.

    Author: Nick Deyette
    """
    if request.user.is_authenticated():
        try:
            user_type = request.user.userprofile.user_type
        except UserProfile.DoesNotExist:
            return redirect('/messages')

        if user_type == "admin":
            return redirect('/healthnet/hospital_admin_index')
        else:
            return redirect('/healthnet/appointments')

    if request.method == "POST":
        button_choice = request.POST.get('button_choice')

        if button_choice == "Login":
            return redirect('/healthnet/Login')
        else:
            return redirect('/healthnet/register')
    return render(request, 'healthnet/index.html')

def appointments(request):
    """
    Displays all appointments that can be viewed/edited by current user
    Patient or Doctor: Can view their own appointments
    Nurse: Can view all appointments for the current week

    Author: Kyler Freas
    """

    if not request.user.is_authenticated():
        return redirect('/healthnet/Login')

    try:
        user_type = request.user.userprofile.user_type
    except UserProfile.DoesNotExist:
        return redirect('/healthnet/Login')

    user_id = request.user.id
    username = User.objects.get(pk=user_id).username
    user_type = request.user.userprofile.user_type

    appt_list = Appointment.objects.order_by('-start').reverse()

    if user_type == 'patient':
        patient_id = Patient.objects.get(user_id=user_id).id
        appt_list = [appt for appt in appt_list if appt.patient_id == patient_id]

    if user_type == 'doctor':
        doctor_id = Doctor.objects.get(user_id=user_id).id
        appt_list = [appt for appt in appt_list if appt.doctor_id == doctor_id]

    if user_type == 'nurse':
        date = datetime.datetime.today().replace(tzinfo=None)
        start_week = date - datetime.timedelta(date.weekday())
        end_week = start_week + datetime.timedelta(7)

        appt_list = [appt for appt in appt_list if start_week <= appt.start.replace(tzinfo=None) <= end_week]

    if request.POST.get('create an appointment'):
        return redirect('/healthnet/create_appointment')

    if request.POST.get('edit_info'):
        return redirect('/healthnet/edit_profile_information/%s' % user_id)

    if request.POST.get('logout'):
        logout(request)
        Logger.log_system_activity(activity="has logged out", username1=username, user_type1=user_type)
        return HttpResponseRedirect('index.html')

    data = []
    for appt in appt_list:
        # Calendar title for the appointment
        appt_title = User.objects.get(id=Doctor.objects.get(id=appt.doctor_id).user_id)

        # Show patient if current user is a doctor. Otherwise, show doctor.
        if user_type == 'doctor':
            appt_title = User.objects.get(id=Patient.objects.get(id=appt.patient_id).user_id)

        data.append(
            {
                'id': appt.id,
                'title': appt_title,
                'start': appt.start.replace(tzinfo=None, microsecond=0).isoformat(),
                'end': appt.end.replace(tzinfo=None, microsecond=0).isoformat()
            })

    context = {'appt_list': appt_list, 'json_data': data, 'username': username, 'user_type': user_type, 'user_id': request.user.id}
    return render(request, 'healthnet/appointments.html', context)

def create_appointment(request):
    """
    Allows user to save a new appointment
    This action is logged

    Author: Kyler Freas
    """
    context=RequestContext(request)
    new_appt_form = CreateAppointmentForm(data=request.POST or None)

    date_format = '%Y-%m-%dT%H:%M'

    user_id = request.user.id
    username = request.user.username
    user_type = request.user.userprofile.user_type

    doc_list = Doctor.objects.all()
    patient_list = Patient.objects.all()

    if request.POST.get('create'):
        if request.POST.get('doctor'):
            doctor = request.POST.get('doctor')
            if doctor == "None":
                return redirect('/healthnet/create_appointment_errors.html')
        if request.POST.get('patient'):
            patient = request.POST.get('patient')
            if patient == "None":
                return redirect('/healthnet/create_appointment_errors.html')
        if user_type == 'doctor':
            doctor_id = Doctor.objects.get(user_id=user_id).id
            doctor_username = User.objects.get(pk=user_id).username
            appt_location = Doctor.objects.get(user_id=user_id).hospital
        else:
            doctor_id = request.POST.get('doctor')
            doctor_user_id = Doctor.objects.get(pk=doctor_id).user_id
            doctor_username = User.objects.get(pk=doctor_user_id).username
            appt_location = Doctor.objects.get(pk=doctor_id).hospital

        if user_type == 'patient':
            patient_id = Patient.objects.get(user_id=user_id).id
            patient_username = User.objects.get(pk=user_id).username
        else:
            patient_id = request.POST.get('patient')
            patient_user_id = Patient.objects.get(pk=patient_id).user_id
            patient_username = User.objects.get(pk=patient_user_id).username

        if request.POST.get('start'):
            str_appt_start = request.POST.get('start')

            # Convert date string to timezone-aware date
            appt_start = datetime.datetime.strptime(str_appt_start, date_format) - datetime.timedelta(hours=5)

            print(appt_start)
        else:
            return redirect('/healthnet/create_appointment_errors.html')
        if request.POST.get('end'):
            str_appt_end = request.POST.get('end')

            appt_end = datetime.datetime.strptime(str_appt_end, date_format) - datetime.timedelta(hours=5)
        else:
            return redirect('/healthnet/create_appointment_errors.html')

        # Check for time conflicts
        doc_conflict = Appointment.objects.filter(doctor_id=doctor_id, start__gt=appt_start, start__lt=appt_end).exists() \
                       or Appointment.objects.filter(doctor_id=doctor_id, end__gt=appt_start, end__lt=appt_end).exists() \
                       or Appointment.objects.filter(doctor_id=doctor_id, start=appt_start, end=appt_end).exists()

        patient_conflict = Appointment.objects.filter(patient_id=patient_id, start__gt=appt_start, start__lt=appt_end).exists() \
                       or Appointment.objects.filter(patient_id=patient_id, end__gt=appt_start, end__lt=appt_end).exists() \
                       or Appointment.objects.filter(patient_id=patient_id, start=appt_start, end=appt_end).exists()

        invalid_date = (appt_start+datetime.timedelta(hours=5) < datetime.datetime.now()) or (appt_end < appt_start)

        # If there is a time conflict, abort saving the appointment
        if doc_conflict:
            context = {'doc_list': doc_list, 'patient_list': patient_list, 'username': username,
                       'doc_conflict': doc_conflict, 'user_id': request.user.id, 'patient_id': patient_id, 'doctor_id': doctor_id,
                       'user_type': request.user.userprofile.user_type, 'start': str_appt_start, 'end': str_appt_end}
            return render(request, 'healthnet/create_appointment.html', context)
        elif patient_conflict:
            context = {'doc_list': doc_list, 'patient_list': patient_list, 'username': username,
                       'patient_conflict': patient_conflict, 'user_id': request.user.id, 'patient_id': patient_id, 'doctor_id': doctor_id,
                       'user_type': request.user.userprofile.user_type, 'start': str_appt_start, 'end': str_appt_end}
            return render(request, 'healthnet/create_appointment.html', context)
        elif invalid_date:
            context = {'doc_list': doc_list, 'patient_list': patient_list, 'username': username,
                       'invalid_date': invalid_date, 'user_id': request.user.id, 'patient_id': patient_id, 'doctor_id': doctor_id,
                       'user_type': request.user.userprofile.user_type, 'start': str_appt_start, 'end': str_appt_end}
            return render(request, 'healthnet/create_appointment.html', context)

        new_appointment = Appointment(doctor_id=doctor_id, patient_id=patient_id, location=appt_location, start=appt_start, end=appt_end)
        new_appointment.save()

        Logger.log_system_activity(activity="has created an appointment with", username1=doctor_username, username2=patient_username, user_type1="doctor", user_type2="patient", hospital1=appt_location)

        return redirect('/healthnet/appointments/')

    if request.POST.get("back"):
        return redirect('/healthnet/appointments')

    context = {'doc_list': doc_list, 'patient_list': patient_list, 'username': username, 'user_id': request.user.id,
               'user_type': request.user.userprofile.user_type}

    return render(request, 'healthnet/create_appointment.html', context)

def create_appointment_errors(request):
    """
    Displays the errors page for creating an appointment.

    Author: Nick Deyette
    """
    username = request.user.username

    if request.POST.get('back'):
        return redirect('/healthnet/create_appointment')

    return render(request, 'healthnet/create_appointment_errors.html', {'username': username, 'user_id': request.user.id,
                                                                        'user_type': request.user.userprofile.user_type})

def view_appointment(request, appointment_id):
    """
    Displays data for an appointment
    :param appointment_id: id of appointment to be viewed in the database

    Author: Kyler Freas
    """

    username = request.user.username
    user_type = request.user.userprofile.user_type

    if request.POST.get('delete'):
        return redirect('/healthnet/delete_appointment/%s' % appointment_id)
    if request.POST.get("back"):
        return redirect('/healthnet/appointments')
    if request.POST.get("edit"):
        return redirect('/healthnet/update_appointment/%s' % appointment_id)
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        # No appointment with the given id found
        raise Http404("Appointment does not exist")

    doctor = Doctor.objects.get(id=appointment.doctor_id)
    patient = Patient.objects.get(id=appointment.patient_id)
    appt_start = appointment.start.replace(tzinfo=None)
    appt_end = appointment.end.replace(tzinfo=None)
    location = appointment.location

    can_edit = appt_start > datetime.datetime.now()

    return render(request, 'healthnet/view_appointment.html', {'doctor': doctor, 'patient': patient,
                                                               'start': appt_start, 'end': appt_end,
                                                               'id': appointment_id, 'username': username,
                                                               'user_type': user_type, 'location': location,
                                                               'user_id': request.user.id, 'can_edit': can_edit})


def update_appointment(request, appointment_id):
    """
    Allows user to update an existing appointment
    :param appointment_id: id of appointment to be saved in the database

    This action is logged.

    Author: Kyler Freas
    """
    username = request.user.username
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        # No appointment with the given id found
        raise Http404("Appointment does not exist")

    user_type = request.user.userprofile.user_type

    doc_list = Doctor.objects.all()
    patient_list = Patient.objects.all()

    str_start = appointment.start.replace(tzinfo=None, microsecond=0).isoformat()
    str_end = appointment.end.replace(tzinfo=None, microsecond=0).isoformat()

    if request.POST.get('delete'):
        return redirect('/healthnet/delete_appointment/%s' % appointment_id)
    elif request.POST.get('cancel'):
        return redirect('/healthnet/view_appointment/%s' % appointment_id)
    elif request.POST.get('update'):
        if user_type == 'doctor':
            new_doc = Doctor.objects.get(user_id=request.user.id).id
        else:
            new_doc = request.POST.get('doctor')

        doctor_username = User.objects.get(pk=Doctor.objects.get(pk=new_doc).pk)
        appt_location = Doctor.objects.get(pk=new_doc).hospital

        if user_type == 'patient':
            new_patient = Patient.objects.get(user_id=request.user.id).id
        else:
            new_patient = request.POST.get('patient')

        patient_username = User.objects.get(pk=Patient.objects.get(pk=new_patient).pk)

        str_new_start = request.POST.get('start')
        str_new_end = request.POST.get('end')

        date_format = '%Y-%m-%dT%H:%M' + (':%S' if str_new_start == str_start else '')

        # Convert date string to timezone-aware date
        new_start = datetime.datetime.strptime(str_new_start, date_format) - datetime.timedelta(hours=5)

        date_format = '%Y-%m-%dT%H:%M' + (':%S' if str_new_end == str_end else '')

        # Convert date string to timezone-aware date
        new_end = datetime.datetime.strptime(str_new_end, date_format) - datetime.timedelta(hours=5)

        if new_start != str_start and new_end != str_end:
            doctor_id = appointment.doctor_id
            patient_id = appointment.patient_id
            doctor = Doctor.objects.get(id=doctor_id)
            patient = Patient.objects.get(id=patient_id)

            # Check for time conflicts
            doc_conflict = Appointment.objects.filter(~Q(id=appointment_id), doctor_id=new_doc, start__gt=new_start, start__lt=new_end).exists() \
                       or Appointment.objects.filter(~Q(id=appointment_id), doctor_id=new_doc, end__gt=new_start, end__lt=new_end).exists() \
                       or Appointment.objects.filter(~Q(id=appointment_id), doctor_id=new_doc, start=new_start, end=new_end).exists()

            patient_conflict = Appointment.objects.filter(~Q(id=appointment_id), patient_id=new_patient, start__gt=new_start, start__lt=new_end).exists() \
                       or Appointment.objects.filter(~Q(id=appointment_id), patient_id=new_patient, end__gt=new_start, end__lt=new_end).exists() \
                       or Appointment.objects.filter(~Q(id=appointment_id), patient_id=new_patient, start=new_start, end=new_end).exists()

            invalid_date = (new_start >= new_end)

            # If there is a time conflict, abort saving the appointment
            if doc_conflict:
                context = {'doc_list': doc_list, 'patient_list': patient_list, 'doctor': doctor,
                           'patient': patient, 'start': str_new_start, 'end': str_new_end, 'id': appointment_id,
                           "user_type": user_type, 'username': username, 'doc_conflict': doc_conflict,
                           'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}
                return render(request, 'healthnet/update_appointment.html', context)
            elif patient_conflict:
                context = {'doc_list': doc_list, 'patient_list': patient_list, 'doctor': doctor,
                           'patient': patient, 'start': str_new_start, 'end': str_new_end, 'id': appointment_id,
                           "user_type": user_type, 'username': username, 'patient_conflict': patient_conflict,
                           'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}
                return render(request, 'healthnet/update_appointment.html', context)
            elif invalid_date:
                context = {'doc_list': doc_list, 'patient_list': patient_list, 'doctor': doctor,
                           'patient': patient, 'start': str_new_start, 'end': str_new_end, 'id': appointment_id,
                           "user_type": user_type, 'username': username, 'invalid_date': invalid_date,
                           'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}
                return render(request, 'healthnet/update_appointment.html', context)

        appointment.update_appointment(new_doctor_id=new_doc, new_patient_id=new_patient, new_start=new_start, new_end=new_end)

        Logger.log_system_activity(activity="has updated an appointment with", username1=doctor_username, username2=patient_username, user_type1="doctor", user_type2="patient", hospital1=appt_location)

        return redirect('/healthnet/appointments/')

    doctor = Doctor.objects.get(id=appointment.doctor_id)
    patient = Patient.objects.get(id=appointment.patient_id)

    return render(request, 'healthnet/update_appointment.html',
            {'doc_list': doc_list, 'patient_list': patient_list, 'doctor': doctor, 'patient': patient, 'start': str_start, 'end': str_end, 'id': appointment_id, "user_type": user_type, 'username': username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})

def delete_appointment(request, appointment_id):
    """
    Displays the confirmation page for deleting an appointment.
    This action is logged.

    :param: appointment_id: id of appointment that is being displayed

    Author: Nick Deyette
    """
    username = request.user.username
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        raise Http404("Appointment does not exist")

    if request.POST.get('confirm'):
        appointment.delete()
        doctor_user_id = Doctor.objects.get(pk=appointment.doctor_id).user_id
        doctor_username = User.objects.get(pk=doctor_user_id)
        location = Doctor.objects.get(pk=appointment.doctor_id).hospital
        patient_user_id = Patient.objects.get(pk=appointment.patient_id).user_id
        patient_username = User.objects.get(pk=patient_user_id)
        Logger.log_system_activity(activity="has deleted an appointment with", username1=doctor_username, username2=patient_username, user_type1="doctor", user_type2="patient", hospital1=location)
        return redirect('/healthnet/appointments/')
    elif request.POST.get('deny'):
        return redirect('/healthnet/view_appointment/%s' % appointment_id)

    doctor = Doctor.objects.get(id=appointment.doctor_id)
    patient = Patient.objects.get(id=appointment.patient_id)
    datetime = appointment.start

    return render(request, 'healthnet/delete_appointment.html', {'doctor': doctor, 'patient': patient, 'datetime': datetime, 'username': username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})

def hospital_admin_index(request):
    """
    Displays the index for hospital admins.

    Author: Nick Deyette
    """
    user_name = request.user.username
    if request.method == "POST":
        if request.POST.get('create'):
            return redirect('/healthnet/hospital_admin/create_user')
        elif request.POST.get('view_logs'):
            return redirect('/healthnet/hospital_admin/view_logs')
        elif request.POST.get('view_system_statistics'):
            return redirect('/healthnet/hospital_admin_view_system_statistics')
        elif request.POST.get('change_password'):
            return redirect('/healthnet/change_password/%s' % request.user.id)
        elif request.POST.get('transfer_patient'):
            return redirect('/healthnet/transfer_patient')
    return render(request, 'healthnet/hospital_admin_index.html', {'username': user_name, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})

def doctor_index(request):
    """
    Landing page for doctor login

    Author: Kyler Freas
    """
    username = request.user.username
    user_id = request.user.id

    return render(request, 'healthnet/doctor_index.html', {'username': username, 'user_id': user_id, 'user_type': request.user.userprofile.user_type})

def nurse_index(request):
    """
    Landing page for doctor login

    Author: Kyler Freas
    """
    return render(request, 'healthnet/nurse_index.html', {'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})

def hospital_admin_create_user(request):
    """
    Displays the page that allows a hospital admin to create a new user (Doctor, Nurse, Admin)
    This action is logged

    Author: Nick Deyette
    """
    user_name = request.user.username
    admin_username = User.objects.get(pk=request.user.id).username

    context = RequestContext(request)
    user_form = UserForm(request.POST or None)
    create_user_form = AdminCreateUserForm(request.POST or None)

    if request.POST.get("back2"):
        return redirect('/healthnet/hospital_admin_index')

    if request.POST.get("submit"):
        if user_form.is_valid() and create_user_form.is_valid():
            new_user=user_form.save()
            new_user.set_password(new_user.password)

            username = new_user.username

            form_data=create_user_form.cleaned_data
            user_type = form_data.get('user_type')
            first_name = form_data.get('first_name')
            last_name = form_data.get('last_name')
            hospital = form_data.get('hospital')

            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()

            Logger.log_system_activity(activity="has created a new user:", username1=admin_username, username2=username, user_type1="admin", user_type2=user_type, hospital1=hospital)
            if user_type == "nurse":
                new_nurse = Nurse(user_id=new_user.pk, hospital=hospital)
                new_nurse.save()
                user_profile = UserProfile(user=new_user, user_type="nurse")
                user_profile.save()
            elif user_type == "doctor":
                new_doctor = Doctor(user_id=new_user.pk, hospital=hospital)
                new_doctor.save()
                user_profile = UserProfile(user=new_user, user_type="doctor")
                user_profile.save()
            else:
                new_admin = Administrator(user_id=new_user.pk, hospital=hospital)
                new_admin.save()
                user_profile = UserProfile(user=new_user, user_type="admin")
                user_profile.save()
            return redirect('/healthnet/hospital_admin_create_user_success')

    hospital_list = Hospital.objects.all()
    return render_to_response('healthnet/hospital_admin_create_user.html', {'user_form': user_form, 'form': create_user_form, 'username': user_name, 'hospital_list': hospital_list, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}, context)

def hospital_admin_create_user_success(request):
    """
    Displays a page stating that the creation of the user was
    successful

    Author: Nick Deyette
    """
    username = request.user.username
    if request.method == "POST":
        return redirect('/healthnet/hospital_admin_index')
    return render(request, 'healthnet/hospital_admin_create_user_success.html', {'username': username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})

def hospital_admin_create_user_failure(request):
    """
    Displays a page stating that the creation of the user was
    a failure.

    Author: Nick Deyette
    """
    username = request.user.username
    if request.POST.get('back'):
        return redirect('/healthnet/hospital_admin/create_user')
    return render(request, 'healthnet/hospital_admin_create_user_failure.html', {'username': username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})

def hospital_admin_view_logs(request):
    """
    Displays all of the log actions

     Author: Nick Deyette
    """
    username = request.user.username
    filter = "None"

    if request.POST.get("back"):
        return redirect('/healthnet/hospital_admin_index')
    if request.POST.get("filter"):
        return redirect('/healthnet/hospital_admin_view_logs_create_filters')
    logs = LogItem.objects.order_by('-timestamp')

    context = {'logs': logs, 'username': username, 'filter': filter, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}

    return render(request, 'healthnet/hospital_admin_view_logs.html', context)

def hospital_admin_view_logs_with_filters(request, start_date, end_date, user_name, user_type, action, hospital):
    """
    Displays all of the log items based on the filters passed in

     Author: Nick Deyette
    """
    username = request.user.username
    user_type = user_type.lower()
    action_message = determine_action(action)

    if request.POST.get("back"):
        return redirect('/healthnet/hospital_admin_index')

    if start_date != '' and end_date != '' and user_name != '' and user_type != '' and action != '' and hospital != '':
        # filter by date, username, user type, action and hospital
        filter = start_date + " to " + end_date + " for " + user_name + " of type: " + user_type + " of action: " + action + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type != '' and action != '' and hospital != '':
        # filter by username, user type, action and hospital
        filter = " For " + user_name + " of type: " + user_type + " of action: " + action + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(
            (Q(username1=user_name) | Q(username2=user_name)) & (
            Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message) & (
            Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name != '' and user_type != '' and action != '' and hospital == '':
        # filter by date, username, user type and action
        filter = start_date + " to " + end_date + " for " + user_name + " of type: " + user_type + " of action: " + action
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type == '' and action == '' and hospital != '':
        # filter by hospital
        filter = " At hospital: " + hospital
        filtered_logs = LogItem.objects.filter((Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type == '' and action == '' and hospital != '':
        # filter by date and hospital
        filter = start_date + " to " + end_date + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type == '' and action == '' and hospital != '':
        # filter by username and hospital
        filter = " For " + user_name + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter((Q(username1=user_name) | Q(username2=user_name)) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name != '' and user_type == '' and action == '' and hospital != '':
        # filter by date, username, and hospital
        filter = start_date + " to " + end_date + " for " + user_name + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type != '' and action == '' and hospital != '':
        # filter by user type and hospital
        filter = " Of type: " + user_type + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter((Q(user_type1=user_type) | Q(user_type2=user_type)) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type != '' and action == '' and hospital != '':
        # filter by date, user type, and hospital
        filter = start_date + " to " + end_date + " of type: " + user_type + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type != '' and action == '' and hospital != '':
        # filter by username, user type, and hospital
        filter = " For " + user_name + " of type: " + user_type + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter((Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type == '' and action != '' and hospital != '':
        # filter by date, action and hospital
        filter = start_date + " to " + end_date + " of action: " + action + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains=action_message) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type == '' and action != '' and hospital != '':
        # filter by action and hospital
        filter = " Of action: " + action + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(Q(activity__icontains=action_message) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name != '' and user_type != '' and action == '' and hospital != '':
        # filter by date, username, user type, and hospital
        filter = start_date + " to " + end_date + " for " + user_name + " of type: " + user_type + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type == '' and action != '' and hospital != '':
        # filter by username, action and hospital
        filter = " For " + user_name + " of action: " + action + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter((Q(username1=user_name) | Q(username2=user_name)) & Q(activity__icontains=action_message) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name != '' and user_type == '' and action != '' and hospital != '':
        # filter by date, username, action and hospital
        filter = start_date + " to " + end_date + " for " + user_name + " of action: " + action + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & Q(activity__icontains=action_message) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type != '' and action != '' and hospital != '':
        # filter by user type, action and hospital
        filter = " Of type: " + user_type + " of action: " + action + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter((Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type != '' and action != '' and hospital != '':
        # filter by date, user type, action and hospital
        filter = start_date + " to " + end_date + " of type: " + user_type + " of action: " + action + " at hospital: " + hospital
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message) & (Q(hospital1=hospital) | Q(hospital2=hospital))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name != '' and user_type != '' and action == '':
        # filter by date, username and user type
        filter = start_date + " to " + end_date + " for " + user_name + " of type: " + user_type
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type))).order_by("-timestamp")
    elif start_date != '' and end_date != '' and user_name != '' and user_type == '' and action != '':
        # filter by date, username and action
        filter = start_date + " to " + end_date + " for " + user_name + " of action: " + action
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type != '' and action != '':
        # filter by date, user type and action
        filter = start_date + " to " + end_date + " of type: " + user_type + " of action: " + action
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type != '' and action != '':
        # filter by username, user type and action
        filter = " For " + user_name + " of type: " + user_type + " of action: " + action
        filtered_logs = LogItem.objects.filter((Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name != '' and user_type == '' and action == '':
        # filter by date and username
        filter = start_date + " to " + end_date + " for " + user_name
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(username1=user_name) | Q(username2=user_name))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type != '' and action == '':
        # filter by date and user type
        filter = start_date + " to " + end_date + " of type: " + user_type
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & (Q(user_type1=user_type) | Q(user_type2=user_type))).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type != '' and action == '':
        # filter by username and user type
        filter = "For " + user_name + " of type: " + user_type
        filtered_logs = LogItem.objects.filter((Q(username1=user_name) | Q(username2=user_name)) & (Q(user_type1=user_type) | Q(user_type2=user_type))).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type == '' and action != '':
        # filter by date and action
        filter = start_date + " to " + end_date + " of action: " + action
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date]) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type == '' and action != '':
        # filter by username and action
        filter = " For " + user_name + " of action: " + action
        filtered_logs = LogItem.objects.filter((Q(username1=user_name) | Q(username2=user_name)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type != '' and action != '':
        # filter by user type and action
        filter = " Of type: " + user_type + " of action: " + action
        filtered_logs = LogItem.objects.filter((Q(user_type1=user_type) | Q(user_type2=user_type)) & Q(activity__icontains=action_message)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type != '' and action == '':
        # filter by user type
        filter = "Of type: " + user_type
        filtered_logs = LogItem.objects.filter(Q(user_type1=user_type) | Q(user_type2=user_type)).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name != '' and user_type == '' and action == '':
        # filter by username
        filter = "For " + user_name
        filtered_logs = LogItem.objects.filter(Q(username1=user_name) | Q(username2=user_name)).order_by('-timestamp')
    elif start_date != '' and end_date != '' and user_name == '' and user_type == '' and action == '':
        # filter by date
        filter = start_date + " to " + end_date
        filtered_logs = LogItem.objects.filter(Q(timestamp__range=[start_date, end_date])).order_by('-timestamp')
    elif start_date == '' and end_date == '' and user_name == '' and user_type == '' and action != '':
        # filter by action
        filter = " Of action: " + action
        filtered_logs = LogItem.objects.filter(Q(activity__icontains=action_message)).order_by('-timestamp')
    else:
        # no filters
        return hospital_admin_view_logs(request)

    return render(request, 'healthnet/hospital_admin_view_logs.html', {'logs': filtered_logs, 'username': username, 'filter': filter, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})

def hospital_admin_view_logs_create_filters(request):
    """
    Displays the page responsible for allowing an admin to create filters
    for log activities.

    Author: Nick Deyette
    """
    username = request.user.username

    if request.POST.get('back_create'):
        return redirect('/healthnet/hospital_admin/view_logs')

    if request.POST.get('back_choose'):
        return redirect('/healthnet/hospital_admin_view_logs_create_filters')

    if request.POST.get('submit_create'):
        if request.POST.get('date'):
            date = request.POST.get('date')
        else:
            date = ''
        if request.POST.get('username'):
            user_name = request.POST.get('username')
        else:
            user_name = ''
        if request.POST.get('user_type'):
            user_type = request.POST.get('user_type')
        else:
            user_type = ''
        if request.POST.get('action'):
            action = request.POST.get('action')
        else:
            action = ''
        if request.POST.get('hospital'):
            hospital = request.POST.get('hospital')
        else:
            hospital = ''

        user_list = User.objects.all
        user_type_list = ['Patient', 'Nurse', 'Doctor', 'Admin']
        action_list = ['Logging In', 'Logging Out', 'Create Appointment', 'Update Appointment', 'Delete Appointment', 'Create User', 'Update Profile Info', 'Register', 'Change Password',
                       'Exporting Information', 'Creating Prescription', 'Removing Prescription', 'Admitting Patient', 'Discharging Patient', 'Updating Medical Info', 'Transferring Patient']
        hospital_list = Hospital.objects.all
        return render(request, 'healthnet/hospital_admin_view_logs_choose_filters.html', {'username': username, 'date': date, 'user_name': user_name, 'user_type': user_type, 'user_list': user_list, 'user_type_list': user_type_list, 'action': action, 'action_list': action_list, 'hospital': hospital, 'hospital_list': hospital_list, 'user_id': request.user.id})

    if request.POST.get('submit_choose'):
        if request.POST.get('start_date'):
            start_date = request.POST.get('start_date')
        else:
            start_date = ''
        if request.POST.get('end_date'):
            end_date = request.POST.get('end_date')
        else:
            end_date = ''
        if request.POST.get('user_name'):
            user_name = request.POST.get('user_name')
        else:
            user_name = ''
        if request.POST.get('user_type'):
            user_type = request.POST.get('user_type')
        else:
            user_type = ''
        if request.POST.get('action'):
            action = request.POST.get('action')
        else:
            action = ''
        if request.POST.get('hospital'):
            hospital = request.POST.get('hospital')
        else:
            hospital = ''
        return hospital_admin_view_logs_with_filters(request, start_date, end_date, user_name, user_type, action, hospital)

    return render(request, 'healthnet/hospital_admin_view_logs_create_filters.html', {'username': username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})


def hospital_admin_view_system_statistics(request):
    """
    Displays the most system statistics at the
    Admin's hospital.

    Author: Nick Deyette
    """
    username = request.user.username
    hospital = Administrator.objects.get(user_id=request.user.id).hospital

    context = RequestContext(request)
    timeframe_form = SelectTimeframeForm(request.POST or None)

    if request.POST.get('back-select_date'):
        return redirect('/healthnet/hospital_admin_index/view_logs')
    if request.POST.get('back-errors'):
        return redirect('/healthnet/hospital_admin_view_system_statistics_select_date')
    if request.POST.get('back-statistics'):
        return redirect('/healthnet/hospital_admin_index')
    if request.POST.get("view_prescription_statistics"):
        return redirect('/healthnet/hospital_admin_view_prescription_statistics')
    if request.POST.get('submit'):
        if timeframe_form.is_valid():
            form_data = timeframe_form.cleaned_data
            start_date = form_data.get('start_date')
            end_date = form_data.get('end_date')

            # System statistics information
            number_of_patients = determine_number_of_patients(hospital, start_date, end_date)
            average_number_of_visits_per_patient = determine_average_number_of_visits_per_patient(hospital, start_date, end_date)
            average_length_of_stay = determine_average_length_of_stay(hospital, start_date, end_date)
            most_common_reason_for_being_admitted = determine_most_common_reason_for_being_admitted(hospital, start_date, end_date)

            # Most common activities information
            total_number_of_activities = determine_total_number_of_activities(start_date, end_date, hospital)

            most_common_activity_list = determine_most_common_activity(start_date, end_date, hospital)
            most_common_activity = most_common_activity_list[0]
            number_of_most_common_activity = most_common_activity_list[1]
            percent_of_most_common_activity = most_common_activity_list[2]

            most_common_patient_activity_list = determine_most_common_user_activity(start_date, end_date, "patient", hospital)
            most_common_patient_activity = most_common_patient_activity_list[0]
            number_of_most_common_patient_activity = most_common_patient_activity_list[1]
            percent_of_most_common_patient_activity = most_common_patient_activity_list[2]

            most_common_nurse_activity_list = determine_most_common_user_activity(start_date, end_date, "nurse", hospital)
            most_common_nurse_activity = most_common_nurse_activity_list[0]
            number_of_most_common_nurse_activity = most_common_nurse_activity_list[1]
            percent_of_most_common_nurse_activity = most_common_nurse_activity_list[2]

            most_common_doctor_activity_list = determine_most_common_user_activity(start_date, end_date, "doctor", hospital)
            most_common_doctor_activity = most_common_doctor_activity_list[0]
            number_of_most_common_doctor_activity = most_common_doctor_activity_list[1]
            percent_of_most_common_doctor_activity = most_common_doctor_activity_list[2]

            most_common_admin_activity_list = determine_most_common_user_activity(start_date, end_date, "admin", hospital)
            most_common_admin_activity = most_common_admin_activity_list[0]
            number_of_most_common_admin_activity = most_common_admin_activity_list[1]
            percent_of_most_common_admin_activity = most_common_admin_activity_list[2]

            return render(request, 'healthnet/hospital_admin_view_system_statistics.html', {'username': username,
                                                                                            'start_date': start_date,
                                                                                            'end_date': end_date,
                                                                                            'hospital': hospital,
                                                                                            'number_of_patients': number_of_patients,
                                                                                            'average_number_of_visits_per_patient': average_number_of_visits_per_patient,
                                                                                            'average_length_of_stay': average_length_of_stay,
                                                                                            'most_common_reason_for_being_admitted': most_common_reason_for_being_admitted,
                                                                                            'total_number_of_activities': total_number_of_activities,
                                                                                            'most_common_activity': most_common_activity,
                                                                                            'number_of_most_common_activity': number_of_most_common_activity,
                                                                                            'percent_of_most_common_activity': percent_of_most_common_activity,
                                                                                            'most_common_patient_activity': most_common_patient_activity,
                                                                                            'number_of_most_common_patient_activity': number_of_most_common_patient_activity,
                                                                                            'percent_of_most_common_patient_activity': percent_of_most_common_patient_activity,
                                                                                            'most_common_nurse_activity': most_common_nurse_activity,
                                                                                            'number_of_most_common_nurse_activity': number_of_most_common_nurse_activity,
                                                                                            'percent_of_most_common_nurse_activity': percent_of_most_common_nurse_activity,
                                                                                            'most_common_doctor_activity': most_common_doctor_activity,
                                                                                            'number_of_most_common_doctor_activity': number_of_most_common_doctor_activity,
                                                                                            'percent_of_most_common_doctor_activity': percent_of_most_common_doctor_activity,
                                                                                            'most_common_admin_activity': most_common_admin_activity,
                                                                                            'number_of_most_common_admin_activity': number_of_most_common_admin_activity,
                                                                                            'percent_of_most_common_admin_activity': percent_of_most_common_admin_activity,
                                                                                            'user_id': request.user.id,
                                                                                            'user_type': request.user.userprofile.user_type
                                                                                            })

    return render_to_response('healthnet/hospital_admin_view_system_statistics_select_date.html', {'timeframe_form': timeframe_form, 'username': username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}, context)

def hospital_admin_view_prescription_statistics(request):
    """
    Displays the page for all of the
    prescription statistics.

    Author: Nick Deyette
    """
    admin_user_id = request.user.id
    admin = Administrator.objects.get(user_id=admin_user_id)
    admin_hospital = admin.hospital

    if request.POST.get('submit'):
        if request.POST.get('start_date'):
            start_date = request.POST.get('start_date')
        else:
            return render(request, 'healthnet/hospital_admin_view_prescription_statistics_errors.html', {'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})
        if request.POST.get('end_date'):
            end_date = request.POST.get('end_date')
        else:
            return render(request, 'healthnet/hospital_admin_view_prescription_statistics_errors.html', {'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})
        if request.POST.get('doctor') != 'Select a doctor':
            doctor_username = request.POST.get('doctor')
            doctor_user_id = User.objects.get(username=doctor_username).id
            doctor = Doctor.objects.get(user_id=doctor_user_id)
            medications_prescribed_by_doctor = determine_medications_prescribed_by_doctor(doctor, start_date, end_date)
        else:
            doctor = ''
            medications_prescribed_by_doctor = ''
        if request.POST.get('medication') != 'Select a medication':
            medication = request.POST.get('medication')
            number_of_times_medication_prescribed = determine_number_of_times_medication_prescribed(medication, admin_hospital, start_date, end_date)
        else:
            medication = ''
            number_of_times_medication_prescribed = ''

        return render(request, 'healthnet/hospital_admin_view_prescription_statistics.html', {'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type,
                                                                                              'start_date': start_date,
                                                                                              'end_date': end_date,
                                                                                              'medication': medication,
                                                                                              'doctor': doctor,
                                                                                              'hospital': admin_hospital,
                                                                                              'number_of_times_medication_prescribed': number_of_times_medication_prescribed,
                                                                                              'medications_prescribed_by_doctor': medications_prescribed_by_doctor})
    if request.POST.get('back_choose_date_and_type'):
        return redirect('/healthnet/hospital_admin_index')

    medication_list = determine_medication_list(admin_hospital)
    doctor_list = determine_doctor_list(admin_hospital)

    return render(request, 'healthnet/hospital_admin_view_prescription_statistics_choose_date_and_type.html', {'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type, 'medication_list': medication_list, 'doctor_list': doctor_list})

def transfer_patient(request):
    """
    Displays the page for transferring patients.

    Author: Nick Deyette
    """
    user_type = request.user.userprofile.user_type
    new_hospital = None

    if user_type == 'doctor':
        doctor_user_id = request.user.id
        doctor = Doctor.objects.get(user_id=doctor_user_id)
        new_hospital = doctor.hospital
    elif user_type == 'admin':
        admin_user_id = request.user.id
        admin = Administrator.objects.get(user_id=admin_user_id)
        new_hospital = admin.hospital

    context=RequestContext(request)
    transfer_form = TransferPatientForm(data=request.POST or None)
    transfer_form.fields['patient'].queryset = Patient.objects.filter(~Q(current_hospital=new_hospital), ~Q(current_hospital=None))

    if request.POST.get('back'):
        return HttpResponseRedirect('index')
    if request.POST.get('transfer'):
        if transfer_form.is_valid():
            form_data = transfer_form.cleaned_data
            patient = form_data.get('patient')

            patient_username = User.objects.get(id=patient.user_id)
            patient_old_hospital = patient.current_hospital

            patient.transfer_patient(new_hospital)
            Logger.log_system_activity(activity="has transferred the following patient to " + new_hospital.name + " from " + patient_old_hospital.name + ": ", username1=request.user.username, user_type1=user_type, username2=patient_username, user_type2="patient", hospital1=patient_old_hospital.name, hospital2=new_hospital.name)
            return HttpResponseRedirect('index')

    return render_to_response('healthnet/transfer_patient.html', {'form': transfer_form}, context)

def edit_profile_information(request, user_id):
    """
    Displays the page allowing a Patient to edit their information
    This action is logged

    :param user_id: the user_id of the patient editing their page
    """
    user = User.objects.get(pk=user_id)
    username = User.objects.get(pk=user_id).username
    patient = Patient.objects.get(user_id=user_id)
    contact_number = patient.contact_number
    emergency_contact_number = patient.emergency_contact_number
    first_name = patient.first_name
    last_name = patient.last_name
    address = patient.address
    prescription_list = Prescription.objects.filter(patient=patient)
    test_result_list = TestResult.objects.filter(patient=patient)

    if request.POST.get('edit_info'):
        return redirect('/healthnet/edit_profile_information_edit')
    elif request.POST.get('cancel'):
        return redirect('/healthnet/appointments')
    elif request.POST.get('password'):
        return redirect('/healthnet/change_password/%s' % user_id)
    elif request.POST.get('export_info'):
        return redirect('/healthnet/edit_profile_information_export_info_download')

    context = {'user': user, 'contact_number': contact_number, 'emergency_contact_number': emergency_contact_number,
               'username': username, 'first_name': first_name, 'last_name': last_name, 'address': address,
               'prescription_list': prescription_list, 'preferred_hospital': patient.preferred_hospital,
               'current_hospital': patient.current_hospital, 'insurance_company': patient.insurance_company,
               'insurance_id': patient.insurance_id, 'age': patient.age, 'weight': patient.weight,
               'height': patient.height, 'test_result_list': test_result_list, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type,
               'city': patient.city, 'state': patient.state, 'zipcode': patient.zipcode}

    return render(request, 'healthnet/edit_profile_information.html', context)

def edit_profile_information_edit(request):
    """
    Displays the page allowing the user to edit
    their profile information.

    Author: Nick Deyette
    """

    patient_user_id = request.user.id
    patient = Patient.objects.get(user_id=patient_user_id)

    user = User.objects.get(pk=request.user.id)

    state_choices = {
         'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
         'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia',
         'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana',
         'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
         'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
         'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
         'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
         'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
         'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
         'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }

    state_choice_keys = collections.OrderedDict(sorted(state_choices.items()))

    del state_choice_keys[patient.state]

    if request.POST.get('submit'):
        if request.POST.get('new_email'):
            new_email = request.POST.get('new_email')
        else:
            return redirect('/healthnet/edit_profile_information_failure')
        if request.POST.get('new_contact_number'):
            new_contact_number = request.POST.get('new_contact_number')
        else:
            return redirect('/healthnet/edit_profile_information_failure')
        if request.POST.get('new_emergency_contact_number'):
            new_emergency_conact_number = request.POST.get('new_emergency_contact_number')
        else:
            return redirect('/healthnet/edit_profile_information_failure')
        if request.POST.get('new_address'):
            new_address = request.POST.get('new_address')
        else:
            return redirect('/healthnet/edit_profile_information_failure')
        if request.POST.get('new_city'):
            new_city = request.POST.get('new_city')
        else:
            return redirect('/healthnet/edit_profile_information_failure')
        if request.POST.get('new_zipcode'):
            new_zipcode = request.POST.get('new_zipcode')
        else:
            return redirect('/healthnet/edit_profile_information_failure')
        if request.POST.get('new_state'):
            new_state = request.POST.get('new_state')
        else:
            return redirect('/healthnet/edit_profile_information_failure')
        patient.update_profile_info(new_email=new_email, new_contact_number=new_contact_number, new_emergency_contact_number=new_emergency_conact_number, new_address=new_address,
                                    new_city=new_city, new_zipcode=new_zipcode, new_state=new_state)
        Logger.log_system_activity(activity="has updated their profile information", username1=user.username, user_type1=user.userprofile.user_type)
        return redirect('/healthnet/edit_profile_information/%s' % request.user.id)
    if request.POST.get('back'):
        return redirect('/healthnet/edit_profile_information/%s' % request.user.id)

    return render(request, 'healthnet/edit_profile_information_edit.html', {'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type, 'user': user, 'patient': patient, 'state_choices': state_choice_keys})

def edit_profile_information_failure(request):
    """
    Displays a page when an error occurs in editing profile
    information.

    Author: Nick Deyette
    """
    if request.POST.get('back'):
        return redirect('/healthnet/edit_profile_information/%s' % request.user.id)
    return render(request, 'healthnet/edit_profile_information_failure.html', {'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})

def edit_profile_information_export_info(request):
    """
    Displays a page that first prompts for confirmation of the download.
    Then creates a PDF and downloads it to the user's computer.

    Author: Nick Deyette
    """
    if request.POST.get('cancel'):
        return redirect('/healthnet/edit_profile_information/%s' % request.user.id)
    if request.POST.get('continue-download'):
        Logger.log_system_activity(activity="has exported their profile information", username1=request.user.username,
                                   user_type1="patient")
        return redirect('/healthnet/edit_profile_information/%s' % request.user.id)
    return render(request, 'healthnet/edit_profile_information_export_info_download.html', {'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type})

def register_success(request):
    '''to display the successful registration message
    Author:Smruthi
    date: 30 Sep 2016'''
    return render(request,'healthnet/Success.html')

def register(request):
    '''view to register new user
    fetches the data from the form and saves the information required for registering the new Patient
    Author:Smruthi
    date: 30 Sep 2016
    this action is logged'''
    context=RequestContext(request)
    registered=False
    if request.method == 'POST':
        if request.POST.get('submit'):
            new_user_form=UserForm(data=request.POST)
            new_profile_form=UserProfileForm(data=request.POST)


            if new_user_form.is_valid() and new_profile_form.is_valid():
                user=new_user_form.save()
                user.set_password(user.password)
                user.save()

                user_id = user.pk

                profile=new_profile_form.save(commit=False)

                user_profile = UserProfile(user=user, user_type="patient")

                user_profile.save()
                patient_obj=Patient(
                    user_id=user_id,
                    first_name=profile.first_name,
                    last_name=profile.last_name,
                    age=profile.age,
                    weight=profile.weight,
                    height=profile.height,
                    insurance_company=profile.insurance_company,
                    insurance_id=profile.insurance_id,
                    preferred_hospital=profile.preferred_hospital,
                    current_hospital=None,
                    address=profile.address,
                    city=profile.city,
                    state=profile.state,
                    zipcode=profile.zipcode,
                    country=profile.country,
                    contact_number=profile.contact_number,
                    emergency_contact_number=profile.emergency_contact_number)
                patient_obj.save()
                Logger.log_system_activity(activity="has registered", username1=user.username, user_type1="patient")
                registered=True
                return redirect('/healthnet/index')
            else:
                print (new_user_form.errors,new_profile_form.errors)
        elif request.POST.get('back'):
            return redirect('/healthnet/index')
        else:
            return redirect('/healthnet/index')
    else:
        new_user_form=UserForm()
        new_profile_form=UserProfileForm()
    return render_to_response('healthnet/Registration.html',{'user_form':new_user_form,'profile_form':new_profile_form,'registered':registered},context)

def user_login(request):
    '''Vew to login  user and route to home page
    Author:Smruthi
    date: 30 Sep 2016
    this action is logged'''
    if request.POST.get('submit'):
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request, user)
                try:
                    user_type = UserProfile.objects.get(user=user).user_type
                except UserProfile.DoesNotExist:
                    Logger.log_system_activity(activity="has logged in", username1=username)
                    return redirect('/messages')

                Logger.log_system_activity(activity="has logged in", username1=username, user_type1=user_type)

                return HttpResponseRedirect('index')
            else:
                return HttpResponse('Your account is inactive')
        else:
            return redirect('/healthnet/login/invalid_login')
    elif request.POST.get('back'):
        return redirect('/healthnet/index/')
    else:
        return render(request,'healthnet/Login.html')

def create_prescription(request):
    """
    View to create a new prescription
    Only accessible to Doctors

    Author: Kyler Freas
    """

    context=RequestContext(request)
    new_prescription_form = CreatePrescriptionForm()

    if request.POST.get('create'):
        new_prescription_form=CreatePrescriptionForm(data=request.POST)

        if new_prescription_form.is_valid():
            new_prescription = new_prescription_form.save(commit=False)
            new_prescription.doctor = Doctor.objects.get(user_id=request.user.id)
            new_prescription.date_prescribed = datetime.datetime.now()
            new_prescription.hospital = Doctor.objects.get(user_id=request.user.id).hospital
            new_prescription.save()
            Logger.log_system_activity(activity="has created a prescription for", username1=new_prescription.doctor, username2=new_prescription.patient, user_type1="doctor", user_type2="patient")

            return HttpResponseRedirect('index')

    if request.user.userprofile.user_type == 'doctor':
        return render_to_response('healthnet/create_prescription.html',{'form': new_prescription_form, 'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}, context)
    else:
        return redirect('healthnet/appointments')

def remove_prescription(request):
    """
    Displays the page for removing prescriptions

    Author: Nick Deyette
    """
    context = RequestContext(request)
    select_patient_form = SelectPatientForm(data=request.POST or None)

    if request.POST.get('back_select_patient'):
        return HttpResponseRedirect('appointments')
    if request.POST.get('submit_select_patient'):
        if select_patient_form.is_valid():
            form_data = select_patient_form.cleaned_data
            patient = form_data.get('patient')

            prescription_list = Prescription.objects.filter(patient=patient)
            return render(request, 'healthnet/remove_prescription_choose_prescription.html', {'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type, 'prescription_list': prescription_list})
    if request.POST.get('back_select_prescription'):
        return redirect('/healthnet/remove_prescription')
    if request.POST.get('submit_select_prescription'):
        prescription_id = request.POST.get('prescription')
        prescription = Prescription.objects.get(pk=prescription_id)
        prescription_doctor = prescription.doctor
        prescription_patient = prescription.patient
        prescription.delete()
        Logger.log_system_activity(activity="has removed a prescription for", username1=prescription_doctor, username2=prescription_patient, user_type1="doctor", user_type2="patient")
        return redirect('/healthnet/appointments')

    return render_to_response('healthnet/remove_prescription.html', {'form': select_patient_form}, context)

def admit_patient(request):
    """
    View to admit a patient to a hospital
    Only accessible to Doctors and Nurses

    Author: Kyler Freas
    """

    if request.user.userprofile.user_type != 'patient':
        context=RequestContext(request)
        admit_form = AdmitPatientForm()

        if request.POST.get('admit'):
            admit_form=AdmitPatientForm(data=request.POST)

            if admit_form.is_valid():
                form_data = admit_form.cleaned_data

                patient = form_data.get('patient')
                hospital = form_data.get('hospital')
                reason = form_data.get('reason')

                patient.admit_patient(hospital)

                Logger.log_system_activity(activity="has admitted the following patient to " + hospital.name + " for " + reason + ": ",
                                           username1=request.user.username,
                                           username2=patient, user_type1=request.user.userprofile.user_type,
                                           user_type2="patient", hospital1=hospital)

                return HttpResponseRedirect('index')

        return render_to_response('healthnet/admit_patient.html', {'form': admit_form, 'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}, context)
    else:
        return redirect('/healthnet/appointments.html')

def discharge_patient(request):
    """
    View to discharge a patient from a hospital
    Only accessible to Doctors

    Author: Kyler Freas
    """

    if request.user.userprofile.user_type == 'doctor':
        context=RequestContext(request)

        hospital = Doctor.objects.get(user_id=request.user.id).hospital
        discharge_form = DischargePatientForm()
        discharge_form.fields['patient'].queryset = Patient.objects.filter(current_hospital=hospital)

        if request.POST.get('discharge'):
            discharge_form=DischargePatientForm(data=request.POST)

            if discharge_form.is_valid():
                form_data = discharge_form.cleaned_data

                patient = form_data.get('patient')
                hospital = patient.current_hospital

                patient.discharge_patient()

                Logger.log_system_activity(activity="has discharged the following patient from " + hospital.name + ": ",
                                           username1=request.user.username,
                                           username2=patient, user_type1="doctor",
                                           user_type2="patient", hospital1=hospital)

                return HttpResponseRedirect('index')

        return render_to_response('healthnet/discharge_patient.html', {'form': discharge_form, 'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}, context)
    else:
        return redirect('healthnet/appointments.html')

def select_patient_update(request):
    """
    View to allow nurses to select a patient to update their
    medical information.

    Author: Kyler Freas
    """

    if request.user.userprofile.user_type != "patient":
        context=RequestContext(request)
        patient_select_form = SelectPatientForm(request.POST or None)

        if request.POST.get('submit'):
            if patient_select_form.is_valid():
                form_data = patient_select_form.cleaned_data
                patient_id = form_data.get('patient').id

                return redirect('/healthnet/update_patient_medical/' + str(patient_id))

        return render_to_response('healthnet/select_patient_update.html', {'form': patient_select_form, 'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}, context)
    else:
        return redirect("/healthnet/index/")

def update_patient_medical(request, patient_id):
    """
    View to allow nurses to update patients' medical information
    Only accessible to nurses and doctors.

    Author: Kyler Freas
    """

    if request.user.userprofile.user_type != 'patient':
        context=RequestContext(request)
        instance = get_object_or_404(Patient, id=patient_id)
        update_form = UpdateMedicalForm(request.POST or None, instance=instance)

        if request.POST.get('update'):
            if update_form.is_valid():
                new_patient_data = update_form.save(commit=False)

                instance.update_patient_medical_info(new_patient_data.insurance_company, new_patient_data.insurance_id,
                                                     new_patient_data.age, new_patient_data.weight,
                                                     new_patient_data.height, new_patient_data.preferred_hospital)

                Logger.log_system_activity(activity="has updated the following patient's medical info: ",
                                           username1=request.user.username,
                                           username2=Patient.objects.get(pk=patient_id),
                                           user_type1=request.user.userprofile.user_type,
                                           user_type2="patient")

                return redirect('/healthnet/index/')
        elif request.POST.get('Add_Test_Results'):
            # testresults = TestResult.objects.get(patient=patient_id)
            context['patient']=patient_id
            return redirect('/healthnet/test_results/' + str(patient_id))

        prescription_list = Prescription.objects.filter(patient=instance)
        test_result_list = TestResult.objects.filter(patient=instance)

        return render_to_response('healthnet/update_patient_medical.html', {'form': update_form, 'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type, 'prescription_list': prescription_list, 'test_result_list': test_result_list, 'patient': instance}, context)
    else:
        return redirect('/healthnet/index/')

def release_test_result(request, test_result_id):
    """
    View that releases the test result
    that test_result_id corresponds to
    """
    test_result = TestResult.objects.get(pk=test_result_id)
    test_result.release()

    patient_id = test_result.patient.id

    return redirect('/healthnet/update_patient_medical/%d' % patient_id)

def getAttachment(request,testId):
   doc = TestResult.objects.get(id=testId)
   filename=str(doc.testfile)
   filename=filename.split('/')


   file = open( MEDIA_ROOT+ '/documents/' + filename[1],'rb')

   response = HttpResponse(file,content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
   response['Content-Disposition'] = 'attachment; filename="' + filename[1] + '"'

   return response


def view_test_results(request,patient_id):
    """
    View responsible for showing the test results
    for patient corresponding to patient_id
    """
    context = RequestContext(request)
    patient = Patient.objects.get(id=patient_id)
    # testresults=[]
    testresults=TestResult.objects.all()

    for object in testresults:
        if object.patient==patient:
            context['pk']=object.id
            context['testresults'] = testresults
            context['patient'] = patient
            print('released',object.released)




    if request.POST.get('View_Test_Results'):

        return redirect('/healthnet/view_test_results/' + str(patient_id))

    # if request.POST.get('Save'):
    #
    #
    #
    #     # results.release(id)
    #
    #
    #     return render_to_response('healthnet/view_test_results.html',
    #                               {'username': request.user.username, 'user_id': request.user.id,
    #                                'user_type': request.user.userprofile.user_type},
    #                               context)  # render_to_response('/healthnet/view_test_results/' + str(patient_id),context)

    if request.POST.get('Test_Results'):

        return redirect('/healthnet/test_results/' + str(patient_id))
    if request.POST.get('back'):

        return redirect('/healthnet/update_patient_medical/' + str(patient_id))
    return render_to_response('healthnet/view_test_results.html' ,{'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type},context)#render_to_response('/healthnet/view_test_results/' + str(patient_id),context)
def release_results(request,testId):
    """
    View responsible for releasing the rest result
    at testID
    """
    context=RequestContext(request)
    testResults=TestResult.objects.get(id=testId)
    testResults.release()
    print('patientid',testResults.patient.user_id)
    patient_id=testResults.patient.id

    return redirect('/healthnet/update_patient_medical/' + str(patient_id))


def upload_test_results(request,patient_id):
    '''
        Form for uploading test results files and adding comments
        Author: Smruthi Gadenkanahalli
        '''
    context = RequestContext(request)

    test_form=TestResultsForm(request.POST or None,request.FILES or None)

    # test_form.save()
    print(patient_id)
    patient=Patient.objects.get(id=patient_id)
    # testresults=(TestResult.objects.get(patient=patient))
    # testresults.append(TestResult.objects.get(patient=patient))#TestResult.objects.get(id=patient_id)
    context['patient_id']=patient_id
    # context['testresults']=testresults
    # print(testresults)
    if request.method=='POST':
        # print('saved')
        # print(new_test_data.comments)
        if test_form.is_valid():

            new_test_data=test_form.save(commit=False)
            testResults=TestResult(comments=new_test_data.comments,
            name=new_test_data.name,
            patient=patient,
            released=new_test_data.released,
            results=new_test_data.results,
            testfile=new_test_data.testfile)
            # test_form.save()
            print(new_test_data.testfile)

            testResults.save()
            print('saved')
            context['testresults']=testResults
            return redirect('/healthnet/update_patient_medical/'+patient_id)

    return render_to_response('healthnet/test_results.html',{'form':test_form, 'username': request.user.username, 'user_id': request.user.id, 'user_type': request.user.userprofile.user_type}, context)

def user_logout(request):
    '''View to logout and route to index page
    Author:Smruthi
    date: 30 Sep 2016
    this action is logged'''
    try:
        user_type = request.user.userprofile.user_type
    except UserProfile.DoesNotExist:
        return redirect('/healthnet/Login')

    username = request.user.username
    logout(request)
    Logger.log_system_activity(activity="has logged out", username1=username, user_type1=user_type)
    return HttpResponseRedirect('index.html')

def invalid_login(request):
    """
    Displays the page for an invalid login

    Author: Nick Deyette
    """
    if request.method == "POST":
        return redirect('/healthnet/Login')
    return render(request, 'healthnet/invalid_login.html')

def change_password(request, user_id):
    """
    Displays the page for changing a Patient's password.

    Authenticates that the password and username are correct.
    :param user_id: user id of the Patient attempting to change their password

    Author: Nick Deyette
    """
    if request.POST.get("back"):
        return redirect("/healthnet/index.html")

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user) # dont logout the user.
            messages.success(request, "Password changed.")
            return redirect("/healthnet/index.html")
    else:
        form = PasswordChangeForm(request.user)
    data = {
        'form': form
    }
    return render(request, "healthnet/change_password.html", data)

def invalid_password_change_1(request):
    """
    Displays the page for changing a password and the two new passwords
    do not match.

    Author: Nick Deyette
    """
    if request.POST.get('back'):
        user_id = request.user.id
        return redirect('/healthnet/change_password/%s' % user_id)
    return render(request, 'healthnet/invalid_password_change_1.html')

def invalid_password_change_2(request):
    """
    Displays the page for changing a password and the password
    is not correct.

    Author: Nick Deyette
    """
    if request.POST.get('back'):
        user_id = request.user.id
        return redirect('/healthnet/change_password/%s' % user_id)
    return render(request, 'healthnet/invalid_password_change_2.html')
