import csv
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist as ObjException
from django.contrib import messages
from datetime import datetime
from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt
from ..models import ( SeminarAttendance, TransactionReport, StudentUser, 
                     JobPlacementAdminUser, Seminar, OJTCompany, OJTStudent,
                     OJTRequirements,
                    )
from ..forms import ( SeminarForm, SeminarAttendanceForm, TransactionForm, 
                    AdminLoginForm,  AdminSignUpForm,  # StudentSignUpForm, StudentLoginForm,
                    OjtHiringForm, OJTStudentForm, EmailAuthenticationForm, 
                    OJTRequirementsForm, StatusWidget, ScrapperFile
                    )

# Seminar Attendance AJAX post request
import json
from django.http import JsonResponse
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db import transaction
import os
import time
# autogenerate requirements
from docx import Document
from io import BytesIO
from zipfile import ZipFile
from django.http import FileResponse, Http404
ojtrequirements_application_letter = './media/templates/ojt_requirements/application_letter.docx'
ojtrequirements_biodata = './media/templates/ojt_requirements/biodata.docx'
ojtrequirements_endorsement_letter = './media/templates/ojt_requirements/endorsement_letter.docx'
ojtrequirements_medical = './media/templates/ojt_requirements/medical_clearance.docx'
ojtrequirements_moa = './media/templates/ojt_requirements/moa.docx'
ojtrequirements_template_output_path = './media/templates/ojt_requirements/generated'
from mainpage.decorators.decorators import sao_admin_required

def get_user_backend(user):
    if isinstance(user, JobPlacementAdminUser):
        return 'jobplacement.auth_backends.AdminUserBackend'
    elif isinstance(user, StudentUser):
        return 'jobplacement.auth_backends.StudentUserBackend'
    return None
#deleteable
from django.contrib.auth.hashers import check_password


# GI COMMENT KAY DILI NA JOBPLACEMENT GA HANDLE SA STUDENT LOGIN/SIGN UP

# @login_required(login_url='jobplacement:admin_login')
# def student_signup_view(request):
#     if not (request.user.is_staff or request.user.is_superuser):
#         messages.info(request, 'Must be a superuser to access page')
#         return redirect('jobplacement:admin_login')

#     page = 'student_signup'
#     if request.method == 'POST':
#         form = StudentSignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             backend = get_user_backend(user)
#             return redirect('jobplacement:home') 
#         else:
#             messages.error(request, 'There was an error with your sign-up.')
#     else:
#         form = StudentSignUpForm()
#     return render(request, 'jobplacement/student_login.html', {'form': form, 'page': page})

# def student_login(request):
#     page = 'student_login'
#     form = EmailAuthenticationForm()

#     if request.method == 'POST':
#         form = EmailAuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=email, password=password)
#             if user is not None and isinstance(user, StudentUser):
#                 login(request, user)
#                 return redirect('jobplacement:home')  # Student dashboard URL
#             else:
#                 messages.error(request, 'Invalid email or password')
#         else:
#             messages.error(request, 'Invalid email or password')
#     else:
#         form = EmailAuthenticationForm()
#     return render(request, 'jobplacement/student_login.html', {'form': form, 'page': page})

# Create your views here.

def get_user_backend(user):
    if isinstance(user, JobPlacementAdminUser):
        return 'jobplacement.auth_backends.AdminUserBackend'
    elif isinstance(user, StudentUser):
        return 'jobplacement.auth_backends.StudentUserBackend'
    return None

@login_required(login_url='jobplacement:admin_login')
def admin_signup_view(request):
    if not request.user.is_superuser:
        messages.info(request, 'Must be a superuser to access page')
        return redirect('jobplacement:admin_login')

    page = "admin_signup"
    if request.method == 'POST':
        form = AdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend = get_user_backend(user)
            # login(request, user, backend=backend)
            log_activity (
                user=user,
                action="Admin Signup",
                )
            messages.success(request, 'Successfully register admin')
            return redirect('jobplacement:home') 
        else:
            messages.error(request, "Form invalid")
    else:
        form = AdminSignUpForm()
    return render(request, 'jobplacement/admin_login.html', {'form': form, 'page':page})

# end of deletables\

def admin_student(request):
    return render(request, 'jobplacement/admin_and_student.html', {})

def admin_login(request):
    page='admin_login'
    form = AdminLoginForm()
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_staff:
                backend = get_user_backend(user)
                login(request, user, backend=backend)
                return redirect('jobplacement:home')
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Invalid email or password')
    else:
        form = AdminLoginForm()
    return render(request, 'jobplacement/signin.html', {'page':page, 'form':form})

def logout_user(request):
    logout(request)
    return redirect('jobplacement:admin_student')

# @login_required(login_url='jobplacement:admin_student')
def mainpage(request):
    return redirect('jobplacement:ojt_hiring')

#   OJT HIRING THINGS
# @login_required(login_url='jobplacement:admin_student')
def ojt_hiring(request): # ojthiring main page
    ojt_hiring_form = OjtHiringForm()
    ojt_assign_form = OJTStudentForm()
    ojt_hiring = OJTCompany.objects.all()

    if request.method == 'POST':
        if not (request.user.is_staff or request.user.is_superuser):
            messages.info(request, 'Must be staff/admin to access page')
            return redirect('jobplacement:admin_login')
        
        if not (isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser ):
            messages.info(request, 'Must be Jobplacement staff/admin to access page')
            return redirect('jobplacement:admin_login')
            
        form = OjtHiringForm(request.POST)
        if form.is_valid():
            newojt = form.save(commit=False)
            newojt.save()
            messages.success(request, "New OJT Hiring created successfully!")
            log_activity(request.user, "Created new OJT hiring")  # Log the activity
            return render(request, 'jobplacement/ojthiring.html', {'form': ojt_hiring_form, 'ojt_list':ojt_hiring, 'assign_form':ojt_assign_form} )
        else:
            messages.error(request, "Form invalid")

    context = {'form': ojt_hiring_form, 'ojt_list':ojt_hiring, 'assign_form':ojt_assign_form}
    return render(request, 'jobplacement/ojthiring.html', context)

