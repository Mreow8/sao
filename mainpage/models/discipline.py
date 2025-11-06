# models.py
from django.db import models
from datetime import date
from ..models import studentInfo
from datetime import datetime

# models.py
from django.db import models
from datetime import date
from ..models import studentInfo
from datetime import datetime

from django.db import models
from datetime import date

# Assuming studentInfo is imported/defined elsewhere, e.g.:
# from .models import studentInfo 

class CaseProfile(models.Model):
    # Link to the student record
    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)

    # --- OFFENSE CHOICES (Based on CTU Manual Content) ---
    OFFENSE_CHOICES = [
        ('Bullying', 'Bullying/Harassment'),
        ('Cheating', 'Academic Dishonesty (Cheating/Plagiarism)'),
        ('Uniform/ID Violation', 'Uniform/ID Violation'),
        ('Class Disruption', 'Class or Academic Activity Disruption'),
        ('Drug/Alcohol Use', 'Drug or Alcohol Possession/Use'),
        ('Theft/Vandalism', 'Theft or Vandalism'),
        ('Immorality/Lewdness', 'Immorality or Lewd Acts'),
        ('Deadly Weapon', 'Possession of Deadly Weapon'),
        ('Hazing', 'Hazing or Initiation Rites'),
        ('Falsification', 'Falsification of Documents'),
        ('Unauthorized Use', 'Unauthorized Activity/Collection'),
        ('Others', 'Other Offense'),
    ]

    # --- ACTION CHOICES (Based on CTU Manual Penalties) ---
    ACTION_CHOICES = [
        ('Oral Reprimand', 'Oral Reprimand'),
        ('Written Reprimand', 'Written Reprimand'),
        ('Community Service', 'Community Service'),
        ('Suspension', 'Suspension'),
        ('Expulsion', 'Expulsion'),
        ('Counseling', 'Counseling/Intervention'),
        ('Others', 'Other Action/Penalty'),
    ]

    # --- OFFENSE NUMBER ---
    OFFENSE_NUMBER_CHOICES = [
        ('1st', '1st Offense'),
        ('2nd', '2nd Offense'),
        ('3rd', '3rd Offense'),
        ('4th', '4th Offense'),
        ('5th', '5th Offense'),
        ('Subsequent', 'Subsequent Offense (Beyond 5th)'),
    ]
    
    offense_number = models.CharField(
        max_length=10, 
        choices=OFFENSE_NUMBER_CHOICES, 
        default='1st',
        verbose_name='Offense Number'
    )
    
    # Offense Details
    offense_type = models.CharField(
        max_length=50, 
        choices=OFFENSE_CHOICES,
        verbose_name='Offense Type'
    )
    custom_offense = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name='Specify Custom Offense'
    )
    description = models.TextField(
        verbose_name='Description of Incident',
        blank=True,
        null=True,   # <-- allow NULL so migration can add column safely
    )
    # Action/Penalty Details
    action_taken = models.CharField(
        max_length=50, 
        choices=ACTION_CHOICES,
        verbose_name='Action Taken'
    )
    community_service_hours = models.IntegerField(
        blank=True, 
        null=True,
        verbose_name='Community Service Hours'
    )
    suspension_duration = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Suspension Duration (e.g., "5 days")'
    )
    custom_action = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name='Specify Custom Action'
    )

    # Reporting and Status Fields (Added for completeness)
    date_reported = models.DateField(
        default=date.today,
        verbose_name='Date Reported'
    )
    reported_by = models.CharField(
        max_length=100, 
        verbose_name='Reported By (User ID/Name)', blank=True,
        null=True,
    )
    
    STATUS_CHOICES = [
        ('Pending', 'Pending Review'),
        ('Under Investigation', 'Under Investigation'),
        ('Resolved', 'Resolved/Closed'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending',
        verbose_name='Case Status'
    )

    # Evidence (File Upload)
    evidence = models.FileField(
        upload_to='discipline_evidence/', 
        blank=True, 
        null=True,
        verbose_name='Supporting Evidence (Attachment)'
    )

    class Meta:
        verbose_name = "Case Profile"
        verbose_name_plural = "Case Profiles"
        ordering = ['-date_reported']

    def __str__(self):
        return f"{self.student.firstname} {self.student.lastname} - {self.offense_number} {self.get_offense_type_display()}"
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
    def get_duration(self):
        """Calculates the duration in hours and minutes."""
        if not self.time_in or not self.time_out:
            return 0, 0
        
        try:
            # Combine with a dummy date to create datetime objects
            today = date.today()
            datetime_in = datetime.combine(today, self.time_in)
            datetime_out = datetime.combine(today, self.time_out)
            
            # Handle overnight or invalid times
            if datetime_out <= datetime_in:
                return 0, 0
                
            delta = datetime_out - datetime_in
            total_minutes = delta.total_seconds() / 60
            hours = int(total_minutes // 60)
            minutes = int(total_minutes % 60)
            return hours, minutes
        except Exception:
            # Catch any errors (e.g., invalid time format)
            return 0, 0

    def get_duration_str(self):
       
        hours, minutes = self.get_duration()
        return f"{hours}h {minutes}m"

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
