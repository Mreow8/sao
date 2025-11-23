
import logging
from .models import studentInfo
from .models.alumni import Alumni, graduateForm

logger = logging.getLogger(__name__)
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages



class RoleRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Check if user is logged in
        if request.user.is_authenticated and hasattr(request.user, 'role'):
            
            # 2. Logic specifically for CLINIC ADMIN
            if request.user.role == 'clinic_admin':
                
                # --- THE LOOP BREAKER (Crucial Fix) ---
                try:
                    dashboard_url = reverse('clinic_dashboard') # Must match name in urls.py
                except:
                    # Fallback if URL name is wrong, prevents crash but might loop if paths don't match
                    dashboard_url = '/main/dashboard/clinic/' 

                # If the user is ALREADY at the dashboard, stop checking and let them in.
                # We strip '/' to ensure /clinic and /clinic/ are treated the same.
                if request.path.rstrip('/') == dashboard_url.rstrip('/'):
                    return self.get_response(request)

                # --- Allowed Paths Configuration ---
                allowed_prefixes = [
                    '/clinic/',       
                    '/medical/',      
                    '/media/',        
                    '/static/',
                    '/med/',
                    '/admin/', # Usually needed for logout or internal tools
                ]
                
                allowed_exact_paths = [
                    reverse('homepage'),        
                    '/logout/',
                    dashboard_url, # Explicitly allow the dashboard
                ]

                current_path = request.path
                is_allowed = False
                
                # Check exact matches
                if current_path in allowed_exact_paths:
                    is_allowed = True
                
                # Check prefixes
                if not is_allowed:
                    for prefix in allowed_prefixes:
                        if current_path.startswith(prefix):
                            is_allowed = True
                            break

                # If they are trying to access a restricted page
                if not is_allowed:
                    # Only show message if it's not an automated request (optional)
                    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        messages.error(request, "Access Denied: Restricted to Medical Personnel only.")
                    
                    return redirect('homepage')

        response = self.get_response(request)
        return response
class AlumniStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set default values for all users
        request.is_alumni_approved = False
        request.has_filled_tracer = False

        logger.debug("AlumniStatusMiddleware START path=%s user=%s authenticated=%s",
                     request.path,
                     getattr(request, 'user', None),
                     getattr(request.user, 'is_authenticated', False))

        # Check only if the user is logged in
        if getattr(request.user, 'is_authenticated', False):
            try:
                # 1. Find the student record
                student = studentInfo.objects.get(studID=int(request.user.username))

                # 2. Check if they are an APPROVED alumnus
                alumni = Alumni.objects.get(student=student, approved=True)
                request.is_alumni_approved = True

                # 3. If they are, check if they have filled the tracer form
                request.has_filled_tracer = graduateForm.objects.filter(student=student).exists()

            except (studentInfo.DoesNotExist, Alumni.DoesNotExist, ValueError, TypeError) as e:
                logger.debug("AlumniStatusMiddleware lookup failed: %s", e)

        logger.debug("AlumniStatusMiddleware END path=%s is_alumni_approved=%s has_filled_tracer=%s",
                     request.path, request.is_alumni_approved, request.has_filled_tracer)

        response = self.get_response(request)
        return response
# ...existing code...