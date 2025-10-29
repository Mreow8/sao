import csv
# In your views.py

from django.contrib.auth.decorators import login_required # 👈 Import this
from datetime import datetime
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from ..forms import CounselingSchedulerForm, IndividualProfileForm, FileUpload, UploadFileForm, ExitInterviewForm, OjtAssessmentForm, StaffForm
from ..models import TestArray, studentInfo, counseling_schedule, exit_interview_db, OjtAssessment, IndividualProfileBasicInfo, IntakeInverView, staffInfo
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.template.defaulttags import register
from django.core.mail import send_mail
from django.http import HttpResponse

# def upload_files(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             csv_file = request.FILES['file']
#             decoded_file = csv_file.read().decode('utf-8').splitlines()
#             reader = csv.DictReader(decoded_file)
            
#             for row in reader:
#                 studentInfo.objects.create(
#                     studID=row['studID'],
#                     lrn=row['lrn'],
#                     lastname=row['lastname'],
#                     firstname=row['firstname'],
#                     middlename=row['middlename'],
#                     degree=row['degree'],
#                     yearlvl=row['yearlvl'],
#                     sex=row['sex'],
#                     emailadd=row['emailadd'],
#                     contact=row['contact']
#                 )
            
#             messages.success(request, 'File uploaded and data imported successfully')
#             return redirect('upload_file')
#     else:
#         form = UploadFileForm()
#     return render(request, 'upload.html', {'form': form})
def upload_files(request):
    student_form = UploadFileForm()
    staff_form = UploadFileForm()
    staff_manual_form = StaffForm()

    return render(request, 'upload.html', {
        'form': student_form,   # for students
        'staff_form': staff_form,   # for staff CSV
        'staff_manual_form': staff_manual_form  # for manual staff
    })

def staff_input(request):
    if request.method == "POST":
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("staff_input")  # reload page after save
    else:
        form = StaffForm()
    return render(request, "staff_input.html", {"form": form})
def staff_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                staffInfo.objects.create(
                    staffID=row['staffID'],
                    lrn=row['lrn'],
                    lastname=row['lastname'],
                    firstname=row['firstname'],
                    middlename=row['middlename'],
                    sex=row['sex'],
                    emailadd=row['emailadd'],
                    contact=row['contact']
                )
            
            messages.success(request, 'File uploaded and data imported successfully')
            return redirect('upload_file')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

#Page View
def home(request):
	return render(request, 'main.html',{})

def calculate_age(birth_date):
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age
def individualProfile(request):
    student = None
    user = request.user

    if user.is_authenticated:
        try:
            student = studentInfo.objects.get(studID=int(user.username))
        except studentInfo.DoesNotExist:
            messages.error(request, "Student not found")

    if request.method == 'POST':
        form = IndividualProfileForm(request.POST, request.FILES)
        if form.is_valid():
            siblings_name = request.POST.getlist('name[]')
            siblings_age = request.POST.getlist('age[]')
            siblings_placework = request.POST.getlist('placework[]')

            name_of_organization = request.POST.getlist('name_of_organization[]')
            in_out_school = request.POST.getlist('inoutSchool[]')
            position = request.POST.getlist('position[]')
            inclusive_years = request.POST.getlist('inclusiveyears[]')

            current_datetime = timezone.now()

            describeYouBest_values = [
                'Friendly', 'Self-Confident', 'Calm', 'Quick-Tempered', 'Feels Inferior',
                'Unhappy', 'Easily Bored', 'Talented', 'Withdrawn', 'Conscientious',
                'Talkative', 'Cheerful', 'Moody', 'Easily Exhausted', 'Lazy',
                'Sensitive', 'Poor health', 'Reserved', 'Quiet', 'Independent',
                'Depressed', 'Suspicious', 'Irritable', 'Stubborn', 'Thoughtful',
                'Lovable', 'Jealous', 'Shy', 'Sarcastic', 'Tactful',
                'Pessimistic', 'Submissive', 'Optimistic', 'Happy-go-lucky', 'Goal-oriented'
            ]

            describeYouBest_checked = request.POST.getlist('describeYouBest[]')
            student_id = request.POST.get('student_id_val')

            date_of_birth_str = form.cleaned_data['dateOfBirth']
            date_of_birth = datetime.strptime(str(date_of_birth_str), '%Y-%m-%d')
            age = calculate_age(date_of_birth)

            student = get_object_or_404(studentInfo, studID=student_id)

            describeYouBest_state = {value: value in describeYouBest_checked for value in describeYouBest_values}

            new_form = form.save(commit=False)
            new_form.age = age
            new_form.studentId = student
            new_form.dateFilled = current_datetime
            new_form.siblingsName = siblings_name
            new_form.siblingsAge = siblings_age
            new_form.siblingsSchoolWork = siblings_placework
            new_form.nameOfOrganization = name_of_organization
            new_form.inOutSchool = in_out_school
            new_form.positionTitle = position
            new_form.inclusiveYears = inclusive_years
            new_form.describeYouBest = describeYouBest_state

            if 'studentPhoto' in request.FILES:
                new_form.studentPhoto = request.FILES['studentPhoto']

            new_form.save()
            messages.success(request, 'Your request has been successfully added. An email will be sent if it is accepted.')
            return redirect('Individual Profile')
    else:
        form = IndividualProfileForm()

    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'guidance/individual_profile.html', context)


