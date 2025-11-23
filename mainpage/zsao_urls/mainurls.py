from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .. import views
from ..views import org_profile, add_organization

urlpatterns = [
    path('captcha/', include('captcha.urls')),

           path('assign-role/', views.assign_role, name='assign_role'), 
           path('change-password/', views.change_password, name='password_change'),
  path("search/students/", views.search_students, name="search_students"),
path('dashboard/student-life/', views.student_life_dashboard, name='student_life_dashboard'),
    path('dashboard/scholarship/', views.scholarship_dashboard, name='scholarship_dashboard'),
    path('dashboard/guidance/', views.guidance_dashboard, name='guidance_dashboard'),
    path('dashboard/clinic/', views.clinic_dashboard, name='clinic_dashboard'),
    path('dashboard/placement/', views.placement_dashboard, name='placement_dashboard'),
# urls.py
path('dashboard/organization/', views.org_dashboard, name='org_dashboard'),
path('organization/<slug:org_slug>/advisers/', views.view_adviser, name='view_adviser_list'),
path('orgmain/', views.orgmain, name='orgmain'),

path('studentlifedashboard/', views.admin_dashboard, name='studentlifedashboard'),

  path("organizations/<slug:slug>/accreditations/upload/", views.upload_accreditation, name="view_accreditation_by_slug"),
    # ... your other direct paths ...
    # urls.py
path('officerform/<slug:slug>/', views.officer_form, name='officer_form'),
# path('officerforms/', views.officer_forms, name='officer_forms'),
   path('Gen_Home', views.Gen_Home, name="Gen_Home"),
    path('add-organization/', add_organization, name='add_organization'),
    path('org/<slug:slug>/', org_profile, name='org_profile'),
  path('<slug:slug>_financial/', views.view_financial, name='view_financial_by_slug'),
    path('<slug:org_slug>/advisers/', views.view_adviser, name='view_adviser'),

      path('officer/<slug:slug>/', views.view_officers, name='view_officers'),
        path('projects/<slug:slug>/', views.view_project_by_slug, name='view_project_by_slug'),
    path('register/', views.signupuser, name='signupuser'),
    path('<slug:slug>_adviserdata/', views.register_adviser, name='register_adviser'),

    path('login/', views.signinuser, name='signinuser'), 
    
 path('post', views.post , name='post'),
    # Community Service Tracker





path('history/transaction_report/', views.view_transaction_history, name='transaction_report_view'),



    path("equipmenttracker", views.equipmentTracker, name="equipmentTracker"),
    path("requestgmc", views.requestedgmc, name="requestgmc"),
    path("equipmenttracker/", views.equipmentTracker, name="equipmentTracker"),
   
    path(
        "save_equipment_borrowing/",
        views.save_equipment_borrowing,
        name="save_equipment_borrowing",
    ),
    path(
        "update_return_status/", views.update_return_status, name="update_return_status"
    ),

    
    path("adminmain", views.adminhome, name="adminmain"),
    # path("gmc-form", views.gmcform, name="gmcform"),
    path("generate-gmc/<int:request_id>/", views.generateGmc, name="generateGmc"),
    # path(
    #     "transactionreport",
    #     views.processed_gmc_transactions,
    #     name="processed_gmc_transactions",
    # ),
    path("monthlyCalendar", views.monthlyCalendar, name="monthlyCalendar"),
  
    path('admin/equipment/get-student-details/', views.get_student_details_ajax, name='get_student_details_ajax'),
    # path("addEquipment/", views.addEquipment, name="addEquipment"),
   path('verify-otp/<str:user_id>/', views.verify_otp, name='verify_otp_page'),
    path('org/<slug:org_slug>/upload-cbl/', views.upload_org_cbl, name='upload_org_cbl'),
    path('<slug:org_slug>/CBL/', views.view_org_cbl, name='view_org_cbl'),
    path("upload/", views.upload_files, name="upload_files"),
    path("display_items/", views.display_items, name="display_items"),
    # path("update_status/", UpdateStatusView.as_view(), name="update_status"),
    path("purchased_items/", views.purchased_items, name="purchased_items"),
    path("lnd_file/", views.lnd_file, name="lnd_file"),
    path(
        "display_storage_items/",
        views.display_storage_items,
        name="display_storage_items",
    ),
    path(
        "update_serial_no/<int:storage_id>/",
        views.update_serial_no,
        name="update_serial_no",
    ),
    path(
        "edit/", views.edit_excel_data, name="edit_excel_data"
    ),  # mao ne na lines napuno
    path(
        "update/<int:pk>/", views.update_excel_data, name="update_excel_data"
    ),



   # ADMIN
   path('admin_manageofficer/', views.admin_manageofficer, name="admin_manageofficer"),
   path('admin_manageadviser/', views.admin_manageadviser, name='admin_manageadviser'),
   path('admin_managefinancial/', views.admin_managefinancial, name="admin_managefinancial"),
   path('admin_manageproject/', views.admin_manageproject, name="admin_manageproject"),
   path('admin_manage_accreditations/', views.admin_manage_accreditations, name='admin_manage_accreditations'),
   path('admin_view_accreditations/', views.admin_view_accreditations, name='admin_view_accreditations'),
   path('admin_transactionreport/', views.admin_transactionreport, name="transaction_report"),


   path('ssg_CBL', views.SSG_CBL, name="SSG_CBL"),

 path('FSTLP_CBL', views.FSTLP_CBL, name="FSTLP_CBL"),
   path('technocrats_CBL', views.TECHNOCRATS_CBL, name="TECHNOCRATS_CBL"),
   path('si_CBL', views.SI_CBL, name="SI_CBL"),
   path('the-equationers_CBL', views.THEEQUATIONERS_CBL, name="THEEQUATIONERS_CBL"),

   # SI++

 

    # Individual Profile URLS
    path('individual_profile', views.individualProfile, name="Individual Profile"),
    path('search_student_info_for_individual_profile/', views.search_student_info_for_individual, name='search_student_info_for_individual_profile'),

    # Intake Interview URLS
    path('intake_interview/', views.intake_interview_view, name="Intake Interview"),
    path('search_student_info_for_intake/', views.search_student_info_for_intake, name='search_student_info_for_intake'),

    # Counseling App Views URLS
    path('counseling_app/', views.counseling_app, name="Counseling App With Scheduler"),
    path('counseling_app/admin/', views.counseling_app_admin_view, name="Counseling App With Scheduler Admin View"),

    # Counseling App Validator, Updator URLS
    path('check_date_time_validity/', views.check_date_time_validity, name='check_date_time_validity'),
    path('update_counseling_schedule/', views.update_counseling_schedule, name='update_counseling_schedule'),
    path('delete_counseling_schedule/', views.delete_counseling_schedule, name='delete_counseling_schedule'),

    # Exit Interview Views URLS
    
    path('exit_interview', views.exit_interview, name="Exit Interview"),
    path('print_exit_interview/<int:request_id>/', views.print_exit_interview, name="print_exit_interview"),
    path('exit_interview/admin/', views.exit_interview_admin_view, name="Exit Interview Admin View"),
    path('search_exit_interview_request/',views. search_exit_interview_request, name='search_exit_interview_request'),

    # Exit Interview Searcher, Validator, Updator URLS
    path('search_student_info/', views.search_student_info, name='search_student_info'),
    path('check_date_time_validity_for_exit/', views.check_date_time_validity_for_exit, name='check_date_time_validity_for_exit'),
    path('update_exit_interview_status/', views.update_exit_interview_status, name='update_exit_interview_status'),
    path('delete_exit_interview_status/', views.delete_exit_interview_status, name='delete_exit_interview_status'),
    path('get_exit_interview_request/', views.get_exit_interview_request, name="get_exit_interview_request"),

    # OJT Assessment Views URLS
    path('ojt_assessment', views.ojt_assessment, name="OJT Assessment"),
    path('ojt_assessment/admin/', views.ojt_assessment_admin_view, name="OJT Assessment Admin View"),
    
    # OJT Assessment Seacher, Validator, Updator URLS
    path('search_ojt_assessment_request/', views.search_ojt_assessment_request, name='search_ojt_assessment_request'),
    path('print/assessment/<int:request_id>/', 
         views.print_ojt_assessment, 
         name='print_ojt_assessment'),
    path('update_ojt_assessment/', views.update_ojt_assessment, name='update_ojt_assessment'),
    path('delete_ojt_assessment/', views.delete_ojt_assessment, name='delete_ojt_assessment'),
    path('get_ojt_assessment_data/', views.get_ojt_assessment_data, name="get_ojt_assessment_data"),

    path('upload/', views.upload_file, name='upload_file'),

    path('alumniIdRequests/', views.alumni_main, name='alumni_main'),    
    # path('login/', views.login_view, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)