
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
from django import forms

from datetime import date

# Note: Assuming studentInfo model is accessible for ForeignKey, 
# and the actual student lookup/assignment is handled in the view.

class CaseProfileForm(forms.ModelForm):
    # This field is used in your template for the Datalist/AJAX student ID lookup.
    # We include it here for form rendering, even though the ModelForm won't save it directly.
    # The view must use this input's value to set the 'student' ForeignKey.
    # For the edit modal, this field should ideally be read-only (or hidden) 
    # since the student link shouldn't change.
    student_id_input = forms.CharField(
        label='Student ID',
        max_length=20,
        required=False, # Set to False for the edit form if student is already linked
        help_text='Student ID (Read-only for existing cases)',
        initial='', # Will be populated in the view for edit
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    # These fields are included in the form to carry data when 'Others' or a 
    # specific action is selected, but they are hidden/shown via JavaScript.
    custom_offense = forms.CharField(label='Specify Offense', max_length=255, required=False)
    community_service_hours = forms.IntegerField(label='Hours', required=False)
    suspension_duration = forms.CharField(label='Duration', max_length=50, required=False)
    custom_action = forms.CharField(label='Specify Action', max_length=255, required=False)

    class Meta:
        model = CaseProfile
        fields = [
            'student',
            'student_id_input', # Include the custom field in the display order
            'date_reported',
            'offense_number',
            'offense_type',
            'custom_offense', # Included for data capture
            'description',
            'reported_by',
            'action_taken',
            'community_service_hours', # Included for data capture
            'suspension_duration',     # Included for data capture
            'custom_action',           # Included for data capture
            'status',
            'evidence',
        ]
        
        widgets = {
            # The actual ForeignKey to student must be hidden; the user interacts with student_id_input
            'student': forms.HiddenInput(), 
            
            # Use appropriate HTML5 widgets
            'date_reported': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            
            # This field should be read-only since it's set by the system/user
            'reported_by': forms.TextInput(attrs={'readonly': 'readonly'}), 

            # Set placeholders for clarity
            'community_service_hours': forms.NumberInput(attrs={'placeholder': 'Number of Hours'}),
            'suspension_duration': forms.TextInput(attrs={'placeholder': 'e.g., 5 days or 1 semester'}),
        }
        
        # Override default labels for form clarity
        labels = {
            'reported_by': 'Reported By',
            'evidence': 'Attachment (optional)',
        }

from django import forms
from ..models import CommunityServiceTracker



class CommunityServiceForm(forms.ModelForm):
    class Meta:
        model = CommunityServiceTracker
        fields = ['session', 'service_date', 'time_in', 'time_out',  'remarks']
        widgets = {
            'session': forms.Select(attrs={'class': 'form-control'}),
            'service_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
         'time_in': forms.TimeInput(attrs={'type':'time','id':'id_time_in','step':900}),
    'time_out': forms.TimeInput(attrs={'type':'time','id':'id_time_out','step':900}),
           
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
