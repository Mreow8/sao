from django.db import models
# from ..models import *
from mainpage.models import *  # Adjust the import path if studentInfo is elsewhere
from mainpage.models.guidance import studentInfo
class RequestedGMC(models.Model):
    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    reason = models.TextField()
    or_num = models.CharField(max_length=100, null=True, blank=True)
    request_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"GMC Request for {self.student} - {self.reason}"


# MONTHLY CALENDAR OF ACTIVITIES
class Schedule(models.Model):
    sched_Id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.sched_Id} {self.title}"


# EQUIPMENT TRACKER
class Equipment(models.Model):
    itemId = models.AutoField(primary_key=True)
    equipmentName = models.CharField(max_length=255)
    equipmentSN = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.equipmentName} {self.equipmentSN}"


# PPMP TRACKER
class ProcurementItem(models.Model):
    itemid = models.AutoField(primary_key=True)
    item = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, default="your_default_value")
    estimated_budget = models.DecimalField(max_digits=10, decimal_places=2)
    mode_of_procurement = models.CharField(max_length=255)
    jan = models.IntegerField(default=0)
    feb = models.IntegerField(default=0)
    mar = models.IntegerField(default=0)
    apr = models.IntegerField(default=0)
    may = models.IntegerField(default=0)
    jun = models.IntegerField(default=0)
    jul = models.IntegerField(default=0)
    aug = models.IntegerField(default=0)
    sep = models.IntegerField(default=0)
    oct = models.IntegerField(default=0)
    nov = models.IntegerField(default=0)
    dec = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    # adding field para sa status: for purchase, purchased, delivered
    STATUS_CHOICES = (
        ("for_purchase", "For Purchase"),
        ("purchased", "Purchased"),
        ("delivered", "Delivered"),
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="for_purchase"
    )

    def __str__(self):
        return self.item


# subukan ulit huhu
class Storage(models.Model):
    procurement_item = models.OneToOneField(ProcurementItem, on_delete=models.CASCADE)
    serial_no = models.CharField(max_length=255, null=True, blank=True)


# learning & development
class ExcelData(models.Model):
    title_of_l_d = models.CharField("Title of L & D", max_length=255)
    frequency = models.CharField(
        "Frequency (Annual, Semi-Annual, Quarterly)", max_length=255
    )
    category = models.CharField(
        "Category (International, National & Regional/Local)", max_length=255
    )
    expected_number_of_participants = models.CharField(
        "Expected Number of Participants", max_length=255
    )
    duration = models.CharField("Duration", max_length=255)
    registration_fees = models.CharField("Registration Fees", max_length=255)
    travelling_expenses = models.CharField(
        "Travelling Expenses (Per Diem and Transportation)", max_length=255
    )
    planned_total_budget = models.CharField("Planned Total Budget", max_length=255)
    actual_total_budget = models.CharField("Actual Total Budget", max_length=255)

    # HERE ANG NAPUNO TO SOLVE FOR THE DIFFERENCE pati remarks
    variance = models.FloatField(null=True, blank=True)
    admin_remarks = models.TextField(null=True, blank=True, max_length=2000)

    @classmethod
    def create_total_labels(cls):
        cls.objects.create(
            title_of_l_d="Total",
            frequency="",
            category="",
            expected_number_of_participants="",
            duration="",
            registration_fees="",
            travelling_expenses="",
            planned_total_budget="",
            actual_total_budget="",
            variance=None,  # napuno pd ne syaaa
        )

    def save(self, *args, **kwargs):
        # Calculate variance before saving
        if self.planned_total_budget and self.actual_total_budget:
            self.variance = float(self.planned_total_budget) - float(
                self.actual_total_budget
            )
        super().save(*args, **kwargs)


class BorrowingRecord(models.Model):
    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    date_borrowed = models.DateField()
    date_returned = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} borrowed {self.equipment} on {self.date_borrowed}"
