from django.db import models
from django.core.exceptions import ValidationError
from mainpage.models.guidance import studentInfo

from django.utils.text import slugify


def validate_file_extension(value):
    valid_extensions = ('.pdf', '.docx', '.jpg', '.jpeg', '.png', '.gif')
    if not value.name.lower().endswith(valid_extensions):
        raise ValidationError('Only .pdf, .docx, .jpg, .jpeg, .png, and .gif files are allowed.')
    
class Organization(models.Model):
    id = None  # remoe default 'id'
    org_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='org_logos/')
    description = models.TextField(blank=True)
    key_elements = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
        # No 'timezone' import is needed for this version
from django.db import models
# Make sure your other models are imported or defined
# from .models import studentInfo, Organization

class OrganizationCBL(models.Model):
    cbl_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name="cbl_documents"
    )
    cbl_file = models.FileField(
        upload_to='organization_cbls/', 
        validators=[validate_file_extension],
        verbose_name="Constitution and By-Laws File"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Is this the currently active CBL for the organization?"
    )

    class Meta:
        ordering = ['-uploaded_at'] # Show the newest ones first

    def __str__(self):
        return f"{self.organization.name} - CBL ({self.uploaded_at.strftime('%Y-%m-%d')})"
class Officer(models.Model):
    officer_id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(
        upload_to='officer_profiles/',  # Saves to 'media/officer_profiles/'
        blank=True, 
        null=True
    )
    student = models.ForeignKey(studentInfo, on_delete=models.CASCADE)

    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, blank=True, null=True)
    surname = models.CharField(max_length=100)
    
    sex = models.CharField(
        max_length=10,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
        ]
    )
    date_of_birth = models.DateField()
    age = models.PositiveIntegerField()
    
    civil_status = models.CharField(
        max_length=10,
        choices=[
            ('Single', 'Single'),
            ('Married', 'Married'),
            ('Widowed', 'Widowed'),
            ('Separated', 'Separated'),
            ('Divorced', 'Divorced'),
        ]
    )
    nationality = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=15)
    position = models.CharField(max_length=100)
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="officers"
    )
    
    course = models.CharField(max_length=50 )
    
    year = models.CharField(max_length=50, choices=[
        ('1st', '1st'),
        ('2nd', '2nd'),
        ('3rd', '3rd'),
        ('4th', '4th'),
        ('Irregular', 'Irregular'),
    ])
    
    home_address  = models.CharField(max_length=200)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # --- NEW FIELDS FOR "YEAR ONLY" ---
    
    academic_year = models.CharField(
        max_length=10,  # For "2024-2025"
        verbose_name="Academic Year",
        help_text="The academic year of service (e.g., 2024-2025)",
        null=True, blank=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Currently Active",
        help_text="Is this officer currently active? (Uncheck this for past officers)"
    )
    
    # --- NO @property is_active function needed ---

    def __str__(self):
        middle = f" {self.middlename}" if self.middlename else ""
        return f"{self.surname}, {self.firstname}{middle}"
class OfficerMembership(models.Model):
    membership_id = models.AutoField(primary_key=True)
    officer = models.ForeignKey(
        Officer,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    position = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.officer.surname}, {self.officer.firstname} - {self.organization or 'No Org'} ({self.position or 'No Position'})"

class OfficerSeminar(models.Model):
    seminar_id = models.AutoField(primary_key=True)
    officer = models.ForeignKey(
        Officer,
        on_delete=models.CASCADE,
        related_name="seminars"
    )
    title = models.CharField(max_length=200)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.date}) - {self.officer.surname}, {self.officer.firstname}"
    
    
# class Officer(models.Model):
#     Officer_profile_picture =models.FileField(upload_to='Officer_Profile/', validators=[validate_file_extension])
#     surname = models.CharField(max_length=100)
#     firstname = models.CharField(max_length=100)
#     middlename = models.CharField(max_length=100)

#     course = models.CharField(max_length=50, choices=[
#         ('BSIT', 'BSIT'),
#         ('BSIE', 'BSIE'),
#         ('BIT-CT', 'BIT-COMPTECH'),
#         ('BIT-GARMENTS', 'BIT-GARMENTS'),
#         ('BIT-AUTOMOTIVE', 'BIT-AUTOMOTIVE'),
#         ('BIT-DRAFTING', 'BIT-DRAFTING'),
#         ('BIT-ELECTRONICS', 'BIT-ELECTRONICS'),
#         ('BEED','BEED'),
#         ('BSED-MATH','BSED-MATH'),  ('BSED-ENGLISH','BSED-ENGLISH'),
#         ('BTLED','BTLED'),
#         ('BSF','BSF'),
#         ('BSA','BSA'),
#         ('BAL','BAL'),
#         ('BAEL','BAEL'),
#         ('BS-PSYCHOLOGY','BS-PSYCHOLOGY'),
#         ('BSHM','BSHM'),
#         ('BSTM','BSTM'),
#     ], default='')

