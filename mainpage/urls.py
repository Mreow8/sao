from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import views
from django.contrib import admin
from . import views



urlpatterns = [
  path('', views.home, name="home"),
    path('scholarship', include('mainpage.schol_url')),


   path('register_officer/', views.register_officer, name='register_officer'),
   path('officer_login/', views.officer_login, name="officer_login"),

   # ADMIN
   path('admin_manageofficer/', views.admin_manageofficer, name="admin_manageofficer"),
   path('admin_manageadviser/', views.admin_manageadviser, name='admin_manageadviser'),
   path('admin_managefinancial/', views.admin_managefinancial, name="admin_managefinancial"),
   path('admin_manageproject/', views.admin_manageproject, name="admin_manageproject"),
   path('admin_manage_accreditations/', views.admin_manage_accreditations, name='admin_manage_accreditations'),
   path('admin_view_accreditations/', views.admin_view_accreditations, name='admin_view_accreditations'),
   path('admin_transactionreport/', views.admin_transactionreport, name="transaction_report"),

   # Certification
   path('FSTLP_certification', views.FSTLP_certification, name="FSTLP_certification"),
   path('SI_certification', views.SI_certification, name="SI_certification"),
   path('THEEQUATIONERS_certification', views.THEEQUATIONERS_certification, name="THEEQUATIONERS_certification"),
   path('SSG_certification', views.SSG_certification, name="SSG_certification"),
   path('TECHNOCRATS_certification', views.TECHNOCRATS_certification, name="TECHNOCRATS_certification"),

   # FSTLP
   path('FSTLP_profile', views.FSTLP_profile, name="FSTLP_profile"),
   path('FSTLP_projects', views.FSTLP_projects, name="FSTLP_projects"),
   path('FSTLP_financial', views.FSTLP_financial, name="FSTLP_financial"),
   path('FSTLP_CBL', views.FSTLP_CBL, name="FSTLP_CBL"),
   path('FSTLP_officerdata', views.FSTLP_officerdata, name="FSTLP_officerdata"),
   path('FSTLP_adviserdata', views.FSTLP_adviserdata, name='FSTLP_adviserdata'),
   path('FSTLP_viewproject', views.FSTLP_viewproject, name="FSTLP_viewproject"),
   path('FSTLP_viewfinancial', views.FSTLP_viewfinancial, name="FSTLP_viewfinancial"),
   path('FSTLP_viewofficer', views.FSTLP_viewofficer, name="FSTLP_viewofficer"),
   path('FSTLP_viewadviser', views.FSTLP_viewadviser, name="FSTLP_viewadviser"),
   path('FSTLP_accreditation', views.FSTLP_accreditation, name="FSTLP_accreditation"),

   # SI++
   path('SI_profile', views.SI_profile, name="SI_profile"),
   path('SI_projects', views.SI_projects, name="SI_projects"),
   path('SI_financial', views.SI_financial, name="SI_financial"),
   path('SI_CBL', views.SI_CBL, name="SI_CBL"),
   path('SI_officerdata', views.SI_officerdata, name="SI_officerdata"),
   path('SI_adviserdata', views.SI_adviserdata, name='SI_adviserdata'),
   path('SI_viewproject', views.SI_viewproject, name="SI_viewproject"),
   path('SI_viewfinancial', views.SI_viewfinancial, name="SI_viewfinancial"),
   path('SI_viewadviser', views.SI_viewadviser, name="SI_viewadviser"),
   path('SI_viewofficer', views.SI_viewofficer, name="SI_viewofficer"),
   path('SI_accreditation', views.SI_accreditation, name="SI_accreditation"),

   # THE EQUATIONERS
   path('THEEQUATIONERS_profile', views.THEEQUATIONERS_profile, name="THEEQUATIONERS_profile"),
   path('THEEQUATIONERS_projects', views.THEEQUATIONERS_projects, name="THEEQUATIONERS_projects"),
   path('THEEQUATIONERS_financial', views.THEEQUATIONERS_financial, name="THEEQUATIONERS_financial"),
   path('THEEQUATIONERS_accreditation', views.THEEQUATIONERS_accreditation, name="THEEQUATIONERS_accreditation"),
   path('THEEQUATIONERS_CBL', views.THEEQUATIONERS_CBL, name="THEEQUATIONERS_CBL"),
   path('THEEQUATIONERS_officerdata', views.THEEQUATIONERS_officerdata, name="THEEQUATIONERS_officerdata"),
   path('THEEQUATIONERS_adviserdata', views.THEEQUATIONERS_adviserdata, name='THEEQUATIONERS_adviserdata'),
   path('THEEQUATIONERS_viewproject', views.THEEQUATIONERS_viewproject, name="THEEQUATIONERS_viewproject"),
   path('THEEQUATIONERS_viewfinancial', views.THEEQUATIONERS_viewfinancial, name="THEEQUATIONERS_viewfinancial"),
   path('THEEQUATIONERS_viewadviser', views.THEEQUATIONERS_viewadviser, name="THEEQUATIONERS_viewadviser"),
   path('THEEQUATIONERS_viewofficer', views.THEEQUATIONERS_viewofficer, name="THEEQUATIONERS_viewofficer"),

   # SSG
   path('SSG_profile', views.SSG_profile, name="SSG_profile"),
   path('SSG_projects', views.SSG_projects, name="SSG_projects"),
   path('SSG_financial', views.SSG_financial, name="SSG_financial"),
   path('SSG_accreditation', views.SSG_accreditation, name="SSG_accreditation"),
   path('SSG_CBL', views.SSG_CBL, name="SSG_CBL"),
   path('SSG_officerdata', views.SSG_officerdata, name="SSG_officerdata"),
   path('SSG_adviserdata', views.SSG_adviserdata, name='SSG_adviserdata'),
   path('SSG_viewproject', views.SSG_viewproject, name="SSG_viewproject"),
   path('SSG_viewfinancial', views.SSG_viewfinancial, name="SSG_viewfinancial"),
   path('SSG_viewadviser', views.SSG_viewadviser, name="SSG_viewadviser"),
   path('SSG_viewofficer', views.SSG_viewofficer, name="SSG_viewofficer"),

   # TECHNOCRATS
   path('TECHNOCRATS_profile', views.TECHNOCRATS_profile, name="TECHNOCRATS_profile"),
   path('TECHNOCRATS_projects', views.TECHNOCRATS_projects, name="TECHNOCRATS_projects"),
   path('TECHNOCRATS_financial', views.TECHNOCRATS_financial, name="TECHNOCRATS_financial"),
   path('TECHNOCRATS_accreditation', views.TECHNOCRATS_accreditation, name="TECHNOCRATS_accreditation"),
   path('TECHNOCRATS_CBL', views.TECHNOCRATS_CBL, name="TECHNOCRATS_CBL"),
   path('TECHNOCRATS_officerdata', views.TECHNOCRATS_officerdata, name="TECHNOCRATS_officerdata"),
   path('TECHNOCRATS_adviserdata', views.TECHNOCRATS_adviserdata, name='TECHNOCRATS_adviserdata'),
   path('TECHNOCRATS_viewproject', views.TECHNOCRATS_viewproject, name="TECHNOCRATS_viewproject"),
   path('TECHNOCRATS_viewfinancial', views.TECHNOCRATS_viewfinancial, name="TECHNOCRATS_viewfinancial"),
   path('TECHNOCRATS_viewadviser', views.TECHNOCRATS_viewadviser, name="TECHNOCRATS_viewadviser"),
   path('TECHNOCRATS_viewofficer', views.TECHNOCRATS_viewofficer, name="TECHNOCRATS_viewofficer"),

   # General View
   path('Gen_Home', views.Gen_Home, name="Gen_Home"),

   

   path('Gen_FSTLP_profile', views.Gen_FSTLP_profile, name="Gen_FSTLP_profile"),
   path('Gen_SI_profile', views.Gen_SI_profile, name="Gen_SI_profile"),
   path('Gen_THEEQUATIONERS_profile', views.Gen_THEEQUATIONERS_profile, name="Gen_THEEQUATIONERS_profile"),
   path('Gen_SSG_profile', views.Gen_SSG_profile, name="Gen_SSG_profile"),
   path('Gen_TECHNOCRATS_profile', views.Gen_TECHNOCRATS_profile, name="Gen_TECHNOCRATS_profile"),
   

   path('Gen_FSTLP_viewofficer', views.Gen_FSTLP_viewofficer, name="Gen_FSTLP_viewofficer"),
   path('Gen_FSTLP_viewfinancial', views.Gen_FSTLP_viewfinancial, name="Gen_FSTLP_viewfinancial"),
   path('Gen_FSTLP_viewadviser', views.Gen_FSTLP_viewadviser, name="Gen_FSTLP_viewadviser"),
   path('Gen_FSTLP_viewproject', views.Gen_FSTLP_viewproject, name="Gen_FSTLP_viewproject"),

   
   path('Gen_SI_viewproject', views.Gen_SI_viewproject, name="Gen_SI_viewproject"),
   path('Gen_SI_viewfinancial', views.Gen_SI_viewfinancial, name="Gen_SI_viewfinancial"),
   path('Gen_SI_viewadviser', views.Gen_SI_viewadviser, name="Gen_SI_viewadviser"),
   path('Gen_SI_viewofficer', views.Gen_SI_viewofficer, name="Gen_SI_viewofficer"),

   path('Gen_THEEQUATIONERS_viewproject', views.Gen_THEEQUATIONERS_viewproject, name="Gen_THEEQUATIONERS_viewproject"),
   path('Gen_THEEQUATIONERS_viewfinancial', views.Gen_THEEQUATIONERS_viewfinancial, name="Gen_THEEQUATIONERS_viewfinancial"),
   path('Gen_THEEQUATIONERS_viewadviser', views.Gen_THEEQUATIONERS_viewadviser, name="Gen_THEEQUATIONERS_viewadviser"),
   path('Gen_THEEQUATIONERS_viewofficer', views.Gen_THEEQUATIONERS_viewofficer, name="Gen_THEEQUATIONERS_viewofficer"),

   path('Gen_SSG_viewproject', views.Gen_SSG_viewproject, name="Gen_SSG_viewproject"),
   path('Gen_SSG_viewfinancial', views.Gen_SSG_viewfinancial, name="Gen_SSG_viewfinancial"),
   path('Gen_SSG_viewadviser', views.Gen_SSG_viewadviser, name="Gen_SSG_viewadviser"),
   path('Gen_SSG_viewofficer', views.Gen_SSG_viewofficer, name="Gen_SSG_viewofficer"),
 
   path('Gen_TECHNOCRATS_viewproject', views.Gen_TECHNOCRATS_viewproject, name="Gen_TECHNOCRATS_viewproject"),
   path('Gen_TECHNOCRATS_viewfinancial', views.Gen_TECHNOCRATS_viewfinancial, name="Gen_TECHNOCRATS_viewfinancial"),
   path('Gen_TECHNOCRATS_viewadviser', views.Gen_TECHNOCRATS_viewadviser, name="Gen_TECHNOCRATS_viewadviser"),
   path('Gen_TECHNOCRATS_viewofficer', views.Gen_TECHNOCRATS_viewofficer, name="Gen_TECHNOCRATS_viewofficer"),

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
    path('update_ojt_assessment/', views.update_ojt_assessment, name='update_ojt_assessment'),
    path('delete_ojt_assessment/', views.delete_ojt_assessment, name='delete_ojt_assessment'),
    path('get_ojt_assessment_data/', views.get_ojt_assessment_data, name="get_ojt_assessment_data"),

    path('upload/', views.upload_file, name='upload_file'),

    path('', views.homepage, name='homepage'),
    path('alumniIdRequests/', views.alumni_main, name='alumni_main'),    
    path('calendarOfAct/', views.calendar, name='calendar'),
    path('login/', views.login_view, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)