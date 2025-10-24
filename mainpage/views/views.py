from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='signinuser')  # or the URL name of your login page

def homepage(request):
    if request.user.is_superuser:
        return render(request, 'adminmain.html')
    else:
        return render(request, 'main.html')
def alumni_main(request):
    return render(request, 'alumni/id_requests.html')
def calendar(request):
    return render(request, 'officeOfStudentL/calendarOfEvents.html')
def login_view(request):
    return render(request, 'login.html')
def post(request):
    return render(request, 'scrapper.html')# mainpage/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from ..models import CustomUser
from ..forms import RoleAssignForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from ..models.studentorg import Organization

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def assign_role(request):
    users = CustomUser.objects.all()
    organizations = Organization.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        org_id = request.POST.get('organization_id') or None

        try:
            user = CustomUser.objects.get(id=user_id)
            user.role = role
            
            # Set organization to None if the role is not 'org_admin'
            if role == 'org_admin' and org_id:
                user.organization_id = org_id
            else:
                user.organization = None
            
            user.save()
            messages.success(request, f"{user.username}'s role updated to {user.get_role_display()}.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
        
        return redirect('assign_role')

    # This context dictionary is what gets passed to the template
    context = {
        'users': users,
        'organizations': organizations,
        'role_choices': CustomUser.ROLE_CHOICES,  # This is the line to add
    }
    
    return render(request, 'assign_role.html', context)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings # Import Django settings
import requests # Import the requests library for making HTTP requests
import logging # Import the logging library

# Make sure your User model is imported correctly
from django.contrib.auth import get_user_model
User = get_user_model()

# Get an instance of a logger
logger = logging.getLogger(__name__)

def signinuser(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        recaptcha_response = request.POST.get('g-recaptcha-response') # Get the response token from the form

        # --- reCAPTCHA Verification Step ---
        if not recaptcha_response:
            messages.error(request, "Please complete the reCAPTCHA.")
            return render(request, 'login.html')

        # 1. Check if the secret key is configured in settings.py
        secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', None) # Use SECRET_KEY as recommended
        if not secret_key:
            messages.error(request, "reCAPTCHA is not configured correctly (missing secret key). Please contact the administrator.")
            # Log a more detailed error for the admin
            logger.error("RECAPTCHA_SECRET_KEY is missing in Django settings.")
            return render(request, 'login.html')

        try:
            # Prepare data for Google's verification API
            data = {
                'secret': secret_key,
                'response': recaptcha_response
            }
            # Send verification request to Google
            verify_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, timeout=5) # Added timeout
            verify_response.raise_for_status() # Raise an error for bad status codes
            result = verify_response.json()

        except requests.exceptions.Timeout:
            messages.error(request, "Could not verify reCAPTCHA (timeout). Please try again.")
            logger.warning("reCAPTCHA verification request timed out.")
            return render(request, 'login.html')
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not connect to reCAPTCHA service. Error: {e}")
            logger.error(f"reCAPTCHA connection error: {e}")
            return render(request, 'login.html')
        except Exception as e: # Catch potential JSON errors or other issues
            messages.error(request, f"An unexpected error occurred during reCAPTCHA verification: {e}")
            logger.error(f"Unexpected reCAPTCHA error: {e}")
            return render(request, 'login.html')

        # 2. Check Google's response for success AND potential secret key errors
        if not result.get('success'):
            error_codes = result.get('error-codes', [])
            logger.warning(f"reCAPTCHA verification failed. Error codes: {error_codes}") # Log errors

            if 'missing-input-secret' in error_codes:
                messages.error(request, "reCAPTCHA configuration error (missing secret). Please contact the administrator.")
            elif 'invalid-input-secret' in error_codes:
                 messages.error(request, "reCAPTCHA configuration error (invalid secret). Please contact the administrator.")
            else:
                 messages.error(request, "Invalid reCAPTCHA. Please try again.") # Generic message for other errors

            return render(request, 'login.html')
        # --- End reCAPTCHA Validation ---

        # --- User Authentication (Proceed ONLY if reCAPTCHA was successful) ---
        try:
            # Find the user by email first
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Account does not exist.")
            return render(request, 'login.html')

        # Check if account is active
        if not user_obj.is_active:
            messages.error(request, "This account is inactive. Contact admin.")
            return render(request, 'login.html')

        # Authenticate using the username found via email
        user = authenticate(request, username=user_obj.username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}!") # Optional welcome message

            # Redirect based on user role (Make sure 'role' attribute exists on your User model)
            if user.is_superuser:
                return redirect('adminmain') # Use your actual admin URL name
            elif hasattr(user, 'role') and user.role == 'student':
                 return redirect('homepage') # Use your actual student URL name
            elif hasattr(user, 'role') and user.role in ['clinic_admin', 'staff', 'guidance', 'scholarship_officer', 'placement_officer', 'discipline_officer', 'alumni_officer', 'student_life_staff']: # Check for any staff role
                 return redirect('adminmain') # Use your actual staff URL name
            elif hasattr(user, 'role') and user.role == 'guard':
                return redirect('guard_homepage') # Example: Redirect guard to a specific page
            elif hasattr(user, 'role') and user.role == 'org_admin':
                return redirect('org_admin_homepage') # Example: Redirect org admin to a specific page
            else:
                 # Fallback for users without specific roles or profiles
                 return redirect('homepage') # Use your actual default homepage URL name
        else:
            messages.error(request, "Incorrect password.")
            return render(request, 'login.html')

    # If GET request, just render the login page
    return render(request, 'login.html')