from django.shortcuts import render, redirect, get_object_or_404

# Assuming necessary models are imported:
# from .models import IndividualProfileBasicInfo, IntakeInterview, studentInfo 
# from django.contrib import messages # Import if using messages

def intake_interview_view(request):
    # 1. FIX: Fetch students before the POST check so it's available 
    # for the template rendering in both GET and POST (if form invalid).
    students = studentInfo.objects.all()

    if request.method == 'POST':
        individualId = request.POST.get('individualId')

        # --- I. Individual Inventory Service ---
        individualActivity = request.POST.getlist('individualActivity[]')
        individualDateAccomplished = request.POST.getlist('individualAccomplished[]')
        individualRemarks = request.POST.getlist('individualRemarks[]')

        # --- II. Appraisal Service (Typo: apprailsal -> appraisal) ---
        appraisalTest = request.POST.getlist('appraisalTest[]')
        appraisalDateTaken = request.POST.getlist('appraisalDateTaken[]')
        appraisalDateInterpreted = request.POST.getlist('appraisalDateInterpreted[]')
        appraisalRemarks = request.POST.getlist('appraisalRemarks[]')

        # --- III. Counseling Service (CRITICAL ISSUE: HTML Radio Names) ---
        # The HTML uses 'couseling_type1[]', 'couseling_type2[]', etc.
        # This view logic assumes a single name, which is incorrect for the current HTML.
        # It's highly recommended to fix the HTML to use a consistent name like 'counseling_type'.
        # Assuming the HTML fix suggested previously: name="counseling_type" and values="Walk-in"/"Referral"
        # If the HTML is NOT fixed, the block below is error-prone.
        
        # Current (flawed) logic:
        # counseling_types = request.POST.getlist('couseling_type[]')
        # selected_types = []
        # for ctype in counseling_types:
        #     if ctype == 'True':
        #         selected_types.append('Referral')
        #     elif ctype == 'False':
        #         selected_types.append('Walk-in')
        
        # Since the HTML uses names like couseling_type1[], couseling_type2[], etc.
        # A workaround (if HTML isn't fixed) must iterate over all 10 possible groups:
        selected_types = []
        for i in range(1, 11): # Iterate from 1 to 10
            # Get the list of selected values for this row's radio group (should be 0 or 1 item)
            radio_value = request.POST.getlist(f'couseling_type{i}[]') 
            if radio_value:
                # Apply the specific logic for this form's True/False values
                if radio_value[0] == 'True':
                    selected_types.append('Walk-in')
                elif radio_value[0] == 'False':
                    selected_types.append('Referral')

        counselingDate = request.POST.getlist('counselingDate[]')
        counselingConcern = request.POST.getlist('counselingConcern[]')
        counselingRemarks = request.POST.getlist('counselingRemarks[]')

        # --- IV. Follow-up Service ---
        followActivity = request.POST.getlist('followActivity[]')
        followDate = request.POST.getlist('followDate[]')
        followRemarks = request.POST.getlist('followRemarks[]')

        # --- V. Information Service ---
        informationActivity = request.POST.getlist('informationActivity[]')
        informationDate = request.POST.getlist('informationDate[]')    
        informationRemarks = request.POST.getlist('informationRemarks[]')

        # --- VI. Consultation Service (Typo: counsultation -> consultation) ---
        consultationActivity = request.POST.getlist('counseltationActivity[]')
        consultationDate = request.POST.getlist('counseltationDate[]')    
        consultationRemarks = request.POST.getlist('counseltationRemarks[]')

        individual = get_object_or_404(IndividualProfileBasicInfo, individualProfileID=individualId)

        # Typo: IntakeInverView should likely be IntakeInterview
        try:
            obj = IntakeInverView( # Assuming this is your actual model name
                individualProfileId = individual,
                
                individualActivity = individualActivity,
                individualDateAccomplished = individualDateAccomplished,
                individualRemarks = individualRemarks,

                appraisalTest = appraisalTest,
                appraisalDateTaken = appraisalDateTaken,
                appraisalDateInterpreted = appraisalDateInterpreted,
                appraisalRemarks = appraisalRemarks,

                counselingType = selected_types,
                counselingDate = counselingDate,
                counselingConcern = counselingConcern,
                counselingRemarks = counselingRemarks,

                followActivity = followActivity,
                followDate = followDate,
                followRemarks = followRemarks,

                informationActivity = informationActivity,
                informationDate = informationDate,    
                informationRemarks = informationRemarks,

                # Corrected variable names in model saving
                counsultationActivity = consultationActivity,
                counsultationDate = consultationDate,    
                counsultationRemarks = consultationRemarks,
            )
            obj.save()
            # If using messages: messages.success(request, "Intake interview saved.")
            return redirect('Intake Interview') # Make sure this is a valid URL name
        except Exception as e:
            # logger.error(f"Error saving IntakeInterview: {e}") # Add logging if available
            # If using messages: messages.error(request, "An error occurred while saving the form.")
            pass # Continue to render the form with context if an error occurs

    # 2. FIX: Ensure 'students' is passed to the context for the GET request 
    # (and for the POST request if execution reaches here due to an error/return).
    return render(request, 'guidance/intake_interview.html', {'students': students})

def search_student_info_for_intake(request):
     if request.method == 'POST':
        id_number = request.POST.get('id_number', '')
        try:
            student = studentInfo.objects.get(studID = id_number)
            individual = IndividualProfileBasicInfo.objects.filter(studentId = student)
            items = []
            for val in individual:
                response = {
                    'profile_number': val.individualProfileID,
                    'studentid': val.studentId.studID,
                    'name': f"{val.studentId.lastname}, {val.studentId.middlename}, {val.studentId.firstname}",
                    'datefilled': val.dateFilled.strftime("%B %d, %Y")
                }
                items.append(response)

            return JsonResponse({'response': items})
        except studentInfo.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

def counseling_app(request):
    student = None
    user = request.user

    if user.is_authenticated:
        if user.username.isdigit():  # ✅ Prevent ValueError
            try:
                student = studentInfo.objects.get(studID=int(user.username))
                print(student)
            except studentInfo.DoesNotExist:
                messages.error(request, "Student not found")
        else:
            messages.error(request, "Invalid username format")
    if request.method == 'POST':
        form = CounselingSchedulerForm(request.POST)
        if form.is_valid():
            current_datetime = timezone.now()
            student_id = request.POST.get('student_id_val')

            if not student_id or not student_id.isdigit():
                messages.error(request, "Invalid student ID.")
                return redirect('Counseling App With Scheduler')

            student = get_object_or_404(studentInfo, studID=int(student_id))
                        
            # Check for ongoing schedules
            ongoing_schedule = counseling_schedule.objects.filter(
                studentID=student, 
                scheduled_date__gte=current_datetime.date()
            ).first()
            
            if ongoing_schedule and not ongoing_schedule.status == 'Declined' and not ongoing_schedule.status == 'Expired':
                time = {
					'8-9': '8:00 AM - 9:00 AM',
					'9-10': '9:00 AM - 10:00 AM',
					'10-11': '10:00 AM-11:00 AM',
					'11-12': '11:00 AM -12:00 PM',
					'1-2':'1:00 PM - 2:00 PM',
					'2-3':'2:00 PM - 3:00 PM',
					'3-4':'3:00 PM - 4:00 PM',
					'4-5':'4:00 PM - 5:00 PM'
				}

                scheduled_date = ongoing_schedule.scheduled_date.strftime('%B %d, %Y')
                scheduled_time = time[f'{ongoing_schedule.scheduled_time}']
                messages.error(request, f'You still have an ongoing schedule on {scheduled_date} on {scheduled_time}.')
                return redirect('Counseling App With Scheduler')
            print("erwerer")
            formatted_date = current_datetime.strftime('%Y-%m-%d')
            counseling = form.save(commit=False)
            counseling.dateRecieved = formatted_date
            counseling.studentID = student  # Assign the studentInfo instance
            counseling.save()
            print("Counseling schedule saved to database:")
            print("Student:", counseling.studentID)
            print("Date Received:", counseling.dateRecieved)
        
            print("Scheduled Date:", counseling.scheduled_date)
            print("Scheduled Time:", counseling.scheduled_time)

            messages.success(request, 'Your request has been successfully added. An email will be sent if it is accepted.')
            return redirect('Counseling App With Scheduler')
    else:
        form = CounselingSchedulerForm()
    
    context = {'form': form, 
        'student': student,
    }
    return render(request, 'guidance/counseling_app.html', context)

