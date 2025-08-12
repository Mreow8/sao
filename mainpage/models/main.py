# models.py
# from django.contrib.auth.models import User
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
        ('superadmin', 'Superadmin'),
        ('guard', 'Guard'),
        ('org_member', 'Org Member'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.username} ({self.role})"
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        app_label = "mainpage" 