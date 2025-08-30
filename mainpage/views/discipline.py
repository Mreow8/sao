from django.shortcuts import render, redirect
from ..models.discipline import CaseProfile
from ..forms.discipline import CaseProfileForm
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from datetime import datetime
from ..models import studentInfo  # Add this import at the top

# Replace these with the correct import paths from your models
from mainpage.models import CommunityServiceTracker
from django.shortcuts import render, redirect
from ..forms import CommunityServiceForm
from ..models import CommunityServiceTracker
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from ..models import studentInfo, counseling_schedule, CaseProfile  # adjust model name
from ..forms import CounselingSchedulerForm  # adjust form name

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_suspension(request, case_id):
    if request.method == "POST":
        data = json.loads(request.body)
        suspension_type = data.get("type")
        value = data.get("value")

        try:
            case = CaseProfile.objects.get(id=case_id)
            case.suspension_duration = f"{value} {suspension_type}"
            case.save()
            return JsonResponse({"success": True})
        except CaseProfile.DoesNotExist:
            return JsonResponse({"success": False, "error": "Case not found"})

def counseling_form_view(request, case_id):
    # Get the case record first
    case = get_object_or_404(CaseProfile, id=case_id)

    # Then get the student from the case
    student = case.student  # assuming ForeignKey to studentInfo

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
                messages.error(request, f"Student already has a counseling schedule on {scheduled_date} at {scheduled_time}.")
                return redirect("counseling_form", case_id=case.id)

            counseling = form.save(commit=False)
            counseling.dateRecieved = current_datetime.strftime('%Y-%m-%d')
            counseling.studentID = student
            counseling.save()

            messages.success(request, f"Counseling request for {student.firstname} {student.lastname} has been created.")
            return redirect("counseling_form", case_id=case.id)
    else:
        form = CounselingSchedulerForm()

    context = {
        "form": form,
        "student": student,
        "case": case
    }
    return render(request, "discipline/counseling_form.html", context)

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
import logging

logger = logging.getLogger(__name__)
def student_hours_view(request, case_id):
    case = get_object_or_404(CaseProfile, pk=case_id)
    records = CommunityServiceTracker.objects.filter(case=case).order_by('-date')

    if request.method == 'POST':
        form = CommunityServiceForm(request.POST)
        if form.is_valid():
            tracker_date = form.cleaned_data['date']

            # Check if record for this date exists
            existing = CommunityServiceTracker.objects.filter(case=case, date=tracker_date).first()

            if existing:
                # Fill the next empty time slot
                if not existing.morning_in:
                    existing.morning_in = form.cleaned_data.get('time_in')
                elif not existing.morning_out:
                    existing.morning_out = form.cleaned_data.get('time_out')
                elif not existing.afternoon_in:
                    existing.afternoon_in = form.cleaned_data.get('time_in')
                elif not existing.afternoon_out:
                    existing.afternoon_out = form.cleaned_data.get('time_out')
                else:
                    messages.error(request, "All time slots for this date are already filled.")
                    return redirect('student_hours', case_id=case.id)
                
                existing.save()
                messages.success(request, "Time logged successfully.")
            else:
                tracker = form.save(commit=False)
                tracker.case = case
                tracker.save()
                messages.success(request, "New date record created.")
            
            return redirect('student_hours', case_id=case.id)
    else:
        form = CommunityServiceForm()

    return render(request, 'discipline/student_hours_rendered.html', {
        'form': form,
        'records': records,
        'case': case,
        'student': case.student,
    })