#     year = models.CharField(max_length=50, choices=[
#         ('1st', '1st'),
#         ('2nd', '2nd'),
#         ('3rd', '3rd'),
#         ('4th', '4th'),
#         ('Irregular', 'Irregular'),
#     ], default='')

#     mobile_number = models.CharField(max_length=15)
#     position = models.CharField(max_length=100)

#     organization = models.ForeignKey(
#         Organization,
#         on_delete=models.CASCADE,
#         related_name="officers"
#     )
#     town_address = models.CharField(max_length=200)
#     home_address = models.CharField(max_length=200)
#     age = models.PositiveIntegerField()
#     place_of_birth = models.CharField(max_length=100)
#     date_of_birth = models.DateField()
#     nationality = models.CharField(max_length=50)
#     civil_status = models.CharField(max_length=10, choices=[
#         ('Single', 'Single'),
#         ('Married', 'Married'),
#         ('Widowed', 'Widowed'),
#         ('Separated', 'Separated'),
#         ('Divorced', 'Divorced'),
#     ])
#     sex = models.CharField(max_length=10, choices=[
#         ('Male', 'Male'),
#         ('Female', 'Female'),
#     ])
#     height = models.FloatField()
#     distinguishing_mark = models.CharField(max_length=200, blank=True, null=True)
#     weight = models.FloatField()
#     hobbies = models.CharField(max_length=200, blank=True, null=True)
#     special_talent = models.CharField(max_length=200, blank=True, null=True)

#     # Parents
#     father_name = models.CharField(max_length=100, blank=True, null=True)
#     father_occupation = models.CharField(max_length=100, blank=True, null=True)
#     father_address = models.CharField(max_length=200, blank=True, null=True)
#     father_mobile_number = models.CharField(max_length=15, blank=True, null=True)
    
#     mother_name = models.CharField(max_length=100, blank=True, null=True)
#     mother_occupation = models.CharField(max_length=100, blank=True, null=True)
#     mother_address = models.CharField(max_length=200, blank=True, null=True)
#     mother_mobile_number = models.CharField(max_length=15, blank=True, null=True)

#     guardian_name = models.CharField(max_length=100, blank=True, null=True)
#     guardian_occupation = models.CharField(max_length=100, blank=True, null=True)
#     guardian_address = models.CharField(max_length=200, blank=True, null=True)
#     guardian_mobile_number = models.CharField(max_length=15, blank=True, null=True)

#     # Educational background
#     tertiary_institution = models.CharField(max_length=200, blank=True, null=True)
#     tertiary_address = models.CharField(max_length=200, blank=True, null=True)
#     tertiary_degree_level = models.CharField(max_length=100, blank=True, null=True)
#     tertiary_date = models.DateField(blank=True, null=True)
    
#     secondary_institution = models.CharField(max_length=200, blank=True, null=True)
#     secondary_address = models.CharField(max_length=200, blank=True, null=True)
#     secondary_degree_level = models.CharField(max_length=100, blank=True, null=True)
#     secondary_date = models.DateField(blank=True, null=True)
    
#     elementary_institution = models.CharField(max_length=200, blank=True, null=True)
#     elementary_address = models.CharField(max_length=200, blank=True, null=True)
#     elementary_degree_level = models.CharField(max_length=100, blank=True, null=True)
#     elementary_date = models.DateField(blank=True, null=True)

#     # Membership in other organizations
#     membership_position1 = models.CharField(max_length=100, blank=True, null=True)
#     membership_organization1 = models.CharField(max_length=200, blank=True, null=True)
#     membership_date1 = models.DateField(blank=True, null=True)
    
#     membership_position2 = models.CharField(max_length=100, blank=True, null=True)
#     membership_organization2 = models.CharField(max_length=200, blank=True, null=True)
#     membership_date2 = models.DateField(blank=True, null=True)
    
#     membership_position3 = models.CharField(max_length=100, blank=True, null=True)
#     membership_organization3 = models.CharField(max_length=200, blank=True, null=True)
#     membership_date3 = models.DateField(blank=True, null=True)
    
