from django.db import models

class Program(models.Model):
    title = models.CharField(max_length=255)
    caption = models.CharField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    event_date = models.DateTimeField(blank=True, null=True)
    venue = models.CharField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True) 
    
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class ProgramImage(models.Model):
    program = models.ForeignKey(
        Program, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="project_images/")

    def __str__(self):
        # FIX: Changed self.project.title to self.program.title
        return f"Image for {self.program.title}"


class CrowdfundingProject(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    # FIX: Removed redundant date_time field. Use created_at instead.
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DonationChannel(models.Model):
    project = models.ForeignKey(
        CrowdfundingProject, related_name="channels", on_delete=models.CASCADE
    )
    # FIX: Added the missing 'name' field used in your template and __str__
    name = models.CharField(max_length=100, default="Payment Channel")
    imageCrowdfunding = models.ImageField(upload_to="imageCrowdfunding/")

    def __str__(self):
        return f"{self.name} for {self.project.title}"


class Donation(models.Model):
    project = models.ForeignKey(
        CrowdfundingProject, related_name="donations", on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2) # This is correct
    donor_name = models.CharField(max_length=255, blank=True, null=True)
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

    # FIX: Changed from IntegerField to DecimalField to handle cents
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)

    what_kind = models.CharField(max_length=20, blank=True, null=True)
    recepient = models.CharField(max_length=20, default="", blank=True, null=True)
    recepient_things = models.CharField(
        max_length=20, default="", blank=True, null=True
    )
    contact_number = models.CharField(max_length=11, blank=True, null=True)
    date_sched = models.CharField(max_length=20, default="", blank=True, null=True)

    def __str__(self):
        return self.name


class QrDonation(models.Model):
    # FIX: Removed redundant qr_id. Django auto-creates an 'id' field.
    gcash = models.ImageField(upload_to="images/")
    bpi = models.ImageField(upload_to="images/")
    bdo = models.ImageField(upload_to="images/")
    landbank = models.ImageField(upload_to="images/")
    pnb = models.ImageField(upload_to="images/")
    metro = models.ImageField(upload_to="images/")
    union = models.ImageField(upload_to="images/")
    china = models.ImageField(upload_to="images/")

    def __str__(self):
        # Use the auto-generated 'id' field
        return f"QR Set {self.id}"