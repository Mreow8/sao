# models.py
from django.db import models
from datetime import date
from ..models import studentInfo
from datetime import datetime

class CaseProfile(models.Model):
    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)

    OFFENSE_CHOICES = [
        ('Bullying', 'Bullying'),
        ('Cheating', 'Cheating'),
  
        ('Others', 'Others'),
    ]

    ACTION_CHOICES = [
        ('Community Service', 'Community Service'),
        ('Suspension', 'Suspension'),
        ('Counseling', 'Counseling'),
        ('Others', 'Others'),
    ]

    offense_type = models.CharField(max_length=50, choices=OFFENSE_CHOICES)
    custom_offense = models.CharField(max_length=255, blank=True, null=True)

    action_taken = models.CharField(max_length=50, choices=ACTION_CHOICES)
    community_service_hours = models.IntegerField(blank=True, null=True)
    suspension_duration = models.CharField(max_length=50, blank=True, null=True)
    custom_action = models.CharField(max_length=255, blank=True, null=True)

    date_reported = models.DateField(default=date.today)    


    def __str__(self):
        return f"{self.student} - {self.offense_type}"


# ...existing code...
# from ..models import studentInfo  # Add this import at the top

class CommunityService(models.Model):
    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    date = models.DateField()
    hours_rendered = models.DecimalField(max_digits=5, decimal_places=2)
    activity_description = models.TextField()

    def __str__(self):
        return f"{self.student} - {self.hours_rendered} hrs on {self.date}"
# models.pyfrom datetime import datetime, date
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.db import models

# ...existing code...
class CommunityServiceTracker(models.Model):
    SESSION_CHOICES = [
    ('morning', 'Morning'),
    ('afternoon', 'Afternoon'),
]

    session = models.CharField(max_length=10, choices=SESSION_CHOICES)
    case = models.ForeignKey('CaseProfile', on_delete=models.CASCADE)
    service_date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField()
    student_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    remarks = models.TextField(blank=True)


    class Meta:
        unique_together = ('case', 'service_date', 'session')  # <-- allow morning & afternoon separately

    def total_hours_decimal(self):
        delta = datetime.combine(date.min, self.time_out) - datetime.combine(date.min, self.time_in)
        return delta.total_seconds() / 3600
    def clean(self):
        if not getattr(self, 'case_id', None):
            return
        if CommunityServiceTracker.objects.filter(
            case_id=self.case_id,
            service_date=self.service_date,
            session=self.session  # <-- include session
        ).exclude(pk=self.pk).exists():
            raise ValidationError({'service_date': f"A log for {self.session} session on {self.service_date} already exists for this case."})


    def save(self, *args, **kwargs):
        self.full_clean()  # enforce validation before saving
        super().save(*args, **kwargs)

    def time_rendered(self):
        delta = datetime.combine(self.service_date, self.time_out) - datetime.combine(self.service_date, self.time_in)
        total_minutes = delta.total_seconds() / 60
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        return f"{hours} hours {minutes} minutes"

    def __str__(self):
        student = getattr(self.case, 'student', None)
        return f"{student} - {self.service_date}"


# class CommunityServiceTracker(models.Model):
#     student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
#     service_date = models.DateField()
#     time_in = models.TimeField()
#     time_out = models.TimeField()
#     # time_rendered = models.IntegerField()
#     student_signature = models.CharField(max_length=100)
    
#     remarks = models.CharField(max_length=100, null=True, blank=True)

#     def time_rendered(self):
#         delta = datetime.combine(self.service_date, self.time_out) - datetime.combine(self.service_date, self.time_in)
#         total_minutes = delta.total_seconds() / 60
#         hours = int(total_minutes // 60)
#         minutes = int(total_minutes % 60)
#         return f'{hours} hours {minutes} minutes'                             
    
#     def total_time_rendered(self):
#         delta = datetime.combine(datetime.today(), self.time_out) - datetime.combine(datetime.today(), self.time_in)
#         total_minutes = delta.total_seconds() / 60
#         hours = int(total_minutes // 60)
#         minutes = int(total_minutes % 60)
#         return hours, minutes
class DisciplinarySanction(models.Model):
    SANCTION_CHOICES = [
        ('apology_letter', 'Apology Letter'),
        ('community_service', 'Community Service'),
        ('suspension', 'Suspension'),
        ('apology_letter_community_service', 'Apology Letter and Community Service'),
        ('expulsion', 'Expulsion'),
    ]

    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    sanction = models.CharField(max_length=50, choices=SANCTION_CHOICES)
    sanction_completed = models.BooleanField(default=False)
    apology_letter = models.FileField(upload_to='apology_letters/', null=True, blank=True)
    community_service_hours = models.IntegerField(null=True, blank=True)
    community_service_deadline = models.DateField(null=True, blank=True)
    suspension_start_date = models.DateField(null=True, blank=True)
    suspension_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.sanction}"

    def save(self, *args, **kwargs):
        if self.suspension_end_date and self.suspension_end_date < date.today():
            self.sanction_completed = True
        super().save(*args, **kwargs)
