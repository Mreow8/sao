# models.py
from django.db import models

class CaseProfile(models.Model):
    student_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20)
    course_year = models.CharField(max_length=50)
    date_of_incident = models.DateField()
    offense_type = models.CharField(max_length=100)
    description = models.TextField()
    action_taken = models.TextField()
    reported_by = models.CharField(max_length=100)
    witnesses = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student_name} - {self.offense_type}"

# ...existing code...
from ..models import studentInfo  # Add this import at the top

class CommunityService(models.Model):
    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    date = models.DateField()
    hours_rendered = models.DecimalField(max_digits=5, decimal_places=2)
    activity_description = models.TextField()

    def __str__(self):
        return f"{self.student} - {self.hours_rendered} hrs on {self.date}"
# ...existing code...