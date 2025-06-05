from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.dateparse import parse_date
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


def validate_file_extension(value):
    valid_extensions = (".pdf", ".docx", ".jpg", ".jpeg", ".png", ".gif")
    if not value.name.lower().endswith(valid_extensions):
        raise ValidationError(
            "Only .pdf, .docx, .jpg, .jpeg, .png, and .gif files are allowed."
        )


class Officer(models.Model):
    student_id = models.CharField(primary_key=True, max_length=20)
    Officer_profile_picture = models.FileField(
        upload_to="Officer_Profile/", validators=[validate_file_extension]
    )
    surname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100)

    course = models.CharField(
        max_length=50,
        choices=[
            ("BSIT", "BSIT"),
            ("BSIE", "BSIE"),
            ("BIT-COMPTECH", "BIT-COMPTECH"),
            ("BIT-GARMENTS", "BIT-GARMENTS"),
            ("BIT-AUTOMOTIVE", "BIT-AUTOMOTIVE"),
            ("BIT-DRAFTING", "BIT-DRAFTING"),
            ("BIT-ELECTRONICS", "BIT-ELECTRONICS"),
            ("BEED", "BEED"),
            ("BSED-MATH", "BSED-MATH"),
            ("BTLED", "BTLED"),
            ("BSF", "BSF"),
            ("BSA", "BSA"),
            ("BAL", "BAL"),
            ("BAEL", "BAEL"),
            ("BS-PSYCHOLOGY", "BS-PSYCHOLOGY"),
            ("BSHM", "BSHM"),
            ("BSTM", "BSTM"),
        ],
        default="",
    )

    year = models.CharField(
        max_length=50,
        choices=[
            ("1st", "1st"),
            ("2nd", "2nd"),
            ("3rd", "3rd"),
            ("4th", "4th"),
            ("Irregular", "Irregular"),
        ],
        default="",
    )

    mobile_number = models.CharField(max_length=15)
    position = models.CharField(max_length=100)

    organization = models.CharField(
        max_length=30,
        choices=[
            ("SSG", "SSG"),
            ("FSTLP", "FSTLP"),
            ("SI++", "SI++"),
            ("THE EQUATIONERS", "THE EQUATIONERS"),
            ("TECHNOCRATS", "TECHNOCRATS"),
        ],
    )

    town_address = models.CharField(max_length=200)
    home_address = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    place_of_birth = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=50)
    civil_status = models.CharField(
        max_length=10,
        choices=[
            ("Single", "Single"),
            ("Married", "Married"),
            ("Widowed", "Widowed"),
            ("Separated", "Separated"),
            ("Divorced", "Divorced"),
        ],
    )
    sex = models.CharField(
        max_length=10,
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
        ],
    )
    height = models.FloatField()
    distinguishing_mark = models.CharField(max_length=200, blank=True, null=True)
    weight = models.FloatField()
    hobbies = models.CharField(max_length=200, blank=True, null=True)
    special_talent = models.CharField(max_length=200, blank=True, null=True)

    # Parents
    father_name = models.CharField(max_length=100, blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    father_address = models.CharField(max_length=200, blank=True, null=True)
    father_mobile_number = models.CharField(max_length=15, blank=True, null=True)

    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_address = models.CharField(max_length=200, blank=True, null=True)
    mother_mobile_number = models.CharField(max_length=15, blank=True, null=True)

    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_occupation = models.CharField(max_length=100, blank=True, null=True)
    guardian_address = models.CharField(max_length=200, blank=True, null=True)
    guardian_mobile_number = models.CharField(max_length=15, blank=True, null=True)

    # Educational background
    tertiary_institution = models.CharField(max_length=200, blank=True, null=True)
    tertiary_address = models.CharField(max_length=200, blank=True, null=True)
    tertiary_degree_level = models.CharField(max_length=100, blank=True, null=True)
    tertiary_date = models.DateField(blank=True, null=True)

    secondary_institution = models.CharField(max_length=200, blank=True, null=True)
    secondary_address = models.CharField(max_length=200, blank=True, null=True)
    secondary_degree_level = models.CharField(max_length=100, blank=True, null=True)
    secondary_date = models.DateField(blank=True, null=True)

    elementary_institution = models.CharField(max_length=200, blank=True, null=True)
    elementary_address = models.CharField(max_length=200, blank=True, null=True)
    elementary_degree_level = models.CharField(max_length=100, blank=True, null=True)
    elementary_date = models.DateField(blank=True, null=True)

    # Membership in other organizations
    membership_position1 = models.CharField(max_length=100, blank=True, null=True)
    membership_organization1 = models.CharField(max_length=200, blank=True, null=True)
    membership_date1 = models.DateField(blank=True, null=True)

    membership_position2 = models.CharField(max_length=100, blank=True, null=True)
    membership_organization2 = models.CharField(max_length=200, blank=True, null=True)
    membership_date2 = models.DateField(blank=True, null=True)

    membership_position3 = models.CharField(max_length=100, blank=True, null=True)
    membership_organization3 = models.CharField(max_length=200, blank=True, null=True)
    membership_date3 = models.DateField(blank=True, null=True)

    membership_position4 = models.CharField(max_length=100, blank=True, null=True)
    membership_organization4 = models.CharField(max_length=200, blank=True, null=True)
    membership_date4 = models.DateField(blank=True, null=True)

    membership_position5 = models.CharField(max_length=100, blank=True, null=True)
    membership_organization5 = models.CharField(max_length=200, blank=True, null=True)
    membership_date5 = models.DateField(blank=True, null=True)

    # Seminars
    seminar_title1 = models.CharField(max_length=200, blank=True, null=True)
    seminar_date1 = models.DateField(blank=True, null=True)

    seminar_title2 = models.CharField(max_length=200, blank=True, null=True)
    seminar_date2 = models.DateField(blank=True, null=True)

    seminar_title3 = models.CharField(max_length=200, blank=True, null=True)
    seminar_date3 = models.DateField(blank=True, null=True)

    seminar_title4 = models.CharField(max_length=200, blank=True, null=True)
    seminar_date4 = models.DateField(blank=True, null=True)

    seminar_title5 = models.CharField(max_length=200, blank=True, null=True)
    seminar_date5 = models.DateField(blank=True, null=True)

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
        ("terminated", "Terminated"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.student_id}, {self.surname} {self.firstname} {self.middlename}"


class OfficerLogin(models.Model):
    student_id = models.OneToOneField(
        Officer, on_delete=models.CASCADE, primary_key=True
    )
    ORG_CHOICES = [
        ("SSG", "SSG"),
        ("FSTLP", "FSTLP"),
        ("SI++", "SI++"),
        ("THE EQUATIONERS", "THE EQUATIONERS"),
        ("TECHNOCRATS", "TECHNOCRATS"),
    ]
    organization = models.CharField(max_length=20, choices=ORG_CHOICES)
    course = models.CharField(
        max_length=50,
        choices=[
            ("BSIT", "BSIT"),
            ("BSIE", "BSIE"),
            ("BIT-COMPTECH", "BIT-COMPTECH"),
            ("BIT-GARMENTS", "BIT-GARMENTS"),
            ("BIT-AUTOMOTIVE", "BIT-AUTOMOTIVE"),
            ("BIT-DRAFTING", "BIT-DRAFTING"),
            ("BIT-ELECTRONICS", "BIT-ELECTRONICS"),
            ("BEED", "BEED"),
            ("BSED-MATH", "BSED-MATH"),
            ("BTLED", "BTLED"),
            ("BSF", "BSF"),
            ("BSA", "BSA"),
            ("BAL", "BAL"),
            ("BAEL", "BAEL"),
            ("BS-PSYCHOLOGY", "BS-PSYCHOLOGY"),
            ("BSHM", "BSHM"),
            ("BSTM", "BSTM"),
        ],
        default="",
    )
    username = models.CharField(max_length=100, unique=True, null=False, blank=False)
    password = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return f"OfficerLogin {self.student_id}"


class Adviser(models.Model):
    Adviser_profile_picture = models.FileField(
        upload_to="Adviser_Profile/", validators=[validate_file_extension]
    )
    surname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100)
    department = models.CharField(
        max_length=50,
        choices=[
            ("BSIT", "BSIT"),
            ("BSIE", "BSIE"),
            ("BIT", "BIT"),
        ],
        default="",
    )
    ORG_CHOICES = [
        ("SSG", "SSG"),
        ("FSTLP", "FSTLP"),
        ("SI++", "SI++"),
        ("THE EQUATIONERS", "THE EQUATIONERS"),
        ("TECHNOCRATS", "TECHNOCRATS"),
    ]
    organization = models.CharField(max_length=20, choices=ORG_CHOICES)

    date_employed = models.DateField()
    number_of_years = models.PositiveIntegerField()
    town_address = models.CharField(max_length=190)
    home_address = models.CharField(max_length=190)
    cell1 = models.CharField(max_length=15)
    cell2 = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    nationality = models.CharField(max_length=50)
    sex = models.CharField(
        max_length=10, choices=[("Male", "Male"), ("Female", "Female")]
    )
    civil_status = models.CharField(
        max_length=10,
        choices=[
            ("Single", "Single"),
            ("Married", "Married"),
            ("Widowed", "Widowed"),
            ("Separated", "Separated"),
            ("Divorced", "Divorced"),
        ],
    )
    height = models.FloatField()
    weight = models.FloatField()
    distinguishing_mark = models.CharField(max_length=100, blank=True, null=True)
    hobbies = models.CharField(max_length=100, blank=True, null=True)
    special_talent = models.CharField(max_length=100, blank=True, null=True)

    # Parents' information
    father_name = models.CharField(max_length=100, blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    father_address = models.CharField(max_length=190, blank=True, null=True)
    father_mobile_number = models.CharField(max_length=15, blank=True, null=True)

    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_address = models.CharField(max_length=190, blank=True, null=True)
    mother_mobile_number = models.CharField(max_length=15, blank=True, null=True)

    # Spouse information
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_occupation = models.CharField(max_length=100, blank=True, null=True)
    spouse_address = models.CharField(max_length=190, blank=True, null=True)
    spouse_mobile_number = models.CharField(max_length=15, blank=True, null=True)

    # Educational background
    first_institution = models.CharField(max_length=100, blank=True, null=True)
    first_address = models.CharField(max_length=190, blank=True, null=True)
    first_degree_level = models.CharField(max_length=100, blank=True, null=True)
    first_date = models.DateField(blank=True, null=True)

    second_institution = models.CharField(max_length=100, blank=True, null=True)
    second_address = models.CharField(max_length=190, blank=True, null=True)
    second_degree_level = models.CharField(max_length=100, blank=True, null=True)
    second_date = models.DateField(blank=True, null=True)

    third_institution = models.CharField(max_length=100, blank=True, null=True)
    third_address = models.CharField(max_length=190, blank=True, null=True)
    third_degree_level = models.CharField(max_length=100, blank=True, null=True)
    third_date = models.DateField(blank=True, null=True)

    fourth_institution = models.CharField(max_length=100, blank=True, null=True)
    fourth_address = models.CharField(max_length=190, blank=True, null=True)
    fourth_degree_level = models.CharField(max_length=100, blank=True, null=True)
    fourth_date = models.DateField(blank=True, null=True)

    fifth_institution = models.CharField(max_length=100, blank=True, null=True)
    fifth_address = models.CharField(max_length=190, blank=True, null=True)
    fifth_degree_level = models.CharField(max_length=100, blank=True, null=True)
    fifth_date = models.DateField(blank=True, null=True)

    # Work experience
    work_institution1 = models.CharField(max_length=100, blank=True, null=True)
    work_position1 = models.CharField(max_length=100, blank=True, null=True)
    work_period1 = models.CharField(max_length=100, blank=True, null=True)

    work_institution2 = models.CharField(max_length=100, blank=True, null=True)
    work_position2 = models.CharField(max_length=100, blank=True, null=True)
    work_period2 = models.CharField(max_length=100, blank=True, null=True)

    work_institution3 = models.CharField(max_length=100, blank=True, null=True)
    work_position3 = models.CharField(max_length=100, blank=True, null=True)
    work_period3 = models.CharField(max_length=100, blank=True, null=True)

    work_institution4 = models.CharField(max_length=100, blank=True, null=True)
    work_position4 = models.CharField(max_length=100, blank=True, null=True)
    work_period4 = models.CharField(max_length=100, blank=True, null=True)

    work_institution5 = models.CharField(max_length=100, blank=True, null=True)
    work_position5 = models.CharField(max_length=100, blank=True, null=True)
    work_period5 = models.CharField(max_length=100, blank=True, null=True)

    # Membership in organizations
    org_name1 = models.CharField(max_length=100, blank=True, null=True)
    org_position1 = models.CharField(max_length=100, blank=True, null=True)
    org_period1 = models.CharField(max_length=100, blank=True, null=True)

    org_name2 = models.CharField(max_length=100, blank=True, null=True)
    org_position2 = models.CharField(max_length=100, blank=True, null=True)
    org_period2 = models.CharField(max_length=100, blank=True, null=True)

    # Advisory roles
    advisory1 = models.CharField(max_length=100, blank=True, null=True)
    inclusive_advisory1 = models.DateField(blank=True, null=True)

    advisory2 = models.CharField(max_length=100, blank=True, null=True)
    inclusive_advisory2 = models.DateField(blank=True, null=True)

    advisory3 = models.CharField(max_length=100, blank=True, null=True)
    inclusive_advisory3 = models.DateField(blank=True, null=True)

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
        ("terminated", "Terminated"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")


def __str__(self):
    return f"{self.surname}, {self.firstname} {self.middlename}"


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    objective = models.CharField(max_length=255)
    activities = models.TextField()

    org_choices = [
        ("SSG", "SSG"),
        ("FSTLP", "FSTLP"),
        ("SI++", "SI++"),
        ("THE EQUATIONERS", "THE EQUATIONERS"),
        ("TECHNOCRATS", "TECHNOCRATS"),
    ]
    org = models.CharField(max_length=15, choices=org_choices, default="")

    target_choices = [
        ("Q1", "Q1"),
        ("Q2", "Q2"),
        ("Q3", "Q3"),
        ("Q4", "Q4"),
    ]
    target = models.CharField(max_length=2, choices=target_choices)
    involved_officer = models.CharField(max_length=100)
    p_budget = models.DecimalField(max_digits=15, decimal_places=2, default="0")
    expected_output = models.TextField()
    actual_accomplishment = models.FileField(
        upload_to="projects/",
        validators=[validate_file_extension],
        blank=True,
        null=True,
    )
    remarks = models.TextField()

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    date_saved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.objective


class FinancialStatement(models.Model):
    financial_id = models.AutoField(primary_key=True)
    date = models.DateField()
    purpose = models.CharField(max_length=255)
    source_of_funds = models.CharField(max_length=255)

    org_choices = [
        ("SSG", "SSG"),
        ("FSTLP", "FSTLP"),
        ("SI++", "SI++"),
        ("THE EQUATIONERS", "THE EQUATIONERS"),
        ("TECHNOCRATS", "TECHNOCRATS"),
    ]
    org = models.CharField(max_length=15, choices=org_choices, default="")

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    remarks = models.TextField()

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    date_saved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.purpose}"


class Accreditation(models.Model):
    ORG_CHOICES = [
        ("SSG", "SSG"),
        ("FSTLP", "FSTLP"),
        ("SI++", "SI++"),
        ("THE EQUATIONERS", "THE EQUATIONERS"),
        ("TECHNOCRATS", "TECHNOCRATS"),
    ]

    accreditation_id = models.AutoField(primary_key=True)
    organization = models.CharField(max_length=20, choices=ORG_CHOICES)

    letter_of_intent = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    list_of_officers = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    certificate_of_registration = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )

    list_of_members = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    accomplishment_report = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    calendar_of_activities = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    financial_statement = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    bank_passbook = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    inventory_of_properties = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    organization_bylaws = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    faculty_adviser_appointment = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )
    other_documents = models.FileField(
        upload_to="accreditation/", validators=[validate_file_extension]
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    date_saved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Accreditation {self.accreditation_id} - {self.organization}"


class AdminLogin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_username = models.CharField(
        max_length=50, null=False, blank=False, unique=True
    )
    admin_password = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return f"Adminlogin {self.admin_id}"


class studentInfo(models.Model):
    studID = models.IntegerField(primary_key=True)
    lrn = models.CharField(max_length=12)
    lastname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=50)
    degree = models.CharField(max_length=150)
    yearlvl = models.CharField(max_length=10)
    sex = models.CharField(max_length=10)
    emailadd = models.EmailField()
    contact = models.CharField(max_length=11)

    def __str__(self):
        return f"{self.studID} {self.lastname} {self.firstname}"

    class Meta:
        ordering = ["lastname"]


