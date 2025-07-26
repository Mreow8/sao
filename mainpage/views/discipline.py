from django.shortcuts import render, redirect
from ..models.discipline import CaseProfile
from ..forms.discipline import CaseProfileForm
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from datetime import datetime
from ..models import studentInfo  # Add this import at the top

# Replace these with the correct import paths from your models
from mainpage.models import CommunityServiceTracker
def case_profile_view(request):
    if request.method == 'POST':
        form = CaseProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('case_profile')
    else:
        form = CaseProfileForm()

    case_list = CaseProfile.objects.all()
    return render(request, 'discipline/case_profile.html', {
        'form': form,
        'case_list': case_list
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

        return redirect(reverse('studentLife_discipline:community-service-tracker', args=[student_id]))
    
    context = {'student':student, 'community_services':community_services, 'time_rendered':time_rendered, 'total_hours': total_hours,
        'total_minutes': total_minutes}
    return render(request, 'discipline/comm_service.html', context)
from django.shortcuts import get_object_or_404

def case_profile_view(request):
    student = get_object_or_404(studentInfo, user=request.user)  # or however you're identifying the student
    context = {
        'student': student
    }
    return render(request, 'main.html', context)
