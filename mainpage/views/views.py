from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='signinuser')  # or the URL name of your login page

def homepage(request):
    if request.user.is_superuser:
        return render(request, 'adminmain.html')
    else:
        return render(request, 'main.html')
def alumni_main(request):
    return render(request, 'alumni/id_requests.html')
def calendar(request):
    return render(request, 'officeOfStudentL/calendarOfEvents.html')
def login_view(request):
    return render(request, 'login.html')
def post(request):
    return render(request, 'scrapper.html')# mainpage/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from ..models import CustomUser
from ..forms import RoleAssignForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from ..models.studentorg import Organization

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def assign_role(request):
    users = User.objects.all()
    organizations = Organization.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        org_id = request.POST.get('organization_id') or None

        try:
            user = User.objects.get(id=user_id)
            user.role = role
            user.organization_id = org_id if org_id else None
            user.save()
            messages.success(request, f"{user.username}'s role updated to {role}.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

        return redirect('assign_role')

    return render(request, 'assign_role.html', {
        'users': users,
        'organizations': organizations
    })
