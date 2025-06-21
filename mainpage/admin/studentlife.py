from django.contrib import admin
from ..models import *
class requestedgmcAdmin(admin.ModelAdmin):
    list_display = ("student", "reason", "or_num", "request_date", "processed")


admin.site.register(RequestedGMC, requestedgmcAdmin)


class scheduleAdmin(admin.ModelAdmin):
    list_display = (
        "sched_Id",
        "title",
        "description",
        "start_datetime",
        "end_datetime",
    )


admin.site.register(Schedule, scheduleAdmin)

admin.site.register(Equipment)

admin.site.register(BorrowingRecord)

# FOR PPMP TRACKER


class ProcurementItemAdmin(admin.ModelAdmin):
    list_display = (
        "itemid",
        "item",
        "quantity",
        "unit",
        "estimated_budget",
        "mode_of_procurement",
        "unit_price",
        "status",
    )
    list_filter = ("mode_of_procurement",)
    search_fields = ("item",)


admin.site.register(ProcurementItem, ProcurementItemAdmin)

# for delivered


class StorageAdmin(admin.ModelAdmin):
    list_display = ("get_item_id", "get_item", "serial_no", "get_unit_price")
    search_fields = ("procurement_item__itemid", "procurement_item__item", "serial_no")

    def get_item_id(self, obj):
        return obj.procurement_item.itemid

    get_item_id.short_description = "Item ID"

    def get_item(self, obj):
        return obj.procurement_item.item

    get_item.short_description = "Item"

    def get_unit_price(self, obj):
        return obj.procurement_item.unit_price

    get_unit_price.short_description = "Unit Price"


admin.site.register(Storage, StorageAdmin)
