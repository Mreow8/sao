import os
from django import forms
from django.db import models
from django.template.defaultfilters import truncatechars
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission, Group

from .managers import AdminUserManager, StudentUserManager
from studentLife_system.models import studentInfo as StudentUser
# Create your models here.
 
class JobPlacementAdminUser(AbstractBaseUser, PermissionsMixin):
    admin_id = models.AutoField(primary_key=True)
    email = models.EmailField(_("email address"), unique = True)
    firstname = models.CharField(max_length=50, blank=False, null=False, default="")
    lastname = models.CharField(max_length=50, blank=False, null=False, default="")
    middlename = models.CharField(max_length=50, null=True, blank=True, default="")
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
 
    objects = AdminUserManager()

    def __str__(self):
        return self.email
    
        #define reverse accessor for GROUP
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        related_name="admin_user_groups"  # Specify a related_name to resolve the clash
    )
        #define reverse accessor for Permission
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        related_name="admin_user_permissions"  # Specify a related_name to resolve the clash
    )

# open ojt from companies
class OJTCompany(models.Model):
    DAY = "Day Shift"
    NIGHT = "Night Shift"

    shift_options = [
        (DAY, 'Day Shift'),
        (NIGHT, 'Night Shift'),
    ]

    company_id = models.AutoField(primary_key = True)   
    company_name = models.CharField(max_length=225, null=False, blank=False, default="")
    owner = models.CharField(max_length=100, null=False, blank=False, default="")
    position = models.CharField(max_length=100, null=False, blank=False, default="")
    address = models.CharField(max_length=100, null=False, blank=False, default="")
    description = models.TextField(null=False, blank=True)
    company_contact = models.CharField(max_length=50, null=True)
    number_of_slots = models.PositiveIntegerField(null=False, blank=False, default=1)
    shift = models.CharField(max_length=12, choices=shift_options, default=DAY)
    

    def __str__(self):
        return self.company_name
    
class OJTStudent(models.Model):
    ojt_id = models.AutoField(primary_key=True)
    studID = models.OneToOneField(StudentUser, on_delete=models.PROTECT, unique=True)
    company_id = models.ForeignKey(OJTCompany, on_delete=models.PROTECT)
    date_started = models.DateField(auto_now=True)
    duration = models.PositiveIntegerField(null=False, blank=False, default=100)
    def __str__(self):
        return f"{self.ojt_id}"
    
    class Meta:
        ordering = ['date_started']

class OJTRequirements(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    DECLINED = 'Declined'
    NOFILE = 'No file'
    STATUS_CHOICES = [
            (PENDING, 'Pending'),
            (ACCEPTED, 'Accepted'),
            (DECLINED, 'Declined'),
            (NOFILE, 'No file')
    ]

    ojt_requirement_id = models.AutoField(primary_key=True)
    company_id = models.ForeignKey(OJTCompany, on_delete=models.CASCADE, null=True, blank=True, default="")
    student_id = models.ForeignKey(StudentUser, on_delete=models.CASCADE) # Change to Students Model
    non_disclosure = models.FileField(blank=True, upload_to='upload/ojt_requirements/')
    biodata = models.FileField(blank=True, upload_to='upload/ojt_requirements/')
    parents_consent = models.FileField(blank=True, upload_to='upload/ojt_requirements/')
    application_letter = models.FileField(blank=True, upload_to='upload/ojt_requirements/')
    medical = models.FileField(blank=True, upload_to='upload/ojt_requirements/')
    moa = models.FileField(blank=True, upload_to='upload/ojt_requirements/')
    endorsement = models.FileField(blank=True, upload_to='upload/ojt_requirements/')
    certification = models.FileField(blank=True, upload_to='upload/ojt_requirements/')

    nondis_stat = models.CharField(max_length = 20, choices = STATUS_CHOICES, default=NOFILE)
    biodata_stat = models.CharField(max_length = 20, choices = STATUS_CHOICES, default=NOFILE)
    consent_stat = models.CharField(max_length = 20, choices = STATUS_CHOICES, default=NOFILE)
    apl_letter_stat = models.CharField(max_length = 20, choices = STATUS_CHOICES, default=NOFILE)
    medical_stat = models.CharField(max_length = 20, choices = STATUS_CHOICES, default=NOFILE)
    moa_stat = models.CharField(max_length = 20, choices = STATUS_CHOICES, default=NOFILE)
    endorsement_stat = models.CharField(max_length = 20, choices = STATUS_CHOICES, default=NOFILE)
    cert_stat = models.CharField(max_length = 20, choices = STATUS_CHOICES, default=NOFILE)

    is_valid = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.non_disclosure and (self.nondis_stat == self.NOFILE or self.nondis_stat == self.DECLINED):
            self.nondis_stat = self.PENDING
        if self.biodata and (self.biodata_stat == self.NOFILE or self.biodata_stat == self.DECLINED):
            self.biodata_stat = self.PENDING
        if self.parents_consent and (self.consent_stat == self.NOFILE or self.consent_stat == self.DECLINED):
            self.consent_stat = self.PENDING
        if self.application_letter and (self.apl_letter_stat == self.NOFILE or self.apl_letter_stat == self.DECLINED):
            self.apl_letter_stat = self.PENDING
        if self.medical and (self.medical_stat == self.NOFILE or self.medical_stat == self.DECLINED):
            self.medical_stat = self.PENDING
        if self.moa and (self.moa_stat == self.NOFILE or self.moa_stat == self.DECLINED):
            self.moa_stat = self.PENDING
        if self.endorsement and (self.endorsement_stat == self.NOFILE or self.endorsement_stat == self.DECLINED):
            self.endorsement_stat = self.PENDING
        if self.certification and (self.cert_stat == self.NOFILE or self.cert_stat == self.DECLINED):
            self.cert_stat = self.PENDING
            
        super(OJTRequirements, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id.email}"

class Seminar(models.Model):
    seminar_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False, default="")
    theme = models.CharField(max_length=150, null=False, default="")
    date_of_event = models.DateField(null=False, default="")
    image = models.FileField(upload_to='upload/seminar_imgs', null=True, blank=True)  # Add this line   

    def __str__(self):
        return f"{self.seminar_id}"

