from django import forms
from django.contrib.auth.models import User
from healthnet.models import *
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django.utils.safestring import mark_safe

# Force DateTimeFields to have HTML5 calendar input
forms.DateTimeInput.input_type = "datetime-local"


class HorizontalRadioRenderer(forms.RadioSelect.renderer):
  def render(self):
    return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class UserForm(forms.ModelForm):
    '''Form for User model
    Author:Smruthi
    date: 30 Sep 2016'''

    error_css_class = 'error'

    password=forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

        CONTENT_HELP_TEXT = ' '.join(['<br>Username must be 30 characters or fewer. Letters, digits and @/./+/-/_ only.'])

        fieldsets = [
            ('Username', {
                'fields':('username',),
                'description': '<div class="helptext">%s</div>' % CONTENT_HELP_TEXT,
            }),
        ]

class UserProfileForm(ModelForm):
    '''Form for UserProfile model
        Author:Smruthi
        date: 30 Sep 2016'''

    error_css_class = 'error'

    class Meta:
        model = Patient
        fields=('first_name','last_name','age','height','weight','insurance_company','insurance_id',
                'preferred_hospital','address','city','state','zipcode','age','weight','height',
                'contact_number','emergency_contact_number')

        labels = {
            "height": _("Height (inches)"),
            "weight": _("Weight (pounds)"),
        }

class AdminCreateUserForm(forms.Form):
    """
    Form for admin to create a new user

    Author: Kyler Freas
    """

    error_css_class = 'error'

    CHOICES=[('nurse','Nurse'),
         ('doctor','Doctor'),
         ('administrator','Administrator')]

    user_type = forms.ChoiceField(choices=CHOICES, initial=0, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer))
    first_name = forms.CharField()
    last_name = forms.CharField()
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all())

class CreateAppointmentForm(forms.Form):
    """
    Form for creation of a new appointment

    Author: Kyler Freas
    """

    error_css_class = 'error'

    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())
    start = forms.DateTimeField()
    end = forms.DateTimeField()

class CreatePrescriptionForm(forms.ModelForm):
    """
    Form for doctor creation of prescriptions

    Author: Kyler Freas
    """

    error_css_class = 'error'

    class Meta:
        model = Prescription
        fields=('patient', 'medication', 'dosage')
        exclude = ['doctor']



class AdmitPatientForm(forms.Form):
    """
    Form for admitting a patient to a hospital

    Author: Kyler Freas
    """

    error_css_class = 'error'

    CHOICES = (
        ('Emergency', 'Emergency'),
        ('Observation', 'Observation'),
        ('Surgery', 'Surgery'),
        ('Other', 'Other'),
    )
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all())
    patient = forms.ModelChoiceField(queryset=Patient.objects.filter(current_hospital=None))
    reason = forms.ChoiceField(choices=CHOICES)

class DischargePatientForm(forms.Form):
    """
    Form for discharging a patient from a hospital

    Author: Kyler Freas
    """

    error_css_class = 'error'

    patient = forms.ModelChoiceField(queryset=Patient.objects.filter(~Q(current_hospital=None)))


class TransferPatientForm(forms.Form):
    """
    Form for transferring patient to another hospital

    Author: Kyler Freas
    """

    error_css_class = 'error'

    patient = forms.ModelChoiceField(queryset=Patient.objects.filter(~Q(current_hospital=None)))


class SelectPatientForm(forms.Form):
    """
    Simple form to select a patient

    Author: Kyler Freas
    """
    error_css_class = 'error'
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())

class UpdateMedicalForm(forms.ModelForm):
    """
    Form for updating patient medical information
    Only shows patient data associated with medical info

    Author: Kyler Freas
    """

    error_css_class = 'error'

    class Meta:
        model = Patient
        fields = ('insurance_company','insurance_id','age','weight','height','preferred_hospital')

        labels = {
            "height": _("Height (inches)"),
            "weight": _("Weight (pounds)"),
        }

class TestResultsForm(forms.ModelForm):
    '''
    Form for uploading test results files and adding comments
    Author: Smruthi Gadenkanahalli
    '''

    error_css_class = 'error'

    class Meta:
        model=TestResult
        fields=('comments','released','name','results','testfile')

        labels = {
            "testfile": _("File"),
        }


class SelectTimeframeForm(forms.Form):
    """
    Form to select a timeframe (start and end date)

    Author: Kyler Freas
    """

    start_date = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M'])
    end_date = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M'])