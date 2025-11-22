# mainpage/views/discipline.py
# (Or wherever your discipline.py file is)

from datetime import datetime
import json
import logging
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# --- Your Models and Forms ---
from ..models import (
    studentInfo,
    counseling_schedule,
    CaseProfile,
    CommunityServiceTracker,CommunityService,
)
from ..forms import (
    CaseProfileForm,
    CommunityServiceForm,
    CounselingSchedulerForm,
)

logger = logging.getLogger(__name__)
def _format_decimal_hours(decimal_hours):
    """Converts decimal hours (e.g., 2.5) into a string ('2h 30m')"""
    if decimal_hours is None:
        decimal_hours = 0.0
    
    hours = int(decimal_hours)
    # Calculate minutes from the fractional part
    minutes = int(round((decimal_hours - hours) * 60))
    
    # Handle rollover if rounding pushes minutes to 60
    if minutes == 60:
        hours += 1
        minutes = 0
        
    return f"{hours}h {minutes}m"
@login_required
def serviceTracker(request, student_id):
    student = get_object_or_404(studentInfo, studID=student_id)

    # use case__student to get records for this student's cases
    community_services = CommunityServiceTracker.objects.filter(case__student=student).order_by('-service_date')
    time_rendered = [svc.time_rendered() for svc in community_services]

    # compute totals using total_hours_decimal()
    total_hours = 0
    total_minutes = 0
    for svc in community_services:
        th = svc.total_hours_decimal() or 0.0
        h = int(th)
        m = int(round((th - h) * 60))
        total_hours += h
        total_minutes += m

    total_hours += total_minutes // 60
    total_minutes = total_minutes % 60

    if student.community_service_hours is not None:
        student.sanction_completed = (total_hours >= student.community_service_hours)
        student.save()

    if request.method == "POST":
        date_str = request.POST.get('service_date')
        service_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_in = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        student_signature = request.FILES.get('student_signature') or request.POST.get('student_signature')
        remarks = request.POST.get('remarks')

        # find a CaseProfile for this student (use most recent)
        case = CaseProfile.objects.filter(student=student).order_by('-date_reported').first()
        if not case:
            messages.error(request, "No case found for this student. Create a case first.")
            return redirect(reverse('community-service-tracker', args=[student_id]))

        CommunityServiceTracker.objects.create(
            case=case,
            service_date=service_date,
            time_in=time_in,
            time_out=time_out,
            student_signature=student_signature,
            remarks=remarks
        )
        return redirect(reverse('community-service-tracker', args=[student_id]))

    context = {
        'student': student,
        'community_services': community_services,
        'time_rendered': time_rendered,
        'total_hours': total_hours,
        'total_minutes': total_minutes,
    }
    return render(request, 'discipline/comm_service.html', context)

