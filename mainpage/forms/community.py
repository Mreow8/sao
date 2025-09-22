from django import forms
from ..models import CrowdfundingProject

class CrowdfundingProjectForm(forms.ModelForm):
    class Meta:
        model = CrowdfundingProject
        fields = ["title", "description", "active"]  # include only fields you want editable
