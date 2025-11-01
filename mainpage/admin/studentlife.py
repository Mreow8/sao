from django.contrib import admin
from ..models import RequestedGMC, PPMPDocument, Schedule, Equipment, ProcurementItem, Storage, ExcelData, BorrowingRecord

@admin.register(RequestedGMC)
class RequestedGMCAdmin(admin.ModelAdmin):
    list_display = ('student', 'reason', 'or_num', 'request_date', 'processed')
    list_filter = ('processed', 'request_date')
    search_fields = ('student__studentName', 'reason', 'or_num')

@admin.register(PPMPDocument)
class PPMPDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'status')
    list_filter = ('status', 'uploaded_at')
    search_fields = ('title', 'uploaded_by__username')
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('sched_Id', 'title', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('title', 'description')
    
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('itemId', 'equipmentName', 'equipmentSN')
    search_fields = ('equipmentName', 'equipmentSN')

@admin.register(ProcurementItem)
class ProcurementItemAdmin(admin.ModelAdmin):
    list_display = ('itemid', 'item', 'quantity', 'unit', 'estimated_budget', 'mode_of_procurement', 'status')
    list_filter = ('status', 'mode_of_procurement')
    search_fields = ('item',)
    list_editable = ('status',)

@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('procurement_item', 'serial_no')
    search_fields = ('procurement_item__item', 'serial_no')

@admin.register(ExcelData)
class ExcelDataAdmin(admin.ModelAdmin):
    list_display = ('title_of_l_d', 'frequency', 'category', 'expected_number_of_participants', 'duration', 'variance')
    search_fields = ('title_of_l_d', 'category')
    list_filter = ('frequency', 'category')

@admin.register(BorrowingRecord)
class BorrowingRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'equipment', 'date_borrowed', 'date_returned', 'is_returned')
    list_filter = ('is_returned', 'date_borrowed')
    search_fields = ('student__studentName', 'equipment__equipmentName')