@login_required(login_url='jobplacement:admin_login')
def ojt_assign_student(request): # handle assigning student to company
    if not (request.user.is_staff or request.user.is_superuser): # prevent student/alien access
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')
    
    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')    
    
    if request.method == 'POST':
        try:
            new_ojt = OJTStudentForm(request.POST)
            student_id = request.POST.get('studID')
            company_id = request.POST.get('company_id')
            endorser = request.POST.get('endorser_name')
            endorser_num = request.POST.get('endorser_num')
            endorser_email = request.POST.get('endorser_email')
            endorser_program = request.POST.get('endorser_program')
            duration = request.POST.get("duration")
            params = {
                'endorser_name': endorser,
                'endorser_num': endorser_num,
                'endorser_email': endorser_email,
                'endorser_program': endorser_program,
            }
        except:
            messages.error(request, "Error: Form incomplete")

        # get student and company instance
        try:
            student = StudentUser.objects.get(studID = student_id)
            company = OJTCompany.objects.get(company_id = company_id)
        except ObjException as e:
            messages.error(request, f"{e}")

        # check if there are slots
        n_hired = OJTStudent.objects.filter(company_id = company).count()
        allowed_slots = company.number_of_slots - n_hired
        if allowed_slots >= 1:
            try:
                new_ojt = new_ojt.save(commit=False)
                new_ojt.student_id = student
                new_ojt.company_id = company
                new_ojt.save()
                messages.success(request, "Student assigned successfully")
                log_activity(user=request.user, action=f"Assigned {student.firstname} {student.lastname} to  {company.company_name}")

                #generate requirements
                # Application Letter
                gen_application_letter(ojtrequirements_application_letter, ojtrequirements_template_output_path, student_id, company_id)

                # Biodata
                gen_biodata(ojtrequirements_biodata, ojtrequirements_template_output_path, student_id, company_id)
                # endorsement letter
                gen_endorsement_letter(ojtrequirements_endorsement_letter, ojtrequirements_template_output_path, student_id, company_id, duration, **params)

                # Medical
                gen_medical(ojtrequirements_medical, ojtrequirements_template_output_path, student_id)

                # MOA
                gen_moa(ojtrequirements_moa, ojtrequirements_template_output_path, student_id=student_id, duration=duration, **params)
                
                # non disclosure
                return redirect('jobplacement:ojt_requiremets_download')

            except:
                messages.error(request, "Failed to assign student")
        else:
            messages.error(request, "There are no slots left")

    return redirect('jobplacement:ojt_hiring')

@login_required(login_url='jobplacement:admin_login')
def ojthiring_delete(request, id):
    if not (request.user.is_staff or request.user.is_superuser):  # prevent student access
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')
    
    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')    

    try:
        company = OJTCompany.objects.get(company_id=id)
        company.delete()
    except Exception as e:
        messages.error(request, "Cannot delete company: There are students assigned to this company")
    
    return redirect('jobplacement:ojt_hiring')

@login_required(login_url='jobplacement:admin_login')
def ojt_hiring_info(request, id):   # ojt company page
    if not (request.user.is_staff or request.user.is_superuser):  # prevent student access
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')
    
    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')    

    ojt = OJTCompany.objects.get(company_id = id)
    hiredStudents = OJTStudent.objects.filter(company_id__company_id=id)
    if request.method == 'POST':
        stud_id = request.POST.get('stud_id')

        student_obj = StudentUser.objects.get(studID = stud_id)
        existing_ojt = OJTStudent.objects.filter(student__studID=stud_id).last()
        if existing_ojt is None:
            form = OJTStudentForm(request.POST)
            if form.is_valid():
                newhired = form.save(commit=False)
                newhired.student = student_obj
                newhired.save()
                messages.success(request, "Student assigned")
            else:
                messages.error(request, "Failed to assign student")
        else:
            messages.info(request, "Student already under ojt")
    context = {'hired_students':hiredStudents, 'ojt':ojt}
    return render(request, 'jobplacement/ojthiring_info.html', context)

@login_required(login_url='jobplacement:admin_student')
def ojtRequirements_tracker(request): # ojt requirement tracker page
    req_records = OJTRequirements.objects.all() # show all requirement tracker for admin view
    existing_requirement = None

    # handles search 
    if request.method == 'POST':
        id = request.POST.get('student_id')
        req_records = OJTRequirements.objects.filter(student_id = id)

    # get requirement instance for logged in student    
    try:
        existing_requirement = OJTRequirements.objects.get(student_id=request.user)
        _reqform = OJTRequirementsForm(instance=existing_requirement) # send form for this instance
        stat_widgets = StatusWidget(instance=existing_requirement) # handles form design for requirement status
    except:
        _reqform = OJTRequirementsForm()
        stat_widgets = StatusWidget()

    context = {'form': _reqform, 
               'existing_form':existing_requirement, 
               'status':stat_widgets, 
               'req_records':req_records} #
    return render(request, 'jobplacement/ojt_requirements.html', context)

login_required(login_url='jobplacement:student_login')
def ojt_requirements_submit(request):
    if not isinstance(request.user, StudentUser): # prevent access for unenrolled student
        return redirect('jobplacement:student_login')

    if request.method == 'POST': # handles ojt requirement submission
        if request.user.is_authenticated and isinstance(request.user, StudentUser):
            print(request.user.emailadd, "as Student")
            try:
                existing_requirement = OJTRequirements.objects.get(student_id=request.user, is_valid=True)
                # updates exisiting requirement
                newform = OJTRequirementsForm(request.POST, request.FILES, instance=existing_requirement)
                if newform.is_valid():
                    _req = newform.save(commit=False)
                    _req.student_id = request.user
                    _req.save()
                    messages.success(request, "Form submitted Successfully")
                    log_activity(request.user, "Submitted OJT requirements")

                    return redirect('jobplacement:ojt_requirements_tracker')
                else:
                    messages.error(request, "Form submission unsuccessful")
            except OJTRequirements.DoesNotExist:
                messages.error(request, "OJTRequirement instance does not exist")
                newform = OJTRequirementsForm(request.POST, request.FILES)
                if newform.is_valid():
                    _req = newform.save(commit=False)
                    _req.student_id = request.user
                    _req.save()
                    messages.success(request, "Form submitted Successfully")
                    return redirect('jobplacement:ojt_requirements_tracker')
                else:
                    messages.error(request, "Form submission unsuccessful")
            except:
                # create new requirements
                messages.error(request, "User is not logged in as student")

    return redirect('jobplacement:')
    

