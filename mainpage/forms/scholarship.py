from django import forms
from ..models import Requirement, applicants, AdminRequest

class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = ['studID', 'semester', 'gpa', 'grade_file', 'cor_file', 'schoolid_file', 'units']
        
class applicantsForm(forms.ModelForm):
    class Meta:
        model = applicants
        fields = ['studID', 'cor_file', 'grade_file', 'schoolid_file', 'scholar_type', 'gpa']
        
class AdminRequestForm(forms.ModelForm):
    class Meta:
        model = AdminRequest
        fields = ['year', 'semester']

# from django import forms
# from .models import Accounts
# from django.contrib.auth.hashers import make_password

# class RegistrationForm(forms.ModelForm):
#     student_id = forms.IntegerField(label="Student ID")
#     cpassword = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

#     class Meta:
#         model = Accounts
#         fields = ['student_id', 'personal_emailadd', 'password']
#         widgets = {
#             'password': forms.PasswordInput(),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         cpassword = cleaned_data.get("cpassword")
#         if password != cpassword:
#             self.add_error('cpassword', "Passwords do not match")

#     def save(self, commit=True):
#         account = super(RegistrationForm, self).save(commit=False)
#         account.password = make_password(self.cleaned_data['password'])  # Hash the password
#         if commit:
#             account.save()
#         return account


# class LoginForm(forms.Form):
#     email = forms.EmailField(label="Email")
#     password = forms.CharField(widget=forms.PasswordInput(), label="Password")



