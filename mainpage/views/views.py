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

from ..models import studentInfo, staffInfo, TemporaryUser, CustomUser, Organization
from ..forms import RoleAssignForm

User = get_user_model()

logger = logging.getLogger(__name__)

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def signupuser(request):
    context = {}

    if request.method == 'POST':
        user_id = request.POST.get('studID', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        # Validate passwords
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

        # Check if student or staff
        is_student = studentInfo.objects.filter(studID=user_id).exists()
        is_staff = staffInfo.objects.filter(staffID=user_id).exists()

        if not (is_student or is_staff):
            context['error_message'] = "Invalid ID. No matching student or staff found."
            context['studID_value'] = user_id
            context['email_value'] = email
            return render(request, 'scholarship/register.html', context)

        try:
            # Check 1: Does the user_id (username) already exist?
            if User.objects.filter(username=user_id).exists():
                context['error_message'] = "This Student/Staff ID is already registered."
                context['studID_value'] = user_id
                context['email_value'] = email
                return render(request, 'scholarship/register.html', context)

            # Check 2: Does the email already exist?
            if User.objects.filter(email=email).exists():
                context['error_message'] = "This Email is already registered."
                context['studID_value'] = user_id
                context['email_value'] = email
                return render(request, 'scholarship/register.html', context)

            # Generate OTP and hash password
            otp = str(random.randint(100000, 999999))
            hashed_password = make_password(password)

            # Save temporary user or update existing one
            temp_user, created = TemporaryUser.objects.update_or_create(
                username=user_id,
                defaults={
                    'email': email,
                    'password': hashed_password,
                    'otp_code': otp,
                    'created_at': timezone.now()
                }
            )

            # Send OTP to email
            # Send OTP to email
            send_mail(
                'Your Account Verification Code',
                f'Your One-Time Password for registration is: {otp}\nIt is valid for 10 minutes.',
                settings.EMAIL_HOST_USER,  # <-- Use this instead
                [email],
                fail_silently=False,
            )

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

@login_required(login_url='signinuser')
def homepage(request):
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"
    
    if request.user.is_authenticated:
        messages.success(request, f'Welcome back, {request.user.username}!')
    else:
        messages.info(request, 'Welcome to the homepage!')

    return render(request, 'homepage.html', {
        'base_template': base_template
    })

def alumni_main(request):
    return render(request, 'alumni/id_requests.html')

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
            elif hasattr(user, 'role') and user.role == 'student':
                 return redirect('homepage')
            elif hasattr(user, 'role') and user.role in ['clinic_admin', 'staff', 'guidance', 'scholarship_officer', 'placement_officer', 'discipline_officer', 'alumni_officer', 'student_life_staff']:
                 return redirect('adminmain')
            elif hasattr(user, 'role') and user.role == 'guard':
                return redirect('guard_homepage')
            elif hasattr(user, 'role') and user.role == 'org_admin':
                return redirect('org_admin_homepage')
            else:
                 return redirect('homepage')
        else:
            messages.error(request, "Incorrect password.")
            return render(request, 'login.html', context)

    return render(request, 'login.html')