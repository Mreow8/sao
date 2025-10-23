from django import forms
from ..models import CrowdfundingProject,Program

class CrowdfundingProjectForm(forms.ModelForm):
    class Meta:
        model = CrowdfundingProject
        fields = ["title", "description", "active"]  # include only fields you want editable
from django import forms

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['title', 'caption', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }