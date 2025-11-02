from django import forms
from ..models import staffInfo

class StaffForm(forms.ModelForm):
    class Meta:
        model = staffInfo
        fields = [
            "staffID",
            "lastname",
            "firstname",
            "middlename",
            "sex",
            "emailadd",
            "contact",
            "extension",
         
        ]
        widgets = {
            "sex": forms.Select(choices=[("Male", "Male"), ("Female", "Female")]),
        }
from ..models import Event  # Import your Event model

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'eventsName', 
            'eventsDate', 
            'eventsLocation', 
            'eventsDescription', 
            'eventsImage'
        ]
        
        # Add this widgets dictionary
        widgets = {
            'eventsDate': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }