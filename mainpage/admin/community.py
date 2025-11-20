from django.contrib import admin
from ..models import (
    Program, 
    ProgramImage, 
    CrowdfundingProject, 
    DonationChannel, 
    Donation, 
    MOD, 
    QrDonation
)

# --- Inlines ---
# These allow you to add images directly inside the parent model page

class ProgramImageInline(admin.TabularInline):
    model = ProgramImage
    extra = 1  # Number of empty slots to show by default

class DonationChannelInline(admin.TabularInline):
    model = DonationChannel
    extra = 1

class DonationInline(admin.TabularInline):
    """
    Shows a list of donations inside the Project page.
    Usually, you don't want to add donations manually here, so it's read-only.
    """
    model = Donation
    extra = 0
    readonly_fields = ('donor_name', 'amount', 'created_at')
    can_delete = False
    show_change_link = True


# --- Model Admins ---

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    inlines = [ProgramImageInline]
    list_display = ('title', 'event_date', 'venue', 'created_at', 'archive')
    list_filter = ('archive', 'created_at', 'event_date')
    search_fields = ('title', 'description', 'venue')
    readonly_fields = ('created_at',)


@admin.register(CrowdfundingProject)
class CrowdfundingProjectAdmin(admin.ModelAdmin):
    inlines = [DonationChannelInline, DonationInline]
    list_display = ('title', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('project', 'donor_name', 'amount', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('donor_name', 'project__title')
    readonly_fields = ('created_at',)


@admin.register(MOD)
class MODAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'donation_type', 
        'amount', 
        'status', 
        'date', 
        'processed_by'
    )
    list_filter = ('status', 'donation_type', 'date', 'what_kind')
    search_fields = ('name', 'contact_number', 'donated')
    readonly_fields = ('date',)
    
    fieldsets = (
        ('Donor Info', {
            'fields': ('name', 'contact_number', 'donated')
        }),
        ('Donation Details', {
            'fields': ('donation_type', 'amount', 'what_kind', 'status', 'date')
        }),
        ('Payment Info', {
            'fields': ('gcash_number', 'bank_number', 'bank_card', 'image_details')
        }),
        ('Recipient Info', {
            'fields': ('recepient', 'recepient_things', 'date_sched')
        }),
        ('Processing', {
            'fields': ('processed_by',)
        }),
    )


@admin.register(QrDonation)
class QrDonationAdmin(admin.ModelAdmin):
    list_display = ('__str__',)