class SeminarAttendance(models.Model):
    sem_at_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(StudentUser, on_delete=models.CASCADE) # Change to studentModel
    seminar_id = models.ForeignKey(Seminar, null=True, on_delete=models.SET_NULL)
    attended = models.BooleanField(default=False)
    ispending = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.sem_at_id}, is attended {self.attended}"
    
class TransactionReport(models.Model):
    STUDENT = "Student"
    ADMIN = "Admin"
    user_type_choice = [
        (STUDENT, 'Student'),
        (ADMIN, 'Admin')
    ]
    # Modify the user field to allow both StudentUser and JobPlacementAdminUser instances
    report_id = models.AutoField(primary_key=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=1)
    object_id = models.CharField(max_length=30, null=False, blank=False, default="1")
    user = GenericForeignKey('content_type', 'object_id') 
    action = models.CharField(max_length=255, null=False, blank=False, default="None")
    date_created = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(max_length=50, choices=user_type_choice, default=STUDENT)


    class Meta:
        verbose_name = 'Transaction Report'
        verbose_name_plural = 'Transaction Reports'
        ordering = ['date_created']

    def __str__(self):
        return f"{self.user} - {self.action} at {self.date_created.strftime('%Y-%m-%d %H:%M:%S')}"

# class StudentUser(AbstractBaseUser, PermissionsMixin):
#     BSIT = "Bachelor of Science Information and Technology"
#     BEED = "Bachelor of Elementary Education"
#     BSED = "Bachelor of Secondary Education"
#     BIT_COMTECH = "Bachelor of Industrial Technology Major in Computech"
#     BIE = "Bachelor of Industrial Engineering"
#     FORESTRY = "Bachelor of Science and Forestry"
#     PSYCH = "Bachelor of Science"
#     BAEL = "Bachelor of English Literature"
#     CRIM = "Bachelor of Science Criminology"
#     HM = "Bachelor of Science Hospitality and Management"
#     TOURISM = "Bachelor of Science Hospitality and Tourism"
#     CAS = "Bachelor of Crafts Arts and Science"
#     ES = "Bachelor of Environmental Science"

#     program_choices = [
#             (BSIT, 'Bachelor of Science Information and Technology'),
#             (BEED, 'Bachelor of Elementary Education'),
#             (BSED, 'Bachelor of Secondary Education'),
#             (BIT_COMTECH, 'Bachelor of Industrial Technology Major in Computech'),
#             (BIE, 'Bachelor of Industrial Engineering'),
#             (FORESTRY, 'Bachelor of Science and Forestry'),
#             (PSYCH, 'Bachelor of Science'),
#             (BAEL, 'Bachelor of English Literature'),
#             (CRIM, 'Bachelor of Science Criminology'),
#             (HM, 'Bachelor of Science Hospitality and Management'),
#             (TOURISM, 'Bachelor of Science Hospitality and Tourism'),
#             (CAS, 'Bachelor of Crafts Arts and Science'),
#             (ES, 'Bachelor of Environmental Science'),
#     ]

#     is_staff = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     date_joined = models.DateTimeField(default=timezone.now)
#     email = models.EmailField(_("email address"), unique=True)
#     studID = models.PositiveIntegerField(primary_key=True)
#     lrn = models.CharField(max_length=15, null=True, blank=True)
#     firstname = models.CharField(max_length=50, blank=False, null=False)
#     lastname = models.CharField(max_length=50, blank=False, null=False)
#     middlename = models.CharField(max_length=50, null=True, blank=True)
#     yearlvl = models.PositiveIntegerField(default=1, null=False)
#     sex = models.CharField(max_length=1, default="M", null=False)
#     contact = models.CharField(max_length=50, null=True)
#     program = models.CharField(max_length=100, choices=program_choices, default=BSIT)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     objects = StudentUserManager()

#     groups = models.ManyToManyField(
#         Group,
#         verbose_name=_("groups"),
#         blank=True,
#         related_name="student_user_groups"
#     )
    
#     user_permissions = models.ManyToManyField(
#         Permission,
#         verbose_name=_("user permissions"),
#         blank=True,
#         related_name="student_user_permissions"
#     )

#     class Meta:
#         ordering = ['lastname', 'firstname']

#     def __str__(self):
#         return self.email
    
#     def fullname(self):
#         return f"{self.firstname} {self.lastname}"
