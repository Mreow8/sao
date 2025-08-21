
from django import forms
from ..models import CaseProfile
# mainpage/forms.py
from django import forms
from ..models import CustomUser,studentInfo

class RoleAssignForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role']
from django import forms
from ..models import CaseProfile

class CaseProfileForm(forms.ModelForm):
    class Meta:
        model = CaseProfile
        fields = '__all__'
        widgets = {
            'student': forms.TextInput(attrs={
                'list': 'student-options',
                'placeholder': 'Enter Student ID',
            }),
            'date_reported': forms.DateInput(attrs={
                'type': 'date',
                'class': 'border border-gray-300 rounded-md px-3 py-2 shadow-sm',
            }),
        }

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
