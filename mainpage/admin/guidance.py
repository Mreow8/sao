from django.contrib import admin
from ..models import IndividualProfileBasicInfo, TestArray,FileUploadTest, counseling_schedule, studentInfo, exit_interview_db, OjtAssessment, IntakeInverView

class IndividualProfileBasicInfoAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.get_fields()]
        super().__init__(model, admin_site)
class IntakeInverViewAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.get_fields()]
        super().__init__(model, admin_site)

admin.site.register(IndividualProfileBasicInfo)
admin.site.register(IntakeInverView)

class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ('studID', 'lrn', 'lastname', 'firstname', 'middlename', 'degree', 'yearlvl', 'sex', 'emailadd', 'contact')
    # Optionally, you can add search_fields, list_filter, etc. to enhance the admin interface
    search_fields = ('lastname', 'firstname', 'lrn', 'degree')
    list_filter = ('degree', 'yearlvl', 'sex')
class counselingSceduleAdmin(admin.ModelAdmin):
    list_display = ('counselingID','dateRecieved','studentID','reason','scheduled_date','scheduled_time','email','status')
    list_editable = ('dateRecieved','reason','scheduled_date','scheduled_time','email','status')

class OjtAssessmentAdmin(admin.ModelAdmin):
    list_display = ['OjtRequestID','studentID','dateRecieved','schoolYear','status','dateAccepted']
    list_editable = ['schoolYear','status','dateAccepted']

class exitInterviewAdmine(admin.ModelAdmin):
    list_display = (
        'exitinterviewId',
        'studentID',
        'dateRecieved',
        'date',
        'dateEnrolled',
        'reasonForLeaving',
        'satisfiedWithAcadamic',
        'feedbackWithAcademic',
        'satisfiedWithSocial',
        'feedbackWithSocial',
        'satisfiedWithServices',
        'feedbackWithServices',
        'contributedToDecision',
        'intendedMajor',
        'firstConsider',
        'whatCondition',
        'recommend',
        'howSatisfied',
        'planTOReturn',
        'accademicExperienceSatisfied',
        'knowAboutYourTime',
        'currentlyEmployed',
        'explainationEmployed',
        'status',
        'scheduled_date',
        'scheduled_time',
        'emailadd'
    )
    list_editable = (
        'date',
        'dateEnrolled',
        'reasonForLeaving',
        'satisfiedWithAcadamic',
        'feedbackWithAcademic',
        'satisfiedWithSocial',
        'feedbackWithSocial',
        'satisfiedWithServices',
        'feedbackWithServices',
        'intendedMajor',
        'firstConsider',
        'whatCondition',
        'recommend',
        'howSatisfied',
        'planTOReturn',
        'accademicExperienceSatisfied',
        'knowAboutYourTime',
        'currentlyEmployed',
        'explainationEmployed',
        'status',
        'scheduled_date',
        'scheduled_time',
        'emailadd'
    )



admin.site.register(studentInfo, StudentInfoAdmin)
admin.site.register(counseling_schedule, counselingSceduleAdmin)
admin.site.register(exit_interview_db, exitInterviewAdmine)
admin.site.register(OjtAssessment,OjtAssessmentAdmin)