def counseling_app_admin_view(request):
    meeting_requests = counseling_schedule.objects.select_related('studentID').order_by('-dateRecieved')

    time = {
        '8-9': '8:00 AM - 9:00 AM',
        '9-10': '9:00 AM - 10:00 AM',
        '10-11': '10:00 AM-11:00 AM',
        '11-12': '11:00 AM -12:00 PM',
        '1-2': '1:00 PM - 2:00 PM',
        '2-3': '2:00 PM - 3:00 PM',
        '3-4': '3:00 PM - 4:00 PM',
        '4-5': '4:00 PM - 5:00 PM'
    }

    context = {
        'meeting_requests': meeting_requests,
        'time': time,
           'page': 'counseling_app_admin'
    }
    return render(request, 'guidance/counseling_app_admin_view.html', context)


@login_required
def exit_interview(request):
    # 1. You ALREADY get the student object securely here. This is correct!
    try:
        student = studentInfo.objects.get(user=request.user)
    except studentInfo.DoesNotExist:
        messages.error(request, "Could not find a student profile for your account.")
        return redirect('some_other_page') # Change to your dashboard or home URL

    # 2. Check for an ongoing request for the GET request
    ongoing_request = exit_interview_db.objects.filter(
        studentID=student,
        status='Pending'
    ).first()

    if request.method == 'POST':
        form = ExitInterviewForm(request.POST)
        
        if form.is_valid():
            
            # 3. Check for an ongoing request AGAIN before saving
            #    We use the SECURE 'student' object from above
            if ongoing_request:
                messages.error(request, f'You still have a pending request.')
                return redirect('Exit Interview')

            # --- START: This is where the fix is ---

            # 4. REMOVED THESE LINES THAT CAUSED THE ERROR:
            # student_id = request.POST.get('studentID') 
            # student = get_object_or_404(studentInfo, studID=student_id)

            # 5. GET THE STUDENT ID from the SECURE student object for your calculation:
            student_id_str = str(student.studID)

            # --- END: This is where the fix is ---
            
            new_form = form.save(commit=False)
            
            # (Your 'fields' logic is fine)
            fields = [
                'academically_too_challenging', 'not_academically_challenging_enough',
                'does_not_offer_my_academic_major', 'what_is_your_intended_major',
                'size_of_the_school', 'location_of_the_school',
                'negative_social_campus_climate', 'residence_hall_environment_not_positive',
                'social_environment_not_diverse_enough', 'not_enough_campus_activities',
                'needed_more_academic_support', 'financial', 'medical_injury',
                'medical_pyscho', 'family-obligations', 'major_event'
            ]
            values = []
            for field in fields:
                value = request.POST.get(field, '')
                values.append(value)
            
            # (Your custom ID logic is fine, just make sure it uses the secure ID)
            current_date = timezone.localtime(timezone.now())
            date_number = current_date.strftime("%m%d%y")

            # 6. USE THE SECURE ID STRING HERE:
            digit_sum = sum(int(digit) for digit in student_id_str)

            preliminary_final_number = f"{date_number}{digit_sum}"
            total_length = 10
            number_of_zeros_needed = total_length - len(preliminary_final_number)
            final_number = f"{date_number}{'0' * number_of_zeros_needed}{digit_sum}"
            
            new_form.date = timezone.now()
            new_form.contributedToDecision = values
            
            # 7. ASSIGN THE SECURE student object here
            new_form.studentID = student 
            
            new_form.dateRecieved = timezone.now()
            new_form.save()
            messages.success(request, 'Your request has been successfully added. An email will be sent if it is accepted.')
            return redirect('Exit Interview')
    else:
        form = ExitInterviewForm()

    # Pass the student and request status to the template
    context = {
        'form': form,
        'student': student,
        'ongoing_request': ongoing_request
    }
    return render(request, 'guidance/exit_interview.html', context)
