from django.shortcuts import render
def homepage(request):
    return render(request, 'aside.html')