#     membership_position4 = models.CharField(max_length=100, blank=True, null=True)
#     membership_organization4 = models.CharField(max_length=200, blank=True, null=True)
#     membership_date4 = models.DateField(blank=True, null=True)
    
#     membership_position5 = models.CharField(max_length=100, blank=True, null=True)
#     membership_organization5 = models.CharField(max_length=200, blank=True, null=True)
#     membership_date5 = models.DateField(blank=True, null=True)

#     # Seminars
#     seminar_title1 = models.CharField(max_length=200, blank=True, null=True)
#     seminar_date1 = models.DateField(blank=True, null=True)
    
#     seminar_title2 = models.CharField(max_length=200, blank=True, null=True)
#     seminar_date2 = models.DateField(blank=True, null=True)
    
#     seminar_title3 = models.CharField(max_length=200, blank=True, null=True)
#     seminar_date3 = models.DateField(blank=True, null=True)
    
#     seminar_title4 = models.CharField(max_length=200, blank=True, null=True)
#     seminar_date4 = models.DateField(blank=True, null=True)
    
#     seminar_title5 = models.CharField(max_length=200, blank=True, null=True)
#     seminar_date5 = models.DateField(blank=True, null=True)

#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('declined', 'Declined'),
#     ]
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')


#     def __str__(self):
#         return f"{self.surname}, {self.firstname} {self.middlename}"
class Adviser(models.Model):
    adviser_id = models.AutoField(primary_key=True)
    profile_picture = models.FileField(upload_to='Adviser_Profile/', validators=[validate_file_extension])
    surname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=50)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="advisers"
    )
    POSITION_CHOICES = [
        ('Main', 'Main Adviser'),
        ('Assistant', 'Assistant Adviser'),
    ]
    
    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        default='Main',
        verbose_name="Adviser Position"
    )
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    civil_status = models.CharField(max_length=10, choices=[
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
        ('Divorced', 'Divorced'),
    ])
    nationality = models.CharField(max_length=50)
    town_address = models.CharField(max_length=190)
    home_address = models.CharField(max_length=190)
    cell_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ], default='pending')
    date_deactivated = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Date Deactivated",
        help_text="The date the adviser was set to inactive. If blank, they are active."
    )
    def __str__(self):
        return f"{self.surname}, {self.firstname} {self.middlename or ''}"
    @property
    def is_active(self):
        """Returns True if the adviser is active (date_deactivated is empty)."""
        return self.date_deactivated is None

class AdviserEducation(models.Model):
    education_id = models.AutoField(primary_key=True)
    adviser = models.ForeignKey(Adviser, on_delete=models.CASCADE, related_name="educations")
    institution = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    degree_level = models.CharField(max_length=100)
    year_graduated = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.institution} - {self.degree_level} ({self.year_graduated})"
class AdviserWorkExperience(models.Model):
    work_id = models.AutoField(primary_key=True)
    adviser = models.ForeignKey(Adviser, on_delete=models.CASCADE, related_name="work_experiences")
    institution = models.CharField(max_length=255)
    position = models.CharField(max_length=150)
    work_period = models.CharField(max_length=100)  # ex: "2018-2021" or "Jan 2020 - Dec 2022"

    def __str__(self):
        return f"{self.position} at {self.institution} ({self.work_period})"


class AdviserOrganization(models.Model):
    org_id = models.AutoField(primary_key=True)
    adviser = models.ForeignKey(Adviser, on_delete=models.CASCADE, related_name="organizations")
    org_name = models.CharField(max_length=255)
    org_position = models.CharField(max_length=150)
    org_period = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.org_name} - {self.org_position} ({self.org_period})"


class AdviserAdvisory(models.Model):
    advisory_id = models.AutoField(primary_key=True)
    adviser = models.ForeignKey(Adviser, on_delete=models.CASCADE, related_name="advisories")
    advisory_name = models.CharField(max_length=255)
    inclusive_period = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.advisory_name} ({self.inclusive_period})"
class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    objective = models.CharField(max_length=255)
    activities = models.TextField()
    
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)  #
    

    target_choices = [
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
    ]
    target = models.CharField(max_length=2, choices=target_choices)
    involved_officer = models.CharField(max_length=100)
    p_budget = models.DecimalField(max_digits=15, decimal_places=2, default='0')
    expected_output = models.TextField()
    actual_accomplishment = models.FileField(upload_to='projects/', validators=[validate_file_extension])
    remarks = models.TextField()

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.objective