# REQUEST FOR GOODMORAL
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


# Alumni


class Alumni(models.Model):
    alumniID = models.AutoField(primary_key=True)
    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    alumnidate = models.DateField()
    alumnibirthday = models.DateField()
    alumnicontact = models.CharField(max_length=15)
    sssgsis = models.CharField(max_length=20)
    tin = models.CharField(max_length=20)
    parentguardian = models.CharField(max_length=100)
    alumniaddress = models.TextField()
    firstname = models.CharField(max_length=100, default="")
    lastname = models.CharField(max_length=100, default="")
    email_add = models.CharField(max_length=100, null=False, default="")
    degree = models.CharField(max_length=100, null=False, default="")
    sex = models.CharField(max_length=10, null=False, default="")
    claimed_date = models.DateTimeField(null=True, blank=True)
    approved = models.BooleanField(default=False)


class graduateForm(models.Model):
    alumniID = models.OneToOneField(Alumni, on_delete=models.CASCADE, primary_key=True)
    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE, default=0)
    firstname = models.CharField(max_length=100, null=False)
    lastname = models.CharField(max_length=100, null=False)
    degree = models.CharField(max_length=100, null=False, default="")
    sex = models.CharField(max_length=10, null=False, default="")
    email_add = models.CharField(max_length=100, null=False, default="")
    contactnum = models.CharField(max_length=100, null=False, default="")
    alumniaddress = models.CharField(max_length=255, null=False)
    dategraduated = models.DateField(null=False)
    nameoforganization = models.CharField(max_length=255, null=False)
    employmenttype = models.CharField(max_length=100, default="default_value_here")
    occupationalClass = models.CharField(max_length=100, null=False)
    gradscholrelated = models.CharField(max_length=10, null=False)
    yearscompany = models.CharField(max_length=20, null=False)
    placework = models.CharField(max_length=100, null=False)
    firstjobgraduate = models.CharField(max_length=10, null=False)
    reasonstayingjob = models.TextField(null=False)
    designation = models.CharField(max_length=100, null=False)
    status = models.CharField(max_length=50, null=True)
    department = models.CharField(max_length=50, null=True)
    monthlyincome = models.CharField(max_length=50, null=False)
    workwhileworking = models.CharField(max_length=10, null=False)
    ifnotworking = models.CharField(max_length=255, null=False)
    reasontimegap = models.TextField(null=False)
    natureemployment = models.CharField(max_length=100, null=False)
    numberofyears = models.CharField(max_length=20, null=False)
    monthlyincome2 = models.CharField(max_length=50, null=False)
    academicprofession = models.IntegerField(null=False)
    researchcapability = models.IntegerField(null=False)
    learningefficiency = models.IntegerField(null=False)
    peopleskills = models.IntegerField(null=False)
    problemsolvingskills = models.IntegerField(null=False)
    informationtechnologyskills = models.IntegerField(null=False)
    communityfield = models.IntegerField(null=False)
    globalfield = models.IntegerField(null=False)
    criticalskills = models.IntegerField(null=False)
    salaryimprovement = models.IntegerField(null=False)
    opportunitiesabroad = models.IntegerField(null=False)
    personalitydevelopment = models.IntegerField(null=False)
    technologiesvaluesformation = models.IntegerField(null=False)
    meetingprofessionalneeds = models.CharField(max_length=100, null=False, default="")
    rangeofcourses = models.CharField(max_length=100, null=False)
    relevanceprofession = models.CharField(max_length=100, null=False)
    extracurricular = models.CharField(max_length=100, null=False)
    premiumresearch = models.CharField(max_length=100, null=True)
    interlearning = models.CharField(max_length=100, null=False)
    teachingenvironment = models.CharField(max_length=100, null=False)
    qualityinstruction = models.CharField(max_length=100, null=False)
    teachrelationship = models.CharField(max_length=100, null=False)
    libraryresources = models.CharField(max_length=100, null=False)
    labresources = models.CharField(max_length=100, null=False)
    classize = models.CharField(max_length=100, null=False)
    profexpertise = models.CharField(max_length=100, null=False)
    profsubjectmatter = models.CharField(max_length=100, null=False)
    enrollmentdate = models.DateField(null=False)
    studiesdegree = models.CharField(max_length=100, null=False)
    universityinstitution = models.CharField(max_length=255, null=False)
    studiesAddress = models.CharField(max_length=255, null=False)
    pursuingstudies = models.TextField(null=False)

    def alumni_id(self):
        return self.alumni.alumniID

    alumni_id.short_description = "Alumni ID"