def print_exit_interview(request, request_id): # <-- 1. Accept the 'request_id' here
    
    # 2. Fetch the ONE specific interview using the ID
    interview = get_object_or_404(exit_interview_db.objects.select_related('studentID'), exitinterviewId=request_id)
    
    # 3. Pass that single 'interview' object to the template
    context = {
        'interview': interview
    }
    return render(request, 'guidance/print_exit.html', context)
def exit_interview_admin_view(request):
    exit_interview_request = exit_interview_db.objects.select_related('studentID').order_by('-dateRecieved')
    context = {'exit_interview_request': exit_interview_request,}
    return render(request, 'guidance/exit_interview_admin.html', context)
# In guidance.py

def print_ojt_assessment(request, request_id): 
    
    # 1. FIX: Fetch from OjtAssessment, not exit_interview_db
    #    Also, use the correct primary key 'OjtRequestID'
    assessment = get_object_or_404(OjtAssessment.objects.select_related('studentID'), OjtRequestID=request_id)
    
    # 2. FIX: Pass the 'assessment' object to the template.
    #    (We'll update the template to use this in Step 3)
    context = {
        'assessment': assessment 
    }
    return render(request, 'guidance/print_assessment.html', context)
def ojt_assessment(request):
    student = None
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to make a request.")
        return redirect('your_login_page_name') # Change to your login URL

    try:
        student = studentInfo.objects.get(studID=int(request.user.username))
    except studentInfo.DoesNotExist:
        messages.error(request, "Student profile not found for your account.")
        return redirect('your_student_dashboard_name') # Change to your dashboard URL
    except ValueError:
        messages.error(request, "Your account type cannot make this request.")
        return redirect('your_student_dashboard_name') # Change to your dashboard URL

    # --- NEW: Check for pending request for the GET request ---
    ongoing_request = OjtAssessment.objects.filter(
        studentID=student,
        status='Pending'
    ).first()

    if request.method == 'POST':
        # This check is crucial for security
        if ongoing_request:
            messages.error(request, f'You still have a pending request.')
            return redirect('OJT Assessment')

        form = OjtAssessmentForm(request.POST)
        # This check is crucial for security
        if ongoing_request:
            messages.error(request, f'You still have a pending request.')
            return redirect('OJT Assessment')

        form = OjtAssessmentForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.studentID = student 
            # new_form.dateRecieved = timezone.now() # No longer needed if you set auto_now_add=True in models.py
            # ensure required dateRecieved is set
            new_form.dateRecieved = timezone.now()
            new_form.save()
            messages.success(request, 'Your request has been successfully added. An email will be sent if it is accepted.')
            return redirect('OJT Assessment')
    else:
        form = OjtAssessmentForm()

    # --- NEW: Get the student's entire request history ---
    request_history = OjtAssessment.objects.filter(studentID=student).order_by('-dateRecieved')
    
    context = {
        'form': form,
        'student': student,
        'request_history': request_history,  # <-- Pass the history to the template
        'ongoing_request': ongoing_request   # <-- Pass the pending request to the template
    }
    return render(request, 'guidance/ojt_assessment.html', context)
