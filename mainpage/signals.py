# # signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from .models import UserProfile

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models import F
# Update this import to match your app's models file location
# NEW (Correct)
from .models.job_placement import OJTStudent, OJTCompany

@receiver(post_delete, sender=OJTStudent)
def add_slot_back_on_delete(sender, instance, **kwargs):
    """
    Listen for an OJTStudent assignment to be deleted.
    When it is, add the slot back to the company.
    """
    try:
        company = instance.company_id
        company.number_of_slots = F('number_of_slots') + 1
        company.save(update_fields=['number_of_slots'])
        print(f"Slot added back to {company.company_name} due to OJTStudent record deletion.")
    except OJTCompany.DoesNotExist:
        print(f"Company not found. Could not add slot back.")