from django.urls import path
from mainpage.views import search_suggestions, company_suggestions
from mainpage import views
from ..import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
        path('logout/', views.logoutuser, name = 'logout'),
        path('discipline/guard/', views.guard_homepage, name='guard_homepage'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)