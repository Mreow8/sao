
from django import forms
from ..models import CaseProfile
# mainpage/forms.py
from django import forms
from ..models import CustomUser,studentInfo

class RoleAssignForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role']

class CaseProfileForm(forms.ModelForm):
    class Meta:
        model = CaseProfile
        fields = '__all__'
        widgets = {
            'student': forms.TextInput(attrs={
                'list': 'student-options',
                'placeholder': 'Enter Student ID or Name',
            }),
            'date_of_incident': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_student(self):
        studID = self.cleaned_data['student']
        try:
            return studentInfo.objects.get(studID=studID)
        except studentInfo.DoesNotExist:
            raise forms.ValidationError("Student not found.")

        # forms.py
from django import forms
from ..models import CommunityServiceTracker



class CommunityServiceForm(forms.ModelForm):
    class Meta:
        model = CommunityServiceTracker
        fields = ['date', 'morning_in', 'morning_out', 'afternoon_in', 'afternoon_out']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),

            'morning_in': forms.TimeInput(
                attrs={'type': 'time', 'min': '06:00', 'max': '11:59'}
            ),
            'morning_out': forms.TimeInput(
                attrs={'type': 'time', 'min': '06:00', 'max': '11:59'}
            ),
            'afternoon_in': forms.TimeInput(
                attrs={'type': 'time', 'min': '12:00', 'max': '17:59'}
            ),
            'afternoon_out': forms.TimeInput(
                attrs={'type': 'time', 'min': '12:00', 'max': '17:59'}
            ),
        }
