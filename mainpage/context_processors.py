from django.conf import settings
from .models import studentInfo, scholars

def alumni_status_context(request):
    """
    Passes the alumni status variables from the middleware
    into the template context.
    """
    return {
        'is_alumni_approved': getattr(request, 'is_alumni_approved', False),
        'has_filled_tracer': getattr(request, 'has_filled_tracer', False)
    }

def role_context(request):
    user = getattr(request, 'user', None)
    role = getattr(user, 'role', None) if user and getattr(user, 'is_authenticated', False) else None
    return {
        'user_role': role,
        'is_org_admin': role == 'org_admin'
    }

def scholarship_status(request):
    if not request.user.is_authenticated:
        return {'is_scholar': False}

    # If the user is staff, don't bother checking
    if request.user.is_staff:
        return {'is_scholar': False}

    try:
        # Get student info from the logged-in user's username (which is their studID)
        student = studentInfo.objects.get(studID=request.user.username)
        
        # Check if that student exists in the scholars table
        is_scholar = scholars.objects.filter(studID=student).exists()
        
        return {'is_scholar': is_scholar}

    except studentInfo.DoesNotExist:
        # If they aren't a student (which they should be if not staff), 
        # they can't be a scholar
        return {'is_scholar': False}
    
def theme_selection(request):
    # Default for unauthenticated or regular users (Students)
    template = 'main.html' 
    
    if request.user.is_authenticated:
        
        # 1. Check Specific Roles
        if hasattr(request.user, 'role'):
            role = request.user.role
            
            if role == 'clinic_admin':
                template = 'roles/clinic_admin.html'
            elif role == 'staff':
                template = 'roles/staff_med.html'
            elif role == 'guidance':
                template = 'roles/guidance_admin.html'
                
            elif role == 'scholarship_admin':
                template = 'roles/scholarship_admin.html'
                
            elif role == 'placement_officer':
                template = 'roles/placement_admin.html'
                
            elif role == 'alumni_officer':
                template = 'alumni_admin.html'
                
            elif role == 'community_admin':
                # Fixed typo: was 'roles/roles/community_admin.html'
                template = 'roles/community_admin.html'
                
            elif role == 'org_admin':
                template = 'roles/org_admin.html'
                
            elif role == 'discipline_officer':
                template = 'roles/discipline_admin.html'
                
            elif role == 'student_life_staff':
                template = 'adminmain.html'


        if template == 'main.html' and (request.user.is_staff or request.user.is_superuser):
            template = 'adminmain.html'
            
    return {'base_template': template}