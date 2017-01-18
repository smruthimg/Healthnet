from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # 127.0.0.1/healthnet/index
    url(r'^index', views.index, name='index'),
    # 127.0.0.1/healthnet/index
    url(r'^doctor_index', views.doctor_index, name='doctor_index'),
    # 127.0.0.1/healthnet/doctor_index
    url(r'^nurse_index', views.nurse_index, name='nurse_index'),
    # 127.0.0.1/healthnet/nurse_index
    url(r'^appointments/', views.appointments, name='appointments'),
    # 127.0.0.1/healthnet/appointments/
    url(r'^create_appointment/$', views.create_appointment, name='create_appointment'),
    # 127.0.0.1/healthnet/create_appointment/
    url(r'^create_appointment_errors', views.create_appointment_errors, name="create_appointment_errors"),
    # 127.0.0.1/healthnet/create_appointment_errors
    url(r'^view_appointment/(?P<appointment_id>[0-9]+)/$', views.view_appointment, name='view_appointment'),
    # 127.0.0.1/healthnet/view_appointment/1/
    url(r'^update_appointment/(?P<appointment_id>[0-9]+)/$', views.update_appointment, name='update_appointment'),
    # 127.0.0.1/healthnet/update_appointment/1/
    url(r'^hospital_admin_index/', views.hospital_admin_index, name="hospital_admin_index"),
    # 127.0.0.1/healthnet/hospital_admin_index/
    url(r'^hospital_admin/create_user', views.hospital_admin_create_user, name="hospital_admin/create_user/"),
    # 127.0.0.1/healthnet/hospital_admin/create_user/
    url(r'^hospital_admin/view_logs/', views.hospital_admin_view_logs, name="hospital_admin/view_logs/"),
    # 127.0.0.1/healthnet/hospital_admin/view_logs/
    url(r'^edit_profile_information/(?P<user_id>[0-9]+)/$', views.edit_profile_information, name="edit_profile_information"),
    # 127.0.0.1/healthnet/edit_profile_information/1/
    url(r'^edit_profile_information_edit', views.edit_profile_information_edit, name="edit_profile_information_edit"),
    # 127.0.0.1/healthnet/edit_profile_information_edit
    url(r'^Appointment', views.Appointment, name='Appointment'),
    # 127.0.0.1/healthnet/Appointment
    url(r'^register', views.register, name='register'),
    # 127.0.0.1/healthnet/register
    url(r'^Login', views.user_login, name='Login'),
    # 127.0.0.1/healthnet/Login
    url(r'^Logout', views.user_logout, name='Logout'),
    # 127.0.0.1/healthnet/Logout
    url(r'^hospital_admin_create_user_success', views.hospital_admin_create_user_success, name="hospital_admin_create_user_success"),
    # 127.0.0.1/healthnet/hospital_admin_create_user_success
    url(r'^login/invalid_login', views.invalid_login, name="invalid_login"),
    # 127.0.0.1/healthnet/login/invalid_login
    url(r'^delete_appointment/(?P<appointment_id>[0-9]+)/$', views.delete_appointment, name="delete_appointment"),
    # 127.0.0.1/healthnet/delete_appointment/1
    url(r'^change_password/(?P<user_id>[0-9]+)/$', views.change_password, name="change_password"),
    # 127.0.0.1/healthnet/change_password/1
    url(r'^invalid_password_change_1', views.invalid_password_change_1, name="invalid_password_change_1"),
    # 127.0.0.1/healthnet/invalid_password_change_1
    url(r'^invalid_password_change_2', views.invalid_password_change_2, name="invalid_password_change_2"),
    # 127.0.0.1/healthnet/invalid_password_change_2
    url(r'^hospital_admin_create_user_failure', views.hospital_admin_create_user_failure, name="hospital_admin_create_user_failure"),
    # 127.0.0.1/healthnet/hospital_admin_create_user_failure
    url(r'^edit_profile_information_failure', views.edit_profile_information_failure, name="edit_profile_information_failure"),
    # 127.0.0.1/healthnet/edit_profile_information_failure
    url(r'^hospital_admin_view_logs_create_filters', views.hospital_admin_view_logs_create_filters, name="hospital_admin_view_logs_create_filters"),
    # 127.0.0.1/healthnet/hospital_admin_view_logs_create_filters
    url(r'^hospital_admin_view_logs_choose_filters', views.hospital_admin_view_logs_create_filters, name="hospital_admin_view_logs_choose_filters"),
    # 127.0.0.1/healthnet/hospital_admin_view_logs_choose_filters
    url(r'create_prescription', views.create_prescription, name="create_prescription"),
    # 127.0.0.1/healthnet/create_prescription
    url(r'remove_prescription', views.remove_prescription, name="remove_prescription"),
    # 127.0.0.1/healthnet/remove_prescription
    url(r'admit_patient', views.admit_patient, name="admit_patient"),
    # 127.0.0.1/healthnet/admit_patient
    url(r'discharge_patient', views.discharge_patient, name="discharge_patient"),
    # 127.0.0.1/healthnet/discharge_patient
    url(r'select_patient_update', views.select_patient_update, name='select_patient_update'),
    # 127.0.0.1/healthnet/select_patient_update
    url(r'^update_patient_medical/(?P<patient_id>[0-9]+)/$', views.update_patient_medical, name='update_patient_medical'),
    # 127.0.0.1/healthnet/update_patient_medical/1
    url(r'^hospital_admin_view_logs_number_filters', views.hospital_admin_view_logs_create_filters, name="hospital_admin_view_logs_number_filters"),
    # 127.0.0.1/healthnet/hospital_admin_view_logs_number_filters
    url(r'^edit_profile_information_export_info', views.edit_profile_information_export_info, name="edit_profile_information_export_info"),
    # 127.0.0.1/healtahnet/edit_profile_information_export_info
    url(r'^edit_profile_information_export_info_download', views.edit_profile_information_export_info, name="edit_profile_information_export_info_download"),
    # 127.0.0.1/healthnet/edit_profile_information_export_info_download
    url(r'^hospital_admin_view_system_statistics', views.hospital_admin_view_system_statistics, name="hospital_admin_view_system_statistics"),
    # 127.0.0.1/healthnet/hospital_admin_view_system_statistics
    url(r'^hospital_admin_view_prescription_statistics', views.hospital_admin_view_prescription_statistics, name="hospital_admin_view_prescription_statistics"),
    # 127.0.0.1/healthnet/hospital_admin_view_prescription_statistics
    url(r'^test_results/(?P<patient_id>[0-9]+)/$',views.upload_test_results,name="test_results"),
    # 127.0.0.1/healthnet/test_results
    url(r'^view_test_results/(?P<patient_id>[0-9]+)/$', views.view_test_results, name="view_test_results"),
    url(r'^release_results/(?P<testId>[0-9]+)/$', views.release_results, name="release_results"),
    url(r'^(?P<testId>[0-9]+)/getAttachment/$', views.getAttachment, name='getAttachment'),
    # 127.0.0.1/healthnet/view_test_results
    url(r'^transfer_patient', views.transfer_patient, name="transfer_patient"),
    # 127.0.0.1/healthnet/transfer_patient
]
