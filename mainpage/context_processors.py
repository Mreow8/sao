def alumni_status_context(request):
    """
    Passes the alumni status variables from the middleware
    into the template context.
    """
    return {
        'is_alumni_approved': getattr(request, 'is_alumni_approved', False),
        'has_filled_tracer': getattr(request, 'has_filled_tracer', False)
    }
from .models import studentInfo, scholars  # Make sure to import your models

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