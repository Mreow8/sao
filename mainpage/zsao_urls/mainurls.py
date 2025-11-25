from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .. import views

urlpatterns = [
    path('captcha/', include('captcha.urls')),
    
    # Authentication
    path('login/', views.signinuser, name='signinuser'), 
    path('register/', views.signupuser, name='signupuser'),
    path('change-password/', views.change_password, name='password_change'),
    path('assign-role/', views.assign_role, name='assign_role'),
    path('verify-otp/<str:user_id>/', views.verify_otp, name='verify_otp_page'),
    
    # Included App URLs (The new files you created)
    # path('medical/', include('medical.urls')),
    # path('organizations/', include('organizations.urls')),
    # path('guidance/', include('guidance.urls')),
    
    # General / Other Dashboards
    path('studentlifedashboard/', views.admin_dashboard, name='studentlifedashboard'),
    path('dashboard/student-life/', views.student_life_dashboard, name='student_life_dashboard'),
    path('dashboard/scholarship/', views.scholarship_dashboard, name='scholarship_dashboard'),
    path('dashboard/placement/', views.placement_dashboard, name='placement_dashboard'),
    path('adminmain', views.adminhome, name="adminmain"),
    
    # Student Life / Equipment / GMC
    path('equipmenttracker', views.equipmentTracker, name="equipmentTracker"),
    path('requestgmc', views.requestedgmc, name="requestgmc"),
    path("save_equipment_borrowing/", views.save_equipment_borrowing, name="save_equipment_borrowing"),
    path("generate-gmc/<int:request_id>/", views.generateGmc, name="generateGmc"),
    path("monthlyCalendar", views.monthlyCalendar, name="monthlyCalendar"),
    path('admin/equipment/get-student-details/', views.get_student_details_ajax, name='get_student_details_ajax'),
    
    # Uploads & Files
    path("upload/", views.upload_files, name="upload_files"),
    # Note: 'upload_file' (singular) was moved to medical/urls.py to avoid conflict
    
    # Inventory / Excel Management
    path("display_items/", views.display_items, name="display_items"),
    path("purchased_items/", views.purchased_items, name="purchased_items"),
    path("lnd_file/", views.lnd_file, name="lnd_file"),
    path("display_storage_items/", views.display_storage_items, name="display_storage_items"),
    path("update_serial_no/<int:storage_id>/", views.update_serial_no, name="update_serial_no"),
    path("edit/", views.edit_excel_data, name="edit_excel_data"),
    path("update/<int:pk>/", views.update_excel_data, name="update_excel_data"),
    
    # Miscellaneous
    path("search/students/", views.search_students, name="search_students"),
    path('Gen_Home', views.Gen_Home, name="Gen_Home"),
    path('post', views.post , name='post'),
    # path('alumniIdRequests/', views.alumni_main, name='alumni_main'),
    path('history/transaction_report/', views.view_transaction_history, name='transaction_report_view'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)