class Event(models.Model):
    eventID = models.AutoField(primary_key=True)
    eventsName = models.CharField(max_length=100)
    eventsDate = models.DateField()
    eventsLocation = models.CharField(max_length=100)
    eventsDescription = models.TextField()
    eventsImage = models.ImageField(upload_to="event_images/", null=True, blank=True)


class JobFair(models.Model):
    jobfair_id = models.AutoField(primary_key=True)
    jobtitle = models.CharField(max_length=255, default="")
    companyname = models.CharField(max_length=255)
    joblocation = models.CharField(max_length=255)
    employmenttype = models.CharField(max_length=100)
    jobdescription = models.TextField()
    jobsalary = models.CharField(max_length=255)
    applicationdeadline = models.DateField(default=None)
    posted_date = models.DateField(default=None)


class Yearbook(models.Model):
    yearbookID = models.AutoField(primary_key=True)
    yearbookFirstname = models.CharField(max_length=100)
    yearbookLastname = models.CharField(max_length=100)
    yearbookAddress = models.CharField(max_length=255)
    yearbookCourse = models.CharField(max_length=100)
    yearbookImage = models.ImageField(upload_to="yearbook_images/")
    yearbookGender = models.CharField(max_length=100, default="")
    yearbookYearGrad = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.yearbookFirstname} {self.yearbookLastname}"


