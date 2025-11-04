# mainpage/views/discipline.py
# (Or wherever your discipline.py file is)

from datetime import datetime
import json
import logging

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

# ---
# VIEW 1: For case_profile.html (Create Form)
# ---
# This view combines the GET (show form) and POST (create case)
# from your original case_profile_view
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
@login_required
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
        form = CaseProfileForm(request.POST, request.FILES) # Added request.FILES
        if form.is_valid():
            student_id = request.POST.get('student')  # text input
            if not student_id:
                messages.error(request, "Student ID is required.")
            else:
                try:
                    student = studentInfo.objects.get(studID=student_id)
                    case = form.save(commit=False)
                    case.student = student
                    # Set reported_by from the form's initial value (which should be user.username)
                    case.reported_by = form.cleaned_data.get('reported_by', user.username)
                    case.save()
                    messages.success(request, "Case profile saved successfully.")
                    return redirect('case_list') # Redirect to the new list view
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

    sort_by = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')

    valid_sort_fields = {
        'student': 'student__firstname',
        'offense': 'offense_type',
        'date': 'date_reported',
        'status': 'status',
    }

    sort_field = valid_sort_fields.get(sort_by, 'date_reported')

    if order == 'desc':
        order_string = f'-{sort_field}'
    else:
        order_string = sort_field
        
    if user.is_authenticated and (user.is_staff or user.is_superuser or getattr(user, 'role', None) == 'guard'):
        all_cases = CaseProfile.objects.all().order_by(order_string)
        
    elif user.is_authenticated and getattr(user, 'role', None) == 'student':
        all_cases = CaseProfile.objects.filter(student__studID=user.username).order_by(order_string)
    else:
        all_cases = CaseProfile.objects.none()

    paginator = Paginator(all_cases, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj, 
        'base_template': base_template,
        'current_sort': sort_by,
        'current_order': order,
    }
    return render(request, 'discipline/case_list.html', context)
@login_required
def case_edit(request, case_id):
    case = get_object_or_404(CaseProfile, id=case_id)
    if request.method == "POST":
        form = CaseProfileForm(request.POST, request.FILES, instance=case)
        if form.is_valid():
            form.save()
            messages.success(request, "Case updated successfully.")
            return redirect("case_list") # Redirect to the list after saving
        else:
            # If form is invalid, re-render the modal form with errors
            context = {"form": form, "case": case}
            return render(request, "discipline/_case_edit_form.html", context)
    else:
        # GET request: show the form pre-filled with case data
        form = CaseProfileForm(instance=case)

    context = {
        "form": form,
        "case": case,
    }
    # Renders the *partial* template for the modal
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
# Your original student_hours_view
@login_required
def student_hours_view(request, case_id):
    case = get_object_or_404(CaseProfile, pk=case_id)
    records = CommunityServiceTracker.objects.filter(case=case).order_by('-service_date')
    if request.method == 'POST':
        form = CommunityServiceForm(request.POST, request.FILES)
        if form.is_valid():
            tracker = form.save(commit=False)
            tracker.case = case
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
                return redirect('student_hours', case_id=case.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CommunityServiceForm()

    existing_sessions = {}
    for r in records:
        date_str = r.service_date.isoformat()
        existing_sessions.setdefault(date_str, []).append(r.session)

    total_hours = sum([r.total_hours_decimal() for r in records])
    total_hours_display = f"{int(total_hours)}h {int((total_hours % 1) * 60)}m"

    context = {
        'case': case,
        'form': form,
        'records': records,
        'total_hours': total_hours_display,
        'rendered_hours': total_hours_display, # Fixed this from your code
        'existing_sessions': existing_sessions,
    }
    return render(request, 'discipline/student_hours_rendered.html', context)