from django.contrib import admin

from .models import *

# Registering all of the models to the admin page for easy management.
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(Patient)
admin.site.register(Administrator)
admin.site.register(UserProfile)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(TestResult)
admin.site.register(LogItem)
admin.site.register(Logger)
admin.site.register(Hospital)
