
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
        fields = ['session', 'service_date', 'time_in', 'time_out', 'student_signature', 'remarks']
        widgets = {
            'session': forms.Select(attrs={'class': 'form-control'}),
            'service_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
         'time_in': forms.TimeInput(attrs={'type':'time','id':'id_time_in','step':900}),
    'time_out': forms.TimeInput(attrs={'type':'time','id':'id_time_out','step':900}),
            'student_signature': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
