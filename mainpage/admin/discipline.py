from django.contrib import admin
from ..models.discipline import (
    CaseProfile,
    CommunityService,
    CommunityServiceTracker,
    DisciplinarySanction,
)

@admin.register(CaseProfile)
class CaseProfileAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_year', 'date_of_incident', 'offense_type', 'status')
    search_fields = ('student__firstname', 'student__lastname', 'offense_type', 'status')
    list_filter = ('status', 'course_year', 'date_of_incident')

@admin.register(CommunityService)
class CommunityServiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'hours_rendered', 'activity_description')
    search_fields = ('student__firstname', 'student__lastname', 'activity_description')
from django.contrib import admin
from ..models import CommunityServiceTracker

@admin.register(CommunityServiceTracker)
class CommunityServiceTrackerAdmin(admin.ModelAdmin):
    list_display = ('case', 'date', 'morning_in', 'morning_out', 'afternoon_in', 'afternoon_out', 'total_hours')
    list_filter = ('date', 'case')
    search_fields = ('case__id', 'case__name')  # adjust if CaseProfile has a name field


@admin.register(DisciplinarySanction)
class DisciplinarySanctionAdmin(admin.ModelAdmin):
    list_display = ('student', 'sanction', 'sanction_completed', 'community_service_hours', 'suspension_start_date', 'suspension_end_date')
    search_fields = ('student__firstname', 'student__lastname', 'sanction')
    list_filter = ('sanction', 'sanction_completed')