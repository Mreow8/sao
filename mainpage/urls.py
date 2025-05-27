from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('alumniIdRequests/', views.alumni_main, name='alumni_main'),    
    path('calendarOfAct/', views.calendar, name='calendar'),
    path('login/', views.login, name='login'),

]

# Append media URL handling (only in development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
