from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.contrib import messages

@login_required(login_url='signinuser')  # or the URL name of your login page


def homepage(request):
    # This logic is correct. An anonymous user will have is_staff=False
    # and is_superuser=False, so they will get 'main.html'.
    base_template = "adminmain.html" if request.user.is_staff or request.user.is_superuser else "main.html"
    
    # Check if the user is logged in (not an 'AnonymousUser')
    if request.user.is_authenticated:
        # Use the user's username in the message
        messages.success(request, f'Welcome back, {request.user.username}!')
    else:
        messages.info(request, 'Welcome to the homepage!')

    return render(request, 'homepage.html', {
        'base_template': base_template
        # NOTE: No need to add 'user': request.user
        # The render() function does this automatically.
    })
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
# In your views.py file

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from ..models import CustomUser, Organization # Make sure all models are imported

def assign_role(request):
    # --- Get parameters for Filter, Search, Sort, and Pagination ---
    
    # 1. NEW: Role Filter
    role_filter = request.GET.get('role', '') # Get the role filter
    
    # 2. Search query
    query = request.GET.get('q', '')
    
    # 3. Sort column and direction
    sort_by = request.GET.get('sort', 'username')
    direction = request.GET.get('dir', 'asc')

    # --- Build the QuerySet ---
    
    # Start with all users
    users_list = CustomUser.objects.all()

    # 1. NEW: Apply Role Filter (if one was selected)
    if role_filter:
        users_list = users_list.filter(role=role_filter)

    # 2. Apply Search Filter (if a query exists)
    if query:
        users_list = users_list.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    # 3. Apply Sorting
    valid_sort_fields = ['username', 'email', 'role']
    if sort_by not in valid_sort_fields:
        sort_by = 'username' # Default to username if invalid
        
    order_field = f"{'-' if direction == 'desc' else ''}{sort_by}"
    users_list = users_list.order_by(order_field)

    # 4. Apply Pagination
    paginator = Paginator(users_list, 25)  # Show 25 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- Handle POST request (no change here) ---
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
        
        # Redirect back to the same page, preserving all GET parameters
        return redirect(request.get_full_path())

    # --- Prepare Context for Template ---
    organizations = Organization.objects.all()
    
    context = {
        'page_obj': page_obj,
        'organizations': organizations,
        'role_choices': CustomUser.ROLE_CHOICES,
        
        # Pass back search/sort/filter state to the template
        'query': query,
        'sort_by': sort_by,
        'direction': direction,
        'role_filter': role_filter, # NEW: Pass the role filter back
    }
    
    return render(request, 'assign_role.html', context)
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
        # --- GET FORM DATA FIRST ---
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # --- PREPARE CONTEXT FOR ERRORS ---
        # This context will be passed back to the template to repopulate the email
        context = {'email': email}

        # --- reCAPTCHA Verification Step ---
        if not recaptcha_response:
            messages.error(request, "Please complete the reCAPTCHA.")
            return render(request, 'login.html', context) # Pass context

        secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', None)
        if not secret_key:
            messages.error(request, "reCAPTCHA is not configured correctly (missing secret key). Please contact the administrator.")
            logger.error("RECAPTCHA_SECRET_KEY is missing in Django settings.")
            return render(request, 'login.html', context) # Pass context

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
            return render(request, 'login.html', context) # Pass context
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not connect to reCAPTCHA service. Error: {e}")
            logger.error(f"reCAPTCHA connection error: {e}")
            return render(request, 'login.html', context) # Pass context
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during reCAPTCHA verification: {e}")
            logger.error(f"Unexpected reCAPTCHA error: {e}")
            return render(request, 'login.html', context) # Pass context

        if not result.get('success'):
            error_codes = result.get('error-codes', [])
            logger.warning(f"reCAPTCHA verification failed. Error codes: {error_codes}")

            if 'missing-input-secret' in error_codes:
                messages.error(request, "reCAPTCHA configuration error (missing secret). Please contact the administrator.")
            elif 'invalid-input-secret' in error_codes:
                 messages.error(request, "reCAPTCHA configuration error (invalid secret). Please contact the administrator.")
            else:
                 messages.error(request, "Invalid reCAPTCHA. Please try again.")

            return render(request, 'login.html', context) # Pass context
        # --- End reCAPTCHA Validation ---

        # --- User Authentication ---
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Account does not exist.")
            return render(request, 'login.html', context) # Pass context

        if not user_obj.is_active:
            messages.error(request, "This account is inactive. Contact admin.")
            return render(request, 'login.html', context) # Pass context

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
            return render(request, 'login.html', context) # Pass context

    # If GET request, just render the login page
    return render(request, 'login.html')