def ojt_assessment_admin_view(request):
    ojt_assessment_request = OjtAssessment.objects.select_related('studentID').order_by('-dateRecieved')
    context = {'ojt_assessment_request': ojt_assessment_request,}
    return render(request, 'guidance/ojt_assessment_admin.html', context)

#Checker/Getter

def check_date_time_validity(request):
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        try:
            # Convert the selected date string to a Python datetime object
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            # Query the counseling_schedule model for entries with the same scheduled_date
            counseling_schedules = counseling_schedule.objects.filter(scheduled_date=selected_date)
            # You can now do something with the counseling_schedules queryset, like serialize it to JSON
            serialized_data = [{'scheduled_time': schedule.scheduled_time, 'status': schedule.status} for schedule in counseling_schedules]
            return JsonResponse({'counseling_schedules': serialized_data})
        except ValueError:
            # Handle invalid date format
            return JsonResponse({'error': 'Invalid date format'}, status=400)

def check_date_time_validity_for_exit(request):
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        try:
            # Convert the selected date string to a Python datetime object
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            # Query the counseling_schedule model for entries with the same scheduled_date
            counseling_schedules = exit_interview_db.objects.filter(scheduled_date=selected_date)
            # You can now do something with the counseling_schedules queryset, like serialize it to JSON
            serialized_data = [{'scheduled_time': schedule.scheduled_time, 'status': schedule.status} for schedule in counseling_schedules]
            return JsonResponse({'counseling_schedules': serialized_data})
        except ValueError:
            # Handle invalid date format
            return JsonResponse({'error': 'Invalid date format'}, status=400)
def search_student_info_for_individual(request):
     if request.method == 'POST':
        id_number = request.POST.get('id_number', '')
        try:
            student = studentInfo.objects.get(studID=id_number)
            response = {
				'student_id': student.studID,
				'name': f"{(student.lastname).title()}, {(student.middlename).title()}, {(student.firstname.title())}",
				'program':student.degree,
                'sex':student.sex,
        	}
            return JsonResponse(response)
        except studentInfo.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)



def search_student_info(request):
    if request.method == 'POST':
        id_number = request.POST.get('id_number', '')
        try:
            student = studentInfo.objects.get(studID=id_number)
            response = {
				'student_id': student.studID,
				'name': f"{student.lastname}, {student.firstname}",
				'program':student.degree,
                'year':student.yearlvl,
				'contact_number': student.contact,
				'email': student.emailadd
        	}
            return JsonResponse(response)
        except studentInfo.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
def search_exit_interview_request(request):
    if request.method == 'POST':
        id_number = request.POST.get('id_number', '')
        students = exit_interview_db.objects.filter(studentID__studID=id_number)
        if students.exists():
            response = []
            for student in students:
                response.append({
                    'exit_interview_id': student.exitinterviewId,
                    'date_received': student.dateRecieved.strftime("%B %d, %Y"),
                    'student_id': student.studentID.studID,
                    'name': f"{student.studentID.lastname}, {student.studentID.firstname}",
                    'status': student.status
                })
            return JsonResponse(response, safe=False)  # safe=False to allow serialization of non-dict objects
        else:
            return JsonResponse({'error': 'Student not found'}, status=404)    
        
