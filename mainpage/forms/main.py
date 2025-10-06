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
