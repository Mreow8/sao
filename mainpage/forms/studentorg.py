from django import forms
from ..models import Officer
from ..models import Project
from ..models import FinancialStatement
from ..models import Accreditation, Adviser

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['objective', 'activities', 'org', 'target', 'involved_officer', 'p_budget', 'expected_output', 'actual_accomplishment', 'remarks']

class FinancialStatementForm(forms.ModelForm):
    class Meta:
        model = FinancialStatement
        fields = ['date', 'purpose', 'source_of_funds', 'org', 'amount', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class OfficerForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = [
            'Officer_profile_picture', 'surname', 'firstname', 'middlename',
            'course', 'year', 'mobile_number', 'position', 'organization',
            'town_address', 'home_address', 'age', 'place_of_birth',
            'date_of_birth', 'nationality', 'civil_status', 'sex', 'height',
            'distinguishing_mark', 'weight', 'hobbies', 'special_talent',
            'father_name', 'father_occupation', 'father_address', 'father_mobile_number',
            'mother_name', 'mother_occupation', 'mother_address', 'mother_mobile_number',
            'guardian_name', 'guardian_occupation', 'guardian_address', 'guardian_mobile_number',
            'tertiary_institution', 'tertiary_address', 'tertiary_degree_level', 'tertiary_date',
            'secondary_institution', 'secondary_address', 'secondary_degree_level', 'secondary_date',
            'elementary_institution', 'elementary_address', 'elementary_degree_level', 'elementary_date',
            'membership_position1', 'membership_organization1', 'membership_date1',
            'membership_position2', 'membership_organization2', 'membership_date2',
            'membership_position3', 'membership_organization3', 'membership_date3',
            'membership_position4', 'membership_organization4', 'membership_date4',
            'membership_position5', 'membership_organization5', 'membership_date5',
            'seminar_title1', 'seminar_date1', 'seminar_title2', 'seminar_date2',
            'seminar_title3', 'seminar_date3', 'seminar_title4', 'seminar_date4',
            'seminar_title5', 'seminar_date5'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'tertiary_date': forms.DateInput(attrs={'type': 'date'}),
            'secondary_date': forms.DateInput(attrs={'type': 'date'}),
            'elementary_date': forms.DateInput(attrs={'type': 'date'}),
            'membership_date1': forms.DateInput(attrs={'type': 'date'}),
            'membership_date2': forms.DateInput(attrs={'type': 'date'}),
            'membership_date3': forms.DateInput(attrs={'type': 'date'}),
            'membership_date4': forms.DateInput(attrs={'type': 'date'}),
            'membership_date5': forms.DateInput(attrs={'type': 'date'}),
            'seminar_date1': forms.DateInput(attrs={'type': 'date'}),
            'seminar_date2': forms.DateInput(attrs={'type': 'date'}),
            'seminar_date3': forms.DateInput(attrs={'type': 'date'}),
            'seminar_date4': forms.DateInput(attrs={'type': 'date'}),
            'seminar_date5': forms.DateInput(attrs={'type': 'date'}),
        }

class AdviserForm(forms.ModelForm):
    class Meta:
        model = Adviser
        fields = [
            'Adviser_profile_picture', 'surname', 'firstname', 'middlename',
            'department','organization', 'date_employed', 'number_of_years',
            'town_address', 'home_address', 'cell1', 'cell2', 'position',
            'date_of_birth', 'place_of_birth', 'age', 'nationality', 'sex',
            'civil_status', 'height', 'weight', 'distinguishing_mark', 'hobbies', 'special_talent',
            'father_name', 'father_occupation', 'father_address', 'father_mobile_number',
            'mother_name', 'mother_occupation', 'mother_address', 'mother_mobile_number',
            'spouse_name', 'spouse_occupation', 'spouse_address', 'spouse_mobile_number',
            'first_institution', 'first_address', 'first_degree_level', 'first_date',
            'second_institution', 'second_address', 'second_degree_level', 'second_date',
            'third_institution', 'third_address', 'third_degree_level', 'third_date',
            'fourth_institution', 'fourth_address', 'fourth_degree_level', 'fourth_date',
            'fifth_institution', 'fifth_address', 'fifth_degree_level', 'fifth_date',
            'work_institution1', 'work_position1', 'work_period1',
            'work_institution2', 'work_position2', 'work_period2',
            'work_institution3', 'work_position3', 'work_period3',
            'work_institution4', 'work_position4', 'work_period4',
            'work_institution5', 'work_position5', 'work_period5',
            'org_name1', 'org_position1', 'org_period1',
            'org_name2', 'org_position2', 'org_period2',
            'advisory1', 'inclusive_advisory1',
            'advisory2', 'inclusive_advisory2',
            'advisory3', 'inclusive_advisory3'
        ]
        widgets = {
            'date_employed': forms.DateInput(attrs={'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'first_date': forms.DateInput(attrs={'type': 'date'}),
            'second_date': forms.DateInput(attrs={'type': 'date'}),
            'third_date': forms.DateInput(attrs={'type': 'date'}),
            'fourth_date': forms.DateInput(attrs={'type': 'date'}),
            'fifth_date': forms.DateInput(attrs={'type': 'date'}),
            'inclusive_advisory1': forms.DateInput(attrs={'type': 'date'}),
            'inclusive_advisory2': forms.DateInput(attrs={'type': 'date'}),
            'inclusive_advisory3': forms.DateInput(attrs={'type': 'date'}),
        }

class AccreditationForm(forms.ModelForm):
    class Meta:
        model = Accreditation
        fields = [
            'organization',
            'letter_of_intent',
            'list_of_officers',
            'certificate_of_registration',
            'list_of_members',
            'accomplishment_report',
            'calendar_of_activities',
            'financial_statement',
            'bank_passbook',
            'inventory_of_properties',
            'organization_bylaws',
            'faculty_adviser_appointment',
            'other_documents'
        ]

class AdminLoginForm(forms.Form):
    admin_username = forms.CharField(label="Username", max_length=50)
    admin_password = forms.CharField(label="Password", max_length=128, widget=forms.PasswordInput)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)