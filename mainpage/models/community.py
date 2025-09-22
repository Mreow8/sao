from django.db import models


class Program(models.Model):
    title = models.CharField(max_length=255)
    caption = models.CharField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ProgramImage(models.Model):
    program = models.ForeignKey(
        Program, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="project_images/")

    def __str__(self):
        return f"Image for {self.project.title}"



class CrowdfundingProject(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    

class DonationChannel(models.Model):
    project = models.ForeignKey(
        CrowdfundingProject, related_name="channels", on_delete=models.CASCADE
    )
    
    imageCrowdfunding = models.ImageField(upload_to="imageCrowdfunding/")

    def __str__(self):
        return f"{self.name} for {self.project.title}"

class Donation(models.Model):
    project = models.ForeignKey(
        CrowdfundingProject, related_name="donations", on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    donor_name = models.CharField(max_length=255, blank=True, null=True)  # optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation {self.amount} to {self.project.title}"
class MOD(models.Model):  # Money/Other Donations
    donated = models.CharField(max_length=255)
    name = models.CharField(max_length=150)

    donation_type = models.CharField(max_length=10)
    gcash_number = models.CharField(max_length=11, blank=True, null=True)

    bank_number = models.CharField(max_length=11, blank=True, null=True)
    bank_card = models.CharField(max_length=20, blank=True, null=True)

    image_details = models.ImageField(upload_to="images/", blank=True, null=True)
    status = models.CharField(max_length=10, null=True, blank=True)

    amount = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    what_kind = models.CharField(max_length=20, blank=True, null=True)
    recepient = models.CharField(max_length=20, default="", blank=True, null=True)
    recepient_things = models.CharField(max_length=20, default="", blank=True, null=True)
    contact_number = models.CharField(max_length=11, blank=True, null=True)
    date_sched = models.CharField(max_length=20, default="", blank=True, null=True)

    def __str__(self):
        return self.name


class QrDonation(models.Model):
    qr_id = models.AutoField(primary_key=True)
    gcash = models.ImageField(upload_to="images/")
    bpi = models.ImageField(upload_to="images/")
    bdo = models.ImageField(upload_to="images/")
    landbank = models.ImageField(upload_to="images/")
    pnb = models.ImageField(upload_to="images/")
    metro = models.ImageField(upload_to="images/")
    union = models.ImageField(upload_to="images/")
    china = models.ImageField(upload_to="images/")

    def __str__(self):
        return f"{self.qr_id}"