def search_ojt_assessment_request(request):
    if request.method == 'POST':
        id_number = request.POST.get('id_number', '')
        students = OjtAssessment.objects.filter(studentID__studID=id_number)
        if students.exists():
            response = []
            for student in students:
                response.append({
                    'ojt_assessment_id': student.OjtRequestID,
                    'date_received': student.dateRecieved.strftime("%B %d, %Y"),
                    'student_id': student.studentID.studID,
                    'name': f"{student.studentID.lastname}, {student.studentID.firstname}",
                    'schoolyear': student.schoolYear,
                    'status': student.status
                })
            return JsonResponse(response, safe=False)  # safe=False to allow serialization of non-dict objects
        else:
            return JsonResponse({'error': 'Student not found'}, status=404)    
        
def get_exit_interview_request(request):
    if request.method == 'POST':
        recordID = request.POST.get('requestID','')
        try:
            student = exit_interview_db.objects.get(exitinterviewId=recordID)
            if student.studentID.middlename == 'NONE':
                middleInit = ''  # Set to empty string if text is 'NONE'
            else:
                middleInit = student.studentID.middlename[0]

            response = {
				'name': f"{student.studentID.firstname.title()} {middleInit} {student.studentID.lastname.title()}",
                'date': (student.date).strftime("%B %d, %Y"),
                'dateenrolled': (student.dateEnrolled).strftime("%B %d, %Y"),
                'contact': student.studentID.contact,
                'reasonforleaving': student.reasonForLeaving,
                'satisfiedWithAcadamic': student.satisfiedWithAcadamic,
                'feedbackWithAcademic': student.feedbackWithAcademic,
                'satisfiedWithSocial': student.satisfiedWithSocial,
                'feedbackWithSocial':student.feedbackWithSocial,
                'satisfiedWithServices':student.satisfiedWithServices,
                'feedbackWithServices':student.feedbackWithServices,
                'contributedToDecision': student.contributedToDecision,
                'intendedMajor': student.intendedMajor,
                'firstConsider': student.firstConsider,
                'whatCondition': student.whatCondition,
                'recommend': student.recommend,
                'howSatisfied': (student.howSatisfied).title(),
                'planTOReturn': student.planTOReturn,
                'accademicExperienceSatisfied': student.accademicExperienceSatisfied,
                'knowAboutYourTime': student.knowAboutYourTime,
                'currentlyEmployed': student.currentlyEmployed,
                'explainationEmployed': student.explainationEmployed
        	}
            return JsonResponse(response)
        except studentInfo.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        
def get_ojt_assessment_data(request):
    if request.method == 'POST':
        recordID = request.POST.get('OjtRequestID','')
        try:
            student = OjtAssessment.objects.get(OjtRequestID=recordID)
            if student.studentID.middlename == 'NONE':
                middleInit = ''  # Set to empty string if text is 'NONE'
            else:
                middleInit = student.studentID.middlename[0]
            dateAccepted =student.dateAccepted
            formatted_dateAccepeted = dateAccepted.strftime("%B %d, %Y")
            response = {
				'name': f"{student.studentID.firstname.title()} {middleInit} {student.studentID.lastname.title()}",
                'schoolyear': student.schoolYear,
				'program':student.studentID.degree,
                'date_accepted':formatted_dateAccepeted,    
        	}
            return JsonResponse(response)
        except studentInfo.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

#Update/Delete

def update_counseling_schedule(request):
    if request.method == 'POST':
        requestID = request.POST.get('counselingID', '')
        update_type = request.POST.get('type','')
        if update_type == 'accept':
            obj = get_object_or_404(counseling_schedule, counselingID=requestID)
            obj.status = 'Accepted'
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your Counseling Schedule request has been approved."
            email = obj.email
            obj.save()

            #This shit takes longer to finish that my will to live

            send_mail(
                'Counseling Schedule Request',
                message,
                'notifytest391@gmail.com',  # From email
                [email],  # To email
                fail_silently=False,
            )
            obj.save()
    
            # Optionally, you can return a JSON response indicating success
            return JsonResponse({'message': 'Value updated successfully'})
        elif update_type == 'decline':
            obj = get_object_or_404(counseling_schedule, counselingID=requestID)
            obj.status = 'Declined'
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your Counseling Schedule request has been declined."
            email = obj.email
            obj.save()
            send_mail(
                'Counseling Schedule Request',
                message,
                'notifytest391@gmail.com',  # From email
                [email],  # To email
                fail_silently=False,
            )
            obj.save()
    
            # Optionally, you can return a JSON response indicating success
            return JsonResponse({'message': 'Value updated successfully'})
