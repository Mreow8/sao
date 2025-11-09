from django import forms
from ..models import Officer
from ..models import Project
from ..models import FinancialStatement
from ..models import Accreditation, Adviser, Organization, OrganizationCBL
# forms.py

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [ 'logo', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
           
        }
class OrganizationCBLForm(forms.ModelForm):
  class Meta:
    model = OrganizationCBL
    fields = ['cbl_file']
    labels = {
        'cbl_file': 'Upload New CBL (PDF, DOCX, etc.)'
    }
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['objective', 'activities', 'org', 'target', 'involved_officer', 'p_budget', 'expected_output', 'actual_accomplishment', 'remarks']

class FinancialStatementForm(forms.ModelForm):
    class Meta:
        model = FinancialStatement
        fields = ['date', 'purpose', 'source_of_funds', 'amount', 'remarks']  # 👈 removed 'org'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

from django import forms
from ..models.studentorg import Officer, OfficerMembership, OfficerSeminar
from django import forms
from django.core.exceptions import ValidationError
class OfficerForm(forms.ModelForm):

    # 1. This is the search box the admin will see
    student_search = forms.CharField(
        label="Search Student by ID",
        required=False, # Not required itself
        widget=forms.TextInput(attrs={
            "id": "id_student_search",  # <-- The ID our script looks for
            "placeholder": "Start typing student ID..."
        })
    )

    # 2. Your mobile number validation (this is correct)
    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get("mobile_number")
        if mobile_number:
            if not mobile_number.isdigit():
                raise ValidationError("Mobile number must contain only digits.")
            if len(mobile_number) != 11:
                raise ValidationError("Mobile number must be exactly 11 digits.")
        return mobile_number


    class Meta:
        model = Officer
        fields = [
            # --- FIELDS YOU MUST ADD ---
            "student_search",
            "student",      # This fixes the NOT NULL error
            "firstname",    # For autofill
            "surname",      # For autofill
            "course",
            "profile_picture",
            # --- Your existing fields ---
            "sex",
            "date_of_birth",
            "age",
            "civil_status",
            "nationality",
            "mobile_number", 
            "position",
            "year",
            "home_address",
            'academic_year',  # <-- ADDED
            'is_active',
        ]
        
        # 3. Set up widgets for autofill and your existing ones
        widgets = {
            # --- WIDGETS YOU MUST ADD ---
            "student": forms.HiddenInput(attrs={"id": "id_student"}),
            "firstname": forms.TextInput(attrs={"readonly": "readonly"}),
            "surname": forms.TextInput(attrs={"readonly": "readonly"}),
            "course": forms.TextInput(attrs={"readonly": "readonly"}),

            # --- Your existing widgets ---
            "date_of_birth": forms.DateInput(attrs={"type": "date", "id": "id_date_of_birth"}),
            "age": forms.NumberInput(attrs={"id": "id_age", "readonly": "readonly"}),
            "sex": forms.Select(),
            "civil_status": forms.Select(),
            # --- ADD THESE WIDGETS ---
            'academic_year': forms.TextInput(
                attrs={'placeholder': 'e.g., 2024-2025'}
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
          # Added readonly/disabled for autofill
        }

    # 4. Re-order the fields to put the search box on top
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define the order
        new_order = ['student_search', 'student', 'firstname', 'surname', 'year']
        
        # Add all other fields
        for field in self.fields:
            if field not in new_order:
                new_order.append(field)
                
        self.order_fields(new_order)
# Officer Membership Form
class OfficerMembershipForm(forms.ModelForm):
    class Meta:
        model = OfficerMembership
        fields = [
            "position",
            "organization",
            "date",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

# Officer Seminar Form
class OfficerSeminarForm(forms.ModelForm):
    class Meta:
        model = OfficerSeminar
        fields = [
           
            "title",
            "date",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

# Officer Info Log Form

from django import forms
from ..models import Adviser, AdviserEducation, AdviserWorkExperience, AdviserOrganization, AdviserAdvisory


class AdviserForm(forms.ModelForm):
    class Meta:
        model = Adviser
        fields = [
            'profile_picture',
            'surname',
            'firstname',
            'middlename',
            'department',
            'organization',
            'position',
            'date_of_birth',
            'place_of_birth',
            'sex',
            'civil_status',
            'nationality',
            'town_address',
            'home_address',
            'cell_number',
            'status',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
class AdviserEducationForm(forms.ModelForm):
    class Meta:
        model = AdviserEducation
        fields = [
            'institution',
            'address',
            'degree_level',
            'year_graduated',
        ]


class AdviserWorkExperienceForm(forms.ModelForm):
    class Meta:
        model = AdviserWorkExperience
        fields = [
            'institution',
            'position',
            'work_period',
        ]


class AdviserOrganizationForm(forms.ModelForm):
    class Meta:
        model = AdviserOrganization
        fields = [
            'org_name',
            'org_position',
            'org_period',
        ]


class AdviserAdvisoryForm(forms.ModelForm):
    class Meta:
        model = AdviserAdvisory
        fields = [
            'advisory_name',
            'inclusive_period',
        ]


from django import forms
from ..models import Accreditation,AccreditationOfficer, AccreditationMember


class AccreditationForm(forms.ModelForm):
    class Meta:
        model = Accreditation
        fields = ['organization', 'status']  # ✅ only real fields in Accreditation
from django import forms
from ..models import Accreditation

class AccreditationForm(forms.ModelForm):
    class Meta:
        model = Accreditation
        fields = [
            "organization",
            "letter_of_intent",
            "list_of_officers",
            "certificate_of_registration",
            "list_of_members",
            "accomplishment_report",
            "calendar_of_activities",
            "financial_statement",
            "bank_passbook",
            "inventory_of_properties",
            "organization_bylaws",
            "faculty_adviser_appointment",
            "other_documents",
        ]
        widgets = {
            "organization": forms.Select(attrs={"class": "form-control"}),
        }

class AccreditationOfficerForm(forms.ModelForm):
    class Meta:
        model = AccreditationOfficer
        fields = ['officer_name', 'officer_position']


class AccreditationMemberForm(forms.ModelForm):
    class Meta:
        model = AccreditationMember
        fields = ['member_name']

# class AdminLoginForm(forms.Form):
#     admin_username = forms.CharField(label="Username", max_length=50)
#     admin_password = forms.CharField(label="Password", max_length=128, widget=forms.PasswordInput)

# class LoginForm(forms.Form):
#     username = forms.CharField(max_length=100, required=True)
#     password = forms.CharField(widget=forms.PasswordInput, required=True)