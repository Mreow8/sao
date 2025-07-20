from django.shortcuts import render, redirect
from ..models.discipline import CaseProfile
from ..forms.discipline import CaseProfileForm

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