def case_profile_view(request):
    user = request.user
    students = studentInfo.objects.all()
    base_template = (
        "adminmain.html" 
        if user.is_staff or user.is_superuser or getattr(user, 'role', None) == 'guard'
        else "main.html"
    )

    # Determine case list based on user role
    if user.is_authenticated and (user.is_staff or user.is_superuser or getattr(user, 'role', None) == 'guard'):
        case_list = CaseProfile.objects.all()
    elif user.is_authenticated and getattr(user, 'role', None) == 'student':
        case_list = CaseProfile.objects.filter(student__studID=user.username)
    else:
        case_list = CaseProfile.objects.none()

    if request.method == 'POST':
        form = CaseProfileForm(request.POST)
        if form.is_valid():
            student_id = request.POST.get('student')  # text input
            if not student_id:
                messages.error(request, "Student ID is required.")
                return render(request, 'discipline/case_profile.html', {
                    'form': form,
                    'case_list': case_list,
                    'students': students,
                    'base_template': base_template,
                })
            
            try:
                student = studentInfo.objects.get(studID=student_id)
            except studentInfo.DoesNotExist:
                messages.error(request, f"Student with ID {student_id} not found.")
                return render(request, 'discipline/case_profile.html', {
                    'form': form,
                    'case_list': case_list,
                    'students': students,
                    'base_template': base_template,
                })
            except Exception as e:
                logger.error(f"Unexpected error fetching student {student_id}: {e}")
                messages.error(request, "An unexpected error occurred while fetching the student.")
                return render(request, 'discipline/case_profile.html', {
                    'form': form,
                    'case_list': case_list,
                    'students': students,
                    'base_template': base_template,
                })
            
            try:
                case = form.save(commit=False)
                case.student = student
                case.save()
                messages.success(request, "Case profile saved successfully.")
                return redirect('case_profile')
            except Exception as e:
                logger.error(f"Error saving case for student {student_id}: {e}")
                messages.error(request, "An error occurred while saving the case profile.")
        else:
            # Form is invalid, log errors
            logger.warning(f"Invalid form submission: {form.errors}")
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = CaseProfileForm()

    return render(request, 'discipline/case_profile.html', {
        'form': form,
        'case_list': case_list,
        'students': students,
        'base_template': base_template,
    })
from ..models import CommunityService
from ..forms import CommunityServiceForm

def community_service_list(request):
    services = CommunityService.objects.all().order_by('-date')
    total_hours = sum(service.hours_rendered for service in services)
    return render(request, 'community_service/list.html', {
        'services': services,
        'total_hours': total_hours
    })

def add_community_service(request):
    if request.method == 'POST':
        form = CommunityServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('community_service_list')
    else:
        form = CommunityServiceForm()
    return render(request, 'community_service/add.html', {'form': form})

def serviceTracker(request, student_id):
    student = get_object_or_404(studentInfo, studID=student_id)
    if student:
        community_services = CommunityServiceTracker.objects.filter(student=student)
        time_rendered = [service.time_rendered() for service in community_services]
        total_hours = 0
        total_minutes = 0
        
        for service in community_services:
            hours, minutes = service.total_time_rendered()
            total_hours += hours
            total_minutes += minutes
        
        # Adjust total hours if total minutes exceed 60
        total_hours += total_minutes // 60
        total_minutes %= 60
        
        if student.community_service_hours is not None:
            total_time_rendered_hours = total_hours
            if total_time_rendered_hours >= student.community_service_hours:
                student.sanction_completed = True
                student.save()
            else:
                student.sanction_completed = False
                student.save()

    if request.method == "POST" and student:
        date_str = request.POST.get('service_date')
        service_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_in = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        student_signature = request.POST.get('student_signature')
        remarks = request.POST.get('remarks')

        CommunityServiceTracker.objects.create(
            student = student,
            service_date = service_date,
            time_in = time_in,
            time_out = time_out,
            student_signature = student_signature,
            remarks = remarks
        )

        return redirect(reverse('community-service-tracker', args=[student_id]))
    
    context = {'student':student, 'community_services':community_services, 'time_rendered':time_rendered, 'total_hours': total_hours,
        'total_minutes': total_minutes}
    return render(request, 'discipline/comm_service.html', context)
from django.shortcuts import get_object_or_404

# def case_profile_view(request):
#     student = get_object_or_404(studentInfo, user=request.user)  # or however you're identifying the student
#     context = {
#         'student': student
#     }
#     return render(request, 'main.html', context)