class exit_interview_db(models.Model):
    exitinterviewId = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    dateRecieved = models.DateField()

    scheduled_date = models.DateField()
    time = [
        ("8-9", "8:00 AM - 9:00 AM"),
        ("9-10", "9:00 AM - 10:00 AM"),
        ("10-11", "10:00 AM-11:00 AM"),
        ("11-12", "11:00 AM -12:00 PM"),
        ("1-2", "1:00 PM - 2:00 PM"),
        ("2-3", "2:00 PM - 3:00 PM"),
        ("3-4", "3:00 PM - 4:00 PM"),
        ("4-5", "4:00 PM - 5:00 PM"),
    ]
    scheduled_time = models.CharField(max_length=15, choices=time)
    emailadd = models.EmailField()
    date = models.DateField()
    dateEnrolled = models.DateField()
    reasonForLeaving = models.CharField(max_length=255)
    satisfiedWithAcadamic = models.BooleanField(default=False)
    feedbackWithAcademic = models.CharField(max_length=255)
    satisfiedWithSocial = models.BooleanField(default=False)
    feedbackWithSocial = models.CharField(max_length=255)
    satisfiedWithServices = models.BooleanField(default=False)
    feedbackWithServices = models.CharField(max_length=255)
    contributedToDecision = models.JSONField()
    intendedMajor = models.CharField(max_length=255)
    majorEvent = models.CharField(max_length=255)
    firstConsider = models.CharField(max_length=255)
    whatCondition = models.CharField(max_length=255)

    recommend = models.BooleanField(default=False)
    howSatisfiedChoices = [
        ("very satisfied", "Very satisfied"),
        ("somewhat satisfied", "Somewhat satisfied"),
        ("satisfied", "Satisfied"),
        ("somewhat dissatisfied", "Somewhat Dissatisfied"),
        ("very dissatisfied", "Very Dissatisfied"),
    ]
    howSatisfied = models.CharField(max_length=30, choices=howSatisfiedChoices)
    planTOReturn = models.CharField(max_length=255)
    accademicExperienceSatisfied = models.BooleanField(default=False)
    knowAboutYourTime = models.CharField(max_length=255)
    currentlyEmployed = models.BooleanField(default=False)
    explainationEmployed = models.CharField(max_length=255)
    approval_status = [
        ("Accepted", "Accepted"),
        ("Declined", "Declined"),
        ("Pending", "Pending"),
        ("Expired", "Expired"),
    ]
    status = models.CharField(max_length=10, choices=approval_status, default="Pending")

    def check_and_update_status(self):
        if self.scheduled_date < timezone.now():
            self.status = "Expired"
        elif self.status == "Expired" and self.scheduled_date >= timezone.now():
            self.status = "Pending"