@login_required(login_url='jobplacement:admin_login')
def ojt_requirements_accept(request):
    if not (request.user.is_staff or request.user.is_superuser): # allow access to admin and superuser only
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')

    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')    

    if request.method == "POST":
        req_id = request.POST.get('req_id')
        attr_name = request.POST.get('attr_name')
        action = request.POST.get('action')
        try:
            req = OJTRequirements.objects.get(ojt_requirement_id = req_id)
            student = req.student_id
            if action == 'accept':              # Accept Action
                if attr_name == 'nondis':
                    try:
                        req.nondis_stat = OJTRequirements.ACCEPTED
                        req.save()
                        log_activity(request.user, f"Accepted OJT Requirement: NON-DISCLOSURE AGREEMENT of  {student.firstname} {student.lastname}")
                        messages.success(request, "File Accepted")
                    except:
                        messages.error(request, "Action Failed")

                elif attr_name == 'biodata':
                    try:
                        req.biodata_stat = OJTRequirements.ACCEPTED
                        req.save()
                        messages.success(request, "File Accepted")
                        log_activity(request.user, f"Accepted OJT Requirement: BIODATA of  {student.firstname} {student.lastname}")
                    except:
                        messages.error(request, "Action Failed")

                elif attr_name == 'consent':
                    try:
                        req.consent_stat = OJTRequirements.ACCEPTED
                        req.save()
                        log_activity(request.user, f"Accepted OJT Requirement: PARENTS CONSENT of  {student.firstname} {student.lastname}")
                        messages.success(request, "File Accepted")
                    except:
                        messages.error(request, "Action Failed")

                elif attr_name == 'medical':
                    try:
                        req.medical_stat = OJTRequirements.ACCEPTED
                        req.save()
                        log_activity(request.user, f"Accepted OJT Requirement: MEDICAL of  {student.firstname} {student.lastname}")
                        messages.success(request, "File Accepted")
                    except:
                        messages.error(request, "Action Failed")

                elif attr_name == 'apl_letter':
                    try:
                        req.apl_letter_stat = OJTRequirements.ACCEPTED
                        req.save()
                        log_activity(request.user, f"Accepted OJT Requirement: APPLICATION LETTER of  {student.firstname} {student.lastname}")
                        messages.success(request, "File Accepted")
                    except:
                        messages.error(request, "Action Failed")

                elif attr_name == 'moa':
                    try:
                        req.moa_stat = OJTRequirements.ACCEPTED
                        req.save()
                        log_activity(request.user, f"Accepted OJT Requirement: MOA of  {student.firstname} {student.lastname}")
                        messages.success(request, "File Accepted")
                    except:
                        messages.error(request, "Action Failed")

                elif attr_name == 'endorsement':
                    try:
                        req.endorsement_stat = OJTRequirements.ACCEPTED
                        req.save()
                        log_activity(request.user, f"Accepted OJT Requirement: ENDORSEMENT LETTER of  {student.firstname} {student.lastname}")
                        messages.success(request, "File Accepted")
                    except:
                        messages.error(request, "Action Failed")
                
                elif attr_name == 'cert':
                    try:
                        req.cert_stat = OJTRequirements.ACCEPTED
                        req.save()
                        log_activity(request.user, f"Accepted OJT Requirement: CERTIFICATION of  {student.firstname} {student.lastname}")
                        messages.success(request, "File Accepted")
                    except:
                        messages.error(request, "Action Failed")
            elif action == 'declined':             # Delete Action
                if attr_name == 'nondis':
                    req.nondis_stat = OJTRequirements.DECLINED
                    req.non_disclosure.delete()    # delete file and reference in database
                    messages.success(request, "File Declined")
                    log_activity(request.user, f"Declined OJT Requirement: NON-DISCLOSURE AGREEMENT of  {student.firstname} {student.lastname}")
                
                elif attr_name == 'biodata':
                    req.biodata_stat = OJTRequirements.DECLINED
                    req.biodata.delete()
                    messages.success(request, "File Declined")
                    log_activity(request.user, f"Declined OJT Requirement: BIODATA of  {student.firstname} {student.lastname}")
                
                elif attr_name == 'consent':
                    req.consent_stat = OJTRequirements.DECLINED
                    req.parents_consent.delete()
                    messages.success(request, "File Declined")
                    log_activity(request.user, f"Declined OJT Requirement: PARENTS CONSENT of  {student.firstname} {student.lastname}")
                
                elif attr_name == 'medical':
                    req.medical_stat = OJTRequirements.DECLINED
                    req.medical.delete()
                    messages.success(request, "File Declined")
                    log_activity(request.user, f"Declined OJT Requirement: MEDICAL of  {student.firstname} {student.lastname}")
                
                elif attr_name == 'apl_letter':
                    req.apl_letter_stat = OJTRequirements.DECLINED
                    req.application_letter.delete()
                    messages.success(request, "File Declined")
                    log_activity(request.user, f"Declined OJT Requirement: APPLICATION LETTER of  {student.firstname} {student.lastname}")
                
                elif attr_name == 'moa':
                    req.moa_stat = OJTRequirements.DECLINED
                    req.moa.delete()
                    messages.success(request, "File Declined")
                    log_activity(request.user, f"Declined OJT Requirement: MOA of  {student.firstname} {student.lastname}")
                
                elif attr_name == 'endorsement':
                    req.endorsement_stat = OJTRequirements.DECLINED
                    req.endorsement.delete()
                    messages.success(request, "File Declined")
                    log_activity(request.user, f"Declined OJT Letter Requirement: Endorsement Letter of  {student.firstname} {student.lastname}")
                elif attr_name == 'cert':
                    req.cert_stat = OJTRequirements.DECLINED
                    req.certification.delete()
                    messages.success(request, "File Declined")
                    log_activity(request.user, f"Declined OJT Requirement: CERTIFICATION of  {student.firstname} {student.lastname}")
        except:
            messages.error(request, "Requirement instance does not exist")
            return redirect('jobplacement:ojt_requirements_tracker')

    return redirect('jobplacement:ojt_requirements_tracker')


