
from django import forms
from ..models import CaseProfile
from ..models import CommunityService

class CommunityServiceForm(forms.ModelForm):
    class Meta:
        model = CommunityService
        fields = ['student', 'date', 'hours_rendered', 'activity_description']
class CaseProfileForm(forms.ModelForm):
    class Meta:
        model = CaseProfile
        fields = '__all__'