class OjtAssessment(models.Model):
    OjtRequestID = models.AutoField(primary_key=True)
    orno = models.IntegerField(default=0)
    studentID = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    dateRecieved = models.DateField()
    schoolYearChoices = [
        ("2020-2021", "2020-2021"),
        ("2021-2022", "2021-2022"),
        ("2022-2023", "2022-2023"),
        ("2023-2024", "2023-2024"),
        ("2024-2025", "2024-2025"),
        ("2025-2026", "2025-2026"),
        ("2026-2027", "2026-2027"),
        ("2027-2028", "2027-2028"),
        ("2028-2029", "2028-2029"),
        ("2029-2030", "2029-2030"),
        ("2030-2031", "2030-2031"),
        ("2031-2032", "2031-2032"),
        ("2032-2033", "2032-2033"),
        ("2033-2034", "2033-2034"),
        ("2034-2035", "2034-2035"),
        ("2035-2036", "2035-2036"),
        ("2036-2037", "2036-2037"),
        ("2037-2038", "2037-2038"),
        ("2038-2039", "2038-2039"),
        ("2039-2040", "2039-2040"),
        ("2040-2041", "2040-2041"),
    ]
    schoolYear = models.CharField(max_length=10, choices=schoolYearChoices)
    approval_status = [
        ("Accepted", "Accepted"),
        ("Declined", "Declined"),
        ("Pending", "Pending"),
        ("Expired", "Expired"),
    ]
    status = models.CharField(max_length=10, choices=approval_status, default="Pending")
    dateAccepted = models.DateField()
    emailadd = models.EmailField()

    def check_and_update_status(self):
        if self.dateAccepted < timezone.now():
            self.status = "Expired"
        elif self.status == "Expired" and self.dateAccepted >= timezone.now():
            self.status = "Pending"