# SEMINAR THINGS
# @login_required(login_url='jobplacement:admin_student')
def seminar(request): # seminar page

    seminars = Seminar.objects.all()
    form = SeminarForm()

    # handle seminar creation
    if request.method == 'POST':
        if not (request.user.is_staff or request.user.is_superuser):  # prevent student access
            messages.info(request, 'Must be staff/admin to access page')
            return redirect('jobplacement:admin_login')

        if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

            messages.info(request, 'Must be Jobplacement staff/admin to access page')
            return redirect('jobplacement:admin_login')    

        form = SeminarForm(request.POST, request.FILES)
        if form.is_valid():
            newseminar = form.save(commit=False)
            newseminar.save()
            log_activity(request.user, f"Scheduled new seminar: {newseminar.title}")
            return redirect('jobplacement:seminar_page')
            
    context = {'seminars':seminars, 'form':form}
    return render(request, 'jobplacement/seminar_page.html', context)

# @login_required(login_url='jobplacement:admin_login')
def seminar_delete(request, id):
    if not (request.user.is_staff or request.user.is_superuser):  # prevent student access
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')

    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')  
          
    seminar = Seminar.objects.get(seminar_id=id)
    seminar.delete()
    return redirect('jobplacement:seminar_page')

# @login_required(login_url='jobplacement:admin_login')
def manage_attendance(request, id): # seminar attendance page
    if not (request.user.is_staff or request.user.is_superuser): # prevent student/alien access
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')

    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')    
    
    sem_form = SeminarAttendanceForm()
    attendance = SeminarAttendance.objects.filter(seminar_id__seminar_id=id, ispending=True, attended=False)
    present_students = SeminarAttendance.objects.filter(attended=True, seminar_id__seminar_id = id)
    
    print(attendance)
    context = {'attendance':attendance, 'sem_id':id, 'sem_form':sem_form, 'presents':present_students}
    return render(request, 'jobplacement/sem_att_manager.html', context)

# @login_required(login_url='jobplacement:admin_login')
def pend_attendance(request):
    if not request.user.is_authenticated: # prevent alien access
        messages.info(request, 'Must be logged in to access page')
        return redirect('jobplacement:admin_login')
    
    # handles student attendance request
    if request.method == 'POST':
        stud_id = request.POST.get('student_id')
        sem_id = request.POST.get('seminar_id')

        if not stud_id or not sem_id:
            messages.error(request, "Student ID and Seminar ID are required.")
            return redirect('jobplacement:manage_att', sem_id)

        try:
            # Check if the attendance record already exists
            sem_att = SeminarAttendance.objects.get(student_id__studID=stud_id, seminar_id__seminar_id=sem_id)
            sem_att.ispending = True
            sem_att.save()
            messages.success(request, "Attendance updated successfully.")
            log_activity(request.user, "Attendance Updated")
            return redirect('jobplacement:manage_att', id=sem_id)
        except SeminarAttendance.DoesNotExist:
            # If the attendance record does not exist, create a new one
            try:
                student_obj = StudentUser.objects.get(studID=stud_id)
            except StudentUser.DoesNotExist:
                messages.error(request, "Student does not exist.")
                return redirect('jobplacement:manage_att', id=sem_id)
            try:
                seminar_obj = Seminar.objects.get(seminar_id=sem_id)
            except Seminar.DoesNotExist:
                messages.error(request, "Seminar does not exist.")
                return redirect('jobplacement:manage_att', id=sem_id)

            try:
                SeminarAttendance.objects.create(
                    student_id=student_obj,
                    seminar_id=seminar_obj,
                    ispending=True
                )
                log_activity(request.user, "New attendance recorded")
                messages.success(request, "New attendance recorded successfully.")
                return redirect('jobplacement:manage_att', id=sem_id)
            except Exception as e:
                messages.error(request, f"Error creating new attendance: {e}")
                return redirect('jobplacement:manage_att', id=sem_id)

    return redirect('jobplacement:home')

# @login_required(login_url='jobplacement:admin_login')
def cancel_pending(request, id): # handles attendance request cancel
    if not (request.user.is_staff or request.user.is_superuser):
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')    
    
    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')        
    
    if request.method == 'POST':
        try:
            att = SeminarAttendance.objects.get(sem_at_id = id)
            att.ispending = False
            att.save()
            return redirect('jobplacement:manage_att', id=att.seminar_id.seminar_id)
        except ObjException:
            messages.error(request, "Object does not exist")
        return redirect('jobplacement:home')

@csrf_exempt
@login_required(login_url='jobplacement:admin_login')
def attend_all_pending(request, id): # handle attend all button
    if not (request.user.is_staff or request.user.is_superuser): # prevent student/alien access
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')
     
    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')    
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Datas: {data}")
            for item in data:
                print(f"Item: {item}")
                sem_id = item.get('sem_att_id')
                print(f"sem_id: {sem_id}")
                att_li = SeminarAttendance.objects.get(sem_at_id = sem_id, ispending=True, attended=False)
                att_li.ispending = False
                att_li.attended = True
                att_li.save()
                
        except SeminarAttendance.DoesNotExist:
            print("Seminar Attendance does not exist")
            return JsonResponse({"error": "Seminar Attendance id does not exist"})
        except Exception as e:
            print(e)
            return JsonResponse({"error": "Failed to mark student attendance"})

        return JsonResponse({"success": "Attendance all successful"})
    return redirect('jobplacement:manage_att', id=id)

    # NON-ACADEMIC AWARD ISSUANCE
