from django.contrib import admin
from ..models import (
    Organization, Officer, OfficerMembership, OfficerSeminar, 
    Adviser, Project, FinancialStatement, Accreditation,

)


# -------------------
# Organization Admin
# -------------------
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'logo_preview')
    search_fields = ('name', 'slug')
    readonly_fields = ('slug', 'logo_preview')

    def logo_preview(self, obj):
        if obj.logo:
            return f'<img src="{obj.logo.url}" width="80" height="80" style="object-fit: contain;" />'
        return "No image"
    logo_preview.allow_tags = True
    logo_preview.short_description = 'Logo'


# -------------------
# Officer Admin
# -------------------
@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = (
        'surname', 'firstname', 'middlename',
        'organization', 'course', 'year', 'status'
    )
    search_fields = ('surname', 'firstname', 'middlename')
    list_filter = ('organization', 'course', 'year', 'status')


@admin.register(OfficerMembership)
class OfficerMembershipAdmin(admin.ModelAdmin):
    list_display = ('officer', 'position', 'organization', 'date')
    search_fields = ('organization', 'position')
    list_filter = ('organization',)


@admin.register(OfficerSeminar)
class OfficerSeminarAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'officer')
    search_fields = ('title',)
    list_filter = ('date',)



# -------------------
# Adviser Admin
# -------------------
@admin.register(Adviser)
class AdviserAdmin(admin.ModelAdmin):
    list_display = (
        'surname', 'firstname', 'middlename',
        'department', 'organization', 'status'
    )
    search_fields = ('surname', 'firstname', 'middlename')
    list_filter = ('department', 'organization', 'status')
    @admin.display(boolean=True, description='Currently Active?')
    def is_active_display(self, obj):
        return obj.is_active

# -------------------
# Project Admin
# -------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'project_id', 'objective', 'org',
        'target', 'involved_officer',
        'p_budget', 'status'
    )
    search_fields = ('objective', 'org__name')
    list_filter = ('status', 'target', 'org')


# -------------------
# Financial Statement Admin
# -------------------
@admin.register(FinancialStatement)
class FinancialStatementAdmin(admin.ModelAdmin):
    list_display = ('financial_id', 'date', 'purpose', 'org', 'amount', 'status')
    search_fields = ('purpose',)
    list_filter = ('org', 'status')


# -------------------
# Accreditation Admin
# -------------------
@admin.register(Accreditation)
class AccreditationAdmin(admin.ModelAdmin):
    list_display = ('accreditation_id', 'organization', 'status')
    list_filter = ('organization', 'status')


# -------------------
# Logins Admin
# -------------------
# @admin.register(OfficerLogin)
# class OfficerLoginAdmin(admin.ModelAdmin):
#     list_display = (
#         'student_id', 'student_lname', 'student_fname',
#         'course', 'officer_position', 'organization', 'year_lvl'
#     )
#     search_fields = ('student_lname', 'student_fname', 'username')
#     list_filter = ('course', 'organization', 'year_lvl')


# @admin.register(AdminLogin)
# class AdminLoginAdmin(admin.ModelAdmin):
#     list_display = ('admin_id', 'admin_username')
#     search_fields = ('admin_username',)
