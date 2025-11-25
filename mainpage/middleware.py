import logging
from .models import studentInfo
from .models.alumni import Alumni, graduateForm
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.contrib import messages

logger = logging.getLogger(__name__)
class RoleRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'role'):
            
            # 0. Superusers bypass everything
            if request.user.is_superuser:
                return self.get_response(request)

            # Common paths allowed for ALL users
            global_allowed = [
                '/sao/logout/', 
                'main/login/', 
                '/change-password/', 
                '/media/', 
                '/static/',
                '/admin/' 
            ]

            ROLE_CONFIG = {
                # --- STAFF (Restricted to Medical Sidebar Links) ---
                'staff': { 
                    'dashboard_name': 'student_dashboard', 
                    # specific prefixes based on your sidebar links
                    'allowed_prefixes': [
                        '/med/', 
                        '/medical/', 
                        '/dental/', 
                        '/requests/', 
                        '/requirements/'
                    ] 
                },

                # --- STUDENT ---
                'student': {
                    'dashboard_name': 'student_dashboard', 
                    'allowed_prefixes': ['/main/', '/fe/', '/student/'] 
                },

                # --- MEDICAL / CLINIC ---
                'clinic_admin': { 
                    'dashboard_name': 'admin_dashboard', 
                    'allowed_prefixes': ['/med/', '/medical/', '/clinic/'] 
                },

                # --- GUIDANCE ---
                'guidance': { 
                    'dashboard_name': 'guidance_dashboard', 
                    'allowed_prefixes': ['/guidance/', '/sao/'] 
                },

                # --- SCHOLARSHIP ---
                'scholarship_admin': { 
                    'dashboard_name': 'scholarship_dashboard', 
                    'allowed_prefixes': ['/scholarship/'] 
                },

                # --- JOB PLACEMENT ---
                'placement_officer': { 
                    'dashboard_name': 'placement_dashboard', 
                    'allowed_prefixes': ['/jobplacement/'] 
                },

                # --- ALUMNI ---
                'alumni_officer': { 
                    'dashboard_name': 'alumni_dashboard', 
                    'allowed_prefixes': ['/alumni/', '/alum/'] 
                },

                # --- COMMUNITY INVOLVEMENT ---
                'community_admin': { 
                    'dashboard_name': 'community_dashboard', 
                    'allowed_prefixes': ['/community/'] 
                },

                # --- ORGANIZATION ---
                'org_admin': { 
                    'dashboard_name': 'org_dashboard', 
                    'allowed_prefixes': ['/org/', '/organizations/'] 
                },

                # --- DISCIPLINE ---
                'discipline_officer': { 
                    'dashboard_name': 'discipline_dashboard', 
                    'allowed_prefixes': ['/discipline/'] 
                },

                # --- STUDENT LIFE (MAIN) ---
                'student_life_admin': {
                    'dashboard_name': 'student_life_dashboard',
                    'allowed_prefixes': ['/main/', '/fe/']
                },

                # --- SECURITY GUARD ---
                'guard': {
                    'dashboard_name': 'guard_homepage', 
                    'allowed_prefixes': ['/discipline/'] 
                }
            }

            user_role = request.user.role

            # 2. Check if the user's role is in our restricted list
            if user_role in ROLE_CONFIG:
                config = ROLE_CONFIG[user_role]
                
                # Resolve Dashboard URL
                try:
                    dashboard_url = reverse(config['dashboard_name'])
                except (NoReverseMatch, Exception):
                    dashboard_url = '/' 

                # ALLOW: If user is already at their dashboard
                if request.path.rstrip('/') == dashboard_url.rstrip('/'):
                    return self.get_response(request)

                current_path = request.path
                is_allowed = False

                # A. Check Global Whitelist
                for path in global_allowed:
                    if current_path.startswith(path):
                        is_allowed = True
                        break

                # B. Check Role-Specific Prefixes
                if not is_allowed:
                    for prefix in config['allowed_prefixes']:
                        if current_path.startswith(prefix):
                            is_allowed = True
                            break

                # BLOCK: If path is not allowed, redirect to dashboard
                if not is_allowed:
                    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        messages.error(request, "Access Denied: You are restricted to your department area.")
                    
                    return redirect(dashboard_url)

        response = self.get_response(request)
        return response
class AlumniStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_alumni_approved = False
        request.has_filled_tracer = False

        if getattr(request.user, 'is_authenticated', False):
            try:
                if str(request.user.username).isdigit():
                    student = studentInfo.objects.get(studID=int(request.user.username))
                    alumni = Alumni.objects.filter(student=student, approved=True).first()
                    
                    if alumni:
                        request.is_alumni_approved = True
                        request.has_filled_tracer = graduateForm.objects.filter(student=student).exists()

            except Exception:
                pass 

        response = self.get_response(request)
        return response