def delete_counseling_schedule(request):
    if request.method == 'POST':
        requestID = request.POST.get('counselingID', '')
        obj = get_object_or_404(counseling_schedule, counselingID=requestID)
        obj.delete()
        return JsonResponse({'message': 'Value updated successfully'}) 
     
def update_exit_interview_status(request):
    if request.method == 'POST':
        requestID = request.POST.get('exitinterviewId', '')
        update_type = request.POST.get('type','')
        if update_type == 'accept':
            obj = get_object_or_404(exit_interview_db, exitinterviewId=requestID)
            obj.status = 'Accepted'
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your Exit Interview request has been approved."
            email = obj.emailadd
            obj.save()
            send_mail(
                'Exit Interview Request',
                message,
                'notifytest391@gmail.com',  # From email
                [email],  # To email
                fail_silently=False,
            )
            obj.save()
    
            # Optionally, you can return a JSON response indicating success
            return JsonResponse({'message': 'Value updated successfully'})
        elif update_type == 'decline':
            obj = get_object_or_404(exit_interview_db, exitinterviewId=requestID)
            obj.status = 'Declined'
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your Exit Interview request has been declined."
            email = obj.emailadd
            obj.save()
            send_mail(
                'Exit Interview Request',
                message,
                'notifytest391@gmail.com',  # From email
                [email],  # To email
                fail_silently=False,
            )
            obj.save()
    
            # Optionally, you can return a JSON response indicating success
            return JsonResponse({'message': 'Value updated successfully'})
def delete_exit_interview_status(request):
    if request.method == 'POST':
        requestID = request.POST.get('exitinterviewId', '')
        obj = get_object_or_404(exit_interview_db, exitinterviewId=requestID)
        obj.delete()
        return JsonResponse({'message': 'Value updated successfully'})
def update_ojt_assessment(request):
    if request.method == 'POST':
        requestID = request.POST.get('OjtRequestID', '')
        update_type = request.POST.get('type','')
        if update_type == 'accept':
            obj = get_object_or_404(OjtAssessment, OjtRequestID=requestID)
            obj.status = 'Accepted'
            obj.dateAccepted = timezone.now()
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your OJT Assessments/Psychological Issuance request has been approved."
            email = obj.emailadd
            obj.save()
            send_mail(
                'OJT Assessments/Psychological Issuance Request',
                message,
                'notifytest391@gmail.com',  # From email
                [email],  # To email
                fail_silently=False,
            )
    
            # Optionally, you can return a JSON response indicating success
            return JsonResponse({'message': 'Value updated successfully'})
        elif update_type == 'decline':
            obj = get_object_or_404(OjtAssessment, OjtRequestID=requestID)
            obj.status = 'Declined'
            obj.save()
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your OJT Assessments/Psychological Issuance request has been declined."
            email = obj.emailadd
            send_mail(
                'OJT Assessments/Psychological Issuance Request',
                message,
                'notifytest391@gmail.com',  # From email
                [email],  # To email
                fail_silently=False,
            )
            # Optionally, you can return a JSON response indicating success
            return JsonResponse({'message': 'Value updated successfully'})       
def delete_ojt_assessment(request):
    if request.method == 'POST':
        requestID = request.POST.get('exitinterviewId', '')
        obj = get_object_or_404(OjtAssessment, OjtRequestID=requestID)
        obj.delete()
        return JsonResponse({'message': 'Value updated successfully'})  

#Filter

@register.filter
def get_formatted_time(dictionary, key):
    return dictionary.get(key)
