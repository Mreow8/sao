from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from mainpage.models import studentInfo
from mainpage.models.alumni import graduateForm # <-- Import graduateForm

def tracer_gatekeeper_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login') 

        try:
            student = studentInfo.objects.get(studID=request.user.username)
        except studentInfo.DoesNotExist:
            messages.error(request, 'Your user account is not linked to a student profile.')
            return redirect('homepage') 

        try:
            form = graduateForm.objects.get(student=student)
            
            if form.approval_status == 'Accepted':
                return view_func(request, *args, **kwargs)
            
            if request.resolver_match.url_name == 'graduateTracer':
                return view_func(request, *args, **kwargs)

            if form.approval_status == 'Pending':
                messages.warning(request, 'Your tracer form is still pending approval. Please check back later.')
            elif form.approval_status == 'Declined':
                messages.error(request, 'Your tracer form submission was declined. Please contact an administrator.')
            
            return redirect('graduateTracer') 

        except graduateForm.DoesNotExist:
            if request.resolver_match.url_name == 'graduateTracer':
                return view_func(request, *args, **kwargs)
            
            messages.warning(request, 'You must complete the Graduate Tracer form to access any alumni features.')
            return redirect('graduateTracer')
        
    return _wrapped_view
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
        
        # 1. Check for authenticated user (should be covered by @login_required)
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login') 

        # 2. Find the student and alumni profile
        try:
            student = studentInfo.objects.get(studID=request.user.username)
            alumni = Alumni.objects.get(student=student)
        except studentInfo.DoesNotExist:
            messages.error(request, "Your user account is not linked to a student profile.")
            return redirect('homepage') 
        except Alumni.DoesNotExist:
            messages.error(request, "You must register for an Alumni ID first.")
            return redirect('idRequest') # Send them to the ID request page

        # 3. CRITICAL CHECK: Allow access to the 'graduateTracer' page
        #    This page has its own logic to show the pending/accepted/blank form.
        if view_func.__name__ == 'graduateTracer':
            return view_func(request, *args, **kwargs)

        # 4. For ALL OTHER alumni pages, check the form status
        try:
            # Find their submitted form
            grad_form = graduateForm.objects.get(alumniID=alumni)
            
            if grad_form.approval_status == 'Accepted':
                # SUCCESS: They are fully approved. Let them access the page.
                return view_func(request, *args, **kwargs)
            
            elif grad_form.approval_status == 'Pending':
                # PENDING: Block access and redirect to the tracer page
                messages.warning(request, "Your tracer form is still pending approval. You cannot access this page yet.")
                return redirect('graduateTracer')
                
            elif grad_form.approval_status == 'Declined':
                # DECLINED: Block access and redirect to the tracer page
                messages.error(request, "Your tracer form submission was declined.")
                return redirect('graduateTracer')
                
        except graduateForm.DoesNotExist:
            # NO FORM: They have an Alumni ID but haven't submitted the form.
            messages.error(request, "You must complete the Graduate Tracer form to access this page.")
            return redirect('graduateTracer')

        # Failsafe redirect
        messages.error(request, "You do not have permission to view this page.")
        return redirect('homepage')
    
    return _wrapped_view                                                                                                             
def staff_role(user):
  
    return user.role != 'student'