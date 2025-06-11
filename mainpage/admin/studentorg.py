from django.contrib import admin
from ..models import  Officer, Project, FinancialStatement, Accreditation, Adviser, AdminLogin, OfficerLogin

# Register your models here.
class OfficerAdmin(admin.ModelAdmin):
    list_display = ('surname','Officer_profile_picture','firstname','middlename','organization','course', 'year', 'status')

class AdviserAdmin(admin.ModelAdmin):
    list_display=('surname','Adviser_profile_picture', 'firstname', 'middlename', 'department', 'status')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_id', 'objective', 'org', 'target', 'involved_officer', 'p_budget', 'expected_output', 'actual_accomplishment', 'remarks', 'status']

class FinancialStatementAdmin(admin.ModelAdmin):
    list_display = ['financial_id', 'date', 'purpose', 'source_of_funds', 'org', 'amount', 'remarks', 'status']

class AccreditationAdmin(admin.ModelAdmin):
    list_display = ('accreditation_id', 'organization')

class LoginadminAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'admin_username', 'admin_password')

class OfficerLoginAdmin(admin.ModelAdmin):
    list_display=('student_id', 'student_lname', 'student_fname', 'student_mname', 'course','officer_position', 'year_lvl')

admin.site.register(OfficerLogin, OfficerLoginAdmin)
admin.site.register(AdminLogin, LoginadminAdmin)
admin.site.register(FinancialStatement, FinancialStatementAdmin)
admin.site.register(Adviser, AdviserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Officer, OfficerAdmin)
admin.site.register(Accreditation, AccreditationAdmin)