@require_POST
@login_required
def update_case_status(request, case_id):
    try:
        case = get_object_or_404(CaseProfile, id=case_id)
        
        # Load the new status from the request
        data = json.loads(request.body)
        new_status = data.get('status')

        # A list of valid statuses from your model
        valid_statuses = ['Pending', 'Under Investigation', 'Resolved']

        if new_status in valid_statuses:
            case.status = new_status
            case.save()

            # --- NEW LOGIC: SEND EMAIL IF RESOLVED ---
            if new_status == 'Resolved':
                try:
                    # Check if student has an email address
                    # Adjust 'email' below if your model uses a different field name (e.g., 'email_address')
                    student_email = getattr(case.student, 'email', None) 
                    
                    if student_email:
                        subject = f"Case Resolved: {case.offense_type}"
                        message = (
                            f"Dear {case.student.firstname},\n\n"
                            f"This email is to inform you that your case regarding '{case.offense_type}' "
                            f"reported on {case.date_reported} has been officially marked as RESOLVED.\n\n"
                            f"If you have any questions, please contact the Student Affairs Office.\n\n"
                            "Best regards,\n"
                            "Student Affairs Office"
                        )
                        
                        send_mail(
                            subject,
                            message,
                            settings.EMAIL_HOST_USER, # From email
                            [student_email],          # To email
                            fail_silently=False,
                        )
                        logger.info(f"Resolution email sent to {student_email}")
                    else:
                        logger.warning(f"Case {case_id} resolved, but student {case.student.studID} has no email address.")

                except Exception as email_error:
                    # We log the error but DO NOT stop the function. 
                    # The status update was successful, even if the email failed.
                    logger.error(f"Failed to send resolution email: {email_error}")
            # --- END NEW LOGIC ---

            return JsonResponse({"success": True, "new_status": new_status})
        else:
            return JsonResponse({"success": False, "error": "Invalid status value"}, status=400)
            
    except Exception as e:
        logger.error(f"Error updating status for case {case_id}: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)
@login_required
def case_profile_create(request):
    user = request.user
    students = studentInfo.objects.all()
    base_template = (
        "adminmain.html" 
        if user.is_staff or user.is_superuser or getattr(user, 'role', None) == 'guard'
        else "main.html"
    )

    if request.method == 'POST':
        form = CaseProfileForm(request.POST, request.FILES)
        if form.is_valid():
            student_id = request.POST.get('student')
            if not student_id:
                messages.error(request, "Student ID is required.")
            else:
                try:
                    student = studentInfo.objects.get(studID=student_id)
                    
                    # Save the case (this is the same as your code)
                    case = form.save(commit=False)
                    case.student = student
                    case.reported_by = form.cleaned_data.get('reported_by', user.username)
                    case.save()
                    
                    messages.success(request, "Case profile saved successfully.")

                    # --- THIS IS THE NEW LOGIC YOU ASKED FOR ---
                    
                    # 1. We check the 'action_taken' value from the saved case
                    #    (This assumes the value in your dropdown is "Counseling")
                    if case.action_taken == 'Counseling':
                        
                        # 2. Add a message to prompt the admin
                        messages.info(request, f"Please create a counseling schedule for {student.firstname}.")
                        
                        # 3. Redirect to your *existing* counseling_form_view
                        return redirect('counseling_form', case_id=case.id)
                    
                    else:
                        # 4. If it's not counseling, just go to the list as normal
                        return redirect('case_list')
                    
                    # --- END OF NEW LOGIC ---

                except studentInfo.DoesNotExist:
                    messages.error(request, f"Student with ID {student_id} not found.")
                except Exception as e:
                    logger.error(f"Error saving case for student {student_id}: {e}")
                    messages.error(request, "An error occurred while saving the case profile.")
        else:
            logger.warning(f"Invalid form submission: {form.errors}")
            messages.error(request, "Please correct the errors in the form.")
    else:
        # Set initial 'reported_by' for the create form
        form = CaseProfileForm(initial={'reported_by': user.username})

    context = {
        'form': form,
        'students': students,
        'base_template': base_template,
    }
    return render(request, 'discipline/case_profile.html', context)


# Make sure to add this import at the top of your views.py
from django.core.paginator import Paginator

# ... (all your other imports) ...
@login_required
def case_list(request):
    user = request.user
    base_template = (
        "adminmain.html" 
        if user.is_staff or user.is_superuser or getattr(user, 'role', None) == 'guard'
        else "main.html"
    )

    # --- 1. Get all GET parameters ---
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')
    
    # --- NEW: Get filter parameters ---
    status_filter = request.GET.get('status_filter', '')
    offense_filter = request.GET.get('offense_filter', '')

    # --- 2. Define Sort Fields ---
    valid_sort_fields = {
        'student': 'student__firstname',
        'offense': 'offense_type',
        'date': 'date_reported',
        'status': 'status',
    }
    sort_field = valid_sort_fields.get(sort_by, 'date_reported')
    order_string = f'-{sort_field}' if order == 'desc' else sort_field
    
    # --- 3. Get Base Queryset based on Role ---
    if user.is_authenticated and (user.is_staff or user.is_superuser or getattr(user, 'role', None) == 'guard'):
        all_cases = CaseProfile.objects.select_related('student').all() 
    elif user.is_authenticated and getattr(user, 'role', None) == 'student':
        all_cases = CaseProfile.objects.select_related('student').filter(student__studID=user.username)
    else:
        all_cases = CaseProfile.objects.none()

    # --- 4. Apply Search Filter ---
    if search_query:
        all_cases = all_cases.filter(
            Q(student__studID__icontains=search_query) |
            Q(student__firstname__icontains=search_query) |
            Q(student__lastname__icontains=search_query) |
            Q(offense_type__icontains=search_query) |
            Q(custom_offense__icontains=search_query)
        )
    
    # --- NEW: Apply Dropdown Filters ---
    if status_filter:
        all_cases = all_cases.filter(status=status_filter)
    
    if offense_filter:
        all_cases = all_cases.filter(offense_type=offense_filter)

    # --- 5. Apply Sorting ---
    all_cases = all_cases.order_by(order_string)

    # --- 6. Prepare Query Strings for Links ---
    # This logic already works! It copies all GET params,
    # so 'status_filter' and 'offense_filter' will be included.
    pagination_params = request.GET.copy()
    if 'page' in pagination_params:
        del pagination_params['page']
    pagination_params_str = f"&{pagination_params.urlencode()}" if pagination_params else ""

    sort_params = request.GET.copy()
    for key in ['sort', 'order', 'page']:
        if key in sort_params:
            del sort_params[key]
    sort_params_str = f"&{sort_params.urlencode()}" if sort_params else ""

    # --- 7. Apply Pagination ---
    paginator = Paginator(all_cases, 10) # 10 cases per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- NEW: Get choices for dropdowns ---
    # Get status choices (based on what's in your JS)
    status_choices = ['Pending', 'Under Investigation', 'Resolved']
    # Get all unique offense types from the database
    offense_choices = CaseProfile.objects.order_by('offense_type').values_list('offense_type', flat=True).distinct()

    # --- 8. Context (Updated) ---
    context = {
        'page_obj': page_obj, 
        'base_template': base_template,
        'current_sort': sort_by,
        'current_order': order,
        'search_query': search_query,
        'pagination_params': pagination_params_str,
        'sort_params': sort_params_str,
        
        # --- NEW CONTEXT ---
        'status_choices': status_choices,
        'offense_choices': offense_choices,
        'current_status_filter': status_filter,
        'current_offense_filter': offense_filter,
    }
    return render(request, 'discipline/case_list.html', context)
@login_required
def student_case_view(request, studID):
  
    user = request.user
    
    # Determine the correct base template based on user role
    base_template = (
        "adminmain.html" 
        if user.is_staff or user.is_superuser or getattr(user, 'role', None) == 'guard'
        else "main.html"
    )

    try:
        # 1. Get the student object from the studID in the URL
        student = get_object_or_404(studentInfo, studID=studID)
        
        # 2. Get all cases for that student, ordered by most recent
        student_cases = CaseProfile.objects.filter(student=student).order_by('-date_reported')

        # 3. Pass the student and their cases to the template
        context = {
            'student': student,
            'student_cases': student_cases,
            'base_template': base_template,
        }
        
        return render(request, 'discipline/student_case_view.html', context)

    except Exception as e:
        logger.error(f"Error loading student case view for {studID}: {e}")
        messages.error(request, "Could not load student case profile.")
        return redirect('case_list')
@login_required
def case_edit(request, case_id):
    case = get_object_or_404(CaseProfile, id=case_id)
    if request.method == "POST":
        form = CaseProfileForm(request.POST, request.FILES, instance=case)
        if form.is_valid():
            form.save()
            messages.success(request, "Case updated successfully.")
            return redirect("case_list")
        else:
            # Form is invalid, re-render the partial template with errors
            logger.warning(f"Invalid edit form submission: {form.errors}")
            context = {"form": form, "case": case}
            # We return a 400 status to indicate a bad request, which can be
            # handled in JS, but for now just re-rendering is fine.
            return render(request, "discipline/edit_case.html", context)
    else:
        # GET request: show the form pre-filled
        form = CaseProfileForm(instance=case)

    context = {
        "form": form,
        "case": case,
    }
    return render(request, "discipline/edit_case.html", context)

@login_required
def get_student(request, studID):
    try:
        studID = int(studID)  # convert to integer
        student = studentInfo.objects.get(studID=studID)
        return JsonResponse({
            'found': True,
            'name': f"{student.firstname} {student.lastname}",
            'course': student.degree,
            'year': student.yearlvl,
        })
    except ValueError:
        # studID was not a valid integer
        return JsonResponse({'found': False, 'error': 'Invalid student ID'})
    except studentInfo.DoesNotExist:
        return JsonResponse({'found': False})
    except Exception as e:
        print(f"Error fetching student {studID}: {e}")
        return JsonResponse({'found': False, 'error': str(e)})
@login_required
def community_service_list(request):
    services = CommunityService.objects.all().order_by('-service_date')
    total_hours = sum(service.hours_rendered for service in services)
    return render(request, 'community_service/list.html', {
        'services': services,
        'total_hours': total_hours
    })

@login_required
def add_community_service(request):
    if request.method == 'POST':
        form = CommunityServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('community_service_list')
    else:
        form = CommunityServiceForm()
    return render(request, 'community_service/add.html', {'form': form})
# ---
# VIEW 4: For the Delete Button (AJAX)
# ---
# This view handles the POST request from the SweetAlert pop-up
# It replaces your original delete_case view
@require_POST # Ensures this view only accepts POST requests
@login_required
def case_delete(request, case_id):
    try:
        case = get_object_or_404(CaseProfile, id=case_id)
        case.delete()
        # Return a success JSON response, which the JavaScript expects
        return JsonResponse({"status": "success", "message": "Case deleted successfully."})
    except Exception as e:
        logger.error(f"Error deleting case {case_id}: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ---
# ALL OTHER VIEWS (Copied from your file)
# ---

# This is your AJAX view for the student datalist
# Renamed from get_student to avoid confusion, but it's your code
@login_required
def get_student_details(request, studID):
    try:
        studID = int(studID)  # convert to integer
        student = studentInfo.objects.get(studID=studID)
        return JsonResponse({
            'found': True,
            'name': f"{student.firstname} {student.lastname}",
            'course': student.degree,
            'year': student.yearlvl,
        })
    except ValueError:
        return JsonResponse({'found': False, 'error': 'Invalid student ID'})
    except studentInfo.DoesNotExist:
        return JsonResponse({'found': False})
    except Exception as e:
        print(f"Error fetching student {studID}: {e}")
        return JsonResponse({'found': False, 'error': str(e)})

# Your original update_suspension view
@csrf_exempt
@login_required
def update_suspension(request, case_id):
    if request.method == "POST":
        data = json.loads(request.body)
        # Note: Your JS sends 'type' and 'value'
        suspension_type = data.get("type") 
        value = data.get("value")

        try:
            case = CaseProfile.objects.get(id=case_id)
            # Your original code used this f-string, but the JS
            # from case_list.html sends a combined string.
            # I'll use the one from the JS:
            duration = data.get('suspension_duration')
            if duration:
                 case.suspension_duration = duration
            else:
                 # Fallback to your original logic if 'suspension_duration' isn't sent
                 case.suspension_duration = f"{value} {suspension_type}"
            
            case.save()
            return JsonResponse({"success": True})
        except CaseProfile.DoesNotExist:
            return JsonResponse({"success": False, "error": "Case not found"})
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

@login_required
def counseling_form_view(request, case_id):
    case = get_object_or_404(CaseProfile, id=case_id)
    student = case.student 

    if request.method == "POST":
        form = CounselingSchedulerForm(request.POST)
        if form.is_valid():
            current_datetime = timezone.now()
            ongoing_schedule = counseling_schedule.objects.filter(
                studentID=student,
                scheduled_date__gte=current_datetime.date()
            ).exclude(status__in=["Declined", "Expired"]).first()

            if ongoing_schedule:
                time = {
                    '8-9': '8:00 AM - 9:00 AM',
                    '9-10': '9:00 AM - 10:00 AM',
                    '10-11': '10:00 AM - 11:00 AM',
                    '11-12': '11:00 AM - 12:00 PM',
                    '1-2': '1:00 PM - 2:00 PM',
                    '2-3': '2:00 PM - 3:00 PM',
                    '3-4': '3:00 PM - 4:00 PM',
                    '4-5': '4:00 PM - 5:00 PM'
                }
                scheduled_date = ongoing_schedule.scheduled_date.strftime('%B %d, %Y')
                scheduled_time = time.get(ongoing_schedule.scheduled_time, ongoing_schedule.scheduled_time)
                
                # [FIX 1] Add 'counseling_form' tag to the ERROR message
                messages.error(request, f"Student already has a counseling schedule on {scheduled_date} at {scheduled_time}.", extra_tags='counseling_form')
                
                # Redirect back to the form to show the error
                return redirect("counseling_form", case_id=case.id)

            counseling = form.save(commit=False)
            counseling.dateRecieved = current_datetime.strftime('%Y-%m-%d')
            counseling.studentID = student
            counseling.save()
            
            # [FIX 2] Add 'case_list' tag to the SUCCESS message
            messages.success(request, f"Counseling request for {student.firstname} {student.lastname} has been created.", extra_tags='case_list')
            
            # [FIX 3] Redirect to your case list view
            # !!! Change 'case_list_view' to your actual URL name for the case list !!!
            return redirect("case_list") 
            
    else:
        form = CounselingSchedulerForm()

    context = {
        "form": form,
        "student": student,
        "case": case
    }
    return render(request, "discipline/counseling_form.html", context)

# In 'discipline copy 2.py', replace your old student_hours_view with this:

@login_required
def student_hours_view(request, case_id):
    case = get_object_or_404(CaseProfile, pk=case_id)
    records = CommunityServiceTracker.objects.filter(case=case).order_by('-service_date')
    
    # --- NEW CALCULATION LOGIC ---
    
    # 1. Get TOTAL REQUIRED hours from the case
    #    (We use the community_service_hours field from the CaseProfile model)
    total_required_decimal = float(case.community_service_hours or 0.0)

    # 2. Calculate TOTAL RENDERED hours (from all tracker records)
    total_rendered_decimal = 0.0
    for r in records:
        rendered = r.total_hours_decimal()
        if rendered:
            total_rendered_decimal += rendered

    # 3. Calculate REMAINING hours and check completion
    remaining_decimal = max(0.0, total_required_decimal - total_rendered_decimal)
    is_completed = (total_rendered_decimal >= total_required_decimal) and (total_required_decimal > 0)
    
    # 4. Format all values as strings for the template
    #    (These variable names match your student_hours_rendered.html template)
    total_required_str = _format_decimal_hours(total_required_decimal)
    total_rendered_str = _format_decimal_hours(total_rendered_decimal)
    remaining_str = _format_decimal_hours(remaining_decimal)

    # --- END NEW LOGIC ---

    if request.method == 'POST':
        # This POST logic is from your discipline.py (forms file)
        # and discipline copy 2.py (views file)
        
        # Note: Your template just has fields 'date', 'time_in', 'time_out'.
        # Your form expects 'session'. This will cause a mismatch.
        # For now, I am using the form defined in your 'discipline.py' (forms) file.
        
        form = CommunityServiceForm(request.POST) 
        
        if form.is_valid():
            tracker = form.save(commit=False)
            tracker.case = case # Link to the current case
            
            # Check for duplicates (from your original code)
            exists = CommunityServiceTracker.objects.filter(
                case=case,
                service_date=tracker.service_date,
                session=tracker.session
            ).exists()
            
            if exists:
                messages.error(request, f"{tracker.session.capitalize()} session already exists for {tracker.service_date}.")
            else:
                tracker.save()
                messages.success(request, "Community service record added successfully!")
                # Redirect to refresh the page and see new totals
                return redirect('student_hours', case_id=case.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Show a blank form on GET request
        form = CommunityServiceForm()

    # This 'existing_sessions' logic was in your view, but your template doesn't use it.
    # I've left it in case you need it.
    existing_sessions = {}
    for r in records:
        date_str = r.service_date.isoformat()
        existing_sessions.setdefault(date_str, []).append(r.session)

    # This context dictionary now provides ALL variables your template needs
    context = {
        'case': case,
        'form': form,
        
        # FIX: Your template loops 'sessions', but your view used 'records'.
        # We now pass 'sessions' correctly.
        'sessions': records, 
        
        # Pass the new calculated values to the template
        'total_required_str': total_required_str,
        'total_rendered_str': total_rendered_str,
        'remaining_str': remaining_str,
        'is_completed': is_completed,
        
        'existing_sessions': existing_sessions,
    }
    return render(request, 'discipline/student_hours_rendered.html', context)