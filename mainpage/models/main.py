
from django.db import models

# class UserProfile(models.Model):
#     ROLE_CHOICES = (
#         ('admin', 'Admin'),
#         ('user', 'User'),
#     )
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

#     def __str__(self):
#         return f"{self.user.username} - {self.role}"
# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from ..models.studentorg import Organization

# --- CustomUser Model ---
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        # Existing Roles
        ('superadmin', 'Superadmin'),
        ('clinic_admin', 'Clinic Admin'),
        ('guidance', 'Guidance'),
        ('org_admin', 'Org Admin'),
        ('guard', 'Guard'),
        ('student', 'Student'),

        # New University Staff Roles
        ('staff', 'Staff'),
        ('discipline_officer', 'Discipline Officer'),
        ('alumni_officer', 'Alumni Officer'),
        ('student_life_staff', 'Student Life Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError
from ..models import studentInfo
from django.conf import settings
class EmailVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_otp_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"Verification for {self.user.email}"

class SystemSettings(models.Model):
    require_otp_verification = models.BooleanField(default=True, help_text="If enabled, users will need to verify their email with OTP during login")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SystemSettings.objects.exists():
            raise ValidationError("There can be only one SystemSettings instance")
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    def __str__(self):
        return "System Settings"
class TemporaryUser(models.Model):
    # --- Role Choices (Mirroring CustomUser for temporary storage) ---
    ROLE_CHOICES = [
        ('superadmin', 'Superadmin'),
        ('clinic_admin', 'Clinic Admin'),
        ('guidance', 'Guidance'),
        ('org_admin', 'Org Admin'),
        ('guard', 'Guard'),
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('discipline_officer', 'Discipline Officer'),
        ('alumni_officer', 'Alumni Officer'),
        ('student_life_staff', 'Student Life Staff'),
    ]

    # Store the unique identifier (studID or staffID)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    
    # Store the HASHED password
    password = models.CharField(max_length=128) 
    
    # === FIX: ADDED ROLE FIELD ===
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    # ==============================
    
    # OTP details
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now) # Changed to default=timezone.now for explicit tracking
    
    def __str__(self):
        return self.email

    # Helper method for checking expiration (as used in verify_otp)
    def is_expired(self):
        from datetime import timedelta
        return self.created_at < timezone.now() - timedelta(minutes=10)