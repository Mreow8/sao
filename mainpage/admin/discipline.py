from django.contrib import admin
from ..models.discipline import (
    CaseProfile,
    CommunityService,
    CommunityServiceTracker,
    DisciplinarySanction,
)

@admin.register(CaseProfile)
class CaseProfileAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_yearlvl', 'date_reported', 'offense_type', 'action_taken')
    search_fields = ('student__firstname', 'student__lastname', 'offense_type')
    list_filter = ('offense_type', 'action_taken', 'date_reported', 'student__yearlvl')

    def get_yearlvl(self, obj):
        return obj.student.yearlvl
    get_yearlvl.short_description = 'Year Level'

    def get_status(self, obj):
        # If you have no status field yet, just return something placeholder
        return "Pending"  
    get_status.short_description = 'Status'

@admin.register(CommunityService)
class CommunityServiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'hours_rendered', 'activity_description')
    search_fields = ('student__firstname', 'student__lastname', 'activity_description')
from django.contrib import admin
from ..models import CommunityServiceTracker

@admin.register(CommunityServiceTracker)
class CommunityServiceTrackerAdmin(admin.ModelAdmin):
    list_display = [
        'case', 'service_date', 'time_in', 'time_out', 'remarks', 'total_hours_decimal'
    ]
    list_filter = ['service_date', 'case']

@admin.register(DisciplinarySanction)
class DisciplinarySanctionAdmin(admin.ModelAdmin):
    list_display = ('student', 'sanction', 'sanction_completed', 'community_service_hours', 'suspension_start_date', 'suspension_end_date')
    search_fields = ('student__firstname', 'student__lastname', 'sanction')
    list_filter = ('sanction', 'sanction_completed')