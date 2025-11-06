from django import forms
from ..models import counseling_schedule, IndividualProfileBasicInfo, FileUploadTest, exit_interview_db, OjtAssessment
from datetime import date
from django.core.validators import RegexValidator
class UploadFileForm(forms.Form):
    file = forms.FileField()


class CounselingSchedulerForm(forms.ModelForm):

    # By defining the field here, we can set 'required' and 'error_messages'
    # without needing an __init__ method.
    email = forms.EmailField(
        required=True,  # Makes the field mandatory
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address.'
        }),
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email format (e.g., user@example.com).'
        }
    )

    class Meta:
        model = counseling_schedule
        fields = ['reason', 'scheduled_date', 'scheduled_time', 'email']
        widgets = {
            'reason': forms.TextInput(attrs={
                'placeholder': 'Enter a reason for counseling'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat(),
                'placeholder': 'Select a date'
            }),
           'scheduled_time': forms.Select()
           # No 'email' widget needed here, as it's defined above
        }
class OjtAssessmentForm(forms.ModelForm):
    class Meta:
        model = OjtAssessment
        fields = ['schoolYear', 'emailadd']
        widgets ={
            'emailadd': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address.'
            }),
        }

class ExitInterviewForm(forms.ModelForm):
    yes_no =[
        (True,'Yes'),
        (False,'No'),
    ]
    satisfiedWithAcadamic = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect(attrs={'class': 'yes_no'}))
    satisfiedWithSocial = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect(attrs={'class': 'yes_no'}))
    satisfiedWithServices = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect(attrs={'class': 'yes_no'}))
    recommend =forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect(attrs={'class': 'yes_no'}))
    accademicExperienceSatisfied =forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect(attrs={'class': 'yes_no'}))
    currentlyEmployed =forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect(attrs={'class': 'yes_no'}))
    class Meta:
        model = exit_interview_db
        exclude = ['exitinterviewId','studentID','date','contributedToDecision', 'dateRecieved','status']
        widgets ={
            'dateEnrolled': forms.DateInput(attrs={'type':'date'}),
            'reasonForLeaving': forms.Textarea(),
            'feedbackWithAcademic': forms.Textarea(),
            'feedbackWithSocial': forms.Textarea(),
            'feedbackWithServices': forms.Textarea(),
            'firstConsider': forms.Textarea(),
            'whatCondition': forms.Textarea(),
            'planTOReturn': forms.Textarea(),
            'knowAboutYourTime': forms.Textarea(),
            'explainationEmployed': forms.Textarea(),
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat(),
                'placeholder': 'Select a date'
            }),
            'scheduled_time': forms.Select(attrs={'disabled': 'disabled'}),
            'emailadd': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address.'
            }),
            'intendedMajor': forms.TextInput(attrs={
                'placeholder': 'Enter your intended major.',
                'class': 'table_input hidden'
            }),
            'majorEvent': forms.TextInput(attrs={
                'placeholder': 'Enter your reason.',
                'class': 'table_input hidden'
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feedbackWithAcademic'].required = False
        self.fields['feedbackWithSocial'].required = False
        self.fields['feedbackWithServices'].required = False
        self.fields['knowAboutYourTime'].required = False
        self.fields['whatCondition'].required = False
        self.fields['planTOReturn'].required = False
        self.fields['intendedMajor'].required = False
        self.fields['majorEvent'].required = False


from datetime import date
from django import forms
from ..models import counseling_schedule, IndividualProfileBasicInfo, FileUploadTest, exit_interview_db, OjtAssessment
from datetime import date
from django.core.validators import RegexValidator

# ... (Other forms are unchanged) ...

class IndividualProfileForm(forms.ModelForm):
    schoolTypeChoices = [
        (True,'Private'),
        (False,'Public'),
    ]
    yes_no =[
        (True,'Yes'),
        (False,'No'),
    ]
    
    elementaryType = forms.ChoiceField(choices=schoolTypeChoices, widget=forms.RadioSelect, required=True)
    seniorHighSchoolType = forms.ChoiceField(choices=schoolTypeChoices, widget=forms.RadioSelect, required=True)
    schoolLeaver = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect, required=True)
    fatherCTU = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect, required=True)
    motherCTU = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect, required=True)
    doYouPlanToWork = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect, required=True)

    class Meta:
        model = IndividualProfileBasicInfo
        exclude = [
            'age','dateFilled','studentId','siblingsName','siblingsAge','siblingsSchoolWork',
            'nameOfOrganization','inOutSchool','positionTitle','inclusiveYears','describeYouBest'
        ]
        widgets = {
            'dateOfBirth': forms.DateInput(attrs={'type':'date'}),
            'fatherDateOfBirth': forms.DateInput(attrs={'type':'date'}),
            'motherDateOfBirth': forms.DateInput(attrs={'type':'date'}),
            
            # --- FINAL PHONE WIDGETS ---
            'mobileNo': forms.TextInput(attrs={
                'type': 'text',
                'inputmode': 'tel',        # Brings up numeric keypad on mobile
                'pattern': '^(09)\\d{9}$', # HTML5 validation
                'title': 'Enter 11 digits (e.g., 09171234567).',
                'placeholder': '09171234567',
                'maxlength': '11'          # Hard limit
            }),
            'fatherMobilePhone': forms.TextInput(attrs={
                'type': 'text',
                'inputmode': 'tel',
                'pattern': '^(09)\\d{9}$',
                'title': 'Enter 11 digits (e.g., 09171234567).',
                'placeholder': '09171234567',
                'maxlength': '11'
            }),
            'motherMobilePhone': forms.TextInput(attrs={
                'type': 'text',
                'inputmode': 'tel',
                'pattern': '^(09)\\d{9}$',
                'title': 'Enter 11 digits (e.g., 09171234567).',
                'placeholder': '09171234567',
                'maxlength': '11'
            }),
            'personInCaseofEmergencyMobileNo': forms.TextInput(attrs={
                'type': 'text',
                'inputmode': 'tel',
                'pattern': '^(09)\\d{9}$',
                'title': 'Enter 11 digits (e.g., 09171234567).',
                'placeholder': '09171234567',
                'maxlength': '11'
            }),
            
            # --- Other fields (onkeydown removed) ---
            'landlineNo': forms.TextInput(attrs={
                'type': 'number',
            }),
            'fatherLandline': forms.TextInput(attrs={
                'type': 'number',
            }),
            'motherLandLine': forms.TextInput(attrs={
                'type': 'number',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'example@email.com'
            }),
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ... (Birthday validation rule is unchanged) ...
        today = date.today()
        max_date = today.replace(year=today.year - 10)
        min_date = date(1900, 1, 1)

        self.fields['dateOfBirth'].widget.attrs.update({
            'max': max_date.strftime('%Y-%m-%d'),
            'min': min_date.strftime('%Y-%m-%d'),
        })

        # ... (required=False fields are unchanged) ...
        self.fields['personInCaseofEmergencyLandline'].required = False
        self.fields['curriculumtype'].required = False
        self.fields['fatherMobilePhone'].required = False 
        self.fields['motherMobilePhone'].required = False 
        self.fields['fatherEducationLevel'].required = False
        self.fields['motherEducationLevel'].required = False
        self.fields['track'].required = False
        self.fields['livingSpecify'].required = False
        self.fields['placeOfLivingOthers'].required = False
        self.fields['sourceOfIncomeSpecify'].required = False
        self.fields['fatherOtherOccupation'].required = False
        self.fields['motherOtherOccupation'].required = False
        self.fields['typeOfScholarship'].required = False
        self.fields['specifyScholarship'].required = False
        self.fields['schoolLeaverWhy'].required = False
        self.fields['specifyIfNo'].required = False
        self.fields['landlineNo'].required = False
        self.fields['fatherLandline'].required = False
        self.fields['motherLandLine'].required = False
        self.fields['disabilies'].required = False
        self.fields['allergies'].required = False
        self.fields['collegeName'].required = False
        self.fields['collegeAwardsRecieved'].required = False
        self.fields['collegeYearGraduated'].required = False
        self.fields['lastEducationAttainment'].required = False
        self.fields['specifyTheDecision'].required = False
        self.fields['describeYouBestOther'].required = False

        # --- RegexValidator (unchanged) ---
        phone_regex = RegexValidator(
            regex=r'^(09)\d{9}$', 
            message="Enter a valid 11-digit mobile number (e.g., 09171234567)."
        )
        
        self.fields['mobileNo'].validators.append(phone_regex)
        self.fields['fatherMobilePhone'].validators.append(phone_regex)
        self.fields['motherMobilePhone'].validators.append(phone_regex)
        self.fields['personInCaseofEmergencyMobileNo'].validators.append(phone_regex)

# ... (FileUpload form is unchanged) ...
class FileUpload(forms.ModelForm):
    class Meta:
        model = FileUploadTest
        fields = '__all__'
        widgets = {
            'file': forms.FileInput(attrs={'accept':'image/*'}),
        }