class counseling_schedule(models.Model):
    counselingID = models.AutoField(primary_key=True)
    counselingOrigin = models.CharField(max_length=20)
    dateRecieved = models.DateField()
    studentID = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    scheduled_date = models.DateField()
    time = [
        ("8-9", "8:00 AM - 9:00 AM"),
        ("9-10", "9:00 AM - 10:00 AM"),
        ("10-11", "10:00 AM-11:00 AM"),
        ("11-12", "11:00 AM -12:00 PM"),
        ("1-2", "1:00 PM - 2:00 PM"),
        ("2-3", "2:00 PM - 3:00 PM"),
        ("3-4", "3:00 PM - 4:00 PM"),
        ("4-5", "4:00 PM - 5:00 PM"),
    ]
    scheduled_time = models.CharField(max_length=15, choices=time)
    email = models.EmailField()
    approval_status = [
        ("Accepted", "Accepted"),
        ("Declined", "Declined"),
        ("Pending", "Pending"),
        ("Expired", "Expired"),
    ]
    status = models.CharField(max_length=10, choices=approval_status, default="Pending")

    def check_and_update_status(self):
        if self.scheduled_date < timezone.now():
            self.status = "Expired"
        elif self.status == "Expired" and self.scheduled_date >= timezone.now():
            self.status = "Pending"


