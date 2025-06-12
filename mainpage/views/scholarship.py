from collections import defaultdict
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import LiquidationTDP, studentInfo, scholars, Requirement, applicants,SemesterDetails, AdminRequest,tesDisbursement,tdpDisbursement
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..forms import RequirementForm, applicantsForm, AdminRequestForm
from django.http import HttpResponse
from django.db.models import Q
from django.db.models import Sum
from django.shortcuts import render
from django.db.models import Sum
from django.db import transaction
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# @login_required
def adminhome(request):
    return render(request, 'adminhome.html', {})

def studenthome(request):
    user = request.user
    print(user)
    try:
        student = studentInfo.objects.get(studID=user.username)
        is_scholar = scholars.objects.filter(studID=student).exists()
    except studentInfo.DoesNotExist:
        student = None
        is_scholar = False

    context = {
        'student': student,
        'is_scholar': is_scholar
    }
    return render(request, 'studenthome.html', context)

def logoutuser(request):
    logout(request)
    return redirect('signinuser')

def signupuser(request):
    error_message = None
    success_message = None

    if request.method == 'POST':
        studentID = request.POST.get('studID')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        try:
            student = studentInfo.objects.get(studID=studentID)
        except studentInfo.DoesNotExist:
            error_message = 'Invalid student ID.'

        if not error_message:
            if cpassword != password:
                error_message = 'Passwords do not match.'
            elif len(password) < 8:
                error_message = 'Password must be at least 8 characters.'
            elif User.objects.filter(username=studentID).exists():
                error_message = 'Student ID already exists.'
            elif User.objects.filter(email=email).exists():
                error_message = 'Email already exists.'
            else:
                user = User.objects.create_user(username=studentID, email=email, password=password)
                user.save()
                success_message = 'Account created successfully'
                return redirect('signinuser')

    return render(request, 'scholarship/register.html', {'error_message': error_message, 'success_message': success_message})

