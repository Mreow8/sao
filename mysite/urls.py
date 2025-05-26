from django.contrib import admin
from django.urls import path, include
from mainpage.views import homepage
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    # path('', include('mainpage.urls')), 

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
