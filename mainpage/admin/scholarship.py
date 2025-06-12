from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ..models import (
    studentInfo, Requirement, scholars, applicants, SemesterDetails, 
    LiquidationCoScho, AdminRequest, LiquidationTDP, tdpDisbursement, 
    LiquidationTES, tesDisbursement
)

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'password_display')

    def password_display(self, obj):
        return "********"  # Masked password for display

    password_display.short_description = 'Password'
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ('studID', 'lastname', 'firstname', 'emailadd')
    search_fields = ('studID', 'lastname', 'firstname', 'emailadd')

admin.site.register(studentInfo, StudentInfoAdmin)

class RequirementAdmin(admin.ModelAdmin):
    list_display = ('scholar_ID', 'year', 'semester', 'gpa', 'submission_date', 'grade_file', 'cor_file', 'schoolid_file', 'status', 'record')

admin.site.register(Requirement, RequirementAdmin)

class SemesterDetailsInline(admin.TabularInline):
    model = SemesterDetails
    extra = 1
    
class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 1

class ScholarsAdmin(admin.ModelAdmin):
    list_display = ('scholar_ID', 'get_studID', 'get_first_name', 'get_last_name', 'scholar_type')
    raw_id_fields = ("studID",)
    search_fields = ('scholar_ID', 'studID__studID', 'studID__lastname', 'studID__firstname', 'scholar_type')
    list_filter = ('scholar_type',)

    inlines = [SemesterDetailsInline, RequirementInline]

    def get_studID(self, obj):
        return obj.studID.studID

    def get_first_name(self, obj):
        return obj.studID.firstname

    def get_last_name(self, obj):
        return obj.studID.lastname

    get_studID.short_description = 'Student ID'
    get_first_name.short_description = 'First Name'
    get_last_name.short_description = 'Last Name'

admin.site.register(scholars, ScholarsAdmin)

class ApplicantsAdmin(admin.ModelAdmin):
    list_display = ('get_studID', 'get_first_name', 'get_last_name', 'get_degree', 'cor_file', 'grade_file', 'schoolid_file', 'scholar_type', 'gpa', 'status', 'note')
    search_fields = ('studID__studID', 'studID__lastname', 'studID__firstname', 'scholar_type', 'status')
    list_filter = ('scholar_type', 'status')

    def get_studID(self, obj):
        return obj.studID.studID

    def get_first_name(self, obj):
        return obj.studID.firstname

    def get_last_name(self, obj):
        return obj.studID.lastname
    
    def get_degree(self, obj):
        return obj.studID.degree

    get_studID.short_description = 'Student ID'
    get_first_name.short_description = 'First Name'
    get_last_name.short_description = 'Last Name'
    get_degree.short_description = 'Degree'

admin.site.register(applicants, ApplicantsAdmin)

class SemesterDetailsAdmin(admin.ModelAdmin):
    list_display = ('scholar_ID', 'year', 'semester', 'amount', 'gpa', 'scholar_status', 'remarks', 'date_added', 'total_units_enrolled')
    search_fields = ('scholar_ID__scholar_ID', 'scholar_ID__studID__lastname', 'scholar_ID__studID__firstname', 'semester', 'year')
    list_filter = ('semester', 'scholar_status')

admin.site.register(SemesterDetails, SemesterDetailsAdmin)

class AdminRequestAdmin(admin.ModelAdmin):
    list_display = ('year', 'semester', 'requesting')

admin.site.register(AdminRequest, AdminRequestAdmin)

class LiquidationCoSchoAdmin(admin.ModelAdmin):
    list_display = (
        'dv_no', 'dv_date', 'total_admin_cost', 'total_stipend', 'balance'
    )
    search_fields = ('dv_no', 'dv_date')
    list_filter = ('dv_date',)

admin.site.register(LiquidationCoScho, LiquidationCoSchoAdmin)

class TdpDisbursementInline(admin.TabularInline):
    model = tdpDisbursement
    extra = 1

class LiquidationTDPAdmin(admin.ModelAdmin):
    list_display = ('check_number', 'date','amount', 'total_amount','liquidation_cost', 'total_disbursement', 'balance')
    inlines = [TdpDisbursementInline]

admin.site.register(LiquidationTDP, LiquidationTDPAdmin)

class TesDisbursementInline(admin.TabularInline):
    model = tesDisbursement
    extra = 1

class LiquidationTESAdmin(admin.ModelAdmin):
    list_display = ('check_number', 'date','amount', 'total_amount','liquidation_cost', 'total_disbursement', 'balance')
    inlines = [TesDisbursementInline]

admin.site.register(LiquidationTES, LiquidationTESAdmin)

# Register tdpDisbursement and tesDisbursement separately if needed
admin.site.register(tdpDisbursement)
admin.site.register(tesDisbursement)
