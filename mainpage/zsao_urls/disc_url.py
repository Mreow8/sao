# mainpage/discipline_urls.py

from django.urls import path
from .. import views  # Assumes your views are in the app's views.py

urlpatterns = [
   path('update-status/<int:case_id>/', views.update_case_status, name='update_case_status'),
    path('dashboard/discipline/', views.discipline_dashboard, name='discipline_dashboard'),
  
    path('case-profile/', views.case_profile_create, name='case_profile'),
  
    path('cases/list/', views.case_list, name='case_list'),
    path('student-cases/<str:studID>/', views.student_case_view, name='student_case_view'),
    path('cases/edit/<int:case_id>/', views.case_edit, name='case_edit'),

 
    path('cases/delete/<int:case_id>/', views.case_delete, name='case_delete'),

    path('get-student/<str:studID>/', views.get_student, name='get_student'),
    
    # 6. AJAX for suspension update
    path('update-suspension/<int:case_id>/', views.update_suspension, name='update_suspension'),

    # 7. Counseling form page
    path('counseling/<int:case_id>/', views.counseling_form_view, name='counseling_form'),
    
    # 8. Student hours page
    path('student-hours/<int:case_id>/', views.student_hours_view, name='student_hours'),
    
    # 9. Community service list
    path('community-service/', views.community_service_list, name='community_service_list'),
    
    # 10. Add community service
    path('community-service/add/', views.add_community_service, name='add_community_service'), 
    
    # 11. Community service tracker
    path('community-service-tracker/<int:student_id>/', views.serviceTracker, name="community-service-tracker"),
]