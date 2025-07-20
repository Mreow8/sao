from django.db import models
from ..models import studentInfo 

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

