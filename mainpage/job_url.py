from django.urls import path
from .views import search_suggestions, company_suggestions
from . import views
from django.conf import settings
from django.conf.urls.static import static
# from .views import index as cu_semundex
app_name='jobplacement'

urlpatterns = [
    path('jobplacement/', views.mainpage, name="home"),
    # OJT HIRING THINGS
    path('jobplacement/ojthiring/admin', views.ojt_hiring, name="ojt_hiring"),
    path('jobplacement/ojthiring/admin/assign', views.ojt_assign_student, name='ojthiring_assign'),
    path('jobplacement/ojthiring/more/<str:id>', views.ojt_hiring_info, name='ojthiring_info'),
    path('jobplacement/ojt/requirements/tracker/', views.ojtRequirements_tracker, name="ojt_requirements_tracker"),
    path('jobplacement/ojt/requirements/tracker/update', views.ojt_requirements_accept, name='ojt_requirement_update'),
    path('jobplacement/ojthiring/clear', views.del_ojt, name="del_ojt"),
    path('jobplacement/ojt_requirements/download', views.download_zipped_ojt_templates, name="ojt_requiremets_download"),
    path('jobplacement/ojt/requirements/submit', views.ojt_requirements_submit, name='ojt_requirements_submit'),
    path('jobplacement/ojthiring/delete/<int:id>', views.ojthiring_delete, name="ojt_hiring_delete"),
   
    #   Career Guidance THINGS
    path('jobeplacement/main/', views.seminar, name="seminar_page"),
    # path('jobplacement/new_seminar/', views.newSeminar, name="new_seminar"), # create new seminar
    path('jobplacement/seminar/attendance/manager/<int:id>', views.manage_attendance, name='manage_att'), # manage students with attendance
    path('jobplacement/pending_student_att', views.pend_attendance, name='pending_attendance'), # set attendance to pending
    path('jobplacement/attendance/cancel/<str:id>', views.cancel_pending, name="cancel_pending"), # cancel pending
    path('jobplacement/seminar/attendance/manager/jobplacement/attendance/attend_all/<str:id>', views.attend_all_pending),
    path('jobplacement/attendance/attend_all/<str:id>', views.attend_all_pending, name='attend_all_pending'),
    path('jobplacement/seminar/delete/<int:id>', views.seminar_delete, name='seminar_delete'),

    # Suggestions
    path('suggestions/', search_suggestions.as_view(), name='search_suggestions'),
    path('suggestions/companies', company_suggestions.as_view(), name='company_suggestions'),

    # Transaction Report
    path('jobplacement/report/', views.transRep, name="job_trans_rep"), # report page
    # path('jobplacement/report/creation', views.transaction_creation, name="new_transaction"),
    path('jobplacement/report/print', views.transRep_print, name="rep_print"), # print report

    # Non Academic Issuance
    path('jobplacement/non_acad', views.non_acad_page, name="non_acad"),
    
    # DELETABLE PATHS
    # path('jobplacement/login/', cu_index, name="student_login"),
    # path('jobplacement/signup/', views.student_signup_view, name="student_signup"),
    path('jobplacement/login/admin/', views.admin_login, name="admin_login"),
    path('jobplacement/signup/admin', views.admin_signup_view, name="admin_signup"),
    path('jobplacement/logout', views.logout_user, name="logout_user"),

    # ---------------------- STUDENTS PATHS ----------------------------------
    # homescreen sa login og admin    
    path('jobplacement/homepage/admin_student', views.admin_student, name='admin_student'),

    path('jobplacement/ojt/requirements/tracker/view/iframe/<int:id>', views.view_pdf, name='view_pdf'),
    path('jobplacement/upload/', views.file_scrapper, name='scrapper'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)