def signinuser(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('set_password')

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                return redirect('studenthome')
            else:
                pass
        except User.DoesNotExist:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    return redirect('adminhome')
                else:
                    return redirect('studenthome')
            else:
                pass

    return render(request, 'login.html')

def studentapplicationform(request):
    studID = request.user.username
    student = get_object_or_404(studentInfo, studID=studID)
    passed = applicants.objects.filter(studID_id=studID).exists()
    note = applicants.objects.filter(studID_id=studID).filter(~Q(note=""), note__isnull=False).first()
    application_data = applicants.objects.filter(studID__studID=studID).first()
    context = {'student': student, 'passed': passed, 'note': note}
    print(note)

    if request.method == 'POST':
        action = request.POST.get('action')
        student_ID = request.POST.get('studID')
        print("1")
        if action == 'submit':
            print("2")
            form = applicantsForm(request.POST, request.FILES)
            print("3")
            # Check if the requirement already exists and note exists
            if application_data and note:
                print("4")
                cor_file = request.FILES.get('cor_file')
                grade_file = request.FILES.get('grade_file')
                schoolid_file = request.FILES.get('schoolid_file')
                scholar_type = request.POST.get('scholar_type')
                gpa = request.POST.get('gpa')
                print("5")
                # Update application data
                if cor_file:
                    print("6")
                    application_data.cor_file = cor_file
                print("7")
                if grade_file:
                    print("8")
                    application_data.grade_file = grade_file
                print("9")
                if schoolid_file:
                    print("10")
                    application_data.schoolid_file = schoolid_file
                print("11")
                if scholar_type:
                    print("12")
                    application_data.scholar_type = scholar_type
                print("13")
                if gpa:
                    print("14")
                    application_data.gpa = gpa
                print("15")
                print("shit")
                application_data.note = ""
                application_data.save()
                return redirect('studentapplication')
            else:
                # Check if the requirement already exists
                if applicants.objects.filter(studID_id=student_ID).exists() and not note:
                    print("student id already exists")
                    context['error'] = "Student ID already exists"
                else:
                    if form.is_valid():
                        form.save()
                        print("form saved")
                        if applicants.objects.filter(studID_id=student_ID).exists():
                            passed = True
                        context.update({'passed': passed})
                        return render(request, 'scholarship/studentapplicationform.html', context)  # Redirect to the same page or any other success page
                    else:
                        # Print form errors for debugging
                        print(form.errors)  # Add this line to print the form errors to the console
                        print("error form")

    return render(request, 'scholarship/studentapplicationform.html', context)


def adminapplication(request):
    scholar_type = request.GET.get('scholar_type')
    context = {}

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('action'):
                action, applicant_id = value.split('_')
                note = request.POST.get(f'note_{applicant_id}')
                
                try:
                    application_data = applicants.objects.get(id=applicant_id)
                    if action == 'UPDATE' and note:
                        application_data.note = note
                        application_data.save()
                        print("Note updated")
                    elif action == 'ACCEPT':
                        application_data.status = "ACCEPTED"
                        application_data.save()
                        print("Application accepted")
                    elif action == 'REJECTED':
                        application_data.delete()
                        print("Application rejected and deleted")
                except applicants.DoesNotExist:
                    print("Applicant not found")
    
    # Filter applicant_data based on scholar_type
    if scholar_type:
        if scholar_type == 'all':
            applicant_data = applicants.objects.filter(status='PENDING')
        else:
            applicant_data = applicants.objects.filter(status='PENDING', scholar_type=scholar_type)
    else:
        applicant_data = applicants.objects.filter(status='PENDING')

    context = {'applicant_data': applicant_data}
    return render(request, 'scholarship/adminapplication.html', context)


# @login_required
def adminreqsubmission(request):
    studID = request.user.username
    scholar_type = request.GET.get('scholar_type')
    
    is_requesting = AdminRequest.objects.filter(requesting=True).exists()
    active_request = AdminRequest.objects.filter(requesting=True).first()
    req_data = Requirement.objects.filter(status="PENDING", record="NEW")
    
    msg = False
    context = {}

    if request.method == 'POST':
        action = request.POST.get('action')
        year = request.POST.get('years')
        semester = request.POST.get('semester')

        if action == 'CLOSE':
            if active_request:
                Requirement.objects.filter(status='PENDING', record='NEW').update(record='OLD')
                Requirement.objects.filter(status='ACCEPTED', record='NEW').update(record='OLD')
                active_request.requesting = False
                active_request.save()
                is_requesting = False
                active_request = None
        elif action == 'REQUEST':
            # Check if the exact year and semester combination already exists
            if AdminRequest.objects.filter(year=year, semester=semester).exists():
                msg = True
            else:
                pattern = re.compile(r'^\d{4}-\d{4}$')
                if year and pattern.match(year):
                    try:
                        admin_request = AdminRequest(year=year, semester=semester, requesting=True)
                        admin_request.save()
                        is_requesting = True
                        active_request = admin_request
                    except Exception as e:
                        print("Invalid input")
                        print(e)  # Print the exception for debugging
                else:
                    print("Year must be in the format YYYY - YYYY")
        else:
            print("1")
            for key, value in request.POST.items():
                print("2")
                if key.startswith('action'):
                    action, requirement_id = value.split('_')
                    note = request.POST.get(f'note_{requirement_id}')
                    
                    print("3")
                    try:
                        print("4")
                        requirement_id = int(requirement_id)
                        print("requirement_id: ",requirement_id)
                        req_data = Requirement.objects.get(id=requirement_id)
                        print("5")
                        if action == 'UPDATE2' and note:
                            print("6")
                            req_data.note = note
                            print("7")
                            req_data.save()
                            print("Note updated")
                        elif action == 'ACCEPT2':
                            print("8")
                            req_data.status = "ACCEPTED"
                            print("9")
                            req_data.save()
                            print("Application accepted")
                        elif action == 'REJECTED2':
                            print("10")
                            req_data.delete()
                            print("requirement rejected and deleted")
                    except applicants.DoesNotExist:
                        print("requirement_id not found")
    else:
        form = AdminRequestForm()
        
    print("1")
    if scholar_type:
        print("2")
        if scholar_type == 'all':
            print("3")
            req_data = Requirement.objects.filter(status="PENDING", record="NEW")
        else:
            print("4")
            req_data = Requirement.objects.filter(status="PENDING", record="NEW", scholar_type=scholar_type)
    else:
        print(scholar_type)
        req_data = Requirement.objects.filter(status="PENDING", record="NEW")
    
    if 'form' not in locals():
        form = AdminRequestForm()

    context = {
        'is_requesting': is_requesting,
        'form': form,
        'msg': msg,  # Add msg to the context
        'active_request': active_request,
        'req_data': req_data
    }
    return render(request, 'scholarship/adminrequirements.html', context)



def studentreqsubmission(request):
    studID = request.user.username
    is_requesting = AdminRequest.objects.filter(requesting=True).exists()
    active_request = AdminRequest.objects.filter(requesting=True).first()
    passed_accepted_new = Requirement.objects.filter(studID=studID, status="ACCEPTED", record="NEW").first()
    note = Requirement.objects.filter(studID_id=studID, status="PENDING").filter(~Q(note=""), note__isnull=False).first()
    requirement_data = Requirement.objects.filter(studID__studID=studID, status="PENDING", record="NEW").first()
    
    user = request.user
    
    try:
        student = studentInfo.objects.get(studID=user.username)
        scholar = scholars.objects.get(studID=student)
        passed = Requirement.objects.filter(studID=studID, status="PENDING", record="NEW").first()
        is_scholar = scholars.objects.filter(studID=student).exists()
    except studentInfo.DoesNotExist:
        student = None
        scholar = None
        passed = None
        is_scholar = False
    except scholars.DoesNotExist:
        scholar = None
        is_scholar = False
        
    print("about to enter in the condition")
    if request.method == 'POST':
        print("Entered in the condition")
        gpa = request.POST.get('gpa')
        units = request.POST.get('units')
        cor_file = request.FILES.get('cor_file')
        grade_file = request.FILES.get('grade_file')
        schoolid_file = request.FILES.get('schoolid_file')
        print(gpa)
        print(units)
        print(cor_file)
        print(grade_file)
        print(schoolid_file)

        if is_scholar and active_request:
            print("3")
            if note:
                cor_file2 = request.FILES.get('cor_file')
                grade_file2 = request.FILES.get('grade_file')
                schoolid_file2 = request.FILES.get('schoolid_file')
                gpa2 = request.POST.get('gpa')
                units2 = request.POST.get('units')
            
                if cor_file2:
                    print("6")
                    requirement_data.cor_file = cor_file2
                    print("7")
                    if grade_file2:
                        print("8")
                        requirement_data.grade_file = grade_file2
                    print("9")
                    if schoolid_file2:
                        print("10")
                        requirement_data.schoolid_file = schoolid_file2
                    print("11")
                    if gpa2:
                        print("14")
                        requirement_data.gpa = gpa2
                    if units2:
                        print("14")
                        requirement_data.units = units2
                    print("15")
                    print("haha")
                    requirement_data.note = ""
                    requirement_data.save()
                    return redirect('student_req')
            else:
                requirement = Requirement(
                    studID=student,
                    scholar_ID=scholar,
                    year=active_request.year,
                    semester=active_request.semester,
                    scholar_type=scholar.scholar_type,
                    gpa=gpa,
                    cor_file=cor_file,
                    grade_file=grade_file,
                    schoolid_file=schoolid_file,
                    units=units
                )
                print("4")
                requirement.save()
                print("5")
                return redirect('student_req')
        else:
            print("Did not enter in the condition")
        
        
    
    context = {
        'is_requesting': is_requesting,
        'active_request': active_request,
        'is_scholar': is_scholar,
        'student': student,
        'scholar': scholar,
        'passed': passed,
        'passed_accepted_new': passed_accepted_new,
        'note': note
    }
    return render(request, 'scholarship/studentrequirements.html', context)


def save_requirements(request):
    passed = False
    if request.method == 'POST':
        student_ID = request.POST.get('student_ID')
        semester = request.POST.get('semester')

        # Check if the requirement already exists
        if Requirement.objects.filter(studID_id=student_ID, semester=semester).exists():
            messages.error(request, 'You already have passed the requirements for this semester.')
        else:
            form = RequirementForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Requirements submitted successfully.')
                if Requirement.objects.filter(studID_id=student_ID, semester=semester).exists():
                    passed = True
                return render(request, 'scholarship/studentrequirements.html', {'passed': passed})  # Redirect to the same page or any other success page
            else:
                # Print form errors for debugging
                print(form.errors)  # Add this line to print the form errors to the console
                messages.error(request, 'Error in form submission.')

        return render(request, 'studentrequirements.html', {'form': form, 'student': student})  # Pass form back to the template
    else:
        form = RequirementForm()
        student = get_object_or_404(studentInfo, studID=request.user.username)
    return render(request, 'scholarship/studentrequirements.html', {'form': form, 'student': student})
                  
def calculate_gpa_from_text(text):
    grades_units = {}
    total_units = 0
    total_grade_points = 0

    # Extract Total Units
    for line in text.split('\n'):
        if "Total Units" in line:
            try:
                total_units = float(line.split(':')[-1].strip())
            except ValueError:
                total_units = 0  # Default to 0 if parsing fails

    # Extract Grades and their corresponding units
    lines = text.split('\n')
    for line in lines:
        if "COMPL" in line or "CAS3" in line or "GE" in line or "ST" in line or "FIELD" in line:
            parts = line.split('|') if '|' in line else line.split('/')
            if len(parts) > 1:
                grade_str = parts[-1].strip()
                try:
                    grade = float(grade_str)
                    # Assuming each subject has 3 units
                    grades_units[line] = (grade, 3)
                except ValueError:
                    continue

    # Map extracted grades to grade points
    grade_points_mapping = {
        1.0: 1.0,
        1.1: 1.1,
        1.2: 1.2,
        1.3: 1.3,
        1.4: 1.4,
        1.5: 1.5,
        1.6: 1.6,
        1.7: 1.7,
        1.8: 1.8,
        1.9: 1.9,
        2.0: 2.0,
        2.1: 2.1,
        2.2: 2.2,
        2.3: 2.3,
        2.4: 2.4,
        2.5: 2.5,
        2.6: 2.6,
        2.7: 2.7,
        2.8: 2.8,
        2.9: 2.9,
        3.0: 3.0,
        3.1: 3.1,
        3.2: 3.2,
        3.3: 3.3,
        3.4: 3.4,
        3.5: 3.5,
        3.6: 3.6,
        3.7: 3.7,
        3.8: 3.8,
        3.9: 3.9,
        4.0: 4.0,
    }

    for grade, units in grades_units.values():
        total_grade_points += grade_points_mapping.get(grade, 0) * units

    gpa = total_grade_points / total_units if total_units > 0 else 0

    return round(gpa, 2), total_units, total_grade_points

def process_grade_image(request):
    if request.method == 'POST' and request.FILES.get('gradeFile'):
        grade_file = request.FILES['gradeFile']
        fs = FileSystemStorage()
        filename = fs.save(grade_file.name, grade_file)
        file_path = fs.path(filename)

        # Preprocess the image for better OCR accuracy
        image = Image.open(file_path)
        image = image.convert('L')  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
        image = ImageEnhance.Contrast(image).enhance(2)  # Enhance contrast
        extracted_text = pytesseract.image_to_string(image)

        # Print the extracted text in the terminal
        print("Extracted Text:")
        print(extracted_text)

        # Calculate GPA, total units, and total grade points from the extracted text
        gpa, total_units, total_grade_points = calculate_gpa_from_text(extracted_text)

        # Clean up the uploaded file
        os.remove(file_path)

        # Print the values in the terminal
        print("GPA:", gpa)
        print("Total Units:", total_units)
        print("Total Grade Points:", total_grade_points)

        return JsonResponse({'success': True, 'gpa': gpa, 'total_units': total_units})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def scholars_profile_admin(request):
    scholar_type = request.GET.get('scholar_type', '').lower()
    msg = ""
    context = {}

    if request.method == 'POST':
        for key in request.POST.keys():
            if key.startswith('action_') and request.POST[key] == 'ADD':
                index = key.split('_')[1]
                applicant_id = request.POST.get(f'applicant_id_{index}')
                scholar_id = request.POST.get(f'scholar_id_{index}')
                year = request.POST.get(f'year_{index}')
                gpa = request.POST.get(f'gpa_{index}')

                if not scholars.objects.filter(scholar_ID=scholar_id).exists():
                    applicant = applicants.objects.get(id=applicant_id)
                    student = applicant.studID

                    new_scholar = scholars(
                        scholar_ID=scholar_id,
                        studID=student,
                        scholar_type=applicant.scholar_type,
                        year=year
                    )
                    new_scholar.save()

                    # Update the applicant's GPA
                    applicant.gpa = gpa
                    applicant.status = 'APPROVED'
                    applicant.save()

                    msg = "Scholar added successfully."
                else:
                    messages.error(request, "Scholar ID already exists.")

                context['msg'] = msg
                return redirect('profile')

    if scholar_type:
        if scholar_type == 'all':
            applicant_data = applicants.objects.filter(status='ACCEPTED')
        else:
            applicant_data = applicants.objects.filter(status='ACCEPTED', scholar_type=scholar_type)
    else:
        applicant_data = applicants.objects.filter(status='ACCEPTED')

    student_data = studentInfo.objects.all()
    context = {'student_data': student_data, 'applicant_data': applicant_data, 'msg': msg}

    return render(request, 'scholarship/scholarsprofileadmin.html', context)
    

def add_scholar(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        applicant_id = request.POST.get('applicant_id')
        
        if action == 'ADD':
            try:
                applicant = applicants.objects.get(id=applicant_id)
                scholar_id = request.POST.get('scholarid')
                amount = request.POST.get('amount')
                gpa = applicant.gpa
                year = request.POST.get('year')

                # Calculate remarks based on GPA
                remarks = "PASSED" if gpa <= 3 else "FAILED"

                # Create a new scholar entry
                scholar = scholars.objects.create(
                    scholar_ID=scholar_id,
                    studID=applicant.studID,
                    scholar_type=applicant.scholar_type,
                    amount=amount,
                    gpa=gpa,
                    year=year,
                    remarks=remarks
                )

                # Set the status of the applicant to 'ACCEPTED'
                applicant.status = 'APPROVED'
                applicant.save()
                print("saved")
                return redirect('profile')
            except Exception as e:
                return redirect('profile')
            


def scholars_profile_student(request):
    studID = request.user.username
    application_data = applicants.objects.filter(studID__studID=studID).first()
    
    is_requesting = AdminRequest.objects.filter(requesting=True).exists()
    active_request = AdminRequest.objects.filter(requesting=True).first()
    applicant_approved = applicants.objects.filter(studID=studID, status="APPROVED").first()
    reqs = Requirement.objects.filter(studID=studID, status="PENDING", record="NEW").first() #data of the requirement
    reqs2 = Requirement.objects.filter(studID=studID, status="ACCEPTED", record="NEW").first()
    print("reqs: ", reqs)
    print("reqs2: ", reqs2)
    req_accepted = Requirement.objects.filter(studID=studID, status="ACCEPTED")
    print("req_accepted: ", req_accepted)
    
    student_data = studentInfo.objects.filter(studID=studID).first()
    scholars_table = scholars.objects.filter(studID_id=studID).first()
    note = applicants.objects.filter(studID_id=studID, status="PENDING").filter(~Q(note=""), note__isnull=False).first()
    note2 = Requirement.objects.filter(studID_id=studID, status="PENDING").filter(~Q(note=""), note__isnull=False).first()
    app_exist = application_data is not None
    exist = scholars_table is not None
    edit_mode = False
    edit_mode_2 = False
    user = request.user
    try:
        student = studentInfo.objects.get(studID=user.username)
        is_scholar = scholars.objects.filter(studID=student).exists()
    except studentInfo.DoesNotExist:
        student = None
        is_scholar = False
    
    print("1")
    if request.method == 'POST':
        print("2")
        action = request.POST.get('action')
        print("3")
        if action == 'EDIT':
            print("4")
            edit_mode = True
        elif action == 'DONE':
            print("5")
            if application_data:
                print("6")
                cor_file = request.FILES.get('cor_file')
                print("7")
                grade_file = request.FILES.get('grade_file')
                print("8")
                schoolid_file = request.FILES.get('schoolid_file')
                print("COR: ",cor_file)
                print("GRADE: ", grade_file)
                print("SCHOOL ID: ", schoolid_file)
                print("9")
                
                if cor_file:
                    print("10")
                    application_data.cor_file = cor_file
                    print("11")
                if grade_file:
                    print("12")
                    application_data.grade_file = grade_file
                    print("13")
                if schoolid_file:
                    print("14")
                    application_data.schoolid_file = schoolid_file
                    print("15")
                print("16")
                application_data.gpa = request.POST.get('gpa', application_data.gpa)
                print("17")
                application_data.save()
                print("18")
            print("19")
            edit_mode = False
        elif action == 'CANCEL':
            print("20")
            if application_data:
                print("21")
                application_data.delete()
                return redirect('profile_student')
        elif action == 'EDIT2':
            print("22")
            edit_mode_2 = True
        elif action == 'DONE2':
            if reqs:
                print("6")
                cor_file = request.FILES.get('cor_file2')
                print("7")
                grade_file = request.FILES.get('grade_file2')
                print("8")
                schoolid_file = request.FILES.get('schoolid_file2')
                print("COR: ",cor_file)
                print("GRADE: ", grade_file)
                print("SCHOOL ID: ", schoolid_file)
                print("9")
                
                if cor_file:
                    reqs.cor_file = cor_file
                if grade_file:
                    reqs.grade_file = grade_file
                if schoolid_file:
                    reqs.schoolid_file = schoolid_file
                reqs.gpa = request.POST.get('gpa2', reqs.gpa)
                reqs.save()
            edit_mode_2 = False
        elif action == 'CANCEL2':
            print("20")
            if reqs:
                print("to delete")
                reqs.delete()
                return redirect('profile_student')
            

    context = {
        'application_data': application_data,
        'student_data': student_data,
        'scholars_table': scholars_table,
        'app_exist': app_exist,
        'exist': exist,
        'note': note,
        'note2': note2,
        'is_scholar': is_scholar,
        'edit_mode': edit_mode,
        'cor_file_url': application_data.cor_file.url if application_data and application_data.cor_file else None,
        'grade_file_url': application_data.grade_file.url if application_data and application_data.grade_file else None,
        'schoolid_file_url': application_data.schoolid_file.url if application_data and application_data.schoolid_file else None,
        'gpa_current': application_data.gpa if application_data and application_data.gpa else None,
        'applicant_approved': applicant_approved,
        'reqs': reqs,
        'is_requesting': is_requesting,
        'active_request': active_request,
        'edit_mode_2': edit_mode_2,
        'cor_file_url2': reqs.cor_file.url if reqs and reqs.cor_file else None,
        'grade_file_url2': reqs.grade_file.url if reqs and reqs.grade_file.url else None,
        'schoolid_file_url2': reqs.schoolid_file if reqs and reqs.schoolid_file else None,
        'reqs2': reqs2,
        'req_accepted': req_accepted
    }
    print(edit_mode_2)
    
    return render(request, 'scholarship/scholarsprofilestudent.html', context)


def grade_submission(request):
    return render(request, 'scholarship/gradesubmission.html', {})

def mentorship(request):
    user = request.user
    try:
        student = studentInfo.objects.get(studID=user.username)
        is_scholar = scholars.objects.filter(studID=student).exists()
    except studentInfo.DoesNotExist:
        student = None
        is_scholar = False

    context = {
        'student': student,
        'is_scholar': is_scholar
    }
    return render(request, 'scholarship/studenthome.html', context)



def search_student(request):
    query = request.GET.get('search_id')
    student = None
    invalid = False
    invalid_input = False
    is_scholar = False
    not_scholar = False
    scholar = None  # Initialize scholar object to None
    if query:
        if query.isnumeric():
            try:
                student = studentInfo.objects.get(studID=query)
                # Check if the student is a scholar
                if scholars.objects.filter(studID=query).exists():
                    scholar = scholars.objects.get(studID=query)
                    is_scholar = True
                    not_scholar = False
                    print("Not: ",not_scholar)
                    print("Yes: ",is_scholar)
                else:
                    not_scholar = True
                    is_scholar = False
                    print("Not: ",not_scholar)
                    print("Yes: ",is_scholar)
            except studentInfo.DoesNotExist:
                student = None
                invalid = True
        else:
            invalid_input = True
    return render(request, 'scholarship/scholarsprofileadmin.html', {'student': student, 'invalid': invalid, 'invalid_input': invalid_input, 'is_scholar': is_scholar, 'scholar': scholar, 'not_scholar': not_scholar})

def admingrant(request):
    scholar_type = request.GET.get('scholar_type', '').lower()
    context = {}
    
    print("1")
    if request.method == 'POST':
        print("2")
        action = request.POST.get('action')
        print("3")
        if action and action.startswith("GRANT"):
            print("4")
            index = action.split('_')[1]
            amount = request.POST.get(f'amount_{index}')
            applicant_id = request.POST.get(f'applicant_id_{index}')
            print("5")
            try:
                print("6")
                with transaction.atomic():
                    print("7")
                    grant = Requirement.objects.select_for_update().get(id=applicant_id)
                    scholar_id = grant.scholar_ID
                    year = grant.year
                    semester = grant.semester
                    gpa = grant.gpa
                    scholar_status = scholar_id.scholar_status
                    total_units_enrolled = grant.units
                    remarks = "PASSED" if gpa <= 3 else "FAILED"
                    print("8")

                    # Create SemesterDetails entry
                    SemesterDetails.objects.create(
                        scholar_ID=scholar_id,
                        year=year,
                        semester=semester,
                        amount=amount,
                        gpa=gpa,
                        scholar_status=scholar_status,
                        remarks=remarks,
                        total_units_enrolled=total_units_enrolled
                    )
                    print("9")

                    # Update Requirement record field
                    grant.record = 'OLD'
                    print("10")
                    grant.save()
                    print("11")

            except Requirement.DoesNotExist:
                print("12")
                pass
            except Exception as e:
                print("13")
                print(f"Exception occurred: {e}")
                pass
    print("14")
    if scholar_type:
        if scholar_type == 'all':
            to_be_granted_data = Requirement.objects.filter(status='ACCEPTED', record="NEW")
        else:
            to_be_granted_data = Requirement.objects.filter(status='ACCEPTED', record="NEW", scholar_type=scholar_type)
    else:
        to_be_granted_data = Requirement.objects.filter(status='ACCEPTED', record="NEW")

    student_data = studentInfo.objects.all()
    context = {'student_data': student_data, 'to_be_granted_data': to_be_granted_data}

    return render(request, 'scholarship/admingrant.html', context)
# from .models import studentInfo, scholars, SemesterDetails, Requirement

def scholarupdate(request):
    error = None
    scholar_data = None

    if request.method == "POST":
        if 'search-box' in request.POST:
            search_id = request.POST.get('search-box')
            if not search_id.isdigit():
                error = "Invalid Input"
            else:
                try:
                    scholar = scholars.objects.get(pk=search_id)
                    student = scholar.studID
                    semester_detail = scholar.semester_details.first()
                    scholar_data = {
                        'student_id': student.studID,
                        'lrn': student.lrn,
                        'fname': student.firstname,
                        'mname': student.middlename,
                        'lname': student.lastname,
                        'college_prog': student.degree,
                        'award_id': scholar.scholar_ID,
                        'scholar_type': scholar.scholar_type,
                        'amount': semester_detail.amount if semester_detail else '',
                        'units': semester_detail.total_units_enrolled if semester_detail else '',
                        'gpa': semester_detail.gpa if semester_detail else ''
                    }
                except scholars.DoesNotExist:
                    error = "No scholar Found"

        else:
            scholar_id = request.POST.get('award_id')
            scholar_type = request.POST.get('scholar_type')
            amount = request.POST.get('amount')
            student_id = request.POST.get('student_id')
            lrn = request.POST.get('lrn')
            fname = request.POST.get('fname')
            mname = request.POST.get('mname')
            lname = request.POST.get('lname')
            college_prog = request.POST.get('college_prog')
            original_scholar_id = request.POST.get('original_scholar_id')

            try:
                current_scholar = scholars.objects.get(pk=original_scholar_id)
                current_student = current_scholar.studID

                if scholar_id != original_scholar_id:
                    if scholars.objects.filter(pk=scholar_id).exists():
                        error = "Scholar ID already exists"
                    else:
                        current_scholar.scholar_ID = scholar_id

                if scholar_type:
                    current_scholar.scholar_type = scholar_type

                current_scholar.save()

                if student_id and lrn and fname and lname and college_prog:
                    current_student.studID = student_id
                    current_student.lrn = lrn
                    current_student.firstname = fname
                    current_student.middlename = mname
                    current_student.lastname = lname
                    current_student.degree = college_prog
                    current_student.save()

                if amount:
                    semester_detail = current_scholar.semester_details.first()
                    if semester_detail:
                        semester_detail.amount = amount
                        semester_detail.save()

                error = "Scholar updated successfully"
            except scholars.DoesNotExist:
                error = "No scholar Found"
            except Exception as e:
                error = str(e)

    context = {
        'error': error,
        'scholar_data': scholar_data,
    }
    return render(request, 'scholarship/updatescholars.html', context)


# def scholarupdate(request):
#     return render(request, 'updatescholars.html', {})



# ------------------------------------    dayag code    --------------------

def chedreports(request):
    return render(request, 'scholarship/chedreports.html', {})


def chedreports_merit(request):
    # Get the selected semester and year from the GET parameters
    selected_semester = request.GET.get('semester', 'all')
    selected_year = request.GET.get('scholarship_year')
    
    years = AdminRequest.objects.values_list('year', flat=True).distinct()

    # Fetch scholars based on the selected criteria
    scholars_list = scholars.objects.filter(Q(scholar_type="CHED - Full Merit") | Q(scholar_type="CHED - Half Merit"))
    scholar_ids = SemesterDetails.objects.filter(scholar_ID__in=scholars_list)
    
    
    print("1")
    if selected_semester == 'all' and selected_year == 'All':
        print("2")
        scholar_ids = SemesterDetails.objects.filter(scholar_ID__in=scholars_list)
        print("3")
    elif selected_semester and selected_year == 'All':
        print("hehe")
        scholar_ids = scholar_ids.filter(semester=selected_semester)
        print("huuhu")
    elif selected_semester == 'all' and selected_year:
        print("0")
        scholar_ids = scholar_ids.filter(year=selected_year)
        print("0")
    elif selected_semester and selected_year:
        print("4")
        scholar_ids = scholar_ids.filter(semester=selected_semester, year=selected_year)
        print("5")
    else:
        print("6")
        scholar_ids = SemesterDetails.objects.filter(scholar_ID__in=scholars_list)
        print("7")
    print("8")
        
        # scholar_ids = scholar_ids.values_list('scholar_id', flat=True)
        # scholars_list = scholars_list.filter(scholar_ID__in=scholar_ids)
    print("year: ", selected_year)
    print("semester: ", selected_semester)

    context = {
        'scholars': scholars_list,
        'semester': selected_semester,
        'scholarship_year': selected_year,
        'scholar_ids': scholar_ids,
        'years': years
    }
    return render(request, 'scholarship/dayag/ched_merit.html', context)



# views.py
def chedreports_TES(request):
    selected_semester = request.GET.get('semester', 'all')
    selected_year = request.GET.get('scholarship_year')
    
    years = AdminRequest.objects.values_list('year', flat=True).distinct()

    # Fetch scholars based on the selected criteria, CHED - Tertiary Education Subsidy
    scholars_list = scholars.objects.filter(scholar_type="CHED - Tertiary Education Subsidy")
    scholar_ids = SemesterDetails.objects.filter(scholar_ID__in=scholars_list)
    
    
    print("1")
    if selected_semester == 'all' and selected_year == 'All':
        print("2")
        scholar_ids = SemesterDetails.objects.filter(scholar_ID__in=scholars_list)
        print("3")
    elif selected_semester and selected_year == 'All':
        print("hehe")
        scholar_ids = scholar_ids.filter(semester=selected_semester)
        print("huuhu")
    elif selected_semester == 'all' and selected_year:
        print("0")
        scholar_ids = scholar_ids.filter(year=selected_year)
        print("0")
    elif selected_semester and selected_year:
        print("4")
        scholar_ids = scholar_ids.filter(semester=selected_semester, year=selected_year)
        print("5")
    else:
        print("6")
        scholar_ids = SemesterDetails.objects.filter(scholar_ID__in=scholars_list)
        print("7")
    print("8")
        
    print("year: ", selected_year)
    print("semester: ", selected_semester)
    
    for index, scholar in enumerate(scholar_ids, start=7001):
        scholar.sequence = index

    context = {
        'scholars': scholars_list,
        'semester': selected_semester,
        'scholarship_year': selected_year,
        'scholar_ids': scholar_ids,
        'years': years
    }
    return render(request, 'scholarship/dayag/ched_tes.html', context)

def chedreports_TDP(request):
    tulong_dunong_program_scholars = scholars.objects.filter(scholar_type='CHED - Tulong Dunong Program')
    selected_year = request.GET.get('scholarship_year')
    
    years = AdminRequest.objects.values_list('year', flat=True).distinct()
    if selected_year == 'All':
        first_semester = SemesterDetails.objects.filter(
            scholar_ID__in=tulong_dunong_program_scholars, semester="1st Semester"
        )
        second_semester = SemesterDetails.objects.filter(
            scholar_ID__in=tulong_dunong_program_scholars, semester="2nd Semester"
        )
    elif selected_year:
        first_semester = SemesterDetails.objects.filter(scholar_ID__in=tulong_dunong_program_scholars, semester="1st Semester", year=selected_year)
        second_semester = SemesterDetails.objects.filter(scholar_ID__in=tulong_dunong_program_scholars, semester="2nd Semester", year=selected_year)
    else:
        first_semester = SemesterDetails.objects.filter(
            scholar_ID__in=tulong_dunong_program_scholars, semester="1st Semester"
        )
        second_semester = SemesterDetails.objects.filter(
            scholar_ID__in=tulong_dunong_program_scholars, semester="2nd Semester"
        )
    
    # Create a dictionary to hold second semester details keyed by scholar_ID
    second_semester_dict = {detail.scholar_ID_id: detail for detail in second_semester}
    
    # Add the second semester detail to the first semester detail if available
    for detail in first_semester:
        second_sem_detail = second_semester_dict.get(detail.scholar_ID_id, None)
        if second_sem_detail:
            detail.second_semester_amount = second_sem_detail.amount
            detail.second_semester_date_added = second_sem_detail.date_added
        else:
            detail.second_semester_amount = 0
            detail.second_semester_date_added = ''

    # Calculate totals
    total_first_semester = sum(detail.amount for detail in first_semester)
    total_second_semester = sum(detail.second_semester_amount for detail in first_semester)

    context = {
        'first_semester': first_semester,
        'selected_year': selected_year,
        'years': years,
        'total_first_semester': total_first_semester,
        'total_second_semester': total_second_semester,
    }
    return render(request, 'scholarship/dayag/ched_tdp.html', context)


def chedreports_Coscho(request):
    selected_semester = request.GET.get('semester', 'all')
    selected_year = request.GET.get('scholarship_year')
    
    years = AdminRequest.objects.values_list('year', flat=True).distinct()

    # Fetch scholars based on the selected criteria, CHED - Tertiary Education Subsidy
    scholars_list = scholars.objects.filter(scholar_type="CHED - Coscho")
    scholar_ids = SemesterDetails.objects.filter(scholar_ID__in=scholars_list)
    
    
    print("1")
    if selected_semester == 'all' and selected_year == 'All':
        print("2")
        scholar_ids = SemesterDetails.objects.filter(scholar_ID__in=scholars_list)
        print("3")
    elif selected_semester and selected_year == 'All':
        print("hehe")
        scholar_ids = scholar_ids.filter(semester=selected_semester)
        print("huuhu")
    elif selected_semester == 'all' and selected_year:
        print("0")
        scholar_ids = scholar_ids.filter(year=selected_year)
        print("0")
    elif selected_semester and selected_year:
        print("4")
        scholar_ids = scholar_ids.filter(semester=selected_semester, year=selected_year)
        print("5")
    else:
        print("6")
        scholar_ids = SemesterDetails.objects.filter(scholar_ID__in=scholars_list)
        print("7")
    print("8")
        
    print("year: ", selected_year)
    print("semester: ", selected_semester)
    
    for index, scholar in enumerate(scholar_ids, start=1):
        scholar.sequence = index
        
    total_amount = sum(scholar.amount for scholar in scholar_ids)

    context = {
        'scholars': scholars_list,
        'semester': selected_semester,
        'scholarship_year': selected_year,
        'scholar_ids': scholar_ids,
        'years': years,
        'total_amount': total_amount
    }
    return render(request, 'scholarship/dayag/ched_coscho.html', context)


# ------------------------ ADMINLIQUIDATION ---------------------------
def adminliquidation(request):
    return render(request, 'adminliquidation.html', {})

from ..models import LiquidationTES
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def adminliquidation_TES(request):
    if request.method == 'POST':
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        total_amount = request.POST.get('total1_0_05')
        total_disbursement = request.POST.get('totalDisbursement1_0_05')
        balance = request.POST.get('balance')

        # Check details
        index = 1
        check_data = []
        while True:
            date = request.POST.get(f'date{index}')
            if not date:
                break
            check_number = request.POST.get(f'checkNumber{index}')
            particulars = request.POST.get(f'particulars{index}')
            amount = request.POST.get(f'amount{index}')
            liquidation_cost = float(amount) * 0.005 
            if LiquidationTES.objects.filter(check_number=check_number).exists():
                context = {
                    'error_message': f"Check number {check_number} already exists! Try Again..."
                }
                return render(request, 'scholarship/dayag/liquidation_TES.html', context)

            check_data.append({
                'date': date,
                'check_number': check_number,
                'particulars': particulars,
                'amount': amount,
                'liquidation_cost': liquidation_cost 
            })
            index += 1

        # Create the first LiquidationTDP instance
        first_check = check_data[0]
        liquidation = LiquidationTES.objects.create(
            date=first_check['date'],
            check_number=first_check['check_number'],
            particulars=first_check['particulars'],
            amount=first_check['amount'],
            liquidation_cost=first_check['liquidation_cost'],
            semester=semester,
            academic_year=academic_year,
            total_amount=total_amount,
            total_disbursement=total_disbursement,
            balance=balance,
        )

        # Save remaining check details
        for check in check_data[1:]:
            LiquidationTES.objects.create(
                date=check['date'],
                check_number=check['check_number'],
                particulars=check['particulars'],
                amount=check['amount'],
                semester=semester,
                academic_year=academic_year,
                total_amount=total_amount,
                total_disbursement=total_disbursement,
                balance=balance,
            )

        # Disbursement details
        disbursement_index = 1
        while True:
            disbursement_date = request.POST.get(f'disbursementDate{disbursement_index}')
            if not disbursement_date:
                break
            disbursement_number = request.POST.get(f'disbursementNumber{disbursement_index}')
            disbursement_particulars = request.POST.get(f'disbursementParticulars{disbursement_index}')
            disbursement_amount = request.POST.get(f'disbursementAmount{disbursement_index}')

            tesDisbursement.objects.create(
                liquidation=liquidation,
                disbursement_date=disbursement_date,
                disbursement_number=disbursement_number,
                disbursement_particulars=disbursement_particulars,
                disbursement_amount=disbursement_amount,
            )
            disbursement_index += 1

        return redirect('liquidation_TES')
    return render(request, 'scholarship/dayag/liquidation_TES.html')



def adminliquidation_TDP(request):
    if request.method == 'POST':
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        total_amount = request.POST.get('total1_0_05')
        total_disbursement = request.POST.get('totalDisbursement1_0_05')
        balance = request.POST.get('balance')

        # Check details
        index = 1
        check_data = []
        while True:
            date = request.POST.get(f'date{index}')
            if not date:
                break
            check_number = request.POST.get(f'checkNumber{index}')
            particulars = request.POST.get(f'particulars{index}')
            amount = request.POST.get(f'amount{index}')
            liquidation_cost = float(amount) * 0.005 
            if LiquidationTDP.objects.filter(check_number=check_number).exists():
                context = {
                    'error_message': f"Check number {check_number} already exists! Try Again..."
                }
                return render(request, 'scholarship/dayag/liquidation_TDP.html', context)

            check_data.append({
                'date': date,
                'check_number': check_number,
                'particulars': particulars,
                'amount': amount,
                'liquidation_cost': liquidation_cost 
            })
            index += 1

        # Create the first LiquidationTDP instance
        first_check = check_data[0]
        liquidation = LiquidationTDP.objects.create(
            date=first_check['date'],
            check_number=first_check['check_number'],
            particulars=first_check['particulars'],
            amount=first_check['amount'],
            liquidation_cost=first_check['liquidation_cost'],
            semester=semester,
            academic_year=academic_year,
            total_amount=total_amount,
            total_disbursement=total_disbursement,
            balance=balance,
        )

        # Save remaining check details
        for check in check_data[1:]:
            LiquidationTDP.objects.create(
                date=check['date'],
                check_number=check['check_number'],
                particulars=check['particulars'],
                amount=check['amount'],
                semester=semester,
                academic_year=academic_year,
                total_amount=total_amount,
                total_disbursement=total_disbursement,
                balance=balance,
            )

        # Disbursement details
        disbursement_index = 1
        while True:
            disbursement_date = request.POST.get(f'disbursementDate{disbursement_index}')
            if not disbursement_date:
                break
            disbursement_number = request.POST.get(f'disbursementNumber{disbursement_index}')
            disbursement_particulars = request.POST.get(f'disbursementParticulars{disbursement_index}')
            disbursement_amount = request.POST.get(f'disbursementAmount{disbursement_index}')

            tdpDisbursement.objects.create(
                liquidation=liquidation,
                disbursement_date=disbursement_date,
                disbursement_number=disbursement_number,
                disbursement_particulars=disbursement_particulars,
                disbursement_amount=disbursement_amount,
            )
            disbursement_index += 1

        return redirect('liquidation_TDP')

    return render(request, 'scholarship/dayag/liquidation_TDP.html')

from ..models import LiquidationCoScho

def adminliquidation_CoScho(request):
    if request.method == "POST":
        dv_no = request.POST.get('dv_no')
        dv_date = request.POST.get('dv_date')
        total_admin_cost = request.POST.get('total_admin_cost')
        total_stipend = request.POST.get('total_stipend')
        office_supplies = request.POST.get('office_supplies')
        communication = request.POST.get('communication')
        traveling = request.POST.get('traveling')
        representation = request.POST.get('representation')
        professional_services = request.POST.get('professional_services')
        legal_services = request.POST.get('legal_services')
        other_expenses = request.POST.get('other_expenses')
        balance = request.POST.get('balance')
        if LiquidationCoScho.objects.filter(dv_no=dv_no).exists():
                context = {
                    'error_message': f"DV Number {dv_no} already exists! Try Again..."
                }
                return render(request, 'scholarship/dayag/liquidation_CoScho.html', context)
        LiquidationCoScho.objects.create(
            dv_no=dv_no,
            dv_date=dv_date,
            total_admin_cost=total_admin_cost,
            total_stipend=total_stipend,
            office_supplies=office_supplies,
            communication=communication,
            traveling=traveling,
            representation=representation,
            professional_services=professional_services,
            legal_services=legal_services,
            other_expenses=other_expenses,
            balance=balance
        )
        return redirect('liquidation_CoScho')
    return render(request, 'scholarship/dayag/liquidation_CoScho.html')

#  --------------------------- transaction report ----------------------
def transactionreports(request):
    return render(request, 'scholarship/transactionreports.html', {})
from django.shortcuts import render
from datetime import datetime
from ..models import scholars, SemesterDetails


# def scholarship_program(request):
#     selected_semester = request.GET.get('semester', 'all')
#     selected_year = request.GET.get('scholarship_year')
    
#     years = AdminRequest.objects.values_list('year', flat=True).distinct()
    
#     unique_scholar_types = scholars.objects.values_list('scholar_type', flat=True).distinct()
#     scholars_data = scholars.objects.all()

#     male_total = 0
#     female_total = 0
#     total = 0

#     # Dictionary to store the counts by scholar type
#     scholarship_counts = defaultdict(lambda: {'male': 0, 'female': 0})

#     for scholar in scholars_data:
#         student = scholar.studID
        
#         if student.sex == 'M':
#             male_total += 1
#             scholarship_counts[scholar.scholar_type]['male'] += 1
#         elif student.sex == 'F':
#             female_total += 1
#             scholarship_counts[scholar.scholar_type]['female'] += 1
#         total += 1

#     # Convert the scholarship_counts dictionary to a list of dictionaries
#     scholarship_counts_list = [
#         {'scholar_type': key, 'male': value['male'], 'female': value['female'], 'total': value['male'] + value['female']}
#         for key, value in scholarship_counts.items()
#     ]

#     # Prepare the context
#     context = {
#         'unique_scholar_types': unique_scholar_types,
#         'male_total': male_total,
#         'female_total': female_total,
#         'total': total,
#         'scholarship_counts': scholarship_counts_list
#     }

#     return render(request, 'dayag/scholarship_program.html', context)
    

   
def scholarship_program(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_semester = request.GET.get('semester', 'All')
    academic_year = request.GET.get('scholarship_year')

    # Get unique years from AdminRequest model
    years = AdminRequest.objects.values_list('year', flat=True).distinct()

    # Initial filtering for date range
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            semester_details = SemesterDetails.objects.filter(date_added__range=(start_date, end_date))
        except ValueError:
            semester_details = SemesterDetails.objects.none()
    else:
        semester_details = SemesterDetails.objects.all()

    # Additional filtering for semester
    if selected_semester != 'All':
        semester_details = semester_details.filter(semester=selected_semester)
        
    # Filter by academic year if provided
    if academic_year and academic_year != 'All':
        semester_details = semester_details.filter(year=academic_year)

    # Recalculate total counts after all filters have been applied
    total_transactions = semester_details.count()
    total_male = semester_details.filter(scholar_ID__studID__sex='M').count()
    total_female = semester_details.filter(scholar_ID__studID__sex='F').count()

    scholarship_data = {}
    scholarships = scholars.objects.all()

    for scholarship in scholarships:
        scholarship_type = scholarship.scholar_type
        if scholarship_type not in scholarship_data:
            scholarship_data[scholarship_type] = {'details': [], 'male_count': 0, 'female_count': 0}

        details = semester_details.filter(scholar_ID=scholarship)

        male_count = details.filter(scholar_ID__studID__sex='M').count()
        female_count = details.filter(scholar_ID__studID__sex='F').count()

        scholarship_data[scholarship_type]['details'].append({
            'scholar': scholarship,
            'semester_details': details,
        })
        scholarship_data[scholarship_type]['male_count'] += male_count
        scholarship_data[scholarship_type]['female_count'] += female_count

    return render(request, 'scholarship/dayag/scholarship_program.html', {
        'scholarship_data': scholarship_data,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
        'academic_year': academic_year,
        'selected_semester': selected_semester,
        'total_transactions': total_transactions,
        'total_male': total_male,
        'total_female': total_female,
        'years': years,  # Pass the unique years to the template
    })


     

def format_date(date_string):
    date_obj = datetime.strptime(date_string, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%B %d, %Y')
    return formatted_date
from django.shortcuts import render
from ..models import SemesterDetails, AdminRequest

def format_date(date_str):
    # Add your date formatting logic here if needed
    return date_str

def scholarship_billing_report(request):
    selected_scholarship_type = request.GET.get('scholarship_type', 'All')
    selected_semester = request.GET.get('semester', 'All')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    selected_year = request.GET.get('scholarship_year', 'All')

    years = AdminRequest.objects.values_list('year', flat=True).distinct()
    
    scholarships = SemesterDetails.objects.all()

    if selected_scholarship_type != 'All':
        scholarships = scholarships.filter(scholar_ID__scholar_type=selected_scholarship_type)
    
    if selected_semester != 'All':
        scholarships = scholarships.filter(semester=selected_semester)
    
    if start_date and end_date:
        scholarships = scholarships.filter(date_added__range=[start_date, end_date])

    if selected_year != 'All':
        scholarships = scholarships.filter(year=selected_year)

    formatted_start_date = format_date(start_date) if start_date else ''
    formatted_end_date = format_date(end_date) if end_date else ''

    period = f"{formatted_start_date} to {formatted_end_date}" if start_date and end_date else 'All time'

    context = {
        'scholarships': scholarships,
        'selected_scholarship_type': selected_scholarship_type,
        'selected_semester': selected_semester,
        'start_date': start_date,
        'end_date': end_date,
        'period': period,
        'years': years,
        'selected_year': selected_year,
    }

    return render(request, 'scholarship/dayag/scholarship_billing_report.html', context)

def Admin_cost_liquidation(request):
    return render(request, 'scholarship/dayag/Admin_cost_liquidation.html', {})

def coscho_liquidation(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_semester = request.GET.get('semester', 'All')
    
    # Filter data based on the date range and semester if provided
    if start_date and end_date:
        transactions = LiquidationCoScho.objects.filter(dv_date__range=[start_date, end_date])
    else:
        transactions = LiquidationCoScho.objects.all()

    total_transactions = transactions.count()

    context = {
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'total_transactions': total_transactions,
        'selected_semester': selected_semester,
    }

    return render(request, 'scholarship/dayag/coscho_transLiquidation.html', context)


def tdp_liquidation(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    selected_semester = request.GET.get('semester', 'All')
    academic_year = request.GET.get('academic_year', '')

    transactions = LiquidationTDP.objects.all()

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if selected_semester and selected_semester != 'All':
        transactions = transactions.filter(semester=selected_semester)
    if academic_year:
        transactions = transactions.filter(academic_year__icontains=academic_year)

    total_transactions = transactions.count()

    context = {
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'selected_semester': selected_semester,
        'academic_year': academic_year,
        'total_transactions': total_transactions,
    }

    return render(request, 'scholarship/dayag/tdp_transLiquidation.html', context)


def tes_liquidation(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    selected_semester = request.GET.get('semester', 'All')
    academic_year = request.GET.get('academic_year', '')

    transactions = LiquidationTES.objects.all()

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if selected_semester and selected_semester != 'All':
        transactions = transactions.filter(semester=selected_semester)
    if academic_year:
        transactions = transactions.filter(academic_year__icontains=academic_year)

    total_transactions = transactions.count()

    context = {
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'selected_semester': selected_semester,
        'academic_year': academic_year,
        'total_transactions': total_transactions,
    }

    return render(request, 'scholarship/dayag/tes_transLiquidation.html', context)
