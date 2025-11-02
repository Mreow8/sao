from django.urls import path
from mainpage.views import search_suggestions, company_suggestions
from mainpage import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # The main 'jobplacement/' is in your main urls.py
    path('', views.mainpage, name="home"), 
    path('admin/student-tracker/', views.admin_student_tracker, name='admin_student_tracker'),
  
    # path('admin/unassign-student/<int:assignment_id>/', views.unassign_student_view, name='unassign_student_view'),
    path('ojt/download-requirements/', views.ojt_requiremets_download, name='ojt_requiremets_download'),
    # OJT HIRING THINGS (removed 'jobplacement/' prefix)
    path('student-suggestions/', views.student_suggestions, name='student_suggestions'),
    path('suggestions/', views.search_suggestions.as_view(), name='suggestions'),
    path('ojthiring/admin', views.ojt_hiring, name="ojt_hiring"),
    path('ojthiring/admin/assign', views.ojt_assign_student, name='ojthiring_assign'),
    path('ojthiring/more/<str:id>', views.ojt_hiring_info, name='ojthiring_info'),
    path('ojt/requirements/tracker/', views.ojtRequirements_tracker, name="ojt_requirements_tracker"),
    path('ojt/requirements/tracker/update', views.ojt_requirements_accept, name='ojt_requirement_update'),
    path('ojthiring/clear', views.del_ojt, name="del_ojt"),
    path('ojt_requirements/download', views.download_zipped_ojt_templates, name="ojt_requiremets_download"),
    path('ojt/requirements/submit', views.ojt_requirements_submit, name='ojt_requirements_submit'),
    path('ojthiring/delete/<int:id>', views.ojthiring_delete, name="ojt_hiring_delete"),
    
    # Career Guidance THINGS (removed 'jobplacement/' prefix and fixed typo)
    path('main/', views.seminar, name="seminar_page"), # Fixed 'jobeplacement' typo
    path('seminar/attendance/manager/<int:id>', views.manage_attendance, name='manage_att'),
    path('pending_student_att', views.pend_attendance, name='pending_attendance'),
    path('attendance/cancel/<str:id>', views.cancel_pending, name="cancel_pending"),
   
    # This is the line you fixed, which was correct.
    path('attendance/attend_all/<str:id>/', views.attend_all_pending, name='attend_all_pending'),
    
    path('seminar/delete/<int:id>', views.seminar_delete, name='seminar_delete'),

    # Suggestions (This one was already correct)
    path('suggestions/', search_suggestions.as_view(), name='search_suggestions'),
    path('suggestions/companies', company_suggestions.as_view(), name='company_suggestions'),

    # Transaction Report (removed 'jobplacement/' prefix)
    path('report/', views.transRep, name="job_trans_rep"),
    path('report/print', views.transRep_print, name="rep_print"),

    # Non Academic Issuance (removed 'jobplacement/' prefix)
    path('non_acad', views.non_acad_page, name="non_acad"),
    
    # STUDENTS PATHS (removed 'jobplacement/' prefix)
    path('ojt/requirements/tracker/view/iframe/<int:id>', views.view_pdf, name='view_pdf'),
    path('upload/', views.file_scrapper, name='scrapper'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)