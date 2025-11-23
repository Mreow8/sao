# organizations/urls.py
from django.urls import path
from .. import views

urlpatterns = [
    path('dashboard/', views.org_dashboard, name='org_dashboard'),
    path('orgmain/', views.orgmain, name='orgmain'),
    path('add-organization/', views.add_organization, name='add_organization'),
    
    # Org Specific
    path('org/<slug:slug>/', views.org_profile, name='org_profile'),
    path('organization/<slug:org_slug>/advisers/', views.view_adviser, name='view_adviser_list'),
    path('<slug:slug>_financial/', views.view_financial, name='view_financial_by_slug'),
    path('<slug:org_slug>/advisers/', views.view_adviser, name='view_adviser'),
    path('officer/<slug:slug>/', views.view_officers, name='view_officers'),
    path('projects/<slug:slug>/', views.view_project_by_slug, name='view_project_by_slug'),
    path('<slug:slug>_adviserdata/', views.register_adviser, name='register_adviser'),
    
    # Forms & Uploads
    path('officerform/<slug:slug>/', views.officer_form, name='officer_form'),
    path('organizations/<slug:slug>/accreditations/upload/', views.upload_accreditation, name='view_accreditation_by_slug'),
    path('org/<slug:org_slug>/upload-cbl/', views.upload_org_cbl, name='upload_org_cbl'),
    path('<slug:org_slug>/CBL/', views.view_org_cbl, name='view_org_cbl'),
    
    # Admin Management
    path('admin_manageofficer/', views.admin_manageofficer, name="admin_manageofficer"),
    path('admin_manageadviser/', views.admin_manageadviser, name='admin_manageadviser'),
    path('admin_managefinancial/', views.admin_managefinancial, name="admin_managefinancial"),
    path('admin_manageproject/', views.admin_manageproject, name="admin_manageproject"),
    path('admin_manage_accreditations/', views.admin_manage_accreditations, name='admin_manage_accreditations'),
    path('admin_view_accreditations/', views.admin_view_accreditations, name='admin_view_accreditations'),
    path('admin_transactionreport/', views.admin_transactionreport, name="transaction_report"),
    
    # CBLs
    path('ssg_CBL', views.SSG_CBL, name="SSG_CBL"),
    path('FSTLP_CBL', views.FSTLP_CBL, name="FSTLP_CBL"),
    path('technocrats_CBL', views.TECHNOCRATS_CBL, name="TECHNOCRATS_CBL"),
    path('si_CBL', views.SI_CBL, name="SI_CBL"),
    path('the-equationers_CBL', views.THEEQUATIONERS_CBL, name="THEEQUATIONERS_CBL"),
]