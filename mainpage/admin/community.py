from django.contrib import admin
from ..models import Program, ProgramImage

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("programid", "title", "caption", "date_time", "archive")
    list_filter = ("archive", "date_time")
    search_fields = ("title", "caption", "description")
    ordering = ("-date_time",)
@admin.register(ProgramImage)
class ProgramImageAdmin(admin.ModelAdmin):
    list_display = ("program", "image", "uploaded_at")
    list_filter = ("uploaded_at",)
from ..models import CrowdfundingProject, DonationChannel


class DonationChannelInline(admin.TabularInline):  # or StackedInline
    model = DonationChannel
    extra = 1  # how many empty forms to display


@admin.register(CrowdfundingProject)
class CrowdfundingProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "active", "created_at", "date_time")
    list_filter = ("active", "created_at")
    search_fields = ("title", "description")
    inlines = [DonationChannelInline]


@admin.register(DonationChannel)
class DonationChannelAdmin(admin.ModelAdmin):
    list_display = ("project", "imageCrowdfunding")
    list_filter = ("project",)
