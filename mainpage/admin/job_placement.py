from django.contrib import admin
from ..models import ( JobPlacementAdminUser, StudentUser, SeminarAttendance,
                        Seminar, TransactionReport, OJTCompany, OJTStudent,
                        OJTRequirements
                     )
from ..forms import ( AdminTransactionForm, AdminUserCreationForm, SeminarForm,
                    AdminUserChangeForm, OjtHiringForm, OJTStudentForm, OJTRequirementsForm,
                    )
# Register your models here.

class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'user', 'action', 'date_created', 'user_type']
    form = AdminTransactionForm

class AdminChange(admin.ModelAdmin):
    list_display = ['email', 'firstname', 'lastname', 'middlename']
    form = AdminUserChangeForm

class AdminSeminar(admin.ModelAdmin):
    list_display = ['seminar_id', 'title', 'theme', 'date_of_event']
    model = SeminarForm

# class AdminStudent(admin.ModelAdmin):
#     list_display = ['studID', 'lrn', 'emailadd', 'firstname', 'lastname', 'middlename', 'yearlvl', 'sex', 'contact']
#     model = StudentUser

class AdminSemAttendance(admin.ModelAdmin):
    list_display = ['sem_at_id', 'student_id', 'seminar_id', 'attended', 'ispending']
    model = SeminarAttendance

class AdminOjt(admin.ModelAdmin):
    list_display = ['company_id', 'owner', 'company_name', 'address', 'description', 'company_contact', 'number_of_slots', 'shift']
    form = OjtHiringForm

class AdminOJTStudent(admin.ModelAdmin):
    list_display = ['ojt_id', 'studID', 'date_started', 'company_id', 'duration']
    model = OJTStudent

class AdminRequirements(admin.ModelAdmin):
    list_display = ['student_id', 'nondis_stat', 'biodata_stat', 'consent_stat',
                    'apl_letter_stat', 'medical_stat', 'moa_stat', 
                    'endorsement_stat', 'cert_stat'
                    ]

admin.site.register(JobPlacementAdminUser, AdminChange)
# admin.site.register(StudentUser, AdminStudent)
admin.site.register(Seminar, AdminSeminar)
admin.site.register(SeminarAttendance, AdminSemAttendance)
admin.site.register(OJTCompany, AdminOjt)
admin.site.register(OJTStudent, AdminOJTStudent)
admin.site.register(TransactionReport, ReportAdmin)
admin.site.register(OJTRequirements, AdminRequirements)