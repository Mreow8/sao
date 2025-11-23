from django.urls import path
from .. import views

urlpatterns = [
    path('dashboard/', views.guidance_dashboard, name='guidance_dashboard'),
    
    # Individual Profile
    path('individual_profile', views.individualProfile, name="Individual Profile"),
    path('search_student_info_for_individual_profile/', views.search_student_info_for_individual, name='search_student_info_for_individual_profile'),

    # Intake Interview
    path('intake_interview/', views.intake_interview_view, name="Intake Interview"),
    path('search_student_info_for_intake/', views.search_student_info_for_intake, name='search_student_info_for_intake'),

    # Counseling App
    path('counseling_app/', views.counseling_app, name="Counseling App With Scheduler"),
    path('counseling_app/admin/', views.counseling_app_admin_view, name="Counseling App With Scheduler Admin View"),
    path('check_date_time_validity/', views.check_date_time_validity, name='check_date_time_validity'),
    path('update_counseling_schedule/', views.update_counseling_schedule, name='update_counseling_schedule'),
    path('delete_counseling_schedule/', views.delete_counseling_schedule, name='delete_counseling_schedule'),

    # Exit Interview
    path('exit_interview', views.exit_interview, name="Exit Interview"),
    path('print_exit_interview/<int:request_id>/', views.print_exit_interview, name="print_exit_interview"),
    path('exit_interview/admin/', views.exit_interview_admin_view, name="Exit Interview Admin View"),
    path('search_exit_interview_request/', views.search_exit_interview_request, name='search_exit_interview_request'),
    path('search_student_info/', views.search_student_info, name='search_student_info'),
    path('check_date_time_validity_for_exit/', views.check_date_time_validity_for_exit, name='check_date_time_validity_for_exit'),
    path('update_exit_interview_status/', views.update_exit_interview_status, name='update_exit_interview_status'),
    path('delete_exit_interview_status/', views.delete_exit_interview_status, name='delete_exit_interview_status'),
    path('get_exit_interview_request/', views.get_exit_interview_request, name="get_exit_interview_request"),

    # OJT Assessment
    path('ojt_assessment', views.ojt_assessment, name="OJT Assessment"),
    path('ojt_assessment/admin/', views.ojt_assessment_admin_view, name="OJT Assessment Admin View"),
    path('search_ojt_assessment_request/', views.search_ojt_assessment_request, name='search_ojt_assessment_request'),
    path('print/assessment/<int:request_id>/', views.print_ojt_assessment, name='print_ojt_assessment'),
    path('update_ojt_assessment/', views.update_ojt_assessment, name='update_ojt_assessment'),
    path('delete_ojt_assessment/', views.delete_ojt_assessment, name='delete_ojt_assessment'),
    path('get_ojt_assessment_data/', views.get_ojt_assessment_data, name="get_ojt_assessment_data"),
]