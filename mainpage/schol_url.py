from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('ee', views.adminhome, name='adminhome'),
    path('studentgome/', views.studenthome, name='studenthome'),
    path('logout/', views.logoutuser, name = 'logout'),
    path('studentreqsubmission/', views.studentreqsubmission, name='student_req'),
    path('adminreqsubmission/', views.adminreqsubmission, name='admin_req'),
    path('scholars_admin/', views.scholars_profile_admin, name='profile'),
    path('scholars_student/', views.scholars_profile_student, name='profile_student'),
    path('grade_submission/', views.grade_submission, name='grade'),
    path('mentorship/', views.mentorship, name='mentor'),
    path('transactionreports/', views.transactionreports, name='transaction'),
    path('register/', views.signupuser, name='signupuser'),
    path('chedreports/', views.chedreports, name='ched'),
    # path('login/', views.signinuser, name='signinuser'),
    path('search_student/', views.search_student, name='search_student'),
    path('process_grade_image/', views.process_grade_image, name='process_grade_image'),
    path('save_requirements/', views.save_requirements, name='save_requirements'),
    path('add_scholar/', views.add_scholar, name='add_scholar'),
    path('studentapplicationform/', views.studentapplicationform, name='studentapplication'),
    path('adminapplicationform/', views.adminapplication, name='adminapplication'),
    path('admingrant/', views.admingrant, name='admingrant'),
    path('scholarupdate/', views.scholarupdate, name='scholarupdate'),

# --------------------------------- dayag code ---------------------------------

    path('chedreports/Merit_Scholarship', views.chedreports_merit, name='ched_merit'),
    path('chedreports/TES_Scholarship', views.chedreports_TES, name='ched_TES'),
    path('chedreports/TDP_Scholarship', views.chedreports_TDP, name='ched_TDP'),
    path('chedreports/Coscho_Scholarship', views.chedreports_Coscho, name='ched_Coscho'),


    path('adminliquidation/', views.adminliquidation, name='liquidation'),
    path('adminliquidation/TDP_Liquidation', views.adminliquidation_TDP, name='liquidation_TDP'),
    path('adminliquidation/CoScho_Liquidation', views.adminliquidation_CoScho, name='liquidation_CoScho'),
    path('adminliquidation/TES_Liquidation', views.adminliquidation_TES, name='liquidation_TES'),


    path('Transaction_Report/Scholarship_Program', views.scholarship_program, name='ScholarshipProgram'),
    path('Transaction_Report/Scholarship_Billing_Report', views.scholarship_billing_report, name='ScholarshipBillingReport'),
   
   
    path('Transaction_Report/FUR/Admin_Cost_Liquidation', views.Admin_cost_liquidation, name='AdminCostLiquidation'),
    path('Transaction_Report/FUR/Admin_Cost_Liquidation/Coscho', views.coscho_liquidation, name='transliquidation_coscho'),
    path('Transaction_Report/FUR/Admin_Cost_Liquidation/TDP', views.tdp_liquidation, name='transliquidation_tdp'),
    path('Transaction_Report/FUR/Admin_Cost_Liquidation/TES', views.tes_liquidation, name='transliquidation_tes'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
