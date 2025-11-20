from django.contrib import admin
from mainpage.models.alumni import Alumni, graduateForm, Event, JobFair, Yearbook
class AlumniAdmin(admin.ModelAdmin):
    list_display = (
        "alumniID",
        "student_id",
        "firstname",
        "lastname",
        "degree",
        "alumniaddress",
    )

    def get_firstname(self, obj):
        return obj.student.fname

    get_firstname.short_description = "First Name"

    def get_lastname(self, obj):
        return obj.student.lname

    get_lastname.short_description = "Last Name"


class graduateFormAdmin(admin.ModelAdmin):
    list_display = (
        "dategraduated",
        "firstname",
        "lastname",
        "alumniaddress",
    )




class EventAdmin(admin.ModelAdmin):
    list_display = ("eventID", "eventsName", "eventsDate", "eventsLocation")


class JobFairAdmin(admin.ModelAdmin):
    list_display = (
        "jobfair_id",
        "jobtitle",
        "companyname",
        "joblocation",
        "employmenttype",
        "jobsalary",
    )


class YearbookAdmin(admin.ModelAdmin):
    list_display = (
        "yearbookID",
        "yearbookFirstname",
        "yearbookLastname",
        "yearbookGender",
        "yearbookAddress",
        "yearbookCourse",
        "yearbookYearGrad",
    )


admin.site.register(Yearbook, YearbookAdmin)
admin.site.register(JobFair, JobFairAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(graduateForm, graduateFormAdmin)
admin.site.register(Alumni, AlumniAdmin)

