from django import forms
from ..models import counseling_schedule, IndividualProfileBasicInfo, FileUploadTest, exit_interview_db, OjtAssessment
from datetime import date

class UploadFileForm(forms.Form):
    file = forms.FileField()



class CounselingSchedulerForm(forms.ModelForm):
    class Meta:
        model = counseling_schedule
        fields = ['reason', 'scheduled_date', 'scheduled_time', 'email']
        widgets = {
            'reason': forms.TextInput(attrs={
                'placeholder': 'Enter a reason for counseling'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address.'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat(),
                'placeholder': 'Select a date'
            }),
            'scheduled_time': forms.Select(attrs={'disabled': 'disabled'})
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



class IndividualProfileForm(forms.ModelForm):
    schoolTypeChoices = [
        (True,'Private'),
        (False,'Public'),
    ]
    yes_no =[
        (True,'Yes'),
        (False,'No'),
    ]
    elementaryType = forms.ChoiceField(choices=schoolTypeChoices, widget=forms.RadioSelect)
    seniorHighSchoolType = forms.ChoiceField(choices=schoolTypeChoices, widget=forms.RadioSelect)
    schoolLeaver = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect)
    fatherCTU = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect)
    motherCTU = forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect)
    doYouPlanToWork =forms.ChoiceField(choices=yes_no, widget=forms.RadioSelect)

    class Meta:
        model = IndividualProfileBasicInfo
        exclude = ['age','dateFilled','studentId','siblingsName','siblingsAge','siblingsSchoolWork','nameOfOrganization','inOutSchool','positionTitle','inclusiveYears','describeYouBest']
        widgets ={
            'dateOfBirth': forms.DateInput(attrs={'type':'date'}),
            'fatherDateOfBirth': forms.DateInput(attrs={'type':'date'}),
            'motherDateOfBirth': forms.DateInput(attrs={'type':'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        self.fields['nickName'].required = False
        self.fields['landlineNo'].required = False
        self.fields['fatherLandline'].required = False
        self.fields['motherLandLine'].required = False
        self.fields['personInCaseofEmergency'].required = False
        self.fields['disabilies'].required = False
        self.fields['allergies'].required = False
        self.fields['collegeName'].required = False
        self.fields['collegeAwardsRecieved'].required = False
        self.fields['collegeYearGraduated'].required = False
        self.fields['lastEducationAttainment'].required = False
        self.fields['specifyTheDecision'].required = False
        self.fields['describeYouBestOther'].required = False


class FileUpload(forms.ModelForm):
    class Meta:
        model = FileUploadTest
        fields = '__all__'
        widgets = {
            'file': forms.FileInput(attrs={'accept':'image/*'}),
        }