@login_required(login_url='jobplacement:admin_login')
def non_acad_page(request):
    if not (request.user.is_staff or request.user.is_superuser): # prevent student/alien access
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')
    
    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')    
    
    def fill_placeholders(doc, data): # replace placeholders from template
        for p in doc.paragraphs:
            for key, value in data.items():
                if key in p.text:
                    inline = p.runs
                    for item in inline:
                        if key in item.text:
                            item.text = item.text.replace(key, value)

    def generate_document(template_path, output_path, data): # generate document for student
        try:
            doc = Document(template_path)
            fill_placeholders(doc, data)
            doc.save(output_path)
            # messages.success(request, "Successfully generated Docs")
        except:
            messages.error(request, "Failed to generate Docs")

    # Processes Non-Academic Award
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_id')
            student = StudentUser.objects.get(studID = student_id)
            date_issued_str = request.POST.get('date_issued')
        except: 
            messages.error(request, "failed to get inputs")
            
        # Default value if date_issued_str is None or empty
        default_date = datetime.now()   

        # Parse the date string if it's not None or empty, else use the default date
        if date_issued_str:
            date_issued = datetime.strptime(date_issued_str, '%Y-%m-%d').date()
        else:
            date_issued = default_date        

        formatted_date_issued = date_issued.strftime('%B %d, %Y')
        award = request.POST.get('award', '').strip()
        program = request.POST.get('program', '').strip().upper()

        achievement = request.POST.get('achievement')
        try:
            print('generating data')
            data = {
                '[date_given]': formatted_date_issued,
                '[firstname]': student.firstname,
                '[lastname]': student.lastname,

                # OJT
                '[position]': request.POST.get('position'),
                '[company]': request.POST.get('company_name'),
                '[company_address]': request.POST.get('company_address'),

                # CAPSTONE
                '[capstone_title]': request.POST.get('capstone_title'),

                # Leadership
                '[academic_year]': request.POST.get('acad_year'),

                # Research Fields
                '[research_title]': request.POST.get('research_title'),

                # Others
                '[achievement]': f"{achievement.upper()}",

            }
        except:
            messages.error(request, "Error in datas")

        try: 
            print(f'{program}')
            print(f'{award}')
            print(f"COED:{program == 'COED'}, {award == 'Researcher of the Year'}")

            if program == 'AGRICULTURE' and award == 'Leadership Award':
                template_path = './media/templates/non_academic_awards/AGRICULTURE/leadership_award_AGRICULTURE.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_Leadership_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_Leadership_Award.docx'
                    log_activity(user=request.user, action=f"Issued Leadership Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'AGRICULTURE' and award == 'Social Responsibility and Civic Engangement Award':
                
                template_path = './media/templates/non_academic_awards/AGRICULTURE/social_responsibility_and_civic_engangement_award_AGRICULTURE.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_Social_Responsibility_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_Social_Responsibility_Award.docx'
                    log_activity(user=request.user, action=f"Issued Social Responsibility and Civic Engangement Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'AGRICULTURE' and award == 'Others':
                
                template_path = './media/templates/non_academic_awards/AGRICULTURE/new_achievement_AGRICULTURE.docx'
                output_path = f"./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_{achievement}_Award.docx"
                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_{achievement}_Award.docx'
                    log_activity(user=request.user, action=f"Issued Social {achievement} Award to {student.firstname} {student.lastname}")
                    return response
        
            elif program == 'BIT' and award == 'Best OJT Award':
                template_path = './media/templates/non_academic_awards/BIT/best_OJT_awards_BIT.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_best_OJT_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_best_OJT_award.docx'
                    log_activity(user=request.user, action=f"Issued Best OJT Award to {student.firstname} {student.lastname}")
                    return response
            
            elif program == 'BIT' and award == 'Researcher of the Year':
                template_path = './media/templates/non_academic_awards/BIT/researcher_of_the_year_award_BIT.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_researcher_of_the_year_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_researcher_of_the_year_award.docx'
                    log_activity(user=request.user, action=f"Issued Researcher of the year Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'BIT' and award == 'Others':
                
                template_path = './media/templates/non_academic_awards/BIT/new_achievement_BIT.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_{achievement}_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_{achievement}_Award.docx'
                    log_activity(user=request.user, action=f"Issued {achievement} Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'BES' and award == 'Leadership Award':
                template_path = './media/templates/non_academic_awards/BES/leadership_award_ENVIRONMENTAL_SCIENCE.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_leadership_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_leadership_award.docx'
                    log_activity(user=request.user, action=f"Issued Leadership Award to {student.firstname} {student.lastname}")
                    return response
        
            elif program == 'BES' and award == 'Others':
                
                template_path = './media/templates/non_academic_awards/BES/new_achievement_BES.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_{achievement}_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_{achievement}_Award.docx'
                    log_activity(user=request.user, action=f"Issued {achievement} Award to {student.firstname} {student.lastname}")
                    return response
        
            elif program == 'BSHM' and award == 'Leadership Award':
                template_path = './media/templates/non_academic_awards/BSHM/leadership_award_BSHM.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_leadership_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_leadership_award.docx'
                    log_activity(user=request.user, action=f"Issued Leadership Award to {student.firstname} {student.lastname}")
                    return response
        
            elif program == 'BSHM' and award == 'Others':
                
                template_path = './media/templates/non_academic_awards/BSHM/new_achievement_BSHM.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_{achievement}_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_{achievement}_Award.docx'
                    log_activity(user=request.user, action=f"Issued {achievement} Award to {student.firstname} {student.lastname}")
                    return response
        
            elif program == 'BSIE' and award == 'Leadership Award':
                template_path = './media/templates/non_academic_awards/BSIE/leadership_award_BSIE.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_leadership_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_leadership_award.docx'
                    log_activity(user=request.user, action=f"Issued Leadership Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'BSIE' and award == 'Outstanding Athlete Award':
                template_path = './media/templates/non_academic_awards/BSIE/outstanding_athlete_award_BSIE.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_outstanding_athlete_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_outstanding_athlete_award.docx'
                    log_activity(user=request.user, action=f"Issued Outstanding Athletic Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'BSIE' and award == 'Researcher of the Year':
                template_path = './media/templates/non_academic_awards/BSIE/researcher_of_the_year_award_BSIE.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_researcher_of_the_year_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_researcher_of_the_year_award.docx'
                    log_activity(user=request.user, action=f"Issued Researcher of the year Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'BSIE' and award == 'Others':
                
                template_path = './media/templates/non_academic_awards/BSIE/new_achievement_BSIE.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_{achievement}_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_{achievement}_Award.docx'
                    log_activity(user=request.user, action=f"Issued {achievement} Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'BSIT' and award == 'Best Capstone':
                template_path = './media/templates/non_academic_awards/BSIT/best_capstone_award_BSIT.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_best_capstone_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_best_capstone_award.docx'
                    log_activity(user=request.user, action=f"Issued Best Capstone Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'BSIT' and award == 'Excellence Award':
                template_path = './media/templates/non_academic_awards/BSIT/excellence_award_BSIT.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_excellence_award_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_excellence_award_award.docx'
                    log_activity(user=request.user, action=f"Issued Excellence Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'BSIT' and award == 'Leadership Award':
                template_path = './media/templates/non_academic_awards/BSIT/leadership_award_BSIT.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_leadership_award_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_leadership_award_award.docx'
                    log_activity(user=request.user, action=f"Issued Leadership Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'BSIT' and award == 'Programmer of the Year':
                template_path = './media/templates/non_academic_awards/BSIT/programmer_of_the_year_award_BSIT.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_programmer_of_the_year_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_programmer_of_the_year_award.docx'
                    log_activity(user=request.user, action=f"Issued Programmer of the Year Award to {student.firstname} {student.lastname}")
                    return response
            
            elif program == 'BSIT' and award == 'Others':
                
                template_path = './media/templates/non_academic_awards/BSIT/new_achievement_BSIT.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_{achievement}_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_{achievement}_Award.docx'
                    log_activity(user=request.user, action=f"Issued {achievement} Award to {student.firstname} {student.lastname}")
                    return response
            
            elif program == 'CAS' and award == 'Academic Leadership Award':
                template_path = './media/templates/non_academic_awards/CAS/academic_leadership_award_CAS.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_academic_leadership_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_academic_leadership_award.docx'
                    log_activity(user=request.user, action=f"Issued Academic Leadership Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'CAS' and award == 'BAEL Pride Award':
                template_path = './media/templates/non_academic_awards/CAS/bael_pride_award_CAS.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_bael_pride_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_bael_pride_award.docx'
                    log_activity(user=request.user, action=f"Issued Bael Pride Award to {student.firstname} {student.lastname}")
                    return response
                                
            elif program == 'CAS' and award == 'Leadership Award':
                template_path = './media/templates/non_academic_awards/CAS/leadership_award_CAS.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_leadership_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_leadership_award.docx'
                    log_activity(user=request.user, action=f"Issued Leadership Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'CAS' and award == 'Loyalty Award':
                template_path = './media/templates/non_academic_awards/CAS/loyalty_award_CAS.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_loyalty_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_loyalty_award.docx'
                    log_activity(user=request.user, action=f"Issued Loyalty Award to {student.firstname} {student.lastname}")
                    return response
            
            elif program == 'CAS' and award == 'Outstanding Athlete Award':
                template_path = './media/templates/non_academic_awards/CAS/outstanding_athlete_award_CAS.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_outstanding_athlete_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_outstanding_athlete.docx'
                    log_activity(user=request.user, action=f"Issued Outstanding Athlete Award to {student.firstname} {student.lastname}")
                    return response
        
            elif program == 'CAS' and award == 'Others':
                
                template_path = './media/templates/non_academic_awards/CAS/new_achievement_CAS.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_{achievement}_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_{achievement}_Award.docx'
                    log_activity(user=request.user, action=f"Issued {achievement} Award to {student.firstname} {student.lastname}")
                    return response
        
            elif program == 'COED' and award == 'Best in Elocution Award':
                template_path = './media/templates/non_academic_awards/COED/best_in_elocution_award_COED.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_best_in_elocution_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_best_in_elocution.docx'
                    log_activity(user=request.user, action=f"Issued Best in Elocution Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'COED' and award == 'Leadership Award':
                template_path = './media/templates/non_academic_awards/COED/leadership_award_COED.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_leadership_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_leadership_award.docx'
                    log_activity(user=request.user, action=f"Issued Leadership Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'COED' and award == 'Relentless Mentor of the Year Award':
                template_path = './media/templates/non_academic_awards/COED/relentless_mentor_of_the_year_award_COED.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_relentless_mentor_of_the_year_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_relentless_mentor_of_the_year.docx'
                    log_activity(user=request.user, action=f"Issued Relentles Mentor of the Year Award to {student.firstname} {student.lastname}")
                    return response
            
            elif program == 'COED' and award == 'Researcher of the Year':
                template_path = './media/templates/non_academic_awards/COED/researcher_of_the_year_award_COED.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_researcher_of_the_year_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_researcher_of_the_year.docx'
                    log_activity(user=request.user, action=f"Issued Researcher of the Year Award to {student.firstname} {student.lastname}")
                    return response

            elif program == 'COED' and award == 'Student Extensionista of the Year Award':
                template_path = './media/templates/non_academic_awards/COED/student_extensionista_of_the_year_award_COED.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_student_extensionista_of_the_year_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_student_extensionista_of_the_year.docx'
                    log_activity(user=request.user, action=f"Issued Student Extensionista of the Year Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'COED' and award == 'Others':
                template_path = './media/templates/non_academic_awards/COED/new_achievement_COED.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_{achievement}_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_{achievement}_Award.docx'
                    log_activity(user=request.user, action=f"Issued {achievement} Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'FORESTRY' and award == 'Leadership Award':
                template_path = './media/templates/non_academic_awards/COED/leadership_award_COED.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_leadership_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_leadership_award.docx'
                    log_activity(user=request.user, action=f"Issued Leadership Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'FORESTRY' and award == 'Outstanding Athlete':
                template_path = './media/templates/non_academic_awards/FORESTRY/outstanding_athlete_award_FORESTRY.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_outstanding_athlete_award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_outstanding_athlete_award.docx'
                    log_activity(user=request.user, action=f"Issued Outstanding Athlete Award to {student.firstname} {student.lastname}")
                    return response
                
            elif program == 'FORESTRY' and award == 'Others':
                template_path = './media/templates/non_academic_awards/FORESTRY/new_achievement_FORESTRY.docx'
                output_path = f'./media/templates/non_academic_awards/output/{student.firstname}_{student.lastname}_{achievement}_Award.docx'

                generate_document(template_path, output_path, data)
                print('passed generate document')
                # Optionally return a response with the document, like a download link
                with open(output_path, 'rb') as doc_file:
                    response = HttpResponse(doc_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename={student.firstname}_{student.lastname}_{achievement}_Award.docx'
                    log_activity(user=request.user, action=f"Issued {achievement} Award to {student.firstname} {student.lastname}")
                    return response
        except:
            messages.error(request, "Failed to create achievement")
    context = {}
    return render(request, 'jobplacement/non_academic.html', context)

    # TRANSACTION REPORTS THINGS
def log_activity(user, action): # transaction report auto record
    user_type = 'admin' if user.is_staff else 'student'
    TransactionReport.objects.create(
        user=user,
        action=action,
        date_created=timezone.now(),
        user_type=user_type
    )

@login_required(login_url='jobplacement:admin_login')
def transRep(request): # transaction report page
    if not (request.user.is_staff or request.user.is_superuser): # prevent student/alien access
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')    
    
    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access

        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')    

    form = TransactionForm()
    records = TransactionReport.objects.all()
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M')
    print(f"Date time now: {dt}")
    _monthly = False

    # handle filter function
    if request.method == 'POST':
        monthly_filter = request.POST.get('monthly_filter')
        date_time = request.POST.get('date_time_filter')
        day = month = year = None

        try: 
            date_time = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')
            dt = date_time.strftime('%Y-%m-%dT%H:%M')

            try:
                day = date_time.day
                month = date_time.month
                year = date_time.year
            except:
                messages.error(request, f"Invalid: {day}, {month}, {year}")
        except ValueError:
            messages.error(request, "Invalid date time")
        print(monthly_filter)
        if monthly_filter == 'true':
            print("monthly filter")
            _monthly = True
            records = records.filter(date_created__month = month, date_created__year = year)
        else:
            print("daily filter")
            _monthly = False
            records = records.filter(date_created__month = month, date_created__year=year, date_created__day=day)
    
    context = {'transactions':records, 'date_time':dt,'prev_period':_monthly, 'form':form}
    return render(request, 'jobplacement/trans_report.html', context )

@login_required(login_url='jobplacement:admin_login')
def transRep_print(request): 
    if not (request.user.is_staff or request.user.is_superuser): # prevent student/alien access
        messages.info(request, 'Must be staff/admin to access page')
        return redirect('jobplacement:admin_login')
    
    if not ( isinstance(request.user, JobPlacementAdminUser) or request.user.is_superuser): # prevent other admin access
        messages.info(request, 'Must be Jobplacement staff/admin to access page')
        return redirect('jobplacement:admin_login')    

    records = TransactionReport.objects.all()
    dt = datetime.now().strftime('%B %d, %Y %H:%M:%S')
    filter_type = "None"

    # Print transaction report
    if request.method == 'POST':
        monthly_filter = request.POST.get('period_filter')
        date_time = request.POST.get('date_filter')

        day = month = year = None
        try: 
            date_time = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')

            try:
                day = date_time.day
                month = date_time.month
                year = date_time.year
            except:
                messages.error(request, f"Invalid: {day}, {month}, {year}")
        except ValueError:
            messages.error(request, "Invalid date time")
        
        if monthly_filter == 'True':
            filter_type = "MONTHLY"
            print("monthly filter")
            records = records.filter(date_created__month = month, date_created__year = year)
        else:
            filter_type = "DAILY"
            print("daily filter")
            records = records.filter(date_created__month = month, date_created__year=year, date_created__day=day)

    context = {'transactions':records, 'datetime':dt, 'filter_type':filter_type}
    # return render(request, 'jobplacement/ready_to_print2.html', context)

    html_string = render_to_string('jobplacement/ready_to_print2.html', context)

    base_url = request.build_absolute_uri(os.path.join(os.path.dirname(request.path), 'static'))
    
    pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename="TransactionReport.pdf"'

    return response 

# suggest students with matching query
class search_suggestions(View):
    def get(self, request):
        query = request.GET.get('query', '') # query comes from ajax
        suggestions = []
        if query:
            suggestions = list(StudentUser.objects.filter(
                Q(studID__icontains=query) |
                Q(firstname__icontains = query) |
                Q(lastname__icontains = query)
            ).values_list('studID', 'lastname', 'firstname'))
            return JsonResponse(suggestions, safe=False)

# suggest companies with matching query
class company_suggestions(View):
    print('company suggest')
    def get(self, request):
        query = request.GET.get('query', '') # query comes from ajax
        suggestions = []
        if query:
            suggestions = list(OJTCompany.objects.filter(
                Q(company_id__icontains=query) |
                Q(company_name__icontains = query) |
                Q(owner__icontains = query)
            ).values_list('company_id', 'company_name', 'owner'))
            return JsonResponse(suggestions, safe=False)


@login_required(login_url='jobplacement:admin_login')
def del_ojt(request):
    if OJTRequirements.objects.all().delete():
        messages.success(request, "Clear success")
    else:
        messages.error(request, "Clear failed")
    
    return redirect('jobplacement:home')

# view ojt requirement pdf/image 
@csrf_exempt
def view_pdf(request, id):
    req = OJTRequirements.objects.get(ojt_requirement_id = id)
    pdf = req
    if request.method == 'POST':
        attr_name = request.POST.get('attr_name') 
        
        if attr_name == 'nondis':
            pdf = req.non_disclosure
        elif attr_name == 'biodata':
            pdf = req.biodata
        elif attr_name == 'consent':
            pdf = req.parents_consent
        elif attr_name == 'medical':
            pdf = req.medical
        elif attr_name == 'apl_letter':
            pdf = req.application_letter
        elif attr_name == 'moa':
            pdf = req.moa
        elif attr_name == 'endorsement':
            pdf = req.endorsement
        elif attr_name == 'cert':
            pdf = req.certification

        pdf_data = {
            'url': pdf.url if pdf else None,
            'name': pdf.name if pdf else None,
        }

        return JsonResponse(pdf_data)
    error = {'error': "OJT Requirement NOT Found"}
    return JsonResponse(error)


# generate application letter document
def gen_application_letter(template_path, output_path, student_id, company_id):
    student = StudentUser.objects.get(studID = student_id)
    company = OJTCompany.objects.get(company_id = company_id)
    current_date = datetime.now().strftime("%B %d, %Y")

    th = ""
    if student.yearlvl == 1:
        th = "st"
    elif student.yearlvl == 2:
        th = "nd"
    elif student.yearlvl == 3:
        th = "rd"
    else:
        th = 'th'

    data = {
        '[date]': f"{current_date}",
        '[position]': f"{company.position}",
        '[name_of_company_representative]': f"{company.owner}",
        '[company_name]': f"{company.company_name}",
        '[company_address]': f"{company.address}",
        '[degree_and_year_of_student]': f"{student.program} as {student.yearlvl}{th} student",
        '[contact_number_of_student]': f"{student.contact}",
        '[firstname]': f"{student.firstname}",
        '[lastname]': f"{student.lastname}",
    }
    try:
        doc = Document(template_path)
        for paragraph in doc.paragraphs:
                for key, value in data.items():
                    if key in paragraph.text:
                        paragraph.text = paragraph.text.replace(key, value)
    except:
        print("Failed to generate letter")

    try:
        new_path = os.path.join(output_path, f"{student.lastname}_ApplicationLetter_{current_date}.docx")

        doc.save(new_path)
    except:
        print("failed to save file")

    print("Application Letter Generated")

# generate biodata document
def gen_biodata(template_path, output_path, student_id, company_id):
    print("generating biodata")
    student = StudentUser.objects.get(studID = student_id)
    company = OJTCompany.objects.get(company_id = company_id)
    print(student)
    print(company)
    current_date = datetime.now().strftime("%B %d, %Y")

    try:
        doc = Document(template_path)
        new_path = os.path.join(output_path, f"{student.lastname}_biodata_{current_date}.docx")

        doc.save(new_path)
    except:
        print("failed to save file")

    print("Biodata Generated")

# generate endorsement letter document
def gen_endorsement_letter(template_path, output_path, student_id, company_id, duration, **params):
    print("generating endorsement")
    student = StudentUser.objects.get(studID = student_id)
    company = OJTCompany.objects.get(company_id = company_id)
    current_date = datetime.now().strftime("%B %d, %Y")

    data = {
        '[date]': current_date,
        '[name_of_company_representative]': company.owner,
        '[position]': company.position,
        '[company_name]': company.company_name,
        '[company_address]': company.address,
        '[hours_needed]': duration,
        '[firstname]': student.firstname,
        '[lastname]': student.lastname,
        '[endorser_phonenum]': params.get('endorser_num'),
        '[endorser_email]': params.get('endorser_email'),
        '[endorser_name]': params.get('endorser_name'),
        '[program]': params.get('endorser_program'),
    }
    try:
        print('saving letter')
        doc = Document(template_path)
        for paragraph in doc.paragraphs:
                for key, value in data.items():
                    if key in paragraph.text:
                        paragraph.text = paragraph.text.replace(key, value)
    except:
        print("Failed to generate letter")

    try:
        new_path = os.path.join(output_path, f"{student.lastname}_Endorsement{current_date}.docx")

        doc.save(new_path)
    except:
        print("failed to save file")

    print("Endorsement Generated")

# generate medical document
def gen_medical(template_path, output_path, student_id):
    print('Generating Medical')
    student = StudentUser.objects.get(studID = student_id)
    print(student)
    current_date = datetime.now().strftime("%B %d, %Y")

    try:
        doc = Document(template_path)
        new_path = os.path.join(output_path, f"{student.lastname}_medical_{current_date}.docx")

        doc.save(new_path)
    except:
        print("failed to save file")

    print("Medical Generated")

# generate moa document
def gen_moa(template_path, output_path, student_id, duration, **params):
    print('generating MOA')
    student = StudentUser.objects.get(studID = student_id)
    current_date = datetime.now()
    day = current_date.strftime("%d")
    month = current_date.strftime("%B")
    year = current_date.strftime("%Y")
    date_for_filename = current_date.strftime("%Y%m%d")
    data = {
        '[date]': day,
        '[month]': month,
        '[year]': year,
        '[name_of_coordinator]': params.get('endorser_name'),
        '[firstname]': student.firstname,
        '[lastname]': student.lastname,
        '[degree_program]': student.program,
        '[hours]': duration,
    }
    doc = Document(template_path)
    try:
        print('saving letter')
        doc = Document(template_path)
        for paragraph in doc.paragraphs:
                for key, value in data.items():
                    if key in paragraph.text:
                        paragraph.text = paragraph.text.replace(key, value)
                        print(f"{paragraph.text}: {value}")

        print('updating table')
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for key, value in data.items():
                        if key in cell.text:
                            cell.text = cell.text.replace(key, value)
    except:
        print("Failed to generate letter")

    try:
        new_path = os.path.join(output_path, f"{student.lastname}_MOA_{date_for_filename}.docx")

        doc.save(new_path)
    except:
        print("failed to save file")

    print("MOA Generated")

# zip folder
def zip_files_in_folder(folder_path):
    print("buffing zip folder")
    zip_buffer = BytesIO()
    
    with ZipFile(zip_buffer, 'w') as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))
    
    zip_buffer.seek(0)
    return zip_buffer

# download zip folders
def download_zipped_folder(request, folder_path):
    print("downlodaing zip folder")
    try:
        zip_buffer = zip_files_in_folder(folder_path)
        zip_filename = os.path.basename(folder_path.rstrip('/')) + '.zip'
        
        response = FileResponse(zip_buffer, as_attachment=True, filename=zip_filename)
        
        # Delete files after downloading
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                os.remove(os.path.join(root, file))

        return response
    
    except Exception as e:
        print(f"Failed to zip and download folder: {e}")
        raise Http404("Failed to generate zip file.")

# download zipped folder
def download_zipped_ojt_templates(request):
    print("downloading ojt_templates")
    folder_path = './media/templates/ojt_requirements/generated'
    return download_zipped_folder(request, folder_path)

# as the function name
def file_scrapper(request):
    if request.method == 'POST':
        file = ScrapperFile( request.POST, request.FILES)
        if file.is_valid():
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                StudentUser.objects.create(
                    studID=row['studID'],
                    lrn = row['lrn'],
                    firstname=row['firstname'],
                    lastname= row['lastname'],
                    middlename=row['middlename'],
                    program=row['degree'],
                    yearlvl = row['yearlvl'],
                    sex = row['sex'],
                    email = row['emailadd'],
                    contact = row['contact']
                )

            messages.success(request, "File scrapper success")
            return redirect('jobplacement:home')
        
    else:
        form = ScrapperFile()
    return render(request, 'jobplacement/scrapper.html', {"form":form})