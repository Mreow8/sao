from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

def sao_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type == 'sao admin':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse('Permission denied: SAO admin access required.', status=403)
    return _wrapped_view

def medical_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type == 'medical admin':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse('Permission denied: Medical admin access required.', status=403)
    return _wrapped_view
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
# In mainpage/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from ..models import studentInfo
from ..models.alumni import Alumni, graduateForm
from functools import wraps
                                                                                                                                                                                                                                                                                                                                                                             
def alumni_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        
        # 1. Check if logged in
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to continue.')
            return redirect('login') 

        try:
            # 2. Check for student profile
            student = studentInfo.objects.get(studID=request.user.username)
        except studentInfo.DoesNotExist:
            messages.error(request, 'Your user account is not linked to a student profile.')
            return redirect('homepage') 

        # 3. 'student_status' check is removed, as requested.

        # 4. Get or create their alumni record.
        alumni_obj, created = Alumni.objects.get_or_create(student=student)

        # 5. Check if they have filled out the tracer form
        has_filled_form = graduateForm.objects.filter(alumniID=alumni_obj).exists()

        # 6. Get the name of the page they are trying to visit
        current_url_name = request.resolver_match.url_name

        # 7. The logic to force them to the tracer form
        if not has_filled_form:
            # If they haven't filled the form...
            
            if current_url_name == 'graduateTracer' or current_url_name == 'graduateTracer_submit':
                # ...but they are *already* on the tracer page, let them stay.
                return view_func(request, *args, **kwargs)
            else:
                # ...and they are trying to go *anywhere else* (like idRequest),
                # force them to the tracer page first.
                messages.info(request, 'Please complete the Graduate Tracer form before accessing other alumni features.')
                return redirect('graduateTracer')
        
        # 8. They HAVE filled the form, let them go anywhere.
        return view_func(request, *args, **kwargs)
        
    return _wrapped_view
def staff_role(user):
  
    return user.role != 'student'