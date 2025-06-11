from django.db import models
from django.core.exceptions import ValidationError




def validate_file_extension(value):
    valid_extensions = ('.pdf', '.docx', '.jpg', '.jpeg', '.png', '.gif')
    if not value.name.lower().endswith(valid_extensions):
        raise ValidationError('Only .pdf, .docx, .jpg, .jpeg, .png, and .gif files are allowed.')
    
class Officer(models.Model):
    Officer_profile_picture =models.FileField(upload_to='Officer_Profile/', validators=[validate_file_extension])
    surname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100)

    course = models.CharField(max_length=50, choices=[
        ('BSIT', 'BSIT'),
        ('BSIE', 'BSIE'),
        ('BIT-CT', 'BIT-COMPTECH'),
        ('BIT-GARMENTS', 'BIT-GARMENTS'),
        ('BIT-AUTOMOTIVE', 'BIT-AUTOMOTIVE'),
        ('BIT-DRAFTING', 'BIT-DRAFTING'),
        ('BIT-ELECTRONICS', 'BIT-ELECTRONICS'),
        ('BEED','BEED'),
        ('BSED-MATH','BSED-MATH'),
        ('BTLED','BTLED'),
        ('BSF','BSF'),
        ('BSA','BSA'),
        ('BAL','BAL'),
        ('BAEL','BAEL'),
        ('BS-PSYCHOLOGY','BS-PSYCHOLOGY'),
        ('BSHM','BSHM'),
        ('BSTM','BSTM'),
    ], default='')

    year = models.CharField(max_length=50, choices=[
        ('1st', '1st'),
        ('2nd', '2nd'),
        ('3rd', '3rd'),
        ('4th', '4th'),
        ('Irregular', 'Irregular'),
    ], default='')

    mobile_number = models.CharField(max_length=15)
    position = models.CharField(max_length=100)

    organization = models.CharField(max_length=30, choices=[
        ('SSG', 'SSG'),
        ('FSTLP', 'FSTLP'),
        ('SI++', 'SI++'),
        ('THE EQUATIONERS', 'THE EQUATIONERS'),
        ('TECHNOCRATS', 'TECHNOCRATS'),
    ])
    
    town_address = models.CharField(max_length=200)
    home_address = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    place_of_birth = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=50)
    civil_status = models.CharField(max_length=10, choices=[
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
        ('Divorced', 'Divorced'),
    ])
    sex = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
    ])
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
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')


    def __str__(self):
        return f"{self.surname}, {self.firstname} {self.middlename}"
    
class Adviser(models.Model):
    Adviser_profile_picture = models.FileField(upload_to='Adviser_Profile/', validators=[validate_file_extension])
    surname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100)
    department = models.CharField(max_length=50, choices=[
        ('BSIT', 'BSIT'),
        ('BSIE', 'BSIE'),
        ('BIT', 'BIT'),
    ], default='')
    ORG_CHOICES = [
        ('SSG', 'SSG'),
        ('FSTLP', 'FSTLP'),
        ('SI++', 'SI++'),
        ('THE EQUATIONERS', 'THE EQUATIONERS'),
        ('TECHNOCRATS', 'TECHNOCRATS'),
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
    sex = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female')
    ])
    civil_status = models.CharField(max_length=10, choices=[
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
        ('Divorced', 'Divorced')
    ])
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
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    
    def __str__(self):
        return f"{self.surname}, {self.firstname} {self.middlename}"

    
class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    objective = models.CharField(max_length=255)
    activities = models.TextField()
    
    org_choices = [
        ('SSG', 'SSG'),
        ('FSTLP', 'FSTLP'),
        ('SI++', 'SI++'),
        ('THE EQUATIONERS', 'THE EQUATIONERS'),
        ('TECHNOCRATS', 'TECHNOCRATS'),
    ]
    org = models.CharField(max_length=15, choices=org_choices, default='')

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
    
    org_choices = [
        ('SSG', 'SSG'),
        ('FSTLP', 'FSTLP'),
        ('SI++', 'SI++'),
        ('THE EQUATIONERS', 'THE EQUATIONERS'),
        ('TECHNOCRATS', 'TECHNOCRATS'),
    ]
    org = models.CharField(max_length=15, choices=org_choices, default='')

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

 
    
class Accreditation(models.Model):
    ORG_CHOICES = [
        ('SSG', 'SSG'),
        ('FSTLP', 'FSTLP'),
        ('SI++', 'SI++'),
        ('THE EQUATIONERS', 'THE EQUATIONERS'),
        ('TECHNOCRATS', 'TECHNOCRATS'),
    ]
    
    accreditation_id = models.AutoField(primary_key=True)
    organization = models.CharField(max_length=20, choices=ORG_CHOICES)

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
        return f"Accreditation {self.accreditation_id} - {self.organization}"

class OfficerLogin(models.Model):
    student_id = models.IntegerField(primary_key=True)
    
    student_lname = models.CharField(max_length=100, blank=False, null=False)
    student_fname = models.CharField(max_length=100, blank=False, null=False)
    student_mname = models.CharField(max_length=100, blank=False, null=False)
    course = models.CharField(max_length=50, choices=[
        ('BSIT', 'BSIT'),
        ('BSIE', 'BSIE'),
        ('BIT-CT', 'BIT-COMPTECH'),
        ('BIT-GARMENTS', 'BIT-GARMENTS'),
        ('BIT-AUTOMOTIVE', 'BIT-AUTOMOTIVE'),
        ('BIT-DRAFTING', 'BIT-DRAFTING'),
        ('BIT-ELECTRONICS', 'BIT-ELECTRONICS'),
        ('BEED','BEED'),
        ('BSED-MATH','BSED-MATH'),
        ('BTLED','BTLED'),
        ('BSF','BSF'),
        ('BSA','BSA'),
        ('BAL','BAL'),
        ('BAEL','BAEL'),
        ('BS-PSYCHOLOGY','BS-PSYCHOLOGY'),
        ('BSHM','BSHM'),
        ('BSTM','BSTM'),
    ], default='')
    
    officer_position = models.CharField(max_length=200, blank=False, null=False)
    ORG_CHOICES = [
        ('SSG', 'SSG'),
        ('FSTLP', 'FSTLP'),
        ('SI++', 'SI++'),
        ('THE EQUATIONERS', 'THE EQUATIONERS'),
        ('TECHNOCRATS', 'TECHNOCRATS'),
    ]
    organization = models.CharField(max_length=20, choices=ORG_CHOICES)
    year_lvl = models.CharField(
        max_length=10,
        choices=[
            ('1st', '1st'),
            ('2nd', '2nd'),
            ('3rd', '3rd'),
            ('4th', '4th'),
            ('Irregular', 'Irregular'),
        ],
        blank=False,
        null=False
    )
    username = models.CharField(max_length=100, unique=True, null=False, blank=False)
    password = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return f"OfficerLogin {self.student_id}"

class AdminLogin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_username = models.CharField(max_length=50, null=False, blank=False)
    admin_password = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return f"Adminlogin {self.admin_id}"
    