class IndividualProfileBasicInfo(models.Model):
    individualProfileID = models.AutoField(primary_key=True)
    studentId = models.ForeignKey(studentInfo, on_delete=models.CASCADE)
    studentPhoto = models.FileField(upload_to="media/studentPhoto")

    nickName = models.CharField(max_length=255)
    yearlvl = models.IntegerField()
    section = models.CharField(max_length=255)
    major = models.CharField(max_length=255)
    dateFilled = models.DateField()

    studentTypeChoices = [
        ("newStudent", "New Student"),
        ("returnee", "Returnee"),
        ("shifter", "Shifter"),
        ("transferee", "Transferee"),
        ("alspasses", "ALS Passer"),
        ("foreignstudent", "Foreign Student"),
    ]

    studentType = models.CharField(max_length=30, choices=studentTypeChoices)

    # Only need if student is new student

    curriculumtypeChoices = [
        ("oldsecondary", "Old Secondary Curriculum Graduate"),
        ("seniorhigh", "Senior High School Graduate"),
    ]

    curriculumtype = models.CharField(max_length=50, choices=curriculumtypeChoices)

    track = models.CharField(
        max_length=255, default=""
    )  # Will only be used if curriculumtype is senior high

    age = models.IntegerField()
    religion = models.CharField(max_length=255)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    birthOrderAmongSiblings = models.CharField(max_length=10)

    sexualOrientationChoices = [
        ("heterosexual", "Heterosexual"),
        ("gay", "Gay"),
        ("lesbian", "Lesbian"),
        ("others", "Others"),
    ]

    sexualOrientation = models.CharField(
        max_length=15, choices=sexualOrientationChoices
    )

    civilStatus = models.CharField(max_length=255)
    citizenship = models.CharField(max_length=255)
    dateOfBirth = models.DateField()
    placeOfBirth = models.CharField(max_length=255)
    currentAddress = models.CharField(max_length=255)
    permanentAddress = models.CharField(max_length=255)
    landlineNo = models.CharField(max_length=255)
    mobileNo = models.CharField(max_length=255)
    email = models.EmailField()
    languagesDialectsSpokenAtHome = models.CharField(max_length=255)
    languagesDialectsMostFluentIn = models.CharField(max_length=255)

    livingWithChoices = [
        ("parents", "Parents"),
        ("fatheronly", "Father Only"),
        ("motheronly", "Mother Only"),
        ("spouse", "Spouse"),
        ("relative", "Relative"),
        ("employer", "Employer"),
        ("others", "Others"),
    ]

    livingWith = models.CharField(max_length=15, choices=livingWithChoices)

    livingSpecify = models.CharField(
        max_length=255, default=""
    )  # Will be used if living with relative is true

    placeOfLivingChoices = [
        ("dormitory", "Dormitory"),
        ("boardinghouse", "Boarding House"),
        ("ownhouse", "Own House"),
        ("others", " Others"),
    ]
    placeOfLiving = models.CharField(max_length=20, choices=placeOfLivingChoices)
    placeOfLivingOthers = models.CharField(
        max_length=255, default=""
    )  # Will be used if place of living is other

    fatherName = models.CharField(max_length=255)
    motherName = models.CharField(max_length=255)
    fatherDateOfBirth = models.DateField()
    motherDateOfBirth = models.DateField()
    fatherAddress = models.CharField(max_length=255)
    motherAddress = models.CharField(max_length=255)
    fatherLandline = models.CharField(max_length=255)
    motherLandLine = models.CharField(max_length=255)
    fatherMobilePhone = models.CharField(max_length=255)
    motherMobilePhone = models.CharField(max_length=255)

    educationLevelChoices = [
        ("elementarylevel", "Elementary Level"),
        ("elementarygraduate", "Elementary Graduate"),
        ("highschoollevel", "High School Level"),
        ("highschoolgraduate", "High School Graduate"),
        ("collegelevel", "College Level"),
        ("collegegraduate", "College Graduate"),
        ("postgraduate", "Post Graduate"),
    ]

    fatherEducationLevel = models.CharField(
        max_length=30, choices=educationLevelChoices
    )
    motherEducationLevel = models.CharField(
        max_length=30, choices=educationLevelChoices
    )

    fatherCTU = models.BooleanField()
    motherCTU = models.BooleanField()
    sourceOfIncomeChoices = [
        ("onlyfatherworks", "Only father works"),
        ("onlymotherworks", "Only mother works"),
        ("bothparentswork", "Both parents work"),
        ("siblingswork", "Sibling(s) work"),
        ("familyownedbusiness", "Family owned business"),
        ("relatives", "Relative(s)"),
    ]
    sourceOfIncome = models.CharField(max_length=30, choices=sourceOfIncomeChoices)
    sourceOfIncomeSpecify = models.CharField(max_length=255, default="")

    parentsOccupationChoices = [
        ("agriculture", "Agriculture, Food and Natural Resources"),
        ("architecture", "Architecture, Design and Construction"),
        ("businessmanagement", "Business Management, Marketing and Sales"),
        ("clerical", "Clerical and Customer Service"),
        ("education", "Education and Training"),
        ("health", "Health"),
        ("law", "Law, Public Safety Corrections and Security"),
        ("manufacturing", "Manufacturing"),
        ("science", "Science, Technology, Engineering"),
        ("maintenance", "Maintenance and Services"),
        ("transportation", "Transportation, Distribution and Logistics"),
        ("unemployed", "Unemployed"),
        ("others", "Others"),
    ]

    fatherOccupation = models.CharField(
        max_length=255, choices=parentsOccupationChoices
    )
    fatherOtherOccupation = models.CharField(max_length=255, default="")

    motherOccupation = models.CharField(
        max_length=255, choices=parentsOccupationChoices
    )
    motherOtherOccupation = models.CharField(max_length=255, default="")

    familyEarningInaMonthChoices = [
        ("below1000", "below P 1,000"),
        ("1000-5000", "P 1,000 - P 5,000"),
        ("11000-15000", "P 11,000 - P 15,000"),
        ("16000-20000", "P 16,000 - P 20,000"),
        ("21000-25000", "P 21,000 - P 25,000"),
        ("26000-30000", "P 26,000 - P 30,000"),
        ("31000-40000", "P 31,000 - P 40,000"),
        ("41000andabove", "P 41,000 and above"),
    ]

    familyEarningInaMonth = models.CharField(
        max_length=30, choices=familyEarningInaMonthChoices
    )

    parentStatusChoices = [
        ("together&married", "Living together and legally married"),
        ("together&notmarried", "Living together and not legally married"),
        ("marriedbutseparate", "Legally married but living separetely"),
        ("mohterofw", "Mother is OFW"),
        ("fatherofw", "Father is OFW"),
        ("fatherwanother", "Father w/ Another Partner"),
        ("motherwanother", "Mother w/ Another Partner"),
    ]

    parentStatus = models.CharField(max_length=50, choices=parentStatusChoices)

    siblingsName = models.JSONField()
    siblingsAge = models.JSONField()
    siblingsSchoolWork = models.JSONField()

    # Contact persons

    personInCaseofEmergency = models.CharField(max_length=255)
    personInCaseofEmergencyRelationship = models.CharField(max_length=255)
    personInCaseofEmergencyAddress = models.CharField(max_length=255)
    personInCaseofEmergencyLandline = models.CharField(max_length=255, default="")
    personInCaseofEmergencyMobileNo = models.CharField(max_length=255)

    # Healh Data

    disabilies = models.CharField(max_length=255)
    allergies = models.CharField(max_length=255)

    bloodTypeChoices = [
        ("O-", "O negative"),
        ("O+", "O positive"),
        ("A-", "A negative"),
        ("A+", "A positive"),
        ("B-", "B negative"),
        ("B+", "B positive"),
        ("AB-", "AB negative"),
        ("AB+", "AB positive"),
        ("unknown", "Unknown"),
    ]
    bloodType = models.CharField(max_length=10, choices=bloodTypeChoices)

    # Education Background

    elementaryName = models.CharField(max_length=255)
    elementaryType = models.BooleanField()
    elementaryAwardsRecieved = models.CharField(max_length=255)
    elementaryYearGraduated = models.IntegerField()

    seniorHighSchoolName = models.CharField(max_length=255)
    seniorHighSchoolType = models.BooleanField()
    seniorHighSchoolAwardsRecieved = models.CharField(max_length=255)
    seniorHighSchoolYearGraduated = models.IntegerField()

    collegeName = models.CharField(max_length=255, default="")
    collegeAwardsRecieved = models.CharField(max_length=255, default="")
    collegeYearGraduated = models.IntegerField(default=0)

    schoolLeaver = models.BooleanField()
    schoolLeaverWhy = models.CharField(max_length=255)  # If school leaver is yes
    lastEducationAttainment = models.CharField(max_length=255)

    finaciallySupportingChoices = [
        ("parents", "Parents"),
        ("spouse", "Spouse"),
        ("relatives", "Relatives"),
        ("selfsupporting", "Self-supporting"),
        ("scholarship", "Scholarship"),
    ]

    finaciallySupporting = models.CharField(
        max_length=20, choices=finaciallySupportingChoices
    )

    typeOfScholarshipChoices = [
        ("private", " Scholarship by private institution"),
        ("government", "Government Scholarship"),
        ("organizations", " Scholarships granted by organizations within CTU"),
    ]

    typeOfScholarship = models.CharField(
        max_length=100, choices=typeOfScholarshipChoices
    )
    specifyScholarship = models.CharField(max_length=255, default="")

    # Membership in organizations

    nameOfOrganization = models.JSONField()
    inOutSchool = models.JSONField()
    positionTitle = models.JSONField()
    inclusiveYears = models.JSONField()

    # Unique Features

    specialSkill = models.CharField(max_length=255)
    goals = models.CharField(max_length=255)
    presentConcerns = models.CharField(max_length=255)

    # Students

    describeYouBest = models.JSONField()
    describeYouBestOther = models.CharField(max_length=255, default="")

    # School/Career-related

    decisionForTheCourseChoices = [
        ("self", "Self"),
        ("parents", "Parent(s)"),
        ("brothersister", "Brother/Sister"),
        ("sponsorsscholarship", "Sponsors/Scholarship"),
        ("relatives", "Relatives"),
        ("friends", "Friends"),
    ]

    decisionForTheCourse = models.CharField(
        max_length=40, choices=decisionForTheCourseChoices
    )
    specifyTheDecision = models.CharField(max_length=255)
    doYouPlanToWork = models.BooleanField()
    specifyIfNo = models.CharField(max_length=255)
    possibleFactors = models.CharField(max_length=255)


