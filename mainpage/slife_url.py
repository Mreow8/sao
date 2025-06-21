from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views 


# app_name = "studentLife_system"

urlpatterns = [

    path("requestgmc", views.requestedgmc, name="requestgmc"),
    path("equipmenttracker", views.equipmentTracker, name="equipmentTracker"),
    path(
        "equipmenttrackerAdmin/",
        views.equipmentTrackerAdmin,
        name="equipmentTrackerAdmin",
    ),
    path(
        "save_equipment_borrowing/",
        views.save_equipment_borrowing,
        name="save_equipment_borrowing",
    ),
    path(
        "update_return_status/", views.update_return_status, name="update_return_status"
    ),
    
    path("adminmain", views.adminhome, name="adminmain"),
    path("requested-gmc", views.adminRequestedGmc, name="adminRequestedGmc"),
    path("gmc-form", views.gmcform, name="gmcform"),
    path("generate-gmc/<int:request_id>/", views.generateGmc, name="generateGmc"),
    path(
        "transactionreport",
        views.processed_gmc_transactions,
        name="processed_gmc_transactions",
    ),
    path("monthlyCalendar", views.monthlyCalendar, name="monthlyCalendar"),
    path(
        "monthlyCalendarAdmin", views.monthlyCalendarAdmin, name="monthlyCalendarAdmin"
    ),
    path("save-schedule/", views.save_schedule, name="save_schedule"),
    path(
        "update-schedule/<int:schedule_id>/",
        views.update_schedule,
        name="update_schedule",
    ),
    path(
        "delete-schedule/<int:schedule_id>/",
        views.delete_schedule,
        name="delete_schedule",
    ),
    path("addEquipment/", views.addEquipment, name="addEquipment"),
    path("upload/", views.upload_file, name="upload_file"),
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
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
