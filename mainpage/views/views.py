from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model, authenticate, login
from django.conf import settings
import random
import requests
import logging
from threading import Thread

from ..models import studentInfo, staffInfo, TemporaryUser, CustomUser, Organization
from ..forms import RoleAssignForm

User = get_user_model()

logger = logging.getLogger(__name__)

def is_admin(user):
    return user.is_authenticated and user.is_superuser
def is_org_admin_or_super(user):
    return user.is_authenticated and (user.role == 'org_admin' or user.role == 'superadmin')
def send_otp_email(email, otp):
    subject = 'Your Account Verification Code'
    message = f'Your One-Time Password for registration is: {otp}\nIt is valid for 10 minutes.'
    Thread(
        target=send_mail,
        args=(subject, message, settings.EMAIL_HOST_USER, [email]),
        kwargs={'fail_silently': False}
    ).start()
def signupuser(request):
    context = {}

    if request.method == 'POST':
        user_id = request.POST.get('studID', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        determined_role = None # Initialize role variable

        # Validate passwords (Omitted for brevity, but keep in your code)
        if cpassword != password:
            context['error_message'] = "Passwords do not match."
            context['studID_value'] = user_id
            context['email_value'] = email
            return render(request, 'scholarship/register.html', context)

        if len(password) < 8:
            context['error_message'] = "Password must be at least 8 characters."
            context['studID_value'] = user_id
            context['email_value'] = email
            return render(request, 'scholarship/register.html', context)

        # Check if student or staff AND determine role
        is_student = studentInfo.objects.filter(studID=user_id).exists()
        is_staff = staffInfo.objects.filter(staffID=user_id).exists()

        if is_student and not is_staff:
            determined_role = 'student'
        elif is_staff and not is_student:
            # IMPORTANT: If 'staff' is not the precise role, you must 
            # fetch the actual role from the staffInfo object here.
            determined_role = 'staff'
        else:
            context['error_message'] = "Invalid ID. No matching student or staff found."
            context['studID_value'] = user_id
            context['email_value'] = email
            return render(request, 'scholarship/register.html', context)

        try:
            # Check 1: Does the user_id (username) already exist? (Omitted for brevity)
            if User.objects.filter(username=user_id).exists():
                context['error_message'] = "This Student/Staff ID is already registered."
                context['studID_value'] = user_id
                context['email_value'] = email
                return render(request, 'scholarship/register.html', context)

            # Check 2: Does the email already exist? (Omitted for brevity)
            if User.objects.filter(email=email).exists():
                context['error_message'] = "This Email is already registered."
                context['studID_value'] = user_id
                context['email_value'] = email
                return render(request, 'scholarship/register.html', context)

            # Generate OTP and hash password (Omitted for brevity)
            otp = str(random.randint(100000, 999999))
            hashed_password = make_password(password)

            # Save temporary user or update existing one
            temp_user, created = TemporaryUser.objects.update_or_create(
                username=user_id,
                defaults={
                    'email': email,
                    'password': hashed_password,
                    'otp_code': otp,
                    'created_at': timezone.now(),
                    'role': determined_role, # <--- 🔑 The new crucial line
                }
            )

            # Send OTP to email (Omitted for brevity)
            send_otp_email(email, otp)

            messages.info(request, f"A 6-digit verification code has been sent to {email}.")
            return redirect('verify_otp_page', user_id=user_id)

        except Exception as e:
            context['error_message'] = f"An error occurred during signup: {e}"
            print(f"Error during signup: {e}")

    return render(request, 'scholarship/register.html', context)

    
def verify_otp(request, user_id):
    context = {'user_id': user_id}

    try:
        temp_user = TemporaryUser.objects.get(username=user_id)
        context['email'] = temp_user.email
    except TemporaryUser.DoesNotExist:
        messages.error(request, "Your verification session has expired. Please sign up again.")
        return redirect('signupuser')

    if request.method == 'POST':
        otp_submitted = request.POST.get('otp', '').strip()

        # Check expiration
        if temp_user.created_at < timezone.now() - timedelta(minutes=10):
            temp_user.delete()
            messages.error(request, "Verification code expired. Please sign up again.")
            return redirect('signupuser')

        # Compare OTP
        if otp_submitted == temp_user.otp_code:
            try:
                user = User(
                    username=temp_user.username,
                    email=temp_user.email,
                    password=temp_user.password
                )

                # Determine role
                if studentInfo.objects.filter(studID=temp_user.username).exists():
                    user.role = 'student'
                    info_obj = studentInfo.objects.get(studID=user.username)
                elif staffInfo.objects.filter(staffID=temp_user.username).exists():
                    user.role = 'staff'
                    info_obj = staffInfo.objects.get(staffID=user.username)
                else:
                    messages.error(request, "No student/staff record found.")
                    temp_user.delete()
                    return redirect('signupuser')

                user.save()
                info_obj.user = user
                info_obj.save()

                temp_user.delete()
                messages.success(request, "Account verified successfully! You can now log in.")
                return redirect('signinuser')

            except Exception as e:
                context['error_message'] = f"An error occurred during verification: {e}"
                print(f"Error creating user: {e}")
        else:
            context['error_message'] = "Invalid verification code. Please try again."

    return render(request, 'scholarship/verify_otp.html', context)
def homepage(request):
    base_template = get_base_template(request.user)
    context = {'base_template': base_template}
    
    # Add this logic to prevent the crash
    if request.user.is_authenticated and request.user.role == 'org_admin':
        if hasattr(request.user, 'organization'):
            context['org'] = request.user.organization
            # Also pass empty forms so the template tags don't crash
            from ..forms import AccreditationForm # Import if needed or pass None and handle in template
            context['accreditation_form'] = None 

    return render(request, 'homepage.html', context)


@login_required 
@user_passes_test(is_org_admin_or_super)
def orgmain(request):
    return render(request, 'orgadmin.html')


def calendar(request):
    return render(request, 'officeOfStudentL/calendarOfEvents.html')

def login_view(request):
    return render(request, 'login.html')

def post(request):
    return render(request, 'scrapper.html')

def assign_role(request):
    role_filter = request.GET.get('role', '')
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'username')
    direction = request.GET.get('dir', 'asc')

    users_list = CustomUser.objects.all()

    if role_filter:
        users_list = users_list.filter(role=role_filter)

    if query:
        users_list = users_list.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    valid_sort_fields = ['username', 'email', 'role']
    if sort_by not in valid_sort_fields:
        sort_by = 'username'
        
    order_field = f"{'-' if direction == 'desc' else ''}{sort_by}"
    users_list = users_list.order_by(order_field)

    paginator = Paginator(users_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        org_id = request.POST.get('organization_id') or None

        try:
            user = CustomUser.objects.get(id=user_id)
            user.role = role
            
            if role == 'org_admin' and org_id:
                user.organization_id = org_id
            else:
                user.organization = None
            
            user.save()
            messages.success(request, f"{user.username}'s role updated to {user.get_role_display()}.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
        
        return redirect(request.get_full_path())

    organizations = Organization.objects.all()
    
    context = {
        'page_obj': page_obj,
        'organizations': organizations,
        'role_choices': CustomUser.ROLE_CHOICES,
        'query': query,
        'sort_by': sort_by,
        'direction': direction,
        'role_filter': role_filter,
    }
    
    return render(request, 'assign_role.html', context)


def signinuser(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        recaptcha_response = request.POST.get('g-recaptcha-response')

        context = {'email': email}

        if not recaptcha_response:
            messages.error(request, "Please complete the reCAPTCHA.")
            return render(request, 'login.html', context)

        secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', None)
        if not secret_key:
            messages.error(request, "reCAPTCHA is not configured correctly (missing secret key). Please contact the administrator.")
            logger.error("RECAPTCHA_SECRET_KEY is missing in Django settings.")
            return render(request, 'login.html', context)

        try:
            data = {
                'secret': secret_key,
                'response': recaptcha_response
            }
            verify_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, timeout=5)
            verify_response.raise_for_status()
            result = verify_response.json()

        except requests.exceptions.Timeout:
            messages.error(request, "Could not verify reCAPTCHA (timeout). Please try again.")
            logger.warning("reCAPTCHA verification request timed out.")
            return render(request, 'login.html', context)
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not connect to reCAPTCHA service. Error: {e}")
            logger.error(f"reCAPTCHA connection error: {e}")
            return render(request, 'login.html', context)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during reCAPTCHA verification: {e}")
            logger.error(f"Unexpected reCAPTCHA error: {e}")
            return render(request, 'login.html', context)

        if not result.get('success'):
            error_codes = result.get('error-codes', [])
            logger.warning(f"reCAPTCHA verification failed. Error codes: {error_codes}")

            if 'missing-input-secret' in error_codes:
                messages.error(request, "reCAPTCHA configuration error (missing secret). Please contact the administrator.")
            elif 'invalid-input-secret' in error_codes:
                 messages.error(request, "reCAPTCHA configuration error (invalid secret). Please contact the administrator.")
            else:
                 messages.error(request, "Invalid reCAPTCHA. Please try again.")

            return render(request, 'login.html', context)

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Account does not exist.")
            return render(request, 'login.html', context)

        if not user_obj.is_active:
            messages.error(request, "This account is inactive. Contact admin.")
            return render(request, 'login.html', context)

        user = authenticate(request, username=user_obj.username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}!")

            if user.is_superuser:
                return redirect('homepage')
            if user.is_superuser:
    # You might want to create a specific 'superadmin_dashboard' later
                return redirect('homepage') 

            elif hasattr(user, 'role'):
                # --- Student ---
                if user.role == 'student':
                    return redirect('homepage')

                # --- Student Life Staff (and generic staff) ---
                elif user.role == 'student_life_staff' or user.role == 'staff':
                    return redirect('student_life_dashboard')

                # --- Scholarship ---
                elif user.role == 'scholarship_officer':
                    return redirect('scholarship_dashboard')

                # --- Guidance ---
                elif user.role == 'guidance':
                    return redirect('guidance_dashboard')

                # --- Medical / Clinic ---
                elif user.role == 'clinic_admin':
                    return redirect('clinic_dashboard')

                # --- Job Placement ---
                elif user.role == 'placement_officer':
                    return redirect('placement_dashboard')

                # --- Discipline ---
                elif user.role == 'discipline_officer':
                    return redirect('discipline_dashboard')

                # --- Alumni ---
                elif user.role == 'alumni_officer':
                    return redirect('alumni_dashboard')

                # --- Organization Admin ---
                elif user.role == 'org_admin':
                    return redirect('org_dashboard') # Updated from 'orgmain' for consistency

                # --- Security Guard ---
                elif user.role == 'guard':
                    return redirect('guard_homepage')

                else:
                    return redirect('homepage')
            else:
                return redirect('homepage')
        else:
            messages.error(request, "Incorrect password.")
            return render(request, 'login.html', context)

    return render(request, 'login.html')

# ...existing code...
ROLE_TEMPLATE_MAP = {
    "clinic_admin": "roles/clinic_admin.html",
    "guidance": "roles/guidance_admin.html",
    "scholarship_admin": "roles/scholarship_admin.html",
    "placement_officer": "roles/placement_admin.html",
    "alumni_officer": "roles/alumni_admin.html",
    "community_admin": "roles/community_admin.html",
    "org_admin": "roles/org_admin.html",
    "discipline_officer": "roles/discipline_admin.html",
    "student_life_admin": "adminmain.html",
    "staff": "roles/staff_med.html",
}

def get_base_template(user):
    """
    Return base template name for the given user with precedence:
      - unauthenticated -> 'main.html'
      - superuser         -> 'adminmain.html'
      - role mapping      -> ROLE_TEMPLATE_MAP
      - staff fallback    -> 'adminmain.html'
      - default           -> 'main.html'
    """
    if not getattr(user, "is_authenticated", False):
        return "main.html"

    if getattr(user, "is_superuser", False):
        return "adminmain.html"

    role = getattr(user, "role", None)
    if role:
        template = ROLE_TEMPLATE_MAP.get(role)
        if template:
            return template

    if getattr(user, "is_staff", False):
        return "adminmain.html"

    return "main.html"
# ...existing code...
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from itertools import chain
from operator import itemgetter
import datetime  # MAKE SURE THIS IS IMPORTED

# --- Import all relevant models ---
from ..models.guidance import (
    counseling_schedule, 
    exit_interview_db, 
    OjtAssessment, 
    studentInfo
)
from ..models.job_placement import TransactionReport, SeminarAttendance
from ..models.medical import (
    TransactionRecord as MedicalTransaction, 
    PatientRequest, 
    FacultyRequest, 
    DentalRecords, 
    EmergencyHealthAssistanceRecord
)
from ..models.student_life import BorrowingRecord, RequestedGMC
from ..models.community import Donation, MOD
from ..models.alumni import Alumni, graduateForm
from ..models.scholarship import applicants, Requirement as ScholarshipRequirement
from ..models.discipline import CaseProfile

# --- Helper Functions ---

def normalize_to_date(dt_obj):
    """
    Converts a datetime.datetime object to a datetime.date object.
    If it's already a date, or None, it returns it as-is.
    """
    if dt_obj is None:
        return datetime.date.min
    if isinstance(dt_obj, datetime.datetime):
        return dt_obj.date()
    return dt_obj

def get_user_name(item):
    """
    Tries to get a user-friendly name from various related user/patient/student
    fields found across the different models.
    """
    try:
        if hasattr(item, 'user') and item.user:
            if hasattr(item.user, 'get_full_name'):
                return item.user.get_full_name() or item.user.username
            else:
                return str(item.user)
        if hasattr(item, 'student') and item.student:
            return f"{item.student.firstname} {item.student.lastname}"
        if hasattr(item, 'studID') and item.studID:
            return f"{item.studID.firstname} {item.studID.lastname}"
        if hasattr(item, 'student_id') and item.student_id:
            return f"{item.student_id.firstname} {item.student_id.lastname}"
        if hasattr(item, 'faculty') and item.faculty:
            return f"{item.faculty.firstname} {item.faculty.lastname}"
        if hasattr(item, 'patient') and item.patient:
            return get_user_name(item.patient)
        if hasattr(item, 'donor_name') and item.donor_name:
            return item.donor_name
        if hasattr(item, 'name') and item.name:
            return item.name
    except Exception:
        pass
    
    return "System/Unknown"

# --- Main Transaction View ---

@login_required
def view_transaction_history(request):
    """
    Consolidates records from ALL app models to create a single,
    chronological transaction history, AND provides separate lists
    for each module to power a tabbed view.
    """
    
    all_transactions = []
    medical_transactions = []
    alumni_transactions = []
    guidance_transactions = []
    student_life_transactions = []
    job_placement_transactions = []
    scholarship_transactions = []
    discipline_transactions = []
    community_transactions = []

    # --- 1. Medical Module ---
    med_records = MedicalTransaction.objects.all().select_related('patient__user')
    for record in med_records:
        medical_transactions.append({
            'date': record.transac_date,
            'is_datetime': isinstance(record.transac_date, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(record),
            'event_type': 'Medical Transaction',
            'description': record.transac_type,
            'status': 'Completed',
            'source_app': 'Medical'
        })
    
    med_requests = PatientRequest.objects.all().select_related('patient__user', 'faculty')
    for req in med_requests:
        medical_transactions.append({
            'date': req.date_requested,
            'is_datetime': isinstance(req.date_requested, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(req),
            'event_type': 'Medical Request',
            'description': req.request_type,
            'status': req.get_status_display(),
            'source_app': 'Medical'
        })

    # --- 2. Alumni Module ---
    alumni_id_reqs = Alumni.objects.all().select_related('student')
    for req in alumni_id_reqs:
        event_date = req.claimed_date or (datetime.datetime.combine(req.alumnidate, datetime.time()) if req.alumnidate else None)
        if event_date:
            alumni_transactions.append({
                'date': event_date,
                'is_datetime': isinstance(event_date, datetime.datetime), # <-- ADD THIS
                'user_name': get_user_name(req),
                'event_type': 'Alumni ID Request',
                'description': f"Alumni ID for {get_user_name(req)}",
                'status': 'Claimed' if req.claimed_date else ('Approved' if req.approved else 'Pending'),
                'source_app': 'Alumni'
            })

    grad_forms = graduateForm.objects.all().select_related('student')
    for form in grad_forms:
        alumni_transactions.append({
            'date': form.dategraduated,
            'is_datetime': isinstance(form.dategraduated, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(form),
            'event_type': 'Graduate Tracer Form',
            'description': f"Tracer Form submitted by {form.firstname} {form.lastname}",
            'status': form.approval_status,
            'source_app': 'Alumni'
        })

    # --- 3. Guidance Module ---
    counsel_reqs = counseling_schedule.objects.all().select_related('studentID')
    for req in counsel_reqs:
        guidance_transactions.append({
            'date': req.dateRecieved,
            'is_datetime': isinstance(req.dateRecieved, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(req),
            'event_type': 'Counseling Request',
            'description': f"Reason: {req.reason}",
            'status': req.status,
            'source_app': 'Guidance'
        })
        
    exit_interviews = exit_interview_db.objects.all().select_related('studentID')
    for req in exit_interviews:
        guidance_transactions.append({
            'date': req.dateRecieved,
            'is_datetime': isinstance(req.dateRecieved, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(req),
            'event_type': 'Exit Interview Request',
            'description': f"Reason: {req.reasonForLeaving}",
            'status': req.status,
            'source_app': 'Guidance'
        })

    # --- 4. Student Life Module ---
    borrow_records = BorrowingRecord.objects.all().select_related('student', 'equipment')
    for record in borrow_records:
        student_life_transactions.append({
            'date': record.date_borrowed,
            'is_datetime': isinstance(record.date_borrowed, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(record),
            'event_type': 'Equipment Borrowing',
            'description': f"Borrowed: {record.equipment.equipmentName}",
            'status': 'Borrowed',
            'source_app': 'Student Life'
        })
        if record.is_returned and record.date_returned:
            student_life_transactions.append({
                'date': record.date_returned,
                'is_datetime': isinstance(record.date_returned, datetime.datetime), # <-- ADD THIS
                'user_name': get_user_name(record),
                'event_type': 'Equipment Return',
                'description': f"Returned: {record.equipment.equipmentName}",
                'status': 'Returned',
                'source_app': 'Student Life'
            })
            
    gmc_requests = RequestedGMC.objects.all().select_related('student')
    for req in gmc_requests:
        student_life_transactions.append({
            'date': req.request_date,
            'is_datetime': isinstance(req.request_date, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(req),
            'event_type': 'Good Moral Request',
            'description': f"Reason: {req.reason}",
            'status': 'Processed' if req.processed else 'Pending',
            'source_app': 'Student Life'
        })

    # --- 5. Job Placement Module ---
    jp_reports = TransactionReport.objects.all().select_related('content_type')
    for report in jp_reports:
        user_name = get_user_name(report)
        job_placement_transactions.append({
            'date': report.date_created,
            'is_datetime': isinstance(report.date_created, datetime.datetime), # <-- ADD THIS
            'user_name': user_name,
            'event_type': 'System Action',
            'description': report.action,
            'status': report.user_type,
            'source_app': 'Job Placement'
        })

    # --- 6. Scholarship Module ---
    applications = applicants.objects.all().select_related('studID__user')
    for app in applications:
        app_date = app.studID.user.date_joined if app.studID and hasattr(app.studID, 'user') and app.studID.user else datetime.datetime.now()
        scholarship_transactions.append({
            'date': app_date,
            'is_datetime': isinstance(app_date, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(app),
            'event_type': 'Scholarship Application',
            'description': f"Applied for {app.scholar_type}",
            'status': app.status,
            'source_app': 'Scholarship'
        })

    req_subs = ScholarshipRequirement.objects.all().select_related('studID', 'scholar_ID')
    for sub in req_subs:
        scholarship_transactions.append({
            'date': sub.submission_date,
            'is_datetime': isinstance(sub.submission_date, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(sub),
            'event_type': 'Scholarship Requirement',
            'description': f"Submitted requirements for {sub.scholar_type or 'scholarship'}",
            'status': sub.status,
            'source_app': 'Scholarship'
        })

    # --- 7. Discipline Module ---
    cases = CaseProfile.objects.all().select_related('student')
    for case in cases:
        discipline_transactions.append({
            'date': case.date_reported,
            'is_datetime': isinstance(case.date_reported, datetime.datetime), # <-- ADD THIS
            'user_name': get_user_name(case),
            'event_type': 'Discipline Case',
            'description': f"Offense: {case.get_offense_type_display()}",
            'status': case.status,
            'source_app': 'Discipline'
        })
        
    # --- 8. Community Module ---
    donations = Donation.objects.all().select_related('project')
    for donation in donations:
        community_transactions.append({
            'date': donation.created_at,
            'is_datetime': isinstance(donation.created_at, datetime.datetime), # <-- ADD THIS
            'user_name': donation.donor_name or 'Anonymous',
            'event_type': 'Project Donation',
            'description': f"Donated {donation.amount} to {donation.project.title}",
            'status': 'Completed',
            'source_app': 'Community'
        })

    mod_donations = MOD.objects.all()
    for mod in mod_donations:
        community_transactions.append({
            'date': mod.date,
            'is_datetime': isinstance(mod.date, datetime.datetime), # <-- ADD THIS
            'user_name': mod.name,
            'event_type': 'General Donation',
            'description': f"Donated: {mod.donated} ({mod.donation_type})",
            'status': mod.status or 'Unknown',
            'source_app': 'Community'
        })

    # --- Final Consolidation and Sorting ---
    
    all_transactions = list(chain(
        medical_transactions,
        alumni_transactions,
        guidance_transactions,
        student_life_transactions,
        job_placement_transactions,
        scholarship_transactions,
        discipline_transactions,
        community_transactions
    ))
    
    key_func = lambda item: normalize_to_date(item.get('date'))

    sorted_all_transactions = sorted(all_transactions, key=key_func, reverse=True)
    
    # --- Prepare Context for Template ---
    context = {
        'all_transactions': sorted_all_transactions,
        
        'medical_transactions': sorted(medical_transactions, key=key_func, reverse=True),
        'alumni_transactions': sorted(alumni_transactions, key=key_func, reverse=True),
        'guidance_transactions': sorted(guidance_transactions, key=key_func, reverse=True),
        'student_life_transactions': sorted(student_life_transactions, key=key_func, reverse=True),
        'job_placement_transactions': sorted(job_placement_transactions, key=key_func, reverse=True),
        'scholarship_transactions': sorted(scholarship_transactions, key=key_func, reverse=True),
        'discipline_transactions': sorted(discipline_transactions, key=key_func, reverse=True),
        'community_transactions': sorted(community_transactions, key=key_func, reverse=True),
    }

    return render(request, 'reports/transaction_report.html', context)

def student_life_dashboard(request):
    return render(request, 'student_life_staff.html')

def scholarship_dashboard(request):
    return render(request, 'scholarship_officer.html')


def clinic_dashboard(request):
    return render(request, 'roles/clinic_admin.html')

def placement_dashboard(request):
    return render(request, 'placement_officer.html')

def discipline_dashboard(request):
    return render(request, 'discipline_officer.html')


def org_dashboard(request):
    return render(request, 'roles/org_admin.html')

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import redirect

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # update_session_auth_hash keeps the user logged in after password change
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully updated!')
            # Redirect back to the page they came from
            return redirect(request.META.get('HTTP_REFERER', 'homepage'))
        else:
            # If there are errors (e.g., password too short), display them
            for error in form.errors.values():
                messages.error(request, error)
            return redirect(request.META.get('HTTP_REFERER', 'homepage'))
    
    # If someone tries to access this URL via GET, send them home
    return redirect('homepage')