class TestArray(models.Model):
    myarray = models.JSONField()


class FileUploadTest(models.Model):
    file = models.FileField()


class IntakeInverView(models.Model):
    intakeId = models.AutoField(primary_key=True)
    individualProfileId = models.ForeignKey(
        IndividualProfileBasicInfo, on_delete=models.CASCADE
    )

    individualActivity = models.JSONField()
    individualDateAccomplished = models.JSONField()
    individualRemarks = models.JSONField()

    appraisalTest = models.JSONField()
    appraisalDateTaken = models.JSONField()
    appraisalDateInterpreted = models.JSONField()
    appraisalRemarks = models.JSONField()

    counselingType = models.JSONField()
    counselingDate = models.JSONField()
    counselingConcern = models.JSONField()
    counselingRemarks = models.JSONField()

    followActivity = models.JSONField()
    followDate = models.JSONField()
    followRemarks = models.JSONField()

    informationActivity = models.JSONField()
    informationDate = models.JSONField()
    informationRemarks = models.JSONField()

    counsultationActivity = models.JSONField()
    counsultationDate = models.JSONField()
    counsultationRemarks = models.JSONField()


class GuidanceTransaction(models.Model):
    transactionId = models.AutoField(primary_key=True)
    transactionOrigin = models.CharField(max_length=255)
    transactionType = models.CharField(max_length=255)
    transactionDate = models.DateField(max_length=255)


class Program(models.Model):
    title = models.CharField(max_length=255)
    caption = models.CharField(max_length=1000)
    date_time = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)
    image_upload = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.title


class Projects(models.Model):
    title = models.CharField(max_length=255)
    caption = models.CharField(max_length=1000)
    date_time = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)
    image_upload = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.title


class MOD(models.Model):
    donated = models.CharField(max_length=255)
    name = models.CharField(max_length=150)

    donation_type = models.CharField(max_length=10)
    gcash_number = models.CharField(max_length=11)

    bank_number = models.CharField(max_length=11)
    bank_card = models.CharField(max_length=20)

    image_details = models.ImageField(upload_to="images/")
    status = models.CharField(max_length=10, null=True, blank=True)

    amount = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    what_kind = models.CharField(max_length=20)
    recepient = models.CharField(max_length=20, default="")
    recepient_things = models.CharField(max_length=20, default="")
    contact_number = models.CharField(max_length=11)
    date_sched = models.CharField(max_length=20, default="")

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
