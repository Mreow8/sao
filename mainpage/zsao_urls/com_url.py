from django.urls import path
from mainpage import views


urlpatterns = [
    path("programs/", views.programs, name="programs"),
    path("add_program/", views.add_programs, name="add_program"),
      path("crowdfunding/", views.crowdfunding_list, name="crowdfunding_list"),
    path("crowdfunding/<int:pk>/", views.crowdfunding_detail, name="crowdfunding_detail"),
        path("add-event/", views.add_event, name="add_event"),

    path("donates/<int:pk>/", views.donate, name="donates"),  path("crowdfunding/<int:pk>/edit/", views.edit_project, name="edit_project"),
    path("crowdfunding/<int:pk>/delete/", views.delete_project, name="delete_project"),
      path("donate", views.donate_view, name="donate"), 

path("projects/gcash-mode", views.gcash_mode, name="gcash-mode"),
  path("projects/bank-mode", views.bank_mode, name="bank-mode"),
  path("projects/volunteer-mode", views.volunteer_mode, name="volunteer-mode"),
    path("reports/", views.reports, name="reports"),
    path("reports-all/", views.reports_all, name="reports-all"),
    path("reports-find/", views.reports_find, name="reports-find"),
    path("dashboard/", views.dashboard, name="dashboard"),
   path("donation-dashboard/", views.donation_dashboard, name="donation_dashboard"),
  path("gcash-dashboard/", views.gcash_dashboard, name="gcash_dashboard"),
  path("banks-dashboard/", views.banks_dashboard, name="banks_dashboard"),
   path("volunteer-dashboard/", views.volunteer_dashboard, name="volunteer_dashboard"),
  path("donation-validate/", views.donation_validate, name="donation-validate"),
   path("donation_accept/<int:id>/", views.donation_accept, name="donation_accept"),
   path("donation_decline/<int:id>/", views.donation_decline, name="donation_decline"),
path("gcash_mode_admin/<int:id>/", views.gcash_mode_admin, name="gcash_mode_admin"),
 path("bank_mode_admin/<int:id>/", views.bank_mode_admin, name="bank_mode_admin"),
    path("donation_filter/", views.donation_filter, name="donation_filter"),
]
