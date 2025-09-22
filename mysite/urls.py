from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mainpage import views

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Homepage (root)
    path('admin/', admin.site.urls),

    # Use unique prefixes to avoid collisions
    path('scholarship/', include('mainpage.zsao_urls.schol_url')),
    path('slife/', include('mainpage.zsao_urls.slife_url')),
    path('jobplacement/', include('mainpage.zsao_urls.job_url')),
    path('alum/', include('mainpage.zsao_urls.alum_url')),
    path('main/', include('mainpage.zsao_urls.mainurls')),
    path('med/', include('mainpage.zsao_urls.med_urls')),
    path('community/', include('mainpage.zsao_urls.com_url')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