class FinancialStatement(models.Model):
    financial_id = models.AutoField(primary_key=True)
    date = models.DateField()
    purpose = models.CharField(max_length=255)
    source_of_funds = models.CharField(max_length=255)
    
    org = models.ForeignKey(
    Organization, 
    on_delete=models.SET_NULL,  # Keeps statement if org is deleted
    null=True,                 # Allows the field to be empty
    related_name="financial_statements"
)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    remarks = models.TextField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.date} - {self.purpose}"

 

from django.db import models

class Accreditation(models.Model):
    accreditation_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        'Organization',  # links to your Organization model
        on_delete=models.CASCADE,
        related_name='accreditations'
    )

    letter_of_intent = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    list_of_officers = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    certificate_of_registration = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    
    list_of_members = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    accomplishment_report = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    calendar_of_activities = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    financial_statement = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    bank_passbook = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    inventory_of_properties = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    organization_bylaws = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    faculty_adviser_appointment = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])
    other_documents = models.FileField(upload_to='accreditation/', validators=[validate_file_extension])

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.organization.name} Accreditation"

class AccreditationOfficer(models.Model):
    officer_id = models.AutoField(primary_key=True)
    accreditation = models.ForeignKey(
        Accreditation, on_delete=models.CASCADE, related_name="officers"
    )
    officer_name = models.CharField(max_length=255)
    officer_position = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.officer_name} - {self.officer_position}"


class AccreditationMember(models.Model):
    member_id = models.AutoField(primary_key=True)
    accreditation = models.ForeignKey(
        Accreditation, on_delete=models.CASCADE, related_name="members"
    )
    member_name = models.CharField(max_length=255)

    def __str__(self):
        return self.member_name
# class OfficerLogin(models.Model):
#     student_id = models.IntegerField(primary_key=True)
    
#     student_lname = models.CharField(max_length=100, blank=False, null=False)
#     student_fname = models.CharField(max_length=100, blank=False, null=False)
#     student_mname = models.CharField(max_length=100, blank=False, null=False)
#     course = models.CharField(max_length=50, choices=[
#         ('BSIT', 'BSIT'),
#         ('BSIE', 'BSIE'),
#         ('BIT-CT', 'BIT-COMPTECH'),
#         ('BIT-GARMENTS', 'BIT-GARMENTS'),
#         ('BIT-AUTOMOTIVE', 'BIT-AUTOMOTIVE'),
#         ('BIT-DRAFTING', 'BIT-DRAFTING'),
#         ('BIT-ELECTRONICS', 'BIT-ELECTRONICS'),
#         ('BEED','BEED'),
#         ('BSED-MATH','BSED-MATH'),
#         ('BTLED','BTLED'),
#         ('BSF','BSF'),
#         ('BSA','BSA'),
#         ('BAL','BAL'),
#         ('BAEL','BAEL'),
#         ('BS-PSYCHOLOGY','BS-PSYCHOLOGY'),
#         ('BSHM','BSHM'),
#         ('BSTM','BSTM'),
#     ], default='')
    
#     officer_position = models.CharField(max_length=200, blank=False, null=False)
#     ORG_CHOICES = [
#         ('SSG', 'SSG'),
#         ('FSTLP', 'FSTLP'),
#         ('SI++', 'SI++'),
#         ('THE EQUATIONERS', 'THE EQUATIONERS'),
#         ('TECHNOCRATS', 'TECHNOCRATS'),
#     ]
#     organization = models.CharField(max_length=20, choices=ORG_CHOICES)
#     year_lvl = models.CharField(
#         max_length=10,
#         choices=[
#             ('1st', '1st'),
#             ('2nd', '2nd'),
#             ('3rd', '3rd'),
#             ('4th', '4th'),
#             ('Irregular', 'Irregular'),
#         ],
#         blank=False,
#         null=False
#     )
#     username = models.CharField(max_length=100, unique=True, null=False, blank=False)
#     password = models.CharField(max_length=128, null=False, blank=False)

#     def __str__(self):
#         return f"OfficerLogin {self.student_id}"

# class AdminLogin(models.Model):
#     admin_id = models.AutoField(primary_key=True)
#     admin_username = models.CharField(max_length=50, null=False, blank=False)
#     admin_password = models.CharField(max_length=128, null=False, blank=False)

#     def __str__(self):
#         return f"Adminlogin {self.admin_id}"
    

