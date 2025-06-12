from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from ..models import studentInfo


class applicants(models.Model):
    studID = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    cor_file = models.FileField(upload_to='applicants/cor_pic/', blank=True, null=True)
    grade_file = models.FileField(upload_to='applicants/grade_pic/', blank=True, null=True)
    schoolid_file = models.FileField(upload_to='applicants/schoolid_pic/', blank=True, null=True)
    scholar_type = models.CharField(max_length=50)
    gpa = models.FloatField()
    note = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, default="PENDING")


class scholars(models.Model):
    scholar_ID = models.IntegerField(primary_key=True)
    studID = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    scholar_type = models.CharField(max_length=50)
    year = models.CharField(max_length=10, null=True)
    scholar_status = models.CharField(max_length=10, default="ACTIVE")

    def __str__(self):
        return f"{self.scholar_ID}"
    
class AdminRequest(models.Model):
    year = models.CharField(max_length=10)
    semester = models.CharField(max_length=50)
    requesting = models.BooleanField(default=False)

    class Meta:
        unique_together = ('year', 'semester')  # Ensure unique combination of year and semester

    def __str__(self):
        return f"{self.year} - {self.semester}"
    
    
class Requirement(models.Model):
    studID = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    scholar_ID = models.ForeignKey(scholars, on_delete=models.CASCADE)
    year = models.CharField(max_length=10, blank=True, null=True)
    semester = models.CharField(max_length=50, blank=True, null=True)
    scholar_type = models.CharField(max_length=50, blank=True, null=True)
    gpa = models.FloatField()
    cor_file = models.FileField(upload_to='scholar_requirements/cor_files/', blank=True, null=True)
    grade_file = models.FileField(upload_to='scholar_requirements/grade_files/', blank=True, null=True)
    schoolid_file = models.FileField(upload_to='scholar_requirements/schoolid_files/', blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    units = models.IntegerField(default=0)
    note = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, default="PENDING")
    record = models.CharField(max_length=10, default="NEW")
    

class SemesterDetails(models.Model):
    # SEMESTER_CHOICES = (
    #     ('1', '1st Semester'),
    #     ('2', '2nd Semester'),
    # )
    
    scholar_ID = models.ForeignKey(scholars, related_name='semester_details', on_delete=models.CASCADE)
    year = models.CharField(max_length=10, null=True)
    semester = models.CharField(max_length=50, blank=True, null=True) 
    amount = models.IntegerField(default=0)
    gpa = models.FloatField()
    scholar_status = models.CharField(max_length=10, default="ACTIVE")
    remarks = models.CharField(max_length=10, null=True, blank=True)
    date_added = models.DateField(default=timezone.now)
    total_units_enrolled = models.IntegerField(null=True)

    class Meta:
        unique_together = ('scholar_ID', 'year', 'semester')

    def __str__(self):
        return f"{self.scholar_ID} - {self.semester}" 


#  ------------ ADMIN COST LIQUIDATION SA COSCHO -----------------------------

class LiquidationCoScho(models.Model):
    dv_no = models.CharField(max_length=50, primary_key=True)
    dv_date = models.DateField()
    total_admin_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_stipend = models.DecimalField(max_digits=10, decimal_places=2)
    office_supplies = models.DecimalField(max_digits=10, decimal_places=2)
    communication = models.DecimalField(max_digits=10, decimal_places=2)
    traveling = models.DecimalField(max_digits=10, decimal_places=2)
    representation = models.DecimalField(max_digits=10, decimal_places=2)
    professional_services = models.DecimalField(max_digits=10, decimal_places=2)
    legal_services = models.DecimalField(max_digits=10, decimal_places=2)
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.dv_no


# class LiquidationTDP(models.Model):
#     SEMESTER_CHOICES = [
#         ('1', '1st Semester'),
#         ('2', '2nd Semester'),
#     ]

#     date = models.DateField()
#     check_number = models.CharField(max_length=50, primary_key=True)
#     particulars = models.CharField(max_length=255)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     disbursement_date = models.DateField(blank=True, null=True)
#     disbursement_number = models.CharField(max_length=50, blank=True, null=True)
#     disbursement_particulars = models.CharField(max_length=255, blank=True, null=True)
#     disbursement_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, null=True)
#     academic_year = models.CharField(max_length=9, null=True)  # Format: "YYYY-YYYY"
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     total_disbursement = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    
#     def __str__(self):
#         return f"{self.date} - {self.check_number}"
   
from django.db import models

class LiquidationTDP(models.Model):
    SEMESTER_CHOICES = [
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
    ]

    date = models.DateField()
    check_number = models.CharField(max_length=50, primary_key=True)
    particulars = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, null=True)
    academic_year = models.CharField(max_length=9, null=True)  # Format: "YYYY-YYYY"
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    liquidation_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_disbursement = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.date} - {self.check_number}"


class tdpDisbursement(models.Model):
    liquidation = models.ForeignKey(LiquidationTDP, related_name='tdpdisbursements', on_delete=models.CASCADE)
    disbursement_date = models.DateField(blank=True, null=True)
    disbursement_number = models.CharField(max_length=50, blank=True, null=True)
    disbursement_particulars = models.CharField(max_length=255, blank=True, null=True)
    disbursement_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.disbursement_number}"

    from django.db import models

class LiquidationTES(models.Model):
    SEMESTER_CHOICES = [
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
    ]

    date = models.DateField()
    check_number = models.CharField(max_length=50, primary_key=True)
    particulars = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, null=True)
    academic_year = models.CharField(max_length=9, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    liquidation_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_disbursement = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Format: "YYYY-YYYY"

    def __str__(self):
        return f"{self.date} - {self.check_number}"


class tesDisbursement(models.Model):
    liquidation = models.ForeignKey(LiquidationTES, related_name='disbursements', on_delete=models.CASCADE)
    disbursement_date = models.DateField(blank=True, null=True)
    disbursement_number = models.CharField(max_length=50, blank=True, null=True)
    disbursement_particulars = models.CharField(max_length=255, blank=True, null=True)
    disbursement_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.disbursement_number} "
