from django.urls import path
from mainpage.views import search_suggestions, company_suggestions
from mainpage import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.mainpage, name="home"), 
    path('admin/student-tracker/', views.admin_student_tracker, name='admin_student_tracker'),
    
    # URL for getting the PDF/image link (called by AJAX)
    path('get-ojt-pdf-url/<int:req_id>/<str:attr_name>/', 
         views.get_ojt_pdf_url, 
         name='get_ojt_pdf_url'),

    path('ojt/download-requirements/', views.ojt_requiremets_download, name='ojt_requiremets_download'),
    
    # STUDENT SUGGESTIONS
    path('student-suggestions/', views.student_suggestions, name='student_suggestions'),
    
    # Removed the first duplicate 'suggestions/' path
    
    # OJT HIRING
    path('ojthiring/admin', views.ojt_hiring, name="ojt_hiring"),
    path('ojthiring/admin/assign', views.ojt_assign_student, name='ojthiring_assign'),
    path('ojthiring/more/<str:id>', views.ojt_hiring_info, name='ojthiring_info'),
    path('ojthiring/clear', views.del_ojt, name="del_ojt"),
    path('ojthiring/delete/<int:id>', views.ojthiring_delete, name="ojt_hiring_delete"),

    # OJT REQUIREMENTS
    path('ojt/requirements/tracker/', views.ojtRequirements_tracker, name="ojt_requirements_tracker"),
    path('ojt/requirements/tracker/update', views.ojt_requirements_accept, name='ojt_requirement_update'),
    
    # FIXED: Renamed this to avoid conflict
    path('ojt_requirements/download', views.download_zipped_ojt_templates, name="ojt_templates_download"), 
    
    path('ojt/requirements/submit', views.ojt_requirements_submit, name='ojt_requirements_submit'),
     # KEEP THIS
path('ojt/requirements/stream_file/<int:req_id>/<str:attr_name>/', 
     views.stream_ojt_file, 
     name='stream_ojt_file'),
   path('ojt/requirements/tracker/view/iframe/<int:id>', 
         views.view_pdf, 
         name='view_pdf'),

    # CAREER GUIDANCE
    path('main/', views.seminar, name="seminar_page"),
    path('seminar/attendance/manager/<int:id>', views.manage_attendance, name='manage_att'),
    path('pending_student_att', views.pend_attendance, name='pending_attendance'),
    path('attendance/cancel/<str:id>', views.cancel_pending, name="cancel_pending"),
    path('attendance/attend_all/<str:id>/', views.attend_all_pending, name='attend_all_pending'),
    path('seminar/delete/<int:id>', views.seminar_delete, name='seminar_delete'),

    # SUGGESTIONS
    # This is the correct, single path for suggestions
    path('suggestions/', search_suggestions.as_view(), name='search_suggestions'), 
    path('suggestions/companies', company_suggestions.as_view(), name='company_suggestions'),

    # TRANSACTION REPORT
    path('report/', views.transRep, name="job_trans_rep"),
    path('report/print', views.transRep_print, name="rep_print"),

    # NON-ACADEMIC ISSUANCE
    path('non_acad', views.non_acad_page, name="non_acad"),
    
    path('upload/', views.file_scrapper, name='scrapper'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)