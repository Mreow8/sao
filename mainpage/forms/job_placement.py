from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from ..models import ( JobPlacementAdminUser, StudentUser, Seminar,
                     SeminarAttendance, TransactionReport, OJTCompany, OJTStudent, OJTRequirements
                    )
from django.forms import ModelForm

from django import forms
from django.contrib.auth import authenticate
from django.utils.safestring import mark_safe

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': 'email'},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
    
class StatusTextWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        status_text = dict(OJTRequirements.STATUS_CHOICES).get(value, '')
        return mark_safe(f'<p class="file_status">{status_text}</p>')

class StatusWidget(forms.ModelForm):
    class Meta:
        model = OJTRequirements
        fields = [ 'nondis_stat', 'biodata_stat', 'consent_stat', 
                  'apl_letter_stat' ,'medical_stat', 'moa_stat', 'endorsement_stat',
                  'cert_stat']
        widgets = {
            'nondis_stat': StatusTextWidget(),
            'biodata_stat': StatusTextWidget(),
            'consent_stat': StatusTextWidget(),
            'apl_letter_stat': StatusTextWidget(),
            'medical_stat': StatusTextWidget(),
            'moa_stat': StatusTextWidget(),
            'endorsement_stat': StatusTextWidget(),
            'cert_stat': StatusTextWidget(),
        }

    # CREATION FORMS
class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = JobPlacementAdminUser
        fields = ("email",'firstname', 'lastname', 'middlename')

class AdminUserChangeForm(UserChangeForm):
    class Meta:
        model = JobPlacementAdminUser
        fields = ("email", 'firstname', 'lastname', 'middlename')

# class StudentUserChangeForm(UserChangeForm):
#     class Meta:
#         model=StudentUser
#         fields = ('email', 'firstname', 'lastname', 'middlename')

class AdminSignUpForm(UserCreationForm):
    class Meta:
        model = JobPlacementAdminUser
        fields = ('email', 'firstname', 'lastname', 'password1', 'password2')

# class StudentSignUpForm(UserCreationForm):
#     class Meta:
#         model = StudentUser
#         fields = (
#             'email', 'password1', 'password2', 'studID', 'lrn',
#             'firstname', 'lastname', 'middlename', 'yearlvl', 'sex', 'contact'
#         )

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data["password1"])
    #     if commit:
    #         user.save()
    #     return user    
    
    # LOGIN FORMS
class AdminLoginForm(AuthenticationForm):
    pass

# class StudentLoginForm(AuthenticationForm):
#     pass

class SeminarForm(ModelForm):
    class Meta:
        model = Seminar
        exclude = ('seminar_id',)

class SeminarAttendanceForm(ModelForm):
    class Meta:
        model = SeminarAttendance
        exclude = ('sem_at_id',)

class TransactionForm(ModelForm):
    class Meta:
        model = TransactionReport
        exclude = ('report_id','transactor', 'date_created', 'date_updated' )

class AdminTransactionForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        exclude = ('report_id',)

class OjtHiringForm(ModelForm):
    class Meta:
        model = OJTCompany
        exclude = ('ojt_id',)

class OJTStudentForm(ModelForm):
    class Meta:
        model = OJTStudent
        exclude = ('ojt_id', 'date_started')

class OJTRequirementsForm(ModelForm):
    class Meta:
        model = OJTRequirements
        fields = ('ojt_requirement_id','non_disclosure', 'biodata',
                  'parents_consent', 'application_letter', 'medical', 'moa',
                  'endorsement', 'certification',
                  )
        
class ScrapperFile(forms.Form):
    file = forms.FileField()
   