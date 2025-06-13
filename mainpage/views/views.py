from django.shortcuts import render
def homepage(request):
    return render(request, 'main.html')
def alumni_main(request):
    return render(request, 'alumni/id_requests.html')
def calendar(request):
    return render(request, 'officeOfStudentL/calendarOfEvents.html')
def login_view(request):
    return render(request, 'login.html')